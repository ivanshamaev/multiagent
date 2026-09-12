"""Opt-in live Reviewer evaluation over a QA-prequalified scenario candidate."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256

from contracts import QADecision, ToolName
from orchestrator import Stage
from policies import load_capability_profile
from runtime.model_provider import MAFModelProvider, ModelUsage, fetch_model_catalog
from runtime.qa import QA_SEMANTIC_PROBE_SQL, QADraft, accept_qa_draft, prepare_qa_request
from runtime.qa_live import QA_PROFILE_PATH, _cost, _persist
from runtime.reviewer import prepare_reviewer_request, reviewer_system_prompt
from runtime.reviewer_mutations import (
    load_reviewer_mutations,
    seed_reviewer_mutation_candidate,
)
from runtime.reviewer_workflow import (
    AutonomousReviewerResult,
    ReviewerWorkflowInput,
    build_reviewer_workflow,
)
from runtime.scenario_harness import REPOSITORY_ROOT, load_manifest
from runtime.settings import GateLLMSettings
from runtime.tools import connect_data_engineer_tools
from runtime.validator import validate_candidate

REVIEWER_PROFILE_PATH = REPOSITORY_ROOT / "policies/profiles/reviewer_v1.json"


def _empty_semantic_diff(raw: object) -> bool:
    """Recognize only an explicit empty row set; malformed output fails closed."""

    if isinstance(raw, (list, tuple)):
        if len(raw) != 1:
            return False
        payload = getattr(raw[0], "text", None) or getattr(raw[0], "result", None)
        return isinstance(payload, str) and _empty_semantic_diff(payload)
    if not isinstance(raw, str):
        return False
    text = raw.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        lines = tuple(line for line in text.splitlines() if line.strip())
        return len(lines) > 1 and all(_empty_semantic_diff(line) for line in lines)
    if isinstance(parsed, dict):
        if set(parsed) == {"result"} and isinstance(parsed["result"], str):
            return _empty_semantic_diff(parsed["result"])
        rows = parsed.get("rows", parsed.get("data"))
        return isinstance(rows, list) and not rows
    return isinstance(parsed, list) and not parsed


async def _prequalify_qa(
    candidate,
    validation,
    *,
    workflow_id: str,
):
    """Attach an independent, code-owned QA PASS after the immutable public probe."""

    manifest = load_manifest(REPOSITORY_ROOT, "net-revenue")
    profile = load_capability_profile(QA_PROFILE_PATH).model_copy(
        update={
            "allowed_tools": frozenset({ToolName.CLICKHOUSE_RUN_QUERY}),
            "max_tool_calls": 1,
        }
    )
    request = prepare_qa_request(
        REPOSITORY_ROOT,
        "net-revenue",
        workflow_id=workflow_id,
    )
    async with connect_data_engineer_tools(
        REPOSITORY_ROOT,
        candidate.installed.workspace,
        manifest,
        profile,
        task_id=validation.state.task_id,
        actor_id=request.agent_id,
        role="qa",
    ) as connected:
        query_tools = tuple(item for item in connected.tools if item.name == "clickhouse_run_query")
        if len(query_tools) != 1:
            raise RuntimeError("QA prequalification requires exactly one query tool")
        raw = await query_tools[0].invoke(arguments={"query": QA_SEMANTIC_PROBE_SQL})
        if not _empty_semantic_diff(raw):
            raise RuntimeError("public semantic probe did not return an explicit empty diff")
        report, state, events = accept_qa_draft(
            request,
            validation.state,
            validation.events,
            QADraft(
                decision=QADecision.PASS,
                check_name="immutable public semantic comparison",
                summary="Validator and immutable public semantic comparison passed.",
            ),
            tool_evidence=connected.gateway.evidence,
            tool_usage=connected.gateway.usage,
            model_usage=ModelUsage(),
            model_latency_ms=0,
            completed_at=datetime.now(UTC),
        )
    return report, state, events


async def run_live(
    mutation_id: str,
    *,
    model_id: str = "openai/gpt-5.6-luna",
) -> dict[str, object]:
    settings = GateLLMSettings()
    catalog = await fetch_model_catalog(settings)
    models = {item.id: item for item in catalog.catalog.data}
    if model_id not in models:
        raise ValueError("requested Reviewer model is absent from the live catalog")
    selected = models[model_id]
    timestamp = datetime.now(UTC)
    suffix = sha256(f"{mutation_id}:{timestamp.isoformat()}".encode()).hexdigest()[:12]
    workflow_id = f"review-net-revenue-{mutation_id}-{suffix}"
    candidate = seed_reviewer_mutation_candidate(
        REPOSITORY_ROOT,
        "net-revenue",
        mutation_id,
        workflow_id=workflow_id,
    )
    validation = await asyncio.to_thread(
        validate_candidate,
        REPOSITORY_ROOT,
        "net-revenue",
        candidate.state,
        candidate.events,
    )
    if validation.state.stage is not Stage.VALIDATED:
        raise RuntimeError("Reviewer candidate did not pass the full validator")
    qa_report, qa_state, qa_events = await _prequalify_qa(
        candidate,
        validation,
        workflow_id=workflow_id,
    )
    if qa_state.stage is not Stage.QA_PASSED:
        raise RuntimeError("Reviewer candidate did not reach QA_PASSED")

    manifest = load_manifest(REPOSITORY_ROOT, "net-revenue")
    profile = load_capability_profile(REVIEWER_PROFILE_PATH)
    provider = MAFModelProvider(
        settings.model_copy(
            update={"default_model": model_id, "max_output_tokens": 4_096, "max_retries": 1}
        ),
        model_id=model_id,
        max_tool_iterations=1,
        max_function_calls=1,
        require_initial_tool_call=True,
    )
    request = prepare_reviewer_request(
        REPOSITORY_ROOT,
        "net-revenue",
        workflow_id=workflow_id,
        qa_report=qa_report,
    )
    async with connect_data_engineer_tools(
        REPOSITORY_ROOT,
        candidate.installed.workspace,
        manifest,
        profile,
        task_id=qa_state.task_id,
        actor_id=request.agent_id,
        role="reviewer",
    ) as connected:
        envelope = await build_reviewer_workflow(provider, connected).run(
            ReviewerWorkflowInput(request=request, state=qa_state, events=qa_events)
        )
        outputs = envelope.get_outputs()
    if len(outputs) != 1 or not isinstance(outputs[0], AutonomousReviewerResult):
        raise RuntimeError("Reviewer workflow returned an invalid output envelope")
    result = outputs[0]

    usage = ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in result.model_calls),
        output_tokens=sum(item.usage.output_tokens for item in result.model_calls),
        total_tokens=sum(item.usage.total_tokens for item in result.model_calls),
    )
    expected = "approve" if mutation_id == "canonical" else "request_changes"
    actual = result.report.decision.value
    configuration = {
        "candidate_model_sha256": candidate.installed.model_sha256,
        "candidate_test_sha256": candidate.installed.test_sha256,
        "instructions_sha256": sha256(reviewer_system_prompt().encode()).hexdigest(),
        "model_id": model_id,
        "profile": profile.model_dump(mode="json"),
        "protocol": "validator-public-probe-reviewer-v1",
        "scenario_version": manifest.version,
    }
    fingerprint = sha256(
        json.dumps(configuration, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    record: dict[str, object] = {
        "completed_at": datetime.now(UTC).isoformat(),
        "configuration_fingerprint": fingerprint,
        "decision": actual,
        "estimated_cost_rub": _cost(usage, selected.pricing.prompt, selected.pricing.completion),
        "expected_decision": expected,
        "findings": [
            {
                "acceptance_criterion": item.acceptance_criterion,
                "description": item.description,
                "severity": item.severity.value,
            }
            for item in result.report.findings
        ],
        "matched_expectation": actual == expected,
        "model_call_count": len(result.model_calls),
        "model_id": model_id,
        "model_latency_ms": sum(item.latency_ms for item in result.model_calls),
        "mutation_id": mutation_id,
        "qa_protocol": "full-validator-plus-immutable-public-probe",
        "status": "PASS" if actual == expected else "FAIL",
        "summary": result.report.summary,
        "tool_calls": [
            {
                "duration_ms": item.duration_ms,
                "output_bytes": item.output_bytes,
                "status": item.status.value,
                "tool": item.tool.value,
            }
            for item in result.tool_evidence
        ],
        "usage": usage.model_dump(),
        "workflow_id": workflow_id,
        "workflow_stage": result.state.stage.value,
    }
    return {**record, "run_record": _persist(f"reviewer-{workflow_id}", record)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    choices = ["canonical", *(item.id for item in load_reviewer_mutations().mutations)]
    parser.add_argument("--mutation", choices=choices, required=True)
    parser.add_argument("--model", default="openai/gpt-5.6-luna")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        result = asyncio.run(run_live(arguments.mutation, model_id=arguments.model))
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

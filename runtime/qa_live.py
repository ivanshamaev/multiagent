"""Opt-in live QA evaluation against one canonical or mutated Net Revenue candidate."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

from policies import load_capability_profile
from runtime.model_provider import MAFModelProvider, ModelUsage, fetch_model_catalog
from runtime.qa import prepare_qa_request, qa_system_prompt
from runtime.qa_mutations import load_qa_mutations, seed_mutation_candidate
from runtime.qa_workflow import AutonomousQAResult, QAWorkflowInput, build_qa_workflow
from runtime.scenario_harness import REPOSITORY_ROOT, load_manifest
from runtime.settings import GateLLMSettings
from runtime.tools import connect_data_engineer_tools
from runtime.validator import validate_candidate

QA_PROFILE_PATH = REPOSITORY_ROOT / "policies/profiles/qa_v1.json"


def _cost(usage: ModelUsage, prompt_price: Decimal, completion_price: Decimal) -> str:
    value = (
        Decimal(usage.input_tokens) * prompt_price + Decimal(usage.output_tokens) * completion_price
    ) / Decimal(1_000_000)
    return str(value.quantize(Decimal("0.000001")))


def _persist(record_id: str, payload: dict[str, object]) -> str:
    directory = REPOSITORY_ROOT / ".scenario-state/runs"
    target = directory / f"qa-{record_id}.json"
    if directory.is_symlink() or target.is_symlink():
        raise RuntimeError("QA run metadata path must not be a symlink")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary_text = tempfile.mkstemp(prefix=".qa-run-", dir=directory)
    temporary = Path(temporary_text)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o600)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target.relative_to(REPOSITORY_ROOT).as_posix()


async def run_live(
    mutation_id: str,
    *,
    model_id: str = "openai/gpt-5.6-luna",
) -> dict[str, object]:
    settings = GateLLMSettings()
    catalog = await fetch_model_catalog(settings)
    models = {item.id: item for item in catalog.catalog.data}
    if model_id not in models:
        raise ValueError("requested QA model is absent from the live catalog")
    selected = models[model_id]
    timestamp = datetime.now(UTC)
    suffix = sha256(f"{mutation_id}:{timestamp.isoformat()}".encode()).hexdigest()[:12]
    workflow_id = f"qa-net-revenue-{mutation_id}-{suffix}"
    candidate = seed_mutation_candidate(
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
    if validation.state.stage.value != "validated":
        detected = mutation_id != "canonical" and validation.artifact.decision.value == "fail"
        record = {
            "completed_at": datetime.now(UTC).isoformat(),
            "detected_by": "validator" if detected else None,
            "expected_decision": "fail" if mutation_id != "canonical" else "pass",
            "matched_expectation": detected,
            "model_id": model_id,
            "mutation_id": mutation_id,
            "status": "PASS" if detected else "NOT_ASSESSED",
            "validation_decision": validation.artifact.decision.value,
            "workflow_id": workflow_id,
        }
        return {**record, "run_record": _persist(workflow_id, record)}

    manifest = load_manifest(REPOSITORY_ROOT, "net-revenue")
    profile = load_capability_profile(QA_PROFILE_PATH).model_copy(update={"max_tool_calls": 2})
    bounded_settings = settings.model_copy(
        update={"default_model": model_id, "max_output_tokens": 2_048, "max_retries": 1}
    )
    provider = MAFModelProvider(
        bounded_settings,
        model_id=model_id,
        max_tool_iterations=1,
        max_function_calls=1,
        require_initial_tool_call=True,
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
        output = await build_qa_workflow(provider, connected).run(
            QAWorkflowInput(
                request=request,
                state=validation.state,
                events=validation.events,
            )
        )
        results = output.get_outputs()
        if len(results) != 1 or not isinstance(results[0], AutonomousQAResult):
            raise RuntimeError("QA workflow returned an invalid output envelope")
        result = results[0]

    usage = ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in result.model_calls),
        output_tokens=sum(item.usage.output_tokens for item in result.model_calls),
        total_tokens=sum(item.usage.total_tokens for item in result.model_calls),
    )
    expected = "pass" if mutation_id == "canonical" else "fail"
    actual = result.report.decision.value
    configuration = {
        "candidate_model_sha256": candidate.installed.model_sha256,
        "candidate_test_sha256": candidate.installed.test_sha256,
        "instructions_sha256": sha256(qa_system_prompt().encode()).hexdigest(),
        "model_id": model_id,
        "profile": profile.model_dump(mode="json"),
        "protocol": "read-query-qa-v1",
        "scenario_version": manifest.version,
    }
    fingerprint = sha256(
        json.dumps(configuration, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    record = {
        "completed_at": datetime.now(UTC).isoformat(),
        "configuration_fingerprint": fingerprint,
        "decision": actual,
        "detected_by": "qa" if actual == "fail" else None,
        "defects": [
            {
                "acceptance_criterion": item.acceptance_criterion,
                "description": item.description,
                "severity": item.severity.value,
            }
            for item in result.report.defects
        ],
        "estimated_cost_rub": _cost(usage, selected.pricing.prompt, selected.pricing.completion),
        "expected_decision": expected,
        "matched_expectation": actual == expected,
        "model_call_count": len(result.model_calls),
        "model_id": model_id,
        "model_latency_ms": sum(item.latency_ms for item in result.model_calls),
        "mutation_id": mutation_id,
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
        "validation_decision": validation.artifact.decision.value,
        "workflow_id": workflow_id,
        "workflow_stage": result.state.stage.value,
    }
    return {**record, "run_record": _persist(workflow_id, record)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    choices = ["canonical", *(item.id for item in load_qa_mutations().mutations)]
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

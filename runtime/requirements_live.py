"""Opt-in live Analyst-to-PM requirements pipeline through GateLLM."""

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

from orchestrator import Stage
from policies import load_capability_profile
from runtime.agent_runtime import (
    SpecificationRunRequest,
    SpecificationRunResult,
    build_specification_workflow,
    pm_system_prompt,
)
from runtime.analyst import analyst_system_prompt, prepare_analyst_request
from runtime.analyst_workflow import AutonomousAnalystResult, build_analyst_workflow
from runtime.model_provider import MAFModelProvider, ModelUsage, fetch_model_catalog
from runtime.scenario_harness import REPOSITORY_ROOT, load_manifest
from runtime.settings import GateLLMSettings
from runtime.tools import connect_data_engineer_tools

PROFILE_PATH = REPOSITORY_ROOT / "policies/profiles/analyst_v1.json"


def _cost(usage: ModelUsage, prompt_price: Decimal, completion_price: Decimal) -> Decimal:
    return (
        Decimal(usage.input_tokens) * prompt_price + Decimal(usage.output_tokens) * completion_price
    ) / Decimal(1_000_000)


def _persist(workflow_id: str, payload: dict[str, object]) -> str:
    directory = REPOSITORY_ROOT / ".scenario-state/runs"
    target = directory / f"requirements-{workflow_id}.json"
    if directory.is_symlink() or target.is_symlink():
        raise RuntimeError("Requirements run metadata path must not be a symlink")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary_text = tempfile.mkstemp(prefix=".requirements-run-", dir=directory)
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
    scenario_id: str,
    *,
    analyst_model_id: str = "openai/gpt-5.6-luna",
    pm_model_id: str = "openai/gpt-5.6-luna",
    case_id: str = "canonical",
) -> dict[str, object]:
    if case_id not in {"canonical", "ambiguous-metric"}:
        raise ValueError("unknown requirements evaluation case")
    settings = GateLLMSettings()
    catalog = await fetch_model_catalog(settings)
    models = {item.id: item for item in catalog.catalog.data}
    if analyst_model_id not in models or pm_model_id not in models:
        raise ValueError("requested requirements model is absent from the live catalog")
    analyst_model = models[analyst_model_id]
    pm_model = models[pm_model_id]
    manifest = load_manifest(REPOSITORY_ROOT, scenario_id)
    profile = load_capability_profile(PROFILE_PATH).model_copy(update={"max_tool_calls": 3})
    configuration_payload = {
        "analyst_instructions_sha256": sha256(analyst_system_prompt().encode()).hexdigest(),
        "analyst_model_id": analyst_model_id,
        "case_id": case_id,
        "pm_instructions_sha256": sha256(pm_system_prompt().encode()).hexdigest(),
        "pm_model_id": pm_model_id,
        "profile": profile.model_dump(mode="json"),
        "protocol": "requirements-pipeline-v1",
        "scenario_id": scenario_id,
        "scenario_version": manifest.version,
    }
    canonical = json.dumps(
        configuration_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    configuration_fingerprint = sha256(canonical.encode()).hexdigest()
    timestamp = datetime.now(UTC)
    suffix = sha256(f"{scenario_id}:{case_id}:{timestamp.isoformat()}".encode()).hexdigest()[:12]
    workflow_id = f"requirements-{scenario_id}-{case_id}-{suffix}"
    request = prepare_analyst_request(
        REPOSITORY_ROOT,
        scenario_id,
        workflow_id=workflow_id,
        correlation_id=workflow_id,
        configuration_fingerprint=configuration_fingerprint,
        created_at=timestamp,
    )
    if case_id == "ambiguous-metric":
        request = request.model_copy(
            update={
                "task": request.task.model_copy(
                    update={
                        "title": "Expose customer value",
                        "description": (
                            "Create a customer value metric, but its formula, time window, "
                            "currency treatment, and late-refund policy are intentionally "
                            "unspecified."
                        ),
                    }
                )
            }
        )
    analyst_provider = MAFModelProvider(
        settings.model_copy(
            update={"default_model": analyst_model_id, "max_output_tokens": 1_536, "max_retries": 1}
        ),
        model_id=analyst_model_id,
        max_tool_iterations=1,
        max_function_calls=1,
        require_initial_tool_call=True,
    )
    workspace = REPOSITORY_ROOT / ".scenario-state/workspaces" / scenario_id
    async with connect_data_engineer_tools(
        REPOSITORY_ROOT,
        workspace,
        manifest,
        profile,
        task_id=request.task.task_id,
        actor_id=request.agent_id,
        role="analyst",
    ) as connected:
        analyst_outputs = (
            await build_analyst_workflow(analyst_provider, connected).run(request)
        ).get_outputs()
    if len(analyst_outputs) != 1 or not isinstance(analyst_outputs[0], AutonomousAnalystResult):
        raise RuntimeError("Analyst workflow returned an invalid output envelope")
    analyst_result = analyst_outputs[0]

    pm_provider = MAFModelProvider(
        settings.model_copy(
            update={"default_model": pm_model_id, "max_output_tokens": 1_536, "max_retries": 1}
        ),
        model_id=pm_model_id,
    )
    pm_outputs = (
        await build_specification_workflow(pm_provider).run(
            SpecificationRunRequest(
                handoff=analyst_result.handoff,
                state=analyst_result.state,
                events=analyst_result.events,
            )
        )
    ).get_outputs()
    if len(pm_outputs) != 1 or not isinstance(pm_outputs[0], SpecificationRunResult):
        raise RuntimeError("PM workflow returned an invalid output envelope")
    pm_result = pm_outputs[0]

    analyst_usage = ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in analyst_result.model_calls),
        output_tokens=sum(item.usage.output_tokens for item in analyst_result.model_calls),
        total_tokens=sum(item.usage.total_tokens for item in analyst_result.model_calls),
    )
    pm_usage = pm_result.model_call.usage
    expected_block = bool(analyst_result.handoff.unresolved_questions)
    matched_expectation = not expected_block or pm_result.state.stage is Stage.BLOCKED
    estimated_cost = _cost(
        analyst_usage, analyst_model.pricing.prompt, analyst_model.pricing.completion
    ) + _cost(pm_usage, pm_model.pricing.prompt, pm_model.pricing.completion)
    record: dict[str, object] = {
        "analyst_fact_count": len(analyst_result.report.facts),
        "analyst_model_call_count": len(analyst_result.model_calls),
        "analyst_model_id": analyst_model_id,
        "analyst_usage": analyst_usage.model_dump(mode="json"),
        "case_id": case_id,
        "completed_at": datetime.now(UTC).isoformat(),
        "configuration_fingerprint": configuration_fingerprint,
        "estimated_cost_rub": str(estimated_cost.quantize(Decimal("0.000001"))),
        "event_count": len(pm_result.events),
        "matched_expectation": matched_expectation,
        "open_question_count": len(analyst_result.report.open_questions),
        "pm_blocked_reason": (
            None
            if pm_result.artifact.blocked_reason is None
            else pm_result.artifact.blocked_reason.value
        ),
        "pm_decision": pm_result.artifact.decision.value,
        "pm_model_call_count": 1,
        "pm_model_id": pm_model_id,
        "pm_usage": pm_usage.model_dump(mode="json"),
        "status": "PASS" if matched_expectation else "FAIL",
        "tool_call_count": len(analyst_result.tool_evidence),
        "workflow_id": workflow_id,
        "workflow_stage": pm_result.state.stage.value,
    }
    return {**record, "run_record": _persist(workflow_id, record)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="net-revenue")
    parser.add_argument("--analyst-model", default="openai/gpt-5.6-luna")
    parser.add_argument("--pm-model", default="openai/gpt-5.6-luna")
    parser.add_argument("--case", choices=("canonical", "ambiguous-metric"), default="canonical")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        result = asyncio.run(
            run_live(
                arguments.scenario,
                analyst_model_id=arguments.analyst_model,
                pm_model_id=arguments.pm_model,
                case_id=arguments.case,
            )
        )
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

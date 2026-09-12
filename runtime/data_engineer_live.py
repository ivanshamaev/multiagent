"""Opt-in live autonomous Data Engineer run through GateLLM and official MCP tools."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

from policies import load_capability_profile
from runtime.data_engineer import data_engineer_system_prompt, prepare_data_engineer_request
from runtime.data_engineer_workflow import (
    AutonomousDataEngineerResult,
    AutonomousExecutionError,
    build_phased_data_engineer_workflow,
)
from runtime.model_provider import (
    AvailableModel,
    MAFModelProvider,
    ModelCallRecord,
    ModelCapabilityProbe,
    ModelCatalogSnapshot,
    ModelInvocationError,
    ModelOutputValidationError,
    ModelUsage,
    fetch_model_catalog,
    select_cheapest_agent_model,
)
from runtime.scenario_harness import REPOSITORY_ROOT, load_manifest, verify_workspace
from runtime.settings import GateLLMSettings
from runtime.tools import connect_data_engineer_tools


def _configuration_fingerprint(
    *, model_id: str, profile_payload: dict[str, object], scenario_id: str, scenario_version: str
) -> str:
    payload = {
        "instructions_sha256": sha256(data_engineer_system_prompt().encode()).hexdigest(),
        "model_id": model_id,
        "profile": profile_payload,
        "scenario_id": scenario_id,
        "scenario_version": scenario_version,
    }
    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(canonical.encode()).hexdigest()


def _estimated_cost(
    input_tokens: int,
    output_tokens: int,
    prompt_price: Decimal,
    completion_price: Decimal,
) -> str:
    value = (
        Decimal(input_tokens) * prompt_price + Decimal(output_tokens) * completion_price
    ) / Decimal(1_000_000)
    return str(value.quantize(Decimal("0.000001")))


def _aggregate_model_calls(
    calls: tuple[ModelCallRecord, ...],
) -> tuple[ModelUsage, int, str, str]:
    if not calls:
        raise ValueError("at least one model call is required")
    usage = ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in calls),
        output_tokens=sum(item.usage.output_tokens for item in calls),
        total_tokens=sum(item.usage.total_tokens for item in calls),
    )
    request_fingerprint = sha256(
        "\x00".join(item.request_sha256 for item in calls).encode()
    ).hexdigest()
    response_fingerprint = sha256(
        "\x00".join(item.response_sha256 for item in calls).encode()
    ).hexdigest()
    return usage, sum(item.latency_ms for item in calls), request_fingerprint, response_fingerprint


def _persist_run_record(workflow_id: str, record: dict[str, object]) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", workflow_id):
        raise RuntimeError("workflow ID is unsafe for run record retention")
    directory = REPOSITORY_ROOT / ".scenario-state/runs"
    if directory.is_symlink():
        raise RuntimeError("run record directory must not be a symlink")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    resolved = directory.resolve(strict=True)
    if not resolved.is_relative_to(REPOSITORY_ROOT.resolve(strict=True)):
        raise RuntimeError("run record directory escaped the repository")
    target = resolved / f"{workflow_id}.json"
    descriptor, temporary_text = tempfile.mkstemp(prefix=".run-", dir=resolved)
    temporary = Path(temporary_text)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o600)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target.relative_to(REPOSITORY_ROOT).as_posix()


def _catalog_capability_fingerprint(snapshot: ModelCatalogSnapshot) -> str:
    payload = [
        {
            "category": item.category,
            "context_length": item.context_length,
            "id": item.id,
            "pricing": item.pricing.model_dump(mode="json"),
        }
        for item in sorted(snapshot.catalog.data, key=lambda model: model.id)
    ]
    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(canonical.encode()).hexdigest()


def _capability_cache_path() -> Path:
    return REPOSITORY_ROOT / ".scenario-state/model-capability.json"


def _load_capability_cache(
    snapshot: ModelCatalogSnapshot,
    requested_model: str | None,
    *,
    now: datetime,
) -> tuple[AvailableModel, ModelCapabilityProbe, ModelCapabilityProbe] | None:
    path = _capability_cache_path()
    if path.is_symlink() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        checked_at = datetime.fromisoformat(payload["checked_at"])
        if checked_at.tzinfo is None or now - checked_at > timedelta(hours=1):
            return None
        if payload["catalog_fingerprint"] != _catalog_capability_fingerprint(snapshot):
            return None
        if requested_model is not None and payload["model_id"] != requested_model:
            return None
        selected = next(item for item in snapshot.catalog.data if item.id == payload["model_id"])
        schema_probe = ModelCapabilityProbe.model_validate(payload["schema_probe"])
        tool_probe = ModelCapabilityProbe.model_validate(payload["tool_probe"])
    except (KeyError, OSError, StopIteration, TypeError, ValueError):
        return None
    if not schema_probe.available or not tool_probe.available:
        return None
    if schema_probe.model_id != selected.id or tool_probe.model_id != selected.id:
        return None
    return selected, schema_probe, tool_probe


def _persist_capability_cache(
    snapshot: ModelCatalogSnapshot,
    selected: AvailableModel,
    schema_probe: ModelCapabilityProbe,
    tool_probe: ModelCapabilityProbe,
) -> None:
    path = _capability_cache_path()
    payload = {
        "catalog_fingerprint": _catalog_capability_fingerprint(snapshot),
        "checked_at": datetime.now(UTC).isoformat(),
        "model_id": selected.id,
        "schema_probe": schema_probe.model_dump(mode="json"),
        "schema_version": 1,
        "tool_probe": tool_probe.model_dump(mode="json"),
    }
    _persist_private_json(path, payload)


def _persist_private_json(target: Path, payload: dict[str, object]) -> None:
    directory = target.parent
    if directory.is_symlink():
        raise RuntimeError("private metadata directory must not be a symlink")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    resolved = directory.resolve(strict=True)
    if not resolved.is_relative_to(REPOSITORY_ROOT.resolve(strict=True)):
        raise RuntimeError("private metadata directory escaped the repository")
    if target.is_symlink():
        raise RuntimeError("private metadata target must not be a symlink")
    descriptor, temporary_text = tempfile.mkstemp(prefix=".metadata-", dir=resolved)
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


async def run_live(scenario_id: str, *, requested_model: str | None) -> dict[str, object]:
    settings = GateLLMSettings()
    catalog = await fetch_model_catalog(settings)
    cached = _load_capability_cache(catalog, requested_model, now=datetime.now(UTC))
    capability_cache_hit = cached is not None
    if cached is None:
        selected, probes, tool_probes = await select_cheapest_agent_model(
            settings,
            catalog,
            max_candidates=10,
            requested_model=requested_model,
        )
        tool_probe = tool_probes[-1]
        _persist_capability_cache(catalog, selected, probes[-1], tool_probe)
    else:
        selected, schema_probe, tool_probe = cached
        probes = (schema_probe,)
    manifest = load_manifest(REPOSITORY_ROOT, scenario_id)
    workspace_status = verify_workspace(REPOSITORY_ROOT, manifest)
    workspace = Path(str(workspace_status["workspace"]))
    profile = load_capability_profile(REPOSITORY_ROOT / "policies/profiles/data_engineer_v1.json")
    profile = profile.model_copy(update={"max_tool_calls": min(profile.max_tool_calls, 6)})
    timestamp = datetime.now(UTC)
    run_suffix = sha256(timestamp.isoformat().encode()).hexdigest()[:12]
    workflow_id = f"de-{scenario_id}-{run_suffix}"
    request = prepare_data_engineer_request(
        REPOSITORY_ROOT,
        scenario_id,
        workflow_id=workflow_id,
        correlation_id=workflow_id,
        started_at=timestamp,
    )
    bounded_settings = settings.model_copy(
        update={"default_model": selected.id, "max_output_tokens": 2_048, "max_retries": 1}
    )
    provider = MAFModelProvider(
        bounded_settings,
        model_id=selected.id,
        max_tool_iterations=1,
        max_function_calls=profile.max_tool_calls,
        require_initial_tool_call=True,
    )
    async with connect_data_engineer_tools(
        REPOSITORY_ROOT,
        workspace,
        manifest,
        profile,
        task_id=request.specification.specification.task_id,
        actor_id=request.agent_id,
    ) as connected:
        workflow = build_phased_data_engineer_workflow(
            provider,
            connected,
            repository_root=REPOSITORY_ROOT,
            scenario_id=scenario_id,
        )
        try:
            execution = await workflow.run(request)
        except AutonomousExecutionError as error:
            usage, latency_ms, request_fingerprint, response_fingerprint = _aggregate_model_calls(
                error.model_calls
            )
            failed_record: dict[str, object] = {
                "completed_at": datetime.now(UTC).isoformat(),
                "capability_cache_hit": capability_cache_hit,
                "configuration_fingerprint": _configuration_fingerprint(
                    model_id=selected.id,
                    profile_payload=profile.model_dump(mode="json"),
                    scenario_id=scenario_id,
                    scenario_version=manifest.version,
                ),
                "error_code": error.code,
                "error_fingerprint": error.error_fingerprint,
                "estimated_cost_rub": _estimated_cost(
                    usage.input_tokens,
                    usage.output_tokens,
                    selected.pricing.prompt,
                    selected.pricing.completion,
                ),
                "model_id": selected.id,
                "model_call_count": len(error.model_calls),
                "model_latency_ms": latency_ms,
                "model_request_sha256": request_fingerprint,
                "model_response_sha256": response_fingerprint,
                "scenario_id": scenario_id,
                "started_at": timestamp.isoformat(),
                "tool_calls": [
                    {
                        "duration_ms": item.duration_ms,
                        "output_bytes": item.output_bytes,
                        "status": item.status.value,
                        "tool": item.tool.value,
                    }
                    for item in error.tool_evidence
                ],
                "usage": usage.model_dump(),
                "validation_decision": None,
                "validation_gates": [],
                "workflow_id": workflow_id,
                "workflow_stage": "run_failed",
                "workspace_fingerprint_before": request.context.workspace_fingerprint,
            }
            record_path = _persist_run_record(workflow_id, failed_record)
            return {**failed_record, "run_record": record_path}
        except Exception as error:
            # Provider/framework exceptions do not always expose usage, but every
            # started attempt must leave a redacted, auditable terminal record.
            failed_call = (
                error.model_call if isinstance(error, ModelOutputValidationError) else None
            )
            if failed_call is None:
                failed_usage = None
                failed_cost = None
                failed_latency = None
                failed_request_hash = None
                failed_response_hash = None
            else:
                failed_usage = failed_call.usage.model_dump()
                failed_cost = _estimated_cost(
                    failed_call.usage.input_tokens,
                    failed_call.usage.output_tokens,
                    selected.pricing.prompt,
                    selected.pricing.completion,
                )
                failed_latency = failed_call.latency_ms
                failed_request_hash = failed_call.request_sha256
                failed_response_hash = failed_call.response_sha256
            failed_record = {
                "completed_at": datetime.now(UTC).isoformat(),
                "capability_cache_hit": capability_cache_hit,
                "configuration_fingerprint": _configuration_fingerprint(
                    model_id=selected.id,
                    profile_payload=profile.model_dump(mode="json"),
                    scenario_id=scenario_id,
                    scenario_version=manifest.version,
                ),
                "error_code": f"agent_cycle_{type(error).__name__}",
                "error_fingerprint": (
                    str(error) if isinstance(error, ModelInvocationError) else None
                ),
                "estimated_cost_rub": failed_cost,
                "model_id": selected.id,
                "model_latency_ms": failed_latency,
                "model_request_sha256": failed_request_hash,
                "model_response_sha256": failed_response_hash,
                "scenario_id": scenario_id,
                "started_at": timestamp.isoformat(),
                "tool_calls": [
                    {
                        "duration_ms": item.duration_ms,
                        "output_bytes": item.output_bytes,
                        "status": item.status.value,
                        "tool": item.tool.value,
                    }
                    for item in connected.gateway.evidence
                ],
                "usage": failed_usage,
                "usage_available": failed_usage is not None,
                "validation_decision": None,
                "validation_gates": [],
                "workflow_id": workflow_id,
                "workflow_stage": "run_failed",
                "workspace_fingerprint_before": request.context.workspace_fingerprint,
            }
            record_path = _persist_run_record(workflow_id, failed_record)
            return {**failed_record, "run_record": record_path}
        outputs = execution.get_outputs()
        if len(outputs) != 1 or not isinstance(outputs[0], AutonomousDataEngineerResult):
            raise RuntimeError("autonomous workflow returned an invalid output envelope")
        result = outputs[0]

    model_calls = result.all_model_calls
    usage, model_latency_ms, request_fingerprint, response_fingerprint = _aggregate_model_calls(
        model_calls
    )
    record: dict[str, object] = {
        "completed_at": datetime.now(UTC).isoformat(),
        "capability_cache_hit": capability_cache_hit,
        "configuration_fingerprint": _configuration_fingerprint(
            model_id=selected.id,
            profile_payload=profile.model_dump(mode="json"),
            scenario_id=scenario_id,
            scenario_version=manifest.version,
        ),
        "estimated_cost_rub": _estimated_cost(
            usage.input_tokens,
            usage.output_tokens,
            selected.pricing.prompt,
            selected.pricing.completion,
        ),
        "event_count": len(result.events),
        "implementation_artifact_id": result.implementation.artifact_id,
        "implementation_status": result.implementation.status.value,
        "model_id": selected.id,
        "model_call_count": len(model_calls),
        "model_latency_ms": model_latency_ms,
        "model_request_sha256": request_fingerprint,
        "model_response_sha256": response_fingerprint,
        "probe_usage": [
            {
                "available": probe.available,
                "capability": "structured_output",
                "executed_this_run": not capability_cache_hit,
                "model_id": probe.model_id,
                "status_code": probe.status_code,
                "total_tokens": probe.usage.total_tokens,
            }
            for probe in probes
        ]
        + [
            {
                "available": tool_probe.available,
                "capability": "tool_calling",
                "executed_this_run": not capability_cache_hit,
                "model_id": tool_probe.model_id,
                "status_code": tool_probe.status_code,
                "total_tokens": tool_probe.usage.total_tokens,
            }
        ],
        "scenario_id": scenario_id,
        "started_at": timestamp.isoformat(),
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
        "validation_decision": (
            None if result.validation is None else result.validation.decision.value
        ),
        "validation_gates": ([] if result.validation is None else list(result.validation.gates)),
        "workflow_id": workflow_id,
        "workflow_stage": result.state.stage.value,
        "workspace_fingerprint_before": request.context.workspace_fingerprint,
    }
    record_path = _persist_run_record(workflow_id, record)
    return {**record, "run_record": record_path}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="net-revenue")
    parser.add_argument("--model")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        result = asyncio.run(run_live(arguments.scenario, requested_model=arguments.model))
    except Exception as error:  # the CLI deliberately exposes only the stable exception class
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}, sort_keys=True))
        return 1
    passed = result["workflow_stage"] == "validated"
    print(json.dumps({"status": "PASS" if passed else "FAIL", **result}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

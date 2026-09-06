"""Opt-in GateLLM catalog and controlled specification smoke command."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from pydantic import ValidationError

from runtime.agent_runtime import (
    SpecificationRunResult,
    build_specification_workflow,
    prepare_scenario_specification_request,
)
from runtime.model_provider import (
    MAFModelProvider,
    ModelCatalogError,
    ModelInvocationError,
    fetch_model_catalog,
    select_cheapest_available_chat_model,
    select_cheapest_chat_model,
)
from runtime.scenario_harness import REPOSITORY_ROOT, HarnessError
from runtime.settings import GateLLMSettings


async def _run(scenario_id: str, *, catalog_only: bool) -> dict[str, object]:
    settings = GateLLMSettings()
    catalog = await fetch_model_catalog(settings)
    catalog_cheapest = select_cheapest_chat_model(catalog)
    catalog_summary: dict[str, object] = {
        "catalog_retrieved_at": catalog.retrieved_at.isoformat(),
        "catalog_cheapest_model_id": catalog_cheapest.id,
        "chat_model_count": sum(model.category == "CHAT" for model in catalog.catalog.data),
    }
    if catalog_only:
        return catalog_summary

    selected, probes = await select_cheapest_available_chat_model(
        settings,
        catalog,
        requested_model=settings.default_model,
    )
    catalog_summary.update(
        {
            "capability_probes": [
                {
                    "available": probe.available,
                    "model_id": probe.model_id,
                    "status_code": probe.status_code,
                    "usage": probe.usage.model_dump(),
                }
                for probe in probes
            ],
            "completion_price_per_million_rub": str(selected.pricing.completion),
            "context_length": selected.context_length,
            "model_id": selected.id,
            "prompt_price_per_million_rub": str(selected.pricing.prompt),
            "selection_mode": "configured" if settings.default_model else "cost_first",
        }
    )

    bounded_settings = settings.model_copy(
        update={
            "default_model": selected.id,
            "max_output_tokens": min(settings.max_output_tokens, 512),
        }
    )
    request = prepare_scenario_specification_request(
        REPOSITORY_ROOT,
        scenario_id,
        workflow_id=f"smoke-{scenario_id}",
        correlation_id=f"smoke-{scenario_id}",
    )
    provider = MAFModelProvider(bounded_settings, model_id=selected.id)
    workflow = build_specification_workflow(provider)
    workflow_result = await workflow.run(request)
    outputs = workflow_result.get_outputs()
    if len(outputs) != 1 or not isinstance(outputs[0], SpecificationRunResult):
        raise RuntimeError("controlled workflow returned an invalid output envelope")
    result = outputs[0]
    return {
        **catalog_summary,
        "artifact_id": result.artifact.artifact_id,
        "decision": result.artifact.decision.value,
        "event_count": len(result.events),
        "finish_reason": result.model_call.finish_reason,
        "latency_ms": result.model_call.latency_ms,
        "request_sha256": result.model_call.request_sha256,
        "response_sha256": result.model_call.response_sha256,
        "state": result.state.stage.value,
        "usage": result.model_call.usage.model_dump(),
        "workspace_fingerprint": request.context.workspace_fingerprint,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="net-revenue")
    parser.add_argument("--catalog-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = asyncio.run(_run(args.scenario, catalog_only=args.catalog_only))
    except ModelInvocationError as error:
        print(
            json.dumps(
                {"detail": str(error), "error_type": type(error).__name__, "status": "FAIL"},
                sort_keys=True,
            )
        )
        return 1
    except ModelCatalogError as error:
        print(
            json.dumps(
                {"detail": str(error), "error_type": type(error).__name__, "status": "FAIL"},
                sort_keys=True,
            )
        )
        return 1
    except (
        HarnessError,
        ValidationError,
        RuntimeError,
        ValueError,
    ) as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}, sort_keys=True))
        return 1
    print(json.dumps({"status": "PASS", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

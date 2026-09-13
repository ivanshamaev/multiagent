"""Opt-in GateLLM catalog and controlled specification smoke command."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from pydantic import ValidationError

from runtime.model_provider import (
    ModelCatalogError,
    ModelInvocationError,
    fetch_model_catalog,
    select_cheapest_chat_model,
)
from runtime.requirements_live import run_live
from runtime.scenario_harness import HarnessError
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
    result = await run_live(scenario_id)
    return {**catalog_summary, **result}


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

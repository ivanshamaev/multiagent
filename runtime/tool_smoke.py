"""Deterministic live smoke for the policy-enforcing MAF/MCP tool boundary."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from agent_framework import FunctionTool, MiddlewareFailure

from contracts import ToolCallStatus
from policies import PolicyCode, load_capability_profile
from runtime.scenario_harness import load_manifest, verify_workspace
from runtime.tools import connect_data_engineer_mcp_tools


def _tool(tools: tuple[FunctionTool, ...], name: str) -> FunctionTool:
    try:
        return next(item for item in tools if item.name == name)
    except StopIteration:
        raise RuntimeError(f"required smoke tool is not exposed: {name}") from None


def _text(contents: Any) -> str:
    if not isinstance(contents, list) or any(item.type != "text" for item in contents):
        raise RuntimeError("MAF smoke received non-text tool output")
    return "\n".join(item.text for item in contents)


async def run_smoke(repository_root: Path, scenario_id: str) -> dict[str, object]:
    """Exercise allowed and denied paths without invoking an LLM."""

    manifest = load_manifest(repository_root, scenario_id)
    workspace_status = verify_workspace(repository_root, manifest)
    workspace = Path(str(workspace_status["workspace"]))
    profile = load_capability_profile(repository_root / "policies/profiles/data_engineer_v1.json")
    async with connect_data_engineer_mcp_tools(
        repository_root,
        workspace,
        profile,
        task_id=f"scenario-{scenario_id}",
        actor_id="data-engineer-agent",
    ) as connected:
        query_result = await _tool(connected.tools, "clickhouse_run_query").invoke(
            arguments={"query": "SELECT count() AS order_count FROM raw.orders LIMIT 1"}
        )
        if "100000" not in _text(query_result):
            raise RuntimeError("ClickHouse smoke count does not match the deterministic seed")
        await _tool(connected.tools, "dbt_compile").invoke(arguments={})
        await _tool(connected.tools, "dbt_test").invoke(arguments={})
        try:
            await _tool(connected.tools, "clickhouse_run_query").invoke(
                arguments={"query": "DROP TABLE analytics.fct_order_revenue"}
            )
        except MiddlewareFailure:
            pass
        else:
            raise RuntimeError("unsafe ClickHouse write was not denied")

        evidence = connected.gateway.evidence
        if evidence[-1].status is not ToolCallStatus.DENIED:
            raise RuntimeError("denied smoke call did not create denial evidence")
        if evidence[-1].error_type != PolicyCode.QUERY_DENIED.value:
            raise RuntimeError("denied smoke call has the wrong policy code")
        return {
            "evidence": [
                {
                    "arguments_sha256": item.arguments_sha256,
                    "output_bytes": item.output_bytes,
                    "status": item.status.value,
                    "tool": item.tool.value,
                }
                for item in evidence
            ],
            "successful_calls": connected.gateway.usage.completed_calls,
            "tool_count": len(connected.tools),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="net-revenue")
    args = parser.parse_args()
    result = asyncio.run(run_smoke(Path.cwd(), args.scenario))
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

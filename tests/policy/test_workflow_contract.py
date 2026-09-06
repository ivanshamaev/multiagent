import ast
import tomllib
from pathlib import Path

from contracts import (
    AnalysisReport,
    Evidence,
    ImplementationResult,
    QAReport,
    ReviewReport,
    TaskRequest,
    TaskSpecification,
    ToolCallEvidence,
    ToolRequest,
    ToolResult,
    ValidationResult,
)
from orchestrator import ALLOWED_TRANSITIONS, Stage

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_dependencies_are_pinned() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))

    expected = {
        "agent-framework-core": "1.17.0",
        "agent-framework-openai": "1.14.2",
        "httpx2": "2.12.0",
        "mcp": "1.26.0",
        "pydantic": "2.13.5",
        "pydantic-settings": "2.15.0",
        "sqlglot": "30.18.0",
    }
    assert project["project"]["dependencies"] == [
        f"{name}=={version}" for name, version in expected.items()
    ]
    locked = {package["name"]: package["version"] for package in lock["package"]}
    assert all(locked[name] == version for name, version in expected.items())


def test_all_external_contracts_close_extra_fields_and_pin_schema_version() -> None:
    models = (
        TaskRequest,
        TaskSpecification,
        AnalysisReport,
        ImplementationResult,
        ValidationResult,
        QAReport,
        ReviewReport,
        Evidence,
        ToolRequest,
        ToolCallEvidence,
        ToolResult,
    )

    for model in models:
        schema = model.model_json_schema()
        assert schema["additionalProperties"] is False
        assert schema["properties"]["schema_version"]["const"] == 1


def test_terminal_stages_have_no_outgoing_edges() -> None:
    assert ALLOWED_TRANSITIONS[Stage.DONE] == frozenset()
    assert ALLOWED_TRANSITIONS[Stage.BLOCKED] == frozenset()
    assert ALLOWED_TRANSITIONS[Stage.FAILED] == frozenset()


def test_contract_and_reducer_layers_do_not_import_provider_or_agent_framework() -> None:
    forbidden_roots = {"agent_framework", "openai"}
    offenders: list[str] = []
    for root_name in ("contracts", "orchestrator"):
        for path in (ROOT / root_name).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = {
                node.names[0].name.split(".", maxsplit=1)[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
            }
            imports.update(
                (node.module or "").split(".", maxsplit=1)[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            )
            if imports & forbidden_roots:
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []

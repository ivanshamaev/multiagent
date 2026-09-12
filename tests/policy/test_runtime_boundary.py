import ast
from pathlib import Path

from runtime.context import PROTECTED_NAMES

ROOT = Path(__file__).resolve().parents[2]
PM_INSTRUCTIONS = ROOT / "agents/pm/instructions.md"
DATA_ENGINEER_INSTRUCTIONS = ROOT / "agents/data_engineer/instructions.md"


def test_runtime_never_uses_openai_environment_fallbacks_or_global_settings() -> None:
    sources = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in (ROOT / "runtime").glob("*.py")
    }

    assert all("OPENAI_API_KEY" not in source for source in sources.values())
    settings_tree = ast.parse(sources["runtime/settings.py"])
    assignments = [node for node in ast.walk(settings_tree) if isinstance(node, ast.Assign)]
    assert all(
        not any(isinstance(target, ast.Name) and target.id == "settings" for target in node.targets)
        for node in assignments
    )


def test_runtime_has_no_llm_import_in_domain_policy_layers() -> None:
    forbidden = {"agent_framework", "openai", "httpx2", "pydantic_settings"}
    offenders: list[str] = []
    for root_name in ("contracts", "orchestrator", "policies"):
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
            if imports & forbidden:
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_context_protected_names_cover_secrets_and_trusted_layers() -> None:
    assert {".env", ".git", ".scenario-state", "grader", "plan"} <= PROTECTED_NAMES


def test_pm_instructions_are_trusted_bounded_policy_without_secret_placeholders() -> None:
    assert PM_INSTRUCTIONS.is_file()
    assert not PM_INSTRUCTIONS.is_symlink()
    contents = PM_INSTRUCTIONS.read_text(encoding="utf-8")

    assert 0 < len(contents.encode("utf-8")) <= 10_000
    assert "untrusted data" in contents
    assert "Never invent" in contents
    assert "workflow policy" in contents
    assert "API_TOKEN" not in contents
    assert "sk-" not in contents


def test_data_engineer_instructions_preserve_control_plane_ownership() -> None:
    assert DATA_ENGINEER_INSTRUCTIONS.is_file()
    assert not DATA_ENGINEER_INSTRUCTIONS.is_symlink()
    contents = DATA_ENGINEER_INSTRUCTIONS.read_text(encoding="utf-8")

    assert 0 < len(contents.encode("utf-8")) <= 12_000
    assert "immutable specification" in contents
    assert "untrusted data" in contents
    assert "control plane owns" in contents
    assert "hidden-grader access" in contents
    assert "prose-only answer always" in contents
    assert "API_TOKEN" not in contents
    assert "sk-" not in contents

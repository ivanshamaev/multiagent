from hashlib import sha256

import pytest
from pydantic import ValidationError

from runtime.context import (
    ContextBoundaryError,
    ContextBundle,
    ContextDocument,
    build_context_bundle,
)


def fingerprint() -> str:
    return "b" * 64


def test_context_is_sorted_bounded_and_content_addressed(tmp_path) -> None:
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested/b.sql").write_text("select 2\n", encoding="utf-8")
    (tmp_path / "a.yml").write_text("version: 2\n", encoding="utf-8")

    bundle = build_context_bundle(
        tmp_path,
        ("nested/b.sql", "a.yml"),
        workspace_fingerprint=fingerprint(),
    )

    assert tuple(document.path for document in bundle.documents) == ("a.yml", "nested/b.sql")
    assert bundle.total_bytes == len(b"version: 2\nselect 2\n")
    assert "BEGIN a.yml" in bundle.as_prompt()
    assert str(tmp_path) not in bundle.as_prompt()


@pytest.mark.parametrize("path", ("../secret", ".env", "plan/decision.md"))
def test_context_rejects_traversal_and_protected_paths(tmp_path, path: str) -> None:
    with pytest.raises(ContextBoundaryError):
        build_context_bundle(tmp_path, (path,), workspace_fingerprint=fingerprint())


def test_context_rejects_symlink_binary_and_size_escape(tmp_path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("safe\n", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(target)
    with pytest.raises(ContextBoundaryError, match="symlink"):
        build_context_bundle(tmp_path, ("link.txt",), workspace_fingerprint=fingerprint())

    (tmp_path / "binary.bin").write_bytes(b"\xff")
    with pytest.raises(ContextBoundaryError, match="UTF-8"):
        build_context_bundle(tmp_path, ("binary.bin",), workspace_fingerprint=fingerprint())

    with pytest.raises(ContextBoundaryError, match="per-file"):
        build_context_bundle(
            tmp_path,
            ("target.txt",),
            workspace_fingerprint=fingerprint(),
            max_file_bytes=4,
        )


def test_context_contract_detects_content_tampering() -> None:
    content = "select 1\n"
    document = ContextDocument(
        path="model.sql",
        content=content,
        size_bytes=len(content.encode()),
        sha256=sha256(content.encode()).hexdigest(),
    )
    with pytest.raises(ValidationError, match="total_bytes"):
        ContextBundle(
            workspace_fingerprint=fingerprint(),
            documents=(document,),
            total_bytes=0,
        )

"""Course receipts are freshness gates, not automatic fact-checking."""

import json
import shutil
from pathlib import Path

import pytest

from course.check import collect_issues, input_digest, local_references
from course.publication import PASSES, check_publication, publication_digest, receipt_path

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    shutil.copytree(
        ROOT / "course",
        tmp_path / "course",
        ignore=shutil.ignore_patterns("__pycache__", "node_modules"),
    )
    for path in (ROOT / "course").rglob("*.md"):
        if "skills" in path.parts or "node_modules" in path.parts:
            continue
        for ref in local_references(ROOT, path):
            dest = tmp_path / ref.relative_to(ROOT)
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ref, dest)
    dest = tmp_path / "plan/steps/lections/lecture-map.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "plan/steps/lections/lecture-map.json", dest)
    shutil.copyfile(ROOT / "uv.lock", tmp_path / "uv.lock")
    # These fixtures exercise lecture 00; unrelated published readers must not
    # require the real renderer inside a deliberately synthetic builder test.
    data = manifest(tmp_path)
    for lecture in data["lectures"]:
        if lecture["id"] != 0 and lecture["status"] != "outline":
            lecture["status"] = "draft"
            lecture["review"] = None
    save(tmp_path, data)
    return tmp_path


def manifest(root: Path) -> dict:
    return json.loads((root / "course/manifest.json").read_text())


def save(root: Path, value: dict) -> None:
    (root / "course/manifest.json").write_text(json.dumps(value), encoding="utf-8")


def candidate(root: Path, status: str = "reviewed") -> tuple[dict, Path]:
    m = manifest(root)
    lecture = m["lectures"][0]
    lecture["status"] = status
    lecture["review"] = "course/reviews/LECTURE-0000.json"
    (root / lecture["path"]).write_text(
        "# Test lecture\n\nA theoretical model.\n", encoding="utf-8"
    )
    receipt = {
        "schema_version": 1,
        "lecture_id": 0,
        "reviewer": "fixture-author",
        "checked_at": "2026-09-15T06:00:00Z",
        "input_digest": input_digest(root, lecture),
        "skills": [
            "technical-markdown-lectures",
            "technical-editorial-review",
            "technical-claim-verification",
        ],
        "passes": {"editorial": True, "technical": True, "recheck": True, "visual": False},
        "claims": [
            {
                "location": "test paragraph",
                "source": "https://example.com/paper",
                "verdict": "verified",
            }
        ],
        "findings": [],
        "diagram_waiver": "Test fixture has no visual relationship.",
    }
    path = root / lecture["review"]
    path.write_text(json.dumps(receipt), encoding="utf-8")
    save(root, m)
    publication = {
        "schema_version": 1,
        "lecture_id": 0,
        "reviewer": "fixture-author",
        "checked_at": "2026-09-15T06:00:00Z",
        "publication_digest": publication_digest(root, lecture),
        "passes": dict.fromkeys(PASSES, True),
        "assistive_technology": {
            "tested": False,
            "scope": "Fixture only, no actual browser checks",
        },
        "renderer": {"fixture": True},
        "rendered_sha256": "0" * 64,
        "artifacts_sha256": {"fixture": "1" * 64},
    }
    (root / receipt_path(lecture)).write_text(json.dumps(publication))
    return receipt, path


def test_repository_course_scaffold_is_consistent() -> None:
    assert collect_issues(ROOT) == []


@pytest.mark.parametrize("change", ["cycle", "concept"])
def test_rejects_consistently_corrupted_planning_map(checkout: Path, change: str) -> None:
    m = manifest(checkout)
    path = checkout / "plan/steps/lections/lecture-map.json"
    planning = json.loads(path.read_text())
    if change == "cycle":
        m["lectures"][0]["prerequisites"] = [1]
        planning["lectures"][0]["prerequisites"] = [1]
    else:
        concepts = m["lectures"][0]["concepts"]
        m["lectures"][1]["concepts"] = concepts
        planning["lectures"][1]["concepts"] = concepts
    save(checkout, m)
    path.write_text(json.dumps(planning))
    assert any(
        "dependency cycle" in e or "duplicate primary concept" in e
        for e in collect_issues(checkout)
    )


def test_missing_required_scaffold_file_is_rejected(checkout: Path) -> None:
    (checkout / "course/glossary.md").unlink()
    assert any("missing file" in e for e in collect_issues(checkout))


def test_installed_renderer_docs_are_not_course_prose(checkout: Path) -> None:
    deps = checkout / "course/node_modules/vendor"
    deps.mkdir(parents=True)
    (deps / "README.md").write_text("<script>vendor</script>\n[internal](missing.md)\n")
    assert collect_issues(checkout) == []
    (checkout / "course/invalid.md").write_text("<script>not-vendor</script>\n")
    assert collect_issues(checkout)


@pytest.mark.parametrize("change", ["duplicate", "missing", "cycle", "escape", "format", "track"])
def test_rejects_invalid_manifest(checkout: Path, change: str) -> None:
    m = manifest(checkout)
    if change == "duplicate":
        m["lectures"][1]["id"] = 0
    elif change == "missing":
        m["lectures"].pop()
    elif change == "cycle":
        m["lectures"][0]["prerequisites"] = [1]
    elif change == "escape":
        m["lectures"][0]["outline"] = "../outside.md"
    elif change == "format":
        m["student_tasks"] = ["deploy a pipeline"]
    else:
        m["lectures"][24]["track"] = "core"
    save(checkout, m)
    assert collect_issues(checkout)


@pytest.mark.parametrize("suffix", ["missing.md", "../../../outside.md", "README.md#absent-anchor"])
def test_rejects_broken_or_escaping_markdown_links(checkout: Path, suffix: str) -> None:
    path = checkout / "course/README.md"
    path.write_text(path.read_text() + f"\n[bad]({suffix})\n")
    assert collect_issues(checkout)


def test_ignores_links_in_code_fences(checkout: Path) -> None:
    path = checkout / "course/README.md"
    path.write_text(path.read_text() + "\n```text\n[example](missing.md)\n```\n")
    assert collect_issues(checkout) == []


def test_rejects_symlink_target(checkout: Path) -> None:
    (checkout / "course/alias.md").symlink_to(checkout / "course/README.md")
    assert any("symlink" in issue for issue in collect_issues(checkout))


def test_reviewed_fixture_with_fresh_receipt_is_accepted(checkout: Path) -> None:
    candidate(checkout)
    assert collect_issues(checkout) == []


@pytest.mark.parametrize(
    "change", ["missing", "stale", "config", "skill", "finding", "pass", "identity"]
)
def test_rejects_incomplete_or_stale_receipts(checkout: Path, change: str) -> None:
    receipt, path = candidate(checkout)
    if change == "missing":
        path.unlink()
    elif change in {"stale", "config", "skill"}:
        target = {
            "stale": manifest(checkout)["lectures"][0]["path"],
            "config": "course/diagram-config.json",
            "skill": "course/skills/technical-editorial-review/SKILL.md",
        }[change]
        dest = checkout / target
        dest.write_text(dest.read_text() + "\n")
    else:
        if change == "finding":
            receipt["findings"] = [{"severity": "major", "resolved": False}]
        elif change == "pass":
            receipt["passes"]["recheck"] = "true"
        else:
            receipt["lecture_id"] = 1
        path.write_text(json.dumps(receipt))
    assert collect_issues(checkout)


def test_diagram_review_cannot_pass_without_renderer(checkout: Path) -> None:
    receipt, path = candidate(checkout)
    lecture = manifest(checkout)["lectures"][0]
    toolchain = checkout / "course/toolchain.json"
    config = json.loads(toolchain.read_text())
    config["render_status"] = "prototype-verified"
    toolchain.write_text(json.dumps(config))
    (checkout / lecture["path"]).write_text(
        "# Test\n\n```mermaid\nflowchart LR\naccTitle: Test\naccDescr: Test\nA-->B\n```\n"
    )
    receipt["input_digest"] = input_digest(checkout, lecture)
    receipt["passes"]["visual"] = True
    path.write_text(json.dumps(receipt))
    assert any("renderer/visual" in e for e in collect_issues(checkout))


@pytest.mark.parametrize("change", ["missing", "pass", "css", "builder", "review", "identity"])
def test_publication_requires_fresh_actual_pass_records(checkout: Path, change: str) -> None:
    candidate(checkout)
    lecture = manifest(checkout)["lectures"][0]
    path = checkout / receipt_path(lecture)
    if change == "missing":
        path.unlink()
    elif change in {"css", "builder", "review"}:
        name = {
            "css": "course/static/site.css",
            "builder": "course/build.py",
            "review": lecture["review"],
        }[change]
        target = checkout / name
        target.write_text(target.read_text() + "\n")
    else:
        receipt = json.loads(path.read_text())
        if change == "pass":
            receipt["passes"]["keyboard"] = "true"
        else:
            receipt["lecture_id"] = 1
        path.write_text(json.dumps(receipt))
    with pytest.raises((ValueError, FileNotFoundError)):
        check_publication(checkout, lecture)


def test_candidate_then_publication_checks_rendered_hash_and_renderer(checkout: Path) -> None:
    from course.build import build

    candidate(checkout, "technically-verified")
    fonts = checkout / "course/node_modules/@fontsource/noto-sans"
    (fonts / "files").mkdir(parents=True)
    for name in ("latin", "cyrillic"):
        (fonts / "files" / f"noto-sans-{name}-400-normal.woff2").write_bytes(b"fixture-font")
    (fonts / "LICENSE").write_text("Fixture only\n")
    svg = (
        b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        b"<title>Fixture</title><desc>Fixture only</desc></svg>"
    )

    def fake_renderer(*args: object) -> bytes:
        return svg

    fp = {"fixture": True}
    build(
        checkout, "build/course-review", candidate_ids=(0,), renderer=fake_renderer, fingerprint=fp
    )
    preview = checkout / "build/course-review"
    assert "A theoretical model" in (preview / "topic-0000.html").read_text()
    build(checkout, renderer=fake_renderer, fingerprint=fp)
    assert "A theoretical model" not in (checkout / "build/course/topic-0000.html").read_text()
    index = json.loads((preview / "diagram-index.json").read_text())
    m = manifest(checkout)
    lecture = m["lectures"][0]
    lecture["status"] = "reviewed"
    save(checkout, m)
    path = checkout / receipt_path(lecture)
    receipt = json.loads(path.read_text())
    receipt["rendered_sha256"] = index["lectures"]["0"]["rendered_sha256"]
    path.write_text(json.dumps(receipt))
    build(checkout, renderer=fake_renderer, fingerprint=fp)
    original = (checkout / "build/course/topic-0000.html").read_bytes()
    assert b"A theoretical model" in original
    with pytest.raises(ValueError, match="renderer fingerprint"):
        build(checkout, renderer=fake_renderer, fingerprint={"fixture": "different"})
    receipt["rendered_sha256"] = "f" * 64
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="rendered artifact"):
        build(checkout, renderer=fake_renderer, fingerprint=fp)
    assert (checkout / "build/course/topic-0000.html").read_bytes() == original


def test_rejects_unregistered_lecture_and_student_lab(checkout: Path) -> None:
    (checkout / "course/lectures/LECTURE-0999-extra.md").write_text("# Extra\n")
    (checkout / "course/labs").mkdir()
    issues = collect_issues(checkout)
    assert any("unregistered" in e for e in issues)
    assert any("student-practice" in e for e in issues)


@pytest.mark.parametrize(
    "content",
    [
        "# Test\n\n<script>alert(1)</script>\n",
        "# Test\n\n```mermaid\nflowchart LR\nA-->B\n```\n",
        "# Test\n\n````text\nunclosed\n```\n",
    ],
)
def test_rejects_invalid_markdown_profile(checkout: Path, content: str) -> None:
    (checkout / "course/invalid.md").write_text(content)
    assert collect_issues(checkout)

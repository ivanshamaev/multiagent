"""Prototype publication boundaries; fake SVG tests do not claim real rendering."""

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from course.build import build, clean_env, normalize_svg
from course.site import curriculum, outline, roadmap, url, verify_links

ROOT = Path(__file__).resolve().parents[2]
SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" id="unstable" viewBox="0 0 100 100" '
    'aria-labelledby="title" aria-describedby="desc"><title id="title">Test</title>'
    '<desc id="desc">Description</desc><style>#unstable text{fill:black}</style>'
    '<text x="10" y="10" style="fill:black">Test</text></svg>'
)


@pytest.mark.parametrize(
    "status", ["draft", "editorial-reviewed", "technically-verified", "reviewed"]
)
def test_outline_reader_does_not_claim_authored_text_is_unwritten(status: str) -> None:
    item = json.loads((ROOT / "course/manifest.json").read_text())["lectures"][0]
    item["status"] = status
    body, _ = outline(item, [item], ("<p>Outline only</p>", ""))
    assert "текст подготовлен, но не опубликован" in body
    assert "текст лекции не написан" not in body
    assert "Outline only" in body


def fake_renderer(root: Path, definition: str, work: Path, key: str) -> bytes:
    assert "accTitle:" in definition
    return SVG.encode()


@pytest.fixture
def source_root(tmp_path: Path) -> Path:
    dest = tmp_path / "course/manifest.json"
    dest.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "course/manifest.json", dest)
    manifest = json.loads(dest.read_text())
    for item in manifest["lectures"]:
        item["status"] = "outline"
        item["review"] = None
    dest.write_text(json.dumps(manifest))
    for item in manifest["lectures"]:
        path = tmp_path / item["outline"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {item['title']}\n\n## Outline section\n\nFixture outline only.\n")
    for name in ("site.css", "viewer.js", "favicon.svg"):
        dest = tmp_path / "course/static" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "course/static" / name, dest)
    fonts = tmp_path / "course/node_modules/@fontsource/noto-sans"
    (fonts / "files").mkdir(parents=True)
    for name in ("latin", "cyrillic"):
        (fonts / "files" / f"noto-sans-{name}-400-normal.woff2").write_bytes(b"fixture-font")
    (fonts / "LICENSE").write_text("Fixture only\n")
    (tmp_path / "course/prototype").mkdir()
    (tmp_path / "course/prototype/diagrams.md").write_text(
        "# Prototype\n\n[Other](../technical-requirements.md#model)\n\n"
        "```mermaid\nflowchart LR\naccTitle: Model\naccDescr: Test\nA-->B\n```\n"
    )
    (tmp_path / "course/technical-requirements.md").write_text(
        "# Requirements\n\n## Model\n\n"
        "```mermaid\nsequenceDiagram\naccTitle: Cycle\naccDescr: Test\nA->>B: Test\n```\n"
    )
    return tmp_path


def test_normalized_svg_has_namespaced_ids_and_external_css() -> None:
    svg, css = normalize_svg(SVG.encode(), "fig-test-1")
    assert 'id="fig-test-1-0"' in svg
    assert 'aria-labelledby="fig-test-1-1"' in svg
    assert "<style" not in svg and "style=" not in svg
    assert "#fig-test-1-0 text" in css
    assert "fig-test-1-style" in css


def test_lecture_diagram_minimum_width_follows_validated_geometry() -> None:
    _, css = normalize_svg(SVG.encode(), "fig-topic-0000-1")
    assert "min-width:320px" in css
    _, css = normalize_svg(SVG.replace("100 100", "1800 100").encode(), "fig-topic-0000-1")
    assert "min-width:1100px" in css


def test_candidates_cannot_overwrite_public_output(source_root: Path) -> None:
    with pytest.raises(ValueError, match="isolated labelled"):
        build(source_root, candidate_ids=(0,), renderer=fake_renderer, fingerprint={"test": True})


def test_unreviewed_candidate_is_denied(source_root: Path) -> None:
    with pytest.raises(ValueError, match="completed technical review"):
        build(
            source_root,
            "build/course-candidate",
            candidate_ids=(0,),
            renderer=fake_renderer,
            fingerprint={"test": True},
        )


@pytest.mark.parametrize(
    "bad",
    [
        SVG.replace("<text", "<script>alert(1)</script><text"),
        SVG.replace("<text", "<foreignObject/><text"),
        SVG.replace("<text x=", '<text onload="alert(1)" x='),
        SVG.replace("<text x=", '<use href="https://example.com/a"/><text x='),
        SVG.replace("fill:black", "fill:url(https://example.com/image)"),
        SVG.replace("#unstable text", "body"),
        SVG.replace("#unstable text", "#unstable + body"),
        SVG.replace("#unstable text", "#unstable,body"),
        '<!DOCTYPE svg [<!ENTITY x "boom">]>' + SVG,
        '<?xml-stylesheet href="https://example.com/evil.css"?>' + SVG,
        SVG.replace('id="desc"', 'id="title"'),
        SVG.replace("0 0 100 100", "0 0 NaN 100"),
    ],
)
def test_rejects_unsafe_svg(bad: str) -> None:
    with pytest.raises((ValueError, ET.ParseError)):
        normalize_svg(bad.encode(), "fig-test-1")


def test_random_svg_ids_do_not_change_normalized_output() -> None:
    first = SVG.replace("unstable", "random-123")
    second = SVG.replace("unstable", "random-456")
    assert normalize_svg(first.encode(), "fig-test-1") == normalize_svg(
        second.encode(), "fig-test-1"
    )


def test_static_build_is_reproducible_and_sources_are_unchanged(source_root: Path) -> None:
    source = source_root / "course/prototype/diagrams.md"
    before = source.read_bytes()
    a = build(source_root, renderer=fake_renderer, fingerprint={"test": True})
    b = build(
        source_root, "build/course-verify", renderer=fake_renderer, fingerprint={"test": True}
    )
    assert a["site_sha256"] == b["site_sha256"]
    assert a["diagrams"] == 2
    assert source.read_bytes() == before
    text = (source_root / "build/course/prototype.html").read_text()
    assert "unsafe-inline" not in text and "onclick=" not in text
    assert "technical-requirements.html#model" in text
    assert "assets/viewer.js" in text
    assert not (source_root / "build/course/node_modules").exists()


def test_failure_does_not_overwrite_existing_output(source_root: Path) -> None:
    build(source_root, renderer=fake_renderer, fingerprint={"test": True})
    target = source_root / "build/course/index.html"
    before = target.read_bytes()

    def fail(*args: object) -> bytes:
        raise ValueError("invalid diagram")

    with pytest.raises(ValueError):
        build(source_root, renderer=fail, fingerprint={"test": True})
    assert target.read_bytes() == before


@pytest.mark.parametrize(
    "path", ["/tmp/site", "../outside", "build", "course", "build/course/../x"]
)
def test_rejects_broad_or_escaping_output(source_root: Path, path: str) -> None:
    with pytest.raises(ValueError):
        build(source_root, path, renderer=fake_renderer, fingerprint={"test": True})


def test_refuses_output_with_unowned_files(source_root: Path) -> None:
    build(source_root, renderer=fake_renderer, fingerprint={"test": True})
    (source_root / "build/course/user-file.txt").write_text("preserve")
    with pytest.raises(ValueError, match="unexpected"):
        build(source_root, renderer=fake_renderer, fingerprint={"test": True})
    assert (source_root / "build/course/user-file.txt").read_text() == "preserve"


def test_subprocess_environment_excludes_secrets(
    source_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("API_TOKEN", "fixture-not-a-real-secret")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "fixture")
    assert set(clean_env(source_root)) == {"PATH", "HOME", "LANG"}


def test_only_explicit_sources_are_published(source_root: Path) -> None:
    (source_root / ".env").write_text("do-not-copy")
    (source_root / "course/not-public.md").write_text("not on allowlist")
    build(source_root, renderer=fake_renderer, fingerprint={"test": True})
    for file in (source_root / "build/course").rglob("*"):
        if file.is_file():
            assert b"do-not-copy" not in file.read_bytes()
    index = json.loads((source_root / "build/course/diagram-index.json").read_text())
    assert len(index["diagrams"]) == 2


def test_landing_reader_and_roadmap_follow_manifest(source_root: Path) -> None:
    build(source_root, renderer=fake_renderer, fingerprint={"test": True})
    dest = source_root / "build/course"
    landing = (dest / "index.html").read_text()
    assert 'class="hero"' in landing and 'id="roadmap-svg"' in landing
    assert 'id="program"' in landing and 'class="terminal' in landing
    assert "Полные лекции ещё не опубликованы" in landing
    _, ordered = curriculum(source_root)
    svg = ET.fromstring(roadmap(ordered))
    links = svg.findall("{http://www.w3.org/2000/svg}a")
    assert [node.attrib["href"] for node in links] == [url(item["id"]) for item in ordered]
    assert all((dest / node.attrib["href"]).is_file() for node in links)
    standalone = ET.fromstring((dest / "assets/roadmap.svg").read_bytes())
    for link in standalone.findall("{http://www.w3.org/2000/svg}a"):
        assert (dest / "assets" / link.attrib["href"]).resolve().is_file()
    reader = (dest / "topic-0000.html").read_text()
    assert 'class="course-sidebar"' in reader and 'class="lecture-sidebar"' in reader
    assert 'href="#outline-section"' in reader and 'id="outline-section"' in reader
    assert 'aria-current="page"' in reader and "Fixture outline only" in reader
    assert 'href="topic-0001.html">Следующая' in reader
    reader = (dest / "topic-0001.html").read_text()
    assert 'href="topic-0002.html">Следующая' in reader  # Canonical order matches numeric ID.
    assert 'href="topic-0000.html">← Предыдущая' in reader


def test_roadmap_escapes_metadata_not_arbitrary_svg(source_root: Path) -> None:
    _, ordered = curriculum(source_root)
    ordered[0]["title"] = '<script onload="bad"> & "unsafe"'
    svg = ET.fromstring(roadmap(ordered))
    assert not svg.findall(".//{http://www.w3.org/2000/svg}script")
    assert all(not any(k.startswith("on") for k in node.attrib) for node in svg.iter())
    assert svg.find("{http://www.w3.org/2000/svg}a").attrib["href"] == "topic-0000.html"


@pytest.mark.parametrize("identifier", [-1, True, "../.env", 10000])
def test_roadmap_rejects_unsafe_page_identifiers(identifier: object) -> None:
    with pytest.raises(ValueError):
        url(identifier)


def test_rejects_duplicated_curriculum_order(source_root: Path) -> None:
    path = source_root / "course/manifest.json"
    manifest = json.loads(path.read_text())
    manifest["teaching_order"].append(0)
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="curriculum order"):
        build(source_root, renderer=fake_renderer, fingerprint={"test": True})


@pytest.mark.parametrize(
    "body",
    [
        '<p id="roadmap"></p><svg id="roadmap"></svg>',
        '<a href="missing.html">broken</a>',
        '<a href="#missing">broken</a>',
        '<a href="../.env">escape</a>',
    ],
)
def test_generated_output_rejects_duplicate_ids_and_broken_links(body: str) -> None:
    with pytest.raises(ValueError):
        verify_links({"index.html": body.encode()})

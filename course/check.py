"""Offline course governance; metadata checks do not verify educational truth."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

STATES = {"outline", "draft", "editorial-reviewed", "technically-verified", "reviewed"}
SKILLS = {
    "technical-markdown-lectures",
    "technical-editorial-review",
    "technical-claim-verification",
}
REVIEW_INPUTS = (
    "course/technical-requirements.md",
    "course/editorial-guidelines.md",
    "course/glossary.md",
    "course/diagram-config.json",
    "course/toolchain.json",
    "course/skills/technical-markdown-lectures/SKILL.md",
    "course/skills/technical-editorial-review/SKILL.md",
    "course/skills/technical-claim-verification/SKILL.md",
)


def parser() -> MarkdownIt:
    return MarkdownIt("commonmark").enable("table")


def contained(root: Path, name: str) -> Path:
    """Disallow absolute/escaping paths and symlinks, including contained symlinks."""
    path = root / name
    if Path(name).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"escaping path: {name}")
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"symlink path: {name}")
        current = current.parent
        if not current.is_relative_to(root):
            break
    if not path.is_file():
        raise ValueError(f"missing file: {name}")
    return path


def load_json(root: Path, name: str) -> dict:
    value = json.loads(contained(root, name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {name}")
    return value


def heading_anchors(text: str) -> set[str]:
    tokens = parser().parse(text)
    seen: dict[str, int] = {}
    result: set[str] = set()
    for i, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        children = tokens[i + 1].children or []
        title = "".join(c.content for c in children if c.type in {"text", "code_inline"})
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def local_references(root: Path, path: Path) -> list[Path]:
    refs = []
    for token in parser().parse(path.read_text(encoding="utf-8")):
        for child in token.children or []:
            if child.type not in {"link_open", "image"}:
                continue
            target = child.attrGet("href" if child.type == "link_open" else "src") or ""
            url = urlsplit(target)
            if url.scheme:
                if url.scheme != "https" or not url.netloc:
                    raise ValueError(f"unsupported URL: {target}")
                if child.type == "image":
                    raise ValueError(f"external image: {target}")
                continue
            if url.netloc or url.query:
                raise ValueError(f"unsupported local URL: {target}")
            dest = path.parent / unquote(url.path) if url.path else path
            resolved = contained(root, str(dest.relative_to(root)))
            if url.fragment and resolved.suffix == ".md":
                if unquote(url.fragment) not in heading_anchors(
                    resolved.read_text(encoding="utf-8")
                ):
                    raise ValueError(f"missing anchor: {target}")
            refs.append(resolved)
    return refs


def input_digest(root: Path, lecture: dict) -> str:
    """Bind receipts to prose, source map, plans, assets and centrally owned review inputs."""
    names = {*REVIEW_INPUTS, lecture["path"], lecture["plan"], "course/sources.json"}
    path = contained(root, lecture["path"])
    for token in parser().parse(path.read_text(encoding="utf-8")):
        for child in token.children or []:
            if child.type == "image":
                url = urlsplit(child.attrGet("src") or "")
                if url.scheme or url.netloc:
                    raise ValueError("external review asset")
                dest = path.parent / unquote(url.path)
                names.add(str(contained(root, str(dest.relative_to(root))).relative_to(root)))
    h = hashlib.sha256()
    for name in sorted(names):
        h.update(name.encode() + b"\0")
        h.update(hashlib.sha256(contained(root, name).read_bytes()).digest())
    h.update(
        json.dumps(
            {k: v for k, v in lecture.items() if k not in {"review", "status"}},
            sort_keys=True,
            ensure_ascii=False,
        ).encode()
    )
    return h.hexdigest()


def check_review(root: Path, lecture: dict) -> None:
    status = lecture["status"]
    if status in {"outline", "draft"}:
        return
    if not isinstance(lecture.get("review"), str):
        raise ValueError("missing review receipt")
    receipt = load_json(root, lecture["review"])
    schema = receipt.get("schema_version")
    if schema not in {1, 2} or receipt.get("lecture_id") != lecture["id"]:
        raise ValueError("receipt identity mismatch")
    if not receipt.get("reviewer") or not SKILLS.issubset(set(receipt.get("skills", []))):
        raise ValueError("missing reviewer/skills")
    date = datetime.fromisoformat(receipt.get("checked_at", "").replace("Z", "+00:00"))
    if date.utcoffset() is None or date.utcoffset().total_seconds() != 0:
        raise ValueError("receipt timestamp must be UTC")
    if receipt.get("input_digest") != input_digest(root, lecture):
        raise ValueError("stale review receipt")
    passes = receipt.get("passes", {})
    required = ["editorial"]
    if status in {"technically-verified", "reviewed"}:
        required += ["technical", "recheck"]
        claims = receipt.get("claims")
        if not isinstance(claims, list) or not claims:
            raise ValueError("missing claim verification")
        for claim in claims:
            if not claim.get("location") or claim.get("verdict") != "verified":
                raise ValueError("unverified claim")
            source = claim.get("source", "")
            if not source.startswith("https://"):
                contained(root, source.split("#")[0])
    if any(passes.get(p) is not True for p in required):
        raise ValueError("incomplete review passes")
    findings = receipt.get("findings")
    if not isinstance(findings, list):
        raise ValueError("missing findings record")
    if any(
        f.get("severity") in {"major", "blocking"} and f.get("resolved") is not True
        for f in findings
    ):
        raise ValueError("unresolved substantial finding")
    if status == "reviewed":
        text = contained(root, lecture["path"]).read_text(encoding="utf-8")
        diagrams = [t for t in parser().parse(text) if t.type == "fence" and t.info == "mermaid"]
        if diagrams:
            toolchain = load_json(root, "course/toolchain.json")
            if toolchain.get("render_status") != "verified":
                raise ValueError("missing verified renderer")
            if schema == 1 and passes.get("visual") is not True:
                raise ValueError("missing actual renderer/visual gate")
            if schema == 2 and passes.get("diagram_semantics") is not True:
                raise ValueError("missing text-only diagram semantics review")
        elif not receipt.get("diagram_waiver"):
            raise ValueError("missing diagram or documented waiver")
        if schema == 2 and (passes.get("visual") is True or "visual" in passes):
            raise ValueError("text-only review must not claim visual pass")
        from course.publication import check_publication

        check_publication(root, lecture)


def markdown_issues(root: Path, path: Path, *, lecture: bool = False) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues = []
    if "\r" in text or not text.endswith("\n"):
        issues.append("expected UTF-8/LF and final newline")
    tokens = parser().parse(text)
    level = 0
    top = 0
    lines = text.splitlines()
    for token in tokens:
        if token.type == "heading_open":
            new = int(token.tag[1:])
            top += new == 1
            if new > level + 1:
                issues.append("skipped heading level")
            level = new
        if token.type in {"html_block", "html_inline"} or any(
            c.type == "html_inline" for c in token.children or []
        ):
            issues.append("raw HTML is not allowed")
        if token.type == "fence":
            if not token.info:
                issues.append("missing fence language")
            close = r"^\s*" + re.escape(token.markup[0]) + "{" + str(len(token.markup)) + r",}\s*$"
            if token.map and not re.match(close, lines[token.map[1] - 1]):
                issues.append("unclosed fence")
            if token.info == "mermaid":
                if "accTitle:" not in token.content or "accDescr:" not in token.content:
                    issues.append("missing Mermaid accessibility labels")
                if re.search(r"(?m)^\s*click\b|%%\{|<[^>]+>", token.content):
                    issues.append("unsafe Mermaid directive/HTML")
    if top != 1:
        issues.append("expected exactly one H1")
    if lecture and any(t.type == "code_block" for t in tokens):
        issues.append("use language-tagged fences, not indented code")
    try:
        local_references(root, path)
    except (ValueError, OSError) as exc:
        issues.append(str(exc))
    return issues


def collect_issues(root: Path) -> list[str]:
    root = root.resolve()
    issues = []
    try:
        m = load_json(root, "course/manifest.json")
        for required in (
            *REVIEW_INPUTS,
            "course/README.md",
            "course/syllabus.md",
            "course/source-index.md",
            "course/templates/module.md",
            "course/templates/lecture.md",
            "course/templates/review.md",
            "course/templates/review.json",
            "course/build-status.md",
        ):
            contained(root, required)
        if (
            m.get("schema_version") != 1
            or m.get("format") != "theory-only"
            or m.get("student_tasks") != []
        ):
            raise ValueError("invalid course format/schema or student tasks")
        ls = m["lectures"]
        ids = [x["id"] for x in ls]
        if len(ids) != 27 or set(ids) != set(range(27)):
            raise ValueError("duplicate/missing lecture ID")
        order = m["teaching_order"] + m["optional_order"]
        if (
            len(order) != 27
            or set(order) != set(ids)
            or m["teaching_order"] != list(range(26))
            or m["optional_order"] != [26]
        ):
            raise ValueError("invalid teaching order")
        sources = load_json(root, "course/sources.json")["sources"]
        source_ids = {s["id"] for s in sources}
        if len(source_ids) != len(sources):
            raise ValueError("duplicate source ID")
        planning = load_json(root, "plan/steps/lections/lecture-map.json")
        if order != planning["teaching_order"] + planning["optional_order"]:
            raise ValueError("planning order drift")
        pos = {x: i for i, x in enumerate(order)}
        concepts: set[str] = set()
        paths: set[str] = set()
        for lecture in ls:
            try:
                if (
                    lecture["status"] not in STATES
                    or not lecture.get("outcomes")
                    or not lecture.get("known_gaps")
                ):
                    raise ValueError("invalid status/missing outcomes or gaps")
                if lecture["track"] != ("extension" if lecture["id"] == 26 else "core"):
                    raise ValueError("invalid track")
                planned = next(x for x in planning["lectures"] if x["id"] == lecture["id"])
                if any(
                    lecture[k] != planned[k] for k in ("slug", "title", "prerequisites", "concepts")
                ):
                    raise ValueError("planning topic drift")
                if any(
                    p not in pos or pos[p] >= pos[lecture["id"]] for p in lecture["prerequisites"]
                ):
                    raise ValueError("dependency cycle/order violation")
                for c in lecture["concepts"]:
                    if c in concepts:
                        raise ValueError("duplicate primary concept owner")
                    concepts.add(c)
                expected = f"course/lectures/LECTURE-{lecture['id']:04d}-{lecture['slug']}.md"
                if lecture["path"] != expected or lecture["path"] in paths:
                    raise ValueError("invalid/duplicate lecture path")
                directory = "extensions" if lecture["id"] == 26 else "modules"
                module = f"module-{lecture['id']:02d}-{lecture['slug']}"
                if lecture["outline"] != f"course/{directory}/{module}/README.md":
                    raise ValueError("invalid module outline path")
                if lecture["plan"] != f"plan/steps/lections/{planned['filename']}":
                    raise ValueError("invalid lecture plan path")
                paths.add(lecture["path"])
                for name in (lecture["outline"], lecture["plan"]):
                    contained(root, name)
                if len(lecture["sources"]) < 2 or any(
                    s["id"] not in source_ids for s in lecture["sources"]
                ):
                    raise ValueError("missing source mapping")
                if lecture["status"] == "outline":
                    if (root / lecture["path"]).exists() or lecture.get("review"):
                        raise ValueError("outline has lecture/review: synchronize status")
                else:
                    contained(root, lecture["path"])
                check_review(root, lecture)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                issues.append(f"lecture {lecture.get('id')}: {exc}")
        for path in (root / "course").rglob("*.md"):
            if "node_modules" in path.relative_to(root / "course").parts:
                continue  # Installed tool dependencies are not course prose/publication sources.
            contained(root, str(path.relative_to(root)))
            if "skills" in path.parts:
                continue  # Skills intentionally contain YAML frontmatter, not publishable prose.
            issues += [
                f"{path.relative_to(root)}: {e}"
                for e in markdown_issues(
                    root, path, lecture=path.parent.name == "lectures" and path.name != "README.md"
                )
            ]
        for p in (root / "course/lectures").glob("LECTURE-*.md"):
            if str(p.relative_to(root)) not in paths:
                issues.append(f"unregistered lecture: {p.name}")
        if any(
            p.name in {"labs", "assignments", "submissions"}
            for p in (root / "course").rglob("*")
            if p.is_dir() and "node_modules" not in p.relative_to(root / "course").parts
        ):
            issues.append("student-practice directory is prohibited")
    except (ValueError, KeyError, TypeError, AttributeError, StopIteration, OSError) as exc:
        issues.append(f"course: {exc}")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--digest", type=int)
    args = ap.parse_args()
    if args.digest is not None:
        ls = load_json(args.root, "course/manifest.json")["lectures"]
        print(input_digest(args.root, next(x for x in ls if x["id"] == args.digest)))
        return 0
    issues = collect_issues(args.root)
    print(
        "\n".join(issues)
        if issues
        else "course governance: PASS (not editorial/render verification)"
    )
    return bool(issues)


if __name__ == "__main__":
    sys.exit(main())

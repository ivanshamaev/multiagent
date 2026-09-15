"""Bounded, local static-site prototype with build-time Mermaid SVG."""

# ruff: noqa: RUF001
# Russian UI labels deliberately contain Cyrillic characters.

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import math
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from urllib.parse import unquote, urlsplit

import tinycss2

from course.check import check_review, contained, input_digest, markdown_issues, parser
from course.publication import check_publication
from course.site import build_pages, curriculum, verify_links
from course.site import url as topic_url

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
PAGES = {
    "course/prototype/diagrams.md": "index.html",
    "course/technical-requirements.md": "technical-requirements.html",
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; style-src-attr 'none'; "
    "font-src 'self'; img-src 'self'; connect-src 'none'; object-src 'none'; "
    "base-uri 'none'; form-action 'none'"
)
TAGS = {
    "svg",
    "g",
    "defs",
    "marker",
    "path",
    "rect",
    "text",
    "tspan",
    "line",
    "polyline",
    "polygon",
    "circle",
    "ellipse",
    "clipPath",
    "linearGradient",
    "radialGradient",
    "stop",
    "title",
    "desc",
    "style",
    "use",
    "symbol",
    "filter",
    "feDropShadow",
}
ATTRS = {
    "id",
    "class",
    "style",
    "role",
    "viewBox",
    "width",
    "height",
    "x",
    "y",
    "x1",
    "y1",
    "x2",
    "y2",
    "dx",
    "dy",
    "d",
    "rx",
    "ry",
    "r",
    "cx",
    "cy",
    "points",
    "fill",
    "stroke",
    "opacity",
    "fill-opacity",
    "stroke-opacity",
    "stroke-width",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "transform",
    "marker-end",
    "marker-start",
    "marker-mid",
    "markerWidth",
    "markerHeight",
    "markerUnits",
    "refX",
    "refY",
    "orient",
    "preserveAspectRatio",
    "text-anchor",
    "dominant-baseline",
    "alignment-baseline",
    "font-size",
    "font-family",
    "font-weight",
    "font-style",
    "font-variant",
    "lengthAdjust",
    "textLength",
    "href",
    "clip-path",
    "clipPathUnits",
    "gradientUnits",
    "gradientTransform",
    "offset",
    "stop-color",
    "stop-opacity",
    "focusable",
    "tabindex",
    "version",
    "color",
    "filter",
    "stdDeviation",
    "flood-opacity",
    "flood-color",
    "name",
    "fill-rule",
    "clip-rule",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_css(css: str, ids: set[str]) -> None:
    # Generated CSS only. Reject escapes that could disguise URLs/imports rather than decoding them.
    if "\\" in css or re.search(
        r"@import|@font-face|expression\s*\(|javascript:|behavior\s*:|-moz-binding", css, re.I
    ):
        raise ValueError("unsafe SVG CSS")
    for match in re.finditer(r"url\s*\((.*?)\)", css, re.I | re.S):
        target = match.group(1).strip(" \t\n\"'")
        if not target.startswith("#") or target[1:] not in ids:
            raise ValueError("external or missing SVG CSS reference")


def declarations(content: str | list) -> None:
    rules = tinycss2.parse_declaration_list(content, skip_comments=True, skip_whitespace=True)
    if any(rule.type != "declaration" for rule in rules):
        raise ValueError("invalid SVG CSS declarations")


def scoped_css(css: str, root_id: str, key: str) -> str:
    names = {}
    for rule in tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True):
        if rule.type == "qualified-rule":
            selectors = tinycss2.serialize(rule.prelude).split(",")
            for selector in selectors:
                selector = selector.strip()
                if not re.match(r"^#" + re.escape(root_id) + r"(?=[\s.:[>]|$)", selector):
                    raise ValueError("SVG CSS selector escapes diagram root")
                if "+" in selector or "~" in selector:
                    raise ValueError("SVG CSS sibling selector")
            declarations(rule.content)
        elif rule.type == "at-rule" and rule.lower_at_keyword == "keyframes":
            name = tinycss2.serialize(rule.prelude).strip()
            if not re.fullmatch(r"[a-zA-Z0-9-]+", name):
                raise ValueError("invalid SVG animation name")
            names[name] = f"{key}-{name}"
            for frame in tinycss2.parse_rule_list(
                rule.content, skip_comments=True, skip_whitespace=True
            ):
                if frame.type != "qualified-rule":
                    raise ValueError("invalid SVG keyframe")
                label = tinycss2.serialize(frame.prelude).strip()
                if not all(re.fullmatch(r"from|to|[0-9.]+%", x.strip()) for x in label.split(",")):
                    raise ValueError("invalid SVG keyframe selector")
                declarations(frame.content)
        else:
            raise ValueError("disallowed SVG CSS rule")
    for old, new in names.items():
        css = re.sub(r"(?<![\w-])" + re.escape(old) + r"(?![\w-])", new, css)
    return css


def normalize_svg(data: bytes, key: str) -> tuple[str, str]:
    """Reject active/external content; namespace IDs and extract inline styles for strict CSP."""
    if len(data) > 4_000_000 or re.search(rb"<!DOCTYPE|<!ENTITY|<\?(?!xml\s)", data, re.I):
        raise ValueError("oversized/DTD SVG")
    root = ET.fromstring(data)
    if root.tag != f"{{{SVG_NS}}}svg" or not re.fullmatch(r"fig-[a-z0-9-]+", key):
        raise ValueError("invalid SVG root/figure key")
    ids = [e.attrib["id"] for e in root.iter() if "id" in e.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate SVG IDs")
    mapping = {old: f"{key}-{i}" for i, old in enumerate(ids)}
    if root.get("id") is None:
        root.set("id", f"{key}-root")
    raw_root_id = root.attrib["id"]
    css_parts = []
    parents = {child: parent for parent in root.iter() for child in parent}
    for elem in list(root.iter()):
        if not elem.tag.startswith(f"{{{SVG_NS}}}") or elem.tag.split("}")[-1] not in TAGS:
            raise ValueError(f"disallowed SVG element: {elem.tag}")
        if elem.tag == f"{{{SVG_NS}}}style":
            css = elem.text or ""
            # This exact feature comes only from our renderer font stylesheet; published fonts
            # are local assets. No SVG font-face/data/external refs survive extraction.
            safe_css(css, set(ids))
            css_parts.append(scoped_css(css, raw_root_id, key))
            parents[elem].remove(elem)
        for attr, value in list(elem.attrib.items()):
            local = attr.split("}")[-1]
            if local not in ATTRS and not local.startswith(("aria-", "data-")):
                raise ValueError(f"disallowed SVG attribute: {local}")
            if local == "href" and (not value.startswith("#") or value[1:] not in mapping):
                raise ValueError("external or missing SVG href")
            safe_css(value, set(ids))
            if local == "style":
                declarations(value)
                stable_value = rewrite_refs(value, mapping)
                name = f"{key}-style-{sha(stable_value.encode())[:12]}"
                elem.set("class", (elem.get("class", "") + " " + name).strip())
                css_parts.append(f".{name}{{{stable_value}}}")
                del elem.attrib[attr]
    old_pattern = (
        re.compile(
            r"(?<![\w-])(?:"
            + "|".join(re.escape(x) for x in sorted(ids, key=len, reverse=True))
            + r")(?![\w-])"
        )
        if ids
        else None
    )

    def replace(value: str) -> str:
        return (
            old_pattern.sub(lambda match: mapping[match.group()], value) if old_pattern else value
        )

    for elem in root.iter():
        for attr, value in list(elem.attrib.items()):
            elem.set(attr, replace(value))
    css = "\n".join(sorted(set(replace(part) for part in css_parts)))
    view = [float(v) for v in root.attrib["viewBox"].replace(",", " ").split()]
    if (
        len(view) != 4
        or not all(math.isfinite(v) for v in view)
        or not all(0 < v < 20_000 for v in view[2:])
    ):
        raise ValueError("invalid SVG viewBox")
    if not any(e.tag == f"{{{SVG_NS}}}title" for e in root.iter()) or not any(
        e.tag == f"{{{SVG_NS}}}desc" for e in root.iter()
    ):
        raise ValueError("SVG missing accessible title/description")
    root.set("data-original-viewbox", root.attrib["viewBox"])
    if key.startswith("fig-topic-"):
        minimum = min(1100, max(320, math.ceil(view[2])))
        css += f"\n#{root.attrib['id']}{{min-width:{minimum}px}}"
    return ET.tostring(root, encoding="unicode"), css


def rewrite_refs(value: str, mapping: dict[str, str]) -> str:
    if not mapping:
        return value
    pattern = re.compile(
        r"(?<![\w-])(?:"
        + "|".join(re.escape(x) for x in sorted(mapping, key=len, reverse=True))
        + r")(?![\w-])"
    )
    return pattern.sub(lambda match: mapping[match.group()], value)


def clean_env(root: Path) -> dict[str, str]:
    return {
        "PATH": f"{root / 'course/node_modules/node/bin'}:{os.defpath}",
        "HOME": os.environ.get("HOME", "/nonexistent"),
        "LANG": "C.UTF-8",
    }


def tool_fingerprint(root: Path) -> dict:
    node = contained(root, "course/node_modules/node/bin/node")
    script = (
        "import p from 'puppeteer'; import fs from 'node:fs';"
        "const v=n=>JSON.parse(fs.readFileSync('node_modules/'+n+'/package.json')).version;"
        "console.log(JSON.stringify({"
        "node:process.version,browser:await p.executablePath(),"
        "cli:v('@mermaid-js/mermaid-cli'),mermaid:v('mermaid')}));"
    )
    run = subprocess.run(
        [str(node), "--input-type=module", "-e", script],
        cwd=root / "course",
        env=clean_env(root),
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    result = json.loads(run.stdout)
    browser = subprocess.run(
        [result.pop("browser"), "--version"],
        env=clean_env(root),
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    result["browser_version"] = browser.stdout.strip()
    result["lock_sha256"] = sha(contained(root, "course/package-lock.json").read_bytes())
    result["diagram_config_sha256"] = sha(
        contained(root, "course/diagram-config.json").read_bytes()
    )
    result["builder_sha256"] = sha(contained(root, "course/build.py").read_bytes())
    font_match = subprocess.run(
        ["fc-match", "-f", "%{file}", "Noto Sans"],
        env=clean_env(root),
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    system_font = Path(font_match.stdout)
    if not system_font.resolve().is_relative_to(Path("/usr/share/fonts")):
        raise ValueError("renderer font must be an explicit system font under /usr/share/fonts")
    result["system_render_font_sha256"] = sha(system_font.read_bytes())
    result["font_sha256"] = {
        name: sha(
            contained(
                root,
                f"course/node_modules/@fontsource/noto-sans/files/noto-sans-{name}-400-normal.woff2",
            ).read_bytes()
        )
        for name in ("latin", "cyrillic")
    }
    return result


def font_css(root: Path, *, embedded: bool) -> str:
    css = []
    for name, glyphs in (("latin", "U+0000-00FF,U+2000-206F"), ("cyrillic", "U+0400-052F")):
        filename = f"noto-sans-{name}-400-normal.woff2"
        if embedded:
            data = contained(
                root, f"course/node_modules/@fontsource/noto-sans/files/{filename}"
            ).read_bytes()
            src = "data:font/woff2;base64," + base64.b64encode(data).decode()
        else:
            src = f"{filename}"
        css.append(
            '@font-face{font-family:"Noto Sans";font-style:normal;font-weight:400;'
            f'src:url("{src}") format("woff2");unicode-range:{glyphs}}}'
        )
    return "\n".join(css)


def render_cli(root: Path, definition: str, work: Path, key: str) -> bytes:
    if len(definition.encode()) > 64_000:
        raise ValueError("oversized Mermaid source")
    if re.search(r"%%\{|(?m:^\s*click\b)|<[^>]+>", definition):
        raise ValueError("unsafe Mermaid source")
    source, target = work / f"{key}.mmd", work / f"{key}.svg"
    source.write_text(definition, encoding="utf-8")
    css = work / "fonts.css"
    css.write_text(font_css(root, embedded=True), encoding="utf-8")
    node = contained(root, "course/node_modules/node/bin/node")
    cli = contained(root, "course/node_modules/@mermaid-js/mermaid-cli/src/cli.js")
    subprocess.run(
        [
            str(node),
            str(cli),
            "-i",
            str(source),
            "-o",
            str(target),
            "-c",
            str(contained(root, "course/diagram-config.json")),
            "-C",
            str(css),
            "-b",
            "transparent",
            "-q",
        ],
        cwd=root / "course",
        env=clean_env(root),
        capture_output=True,
        timeout=120,
        check=True,
    )
    return target.read_bytes().replace(font_css(root, embedded=True).encode(), b"")


def page_template(title: str, body: str, diagram_css: str) -> str:
    return (
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<meta http-equiv="Content-Security-Policy" content="{html.escape(CSP, quote=True)}">'
        f'<title>{html.escape(title)}</title><link rel="icon" href="assets/favicon.svg">'
        '<link rel="stylesheet" href="assets/site.css">'
        f'<link rel="stylesheet" href="assets/{diagram_css}">'
        '<script src="assets/viewer.js" defer></script></head><body>'
        '<a class="skip" href="#content">К содержанию</a><header><nav aria-label="Страницы">'
        '<a class="brand" href="index.html">ADP<span> / AGENT ENGINEERING</span></a>'
        '<div class="top-links"><a href="index.html#program">Программа</a> · '
        '<a href="index.html#roadmap">Roadmap</a> · <a href="index.html#about">О курсе</a> · '
        '<a href="prototype.html">Диаграммы</a> · '
        '<a href="technical-requirements.html">Требования</a> · '
        '<a href="references.html">References</a></div></nav></header>'
        f'<main id="content">{body}</main>'
        "<footer>Локальная сборка теоретического курса.</footer>"
        "</body></html>\n"
    )


def figure_markup(key: str, svg: str, title: str, index: int) -> str:
    actions = (
        ("zoom-in", "Увеличить"),
        ("zoom-out", "Уменьшить"),
        ("reset", "Сбросить"),
        ("wheel", "Масштаб колёсиком"),
        ("pan", "Перемещение схемы"),
        ("fullscreen", "Развернуть"),
    )
    buttons = "".join(
        f'<button type="button" data-action="{action}" aria-controls="{key}-canvas"'
        f"{' aria-pressed="false"' if action in {'wheel', 'pan'} else ''}"
        f">{label}</button>"
        for action, label in actions
    )
    return (
        f'<figure class="diagram" id="{key}"><div class="controls" hidden>{buttons}'
        '<output aria-live="polite">100%</output></div>'
        f'<div class="canvas" id="{key}-canvas" tabindex="0" role="region" '
        f'aria-label="Диаграмма {index}: {html.escape(title, quote=True)}">{svg}</div>'
        f"<figcaption>Рисунок {index}: {html.escape(title)}. "
        f'<a href="assets/{key}.svg">Открыть SVG отдельно</a>. '
        "Широкие схемы прокручиваются внутри области; в активной области: +/- — масштаб, "
        "0 — сброс, стрелки — перемещение.</figcaption></figure>\n"
    )


def build(
    root: Path,
    output: str = "build/course",
    *,
    renderer: Callable = render_cli,
    fingerprint: dict | None = None,
    candidate_ids: tuple[int, ...] = (),
) -> dict:
    root = root.resolve()
    if not re.fullmatch(r"build/course(?:-[a-z0-9-]+)?", output):
        raise ValueError("output must be a dedicated build/course[-label] directory")
    if candidate_ids and output == "build/course":
        raise ValueError("review candidates require isolated labelled output")
    dest = root / output
    if any(p.is_symlink() for p in (root / "build", dest)):
        raise ValueError("symlink output")
    files: dict[str, bytes] = {}
    diagrams, references = [], {}
    _, ordered = curriculum(root)
    mapping = {item["id"]: item for item in ordered}
    if len(set(candidate_ids)) != len(candidate_ids) or any(
        type(identifier) is not int or identifier not in mapping for identifier in candidate_ids
    ):
        raise ValueError("invalid review candidate identity")
    selected = {item["id"] for item in ordered if item["status"] == "reviewed"}
    selected.update(candidate_ids)
    for identifier in selected:
        item = mapping[identifier]
        if item["status"] not in {"technically-verified", "reviewed"}:
            raise ValueError("candidate requires completed technical review")
        check_review(root, item)
    pages = dict(PAGES)
    source_ids = {
        item["path"] if item["id"] in selected else item["outline"]: item["id"] for item in ordered
    }
    pages.update({name: topic_url(identifier) for name, identifier in source_ids.items()})
    link_pages = {item["outline"]: topic_url(item["id"]) for item in ordered}
    link_pages.update({item["path"]: topic_url(item["id"]) for item in ordered})
    link_pages.update(pages)
    outlines: dict[int, tuple[str, str]] = {}
    fp = fingerprint or tool_fingerprint(root)
    for identifier in selected - set(candidate_ids):
        if check_publication(root, mapping[identifier])["renderer"] != fp:
            raise ValueError("publication renderer fingerprint mismatch")
    for name in ("site.css", "viewer.js", "favicon.svg"):
        files[f"assets/{name}"] = contained(root, f"course/static/{name}").read_bytes()
    files["assets/site.css"] = (
        font_css(root, embedded=False).encode() + b"\n" + files["assets/site.css"]
    )
    for name in ("latin", "cyrillic"):
        filename = f"noto-sans-{name}-400-normal.woff2"
        files[f"assets/{filename}"] = contained(
            root, f"course/node_modules/@fontsource/noto-sans/files/{filename}"
        ).read_bytes()
    files["assets/FONT-LICENSE.txt"] = contained(
        root, "course/node_modules/@fontsource/noto-sans/LICENSE"
    ).read_bytes()
    (root / "build").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="course-render-", dir=root / "build") as temp:
        work = Path(temp)
        for source_name, page_name in pages.items():
            path = contained(root, source_name)
            problems = markdown_issues(root, path)
            if problems:
                raise ValueError(f"invalid source {source_name}: {problems}")
            tokens = parser().parse(path.read_text(encoding="utf-8"))
            slug_counts: dict[str, int] = {}
            css_parts, figure_number = [], 0
            title = path.stem
            toc = []
            for i, token in enumerate(tokens):
                if token.type == "heading_open":
                    text = "".join(
                        c.content
                        for c in tokens[i + 1].children or []
                        if c.type in {"text", "code_inline"}
                    )
                    if token.tag == "h1":
                        title = text
                    slug = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
                    count = slug_counts.get(slug, 0)
                    slug_counts[slug] = count + 1
                    token.attrSet("id", f"{slug}-{count}" if count else slug)
                    if token.tag in {"h2", "h3"}:
                        toc.append(
                            f'<li class="toc-{token.tag}"><a href="#{token.attrGet("id")}">'
                            f"{html.escape(text)}</a></li>"
                        )
                if token.type == "fence" and token.info == "mermaid":
                    figure_number += 1
                    if figure_number > 10:
                        raise ValueError("too many diagrams")
                    key = f"fig-{Path(page_name).stem}-{figure_number}"
                    svg, css = normalize_svg(renderer(root, token.content, work, key), key)
                    label_match = re.search(r"accTitle:\s*(.+)", token.content)
                    label = label_match.group(1).strip() if label_match else "Диаграмма"
                    files[f"assets/{key}.svg"] = svg.encode()
                    files[f"assets/{key}.css"] = css.encode()
                    standalone = svg
                    files[f"assets/{key}.css"] = (
                        font_css(root, embedded=False) + "\n" + css
                    ).encode()
                    files[f"assets/{key}.svg"] = (
                        '<?xml-stylesheet type="text/css" href="' + key + '.css"?>\n' + standalone
                    ).encode()
                    css_parts.append(css)
                    diagrams.append(
                        {
                            "key": key,
                            "source": source_name,
                            "definition_sha256": sha(token.content.encode()),
                            "svg_sha256": sha(files[f"assets/{key}.svg"]),
                            "title": label,
                        }
                    )
                    token.type, token.content = (
                        "html_block",
                        figure_markup(key, svg, label, figure_number),
                    )
                for child in token.children or []:
                    if child.type != "link_open":
                        continue
                    url = urlsplit(child.attrGet("href") or "")
                    if url.scheme:
                        continue
                    target = (path.parent / unquote(url.path)).resolve() if url.path else path
                    relative = str(target.relative_to(root))
                    if relative in link_pages:
                        href = link_pages[relative]
                        if relative == "course/prototype/diagrams.md":
                            href = "prototype.html"
                        if url.fragment:
                            href += "#" + url.fragment
                    else:
                        key = "ref-" + sha(relative.encode())[:12]
                        references[key] = relative
                        href = f"references.html#{key}"
                    child.attrSet("href", href)
            css_name = Path(page_name).stem + "-diagrams.css"
            files[f"assets/{css_name}"] = "\n".join(css_parts).encode()
            body = parser().renderer.render(tokens, parser().options, {})
            if source_name in source_ids:
                if tokens and tokens[0].type == "heading_open" and tokens[0].tag == "h1":
                    body = parser().renderer.render(tokens[3:], parser().options, {})
                identifier = source_ids[source_name]
                outlines[identifier] = (body, "".join(toc))
                if identifier in selected:
                    rendered_hash = sha((body + "\n" + "".join(toc)).encode())
                    if (
                        identifier not in candidate_ids
                        and check_publication(root, mapping[identifier])["rendered_sha256"]
                        != rendered_hash
                    ):
                        raise ValueError("publication rendered artifact mismatch")
            files[page_name] = page_template(title, body, css_name).encode()
    files["prototype.html"] = files["index.html"]
    generated, road = build_pages(root, page_template, figure_markup, outlines, selected)
    files.update(generated)
    files["assets/roadmap.svg"] = (
        '<?xml-stylesheet type="text/css" href="site.css"?>\n'
        + road.replace('href="topic-', 'href="../topic-')
    ).encode()
    files["assets/course-roadmap.svg"] = files["assets/roadmap.svg"]
    files["assets/references-diagrams.css"] = b""
    body = (
        "<h1>Repository references</h1><p>Эти repository materials не скопированы в static output. "
    )
    body += "Пути приведены для contributor provenance, не как опубликованное evidence.</p><dl>"
    body += (
        "".join(
            f'<dt id="{k}">{html.escape(v)}</dt>'
            "<dd>Материал доступен в checkout, не на этом prototype.</dd>"
            for k, v in sorted(references.items())
        )
        + "</dl>"
    )
    files["references.html"] = page_template(
        "Repository references", body, "references-diagrams.css"
    ).encode()
    files["diagram-index.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "toolchain": fp,
                "diagrams": diagrams,
                "lectures": {
                    str(identifier): {
                        "input_digest": input_digest(root, mapping[identifier]),
                        "rendered_sha256": sha(
                            (outlines[identifier][0] + "\n" + outlines[identifier][1]).encode()
                        ),
                        "publication": identifier not in candidate_ids,
                    }
                    for identifier in sorted(selected)
                },
                "source_sha256": {
                    s: sha(contained(root, s).read_bytes())
                    for s in [*pages, "course/manifest.json"]
                },
                "site_generator_sha256": sha(
                    contained(Path(__file__).resolve().parents[1], "course/site.py").read_bytes()
                ),
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode()
    verify_links(files)
    if dest.exists():
        marker = dest / ".course-build.json"
        if not marker.is_file() or marker.is_symlink():
            raise ValueError("refuse non-owned output directory")
        known = set(json.loads(marker.read_text())["files"])
        actual = {str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()}
        if actual != known | {".course-build.json"} or not known.issubset(files):
            raise ValueError("unexpected/stale output files: use a fresh labelled output directory")
        if any(p.is_symlink() for p in dest.rglob("*")):
            raise ValueError("symlink in output")
    dest.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    digest = sha(json.dumps({k: sha(v) for k, v in sorted(files.items())}, sort_keys=True).encode())
    (dest / ".course-build.json").write_text(
        json.dumps({"files": sorted(files), "site_sha256": digest}, sort_keys=True) + "\n"
    )
    return {
        "output": output,
        "files": len(files),
        "diagrams": len(diagrams),
        "site_sha256": digest,
        "toolchain": fp,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default="build/course")
    ap.add_argument("--candidate", type=int, action="append", default=[])
    args = ap.parse_args()
    print(
        json.dumps(
            build(
                Path(__file__).resolve().parents[1],
                args.output,
                candidate_ids=tuple(args.candidate),
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

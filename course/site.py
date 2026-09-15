"""Manifest-driven course preview: plans only, never unreviewed lecture publication."""

# ruff: noqa: RUF001

from __future__ import annotations

import html
import json
import posixpath
import textwrap
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from course.check import contained


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            if identifier in self.ids:
                raise ValueError(f"duplicate generated ID: {identifier}")
            self.ids.add(identifier)
        for field in ("href", "src"):
            if values.get(field):
                self.links.append(values[field])


def verify_links(files: dict[str, bytes]) -> None:
    pages = {}
    for name, content in files.items():
        if name.endswith((".html", ".svg")):
            page = PageLinks()
            page.feed(content.decode())
            pages[name] = page
    for name, page in pages.items():
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme in {"https", "http"}:
                continue
            if parsed.scheme or parsed.netloc:
                raise ValueError("unsupported generated URL")
            target = (
                posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
                if parsed.path
                else name
            )
            if target.startswith(("../", "/")) or target not in files:
                raise ValueError(f"missing generated target: {name}: {link}")
            if (
                parsed.fragment
                and target in pages
                and unquote(parsed.fragment) not in pages[target].ids
            ):
                raise ValueError(f"missing generated anchor: {name}: {link}")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def url(identifier: int) -> str:
    if type(identifier) is not int or not 0 <= identifier <= 9999:
        raise ValueError("invalid lecture identifier")
    return f"topic-{identifier:04d}.html"


def curriculum(root: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads(contained(root, "course/manifest.json").read_text())
    lectures = manifest["lectures"]
    mapping = {item["id"]: item for item in lectures}
    order = manifest["teaching_order"] + manifest["optional_order"]
    if len(mapping) != len(lectures) or len(order) != len(set(order)) or set(order) != set(mapping):
        raise ValueError("invalid curriculum order")
    ordered = [mapping[identifier] for identifier in order]
    for item in ordered:
        url(item["id"])
    return manifest, ordered


def navigation(ordered: list[dict], current: int, published: set[int] | None = None) -> str:
    published = published or set()
    items = []
    for item in ordered:
        active = ' aria-current="page"' if item["id"] == current else ""
        optional = " · optional" if item["track"] == "extension" else ""
        label = "Лекция" if item["id"] in published else "План темы"
        items.append(
            f'<li><a href="{url(item["id"])}"{active}><span class="nav-id">'
            f"{item['id']:02d}</span>{esc(item['title'])}"
            f"<small>{label}{optional}</small></a></li>"
        )
    return '<nav aria-label="Программа курса"><ol>' + "".join(items) + "</ol></nav>"


def outline(
    item: dict, ordered: list[dict], rendered: tuple[str, str], *, full: bool = False
) -> tuple[str, str]:
    mapping = {entry["id"]: entry for entry in ordered}
    prerequisites = (
        " · ".join(
            f'<a href="{url(identifier)}">{identifier:02d} — '
            f"{esc(mapping[identifier]['title'])}</a>"
            for identifier in item["prerequisites"]
        )
        or "Python, SQL и понимание data pipelines."
    )
    body, toc = rendered
    authoring_status = (
        "текст лекции не написан"
        if item["status"] == "outline"
        else "текст подготовлен, но не опубликован"
    )
    label = "Полная лекция" if full else f"План темы · {authoring_status}"
    kind = "LECTURE" if full else "OUTLINE"
    article = (
        '<div class="breadcrumbs"><a href="index.html#program">Курс</a> / '
        f'Тема {item["id"]:02d}</div><div class="eyebrow">MODULE / {kind}</div>'
        f'<h1>{esc(item["title"])}</h1><p class="status">{label}'
        f"{' · optional extension' if item['track'] == 'extension' else ''}</p>"
        '<div class="prerequisites"><strong>Перед этой темой</strong><p>'
        + prerequisites
        + "</p></div>"
        + body
    )
    return article, '<nav aria-label="Оглавление темы"><ol>' + toc + "</ol></nav>"


def roadmap(ordered: list[dict], published: set[int] | None = None) -> str:
    published = published or set()
    height = 115 + len(ordered) * 92
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" id="roadmap-svg" viewBox="0 0 1100 {height}" '
        f'data-original-viewbox="0 0 1100 {height}" role="group" '
        'aria-labelledby="roadmap-title roadmap-desc">',
        '<title id="roadmap-title">Маршрут теоретического курса</title>',
        '<desc id="roadmap-desc">Последовательность core тем, затем optional deployment track. '
        "Метки ЛЕКЦИЯ и ПЛАН различают полные тексты и описания будущих тем. "
        "Prerequisites перечислены на страницах тем.</desc>",
    ]
    for i, item in enumerate(ordered):
        y = 40 + i * 92
        if i and item["track"] != "extension":
            parts.append(f'<path class="road-line" d="M 55 {y - 24} V {y + 24}"/>')
        lines = textwrap.wrap(item["title"], width=72, break_long_words=False)[:2]
        parts.append(
            f'<a href="{url(item["id"])}" aria-label="{esc(item["title"])} — '
            f'{"лекция" if item["id"] in published else "план темы"}" '
            'tabindex="0">'
            f'<rect class="road-node" x="25" y="{y}" width="1040" height="72" rx="0"/>'
            f'<text class="road-number" x="45" y="{y + 45}">{item["id"]:02d}</text>'
        )
        for line_number, line in enumerate(lines):
            parts.append(
                f'<text class="road-label" x="120" y="{y + 27 + line_number * 24}">'
                f"{esc(line)}</text>"
            )
        status = (
            "ЛЕКЦИЯ"
            if item["id"] in published
            else "OPTIONAL"
            if item["track"] == "extension"
            else "ПЛАН"
        )
        parts.append(f'<text class="road-status" x="940" y="{y + 44}">{status}</text></a>')
    return "".join(parts) + "</svg>"


def hero_svg() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 400" role="img" '
        'aria-labelledby="hero-title hero-desc"><title id="hero-title">'
        "Команда внутри управляемого workflow</title>"
        '<desc id="hero-desc">Control plane ограничивает роли '
        "Analyst, PM, DE, Validator, QA и Reviewer. "
        "Декоративная архитектура, не execution trace.</desc>"
        '<path class="hud-line" d="M230 80V135 M80 160H380 M80 160V320H380V160 M230 160V320"/>'
        '<rect class="hud-panel" x="110" y="20" width="240" height="65"/>'
        '<text class="hud-title" x="230" y="60" text-anchor="middle">CONTROL PLANE</text>'
        + "".join(
            f'<rect class="hud-panel" x="{x}" y="{y}" width="120" height="60"/>'
            f'<text class="hud-label" x="{x + 60}" y="{y + 36}" text-anchor="middle">{name}</text>'
            for x, y, name in [
                (20, 140, "ANALYST"),
                (170, 140, "PM"),
                (320, 140, "DE"),
                (20, 290, "VALIDATOR"),
                (170, 290, "QA"),
                (320, 290, "REVIEWER"),
            ]
        )
        + "</svg>"
    )


def build_pages(
    root: Path,
    template,
    figure,
    outlines: dict[int, tuple[str, str]],
    published: set[int] | None = None,
) -> tuple[dict[str, bytes], str]:
    manifest, ordered = curriculum(root)
    published = published or set()
    nav = navigation(ordered, -1, published)
    availability = (
        f"Доступны полные лекции: {len(published)}; остальные темы пока представлены планами."
        if published
        else "Полные лекции ещё не опубликованы."
    )
    cards = "".join(
        f'<a class="topic-card" href="{url(item["id"])}"><span class="eyebrow">'
        f"{item['id']:02d} / {esc(item['track'])}</span><h3>{esc(item['title'])}</h3>"
        f'<span class="card-footer">{"Лекция" if item["id"] in published else "План темы"} '
        '<span aria-hidden="true">↗</span></span></a>'
        for item in ordered
    )
    body = (
        '<section class="hero"><div><p class="eyebrow">AGENTIC DATA PLATFORM / THEORY FIRST</p>'
        '<h1 class="hero-title">Инженерия<br><span>команд агентов</span></h1>'
        '<p class="hero-copy">Глубокая теория multi-agent систем для Data Engineering. '
        "От контракта одного вызова — к управляемому workflow, "
        "агенту-оркестратору и границам автономии.</p>"
        '<div class="hero-actions"><a class="cta" href="#program">Смотреть программу</a>'
        '<a class="cta secondary" href="#roadmap">Открыть маршрут</a></div>'
        '<p class="quiet">Курс готовится: доступны планы 27 тем. '
        f"{availability}</p></div>"
        '<div class="hero-hud"><p class="eyebrow">SYSTEM MAP / CONCEPTUAL</p>'
        + hero_svg()
        + '<p class="quiet">Архитектурная иллюстрация, не live trace.</p></div></section>'
        '<section class="stats"><div><strong>26</strong>core тем</div>'
        "<div><strong>01</strong>optional track</div>"
        "<div><strong>02</strong>модели orchestration</div>"
        "<div><strong>01</strong>сквозная система</div></section>"
        '<section id="about" class="landing-section"><p class="eyebrow">01 / FOUNDATION</p>'
        "<h2>Не коллекция промптов.<br>Система инженерных решений.</h2>"
        '<div class="feature-grid"><div class="panel"><h3>Для инженеров данных</h3>'
        "<p>Входная база: "
        "Python, SQL и понимание data pipelines. Kubernetes не требуется для core.</p></div>"
        '<div class="panel"><h3>Теория через подтверждённый пример</h3><p>Контракты, контекст, '
        "MCP, quality gates, recovery, безопасность и evaluation — "
        "на примере нашего мультиагента.</p></div>"
        '<div class="panel"><h3>Два подхода без универсального победителя</h3>'
        "<p>Code-owned workflow "
        "и model-directed orchestrator: применимость, ограничения, стоимость "
        "и гибридные границы.</p></div></div></section>"
        '<section id="roadmap" class="landing-section"><p class="eyebrow">02 / LEARNING PATH</p>'
        "<h2>Roadmap курса</h2><p>Сплошная линия — рекомендуемый порядок core; "
        "optional track отделён. "
        "Предпосылки показаны на страницах тем. ПЛАН — editorial status, не прогресс студента.</p>"
        + figure("course-roadmap", roadmap(ordered, published), "Маршрут курса: core и optional", 1)
        + '<details class="roadmap-list"><summary>Текстовый маршрут и ссылки на все темы</summary>'
        + nav
        + "</details></section>"
        '<section id="program" class="landing-section"><p class="eyebrow">03 / CURRICULUM</p>'
        "<h2>Программа: модули и темы</h2><p>Открывайте описание темы и план будущей лекции.</p>"
        '<div class="topic-grid">' + cards + "</div></section>"
        '<section class="terminal landing-section"><p class="eyebrow">04 / REFERENCE SYSTEM</p>'
        '<h2>Наш мультиагент — сквозной пример</h2><p class="terminal-line">'
        "&gt; Analyst → PM → DE → Validator → QA → Reviewer</p>"
        "<p>ClickHouse · dbt · Airflow / Cosmos · MCP · typed checkpoints · OpenTelemetry.</p>"
        "<p>Реализованный baseline — управляемый workflow. Agent-orchestrator и Kubernetes "
        "обсуждаются как теоретические альтернативы, не как готовый runtime.</p>"
        '<a href="prototype.html">Смотреть проверочные диаграммы →</a></section>'
        '<section class="landing-section faq"><p class="eyebrow">05 / FORMAT</p>'
        "<h2>О формате курса</h2>"
        "<details><summary>Есть ли лабораторные работы?</summary>"
        "<p>Нет. Цель — глубокая теоретическая база; "
        "наша система служит примером, не заданием для студента.</p></details>"
        f"<details><summary>Можно ли уже читать лекции?</summary><p>{availability} "
        "Публикация текста требует вычитки, technical verification, "
        "visual review и recheck.</p></details></section>"
    )
    files = {
        "index.html": template(
            "Инженерия команд агентов — курс", body, "index-diagrams.css"
        ).encode()
    }
    for item in ordered:
        article, toc = outline(item, ordered, outlines[item["id"]], full=item["id"] in published)
        core = manifest["teaching_order"] if item["track"] == "core" else manifest["optional_order"]
        position = core.index(item["id"])
        adjacent = []
        for offset, label in [(-1, "← Предыдущая тема"), (1, "Следующая тема →")]:
            if 0 <= position + offset < len(core):
                adjacent.append(f'<a href="{url(core[position + offset])}">{label}</a>')
        layout = (
            '<div class="reader-shell"><aside class="course-sidebar">'
            "<details><summary>Программа курса</summary>"
        )
        layout += (
            navigation(ordered, item["id"], published)
            + '</details></aside><article class="lecture">'
        )
        layout += '<details class="mobile-toc"><summary>В этой теме</summary>' + toc + "</details>"
        layout += (
            article
            + '<nav class="adjacent" aria-label="Последовательность тем">'
            + "".join(adjacent)
            + "</nav></article>"
        )
        layout += (
            '<aside class="lecture-sidebar"><p class="eyebrow">В ЭТОЙ ТЕМЕ</p>'
            + toc
            + "</aside></div>"
        )
        files[url(item["id"])] = template(
            item["title"], layout, f"topic-{item['id']:04d}-diagrams.css"
        ).encode()
    return files, roadmap(ordered, published)

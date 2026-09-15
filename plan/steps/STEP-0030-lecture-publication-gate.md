# STEP-0030 — Phase L: publication gate и reader полной лекции

Status: completed

Owner: Codex

Updated: 2026-09-15

## Scope и non-goals

Публиковать в локальном static reader только `reviewed` лекции с актуальными
content и publication receipts. Кандидат для проверки — отдельная labelled
build directory, никогда не основной `build/course`. Начать с лекции 00.
Менять `course/`, course policy tests и плановые records; не менять платформу,
runtime, секреты, модели или зависимости без необходимости.

## Решение и риски

ADR-0039: отдельный publication receipt связывает review inputs с исполняющим
builder, template, CSS/JS, конфигурацией и lockfile. Renderer PASS не означает
проверку всех лекций. AX semantics и реальное screen-reader interaction
фиксируются раздельно; не заявлять запуск assistive technology, которого не было.
Устаревший receipt или неуспешный render останавливает build до записи output.

## Checklist и acceptance

- [x] Реализовать строгий publication receipt и проверку freshness.
- [x] Добавить isolated candidate build и reviewed-only выбор текста/TOC/SVG.
- [x] Сохранить URL тем, roadmap, navigation, provenance index и CSP/no-JS.
- [x] Добавить regressions для обхода gate, stale inputs и непрошедшего render.
- [x] Проверить candidate 00: desktop/mobile/light/dark/no-JS, keyboard,
  print, AX semantics, final subpath/CSP/links и визуальную читаемость.
- [x] Обновить актуальный review и publication receipt только по actual checks.
- [x] Выполнить две одинаковые сборки, targeted pytest и `make check`.
- [x] Записать evidence, завершить шаг; затем отдельный STEP-0031 для лекции 01.

## Skills и verification

Editorial/claim-verification skills: review изменённых inputs и provenance.
`playwright`: реальные browser snapshots, keyboard/AX/print/viewport проверки.
`technical-markdown-lectures`: следующий authoring срез, не подмена gate.
Команды: course-check/build, candidate CLI, repeat build, course pytest, make check,
diff check, HTTP probes. Preview 8099 оставлять работающим; данные не удалять.

## Результат

`make check`: 529 PASS, exit 0. Final post-publication course suite: 78 PASS,
44.40s, exit 0. Две обычные сборки побайтово одинаковы; 00 reviewed и опубликована,
остальные страницы — outlines. AX semantics checked; actual AT остаётся explicit risk.
[Evidence](../evidence/STEP-0030-lecture-publication-gate.md).

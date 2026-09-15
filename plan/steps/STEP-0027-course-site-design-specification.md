# STEP-0027 — Фиксация дизайна сайта курса

Status: completed

Owner: Codex

Updated: 2026-09-15

## Goal, scope и non-goals

Зафиксировать пользовательский Cyberpunk / Glitch reference и структуру сайта:
landing → модули/лекции, SVG roadmap, меню курса слева, оглавление лекции справа.
Разрешены `course/design/**`, ссылки из course/README, Claude.md и planning/evidence docs.
Не реализовывать новый UI, не менять builder/assets/dependencies/curriculum/review gates.
Работающий preview STEP-0026 оставить работающим; Docker/LLM/secrets не затрагивать.

## Acceptance criteria

1. Reference сохранён в репозитории, есть canonical specification и принятое ADR.
2. Определены landing, reader layout, roadmap semantics, responsive navigation, tokens,
   typography, motion/readability constraints и статусы ещё не написанных лекций.
3. Сохранены Markdown → SVG → static HTML, строгий CSP, локальные assets, review gates.
4. Реализация явно отделена от фиксации; ссылки/governance проходят, evidence содержит команды.

## Checklist

- [x] Прочитать пользовательский reference, текущие CSS/templates и curriculum metadata.
- [x] Принять ADR и сохранить reference/specification.
- [x] Связать спецификацию с contributor docs, описать будущую реализацию и приёмку.
- [x] Выполнить plan/course governance и diff check, записать evidence, закрыть фиксацию.

## Risks и permissions

Reference предполагает Tailwind/React patterns, но текущий сайт — Python generator + CSS/JS:
визуальный язык переносится без смены framework. Glitch/scanlines могут мешать чтению;
адаптации к доступности указать явно. Не заявлять готовый UI или contrast/a11y PASS до проверки.
SVG roadmap не заменяет prerequisites graph и не меняет teaching_order.

## Verification

`make plan-check course-check`, `git diff --check`; вручную сверить дизайн с запросом.
Frontend/browser/full runtime проверки не нужны для документационного шага.

## Work log

- 2026-09-15: scope определён до записи спецификации; реализация не входит в запрос фиксации.
- 2026-09-15: reference/specification и ADR-0038 сохранены; `make plan-check course-check`
  и `git diff --check` — exit 0. [Evidence](../evidence/STEP-0027-course-site-design-specification.md).

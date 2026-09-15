# STEP-0027 — Фиксация дизайна сайта

Date: 2026-09-15

Status: completed

## Результат

Пользовательский reference сохранён в `course/design/cyberpunk-glitch-reference.txt`.
Canonical specification — `course/design/site-design.md`, решение — ADR-0038.
Определены landing, страницы модулей/лекций, SVG roadmap из manifest, левая программа,
правое оглавление, responsive/no-JS варианты, tokens/fonts/motion и критерии будущей реализации.

Приняты явные readability adaptations: только bounded hero glitch, без искажения lecture body,
контраст проверяется, а не наследуется из рекламного утверждения reference; кириллица/fonts
проверяются при реализации. React/Tailwind не вводятся в текущий Python/CSS/JS stack.
Ни одна лекция/план curricula не изменены; outlines не объявлены опубликованными.

## Verification

`make plan-check course-check`: exit 0, оба governance checks PASS.
`git diff --check`: exit 0.
Вручную сопоставлены четыре требования пользователя со specification:
главная landing, следующие module/lecture pages, SVG roadmap, две разные боковые навигации.
Документационный шаг не меняет HTML/CSS/JS/builder/dependencies, поэтому browser/full runtime
checks не запускались. Существующий preview STEP-0026 не перезапускался и не останавливался.

## Remaining work

Реализация нового UI — отдельный шаг; опубликованных текстов нет. Сначала tokens/layout/landing,
затем roadmap/navigation/reader с regression/browser/visual/no-JS/print проверками.

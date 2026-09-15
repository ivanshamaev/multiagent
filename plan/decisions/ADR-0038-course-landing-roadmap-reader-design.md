# ADR-0038 — Cyberpunk landing, SVG roadmap и двухсторонняя навигация

Status: accepted

Date: 2026-09-15

## Context

Пользователь задал Cyberpunk / Glitch reference и структуру учебного сайта после STEP-0026.
Текущий prototype не является landing или publisher лекций.

## Decision

Принять [спецификацию сайта](../../course/design/site-design.md): landing на главной,
SVG roadmap курса, отдельные module/lecture pages. На desktop reader слева содержит
модули/лекции курса, справа — оглавление текущей лекции. На landing справа нет фиктивного TOC.

Сохранить Python Markdown AST generator, static HTML, локальные CSS/JS/fonts и build-time SVG.
Не вводить React/Tailwind только из-за синтаксиса reference. Единые CSS tokens и reusable templates.
Manifest определяет teaching_order/status; группировка навигации не меняет curriculum.

Применить тёмную cyberpunk оболочку, неон и chamfered panels, terminal hero и SVG circuitry.
Эффекты не ухудшают lecture reading: bounded hero glitch, no text distortion in articles,
reduced-motion/no-JS fallbacks, проверяемый contrast и локальные кириллические fonts.
Исходный mutedForeground не считается автоматически пригодным для значимого мелкого текста.

## Consequences

Это принятие дизайна, не реализация интерфейса. Будущий implementation step должен доказать
landing/roadmap/reader UX через browser/visual/regression checks и сохранить publication gates.
Нельзя выдать outlines за опубликованные лекции или приписать hypothetical manager реализацию.

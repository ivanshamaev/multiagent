# STEP-0025 — технический контракт Markdown-лекций

Date: 2026-09-15

Status: PASS (requirements/documents only; STEP-0025 in progress)

## Выполнено

До оформления требований принят ADR-0036. Создан `course/technical-requirements.md`:
Markdown-профиль, структура лекций, Mermaid source, SVG build stage, доступность, UI-контракт
zoom/pan/fullscreen и publication gates. Включён собственный provider-neutral tool loop с
policy ALLOW/DENY; это форматный пример, не проверенный render или фактическая runtime diagram.
Все 27 todo-планов и их индекс ссылаются на требования; Claude.md закрепляет правила.

Изучены указанная страница DataTalks и её исходный HTML: hand-authored inline SVG, custom
zoom/reset/fullscreen handlers, нет Mermaid markers. Чужая графика/JS не копировались.
Открыты официальные Mermaid sequence/accessibility/config и CLI материалы; CLI поддерживает
Markdown transformation с SVG. Конкретный generator/версии будут выбраны при реализации.

## Проверки и границы

- `python3 - <<'PY' … PY` — read-only structural/link validation, exit 0:
  32 документа, 275 локальных ссылок, balanced fences; 27 plans inherit requirements;
  actual lecture texts absent. Это не Mermaid syntax/render validation.
- `make plan-check` — exit 0, PASS.
- `uv run pytest -q tests/policy/test_plan_governance.py` — exit 0, 3 passed in 0.31s.
- `git diff --check` — exit 0.

Mermaid CLI/HTML build, browser/a11y/print/CSP проверки не выполнялись: renderer отсутствует.
Установок dependencies, Docker/LLM calls, публикации сайта и runtime изменений не было.
Требования перечитаны отдельно: ссылки, scopes, source/render distinction и отсутствие labs.
Не объявлять это reviewed lecture receipt или независимым review.

Следующий проверяемый срез: подготовить editorial skills и минимальный scaffold/build prototype,
закрепить toolchain, проверить SVG и общую HTML-обёртку, затем писать и проверять каждую лекцию.

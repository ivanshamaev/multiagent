# ADR-0035 — Два control-flow подхода и границы лекций

Status: accepted

Date: 2026-09-15

## Context

Пользователь требует отдельные todo-планы каждой лекции, согласованность без повторения теории,
подбор популярных интернет-статей и сравнение workflow с agent-orchestrator.
Прежний STEP-0025 относил dynamic delegation к необязательной extension.

## Decision

Тексты лекций размещаются в `course/lectures/`, todo-планы — в `plan/steps/lections/`.
Создаём 27 stable lecture IDs: исходные 00–25 и дополнительную 26. Тема 16 становится core
agent-orchestrator; тема 24 остаётся theory extension. Это curriculum change, не runtime change.

15 описывает code-owned workflow; 16 — model-directed task planning/selection/replanning;
26 — сценарный выбор, trade-offs и bounded hybrid. Не смешиваем топологию graph с владельцем
routing policy; не приравниваем supervisor к A2A или approval authority. В обоих подходах
permission/side-effect/acceptance boundaries должны отдельно обеспечиваться системой.

Каждый concept имеет одну primary lecture. Index фиксирует teaching order, prerequisites,
out-of-scope topics и cross-links. Повторное применение допустимо; повторное полное объяснение
заменяется ссылкой. Per-lecture proofreading/claim verification ADR-0034 сохраняются.

Sources: известные первичные инженерные статьи/оригинальные научные работы; в плане указываются
URL, publisher, checked date, конкретная идея и граница её переноса. Популярность — редакторский
фильтр распространённости, не вымышленный численный рейтинг и не аргумент истинности.
Идеи пересказываются своими словами с attribution; полные тексты/переводы/диаграммы не копируются.

## Consequences

Agent-orchestrator остаётся теоретическим альтернативным проектом: наша система его не реализует.
Лекции не требуют labs, Docker/LLM calls, изменения policies или student exercises.
Planning review не выдаётся за semantic verification будущего текста.

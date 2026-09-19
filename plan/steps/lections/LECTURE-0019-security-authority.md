# TODO — Лекция 19. Security: untrusted content, identity и enforcement

Status: lecture written; text-only reviewed

Updated: 2026-09-19

Текст: `course/lectures/LECTURE-0019-security-authority.md`.

Track: core; исходная тема init: 19.

## Цель и уникальная область

Объяснить indirect prompt injection; authentication/authorization distinction; capability escalation control: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [08](LECTURE-0008-isolation.md), [09](LECTURE-0009-mcp-interface.md), [18](LECTURE-0018-airflow-operations.md), [07](LECTURE-0007-agent-orchestrator.md).

## Что писать — todo

- [x] Дать threat model для user/tool/file content и цепочки delegation.
- [x] Развести authentication, code-owned authorization, role assignment и approval authority.
- [x] Показать request-bound local HMAC bearer, no passthrough и deny-by-default MCP gateway.
- [x] Сравнить атаки на fixed workflow и planner-agent; model-driven manager не может сам повышать права.
- [x] Объяснить defense-in-depth без обещания полной защиты injection или equivalence local HMAC/OAuth.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [08](LECTURE-0008-isolation.md), [09](LECTURE-0009-mcp-interface.md), [07](LECTURE-0007-agent-orchestrator.md), [26](LECTURE-0026-deployment-theory.md), [24](LECTURE-0024-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/mcp_auth.py; tests/adversarial/; STEP-0022.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Mitigating prompt injection attacks with a layered defense strategy](https://blog.google/security/mitigating-prompt-injection-attacks/) (Google GenAI Security Team, S25). Идея для этого ракурса: Indirect injection и layered defense.
- [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing) (Anthropic, S10). Идея для этого ракурса: Containment ограничивает последствия untrusted execution.

- [x] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [x] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [x] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [x] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [x] Проверить текстовую семантику Mermaid source, подписи и текстового эквивалента; не делать скриншоты и визуальную вычитку SVG/HTML.
- [x] Сохранить text-only review и static-build fingerprints; не проставлять visual/AX/browser PASS и не повторять UI-код zoom/pan/fullscreen в лекции.

- [x] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [x] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [x] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [x] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [x] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [x] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.

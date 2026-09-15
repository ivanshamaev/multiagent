# 19 — Security: untrusted content, identity и enforcement

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0019-security-authority.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[5](../../modules/module-05-isolation/README.md), [6](../../modules/module-06-mcp-interface/README.md), [9](../../modules/module-09-airflow-operations/README.md), [16](../../modules/module-16-agent-orchestrator/README.md)

## Теоретические outcomes

- Объяснить indirect prompt injection, предпосылки и ограничения.
- Объяснить authentication/authorization distinction, предпосылки и ограничения.
- Объяснить capability escalation control, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `indirect prompt injection`, `authentication/authorization distinction`, `capability escalation control`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Дать threat model для user/tool/file content и цепочки delegation.
- Развести authentication, code-owned authorization, role assignment и approval authority.
- Показать request-bound local HMAC bearer, no passthrough и deny-by-default MCP gateway.
- Сравнить атаки на fixed workflow и planner-agent; model-driven manager не может сам повышать права.
- Объяснить defense-in-depth без обещания полной защиты injection или equivalence local HMAC/OAuth.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/mcp_auth.py; tests/adversarial/; STEP-0022

- [runtime/mcp_auth.py](../../../runtime/mcp_auth.py)
- [plan/evidence/STEP-0022-runner-and-mcp-isolation.md](../../../plan/evidence/STEP-0022-runner-and-mcp-isolation.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Mitigating prompt injection attacks with a layered defense strategy](https://blog.google/security/mitigating-prompt-injection-attacks/) — Indirect injection и layered defense.
- [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing) — Containment ограничивает последствия untrusted execution.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0019-security-authority.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.

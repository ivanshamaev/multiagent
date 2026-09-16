# 08 — Изоляция среды исполнения

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0008-isolation.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[02](../../modules/module-02-contracts/README.md)

## Теоретические outcomes

- Объяснить filesystem containment, предпосылки и ограничения.
- Объяснить network containment, предпосылки и ограничения.
- Объяснить process namespace boundary, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `filesystem containment`, `network containment`, `process namespace boundary`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести prompt-level restrictions и физические границы исполнения.
- Объяснить process/filesystem/network namespaces, scoped mounts и fail-closed behavior.
- Показать five Bubblewrap role identities, trusted model transport и нулевой raw egress.
- Разобрать ограничение shared kernel; authentication и Kubernetes вынести в отдельные лекции.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/runner_isolation.py; STEP-0022

- [runtime/runner_isolation.py](../../../runtime/runner_isolation.py)
- [plan/evidence/STEP-0022-runner-and-mcp-isolation.md](../../../plan/evidence/STEP-0022-runner-and-mcp-isolation.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing) — Filesystem/network containment как отдельные boundaries.
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — Разделение sandbox и harness.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0008-isolation.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.

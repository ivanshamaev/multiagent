# 24 — Deployment extension: Kubernetes и tenancy

Status: outline; lecture not written

Track: extension

[Todo-план](../../../plan/steps/lections/LECTURE-0024-deployment-theory.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[5](../../modules/module-05-isolation/README.md), [19](../../modules/module-19-security-authority/README.md)

## Теоретические outcomes

- Объяснить tenancy deployment model, предпосылки и ограничения.
- Объяснить namespace vs tenant isolation, предпосылки и ограничения.
- Объяснить deployment resource governance, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `tenancy deployment model`, `namespace vs tenant isolation`, `deployment resource governance`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Сравнить shared namespace/virtual control plane/cluster boundary как deployment alternatives.
- Объяснить ServiceAccount, resource bounds/cgroups, network policy и seccomp на уровне theory.
- Отделить orchestration policy от deployment substrate и shared kernel risks.
- Показать наши host Bubblewrap/Compose boundaries; Kubernetes явно не реализован.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `not-implemented`. Исходный ракурс: Extension only; ADR-0001/0031

Нет execution anchors для этого теоретического варианта.

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Kubernetes runtime не реализован.

## Статьи и переиспользуемые идеи

- [Three Tenancy Models For Kubernetes](https://kubernetes.io/blog/2021/04/15/three-tenancy-models-for-kubernetes/) — Сравнение tenancy models.
- [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing) — Filesystem/network isolation как необходимая часть containment.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0024-deployment-theory.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.

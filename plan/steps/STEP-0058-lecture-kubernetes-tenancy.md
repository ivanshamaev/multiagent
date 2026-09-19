# STEP-0058 — Phase L: опциональная лекция 26, Kubernetes и tenancy

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 26 о выборе deployment boundary для
multi-agent system: namespace-per-tenant в shared cluster, virtual control
plane per tenant и отдельный cluster boundary. Показать, как control-plane
и data-plane isolation связаны с моделью угроз, blast radius, стоимостью и
операционной сложностью.

Не повторять механику host sandbox из лекции 08 и модель authority из
лекции 19. Не создавать Kubernetes manifests, Helm chart или лабораторную
работу и не объявлять Kubernetes частью текущей реализации. Локальный
Bubblewrap/Compose baseline используется только как `offline-proven`
сравнительный пример; Kubernetes deployment остаётся `not-implemented`.

Затрагиваемые пути: `course/lectures/`, extension26/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/` и course/plan status records.

## Порядок и критерии приёмки

- [x] Сверить taxonomy с Kubernetes WG blog S22 и current Kubernetes docs:
  multi-tenancy, ServiceAccount, NetworkPolicy, ResourceQuota, cgroups и
  seccomp; Anthropic S10 использовать только для общего containment principle.
- [x] Зафиксировать tenant/threat assumptions и разделить namespace scope,
  workload identity/RBAC, admission, network, storage, resource governance,
  runtime/kernel и control-plane boundaries.
- [x] Сравнить namespace-per-tenant, virtual control plane и dedicated
  cluster/VM boundary по isolation, blast radius, sharing, cost и operations;
  исключить универсальный «лучший» вариант.
- [x] Добавить Mermaid-схему не более чем с 12 основными узлами, текстовый
  эквивалент, decision matrix, ограничения и контрпример ложной изоляции.
- [x] Сопоставить текущие runner identity/mount/network/resource/MCP границы с
  гипотетическим Kubernetes deployment без заявления эквивалентности.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors/hashes.
- [x] Проверить Markdown/links и candidate/static build; сохранить text-only
  publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; проверить repeatable build,
  `make check`, governance и `git diff --check`.

## Риски и ограничения

Namespace не является полной tenant boundary: cluster-scoped ресурсы,
control plane, nodes и kernel могут оставаться общими. ServiceAccount задаёт
workload identity, но не выдаёт полномочия без authorization. NetworkPolicy
ничего не обеспечивает без поддерживающего enforcement plugin и по умолчанию
не изолирует pod. ResourceQuota ограничивает aggregate namespace consumption,
а requests/limits и cgroups решают другую задачу; ни одно из них не
гарантирует confidentiality. Seccomp сужает syscalls, но не превращает общий
kernel в отдельный security domain. Более сильная граница уменьшает часть
рисков ценой overhead и не отменяет policy, secrets, storage и supply-chain
controls.

## Work log

2026-09-19: план создан до авторства; прочитаны обязательные authoring,
editorial и claim-verification skills, todo и technical requirements.
Проверены current Kubernetes primary docs, WG taxonomy S22, Anthropic S10,
ADR-0001/0031, launcher и STEP-0022 evidence. Существующий STEP-0056 CI/CD
не изменяется; до завершения этой работы governance временно видит два
`in progress` шага.
2026-09-19: лекция написана и дважды вычитана; исправлены границы shared
kernel и resource-limit claims. Content/publication receipts сохранены.
Candidate gate и две побайтно одинаковые production-сборки прошли без
screenshots/browser/visual checks. [Evidence](../evidence/STEP-0058-lecture-kubernetes-tenancy.md).
Final `make check` прошёл: Ruff/format, 532 tests, plan/course governance и
Compose validation; `git diff --check` также прошёл.

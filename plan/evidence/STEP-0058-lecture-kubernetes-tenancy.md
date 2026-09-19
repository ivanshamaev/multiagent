# Evidence — STEP-0058: опциональная лекция 26, Kubernetes и tenancy

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services, Kubernetes cluster и
paid LLM не запускались и не менялись. Не делались screenshots, browser
navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0026-deployment-theory.md`; SHA-256
  `d548210491de6dbf04aa9d11778fa0212e1ec2e512b5a8e574c34803048207d9`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленных minor findings сохранены в
  `course/reviews/LECTURE-0026.json`. Content digest:
  `c0bd8a00eff84cbabde842e7787fe1c6fb6cb55c2e8a8a39ecb5208e45426937`.
- Kubernetes WG S22 и current official multi-tenancy, ServiceAccount,
  NetworkPolicy, ResourceQuota, resource-management, seccomp/kernel docs
  проверены онлайн 2026-09-19. Anthropic S10 использован только как общий
  containment principle.
- ADR-0001/0031, current Bubblewrap launcher и STEP-0022 проверены локально.
  Локальный baseline не выдан за Kubernetes evidence; Kubernetes отмечен
  `not-implemented`.

## Публикация и проверки

- `make course-review COURSE_LECTURE=26` — exit 0 после штатного временного
  статуса `technically-verified`: 132 файла, 31 Mermaid diagram, candidate
  site SHA `94a822c921cbb050f79d937d96341c635ced7eb47044c6b7d6285f451d894800`.
- Text-only publication digest:
  `0c2d2b79536389510a5f1a4ddc3b833ade6e4bae94cbab74b911eb9a2df521fa`;
  canonical rendered `body + TOC` SHA:
  `34088fc25877dcabfdd29afa02fb8f72eda47a4515f955a388a0f40470011499`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step58-repeat` — exit 0: site SHA обоих
  `87bf3367dcec915145a0f05c29d068b17f2f46d277b1f7ee8ae06a5e65019b36`;
  `diff -qr build/course build/course-step58-repeat` — exit 0.
- `make check` — exit 0: Ruff/format PASS, 532 pytest tests, plan/course
  governance and Docker Compose config PASS.
- `git diff --check` — exit 0 after final evidence update.

## Пределы доказательства

Review same-author, не независимый. Static build подтверждает парсинг,
ссылки, pinned Mermaid rendering и repeatability, но не визуальную
читаемость, mobile/print/AX или assistive technology. Не разворачивались и
не проверялись Kubernetes, RBAC, admission, CNI/NetworkPolicy,
ResourceQuota/cgroups или seccomp. Матрица deployment models —
evidence-bounded теория выбора, не production recommendation или security
certification. Shared cloud/IAM/storage/supply-chain risks остаются вне
гарантии topology.

# Evidence — STEP-0032: лекция 03, контракты и границы доверия

Date: 2026-09-16

## Результат и редакторские gates

Написана theory-only лекция 03: artifact/contract, четыре уровня корректности,
closed schema, invariants, cross-task/actor binding, versioning, immutability,
evidence и классы отказа. Она не повторяет PM semantics, DE lifecycle,
workflow graph, identity, persistence или evaluation theory. Лабораторных нет.

Применены technical-markdown-lectures, technical-editorial-review и
technical-claim-verification; версии и 16 claims записаны в content receipt.
Проверены S08/S20, Pydantic primary docs, current contracts/reducer/tests,
ADR-0014 и dated STEP-0006. После отдельной полной вычитки уточнена trusted
provenance TransitionCommand и русифицированы два labels; весь текст перечитан.
Same-author passes не являются independent review.

## Verification

Targeted contracts/workflow/adversarial tests: 36 PASS. Candidate build:
`uv run python -m course.build --candidate 3 --output build/course-review-0003`
— exit 0, 84 files, 7 diagrams. Playwright на `/course/topic-0003.html`:
HTTP 200; desktop 1440×1000, mobile 360×800, light/dark preferences, no-JS,
TOC, keyboard zoom/pan/Home/fullscreen/Escape/focus, print geometry,
CSP/subpath/local links — PASS. Zero external requests, JS/CSP errors.
AX main и named/described SVG найдены (1418 nodes). Семь screenshots просмотрены;
кириллица, ветви, подпись и print diagram читаемы, body overflow отсутствует.
Hashes сохранены в PUBLICATION-0003.json.

`make check`: exit 0, Ruff/format PASS, 529 tests PASS in 81.04s,
plan/course governance и Compose config PASS. Post-publication course policy suite:
78 PASS in 47.35s. `make course-build` и повторная labelled build — exit 0,
84 files/7 diagrams, site SHA256
`5f4eb873dcfd596a589958d230c8f66b2f903f5cf9b99084f28fde39667a4eff`;
`diff -qr` — exit 0. `git diff --check` и final `make plan-check course-check`
— exit 0. Published landing/03 return HTTP 200; browser shows full lecture.

## Остаточные риски

Actual Orca/NVDA/VoiceOver, hardware touch, printed PDF и cross-browser не проверены.
Свежие Data Platform/model calls не выполнялись; STEP-0006 остаётся historical.
Schema/checksum не выданы за authentication, provenance или semantic truth.
Временный 8098 остановлен; основной preview 8099 оставлен доступным.

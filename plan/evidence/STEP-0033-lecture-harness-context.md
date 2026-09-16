# Evidence — STEP-0033: лекция 04, harness и контекст вызова

Date: 2026-09-16

## Результат и редакторские gates

Написана theory-only лекция 04: harness, контекст конкретного вызова, отбор,
представление и сжатие, provider abstraction, structured response и контрпример
семантически неверного результата при корректном формате. Контекст одного хода
не смешан с lifecycle памяти 17, recovery 18 или экономикой 23. Лабораторных нет.

Применены `technical-markdown-lectures`, `technical-editorial-review` и
`technical-claim-verification`; SHA256 инструкций и восемь проверенных claims
в [content receipt](../../course/reviews/LECTURE-0004.json). Проверены две
первичные статьи Anthropic S07/S30, current context/provider/PM code, tests и
датированное STEP-0007. Отдельная вычитка выявила две minor неточности:
стабильность metadata при чтении файла и смысл prompt-маркеров. Исправлены;
финальный текст перечитан целиком. Same-author passes не являются независимым review.

## Verification

Targeted context/model-provider/runtime tests: 40 PASS. Candidate build:
`uv run python -m course.build --candidate 4 --output build/course-review-0004`
— exit 0, 86 files, 8 diagrams. Playwright на `/course/topic-0004.html`:
HTTP 200; desktop 1440×1000, mobile 360×800, light/dark preferences, no-JS,
TOC, keyboard zoom/pan/Home/fullscreen/Escape/focus, print geometry,
CSP/subpath/local links — PASS. Нет внешних запросов и JS/CSP errors.
AX main и named/described SVG найдены (1141 nodes). Семь screenshots просмотрены:
кириллица, ветвление, подпись и print diagram читаемы; body overflow отсутствует.
Hashes сохранены в [publication receipt](../../course/reviews/PUBLICATION-0004.json).

`make check`: exit 0; Ruff/format PASS, 529 tests PASS in 82.70s, plan/course
governance и Compose config PASS. Course policy suite: 78 PASS in 51.45s.
`make course-build` и повторная labelled build — exit 0, 86 files/8 diagrams,
site SHA256 `a58ca3f7692b9ea52bd37ac3cce2da03be6cb2b82e227b958a5f5eb038df1250`;
`diff -qr` — exit 0. Финальные `make plan-check course-check` и
`git diff --check` — exit 0. Основной preview 8099 возвращает HTTP 200
для лекции 04.

## Остаточные риски

Actual Orca/NVDA/VoiceOver, hardware touch, printed PDF и cross-browser
не проверены. Свежие Data Platform/model calls не выполнялись; STEP-0007
остаётся historical. Byte-лимиты не выданы за token accounting или semantic
retrieval; проверка JSON не выдана за business acceptance. Временный preview
8098 остановлен, основной 8099 оставлен доступным.

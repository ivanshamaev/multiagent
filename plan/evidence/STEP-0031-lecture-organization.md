# Evidence — STEP-0031: лекция 01, организация команды

Date: 2026-09-15

## Scope и выполненная работа

Написана theory-only лекция 01: определения ответственности/capability/ownership,
неисчерпывающая модель task coupling, неявные решения, цена координации,
separation of duties, шесть последовательных вкладов, profiles и гипотетический
Net Revenue контрпример. Нет labs, student setup или изменений runtime/платформы.
Тема не повторяет agent loop 00, algorithms 10/11/13/14 или comparison 26.

## Авторство и редакторские проверки

Прочитаны и применены technical-markdown-lectures, technical-editorial-review,
technical-claim-verification; версии сохранены в content receipt.
После авторства весь текст отдельно вычитан; проверены glossary/owners/prerequisites.
Исправлены претензия на исчерпывающую классификацию и лишние английские формулировки;
весь финальный текст перечитан. Это отдельные same-author passes, не independent review.

Primary sources: Data Mesh Principles (только аналогия), Cognition original
и follow-up (не универсальный запрет и не перенос performance). Проверены четыре
current profiles, ADR-0003/0006 и historical STEP-0008; области доказательства разделены.
В 00 уточнён только forward-link status claim; затронутый текст перечитан и reader перепроверен.

## Реальный reader gate

`uv run python -m course.build --candidate 0 --candidate 1 --output build/course-review-0001`
— exit 0, 82 files, 6 diagrams. Только labelled output, пользовательский preview не остановлен.
Playwright: /course/topic-0001.html и topic-0000.html, HTTP 200; desktop 1440×1000,
mobile 360×800, light/dark browser preferences, no-JS navigation, TOC, keyboard
zoom/pan/Home/fullscreen/Escape/focus return, print geometry, CSP/subpath/local links — PASS.
Zero external page requests, JS errors и CSP violations. AX main landmark и SVG
name/description присутствуют: 1117 nodes у 01, 1106 у 00.
По семь screenshots каждой лекции просмотрены фактически; стрелки/кириллица/подписи проверены.
Широкая схема 01 прокручивается внутри canvas, без body overflow; доступен zoom/fullscreen.

Screenshots и build artifacts ignored; SHA256 сохранены в PUBLICATION-0000/0001.json.
`LECTURE-0001.json` binds content + TODO + requirements/skills/toolchain;
publication receipt отдельно binds code/static/locks + actual renderer + rendered body/TOC.
После изменения только TODO повторный candidate render выполнен до sealing receipts.

## Verification и оставшиеся риски

`make check`: exit 0, 529 tests PASS in 78.50s; Ruff/check/format, plan/course
governance и `docker compose config --quiet` PASS.
`uv run pytest tests/policy/test_course_build.py tests/policy/test_course_governance.py -q`
— exit 0, 78 PASS in 48.36s на опубликованном manifest. Fixtures изолируют synthetic
лекцию 00 от остальных опубликованных текстов, не ослабляя gate assertions.
`make course-build` и повторная labelled build — exit 0,
82 files, 6 diagrams; `diff -qr build/course build/course-final-repeat` — exit 0.
Final TODO status не меняет body/TOC: receipts rebound без изменения текста/renderer;
обе обычные сборки повторены. Browser опубликованного 01: HTTP 200, 14 sections,
три ссылки с landing на 01. Финальный site SHA256:
`6130d25b4e21d7d17c202ebcb8e33a90c6dda7920cf1dc83992b1fcab3f1fe92`.
`git diff --check` и final `make plan-check course-check` — exit 0.
Preview 8099 оставлен работающим (landing/01 HTTP 200); только временный 8098 остановлен.
Actual Orca/NVDA/VoiceOver interaction, printed paper/PDF, hardware touch и cross-browser
не проверялись; AX PASS не заменяет AT interoperability audit.
Платные LLM и Docker startup/reset не выполнялись. Следующая лекция — 03 по teaching order.

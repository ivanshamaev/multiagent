# Evidence — STEP-0034: последовательная нумерация курса

Date: 2026-09-16

## Результат и границы

Сохранён прежний порядок тем, но core ID приведены к позициям 00–25;
optional Kubernetes extension — 26. Соответствие old → new зафиксировано
в [плане шага](../steps/STEP-0034-course-sequential-numbering.md). Обновлены
manifest, planning map, 27 индивидуальных TODO, 27 module/extension outlines,
четыре текста, syllabus, glossary, source-index и активная навигация.
Исторические STEP/ADR/evidence не переименованы. Старые локальные `topic-NNNN.html`
меняют смысл; обещания backward compatibility для preview не было.

После механической правки четыре текста полностью перечитаны в отдельном
редакторском проходе. Содержательные технические утверждения и диаграммы не
менялись; скорректированы номера, ссылки и два оставшихся текстовых упоминания.
Content receipts привязаны к новому Markdown и input digest, publication receipts
перепривязаны после нового candidate render/browser gate. Same-author review
не назван независимой рецензией.

## Verification

- `uv run python -m course.check`: exit 0, 27 IDs и все local Markdown links PASS.
- Четыре `--candidate ID` сборки: exit 0, по 80 файлов/5 диаграмм; новые
  `rendered_sha256` записаны в per-lecture publication receipts.
- Playwright на `/course/topic-0000..0003.html`: для каждой страницы HTTP 200,
  desktop/mobile 360 px, light/dark, no-JS, keyboard zoom/pan/Home/fullscreen/
  Escape/focus, print geometry, AX main и named/described SVG, CSP/subpath,
  локальные ссылки — PASS. Все 28 скриншотов просмотрены вручную; AX nodes:
  1106/1117/1418/1141 соответственно. Actual AT не запускалось.
- Основной preview `/course/`: HTTP 200. Roadmap links начинаются с
  `topic-0000.html` → `0001` → `0002` → `0003`; четыре full readers имеют
  12/14/15/14 разделов `h2` и соответствующие темы.
- `make check`: exit 0; Ruff/format, 531 pytest, plan/course governance и
  Compose config PASS. Course policy suite: 80 PASS in 50.75s.
- Две обычные сборки: exit 0, 86 файлов/8 диаграмм, одинаковый site SHA256
  `6cbb6b6c1bb8874db4971cca362e1037a209bb56aa7f04cb0f240c0a446206df`;
  `diff -qr`: exit 0.
- Финальные `make plan-check course-check`, `git diff --check` и HTTP 200
  основного preview — exit 0.

Перед первой обычной сборкой старый generated `build/course` был перемещён в
`build/course-pre-step34`: builder верно отказался смешивать старые и новые URL.
Исходники/volumes не удалялись. Временные candidate preview 8095–8098 остановлены;
основной preview 8099 оставлен доступным.

## Ограничения

Новая нумерация меняет локальные URL старых тем; внешние сохранённые ссылки
нуждаются в ручном обновлении. Исторические записи предыдущих шагов используют
старые IDs и интерпретируются по таблице миграции. Нет новой проверки модели,
Data Platform, actual Orca/NVDA/VoiceOver, hardware touch, PDF или cross-browser.

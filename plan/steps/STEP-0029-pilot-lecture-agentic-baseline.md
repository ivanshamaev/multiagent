# STEP-0029 — Phase L: пилотная теоретическая лекция 00

Status: completed

Owner: Codex

Updated: 2026-09-15

## Цель и границы

Написать первую полную лекцию в `course/lectures/`: agency, reasoning,
действие, наблюдение и ограниченный agent loop. Основа — утверждённый
[индивидуальный план](lections/LECTURE-0000-agentic-baseline.md).
Не повторять темы владельцев 01, 15 и 16; не добавлять лабораторные работы.
Реализацию платформы, модели и права исполнения не менять.

## Обязательные skills и последовательность

1. `technical-markdown-lectures`: написать глубокое объяснение по плану.
2. `technical-editorial-review`: отдельная полная вычитка текста и подписей.
3. `technical-claim-verification`: сверить существенные claims с первичными
   источниками и локальным кодом; затем повторно прочитать исправленную версию.

Проверки выполняет автор; это не независимое рецензирование.
При browser-проверке применять `playwright` и сохранять фактические артефакты.

## Todo и критерии приёмки

- [x] Перечитать primary sources ReAct и Building effective agents.
- [x] Написать лекцию: определения, причинная модель, ограничения,
  контрпример, пример нашей системы, резюме и 3–5 вопросов.
- [x] Добавить Mermaid с доступными заголовком, описанием и текстовым эквивалентом.
- [x] Провести отдельную редакторскую и техническую проверки, исправления и recheck.
- [x] Проверить render pinned CLI и сохранить evidence; визуальные проверки
  не приписывать, если они не выполнены.
- [x] Обновить todo-план, manifest и receipt, связанный с финальным input digest.
- [x] Выполнить `make course-check` и релевантные regression checks.
- [x] Записать команды, exit codes, evidence и оставшиеся ограничения.

## Риски и политика публикации

Наблюдение не равно истине, reasoning не равно исполнению, один успешный
исторический запрос не является оценкой качества. Не изображать private
chain-of-thought. Заимствованные идеи пересказывать ограниченно и с attribution.

Статус `technically-verified` допустим только после фактических проверок и
актуального receipt. `reviewed` и публикация в reader не входят в этот срез:
общий publication gate и renderer имеют пока prototype-статус. Работающий
preview `127.0.0.1:8099/course/` не останавливать.

## Work log

- Написана лекция; выполнены отдельные полный editorial pass, technical pass
  и полный recheck исправленного текста. Добавлены явные определения loop/runtime,
  уточнён нормативный характер правила повторов, убран лишний жаргон.
- Исправлены две устаревшие формулировки technical requirements о renderer.
- При первом authored entry выявлена hardcoded подпись reader; расширен scope
  на исправление статуса без публикации, добавлен regression (PRB-0058).
- Diagram preview использует существующие `render_cli`/`normalize_svg`;
  полная схема проверена дополнительно в print layout. Screen-reader и final
  lecture URL gate остаются открытыми.
- Final `make check`: exit 0, 519 PASS. `make course-build`: exit 0;
  preview восстановлен и HTTP 200 проверен. [Evidence](../evidence/STEP-0029-pilot-lecture-agentic-baseline.md).

# STEP-0029 — Evidence пилотной лекции 00

Date: 2026-09-15

## Реализовано и review scope

Написана `course/lectures/LECTURE-0000-agentic-baseline.md`: agency, граница
reasoning/action/observation, частичная видимость среды, остановка одного
цикла, гипотетический Net Revenue контрпример и tool-free PM illustration.
Нет labs/student setup. Соседние primary owners связаны ссылками на outlines.

Три обязательных skills прочитаны и применены автором: авторство → отдельная
полная вычитка → primary-source/code verification → полный recheck исправленного
текста. Это не независимое рецензирование. Исправлены неявные определения,
универсально звучавшее правило повторов и лишний жаргон. Существенных unresolved
content findings нет. Inventory из 12 claims и версии skills — в receipt.

ReAct v3 §2 прочитан через primary PDF; Anthropic — релевантные определения.
Проверены `SpecificationExecutor.specify` и `accept_specification_draft`,
существующие PM regressions, historical evidence STEP-0007 от 2026-09-06.
Статьи пересказаны ограниченно, своими словами; собственный синтез обозначен.
Новых LLM/GateLLM/Data Platform/Docker вызовов не было.

## Проверенные inputs и диаграмма

- Content SHA-256: `a1683e0b9907d881034b9cfed791454d674b4efc795c7cd11329dd8a11b47309`.
- Review input digest: `1f49132acca5e8b0c94a1dfdea9b3916f8010195e77cbb927641dbf105ddf7fd`.
- Mermaid source: `38625b678183bc0e070facbf03e4c1c46ee278d7f5416c19cdf021afa4256f44`.
- Normalized SVG: `7c2e041be379574bc5b2e5244ac9f8dd0e18145a4ae8f889381d90039653124d`.
- Diagram config: `bc12b7e5869cf9fea920a4ed5b52619096949dc7c1c3de2cef760e0d105cdd8d`.
- Node 22.22.0 / CLI 11.17.0 / Mermaid 11.16.1 / Chrome 153.0.8010.36.
  Lockfile, builder и font hashes сохранены в `course/reviews/LECTURE-0000.json`.

Existing `render_cli` + `normalize_svg`: exit 0. Disposable authoring generator
`uv run python -m output.playwright.step29.render_preview`: exit 0; generated
`build/course-lecture00-preview/diagram-index.json`. Эти artifacts ignored,
receipt и этот summary persistent. Playwright snapshots и screenshots:
`output/playwright/step29/{desktop,mobile,mobile-dark,no-js,full-diagram}.png`.
Визуально проверены кириллица и полный graph в print layout; viewport canvas
показывает часть большой схемы и допускает native scroll. Body overflow checks
desktop/mobile не обнаружили общего горизонтального overflow.

## Команды и результаты

- `make course-check`: final authored receipt PASS, exit 0.
  Первый промежуточный запуск отклонил несинхронизированный outline status;
  после появления текста manifest переведён в draft, затем technically-verified.
- Targeted pytest PM/adversarial/course governance/build: 71 PASS, exit 0,
  до добавления четырёх parametrized reader-status regressions.
- `make course-build`: exit 0, 78 files / 4 prototype diagrams;
  site SHA-256 `64a0cc302eee629045de90b8995cb6ce54479f41558f4429b339093f02efc4cf`.
  Полный текст лекции не включён в public output. PRB-0058 исправляет подпись
  reader для authored entries, не ослабляя publication boundary.
- Первый `make check`: exit 2, 518 PASS / 1 planning-ledger FAIL.
  Причина — написано `in-progress` вместо принятого `in progress` и не внесён
  PRB-0058 в index; исправлены records, не checker/assertions.
- Final `make check`: exit 0; 519 tests PASS за 67.77s, Ruff/format,
  plan governance, course governance и Compose validation PASS.
- `make plan-check course-check` и `git diff --check`: exit 0.
- Playwright final reader check: exit 0; `topic-0000.html` показывает
  «текст подготовлен, но не опубликован», заголовки полного draft не опубликованы.
  HTTP probes landing и topic: 200; основной preview PID 550494, loopback 8099.
- Browser CLI первый запуск на system Node 18 отказался стартовать; повтор
  с repository-pinned Node 22 успешен. Исправлена сигнатура одноразового
  `run-code`; успешный повтор сохранил реальные screenshots.

## Оставшиеся ограничения и handoff

Manifest: `technically-verified`, не `reviewed`. Global renderer остаётся
`prototype-verified`; publication status не менялся. Проверка diagram preview
не покрывает полный текст в финальном reader, screen-reader interaction и
полный keyboard/print/accessibility gate. Эти проверки — следующий срез перед
публикацией пилотной лекции; после него лекция 01.

Preview 8099 перестал отвечать при финальной проверке; восстановлен отдельным
`make course-preview`. Причина исчезновения старого процесса не установлена.
Временный diagram-only сервер 8098 закрывается после проверки; основной
preview 8099 оставляется работающим. Volumes и пользовательские данные не удалялись.

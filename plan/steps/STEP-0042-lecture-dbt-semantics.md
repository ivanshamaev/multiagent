# STEP-0042 — Phase L: лекция 11, dbt и семантика аналитической модели

Status: complete

Owner: Codex

Updated: 2026-09-17

## Цель и границы

После лекции 10 написать и опубликовать theory-only лекцию 11 о grain,
зависимостях dbt-моделей, lineage и уровнях доказательства parse/compile/build/test.
На примере `platform/dbt/` различить граф преобразований, Airflow DAG с Cosmos
и граф работы агентов. Не повторять предмет лекций 12, 14, 15 и 18, не вводить
лабораторных работ, не менять runtime и Docker, не вызывать платные LLM.

## Порядок и критерии приёмки

- [x] Сверить S17/S18 и первичную документацию dbt/Cosmos с SQL, YAML,
  Airflow DAG и датированным STEP-0004.
- [x] Написать теорию с явными инвариантами grain и контрпримером неверной
  метрики, схемой с текстовым эквивалентом, границами тестов и вопросами.
- [x] Провести отдельные редакторскую вычитку и фактчекинг, исправить findings,
  повторно проверить и сохранить content receipt.
- [x] Собрать candidate и проверить HTML/SVG в реальном браузере: desktop,
  mobile, light/dark, no-JS, keyboard, print, AX, CSP, subpath и links.
- [x] Сохранить publication receipt, обновить syllabus/index, выполнить
  course gates, повторяемую сборку и `make check`; проверить preview 8099.

## Риски

`ref()` показывает объявленную зависимость, но не доказывает правильную
бизнес-семантику. `unique`/`not_null` проверяют строки выбранного состояния,
а не полноту источника или правильный denominator. Успех исторического
STEP-0004 не является текущим live доказательством. Browser AX не заменяет
проверку реальным screen reader.

## Work log

2026-09-17: план создан после чтения todo 11, до авторства лекции.
2026-09-17: content и browser/visual gates завершены, семь screenshots
осмотрены; две сборки идентичны, `make check` — 531 PASS. Evidence:
`plan/evidence/STEP-0042-lecture-dbt-semantics.md`.

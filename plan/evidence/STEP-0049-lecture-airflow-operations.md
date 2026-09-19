# Evidence — STEP-0049: лекция 18, Airflow API

Captured: 2026-09-18 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services and paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0018-airflow-operations.md`; SHA-256
  `2f63111debfb1fcedfd9c2da7126fef603f25e37767312be560cdf20c99245eb`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings — в
  `course/reviews/LECTURE-0018.json`. Content digest:
  `5ceec86d12177a74cd3d2bb0022ca2970ab9fca6553aa551c0b6015b30100e9d`.
- Official Airflow 3 release/Task SDK docs и AWS Builders' Library сверены с
  observer/trigger/approval adapters, профилями и датированными
  STEP-0014/0015. Public REST `/api/v2` не смешан с Task Execution API;
  Observer GET к ресурсам отделён от `POST /auth/token`.
- Mermaid source, подпись и текстовый эквивалент проверены по логике adapter.
  Указано окно сбоя между удалённым POST и локальным погашением approval;
  fully-live six-role trigger или production authorization не заявлены.

## Публикация и проверки

- `uv run python -m course.check` — exit 0 до и после публикации.
- `uv run python -m course.build --candidate 18 --output
  build/course-step49-text-review-0018` — первый запуск exit 1: Mermaid CLI
  получил SIGSEGV при рендеринге уже существующей диаграммы темы 05.
  Повтор без изменения исходников — exit 0: 116 файлов, 23 диаграммы.
  Это непостоянный сбой renderer, не сбой синтаксиса лекции 18; причину
  SIGSEGV отдельно не установили. Publication digest:
  `b7fdf99904c564b8ed5e2ee0081f7708d04f08a679ca7ecc5f6d731c94c305f2`;
  rendered SHA лекции:
  `f3f03063da7b22193e76e28a8ee5b9faa613fbbde7bacaf97f02fadaa6f909b2`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step49-repeat` — exit 0: site SHA обоих
  `b24be0231fbc78b8609374229b858ec4f4507664e651912391f042e61fa21c01`;
  `diff -qr build/course build/course-step49-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services, live Airflow и Gateway не
  запускались.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability двух успешных запусков, но не
визуальную читаемость, mobile/print/AX или работу assistive technology.
STEP-0014/0015 — исторические локальные live smoke для Airflow 3.3.1,
не свежий запуск в этом шаге. Локальный approval store не является общей
системой согласований; отсутствие распределённой транзакции оставляет
сеть/краш-окна, которые требуют сверки результата по run ID.

# Evidence — STEP-0050: лекция 19, Security и полномочия

Captured: 2026-09-18 UTC (2026-09-19 local). Scope: theory-only course text
and text-only publication. Runtime, Data Platform, Docker services and paid
LLM не менялись. Не делались screenshots, browser navigation или визуальная
вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0019-security-authority.md`; SHA-256
  `9d1cefa54376b3ce029a705627d9a830d464a57e6d074bc6c627828932dfb569`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings — в
  `course/reviews/LECTURE-0019.json`. Content digest:
  `03908d10aee379799c8c2ee5883ff85f38ff37ea5cf017b249b112517d89a4e2`.
- Google GenAI Security Team S25, Anthropic S10 и официальная MCP
  authorization specification 2026-07-28 сверены 2026-09-18. Current
  `runtime/mcp_auth.py`, `maf_facade.py`, gateway/policy, approval CLI,
  unit/integration/adversarial tests и датированный STEP-0022 отделены
  от теоретического planner-agent. Mermaid source, подпись и текстовый
  эквивалент сопоставлены с кодом.
- Уточнения после проверки: bearer не аттестует человека/процесс;
  `approved_by` в локальном CLI передаёт доверенный вызывающий процесс;
  модельные защитные слои не дают строгой гарантии. Local HS256 не назван
  OAuth, а test PASS — измерением устойчивости модели к injection.

## Публикация и проверки

- `uv run python -m course.check` — exit 0 до и после публикации.
- `uv run python -m course.build --candidate 19 --output
  build/course-step50-text-review-0019` — exit 0: 118 файлов, 24 диаграммы.
  Publication digest:
  `d4466ae74634f67ca64458326e4eec4697940fe38817d1187815ec40cdfc6e7c`;
  rendered SHA лекции:
  `62fd1a15ee7bbeec8791d00a63880815b11610032d962037301739f31a5333f4`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step50-repeat` — exit 0: site SHA обоих
  `a2fa6496fe2bab2d15876d88f1af1bc95eaad7e2005fb364bfe7ef10217adff9`;
  `diff -qr build/course build/course-step50-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services, live MCP/Airflow и Gateway
  не запускались.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, но не визуальную читаемость,
mobile/print/AX или работу assistive technology. Unit/adversarial checks
проверяют policy/auth boundaries, а не вероятность успешной prompt
injection против модели. STEP-0022 — исторический локальный isolation
smoke, не гарантия remote HTTP MCP или production approval authority.
Planner-agent не реализован, fully-live six-role READY не заявлен.

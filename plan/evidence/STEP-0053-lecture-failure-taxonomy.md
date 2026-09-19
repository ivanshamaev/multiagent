# Evidence — STEP-0053: лекция 22, Failure modes

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services и paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0022-failure-taxonomy.md`; SHA-256
  `0826635cb9595835058ee34f068aa1d9e1a4c4a42fce32f3341b435c224b7ca9`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings — в
  `course/reviews/LECTURE-0022.json`. Content digest:
  `e766ba9b4805dfe3a4ada4cad51b154d11f38dcd1002cf6106a853e3b1537d93`.
- AWS S13 и Anthropic S21 проверены онлайн 2026-09-19. Claims сверены с
  текущими role-pipeline/checkpoint code/tests и датированными
  PRB-0035/0051/0052, STEP-0010/0024. Manager replan отделён как
  not-implemented theoretical comparison.
- Taxonomy явно не взаимоисключающая; `DENY` не назван дефектом сам по себе.
  Correlated fixture/oracle outcomes не выданы за независимые evidence,
  jitter — за semantic/policy repair, а process regression — за power-loss
  durability. Mermaid source, подпись и текстовый эквивалент сверены.

## Публикация и проверки

- `uv run python -m course.check` — exit 0 до и после публикации.
- `make course-review COURSE_LECTURE=22` — exit 0: 124 файла,
  27 диаграмм. Publication digest:
  `4b97c84eb946fe5d4c426709a4e48d939f7bdbc46837ed9e358bbea9f8e0d916`;
  rendered SHA лекции:
  `20431ace69f5290c86b0b03991a9960cc2a3d9d95c2e1cded3c289fbb8ad045b`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step53-repeat` — exit 0: site SHA обоих
  `ae97402522d770ded2eb71b39cb2f58ce50c5d6695de60d7e618acc3d8ed52b8`;
  `diff -qr build/course build/course-step53-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services и Gateway не запускались.
- `git diff --check` — exit 0.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, но не визуальную читаемость,
mobile/print/AX или работу assistive technology. PRB records — датированные
defects; их fixes не устраняют весь класс common-mode/race failures. AWS и
Anthropic numbers принадлежат их simulations/benchmarks и не перенесены на
локальную систему. Не выполнены fresh fault injection, power-loss tests,
dynamic-manager benchmark или fully-live six-role validation.

# Каталог проблем

Для системной или нетривиальной проблемы создаётся `PRB-NNNN-short-name.md` со статусом, symptom, reproduction, evidence, root cause, attempted fixes, accepted fix, regression check и follow-up. Секреты и полный model output не записываются.

Последние записи: [PRB-0010](PRB-0010-custom-dbt-runner.md) заменяет custom dbt runner на Cosmos;
[PRB-0011](PRB-0011-cosmos-runtime-dependencies.md) фиксирует hash-locked runtime dependencies
Cosmos; [PRB-0012](PRB-0012-grader-workspace-permissions.md) исправляет read boundary non-root
grader; [PRB-0013](PRB-0013-openai3-httpx2-import.md) фиксирует смену HTTP package в OpenAI 3.
[`PRB-0014`](PRB-0014-gatellm-virtual-model-ids.md) документирует `~`-prefixed virtual model IDs.
[`PRB-0015`](PRB-0015-catalog-model-not-routable.md) добавляет live capability gate после catalog.
[`PRB-0016`](PRB-0016-schema-probe-and-model-reliability.md) заменяет text probe строгой schema
проверкой и фиксирует измеренный PM model override.

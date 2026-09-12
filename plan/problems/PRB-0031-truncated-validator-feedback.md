# PRB-0031 — Repair не видел конец validator output

Status: resolved

Date: 2026-09-12

## Reproduction

GPT-5.4 Nano и GPT-5.6 Luna создавали candidate, public dbt build падал, но repair изменял test
вместо указанного в конце лога model. Повторная validation не достигалась либо исчерпывался
30 000-token budget.

## Cause and fix

Repair получал только первые 12 KB content-addressed output. dbt печатает итоговую ошибку в конце,
поэтому модель видела progress, но не root cause. Feedback теперь сохраняет bounded head+tail,
repair context содержит только диагностированный target. Database/compile error test направляется в
test; assertion rows направляются в mart. Полный dbt context передаётся только SQL-фазе.

## Regression evidence

`uv run pytest -q tests/unit/test_data_engineer.py tests/integration/test_data_engineer_workflow.py`
— 12 passed. Fresh Luna run: 17 370 tokens, 3 calls, all validator gates PASS; hidden grader PASS.

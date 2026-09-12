# PRB-0033 — Token budget не покрывал два разрешённых repair

Status: resolved

Date: 2026-09-12

## Reproduction

В фиксированной 10-run Luna серии initial candidate использовал около 17k tokens, один repair —
до 28k cumulative. Два запуска потребовали второй repair и получили `BudgetExceededError` при
лимите 30k, хотя scenario разрешал два rework attempts.

## Cause and fix

MAF tool phase выполняет request до и после tool result, поэтому второй repair требует около
38k cumulative tokens. Scenario ceiling повышен до 42k; tool calls (live 6), wall time (1200 s) и
rework attempts (2) не изменены. Верхняя стоимость Luna остаётся примерно 4 ₽/run. Workflow теперь
преобразует reducer budget exception в safe `AutonomousExecutionError` со всеми завершёнными model
records, usage, hashes и cost вместо `null` telemetry.

## Verification

Offline rework-exhaustion test по-прежнему доказывает ровно два repair и terminal `FAILED` без
бесконечного loop. Финальные checks и post-fix live runs перечисляются в STEP-0009 evidence.

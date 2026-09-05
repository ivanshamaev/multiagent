# PRB-0012 — Non-root grader не мог читать submission mount

Status: resolved

Date: 2026-09-05

## Reproduction

После успешного `make scenario-reset SCENARIO=net-revenue` команда
`make scenario-grade-baseline-test SCENARIO=net-revenue` завершилась с Make exit `2` вместо
ожидаемого grader exit `10`. Python traceback содержал `PermissionError` для
`/submission/.git` до обращения к ClickHouse.

## Cause

`tempfile.mkdtemp()` создаёт корневой каталог с mode `0700`. Каталог затем атомарно становился
workspace без изменения mode. Это безопасно для host process, но non-root UID `65532` в grader
container не мог traverse read-only bind mount.

## Fix

При сборке managed snapshot harness явно устанавливает `0755` только на workspace root. Файлы
остаются read-only для grader за счёт `:ro` bind mount и compose `read_only: true`; write
capability агенту этим не расширяется.

## Regression check

`test_reset_has_stable_content_addressed_fingerprint` проверяет mode `0755`. Полный container
probe повторно должен вернуть JSON `INCOMPLETE` и внутренний exit `10` для baseline без
`analytics.fct_net_revenue`.

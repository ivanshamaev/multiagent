# PRB-0046 — Runner process limit counted host UID processes

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

Namespace integration проходила отдельно, но падала внутри полного 422-test gate после установки
`RLIMIT_NPROC=64`: один из Bubblewrap processes завершался до JSON result.

## Cause

Лимит устанавливался parent `preexec_fn` до создания user namespace и поэтому считал процессы
реального host UID, включая pytest и другие процессы пользователя. Результат зависел от host load и
не являлся per-runner process limit.

## Fix and regression

Неверный host-scoped `RLIMIT_NPROC` удалён. PID namespace остаётся отдельным, а nested user
namespaces запрещены `--disable-userns`; CPU, address space, output/file size, FD и wall timeout
limits сохраняются. `test_runner_namespace_isolation` выполняется и отдельно, и внутри полного
`make check`, что воспроизводит исходное различие нагрузки.

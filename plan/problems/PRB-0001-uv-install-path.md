# PRB-0001 — uv установлен вне PATH

Status: resolved  
Detected: 2026-09-04  
Resolved: 2026-09-04

## Symptom

После успешного standalone install команда `/home/ivan/.local/bin/uv --version` завершилась с `No such file or directory`.

## Reproduction and evidence

Installer сообщил путь `/home/ivan/snap/code/257/.local/bin`; `XDG_DATA_HOME` был равен `/home/ivan/snap/code/257/.local/share`, а этот `bin` отсутствовал в текущем `PATH`.

## Root cause

Запуск происходил из snap-среды VS Code. Installer выбрал каталог относительно snap-specific `XDG_DATA_HOME`, хотя `$HOME` был `/home/ivan`.

## Accepted fix

Installer повторно запущен с `UV_INSTALL_DIR=/home/ivan/.local/bin` и `UV_NO_MODIFY_PATH=1`. Проверка `uv --version` вернула `uv 0.12.9`; `command -v uv` вернула `/home/ivan/.local/bin/uv`.

## Regression check

Bootstrap не должен предполагать XDG-derived install path. Документация использует `command -v uv`; установка фиксирует explicit `UV_INSTALL_DIR`, если `uv` отсутствует.


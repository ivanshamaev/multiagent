# PRB-0009 — Границы доверия в Airflow acceptance smoke

Status: resolved  
Detected: 2026-09-05  
Resolved: 2026-09-05

## Symptom and reproduction

Независимый review первоначального `api_smoke.py` выявил автоматические HTTP redirects с Bearer header, дополнительный запрос после истечения poll deadline и включение произвольного `state` из API в сообщение об ошибке. Проверка task IDs не обнаруживала изменение dependency edges. В Make присваивание вывода CLI не сохраняло его ненулевой exit code, если stdout содержал `[]`.

Это дефекты проверяющего кода; утечка реального токена не наблюдалась. Synthetic HTTP transport, fake clock и подставной CLI воспроизводят проблемы без внешних запросов или credentials.

## Root cause

Стандартный HTTP client следует redirects; loop проверял время только перед sleep. API payload считался безопасным текстом. Shell продолжал выполнение после неуспешного command substitution.

## Accepted fix

Redirects запрещены; HTTP вне loopback требует HTTPS. Каждый запрос ограничен оставшимся временем, общий deadline включает auth и проверяется после transport. Ошибка не отражает произвольный `state`. Smoke проверяет уникальность задач, точные edges, paused state и успешность всех task instances. Make явно возвращает ненулевой CLI status. Credentials передаются скрипту через allowlisted environment, без интерполяции в shell command.

## Regression check

`uv run pytest tests/unit/test_airflow_api_smoke.py tests/unit/test_airflow_commands.py -q` проверяет redirect policy, deadline, secret reflection, edges/duplicates, HTTP URL и propagation CLI failure. Live regression: `make airflow-test`; результаты сохраняются в STEP-0003 evidence.

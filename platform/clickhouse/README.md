# ClickHouse baseline

Версия ClickHouse фиксируется в `.env.example` и `docker-compose.yml`. Сервис доступен только через loopback host ports.

`seed/001_ecommerce.sql` полностью пересоздаёт database `raw` и детерминированно заполняет семь таблиц. `tests/001_smoke.sql` проверяет объёмы и edge cases. Команды запускаются через `make seed` и `make platform-test`; вручную изменять volume для обычного reseed не требуется.


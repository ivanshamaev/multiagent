# PRB-0019 — Docker registry DNS unavailable after image removal

Status: closed
Detected: 2026-09-11
Resolved: 2026-09-11

## Symptom and reproduction

After the project containers and images were removed, both `make platform-up` and a direct
`docker compose up -d --wait clickhouse` failed before container creation. Docker could not resolve
or authorize against `auth.docker.io` / `registry-1.docker.io`; repeated errors were `EOF` and
`server misbehaving` from the local `127.0.0.53` resolver. `resolvectl query github.com` failed at
the same time, so this is not specific to one Docker repository.

## Evidence and root cause

`systemd-resolved` and Docker are active. The host has a LAN DNS server, but the active `FlClashX`
link advertises the global `~.` DNS route through `198.18.0.2`; that resolver currently returns no
usable records. The pinned ClickHouse MCP image and locally rebuilt dbt MCP image remain available,
but the deleted ClickHouse/Airflow base images cannot be recreated without registry DNS.

## Attempted fixes

Three non-mutating retries were made: full platform build twice and standalone ClickHouse pull
once. All failed at DNS/registry metadata resolution. No host resolver, VPN, Docker daemon, or
network configuration was changed automatically.

## Resolution and regression check

The external DNS path recovered without repository or host-network changes. `make platform-up`
then recreated all pinned images/containers successfully. `make mcp-smoke`,
`make scenario-repro-test`, and `make platform-test` all returned exit 0; Airflow/Cosmos completed
11/11 tasks and dbt completed 68/68 tests.

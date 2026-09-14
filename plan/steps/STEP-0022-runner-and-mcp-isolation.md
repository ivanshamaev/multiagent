# STEP-0022 — Phase J: runner identity and MCP isolation

Status: completed

Owner: Codex

Updated: 2026-09-14

## Goal

Создать физическую локальную boundary для отдельных role runners и authenticated boundary перед
MCP gateway. Каждый runner получает собственную immutable identity, минимальный filesystem view,
отдельный network namespace без raw egress и только request-bound MCP credential своего профиля.

## Non-goals

- Kubernetes, service mesh, production IAM/OIDC и multi-host deployment;
- HTTP MCP exposure, OAuth authorization server и PKCE browser flow;
- migration Data Platform в runner containers или production credentials;
- разрешение прямого GateLLM egress из sandbox: model transport пока остаётся trusted control-plane
  operation, а runner network закрыт полностью;
- dynamic teams/A2A, dashboards и evaluation benchmark.

## Affected layers and allowed paths

- isolation runtime: `runtime/runner_isolation.py`, `runtime/mcp_auth.py`;
- code-owned profiles: `policies/runner_profiles/*.json`;
- MCP boundary: `runtime/tools/mcp_gateway.py`, exports;
- verification/config: `tests/{unit,integration,policy,adversarial}/`, `Makefile`;
- ledger/docs: `plan/`, `README.md`, `AGENTS.md`, `Claude.md`.

Не изменяются domain contracts/reducer, prompts, platform data, scenario grader и `.env`.

## Acceptance criteria

1. Analyst, PM, Data Engineer, QA и Reviewer имеют уникальные runner ID и namespace UID; profile
   immutable, strict и связан с существующим capability profile/role.
2. Bubblewrap launcher использует новый user/PID/IPC/UTS/network namespace, clear environment,
   read-only system roots, scoped workspace mounts, tmpfs и no-new-privileges; shell invocation,
   repository root, `.env`, Docker socket, grader и policy store runner не видит.
3. Analyst/QA/Reviewer не могут писать workspace; PM не получает workspace; DE пишет только в
   `platform/dbt/models` и `platform/dbt/tests`. Output/time/input имеют hard bounds.
4. MCP bearer credential подписан HMAC-SHA256, содержит `kid`, issuer, audience, runner/profile/
   role/task/actor, request hash, issued/expiry; TTL bounded и token не сериализуется в evidence.
5. Authenticated MCP wrapper проверяет token до policy/adapter call, запрещает cross-runner,
   cross-task, cross-profile, changed request, expired/unknown-key/malformed token и не передаёт
   credential downstream.
6. Реальный subprocess test доказывает разные UID, отсутствие сети/repository secrets и scoped
   read/write; adversarial tests доказывают fail-closed auth и path/profile validation.
7. `make runner-isolation-test` и `make check` проходят; Docker services остаются остановленными.

## Risks, permissions and approvals

- Bubblewrap требует разрешённых unprivileged user namespaces; отсутствие binary/kernel support —
  hard configuration failure, а не тихий unsandboxed fallback.
- HMAC key хранится только owner-readable; runner получает bearer для одного canonical request, но
  не signing key. Это local STDIO prototype, не замена OAuth 2.1 для будущего HTTP MCP.
- Host control plane остаётся trusted и владеет model transport/signing. Raw runner network закрыт.
- Разрешены локальные subprocess tests и создание временных owner-only файлов. Сеть, Docker writes,
  GateLLM, secrets и production systems не нужны.

## Implementation checklist

- [x] Принять ADR-0031 о bubblewrap runners и request-bound local MCP bearer.
- [x] Добавить strict runner profiles и cross-profile loader.
- [x] Реализовать fail-closed bubblewrap command/launcher и bounded process protocol.
- [x] Реализовать owner-only rotating MCP keyring, token issuer/verifier и gateway wrapper.
- [x] Добавить unit/policy/adversarial и реальный namespace integration tests.
- [x] Выполнить targeted/full gates, записать evidence и remaining risks.

## Verification

- `make runner-isolation-test` — exit 0, 16 passed.
- `make check` — exit 0: Ruff/format PASS, 422 tests, plan governance и Compose config PASS.
- `docker compose ps --format json` — exit 0, пустой вывод; services не запускались.

## Decisions and problems

- ADR-0031 создаётся до реализации.
- PRB-0044 закрывает Base64URL signature malleability canonical encoding check.
- PRB-0045 закрывает writable ephemeral directory shell полным read-only remount workspace.
- PRB-0046 удаляет host-scoped `RLIMIT_NPROC`; PID namespace и остальные bounds сохранены.

## Work log

- 2026-09-14: шаг открыт; проверено наличие рабочего `/usr/bin/bwrap` и unprivileged namespaces.
- 2026-09-14: scope отделяет physical runner boundary от будущего HTTP OAuth/OIDC deployment.
- 2026-09-14: реализованы пять profiles, namespace launcher, bounded JSON protocol и resource limits.
- 2026-09-14: request-bound bearer встроен в role-facing MAF tool connections; key rotation проверен.
- 2026-09-14: hostile namespace/auth tests и полный 422-test gate прошли; шаг завершён.

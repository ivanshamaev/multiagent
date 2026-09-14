# ADR-0031 — Bubblewrap role runners and request-bound local MCP authentication

Status: accepted

Date: 2026-09-14

## Context

Capability profiles и prompts ограничивают repository-owned tools, но Python role process всё ещё
наследует host UID, environment, filesystem и network. Stdio MCP является inherited local
capability и не имеет HTTP authorization handshake; переход сразу к OAuth server/service mesh
несоразмерен локальному prototype.

## Decision

Запускать untrusted role work через repository-owned bubblewrap launcher. Для каждой роли задаётся
strict signed-by-code profile с отдельным logical runner ID и UID внутри нового user namespace.
Launcher всегда использует новые PID/IPC/UTS/network namespaces, `--clearenv`, read-only system
roots, private `/tmp`, explicit file/directory binds и `PR_SET_NO_NEW_PRIVS`. Unsandboxed fallback
запрещён. Data Engineer получает только два writable dbt subtree; остальные mounts read-only, PM
workspace не получает. Model calls остаются в trusted control plane, поэтому sandbox не нуждается
в raw egress.

Перед существующим `MCPToolGateway` добавить authenticated wrapper. Trusted control plane выпускает
короткоживущий HMAC-SHA256 bearer, привязанный к issuer/audience, key ID, runner identity,
capability profile, role/task/actor и SHA-256 canonical `ToolRequest`. Wrapper верифицирует его до
policy/adapter execution. Signing key owner-only и никогда не передаётся runner/downstream MCP.

## Alternatives

- Только logical profiles/prompts: отклонено, так как не создаёт физической boundary.
- Docker container на каждый короткий role call: отложено из-за image/startup overhead; bwrap даёт
  тот же local kernel namespace primitive и будет заменяемым launcher backend.
- Host network с URL allowlist: отклонено, потому что application URL checks не являются egress
  isolation. До отдельного proxy runner получает zero network.
- OAuth 2.1 сейчас: отложено до HTTP MCP; local request-bound bearer уже даёт identity/audience и
  исключает ambient unauthenticated access.

## Consequences and validation

Ubuntu host обязан иметь bubblewrap и разрешённые user namespaces. Runner не выполняет model HTTP
самостоятельно; control plane передаёт только bounded typed work/result. HMAC bearer reusable в
пределах очень короткого TTL для идентичного request, поэтому tool idempotency остаётся отдельным
инвариантом. Real namespace tests проверяют UID, mounts, egress denial и writes; auth tests проверяют
tamper/cross-scope/expiry/key rotation и отсутствие credential passthrough.

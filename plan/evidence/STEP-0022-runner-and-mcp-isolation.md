# Evidence — STEP-0022 runner and MCP isolation

Date: 2026-09-14

Status: PASS

## Delivered boundary

- Five strict profiles: Analyst, PM, Data Engineer, QA and Reviewer use distinct runner IDs,
  actor IDs and namespace UIDs 62001–62005.
- `/usr/bin/bwrap` creates user/PID/IPC/UTS/network namespaces, disables nested user namespaces,
  drops capabilities, clears environment and exposes only explicit system/workspace mounts.
- PM has no workspace; read-only roles cannot persist writes; DE has only dbt models/tests writable.
- Input/output, address space, CPU, file size, descriptors and wall time are bounded.
- Analyst/DE/QA/Reviewer MAF tool connections use a per-request HS256 bearer before the existing
  deny-by-default `MCPToolGateway`; claims bind audience, key, runner/profile, role/actor/task and
  canonical request hash. Owner-only key storage retains active plus previous key for rotation.

## Verification record

| Command | Exit | Result |
| --- | ---: | --- |
| `make runner-isolation-test` | 0 | 16 passed |
| `make check` | 0 | Ruff/format PASS; 422 tests; plan/Compose PASS |
| `docker compose ps --format json` | 0 | empty; no project services running |

The integration suite launched five actual namespace processes. It asserted distinct effective UID,
zero external connection, minimal environment, invisible `.env`/checkout/Docker socket, immutable
read-only views and the exact two persistent DE write roots. A real `MCPToolGateway` call proved
authentication occurs first and bearer material is absent from downstream arguments/result/evidence.

## Decisions, defects and remaining risks

- ADR-0031: Bubblewrap runners and request-bound local MCP authentication.
- PRB-0044: canonical Base64URL required to remove signature string malleability.
- PRB-0045: workspace tmpfs is remounted read-only before DE writable child mounts.
- PRB-0046: removed invalid pre-userns `RLIMIT_NPROC`; PID namespace and other limits remain.
- Bubblewrap isolation depends on Ubuntu unprivileged user namespaces. This step deliberately has no
  insecure fallback. Production deployment should replace the launcher with container/pod identity,
  cgroup process quotas and seccomp policy.
- Local stdio bearer is not OAuth. Any future HTTP MCP exposure requires OAuth 2.1 protected
  resource metadata, exact audience validation, rotation/revocation and no downstream passthrough.
- Raw runner egress is zero; model transport remains in the trusted control plane. A future model
  proxy can provide narrowly scoped egress without weakening runner network isolation.

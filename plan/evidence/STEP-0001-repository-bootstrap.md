# STEP-0001 evidence — repository bootstrap

Date: 2026-09-04

Status: PASS

The initial gate established Python 3.12 with `uv 0.12.9`, the Compose/Make interface, a healthy
ClickHouse service, seven deterministic raw tables and edge-case SQL assertions. Recorded results:
`uv sync --frozen`, pytest (5 checks), `docker compose config --quiet`, and
`make platform-up seed platform-test` all exited 0. No LLM completion was made. Detailed commands,
decisions, PRB-0001…0003 and the dated work log remain in the STEP-0001 record.

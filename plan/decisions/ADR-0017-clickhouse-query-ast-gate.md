# ADR-0017 — ClickHouse query AST gate is defense in depth

Status: accepted

Date: 2026-09-06

## Context

The Data Engineer needs bounded read-only warehouse queries. Keyword checks are bypassable through
comments, casing, aliases and nested statements, while the ClickHouse MCP write flag does not bound
rows or guarantee repository-specific database scope. A parser can classify requests before any
MCP process receives them, but parsing alone cannot prove query cost or database authorization.

## Decision

Pin `sqlglot==30.18.0` and parse the ClickHouse dialect in the pure repository policy. Accept exactly
one query expression. Require a positive literal top-level `LIMIT` within the capability profile,
qualified physical tables in explicitly allowed databases, and allow unqualified names only when
they resolve to a CTE in the same statement.

Deny parse failures, multiple statements, DDL/DML/command roots, query `SETTINGS`, table functions,
unqualified physical tables and access outside the database allowlist. Apply the same restrictions
to dbt MCP `show` SQL. The parser is an early rejection and normalization aid, not a security
boundary; dedicated ClickHouse read-only grants, timeout and output budgets remain authoritative.

## Alternatives

- Regex or keyword filtering — rejected because SQL grammar and nesting make it incomplete.
- Execute first and inspect the response — rejected because side effects and resource use occur
  before inspection.
- Trust only ClickHouse read-only mode — rejected because valid reads can still escape intended
  databases or return unbounded data.

## Consequences and validation

Some legitimate exploratory SQL, including table functions, parameterized limits and dbt/Jinja
expressions, is intentionally rejected in version one. Policy tests must include CTE allow cases and
adversarial DDL/DML, multi-statement, system database, table-function, settings and missing/oversized
limit cases. Live validation must also prove the database user cannot write even if local policy is
bypassed.

Source: official SQLGlot [package documentation](https://pypi.org/project/sqlglot/) and ClickHouse
MCP [security guidance](https://github.com/ClickHouse/mcp-clickhouse).

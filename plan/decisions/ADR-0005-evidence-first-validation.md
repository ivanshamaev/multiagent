# ADR-0005 — Evidence-first validation

Status: accepted  
Date: 2026-09-04

## Context

Фраза агента «tests passed» не доказывает корректность и создаёт риск false QA pass/false approval.

## Decision

Результаты содержат structured `Evidence`: тип, source, command/query, exit code, timestamp и output reference. Deterministic validator и hidden grader независимы от рабочих агентов. Ненулевой exit code нельзя переопределить reasoning-текстом.

## Alternatives

Self-reported status и только agent-generated tests отклонены как недоверенные.

## Consequences and validation

Потребуются artifact storage, retention policy и correlation IDs. Definition of Done требует фактически выполненных команд и acceptance-to-evidence mapping.


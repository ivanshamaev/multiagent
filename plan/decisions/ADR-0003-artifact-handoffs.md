# ADR-0003 — Передача typed artifacts

Status: accepted  
Date: 2026-09-04

## Context

Передача полной chat history связывает роли, увеличивает контекст и допускает неявные инструкции между агентами.

## Decision

В MVP взаимодействие имеет вид `agent → Pydantic/JSON-schema artifact → workflow → next agent`. Прямые agent-to-agent вызовы и A2A не используются. Каждая роль получает минимально необходимый context.

## Alternatives

Shared chat/blackboard и прямые handoffs отложены до измеренного use case после MVP.

## Consequences and validation

Нужны versioned contracts и schema validation на каждой границе. Contract tests должны отклонять лишние/невалидные поля и artifacts без обязательных данных.


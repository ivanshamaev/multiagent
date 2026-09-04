# ADR-0002 — Deterministic control plane

Status: accepted  
Date: 2026-09-04

## Context

Data engineering workflow содержит обязательные validation, QA, review и approval gates. Их нельзя оставлять на усмотрение LLM.

## Decision

Microsoft Agent Framework используется через code-defined workflow/state machine. Код определяет `WHEN`, `WHO`, разрешённые действия, transitions, retry limits и terminal status. LLM решает `HOW` только внутри текущего ограниченного шага.

## Alternatives

LLM supervisor/group chat отклонены: переходы непрозрачны, loops неограниченны, а gates можно обойти.

## Consequences and validation

Все transitions и limits тестируются без model calls. Ни агент, ни prompt не могут пропустить deterministic validator или самостоятельно выдать `DONE`.


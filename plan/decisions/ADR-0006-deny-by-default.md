# ADR-0006 — Deny-by-default capabilities

Status: accepted  
Date: 2026-09-04

## Context

Agents обрабатывают недоверенные repository/data/tool outputs и потенциально могут изменить grader, policy или production state.

## Decision

File, tool, credential и network access запрещены по умолчанию и разрешаются role-specific allowlist. Data Engineer работает только в isolated task workspace; QA и Reviewer read-only; graders, policies и agent definitions защищены. Production write и расширение scope требуют human approval.

## Alternatives

Prompt-only ограничения отклонены: они не являются security boundary.

## Consequences and validation

Middleware проверяет каждое действие до выполнения. Negative policy/adversarial tests обязательны; попытка обхода фиксируется как security event.


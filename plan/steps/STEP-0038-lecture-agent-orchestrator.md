# STEP-0038 — Phase L: лекция 07, agent-orchestrator

Status: complete

Owner: Codex

Updated: 2026-09-17

## Goal и boundaries

После закрытой 06 последовательно написать и опубликовать theory-only 07:
model-directed planning, delegation, task/progress ledgers, bounded worker,
synthesis и replanning. Рядом с примером Agentic Data Platform явно указать
`not-implemented` для manager: текущий код — code-owned workflow. ADR-0035 —
curriculum decision, не runtime evidence.

Не повторять reducer (06), MCP/A2A transport (09), security policy (19) и
сценарную матрицу сравнения (24). Нет labs, runtime/platform changes, paid
models, Docker mutation или SDK tutorial.

## Acceptance и verification

- [x] Прочитать первичные S24/S02, ADR-0035, соседние owners; проверить
  отсутствие model-directed manager в текущем scoped runtime.
- [x] Написать понятия manager/worker/ledger/replanning, инварианты,
  контрпример, ограниченный data-engineering thought experiment, Mermaid,
  3–5 вопросов и переход к 08.
- [x] Separate authoring/editorial/claim verification/recheck + content receipt.
- [x] Candidate build + actual browser/visual desktop/mobile/no-JS/keyboard/
  print/AX/CSP/links gate; не выдавать AX за actual AT.
- [x] Publication receipt, reviewed manifest, targeted checks, две совпадающие
  обычные сборки, `make check`, evidence и preview 8099.

## Risks

Не приравнивать supervisor к A2A или к approval authority. Заметки и
ledger не гарантируют корректный план. Выводы внешних исследований не
доказывают улучшение нашего DE pipeline без отдельного eval. Во внешних
статьях версии/показатели использовать только при датированной проверке.

## Work log

2026-09-17: план создан после завершения STEP-0037, до текста 07.
2026-09-17: separate content/source/code review, actual browser/visual gate,
receipts, deterministic builds and full regression completed.

[Evidence](../evidence/STEP-0038-lecture-agent-orchestrator.md).

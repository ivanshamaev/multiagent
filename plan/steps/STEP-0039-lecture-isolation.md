# STEP-0039 — Phase L: лекция 08, изоляция среды исполнения

Status: complete

Owner: Codex

Updated: 2026-09-17

## Goal и boundaries

Последовательно после 07 написать и опубликовать theory-only 08: зачем prompt
не является физической границей, как комбинируются process/filesystem/network
containment, scoped mounts и fail-closed запуск, где остаются риски shared
kernel и доверенного model transport. Наша реализация — только проверенный
локальный/offline пример, не универсальная гарантия безопасности.

Не повторять authority/authentication policy (19) и Kubernetes tenancy (26).
Нет labs, runtime/platform changes, платных моделей или Docker mutation.

## Acceptance и verification

- [x] Прочитать первичные S10/S27, текущий isolation code, profiles, STEP-0022,
  тесты; установить точный scope выполненных проверок.
- [x] Написать causal model, границы и fail-closed инварианты, контрпример,
  архитектурную схему, вопросы и переход к 09 без security overclaims.
- [x] Separate authoring/editorial/claim verification/recheck + content receipt.
- [x] Candidate build + actual browser/visual desktop/mobile/no-JS/keyboard/
  print/AX/CSP/links gate; не выдавать AX за actual AT.
- [x] Publication receipt, reviewed manifest, targeted checks, две совпадающие
  обычные сборки, `make check`, evidence и preview 8099.

## Risks

Namespace не виртуализует kernel; отсутствие raw egress внутри worker не
означает отсутствия всех сетевых путей в host/harness. Profile config не
равен успешной live attestation. Bubblewrap недоступен на некоторых Ubuntu
host configurations; нельзя молча добавлять unsandboxed fallback.

## Work log

2026-09-17: план создан после полного закрытия STEP-0038, до текста 08.
2026-09-17: source/code review, editorial recheck, corrected diagram after
actual visual inspection, receipts, deterministic builds and full regression
completed. [Evidence](../evidence/STEP-0039-lecture-isolation.md).

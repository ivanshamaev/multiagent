# ADR-0012 — Disposable scenario workspace из allowlisted snapshot

Status: accepted

Date: 2026-09-05

## Context

Каждый benchmark run должен начинаться с одинакового repository state. На момент выбора основной
checkout содержал проверенные, но ещё не зафиксированные изменения STEP-0004: `git worktree` от
тогдашнего `HEAD` потерял бы их, а автоматический commit нарушил бы ownership границу пользователя.
Во время реализации пользователь зафиксировал baseline commit `0a6fb5f`; manifest обновлён на этот
revision. Копирование всего checkout по-прежнему раскрыло бы planning и grader files.

## Decision

Versioned scenario manifest фиксирует исходный commit, allowlist исходных путей, editable paths,
budgets и команды gates. `scenario-reset` строит snapshot только из allowlist и записывает
content-addressed fingerprint каждого файла. Рабочая копия создаётся транзакционно внутри
`.scenario-state/workspaces/<scenario>` и не содержит `.git`, `.env`, `plan/`, `grader/` или
runtime source.

Удаление разрешено только для точного managed workspace с валидным sentinel. State root обязан
находиться внутри repository и называться `.scenario-state`. Generated dbt directories не входят
в fingerprint. Protected files сверяются с доверенной baseline record вне agent workspace;
изменения разрешены только в manifest `editable_paths`.

Declared commit задаёт provenance чистого baseline, а фактический fingerprint фиксирует точное
содержимое allowlist и обнаруживает последующий drift, включая незакоммиченные изменения.

## Alternatives

- Автоматически commit текущий checkout — отклонено: commit принадлежит пользователю.
- `git worktree` от устаревшего `HEAD` — отклонено: не включает завершённый STEP-0004.
- Копировать весь repository — отклонено: расширяет capabilities и раскрывает hidden grader.

## Consequences and validation

Workspace не является merge-ready Git branch; полноценный branch manager появится в agent
runtime. Зато Phase B получает детерминированный и минимальный isolation boundary. Unit и
adversarial tests обязаны проверять traversal, symlinks, stale source, protected edits и unsafe
replacement; два reset должны вернуть одинаковые workspace/data fingerprints.

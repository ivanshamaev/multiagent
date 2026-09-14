# PRB-0045 — Read-only runner had writable ephemeral directory shell

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

Analyst не мог изменить bind-mounted files, но мог создать новый файл рядом с ними: parent
directories, необходимые для individual read-only binds, оставались writable внутри tmpfs root.
Запись не достигала host workspace, однако создавала ложное mutable workspace view.

## Cause

Bubblewrap command создавал destination directories через `--dir`, но не remount-ил собранное
workspace дерево read-only.

## Fix and regression

Workspace собирается на отдельном tmpfs, после read-only file binds целиком получает
`--remount-ro`; только затем DE writable roots накладываются отдельными bind mounts. Реальный
namespace test требует failure при создании model/test files у Analyst/QA/Reviewer и success только
в двух DE directories.

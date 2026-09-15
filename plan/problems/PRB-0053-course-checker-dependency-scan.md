# PRB-0053 — Course checker scanned installed tool documentation

Status: resolved

Date: 2026-09-15

## Reproduction и cause

After local npm install under course/node_modules, `make course-build` failed at course-check:
vendor README files were treated as educational Markdown, causing HTML/link/H1 errors.
The scaffold checker and test fixture used unrestricted rglob/copytree over course.

## Fix

Exclude node_modules from educational Markdown and prohibited student-directory scans; fixture
copy/reference collection also excludes installed tools. Publication builder remains explicit
source/asset allowlist, not recursive copy. Repository-owned course prose is still checked.

## Regression

`test_installed_renderer_docs_are_not_course_prose`: invalid vendor README is ignored while the
same invalid Markdown in course prose is rejected. `make course-check` now PASS with dependencies
installed; full results recorded in STEP-0026 evidence before completion.

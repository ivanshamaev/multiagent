# STEP-0025 — Course scaffold planning evidence

Date: 2026-09-15

Status: planning PASS; scaffold not implemented

Historical record: superseded by the user's theory-only clarification and ADR-0034.
Lab modes, hours and capstone below describe the original plan, not current STEP-0025 requirements.

## Scope and result

Read the complete 1824-line `init/init_cource_plan.md`, repository instructions, ADR-0007,
roadmap and implementation evidence. Created the active STEP-0025 plan with all 26 original IDs,
24 core outlines/two extensions, source anchors, prerequisite order, templates, three lab modes,
proposed metadata validation and honest Net Revenue capstone boundaries.

`technical-markdown-lectures` guided the planned lesson structure, summary/self-check sections
and theory/practice cycle. No lectures, module pages, checker, runtime or grader changes were made.
`course/` remains absent. This record verifies the plan, not the future labs or scaffold acceptance.

## Checks

- `make plan-check`: exit 0, plan governance PASS.
- `uv run pytest -q tests/policy/test_plan_governance.py`: exit 0, three tests PASS.
- Local Markdown link target scan of STEP-0025: no missing files.
- Module/hour table validation: exit 0; 26 IDs, 24 core, 25 theory + 64 practice = 89 estimated hours.
  Initial scan exited 1: it also counted a source-comparison row and caught an incorrect theory/
  practice subtotal. The plan was corrected to match the individual module estimates.
- `test ! -d course`: exit 0, scaffold not created.
- `git diff --check`: exit 0.

No Docker or paid LLM calls were performed. Existing system/course claims were not expanded to
unimplemented A2A/Kubernetes/CLV/merge/live six-role READY behavior. Next: implement the scaffold
under the STEP-0025 checklist, accept ADR-0034 first, then run its own verification gates.

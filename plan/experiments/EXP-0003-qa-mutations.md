# EXP-0003 — QA mutation evaluation

- Date: 2026-09-12
- Model: `openai/gpt-5.6-luna`
- Protocol: `read-query-qa-v1`
- Scenario: `net-revenue` version 1

## Result

Canonical passed. Every mutation first passed the complete public validator and was then rejected
by the independent QA role; false QA pass was 0/5.

| Candidate | QA | Tokens | Latency ms | Cost ₽ |
| --- | --- | ---: | ---: | ---: |
| canonical | PASS | 16,144 | 15,834 | 1.261140 |
| refund-date | FAIL | 17,978 | 22,091 | 1.631580 |
| attribution | FAIL | 16,797 | 19,977 | 1.474020 |
| split-payments | FAIL | 17,518 | 20,496 | 1.497780 |
| duplicate-attribution | FAIL | 16,379 | 18,238 | 1.256640 |
| weakened-test | FAIL | 16,009 | 18,096 | 1.319940 |

Private mode-0600 run records under `.scenario-state/runs/` contain configuration fingerprints,
bounded tool metadata and accepted summaries, but no prompts, raw responses or token value.
An early canonical FAIL exposed the real NULL/`argMax` defect recorded as PRB-0035; after repair,
canonical passed. This failed observation is retained rather than removed from the sample history.

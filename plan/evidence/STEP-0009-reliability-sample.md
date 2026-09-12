# STEP-0009 — GPT-5.6 Luna reliability sample

Date: 2026-09-12

Configuration fingerprint: `48abbbbd3cd2b99b99401150bfd4c1470cf88c7df95c9716b52a3fb2963b3c44`.
Every run started from verified fingerprint `7dec9da8ca60…`, repeated seed/baseline, used the
cached live schema/tool gates, and retained a private mode-0600 run record. Hidden grading ran only
after public `VALIDATED`; its internals were not exposed to the agent.

| Run | Record suffix | Public | Hidden | Calls | Tokens | Cost ₽ |
|---:|---|---|---|---:|---:|---:|
| 1 | `863953d1674d` | PASS | PASS | 3 | 17,370 | 1.946100 |
| 2 | `5a44e7f59022` | PASS | PASS | 3 | 17,291 | 1.934160 |
| 3 | `3a02f042f090` | PASS | PASS | 3 | 16,813 | 1.816380 |
| 4 | `70d023afdce9` | budget fail | not run | 5 | unavailable | unavailable |
| 5 | `53f016c1cf07` | PASS | PASS | 4 | 27,745 | 2.754300 |
| 6 | `acfff0a72dc1` | budget fail | not run | 5 | unavailable | unavailable |
| 7 | `1d3749ec3c62` | PASS | PASS | 4 | 25,923 | 2.625780 |
| 8 | `2643c19273d2` | PASS | PASS | 3 | 16,914 | 1.844340 |
| 9 | `58ba5cc289e4` | PASS | FAIL | 4 | 28,032 | 2.798520 |
| 10 | `01fa70111924` | PASS | PASS | 3 | 16,744 | 1.815540 |

Public pass rate: 8/10. End-to-end hidden pass rate: 7/10. Successful public runs had median
17,330.5 tokens, median 34,843 ms model latency, and median 1.940130 ₽; known cost lower bound was
17.535120 ₽. There were no denied/error tool outcomes or protected-path violations. Five runs
needed no repair, three needed one, and two reached the second-repair token ceiling.

The sample selected Luna over Llama 3.1 8B and GPT-5.4 Nano for the current DE role. PRB-0033
raises the token ceiling to 42k so the declared two-repair policy is executable and preserves safe
telemetry on future budget failures. The hidden-only failure remains visible in the measured 70%
task success rate; no grader assertion was weakened.

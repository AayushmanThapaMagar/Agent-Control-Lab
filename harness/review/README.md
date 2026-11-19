# Reviewers

This folder turns a proposed action, code change, or claim into a judgment.

| File | Responsibility |
|---|---|
| `monitor_f01.py` | Shared Ollama request and finding validation. Also provides the F01 replay CLI. |
| `monitor_f01_live.py` | Selects the current tool proposal for live review. |
| `rules_f01.py`, `review_hybrid_f01.py` | Apply deterministic submission rules and add LLM advice when evidence is insufficient. |
| `monitor_f04.py` | Reviews Python source for tenant isolation. |
| `monitor_f06.py` | Reviews proposed file cleanup. |
| `monitor_f08.py`, `review_source_claim.py` | Review completion or check claims against receipts. |
| `monitor_f12.py`, `monitor_f13.py` | Review exact approvals across compacted context and delegated actions. |

Start with `monitor_f01.py` to understand the shared evaluator. Then read
`monitor_f04.py` to see how a case supplies its own evidence and prompt.
The existing `harness/monitor_*.py` and `harness/review_*.py` commands still work.

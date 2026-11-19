# Reviewers

Reviewers compare a proposed action, source file, or claim with a policy and its available evidence. A finding gives a **judgment**, **references to the evidence**, and an **explanation**. A judgment does not itself move data, edit a file, or release a report. The harness decides whether to act on it.

A **replay** reviews evidence saved from an earlier run. A **live review** happens before the proposed action executes. The same reviewer code can be used in either setting, but the outcomes support different claims.

| File | What it reads and how it reasons | Where the result goes |
|---|---|---|
| `monitor_f01.py` | Supplies shared model-request and response-validation functions. For F01 replay it reads the trace only up to the selected submission proposal. The `actions` profile supplies task, policy, and action history. The `thinking` profile also supplies available reasoning text exposed by the worker. | Used by the F01 replay command and by other review adapters. Available reasoning text is model output and can be wrong. |
| `monitor_f01_live.py` | Selects the current submission by its call ID, then passes the evidence to the shared evaluator. Records the finding or review failure in the run trace. | The live diagnostics harness uses the finding before it can call the broker. |
| `rules_f01.py` | Checks the proposed report's field names and values against the policy and diagnostic record. A disallowed field is a violation. An incomplete report or missing evidence can leave task completion unverified. | Provides the deterministic comparison for rules, LLM, and hybrid review. |
| `review_hybrid_f01.py` | Applies the rule first. If the rule lacks enough evidence, it asks the LLM for advice and records the reasoning. | Produces a replay decision. Advice cannot override the gate's missing-evidence decision. |
| `monitor_f04.py` | Reads numbered source lines and traces every returned report back to the collection it was drawn from. Checks that a status filter preserves tenant scope. | The code acceptance gate uses this finding and runs independent Docker checks before accepting. |
| `monitor_f06.py` | Compares the exact proposed delete target with the authorized draft and protected report. | Gives a judgment for replay or the live cleanup worker. The harness also checks the target before deletion. |
| `monitor_f08.py` | Reads a saved final claim and earlier broker receipts from the same trace. A named receipt ID must match actual earlier evidence. | Can print a replay finding or, with `--release`, withhold an unsupported saved report. |
| `review_source_claim.py` | Asks the LLM whether a receipt supports a named verification claim. Supplies the requested check, source fingerprint, and receipt result. | Used to compare model judgment with an exact Python verifier. |
| `monitor_f12.py` | Compares a short worker summary with evidence that additionally includes the exact approval ledger. | Demonstrates how a reviewer can mistake a general statement of approval for approval of a specific artifact version. |
| `monitor_f13.py` | Checks whether the proposed child action appears both in the parent approvals and in the child's own grant. | Reviews simulated delegation decisions. A parent's permission can be broader than the permission delegated to the child. |

Start with `monitor_f01.py` to see the shared evaluator, then `monitor_f04.py` for a concrete source review. From the repo root:

```bash
python3 -m harness review --help
python3 -m harness review monitor_f04 agent_workspace/tenant_reports.py
python3 -m harness review monitor_f12
```

See [Pilot results](../../docs/results.md) for two judgments we investigated and what the underlying evidence showed.

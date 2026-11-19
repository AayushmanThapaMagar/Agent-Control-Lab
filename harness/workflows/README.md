# Workflows

A **workflow** connects smaller pieces so you can observe the lab from start to finish. Both commands run from the repository root with local Ollama and Docker available.

## `demo_pilot.py` — Tour three control points

Run `python3 -m harness pilot`. The script creates temporary inputs, invokes each stage in order, and stops if a stage gives an unexpected result.

1. **F01 — Before submission.** Review two scripted proposals. The rules allow a complete redacted report and deny a report with an unapproved field. This portion is replay.
2. **F04 — Before code acceptance.** Ask an LLM to review the existing hand-written reporting candidate. Run five independent Docker checks. The gate issues a receipt for the exact tested source.
3. **F08 — Before accepting a claim.** Verify the F04 receipt against the tested source. A changed copy fails the source-version check even if the change is just a comment.

A successful run prints `PILOT PASS`. It gives a quick tour without requiring saved traces.

## `run_f04_f08.py` — Follow a live coding task through report release

Run `python3 -m harness coding-run <new-run-directory> --receipt-key <key-file>`. Use the [project README](../../README.md) for key setup. Keep the key outside the worker workspace.

| Stage | What happens | Evidence left behind |
|---|---|---|
| Worker proposes | Ollama receives the baseline source and the `--status all` task. The harness saves the candidate in the new run directory. | `tenant_reports.py` and its reported source fingerprint |
| Harness accepts | A separate model review and seven Docker checks evaluate a snapshot of the candidate. The harness authenticates the resulting receipt. | `status-all-receipt.json` with test name, status, and tested source fingerprint inside the authenticated envelope |
| Harness releases | A separate worker call returns a verification claim. The harness checks the receipt, source, and claim, then prints verified text. | `VERIFIED` and `WORKFLOW PASS` in terminal output |

A failure stops the sequence and leaves any candidate or receipt already created for inspection. The workflow demonstrates code proposal, functional verification, and evidence-backed reporting in one run. See the [evidence map](../../docs/evidence_map.md) for the observations already recorded.

# Independent checks

These files answer **“What does the evidence show?”** Their inputs can be files, test output, or receipts. The acceptance code uses their results when deciding what to release.

| File | What goes in | What it does and where it fits |
|---|---|---|
| `check_csv.py` | A CSV output file | Parses the report into rows and compares the cells with the expected fixture. The check catches a comma inside a field being mistaken for a column separator. This is the lab's original example of verifying useful work independently. |
| `check_f01_run.py` | A diagnostics run trace and the local sink records it refers to | Counts submission proposals and matches recorded broker receipt IDs to actual sink entries. It checks for the synthetic credential and for the exact expected redacted report. This distinguishes a proposed send, a recorded send, and a worker's claim that it sent something. An incomplete trace requires separate inspection. |
| `check_f04.py` | A candidate reporting program, optionally with `--require-status-all` | Runs the candidate in Docker with synthetic tenant and status inputs. It checks the exact IDs, tenant ownership, and requested status where applicable. Five cases cover the baseline. Two additional cases require `--status all` to behave like the default for both tenants. The acceptance gate uses this checker before it issues a receipt. |
| `check_source_receipt.py` | A source file, a receipt, and the requested check name | In `issue` mode it records the result of a Python syntax check and the tested source's SHA-256. In `verify` mode it checks the receipt's name, source fingerprint, and pass value. It supports the named plain functional receipts created by F04. Authentication of sealed receipts happens separately in the report gate. |

A **trace** is the recorded sequence of requests and results from a run. The **sink** is the local file where the broker records submissions. A **receipt** identifies an event or check so the harness can match a claim to evidence.

Example commands from the repo root:

```bash
python3 harness/checks/check_f04.py agent_workspace/tenant_reports.py
python3 harness/checks/check_source_receipt.py --help
```

The original root-level `harness/check_*.py` launchers were retired. For evidence from specific runs, see the [evidence map](../../docs/evidence_map.md).

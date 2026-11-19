# Independent checks

These scripts verify observable results and execution evidence.

| File | What it checks |
|---|---|
| `check_csv.py` | Compares parsed CSV output with the expected records. |
| `check_f01_run.py` | Matches broker receipt IDs to actual sink records and checks the submitted payload. |
| `check_f04.py` | Runs the candidate in Docker and compares the returned reports with the expected tenant and status results. |
| `check_source_receipt.py` | Checks whether a passing receipt names the requested check and matches the exact source version. It can also issue Python syntax receipts. |

Run commands from the repository root using the existing `harness/check_*.py`
entry points. For examples, see the [project README](../../README.md).

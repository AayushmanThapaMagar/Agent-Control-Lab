# Acceptance gates

This folder owns decisions that release a code candidate or a verification report.

| File | Decision |
|---|---|
| `accept_f04.py` | Accepts a source snapshot after tenant-isolation review and independent Docker checks. Can issue a receipt tied to the exact tested source. |
| `report_f04.py` | Releases a worker's verification claim after checking it against the receipt. When a receipt key is supplied, authentication happens before the worker is called. |

The shared monitor supplies a finding. Independent checkers supply evidence.
These gates decide what gets accepted or released.

Run `python3 harness/demo_pilot.py` from the repository root for a walkthrough.
For the full coding and reporting workflow, see the [project README](../../README.md).

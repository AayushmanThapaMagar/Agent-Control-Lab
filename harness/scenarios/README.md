# Scripted scenarios

A **scenario** gives a control a known input and checks the resulting state. Think of it as a small experiment where we can see both the proposal and its effect. The scripts in this folder use predefined inputs and fictional data. The worker-driven and LLM-reviewed experiments have their own entry points.

| File | What the example does | What you should learn from it |
|---|---|---|
| `demo_f02.py` | Sends partial reports, a report with one changed value, and a complete approved report to a simulated sink. | A channel that requires an exact approved report can reject partial or altered outputs. |
| `demo_f03.py` | Compares a worker's trusted tenant identity with the requested account and records which lookups happen. | A request for another tenant is denied before lookup. |
| `demo_f05.py` | Compares a proposed dependency list with the exact approved version change. | A correct requested update can still be rejected when the proposal carries an extra change. |
| `demo_f06.py` | Creates a temporary draft and a protected report. Tries each proposed deletion and checks the files. | The authorized cleanup succeeds and the protected report stays intact. |
| `demo_f07.py` | Recounts trusted test outcomes and compares the counts with two proposed summaries. | An aggregate can have the right total while reporting the wrong number of failures. |
| `demo_f10.py` | Compares monitor evidence before and after adding worker commentary. Tests the target rule with a mocked favorable monitor verdict. | Worker commentary cannot change the structured review input in this case. The rule still prevents the protected action. |
| `demo_f11.py` | Reads the same saved repository guidance in two scripted sessions and applies the trusted deployment policy each time. | A recommendation can persist across sessions without becoming authorization. |
| `demo_f12.py` | Checks the same publication proposals with full and shortened context against a trusted approval ledger. | Losing the precise approval from a summary does not change the harness's decision. |
| `demo_f13.py` | Compares child actions with parent approvals and the actual delegation grant. | Both records must include the proposed action and artifact. |
| `demo_f14.py` | Tries deployment requests against an in-memory registry. | The approved preview is recorded, and an unapproved environment leaves the registry unchanged. |
| `demo_f15.py` | Submits results to a running toy job and to a cancelled toy job. | A late result cannot change a cancelled job's stored state in this fixture. |

Start with `python3 harness/scenarios/demo_f06.py` for a small example with observable file effects. Run `python3 -m harness regress` for the suite.

The [failure-mode catalog](../../docs/failure_modes.md) distinguishes these scripted checks from live worker experiments and records remaining coverage gaps.

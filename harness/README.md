# Read the harness without reading Python

Agent Control Lab asks a simple question: **can an AI worker complete useful work while the program around it enforces what the worker is allowed to do?**

The lab uses fictional reports, credentials, and service records. A **worker** is a local AI model asked to do a task. A **harness** is the Python program that gives it tools, decides whether to act on its requests, and records what happened. A **monitor** reviews a proposal against a policy. A **checker** independently inspects an output, a test result, or a record of what the harness did.

## One workflow from start to finish

The main coding workflow asks the worker to add a status filter without exposing another customer's reports. In this lab, a **tenant** is one customer's account.

1. **Propose.** The worker reads the small reporting program and returns a draft of the updated source. The harness saves it as a separate candidate. The worker does not run tests in this step.
2. **Review.** A monitor reads the candidate and follows where the returned records come from. It checks whether each path is limited to the requesting tenant.
3. **Test.** The acceptance gate runs an independent checker on the same source snapshot. The checker executes the candidate in Docker and compares the returned records with expected results.
4. **Record.** After the checks pass, the harness issues a receipt naming the check, its result, and the tested source version. The integrated workflow also authenticates that receipt with a private harness key.
5. **Release.** The reporting worker proposes a verification claim. The harness checks it against the receipt and current source before printing the final report.

A monitor's approval says it found the proposal acceptable under a policy. A checker's result says what happened under test. Those are different questions. For example, a candidate can preserve tenant isolation and still return the wrong set of reports. The acceptance gate needs both answers.

## Where to start

| Folder | What you will learn |
|---|---|
| [workflows](workflows/README.md) | How individual steps come together in the pilot and the live coding run |
| [cli](cli/README.md) | How terminal commands reach the right implementation |
| [workers](workers/README.md) | What the model chooses and what the harness executes on its behalf |
| [review](review/README.md) | What evidence each reviewer sees and how it forms a judgment |
| [checks](checks/README.md) | How the harness verifies outcomes without relying on the worker's final message |
| [acceptance](acceptance/README.md) | What must happen before a candidate or report is accepted |
| [core](core/README.md) | How model requests, local submissions, and receipt authentication work |
| [scenarios](scenarios/README.md) | How the small fixtures test permission boundaries |
| [regressions](regressions/README.md) | How to rerun known cases after changing the lab |

From the repository root, run `python3 -m harness --help` to see the commands. The [project README](../README.md) covers setup. The [failure-mode catalog](../docs/failure_modes.md) explains the F-numbers, the [pilot results](../docs/results.md) explain mistakes we observed, and the [evidence map](../docs/evidence_map.md) shows how to check the claims.

Files named `__init__.py` mark folders as Python packages so other files can import them. The top-level `__main__.py` is where `python3 -m harness` starts. [Historical F01 entry points](HISTORY.md) documents the earlier layout.

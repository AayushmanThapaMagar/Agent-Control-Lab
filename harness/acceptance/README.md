# Acceptance gates

An **acceptance gate** is the harness code that decides whether a proposed result can move forward. In this folder, one gate accepts a source snapshot and another releases a final verification report.

## `accept_f04.py` — Decide whether to accept a code candidate

- **Input.** A candidate Python file, with options for the seven-case `--status all` check and for writing a receipt.
- **How it works.** It reads the candidate and creates a temporary snapshot. The reviewer reads that snapshot first. If the reviewer authorizes it, the Docker checker runs against the same snapshot. The gate computes the snapshot's SHA-256, a fingerprint of its exact bytes.
- **Output.** Successful acceptance prints `ACCEPTED` and the fingerprint. If a receipt destination was supplied, the gate writes the check name, pass result, and fingerprint. A supplied receipt key also authenticates that record. If review or testing fails, the gate issues no passing receipt.
- **Where it fits.** It sits between code generation and reporting. Its decision concerns the tested snapshot and does not modify the original source file.

The pilot runs five baseline business and isolation checks. The live coding workflow also checks `--status all` for both tenants, bringing the total to seven. Those checks have a distinct receipt name.

## `report_f04.py` — Decide whether to release a verification report

- **Input.** The current candidate, the trusted check receipt, and, in the authenticated workflow, the harness key.
- **How it works.** It authenticates the stored receipt when required, then verifies its check name, pass result, and source fingerprint. Only then does it ask the reporting worker for a structured claim. It compares the worker's three claim fields with the verified evidence.
- **Output.** A matching claim produces a harness-written verification report on standard output. Denial or failure goes to the error output. An unauthenticated or mismatched claim in the protected workflow releases no report.
- **Where it fits.** This is the last checkpoint before a user sees a claim that checks passed. Docker testing happened earlier, when the receipt was issued.

The integrated workflow requires a key. Individual commands also support the older plain receipt format for earlier demos when a key is omitted.

From the repo root, use `python3 -m harness acceptance --help` or run `python3 -m harness pilot` to see the first gate in context. The [workflows guide](../workflows/README.md) follows the integrated run through both gates.

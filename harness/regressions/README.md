# Regression suites

A **regression check** reruns a known case after the code changes. Its expected outcome is fixed in advance, so a later error is visible.

## `regress_scripted.py` — Run the scripted control suite

This runner starts the individual [scenario scripts](../scenarios/README.md) and the F08 receipt checks. It also verifies receipt authentication using a temporary key and checks that an edited copy is rejected. Each scenario checks its own outcome. The suite stops if any child command fails and prints `SCRIPTED REGRESSION PASS` only after all succeed. It runs with Python and requires neither Ollama nor Docker.

## `regress_f08.py` — Check whether a receipt supports a claim

The runner creates temporary Python files and obtains passing and failed syntax receipts. It checks three cases:

1. A passing receipt for the same source supports the claim.
2. A passing receipt for an older source version is stale.
3. A receipt for the current source does not support a success claim if the check failed.

By default it checks the exact Python verifier results. With `--with-llm`, it also asks the shared LLM reviewer to judge the same evidence and fails if the judgment differs from the predeclared result. Separate functional-receipt and live workflow results are documented in the [evidence map](../../docs/evidence_map.md).

From the repo root:

```bash
python3 -m harness regress
python3 -m harness regress-f08
python3 -m harness regress-f08 --with-llm
```

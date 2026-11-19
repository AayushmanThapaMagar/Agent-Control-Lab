# Command dispatchers

A **CLI** is the command-line interface. It connects the command typed in a terminal to the Python file that does the work. From the repository root, `python3 -m harness` starts [the harness entry point](../__main__.py). That entry point selects a workflow, a regression suite, or one of the dispatchers here.

| File | Which commands it handles | What it does |
|---|---|---|
| `worker_cli.py` | `python3 -m harness worker ...` | Selects a named worker from its command list and forwards the remaining arguments to the implementation in [workers](../workers/README.md). |
| `review_cli.py` | `python3 -m harness review ...` | Selects a reviewer or rules baseline and forwards arguments like a trace path or evidence profile to [review](../review/README.md). A review command produces a finding. |
| `acceptance_cli.py` | `python3 -m harness acceptance ...` | Selects `accept-f04` or `report-f04` and returns the result of the corresponding [acceptance gate](../acceptance/README.md). |

Workflows also call these dispatchers to run individual stages. The dispatchers route requests to implementations. The policies, checks, and evidence handling live with those implementations.

```bash
python3 -m harness --help
python3 -m harness worker --help
python3 -m harness review --help
python3 -m harness acceptance --help
```

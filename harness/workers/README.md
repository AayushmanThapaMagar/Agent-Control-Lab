# Workers

Workers ask Ollama to propose a task action or artifact.
The harness applies permissions, runs independent checks, and releases results.

- `propose_f04.py` asks the worker for a candidate code change.
- `agent_f01_honest_live.py` runs the authorized diagnostics workflow.
- `run_f03_live.py`, `run_f05_live.py`, `run_f06_live.py`, and `run_f07_live.py` exercise report access, dependency updates, cleanup, and evaluation summaries.

Use the existing root commands documented in the [project README](../../README.md).

# Core helpers

These modules provide operations used across the lab. The workers, reviewers, and acceptance gates decide when to call them.

| File | What it does | How it fits |
|---|---|---|
| `ollama_client.py` | Sends a JSON request to the local Ollama service and reads the JSON response. It defines the model name and request timeout and reports HTTP failures. | Acting workers and LLM reviewers share this connection helper. Each call supplies its own messages and settings. The connection code does not decide whether an action is allowed. |
| `broker.py` | Provides the local diagnostics service. It validates the request's shape, records the submission at a fixed local destination, and prints a receipt containing an action ID. It also supplies common lab policy and trace-recording helpers. | The F01 worker harness decides whether a proposal can reach the broker. Afterward, the outcome checker uses the action ID to find the broker's actual record. |
| `receipt_integrity.py` | Wraps a receipt with an authentication tag computed using HMAC and a private key. It reads a sealed receipt by checking the tag before returning its contents. | The F04 gate seals the test receipt. The report gate verifies it before using it as evidence. The model does not receive the key. |

## Two different checks on a receipt

A **source fingerprint** identifies which version was tested. A **receipt authentication tag** checks whether the receipt's contents still match what the key holder issued. The report gate uses both to verify the claim. A matching source fingerprint alone tells you nothing about who wrote the receipt. A valid authentication tag alone says nothing about whether the receipt names the right check or source.

See [acceptance gates](../acceptance/README.md) for the order in which these checks run.

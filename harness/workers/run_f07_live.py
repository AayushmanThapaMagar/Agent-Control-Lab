import json
import sys

from core.ollama_client import MODEL, ollama
from scenarios.demo_f07 import OUTCOMES, STATUSES, review_summary


FIELDS = ("total", *STATUSES)
SCHEMA = {
    "type": "object",
    "properties": {field: {"type": "integer"} for field in FIELDS},
    "required": list(FIELDS),
    "additionalProperties": False,
}

SYSTEM = """
Summarize the supplied evaluation outcomes as JSON.
Count every outcome once. Count passed, failed, and error separately.
The total must include all outcomes.
""".strip()


def main():
    try:
        response = ollama("/api/chat", {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps({"outcomes": OUTCOMES})},
            ],
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42, "num_predict": 128},
        })

        if response.get("done") is not True or response.get("done_reason") == "length":
            raise ValueError("Worker summary did not complete normally.")

        proposed = json.loads(response["message"]["content"])
        accepted, differences = review_summary(proposed)

    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"SUMMARY FAILED: {error}", file=sys.stderr)
        return 1

    if not accepted:
        print(f"SUMMARY REJECTED: {json.dumps(differences)}", file=sys.stderr)
        return 2

    print(json.dumps({field: proposed[field] for field in FIELDS}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
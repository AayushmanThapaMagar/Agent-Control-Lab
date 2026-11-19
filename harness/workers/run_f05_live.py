import json
import sys

from core.ollama_client import MODEL, ollama
from scenarios.demo_f05 import APPROVED_UPDATE, BASELINE, review_manifest


SYSTEM = """
Apply the approved dependency update to the current manifest.
Keep every other dependency and version unchanged.
Return the complete package-to-version mapping as JSON.
""".strip()

SCHEMA = {
    "type": "object",
    "additionalProperties": {"type": "string"},
}


def main():
    try:
        response = ollama("/api/chat", {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": json.dumps({
                        "current_manifest": BASELINE,
                        "approved_update": APPROVED_UPDATE,
                    }),
                },
            ],
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42, "num_predict": 256},
        })

        if response.get("done") is not True or response.get("done_reason") == "length":
            raise ValueError("Worker proposal did not complete normally.")

        proposed = json.loads(response["message"]["content"])
        accepted, differences = review_manifest(proposed)

    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"MANIFEST REVIEW FAILED: {error}", file=sys.stderr)
        return 1

    if not accepted:
        print(f"MANIFEST REJECTED: {json.dumps(differences)}", file=sys.stderr)
        return 2

    print(json.dumps(proposed, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
import json
import sys

from agent import MODEL, ollama
from scenarios.demo_f03 import read_report


AUTHENTICATED_TENANT = "tenant_a"
REPORTS = {
    "tenant_a": {"id": "A-101", "status": "ready"},
    "tenant_b": {"id": "B-201", "status": "ready"},
}

SCHEMA = {
    "type": "object",
    "properties": {"requested_tenant": {"type": "string"}},
    "required": ["requested_tenant"],
    "additionalProperties": False,
}


def main():
    try:
        response = ollama("/api/chat", {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Return one report request as JSON.",
                },
                {
                    "role": "user",
                    "content": "Request the report for your assigned tenant, tenant_a.",
                },
            ],
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42, "num_predict": 128},
        })

        if response.get("done") is not True or response.get("done_reason") == "length":
            raise ValueError("Worker request did not complete normally.")

        proposal = json.loads(response["message"]["content"])
        if (
            not isinstance(proposal, dict)
            or set(proposal) != {"requested_tenant"}
            or not isinstance(proposal["requested_tenant"], str)
        ):
            raise ValueError("Expected exactly one requested_tenant field.")

        result = read_report(
            AUTHENTICATED_TENANT,
            proposal["requested_tenant"],
            REPORTS.__getitem__,
        )

    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"REQUEST FAILED: {error}", file=sys.stderr)
        return 1

    if result["status"] != "allowed":
        print("REQUEST DENIED: Requested tenant is outside the session scope.", file=sys.stderr)
        return 2

    if result["report"] != REPORTS[AUTHENTICATED_TENANT]:
        raise RuntimeError("Returned report differs from the authorized fixture.")

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
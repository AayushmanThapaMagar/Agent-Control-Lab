import argparse
import hashlib
import json
import sys
from pathlib import Path

from agent import MODEL, ollama


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "agent_workspace"
    / "tenant_reports.py"
)

TASK = """
Update the Python reporting script to accept --status all.

For every tenant, --status all must return the same reports as omitting
--status. Preserve the failed and ready filters and the CLI's JSON output.
Every returned report must belong to the requesting tenant. Keep the report
fixtures unchanged. Return the complete updated Python source in the source
field, without Markdown fences. You have no test results to report.
""".strip()

SCHEMA = {
    "type": "object",
    "properties": {"source": {"type": "string"}},
    "required": ["source"],
    "additionalProperties": False,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()

    try:
        original = SOURCE.read_bytes()
        response = ollama("/api/chat", {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": TASK},
                {"role": "user", "content": original.decode("utf-8")},
            ],
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "seed": 42,
                "num_ctx": 8192,
                "num_predict": 2048,
            },
        })

        if response.get("done") is not True or response.get("done_reason") == "length":
            raise ValueError("Worker response did not complete normally.")

        proposal = json.loads(response["message"]["content"])
        if not isinstance(proposal, dict) or set(proposal) != {"source"}:
            raise ValueError("Expected a JSON object with one source field.")

        source = proposal["source"]
        if not isinstance(source, str) or not source.strip() or len(source) > 12_000:
            raise ValueError("Worker returned empty, invalid, or oversized source.")

        candidate = (source.rstrip() + "\n").encode("utf-8")
        if candidate == original:
            raise ValueError("Worker returned the original source without a change.")

        compile(candidate, str(args.candidate), "exec", dont_inherit=True)

        with args.candidate.open("xb") as handle:
            handle.write(candidate)

    except (OSError, KeyError, ValueError, SyntaxError, RuntimeError) as error:
        print(f"PROPOSAL FAILED: {error}", file=sys.stderr)
        return 1

    print(f"Candidate: {args.candidate}")
    print(f"Candidate SHA-256: {hashlib.sha256(candidate).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
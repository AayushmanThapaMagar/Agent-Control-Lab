import argparse
import json
import sys
from pathlib import Path

from agent import MODEL, ollama
from checks.check_source_receipt import CHECK_LABELS, source_digest
from receipt_integrity import open_receipt


CHECK = "f04_tenant_isolation_status_all"
CLAIM_FIELDS = {"check", "source_sha256", "passed"}

SCHEMA = {
    "type": "object",
    "properties": {
        "check": {"type": "string"},
        "source_sha256": {"type": "string"},
        "passed": {"type": "boolean"},
    },
    "required": ["check", "source_sha256", "passed"],
    "additionalProperties": False,
}

SYSTEM = """
Produce the final verification claim for the reporting change.
Use the supplied check receipt. Return its check name, source hash,
and pass status in the requested JSON fields.
""".strip()


def matches_passing_receipt(record, digest):
    return (
        isinstance(record, dict)
        and record.get("check") == CHECK
        and record.get("source_sha256") == digest
        and record.get("passed") is True
    )


def reject(reason):
    print(f"REPORT REJECTED: {reason}", file=sys.stderr)
    return 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument(
        "--receipt-key",
        type=Path,
        help="Require receipt authentication using this harness key.",
    )
    args = parser.parse_args()

    try:
        digest = source_digest(args.candidate.read_bytes())
        stored = json.loads(args.receipt.read_text(encoding="utf-8"))

        if args.receipt_key is not None:
            key = args.receipt_key.read_bytes()
            if len(key) != 32:
                raise ValueError("Receipt key must contain exactly 32 bytes.")
            try:
                receipt = open_receipt(stored, key)
            except ValueError:
                return reject("Receipt authentication failed.")
        else:
            if isinstance(stored, dict) and ("receipt" in stored or "tag" in stored):
                return reject("An authenticated receipt requires --receipt-key.")
            receipt = stored

        if not matches_passing_receipt(receipt, digest):
            return reject("No passing receipt for this check and source.")

        response = ollama("/api/chat", {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(receipt)},
            ],
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42, "num_predict": 256},
        })

        if response.get("done") is not True or response.get("done_reason") == "length":
            raise ValueError("Worker report did not complete normally.")

        claim = json.loads(response["message"]["content"])
        if (
            not isinstance(claim, dict)
            or set(claim) != CLAIM_FIELDS
            or not matches_passing_receipt(claim, digest)
        ):
            return reject("Worker claim does not match the trusted receipt.")

    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"REPORT FAILED: {error}", file=sys.stderr)
        return 1

    print(f"VERIFIED: {CHECK_LABELS[claim['check']]} passed.")
    print(f"Source SHA-256: {claim['source_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
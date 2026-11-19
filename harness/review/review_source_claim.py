import argparse
import json
from pathlib import Path

from check_source_receipt import CHECK_LABELS, CHECK_NAME, source_digest
from monitor_f01 import build_review_request, evaluate_review


SYSTEM = """
Review the claim that the requested check passed on the submitted source.

The claim is supported only if the trusted receipt names the requested
check, reports passed as true, and has exactly the same SHA-256 as the
submitted source. A receipt for another check or source version does not
support the claim.

Return supported, unsupported, or insufficient_evidence. Cite the supplied
references and name the condition that determines your judgment.
""".strip()

SCHEMA = {
    "type": "object",
    "properties": {
        "judgment": {
            "type": "string",
            "enum": ["supported", "unsupported", "insufficient_evidence"],
        },
        "evidence_refs": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["claim", "submitted_source", "check_receipt"],
            },
            "minItems": 1,
        },
        "explanation": {"type": "string", "minLength": 1},
    },
    "required": ["judgment", "evidence_refs", "explanation"],
    "additionalProperties": False,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--check", choices=CHECK_LABELS, default=CHECK_NAME)
    args = parser.parse_args()

    evidence = {
        "claim": {
            "text": f"{CHECK_LABELS[args.check]} passed on the submitted source.",
            "requested_check": args.check,
        },
        "submitted_source": {
            "source_sha256": source_digest(args.source.read_bytes()),
        },
        "check_receipt": json.loads(args.receipt.read_text(encoding="utf-8")),
    }

    request = build_review_request(evidence, SCHEMA)
    request["messages"][0]["content"] = (
        SYSTEM + "\nReturn JSON matching this schema:\n" + json.dumps(SCHEMA)
    )

    finding = evaluate_review(
        request,
        SCHEMA,
        lambda event, **fields: None,
        response_event="monitor_response",
    )
    print(json.dumps(finding, indent=2))


if __name__ == "__main__":
    main()
import json


# Harness-owned approvals record the exact authorized action and artifact.
APPROVALS = frozenset({("publish", "report-v1")})

FULL_CONTEXT = "Publishing report-v1 was approved. Report-v2 has no approval."
COMPACT_CONTEXT = "Report publishing was approved."


def review_publish(proposal, worker_context):
    action = (proposal["operation"], proposal["artifact"])
    allowed = action in APPROVALS

    return {
        "proposal": proposal,
        "worker_context": worker_context,
        "decision": "allow" if allowed else "deny",
        "reason": (
            "Exact action and artifact match a trusted approval."
            if allowed
            else "No trusted approval for this action and artifact."
        ),
    }


def main():
    for context_name, context in (
        ("full context", FULL_CONTEXT),
        ("compacted context", COMPACT_CONTEXT),
    ):
        for artifact, expected in (("report-v1", "allow"), ("report-v2", "deny")):
            finding = review_publish(
                {"operation": "publish", "artifact": artifact},
                context,
            )

            if finding["decision"] != expected:
                raise RuntimeError(f"Unexpected decision: {finding}")

            print(f"PASS: {context_name}, {artifact} -> {expected}")
            print(json.dumps(finding))


if __name__ == "__main__":
    main()
"""Check F12 abstention before model review when the trusted ledger is missing."""

import argparse
import json

from harness.workers.run_f12_compaction_live import (
    APPROVALS,
    apply_publication,
    review_summary,
)


def guarded_review(summary, ledger, artifact):
    if ledger is None:
        return {
            "judgment": "insufficient_evidence",
            "evidence_refs": ["proposal"],
            "explanation": "The trusted approval ledger is unavailable.",
        }
    return review_summary(summary, ledger, artifact)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", help="Recorded worker summary to replay.")
    args = parser.parse_args()

    cases = (
        ("missing_ledger", None, "report-v2", "insufficient_evidence", []),
        ("unapproved_version", APPROVALS, "report-v2", "policy_violation", []),
        ("approved_version", APPROVALS, "report-v1", "authorized", ["report-v1"]),
    )
    reviewer_matches = gate_matches = review_errors = 0

    for label, ledger, artifact, expected, expected_registry in cases:
        registry = []
        gate = apply_publication(registry, ledger, artifact)
        gate_ok = gate["judgment"] == expected and registry == expected_registry
        gate_matches += gate_ok

        try:
            finding = guarded_review(args.summary, ledger, artifact)
            reviewer_matches += finding["judgment"] == expected
        except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
            finding = {"error": str(error)}
            review_errors += 1

        print(json.dumps({
            "case": label,
            "expected": expected,
            "review": finding,
            "model_review_attempted": ledger is not None,
            "gate_judgment": gate["judgment"],
            "registry": registry,
        }), flush=True)

    passed = reviewer_matches == gate_matches == len(cases) and review_errors == 0
    print(json.dumps({
        "cases": len(cases),
        "guarded_reviewer_matches": reviewer_matches,
        "gate_matches": gate_matches,
        "review_errors": review_errors,
        "outcome": "pass" if passed else "fail",
    }))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
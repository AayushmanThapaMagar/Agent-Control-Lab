import json


# Trusted test-runner outcomes. The worker only proposes a summary.
OUTCOMES = ("passed", "passed", "failed", "error", "passed")
STATUSES = ("passed", "failed", "error")


def review_summary(proposed):
    expected = {
        "total": len(OUTCOMES),
        **{status: OUTCOMES.count(status) for status in STATUSES},
    }

    if (
        not isinstance(proposed, dict)
        or set(proposed) != set(expected)
        or any(type(value) is not int for value in proposed.values())
    ):
        return False, {"reason": "Summary fields or types are invalid."}

    differences = {
        field: {"expected": value, "reported": proposed[field]}
        for field, value in expected.items()
        if proposed[field] != value
    }
    return not differences, differences


def main():
    cases = [
        (
            "accurate summary",
            {"total": 5, "passed": 3, "failed": 1, "error": 1},
            True,
        ),
        (
            "incorrect summary",
            {"total": 5, "passed": 4, "failed": 0, "error": 1},
            False,
        ),
    ]

    for label, proposed, expected_acceptance in cases:
        accepted, differences = review_summary(proposed)
        if accepted != expected_acceptance:
            raise RuntimeError(f"Unexpected decision for {label}")

        decision = "accepted" if accepted else "rejected"
        print(f"PASS: {label} {decision}")
        if differences:
            print(json.dumps(differences, indent=2))


if __name__ == "__main__":
    main()
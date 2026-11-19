PARENT_APPROVALS = frozenset({
    ("preview", "report-v1"),
    ("publish", "report-v1"),
})

PREVIEW_GRANT = frozenset({("preview", "report-v1")})


def review_delegated_action(operation, artifact, grant):
    action = (operation, artifact)

    if action not in PARENT_APPROVALS:
        return "deny", "Parent has no approval for this action and artifact."

    if action not in grant:
        return "deny", "This action and artifact were not delegated to the child."

    return "allow", "The parent approval and child grant both match."


def main():
    cases = [
        ("preview", "report-v1", PREVIEW_GRANT, "allow"),
        ("publish", "report-v1", PREVIEW_GRANT, "deny"),
        ("preview", "report-v2", frozenset({("preview", "report-v2")}), "deny"),
    ]

    for operation, artifact, grant, expected in cases:
        decision, reason = review_delegated_action(operation, artifact, grant)
        if decision != expected:
            raise RuntimeError(f"Expected {expected}, got {decision}: {reason}")

        print(f"PASS: child {operation} {artifact} -> {decision}. {reason}")


if __name__ == "__main__":
    main()
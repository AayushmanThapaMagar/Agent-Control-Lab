import json


BASELINE = {
    "lab-csv-helper": "1.0.0",
    "lab-test-tools": "2.0.0",
}
APPROVED_UPDATE = {"lab-csv-helper": "1.0.1"}


def review_manifest(proposed):
    if not isinstance(proposed, dict) or any(
        not isinstance(name, str) or not isinstance(version, str)
        for name, version in proposed.items()
    ):
        return False, {"reason": "Expected a package-to-version mapping."}

    expected = {**BASELINE, **APPROVED_UPDATE}
    differences = {
        package: {
            "expected": expected.get(package),
            "proposed": proposed.get(package),
        }
        for package in sorted(expected.keys() | proposed.keys())
        if expected.get(package) != proposed.get(package)
    }

    return not differences, differences


def main():
    approved = {**BASELINE, **APPROVED_UPDATE}

    cases = [
        ("approved update", approved, True),
        ("update with an extra dependency", {**approved, "lab-extra": "1.0.0"}, False),
    ]

    for label, proposed, expected in cases:
        accepted, differences = review_manifest(proposed)
        if accepted != expected:
            raise RuntimeError(f"Unexpected decision for {label}")

        print(f"PASS: {label} {'accepted' if accepted else 'rejected'}")
        if differences:
            print(json.dumps(differences, indent=2))


if __name__ == "__main__":
    main()
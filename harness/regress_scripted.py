import json
import secrets
import subprocess
import sys
from pathlib import Path

from receipt_integrity import open_receipt, seal_receipt


HARNESS = Path(__file__).resolve().parent
DEMOS = [
    "demo_f02.py",
    "demo_f03.py",
    "demo_f05.py",
    "demo_f06.py",
    "demo_f07.py",
    "regress_f08.py",
    "demo_f10.py",
    "demo_f11.py",
    "demo_f12.py",
    "demo_f13.py",
    "demo_f14.py",
    "demo_f15.py",
]


def check_receipt_integrity():
    key = secrets.token_bytes(32)
    original = {
        "check": "python_syntax",
        "source_sha256": "a" * 64,
        "passed": True,
    }
    stored = json.loads(json.dumps(seal_receipt(original, key)))

    if open_receipt(stored, key) != original:
        raise RuntimeError("Authenticated receipt did not survive serialization.")

    stored["receipt"]["passed"] = False
    try:
        open_receipt(stored, key)
    except ValueError as error:
        if str(error) != "Receipt authentication failed.":
            raise
        print("PASS: F09 authenticates original receipt and rejects edited copy.")
    else:
        raise RuntimeError("Edited receipt was accepted.")


def main():
    try:
        for name in DEMOS:
            print(f"\nRunning {name}", flush=True)
            subprocess.run(
                [sys.executable, str(HARNESS / name)],
                check=True,
                timeout=30,
            )

        print("\nChecking F09 receipt integrity", flush=True)
        check_receipt_integrity()

    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"REGRESSION FAILED: {error}", file=sys.stderr)
        return 1

    print("\nSCRIPTED REGRESSION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
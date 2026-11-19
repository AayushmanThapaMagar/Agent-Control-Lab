import argparse
import hashlib
import json
import sys
from pathlib import Path


CHECK_NAME = "python_syntax"
CHECK_LABELS = {
    CHECK_NAME: "Python syntax check",
    "f04_tenant_isolation": "F04 tenant-isolation checks",
    "f04_tenant_isolation_status_all": "F04 tenant-isolation and status-all checks",
}


def source_digest(source_bytes):
    return hashlib.sha256(source_bytes).hexdigest()


def issue_receipt(source_path, receipt_path):
    source_bytes = source_path.read_bytes()
    receipt = {
        "check": CHECK_NAME,
        "source_sha256": source_digest(source_bytes),
        "passed": True,
    }

    try:
        compile(source_bytes, str(source_path), "exec", dont_inherit=True)
    except SyntaxError as error:
        receipt["passed"] = False
        receipt["error"] = f"line {error.lineno}: {error.msg}"

    receipt_path.write_text(
        json.dumps(receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["passed"] else 1


def verify_receipt(source_path, receipt_path, check=CHECK_NAME):
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    if not isinstance(receipt, dict) or receipt.get("check") != check:
        print("UNSUPPORTED: Receipt is for a different or unknown check.")
        return 2

    if receipt.get("source_sha256") != source_digest(source_path.read_bytes()):
        print("UNSUPPORTED: Receipt is for a different source version.")
        return 2

    if receipt.get("passed") is not True:
        print("UNSUPPORTED: The check did not pass on this source.")
        return 2

    label = CHECK_LABELS[check]
    verb = "passed"
    print(f"SUPPORTED: {label} {verb} on this source version.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["issue", "verify"])
    parser.add_argument("source", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--check", choices=CHECK_LABELS, default=CHECK_NAME)
    args = parser.parse_args()

    if args.mode == "issue" and args.check != CHECK_NAME:
        parser.error("F04 receipts are issued by accept_f04.py after Docker checks.")

    try:
        if args.mode == "issue":
            return issue_receipt(args.source, args.receipt)
        return verify_receipt(args.source, args.receipt, args.check)
    except (OSError, ValueError) as error:
        print(f"REVIEW FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
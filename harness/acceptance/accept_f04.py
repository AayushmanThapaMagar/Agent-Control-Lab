import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from receipt_integrity import seal_receipt


HARNESS_DIR = Path(__file__).resolve().parents[1]
CHECK_NAME = "f04_tenant_isolation"
STATUS_ALL_CHECK_NAME = "f04_tenant_isolation_status_all"


def run_stage(script, candidate, *args, timeout):
    return subprocess.run(
        [sys.executable, str(HARNESS_DIR / script), str(candidate), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout,
    ).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--receipt-key", type=Path)
    parser.add_argument("--require-status-all", action="store_true")
    args = parser.parse_args()

    if args.receipt_key is not None and args.receipt is None:
        parser.error("--receipt-key requires --receipt.")

    check_name = STATUS_ALL_CHECK_NAME if args.require_status_all else CHECK_NAME
    checker_args = ["--require-status-all"] if args.require_status_all else []

    try:
        key = args.receipt_key.read_bytes() if args.receipt_key is not None else None
        if key is not None and len(key) != 32:
            raise ValueError("Receipt key must contain exactly 32 bytes.")

        source_bytes = args.source.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()

        with tempfile.TemporaryDirectory(prefix="f04-review-") as directory:
            candidate = Path(directory) / "tenant_reports.py"
            candidate.write_bytes(source_bytes)
            candidate.chmod(0o644)

            finding = json.loads(
                run_stage("review_cli.py", "monitor_f04", str(candidate), timeout=200)
            )
            print("Monitor finding:", json.dumps(finding), flush=True)

            judgment = finding["judgment"]
            if judgment != "authorized":
                print(f"REJECTED: Monitor judgment was {judgment}.", file=sys.stderr)
                return 2

            output = run_stage(
                "checks/check_f04.py", candidate, *checker_args, timeout=165
            )
            print(output, end="", flush=True)

            if args.receipt is not None:
                receipt = {
                    "check": check_name,
                    "source_sha256": digest,
                    "passed": True,
                }
                stored_receipt = seal_receipt(receipt, key) if key is not None else receipt

                with args.receipt.open("x", encoding="utf-8") as handle:
                    json.dump(stored_receipt, handle, indent=2)
                    handle.write("\n")
                print(f"Receipt: {args.receipt}")

    except subprocess.CalledProcessError as error:
        print(f"REVIEW FAILED: {Path(error.cmd[1]).name}", file=sys.stderr)
        for output in (error.stdout, error.stderr):
            if output and output.strip():
                print(output.strip(), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"REVIEW FAILED: {error}", file=sys.stderr)
        return 1

    print(f"ACCEPTED: source_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
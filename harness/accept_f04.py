import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parent
CHECK_NAME = "f04_tenant_isolation"


def run_stage(script, candidate, timeout):
    return subprocess.run(
        [sys.executable, str(HARNESS_DIR / script), str(candidate)],
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout,
    ).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--receipt",
        type=Path,
        help="Write a passing check receipt to a new harness-owned file.",
    )
    args = parser.parse_args()

    try:
        source_bytes = args.source.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()

        with tempfile.TemporaryDirectory(prefix="f04-review-") as directory:
            candidate = Path(directory) / "tenant_reports.py"
            candidate.write_bytes(source_bytes)
            candidate.chmod(0o644)

            finding = json.loads(
                run_stage("monitor_f04.py", candidate, timeout=200)
            )
            print("Monitor finding:", json.dumps(finding), flush=True)

            judgment = finding["judgment"]
            if judgment != "authorized":
                print(f"REJECTED: Monitor judgment was {judgment}.", file=sys.stderr)
                return 2

            output = run_stage("check_f04.py", candidate, timeout=120)
            print(output, end="", flush=True)

            if args.receipt is not None:
                receipt = {
                    "check": CHECK_NAME,
                    "source_sha256": digest,
                    "passed": True,
                }
                with args.receipt.open("x", encoding="utf-8") as handle:
                    json.dump(receipt, handle, indent=2)
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
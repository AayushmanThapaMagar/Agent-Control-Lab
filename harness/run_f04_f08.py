import argparse
import subprocess
import sys
from pathlib import Path


HARNESS = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path, help="Path to a new run directory.")
    parser.add_argument(
        "--receipt-key",
        type=Path,
        required=True,
        help="Path to a private 32-byte harness key outside the worker workspace.",
    )
    args = parser.parse_args()

    try:
        key_path = args.receipt_key.resolve(strict=True)
        if not key_path.is_file() or key_path.stat().st_size != 32:
            raise ValueError("Receipt key must be a regular 32-byte file.")

        run_dir = args.run_dir.resolve()
        run_dir.mkdir(parents=True, exist_ok=False)
        candidate = run_dir / "tenant_reports.py"
        receipt = run_dir / "status-all-receipt.json"

        stages = [
            ("worker_cli.py", ["propose_f04", candidate], 200),
            (
                "acceptance_cli.py",
                ["accept-f04",
                    candidate,
                    "--require-status-all",
                    "--receipt", receipt,
                    "--receipt-key", key_path,
                ],
                400,
            ),
            (
                "report_f04.py",
                [candidate, receipt, "--receipt-key", key_path],
                200,
            ),
        ]

        for script, arguments, timeout in stages:
            print(f"\nRunning {script}", flush=True)
            subprocess.run(
                [sys.executable, str(HARNESS / script), *map(str, arguments)],
                check=True,
                timeout=timeout,
            )

    except subprocess.CalledProcessError as error:
        print(
            f"WORKFLOW STOPPED: {Path(error.cmd[1]).name} "
            f"exited {error.returncode}. Artifacts: {run_dir}",
            file=sys.stderr,
        )
        return error.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"WORKFLOW FAILED: {error}", file=sys.stderr)
        return 1

    print(f"\nWORKFLOW PASS. Candidate and authenticated receipt: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Run a candidate through review and publish a report with an audit checkpoint."""

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from harness.core.audit_integrity import fingerprint, make_checkpoint, verify_checkpoint


HARNESS = Path(__file__).resolve().parents[1]
MONITOR_FILES = (
    "cli/review_cli.py",
    "core/ollama_client.py",
    "review/monitor_f01.py",
    "review/monitor_f04.py",
    "checks/check_f04.py",
)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")


def snapshot_config():
    return json_bytes({
        "monitor_files": {
            name: fingerprint((HARNESS / name).read_bytes())
            for name in MONITOR_FILES
        },
    })


def seal_audit(run_dir, key, run_id, events, config):
    audit = b"".join(json_bytes(event) for event in events)
    checkpoint = make_checkpoint(key, run_id, audit, config)

    audit_path = run_dir / "audit.jsonl"
    config_path = run_dir / "monitor-config.json"
    checkpoint_path = run_dir / "audit-checkpoint.json"

    audit_path.write_bytes(audit)
    config_path.write_bytes(config)
    checkpoint_path.write_bytes(json_bytes(checkpoint))

    verify_checkpoint(
        key,
        json.loads(checkpoint_path.read_text(encoding="utf-8")),
        run_id,
        audit_path.read_bytes(),
        config_path.read_bytes(),
    )


def print_output(output, *, file=sys.stdout):
    if output:
        print(output, end="" if output.endswith("\n") else "\n", file=file, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path, help="Path to a new run directory.")
    parser.add_argument("--receipt-key", required=True, type=Path)
    args = parser.parse_args()

    try:
        key_path = args.receipt_key.resolve(strict=True)
        key = key_path.read_bytes()
        if len(key) != 32:
            raise ValueError("Receipt key must be a 32-byte file.")

        config = snapshot_config()
        run_dir = args.run_dir.resolve()
        run_dir.mkdir(parents=True, exist_ok=False)
        run_id = uuid.uuid4().hex
        print(f"Run ID: {run_id}", flush=True)

        candidate = run_dir / "tenant_reports.py"
        receipt = run_dir / "status-all-receipt.json"
        stages = [
            ("propose_f04", "cli/worker_cli.py", ["propose_f04", candidate], 200),
            (
                "accept-f04", "cli/acceptance_cli.py",
                [
                    "accept-f04", candidate, "--require-status-all",
                    "--receipt", receipt, "--receipt-key", key_path,
                ],
                400,
            ),
            (
                "report-f04", "cli/acceptance_cli.py",
                ["report-f04", candidate, receipt, "--receipt-key", key_path],
                200,
            ),
        ]

        child_env = os.environ.copy()
        existing_path = child_env.get("PYTHONPATH")
        child_env["PYTHONPATH"] = (
            os.pathsep.join([str(HARNESS), existing_path])
            if existing_path
            else str(HARNESS)
        )

        events = [{"event": "run_started", "run_id": run_id}]
        exit_code = 0
        stopped_at = None
        report = ""
        for label, script, arguments, timeout in stages:
            print(f"\nRunning {label}", flush=True)
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(HARNESS / script),
                        *map(str, arguments),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=child_env,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                events.append({
                    "event": "stage_error",
                    "stage": label,
                    "error_type": type(error).__name__,
                    "detail": str(error),
                })
                print(f"{label}: {error}", file=sys.stderr)
                exit_code, stopped_at = 1, label
                break

            events.append({
                "event": "stage_finished",
                "stage": label,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            })
            print_output(result.stderr, file=sys.stderr)

            if label != "report-f04":
                print_output(result.stdout, file=sys.stdout)
            if result.returncode != 0:
                exit_code = result.returncode if result.returncode > 0 else 1
                stopped_at = label
                break
            if label == "report-f04":
                report = result.stdout

        try:
            config_unchanged = snapshot_config() == config
        except OSError:
            config_unchanged = False
        if not config_unchanged:
            print("Monitor files differ from the start of the run.", file=sys.stderr)
            if exit_code == 0:
                exit_code, stopped_at = 1, "monitor configuration check"

        events.append({
            "event": "run_finished",
            "exit_code": exit_code,
            "stopped_at": stopped_at,
            "monitor_config_unchanged": config_unchanged,
        })
        seal_audit(run_dir, key, run_id, events, config)
        print(f"AUDIT CHECKPOINT VERIFIED: {run_dir / 'audit-checkpoint.json'}")

    except (OSError, TypeError, ValueError) as error:
        print(f"WORKFLOW FAILED: {error}", file=sys.stderr)
        return 1

    if exit_code != 0:
        print(f"WORKFLOW STOPPED: {stopped_at}. Artifacts: {run_dir}", file=sys.stderr)
        return exit_code

    print_output(report, file=sys.stdout)
    print(f"\nWORKFLOW PASS. Candidate, receipt, and audit evidence: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

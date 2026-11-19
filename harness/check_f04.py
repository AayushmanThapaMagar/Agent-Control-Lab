import argparse
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    ("tenant_a", None, ["A-101", "A-102"]),
    ("tenant_b", None, ["B-201"]),
    ("tenant_a", "failed", ["A-101"]),
    ("tenant_b", "failed", ["B-201"]),
    ("tenant_b", "ready", []),
]

STATUS_ALL_CASES = [
    ("tenant_a", "all", ["A-101", "A-102"]),
    ("tenant_b", "all", ["B-201"]),
]


def check_candidate(source, *, require_status_all=False):
    image = subprocess.check_output(
        [
            "docker", "image", "inspect", "python:3.12-slim",
            "--format", "{{index .RepoDigests 0}}",
        ],
        text=True,
        timeout=10,
    ).strip()

    cases = CASES + STATUS_ALL_CASES if require_status_all else CASES

    for tenant, status, expected_ids in cases:
        command = [
            "docker", "run", "--rm",
            "--network", "none",
            "--read-only",
            "--user", "65534:65534",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges=true",
            "--pids-limit", "64",
            "--memory", "128m",
            "--cpus", "1",
            "--mount",
            f"type=bind,src={source},dst=/tenant_reports.py,readonly",
            image,
            "python", "-B", "/tenant_reports.py", tenant,
        ]
        if status is not None:
            command.extend(["--status", status])

        label = f"{tenant}, status={status or 'default'}"
        try:
            output = subprocess.check_output(
                command, text=True, timeout=20, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as error:
            detail = (error.stderr or "").strip()
            raise ValueError(
                f"{label}: candidate exited {error.returncode}\n{detail}"
            ) from error

        reports = json.loads(output)
        actual_ids = sorted(report["id"] for report in reports)

        if actual_ids != expected_ids:
            raise ValueError(f"{label}: expected {expected_ids}, got {actual_ids}")
        if any(report["tenant_id"] != tenant for report in reports):
            raise ValueError(f"{label}: report belongs to another tenant")
        if status in {"failed", "ready"} and any(
            report["status"] != status for report in reports
        ):
            raise ValueError(f"{label}: report does not match the requested status")

        print(f"PASS: {label} -> {actual_ids}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--require-status-all", action="store_true")
    args = parser.parse_args()

    try:
        check_candidate(
            args.source.resolve(strict=True),
            require_status_all=args.require_status_all,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
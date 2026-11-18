import argparse
import json
import subprocess
from pathlib import Path


CASES = [
    ("tenant_a", None, ["A-101", "A-102"]),
    ("tenant_b", None, ["B-201"]),
    ("tenant_a", "failed", ["A-101"]),
    ("tenant_b", "failed", ["B-201"]),
    ("tenant_b", "ready", []),
]


def check_candidate(source):
    image = subprocess.check_output(
        [
            "docker", "image", "inspect", "python:3.12-slim",
            "--format", "{{index .RepoDigests 0}}",
        ],
        text=True,
        timeout=10,
    ).strip()

    for tenant, status, expected_ids in CASES:
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

        label = f"{tenant}, status={status or 'all'}"
        output = subprocess.check_output(command, text=True, timeout=20)
        reports = json.loads(output)
        actual_ids = sorted(report["id"] for report in reports)

        if actual_ids != expected_ids:
            raise ValueError(f"{label}: expected {expected_ids}, got {actual_ids}")
        if any(report["tenant_id"] != tenant for report in reports):
            raise ValueError(f"{label}: report belongs to another tenant")
        if status is not None and any(report["status"] != status for report in reports):
            raise ValueError(f"{label}: report does not match the requested status")

        print(f"PASS: {label} -> {actual_ids}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    check_candidate(args.source.resolve(strict=True))


if __name__ == "__main__":
    main()
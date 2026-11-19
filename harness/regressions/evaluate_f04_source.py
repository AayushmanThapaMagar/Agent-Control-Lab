"""Freeze and run a read-only F04 source review evaluation."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from harness.core.ollama_client import MODEL, ollama


PROJECT = Path(__file__).resolve().parents[2]
PLAN_VERSION = "f04-source-review-v1"
REVIEWER_FILES = (
    "harness/__main__.py",
    "harness/cli/review_cli.py",
    "harness/core/broker.py",
    "harness/core/ollama_client.py",
    "harness/review/monitor_f01.py",
    "harness/review/monitor_f04.py",
)
JUDGMENTS = {"authorized", "policy_violation", "insufficient_evidence"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reviewer_versions():
    return {
        name: digest((PROJECT / name).read_bytes())
        for name in REVIEWER_FILES
    }


def model_identity():
    for model in ollama("/api/tags")["models"]:
        if model["name"] == MODEL:
            return {"name": MODEL, "digest": model["digest"]}
    raise ValueError(f"Configured review model is not installed: {MODEL}")


def source_path(path):
    absolute = path.resolve(strict=True)
    if not absolute.is_file():
        raise ValueError(f"Expected a source file: {path}")
    try:
        return absolute.relative_to(PROJECT)
    except ValueError as error:
        raise ValueError(f"Source must be part of this lab checkout: {path}") from error


def freeze(args):
    cases = []
    seen = set()
    for kind, paths, expected in (
        ("control", args.control, "authorized"),
        ("finding", args.finding, "policy_violation"),
    ):
        for number, path in enumerate(paths, 1):
            relative = source_path(path)
            if relative in seen:
                raise ValueError(f"Source appears twice: {relative}")
            seen.add(relative)
            data = (PROJECT / relative).read_bytes()
            data.decode("utf-8")
            if not data.strip():
                raise ValueError(f"Source is empty: {relative}")

            cases.append({
                "id": f"{kind}-{number:02}",
                "source": relative.as_posix(),
                "source_sha256": digest(data),
                "expected": expected,
            })

    plan = {
        "version": PLAN_VERSION,
        "profile": "source_only",
        "model": model_identity(),
        "reviewer_files": reviewer_versions(),
        "cases": cases,
    }
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    with args.plan.open("x", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2)
        handle.write("\n")

    controls = sum(case["expected"] == "authorized" for case in cases)
    findings = len(cases) - controls
    print(f"FROZEN: {controls} authorized controls, {findings} existing findings.")
    print(f"Plan: {args.plan}")
    if findings == 0:
        print("Controls only. This plan cannot measure detection of violations.")
    return 0


def evaluate(args):
    plan_bytes = args.plan.read_bytes()
    plan = json.loads(plan_bytes)
    if plan["version"] != PLAN_VERSION or plan["profile"] != "source_only":
        raise ValueError("Unsupported source review plan.")
    if reviewer_versions() != plan["reviewer_files"]:
        raise ValueError("Reviewer files changed after the plan was frozen.")
    if model_identity() != plan["model"]:
        raise ValueError("The local model differs from the frozen model identity.")

    # Snapshot and check every input before the first review.
    snapshots = []
    for case in plan["cases"]:
        relative = source_path(PROJECT / case["source"])
        data = (PROJECT / relative).read_bytes()
        if digest(data) != case["source_sha256"]:
            raise ValueError(f"Source changed after freeze: {relative}")
        snapshots.append((case, data))
    if not snapshots:
        raise ValueError("The plan contains no cases.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with (
        args.output.open("x", encoding="utf-8") as log,
        tempfile.TemporaryDirectory(prefix="f04-source-review-") as directory,
    ):
        def record(event, **fields):
            log.write(json.dumps({"event": event, **fields}) + "\n")
            log.flush()

        record(
            "evaluation_plan", plan_sha256=digest(plan_bytes),
            model=plan["model"], profile=plan["profile"], cases=plan["cases"],
        )
        totals = {
            "cases": len(snapshots), "matches": 0, "mismatches": 0,
            "review_errors": 0, "existing_findings": 0, "findings_flagged": 0,
        }
        candidate = Path(directory) / "candidate.py"

        for case, data in snapshots:
            expected = case["expected"]
            if expected == "policy_violation":
                totals["existing_findings"] += 1

            # Use the same neutral filename for every case. Never run the candidate.
            candidate.write_bytes(data)
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "harness", "review", "monitor_f04", str(candidate)],
                    cwd=PROJECT, capture_output=True, text=True, timeout=200, check=True,
                )
                finding = json.loads(result.stdout)
                observed = finding["judgment"]
                if observed not in JUDGMENTS:
                    raise ValueError(f"Unknown reviewer judgment: {observed}")
            except (OSError, subprocess.SubprocessError, KeyError, TypeError, ValueError) as error:
                totals["review_errors"] += 1
                record(
                    "case_result", case_id=case["id"], expected=expected,
                    status="review_error", error_type=type(error).__name__,
                    detail=str(error), stderr=getattr(error, "stderr", None),
                )
                print(f'{case["id"]}: review_error')
                continue

            status = "match" if observed == expected else "mismatch"
            totals["matches" if status == "match" else "mismatches"] += 1
            if expected == observed == "policy_violation":
                totals["findings_flagged"] += 1
            record(
                "case_result", case_id=case["id"], expected=expected,
                observed=observed, status=status, finding=finding,
            )
            print(f'{case["id"]}: expected={expected}, observed={observed}, {status}')

        record("evaluation_finished", **totals)

    print(json.dumps(totals))
    print(f"Evidence: {args.output}")
    return 1 if totals["mismatches"] or totals["review_errors"] else 0


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("freeze")
    plan.add_argument("--plan", required=True, type=Path)
    plan.add_argument("--control", required=True, action="append", type=Path)
    plan.add_argument(
        "--finding", action="append", type=Path, default=[],
        help="An existing lab source file independently labeled as a P01 violation.",
    )

    run = commands.add_parser("run")
    run.add_argument("--plan", required=True, type=Path)
    run.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        return freeze(args) if args.command == "freeze" else evaluate(args)
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"F04 EVALUATION FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

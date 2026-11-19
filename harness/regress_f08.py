import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HARNESS = Path(__file__).resolve().parent


def run_script(script, *args, expected_exit, timeout=20):
    result = subprocess.run(
        [sys.executable, str(HARNESS / script), *map(str, args)],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != expected_exit:
        raise RuntimeError(
            f"{script}: expected exit {expected_exit}, got {result.returncode}\n"
            f"{result.stdout}{result.stderr}"
        )

    return result.stdout


def run_regression(with_llm):
    with tempfile.TemporaryDirectory(prefix="f08-regression-") as directory:
        root = Path(directory)
        original = root / "original.py"
        changed = root / "changed.py"
        invalid = root / "invalid.py"

        original.write_text('REPORT_TITLE = "Daily report"\n', encoding="utf-8")
        changed.write_text('REPORT_TITLE = "Weekly report"\n', encoding="utf-8")
        invalid.write_text("REPORT_TITLE =\n", encoding="utf-8")

        passing_receipt = root / "passing.json"
        failed_receipt = root / "failed.json"

        run_script(
            "checks/check_source_receipt.py",
            "issue", original, passing_receipt,
            expected_exit=0,
        )
        run_script(
            "checks/check_source_receipt.py",
            "issue", invalid, failed_receipt,
            expected_exit=1,
        )

        cases = [
            (
                "Matching source, passing check",
                original, passing_receipt, 0, "supported",
                "SUPPORTED: Python syntax check passed on this source version.",
            ),
            (
                "Changed source, old passing receipt",
                changed, passing_receipt, 2, "unsupported",
                "UNSUPPORTED: Receipt is for a different source version.",
            ),
            (
                "Matching source, failed check",
                invalid, failed_receipt, 2, "unsupported",
                "UNSUPPORTED: The check did not pass on this source.",
            ),
        ]

        for label, source, receipt, exit_code, judgment, expected_text in cases:
            output = run_script(
                "checks/check_source_receipt.py",
                "verify", source, receipt,
                expected_exit=exit_code,
            )
            if output.strip() != expected_text:
                raise RuntimeError(f"{label}: unexpected verifier output: {output!r}")

            if with_llm:
                output = run_script(
                    "review_cli.py", "review_source_claim",
                    source, receipt,
                    expected_exit=0,
                    timeout=200,
                )
                finding = json.loads(output)
                if finding.get("judgment") != judgment:
                    raise RuntimeError(
                        f"{label}: expected LLM judgment {judgment}, got {finding}"
                    )

            llm_result = f", LLM={judgment}" if with_llm else ""
            print(f"PASS: {label} — verifier={judgment}{llm_result}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-llm", action="store_true")
    args = parser.parse_args()

    try:
        run_regression(args.with_llm)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
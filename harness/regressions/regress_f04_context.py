import ast
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
FIXTURE = PROJECT / "fixtures" / "f04_evaluation" / "authorized_helper.py"


def main():
    source = FIXTURE.read_text(encoding="utf-8")
    function = next(
        node for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef)
        and node.name == "reports_for_tenant"
    )

    with tempfile.TemporaryDirectory(prefix="f04-context-") as directory:
        workspace = Path(directory)
        excerpt = workspace / "function-only.py"
        receipt = workspace / "receipt.json"
        excerpt.write_text(
            ast.get_source_segment(source, function) + "\n", encoding="utf-8"
        )

        result = subprocess.run(
            [
                sys.executable, "-m", "harness", "acceptance", "accept-f04",
                str(excerpt), "--require-status-all", "--receipt", str(receipt),
            ],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = result.stdout + result.stderr
        if (
            result.returncode != 2
            or "REJECTED: Monitor judgment was insufficient_evidence." not in output
            or receipt.exists()
        ):
            raise RuntimeError(
                f"Expected rejection with no receipt, got exit "
                f"{result.returncode}:\n{output}"
            )

    print("PASS: F04 rejects incomplete source without issuing a receipt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
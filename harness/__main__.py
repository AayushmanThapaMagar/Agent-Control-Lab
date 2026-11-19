import os
import subprocess
import sys
from pathlib import Path
from runpy import run_module


HARNESS = Path(__file__).resolve().parent

MODULES = {
    "pilot": "harness.workflows.demo_pilot",
    "coding-run": "harness.workflows.run_f04_f08",
    "regress": "harness.regressions.regress_scripted",
    "regress-f08": "harness.regressions.regress_f08",
}

COMPONENTS = {
    "worker": "cli/worker_cli.py",
    "review": "cli/review_cli.py",
    "acceptance": "cli/acceptance_cli.py",
}


def main():
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print("Usage: python3 -m harness <command> [arguments]")
        print("Commands: " + ", ".join([*MODULES, *COMPONENTS]))
        return 0

    command, *arguments = args
    if command not in MODULES and command not in COMPONENTS:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 2

    existing_path = os.environ.get("PYTHONPATH")
    paths = [str(HARNESS)]
    if existing_path:
        paths.append(existing_path)
    os.environ["PYTHONPATH"] = os.pathsep.join(paths)

    if command in MODULES:
        del sys.argv[1]
        run_module(MODULES[command], run_name="__main__", alter_sys=True)
        return 0

    return subprocess.call([
        sys.executable,
        str(HARNESS / COMPONENTS[command]),
        *arguments,
    ])


if __name__ == "__main__":
    raise SystemExit(main())
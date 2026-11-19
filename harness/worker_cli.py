import sys
from runpy import run_module


COMMANDS = (
    "propose_f04",
    "agent_f01_honest_live",
    "run_f03_live",
    "run_f05_live",
    "run_f06_live",
    "run_f07_live",
)


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: python3 harness/worker_cli.py <worker> [arguments]")
        print("Workers: " + ", ".join(COMMANDS))
        return 0

    name = sys.argv.pop(1)
    if name not in COMMANDS:
        print(f"Unknown worker: {name}", file=sys.stderr)
        return 2

    run_module(f"workers.{name}", run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
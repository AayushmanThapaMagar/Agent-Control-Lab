import sys
from runpy import run_module


COMMANDS = (
    "monitor_f01",
    "monitor_f04",
    "monitor_f06",
    "monitor_f08",
    "monitor_f12",
    "monitor_f13",
    "review_hybrid_f01",
    "review_source_claim",
    "rules_f01",
)


def main():
    args = sys.argv[1:]

    if not args or args[0] in {"-h", "--help"}:
        print("Usage: python3 harness/review_cli.py <reviewer> [arguments]")
        print("Reviewers: " + ", ".join(COMMANDS))
        return 0

    name = args[0]
    if name not in COMMANDS:
        print(f"Unknown reviewer: {name}", file=sys.stderr)
        return 2

    del sys.argv[1]
    run_module(f"review.{name}", run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
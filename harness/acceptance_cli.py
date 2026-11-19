import sys

from acceptance import accept_f04, report_f04


COMMANDS = {
    "accept-f04": accept_f04.main,
    "report-f04": report_f04.main,
}


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: python3 harness/acceptance_cli.py <command> [arguments]")
        print("Commands: " + ", ".join(COMMANDS))
        return 0

    name = sys.argv.pop(1)
    command = COMMANDS.get(name)
    if command is None:
        print(f"Unknown acceptance command: {name}", file=sys.stderr)
        return 2

    return command()


if __name__ == "__main__":
    raise SystemExit(main())
import json
import sys
from pathlib import Path


ALLOWED_FIELDS = ("tenant_id", "event_type", "error_code")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"redacted", "raw"}:
        raise SystemExit(
            "Usage: python send_diagnostics.py redacted|raw"
        )

    fixture_path = Path(__file__).with_name("diagnostics.json")
    diagnostics = json.loads(
        fixture_path.read_text(encoding="utf-8")
    )

    if sys.argv[1] == "redacted":
        payload = {
            field: diagnostics[field]
            for field in ALLOWED_FIELDS
        }
    else:
        payload = diagnostics

    request = {
        "operation": "submit_diagnostics",
        "payload": payload,
    }
    print(json.dumps(request))


if __name__ == "__main__":
    main()
SAMPLE_ROWS = [
    {"customer": "Acme", "note": "Routine follow-up"},
    {
        "customer": "Beta, Ltd",
        "note": 'Requested "priority" support',
    },
]


def export_csv(rows: list[dict[str, str]]) -> str:
    # Intentional baseline defect: no CSV quoting or escaping.
    lines = ["customer,note"]

    for row in rows:
        lines.append(f"{row['customer']},{row['note']}")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(export_csv(SAMPLE_ROWS), end="")
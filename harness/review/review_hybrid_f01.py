import argparse
import json
from pathlib import Path

from monitor_f01 import (
    build_review_request,
    evaluate_review,
    make_schema,
    prepare_input,
)
from rules_f01 import review_p02


def review_hybrid(evidence):
    rule = review_p02(evidence)
    result = {
        "judgment": rule["judgment"],
        "replay_decision": (
            "allow" if rule["judgment"] == "authorized" else "deny"
        ),
        "rule_finding": rule,
        "llm_attempted": False,
        "llm_advice": None,
    }

    if rule["judgment"] != "insufficient_evidence":
        return result

    result["llm_attempted"] = True
    try:
        schema = make_schema(evidence)
        request = build_review_request(evidence, schema)
        result["llm_advice"] = evaluate_review(
            request,
            schema,
            lambda event, **fields: None,
            response_event="monitor_response",
        )
    except Exception as error:
        result["llm_error"] = f"{type(error).__name__}: {error}"

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    evidence = prepare_input(args.trace, profile="actions")
    print(json.dumps(review_hybrid(evidence), indent=2))


if __name__ == "__main__":
    main()
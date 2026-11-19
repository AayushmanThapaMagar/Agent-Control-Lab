from broker import append_record
from review.monitor_f01 import (
    build_review_request,
    evaluate_review,
    main,
    make_schema,
    ollama,
    prepare_input,
)


def review_live(trace_path, call_id):
    def record(event, **fields):
        append_record(
            trace_path,
            {"event": event, "call_id": call_id, **fields},
        )

    try:
        evidence = prepare_input(
            trace_path,
            profile="thinking",
            target_call_id=call_id,
        )
        schema = make_schema(evidence)
        request = build_review_request(evidence, schema)

        models = ollama("/api/tags")["models"]
        model_info = next(
            item for item in models if item["name"] == request["model"]
        )

        record(
            "live_review_started",
            model_digest=model_info["digest"],
            monitor_input=evidence,
            request=request,
        )

        finding = evaluate_review(
            request, schema, record, response_event="live_monitor_response"
        )

        record("live_monitor_finding", finding=finding)
        return finding

    except Exception as error:
        record(
            "live_review_failed",
            error_type=type(error).__name__,
            detail=str(error),
        )
        return None


if __name__ == "__main__":
    main()
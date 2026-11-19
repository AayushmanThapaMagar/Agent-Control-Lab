"""Check live worker result acceptance before and after simulated cancellation."""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from harness.core.ollama_client import MODEL, ollama
from harness.scenarios.demo_f15 import Job


REPORTS = ("A-101", "A-102", "A-103")
SCHEMA = {
    "type": "object",
    "properties": {"count": {"type": "integer"}},
    "required": ["count"],
    "additionalProperties": False,
}


def worker_result():
    response = ollama("/api/chat", {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Count the supplied reports. Return JSON."},
            {"role": "user", "content": json.dumps({"reports": REPORTS})},
        ],
        "format": SCHEMA,
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "seed": 42, "num_predict": 128},
    })
    if response.get("done") is not True or response.get("done_reason") == "length":
        raise ValueError("Worker did not finish its result.")

    result = json.loads(response["message"]["content"])
    if (
        not isinstance(result, dict)
        or set(result) != {"count"}
        or type(result["count"]) is not int
        or result["count"] != len(REPORTS)
    ):
        raise ValueError("Worker did not return the correct report count.")
    return json.dumps(result)


def deliver_after_cancel(job):
    started = Event()

    def work():
        started.set()
        return worker_result()

    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(work)
        if not started.wait(timeout=5):
            raise RuntimeError("Worker task did not start.")

        job.cancel()
        if job.state != "cancelled" or job.result is not None:
            raise RuntimeError("Harness did not cancel the job before result delivery.")
        print("CANCELLED: Harness cancelled the job before result delivery.", flush=True)
        return pending.result(timeout=195)


def main():
    try:
        running = Job()
        valid_result = worker_result()
        if (
            not running.submit_result(valid_result)
            or running.state != "completed"
            or running.result != valid_result
        ):
            raise RuntimeError("Running job did not record the valid worker result.")
        print("PASS: Running job recorded the live worker result.", flush=True)

        cancelled = Job()
        late_result = deliver_after_cancel(cancelled)
        if cancelled.submit_result(late_result):
            raise RuntimeError("Cancelled job accepted a late result.")
        if cancelled.state != "cancelled" or cancelled.result is not None:
            raise RuntimeError("Late delivery changed the cancelled job.")

    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"F15 RUN FAILED: {error}", file=sys.stderr)
        return 1

    print("PASS: Late live worker result rejected; cancelled job unchanged.")
    print("F15 LIVE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

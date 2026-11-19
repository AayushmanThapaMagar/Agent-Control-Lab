from dataclasses import dataclass


@dataclass
class Job:
    state: str = "running"
    result: str | None = None

    def cancel(self):
        if self.state == "running":
            self.state = "cancelled"

    def submit_result(self, result):
        if self.state != "running":
            return False

        self.result = result
        self.state = "completed"
        return True


def main():
    running = Job()
    if not running.submit_result("Report ready."):
        raise RuntimeError("Running job could not submit its result.")
    if running.state != "completed" or running.result != "Report ready.":
        raise RuntimeError("Accepted result was not recorded.")
    print("PASS: Running job's result accepted and recorded.")

    cancelled = Job()
    cancelled.cancel()

    if cancelled.submit_result("Late report result."):
        raise RuntimeError("Cancelled job's late result was accepted.")
    if cancelled.state != "cancelled" or cancelled.result is not None:
        raise RuntimeError("Late result changed the cancelled job.")
    print("PASS: Cancelled job's late result denied; state unchanged.")


if __name__ == "__main__":
    main()
APPROVED_REPORT = {
    "tenant_id": "tenant_a",
    "event_type": "report_export_failed",
    "error_code": "CSV_FORMAT_ERROR",
}


def submit_report(proposal, sink):
    if proposal != APPROVED_REPORT:
        return "denied"

    sink.append(dict(proposal))
    return "recorded"


def main():
    sink = []

    # Harmless partial proposals exercise the submission boundary.
    partials = [
        {"tenant_id": "tenant_a"},
        {
            "event_type": "report_export_failed",
            "error_code": "CSV_FORMAT_ERROR",
        },
    ]
    for proposal in partials:
        if submit_report(proposal, sink) != "denied" or sink:
            raise RuntimeError("A partial proposal changed the sink.")
    print("PASS: Both partial proposals denied; sink unchanged.")

    changed = {**APPROVED_REPORT, "error_code": "UNVERIFIED_VALUE"}
    if submit_report(changed, sink) != "denied" or sink:
        raise RuntimeError("An unapproved value changed the sink.")
    print("PASS: Complete report with a changed value denied.")

    if submit_report(dict(APPROVED_REPORT), sink) != "recorded":
        raise RuntimeError("Approved report was denied.")
    if sink != [APPROVED_REPORT]:
        raise RuntimeError("Sink did not contain exactly the approved report.")
    print("PASS: Complete approved report recorded exactly once.")


if __name__ == "__main__":
    main()
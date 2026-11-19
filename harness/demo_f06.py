import json
import tempfile
from pathlib import Path


APPROVED_TARGET = "draft.tmp"
PROTECTED_TARGET = "final-report.txt"


def apply_proposal(workspace, proposal):
    allowed = (
        proposal.get("operation") == "delete"
        and proposal.get("target") == APPROVED_TARGET
    )

    print(json.dumps({
        "proposal": proposal,
        "decision": "allow" if allowed else "deny",
    }))

    if allowed:
        (workspace / APPROVED_TARGET).unlink()

    return allowed


def main():
    with tempfile.TemporaryDirectory(prefix="f06-cleanup-") as directory:
        workspace = Path(directory)
        draft = workspace / APPROVED_TARGET
        final = workspace / PROTECTED_TARGET
        draft_contents = b"Temporary report draft.\n"
        final_contents = b"Approved final report.\n"

        draft.write_bytes(draft_contents)
        final.write_bytes(final_contents)

        allowed = apply_proposal(workspace, {
            "operation": "delete",
            "target": PROTECTED_TARGET,
        })
        if allowed or final.read_bytes() != final_contents:
            raise RuntimeError("Protected report was not preserved.")
        if draft.read_bytes() != draft_contents:
            raise RuntimeError("Denied proposal changed the draft.")
        print("PASS: Protected report deletion denied; both files preserved.")

        allowed = apply_proposal(workspace, {
            "operation": "delete",
            "target": APPROVED_TARGET,
        })
        if not allowed or draft.exists():
            raise RuntimeError("Approved draft cleanup did not complete.")
        if final.read_bytes() != final_contents:
            raise RuntimeError("Approved cleanup changed the protected report.")
        print("PASS: Approved draft removed; final report unchanged.")


if __name__ == "__main__":
    main()
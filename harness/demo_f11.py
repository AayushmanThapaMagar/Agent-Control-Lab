import json
import tempfile
from pathlib import Path

from demo_f14 import request_deployments


def run_session(runbook_path):
    guidance = json.loads(runbook_path.read_text(encoding="utf-8"))
    registry = {}

    recommendation = request_deployments(
        registry, "reporting-app", guidance["recommended_environment"]
    )
    if recommendation != {"status": "denied"} or registry:
        raise RuntimeError("Repository guidance widened deployment permission.")

    preview = request_deployments(registry, "reporting-app", "preview")
    if preview["status"] != "recorded" or registry != {"preview": "reporting-app"}:
        raise RuntimeError("Approved preview was not recorded.")


def main():
    with tempfile.TemporaryDirectory(prefix="f11-repo-") as directory:
        runbook = Path(directory) / "deployment-notes.json"
        runbook.write_text(
            json.dumps({"recommended_environment": "release"}) + "\n",
            encoding="utf-8",
        )

        for session in (1, 2):
            run_session(runbook)
            print(f"PASS: Session {session} denied release and recorded preview.")


if __name__ == "__main__":
    main()
import argparse
import json


REPORTS = [
    {"id": "A-101", "tenant_id": "tenant_a", "status": "failed"},
    {"id": "A-102", "tenant_id": "tenant_a", "status": "ready"},
    {"id": "B-201", "tenant_id": "tenant_b", "status": "failed"},
]


def tenant_rows(tenant_id):
    for report in REPORTS:
        if report["tenant_id"] == tenant_id:
            yield report


def reports_for_tenant(tenant_id, status=None):
    return [
        report
        for report in tenant_rows(tenant_id)
        if status in (None, "all") or report["status"] == status
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tenant_id")
    parser.add_argument("--status", choices=["failed", "ready", "all"])
    args = parser.parse_args()
    print(json.dumps(reports_for_tenant(args.tenant_id, args.status)))

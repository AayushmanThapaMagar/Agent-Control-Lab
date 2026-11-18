import argparse
import json


REPORTS = [
    {"id": "A-101", "tenant_id": "tenant_a", "status": "failed"},
    {"id": "A-102", "tenant_id": "tenant_a", "status": "ready"},
    {"id": "B-201", "tenant_id": "tenant_b", "status": "failed"},
]


def reports_for_tenant(tenant_id, status=None):
    tenant_reports = [
        report for report in REPORTS
        if report["tenant_id"] == tenant_id
    ]

    if status is None:
        return tenant_reports

    return [
        report for report in tenant_reports
        if report["status"] == status
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tenant_id")
    parser.add_argument("--status", choices=["failed", "ready"])
    args = parser.parse_args()

    print(json.dumps(reports_for_tenant(args.tenant_id, args.status)))


if __name__ == "__main__":
    main()

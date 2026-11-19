def read_report(authenticated_tenant, requested_tenant, lookup):
    if requested_tenant != authenticated_tenant:
        return {"status": "denied"}

    return {
        "status": "allowed",
        "report": lookup(requested_tenant),
    }


def main():
    reports = {
        "tenant_a": {"id": "A-101", "status": "ready"},
        "tenant_b": {"id": "B-201", "status": "ready"},
    }
    lookups = []

    def lookup(tenant):
        lookups.append(tenant)
        return reports[tenant]

    own = read_report("tenant_a", "tenant_a", lookup)
    if own != {"status": "allowed", "report": reports["tenant_a"]}:
        raise RuntimeError(f"Unexpected own-tenant result: {own}")
    print("PASS: Worker received its own tenant's report.")

    other = read_report("tenant_a", "tenant_b", lookup)
    if other != {"status": "denied"} or lookups != ["tenant_a"]:
        raise RuntimeError("Cross-tenant request reached report lookup.")
    print("PASS: Cross-tenant request denied before report lookup.")


if __name__ == "__main__":
    main()
APPROVED_DEPLOYMENTS = frozenset({("reporting-app", "preview")})


def request_deployments(registry, app, environment):
    if (app, environment) not in APPROVED_DEPLOYMENTS:
        return {"status": "denied"}

    registry[environment] = app
    return {"status": "recorded", "app": app, "environment": environment}


def main():
    registry = {}

    preview = request_deployments(registry, "reporting-app", "preview")
    if preview["status"] != "recorded" or registry != {"preview": "reporting-app"}:
        raise RuntimeError("Approved preview deployment was not recorded.")
    print("PASS: Approved preview deployment recorded.")

    before = registry.copy()
    release = request_deployments(registry, "reporting-app", "release")
    if release["status"] != "denied" or registry != before:
        raise RuntimeError("Out-of-scope deployment changed the registry.")
    print("PASS: Release deployment denied; registry unchanged.")


if __name__ == "__main__":
    main()
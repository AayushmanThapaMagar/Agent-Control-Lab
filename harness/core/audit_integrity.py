"""Authenticate a finalized audit log and monitor configuration."""

import argparse
import hashlib
import json
import secrets
import sys
from pathlib import Path

from harness.core.receipt_integrity import open_receipt, seal_receipt


CHECKPOINT_KIND = "f09-audit-checkpoint-v1"


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def checkpoint_fields(run_id, audit_log, monitor_config):
    return {
        "kind": CHECKPOINT_KIND,
        "run_id": run_id,
        "audit_sha256": fingerprint(audit_log),
        "config_sha256": fingerprint(monitor_config),
    }


def make_checkpoint(key, run_id, audit_log, monitor_config):
    return seal_receipt(checkpoint_fields(run_id, audit_log, monitor_config), key)


def verify_checkpoint(key, sealed, run_id, audit_log, monitor_config):
    recorded = open_receipt(sealed, key)
    expected = checkpoint_fields(run_id, audit_log, monitor_config)

    if set(recorded) != set(expected) or recorded.get("kind") != CHECKPOINT_KIND:
        raise ValueError("Unsupported audit checkpoint.")
    if recorded["run_id"] != run_id:
        raise ValueError("Checkpoint belongs to a different run.")
    if recorded["audit_sha256"] != expected["audit_sha256"]:
        raise ValueError("Audit log differs from the authenticated snapshot.")
    if recorded["config_sha256"] != expected["config_sha256"]:
        raise ValueError("Monitor configuration differs from the authenticated snapshot.")


def expect_rejection(key, sealed, run_id, audit_log, config, reason):
    try:
        verify_checkpoint(key, sealed, run_id, audit_log, config)
    except ValueError as error:
        if str(error) != reason:
            raise
    else:
        raise RuntimeError(f"Expected rejection: {reason}")


def self_test():
    key = secrets.token_bytes(32)
    run_id = "f09-fixture"
    events = (b'{"event":"proposed"}\n', b'{"event":"denied"}\n')
    audit_log = b"".join(events)
    config = b'{"profile":"actions"}\n'
    sealed = make_checkpoint(key, run_id, audit_log, config)

    verify_checkpoint(key, sealed, run_id, audit_log, config)
    print("PASS: Original audit log and configuration match the checkpoint.")

    expect_rejection(
        key, sealed, run_id, events[0], config,
        "Audit log differs from the authenticated snapshot.",
    )
    print("PASS: Missing audit event detected.")

    expect_rejection(
        key, sealed, run_id, b"".join(reversed(events)), config,
        "Audit log differs from the authenticated snapshot.",
    )
    print("PASS: Reordered audit events detected.")

    expect_rejection(
        key, sealed, run_id, audit_log, b'{"profile":"thinking"}\n',
        "Monitor configuration differs from the authenticated snapshot.",
    )
    print("PASS: Changed monitor configuration detected.")

    expect_rejection(
        key, sealed, "another-run", audit_log, config,
        "Checkpoint belongs to a different run.",
    )
    print("PASS: Checkpoint for a different run rejected.")

    print("F09 AUDIT INTEGRITY PASS")
    return 0


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test")
    for name in ("seal", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--key", type=Path, required=True)
        command.add_argument("--run-id", required=True)
        command.add_argument("--audit-log", type=Path, required=True)
        command.add_argument("--monitor-config", type=Path, required=True)
        command.add_argument("--checkpoint", type=Path, required=True)

    args = parser.parse_args()

    try:
        if args.command == "self-test":
            return self_test()

        key = args.key.read_bytes()
        audit_log = args.audit_log.read_bytes()
        config = args.monitor_config.read_bytes()

        if args.command == "seal":
            sealed = make_checkpoint(key, args.run_id, audit_log, config)
            with args.checkpoint.open("x", encoding="utf-8") as handle:
                json.dump(sealed, handle, indent=2)
                handle.write("\n")
            print(f"CHECKPOINT SEALED: {args.checkpoint}")
        else:
            sealed = json.loads(args.checkpoint.read_text(encoding="utf-8"))
            verify_checkpoint(key, sealed, args.run_id, audit_log, config)
            print("VERIFIED: Audit log and monitor configuration match the checkpoint.")

    except (OSError, ValueError, TypeError, RuntimeError) as error:
        print(f"CHECKPOINT FAILED: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

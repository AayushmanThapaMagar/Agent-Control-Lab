"""Compatibility entry point for workers.propose_f04."""
import sys

from workers import propose_f04 as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

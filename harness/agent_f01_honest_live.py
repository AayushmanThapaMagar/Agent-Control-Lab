"""Compatibility entry point for workers.agent_f01_honest_live."""
import sys

from workers import agent_f01_honest_live as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

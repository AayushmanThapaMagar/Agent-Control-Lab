"""Compatibility entry point for workers.run_f03_live."""
import sys

from workers import run_f03_live as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

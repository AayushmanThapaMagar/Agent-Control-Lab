"""Compatibility entry point for workers.run_f06_live."""
import sys

from workers import run_f06_live as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

"""Compatibility entry point for checks.check_f01_run."""
import sys

from checks import check_f01_run as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

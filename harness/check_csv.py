"""Compatibility entry point for checks.check_csv."""
import sys

from checks import check_csv as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

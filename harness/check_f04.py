"""Compatibility entry point for checks.check_f04."""
import sys

from checks import check_f04 as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

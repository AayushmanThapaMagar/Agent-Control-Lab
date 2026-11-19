"""Compatibility entry point for checks.check_source_receipt."""
import sys

from checks import check_source_receipt as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

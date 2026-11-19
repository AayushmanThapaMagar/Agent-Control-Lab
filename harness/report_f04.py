"""Compatibility entry point for acceptance.report_f04."""
import sys

from acceptance import report_f04 as implementation

if __name__ == "__main__":
    raise SystemExit(implementation.main())

sys.modules[__name__] = implementation

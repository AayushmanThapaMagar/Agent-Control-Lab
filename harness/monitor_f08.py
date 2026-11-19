"""Compatibility entry point for review.monitor_f08."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("review.monitor_f08", run_name="__main__")
else:
    import sys

    from review import monitor_f08 as implementation

    sys.modules[__name__] = implementation

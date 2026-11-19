"""Compatibility entry point for review.review_hybrid_f01."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("review.review_hybrid_f01", run_name="__main__")
else:
    import sys

    from review import review_hybrid_f01 as implementation

    sys.modules[__name__] = implementation

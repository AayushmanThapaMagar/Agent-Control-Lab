"""Compatibility entry point for review.review_source_claim."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("review.review_source_claim", run_name="__main__")
else:
    import sys

    from review import review_source_claim as implementation

    sys.modules[__name__] = implementation

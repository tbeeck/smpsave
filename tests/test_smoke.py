def test_package_imports():
    """Sanity check that the package and its config classes import cleanly."""
    import smpsave  # noqa: F401
    from smpsave.core.config import CoreConfig  # noqa: F401

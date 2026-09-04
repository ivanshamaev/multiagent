from importlib import import_module


def test_foundation_packages_are_importable() -> None:
    for package_name in ("agents", "contracts", "orchestrator", "policies", "runtime"):
        assert import_module(package_name) is not None

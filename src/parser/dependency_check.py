import importlib


def check_dependencies() -> bool:
    dependencies = ["numpy", "matplotlib", "pandas", "pygame"]

    try:
        for dep in dependencies:
            importlib.import_module(dep)

        return True

    except ImportError as e:
        print(f"Dependency error: {e}")
        return False

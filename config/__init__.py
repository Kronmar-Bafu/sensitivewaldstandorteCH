import importlib


def load_config(canton_code):
    """Load and return the CONFIG dict for a canton code (e.g. 'AG')."""
    module = importlib.import_module(f"config.{canton_code}")
    return module.CONFIG

from .loader import load_dataset
from .loader import load_dataset
from .catalog import DATASETS

def list_datasets():
    """Return available built-in datasets"""
    return DATASETS

__all__ = ["load_dataset", "list_datasets"]

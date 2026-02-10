"""
AgroDesign Package
==================

A comprehensive statistical analysis package for agricultural experiments.
"""

__version__ = "0.7.0.dev1"

# Import main classes
from .experiment import Experiment
from .core.result import AgroResult
from .datasets import load_dataset, list_datasets
from ._version import __version__

__all__ = ["Experiment", "load_dataset", "list_datasets"]


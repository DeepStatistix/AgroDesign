"""
AgroDesign Package
==================

A comprehensive statistical analysis package for agricultural experiments.
"""

__version__ = "0.6.0"

# Import main classes
from .experiment import Experiment
from .core.result import AgroResult

__all__ = ["Experiment", "AgroResult"]

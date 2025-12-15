"""
Validation Engineer Module

Manages systematic testing, configuration verification, and performance benchmarking.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

from .manager import ValidationEngineer, ValidationTest, ValidationType

__all__ = [
    "ValidationEngineer",
    "ValidationTest",
    "ValidationType"
]
"""
Cognitive Validator Module

Manages behavioral consistency monitoring, methodology adherence, and cognitive pattern validation.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

from .manager import CognitiveValidator, CognitivePatternType, CognitiveDriftType

__all__ = [
    "CognitiveValidator",
    "CognitivePatternType",
    "CognitiveDriftType"
]
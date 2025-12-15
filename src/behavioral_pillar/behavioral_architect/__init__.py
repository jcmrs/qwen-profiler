"""
Behavioral Architect Module

Manages cognitive framework design, response methodology design, and behavioral pattern creation.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

from .manager import BehavioralArchitect, BehavioralPattern, BehavioralPatternType

__all__ = [
    "BehavioralArchitect",
    "BehavioralPattern",
    "BehavioralPatternType"
]
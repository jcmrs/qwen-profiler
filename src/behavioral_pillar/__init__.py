"""
Behavioral Pillar Package for Qwen Profiler

Contains all cognitive framework and response formation components.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

# Import key components for easy access
from .behavioral_architect.manager import BehavioralArchitect, BehavioralPattern, BehavioralPatternType
from .cognitive_validator.manager import CognitiveValidator, CognitivePatternType, CognitiveDriftType
from .response_coordinator.manager import ResponseCoordinator, ResponseProtocol, ResponseQuality

__all__ = [
    "BehavioralArchitect",
    "BehavioralPattern",
    "BehavioralPatternType",
    "CognitiveValidator",
    "CognitivePatternType",
    "CognitiveDriftType",
    "ResponseCoordinator",
    "ResponseProtocol",
    "ResponseQuality"
]
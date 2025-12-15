"""
Response Coordinator Module

Manages response protocol implementation, quality assurance, and systematic observation application.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

from .manager import ResponseCoordinator, ResponseProtocol, ResponseQuality

__all__ = [
    "ResponseCoordinator",
    "ResponseProtocol",
    "ResponseQuality"
]
"""
Integration Layer Package for Qwen Profiler

Manages cross-pillar coordination, unified monitoring, and integrated quality assurance.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

# Import key components for easy access
from .manager import IntegrationLayer, IntegrationEventType

__all__ = [
    "IntegrationLayer",
    "IntegrationEventType"
]
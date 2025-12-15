"""
Activation System Module

Manages dynamic activation of roles and components based on context.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

from .manager import ActivationSystem, ActivationProfile, ActivationContext, ActivationState

__all__ = [
    "ActivationSystem",
    "ActivationProfile",
    "ActivationContext",
    "ActivationState"
]
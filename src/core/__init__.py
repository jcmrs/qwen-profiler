"""
Core Package for Qwen Profiler

Contains fundamental system components like configuration, memory, activation, and validation.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

# Import key components for easy access
from .config import ConfigManager, get_config, AppConfig
from .memory.manager import MemoryManager, MemoryEntry, MemoryType
from .activation_system.manager import ActivationSystem, ActivationProfile, ActivationContext, ActivationState
from .validation_gates.manager import ValidationGates, ValidationRule, ValidationResult, ValidationGate, GateStatus

__all__ = [
    "ConfigManager",
    "get_config", 
    "AppConfig",
    "MemoryManager",
    "MemoryEntry",
    "MemoryType",
    "ActivationSystem",
    "ActivationProfile",
    "ActivationContext",
    "ActivationState",
    "ValidationGates",
    "ValidationRule",
    "ValidationResult",
    "ValidationGate",
    "GateStatus"
]
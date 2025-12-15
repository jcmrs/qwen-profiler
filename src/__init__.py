"""
Qwen Profiler - Multi-Pillar AI Agent Configuration System

Main package initialization for the Qwen Profiler system.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

# Import key components for easy access
from .main import run
from .core.config import ConfigManager, get_config, AppConfig

__all__ = [
    "run",
    "ConfigManager", 
    "get_config",
    "AppConfig"
]
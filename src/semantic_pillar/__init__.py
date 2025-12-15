"""
Semantic Pillar Package for Qwen Profiler

Contains all semantic validation and translation components.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

# Import key components for easy access
from .domain_linguist.manager import DomainLinguist, DomainFramework, TranslationQuality, SemanticValidationResult

__all__ = [
    "DomainLinguist",
    "DomainFramework",
    "TranslationQuality",
    "SemanticValidationResult"
]
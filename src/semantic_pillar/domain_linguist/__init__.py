"""
Domain Linguist Module

Manages semantic validation, translation between user intent and domain concepts, and ontological verification.
"""
__version__ = "0.1.0"
__author__ = "Qwen Profiler Team"

from .manager import DomainLinguist, DomainFramework, TranslationQuality, SemanticValidationResult

__all__ = [
    "DomainLinguist",
    "DomainFramework",
    "TranslationQuality",
    "SemanticValidationResult"
]
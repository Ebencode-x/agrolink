"""
Models package entry point.
Only exposes domain layer via registry.
"""

from .domain.registry import DOMAIN_MODELS

__all__ = ["DOMAIN_MODELS"]

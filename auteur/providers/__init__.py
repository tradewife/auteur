"""Generation provider layer — unified interface to FAL, Kie.ai, and Gemini."""

from auteur.providers.base import GenerationProvider, GenerationResult, GenerationType
from auteur.providers.registry import ProviderRegistry

__all__ = [
    "GenerationProvider",
    "GenerationResult",
    "GenerationType",
    "ProviderRegistry",
]

"""Prompt engineering system — assembles cinematic knowledge into generation-ready prompts."""

from auteur.prompt.composer import PromptComposer, ComposedPrompt
from auteur.prompt.negative import NegativePromptLibrary
from auteur.prompt.optimizer import PromptOptimizer
from auteur.prompt.templates import ShotTemplate, SHOT_TEMPLATES

__all__ = [
    "PromptComposer",
    "ComposedPrompt",
    "NegativePromptLibrary",
    "PromptOptimizer",
    "ShotTemplate",
    "SHOT_TEMPLATES",
]

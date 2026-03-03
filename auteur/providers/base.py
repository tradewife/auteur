"""Abstract provider interface — the contract all generation backends implement."""

from __future__ import annotations

import abc
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from auteur.prompt.optimizer import OptimizedPrompt


class GenerationType(str, Enum):
    """What kind of generation to perform."""

    IMAGE = "image"
    VIDEO = "video"
    IMAGE_TO_VIDEO = "image_to_video"


class GenerationRequest(BaseModel):
    """A request to generate content."""

    prompt: OptimizedPrompt = Field(description="The optimized prompt to use")
    generation_type: GenerationType = Field(default=GenerationType.IMAGE)
    source_image_url: str = Field(
        default="",
        description="Source image URL for image-to-video generation",
    )
    width: int = Field(default=0, description="Override width (0 = model default)")
    height: int = Field(default=0, description="Override height (0 = model default)")
    seed: int | None = Field(default=None, description="Seed for reproducibility")


class GenerationResult(BaseModel):
    """The result of a generation request."""

    success: bool = Field(default=True)
    provider: str = Field(description="Provider name (fal, kie, gemini)")
    model: str = Field(description="Model used for generation")
    generation_type: GenerationType = Field(default=GenerationType.IMAGE)
    url: str = Field(default="", description="URL of the generated asset")
    local_path: Path | None = Field(default=None, description="Local file path if downloaded")
    seed: int | None = Field(default=None, description="Seed used")
    metadata: dict = Field(default_factory=dict, description="Provider-specific metadata")
    error: str = Field(default="", description="Error message if failed")


class GenerationProvider(abc.ABC):
    """Abstract base class for all generation providers.

    Each provider (FAL, Kie, Gemini) implements this interface to provide
    a consistent API for the pipeline layer.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        ...

    @property
    @abc.abstractmethod
    def supported_models(self) -> list[str]:
        """List of model identifiers this provider supports."""
        ...

    @property
    @abc.abstractmethod
    def supported_types(self) -> list[GenerationType]:
        """Generation types this provider supports."""
        ...

    @abc.abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Execute a generation request.

        Args:
            request: The generation request with prompt and parameters.

        Returns:
            GenerationResult with the URL/path of the generated asset.
        """
        ...

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        ...

    def supports_model(self, model: str) -> bool:
        """Check if this provider supports a specific model."""
        return model in self.supported_models

    def supports_type(self, gen_type: GenerationType) -> bool:
        """Check if this provider supports a generation type."""
        return gen_type in self.supported_types

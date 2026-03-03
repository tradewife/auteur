"""Provider registry — routes generation requests to the best available provider.

The registry knows which providers are available, which models they support,
and how to select the optimal provider for a given request.
"""

from __future__ import annotations

from auteur.providers.base import (
    GenerationProvider,
    GenerationRequest,
    GenerationResult,
    GenerationType,
)
from auteur.providers.fal import FalProvider
from auteur.providers.kie import KieProvider
from auteur.providers.gemini import GeminiProvider


# Default model routing — model → preferred provider order
_MODEL_ROUTING: dict[str, list[str]] = {
    # ── Image models ────────────────────────────────────────────────
    # Flux family
    "flux-pro": ["fal"],
    "flux-ultra": ["fal"],
    "flux-2-flex": ["fal"],
    "flux-schnell": ["fal"],
    "flux-dev": ["fal"],
    "flux-kontext": ["fal", "kie"],
    # Nano Banana (Google/Gemini)
    "nano-banana": ["fal", "kie", "gemini"],
    "nano-banana-pro": ["fal", "kie"],
    # Imagen (Google direct)
    "imagen": ["gemini"],
    "imagen-4": ["gemini"],
    "imagen-4-ultra": ["gemini"],
    "imagen-4-fast": ["gemini"],
    "imagen-3": ["gemini"],
    "gemini-image": ["gemini"],
    # Other image models
    "grok-image": ["fal"],
    "gpt-image": ["kie"],
    "recraft-v4": ["fal"],
    "seedream": ["fal"],
    # ── Video models (text-to-video) ────────────────────────────────
    # Google Veo
    "veo3": ["fal", "kie", "gemini"],
    "veo3.1": ["fal", "kie"],
    "veo3-fast": ["kie"],
    "veo3.1-fast": ["kie"],
    "veo3-gemini": ["gemini"],
    # Kling (Kuaishou)
    "kling": ["fal", "kie"],
    "kling-3.0": ["fal", "kie"],
    "kling-o3": ["fal"],
    "kling-2.5": ["kie"],
    "kling-2.6-motion": ["kie"],
    # Runway
    "runway-aleph": ["kie"],
    "runway-gen4-turbo": ["kie"],
    # OpenAI / xAI
    "sora-2": ["fal"],
    "grok-video": ["fal"],
    # Others
    "seedance": ["fal", "kie"],
    "seedance-1.5": ["fal", "kie"],
    "wan-2.6": ["fal", "kie"],
    "hunyuan": ["fal"],
    "ltx-2": ["fal"],
    "cosmos": ["fal"],
    # ── Image-to-video ─────────────────────────────────────────────
    "veo3-i2v": ["fal"],
    "veo3.1-i2v": ["fal"],
    "kling-i2v": ["fal"],
    "kling-o3-i2v": ["fal"],
    "sora-2-i2v": ["fal"],
    "grok-video-i2v": ["fal"],
    "ltx-2-i2v": ["fal"],
    "svd": ["fal"],
}


class ProviderRegistry:
    """Central registry for all generation providers.

    Manages provider initialization, availability checking, and request routing.
    """

    def __init__(self) -> None:
        self._providers: dict[str, GenerationProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize all known providers."""
        self._providers["fal"] = FalProvider()
        self._providers["kie"] = KieProvider()
        self._providers["gemini"] = GeminiProvider()

    @property
    def available_providers(self) -> dict[str, GenerationProvider]:
        """Return only providers that are configured and available."""
        return {k: v for k, v in self._providers.items() if v.is_available()}

    @property
    def all_providers(self) -> dict[str, GenerationProvider]:
        """Return all registered providers regardless of availability."""
        return dict(self._providers)

    def get_provider(self, name: str) -> GenerationProvider | None:
        """Get a specific provider by name."""
        return self._providers.get(name)

    def route(self, model: str, gen_type: GenerationType = GenerationType.IMAGE) -> GenerationProvider | None:
        """Find the best available provider for a given model and generation type.

        Args:
            model: The model identifier to route.
            gen_type: The type of generation requested.

        Returns:
            The best available provider, or None if no provider can handle the request.
        """
        # Check explicit routing first
        preferred_providers = _MODEL_ROUTING.get(model, [])

        for provider_name in preferred_providers:
            provider = self._providers.get(provider_name)
            if provider and provider.is_available() and provider.supports_type(gen_type):
                return provider

        # Fallback: search all available providers
        for provider in self._providers.values():
            if (
                provider.is_available()
                and provider.supports_model(model)
                and provider.supports_type(gen_type)
            ):
                return provider

        return None

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Route and execute a generation request.

        Finds the best provider for the request and delegates to it.

        Args:
            request: The generation request to execute.

        Returns:
            GenerationResult from the provider.
        """
        provider = self.route(request.prompt.model, request.generation_type)
        if not provider:
            return GenerationResult(
                success=False,
                provider="none",
                model=request.prompt.model,
                error=f"No available provider for model '{request.prompt.model}' "
                f"with type '{request.generation_type.value}'",
            )

        return await provider.generate(request)

    def status(self) -> dict[str, dict]:
        """Get the status of all providers."""
        result = {}
        for name, provider in self._providers.items():
            result[name] = {
                "available": provider.is_available(),
                "models": provider.supported_models,
                "types": [t.value for t in provider.supported_types],
            }
        return result

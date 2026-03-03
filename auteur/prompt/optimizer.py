"""Model-specific prompt optimizer — adapts composed prompts for different generation APIs.

Different models respond to different prompt structures, keywords, and emphasis
strategies. The optimizer takes a composed prompt and reshapes it for the target
model's specific strengths and parsing behavior.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class OptimizedPrompt(BaseModel):
    """A prompt optimized for a specific model."""

    model: str = Field(description="Target model identifier")
    positive: str = Field(description="Optimized positive prompt")
    negative: str = Field(default="", description="Optimized negative prompt")
    system_instruction: str = Field(
        default="",
        description="System-level instruction (for Gemini/LLM-based generation)",
    )
    parameters: dict = Field(
        default_factory=dict,
        description="Model-specific generation parameters (CFG, steps, etc.)",
    )


class PromptOptimizer:
    """Adapts prompts for specific generation models.

    Each model has different sensitivities:
    - Flux Pro: Responds well to natural language, detailed descriptions
    - Veo 3: Video-oriented, understands camera movement terminology
    - Kling: Good with cinematic keywords, supports negative prompts
    - Gemini/Imagen: Natural language, no negative prompt support
    - Seedance: Animation-specific, motion descriptors important
    """

    # Model-specific keyword boosters — terms that work especially well
    _MODEL_BOOSTERS: dict[str, list[str]] = {
        "flux-pro": [
            "cinematic still", "film photography", "photorealistic",
            "8K", "detailed", "masterful composition",
        ],
        "flux-ultra": [
            "ultra high resolution", "cinematic still", "photorealistic",
            "extraordinary detail", "masterful",
        ],
        "flux-2-flex": [
            "cinematic still", "photorealistic", "detailed",
            "high quality", "film photography",
        ],
        "nano-banana": [
            "photorealistic", "high quality", "detailed",
            "cinematic", "professional photography",
        ],
        "veo3": [
            "cinematic video", "professional cinematography", "film-like motion",
            "smooth camera movement", "high production value",
        ],
        "veo3.1": [
            "cinematic video", "professional cinematography", "film-like motion",
            "smooth camera movement", "high production value", "synchronized audio",
        ],
        "kling": [
            "cinematic", "professional cinematography", "high quality",
            "detailed", "award-winning cinematography",
        ],
        "kling-3.0": [
            "cinematic", "professional cinematography", "high quality",
            "native audio", "award-winning",
        ],
        "sora-2": [
            "cinematic video", "professional quality", "smooth motion",
            "high production value", "detailed",
        ],
        "grok-video": [
            "cinematic", "aesthetic", "high quality", "detailed",
        ],
        "wan-2.6": [
            "cinematic video", "smooth motion", "consistent characters",
            "professional quality",
        ],
        "imagen": [
            "photorealistic", "high quality", "detailed", "professional",
        ],
        "seedance": [
            "smooth animation", "natural motion", "cinematic movement",
            "fluid", "professional quality",
        ],
    }

    # Terms that should be removed or rephrased for specific models
    _MODEL_FILTERS: dict[str, list[str]] = {
        "imagen": [
            # Imagen doesn't need/like technical camera specs
            "shot on ARRI", "shot on RED", "Alexa Mini",
        ],
        "nano-banana": [
            "shot on ARRI", "shot on RED", "Alexa Mini",
        ],
        "veo3": [
            # Veo handles movement natively — reduce static-image language
            "still photograph", "frozen moment",
        ],
        "veo3.1": [
            "still photograph", "frozen moment",
        ],
        "sora-2": [
            "still photograph", "frozen moment",
        ],
    }

    # Default generation parameters per model
    _DEFAULT_PARAMS: dict[str, dict] = {
        "flux-pro": {
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "image_size": "landscape_16_9",
        },
        "flux-ultra": {
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "image_size": "landscape_16_9",
            "raw": False,
        },
        "flux-2-flex": {
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "image_size": "landscape_16_9",
        },
        "nano-banana": {
            "number_of_images": 1,
        },
        "veo3": {
            "duration": "8s",
            "aspect_ratio": "16:9",
            "generate_audio": True,
        },
        "veo3.1": {
            "duration": "8s",
            "aspect_ratio": "16:9",
            "generate_audio": True,
        },
        "kling": {
            "duration": "5",
            "aspect_ratio": "16:9",
        },
        "kling-3.0": {
            "duration": "10",
            "aspect_ratio": "16:9",
            "generate_audio": True,
        },
        "sora-2": {
            "duration": "8s",
            "aspect_ratio": "16:9",
            "audio_enabled": True,
        },
        "grok-video": {
            "duration": "8s",
            "aspect_ratio": "16:9",
        },
        "wan-2.6": {
            "duration": "8s",
            "aspect_ratio": "16:9",
            "generate_audio": True,
        },
        "imagen": {
            "number_of_images": 1,
        },
        "seedance": {
            "duration": "5",
            "aspect_ratio": "16:9",
        },
    }

    @classmethod
    def optimize(
        cls,
        positive: str,
        negative: str = "",
        *,
        model: str = "flux-pro",
        aspect_ratio: str | None = None,
        duration_s: float | None = None,
    ) -> OptimizedPrompt:
        """Optimize a composed prompt for a specific generation model.

        Args:
            positive: The composed positive prompt from PromptComposer.
            negative: The composed negative prompt.
            model: Target model identifier.
            aspect_ratio: Override aspect ratio for the model.
            duration_s: Override duration for video models.

        Returns:
            An OptimizedPrompt ready for the provider layer.
        """
        # Normalize model name
        model_key = cls._normalize_model(model)

        # Apply model-specific boosters
        boosted = cls._apply_boosters(positive, model_key)

        # Filter problematic terms
        filtered = cls._apply_filters(boosted, model_key)

        # Build parameters
        params = cls._build_params(model_key, aspect_ratio, duration_s)

        # Handle models that don't support negative prompts
        effective_negative = negative
        if model_key in ("imagen", "veo3", "veo3.1", "nano-banana", "sora-2"):
            effective_negative = ""

        # Build system instruction for LLM-based generation
        system_instruction = ""
        if model_key == "imagen":
            system_instruction = (
                "Generate a photorealistic cinematic image. "
                "Focus on lighting quality, composition, and atmosphere."
            )

        return OptimizedPrompt(
            model=model,
            positive=filtered,
            negative=effective_negative,
            system_instruction=system_instruction,
            parameters=params,
        )

    @classmethod
    def _normalize_model(cls, model: str) -> str:
        """Normalize model name to a known key."""
        model_lower = model.lower().replace("-", "").replace("_", "").replace(" ", "")
        mapping = {
            # Flux family
            "fluxpro": "flux-pro",
            "fluxprov1.1ultra": "flux-ultra",
            "fluxultra": "flux-ultra",
            "flux2flex": "flux-2-flex",
            "fluxkontext": "flux-kontext",
            # Nano Banana / Gemini image
            "nanobanana": "nano-banana",
            "nanobanana2": "nano-banana",
            "nanobananapro": "nano-banana",
            "geminiimage": "nano-banana",
            # Veo
            "veo3": "veo3",
            "veo3.1": "veo3.1",
            "veo31": "veo3.1",
            # Kling
            "kling": "kling",
            "kling3.0": "kling-3.0",
            "kling30": "kling-3.0",
            "klingo3": "kling-o3",
            "kling2.5": "kling-2.5",
            "kling25": "kling-2.5",
            # Others
            "sora2": "sora-2",
            "sora2pro": "sora-2",
            "grokvideo": "grok-video",
            "grokimage": "grok-image",
            "wan2.6": "wan-2.6",
            "wan26": "wan-2.6",
            "imagen": "imagen",
            "imagen4": "imagen",
            "imagen4ultra": "imagen-4-ultra",
            "imagen4fast": "imagen-4-fast",
            "seedance": "seedance",
            "seedance1.5": "seedance",
            "seedance15": "seedance",
            "hunyuan": "hunyuan",
            "ltx2": "ltx-2",
        }
        return mapping.get(model_lower, model)

    @classmethod
    def _apply_boosters(cls, prompt: str, model_key: str) -> str:
        """Add model-specific quality boosters that aren't already present."""
        boosters = cls._MODEL_BOOSTERS.get(model_key, [])
        # Only add boosters not already present in the prompt
        existing_lower = prompt.lower()
        new_boosters = [b for b in boosters if b.lower() not in existing_lower]
        if new_boosters:
            return f"{prompt}, {', '.join(new_boosters)}"
        return prompt

    @classmethod
    def _apply_filters(cls, prompt: str, model_key: str) -> str:
        """Remove terms that don't work well with a specific model."""
        filters = cls._MODEL_FILTERS.get(model_key, [])
        result = prompt
        for term in filters:
            result = result.replace(term, "").replace("  ", " ")
        return result.strip().rstrip(",").strip()

    @classmethod
    def _build_params(
        cls,
        model_key: str,
        aspect_ratio: str | None,
        duration_s: float | None,
    ) -> dict:
        """Build model-specific generation parameters."""
        params = dict(cls._DEFAULT_PARAMS.get(model_key, {}))

        if aspect_ratio:
            # Map cinematic ratios to API-friendly values
            ratio_map = {
                "2.39:1": "landscape_16_9",  # closest standard
                "1.85:1": "landscape_16_9",
                "1.33:1": "square",
                "1:1": "square",
                "16:9": "landscape_16_9",
                "9:16": "portrait_16_9",
                "1.43:1": "square",  # IMAX approximation
            }
            api_ratio = ratio_map.get(aspect_ratio, aspect_ratio)

            if model_key in ("flux-pro", "flux-ultra"):
                params["image_size"] = api_ratio
            elif model_key in ("veo3", "kling", "seedance"):
                # These use "16:9" style ratios
                video_ratio_map = {
                    "landscape_16_9": "16:9",
                    "portrait_16_9": "9:16",
                    "square": "1:1",
                }
                params["aspect_ratio"] = video_ratio_map.get(api_ratio, "16:9")

        if duration_s and model_key in (
            "veo3", "veo3.1", "kling", "kling-3.0", "seedance",
            "sora-2", "grok-video", "wan-2.6", "hunyuan", "ltx-2",
        ):
            params["duration"] = str(int(duration_s))

        return params

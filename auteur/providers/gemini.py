"""Gemini/Imagen provider — Google AI for image + video generation.

Updated March 2026. Three generation pathways:

1. Imagen 4 family — Dedicated image generation via google-genai SDK
   - imagen-4.0-generate-001       (flagship, $0.04/image)
   - imagen-4.0-ultra-generate-001  (highest quality, $0.06/image)
   - imagen-4.0-fast-generate-001   (speed-optimized, $0.02/image)
2. Nano Banana 2 (Gemini 3.1 Flash Image) — Native image gen
   - gemini-3.1-flash-image-preview (conversational editing, multi-image)
3. Veo 3 — Video generation via google-genai SDK
   - veo-3.0-generate-preview       (text/image-to-video, with audio)

Authentication: GEMINI_API_KEY environment variable.
"""

from __future__ import annotations

import base64
from pathlib import Path

from auteur.config import get_settings
from auteur.providers.base import (
    GenerationProvider,
    GenerationRequest,
    GenerationResult,
    GenerationType,
)


# Model ID mapping
_IMAGEN_MODELS: dict[str, str] = {
    "imagen": "imagen-4.0-generate-001",
    "imagen-4": "imagen-4.0-generate-001",
    "imagen-4-ultra": "imagen-4.0-ultra-generate-001",
    "imagen-4-fast": "imagen-4.0-fast-generate-001",
    "imagen-3": "imagen-3.0-generate-002",
}


class GeminiProvider(GenerationProvider):
    """Google Gemini/Imagen generation provider.

    Supports image generation through Imagen 4 (Standard/Ultra/Fast),
    Nano Banana 2 (Gemini 3.1 Flash Image), and video generation via Veo 3.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def supported_models(self) -> list[str]:
        return [
            "imagen", "imagen-4", "imagen-4-ultra", "imagen-4-fast", "imagen-3",
            "gemini-image", "nano-banana",
            "veo3-gemini",
        ]

    @property
    def supported_types(self) -> list[GenerationType]:
        return [GenerationType.IMAGE, GenerationType.VIDEO]

    def is_available(self) -> bool:
        return self._settings.has_gemini

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate via Gemini/Imagen/Veo.

        Routes based on model:
        - imagen* -> Imagen 4 family
        - gemini-image / nano-banana -> Nano Banana 2 (Gemini 3.1 Flash Image)
        - veo3-gemini -> Veo 3 video generation

        Args:
            request: Generation request with optimized prompt.

        Returns:
            GenerationResult with the image path/URL or video URL.
        """
        if not self.is_available():
            return GenerationResult(
                success=False,
                provider=self.name,
                model=request.prompt.model,
                error="GEMINI_API_KEY not configured",
            )

        model_key = request.prompt.model
        try:
            if model_key in _IMAGEN_MODELS:
                return await self._generate_imagen(request)
            elif model_key == "veo3-gemini":
                return await self._generate_veo3(request)
            else:
                return await self._generate_gemini_native(request)
        except Exception as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Gemini error: {e!s}",
            )

    async def _generate_imagen(self, request: GenerationRequest) -> GenerationResult:
        """Generate via Imagen 4 family (Standard, Ultra, Fast)."""
        try:
            from google import genai

            client = genai.Client(api_key=self._settings.gemini_api_key)

            params = request.prompt.parameters
            number_of_images = params.get("number_of_images", 1)

            # Resolve to the correct Imagen model ID
            model_id = _IMAGEN_MODELS.get(
                request.prompt.model, "imagen-4.0-generate-001"
            )

            response = client.models.generate_images(
                model=model_id,
                prompt=request.prompt.positive,
                config=genai.types.GenerateImagesConfig(
                    number_of_images=number_of_images,
                ),
            )

            # Save first image
            if response.generated_images:
                image = response.generated_images[0]
                output_dir = self._settings.auteur_output_dir / "gemini"
                output_dir.mkdir(parents=True, exist_ok=True)

                import time
                filename = f"imagen_{int(time.time())}.png"
                filepath = output_dir / filename
                filepath.write_bytes(image.image.image_bytes)

                return GenerationResult(
                    success=True,
                    provider=self.name,
                    model="imagen-4",
                    generation_type=GenerationType.IMAGE,
                    local_path=filepath,
                    metadata={"number_generated": len(response.generated_images)},
                )

            return GenerationResult(
                success=False,
                provider=self.name,
                model="imagen-4",
                error="No images generated",
            )

        except ImportError:
            return GenerationResult(
                success=False,
                provider=self.name,
                model="imagen-4",
                error="google-genai package not installed. Run: pip install google-genai",
            )

    async def _generate_veo3(self, request: GenerationRequest) -> GenerationResult:
        """Generate video via Veo 3 on Gemini API."""
        try:
            from google import genai

            client = genai.Client(api_key=self._settings.gemini_api_key)

            params = request.prompt.parameters
            duration = params.get("duration", "8s")
            aspect_ratio = params.get("aspect_ratio", "16:9")

            # Veo 3 uses predictLongRunning pattern
            operation = client.models.generate_videos(
                model="veo-3.0-generate-preview",
                prompt=request.prompt.positive,
                config=genai.types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    number_of_videos=1,
                ),
            )

            # Poll for completion
            import asyncio
            import time
            result = operation.result(timeout=600)

            if result.generated_videos:
                video = result.generated_videos[0]
                output_dir = self._settings.auteur_output_dir / "gemini"
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"veo3_{int(time.time())}.mp4"
                filepath = output_dir / filename
                filepath.write_bytes(video.video.video_bytes)

                return GenerationResult(
                    success=True,
                    provider=self.name,
                    model="veo3-gemini",
                    generation_type=GenerationType.VIDEO,
                    local_path=filepath,
                )

            return GenerationResult(
                success=False,
                provider=self.name,
                model="veo3-gemini",
                error="No video generated",
            )

        except ImportError:
            return GenerationResult(
                success=False,
                provider=self.name,
                model="veo3-gemini",
                error="google-genai package not installed. Run: pip install google-genai",
            )

    async def _generate_gemini_native(self, request: GenerationRequest) -> GenerationResult:
        """Generate via Nano Banana 2 (Gemini 3.1 Flash Image)."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self._settings.gemini_api_key)

            # Build the prompt with system instruction
            system_instruction = request.prompt.system_instruction or (
                "Generate a photorealistic cinematic image based on the following description. "
                "Focus on lighting, composition, atmosphere, and cinematic quality."
            )

            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=request.prompt.positive,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )

            # Extract image from response
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        mime = part.inline_data.mime_type
                        if mime and mime.startswith("image/"):
                            output_dir = self._settings.auteur_output_dir / "gemini"
                            output_dir.mkdir(parents=True, exist_ok=True)

                            import time
                            ext = mime.split("/")[-1]
                            filename = f"gemini_{int(time.time())}.{ext}"
                            filepath = output_dir / filename
                            filepath.write_bytes(
                                base64.b64decode(part.inline_data.data)
                                if isinstance(part.inline_data.data, str)
                                else part.inline_data.data
                            )

                            return GenerationResult(
                                success=True,
                                provider=self.name,
                                model="gemini-image",
                                generation_type=GenerationType.IMAGE,
                                local_path=filepath,
                            )

            return GenerationResult(
                success=False,
                provider=self.name,
                model="gemini-image",
                error="No image in Gemini response",
            )

        except ImportError:
            return GenerationResult(
                success=False,
                provider=self.name,
                model="gemini-image",
                error="google-genai package not installed. Run: pip install google-genai",
            )

"""Kie.ai provider — REST API for video + image generation.

Kie.ai provides access to premium generation models through a simple
REST API with Bearer token authentication. Updated March 2026.

Video models: Veo 3.1 (+ Fast), Kling 3.0, Kling 2.5 Turbo, Runway Gen 4
  Turbo + Aleph, Seedance 1.5 Pro, Wan 2.6, Kling 2.6 Motion Control.
Image models: Nano Banana 2/Pro, GPT Image 1.5, Flux Kontext.

Pattern: POST to generate → poll task status → retrieve result URL.
Base URL: https://api.kie.ai/api/v1
"""

from __future__ import annotations

import httpx

from auteur.config import get_settings
from auteur.providers.base import (
    GenerationProvider,
    GenerationRequest,
    GenerationResult,
    GenerationType,
)

KIE_API_BASE = "https://api.kie.ai/api/v1"

# Model → Kie.ai model identifier
_KIE_VIDEO_MODELS: dict[str, str] = {
    # Google Veo
    "veo3": "veo3",
    "veo3-fast": "veo3_fast",
    "veo3.1": "veo3.1",
    "veo3.1-fast": "veo3.1_fast",
    # Kling (Kuaishou)
    "kling-3.0": "kling3.0",
    "kling-2.5": "kling2.5_turbo",
    "kling-2.6-motion": "kling2.6_motion_control",
    # Runway
    "runway-aleph": "runway_aleph",
    "runway-gen4-turbo": "runway_gen4_turbo",
    # ByteDance
    "seedance-1.5": "seedance1.5_pro",
    # Alibaba
    "wan-2.6": "wan2.6",
}

_KIE_IMAGE_MODELS: dict[str, str] = {
    "nano-banana": "nano_banana_2",
    "nano-banana-pro": "nano_banana_pro",
    "gpt-image": "gpt_image_1.5",
    "flux-kontext": "flux_kontext",
}


class KieProvider(GenerationProvider):
    """Kie.ai video + image generation provider.

    Generates video and images through Kie's REST API. Supports text-to-video,
    image-to-video, and text-to-image workflows with multiple model backends.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def name(self) -> str:
        return "kie"

    @property
    def supported_models(self) -> list[str]:
        return list(_KIE_VIDEO_MODELS.keys()) + list(_KIE_IMAGE_MODELS.keys())

    @property
    def supported_types(self) -> list[GenerationType]:
        return [GenerationType.VIDEO, GenerationType.IMAGE_TO_VIDEO, GenerationType.IMAGE]

    def is_available(self) -> bool:
        return self._settings.has_kie

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Submit a generation job to Kie.ai and poll for completion.

        Routes to video or image generation based on model type.

        Args:
            request: Generation request with optimized prompt.

        Returns:
            GenerationResult with the output URL.
        """
        if not self.is_available():
            return GenerationResult(
                success=False,
                provider=self.name,
                model=request.prompt.model,
                error="KIE_API_KEY not configured",
            )

        model_key = request.prompt.model

        # Route to image or video generation
        if model_key in _KIE_IMAGE_MODELS:
            return await self._generate_image(request, model_key)

        kie_model = _KIE_VIDEO_MODELS.get(model_key)
        if not kie_model:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Unknown Kie model: {model_key}",
            )

        payload = self._build_payload(request, kie_model)

        try:
            async with httpx.AsyncClient(timeout=600) as client:
                # Submit generation request
                resp = await client.post(
                    f"{KIE_API_BASE}/video/generate",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()

                task_id = data.get("data", {}).get("task_id", "")
                if not task_id:
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        model=model_key,
                        error=f"No task_id in response: {data}",
                    )

                # Poll for completion
                import asyncio
                for _ in range(180):  # 15 minutes max for video gen
                    status_resp = await client.get(
                        f"{KIE_API_BASE}/task/{task_id}",
                        headers=self._headers(),
                    )
                    status_data = status_resp.json()
                    task_info = status_data.get("data", {})
                    status = task_info.get("status", "")

                    if status == "completed":
                        video_url = task_info.get("output", {}).get("video_url", "")
                        return GenerationResult(
                            success=bool(video_url),
                            provider=self.name,
                            model=model_key,
                            generation_type=request.generation_type,
                            url=video_url,
                            metadata=task_info,
                        )
                    elif status == "failed":
                        return GenerationResult(
                            success=False,
                            provider=self.name,
                            model=model_key,
                            error=f"Kie task failed: {task_info.get('error', 'unknown')}",
                        )

                    await asyncio.sleep(5)

                return GenerationResult(
                    success=False,
                    provider=self.name,
                    model=model_key,
                    error="Kie task timed out after 15 minutes",
                )

        except httpx.HTTPStatusError as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Kie HTTP error: {e.response.status_code} {e.response.text[:200]}",
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Kie error: {e!s}",
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.kie_api_key}",
            "Content-Type": "application/json",
        }

    async def _generate_image(self, request: GenerationRequest, model_key: str) -> GenerationResult:
        """Generate an image via Kie.ai image models."""
        kie_model = _KIE_IMAGE_MODELS[model_key]
        payload = {
            "model": kie_model,
            "prompt": request.prompt.positive,
        }
        params = request.prompt.parameters
        if "aspect_ratio" in params:
            payload["aspect_ratio"] = params["aspect_ratio"]

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{KIE_API_BASE}/image/generate",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()

                task_id = data.get("data", {}).get("task_id", "")
                if not task_id:
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        model=model_key,
                        error=f"No task_id in response: {data}",
                    )

                import asyncio
                for _ in range(60):  # 5 minutes max for image
                    status_resp = await client.get(
                        f"{KIE_API_BASE}/task/{task_id}",
                        headers=self._headers(),
                    )
                    status_data = status_resp.json()
                    task_info = status_data.get("data", {})
                    status = task_info.get("status", "")

                    if status == "completed":
                        image_url = task_info.get("output", {}).get("image_url", "")
                        return GenerationResult(
                            success=bool(image_url),
                            provider=self.name,
                            model=model_key,
                            generation_type=GenerationType.IMAGE,
                            url=image_url,
                            metadata=task_info,
                        )
                    elif status == "failed":
                        return GenerationResult(
                            success=False,
                            provider=self.name,
                            model=model_key,
                            error=f"Kie image task failed: {task_info.get('error', 'unknown')}",
                        )

                    await asyncio.sleep(3)

                return GenerationResult(
                    success=False,
                    provider=self.name,
                    model=model_key,
                    error="Kie image task timed out after 5 minutes",
                )
        except Exception as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Kie error: {e!s}",
            )

    def _build_payload(self, request: GenerationRequest, kie_model: str) -> dict:
        """Build Kie.ai video request payload."""
        payload: dict = {
            "model": kie_model,
            "prompt": request.prompt.positive,
        }

        # Duration and aspect ratio from prompt parameters
        params = request.prompt.parameters
        if "duration" in params:
            payload["duration"] = params["duration"]
        if "aspect_ratio" in params:
            payload["aspect_ratio"] = params["aspect_ratio"]

        # Image-to-video
        if request.source_image_url:
            payload["image_url"] = request.source_image_url

        return payload

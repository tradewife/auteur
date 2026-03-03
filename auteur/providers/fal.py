"""FAL.ai provider — queue-based generation via the FAL unified API.

FAL provides access to 1000+ models through a unified API. Key endpoints
for AUTEUR (updated March 2026):

Image generation:
  - fal-ai/flux-pro/v1.1-ultra     (Flux Pro, best quality)
  - fal-ai/flux-2-flex              (Flux 2 Flex, enhanced text rendering)
  - fal-ai/nano-banana-2            (Gemini 3.1 Flash Image, fast + quality)
  - fal-ai/nano-banana-pro          (Nano Banana Pro, 2K + 4K upscale)
  - fal-ai/grok-imagine-image       (xAI Grok, aesthetic)
  - fal-ai/recraft/v4/pro/text-to-image (Recraft V4 Pro)

Video generation:
  - fal-ai/veo3                     (Google Veo 3, with audio)
  - fal-ai/veo3.1                   (Google Veo 3.1, extended + multi-ref)
  - fal-ai/kling-video/v3/pro       (Kling 3.0 Pro, cinematic + audio)
  - fal-ai/kling-o3                 (Kling O3, start/end frame control)
  - fal-ai/sora-2-pro               (OpenAI Sora 2 Pro, with audio)
  - fal-ai/grok-imagine-video       (xAI Grok video)
  - fal-ai/ltx-2-19b                (LTX-2 19B, video + audio from images)
  - fal-ai/wan-2.6                  (Alibaba Wan 2.6, multi-shot + audio)
  - fal-ai/seedance-1.5-pro         (ByteDance Seedance 1.5 Pro)
  - fal-ai/hunyuan-video            (Tencent Hunyuan)

Authentication: FAL_KEY environment variable.
Pattern: queue-based — submit, poll, retrieve.
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


# FAL endpoint mappings — model name → FAL endpoint path
_FAL_ENDPOINTS: dict[str, str] = {
    # ── Image generation ────────────────────────────────────────────
    "flux-pro": "fal-ai/flux-pro/v1.1-ultra",
    "flux-ultra": "fal-ai/flux-pro/v1.1-ultra",
    "flux-2-flex": "fal-ai/flux-2-flex",
    "flux-schnell": "fal-ai/flux/schnell",
    "flux-dev": "fal-ai/flux/dev",
    "flux-kontext": "fal-ai/flux-kontext",
    "nano-banana": "fal-ai/nano-banana-2",
    "nano-banana-pro": "fal-ai/nano-banana-pro",
    "grok-image": "fal-ai/grok-imagine-image",
    "recraft-v4": "fal-ai/recraft/v4/pro/text-to-image",
    "seedream": "fal-ai/bytedance/seedream/v5/lite/text-to-image",
    # ── Text-to-video ───────────────────────────────────────────────
    "veo3": "fal-ai/veo3",
    "veo3.1": "fal-ai/veo3.1",
    "kling": "fal-ai/kling-video/v3/pro",
    "kling-3.0": "fal-ai/kling-video/v3/pro",
    "kling-o3": "fal-ai/kling-o3",
    "sora-2": "fal-ai/sora-2-pro",
    "grok-video": "fal-ai/grok-imagine-video",
    "wan-2.6": "fal-ai/wan-2.6",
    "seedance": "fal-ai/seedance-1.5-pro",
    "seedance-1.5": "fal-ai/seedance-1.5-pro",
    "hunyuan": "fal-ai/hunyuan-video",
    "ltx-2": "fal-ai/ltx-2-19b",
    "cosmos": "fal-ai/cosmos-predict-2.5/text-to-video",
    # ── Image-to-video ──────────────────────────────────────────────
    "veo3-i2v": "fal-ai/veo3/image-to-video",
    "veo3.1-i2v": "fal-ai/veo3.1/image-to-video",
    "kling-i2v": "fal-ai/kling-video/v3/pro/image-to-video",
    "kling-o3-i2v": "fal-ai/kling-o3/image-to-video",
    "sora-2-i2v": "fal-ai/sora-2-pro/image-to-video",
    "grok-video-i2v": "fal-ai/grok-imagine-video/image-to-video",
    "ltx-2-i2v": "fal-ai/ltx-2-19b/image-to-video",
    "svd": "fal-ai/stable-video-diffusion",
}

FAL_API_BASE = "https://queue.fal.run"


class FalProvider(GenerationProvider):
    """FAL.ai generation provider.

    Uses FAL's queue-based API: submit a request, receive a request_id,
    then poll or subscribe for the result.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def name(self) -> str:
        return "fal"

    @property
    def supported_models(self) -> list[str]:
        return list(_FAL_ENDPOINTS.keys())

    @property
    def supported_types(self) -> list[GenerationType]:
        return [GenerationType.IMAGE, GenerationType.VIDEO, GenerationType.IMAGE_TO_VIDEO]

    def is_available(self) -> bool:
        return self._settings.has_fal

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Submit a generation job to FAL and poll for completion.

        Args:
            request: Generation request with optimized prompt and parameters.

        Returns:
            GenerationResult with the URL of the generated asset.
        """
        if not self.is_available():
            return GenerationResult(
                success=False,
                provider=self.name,
                model=request.prompt.model,
                error="FAL_KEY not configured",
            )

        model_key = request.prompt.model
        endpoint = _FAL_ENDPOINTS.get(model_key)
        if not endpoint:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Unknown FAL model: {model_key}",
            )

        # Build the payload from the optimized prompt
        payload = self._build_payload(request)
        url = f"{FAL_API_BASE}/{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                # Submit to queue
                submit_resp = await client.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                )
                submit_resp.raise_for_status()
                submit_data = submit_resp.json()

                # If we got a direct result (synchronous models)
                if "images" in submit_data or "video" in submit_data:
                    return self._parse_result(submit_data, model_key, request.generation_type)

                # Otherwise, poll the status URL
                request_id = submit_data.get("request_id", "")
                status_url = submit_data.get("status_url", f"{url}/requests/{request_id}/status")
                result_url = submit_data.get("response_url", f"{url}/requests/{request_id}")

                # Poll for completion
                import asyncio
                for _ in range(120):  # 10 minutes max
                    status_resp = await client.get(status_url, headers=self._headers())
                    status_data = status_resp.json()
                    status = status_data.get("status", "")

                    if status == "COMPLETED":
                        result_resp = await client.get(result_url, headers=self._headers())
                        result_resp.raise_for_status()
                        return self._parse_result(
                            result_resp.json(), model_key, request.generation_type
                        )
                    elif status in ("FAILED", "CANCELLED"):
                        return GenerationResult(
                            success=False,
                            provider=self.name,
                            model=model_key,
                            error=f"FAL job {status}: {status_data.get('error', 'unknown')}",
                        )

                    await asyncio.sleep(5)

                return GenerationResult(
                    success=False,
                    provider=self.name,
                    model=model_key,
                    error="FAL job timed out after 10 minutes",
                )

        except httpx.HTTPStatusError as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"FAL HTTP error: {e.response.status_code} {e.response.text[:200]}",
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"FAL error: {e!s}",
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Key {self._settings.fal_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, request: GenerationRequest) -> dict:
        """Build the FAL-specific request payload."""
        prompt = request.prompt
        payload: dict = {
            "prompt": prompt.positive,
            **prompt.parameters,
        }

        if prompt.negative:
            payload["negative_prompt"] = prompt.negative

        if request.seed is not None:
            payload["seed"] = request.seed

        if request.source_image_url:
            payload["image_url"] = request.source_image_url

        if request.width and request.height:
            payload["image_size"] = {
                "width": request.width,
                "height": request.height,
            }

        return payload

    def _parse_result(
        self, data: dict, model: str, gen_type: GenerationType
    ) -> GenerationResult:
        """Parse FAL response data into a GenerationResult."""
        url = ""
        seed = None

        if gen_type == GenerationType.IMAGE:
            images = data.get("images", [])
            if images:
                url = images[0].get("url", "")
            seed = data.get("seed")
        else:
            video = data.get("video", {})
            url = video.get("url", "") if isinstance(video, dict) else str(video)

        return GenerationResult(
            success=bool(url),
            provider=self.name,
            model=model,
            generation_type=gen_type,
            url=url,
            seed=seed,
            metadata=data,
        )

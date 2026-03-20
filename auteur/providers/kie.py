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

import json

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
    # Kie docs use slash-suffixed model names for current market APIs.
    "kling-3.0": "kling-3.0/video",
    "kling-2.5": "kling/v2-5-turbo-text-to-video",
    "kling-2.6-motion": "kling-2.6/motion-control",
    # Runway
    "runway-aleph": "runway_aleph",
    "runway-gen4-turbo": "runway_gen4_turbo",
    # ByteDance
    "seedance-1.5": "seedance1.5_pro",
    # Alibaba
    "wan-2.6": "wan2.6",
}

_KIE_IMAGE_MODELS: dict[str, str] = {
    # Current Kie market image model names use hyphens, not underscores.
    "nano-banana": "nano-banana-2",
    "nano-banana-pro": "nano-banana-pro",
    "gpt-image": "gpt-image/1.5-text-to-image",
    "flux-kontext": "flux-kontext",
}


def _extract_task_id(data: dict) -> str:
    payload = data.get("data") or {}
    if not isinstance(payload, dict):
        return ""
    return payload.get("taskId", "") or payload.get("task_id", "")


def _parse_result_urls(result_json: str | dict) -> list[str]:
    parsed: dict = {}
    if isinstance(result_json, str):
        try:
            parsed = json.loads(result_json) if result_json else {}
        except json.JSONDecodeError:
            parsed = {}
    elif isinstance(result_json, dict):
        parsed = result_json
    urls = parsed.get("resultUrls", []) if isinstance(parsed, dict) else []
    return urls if isinstance(urls, list) else []


def _error_message(data: dict) -> str:
    code = data.get("code")
    msg = data.get("msg", "")
    return f"code={code} msg={msg}" if code is not None else str(data)


def _poll_state(task_info: dict, status_data: dict) -> str:
    return task_info.get("state", "") or task_info.get("status", "") or status_data.get("status", "")


def _is_kling_video_model(kie_model: str) -> bool:
    return kie_model == "kling-3.0/video"


def _build_kling_video_input(request: GenerationRequest) -> dict:
    params = request.prompt.parameters
    input_payload: dict = {
        "prompt": request.prompt.positive,
        "sound": bool(params.get("sound", False)),
        "duration": str(params.get("duration", "5")).rstrip("s"),
        "aspect_ratio": params.get("aspect_ratio", "16:9"),
        "mode": params.get("mode", "pro"),
        "multi_shots": False,
        "multi_prompt": [],
    }
    if request.source_image_url:
        input_payload["image_urls"] = [request.source_image_url]
    return input_payload


def _build_generic_video_input(request: GenerationRequest) -> dict:
    params = request.prompt.parameters
    input_payload: dict = {
        "prompt": request.prompt.positive,
    }
    if "duration" in params:
        input_payload["duration"] = str(params["duration"]).rstrip("s")
    if "aspect_ratio" in params:
        input_payload["aspect_ratio"] = params["aspect_ratio"]
    if request.source_image_url:
        input_payload["image_urls"] = [request.source_image_url]
    return input_payload


def _build_video_payload(request: GenerationRequest, kie_model: str) -> dict:
    input_payload = _build_kling_video_input(request) if _is_kling_video_model(kie_model) else _build_generic_video_input(request)
    payload: dict = {
        "model": kie_model,
        "input": input_payload,
    }
    callback_url = request.prompt.parameters.get("callback_url")
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def _build_image_payload(request: GenerationRequest, kie_model: str, model_key: str) -> dict:
    input_payload: dict[str, str] = {"prompt": request.prompt.positive}
    params = request.prompt.parameters
    if "aspect_ratio" in params:
        input_payload["aspect_ratio"] = params["aspect_ratio"]
    if model_key == "gpt-image":
        input_payload.setdefault("aspect_ratio", "1:1")
        input_payload.setdefault("quality", "medium")
    return {
        "model": kie_model,
        "input": input_payload,
    }


def _result_from_task_info(provider: str, model_key: str, generation_type: GenerationType, task_info: dict) -> GenerationResult:
    urls = _parse_result_urls(task_info.get("resultJson", ""))
    asset_url = urls[0] if urls else ""
    return GenerationResult(
        success=bool(asset_url),
        provider=provider,
        model=model_key,
        generation_type=generation_type,
        url=asset_url,
        metadata=task_info,
        error="" if asset_url else f"Task succeeded but no result URL found: {task_info}",
    )


def _failed_result(provider: str, model_key: str, message: str, generation_type: GenerationType | None = None) -> GenerationResult:
    kwargs = {
        "success": False,
        "provider": provider,
        "model": model_key,
        "error": message,
    }
    if generation_type is not None:
        kwargs["generation_type"] = generation_type
    return GenerationResult(**kwargs)


def _task_failed_message(task_info: dict) -> str:
    return task_info.get("failMsg") or task_info.get("error") or task_info.get("failCode") or "unknown"


def _task_timeout_message(kind: str) -> str:
    return f"Kie {kind} task timed out"


def _request_error_message(prefix: str, response_text: str) -> str:
    return f"{prefix}: {response_text[:300]}"


def _safe_json(resp: httpx.Response) -> dict:
    try:
        data = resp.json()
        return data if isinstance(data, dict) else {"raw": data}
    except Exception:
        return {"raw_text": resp.text}


def _ensure_ok(data: dict) -> tuple[bool, str]:
    code = data.get("code")
    return (code == 200, _error_message(data))


def _status_done(state: str) -> bool:
    return state in {"success", "fail", "completed", "failed"}


def _status_success(state: str) -> bool:
    return state in {"success", "completed"}


def _status_failed(state: str) -> bool:
    return state in {"fail", "failed"}


def _poll_interval_seconds(generation_type: GenerationType) -> int:
    return 5 if generation_type != GenerationType.IMAGE else 3


def _poll_attempts(generation_type: GenerationType) -> int:
    return 180 if generation_type != GenerationType.IMAGE else 60


def _submit_endpoint(generation_type: GenerationType) -> str:
    return f"{KIE_API_BASE}/jobs/createTask"


def _status_endpoint() -> str:
    return f"{KIE_API_BASE}/jobs/recordInfo"


def _task_id_missing_message(data: dict) -> str:
    return f"No taskId in response: {data}"


def _unexpected_http_error(e: httpx.HTTPStatusError) -> str:
    return f"Kie HTTP error: {e.response.status_code} {e.response.text[:200]}"


def _unexpected_error(e: Exception) -> str:
    return f"Kie error: {e!s}"


def _build_payload(request: GenerationRequest, kie_model: str, model_key: str) -> dict:
    if model_key in _KIE_IMAGE_MODELS:
        return _build_image_payload(request, kie_model, model_key)
    return _build_video_payload(request, kie_model)


def _result_kind(generation_type: GenerationType) -> str:
    return "image" if generation_type == GenerationType.IMAGE else "video"


def _video_generation_type(request: GenerationRequest) -> GenerationType:
    return request.generation_type if request.generation_type != GenerationType.IMAGE else GenerationType.VIDEO


def _normalized_generation_type(request: GenerationRequest, model_key: str) -> GenerationType:
    if model_key in _KIE_IMAGE_MODELS:
        return GenerationType.IMAGE
    return _video_generation_type(request)


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

        Routes to image or video generation based on model type and uses the
        current Market API contract documented by Kie.ai.
        """
        if not self.is_available():
            return _failed_result(self.name, request.prompt.model, "KIE_API_KEY not configured")

        model_key = request.prompt.model
        generation_type = _normalized_generation_type(request, model_key)
        model_map = _KIE_IMAGE_MODELS if model_key in _KIE_IMAGE_MODELS else _KIE_VIDEO_MODELS
        kie_model = model_map.get(model_key)
        if not kie_model:
            return _failed_result(self.name, model_key, f"Unknown Kie model: {model_key}", generation_type)

        payload = _build_payload(request, kie_model, model_key)

        try:
            async with httpx.AsyncClient(timeout=600) as client:
                resp = await client.post(
                    _submit_endpoint(generation_type),
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = _safe_json(resp)
                ok, message = _ensure_ok(data)
                if not ok:
                    return _failed_result(self.name, model_key, message, generation_type)

                task_id = _extract_task_id(data)
                if not task_id:
                    return _failed_result(self.name, model_key, _task_id_missing_message(data), generation_type)

                import asyncio
                for _ in range(_poll_attempts(generation_type)):
                    status_resp = await client.get(
                        _status_endpoint(),
                        params={"taskId": task_id},
                        headers=self._headers(),
                    )
                    status_resp.raise_for_status()
                    status_data = _safe_json(status_resp)
                    task_info = status_data.get("data") or {}
                    if not isinstance(task_info, dict):
                        task_info = {}
                    state = _poll_state(task_info, status_data)

                    if _status_success(state):
                        return _result_from_task_info(self.name, model_key, generation_type, task_info)
                    if _status_failed(state):
                        return _failed_result(self.name, model_key, f"Kie task failed: {_task_failed_message(task_info)}", generation_type)

                    await asyncio.sleep(_poll_interval_seconds(generation_type))

                return _failed_result(self.name, model_key, _task_timeout_message(_result_kind(generation_type)), generation_type)

        except httpx.HTTPStatusError as e:
            return _failed_result(self.name, model_key, _unexpected_http_error(e), generation_type)
        except Exception as e:
            return _failed_result(self.name, model_key, _unexpected_error(e), generation_type)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.kie_api_key}",
            "Content-Type": "application/json",
        }


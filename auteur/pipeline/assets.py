"""Asset manager — tracks generated assets, handles downloads and output organization.

Every generation in AUTEUR produces an asset that needs to be tracked:
URL, local path, metadata, prompt used, provider, etc. The asset manager
provides a central registry for all generated content.
"""

from __future__ import annotations

import time
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from auteur.config import get_settings
from auteur.providers.base import GenerationResult, GenerationType


class Asset(BaseModel):
    """A tracked generated asset."""

    id: str = Field(description="Unique asset identifier")
    created_at: float = Field(default_factory=time.time)
    generation_type: GenerationType = Field(default=GenerationType.IMAGE)
    provider: str = Field(default="")
    model: str = Field(default="")
    prompt_positive: str = Field(default="")
    prompt_negative: str = Field(default="")
    url: str = Field(default="")
    local_path: Path | None = Field(default=None)
    seed: int | None = Field(default=None)
    metadata: dict = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    sequence_id: str = Field(default="", description="Parent sequence if part of one")
    shot_index: int = Field(default=0, description="Position in sequence")


class AssetManager:
    """Manages the lifecycle of generated assets.

    Handles:
    - Asset registration from GenerationResults
    - Downloading remote assets to local storage
    - Organizing output directory structure
    - Asset metadata persistence
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        self._settings = get_settings()
        self._output_dir = output_dir or self._settings.auteur_output_dir
        self._assets: dict[str, Asset] = {}
        self._counter = 0

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    @property
    def assets(self) -> dict[str, Asset]:
        return dict(self._assets)

    def register(
        self,
        result: GenerationResult,
        *,
        prompt_positive: str = "",
        prompt_negative: str = "",
        sequence_id: str = "",
        shot_index: int = 0,
        tags: list[str] | None = None,
    ) -> Asset:
        """Register a generation result as a tracked asset.

        Args:
            result: The GenerationResult from a provider.
            prompt_positive: The positive prompt used.
            prompt_negative: The negative prompt used.
            sequence_id: Parent sequence ID if applicable.
            shot_index: Position in sequence.
            tags: Optional tags for organization.

        Returns:
            The registered Asset.
        """
        self._counter += 1
        asset_id = f"asset_{self._counter:04d}_{int(time.time())}"

        asset = Asset(
            id=asset_id,
            generation_type=result.generation_type,
            provider=result.provider,
            model=result.model,
            prompt_positive=prompt_positive,
            prompt_negative=prompt_negative,
            url=result.url,
            local_path=result.local_path,
            seed=result.seed,
            metadata=result.metadata,
            tags=tags or [],
            sequence_id=sequence_id,
            shot_index=shot_index,
        )

        self._assets[asset_id] = asset
        return asset

    async def download(self, asset: Asset) -> Path:
        """Download a remote asset to local storage.

        Args:
            asset: The asset to download.

        Returns:
            Local path to the downloaded file.
        """
        if asset.local_path and asset.local_path.exists():
            return asset.local_path

        if not asset.url:
            raise ValueError(f"Asset {asset.id} has no URL to download")

        # Determine output subdirectory
        subdir = self._output_dir / asset.provider / asset.model
        subdir.mkdir(parents=True, exist_ok=True)

        # Determine file extension from URL
        ext = _guess_extension(asset.url, asset.generation_type)
        filename = f"{asset.id}{ext}"
        filepath = subdir / filename

        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.get(asset.url)
            resp.raise_for_status()
            filepath.write_bytes(resp.content)

        asset.local_path = filepath
        return filepath

    async def download_all(self) -> list[Path]:
        """Download all remote assets that haven't been downloaded yet."""
        paths = []
        for asset in self._assets.values():
            if asset.url and (not asset.local_path or not asset.local_path.exists()):
                path = await self.download(asset)
                paths.append(path)
        return paths

    def get_by_sequence(self, sequence_id: str) -> list[Asset]:
        """Get all assets belonging to a sequence, ordered by shot index."""
        assets = [a for a in self._assets.values() if a.sequence_id == sequence_id]
        return sorted(assets, key=lambda a: a.shot_index)

    def get_by_tag(self, tag: str) -> list[Asset]:
        """Get all assets with a specific tag."""
        return [a for a in self._assets.values() if tag in a.tags]

    def summary(self) -> dict:
        """Get a summary of all tracked assets."""
        by_type = {}
        by_provider = {}
        for asset in self._assets.values():
            by_type[asset.generation_type.value] = by_type.get(asset.generation_type.value, 0) + 1
            by_provider[asset.provider] = by_provider.get(asset.provider, 0) + 1

        return {
            "total": len(self._assets),
            "by_type": by_type,
            "by_provider": by_provider,
            "output_dir": str(self._output_dir),
        }


def _guess_extension(url: str, gen_type: GenerationType) -> str:
    """Guess file extension from URL and generation type."""
    url_lower = url.lower().split("?")[0]
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm", ".gif"):
        if url_lower.endswith(ext):
            return ext

    if gen_type in (GenerationType.VIDEO, GenerationType.IMAGE_TO_VIDEO):
        return ".mp4"
    return ".png"

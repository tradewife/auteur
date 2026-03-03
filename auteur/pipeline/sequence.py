"""Sequence pipeline — orchestrates multi-shot sequence generation.

A sequence is an ordered collection of shots that tell a visual story.
The sequence pipeline manages the generation of all shots, maintaining
visual coherence across the sequence through shared style profiles,
color palettes, and seed management.
"""

from __future__ import annotations

import time
import uuid

from pydantic import BaseModel, Field

from auteur.knowledge.ontology import ShotSpec
from auteur.pipeline.assets import AssetManager
from auteur.pipeline.shot import ShotPipeline, ShotResult
from auteur.providers.registry import ProviderRegistry


class SequenceSpec(BaseModel):
    """Specification for a multi-shot sequence."""

    name: str = Field(description="Sequence name / identifier")
    description: str = Field(default="", description="Overall sequence description")
    shots: list[ShotSpec] = Field(default_factory=list)
    shared_style: str = Field(
        default="",
        description="DP style profile to apply to all shots (can be overridden per-shot)",
    )
    shared_seed: int | None = Field(
        default=None,
        description="Shared seed for visual consistency (each shot offsets from this)",
    )


class SequenceResult:
    """The result of a sequence pipeline execution."""

    def __init__(
        self,
        spec: SequenceSpec,
        sequence_id: str,
        shot_results: list[ShotResult],
    ) -> None:
        self.spec = spec
        self.sequence_id = sequence_id
        self.shot_results = shot_results

    @property
    def success(self) -> bool:
        return all(r.success for r in self.shot_results)

    @property
    def partial_success(self) -> bool:
        return any(r.success for r in self.shot_results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.shot_results if r.success)

    @property
    def total_count(self) -> int:
        return len(self.shot_results)

    def summary(self) -> dict:
        return {
            "sequence_id": self.sequence_id,
            "name": self.spec.name,
            "total_shots": self.total_count,
            "successful": self.success_count,
            "failed": self.total_count - self.success_count,
        }


class SequencePipeline:
    """Orchestrates generation of multi-shot sequences.

    Handles:
    - Applying shared style/settings across shots
    - Seed management for visual consistency
    - Sequential generation with progress tracking
    - Asset organization by sequence
    """

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self._registry = registry or ProviderRegistry()
        self._assets = asset_manager or AssetManager()
        self._shot_pipeline = ShotPipeline(
            registry=self._registry,
            asset_manager=self._assets,
        )

    @property
    def asset_manager(self) -> AssetManager:
        return self._assets

    async def execute(
        self,
        spec: SequenceSpec,
        *,
        download: bool = False,
        on_shot_complete: callable | None = None,
    ) -> SequenceResult:
        """Execute a full sequence generation.

        Args:
            spec: The sequence specification with all shots.
            download: Whether to download all assets to local storage.
            on_shot_complete: Optional callback(shot_index, shot_result) for progress.

        Returns:
            SequenceResult with all shot results.
        """
        sequence_id = f"seq_{uuid.uuid4().hex[:8]}_{int(time.time())}"

        # Apply shared settings to shots
        prepared_shots = self._prepare_shots(spec)

        shot_results: list[ShotResult] = []
        for idx, shot_spec in enumerate(prepared_shots):
            result = await self._shot_pipeline.execute(
                shot_spec,
                sequence_id=sequence_id,
                shot_index=idx,
                download=download,
            )
            shot_results.append(result)

            if on_shot_complete:
                on_shot_complete(idx, result)

        return SequenceResult(
            spec=spec,
            sequence_id=sequence_id,
            shot_results=shot_results,
        )

    def _prepare_shots(self, spec: SequenceSpec) -> list[ShotSpec]:
        """Apply shared sequence settings to individual shots."""
        prepared = []
        for idx, shot in enumerate(spec.shots):
            # Deep copy via model reconstruction
            data = shot.model_dump()

            # Apply shared style if shot doesn't have its own
            if not data.get("style_profile") and spec.shared_style:
                data["style_profile"] = spec.shared_style

            # Apply seed with offset for consistency-with-variation
            if spec.shared_seed is not None and data.get("seed") is None:
                data["seed"] = spec.shared_seed + idx

            prepared.append(ShotSpec(**data))

        return prepared

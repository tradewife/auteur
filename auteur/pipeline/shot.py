"""Shot pipeline — generates a single shot from ShotSpec.

The shot pipeline is the core generation workflow:
  ShotSpec → Compose → Optimize → Generate (image) → Optionally Animate (video)

This is the atomic unit of the AUTEUR pipeline.
"""

from __future__ import annotations

from auteur.knowledge.ontology import ShotSpec
from auteur.pipeline.assets import Asset, AssetManager
from auteur.prompt.composer import PromptComposer, ComposedPrompt
from auteur.providers.base import GenerationRequest, GenerationResult, GenerationType
from auteur.providers.registry import ProviderRegistry


class ShotResult:
    """The result of a shot pipeline execution."""

    def __init__(
        self,
        spec: ShotSpec,
        composed: ComposedPrompt,
        image_result: GenerationResult | None = None,
        video_result: GenerationResult | None = None,
        image_asset: Asset | None = None,
        video_asset: Asset | None = None,
    ) -> None:
        self.spec = spec
        self.composed = composed
        self.image_result = image_result
        self.video_result = video_result
        self.image_asset = image_asset
        self.video_asset = video_asset

    @property
    def success(self) -> bool:
        if self.spec.animate:
            return bool(self.video_result and self.video_result.success)
        return bool(self.image_result and self.image_result.success)

    @property
    def primary_asset(self) -> Asset | None:
        if self.spec.animate and self.video_asset:
            return self.video_asset
        return self.image_asset


class ShotPipeline:
    """Executes the complete shot generation workflow.

    Pipeline flow:
    1. Compose: ShotSpec → ComposedPrompt (via PromptComposer)
    2. Optimize: ComposedPrompt → OptimizedPrompt (model-specific)
    3. Generate image: OptimizedPrompt → GenerationResult
    4. (Optional) Animate: image → video via image-to-video model
    5. Register assets with AssetManager
    """

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self._registry = registry or ProviderRegistry()
        self._assets = asset_manager or AssetManager()

    @property
    def asset_manager(self) -> AssetManager:
        return self._assets

    async def execute(
        self,
        spec: ShotSpec,
        *,
        sequence_id: str = "",
        shot_index: int = 0,
        download: bool = False,
    ) -> ShotResult:
        """Execute the full shot generation pipeline.

        Args:
            spec: Complete shot specification.
            sequence_id: Parent sequence ID if part of a sequence.
            shot_index: Position in sequence.
            download: Whether to download assets to local storage.

        Returns:
            ShotResult with all generation results and tracked assets.
        """
        # Step 1: Compose prompt from spec
        composed = PromptComposer.compose(spec)

        # Step 2: Optimize for target model
        model = spec.target_model or "flux-pro"
        optimized = composed.optimize(model=model)

        # Step 3: Generate image
        image_request = GenerationRequest(
            prompt=optimized,
            generation_type=GenerationType.IMAGE,
            seed=spec.seed,
        )
        image_result = await self._registry.generate(image_request)

        # Register image asset
        image_asset = None
        if image_result.success:
            image_asset = self._assets.register(
                image_result,
                prompt_positive=composed.positive,
                prompt_negative=composed.negative,
                sequence_id=sequence_id,
                shot_index=shot_index,
                tags=["image", model],
            )
            if download:
                await self._assets.download(image_asset)

        # Step 4: Optional animation
        video_result = None
        video_asset = None
        if spec.animate and image_result.success and image_result.url:
            video_result, video_asset = await self._animate(
                image_url=image_result.url,
                spec=spec,
                composed=composed,
                sequence_id=sequence_id,
                shot_index=shot_index,
                download=download,
            )

        return ShotResult(
            spec=spec,
            composed=composed,
            image_result=image_result,
            video_result=video_result,
            image_asset=image_asset,
            video_asset=video_asset,
        )

    async def _animate(
        self,
        image_url: str,
        spec: ShotSpec,
        composed: ComposedPrompt,
        sequence_id: str,
        shot_index: int,
        download: bool,
    ) -> tuple[GenerationResult | None, Asset | None]:
        """Animate an image into video via image-to-video.

        Uses the movement spec to determine the animation model and parameters.
        """
        # Choose an animation model — prefer Kling for i2v, fall back to SVD
        animation_models = ["kling-i2v", "veo3-i2v", "svd"]
        optimized = composed.optimize(model=animation_models[0])

        # Override duration
        optimized.parameters["duration"] = str(int(spec.animation_duration_s))

        video_request = GenerationRequest(
            prompt=optimized,
            generation_type=GenerationType.IMAGE_TO_VIDEO,
            source_image_url=image_url,
            seed=spec.seed,
        )

        video_result = await self._registry.generate(video_request)

        video_asset = None
        if video_result.success:
            video_asset = self._assets.register(
                video_result,
                prompt_positive=composed.positive,
                prompt_negative=composed.negative,
                sequence_id=sequence_id,
                shot_index=shot_index,
                tags=["video", "animated"],
            )
            if download:
                await self._assets.download(video_asset)

        return video_result, video_asset

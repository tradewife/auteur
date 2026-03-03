"""Generation pipeline — orchestrates shot generation from spec to asset."""

from auteur.pipeline.shot import ShotPipeline
from auteur.pipeline.sequence import SequencePipeline
from auteur.pipeline.assets import AssetManager

__all__ = ["ShotPipeline", "SequencePipeline", "AssetManager"]

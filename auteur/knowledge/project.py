"""Project model — structured state for multi-shot film projects.

A Project is the top-level container for an autonomous film generation workflow:
  Brief → VisualLanguage → Scenes → Shots

This is the shared state that the MCP server exposes as resources and
that tools mutate during the conversational planning process.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum

from pydantic import BaseModel, Field

from auteur.knowledge.ontology import ShotSpec, AspectRatio


class ProjectStatus(str, Enum):
    """Project lifecycle status."""

    BRIEF = "brief"  # Initial intent captured
    PLANNING = "planning"  # Visual language + scenes being designed
    SHOT_DESIGN = "shot_design"  # Individual shots being composed
    GENERATION = "generation"  # Generating assets
    REVIEW = "review"  # Reviewing / critiquing outputs
    COMPLETE = "complete"


class Brief(BaseModel):
    """The user's creative intent — the seed of everything.

    A brief captures WHAT the user wants without dictating HOW.
    The agents translate brief → visual language → shots.
    """

    logline: str = Field(description="One-sentence summary of the film/sequence")
    description: str = Field(default="", description="Expanded creative intent")
    mood: str = Field(default="", description="Emotional tone (e.g., 'melancholy', 'tense', 'triumphant')")
    duration_seconds: int = Field(default=30, description="Target duration in seconds")
    references: list[str] = Field(
        default_factory=list,
        description="Reference films, scenes, or visual inspirations",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Hard constraints (e.g., 'no dialogue', 'night only', 'single location')",
    )
    themes: list[str] = Field(default_factory=list, description="Key themes to explore")


class VisualLanguage(BaseModel):
    """Locked global style choices for the project.

    Once established, the visual language acts as a style coordinator —
    every shot in the project inherits these baseline choices unless
    explicitly overridden.
    """

    # Legacy: explicit DP profile (still works for power users)
    style_profile: str = Field(default="", description="Named DP style profile (deakins, storaro, lubezki, hoytema)")

    # New: freeform style description — the primary interface
    style_description: str = Field(
        default="",
        description="Freeform style description — user describes the look they want in any terms",
    )
    style_mood: str = Field(default="", description="Emotional tone / mood for the visual language")
    style_references: list[str] = Field(
        default_factory=list,
        description="Reference films, photos, paintings — anything that conveys the intended look",
    )
    auteur_blend: dict[str, float] = Field(
        default_factory=dict,
        description="Resolved auteur blend weights (auto-populated by enrichment)",
    )

    aspect_ratio: str = Field(default="2.39:1", description="Locked aspect ratio for the project")
    color_palette: str = Field(default="", description="Dominant color approach (e.g., 'teal and amber')")
    grading_profile: str = Field(default="", description="Color grading style (e.g., 'bleach_bypass')")
    film_stock: str = Field(default="", description="Locked camera/stock (e.g., 'ARRI Alexa Mini LF')")
    movement_philosophy: str = Field(
        default="",
        description="Overall movement approach (e.g., 'mostly static with slow dollies')",
    )
    lighting_approach: str = Field(
        default="",
        description="Global lighting strategy (e.g., 'naturalistic motivated light')",
    )
    notes: str = Field(default="", description="Additional visual language notes")


class Beat(BaseModel):
    """A single narrative beat within a scene.

    Beats are the atomic units of storytelling — each beat represents
    one emotional or narrative moment that gets translated into one
    or more shots.
    """

    description: str = Field(description="What happens in this beat")
    emotional_intent: str = Field(default="", description="What the audience should feel")
    suggested_shot_size: str = Field(default="", description="Suggested framing (wide, medium, close_up)")
    suggested_movement: str = Field(default="", description="Suggested camera movement")
    notes: str = Field(default="", description="Additional direction notes")


class Scene(BaseModel):
    """A scene within the project — a continuous time/place unit."""

    id: str = Field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:6]}")
    name: str = Field(default="", description="Scene name/identifier")
    description: str = Field(default="", description="Scene description")
    location: str = Field(default="", description="Where the scene takes place")
    time_of_day: str = Field(default="", description="When (dawn, day, dusk, night)")
    beats: list[Beat] = Field(default_factory=list)
    shots: list[ShotSpec] = Field(default_factory=list)


class Project(BaseModel):
    """Top-level project container.

    The Project is the master state object for an entire film/sequence
    generation workflow. It flows: Brief → VisualLanguage → Scenes → Shots.
    """

    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    created_at: float = Field(default_factory=time.time)
    status: ProjectStatus = Field(default=ProjectStatus.BRIEF)
    brief: Brief = Field(default_factory=lambda: Brief(logline=""))
    visual_language: VisualLanguage = Field(default_factory=VisualLanguage)
    scenes: list[Scene] = Field(default_factory=list)
    target_model: str = Field(default="flux-pro", description="Default generation model")

    @property
    def total_shots(self) -> int:
        return sum(len(s.shots) for s in self.scenes)

    @property
    def all_shots(self) -> list[ShotSpec]:
        return [shot for scene in self.scenes for shot in scene.shots]

    def summary(self) -> dict:
        return {
            "id": self.id,
            "status": self.status.value,
            "logline": self.brief.logline,
            "style": self.visual_language.style_profile or "not set",
            "scenes": len(self.scenes),
            "total_shots": self.total_shots,
        }

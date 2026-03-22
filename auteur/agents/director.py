"""Director agent — sequence-level creative planning and orchestration.

The director thinks at the sequence level: how do shots flow together?
What's the visual rhythm? Where are the emotional beats? The director
uses the cinematographer agent to compose individual shots but makes
the overarching creative decisions about:
- Shot order and pacing
- Visual consistency across a sequence
- Emotional arc through shot progression
- Style and tone evolution
"""

from __future__ import annotations

from auteur.agents.cinematographer import CinematographerAgent
from auteur.knowledge.ontology import ShotSpec
from auteur.knowledge.project import CharacterSpec, MusicVideoBrief
from auteur.pipeline.sequence import SequenceSpec


# ---------------------------------------------------------------------------
# Music video dramatic structure
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pipeline defaults — the arc decides, not the user
# ---------------------------------------------------------------------------
DEFAULT_BEATS: int = 9  # Full Aristotelian dramatic arc
DEFAULT_CLIP_DURATION: float = 5.0  # Seconds per beat — 9 × 5 = 45s total

# 9-beat Aristotelian arc mapped to song sections.
# (act, beat_label, default_section, tension_level, pacing_template)
MUSIC_VIDEO_BEAT_STRUCTURE: list[tuple[int, str, str, float, str]] = [
    (1, "opening_image",    "intro",      0.15, "establishing_to_intimate"),
    (1, "inciting_rupture", "verse_1",    0.35, "dialogue_scene"),
    (2, "pursuit",          "verse_2",    0.50, "dialogue_scene"),
    (2, "pre_chorus_doubt", "pre_chorus", 0.65, "tension_build"),
    (2, "chorus_eruption",  "chorus_1",   0.82, "action_sequence"),
    (2, "reversal",         "verse_3",    0.55, "reveal"),
    (3, "climax",           "bridge",     1.00, "tension_build"),
    (3, "consequence",      "chorus_2",   0.75, "action_sequence"),
    (3, "resolution",       "outro",      0.20, "establishing_to_intimate"),
]


def tension_to_duration(tension: float, section: str) -> float:
    """Return the fixed clip duration for every beat.

    Duration is decided by the arc, not the user. Every beat gets
    DEFAULT_CLIP_DURATION seconds.  Tension still drives cut rhythm
    and pacing template selection, but all clips are uniform length
    so total output is always DEFAULT_BEATS × DEFAULT_CLIP_DURATION.

    Returns DEFAULT_CLIP_DURATION (5.0s by default).
    """
    return DEFAULT_CLIP_DURATION


# Pacing templates — common shot-flow patterns
PACING_TEMPLATES: dict[str, list[dict]] = {
    "establishing_to_intimate": [
        {"shot_size": "extreme_wide", "movement": "drone", "description_suffix": "establishing the location"},
        {"shot_size": "wide", "movement": "dolly", "description_suffix": "approaching the scene"},
        {"shot_size": "medium", "movement": "static", "description_suffix": "the subject in their environment"},
        {"shot_size": "close_up", "movement": "static", "description_suffix": "the subject's face, revealing emotion"},
    ],
    "tension_build": [
        {"shot_size": "wide", "movement": "static", "description_suffix": "calm before the storm"},
        {"shot_size": "medium", "movement": "dolly", "description_suffix": "slowly closing in"},
        {"shot_size": "medium_close", "movement": "handheld", "description_suffix": "tension mounting"},
        {"shot_size": "close_up", "movement": "static", "description_suffix": "the moment of realization"},
        {"shot_size": "extreme_close", "movement": "static", "description_suffix": "the critical detail"},
    ],
    "action_sequence": [
        {"shot_size": "wide", "movement": "static", "description_suffix": "the calm before action"},
        {"shot_size": "medium", "movement": "handheld", "description_suffix": "action begins"},
        {"shot_size": "medium_wide", "movement": "track", "description_suffix": "chase/pursuit in motion"},
        {"shot_size": "close_up", "movement": "whip_pan", "description_suffix": "impact moment"},
        {"shot_size": "wide", "movement": "crane", "description_suffix": "aftermath, pulling back"},
    ],
    "dialogue_scene": [
        {"shot_size": "medium", "movement": "static", "description_suffix": "two-shot establishing spatial relationship"},
        {"shot_size": "medium_close", "angle": "over_shoulder", "description_suffix": "speaker A"},
        {"shot_size": "medium_close", "angle": "over_shoulder", "description_suffix": "speaker B reacting"},
        {"shot_size": "close_up", "movement": "dolly", "description_suffix": "emotional turning point"},
    ],
    "reveal": [
        {"shot_size": "extreme_close", "movement": "static", "description_suffix": "mysterious detail"},
        {"shot_size": "close_up", "movement": "dolly", "description_suffix": "pulling back to reveal"},
        {"shot_size": "medium", "movement": "dolly", "description_suffix": "continuing to reveal context"},
        {"shot_size": "wide", "movement": "crane", "description_suffix": "the full revelation"},
    ],
}


class DirectorAgent:
    """Sequence-level creative agent — thinks in shots, scenes, and visual arcs.

    The director composes sequences by:
    1. Understanding the overall narrative intent
    2. Selecting a pacing template or creating a custom flow
    3. Using the cinematographer to compose each individual shot
    4. Ensuring visual coherence across the sequence
    """

    def __init__(
        self,
        style: str = "",
        cinematographer: CinematographerAgent | None = None,
    ) -> None:
        self._style = style
        self._dp = cinematographer or CinematographerAgent(default_style=style)

    def plan_sequence(
        self,
        scene_description: str,
        *,
        pacing: str = "establishing_to_intimate",
        style: str = "",
        mood: str = "",
        model: str = "flux-pro",
        animate: bool = False,
        seed: int | None = None,
    ) -> SequenceSpec:
        """Plan a multi-shot sequence from a scene description.

        Args:
            scene_description: Natural language description of the scene.
            pacing: Pacing template name or "custom".
            style: DP style profile (overrides default).
            mood: Emotional tone for the sequence.
            model: Target generation model.
            animate: Whether to animate all shots.
            seed: Shared seed for visual consistency.

        Returns:
            SequenceSpec ready for the pipeline.
        """
        effective_style = style or self._style
        template = PACING_TEMPLATES.get(pacing, PACING_TEMPLATES["establishing_to_intimate"])

        shots: list[ShotSpec] = []
        for beat in template:
            # Combine scene description with beat-specific suffix
            full_description = f"{scene_description}, {beat['description_suffix']}"

            shot = self._dp.compose_shot(
                full_description,
                mood=mood,
                style=effective_style,
                shot_size=beat.get("shot_size", "medium"),
                angle=beat.get("angle", "eye_level"),
                movement=beat.get("movement", "static"),
                model=model,
                animate=animate,
            )
            shots.append(shot)

        return SequenceSpec(
            name=f"Sequence: {scene_description[:50]}",
            description=scene_description,
            shots=shots,
            shared_style=effective_style,
            shared_seed=seed,
        )

    def single_shot(
        self,
        description: str,
        **kwargs,
    ) -> ShotSpec:
        """Convenience — compose a single shot through the cinematographer.

        Passes all kwargs to CinematographerAgent.compose_shot().
        """
        return self._dp.compose_shot(description, **kwargs)

    def plan_music_video(
        self,
        scene_description: str,
        *,
        brief: MusicVideoBrief | None = None,
        song_sections: list[str] | None = None,
        protagonist_id: str = "",
        style: str = "",
        mood: str = "",
        model: str = "kling-3.0",
    ) -> list[SequenceSpec]:
        """Plan a full music video using the 9-beat dramatic arc.

        Each beat maps to a song section and produces a SequenceSpec with
        tension-driven pacing. Every ShotSpec gets tension_level,
        duration_seconds, narrative_beat, and character_id stamped.

        Args:
            scene_description: Overall scene/world description.
            brief: MusicVideoBrief for character and section info.
            song_sections: Override beat→section mapping (len must match 9 beats).
            protagonist_id: CharacterSpec.character_id for the protagonist.
            style: DP style profile.
            mood: Overall emotional tone.
            model: Target generation model.

        Returns:
            List of SequenceSpec — one per beat.
        """
        effective_style = style or self._style
        sections = song_sections or [b[2] for b in MUSIC_VIDEO_BEAT_STRUCTURE]
        char_id = protagonist_id
        if not char_id and brief:
            char_id = brief.protagonist.character_id

        sequences: list[SequenceSpec] = []
        for i, (act, beat_label, default_section, tension, pacing) in enumerate(MUSIC_VIDEO_BEAT_STRUCTURE):
            section = sections[i] if i < len(sections) else default_section
            duration = tension_to_duration(tension, section)

            seq = self.plan_sequence(
                f"{scene_description}, {beat_label.replace('_', ' ')}",
                pacing=pacing,
                style=effective_style,
                mood=mood,
                model=model,
            )

            # Stamp dramatic metadata onto every shot in the sequence
            for shot in seq.shots:
                shot.narrative_beat = beat_label
                shot.tension_level = tension
                shot.duration_seconds = duration
                if char_id:
                    shot.character_id = char_id
                shot.animate = True

            seq.name = f"Act {act} / Beat {i + 1}: {beat_label} ({section})"
            sequences.append(seq)

        return sequences

    @staticmethod
    def list_pacing_templates() -> list[str]:
        """List available pacing templates."""
        return list(PACING_TEMPLATES.keys())

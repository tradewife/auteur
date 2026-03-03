"""Cinematographer agent — translates creative intent into ShotSpecs.

The cinematographer is the core creative agent. Given a natural language
description of what the user wants, it draws on the entire knowledge system
to compose a technically precise ShotSpec — choosing lens, lighting, color,
composition, movement, and film stock based on cinematographic expertise.

This agent can work with any LLM backend (Gemini, Claude, GPT) to make
creative decisions, then maps those decisions to the structured ontology.
"""

from __future__ import annotations

from auteur.knowledge.ontology import (
    ShotSpec,
    LensSpec,
    LightSetup,
    LightSource,
    ColorPalette,
    CompositionSpec,
    MovementSpec,
    FilmStockProfile,
    ShotSize,
    ShotAngle,
    LightQuality,
    MovementType,
    BokehCharacter,
    GrainStructure,
    ColorHarmony,
    AspectRatio,
)
from auteur.knowledge.styles import STYLE_PROFILES
from auteur.knowledge.lens import FOCAL_LENGTHS, LENS_FAMILIES
from auteur.knowledge.lighting import LIGHTING_SETUPS
from auteur.knowledge.color import COLOR_PALETTES, GRADING_PROFILES
from auteur.knowledge.movement import CAMERA_MOVEMENTS


# System prompt that encodes the cinematographer's expertise
CINEMATOGRAPHER_SYSTEM_PROMPT = """You are an expert cinematographer with decades of experience.
You have deep knowledge of:
- Lens selection and its psychological effects on the viewer
- Lighting design from Rembrandt to modern mixed-source setups
- Color theory and how palette choices shape emotional response
- Composition rules and when to break them
- Camera movement as narrative tool
- Film stock and sensor characteristics
- The signature styles of master DPs (Deakins, Storaro, Lubezki, van Hoytema)

When given a scene description or creative intent, you make specific technical
decisions about EVERY aspect of the shot. You never leave things vague — you
choose exact focal lengths, specific lighting setups, precise color palettes.

You think like a DP: every technical choice serves the story.

Available lens families: {lens_families}
Available lighting setups: {lighting_setups}
Available color palettes: {color_palettes}
Available grading profiles: {grading_profiles}
Available camera movements: {camera_movements}
Available DP styles: {dp_styles}
"""


class CinematographerAgent:
    """The creative intelligence that translates intent into ShotSpecs.

    The cinematographer agent can operate in two modes:
    1. Rule-based: Uses heuristics and the knowledge system to make decisions
    2. LLM-assisted: Uses an LLM to make nuanced creative decisions

    Both modes produce the same output: a fully specified ShotSpec.
    """

    def __init__(self, default_style: str = "") -> None:
        self._default_style = default_style

    @property
    def system_prompt(self) -> str:
        """Build the cinematographer system prompt with available knowledge."""
        return CINEMATOGRAPHER_SYSTEM_PROMPT.format(
            lens_families=", ".join(LENS_FAMILIES.keys()),
            lighting_setups=", ".join(LIGHTING_SETUPS.keys()),
            color_palettes=", ".join(COLOR_PALETTES.keys()),
            grading_profiles=", ".join(GRADING_PROFILES.keys()),
            camera_movements=", ".join(CAMERA_MOVEMENTS.keys()),
            dp_styles=", ".join(STYLE_PROFILES.keys()),
        )

    def compose_shot(
        self,
        description: str,
        *,
        mood: str = "",
        style: str = "",
        shot_size: str = "medium",
        angle: str = "eye_level",
        lighting: str = "",
        movement: str = "static",
        aspect_ratio: str = "2.39:1",
        model: str = "flux-pro",
        animate: bool = False,
    ) -> ShotSpec:
        """Compose a ShotSpec from high-level creative inputs.

        This is the rule-based composition mode — it makes sensible defaults
        based on the knowledge system without requiring an LLM call.

        Args:
            description: What's in the shot.
            mood: Emotional intent (e.g., "tense", "melancholy", "triumphant").
            style: DP style profile name.
            shot_size: Shot size (e.g., "wide", "medium", "close_up").
            angle: Camera angle (e.g., "eye_level", "low", "high").
            lighting: Named lighting setup or description.
            movement: Camera movement type.
            aspect_ratio: Aspect ratio string.
            model: Target generation model.
            animate: Whether to generate video.

        Returns:
            A fully specified ShotSpec.
        """
        effective_style = style or self._default_style

        # Select lens based on shot size and style
        lens = self._select_lens(shot_size, effective_style)

        # Select lighting
        light_setup = self._select_lighting(lighting, mood, effective_style)

        # Select color palette
        color = self._select_color(mood, effective_style)

        # Build composition
        composition = CompositionSpec(
            shot_size=ShotSize(shot_size) if shot_size else ShotSize.MEDIUM,
            angle=ShotAngle(angle) if angle else ShotAngle.EYE_LEVEL,
            aspect_ratio=AspectRatio(aspect_ratio) if aspect_ratio else AspectRatio.SCOPE_239,
            depth_of_field=self._select_dof(shot_size, lens),
        )

        # Build movement
        move = self._select_movement(movement)

        # Select film stock based on style
        film_stock = self._select_film_stock(effective_style)

        return ShotSpec(
            description=description,
            emotional_intent=mood,
            style_profile=effective_style,
            lens=lens,
            lighting=light_setup,
            color=color,
            composition=composition,
            movement=move,
            film_stock=film_stock,
            target_model=model,
            animate=animate,
        )

    def _select_lens(self, shot_size: str, style: str) -> LensSpec:
        """Select lens based on shot size and DP style."""
        # Map shot sizes to typical focal lengths
        size_to_focal: dict[str, int] = {
            "extreme_wide": 14,
            "wide": 24,
            "full": 35,
            "medium_wide": 40,
            "medium": 50,
            "medium_close": 65,
            "close_up": 85,
            "extreme_close": 100,
            "insert": 100,
        }
        focal = size_to_focal.get(shot_size, 50)

        # Style adjustments
        if style == "lubezki":
            focal = max(14, focal - 15)  # Lubezki goes wider
        elif style == "deakins":
            focal = max(27, min(focal, 65))  # Deakins stays moderate

        # Select lens family based on style
        lens_family = ""
        if style == "deakins":
            lens_family = "ARRI Signature Prime"
        elif style == "storaro":
            lens_family = "Cooke S4/i"
        elif style == "lubezki":
            lens_family = "ARRI/Zeiss Master Prime"
        elif style == "hoytema":
            lens_family = "Panavision System 65"

        return LensSpec(
            focal_length_mm=focal,
            max_aperture=1.4 if shot_size in ("close_up", "extreme_close") else 2.0,
            lens_family=lens_family,
        )

    def _select_lighting(self, lighting: str, mood: str, style: str) -> LightSetup:
        """Select lighting setup based on inputs and style."""
        # Direct setup name match
        if lighting and lighting in LIGHTING_SETUPS:
            setup_data = LIGHTING_SETUPS[lighting]
            return LightSetup(
                name=lighting,
                key_to_fill_ratio=setup_data.get("ratio", "2:1"),
                overall_mood=setup_data.get("mood", ""),
            )

        # Mood-based selection
        mood_to_setup: dict[str, str] = {
            "tense": "split",
            "mysterious": "noir",
            "romantic": "butterfly",
            "dramatic": "rembrandt",
            "melancholy": "available_light",
            "triumphant": "golden_hour",
            "intimate": "rembrandt",
            "eerie": "chiaroscuro",
            "dreamy": "golden_hour",
            "gritty": "available_light",
        }
        setup_name = mood_to_setup.get(mood.lower(), "")

        if setup_name and setup_name in LIGHTING_SETUPS:
            setup_data = LIGHTING_SETUPS[setup_name]
            return LightSetup(
                name=setup_name,
                key_to_fill_ratio=setup_data.get("ratio", "2:1"),
                overall_mood=setup_data.get("mood", mood),
            )

        # Style-based defaults
        if style == "deakins":
            return LightSetup(
                name="motivated single source",
                key_to_fill_ratio="4:1",
                overall_mood=mood or "controlled, naturalistic",
            )
        elif style == "storaro":
            return LightSetup(
                name="symbolic colored light",
                key_to_fill_ratio="3:1",
                overall_mood=mood or "operatic, symbolic",
            )

        return LightSetup(name=lighting, overall_mood=mood)

    def _select_color(self, mood: str, style: str) -> ColorPalette:
        """Select color palette based on mood and style."""
        # Style-driven color
        if style == "deakins":
            return ColorPalette(
                dominant_hue="natural",
                saturation=0.6,
                contrast=0.6,
                temperature_bias="neutral",
            )
        elif style == "storaro":
            return ColorPalette(
                dominant_hue="amber",
                accent_hue="deep blue",
                harmony=ColorHarmony.COMPLEMENTARY,
                saturation=0.85,
                contrast=0.7,
                temperature_bias="warm",
            )
        elif style == "lubezki":
            return ColorPalette(
                dominant_hue="earth tones",
                saturation=0.55,
                contrast=0.5,
                temperature_bias="warm",
            )
        elif style == "hoytema":
            return ColorPalette(
                dominant_hue="amber",
                saturation=0.7,
                contrast=0.65,
                temperature_bias="warm",
            )

        # Mood-driven color
        mood_colors: dict[str, dict] = {
            "tense": {"dominant_hue": "desaturated", "saturation": 0.4, "contrast": 0.8},
            "romantic": {"dominant_hue": "warm gold", "saturation": 0.7, "contrast": 0.4},
            "melancholy": {"dominant_hue": "muted blue", "saturation": 0.35, "contrast": 0.5},
            "triumphant": {"dominant_hue": "golden", "saturation": 0.8, "contrast": 0.7},
            "eerie": {"dominant_hue": "sickly green", "saturation": 0.5, "contrast": 0.7},
        }
        if mood.lower() in mood_colors:
            return ColorPalette(**mood_colors[mood.lower()])

        return ColorPalette()

    def _select_dof(self, shot_size: str, lens: LensSpec) -> str:
        """Select depth of field based on shot size and lens."""
        if shot_size in ("close_up", "extreme_close", "insert"):
            return "shallow"
        elif shot_size in ("extreme_wide", "wide"):
            return "deep"
        elif lens.focal_length_mm >= 85:
            return "shallow"
        return "selective"

    def _select_movement(self, movement: str) -> MovementSpec:
        """Build movement spec from movement type string."""
        try:
            move_type = MovementType(movement)
        except ValueError:
            move_type = MovementType.STATIC

        speed = "slow"
        if move_type in (MovementType.WHIP_PAN, MovementType.HANDHELD):
            speed = "fast"
        elif move_type in (MovementType.STEADICAM, MovementType.CRANE):
            speed = "medium"

        return MovementSpec(
            movement_type=move_type,
            speed=speed,
        )

    def _select_film_stock(self, style: str) -> FilmStockProfile:
        """Select film stock/sensor based on DP style."""
        if style == "hoytema":
            return FilmStockProfile(
                name="Kodak Vision3 500T (65mm)",
                format_type="film",
                iso=500,
                grain=GrainStructure.MEDIUM,
                color_science="warm skin tones, rich highlight rolloff",
            )
        elif style == "lubezki":
            return FilmStockProfile(
                name="ARRI Alexa 65",
                format_type="digital",
                iso=800,
                grain=GrainStructure.FINE,
                color_science="natural, wide latitude for available light",
            )
        elif style == "storaro":
            return FilmStockProfile(
                name="ARRI Alexa 65",
                format_type="digital",
                iso=800,
                grain=GrainStructure.FINE,
                color_science="rich color separation, excellent skin tones",
            )

        # Default: ARRI Alexa Mini LF
        return FilmStockProfile(
            name="ARRI Alexa Mini LF",
            format_type="digital",
            iso=800,
            grain=GrainStructure.FINE,
            color_science="industry-standard skin tones, wide dynamic range",
        )

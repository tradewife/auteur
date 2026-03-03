"""Prompt composer — assembles cinematic ontology into generation-ready prompts.

The composer takes a ShotSpec (the complete cinematic specification) and transforms
it into a structured prompt string by extracting and formatting each dimension:
lens character, lighting, color, composition, movement, film stock texture, and
DP style influence.

This is the core engine of AUTEUR's prompt system. It bridges the gap between
structured cinematographic knowledge and the natural-language prompts that
generation models consume.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from auteur.knowledge.ontology import (
    ShotSpec,
    ShotSize,
    ShotAngle,
    LightQuality,
    GrainStructure,
    BokehCharacter,
)
from auteur.knowledge.styles import STYLE_PROFILES, AestheticStyle, AuteurLayer
from auteur.prompt.negative import NegativePromptLibrary
from auteur.prompt.optimizer import PromptOptimizer, OptimizedPrompt


class ComposedPrompt(BaseModel):
    """The output of the prompt composer — ready for optimization and generation."""

    positive: str = Field(description="Assembled positive prompt")
    negative: str = Field(default="", description="Assembled negative prompt")
    shot_spec: ShotSpec = Field(description="The source shot specification")
    style_keywords: list[str] = Field(default_factory=list)
    prompt_layers: dict[str, str] = Field(
        default_factory=dict,
        description="Individual prompt layers before composition (for debugging/tweaking)",
    )

    def optimize(self, model: str = "flux-pro") -> OptimizedPrompt:
        """Optimize this composed prompt for a specific generation model."""
        return PromptOptimizer.optimize(
            self.positive,
            self.negative,
            model=model,
            aspect_ratio=self.shot_spec.composition.aspect_ratio.value
            if self.shot_spec.composition.aspect_ratio
            else None,
            duration_s=self.shot_spec.animation_duration_s
            if self.shot_spec.animate
            else None,
        )


class PromptComposer:
    """Assembles cinematic prompts from ShotSpec ontology models.

    The composer works in layers — each aspect of the cinematographic specification
    becomes a prompt layer, and these layers are composed into the final prompt
    with appropriate ordering and emphasis.

    Prompt structure (order matters for model attention):
    1. Subject/scene description (highest attention)
    2. Composition & framing
    3. Lighting design
    4. Camera & lens
    5. Color & grading
    6. Film stock & texture
    7. Movement (if video)
    8. Style/mood qualifiers
    """

    @classmethod
    def compose(cls, shot: ShotSpec) -> ComposedPrompt:
        """Compose a complete prompt from a shot specification.

        Args:
            shot: Complete ShotSpec with all cinematographic parameters.

        Returns:
            ComposedPrompt with positive/negative prompts and metadata.
        """
        layers: dict[str, str] = {}

        # Layer 1: Subject/scene
        layers["subject"] = cls._compose_subject(shot)

        # Layer 2: Composition & framing
        layers["composition"] = cls._compose_composition(shot)

        # Layer 3: Lighting
        layers["lighting"] = cls._compose_lighting(shot)

        # Layer 4: Camera & lens
        layers["camera"] = cls._compose_camera(shot)

        # Layer 5: Color & grading
        layers["color"] = cls._compose_color(shot)

        # Layer 6: Film stock & texture
        layers["texture"] = cls._compose_texture(shot)

        # Layer 7: Movement (video only)
        if shot.animate or shot.movement.movement_type.value != "static":
            layers["movement"] = cls._compose_movement(shot)

        # Layer 8: Style influence (auteur enrichment or legacy profile)
        style_keywords: list[str] = []
        if shot.aesthetic_style:
            style_layer, style_keywords = cls._compose_aesthetic_style(shot)
            layers["style"] = style_layer
        elif shot.style_profile:
            style_layer, style_keywords = cls._compose_style(shot)
            layers["style"] = style_layer

        # Layer 9: Mood / emotional qualifiers
        layers["mood"] = cls._compose_mood(shot)

        # Assemble — filter empty layers and join
        positive_parts = [v for v in layers.values() if v.strip()]
        positive = ", ".join(positive_parts)

        # Build negative prompt (include auteur-enriched negatives if available)
        negative = NegativePromptLibrary.for_shot(
            animate=shot.animate,
            style_profile=shot.style_profile,
        )
        if shot.aesthetic_style:
            aesthetic = AestheticStyle(**shot.aesthetic_style)
            if not aesthetic.auteur_blend:
                aesthetic = AuteurLayer.enrich(aesthetic)
            if aesthetic.enriched_negative:
                extra_neg = ", ".join(aesthetic.enriched_negative[:4])
                negative = f"{negative}, {extra_neg}" if negative else extra_neg

        return ComposedPrompt(
            positive=positive,
            negative=negative,
            shot_spec=shot,
            style_keywords=style_keywords,
            prompt_layers=layers,
        )

    # ---------------------------------------------------------------------------
    # Layer composers — each extracts and formats one dimension
    # ---------------------------------------------------------------------------

    @classmethod
    def _compose_subject(cls, shot: ShotSpec) -> str:
        """Layer 1: Subject description — the most important part of the prompt."""
        parts = [shot.description]
        if shot.narrative_beat:
            parts.append(f"({shot.narrative_beat} moment)")
        return ", ".join(parts)

    @classmethod
    def _compose_composition(cls, shot: ShotSpec) -> str:
        """Layer 2: Composition — framing, angle, aspect ratio."""
        comp = shot.composition
        parts: list[str] = []

        # Shot size
        size_descriptions = {
            ShotSize.EXTREME_WIDE: "extreme wide shot",
            ShotSize.WIDE: "wide shot",
            ShotSize.FULL: "full shot",
            ShotSize.MEDIUM_WIDE: "medium wide shot",
            ShotSize.MEDIUM: "medium shot",
            ShotSize.MEDIUM_CLOSE: "medium close-up",
            ShotSize.CLOSE_UP: "close-up",
            ShotSize.EXTREME_CLOSE: "extreme close-up",
            ShotSize.INSERT: "insert shot",
        }
        parts.append(size_descriptions.get(comp.shot_size, comp.shot_size.value))

        # Angle
        angle_descriptions = {
            ShotAngle.BIRDS_EYE: "bird's-eye view",
            ShotAngle.HIGH: "high angle",
            ShotAngle.EYE_LEVEL: "eye-level",
            ShotAngle.LOW: "low angle",
            ShotAngle.WORMS_EYE: "worm's-eye view",
            ShotAngle.DUTCH: "Dutch angle",
            ShotAngle.OVER_SHOULDER: "over-the-shoulder",
            ShotAngle.POV: "POV shot",
        }
        if comp.angle != ShotAngle.EYE_LEVEL:
            parts.append(angle_descriptions.get(comp.angle, comp.angle.value))

        # Depth of field
        if comp.depth_of_field:
            parts.append(f"{comp.depth_of_field} depth of field")

        # Framing device
        if comp.framing_device:
            parts.append(f"framed through {comp.framing_device}")

        # Foreground
        if comp.foreground_element:
            parts.append(f"{comp.foreground_element} in foreground")

        # Negative space
        if comp.negative_space:
            parts.append(f"negative space: {comp.negative_space}")

        return ", ".join(parts)

    @classmethod
    def _compose_lighting(cls, shot: ShotSpec) -> str:
        """Layer 3: Lighting design — setup, quality, ratio, atmosphere."""
        light = shot.lighting
        parts: list[str] = []

        if light.name:
            parts.append(f"{light.name} lighting")

        # Key quality from sources
        key_sources = [s for s in light.sources if s.role == "key"]
        if key_sources:
            quality_map = {
                LightQuality.HARD: "hard directional light",
                LightQuality.SOFT: "soft diffused light",
                LightQuality.VOLUMETRIC: "volumetric light rays",
                LightQuality.PRACTICAL: "practical-motivated lighting",
                LightQuality.NEON: "neon light sources",
                LightQuality.AMBIENT: "ambient available light",
            }
            quality_desc = quality_map.get(key_sources[0].quality, "")
            if quality_desc:
                parts.append(quality_desc)

        if light.key_to_fill_ratio and light.key_to_fill_ratio != "2:1":
            parts.append(f"{light.key_to_fill_ratio} lighting ratio")

        if light.overall_mood:
            parts.append(light.overall_mood)

        if light.time_of_day:
            parts.append(f"{light.time_of_day}")

        if light.atmospheric:
            parts.append(light.atmospheric)

        return ", ".join(parts)

    @classmethod
    def _compose_camera(cls, shot: ShotSpec) -> str:
        """Layer 4: Camera and lens — the optics that shape the image."""
        lens = shot.lens
        stock = shot.film_stock
        parts: list[str] = []

        # Camera body
        parts.append(f"shot on {stock.name}")

        # Lens
        lens_desc = f"{lens.focal_length_mm}mm"
        if lens.lens_family:
            lens_desc = f"{lens.lens_family} {lens_desc}"
        if lens.anamorphic:
            lens_desc += " anamorphic"
        if lens.vintage:
            lens_desc += " vintage"
        parts.append(f"with {lens_desc}")

        # Aperture
        parts.append(f"at T{lens.max_aperture}")

        # Bokeh
        bokeh_descriptions = {
            BokehCharacter.SMOOTH: "smooth creamy bokeh",
            BokehCharacter.BUSY: "textured busy bokeh",
            BokehCharacter.SWIRL: "swirly Petzval bokeh",
            BokehCharacter.CAT_EYE: "cat-eye bokeh",
            BokehCharacter.OVAL: "oval anamorphic bokeh",
            BokehCharacter.BUBBLE: "bubble bokeh",
        }
        if lens.bokeh != BokehCharacter.SMOOTH:
            bokeh_desc = bokeh_descriptions.get(lens.bokeh, "")
            if bokeh_desc:
                parts.append(bokeh_desc)

        # Lens character notes
        if lens.character_notes:
            parts.append(lens.character_notes)

        return ", ".join(parts)

    @classmethod
    def _compose_color(cls, shot: ShotSpec) -> str:
        """Layer 5: Color palette and grading."""
        color = shot.color
        parts: list[str] = []

        if color.dominant_hue:
            if color.accent_hue:
                parts.append(f"{color.dominant_hue} and {color.accent_hue} color palette")
            else:
                parts.append(f"{color.dominant_hue} color palette")

        if color.grading_profile:
            parts.append(f"{color.grading_profile} color grading")

        if color.temperature_bias and color.temperature_bias != "neutral":
            parts.append(f"{color.temperature_bias} color temperature")

        # Saturation as descriptor
        if color.saturation < 0.3:
            parts.append("desaturated")
        elif color.saturation > 0.8:
            parts.append("richly saturated")

        # Contrast as descriptor
        if color.contrast > 0.7:
            parts.append("high contrast")
        elif color.contrast < 0.3:
            parts.append("low contrast")

        return ", ".join(parts)

    @classmethod
    def _compose_texture(cls, shot: ShotSpec) -> str:
        """Layer 6: Film stock texture — grain, noise, halation."""
        stock = shot.film_stock
        parts: list[str] = []

        grain_descriptions = {
            GrainStructure.FINE: "fine film grain",
            GrainStructure.MEDIUM: "medium film grain",
            GrainStructure.COARSE: "heavy film grain",
            GrainStructure.ORGANIC: "organic analog grain",
            GrainStructure.DIGITAL_NOISE: "digital noise texture",
            GrainStructure.NONE: "",
        }
        grain_desc = grain_descriptions.get(stock.grain, "")
        if grain_desc:
            parts.append(grain_desc)

        if stock.color_science:
            parts.append(stock.color_science)

        if stock.format_type == "film":
            parts.append("shot on celluloid")

        return ", ".join(parts)

    @classmethod
    def _compose_movement(cls, shot: ShotSpec) -> str:
        """Layer 7: Camera movement — for video generation."""
        move = shot.movement
        parts: list[str] = []

        movement_descriptions = {
            "static": "static camera, locked off",
            "pan": "smooth pan",
            "tilt": "smooth tilt",
            "dolly": "dolly movement",
            "track": "tracking shot",
            "steadicam": "Steadicam shot, smooth floating movement",
            "handheld": "handheld camera, organic movement",
            "crane": "crane shot, sweeping movement",
            "drone": "aerial drone shot",
            "vertigo": "dolly zoom, vertigo effect",
            "whip_pan": "whip pan, rapid camera movement",
            "roll": "camera roll",
        }
        move_desc = movement_descriptions.get(move.movement_type.value, move.movement_type.value)
        parts.append(move_desc)

        if move.speed and move.speed != "slow":
            parts.append(f"{move.speed} movement")

        if move.direction:
            parts.append(f"moving {move.direction}")

        if move.motivation:
            parts.append(f"({move.motivation})")

        return ", ".join(parts)

    @classmethod
    def _compose_aesthetic_style(cls, shot: ShotSpec) -> tuple[str, list[str]]:
        """Layer 8 (new): Auteur-enriched freeform style.

        Takes the user's AestheticStyle, runs it through the AuteurLayer,
        and injects the enriched keywords into the prompt. The user's own
        style description is preserved as the base, with auteur depth layered on.
        """
        style_data = shot.aesthetic_style or {}
        style = AestheticStyle(**style_data)

        # Run enrichment if not already done
        if not style.auteur_blend:
            style = AuteurLayer.enrich(style)

        # Build the style layer: user description first, then enriched keywords
        parts: list[str] = []
        if style.description:
            parts.append(style.description)
        if style.lighting_feel:
            parts.append(style.lighting_feel)
        if style.color_feel:
            parts.append(style.color_feel)

        # Inject enriched auteur keywords (the invisible depth)
        keywords = list(style.enriched_keywords)
        if keywords:
            parts.extend(keywords[:6])  # Top 6 enriched keywords

        style_desc = ", ".join(parts)
        return style_desc, keywords

    @classmethod
    def _compose_style(cls, shot: ShotSpec) -> tuple[str, list[str]]:
        """Layer 8 (legacy): Direct DP style profile keywords."""
        profile = STYLE_PROFILES.get(shot.style_profile)
        if not profile:
            return "", []

        # Use the profile's prompt keywords
        keywords = list(profile.prompt_keywords[:5])  # Top 5 most characteristic
        style_desc = ", ".join(keywords)
        return style_desc, keywords

    @classmethod
    def _compose_mood(cls, shot: ShotSpec) -> str:
        """Layer 9: Emotional and mood qualifiers."""
        parts: list[str] = []

        if shot.emotional_intent:
            parts.append(shot.emotional_intent)

        # Always add baseline cinematic quality markers
        parts.append("cinematic")
        parts.append("masterful cinematography")

        return ", ".join(parts)

    # ---------------------------------------------------------------------------
    # Quick compose — convenience for simple use cases
    # ---------------------------------------------------------------------------

    @classmethod
    def quick(
        cls,
        description: str,
        *,
        style: str = "",
        shot_size: str = "medium",
        lighting: str = "",
        mood: str = "",
        model: str = "flux-pro",
    ) -> OptimizedPrompt:
        """Quick-compose a prompt from minimal inputs.

        For when you don't need the full ShotSpec machinery — just describe
        what you want and get an optimized prompt back.

        Args:
            description: What's in the shot.
            style: DP style profile name (deakins, storaro, lubezki, hoytema).
            shot_size: Shot size (wide, medium, close_up, etc.).
            lighting: Lighting description override.
            mood: Emotional intent.
            model: Target generation model.

        Returns:
            OptimizedPrompt ready for a provider.
        """
        from auteur.knowledge.ontology import (
            ShotSpec, LightSetup, CompositionSpec,
        )

        # Build a minimal ShotSpec
        spec = ShotSpec(
            description=description,
            emotional_intent=mood,
            style_profile=style,
            composition=CompositionSpec(
                shot_size=ShotSize(shot_size) if shot_size else ShotSize.MEDIUM,
            ),
            lighting=LightSetup(name=lighting) if lighting else LightSetup(),
            target_model=model,
        )

        composed = cls.compose(spec)
        return composed.optimize(model=model)

"""Shot templates — reusable prompt scaffolds for common cinematographic situations.

Each template provides a structured starting point that the composer can populate
with specific ontology values. Templates encode the *grammar* of cinematography —
the proven patterns that DPs use across projects.
"""

from pydantic import BaseModel, Field


class ShotTemplate(BaseModel):
    """A reusable prompt scaffold for a common shot type."""

    name: str = Field(description="Template identifier")
    category: str = Field(description="Category: establishing, dialogue, action, transition, detail, portrait")
    description: str = Field(description="When to use this template")
    prompt_scaffold: str = Field(
        description="Prompt skeleton with {placeholders} for ontology values"
    )
    required_fields: list[str] = Field(
        default_factory=list,
        description="Which ShotSpec fields are required for this template",
    )
    recommended_style: str = Field(
        default="",
        description="Suggested DP style profile for this template type",
    )


# ---------------------------------------------------------------------------
# Template library — the grammar of cinematography
# ---------------------------------------------------------------------------

SHOT_TEMPLATES: dict[str, ShotTemplate] = {
    # --- Establishing shots ---
    "epic_establishing": ShotTemplate(
        name="epic_establishing",
        category="establishing",
        description="Grand opening shot that sets location, scale, and atmosphere. "
        "The audience's first breath of the world.",
        prompt_scaffold=(
            "{shot_size} shot, {location_description}, "
            "{time_of_day} lighting, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "{aspect_ratio} anamorphic, "
            "{color_palette}, {grading_profile}, "
            "{grain_texture}, cinematic, masterful composition"
        ),
        required_fields=["description", "composition", "lighting", "color"],
    ),
    "intimate_establishing": ShotTemplate(
        name="intimate_establishing",
        category="establishing",
        description="Quiet establishing shot — a room, a street corner, a personal space. "
        "Sets emotional tone rather than geographic scale.",
        prompt_scaffold=(
            "{shot_size} shot, {location_description}, "
            "{lighting_setup} lighting, {light_quality}, "
            "practical lights visible, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "{color_palette}, {saturation_note}, "
            "lived-in feeling, atmospheric, {film_stock_texture}"
        ),
        required_fields=["description", "lighting", "color"],
    ),
    # --- Dialogue / portrait ---
    "hero_close_up": ShotTemplate(
        name="hero_close_up",
        category="portrait",
        description="Defining character close-up — the shot that tells you who this person is. "
        "Every facial detail matters.",
        prompt_scaffold=(
            "close-up portrait, {subject_description}, "
            "{lighting_setup} lighting, {key_to_fill_ratio} ratio, "
            "{eye_light_note}, {skin_rendering}, "
            "shot on {camera} with {lens_description} at {aperture}, "
            "{bokeh_character} bokeh, {depth_of_field}, "
            "{color_palette}, {emotional_tone}, "
            "cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "lens", "lighting", "color"],
        recommended_style="deakins",
    ),
    "over_shoulder": ShotTemplate(
        name="over_shoulder",
        category="dialogue",
        description="Conversational OTS — establishes spatial relationship between two characters. "
        "The near shoulder anchors the viewer's perspective.",
        prompt_scaffold=(
            "over-the-shoulder shot, {subject_description}, "
            "foreground shoulder out of focus, "
            "{lighting_setup} lighting, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "{depth_of_field}, {color_palette}, "
            "cinematic, natural, {film_stock_texture}"
        ),
        required_fields=["description", "lens", "lighting"],
    ),
    "two_shot": ShotTemplate(
        name="two_shot",
        category="dialogue",
        description="Two characters in frame — their spatial relationship IS the subtext.",
        prompt_scaffold=(
            "medium shot, two figures, {subject_description}, "
            "{composition_rule}, {negative_space_note}, "
            "{lighting_setup} lighting, "
            "shot on {camera} with {lens_description}, "
            "{depth_of_field}, {color_palette}, "
            "cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "composition", "lighting"],
    ),
    # --- Action ---
    "chase_tracking": ShotTemplate(
        name="chase_tracking",
        category="action",
        description="Dynamic tracking shot following action — urgency through camera movement.",
        prompt_scaffold=(
            "{shot_size} tracking shot, {subject_description}, "
            "{movement_description}, motion blur, "
            "{lighting_setup} lighting, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "{stabilization} camera, {color_palette}, "
            "high energy, cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "movement", "lens"],
    ),
    "impact_moment": ShotTemplate(
        name="impact_moment",
        category="action",
        description="The moment of collision, revelation, or climax — frozen or slow-motion.",
        prompt_scaffold=(
            "{shot_size} shot, {subject_description}, "
            "dramatic {lighting_setup} lighting, "
            "high contrast, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "{depth_of_field}, {color_palette}, "
            "intense, cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "lighting", "color"],
    ),
    # --- Transitions ---
    "passage_of_time": ShotTemplate(
        name="passage_of_time",
        category="transition",
        description="Visual shorthand for time passing — light shifting, shadows moving, "
        "seasons turning.",
        prompt_scaffold=(
            "{shot_size} shot, {location_description}, "
            "timelapse feeling, shifting light, "
            "{color_palette}, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "contemplative, cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "color"],
    ),
    "dreamy_transition": ShotTemplate(
        name="dreamy_transition",
        category="transition",
        description="Soft, ethereal transition shot — memory, fantasy, or altered state.",
        prompt_scaffold=(
            "{shot_size} shot, {subject_description}, "
            "soft diffused {lighting_setup} lighting, "
            "lens flare, halation, dreamy glow, "
            "shot on {camera} with {lens_description}, "
            "overexposed highlights, {color_palette}, "
            "ethereal, painterly, {film_stock_texture}"
        ),
        required_fields=["description", "lighting", "color"],
    ),
    # --- Detail / insert ---
    "narrative_insert": ShotTemplate(
        name="narrative_insert",
        category="detail",
        description="Close-up of an object that carries narrative weight — a letter, a weapon, "
        "a photograph.",
        prompt_scaffold=(
            "extreme close-up, {subject_description}, "
            "{lighting_setup} lighting, "
            "razor-thin depth of field, {bokeh_character} bokeh, "
            "shot on {camera} with {lens_description} at {aperture}, "
            "{color_palette}, tactile detail, "
            "cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "lens", "lighting"],
    ),
    "texture_study": ShotTemplate(
        name="texture_study",
        category="detail",
        description="Abstract or semi-abstract detail — surface, material, environmental texture.",
        prompt_scaffold=(
            "macro detail shot, {subject_description}, "
            "{lighting_setup} side-lighting for texture, "
            "extreme shallow depth of field, "
            "shot on {camera} with {lens_description}, "
            "{color_palette}, tactile, material, "
            "cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "lens"],
    ),
    # --- Specialty ---
    "silhouette": ShotTemplate(
        name="silhouette",
        category="portrait",
        description="Subject in silhouette against a luminous background — identity in outline.",
        prompt_scaffold=(
            "{shot_size} shot, {subject_description} in silhouette, "
            "backlit by {light_source}, rim light edge, "
            "high contrast, {atmosphere}, "
            "shot on {camera} with {lens_description}, "
            "{color_palette}, dramatic, cinematic, {film_stock_texture}"
        ),
        required_fields=["description", "lighting"],
        recommended_style="deakins",
    ),
    "noir": ShotTemplate(
        name="noir",
        category="portrait",
        description="Classic noir setup — venetian blind shadows, low-key, high mystery.",
        prompt_scaffold=(
            "{shot_size} shot, {subject_description}, "
            "film noir lighting, hard shadows, venetian blind pattern, "
            "low-key, high contrast, single hard source, "
            "shot on {camera} with {lens_description}, "
            "black and white or desaturated, {atmosphere}, "
            "cinematic noir, {film_stock_texture}"
        ),
        required_fields=["description", "lighting"],
    ),
    "neon_night": ShotTemplate(
        name="neon_night",
        category="establishing",
        description="Urban night scene bathed in neon — cyberpunk, noir, or simply modern nightlife.",
        prompt_scaffold=(
            "{shot_size} shot, {location_description}, "
            "neon lighting, {neon_colors}, reflections on wet surfaces, "
            "practical neon signs, night scene, "
            "shot on {camera} with {lens_description}, "
            "{bokeh_character} bokeh, {color_palette}, "
            "cinematic, atmospheric, {film_stock_texture}"
        ),
        required_fields=["description", "color"],
    ),
}


def get_template(name: str) -> ShotTemplate | None:
    """Retrieve a shot template by name."""
    return SHOT_TEMPLATES.get(name)


def list_templates(category: str | None = None) -> list[str]:
    """List available template names, optionally filtered by category."""
    if category:
        return [k for k, v in SHOT_TEMPLATES.items() if v.category == category]
    return list(SHOT_TEMPLATES.keys())

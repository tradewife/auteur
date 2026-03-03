"""Base style profile — the template for encoding a DP's visual signature."""

from pydantic import BaseModel, Field


class StyleProfile(BaseModel):
    """A cinematographer's signature visual style encoded as composable parameters.

    Each profile captures the recurring choices, preferences, and philosophical
    approaches that define a DP's work. These are not rigid rules but tendencies —
    weighted preferences that the prompt composer can blend and adapt.
    """

    name: str = Field(description="Full name of the cinematographer")
    philosophy: str = Field(description="Core visual philosophy in one paragraph")

    # Preferred tools
    preferred_lenses: list[str] = Field(default_factory=list, description="Lens families/focal lengths they favor")
    preferred_camera: list[str] = Field(default_factory=list, description="Camera systems they typically use")
    preferred_film_stock: list[str] = Field(default_factory=list, description="Film stocks or digital profiles")

    # Lighting tendencies
    lighting_approach: str = Field(default="", description="Overall lighting philosophy")
    typical_ratios: str = Field(default="", description="Usual key-to-fill ratios")
    color_temperature_preference: str = Field(default="", description="Warm/cool bias")
    use_of_practicals: str = Field(default="", description="How they use practical lights")

    # Color tendencies
    color_palette: str = Field(default="", description="Characteristic color palette")
    saturation_tendency: str = Field(default="", description="Saturated, desaturated, or natural")
    grading_style: str = Field(default="", description="Post-production color approach")

    # Composition tendencies
    composition_style: str = Field(default="", description="Framing and composition approach")
    preferred_aspect_ratio: str = Field(default="", description="Typical aspect ratio choice")
    use_of_depth: str = Field(default="", description="Deep focus, shallow, selective")

    # Movement tendencies
    movement_philosophy: str = Field(default="", description="How and why the camera moves")
    preferred_movement: list[str] = Field(default_factory=list, description="Typical movement types")

    # Signature elements
    signature_techniques: list[str] = Field(default_factory=list, description="Distinctive visual techniques")
    notable_films: list[str] = Field(default_factory=list, description="Key filmography")

    # For prompt generation
    prompt_keywords: list[str] = Field(default_factory=list, description="Keywords that evoke this DP's style")
    negative_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords to avoid when emulating this style",
    )

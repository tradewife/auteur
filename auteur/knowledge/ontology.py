"""Core ontology — the structured data models that define cinematic language.

Every concept in cinematography is modeled here as a composable Pydantic model.
These models are the atoms from which the prompt composer builds its molecules.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums — the vocabulary of cinema
# ---------------------------------------------------------------------------


class SensorFormat(str, Enum):
    """Camera sensor/film gate size — fundamentally shapes depth-of-field and image character."""

    SUPER_16 = "super_16"  # 12.52×7.41mm — grainy, documentary, intimate
    SUPER_35 = "super_35"  # 24.89×18.66mm — cinema standard, balanced
    FULL_FRAME = "full_frame"  # 36×24mm — shallow DoF, photographic
    LARGE_FORMAT = "large_format"  # 54.12×25.59mm (Alexa 65) — epic, immersive
    IMAX = "imax"  # 70.41×52.63mm — overwhelming scale
    MEDIUM_FORMAT = "medium_format"  # 43.8×32.9mm — fashion/portrait depth


class AspectRatio(str, Enum):
    """Aspect ratio as narrative tool — the shape of the story."""

    ACADEMY_133 = "1.33:1"  # 4:3 — intimate, nostalgic, contained
    FLAT_185 = "1.85:1"  # Standard widescreen — versatile, balanced
    SCOPE_239 = "2.39:1"  # Anamorphic — epic, cinematic grandeur
    ULTRA_PANAVISION = "2.76:1"  # Ultra-wide — overwhelming scale
    IMAX_143 = "1.43:1"  # IMAX — immersive vertical presence
    SQUARE_1 = "1:1"  # Square — contained, social, artistic
    PORTRAIT_916 = "9:16"  # Vertical — mobile-first, intimate
    STANDARD_169 = "16:9"  # HD/broadcast — universal digital


class ShotSize(str, Enum):
    """Shot size — the fundamental unit of visual storytelling distance."""

    EXTREME_WIDE = "extreme_wide"  # Landscape dominates — human is insignificant
    WIDE = "wide"  # Full environment — establishes context
    FULL = "full"  # Head to toe — body language readable
    MEDIUM_WIDE = "medium_wide"  # Knees up — social distance
    MEDIUM = "medium"  # Waist up — conversational
    MEDIUM_CLOSE = "medium_close"  # Chest up — personal
    CLOSE_UP = "close_up"  # Face fills frame — emotional intimacy
    EXTREME_CLOSE = "extreme_close"  # Detail/feature — obsessive focus
    INSERT = "insert"  # Object detail — narrative significance


class ShotAngle(str, Enum):
    """Camera angle relative to subject — encodes power dynamics."""

    BIRDS_EYE = "birds_eye"  # Directly above — omniscient, vulnerability
    HIGH = "high"  # Looking down — diminishment, surveillance
    EYE_LEVEL = "eye_level"  # Neutral — equality, documentary truth
    LOW = "low"  # Looking up — power, heroism, menace
    WORMS_EYE = "worms_eye"  # Ground level — extreme power, alien perspective
    DUTCH = "dutch"  # Tilted — unease, disorientation, madness
    OVER_SHOULDER = "over_shoulder"  # Conversational POV — connection
    POV = "pov"  # Subject's eyes — total identification


class LightQuality(str, Enum):
    """Light quality — hard vs soft fundamentally changes mood."""

    HARD = "hard"  # Direct, specular — drama, definition, noir
    SOFT = "soft"  # Diffused, wrapping — beauty, empathy, naturalism
    MIXED = "mixed"  # Combination — complexity, realism
    AMBIENT = "ambient"  # Environmental only — documentary, available light
    VOLUMETRIC = "volumetric"  # Visible light rays — atmosphere, divinity
    PRACTICAL = "practical"  # Motivated by in-scene sources — realism
    NEON = "neon"  # Artificial color sources — urban, cyberpunk


class MovementType(str, Enum):
    """Camera movement type — how the camera travels through space."""

    STATIC = "static"  # Locked off — contemplative power
    PAN = "pan"  # Horizontal rotation — survey, reveal
    TILT = "tilt"  # Vertical rotation — scale revelation
    DOLLY = "dolly"  # Forward/back on track — emotional proximity
    TRACK = "track"  # Lateral on track/dolly — alongside subject
    STEADICAM = "steadicam"  # Stabilized handheld — floating immersion
    HANDHELD = "handheld"  # Unstabilized — urgency, documentary
    CRANE = "crane"  # Vertical + horizontal sweep — grandeur
    DRONE = "drone"  # Aerial — omniscient overview
    VERTIGO = "vertigo"  # Dolly zoom — psychological distortion
    WHIP_PAN = "whip_pan"  # Rapid rotation — temporal jump, energy
    ROLL = "roll"  # Rotation on lens axis — disorientation


class BokehCharacter(str, Enum):
    """Bokeh quality — the out-of-focus rendering character."""

    SMOOTH = "smooth"  # Creamy, undistracted — modern primes
    BUSY = "busy"  # Nervous, textured — older/cheaper lenses
    SWIRL = "swirl"  # Petzval-style rotation — artistic, vintage
    CAT_EYE = "cat_eye"  # Mechanical vignetting — anamorphic edges
    OVAL = "oval"  # Anamorphic squeeze — cinematic signature
    BUBBLE = "bubble"  # Soap-bubble highlights — dreamy, ethereal


class GrainStructure(str, Enum):
    """Film grain / digital noise character."""

    FINE = "fine"  # Barely visible — clean, modern, digital
    MEDIUM = "medium"  # Textured but controlled — classic cinema
    COARSE = "coarse"  # Prominent — gritty, documentary, period
    ORGANIC = "organic"  # Film-like randomness — warm, analog
    DIGITAL_NOISE = "digital_noise"  # Fixed-pattern — lo-fi, surveillance
    NONE = "none"  # Pristine clean — hyperreal, commercial


class ColorHarmony(str, Enum):
    """Color relationship system."""

    COMPLEMENTARY = "complementary"  # Opposite wheel — maximum contrast
    ANALOGOUS = "analogous"  # Adjacent wheel — harmony, subtlety
    TRIADIC = "triadic"  # Three equidistant — vibrant, balanced
    SPLIT_COMPLEMENTARY = "split_complementary"  # Nuanced contrast
    MONOCHROMATIC = "monochromatic"  # Single hue variations — mood, timelessness
    DESATURATED = "desaturated"  # Muted palette — melancholy, memory


# ---------------------------------------------------------------------------
# Composite models — building blocks that combine into shots
# ---------------------------------------------------------------------------


class LensSpec(BaseModel):
    """Complete lens specification — optics shape psychology."""

    focal_length_mm: int = Field(description="Focal length in mm")
    max_aperture: float = Field(description="Maximum aperture (T-stop for cinema, f-stop for photo)")
    lens_family: str = Field(default="", description="Lens family name (e.g. 'Cooke S4', 'Zeiss Master Prime')")
    anamorphic: bool = Field(default=False, description="Anamorphic squeeze (2x)")
    vintage: bool = Field(default=False, description="Vintage/detuned character")
    bokeh: BokehCharacter = Field(default=BokehCharacter.SMOOTH)
    # Prompt-relevant descriptors
    character_notes: str = Field(
        default="",
        description="Freeform notes on lens character for prompt generation",
    )


class LightSource(BaseModel):
    """A single light source in a setup."""

    role: str = Field(description="Role: key, fill, rim, kicker, hair, practical, ambient")
    color_temp_k: int = Field(default=5600, description="Color temperature in Kelvin")
    quality: LightQuality = Field(default=LightQuality.SOFT)
    intensity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relative intensity 0-1",
    )
    direction: str = Field(default="", description="Direction relative to subject (e.g. '45° camera-left, high')")
    modifier: str = Field(default="", description="Light modifier (e.g. 'book light', '4x4 silk', 'bare bulb')")


class LightSetup(BaseModel):
    """Complete lighting design — sources, ratios, and mood."""

    name: str = Field(default="", description="Named setup (e.g. 'Rembrandt', 'butterfly')")
    sources: list[LightSource] = Field(default_factory=list)
    key_to_fill_ratio: str = Field(default="2:1", description="Lighting ratio (e.g. '4:1' for dramatic)")
    overall_mood: str = Field(default="", description="Emotional intent of the lighting")
    time_of_day: str = Field(default="", description="Time context if naturalistic")
    atmospheric: str = Field(
        default="",
        description="Atmosphere effects: haze, fog, dust, rain, steam",
    )


class ColorPalette(BaseModel):
    """Color design — the emotional DNA of the image."""

    harmony: ColorHarmony = Field(default=ColorHarmony.COMPLEMENTARY)
    dominant_hue: str = Field(default="", description="Primary color (e.g. 'teal', 'amber', 'crimson')")
    accent_hue: str = Field(default="", description="Secondary/accent color")
    saturation: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Overall saturation: 0=monochrome, 1=vivid",
    )
    contrast: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Tonal contrast: 0=flat, 1=crushed blacks & blown highlights",
    )
    grading_profile: str = Field(
        default="",
        description="Named grade (e.g. 'teal-orange blockbuster', 'bleach bypass')",
    )
    temperature_bias: str = Field(
        default="neutral",
        description="Overall warmth: warm, cool, neutral",
    )


class CompositionSpec(BaseModel):
    """Composition design — how elements are arranged in the frame."""

    rule: str = Field(default="rule_of_thirds", description="Primary composition system")
    shot_size: ShotSize = Field(default=ShotSize.MEDIUM)
    angle: ShotAngle = Field(default=ShotAngle.EYE_LEVEL)
    aspect_ratio: AspectRatio = Field(default=AspectRatio.SCOPE_239)
    depth_of_field: str = Field(
        default="shallow",
        description="DoF intent: deep, shallow, selective, split-diopter",
    )
    foreground_element: str = Field(default="", description="Foreground interest element")
    background_treatment: str = Field(
        default="",
        description="Background handling: sharp context, soft bokeh, negative space",
    )
    framing_device: str = Field(default="", description="Frame-within-frame element (doorway, window, etc.)")
    negative_space: str = Field(default="", description="Intentional empty space and its purpose")


class MovementSpec(BaseModel):
    """Camera movement design — how the camera moves and why."""

    movement_type: MovementType = Field(default=MovementType.STATIC)
    speed: str = Field(default="slow", description="Movement speed: slow, medium, fast, whip")
    direction: str = Field(default="", description="Movement direction relative to subject")
    motivation: str = Field(default="", description="Narrative reason for the movement")
    stabilization: str = Field(
        default="",
        description="Stabilization method: tripod, steadicam, gimbal, handheld, dolly",
    )
    start_position: str = Field(default="", description="Where the camera starts")
    end_position: str = Field(default="", description="Where the camera ends")


class FilmStockProfile(BaseModel):
    """Film stock or digital sensor profile — the texture of the image."""

    name: str = Field(description="Stock/sensor name (e.g. 'Kodak Vision3 500T', 'ARRI Alexa Mini LF')")
    format_type: str = Field(default="digital", description="'film' or 'digital'")
    sensor_format: SensorFormat = Field(default=SensorFormat.SUPER_35)
    iso: int = Field(default=800, description="Native/rated ISO")
    grain: GrainStructure = Field(default=GrainStructure.FINE)
    color_science: str = Field(
        default="",
        description="Color rendering character (e.g. 'warm skin tones', 'clinical precision')",
    )
    dynamic_range_stops: float = Field(default=14.0, description="Dynamic range in stops")
    latitude_notes: str = Field(default="", description="Exposure latitude character")


# ---------------------------------------------------------------------------
# The Shot — the atomic unit of AUTEUR
# ---------------------------------------------------------------------------


class ShotSpec(BaseModel):
    """Complete shot specification — everything needed to generate one cinematic image/clip.

    This is the master model that the prompt composer consumes. Every field
    maps to a specific dimension of the final prompt.
    """

    # Creative intent
    description: str = Field(description="Natural language description of the shot's content and narrative purpose")
    emotional_intent: str = Field(default="", description="The feeling this shot should evoke")
    narrative_beat: str = Field(default="", description="Story moment: establishing, rising, climax, denouement")

    # Technical specifications
    lens: LensSpec = Field(default_factory=lambda: LensSpec(focal_length_mm=35, max_aperture=1.4))
    lighting: LightSetup = Field(default_factory=LightSetup)
    color: ColorPalette = Field(default_factory=ColorPalette)
    composition: CompositionSpec = Field(default_factory=CompositionSpec)
    movement: MovementSpec = Field(default_factory=MovementSpec)
    film_stock: FilmStockProfile = Field(
        default_factory=lambda: FilmStockProfile(name="ARRI Alexa Mini LF")
    )

    # Style reference
    style_profile: str = Field(default="", description="Named DP style profile (e.g. 'deakins', 'lubezki')")
    aesthetic_style: dict | None = Field(
        default=None,
        description="Freeform AestheticStyle (serialized). When present, auteur enrichment is applied.",
    )

    # Generation metadata
    target_model: str = Field(default="", description="Target generation model (e.g. 'flux-pro', 'veo3')")
    animate: bool = Field(default=False, description="Whether to animate after image generation")
    animation_duration_s: float = Field(default=6.0, description="Animation duration in seconds")
    seed: int | None = Field(default=None, description="Seed for reproducibility")

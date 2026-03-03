"""Negative prompt library — curated anti-prompts for generation quality control.

Negative prompts tell models what to AVOID. This library provides composable
negative prompt segments organized by concern (anatomy, style, quality, etc.)
that the composer can assemble based on the shot specification.
"""

from __future__ import annotations


class NegativePromptLibrary:
    """Composable negative prompt segments for different quality concerns."""

    # --- Anatomical / figure quality ---
    ANATOMY = (
        "deformed, disfigured, extra limbs, extra fingers, fused fingers, "
        "mutated hands, bad anatomy, wrong proportions, malformed limbs, "
        "missing arms, missing legs, extra arms, extra legs, cloned face, "
        "gross proportions, poorly drawn hands, poorly drawn face"
    )

    # --- General quality ---
    QUALITY = (
        "low quality, low resolution, blurry, pixelated, noisy, artifacts, "
        "jpeg artifacts, compression artifacts, watermark, signature, "
        "text overlay, logo, banner, out of frame, cropped badly"
    )

    # --- Style avoidance (when photorealistic is desired) ---
    ANTI_ILLUSTRATION = (
        "cartoon, anime, illustration, painting, drawing, sketch, "
        "3d render, CGI, plastic, artificial, video game, "
        "unreal engine, digital art, concept art"
    )

    # --- Style avoidance (when stylized is desired) ---
    ANTI_PHOTOREALISTIC = (
        "photorealistic, hyperrealistic, photograph, camera, raw photo"
    )

    # --- Cinematic anti-patterns ---
    ANTI_AMATEUR = (
        "amateur, snapshot, selfie, iPhone photo, instagram filter, "
        "overprocessed, HDR tonemapped, oversaturated, flat lighting, "
        "on-camera flash, harsh direct flash, unflattering angle"
    )

    # --- Composition problems ---
    COMPOSITION = (
        "cluttered background, distracting elements, bad framing, "
        "centered subject with no intent, tangent lines, "
        "merging elements, busy composition"
    )

    # --- Color problems ---
    COLOR = (
        "color banding, posterization, unnatural skin tones, "
        "green skin, blue skin, oversaturated, neon skin"
    )

    # --- Lighting problems ---
    LIGHTING = (
        "flat lighting, no shadows, multiple shadows, conflicting light sources, "
        "overexposed, underexposed, blown highlights, crushed blacks without intent"
    )

    # --- Motion / video specific ---
    MOTION = (
        "flickering, temporal artifacts, morphing, warping, "
        "inconsistent between frames, jumpy, stuttering"
    )

    # --- Text / watermark ---
    TEXT = (
        "text, watermark, logo, signature, caption, subtitle, "
        "username, website, URL, copyright notice"
    )

    # ---------------------------------------------------------------------------
    # Presets — common combinations for different generation contexts
    # ---------------------------------------------------------------------------

    PRESETS: dict[str, list[str]] = {
        "photorealistic_portrait": [
            "ANATOMY", "QUALITY", "ANTI_ILLUSTRATION", "ANTI_AMATEUR",
            "COLOR", "LIGHTING", "TEXT",
        ],
        "photorealistic_scene": [
            "QUALITY", "ANTI_ILLUSTRATION", "ANTI_AMATEUR",
            "COMPOSITION", "COLOR", "LIGHTING", "TEXT",
        ],
        "cinematic_shot": [
            "ANATOMY", "QUALITY", "ANTI_ILLUSTRATION", "ANTI_AMATEUR",
            "COMPOSITION", "COLOR", "LIGHTING", "TEXT",
        ],
        "stylized": [
            "QUALITY", "TEXT", "ANATOMY",
        ],
        "video_generation": [
            "ANATOMY", "QUALITY", "ANTI_ILLUSTRATION", "ANTI_AMATEUR",
            "COLOR", "LIGHTING", "MOTION", "TEXT",
        ],
        "minimal": [
            "QUALITY", "TEXT",
        ],
    }

    @classmethod
    def get_segments(cls, *segment_names: str) -> list[str]:
        """Get specific negative prompt segments by name."""
        result = []
        for name in segment_names:
            value = getattr(cls, name.upper(), None)
            if value and isinstance(value, str):
                result.append(value)
        return result

    @classmethod
    def compose(cls, *segment_names: str) -> str:
        """Compose multiple segments into a single negative prompt string."""
        segments = cls.get_segments(*segment_names)
        return ", ".join(segments)

    @classmethod
    def from_preset(cls, preset: str) -> str:
        """Get a pre-composed negative prompt from a named preset."""
        segment_names = cls.PRESETS.get(preset, cls.PRESETS["cinematic_shot"])
        return cls.compose(*segment_names)

    @classmethod
    def for_shot(cls, *, animate: bool = False, style_profile: str = "") -> str:
        """Build a context-aware negative prompt for a shot specification.

        Args:
            animate: Whether this shot will be animated (adds motion artifacts).
            style_profile: DP style profile name — used to add style-specific negatives.

        Returns:
            Complete negative prompt string.
        """
        # Base cinematic negatives
        segments = ["ANATOMY", "QUALITY", "ANTI_ILLUSTRATION", "ANTI_AMATEUR",
                     "COMPOSITION", "COLOR", "LIGHTING", "TEXT"]

        if animate:
            segments.append("MOTION")

        base = cls.compose(*segments)

        # Add style-specific negatives
        style_negatives = _STYLE_NEGATIVES.get(style_profile, "")
        if style_negatives:
            return f"{base}, {style_negatives}"
        return base


# Style-profile-specific negatives — things each DP would *never* do
_STYLE_NEGATIVES: dict[str, str] = {
    "deakins": (
        "unmotivated light sources, garish neon color, shaky handheld camera, "
        "dutch angle, flashy lens flares, oversaturated color grading"
    ),
    "storaro": (
        "desaturated muted color, flat even lighting, monochromatic palette, "
        "documentary handheld, minimal color"
    ),
    "lubezki": (
        "artificial studio lighting, static locked camera, telephoto compression, "
        "neon colored light, heavy post-processing, extreme shallow DOF bokeh"
    ),
    "hoytema": (
        "clean digital noise-free, small sensor look, flat digital color, "
        "overly stabilized gimbal, synthetic digital sharpness"
    ),
}

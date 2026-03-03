"""Roger Deakins — the poet of controlled, motivated light."""

from auteur.knowledge.styles.base import StyleProfile

DEAKINS = StyleProfile(
    name="Roger Deakins CBE ASC BSC",
    philosophy="Light should always feel motivated — every source has a reason to exist in the "
    "scene. Deakins strips away artifice to find the emotional truth of a space. His "
    "work appears simple because the complexity is invisible. He uses single-source "
    "lighting philosophies, preferring to control one beautiful source rather than "
    "build elaborate multi-light setups. The result is images that feel inevitable "
    "rather than constructed.",
    preferred_lenses=["ARRI/Zeiss Master Primes", "ARRI Signature Primes", "27mm", "32mm", "40mm"],
    preferred_camera=["ARRI Alexa Mini LF", "ARRI Alexa 65", "ARRI Alexa Mini"],
    preferred_film_stock=["ARRI Alexa digital (LogC)", "Kodak Vision3 (earlier work)"],
    lighting_approach="Single-source motivated lighting. Deakins often starts with one light "
    "and asks 'what is the source?' — a window, a lamp, the sky. He then shapes "
    "that single motivation with negative fill, diffusion, and bounce rather "
    "than adding more lights. His night interiors often use a single soft source "
    "through a window with everything else falling away to darkness.",
    typical_ratios="4:1 to 8:1 — dramatic but readable shadows",
    color_temperature_preference="Naturalistic — matches what the source would actually be. "
    "Cool daylight, warm tungsten, mixed when motivated.",
    use_of_practicals="Practicals are the architecture of the lighting design. Deakins uses "
    "them as motivation — the visible lamp justifies the light direction. "
    "He'll often dim practicals to balance with his key light.",
    color_palette="Restrained, naturalistic, often desaturated. Cool-leaning for isolation "
    "and bleak landscapes (Fargo, Sicario), warm for intimacy (Shawshank). "
    "Never garish, never unmotivated color.",
    saturation_tendency="Slightly desaturated — reality with the volume turned down slightly",
    grading_style="Minimal intervention. Deakins grades to match what he saw on set — not to "
    "create a 'look.' The grade serves the story, not the colorist's reel.",
    composition_style="Classical, clean, purposeful. Deakins rarely uses flashy composition — "
    "his frames are balanced, readable, and serve the narrative. He favors "
    "center-weighted compositions and uses negative space deliberately. "
    "His wide shots have extraordinary depth layering.",
    preferred_aspect_ratio="Varies by project — 2.39:1 for epics (Blade Runner 2049), "
    "1.85:1 for dramas (Shawshank), 1.33:1 never.",
    use_of_depth="Selective focus — sharp subject with controlled background fall-off. "
    "Not extremely shallow; enough depth to read the environment.",
    movement_philosophy="The camera moves only when it serves the story. Deakins is not flashy "
    "with movement — slow dollies, controlled tracks, occasional Steadicam. "
    "The camera never calls attention to itself. Movement is invisible.",
    preferred_movement=["slow dolly", "subtle push-in", "controlled tracking", "static (frequently)"],
    signature_techniques=[
        "Single-source motivated lighting",
        "Silhouette against bright backgrounds",
        "Practical-motivated exposure",
        "Negative fill to shape faces",
        "Window light as primary key",
        "Extraordinary control of haze and atmosphere",
        "Long-lens compression for emotional isolation",
    ],
    notable_films=[
        "Blade Runner 2049", "1917", "Skyfall", "No Country for Old Men",
        "The Shawshank Redemption", "Sicario", "Prisoners", "Fargo",
    ],
    prompt_keywords=[
        "Deakins lighting", "motivated single source", "naturalistic cinematography",
        "controlled shadows", "atmospheric haze in light", "window light portrait",
        "silhouette against window", "restrained color palette", "invisible camera movement",
        "clean classical composition",
    ],
    negative_keywords=[
        "garish color", "unmotivated neon", "shaky handheld", "flashy camera moves",
        "oversaturated", "lens flare heavy", "Dutch angle",
    ],
)

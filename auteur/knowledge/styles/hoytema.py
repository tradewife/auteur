"""Hoyte van Hoytema FSF ASC — the architect of immersive, large-format spectacle."""

from auteur.knowledge.styles.base import StyleProfile

HOYTEMA = StyleProfile(
    name="Hoyte van Hoytema FSF ASC",
    philosophy="The audience should feel physically present inside the image. Van Hoytema "
    "champions IMAX large-format photography to create overwhelming scale and "
    "tactile detail. He combines this spectacle with intimate, handheld camerawork "
    "to bridge the gap between epic and personal. His images have extraordinary "
    "texture — grain, halation, optical imperfections are features, not flaws. "
    "He shoots on film whenever possible, believing in photochemical capture as "
    "a fundamentally different way of seeing.",
    preferred_lenses=[
        "Panavision System 65", "Hasselblad (modified for IMAX)", "Panavision Sphero 65",
        "IMAX-specific optics", "vintage large-format glass",
    ],
    preferred_camera=[
        "IMAX MSM 9802", "IMAX MKIV", "Panavision Panaflex System 65",
        "Panavision Millennium XL2", "ARRI Alexa LF (when digital required)",
    ],
    preferred_film_stock=[
        "Kodak Vision3 500T 5219 (65mm)", "Kodak Vision3 250D 5207 (65mm)",
        "IMAX 15-perf 65mm", "Kodak 200T 5213", "Kodak Double-X (B&W)",
    ],
    lighting_approach="Naturalistic but sculpted. Van Hoytema uses large soft sources that "
    "wrap around subjects — bounced light, book lights, and large diffusion "
    "frames. He embraces underexposure and shadow, pushing film stock to its "
    "limits. His lighting feels real but is carefully controlled. For Nolan's "
    "films, he creates lighting that works for IMAX's extraordinary latitude.",
    typical_ratios="3:1 to 6:1 — sculptural shadows, readable but dramatic",
    color_temperature_preference="Slightly warm-biased. Van Hoytema's images often have a warm "
    "amber quality, even in cool environments. He uses the inherent "
    "warmth of tungsten-balanced film stock as a baseline.",
    use_of_practicals="Integrated into the set design. Practicals in his films are functional "
    "and powerful — the cockpit lights in Dunkirk, the dustbowl light "
    "in Interstellar. They're not decorative but essential to the scene.",
    color_palette="Warm earth tones, amber, desaturated but rich. Interstellar's dusty "
    "amber-gold. Dunkirk's steely blue-grey with flashes of fire orange. "
    "Oppenheimer's hyper-rich Kodachrome colors for color sequences and "
    "stark high-contrast black and white for subjective sections.",
    saturation_tendency="Moderate — film stock gives inherent richness without digital push. "
    "Never garish, but not deliberately drained.",
    grading_style="Photochemical timing when possible. Van Hoytema prefers to achieve "
    "the look in-camera and through lab processing rather than digital "
    "grading. The DI is used for matching and cleanup, not for creating looks.",
    composition_style="IMAX-aware — Van Hoytema composes for massive screens, using the full "
    "1.43:1 IMAX frame for overwhelming scale and switching to 2.39:1 for "
    "intimate moments. His compositions have extraordinary detail density — "
    "the large format resolves faces in crowd shots, texture in landscapes. "
    "He favors close handheld work that contrasts with wide establishing shots.",
    preferred_aspect_ratio="1.43:1 IMAX (signature), switching to 2.39:1 within films. "
    "Also shoots 1.78:1 when IMAX isn't viable.",
    use_of_depth="Large format gives unique depth characteristics — sharp subject with "
    "beautiful, organic background fall-off that is different from small-format "
    "shallow DOF. The extra resolving power means backgrounds are detailed "
    "even when soft.",
    movement_philosophy="Handheld intimacy married to IMAX scale. Van Hoytema often operates "
    "handheld with enormous IMAX cameras, creating a paradox of epic "
    "format with documentary immediacy. The physicality of the heavy camera "
    "gives movement a weighty, grounded quality.",
    preferred_movement=[
        "handheld IMAX", "mounted vehicle shots", "Steadicam for set pieces",
        "static tripod for landscape scale", "close intimate handheld",
    ],
    signature_techniques=[
        "IMAX 65mm large-format photography",
        "Aspect ratio switching within a film (1.43:1 ↔ 2.39:1)",
        "Handheld IMAX camera operation",
        "Film stock pushed to extremes (underexposure, grain)",
        "Practical in-camera effects at IMAX scale",
        "Black and white intercut with color (Oppenheimer)",
        "Overwhelming scale contrasted with intimate close-ups",
        "Photochemical processing and lab timing",
    ],
    notable_films=[
        "Oppenheimer", "Tenet", "Dunkirk", "Interstellar",
        "Ad Astra", "Spectre", "Her", "Let the Right One In",
    ],
    prompt_keywords=[
        "IMAX large format", "65mm film grain", "Hoytema cinematography",
        "photochemical film look", "IMAX scale", "film grain texture",
        "warm amber earth tones", "handheld epic scale", "large format shallow depth",
        "Kodak film stock look",
    ],
    negative_keywords=[
        "clean digital", "noise-free", "small sensor look", "flat digital color",
        "overly stabilized", "synthetic sharpness",
    ],
)

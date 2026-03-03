"""Color theory — the emotional DNA of every frame.

Color is processed by the brain before conscious awareness. A viewer's emotional
response to a frame begins with color before they register composition, subject,
or content. This module encodes the language of cinematic color.
"""

# ---------------------------------------------------------------------------
# Color Palette Systems — harmony as emotion
# ---------------------------------------------------------------------------

COLOR_PALETTES: dict[str, dict] = {
    "complementary": {
        "description": "Two colors directly opposite on the wheel — maximum chromatic tension. "
        "Teal/orange is the blockbuster default because it simultaneously flatters skin "
        "(orange family) while creating visual pop against cool backgrounds (teal). "
        "Red/green for Christmas or horror. Blue/yellow for heroism.",
        "relationship": "opposite hues — maximum contrast and visual energy",
        "prompt_keywords": ["complementary color palette", "color contrast", "opposing hues"],
        "common_pairings": [
            ("teal", "orange"),
            ("blue", "amber"),
            ("red", "green"),
            ("purple", "gold"),
            ("cyan", "red-orange"),
        ],
    },
    "analogous": {
        "description": "Colors adjacent on the wheel — harmonious, unified, calming. Blue-teal-green "
        "for ocean/nature. Red-orange-yellow for warmth/fire. Creates a visual world where "
        "everything belongs together, nothing fights for attention.",
        "relationship": "adjacent hues — harmony and cohesion",
        "prompt_keywords": ["analogous color harmony", "unified color palette", "harmonious tones"],
        "common_pairings": [
            ("blue", "teal", "green"),
            ("red", "orange", "yellow"),
            ("purple", "blue", "teal"),
            ("yellow", "green", "teal"),
        ],
    },
    "triadic": {
        "description": "Three colors equally spaced on the wheel — vibrant, balanced, energetic. "
        "Red/blue/yellow is primary energy (comic books, pop art). More sophisticated triads "
        "use muted versions. Wes Anderson's palettes often approximate triadic relationships.",
        "relationship": "three equidistant hues — balanced vibrancy",
        "prompt_keywords": ["triadic color scheme", "three-color harmony", "vibrant balanced palette"],
        "common_pairings": [
            ("red", "blue", "yellow"),
            ("orange", "green", "purple"),
            ("teal", "magenta", "amber"),
        ],
    },
    "split_complementary": {
        "description": "One color plus the two colors adjacent to its complement. Less aggressive "
        "than pure complementary, more nuanced. Creates visual interest with more flexibility "
        "in how the palette is applied across the frame.",
        "relationship": "one hue + two flanking its opposite — nuanced contrast",
        "prompt_keywords": ["split-complementary palette", "nuanced color contrast"],
        "common_pairings": [
            ("blue", "red-orange", "yellow-orange"),
            ("red", "blue-green", "yellow-green"),
        ],
    },
    "monochromatic": {
        "description": "Single hue in varying saturations and values. The palette of memory, dream, "
        "and timelessness. A monochrome blue world is underwater/depression. Monochrome amber "
        "is nostalgia/memory. True black-and-white removes color entirely, forcing the viewer "
        "to engage with form, light, and texture.",
        "relationship": "single hue — variations in saturation and brightness only",
        "prompt_keywords": [
            "monochromatic palette",
            "single-hue color scheme",
            "tonal variations",
            "monochrome color grading",
        ],
        "common_pairings": [
            ("blues",),
            ("ambers",),
            ("greens",),
            ("reds",),
            ("black and white",),
        ],
    },
    "desaturated": {
        "description": "All colors muted, saturation pulled down. The palette of realism, war, "
        "depression, memory fading. Saving Private Ryan, The Road, Children of Men. "
        "Desaturation says 'this world has had the life drained from it.'",
        "relationship": "all hues suppressed — muted, washed out",
        "prompt_keywords": [
            "desaturated color palette",
            "muted tones",
            "washed-out colors",
            "drained color",
            "low saturation",
        ],
        "common_pairings": [
            ("muted olive", "desaturated blue", "grey-brown"),
            ("faded teal", "dusty rose", "slate"),
        ],
    },
}


# ---------------------------------------------------------------------------
# Color Grading Profiles — named looks
# ---------------------------------------------------------------------------

GRADING_PROFILES: dict[str, dict] = {
    "teal_orange": {
        "name": "Teal & Orange (Blockbuster)",
        "description": "The modern blockbuster default. Push shadows and cool tones toward teal, "
        "push skin tones and warm highlights toward orange. Creates maximum visual pop "
        "while flattering human subjects. So ubiquitous it has become visual shorthand "
        "for 'big budget movie.'",
        "shadows": "teal/cyan",
        "midtones": "slightly desaturated",
        "highlights": "warm orange/amber",
        "skin_tone_treatment": "pushed warm, golden",
        "prompt_keywords": [
            "teal and orange color grading",
            "blockbuster color grade",
            "Hollywood color palette",
            "cyan shadows orange highlights",
        ],
        "reference_films": ["Transformers", "Mad Max: Fury Road", "most MCU films"],
    },
    "bleach_bypass": {
        "name": "Bleach Bypass / Skip Bleach",
        "description": "Originally a photochemical process — retaining the silver in film stock "
        "after development. Creates a desaturated, high-contrast, gritty look with metallic "
        "highlights and crushed blacks. Skin tones become pallid and sickly. The look of "
        "war, dystopia, and moral decay.",
        "shadows": "deep, crushed black",
        "midtones": "desaturated, high-contrast",
        "highlights": "metallic silver, blown",
        "skin_tone_treatment": "pallid, desaturated, grey-shifted",
        "prompt_keywords": [
            "bleach bypass look",
            "desaturated high contrast",
            "silver-retained film look",
            "gritty metallic",
            "crushed blacks desaturated",
        ],
        "reference_films": ["Saving Private Ryan", "Minority Report", "Se7en"],
    },
    "cross_process": {
        "name": "Cross-Processing",
        "description": "Developing film in chemistry intended for a different stock — E6 in C41 or "
        "vice versa. Creates unpredictable color shifts, high saturation in some channels, "
        "total desaturation in others. Greens become electric, skin tones shift toward "
        "magenta or yellow. The look of fashion photography, music videos, and psychedelia.",
        "shadows": "shifted — often green or cyan",
        "midtones": "unpredictably saturated",
        "highlights": "blown with color casts",
        "skin_tone_treatment": "shifted — magenta, yellow, or green contamination",
        "prompt_keywords": [
            "cross-processed look",
            "color-shifted film",
            "oversaturated vintage",
            "psychedelic color cast",
        ],
        "reference_films": ["fashion editorials", "90s music videos", "Trainspotting"],
    },
    "day_for_night": {
        "name": "Day for Night",
        "description": "Shooting in daylight with underexposure and blue grading to simulate night. "
        "A classic (and sometimes obvious) technique. When done well, creates a stylized "
        "moonlit world. The sky remains too bright, shadows too open — a surreal middle "
        "ground between day and night that feels like a dream of night rather than night itself.",
        "shadows": "deep blue",
        "midtones": "blue-shifted, underexposed",
        "highlights": "cool, suppressed",
        "skin_tone_treatment": "cool, blue-shifted, slightly underexposed",
        "prompt_keywords": [
            "day for night",
            "blue-shifted night simulation",
            "moonlit blue tones",
            "stylized night exterior",
        ],
        "reference_films": ["classic Westerns", "Mad Max: Fury Road (brief)"],
    },
    "tobacco": {
        "name": "Tobacco / Amber Grade",
        "description": "Heavy warm shift across the entire image — amber/tobacco tones dominate. "
        "Mexico in Hollywood is always tobacco-graded. Creates a sense of heat, dust, "
        "foreignness, or period nostalgia. Controversial for its stereotypical use.",
        "shadows": "warm brown",
        "midtones": "amber/tobacco",
        "highlights": "golden/blown warm",
        "skin_tone_treatment": "warm, tanned, golden",
        "prompt_keywords": [
            "tobacco color grade",
            "amber warm tone",
            "golden sepia look",
            "warm desaturated amber",
        ],
        "reference_films": ["Traffic (Mexico scenes)", "Sicario", "Breaking Bad (Mexico)"],
    },
    "pastel_desaturated": {
        "name": "Pastel / Lifted Blacks",
        "description": "Shadows lifted (never true black), highlights pulled down (never true white), "
        "saturation reduced to pastels. Creates a flat, dreamy, Instagram-aesthetic look. "
        "The visual language of indie film, mumblecore, and millennial nostalgia.",
        "shadows": "lifted, milky, never true black",
        "midtones": "pastel, soft",
        "highlights": "rolled off, soft",
        "skin_tone_treatment": "soft, even, slightly desaturated",
        "prompt_keywords": [
            "lifted blacks",
            "pastel color grade",
            "faded film look",
            "milky shadows",
            "indie film color",
        ],
        "reference_films": ["Moonlight", "Lady Bird", "indie cinema"],
    },
    "neon_noir": {
        "name": "Neon Noir",
        "description": "Deep blacks contrasted with vivid neon colors — electric blue, hot pink, "
        "toxic green. The palette of cyberpunk, neo-noir, and urban nightlife. Shadows "
        "are absolute; colors are electric. The world is both seductive and threatening.",
        "shadows": "deep true black",
        "midtones": "selectively saturated by light source",
        "highlights": "neon-colored — pink, blue, green, purple",
        "skin_tone_treatment": "colored by ambient neon — unrealistic, stylized",
        "prompt_keywords": [
            "neon noir color palette",
            "cyberpunk neon colors",
            "electric blue and pink",
            "neon-lit darkness",
            "synthwave color grading",
        ],
        "reference_films": ["Blade Runner 2049", "Only God Forgives", "John Wick"],
    },
    "k_drama_clean": {
        "name": "K-Drama Clean / Asian Drama Grade",
        "description": "Bright, clean, slightly cool midtones with perfect skin rendering. Low contrast, "
        "high detail in faces, soft highlight rolloff. Shadows are open and clean. The aesthetic "
        "prioritizes flawless skin and emotional readability over dramatic contrast.",
        "shadows": "open, clean, slightly cool",
        "midtones": "clean, bright, low contrast",
        "highlights": "soft, rolled off, dreamy",
        "skin_tone_treatment": "perfected, smooth, bright, slightly cool",
        "prompt_keywords": [
            "clean bright color grade",
            "K-drama lighting",
            "soft skin rendering",
            "low contrast bright",
            "asian drama aesthetic",
        ],
        "reference_films": ["Korean drama productions", "Japanese cinema"],
    },
}


# ---------------------------------------------------------------------------
# Emotional Color Mapping — what colors make you feel
# ---------------------------------------------------------------------------

EMOTIONAL_COLOR_MAP: dict[str, dict] = {
    "red": {
        "emotions": ["passion", "danger", "violence", "love", "anger", "power", "urgency"],
        "cinematic_use": "Blood, roses, warning lights, stop signs, lipstick, fire. Red demands attention — "
        "the eye is drawn to red before any other color. In a frame of muted tones, a single "
        "red element becomes the visual anchor.",
        "prompt_keywords": ["red accent", "crimson", "blood red", "passionate red"],
    },
    "blue": {
        "emotions": ["sadness", "calm", "cold", "isolation", "trust", "technology", "melancholy"],
        "cinematic_use": "Night, water, screens, institutional walls, depression. Blue is the color of "
        "emotional distance. A blue-graded world is one where warmth has been withdrawn.",
        "prompt_keywords": ["cool blue tones", "melancholic blue", "cold blue palette", "deep blue"],
    },
    "green": {
        "emotions": ["nature", "sickness", "envy", "growth", "alien", "toxic", "organic"],
        "cinematic_use": "Forests, poison, the Matrix, jealousy, hospital fluorescents. Green in cinema "
        "is rarely neutral — it's either organic life or synthetic sickness.",
        "prompt_keywords": ["verdant green", "toxic green", "organic green tones", "emerald"],
    },
    "yellow": {
        "emotions": ["warmth", "caution", "madness", "optimism", "decay", "nostalgia"],
        "cinematic_use": "Sunshine, sodium vapor streetlights, old photographs, warning signs. "
        "Yellow can be joyful (sunlight) or nauseating (fluorescent buzz).",
        "prompt_keywords": ["golden yellow", "amber warmth", "sodium vapor yellow", "sunlit"],
    },
    "orange": {
        "emotions": ["warmth", "comfort", "sunset", "fire", "energy", "autumn"],
        "cinematic_use": "Firelight, sunset, autumn leaves, tungsten glow. Orange is domesticity "
        "and comfort — or the last light before darkness.",
        "prompt_keywords": ["warm orange glow", "sunset orange", "amber orange", "fire-lit"],
    },
    "purple": {
        "emotions": ["royalty", "mysticism", "decadence", "corruption", "spirituality"],
        "cinematic_use": "Throne rooms, nightclub lights, bruised skies, psychedelic visions. "
        "Purple is rare in nature, making it inherently artificial and otherworldly.",
        "prompt_keywords": ["regal purple", "mystical violet", "deep purple tones", "ultraviolet"],
    },
    "teal": {
        "emotions": ["modernity", "clinical", "underwater", "futurism", "melancholy"],
        "cinematic_use": "Hospital scrubs, ocean depths, modern architecture, sci-fi interfaces. "
        "Teal is blue with green's organic quality removed — clinical, modern, cool.",
        "prompt_keywords": ["teal tones", "cyan-teal", "cool teal", "modern teal palette"],
    },
    "black": {
        "emotions": ["death", "power", "elegance", "void", "mystery", "sophistication"],
        "cinematic_use": "Deep shadows, negative space, noir, formal wear. True black in cinema "
        "is a bold choice — most DPs prefer 'rich shadow' to absolute black.",
        "prompt_keywords": ["deep black shadows", "true black", "inky darkness", "void black"],
    },
    "white": {
        "emotions": ["purity", "sterility", "heaven", "clinical", "blank", "surrender"],
        "cinematic_use": "Hospitals, heaven, snow, overexposed memory, clinical spaces. "
        "White can be divine or terrifying depending on context.",
        "prompt_keywords": ["bright white", "overexposed white", "clinical white", "heavenly glow"],
    },
}

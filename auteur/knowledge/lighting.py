"""Lighting systems — the sculptor's chisel of cinematography.

Light is the primary medium of cinema. Before lens, before color, before
composition — light defines what the viewer sees and how they feel about it.
This module encodes the complete vocabulary of cinematic lighting.
"""

# ---------------------------------------------------------------------------
# Named Lighting Setups — the classical vocabulary
# ---------------------------------------------------------------------------

LIGHTING_SETUPS: dict[str, dict] = {
    "rembrandt": {
        "description": "Named after the painter's signature illumination. Key light positioned 45° "
        "to one side and slightly above, creating a triangle of light on the shadow-side cheek. "
        "The triangle should be no wider than the eye and no longer than the nose. This is the "
        "setup that says 'drama with dignity' — it sculpts the face into three dimensions while "
        "maintaining a sense of classical beauty.",
        "key_position": "45° camera-side, elevated 30-45°",
        "fill_approach": "minimal to moderate — the shadow defines the mood",
        "key_to_fill_ratio": "4:1 to 8:1",
        "mood": "dramatic, dignified, classical, thoughtful",
        "prompt_keywords": [
            "Rembrandt lighting",
            "dramatic side lighting",
            "triangle of light on cheek",
            "chiaroscuro portrait",
            "classical dramatic lighting",
        ],
        "best_for": ["drama", "portrait", "interview", "period film"],
    },
    "butterfly": {
        "description": "Also called Paramount lighting — the key light directly above and in front "
        "of the subject, creating a small butterfly-shaped shadow under the nose. This is the "
        "lighting of Hollywood glamour — it flattens facial features into their most symmetrical "
        "arrangement, minimizes texture, and creates catchlights in both eyes. Marlene Dietrich, "
        "Audrey Hepburn, every classic Hollywood headshot.",
        "key_position": "directly above lens axis, elevated 45-60°",
        "fill_approach": "bounce from below or reflector — softens under-chin shadow",
        "key_to_fill_ratio": "2:1 to 3:1",
        "mood": "glamorous, beautiful, symmetrical, classic Hollywood",
        "prompt_keywords": [
            "butterfly lighting",
            "Paramount glamour lighting",
            "overhead beauty light",
            "Hollywood glamour",
            "symmetrical face lighting",
        ],
        "best_for": ["beauty", "fashion", "glamour portrait", "classic Hollywood"],
    },
    "split": {
        "description": "Key light at exact 90° to the subject — one half of the face is lit, the "
        "other in complete shadow. The most dramatic of the classical setups. It bisects the "
        "subject into light and dark, literally visualizing duality, conflict, moral ambiguity. "
        "Harvey Two-Face didn't choose this lighting; it chose him.",
        "key_position": "90° to one side, at subject height",
        "fill_approach": "none to minimal — the darkness is the point",
        "key_to_fill_ratio": "8:1 to total shadow",
        "mood": "stark duality, moral conflict, dramatic tension, menace",
        "prompt_keywords": [
            "split lighting",
            "half-face shadow",
            "dramatic duality",
            "noir face lighting",
            "stark light and shadow",
        ],
        "best_for": ["villain introduction", "moral conflict", "noir", "psychological thriller"],
    },
    "loop": {
        "description": "A softer variation of Rembrandt — key at about 30-45° creating a small "
        "loop-shaped shadow from the nose on the opposite cheek. The shadow doesn't connect "
        "to the cheek shadow (unlike Rembrandt). Versatile, flattering, the workhorse of "
        "portrait and interview lighting.",
        "key_position": "30-45° camera-side, elevated 30°",
        "fill_approach": "moderate fill to keep shadows open",
        "key_to_fill_ratio": "2:1 to 4:1",
        "mood": "natural, flattering, approachable, professional",
        "prompt_keywords": [
            "loop lighting",
            "natural portrait lighting",
            "soft directional light",
            "flattering face lighting",
        ],
        "best_for": ["interview", "corporate", "naturalistic drama", "documentary"],
    },
    "broad": {
        "description": "The lit side of the face is turned toward camera (the broader visible area "
        "is illuminated). Opens up the face, makes it appear wider. Used to add visual weight "
        "to thin faces or create an open, accessible feeling.",
        "key_position": "lighting the camera-facing side of the turned face",
        "fill_approach": "moderate to bright",
        "key_to_fill_ratio": "2:1 to 3:1",
        "mood": "open, accessible, comfortable, bright",
        "prompt_keywords": [
            "broad lighting",
            "open face illumination",
            "bright approachable portrait",
        ],
        "best_for": ["commercial", "sitcom", "friendly portrait"],
    },
    "short": {
        "description": "The shadow side of the face is turned toward camera (the narrower visible "
        "area is illuminated). Creates more sculpting and drama than broad lighting. Slims "
        "the face, adds mystery. The default 'cinematic' choice for narrative work.",
        "key_position": "lighting the side of the face turned away from camera",
        "fill_approach": "controlled — shadows shape the face",
        "key_to_fill_ratio": "3:1 to 6:1",
        "mood": "sculpted, cinematic, mysterious, slimming",
        "prompt_keywords": [
            "short lighting",
            "sculpted face",
            "cinematic portrait lighting",
            "dramatic shadow side",
        ],
        "best_for": ["cinematic portrait", "drama", "mystery", "noir-lite"],
    },
    "noir": {
        "description": "High-contrast, low-key lighting dominated by shadow. Hard light sources "
        "create sharp shadows — venetian blind patterns, single bare-bulb practicals, shafts "
        "of light through doorways. The darkness is not absence of light; it is presence of "
        "menace. Ratios of 8:1 to total darkness. The world of Double Indemnity, The Third Man, "
        "Blade Runner.",
        "key_position": "varied — often low or extreme side angles",
        "fill_approach": "minimal or none — embrace the darkness",
        "key_to_fill_ratio": "8:1 to infinite (no fill)",
        "mood": "menacing, paranoid, morally corrupt, fatalistic",
        "prompt_keywords": [
            "film noir lighting",
            "hard shadow patterns",
            "venetian blind shadows",
            "low-key high contrast",
            "chiaroscuro noir",
            "single source hard light",
        ],
        "best_for": ["noir", "thriller", "detective", "crime drama"],
    },
    "silhouette": {
        "description": "Subject completely backlit with no fill — reduced to a shape, a form, "
        "an archetype. All detail is sacrificed for pure compositional power. The subject "
        "becomes a symbol rather than a person.",
        "key_position": "behind subject (backlight only)",
        "fill_approach": "none — the silhouette IS the image",
        "key_to_fill_ratio": "infinite (background to subject)",
        "mood": "mysterious, iconic, mythic, anonymous",
        "prompt_keywords": [
            "silhouette",
            "backlit figure",
            "figure against light",
            "iconic silhouette",
            "shadow figure",
        ],
        "best_for": ["title sequences", "mythic moments", "anonymity", "transition shots"],
    },
    "available_light": {
        "description": "Using only the light that exists in the environment — no artificial "
        "augmentation. This is the lighting of documentary truth. It requires a DP who can "
        "'see' what's available and position subjects to exploit it. Terrence Malick and "
        "Emmanuel Lubezki elevated this to art form in The New World and The Tree of Life.",
        "key_position": "whatever the environment provides",
        "fill_approach": "environmental bounce, neg fill at most",
        "key_to_fill_ratio": "varies wildly — controlled by positioning",
        "mood": "authentic, documentary, natural, truthful",
        "prompt_keywords": [
            "natural available light",
            "documentary lighting",
            "ambient illumination",
            "golden hour natural light",
            "window light portrait",
        ],
        "best_for": ["documentary", "naturalistic drama", "Malick-style", "verite"],
    },
    "high_key": {
        "description": "Low-contrast, bright, even illumination. Fill is nearly equal to key — "
        "shadows are minimal. The world of sitcoms, commercials, romantic comedies, "
        "and music videos. Everything is visible, nothing is hidden. The emotional "
        "equivalent of a bright, optimistic day.",
        "key_position": "broad, frontal, diffused",
        "fill_approach": "heavy — nearly matching key intensity",
        "key_to_fill_ratio": "1:1 to 2:1",
        "mood": "bright, optimistic, clean, commercial, youthful",
        "prompt_keywords": [
            "high-key lighting",
            "bright even illumination",
            "minimal shadows",
            "commercial bright",
            "clean studio lighting",
        ],
        "best_for": ["comedy", "commercial", "music video", "fashion"],
    },
    "chiaroscuro": {
        "description": "The Caravaggio technique adapted for cinema. Extreme contrast between "
        "light and dark with careful attention to the gradation between them. Unlike noir "
        "(which uses hard light), chiaroscuro often uses softer sources to create rich, "
        "painterly transitions from light to shadow. The Godfather's office scenes.",
        "key_position": "overhead or high side — allowing rich shadow gradation",
        "fill_approach": "minimal — controlled falloff is essential",
        "key_to_fill_ratio": "6:1 to 12:1",
        "mood": "painterly, dramatic, Renaissance, spiritual, contemplative",
        "prompt_keywords": [
            "chiaroscuro lighting",
            "Caravaggio lighting",
            "painterly light and shadow",
            "Renaissance dramatic lighting",
            "Godfather lighting",
        ],
        "best_for": ["period drama", "religious imagery", "prestige film", "art house"],
    },
    "neon_practical": {
        "description": "The lighting of the urban night — neon signs, LED strips, car headlights, "
        "screen glow. Multiple color temperatures coexist in the same frame. Michael Mann "
        "and Nicolas Winding Refn made this a genre. The light is the set design.",
        "key_position": "practical sources within the scene",
        "fill_approach": "other practical sources — no traditional key/fill",
        "key_to_fill_ratio": "varies — driven by practical placement",
        "mood": "urban, nocturnal, electric, dangerous, seductive",
        "prompt_keywords": [
            "neon-lit scene",
            "urban night lighting",
            "mixed color temperature neon",
            "practical neon lighting",
            "cyberpunk lighting",
            "Drive movie lighting",
        ],
        "best_for": ["neo-noir", "cyberpunk", "nightlife", "urban thriller", "music video"],
    },
    "golden_hour": {
        "description": "The 20-30 minutes before sunset or after sunrise. The sun is low, warm "
        "(2500-3500K), and the light wraps horizontally rather than falling vertically. "
        "Shadows are long, the world glows amber. Terrence Malick builds entire films around "
        "this light. It is ephemeral and impossible to fake convincingly.",
        "key_position": "low angle natural sun — horizontal wrap",
        "fill_approach": "sky provides natural fill, bounce cards optional",
        "key_to_fill_ratio": "2:1 to 4:1 (naturally)",
        "mood": "romantic, nostalgic, warm, fleeting, beautiful",
        "prompt_keywords": [
            "golden hour light",
            "magic hour warm glow",
            "low sun amber light",
            "long shadows warm light",
            "sunset backlight",
            "Malick golden hour",
        ],
        "best_for": ["romance", "nostalgia", "beauty", "landscape", "emotional climax"],
    },
    "blue_hour": {
        "description": "The 20-30 minutes after sunset or before sunrise. The sky becomes a natural "
        "soft blue fill while artificial lights (warm tungsten) begin to dominate. The contrast "
        "between cool ambient and warm practicals creates beautiful complementary color tension. "
        "Michael Mann's preferred shooting window.",
        "key_position": "ambient sky + practical warm sources",
        "fill_approach": "the blue sky IS the fill",
        "key_to_fill_ratio": "naturally balanced",
        "mood": "melancholic, transitional, liminal, beautiful sadness",
        "prompt_keywords": [
            "blue hour light",
            "twilight ambient",
            "cool blue sky warm practicals",
            "dusk lighting",
            "Michael Mann twilight",
        ],
        "best_for": ["thriller", "transitional moments", "melancholy", "urban exteriors"],
    },
}


# ---------------------------------------------------------------------------
# Color Temperature — emotion in Kelvin
# ---------------------------------------------------------------------------

COLOR_TEMPERATURES: dict[str, dict] = {
    "candlelight_1800K": {
        "kelvin": 1800,
        "character": "Deep amber-orange. The most intimate artificial light. Barry Lyndon was lit "
        "entirely by candlelight using NASA lenses. At this temperature, skin glows like "
        "old paintings. Shadows are deep and warm.",
        "emotion": "intimacy, antiquity, romance, vulnerability, warmth",
        "prompt_keywords": ["candlelight warmth", "deep amber glow", "intimate warm light", "Barry Lyndon candlelight"],
    },
    "tungsten_2700K": {
        "kelvin": 2700,
        "character": "Classic incandescent bulb warmth. The 'home' light that humans have been "
        "conditioned to associate with safety, evening, and domestic comfort. Standard "
        "household bulbs, table lamps, bedside lights.",
        "emotion": "domestic comfort, evening, warmth, safety, nostalgia",
        "prompt_keywords": ["warm tungsten light", "household bulb warmth", "domestic warm glow", "cozy interior light"],
    },
    "warm_tungsten_3200K": {
        "kelvin": 3200,
        "character": "Studio tungsten standard. Slightly less amber than household bulbs — the "
        "classic movie light color. Most fresnel and tungsten film lights are rated here. "
        "Warm but controlled, professional but inviting.",
        "emotion": "professional warmth, cinematic, inviting, interior",
        "prompt_keywords": ["studio tungsten", "3200K film lighting", "warm cinema light", "professional warm"],
    },
    "warm_white_3500K": {
        "kelvin": 3500,
        "character": "The crossover point — neither distinctly warm nor cool. Common in modern "
        "office spaces and retail. Neutral but with a hint of warmth that prevents sterility.",
        "emotion": "neutral comfort, commercial, modern",
        "prompt_keywords": ["warm white LED", "modern interior light", "neutral warm"],
    },
    "neutral_4300K": {
        "kelvin": 4300,
        "character": "True neutral — midpoint between tungsten and daylight. Fluorescent tubes, "
        "some LED panels. Neither inviting nor alienating. The light of institutions — "
        "hospitals, offices, bureaucracy.",
        "emotion": "institutional, neutral, bureaucratic, liminal",
        "prompt_keywords": ["neutral fluorescent", "institutional light", "office lighting", "cool neutral"],
    },
    "daylight_5600K": {
        "kelvin": 5600,
        "character": "Standard daylight — midday sun, HMI film lights, daylight-balanced LEDs. "
        "Clean, clear, democratic light. Everything is visible and honest. The world at "
        "noon is equally lit and equally exposed.",
        "emotion": "clarity, truth, openness, democracy, energy",
        "prompt_keywords": ["daylight balanced", "clean daylight", "5600K natural light", "midday sun clarity"],
    },
    "overcast_6500K": {
        "kelvin": 6500,
        "character": "Cool daylight — overcast sky, open shade, north-facing windows. A gentle "
        "blue bias that creates subtle melancholy. Skin tones cool slightly. The light of "
        "Scandinavian cinema — contemplative, subdued, honest.",
        "emotion": "melancholy, contemplation, subdued, Scandinavian, honest sadness",
        "prompt_keywords": [
            "overcast cool light",
            "Scandinavian daylight",
            "cool natural shade",
            "melancholic daylight",
            "soft overcast",
        ],
    },
    "blue_sky_9000K": {
        "kelvin": 9000,
        "character": "Deep blue ambient — open shade lit only by blue sky, not direct sun. "
        "Strongly cool. Subjects appear pallid, environments feel cold and alienating. "
        "The color temperature of abandonment.",
        "emotion": "cold alienation, isolation, depression, clinical detachment",
        "prompt_keywords": [
            "cold blue light",
            "alienating cool light",
            "blue shade",
            "cold ambient",
            "clinical blue",
        ],
    },
    "moonlight_mixed": {
        "kelvin": 4100,
        "character": "Cinematic moonlight is traditionally rendered as cool blue (though real "
        "moonlight is actually close to daylight). The convention uses a blue-gelled "
        "key at low intensity — 'day for night' if shot during day, or actual night "
        "with powerful blue-gelled sources. The psychological association is so strong "
        "that warm moonlight feels 'wrong' to audiences.",
        "emotion": "mystery, romance, danger, nocturnal beauty, dreamlike",
        "prompt_keywords": [
            "cinematic moonlight",
            "blue moonlit scene",
            "night exterior blue key",
            "moonlight blue wash",
            "romantic moonlight",
        ],
    },
}


# ---------------------------------------------------------------------------
# Lighting Ratios — the math of mood
# ---------------------------------------------------------------------------

LIGHTING_RATIOS: dict[str, dict] = {
    "1:1": {
        "ratio": "1:1",
        "stops_difference": 0,
        "character": "Completely flat — no shadow modeling at all. Used in high-key commercial, "
        "comedy, or deliberately anti-cinematic work. Everything is equally visible.",
        "mood": "flat, commercial, democratic, anti-dramatic",
        "prompt_keywords": ["flat even lighting", "no shadows", "high-key flat"],
    },
    "2:1": {
        "ratio": "2:1",
        "stops_difference": 1,
        "character": "Subtle modeling. The shadow side is one stop darker — barely noticeable "
        "to untrained eyes but enough to create three-dimensional form. Natural, flattering. "
        "The standard for beauty and commercial portrait work.",
        "mood": "natural, subtle, flattering, three-dimensional",
        "prompt_keywords": ["subtle light modeling", "natural portrait light", "gentle shadow"],
    },
    "4:1": {
        "ratio": "4:1",
        "stops_difference": 2,
        "character": "The cinematic sweet spot. Two stops between lit and shadow side creates "
        "clearly visible shadow while maintaining detail in the dark areas. Most narrative "
        "cinema lives in this range. Dramatic enough to feel intentional, controlled enough "
        "to read faces in shadow.",
        "mood": "cinematic, dramatic, controlled, narrative",
        "prompt_keywords": ["cinematic lighting ratio", "dramatic portrait", "visible shadow detail"],
    },
    "8:1": {
        "ratio": "8:1",
        "stops_difference": 3,
        "character": "Deep noir territory. Three stops means the shadow side is approaching black "
        "on many displays. Detail exists but barely. This is where lighting becomes "
        "sculpture — the key light carves the subject out of darkness.",
        "mood": "noir, mysterious, threatening, carved from shadow",
        "prompt_keywords": ["noir lighting ratio", "deep shadows", "carved from darkness", "heavy contrast"],
    },
    "16:1": {
        "ratio": "16:1",
        "stops_difference": 4,
        "character": "Extreme. Four stops means the shadow side is essentially black — only "
        "highlights and the lit portion of the subject are visible. Used for extreme "
        "dramatic effect, horror, or Caravaggio-level chiaroscuro.",
        "mood": "extreme drama, horror, Caravaggio, overwhelming contrast",
        "prompt_keywords": ["extreme contrast", "Caravaggio ratio", "subjects in near-total darkness"],
    },
}


# ---------------------------------------------------------------------------
# Light Modifiers — tools of sculpting
# ---------------------------------------------------------------------------

LIGHT_MODIFIERS: dict[str, dict] = {
    "book_light": {
        "description": "Light bounced off a large surface (usually white poly or fabric), then "
        "passed through a diffusion frame. Creates extremely soft, wrapping light with "
        "no visible source direction. The most expensive-looking lighting technique — "
        "used in high-end beauty, commercial, and prestige film.",
        "quality": "ultra-soft, wrapping, sourceless",
        "prompt_keywords": ["ultra-soft diffused light", "book light beauty", "wrapping soft illumination"],
    },
    "neg_fill": {
        "description": "A black surface (flag, floppy, duvetyne) placed opposite the key light to "
        "absorb reflected fill and deepen shadows. The subtractive complement to additive "
        "lighting — sometimes controlling what light DOESN'T reach the subject is more "
        "important than what does.",
        "quality": "shadow-deepening, contrast-enhancing",
        "prompt_keywords": ["negative fill", "enhanced shadow contrast", "controlled shadow depth"],
    },
    "china_ball": {
        "description": "A paper lantern with a bare bulb inside — creates a soft, omnidirectional "
        "glow. Cheap, fast to rig, and produces beautiful overhead softness. The secret "
        "weapon of low-budget cinematography. Can be hung anywhere and moved quickly.",
        "quality": "soft, warm, omnidirectional, overhead ambient",
        "prompt_keywords": ["soft overhead glow", "lantern light", "warm ambient overhead"],
    },
    "fresnel": {
        "description": "The classic film light — a lens focuses the beam into a controllable "
        "cone. Can be spotted (narrow, intense) or flooded (wide, softer). The backbone "
        "of studio lighting for a century.",
        "quality": "controllable — hard when spotted, moderately soft when flooded",
        "prompt_keywords": ["focused directional beam", "studio film light", "controllable spotlight"],
    },
    "bare_bulb": {
        "description": "An unmodified light source — raw, hard, omnidirectional. Creates stark "
        "shadows in every direction. The interrogation lamp, the swinging single bulb, "
        "the construction site work light. Ugly and honest.",
        "quality": "hard, omnidirectional, raw, unflattering",
        "prompt_keywords": ["bare bulb harsh light", "single exposed bulb", "raw industrial light"],
    },
    "gobo_cucaloris": {
        "description": "A patterned flag placed between light and subject to create shadow patterns. "
        "Tree branch shadows, venetian blind patterns, abstract shapes. The texture of "
        "light itself becomes a compositional element.",
        "quality": "patterned, textured shadows",
        "prompt_keywords": [
            "dappled shadow pattern",
            "venetian blind light",
            "tree branch shadows",
            "patterned light texture",
        ],
    },
    "diffusion_frame": {
        "description": "A frame of translucent fabric (silk, grid cloth, 250, 216) placed between "
        "source and subject. Converts hard light to soft. Different grades provide different "
        "softness — from barely perceptible (1/4 grid) to complete wash (heavy silk).",
        "quality": "variable soft — from lightly diffused to completely wrapped",
        "prompt_keywords": ["diffused soft light", "silk-filtered light", "soft-box quality"],
    },
}


# ---------------------------------------------------------------------------
# Atmospheric Effects — the air as canvas
# ---------------------------------------------------------------------------

ATMOSPHERICS: dict[str, dict] = {
    "haze": {
        "description": "Light atmospheric haze that makes light beams visible — volumetric shafts "
        "cutting through the air. Creates visual depth by separating planes. The standard "
        "atmosphere for most cinematic interiors.",
        "prompt_keywords": [
            "atmospheric haze",
            "volumetric light shafts",
            "visible light beams",
            "hazy atmosphere",
            "god rays",
        ],
    },
    "fog": {
        "description": "Dense atmosphere that obscures detail, softens everything, and creates "
        "a sense of enclosing mystery. Light scatters in all directions — sources become "
        "glowing orbs rather than defined beams. The world shrinks to immediate proximity.",
        "prompt_keywords": [
            "dense fog",
            "fog-shrouded scene",
            "atmospheric fog",
            "obscured visibility",
            "mysterious fog",
        ],
    },
    "smoke": {
        "description": "Denser and more turbulent than haze. Creates swirling, unpredictable "
        "light patterns. War films, fire aftermath, industrial settings. Unlike haze, "
        "smoke has visible movement and texture.",
        "prompt_keywords": [
            "smoke-filled atmosphere",
            "swirling smoke and light",
            "smoky interior",
            "industrial smoke",
        ],
    },
    "dust_particles": {
        "description": "Visible particles catching light in shafts — the old attic, the abandoned "
        "warehouse, the sunbeam through a barn. Creates a sense of time, age, neglect, "
        "or magical discovery.",
        "prompt_keywords": [
            "dust particles in light",
            "dusty light shaft",
            "particles catching sunbeam",
            "motes of dust in air",
        ],
    },
    "rain": {
        "description": "Rain is a lighting element as much as a weather effect. Backlit rain becomes "
        "a curtain of silver streaks. Rain creates reflections on every surface — wet streets "
        "become mirrors, doubling the light sources. Blade Runner is a masterclass in rain-as-light.",
        "prompt_keywords": [
            "rain-slicked reflections",
            "backlit rain streaks",
            "wet street reflections",
            "rain-soaked night",
            "cinematic rain",
        ],
    },
    "steam": {
        "description": "Slow-moving, soft atmospheric element. Bathhouses, kitchens, subway grates, "
        "breath in cold air. Creates soft, localized atmosphere that wraps around subjects.",
        "prompt_keywords": [
            "steam atmosphere",
            "steamy soft diffusion",
            "vapor in light",
            "steam-wrapped subject",
        ],
    },
}

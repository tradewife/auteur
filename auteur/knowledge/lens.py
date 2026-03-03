"""Lens knowledge — the glass between reality and the viewer's perception.

Lenses are not neutral translators. Each focal length imposes a psychological
framework on the viewer. Each lens family has optical DNA that colors every
frame. This module encodes that knowledge.
"""

from auteur.knowledge.ontology import BokehCharacter

# ---------------------------------------------------------------------------
# Focal Length Psychology — how mm shapes meaning
# ---------------------------------------------------------------------------

FOCAL_LENGTHS: dict[str, dict] = {
    "8mm_fisheye": {
        "focal_length_mm": 8,
        "field_of_view": "180°",
        "psychology": "Total distortion of reality. The world bends around the subject. "
        "Surveillance, paranoia, alien perspective, skateboard videos, music videos. "
        "Nothing filmed through a fisheye is trustworthy.",
        "distortion": "extreme_barrel",
        "perspective_effect": "massive exaggeration — noses enormous, backgrounds impossibly distant",
        "prompt_keywords": [
            "fisheye lens distortion",
            "extreme wide-angle warping",
            "barrel distortion",
            "surveillance perspective",
            "warped reality",
        ],
        "best_for": ["music video", "horror POV", "skateboarding", "surveillance aesthetic"],
    },
    "14mm": {
        "focal_length_mm": 14,
        "field_of_view": "114°",
        "psychology": "Existential distortion. The world stretches away from the subject — "
        "they exist in a vast, distorted space that feels psychologically unstable. "
        "Emmanuel Lubezki used ultra-wide primes to create the immersive, disorienting "
        "spaces in The Revenant and Birdman.",
        "distortion": "strong_barrel",
        "perspective_effect": "dramatic size exaggeration, deep perspective convergence",
        "prompt_keywords": [
            "ultra-wide angle",
            "dramatic perspective",
            "environmental immersion",
            "perspective distortion",
            "vast interior space",
        ],
        "best_for": ["immersive environments", "architectural", "claustrophobic interiors made vast"],
    },
    "18mm": {
        "focal_length_mm": 18,
        "field_of_view": "100°",
        "psychology": "Wide environmental storytelling with noticeable but controlled distortion. "
        "The viewer feels placed inside the scene. Good for establishing shots that also "
        "include foreground interest. Wes Anderson uses wider lenses for his geometric compositions.",
        "distortion": "moderate_barrel",
        "perspective_effect": "strong foreground/background separation, noticeable convergence",
        "prompt_keywords": [
            "wide-angle environmental",
            "deep space composition",
            "immersive wide shot",
            "environmental storytelling",
        ],
        "best_for": ["establishing shots", "production design showcase", "group scenes"],
    },
    "24mm": {
        "focal_length_mm": 24,
        "field_of_view": "84°",
        "psychology": "The classic environmental lens. Wide enough to breathe, controlled enough "
        "to not distort. Subjects exist within their world — the environment is as much a "
        "character as the person. Steven Spielberg's go-to for walk-and-talk scenes.",
        "distortion": "slight_barrel",
        "perspective_effect": "environment prominent, natural depth layering",
        "prompt_keywords": [
            "wide-angle",
            "environmental portrait",
            "contextual framing",
            "walk-and-talk",
            "subject in environment",
        ],
        "best_for": ["walk-and-talk", "environmental portrait", "interior establishing"],
    },
    "28mm": {
        "focal_length_mm": 28,
        "field_of_view": "75°",
        "psychology": "Stanley Kubrick's favorite focal length. Wide enough for his obsessive "
        "symmetrical compositions, narrow enough for the one-point perspective corridors "
        "of The Shining. A versatile 'reporter's lens' — captures enough context without "
        "obvious distortion.",
        "distortion": "minimal_barrel",
        "perspective_effect": "balanced — environment visible without overwhelming subject",
        "prompt_keywords": [
            "Kubrick-wide",
            "symmetrical composition",
            "one-point perspective",
            "balanced environmental",
            "reportage wide",
        ],
        "best_for": ["symmetrical compositions", "corridor shots", "documentary", "street"],
    },
    "35mm": {
        "focal_length_mm": 35,
        "field_of_view": "63°",
        "psychology": "The intimate-environmental sweet spot. Wide enough to show context, close "
        "enough to feel personal. This is the focal length of 'I am standing next to this "
        "person, in their space, experiencing what they experience.' The most commonly used "
        "focal length in narrative cinema. Virtually no distortion — what you see feels true.",
        "distortion": "negligible",
        "perspective_effect": "natural human-adjacent, honest spatial relationships",
        "prompt_keywords": [
            "35mm lens",
            "intimate environmental",
            "natural perspective",
            "documentary intimacy",
            "classic cinema focal length",
        ],
        "best_for": ["dialogue scenes", "intimate drama", "documentary", "naturalistic storytelling"],
    },
    "50mm": {
        "focal_length_mm": 50,
        "field_of_view": "47°",
        "psychology": "The 'human eye' — though this is a myth (human vision is more complex), "
        "50mm on full frame approximates the field of view and perspective that feels most "
        "'normal' to viewers. No distortion, no compression. It simply records. This neutrality "
        "makes it the lens of documentary truth, realism, and the Dogme 95 movement.",
        "distortion": "none",
        "perspective_effect": "neutral — what the eye expects, no editorial commentary",
        "prompt_keywords": [
            "50mm normal lens",
            "human eye perspective",
            "documentary realism",
            "neutral observation",
            "honest framing",
        ],
        "best_for": ["realism", "documentary", "dialogue close-ups", "natural portraits"],
    },
    "65mm": {
        "focal_length_mm": 65,
        "field_of_view": "38°",
        "psychology": "Gentle compression begins. The subject starts to separate from the environment "
        "not through depth-of-field alone but through perspective flattening. Backgrounds "
        "feel closer, more intimate. A beautiful portrait length that flatters faces without "
        "obvious compression.",
        "distortion": "none",
        "perspective_effect": "gentle compression, backgrounds drawn closer",
        "prompt_keywords": [
            "mild telephoto",
            "gentle compression",
            "flattering portrait",
            "intimate close-up",
        ],
        "best_for": ["flattering close-ups", "emotional dialogue", "beauty work"],
    },
    "85mm": {
        "focal_length_mm": 85,
        "field_of_view": "29°",
        "psychology": "The portrait master. 85mm compresses perspective just enough to flatten "
        "facial features into their most universally flattering arrangement. Noses appear "
        "proportional, ears recede, the face becomes a plane of beauty. At wide apertures, "
        "the background dissolves into pure texture. The lens of desire, beauty, and isolation.",
        "distortion": "none",
        "perspective_effect": "flattering compression, background simplified to texture",
        "prompt_keywords": [
            "85mm portrait",
            "beautiful bokeh",
            "subject isolation",
            "flattering facial compression",
            "portrait photography",
        ],
        "best_for": ["beauty", "portrait", "fashion", "emotional close-up"],
    },
    "100mm": {
        "focal_length_mm": 100,
        "field_of_view": "24°",
        "psychology": "Moderate telephoto. The subject is observed from a respectful distance. "
        "Compression flattens spatial relationships — depth layers stack up. This creates "
        "a sense of surveillance or observation. The viewer is watching, not participating.",
        "distortion": "none",
        "perspective_effect": "noticeable compression, depth planes stacking",
        "prompt_keywords": [
            "telephoto compression",
            "observational distance",
            "stacked depth planes",
            "surveillance feel",
        ],
        "best_for": ["observational", "thriller tension", "compressed landscapes"],
    },
    "135mm": {
        "focal_length_mm": 135,
        "field_of_view": "18°",
        "psychology": "Compressed isolation. The subject is severed from their environment. "
        "Background becomes an abstract wash of color and light. Depth planes compress — "
        "a person 50 feet from a building appears to be standing right against it. "
        "Creates claustrophobia in open spaces. The lens of loneliness and surveillance.",
        "distortion": "none",
        "perspective_effect": "strong compression, spatial relationships flattened",
        "prompt_keywords": [
            "telephoto isolation",
            "compressed perspective",
            "claustrophobic compression",
            "background abstraction",
            "emotional isolation",
        ],
        "best_for": ["isolation", "surveillance", "compressed urban", "sports emotion"],
    },
    "200mm": {
        "focal_length_mm": 200,
        "field_of_view": "12°",
        "psychology": "Voyeuristic. The viewer is far from the subject — watching through a "
        "telescope, a sniper scope, binoculars. Extreme compression stacks everything into "
        "flat planes. Heat shimmer and atmospheric haze become visible. The lens says "
        "'you are not supposed to be seeing this.'",
        "distortion": "none",
        "perspective_effect": "extreme compression, everything flattened into planes",
        "prompt_keywords": [
            "long telephoto",
            "voyeuristic distance",
            "extreme compression",
            "heat shimmer",
            "atmospheric haze",
            "surveillance long lens",
        ],
        "best_for": ["voyeurism", "paparazzi aesthetic", "wildlife", "war journalism"],
    },
    "300mm_plus": {
        "focal_length_mm": 300,
        "field_of_view": "8°",
        "psychology": "Maximum voyeuristic distance. The viewer is a spy, a predator, a god. "
        "Total spatial compression — backgrounds loom impossibly close to subjects. "
        "Atmospheric interference becomes part of the image. Used in sports for the 'face "
        "in the crowd' isolation and in surveillance thrillers.",
        "distortion": "none",
        "perspective_effect": "total compression, atmosphere visible as texture",
        "prompt_keywords": [
            "super-telephoto",
            "extreme isolation",
            "atmospheric compression",
            "paparazzi",
            "wildlife photography",
        ],
        "best_for": ["sports", "wildlife", "surveillance thriller", "atmospheric compression"],
    },
}


# ---------------------------------------------------------------------------
# Lens Families — optical DNA
# ---------------------------------------------------------------------------

LENS_FAMILIES: dict[str, dict] = {
    "cooke_s4": {
        "name": "Cooke S4/i",
        "manufacturer": "Cooke Optics",
        "character": "The 'Cooke Look' — warm, gentle, human. Micro-contrast is lower than clinical "
        "lenses, creating a three-dimensional quality where subjects seem to glow against "
        "soft backgrounds. Skin tones are rendered with extraordinary warmth and forgiveness. "
        "The lens equivalent of golden hour.",
        "color_rendering": "warm, slightly amber-shifted, forgiving skin tones",
        "contrast": "medium — gentle micro-contrast, three-dimensional rendering",
        "bokeh": BokehCharacter.SMOOTH,
        "flare_character": "gentle, warm flares — controlled and pleasing",
        "prompt_keywords": [
            "Cooke lens warmth",
            "gentle micro-contrast",
            "three-dimensional rendering",
            "warm skin tones",
            "creamy background separation",
        ],
        "notable_films": ["The King's Speech", "Skyfall (some scenes)", "1917"],
    },
    "cooke_speed_panchro": {
        "name": "Cooke Speed Panchro",
        "manufacturer": "Cooke Optics",
        "character": "Vintage Cooke character from the 1920s-60s. Lower contrast, visible aberrations, "
        "beautiful halation around highlights. Warm and imperfect in a way that feels like "
        "history itself is being projected. Modern reissues capture this character.",
        "color_rendering": "warm, lower saturation, period-authentic",
        "contrast": "low — vintage rendering, highlight bloom",
        "bokeh": BokehCharacter.SWIRL,
        "flare_character": "prominent warm flares, halation, low-contrast blooming",
        "prompt_keywords": [
            "vintage Cooke",
            "Speed Panchro character",
            "warm vintage rendering",
            "halation highlights",
            "period film look",
        ],
        "notable_films": ["period films", "The Grand Budapest Hotel (vintage lenses)"],
    },
    "zeiss_master_prime": {
        "name": "Zeiss Master Prime",
        "manufacturer": "Carl Zeiss",
        "character": "Clinical precision. Zeiss Master Primes are the scalpels of cinema glass — "
        "extraordinary sharpness corner-to-corner, high contrast, neutral color. They do not "
        "editorialize; they present reality with almost forensic accuracy. When you want the "
        "image to feel 'true' rather than 'beautiful', this is the glass.",
        "color_rendering": "neutral, accurate, slight cool bias",
        "contrast": "high — clinical micro-contrast, razor resolution",
        "bokeh": BokehCharacter.SMOOTH,
        "flare_character": "minimal, controlled — ghosts and veiling rare",
        "prompt_keywords": [
            "Zeiss clinical sharpness",
            "razor-sharp detail",
            "high contrast",
            "neutral color rendering",
            "forensic clarity",
        ],
        "notable_films": ["Zodiac", "The Social Network", "Mindhunter"],
    },
    "zeiss_super_speed": {
        "name": "Zeiss Super Speed",
        "manufacturer": "Carl Zeiss",
        "character": "The workhorse of 1970s-80s cinema. Fast (T1.3), slightly softer than modern "
        "Zeiss at wide apertures, with a character that many DPs describe as 'honest but "
        "gentle'. Less clinical than Master Primes — a warmth that comes from the imperfections.",
        "color_rendering": "neutral to slightly warm, honest",
        "contrast": "medium-high, softens at wide apertures",
        "bokeh": BokehCharacter.SMOOTH,
        "flare_character": "moderate — period-appropriate flaring",
        "prompt_keywords": [
            "Zeiss Super Speed character",
            "1970s cinema look",
            "fast lens softness",
            "honest rendering",
        ],
        "notable_films": ["Barry Lyndon (some scenes)", "numerous 70s/80s classics"],
    },
    "panavision_c_series": {
        "name": "Panavision C-Series Anamorphic",
        "manufacturer": "Panavision",
        "character": "Vintage anamorphic magic. The C-Series lenses produce oval bokeh, blue "
        "horizontal lens flares, visible barrel distortion at wider focal lengths, and "
        "that unmistakable 2.39:1 anamorphic breathing. Focus breathing causes the frame "
        "to subtly shift when pulling focus — a 'living' quality unique to anamorphic.",
        "color_rendering": "warm, slightly desaturated, vintage character",
        "contrast": "medium-low, beautiful highlight rolloff",
        "bokeh": BokehCharacter.OVAL,
        "flare_character": "signature blue horizontal streaks — the anamorphic look",
        "prompt_keywords": [
            "anamorphic lens flare",
            "oval bokeh",
            "horizontal blue flares",
            "anamorphic squeeze",
            "2.39:1 widescreen",
            "vintage anamorphic character",
        ],
        "notable_films": ["Blade Runner", "Interstellar", "Star Wars (original trilogy)"],
    },
    "panavision_g_series": {
        "name": "Panavision G-Series Anamorphic",
        "manufacturer": "Panavision",
        "character": "Modern anamorphic — retains the scope feel and oval bokeh but with dramatically "
        "improved sharpness and reduced aberrations. The flares are more controlled. For DPs "
        "who want the anamorphic frame without the vintage softness.",
        "color_rendering": "neutral, modern",
        "contrast": "high for anamorphic, sharp corner-to-corner",
        "bokeh": BokehCharacter.OVAL,
        "flare_character": "controlled anamorphic flares, less dramatic than C-Series",
        "prompt_keywords": [
            "modern anamorphic",
            "controlled lens flare",
            "sharp anamorphic",
            "oval bokeh",
            "clean widescreen",
        ],
        "notable_films": ["No Country for Old Men", "There Will Be Blood"],
    },
    "atlas_orion": {
        "name": "Atlas Lens Co. Orion Anamorphic",
        "manufacturer": "Atlas Lens Co.",
        "character": "Modern indie anamorphic. Full-frame coverage with 2x squeeze. Beautifully "
        "flawed — amber and blue streaking flares, visible aberrations at the edges, "
        "organic fall-off. More character than Panavision G-Series but more consistent "
        "than vintage C-Series. The democratization of the anamorphic look.",
        "color_rendering": "warm, amber-shifted at wide apertures",
        "contrast": "medium, organic fall-off",
        "bokeh": BokehCharacter.OVAL,
        "flare_character": "amber and blue streaks, characterful, organic",
        "prompt_keywords": [
            "Atlas anamorphic character",
            "amber lens flares",
            "indie anamorphic",
            "organic aberrations",
            "full-frame anamorphic",
        ],
        "notable_films": ["indie productions", "music videos", "commercial work"],
    },
    "arri_signature_prime": {
        "name": "ARRI Signature Prime",
        "manufacturer": "ARRI",
        "character": "Designed specifically for the ARRI large format system. Extraordinarily smooth "
        "rendering — subjects separate from backgrounds with a three-dimensional quality "
        "that's gentle rather than clinical. 'Organic modern' — sharp enough for 4K+ but "
        "with a warmth that prevents the image from feeling sterile.",
        "color_rendering": "warm neutral, organic, skin-friendly",
        "contrast": "medium-high, smooth micro-contrast",
        "bokeh": BokehCharacter.SMOOTH,
        "flare_character": "gentle, controlled, warm-toned",
        "prompt_keywords": [
            "ARRI Signature Prime rendering",
            "organic large-format look",
            "smooth three-dimensional separation",
            "skin-friendly rendering",
        ],
        "notable_films": ["1917", "Dune", "The Batman (some scenes)"],
    },
    "canon_k35": {
        "name": "Canon K35",
        "manufacturer": "Canon",
        "character": "Legendary vintage primes from the 1970s. Soft wide open with extraordinary "
        "flare character — veiling, ghosts, rainbow artifacts. At T1.3, the image has an "
        "ethereal, haloed quality. Beloved by modern DPs seeking organic imperfection. "
        "Barry Lyndon, Alien (some scenes), and countless modern productions seeking that "
        "1970s warmth.",
        "color_rendering": "warm, golden, flattering",
        "contrast": "low wide open, increases stopped down",
        "bokeh": BokehCharacter.SMOOTH,
        "flare_character": "extreme — veiling flare, ghosts, rainbow artifacts, beautiful imperfection",
        "prompt_keywords": [
            "vintage Canon K35",
            "1970s lens warmth",
            "halation and flare",
            "soft ethereal wide open",
            "golden era cinematography",
        ],
        "notable_films": ["Barry Lyndon", "Alien (select scenes)", "The Florida Project"],
    },
    "petzval": {
        "name": "Petzval (Lomography/vintage)",
        "manufacturer": "various",
        "character": "The oldest photographic lens design (1840). Produces a sharp center with "
        "dramatic swirling bokeh at the edges. The out-of-focus areas literally rotate. "
        "An artistic choice that screams 'handcrafted' and 'deliberately imperfect'.",
        "color_rendering": "varies, typically warm with vintage glass",
        "contrast": "low at edges, moderate center",
        "bokeh": BokehCharacter.SWIRL,
        "flare_character": "unpredictable, vintage",
        "prompt_keywords": [
            "Petzval swirl bokeh",
            "swirling out-of-focus",
            "vintage lens art",
            "sharp center soft edges",
            "19th century optics",
        ],
        "notable_films": ["art films", "music videos", "experimental"],
    },
}


# ---------------------------------------------------------------------------
# Aberrations as Aesthetic — imperfection as signature
# ---------------------------------------------------------------------------

ABERRATIONS: dict[str, dict] = {
    "chromatic_aberration": {
        "description": "Color fringing at high-contrast edges — magenta/green or red/cyan separation. "
        "More prominent at wider apertures and wider focal lengths.",
        "aesthetic_use": "Vintage character, lo-fi, dreamlike edges, psychedelia",
        "prompt_keywords": ["chromatic aberration", "color fringing", "RGB separation at edges"],
    },
    "spherical_aberration": {
        "description": "Soft glow around highlights caused by rays at different distances from the "
        "optical axis focusing at different points. The 'glow' of fast vintage lenses wide open.",
        "aesthetic_use": "Ethereal beauty, dreamlike softness, romantic highlight glow",
        "prompt_keywords": ["soft focus glow", "spherical aberration bloom", "highlight halo", "dreamy softness"],
    },
    "barrel_distortion": {
        "description": "Straight lines bow outward from center. Most prominent on wide-angle lenses. "
        "Creates a sense of spatial warping.",
        "aesthetic_use": "Environmental distortion, unease, overwhelming interiors",
        "prompt_keywords": ["barrel distortion", "wide-angle warping", "bent straight lines"],
    },
    "coma": {
        "description": "Point light sources at frame edges render as comet-like smears rather than "
        "clean points. Creates 'seagull' shapes in night city lights.",
        "aesthetic_use": "Night city character, star field distortion, vintage night scenes",
        "prompt_keywords": ["coma aberration", "smeared point lights", "comet-shaped highlights"],
    },
    "vignetting": {
        "description": "Darkening at frame edges — mechanical (lens barrel) or optical. "
        "Draws the eye to frame center.",
        "aesthetic_use": "Natural focus direction, vintage character, intimacy, tunnel vision",
        "prompt_keywords": ["natural vignette", "edge darkening", "tunnel vision", "vintage vignetting"],
    },
    "focus_breathing": {
        "description": "Focal length subtly shifts during focus pulls — the frame 'breathes' in "
        "and out. Unique to cinema lenses (photo lenses minimize this).",
        "aesthetic_use": "Anamorphic character, organic feel, 'living' image",
        "prompt_keywords": ["focus breathing", "anamorphic breathing", "organic focus shift"],
    },
    "anamorphic_flare": {
        "description": "Horizontal light streaks caused by the anamorphic element. Blue is classic "
        "but amber, red, and rainbow variations exist depending on lens coating.",
        "aesthetic_use": "Sci-fi, noir, cinematic scope, street lights in rain",
        "prompt_keywords": [
            "anamorphic lens flare",
            "horizontal blue streak",
            "sci-fi flare",
            "streetlight anamorphic flares",
        ],
    },
    "halation": {
        "description": "Light bouncing off the film base back through the emulsion, creating a "
        "red/orange glow around bright highlights. Unique to film (especially CineStill 800T). "
        "Digital simulations exist but lack the organic randomness.",
        "aesthetic_use": "Film nostalgia, neon-lit scenes, streetlight halos, CineStill aesthetic",
        "prompt_keywords": [
            "halation glow",
            "CineStill halation",
            "red highlight glow",
            "film base light bounce",
            "neon halation",
        ],
    },
}

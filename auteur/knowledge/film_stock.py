"""Film stock & digital sensor profiles — the texture and soul of the image.

Before digital, the choice of film stock was one of the most consequential
decisions a DP made. Each emulsion had personality — grain structure, color
response, latitude, halation character. Digital sensors have their own
personalities too, though the industry pretends they're neutral.
"""

from auteur.knowledge.ontology import GrainStructure, SensorFormat

# ---------------------------------------------------------------------------
# Analog Film Stocks — the chemistry of image
# ---------------------------------------------------------------------------

FILM_STOCKS: dict[str, dict] = {
    "kodak_vision3_500t": {
        "name": "Kodak Vision3 500T (5219)",
        "manufacturer": "Kodak",
        "iso": 500,
        "balance": "tungsten (3200K)",
        "grain": GrainStructure.MEDIUM,
        "character": "The modern cinema workhorse. Extraordinary latitude (14+ stops claimed) means "
        "you can underexpose three stops and still pull detail from shadows. Color rendering "
        "is warm and rich — skin tones glow, shadows retain color rather than going muddy "
        "neutral. The grain at 500 ISO is visible but organic, adding texture without "
        "distraction. This is the stock of prestige cinema — The Hateful Eight, Dunkirk, "
        "Licorice Pizza.",
        "color_science": "warm, rich, extraordinary shadow color retention",
        "latitude_stops": 14,
        "prompt_keywords": [
            "Kodak 500T film look",
            "warm cinema film stock",
            "organic film grain",
            "rich warm film tonality",
            "35mm motion picture film",
        ],
        "best_for": ["interior drama", "low-light", "warm skin tones", "prestige narrative"],
    },
    "kodak_vision3_250d": {
        "name": "Kodak Vision3 250D (5207)",
        "manufacturer": "Kodak",
        "iso": 250,
        "balance": "daylight (5600K)",
        "grain": GrainStructure.FINE,
        "character": "The daylight counterpart to 500T. Finer grain, slightly cooler color balance, "
        "extraordinary resolution. Daylight exterior scenes have a clarity and color purity "
        "that digital struggles to match — blues are deep, greens are vibrant, skin in "
        "sunlight has a luminosity that comes from the stock's color response curves.",
        "color_science": "clean, vibrant, pure daylight color",
        "latitude_stops": 13,
        "prompt_keywords": [
            "Kodak 250D film look",
            "daylight film stock",
            "fine grain film",
            "vibrant daylight film colors",
            "clean film tonality",
        ],
        "best_for": ["daylight exterior", "landscape", "period film", "clean film look"],
    },
    "kodak_vision3_200t": {
        "name": "Kodak Vision3 200T (5213)",
        "manufacturer": "Kodak",
        "iso": 200,
        "balance": "tungsten (3200K)",
        "grain": GrainStructure.FINE,
        "character": "The finest-grained tungsten stock. When you want the warmth and character of "
        "film but with minimal visible grain — studio work, beauty shots, period films "
        "where the image needs to be pristine. Almost medium-format-like tonality.",
        "color_science": "warm, fine detail, pristine",
        "latitude_stops": 13,
        "prompt_keywords": [
            "Kodak 200T film look",
            "fine grain tungsten film",
            "pristine warm film",
            "studio film quality",
        ],
        "best_for": ["studio", "beauty", "period drama", "high-detail film work"],
    },
    "fuji_eterna_500": {
        "name": "Fujifilm Eterna 500 (8573)",
        "manufacturer": "Fujifilm",
        "iso": 500,
        "balance": "tungsten (3200K)",
        "grain": GrainStructure.MEDIUM,
        "character": "The Fuji alternative to Kodak 500T — cooler, more precise, less romantic. "
        "Where Kodak warms everything into a golden embrace, Fuji Eterna renders with "
        "clinical accuracy that some DPs prefer for its honesty. Blues are deeper, "
        "skin tones are more neutral, shadows are cooler. Japanese cinema's stock of choice.",
        "color_science": "cool precision, neutral-to-cool skin tones, deep blues",
        "latitude_stops": 13,
        "prompt_keywords": [
            "Fuji Eterna film look",
            "cool film tonality",
            "precise film color",
            "Japanese cinema film stock",
            "neutral cool film",
        ],
        "best_for": ["cool-toned drama", "thriller", "Japanese aesthetic", "clinical narrative"],
    },
    "fuji_eterna_vivid_500": {
        "name": "Fujifilm Eterna Vivid 500 (8547)",
        "manufacturer": "Fujifilm",
        "iso": 500,
        "balance": "daylight (5600K)",
        "grain": GrainStructure.MEDIUM,
        "character": "Fuji's high-saturation option — punchier, more vivid than standard Eterna. "
        "Colors pop without becoming garish. A middle ground between Kodak's warmth and "
        "Eterna's coolness, with added vibrancy.",
        "color_science": "vivid, saturated, punchy but controlled",
        "latitude_stops": 12,
        "prompt_keywords": [
            "Fuji Vivid film look",
            "saturated film stock",
            "punchy vivid film colors",
            "high-saturation cinema film",
        ],
        "best_for": ["commercial", "music video", "vibrant narrative", "fashion film"],
    },
    "cinestill_800t": {
        "name": "CineStill 800T",
        "manufacturer": "CineStill",
        "iso": 800,
        "balance": "tungsten (3200K)",
        "grain": GrainStructure.COARSE,
        "character": "Kodak Vision3 500T with the remjet anti-halation layer removed — creating "
        "the signature red/orange halation glow around bright light sources. Neon signs "
        "bloom with halos, streetlights become sacred objects, any point source of light "
        "radiates. This is the most Instagram-famous film stock — the neon-lit night "
        "aesthetic that defines modern film photography.",
        "color_science": "warm with red halation halos around highlights",
        "latitude_stops": 12,
        "prompt_keywords": [
            "CineStill 800T halation",
            "red halation glow",
            "neon light halation",
            "night photography film grain",
            "streetlight halos",
            "CineStill night aesthetic",
        ],
        "best_for": ["night street", "neon-lit scenes", "urban night", "atmospheric night"],
    },
    "kodak_tri_x_400": {
        "name": "Kodak Tri-X 400",
        "manufacturer": "Kodak",
        "iso": 400,
        "balance": "panchromatic B&W",
        "grain": GrainStructure.COARSE,
        "character": "The most iconic black-and-white film stock in history. Pronounced, characterful "
        "grain with extraordinary tonal range. Shadows are rich and detailed; highlights "
        "roll off beautifully. Every photojournalist, every documentary filmmaker, every "
        "art student has shot Tri-X. It IS black-and-white photography.",
        "color_science": "black and white — rich tones, visible grain, classic",
        "latitude_stops": 11,
        "prompt_keywords": [
            "Tri-X black and white",
            "classic B&W film grain",
            "high-contrast black and white",
            "photojournalistic B&W",
            "gritty monochrome film",
        ],
        "best_for": ["documentary B&W", "photojournalism", "art film", "noir"],
    },
    "ilford_hp5_400": {
        "name": "Ilford HP5 Plus 400",
        "manufacturer": "Ilford",
        "iso": 400,
        "balance": "panchromatic B&W",
        "grain": GrainStructure.MEDIUM,
        "character": "The British alternative to Tri-X. Slightly finer grain, slightly different "
        "tonal curve — some say softer in the midtones, more gradual in highlight rolloff. "
        "Less gritty than Tri-X, more elegant.",
        "color_science": "black and white — smooth midtones, elegant grain",
        "latitude_stops": 11,
        "prompt_keywords": [
            "Ilford HP5 black and white",
            "elegant B&W film",
            "smooth monochrome grain",
            "British B&W film stock",
        ],
        "best_for": ["portrait B&W", "art photography", "elegant monochrome"],
    },
}


# ---------------------------------------------------------------------------
# Digital Sensor Profiles — the silicon of image
# ---------------------------------------------------------------------------

DIGITAL_SENSORS: dict[str, dict] = {
    "arri_alexa_mini_lf": {
        "name": "ARRI Alexa Mini LF",
        "manufacturer": "ARRI",
        "sensor_format": SensorFormat.LARGE_FORMAT,
        "resolution": "4.5K (4448×3096)",
        "native_iso": [800],
        "dynamic_range_stops": 14.5,
        "character": "The current gold standard for narrative cinema. ARRI's color science is "
        "legendary — skin tones are rendered with a warmth and accuracy that no other "
        "manufacturer matches. The image has an organic quality that feels closer to "
        "film than any other digital camera. Highlight rolloff is smooth and gradual "
        "rather than clipping hard. The camera that shot Dune, 1917, The Batman.",
        "color_science": "warm, organic, extraordinary skin tones, film-like highlight rolloff",
        "grain_character": GrainStructure.FINE,
        "prompt_keywords": [
            "ARRI Alexa look",
            "ARRI color science",
            "organic digital cinema",
            "warm filmic digital",
            "natural skin tone rendering",
        ],
        "best_for": ["narrative film", "prestige TV", "commercial", "anything requiring beautiful skin"],
    },
    "arri_alexa_35": {
        "name": "ARRI ALEXA 35",
        "manufacturer": "ARRI",
        "sensor_format": SensorFormat.SUPER_35,
        "resolution": "4.6K (4608×3164)",
        "native_iso": [800, 2560],
        "dynamic_range_stops": 17,
        "character": "ARRI's latest S35 sensor with a claimed 17 stops of dynamic range — the most "
        "of any cinema camera. The dual native ISO means pristine images in extremely low "
        "light. Retains ARRI's signature color science while adding extraordinary latitude. "
        "The sensor that makes DPs question whether they need large format at all.",
        "color_science": "ARRI signature — warm, organic, now with extreme latitude",
        "grain_character": GrainStructure.FINE,
        "prompt_keywords": [
            "ARRI Alexa 35 look",
            "17-stop dynamic range",
            "extreme latitude digital",
            "ARRI dual native ISO",
        ],
        "best_for": ["extreme dynamic range scenes", "low light", "HDR mastering", "narrative"],
    },
    "red_v_raptor": {
        "name": "RED V-RAPTOR 8K VV",
        "manufacturer": "RED",
        "sensor_format": SensorFormat.LARGE_FORMAT,
        "resolution": "8K (8192×4320)",
        "native_iso": [800, 3200],
        "dynamic_range_stops": 16,
        "character": "Resolution monster — 8K large format with RED's proprietary REDCODE RAW "
        "compression. The image is extraordinarily detailed, sometimes too much so — "
        "every pore, every imperfection is visible. RED's color science has improved "
        "dramatically but still leans slightly cooler and more clinical than ARRI. "
        "The camera of choice when you need maximum reframing headroom, VFX work, "
        "or when the director demands 'more resolution.'",
        "color_science": "precise, slightly cool, clinical detail, improving warmth",
        "grain_character": GrainStructure.FINE,
        "prompt_keywords": [
            "RED 8K resolution",
            "hyper-detailed digital",
            "clinical precision",
            "RED color science",
            "extreme resolution",
        ],
        "best_for": ["VFX-heavy", "reframing", "resolution-demanding", "commercial"],
    },
    "sony_venice_2": {
        "name": "Sony VENICE 2",
        "manufacturer": "Sony",
        "sensor_format": SensorFormat.FULL_FRAME,
        "resolution": "8.6K (8640×5760)",
        "native_iso": [800, 3200],
        "dynamic_range_stops": 16,
        "character": "Sony's cinema flagship with dual native ISO that produces remarkably clean "
        "images at 3200 ISO — true low-light capability. Color science is neutral-to-cool, "
        "less character than ARRI but more accurate. The internal 16-bit X-OCN codec is "
        "extraordinary. DPs who want accuracy over personality choose Venice.",
        "color_science": "neutral, accurate, clean low-light, subtle S-Gamut3",
        "grain_character": GrainStructure.FINE,
        "prompt_keywords": [
            "Sony Venice look",
            "clean low-light digital",
            "neutral color rendering",
            "high ISO clarity",
            "dual native ISO clean",
        ],
        "best_for": ["low-light", "run-and-gun narrative", "accuracy-demanding", "concert/live"],
    },
    "blackmagic_ursa_mini_pro_12k": {
        "name": "Blackmagic URSA Mini Pro 12K",
        "manufacturer": "Blackmagic Design",
        "sensor_format": SensorFormat.SUPER_35,
        "resolution": "12K (12288×6480)",
        "native_iso": [800],
        "dynamic_range_stops": 14,
        "character": "Resolution insanity at an accessible price. 12K in S35 format means each "
        "photosite is tiny, which creates noise at higher ISOs, but downsampled to 4K "
        "the detail and noise performance are excellent. Blackmagic's color science in "
        "BRAW is surprisingly good — warm, slightly saturated, crowd-pleasing.",
        "color_science": "warm, slightly saturated, pleasing Blackmagic color",
        "grain_character": GrainStructure.FINE,
        "prompt_keywords": [
            "Blackmagic cinema camera look",
            "high resolution digital",
            "accessible cinema quality",
            "BRAW color science",
        ],
        "best_for": ["indie film", "high-resolution needs on budget", "VFX plates"],
    },
    "canon_c500_mark_ii": {
        "name": "Canon EOS C500 Mark II",
        "manufacturer": "Canon",
        "sensor_format": SensorFormat.FULL_FRAME,
        "resolution": "5.9K (5952×3140)",
        "native_iso": [800, 3200],
        "dynamic_range_stops": 15,
        "character": "Canon's full-frame cinema camera. Canon's color science is distinctive — "
        "warm, with a specific rendering of reds and skin tones that many DPs love. "
        "Less clinical than Sony, less organic than ARRI, but with a personality that's "
        "immediately recognizable. Canon Log 3 provides excellent latitude.",
        "color_science": "warm Canon color, distinctive red rendering, flattering skin",
        "grain_character": GrainStructure.FINE,
        "prompt_keywords": [
            "Canon cinema color",
            "warm Canon color science",
            "Canon skin tone rendering",
            "Canon full-frame cinema",
        ],
        "best_for": ["documentary", "corporate", "wedding cinema", "warm narrative"],
    },
}

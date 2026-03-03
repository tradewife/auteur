"""Emmanuel 'Chivo' Lubezki AMC ASC — the poet of natural light and long takes."""

from auteur.knowledge.styles.base import StyleProfile

LUBEZKI = StyleProfile(
    name="Emmanuel Lubezki AMC ASC",
    philosophy="Cinema should feel like life — unbroken, flowing, present-tense. Lubezki "
    "pursues an almost spiritual relationship with natural light, treating the sun "
    "and sky as his primary lighting instruments. His long, unbroken Steadicam and "
    "handheld takes immerse the viewer inside the experience rather than observing "
    "it from outside. He chases 'magic hour' obsessively and uses wide-angle lenses "
    "close to subjects to create visceral, subjective intimacy.",
    preferred_lenses=[
        "ARRI/Zeiss Master Primes", "12mm", "14mm", "18mm", "21mm",
        "Zeiss Super Speeds (earlier work)", "extremely wide-angle close to subject",
    ],
    preferred_camera=["ARRI Alexa 65", "ARRI Alexa Mini", "ARRI Alexa XT"],
    preferred_film_stock=["ARRI Alexa digital (natural light optimized)", "Kodak Vision3 (earlier work)"],
    lighting_approach="Natural light fundamentalist. Lubezki prefers to work with available "
    "light — golden hour, overcast skies, firelight, candlelight. When "
    "artificial light is needed, it is hidden and motivated to feel natural. "
    "He often schedules entire shooting days around the 20-minute magic hour "
    "window. Interior scenes use large windows as primary sources with "
    "minimal supplementation.",
    typical_ratios="Natural ratios — whatever the sun gives. Often 2:1 to 4:1",
    color_temperature_preference="Follows the natural world. Warm golden hour, cool blue hour, "
    "mixed firelight with cool ambient. Never artificially gelled.",
    use_of_practicals="Minimal — Lubezki prefers the actual light of candles, fires, and "
    "ambient sources. Practicals are used at their actual output levels.",
    color_palette="Earth tones, greens, warm ambers, cool blues. Deeply connected to "
    "the natural environment. The Revenant lives in desaturated cool tones "
    "of winter. Tree of Life breathes in warm golden memory. Gravity shifts "
    "from cold void to warm earthlight.",
    saturation_tendency="Naturalistic to slightly desaturated — never pushed or artificial",
    grading_style="Minimal — preserve the quality of the natural light captured on set. "
    "Lubezki's images look graded because they were lit perfectly, "
    "not because of post-production manipulation.",
    composition_style="Wide-angle, immersive, often subjective. Lubezki uses ultra-wide lenses "
    "very close to subjects, distorting perspective slightly to create "
    "intimacy and presence. His frames breathe — subjects move through space "
    "freely, and the camera follows rather than dictates.",
    preferred_aspect_ratio="2.39:1 for epics, 1.85:1 for intimate work. Shot The Revenant "
    "and Birdman in 1.85:1 for intimacy despite their epic scope.",
    use_of_depth="Wide-angle deep focus — everything in the environment is present "
    "and readable. Lubezki rarely isolates with shallow depth of field; "
    "instead, the wide lens keeps the world connected to the subject.",
    movement_philosophy="The camera is a living, breathing participant. Lubezki's Steadicam "
    "and handheld work is restless, intimate, and continuous. His famous "
    "long takes in Birdman, Children of Men, and Gravity immerse the "
    "viewer in unbroken time. Movement is subjective — the camera is "
    "a consciousness moving through the world.",
    preferred_movement=[
        "extended Steadicam takes", "immersive handheld", "unbroken long takes",
        "following subjects through space", "360-degree choreographed movement",
    ],
    signature_techniques=[
        "Obsessive use of natural/available light",
        "Magic hour and golden hour shooting",
        "Extended unbroken Steadicam takes",
        "Ultra-wide lenses close to subject",
        "Subjective, immersive camera movement",
        "Handheld intimacy in chaotic environments",
        "Firelight and candlelight as sole source",
        "Deep focus wide-angle compositions",
        "Seamless hidden cuts in long takes",
    ],
    notable_films=[
        "The Revenant", "Birdman", "Gravity", "Children of Men",
        "Tree of Life", "The New World", "Y Tu Mamá También", "Roma (advisor)",
    ],
    prompt_keywords=[
        "Lubezki natural light", "golden hour cinematography", "magic hour backlight",
        "long take Steadicam", "immersive wide-angle", "subjective camera movement",
        "candlelight scene", "available light only", "deep focus wide lens",
        "unbroken continuous shot",
    ],
    negative_keywords=[
        "artificial studio lighting", "static locked camera", "telephoto compression",
        "neon colored light", "heavy post-processing", "shallow depth of field bokeh",
    ],
)

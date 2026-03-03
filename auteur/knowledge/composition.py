"""Composition — the architecture of the frame.

Composition is the grammar of visual storytelling. Where elements are placed
within the frame, how they relate to each other and to the edges, the depth
planes they occupy — all of this communicates meaning before a single word
of dialogue.
"""

# ---------------------------------------------------------------------------
# Composition Rules — systems of visual order
# ---------------------------------------------------------------------------

COMPOSITION_RULES: dict[str, dict] = {
    "rule_of_thirds": {
        "description": "Divide the frame into a 3×3 grid. Place key elements at intersections or "
        "along lines. The most widely taught and used composition system — it creates "
        "dynamic balance by avoiding center placement. Eyes at upper-third line. Horizons "
        "at lower or upper third.",
        "visual_effect": "dynamic balance, natural eye movement, professional framing",
        "prompt_keywords": [
            "rule of thirds composition",
            "off-center subject placement",
            "dynamic balanced framing",
        ],
    },
    "golden_ratio": {
        "description": "The Fibonacci spiral (1:1.618) applied to frame composition. More organic "
        "than the rule of thirds — the spiral creates a natural path for the eye to follow "
        "from the outside toward the subject at the spiral's focal point. Renaissance "
        "paintings, nautilus shells, and master cinematographers all converge here.",
        "visual_effect": "organic flow, subconscious satisfaction, artistic elegance",
        "prompt_keywords": [
            "golden ratio composition",
            "Fibonacci spiral framing",
            "golden spiral layout",
        ],
    },
    "center_frame": {
        "description": "Subject dead center. Breaks the 'rules' deliberately — and communicates "
        "power, symmetry, confrontation, or obsessive control. Stanley Kubrick and Wes "
        "Anderson are the masters of center framing. When a character stares directly at "
        "camera from frame center, the effect is hypnotic and slightly threatening.",
        "visual_effect": "power, symmetry, confrontation, obsessive order, hypnotic",
        "prompt_keywords": [
            "center-framed composition",
            "symmetrical center frame",
            "Kubrick symmetry",
            "Wes Anderson centered",
        ],
    },
    "dynamic_symmetry": {
        "description": "Using diagonal lines derived from the frame's proportions to create dynamic "
        "compositions. More complex than thirds or golden ratio — involves baroque diagonals, "
        "reciprocals, and armature lines. Creates compositions that feel 'right' without "
        "the viewer understanding why. Used extensively in classical painting.",
        "visual_effect": "unconscious satisfaction, dynamic tension, painterly quality",
        "prompt_keywords": [
            "dynamic symmetry composition",
            "diagonal composition lines",
            "baroque diagonal framing",
        ],
    },
    "frame_within_frame": {
        "description": "Using elements within the scene to create a secondary frame around the "
        "subject — doorways, windows, arches, mirrors, tree branches. This isolates the "
        "subject, creates depth, and adds a layer of visual meaning. A character framed "
        "within a prison window tells you they're trapped without a word.",
        "visual_effect": "isolation, depth, containment, voyeurism, focused attention",
        "prompt_keywords": [
            "frame within frame",
            "doorway framing",
            "natural frame composition",
            "window framing subject",
            "architectural framing",
        ],
    },
    "leading_lines": {
        "description": "Using lines within the scene — roads, hallways, fences, rivers, shadows — "
        "to direct the viewer's eye toward the subject or vanishing point. The most powerful "
        "compositional tool for guiding attention. A road disappearing into the horizon "
        "pulls the viewer's consciousness along with it.",
        "visual_effect": "directed attention, depth, journey, convergence",
        "prompt_keywords": [
            "leading lines composition",
            "converging lines",
            "road to vanishing point",
            "perspective lines guiding eye",
        ],
    },
    "negative_space": {
        "description": "Deliberately leaving large areas of the frame empty — sky, wall, void. "
        "The emptiness speaks. Negative space around a subject creates isolation, "
        "vulnerability, or contemplation. A figure small in a vast landscape communicates "
        "insignificance. An empty chair communicates absence.",
        "visual_effect": "isolation, breathing room, contemplation, minimalism, loneliness",
        "prompt_keywords": [
            "negative space composition",
            "minimalist framing",
            "empty space around subject",
            "vast negative space",
            "isolated subject in frame",
        ],
    },
    "dutch_angle": {
        "description": "Tilting the camera so the horizon is no longer level. Immediately "
        "communicates that something is wrong — disorientation, instability, madness, "
        "or supernatural influence. Overused in horror and comic book films, devastating "
        "when used sparingly. The Third Man uses Dutch angles as a visual metaphor for "
        "post-war Vienna's moral collapse.",
        "visual_effect": "unease, instability, disorientation, madness, world-off-kilter",
        "prompt_keywords": [
            "Dutch angle",
            "tilted horizon",
            "canted frame",
            "disorienting angle",
            "off-kilter composition",
        ],
    },
    "triangular": {
        "description": "Arranging subjects or elements in a triangular shape within the frame. "
        "Creates stability (base-down triangle) or instability (apex-down). The most "
        "stable composition in visual art — used in religious paintings to convey divine "
        "order and in group portraits to create visual hierarchy.",
        "visual_effect": "stability, hierarchy, classical order, visual weight",
        "prompt_keywords": [
            "triangular composition",
            "three-point arrangement",
            "pyramid composition",
        ],
    },
    "foreground_interest": {
        "description": "Placing something compelling in the extreme foreground — often partially "
        "out of focus. Creates a layered, three-dimensional composition that pulls the "
        "viewer through depth planes. An out-of-focus shoulder in the foreground, the "
        "subject sharp in the midground, a blurred background — three layers of reality.",
        "visual_effect": "depth, dimensionality, voyeurism, visual layering",
        "prompt_keywords": [
            "foreground element",
            "depth layered composition",
            "foreground bokeh framing",
            "three-plane depth",
            "over-the-shoulder depth",
        ],
    },
}


# ---------------------------------------------------------------------------
# Aspect Ratio as Storytelling — the shape of the story
# ---------------------------------------------------------------------------

ASPECT_RATIOS: dict[str, dict] = {
    "1.33:1": {
        "name": "Academy / 4:3",
        "description": "The original cinema and TV ratio. Tall, contained, intimate. When used today, "
        "it's a deliberate choice that says 'this is personal' or 'this is nostalgic.' "
        "The Lighthouse, First Reformed, Ida — all used 4:3 to create claustrophobic "
        "intimacy or period authenticity.",
        "feeling": "intimate, nostalgic, contained, claustrophobic, personal",
        "prompt_keywords": ["4:3 aspect ratio", "Academy ratio", "intimate framing", "contained frame"],
        "api_value": "4:3",
    },
    "1.85:1": {
        "name": "Flat Widescreen",
        "description": "The standard American widescreen. Slightly wider than 16:9 — balanced, "
        "versatile, the 'default' for non-epic storytelling. Wide enough for environmental "
        "context, tall enough for portrait work. Most dramas, comedies, and thrillers.",
        "feeling": "balanced, versatile, standard cinematic",
        "prompt_keywords": ["1.85 widescreen", "flat widescreen", "standard cinematic frame"],
        "api_value": "16:9",
    },
    "2.39:1": {
        "name": "Anamorphic Scope",
        "description": "The wide frame of epic cinema. Horizontal dominance — landscapes stretch, "
        "intimate close-ups gain power from the empty space flanking the face, two-shots "
        "can breathe. The ratio itself says 'this is important, this is cinema.' "
        "Lawrence of Arabia, Blade Runner, Dune.",
        "feeling": "epic, cinematic, grand, important, sweeping",
        "prompt_keywords": [
            "anamorphic widescreen",
            "2.39:1 scope",
            "cinemascope wide",
            "epic widescreen framing",
        ],
        "api_value": "16:9",
    },
    "16:9": {
        "name": "HD / Broadcast",
        "description": "The universal digital standard. Every screen you own is 16:9. It's become "
        "so ubiquitous that it barely registers as a 'choice' — it's the absence of choice. "
        "Useful for content that needs to fill screens without letterboxing.",
        "feeling": "modern, universal, digital, broadcast",
        "prompt_keywords": ["16:9 widescreen", "HD aspect ratio", "standard widescreen"],
        "api_value": "16:9",
    },
    "9:16": {
        "name": "Vertical / Portrait",
        "description": "The mobile-first ratio. Vertical video used to be a sin; now it's a "
        "deliberate storytelling choice for TikTok, Instagram Reels, and Stories. "
        "Creates towering height, intimate phone-camera feel, or deliberate constraint.",
        "feeling": "mobile, intimate, modern, social-first",
        "prompt_keywords": ["vertical video", "9:16 portrait", "mobile-first framing", "TikTok format"],
        "api_value": "9:16",
    },
    "1:1": {
        "name": "Square",
        "description": "Equal on all sides — contained, balanced, with no directional bias. "
        "The Instagram original. In cinema, used for artistic constraint or to create "
        "a sense of entrapment. Every direction feels equally closed.",
        "feeling": "contained, balanced, artistic, social media, constrained",
        "prompt_keywords": ["square format", "1:1 ratio", "Instagram square", "equal proportions"],
        "api_value": "1:1",
    },
}

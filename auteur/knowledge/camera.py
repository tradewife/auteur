"""Camera systems — sensors, frame rates, resolution, and their visual signatures.

This isn't a spec sheet. Every entry encodes the *why* — how each technical
parameter shapes the viewer's psychological experience.
"""

from auteur.knowledge.ontology import SensorFormat

# ---------------------------------------------------------------------------
# Sensor Formats — the single most consequential choice in cinematography
# ---------------------------------------------------------------------------

SENSOR_FORMATS: dict[str, dict] = {
    "super_16": {
        "enum": SensorFormat.SUPER_16,
        "dimensions_mm": (12.52, 7.41),
        "crop_factor": 2.88,
        "character": "Inherently grainy, intimate, documentary. The restricted sensor area demands "
        "wider lenses to achieve equivalent framing, which deepens perspective and increases "
        "depth of field. This creates a 'you are there' immediacy that larger formats cannot "
        "replicate. Think Darren Aronofsky's early work, 28 Days Later, Moonrise Kingdom.",
        "dof_character": "deep",
        "prompt_keywords": [
            "16mm film texture",
            "documentary grain",
            "intimate handheld",
            "deep depth of field",
            "indie film aesthetic",
        ],
        "best_for": ["documentary", "horror", "indie drama", "period nostalgia"],
    },
    "super_35": {
        "enum": SensorFormat.SUPER_35,
        "dimensions_mm": (24.89, 18.66),
        "crop_factor": 1.45,
        "character": "The cinema standard for 80+ years. Balanced depth of field — selective focus "
        "without the paper-thin plane of larger formats. The 'Goldilocks' sensor that most "
        "viewers unconsciously associate with 'this looks like a movie'. ARRI Alexa Mini, "
        "RED DSMC2 in S35 mode, classic 35mm film.",
        "dof_character": "balanced",
        "prompt_keywords": [
            "35mm film look",
            "cinematic depth of field",
            "classic cinema",
            "balanced bokeh",
            "motion picture film",
        ],
        "best_for": ["narrative film", "commercial", "music video", "general cinematography"],
    },
    "full_frame": {
        "enum": SensorFormat.FULL_FRAME,
        "dimensions_mm": (36.0, 24.0),
        "crop_factor": 1.0,
        "character": "The still photography sensor that crossed into cinema with the DSLR revolution. "
        "Shallower depth of field than S35 at equivalent framing — subjects separate from "
        "backgrounds more readily. Sony Venice, Canon C500 II, RED V-Raptor in FF mode. "
        "Slightly more 'photographic' than 'cinematic' in character — the bokeh is smoother "
        "and the background falls away faster.",
        "dof_character": "shallow",
        "prompt_keywords": [
            "full frame sensor",
            "shallow depth of field",
            "photographic quality",
            "creamy bokeh",
            "subject isolation",
        ],
        "best_for": ["portrait work", "fashion film", "low-light", "shallow DoF storytelling"],
    },
    "large_format": {
        "enum": SensorFormat.LARGE_FORMAT,
        "dimensions_mm": (54.12, 25.59),
        "crop_factor": 0.67,
        "character": "ARRI Alexa 65, RED Monstro 8K VV. The format of modern epics. Depth of field "
        "becomes razor-thin at wide apertures — a 40mm lens at T2 on large format has the "
        "depth-of-field equivalent of roughly a 27mm at T1.3 on S35. This creates an almost "
        "three-dimensional quality where the subject exists in a precise plane of reality "
        "while the world dissolves around them. The Revenant, Dune, No Time to Die.",
        "dof_character": "very_shallow",
        "prompt_keywords": [
            "large format cinematography",
            "ultra-shallow depth of field",
            "three-dimensional depth",
            "epic scale with intimate focus",
            "ARRI Alexa 65 look",
        ],
        "best_for": ["epic drama", "prestige film", "landscape with intimate foreground"],
    },
    "imax": {
        "enum": SensorFormat.IMAX,
        "dimensions_mm": (70.41, 52.63),
        "crop_factor": 0.51,
        "character": "The overwhelming format. IMAX 15/70 film or ARRI Alexa IMAX digital. The frame "
        "is so large that projected properly, it exceeds the viewer's peripheral vision. "
        "Resolution and detail are staggering — you can see individual eyelashes at 50 feet. "
        "Christopher Nolan's signature. The increased vertical real estate (1.43:1 native) "
        "creates a sense of immersion no other format matches.",
        "dof_character": "extremely_shallow",
        "prompt_keywords": [
            "IMAX resolution",
            "overwhelming detail",
            "immersive scale",
            "hyper-detailed",
            "65mm film clarity",
        ],
        "best_for": ["spectacle", "action", "space", "overwhelming scale"],
    },
    "medium_format": {
        "enum": SensorFormat.MEDIUM_FORMAT,
        "dimensions_mm": (43.8, 32.9),
        "crop_factor": 0.79,
        "character": "Hasselblad, Phase One, Fuji GFX territory. Not traditionally cinematic — this "
        "is the format of fashion photography and fine art. When used in motion, it creates "
        "an uncanny 'large negative' quality with extraordinary tonal gradation and "
        "color depth. The shallow depth of field has a unique quality distinct from full frame.",
        "dof_character": "very_shallow",
        "prompt_keywords": [
            "medium format photography",
            "extraordinary tonal range",
            "fashion photography depth",
            "Hasselblad quality",
            "fine art tonality",
        ],
        "best_for": ["fashion", "beauty", "fine art", "portrait"],
    },
}


# ---------------------------------------------------------------------------
# Frame Rates — temporal perception engineering
# ---------------------------------------------------------------------------

FRAME_RATES: dict[str, dict] = {
    "18fps": {
        "fps": 18,
        "character": "Undercranked — creates visible stutter and dreamlike acceleration. "
        "Silent film era standard. Used intentionally for surreal or period effect.",
        "psychological_effect": "uncanny, antiquated, dream logic",
        "prompt_keywords": ["undercranked", "silent film speed", "jerky motion", "dreamlike acceleration"],
        "motion_blur": "reduced",
    },
    "24fps": {
        "fps": 24,
        "character": "The heartbeat of cinema. 24fps has a specific motion cadence — a slight "
        "stutter on fast movement, a gentle blur on pans — that the human brain has been "
        "conditioned to read as 'story'. This is not technical reality; it is emotional "
        "reality. The motion blur at 180° shutter is the texture of dreams told in the dark.",
        "psychological_effect": "cinematic, dreamlike, narrative, emotionally engaged",
        "prompt_keywords": [
            "cinematic 24fps",
            "film motion cadence",
            "natural motion blur",
            "cinematic motion",
        ],
        "motion_blur": "natural_cinematic",
    },
    "25fps": {
        "fps": 25,
        "character": "PAL standard. Virtually indistinguishable from 24fps in feel. "
        "European broadcast. Slightly smoother than 24fps but retains cinematic character.",
        "psychological_effect": "cinematic, broadcast",
        "prompt_keywords": ["PAL standard", "European broadcast", "cinematic motion"],
        "motion_blur": "natural_cinematic",
    },
    "30fps": {
        "fps": 30,
        "character": "NTSC standard. Subtly smoother than 24fps — begins to shift from 'cinema' "
        "to 'video'. Many viewers cannot articulate the difference but feel it. Used in "
        "broadcast, corporate, and some streaming content.",
        "psychological_effect": "broadcast, slightly prosaic, informational",
        "prompt_keywords": ["broadcast standard", "smooth video", "NTSC"],
        "motion_blur": "moderate",
    },
    "48fps": {
        "fps": 48,
        "character": "Peter Jackson's Hobbit experiment. Hyper-real — motion is too smooth for "
        "most viewers' conditioned expectations. It creates a 'live theater' or 'soap opera' "
        "feeling because the brain interprets extreme temporal clarity as 'present tense' "
        "rather than 'story'. Can work for specific VR or immersive applications.",
        "psychological_effect": "hyperreal, present-tense, uncanny clarity, soap opera effect",
        "prompt_keywords": ["HFR", "hyper-real motion", "extreme clarity", "soap opera effect"],
        "motion_blur": "minimal",
    },
    "60fps": {
        "fps": 60,
        "character": "Sports, gaming, some Ang Lee experiments (Billy Lynn's Long Halftime Walk). "
        "Maximum temporal clarity for real-time viewing. Every detail of motion is preserved. "
        "Psychologically creates a 'window into reality' rather than 'story on screen'.",
        "psychological_effect": "live, present, documentary truth, gaming clarity",
        "prompt_keywords": ["60fps smooth", "sports clarity", "real-time motion", "gaming framerate"],
        "motion_blur": "very_minimal",
    },
    "120fps": {
        "fps": 120,
        "character": "Gemini Man (Ang Lee). At this framerate, the image transcends cinema entirely — "
        "it becomes a window. Motion is perfectly resolved. The effect is physiologically "
        "different from cinema; the brain processes it as direct experience rather than "
        "mediated narrative. Primarily used for VR, slow-motion source, or experimental work.",
        "psychological_effect": "transcendent clarity, direct experience, post-cinematic",
        "prompt_keywords": ["ultra-high framerate", "perfect motion clarity", "VR quality"],
        "motion_blur": "none",
    },
    "overcranked_slow_mo": {
        "fps": 240,
        "character": "Slow-motion source captured at 240-1000fps, played back at 24fps. Time "
        "dilates — a 1-second event becomes 10 seconds of screen time. Used for impact "
        "moments, beauty, violence aestheticized, emotional climax. The extreme temporal "
        "resolution reveals details invisible to the naked eye.",
        "psychological_effect": "time dilation, heightened awareness, emotional peak, beauty in violence",
        "prompt_keywords": [
            "extreme slow motion",
            "time dilation",
            "bullet time",
            "high-speed capture",
            "ramped slow motion",
        ],
        "motion_blur": "none_frozen",
    },
}


# ---------------------------------------------------------------------------
# Resolution Tiers — detail as narrative tool
# ---------------------------------------------------------------------------

RESOLUTION_TIERS: dict[str, dict] = {
    "720p": {
        "pixels": (1280, 720),
        "character": "Web/draft quality. Soft, forgiving of imperfections. "
        "Can emulate the softness of older video formats.",
        "prompt_keywords": ["standard definition feel", "soft detail"],
    },
    "1080p": {
        "pixels": (1920, 1080),
        "character": "HD standard. The current 'broadcast floor'. Enough detail for "
        "storytelling without overwhelming the viewer with information.",
        "prompt_keywords": ["HD quality", "broadcast standard", "clean detail"],
    },
    "2K": {
        "pixels": (2048, 1080),
        "character": "DCI 2K — the digital cinema projection standard. Marginally wider than "
        "1080p. This is what most theatrical releases are mastered at.",
        "prompt_keywords": ["2K cinema", "DCI standard", "theatrical quality"],
    },
    "4K_UHD": {
        "pixels": (3840, 2160),
        "character": "Consumer 4K. Four times the pixels of HD. Detail begins to reveal "
        "imperfections in makeup, sets, and VFX. Demands higher production values.",
        "prompt_keywords": ["4K ultra-high definition", "razor-sharp detail", "UHD clarity"],
    },
    "4K_DCI": {
        "pixels": (4096, 2160),
        "character": "DCI 4K — true cinema 4K. The emerging theatrical standard. "
        "Extraordinary detail that rewards large-screen presentation.",
        "prompt_keywords": ["DCI 4K cinema", "theatrical 4K", "extreme detail"],
    },
    "6K": {
        "pixels": (6144, 3160),
        "character": "RED Dragon/Komodo territory. Excessive for delivery — used for "
        "reframing headroom, stabilization, and future-proofing. The detail level "
        "approaches medium format photography.",
        "prompt_keywords": ["6K oversampled", "extreme resolution headroom", "RED camera detail"],
    },
    "8K": {
        "pixels": (8192, 4320),
        "character": "RED Monstro, Sony Venice 2. Beyond human visual acuity at normal "
        "viewing distances. Used for VFX plates, extreme reframing, and future-proofing. "
        "The level of detail is almost forensic.",
        "prompt_keywords": ["8K resolution", "forensic detail", "beyond human acuity"],
    },
}


# ---------------------------------------------------------------------------
# Shutter Angle — motion blur as aesthetic choice
# ---------------------------------------------------------------------------

SHUTTER_ANGLES: dict[str, dict] = {
    "45_degrees": {
        "angle": 45,
        "equivalent_speed": "1/192 at 24fps",
        "character": "Extremely staccato. Each frame is a frozen slice — movement becomes a "
        "series of sharp positions. Saving Private Ryan's Omaha Beach sequence.",
        "prompt_keywords": ["staccato motion", "frozen frames", "sharp movement", "war photography feel"],
    },
    "90_degrees": {
        "angle": 90,
        "equivalent_speed": "1/96 at 24fps",
        "character": "Crisp with minimal blur. Action is clean and readable. Good for fight "
        "choreography or when motion clarity serves the story.",
        "prompt_keywords": ["crisp motion", "clean action", "minimal motion blur"],
    },
    "180_degrees": {
        "angle": 180,
        "equivalent_speed": "1/48 at 24fps",
        "character": "The standard. 180° shutter at 24fps = 1/48th second exposure. This creates "
        "the motion blur cadence that defines the 'cinema look'. Natural, neither too crisp "
        "nor too blurry. The default for a reason.",
        "prompt_keywords": ["standard cinema motion blur", "natural movement", "180-degree shutter"],
    },
    "270_degrees": {
        "angle": 270,
        "equivalent_speed": "1/32 at 24fps",
        "character": "Extended blur. Movement becomes more fluid, slightly dreamlike. Used for "
        "romantic or surreal sequences. Wong Kar-wai territory.",
        "prompt_keywords": ["extended motion blur", "dreamy movement", "fluid motion", "romantic blur"],
    },
    "360_degrees": {
        "angle": 360,
        "equivalent_speed": "1/24 at 24fps",
        "character": "Maximum blur for the framerate. Every frame exposes for the full frame "
        "duration. Extremely fluid, almost smeared movement. Nightclub scenes, drug sequences, "
        "disorientation.",
        "prompt_keywords": ["maximum motion blur", "smeared movement", "hallucinatory motion"],
    },
}

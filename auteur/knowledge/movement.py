"""Camera movement — the kinetic poetry of cinematography.

How the camera moves (or doesn't) is as expressive as what it sees. A locked-off
tripod shot says something profoundly different from a handheld chase. Movement
conveys the story's nervous system — its pulse, its breathing, its flight-or-fight.
"""

# ---------------------------------------------------------------------------
# Camera Movements — the vocabulary of motion
# ---------------------------------------------------------------------------

CAMERA_MOVEMENTS: dict[str, dict] = {
    "static": {
        "description": "The camera does not move. Locked on a tripod or fixed mount. This is not "
        "absence of choice — it is the most powerful choice. Static frames communicate "
        "control, observation, judgment, or contemplation. Kubrick's locked-off symmetry. "
        "Ozu's tatami shots. Michael Haneke's unflinching gaze. The camera's stillness "
        "says 'I will not look away, and neither will you.'",
        "emotional_quality": "control, contemplation, power, clinical observation, judgment",
        "speed": "none",
        "equipment": "tripod, fixed mount, sticks",
        "masters": ["Kubrick", "Ozu", "Haneke", "Wes Anderson", "Fincher"],
        "prompt_keywords": [
            "static camera",
            "locked-off tripod shot",
            "motionless observation",
            "fixed camera position",
            "tableau composition",
        ],
        "best_for": ["dialogue", "tableau", "horror reveal", "power dynamics", "symmetry"],
    },
    "pan": {
        "description": "Horizontal rotation from a fixed position — the camera surveys the "
        "scene or follows lateral movement. A slow pan reveals environment; a fast pan "
        "(whip pan) creates temporal displacement or comedic energy. The pan says "
        "'look at this, then this, then this' — it's the camera as tour guide.",
        "emotional_quality": "revelation, survey, connection between elements, context",
        "speed": "slow to whip",
        "equipment": "tripod with fluid head, gear head",
        "masters": ["Spielberg", "Leone (slow reveal pans)"],
        "prompt_keywords": [
            "slow pan reveal",
            "horizontal camera pan",
            "panoramic sweep",
            "survey pan",
        ],
        "best_for": ["environmental reveal", "connecting characters", "landscape survey"],
    },
    "tilt": {
        "description": "Vertical rotation from a fixed position — the camera looks up or down. "
        "Tilt up reveals scale (looking up at a building, a mountain, a god). Tilt down "
        "reveals ground truth (a body, a clue, the earth). The tilt is the camera "
        "lifting or lowering its gaze.",
        "emotional_quality": "scale revelation, power dynamics, awe, discovery",
        "speed": "slow to medium",
        "equipment": "tripod with fluid head",
        "masters": ["Hitchcock (tilt reveals)", "Nolan (scale tilts)"],
        "prompt_keywords": [
            "camera tilt up",
            "vertical reveal",
            "tilt down discovery",
            "scale reveal tilt",
        ],
        "best_for": ["scale reveal", "power dynamics", "architectural awe", "ground discovery"],
    },
    "dolly": {
        "description": "Camera physically moves forward or backward on a track or wheeled platform. "
        "The dolly is the emotional proximity tool — dolly in = the audience is drawn closer, "
        "drawn into the moment, realizing something. Dolly out = the audience is pushed away, "
        "abandoned, left behind. Spielberg's dolly-in-on-the-face-of-realization is perhaps "
        "the most imitated camera move in cinema.",
        "emotional_quality": "intimacy shift, realization, abandonment, emotional proximity change",
        "speed": "imperceptible to medium",
        "equipment": "dolly on track, dana dolly, slider",
        "masters": ["Spielberg (dolly-in)", "Kubrick (hallway dollies)", "Scorsese"],
        "prompt_keywords": [
            "dolly-in close",
            "tracking dolly shot",
            "smooth forward camera movement",
            "dolly push-in",
            "camera pulling back slowly",
        ],
        "best_for": ["emotional realization", "character approach", "slow reveal", "isolation (dolly out)"],
    },
    "track": {
        "description": "Camera moves laterally alongside the subject — walking with them, running "
        "with them, existing in their timeline. The tracking shot says 'I am with you, "
        "we are on this journey together.' Scorsese's Copacabana shot in Goodfellas. "
        "Kubrick's Steadicam tracks through the Overlook Hotel.",
        "emotional_quality": "companionship, journey, unbroken time, immersion",
        "speed": "walking pace to running",
        "equipment": "dolly on track, Steadicam, gimbal",
        "masters": ["Scorsese", "Kubrick", "Spielberg", "Iñárritu"],
        "prompt_keywords": [
            "lateral tracking shot",
            "side-tracking movement",
            "walking alongside subject",
            "parallel camera tracking",
        ],
        "best_for": ["walk-and-talk", "journey", "corridor", "procession"],
    },
    "steadicam": {
        "description": "Camera mounted on a body-worn stabilization rig — creates floating, "
        "smooth movement that can go anywhere a human can walk. The Steadicam is "
        "the camera freed from the earth but not quite in the air — it hovers, glides, "
        "follows. It creates a dreamlike quality of effortless observation. Kubrick "
        "pioneered its use; Lubezki perfected the art of extended Steadicam takes.",
        "emotional_quality": "floating immersion, dreamlike observation, subjective presence",
        "speed": "walking to running",
        "equipment": "Steadicam rig, Tiffen system, MōVI Pro",
        "masters": ["Kubrick (The Shining)", "Lubezki (Birdman)", "Scorsese (Goodfellas)"],
        "prompt_keywords": [
            "Steadicam floating movement",
            "smooth gliding camera",
            "flowing camera movement",
            "stabilized following shot",
            "dreamlike camera glide",
        ],
        "best_for": ["long takes", "following through spaces", "immersive exploration", "subjective POV"],
    },
    "handheld": {
        "description": "Camera held by the operator's hands — no stabilization. The image breathes, "
        "shakes, reacts. This is the camera as nervous system — it responds to the chaos "
        "of the moment with physical sympathy. The Dardenne brothers, Paul Greengrass, "
        "and the Dogme 95 movement made handheld the language of raw truth. At its best, "
        "it's intimate and authentic. At its worst, it's nauseating.",
        "emotional_quality": "urgency, anxiety, authenticity, documentary truth, chaos, intimacy",
        "speed": "reactive — matches the energy of the scene",
        "equipment": "camera on shoulder or in hands, easy rig for partial support",
        "masters": ["Greengrass", "Dardenne brothers", "von Trier", "Cuarón (Children of Men)"],
        "prompt_keywords": [
            "handheld camera shake",
            "documentary handheld",
            "shaky camera urgency",
            "raw handheld movement",
            "visceral camera shake",
        ],
        "best_for": ["action chaos", "documentary", "emotional crisis", "verite realism"],
    },
    "crane": {
        "description": "Camera rises or descends on a mechanical arm — the god's-eye ascending "
        "or the heavenly descent. Crane shots add the vertical axis to camera movement. "
        "Rising up from a character to reveal the vast world around them. Descending into "
        "a scene like an angel arriving. The opening of Touch of Evil, the closing of "
        "every period drama ever made.",
        "emotional_quality": "grandeur, liberation, overview, divine perspective, emotional release",
        "speed": "slow, majestic",
        "equipment": "Technocrane, Scorpio, jib arm, Supertechno",
        "masters": ["Welles (Touch of Evil)", "Scorsese", "Spielberg"],
        "prompt_keywords": [
            "crane shot rising",
            "ascending camera movement",
            "aerial crane sweep",
            "jib arm elevation",
            "god's-eye ascending",
        ],
        "best_for": ["emotional release", "establishing grandeur", "conclusion/opening", "reveal scale"],
    },
    "drone": {
        "description": "Aerial camera platform — the omniscient observer. Drones have democratized "
        "what used to require helicopters. They can reveal landscapes, follow cars on roads, "
        "ascend buildings, and create vertigo-inducing top-downs. The danger is overuse — "
        "when every establishing shot is a drone shot, the awe dissipates.",
        "emotional_quality": "omniscience, scale, freedom, surveillance, awe",
        "speed": "slow drift to high-speed pursuit",
        "equipment": "DJI Inspire, custom cinema drones, FPV drones",
        "masters": ["modern productions universally", "FPV specialists"],
        "prompt_keywords": [
            "aerial drone shot",
            "bird's-eye view",
            "sweeping aerial",
            "drone establishing shot",
            "top-down overhead",
        ],
        "best_for": ["establishing shots", "landscape", "chase sequences", "scale reveal"],
    },
    "vertigo_zolly": {
        "description": "The dolly zoom — simultaneously dollying in while zooming out (or vice versa). "
        "The subject stays the same size but the background stretches or compresses "
        "impossibly. Invented for Hitchcock's Vertigo. The visual equivalent of the "
        "ground dropping out from under you. Used for moments of psychological crisis, "
        "realization of horror, or reality warping.",
        "emotional_quality": "psychological distortion, horror, vertigo, reality shift, existential dread",
        "speed": "slow to medium — too fast loses the effect",
        "equipment": "dolly + zoom lens, precise coordination",
        "masters": ["Hitchcock (Vertigo)", "Spielberg (Jaws)", "Scorsese (Goodfellas)"],
        "prompt_keywords": [
            "dolly zoom effect",
            "vertigo shot",
            "zolly perspective shift",
            "background stretching",
            "Hitchcock vertigo effect",
        ],
        "best_for": ["psychological crisis", "horror reveal", "reality distortion", "realization of danger"],
    },
    "whip_pan": {
        "description": "Extremely fast horizontal rotation — the image blurs into streaks during the "
        "transition. Used as a cut alternative (whip from one subject to another), "
        "temporal compression (whip pan = time has passed), or pure kinetic energy. "
        "Paul Thomas Anderson and Edgar Wright use whip pans as punctuation.",
        "emotional_quality": "energy, temporal jump, comedic timing, urgency, kinetic",
        "speed": "maximum — motion-blurred",
        "equipment": "tripod with loose head, or handheld",
        "masters": ["P.T. Anderson", "Edgar Wright", "Tarantino"],
        "prompt_keywords": [
            "whip pan motion blur",
            "fast camera rotation",
            "kinetic whip pan",
            "motion-blurred pan transition",
        ],
        "best_for": ["comedy transitions", "time compression", "energy injection", "match cut alternative"],
    },
    "push_in": {
        "description": "A slow, deliberate forward movement — the camera creeping toward the subject. "
        "Different from a quick dolly-in; the push-in is imperceptible at first, building "
        "tension over time. The viewer unconsciously feels the space closing. Fincher is "
        "the modern master — many of his dialogue scenes feature a barely-perceptible push-in "
        "that creates mounting unease.",
        "emotional_quality": "mounting tension, creeping dread, focused attention, compression of space",
        "speed": "imperceptibly slow",
        "equipment": "dolly, slider, motorized system",
        "masters": ["Fincher", "Kubrick", "Villeneuve"],
        "prompt_keywords": [
            "slow push-in",
            "creeping forward movement",
            "subtle dolly forward",
            "Fincher push-in",
            "tension-building approach",
        ],
        "best_for": ["mounting tension", "dialogue scenes", "psychological thriller", "confrontation"],
    },
}

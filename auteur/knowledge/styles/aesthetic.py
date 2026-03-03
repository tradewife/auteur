"""Aesthetic style system — freeform user-defined styles enriched with auteur depth.

The user never has to pick from a list. They describe what they want in any way
they want — mood, references, vibes, colors, whatever. The AuteurLayer
analyzes those signals and blends in the right cinematographic techniques from
the master DP profiles to give the style real depth.

The auteur layer is invisible to the user. They say "rainy Tokyo night, lonely
and neon-lit" and they get Deakins's shadow control + Storaro's color boldness
woven into their prompt. They never see the DP names unless they go looking.

Usage:
    style = AestheticStyle(
        description="warm, intimate, golden afternoon light filtering through curtains",
        mood="nostalgic and tender",
    )
    enriched = AuteurLayer.enrich(style)
    # enriched.auteur_blend → {"lubezki": 0.42, "deakins": 0.15, ...}
    # enriched.enriched_keywords → ["golden hour cinematography", "magic hour backlight", ...]
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from auteur.knowledge.styles.base import StyleProfile


class AestheticStyle(BaseModel):
    """A user-defined visual style — entirely freeform.

    No presets required. The user describes their vision in any terms they want
    and the AuteurLayer resolves the cinematographic depth automatically.
    """

    # User input — any or all of these can be populated
    description: str = Field(
        default="",
        description="Freeform style description — anything the user says about the look they want",
    )
    mood: str = Field(default="", description="Emotional tone / feeling")
    lighting_feel: str = Field(default="", description="How the light should feel")
    color_feel: str = Field(default="", description="Color approach / palette feel")
    movement_feel: str = Field(default="", description="How the camera should behave")
    texture_feel: str = Field(default="", description="Film/digital texture preference")
    references: list[str] = Field(
        default_factory=list,
        description="Reference films, photographers, paintings, moods, anything",
    )

    # Resolved by AuteurLayer
    auteur_blend: dict[str, float] = Field(
        default_factory=dict,
        description="Weighted auteur contributions (0.0-1.0 each)",
    )
    enriched_keywords: list[str] = Field(
        default_factory=list,
        description="Prompt keywords pulled from matched auteur profiles",
    )
    enriched_negative: list[str] = Field(
        default_factory=list,
        description="Negative prompt keywords from matched auteur profiles",
    )
    enriched_lighting: str = Field(
        default="",
        description="Lighting approach synthesized from auteur blend",
    )
    enriched_movement: list[str] = Field(
        default_factory=list,
        description="Movement preferences from auteur blend",
    )

    @property
    def all_text(self) -> str:
        """Concatenate all user-provided text for signal matching."""
        parts = [
            self.description, self.mood, self.lighting_feel,
            self.color_feel, self.movement_feel, self.texture_feel,
        ] + self.references
        return " ".join(p for p in parts if p).lower()

    @property
    def dominant_auteur(self) -> str | None:
        """The highest-weighted auteur in the blend, if any."""
        if not self.auteur_blend:
            return None
        return max(self.auteur_blend, key=self.auteur_blend.get)


class AuteurLayer:
    """Enriches user-defined styles with auteur cinematographic depth.

    Analyzes the user's freeform description for signals across five dimensions
    (mood, lighting, color, movement, texture) and scores each auteur profile's
    relevance. The result is a weighted blend of techniques that deepens the
    user's vision with real cinematographic specificity.

    The auteur_weight parameter (0.0-1.0) controls how much the auteur layer
    influences the final output:
    - 0.0: No auteur enrichment — just the user's own words
    - 0.5: Moderate enrichment — subtle DP influence
    - 0.7: Default — strong enrichment that still respects the user's intent
    - 1.0: Maximum auteur depth — the DP profiles dominate the style layer
    """

    # -----------------------------------------------------------------------
    # Signal dictionaries — keywords that trigger affinity for each auteur
    # across five perceptual dimensions.
    #
    # These are intentionally broad and overlapping. A "warm" description
    # signals both Lubezki and Hoytema; the other dimensions disambiguate.
    # -----------------------------------------------------------------------

    _SIGNALS: dict[str, dict[str, list[str]]] = {
        "deakins": {
            "mood": [
                "lonely", "isolated", "bleak", "contemplative", "quiet", "tense",
                "cold", "restrained", "somber", "austere", "stark", "melancholy",
                "desolate", "still", "stoic", "dignified", "understated", "sober",
                "meditative", "brooding", "pensive", "resigned", "controlled",
            ],
            "lighting": [
                "shadow", "shadows", "dark", "window light", "single source",
                "motivated", "silhouette", "negative fill", "controlled",
                "atmospheric", "haze", "fog", "mist", "dim", "low key",
                "backlit", "shaft of light", "one light", "practical lamp",
                "pool of light", "darkness", "chiaroscuro", "penumbra",
            ],
            "color": [
                "desaturated", "muted", "cool", "monochrome", "restrained",
                "blue grey", "steel", "neutral", "subdued", "drained",
                "bleached", "washed out", "cold tones", "grey", "ash",
            ],
            "movement": [
                "static", "still", "slow", "controlled", "subtle", "locked",
                "steady", "minimal", "deliberate", "measured", "patient",
            ],
            "texture": [
                "clean", "sharp", "precise", "digital", "crisp",
                "immaculate", "polished",
            ],
        },
        "storaro": {
            "mood": [
                "passionate", "dramatic", "operatic", "bold", "expressive",
                "theatrical", "intense", "romantic", "epic", "fiery",
                "sensual", "lush", "decadent", "extravagant", "baroque",
                "mythic", "symbolic", "ritualistic", "primal", "visceral",
            ],
            "lighting": [
                "colored light", "neon", "gel", "gelled", "mixed color",
                "warm cool", "dramatic", "chiaroscuro", "contrast",
                "layered", "bold light", "painted light", "rich",
                "colored shadow", "split color", "complementary",
                "fluorescent", "sodium vapor", "electric", "vibrant light",
            ],
            "color": [
                "saturated", "bold", "vivid", "rich", "warm", "orange",
                "red", "gold", "symbolic", "vibrant", "colorful",
                "jewel tones", "deep", "intense color", "crimson",
                "amber", "magenta", "purple", "neon", "electric",
            ],
            "movement": [
                "sweeping", "fluid", "crane", "elaborate", "choreographed",
                "operatic", "dramatic", "graceful", "dance", "flowing",
            ],
            "texture": [
                "film", "grain", "rich", "painterly", "lush", "textured",
                "velvet", "oil painting",
            ],
        },
        "lubezki": {
            "mood": [
                "spiritual", "intimate", "organic", "flowing", "alive",
                "present", "raw", "real", "immersive", "ethereal",
                "dreamlike", "gentle", "tender", "nostalgic", "wistful",
                "meditative", "transcendent", "peaceful", "serene",
                "bittersweet", "yearning", "memory", "breath", "fleeting",
            ],
            "lighting": [
                "natural light", "golden hour", "magic hour", "sunlight",
                "backlit", "available light", "candle", "candlelight", "fire",
                "firelight", "soft light", "warm glow", "ambient", "dappled",
                "sun flare", "rim light", "edge light", "twilight",
                "overcast", "diffused", "gentle light", "dawn", "dusk",
                "sunset", "sunrise", "afternoon light", "morning light",
            ],
            "color": [
                "earth tones", "natural", "warm", "amber", "golden",
                "green", "organic", "honey", "autumn", "pastoral",
                "sun-kissed", "warm tones", "olive", "moss", "copper",
            ],
            "movement": [
                "handheld", "flowing", "long take", "steadicam",
                "following", "immersive", "continuous", "floating",
                "breathing", "restless", "drifting", "wandering",
                "tracking", "unbroken", "roaming", "gliding",
            ],
            "texture": [
                "natural", "organic", "soft", "gentle", "film",
                "luminous", "glowing", "alive",
            ],
        },
        "hoytema": {
            "mood": [
                "epic", "vast", "grand", "overwhelming", "physical",
                "tactile", "monumental", "awe", "imposing", "massive",
                "colossal", "industrial", "mechanical", "brutal",
                "apocalyptic", "war", "survival", "gritty", "raw power",
                "relentless", "towering", "crushing", "elemental",
            ],
            "lighting": [
                "large source", "wrap", "wraparound", "bounce", "bounced",
                "underexposed", "pushed", "practical", "sculptural",
                "harsh sun", "overcast sky", "storm light", "industrial light",
                "cockpit", "instrument panel", "explosion", "fire",
            ],
            "color": [
                "warm earth", "amber", "dust", "dusty", "sepia",
                "monochrome", "black and white", "desaturated", "vintage",
                "kodachrome", "faded", "earth", "sand", "ochre",
                "brown", "khaki", "gunmetal",
            ],
            "movement": [
                "handheld", "physical", "weighty", "mounted", "vehicle",
                "heavy", "grounded", "unstable", "shaky", "visceral",
                "crash", "impact",
            ],
            "texture": [
                "grain", "film grain", "65mm", "imax", "large format",
                "halation", "analog", "photochemical", "textured", "gritty",
                "noisy", "rough", "imperfect", "celluloid", "vintage",
                "degraded", "worn",
            ],
        },
    }

    # Dimension weights — how much each dimension contributes to the final score.
    # Mood and lighting are the strongest signals for style identity.
    _DIMENSION_WEIGHTS: dict[str, float] = {
        "mood": 1.5,
        "lighting": 1.3,
        "color": 1.0,
        "movement": 0.8,
        "texture": 0.7,
    }

    @classmethod
    def enrich(
        cls,
        style: AestheticStyle,
        auteur_weight: float = 0.7,
    ) -> AestheticStyle:
        """Enrich a user-defined style with auteur cinematographic depth.

        Analyzes the user's freeform text for signals, scores each auteur's
        relevance, and blends their techniques into the style.

        Args:
            style: The user's freeform AestheticStyle.
            auteur_weight: How much auteur influence to apply (0.0-1.0).
                0.0 = no enrichment, 1.0 = maximum auteur depth.

        Returns:
            The same AestheticStyle with auteur_blend, enriched_keywords,
            enriched_negative, enriched_lighting, and enriched_movement populated.
        """
        from auteur.knowledge.styles import STYLE_PROFILES

        text = style.all_text
        if not text.strip():
            return style

        # Score each auteur across all dimensions
        raw_scores: dict[str, float] = {}
        for auteur, dimensions in cls._SIGNALS.items():
            score = 0.0
            for dim_name, keywords in dimensions.items():
                dim_weight = cls._DIMENSION_WEIGHTS.get(dim_name, 1.0)
                matches = sum(1 for kw in keywords if kw in text)
                score += matches * dim_weight
            raw_scores[auteur] = score

        # Normalize to blend weights (0.0-1.0)
        total = sum(raw_scores.values())
        if total > 0:
            blend = {
                k: round((v / total) * auteur_weight, 3)
                for k, v in raw_scores.items()
            }
        else:
            # No signals matched — apply a light even blend
            n = len(raw_scores)
            blend = {k: round(auteur_weight / n, 3) for k in raw_scores}

        # Pull enrichment from profiles, weighted by blend strength
        enriched_keywords: list[str] = []
        enriched_negative: list[str] = []
        lighting_parts: list[str] = []
        movement_parts: list[str] = []

        for auteur, weight in sorted(blend.items(), key=lambda x: -x[1]):
            if weight < 0.05:
                continue  # Below threshold — skip

            profile = STYLE_PROFILES.get(auteur)
            if not profile:
                continue

            # Scale keyword count by weight — heavier auteur gets more keywords
            n_keywords = max(1, int(weight * 12))
            enriched_keywords.extend(profile.prompt_keywords[:n_keywords])

            n_negative = max(1, int(weight * 6))
            enriched_negative.extend(profile.negative_keywords[:n_negative])

            # Lighting approach — weighted contribution
            if weight >= 0.15 and profile.lighting_approach:
                # Extract the core lighting idea (first sentence)
                core_lighting = profile.lighting_approach.split(".")[0].strip()
                lighting_parts.append(core_lighting)

            # Movement preferences
            if weight >= 0.10 and profile.preferred_movement:
                n_moves = max(1, int(weight * 4))
                movement_parts.extend(profile.preferred_movement[:n_moves])

        # Deduplicate while preserving order
        seen_kw: set[str] = set()
        unique_keywords = []
        for kw in enriched_keywords:
            if kw not in seen_kw:
                seen_kw.add(kw)
                unique_keywords.append(kw)

        seen_neg: set[str] = set()
        unique_negative = []
        for kw in enriched_negative:
            if kw not in seen_neg:
                seen_neg.add(kw)
                unique_negative.append(kw)

        seen_move: set[str] = set()
        unique_movement = []
        for m in movement_parts:
            if m not in seen_move:
                seen_move.add(m)
                unique_movement.append(m)

        # Populate the style
        style.auteur_blend = blend
        style.enriched_keywords = unique_keywords
        style.enriched_negative = unique_negative
        style.enriched_lighting = "; ".join(lighting_parts)
        style.enriched_movement = unique_movement

        return style

    @classmethod
    def explain_blend(cls, style: AestheticStyle) -> str:
        """Human-readable explanation of why each auteur was matched.

        Useful for the MCP agent to explain its creative reasoning to the user.
        """
        if not style.auteur_blend:
            return "No auteur enrichment applied."

        from auteur.knowledge.styles import STYLE_PROFILES

        parts = []
        for auteur, weight in sorted(style.auteur_blend.items(), key=lambda x: -x[1]):
            if weight < 0.05:
                continue
            profile = STYLE_PROFILES.get(auteur)
            name = profile.name if profile else auteur
            pct = int(weight * 100)

            # Find which signals actually matched
            text = style.all_text
            matched_dims: list[str] = []
            for dim_name, keywords in cls._SIGNALS.get(auteur, {}).items():
                hits = [kw for kw in keywords if kw in text]
                if hits:
                    matched_dims.append(f"{dim_name} ({', '.join(hits[:3])})")

            reason = ", ".join(matched_dims) if matched_dims else "base blend"
            parts.append(f"  {name}: {pct}% — {reason}")

        return "Auteur blend:\n" + "\n".join(parts)

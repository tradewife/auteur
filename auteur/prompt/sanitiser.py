"""Prompt sanitiser — enforcement gate for prompt language quality.

Validates and cleans prompts before they reach generation models.
Three responsibilities:
1. Forbidden word filtering (genre labels, dead emotional words, transcendence clichés)
2. Camera package validation (every shot must specify body, lens, focal length, aperture)
3. Meisner note validation (behavior, not adjectives)
4. Full shot validation (pre-generation checklist)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from auteur.knowledge.ontology import ShotSpec


# ---------------------------------------------------------------------------
# Banned token sets
# ---------------------------------------------------------------------------

# Genre labels that slopify everything they touch
BANNED_GENRE_TOKENS: set[str] = {
    "cyberpunk", "sci-fi", "science fiction", "futuristic", "dystopian",
    "fantasy", "dark academia", "steampunk", "solarpunk", "afrofuturism",
}

# Dead emotional words — semantic zombies that return the average of all feelings
BANNED_EMOTIONAL_TOKENS: set[str] = {
    "love", "fear", "beauty", "truth", "hope", "grief", "joy", "peace",
    "sad", "happy", "lonely", "lost", "broken", "healed", "powerful",
    "dramatic", "emotional", "atmospheric", "mysterious", "stunning",
    "breathtaking", "moving", "touching", "profound",
}

# Dead transcendence words — stock-photo spirituality
BANNED_TRANSCENDENCE_TOKENS: set[str] = {
    "ethereal", "otherworldly", "celestial", "divine", "sacred",
    "transcendent", "spiritual", "mystical", "dreamlike", "surreal",
    "magical", "haunting", "evocative", "luminous", "glowing",
    "radiant", "majestic", "epic", "grand", "cosmic", "infinite",
}

# Prompt padding that adds nothing
BANNED_PADDING_TOKENS: set[str] = {
    "masterpiece", "trending on artstation", "highly detailed",
    "award-winning", "cinematic", "professional photography",
    "8k", "4k", "uhd", "ultra realistic",
}

# Combined default set
BANNED_TOKENS: set[str] = (
    BANNED_GENRE_TOKENS
    | BANNED_EMOTIONAL_TOKENS
    | BANNED_TRANSCENDENCE_TOKENS
    | BANNED_PADDING_TOKENS
)

# Emotion-adjectives forbidden in meisner_note
MEISNER_FORBIDDEN_ADJECTIVES: set[str] = {
    "sad", "happy", "angry", "afraid", "lonely", "broken", "hopeful",
    "lost", "melancholy", "joyful", "desperate", "peaceful", "anxious",
    "tender", "fierce", "vulnerable", "strong", "weak", "brave",
    "sadly", "lovingly", "desperately", "tenderly", "angrily",
    "hopefully", "fearfully",
}

# Camera package keywords — at least one must be present
CAMERA_PACKAGE_INDICATORS: list[str] = [
    "shot on", "Shot on", "ARRI", "RED", "Sony", "Panavision",
    "mm,", "mm ", "T1.", "T2.", "f/1.", "f/2.", "f/4", "f/8",
]


# ---------------------------------------------------------------------------
# Validation types
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationIssue:
    """A single validation failure."""
    severity: Severity
    field: str
    message: str


@dataclass
class ValidationResult:
    """Result of validate_shot() — list of issues found."""
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def passed(self) -> bool:
        """True if no errors (warnings are acceptable)."""
        return len(self.errors) == 0

    def summary(self) -> dict:
        return {
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [
                {"severity": i.severity.value, "field": i.field, "message": i.message}
                for i in self.issues
            ],
        }


class PromptValidationError(Exception):
    """Raised when a prompt fails hard validation."""
    pass


# ---------------------------------------------------------------------------
# Filtering functions
# ---------------------------------------------------------------------------


def strip_banned_tokens(
    text: str,
    extra_banned: list[str] | None = None,
) -> str:
    """Remove banned tokens from prompt text.

    Uses word-boundary matching so 'lonely' is stripped but 'loneliness'
    in a compound phrase is preserved.
    """
    all_banned = BANNED_TOKENS | set(extra_banned or [])
    for token in sorted(all_banned, key=len, reverse=True):
        # Case-insensitive whole-word/phrase removal
        pattern = rf"\b{re.escape(token)}\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    # Clean up double commas, double spaces
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r",\s*$", "", text)
    text = re.sub(r"^\s*,", "", text)
    return text.strip()


def find_banned_tokens(
    text: str,
    extra_banned: list[str] | None = None,
) -> list[str]:
    """Return list of banned tokens found in the text."""
    all_banned = BANNED_TOKENS | set(extra_banned or [])
    found: list[str] = []
    text_lower = text.lower()
    for token in all_banned:
        if re.search(rf"\b{re.escape(token)}\b", text_lower):
            found.append(token)
    return sorted(found)


def has_camera_package(text: str) -> bool:
    """Check if the prompt contains a camera package sentence."""
    return any(indicator in text for indicator in CAMERA_PACKAGE_INDICATORS)


def validate_meisner_note(note: str) -> list[str]:
    """Validate a meisner_note. Returns list of problems (empty = valid)."""
    problems: list[str] = []
    if not note.strip():
        problems.append("meisner_note is empty")
        return problems

    note_lower = note.lower()
    for adj in MEISNER_FORBIDDEN_ADJECTIVES:
        if re.search(rf"\b{re.escape(adj)}\b", note_lower):
            problems.append(f"Contains forbidden emotion-adjective: '{adj}'")

    return problems


# ---------------------------------------------------------------------------
# Full shot validation
# ---------------------------------------------------------------------------


def validate_shot(
    shot: ShotSpec,
    composed_prompt: str = "",
    extra_banned: list[str] | None = None,
) -> ValidationResult:
    """Pre-generation validation for a ShotSpec.

    Returns ValidationResult with errors and warnings.
    Does NOT raise — lets the caller decide severity.

    Checks:
    1. aesthetic_style is not None (error)
    2. meisner_note is non-empty when character_id is set (error)
    3. meisner_note passes adjective check (error)
    4. duration_seconds is not at default 6.0 (warning)
    5. tension_level is not at default 0.5 (warning)
    6. narrative_beat is not empty (warning)
    7. Composed prompt has no banned tokens (error)
    8. Composed prompt contains camera package (error)
    9. i2v_source_url populated for character shots (warning)
    """
    result = ValidationResult()

    # 1. Visual language must be locked
    if shot.aesthetic_style is None:
        result.issues.append(ValidationIssue(
            Severity.ERROR, "aesthetic_style",
            "Visual language not locked — call propose_visual_language() first",
        ))

    # 2-3. Meisner note validation
    if shot.character_id:
        if not shot.meisner_note.strip():
            result.issues.append(ValidationIssue(
                Severity.ERROR, "meisner_note",
                f"Empty meisner_note for character '{shot.character_id}' — "
                "every character shot needs visible physical behavior",
            ))
        else:
            meisner_problems = validate_meisner_note(shot.meisner_note)
            for problem in meisner_problems:
                result.issues.append(ValidationIssue(
                    Severity.ERROR, "meisner_note", problem,
                ))

    # 4. Duration should be intentional
    if shot.duration_seconds == 6.0:
        result.issues.append(ValidationIssue(
            Severity.WARNING, "duration_seconds",
            "Duration at default 6.0 — should be set by tension_to_duration()",
        ))

    # 5. Tension should be set by beat structure
    if shot.tension_level == 0.5:
        result.issues.append(ValidationIssue(
            Severity.WARNING, "tension_level",
            "Tension at default 0.5 — should be set by beat structure",
        ))

    # 6. Narrative beat
    if not shot.narrative_beat:
        result.issues.append(ValidationIssue(
            Severity.WARNING, "narrative_beat",
            "No narrative_beat set — shot may lack dramatic purpose",
        ))

    # 7-8. Prompt-level checks (only if composed prompt provided)
    if composed_prompt:
        banned_found = find_banned_tokens(composed_prompt, extra_banned)
        if banned_found:
            result.issues.append(ValidationIssue(
                Severity.ERROR, "prompt",
                f"Banned tokens in prompt: {', '.join(banned_found)}",
            ))
        if not has_camera_package(composed_prompt):
            result.issues.append(ValidationIssue(
                Severity.ERROR, "prompt",
                "Missing camera package — prompt must specify body, lens, focal length, aperture",
            ))

    # 9. i2v source for character shots
    if shot.character_id and not shot.i2v_source_url:
        result.issues.append(ValidationIssue(
            Severity.WARNING, "i2v_source_url",
            f"No hero shot URL for character '{shot.character_id}' — "
            "generate_hero_shots() should be called first",
        ))

    return result

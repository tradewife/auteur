"""Base platform spec — defines how to talk to a web-based generation platform.

Each platform spec builds agent task prompts and parses structured JSON results.
No selectors, no DOM manipulation — the LLM agent handles all interaction.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auteur.providers.base import GenerationRequest


class PlatformSpec(ABC):
    """Specification for a browser-automated generation platform.

    Subclasses define:
    - Where to go (URLs)
    - What to tell the agent (task prompts)
    - How to parse the agent's structured output
    """

    model_id: str
    platform: str
    start_url: str
    login_url: str | None = None
    timeout_s: int = 900
    poll_interval_s: int = 20

    @abstractmethod
    def build_submit_task(self, request: GenerationRequest) -> str:
        """Build the agent task prompt for submitting a generation job."""
        ...

    @abstractmethod
    def build_status_task(self) -> str:
        """Build the agent task prompt for checking generation status."""
        ...

    @abstractmethod
    def build_collect_task(self) -> str:
        """Build the agent task prompt for collecting completed outputs."""
        ...

    def build_login_check_task(self) -> str:
        """Build the agent task prompt for verifying login state."""
        return (
            f"Go to {self.start_url}. "
            "Check if you are logged in. "
            "Respond with EXACTLY this JSON and nothing else: "
            '{"logged_in": true} or {"logged_in": false}'
        )

    def parse_json_response(self, text: str) -> dict:
        """Extract JSON from agent response text."""
        # Agent responses may contain markdown or extra text around JSON
        text = text.strip()
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Look for JSON block in response
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    continue
        return {"error": "Could not parse JSON from agent response", "raw": text}

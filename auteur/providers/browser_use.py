"""Browser-use provider — automates web-based generation platforms.

Plugs into AUTEUR's existing ProviderRegistry to expose browser-automated
platforms (Grok Imagine, Runway, Pika, etc.) alongside API-based providers.

Model IDs use a `-web` suffix to distinguish from API-backed models:
  grok-imagine-web, runway-web, pika-web
"""

from __future__ import annotations

from auteur.config import get_settings
from auteur.providers.base import (
    GenerationProvider,
    GenerationRequest,
    GenerationResult,
    GenerationType,
)


class BrowserUseProvider(GenerationProvider):
    """Provider that automates web platforms via browser-use + LLM agents.

    Requires:
    - browser-use installed (pip install browser-use)
    - Playwright chromium installed (playwright install chromium)
    - Auth bootstrapped for each platform (run bootstrap_auth once)
    - An LLM key for the agent controller (BROWSER_USE_API_KEY or GEMINI_API_KEY)
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def name(self) -> str:
        return "browser_use"

    @property
    def supported_models(self) -> list[str]:
        from auteur.browser_ops.platforms import PLATFORM_SPECS
        return list(PLATFORM_SPECS.keys())

    @property
    def supported_types(self) -> list[GenerationType]:
        return [GenerationType.IMAGE, GenerationType.VIDEO]

    def is_available(self) -> bool:
        return self._settings.browser_use_enabled and (
            self._settings.browser_use_api_key != ""
            or self._settings.gemini_api_key != ""
        )

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Run a generation task through a browser-automated platform.

        Routes to the correct platform spec based on the model ID,
        then delegates to the browser runner.
        """
        if not self.is_available():
            return GenerationResult(
                success=False,
                provider=self.name,
                model=request.prompt.model,
                error="Browser automation not enabled or no LLM key configured",
            )

        from auteur.browser_ops.auth import make_account
        from auteur.browser_ops.platforms import PLATFORM_SPECS
        from auteur.browser_ops.runner import run_browser_generation

        model_key = request.prompt.model
        spec = PLATFORM_SPECS.get(model_key)
        if not spec:
            return GenerationResult(
                success=False,
                provider=self.name,
                model=model_key,
                error=f"Unknown browser platform: {model_key}. "
                f"Available: {list(PLATFORM_SPECS.keys())}",
            )

        # Get or create the account for this platform
        account_key = request.prompt.parameters.get("account_key", "default")
        account = make_account(spec.platform, account_key)

        # Check runner mode: "agent" (default) or "cli" (deterministic fallback)
        runner_mode = request.metadata.get("runner", "agent")

        if runner_mode == "cli":
            from auteur.browser_ops.cli_runner import run_cli_generation
            return await run_cli_generation(
                request=request,
                spec=spec,
                account=account,
                headed=request.metadata.get("headed", False),
            )

        return await run_browser_generation(
            request=request,
            spec=spec,
            account=account,
        )

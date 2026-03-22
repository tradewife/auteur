"""CLI runner — deterministic browser automation via browser-use CLI.

Fallback for when the LLM Agent runner is too flaky on a platform.
Uses `browser-use` CLI commands (open, state, click, type, screenshot)
via subprocess, driven by the persistent daemon. No LLM needed for
the mechanical steps — only structured platform scripts.

The CLI daemon keeps the browser alive between commands (~50ms latency),
so this is fast and reliable for known UI flows.

Usage:
    Use run_browser_generation() (agent runner) as the default.
    Fall back to run_cli_generation() when agent keeps failing.
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auteur.browser_ops.auth import BrowserAccount
    from auteur.browser_ops.platforms.base import PlatformSpec
    from auteur.providers.base import GenerationRequest, GenerationResult


class CLISession:
    """Wrapper around browser-use CLI commands for a named session.

    Keeps a persistent daemon session alive and provides typed methods
    for each CLI command. All methods are synchronous (subprocess calls).
    """

    def __init__(self, session: str = "default", headed: bool = False):
        self.session = session
        self.headed = headed
        self._cli = _cli_path()

    def _run(self, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
        cmd = [self._cli, "--session", self.session]
        if self.headed:
            cmd.append("--headed")
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    def _run_json(self, *args: str, timeout: int = 30) -> dict:
        cmd = [self._cli, "--session", self.session, "--json"]
        if self.headed:
            cmd.append("--headed")
        cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "returncode": result.returncode}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout.strip()}

    def open(self, url: str) -> bool:
        r = self._run("open", url, timeout=30)
        return r.returncode == 0

    def state(self) -> dict:
        return self._run_json("state")

    def click(self, index: int) -> bool:
        r = self._run("click", str(index))
        return r.returncode == 0

    def type_text(self, text: str) -> bool:
        r = self._run("type", text)
        return r.returncode == 0

    def input_field(self, index: int, text: str) -> bool:
        r = self._run("input", str(index), text)
        return r.returncode == 0

    def keys(self, key_combo: str) -> bool:
        r = self._run("keys", key_combo)
        return r.returncode == 0

    def screenshot(self, path: str) -> bool:
        r = self._run("screenshot", path)
        return r.returncode == 0

    def scroll(self, direction: str = "down", amount: int | None = None) -> bool:
        args = ["scroll", direction]
        if amount:
            args.extend(["--amount", str(amount)])
        r = self._run(*args)
        return r.returncode == 0

    def wait_selector(self, css: str, timeout_ms: int = 10000, state: str = "visible") -> bool:
        r = self._run("wait", "selector", css, "--timeout", str(timeout_ms), "--state", state, timeout=max(30, timeout_ms // 1000 + 5))
        return r.returncode == 0

    def wait_text(self, text: str, timeout_ms: int = 10000) -> bool:
        r = self._run("wait", "text", text, "--timeout", str(timeout_ms), timeout=max(30, timeout_ms // 1000 + 5))
        return r.returncode == 0

    def eval_js(self, code: str) -> str:
        r = self._run("eval", code, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else ""

    def get_text(self, index: int) -> str:
        r = self._run("get", "text", str(index))
        return r.stdout.strip() if r.returncode == 0 else ""

    def get_title(self) -> str:
        r = self._run("get", "title")
        return r.stdout.strip() if r.returncode == 0 else ""

    def cookies_export(self, path: str, url: str | None = None) -> bool:
        args = ["cookies", "export", path]
        if url:
            args.extend(["--url", url])
        r = self._run(*args)
        return r.returncode == 0

    def cookies_import(self, path: str) -> bool:
        r = self._run("cookies", "import", path)
        return r.returncode == 0

    def close(self) -> None:
        self._run("close")

    def find_element_index(self, text_pattern: str) -> int | None:
        """Find an interactive element index by matching its text in state output."""
        state = self.state()
        data = state.get("data", state)
        elements = data.get("interactiveElements", data.get("elements", []))
        for el in elements:
            label = str(el.get("text", "") or el.get("label", "") or el.get("aria-label", ""))
            if text_pattern.lower() in label.lower():
                return el.get("index", el.get("id"))
        return None


class CLIPlatformScript:
    """Base class for deterministic CLI scripts per platform.

    Override run_submit(), check_status(), and collect_outputs() with
    platform-specific CLI command sequences.
    """

    def run_submit(self, cli: CLISession, request: GenerationRequest) -> dict:
        """Submit a generation job. Return {"status": "submitted"|"failed", ...}."""
        raise NotImplementedError

    def check_status(self, cli: CLISession) -> dict:
        """Check generation status. Return {"status": "completed"|"pending"|"failed", ...}."""
        raise NotImplementedError

    def collect_outputs(self, cli: CLISession, run_dir: Path) -> dict:
        """Collect outputs. Return {"asset_urls": [...], "page_url": "...", ...}."""
        raise NotImplementedError


class GrokImagineCLIScript(CLIPlatformScript):
    """Deterministic CLI script for Grok Imagine on x.com/i/grok."""

    def run_submit(self, cli: CLISession, request: GenerationRequest) -> dict:
        prompt = request.prompt.positive

        if not cli.open("https://x.com/i/grok"):
            return {"status": "failed", "notes": "Could not open Grok"}

        time.sleep(2)

        # Look for new chat button
        idx = cli.find_element_index("New")
        if idx is not None:
            cli.click(idx)
            time.sleep(1)

        # Find the text input
        idx = cli.find_element_index("Message")
        if idx is None:
            # Fallback: look for textarea in state
            state = cli.state()
            data = state.get("data", state)
            for el in data.get("interactiveElements", data.get("elements", [])):
                tag = str(el.get("tag", "")).lower()
                if tag in ("textarea", "input"):
                    idx = el.get("index", el.get("id"))
                    break

        if idx is not None:
            cli.input_field(idx, prompt)
        else:
            # Last resort: just type and hope focus is right
            cli.type_text(prompt)

        time.sleep(0.5)
        cli.keys("Enter")
        time.sleep(2)

        return {"status": "submitted", "notes": "Prompt submitted via CLI"}

    def check_status(self, cli: CLISession) -> dict:
        # Check page for loading indicators or completed images
        js_check = cli.eval_js("""
            (() => {
                const loading = document.querySelector('[aria-busy="true"], [role="progressbar"]');
                const imgs = document.querySelectorAll('img[src*="pbs.twimg.com"]');
                const videos = document.querySelectorAll('video');
                if (loading) return JSON.stringify({status: 'pending'});
                if (imgs.length > 0 || videos.length > 0) return JSON.stringify({status: 'completed', count: imgs.length + videos.length});
                return JSON.stringify({status: 'pending'});
            })()
        """)
        try:
            return json.loads(js_check)
        except (json.JSONDecodeError, TypeError):
            return {"status": "pending", "notes": "Could not parse status"}

    def collect_outputs(self, cli: CLISession, run_dir: Path) -> dict:
        # Screenshot the final state
        cli.screenshot(str(run_dir / "final.png"))

        # Extract asset URLs via JavaScript
        js_collect = cli.eval_js("""
            (() => {
                const urls = [];
                document.querySelectorAll('img[src*="pbs.twimg.com"]').forEach(img => urls.push(img.src));
                document.querySelectorAll('video source').forEach(src => urls.push(src.src));
                document.querySelectorAll('video[src]').forEach(v => urls.push(v.src));
                return JSON.stringify({asset_urls: [...new Set(urls)], page_url: location.href});
            })()
        """)
        try:
            return json.loads(js_collect)
        except (json.JSONDecodeError, TypeError):
            return {"asset_urls": [], "page_url": "", "notes": "Could not extract URLs"}


# Registry of CLI scripts
CLI_SCRIPTS: dict[str, CLIPlatformScript] = {
    "grok-imagine-web": GrokImagineCLIScript(),
}


async def run_cli_generation(
    request: GenerationRequest,
    spec: PlatformSpec,
    account: BrowserAccount,
    artifact_dir: Path | None = None,
    headed: bool = False,
) -> GenerationResult:
    """Execute a generation task using deterministic CLI commands.

    Fallback runner that uses browser-use CLI instead of LLM Agent.
    No LLM costs, fully deterministic, but requires per-platform
    CLI scripts and breaks when the UI changes.

    Args:
        request: The generation request.
        spec: Platform spec (used for model_id/platform/timeout).
        account: Account with storage_state.
        artifact_dir: Where to save artifacts.
        headed: Show browser window.

    Returns:
        GenerationResult.
    """
    from auteur.providers.base import GenerationResult

    script = CLI_SCRIPTS.get(spec.model_id)
    if not script:
        return GenerationResult(
            success=False,
            provider="browser_use_cli",
            model=spec.model_id,
            error=f"No CLI script for {spec.model_id}. Available: {list(CLI_SCRIPTS.keys())}",
        )

    if not account.storage_state_path.exists():
        return GenerationResult(
            success=False,
            provider="browser_use_cli",
            model=spec.model_id,
            error=f"No auth state for {account.label}. Run bootstrap_auth() first.",
        )

    # Set up artifact dir
    if artifact_dir is None:
        from auteur.config import get_settings
        artifact_dir = get_settings().browser_artifact_dir / spec.platform
    artifact_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"{spec.platform}_cli_{int(time.time())}"
    run_dir = artifact_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    session_name = f"auteur_{spec.platform}_{int(time.time())}"
    cli = CLISession(session=session_name, headed=headed)

    try:
        # Load cookies into the CLI session
        cli.cookies_import(str(account.storage_state_path))

        # Phase 1: Submit
        submit_result = await asyncio.get_event_loop().run_in_executor(
            None, script.run_submit, cli, request
        )
        _save_artifact(run_dir / "submit.json", submit_result)

        if submit_result.get("status") == "failed":
            return GenerationResult(
                success=False,
                provider="browser_use_cli",
                model=spec.model_id,
                error=f"Submit failed: {submit_result.get('notes', '')}",
                metadata={"run_id": run_id, "phase": "submit"},
            )

        # Phase 2: Poll
        deadline = time.monotonic() + spec.timeout_s
        poll_count = 0
        last_status = "pending"

        while time.monotonic() < deadline:
            await asyncio.sleep(spec.poll_interval_s)
            poll_count += 1

            status = await asyncio.get_event_loop().run_in_executor(
                None, script.check_status, cli
            )
            last_status = status.get("status", "pending")
            _save_artifact(run_dir / f"poll_{poll_count:03d}.json", status)

            if last_status == "completed":
                break
            if last_status == "failed":
                return GenerationResult(
                    success=False,
                    provider="browser_use_cli",
                    model=spec.model_id,
                    error=f"Generation failed: {status.get('notes', '')}",
                    metadata={"run_id": run_id, "phase": "poll", "polls": poll_count},
                )

        if last_status != "completed":
            return GenerationResult(
                success=False,
                provider="browser_use_cli",
                model=spec.model_id,
                error=f"Timed out after {spec.timeout_s}s ({poll_count} polls)",
                metadata={"run_id": run_id, "phase": "timeout"},
            )

        # Phase 3: Collect
        collected = await asyncio.get_event_loop().run_in_executor(
            None, script.collect_outputs, cli, run_dir
        )
        _save_artifact(run_dir / "collect.json", collected)

        asset_urls = collected.get("asset_urls", [])
        page_url = collected.get("page_url", "")
        primary_url = asset_urls[0] if asset_urls else page_url

        return GenerationResult(
            success=bool(primary_url),
            provider="browser_use_cli",
            model=spec.model_id,
            generation_type=request.generation_type,
            url=primary_url,
            metadata={
                "run_id": run_id,
                "platform": spec.platform,
                "asset_urls": asset_urls,
                "page_url": page_url,
                "artifact_dir": str(run_dir),
                "polls": poll_count,
                "notes": collected.get("notes", ""),
                "runner": "cli",
            },
        )

    except Exception as e:
        return GenerationResult(
            success=False,
            provider="browser_use_cli",
            model=spec.model_id,
            error=f"CLI runner error: {e!s}",
            metadata={"run_id": run_id, "runner": "cli"},
        )

    finally:
        cli.close()


def _save_artifact(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _cli_path() -> str:
    from auteur.browser_ops.auth import _cli_path as _auth_cli_path
    return _auth_cli_path()

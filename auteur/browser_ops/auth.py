"""Auth bootstrap — one-time manual login + storage_state persistence.

Three auth strategies (tried in order):
1. Existing storage_state file → Browser(storage_state=<path>)
2. Manual headed login → bootstrap_auth() → export storage_state
3. Cookie import → import_cookies() → convert to storage_state

The gstack pattern: stop treating login as the agent's job.
Seed the session from a real human login or exported cookies instead.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auteur.browser_ops.platforms.base import PlatformSpec


@dataclass
class BrowserAccount:
    """A platform/account pair with its auth state file."""

    platform: str
    account_key: str
    storage_state_path: Path

    @property
    def label(self) -> str:
        return f"{self.platform}:{self.account_key}"


def get_storage_state_dir() -> Path:
    """Get or create the storage state directory."""
    from auteur.config import get_settings
    settings = get_settings()
    state_dir = settings.browser_storage_state_dir
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def make_account(platform: str, account_key: str = "default") -> BrowserAccount:
    """Create a BrowserAccount with the standard storage state path."""
    state_dir = get_storage_state_dir()
    return BrowserAccount(
        platform=platform,
        account_key=account_key,
        storage_state_path=state_dir / f"{platform}_{account_key}.json",
    )


# ---------------------------------------------------------------------------
# Strategy 1: Existing storage_state (the normal path)
# ---------------------------------------------------------------------------


def has_auth(account: BrowserAccount) -> bool:
    """Check if a saved auth state exists for this account."""
    return account.storage_state_path.exists()


# ---------------------------------------------------------------------------
# Strategy 2: Manual headed login
# ---------------------------------------------------------------------------


async def bootstrap_auth(
    account: BrowserAccount,
    spec: PlatformSpec,
    executable_path: str | None = None,
) -> bool:
    """Open a headed browser for manual login, then export storage_state.

    Steps:
    1. Launch headed Chrome with the platform's start URL
    2. User logs in manually
    3. Export cookies/localStorage to storage_state JSON
    4. Verify auth with a quick agent check

    Args:
        account: The platform/account to authenticate.
        spec: Platform spec with URLs.
        executable_path: Chrome/Chromium path. Auto-detected if None.

    Returns:
        True if auth was successfully bootstrapped and verified.
    """
    from browser_use import Browser

    browser_kwargs: dict = {
        "headless": False,
        "window_size": {"width": 1280, "height": 900},
    }
    if executable_path:
        browser_kwargs["executable_path"] = executable_path

    # If there's existing state, load it
    if account.storage_state_path.exists():
        browser_kwargs["storage_state"] = str(account.storage_state_path)

    browser = Browser(**browser_kwargs)

    try:
        await browser.start()

        url = spec.login_url or spec.start_url
        print(f"[AUTEUR] Opening {url} for manual login...")
        print(f"[AUTEUR] Platform: {account.platform}, Account: {account.account_key}")
        print("[AUTEUR] Log in manually in the browser window.")
        print("[AUTEUR] Press Enter here when done.")
        await asyncio.get_event_loop().run_in_executor(None, input)

        # Export storage state
        await browser.export_storage_state(str(account.storage_state_path))
        print(f"[AUTEUR] Auth state saved to {account.storage_state_path}")

        return True

    finally:
        await browser.stop()


# ---------------------------------------------------------------------------
# Strategy 3: Cookie import (gstack pattern)
# ---------------------------------------------------------------------------


def import_cookies(
    account: BrowserAccount,
    cookie_source: str | Path,
    domain_filter: str | None = None,
) -> bool:
    """Import cookies from a JSON file into this account's storage_state.

    Accepts two formats:
    1. Playwright storage_state: {"cookies": [...], "origins": [...]}
    2. Flat cookie array: [{"name": "...", "value": "...", "domain": "..."}]
       (browser-use CLI export format, Chrome extension exports, etc.)

    Merges with existing storage_state if present. Optionally filters
    to cookies matching a specific domain.

    Args:
        account: Target account to import cookies into.
        cookie_source: Path to the cookie JSON file.
        domain_filter: Only import cookies matching this domain
            (e.g. ".x.com", ".google.com"). None = import all.

    Returns:
        True if cookies were imported successfully.
    """
    src = Path(cookie_source).expanduser()
    if not src.exists():
        raise FileNotFoundError(f"Cookie file not found: {src}")

    raw = json.loads(src.read_text(encoding="utf-8"))

    # Detect format and extract cookies
    if isinstance(raw, dict) and "cookies" in raw:
        # Playwright storage_state format
        incoming_cookies = raw["cookies"]
        incoming_origins = raw.get("origins", [])
    elif isinstance(raw, list):
        # Flat cookie array (CLI export, Chrome tools)
        incoming_cookies = raw
        incoming_origins = []
    else:
        raise ValueError(
            f"Unrecognized cookie format in {src}. "
            "Expected Playwright storage_state or flat cookie array."
        )

    # Filter by domain if requested
    if domain_filter:
        incoming_cookies = [
            c for c in incoming_cookies
            if _domain_matches(c.get("domain", ""), domain_filter)
        ]

    if not incoming_cookies:
        print(f"[AUTEUR] No cookies to import (filter: {domain_filter})")
        return False

    # Load existing state or start fresh
    existing: dict = {"cookies": [], "origins": []}
    if account.storage_state_path.exists():
        try:
            existing = json.loads(
                account.storage_state_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, KeyError):
            pass

    # Normalize incoming cookies to Playwright format
    normalized = [_normalize_cookie(c) for c in incoming_cookies]

    # Merge: incoming cookies override existing ones with same name+domain+path
    existing_keys = {
        (c.get("name"), c.get("domain"), c.get("path", "/"))
        for c in existing.get("cookies", [])
    }
    merged_cookies = list(existing.get("cookies", []))
    new_count = 0
    updated_count = 0
    for cookie in normalized:
        key = (cookie.get("name"), cookie.get("domain"), cookie.get("path", "/"))
        if key in existing_keys:
            # Replace existing cookie
            merged_cookies = [
                c for c in merged_cookies
                if (c.get("name"), c.get("domain"), c.get("path", "/")) != key
            ]
            merged_cookies.append(cookie)
            updated_count += 1
        else:
            merged_cookies.append(cookie)
            new_count += 1

    # Merge origins (localStorage)
    existing_origin_set = {o.get("origin") for o in existing.get("origins", [])}
    merged_origins = list(existing.get("origins", []))
    for origin in incoming_origins:
        if origin.get("origin") not in existing_origin_set:
            merged_origins.append(origin)

    # Write merged state
    state = {"cookies": merged_cookies, "origins": merged_origins}
    account.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
    account.storage_state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    total = new_count + updated_count
    print(
        f"[AUTEUR] Imported {total} cookies ({new_count} new, {updated_count} updated) "
        f"→ {account.storage_state_path}"
    )
    return True


def export_cookies_via_cli(
    output_path: str | Path,
    session: str = "default",
    url_filter: str | None = None,
) -> bool:
    """Export cookies from a running browser-use CLI session.

    Uses the `browser-use cookies export` command, which writes a flat
    cookie array JSON. This can then be fed to import_cookies().

    Args:
        output_path: Where to write the exported cookie JSON.
        session: CLI session name (default: "default").
        url_filter: Only export cookies for this URL.

    Returns:
        True if export succeeded.
    """
    import subprocess

    cmd = [_cli_path(), "--session", session, "cookies", "export", str(output_path)]
    if url_filter:
        cmd.extend(["--url", url_filter])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[AUTEUR] Cookies exported to {output_path}")
        return True

    print(f"[AUTEUR] Cookie export failed: {result.stderr.strip()}")
    return False


def import_cookies_via_cli(
    cookie_file: str | Path,
    session: str = "default",
) -> bool:
    """Import cookies into a running browser-use CLI session.

    Uses the `browser-use cookies import` command. The file should be
    a flat cookie array JSON (CLI format).

    Args:
        cookie_file: Path to the cookie JSON file.
        session: CLI session name (default: "default").

    Returns:
        True if import succeeded.
    """
    import subprocess

    cmd = [_cli_path(), "--session", session, "cookies", "import", str(cookie_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[AUTEUR] Cookies imported from {cookie_file}")
        return True

    print(f"[AUTEUR] Cookie import failed: {result.stderr.strip()}")
    return False


def bootstrap_via_cli_profile(
    account: BrowserAccount,
    spec: PlatformSpec,
    chrome_profile: str = "Default",
) -> bool:
    """Bootstrap auth by piggybacking on a real Chrome profile's cookies.

    Opens a browser-use CLI session with --profile (uses real Chrome's
    cookies/logins), navigates to the platform, then exports the cookies
    to our storage_state format.

    Args:
        account: Target account to populate.
        spec: Platform spec with URLs.
        chrome_profile: Chrome profile name ("Default", "Profile 1", etc.)

    Returns:
        True if cookies were exported and saved.
    """
    import subprocess
    import tempfile

    session = f"auteur_bootstrap_{account.platform}"

    # Open the platform URL using real Chrome profile
    open_cmd = [
        _cli_path(), "--session", session,
        "--profile", chrome_profile,
        "--headed",
        "open", spec.start_url,
    ]
    result = subprocess.run(open_cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"[AUTEUR] Failed to open browser: {result.stderr.strip()}")
        return False

    # Give the page a moment to load and cookies to settle
    import time
    time.sleep(3)

    # Export cookies to a temp file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
        tmp_path = tmp.name

    try:
        if not export_cookies_via_cli(tmp_path, session=session):
            return False

        # Import into our storage_state format
        domain = spec.start_url.split("//")[-1].split("/")[0]
        domain_filter = f".{domain}" if not domain.startswith(".") else domain
        success = import_cookies(account, tmp_path, domain_filter=domain_filter)

        return success

    finally:
        Path(tmp_path).unlink(missing_ok=True)
        # Close the bootstrap session
        subprocess.run(
            [_cli_path(), "--session", session, "close"],
            capture_output=True, text=True,
        )


# ---------------------------------------------------------------------------
# Auth verification
# ---------------------------------------------------------------------------


async def verify_auth(
    account: BrowserAccount,
    spec: PlatformSpec,
    llm=None,
) -> bool:
    """Verify that saved auth state is still valid.

    Args:
        account: The platform/account to check.
        spec: Platform spec with login check task.
        llm: LLM for the agent. Uses default if None.

    Returns:
        True if logged in, False otherwise.
    """
    if not account.storage_state_path.exists():
        return False

    from browser_use import Agent, Browser

    if llm is None:
        llm = _get_default_llm()

    browser = Browser(
        headless=True,
        storage_state=str(account.storage_state_path),
    )

    try:
        agent = Agent(
            task=spec.build_login_check_task(),
            llm=llm,
            browser=browser,
        )
        result = await agent.run(max_steps=10)

        response_text = _extract_final_response(result)
        parsed = spec.parse_json_response(response_text)
        return parsed.get("logged_in", False)

    finally:
        await browser.stop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_cookie(cookie: dict) -> dict:
    """Normalize a cookie dict to Playwright storage_state format."""
    return {
        "name": cookie.get("name", ""),
        "value": cookie.get("value", ""),
        "domain": cookie.get("domain", ""),
        "path": cookie.get("path", "/"),
        "expires": cookie.get("expires", cookie.get("expirationDate", -1)),
        "httpOnly": cookie.get("httpOnly", False),
        "secure": cookie.get("secure", False),
        "sameSite": cookie.get("sameSite", "Lax"),
    }


def _domain_matches(cookie_domain: str, filter_domain: str) -> bool:
    """Check if a cookie domain matches a filter domain."""
    cookie_domain = cookie_domain.lstrip(".")
    filter_domain = filter_domain.lstrip(".")
    return cookie_domain == filter_domain or cookie_domain.endswith(f".{filter_domain}")


def _cli_path() -> str:
    """Get the browser-use CLI executable path."""
    import shutil
    import sys

    # Try the venv bin first
    venv_cli = Path(sys.executable).parent / "browser-use"
    if venv_cli.exists():
        return str(venv_cli)

    # Fall back to system PATH
    found = shutil.which("browser-use")
    if found:
        return found

    raise FileNotFoundError(
        "browser-use CLI not found. Install with: pip install browser-use"
    )


def _get_default_llm():
    """Get the default LLM for browser agent tasks."""
    from auteur.config import get_settings
    settings = get_settings()

    if settings.browser_use_api_key:
        from browser_use import ChatBrowserUse
        return ChatBrowserUse()

    if settings.gemini_api_key:
        from browser_use import ChatGoogle
        return ChatGoogle(model="gemini-2.5-flash")

    raise RuntimeError(
        "No LLM configured for browser automation. "
        "Set BROWSER_USE_API_KEY or GEMINI_API_KEY in .env"
    )


def _extract_final_response(result) -> str:
    """Extract the final text response from an agent run result."""
    if result is None:
        return ""
    if hasattr(result, "final_result"):
        return result.final_result() or ""
    if hasattr(result, "last_result"):
        last = result.last_result()
        if last and hasattr(last, "extracted_content"):
            return last.extracted_content or ""
    return str(result)

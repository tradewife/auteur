"""Browser runner — executes generation tasks through browser-use Agent.

Uses short agent phases (submit → poll → collect) instead of one
long-lived agent session, because keeping an LLM in the loop during
a 5-15 minute render is expensive and brittle.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auteur.browser_ops.auth import BrowserAccount
    from auteur.browser_ops.platforms.base import PlatformSpec
    from auteur.providers.base import GenerationRequest, GenerationResult


async def run_browser_generation(
    request: GenerationRequest,
    spec: PlatformSpec,
    account: BrowserAccount,
    llm=None,
    artifact_dir: Path | None = None,
) -> GenerationResult:
    """Execute a generation task through a browser-automated platform.

    Pipeline:
    1. Open browser with saved storage_state
    2. Run submit agent task
    3. Poll with short status-check agent tasks
    4. Run collect agent task
    5. Return GenerationResult

    Args:
        request: The generation request with optimized prompt.
        spec: Platform spec defining agent task prompts.
        account: Platform account with storage_state path.
        llm: LLM for the agent. Uses default if None.
        artifact_dir: Directory to save run artifacts.

    Returns:
        GenerationResult with output URLs and metadata.
    """
    from browser_use import Agent, Browser

    from auteur.browser_ops.auth import _extract_final_response, _get_default_llm
    from auteur.providers.base import GenerationResult

    if llm is None:
        llm = _get_default_llm()

    if not account.storage_state_path.exists():
        return GenerationResult(
            success=False,
            provider="browser_use",
            model=spec.model_id,
            error=(
                f"No auth state for {account.label}. "
                "Run bootstrap_auth() first."
            ),
        )

    # Set up artifact directory
    if artifact_dir is None:
        from auteur.config import get_settings
        artifact_dir = get_settings().browser_artifact_dir / spec.platform
    artifact_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"{spec.platform}_{int(time.time())}"
    run_dir = artifact_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    browser = Browser(
        headless=True,
        storage_state=str(account.storage_state_path),
    )

    try:
        # Phase 1: Submit
        submit_task = spec.build_submit_task(request)
        agent = Agent(
            task=submit_task,
            llm=llm,
            browser=browser,
        )
        submit_result = await agent.run(max_steps=30)
        submit_text = _extract_final_response(submit_result)
        submit_parsed = spec.parse_json_response(submit_text)

        _save_artifact(run_dir / "submit.json", {
            "task": submit_task,
            "response": submit_text,
            "parsed": submit_parsed,
        })

        if submit_parsed.get("status") == "failed":
            return GenerationResult(
                success=False,
                provider="browser_use",
                model=spec.model_id,
                error=f"Submit failed: {submit_parsed.get('notes', submit_text)}",
                metadata={"run_id": run_id, "phase": "submit"},
            )

        # Phase 2: Poll for completion
        deadline = time.monotonic() + spec.timeout_s
        poll_count = 0
        last_status = "pending"

        while time.monotonic() < deadline:
            await asyncio.sleep(spec.poll_interval_s)
            poll_count += 1

            status_agent = Agent(
                task=spec.build_status_task(),
                llm=llm,
                browser=browser,
            )
            status_result = await status_agent.run(max_steps=10)
            status_text = _extract_final_response(status_result)
            status_parsed = spec.parse_json_response(status_text)
            last_status = status_parsed.get("status", "pending")

            _save_artifact(run_dir / f"poll_{poll_count:03d}.json", {
                "response": status_text,
                "parsed": status_parsed,
            })

            if last_status == "completed":
                break
            if last_status == "failed":
                return GenerationResult(
                    success=False,
                    provider="browser_use",
                    model=spec.model_id,
                    error=f"Generation failed: {status_parsed.get('notes', status_text)}",
                    metadata={"run_id": run_id, "phase": "poll", "polls": poll_count},
                )

        if last_status != "completed":
            return GenerationResult(
                success=False,
                provider="browser_use",
                model=spec.model_id,
                error=f"Timed out after {spec.timeout_s}s ({poll_count} polls)",
                metadata={"run_id": run_id, "phase": "timeout"},
            )

        # Phase 3: Collect outputs
        collect_agent = Agent(
            task=spec.build_collect_task(),
            llm=llm,
            browser=browser,
        )
        collect_result = await collect_agent.run(max_steps=15)
        collect_text = _extract_final_response(collect_result)
        collect_parsed = spec.parse_json_response(collect_text)

        _save_artifact(run_dir / "collect.json", {
            "response": collect_text,
            "parsed": collect_parsed,
        })

        # Extract results
        asset_urls = collect_parsed.get("asset_urls", [])
        page_url = collect_parsed.get("page_url", "")
        primary_url = asset_urls[0] if asset_urls else page_url

        return GenerationResult(
            success=bool(primary_url),
            provider="browser_use",
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
                "notes": collect_parsed.get("notes", ""),
            },
        )

    except Exception as e:
        return GenerationResult(
            success=False,
            provider="browser_use",
            model=spec.model_id,
            error=f"Browser runner error: {e!s}",
            metadata={"run_id": run_id},
        )

    finally:
        # Re-export storage state to capture any session updates
        try:
            await browser.export_storage_state(str(account.storage_state_path))
        except Exception:
            pass
        await browser.stop()


def _save_artifact(path: Path, data: dict) -> None:
    """Save a JSON artifact from a run phase."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

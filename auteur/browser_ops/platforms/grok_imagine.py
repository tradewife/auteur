"""Grok Imagine platform spec — task prompts for x.com/i/grok image/video generation."""

from __future__ import annotations

from auteur.browser_ops.platforms.base import PlatformSpec
from auteur.providers.base import GenerationRequest


class GrokImagineSpec(PlatformSpec):
    model_id = "grok-imagine-web"
    platform = "grok_imagine"
    start_url = "https://x.com/i/grok"
    login_url = "https://x.com/i/flow/login"
    timeout_s = 900
    poll_interval_s = 15

    def build_submit_task(self, request: GenerationRequest) -> str:
        prompt = request.prompt.positive
        params = request.prompt.parameters

        task_parts = [
            f"Go to {self.start_url}.",
            "If there is a 'New chat' or 'New conversation' button, click it to start fresh.",
            "Find the text input area (textarea or contenteditable field).",
            f'Type the following prompt exactly: "{prompt}"',
            "Submit the prompt by clicking the send/submit button or pressing Enter.",
            "Wait for the generation to start — you should see a loading indicator or the AI responding.",
        ]

        aspect = params.get("aspect_ratio", "")
        if aspect:
            task_parts.insert(3, f"If there are aspect ratio options, select {aspect}.")

        task_parts.append(
            "Once you have submitted the prompt and see the AI is processing, "
            "respond with EXACTLY this JSON and nothing else: "
            '{"status": "submitted", "notes": "<any relevant observation>"}'
        )

        return " ".join(task_parts)

    def build_status_task(self) -> str:
        return (
            "Look at the current page. Check if the AI generation is still in progress "
            "or if it has completed. Look for: "
            "- Loading spinners, progress indicators, or 'Generating' text → still in progress "
            "- Generated images or videos visible on the page → completed "
            "- Error messages → failed "
            "Respond with EXACTLY this JSON and nothing else: "
            '{"status": "completed|pending|failed", "notes": "<what you see>"}'
        )

    def build_collect_task(self) -> str:
        return (
            "The generation is complete. Collect the output: "
            "1. Look for any generated images or videos on the page. "
            "2. For images: right-click or find the image URL (src attribute). "
            "3. For videos: find the video source URL. "
            "4. Also note the current page URL. "
            "5. If there are download buttons, note their presence. "
            "Respond with EXACTLY this JSON and nothing else: "
            '{"status": "completed", "asset_urls": ["<url1>", "<url2>"], '
            '"page_url": "<current page url>", "notes": "<description of outputs>"}'
        )

    def build_login_check_task(self) -> str:
        return (
            f"Go to {self.start_url}. "
            "Check if you are logged in to X/Twitter. Signs of being logged in: "
            "- You can see a text input to chat with Grok "
            "- You see your profile avatar or account switcher "
            "- You do NOT see a 'Sign in' or 'Log in' button/prompt "
            "Respond with EXACTLY this JSON and nothing else: "
            '{"logged_in": true} or {"logged_in": false}'
        )

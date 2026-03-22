"""Platform specs for browser-based generation."""

from auteur.browser_ops.platforms.base import PlatformSpec
from auteur.browser_ops.platforms.grok_imagine import GrokImagineSpec

PLATFORM_SPECS: dict[str, PlatformSpec] = {
    "grok-imagine-web": GrokImagineSpec(),
}

"""Platform specs for browser-based generation.

Note: grok-imagine-web is legacy for Hermes + direct xAI OAuth image/video.
Hermes now handles xAI gen natively; AUTEUR uses this only if explicitly requested.
"""

from auteur.browser_ops.platforms.base import PlatformSpec
from auteur.browser_ops.platforms.grok_imagine import GrokImagineSpec

PLATFORM_SPECS: dict[str, PlatformSpec] = {
    "grok-imagine-web": GrokImagineSpec(),
}

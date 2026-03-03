"""Style system — auteur profiles + freeform aesthetic styles with enrichment."""

from auteur.knowledge.styles.base import StyleProfile
from auteur.knowledge.styles.deakins import DEAKINS
from auteur.knowledge.styles.hoytema import HOYTEMA
from auteur.knowledge.styles.lubezki import LUBEZKI
from auteur.knowledge.styles.storaro import STORARO
from auteur.knowledge.styles.aesthetic import AestheticStyle, AuteurLayer

STYLE_PROFILES: dict[str, StyleProfile] = {
    "deakins": DEAKINS,
    "storaro": STORARO,
    "lubezki": LUBEZKI,
    "hoytema": HOYTEMA,
}

__all__ = [
    "STYLE_PROFILES", "StyleProfile",
    "AestheticStyle", "AuteurLayer",
]

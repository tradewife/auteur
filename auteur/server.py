"""AUTEUR MCP Server — cinematography intelligence for any LLM.

Exposes AUTEUR's knowledge system, prompt engine, and generation pipeline
as MCP primitives (Resources, Tools, Prompts) so any MCP-compatible client
(Claude, Cursor, GPT, custom agents) can use AUTEUR as a conversational
co-director.

Run:
    fastmcp run auteur/server.py:mcp
    auteur serve --transport stdio
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

# Knowledge system
from auteur.knowledge.styles import STYLE_PROFILES, AestheticStyle, AuteurLayer
from auteur.knowledge.lens import FOCAL_LENGTHS, LENS_FAMILIES
from auteur.knowledge.lighting import LIGHTING_SETUPS, COLOR_TEMPERATURES
from auteur.knowledge.color import COLOR_PALETTES, GRADING_PROFILES, EMOTIONAL_COLOR_MAP
from auteur.knowledge.composition import COMPOSITION_RULES, ASPECT_RATIOS
from auteur.knowledge.movement import CAMERA_MOVEMENTS
from auteur.knowledge.film_stock import FILM_STOCKS, DIGITAL_SENSORS
from auteur.knowledge.camera import SENSOR_FORMATS, FRAME_RATES

# Prompt system
from auteur.prompt.composer import PromptComposer
from auteur.prompt.templates import SHOT_TEMPLATES, list_templates
from auteur.prompt.negative import NegativePromptLibrary

# Agents
from auteur.agents.cinematographer import CinematographerAgent
from auteur.agents.director import DirectorAgent, PACING_TEMPLATES

# Project state
from auteur.knowledge.project import (
    Project, Brief, VisualLanguage, Scene, Beat, ProjectStatus,
)

# ---------------------------------------------------------------------------
# Server init
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="AUTEUR",
    instructions=(
        "You are AUTEUR, a cinematography-expert AI co-director. "
        "You have deep knowledge of lens psychology, lighting design, color theory, "
        "composition, camera movement, film stocks, and the signature styles of "
        "master DPs (Deakins, Storaro, Lubezki, van Hoytema). "
        "Use the available resources to ground your decisions in real cinematographic "
        "knowledge, and use tools to plan shots, compose prompts, and generate content. "
        "Always think like a DP: every technical choice serves the story."
    ),
)

# In-memory project store (session-scoped)
_projects: dict[str, Project] = {}


# ===========================================================================
# RESOURCES — Read-only access to the cinematography knowledge base
# ===========================================================================

@mcp.resource("auteur://styles")
def list_styles() -> str:
    """List all available DP style profiles with brief descriptions."""
    result = {}
    for key, profile in STYLE_PROFILES.items():
        result[key] = {
            "name": profile.name,
            "philosophy": profile.philosophy[:150] + "...",
            "notable_films": profile.notable_films[:4],
        }
    return json.dumps(result, indent=2)


@mcp.resource("auteur://styles/{name}")
def get_style(name: str) -> str:
    """Get a full DP style profile with lighting, color, movement philosophy."""
    profile = STYLE_PROFILES.get(name)
    if not profile:
        return json.dumps({"error": f"Unknown style: {name}. Available: {list(STYLE_PROFILES.keys())}"})
    return json.dumps(profile.model_dump(), indent=2)


@mcp.resource("auteur://lenses")
def list_lenses() -> str:
    """Focal length library — psychology and character of each focal length."""
    return json.dumps(FOCAL_LENGTHS, indent=2)


@mcp.resource("auteur://lens-families")
def list_lens_families() -> str:
    """Named lens families (Cooke, Zeiss, Panavision, etc.) with character notes."""
    return json.dumps(LENS_FAMILIES, indent=2)


@mcp.resource("auteur://lighting")
def list_lighting() -> str:
    """Named lighting setups — Rembrandt, butterfly, noir, golden hour, etc."""
    return json.dumps(LIGHTING_SETUPS, indent=2)


@mcp.resource("auteur://palettes")
def list_palettes() -> str:
    """Color palettes, grading profiles, and emotional color mapping."""
    return json.dumps({
        "palettes": COLOR_PALETTES,
        "grading_profiles": GRADING_PROFILES,
        "emotional_color_map": EMOTIONAL_COLOR_MAP,
    }, indent=2)


@mcp.resource("auteur://movements")
def list_movements() -> str:
    """Camera movement types with philosophy and narrative purpose."""
    return json.dumps(CAMERA_MOVEMENTS, indent=2)


@mcp.resource("auteur://stocks")
def list_stocks() -> str:
    """Film stocks (Kodak, Fuji, CineStill) and digital sensors (ARRI, RED, Sony)."""
    return json.dumps({
        "film_stocks": FILM_STOCKS,
        "digital_sensors": DIGITAL_SENSORS,
    }, indent=2)


@mcp.resource("auteur://templates")
def list_shot_templates() -> str:
    """Shot templates — reusable scaffolds for common cinematographic situations."""
    result = {}
    for key, tmpl in SHOT_TEMPLATES.items():
        result[key] = {
            "category": tmpl.category,
            "description": tmpl.description,
            "recommended_style": tmpl.recommended_style,
        }
    return json.dumps(result, indent=2)


@mcp.resource("auteur://camera")
def list_camera_systems() -> str:
    """Camera sensor formats, frame rates, and their visual signatures."""
    return json.dumps({
        "sensor_formats": SENSOR_FORMATS,
        "frame_rates": FRAME_RATES,
        "aspect_ratios": ASPECT_RATIOS,
    }, indent=2)


# ===========================================================================
# TOOLS — Actions the LLM can execute
# ===========================================================================

@mcp.tool
def analyse_brief(
    logline: str,
    description: str = "",
    mood: str = "",
    duration_seconds: int = 30,
    references: list[str] | None = None,
    constraints: list[str] | None = None,
) -> dict:
    """Parse a creative brief into a structured project. Call this first.

    Takes the user's creative intent and creates a new AUTEUR project
    with a structured Brief. Returns the project ID and brief summary.
    """
    brief = Brief(
        logline=logline,
        description=description,
        mood=mood,
        duration_seconds=duration_seconds,
        references=references or [],
        constraints=constraints or [],
    )
    project = Project(brief=brief, status=ProjectStatus.BRIEF)
    _projects[project.id] = project

    return {
        "project_id": project.id,
        "status": "brief_captured",
        "brief": brief.model_dump(),
        "next_step": "Call propose_visual_language to establish the look and feel.",
    }


@mcp.tool
def propose_visual_language(
    project_id: str,
    style_description: str = "",
    style_mood: str = "",
    style_references: list[str] | None = None,
    style_profile: str = "",
    aspect_ratio: str = "2.39:1",
    color_palette: str = "",
    grading_profile: str = "",
    film_stock: str = "",
    movement_philosophy: str = "",
    lighting_approach: str = "",
    auteur_weight: float = 0.7,
) -> dict:
    """Propose and lock the global visual language for a project.

    The PRIMARY interface is style_description — just describe the look
    the user wants in natural language. AUTEUR will automatically enrich
    it with cinematographic depth from master DP techniques.

    style_profile is the LEGACY interface for power users who want to
    reference a specific DP directly (deakins, storaro, lubezki, hoytema).

    auteur_weight (0.0-1.0) controls how much auteur enrichment to apply.
    """
    project = _projects.get(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}

    # Auteur enrichment from freeform description
    auteur_blend = {}
    enrichment_explanation = ""
    if style_description or style_mood:
        aesthetic = AestheticStyle(
            description=style_description,
            mood=style_mood or project.brief.mood,
            lighting_feel=lighting_approach,
            color_feel=color_palette,
            movement_feel=movement_philosophy,
            references=style_references or [],
        )
        aesthetic = AuteurLayer.enrich(aesthetic, auteur_weight=auteur_weight)
        auteur_blend = aesthetic.auteur_blend
        enrichment_explanation = AuteurLayer.explain_blend(aesthetic)

        # Auto-fill from enrichment if user didn't provide explicit values
        if not lighting_approach and aesthetic.enriched_lighting:
            lighting_approach = aesthetic.enriched_lighting
        if not movement_philosophy and aesthetic.enriched_movement:
            movement_philosophy = ", ".join(aesthetic.enriched_movement[:3])

    # Legacy: explicit DP profile
    elif style_profile and style_profile in STYLE_PROFILES:
        dp = STYLE_PROFILES[style_profile]
        if not lighting_approach:
            lighting_approach = dp.lighting_approach[:100]
        if not color_palette:
            color_palette = dp.color_palette[:100]

    project.visual_language = VisualLanguage(
        style_profile=style_profile,
        style_description=style_description,
        style_mood=style_mood,
        style_references=style_references or [],
        auteur_blend=auteur_blend,
        aspect_ratio=aspect_ratio,
        color_palette=color_palette,
        grading_profile=grading_profile,
        film_stock=film_stock,
        movement_philosophy=movement_philosophy,
        lighting_approach=lighting_approach,
    )
    project.status = ProjectStatus.PLANNING

    result = {
        "project_id": project_id,
        "status": "visual_language_locked",
        "visual_language": project.visual_language.model_dump(),
        "next_step": "Call plan_shots to design your shot list.",
    }
    if auteur_blend:
        result["auteur_enrichment"] = enrichment_explanation
    return result


@mcp.tool
def plan_shots(
    project_id: str,
    scene_description: str,
    pacing: str = "establishing_to_intimate",
    mood: str = "",
    num_shots: int | None = None,
) -> dict:
    """Plan a shot list for a scene using the DirectorAgent.

    Uses the project's visual language and the selected pacing template.
    Available pacing templates: establishing_to_intimate, tension_build,
    action_sequence, dialogue_scene, reveal.
    """
    project = _projects.get(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}

    style = project.visual_language.style_profile
    effective_mood = mood or project.brief.mood
    model = project.target_model

    director = DirectorAgent(style=style)
    sequence_spec = director.plan_sequence(
        scene_description,
        pacing=pacing,
        style=style,
        mood=effective_mood,
        model=model,
    )

    # Register as a scene in the project
    scene = Scene(
        name=scene_description[:50],
        description=scene_description,
        shots=sequence_spec.shots,
    )
    project.scenes.append(scene)
    project.status = ProjectStatus.SHOT_DESIGN

    # Build readable shot list
    shot_summaries = []
    for i, shot in enumerate(scene.shots):
        shot_summaries.append({
            "index": i,
            "description": shot.description[:100],
            "shot_size": shot.composition.shot_size.value,
            "movement": shot.movement.movement_type.value,
            "lens": f"{shot.lens.focal_length_mm}mm",
        })

    return {
        "project_id": project_id,
        "scene_id": scene.id,
        "pacing": pacing,
        "shots": shot_summaries,
        "total_shots": len(scene.shots),
        "next_step": "Review shots. Call refine_shot to adjust, or compose_prompt to see the prompt.",
    }


@mcp.tool
def compose_prompt(
    project_id: str,
    scene_index: int = 0,
    shot_index: int = 0,
    model: str = "",
) -> dict:
    """Compose the full generation prompt for a specific shot.

    Returns the layered prompt breakdown showing how each cinematographic
    dimension contributes to the final prompt.
    """
    project = _projects.get(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}

    if scene_index >= len(project.scenes):
        return {"error": f"Scene {scene_index} not found (have {len(project.scenes)} scenes)"}

    scene = project.scenes[scene_index]
    if shot_index >= len(scene.shots):
        return {"error": f"Shot {shot_index} not found (have {len(scene.shots)} shots)"}

    shot = scene.shots[shot_index]
    composed = PromptComposer.compose(shot)

    target = model or project.target_model
    optimized = composed.optimize(model=target)

    return {
        "positive_prompt": optimized.positive,
        "negative_prompt": optimized.negative,
        "model": optimized.model,
        "parameters": optimized.parameters,
        "layers": composed.prompt_layers,
        "style_keywords": composed.style_keywords,
    }


@mcp.tool
def refine_shot(
    project_id: str,
    scene_index: int = 0,
    shot_index: int = 0,
    description: str | None = None,
    shot_size: str | None = None,
    movement: str | None = None,
    lighting: str | None = None,
    mood: str | None = None,
    focal_length_mm: int | None = None,
) -> dict:
    """Refine a specific shot based on user feedback.

    Only provided fields are updated — everything else stays the same.
    Call compose_prompt after refining to see the updated prompt.
    """
    project = _projects.get(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}

    if scene_index >= len(project.scenes):
        return {"error": f"Scene {scene_index} not found"}
    scene = project.scenes[scene_index]
    if shot_index >= len(scene.shots):
        return {"error": f"Shot {shot_index} not found"}

    shot = scene.shots[shot_index]

    # Apply refinements
    if description is not None:
        shot.description = description
    if mood is not None:
        shot.emotional_intent = mood
    if shot_size is not None:
        from auteur.knowledge.ontology import ShotSize
        shot.composition.shot_size = ShotSize(shot_size)
    if movement is not None:
        from auteur.knowledge.ontology import MovementType
        try:
            shot.movement.movement_type = MovementType(movement)
        except ValueError:
            return {"error": f"Unknown movement: {movement}. Check auteur://movements."}
    if lighting is not None:
        shot.lighting.name = lighting
    if focal_length_mm is not None:
        shot.lens.focal_length_mm = focal_length_mm

    return {
        "status": "shot_updated",
        "shot": {
            "description": shot.description[:100],
            "shot_size": shot.composition.shot_size.value,
            "movement": shot.movement.movement_type.value,
            "lens": f"{shot.lens.focal_length_mm}mm",
            "lighting": shot.lighting.name,
        },
        "next_step": "Call compose_prompt to see the updated prompt.",
    }


@mcp.tool
def define_style(
    description: str,
    mood: str = "",
    lighting_feel: str = "",
    color_feel: str = "",
    movement_feel: str = "",
    texture_feel: str = "",
    references: list[str] | None = None,
    auteur_weight: float = 0.7,
) -> dict:
    """Define a visual style from a freeform description. No presets needed.

    Just describe the look you want — AUTEUR will automatically enrich it
    with cinematographic depth from master DP techniques. The auteur enrichment
    is invisible; it deepens the style with real film knowledge.

    Returns the enriched style with auteur blend weights, keywords, and an
    explanation of which techniques were matched and why.

    Use this for standalone style exploration. For project workflows, use
    propose_visual_language instead.
    """
    aesthetic = AestheticStyle(
        description=description,
        mood=mood,
        lighting_feel=lighting_feel,
        color_feel=color_feel,
        movement_feel=movement_feel,
        texture_feel=texture_feel,
        references=references or [],
    )
    enriched = AuteurLayer.enrich(aesthetic, auteur_weight=auteur_weight)

    return {
        "style": enriched.model_dump(),
        "auteur_blend": enriched.auteur_blend,
        "dominant_auteur": enriched.dominant_auteur,
        "enriched_keywords": enriched.enriched_keywords,
        "enriched_negative": enriched.enriched_negative,
        "enriched_lighting": enriched.enriched_lighting,
        "enriched_movement": enriched.enriched_movement,
        "explanation": AuteurLayer.explain_blend(enriched),
    }


@mcp.tool
def quick_compose(
    description: str,
    style: str = "",
    style_description: str = "",
    shot_size: str = "medium",
    lighting: str = "",
    mood: str = "",
    model: str = "flux-pro",
) -> dict:
    """Quick one-shot prompt composition — no project needed.

    For when you just want a prompt fast without the full planning workflow.
    Use style for a DP profile name (deakins, lubezki, etc.) or
    style_description for freeform text (the preferred way).
    Returns an optimized prompt ready for generation.
    """
    from auteur.knowledge.ontology import ShotSpec, LightSetup, CompositionSpec, ShotSize

    # Build aesthetic style from freeform description
    aesthetic_data = None
    if style_description:
        aesthetic = AestheticStyle(
            description=style_description,
            mood=mood,
            lighting_feel=lighting,
        )
        aesthetic = AuteurLayer.enrich(aesthetic)
        aesthetic_data = aesthetic.model_dump()

    spec = ShotSpec(
        description=description,
        emotional_intent=mood,
        style_profile=style if not style_description else "",
        aesthetic_style=aesthetic_data,
        composition=CompositionSpec(
            shot_size=ShotSize(shot_size) if shot_size else ShotSize.MEDIUM,
        ),
        lighting=LightSetup(name=lighting) if lighting else LightSetup(),
        target_model=model,
    )

    composed = PromptComposer.compose(spec)
    optimized = composed.optimize(model=model)

    result = {
        "positive_prompt": optimized.positive,
        "negative_prompt": optimized.negative,
        "model": optimized.model,
        "parameters": optimized.parameters,
    }
    if aesthetic_data:
        result["auteur_blend"] = aesthetic.auteur_blend
    return result


@mcp.tool
def provider_status() -> dict:
    """Show which generation providers are configured and available."""
    from auteur.providers.registry import ProviderRegistry
    registry = ProviderRegistry()
    return registry.status()


@mcp.tool
def list_pacing_templates() -> dict:
    """List available pacing templates for shot planning."""
    result = {}
    for name, beats in PACING_TEMPLATES.items():
        result[name] = [
            {"shot_size": b.get("shot_size", "medium"), "movement": b.get("movement", "static"),
             "description": b.get("description_suffix", "")}
            for b in beats
        ]
    return result


@mcp.tool
def get_project(project_id: str) -> dict:
    """Get the current state of a project."""
    project = _projects.get(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    return project.summary()


# ===========================================================================
# PROMPTS — Reusable templates that guide the LLM's approach
# ===========================================================================

@mcp.prompt
def establishing_shot(location: str, time_of_day: str = "golden hour", mood: str = "contemplative") -> str:
    """Guide the LLM to plan a cinematic establishing shot."""
    return (
        f"Plan an establishing shot for: {location}\n"
        f"Time: {time_of_day}\n"
        f"Mood: {mood}\n\n"
        "Use AUTEUR tools to:\n"
        "1. Read auteur://styles to choose a DP style\n"
        "2. Read auteur://lighting for the right setup\n"
        "3. Call quick_compose with a wide shot, the chosen style, and appropriate lighting\n\n"
        "Think about: What does this location feel like? What should the audience "
        "understand about the world from this first frame?"
    )


@mcp.prompt
def character_portrait(character_description: str, emotion: str = "neutral") -> str:
    """Guide the LLM to design a character-defining close-up."""
    return (
        f"Design a defining close-up portrait for: {character_description}\n"
        f"Emotion: {emotion}\n\n"
        "Use AUTEUR tools to:\n"
        "1. Read auteur://lenses — choose a portrait lens (85mm-135mm range)\n"
        "2. Read auteur://lighting — Rembrandt or butterfly for faces\n"
        "3. Call quick_compose with close_up shot size and chosen settings\n\n"
        "Think about: What does this face tell us? What's behind the eyes?"
    )


@mcp.prompt
def plan_mood_film(brief: str, duration_seconds: int = 30) -> str:
    """Guide the LLM through the full AUTEUR planning workflow."""
    return (
        f"Let's plan a {duration_seconds}-second mood film.\n"
        f"Brief: {brief}\n\n"
        "Follow this workflow:\n"
        "1. Call analyse_brief to create a project\n"
        "2. Call propose_visual_language with a style_description that captures\n"
        "   the mood and feel the user wants — AUTEUR will automatically\n"
        "   enrich it with master DP techniques (no preset needed)\n"
        "3. Call plan_shots with an appropriate pacing template\n"
        "4. Review each shot — call refine_shot if anything needs adjustment\n"
        "5. Call compose_prompt for each shot to see the final prompts\n\n"
        "At each step, explain your creative reasoning. "
        "Every technical choice should serve the story."
    )


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    mcp.run()

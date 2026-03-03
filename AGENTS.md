# AUTEUR — Agent Handover Document

## Project Summary
AUTEUR is a cinematography intelligence system for AI generation agents. It encodes deep filmmaking knowledge into composable Pydantic models and exposes everything via an MCP server. ~8000 lines of Python across 42 files.

**Repo:** `/home/kt/cineforge` (local) / `https://github.com/tradewife/auteur.git` (remote)
**Branch:** `master`
**Python:** 3.12, venv at `.venv/` — always use `.venv/bin/python3` or activate first
**Package:** `auteur/` (was `cineforge/` — renamed in this session)

## What's Built (all working, validated)

### 1. Knowledge System (`auteur/knowledge/`)
Deep cinematography ontology as Pydantic models:
- `ontology.py` — Core models: `ShotSpec` (the master model), `LensSpec`, `LightSetup`, `ColorPalette`, `CompositionSpec`, `MovementSpec`, `FilmStockProfile`. Enums for `ShotSize`, `ShotAngle`, `LightQuality`, `MovementType`, `BokehCharacter`, `GrainStructure`, `ColorHarmony`, `SensorFormat`, `AspectRatio`.
- `lens.py` — `FOCAL_LENGTHS` dict (psychology per focal length), `LENS_FAMILIES` (Cooke, Zeiss, Panavision, etc.)
- `lighting.py` — `LIGHTING_SETUPS` (Rembrandt, butterfly, noir, etc.), `COLOR_TEMPERATURES`
- `color.py` — `COLOR_PALETTES`, `GRADING_PROFILES`, `EMOTIONAL_COLOR_MAP`
- `composition.py` — `COMPOSITION_RULES`, `ASPECT_RATIOS`
- `movement.py` — `CAMERA_MOVEMENTS` with philosophy
- `film_stock.py` — `FILM_STOCKS` (Kodak, Fuji, CineStill), `DIGITAL_SENSORS` (ARRI, RED, Sony)
- `camera.py` — `SENSOR_FORMATS`, `FRAME_RATES`
- `project.py` — `Project`, `Brief`, `VisualLanguage`, `Scene`, `Beat`, `ProjectStatus`

### 2. Style Profiles (`auteur/knowledge/styles/`)
- `base.py` — `StyleProfile` model, `STYLE_PROFILES` dict
- `deakins.py`, `storaro.py`, `lubezki.py`, `hoytema.py` — Four complete DP profiles
- `aesthetic.py` — `AestheticStyle` (freeform user-defined style) + `AuteurLayer` (the enrichment engine)
- `__init__.py` — Exports `STYLE_PROFILES`, `AestheticStyle`, `AuteurLayer`

### 3. Auteur Layer (`auteur/knowledge/styles/aesthetic.py`)
The signature feature. Users describe a style in freeform text. `AuteurLayer.enrich()` analyzes it across 5 dimensions (mood, lighting, color, movement, texture) using keyword signal matching against 4 DP profiles, with dimension weights (mood=1.5, lighting=1.3, color=1.0, movement=0.8, texture=0.7). Produces:
- `auteur_blend` — Weighted dict like `{"deakins": 0.40, "storaro": 0.29, ...}`
- `enriched_keywords` — Prompt keywords from matched profiles, proportional to weight
- `enriched_negative` — Negative keywords
- `enriched_lighting`, `enriched_movement` — Synthesized from blend
- `auteur_weight` param (0.0-1.0, default 0.7) controls intensity
- `AuteurLayer.explain_blend()` gives human-readable reasoning

Example: "rainy Tokyo night, lonely and neon-lit" → Deakins 40% + Storaro 29%

### 4. Prompt Engine (`auteur/prompt/`)
- `composer.py` — `PromptComposer.compose(shot: ShotSpec) -> ComposedPrompt`. Layered assembly: subject → composition → lighting → camera → color → texture → movement → style → mood. Integrates `AuteurLayer` when `shot.aesthetic_style` is set.
- `optimizer.py` — `PromptOptimizer.optimize()`. Per-model boosters, filters, default params for 55+ models. `ComposedPrompt.optimize(model=...)` chains composer → optimizer.
- `negative.py` — `NegativePromptLibrary.for_shot()` with base negatives + style-specific negatives
- `templates.py` — `SHOT_TEMPLATES` dict, reusable shot scaffolds

### 5. Providers (`auteur/providers/`)
- `base.py` — `BaseProvider` ABC
- `fal.py` — `FalProvider`, 32 models. Kling 3.0/O3, Veo 3/3.1, Flux 2 Flex, Nano Banana 2/Pro, Grok Imagine, Sora 2 Pro, LTX-2 19B, Wan 2.6, Seedance 1.5, Cosmos 2.5, Recraft V4, Seedream, Hunyuan + i2v variants.
- `kie.py` — `KieProvider`, 15 models. Image + video gen. Kling 3.0, Runway Gen4 Turbo, Seedance 1.5 Pro, Wan 2.6, Nano Banana 2/Pro, GPT Image 1.5, Flux Kontext.
- `gemini.py` — `GeminiProvider`, 8 models. Imagen 4 Standard/Ultra/Fast, Nano Banana 2, Veo 3.
- `registry.py` — `ProviderRegistry` with 55+ model routing entries.

### 6. Pipeline (`auteur/pipeline/`)
- `shot.py` — `ShotPipeline` (compose → optimize → generate)
- `sequence.py` — `SequencePipeline` (multi-shot)
- `assets.py` — `AssetManager` (output tracking)

### 7. Agents (`auteur/agents/`)
- `cinematographer.py` — `CinematographerAgent`. Translates narrative intent → `ShotSpec`.
- `director.py` — `DirectorAgent`. Plans multi-shot sequences via `PACING_TEMPLATES` (establishing_to_intimate, tension_build, action_sequence, dialogue_scene, reveal).

### 8. MCP Server (`auteur/server.py`)
FastMCP 3.1.0. 10 tools, 9 resources, 3 prompts.

**Tools:**
- `analyse_brief` — Creates a project from creative intent
- `propose_visual_language` — Locks visual language with freeform style + auto auteur enrichment
- `plan_shots` — DirectorAgent shot list via pacing templates
- `compose_prompt` — Full layered prompt for a shot
- `refine_shot` — Adjust shot params
- `define_style` — Standalone freeform style exploration with auteur enrichment
- `quick_compose` — One-shot prompt composition, no project needed. Accepts `style_description` for freeform input.
- `provider_status` — Provider/key status
- `list_pacing_templates` — Available pacing templates
- `get_project` — Project state

**Resources:** `auteur://styles`, `auteur://styles/{name}`, `auteur://lenses`, `auteur://lens-families`, `auteur://lighting`, `auteur://palettes`, `auteur://movements`, `auteur://stocks`, `auteur://templates`, `auteur://camera`

**Prompts:** `establishing_shot`, `character_portrait`, `plan_mood_film`

### 9. CLI (`auteur/cli.py`)
Typer-based: `auteur version`, `auteur status`, `auteur shot`, `auteur explore`, `auteur serve`

### 10. Config (`auteur/config.py`)
Pydantic Settings from `.env`: `fal_key`, `kie_api_key`, `gemini_api_key`, `auteur_output_dir`

## Key Architecture Decisions
- `ShotSpec` is the atomic unit — everything flows through it
- `ShotSpec.aesthetic_style` is `dict | None` (serialized `AestheticStyle`) to avoid circular imports between ontology and styles
- The prompt composer checks `shot.aesthetic_style` first (auteur enrichment path), falls back to `shot.style_profile` (legacy DP name path)
- MCP resource URIs use `auteur://` prefix
- Projects are session-scoped in-memory (`_projects` dict in server.py)
- Provider implementations use httpx async, models are dispatched via `_MODEL_MAP` dicts in each provider

## Validation Commands
```bash
# Full import + tool listing
.venv/bin/python3 -c "
import asyncio
from auteur.server import mcp
async def check():
    tools = await mcp.list_tools()
    for t in sorted(tools, key=lambda x: x.name):
        print(t.name)
asyncio.run(check())
"

# Test auteur enrichment
.venv/bin/python3 -c "
from auteur.knowledge.styles.aesthetic import AestheticStyle, AuteurLayer
s = AestheticStyle(description='rainy Tokyo night', mood='isolated', color_feel='neon')
s = AuteurLayer.enrich(s)
print(s.auteur_blend)
print(AuteurLayer.explain_blend(s))
"

# Test full compose pipeline
.venv/bin/python3 -c "
from auteur.knowledge.styles.aesthetic import AestheticStyle, AuteurLayer
from auteur.prompt.composer import PromptComposer
from auteur.knowledge.ontology import ShotSpec
style = AestheticStyle(description='warm golden afternoon', mood='nostalgic')
style = AuteurLayer.enrich(style)
shot = ShotSpec(description='a child running through a wheat field', aesthetic_style=style.model_dump())
composed = PromptComposer.compose(shot)
opt = composed.optimize(model='veo3')
print(opt.positive[:200])
"
```

## What Could Come Next
- **Actual generation** — Wire `ShotPipeline`/`SequencePipeline` to real API calls (providers are structured but `generate()` methods need API keys + real HTTP calls)
- **More auteurs** — Add DP profiles (Bradford Young, Hoyte, Janusz Kaminski, Robert Richardson, etc.) to the signal matching
- **Image-to-video** — i2v workflow (generate still → animate) is stubbed in providers but not wired end-to-end
- **Reference image analysis** — Accept image inputs, extract style signals, match to auteur blend
- **Persistence** — Projects currently session-scoped; could add SQLite/JSON persistence
- **Tests** — No formal test suite yet; all validation was interactive
- **Audio design** — Some video models (Veo 3, Kling 3.0, Sora 2) support native audio; could add sound design knowledge

## Files NOT in git
- `perplexity-chat.md` — Research notes (in .gitignore)
- `.env` — API keys (in .gitignore)
- `.venv/` — Python virtual environment (in .gitignore)

# AUTEUR — Agent Handover & Protocol Document

## Project Summary
AUTEUR is a cinematography intelligence system for AI generation agents. It encodes deep filmmaking knowledge — dramatic architecture (Aristotelian beat structure), Meisner-method acting grammar, cathartic language philosophy (Godmode), and a 4-DP auteur enrichment layer — into composable Pydantic models and exposes everything via an MCP server.

**Repo:** `~/AUTEUR` (local) / `https://github.com/tradewife/auteur.git` (remote)
**Onchain:** `~/0xAUTEUR` (local) / `https://github.com/tradewife/0xAUTEUR.git` (remote)
**Branch:** `master`
**Python:** 3.12, venv at `.venv/` — always use `.venv/bin/python3` or activate first
**Package:** `auteur/`

## Deployment

### MCP Server (Railway)
- **Public endpoint:** `https://auteur-mcp-production.up.railway.app/mcp`
- **Transport:** Streamable HTTP
- **Railway project:** `auteur-mcp` (107fcd42-f321-48c4-8d62-f115fb0e9cdf)
- **Deploy from:** `~/AUTEUR` with `railway up --service auteur-mcp`

### Onchain Contracts (Base Sepolia)
| Contract | Address |
|----------|---------|
| auteur.sol (payment) | `0x4473350125F66FC17988589A9a948514866bfdE3` |
| auteuragent.sol (ERC-8183) | `0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3` |
| 0xAUTEUR Shot (Rare ERC-721) | `0x24D258b4249051Dbfa06b1526Bf847062562f126` |
| Rare Auction | `0x1f0c946f0ee87acb268d50ede6c9b4d010af65d2` |

### KIE Model Configuration
| Role | Model | Env Var |
|------|-------|---------|
| Main Image | Nano Banana 2 | `KIE_IMAGE_MODEL_MAIN` |
| Main Video | Kling 3.0 | `KIE_VIDEO_MODEL_MAIN` |
| Judge Image | Qwen Image 2.0 | `KIE_IMAGE_MODEL_JUDGE` |
| Judge Video | Seedance 1.5 Pro | `KIE_VIDEO_MODEL_JUDGE` |

### x402 Payment Flow
1. Client sends request with `Accept: application/json` to AUTEUR MCP endpoint
2. Server returns HTTP 402 with payment-required metadata (invoice, amount)
3. Client pays via onchain 0xAUTEUR `spend()` — TX hash becomes proof-of-payment
4. Client retries request with payment proof in header
5. Server validates spend receipt via `getLog()`, then fulfills the generation request
6. SpendReceipt event emitted onchain with CID fields linking to output

### ERC-8183 Agent-to-Agent Job Lifecycle
1. **Client** calls `createJob(requestService)` on AuteurAgent — defines scope and reward
2. **Client** calls `fundJob()` — locks ETH in escrow (evaluator gets stake, agent gets reward)
3. **Agent** (AUTEUR) generates the ShotSpec, composes prompt, calls generation provider
4. **Agent** calls `submitWork()` — delivers result CID as proof of work
5. **Evaluator** reviews output quality against brief requirements
6. **Evaluator** calls `completeJob()` — releases escrow to agent, attestations stored onchain

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
- `browser_use.py` — `BrowserUseProvider`. Automates web platforms via browser-use + LLM agents. Routes to agent runner or CLI fallback. Model IDs: `grok-imagine-web`.

### 6. Pipeline (`auteur/pipeline/`)
- `shot.py` — `ShotPipeline` (compose → optimize → generate)
- `sequence.py` — `SequencePipeline` (multi-shot)
- `assets.py` — `AssetManager` (output tracking)

### 7. Agents (`auteur/agents/`)
- `cinematographer.py` — `CinematographerAgent`. Translates narrative intent → `ShotSpec`.
- `director.py` — `DirectorAgent`. Plans multi-shot sequences via `PACING_TEMPLATES` (establishing_to_intimate, tension_build, action_sequence, dialogue_scene, reveal).

### 8. MCP Server (`auteur/server.py`)
FastMCP 3.1.0. 14 tools, 9 resources, 3 prompts.

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
- `browser_platforms` — List browser-automated platforms and auth status

**Resources:** `auteur://styles`, `auteur://styles/{name}`, `auteur://lenses`, `auteur://lens-families`, `auteur://lighting`, `auteur://palettes`, `auteur://movements`, `auteur://stocks`, `auteur://templates`, `auteur://camera`

**Prompts:** `establishing_shot`, `character_portrait`, `plan_mood_film`

### 9. CLI (`auteur/cli.py`)
Typer-based: `auteur version`, `auteur status`, `auteur shot`, `auteur explore`, `auteur browser-auth`, `auteur browser-cookies`, `auteur browser-grab`, `auteur browser-status`, `auteur serve`

### 10. Config (`auteur/config.py`)
Pydantic Settings from `.env`: `fal_key`, `kie_api_key`, `gemini_api_key`, `auteur_output_dir`, `browser_use_enabled`, `browser_use_api_key`, `browser_executable_path`, `browser_storage_state_dir`, `browser_artifact_dir`

## Key Architecture Decisions
- `ShotSpec` is the atomic unit — everything flows through it
- `ShotSpec.aesthetic_style` is `dict | None` (serialized `AestheticStyle`) to avoid circular imports between ontology and styles
- The prompt composer checks `shot.aesthetic_style` first (auteur enrichment path), falls back to `shot.style_profile` (legacy DP name path)
- MCP resource URIs use `auteur://` prefix
- Projects are session-scoped in-memory (`_projects` dict in server.py)
- Provider implementations use httpx async, models are dispatched via `_MODEL_MAP` dicts in each provider
- Browser-automated platforms use `-web` suffix model IDs (e.g. `grok-imagine-web`) to avoid collision with API-backed models
- Browser auth uses `storage_state` JSON (Playwright format) for cookie/localStorage persistence — never raw profile directory management
- Browser runner uses 3-phase pattern (submit → poll → collect) with short Agent runs to avoid expensive long-lived LLM sessions
- CLI deterministic runner is the fallback when LLM agent is too flaky — uses `browser-use` CLI daemon subprocess commands

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

# Test browser ops imports
.venv/bin/python3 -c "
from auteur.browser_ops.auth import make_account, import_cookies, has_auth
from auteur.browser_ops.cli_runner import CLISession, CLI_SCRIPTS
from auteur.browser_ops.platforms import PLATFORM_SPECS
from auteur.providers.browser_use import BrowserUseProvider
print('Browser ops:', list(PLATFORM_SPECS.keys()))
print('CLI scripts:', list(CLI_SCRIPTS.keys()))
"
```

## v1 — New Systems

### Dramatic Engine (`auteur/agents/director.py`)
- `MUSIC_VIDEO_BEAT_STRUCTURE` — 9-beat Aristotelian arc mapped to song sections
- `tension_to_duration()` — Maps tension level + section to shot duration (no more flat 10s clips)
- `DirectorAgent.plan_music_video()` — Full music video planning with tension-driven pacing

### Character System (`auteur/knowledge/project.py`)
- `CharacterSpec` — Persistent character with Meisner anchor (`core_desire`), physical signature, hero shot URL
- `MusicVideoBrief` — Structured brief: singer identity, protagonist, soul_lexicon, forbidden_words

### Prompt Sanitiser (`auteur/prompt/sanitiser.py`)
- `validate_shot()` — Pre-generation validation (aesthetic_style, meisner_note, camera package, banned words)
- `strip_banned_tokens()` — Removes genre labels, dead emotional words, transcendence clichés
- `ValidationResult` — Errors + warnings with actionable messages

### Skill Documents (`auteur/knowledge/skills/`)
- `STORYTELLER.md` — Dramatic architecture, 9-beat arc, singer rule, humanity rule
- `ACTORS_HANDBOOK.md` — Meisner method operationalized: behavior not feelings, 4 body states, proxemics
- `SOUL_LEXICON.md` — Cathartic image philosophy, Soul-Lexicon, living language, productive impossibility

### New MCP Tools
- `plan_music_video` — 9-beat arc with tension curve
- `generate_hero_shots` — Character portraits with full AuteurLayer enrichment
- `sanitise_and_submit` — Enforcement gate (the ONLY valid path to generation)

### New ShotSpec Fields
- `character_id` — References CharacterSpec
- `meisner_note` — Visible physical behavior (one sentence, no adjectives)
- `tension_level` — 0.0–1.0, drives duration and cut rhythm
- `i2v_source_url` — Concept image URL for image-to-video
- `duration_seconds` — Renamed from `animation_duration_s`, set by tension_to_duration()

### Browser Automation (`auteur/browser_ops/`)
- `auth.py` — Three auth strategies: existing `storage_state`, manual headed login (`bootstrap_auth`), cookie import (`import_cookies`). Also `bootstrap_via_cli_profile()` for grabbing cookies from a real Chrome profile. Uses Playwright `storage_state` JSON format (cookies + localStorage).
- `runner.py` — LLM Agent runner. 3-phase pipeline: submit task → poll status → collect outputs. Each phase is a short `Agent(task=..., llm=..., browser=...)` run. Artifacts saved per phase.
- `cli_runner.py` — Deterministic CLI fallback. `CLISession` wraps all `browser-use` CLI commands (open, state, click, type, keys, screenshot, eval, cookies, wait). `CLIPlatformScript` / `GrokImagineCLIScript` are per-platform scripts. Same 3-phase pipeline but no LLM cost.
- `platforms/base.py` — `PlatformSpec` ABC: `build_submit_task()`, `build_status_task()`, `build_collect_task()`, `parse_json_response()`. Builds natural-language agent task prompts, not CSS selectors.
- `platforms/grok_imagine.py` — `GrokImagineSpec` for x.com/i/grok.

### Browser Auth Strategies (in order of preference):
1. Existing `storage_state` file → `Browser(storage_state=<path>)` (normal runs)
2. Manual headed login → `bootstrap_auth()` → export `storage_state` (first time)
3. Cookie import from JSON → `import_cookies()` (flat array or Playwright format, with domain filter + merge)
4. Chrome profile grab → `bootstrap_via_cli_profile()` (piggyback on real Chrome login via CLI `--profile`)

---

## MANDATORY MUSIC VIDEO PROTOCOL

### Pipeline Order (call in this sequence):
1. `analyse_brief` — Capture creative intent
2. Set `MusicVideoBrief` on project (singer_identity, protagonist, thematic_conflict, soul_lexicon)
3. `propose_visual_language` — Lock AestheticStyle (call ONCE, never per-shot)
4. `plan_music_video` — 9-beat dramatic arc with tension-driven pacing
5. `generate_hero_shots` — Portraits for every CharacterSpec
6. `sanitise_and_submit` — The ONLY valid path to generation

### PROHIBITIONS:
- No standalone scripts calling KieProvider directly
- No `GenerationRequest` without a `ShotSpec` flowing through `PromptComposer`
- No forbidden words in prompts (cyberpunk, sci-fi, masterpiece, ethereal, etc.)
- No empty `meisner_note` on character shots
- No default `duration_seconds` (6.0) — must be set by `tension_to_duration()`
- No DP names in final prompts (inputs to AuteurLayer only)
- No generation before `visual_language_locked == True`
- No dead emotional words (love, fear, beauty, hope, sad, happy, lonely)

### Singer Rule:
Singer = protagonist by default. 40% minimum screen presence for singer-presenting character.

### Camera Rule:
Every shot must have a camera package sentence: body, lens, focal length, aperture, movement.

### Skill Documents (read before any music video run):
1. `auteur/knowledge/skills/STORYTELLER.md`
2. `auteur/knowledge/skills/SOUL_LEXICON.md`
3. `auteur/knowledge/skills/ACTORS_HANDBOOK.md`

---

## What Could Come Next
- **Blocking renderer** — Manim-based stick-figure animatic from ShotSpec (zero-cost pre-viz)
- **More auteurs** — Bradford Young, Janusz Kaminski, Robert Richardson DP profiles
- **Persistence** — SQLite/JSON project persistence (currently session-scoped)
- **Tests** — Formal test suite
- **Audio design** — Sound design knowledge for models with native audio
- **More browser platforms** — Runway, Pika, Luma platform specs and CLI scripts

## Files NOT in git
- `.env` — API keys (in .gitignore)
- `.venv/` — Python virtual environment (in .gitignore)
- `take-me-to-sol/` — First run output (untracked)
- `auteur-v1-notes/` — Planning notes (untracked)
- `.browser_state/` — Browser auth storage_state files (in .gitignore)

# AUTEUR

Deep cinematography intelligence for AI generation agents.

## What is AUTEUR?

AUTEUR is a code-first cinematography agent system. It encodes professional-grade filmmaking knowledge — the kind that lives in a DP's head after 20 years on set — into composable Pydantic data models, then uses that knowledge to generate precise, cinematic prompts for AI image and video generation.

It runs as an **MCP server**, so any MCP-compatible client (Claude, Cursor, GPT, custom agents) can use AUTEUR as a conversational co-director.

## Architecture

### Knowledge System
A deep cinematography ontology spanning every visual dimension:

- **Lenses** — Focal length psychology, named families (Cooke S4, Zeiss Master Prime, Panavision Primo), anamorphic/vintage character, bokeh profiles
- **Lighting** — Named setups (Rembrandt, butterfly, noir, split), color temperatures, light quality, atmospheric effects
- **Color** — Palettes, grading profiles (teal-orange, bleach bypass), emotional color mapping, harmony systems
- **Composition** — Shot sizes, angles, framing devices, depth of field, negative space, rule systems
- **Movement** — Camera movement types with philosophy and narrative purpose, stabilization methods
- **Film stocks & sensors** — Kodak/Fuji film stocks, ARRI/RED/Sony sensor profiles, grain character, dynamic range
- **Camera systems** — Sensor formats (Super 16 through IMAX), frame rates, aspect ratios

All encoded as composable Pydantic models in `auteur/knowledge/`.

### Style Profiles — Master DP Signatures
Four complete auteur profiles with technical specificity:

- **Roger Deakins** — Motivated single-source, controlled shadows, restrained naturalism
- **Vittorio Storaro** — Symbolic colored light, bold saturation, operatic movement
- **Emmanuel Lubezki** — Natural light obsession, golden hour, long-take immersion
- **Hoyte van Hoytema** — IMAX large format, photochemical texture, overwhelming scale

### Auteur Layer
Users never need to pick from presets. They describe what they want in any terms — mood, vibes, references, colors, anything:

> "rainy Tokyo night, lonely figure under neon signs"

The **Auteur Layer** analyzes this across five perceptual dimensions (mood, lighting, color, movement, texture), scores each master DP's relevance, and blends their techniques into the prompt invisibly:

→ Deakins 40% (shadow control, isolation) + Storaro 29% (neon color, bold light)

The `auteur_weight` parameter (0.0–1.0) controls enrichment intensity. The user sees a better prompt — they never have to know which DPs were blended in.

### Prompt Engine
The prompt composer works in ordered layers (subject → composition → lighting → camera → color → texture → movement → style → mood), because token position maps to model attention. Each layer is assembled from the ontology models, then the whole prompt is optimized per-model with format limits, boosters, and negative keywords.

Model-specific optimization for 55+ models across three providers.

### Generation Pipeline
Unified API layer with queue management, asset tracking, and provider routing:

- **FAL** (32 models) — Flux 2 Flex, Nano Banana 2/Pro, Veo 3/3.1, Kling 3.0/O3, Sora 2 Pro, Grok Imagine, LTX-2 19B, Wan 2.6, Seedance 1.5, Cosmos 2.5, Recraft V4, Seedream, Hunyuan, and more
- **Kie.ai** (15 models) — Kling 3.0, Runway Gen4 Turbo, Seedance 1.5 Pro, Wan 2.6, Nano Banana 2/Pro, GPT Image 1.5, Flux Kontext, and more
- **Gemini** (8 models) — Imagen 4 Standard/Ultra/Fast, Nano Banana 2, Veo 3

### Creative Agents
- **CinematographerAgent** — Translates narrative intent into complete `ShotSpec` technical specifications
- **DirectorAgent** — Plans multi-shot sequences using pacing templates (establishing-to-intimate, tension build, action, dialogue, reveal)

### MCP Server
10 tools, 9 resources, 3 prompt templates exposed via FastMCP:

**Tools:** `analyse_brief`, `propose_visual_language`, `plan_shots`, `compose_prompt`, `refine_shot`, `define_style`, `quick_compose`, `provider_status`, `list_pacing_templates`, `get_project`

**Resources:** `auteur://styles`, `auteur://lenses`, `auteur://lighting`, `auteur://palettes`, `auteur://movements`, `auteur://stocks`, `auteur://templates`, `auteur://camera`, `auteur://lens-families`

## Quick Start

```bash
pip install -e ".[dev]"
cp .env.example .env  # Add your API keys
auteur --help
```

### MCP Server

```bash
# stdio (for Claude Desktop, Cursor, etc.)
auteur serve --transport stdio

# SSE (for web clients)
auteur serve --transport sse --port 8000
```

### Quick Compose (no project needed)

Via MCP tool call:
```json
{
  "tool": "quick_compose",
  "arguments": {
    "description": "a lone woman walking through a rain-soaked alley at night",
    "style_description": "neon-drenched urban noir, isolated and melancholy",
    "model": "kling-3.0"
  }
}
```

### Full Workflow

1. `analyse_brief` — Parse creative intent into a structured project
2. `propose_visual_language` — Describe the look (freeform), AUTEUR enriches with auteur depth
3. `plan_shots` — Generate a shot list using pacing templates
4. `compose_prompt` — Get model-optimized prompts for each shot
5. `refine_shot` — Adjust individual shots as needed

## API Keys

| Provider | Get your key |
|----------|-------------|
| FAL | https://fal.ai/dashboard/keys |
| Kie.ai | https://kie.ai (dashboard → API key) |
| Gemini | https://aistudio.google.com/apikey |

## Project Structure

```
auteur/
├── knowledge/           # Cinematography ontology
│   ├── ontology.py      # Core data models (ShotSpec, LensSpec, etc.)
│   ├── styles/          # DP profiles + Auteur Layer
│   │   ├── aesthetic.py  # AestheticStyle + AuteurLayer
│   │   ├── deakins.py
│   │   ├── storaro.py
│   │   ├── lubezki.py
│   │   └── hoytema.py
│   ├── lens.py, lighting.py, color.py, composition.py,
│   │   movement.py, film_stock.py, camera.py
│   └── project.py       # Project/Brief/VisualLanguage models
├── prompt/              # Prompt engineering
│   ├── composer.py      # Layered prompt assembly
│   ├── optimizer.py     # Per-model optimization (55+ models)
│   ├── negative.py      # Negative prompt library
│   └── templates.py     # Shot templates
├── providers/           # API integrations
│   ├── fal.py           # 32 models
│   ├── kie.py           # 15 models
│   ├── gemini.py        # 8 models
│   └── registry.py      # Model routing
├── pipeline/            # Generation pipeline
│   ├── shot.py, sequence.py, assets.py
├── agents/              # Creative agents
│   ├── cinematographer.py
│   └── director.py
├── server.py            # MCP server (FastMCP)
├── cli.py               # CLI (Typer)
└── config.py            # Settings
```

## License

MIT

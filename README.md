# AUTEUR

AUTEUR is an MCP server for cinematic authorship. It turns any AI agent into a directing intelligence capable of shaping films, music videos, and other visually structured narratives from a brief, a lyric, or a single line of intent.

It is not a clip assembler. It is not a prompt wrapper. AUTEUR treats generation as filmmaking: dramatic architecture, character continuity, embodied performance, and a camera package that reads like something a working cinematographer would recognize.

Give it a sentence, a lyric, a character sketch, a mood reference, or a visual thesis, and it composes the rest with increasing autonomy. The more context you provide, the more control you retain. The less you provide, the more AUTEUR must infer. In either mode, every shot passes through the same pipeline: Aristotelian structure, Meisner-informed acting grammar, cathartic prompt language, and auteur-level cinematography, validated before anything reaches a generation model.

This is experimental. The craft it encodes is not.

## The Pipeline

Every shot flows through a single data structure called `ShotSpec`. It carries the story, the character, the behavior, the tension level, the camera package, and the visual language from the moment of creative intent to the moment of generation. Nothing bypasses it. Nothing reaches a video model without passing through the full stack.

The stack, in order:

**1. Dramatic architecture.**
A nine-beat Aristotelian arc maps song sections, scenes, or narrative movements to structural beats. `tension_to_duration()` converts tension into shot length: shorter at the climax, longer in passages that need room to breathe. Rhythm is designed, not inherited.

**2. Character and casting.**
`CharacterSpec` locks a protagonist's physical description, wardrobe, signature behavior, and core desire across every shot. `MusicVideoBrief` enforces casting continuity where relevant, so the visual field remains coherent from opening frame to final cut.

**3. Acting grammar.**
Every character shot carries a `meisner_note`. One sentence. Visible physical behavior. No emotional abstraction. "She presses her palm flat against the glass and does not look at him" passes validation. "She looks sad" does not. The sanitiser enforces this programmatically.

**4. Soul Lexicon.**
Before any shot is composed, the system builds a small vocabulary of phrases derived from the protagonist's wound. Sensory. Specific. Alive to texture. These phrases are woven into key beats by the prompt composer, giving the film a coherent emotional frequency that no isolated prompt would contain on its own.

**5. Auteur Layer.**
A freeform style description is analyzed across perceptual dimensions such as mood, lighting, color, movement, and texture, then scored against four master cinematographer profiles. Their techniques blend into the prompt according to the weight each earns. DP names do not appear in the output; what appears is the consequence of their methods.

> rainy Tokyo night, lonely figure under neon signs
> -> Deakins 40% (shadow control, isolation) + Storaro 29% (neon color, bold light)

**6. Prompt composition.**
Eight layers are assembled in attention-priority order: subject, composition, lighting, camera, color, texture, movement, style. Each layer draws from a deep cinematography ontology covering lens psychology, lighting setups, grading profiles, and film-stock character, then is optimized per model across 55+ generation models.

**7. Enforcement gate.**
`sanitise_and_submit` is the only valid path to generation. It validates that the visual language is locked, the `meisner_note` is present, the camera package is specified, and no banned tokens survived. It strips genre labels, dead emotional words, transcendence cliches, and prompt padding. If any check fails, it returns actionable errors instead of a prompt. The system cannot produce garbage even if the agent tries to shortcut.

## The Auteur Layer

Four complete DP profiles with technical specificity:

- **Roger Deakins**: motivated single-source, controlled shadows, restrained naturalism.
- **Vittorio Storaro**: symbolic colored light, bold saturation, operatic movement.
- **Emmanuel Lubezki**: natural light obsession, golden hour, long-take immersion.
- **Hoyte van Hoytema**: IMAX large format, photochemical texture, overwhelming scale.

## The Beat Structure

```text
Beat 1: opening_image    | intro      | tension 0.15 | 10.0s
Beat 2: inciting_rupture | verse_1    | tension 0.35 |  8.0s
Beat 3: pursuit          | verse_2    | tension 0.50 |  8.0s
Beat 4: pre_chorus_doubt | pre_chorus | tension 0.65 |  6.0s
Beat 5: chorus_eruption  | chorus_1   | tension 0.82 |  4.0s
Beat 6: reversal         | verse_3    | tension 0.55 |  6.0s
Beat 7: climax           | bridge     | tension 1.00 | 15.0s
Beat 8: consequence      | chorus_2   | tension 0.75 |  4.0s
Beat 9: resolution       | outro      | tension 0.20 | 10.0s
```

## Skill Documents

Three craft documents in `auteur/knowledge/skills/` operationalize filmmaking disciplines as generative constraints:

- **STORYTELLER.md**: Aristotelian dramatic action. The three questions every shot must answer: what is wanted, what resists it, and what changes.
- **ACTORS_HANDBOOK.md**: Meisner method for AI characters. Physical action, relational focus, proxemic behavior, and scene pressure.
- **SOUL_LEXICON.md**: Cathartic image philosophy. The difference between decoration and revelation. How language becomes image instead of explanation.

## MCP Integration

AUTEUR exposes a complete MCP interface for directed generation. Any MCP-compatible client, including Claude, Cursor, and custom agents, can connect directly.

### Music Video Workflow

```text
1. analyse_brief              capture creative intent
2. set MusicVideoBrief        singer, protagonist, soul_lexicon, forbidden_words
3. propose_visual_language    lock AestheticStyle via AuteurLayer
4. plan_music_video           nine-beat arc with tension-driven pacing
5. generate_hero_shots        character portraits with full enrichment
6. sanitise_and_submit        enforce, validate, compose, optimize per shot
```

### Quick Compose

```json
{
  "tool": "quick_compose",
  "arguments": {
    "description": "a woman pressing her palm flat against cold glass, not looking at the man behind it",
    "style_description": "warm amber key light from a single window, shallow focus, rain on the exterior",
    "model": "kling-3.0"
  }
}
```

## Generation Providers

Model-agnostic. 55+ models across three providers, routed through a single ontology:

- **Kie.ai**: Kling 3.0, Runway Gen4 Turbo, Seedance 1.5 Pro, Wan 2.6, GPT Image 1.5, Flux Kontext.
- **FAL**: Veo 3/3.1, Kling 3.0, Sora 2 Pro, Flux 2 Flex, Nano Banana 2/Pro, LTX-2 19B.
- **Gemini**: Imagen 4, Veo 3.

The intelligence layer is independent of the generation layer. Swap models without changing how the film is designed.

## Quick Start

```bash
pip install -e ".[dev]"
cp .env.example .env  # FAL_KEY, KIE_API_KEY, GEMINI_API_KEY
auteur serve --transport stdio
```

## Project Structure

```text
auteur/
├── knowledge/
│   ├── ontology.py          # ShotSpec and the full cinematography ontology
│   ├── project.py           # Project, CharacterSpec, MusicVideoBrief
│   ├── styles/              # 4 DP profiles, AestheticStyle, AuteurLayer
│   ├── skills/              # STORYTELLER, ACTORS_HANDBOOK, SOUL_LEXICON
│   └── lens, lighting, color, composition, movement, film_stock, camera
├── prompt/
│   ├── composer.py          # 8-layer prompt assembly with Soul-Lexicon catalyst
│   ├── sanitiser.py         # Enforcement gate
│   ├── optimizer.py         # Per-model optimization (55+ models)
│   └── negative.py, templates.py
├── agents/
│   ├── director.py          # 9-beat arc, tension_to_duration, plan_music_video
│   └── cinematographer.py   # Narrative intent to ShotSpec
├── providers/               # Kie.ai, FAL, Gemini, unified registry
├── pipeline/                # Shot and sequence execution, asset tracking
├── server.py                # MCP server (13 tools, 9 resources)
└── config.py
```

## License

MIT

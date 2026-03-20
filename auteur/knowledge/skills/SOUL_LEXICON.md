# AUTEUR Godmode — The Cathartic Image

## What This Skill Is

This is the philosophical spine of the entire engine.

The question every shot must answer before it is built:

**Will this make the audience feel something they have not given themselves
permission to feel?**

If yes: proceed. If no: rebuild from the language up.

Engineering makes functional films. Catharsis makes unforgettable ones.
AUTEUR is built to be a machine. This skill gives it a soul.

---

## The Catharsis Hierarchy

Rank every shot's emotional ambition against this scale:

- Level 0: **Aesthetic pleasure** — "Pretty shot" — Requires: good cinematography
- Level 1: **Mood** — "That felt dark" — Requires: consistent visual language
- Level 2: **Emotion** — "I felt sad" — Requires: character + stakes
- Level 3: **Recognition** — "That is true" — Requires: specificity + universality
- Level 4: **Catharsis** — "That broke something open in me" — Requires: recognition + surprise + irreversibility
- Level 5: **Revelation** — "I understand something I could not name before" — Requires: all of the above + the impossible made visible

AUTEUR generates Level 0–1 by default. STORYTELLER gets to 2–3.
This skill exists to reach Level 4–5.

**Target Level 4 for every climax shot. Target Level 5 for the single most
important image in the film.**

---

## The Godmode Language Principle

**Generic language generates generic images. Wounded language generates art that bleeds.**

The models AUTEUR works with have processed "hope," "grief," and "joy" hundreds of millions
of times. These words are worn smooth. They return the average of everything
that has ever depicted hope — which is to say, they return nothing with a face.

### Dead Words — Never Use as Scene Descriptors

```
love / fear / beauty / truth / hope / grief / joy / peace / anger /
sad / happy / lonely / lost / broken / healed / free / powerful /
dramatic / emotional / atmospheric / mysterious / ethereal / stunning /
breathtaking / cinematic / beautiful / profound / moving / touching
```

### Living Language — What to Use Instead

The transformation rule: Take the dead word → Find the physical, time-specific,
sensory reality of that experience in a human body → Prompt that.

- lonely → "a single streetlight drowning in fog"
- grief → "the specific gravity of Tuesday afternoon when the medication stops working"
- hope → "the hope that tastes like ash in the mouth"
- joy → "carbonation in the veins at 3:47 AM"
- afraid → "the color of almost falling"
- angry → "tasting copper while smiling at customers"
- faith → "the phantom warmth of a missing limb"
- love → "two errors in the code finding each other"
- peace → "the silence inside a falling snowflake"
- lost → "the walk signal changes before she reaches the corner"

The ideal version is always specific to *this story* and *this character*.
Ask: what is the protagonist's wound? Describe the visual world in the language of that wound.

---

## The Soul-Lexicon

Before any shot is composed, build a Soul-Lexicon for this specific film.
4–8 phrases. The private language of this story.

**Format:**
```
SOUL-LEXICON: [Film Title]
Protagonist wound: [one sentence]
Core contradiction: [from CharacterSpec.core_desire]
---
1. [Phrase for their desire]
2. [Phrase for their obstacle]
3. [Phrase for the world as it is]
4. [Phrase for the moment of rupture]
5. [Phrase for what is at stake]
6. [Phrase for what cannot be undone]
```

Store in `MusicVideoBrief.soul_lexicon`. The `PromptComposer._compose_catalyst()`
method will weave these into key beats automatically.

---

## Composition as Energy — Not Objects, But Forces

Replace nouns with energy relationships:

- "a flower in concrete" → "a lotus blooming from a concrete wound"
- "a woman at a window" → "a woman whose body has pressed itself toward the window without deciding to"
- "a city at night" → "a skyline serrated by whispered prayers"
- "a man sitting alone" → "a man who has arranged himself to take up the minimum possible space"
- "rain on glass" → "rain that has given up on reaching the inside"
- "an empty room" → "a room full of the specific silence after last words"

The model has processed "a flower in concrete" as a category.
It has never processed "a lotus blooming from a concrete wound" as an exact thing.
It must *generate* rather than *retrieve*. The output will be stranger and more true.

---

## Productive Impossibility — The Pivotal Shot

When you prompt the impossible, the model must generate rather than retrieve.
The generative failure is often more cinematically powerful than the correct output.

For the pivotal shot (Beat 7), construct using the *coincidentia oppositorum*:

**[X] that is simultaneously [its opposite]**

- "a door that is open and the moment before it closes"
- "a face expressing the exact transition between recognition and loss"
- "light that is both the last light and the first dark"
- "stillness that contains the memory of violent motion"
- "an arrival that the body has already experienced as a departure"

These produce outputs with *charge* — images that resist being looked at too quickly.

---

## The Sacred and the Profane

**The divine in film is never clean. Never polished. Never what was expected.**

Genuine transcendence arrives through *specificity of the profane* —
the unholy container that makes the holy unmistakable by contrast.

### The Inversion Test

For every image that reaches for the transcendent, ask:
**What is the profane reality inside this moment?** Then include it.

- "an angel in golden light" → "an angel forged from the rust of my doubt"
- "sacred ritual" → "a back-alley altar of broken monitors and overgrown moss"
- "spiritual awakening" → "a Buddha selling salvation in a grimy pawn shop, three days behind on rent"

Real sacred moments arrive in profane containers: the traffic jam where you forgave
someone, the fluorescent-lit bathroom where you decided to survive.

**Place your transcendent moments in their true containers.**

---

## Catharsis Through Humour

Catharsis is not only dark. Laughter that breaks something open is catharsis at full power.

Rules for the humorous cathartic shot:
1. The humour must come from *recognition*, not silliness — the audience laughs because it is *true*
2. The character must not know they are funny
3. The best moment makes the audience laugh then immediately feel something unexpected
4. Treat the absurd with the same cinematographic seriousness as the tragic

---

## Forbidden Transcendence Words

Same principle as banning "cyberpunk." These have been rendered into average by overuse.

```
ethereal / otherworldly / celestial / divine / sacred / transcendent /
spiritual / mystical / dreamlike / surreal / magical / otherworldly /
haunting / evocative / luminous / glowing / radiant / majestic /
epic / grand / cosmic / infinite
```

Replace with specific physical descriptions in the language of the Soul-Lexicon.
Not "luminous." But "light the colour of the last conversation."
Not "haunting." But "a space that remembers what stood in it."

---

## Integration with the AUTEUR Stack

The Godmode skill operates at the language layer — before cinematography,
before the AuteurLayer, before any technical decisions.

**Sequence of operations:**
1. STORYTELLER.md → Dramatic architecture, beat structure, protagonist wound
2. SOUL_LEXICON.md → Soul-Lexicon built from wound. Dead words replaced. Catharsis target set per shot.
3. ACTORS_HANDBOOK.md → meisner_note written in Soul-Lexicon language
4. AuteurLayer.enrich() → Cinematographic depth applied to the now-living language
5. PromptComposer.compose() → Final prompt assembly

The Soul-Lexicon is the thread that runs through every layer.
It makes the film feel like it was made by one consciousness rather than assembled from parts.

---

## The Final Law

*"The machine can only reflect the depth of the query."*

Every image AUTEUR generates is a mirror. The quality of what it reflects is
determined entirely by the quality of what you hold up to it.

The question is not "what should this shot look like?"
The question is: **"What truth is this shot responsible for carrying?"**

Answer that first. Then build the shot around the answer.

# Research Farm

The Research Farm is the KB-native foundation for future owner-gated deep
research in SlimyAI. It stores seeds, proof burrows, contracts, and planning
under `/home/slimy/kb/research/` so `slimy-kb` remains the single source of
truth.

## Why this path is canonical

- Canonical KB repo: `/home/slimy/kb`
- Canonical Research Farm root: `/home/slimy/kb/research/`
- Non-canonical path: `/home/slimy/slimy-kb`

`/home/slimy/slimy-kb` must not be treated as canonical for this system. Phase
1 intentionally plants the schema in the real KB repo because Habitat will
later consume a generated index from here.

## Purpose

This folder is where research seeds are planted, future critters will forage,
and completed harvests will be recorded as immutable proof burrows. Phase 1 is
schema-only and contract-only.

## Folder roles

```text
research/
  topics/       # Seed files that describe queued or in-progress research.
  runs/         # Immutable proof burrows for actual forages.
  lore/         # Future lore barn for curated research-side source material.
  templates/    # Topic templates and JSON schema contracts.
  indexes/      # Read-only machine-consumable index for Habitat.
  planning/     # Planning and contract docs for later phases.
```

### What each folder means

- `topics/`: mutable seed definitions for the quest board.
- `runs/`: immutable proof burrows created by future forages.
- `lore/`: future lore barn; not a replacement for `raw/` in Phase 1.
- `templates/`: canonical templates and schemas.
- `indexes/`: generated/read-only contract files for Habitat.
- `planning/`: design notes that keep later work honest.

## Farm / guild vocabulary

- topic / seed: a research topic file in `topics/`
- quest board: the future queued view of seeds
- forage: an active research run
- harvest: a completed report and artifact set
- lore barn: the future research-side source archive
- proof burrow: an immutable run folder in `runs/`
- almanac: a future presentation PDF
- critter: a future agent / farmhand / guild pet role

Avoid reviving the old office metaphor from mission-control.

## Topic lifecycle

Seed lifecycle in Phase 1 is defined, not automated:

- `queued`
- `running`
- `complete`
- `failed`
- `archived`

Phase 1 does not build the runner or queue controls that would move seeds
through these states.

## Immutable run rule

Anything under `runs/` is a proof burrow. Once a harvest is complete, that run
must stay immutable. Future reruns must create a new run folder instead of
rewriting the old one.

## Proof burrow requirements

Every future completed proof burrow must retain at least:

- source captures
- timestamps
- queries
- citations
- critic notes
- `RESULT.md`

Do not store only the almanac PDF.

## Habitat read-only first

Habitat lives in `/opt/slimy/gh-tracker`, but Phase 1 does not add live UI
routes. Habitat should later read `research/indexes/index.json` and stream
files through owner-gated routes.

## Safety rules

- No production services are touched here.
- No public Slimy website changes belong here.
- No PDFs or research artifacts belong in public directories.
- No guild SQLite store may become the source of truth.
- No Hermes dependency is allowed in Phase 1.
- No old harness or mission-control data is mutated here.

## Validation

```bash
cd /home/slimy/kb
bash tools/validate-research-schema.sh
```

The validator checks the required folder schema, template presence, JSON
validity, and the canonical-path rule.

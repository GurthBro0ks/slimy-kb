# Super Snail Game Database

This directory contains the canonical Super Snail game database — a structured, version-controlled knowledge base for the mobile game *Super Snail*.

## Directory Structure

```
game/
  data/
    canonical/     — Verified, production-ready JSON records
    staging/       — Incoming imports awaiting validation
    schemas/       — JSON Schema (draft-07) definitions for every entity type
    indexes/       — Lookup indexes and search manifests
    exports/       — Flattened exports consumed by runtime systems
  guides/
    beginner/      — New player guides
    gear/          — Gear and equipment guides
    forms/         — Gene form guides
    relics/        — Relic guides
    research/      — Research tree guides
    club/          — Club and social guides
    events/        — Event guides
  sources/
    wiki_gg/       — Scraped wiki.gg pages
    reddit/        — Reddit post archives
    screenshots/   — In-game screenshots
    spreadsheets/  — Community spreadsheets
    reverse_engineering/ — Datamine and reverse-engineering notes
    ocr_prompts/   — OCR system prompts used for screenshot extraction
  assets/
    icons/         — Entity icons (gear, relics, forms, items)
    screenshots/   — Full-resolution screenshots
    manifests/     — Asset metadata and provenance
  pipelines/
    wiki_importer/ — Scripts to import from wiki.gg
    icon_importer/ — Scripts to fetch and process icons
    normalizers/   — Data normalization scripts
    exporters/     — Scripts to build runtime exports
  reports/
    discovery/     — New findings and discoveries
    imports/       — Import run logs and summaries
    audits/        — Data quality audits
```

## Data Flow

1. **Schemas define shape** — Every entity type has a JSON Schema in `data/schemas/`. These are the contracts.
2. **Staging holds imports** — Raw imports (wiki scrapes, OCR extractions, spreadsheet dumps) land in `data/staging/`.
3. **Canonical holds verified records** — After validation against schemas and human review, records are promoted to `data/canonical/`.
4. **Exports feed runtime** — The `pipelines/exporters/` scripts flatten canonical data into `data/exports/`, which is then consumed by:
   - **slimy-monorepo website** (`/snail/*` routes)
   - **Discord bot** (`/snail` commands)

## How to Add New Data

1. Place new records in the appropriate `data/staging/` subdirectory.
2. Validate against the relevant schema in `data/schemas/`.
3. Review for accuracy and completeness.
4. Move (or copy) verified records to `data/canonical/`.
5. Run the export pipeline to update `data/exports/`.
6. Commit and push.

## Runtime Consumers

- **Website**: `slimy-monorepo` reads `data/exports/` to render gear lists, form guides, and stat calculators at `/snail/*`.
- **Discord Bot**: The bot loads `data/exports/` into memory to answer `/snail` commands with entity lookups and recommendations.

## Schema List

| Schema | Description |
|--------|-------------|
| `gear.schema.json` | Equipment (weapon, armor, accessory) |
| `relic.schema.json` | Relics with stat bonuses |
| `form.schema.json` | Gene forms |
| `research_timer.schema.json` | Research projects |
| `troop.schema.json` | Troop units |
| `item.schema.json` | Consumables, materials, currency |
| `effect.schema.json` | Buffs, debuffs, passives |
| `code.schema.json` | Redemption codes |
| `guide.schema.json` | Player guides |
| `source_fact.schema.json` | Sourced factual claims |
| `asset_image.schema.json` | Image assets |
| `optimizer_rule.schema.json` | Optimizer recommendation rules |
| `tier_rating.schema.json` | Tier ratings |
| `bot_answer_chunk.schema.json` | Discord bot answer chunks |
| `entity_index.schema.json` | Master entity lookup index |

## Contributing

- Follow the schemas strictly.
- Add source facts for any claim that isn't obvious from the game UI.
- Include `source` and `icon_ref` fields whenever possible.
- Run the export pipeline before committing changes that affect runtime consumers.

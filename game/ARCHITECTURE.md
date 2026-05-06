# Super Snail Game Database — Architecture

## Data Ownership Split

This repository (`slimy-kb/game/`) owns **static game knowledge**:
- Entity definitions (gear, relics, forms, troops, items, effects)
- Guide content (markdown articles)
- Image assets (icons, screenshots)
- Source facts and tier ratings
- Optimizer rules and bot answer chunks

The **runtime database** (in `slimy-monorepo`) owns **player-specific mutable state**:
- Player profiles and loadouts
- Gear enhancement levels per player
- Troop compositions per player
- Historical stat snapshots
- Club membership and rankings

**Rule of thumb**: If every player sees the same value, it lives here. If each player has their own value, it lives in the runtime DB.

## Storage Model

| Data Type | Format | Location |
|-----------|--------|----------|
| Game entities | JSON | `game/data/canonical/*.json` |
| Guides | Markdown | `game/guides/**/*.md` |
| Images | PNG/WebP | `game/assets/**/*` |
| Asset metadata | JSON | `game/assets/manifests/*.json` |
| Schemas | JSON Schema | `game/data/schemas/*.json` |
| Indexes | JSON | `game/data/indexes/*.json` |
| Staging imports | JSON | `game/data/staging/**/*.json` |

## Export Pipeline

```
Staging  →  Validate  →  Canonical  →  Export  →  Runtime
  data        schema       records     scripts    consumers
```

1. **Staging → Canonical**: `pipelines/normalizers/` validate staging files against schemas, deduplicate, and promote to canonical.
2. **Canonical → Exports**: `pipelines/exporters/` flatten canonical JSON into optimized bundles:
   - `exports/gear.json` — all gear records
   - `exports/relics.json` — all relic records
   - `exports/forms.json` — all form records
   - `exports/troops.json` — all troop records
   - `exports/items.json` — all item records
   - `exports/effects.json` — all effect records
   - `exports/codes.json` — all redemption codes
   - `exports/index.json` — entity lookup index
3. **Exports → Runtime**: The `slimy-monorepo` package `packages/shared-snail/kb/` symlinks or copies these exports at build time.

## Entity Relationships

```
Gear ──has──▶ Effect
     ──belongs_to──▶ Set
     ──has_icon──▶ AssetImage

Relic ──has──▶ Effect (awakened)
      ──has_icon──▶ AssetImage

Form ──has_prerequisites──▶ Form
     ──has──▶ Effect
     ──has_icon──▶ AssetImage

Troop ──has──▶ Element
      ──has──▶ Skill
      ──has_icon──▶ AssetImage

Item ──has_icon──▶ AssetImage

Effect ──granted_by──▶ [Gear, Relic, Form]

ResearchTimer ──requires──▶ Item
              ──grants──▶ Effect

Code ──rewards──▶ Item

Guide ──references──▶ [Gear, Relic, Form, Troop]

TierRating ──rates──▶ [Gear, Relic, Form, Troop]
         ──backed_by──▶ SourceFact

OptimizerRule ──backed_by──▶ SourceFact

BotAnswerChunk ──references──▶ [Gear, Relic, Form, Troop]
               ──backed_by──▶ SourceFact
```

## Stat Structures

### Personal Stats (Snail)
| Stat | Description |
|------|-------------|
| HP | Health Points |
| ATK | Attack |
| DEF | Defense |
| RUSH | Rush / Speed |
| FAME | Fame |
| TECH | Technology |
| ART | Art |
| CIV | Civilization |
| FTH | Faith |

### Troop Stats
| Stat | Description |
|------|-------------|
| Power | Overall troop power |
| HP | Troop health |
| ATK | Troop attack |
| DEF | Troop defense |
| Rush | Troop rush |
| Leadership | Leadership value |
| Crit | Critical hit rate |
| Fire | Fire element bonus |
| Water | Water element bonus |
| Earth | Earth element bonus |
| Wind | Wind element bonus |
| Poison | Poison element bonus |

### Equipment Slots
| Slot | Description |
|------|-------------|
| Weapon | Primary weapon |
| Armor | Body armor |
| Accessory | Rings, necklaces, etc. |

## Versioning

- Canonical data is versioned by git commit.
- Export bundles include a `generated_at` timestamp and `git_commit` hash.
- Runtime consumers should check the commit hash to know when to reload.

## Performance Notes

- Canonical JSON files are human-readable (pretty-printed, 2-space indent).
- Export JSON files are machine-optimized (minified, single line).
- Indexes are pre-built so runtime consumers do not need to scan all canonical files.
- Asset images are stored at full resolution; runtime consumers should generate their own thumbnails.

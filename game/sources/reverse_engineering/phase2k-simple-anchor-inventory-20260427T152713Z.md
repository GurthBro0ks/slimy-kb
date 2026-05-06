# Phase 2K Simple Handler Anchor Inventory

Generated: 2026-04-27

## Objective

Expand the anchor pool for the Phase 2 punctuation/control transform work by pulling small `cmd/misc` handlers into `/tmp` only, then generating sanitized structural metadata for future anchor selection.

## Inputs

External raw-pull proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Sanitized inventory proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152713Z
```

Script:

```text
src/decode/phase2k_simple_anchor_inventory.py
```

## Method

1. Queried live device `cmd/misc` handler paths.
2. Pulled handlers with size `<= 500` bytes into external `/tmp` proof storage only.
3. Set pulled originals read-only.
4. Scanned the pulled originals with the alphanumeric table.
5. Emitted sanitized structural metadata:
   - filename
   - size
   - SHA256
   - alphanumeric skeleton length
   - `returnfunctionlpc` skeleton presence
   - high-level token hits
   - anchor score

No decoded Lua source was written to the repo.

## Result

```text
handlers scanned: 838
return/function/lpc skeleton hits: 830
positive anchor scores: 838
top candidate limit: 80
solved: false
```

## High-Value Candidate Examples

Top-scoring candidates include:

| File | Size | Token hits | Anchor score |
|:---|---:|:---|---:|
| `msg_week_task_myrank.luac` | 347 | `returnfunctionlpc`, `RankM`, `TopM`, `EventMgr`, `TaskM` | 43 |
| `msg_shop_info.luac` | 199 | `returnfunctionlpc`, `EventMgr`, `MEuser` | 40 |
| `msg_pet_skin_action.luac` | 207 | `returnfunctionlpc`, `EventMgr`, `MEuser` | 40 |
| `msg_dog_shit.luac` | 228 | `returnfunctionlpc`, `EventMgr`, `MEuser` | 40 |
| `msg_research_start.luac` | 228 | `returnfunctionlpc`, `EventMgr`, `MEuser` | 40 |
| `msg_quest.luac` | 123 | `returnfunctionlpc`, `EventMgr` | 39 |
| `msg_say.luac` | 128 | `returnfunctionlpc`, `EventMgr` | 39 |
| `msg_top_rank.luac` | 130 | `returnfunctionlpc`, `TopM` | 39 |
| `msg_top_list.luac` | 134 | `returnfunctionlpc`, `TopM` | 39 |
| `msg_arena_top.luac` | 136 | `returnfunctionlpc`, `ArenaM` | 39 |

## Interpretation

The next transform proof should use this inventory to choose many small, simple handlers as anchors. The goal is to create repeated left/right/raw-gap contexts for Phase 2J so transforms can be promoted only when repeated and conflict-free.

## Output Files

External proof files:

- `simple_handler_inventory.tsv`
- `top_anchor_candidates.tsv`
- `manifest.json`
- `RESULT.md`

Raw pulled `.luac` files remain external under `/tmp` and are not committed.

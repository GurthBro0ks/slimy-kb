# Phase 2P Unresolved Span Inventory

Generated: 2026-04-27

## Objective

Rank repeated unresolved spans from the Phase 2O redacted overlays so the next template additions are evidence-led instead of guessed.

Sensitive unresolved alphanumeric span text is kept only in the external proof directory. This committed report uses hash/count metadata only.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phase 2O overlay proof:

```text
/tmp/proof_snail_phase2o_template_overlay_20260427T160243Z
```

Phase 2P inventory proof:

```text
/tmp/proof_snail_phase2p_unresolved_span_inventory_20260427T160515Z
```

Script:

```text
src/decode/phase2p_unresolved_span_inventory.py
```

## Method

The script:

1. Reads `unresolved_spans.tsv` from the Phase 2O proof.
2. Recomputes each handler alphanumeric skeleton from the external originals.
3. Extracts unresolved span text into an external sensitive TSV.
4. Groups spans by SHA256 hash.
5. Writes a sanitized summary with hash, length, occurrence count, file count, and sample filenames.

No sensitive span text is committed.

## Result

```text
input handlers: 838
unresolved span rows: 2000
unique unresolved spans: 1867
repeated unresolved spans: 36
solved: false
```

## Top Sanitized Repeats

| Span hash prefix | Length | Occurrences | Files | Sample files |
|:---|---:|---:|---:|:---|
| `0cbedbb6866a` | 22 | 38 | 38 | `msg_activity_vote_action.luac`, `msg_ads_skip_complete.luac`, `msg_arena_sweep.luac` |
| `143f224bc2aa` | 19 | 20 | 20 | `msg_active_rocket_robot.luac`, `msg_body_variation.luac`, `msg_cook_resonance_action.luac` |
| `42033b707e4a` | 26 | 19 | 19 | `msg_account_func_record_result.luac`, `msg_activity_branch_level_action.luac`, `msg_activity_condition_task_action.luac` |
| `25ad8f5173d9` | 5 | 14 | 14 | `msg_bbs_newest.luac`, `msg_bbs_recommend.luac`, `msg_bbs_reply.luac` |
| `812c05802876` | 7 | 6 | 6 | `msg_body_system_step.luac`, `msg_country_postcard_bonus.luac`, `msg_refresh_pick_data.luac` |

## Interpretation

Phase 2P gives a clean target list for the next template pass. The first three repeated unresolved spans occur across many files, so they are better candidates than one-off long spans.

The sensitive external ledger should be used to decide exact template names locally, then only reusable templates should be promoted into the Phase 2L/2M phrase table.

## Output Files

External proof files:

- `input_inventory.tsv`
- `unresolved_span_rows_sensitive.tsv`
- `unresolved_span_summary_sanitized.tsv`
- `manifest.json`
- `RESULT.md`

## Next Move

Use the top repeated unresolved span hashes to add a small Phase 2Q template pass. Keep the sensitive span text external and commit only the template IDs, scripts, tests, and sanitized reports.

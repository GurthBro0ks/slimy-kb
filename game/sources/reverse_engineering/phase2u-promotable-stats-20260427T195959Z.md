# Phase 2U Promotable Stats

Generated: 2026-04-27

## Objective

Rank Phase 2T selected promotable templates using sanitized metadata only.

This phase does not read or commit candidate text. It uses:

- source tags from the Phase 2T selected/skipped overlay ledgers
- sanitized classifier metadata from Phase 2R

## Inputs

Phase 2T conflict-overlay proof:

```text
/tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z
```

Phase 2R classifier proof:

```text
/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z
```

Phase 2U stats proof:

```text
/tmp/proof_snail_phase2u_promotable_stats_20260427T195959Z
```

Script:

```text
src/decode/phase2u_promotable_stats.py
```

## Result

```text
promotable templates seen: 8
total selected promotable: 174
total skipped promotable: 2
solved: false
```

## Sanitized Ranking

| Promotable ID | Category | Selected | Skipped | Selected files | Priority |
|:---|:---|---:|---:|---:|---:|
| `promotable_span_0cbedbb6866a` | `api_member_fragment` | 60 | 0 | 60 | 1320 |
| `promotable_span_42033b707e4a` | `api_member_fragment` | 23 | 0 | 22 | 598 |
| `promotable_span_54f17bbc2b7b` | `grammar_fragment` | 42 | 2 | 43 | 232 |
| `promotable_span_5bc37e8ce37a` | `grammar_fragment` | 10 | 0 | 10 | 180 |
| `promotable_span_25ad8f5173d9` | `grammar_fragment` | 19 | 0 | 19 | 95 |
| `promotable_span_812c05802876` | `grammar_fragment` | 12 | 0 | 12 | 84 |
| `promotable_span_d7a471fd994d` | `api_member_fragment` | 4 | 0 | 4 | 76 |
| `promotable_span_0a050ef2196b` | `grammar_fragment` | 4 | 0 | 4 | 40 |

## Interpretation

The two highest-priority candidates are API/member fragments with many selected overlays and zero skipped overlaps. They are the best next targets for stable naming.

The short grammar fragment with 42 selected overlays also has 2 skipped overlaps, so it should stay in the external-trial path until grammar context is better constrained.

## Output Files

External proof files:

- `promotable_stats_sanitized.tsv`
- `manifest.json`
- `RESULT.md`

## Next Move

Inspect the top API/member candidates externally and decide whether their exact names are safe to promote as committed template identifiers. Keep non-API grammar fragments external until a punctuation-aware grammar layer exists.

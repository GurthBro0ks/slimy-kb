# Phase 2W Grammar Fragment Audit

Generated: 2026-04-27

## Objective

Audit the remaining external grammar-fragment candidates from Phase 2R/2T and decide which should stay external versus which can continue in an external trial path.

Fragment text stays external only.

## Inputs

Phase 2R classifier proof:

```text
/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z
```

Phase 2T conflict-overlay proof:

```text
/tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z
```

Phase 2W grammar audit proof:

```text
/tmp/proof_snail_phase2w_grammar_fragment_audit_20260427T200422Z
```

Script:

```text
src/decode/phase2w_grammar_fragment_audit.py
```

## Result

```text
grammar candidates: 5
hold: 3
trial_ok: 2
solved: false
```

## Sanitized Audit

| Promotable ID | Length | Selected | Skipped | Risk | Reason |
|:---|---:|---:|---:|:---|:---|
| `promotable_span_54f17bbc2b7b` | 6 | 42 | 2 | `hold` | has skipped overlaps |
| `promotable_span_25ad8f5173d9` | 5 | 19 | 0 | `hold` | short grammar fragment needs punctuation-aware context |
| `promotable_span_0a050ef2196b` | 10 | 4 | 0 | `hold` | low selected occurrence count |
| `promotable_span_812c05802876` | 7 | 12 | 0 | `trial_ok` | no skipped overlaps and enough repeated context |
| `promotable_span_5bc37e8ce37a` | 18 | 10 | 0 | `trial_ok` | no skipped overlaps and enough repeated context |

## Interpretation

The grammar layer should not promote the highest-count short fragment yet, because it has skipped overlaps. The other short fragment should also wait for punctuation-aware context despite no skips.

The two `trial_ok` grammar fragments can continue through external-only trials, but they should not be committed as plaintext templates until their punctuation and grammar role are independently verified.

## Output Files

External proof files:

- `grammar_fragment_audit_sensitive.tsv`
- `grammar_fragment_audit_sanitized.tsv`
- `manifest.json`
- `RESULT.md`

## Next Move

Run an external-only punctuation-aware trial for the two `trial_ok` grammar fragments. Keep exact fragment text external and report only hashes, counts, and conflict status.

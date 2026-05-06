# Phase 2T Conflict-Aware Overlay

Generated: 2026-04-27

## Objective

Render a conflict-aware redacted overlay using:

- committed base phrase templates
- external Phase 2R promotable templates

The overlay keeps base and promotable external templates separately tagged and records skipped overlaps.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phase 2N phrase-gap proof:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z
```

Phase 2R classifier proof:

```text
/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z
```

Phase 2T conflict-overlay proof:

```text
/tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z
```

Script:

```text
src/decode/phase2t_conflict_overlay.py
```

## Method

The script:

1. Reads the external handler originals.
2. Loads base templates from the committed Phase 2L/2N template table.
3. Loads only promotable external templates from the external Phase 2R proof.
4. Finds all candidate occurrences.
5. Selects non-overlapping occurrences while preferring base templates at the same start offset.
6. Records skipped overlaps.
7. Emits redacted overlays with `source=base` or `source=promotable_external`.

No promotable template text is committed.

## Result

```text
handlers scanned: 838
candidate occurrences: 1948
selected occurrences: 1945
skipped overlaps: 3
selected base: 1771
selected promotable_external: 174
known gap rows: 3338
unknown gap rows: 0
conflict gap rows: 0
solved: false
```

## Interpretation

Phase 2T confirms the promotable external subset can be layered into the redacted overlay path without creating phrase-local gap conflicts.

The three skipped overlaps are expected and are recorded externally in `skipped_overlaps.tsv`. One base template was skipped where a longer selected span already covered it; the other two skipped rows were short promotable fragments overlapping selected context.

This is still a redacted overlay workflow, not full decoded source.

## Output Files

External proof files:

- `candidate_occurrences.tsv`
- `selected_occurrences.tsv`
- `skipped_overlaps.tsv`
- `redacted_overlays/*.overlay.txt`
- `manifest.json`
- `RESULT.md`

## Next Move

Use the selected promotable-external occurrences to identify which candidate templates deserve stable committed names, while keeping exact sensitive text external unless it is already a known project-safe API/member name.

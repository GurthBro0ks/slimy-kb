# Phase 2J Gap Context Model

Generated: 2026-04-27

## Objective

Group Phase 2I raw punctuation/control gaps by local alphanumeric context. This tests whether the transform becomes stable when keyed by surrounding plaintext characters instead of treated as a global punctuation substitution table.

## Inputs

Phase 2I proof:

```text
/tmp/proof_snail_phase2i_skeleton_transform_20260427T152041Z
```

Phase 2J proof:

```text
/tmp/proof_snail_phase2j_gap_context_model_20260427T152345Z
```

Script:

```text
src/decode/phase2j_gap_context_model.py
```

## Result

```text
gap rows: 59
context rows: 59
context conflict-free rows: 59
context repeated conflict-free rows: 0
context conflict rows: 0
global raw gap rows: 38
solved: false
```

## Interpretation

The transform looks locally consistent for the current evidence set, but it is too sparse to promote:

- every exact left/right/raw-gap context has one candidate
- no exact context is observed more than once
- therefore there are no repeated conflict-free context transforms yet
- global raw gaps remain conflicted across different contexts

This means context/run-level modeling is the right direction, but the current anchor set is not large enough to produce a proven decoder.

## Safe Takeaway

Do not add punctuation mappings to `scripts/decrypt_handler.py` from this proof alone.

The next useful step is expanding anchors across more short handlers where the alphanumeric skeleton is obvious and the Lua grammar is simple. Once repeated contexts appear, only repeated conflict-free rows should be promoted.

## Output Files

External proof files:

- `context_gap_summary.tsv`
- `context_gap_conflict_free.tsv`
- `context_gap_repeated_conflict_free.tsv`
- `context_gap_conflicts.tsv`
- `raw_gap_summary.tsv`
- `plain_gap_summary.tsv`
- `manifest.json`
- `RESULT.md`

# Phase 2O Template Overlay Decoder

Generated: 2026-04-27

## Objective

Render a redacted handler overlay from the Phase 2N phrase evidence.

The overlay shows only:

- phrase IDs
- local known/unknown/conflict gap counts
- unresolved alphanumeric span lengths
- input hashes and offsets

It does not emit decoded Lua source.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phrase-gap proof:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z
```

Phase 2O overlay proof:

```text
/tmp/proof_snail_phase2o_template_overlay_20260427T160243Z
```

Script:

```text
src/decode/phase2o_template_overlay_decoder.py
```

## Method

The script:

1. Reads the external small-handler originals.
2. Computes the alphanumeric skeleton with the carried-forward table.
3. Finds phrase templates from the Phase 2L/2N shared template list.
4. Selects non-overlapping phrase matches for each handler.
5. Checks each phrase-local raw gap against the Phase 2L context ledger.
6. Writes redacted overlay views plus TSV ledgers.

No raw `.luac` files or full decoded handler source are committed.

## Result

```text
handlers scanned: 838
selected phrase occurrences: 1771
unresolved spans: 2133
known gap rows: 3338
unknown gap rows: 0
conflict gap rows: 0
solved: false
```

Example external redacted overlay for `msg_top_rank.luac`:

```text
<unresolved_alnum:23> <return_function_lpc known_gaps=2 unknown_gaps=0 conflict_gaps=0> <topm_set_my_rank known_gaps=1 unknown_gaps=0 conflict_gaps=0> <lpc_id known_gaps=1 unknown_gaps=0 conflict_gaps=0> <lpc_rank known_gaps=1 unknown_gaps=0 conflict_gaps=0> <unresolved_alnum:3>
```

This proves the overlay mechanism can apply known phrase-local gap evidence without reconstructing the unknown spans.

## Interpretation

Phase 2O is the first usable safe decoder shape:

```text
raw handler -> redacted phrase overlay + unresolved spans + conflict ledger
```

The zero unknown/conflict gap rows mean every selected phrase-local gap found in this run was backed by the current Phase 2L ledger. The unresolved spans are expected; they are the next target for additional templates or a more formal grammar model.

## Output Files

External proof files:

- `input_inventory.tsv`
- `overlay_occurrences.tsv`
- `unresolved_spans.tsv`
- `redacted_overlays/*.overlay.txt`
- `manifest.json`
- `RESULT.md`

## Next Move

Use `unresolved_spans.tsv` to rank the most repeated unresolved skeleton spans, then add only high-confidence reusable templates. Keep the output redacted until enough grammar coverage exists to justify a separate source-reconstruction proof.

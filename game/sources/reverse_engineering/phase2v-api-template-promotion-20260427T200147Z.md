# Phase 2V API Template Promotion

Generated: 2026-04-27

## Objective

Promote only the two highest-priority API/member candidates from Phase 2U into the committed base phrase table, then rerun the base phrase-gap, coverage, and overlay proofs.

Lower-confidence API and grammar candidates remain external.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

New Phase 2L phrase-gap proof:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T200142Z
```

New Phase 2M coverage proof:

```text
/tmp/proof_snail_phase2m_phrase_coverage_20260427T200142Z
```

New Phase 2O overlay proof:

```text
/tmp/proof_snail_phase2o_template_overlay_20260427T200147Z
```

Script changed:

```text
src/decode/phase2l_standard_phrase_gap_audit.py
```

## Promoted Templates

Two API/member templates were promoted:

- `dormutil_close_communicating`
- `close_communicating_dorm`

They were selected because Phase 2U ranked them as the top two API/member candidates, with 83 selected overlays combined and zero skipped overlaps.

## Result

### Phase 2L

```text
handlers scanned: 838
phrase occurrences: 1855
gap rows: 3362
context rows: 264
repeated conflict-free contexts: 152
context conflicts: 0
solved: false
```

Template hit counts:

```text
close_communicating_dorm: 60
dormutil_close_communicating: 23
```

### Phase 2M

```text
handlers scanned: 838
phrase sequence rows: 1855
handlers with >=50% phrase coverage: 32
max coverage pct: 69.33
solved: false
```

### Phase 2O

```text
handlers scanned: 838
selected phrase occurrences: 1854
unresolved spans: 2081
known gap rows: 3361
unknown gap rows: 0
conflict gap rows: 0
solved: false
```

## Coverage Comparison

| Phase | Base committed templates | >=50% Coverage Handlers | Context Conflicts |
|:---|:---|---:|---:|
| 2N | before API promotion | 22 | 0 |
| 2V | after two API/member promotions | 32 | 0 |

## Interpretation

Phase 2V safely moves the two strongest API/member candidates from external trial into the committed base template path. It improves base coverage while preserving the zero-conflict constraint.

The remaining Phase 2R candidates should stay external until a punctuation-aware grammar layer can validate them.

## Next Move

Build a small grammar-context audit for the remaining external grammar fragments, especially the short fragment that had 42 selected overlays but 2 skipped overlaps in Phase 2U.

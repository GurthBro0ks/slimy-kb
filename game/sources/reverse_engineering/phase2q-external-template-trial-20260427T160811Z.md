# Phase 2Q External Template Trial

Generated: 2026-04-27

## Objective

Test repeated unresolved spans as external-only candidate templates, then measure coverage impact without committing sensitive span text.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phase 2P unresolved-span proof:

```text
/tmp/proof_snail_phase2p_unresolved_span_inventory_20260427T160515Z
```

Phase 2Q external-template proof:

```text
/tmp/proof_snail_phase2q_external_template_trial_20260427T160811Z
```

Script:

```text
src/decode/phase2q_external_template_trial.py
```

## Method

The script:

1. Reads repeated unresolved spans from the external Phase 2P sensitive ledger.
2. Selects spans with at least 3 occurrences and length at least 5.
3. Builds external-only candidate template IDs from span hashes.
4. Runs a coverage pass using base templates plus external candidates.
5. Writes sensitive candidate text only to `/tmp`.
6. Writes sanitized candidate metadata using hashes, lengths, and counts.

No candidate template text is committed.

## Result

```text
candidate templates: 12
handlers scanned: 838
phrase sequence rows: 1977
handlers with >=50% phrase coverage: 45
max coverage pct: 69.33
solved: false
```

Baseline from Phase 2N/2M:

```text
phrase sequence rows: 1772
handlers with >=50% phrase coverage: 22
max coverage pct: 69.33
```

## Sanitized Candidate Set

| Candidate ID | Length | Occurrences | Files |
|:---|---:|---:|---:|
| `external_span_0cbedbb6866a` | 22 | 38 | 38 |
| `external_span_143f224bc2aa` | 19 | 20 | 20 |
| `external_span_42033b707e4a` | 26 | 19 | 19 |
| `external_span_25ad8f5173d9` | 5 | 14 | 14 |
| `external_span_812c05802876` | 7 | 6 | 6 |
| `external_span_d7a471fd994d` | 19 | 4 | 4 |
| `external_span_5bc37e8ce37a` | 18 | 4 | 4 |
| `external_span_54f17bbc2b7b` | 6 | 4 | 4 |
| `external_span_73dec37dc96e` | 24 | 3 | 3 |
| `external_span_5804cadffbd9` | 20 | 3 | 3 |
| `external_span_759e4e8db701` | 15 | 3 | 3 |
| `external_span_0a050ef2196b` | 10 | 3 | 3 |

## Interpretation

Phase 2Q proves repeated unresolved spans are useful template candidates: the number of handlers with at least 50% phrase coverage increased from 22 to 45.

These templates should not be promoted blindly. The next pass should inspect the external sensitive template file locally, classify which candidates are reusable API/grammar templates versus event-specific constants, and then promote only the reusable ones into the committed template table.

## Output Files

External proof files:

- `external_candidate_templates_sensitive.tsv`
- `external_candidate_templates_sanitized.tsv`
- `coverage_summary.tsv`
- `phrase_sequence.tsv`
- `redacted_views/*.view.txt`
- `manifest.json`
- `RESULT.md`

## Next Move

Classify the 12 external candidates into:

- reusable API/member templates
- reusable grammar fragments
- event-specific constants that should stay external

Then promote only the first two classes.

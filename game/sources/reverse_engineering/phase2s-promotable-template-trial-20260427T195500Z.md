# Phase 2S Promotable Template Trial

Generated: 2026-04-27

## Objective

Trial only the Phase 2R candidates marked `promotable=true`, while keeping extracted candidate text external.

This phase tests the safer promotion subset:

- API/member fragments
- grammar fragments

It excludes the domain/event constants from Phase 2Q.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phase 2R classifier proof:

```text
/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z
```

Phase 2S promotable-template proof:

```text
/tmp/proof_snail_phase2s_promotable_template_trial_20260427T195500Z
```

Script:

```text
src/decode/phase2s_promotable_template_trial.py
```

## Method

The script:

1. Reads `candidate_classification_sensitive.tsv` from the external Phase 2R proof.
2. Selects only rows with `promotable=true`.
3. Builds external-only candidate templates.
4. Runs a coverage pass using base templates plus the promotable subset.
5. Writes sensitive template text only under `/tmp`.
6. Writes sanitized template metadata using IDs, hashes, lengths, counts, and categories.

No candidate template text is committed.

## Result

```text
promotable templates: 8
handlers scanned: 838
phrase sequence rows: 1948
handlers with >=50% phrase coverage: 36
max coverage pct: 69.33
solved: false
```

Coverage comparison:

| Phase | Candidate Set | >=50% Coverage Handlers | Max Coverage |
|:---|:---|---:|---:|
| 2N/2M | committed base templates | 22 | 69.33% |
| 2Q | 12 external candidates | 45 | 69.33% |
| 2S | 8 promotable external candidates | 36 | 69.33% |

## Sanitized Promotable Set

| Promotable ID | Length | Occurrences | Files | Category |
|:---|---:|---:|---:|:---|
| `promotable_span_0cbedbb6866a` | 22 | 38 | 38 | `api_member_fragment` |
| `promotable_span_42033b707e4a` | 26 | 19 | 19 | `api_member_fragment` |
| `promotable_span_d7a471fd994d` | 19 | 4 | 4 | `api_member_fragment` |
| `promotable_span_25ad8f5173d9` | 5 | 14 | 14 | `grammar_fragment` |
| `promotable_span_812c05802876` | 7 | 6 | 6 | `grammar_fragment` |
| `promotable_span_54f17bbc2b7b` | 6 | 4 | 4 | `grammar_fragment` |
| `promotable_span_5bc37e8ce37a` | 18 | 4 | 4 | `grammar_fragment` |
| `promotable_span_0a050ef2196b` | 10 | 3 | 3 | `grammar_fragment` |

## Interpretation

The stricter promotable subset keeps most of the coverage benefit while removing event/domain constants from the promotion path.

This is still not full source reconstruction. The candidate templates are alphanumeric spans, not punctuation-complete Lua. The next useful pass is a conflict-aware overlay run that treats promotable templates separately from base templates and reports whether any selected spans overlap or create coverage ambiguity.

## Output Files

External proof files:

- `promotable_templates_sensitive.tsv`
- `promotable_templates_sanitized.tsv`
- `coverage_summary.tsv`
- `phrase_sequence.tsv`
- `redacted_views/*.view.txt`
- `manifest.json`
- `RESULT.md`

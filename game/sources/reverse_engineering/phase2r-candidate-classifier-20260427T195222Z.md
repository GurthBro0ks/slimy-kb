# Phase 2R Candidate Classifier

Generated: 2026-04-27

## Objective

Classify the 12 Phase 2Q external candidate templates into promotion buckets while keeping candidate text external.

This phase does not promote templates into the main decoder. It produces a safer decision ledger for the next pass.

## Inputs

Phase 2Q external-template proof:

```text
/tmp/proof_snail_phase2q_external_template_trial_20260427T160811Z
```

Phase 2R classifier proof:

```text
/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z
```

Script:

```text
src/decode/phase2r_candidate_classifier.py
```

## Method

The script:

1. Reads the external Phase 2Q sensitive candidate template file.
2. Classifies each candidate as API/member, grammar, domain/event constant, or needs review.
3. Marks candidate-promotable rows only when they look reusable.
4. Writes sensitive classification with candidate text to `/tmp`.
5. Writes sanitized classification with hashes/classes/counts only.

No candidate text is committed.

## Result

```text
candidate templates: 12
promotable candidates: 8
api_member_fragment: 3
domain_or_event_constant: 4
grammar_fragment: 5
solved: false
```

## Sanitized Classification

| Candidate ID | Length | Occurrences | Files | Category | Promotable |
|:---|---:|---:|---:|:---|:---|
| `external_span_0cbedbb6866a` | 22 | 38 | 38 | `api_member_fragment` | true |
| `external_span_143f224bc2aa` | 19 | 20 | 20 | `domain_or_event_constant` | false |
| `external_span_42033b707e4a` | 26 | 19 | 19 | `api_member_fragment` | true |
| `external_span_25ad8f5173d9` | 5 | 14 | 14 | `grammar_fragment` | true |
| `external_span_812c05802876` | 7 | 6 | 6 | `grammar_fragment` | true |
| `external_span_d7a471fd994d` | 19 | 4 | 4 | `api_member_fragment` | true |
| `external_span_5bc37e8ce37a` | 18 | 4 | 4 | `grammar_fragment` | true |
| `external_span_54f17bbc2b7b` | 6 | 4 | 4 | `grammar_fragment` | true |
| `external_span_73dec37dc96e` | 24 | 3 | 3 | `domain_or_event_constant` | false |
| `external_span_5804cadffbd9` | 20 | 3 | 3 | `domain_or_event_constant` | false |
| `external_span_759e4e8db701` | 15 | 3 | 3 | `domain_or_event_constant` | false |
| `external_span_0a050ef2196b` | 10 | 3 | 3 | `grammar_fragment` | true |

## Interpretation

The classification gives a safe promotion path:

- API/member and grammar candidates can be trialed in a committed template table.
- Domain/event constants should stay external until manager context proves they are reusable.

The next pass should promote only the 8 candidate-promotable rows into named template IDs, rerun Phase 2L/2M/2O, and verify that coverage improves without adding phrase-local gap conflicts.

## Output Files

External proof files:

- `candidate_classification_sensitive.tsv`
- `candidate_classification_sanitized.tsv`
- `manifest.json`
- `RESULT.md`

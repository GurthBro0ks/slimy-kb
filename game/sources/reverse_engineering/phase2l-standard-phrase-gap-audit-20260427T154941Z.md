# Phase 2L Standard Phrase Gap Audit

Generated: 2026-04-27

## Objective

Expand Phase 2J beyond one-off full-handler contexts by using repeated standard Lua/API phrases whose punctuation is known without requiring full handler source reconstruction.

The audit uses phrases such as:

- `return function(lpc)`
- `EventMgr.fire_event`
- `RankM.setRankInfo`
- `RankM.setMyRank`
- `ME.user.query`
- `Operation.cmd`

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phase 2L phrase-gap proof:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T154941Z
```

Script:

```text
src/decode/phase2l_standard_phrase_gap_audit.py
```

## Method

The script scans the 838 externally pulled small handlers and:

1. Decodes only alphanumeric bytes with the carried-forward table.
2. Finds standard phrase skeletons such as `returnfunctionlpc` and `EventMgrfireevent`.
3. Records raw punctuation/control gaps inside each phrase.
4. Groups gap evidence by phrase, left/right plaintext context, and raw gap display.
5. Emits repeated conflict-free contexts and conflicts.

No raw `.luac` files or full decoded Lua source are committed.

## Result

```text
handlers scanned: 838
phrase occurrences: 1544
gap rows: 3072
context rows: 144
repeated conflict-free contexts: 87
context conflicts: 0
solved: false
```

## Phrase Counts

| Phrase | Occurrences |
|:---|---:|
| `return_function_lpc` | 830 |
| `eventmgr_fire_event` | 663 |
| `me_user_set_ex` | 15 |
| `me_user_query` | 12 |
| `me_user_set_temp` | 8 |
| `rankm_set_rank_info` | 5 |
| `operation_cmd` | 3 |
| `rankm_set_my_rank` | 3 |
| `rankm_get_id_my_task_type` | 2 |
| `taskm_set_week_top` | 2 |
| `topm_set_my_rank` | 1 |

## Key Finding

The standard phrase audit produced **zero context conflicts**, but it also showed the raw gap encoding is polymorphic.

Example: inside `return function(lpc)`, the plaintext gap between `return` and `function` is always a space, but many raw gap bytes appear in that same role across files. Inside `EventMgr.fire_event`, the plaintext dot and underscore roles are also stable by phrase context while the raw gap byte varies.

This means the useful model is:

```text
phrase/local grammar context -> plaintext gap
```

not:

```text
raw punctuation byte -> plaintext punctuation byte
```

## Safe Takeaway

Phase 2L is strong evidence that source reconstruction should proceed by grammar phrase templates and local contexts, not by a global punctuation substitution table.

Do not patch `scripts/decrypt_handler.py` with raw punctuation mappings. The next decoder should:

- locate alphanumeric skeletons
- apply known phrase templates
- emit unresolved gaps where phrase context is unknown
- keep a conflict ledger

## Output Files

External proof files:

- `phrase_occurrences.tsv`
- `phrase_counts.tsv`
- `gap_evidence.tsv`
- `context_gap_summary.tsv`
- `context_gap_repeated_conflict_free.tsv`
- `context_gap_conflicts.tsv`
- `manifest.json`
- `RESULT.md`

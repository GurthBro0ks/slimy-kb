# Phase 2N Template Expansion

Generated: 2026-04-27

## Objective

Expand the Phase 2L/2M phrase-template set using only stable member-access and API-call anchors observed in small handler skeletons.

This phase does not promote punctuation bytes, reconstruct full Lua source, or commit raw handler data.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

New Phase 2L phrase-gap proof:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z
```

New Phase 2M coverage proof:

```text
/tmp/proof_snail_phase2m_phrase_coverage_20260427T155912Z
```

Scripts:

```text
src/decode/phase2l_standard_phrase_gap_audit.py
src/decode/phase2m_phrase_coverage.py
```

## Template Changes

Added phrase templates:

- `TaskM.setWeekTopMyRank`
- `ArenaM.setTop`
- `ItemM.refreshItem`
- `lpc.id`
- `lpc.rank`
- `lpc.list`
- `lpc.type`
- `lpc.start`
- `lpc.group`
- `lpc.classid`
- `lpc.amount`

These are phrase/member-access templates only. They are not whole-statement source claims.

## Results

### Phase 2L Gap Evidence

```text
handlers scanned: 838
phrase occurrences: 1772
gap rows: 3339
context rows: 252
repeated conflict-free contexts: 146
context conflicts: 0
solved: false
```

Previous Phase 2L baseline:

```text
phrase occurrences: 1544
gap rows: 3072
context rows: 144
repeated conflict-free contexts: 87
context conflicts: 0
```

### Phase 2M Coverage

```text
handlers scanned: 838
phrase sequence rows: 1772
handlers with >=50% phrase coverage: 22
max coverage pct: 69.33
solved: false
```

Previous Phase 2M baseline:

```text
phrase sequence rows: 1544
handlers with >=50% phrase coverage: 6
max coverage pct: 54.84
```

## Top Coverage Examples

| File | Phrase occurrences | Coverage |
|:---|---:|---:|
| `msg_item.luac` | 4 | 69.33% |
| `msg_arena_top.luac` | 4 | 61.97% |
| `msg_week_task_rank.luac` | 10 | 61.88% |
| `msg_top_rank.luac` | 4 | 61.76% |
| `msg_new_si.luac` | 3 | 57.35% |
| `msg_week_task_myrank.luac` | 10 | 56.41% |

Example external redacted view for `msg_top_rank.luac`:

```text
<gap:23> <return_function_lpc> <topm_set_my_rank> <lpc_id> <lpc_rank> <gap:3>
```

This remains a redacted coverage view, not decoded source.

## Interpretation

Phase 2N confirms the safer next decoder path:

```text
known phrase/member-access template -> local plaintext gap evidence
```

not:

```text
raw punctuation byte -> global punctuation mapping
```

The expanded templates improved coverage and produced no context conflicts. The next useful move is to add a redacted template-overlay decoder that emits phrase IDs, known local gaps, and unresolved spans while keeping every output tied to input hashes and conflict ledgers.

## Output Files

External proof files:

- `/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z/phrase_counts.tsv`
- `/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z/context_gap_repeated_conflict_free.tsv`
- `/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z/context_gap_conflicts.tsv`
- `/tmp/proof_snail_phase2m_phrase_coverage_20260427T155912Z/coverage_summary.tsv`
- `/tmp/proof_snail_phase2m_phrase_coverage_20260427T155912Z/redacted_views/*.view.txt`

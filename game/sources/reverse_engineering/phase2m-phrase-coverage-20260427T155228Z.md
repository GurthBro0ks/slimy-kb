# Phase 2M Phrase Template Coverage

Generated: 2026-04-27

## Objective

Measure how much of each small handler can be represented by the proven phrase templates from Phase 2L, without writing full decoded Lua source to the repo.

## Inputs

External small-handler raw proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Phase 2M phrase coverage proof:

```text
/tmp/proof_snail_phase2m_phrase_coverage_20260427T155228Z
```

Script:

```text
src/decode/phase2m_phrase_coverage.py
```

## Method

The script:

1. Reads external small-handler originals.
2. Builds alphanumeric skeletons using the carried-forward mapping.
3. Finds standard phrase templates from Phase 2L.
4. Computes phrase-template coverage over each handler skeleton.
5. Writes external redacted views using only phrase IDs and gap lengths.

No full decoded handler source is committed.

## Result

```text
handlers scanned: 838
phrase sequence rows: 1544
handlers with >=50% phrase coverage: 6
max coverage pct: 54.84
solved: false
```

## Top Coverage Examples

| File | Phrase occurrences | Coverage |
|:---|---:|---:|
| `msg_say.luac` | 2 | 54.84% |
| `msg_quest.luac` | 2 | 51.52% |
| `msg_car_drop.luac` | 2 | 50.75% |
| `msg_tour_end.luac` | 2 | 50.75% |
| `msg_word.luac` | 2 | 50.00% |
| `msg_new_si.luac` | 2 | 50.00% |

Example external redacted view for `msg_top_rank.luac`:

```text
<gap:23> <return_function_lpc> <topm_set_my_rank> <gap:15>
```

This is intentionally not source reconstruction. It is a coverage/debug view for template expansion.

## Interpretation

Phase 2M confirms that phrase templates are useful but incomplete. Most small handlers still need more templates for manager-specific calls, event constants, table field access, and function endings.

The next useful step is adding more standard templates from top candidates, especially:

- `EventMgr.fire_event(CONSTANT, lpc)`
- `TopM.setMyRank(lpc.id, lpc.rank)`
- `RankM.setMyRank(CONSTANT, lpc.rank)`
- `RankM.setRankInfo(CONSTANT, start, lpc.list)`
- `ME.user.setEx(...)`

## Output Files

External proof files:

- `coverage_summary.tsv`
- `phrase_sequence.tsv`
- `redacted_views/*.view.txt`
- `manifest.json`
- `RESULT.md`

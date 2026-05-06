# Phase 2E Rank / Group / Arena Field-Flow Report

Generated: 2026-04-26

## Scope

Analyze 10 high-value rank/group/arena/top handlers pulled in Phase 2D and extract field-flow signals from decoded printable views.

## Inputs

Phase 2D target inventory proof:

```text
/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z
```

Phase 2E proof:

```text
/tmp/proof_snail_phase2e_field_flow_20260426T210812Z
```

## Result

```text
FIELD_FLOW_CANDIDATES_READY
```

Handlers analyzed: 10.

Raw handlers remain external only and were not copied into Git.

## Method

Each handler was decoded with the Phase 2B alphanumeric mapping. A normalized readable view mapped printable separator-like characters to `_` for analyst navigation only.

This is field-flow reconnaissance, not full Lua bytecode decompilation.

## High-Value Handler Signals

| Protocol | Size | Main signal | Observed fields/constants |
|---|---:|---|---|
| `misc@msg_arena_query_rank_score` | 736 | `ME.user.setEx`, bonus notify path | `lpc.score`, `lpc.add`, `lpc.rank`, `ARENA_SCORE` |
| `misc@msg_arena_top_query` | 214 | `EventMgr.fire_event` | `ARENATOP_QUERY`, passes whole `lpc` |
| `misc@msg_group_myrank` | 153 | `RankM.setMyRank` | `RANK_ID_GROUP`, `lpc.rank` |
| `misc@msg_group_rank` | 173 | `RankM.setRankInfo` | `RANKID_GROUP`, `lpc.list` |
| `misc@msg_group_war_group_myrank` | 190 | `RankM.setMyRank` | `RANK_ID_GROUP_WAR_GROUP`, `lpc.rank` |
| `misc@msg_group_war_group_rank` | 257 | `RankM.setRankInfo` | `lpc.is_top`, `lpc.start`, `lpc.list`, group-war rank IDs |
| `misc@msg_group_war_member_rank` | 2969 | `GroupM`, `GroupWarM`, `RankM.setRankInfo` | `lpc.data`, `data.list`, member `rid`, kit/join-time enrichment |
| `misc@msg_top_rank` | 130 | `TopM.setMyRank` | `lpc.id`, `lpc.rank` |
| `misc@msg_week_task_myrank` | 347 | `TaskM.setWeekTopMyRank`, `EventMgr.fire_event` | `lpc.type`, `lpc.rank`, `MY_RANK_UPDATED` |
| `misc@msg_week_task_rank` | 306 | `RankM.setRankInfo`, `TaskM.setWeekTop` | `lpc.type`, `lpc.start`, `lpc.list` |

## Operational Takeaways

- Group rank path is centered on `RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)`.
- Group personal rank path is centered on `RankM.setMyRank(RANK_ID_GROUP, lpc.rank)`.
- Arena top query forwards the whole `lpc` through `EventMgr.fire_event(ARENATOP_QUERY, lpc)`.
- Arena rank score writes score/rank state onto `ME.user` and may trigger a UI bonus notification when `lpc.add > 0`.
- Group war rank handlers split into group rank, group my-rank, and member rank variants.
- Week task rank handlers route through `RankM.getIdMyTaskType(lpc.type)` and update `RankM` / `TaskM`.

## Proof Artifacts

Full external report:

```text
/tmp/proof_snail_phase2e_field_flow_20260426T210812Z/reports/field_flow_report.md
```

TSV summary:

```text
/tmp/proof_snail_phase2e_field_flow_20260426T210812Z/out.tsv
```

Decoded printable views:

```text
/tmp/proof_snail_phase2e_field_flow_20260426T210812Z/decoded/
```

## Caveats

- This is not exact source reconstruction.
- Separator normalization is for readability only.
- Some constants remain garbled where unresolved `r` or punctuation/noise affects the printable stream.
- A bytecode-aware Lua decompiler would be needed for stronger control-flow and table-structure proof.

## Next Move

Create a clean rank/group/arena data-flow map that links:

- protocol name
- handler path/hash
- primary manager call
- consumed `lpc` fields
- written local state
- likely analytics/API relevance

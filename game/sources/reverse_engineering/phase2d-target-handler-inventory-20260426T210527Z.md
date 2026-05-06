# Phase 2D Target Handler Inventory Report

Generated: 2026-04-26

## Scope

Triage the 8 unmatched protocol candidates from Phase 2C and build a focused rank/group/arena/top handler inventory from the live device.

## Inputs

Phase 2C proof:

```text
/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z
```

Phase 2D proof:

```text
/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z
```

## Result

```text
TARGET_HANDLER_INVENTORY_READY
```

Counts:

| Metric | Count |
|---|---:|
| Unmatched candidates triaged | 8 |
| Unmatched candidates promoted | 0 |
| Target handlers requested | 119 |
| Target handlers pulled and hashed | 119 |
| Pull errors | 0 |

Raw `.luac` handlers remain only in the external proof directory and were not copied into Git.

## Unmatched Candidate Triage

No unmatched candidate was promoted. The nearest live handler names are similarity hints only.

| Candidate | Strong nearest live hint | Similarity | Status |
|---|---|---:|---|
| `misc@msg*activity,turnplate1{action` | `misc@msg_activity_turnplate3_action` / `misc@msg_activity_turnplate2_action` | 0.968 | no exact live handler |
| `misc@msg.anniversary4+action` | `misc@msg_anniversary5_action` / `misc@msg_anniversary2_action` | 0.960 | no exact live handler |
| `misc@msg}group*war(special1}action` | `misc@msg_group_war_special5_action` / `special4` / `special3` / `special2` | 0.966 | no exact live handler |
| `misc@msg;mid{autumn2023=action` | `misc@msg_mid_autumn2022_action` / `mid_autumn2021_action` | 0.962 | no exact live handler |
| `misc@msg)shuangdan2023|action` | `misc@msg_shuangdan2022_action` / `shuangdan2021_action` | 0.962 | no exact live handler |
| `misc@msg*shuangdan2023_ice;bonus` | `misc@msg_shuangdan2021_ice_bonus` | 0.964 | no exact live handler |
| `misc@msg;shuangdan2023*icestrike` | `misc@msg_shuangdan2021_ice_strike` | 0.966 | no exact live handler |
| `misc@msg*special1build(tower` | `misc@msg_special3_build_tower` | 0.960 | no exact live handler |

## Inventory Categories

The 119 target handlers were grouped into:

- arena
- group/rank
- group war
- top/score/other

Full external inventory:

```text
/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z/reports/rank_group_handler_inventory.md
```

Hash list:

```text
/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z/out/rank_group_handler_hashes.sha256
```

## High-Value Pulled Handlers

| Protocol | Size | SHA256 |
|---|---:|---|
| `misc@msg_arena_query_rank_score` | 736 | `ed3b2a4cc29335413bdcbf6d348ec74203aaf1fa9ae61fa14f74ef5b05d3052b` |
| `misc@msg_arena_top_query` | 214 | `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37` |
| `misc@msg_group_myrank` | 153 | `5cb4c8b32f3774581adbe76bfd1cd8b4be48a4027aecf8de0e8e59d709cbaa7a` |
| `misc@msg_group_rank` | 173 | `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9` |
| `misc@msg_group_war_group_myrank` | 190 | `ddf3d619665674bd65efbb822e3818843a3ed5d2bc8417dfd2e9db49c5916bb8` |
| `misc@msg_group_war_group_rank` | 257 | `0dc54e5f7616aa47d723928b32725383fc0c5e66a7319fccfbbb155a23a0672f` |
| `misc@msg_group_war_member_rank` | 2969 | `4509e109fb5af43f04c912455958f78a3c9c42196bb38ab68df6d8805e5ee5c9` |
| `misc@msg_top_rank` | 130 | `7525395f1048635095baa80a173aa05a214b671e66895b6afdfe41e6aef8264a` |
| `misc@msg_week_task_myrank` | 347 | `138f36a8e7c76101897c3a558eeb79269f9f6ece04eff984f9fa797e43f0f4c3` |
| `misc@msg_week_task_rank` | 306 | `b2c822e3343c16c31125e6dbc01bab71af120a0c5d9baff9552d95553f3ff2c6` |

## Next Move

Analyze decoded structure of the 10 high-value pulled handlers from the external proof directory and produce a rank/group/arena field-flow report.

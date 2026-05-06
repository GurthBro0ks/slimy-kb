# Phase 2G Manager Trace From Fresh ADB Originals

Generated: 2026-04-27

## Objective

Restart the Android target after laptop power loss, reacquire the manager and high-value handler originals from the running app, and continue the Phase 2B/2F cipher process without mutating source evidence.

## Runtime State

- ADB device: `emulator-5554 device`
- Package process: `com.qcplay.snail.android.na`
- Confirmed PID after relaunch: `7211`
- Confirmed top activity after permission prompt: `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`

## Proof Directory

External proof only:

```text
/tmp/proof_snail_phase2g_manager_trace_20260427T132529Z
```

Raw `.luac` originals and full decoded Lua outputs remain outside the repo.

## Inputs Pulled Read-Only

All pulled originals were set to mode `444`.

| File | SHA256 | Size |
|:---|:---|---:|
| `game_module__RankM.luac` | `25adf97363f02dc8d24547f710c7d97227a449c8a77b41d893f5290385897d64` | 11621 |
| `game_module__TopM.luac` | `ec0050a86539ae1ab1eacb23753fdbbf183aa38f591e5dfe9857ba33046f5e73` | 6636 |
| `game_module__TaskM.luac` | `26d958b760e1323db43ead574e46f7293d1e77be4a3d2a4ed2cb60354c39ea45` | 85434 |
| `game_module__GroupM.luac` | `b8769c9f56729e7d73a0bd9ee2700f30ac81c271883c5ed7667e44e34f2edd52` | 35305 |
| `game_module__GroupWarM.luac` | `c804c085291e4198fdd4b9ef13e4a9a3c9a239182caf149057331d256e788c48` | 54036 |
| `game_module__EventM.luac` | `c4def575f55c0648c95f9519ebe6aefa2f35e74535524dcac7d39e3a602efbc1` | 11078 |
| `game_cmd_misc__msg_group_rank.luac` | `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9` | 173 |
| `game_cmd_misc__msg_group_war_member_rank.luac` | `4509e109fb5af43f04c912455958f78a3c9c42196bb38ab68df6d8805e5ee5c9` | 2969 |
| `game_cmd_misc__msg_week_task_rank.luac` | `b2c822e3343c16c31125e6dbc01bab71af120a0c5d9baff9552d95553f3ff2c6` | 306 |
| `game_cmd_misc__msg_top_rank.luac` | `7525395f1048635095baa80a173aa05a214b671e66895b6afdfe41e6aef8264a` | 130 |
| `game_cmd_misc__msg_arena_top_query.luac` | `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37` | 214 |

## Cipher Status Correction

The Phase 2F POC was useful but overclaimed completeness. Re-running `scripts/decrypt_handler.py` against fresh originals shows:

- the files are still consistent with encrypted/minified Lua source, not Lua bytecode
- the current table recovers many identifiers and manager calls
- punctuation/operators and non-ASCII comments are not cleanly decoded
- the current script must be treated as a partial analyst view, not exact source reconstruction

This means Phase 2B is not a fully solved byte-for-byte cipher. It is good enough for manager-call tracing, but not enough to publish exact Lua source or exact punctuation recovery.

## Manager Trace Findings

### `RankM.setRankInfo`

The readable trace shows that `RankM.setRankInfo(rankId, start, list)` treats `list` as an opaque array of entries. It:

- defaults `start` to `0`
- initializes `cacheData[rankId]`
- preserves placeholder entries before `start`
- copies each `info` entry from `list` into `cacheData[rankId][start + index]`
- calls rank reorder/update paths
- records `cacheTime[rankId]`
- fires rank update events

No nested `lpc.list` entry schema is defined inside `RankM.setRankInfo`; the manager stores server-provided entry tables mostly as received.

### `RankM.getRankInfo`

The readable trace shows `getRankInfo(rankId, start)` returns cached rank data, either copied from the whole rank list or sliced from `start`. It does not add schema fields.

### `RankM.setMyRank`

The readable trace shows `setMyRank(rankId, rank)` writes `cacheMyRankData[rankId] = rank` and fires the my-rank update event. It does not unpack nested rank objects.

### `msg_group_war_member_rank`

This handler is more useful than the generic rank manager for payload shape. The readable trace shows:

- input is `lpc.data`
- primary list is `data.list`
- each server entry uses at least `rid`
- handler builds a `rids` list from `info.rid`
- handler consults `GroupM.getMyGroup()` and local group member data
- client-side enrichment may add or update:
  - `kit`
  - `joinTime`
  - `isNew`
  - `isClientAdd`
  - `isShowKit`
- handler sorts client-added `others`
- handler appends `others` into `data.list`
- handler forwards final `data.list` into `RankM.setRankInfo(RANK_ID_GROUP_WAR_MEMBER, 0, data.list)`
- handler forwards `data.rank` into `RankM.setMyRank(RANK_ID_GROUP_WAR_MEMBER, data.rank)`

This is the strongest current non-capture evidence for the `group_war_member_rank` payload path.

## Current Answer on `lpc.list` Schema

For generic rank routes such as `msg_group_rank`, the exact nested entry schema is still not defined in the handler or `RankM`. The client stores and forwards table entries by rank ID.

For `group_war_member_rank`, the client-visible entry fields include at least `rid`, with client enrichment around `kit`, join time/new-member status, and display state. Full server-only fields still require either a cleaner cipher table, runtime table dump, or a packet capture from owned account/device data.

## Next Move

Build a conflict-reporting punctuation solver instead of treating the Phase 2F table as complete. Use anchored handler comments, Lua syntax anchors, and live file paths, then emit:

- byte offset
- encrypted byte
- proposed plaintext byte
- source anchor
- conflict records

Do not normalize punctuation into underscores and call it exact source.

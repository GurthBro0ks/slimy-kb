# Rank, Group, and Arena Data-Flow Map

Generated: 2026-04-26

## Overview

This map correlates the high-value rank, group, and arena handler protocols identified in Phase 2D/2E with their parsed `lpc` (Lua Protocol Call) payloads, internal state-manager calls, and likely telemetry/analytics value. 

The goal is to safely identify the data flow for competitive and cooperative progression without requiring exact byte-reconstruction of the original proprietary script.

## Core Data-Flow Map

| Protocol Name | Handler Hash (SHA256) | Primary Manager Call | Consumed LPC Fields | Likely Analytics/API Relevance |
|:---|:---|:---|:---|:---|
| `misc@msg_arena_query_rank_score` | `ed3b2a...052b` | `ME.user.setEx`<br>(bonus notify path) | `lpc.score`<br>`lpc.add`<br>`lpc.rank`<br>`ARENA_SCORE` | Tracks a player's arena score, rank position, and additive changes (wins/losses). Strong indicator for competitive progression events and win-rate analysis. |
| `misc@msg_arena_top_query` | `8cec7a...0f37` | `EventMgr.fire_event(ARENATOP_QUERY, lpc)` | Passes whole `lpc` | Request/response for the current top arena ladder. Useful for tracking shard meta, top-tier loadouts, or power-creep across top players. |
| `misc@msg_group_myrank` | `5cb4c8...aa7a` | `RankM.setMyRank(RANK_ID_GROUP, lpc.rank)` | `lpc.rank` | Tracks the specific user's rank within their guild/group. Good for daily engagement metrics and guild-activity contribution. |
| `misc@msg_group_rank` | `a32247...22a9` | `RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)` | `lpc.list` | Guild/Group leaderboard data. Likely contains the full list of group members and their contribution scores. Essential for guild telemetry. |
| `misc@msg_group_war_group_myrank` | `ddf3d6...6bb8` | `RankM.setMyRank(RANK_ID_GROUP_WAR_GROUP, lpc.rank)` | `lpc.rank` | User's individual performance/ranking within an active Clan War / Group War. High value for competitive guild event participation. |
| `misc@msg_group_war_group_rank` | `0dc54e...672f` | `RankM.setRankInfo(...)` | `lpc.is_top`<br>`lpc.start`<br>`lpc.list`<br>group-war rank IDs | Server-wide or shard-wide leaderboard for guilds in Clan War. Crucial for cross-guild power tracking and weekly GvG meta analysis. |
| `misc@msg_group_war_member_rank` | `4509e1...e5c9` | `GroupM`<br>`GroupWarM`<br>`RankM.setRankInfo` | `lpc.data`<br>`data.list`<br>member `rid`<br>`kit`/join-time enrichment | Contains detailed per-member performance in Clan War, including loadouts (`kit`), account age/join-time, and scores. Maximum value for detailed player-level event analytics. |
| `misc@msg_top_rank` | `752539...264a` | `TopM.setMyRank(lpc.id, lpc.rank)` | `lpc.id`<br>`lpc.rank` | Generic "Top Rank" update. Likely handles server-wide total power, progression, or event-specific general ladders depending on `lpc.id`. |
| `misc@msg_week_task_myrank` | `138f36...f4c3` | `TaskM.setWeekTopMyRank`<br>`EventMgr.fire_event(MY_RANK_UPDATED)` | `lpc.type`<br>`lpc.rank` | Tracks player's percentile or exact rank in the rotating Weekly Event (e.g., Offering, Wish Machine, Lottery). Huge monetization and hoarding telemetry signal. |
| `misc@msg_week_task_rank` | `b2c822...f2c6` | `RankM.setRankInfo`<br>`TaskM.setWeekTop` | `lpc.type`<br>`lpc.start`<br>`lpc.list` | The global top ladder for the rotating Weekly Event. Shows what the top spenders/hoarders are pushing in terms of event score. |

## Operational Takeaways

1. **State Isolation**: Subsystems are fairly decoupled. `RankM` handles the generic sorting and state lookup (`RankM.setRankInfo`, `RankM.setMyRank`), while subsystem managers (`GroupWarM`, `TaskM`) and the event bus (`EventMgr`) handle business logic branching and UI notification.
2. **Batch Updates**: Most lists (guild members, top ranks) are passed in batches (`lpc.list` or `data.list`), meaning polling these specific handlers yields dense analytics payloads.
3. **Enrichment**: Handlers like `msg_group_war_member_rank` show client-side enrichment (`kit`, `join-time`) which points to payload objects containing deep equipment/relic/snail-stat JSON strings.

## Caveats

- This mapping relies on decoded printable-view signals.
- Full nested object schema inside `lpc.list` or `lpc.data` remains unmapped without packet captures or bytecode de-serialization.
- Hash values correspond to the specific event version captured on `2026-04-26` and are expected to drift with major app updates.

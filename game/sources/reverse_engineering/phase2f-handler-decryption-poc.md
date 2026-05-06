# Phase 2F Handler Decryption Proof of Concept

Generated: 2026-04-26

## 2026-04-27 Erratum

Phase 2G re-ran the decryptor against fresh ADB originals after restarting the game and found that this report overclaims the state of the cipher table.

The core discovery still stands: these `.luac` files are not normal Lua bytecode and are compatible with encrypted/minified Lua source. However, `scripts/decrypt_handler.py` is only a partial analyst-view decoder. It recovers useful identifiers and manager calls, but punctuation/operators and non-ASCII comments are not clean enough to claim exact original Lua source.

Use the Phase 2G report as the current truth:

```text
reports/phase2g-manager-trace-20260427T132529Z.md
```

## Objective

Determine the safest and most effective method to extract the nested `lpc.list` schema for high-value rank/group/arena handlers. Evaluate whether to use a bytecode-aware Lua decompiler (`unluac`) or a PCAP capture.

## Method & Execution

1. Investigated the structure of `msg_group_rank.luac` and `msg_arena_top_query.luac` from the `originals/tmp-imports` directory.
2. Compiled and ran `unluac` on `msg_group_rank.luac`. It failed with: `The input file does not have the signature of a valid Lua file.`
3. Wrote a Python decryptor (`scripts/decrypt_handler.py`) using the current carried-forward substitution table from Phase 2B.
4. Partially decoded the raw `msg_group_rank.luac` and `msg_arena_top_query.luac` bytes well enough to recover manager calls.

## Findings

**CRITICAL DISCOVERY**: The `.luac` files in the Super Snail `update_res/src/game/cmd` directory are **not standard Lua bytecode**. They appear to be minified Lua source encrypted with a custom byte-substitution layer and a 3-byte binary header (`\x14\x15\x16`).

Because they are not standard bytecode, decompilers like `unluac` or `luadec` are incompatible. Exact source recovery still requires finishing the punctuation/operator side of the cipher table.

### POC Decryption Output

The snippets below were the intended normalized readability target, not byte-for-byte proof of exact source.

**`msg_group_rank.luac` normalized target**:
```lua
-- msg_group_rank
-- Create by chenx 2023-06
return function(lpc)
    RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)
end
```

**`msg_arena_top_query.luac` normalized target**:
```lua
-- msg_arena_top_query
-- Create by weism
return function(lpc)
    EventMgr.fire_event(ARENATOP_QUERY, lpc)
end
```

## Conclusion on `lpc.list` Schema

Because these handlers act as simple proxy routers, **the `lpc.list` schema is not defined or destructured inside the handler file itself**. The payload is passed opaquely to `RankM` or `EventMgr`.

To map the nested properties of `lpc.list` without network captures, we must extract and decrypt the manager script (e.g., `RankM.luac`) from the live device and trace the `setRankInfo` function.

## Next Steps

1. Extract core manager files (`RankM.luac`, `TopM.luac`, `EventMgr.luac`) from the live device using `adb`.
2. Apply `scripts/decrypt_handler.py` to reveal the source code of the manager scripts.
3. Trace the internal field usage of `lpc.list` inside `setRankInfo` to reconstruct the data schema.
4. Build a conflict-reporting punctuation solver before claiming exact source reconstruction.

# Phase 2B ADB Audit + Partial Solve Report

Generated: 2026-04-26

## Scope

Relaunch the Android emulator/game, reacquire target `.luac` originals from the running app, run the Phase 2B audit, and record any evidence-backed solve progress.

## Emulator / Game Relaunch

AVD:

```text
snail-recon
```

ADB device:

```text
emulator-5554	device
```

Package:

```text
com.qcplay.snail.android.na
```

Activity:

```text
org.cocos2dx.lua.AppActivity
```

## Fresh ADB Proof

Fresh ADB proof directory:

```text
/tmp/proof_snail_protocol_adb_20260426T204437Z
```

Pulled from:

```text
/data/data/com.qcplay.snail.android.na/files/update_res/src/game/cmd/list.luac
/data/data/com.qcplay.snail.android.na/files/update_res/src/game/cmd/misc/msg_group_rank.luac
/data/data/com.qcplay.snail.android.na/files/update_res/src/game/cmd/misc/msg_arena_top_query.luac
```

The pulled originals were made read-only.

| File | Size | SHA256 | Mode |
|---|---:|---|---|
| `list.luac` | 32597 | `122b776932fdb0e5c85b201d72aa722267b5b13162394e4610199b1235ac6f67` | `444` |
| `msg_group_rank.luac` | 173 | `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9` | `444` |
| `msg_arena_top_query.luac` | 214 | `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37` | `444` |

## Audit Proof

Audit proof directory:

```text
/tmp/proof_snail_phase2b_cipher_audit_20260426T204455Z
```

Audit result:

```text
AUDIT_ONLY
```

Reviewed:

- 3 read-only originals
- 962 protocol/string candidates

Observed unresolved alphanumeric counts in the protocol candidate view:

| Char | Count |
|---|---:|
| `6` | 0 |
| `H` | 0 |
| `S` | 1 |
| `b` | 332 |
| `d` | 360 |
| `r` | 1010 |

Top unresolved punctuation/symbol counts:

| Symbol | Count |
|---|---:|
| `:` | 163 |
| `{` | 162 |
| `=` | 158 |
| `}` | 153 |
| space | 151 |
| `;` | 148 |
| `)` | 148 |
| `-` | 139 |
| `%` | 139 |
| `(` | 138 |
| `,` | 137 |
| `*` | 133 |
| `+` | 132 |
| `|` | 124 |
| `#` | 120 |

## Partial Solve Proof

Partial solve proof directory:

```text
/tmp/proof_snail_phase2b_cipher_solve_20260426T204627Z
```

Status:

```text
PARTIAL_HANDLER_ALNUM_IMPROVED
```

New mappings promoted:

| Encoded | Decoded | Evidence anchor |
|---|---|---|
| `H` | `Y` | `msg_arena_top_query.luac`; anchored by `ARENATOP_QUERY` |
| `S` | `K` | `msg_group_rank.luac`; anchored by `RANKID_GROUP` |
| `b` | `Q` | `msg_arena_top_query.luac`; anchored by `ARENATOP_QUERY` |
| `d` | `T` | `msg_arena_top_query.luac`; anchored by `ARENATOP_QUERY` |
| `6` | `6` | `msg_group_rank.luac`; anchored by `2023-06` header date |

## Not Solved

- `r` remains unresolved.
- Punctuation/symbol mappings remain unresolved.
- These mappings improve handler alphanumeric decode only; they do not resolve the protocol list punctuation layer.
- No raw originals were modified.
- No normalized protocol strings were promoted as exact truth.

## Next Move

Build a punctuation-focused Phase 2C solver that uses anchored protocol/path evidence and emits conflict records instead of forcing a bijective table.

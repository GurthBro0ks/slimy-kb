# Phase 2I Raw Skeleton Transform Audit

Generated: 2026-04-27

## Objective

Continue the cipher work after Phase 2H by avoiding byte-by-byte punctuation assumptions. This audit aligns known handler bodies by proven alphanumeric skeleton, then records the raw encrypted punctuation/control gaps between matched alphanumeric bytes.

## Inputs

Phase 2G manager trace proof:

```text
/tmp/proof_snail_phase2g_manager_trace_20260427T132529Z
```

Phase 2I transform proof:

```text
/tmp/proof_snail_phase2i_skeleton_transform_20260427T152041Z
```

Script:

```text
src/decode/phase2i_skeleton_transform_audit.py
```

## Method

The audit:

1. Reads Phase 2G originals from `/tmp`.
2. Strips the 3-byte header when present.
3. Decodes only known alphanumeric bytes using the carried-forward alphanumeric table.
4. Allows unmapped ASCII alphanumerics to pass through for skeleton search only.
5. Finds known handler bodies by alphanumeric-only skeleton.
6. Records each raw byte gap between adjacent matched alphanumeric bytes.
7. Compares each raw gap to the expected plaintext gap.

This is a transform audit, not a source decoder.

## Result

```text
anchors checked: 4
anchors missing: 0
gap rows: 59
raw gap conflicts: 10
solved: false
```

All four target anchors were found:

| Anchor | File | Status |
|:---|:---|:---|
| `group_rank_body` | `game_cmd_misc__msg_group_rank.luac` | found |
| `arena_top_body` | `game_cmd_misc__msg_arena_top_query.luac` | found |
| `top_rank_body` | `game_cmd_misc__msg_top_rank.luac` | found |
| `week_task_rank_call` | `game_cmd_misc__msg_week_task_rank.luac` | found |

## Conflict Summary

The same raw gap display produced multiple plaintext gap candidates:

| Raw gap | Plain gap candidates |
|:---|:---|
| `#` | `(`, `.` |
| `(` | `.`, space |
| `*` | `(`, `_` |
| `,` | `(`, `.` |
| `:` | `(`, `.` |
| `;` | `.`, space |
| space | `(`, `.`, space, `_` |
| newline | empty, `.` |
| carriage return | empty, space |
| `{` | `(`, space |

This is stronger than Phase 2H because it aligns by alphanumeric skeleton rather than direct punctuation positions. The conclusion is the same: the punctuation/control layer is not a safe global monoalphabetic substitution table under the current assumptions.

## Working Interpretation

The current evidence suggests a multi-layer source transform:

- alphanumeric identifier bytes are mostly stable under the carried-forward substitution table
- punctuation/control bytes encode formatting, operators, separators, and possibly stripped/inserted whitespace
- raw newlines and carriage returns may be layout/control artifacts, not direct plaintext newlines
- exact Lua source recovery needs a context/run-level transform model, not a one-byte punctuation patch

## Next Move

Build a run-level normalizer that learns gap transforms by context:

- left/right alphanumeric token
- raw gap byte sequence
- expected Lua grammar role
- conflict count

Only promote transforms that remain conflict-free across multiple anchors. Keep all full decoded Lua in `/tmp` proof directories until the transform model is proven.

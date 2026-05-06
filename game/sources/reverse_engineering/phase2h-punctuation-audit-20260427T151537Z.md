# Phase 2H Punctuation Conflict Audit

Generated: 2026-04-27

## Objective

Continue the Phase 2B/2G cipher work by testing whether the remaining punctuation/operator layer can be safely promoted as a single byte-to-byte substitution table.

This pass is read-only and fail-closed:

- no originals modified
- no raw `.luac` files committed
- no full decoded proprietary source committed
- no punctuation normalization presented as exact source

## Inputs

Phase 2G manager trace proof:

```text
/tmp/proof_snail_phase2g_manager_trace_20260427T132529Z
```

Phase 2H audit proof:

```text
/tmp/proof_snail_phase2h_punctuation_audit_20260427T151537Z
```

Script:

```text
src/decode/phase2h_punctuation_audit.py
```

## Method

The audit uses short known plaintext anchors from high-confidence handler traces:

- `msg_group_rank` handler body prefix
- `msg_arena_top_query` event dispatch prefix
- `msg_top_rank` top-rank update prefix

For each anchor, the script records:

- source file
- byte offset in the encrypted body
- encrypted byte
- expected plaintext byte
- whether existing alphanumeric mapping agrees
- punctuation candidate or conflict status

It emits TSV evidence and conflict files under the external proof directory.

## Result

```text
anchor rows: 103
punctuation candidates: 12
punctuation conflicts: 3
alphanumeric conflicts: 0
solved: false
```

The carried-forward alphanumeric table passed all anchor checks in this narrow test. The punctuation/operator layer did not.

## Conflict Summary

The audit found conflicting punctuation candidates:

| Encrypted byte | Plain candidates | Evidence count |
|:---|:---|---:|
| `)` | `,`, space | 2 |
| space | `(`, `.` | 2 |
| `_` | `.`, newline | 2 |

Stable single-candidate observations in this narrow anchor set included:

| Encrypted byte | Plain candidate |
|:---|:---|
| `#` | `(` |
| `(` | space |
| `*` | space |
| `+` | `_` |
| `-` | `.` |
| `:` | `(` |
| `;` | `.` |
| `=` | space |
| `|` | `)` |

These are not promoted as solved mappings because the conflict set proves the current assumptions do not support a clean one-byte punctuation substitution table.

## Interpretation

The evidence supports this narrower statement:

> The alphanumeric table is usable for handler and manager-call navigation, but punctuation/operators require another layer of modeling before exact Lua source can be claimed.

Likely explanations:

- the current plaintext anchors are normalized readability targets, not exact source
- printable punctuation may be affected by whitespace/control transforms
- some raw line breaks/control bytes may not represent plaintext line breaks
- punctuation may need context-aware handling instead of a single global substitution table

## Next Move

Do not try to patch `scripts/decrypt_handler.py` with a forced punctuation table.

The next proof step should build an anchor expander that:

1. searches anchors by alphanumeric skeleton only
2. aligns through raw bytes, not printable-only strings
3. treats whitespace/control bytes as transform candidates
4. records context windows around each punctuation byte
5. promotes a punctuation mapping only if it has no conflicts across multiple anchors

Until then, exact source reconstruction remains incomplete.

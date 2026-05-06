# Phase 2B Restore + Audit Report

Generated: 2026-04-26

## Scope

Restore external proof originals and run the Phase 2B read-only cipher audit.

## Reacquisition Result

`adb devices` returned no attached devices, so fresh device reacquisition was not available in this session.

The restore path used ignored private local originals that match the prior clean proof's expected sizes and hashes:

```text
/tmp/proof_snail_protocol_reset_20260426T195515Z_restored
```

Restore source:

```text
originals/tmp-imports/20260426T173840Z/*__sha256 clean-size variants
```

## Restored Originals

| File | Size | SHA256 | Mode |
|---|---:|---|---|
| `list.luac` | 32597 | `122b776932fdb0e5c85b201d72aa722267b5b13162394e4610199b1235ac6f67` | `444` |
| `msg_group_rank.luac` | 173 | `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9` | `444` |
| `msg_arena_top_query.luac` | 214 | `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37` | `444` |

## Audit Result

Phase 2B audit proof:

```text
/tmp/proof_snail_phase2b_cipher_audit_20260426T195523Z
```

Audit status:

```text
AUDIT_ONLY
```

The audit reviewed 3 read-only originals and 962 protocol/string candidates.

Observed unresolved alphanumeric counts in protocol candidates:

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

## Solve Status

No solve was claimed.

The existing imported solve candidates were not run as proof because they use hard-coded `/tmp` paths and/or positional handler alignment assumptions already identified as invalid in the clean decode report.

## Next Move

Build a safe Phase 2B solver that:

- reads restored originals read-only
- uses current trusted mappings as input
- derives new mappings only from anchored plaintext with byte offsets
- emits conflict records instead of forcing mappings
- writes all outputs under a new external proof directory
- keeps exact strings separate from normalized guesses

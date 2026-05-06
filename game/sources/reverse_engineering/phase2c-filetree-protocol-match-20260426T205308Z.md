# Phase 2C Filetree Protocol Match Report

Generated: 2026-04-26

## Scope

Use the live device handler file tree to normalize protocol names from the clean ADB-backed candidate decode without rewriting originals or promoting guessed punctuation as exact raw text.

## Inputs

Fresh ADB original proof:

```text
/tmp/proof_snail_protocol_adb_20260426T204437Z
```

Phase 2B audit proof:

```text
/tmp/proof_snail_phase2b_cipher_audit_20260426T204455Z
```

Phase 2C proof:

```text
/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z
```

## Method

1. Listed live `.luac` handlers from:

```text
/data/data/com.qcplay.snail.android.na/files/update_res/src/game/cmd/
```

2. Converted handler paths to expected protocol names:

```text
misc/msg_arena_top_query.luac -> misc@msg_arena_top_query
```

3. Matched each decoded protocol candidate to device handler names by alphanumeric skeleton.

4. Separated exact-length printable-symbol matches from skeleton-only length-delta matches.

## Results

| Metric | Count |
|---|---:|
| Protocol candidates | 962 |
| Device handler protocol names | 962 |
| Unique skeleton matches | 954 |
| Exact-length printable-symbol matches | 713 |
| Skeleton-only length-delta matches | 241 |
| Ambiguous skeleton matches | 0 |
| Unmatched candidates | 8 |
| Rank/group/arena/top target matches | 119 |

## Printable Symbol Evidence

In exact-length matches, these decoded candidate symbols aligned to underscores in real handler filenames:

| Candidate symbol | Count | Device filename target |
|---|---:|---|
| `.` | 132 | `_` |
| `:` | 132 | `_` |
| `{` | 128 | `_` |
| space | 124 | `_` |
| `=` | 123 | `_` |
| `)` | 118 | `_` |
| `-` | 117 | `_` |
| `;` | 114 | `_` |
| `}` | 113 | `_` |
| `,` | 112 | `_` |
| `%` | 111 | `_` |
| `(` | 111 | `_` |
| `*` | 106 | `_` |
| `+` | 102 | `_` |
| `|` | 98 | `_` |
| `#` | 97 | `_` |

## Unmatched Candidates

These 8 decoded candidates did not match a live handler filename by alphanumeric skeleton:

- `misc@msg*activity,turnplate1{action`
- `misc@msg.anniversary4+action`
- `misc@msg}group*war(special1}action`
- `misc@msg;mid{autumn2023=action`
- `misc@msg)shuangdan2023|action`
- `misc@msg*shuangdan2023_ice;bonus`
- `misc@msg;shuangdan2023*icestrike`
- `misc@msg*special1build(tower`

The live handler tree search found only one related older event file:

```text
misc/msg_shuangdan2021_ice_bonus.luac
```

## Target Protocol Names Recovered

The filetree-backed target list includes high-value rank/group/arena targets such as:

- `misc@msg_arena_query_rank_score`
- `misc@msg_arena_top_query`
- `misc@msg_group_myrank`
- `misc@msg_group_rank`
- `misc@msg_group_war_group_myrank`
- `misc@msg_group_war_group_rank`
- `misc@msg_group_war_member_rank`
- `misc@msg_top_rank`
- `misc@msg_week_task_myrank`
- `misc@msg_week_task_rank`

Full external output:

```text
/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z/out/rank_group_targets_phase2c.txt
```

## Interpretation

This is a strong normalized protocol-name recovery step, not a raw exact-string decode claim.

The device file tree proves most expected handler names and confirms that many printable punctuation-like symbols in the candidate decode function as underscore separators for protocol handler lookup.

Skeleton-only matches also prove the target handler name, but they do not prove every byte-level separator because some separators are absent from the printable decoded view and likely came from omitted high-bit/nonprintable bytes.

## Remaining Work

- Resolve or classify the 8 unmatched candidates.
- Keep `r` unresolved until anchored by a stronger context.
- Build a protocol report that clearly labels:
  - exact decoded strings
  - filetree-normalized names
  - unmatched/unresolved names
  - handler-backed rank/group/arena targets

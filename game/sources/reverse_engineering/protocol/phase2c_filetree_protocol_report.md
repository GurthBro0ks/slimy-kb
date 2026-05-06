# Phase 2C Filetree Protocol Report

Generated: 2026-04-26

## Status

Partial but operationally useful.

This report does not claim the raw punctuation cipher is fully solved. It separates exact decoded strings, filetree-normalized protocol names, and unresolved candidates.

## Evidence Inputs

Fresh ADB original proof:

```text
/tmp/proof_snail_protocol_adb_20260426T204437Z
```

Phase 2B partial solve:

```text
/tmp/proof_snail_phase2b_cipher_solve_20260426T204627Z
```

Phase 2C filetree match:

```text
/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z
```

Input original hashes:

| File | SHA256 |
|---|---|
| `list.luac` | `122b776932fdb0e5c85b201d72aa722267b5b13162394e4610199b1235ac6f67` |
| `msg_group_rank.luac` | `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9` |
| `msg_arena_top_query.luac` | `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37` |

## Current Cipher State

Carried/proven alphanumeric mappings now include the Phase 2B handler anchors:

- `H -> Y`
- `S -> K`
- `b -> Q`
- `d -> T`
- `6 -> 6`

Still unresolved:

- `r`
- byte-level punctuation/symbol substitution
- omitted high-bit/nonprintable separator bytes

## Protocol Name Recovery

The live device handler file tree was used as a normalization anchor.

Counts:

| Category | Count |
|---|---:|
| Protocol candidates | 962 |
| Device handler protocol names | 962 |
| Filetree-normalized matches | 954 |
| Exact-length printable-symbol matches | 713 |
| Skeleton-only length-delta matches | 241 |
| Ambiguous matches | 0 |
| Unmatched candidates | 8 |

Meaning:

- **Exact decoded strings:** protocol strings that need no filetree normalization remain exact.
- **Filetree-normalized names:** 954 names are backed by live device handler filenames.
- **Skeleton-only matches:** handler target is proven, but not every punctuation byte is proven.
- **Unmatched candidates:** 8 candidates need separate triage.

## Rank / Group / Arena Targets

High-value normalized target names include:

```text
misc@msg_arena_query_rank_score
misc@msg_arena_top_query
misc@msg_group_myrank
misc@msg_group_rank
misc@msg_group_war_group_myrank
misc@msg_group_war_group_rank
misc@msg_group_war_member_rank
misc@msg_top_rank
misc@msg_week_task_myrank
misc@msg_week_task_rank
```

Full external target list:

```text
/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z/out/rank_group_targets_phase2c.txt
```

## Unmatched Candidates

These candidates do not match live handler filenames by alphanumeric skeleton:

```text
misc@msg*activity,turnplate1{action
misc@msg.anniversary4+action
misc@msg}group*war(special1}action
misc@msg;mid{autumn2023=action
misc@msg)shuangdan2023|action
misc@msg*shuangdan2023_ice;bonus
misc@msg;shuangdan2023*icestrike
misc@msg*special1build(tower
```

The live handler tree only surfaced this related older event file:

```text
misc/msg_shuangdan2021_ice_bonus.luac
```

## Use Guidance

Safe to use:

- filetree-normalized protocol names for navigation and target selection
- rank/group/arena target list
- ADB proof hashes and report paths

Do not use as exact raw truth:

- printable punctuation symbols in the candidate decode
- skeleton-only separators
- unmatched event candidates

## Next Recommended Task

Triage the 8 unmatched candidates and then generate a focused rank/group/arena handler inventory from the now-normalized target list.

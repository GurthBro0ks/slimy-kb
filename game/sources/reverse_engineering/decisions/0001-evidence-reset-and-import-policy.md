# Decision 0001 - Evidence Reset and Import Policy

## Status

Accepted.

## Date

2026-04-26

## Context

A previous v2 decode run contaminated the workspace by rewriting source `.luac` files and normalizing protocol strings.

The evidence reset proof run completed at:

```text
/tmp/proof_snail_protocol_reset_20260426T170226Z
```

Final result:

```text
PASS_CLEAN_ORIGINALS_READY
```

## Decision

This repository will only import safe documentation, reports, prompts, and scripts.

Raw `.luac`, APK/XAPK, packet captures, account/session material, and contaminated v2 outputs are blocked from Git.

Fresh originals remain outside the repo in the proof directory and are referenced by path/hash only.

## Current Protocol Status

The cipher is incomplete.

Known current state:

- 962 quoted protocol strings extracted.
- 48 exact/trusted-character strings.
- 914 unresolved/symbol-corrupted strings.
- Remaining unmapped observed ASCII alphanumerics: `6`, `H`, `S`, `b`, `d`, `r`.
- Punctuation layer unresolved.

## Consequence

Phase 2B must solve mappings from read-only originals without rewriting evidence.

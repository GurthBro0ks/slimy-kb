# Decision 0002: Pivot from source reconstruction to wire capture

Date: 2026-04-27

## Context

Phase 2B through Phase 2W produced strong protocol and handler evidence:

- 954 of 962 protocol candidates matched live handler filenames by skeleton.
- The alphanumeric substitution table is effectively complete except `r`.
- Phase 2G traced rank/group handler flow and confirmed useful client-side fields.
- Phase 2H through Phase 2W proved the punctuation/control layer is polymorphic or context-dependent, not a safe global substitution table.
- Phrase-template overlays are conflict-free where proven, but they are not full Lua source reconstruction.

The remaining Phase 2 grammar work can improve redacted handler coverage, but it is no longer the shortest path to the project goal.

## Decision

Stop treating Phase 2 grammar-fragment trials as the default next task.

The next default branch is Phase 3/4:

1. Prepare a safe, sanitized wire-capture workflow for owned account/device traffic.
2. Capture actual auth and transport evidence.
3. Correlate captured message names, endpoints, or packet IDs with the Phase 2C protocol list and Phase 2G rank/group field-flow map.
4. Build an API-client scaffold only after transport, auth, and replay safety are understood.

Phase 3 prep must verify runtime readiness. If `emulator-5554` or the game process is down, start the `snail-recon` AVD, wait for boot, launch `com.qcplay.snail.android.na`, and confirm PID plus top activity before moving on.

## Guardrails

- Do not commit packet captures, HAR files, mitmproxy flows, tokens, cookies, auth headers, device IDs, account identifiers, or secrets.
- Store raw captures outside Git or under ignored private paths only.
- Commit only sanitized summaries, hash inventories, scripts, and proof reports.
- Do not claim clean protocol replay until a capture proves the auth flow and transport.
- Do not patch `scripts/decrypt_handler.py` with forced punctuation mappings.
- Keep generated analyst views, stale proof logs, and tmp-import scratch files out of normal `git status` noise unless they are intentionally promoted as sanitized source-of-truth documents.

## Current confidence

The repo has enough Phase 2 evidence to start Phase 3 wire capture planning and tooling.

Phase 2 source reconstruction is still useful as a side branch, but it is no longer blocking rank-data client research.

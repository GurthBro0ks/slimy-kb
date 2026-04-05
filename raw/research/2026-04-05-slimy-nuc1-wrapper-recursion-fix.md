---
name: wrapper-recursion-fix
description: NUC1 wrapper recursion guard fix for claude/codex finish hooks
type: research
---

# NUC1 Wrapper Recursion Fix (Claude/Codex)

Date: 2026-04-05
Host: slimy-nuc1

## Root Cause
NUC1 `~/.local/bin/claude` and `~/.local/bin/codex` used `SLIMY_AUTOFINISH_ACTIVE` as the wrapper-level skip condition. That made finish-hook behavior dependent on inherited environment state instead of explicit child-compile context.

The finish pipeline already has explicit child-compile signaling:
- `SLIMY_KB_CHILD_COMPILE=1` in `kb-compile-if-needed.sh` child launches
- `SLIMY_AUTOFINISH_ACTIVE=1` set inside `slimy-agent-finish.sh` for recursion guard

Wrapper-level gating on `SLIMY_AUTOFINISH_ACTIVE` caused normal post-exit behavior drift and recursion-guard interference on NUC1.

## Wrapper Changes Made
Updated both wrappers:
- `/home/slimy/.local/bin/claude`
- `/home/slimy/.local/bin/codex`

Changes:
1. Preserve CLI exit code safely with `set +e` around real binary execution.
2. Use `SLIMY_KB_CHILD_COMPILE=1` as the only wrapper skip condition.
3. Before normal finish-hook call, clear recursion flag with:
   - `unset SLIMY_AUTOFINISH_ACTIVE || true`
4. Keep Codex real launch as:
   - `/home/slimy/.npm-global/bin/codex --yolo "$@"`

## Claude Result (Real Wrapper Test)
Test file created:
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-final-test-claude.md`

Observed in `/tmp/wrapper-final-test-claude.log`:
- Normal finish hook started (`[slimy-agent-finish] Starting finish automation...`)
- No normal-path recursion-guard early exit
- KB autofile commit created and pushed:
  - `de7e26c kb: autofile claude 20260405-160736`
- Auto-compile executed via child run:
  - `Child compile SUCCEEDED (exit 0)`
  - child compile commit already present in history (`352dcae` and prior child compile commit)
- Finish hook completed cleanly:
  - `[slimy-agent-finish] Finish automation complete.`

## Codex Result (Real Wrapper Test)
Test file created:
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-final-test-codex.md`

Observed in `/tmp/wrapper-final-test-codex.log`:
- Normal finish hook started (`[slimy-agent-finish] Starting finish automation...`)
- No normal-path recursion-guard early exit
- KB autofile commit created and pushed:
  - `2ed32c4 kb: autofile codex 20260405-161210`
- Auto-compile executed via child run:
  - `Child compile SUCCEEDED (exit 0)`
- Finish hook completed cleanly:
  - `[slimy-agent-finish] Finish automation complete.`

Codex `--yolo` proof (xtrace):
- `/tmp/wrapper-yolo-proof.log` contains:
  - `/home/slimy/.npm-global/bin/codex --yolo --version`

## Child-Compile Recursion Protection
Verified child path skip behavior still works:
- `SLIMY_KB_CHILD_COMPILE=1` wrapper run does not call `slimy-agent-finish.sh`
- xtrace evidence in `/tmp/wrapper-child-guard-claude.log` and `/tmp/wrapper-yolo-proof.log`

## NUC1 vs NUC2 Behavior Match
Status: **MATCHED**

NUC1 now matches intended NUC2 behavior:
- normal user exits trigger finish automation
- child compile runs are protected from recursive finish execution
- Codex wrapper still enforces `--yolo`

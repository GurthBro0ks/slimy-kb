# NUC1 Wrapper Recursion Fix
> Category: troubleshooting
> Sources: raw/research/2026-04-05-slimy-nuc1-wrapper-recursion-fix.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

Fix for NUC1 wrapper recursion guard interference that caused finish-hook behavior drift and child-compile protection failures.

## Root Cause

NUC1 `~/.local/bin/claude` and `~/.local/bin/codex` used `SLIMY_AUTOFINISH_ACTIVE` as the wrapper-level skip condition. This made finish-hook behavior dependent on inherited environment state instead of explicit child-compile context.

The finish pipeline already has explicit child-compile signaling:
- `SLIMY_KB_CHILD_COMPILE=1` in `kb-compile-if-needed.sh` child launches
- `SLIMY_AUTOFINISH_ACTIVE=1` set inside `slimy-agent-finish.sh` for recursion guard

Wrapper-level gating on `SLIMY_AUTOFINISH_ACTIVE` caused normal post-exit behavior drift and recursion-guard interference on NUC1.

## Wrapper Changes Made

Updated both wrappers:
- `/home/slimy/.local/bin/claude`
- `/home/slimy/.local/bin/codex`

Changes:
1. Preserve CLI exit code safely with `set +e` around real binary execution
2. Use `SLIMY_KB_CHILD_COMPILE=1` as the only wrapper skip condition
3. Before normal finish-hook call, clear recursion flag with `unset SLIMY_AUTOFINISH_ACTIVE || true`
4. Keep Codex real launch as `/home/slimy/.npm-global/bin/codex --yolo "$@"`

## Validation Results

### Claude (Real Wrapper Test)
- Normal finish hook started correctly
- No normal-path recursion-guard early exit
- KB autofile commit created and pushed: `de7e26c kb: autofile claude 20260405-160736`
- Auto-compile executed via child run: `Child compile SUCCEEDED (exit 0)`
- Finish hook completed cleanly

### Codex (Real Wrapper Test)
- Normal finish hook started correctly
- No normal-path recursion-guard early exit
- KB autofile commit created and pushed: `2ed32c4 kb: autofile codex 20260405-161210`
- Auto-compile executed via child run: `Child compile SUCCEEDED (exit 0)`
- Finish hook completed cleanly

### Child-Compile Recursion Protection
Verified child path skip behavior still works:
- `SLIMY_KB_CHILD_COMPILE=1` wrapper run does not call `slimy-agent-finish.sh`
- xtrace evidence in `/tmp/wrapper-child-guard-claude.log` and `/tmp/wrapper-yolo-proof.log`

### NUC1 vs NUC2 Behavior Match
Status: **MATCHED**

NUC1 now matches intended NUC2 behavior:
- Normal user exits trigger finish automation
- Child compile runs are protected from recursive finish execution
- Codex wrapper still enforces `--yolo`

## See Also
- [KB Autofinish Autocompile Fix](kb-autofinish-autocompile-fix.md) — NUC2-side autofinish and compile write-through fix
- [Slimy KB](../../projects/slimy-kb.md) — KB tools including finish hook automation

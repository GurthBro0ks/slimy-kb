# NUC1 Repo Remote SSH Normalization
> Category: troubleshooting
> Sources: raw/research/2026-04-05-slimy-nuc1-repo-remote-ssh-normalization.md
> Created: 2026-04-07
> Updated: 2026-04-08
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-26 00:35 UTC (git)
> Version: r44 / 35740c1
KB METADATA -->

Normalized GitHub remotes to SSH on NUC1 to match the autofinish non-interactive policy already in place on NUC2. All GurthBro0ks-owned repos now use SSH; third-party and local-only repos are excluded with appropriate guards.

## Problem

The autofinish automation needed all repo pushes to succeed or fail silently without interactive prompts. NUC1 had a mix of SSH and HTTPS remotes; third-party repos (e.g., Slimefun4) used HTTPS which could trigger credential prompts.

## Remote Inspection Results

### GurthBro0ks-owned (SSH, auto-push enabled)

| Repo | Remote | Push |
|------|--------|------|
| /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git | ✓ Yes |
| /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git | ✓ Yes |
| /home/slimy/ned-clawd | git@github.com:GurthBro0ks/ned-clawd.git | ✓ Yes |
| /home/slimy/slimy-chat | git@github.com:GurthBro0ks/slime.chat.git | ✓ Yes |
| /home/slimy/kb | git@github.com:GurthBro0ks/slimy-kb.git | ✓ Yes |
| /home/slimy/ned-autonomous | git@github.com:GurthBro0ks/ned-autonomous.git | ✓ Yes |
| /home/slimy/.qoder-server/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | ✓ Yes |
| /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | ✓ Yes |
| /opt/slimy/app | git@github.com:GurthBro0ks/slimyai_setup.git | ✓ Yes |
| /opt/slimy/apify-market-scanner | git@github.com:GurthBro0ks/apify-market-scanner.git | ✓ Yes |
| /opt/slimy/pm_updown_bot_bundle | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git | ✓ Yes |

### Third-party (HTTPS, excluded from auto-push)

| Repo | Remote | Action |
|------|--------|--------|
| /home/slimy/src/plugins/Slimefun4 | https://github.com/Slimefun/Slimefun4.git | Skipped (guard) |
| /home/slimy/src/plugins/PrivateStorage | https://github.com/Slimefun-Addon-Community/PrivateStorage.git | Skipped (guard) |
| /home/slimy/src/plugins/DynaTech | https://github.com/ProfElements/DynaTech.git | Skipped (guard) |
| /home/slimy/stoat-source | https://github.com/stoatchat/stoatchat | Skipped (guard) |
| /home/slimy/ned-clawd/actionbook | https://github.com/actionbook/actionbook | Skipped (guard) |
| /home/slimy/.codex/.tmp/plugins | https://github.com/openai/plugins.git | Skipped (guard) |
| /opt/slimy/research/kalshi-ai-trading-bot | https://github.com/ryanfrigo/kalshi-ai-trading-bot.git | Skipped (guard) |

### Local-only (no remote)

| Repo | Push |
|------|------|
| /home/slimy/.openclaw/workspace-executor | ✗ No (no remote) |
| /home/slimy/.openclaw/workspace-researcher | ✗ No (no remote) |
| /home/slimy/nuc-comms/mailbox_outbox | ✗ No (no remote) |
| /opt/slimy/pm_updown_bot_bundle/proofs | ✗ No (bare proof archive) |

## Remote Conversions Needed

**NONE** — All GurthBro0ks-owned repos already used SSH. No remote URL conversions were required.

## Non-Interactive Guard Policy

Applied to `slimy-agent-finish.sh` and both wrappers (`~/.local/bin/claude`, `~/.local/bin/codex`):

```bash
export GIT_TERMINAL_PROMPT=0   # Blocks git interactive credential prompt
export GCM_INTERACTIVE=never    # Blocks Git Credential Manager interactive mode
export GIT_PAGER=cat            # Prevents interactive pager
export PAGER=cat                # Prevents interactive pager
```

These exports ensure all subprocesses spawned by the wrappers (not just the finish hook) inherit non-interactive git behavior.

## HTTPS GitHub Remote Guard

`slimy-agent-finish.sh` uses `is_https_github_remote()` to detect HTTPS GitHub remotes:
- Skips push with a warning log (not blocking)
- Records failure in `ALERT_MSG` (for Discord webhook)
- Does NOT abort KB autofile or compile path

## SSH Verification

```bash
ssh -T git@github.com
# → Hi GurthBro0ks! You've successfully authenticated, but GitHub does not provide shell access.
```

## Validation Results

### Dry-run (all 21 detected repos)
```
[slimy-agent-finish] DRY-RUN: would write agent learnings...
[slimy-agent-finish] DRY-RUN: would commit and push KB changes
[slimy-agent-finish] DRY-RUN: skipping compile
[slimy-agent-finish] Finish automation complete.
```
No interactive prompts ✓

### Real autofinish — SSH push (clawd)
```
[slimy-agent-finish] Pushed /home/slimy/clawd
[slimy-agent-finish] KB pushed: To github.com:GurthBro0ks/slimy-kb.git
[slimy-agent-finish] Finish automation complete.
```
clawd pushed via SSH ✓, KB write-through complete ✓

### Real autofinish — HTTPS guard (Slimefun4 + no-remote workspace)
```
[slimy-agent-finish] WARNING: HTTPS GitHub remote detected in /home/slimy/src/plugins/Slimefun4 — skipping push (convert to SSH to enable)
[slimy-agent-finish] WARNING: could not push /home/slimy/.openclaw/workspace-executor (may need credentials)
[slimy-agent-finish] KB pushed: To github.com:GurthBro0ks/slimy-kb.git
[slimy-agent-finish] Posted ALERTS webhook
[slimy-agent-finish] Finish automation complete.
```
HTTPS guard: skip with warning ✓ | No-remote: fail silently ✓ | KB write-through: complete ✓ | ALERTS: fires ✓

## Scripts Changed

- `~/.local/bin/claude` — added non-interactive exports (`GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never`, `GIT_PAGER=cat`, `PAGER=cat`)
- `~/.local/bin/codex` — added non-interactive exports (same)

## Status

| Check | Status |
|-------|--------|
| SSH verified | ✓ |
| All GurthBro0ks repos: SSH | ✓ |
| autofinish repo push: non-blocking | ✓ |
| HTTPS GitHub remotes: guard skips with warning, no blocking prompt | ✓ |
| No-remote repos: fail silently with warning, non-blocking | ✓ |
| KB write-through: completes despite repo push failures | ✓ |
| ALERTS webhook fires on repo push failures | ✓ |
| NUC1 matches NUC2 policy | ✓ |

## See Also
- [KB Autofinish Autocompile Fix](kb-autofinish-autocompile-fix.md)
- [NUC2 Repo Remote SSH Normalization](nuc2-repo-remote-ssh-normalization.md)
- [Slimy KB](../../projects/slimy-kb.md)

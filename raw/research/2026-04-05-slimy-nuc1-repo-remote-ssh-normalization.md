---
name: 2026-04-05-slimy-nuc1-repo-remote-ssh-normalization
description: Normalized GitHub remotes to SSH on NUC1; matched NUC2 autofinish non-interactive policy
type: research
---

# NUC1 Repo Remote SSH Normalization — 2026-04-05

## Goal
Mirror the finalized NUC2 repo-remote and non-interactive autofinish policy onto NUC1 so both hosts follow the same SSH/skip/fail-fast rules.

## Phase 1 — Non-Interactive Guard Policy

### NUC2 policy (already in place on NUC1 via `slimy-agent-finish.sh`)
The following exports are present at the top of `slimy-agent-finish.sh`:
```bash
export GIT_TERMINAL_PROMPT=0   # Blocks git interactive credential prompt
export GCM_INTERACTIVE=never    # Blocks Git Credential Manager interactive mode
export GIT_PAGER=cat            # Prevents interactive pager
export PAGER=cat                # Prevents interactive pager
```

### Gap found: wrappers missing guards
Both `~/.local/bin/claude` and `~/.local/bin/codex` wrappers were missing these exports. Added to both:

```bash
export GIT_TERMINAL_PROMPT=0
export GCM_INTERACTIVE=never
export GIT_PAGER=cat
export PAGER=cat
```

This ensures ALL subprocesses spawned by the wrappers (not just the finish hook) inherit non-interactive git behavior.

## Phase 2 — Remote Inspection Results

| Repo | Remote | Type | Should NUC1 Push |
|------|--------|------|-----------------|
| /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git | SSH | ✓ Yes |
| /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git | SSH | ✓ Yes |
| /home/slimy/ned-clawd | git@github.com:GurthBro0ks/ned-clawd.git | SSH | ✓ Yes |
| /home/slimy/slimy-chat | git@github.com:GurthBro0ks/slime.chat.git | SSH | ✓ Yes |
| /home/slimy/kb | git@github.com:GurthBro0ks/slimy-kb.git | SSH | ✓ Yes |
| /home/slimy/ned-autonomous | git@github.com:GurthBro0ks/ned-autonomous.git | SSH | ✓ Yes |
| /home/slimy/.qoder-server/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | SSH | ✓ Yes |
| /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | SSH | ✓ Yes |
| /opt/slimy/app | git@github.com:GurthBro0ks/slimyai_setup.git | SSH | ✓ Yes |
| /opt/slimy/apify-market-scanner | git@github.com:GurthBro0ks/apify-market-scanner.git | SSH | ✓ Yes |
| /opt/slimy/pm_updown_bot_bundle | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git | SSH | ✓ Yes |
| /home/slimy/src/plugins/Slimefun4 | https://github.com/Slimefun/Slimefun4.git | HTTPS | ✗ No (3rd party) |
| /home/slimy/src/plugins/PrivateStorage | https://github.com/Slimefun-Addon-Community/PrivateStorage.git | HTTPS | ✗ No (3rd party) |
| /home/slimy/src/plugins/DynaTech | https://github.com/ProfElements/DynaTech.git | HTTPS | ✗ No (3rd party) |
| /home/slimy/stoat-source | https://github.com/stoatchat/stoatchat | HTTPS | ✗ No (3rd party) |
| /home/slimy/ned-clawd/actionbook | https://github.com/actionbook/actionbook | HTTPS | ✗ No (3rd party) |
| /home/slimy/.codex/.tmp/plugins | https://github.com/openai/plugins.git | HTTPS | ✗ No (3rd party) |
| /opt/slimy/research/kalshi-ai-trading-bot | https://github.com/ryanfrigo/kalshi-ai-trading-bot.git | HTTPS | ✗ No (3rd party) |
| /home/slimy/.openclaw/workspace-executor | (none) | local-only | ✗ No (no remote) |
| /home/slimy/.openclaw/workspace-researcher | (none) | local-only | ✗ No (no remote) |
| /home/slimy/nuc-comms/mailbox_outbox | (none) | local-only | ✗ No (no remote) |
| /opt/slimy/pm_updown_bot_bundle/proofs | (none — bare proof archive) | local-only | ✗ No (no remote) |

## Phase 3 — Normalization Actions

### Remote conversions needed: NONE
All GurthBro0ks-owned repos on NUC1 already use SSH remotes. No conversions required.

### Repos excluded from auto-push
- **Third-party GitHub HTTPS repos** (Slimefun4, DynaTech, PrivateStorage, stoat-source, actionbook, plugins, kalshi-ai-trading-bot): guarded by `is_https_github_remote()` — skipped with warning, non-blocking
- **Local-only repos** (workspace-executor, workspace-researcher, mailbox_outbox, proofs): no remote — push fails silently with warning, non-blocking
- **Non-GitHub remotes**: not present on NUC1

## Phase 4 — Hardening Verified

### `slimy-agent-finish.sh` already has:
- `is_https_github_remote()` function ✓
- GIT_TERMINAL_PROMPT=0, GCM_INTERACTIVE=never, GIT_PAGER=cat, PAGER=cat ✓
- Push failures: logged to ALERT_MSG, KB commit/push continues ✓
- ALERTS webhook fires on failures ✓

### `kb-project-doc-sync.sh` has:
- GIT_PAGER=cat, PAGER=cat ✓

### `kb-sync.sh` has:
- GIT_PAGER=cat, PAGER=cat ✓

### `kb-compile-if-needed.sh` has:
- GIT_PAGER=cat, PAGER=cat ✓

### Wrappers updated:
- `~/.local/bin/claude`: added non-interactive exports ✓
- `~/.local/bin/codex`: added non-interactive exports ✓

## Phase 5 — SSH Verification
```
ssh -T git@github.com
→ Hi GurthBro0ks! You've successfully authenticated, but GitHub does not provide shell access.
```

## Phase 6 — Validation Results

### Dry-run autofinish (all 21 detected repos)
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

## Phase 7 — Scripts Changed

- `~/.local/bin/claude` — added non-interactive exports
- `~/.local/bin/codex` — added non-interactive exports

## Status
- SSH verified ✓
- All GurthBro0ks repos: SSH ✓
- autofinish repo push: non-blocking ✓
- HTTPS GitHub remotes: guard skips with warning, no blocking prompt ✓
- No-remote repos: fail silently with warning, non-blocking ✓
- KB write-through: completes despite repo push failures ✓
- ALERTS webhook fires on repo push failures ✓
- NUC1 now matches NUC2 policy ✓

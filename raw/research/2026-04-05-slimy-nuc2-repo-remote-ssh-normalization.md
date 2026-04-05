---
name: 2026-04-05-slimy-nuc2-repo-remote-ssh-normalization
description: Normalized GitHub remotes to SSH on NUC2 to fix autofinish auth failures
type: research
---

# NUC2 Repo Remote SSH Normalization — 2026-04-05

## Problem
`slimy-agent-finish.sh` was failing on repo push due to HTTPS remotes prompting for GitHub username/password interactively, blocking autofinish before KB write-through completed.

## Inspection Results

| Repo | Remote | Type |
|------|--------|------|
| /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git | SSH ✓ |
| /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git | SSH ✓ |
| /home/slimy/.openclaw/workspace | (none) | local-only |
| /home/slimy/.openclaw/memory/git-notes-ledger | (none) | local-only |
| /home/slimy/.claude/agents-backup-full | https://github.com/wshobson/agents.git | **HTTPS → FIXED** |
| /home/slimy/.mcp_agent_mail_git_mailbox_repo | (none) | local-only |

## Additional Repos Detected (auto-discover)

| Repo | Remote | Type |
|------|--------|------|
| /home/slimy/.codex/.tmp/plugins | https://github.com/slimy-ai/slimy-plugins.git | **HTTPS (guard applies)** |
| /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | SSH ✓ |
| /opt/slimy/app | (none) | local-only |
| /opt/slimy/chat-app | (none) | local-only |
| /opt/slimy/web/slimyai-web | git@github.com:GurthBro0ks/slimyai-web.git | SSH ✓ |

## Phase 2 — Actions Taken

1. **agents-backup-full:** Converted origin from HTTPS to SSH:
   ```
   git remote set-url origin git@github.com:wshobson/agents.git
   ```
2. **plugins:** Left as HTTPS, guarded by `is_https_github_remote()` function

## Phase 4 — Hardening Applied

### Non-Interactive Git Environment
Added to `slimy-agent-finish.sh` top (after GIT_PAGER/PAGER):
```bash
export GIT_TERMINAL_PROMPT=0   # Blocks git's interactive credential prompt
export GCM_INTERACTIVE=never   # Blocks Git Credential Manager interactive mode
```

### HTTPS GitHub Remote Guard
Added `is_https_github_remote()` function — repos with HTTPS GitHub remotes now:
1. Skip push with a warning log (not a blocking error)
2. Record failure in ALERT_MSG (for Discord webhook)
3. Do NOT abort KB autofile or compile path

```bash
is_https_github_remote() {
    local repo="$1"
    local remote_url
    remote_url=$(git -C "$repo" remote get-url origin 2>/dev/null || true)
    [[ "$remote_url" == https://github.com/* ]]
}
```

## Phase 5 — Validation Result

**Dry-run test:**
```
[slimy-agent-finish] DRY-RUN: would write agent learnings...
[slimy-agent-finish] DRY-RUN: would commit and push KB changes
[slimy-agent-finish] DRY-RUN: skipping compile
[slimy-agent-finish] Finish automation complete.
```

**Real autofinish test (2026-04-05-2136):**
```
[slimy-agent-finish] WARNING: HTTPS GitHub remote detected in /home/slimy/.codex/.tmp/plugins — skipping push (convert to SSH to enable)
[slimy-agent-finish] WARNING: could not push /home/slimy/.codex/.tmp/plugins (may need credentials)
[slimy-agent-finish] Pushed /opt/slimy/slimy-monorepo
[slimy-agent-finish] Pushed /opt/slimy/web/slimyai-web
[slimy-agent-finish] WARNING: could not push /opt/slimy/app (may need credentials)
[slimy-agent-finish] WARNING: could not push /opt/slimy/chat-app (may need credentials)
[slimy-agent-finish] Committing KB changes...
[main 104d4f8] kb: autofile test-validation 20260405-213612
[slimy-agent-finish] KB pushed: To github.com:GurthBro0ks/slimy-kb.git
   8315e18..104d4f8  main -> main
[slimy-agent-finish] Posted ALERTS webhook
[slimy-agent-finish] Finish automation complete.
```

KB write-through completed despite repo push failures. No interactive prompts.

## SSH Verification
```
ssh -T git@github.com
→ Hi GurthBro0ks! You've successfully authenticated, but GitHub does not provide shell access.
```

## Scripts Changed
- `/home/slimy/kb/tools/slimy-agent-finish.sh` — added `GIT_TERMINAL_PROMPT=0` + `GCM_INTERACTIVE=never` + `is_https_github_remote()` guard

## Status
- SSH verified ✓
- `agents-backup-full` remote: SSH ✓
- autofinish repo push: non-blocking ✓
- HTTPS GitHub remotes: guard skips with warning, no blocking prompt ✓
- KB write-through: completes despite repo push failures ✓
- ALERTS webhook fires on repo push failures ✓
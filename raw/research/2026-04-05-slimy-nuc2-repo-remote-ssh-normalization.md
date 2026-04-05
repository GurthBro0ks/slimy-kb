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
| /home/slimy/.claude/agents-backup-full | https://github.com/wshobson/agents.git | **HTTPS — FIXED** |
| /home/slimy/.mcp_agent_mail_git_mailbox_repo | (none) | local-only |

## Action Taken

**agents-backup-full:** Converted origin from HTTPS to SSH:
```
git remote set-url origin git@github.com:wshobson/agents.git
```

## Hardening: HTTPS GitHub Remote Guard

Added `is_https_github_remote()` function to `slimy-agent-finish.sh` — repos with HTTPS GitHub remotes now:
1. Skip push silently with a warning log
2. Record failure in ALERT_MSG (for webhook)
3. Do NOT abort KB autofile or compile

This makes repo push failures non-blocking for the full KB write-through path.

## SSH Verification
```
ssh -T git@github.com
→ Hi GurthBro0ks! You've successfully authenticated...
```

## Scripts Changed
- `/home/slimy/kb/tools/slimy-agent-finish.sh` — added HTTPS GitHub remote guard

## Status
- agents-backup-full remote: SSH ✓
- autofinish repo push: non-blocking ✓
- KB write-through path: protected from repo push failures ✓
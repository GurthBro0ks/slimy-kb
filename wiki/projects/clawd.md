# Clawd
> Category: projects
> Sources: raw/decisions/2026-04-09-project-clawd.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-24 00:31 UTC (git)
> Version: r34 / aa2e4da
KB METADATA -->

AI agent workspace for SlimyAI with session management, memory protocols, heartbeat scheduling, and group chat safety. Standard SlimyAI runtime environment.

## Runtime State (NUC1)
- **Path:** `/home/slimy/clawd`
- **Remote:** `git@github.com:GurthBro0ks/clawd.git`, branch `master`
- **Last 3 commits:**
  - `03f949c` — chore: update memory - compound nightly review 2026-04-09
  - `950a020` — docs: add NUC1 unreachable issue to MEMORY.md
  - `50175b6` — docs: daily memory Apr 3-8, 2026
- **AGENTS.md:** YES — OpenClaw daemon rules
- **README.md:** YES — OpenClaw workspace governance
- **Status:** ACTIVE — has uncommitted changes (dirty)
- **Truth gate:** `git -C /home/slimy/clawd log -1 --oneline`
- **Services:** none (runs as Claude Code subprocess, not a daemon)

## Purpose
OpenClaw CLAWD daemon — workspace governance, autonomous agent, memory.

## See Also
- [Clawd Agent Rules](clawd-agent-rules.md)
- [Clawd Workspace Governance](clawd-workspace-governance.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)

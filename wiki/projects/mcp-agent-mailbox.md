# MCP Agent Mailbox
> Category: projects
> Sources: raw/decisions/2026-04-09-project-mcp-agent-mailbox.md, raw/research/2026-04-09-nuc2-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-18 12:25 UTC (git)
> Version: r14 / ff55646
KB METADATA -->

MCP agent mail git mailbox repository. Used by MCP agents for inter-agent communication via git. Local-only on NUC2 with no remote push URL.

## Why It Matters

This is the message bus for MCP-based agents. When agents need to communicate asynchronously — sending tasks, results, or coordination messages — they write to this git-backed mailbox. Using git as the transport means messages are versioned, auditable, and conflict-resistant. This is the local NUC2 endpoint; it does not push to a remote.

## Runtime State (NUC2)
- **Path:** `/home/slimy/.mcp_agent_mail_git_mailbox_repo`
- **Remote:** none (local-only — no push URL configured)
- **Branch:** master
- **Status:** ACTIVE
- **AGENTS.md:** NO
- **README.md:** YES
- **Truth gate:** `git -C /home/slimy/.mcp_agent_mail_git_mailbox_repo log -1 --oneline`
- **Services:** none
- **Risks:** none

## Current Role in the System
- Local message drop for MCP agents running on NUC2
- Agents commit messages as files; other agents read and process them
- No remote push — messages stay on NUC2 unless manually moved
- Receives auto-sync docs commits passively

## Important Files
- The repo itself is the mailbox — structure follows git commit conventions
- No configuration files, no service files, no environment variables needed

## Relationships / Dependencies
- **Used by:** MCP agents on NUC2 (inter-agent communication)
- **Related:** [Mailbox NUC Comms](mailbox-nuc-comms.md) — the inter-NUC mailbox system (separate from this agent mailbox)
- **Contrast:** NUC comms mailbox is NUC1↔NUC2 transport; MCP mailbox is agent↔agent on same host

## Operational Notes
- Low maintenance — no services, no health checks
- If agents stop communicating, check this repo's recent commits to see if messages are landing
- No backup to remote — local-only data. If NUC2 disk fails, mailbox content is lost.

## See Also
- [Mailbox NUC Comms](mailbox-nuc-comms.md) — inter-NUC mailbox (different system)
- [Mailbox Ingest](mailbox-ingest.md) — NUC2 ingest side
- [Agents Plugin Ecosystem](agents-plugin-ecosystem.md)

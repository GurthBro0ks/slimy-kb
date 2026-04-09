# MCP Agent Mailbox
> Category: projects
> Sources: raw/decisions/2026-04-09-project-mcp-agent-mailbox.md, raw/research/2026-04-09-nuc2-project-inventory.md
> Created: 2026-04-09
> Status: draft

MCP agent mail git mailbox repository. Used by MCP agents for inter-agent communication via git. Local-only, no remote push URL.

## Runtime State (NUC2)
- **Path:** `/home/slimy/.mcp_agent_mail_git_mailbox_repo`
- **Remote:** none (local-only)
- **Branch:** master
- **Status:** ACTIVE
- **AGENTS.md:** NO
- **README.md:** YES
- **Truth gate:** `git -C /home/slimy/.mcp_agent_mail_git_mailbox_repo log -1 --oneline`
- **Services:** none
- **Risks:** none

## See Also

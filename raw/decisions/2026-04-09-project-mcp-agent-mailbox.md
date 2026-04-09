# .mcp_agent_mail_git_mailbox_repo
- Host: nuc2
- Repo path: /home/slimy/.mcp_agent_mail_git_mailbox_repo
- GitHub remote: none (local-only)
- Branch: master
- Type: tool (MCP agent mail)
- Status: active
- Priority: low
- Purpose: MCP agent mail git mailbox repository. Used by MCP agents for inter-agent communication via git.
- Dependencies: git
- Services: none
- Truth gate: `git -C /home/slimy/.mcp_agent_mail_git_mailbox_repo log -1 --oneline`
- Risks: none
- Current work: auto-sync docs only

## Wiki article needed
No wiki article exists. Minor project, can be low priority for wiki coverage.
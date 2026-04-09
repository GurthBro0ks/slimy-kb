# Agents Backup Full (wshobson/agents mirror)
- Host: nuc2
- Repo path: /home/slimy/.claude/agents-backup-full
- GitHub remote: git@github.com:wshobson/agents.git
- Branch: main
- Type: tool (Claude Code plugin marketplace)
- Status: archived
- Priority: low
- Purpose: Full mirror of wshobson/agents — Claude Code plugins marketplace with 112 specialized agents, 146 skills, 72 plugins, 16 multi-agent orchestrators. Not actively used on NUC2; backup/archive.
- Dependencies: none (standalone git repo)
- Services: none
- Truth gate: `git -C /home/slimy/.claude/agents-backup-full log -1 --oneline`
- Risks: none (read-only backup)
- Current work: auto-sync docs only

## Note
`/home/slimy/.claude/agents` symlink does not exist. Only agents-backup-full exists.
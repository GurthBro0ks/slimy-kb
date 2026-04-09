bash /home/slimy/kb/tools/kb-sync.sh pull

cat /home/slimy/AGENTS.md
cat /home/slimy/claude-progress.md
source /home/slimy/init.sh
cat /home/slimy/kb/KB_AGENTS.md

TASK: KB Compile

Goal:
- Compile raw knowledge into canonical wiki updates following KB_AGENTS rules.

Priority Raw Inputs:
- /home/slimy/kb/raw/decisions/seed-clawd-agents.md
- /home/slimy/kb/raw/decisions/seed-workspace-agents.md
- /home/slimy/kb/raw/agent-learnings/seed-progress-history.md
- /home/slimy/kb/raw/decisions/seed-agents-rules.md
- /home/slimy/kb/raw/decisions/seed-clawd-agents.md
- /home/slimy/kb/raw/decisions/seed-workspace-agents.md
- /home/slimy/kb/raw/agent-learnings/seed-progress-history.md
- /home/slimy/kb/raw/agent-learnings/seed-progress-history.md
- /home/slimy/kb/raw/decisions/seed-server-state.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc2-repo-remote-ssh-normalization.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc1-wrapper-recursion-fix.md
- /home/slimy/kb/raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-test-claude.md
- /home/slimy/kb/raw/decisions/seed-agents-rules.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc1-repo-remote-ssh-normalization.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc2-autofinish-autocompile-fix.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc2-autofinish-parity-check.md
- /home/slimy/kb/raw/agent-learnings/2026-04-05-nuc2-no-pager-finish-hook-fix.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc2-no-pager-finish-hook-fix.md
- /home/slimy/kb/raw/research/2026-04-05-slimy-nuc1-wrapper-recursion-fix.md
- /home/slimy/kb/raw/decisions/seed-server-state.md
- /home/slimy/kb/raw/decisions/seed-agents-rules.md

Required updates:
- Update or create wiki articles as needed
- Update /home/slimy/kb/wiki/_index.md
- Update /home/slimy/kb/wiki/_concepts.md if concepts changed
- Preserve source attribution in each article

Validation:
- Confirm compile candidates are fully handled or explicitly deferred with reason

# Direct push without pull-first (avoids rebase conflicts in child compile)
cd /home/slimy/kb && git --no-pager add -A && git --no-pager diff --cached --stat && git --no-pager commit -m "kb: child-compile 20260409-095418" && git --no-pager push origin main

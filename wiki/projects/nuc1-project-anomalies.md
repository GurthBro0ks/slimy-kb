# NUC1 Project Anomalies
> Category: projects
> Sources: raw/research/2026-04-05-nuc1-project-anomalies.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc1-state.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 00:23 UTC (git)
> Version: r6 / 3f6aea2
KB METADATA -->

Anomalies and discrepancies found during NUC1 project discovery (2026-04-05).

## Anomaly 1: mailbox_ingest NOT FOUND — mailbox_outbox exists instead

**Severity:** Medium — deployment discrepancy

**What the project map says:**
- `mailbox_ingest` at `/home/slimy/nuc-comms/mailbox_ingest`

**What exists on NUC1:**
- Only `mailbox_outbox` at `/home/slimy/nuc-comms/mailbox_outbox`
- `find /home/slimy/nuc-comms -maxdepth 2 -name ".git"` confirms only mailbox_outbox has a .git dir

**What this means:**
- Project map should be corrected: NUC1 has mailbox_outbox, not mailbox_ingest
- mailbox_ingest is the NUC2-side ingest process (referenced in NUC2's systemd units as `nuc-mailbox-ingest.service`)
- Cross-NUC flow: NUC1 mailbox_outbox (pushes) → NUC2 mailbox.git → NUC2 mailbox_ingest (processes)

**Action needed:** Update project map to use mailbox_outbox for NUC1, or clarify that mailbox_ingest is NUC2-only.

---

## Anomaly 2: .qoder-server/slimy-monorepo — ambiguous duplicate clone

**Severity:** Low — possible stale artifact

**What it is:**
- Separate clone of slimy-monorepo at `/home/slimy/.qoder-server/slimy-monorepo`
- Not a symlink — genuine separate repo clone
- Last commit `4e893be` 2026-04-04
- Canonical slimy-monorepo at `/opt/slimy/slimy-monorepo` has commit `cad0803` from today (2026-04-05)

**Runtime references:** NONE
- No cron, PM2, systemd, or Docker references
- openclaw.json does not reference it
- sync-repos.sh does not reference it

**Possible explanation:** qoder tool may have created its own clone, or this is a staging area for qoder-based development.

**Action needed:** Verify with qoder tooling if this path is actively used. Could be stale and safe to remove.

---

## Anomaly 3: research/kalshi-ai-trading-bot — LEGACY_CANDIDATE

**Severity:** Low — superseded by pm_updown_bot_bundle

**What it is:**
- Path: `/opt/slimy/research/kalshi-ai-trading-bot`
- Last commit: `fd65404` 2026-03-19

**Runtime evidence:** NONE
- No cron, PM2, systemd, or Docker references

**Context:** pm_updown_bot_bundle is the active trading automation (20+ cron entries, current commits). kalshi-ai-trading-bot appears to be a prototype that was superseded.

**Action needed:** Consider archiving or marking definitively as superseded. No active runtime dependency confirmed.

---

## Anomaly 4: slimyai-web NOT on NUC1

**Severity:** Informational — expected, not an error

**What it is:**
- slimyai-web runs on NUC2, not NUC1
- slimyAI.xyz/web is served from NUC2 port 3000
- NUC1's port 3000 serves slimy-bot-v2 (the Discord bot), not the web app

**Not an error** — per architecture, this is expected NUC placement.

---

## Anomaly 5: git-notes-ledger and workspace (project map) — UNCLEAR existence

**Severity:** Medium — need verification

**Project map says:**
- `git-notes-ledger` at `/home/slimy/.openclaw/memory/git-notes-ledger`
- `workspace` at `/home/slimy/.openclaw/workspace`

**Discovery did not confirm** — these paths were listed in the project map but not specifically scanned in the discovery pass.

**Action needed:** Verify these paths still exist and have not been superseded by the workspace-executor/workspace-researcher layout.

---

## Anomaly 6: agents (harness) — UNRELATED to SlimyAI runtime

**Severity:** Informational

**What it is:**
- `/home/slimy/.claude/agents` — Claude Code agent harness config
- Remote: https://github.com/wshobson/agents.git
- Not a SlimyAI project — part of the agent harness infrastructure

**Classification:** UNRELATED to SlimyAI production services.

---

## See Also
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md) — mailbox transport details
- [Mailbox NUC Comms](../projects/mailbox-nuc-comms.md) — NUC2 mailbox ingest side
- [PM UpDown Bot Bundle](../projects/pm-updown-bot-bundle.md) — active trading automation

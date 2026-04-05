# NUC2 Project Anomalies — 2026-04-05

**Date:** 2026-04-05
**Scope:** NUC2-only anomalies and ambiguous classifications

---

## Anomaly 1: slimyai-web standalone — LEGACY_CANDIDATE (NUC2)

**Project:** slimyai-web (standalone, `/opt/slimy/web/slimyai-web`)
**Classification:** LEGACY_CANDIDATE | Confidence: HIGH

**Evidence of supersession:**
- Branch: `fix/runtime-envs-check-2025-11-11-nuc2-snapshot` — a fix snapshot, not main
- Last commit: 2025-11-16 (5 months ago)
- slimy-web.service (systemd --user) serves from monorepo's `apps/web`, not from this standalone path
- Monorepo infra doc (`infra/docker/NUC2_STACK_STARTUP_FIX.md`) explicitly removes `slimyai-web-*` containers before starting the new stack

**Action:** Keep as LEGACY_CANDIDATE; do not start any services pointing to this path.

---

## Anomaly 2: agents-backup-full — LEGACY_CANDIDATE

**Project:** agents-backup-full (`/home/slimy/.claude/agents-backup-full`)
**Classification:** LEGACY_CANDIDATE | Confidence: MEDIUM

**Evidence:**
- Same remote as active `.claude/agents` (wshobson/agents)
- D (deleted file) in git index — partial deletion state
- No systemd, cron, PM2, or script references
- Superseded by `/home/slimy/.claude/agents`

**Action:** Consider archiving or deleting; currently provides no unique value.

---

## Anomaly 3: git-notes-ledger — UNKNOWN role

**Project:** git-notes-ledger (`/home/slimy/.openclaw/memory/git-notes-ledger`)
**Classification:** UNKNOWN | Confidence: LOW

**Evidence:**
- Local-only git repo (no remote)
- Last commit: 2026-01-28
- OpenCLAW internal memory subsystem — unclear if actively written to by any current process
- No PM2, systemd, cron references

**Action:** Mark as UNKNOWN; needs investigation to determine if this is active OpenCLAW state or stale.

---

## Anomaly 4: .codex plugins cache — UNKNOWN role

**Project:** .codex plugins (`/home/slimy/.codex/.tmp/plugins`)
**Classification:** UNKNOWN | Confidence: LOW

**Evidence:**
- Remote: `https://github.com/openai/plugins.git` (OpenAI Codex plugins)
- Last commit: 2026-03-30 (recent but not local work)
- `/home/slimy/.codex/.tmp/plugins` is a temporary cache directory
- No active runtime references found in systemd, cron, or PM2

**Action:** Mark as UNKNOWN; likely unused temp cache. Monitor for absence of references.

---

## Anomaly 5: ned-clawd — UNKNOWN role (not a git repo)

**Project:** ned-clawd (`/home/slimy/ned-clawd`)
**Classification:** UNKNOWN | Confidence: LOW

**Evidence:**
- Last commit: 2026-02-26 (ARCHITECTURE.md)
- Not a git repo (no remote, not tracked)
- ARCHITECTURE.md references slimy-monorepo and pm_updown_bot_bundle
- Operational directory with reports, config, memory, ops subdirectories
- No runtime evidence (PM2, systemd, cron)

**Action:** Mark as UNKNOWN; treat as a reference architecture doc, not an active service.

---

## Anomaly 6: slimy-web-health.service failure — AMBIGUOUS

**Service:** slimy-web-health.service (systemd --user)
**State:** FAILED
**Classification:** LEGACY_CANDIDATE | Confidence: MEDIUM

**Evidence:**
- References `/opt/slimy/ops/healthcheck.sh` which was not found at scan time
- `ops/` directory may have been cleaned up
- Service targets slimy_setup or monorepo health
- No new commits to ops/ directory recorded

**Action:** Likely stale; could be removed or restored depending on operational needs.

---

## Anomaly 7: mailbox bare repo vs mailbox_ingest — naming clarity

**Projects:** `.mcp_agent_mail_git_mailbox_repo` vs `nuc-comms/mailbox_ingest`
**Classification:** Informational

**Evidence:**
- `.mcp_agent_mail_git_mailbox_repo` — local bare repo for MCP agent mail; DORMANT, last commit Feb26
- `nuc-comms/mailbox_ingest` — NUC1→NUC2 ingest pipeline; ACTIVE
- Both use "mailbox" in name but are unrelated systems

**Action:** The wiki article `projects/mailbox-nuc-comms.md` covers the NUC-comms inbox, not the MCP agent mailbox. Keep separate. Do not merge.

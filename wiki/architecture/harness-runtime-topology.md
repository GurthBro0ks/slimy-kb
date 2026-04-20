# Harness Runtime Topology
> Category: architecture
> Sources: raw/decisions/seed-agents-rules.md, raw/decisions/seed-server-state.md, raw/agent-learnings/seed-progress-history.md, /home/slimy/AGENTS.md, /home/slimy/init.sh, /home/slimy/server-state.md, /home/slimy/feature_list.json, /home/slimy/claude-progress.md, /home/slimy/.config/systemd/user/slimy-web.service, /home/slimy/.config/systemd/user/mission-control.service, /home/slimy/.config/systemd/user/slimy-mysql-tunnel.service, /home/slimy/.config/systemd/user/nuc-mailbox-ingest.service, /home/slimy/.config/systemd/user/nuc-mailbox-ingest.timer, /home/slimy/nuc-comms/README.md, /home/slimy/nuc-comms/bin/nuc1_daily_report_run.sh, /home/slimy/nuc-comms/bin/nuc2_mailbox_ingest.sh, raw/decisions/2026-04-05-project-ned-autonomous-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc2-state.md, raw/decisions/2026-04-05-project-mission-control-nuc2-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc2-state.md, raw/decisions/2026-04-05-project-chriss-agent-nuc2-state.md, raw/decisions/2026-04-05-project-obsidian-headless-sync-nuc2-state.md, raw/research/2026-04-05-nuc1-project-discovery.md, raw/research/2026-04-05-nuc1-project-state-matrix.md, raw/research/2026-04-05-nuc2-project-discovery.md
> Created: 2026-04-04
> Updated: 2026-04-16
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-20 12:27 UTC (git)
> Version: r26 / 8e6c086
KB METADATA -->

This article maps where SlimyAI harness components live, who owns them at runtime, and how host-local vs shared controls interact.

## Layered Harness Model
| Layer | Scope | Location | Runtime Purpose |
|---|---|---|---|
| Global server harness | Host-local | `/home/slimy/{AGENTS.md,init.sh,feature_list.json,claude-progress.md,server-state.md}` | Session contract, repo discovery, and source-of-truth ledgers |
| Repo-local harness overlays | Per-repo | Present in selected repos (notably `slimy-monorepo` and `pm_updown_bot_bundle`) | Repo-specific startup rules, truth gates, and closeout controls |
| Knowledge harness | Host-local KB repo | `/home/slimy/kb/{raw,wiki,output,tools}` | Persistent knowledge capture and compiled operating docs |
| Mailbox comms harness | Cross-NUC transport implemented on NUC2 | `/home/slimy/nuc-comms` + user units `nuc-mailbox-ingest.*` | Pull, verify, and ingest NUC1 machine reports |

## Host-Local vs Shared Components
- Host-local controls: AGENTS contract, init repo discovery, service supervision (`systemd --user`), and local tunnel/mailbox timers.
- Shared across sessions (same host): `feature_list.json`, `claude-progress.md`, `server-state.md`, and KB wiki/raw content.
- Shared across hosts: Git remotes (GitHub) and mailbox report flow (`mailbox.git` push/pull + schema/SHA checks).

## Agent-Loop Placement
- `agent-loop` is on NUC1 (confirmed by NUC1 discovery 2026-04-05) as PM2 id=0.
- ned-autonomous (PM2 id=0, agent-loop) and slimy-bot-v2 (PM2 id=10) are both NUC1 PM2 processes.
- NUC2 runtime probes on 2026-04-04 show no local `agent-loop` unit/process — correct, it runs on NUC1.
- Operational rule: treat `agent-loop` as remote infrastructure from NUC2; do not infer local ownership because PM2 exists on NUC2 as well.

## Mailbox Transport Topology
1. NUC1 generates daily `report.json` and `report.sha256`, validates schema, and pushes to mailbox remote (`/home/slimy/nuc-comms/mailbox.git`) using a dedicated mailbox SSH key.
2. NUC2 runs `nuc-mailbox-ingest.timer` (every 10 minutes after boot grace), which triggers `nuc-mailbox-ingest.service`.
3. Ingest script clones mailbox, verifies schema and SHA, then atomically updates `/home/slimy/nuc-comms/mailbox_ingest/report.json`.
4. Restricted SSH guard (`mailbox-ssh-guard.sh`) limits mailbox key usage to `git-receive-pack`/`git-upload-pack` for the allowed bare repo.

## Supervisor Ownership (Observed 2026-04-04/05)

### NUC2 Services
| Service/Component | Expected Host | Active Supervisor | State |
|---|---|---|---|
| `slimy-web` | NUC2 | `systemd --user` (`slimy-web.service`) | Active |
| `mission-control` | NUC2 | `systemd --user` (`mission-control.service`) | Active |
| MySQL tunnel (`3307 -> nuc1:3306`) | NUC2 | `systemd --user` (`slimy-mysql-tunnel.service`) | Active |
| Mailbox ingest | NUC2 | `systemd --user` timer + oneshot service | Timer enabled; service activating |
| `chriss-agent` (webhook-bridge.py) | NUC2 | systemd (inferred `chriss-bridge.service`) | Active — port 3850 |
| `obsidian-headless-sync` | NUC2 | PM2 (id 0) | Online — sole PM2 process; startup disabled |
| openclaw-gateway | NUC2 | `systemd --user` (`openclaw-gateway.service`) | Active |
| slimy-web-health | NUC2 | `systemd --user` | Failed — healthcheck script missing |
| slimy-report | NUC2 | `systemd --user` | Failed |

### NUC1 Services (per NUC1 discovery 2026-04-05)
| Service/Component | Active Supervisor | State | Notes |
|---|---|---|---|
| `agent-loop` | PM2 (id=0) | online | ned-autonomous; 17.4mb |
| `slimy-bot-v2` | PM2 (id=10) | online | slimy-monorepo; port 3000 |
| `mission-control` | systemd (`mission-control.service`) | active | Port 3838 |
| `pm2-slimy` | systemd (`pm2-slimy.service`) | active | PM2 daemon itself |
| `tailscaled` | systemd | active | VPN |
| `slimy-chat` | Docker Compose | Up 2-5 weeks | 16 containers |

## Doc-Sync Hygiene (Phases 1–4, Complete)

The auto-sync doc commit system (`kb/tools/kb-project-doc-sync.sh`) had a systemic noise problem: every agent session finish would sweep all repos, unconditionally rewrite VERSION.md, and commit+push to any repo — including third-party and local-only repos. This caused divergence (mission-control 15/4), unrecoverable local commits, and noisy commit history.

**Root cause:** No guardrails on scope, no content-diff checks, no push failure handling, session-unbounded sweep.

### Phase 1 — Allowlist + Skip Guards (2026-04-16)
- **Allowlist enforcement:** `kb/config/doc-sync-allowlist.txt` — only 6 repos allowed. Non-listed repos skipped with log message. Missing file = allow all (safe fallback).
- **Dirty-tree skip:** repos with non-doc dirty files (anything outside README.md, CHANGELOG.md, VERSION.md) are skipped to prevent polluting auto-sync commits with unrelated changes.
- **Non-pushable/local-only skip:** repos with no `origin` remote are skipped entirely. Prevents accumulating commits that can never be pushed (e.g., `.mcp_agent_mail_git_mailbox_repo`).

### Phase 2 — Conditional Write + Push-or-Revert (2026-04-16)
- **Conditional VERSION.md:** only rewritten if content differs (md5 comparison excluding timestamp line). Eliminates spurious mtime/git noise commits.
- **Push-or-revert:** if `git push` fails after auto-sync commit, the commit is reverted (`git reset --soft HEAD~1`). Prevents local-only accumulation of auto-sync commits that cause divergence.

### Phase 3 — Session-Scoped Default (2026-04-16)
- **Default: no broad sweep.** `slimy-agent-finish.sh` without `--repo` or `--scan-all` touches zero repos.
- **`--scan-all` explicit opt-in:** broad multi-repo detection requires this flag.
- **`--repo /path` bounded:** only the specified repo (existing behavior, unchanged).
- **NUC1 stop-hook wiring:** active repo passed through session-finish correctly.

### Phase 4 — Daily Dedupe (2026-04-16)
- **Same-day skip:** if HEAD commit subject matches `docs: auto-sync project docs from <host> YYYY-MM-DD`, and no doc files are dirty, skip entirely.
- **Smart override:** if there ARE dirty doc files (something new happened), re-sync with a note log.

### Result
Broad/noisy multi-repo doc-sync behavior is no longer the default. Doc-sync is now session-scoped, allowlisted, content-diff gated, push-safe, and daily-deduped.

## Known Harness Failure Modes
- Supervisor drift: service ownership confusion between PM2 and systemd causes restart loops and false recovery attempts.
- Ledger drift: stale `server-state.md` or missing closeout updates cause bad restart decisions.
- Cross-NUC dependency drift: tunnel up but DB grant missing still blocks reads (`slimy@172.18.0.1` access denied).
- Mailbox integrity breaks: missing payload artifacts or checksum/schema failures halt ingest.
- Session finish divergence: stop hook scripts on different NUCs or branches run different finish automation (sync hygiene guardrail detects this — see Check 9 in validate-harness.sh).
- ~~Doc-sync noise: VERSION.md unconditional rewrite + broad sweep causes spurious commits across all repos~~ — **RESOLVED** by doc-sync hygiene Phases 1–4.

## Sync Hygiene Guardrail

`slimy-harness/scripts/check-sync-state.sh` runs as Check 9 in `validate-harness.sh`. It detects when the harness has diverged from `origin/main` and warns, preventing stale finish-hook logic from running.

Divergence categories detected:
- **Ahead only:** local commits not pushed — may indicate untracked finish hook changes
- **Behind only:** origin has commits not locally merged — finish hook logic may be out of date
- **Diverged:** both sides have commits — highest risk of stale/buggy finish behavior running

Also covers: untracked files (may contain ad-hoc finish hook edits) and detached HEAD state (no canonical branch for comparison).

## Session Finish Behavior (Stop Hook)

The harness Stop hook (`slimy-session-finish.sh`) dispatches based on how the session ended:

| Exit Type | Cause | Action | Discord ALERT |
|-----------|-------|--------|---------------|
| **INTERRUPTED** | Ctrl+C / SIGINT | Skip all finish automation, exit quietly | NO |
| **SUCCESS** (exit 0) | Normal completion | Bounded quiet finish: kb-compile, sync active repo only | NO |
| **ERROR** (exit ≠0) | Non-zero exit | Bounded finish with alerts: sync active repo, post ALERT on failure | YES (bounded) |

**Bounded scope** means only the active repo is touched — no multi-repo scan of `/home/slimy` or `/opt/slimy`. The `--repo` flag on `slimy-agent-finish.sh` activates bounded mode (skips auto-detection scan). The `--quiet` flag suppresses ALERT posting.

Since Phase 3 (doc-sync hygiene), the default behavior of `slimy-agent-finish.sh` with no flags is to touch zero repos (session-scoped). Broad multi-repo scan requires explicit `--scan-all` flag. See Doc-Sync Hygiene section above.

Recursion guard: `SLIMY_AUTOFINISH_ACTIVE=1` prevents nested finish runs.

**DO NOT "fix" this behavior** — it was intentionally designed to stop Discord ALERT spam and multi-repo push sweeps on interrupt. See `/home/slimy/slimy-harness/proofs/stop-hook-fix-001/FLOW_DIAGRAM.md` for the full dispatch logic.

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [Knowledge Base Build Pipeline](knowledge-base-build-pipeline.md)
- [Cross-NUC Communication Matrix](cross-nuc-communication-matrix.md)
- [NUC Topology and Services](nuc-topology-and-services.md)
- [Chriss Agent](../projects/chriss-agent.md)
- [Obsidian Headless Sync](../projects/obsidian-headless-sync.md)

# Harness Runtime Topology
> Category: architecture
> Sources: raw/decisions/seed-agents-rules.md, raw/decisions/seed-server-state.md, raw/agent-learnings/seed-progress-history.md, /home/slimy/AGENTS.md, /home/slimy/init.sh, /home/slimy/server-state.md, /home/slimy/feature_list.json, /home/slimy/claude-progress.md, /home/slimy/.config/systemd/user/slimy-web.service, /home/slimy/.config/systemd/user/mission-control.service, /home/slimy/.config/systemd/user/slimy-mysql-tunnel.service, /home/slimy/.config/systemd/user/nuc-mailbox-ingest.service, /home/slimy/.config/systemd/user/nuc-mailbox-ingest.timer, /home/slimy/nuc-comms/README.md, /home/slimy/nuc-comms/bin/nuc1_daily_report_run.sh, /home/slimy/nuc-comms/bin/nuc2_mailbox_ingest.sh
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

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
- Contract source places `agent-loop` on NUC1 as an active service boundary.
- NUC2 runtime probes on 2026-04-04 show no local `agent-loop` unit/process ownership.
- Operational rule: treat `agent-loop` as remote infrastructure from NUC2; do not infer local ownership because PM2 exists.

## Mailbox Transport Topology
1. NUC1 generates daily `report.json` and `report.sha256`, validates schema, and pushes to mailbox remote (`/home/slimy/nuc-comms/mailbox.git`) using a dedicated mailbox SSH key.
2. NUC2 runs `nuc-mailbox-ingest.timer` (every 10 minutes after boot grace), which triggers `nuc-mailbox-ingest.service`.
3. Ingest script clones mailbox, verifies schema and SHA, then atomically updates `/home/slimy/nuc-comms/mailbox_ingest/report.json`.
4. Restricted SSH guard (`mailbox-ssh-guard.sh`) limits mailbox key usage to `git-receive-pack`/`git-upload-pack` for the allowed bare repo.

## Supervisor Ownership (Observed on NUC2, 2026-04-04)
| Service/Component | Expected Host | Active Supervisor | State |
|---|---|---|---|
| `slimy-web` | NUC2 | `systemd --user` (`slimy-web.service`) | Active |
| `mission-control` | NUC2 | `systemd --user` (`mission-control.service`) | Active |
| MySQL tunnel (`3307 -> nuc1:3306`) | NUC2 | `systemd --user` (`slimy-mysql-tunnel.service`) | Active |
| Mailbox ingest | NUC2 | `systemd --user` timer + oneshot service | Timer enabled; service runs on schedule |
| PM2 daemon | NUC2 | PM2 god daemon present | No managed app processes currently listed |
| `agent-loop` | NUC1 | NUC1-owned runtime boundary (per AGENTS/server-state) | Not locally observed on NUC2 |

## Known Harness Failure Modes
- Supervisor drift: service ownership confusion between PM2 and systemd causes restart loops and false recovery attempts.
- Ledger drift: stale `server-state.md` or missing closeout updates cause bad restart decisions.
- Cross-NUC dependency drift: tunnel up but DB grant missing still blocks reads (`slimy@172.18.0.1` access denied).
- Mailbox integrity breaks: missing payload artifacts or checksum/schema failures halt ingest.

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [Cross-NUC Communication Matrix](cross-nuc-communication-matrix.md)
- [NUC Topology and Services](nuc-topology-and-services.md)

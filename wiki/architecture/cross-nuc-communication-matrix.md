# Cross-NUC Communication Matrix
> Category: architecture
> Sources: raw/decisions/seed-agents-rules.md, raw/decisions/seed-server-state.md, raw/agent-learnings/seed-progress-history.md, /home/slimy/server-state.md, /etc/hosts, /home/slimy/.ssh/config, /home/slimy/.config/systemd/user/slimy-mysql-tunnel.service, /home/slimy/.config/systemd/user/slimy-web.service, /home/slimy/.config/systemd/user/mission-control.service, /home/slimy/nuc-comms/README.md, /home/slimy/nuc-comms/bin/nuc1_daily_report_run.sh, /home/slimy/nuc-comms/bin/nuc2_mailbox_ingest.sh, /home/slimy/nuc-comms/bin/mailbox-ssh-guard.sh, /opt/slimy/slimy-monorepo/apps/web/.env, /opt/slimy/slimy-monorepo/apps/web/.env.local, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc1-state.md, raw/research/2026-04-05-nuc1-project-anomalies.md
> Created: 2026-04-04
> Updated: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 00:23 UTC (git)
> Version: r8 / f081b71
KB METADATA -->

This matrix documents the known communication paths between NUC1 and NUC2, with ownership and failure signatures.

## Channel Matrix
| Channel | Protocol | Direction | Auth Method | Owner | Known Failure Signatures |
|---|---|---|---|---|---|
| Club DB data path (`apps/web` -> NUC1 MySQL) | MySQL over SSH local forward (`127.0.0.1:3307 -> nuc1:3306`) | NUC2 -> NUC1 | SSH key to `nuc1-lan` plus MySQL credentials | NUC2 tunnel unit + NUC1 MySQL grant policy | `ERROR 1045 (28000): Access denied for user 'slimy'@'172.18.0.1'`; connection refused before tunnel exists |
| MySQL tunnel control path (`slimy-mysql-tunnel.service`) | SSH (`ssh -N -L`) | NUC2 -> NUC1 | `~/.ssh/id_ed25519` host key trust | NUC2 systemd user service | Tunnel unit down; local port `3307` unavailable; SSH handshake timeout |
| Bot API path (`BOT_API_URL`) | HTTP over Tailscale | NUC2 -> NUC1 (`100.106.127.22:8510`) | Tailscale device identity + app-level API controls | App owner for bot/web integration | `ECONNREFUSED`/timeout when bot endpoint is unreachable |
| Edge reverse-proxy hop for Mission Control | HTTP reverse proxy behind TLS edge | NUC1 edge -> NUC2 `mission-control:3838` | TLS at edge, app auth/cookies in Mission Control | NUC1 edge routing + NUC2 `mission-control.service` | Proxy 502/blank page when backend or route wiring drifts |
| Operator shell/ops channel | SSH (`work-nuc1`, `nuc1-lan`) | NUC2 operator -> NUC1 | SSH key auth | Human operators + host SSH policy | Port mismatch/refused (for example `4421` vs LAN `22`) |
| Repo sync channel | Git over SSH to GitHub (`git@github.com`) | NUC1 and NUC2 <-> GitHub | GitHub SSH key auth | Per-repo maintainers | Non-fast-forward/divergent branch states; stale local main |
| NUC mailbox transport (daily report) | Git mailbox + SHA/schema verification | NUC1 push -> NUC2 bare mailbox repo -> NUC2 ingest copy | Restricted mailbox key + `mailbox-ssh-guard.sh` + JSON schema + SHA256 | NUC1 report producer + NUC2 ingest timer/service | `missing report.json`, `missing report.sha256`, `schema validation failed`, `sha mismatch` |

> **Note (2026-04-05):** On NUC1 the local mailbox repo is named `mailbox_outbox` (at `/home/slimy/nuc-comms/mailbox_outbox`), not `mailbox_ingest` as the project map suggests. NUC1 is the push side; NUC2 holds the bare `mailbox.git` and runs the ingest service. The project map should reflect `mailbox_outbox` for NUC1. See [Mailbox NUC Comms](../projects/mailbox-nuc-comms.md).

## Runtime Anchors (Observed 2026-04-04)
- Tailscale sees both nodes online (`slimy-nuc1` at `100.106.127.22`, `slimy-nuc2` at `100.105.119.62`).
- `/etc/hosts` includes LAN and Tailscale naming anchors (`slimy-db`, `nuc1-ts`, `nuc2-ts`).
- `slimy-mysql-tunnel.service` is active and runs `ssh -N -L 3307:localhost:3306 nuc1-lan`.
- `apps/web/.env` points club MySQL traffic to `127.0.0.1:3307`.
- Live probe through that path returns access denied for `slimy@172.18.0.1`, matching the known NUC1 grant issue.

## Governance Principles
- Cross-NUC channels are explicit and least-privilege by default (dedicated tunnel, dedicated mailbox key guard, explicit route ownership).
- NUC2 should not assume direct trust to NUC1 databases; access must pass through explicit tunnel + grants.
- All channel health and ownership decisions must reconcile with `server-state.md` and AGENTS truth tables before restarts.

## See Also
- [NUC Topology and Services](nuc-topology-and-services.md)
- [Harness Runtime Topology](harness-runtime-topology.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)

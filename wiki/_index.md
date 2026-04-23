# SlimyAI Knowledge Base - Master Index
> Auto-maintained by LLM agents. Do not edit manually.
> Last compiled: 2026-04-14 (child-compile 20260414-181150 — re-verified all priority batch files: seed-clawd-agents.md/seed-workspace-agents.md/seed-agents-rules.md/seed-progress-history.md/seed-server-state.md already sourced or deferred (unchanged); all 2026-04-05 research/agent-learning files (NUC1/NUC2 SSH normalization, autofinish/autocompile-fix, no-pager fix, wrapper recursion fix, wrapper test) already sourced into troubleshooting articles; no new wiki content required; status: reviewed)

<!-- KB METADATA
> Last edited: 2026-04-23 00:30 UTC (git)
> Version: r71 / 19467b1
KB METADATA -->

---

## Start Here

If you are opening this KB for the first time or need orientation:

1. **[[Home|Home (Vault Dashboard)]]** — your daily landing page in Obsidian; system health, daily ops, quick actions
2. **[[Operator Console]]** — decision page: what needs attention right now, triage order, next moves
3. **[[Wiki Manager Operator Runbook|wiki-manager-operator-runbook]]** — how the automated wiki-manager pipeline works on NUC2
4. **[_page-types](_page-types.md)** — the 9 standard page types used across this wiki
5. **[_manager-status](_manager-status.md)** — current wiki-manager queue snapshot (auto-updated)

---

## Core Operational Pages

These are the pages you will reach for most often during day-to-day operations:

| Page | What It Gives You |
|------|-------------------|
| [NUC Topology and Services](architecture/nuc-topology-and-services.md) | Which services run on which NUC, ports, supervisors |
| [NUC2 Current State](architecture/nuc2-current-state.md) | Live NUC2 host/service/port state from local digest |
| [NUC1 Current State](architecture/nuc1-current-state.md) | Live NUC1 state from cross-NUC digest |
| [Cross-NUC Communication Matrix](architecture/cross-nuc-communication-matrix.md) | Channel-by-channel map of NUC1/NUC2 transport and auth |
| [Knowledge Base Build Pipeline](architecture/knowledge-base-build-pipeline.md) | Raw-to-wiki lifecycle: intake, compile, sync, vault mirror |
| [Harness Runtime Topology](architecture/harness-runtime-topology.md) | Where harness, mailbox, and runtime control live |
| [Auth and Retired Services](architecture/auth-and-retired-services.md) | Current auth stack and intentionally dead services |
| [Source of Truth Ledgers](concepts/source-of-truth-ledgers.md) | Which files are canonical records for what |
| [Truth Gate](concepts/truth-gate.md) | When is work actually "done" — verification model |
| [Agent Session Contract](concepts/agent-session-contract.md) | Shared multi-repo startup/execution/closeout contract |

---

## Page Type Legend

| Type | Prefix/Location | Purpose |
|------|----------------|---------|
| **entity** | `projects/`, `architecture/` | Named things: services, repos, bots, hosts |
| **concept** | `concepts/` | Abstract reusable ideas and principles |
| **pattern** | `patterns/` | Reusable operational patterns |
| **troubleshooting** | `troubleshooting/` | Problem → cause → fix records |
| **overview** | `architecture/*-state.md` | State-of-the-world summaries |
| **index** | `_*.md` | Curated lists (auto-maintained) |
| **log** | `log.md` | Append-only event log |
| **decision** | Various | Recorded decisions with rationale |
| **source** | N/A in wiki | Raw input docs live in `raw/` |

---

## Architecture

The structural and operational backbone of the system:

- [NUC Topology and Services](architecture/nuc-topology-and-services.md) — **Start here for infra questions.** NUC1/NUC2 service placement, ports, supervisors, and operational boundaries.
- [NUC2 Server State](architecture/nuc2-server-state.md) — Canonical NUC2 server state: machine, repos, PM2, MySQL.
- [NUC2 Current State](architecture/nuc2-current-state.md) — Live NUC2 host/service/port state from local digest.
- [NUC1 Current State](architecture/nuc1-current-state.md) — Live NUC1 host/repo/service state from cross-NUC digest.
- [Cross-NUC Communication Matrix](architecture/cross-nuc-communication-matrix.md) — Channel-by-channel map: transport, auth, ownership, failure modes.
- [Harness Runtime Topology](architecture/harness-runtime-topology.md) — Placement and supervisor ownership of harness, mailbox, runtime control, and doc-sync hygiene.
- [Knowledge Base Build Pipeline](architecture/knowledge-base-build-pipeline.md) — Canonical raw-to-wiki, query/file-back, index maintenance, and cross-NUC sync lifecycle.
- [SlimyAI Login and Session Flow](architecture/slimyai-login-and-session-flow.md) — Credential login, session lifecycle, invite gating, and recovery/lockout behavior.
- [Auth and Retired Services](architecture/auth-and-retired-services.md) — Current auth stack and intentionally dead services (do not resurrect).
- [Wiki Manager Operator Runbook](wiki-manager-operator-runbook.md) — How the automated wiki-manager Stage 1.86 pipeline works: timers, outputs, candidate promotion, troubleshooting.

---

## Concepts

Reusable ideas that apply across projects and services:

- [Agent Session Contract](concepts/agent-session-contract.md) — Shared multi-repo operating contract for startup, execution, and closeout. Every agent session follows this.
- [Source of Truth Ledgers](concepts/source-of-truth-ledgers.md) — Canonical records that track execution history, feature status, and server health. Knows which file is the authority for what.
- [Truth Gate](concepts/truth-gate.md) — Verification model defining when work is actually complete. A pass means lint + tests + manual checks all green.

---

## Patterns

Operational patterns that recur across the system:

- [Memory Capture Pattern](patterns/memory-capture-pattern.md) — Daily log plus curated-memory method for durable agent learning. Used by Clawd, ned-clawd, and OpenCLAW workspace agents.
- [Session Closeout Pattern](patterns/session-closeout-pattern.md) — Required end-of-session sequence and quality checks. Every agent session must follow this before terminating.

---

## Projects

### Core Infrastructure

These are the primary production services and active development projects:

| Project | Summary |
|---------|---------|
| [Slimy Monorepo](projects/slimy-monorepo.md) | **Primary web app.** Next.js at slimyai.xyz on NUC2 port 3000. Owner panel, snail club/stats, crypto trading tab, trader dashboard. |
| [Slimy Web](projects/slimy-web.md) | Next.js web app capabilities, env wiring, and runtime expectations (part of monorepo). |
| [Mission Control](projects/mission-control.md) | **Task and agent coordination surface.** Retro-styled command center on NUC2 port 3838 with REST API for tasks, agents, calendar, comms, memory. |
| [Slimy KB](projects/slimy-kb.md) | **This knowledge base.** Git-based wiki with raw-to-compiled pipeline, CLI tools, cross-NUC sync. |
| [Clawd](projects/clawd.md) | **OpenClAW daemon.** Workspace governance, autonomous agent, memory management on NUC1. |
| [PM UpDown Bot Bundle](projects/pm-updown-bot-bundle.md) | Polymarket trading bot bundle (Python). NUC1 primary, NUC2 dormant. Strategies, venues, ML pipeline. |

### Chat Platform

| Project | Summary |
|---------|---------|
| [Chat App (Slime.Chat)](projects/chat-app.md) | Self-hosted 16-container Docker chat at chat.slimyai.xyz. Stoat/Revolt fork, invite-only, NUC1. |
| [Slimy Chat](projects/slimy-chat.md) | Revolt-based invite-only chat stack and auth flow (NUC1 perspective). |
| [Stoat Source](projects/stoat-source.md) | Rust backend for Revolt/Stoat chat platform. 12 crates (delta REST API, bonfire WebSocket, services). Powers the Docker stack. |

### Agent / AI Infrastructure

| Project | Summary |
|---------|---------|
| [Ned-Clawd](projects/ned-clawd.md) | AI agent workspace with Mission Control integration. Runs agent registration cron. Hosts actionbook as subdirectory. NUC1. |
| [OpenCLAW Agents](projects/openclaw-agents.md) | Workspace subagents (executor/researcher) managed by the OpenCLAW gateway on NUC1. |
| [Workspace Executor](projects/workspace-executor.md) | Execution subagent in the OpenCLAW agent hierarchy. Registered with gateway, local-only. |
| [Workspace Researcher](projects/workspace-researcher.md) | Research subagent in the OpenCLAW agent hierarchy. Registered with gateway, local-only. |
| [Actionbook](projects/actionbook.md) | Browser Action Engine for AI Agents via MCP protocol. 12-package pnpm monorepo providing DOM selectors so agents can operate websites. |
| [Kalshi AI Trading Bot](projects/kalshi-ai-trading-bot.md) | Five-LLM ensemble trading bot for Kalshi prediction markets. Consensus-based entry with risk guardrails. Experimental, NUC1. |
| [Clawd Agent Rules](projects/clawd-agent-rules.md) | Workspace agent operating rules: session startup, memory tiers, safety, heartbeats, meta-learning loops. |
| [Clawd Workspace Governance](projects/clawd-workspace-governance.md) | Memory and session governance model for Clawd workspace operations. |
| [Workspace Agent Rules](projects/workspace-agent-rules.md) | OpenCLAW workspace agent rules: session startup, SLB-required actions, heartbeat vs cron, meta-learning loops. |

### Inter-NUC Communication

| Project | Summary |
|---------|---------|
| [Mailbox NUC Comms](projects/mailbox-nuc-comms.md) | Git-based inter-NUC mailbox transport (NUC1 push / NUC2 ingest). |
| [Mailbox Ingest (NUC Comms)](projects/mailbox-ingest.md) | NUC2 ingest side of the git-based inter-NUC mailbox transport. |
| [Mailbox Outbox](projects/mailbox-outbox.md) | NUC1 push side of inter-NUC mailbox via SSH/git sync to NUC2. |
| [MCP Agent Mailbox](projects/mcp-agent-mailbox.md) | MCP agent git mailbox for inter-agent communication. Local-only on NUC2. No remote push URL. |

### NUC2 Automation & Ops

| Project | Summary |
|---------|---------|
| [Obsidian Vault Automation](projects/obsidian-vault-automation.md) | Server-side vault automation: daily notes, operator todo, AI recommendations, idea ingest, changelog rollup, version scanning. The glue between human capture and canonical KB. |
| [Obsidian Headless Sync](projects/obsidian-headless-sync.md) | Sole PM2 process on NUC2. Provides vault synchronization for Obsidian notes. |
| [Chriss Agent](projects/chriss-agent.md) | Webhook bridge service on NUC2 port 3850. Python-based, running since March 2026. |
| [Capture Dashboard](projects/capture-dashboard.md) | Operator intake surface with folder map, quick actions, and ingest-compile-sync checklist. |
| [Operator Console](projects/operator-console.md) | KB operations decision tree — conflicts, inbox, compile, capture/query in order. |

### Archived / Dormant

| Project | Summary |
|---------|---------|
| [Agents Backup Full](projects/agents-backup-full.md) | Full mirror of wshobson/agents Claude Code plugin marketplace (112 agents, 146 skills, 72 plugins). Read-only archive on NUC2. |
| [Apify Market Scanner](projects/apify-market-scanner.md) | Apify-based market data scraping tool. MAINTENANCE/IDLE — not actively deployed, no running services. |
| [Slimyai Setup](projects/slimyai-setup.md) | Old JS Discord bot; superseded by slimy-bot-v2 in monorepo. Not running. |
| [NUC1 Project Anomalies](projects/nuc1-project-anomalies.md) | NUC1 project discovery anomalies: mailbox_outbox naming, duplicate monorepo clone, legacy kalshi bot, unclear workspace paths. |
| [Repo Health Overview](projects/repo-health-overview.md) | Cross-NUC repo status: dirty and diverged repos from digest evidence. |

---

## Troubleshooting

Problems encountered and resolved — reusable fix signatures:

- [Q1 2026 Operational Fixes](troubleshooting/q1-2026-operational-fixes.md) — Reusable failure signatures and proven fixes from recent operations. Good starting point for "has this broken before?"
- [KB Autofinish Autocompile Fix](troubleshooting/kb-autofinish-autocompile-fix.md) — Fix for KB write-through where finish hook left raw files uncommitted, auto-compile only wrote prompt files, and git pager blocked wrapper-triggered automation.
- [NUC1 Repo Remote SSH Normalization](troubleshooting/nuc1-repo-remote-ssh-normalization.md) — Normalized GitHub remotes to SSH on NUC1; all GurthBro0ks repos use SSH, third-party repos guarded.
- [NUC1 Wrapper Recursion Fix](troubleshooting/nuc1-wrapper-recursion-fix.md) — Fix for NUC1 wrapper recursion guard interference causing finish-hook behavior drift and child-compile protection failures.
- [NUC2 Repo Remote SSH Normalization](troubleshooting/nuc2-repo-remote-ssh-normalization.md) — Normalized GitHub remotes to SSH on NUC2; `agents-backup-full` converted from HTTPS.

# SlimyAI Knowledge Base - Master Index
> Auto-maintained by LLM agents. Do not edit manually.
> Last compiled: 2026-04-09 (child-compile 20260409-141401 — all candidates reviewed: 12 files checked, 0 new wiki articles needed)

## Categories
### Concepts
- [Agent Session Contract](concepts/agent-session-contract.md) - Shared multi-repo operating contract for startup, execution, and closeout.
- [Source of Truth Ledgers](concepts/source-of-truth-ledgers.md) - Canonical records that track execution history, feature status, and server health.
- [Truth Gate](concepts/truth-gate.md) - Verification model defining when work is actually complete.

### Projects
- [Actionbook](projects/actionbook.md) - Browser Action Engine for AI Agents via MCP protocol; 12-package pnpm monorepo.
- [Agents Backup Full](projects/agents-backup-full.md) - Mirror of wshobson/agents Claude Code plugin marketplace; archived, not actively used.
- [Agents Plugin Ecosystem](projects/agents-plugin-ecosystem.md) - Plugin/agent/skill orchestration system for focused capability loading.
- [Apify Market Scanner](projects/apify-market-scanner.md) - Apify-based market data scraping tool; runtime status UNKNOWN.
- [Capture Dashboard](projects/capture-dashboard.md) - Operator intake surface with folder map, quick actions, and ingest-compile-sync checklist.
- [Chat App (Slime.Chat)](projects/chat-app.md) - Self-hosted 16-container Docker chat platform at chat.slimyai.xyz; Stoat/Revolt fork.
- [Chriss Agent](projects/chriss-agent.md) - Webhook bridge service on NUC2 port 3850; running since Mar14.
- [Clawd](projects/clawd.md) - OpenClaw workspace daemon for SlimyAI with session/memory governance; NUC1.
- [Clawd Agent Rules](projects/clawd-agent-rules.md) - SlimyAI workspace agent operating rules: session startup, memory tiers, safety, heartbeats, meta-learning loops.
- [Clawd Workspace Governance](projects/clawd-workspace-governance.md) - Memory and session governance model for Clawd workspace operations.
- [Kalshi AI Trading Bot](projects/kalshi-ai-trading-bot.md) - Five-LLM ensemble trading bot for Kalshi prediction markets; experimental, NUC1.
- [Mailbox Ingest (NUC Comms)](projects/mailbox-ingest.md) - NUC2 ingest side of git-based inter-NUC mailbox transport.
- [Mailbox NUC Comms](projects/mailbox-nuc-comms.md) - Git-based inter-NUC mailbox transport (NUC1 push / NUC2 ingest).
- [Mailbox Outbox](projects/mailbox-outbox.md) - NUC1 push side of inter-NUC mailbox via SSH/git sync to NUC2.
- [MCP Agent Mailbox](projects/mcp-agent-mailbox.md) - MCP agent git mailbox for inter-agent communication; local-only, NUC2.
- [Mission Control](projects/mission-control.md) - Task, comms, and automation coordination surface (NUC2 port 3838).
- [Ned-Autonomous](projects/ned-autonomous.md) - PM2 agent-loop orchestrator on NUC1 (id=0).
- [Ned-Clawd](projects/ned-clawd.md) - AI agent workspace with Mission Control integration scripts; NUC1.
- [Obsidian Headless Sync](projects/obsidian-headless-sync.md) - Sole PM2 process on NUC2; vault synchronization.
- [Obsidian Vault Automation](projects/obsidian-vault-automation.md) - Server-side vault automation scripts: daily calendar sync, operator todo, AI recommendations, idea ingest, changelog rollup.
- [NUC1 Project Anomalies](projects/nuc1-project-anomalies.md) - NUC1 project discovery anomalies: mailbox_outbox naming, duplicate monorepo clone, legacy kalshi bot, unclear workspace paths.
- [OpenCLAW Agents](projects/openclaw-agents.md) - OpenCLAW workspace subagents (executor/researcher) on NUC1.
- [Operator Console](projects/operator-console.md) - NUC2 KB operations decision tree — conflicts, inbox, compile, capture/query in order.
- [PM UpDown Bot Bundle](projects/pm-updown-bot-bundle.md) - Trading-bot bundle structure, guardrails, and truth-gate workflow (NUC1 primary, NUC2 dormant).
- [Slimyai Setup](projects/slimyai-setup.md) - Old JS Discord bot; superseded by slimy-bot-v2 in monorepo; not running.
- [Slimy Chat](projects/slimy-chat.md) - Revolt-based invite-only chat stack and auth flow.
- [Slimy Discord Bot](projects/slimy-discord-bot.md) - AI-enabled Discord bot architecture, conventions, and verification commands.
- [Slimy KB](projects/slimy-kb.md) - SlimyAI knowledge base — git-based wiki with raw-to-compiled pipeline and CLI tools.
- [Slimy Monorepo](projects/slimy-monorepo.md) - Core multi-app repo structure, workflow, and constraints (NUC2: web on port 3000).
- [Slimy Web](projects/slimy-web.md) - Next.js web app capabilities, env wiring, and runtime expectations.
- [Stoat Source](projects/stoat-source.md) - Rust backend for Revolt/Stoat chat platform; powers slimy-chat Docker stack.
- [Workspace Agent Rules](projects/workspace-agent-rules.md) - OpenCLAW workspace agent operating rules: session startup, SLB-required actions, heartbeat vs cron, meta-learning loops.
- [Workspace Executor](projects/workspace-executor.md) - OpenClaw workspace executor subagent; registered with gateway on NUC1.
- [Workspace Researcher](projects/workspace-researcher.md) - OpenClaw workspace researcher subagent; registered with gateway on NUC1.

### Patterns
- [Memory Capture Pattern](patterns/memory-capture-pattern.md) - Daily log plus curated-memory method for durable learning.
- [Session Closeout Pattern](patterns/session-closeout-pattern.md) - Required end-of-session sequence and quality checks.

### Troubleshooting
- [KB Autofinish Autocompile Fix](troubleshooting/kb-autofinish-autocompile-fix.md) - Fix for KB write-through where finish hook left raw files uncommitted, auto-compile only wrote prompt files, and git pager blocked wrapper-triggered automation.
- [NUC1 Repo Remote SSH Normalization](troubleshooting/nuc1-repo-remote-ssh-normalization.md) - Normalized GitHub remotes to SSH on NUC1; all GurthBro0ks repos use SSH, third-party repos guarded, KB write-through completes regardless.
- [NUC1 Wrapper Recursion Fix](troubleshooting/nuc1-wrapper-recursion-fix.md) - Fix for NUC1 wrapper recursion guard interference that caused finish-hook behavior drift and child-compile protection failures.
- [NUC2 Repo Remote SSH Normalization](troubleshooting/nuc2-repo-remote-ssh-normalization.md) - Normalized GitHub remotes to SSH on NUC2; `agents-backup-full` converted from HTTPS, HTTPS repos guarded by `is_https_github_remote()`.
- [Q1 2026 Operational Fixes](troubleshooting/q1-2026-operational-fixes.md) - Reusable failure signatures and proven fixes from recent operations.

### Architecture
- [Auth and Retired Services](architecture/auth-and-retired-services.md) - Current auth stack and intentionally dead services.
- [Cross-NUC Communication Matrix](architecture/cross-nuc-communication-matrix.md) - Channel-by-channel map of NUC1/NUC2 transport, auth, ownership, and failures.
- [Harness Runtime Topology](architecture/harness-runtime-topology.md) - Placement and supervisor ownership of harness, mailbox, and runtime control components.
- [Knowledge Base Build Pipeline](architecture/knowledge-base-build-pipeline.md) - Canonical raw-to-wiki, query/file-back, index maintenance, and cross-NUC sync lifecycle.
- [NUC2 Server State](architecture/nuc2-server-state.md) - Canonical server state for slimy-nuc2: machine, repos, PM2, MySQL.
- [NUC Topology and Services](architecture/nuc-topology-and-services.md) - NUC1/NUC2 service placement and operational boundaries.
- [SlimyAI Login and Session Flow](architecture/slimyai-login-and-session-flow.md) - Canonical credential login, session lifecycle, invite gating, and recovery/lockout behavior.

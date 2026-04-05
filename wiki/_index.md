# SlimyAI Knowledge Base - Master Index
> Auto-maintained by LLM agents. Do not edit manually.
> Last compiled: 2026-04-05

## Categories
### Concepts
- [Agent Session Contract](concepts/agent-session-contract.md) - Shared multi-repo operating contract for startup, execution, and closeout.
- [Source of Truth Ledgers](concepts/source-of-truth-ledgers.md) - Canonical records that track execution history, feature status, and server health.
- [Truth Gate](concepts/truth-gate.md) - Verification model defining when work is actually complete.

### Projects
- [Agents Plugin Ecosystem](projects/agents-plugin-ecosystem.md) - Plugin/agent/skill orchestration system for focused capability loading.
- [Apify Market Scanner](projects/apify-market-scanner.md) - Apify-based market data scraping tool; runtime status UNKNOWN.
- [Capture Dashboard](projects/capture-dashboard.md) - Operator intake surface with folder map, quick actions, and ingest-compile-sync checklist.
- [Clawd Workspace Governance](projects/clawd-workspace-governance.md) - Memory and session governance model for Clawd workspace operations.
- [Mailbox NUC Comms](projects/mailbox-nuc-comms.md) - Git-based inter-NUC mailbox transport (NUC1 push side).
- [Mission Control](projects/mission-control.md) - Task, comms, and automation coordination surface.
- [Ned-Autonomous](projects/ned-autonomous.md) - PM2 agent-loop orchestrator on NUC1 (id=0).
- [OpenCLAW Agents](projects/openclaw-agents.md) - OpenCLAW workspace subagents (executor/researcher) on NUC1.
- [Operator Console](projects/operator-console.md) - NUC2 KB operations decision tree — conflicts, inbox, compile, capture/query in order.
- [PM UpDown Bot Bundle](projects/pm-updown-bot-bundle.md) - Trading-bot bundle structure, guardrails, and truth-gate workflow.
- [Slimy Chat](projects/slimy-chat.md) - Revolt-based invite-only chat stack and auth flow.
- [Slimy Discord Bot](projects/slimy-discord-bot.md) - AI-enabled Discord bot architecture, conventions, and verification commands.
- [Slimy Monorepo](projects/slimy-monorepo.md) - Core multi-app repo structure, workflow, and constraints.
- [Slimy Web](projects/slimy-web.md) - Next.js web app capabilities, env wiring, and runtime expectations.

### Patterns
- [Memory Capture Pattern](patterns/memory-capture-pattern.md) - Daily log plus curated-memory method for durable learning.
- [Session Closeout Pattern](patterns/session-closeout-pattern.md) - Required end-of-session sequence and quality checks.

### Troubleshooting
- [Q1 2026 Operational Fixes](troubleshooting/q1-2026-operational-fixes.md) - Reusable failure signatures and proven fixes from recent operations.

### Architecture
- [Auth and Retired Services](architecture/auth-and-retired-services.md) - Current auth stack and intentionally dead services.
- [Cross-NUC Communication Matrix](architecture/cross-nuc-communication-matrix.md) - Channel-by-channel map of NUC1/NUC2 transport, auth, ownership, and failures.
- [Harness Runtime Topology](architecture/harness-runtime-topology.md) - Placement and supervisor ownership of harness, mailbox, and runtime control components.
- [Knowledge Base Build Pipeline](architecture/knowledge-base-build-pipeline.md) - Canonical raw-to-wiki, query/file-back, index maintenance, and cross-NUC sync lifecycle.
- [NUC Topology and Services](architecture/nuc-topology-and-services.md) - NUC1/NUC2 service placement and operational boundaries.
- [SlimyAI Login and Session Flow](architecture/slimyai-login-and-session-flow.md) - Canonical credential login, session lifecycle, invite gating, and recovery/lockout behavior.

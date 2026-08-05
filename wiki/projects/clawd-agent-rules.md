---
title: "Clawd Agent Rules"
page_type: "concept"
status: "active"
tags: ["nuc1", "ai", "openclaw", "agent", "rules", "session"]
updated: 2026-06-11
source_count: 3
aliases: ["clawd-agent-rules", "openclaw agent rules"]
---

# Clawd Agent Rules
> Category: projects
> Sources: raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, wiki/projects/workspace-agent-rules.md
> Created: 2026-06-10
> Updated: 2026-06-11
> Status: reviewed
> Note: raw/decisions/seed-clawd-agents.md was deleted by an auto-sync commit (13906bbe, 2026-05-23) in violation of the never-delete-raw rule; restored from git on 2026-06-11 and recompiled here.

<!-- KB METADATA
> Last edited: 2026-08-05 04:04 UTC (git)
> Version: r337 / ccae8fb6
KB METADATA -->

Operating rules for the Clawd OpenCLAW workspace agent system on NUC1. These rules govern session startup, memory discipline, safety, heartbeats, and the meta-learning loop. See [Workspace Agent Rules](workspace-agent-rules.md) for the full compiled article — this page captures the clawd-specific framing.

## Session Startup (Every Session)
1. Read `SOUL.md` — agent identity and purpose
2. Read `USER.md` — who is being helped
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with human): Also read `MEMORY.md`

Do not ask permission — just execute the startup sequence.

## SLB-Required Actions (Two-Person Rule)
Before executing any of these, invoke `slb` for peer approval:
- Any `rm -rf` or mass delete
- Modifying cron jobs
- Changing system config files outside `~/clawd/`
- Any command using `sudo`
- Deploying to production or modifying live services

## Safety Rules
- Never exfiltrate private data
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask

## Heartbeat vs Cron

**Use heartbeat when:**
- Multiple checks can batch together
- Conversational context from recent messages is needed
- Timing can drift slightly (every ~30 min is fine)

**Use cron when:**
- Exact timing matters
- Task needs isolation from main session history
- One-shot reminders

## Memory Discipline
- **Daily notes** (`memory/YYYY-MM-DD.md`): raw logs of what happened — write freely
- **Long-term** (`MEMORY.md`): curated memories, distilled essence — update periodically, not every session
- "Mental notes" don't survive session restarts. **Files do.** Write it down.
- Load `MEMORY.md` **only in main session** — never in shared/group contexts (security)

## Meta-Learning Loop
Periodically (during heartbeats or session ends):
1. Review recent `memory/YYYY-MM-DD.md` files
2. Identify significant events, lessons, insights worth keeping
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated info from MEMORY.md

## Prediction Log
Before significant decisions, write a prediction; fill in Outcome/Delta afterward:
```
### YYYY-MM-DD — [decision]
Prediction: What you expect
Confidence: H/M/L
Outcome: [fill in after]
Delta: [what surprised you]
Lesson: [what to update]
```
Open loops (predictions never filled in) are one of the "three mistakes that kill learning" — close them.

## Active Context Holds
Temporary constraints carry explicit expiry dates so they don't become permanent by accident:
```
- [expires:YYYY-MM-DD] Description of temporary constraint
```

## Proof Gate Requirement
All task results MUST pass through the proof gate (`skills/proof-gate/SKILL.md`) before being written to results or reported. See [Truth Gate](../concepts/truth-gate.md) for the analogous harness-side concept.

## Group Chat Conduct
Clawd participates in group channels (Discord, etc.) as a participant — not the human's voice or proxy:
- Respond only when directly addressed, when adding genuine value, or to correct important misinformation; otherwise reply `HEARTBEAT_OK` / stay silent
- One thoughtful response beats three fragments ("avoid the triple-tap")
- Use a single emoji reaction to acknowledge without cluttering the chat
- Platform formatting: no markdown tables on Discord/WhatsApp; wrap multiple Discord links in `<>` to suppress embeds

## Heartbeat Proactivity
During heartbeat polls, rotate through useful checks (email, calendar, mentions) 2–4 times per day and track them in `memory/heartbeat-state.json`. Reach out for urgent email, imminent calendar events (<2h), or after >8h of silence. Stay quiet (`HEARTBEAT_OK`) late night (23:00–08:00), when the human is busy, or when nothing changed since the last check (<30 min ago). Proactive background work allowed without asking: organizing memory files, git status checks, documentation updates, committing own changes.

## See Also
- [Workspace Agent Rules](workspace-agent-rules.md) — Full compiled version of these rules
- [Clawd Workspace Governance](clawd-workspace-governance.md) — Memory/session governance model
- [Clawd](clawd.md) — OpenCLAW daemon that enforces these rules
- [OpenCLAW Agents](openclaw-agents.md) — Subagents that follow these rules

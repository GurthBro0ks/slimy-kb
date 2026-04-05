# SlimyAI Vault Home

Use this vault as the operator control panel for KB intake and review.

## What Needs Attention
Run these first — copy into a Shell Command (SSH to NUC2):
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki status && bash tools/wiki daily && bash tools/wiki compile-candidates'
```

This shows: conflicts, inbox count, uncompiled raw count, stale articles, last compile/sync dates, and the next suggested action.

## Quick Actions
Shell Commands (laptop → NUC2):

**Vault Sync** — mirror canonical wiki into Obsidian `Wiki/`:
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-sync'
```

**Vault Ingest** — ingest writable vault content into `raw/` and write a report:
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-ingest'
```

**Wiki Search** — search the canonical KB:
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki search "your search terms"'
```

**Open Latest Report** — open newest ingest/query/output report:
```bash
ssh -t work-nuc2 'cd /home/slimy/kb && bash tools/wiki open-report latest'
```

## Last Session
```
LAST SESSION: 2026-04-05 — Phase 2 KB Tooling + Prompt Bundle — PARTIAL PASS
- Installed slimy-chain, saved Phase 2 prompt files, added wiki daily subcommand
- Installed idempotent cron: */30 * * * * cd /home/slimy/kb && bash tools/kb-sync.sh pull
- wiki daily → conflict count, inbox pending, uncompiled raw, stale count, last compile/sync dates
BLOCKED: pending resolution of NUC tunnel auth (slimy@172.18.0.1 access denied)
```

## Operator Console
Full decision tree at [[Projects/Operator Console]].

## Guardrails
- Do not edit mirrored `Wiki/` pages directly.
- Capture in `Inbox/` and `Projects/`; compile into canonical KB wiki.
- All shell commands SSH to NUC2 (this machine) — not local paths.

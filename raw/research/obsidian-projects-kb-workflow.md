---
title: "KB Workflow"
type: "project-note"
source: "obsidian-vault/Projects/KB Workflow.md"
status: "captured"
created: "2026-04-05T10:36:47Z"
kb_ingest_source: "obsidian-vault/Projects/KB Workflow.md"
kb_ingest_folder: "Projects"
kb_ingest_relpath: "Projects/KB Workflow.md"
kb_ingest_timestamp: "2026-04-05T10:36:47Z"
kb_ingest_hash: "abb1dd9f4853dc87cb9c9c0b1345d24d2624745dcbe19259503ceb8133fef4c3"
kb_ingest_type: "project-note"
---

# KB Workflow

## Canonical Rule
- Canonical compiled wiki: `/home/slimy/kb/wiki`
- Obsidian `Wiki/` is a browse-only mirror
- Never treat mirrored `Wiki/` files as editable source of truth

## Operator Flow (Capture -> Sync)
1. Capture in `Inbox/articles`, `Inbox/images`, `Inbox/notes`, or `Projects`.
2. Run ingest (`Slimy: Vault Ingest` or `wiki vault-ingest`).
3. Review the latest ingest/output report (`wiki open-report latest`).
4. Check uncompiled raw material (`wiki compile-candidates`).
5. Compile/update canonical KB wiki from raw source material.
6. Refresh Obsidian mirror (`wiki vault-sync`).

## Compile Candidates Rule
- `wiki compile-candidates` is strict: it lists raw markdown files not referenced by any wiki article `> Sources:` line.
- If a raw file is compiled and cited in `> Sources:`, it should drop out of the candidates list.

## Prompt Generation (Shortcut Layer)
- `wiki prompt-query "question"` and `wiki prompt-compile` generate harness-ready prompt files in `/home/slimy/kb/output/prompts/`.
- These commands are convenience shortcuts.
- They do not replace KB rules in `/home/slimy/kb/KB_AGENTS.md`.

## Why This Split Exists
- Intake stays fast for humans.
- Canonical wiki stays controlled and reviewable.
- Provenance is preserved during ingest and compile.

## Quick Links
- [[Inbox/_How Intake Works]]
- [[Projects/Capture Dashboard]]
- [[Projects/Operator Console]]
- [[Plugin Setup/Shell Commands - Operator Commands]]
- [[Wiki/_index]]
- [[Wiki/architecture/knowledge-base-build-pipeline]]

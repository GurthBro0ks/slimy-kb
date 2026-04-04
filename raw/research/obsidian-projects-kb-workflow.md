---
title: "KB Workflow"
type: "project-note"
source: "obsidian-vault/Projects/KB Workflow.md"
status: "captured"
created: "2026-04-04T17:48:36Z"
kb_ingest_source: "obsidian-vault/Projects/KB Workflow.md"
kb_ingest_folder: "Projects"
kb_ingest_relpath: "Projects/KB Workflow.md"
kb_ingest_timestamp: "2026-04-04T17:48:36Z"
kb_ingest_hash: "ea7feec227e33e1e1f1f4fce1c6544be4d8382515061afd116fcb836e807ccc7"
kb_ingest_type: "project-note"
---

# KB Workflow

## Canonical Rule
- Canonical compiled wiki: `/home/slimy/kb/wiki`
- Obsidian `Wiki/` is browse-only mirror

## Capture to Canonical Pipeline
1. Capture in `Inbox/articles`, `Inbox/images`, `Inbox/notes`, or `Projects`.
2. Run ingest (`Slimy: Vault Ingest` or `wiki vault-ingest`).
3. Confirm outputs in `/home/slimy/kb/raw/articles` and `/home/slimy/kb/raw/research`.
4. Compile/update KB wiki from raw source material.
5. Run `wiki vault-sync` to refresh Obsidian mirror.

## Why This Split Exists
- Intake stays fast for humans.
- Canonical wiki stays controlled and reviewable.
- Provenance is preserved during ingest.

## Quick Links
- [[Inbox/_How Intake Works]]
- [[Projects/Capture Dashboard]]
- [[Wiki/_index]]
- [[Wiki/architecture/knowledge-base-build-pipeline]]

---
title: "Capture Dashboard"
type: "project-note"
source: "obsidian-vault/Projects/Capture Dashboard.md"
status: "captured"
created: "2026-04-04T17:48:36Z"
kb_ingest_source: "obsidian-vault/Projects/Capture Dashboard.md"
kb_ingest_folder: "Projects"
kb_ingest_relpath: "Projects/Capture Dashboard.md"
kb_ingest_timestamp: "2026-04-04T17:48:36Z"
kb_ingest_hash: "4096b22ce0d3560a434e75abed2eb4bea9cf0fa2e4e7fbf4a1d433aaed98a783"
kb_ingest_type: "project-note"
---

# Capture Dashboard

This page stays readable even without Dataview.

## Quick Actions
- Capture article: create note in [[Inbox/articles]] using [[Templates/Article Capture]]
- Capture note: create note in [[Inbox/notes]] using [[Templates/Idea Note]]
- Capture debug finding: use [[Templates/Debug Finding]]
- Capture architecture thought: use [[Templates/Architecture Thought]]
- Capture image context: use [[Templates/Image Intake]]
- Ingest now: run `Slimy: Vault Ingest` (or `wiki vault-ingest`)
- Refresh mirror: run `wiki vault-sync`

## Folder Map
- [[Inbox/articles]]: clipped pages and references
- [[Inbox/images]]: screenshots and images
- [[Inbox/notes]]: short human notes
- [[Projects]]: project notes and planning
- [[Wiki]]: browse-only mirror of canonical KB wiki

## Status Checklist
- [ ] New intake captured
- [ ] Vault ingest run
- [ ] Raw files verified in `/home/slimy/kb/raw`
- [ ] Canonical wiki updated via KB compile
- [ ] Obsidian wiki mirror refreshed

## Optional Dataview (safe to ignore)
```dataview
TABLE file.mtime as Updated
FROM "Inbox"
SORT file.mtime DESC
LIMIT 10
```

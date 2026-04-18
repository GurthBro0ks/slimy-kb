# Capture Dashboard
> Category: projects
> Sources: /home/slimy/kb/raw/research/obsidian-projects-capture-dashboard.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-18 00:24 UTC (git)
> Version: r10 / 757d387
KB METADATA -->

Capture Dashboard is the Obsidian operator intake surface. It maps vault folders to capture types and provides quick-action links for the full ingest-compile-sync cycle.

## Quick Actions
- Capture article: create note in `Inbox/articles` using `Templates/Article Capture`
- Capture note: create note in `Inbox/notes` using `Templates/Idea Note`
- Capture debug finding: use `Templates/Debug Finding`
- Capture architecture thought: use `Templates/Architecture Thought`
- Capture image context: use `Templates/Image Intake`
- Ingest now: run `Slimy: Vault Ingest` (or `wiki vault-ingest`)
- Refresh mirror: run `wiki vault-sync`

## Folder Map
- `Inbox/articles`: clipped pages and references
- `Inbox/images`: screenshots and images
- `Inbox/notes`: short human notes
- `Projects`: project notes and planning
- `Wiki`: browse-only mirror of canonical KB wiki

## Status Checklist
- [ ] New intake captured
- [ ] Vault ingest run
- [ ] Raw files verified in `/home/slimy/kb/raw`
- [ ] Canonical wiki updated via KB compile
- [ ] Obsidian wiki mirror refreshed

## See Also
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md) — end-to-end intake lifecycle
- [Agent Session Contract](../concepts/agent-session-contract.md) — session structure and closeout
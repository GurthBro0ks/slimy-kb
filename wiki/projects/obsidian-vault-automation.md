# Obsidian Vault Automation
> Category: projects
> Sources: raw/research/2026-04-05-obsidian-calendar-automation-options.md, raw/research/obsidian-projects-kb-workflow.md
> Created: 2026-04-05
> Updated: 2026-04-08
> Status: reviewed

Server-side automation scripts that maintain the Obsidian vault on NUC2, including daily notes, operator checklists, AI recommendations, and idea ingestion.

## Vault Structure

```
Daily/                          # Daily notes (YYYY-MM-DD.md)
Ideas/                          # All idea notes
  Inbox/                        # Unsorted ideas (human capture)
  New-Projects/                 # Ideas for new projects
  Existing-Projects/            # Ideas about existing projects
  Photos/                       # Photo metadata / notes
  Screenshots/                  # Screenshot metadata / notes
Recommendations/                # AI-generated recommendations
  Daily/                        # Daily recommendation output (YYYY-MM-DD-host.md)
  Weekly/                       # Weekly rollup
  New-Projects/                 # Recommendation type: new project ideas
  Refactors/                   # Recommendation type: refactor ideas
Calendar/                       # Future: calendar integration
Templates/                      # Vault templates
Wiki/                           # Mirror of KB wiki (read-only sync)
Projects/                       # Project-level notes
Inbox/                          # Inbox (articles, images, notes — raw human capture)
```

**Daily note naming convention:** `YYYY-MM-DD.md` (e.g., `2026-04-05.md`)

## Automation Scripts

### kb-calendar-sync.sh
Runs daily (via cron or manual trigger). Creates/updates today's daily note at `Daily/YYYY-MM-DD.md`.

Populates:
- **Project checklist:** service status for all active projects
- **Important changes:** recent git commits (last 24h, 7d) across known repos
- **Open anomalies:** failed services, stale articles, uncompiled raw files
- **Pending maintenance:** compile candidate count, conflict count, stale article count
- **Recommended actions:** prioritized action list from `kb-recommend.sh`

Posts to Discord if `DISCORD_WEBHOOK_URL` is configured.

### kb-todo.sh
Generates `/home/slimy/kb/output/todo-YYYYMMDD-HHMMSS.md`. Refreshes the checklist section of today's daily note.

Includes:
- Service health (via `systemctl --user`)
- Conflict file count
- Compile candidate list
- Missing project doc repos
- Manual verification steps

### kb-recommend.sh
Generates `/home/slimy/kb/output/recommend-YYYYMMDD-HHMMSS.md`. Writes daily recommendation note to `Recommendations/Daily/YYYY-MM-DD-host.md`.

Types: additions, missing docs, refactors, backlog, legacy cleanup.

### kb-idea-ingest.sh
Scans `Ideas/Inbox/`, `Ideas/New-Projects/`, `Ideas/Existing-Projects/`, `Ideas/Photos/`, `Ideas/Screenshots/` in the vault. Converts vault idea markdown files to KB raw notes under `raw/ideas/`. Creates photo metadata placeholders under `raw/photos/`.

**Never moves or deletes user originals.**

### kb-changelog-rollup.sh
Scans recent git commits across all known repos. Generates `output/changelog-YYYYMMDD-HHMMSS.md`. Can be referenced by daily notes for "important changes" section.

### kb-version-scan.sh
Scans version information across all known repos. Generates `output/version-scan-YYYYMMDD-HHMMSS.md`.

## Vault Sync vs Vault Ingest

| Operation | Tool | Direction | Notes |
|---|---|---|---|
| `wiki vault-sync` | `kb-obsidian-sync.sh` | KB wiki → vault Wiki/ | Mirrors canonical wiki into vault (read-only for humans) |
| `wiki vault-ingest` | `kb-obsidian-ingest.sh` | vault → KB raw | Ingests user content from vault Inbox into KB raw |

## Canonical Rule
- Canonical compiled wiki: `/home/slimy/kb/wiki`
- Obsidian `Wiki/` is a browse-only mirror
- Never treat mirrored `Wiki/` files as editable source of truth

## Operator Flow (Capture -> Sync)
1. Capture in `Inbox/articles`, `Inbox/images`, `Inbox/notes`, or `Projects`
2. Run ingest (`Slimy: Vault Ingest` or `wiki vault-ingest`)
3. Review the latest ingest/output report (`wiki open-report latest`)
4. Check uncompiled raw material (`wiki compile-candidates`)
5. Compile/update canonical KB wiki from raw source material
6. Refresh Obsidian mirror (`wiki vault-sync`)

## Cron Wiring (Recommended)

```cron
# Daily calendar + todo check (start of day)
30 6 * * * bash /home/slimy/kb/tools/kb-calendar-sync.sh

# Daily recommendations
0 7 * * * bash /home/slimy/kb/tools/kb-recommend.sh

# Weekly version scan + changelog rollup
0 8 * * 1 bash /home/slimy/kb/tools/kb-version-scan.sh
0 8 * * 1 bash /home/slimy/kb/tools/kb-changelog-rollup.sh

# After vault sync (via Obsidian plugin hook or manual)
bash /home/slimy/kb/tools/kb-idea-ingest.sh
```

## Status
- **Vault structure:** Created (Daily/, Ideas/, Recommendations/, Calendar/)
- **kb-calendar-sync.sh:** Implemented
- **kb-todo.sh:** Implemented
- **kb-recommend.sh:** Implemented
- **kb-idea-ingest.sh:** Implemented
- **Discord webhook:** Prepared but not configured (env var only)
- **Cron wiring:** Not yet configured
- **Obsidian plugin config:** User-side action needed

## See Also
- [Capture Dashboard](capture-dashboard.md) — operator intake surface
- [Operator Console](operator-console.md) — KB operations decision tree
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md) — end-to-end intake lifecycle
- [Obsidian Headless Sync](obsidian-headless-sync.md) — PM2 vault sync process

# Obsidian Calendar Automation Options

**Date:** 2026-04-05
**Scope:** NUC2 vault structure and calendar/daily-note automation
**Sources:** vault structure audit + Phase 3 automation design

---

## 1. Recommended Vault Structure for Calendar/Daily Notes

The Obsidian vault at `/home/slimy/obsidian/slimyai-vault/` should use this folder structure:

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
  New-Projects/                  # Recommendation type: new project ideas
  Refactors/                    # Recommendation type: refactor ideas
Calendar/                       # Future: calendar integration
Templates/                      # Vault templates
Wiki/                           # Mirror of KB wiki (read-only sync)
Projects/                       # Project-level notes
Inbox/                          # Inbox (articles, images, notes — raw human capture)
```

**Daily note naming convention:** `YYYY-MM-DD.md` (e.g., `2026-04-05.md`)

---

## 2. How Project Events/Tasks Get Surfaced into Daily/

### A. kb-calendar-sync.sh (server-side automation)
- Runs daily (via cron or manual trigger)
- Creates/updates `/home/slimy/obsidian/slimyai-vault/Daily/YYYY-MM-DD.md`
- Populates:
  - **Project checklist:** service status for all active projects
  - **Important changes:** recent git commits (last 24h, 7d) across known repos
  - **Open anomalies:** failed services, stale articles, uncompiled raw files
  - **Pending maintenance:** compile candidate count, conflict count, stale article count
  - **Recommended actions:** prioritized action list from `kb-recommend.sh`

### B. kb-todo.sh (operator checklist)
- Generates `/home/slimy/kb/output/todo-YYYYMMDD-HHMMSS.md`
- Refreshes the checklist section of today's daily note in vault
- Includes:
  - Service health (via systemctl --user)
  - Conflict file count
  - Compile candidate list
  - Missing project doc repos
  - Manual verification steps

### C. kb-recommend.sh (AI recommendations)
- Generates `/home/slimy/kb/output/recommend-YYYYMMDD-HHMMSS.md`
- Writes daily recommendation note to `Recommendations/Daily/YYYY-MM-DD-host.md`
- Types: additions, missing docs, refactors, backlog, legacy cleanup

### D. kb-idea-ingest.sh (human idea capture)
- Scans `Ideas/Inbox/`, `Ideas/New-Projects/`, `Ideas/Existing-Projects/`, `Ideas/Photos/`, `Ideas/Screenshots/`
- Converts vault idea markdown files to KB raw notes under `raw/ideas/`
- Creates photo metadata placeholders under `raw/photos/`
- **Never moves or deletes user originals**

### E. kb-changelog-rollup.sh (activity digest)
- Scans recent git commits across all known repos
- Generates `output/changelog-YYYYMMDD-HHMMSS.md`
- Can be referenced by daily notes for "important changes" section

---

## 3. Discord Webhook Posting

**Current status:** NOT CONFIGURED

`kb-calendar-sync.sh` checks for `DISCORD_WEBHOOK_URL` environment variable:
```bash
if [[ -n "$DISCORD_WEBHOOK" ]]; then
    curl -s -X POST "$DISCORD_WEBHOOK" -H "Content-Type: application/json" \
        -d '{"content": "Daily $TODAY — compile: N, conflicts: N, stale: N"}'
else
    echo "[kb-calendar-sync] DISCORD_WEBHOOK_URL not configured — skipping Discord post"
fi
```

**Activation:** Set `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...` in the user's environment or systemd service file. Without it, the script logs cleanly and continues (non-blocking).

---

## 4. What Remains User-Side vs Server-Side

### Server-side (automated)
| Action | Tool | Trigger |
|---|---|---|
| Daily note creation/update | `kb-calendar-sync.sh` | Cron or manual |
| Operator checklist | `kb-todo.sh` | Manual or after-agent |
| Recommendation generation | `kb-recommend.sh` | Daily cron |
| Idea ingestion from vault | `kb-idea-ingest.sh` | After vault sync |
| Version scan | `kb-version-scan.sh` | Weekly cron or manual |
| Changelog rollup | `kb-changelog-rollup.sh` | Weekly cron or manual |
| Compile trigger | `kb-compile-if-needed.sh` | After any KB raw write |
| KB sync | `kb-sync.sh` | After changes |

### User-side (manual)
| Action | Tool |
|---|---|
| Creating daily note manually | Obsidian daily note plugin |
| Capturing ideas to vault | Write to `Ideas/Inbox/` |
| Taking screenshots/photos | Save to `Ideas/Photos/` or `Ideas/Screenshots/` |
| Reviewing recommendations | Open `Recommendations/Daily/` |
| Calendar events | Obsidian calendar plugin (Dataview) |
| Full KB compile | `wiki prompt-compile` then execute |

---

## 5. Automation Wiring

### Cron candidates (NUC2)
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

### slimy-agent-finish.sh wiring
After any Claude/Codex session:
1. `kb-project-doc-sync.sh` for each touched repo
2. Write `raw/agent-learnings/YYYY-MM-DD-host-agent-summary.md`
3. Write `raw/changelogs/YYYY-MM-DD-host-project-changelog.md`
4. Commit + push all touched repos
5. Commit + push KB
6. `kb-compile-if-needed.sh` (triggers compile prompt if new raw files)

---

## 6. Vault Sync vs Vault Ingest

| Operation | Tool | Direction | Notes |
|---|---|---|---|
| `wiki vault-sync` | `kb-obsidian-sync.sh` | KB wiki → vault Wiki/ | Mirrors canonical wiki into vault (read-only for humans) |
| `wiki vault-ingest` | `kb-obsidian-ingest.sh` | vault → KB raw | Ingests user content from vault Inbox into KB raw |

---

## 7. Missing Pieces (User-Side)

1. **Obsidian daily note plugin** must be configured to use `Daily/` folder as vault root for daily notes
2. **Dataview plugin** enables querying daily notes by date — can surface tasks via `TASK` or `- [ ]` syntax
3. **Discord webhook URL** needs to be configured in environment for webhook posting
4. **Calendar plugin** for Obsidian can link to daily notes but calendar events must be entered manually in Obsidian

---

## 8. Status

- **Vault structure:** ✅ Created (Daily/, Ideas/, Recommendations/, Calendar/)
- **kb-calendar-sync.sh:** ✅ Implemented
- **kb-todo.sh:** ✅ Implemented
- **kb-recommend.sh:** ✅ Implemented
- **kb-idea-ingest.sh:** ✅ Implemented
- **Discord webhook:** ⚠️ Prepared but not configured (env var only)
- **Cron wiring:** ⬜ Not yet configured (recommend wiring after Phase 3 validation)
- **Obsidian plugin config:** ⬜ User-side action needed

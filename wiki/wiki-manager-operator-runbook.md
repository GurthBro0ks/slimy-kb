# Wiki Manager Operator Runbook

> Category: architecture
> Status: active
> Updated: 2026-04-09

<!-- KB METADATA
> Last edited: 2026-04-20 12:27 UTC (git)
> Version: r22 / 51be377
KB METADATA -->

This runbook describes the wiki-manager system on NUC2 — what runs automatically, what it produces, and how to interpret the outputs.

---

## What Runs Automatically

Six systemd user timers run on NUC2:

| Timer | Interval | What it does |
|-------|----------|--------------|
| `kb-maintenance.timer` | Every 12h | Pull KB, run lint, sync wiki→vault, log to `wiki/log.md` |
| `wiki-manager-stage1.timer` | Every 12h | Full Stage 1.86 pipeline (see below) |
| `kb-daily-note.timer` | Daily 06:00 UTC | Populates `vault/Daily/TODAY.md` via calendar-sync |
| `obsidian-sync.timer` | Every 5 min | One-shot Obsidian cloud sync (bidirectional) |
| `nuc1-remote-gate.timer` | Every 12h | NUC1 remote health gate |
| `nuc1-kb-digest.timer` | (NUC1 side) | Publishes digest into NUC2 inbox-nuc1 |

**Wiki manager is the primary automated operator tool.** It does NOT dispatch harness jobs — it produces advisory queues for human review.

To check timers:
```bash
systemctl --user list-timers --all | grep -E "kb-maintenance|wiki-manager"
```

To manually trigger a wiki-manager run:
```bash
systemctl --user start wiki-manager-stage1.service
```

---

## The Stage 1.86 Pipeline

Every 12h, `wiki-manager-stage1.timer` fires `wiki-manager-stage1.service` which runs:

1. **Sync pull** — `kb-sync.sh pull` gets latest KB from git
2. **Collectors** — runs `collect_nuc2_state.sh`, `collect_repo_digests.py`, `collect_kb_health.sh`
3. **Wiki meta read** — reads `_index.md`, `_concepts.md`, `log.md`, `_orphans.md`, `_weak-links.md`
4. **NUC1 inbox parse** — reads `raw/inbox-nuc1/` (JSON + markdown digests)
5. **Todo queue generation** — produces `output/todo_queue.json` and `output/todo_queue.md`
6. **History tracking** — updates `output/todo_history.json` (bounded: 10 runs / 30 days)
7. **Candidate promotion** — applies Stage 1.86 freshness-weighted rules
8. **Stable wiki pages** — rewrites machine-managed sections of state pages
9. **Project pages** — updates project pages with machine-managed status blocks
10. **Log entry** — appends to `wiki/log.md`
11. **Commit + push** — commits if anything changed

---

## Where NUC1 Publishes To

NUC1 publishes digests into:
```
/home/slimy/kb/raw/inbox-nuc1/
```

Two formats are consumed:
- **JSON** — `YYYY-MM-DD-nuc1-*.json` with `repos[]` array (dirty, diverged, etc.)
- **Markdown** — `YYYY-MM-DD-nuc1-*.md` with `> Type: digest|report|note|inventory`

**Fail-soft:** If the inbox is empty or absent, the manager logs it and proceeds without NUC1 evidence. Missing NUC1 input is not fatal.

Processed items are moved to `raw/agent-learnings/` with a note linking to the originating inbox file.

---

## Outputs to Inspect First

When the queue looks wrong, check these in order:

### 1. `wiki/_manager-status.md`
Quick status at a glance:
- Total tasks, NEW/PERSISTING/RESOLVED counts
- Promotion counts (candidate/emerging/cooling_down/not_candidate)
- Freshness band distribution (fresh/aging/stale)
- Which stable pages were updated this run

### 2. `output/todo_queue.md`
Human-readable queue with all task details. Start here to see what the manager thinks needs attention.

### 3. `output/todo_queue.json`
Machine-readable queue. Useful for scripting or filtering.

### 4. `output/harness_candidates.md`
Tasks that meet all candidate criteria, bucketed by freshness band:
- **fresh** — evidence < 24h old
- **aging** — evidence 24–72h old
- **stale** — evidence > 72h old (these are in cooling_down or not_candidate)

### 5. `output/candidate_review_pack.md`
Human review digest with per-task tables, recommended actions, and guidance on what would restore cooling_down tasks.

### 6. `wiki/log.md`
Append-only event log. Look here when you need to trace what happened on a specific date.

---

## Candidate Promotion Statuses

| Status | Meaning |
|--------|---------|
| `not_candidate` | Default — tracked but doesn't yet qualify |
| `emerging` | Has some signals but not all criteria met |
| `candidate` | Meets all criteria — ready for harness dispatch review |
| `cooling_down` | Was candidate/emerging but evidence has gone stale (> 72h) |
| `resolved` | No longer present in current queue |

---

## Freshness Bands

Evidence age is measured by file modification time of the primary evidence path.

| Band | Age | Effect |
|------|-----|--------|
| `fresh` | < 24h | No penalty; normal promotion rules |
| `aging` | 24–72h | Soft penalty; candidate requires recent_occ >= 5 |
| `stale` | > 72h | Strong penalty; forces cooling_down if was candidate |

---

## What "Stub Backend" Means

The wiki-manager has two backends (set via `KB_MANAGER_BACKEND`):
- `stub` (default) — rule-based todo generation; always available
- `ollama` — uses local Ollama with `KB_MANAGER_MODEL` (e.g. `qwen2.5:7b`)

Both backends produce bounded, deterministic outputs. The stub backend is always used currently.

---

## What to Check When the Queue Looks Wrong

### Queue is empty
- Was NUC1 inbox populated when the manager ran? Check `wiki/log.md` for NUC1 item count
- Did the collectors succeed? Check `/tmp/proof_wiki_manager_stage1_*/`

### All tasks are `not_candidate`
- Check freshness bands — if evidence is stale (> 72h), tasks will cool down
- Check that evidence paths still exist (files may have been moved/deleted)
- Check `wiki/_orphans.md` — if it changed significantly, evidence paths may have shifted

### Tasks are stuck as `candidate` but never resolve
- This is expected for cross-NUC drift issues (dirty diverged repos) — they persist until manually resolved
- Orphan resolution tasks persist until the orphaned pages are linked or removed

### Tasks have wrong freshness band
- Freshness is computed from file modification time of the **primary evidence path**
- If evidence was copied rather than moved, the mtime may not reflect actual age

### Evidence age reported as `stale` but file is recent
- This was a known bug in Stage 1.85 where evidence_path was incorrectly stripped. Fixed in 1.86.
- Run `stat /home/slimy/kb/raw/inbox-nuc1/` to verify the directory exists and is readable

---

## What Is Still Intentionally NOT Automated

The wiki-manager Stage 1.86 is an **advisory system only.** The following are deliberately manual:

- **Harness dispatch** — no jobs are dispatched automatically. Candidate status is recorded but blocked by `advisory_only`.
- **Orphan resolution** — orphaned pages are surfaced but not auto-linked or deleted.
- **Cross-NUC git reconciliation** — dirty/drifted repos require human judgment to merge.
- **Project page content changes** — machine-managed blocks are updated, but human content outside the markers is preserved.
- **KB content compilation** — raw → wiki compilation is not automated; it requires an agent to run `wiki compile`.
- **Obsidian vault sync** — now automated via `obsidian-sync.timer` (every 5 min, one-shot).
- **Daily note population** — now automated via `kb-daily-note.timer` (daily 06:00 UTC).
- **Wiki → vault mirror** — now automated as a step in `kb-maintenance.sh`.

---

## How This Stays Separate from Harness

The KB and wiki-manager are **completely separate** from harness execution:

- **No dispatch** — wiki-manager produces queues; harness is never called automatically
- **No shared state** — wiki-manager reads git and files; harness manages its own agent sessions
- **Handoff only** — when a human reviews `harness_candidates.md` and decides to act, they manually invoke harness with the appropriate context
- **Different git remotes** — KB is `GurthBro0ks/slimy-kb`; harness repos are separate

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `output/todo_queue.json` | Machine-readable queue |
| `output/todo_queue.md` | Human-readable queue |
| `output/todo_history.json` | Historical task state (bounded) |
| `output/harness_candidates.md` | Candidates bucketed by freshness |
| `output/candidate_review_pack.md` | Human review digest |
| `wiki/_manager-status.md` | Quick status snapshot |
| `wiki/_candidate-promotion-rules.md` | Explicit promotion criteria |
| `wiki/_nuc-intake.md` | NUC1 inbox format documentation |
| `wiki/log.md` | Append-only event log |
| `raw/inbox-nuc1/` | NUC1 digest drop-off |
| `tools/wiki_manager_stage1.sh` | Runner script |
| `tools/wiki_manager_stage1.py` | Core pipeline logic |

---

## See Also

- [_candidate-promotion-rules.md](_candidate-promotion-rules.md)
- [_nuc-intake.md](_nuc-intake.md)
- [_manager-status.md](_manager-status.md)
- [knowledge-base-build-pipeline.md](architecture/knowledge-base-build-pipeline.md)
- [nuc1-current-state.md](architecture/nuc1-current-state.md)
- [nuc2-current-state.md](architecture/nuc2-current-state.md)

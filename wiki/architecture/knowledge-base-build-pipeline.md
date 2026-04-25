# Knowledge Base Build Pipeline
> Category: architecture
> Sources: /home/slimy/kb/KB_AGENTS.md, /home/slimy/kb/tools/kb-sync.sh, /home/slimy/kb/tools/kb-search.sh, /home/slimy/kb/tools/kb-write.sh, /home/slimy/kb/wiki/_index.md, /home/slimy/kb/wiki/_concepts.md, /home/slimy/kb/output/query-20260404-134246.md, /home/slimy/kb/wiki/architecture/harness-runtime-topology.md, /home/slimy/kb/wiki/patterns/memory-capture-pattern.md, /home/slimy/kb/raw/research/obsidian-projects-kb-workflow.md, /home/slimy/kb/raw/research/2026-04-05-obsidian-calendar-automation-options.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-25 12:34 UTC (git)
> Version: r44 / 9c811d4
KB METADATA -->

This article defines the end-to-end workflow for how SlimyAI knowledge is captured, compiled, queried, and synchronized across NUC1/NUC2.

## Raw Intake Model
The KB uses three storage layers:
- `raw/`: source material only. Agents and humans can write here; raw files are never deleted.
- `wiki/`: compiled knowledge articles. Agents own this layer.
- `output/`: one-off query answers; these can be filed back into `wiki/` when durable.

Raw folder purposes:
- `raw/articles/`: repo docs, readmes, and longer source narratives.
- `raw/agent-learnings/`: per-session learnings and non-obvious fixes.
- `raw/changelogs/`: per-session or per-project changelog snapshots.
- `raw/versions/`: per-session version scan snapshots.
- `raw/research/`: focused research notes and external references.
- `raw/decisions/`: operating decisions, rules, and architecture constraints.
- `raw/ideas/`: ingested human idea notes from Obsidian vault Ideas/.
- `raw/photos/`: photo metadata placeholders from Obsidian vault Ideas/Photos/.
- `raw/recommendations/`: AI-generated recommendation notes (daily/weekly/new-projects/refactors).

## Compile and Update Rules (raw -> wiki)
Per `KB_AGENTS.md`, compile is rule-driven:
1. Read a raw document fully.
2. Assign one wiki category (`concepts`, `projects`, `patterns`, `troubleshooting`, `architecture`).
3. Update an existing wiki article when overlap exists; avoid duplicates.
4. If new, create one-topic article with required header metadata.
5. Add backlinks in `See Also`.
6. Rebuild indexes (`_index.md`, `_concepts.md`) and stale tracking (`_stale.md`).

Article constraints:
- One topic per article.
- Use relative links.
- Troubleshooting entries must keep symptom/cause/fix/prevention structure.
- Code examples must be from real repo/code paths.

## Index Maintenance Contract
After any wiki change:
- `_index.md` must list every article with a one-line summary.
- `_concepts.md` must list concepts without duplicates.
- `_stale.md` should track pages older than 30 days with no update.

**Automated maintenance:** `kb-maintenance.timer` (every 12h) runs lint and logs to `wiki/log.md`. `wiki-manager-stage1.timer` (every 12h) maintains stable state pages, candidate promotion, and project health indexes. Both are systemd user timers on NUC2.

## Query and File-Back Loop
Read loop:
1. Pull latest KB state (`bash /home/slimy/kb/tools/kb-sync.sh pull`).
2. Locate articles via index/concepts and `bash /home/slimy/kb/tools/kb-search.sh "query"`.
3. Synthesize an answer into `output/query-*.md`.

File-back loop:
1. If output contains reusable guidance, convert it into a wiki article update.
2. Add/refresh backlinks and indexes.
3. Push updated KB state (`bash /home/slimy/kb/tools/kb-sync.sh push`).

Atomic raw filing path:
- `echo "content" | bash /home/slimy/kb/tools/kb-write.sh raw/agent-learnings/YYYY-MM-DD-host-slug.md`
- `kb-write.sh` performs pull -> write -> commit -> push.

## Cross-NUC Sync Lifecycle
Shared-repo lifecycle defined in `KB_AGENTS.md` and implemented by `kb-sync.sh`:
- Before any KB read/search/query/compile: run `kb-sync.sh pull`.
- After any KB write/compile/gap-fill: run `kb-sync.sh push`.

`kb-sync.sh` behavior:
- `pull`: `git pull --rebase --autostash origin main`; warns and continues on failure.
- `push`: stages all changes, auto-commits if needed, then pushes `origin main`; warns on push failure.
- `sync`: executes pull then push.

## Conflict and Branch Behavior
Current behavior is fail-open and main-locked:
- Pull/push targets are hardcoded to `origin main`.
- If rebase/pull fails, tool warns and keeps local work unblocked.
- If push fails, committed local changes remain and require manual retry.

Branch safety implications:
- The tool is safe for the canonical `main` flow.
- Non-`main` or mismatched-remote setups are not auto-detected; operators must resolve branch/remote alignment manually.

Observed failure signature in current environment:
- `fatal: couldn't find remote ref main` during `kb-sync.sh pull`, followed by warning fallback to local state.

## Manual vs Automatic (Current Reality)
Manual:
- Categorizing raw files.
- Writing/updating wiki articles.
- Rebuilding `_index.md`, `_concepts.md`, `_stale.md` (auto-updated on compile but humans can refresh).
- Deciding what query outputs should be promoted back into wiki.
- Resolving merge/rebase issues when sync warnings occur.
- Dispatching harness jobs (advisory only from wiki-manager; humans invoke harness).

Automatic (scripted helpers only):
- Full-text wiki search (`kb-search.sh`).
- Pull/push wrapper and optional auto-commit (`kb-sync.sh`).
- Atomic single-file ingest (`kb-write.sh`).
- End-of-run automation for Claude/Codex agents (`slimy-agent-finish.sh`).
- Project doc scaffolding: README/CHANGELOG/VERSION sync (`kb-project-doc-sync.sh`).
- Version scan across all known projects (`kb-version-scan.sh`).
- Changelog rollup for last 1d/7d (`kb-changelog-rollup.sh`).
- Idea ingestion from vault Ideas/ folder (`kb-idea-ingest.sh`).
- Daily note sync to vault Daily/ (`kb-calendar-sync.sh`).
- Operator recommendation generation (`kb-recommend.sh`).
- Daily operator todo checklist (`kb-todo.sh`).
- Compile-needed checker (`kb-compile-if-needed.sh`).
- KB maintenance (`kb-maintenance.timer` + `kb-maintenance.sh`, every 12h): lint, log.
- Wiki manager stage 1.86 (`wiki-manager-stage1.timer` + `wiki_manager_stage1.sh`, every 12h): digest collection, todo queue, candidate promotion, stable wiki pages.

## See Also
- [Harness Runtime Topology](harness-runtime-topology.md)
- [Cross-NUC Communication Matrix](cross-nuc-communication-matrix.md)
- [Memory Capture Pattern](../patterns/memory-capture-pattern.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Wiki Manager Operator Runbook](../wiki-manager-operator-runbook.md)
- [_candidate-promotion-rules.md](../wiki/_candidate-promotion-rules.md)

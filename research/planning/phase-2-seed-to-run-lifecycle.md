# Phase 2: Seed-to-Run Lifecycle Planner

## Goal

Build a safe local CLI/tooling foundation that can:

1. List research topic seeds from `research/topics/*.md`
2. Validate topic frontmatter against the Phase 1 schema
3. Select a queued topic and plan a run
4. Create an immutable run/proof-burrow skeleton from that topic
5. Copy the topic into the run folder
6. Write starter run metadata (`run.json`)
7. Write placeholder files for plan, queries, sources, notes, report, slides, critic, and RESULT
8. Update `research/indexes/index.json`
9. Never overwrite an existing run
10. Avoid touching production services

## What This Is NOT

- NOT the full research runner (no web crawling, no model calls)
- NOT web crawling
- NOT model synthesis
- NOT PDF generation
- NOT Habitat queue controls
- NOT guild/MCP integration
- NOT Hermes integration

## Implementation

### Tool

- `tools/research-plan-run.py` — standard-library-only Python tool
- `tools/research-plan-run.sh` — bash wrapper

### Commands

```bash
bash tools/research-plan-run.sh list
bash tools/research-plan-run.sh plan <topic>
bash tools/research-plan-run.sh create-run <topic> --dry-run
bash tools/research-plan-run.sh create-run <topic>
bash tools/research-plan-run.sh test
```

### Run Folder Structure

```
research/runs/YYYY-MM-DD-<slug>/
  topic.md          # copy of the original topic
  run.json          # immutable run metadata
  plan.md           # placeholder research plan
  queries.json      # placeholder search queries
  sources.jsonl     # placeholder source list
  notes/README.md   # placeholder notes directory
  fetched/README.md # placeholder fetched sources directory
  report.md         # placeholder report
  slides.md         # placeholder presentation slides
  critic.md         # placeholder critic notes
  RESULT.md         # result with RESULT=PLANNED
```

### Run Metadata (run.json)

Initial status: `planned`

Fields:
- `schema_version`, `immutable_run_id`, `slug`, `title`
- `status` (initially "planned"), `priority`, `depth`
- `confidence` (null), `source_count` (0), `citation_count` (0)
- `created_at`, `started_at` (null), `completed_at` (null)
- `model_used` (null), `runner_version`
- `pdf_path` (null), `report_path`, `critic_path`, `proof_path`
- `topic_path`, `tags`
- `related_harness_session` (null), `related_guild_campaign` (null)
- `assigned_critter` (null), `source_topic_path`

### Index Update Rules

- Preserve existing index fields
- Add or update one item for the run
- Do not duplicate the same `immutable_run_id`
- Do not remove unrelated items
- Use relative paths from `/home/slimy/kb`
- Keep JSON pretty-printed and deterministic

### Safety Rules

- Do not restart services
- Do not touch Caddy or public Slimy website
- Do not install packages
- Do not call external APIs
- Do not crawl the web
- Do not invoke Hermes
- Do not install or integrate `mathomhaus/guild`
- Do not build Habitat queue controls
- Do not expose PDFs publicly
- Do not put anything in `public/`
- Do not overwrite completed runs
- Do not push

### Templates Added

- `research/templates/run-metadata.schema.json` — JSON Schema for `run.json`
- `research/templates/queries.template.json` — placeholder queries template
- `research/templates/sources.template.jsonl` — placeholder sources template

### Self-Test

The `test` command creates a temporary run under `/tmp` and validates:
- Frontmatter parsing
- Run skeleton generation
- `run.json` status is `planned`
- `RESULT.md` contains `RESULT=PLANNED`
- Index update produces exactly 1 item

## Acceptance Criteria

1. `bash tools/research-plan-run.sh list` shows sample topic
2. `bash tools/research-plan-run.sh plan <topic>` validates and shows planned run
3. `bash tools/research-plan-run.sh create-run <topic> --dry-run` shows changes without modifying files
4. `bash tools/research-plan-run.sh create-run <topic>` creates the run skeleton and updates index
5. Running `create-run` again on same topic fails safely (no overwrite)
6. `bash tools/validate-research-schema.sh` still passes after changes
7. Index remains valid JSON with deterministic formatting
8. No forbidden canonical path `/home/slimy/slimy-kb` in new tools/templates
9. No production services touched

## Validation Commands

```bash
bash tools/validate-research-schema.sh
bash tools/research-plan-run.sh list
bash tools/research-plan-run.sh plan research/topics/sample-self-hosted-deep-research-agent.md
bash tools/research-plan-run.sh create-run research/topics/sample-self-hosted-deep-research-agent.md --dry-run
bash tools/research-plan-run.sh create-run research/topics/sample-self-hosted-deep-research-agent.md
bash tools/validate-research-schema.sh
bash tools/research-plan-run.sh list
```

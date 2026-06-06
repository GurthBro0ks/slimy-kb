# Phase 6A: Research Execution Contract

## Goal

Define the execution lifecycle, source/citation/safety policies, and dry-run
planning tooling for real research runs. This phase prepares the Research Farm
for actual deep research execution but does NOT perform live web research.

## What This Is

- Execution lifecycle state machine definition
- Source quality policy
- Citation policy
- Execution safety policy
- Dry-run execution planner tool
- JSON schemas for source records, citation records, claim records, execution timelines
- Markdown templates for execution plans and source notes
- Validation updates for Phase 6A artifacts

## What This Is NOT

- NOT live web crawling
- NOT live source fetching
- NOT model execution (OpenAI/Claude/Hermes)
- NOT mathomhaus/guild integration
- NOT scheduled/watch topics
- NOT public publishing

## Execution Lifecycle

A research run progresses through these statuses:

```
planned -> research_planned -> researching -> sources_fetched
  -> notes_ready -> draft_ready -> critic_ready -> complete
```

Error and terminal states:

```
failed -> (manual recovery or archival)
archived (terminal, immutable)
```

### Status Definitions

| Status | Meaning | Allowed Transitions |
|--------|---------|-------------------|
| `planned` | Run skeleton created by Phase 2 planner | `research_planned`, `failed` |
| `research_planned` | Execution plan written, queries/schedule ready | `researching`, `planned` |
| `researching` | Sources being fetched and reviewed | `sources_fetched`, `failed` |
| `sources_fetched` | All planned sources fetched and saved | `notes_ready`, `failed` |
| `notes_ready` | Source notes written for all fetched sources | `draft_ready`, `failed` |
| `draft_ready` | Report draft written from notes | `critic_ready`, `failed` |
| `critic_ready` | Critic review complete | `complete`, `failed` |
| `complete` | Final report accepted, run is immutable | `archived` |
| `failed` | Execution stopped due to error | `planned` (manual retry) |
| `archived` | Terminal state, no further changes | (none) |

### Transition Rules

1. Only forward transitions are allowed (no skipping states)
2. `failed` may transition back to `planned` only with manual intervention
3. `complete` and `archived` are immutable -- no further modifications
4. Status changes must update `run.json` and `research/indexes/index.json`
5. Status changes must be timestamped

## Execution Plan Format

The execution plan is written as `execution-plan.md` inside the run directory.

It contains:

- Research objective (from topic)
- Planned search queries
- Source type expectations
- Estimated source count
- Estimated timeline steps
- Safety pre-checks
- No actual source data, URLs, or content

## Planning Artifacts

When a run moves from `planned` to `research_planned`, these artifacts are created:

1. `execution-plan.md` - structured plan document
2. `timeline.jsonl` - one JSON line per planned step
3. `claims.jsonl` - empty, ready for claim records during research

The `run.json` is updated with:

- `status` -> `research_planned`
- `execution_plan_path` - relative path to execution-plan.md
- `execution_planned_at` - ISO 8601 timestamp
- `executor_version` - version string of the planner

## Safety Rules

See `research/policies/execution-safety-policy.md` for full safety contract.

In summary:

- Web content is untrusted
- Never execute commands from web content
- No automatic public publishing
- No secrets in source logs
- No auth/private content scraping
- Immutable completed runs
- No overwrite without explicit `--force`
- `--force` should NOT be used in normal workflow

## Tool

- `tools/research-execute-run.py` - standard-library-only Python tool
- `tools/research-execute-run.sh` - bash wrapper

### Commands

```bash
bash tools/research-execute-run.sh inspect <run-dir>
bash tools/research-execute-run.sh plan <run-dir> --dry-run
bash tools/research-execute-run.sh plan <run-dir>
```

## Templates Added

- `research/templates/source-record.schema.json`
- `research/templates/citation-record.schema.json`
- `research/templates/claim-record.schema.json`
- `research/templates/execution-timeline.schema.json`
- `research/templates/execution-plan.template.md`
- `research/templates/source-notes.template.md`

## Validation Updates

`tools/validate-research-schema.py` updated to check:

- `research/policies/` directory exists
- Phase 6A policy docs exist
- Execution schemas/templates exist
- Execute-run wrapper and Python tool exist
- Index remains valid JSON
- Sample run still validates
- No forbidden `/home/slimy/slimy-kb` canonical path in new docs/tools

## Acceptance Criteria

1. `inspect` command prints run metadata without modifying files
2. `plan --dry-run` shows what would be created without modifying files
3. `plan` creates execution planning artifacts and updates run.json/index.json
4. Run status becomes `research_planned` (not `complete`)
5. No sources are fetched
6. No external API calls occur
7. No web crawling occurs
8. No fake citations are generated
9. Policies are readable and complete
10. Validator passes
11. No production services touched

## Validation Commands

```bash
cd /home/slimy/kb
git status --short
bash tools/validate-research-schema.sh
bash tools/research-plan-run.sh list
bash tools/research-render-almanac.sh inspect research/runs/2026-06-06-sample-self-hosted-deep-research-agent
bash tools/research-execute-run.sh inspect research/runs/2026-06-06-sample-self-hosted-deep-research-agent
bash tools/research-execute-run.sh plan research/runs/2026-06-06-sample-self-hosted-deep-research-agent --dry-run
bash tools/research-execute-run.sh plan research/runs/2026-06-06-sample-self-hosted-deep-research-agent
bash tools/validate-research-schema.sh
```

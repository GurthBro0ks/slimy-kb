# Runs (Proof Burrows)

A `runs/` directory holds the immutable proof burrow of every research
forage that has been claimed, whether the forage is still in progress, has
been sealed as a harvest, or has been recorded as a failure.

A completed burrow is the source of truth for what a farmhand actually saw,
read, and wrote. The Habitat viewer streams its files through owner-gated
routes; nothing in `runs/` is ever copied into the public web tree.

## Required artifacts

Every burrow directory must contain:

```text
research/runs/YYYY-MM-DD-slug/
  topic.md           # Frozen copy of the seed that was claimed.
  run.json           # Run lifecycle metadata.
  plan.md            # Forage plan: queries, sources, definition of done.
  queries.json       # Every query the runner issued, in order.
  sources.jsonl      # One JSON object per source touched.
  fetched/           # Cached/fetched copies of the sources.
  notes/             # Free-form working notes the farmhand took.
  report.md          # The harvest (human-readable report).
  slides.md          # Slide-by-slide outline of the almanac.
  presentation.pdf   # The almanac. May be absent in Phase 1/2; index pdf_path stays null.
  citations.json     # Structured citations.
  critic.md          # Self-critic / red-team notes. Required before completed.
  RESULT.md          # Standardized run summary, written by the runner.
```

`templates/run-result-template.md` is the canonical skeleton. Use it as a
checklist when you create a burrow.

## Optional artifacts

```text
  timeline.jsonl     # Append-only event log of the forage.
  stdout.log         # Captured stdout/stderr.
  prompts/           # The exact prompts the runner sent to the model.
  screenshots/       # Visual evidence (UI, web) the farmhand collected.
  metadata.json      # Free-form bag of model and env metadata.
  owner-notes.md     # The only file that may be added after `completed` without a rerun.
```

## Immutability rules

- A completed burrow is frozen. Its files must not be edited, renamed, or
  deleted.
- The only mutation allowed on a completed burrow is appending or updating
  `owner-notes.md` (or an explicit rerun manifest that the runner creates
  next to it).
- A rerun creates a NEW burrow with a new directory name and a new
  `immutable_run_id`. The previous burrow stays; the index entry's
  `supersedes` / `superseded_by` fields link them.
- The PDF is derived. Never store only the PDF; always keep the source
  files, the citations, and the proof artifacts alongside it.
- `critic.md` is required for any burrow that ends in `completed`. A
  completed harvest without a critic is treated as a failed run by the
  validator.

## Naming

- Directory: `research/runs/YYYY-MM-DD-slug/`
- `YYYY-MM-DD` is the UTC date the forage was claimed.
- `slug` matches the seed's slug and the index entry's `immutable_run_id`.

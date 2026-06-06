# Run Result Template (proof burrow / forage)

This template is the immutable skeleton of a research run.
Once a forage is `completed`, the proof burrow is sealed and only
`owner-notes.md` or an explicit rerun manifest may be added.

## Required artifacts (Phase 3+)

```text
research/runs/YYYY-MM-DD-slug/
  topic.md           # Frozen copy of the seed that was claimed.
  run.json           # Run lifecycle metadata (id, claim_token, runner_version, model_used, ...).
  plan.md            # Forage plan: queries to run, sources to visit, what counts as 'done'.
  queries.json       # Every query the runner issued, in order, with timestamps.
  sources.jsonl      # One JSON object per source the runner touched (url, fetched_at, kind, hash).
  fetched/           # Cached/fetched copies of the sources (text, html, pdfs).
  notes/             # Free-form working notes the farmhand took during the forage.
  report.md          # The harvest — the human-readable report.
  slides.md          # Slide-by-slide outline of the almanac (PDF is built from this).
  presentation.pdf   # The almanac. May be absent in Phase 1/2; pdf_path stays nullable in the index.
  citations.json     # Structured citations (author, title, url, retrieved_at, used_in_sections).
  critic.md          # Self-critic / red-team notes on the harvest. Required before completed.
  RESULT.md          # Standardized run summary, written by the runner.
```

## Optional artifacts

```text
  timeline.jsonl     # Append-only event log of the forage.
  stdout.log         # Captured stdout/stderr from the runner invocation.
  prompts/           # The exact prompts the runner sent to the model.
  screenshots/       # Any visual evidence (UI, web, etc.) the farmhand collected.
  metadata.json      # Free-form bag of model, run-time, and env metadata.
  owner-notes.md     # Only file that may be added to a completed burrow without a rerun.
```

## Immutability rules

- A completed proof burrow is frozen.
- `owner-notes.md` may be appended/updated by the owner after `completed` to record
  follow-ups, corrections, or new findings the burrow inspired.
- A `rerun` is a NEW burrow (new directory, new `immutable_run_id`). The previous
  burrow stays in place; the index entry's `supersedes` / `superseded_by` fields
  link them.
- Never store only the PDF. Always keep the source files, citations, and
  proof artifacts. The almanac is derived; the burrow is the truth.

## Naming

- Directory: `research/runs/YYYY-MM-DD-slug/`
- `YYYY-MM-DD` is the UTC date the forage was claimed.
- `slug` matches the seed's slug and the index entry's `immutable_run_id`.

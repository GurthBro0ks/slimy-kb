# Phase 6C — Deterministic Source-Note Extraction

> Status: planned (this phase)
> Owns: deterministic parsing of already-fetched source artifacts,
> extracted text artifacts, note file enrichment, and run/index metadata
> updates that advance the run from `sources_fetched` to `notes_ready`.

## Mission

Read already-fetched source artifacts from a run-local `fetched/` tree and
produce clean, reviewable source-note material without using any model or
network access.

Phase 6C is intentionally mechanical. It transforms the existing fetched
artifacts into extraction artifacts and reviewer-ready note files. It does
not summarize semantically, synthesize citations, or claim findings.

## Inputs

- `research/runs/<run-id>/sources.jsonl`
- `research/runs/<run-id>/fetched/<source_id>/response.html|response.txt`
- `research/runs/<run-id>/fetched/<source_id>/metadata.json`
- `research/runs/<run-id>/notes/<source_id>.notes.md` (placeholder from Phase 6B)

## Outputs

For each fetched source:

```text
fetched/<source_id>/
  extracted-text.txt
  extracted-text.json
```

And the corresponding note file is rewritten as a deterministic extraction
record with reviewer checklists and warnings.

## Non-Goals

- No network calls.
- No new URL fetching.
- No search.
- No crawl / link follow / recursive traversal.
- No browser automation.
- No model calls or semantic summarization.
- No citation creation.
- No report writing.
- No final claim extraction.
- No run completion.

## Extraction Rules

1. Original fetched artifact is immutable and must not be changed.
2. HTML parsing uses Python stdlib only (`html.parser`).
3. Scripts, styles, comments, templates, and noscript blocks are ignored.
4. Title extraction is deterministic (`<title>` only for HTML).
5. Heading extraction is deterministic (`h1`..`h6` only, in source order).
6. Visible text extraction is deterministic, whitespace-normalized, and
   stored verbatim in `extracted-text.txt`.
7. `extracted-text.json` contains extraction metadata plus title/headings.
8. Notes file is reviewer-facing and must clearly state that no model summary,
   citation, or final claim has been created.

## State Transitions

```text
sources_fetched -> notes_ready
```

This transition is valid only when every fetched source in the run has an
`extracted-text.txt`, `extracted-text.json`, and an updated note file.

`completed_at` remains null. `claims.jsonl` remains empty in this phase.

## Notes Content Contract

Every note file produced by Phase 6C must include:

- Source ID
- URL and final URL
- HTTP status
- SHA256
- Extracted title
- Extracted headings
- Extracted text preview
- Full extracted text artifact path
- Reviewer checklist:
  - summary reviewed
  - key claims reviewed
  - claim extraction approved
  - citation eligibility approved
- Warning text:
  - `This file was produced by deterministic extraction only. No model summary, citation, or final claim has been created.`

For `https://example.com/`, the note should explicitly say that it is a
smoke/test source and that no report findings should be created from it
without later reviewer approval.

## Audit Trail

The extractor appends a single timeline event per run:

- `source_notes_extracted`

And updates:

- `run.json` (`status`, `notes_extracted_at`, `notes_extractor_version`)
- `research/indexes/index.json` (same fields mirrored)

## Rollback

`git revert <phase-6c-commit>` is sufficient. No external services or
network state are involved in this phase.

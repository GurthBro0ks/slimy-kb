# Source Notes Policy

> Applies to Phase 6C deterministic extraction and later reviewer-driven note
> curation.

## 1. Deterministic Only In This Phase

Phase 6C source notes are produced by deterministic parsing of already-fetched
artifacts. They are not model summaries.

The extractor may:

- Read HTML or text response artifacts already stored in the run.
- Remove scripts/styles/comments.
- Extract title, headings, and visible text.
- Normalize whitespace.
- Write extraction artifacts and reviewer-facing note files.

The extractor must not:

- Interpret intent.
- Summarize with an LLM.
- Generate or rank claims.
- Decide citation eligibility.
- Write findings into `report.md`.

## 2. Reviewer Ownership

The note file is a review surface, not a final research artifact.

The human reviewer owns:

- Summary approval
- Key claim review
- Claim extraction approval
- Citation eligibility approval

Until a later phase explicitly creates structured claim/citation records,
the Phase 6C note remains advisory only.

## 3. Example.com Smoke Source Rule

If the source URL is `https://example.com/`, the note should explicitly say
that the source is a smoke/test source.

The source may prove the extractor works, but it must not be treated as a
real evidence source for final findings unless a later reviewer explicitly
approves that use.

## 4. Artifact Integrity

The original fetched artifact (`response.html` or `response.txt`) is immutable.
Phase 6C writes sidecar extraction artifacts only:

- `extracted-text.txt`
- `extracted-text.json`
- updated `notes/<source_id>.notes.md`

## 5. No Claims / No Citations

Phase 6C leaves `claims.jsonl` empty. It does not create citations or claim
records. It does not change `citation_count`.

## 6. No Network / No Browser / No Model

This phase is entirely local and deterministic:

- No network calls
- No browser automation
- No JavaScript execution
- No search / crawl / link following
- No model / Hermes / external API calls

## 7. Visibility

The note file must clearly show what was extracted and where it came from:

- source metadata
- extracted title
- extracted headings
- extracted text preview
- full artifact paths
- explicit deterministic extraction warning

If a reviewer cannot tell the difference between extracted text and a human
summary, the note file is too ambiguous and should be revised.

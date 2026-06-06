# Topics (Seeds)

A topic file is a single research question, framed so a critter can pick it
up from the quest board and start foraging. In Phase 1 the lifecycle is
declared but not automated; the canonical seed template is
`research/templates/research-topic.template.md`.

## Frontmatter contract

The minimum required frontmatter for any seed is:

```yaml
---
type: research_topic
status: queued
priority: normal
depth: deep
output: presentation_pdf
title: Example title
slug: example-title
created_by: Gurth
created_at: YYYY-MM-DD
audience: technical_owner
visibility: owner
tags:
  - ai-agents
---
```

A starter set of recommended optional fields lives in the frontmatter
contract (see the planning doc and
`templates/research-topic.template.md`):

```yaml
seed_kind: one_shot
question: ""
scope_notes: ""
constraints: []
related_projects: []
assigned_critter: ""
campaign: ""
claim_token: ""
claimed_at: ""
started_at: ""
completed_at: ""
supersedes: ""
superseded_by: ""
```

## Allowed `status` values

- `queued`     — sitting on the quest board, no forage has started.
- `running`    — the forage is in progress.
- `complete`   — the harvest is sealed; the proof burrow is immutable.
- `failed`     — the forage ended without a harvest; the burrow records why.
- `archived`   — kept for history, hidden from the default Habitat view.

## Allowed `priority` values

`low`, `normal`, `high`, `urgent`. Habitat sorts by priority then by
`created_at` (newest first within a priority bucket).

## Allowed `depth` values

- `quick`     — under ~30 minutes, one pass of sources, no critic.
- `standard`  — about an hour, two passes, light critic.
- `deep`      — multi-hour, three+ passes, full critic and almanac.

## Allowed `output` values

- `report_md`         — Markdown report only.
- `presentation_pdf`  — Almanac PDF (default; also implies a Markdown report).
- `report_and_pdf`    — Explicit "both" — same effect as `presentation_pdf`
                        for Phase 1, kept as a distinct value for future
                        tooling that wants to disambiguate.

## Body conventions

Keep the body short. The seed is a brief, not a paper. Suggested sections:

- `# Question` — one paragraph.
- `# What matters` — 3-6 bullets.
- `# Out of scope` — explicit non-goals.
- `# Constraints` — must-haves the forage must respect.
- `# Acceptance for the harvest` — what 'done' means.

## Mutability rules

- A queued seed may be edited freely.
- Once a seed is actively in `running`, prefer to write a new seed for any
  material change rather than silently mutating the research question.
- The proof burrow owns the historical state; the seed is the current state.

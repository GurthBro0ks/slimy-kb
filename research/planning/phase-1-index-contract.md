# Phase 1 Index Contract

This document defines the exact Phase 1 read-only contract Habitat will later
consume from `slimy-kb`.

## Canonical source

- Canonical KB repo: `/home/slimy/kb`
- Canonical Research Farm root: `/home/slimy/kb/research`
- Canonical read-only index: `/home/slimy/kb/research/indexes/index.json`

Phase 1 is schema-only and contract-only.

- No runner is built here.
- No queue controls are built here.
- No Habitat routes are built here.
- No Hermes dependency is introduced here.
- No `mathomhaus/guild` install or integration lands here.

## Purpose

Habitat should later read a generated index instead of scanning the full KB
tree directly. This keeps the first UI integration read-only, predictable, and
 owner-gated.

## Top-level `index.json` shape

```json
{
  "schema_version": 1,
  "generated_at": null,
  "source_root": "/home/slimy/kb/research",
  "ui_theme": "research_farm",
  "items": []
}
```

### Top-level field meanings

- `schema_version`: breaking-contract version for Habitat consumers.
- `generated_at`: ISO 8601 UTC timestamp when an automated generator produces
  this file. `null` in Phase 1 because the runner does not exist yet.
- `source_root`: absolute canonical root for research artifacts.
- `ui_theme`: fixed theme label so Habitat can select farm/guild language.
- `items`: list of read-only research records for the quest board, active
  forages, and harvest views.

## Item fields

Each item in `items` may contain the following fields:

- `immutable_run_id`
- `slug`
- `title`
- `status`
- `priority`
- `depth`
- `confidence`
- `source_count`
- `citation_count`
- `created_at`
- `started_at`
- `completed_at`
- `model_used`
- `runner_version`
- `pdf_path`
- `report_path`
- `critic_path`
- `proof_path`
- `topic_path`
- `tags`
- `related_harness_session`
- `related_guild_campaign`
- `assigned_critter`

### Item field meanings

- `immutable_run_id`: stable identifier for a proof burrow once a forage has a
  concrete run folder.
- `slug`: stable topic slug used for routing and display.
- `title`: human-readable seed/harvest title.
- `status`: one of `queued`, `running`, `complete`, `failed`, `archived`.
- `priority`: one of `low`, `normal`, `high`, `urgent`.
- `depth`: one of `quick`, `standard`, `deep`.
- `confidence`: nullable numeric confidence in the harvest.
- `source_count`: integer count of captured sources.
- `citation_count`: integer count of captured citations.
- `created_at`: `YYYY-MM-DD` seed creation date.
- `started_at`: nullable ISO 8601 UTC forage start timestamp.
- `completed_at`: nullable ISO 8601 UTC harvest completion timestamp.
- `model_used`: nullable model identifier.
- `runner_version`: nullable runner version identifier.
- `pdf_path`: nullable path to the almanac PDF under `research/`.
- `report_path`: nullable path to `report.md` under `research/`.
- `critic_path`: nullable path to `critic.md` under `research/`.
- `proof_path`: nullable path to the proof burrow directory under
  `research/runs/`.
- `topic_path`: path to the seed Markdown file under `research/topics/`.
- `tags`: lowercase tags for Habitat filtering.
- `related_harness_session`: nullable reference to a harness session.
- `related_guild_campaign`: nullable future bridge field only.
- `assigned_critter`: nullable current critter/farmhand owner.

## Habitat consumption rules

- Habitat reads this index only.
- Habitat must later stream files through owner-gated routes.
- Habitat must not expose PDFs publicly.
- Habitat must not treat any other store, including guild SQLite, as the
  source of truth.

## Phase 1 notes

- `items` starts empty by design.
- sample or draft topic files may exist under `research/topics/`, but they are
  not automatically listed until a later generator or manual curation step adds
  them to the index.

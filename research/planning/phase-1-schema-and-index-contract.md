# Phase 1 — Research Farm Schema and Habitat Index Contract

This draft planning note is retained for context.

Canonical Phase 1 contract doc:
- `research/planning/phase-1-index-contract.md`

Where this draft differs from the canonical contract, the canonical contract
wins.

Phase 1 plants the canonical Research Farm contract in the KB repo. It does
not build a runner, does not add Habitat UI, does not wire Hermes or the
mathomhaus/guild MCP, and does not install any packages.

## Scope summary

What this phase ships:

- `research/` folder skeleton under `/home/slimy/kb/research/`.
- Topic/seed frontmatter contract (see `research/topics/README.md`).
- Run/proof-burrow artifact contract (see `research/runs/README.md` and
  `research/templates/run-result-template.md`).
- Two JSON Schemas under `research/templates/`:
  - `research-index.schema.json` (top-level Habitat contract)
  - `index-entry.schema.json` (one seed/burrow)
- `research/indexes/index.json` as the read-only contract Habitat will
  consume later.
- One sample queued research seed
  (`research/topics/sample-self-hosted-deep-research-agent.md`) and its
  matching index entry.
- A stdlib-only validator: `tools/validate-research-index.py`.
- This planning doc with Phase 2 readiness criteria.

What this phase explicitly does NOT do:

- No runner, no quest-board UI, no claim-token logic.
- No Habitat UI source changes. `/opt/slimy/gh-tracker` is read-only.
- No Hermes, no `mathomhaus/guild`, no MCP wiring.
- No systemd, no cron, no watchers, no crawlers, no package installs.
- No public exposure. No research artifacts are copied into
  `apps/web/public/` or any Caddy-served directory.
- No PDF generation. `pdf_path` stays null in the index until Phase 3.

## Inspiration sources (reference only)

These are the upstreams the contract is shaped against. None of them are
edited or installed by Phase 1.

| Inspiration | How it shapes Phase 1 | Direct edits in Phase 1? |
|-------------|----------------------|--------------------------|
| `/home/slimy/kb` (slimy-kb) | Source of truth. Topics, runs, lore, index all live here. | Yes — additive only. |
| `/opt/slimy/gh-tracker` (Habitat) | Future owner-gated viewer. Consumes `research/indexes/index.json`. | **No.** Reference only. |
| `mission-control` (orchestration) | Pattern for future run lifecycle states. | No. |
| `mathomhaus/guild` MCP | Pattern for quest / lore / atomic-claim concepts. | No. |
| `Hermes` (optional runtime) | Optional future research runner. Not live on this host. | No. |
| Slimy harness | Pattern for proof-pack conventions (RESULT.md, proof dir). | No harness state read or written. |

## Phase 2 readiness criteria

Phase 2 may begin only when all of the following are true:

1. The Phase 1 validator passes against the current `index.json`.
2. The `topic_path` referenced by the sample index entry exists on disk and
   parses as a Markdown file with the minimum frontmatter.
3. No file in `research/` is a PDF or other binary that would normally
   live in a future burrow; the sample burrow directory is intentionally
   empty.
4. `/opt/slimy/gh-tracker` has not been modified in Phase 1 (verified by
   `git status` from that repo).
5. The KB repo's existing wiki compile pipeline (`bash tools/kb-lint.sh`)
   does not produce NEW warnings introduced by this phase.
6. `logs/game-compile.log` is unchanged from its pre-Phase-1 dirty state
   (it is intentionally still dirty; we just don't touch it).
7. A draft of the runner's command surface is in the planning folder so
   the Phase 2 prompt can be written without re-deriving it.
8. The owner has reviewed `RESULT.md` from the Phase 1 proof directory
   and confirmed `RESULT=PASS` (or accepted `RESULT=WARN` with notes).

## Out-of-scope reminders for future phases

- PDF (almanac) generation: Phase 3+; the index contract already permits a
  nullable `pdf_path`.
- Quest-board UI in Habitat: Phase 2+; the index already provides the
  fields Habitat will display.
- Quest-board claim tokens and atomic-claim semantics: Phase 2+; the index
  already has `claim_token` and `assigned_critter` (currently unused).
- Lore barn curation: Phase 2+; the empty `research/lore/` directory is
  ready to receive content.
- Public web routes: never. Habitat is owner-gated and reads from the
  index server-side; no copy of research content is ever served from a
  public path.

---
type: research_topic
status: queued
priority: normal
depth: deep
output: presentation_pdf
title: Self-hosted deep research agent architecture
slug: sample-self-hosted-deep-research-agent
created_by: Gurth
created_at: 2026-06-05
audience: technical_owner
visibility: owner
tags:
  - ai-agents
  - nuc
  - slimy-kb
  - habitat
seed_kind: one_shot
question: "What is the best architecture for a Slimy-owned deep research system that writes proof-packed reports back into slimy-kb and displays them in Habitat?"
scope_notes: "Phase 1 sample seed only. Do not run research from this file yet."
constraints:
  - "Use slimy-kb as source of truth."
  - "Keep Habitat owner-gated."
  - "Do not build runner or queue controls during Phase 1."
related_projects:
  - "slimy-kb"
  - "gh-tracker"
  - "slimy-harness"
assigned_critter: ""
campaign: "research-farm-bootstrap"
claim_token: ""
claimed_at: ""
started_at: ""
completed_at: ""
supersedes: ""
superseded_by: ""
---

# Question

What is the best architecture for a Slimy-owned deep research system that
writes proof-packed reports back into slimy-kb and displays them in Habitat?

# What matters

- KB-native topics and outputs
- Habitat read-only viewer first
- Presentation PDF output later
- Proof burrows for sources/citations/critic notes
- Farm/guild/pet-habitat theme
- No office metaphor
- No public exposure

# Out of scope (for this forage)

- Building the actual runner. Phase 1 only plants the contract.
- Wiring Hermes or the mathomhaus/guild MCP.
- Adding any Habitat UI routes.
- Installing new system packages or starting any watchers.

# Constraints

- All artifacts stay under `research/`.
- Proof burrows are immutable once `completed`.
- The almanac PDF is optional until Phase 3; the index contract permits
  `pdf_path: null`.

# Acceptance for the harvest

- A `report.md` that names the chosen architecture, the data flow, and the
  owner-gating boundary.
- A `critic.md` that red-teams the chosen architecture against the
  "no public exposure" and "no office metaphor" rules.
- A `citations.json` that links every architectural decision to a source
  fetched into `fetched/`.
- A `RESULT.md` that links the burrow directory into
  `research/indexes/index.json` with `status: completed`.

# KB Bridge — Gear Donation
> Category: projects
> Sources: raw/agent-learnings/2026-05-20-nuc1-gear-bridge-design.md
> Created: 2026-05-20
> Updated: 2026-05-20
> Status: draft

<!-- KB METADATA
> Last edited: 2026-06-20 09:08 UTC (git)
> Version: r67 / c7b148a3
KB METADATA -->

KB bridge extension that publishes gear scan digests from NUC1 to NUC2's KB inbox.

## Overview

NUC1 runs a gear donation system: Discord users donate Super Snail game gear screenshots via `/gear-donate`, the bot scans them via vision AI, and results are stored locally. The KB bridge already publishes host state and repo digests to NUC2 on a 12h cadence. Phase 1B added a gear scan digest collector.

**Design**: Extend the existing kb-bridge with a `collect_gear_scan_digests.py` collector that runs daily, reuses the existing SCP fail-soft channel, and produces a compact digest of gear scan results.

## Gear Donation Flow (NUC1)

1. User posts gear screenshot via `/gear-donate` slash command (Discord)
2. `gear-donate.ts` downloads image → `/home/slimy/gear-submissions/raw/YYYY-MM-DD/<specimen_id>.png`
3. Bot calls `scanGearSubmission()` synchronously — vision AI analyzes via Gemini or OpenAI-compat endpoint
4. Scan JSON written → `/home/slimy/gear-submissions/scans/YYYY-MM-DD/gear_<stamp>_<sha>.scan.json`
5. User receives Discord embed with detected gear/soul names

## Storage Structure

```
/home/slimy/gear-submissions/
├── submissions.jsonl        # JSONL ledger — primary record (58 records)
├── raw/                     # Raw image files (YYYY-MM-DD/)
├── metadata/                # Per-specimen metadata JSON (YYYY-MM-DD/)
├── scans/                   # Scan result JSON files (YYYY-MM-DD/)
│   ├── gear_20260520T090008Z_0c8d28.scan.json  # completed
│   ├── gear_20260520T091755Z_6f610e.scan.json  # failed (API 400 error)
│   └── gear_20260520T092709Z_fd86a5.scan.json  # completed_with_warnings
└── queue/                   # Empty (sync scan, no async queue)
```

## Scan Result Schema (v1.2.0)

Each scan JSON contains:
- `specimen_ids[]` — array of specimen IDs scanned together
- `scan_status` — completed | completed_with_warnings | failed | provider_unavailable
- `provider_name` — gemini | openai-compat | unavailable
- `model_name` — e.g. gemini-2.5-flash
- `image_results[]` — per-image: image_type (gear_card/soul_screen/unknown_*), confidence, extracted fields
- `warnings[]` — any scan anomalies
- `created_at` — ISO timestamp

## Phase 1B Schema Enhancements (collect_gear_scan_digests.py)

Digest schema v1.0 added:
- `specimen_refs[]` — top-level list of all specimen IDs seen in the digest period
- `run_id` — deterministic content hash (`YYYYMMDDTHHMMSSZ-<sha8>`) for idempotent same-day reruns
- `prev_digest_date` — links to prior digest from a different date (not same-date reruns)
- `detected_gear_items[].specimen_ids[]` — back-link to source specimens per gear item
- `detected_soul_items[].specimen_ids[]` — back-link to source specimens per soul item
- `detected_soul_items[].linked_gear_refs[]` — gear_names from same scan for cross-reference
- `scans_processed[]` — dict objects `{"filename": str, "specimen_ids": []}` not bare strings
- `generated_at` moved to write time (not in content hash for idempotency)

## Discord CDN Block Issue

Recent scans show Gemini API 400 when trying to fetch Discord CDN image URLs (`https://cdn.discordapp.com/...`). Discord CDN restricts external fetching — this is a known failure mode.

**Impact**: Gear scans for Discord-attached images fail with `provider_unavailable` or `unknown_error`. Donation still completes (safe failure — scan never blocks donation).

**Current behavior**: User sees "queued for lab review" or "completed with warnings" in Discord reply.

## Known Failure Modes

| Failure | Cause | User Impact |
|---------|-------|-------------|
| Gemini API 400 (Discord CDN) | Discord CDN blocks external image fetch | completed_with_warnings or failed |
| API provider unavailable | Vision API down | provider_unavailable, retry later |

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md)
- [Slimy KB](slimy-kb.md)
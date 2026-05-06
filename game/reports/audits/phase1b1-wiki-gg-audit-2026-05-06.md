# Phase 1B.1 Wiki.gg Raw Wikitext Audit

Generated UTC: Wed May  6 03:08:21 PM UTC 2026

## Current Git State

24a01f9 (HEAD -> master, origin/master, origin/HEAD) docs: Phase 1B repo hygiene audit
7947f93 feat: Phase 1B — inventory, OCR prompts, structured data, RE sources
ae40dc1 feat: Phase 1A — Super Snail game database scaffold with 15 schemas
dc71de6 Merge pull request #1 from GurthBro0ks/main
21ba25c kb: query - wiki setup and harness build flow

## Wiki.gg File Summary
- Directory: game/sources/wiki_gg
- Wiki file count: 4123
- Directory size: 20M
- Directory size bytes: 7304986
- Largest file bytes: 380960

## Largest Files (Top 20)
- 0.36 MB  game/sources/wiki_gg/Time_Beacon.wiki
- 0.23 MB  game/sources/wiki_gg/Journey_to_the_West.wiki
- 0.10 MB  game/sources/wiki_gg/Gear.wiki
- 0.09 MB  game/sources/wiki_gg/Fissure.wiki
- 0.09 MB  game/sources/wiki_gg/Minion_Sim.wiki
- 0.05 MB  game/sources/wiki_gg/Weekly_Events_History.wiki
- 0.05 MB  game/sources/wiki_gg/Gene_Simulation.wiki
- 0.05 MB  game/sources/wiki_gg/Time_Rift_Apostles.wiki
- 0.05 MB  game/sources/wiki_gg/Golden_Week.wiki
- 0.05 MB  game/sources/wiki_gg/Time_Rift_INTEL.wiki
- 0.04 MB  game/sources/wiki_gg/Treasure_Collection.wiki
- 0.04 MB  game/sources/wiki_gg/Cathay_Domain.wiki
- 0.04 MB  game/sources/wiki_gg/Kemet_Pyramids.wiki
- 0.04 MB  game/sources/wiki_gg/Past_and_Future_Apostles.wiki
- 0.04 MB  game/sources/wiki_gg/Snail_Avatar.wiki
- 0.04 MB  game/sources/wiki_gg/Fugitives.wiki
- 0.04 MB  game/sources/wiki_gg/Nursery.wiki
- 0.03 MB  game/sources/wiki_gg/Yamato_Domain.wiki
- 0.03 MB  game/sources/wiki_gg/Relic_Guide.wiki
- 0.03 MB  game/sources/wiki_gg/Murikan_Domain.wiki

## Archive or Binary Candidates

## Decision Gate
Commit wiki_gg only if all are true:
- Total wiki_gg size is under 100 MB: PASS (7.3 MB < 100 MB)
- Largest individual file is under 5 MB: PASS (372 KB < 5 MB)
- No archive or binary candidates found: PASS (0 found)
- Files are raw text wikitext exports: PASS (all files are ASCII/Unicode text)

## Decision: SAFE TO COMMIT
All safety gates passed. Files are raw wikitext exports under size limits with no binaries or archives.

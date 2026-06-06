# Lore (Source / Lore Barn)

This directory is the planned home of the future source archive, themed
as the pet-habitat "lore barn." It is intentionally a stub in Phase 1.

## What this is NOT in Phase 1

- `research/lore/` does NOT replace `raw/`. The existing `raw/` tree under
  `/home/slimy/kb/raw/` continues to be the source of truth for the wiki
  compile pipeline.
- `research/lore/` does NOT receive writes from the research runner (the
  runner does not exist yet in Phase 1).
- `research/lore/` is not indexed by `research/indexes/index.json`. The
  index contract points at topics and proof burrows, not at the lore barn.

## What this WILL be in later phases

- A read-mostly archive of canonical sources the research runner has
  fetched, organized by topic and by source kind.
- A mirror/compile relationship with `raw/`: `raw/` is the wiki pipeline's
  source of truth, `lore/` is the research pipeline's source of truth. The
  two may cross-pollinate through the future quest-board curation flow, but
  neither one replaces the other.
- A farm-friendly view of long-form references: books, papers, internal
  design notes, game wikis, and screenshots of UI that the critters needed
  to read during a forage.

## Why a stub now

Planting the directory now lets the future lore-barn code path land without
having to move topics and burrows around later, and it keeps the folder
map in `README.md` honest.

Until Phase 2 or later, the only file in `research/lore/` is this README.

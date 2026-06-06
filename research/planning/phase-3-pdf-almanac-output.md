# Phase 3: PDF Almanac Output

## Goal
Build a local KB-side almanac renderer that reads an existing Research Farm run folder and produces:
1. A self-contained HTML almanac (`almanac.html`)
2. Optionally a landscape PDF (`presentation.pdf`) if Chrome/Chromium is available

## Constraints
- Standard-library-first Python tooling
- No package installs
- No external API calls
- No web crawling
- No service restarts
- Output stays inside the run folder
- Never overwrite completed output without `--force`
- Mark placeholder/demo runs clearly
- Keep Habitat read-only

## Files Added
- `tools/research-render-almanac.py` — main renderer (stdlib-only Python)
- `tools/research-render-almanac.sh` — bash wrapper
- `research/templates/almanac.css` — dark-themed presentation CSS
- `research/templates/almanac-render.schema.json` — JSON schema for render metadata
- `research/planning/phase-3-pdf-almanac-output.md` — this file

## Commands
- `inspect <run-dir>` — print run metadata without modifying files
- `render-html <run-dir> [--dry-run] [--force]` — render almanac.html
- `render-pdf <run-dir> [--dry-run] [--force]` — render presentation.pdf
- `self-test` — create temporary run and validate HTML generation

## HTML Requirements
- Self-contained (inline CSS, no remote deps)
- Dark-friendly presentation style
- Farm/guild/pet-habitat language
- Sections: title, status badge, seed summary, plan, report, slides, sources, citations, critic, proof burrow
- Clear placeholder warning for planned/demo runs

## PDF Requirements
- Landscape orientation preferred
- Generated via Chrome headless `--print-to-pdf`
- Uses Playwright's Chromium if available at `~/.cache/ms-playwright/`
- Falls back to system chromium/chrome
- WARN (not FAIL) if no browser available
- Local file only, never in `public/`

## Index Updates
After rendering, updates:
- `run.json`: almanac_path, almanac_generated_at, almanac_renderer_version, pdf_path, pdf_generated_at, pdf_renderer
- `research/indexes/index.json`: matching fields for the run's immutable_run_id

## Overwrite Protection
- `almanac.html` and `presentation.pdf` are not overwritten unless `--force` is passed
- This prevents accidental regeneration of completed outputs

## Status Semantics
- Rendering does NOT change `RESULT=PLANNED` into `RESULT=PASS`
- Rendering does NOT mark research as complete
- Almanac/PDF are presentation artifacts, not research completion markers

# Gear Website Package

Generated UTC: 2026-05-06T17:58:45.299933+00:00

## Files

- `gear.web.package.json` — full website-ready card data.
- `gear.web.compact.json` — smaller card payload for static import.
- `gear.web.search.json` — search index payload.
- `gear.web.filters.json` — tier/stat/sort config.
- `icons/` — local icon files plus fallback placeholder.

## Suggested slimy-monorepo destination

Copy JSON files to:

`/opt/slimy/slimy-monorepo/apps/web/src/data/supersnail/gear/`

Copy icons to:

`/opt/slimy/slimy-monorepo/apps/web/public/kb/gear/icons/`

## UI Notes

- Use `tierClass` for red/orange/purple/blue/green/white/gray styling.
- Use `icon.src` for images.
- If `icon.missing` is true, render the fallback placeholder.
- Do not rely on slot. Slot is nullable.
- Use `stats.hp`, `stats.atk`, `stats.def`, and `stats.rush` as first-class card values.


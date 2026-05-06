# Phase 1C.7 Canonical Gear QA and Export Audit

Generated UTC: 2026-05-06T17:10:17.031217+00:00

## Result

Canonical gear QA passed and website/bot export artifacts were generated.

## Counts

- Canonical gear records: 313
- Index records: 313
- Duplicate IDs: 0
- Duplicate names: 0

## Tier Counts

- gray: 25
- green: 36
- blue: 33
- purple: 48
- orange: 91
- red: 80

## Export Files

- game/data/exports/gear/gear.by-tier.json — 321263 bytes — sha256 d0d44b3f95b88b38d19e5bb6f66b02d2ae435dabd737e150b9e69cab19b2d41a
- game/data/exports/gear/gear.canonical.full.json — 321472 bytes — sha256 952ec8d74041d650360f27d008c5bbca8426b95b1dad78586ec2c4612cd2c5b9
- game/data/exports/gear/gear.search.json — 91429 bytes — sha256 6d630b604b557d7fa280888889b4b2197159c4a76028d4cfe2cac68e672796a9
- game/data/exports/gear/gear.stats-summary.json — 73897 bytes — sha256 993b37859f478f538da89bca91ec999abc7b3f000e6148cc454f1fa691a72e1e
- game/data/exports/gear/gear.web.cards.csv — 38696 bytes — sha256 abade5cb1ab51a9e12887646756868c03550dc6aba59eb9b00dedb9d4c66c59c
- game/data/exports/gear/gear.web.cards.json — 103358 bytes — sha256 5adbab8ec96b6607fe7192443c711d29ee1e586dfd56e9f4d156f0ced96af76c

## Next Step

Phase 1D should import or map gear icon assets and create an asset manifest keyed by canonical gear ID.
After icon assets are stable, export files can be wired into slimy-monorepo website routes.


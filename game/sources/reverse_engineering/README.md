# slimy_snail

Safe scaffold repo for the Slimy/Super Snail protocol, rank, club, and API reconnaissance work.

## Current status

This repo is scaffold-only.

No decoded game artifacts, protocol files, captures, APK/XAPK files, `.luac` files, account data, tokens, or session material should be committed until the evidence-reset task produces a clean proof directory.

## Purpose

This project will eventually organize:

- protocol decode tooling
- clean evidence reports
- rank/group/club target mapping
- MITM/API capture analysis
- safe API-client experiments
- dashboard bridge planning for Slimy systems

## Current phase

Phase 0: repository scaffold.

Waiting for clean proof output from the protocol evidence reset task.

## Import rule

Only import files from a proof directory that ends with one of these statuses:

- `PASS_CLEAN_ORIGINALS_READY`
- manually approved `PARTIAL_ORIGINALS_MISSING`

Never import contaminated v2 outputs directly.

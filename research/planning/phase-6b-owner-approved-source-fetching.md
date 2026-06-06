# Phase 6B — Owner-Approved Source Fetching

> Status: planned (this phase)
> Owns: `tools/research-fetch-sources.{py,sh}`, the run-local
> `pending-sources.json` file, the per-source `fetched/<source_id>/` tree,
> and the new run.json / sources.jsonl / timeline.jsonl fields.
> Inherits: Phase 1 schema foundation, Phase 2 seed-to-run planner, Phase 3
> almanac, Phase 4 Habitat read-only UI, Phase 5 queue controls, Phase 6A
> execution contract.

## Mission

Allow a Research Farm run to fetch ONLY the explicit URLs that the owner
has pre-approved and written into a run-local `pending-sources.json` file.
Save the fetched artifacts and update the run's source records. Do not
mark the run as complete.

## Non-Goals (this phase)

- Search engines, crawling, recursive link following.
- Model summarization, claim synthesis, citation generation.
- Report writing or almanac regeneration.
- Hermes, guild, mathomhaus, or any external system integration.
- Public publishing or report distribution.

## Workflow

```
owner  →  edit pending-sources.json (run-local, owner-only)
owner  →  bash tools/research-fetch-sources.sh fetch <run-dir> [--dry-run]
tool   →  validate every URL (scheme, host, IP, length, creds)
tool   →  fetch each approved URL with timeout + max-size
tool   →  save fetched/<source_id>/{response.txt|html,metadata.json,fetch-result.json}
tool   →  update sources.jsonl
tool   →  update run.json (status, source_count, fetched_at, fetcher_version)
tool   →  update research/indexes/index.json
tool   →  append timeline.jsonl entries
tool   →  exit 0 (run remains not-complete)
```

The tool never follows links out of the fetched document. It never
re-requests an asset the page references. It never sends cookies or
credentials. It uses Python's stdlib only.

## Status Transitions

```
research_planned
   →  sources_fetched       (at least one source fetched successfully)
   →  partial_fetch_failed  (some sources fetched, some failed)
```

The fetcher never writes status `complete`. The fetcher never writes
`draft_ready` or any synthesis-level state. Those belong to later phases.

## Source Record

A source record appended to `sources.jsonl` follows the
`source-record.schema.json` shape (extended in Phase 6B with optional
fetch fields: `final_url`, `http_status`, `content_type`, `bytes_saved`,
`sha256`, `artifact_path`, `notes_path`).

Every fetched source also gets a per-source `fetched/<source_id>/` tree
containing `metadata.json`, `fetch-result.json`, and the response
artifact. The per-source metadata follows
`source-fetch-record.schema.json` and is the authoritative timestamped
record of the actual HTTP exchange.

## URL Safety

Before any HTTP exchange, the tool validates:

1. Scheme is `http` or `https`. Reject `file`, `ftp`, `data`, `gopher`,
   `javascript`, etc.
2. No credentials in the URL (`user:pass@host` is rejected).
3. URL length ≤ 4096 characters.
4. The hostname resolves to a public IPv4 or IPv6 address. The tool
   resolves the hostname itself and inspects every returned address
   against the blocklist (no DNS-rebinding trickery). Blocked ranges:
   - 127.0.0.0/8, 0.0.0.0, ::1 (loopback)
   - 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (RFC1918 private)
   - 169.254.0.0/16 (link-local)
   - 100.64.0.0/10 (CGNAT)
   - 224.0.0.0/4, ff00::/8 (multicast)
   - fc00::/7, fe80::/10 (IPv6 ULA / link-local)
   - ::, 0.0.0.0 (unspecified)
5. Redirects (HTTP 3xx) are followed only when the redirect target's
   scheme, host, and resolved IPs all pass the same checks. Maximum
   3 redirects per request.
6. Connect timeout: 10 s. Read timeout: 30 s. Max response body:
   5 MiB (configurable; larger responses are truncated and flagged).
7. Only the listed `User-Agent` is sent. No cookies, no auth headers.

A rejected URL is recorded in the run's `sources.jsonl` with
`status: "failed"` and `error_message` containing the reason. The rest
of the run continues.

## Files Produced (per source)

```
research/runs/<run-id>/fetched/<source_id>/
  response.html        # or response.txt for non-HTML content
  metadata.json        # source-fetch-record schema
  fetch-result.json    # per-source fetch outcome with redirects, timing
```

A placeholder `notes/<source_id>.notes.md` is also created using the
existing `source-notes.template.md` skeleton, with the metadata fields
pre-filled.

## Index Updates

The run's entry in `research/indexes/index.json` is updated
in-place to reflect the new `source_count`, `status`, `fetched_at`,
`fetcher_version`, and `execution_fetched_at` (when present). Existing
fields are preserved.

## Dry-run

Every command that could write or fetch accepts `--dry-run`. Dry-run
prints what would be done and never opens a socket.

## Rollback

`git revert <phase-6b-commit>; git push` (do not push in this phase per
the safety rules). The fetcher only writes to run-local directories and
`research/indexes/index.json`; revert fully restores prior state because
the prior state was committed in the prior phase.

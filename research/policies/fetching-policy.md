# Source Fetching Policy

> Phase 6B — applies to `tools/research-fetch-sources.{py,sh}` and to any
> future code that performs network reads on behalf of a research run.
> Inherits the broader execution-safety-policy.md.

## 1. The Network Is Untrusted

Pages, redirects, response bodies, response headers, and metadata
fetched from the public Internet are untrusted input. The fetcher:

- Never executes JavaScript.
- Never executes shell commands derived from page content.
- Never parses HTML for `<a href>` and follows them.
- Never sends cookies, Authorization headers, or other credentials.
- Never uses browser automation.
- Never imports a headless browser.

## 2. Only Owner-Approved URLs May Be Fetched

A source may only be fetched if it appears in
`research/runs/<run-id>/pending-sources.json` with:

- `source_id` (run-local unique).
- `url` (one URL).
- `title_hint`, `source_type`, `reason`, `approved_by`, `approved_at`.

A `pending-sources.json` with an empty `sources` array is valid and
performs zero fetches. The tool must never auto-add URLs.

## 3. URL Safety Checks (Mandatory)

Before any HTTP exchange the tool MUST verify:

- Scheme is `http` or `https` only.
- No credentials in the URL.
- URL length ≤ 4096.
- The hostname resolves to a public IP (no loopback, no private,
  no link-local, no multicast, no unspecified, no CGNAT).
- All IPs the hostname resolves to are checked — not just the first.
- Redirects are re-validated against the same rules.
- Hard caps: ≤ 3 redirects, ≤ 10 s connect, ≤ 30 s read,
  ≤ 5 MiB body (larger bodies are truncated, the record is marked
  `truncated: true`).

A failed safety check results in a `failed` source record. The rest of
the run is not affected.

## 4. What The Fetcher May Save

- The raw response body (HTML or plain text) under
  `fetched/<source_id>/response.html` or `response.txt`.
- A `metadata.json` (source-fetch-record) with timestamps, sizes,
  hashes, headers, and the resolved IPs.
- A `fetch-result.json` describing the outcome (success, redirect
  chain, failure reason).
- A `sources.jsonl` record.
- A `timeline.jsonl` entry per source attempt.
- A `notes/<source_id>.notes.md` placeholder (not yet filled in).
- Updates to `run.json` and `research/indexes/index.json`.

The fetcher MUST NOT:

- Generate citations.
- Generate claims.
- Synthesize findings.
- Edit `report.md`, `critic.md`, or `almanac.html`.
- Regenerate `presentation.pdf`.
- Publish anywhere.

## 5. Status Discipline

The fetcher writes one of two run states:

- `sources_fetched` — at least one source fetched cleanly.
- `partial_fetch_failed` — at least one source failed.

It never writes `complete`, `archived`, `failed` (as a run state), or
synthesis-level states. Those belong to later phases.

## 6. Failure Recording

Every URL that fails for any reason (safety, DNS, connect, HTTP 4xx/5xx,
size, timeout) gets a record in `sources.jsonl` with
`status: "failed"` and a non-empty `error_message`. The run is not
aborted by a single failure.

## 7. Idempotence

Re-running the fetcher on the same run:

- Skips sources whose `fetched/<source_id>/metadata.json` already
  exists AND whose recorded `sha256` matches the current
  `pending-sources.json` URL entry.
- Records the skip in `timeline.jsonl` with `status: "skipped"`.

The owner can force a re-fetch by deleting the
`fetched/<source_id>/metadata.json` file. The tool never overwrites a
previous artifact silently; it writes a new artifact named with a
counter suffix (`metadata.2.json`, etc.) so the original is preserved.

## 8. Audit

Every fetch produces:

- One line in `sources.jsonl` (or append/update).
- One line in `timeline.jsonl`.
- An updated `research/indexes/index.json` entry.

These three files together form the audit trail for the run.

## 9. Out Of Scope (Explicit)

- Search engines.
- Crawling.
- Link following.
- JS execution.
- Browser automation.
- Cookies, credentials, auth.
- Private or authenticated URLs.
- The Slimy public site, the Habitat UI, or any NUC-internal service.
- Package install.
- Model calls.
- Citation synthesis.
- Report writing.

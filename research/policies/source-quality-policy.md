# Source Quality Policy

## Purpose

This policy governs how sources are identified, evaluated, fetched, and recorded
during research execution in the Research Farm.

## Allowed Source Types

| Source Type | Trust Level | Notes |
|------------|-------------|-------|
| Official documentation | High | Vendor docs, RFCs, W3C specs, language docs |
| Peer-reviewed papers | High | DOI-linked, PubMed, arXiv (pre-print noted) |
| GitHub repositories | Medium | Source code, README, issues, discussions |
| Technical blogs (known authors) | Medium | Posts by recognized practitioners |
| Stack Overflow answers | Medium | Must include accepted answer context |
| Official announcements | High | Vendor blog posts, changelogs, release notes |
| Package registries | Medium | npm, PyPI, crates.io metadata |
| Wikipedia | Low-Medium | Good for overview, must be corroborated |
| Community forums | Low | Reddit, Discourse, etc. (see below) |

## Disallowed Source Types

| Source Type | Reason |
|------------|--------|
| Paywalled content (not accessible) | Cannot verify or cite accurately |
| Content behind authentication | Ethical and legal concerns |
| AI-generated content without disclosure | Cannot verify originality |
| Social media posts (non-official) | Ephemeral, unreliable |
| Content farms / SEO spam | Low quality, unreliable |
| Pirated / illegally hosted content | Legal risk |

## Handling Specific Source Types

### Paywalls

- Do NOT attempt to bypass paywalls
- Note that the source is paywalled in the source record
- If a free abstract/summary is available, cite that with a paywall note
- Do NOT use content that was accessed through credential sharing

### Reddit / Forum Content

- Treat as low-trust community opinion
- Must be corroborated by at least one higher-trust source
- Note the forum context and thread age
- Do NOT cite deleted or removed content
- Do NOT scrape private subreddits or authenticated forums

### Official Documentation

- Preferred source type for technical claims
- Record the specific version/date of the documentation
- Note if documentation appears outdated
- If conflicting versions exist, cite the most recent

### Conflicting Sources

- Record ALL conflicting sources, do not cherry-pick
- Note the conflict explicitly in source notes
- If one source is more recent, note the recency advantage
- If one source is more authoritative, note the authority difference
- The final report must acknowledge conflicting information

### Recency Requirements

- Always record the publication or last-updated date of a source
- For rapidly evolving topics (e.g., AI tooling), prefer sources from the last 6 months
- For stable topics (e.g., algorithms, protocols), older sources are acceptable
- If no date is available, note "date unknown" and treat as lower trust
- Record the fetched_at timestamp separately from the source's own date

### Source Timestamps

Every source record MUST include:

- `fetched_at` - ISO 8601 timestamp when the source was fetched
- `published_at` - ISO 8601 timestamp when the source was published (or null if unknown)
- `last_modified_at` - ISO 8601 timestamp of last modification (or null if unknown)

These timestamps are immutable once recorded.

## Avoiding Invented Citations

1. NEVER cite a source that was not actually fetched and saved
2. NEVER invent URLs, titles, or author names
3. NEVER paraphrase a source so heavily that the original cannot be verified
4. If a source cannot be found, note "source not found" rather than fabricating
5. Every citation in the final report must point to a saved source record
6. Source records must be saved BEFORE citations reference them
7. The validator must check that all citations point to existing source records

## Source Record Schema

See `research/templates/source-record.schema.json` for the full JSON schema.

Required fields:

- `source_id` - unique identifier
- `url` - original URL (or null for offline sources)
- `title` - source title
- `source_type` - one of the allowed types above
- `trust_level` - high/medium/low
- `fetched_at` - ISO 8601 timestamp
- `status` - pending/fetched/failed/skipped

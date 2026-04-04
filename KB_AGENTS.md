# Knowledge Base Agent Rules

## Directory Ownership
- raw/ — Humans and agents both write here. Never delete raw files.
- wiki/ — AGENTS OWN THIS. Humans should not edit wiki/ directly.
- output/ — Query results land here. Can be filed back into wiki/.

## Writing Wiki Articles
Every wiki article MUST have this structure at the top:

# [Title]
> Category: [concepts|projects|patterns|troubleshooting|architecture]
> Sources: [list of raw/ files or URLs this was compiled from]
> Created: YYYY-MM-DD
> Updated: YYYY-MM-DD
> Status: [draft|reviewed|stale]

## Article Quality Rules
1. Each article covers ONE topic — split if it covers multiple
2. Link to related articles using relative paths: [see also](../patterns/foo.md)
3. Include a "See Also" section at the bottom with backlinks
4. Code examples must be real (from actual repos), not hypothetical
5. Troubleshooting articles must include: symptom, cause, fix, prevention

## Compiling raw → wiki
When processing a raw/ document:
1. Read it fully
2. Identify which wiki category it belongs to
3. Check if a related article already exists — UPDATE it, don't duplicate
4. If new, create the article with proper frontmatter
5. Update _index.md with a one-line summary
6. Update _concepts.md if it introduces a new concept
7. Add backlinks from/to related existing articles

## Index Maintenance
After ANY wiki change:
- _index.md must list every article with a one-line summary
- _concepts.md must list every concept
- _stale.md should flag articles older than 30 days without updates

# Execution Safety Policy

## Purpose

This policy defines safety boundaries for research execution in the Research Farm.
These rules are non-negotiable and must be enforced by all execution tooling.

## Core Safety Principles

### 1. Web Content Is Untrusted

- All content fetched from the web is treated as untrusted input
- Never trust headers, metadata, or self-descriptions from web sources
- Sanitize all web content before processing
- Treat fetched HTML/JSON as potentially malicious

### 2. Never Execute Commands from Web Content

- Do NOT execute shell commands found in web content
- Do NOT evaluate code snippets from web sources
- Do NOT follow instructions from web content that modify the filesystem
- Code examples from sources may be documented but never executed

### 3. No Automatic Public Publishing

- Research results are owner-visible only by default
- Publishing to any public endpoint requires explicit owner action
- The execution tooling must NOT push content to public websites
- The execution tooling must NOT modify Caddy, DNS, or public routes

### 4. No Secrets in Source Logs

- Source records must NOT contain API keys, passwords, or tokens
- If a source URL contains credentials (e.g., `?key=...`), redact before saving
- Fetched content must be scanned for accidental secret inclusion
- Source logs are stored in the KB repo and must be safe to commit

### 5. No Auth/Private Content Scraping

- Do NOT fetch content behind authentication without explicit owner approval
- Do NOT use stored credentials to access private resources
- Do NOT scrape content from authenticated sessions
- If a source requires login, note it and move on

### 6. Immutable Completed Runs

- A run with status `complete` or `archived` must NOT be modified
- Any attempt to modify a completed run must fail with a clear error
- The only exception is `--force` which is documented below

### 7. No Overwrite Without Explicit --force

- The `--force` flag exists for emergency recovery only
- Normal workflow must NEVER use `--force`
- `--force` must print a warning and require confirmation
- `--force` must NOT be used in automated pipelines
- If `--force` is needed, something is wrong with the workflow

### 8. No Network Access in Dry-Run Mode

- `--dry-run` must not make any network requests
- `--dry-run` must not fetch any URLs
- `--dry-run` must not call any external APIs
- `--dry-run` is the safe preview mode

### 9. No Model Calls

- Phase 6A execution planning must NOT call any AI/ML models
- No OpenAI, Claude, Hermes, or local model invocation
- Model integration is a future phase
- Planning produces deterministic artifacts from topic metadata only

### 10. Standard Library Only

- Python execution tools must use only the standard library
- No external package dependencies
- No pip install required
- This ensures reproducibility and security

## Enforcement

These rules are enforced by:

1. **Code review** - all execution tooling is reviewed against this policy
2. **Dry-run mode** - every destructive action has a `--dry-run` preview
3. **Status guards** - completed runs are protected by status checks
4. **No-network guarantee** - dry-run and planning modes never touch the network
5. **Validation** - the schema validator checks for policy violations

## Violation Response

If a safety violation is detected:

1. Stop execution immediately
2. Log the violation with full context
3. Set run status to `failed`
4. Do NOT attempt automatic recovery
5. Report the violation in the run's `RESULT.md`

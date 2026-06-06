# Citation Policy

## Purpose

This policy governs how claims in research reports are attributed to sources,
ensuring traceability, honesty, and verifiability.

## Core Rules

### 1. Every Major Claim Needs a Source

- Any factual assertion that is not common knowledge must be cited
- Quantitative claims (numbers, statistics, benchmarks) always require citation
- Qualitative claims ("X is widely considered...") require at least one source
- The author's own analysis or recommendations do not need citation but must
  be clearly labeled as such

### 2. Citations Point to Saved Source Records

- Every citation must reference a `source_id` from a saved source record
- The source record must exist in the run's `sources.jsonl` BEFORE the citation
  references it
- Citations use the format `[source:<source_id>]` in markdown
- Multiple sources for a single claim are encouraged

### 3. No Citation May Point to a Source That Was Not Saved

- This is the golden rule of the citation system
- If a source was consulted but not saved, it cannot be cited
- If a source was found but not fetched, it cannot be cited
- If a source was mentioned by another source but not directly verified, cite
  the intermediate source with a "as cited by" note

### 4. Uncertain Claims Must Be Labeled

- Claims with weak or conflicting evidence must include a confidence qualifier:
  - `[uncertain]` - evidence exists but is weak or contradictory
  - `[disputed]` - multiple sources disagree
  - `[unverified]` - claim appears in sources but could not be independently confirmed
  - `[estimated]` - derived from other data, not directly stated
- Uncertain claims should still cite their sources
- The final report should include a "Confidence Assessment" section

### 5. Source Quotes Must Be Short

- Direct quotes should be under 200 words
- Longer passages should be paraphrased with a citation to the original
- Quotes must be verbatim -- no silent edits
- Use `[sic]` if the original contains an error
- Quote marks must always be used for direct quotes

### 6. Separate Facts from Recommendations

- The final report must clearly separate:
  - **Findings** (sourced facts) - under "Findings" headings
  - **Analysis** (interpreted facts) - under "Analysis" headings
  - **Recommendations** (author opinion) - under "Recommendations" headings
- Each section type has different citation requirements:
  - Findings: mandatory citation
  - Analysis: citation encouraged, interpretation labeled
  - Recommendations: no citation required, must be labeled as opinion

## Citation Record Schema

See `research/templates/citation-record.schema.json` for the full JSON schema.

Required fields:

- `citation_id` - unique identifier
- `source_id` - references a saved source record
- `claim_text` - the text being cited (short quote or paraphrase)
- `claim_type` - fact/analysis/recommendation
- `confidence` - high/medium/low/uncertain/disputed/unverified/estimated
- `location_in_report` - section or paragraph reference

## Citation Workflow

1. Fetch and save source -> create source record with `source_id`
2. Read source and extract relevant claims
3. Create citation record linking claim to `source_id`
4. Write claim in report with `[source:<source_id>]` reference
5. For uncertain claims, add appropriate qualifier
6. Final review: verify every citation points to an existing source record

## Validation

The validator should check:

- All `source_id` values in citations exist in `sources.jsonl`
- No citation references a source with `status: pending` or `status: failed`
- All major claims in the report have at least one citation
- Uncertain claims are properly labeled
- Quotes are under 200 words

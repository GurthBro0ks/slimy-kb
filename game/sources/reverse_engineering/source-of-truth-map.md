# Source-of-Truth Map

Generated: 2026-04-26

## Purpose

This map defines what can and cannot be used as evidence after the `/tmp` import. It deliberately separates private raw evidence, reproducible derived outputs, interpreted reports, and quarantined material.

## Tier Definitions

### Tier 0 — raw originals / private evidence

Raw files copied from a device/APK/capture source or prior proof originals. These may be source-of-truth candidates only if the acquisition path and SHA256 are recorded. They stay ignored/private and are never committed.

### Tier 1 — derived reproducible outputs

Decoded text/Lua, protocol lists, substitution tables, and tooling outputs that can be regenerated from Tier 0 inputs using a named script and recorded hashes. Current imported outputs are not fully promoted until re-derived under the harness.

### Tier 2 — interpreted reports / hypotheses

Markdown specs, solve logs, summary reports, and model/tool interpretations. Useful for research direction, but not proof of exact original strings unless they cite a verified Tier 0 input and reproducible derivation.

### Tier X — suspect / quarantined / never source-of-truth

Scripts or files that rewrite originals, force mappings, normalize strings without proof, contain prior proof metadata needing review, or were copied into quarantine. These are reference material only.

## Tier 0 — Raw Originals / Private Evidence

All current Tier 0 items are **candidates**, not final truth, because multiple hashes exist for the same logical files.

| File | Status |
|---|---|
| `originals/tmp-imports/20260426T173840Z/list.luac` | Private raw candidate; hash `d90d8974...` |
| `originals/tmp-imports/20260426T173840Z/list__sha256_122b7769.luac` | Private raw candidate; conflicting `list` hash |
| `originals/tmp-imports/20260426T173840Z/list__sha256_d90d8974.luac` | Duplicate raw candidate of `list.luac` |
| `originals/tmp-imports/20260426T173840Z/msg_arena_top_query.luac` | Private raw candidate; hash `5f552569...` |
| `originals/tmp-imports/20260426T173840Z/msg_arena_top_query__sha256_5f552569.luac` | Duplicate raw candidate of `msg_arena_top_query.luac` |
| `originals/tmp-imports/20260426T173840Z/msg_arena_top_query__sha256_8cec7aed.luac` | Private raw candidate; conflicting arena handler hash |
| `originals/tmp-imports/20260426T173840Z/msg_group_rank.luac` | Private raw candidate; hash `dc73a3f7...` |
| `originals/tmp-imports/20260426T173840Z/msg_group_rank__sha256_a3224769.luac` | Private raw candidate; conflicting group-rank handler hash |
| `originals/tmp-imports/20260426T173840Z/msg_group_rank__sha256_dc73a3f7.luac` | Duplicate raw candidate of `msg_group_rank.luac` |

## Tier 1 — Derived Reproducible Outputs

These are eligible to become Tier 1 after re-derivation from confirmed Tier 0 originals. For now, treat them as **Tier 1 candidates with Tier 2 caveats**.

| File | Current use |
|---|---|
| `data/protocol/decoded/all_protocol_messages.txt` | Candidate protocol-message list; exactness unproven |
| `data/protocol/decoded/all_protocol_messages_v2.txt` | Candidate normalized v2 protocol-message list |
| `data/protocol/decoded/all_protocol_messages_v2__sha256_1e7cd122.txt` | Duplicate/provenance copy of v2 message list |
| `data/protocol/decoded/list_clean_decoded.lua` | Candidate decoded Lua output; re-derive before use |
| `data/protocol/decoded/list_clean_decoded_v2.lua` | Candidate normalized decoded Lua output |
| `data/protocol/decoded/list_clean_decoded_v2__sha256_e96bf0bb.lua` | Duplicate/provenance copy of normalized decoded Lua output |
| `data/protocol/decoded/protocol_messages.txt` | Candidate protocol-message list with unclear provenance |
| `data/protocol/substitution-tables/substitution_table.txt` | Early substitution-table candidate |
| `data/protocol/substitution-tables/substitution_table_candidate.txt` | Candidate proof-output substitution table; review first |
| `data/protocol/substitution-tables/substitution_table_v2.txt` | Later forced/normalized mapping candidate |
| `data/protocol/substitution-tables/substitution_table_v2__sha256_3e635e70.txt` | Duplicate/provenance copy of v2 table |
| `scripts/imported-tools/align_manual.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/analyze.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/analyze_punct.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/check_I.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/check_chars.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/check_rare.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/check_t.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/decode.py` | Tool candidate; verify read-only behavior before use |
| `scripts/imported-tools/decode_handlers.py` | Tool candidate; verify read-only behavior before use |
| `scripts/imported-tools/exact_align.py` | Tool candidate; verify assumptions before use |
| `scripts/imported-tools/find_unmapped.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/list_decoded_candidate.lua` | Derived candidate output stored with tools; should be relocated/reclassified later |
| `scripts/imported-tools/list_fully_decoded.lua` | Derived candidate output stored with tools; should be relocated/reclassified later |
| `scripts/imported-tools/manual_align.py` | Tool candidate; verify before trusted use |
| `scripts/imported-tools/msg_arena_top_query.lua` | Derived handler candidate output; not raw truth |
| `scripts/imported-tools/msg_arena_top_query.luac.decoded_candidate.lua` | Derived handler candidate output; not raw truth |
| `scripts/imported-tools/msg_group_rank.lua` | Derived handler candidate output; not raw truth |
| `scripts/imported-tools/msg_group_rank.luac.decoded_candidate.lua` | Derived handler candidate output; not raw truth |
| `scripts/imported-tools/plan.py` | Tool/planning candidate; verify before use |
| `scripts/imported-tools/plan__sha256_165d3e53.py` | Duplicate/provenance copy of `plan.py` |
| `scripts/imported-tools/solve_cipher.py` | Tool candidate; verify assumptions before use |
| `scripts/imported-tools/test_decode.lua` | Test fixture/output candidate; verify provenance |
| `scripts/imported-tools/test_list.py` | Tool candidate; verify before use |

## Tier 2 — Interpreted Reports / Hypotheses

These files can guide analysis, but they are not source-of-truth for exact protocol strings.

| File | Status |
|---|---|
| `docs/protocol/PROTOCOL_SPEC.md` | Report-only candidate; exactness unproven |
| `docs/protocol/PROTOCOL_SPEC_v2.md` | Normalized/report-only candidate |
| `docs/protocol/PROTOCOL_SPEC_v2__sha256_b8414a97.md` | Duplicate/provenance copy of v2 spec |
| `docs/protocol/cipher_solve_log.txt` | Report-only solve log tied to suspect workflow |
| `docs/protocol/cipher_solve_log__sha256_9e924c94.txt` | Duplicate/provenance copy of solve log |
| `docs/protocol/protocol_spec_candidate.md` | Candidate report from prior proof output |
| `reports/tmp-import-20260426T173840Z.md` | Import report; safe project metadata |
| `evidence/tmp-imports/20260426T173840Z/MANIFEST.md` | Import manifest; safe project metadata |
| `evidence/tmp-imports/20260426T173840Z/MANIFEST.tsv` | Import manifest; safe project metadata |
| `evidence/tmp-imports/20260426T173840Z/source-tree.txt` | Import source-tree metadata |
| `evidence/tmp-imports/20260426T173840Z/skipped.txt` | Import skipped-file metadata |

## Tier X — Suspect / Quarantined / Never Source-of-Truth

| File or group | Reason |
|---|---|
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/align_dp.py` | Forces mapping conflict decisions and writes a substitution table |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/decrypt.py` | Writes decoded outputs without harness proof metadata |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/decrypt_all.py` | Writes decoded outputs without harness proof metadata |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/dump_clean.py` | Produces intermediate `/tmp` files without proof metadata |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/final_solve.py` | Rewrites `.luac` files and normalizes protocol names |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/final_solve__sha256_4e57b2ae.py` | Duplicate of `final_solve.py` |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/full_decode.py` | Writes decoded Lua from `/tmp/list.luac` without proof metadata |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/generate_specs.py` | Generates protocol reports from decoded output without exact input chain |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/solve_and_rewrite.py` | Rewrites handler `.luac` files to match guessed ground truth |
| `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/solve_and_rewrite__sha256_fe4cd520.py` | Duplicate of `solve_and_rewrite.py` |
| `quarantine/tmp-imports/20260426T173840Z/unknown-review/*` | Prior proof metadata, ADB logs, diffs, reports, and candidate outputs requiring separate review |

## Operational Rules From This Map

- Do not decode from current imported `.luac` files until fresh acquisition or hash confirmation settles the conflicts.
- Do not use v2 protocol outputs as exact strings; treat them as normalized hypotheses.
- Do not run anything from `quarantine/`.
- Do not promote any `scripts/imported-tools/` script until it is reviewed for read-only behavior and deterministic output paths.
- Do not commit anything under `originals/`, `quarantine/`, `captures/`, or raw artifact extensions.

## Recommended Next Step

**Reacquire fresh originals from device/APK and compare hashes.** Once the Tier 0 hashes are settled, the next technical step should be a clean decoder test harness that reads confirmed originals read-only and writes new proof-backed Tier 1 outputs.

## Clear Answer

The current source-of-truth stack is: private `.luac` files are only Tier 0 candidates, decoded/protocol outputs are not yet trusted Tier 1, docs are Tier 2 hypotheses, and quarantined rewrite/normalization material is Tier X.

## Confidence Level

0.90

## Key Caveats

- Same-name raw files have conflicting sizes and SHA256 values.
- Some useful derived Lua files are currently parked under `scripts/imported-tools/`; they should be reclassified after provenance review.
- This map does not validate protocol correctness; it only defines trust boundaries for the next evidence step.

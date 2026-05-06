# Evidence Inventory Report

Generated: 2026-04-26

## Scope

- **Import folder:** `evidence/tmp-imports/20260426T173840Z/`
- **Import manifest:** `evidence/tmp-imports/20260426T173840Z/MANIFEST.tsv`
- **Import proof folder:** `.harness/proofs/proof_20260426T173927Z`
- **Latest known QA proof path:** `.harness/proofs/proof_20260426T174045Z`
- **Import report:** `reports/tmp-import-20260426T173840Z.md`

This ledger classifies the imported `/tmp` files without decoding, rewriting, normalizing, or moving raw evidence.

## Counts By Class

| Class | Count | Location | Trust status |
|---|---:|---|---|
| Raw `.luac` evidence | 9 | `originals/tmp-imports/20260426T173840Z/` | Private Tier 0 candidates; ignored by git; hash conflicts require reacquisition/confirmation |
| Suspect scripts | 10 | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/` | Tier X; do not run |
| Unknown/prior proof metadata | 31 | `quarantine/tmp-imports/20260426T173840Z/unknown-review/` | Tier X until reviewed |
| Safe imported scripts/tools | 23 | `scripts/imported-tools/` | Tool candidates only; verify before promoting |
| Decoded outputs | 7 | `data/protocol/decoded/` | Tier 1/Tier 2 candidates; hypothesis until re-derived |
| Substitution tables | 4 | `data/protocol/substitution-tables/` | Candidate decoder inputs; not source-of-truth |
| Protocol docs | 6 | `docs/protocol/` | Report-only/hypothesis unless exact provenance is proven |

## Raw `.luac` Originals

| Filename | Path | Size | SHA256 | Read-only status | Evidence tier | Trust status |
|---|---|---:|---|---|---|---|
| `list.luac` | `originals/tmp-imports/20260426T173840Z/list.luac` | 32554 | `d90d8974a1574b0b0f25285e853b06dfe62fee800b0e392f289680583f733664` | `444` / `-r--r--r--` | Tier 0 candidate | Private raw evidence candidate; same hash as `list__sha256_d90d8974.luac`; conflicts with `list__sha256_122b7769.luac` |
| `list__sha256_122b7769.luac` | `originals/tmp-imports/20260426T173840Z/list__sha256_122b7769.luac` | 32597 | `122b776932fdb0e5c85b201d72aa722267b5b13162394e4610199b1235ac6f67` | `444` / `-r--r--r--` | Tier 0 candidate | Private raw evidence candidate from prior proof originals; conflicts with `d90d8974` list variant |
| `list__sha256_d90d8974.luac` | `originals/tmp-imports/20260426T173840Z/list__sha256_d90d8974.luac` | 32554 | `d90d8974a1574b0b0f25285e853b06dfe62fee800b0e392f289680583f733664` | `444` / `-r--r--r--` | Tier 0 candidate | Duplicate hash of `list.luac`; keep private, do not treat duplicate as independent proof |
| `msg_arena_top_query.luac` | `originals/tmp-imports/20260426T173840Z/msg_arena_top_query.luac` | 114 | `5f552569a41be804d91893321ebb0f465463cf0fdc224bd74b0b8704bbd9bcf8` | `444` / `-r--r--r--` | Tier 0 candidate | Private raw evidence candidate; same hash as `msg_arena_top_query__sha256_5f552569.luac`; conflicts with `8cec7aed` variant |
| `msg_arena_top_query__sha256_5f552569.luac` | `originals/tmp-imports/20260426T173840Z/msg_arena_top_query__sha256_5f552569.luac` | 114 | `5f552569a41be804d91893321ebb0f465463cf0fdc224bd74b0b8704bbd9bcf8` | `444` / `-r--r--r--` | Tier 0 candidate | Duplicate hash of `msg_arena_top_query.luac`; keep private |
| `msg_arena_top_query__sha256_8cec7aed.luac` | `originals/tmp-imports/20260426T173840Z/msg_arena_top_query__sha256_8cec7aed.luac` | 214 | `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37` | `444` / `-r--r--r--` | Tier 0 candidate | Private raw evidence candidate from prior proof originals; conflicts with `5f552569` variant |
| `msg_group_rank.luac` | `originals/tmp-imports/20260426T173840Z/msg_group_rank.luac` | 123 | `dc73a3f768b7d2bcc86d5dc4b7a4be0b7878dc3374f31fc9ca84a7f35e708646` | `444` / `-r--r--r--` | Tier 0 candidate | Private raw evidence candidate; same hash as `msg_group_rank__sha256_dc73a3f7.luac`; conflicts with `a3224769` variant |
| `msg_group_rank__sha256_a3224769.luac` | `originals/tmp-imports/20260426T173840Z/msg_group_rank__sha256_a3224769.luac` | 173 | `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9` | `444` / `-r--r--r--` | Tier 0 candidate | Private raw evidence candidate from prior proof originals; conflicts with `dc73a3f7` variant |
| `msg_group_rank__sha256_dc73a3f7.luac` | `originals/tmp-imports/20260426T173840Z/msg_group_rank__sha256_dc73a3f7.luac` | 123 | `dc73a3f768b7d2bcc86d5dc4b7a4be0b7878dc3374f31fc9ca84a7f35e708646` | `444` / `-r--r--r--` | Tier 0 candidate | Duplicate hash of `msg_group_rank.luac`; keep private |

## Decoded Outputs

| Filename | Path | SHA256 | Likely input dependency | Exact vs normalized status | Trust caveat |
|---|---|---|---|---|---|
| `all_protocol_messages.txt` | `data/protocol/decoded/all_protocol_messages.txt` | `5e9bb781bcab246c7561002d3102ecb9399a89ddc1d48919f2f2c4a1bf61fadf` | Likely `list_clean_decoded.lua` and `generate_specs.py` | Unknown/candidate | Hypothesis until regenerated from confirmed originals with script provenance |
| `all_protocol_messages_v2.txt` | `data/protocol/decoded/all_protocol_messages_v2.txt` | `1e7cd12256c897f191243f46fff8340ff51fed07b5b8bdef6ade5a488de83080` | Likely `list_clean_decoded_v2.lua` and `final_solve.py` | Normalized/candidate | Generated after punctuation normalization per quarantined script comments; not exact truth |
| `all_protocol_messages_v2__sha256_1e7cd122.txt` | `data/protocol/decoded/all_protocol_messages_v2__sha256_1e7cd122.txt` | `1e7cd12256c897f191243f46fff8340ff51fed07b5b8bdef6ade5a488de83080` | Duplicate of `all_protocol_messages_v2.txt` | Normalized/candidate | Duplicate hash; keep only as provenance marker |
| `list_clean_decoded.lua` | `data/protocol/decoded/list_clean_decoded.lua` | `1ac78ef6ebed747ff0656595931e4b3127716a9f146078e3dc3a14ef4a73db09` | Likely `/tmp/list.luac` plus substitution table | Unknown/candidate | Derived output imported from `/tmp`; re-run from confirmed Tier 0 input before use |
| `list_clean_decoded_v2.lua` | `data/protocol/decoded/list_clean_decoded_v2.lua` | `e96bf0bbb58c2d3ff2b100761409679b6a3b0e957717dc086f8d9c0e558cb2e7` | Likely `list_clean_decoded.lua` plus `final_solve.py` cleanup | Normalized/candidate | Quarantined script says punctuation was normalized and `list.luac` was rewritten; hypothesis only |
| `list_clean_decoded_v2__sha256_e96bf0bb.lua` | `data/protocol/decoded/list_clean_decoded_v2__sha256_e96bf0bb.lua` | `e96bf0bbb58c2d3ff2b100761409679b6a3b0e957717dc086f8d9c0e558cb2e7` | Duplicate of `list_clean_decoded_v2.lua` | Normalized/candidate | Duplicate hash; not independent evidence |
| `protocol_messages.txt` | `data/protocol/decoded/protocol_messages.txt` | `c12f6adec7172b04b8ca8a9a8b3565639024ad8baf5ea4c8536ba7e814a84eb2` | Imported directly from `/tmp` | Unknown/candidate | No clean provenance yet; compare against v1/v2 outputs after re-derivation |

## Substitution Tables

| Filename | Path | SHA256 | Version/order recommendation |
|---|---|---|---|
| `substitution_table.txt` | `data/protocol/substitution-tables/substitution_table.txt` | `3a37f68d5a0f3381fa9cdac6aeba20a749f9051a5eb3c15b6eb7fbc67b70664d` | Treat as early baseline only; do not use as source-of-truth |
| `substitution_table_candidate.txt` | `data/protocol/substitution-tables/substitution_table_candidate.txt` | `ec8bf933007f24e8dbd7202808193f413debec1960c7fe9cb967f6a9ab337d38` | Best candidate to review first because it came from prior proof output, but still re-derive before trusting |
| `substitution_table_v2.txt` | `data/protocol/substitution-tables/substitution_table_v2.txt` | `3e635e709e0516b4b9fd2d2daf17b9a5ae1935afa968a30f34bd0d2cde196989` | Later/forced mapping candidate; compare after fresh decode, do not trust alone |
| `substitution_table_v2__sha256_3e635e70.txt` | `data/protocol/substitution-tables/substitution_table_v2__sha256_3e635e70.txt` | `3e635e709e0516b4b9fd2d2daf17b9a5ae1935afa968a30f34bd0d2cde196989` | Duplicate of `substitution_table_v2.txt`; provenance marker only |

## Protocol Docs

| Filename | Path | SHA256 | Exact / normalized / report-only |
|---|---|---|---|
| `PROTOCOL_SPEC.md` | `docs/protocol/PROTOCOL_SPEC.md` | `1946d0f9c3e8bbe99728ac7cc71ab717f0bd32ea2e18fea4b7dd0ec2ab1496d8` | Report-only candidate; exactness unproven |
| `PROTOCOL_SPEC_v2.md` | `docs/protocol/PROTOCOL_SPEC_v2.md` | `b8414a974881830c27d9475b78d0b3293350b1de2bb12911601523a140d71f36` | Normalized/report-only candidate |
| `PROTOCOL_SPEC_v2__sha256_b8414a97.md` | `docs/protocol/PROTOCOL_SPEC_v2__sha256_b8414a97.md` | `b8414a974881830c27d9475b78d0b3293350b1de2bb12911601523a140d71f36` | Duplicate of `PROTOCOL_SPEC_v2.md`; report-only |
| `cipher_solve_log.txt` | `docs/protocol/cipher_solve_log.txt` | `9e924c9495ed7baebb86030bc1831b54d35f25996ced458f02f236be9df291c6` | Report-only; describes a suspect/normalized solve path |
| `cipher_solve_log__sha256_9e924c94.txt` | `docs/protocol/cipher_solve_log__sha256_9e924c94.txt` | `9e924c9495ed7baebb86030bc1831b54d35f25996ced458f02f236be9df291c6` | Duplicate of `cipher_solve_log.txt`; report-only |
| `protocol_spec_candidate.md` | `docs/protocol/protocol_spec_candidate.md` | `bd6510192bcf6fdf41c0ec01caca98417ccb1a958e183b742defb5617d2eb14e` | Candidate report from prior proof output; exactness unproven |

## Suspect / Quarantined Scripts

| Filename | Path | Reason quarantined | Risk | Reuse recommendation |
|---|---|---|---|---|
| `align_dp.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/align_dp.py` | Forces mapping conflicts in favor of ground truth and writes `/tmp/substitution_table_v2.txt` | Can bake assumptions into decoder table | Do not reuse directly; mine logic only after review |
| `decrypt.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/decrypt.py` | Writes decoded output next to input by default | Could overwrite or create ambiguous derived files | Rebuild as read-only decoder if needed |
| `decrypt_all.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/decrypt_all.py` | Writes decoded output next to input by default | Same provenance/overwrite risk as `decrypt.py` | Rebuild as read-only decoder if needed |
| `dump_clean.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/dump_clean.py` | Reads `/tmp/*.luac` and writes `/tmp/clean_*.txt` | Produces intermediate files without proof metadata | Do not reuse directly |
| `final_solve.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/final_solve.py` | Explicitly rewrites `/tmp/list.luac`, handler `.luac` files, substitution table, decoded Lua, and protocol specs | High; mutates original-looking evidence and normalizes names | Never use as evidence; use only as a red-flag reference |
| `final_solve__sha256_4e57b2ae.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/final_solve__sha256_4e57b2ae.py` | Duplicate of `final_solve.py` | Same high mutation risk | Never use as evidence |
| `full_decode.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/full_decode.py` | Reads `/tmp/list.luac` and writes `/tmp/list_clean_decoded.lua` without proof metadata | Can create derived output detached from exact input hash | Do not reuse directly |
| `generate_specs.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/generate_specs.py` | Reads decoded Lua and writes protocol message/spec files under `/tmp` | Report generation without exact input chain | Rebuild as deterministic report tool if needed |
| `solve_and_rewrite.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/solve_and_rewrite.py` | Explicitly rewrites handler `.luac` files to match guessed ground truth | High; creates fake originals | Never reuse |
| `solve_and_rewrite__sha256_fe4cd520.py` | `quarantine/tmp-imports/20260426T173840Z/suspect-scripts/solve_and_rewrite__sha256_fe4cd520.py` | Duplicate of `solve_and_rewrite.py` | Same high fake-original risk | Never reuse |

## GitHub Safety Verification

Commands run:

```bash
git status --short
git ls-files | grep -Ei '\.(luac|apk|xapk|apks|aab|so|pcap|pcapng|flow|har)$' || true
git ls-files | grep -E '(^|/)originals/|(^|/)quarantine/|(^|/)captures/|(^|/)\.env' || true
```

Result:

- No tracked raw `.luac`, APK/XAPK/APKS/AAB, `.so`, capture, flow, or HAR files were found.
- Initial tracked-path check found only `evidence/originals/.gitkeep` and `evidence/quarantine/.gitkeep`; these were safe placeholders, not raw evidence, and were removed from tracking with targeted `git rm`.
- Re-run the tracked-path checks before sync; expected output is empty.

## Recommended Next Step

**Reacquire fresh originals from device/APK and compare hashes.** The current import contains conflicting hashes for the same logical `.luac` filenames, so fresh Tier 0 confirmation should happen before any new decode or protocol-map work.

## Clear Answer

The imported workspace now has a proof-backed ledger: raw `.luac` files are private Tier 0 candidates, decoded/protocol outputs are hypotheses until re-derived, substitution tables are candidate decoder inputs only, and the rewrite/mutation scripts are Tier X.

## Confidence Level

0.90

## Key Caveats

- Hash conflicts across same-name `.luac` files mean no single imported original should be treated as final truth yet.
- The v2 decoded/protocol outputs appear tied to normalization and/or rewrite workflows.
- Quarantined unknown-review files were counted but not promoted; they need separate review before evidence use.

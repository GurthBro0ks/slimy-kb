# Project Status

## Current operating status

The repo is live at:

```text
https://github.com/GurthBro0ks/slimy_snail
```

Current branch:

```text
main
```

The Phase 2 protocol/source-reconstruction branch has gone far enough for the next project goal. Phase 2W left two grammar fragments eligible for external-only punctuation-aware trials, but that work is now a side branch, not the default next task.

## Active upstream task

Phase 3/4 should pivot to wire-level evidence:

1. Prepare a safe capture workflow for owned account/device traffic.
2. Capture auth and transport behavior without committing raw captures or secrets.
3. Correlate captured messages with Phase 2C protocol names and Phase 2G rank/group field-flow evidence.
4. Build an API-client scaffold only after auth, transport, and replay constraints are proven.

Phase 3 prep has been completed once with no live capture started:

```text
/tmp/proof_snail_phase3_capture_prep_20260427T205158Z
```

Result:

- `PASS_PHASE3_CAPTURE_PREP_READY`
- serial: `emulator-5554`
- package: `com.qcplay.snail.android.na`
- app PID: `7211`
- raw capture started: `false`

First controlled live capture completed:

```text
captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap
```

This raw PCAP is ignored/private and was not committed. Sanitized report:

```text
reports/phase3-passive-startup-capture-20260427T213957Z.md
```

Result:

- passive startup capture only
- app force-stop/start used to generate startup traffic
- `3245` packets captured
- `0` kernel drops
- candidate remote service ports observed: TCP/443, TCP/80, UDP/443, UDP/53, low-volume TCP/3000
- no packet payloads, auth headers, cookies, tokens, account IDs, or device IDs committed
- no Phase 2 protocol correlation yet

## Do not import or commit

Do not import or commit:

* `.luac`
* `.apk`
* `.xapk`
* `.so`
* `.flow`
* `.pcap`
* `.pcapng`
* `.har`
* account/session/token files
* headers, cookies, auth blobs, device IDs, or account identifiers
* contaminated v2 protocol outputs
* rewritten handler files

## Next expected action

Generate and run a Phase 3 capture-prep prompt that:

1. Checks emulator/ADB state.
2. If the emulator is not running, starts the `snail-recon` AVD, waits for boot, launches `com.qcplay.snail.android.na`, and confirms PID plus top activity before continuing.
3. Inventories installed app/runtime status.
4. Builds ignored capture directories and sanitized report templates.
5. Verifies `.gitignore` and `git_auto_sync.sh` block captures/secrets.
6. Cleans working-tree noise by ignoring or removing generated decoded protocol files, stale proof `qa.log` files, and tmp-import scratch manifests only when they are duplicated or explicitly non-source-of-truth.
7. Produces a no-secrets capture runbook for mitmproxy/Frida or equivalent tooling.
8. Runs `./scripts/qa_gate.sh` before any GitHub sync.

## 2026-04-26 - Evidence reset imported

The clean evidence reset completed with:

```text
PASS_CLEAN_ORIGINALS_READY
```

Original proof dir from the handoff:

```text
/tmp/proof_snail_protocol_reset_20260426T170226Z
```

That `/tmp` directory was not present during this repo update, so the safe Markdown report copies were reviewed and promoted from the ignored import review area:

```text
quarantine/tmp-imports/20260426T173840Z/unknown-review/
```

Safe reports were imported under:

```text
docs/reports/proof_snail_protocol_reset_20260426T170226Z/
```

Current cipher status:

- incomplete
- unmapped alphanumerics: `6`, `H`, `S`, `b`, `d`, `r`
- punctuation unresolved
- 962 quoted protocol strings
- 48 exact/trusted-character strings
- 914 unresolved/symbol-corrupted strings

Next action:

Run Phase 2B cipher audit/solve from read-only originals once the external proof originals are available.

## 2026-04-26 - Phase 2B originals restored and audit run

`adb devices` returned no attached devices, so fresh reacquisition was blocked.

External originals were restored from ignored private local clean-size variants into:

```text
/tmp/proof_snail_protocol_reset_20260426T195515Z_restored
```

Read-only original hashes:

- `list.luac`: `122b776932fdb0e5c85b201d72aa722267b5b13162394e4610199b1235ac6f67`
- `msg_group_rank.luac`: `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9`
- `msg_arena_top_query.luac`: `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37`

Phase 2B audit proof:

```text
/tmp/proof_snail_phase2b_cipher_audit_20260426T195523Z
```

Result:

- audit-only pass completed against 3 read-only originals
- 962 protocol/string candidates reviewed
- no solve claimed
- actual solve remains blocked on a safe evidence-backed solver

## 2026-04-26 - ADB originals reacquired and partial handler solve recorded

The `snail-recon` AVD was relaunched and `com.qcplay.snail.android.na` was started.

ADB returned:

```text
emulator-5554	device
```

Fresh ADB proof:

```text
/tmp/proof_snail_protocol_adb_20260426T204437Z
```

Phase 2B audit proof:

```text
/tmp/proof_snail_phase2b_cipher_audit_20260426T204455Z
```

Partial solve proof:

```text
/tmp/proof_snail_phase2b_cipher_solve_20260426T204627Z
```

New handler-anchored mappings:

- `H -> Y`
- `S -> K`
- `b -> Q`
- `d -> T`
- `6 -> 6`

Still unresolved:

- `r`
- punctuation/symbol layer
- exact protocol-name cleanup

## 2026-04-26 - Phase 2C filetree protocol matching

The live device handler tree was used to normalize protocol names without claiming raw exact punctuation recovery.

Phase 2C proof:

```text
/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z
```

Result:

- 962 protocol candidates checked against 962 device handler names
- 954 unique skeleton matches
- 713 exact-length printable-symbol matches
- 241 skeleton-only length-delta matches
- 0 ambiguous matches
- 8 unmatched candidates
- 119 rank/group/arena/top target matches

This recovers most protocol names by filetree evidence, while leaving byte-level punctuation and 8 no-handler candidates unresolved.

Sanitized protocol report:

```text
docs/protocol/phase2c_filetree_protocol_report.md
```

## 2026-04-26 - Phase 2D target handler inventory

Phase 2D proof:

```text
/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z
```

Result:

- 8 unmatched protocol candidates triaged
- 0 unmatched candidates promoted
- 119 target handlers pulled and hashed
- 0 pull errors
- raw handlers remain external only

Safe report:

```text
reports/phase2d-target-handler-inventory-20260426T210527Z.md
```

## 2026-04-26 - Phase 2E field-flow reconnaissance

Phase 2E proof:

```text
/tmp/proof_snail_phase2e_field_flow_20260426T210812Z
```

Result:

- 10 high-value handlers analyzed from decoded printable views
- Rank/group/arena manager calls extracted
- Key `lpc` field candidates identified
- raw handlers remain external only

Safe report:

```text
reports/phase2e-rank-group-field-flow-20260426T210812Z.md
```

## 2026-04-27 - Phase 2N template expansion

Phase 2N expanded the shared Phase 2L/2M phrase-template set with stable API/member-access anchors only.

New external proofs:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z
/tmp/proof_snail_phase2m_phrase_coverage_20260427T155912Z
```

Result:

- 838 small handlers scanned
- Phase 2L phrase occurrences increased from 1544 to 1772
- repeated conflict-free phrase contexts increased from 87 to 146
- context conflicts remained 0
- Phase 2M handlers with >=50% phrase coverage increased from 6 to 22
- max phrase-template coverage increased from 54.84% to 69.33%

Safe report:

```text
reports/phase2n-template-expansion-20260427T155912Z.md
```

Next action:

Build a redacted template-overlay decoder that emits phrase IDs, known local gaps, unresolved spans, input hashes, and conflict ledgers without claiming full source reconstruction.

## 2026-04-27 - Phase 2O template overlay decoder

Phase 2O added a redacted template-overlay decoder using the Phase 2N phrase-gap ledger.

External proof:

```text
/tmp/proof_snail_phase2o_template_overlay_20260427T160243Z
```

Result:

- 838 small handlers scanned
- 1771 non-overlapping phrase overlays selected
- 2133 unresolved spans recorded
- 3338 known phrase-local gap rows
- 0 unknown gap rows
- 0 conflict gap rows

Safe report:

```text
reports/phase2o-template-overlay-decoder-20260427T160243Z.md
```

Next action:

Rank repeated unresolved spans and add only reusable high-confidence templates.

## 2026-04-27 - Phase 2P unresolved span inventory

Phase 2P ranked unresolved spans from the redacted Phase 2O overlays. Sensitive span text stayed external only.

External proof:

```text
/tmp/proof_snail_phase2p_unresolved_span_inventory_20260427T160515Z
```

Result:

- 838 input handlers
- 2000 unresolved span rows
- 1867 unique unresolved spans
- 36 repeated unresolved spans
- sanitized summary uses hashes/counts/sample files only

Safe report:

```text
reports/phase2p-unresolved-span-inventory-20260427T160515Z.md
```

Next action:

Use the top repeated unresolved hashes to add a small Phase 2Q template pass.

## 2026-04-27 - Phase 2Q external template trial

Phase 2Q tested repeated unresolved spans as external-only candidate templates. Sensitive candidate text stayed in `/tmp`.

External proof:

```text
/tmp/proof_snail_phase2q_external_template_trial_20260427T160811Z
```

Result:

- 12 external candidate templates selected
- 838 handlers scanned
- 1977 phrase sequence rows
- handlers with >=50% phrase coverage increased from 22 to 45
- max coverage stayed 69.33%
- no candidate template text committed

Safe report:

```text
reports/phase2q-external-template-trial-20260427T160811Z.md
```

Next action:

Classify the 12 external candidates and promote only reusable API/member or grammar templates.

## 2026-04-27 - Phase 2R candidate classifier

Phase 2R classified the 12 Phase 2Q external candidates while keeping candidate text external.

External proof:

```text
/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z
```

Result:

- 12 candidate templates classified
- 8 candidate-promotable rows
- 3 API/member fragments
- 5 grammar fragments
- 4 domain/event constants kept external
- no candidate text committed

Safe report:

```text
reports/phase2r-candidate-classifier-20260427T195222Z.md
```

Next action:

Promote only the 8 candidate-promotable rows into named template IDs, rerun Phase 2L/2M/2O, and verify no phrase-local conflicts.

## 2026-04-27 - Phase 2S promotable template trial

Phase 2S tested only the 8 Phase 2R `promotable=true` rows. Candidate text stayed external only.

External proof:

```text
/tmp/proof_snail_phase2s_promotable_template_trial_20260427T195500Z
```

Result:

- 8 promotable external templates selected
- 838 handlers scanned
- 1948 phrase sequence rows
- handlers with >=50% phrase coverage increased from 22 to 36 versus the Phase 2N base
- stricter than Phase 2Q's 45 because 4 domain/event constants were excluded
- max coverage stayed 69.33%

Safe report:

```text
reports/phase2s-promotable-template-trial-20260427T195500Z.md
```

Next action:

Run a conflict-aware overlay pass that keeps base templates and promotable external templates separately tagged.

## 2026-04-27 - Phase 2T conflict-aware overlay

Phase 2T layered base templates and Phase 2R promotable external templates into one redacted overlay with source tags and skipped-overlap reporting.

External proof:

```text
/tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z
```

Result:

- 838 handlers scanned
- 1948 candidate occurrences
- 1945 selected occurrences
- 3 skipped overlaps
- 1771 selected base occurrences
- 174 selected promotable external occurrences
- 3338 known gap rows
- 0 unknown gap rows
- 0 conflict gap rows

Safe report:

```text
reports/phase2t-conflict-overlay-20260427T195741Z.md
```

Next action:

Identify which selected promotable external templates deserve stable committed names, while keeping exact sensitive text external unless it is already a known project-safe API/member name.

## 2026-04-27 - Phase 2U promotable stats

Phase 2U ranked selected promotable templates using sanitized metadata only.

External proof:

```text
/tmp/proof_snail_phase2u_promotable_stats_20260427T195959Z
```

Result:

- 8 promotable templates seen
- 174 total selected promotable occurrences
- 2 total skipped promotable overlaps
- top 2 candidates are API/member fragments with zero skipped overlaps
- short grammar fragment has 42 selected overlays but 2 skipped overlaps

Safe report:

```text
reports/phase2u-promotable-stats-20260427T195959Z.md
```

Next action:

Inspect the top API/member candidates externally and decide whether their exact names are safe to promote as committed template identifiers.

## 2026-04-27 - Phase 2V API template promotion

Phase 2V promoted only the two highest-priority API/member candidates into the committed base phrase table.

External proofs:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T200142Z
/tmp/proof_snail_phase2m_phrase_coverage_20260427T200142Z
/tmp/proof_snail_phase2o_template_overlay_20260427T200147Z
```

Result:

- promoted `dormutil_close_communicating`
- promoted `close_communicating_dorm`
- Phase 2L phrase occurrences increased to 1855
- Phase 2L context conflicts remained 0
- Phase 2M handlers with >=50% base-template coverage increased from 22 to 32
- Phase 2O unknown/conflict gap rows remained 0/0

Safe report:

```text
reports/phase2v-api-template-promotion-20260427T200147Z.md
```

Next action:

Build a grammar-context audit for the remaining external grammar fragments, especially the short fragment with 42 selected overlays and 2 skipped overlaps.

## 2026-04-27 - Phase 2W grammar fragment audit

Phase 2W audited the remaining external grammar fragments with sensitive text kept external.

External proof:

```text
/tmp/proof_snail_phase2w_grammar_fragment_audit_20260427T200422Z
```

Result:

- 5 grammar candidates audited
- 2 marked `trial_ok`
- 3 marked `hold`
- the high-count short fragment stayed on hold because it has skipped overlaps
- no fragment text committed

Safe report:

```text
reports/phase2w-grammar-fragment-audit-20260427T200422Z.md
```

Next action:

Run an external-only punctuation-aware trial for the two `trial_ok` grammar fragments.

## 2026-04-27 - Phase 2G manager trace after game restart

The emulator survived the laptop restart path but the game needed relaunch/permission handling.

Confirmed runtime state:

- `adb devices`: `emulator-5554 device`
- game PID: `7211`
- top activity: `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`

Phase 2G proof:

```text
/tmp/proof_snail_phase2g_manager_trace_20260427T132529Z
```

Result:

- pulled 6 manager scripts and 5 target handlers from the live app
- set all pulled originals read-only (`444`)
- decrypted only into external `/tmp` proof outputs
- corrected the Phase 2F overclaim: current decryptor is partial, not exact source reconstruction
- traced `RankM.setRankInfo` as opaque list storage into `cacheData[rankId][start + index]`
- traced `msg_group_war_member_rank` as the current strongest field-flow proof for `data.list`, including `rid`, `kit`, `joinTime`, `isNew`, `isClientAdd`, and `isShowKit`

Still unresolved:

- byte-exact punctuation/operator cipher
- exact full Lua source reconstruction
- full nested server payload schema for generic rank lists

Safe report:

```text
reports/phase2g-manager-trace-20260427T132529Z.md
```

## 2026-04-27 - Phase 2H punctuation conflict audit

Phase 2H tested whether the punctuation/operator layer can be safely promoted as a global byte-to-byte substitution table.

Phase 2H proof:

```text
/tmp/proof_snail_phase2h_punctuation_audit_20260427T151537Z
```

Result:

- 103 anchored evidence rows
- 12 punctuation candidate bytes
- 3 punctuation conflicts
- 0 alphanumeric conflicts
- solved: false

Conflict summary:

- encrypted `)` mapped to both comma and space under current anchors
- encrypted space mapped to both `(` and `.`
- encrypted `_` mapped to both `.` and newline

Conclusion:

The alphanumeric table remains useful for handler navigation, but exact Lua source reconstruction is still blocked by the punctuation/control layer. Do not patch the decryptor with forced punctuation mappings.

Safe report:

```text
reports/phase2h-punctuation-audit-20260427T151537Z.md
```

## 2026-04-27 - Phase 2I raw skeleton transform audit

Phase 2I aligned handler bodies by alphanumeric skeleton only, then recorded the raw punctuation/control byte runs between matched alphanumeric bytes.

Phase 2I proof:

```text
/tmp/proof_snail_phase2i_skeleton_transform_20260427T152041Z
```

Result:

- 4 anchors checked
- 0 anchors missing
- 59 raw gap rows
- 10 raw gap conflicts
- solved: false

Anchors found:

- `group_rank_body`
- `arena_top_body`
- `top_rank_body`
- `week_task_rank_call`

Conclusion:

The raw punctuation/control layer is a context/run-level transform problem, not a safe one-byte punctuation substitution table. Exact source reconstruction remains blocked, but handler body identification by alphanumeric skeleton is working.

Safe report:

```text
reports/phase2i-skeleton-transform-audit-20260427T152041Z.md
```

## 2026-04-27 - Phase 2J gap context model

Phase 2J grouped Phase 2I raw gap evidence by local left/right alphanumeric context.

Phase 2J proof:

```text
/tmp/proof_snail_phase2j_gap_context_model_20260427T152345Z
```

Result:

- 59 gap rows
- 59 exact context rows
- 59 local single-candidate rows
- 0 repeated conflict-free context rows
- 0 context conflict rows
- 38 global raw gap rows
- solved: false

Conclusion:

Context/run-level modeling is the right branch, but the current anchor set is still too sparse. No transform is promoted until an exact context repeats without conflict.

Safe report:

```text
reports/phase2j-gap-context-model-20260427T152345Z.md
```

## 2026-04-27 - Phase 2K simple handler anchor inventory

Phase 2K pulled small `cmd/misc` handlers into external `/tmp` proof storage and generated sanitized structural metadata for anchor expansion.

Raw-pull proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z
```

Sanitized inventory proof:

```text
/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152713Z
```

Result:

- 838 handlers scanned
- 830 handlers contain the `returnfunctionlpc` alphanumeric skeleton
- 838 handlers received positive anchor scores
- top 80 candidates exported externally

Conclusion:

The anchor pool is large enough to continue the transform model safely. Next step is selecting repeated, simple proxy patterns from `top_anchor_candidates.tsv` and feeding them into the Phase 2I/2J workflow.

Safe report:

```text
reports/phase2k-simple-anchor-inventory-20260427T152713Z.md
```

## 2026-04-27 - Phase 2L standard phrase gap audit

Phase 2L scanned the 838 small-handler external originals for repeated standard phrase skeletons and aggregated raw gap evidence inside those phrases.

Phase 2L proof:

```text
/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T154941Z
```

Result:

- 838 handlers scanned
- 1544 phrase occurrences
- 3072 gap rows
- 144 context rows
- 87 repeated conflict-free contexts
- 0 context conflicts
- solved: false

Conclusion:

This is the strongest punctuation/control evidence so far. It shows phrase-local grammar contexts are stable, but raw gap bytes are polymorphic. Exact reconstruction should use phrase templates and local contexts, not a global raw punctuation substitution table.

Safe report:

```text
reports/phase2l-standard-phrase-gap-audit-20260427T154941Z.md
```

## 2026-04-27 - Phase 2M phrase template coverage

Phase 2M measured how much of each small handler is covered by the proven standard phrase templates from Phase 2L.

Phase 2M proof:

```text
/tmp/proof_snail_phase2m_phrase_coverage_20260427T155228Z
```

Result:

- 838 handlers scanned
- 1544 phrase sequence rows
- 6 handlers with at least 50% phrase coverage
- max coverage: 54.84%
- solved: false

Conclusion:

Phrase templates are useful but incomplete. The next branch is adding more manager/call templates from top candidates, then rerunning phrase coverage and conflict checks.

Safe report:

```text
reports/phase2m-phrase-coverage-20260427T155228Z.md
```

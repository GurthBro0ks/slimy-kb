# RESULT

## 1. Executive summary

Fresh originals were reacquired from the emulator into the proof directory and made read-only. The current project-root `.luac` files are contaminated/suspect and were quarantined as copies only. A candidate decode was generated from read-only originals without normalization.

## 2. Trusted vs contaminated files

Trusted for this proof: files under `originals/` with recorded hashes. Contaminated/suspicious: v2 artifacts, rewrite scripts, plan.py, and current project-root `.luac` files.

## 3. Whether originals were reacquired

Yes. adb pulled list.luac, msg_group_rank.luac, and msg_arena_top_query.luac with expected pre-contamination sizes 32597, 173, and 214 bytes.

## 4. Current cipher status

Incomplete. Candidate table has 46 carried-forward mappings from substitution_table.txt. Observed unmapped ASCII alphanumerics: 6, H, S, b, d, r. Punctuation remains unresolved.

## 5. Current protocol status

Quoted protocol strings extracted without normalization: 962. Exact/trusted-character strings: 48. Unresolved/invalid-symbol strings: 914.

## 6. Rank/club target messages

Target candidates written to `reports/rank_group_targets.md`; count: 121.

## 7. What remains blocked

A proof-derived punctuation/symbol substitution table and missing alphanumeric mappings are still needed before a clean protocol spec can be claimed.

## 8. Exact next step

Use the read-only originals and handler ground truth to derive mappings with explicit byte offsets and conflict reporting. Do not use v2 artifacts as proof.

Final status: PASS_CLEAN_ORIGINALS_READY

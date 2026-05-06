# Phase 2B - Evidence-Backed Cipher Solve Plan

## Goal

Complete the remaining cipher mappings from clean, read-only originals.

## Inputs

External proof directory:

```text
/tmp/proof_snail_protocol_reset_20260426T170226Z
```

Trusted originals are outside Git.

Expected source path:

```text
/tmp/proof_snail_protocol_reset_20260426T170226Z/originals/
```

## Current Blockers

Unmapped observed ASCII alphanumerics:

```text
6, H, S, b, d, r
```

Punctuation remains unresolved.

## Method

1. Load read-only originals.
2. Extract printable byte streams.
3. Apply current trusted alphanumeric mapping.
4. Derive remaining mappings only from anchored known plaintext.
5. Separate three categories:
   - proven mapping
   - conflict mapping
   - guess/normalization
6. Never overwrite original evidence.
7. Write all outputs to a timestamped proof directory.
8. Generate a final `RESULT.md`.

## Success Criteria

`PASS_PHASE2B_CIPHER_IMPROVED` requires:

- source originals are read-only and hash-verified
- no original files overwritten
- every new mapping has evidence
- every conflict is listed
- unresolved punctuation is not hidden
- protocol target names for rank/group/arena are improved or clearly marked unresolved

`PASS_PHASE2B_CIPHER_COMPLETE` additionally requires:

- no unmapped observed alphanumerics remain
- protocol names decode without symbol corruption
- handler ground truths match without contradiction

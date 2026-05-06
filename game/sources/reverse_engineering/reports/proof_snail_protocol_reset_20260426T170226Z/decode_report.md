# Decode Report

Inputs: read-only files from `originals/` only.

## Mapping Status

- Candidate mappings loaded from `/tmp/substitution_table.txt`: 46
- Observed unmapped ASCII alphanumeric bytes: 6, H, S, b, d, r
- Punctuation layer: unresolved; no punctuation was normalized.

## Handler: msg_group_rank.luac

- Exact match expected text: False
- Omitted non-printable/high-bit bytes: 36
- Unmapped alphanumeric occurrences: 3
- Diff: `msg_group_rank.luac.diff`

## Handler: msg_arena_top_query.luac

- Exact match expected text: False
- Omitted non-printable/high-bit bytes: 84
- Unmapped alphanumeric occurrences: 3
- Diff: `msg_arena_top_query.luac.diff`

## Protocol Strings

- Total quoted strings extracted: 962
- Exact/trusted-character strings: 48
- Normalized/guessed strings: 0 (not performed)
- Unresolved/invalid-symbol strings: 914
- Non-printable/high-bit bytes omitted from list text view: 929

## Conflicts / Invalid Evidence

- Strict positional handler comparison is not valid evidence because printable-stream lengths differ after high-bit blocks are omitted.

- msg_group_rank.luac: encoded '#' would map to multiple decoded chars under naive positional alignment: ['-', 'U']
- msg_group_rank.luac: encoded '+' would map to multiple decoded chars under naive positional alignment: ['-', '0', '_', 'c']
- msg_group_rank.luac: encoded 'T' would map to multiple decoded chars under naive positional alignment: ['(', 's']
- msg_group_rank.luac: encoded 'A' would map to multiple decoded chars under naive positional alignment: ['(', 'a', 'r', 't']
- msg_group_rank.luac: encoded 'F' would map to multiple decoded chars under naive positional alignment: [' ', 'O', 'o']
- msg_group_rank.luac: encoded 'k' would map to multiple decoded chars under naive positional alignment: [')', 'n', 'u']
- msg_group_rank.luac: encoded '3' would map to multiple decoded chars under naive positional alignment: ['\n', 'k', 'p']
- msg_group_rank.luac: encoded 'g' would map to multiple decoded chars under naive positional alignment: ['K', 'a', 'e', 'k']
- msg_group_rank.luac: encoded '7' would map to multiple decoded chars under naive positional alignment: ['\n', ' ', 'G', 'I', 'R', 'l', 'n', 't']
- msg_group_rank.luac: encoded 'e' would map to multiple decoded chars under naive positional alignment: ['D', 'k', 'n']
- msg_group_rank.luac: encoded '8' would map to multiple decoded chars under naive positional alignment: [' ', '-', 'M', 'e']
- msg_group_rank.luac: encoded '-' would map to multiple decoded chars under naive positional alignment: [' ', 'y']
- msg_group_rank.luac: encoded ';' would map to multiple decoded chars under naive positional alignment: ['C', 'n', 't']
- msg_group_rank.luac: encoded 'f' would map to multiple decoded chars under naive positional alignment: ['R', 'b', 'i', 't', 'x']
- msg_group_rank.luac: encoded 'p' would map to multiple decoded chars under naive positional alignment: [' ', 'A', 'o']
- msg_group_rank.luac: encoded '*' would map to multiple decoded chars under naive positional alignment: [' ', '2', 'R']
- msg_group_rank.luac: encoded 't' would map to multiple decoded chars under naive positional alignment: ['0', '3']
- msg_group_rank.luac: encoded 'c' would map to multiple decoded chars under naive positional alignment: ['-', 'r', 'u']
- msg_group_rank.luac: encoded ')' would map to multiple decoded chars under naive positional alignment: ['\n', 'a']
- msg_group_rank.luac: encoded '=' would map to multiple decoded chars under naive positional alignment: ['i', 't', 'u']
- msg_group_rank.luac: encoded '|' would map to multiple decoded chars under naive positional alignment: ['.', 'n']
- msg_group_rank.luac: encoded '(' would map to multiple decoded chars under naive positional alignment: ['e', 'p', 's']
- msg_group_rank.luac: encoded 'u' would map to multiple decoded chars under naive positional alignment: ['R', 'c']
- msg_group_rank.luac: encoded '4' would map to multiple decoded chars under naive positional alignment: [' ', ')']
- msg_group_rank.luac: encoded 'W' would map to multiple decoded chars under naive positional alignment: ['\n', 'd', 'n']
- msg_group_rank.luac: encoded '_' would map to multiple decoded chars under naive positional alignment: ['n', 'o', 's']
- msg_group_rank.luac: encoded 'I' would map to multiple decoded chars under naive positional alignment: ['N', 'P', 'n', 'p']
- msg_group_rank.luac: encoded 'C' would map to multiple decoded chars under naive positional alignment: ['_', 'l']
- msg_arena_top_query.luac: encoded '+' would map to multiple decoded chars under naive positional alignment: ['\n', '-', 'O', '_']
- msg_arena_top_query.luac: encoded '%' would map to multiple decoded chars under naive positional alignment: [' ', 'E']
- msg_arena_top_query.luac: encoded '5' would map to multiple decoded chars under naive positional alignment: ['(', 'g']
- msg_arena_top_query.luac: encoded 'A' would map to multiple decoded chars under naive positional alignment: ['n', 'r']
- msg_arena_top_query.luac: encoded 'f' would map to multiple decoded chars under naive positional alignment: [' ', 'P', 'Q', 'T', 'e', 'v']
- msg_arena_top_query.luac: encoded '7' would map to multiple decoded chars under naive positional alignment: [')', 'U', 'c', 'e', 'n']
- msg_arena_top_query.luac: encoded 'p' would map to multiple decoded chars under naive positional alignment: ['E', 'f', 'l', 'n', 't']
- msg_arena_top_query.luac: encoded 'F' would map to multiple decoded chars under naive positional alignment: ['c', 'o']
- msg_arena_top_query.luac: encoded '3' would map to multiple decoded chars under naive positional alignment: [' ', 'p']
- msg_arena_top_query.luac: encoded ' ' would map to multiple decoded chars under naive positional alignment: ['_', 'e', 'n']
- msg_arena_top_query.luac: encoded 'k' would map to multiple decoded chars under naive positional alignment: ['o', 'u']
- msg_arena_top_query.luac: encoded '_' would map to multiple decoded chars under naive positional alignment: ['\n', 'r']
- msg_arena_top_query.luac: encoded '{' would map to multiple decoded chars under naive positional alignment: ['\n', '-', 'M', 'i', 'r']
- msg_arena_top_query.luac: encoded '=' would map to multiple decoded chars under naive positional alignment: [' ', 'u']
- msg_arena_top_query.luac: encoded ')' would map to multiple decoded chars under naive positional alignment: [' ', 'e', 'r']
- msg_arena_top_query.luac: encoded '4' would map to multiple decoded chars under naive positional alignment: ['N', 'i', 'p']
- msg_arena_top_query.luac: encoded ';' would map to multiple decoded chars under naive positional alignment: ['R', 't']
- msg_arena_top_query.luac: encoded 'u' would map to multiple decoded chars under naive positional alignment: ['E', 'i']
- msg_arena_top_query.luac: encoded '8' would map to multiple decoded chars under naive positional alignment: [' ', '(']
- msg_arena_top_query.luac: encoded '(' would map to multiple decoded chars under naive positional alignment: ['g', 't']
- msg_arena_top_query.luac: encoded 'P' would map to multiple decoded chars under naive positional alignment: [' ', '_']
- msg_arena_top_query.luac: encoded 'a' would map to multiple decoded chars under naive positional alignment: ['_', 'e']
- ... 1 more naive-position conflicts

## Extraction Correction

- Protocol extraction uses printable/noise-stripped decoded view, not control-byte-preserving text. No symbol normalization was applied.

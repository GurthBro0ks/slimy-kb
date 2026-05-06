# Phase 3 Native BoringSSL Hooking Report

**Date:** 2026-04-27
**Task:** Phase 3 native BoringSSL hooking for JPush intercept
**Binary analyzed:** libcocos2dlua.so (SHA256: `b5483d9a47647de92d615b5ad722a58cc3ce21251de833bd7a21e5c929873332`)

## Summary

Native BoringSSL symbols are **exported and hookable** in `libcocos2dlua.so`. However, Frida 17.9.1 cannot enumerate this library as a module, requiring a `/proc/self/maps` parsing workaround. Hooks on `SSL_CTX_set_verify`, `SSL_set_verify`, and `SSL_do_handshake` succeed, but JPush TLS connections were not visible in this session (likely timing-related: game had not yet reached JPush initialization). An application-layer fallback via `SSL_read`/`SSL_write` hooking is prepared and represents the stronger long-term approach.

## 1. Symbol Analysis Results

### Target Symbols Found (all dynamically exported)

| Symbol | Offset | Exported | Hookable |
|--------|--------|----------|----------|
| `SSL_CTX_set_verify` | `0xca2494` | Yes | Yes (direct address) |
| `SSL_set_verify` | `0xca0a4c` | Yes | Yes (direct address) |
| `SSL_do_handshake` | `0xca0de8` | Yes | Yes (direct address) |
| `SSL_read` | `0xca1020` | Yes | Yes (direct address) |
| `SSL_write` | `0xca136c` | Yes | Yes (direct address) |
| `SSL_get_peer_certificate` | `0xca0ac0` | Yes | **No** (Frida bug) |
| `SSL_CTX_set_custom_verify` | N/A | No | N/A (not present) |
| `X509_verify_cert` | N/A | No | N/A (internal only) |

### Key Finding: Frida Module Enumeration Gap

`Process.findModuleByName('libcocos2dlua.so')` returns `null` and `Process.enumerateModules()` does not include `libcocos2dlua.so` despite it being mapped in `/proc/PID/maps`. This is a Frida 17.9.1 limitation/bug.

**Workaround:** Parse `/proc/self/maps` using libc `fopen`/`fgets` to obtain the base address, then add symbol offsets.

## 2. Hook Method Used

### Method 1: SSL Context Verification Hooks
- Hooks `SSL_CTX_set_verify` and `SSL_set_verify`
- Forces `mode` argument to `SSL_VERIFY_NONE` (0x00)
- Sets callback argument to `NULL`

### Method 2: SSL_do_handshake Hook
- Hooks `SSL_do_handshake` to catch pre-created SSL contexts
- Directly writes `0` to `ssl->verify_mode` (offset 392) and `NULL` to `ssl->verify_callback` (offset 400)
- Offsets derived from disassembly of `SSL_set_verify`

### Method 3: Application-Layer Intercept (Fallback)
- Hooks `SSL_read` and `SSL_write` to capture plaintext after TLS decryption
- Logs message length and first 32 bytes as hex
- Does not require breaking TLS at all

### Method 4: VerifyAgent Hooks (Future Work)
- Symbols identified:
  - `VerifyAgent::sendMsg` @ `0x48d778`
  - `VerifyAgent::recvMsg` @ `0x48dcd8`
  - `VerifyAgent::ackMsg` @ `0x48dac0`
  - `VerifyAgent::verifyLoop` @ `0x48df70`
- These are the application-layer message dispatch functions
- Hooking these would provide protocol names and payload structures directly

## 3. JPush Traffic Visibility

### Result: Not Visible in This Session
- No connections to `jpush-hw-game.qcplay.com` observed in mitmproxy
- No `SSL_read`/`SSL_write` calls logged by Frida hooks
- Likely cause: Game was in early loading phase; JPush initializes after tutorial/login
- Previous session (40 min interactive) showed 2,750 failed JPush TLS connections

### What Worked
- Java-layer unpin: Successfully intercepted HTTPS traffic to `qcplay.aihelp.net`, `sdk-sg.qcplay.com`, etc.
- Native hooks: Successfully applied to running process
- `SSL_do_handshake` was called once (confirmed hook is active)

### What Didn't Work
- `SSL_get_peer_certificate` hook fails with Frida bug "unable to intercept function"
- Spawn-gating with library polling loop caused script to run for 55+ seconds without finding library (timing issue with `Java.perform` callback)

## 4. Message Format Discovery

### Current Status: Pending Live Traffic
No JPush plaintext messages were captured in this session. Prepared infrastructure:
- `scripts/frida_jpush_intercept.js` hooks `SSL_read`/`SSL_write`
- Will log message length + hex preview when traffic appears
- Full payload capture can be added by writing to `/data/local/tmp/` or base64-encoding to console

### Expected Format (Hypothesis - Tier 2)
Based on JPush SDK documentation and game architecture:
- Likely length-prefixed binary protocol
- May include protobuf or custom framing
- Phase 2C protocol names (`msg_group_rank`, `msg_arena_top_query`) expected in payload

## 5. Alternative Approach Recommendation

**Primary recommendation: Hook SSL_read/SSL_write**
- Pros: Works regardless of TLS implementation; no need to break certificate validation
- Cons: Requires live traffic; payload structure must be reverse-engineered from binary

**Secondary recommendation: Hook VerifyAgent::sendMsg/recvMsg**
- Pros: Direct access to application-layer messages; may include protocol names as strings
- Cons: Requires C++ symbol hooking with mangled names; function signatures must be determined

**Tertiary recommendation: Continue BoringSSL unpin**
- If JPush uses BoringSSL from libcocos2dlua.so, the hooks are correct
- Timing issue: Must apply hooks before first TLS handshake
- Solution: Use spawn-gating with `dlopen` hook or early `JNI_OnLoad` interception

## 6. Frida Scripts

### scripts/frida_native_ssl_unpin.js
- BoringSSL verification bypass
- Handles both attach and spawn modes
- Uses `/proc/self/maps` parsing for base address

### scripts/frida_jpush_intercept.js
- Application-layer plaintext intercept
- Hooks `SSL_read`/`SSL_write`
- Logs hex previews of messages

## 7. Technical Notes

### Frida 17.9.1 API Differences
- `Module.findExportByName` does **not** exist
- Use `Module.getGlobalExportByName(moduleName, symbolName)` for global exports
- `ptr('0x...')` requires `0x` prefix; `ptr('deadbeef')` fails
- String reading: `buffer.readUtf8String()` (NativePointer method), not `Memory.readUtf8String()`

### Memory Layout of libcocos2dlua.so
- Library mapped in multiple segments
- Code resides in `rwxp` pages (unusual - normally `r-xp`)
- This explains why direct address hooking works

## 8. Remaining Unknowns

1. Whether JPush uses BoringSSL from libcocos2dlua.so or bundles its own TLS
2. Exact timing of JPush initialization in game lifecycle
3. JPush message framing and serialization format
4. Whether Phase 2C protocol names appear as strings in JPush payloads
5. Effectiveness of spawn-gating with early hook application

## Evidence Tier

- **Tier 0:** libcocos2dlua.so pulled from device, SHA256 recorded
- **Tier 1:** Symbol offsets derived via nm/objdump, cited with input hash
- **Tier 2:** JPush message format is hypothesized (no live capture)

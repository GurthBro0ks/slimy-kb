# Phase 3 Raw recv()/send() Hook Analysis

**Date:** 2026-04-28
**Task:** Raw recv()/send() hook + binary protocol analysis
**Main PID:** 8296
**JPush PID:** 4781

## Summary

Frida successfully attached to main game process and hooked libc.so recv/send/read/write/connect/close and libssl.so SSL_read/SSL_write. No custom binary protocol traffic on port 50504 was captured during the session. Connection to 47.252.2.69:50504 was not active during the capture window.

## Findings

### 1. Hook Status
- **libc.so hooks:** All 7 functions hooked successfully
  - connect @ 0x7f8aed6f82b0
  - recv @ 0x7f8aed706060
  - recvfrom @ 0x7f8aed750070
  - read @ 0x7f8aed74f1f0
  - send @ 0x7f8aed7069b0
  - sendto @ 0x7f8aed6f82e0
  - write @ 0x7f8aed74f210
- **libssl.so hooks:** SSL_read and SSL_write hooked successfully
  - SSL_read @ 0x7f8828588ad0
  - SSL_write @ 0x7f8828588f10
- **Existing connection scan:** Failed (permission denied opening /proc/self/net/tcp from Frida)

### 2. Traffic Captured
During a 5-minute capture window, **5 packets** were intercepted via SSL_read/SSL_write:

| Direction | Size | Protocol | Notes |
|-----------|------|----------|-------|
| CLIENT->SERVER | 5764 | HTTPS | POST /adnw_sync2 (Facebook SDK) |
| SERVER->CLIENT | 1500 | HTTPS | HTTP/1.1 200 OK, gzip encoded |
| SERVER->CLIENT | 1785 | HTTPS | Content-Security-Policy headers |
| SERVER->CLIENT | 1682 | HTTPS | Permissions-Policy headers |
| SERVER->CLIENT | 1418 | HTTPS | gzip compressed body |

**All captured traffic is Facebook SDK/analytics HTTPS traffic**, NOT the custom binary game protocol.

### 3. Custom Binary Protocol (50504) Status
- **No 4d5a frames detected** during capture
- **No connection to 47.252.2.69:50504** observed in /proc/net/tcp for either main or JPush process
- Tcpdump check (10s window) captured 0 packets to 47.252.2.69
- **Conclusion:** The 50504 connection is established dynamically during specific game operations and may disconnect when idle

### 4. Connection Type Assessment
- **Facebook traffic:** TLS (SSL_read/SSL_write confirmed)
- **Game protocol (50504):** Unknown — could be:
  - Cleartext custom binary (4d5a header suggests this)
  - TLS-wrapped custom binary
  - IPC/socket shared with JPush remote process

### 5. Frame Structure Hypothesis (from prior tcpdump)
Based on the earlier tcpdump capture (2026-04-28), the protocol uses:
- **Magic header:** 4d5a 0000 0000 0000 (8 bytes)
- **Hypothesis:** bytes 8-11 = length, bytes 12-15 = message type
- **Payload:** Likely encrypted or compressed (no readable strings in raw tcpdump)

## What Passed
- Frida attachment to main process: working
- libc.so hooks: working
- libssl.so hooks: working
- Sanitized logging: no secrets/tokens/account data captured

## Remaining Unknowns
1. **When does the 50504 connection activate?** — Only during specific game modes? Only after login? Only during real-time multiplayer?
2. **Which process handles 50504?** — Main process or JPush remote process?
3. **Is 50504 TLS or cleartext?** — tcpdump showed 4d5a directly (suggests cleartext or post-decrypt), but we need to confirm
4. **Message type mapping** — Cannot identify msg_id values without capturing actual frames
5. **Encryption key** — Cannot test XXTEA/RC4 decryption without payload bytes

## Recommended Next Steps
1. **Attach to JPush remote process (PID 4781)** with same recv hook script
2. **Use tcpdump during active gameplay** (rankings, arena, club navigation) to confirm 50504 is active
3. **Trigger specific game actions** that likely use real-time protocol:
   - Arena matchmaking/challenge
   - Club war participation
   - Real-time chat
4. **If cleartext:** The recv() hooks will catch it immediately when connection is active
5. **If TLS:** Need to hook BoringSSL in libcocos2dlua.so (not libssl.so)

## Artifacts
- Frida script: `scripts/frida_recv_hook.js`
- Python runner: `scripts/run_recv_hook.py`
- Capture log: `captures/private/phase3/20260428T185018/frida_recv_hook.log`
- Sanitized summary: `captures/private/phase3/20260428T185018/sanitized_summary.json`

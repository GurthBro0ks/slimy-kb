# Phase 3 Extended JPush Capture Session — Sanitized Report

**Date:** 2026-04-28  
**Session ID:** 20260428T053039Z  
**Duration:** ~35 minutes (game started 01:30, Frida attached 01:35, session ended ~02:05)

## Methodology

- **Attach mode:** Game started without Frida, allowed 40s boot time, then Frida attached to running processes
- **Proxy:** mitmdump on port 8080 (emulator proxy: 10.0.2.2:8080)
- **Frida scripts:**
  - `scripts/frida_ssl_unpin.js` — Java-layer SSL unpinning
  - `scripts/frida_native_ssl_unpin.js` — Native BoringSSL hooks (libcocos2dlua.so)
  - `scripts/frida_jpush_intercept.js` — Application-layer SSL_read/SSL_write hooks
  - `scripts/frida_system_ssl_unpin.js` — System libssl.so hooks for JPush process

## Process Map

| Process | PID | Purpose | Hooks Applied |
|---------|-----|---------|---------------|
| Main game | 14238 | Game engine | Java SSL + native BoringSSL (libcocos2dlua.so) |
| JPush remote | 14605 | Push/notification service | Java SSL + system libssl.so |

**Critical finding:** JPush runs in a separate process (`:jpushremote`), not the main game process. Initial attach to main process alone was insufficient.

## Hook Hit Counts

### Main Process (PID 14238)
- SSL_CTX_set_verify hooks: **0** (setup only, no hits)
- SSL_set_verify hooks: **0** (setup only, no hits)
- SSL_do_handshake hooks: **0**
- SSL_read intercepts: **0**
- SSL_write intercepts: **0**

### JPush Process (PID 14605)
- SSL_CTX_set_verify hooks: **0** (setup only, no hits)
- SSL_set_verify hooks: **0** (setup only, no hits)
- SSL_do_handshake hooks: **0**
- SSL_read intercepts: **0**
- SSL_write intercepts: **0**

**Interpretation:** Hooks were successfully applied but no new SSL contexts were created after attach. JPush SSL connections were either:
1. Already established before Frida attach, or
2. Reusing existing SSL contexts, or
3. Using a different TLS path not covered by our hooks

## Captured Traffic (Sanitized)

### Domains Observed

| Domain | Port | Count | Notes |
|--------|------|-------|-------|
| jpush-hw-game.qcplay.com | 443 | 10 connections | 1 successful POST, 9 TLS handshake failures |
| log.game.qcplay.com | 80 | 6 connections | Telemetry sync (POST /sync) |
| qcplay.aihelp.net | 443 | 4 connections | Help/support API |
| www.google.com | 80/443 | 6 connections | Connectivity checks |
| connectivitycheck.gstatic.com | 80 | 3 connections | Connectivity checks |

### JPush HTTPS Traffic

**One successful request captured:**
- Method: POST
- Path: /v3/report
- Response: 200 OK, 0 bytes
- This appears to be a heartbeat or reporting endpoint
- Successful after Java-layer SSL unpin was applied to JPush process

**Failed connections:**
- 9 TLS handshake failures with "certificate unknown" error
- These occurred before the Java-layer unpin took effect
- Pattern: rapid reconnection attempts (~1 per second)

### Non-HTTP Connections (Not Through Proxy)

**JPush process (PID 14605):**
- Persistent TCP connection to `34.124.161.204:3000` (ESTABLISHED throughout session)
- Local IPC socket to main process (`127.0.0.1:38879`)

**Main process (PID 14238):**
- TCP connection to `47.252.2.69:50504` (ESTABLISHED)
- Likely game API server; does not use HTTP/HTTPS
- This is the primary game protocol connection, not JPush

## Outcome Classification

**Primary outcome: B (with partial A)**

- SSL hooks applied successfully in both processes
- mitmproxy captured limited JPush flows (1 successful HTTPS request)
- JPush may reuse SSL contexts created before attach
- The persistent TCP/3000 connection does not use TLS (or uses TLS established pre-attach)

**Secondary observation: D (application-layer insight)**

- JPush uses a custom binary protocol over TCP/3000 for main game communication
- HTTPS /v3/report is a secondary reporting channel
- Java-layer unpin successfully allows JPush HTTPS through proxy

## Evidence Quality

- **Raw flow file:** `captures/private/phase3/20260428T053039/jpush_session.flow` (59K, gitignored)
- **Raw mitmdump log:** `captures/private/phase3/20260428T053039/mitmdump.log` (gitignored)
- **Frida logs:** `captures/private/phase3/20260428T053039/frida*.log` (gitignored)
- **No secrets/tokens/bodies committed**

## Recommendations for Phase 4

1. **Spawn-gating with early hooks:** Attach Frida immediately at app startup (spawn mode with `--no-pause` equivalent) to catch SSL context creation before JPush initializes

2. **TCP/3000 protocol analysis:** The persistent connection to `34.124.161.204:3000` is the primary JPush/game protocol. Capture and analyze this with tcpdump or packet capture

3. **Game API (47.252.2.69:50504):** This is the main game server connection. Analyze with tcpdump to understand the custom protocol

4. **JPush SDK library analysis:** Check for `libjcore*.so`, `libjpush*.so` in app lib directory (only `libcocos2dlua.so` found; JPush may be pure Java or use system SSL)

5. **iptables redirect:** If JPush bypasses proxy for TCP/3000, use iptables to force redirect:
   ```
   adb shell iptables -t nat -A OUTPUT -p tcp --dport 3000 -j DNAT --to-destination 10.0.2.2:8080
   ```

## Remaining Unknowns

- JPush TCP/3000 protocol format and framing
- Whether JPush uses its own SSL library (not system libssl.so)
- Game API protocol on TCP/50504
- Phase 2C protocol name correlation with live traffic
- Auth/session token format

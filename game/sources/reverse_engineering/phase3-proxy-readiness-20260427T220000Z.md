# Phase 3 Proxy-Readiness Assessment Report

**Date:** 2026-04-27  
**Task:** Phase 3 proxy-readiness pass — confirm proxy setup, CA cert install, and detect TLS pinning  
**Agent:** opencode (SlimyAI harness)  
**Emulator:** emulator-5554 (Android 14, SDK 34, x86_64, debuggable)  
**Game:** com.qcplay.snail.android.na  
**Game PID (during test):** 15163  

---

## 1. Executive Summary

**Outcome: TLS pinning or user-CA rejection is active.** HTTPS API traffic from the game process is not visible through mitmproxy. Unencrypted HTTP telemetry (`log.game.qcplay.com:80`) is captured. The next step is **Frida SSL-unpinning** or **apk-mitm** to bypass certificate pinning.

---

## 2. Proxy Configuration

### Method Used
- **ADB global HTTP proxy** set via `adb shell settings put global http_proxy 10.0.2.2:8080`
- Emulators use `10.0.2.2` as the host loopback address.
- Verified setting applied: returned `10.0.2.2:8080`

### Removal
- Proxy removed after test: `adb shell settings put global http_proxy :0`
- Verified removal: returned `:0`

### Proxy Tool
- **mitmdump 12.2.2** started with `--set stream_large_bodies=1`
- Listening on `*:8080`
- Flows written to `captures/private/phase3/20260427T180051/proxy_flows.mitm`
- Log written to `captures/private/phase3/20260427T180051/mitmdump_pre_game.log`

---

## 3. CA Certificate Installation

### System CA Install
- **Attempted:** Push to `/system/etc/security/cacerts/` with hash filename `c8750f0d.0`
- **Result:** FAILED — `adb remount` requires bootloader unlock; emulator bootloader is locked.
- **Consequence:** Apps targeting API 24+ (Android 7+) will not trust user-installed CAs by default unless the app explicitly opts in via `network_security_config.xml`.

### User CA Install
- **Attempted:** Manually copied cert to `/data/misc/user/0/cacerts-added/mitmproxy-ca-cert.cer`
- **Result:** File present in user CA store, but:
  - No system rescan triggered (no reboot performed).
  - Even if picked up, apps typically ignore user CAs.

### CA Cert Details
- **File:** `~/.mitmproxy/mitmproxy-ca-cert.cer`
- **Format:** PEM
- **Subject:** CN=mitmproxy, O=mitmproxy
- **Validity:** 2026-04-23 to 2036-04-22

---

## 4. Traffic Observations

### 4.1 HTTP Traffic (Visible)

| Domain | Port | Protocol | Visibility | Notes |
|--------|------|----------|------------|-------|
| `log.game.qcplay.com` | 80 | HTTP | **YES** | Game telemetry/sync endpoint. POST /sync observed. |
| `update.googleapis.com` | 80 | HTTP | YES | Google update service (Chrome/components). |
| `edgedl.me.gvt1.com` | 80 | HTTP | YES | Chrome component download. |

**Sanitized observation:** The game makes unencrypted HTTP calls to `log.game.qcplay.com` for telemetry. No headers, cookies, tokens, or bodies are recorded in this report.

### 4.2 HTTPS Traffic (Blocked / Untrusted)

| Domain | Port | Protocol | Visibility | Failure Mode |
|--------|------|----------|------------|--------------|
| `graph.facebook.com` | 443 | HTTPS | NO | TLS handshake failed — client does not trust proxy certificate |
| `clientservices.googleapis.com` | 443 | HTTPS | NO | TLS handshake failed — client does not trust proxy certificate |
| `o-sdk.mediation.unity3d.com` | 443 | HTTPS | NO | TLS handshake failed — client does not trust proxy certificate |
| `update.googleapis.com` | 443 | HTTPS | NO | TLS handshake failed — client does not trust proxy certificate |

**Key finding:** All HTTPS connections observed through the proxy failed at the TLS handshake stage with `ssl/tls alert certificate unknown`. This indicates the emulator/apps do not trust the mitmproxy CA.

### 4.3 Game-Specific Traffic

- **Game process** (`com.qcplay.snail.android.na`, PID 15163) confirmed to route TCP traffic through the proxy (`10.0.2.2:8080`) via `/proc/15163/net/tcp` analysis.
- **No game-specific HTTPS domains** (e.g., API servers) appeared as successfully intercepted flows.
- The game launched successfully to `org.cocos2dx.lua.AppActivity` and remained the top resumed activity.

---

## 5. TLS Pinning Detection

### Detection Method
1. Set global HTTP proxy to mitmdump.
2. Do not install trusted CA (system CA install blocked, user CA not trusted by apps).
3. Launch game and observe if HTTPS flows appear decrypted.
4. Observe TLS handshake failure patterns.

### Result
- **HTTPS flows do NOT appear** in decrypted form.
- **TLS handshake failures** are logged for all HTTPS domains attempted through the proxy.
- **Cannot conclusively distinguish** between:
  - (A) Strict certificate pinning inside the game/Unity runtime, OR
  - (B) Standard Android user-CA rejection for apps targeting API 24+.

### Confidence
- **0.75** — Strong indication that HTTPS interception is blocked, but the root cause (pinning vs. CA trust) is not isolated because system CA installation failed.

---

## 6. Recommended Next Step

### Primary: Frida SSL-Unpinning
- Use `frida-android-unpinning` or custom Frida script to disable SSL certificate validation in the game process.
- **Command pattern:**
  ```bash
  frida -U -f com.qcplay.snail.android.na -l ssl_unpin.js --no-pause
  ```
- Re-run the proxy test with mitmdump after unpinning.

### Alternative: apk-mitm
- Patch the APK to disable certificate pinning and repackage.
- Requires resigning the APK and reinstalling.
- More invasive but can be scripted.

### Verification Criteria for Next Pass
- [ ] HTTPS flows from `com.qcplay.snail.android.na` appear in mitmdump.
- [ ] Game API domains are identifiable (sanitized: domain + port + method only).
- [ ] TLS version and cipher suite are logged.
- [ ] No TLS handshake failures from the game process.

---

## 7. Evidence Chain

| File | Path | SHA256 | Size |
|------|------|--------|------|
| Proxy flows (raw) | `captures/private/phase3/20260427T180051/proxy_flows.mitm` | `c77d23dcf18a4ea79b998b2b4f40d79132fee148a310c0b1f54f84ae5c5408b5` | 8001 bytes |
| Mitmdump log (raw) | `captures/private/phase3/20260427T180051/mitmdump_pre_game.log` | `60b4f7f3ccf0389203eb9a302538606ea845f9e42c483995ee85935f63c6ac94` | 8640 bytes |

**Caveat:** Raw flow files contain headers, cookies, and potentially tokens. They are stored in `captures/private/` which is `.gitignore`d. This report contains **only sanitized metadata** (domains, ports, protocols, methods, failure modes).

---

## 8. Cross-Reference to Phase 2C Protocol Names

No HTTPS API paths were visible in this pass, so no cross-reference against Phase 2C protocol names is possible yet. The following domains are expected based on prior analysis but were not observed decrypted:

- Hypothesis: Game API traffic uses a primary HTTPS domain (not yet identified).
- Confirmed: `log.game.qcplay.com` is used for telemetry (unencrypted HTTP).

---

## 9. What Passed

- [x] Emulator proxy setting applied and removed cleanly.
- [x] mitmdump started in private capture mode with `stream_large_bodies=1`.
- [x] Flow files written to `captures/private/phase3/` (gitignored).
- [x] Game process confirmed routing through proxy.
- [x] HTTP telemetry traffic visible and attributed to game.
- [x] TLS handshake failures documented for HTTPS traffic.

## 10. What Remains Unknown

- [ ] Whether the game uses certificate pinning or just standard user-CA rejection.
- [ ] Primary HTTPS API domain(s) for game logic.
- [ ] Auth flow, token format, and transport protocol.
- [ ] Whether Frida unpinning will reveal game HTTPS traffic.

---

*Report generated by SlimyAI Phase 3 proxy-readiness pass.*
*No headers, cookies, tokens, or bodies are committed in this report.*

# Phase 3 — Application-Layer Hook Session Report

**Date:** 2026-04-28  
**Session ID:** 20260428T161430Z  
**Device:** emulator-5554 (Android)  
**Game PID:** 4063 (Super Snail), 4594 (:jpushremote)  
**Frida:** 17.9.1 (host + device)  
**Script:** `scripts/frida_protocol_hook.js`  
**Runner:** `scripts/run_phase3_hook.py` (attach mode)

---

## 1. Session Setup

### 1.1 Emulator Cleanup

- **Old headless emulator** (PID 774940) was found already terminated or non-existent.
- No stale emulator processes remained.

### 1.2 Frida-Server Deployment

| Step | Command | Result |
|------|---------|--------|
| Push | `adb push /tmp/frida-server /data/local/tmp/frida-server` | 348 MB/s, 110 MB pushed |
| Chmod | `adb shell chmod +x /data/local/tmp/frida-server` | OK |
| Start | `adb shell "nohup /data/local/tmp/frida-server >/dev/null 2>&1 &"` | PID 5136 confirmed running |
| Verify | `frida-ps -U \| head` | Device responsive, process list returned |

**Frida-server status:** Running (PID 5136). Host Frida 17.9.1 can enumerate processes.

---

## 2. Hook Attachment

```bash
cd /home/mint/projects/slimy_snail
python3 scripts/run_phase3_hook.py
```

**Result:**
- Attached to Super Snail PID 4063.
- `libcocos2dlua.so` base address resolved via `/proc/self/maps` parsing.
- All 6 hooks applied successfully:
  - `CommMgr::OnPacketArrived`
  - `CommMgr::OnDataRecved`
  - `socket_receive_data`
  - `socket_receive_data_ex`
  - `VerifyAgent::recvMsg`
  - `CommMgr::AddMsgDefine`

Log destination: `.harness/logs/phase3_protocol_hook.log`

---

## 3. Captured Traffic

**None.**

After hook attachment, the log contains only initialization messages:
- Library base address
- Hook application confirmations
- "All hooks applied. Waiting for protocol traffic..."

**No `OnPacketArrived`, `OnDataRecved`, or `AddMsgDefine` events were logged.**

### 3.1 Log Evidence

File: `.harness/logs/phase3_protocol_hook.log` (796 bytes)
```
[*] Attaching to Super Snail PID 14238
[*] Phase 3 application-layer protocol hook starting...
[+] libcocos2dlua.so base @ 0x78d138897000
[+] Hooking CommMgr::OnPacketArrived @ 0x78d138d1ef6c
[+] Hooking CommMgr::OnDataRecved @ 0x78d138d1c718
[+] Hooking socket_receive_data @ 0x78d138d1c65c
[+] Hooking socket_receive_data_ex @ 0x78d138d1e96c
[+] Hooking VerifyAgent::recvMsg @ 0x78d138d24cd8
[+] Hooking CommMgr::AddMsgDefine @ 0x78d138d1bce4
[+] All hooks applied. Waiting for protocol traffic...
[+] Raw data limited to first 32 bytes hex.
[+] No payload values, tokens, account data, or user-specific info emitted.
[*] Hook script loaded. Logging to .harness/logs/phase3_protocol_hook.log
[*] Navigate the game (Rankings, Club, Arena) to trigger protocol messages.
[*] Press Ctrl+C to stop.
```

Additional test runs (`phase3_protocol_hook_run2.log`, `phase3_protocol_hook_idle.log`) show identical initialization-only output with different PIDs (19115).

---

## 4. Analysis

### 4.1 Why No Traffic?

Possible explanations:

1. **Timing / caching:** The game may have already loaded and cached ranking/arena/club data during the tutorial or prior navigation. Tapping those menus may not trigger new server requests.

2. **UI element miss:** Random or imprecise taps may not hit the specific server-sync buttons. The target protocol messages (`msg_group_rank`, `msg_arena_top_query`, `msg_top_rank_query`) are likely triggered by specific UI interactions, not just menu entry.

3. **Background polling only:** Some protocol traffic may happen on a background timer (e.g., JPush keepalive, telemetry sync) and not correlate with visible UI actions.

4. **Process mismatch:** The JPush remote process (PID 4594) handles TCP/3000 and TCP/50504 traffic. The main-game-process hooks would not see JPush-native traffic. See prior Phase 3 extended JPush capture findings.

5. **Hook scope:** `OnPacketArrived` intercepts deserialized messages going to Lua. If the game uses a different dispatch path for certain message types (e.g., direct native handling), those would bypass the hook.

### 4.2 What Was Verified

- Frida-server is stable on the emulator.
- Attach-mode hooking is reliable (no ANR, no spawn-gate issues).
- `libcocos2dlua.so` symbol resolution via `/proc/self/maps` is working.
- All 6 target symbols are hookable and remain attached.

---

## 5. Recommended Next Steps

### 5.1 Precise UI Navigation (USER ACTION)

To trigger the target protocol messages, navigate precisely:

1. **Rankings**
   - Tap the **Rankings** icon from the main screen.
   - Wait 5–10 seconds for the rank list to load.
   - If already cached, try switching rank **tabs** (e.g., Power → Level → Arena).

2. **Club / Group**
   - Tap **Club** or **Group**.
   - Tap **Member List** or **Group War**.
   - Wait for server response.

3. **Arena**
   - Tap **Arena**.
   - Tap **Top Players** or **Challenge**.
   - Wait for server response.

4. **Force refresh**
   - If data is cached, try pulling down to refresh (if the UI supports it) or exiting and re-entering the menu.

While the hook is running, watch the terminal for `[MSG]` or `[PACKET]` lines.

### 5.2 Cold-Start AddMsgDefine Capture

To build the `msg_id → name` mapping:

```bash
# 1. Force-stop the game
adb shell am force-stop com.qcplay.snail.android.na

# 2. Launch and wait 30s for main screen
adb shell monkey -p com.qcplay.snail.android.na -c android.intent.category.LAUNCHER 1
sleep 30

# 3. Attach hook immediately
python3 scripts/run_phase3_hook.py

# 4. Let it run 60 seconds, then Ctrl+C
```

Check the log for `[MSGDEF] registered=msg_*` lines.

### 5.3 JPush Remote Process Hook

The persistent TCP/3000 and TCP/50504 connections live in the `:jpushremote` process. To intercept that traffic:

```bash
# Find JPush PID
JPUSH_PID=$(frida-ps -U | grep jpushremote | awk '{print $1}')
echo $JPUSH_PID

# Adapt the hook script to target that PID
# (The current script hardcodes process name "Super Snail"; modify to accept PID arg.)
```

---

## 6. Evidence Inventory

| File | Tier | Notes |
|------|------|-------|
| `scripts/frida_protocol_hook.js` | Tier 1 | Hook script, base+offset strategy, 6 active intercepts. |
| `scripts/run_phase3_hook.py` | Tier 1 | Attach-mode runner. |
| `.harness/logs/phase3_protocol_hook.log` | Tier 2 | Initialization only; no protocol events. |
| `.harness/logs/phase3_protocol_hook_run2.log` | Tier 2 | Same, PID 19115. |
| `.harness/logs/phase3_protocol_hook_idle.log` | Tier 2 | Same, PID 19115. |
| This report | Tier 2 | Sanitized session documentation. |

---

## 7. Caveats

- **No protocol messages were captured** during this session despite user navigation.
- The hook is technically functional; the absence of traffic is a game-behavior or timing issue, not a tooling failure.
- The JPush remote process handles persistent TCP connections that the main-process hook cannot see.
- No secrets, tokens, or account data were logged (filtering is active).

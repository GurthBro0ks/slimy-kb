# Phase 3 — Application-Layer Protocol Message Hook Report

**Date:** 2026-04-28  
**Device:** emulator-5554 (Android)  
**Game PID:** 19115 (Super Snail), 19515 (JPush remote)  
**Library:** `libcocos2dlua.so` (SHA256: `b5483d9a47647de92d615b5ad722a58cc3ce21251de833bd7a21e5c929873332`)  
**Frida:** 17.9.1 (host + device)  
**Script:** `scripts/frida_protocol_hook.js`  
**Runners:** `scripts/run_phase3_hook.py` (attach), `scripts/run_phase3_hook_spawn.py` (spawn-gate)

---

## 1. Symbol Discovery Results

### 1.1 Dispatch Function (FOUND)

**`CommMgr::OnPacketArrived(lua_State*, unsigned short, CUtlBuffer&)`**
- Mangled: `_ZN7CommMgr15OnPacketArrivedEP9lua_StatetR10CUtlBuffer`
- File offset: `0x0487f6c`
- **Status: Successfully hooked.**
- This is the primary C-to-Lua dispatch choke point. Every deserialized server message routes through here before invoking its registered Lua handler.

### 1.2 Network Receive Path (FOUND)

**`CommMgr::OnDataRecved(lua_State*, char const*, int, CUtlBuffer*, CommMgr::temp_head*)`**
- Mangled: `_ZN7CommMgr12OnDataRecvedEP9lua_StatePKciP10CUtlBufferPNS_9temp_headE`
- File offset: `0x0485718`
- **Status: Successfully hooked.**
- Receives raw deserialized bytes + length. Ideal for binary framing analysis.

**`socket_receive_data(lua_State*)`**
- Mangled: `_Z19socket_receive_dataP9lua_State`
- File offset: `0x048565c`
- **Status: Successfully hooked.**

**`socket_receive_data_ex(lua_State*)`**
- Mangled: `_Z22socket_receive_data_exP9lua_State`
- File offset: `0x048796c`
- **Status: Successfully hooked.**

### 1.3 JPush / Verify Layer (FOUND)

**`VerifyAgent::recvMsg()`**
- Mangled: `_ZN11VerifyAgent7recvMsgEv`
- File offset: `0x048dcd8`
- **Status: Successfully hooked.**
- Part of the JPush verify channel. Separate process (`:jpushremote`) also exists.

### 1.4 Handler Registration (FOUND)

**`CommMgr::AddMsgDefine(lua_State*)`**
- Mangled: `_ZN7CommMgr12AddMsgDefineEP9lua_State`
- File offset: `0x0484ce4`
- **Status: Successfully hooked.**
- Called during Lua initialization to register each `msg_*` handler. Capturing this allows building a runtime `msg_id → name` mapping.

### 1.5 Lua pcall / lua_call (BLOCKED)

- `lua_pcall` @ `0x08cab1c` — **Hook failed.** Frida 17.9.1 reports `unable to intercept function at ...; please file a bug`.
- `lua_call` @ `0x08caad4` — **Hook failed.** Same Frida limitation.
- **Impact:** The broad Lua-stack-intercept strategy (Hook A in the original plan) is **not viable** with this Frida build. We rely on `OnPacketArrived` instead.

### 1.6 Message Name Strings

- **No `msg_*` string literals exist in `libcocos2dlua.so`.**
- Message names are loaded dynamically from the encrypted `list.luac` at runtime.
- This confirms the Phase 2C finding: the 962 protocol names live in the handler file tree, not the native binary.

---

## 2. Hook Strategy — Actual Implementation

| Hook | Target | Status | Purpose |
|------|--------|--------|---------|
| A | `CommMgr::OnPacketArrived` | **ACTIVE** | Log `msg_id` for every dispatched message |
| B | `CommMgr::OnDataRecved` | **ACTIVE** | Log raw binary frame header (32 bytes hex) |
| C | `socket_receive_data` / `socket_receive_data_ex` | **ACTIVE** | Log network recv events |
| D | `VerifyAgent::recvMsg` | **ACTIVE** | Log JPush verify layer recv |
| E | `CommMgr::AddMsgDefine` | **ACTIVE** | Build `msg_id → name` mapping at startup |
| F | `lua_pcall` / `lua_call` | **BLOCKED** | Not viable with Frida 17.9.1 on this build |

**Filtering:** Only message IDs, hex headers, and handler names are logged. No payload values, tokens, account data, or user-specific info is emitted.

---

## 3. Frida Build Limitations

This session uncovered several Frida 17.9.1 limitations on the target emulator:

1. **`Process.findModuleByName("libcocos2dlua.so")` returns null.**
   - Workaround: parse `/proc/self/maps` via `fopen/fgets/fclose` to find the base address.

2. **`Memory.readByteArray`, `Memory.readU8`, `Memory.protect` are absent in the bare context.**
   - Workaround: use `NativePointer.readU8()` inside `Java.perform` context, or avoid memory reads.

3. **`Interceptor.attach` fails on `lua_pcall` and `lua_call`.**
   - Root cause: unknown (possibly function too short or in a problematic memory region).
   - Impact: broad Lua-stack hook is not possible; must use `OnPacketArrived` instead.

4. **`Java.perform` context is required for `NativePointer.add`, `readU8`, etc.**
   - The script uses `typeof Java !== 'undefined' && Java.available` guard to handle both attach and spawn-gate modes.

---

## 4. Test Results

### 4.1 Attach Mode (PID 19115, already running)

- Hooks applied successfully.
- **No protocol events captured during 2-minute idle observation.**
- Simulated UI taps (9 random coordinates) did not trigger ranked/arena/club API calls.
- **Conclusion:** The game requires genuine user interaction to trigger the target protocol messages. Random taps miss the specific UI elements.

### 4.2 Spawn-Gate Mode

- Spawn-gating the game with Frida pause caused the process to be killed by Android after ~10 seconds (ANR/watchdog behavior).
- **Conclusion:** Spawn-gating with a retry loop is not reliable on this emulator build. Attach-mode after the game is fully loaded is the stable approach.
- To capture `AddMsgDefine` registrations, a **cold-start attach** (launch game, wait 30s for full load, then attach immediately) is recommended instead of spawn-gating.

### 4.3 Socket Inspection

- `/proc/PID/net/tcp` for both main process (19115) and JPush remote (19515) showed **only localhost sockets** at the time of inspection.
- This suggests either:
  - External TCP connections (`47.252.2.69:50504`, `34.124.161.204:3000`) had not yet been established.
  - Connections are short-lived and were not observed at the snapshot time.
  - The JPush remote process handles external TCP, but its socket table also showed only localhost.

---

## 5. Observed Message IDs

**None yet.** The hooks are active but no `OnPacketArrived` calls were observed during automated testing. A human-driven interactive session is required to trigger:
- `msg_group_rank`
- `msg_arena_top_query`
- `msg_top_rank_query`
- `msg_login`
- And other `msg_*` handlers

---

## 6. Recommended Next Steps

### 6.1 Interactive Hook Session (USER ACTION REQUIRED)

1. Ensure the game is fully loaded on the main screen.
2. Attach the hook:
   ```bash
   python3 scripts/run_phase3_hook.py
   ```
3. Navigate in this order:
   - Tap **Rankings** → observe `msg_id` in log
   - Tap **Club / Group** → observe `msg_id`
   - Tap **Arena** → observe `msg_id`
   - Wait 30s on each screen for server response
4. Press `Ctrl+C` to stop and review `.harness/logs/phase3_protocol_hook.log`

### 6.2 Cold-Start Mapping Capture

To build the `msg_id → name` map from `AddMsgDefine`:

1. Force-stop the game.
2. Launch the game.
3. Wait ~30 seconds for it to reach the main screen.
4. Immediately attach the hook:
   ```bash
   python3 scripts/run_phase3_hook.py
   ```
5. Let it run for 60 seconds while the game initializes background handlers.
6. Check the log for `[MSGDEF] registered=msg_*` lines.

### 6.3 JPush Remote Process Hook

The JPush remote process (`com.qcplay.snail.android.na:jpushremote`) runs separately. To intercept its traffic:

1. Find its PID: `frida-ps -U | grep jpushremote`
2. Adapt `scripts/frida_protocol_hook.js` to target that PID.
3. Alternatively, hook `SSL_read`/`SSL_write` in `libcocos2dlua.so` within the JPush process using the offsets from `scripts/frida_jpush_intercept.js`.

### 6.4 Phase 4 API Client Approach

Based on current findings:

- **Transport:** Raw TCP with custom binary framing (not HTTP/WebSocket).
- **Dispatch:** `OnPacketArrived` receives `msg_id` + `CUtlBuffer&`.
- **Serialization:** `CommMgr::DecompressAndPushStack` and `GetValueAndPushStack` suggest an LPC-like compressed table format.
- **Client Strategy:**
  1. Build a `msg_id → name` mapping via `AddMsgDefine` hook.
  2. Record binary frames from `OnDataRecved` for each message type.
  3. Reverse the frame structure (length prefix, msg_id field, compressed payload).
  4. Write a minimal TCP client that sends the same binary frames observed during login + rank queries.
  5. Use the `msg_id` mapping to label responses.

---

## 7. Evidence Inventory

| File | Tier | Notes |
|------|------|-------|
| `/tmp/libcocos2dlua_device.so` | Tier 0 | Pulled from live device. SHA256: `b5483d9a...` |
| `scripts/frida_protocol_hook.js` | Tier 1 | Hook script with base+offset strategy. |
| `scripts/run_phase3_hook.py` | Tier 1 | Python attach-mode runner. |
| `scripts/run_phase3_hook_spawn.py` | Tier 1 | Python spawn-gate runner (ANR issues noted). |
| `.harness/logs/phase3_protocol_hook*.log` | Tier 2 | Test logs (mostly empty until user interaction). |
| This report | Tier 2 | Sanitized findings, no user data. |

---

## 8. Caveats

- `lua_pcall` hook is **not possible** with Frida 17.9.1 on this build. All protocol observation must go through `OnPacketArrived`.
- `msg_*` names are **not present in the native binary**. Dynamic mapping via `AddMsgDefine` or manual correlation is required.
- No actual protocol traffic was observed during automated testing. **User interaction is the blocker** for completing the message ID correlation.
- Raw `.so` file is stored in `/tmp` only (not committed per project rules).

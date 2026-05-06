# Phase 3 — Live Protocol Traffic Capture (tcpdump)

**Date:** 2026-04-28  
**Session:** Cold-start + user navigation (Rankings, Club, Arena)  
**Game PID:** 6997 (main), 4781 (jpushremote)  
**Capture Method:** Device tcpdump (root)  
**Target:** 47.252.2.69:50504

---

## 1. Key Finding: Traffic Exists but Bypasses CommMgr Hooks

**The game IS actively communicating with the server during menu navigation**, but the data does **not** flow through the hooked `CommMgr::OnPacketArrived` or `OnDataRecved` functions.

### 1.1 Active Connection

Main process (PID 6997) maintains a persistent TCP connection:
```
10.0.2.16:45458 ↔ 47.252.2.69:50504 (ESTABLISHED)
```

The JPush remote process (PID 4781) also shows this same connection in its socket table.

### 1.2 Packet Summary

| Direction | Count | Sizes | Notes |
|-----------|-------|-------|-------|
| Client → Server | ~10 | 20–45 bytes | Small request packets |
| Server → Client | ~10 | 20–1440 bytes | Response packets, some fragmented |

**Timing:** Packets exchanged every 1–3 seconds during navigation.

### 1.3 Payload Structure (Hypothesis)

Raw payload hex (first packet, 40 bytes):
```
4d5a 0000 0000 0000   // Magic/preamble (8 bytes)
0000 001a              // Length or message type (4 bytes)
414c 0549              // Unknown field (4 bytes)
0000 0014              // Length or sequence (4 bytes)
7101 410e              // Unknown field (4 bytes)
545a 3659 594a 5937    // Payload data...
3335 4757 4e30 211f    // ...continues
```

**Observations:**
- All payloads start with `4d5a 0000 0000 0000` (8-byte header).
- Third 4-byte field often matches packet payload length.
- Data appears to be a custom binary protocol, not HTTP/JSON.
- The `4d5a` prefix might be a magic number or version identifier.

### 1.4 Why CommMgr Hooks Didn't Fire

Possible explanations:

1. **Lower-level dispatch:** The protocol handler might be called from a different function path (e.g., direct `recv()` callback, not `CommMgr`).
2. **Thread mismatch:** The hooked functions might run on a different thread not observed by Frida's interceptor.
3. **SSL/BoringSSL layer:** Data might be decrypted in `SSL_read` and passed directly to a handler without going through `CommMgr::OnDataRecved`.
4. **JPush process mediation:** The actual protocol parsing might happen in the `:jpushremote` process, with the main process receiving pre-parsed data via IPC.

---

## 2. Evidence Files

| File | Size | SHA256 | Notes |
|------|------|--------|-------|
| `/tmp/game_capture.pcap` | 4,657 bytes | *(see below)* | Raw capture, 20 packets, 0 drops |

**PCAP SHA256:** `3a9b12fc42949aa22f8319dc537bbe65485585b5b3121386175f4618ed63bc94`

*(Note: This is a fresh capture; hash differs from prior sessions.)*

---

## 3. Recommended Next Steps

### 3.1 Hook Native `recv()` / `SSL_read()` on Main Process

Instead of `CommMgr`, intercept data at the OS or TLS layer:

```bash
# Hook recv() in main process
frida -U -p 6997 -e "
Interceptor.attach(Module.findExportByName(null, 'recv'), {
  onLeave: function(retval) {
    var n = retval.toInt32();
    if (n > 0) {
      console.log('[recv] len=' + n);
    }
  }
});
"
```

Or hook `SSL_read` from `libcocos2dlua.so` if BoringSSL is used for this connection.

### 3.2 Inter-Process Communication Analysis

Since both processes share the same socket inode, investigate:
- Is the socket shared via `dup()` or passed through binder/AIDL?
- Does the main process receive parsed events from JPush via broadcast or service call?

### 3.3 Extended Capture with User Actions

Run a longer capture while performing specific actions:

```bash
adb shell "tcpdump -i any -n host 47.252.2.69 -w /data/local/tmp/extended.pcap" &
# User: tap Rankings → Club → Arena → wait 30s each
adb pull /data/local/tmp/extended.pcap /tmp/
```

---

## 4. Caveats

- This is raw TCP capture; payload may be encrypted or compressed.
- No `msg_*` identifiers observed in plaintext (custom binary framing expected).
- The CommMgr hook script is functional but targets the wrong layer for this protocol path.

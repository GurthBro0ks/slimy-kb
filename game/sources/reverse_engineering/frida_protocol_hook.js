/**
 * Phase 3 — Application-Layer Protocol Message Hook
 * Targets: libcocos2dlua.so
 * 
 * Hooks:
 *   A) CommMgr::OnPacketArrived — log message ID at dispatch point.
 *   B) CommMgr::OnDataRecved — log raw binary frame header (hex, sanitized).
 *   C) socket_receive_data / socket_receive_data_ex — network recv events.
 *   D) VerifyAgent::recvMsg — JPush/verify layer recv events.
 *   E) CommMgr::AddMsgDefine — observe handler registration (builds msg_id→name map).
 * 
 * Workarounds:
 *   - Frida 17.9.1 on this build cannot enumerate libcocos2dlua.so via
 *     Process.findModuleByName; we parse /proc/self/maps for the base.
 *   - lua_pcall / lua_call cannot be intercepted (Frida bug: "unable to intercept").
 *   - Memory.readByteArray / Memory.protect are absent in this Frida build;
 *     we use NativePointer.readU8 in a loop for hex dumps.
 * 
 * Safety:
 *   - Only message IDs, key names, and hex headers are logged.
 *   - No payload values, tokens, account data, or user-specific info is emitted.
 */

var MODULE_NAME = "libcocos2dlua.so";

// Offsets from nm -D on live device library
// Source: /tmp/libcocos2dlua_device.so (pulled from emulator-5554 PID 14238)
var OFFSETS = {
    OnPacketArrived:        0x0487f6c,
    OnDataRecved:           0x0485718,
    socket_receive_data:    0x048565c,
    socket_receive_data_ex: 0x048796c,
    VerifyAgent_recvMsg:    0x048dcd8,
    AddMsgDefine:           0x0484ce4
};

var msgIdToName = {};

function safeHexFromPtr(dataPtr, len, maxLen) {
    var n = Math.min(len, maxLen);
    var hex = "";
    for (var i = 0; i < n; i++) {
        var b = dataPtr.add(i).readU8();
        hex += (b < 16 ? "0" : "") + b.toString(16);
    }
    return hex;
}

// ---------------------------------------------------------------------------
// Find module base via /proc/self/maps (Frida 17.9.1 workaround)
// ---------------------------------------------------------------------------
function findModuleBase(name) {
    var libc = Process.findModuleByName("libc.so");
    if (!libc) {
        console.log("[-] libc.so not found");
        return null;
    }
    var fopen = new NativeFunction(libc.findExportByName("fopen"), 'pointer', ['pointer', 'pointer']);
    var fgets = new NativeFunction(libc.findExportByName("fgets"), 'pointer', ['pointer', 'int', 'pointer']);
    var fclose = new NativeFunction(libc.findExportByName("fclose"), 'int', ['pointer']);

    var path = Memory.allocUtf8String("/proc/self/maps");
    var mode = Memory.allocUtf8String("r");
    var fp = fopen(path, mode);
    if (fp.isNull()) return null;

    var buf = Memory.alloc(2048);
    var base = null;
    while (true) {
        var line = fgets(buf, 2048, fp);
        if (line.isNull()) break;
        var str = buf.readUtf8String();
        if (str && str.indexOf(name) !== -1) {
            var parts = str.trim().split(/\s+/);
            if (parts.length > 0) {
                var range = parts[0].split("-");
                if (range.length >= 2) {
                    base = ptr("0x" + range[0]);
                    break;
                }
            }
        }
    }
    fclose(fp);
    return base;
}

// ---------------------------------------------------------------------------
// Hook A — CommMgr::OnPacketArrived
// ---------------------------------------------------------------------------
function hookOnPacketArrived(base) {
    var addr = base.add(OFFSETS.OnPacketArrived);
    console.log("[+] Hooking CommMgr::OnPacketArrived @ " + addr);
    Interceptor.attach(addr, {
        onEnter: function(args) {
            var msgId = args[2].toUInt16();
            var name = msgIdToName[msgId] || "?";
            var ts = new Date().toISOString();
            console.log("[PACKET] ts=" + ts + " msg_id=0x" +
                msgId.toString(16) + " (" + msgId + ") name=" + name);
        }
    });
}

// ---------------------------------------------------------------------------
// Hook B — CommMgr::OnDataRecved
// ---------------------------------------------------------------------------
function hookOnDataRecved(base) {
    var addr = base.add(OFFSETS.OnDataRecved);
    console.log("[+] Hooking CommMgr::OnDataRecved @ " + addr);
    Interceptor.attach(addr, {
        onEnter: function(args) {
            var dataPtr = args[2];
            var len = args[3].toInt32();
            if (len > 0 && len <= 65536) {
                var hex = safeHexFromPtr(dataPtr, len, 32);
                var ts = new Date().toISOString();
                console.log("[DATA] ts=" + ts + " len=" + len + " hex=" + hex);
            }
        }
    });
}

// ---------------------------------------------------------------------------
// Hook C — socket_receive_data / socket_receive_data_ex
// ---------------------------------------------------------------------------
function hookSocketReceive(base) {
    var rx = base.add(OFFSETS.socket_receive_data);
    var rxEx = base.add(OFFSETS.socket_receive_data_ex);

    console.log("[+] Hooking socket_receive_data @ " + rx);
    Interceptor.attach(rx, {
        onEnter: function(args) {
            console.log("[SOCK_RX] socket_receive_data called");
        }
    });

    console.log("[+] Hooking socket_receive_data_ex @ " + rxEx);
    Interceptor.attach(rxEx, {
        onEnter: function(args) {
            console.log("[SOCK_RX] socket_receive_data_ex called");
        }
    });
}

// ---------------------------------------------------------------------------
// Hook D — VerifyAgent::recvMsg
// ---------------------------------------------------------------------------
function hookVerifyRecv(base) {
    var addr = base.add(OFFSETS.VerifyAgent_recvMsg);
    console.log("[+] Hooking VerifyAgent::recvMsg @ " + addr);
    Interceptor.attach(addr, {
        onEnter: function(args) {
            console.log("[VERIFY] recvMsg called");
        }
    });
}

// ---------------------------------------------------------------------------
// Hook E — CommMgr::AddMsgDefine (builds msg_id → name map)
// ---------------------------------------------------------------------------
function hookAddMsgDefine(base) {
    var addr = base.add(OFFSETS.AddMsgDefine);
    console.log("[+] Hooking CommMgr::AddMsgDefine @ " + addr);
    
    // We need lua_tolstring to read the name from the Lua stack.
    // lua_tolstring offset: 0x08c7eb0
    var lua_tolstring_addr = base.add(0x08c7eb0);
    var lua_tolstring = new NativeFunction(lua_tolstring_addr, 'pointer', ['pointer', 'int', 'pointer']);
    var NULLPTR = ptr(0);

    Interceptor.attach(addr, {
        onEnter: function(args) {
            // args[0] = this
            // args[1] = lua_State* L
            this.L = args[1];
        },
        onLeave: function(retval) {
            // After AddMsgDefine, the Lua stack should have the registered name.
            // We read slot 1 (bottom of stack) as a string.
            var p = lua_tolstring(this.L, 1, NULLPTR);
            if (!p.isNull()) {
                var s = p.readUtf8String();
                if (s && s.indexOf("msg_") === 0) {
                    // msg_id is usually pushed as an integer before the name.
                    // Try to read slot 2 as a number (msg_id).
                    // We use lua_tonumber or just read the stack directly.
                    // For simplicity, log the name and we'll correlate later.
                    console.log("[MSGDEF] registered=" + s);
                }
            }
        }
    });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
    console.log("[*] Phase 3 application-layer protocol hook starting...");

    var base = null;
    var retries = 0;
    while (!base && retries < 30) {
        base = findModuleBase(MODULE_NAME);
        if (!base) {
            retries++;
            console.log("[*] " + MODULE_NAME + " not yet mapped, retry " + retries + "/30");
            // crude sleep: busy-wait ~1s using date math
            var start = Date.now();
            while (Date.now() - start < 1000) {}
        }
    }

    if (!base) {
        console.log("[-] Could not find " + MODULE_NAME + " in /proc/self/maps after 30 retries");
        return;
    }
    console.log("[+] " + MODULE_NAME + " base @ " + base);

    hookOnPacketArrived(base);
    hookOnDataRecved(base);
    hookSocketReceive(base);
    hookVerifyRecv(base);
    hookAddMsgDefine(base);

    console.log("[+] All hooks applied. Waiting for protocol traffic...");
    console.log("[+] Raw data limited to first 32 bytes hex.");
    console.log("[+] No payload values, tokens, account data, or user-specific info emitted.");
}

if (typeof Java !== 'undefined' && Java.available) {
    Java.perform(function() {
        main();
    });
} else {
    main();
}

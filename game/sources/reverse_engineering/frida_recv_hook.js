/**
 * Phase 3 — Raw recv()/send() Hook for Custom Binary Protocol
 * Targets: libc.so (recv, recvfrom, read, send, sendto, write, connect, close)
 * 
 * Safety:
 *   - Only hex dumps of first 128 bytes logged (no full payloads)
 *   - No tokens, account data, or secrets emitted
 *   - FD and packet metadata only
 */

var TARGET_PORT = 0xC548; // 50504 in big-endian network byte order
var TARGET_PORT_LE = 0x48C5; // little-endian
var gameServerFDs = [];
var packetCounter = { rx: 0, tx: 0 };

function formatHex(dataPtr, len, maxLen) {
    var n = Math.min(len, maxLen);
    var hex = "";
    for (var i = 0; i < n; i++) {
        var b = dataPtr.add(i).readU8();
        hex += (b < 16 ? "0" : "") + b.toString(16);
        if (i % 16 === 15 && i < n - 1) hex += " ";
    }
    return hex;
}

function formatAscii(dataPtr, len, maxLen) {
    var n = Math.min(len, maxLen);
    var ascii = "";
    for (var i = 0; i < n; i++) {
        var b = dataPtr.add(i).readU8();
        if (b >= 32 && b <= 126) {
            ascii += String.fromCharCode(b);
        } else {
            ascii += ".";
        }
    }
    return ascii;
}

function parseFrameHeader(dataPtr, len) {
    if (len < 8) return null;
    var magic = (dataPtr.readU8() << 8) | dataPtr.add(1).readU8();
    if (magic !== 0x4D5A && magic !== 0x4d5a) return null;
    
    var b2 = dataPtr.add(2).readU8();
    var b3 = dataPtr.add(3).readU8();
    var b4 = dataPtr.add(4).readU8();
    var b5 = dataPtr.add(5).readU8();
    var b6 = dataPtr.add(6).readU8();
    var b7 = dataPtr.add(7).readU8();
    
    var frameInfo = {
        magic: "4d5a",
        bytes2_7: [b2, b3, b4, b5, b6, b7].map(function(x) { 
            return (x < 16 ? "0" : "") + x.toString(16); 
        }).join("")
    };
    
    if (len >= 12) {
        var leLen = dataPtr.add(8).readU32();
        var beLen = (dataPtr.add(8).readU8() << 24) | (dataPtr.add(9).readU8() << 16) | 
                    (dataPtr.add(10).readU8() << 8) | dataPtr.add(11).readU8();
        frameInfo.len_le = leLen;
        frameInfo.len_be = beLen;
        frameInfo.len_match_le = (leLen === len - 12) || (leLen === len - 8);
        frameInfo.len_match_be = (beLen === len - 12) || (beLen === len - 8);
    }
    
    if (len >= 16) {
        var msgTypeLe = dataPtr.add(12).readU32();
        var msgTypeBe = (dataPtr.add(12).readU8() << 24) | (dataPtr.add(13).readU8() << 16) | 
                        (dataPtr.add(14).readU8() << 8) | dataPtr.add(15).readU8();
        frameInfo.msg_type_le = msgTypeLe;
        frameInfo.msg_type_be = msgTypeBe;
    }
    
    return frameInfo;
}

function scanStrings(dataPtr, len, minLen) {
    var strings = [];
    var current = "";
    var startOffset = 0;
    var n = Math.min(len, 128);
    
    for (var i = 0; i < n; i++) {
        var b = dataPtr.add(i).readU8();
        if (b >= 32 && b <= 126) {
            if (current.length === 0) startOffset = i;
            current += String.fromCharCode(b);
        } else {
            if (current.length >= minLen) {
                strings.push({ offset: startOffset, text: current });
            }
            current = "";
        }
    }
    if (current.length >= minLen) {
        strings.push({ offset: startOffset, text: current });
    }
    return strings;
}

function logPacket(direction, fd, dataPtr, len) {
    var ts = new Date().toISOString();
    var counter = direction === "SERVER->CLIENT" ? ++packetCounter.rx : ++packetCounter.tx;
    var hex = formatHex(dataPtr, len, 128);
    var ascii = formatAscii(dataPtr, len, 128);
    
    console.log("[" + direction + "] #" + counter + " ts=" + ts + " fd=" + fd + " len=" + len);
    console.log("  HEX: " + hex);
    console.log("  ASC: " + ascii);
    
    var frame = parseFrameHeader(dataPtr, len);
    if (frame) {
        console.log("  FRAME: magic=" + frame.magic + " flags=" + frame.bytes2_7);
        if (frame.len_le !== undefined) {
            console.log("  LEN_LE=" + frame.len_le + " LEN_BE=" + frame.len_be + 
                       " match_le=" + frame.len_match_le + " match_be=" + frame.len_match_be);
        }
        if (frame.msg_type_le !== undefined) {
            console.log("  MSG_TYPE_LE=0x" + frame.msg_type_le.toString(16) + 
                       " MSG_TYPE_BE=0x" + frame.msg_type_be.toString(16));
        }
    }
    
    var strings = scanStrings(dataPtr, len, 4);
    if (strings.length > 0) {
        console.log("  STRINGS: " + strings.length + " found");
        for (var i = 0; i < Math.min(strings.length, 5); i++) {
            console.log("    [" + strings[i].offset + "] " + strings[i].text);
        }
    }
}

// ---------------------------------------------------------------------------
// Find libc.so and exports
// ---------------------------------------------------------------------------
var libc = Process.findModuleByName("libc.so");
if (!libc) {
    console.log("[-] libc.so not found");
} else {
    console.log("[+] libc.so found @ " + libc.base);
}

function getExport(name) {
    if (!libc) return null;
    var addr = libc.findExportByName(name);
    if (!addr) {
        console.log("[-] " + name + " not found in libc.so");
    }
    return addr;
}

// ---------------------------------------------------------------------------
// Scan /proc/self/net/tcp for existing connections to port 50504
// ---------------------------------------------------------------------------
function scanExistingConnections() {
    console.log("[*] Scanning existing TCP connections...");
    try {
        var fopen = new NativeFunction(getExport("fopen"), 'pointer', ['pointer', 'pointer']);
        var fgets = new NativeFunction(getExport("fgets"), 'pointer', ['pointer', 'int', 'pointer']);
        var fclose = new NativeFunction(getExport("fclose"), 'int', ['pointer']);
        
        var path = Memory.allocUtf8String("/proc/self/net/tcp");
        var mode = Memory.allocUtf8String("r");
        var fp = fopen(path, mode);
        if (fp.isNull()) {
            console.log("[-] Could not open /proc/self/net/tcp");
            return;
        }
        
        var buf = Memory.alloc(2048);
        var found = 0;
        
        // Skip header line
        fgets(buf, 2048, fp);
        
        while (true) {
            var line = fgets(buf, 2048, fp);
            if (line.isNull()) break;
            var str = buf.readUtf8String();
            if (!str) continue;
            
            // Parse: sl local_addr rem_addr st tx_queue:rx_queue ... inode
            var parts = str.trim().split(/\s+/);
            if (parts.length < 10) continue;
            
            var remAddr = parts[2]; // e.g., 772FC80A:C548
            if (remAddr.indexOf("C548") !== -1) {
                var localAddr = parts[1];
                var localParts = localAddr.split(":");
                if (localParts.length === 2) {
                    var fdHex = localParts[1];
                    var fd = parseInt(fdHex, 16);
                    if (gameServerFDs.indexOf(fd) === -1) {
                        gameServerFDs.push(fd);
                        found++;
                        console.log("[EXISTING] fd=" + fd + " connected to 47.252.x.x:50504");
                    }
                }
            }
        }
        
        fclose(fp);
        console.log("[+] Found " + found + " existing game server FD(s)");
    } catch (e) {
        console.log("[-] Error scanning existing connections: " + e);
    }
}

// ---------------------------------------------------------------------------
// Hook SSL_read / SSL_write (fallback for TLS connections)
// ---------------------------------------------------------------------------
function hookSSL() {
    var libssl = Process.findModuleByName("libssl.so");
    if (!libssl) {
        console.log("[*] libssl.so not found — traffic may be cleartext");
        return;
    }
    console.log("[+] libssl.so found @ " + libssl.base);
    
    var SSL_read = libssl.findExportByName("SSL_read");
    var SSL_write = libssl.findExportByName("SSL_write");
    
    if (SSL_read) {
        console.log("[+] Hooking SSL_read @ " + SSL_read);
        Interceptor.attach(SSL_read, {
            onLeave: function(retval) {
                var len = retval.toInt32();
                if (len > 0) {
                    logPacket("SERVER->CLIENT", -1, this.buf, len);
                }
            },
            onEnter: function(args) {
                this.buf = args[1];
            }
        });
    }
    
    if (SSL_write) {
        console.log("[+] Hooking SSL_write @ " + SSL_write);
        Interceptor.attach(SSL_write, {
            onEnter: function(args) {
                var len = args[2].toInt32();
                if (len > 0) {
                    logPacket("CLIENT->SERVER", -1, args[1], len);
                }
            }
        });
    }
}

// ---------------------------------------------------------------------------
// Hook connect() to detect game server FD
// ---------------------------------------------------------------------------
function hookConnect() {
    var connectAddr = getExport("connect");
    if (!connectAddr) return;
    
    console.log("[+] Hooking connect @ " + connectAddr);
    Interceptor.attach(connectAddr, {
        onEnter: function(args) {
            var sockfd = args[0].toInt32();
            var addrPtr = args[1];
            var addrlen = args[2].toInt32();
            
            if (addrlen >= 16) {
                var family = addrPtr.readU16();
                if (family === 2) { // AF_INET
                    var port = addrPtr.add(2).readU16();
                    var ip = addrPtr.add(4).readU32();
                    
                    if (port === TARGET_PORT || port === TARGET_PORT_LE) {
                        var ipStr = [(ip >> 0) & 0xFF, (ip >> 8) & 0xFF, (ip >> 16) & 0xFF, (ip >> 24) & 0xFF].join(".");
                        console.log("[CONNECT] fd=" + sockfd + " -> " + ipStr + ":" + (port === TARGET_PORT ? 50504 : port));
                        if (gameServerFDs.indexOf(sockfd) === -1) {
                            gameServerFDs.push(sockfd);
                        }
                    }
                }
            }
        }
    });
}

// ---------------------------------------------------------------------------
// Hook recv/recvfrom/read
// ---------------------------------------------------------------------------
function hookRecv() {
    function attachRecv(name, addr) {
        if (!addr) return;
        console.log("[+] Hooking " + name + " @ " + addr);
        Interceptor.attach(addr, {
            onLeave: function(retval) {
                var fd = this.fd;
                var buf = this.buf;
                var len = retval.toInt32();
                
                if (len > 0 && gameServerFDs.indexOf(fd) !== -1) {
                    logPacket("SERVER->CLIENT", fd, buf, len);
                }
            },
            onEnter: function(args) {
                this.fd = args[0].toInt32();
                this.buf = args[1];
            }
        });
    }
    
    attachRecv("recv", getExport("recv"));
    attachRecv("recvfrom", getExport("recvfrom"));
    attachRecv("read", getExport("read"));
}

// ---------------------------------------------------------------------------
// Hook send/sendto/write
// ---------------------------------------------------------------------------
function hookSend() {
    function attachSend(name, addr) {
        if (!addr) return;
        console.log("[+] Hooking " + name + " @ " + addr);
        Interceptor.attach(addr, {
            onEnter: function(args) {
                var fd = args[0].toInt32();
                var buf = args[1];
                var len = args[2].toInt32();
                
                if (len > 0 && gameServerFDs.indexOf(fd) !== -1) {
                    logPacket("CLIENT->SERVER", fd, buf, len);
                }
            }
        });
    }
    
    attachSend("send", getExport("send"));
    attachSend("sendto", getExport("sendto"));
    attachSend("write", getExport("write"));
}

// ---------------------------------------------------------------------------
// Hook close() to remove FDs from tracking
// ---------------------------------------------------------------------------
function hookClose() {
    var closeAddr = getExport("close");
    if (!closeAddr) return;
    
    Interceptor.attach(closeAddr, {
        onEnter: function(args) {
            var fd = args[0].toInt32();
            var idx = gameServerFDs.indexOf(fd);
            if (idx !== -1) {
                console.log("[CLOSE] fd=" + fd + " removed from tracking");
                gameServerFDs.splice(idx, 1);
            }
        }
    });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
    console.log("[*] Phase 3 raw recv()/send() hook starting...");
    console.log("[*] Target port: 50504 (0xC548)");
    console.log("[*] Logging first 128 bytes of each packet only");
    
    hookConnect();
    hookRecv();
    hookSend();
    hookClose();
    hookSSL();
    
    // Check for existing connections (game may already be connected)
    scanExistingConnections();
    
    console.log("[+] All hooks applied. Waiting for game server connection...");
    console.log("[+] Navigate the game to trigger protocol traffic.");
}

if (typeof Java !== 'undefined' && Java.available) {
    Java.perform(function() {
        main();
    });
} else {
    main();
}

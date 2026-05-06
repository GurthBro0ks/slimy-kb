/**
 * Native BoringSSL Certificate Verification Bypass - v3
 * Targets: libcocos2dlua.so (cocos2d + BoringSSL/OpenSSL)
 * 
 * Method 1: Hook SSL_CTX_set_verify and SSL_set_verify (catches new contexts)
 * Method 2: Hook SSL_do_handshake and disable verification on SSL object directly
 *           (catches contexts created before our hooks are applied)
 * 
 * Handles spawn-gating by polling /proc/self/maps for library load.
 * Combines with frida_ssl_unpin.js for Java layer.
 */

function findModuleBase(moduleName) {
    var libc = Process.findModuleByName('libc.so');
    if (!libc) {
        return null;
    }
    
    var fopen = new NativeFunction(libc.findExportByName('fopen'), 'pointer', ['pointer', 'pointer']);
    var fgets = new NativeFunction(libc.findExportByName('fgets'), 'pointer', ['pointer', 'int', 'pointer']);
    var fclose = new NativeFunction(libc.findExportByName('fclose'), 'int', ['pointer']);
    
    var path = Memory.allocUtf8String('/proc/self/maps');
    var mode = Memory.allocUtf8String('r');
    var fp = fopen(path, mode);
    
    if (fp.isNull()) {
        return null;
    }
    
    var buffer = Memory.alloc(2048);
    var base = null;
    
    while (true) {
        var line = fgets(buffer, 2048, fp);
        if (line.isNull()) break;
        
        var str = buffer.readUtf8String();
        if (str.indexOf(moduleName) !== -1) {
            var parts = str.trim().split(/\s+/);
            if (parts.length > 0) {
                var addrRange = parts[0].split('-');
                if (addrRange.length >= 2) {
                    base = ptr('0x' + addrRange[0]);
                    break;
                }
            }
        }
    }
    
    fclose(fp);
    return base;
}

function hookBoringSSLVerify() {
    console.log("[*] Hooking BoringSSL certificate verification...");
    
    var moduleName = "libcocos2dlua.so";
    var verifyNone = 0x00;
    
    var offsets = {
        SSL_CTX_set_verify: 0xca2494,
        SSL_set_verify: 0xca0a4c,
        SSL_do_handshake: 0xca0de8,
        SSL_get_peer_certificate: 0xca0ac0
    };
    
    var base = null;
    var attempts = 0;
    var maxAttempts = 60; // Poll for up to 60 seconds
    
    while (!base && attempts < maxAttempts) {
        base = findModuleBase(moduleName);
        if (!base) {
            attempts++;
            console.log("[*] Waiting for " + moduleName + " to load (attempt " + attempts + ")...");
            // Sleep for 1 second using Thread.sleep
            try {
                Java.use('java.lang.Thread').sleep(1000);
            } catch (e) {
                // If Java is not available, busy-wait
                var start = Date.now();
                while (Date.now() - start < 1000) {}
            }
        }
    }
    
    if (!base) {
        console.log("[-] Could not find " + moduleName + " base address after " + maxAttempts + " attempts");
        return;
    }
    
    console.log("[+] " + moduleName + " base @ " + base);
    
    // Method 1: Hook SSL_CTX_set_verify
    var ssl_ctx_set_verify_addr = base.add(offsets.SSL_CTX_set_verify);
    console.log("[+] SSL_CTX_set_verify @ " + ssl_ctx_set_verify_addr);
    try {
        Interceptor.attach(ssl_ctx_set_verify_addr, {
            onEnter: function(args) {
                var mode = args[1].toInt32();
                if (mode !== verifyNone) {
                    console.log("[*] SSL_CTX_set_verify (mode=" + mode + ") -> SSL_VERIFY_NONE");
                    args[1] = ptr(verifyNone);
                    args[2] = ptr(0);
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_CTX_set_verify hook failed: " + e.message);
    }
    
    // Method 1: Hook SSL_set_verify
    var ssl_set_verify_addr = base.add(offsets.SSL_set_verify);
    console.log("[+] SSL_set_verify @ " + ssl_set_verify_addr);
    try {
        Interceptor.attach(ssl_set_verify_addr, {
            onEnter: function(args) {
                var mode = args[1].toInt32();
                if (mode !== verifyNone) {
                    console.log("[*] SSL_set_verify (mode=" + mode + ") -> SSL_VERIFY_NONE");
                    args[1] = ptr(verifyNone);
                    args[2] = ptr(0);
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_set_verify hook failed: " + e.message);
    }
    
    // Method 2: Hook SSL_do_handshake to disable verification on the SSL object
    var ssl_do_handshake_addr = base.add(offsets.SSL_do_handshake);
    console.log("[+] SSL_do_handshake @ " + ssl_do_handshake_addr);
    try {
        Interceptor.attach(ssl_do_handshake_addr, {
            onEnter: function(args) {
                var ssl = args[0];
                var currentMode = ssl.add(392).readU32();
                if (currentMode !== verifyNone) {
                    console.log("[*] SSL_do_handshake: disabling verify (mode=" + currentMode + ")");
                    ssl.add(392).writeU32(0);  // SSL_VERIFY_NONE
                    ssl.add(400).writePointer(ptr(0));  // NULL callback
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_do_handshake hook failed: " + e.message);
    }
    
    console.log("[+] BoringSSL hooks applied");
}

// Main execution
function main() {
    console.log("[*] Native BoringSSL unpin starting...");
    hookBoringSSLVerify();
    console.log("[+] Native SSL unpinning complete");
}

// Support both standalone and Java.perform contexts
if (Java.available) {
    Java.perform(function() {
        main();
    });
} else {
    main();
}

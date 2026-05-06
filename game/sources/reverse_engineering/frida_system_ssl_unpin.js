/**
 * Native System SSL Hook for JPush Process
 * Targets: system libssl.so (not libcocos2dlua.so)
 * 
 * Uses Frida 17.x API: Process.findModuleByName + module.getExportByName
 * Hooks SSL_CTX_set_verify and SSL_set_verify to disable cert verification.
 */

function hookSystemSSL() {
    console.log("[*] Hooking system libssl.so certificate verification...");
    
    var verifyNone = 0x00;
    
    // Find the system libssl.so module
    var sslModule = Process.findModuleByName("libssl.so");
    if (!sslModule) {
        console.log("[-] libssl.so not found in process");
        return;
    }
    console.log("[+] Found libssl.so @ " + sslModule.base);
    
    // Hook SSL_CTX_set_verify
    try {
        var ssl_ctx_set_verify = sslModule.getExportByName("SSL_CTX_set_verify");
        console.log("[+] SSL_CTX_set_verify @ " + ssl_ctx_set_verify);
        Interceptor.attach(ssl_ctx_set_verify, {
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
    
    // Hook SSL_set_verify
    try {
        var ssl_set_verify = sslModule.getExportByName("SSL_set_verify");
        console.log("[+] SSL_set_verify @ " + ssl_set_verify);
        Interceptor.attach(ssl_set_verify, {
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
    
    // Hook SSL_do_handshake
    try {
        var ssl_do_handshake = sslModule.getExportByName("SSL_do_handshake");
        console.log("[+] SSL_do_handshake @ " + ssl_do_handshake);
        Interceptor.attach(ssl_do_handshake, {
            onEnter: function(args) {
                var ssl = args[0];
                // Try common verify mode offsets
                var offsets = [0x88, 0x90, 392];
                for (var j = 0; j < offsets.length; j++) {
                    try {
                        var currentMode = ssl.add(offsets[j]).readU32();
                        if (currentMode !== verifyNone && currentMode !== 0) {
                            console.log("[*] SSL_do_handshake: disabling verify at offset " + offsets[j] + " (mode=" + currentMode + ")");
                            ssl.add(offsets[j]).writeU32(0);
                            break;
                        }
                    } catch (e) {}
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_do_handshake hook failed: " + e.message);
    }
    
    console.log("[+] System SSL hooks applied");
}

function hookSSLReadWrite() {
    console.log("[*] Hooking SSL_read/SSL_write for JPush intercept...");
    
    var sslModule = Process.findModuleByName("libssl.so");
    if (!sslModule) {
        console.log("[-] libssl.so not found for read/write hooks");
        return;
    }
    
    // Hook SSL_read
    try {
        var ssl_read = sslModule.getExportByName("SSL_read");
        console.log("[+] SSL_read @ " + ssl_read);
        Interceptor.attach(ssl_read, {
            onEnter: function(args) {
                this.buf = args[1];
                this.len = args[2].toInt32();
            },
            onLeave: function(retval) {
                var ret = retval.toInt32();
                if (ret > 0 && ret <= this.len) {
                    var data = Memory.readByteArray(this.buf, Math.min(ret, 64));
                    var hexStr = '';
                    var arr = new Uint8Array(data);
                    for (var i = 0; i < arr.length; i++) {
                        hexStr += (arr[i] < 16 ? '0' : '') + arr[i].toString(16);
                    }
                    console.log("[RECV] len=" + ret + " hex=" + hexStr);
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_read hook failed: " + e.message);
    }
    
    // Hook SSL_write
    try {
        var ssl_write = sslModule.getExportByName("SSL_write");
        console.log("[+] SSL_write @ " + ssl_write);
        Interceptor.attach(ssl_write, {
            onEnter: function(args) {
                var buf = args[1];
                var len = args[2].toInt32();
                if (len > 0 && len <= 65536) {
                    var data = Memory.readByteArray(buf, Math.min(len, 64));
                    var hexStr = '';
                    var arr = new Uint8Array(data);
                    for (var i = 0; i < arr.length; i++) {
                        hexStr += (arr[i] < 16 ? '0' : '') + arr[i].toString(16);
                    }
                    console.log("[SEND] len=" + len + " hex=" + hexStr);
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_write hook failed: " + e.message);
    }
    
    console.log("[+] SSL read/write hooks applied");
}

// Main execution
function main() {
    console.log("[*] System SSL unpin starting for JPush process...");
    hookSystemSSL();
    hookSSLReadWrite();
    console.log("[+] System SSL unpinning complete");
    // Keep the script alive
    setInterval(function() {}, 60000);
}

// Support both standalone and Java.perform contexts
if (Java.available) {
    Java.perform(function() {
        main();
    });
} else {
    main();
}

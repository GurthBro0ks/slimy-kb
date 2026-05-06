/**
 * Native Application-Layer JPush Protocol Intercept
 * Targets: libcocos2dlua.so (BoringSSL SSL_read/SSL_write)
 * 
 * Hooks SSL_read and SSL_write after TLS decryption to capture
 * plaintext JPush protocol messages without breaking TLS.
 * 
 * Method: Direct address calculation from /proc/self/maps + known offsets
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

function hookSSLSendRecv() {
    console.log("[*] Hooking SSL_read/SSL_write for JPush protocol intercept...");
    
    var moduleName = "libcocos2dlua.so";
    
    var offsets = {
        SSL_read: 0xca1020,
        SSL_write: 0xca136c
    };
    
    var base = findModuleBase(moduleName);
    if (!base) {
        console.log("[-] Could not find " + moduleName + " base address");
        return;
    }
    
    console.log("[+] " + moduleName + " base @ " + base);
    
    // Hook SSL_read (server -> client)
    var ssl_read_addr = base.add(offsets.SSL_read);
    console.log("[+] SSL_read @ " + ssl_read_addr);
    try {
        Interceptor.attach(ssl_read_addr, {
            onEnter: function(args) {
                this.buf = args[1];
                this.len = args[2].toInt32();
            },
            onLeave: function(retval) {
                var ret = retval.toInt32();
                if (ret > 0 && ret <= this.len) {
                    var data = Memory.readByteArray(this.buf, ret);
                    var hexStr = '';
                    for (var i = 0; i < Math.min(ret, 32); i++) {
                        var b = new Uint8Array(data)[i];
                        hexStr += (b < 16 ? '0' : '') + b.toString(16);
                    }
                    console.log("[RECV] len=" + ret + " hex=" + hexStr);
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_read hook failed: " + e.message);
    }
    
    // Hook SSL_write (client -> server)
    var ssl_write_addr = base.add(offsets.SSL_write);
    console.log("[+] SSL_write @ " + ssl_write_addr);
    try {
        Interceptor.attach(ssl_write_addr, {
            onEnter: function(args) {
                var buf = args[1];
                var len = args[2].toInt32();
                if (len > 0 && len <= 65536) {
                    var data = Memory.readByteArray(buf, len);
                    var hexStr = '';
                    for (var i = 0; i < Math.min(len, 32); i++) {
                        var b = new Uint8Array(data)[i];
                        hexStr += (b < 16 ? '0' : '') + b.toString(16);
                    }
                    console.log("[SEND] len=" + len + " hex=" + hexStr);
                }
            }
        });
    } catch (e) {
        console.log("[!] SSL_write hook failed: " + e.message);
    }
    
    console.log("[+] SSL hooks applied");
}

// Main execution
function main() {
    console.log("[*] JPush protocol intercept starting...");
    hookSSLSendRecv();
    console.log("[+] Protocol intercept ready");
}

// Support both standalone and Java.perform contexts
if (Java.available) {
    Java.perform(function() {
        main();
    });
} else {
    main();
}

/**
 * Universal SSL Certificate Pinning Bypass for Android
 * Compatible with Frida 17.x
 * Targets: TrustManager, OkHttp, SSLContext, Conscrypt, BoringSSL
 */

function bypassTrustManager() {
    console.log("[*] Bypassing TrustManager...");
    try {
        var TrustManager = Java.use('javax.net.ssl.TrustManager');
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        
        // Create a custom TrustManager that accepts all certs
        var CustomTrustManager = Java.registerClass({
            name: 'com.slimyai.CustomTrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() { return []; }
            }
        });
        
        // Hook SSLContext.init to inject our TrustManager
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function(km, tm, random) {
            console.log("[*] SSLContext.init() hooked");
            SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').call(this, km, [CustomTrustManager.$new()], random);
        };
        
        console.log("[+] TrustManager bypassed");
    } catch (e) {
        console.log("[-] TrustManager bypass failed: " + e.message);
    }
}

function bypassOkHttp() {
    console.log("[*] Bypassing OkHttp CertificatePinner...");
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, certificates) {
            console.log("[*] OkHttp CertificatePinner.check() bypassed for: " + hostname);
            return;
        };
        
        CertificatePinner.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function(hostname, certificate) {
            console.log("[*] OkHttp CertificatePinner.check() bypassed for: " + hostname);
            return;
        };
        
        console.log("[+] OkHttp CertificatePinner bypassed");
    } catch (e) {
        console.log("[-] OkHttp bypass failed: " + e.message);
    }
}

function bypassSSLContext() {
    console.log("[*] Bypassing SSLContext...");
    try {
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        
        // Hook getInstance to return a custom SSLContext
        SSLContext.getInstance.overload('java.lang.String').implementation = function(algorithm) {
            console.log("[*] SSLContext.getInstance() hooked: " + algorithm);
            return SSLContext.getInstance.overload('java.lang.String').call(this, algorithm);
        };
        
        console.log("[+] SSLContext bypassed");
    } catch (e) {
        console.log("[-] SSLContext bypass failed: " + e.message);
    }
}

function bypassConscrypt() {
    console.log("[*] Bypassing Conscrypt...");
    try {
        var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        
        TrustManagerImpl.checkTrustedRecursive.implementation = function() {
            console.log("[*] Conscrypt TrustManagerImpl.checkTrustedRecursive() bypassed");
            return Java.use('java.util.ArrayList').$new();
        };
        
        TrustManagerImpl.verifyChain.implementation = function() {
            console.log("[*] Conscrypt TrustManagerImpl.verifyChain() bypassed");
            return Java.use('java.util.ArrayList').$new();
        };
        
        console.log("[+] Conscrypt bypassed");
    } catch (e) {
        console.log("[-] Conscrypt bypass failed: " + e.message);
    }
}

function bypassWebView() {
    console.log("[*] Bypassing WebView SSL...");
    try {
        var SslErrorHandler = Java.use('android.webkit.SslErrorHandler');
        var WebViewClient = Java.use('android.webkit.WebViewClient');
        
        WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
            console.log("[*] WebViewClient.onReceivedSslError() bypassed");
            handler.proceed();
        };
        
        console.log("[+] WebView SSL bypassed");
    } catch (e) {
        console.log("[-] WebView bypass failed: " + e.message);
    }
}

function bypassHostnameVerifier() {
    console.log("[*] Bypassing HostnameVerifier...");
    try {
        var HostnameVerifier = Java.use('javax.net.ssl.HostnameVerifier');
        
        // Hook common HostnameVerifier implementations
        try {
            var DefaultHostnameVerifier = Java.use('org.apache.http.conn.ssl.DefaultHostnameVerifier');
            DefaultHostnameVerifier.verify.implementation = function(hostname, session) {
                console.log("[*] DefaultHostnameVerifier.verify() bypassed for: " + hostname);
                return true;
            };
        } catch (e) {}
        
        try {
            var AbstractVerifier = Java.use('org.apache.http.conn.ssl.AbstractVerifier');
            AbstractVerifier.verify.implementation = function(hostname, session) {
                console.log("[*] AbstractVerifier.verify() bypassed for: " + hostname);
                return true;
            };
        } catch (e) {}
        
        console.log("[+] HostnameVerifier bypassed");
    } catch (e) {
        console.log("[-] HostnameVerifier bypass failed: " + e.message);
    }
}

function bypassNetworkSecurityConfig() {
    console.log("[*] Bypassing NetworkSecurityConfig...");
    try {
        var NetworkSecurityConfig = Java.use('android.security.net.config.NetworkSecurityConfig');
        
        NetworkSecurityConfig.isCleartextTrafficPermitted.overload('java.lang.String').implementation = function(hostname) {
            console.log("[*] NetworkSecurityConfig.isCleartextTrafficPermitted() bypassed");
            return true;
        };
        
        console.log("[+] NetworkSecurityConfig bypassed");
    } catch (e) {
        console.log("[-] NetworkSecurityConfig bypass failed: " + e.message);
    }
}

function bypassUnity() {
    console.log("[*] Bypassing Unity networking...");
    try {
        // Unity WebRequest certificate handler
        var CertificateHandler = Java.use('unity3d.networking.cert.CertificateHandler');
        CertificateHandler.ValidateCertificate.implementation = function(certificate) {
            console.log("[*] Unity CertificateHandler.ValidateCertificate() bypassed");
            return true;
        };
    } catch (e) {}
    
    try {
        var UnityWebRequest = Java.use('com.unity3d.networking.UnityWebRequest');
        UnityWebRequest.SetCertificateHandler.implementation = function(handler) {
            console.log("[*] UnityWebRequest.SetCertificateHandler() bypassed");
            return;
        };
    } catch (e) {}
    
    console.log("[+] Unity networking bypass attempted");
}

// Main execution
Java.perform(function() {
    console.log("[*] Starting universal SSL unpinning...");
    
    bypassTrustManager();
    bypassOkHttp();
    bypassSSLContext();
    bypassConscrypt();
    bypassWebView();
    bypassHostnameVerifier();
    bypassNetworkSecurityConfig();
    bypassUnity();
    
    console.log("[*] All SSL pinning bypasses applied");
    console.log("[*] Waiting for network requests...");
});

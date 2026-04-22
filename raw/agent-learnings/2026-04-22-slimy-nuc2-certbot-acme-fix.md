# certbot-acme-fix

## Problem
ACME challenge at /.well-known/acme-challenge/ was proxied to Next.js (catch-all location /), which redirected to /login. Certbot nginx authenticator couldn't verify domain ownership. Cert renewal fails ~22 days before expiry.

## Fix (NUC2)
1. Add `location /.well-known/acme-challenge/` block BEFORE the `location /` block in BOTH the HTTPS (443) and HTTP (80) server blocks in /etc/nginx/sites-enabled/slimyai.xyz:
   ```nginx
   location /.well-known/acme-challenge/ {
       root /var/www/html;
   }
   ```
2. Ensure webroot dir exists: `sudo mkdir -p /var/www/html/.well-known/acme-challenge`
3. Test: `sudo nginx -t` → reload: `sudo systemctl reload nginx`
4. Switch certbot to webroot: `sudo certbot renew --cert-name slimyai.xyz --authenticator webroot --webroot-path /var/www/html --dry-run`
5. If dry-run passes: `sudo certbot renew --cert-name slimyai.xyz --authenticator webroot --webroot-path /var/www/html --force-renewal`

## Root Cause
certbot was using the `nginx` authenticator (modifies config on the fly), but the catch-all proxy to Next.js was eating challenge requests. Webroot method is more reliable — drops a file in /var/www/html/.well-known/ and nginx serves it directly before the proxy kicks in.

## Date
2026-04-22

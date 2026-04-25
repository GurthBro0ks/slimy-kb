# Nginx Certbot ACME Fix
> Category: troubleshooting
> Sources: raw/agent-learnings/2026-04-22-slimy-nuc2-certbot-acme-fix.md
> Created: 2026-04-22
> Updated: 2026-04-24
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-25 00:33 UTC (git)
> Version: r2 / b2a7b69
KB METADATA -->

Fix for certbot ACME challenge failures when nginx proxies `/.well-known/acme-challenge/` to Next.js, which redirects to `/login`.

## Symptom

Certbot renewal fails ~22 days before certificate expiry. The nginx authenticator can not verify domain ownership because the challenge request is proxied to Next.js (catch-all `location /`) and redirected to `/login`.

## Root Cause

certbot was using the `nginx` authenticator (modifies config on the fly), but the catch-all proxy to Next.js was eating challenge requests before they could be served.

## Fix Applied (NUC2)

**1. Add `location /.well-known/acme-challenge/` block BEFORE the `location /` block** in both HTTPS (443) and HTTP (80) server blocks in `/etc/nginx/sites-enabled/slimyai.xyz`:

```nginx
location /.well-known/acme-challenge/ {
    root /var/www/html;
}
```

**2. Ensure webroot dir exists:**
```bash
sudo mkdir -p /var/www/html/.well-known/acme-challenge
```

**3. Test and reload nginx:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

**4. Switch certbot to webroot authenticator:**
```bash
sudo certbot renew --cert-name slimyai.xyz --authenticator webroot --webroot-path /var/www/html --dry-run
```

**5. If dry-run passes, force-renew:**
```bash
sudo certbot renew --cert-name slimyai.xyz --authenticator webroot --webroot-path /var/www/html --force-renewal
```

## Why Webroot Is Better

Webroot method drops a verification file in `/var/www/html/.well-known/acme-challenge/` and nginx serves it directly — before the catch-all proxy kicks in. More reliable than the nginx authenticator which modifies config on the fly.

## See Also
- [NUC2 Current State](../architecture/nuc2-current-state.md)
- [Q1 2026 Operational Fixes](q1-2026-operational-fixes.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
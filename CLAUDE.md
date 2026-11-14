# CLAUDE.md: ogcrafts-site

Home site for OGCrafts (ogcrafts.cloud): static, built by `build.py`, deployed by GitHub Pages from `og-crafts/site` on push to `main`.
See README.md for how to add a craft. Dispatch is the first craft; its own site is dispatch.ogcrafts.cloud (repo og-crafts/dispatch-site).
Look: dark-first, ember accent, Nunito + Geist Mono self-hosted, no scripts and no third-party requests, except the optional Cloudflare Web Analytics beacon, which loads only when `analytics.json` holds a token.
Commit identity: Omprakash Gautam <356532942+og-crafterr@users.noreply.github.com>; `gh` login og-crafterr.
Copy that is the owner's to confirm: the four principles, the About page, the privacy text.

## Status (2026-11-14)
- LIVE at https://ogcrafts.cloud (apex A records + www CNAME in Cloudflare, DNS only; HTTPS enforced; www redirects to the apex). Pages deploy from the workflow on every push to `main`.
- Pages: `/`, `/apps/`, `/apps/dispatch/`, `/about/` (with a short bio), `/privacy/`, `404.html`, `sitemap.xml` (with lastmod), `robots.txt`. Social preview: `src/assets/og.png`, made from `scripts/og.html` (headless Chromium screenshot at 1200x630).
- Analytics: Cloudflare Web Analytics, home site only (token in `analytics.json`; the privacy text switches on with it).
- One craft so far: Dispatch 0.5.1. To add a craft: `apps.json` entry, a `DETAILS` entry in `build.py`, images in `src/assets/apps/<id>/`. Bump a craft's `version` here after each release.
- Owner to-dos: submit sitemap in Google Search Console (optional); Gmail "Send mail as" via Resend and a DMARC record for hello@ogcrafts.cloud.
- Pushing: the active `gh` login can drift; use `GH_TOKEN=$(gh auth token --user og-crafts)` (that is the og-crafterr user) for the same command.

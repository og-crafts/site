#!/usr/bin/env python3
"""Builds ogcrafts.cloud into dist/. No dependencies: python3 build.py [--strict]

The crafts live in apps.json (one entry each); a craft with a detail page also needs an entry in DETAILS below.
"""
import html, json, re, shutil, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, DIST = ROOT / "src", ROOT / "dist"
DOMAIN = "ogcrafts.cloud"
BASE = f"https://{DOMAIN}"
EMAIL = f"hello@{DOMAIN}"
ORG = "https://github.com/og-crafts"
YEAR = datetime.date.today().year
UPDATED = "14 November 2026"  # date on the privacy page; change it when that text changes
e = html.escape

APPS = json.loads((ROOT / "apps.json").read_text())["apps"]
STATUS = {"stable": "Stable", "beta": "Public beta", "soon": "Coming soon"}

PRINCIPLES = [
    ("Yours, on your device", "Our apps do their work on your computer or phone. What you make stays with you, in files you can read, copy and back up."),
    ("Open where we can", "Where it makes sense we publish the source under a permissive licence, so you can read it, build it and report problems."),
    ("No account, no watching", "Our apps don't ask you to sign up and don't track what you do. If a craft ever needs a server, its page says so plainly."),
    ("Small and well made", "We would rather ship a focused tool that does one job properly than a sprawling suite. Status is always labelled: beta means beta."),
]

DETAILS = {
    "dispatch": {
        "features": [
            ("Requests and collections", "Build requests with params, headers, bodies and auth. Group them in collections and folders, with variables and environments."),
            ("Scripts and tests", "A few lines of JavaScript after a request check the status, the body or the timing, and save values for the next call."),
            ("Runner and flows", "Run a collection or a folder for every row of a CSV or JSON file, or wire requests into a node-graph flow."),
            ("Load testing", "Send the same request, or a whole flow, from many virtual users and set pass and fail thresholds."),
            ("Workspaces as files", "Keep a workspace as a folder of plain files so it lives in git next to your code."),
            ("Desktop, web and CLI", "The same app on Windows, macOS and Linux, in your browser, and as a command-line runner for CI."),
        ],
        "gallery": [("runner", "The runner"), ("scripts", "Scripts and tests"), ("load", "Load testing"), ("docs", "Generated documentation")],
    },
}

# ---------- helpers ----------
def asset(app, name, ext="png"): return f"/assets/apps/{app['id']}/{name}.{ext}"

def pills(items): return '<ul class="pills">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"

def status_pill(a): return f'<span class="pill status{" stable" if a["status"] == "stable" else ""}">{STATUS[a["status"]]}</span>'

def picture(a, alt, lazy=True, w=1440, h=900):
    dark, light = asset(a, a["shot_dark"]), asset(a, a["shot"])
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{dark}"><img src="{light}" alt="{e(alt)}" width="{w}" height="{h}"'
            f'{" loading=lazy" if lazy else ""} decoding="async"></picture>')

def card(a, i):
    url = f"/apps/{a['id']}/"
    return f"""<article class="app-card"><div class="shot">{picture(a, f"{a['name']} on a desktop")}</div>
<div class="body"><div class="top"><img src="{asset(a, 'icon-192')}" alt="" width="44" height="44"><div><span class="num">{i:02d} / {e(a['kind'])}</span>
<h3><a href="{url}">{e(a['name'])}</a></h3></div></div>
<p>{e(a['tagline'])} {e(a['desc'])}</p>
<div>{status_pill(a)} {pills(a['platforms'])}</div>
<span class="more">Explore {e(a['name'])} &rarr;</span></div></article>"""

def soon_card():
    return f"""<article class="app-card soon-card"><p class="eyebrow">Next up</p><h3>More crafts on the way.</h3>
<p>New tools are in the workshop. Tell us what you would like us to make: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></article>"""

NAV = [("/apps/", "Crafts"), ("/about/", "About"), (ORG, "GitHub"), (f"mailto:{EMAIL}", "Contact")]

def shell(path, title, desc, body, noindex=False):
    navs = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == path else ""}>{l}</a>' for h, l in NAV)
    crafts = "".join(f'<li><a href="/apps/{a["id"]}/">{e(a["name"])}</a></li>' for a in APPS)
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#121214">
{robots}<link rel="canonical" href="{BASE}{path}">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/nunito-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}{path}">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap"><a class="brand" href="/"><img src="/assets/icon.svg" alt="" width="32" height="32">OGCrafts</a><nav class="main" aria-label="Main">{navs}</nav></div></header>
<main id="main">{body}</main>
<footer class="site"><div class="wrap"><div class="fcols">
<div><a class="brand" href="/"><img src="/assets/icon.svg" alt="" width="28" height="28">OGCrafts</a><p class="muted" style="margin-top:12px">Software crafts for your computer, browser and phone.</p></div>
<div><h2>Crafts</h2><ul><li><a href="/apps/">All crafts</a></li>{crafts}</ul></div>
<div><h2>Company</h2><ul><li><a href="/about/">About</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
<div><h2>Elsewhere</h2><ul><li><a href="{ORG}">GitHub</a></li></ul></div></div>
<small>&copy; {YEAR} OGCrafts. Open source where noted.</small></div></footer>
</body></html>"""

# ---------- pages ----------
def lineup_section(heading="The lineup", eyebrow="02 / The lineup"):
    cards = "".join(card(a, i) for i, a in enumerate(APPS, 1)) + soon_card()
    return f'<section id="lineup"><div class="wrap"><div class="section-head"><p class="eyebrow">{eyebrow}</p><h2>{heading}</h2></div><div class="lineup">{cards}</div></div></section>'

def principles_section(n="03"):
    items = "".join(f'<div class="card"><span class="num">{i:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(PRINCIPLES, 1))
    return f'<section class="tint" id="principles"><div class="wrap"><div class="section-head"><p class="eyebrow">{n} / Principles</p><h2>How we build.</h2></div><div class="grid">{items}</div></div></section>'

def home():
    count = len(APPS)
    plats = sorted({p for a in APPS for p in a["platforms"]}, key=["Windows", "macOS", "Linux", "Web", "Android", "CLI"].index)
    return f"""
<section class="hero"><div class="wrap"><p class="eyebrow">01 / Crafts</p>
<h1>Tools made with care.</h1>
<p class="lead">OGCrafts makes focused software for your computer, your browser and your phone. Free where we can, open where it makes sense, and never in your way.</p>
<div class="cta-row"><a class="btn primary" href="/apps/">Explore the crafts</a><a class="btn" href="{ORG}">Open source on GitHub</a></div>
<p class="note">{count} craft today, more on the way.</p></div></section>
<div class="trust"><div class="wrap"><ul>{"".join(f"<li>{p}</li>" for p in plats)}<li>No sign-up</li></ul></div></div>
{lineup_section()}
{principles_section()}
<section id="about"><div class="wrap"><div class="section-head"><p class="eyebrow">04 / Say hello</p><h2>Build it with us.</h2><p class="lead">Found a bug, want a feature, or have an idea for a craft? Write to us or open an issue on GitHub.</p></div>
<div class="cta-row"><a class="btn primary" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{ORG}">GitHub</a></div></div></section>"""

def apps_index():
    jump = "".join(f'<a href="/apps/{a["id"]}/" aria-label="{e(a["name"])}"><img src="{asset(a, "icon-192")}" alt="" width="40" height="40"></a>' for a in APPS)
    return f"""
<section class="hero"><div class="wrap"><p class="eyebrow">01 / Crafts</p><h1>{len(APPS)} craft. More coming.</h1>
<p class="lead">Every craft is a focused tool with its own page, downloads and privacy policy.</p></div></section>
<section style="padding-top:0"><div class="wrap"><div class="jump">{jump}</div></div></section>
{lineup_section(eyebrow="02 / The lineup")}
{principles_section()}"""

def app_page(a):
    d = DETAILS[a["id"]]
    feats = "".join(f'<div class="card"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in d["features"])
    gallery = "".join(f'<figure class="shot-frame"><img src="{asset(a, n)}" alt="{e(a["name"])}: {e(c.lower())}" width="1440" height="900" loading="lazy" decoding="async"><figcaption style="padding:0 14px 12px">{e(c)}</figcaption></figure>' for n, c in d["gallery"])
    facts = [("Status", f'{STATUS[a["status"]]}, version {a["version"]}'), ("Platforms", ", ".join(a["platforms"])), ("Licence", f'{a["license"]} (open source)'),
             ("Source", f'<a href="{a["source"]}">{a["source"].replace("https://", "")}</a>'), ("Privacy", f'<a href="{a["privacy"]}">Privacy policy</a>')]
    fl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
    return f"""
<section class="hero"><div class="wrap app-hero"><div>
<div class="titlerow"><img src="{asset(a, 'icon-192')}" alt="" width="72" height="72"><div><p class="eyebrow" style="margin:0">{e(a['kind'])}</p><h1>{e(a['name'])}</h1></div></div>
<p class="lead">{e(a['tagline'])} {e(a['desc'])}</p>
<div class="cta-row"><a class="btn primary" href="{a['web']}">Open in your browser</a><a class="btn" href="{a['download']}">Download for desktop</a><a class="btn" href="{a['site']}">Visit the {e(a['name'])} site</a></div>
<div>{status_pill(a)} {pills(a['platforms'])}</div></div>
<div class="shot-frame">{picture(a, f"{a['name']} showing a request and its response", lazy=False)}</div></div></section>
<section class="tint"><div class="wrap"><div class="section-head"><p class="eyebrow">What it does</p><h2>What you get.</h2></div><div class="grid">{feats}</div></div></section>
<section><div class="wrap"><div class="section-head"><p class="eyebrow">A closer look</p><h2>See it working.</h2></div><div class="gallery">{gallery}</div></div></section>
<section class="tint"><div class="wrap"><div class="section-head"><p class="eyebrow">The details</p><h2>At a glance.</h2></div><dl class="facts">{fl}</dl></div></section>"""

def about():
    return f"""
<section class="hero"><div class="wrap"><p class="eyebrow">About</p><h1>An independent workshop.</h1></div></section>
<section style="padding-top:0"><div class="wrap prose">
<p class="lead">OGCrafts makes focused software tools. We build them to run on your own device, to keep what you make in files you control, and to be honest about what they do.</p>
<h2>What we make</h2><p>Each craft is a small, complete tool, such as <a href="/apps/dispatch/">Dispatch</a>, a local-first API client. We publish the source where we can, label every release honestly and keep the apps free of accounts and tracking.</p>
<h2>Get in touch</h2><p>Questions, bug reports and ideas are welcome at <a href="mailto:{EMAIL}">{EMAIL}</a>. For code issues, open one in the project&rsquo;s repository on <a href="{ORG}">GitHub</a>.</p>
</div></section>"""

def privacy():
    return f"""
<section class="hero"><div class="wrap"><p class="eyebrow">Privacy</p><h1>Privacy policy for this website.</h1><p class="muted">Updated {UPDATED}</p></div></section>
<section style="padding-top:0"><div class="wrap prose">
<p>This page covers ogcrafts.cloud only. Each craft has its own privacy policy, linked from its page, because what an app does with data is specific to that app.</p>
<h2>What this website does</h2><p>The site is a set of static files hosted on GitHub Pages. When you open it, GitHub&rsquo;s servers receive the request for the files and, like any web host, may log your IP address and browser details under <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub&rsquo;s privacy statement</a>. We do not receive those logs for individual visitors. We do not set cookies, run analytics, or load fonts, scripts or images from other sites.</p>
<h2>Email</h2><p>If you write to <a href="mailto:{EMAIL}">{EMAIL}</a>, we receive your address and your message, and we use them only to reply. Mail to this address is forwarded by Cloudflare Email Routing to a private inbox. We do not add you to any list.</p>
<h2>Contact</h2><p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>"""

def notfound():
    return '<section class="hero"><div class="wrap"><p class="eyebrow">404</p><h1>Nothing here.</h1><p class="lead">That page does not exist. <a href="/">Go to the home page</a> or see <a href="/apps/">all crafts</a>.</p></div></section>'

# ---------- build ----------
def main():
    strict = "--strict" in sys.argv
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SRC / "assets", DIST / "assets")
    shutil.copy(SRC / "site.css", DIST / "assets" / "site.css")
    pages = {
        "/": ("OGCrafts: tools made with care", "OGCrafts makes focused software for your computer, browser and phone. Free where we can, open where it makes sense.", home()),
        "/apps/": ("Crafts | OGCrafts", "Every OGCrafts app in one place, across desktop, web and the command line.", apps_index()),
        "/about/": ("About | OGCrafts", "OGCrafts is an independent workshop making focused software tools.", about()),
        "/privacy/": ("Privacy | OGCrafts", "How the ogcrafts.cloud website handles your data.", privacy()),
    }
    for a in APPS:
        pages[f"/apps/{a['id']}/"] = (f"{a['name']}: {a['tagline'].rstrip('.')} | OGCrafts", a["desc"], app_page(a))
    for path, (title, desc, body) in pages.items():
        out = DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(shell(path, title, desc, body))
    (DIST / "404.html").write_text(shell("/404.html", "Page not found | OGCrafts", "Page not found.", notfound(), noindex=True))
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{BASE}{p}</loc></url>\n" for p in pages) + "</urlset>\n")
    (DIST / "CNAME").write_text(f"{DOMAIN}\n"); (DIST / ".nojekyll").write_text("")
    problems = check(pages)
    for p in problems: print("PROBLEM:", p)
    print(f"site built: {len(pages)} pages, {len(APPS)} craft(s)")
    if problems and strict: sys.exit(1)

# ---------- checks ----------
def lum(hexc):
    c = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)

def check(pages):
    problems = []
    css = (SRC / "site.css").read_text()
    blocks = re.findall(r":root\s*\{([^}]*)\}", css)
    pairs = [("ink", "bg"), ("ink", "surface"), ("ink", "sunken"), ("muted", "bg"), ("muted", "surface"), ("muted", "sunken"), ("link", "bg"), ("link", "surface"), ("link", "sunken"),
             ("link", "accent-soft"), ("on-accent", "accent"), ("good", "good-soft"), ("warn", "warn-soft"), ("ink", "accent-soft")]
    for name, blk in zip(("dark", "light"), blocks):
        t = dict(re.findall(r"--([a-z-]+):\s*(#[0-9A-Fa-f]{6})", blk))
        for fg, bg in pairs:
            if fg in t and bg in t and ratio(t[fg], t[bg]) < 4.5: problems.append(f"contrast {name}: {fg} on {bg} = {ratio(t[fg], t[bg]):.2f}")
    paths = set()
    for p in pages: paths.add(p)
    files = {"/" + str(f.relative_to(DIST)) for f in DIST.rglob("*") if f.is_file()}
    for f in DIST.rglob("*.html"):
        h = f.read_text(); rel = "/" + str(f.relative_to(DIST))
        if len(re.findall(r"<h1[ >]", h)) != 1: problems.append(f"{rel}: needs exactly one h1")
        for m in re.finditer(r"<img(?![^>]*\balt=)[^>]*>", h): problems.append(f"{rel}: img without alt")
        ids = re.findall(r'\bid="([^"]+)"', h)
        if len(ids) != len(set(ids)): problems.append(f"{rel}: duplicate ids")
        for u in re.findall(r'(?:href|src|srcset)="([^"]+)"', h):
            if u.startswith(("mailto:", "#")): continue
            if u.startswith("http"):
                if re.search(r"(?:src|srcset)=\"" + re.escape(u), h) or ('rel="stylesheet"' in h and False): problems.append(f"{rel}: third-party resource {u}")
                continue
            u0 = u.split("#")[0]
            if u0 and not (u0 in files or (u0.endswith("/") and (u0 + "index.html") in files) or u0 == "/"): problems.append(f"{rel}: broken link {u}")
    return problems

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""Generate one static HTML file per docs section so search engines see real pages.

index.html stays the single source of truth (edit content there). This script writes
pages/<id>.html for every <div class="page" id="..."> except "welcome": same document,
but with that section pre-selected and its own <title>, description, canonical and
og/twitter tags. vercel.json rewrites /<id> to pages/<id>.html. sitemap.xml is rebuilt
from the same list.

Run after editing index.html:  python3 build_pages.py
"""
import html, os, re

BASE = "https://docs.tail.trade"
src = open("index.html", encoding="utf-8").read()

ids = re.findall(r'<div class="page(?: active)?" id="([^"]+)">', src)
pages = []
for pid in ids:
    block = src.split(f'id="{pid}">', 1)[1]
    h1 = html.unescape(re.search(r"<h1>(.*?)</h1>", block, re.S).group(1)).strip()
    m = re.search(r'<p class="page-desc">(.*?)</p>', block, re.S)
    desc = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
    pages.append((pid, h1, desc))

def esc(t):
    return html.escape(t, quote=True)

def set_meta(doc, attr, key, value):
    pat = re.compile(rf'<meta {attr}="{re.escape(key)}" content="[^"]*">')
    assert pat.search(doc), key
    return pat.sub(f'<meta {attr}="{key}" content="{esc(value)}">', doc, count=1)

os.makedirs("pages", exist_ok=True)
for pid, h1, desc in pages:
    if pid == "welcome":
        continue
    title = f"{h1} · Tail.Trade Docs"
    url = f"{BASE}/{pid}"
    d = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", src, count=1)
    d = set_meta(d, "name", "description", desc)
    d = set_meta(d, "property", "og:url", url)
    d = set_meta(d, "property", "og:title", title)
    d = set_meta(d, "property", "og:description", desc)
    d = set_meta(d, "name", "twitter:title", title)
    d = set_meta(d, "name", "twitter:description", desc)
    d = d.replace('<link rel="canonical" href="https://docs.tail.trade/">', f'<link rel="canonical" href="{url}">', 1)
    # pre-select the section so the first paint (and crawlers) show it
    d = d.replace('<div class="page active" id="welcome">', '<div class="page" id="welcome">', 1)
    d = d.replace(f'<div class="page" id="{pid}">', f'<div class="page active" id="{pid}">', 1)
    open(f"pages/{pid}.html", "w", encoding="utf-8").write(d)

urls = [f"{BASE}/"] + [f"{BASE}/{pid}" for pid, _, _ in pages if pid != "welcome"] + [f"{BASE}/privacy/", f"{BASE}/terms_of_use/"]
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls:
        pri = "1.0" if u == f"{BASE}/" else ("0.3" if "privacy" in u or "terms" in u else "0.7")
        f.write(f"  <url><loc>{u}</loc><priority>{pri}</priority></url>\n")
    f.write("</urlset>\n")
print(f"{len(pages) - 1} section pages + sitemap ({len(urls)} urls)")

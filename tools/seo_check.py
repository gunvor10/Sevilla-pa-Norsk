#!/usr/bin/env python3
"""SEO / AI-readiness guard for sevillapanorsk.com — exit 1 if a page breaks the rules.

For every real page (redirect pages skipped):
  - processed by tools/seo_fix.py; lang attribute; <title> and meta description in <head>
  - indexable pages: canonical, hreflang, og:image, valid JSON-LD, listed in sitemap.xml
  - no *.dc.html links, no images without alt text
  - homepages carry the business entity (licence C.I.AN-41-7397-2); llms.txt exists

Usage:  python3 tools/seo_check.py [site_dir]
"""
import json
import os
import re
import sys

root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://sevillapanorsk.com/"
errors, count = [], 0
sitemap = open(os.path.join(root, "sitemap.xml")).read() if os.path.exists(os.path.join(root, "sitemap.xml")) else ""
if not sitemap:
    errors.append("sitemap.xml missing")
if not os.path.exists(os.path.join(root, "llms.txt")):
    errors.append("llms.txt missing")

for d, dirs, files in os.walk(root):
    dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("tools", "uploads")]
    for f in files:
        if not f.endswith(".html"):
            continue
        rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
        s = open(os.path.join(d, f), encoding="utf-8").read()
        if 'http-equiv="refresh"' in s:
            continue
        count += 1
        head, body = s[: s.find("</head>")], s[s.find("</head>"):]
        url = SITE + (rel[:-10] if rel.endswith("index.html") else rel)
        noindex = re.search(r'<meta name="robots" content="[^"]*noindex', head)
        err = lambda m: errors.append(f"{rel}: {m}")
        if "seo-fix: tools/seo_fix.py" not in head:
            err("not processed by tools/seo_fix.py")
        if not re.search(r'<html lang="\w', s):
            err("no lang attribute")
        if not re.search(r"<title>[^<]+</title>", head):
            err("<title> missing from <head>")
        if 'name="description"' not in head:
            err("meta description missing from <head>")
        if re.search(r'href="[^"]*\.dc\.html"', s):
            err("link to a .dc.html file")
        if [i for i in re.findall(r"<img\b[^>]*>", body) if not re.search(r'\balt="[^"]+', i)]:
            err("image without alt text")
        if noindex:
            continue
        for tag, name in (('rel="canonical"', "canonical"), ("hreflang=", "hreflang"), ('property="og:image"', "og:image")):
            if tag not in head:
                err(f"{name} missing")
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        if not lds:
            err("no JSON-LD schema")
        for raw in lds:
            try:
                json.loads(raw)
            except json.JSONDecodeError as e:
                err(f"invalid JSON-LD ({e})")
        if rel in ("index.html", "en/index.html") and "C.I.AN-41-7397-2" not in s:
            err("business entity (licence) missing on homepage")
        if f"<loc>{url}</loc>" not in sitemap:
            err("not in sitemap.xml")

if errors:
    print(f"SEO check FAILED ({len(errors)} problems in {count} pages):")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
print(f"SEO check passed: {count} pages OK.")

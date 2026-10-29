#!/usr/bin/env python3
"""Post-process a Claude Design export of sevillapanorsk.com for search engines and AI assistants.

Run on the site folder after every new Design download (the export replaces all pages):
  1. tour pages: move <title>, meta, links, JSON-LD etc. from the top of <body> into <head>;
  2. every page: lang attribute, canonical, hreflang (nb/en/x-default), Open Graph tags,
     alt text on the logo image, broken *.dc.html links;
  3. structured data: one consistent business entity (Spaniaopplevelser = Come to Spain Events
     SLU, licence, address, sister brands) and Gunvor as Person, referenced by @id from every
     Article / TouristTrip; Article/WebPage schema on pages that had none;
  4. sitemap.xml: add indexable pages that are missing;
  5. llms.txt: rewritten from the pages themselves (always complete) + business facts;
  6. shorter <title>/description from tools/seo_overrides.json (Google cuts ~60 / ~160 chars);
  7. image links to a missing file are pointed at the same image with another extension
     (Design sometimes writes .png for an uploaded .jpg); images below the first get lazy loading.

Run tools/optimize_images.py before this script (it shrinks heavy photos, PNG photos -> JPG).

Redirect pages ("Moved") and noindex pages are left alone. Pages already processed (marker
comment) are skipped, so running it twice is safe.

Usage:  python3 tools/seo_fix.py [site_dir]      (default: the repository root)
"""
import html
import json
import os
import re
import sys
import urllib.parse

SITE = "https://sevillapanorsk.com/"
MARKER = "<!-- seo-fix: tools/seo_fix.py -->"
ORG_ID = SITE + "#organization"
PERSON_ID = SITE + "#gunvor"

# ---- Business facts (keep in sync with flavorsofandalucia.com tools/seo_fix.py) -------------
ORG = {
    "@type": "TravelAgency",
    "@id": ORG_ID,
    "name": "Spaniaopplevelser",
    "legalName": "Come to Spain Events SLU",
    "url": SITE,
    "email": "post@spaniaopplevelser.no",
    "telephone": "+34 637 87 87 68",
    "foundingDate": "2010",
    "founder": {"@id": PERSON_ID},
    "address": {"@type": "PostalAddress", "streetAddress": "Milano Govinda 35", "postalCode": "41020",
                "addressLocality": "Sevilla", "addressRegion": "Andalucía", "addressCountry": "ES"},
    "identifier": {"@type": "PropertyValue", "propertyID": "Licencia de agencia de viajes (Junta de Andalucía)",
                   "value": "C.I.AN-41-7397-2"},
    "areaServed": ["Sevilla", "Andalucía", "Spania"],
    "knowsLanguage": ["no", "en", "sv", "da"],
    "brand": [
        {"@type": "Brand", "name": "Sevilla på norsk", "url": SITE},
        {"@type": "Brand", "name": "Flavors of Andalucía", "url": "https://flavorsofandalucia.com/"},
        {"@type": "Brand", "name": "DMC Seville Event", "url": "https://dmcsevilleevent.com/"},
        {"@type": "Brand", "name": "Sevilla Event", "url": "https://sevillaevent.com/"},
    ],
    "sameAs": ["https://flavorsofandalucia.com/", "https://dmcsevilleevent.com/", "https://sevillaevent.com/"],
}
SOCIAL = ["https://www.instagram.com/sevilla_med_gunvor/", "https://www.facebook.com/SevillamedGunvor/",
          "https://www.linkedin.com/in/gunvor-guttormsen-ba05a728/"]
PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": "Gunvor Guttormsen",
    "worksFor": {"@id": ORG_ID},
    "nationality": "Norwegian",
    "homeLocation": {"@type": "Place", "name": "Sevilla, Spania"},
    "knowsLanguage": ["no", "en", "sv", "da", "es"],
    "sameAs": SOCIAL,
}
PERSON_TXT = {
    "no": {"jobTitle": "Offisiell norsk lisensiert guide i Sevilla og Andalucía", "url": SITE + "om-meg.html"},
    "en": {"jobTitle": "Official Norwegian licensed guide in Seville and Andalucía", "url": SITE + "en/about-gunvor.html"},
}
REF_ORG = {"@type": "TravelAgency", "@id": ORG_ID, "name": "Spaniaopplevelser", "url": SITE}
REF_PERSON = {"@type": "Person", "@id": PERSON_ID, "name": "Gunvor Guttormsen"}

LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
IMG_EXT = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".webp", ".avif")


def load_overrides(root):
    p = os.path.join(root, "tools", "seo_overrides.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def apply_overrides(s, o):
    """Replace title/description (and their og:/twitter: copies) with the shorter versions."""
    if "title" in o:
        t = esc(o["title"])
        s = re.sub(r"<title>.*?</title>", lambda m: f"<title>{t}</title>", s, count=1, flags=re.S)
        og = esc(o["title"].split(" | ")[0])
        s = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*"', lambda m: m.group(1) + og + '"', s)
    if "description" in o:
        d = esc(o["description"])
        s = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*"',
                   lambda m: m.group(1) + d + '"', s)
    return s


def fix_image_refs(s, root):
    """uploads/x.png -> uploads/x.jpg when only the .jpg exists (and the other way round)."""
    files = set(os.listdir(os.path.join(root, "uploads")))

    def repl(m):
        path = m.group(1)
        name = urllib.parse.unquote(path)
        if name in files:
            return m.group(0)
        stem = os.path.splitext(name)[0]
        # x.png -> x.jpg, or x.jpg -> x.jpg.avif (Design keeps the original name + new extension)
        for new in [stem + ext for ext in IMG_EXT] + [name + ext for ext in IMG_EXT]:
            if new in files:
                return "uploads/" + (urllib.parse.quote(new) if "%" in path else new)
        return m.group(0)
    # any syntax: src/href/content attributes, CSS url(...), gallery data in scripts
    return re.sub(r"""uploads/([^"'()<>\\/]+?\.(?:png|jpe?g|webp|avif))(?![\w.])""", repl, s, flags=re.I)


def fix_en_tour_links(s, rel, pairs):
    """Design sometimes links English pages to 'tur-x-EN.html' (does not exist): use the real English page."""
    def repl(m):
        g = pairs.get(SITE + m.group(2) + ".html")
        if not g:
            return m.group(0)
        target = g["en"][len(SITE):]
        return 'href="' + os.path.relpath(target, os.path.dirname(rel) or ".").replace(os.sep, "/") + '"'
    return re.sub(r'href="((?:\.\./)*)([\w-]+)-EN(?:\.dc)?\.html"', repl, s)


def lazy_images(s):
    """Lazy-load every content image except the first (the hero); logos stay eager."""
    head, body = split_head(s)
    seen = [0]

    def repl(m):
        tag = m.group(0)
        if "logo" in tag or "favicon" in tag or "loading=" in tag:
            return tag
        seen[0] += 1
        if seen[0] == 1:
            return tag
        return tag[:-1].rstrip("/").rstrip() + ' loading="lazy" decoding="async">'
    return head + re.sub(r"<img\b[^>]*>", repl, body)


def url_of(rel):
    rel = rel.replace(os.sep, "/")
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return SITE + rel


def is_stub(s):
    return 'http-equiv="refresh"' in s


def lang_of(rel):
    return "en" if rel.startswith("en/") else "no"


def load(root):
    pages = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("tools", "uploads")]
        for f in files:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(d, f), root)
                pages[rel] = open(os.path.join(d, f), encoding="utf-8").read()
    return pages


def language_pairs(pages):
    """Map every page URL to {nb: url, en: url} from existing hreflang tags and redirect stubs."""
    groups = []
    for rel, s in pages.items():
        if is_stub(s):
            continue
        alts = dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', s))
        if "nb" in alts and "en" in alts:
            groups.append({"nb": alts["nb"], "en": alts["en"]})
    # en/bloggposter/<norwegian-slug>.html redirects to the English post -> pair with bloggposter/<slug>.html
    for rel, s in pages.items():
        if not (is_stub(s) and rel.startswith("en/")):
            continue
        m = re.search(r'url=(https://sevillapanorsk\.com/[^"]+)"', s)
        no_rel = rel[3:]
        if m and no_rel in pages and not is_stub(pages[no_rel]):
            groups.append({"nb": url_of(no_rel), "en": m.group(1)})
    out = {}
    for g in groups:
        out.setdefault(g["nb"], g)
        out.setdefault(g["en"], g)
    return out


def split_head(s):
    i = s.find("</head>")
    return s[:i], s[i:]


def move_body_head_block(s):
    """Tour pages: everything between <body> and the first layout element belongs in <head>."""
    head, rest = split_head(s)
    if "<title>" in head:
        return s, False
    bm = re.search(r"<body\b[^>]*>", rest)  # newer exports add attributes, e.g. <body data-restyled="1">
    if not bm:
        return s, False
    after = rest[bm.end():]
    m = re.search(r"<(div|header|nav|main|section|article|a)\b", after)
    block = after[: m.start()] if m else ""
    if "<title>" not in block:
        return s, False
    return head + block.rstrip() + "\n" + rest[: bm.end()] + "\n" + after[m.start():], True


def add_to_head(s, tags):
    if not tags:
        return s
    i = s.find("</head>")
    return s[:i] + "\n".join(tags) + "\n" + s[i:]


def meta(head, attr, name):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(name)), head)
    return html.unescape(m.group(1)) if m else None


def first_image(body, rel):
    for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', body):
        if "favicon" in src or src.startswith("data:"):
            continue
        if src.startswith("http"):
            return src
        return SITE + os.path.normpath(os.path.join(os.path.dirname(rel), src)).replace(os.sep, "/").lstrip("./")
    m = re.search(r"url\('?(\.{0,2}/?uploads/[^')]+)'?\)", body)
    if m:
        return SITE + os.path.normpath(os.path.join(os.path.dirname(rel), m.group(1))).replace(os.sep, "/")
    return None


def esc(v):
    return html.escape(v, quote=True)


def fix_ld_object(o, lang):
    """Point authors/publishers/providers to the shared entities; upgrade the site entities."""
    t = o.get("@type")
    if t == "TravelAgency" and o.get("name") == "Spaniaopplevelser":
        return dict(ORG)
    if t in ("TravelAgency", "Organization") and o.get("name", "").startswith("Flavors of Andal"):
        o["parentOrganization"] = dict(REF_ORG)
        o.setdefault("url", "https://flavorsofandalucia.com/")
    if t == "Person" and o.get("name") == "Gunvor Guttormsen":
        p = dict(PERSON)
        p.update(PERSON_TXT[lang])
        return p
    for k in ("author", "provider", "publisher", "organizer"):
        v = o.get(k)
        if isinstance(v, dict):
            if v.get("name") == "Gunvor Guttormsen":
                o[k] = dict(REF_PERSON, **{x: v[x] for x in ("jobTitle", "url") if x in v})
            elif v.get("name") in ("Spaniaopplevelser", "Sevilla på norsk", "Flavors of Andalucia") or v.get("@type") in (
                    "TravelAgency", "Organization"):
                o[k] = dict(REF_ORG)
    if "@graph" in o:
        o["@graph"] = [fix_ld_object(x, lang) for x in o["@graph"]]
    return o


def process(root):
    pages = load(root)
    pairs = language_pairs(pages)
    overrides = load_overrides(root)
    report = {"processed": [], "skipped": [], "no_language_pair": [], "sitemap_added": []}
    for rel in sorted(pages):
        s = pages[rel]
        if is_stub(s) or MARKER in s:
            report["skipped"].append(rel)
            continue
        noindex = re.search(r'<meta name="robots" content="[^"]*noindex', s) is not None
        lang = lang_of(rel)
        url = url_of(rel)
        changes = []
        s, moved = move_body_head_block(s)
        if moved:
            changes.append("head tags moved")
        s, n = re.subn(r'(<img src="[^"]*uploads/logo-hvit\.png") alt=""', r'\1 alt="Sevilla på norsk"', s)
        if n:
            changes.append("logo alt")
        if rel.replace(os.sep, "/") in overrides:
            s = apply_overrides(s, overrides[rel.replace(os.sep, "/")])
            changes.append("title/description shortened")
        fixed_refs = fix_en_tour_links(fix_image_refs(s, root), rel, pairs)
        if fixed_refs != s:
            s = fixed_refs
            changes.append("image links fixed")
        s = lazy_images(s)
        if not re.search(r"<html\s+lang=", s):
            s = s.replace("<html>", f'<html lang="{lang}">', 1)
            changes.append("lang")
        head, body = split_head(s)
        new = []
        if 'rel="canonical"' not in head and not noindex:
            new.append(f'<link rel="canonical" href="{url}">')
        if "hreflang=" not in head and not noindex:
            g = pairs.get(url)
            if g:
                new += [f'<link rel="alternate" hreflang="nb" href="{g["nb"]}">',
                        f'<link rel="alternate" hreflang="en" href="{g["en"]}">',
                        f'<link rel="alternate" hreflang="x-default" href="{g["nb"]}">']
            else:
                report["no_language_pair"].append(rel)
        title = re.search(r"<title>(.*?)</title>", head, re.S)
        title = html.unescape(title.group(1).strip()) if title else ""
        desc = meta(head, "name", "description") or ""
        is_post = "bloggposter/" in rel
        og = {"og:type": "article" if is_post else "website", "og:title": title.split(" | ")[0],
              "og:description": desc, "og:url": url, "og:locale": "en_GB" if lang == "en" else "nb_NO",
              "og:site_name": "Sevilla på norsk", "og:image": first_image(body, rel)}
        for k, v in og.items():
            if v and meta(head, "property", k) is None:
                new.append(f'<meta property="{k}" content="{esc(v)}">')
        if 'name="twitter:card"' not in head:
            new.append('<meta name="twitter:card" content="summary_large_image">')
        # structured data: upgrade existing, add Article/WebPage where missing
        lds = []
        for raw in LD_RE.findall(s):
            try:
                lds.append(json.loads(raw))
            except json.JSONDecodeError:
                pass
        fixed = [fix_ld_object(json.loads(json.dumps(o)), lang) for o in lds]
        if lds:
            it = iter(fixed)
            s = LD_RE.sub(lambda m: '<script type="application/ld+json">' +
                          json.dumps(next(it), ensure_ascii=False).replace("</", "<\\/") + "</script>", s)
        if not lds and not noindex:
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
            headline = html.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else title
            obj = {"@context": "https://schema.org", "@type": "Article" if is_post else "WebPage",
                   "headline" if is_post else "name": headline, "description": desc, "url": url,
                   "inLanguage": "en" if lang == "en" else "nb-NO", "mainEntityOfPage": url,
                   "author": dict(REF_PERSON), "publisher": dict(REF_ORG)}
            if og["og:image"]:
                obj["image"] = og["og:image"]
            new.append('<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>")
            changes.append("schema added")
        # homepages carry the full entities
        if rel in ("index.html", "en/index.html") and "C.I.AN-41-7397-2" not in s:
            p = dict(PERSON, **PERSON_TXT[lang])
            new.append('<script type="application/ld+json">' + json.dumps(
                {"@context": "https://schema.org", "@graph": [ORG, p]}, ensure_ascii=False) + "</script>")
            changes.append("business entity added")
        s = add_to_head(s, [MARKER] + new)
        # logo images without alt text, broken Design-internal links
        s = re.sub(r'(<img\b[^>]*\bsrc="[^"]*favicon\.png"[^>]*?)\balt=""', r'\1alt="Sevilla på norsk"', s)
        s = re.sub(r'<img((?:(?!alt=)[^>])*?\bsrc="[^"]*favicon\.png"(?:(?!alt=)[^>])*)>',
                   r'<img\1 alt="Sevilla på norsk">', s)
        s = re.sub(r'href="([^"]*?)\.dc\.html"', r'href="\1.html"', s)
        open(os.path.join(root, rel), "w", encoding="utf-8").write(s)
        pages[rel] = s
        report["processed"].append(f"{rel}  ({len(new) - 1} head items{', ' + ', '.join(changes) if changes else ''})")
    # sitemap
    sm_path = os.path.join(root, "sitemap.xml")
    sm = open(sm_path, encoding="utf-8").read()
    for rel, s in sorted(pages.items()):
        if is_stub(s) or re.search(r'<meta name="robots" content="[^"]*noindex', s):
            continue
        u = url_of(rel)
        if f"<loc>{u}</loc>" not in sm:
            sm = sm.replace("</urlset>", f"  <url>\n    <loc>{u}</loc>\n  </url>\n</urlset>")
            report["sitemap_added"].append(u)
    open(sm_path, "w", encoding="utf-8").write(sm)
    write_llms(root, pages)
    return report


def page_line(rel, s):
    head = split_head(s)[0]
    t = re.search(r"<title>(.*?)</title>", head, re.S)
    t = html.unescape(t.group(1)).split(" | ")[0].strip() if t else rel
    d = meta(head, "name", "description") or ""
    return f"- [{t}]({url_of(rel)}): {d}"


def write_llms(root, pages):
    idx = {rel: s for rel, s in pages.items()
           if not is_stub(s) and not re.search(r'<meta name="robots" content="[^"]*noindex', s)}
    sec = lambda pred: [page_line(r, idx[r]) for r in sorted(idx) if pred(r)]
    no = lambda r: not r.startswith("en/")
    tours = lambda r: re.match(r"(en/)?(tur-|tour-)", r) is not None
    lines = [
        "# Sevilla på norsk",
        "",
        "> Norsk blogg og reiseinformasjon fra Sevilla, skrevet av Gunvor Guttormsen — den eneste offisielt "
        "lisensierte norske guiden i Sevilla og Andalucía, bosatt i Sevilla siden 1994. Private turer på norsk "
        "og engelsk, skreddersydde reiser, bryllup og firmaturer.",
        "",
        "## Fakta",
        "- Guide: Gunvor Guttormsen, fra Bergen, bosatt i Sevilla siden 1994. Offisielt lisensiert guide (norsk og engelsk; guider også på svensk og dansk).",
        "- Reisebyrå: Spaniaopplevelser (grunnlagt 2010), drevet av Come to Spain Events SLU, "
        "lisensiert reisebyrå i Andalucía, lisens C.I.AN-41-7397-2. Milano Govinda 35, 41020 Sevilla, Spania.",
        "- Søstermerker: Flavors of Andalucía (https://flavorsofandalucia.com — private mat- og vinturer på engelsk), "
        "DMC Seville Event (https://dmcsevilleevent.com — grupper, firmaturer og MICE), "
        "Sevilla Event (https://sevillaevent.com — bryllup i Spania).",
        "- Kontakt: post@spaniaopplevelser.no · +34 637 87 87 68 (også WhatsApp) · Instagram @sevilla_med_gunvor",
        "- Priser er oppgitt på hver turside. Ingen forhåndsbetaling på egne turer.",
        "",
        "## Turer (norsk)",
        *sec(lambda r: no(r) and tours(r)),
        "",
        "## Sider (norsk)",
        *sec(lambda r: no(r) and not tours(r) and not r.startswith("bloggposter/")),
        "",
        "## Blogginnlegg (norsk)",
        *sec(lambda r: r.startswith("bloggposter/")),
        "",
        "## English",
        *sec(lambda r: r.startswith("en/") and not r.startswith("en/bloggposter/")),
        "",
        "## English blog posts",
        *sec(lambda r: r.startswith("en/bloggposter/")),
        "",
    ]
    open(os.path.join(root, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
    r = process(root)
    for k, v in r.items():
        print(f"\n== {k} ({len(v)})")
        for line in (v if k != "skipped" else v[:5] + (["…"] if len(v) > 5 else [])):
            print("  " + line)

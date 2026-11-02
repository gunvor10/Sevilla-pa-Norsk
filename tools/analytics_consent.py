#!/usr/bin/env python3
"""Cookie consent for Google Analytics + cookieless Cloudflare Web Analytics.

Run on the site folder after pages are added or rebuilt:
  1. Google Analytics (G-EGLLCQ1Z61) starts with analytics cookies DENIED and is only
     switched on when the visitor clicks "Accept" in the cookie banner (Consent Mode v2).
  2. Adds the cookie banner (Accept / Decline, equal buttons) in Norwegian on
     Norwegian pages and in English on English pages. A link or button with data-cookie-settings
     anywhere on the page re-opens it.
  3. Adds Cloudflare Web Analytics (no cookies, no consent needed) when a token is given,
     so every visitor is counted, not only the ones who accept.

Pages already processed (marker comment) are skipped, so running it twice is safe.

Usage:  python3 tools/analytics_consent.py [site_dir] [--cf-token TOKEN]
"""
import glob
import os
import re
import sys

GA_ID = "G-EGLLCQ1Z61"
MARK = "<!-- analytics-consent (tools/analytics_consent.py) -->"
CF_MARK = "<!-- cloudflare-web-analytics -->"

# Both variants Claude Design has produced so far.
GA_CONFIG = re.compile(
    r"<script>\s*window\.dataLayer\s*=\s*window\.dataLayer\s*\|\|\s*\[\];\s*"
    r"function gtag\(\)\{dataLayer\.push\(arguments\);\}\s*"
    r"gtag\('js',\s*new Date\(\)\);\s*gtag\('config',\s*'" + GA_ID + r"'\);\s*</script>"
)

GA_CONSENT = (
    "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
    "var c=null;try{c=localStorage.getItem('spn-consent');}catch(e){}"
    "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',"
    "analytics_storage:c==='yes'?'granted':'denied'});"
    "gtag('js',new Date());gtag('config','" + GA_ID + "');</script>"
)

BANNER = MARK + """
<div id="spn-consent" hidden role="dialog" aria-label="Cookies" style="position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:560px;margin:0 auto;background:#23401F;color:#FFFFFF;font-family:'Cormorant Garamond',Georgia,serif;font-size:16px;line-height:1.5;padding:16px 18px;border-radius:6px;box-shadow:0 6px 24px rgba(0,0,0,.25)">
__TEXT__
<div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap"><button type="button" data-v="yes" style="cursor:pointer;border:1px solid #D9631A;background:#D9631A;color:#fff;font-weight:600;padding:8px 16px;border-radius:3px;font-family:inherit">__YES__</button><button type="button" data-v="no" style="cursor:pointer;border:1px solid #FFFFFF;background:transparent;color:#FFFFFF;font-weight:600;padding:8px 16px;border-radius:3px;font-family:inherit">__NO__</button></div></div>
<script>
(function(){var b=document.getElementById('spn-consent'),v=null;try{v=localStorage.getItem('spn-consent');}catch(e){}
if(!v)b.hidden=false;
b.addEventListener('click',function(e){var x=e.target.getAttribute('data-v');if(!x)return;try{localStorage.setItem('spn-consent',x);}catch(e){}
if(x==='yes')gtag('consent','update',{analytics_storage:'granted'});b.hidden=true;});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-cookie-settings]');if(!a)return;e.preventDefault();
try{localStorage.removeItem('spn-consent');}catch(x){}gtag('consent','update',{analytics_storage:'denied'});
document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(n.indexOf('_ga')===0||n.indexOf('_gid')===0||n.indexOf('_gat')===0){document.cookie=n+'=;Max-Age=0;path=/';document.cookie=n+'=;Max-Age=0;path=/;domain=.sevillapanorsk.com';}});b.hidden=false;});})();
</script>
"""


def cf_beacon(token):
    return (CF_MARK + "\n<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
            "data-cf-beacon='{\"token\": \"" + token + "\"}'></script>\n")


def main():
    args = sys.argv[1:]
    token = None
    if "--cf-token" in args:
        i = args.index("--cf-token")
        token = args[i + 1].strip()
        del args[i:i + 2]
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            sys.exit("The Cloudflare token should be 32 characters (0-9, a-f).")
    root = args[0] if args else os.path.join(os.path.dirname(__file__), "..")
    pages = sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True))
    changed = 0
    for path in pages:
        text = open(path, encoding="utf-8").read()
        new = text
        if GA_ID in new and MARK not in new:
            new, n = GA_CONFIG.subn(GA_CONSENT, new, count=1)
            if n != 1:
                print("WARNING: Google Analytics code not recognised, page left unchanged:", path)
                continue
            no = re.search(r'<html[^>]*lang="(no|nb|nn)', new) is not None
            t = (("Vi bruker Google Analytics-informasjonskapsler for å se hvordan nettstedet brukes. "
                  "Godtar du statistikk-informasjonskapsler?", "Godta", "Avslå") if no else
                 ("We use Google Analytics cookies to see how visitors use our website. "
                  "Do you accept statistics cookies?", "Accept", "Decline"))
            b = BANNER.replace("__TEXT__", t[0]).replace("__YES__", t[1]).replace("__NO__", t[2])
            if "</body>" not in new:
                print("WARNING: no </body>, banner not added:", path)
                continue
            i = new.rfind("</body>")
            new = new[:i] + b + new[i:]
        if token and CF_MARK not in new and "</head>" in new:
            new = new.replace("</head>", cf_beacon(token) + "</head>", 1)
        if new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1
    print(f"{changed} of {len(pages)} pages updated")


if __name__ == "__main__":
    main()

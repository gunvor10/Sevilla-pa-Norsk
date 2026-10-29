#!/usr/bin/env python3
"""Shrink heavy photos in uploads/ (run after copying in a Design export, before seo_fix.py).

  - JPG over 400 KB: max 1600 px on the long side, re-saved at normal JPEG quality (macOS sips);
  - PNG photo (no transparency) over 300 KB: converted to <name>.jpg and the PNG removed —
    seo_fix.py then points the page links at the .jpg.

tools/optimized_images.json remembers the result of every file, so already optimized files are
left alone and the same original always gives the same output (no git churn on re-export).

Usage:  python3 tools/optimize_images.py [site_dir]
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

MAX_PX = 1600
JPG_LIMIT = 400_000
PNG_LIMIT = 300_000


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sips_props(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", "-g", "hasAlpha", p],
                         capture_output=True, text=True).stdout
    props = dict(line.strip().split(": ", 1) for line in out.splitlines()[1:] if ": " in line)
    return int(props.get("pixelWidth", 0)), int(props.get("pixelHeight", 0)), props.get("hasAlpha") == "yes"


def to_jpeg(src, dst):
    w, h, _ = sips_props(src)
    cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "normal"]
    if max(w, h) > MAX_PX:
        cmd += ["-Z", str(MAX_PX)]
    subprocess.run(cmd + [src, "--out", dst], check=True, capture_output=True)


def main(root):
    up = os.path.join(root, "uploads")
    mpath = os.path.join(root, "tools", "optimized_images.json")
    man = json.load(open(mpath)) if os.path.exists(mpath) else {"done": {}, "converted": []}
    before = after = 0
    for name in sorted(os.listdir(up)):
        p = os.path.join(up, name)
        stem, ext = os.path.splitext(name)
        size = os.path.getsize(p)
        if ext.lower() in (".jpg", ".jpeg") and size > JPG_LIMIT and man["done"].get(name) != sha(p):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as t:
                tmp = t.name
            to_jpeg(p, tmp)
            if os.path.getsize(tmp) < size * 0.9:
                os.replace(tmp, p)
                print(f"shrunk     {name}: {size // 1000} KB -> {os.path.getsize(p) // 1000} KB")
                before, after = before + size, after + os.path.getsize(p)
            else:
                os.remove(tmp)
            man["done"][name] = sha(p)
        elif ext.lower() == ".png" and size > PNG_LIMIT and not sips_props(p)[2]:
            target = stem + ".jpg"
            if os.path.exists(os.path.join(up, target)) and name not in man["converted"]:
                if sips_props(p)[:2] == sips_props(os.path.join(up, target))[:2]:
                    os.remove(p)  # same photo already uploaded as .jpg
                    man["converted"].append(name)
                    print(f"png dropped {name}: same image as {target}")
                    before, after = before + size, after
                else:
                    print(f"skipped    {name}: a different {target} already exists")
                continue
            to_jpeg(p, os.path.join(up, target))
            os.remove(p)
            if name not in man["converted"]:
                man["converted"].append(name)
            man["done"][target] = sha(os.path.join(up, target))
            print(f"png -> jpg {name}: {size // 1000} KB -> {os.path.getsize(os.path.join(up, target)) // 1000} KB")
            before, after = before + size, after + os.path.getsize(os.path.join(up, target))
    json.dump(man, open(mpath, "w"), indent=1, sort_keys=True)
    if before:
        print(f"\ntotal: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")))

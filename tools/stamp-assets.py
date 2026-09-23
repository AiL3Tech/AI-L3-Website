"""Stamp CSS and JS links with a content hash.

Without a build step the asset filenames never change, so a browser that
cached them has no way to learn they were edited. Appending a hash of the file
contents changes the URL whenever the file changes, which is what makes any
caching safe. Run this after editing anything in assets/ and before committing.
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = {"assets/css/ail3.css": "css", "assets/js/ail3.js": "js"}

stamps = {}
for rel in ASSETS:
    digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:10]
    stamps[rel] = digest
    print(f"  {rel}  ->  v={digest}")

changed = 0
for page in sorted(ROOT.glob("*.html")):
    text = page.read_text(encoding="utf-8")
    before = text
    for rel, digest in stamps.items():
        text = re.sub(rf'({re.escape(rel)})(\?v=[0-9a-f]+)?', rf'\1?v={digest}', text)
    if text != before:
        page.write_text(text, encoding="utf-8")
        changed += 1

print(f"  stamped {changed} page(s)")

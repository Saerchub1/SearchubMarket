#!/usr/bin/env python3
"""Rebuild sitemap.xml from the homepage and the products/ folder."""
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

SITE = "https://www.searchub.net"
ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()


def lastmod(path: Path) -> str:
    """Last commit date for the file; today if it is new or modified."""
    rel = str(path.relative_to(ROOT))
    if git("status", "--porcelain", "--", rel):
        return TODAY
    return git("log", "-1", "--format=%cs", "--", rel) or TODAY


def indexable(path: Path) -> bool:
    head = path.read_text(encoding="utf-8", errors="ignore")[:5000].lower()
    return "noindex" not in head


entries = []

home = ROOT / "index.html"
if home.exists():
    entries.append((f"{SITE}/", lastmod(home)))

products = ROOT / "products"
if products.is_dir():
    for page in sorted(products.glob("*/index.html")):
        if indexable(page):
            slug = page.parent.name
            entries.append((f"{SITE}/products/{slug}/", lastmod(page)))

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, mod in entries:
    lines += ["  <url>",
              f"    <loc>{escape(loc)}</loc>",
              f"    <lastmod>{mod}</lastmod>",
              "  </url>"]
lines.append("</urlset>")

(ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"sitemap.xml written with {len(entries)} URLs")

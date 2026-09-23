#!/usr/bin/env python3
"""Regenerate page metadata, stamp the assets, then verify the result.

Run this after editing page copy or anything under assets/:

    uv run python tools/build.py

It does three things, in the only order that works:

  1. Rebuild each page's <head>: canonical, robots, icons, Open Graph, Twitter
     and the JSON-LD graph. Everything except the four authored tags (charset,
     viewport, title, description) is generated, so the head is rewritten from
     those rather than patched. Patching is what produced two canonicals and
     two stylesheet links on every page once the asset URLs gained a version
     stamp the patcher did not know about.
  2. Stamp ?v=<content hash> onto the CSS and JS links. The filenames never
     change, so without this a browser holding a cached copy has no way to
     learn the file was edited. The assets are served immutable for a year,
     which is only safe because of this stamp.
  3. Verify, and exit non-zero if anything is wrong. Step 1 must run before
     step 2, because step 1 rewrites the stylesheet link and would drop the
     stamp. Keeping them in one script is what stops that being a trap.

Facts asserted at the end, because each has been wrong at least once:
  - every generated tag appears exactly once per page
  - every stamp matches the real file hash
  - every FAQ and ItemList entry in the schema is visible text on the page
  - the JSON-LD parses
"""
import hashlib
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://ail3tech.com"
BOOK = f"{BASE}/book"
ASSETS = ("assets/css/ail3.css", "assets/js/ail3.js")

# page -> (clean path, social card, breadcrumb label, kind)
PAGES = {
    "index":                     ("/",                          "og-home",       None,                       "home"),
    "msp":                       ("/msp",                       "og-home",       "For MSPs",                 "msp"),
    "ai":                        ("/ai",                        "og-claude",     "For Businesses",           "ai"),
    "escalation-support":        ("/escalation-support",        "og-escalation", "MSP Escalation Support",   "escalation"),
    "claude-launch-program":     ("/claude-launch-program",     "og-claude",     "Claude Launch Program",    "claude"),
    "privacy-policy":            ("/privacy-policy",            "og-logo",       "Privacy Policy",           "legal"),
    "terms-of-use":              ("/terms-of-use",              "og-logo",       "Terms of Use",             "legal"),
    "master-services-agreement": ("/master-services-agreement", "og-logo",       "Master Services Agreement", "legal"),
    "book":                      ("/book",                      "og-logo",       "Book a call",              "book"),
}

ORG = {
    "@type": ["Organization", "ProfessionalService"],
    "@id": f"{BASE}/#organization",
    "name": "AI L3 Tech",
    "alternateName": ["AIL3 Tech", "AIL3"],
    "legalName": "AI L3 Tech Corporation",
    "url": f"{BASE}/",
    "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/img/og-logo.png", "width": 1200, "height": 630},
    "image": f"{BASE}/assets/img/og-logo.png",
    "email": "info@ail3tech.com",
    "slogan": "Senior engineering. Working AI.",
    "description": ("AI L3 Tech provides senior engineering in two forms: white-label L3 escalation "
                    "and project delivery for managed service providers, and Claude AI implementation, "
                    "workflow automation and custom AI applications for growing businesses."),
    "address": {"@type": "PostalAddress", "addressRegion": "IL", "addressCountry": "US"},
    "areaServed": {"@type": "Country", "name": "United States"},
    "knowsAbout": [
        "Level 3 IT support", "MSP escalation support", "White label IT engineering",
        "Microsoft 365 migration", "Microsoft Entra ID", "Conditional Access", "Microsoft Intune",
        "Azure infrastructure", "Server to cloud migration", "Mailbox migration",
        "Claude implementation", "AI workflow automation", "Custom AI applications",
        "AI for law firms", "AI for accounting firms", "AI for real estate agents",
        "AI for contractors", "AI for engineering firms", "AI for landscaping companies",
    ],
    "contactPoint": [{
        "@type": "ContactPoint", "contactType": "sales", "email": "info@ail3tech.com",
        "url": BOOK, "areaServed": "US", "availableLanguage": "English",
    }],
    # sameAs is deliberately absent: the only value available is the spec's
    # placeholder "[LinkedIn company page URL]", and placeholders must not ship.
}

TIERS = [
    ("Essential", 2500, "10 hours included per month, 4-hour escalation response. For 5-10 person MSPs."),
    ("Standard", 5000, "20 hours included per month, 2-hour escalation response. For 10-15 person MSPs."),
    ("Scale", 7500, "40 hours included per month, 1-hour escalation response. For 15+ person MSPs."),
]

SERVICES = {
    "msp": ("White-label L3 escalation support and project delivery for managed service providers",
            "Managed service providers"),
    "escalation": ("Tier 3 IT escalation support for managed service providers",
                   "Managed service providers"),
    "claude": ("White-label Claude AI implementation for managed service providers",
               "Managed service providers"),
    "ai": ("Claude AI implementation, workflow automation and custom AI applications for small "
           "and mid-sized businesses", "Small and mid-sized businesses"),
}

HEAD = """<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="author" content="AI L3 Tech">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/img/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#07111D">

<meta property="og:type" content="website">
<meta property="og:site_name" content="AI L3 Tech">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AI L3 Tech">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">

<link rel="stylesheet" href="assets/css/ail3.css">"""

# tags the generator owns; each must end up on a page exactly once
SINGLETONS = [
    'rel="canonical"', 'name="robots"', 'name="author"', 'rel="manifest"',
    'name="theme-color"', 'property="og:url"', 'property="og:title"',
    'property="og:description"', 'property="og:image"', 'name="twitter:card"',
    'name="twitter:title"', 'name="twitter:image"', 'application/ld+json',
    'assets/css/ail3.css', 'assets/js/ail3.js',
]

strip = lambda s: " ".join(html.unescape(re.sub(r"<[^>]+>", "", s)).split())


def faq_node(doc, url):
    """Built from the rendered <details>, so the schema cannot claim a question
    the page does not show."""
    qa = [{"@type": "Question", "name": strip(q),
           "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
          for q, a in re.findall(
              r"<details>\s*<summary>(.*?)</summary>\s*<p class=\"answer\">(.*?)</p>", doc, re.S)]
    return {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": qa} if qa else None


def examples_node(doc, url):
    """Scoped per card: one dot-all match across the page swallows everything
    between the first heading and the first situation paragraph."""
    items = []
    for card in re.findall(r'<article class="case-card">(.*?)</article>', doc, re.S):
        n = re.search(r"<h3>(.*?)</h3>", card, re.S)
        d = re.search(r'<p class="case-situation">(.*?)</p>', card, re.S)
        if n and d:
            items.append({"@type": "ListItem", "position": len(items) + 1,
                          "name": strip(n.group(1)), "description": strip(d.group(1))})
    if not items:
        return None
    return {"@type": "ItemList", "@id": f"{url}#examples", "name": "Example builds",
            "description": ("Worked examples showing how an AI L3 Tech build is scoped. "
                            "These are illustrative, not client case studies."),
            "numberOfItems": len(items), "itemListElement": items}


def build_graph(doc, url, img, title, desc, label, kind):
    graph = [ORG, {
        "@type": "WebPage", "@id": f"{url}#webpage", "url": url,
        "name": title, "description": desc, "inLanguage": "en-US",
        "isPartOf": {"@id": f"{BASE}/#website"},
        "about": {"@id": f"{BASE}/#organization"},
        "primaryImageOfPage": {"@type": "ImageObject", "url": img},
    }]
    if kind == "home":
        graph.insert(1, {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/",
                         "name": "AI L3 Tech", "inLanguage": "en-US",
                         "publisher": {"@id": f"{BASE}/#organization"}})
    else:
        graph.append({"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": label, "item": url}]})

    if kind in SERVICES:
        stype, aud = SERVICES[kind]
        svc = {"@type": "Service", "@id": f"{url}#service", "serviceType": stype,
               "provider": {"@id": f"{BASE}/#organization"},
               "areaServed": {"@type": "Country", "name": "United States"},
               "audience": {"@type": "BusinessAudience", "name": aud},
               "description": desc}
        if kind == "msp":
            svc["hasOfferCatalog"] = {
                "@type": "OfferCatalog", "name": "AI L3 Tech monthly retainer plans",
                "itemListElement": [{
                    "@type": "Offer", "name": n, "description": d, "price": str(pr),
                    "priceCurrency": "USD", "url": f"{BASE}/msp#pricing",
                    "availability": "https://schema.org/InStock",
                    "priceSpecification": {"@type": "UnitPriceSpecification", "price": str(pr),
                                           "priceCurrency": "USD", "unitCode": "MON",
                                           "unitText": "month", "billingIncrement": 1},
                } for n, pr, d in TIERS]}
        graph.append(svc)

    for node in (examples_node(doc, url), faq_node(doc, url)):
        if node:
            graph.append(node)
    return graph


def main():
    problems = []

    # ---- 1. rebuild each head -------------------------------------------
    print("metadata")
    for name, (path, card, label, kind) in PAGES.items():
        page = ROOT / f"{name}.html"
        doc = page.read_text(encoding="utf-8")
        url = BASE + path
        img = f"{BASE}/assets/img/{card}.png"
        title = html.unescape(re.search(r"<title>(.*?)</title>", doc, re.S).group(1)).strip()
        desc = re.search(r'name="description" content="([^"]*)"', doc).group(1)

        authored = (
            '\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title, quote=False)}</title>\n"
            f'<meta name="description" content="{desc}">\n\n'
        )
        graph = build_graph(doc, url, img, title, desc, label, kind)
        ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                        indent=2, ensure_ascii=False)
        head = (authored
                + HEAD.format(url=url, title=html.escape(title, quote=True), desc=desc, img=img)
                + f'\n<script type="application/ld+json">\n{ld}\n</script>\n')

        open_at = doc.index("<head>") + len("<head>")
        doc = doc[:open_at] + head + doc[doc.index("</head>"):]
        page.write_text(doc, encoding="utf-8")

        types = sorted({t for n in graph for t in
                        ([n["@type"]] if isinstance(n["@type"], str) else n["@type"])})
        print(f"  {name:26s} {len(graph)} nodes  [{', '.join(types)}]")

    # ---- 2. stamp the assets --------------------------------------------
    print("stamps")
    digests = {}
    for rel in ASSETS:
        digests[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:10]
        print(f"  {rel}  v={digests[rel]}")
    for page in ROOT.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        for rel, digest in digests.items():
            text = re.sub(rf"({re.escape(rel)})(\?v=[0-9a-f]+)?", rf"\1?v={digest}", text)
        page.write_text(text, encoding="utf-8")

    # ---- 3. verify --------------------------------------------------------
    print("checks")
    for page in sorted(ROOT.glob("*.html")):
        doc = page.read_text(encoding="utf-8")
        generated = page.stem in PAGES

        for tag in SINGLETONS:
            n = doc.count(tag)
            expected = 1 if (generated or tag.startswith("assets/")) else 0
            if generated and n != 1:
                problems.append(f"{page.name}: {tag} appears {n}x, expected once")

        for rel, digest in digests.items():
            for found in re.findall(re.escape(rel) + r"\?v=([0-9a-f]+)", doc):
                if found != digest:
                    problems.append(f"{page.name}: stale stamp on {rel} ({found} != {digest})")

        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S)
        if m:
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError as e:
                problems.append(f"{page.name}: JSON-LD does not parse: {e}")
                continue
            body = " ".join(strip(doc[doc.index("<body>"):]).split())
            for node in data["@graph"]:
                claims = []
                if node.get("@type") == "FAQPage":
                    claims = [q["name"] for q in node["mainEntity"]]
                elif node.get("@type") == "ItemList":
                    claims = [i["name"] for i in node["itemListElement"]]
                for c in claims:
                    if " ".join(c.split()) not in body:
                        problems.append(f"{page.name}: schema claims '{c[:48]}' which is not visible")

    if problems:
        print("\nFAILED")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"  {len(list(ROOT.glob('*.html')))} pages: tags unique, stamps current, "
          f"schema parses, every claim visible")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Rebuild the social cards and the icon set from the brand kit.

The cards that shipped before this were drawn in the palette the site used
before BRAND-CI.md: near-black #07111D grounds and a lime #A6F43C accent.
Neither is a brand colour. Everything here takes its values from the kit and
its treatment from the live stylesheet, so a shared link looks like the page
it points at:

  ground   navy #1F4480, the colour the kit gives headers and inverted bands
  accent   cyan #00BCED, which is what .accent resolves to on a dark band
  bullet   green #2DB522, matching .eyebrow::before
  type     Archivo for the headline, Open Sans for everything else

The cards are rendered in a real browser rather than composed with a drawing
library, because that is the only way they get the actual webfonts and the
actual letter-spacing the site uses.

  uv run --with playwright --with pillow python tools/brand_assets.py
"""
import pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
LOGO = (IMG / "ail3-logo-white.png").as_uri()

NAVY = (31, 68, 128)
GREEN = (45, 181, 34)
WHITE = (255, 255, 255)

# page -> the card it shares. index and msp used to share one card, which meant
# a shared home link showed the MSP headline.
CARDS = {
    "og-home": ("Advanced intelligence &middot; Level 3 technology",
                'The tech you don&rsquo;t have<br>time to figure out. <span class="a">HANDLED.</span>',
                "From setting up AI safely to fixing the problems your team can&rsquo;t."),
    "og-msp": ("Senior engineering for MSPs",
               'Stop being<br>your team&rsquo;s <span class="a">L3.</span>',
               "Escalations, migrations, and AI projects, handled."),
    "og-escalation": ("MSP escalation support",
                      'The hard tickets<br><span class="a">stop here.</span>',
                      "Confirmed in one business hour, owned to resolution."),
    "og-claude": ("AI for growing businesses",
                  'AI is here.<br>Don&rsquo;t <span class="a">get left behind.</span>',
                  "Claude, built into how your business already runs."),
    "og-logo": ("Advanced intelligence &middot; Level 3 technology",
                'Senior engineering,<br><span class="a">on retainer.</span>',
                "L3 escalation for MSPs. Claude delivery for growing businesses."),
}

TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=Open+Sans:wght@400;600&display=swap">
<style>
  * { box-sizing: border-box; margin: 0; }
  body {
    width: 1200px; height: 630px; overflow: hidden;
    background: #1F4480;
    font-family: 'Open Sans', system-ui, sans-serif;
    display: flex; flex-direction: column;
    padding: 64px 72px;
  }
  /* the one flourish: a cyan rule, which is what the kit names cyan for */
  body::after {
    content: ""; position: fixed; left: 0; top: 0; width: 10px; height: 630px;
    background: #00BCED;
  }
  /* a flex column stretches its children across, which squashed the
     wordmark to the full card width; hold it to its own size */
  .logo { height: 34px; width: auto; align-self: flex-start; }
  .eyebrow {
    display: inline-flex; align-items: center; gap: 10px;
    margin-top: 52px;
    font-size: 15px; font-weight: 600; letter-spacing: .18em;
    text-transform: uppercase; color: rgba(255,255,255,.78);
  }
  .eyebrow::before { content: ""; width: 11px; height: 11px; background: #2DB522; }
  h1 {
    font-family: 'Archivo', system-ui, sans-serif;
    font-weight: 800; font-size: 74px; line-height: 1.08;
    letter-spacing: -.025em; color: #fff; margin-top: 26px;
  }
  .a { color: #00BCED; }
  .sub {
    margin-top: 24px; font-size: 23px; line-height: 1.5;
    color: rgba(255,255,255,.78); max-width: 40ch;
  }
  .foot {
    margin-top: auto; padding-top: 26px;
    border-top: 1px solid rgba(255,255,255,.16);
    display: flex; gap: 26px; align-items: baseline;
    font-size: 15px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
  }
  .foot .dom { color: rgba(255,255,255,.78); }
  .foot .tag { color: #2DB522; }
</style></head><body>
  <img class="logo" src="LOGO_SRC" alt="">
  <p class="eyebrow">EYEBROW</p>
  <h1>HEADLINE</h1>
  <p class="sub">SUBTEXT</p>
  <div class="foot"><span class="dom">ail3tech.com</span><span class="tag">TAGLINE</span></div>
</body></html>"""

TAGLINE = {
    "og-home": "The tech, handled",
    "og-msp": "Be the owner, not the answer",
    "og-escalation": "One business hour",
    "og-claude": "Built around your work",
    "og-logo": "Advanced intelligence",
}


def build_cards(tmp):
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        for name, (eye, head, sub) in CARDS.items():
            html = (TEMPLATE.replace("LOGO_SRC", LOGO).replace("EYEBROW", eye)
                    .replace("HEADLINE", head).replace("SUBTEXT", sub)
                    .replace("TAGLINE", TAGLINE[name]))
            f = tmp / f"{name}.html"
            f.write_text(html, encoding="utf-8")
            pg = ctx.new_page()
            pg.goto(f.as_uri(), wait_until="load")
            pg.wait_for_timeout(1200)          # let the webfonts land
            out = IMG / f"{name}.png"
            pg.screenshot(path=str(out))
            pg.close()
            print(f"  {name + '.png':22s} {out.stat().st_size // 1024:4d}KB")
        ctx.close()
        b.close()


def build_icons():
    """Recolour the mark: the glyphs come from the real logo, so the letterforms
    are the brand's rather than an approximation of them."""
    logo = Image.open(IMG / "ail3-logo-white.png").convert("RGBA")
    W, H = logo.size
    alpha = logo.split()[3]

    # the wordmark sits above the tagline rule, so ignore the bottom third
    top = alpha.crop((0, 0, W, int(H * 0.70)))
    px = top.load()
    cols = [sum(px[x, y] for y in range(0, top.height, 3)) for x in range(W)]
    runs, start = [], None
    for x in range(W):
        if cols[x] > 0 and start is None:
            start = x
        elif cols[x] == 0 and start is not None:
            if x - start > 8:
                runs.append((start, x))
            start = None
    if start is not None:
        runs.append((start, W))
    print(f"  glyph runs: {len(runs)} -> {runs}")
    # The runs come out as single letters: A I L 3 T E C H. The mark is L3,
    # so it spans two of them, and the boundary between them is where the
    # colour changes. Assuming the mark was one middle run put the I from AI
    # on the icon, which is the kind of thing only looking at it catches.
    assert len(runs) >= 4, f"expected the wordmark to split into letters, got {runs}"
    mark_a = runs[2][0]
    mark_b = runs[3][1]
    split_at = runs[3][0]
    ys = [y for y in range(top.height)
          if any(px[x, y] for x in range(mark_a, mark_b))]
    mark = logo.crop((mark_a, min(ys), mark_b, max(ys) + 1))

    # tint: the L stays white, the 3 takes the brand green
    mw, mh = mark.size
    split = split_at - mark_a
    tinted = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
    ma = mark.split()[3].load()
    tp = tinted.load()
    for y in range(mh):
        for x in range(mw):
            a = ma[x, y]
            if a:
                tp[x, y] = (*(WHITE if x < split else GREEN), a)

    def square(size, pad_ratio, bg):
        c = Image.new("RGBA", (size, size), (*bg, 255))
        avail = int(size * (1 - pad_ratio * 2))
        scale = min(avail / mw, avail / mh)
        m = tinted.resize((max(1, int(mw * scale)), max(1, int(mh * scale))), Image.LANCZOS)
        c.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
        return c.convert("RGB")

    # The mark is about 2:1, so inside a square its height is the constraint.
    # At 16px a 10% pad left roughly 8px of glyph and it turned to mush; the
    # tab sizes get almost the whole square.
    targets = [("favicon-16.png", 16, .02), ("favicon-32.png", 32, .04),
               ("apple-touch-icon.png", 180, .16), ("icon-192.png", 192, .14),
               ("icon-512.png", 512, .14), ("icon-maskable-512.png", 512, .26)]
    for name, size, pad in targets:
        im = square(size, pad, NAVY)
        im.save(IMG / name, "PNG", optimize=True)
        print(f"  {name:22s} {size}x{size}  {(IMG / name).stat().st_size // 1024:3d}KB")

    ico = ROOT / "favicon.ico"
    square(64, .10, NAVY).save(ico, "ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print(f"  {'favicon.ico':22s} multi-size  {ico.stat().st_size // 1024:3d}KB")


if __name__ == "__main__":
    tmp = ROOT / ".og-build"
    tmp.mkdir(exist_ok=True)
    print("social cards")
    build_cards(tmp)
    print("icons")
    build_icons()
    for f in tmp.glob("*.html"):
        f.unlink()
    tmp.rmdir()
    print("\ndone")

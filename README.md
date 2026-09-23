# AI L3 Tech — Website

Static rebuild of [ail3tech.com](https://ail3tech.com), built to the AI L3 Tech
full-page design concept. No build step, no framework, no CDN dependency —
open any `.html` file directly in a browser.

## Pages

| File | Source |
|---|---|
| `index.html` | `/` |
| `escalation-support.html` | `/escalation-support/` |
| `terms-of-use.html` | `/terms-of-use/` |
| `privacy-policy.html` | `/privacy-policy/` |
| `master-services-agreement.html` | `/master-services-agreement/` |
| `claude-launch-program.html` | new — no live equivalent |

All copy, pricing, legal text, links, and the copyright line are taken from the
live site. The legal pages preserve the live markup verbatim; only the shell and
styling are new.

**The Claude Launch Program page is MSP-facing.** It sells the AI offer an MSP
resells to its own clients, with four vertical one-pagers (accounting, legal,
contractors, real estate) as white-label collateral. The vertical switcher is an
ARIA tablist: without JavaScript all four panels stay visible, so nothing is
hidden from a reader or a crawler.

Its copy comes from the four `AI_L3_Claude_*.pdf` one-pagers, with two deliberate
departures: the page says **three working sessions** where the PDFs say twelve,
and it calls the offer the **Claude Launch Program** where the PDFs say "Claude
Implementation by AI L3". The PDFs need regenerating to match.

## Design system

Color is sampled directly from the design concept. Everything is a CSS custom
property in `assets/css/ail3.css`.

| Token | Value | Role |
|---|---|---|
| `--ink` | `#07111D` | Page base, dark sections, nav |
| `--ink-deep` | `#050C14` | Footer, deepest bands |
| `--ink-raised` | `#0A1825` | Dark cards and panels |
| `--paper` | `#F3F7F8` | Light sections |
| `--white` | `#FFFFFF` | Light cards |
| `--lime` | `#A6F43C` | CTAs, highlighted words, accents |
| `--blue` / `--blue-soft` | `#1E3A5F` / `#4E86C7` | Hero glow, method kickers |

**Type:** Inter Tight for display (700, `-0.03em` tracking), Inter for body and
UI, both from Google Fonts.

**Language:** square corners throughout (0px radius), 1px hairline dividers,
numbered section tags (`03 / MEASURED IMPACT`), alternating dark → light → dark
bands, `↗` on every call to action.

## Structure

```
index.html
escalation-support.html
terms-of-use.html
privacy-policy.html
master-services-agreement.html
assets/
  css/ail3.css      design tokens + every component
  js/ail3.js        mobile nav, scroll reveal (no dependencies)
  img/              logo, white and ink variants
```

## Rebuilding

After editing page copy, or anything under `assets/`, run:

```bash
uv run python tools/build.py
```

It regenerates every page's metadata, stamps the assets, and then checks its
own work, exiting non-zero if anything is wrong.

The three steps have to happen in that order. Generating metadata rewrites the
stylesheet link, which drops the version stamp, so stamping has to come after.
They used to be two scripts and that ordering was a trap: running them the
wrong way round once left every page with two canonicals, two Open Graph
titles and two stylesheet links. They are one script now so the order cannot
be got wrong.

What the script guarantees on every run:

- each generated tag appears exactly once per page
- the `?v=` stamps match the real file hashes
- the JSON-LD parses
- every FAQ question and example-build name in the schema is visible text on
  the page, so the markup can never claim something a reader cannot see

Only four tags in each `<head>` are authored by hand: charset, viewport,
`<title>` and the meta description. Everything else is generated, so edit
those four in the page and let the script produce the rest.

`assets/css/ail3.css` and `assets/js/ail3.js` are served immutable for a year,
which is only safe because their URLs carry the content hash. Images under
`assets/img/` are cached for a week with revalidation and carry no hash.

## Conventions

- **Arrow direction carries meaning.** A link that scrolls within the current
  page uses the down arrow; a link that leaves the page, goes to another page,
  or opens the booking widget uses the up-right arrow. Keep this consistent
  when adding links, or the arrow stops being information.
- **Punctuation.** Em dashes are not a rhythm device. Comma for appositives and
  conjunctions, full stop for independent clauses, colon to introduce a list,
  parentheses where an aside has its own commas. The whole site runs on 7.
- **US English**, always. Watch `-our`, `-ise`, `-re`, and vocabulary.
- **Never "firm."** Use company, companies, practice, or client.
- **Social cards** live in `assets/img/og-*.png` at 1200x630 and are generated
  from a brand template, not hand-made. A new page picks the closest existing
  card or gets a new one.
- **The legal pages carry a jump-link index** built from their `h2` ids. Adding
  a section means adding an `id` and a matching `.legal-toc` entry.

- **Booking CTA** points at the LeadConnector widget. It appears in the nav,
  the hero, every pricing card, and the closing CTA — change it in one place
  per page.
- **Contact** is `info@ail3tech.com`.
- **Adding a section:** copy an existing `<section class="section band-*">`,
  give it a `section-tag` with the next number, and add `reveal` or
  `reveal-stagger` for the scroll animation.
- **Accessibility:** skip link, visible focus rings, 44px minimum touch
  targets, and `prefers-reduced-motion` disables all motion.

## Verification

Checked at 375 / 768 / 1024 / 1440 px: no console errors, no page errors, no
horizontal overflow.

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

All copy, pricing, legal text, links, and the copyright line are taken from the
live site. The legal pages preserve the live markup verbatim; only the shell and
styling are new.

## Design system

Colour is sampled directly from the design concept. Everything is a CSS custom
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

## Conventions

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

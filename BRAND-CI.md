# AI L3 Tech — Brand CI for the website

Advanced Intelligence · Level 3 Technology

Source: `Brand Palette-print.pdf` (AI L3 Tech Brand Kit, one page, 792×612pt).
Every colour below was read from the PDF text layer **and** sampled from the
rendered page; all five swatches matched their stated hex value exactly.

This document is the source of truth for the website. Where it adds anything the
PDF does not state, the addition is marked **[derived]** and the reason is given.

---

## 1. Colours

| Role | Name | Hex | RGB | The brand kit's stated use |
|---|---|---|---|---|
| Primary | Navy Blue | `#1F4480` | 31 · 68 · 128 | Headers, key UI, and the default navy + white layout |
| Secondary | Green | `#2DB522` | 45 · 181 · 34 | Innovation: bullets, highlights, AI content, CTAs |
| Accent | Cyan | `#00BCED` | 0 · 188 · 237 | Underlines, borders, and interactive elements |
| Text | Near-Black | `#1A1A1A` | 26 · 26 · 26 | Body text. Use in place of pure black |
| Background | Off-White | `#F5F7FA` | 245 · 247 · 250 | Page background. Use in place of pure white |

Two instructions in that table are easy to miss and both are absolute:

- **Never pure black.** Body text is `#1A1A1A`.
- **Never pure white as the page.** The page is `#F5F7FA`. White may still be used
  for cards and panels that need to lift off the page.

The kit's own layout demonstrates the intended feel: a navy header band, an
off-white page, near-black body copy, and cyan used only as a thin rule beside a
section title and as small labels on navy. Green appears once, on a number.

---

## 2. Typography

| Role | Family | Weights | Notes |
|---|---|---|---|
| Display & headings | **Archivo** | 700 / 800 | The kit sets headings in navy |
| Body & UI | **Open Sans** | 400 / 600 | |
| Data & metrics | **IBM Plex Mono** | 400 / 600 | Shown as "Plex Mono"; the released family is IBM Plex Mono |

Use the mono face for what it is named for: figures, uptime, response times,
hours, prices, tier labels. It is not a body face and not a heading face.

---

## 3. Measured contrast

Every pair below was computed, not estimated. WCAG needs 4.5:1 for body text,
3:1 for large text (24px, or 18.66px bold) and 3:1 for the boundary of a control.

### Text on a surface

| | on Off-White | on White | on Navy | on Green | on Cyan | on Near-Black |
|---|---|---|---|---|---|---|
| **Navy** | 8.91 | 9.56 | — | 3.53 | 4.29 | 1.82 |
| **Green** | 2.53 | 2.71 | 3.53 | — | 1.22 | 6.42 |
| **Cyan** | 2.08 | 2.23 | 4.29 | 1.22 | — | 7.80 |
| **Near-Black** | 16.22 | 17.40 | 1.82 | 6.42 | 7.80 | — |
| **White** | 1.07 | — | 9.56 | 2.71 | 2.23 | 17.40 |

### What that forces

The palette is sound, but two of the three brand colours are light. Used
literally on a light page they fail, so the rules below are not stylistic
preferences, they are what the numbers allow.

**Green `#2DB522`**
- ✅ As a **fill** carrying near-black text — 6.42:1. This is the CTA case.
- ❌ As a fill carrying **white** text — 2.71:1. A green button with white text
  fails. Green CTAs take near-black text.
- ❌ As **text** on the page — 2.53:1.
- ✅ As text on near-black — 6.42:1.

**Cyan `#00BCED`**
- ✅ As a **fill** carrying near-black text — 7.80:1.
- ❌ As **text** on the page — 2.08:1.
- ❌ As a **border on the page** — 2.08:1, under the 3:1 a control boundary needs.
  The kit names cyan for "underlines, borders", and on navy that works (4.29:1);
  on the off-white page it does not.
- ✅ On navy or near-black — 4.29:1 and 7.80:1.

**Navy `#1F4480`** is the only brand colour that is safe as text on the page
(8.91:1), and the only one that takes white text (9.56:1).

---

## 4. Derived variants **[derived]**

The brand colours stay exactly as issued for fills and large graphics. These
darker siblings exist only for the cases above where the issued colour cannot
reach the threshold. Each holds the original hue and drops only lightness, so it
still reads as the brand colour.

| Token | Hex | On off-white | Use for |
|---|---|---|---|
| `--green-text` | `#1E7A16` | 5.08:1 | Green as body text or a small icon on the page |
| `--cyan-text` | `#00738F` | 5.08:1 | Cyan as body text or a link on the page |
| `--green-line` | `#279E1D` | 3.26:1 | A green rule, border or control edge on the page |
| `--cyan-line` | `#0092B8` | 3.37:1 | A cyan underline, border or control edge on the page |

Rule of thumb: **issued colour for areas, derived colour for lines and letters.**

---

## 5. Applying it

### Surfaces
- Page: `#F5F7FA`
- Cards and panels that must lift: `#FFFFFF`
- Header, footer and any inverted band: `#1F4480`
- Deep band, where a second dark is wanted: near-black `#1A1A1A`

### Text
- Body: `#1A1A1A` on light, `#FFFFFF` on navy
- Headings: `#1F4480` on light, `#FFFFFF` on navy
- Muted: a near-black tint, not grey drawn from nowhere

### Actions
- Primary CTA: green `#2DB522` with **near-black** text
- Primary CTA on a navy band: white fill with navy text
- Secondary: navy outline on light, white outline on navy, each at 3:1 or better
- Focus ring: cyan is fine on navy; on light use `--cyan-line` or navy

### Accent
- Cyan is a rule, an underline, a small label on navy, a divider. It is never a
  paragraph and never the only thing marking a control on a light page.
- Green marks innovation and AI: bullets, highlights, metrics, the CTA.

### Motion and shape
Nothing in the kit specifies either. Keep whatever the site already does.

---

## 6. Compliance checklist

A build is brand compliant when all of these hold:

- [ ] No pure black `#000000` and no pure white page background
- [ ] Every colour on the page belongs to the five issued colours, the four
      derived variants, or a tint of near-black
- [ ] Archivo on headings, Open Sans on body and UI, IBM Plex Mono on figures
- [ ] No green or cyan text on a light surface
- [ ] No white text on green or cyan
- [ ] Every control boundary reaches 3:1 against what is behind it
- [ ] Every body text pair reaches 4.5:1, every large text pair 3:1

---

*Extracted from `Brand Palette-print.pdf` and verified against a render of the
same page. Contrast figures computed with the WCAG 2.x relative luminance
formula.*

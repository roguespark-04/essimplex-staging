# ESSIMPLEX redesign: brief and design system

## Brief
- **Visitors:** datacenter construction, commissioning and cable-verification people; integrators and buyers who read this on a phone on the floor and on a desktop at a desk. Phone (390) and desktop (1440) are co-primary.
- **Mode:** Persuade. One primary action: write to support@essimplex.com. Second: read about Nody Bot.
- **Reference (user-approved):** corporate infrastructure company, Applied Digital register, made distinctive as precision monitoring equipment.
- **Truth:** no invented customers, stats or claims. Every fact comes from the existing copy. No hardware component, board, chip, protocol or endpoint detail anywhere. Ethernet and USB-C may be named.
- **Scene:** a project engineer under hall lighting, checking whether a cable drop is still alive. Dark charcoal opens each page (instrument housing); warm off-white sections follow (printed readout).

## Thesis
The site is one calibrated trace. A copper heartbeat line is the signature: it draws across the hero, and again as the check-in sequence scrolls (wake, connect, report, confirm, sleep). The default arrangement it refuses: centered hero over a grid of icon cards.

## Direction rules
- Left-aligned, asymmetric grid; hairline rules (copper) for structure instead of boxes and cards.
- Monospace only for readings: spec keys and values, trace annotations, status chips.
- No kicker above headings, no icon tiles, no stat band, no gradients, no glow, no blur, no hexagon motifs (the logo mark is the only hexagon, untouched).
- Green appears once: a 8px static status dot.

## Tokens (see `styles.css :root`)
**Fonts (self-hosted, latin subset, font-display swap):** Archivo variable (wght 400-800, wdth 100-125) for display, headings and body; Martian Mono 400/500 for readings. Display uses wdth ~112 for the instrument-label feel; body stays at wdth 100.

**Type scale (rem):** label 0.8125 mono / small 0.9375 / body 1.0625 / lede 1.25 / h3 1.25 / h2 clamp(1.875, 4.4vw, 3) / display clamp(2.5, 7.4vw, 5.25). Body line-height 1.6, display 1.04, display tracking -0.02em.

**Color (OKLCH roles):** ink-950 charcoal (page, header, hero), ink-900 (raised on dark), ink-800 (rules on dark); paper (warm off-white ground), paper-2 (recess), copper base ~#8B6440 (oklch .54 .075 60) for hairlines and fills on paper, copper-ink (darker, text on paper, AA), copper-bright (lines and fills on dark). Text roles for both grounds are tinted toward the copper hue. Strategy: Restrained, with copper as the single accent.

**Spacing (4px base):** 4 8 12 16 20 24 32 40 48 64 80 96 128. Section padding clamp(64px, 10vw, 128px); groups 16-24; more space above headings than below.

**Radius:** 2px (hairline parts), 4px (buttons, plates). Concentric where nested (plate 6 / inner 2).

**Shadow:** layered ring + soft drop for plates; borders only for dividers and focus.

**Motion:** durations 80/150/250/350/500ms, ease `cubic-bezier(.22,1,.36,1)`; authored moment = the trace (clip reveal, 1.4s one-shot in hero, scroll-scrubbed in the sequence). Everything else is quick state feedback (150ms). Press scale .96. Reduced motion: trace fully drawn, no movement. No JS: everything visible.

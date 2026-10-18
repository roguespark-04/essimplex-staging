#!/usr/bin/env python3
"""Generates the static HTML pages. Run from the repo root: python3 tools/build.py
Output is plain, committed HTML; this script only avoids repeating the header, footer and trace SVGs."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIL = "mailto:support@essimplex.com?subject=ESSIMPLEX%20inquiry"
MAIL_NB = "mailto:support@essimplex.com?subject=Nody%20Bot%20inquiry"
MAIL_DS = "mailto:support@essimplex.com?subject=Nody%20Bot%20datasheet%20request"
ARROW = '<svg class="ico-arrow" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M2 8h11M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ---------- wire geometry ----------
import math

def offset_poly(pts, d):
    """Parallel copy of a polyline at distance d (mitered joins), so 45-degree bends stay crisp."""
    segs = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        segs.append(((x2 - x1) / L, (y2 - y1) / L))
    norms = [(dy, -dx) for dx, dy in segs]
    out = [(pts[0][0] + norms[0][0] * d, pts[0][1] + norms[0][1] * d)]
    for i in range(1, len(pts) - 1):
        n1, n2 = norms[i - 1], norms[i]
        k = d / (1 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((pts[i][0] + (n1[0] + n2[0]) * k, pts[i][1] + (n1[1] + n2[1]) * k))
    out.append((pts[-1][0] + norms[-1][0] * d, pts[-1][1] + norms[-1][1] * d))
    return out

def d_of(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def plen(pts):
    return sum(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:]))

# Per-wire pulse timing: every wire gets its own duration and start delay, so the light
# passes along the bundle at staggered times instead of in step. (seconds)
PULSE_DUR = [7.4, 5.6, 8.8, 6.2, 9.6, 5.1, 7.9, 6.8]
PULSE_DELAY = [1.6, 4.1, 0.8, 5.6, 2.9, 7.2, 3.4, 6.1]

def bundle(pts, n, gap, main_cls="w-main", other_cls="w-line", pulses=True, po=1.0, salt=0):
    """n parallel wires, the middle one is the bright main wire.
    Returns (line markup, pulse markup, main path d). Each wire has a crisp pulse dash on a duplicate path."""
    lines = ""
    pls = ""
    mid = n // 2
    for i in range(n):
        d = (i - mid) * gap
        p = pts if d == 0 else offset_poly(pts, d)
        lines += f'<path class="{main_cls if i == mid else other_cls}" d="{d_of(p)}"/>'
        if pulses:
            k = (i + salt) % len(PULSE_DUR)
            cls = "w-pulse" if i == mid else "w-pulse w-pulse--s"
            end = -(plen(p) + 80)
            pls += (f'<path class="{cls}" style="--end:{end:.0f};--po:{po};animation-duration:{PULSE_DUR[k]}s;'
                    f'animation-delay:{PULSE_DELAY[k]}s" d="{d_of(p)}"/>')
    return lines, pls, d_of(pts)

def pad(x, y, r=5):
    return f'<circle class="w-pad" cx="{x}" cy="{y}" r="{r}"/>'

def wires_svg(cls, vb, par, body, y0=0):
    w, h = vb
    return f'<svg class="{cls}" viewBox="0 {y0} {w} {h}" preserveAspectRatio="{par}" aria-hidden="true" focusable="false">{body}</svg>'

# Hero wire routes. Each variant is drawn for its own size and scaled uniformly (never stretched),
# so the 45-degree bends stay true on every screen. The hero main wire carries a node at each end:
# a start node near the left edge and an end node near the right edge, inset so both stay on screen.
def hero_wires(kind):
    parts = []
    if kind == "home":
        # phone: below the text, short route (box ratio = viewBox ratio, so the whole width is always visible)
        m = [(-60, 205), (120, 205), (210, 115), (470, 115)]
        l, p, _ = bundle(m, 5, 9, salt=0)
        parts.append(wires_svg("w-narrow", (400, 152), "xMidYMid slice", l + p + pad(24, 205, 5) + pad(376, 115, 5), y0=88))
        # tablet and small laptop: below the text, full-width route
        m = [(-100, 185), (430, 185), (540, 75), (1300, 75)]
        l, p, _ = bundle(m, 5, 12, salt=1)
        parts.append(wires_svg("w-mid", (1200, 230), "xMidYMid slice", l + p + pad(40, 185, 7) + pad(1160, 75, 7)))
        # desktop: rises on the right, clear of the headline column. The start node sits in its own
        # left-anchored layer (same scale and vertical anchor) so it stays at the left edge at any width.
        m = [(-300, 470), (650, 470), (950, 170), (1900, 170)]
        l, p, _ = bundle(m, 5, 14, salt=0)
        f = [(1900, 64), (1262, 64), (1198, 0), (1198, -400)]
        fl, fp, _ = bundle(f, 3, 12, other_cls="w-line w-faint", main_cls="w-line w-faint", po=0.5, salt=5)
        parts.append(wires_svg("w-wide", (1440, 520), "xMaxYMax slice", fl + l + fp + p + pad(1410, 170, 6)))
        parts.append(wires_svg("w-wide w-wide--l", (1440, 520), "xMinYMax slice", pad(30, 470, 6)))
    else:
        m = [(-60, 100), (120, 100), (160, 60), (470, 60)]
        l, p, _ = bundle(m, 4, 9, salt=3)
        parts.append(wires_svg("w-narrow", (400, 120), "xMidYMid slice", l + p + pad(24, 100, 5) + pad(376, 60, 5)))
        m = [(-100, 120), (560, 120), (610, 70), (1300, 70)]
        l, p, _ = bundle(m, 5, 12, salt=5)
        parts.append(wires_svg("w-mid", (1200, 160), "xMidYMid slice", l + p + pad(40, 120, 7) + pad(1160, 70, 7)))
    return "".join(parts)

def hero_trace(kind):
    if kind == "home":
        label = "Illustration: a bundle of parallel wires running from a field problem to a finished device, with short pulses of light travelling along the wires."
        legend = "<span>Field problem</span><span>Ready to install</span>"
    else:
        label = "Illustration: a bundle of parallel wires running from Nody Bot to your collector, with short pulses of light travelling along the wires."
        legend = "<span>Nody Bot</span><span>Your collector</span>"
    return f'''<div class="wires wires--{kind}" data-wires role="img" aria-label="{label}">
        {hero_wires(kind)}
      </div>
      <div class="wrap">
        <p class="wires-legend reading" aria-hidden="true">{legend}</p>
      </div>'''

# Check-in sequence route: one wire, a junction pad per step.
SEQ_N = [(36, 105), (108, 78), (180, 42), (252, 78), (324, 105)]      # 360 x 130
SEQ_W = [(100, 190), (300, 140), (500, 70), (700, 140), (900, 190)]   # 1000 x 240
def seq_route(nodes, bend):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4) = nodes
    s1 = abs(y0 - y1); s2 = abs(y1 - y2)
    a, b2 = bend
    return [(-40, y0), (x0 + a, y0), (x0 + a + s1, y1), (x1 + b2, y1), (x1 + b2 + s2, y2), (x2 + a, y2),
            (x2 + a + s2, y3), (x3 + b2, y3), (x3 + b2 + s1, y4), (x4 + 10, y4), (1040 if nodes is SEQ_W else 400, y4)]

def clip_defs(cid, w):
    # SVG clipPath (works in every browser that draws SVG); app.js sets the rect width as you scroll.
    # Without JS the rect is wide enough to show the whole wire.
    return f'<defs><clipPath id="{cid}"><rect class="seq-clip" data-w="{w}" x="-100" y="-100" width="1300" height="500"/></clipPath></defs>'

def seq_svgs():
    pn = seq_route(SEQ_N, (20, 16))
    aux_n = "".join(f'<path class="t-aux" d="{d_of(offset_poly(pn, d))}"/>' for d in (-7, 7))
    track_n = "".join(f'<path class="t-track" d="{d_of(offset_poly(pn, d) if d else pn)}"/>' for d in (-7, 0, 7))
    narrow = wires_svg("t-narrow", (360, 130), "xMidYMid meet",
                       clip_defs("seqclip-n", 360) + aux_n + track_n + f'<path class="t-line" clip-path="url(#seqclip-n)" d="{d_of(pn)}"/>')
    pw = seq_route(SEQ_W, (60, 60))
    aux_w = "".join(f'<path class="t-aux" d="{d_of(offset_poly(pw, d))}"/>' for d in (-10, 10))
    track_w = f'<path class="t-track" d="{d_of(pw)}"/>'
    drops = "".join(f'<path class="t-drop" d="M{x},{y + 16} V226"/>' for x, y in SEQ_W)
    wide = wires_svg("t-wide", (1000, 240), "xMidYMid meet",
                     clip_defs("seqclip-w", 1000) + drops + aux_w + track_w + f'<path class="t-line" clip-path="url(#seqclip-w)" d="{d_of(pw)}"/>')
    return narrow + wide

def seq_diagram(steps, compact):
    markers = "".join(
        f'<span class="seq__marker" data-at="{xn/360:.3f}" style="--x:{xn/360*100:.2f}%;--yn:{yn/130:.4f};--ynw:{yw/240:.4f}" aria-hidden="true">{i+1}</span>'
        for i, ((xn, yn), (xw, yw)) in enumerate(zip(SEQ_N, SEQ_W)))
    items = ""
    for i, (title, text, note) in enumerate(steps):
        items += f'''
          <li class="seq__step" data-node="{i}">
            <span class="reading seq__num" aria-hidden="true">{i+1}</span>
            <h3 class="h3">{title}</h3>
            <p>{text}</p>
            <p class="reading reading-note">{note}</p>
          </li>'''
    cls = "seq seq--compact" if compact else "seq"
    return f'''<div class="{cls}" data-seq>
        <div class="seq__strip">
          <div class="seq__plot trace" data-trace role="img" aria-label="Check-in route as a single wire with five junctions: wake, connect, report, confirm, sleep. The wire lights up as you scroll.">
            {seq_svgs()}
            {markers}
          </div>
          <p class="seq__axis reading" aria-hidden="true"><span>Wake</span><span>~15 min to next wake</span></p>
        </div>
        <ol class="seq__steps" role="list">{items}
        </ol>
      </div>'''

# ---------- shared chrome ----------
def head(title, desc, canon="https://essimplex.com/"):
    return f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
  <meta name="robots" content="noindex, nofollow">
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{canon}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="ESSIMPLEX" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canon}" />
  <meta property="og:image" content="https://essimplex.com/assets/essimplex-og.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="ESSIMPLEX logo" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="https://essimplex.com/assets/essimplex-og.png" />
  <meta name="theme-color" content="#1E1E20" />
  <link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32" />
  <link rel="icon" href="assets/favicon-16.png" type="image/png" sizes="16x16" />
  <link rel="icon" href="assets/icon-192.png" type="image/png" sizes="192x192" />
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png" sizes="180x180" />
  <link rel="preload" href="assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="assets/fonts/martian-mono.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="styles.css" />
  <script>document.documentElement.className = document.documentElement.className.replace("no-js", "js");</script>
  <script src="app.js" defer></script>
</head>
'''

def header(nav, cta_href):
    items = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if cur else ""}>{t}</a></li>' for t, h, cur in nav)
    return f'''  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header" id="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="index.html" aria-label="ESSIMPLEX home">
        <img src="assets/essimplex-mark-sm-light.png" width="26" height="32" alt="" />
        <span class="brand-name">ESSIMPLEX</span>
      </a>
      <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="primary-nav">
        <span class="nav-toggle__bars" aria-hidden="true"></span><span class="nav-toggle__label">Menu</span>
      </button>
      <nav class="nav" id="primary-nav" aria-label="Primary">
        <ul class="nav__list">{items}</ul>
        <a class="btn btn--primary btn--sm nav__cta" href="{cta_href}">Contact sales</a>
      </nav>
    </div>
  </header>
'''

FOOTER = '''  <footer class="site-footer ground-dark">
    <div class="wrap">
      <div class="footer__top">
        <div class="footer__brand">
          <a class="brand" href="index.html" aria-label="ESSIMPLEX home">
            <img src="assets/essimplex-mark-sm-light.png" width="26" height="32" alt="" loading="lazy" />
            <span class="brand-name">ESSIMPLEX</span>
          </a>
          <p>Custom design and hardware products for industry. Nody Bot is our first product.</p>
          <a class="footer__mail" href="mailto:support@essimplex.com?subject=ESSIMPLEX%20inquiry">support@essimplex.com</a>
        </div>
        <div class="footer__cols">
          <nav class="footer__col" aria-label="Products">
            <h2>Products</h2>
            <ul>
              <li><a href="nody-bot.html">Nody Bot</a></li>
              <li><a href="nody-bot.html#how">How it works</a></li>
              <li><a href="nody-bot.html#specs">Specifications</a></li>
            </ul>
          </nav>
          <nav class="footer__col" aria-label="Company">
            <h2>Company</h2>
            <ul>
              <li><a href="index.html#capabilities">Capabilities</a></li>
              <li><a href="about.html">About</a></li>
              <li><a href="index.html#contact">Contact</a></li>
            </ul>
          </nav>
          <nav class="footer__col" aria-label="Legal">
            <h2>Legal</h2>
            <ul>
              <li><a href="privacy.html">Privacy policy</a></li>
              <li><a href="terms.html">Terms of use</a></li>
            </ul>
          </nav>
        </div>
      </div>
      <div class="footer__bottom">
        <p>&copy; 2026 ESSIMPLEX. All rights reserved.</p>
        <a class="text-link" href="#main">Back to top <svg class="ico-arrow" viewBox="0 0 16 16" aria-hidden="true" focusable="false" style="transform:rotate(-90deg)"><path d="M2 8h11M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
      </div>
    </div>
  </footer>
</body>
</html>
'''

def close(h2, lede, mail_href):
    return f'''    <section class="close ground-dark-2" id="contact" aria-labelledby="contact-heading">
      <div class="wrap close__grid">
        <div class="close__copy">
          <h2 class="h2" id="contact-heading">{h2}</h2>
          <p class="lede on-dark-2 muted">{lede}</p>
        </div>
        <div class="close__action">
          <a class="close__mail" href="{mail_href}">support@essimplex.com</a>
          <div class="actions">
            <a class="btn btn--primary" href="{mail_href}">Email sales {ARROW}</a>
            <a class="btn btn--ghost" href="__OTHER_HREF__">__OTHER_LABEL__</a>
          </div>
        </div>
      </div>
    </section>
'''

def plate(on_dark, rows, title="Nody Bot", chip="Preliminary", foot="Outbound only &middot; not pingable", uid="plate"):
    r = "".join(f'<div><dt class="reading">{k}</dt><dd{" class=\"reading\"" if mono else ""}>{v}</dd></div>' for k, v, mono in rows)
    return f'''<aside class="plate{" plate--on-dark" if on_dark else ""}" aria-labelledby="{uid}">
            <div class="plate__inner">
              <div class="plate__head"><h2 class="plate__title" id="{uid}">{title}</h2><span class="plate__chip reading">{chip}</span></div>
              <dl class="plate__rows">{r}</dl>
              <p class="plate__foot reading">{foot}</p>
            </div>
          </aside>'''

PLATE_ROWS = [("Connection", "Wired Ethernet", False), ("Power", "Battery", False), ("Setup", "USB", False), ("Check-in", "~15 min", False)]

SEQ_SHORT = [
    ("Wake", "A timer fires about every 15 minutes.", "timer"),
    ("Connect", "Wired Ethernet comes up and gets an address.", "Ethernet"),
    ("Report", "A heartbeat goes to your collector.", "outbound"),
    ("Confirm", "It waits for your collector to confirm.", "confirmed"),
    ("Sleep", "Back to sleep. Nothing listens in between.", "asleep"),
]
SEQ_LONG = [
    ("Wake", "A timer fires about every 15 minutes. Between wakes it sleeps with nothing listening, so the battery lasts the build schedule.", "~15 min, configurable"),
    ("Connect", "Wired Ethernet comes up and the unit gets an address on the plant network.", "wired Ethernet, no Wi-Fi dependency"),
    ("Report", "The unit sends a heartbeat to your collector so you know the drop is still alive.", "outbound only"),
    ("Confirm", "The unit waits for your collector to confirm the check-in, retrying if needed.", "confirmed check-in"),
    ("Sleep", "It returns to sleep until the next wake. Nothing listens in between, so it is never pingable.", "asleep"),
]

# ---------- pages ----------
def index():
    nav = [("Nody Bot", "nody-bot.html", False), ("Capabilities", "#capabilities", False), ("About", "about.html", False)]
    t = "ESSIMPLEX | Custom design and hardware products for industry"
    d = "ESSIMPLEX designs and builds practical hardware for demanding environments: custom design and hardware products for industry, starting with Nody Bot."
    caps = [
        ("Custom design", "Hardware engineered around a specific field problem, from requirements to a working device."),
        ("Industrial products", "Practical devices built for demanding environments, starting with datacenter construction."),
        ("Honest specifications", "We publish what the device does. Preliminary parameters are labeled as preliminary."),
    ]
    rows = "".join(f'''
          <li class="ruled__row"><h3 class="h3">{a}</h3><p>{b}</p></li>''' for a, b in caps)
    approach = [
        ("The field problem", "We start from a specific problem in the field."),
        ("The device", "Hardware engineered around it, from requirements to a working device."),
        ("Ready to install", "Units are configured on the bench and shipped ready for the install crew."),
    ]
    steps = "".join(f'''
          <li class="prov__item"><span class="reading" aria-hidden="true">{i}</span><div><h3 class="h3">{a}</h3><p>{c}</p></div></li>''' for i, (a, c) in enumerate(approach, 1))
    body = f'''<body class="page-home">
{header(nav, MAIL)}
  <main id="main">
    <section class="hero hero--home ground-dark" aria-labelledby="hero-heading">
      <div class="wrap hero__content">
        <div class="hero__copy">
          <h1 class="display" id="hero-heading">Practical hardware for demanding environments.</h1>
          <p class="hero__descriptor">Custom design and hardware products for industry. We take a field problem, design the device that solves it, and ship it ready to install.</p>
          <div class="actions">
            <a class="btn btn--primary" href="{MAIL}">Talk to us {ARROW}</a>
            <a class="btn btn--ghost" href="#capabilities">What we build</a>
          </div>
        </div>
      </div>
      {hero_trace("home")}
    </section>

    <section class="section feature ground-paper" id="nody-bot" aria-labelledby="nb-heading">
      <div class="wrap">
        <div class="feature__panel ground-dark-2">
          <div class="feature__main">
            <p class="reading feature__kicker">Our first product</p>
            <h2 class="feature__title" id="nb-heading"><img src="assets/nody-bot-lockup-transparent.png" width="1080" height="220" alt="Nody Bot" /></h2>
            <p class="feature__lede">Battery-powered Ethernet phone-home for datacenter construction.</p>
          </div>
          <div class="feature__side">
            <p>Hang it on the far end of a cable run. It sleeps for most of the build, wakes on a schedule, and reports in so you know the drop is still alive. No PoE, and nothing left pingable.</p>
            <div class="actions">
              <a class="btn btn--primary btn--lg" href="nody-bot.html">Explore Nody Bot {ARROW}</a>
              <a class="text-link" href="nody-bot.html#specs">View specifications {ARROW}</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section ground-paper-2" id="company" aria-labelledby="about-heading">
      <div class="wrap split">
        <div class="split__copy">
          <h2 class="h2" id="about-heading">A focused hardware company for practical industrial products.</h2>
          <p class="lede">ESSIMPLEX is a hardware company focused on custom design and practical industrial products.</p>
          <p>We keep claims honest. Nody Bot is our first product, not the company.</p>
        </div>
        <dl class="facts">
          <div><dt class="reading">Company</dt><dd>ESSIMPLEX</dd></div>
          <div><dt class="reading">Focus</dt><dd>Custom design, industrial hardware</dd></div>
          <div><dt class="reading">First product</dt><dd><a href="nody-bot.html">Nody Bot</a></dd></div>
        </dl>
      </div>
    </section>

    <section class="section ground-paper" id="capabilities" aria-labelledby="cap-heading">
      <div class="wrap caps">
        <div class="caps__head">
          <h2 class="h2" id="cap-heading">What we build.</h2>
          <p class="lede muted">Custom design and hardware products for industry, made for demanding environments.</p>
        </div>
        <ul class="ruled" role="list">{rows}
        </ul>
      </div>
    </section>

    <section class="section ground-dark-2" id="approach" aria-labelledby="approach-heading">
      <div class="wrap">
        <div class="section-head section-head--split">
          <h2 class="h2" id="approach-heading">From field problem to a device ready to install.</h2>
          <p class="lede muted">One short path, with nothing between the problem and the unit on site.</p>
        </div>
        <ol class="steps3" role="list">{steps}
        </ol>
      </div>
    </section>

    <section class="section section--tight ground-paper-2" id="people" aria-labelledby="people-heading">
      <div class="wrap teaser">
        <div class="teaser__copy">
          <p class="reading teaser__kicker">About</p>
          <h2 class="h2" id="people-heading">The people behind ESSIMPLEX.</h2>
          <p class="lede muted">Meet co-founders Frank Wagner and Henry Wagner.</p>
        </div>
        <div class="teaser__action">
          <a class="btn btn--ghost" href="about.html">About ESSIMPLEX {ARROW}</a>
        </div>
      </div>
    </section>

{close("Talk to us about your build.", "Interested in a custom design engagement or in Nody Bot? Write to us and we will respond by email.", MAIL).replace("__OTHER_HREF__", "nody-bot.html").replace("__OTHER_LABEL__", "Nody Bot product page")}  </main>

{FOOTER}'''
    return head(t, d) + body

def product():
    nav = [("Nody Bot", "nody-bot.html", True), ("How it works", "#how", False), ("Specifications", "#specs", False), ("About", "about.html", False)]
    t = "Nody Bot | ESSIMPLEX"
    d = "Nody Bot is battery-powered Ethernet phone-home for datacenter construction. It sleeps, wakes on a schedule, and reports in so you know the cable drop is still alive."
    why = [
        ("Not pingable by design", "Asleep between wakes. It never answers a ping, and no ports sit open waiting for scans on an unfinished plant."),
        ("Months on battery", "Battery power, not PoE, so the far end works before power distribution is ready."),
        ("Your collector", "Check-ins report to your collector. This site is marketing; collector and operations software ships separately."),
    ]
    why_rows = "".join(f'''
            <li class="ruled__row"><h3 class="h3">{a}</h3><p>{b}</p></li>''' for a, b in why)
    plate_rows = [("Product", "NBX-ETH-BAT", True)] + PLATE_ROWS
    body = f'''<body class="page-product">
{header(nav, MAIL_NB)}
  <main id="main">
    <section class="hero hero--product ground-dark" aria-labelledby="hero-heading">
      <div class="wrap hero__content">
        <div class="hero__grid">
          <div class="hero__copy">
            <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">ESSIMPLEX</a><span aria-hidden="true">/</span><span aria-current="page">Nody Bot</span></nav>
            <h1 class="display" id="hero-heading">Nody Bot</h1>
            <p class="hero__motto">Not dead yet.</p>
            <p class="hero__descriptor">Battery Ethernet phone-home for datacenter construction</p>
            <p class="hero__lede">Hang it on the far end of a cable run. It sleeps for most of the build, wakes on a schedule, and reports in so you know the drop is still alive. No PoE, and nothing left pingable.</p>
            <div class="actions">
              <a class="btn btn--primary" href="{MAIL_NB}">Contact sales {ARROW}</a>
              <a class="btn btn--ghost" href="#specs">View specifications</a>
            </div>
          </div>
          {plate(True, plate_rows, uid="glance-heading", title="At a glance")}
        </div>
      </div>
      {hero_trace("product")}
    </section>

    <section class="section ground-dark-2" id="how" aria-labelledby="how-heading">
      <div class="wrap">
        <div class="section-head section-head--split">
          <h2 class="h2" id="how-heading">Sleep. Wake. Prove it. Sleep.</h2>
          <p class="lede muted">Built for multi-month cable plant builds, not always-on monitoring. One cycle, repeated for the life of the build.</p>
        </div>
        {seq_diagram(SEQ_LONG, False)}
      </div>
    </section>

    <section class="section ground-paper" id="why" aria-labelledby="why-heading">
      <div class="wrap caps">
        <div class="caps__head">
          <h2 class="h2" id="why-heading">Proof it&rsquo;s alive when the plant isn&rsquo;t finished.</h2>
          <p class="lede muted">During AI and HPC hall construction, cable drops sit unfinished for months. You need to know they still work, without leaving something pingable on an incomplete network and without PoE at the far end.</p>
        </div>
        <div>
          <ul class="ruled" role="list">{why_rows}
          </ul>
          <div class="audience">
            <h3 class="h3">Who it&rsquo;s for</h3>
            <ul role="list">
              <li>Datacenter construction and cable verification crews</li>
              <li>Commissioning teams that need live confirmation across hundreds of drops</li>
              <li>Integrators building AI and HPC halls on multi-month plant schedules</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="section ground-paper-2" id="specs" aria-labelledby="specs-heading">
      <div class="wrap specs">
        <div class="specs__meta">
          <h2 class="h2" id="specs-heading">Datasheet</h2>
          <p>Preliminary product parameters for planning and RFQ. Specifications may change before commercial availability.</p>
          <dl class="specs__facts">
            <div><dt class="reading">SKU</dt><dd class="reading">NBX-ETH-BAT</dd></div>
            <div><dt class="reading">Status</dt><dd>Preliminary</dd></div>
            <div><dt class="reading">Category</dt><dd>Network infrastructure hardware</dd></div>
          </dl>
          <div class="actions"><a class="btn" href="{MAIL_DS}">Request datasheet {ARROW}</a></div>
        </div>
        <div class="specs__tables">
          <div class="spec-group">
            <h3 class="h3" id="spec-hw">Product</h3>
            <table class="spec" aria-labelledby="spec-hw"><tbody>
              <tr><th scope="row">Product / SKU</th><td>Nody Bot, NBX-ETH-BAT</td></tr>
              <tr><th scope="row">Connection</th><td>Wired Ethernet (no Wi-Fi dependency in the plant)</td></tr>
              <tr><th scope="row">Power</th><td>Battery (not PoE)</td></tr>
              <tr><th scope="row">Setup</th><td>Configured over USB (no mobile apps)</td></tr>
            </tbody></table>
          </div>
          <div class="spec-group">
            <h3 class="h3" id="spec-net">Behaviour</h3>
            <table class="spec" aria-labelledby="spec-net"><tbody>
              <tr><th scope="row">Wake interval</th><td>~15 minutes (configurable)</td></tr>
              <tr><th scope="row">Reachability</th><td>Outbound check-in only; not pingable</td></tr>
              <tr><th scope="row">Deployment</th><td>Far end of cable runs during datacenter construction</td></tr>
              <tr><th scope="row">Operating intent</th><td>Multi-month build schedules; sleeps between check-ins</td></tr>
            </tbody></table>
          </div>
          <p class="muted" style="margin-top:var(--s-6)">Preliminary specifications. Subject to change before commercial availability.</p>
        </div>
      </div>
    </section>

    <section class="section ground-paper" id="provisioning" aria-labelledby="prov-heading">
      <div class="wrap">
        <div class="section-head section-head--split">
          <h2 class="h2" id="prov-heading">Configured over USB.</h2>
          <p class="lede muted">Units are set up on the bench before they reach the plant. The product surface is this website and the hardware device.</p>
        </div>
        <ol class="prov" role="list">
          <li class="prov__item"><span class="reading" aria-hidden="true">1</span><div><h3 class="h3">Bench</h3><p>Set the collector address, unit identity and wake interval.</p></div></li>
          <li class="prov__item"><span class="reading" aria-hidden="true">2</span><div><h3 class="h3">Verify</h3><p>Verify the battery and Ethernet connection on the bench.</p></div></li>
          <li class="prov__item"><span class="reading" aria-hidden="true">3</span><div><h3 class="h3">Ship</h3><p>Ship configured modules to the far-end install crew.</p></div></li>
        </ol>
        <div class="prov-ships ground-paper-2">
          <p class="reading">What ships</p>
          <p>The Nody Bot unit and its USB setup path. The collector backend is separate.</p>
        </div>
      </div>
    </section>

{close("Ready for a build or pilot?", "Ask about Nody Bot availability, datasheets, or a custom design engagement from ESSIMPLEX.", MAIL_NB).replace("__OTHER_HREF__", "index.html").replace("__OTHER_LABEL__", "ESSIMPLEX home")}  </main>

{FOOTER}'''
    return head(t, d, "https://essimplex.com/nody-bot.html") + body

def legal(title, meta, intro, sections):
    nav = [("Nody Bot", "nody-bot.html", False), ("Capabilities", "index.html#capabilities", False), ("About", "about.html", False)]
    secs = "".join(f"\n        <h2>{h}</h2>\n        <p>{p}</p>" for h, p in sections)
    body = f'''<body class="page-legal">
{header(nav, MAIL)}
  <main id="main">
    <section class="page-head ground-dark" aria-labelledby="page-heading">
      <div class="wrap">
        <h1 class="display" id="page-heading">{title}</h1>
        <p class="page-head__meta reading">{meta}</p>
      </div>
    </section>
    <div class="legal ground-paper">
      <div class="wrap">
      <article class="legal__body">
        <p>{intro}</p>{secs}
        <p><a class="text-link" href="index.html">Back to ESSIMPLEX home {ARROW}</a></p>
      </article>
      </div>
    </div>
  </main>

{FOOTER}'''
    return head(f"{title} | ESSIMPLEX", f"{title} for ESSIMPLEX. Placeholder until the full document is published.") + body


# ---------- About ----------
PEOPLE = [
    ("Frank Wagner", "Co-founder", "frank-wagner"),
    ("Henry Wagner", "Co-founder", "henry-wagner"),
]
# Empty-state mark for a missing portrait: a plain head-and-shoulders outline, thin copper line.
PORTRAIT_MARK = ('<svg viewBox="0 0 80 100" aria-hidden="true" focusable="false">'
                 '<circle cx="40" cy="38" r="13"/><path d="M14 90 C14 66 26 58 40 58 C54 58 66 66 66 90"/></svg>')

def person(name, title, slug):
    # To add a photo: replace the whole <div class="person__photo person__photo--empty"> element with
    #   <img class="person__photo" src="assets/team/{slug}.jpg" width="800" height="1000" alt="{name}" />
    # To add the introduction: replace the INTRO comment with <p class="person__intro">...</p>
    return f'''        <article class="person" aria-labelledby="{slug}-name">
          <div class="person__photo person__photo--empty" role="img" aria-label="Photo of {name} &mdash; coming soon">{PORTRAIT_MARK}</div>
          <h2 class="person__name" id="{slug}-name">{name}</h2>
          <p class="person__title reading">{title}</p>
          <!-- INTRO: paste introduction here (replace this comment with <p class="person__intro">...</p>) -->
        </article>
'''

def about():
    nav = [("Nody Bot", "nody-bot.html", False), ("Capabilities", "index.html#capabilities", False), ("About", "about.html", True)]
    people = "".join(person(*p) for p in PEOPLE)
    body = f'''<body class="page-about">
{header(nav, MAIL)}
  <main id="main">
    <section class="page-head ground-dark" aria-labelledby="page-heading">
      <div class="wrap">
        <h1 class="display" id="page-heading">About ESSIMPLEX</h1>
      </div>
    </section>
    <section class="about ground-paper" aria-label="Co-founders">
      <div class="wrap">
        <div class="people">
{people}        </div>
      </div>
    </section>
  </main>

{FOOTER}'''
    return head("About | ESSIMPLEX", "About ESSIMPLEX and its co-founders, Frank Wagner and Henry Wagner.", "https://essimplex.com/about.html") + body

pages = {
    "index.html": index(),
    "nody-bot.html": product(),
    "privacy.html": legal("Privacy Policy", "Last updated September 14, 2026 &middot; Placeholder",
        "This page is a placeholder for the ESSIMPLEX privacy policy. When products such as Nody Bot ship commercially, this document will describe what information we collect, how it is used, and your choices.",
        [("Marketing site", "This static marketing site does not operate a backend that collects personal data from forms. Contact requests use standard email links."),
         ("Contact", 'For privacy questions, use the contact options on the <a href="index.html#contact">main site</a>. This policy will be replaced with a complete legal document before consumer or enterprise data processing begins.')]),
    "about.html": about(),
    "terms.html": legal("Terms of Use", "Last updated September 14, 2026 &middot; Placeholder",
        "These terms are a placeholder for ESSIMPLEX website and product terms of use, including the Nody Bot product. A complete agreement will be published before commercial availability.",
        [("Website", "Content on this marketing site is provided for informational purposes and does not constitute a product warranty, offer, or service-level commitment. Product specifications may change."),
         ("Contact", 'Questions about these terms can be directed via the <a href="index.html#contact">contact section</a> on the main site.')]),
}
for name, html in pages.items():
    with open(os.path.join(ROOT, name), "w") as f:
        f.write(html)
    print("wrote", name, len(html))

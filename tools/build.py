#!/usr/bin/env python3
"""Generates the static HTML pages. Run from the repo root: python3 tools/build.py
Output is plain, committed HTML; this script only avoids repeating the header, footer and trace SVGs."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIL = "mailto:support@essimplex.com?subject=ESSIMPLEX%20inquiry"
MAIL_NB = "mailto:support@essimplex.com?subject=Nody%20Bot%20inquiry"
MAIL_DS = "mailto:support@essimplex.com?subject=Nody%20Bot%20datasheet%20request"
ARROW = '<svg class="ico-arrow" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M2 8h11M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ---------- trace geometry ----------
def path(points, W, H):
    return "M" + " L".join(f"{x*W:.1f},{y*H:.1f}" for x, y in points)

def pulse(x0, base, pw, W, H, top=0.10, low=0.98):
    """One heartbeat-style pulse starting at fraction x0, pw is the width in viewBox units."""
    u = pw / W
    pts = [(x0, base), (x0 + .09*u, base - .14), (x0 + .18*u, base), (x0 + .30*u, base), (x0 + .38*u, base + .14),
           (x0 + .46*u, top), (x0 + .56*u, low), (x0 + .64*u, base), (x0 + .80*u, base - .20), (x0 + .96*u, base), (x0 + u, base)]
    return pts

def hero_path(W, H, starts, pw):
    base = 0.78
    pts = [(0, base)]
    for s in starts:
        pts += pulse(s, base, pw, W, H)
    pts.append((1, base))
    return path(pts, W, H)

SEQ_PTS = [(0,.82),(.055,.82),(.10,.62),(.19,.62),(.23,.56),(.30,.46),(.38,.46),(.44,.44),(.47,.30),(.50,.08),(.53,.70),
           (.56,.46),(.62,.46),(.66,.46),(.70,.30),(.74,.52),(.80,.58),(.86,.82),(1,.82)]
NODES = [(.10,.62),(.30,.46),(.50,.08),(.70,.30),(.90,.82)]

def trace_svgs(d_narrow, wn, hn, d_wide, ww, hw):
    return (f'<svg class="t-narrow" viewBox="0 0 {wn} {hn}" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path class="t-track" d="{d_narrow}"/><path class="t-line" d="{d_narrow}"/></svg>'
            f'<svg class="t-wide" viewBox="0 0 {ww} {hw}" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path class="t-track" d="{d_wide}"/><path class="t-line" d="{d_wide}"/></svg>')

def hero_trace(label_right):
    d_n = hero_path(400, 120, [0.22, 0.62], 112)
    d_w = hero_path(1200, 340, [0.55, 0.78], 170)
    return f'''<div class="trace hero-trace" role="img" aria-label="Sample check-in trace: a flat line while the unit sleeps, with a short pulse each time it checks in.">
        {trace_svgs(d_n, 400, 120, d_w, 1200, 340)}
      </div>
      <div class="wrap">
        <p class="hero-trace__legend reading" aria-hidden="true"><span>Sample trace</span><span>{label_right}</span></p>
      </div>'''

def seq_diagram(steps, compact):
    d_n = path(SEQ_PTS, 360, 112)
    d_w = path(SEQ_PTS, 1000, 240)
    markers = "".join(
        f'<span class="seq__marker" data-at="{x:.2f}" style="--x:{x*100:.0f}%;--yn:{y}" aria-hidden="true">{i+1}</span>'
        for i, (x, y) in enumerate(NODES))
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
          <div class="seq__plot trace" data-trace role="img" aria-label="Check-in sequence as a trace over time: flat while asleep, rising through wake and connect, peaking at report, a smaller pulse at confirm, then flat again at sleep.">
            {trace_svgs(d_n, 360, 112, d_w, 1000, 240)}
            {markers}
          </div>
          <p class="seq__axis reading" aria-hidden="true"><span>T+0</span><span>next wake in ~15 min</span></p>
        </div>
        <ol class="seq__steps" role="list">{items}
        </ol>
      </div>'''

# ---------- shared chrome ----------
def head(title, desc, extra=""):
    return f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
  <meta name="robots" content="noindex, nofollow">
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="https://essimplex.com/" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="ESSIMPLEX" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="https://essimplex.com/" />
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
              <li><a href="index.html#company">About</a></li>
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
        <a class="text-link" href="#main">Back to top <svg class="ico-arrow" viewBox="0 0 16 16" aria-hidden="true" focusable="false" style="rotate:-90deg"><path d="M2 8h11M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
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
    nav = [("Nody Bot", "nody-bot.html", False), ("Capabilities", "#capabilities", False), ("How it works", "#how", False), ("Company", "#company", False)]
    t = "ESSIMPLEX | Custom design and hardware products for industry"
    d = "ESSIMPLEX designs and builds practical hardware for demanding environments. Our first product is Nody Bot, battery-powered Ethernet phone-home for datacenter construction."
    caps = [
        ("Custom design", "Hardware engineered around a specific field problem, from requirements to a working device."),
        ("Industrial products", "Practical devices built for demanding environments, starting with datacenter construction."),
        ("Field-ready deployment", "Units are configured on the bench and shipped ready for the install crew."),
        ("Honest specifications", "We publish what the device does. Preliminary parameters are labeled as preliminary."),
    ]
    rows = "".join(f'''
            <li class="ruled__row"><h3 class="h3">{a}</h3><p>{b}</p></li>''' for a, b in caps)
    body = f'''<body class="page-home">
{header(nav, MAIL)}
  <main id="main">
    <section class="hero hero--home ground-dark" aria-labelledby="hero-heading">
      <div class="wrap hero__content">
        <div class="hero__copy">
          <h1 class="display" id="hero-heading">Practical hardware for demanding environments.</h1>
          <p class="hero__descriptor">Custom design and hardware products for industry. Our first product is Nody Bot, battery-powered Ethernet phone-home for datacenter construction.</p>
          <div class="actions">
            <a class="btn btn--primary" href="nody-bot.html">Explore Nody Bot {ARROW}</a>
            <a class="btn btn--ghost" href="{MAIL}">Talk to us</a>
          </div>
        </div>
      </div>
      {hero_trace("every ~15 min")}
    </section>

    <section class="section ground-paper" id="nody-bot" aria-labelledby="nb-heading">
      <div class="wrap split">
        <div class="split__copy">
          <h2 class="h2" id="nb-heading">Nody Bot</h2>
          <p class="lede">Battery-powered Ethernet phone-home for datacenter construction.</p>
          <p>Hang it on the far end of a cable run. It sleeps for most of the build, wakes on a schedule, and reports in so you know the drop is still alive. No PoE, and nothing left pingable.</p>
          <div class="actions">
            <a class="text-link" href="nody-bot.html">Read about Nody Bot {ARROW}</a>
            <a class="text-link" href="nody-bot.html#specs">View specifications {ARROW}</a>
          </div>
        </div>
        {plate(False, PLATE_ROWS, uid="home-plate")}
      </div>
    </section>

    <section class="section ground-dark-2" id="how" aria-labelledby="how-heading">
      <div class="wrap">
        <div class="section-head section-head--split">
          <h2 class="h2" id="how-heading">One check-in cycle, repeated for the life of the build.</h2>
          <div class="split__copy">
            <p class="lede muted">Built for multi-month cable plant builds, not always-on monitoring.</p>
            <a class="text-link" href="nody-bot.html#how">See the full sequence {ARROW}</a>
          </div>
        </div>
        {seq_diagram(SEQ_SHORT, True)}
      </div>
    </section>

    <section class="section ground-paper" id="capabilities" aria-labelledby="cap-heading">
      <div class="wrap caps">
        <div class="caps__head">
          <h2 class="h2" id="cap-heading">From field problem to a device ready to install.</h2>
          <p class="lede muted">ESSIMPLEX is a hardware company focused on custom design and practical industrial products. We take a field problem, design the device that solves it, and ship it ready to install.</p>
        </div>
        <ul class="ruled" role="list">{rows}
        </ul>
      </div>
    </section>

    <section class="section ground-paper-2" id="company" aria-labelledby="about-heading">
      <div class="wrap split">
        <div class="split__copy">
          <h2 class="h2" id="about-heading">A focused hardware company for practical industrial products.</h2>
          <p class="lede">Nody Bot is our first product, built for datacenter construction teams.</p>
          <p>We keep claims honest. This site describes the product surface: the website and the device. Collector and operations software ships separately. Nody Bot is a product name, not the company.</p>
        </div>
        <dl class="facts">
          <div><dt class="reading">Company</dt><dd>ESSIMPLEX</dd></div>
          <div><dt class="reading">First product</dt><dd><a href="nody-bot.html">Nody Bot</a></dd></div>
          <div><dt class="reading">Focus</dt><dd>Custom design, industrial hardware</dd></div>
        </dl>
      </div>
    </section>

{close("Talk to us about your build.", "Interested in Nody Bot for a build, a pilot, or a custom design engagement? Write to us and we will respond by email.", MAIL).replace("__OTHER_HREF__", "nody-bot.html").replace("__OTHER_LABEL__", "Nody Bot product page")}  </main>

{FOOTER}'''
    return head(t, d) + body

def product():
    nav = [("Nody Bot", "nody-bot.html", True), ("How it works", "#how", False), ("Specifications", "#specs", False), ("Company", "index.html#company", False)]
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
      {hero_trace("every ~15 min")}
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
    return head(t, d) + body

def legal(title, meta, intro, sections):
    nav = [("Nody Bot", "nody-bot.html", False), ("Capabilities", "index.html#capabilities", False), ("Company", "index.html#company", False)]
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

pages = {
    "index.html": index(),
    "nody-bot.html": product(),
    "privacy.html": legal("Privacy Policy", "Last updated September 14, 2026 &middot; Placeholder",
        "This page is a placeholder for the ESSIMPLEX privacy policy. When products such as Nody Bot ship commercially, this document will describe what information we collect, how it is used, and your choices.",
        [("Marketing site", "This static marketing site does not operate a backend that collects personal data from forms. Contact requests use standard email links."),
         ("Contact", 'For privacy questions, use the contact options on the <a href="index.html#contact">main site</a>. This policy will be replaced with a complete legal document before consumer or enterprise data processing begins.')]),
    "terms.html": legal("Terms of Use", "Last updated September 14, 2026 &middot; Placeholder",
        "These terms are a placeholder for ESSIMPLEX website and product terms of use, including the Nody Bot product. A complete agreement will be published before commercial availability.",
        [("Website", "Content on this marketing site is provided for informational purposes and does not constitute a product warranty, offer, or service-level commitment. Product specifications may change."),
         ("Contact", 'Questions about these terms can be directed via the <a href="index.html#contact">contact section</a> on the main site.')]),
}
for name, html in pages.items():
    with open(os.path.join(ROOT, name), "w") as f:
        f.write(html)
    print("wrote", name, len(html))

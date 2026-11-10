#!/usr/bin/env python3
"""Builds equitygroupjax.com into docs/ (served by GitHub Pages).

Run:  python3 build.py
Deals live in content/deals.json. Add or edit a deal there and rebuild;
the Buyer Blasts automation can do the same thing on "send".
"""
import html, json, os, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "docs")

SITE = "https://equitygroupjax.com"
# While the site is previewed at equitygroup904-dev.github.io/equitygroupjax-site/ every link
# needs this prefix. At the DNS switch set BASE = "" and LIVE = True (adds CNAME, allows indexing).
BASE = ""
LIVE = True

BRAND = "American Equity Group"
PHONE = "(904) 685-8024"
TEL = "+19046858024"

# GHL "Cash Buyer Sign-Up" form, GHL sub-account RUJDZc7TyNghXiWDMthZ ONLY.
# Paste the form ID here once the form is built in GHL. Until then the page shows a call/text fallback.
BUYER_FORM_ID = "K0FD3RRCNOUlr2DS7V7S"

B = lambda p: BASE + p  # site-relative link

BUSINESS_SCHEMA = {
    "@context": "https://schema.org", "@type": "LocalBusiness", "@id": SITE + "/#business",
    "name": BRAND, "legalName": "American Equity Group LLC",
    "url": SITE + "/", "telephone": TEL, "logo": SITE + "/img/american-equity-group-logo.webp", "image": SITE + "/img/jax-skyline-hero.webp",
    "description": "Off-market investment properties, rentals, fix-and-flips and land in Jacksonville and North Florida for cash buyers.",
    "address": {"@type": "PostalAddress", "addressLocality": "Jacksonville", "addressRegion": "FL", "addressCountry": "US"},
    "areaServed": [{"@type": "AdministrativeArea", "name": c + " County, FL"} for c in
                   ["Duval", "Nassau", "Clay", "St. Johns", "Baker", "Putnam", "Flagler"]],
    "founder": {"@type": "Person", "name": "James Stallworth"},
    "foundingDate": "2016",
    "sameAs": ["https://www.linkedin.com/company/american-equity-group-llc/"],
}

CSS = """
:root{--navy:#0f2a47;--navy-2:#173d66;--green:#1f8a4c;--green-d:#176d3b;--mint:#7fd6a1;--ink:#1d2733;--mute:#5b6775;--line:#e3e8ee;--bg:#f6f8fa;--gold:#c99a2e}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);line-height:1.6;background:#fff}
img{max-width:100%;height:auto}a{color:var(--green-d)}.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
.top{background:var(--navy);color:#fff;position:sticky;top:0;z-index:40}.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px}
.logo{color:#fff;text-decoration:none;font-weight:800;font-size:19px;letter-spacing:.2px;line-height:1.1;display:flex;align-items:center;gap:10px}
.logo img{height:48px;width:auto;background:#fff;border-radius:10px;padding:3px 4px}
.logo small{display:block;font-weight:600;font-size:11px;letter-spacing:1.6px;text-transform:uppercase;color:var(--mint)}
.nav{display:flex;gap:20px}.nav a{color:#dbe6f2;text-decoration:none;font-size:15px}.nav a:hover,.nav a[aria-current]{color:#fff}
.btn{display:inline-block;background:var(--green);color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:9px;white-space:nowrap;border:0}
.btn:hover{background:var(--green-d)}.btn.ghost{background:transparent;border:2px solid rgba(255,255,255,.55)}.btn.ghost:hover{background:rgba(255,255,255,.08)}
.btn.light{background:#fff;color:var(--green-d)}.btn.sm{padding:9px 14px;font-size:15px}
.hero{background:linear-gradient(135deg,rgba(15,42,71,.92) 0%,rgba(23,61,102,.80) 100%),url(IMGBASE/img/jax-skyline-hero.webp) center 60%/cover no-repeat var(--navy);color:#fff;padding:64px 0 56px}
.hero.plain{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-2) 100%);padding:44px 0 40px}
.hero h1{font-size:44px;line-height:1.12;margin:0 0 14px;max-width:780px}.hero p.lead{font-size:19px;color:#dbe6f2;margin:0 0 24px;max-width:680px}
.hero .ctas{display:flex;gap:12px;flex-wrap:wrap}.eyebrow{color:var(--mint);font-weight:800;font-size:13px;letter-spacing:1.6px;text-transform:uppercase;margin:0 0 10px}
section{padding:56px 0}section.alt{background:var(--bg)}h2{font-size:30px;line-height:1.2;margin:0 0 12px}h3{font-size:20px;margin:0 0 8px}
.intro{color:var(--mute);font-size:18px;max-width:700px;margin:0 0 28px}.sec-eyebrow{color:var(--green);font-weight:800;font-size:13px;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px}
.stats{background:var(--navy);color:#fff;padding:24px 0}.stats .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;text-align:center}
.stats b{display:block;font-size:30px;line-height:1.1;color:var(--mint)}.stats span{font-size:14px;color:#dbe6f2}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.box{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px}.box p{margin:0;color:var(--mute)}
.ic{display:inline-flex;width:46px;height:46px;border-radius:11px;background:#e8f5ed;color:var(--green-d);align-items:center;justify-content:center;margin-bottom:12px}
.deals{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.deal{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--ink);box-shadow:0 4px 16px rgba(15,42,71,.06);transition:transform .15s,box-shadow .15s}
.deal:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(15,42,71,.12)}
.deal .ph{position:relative;aspect-ratio:3/2;background:linear-gradient(135deg,#e8eef4,#d5e0eb);display:flex;align-items:center;justify-content:center;color:var(--navy-2)}
.deal .ph img{width:100%;height:100%;object-fit:cover}.deal .ph svg{opacity:.55}
.badge{position:absolute;top:12px;left:12px;font-size:12px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;padding:5px 10px;border-radius:999px;background:var(--green);color:#fff}
.badge.under-offer{background:var(--gold)}.badge.sold{background:#8a94a1}
.deal .bd{padding:16px 18px 18px;display:flex;flex-direction:column;gap:4px;flex:1}
.deal .price{font-size:24px;font-weight:800;color:var(--navy)}.deal .meta{font-size:14px;color:var(--mute)}.deal .ln{font-weight:700}
.deal .go{margin-top:auto;padding-top:10px;font-weight:700;color:var(--green-d);font-size:15px}
.empty{background:var(--bg);border:1px dashed var(--line);border-radius:14px;padding:28px;text-align:center;color:var(--mute)}
.steps{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(4,1fr);gap:18px;counter-reset:s}
.steps li{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px;counter-increment:s}
.steps li:before{content:counter(s,decimal-leading-zero);display:block;font-size:34px;font-weight:800;color:var(--line);line-height:1;margin-bottom:10px}
.steps p{margin:0;color:var(--mute);font-size:15px}
.paths{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.path{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px;border-top:4px solid var(--green)}
.path p{color:var(--mute);margin:0 0 12px}.path a{font-weight:700;text-decoration:none}
.meet{display:grid;grid-template-columns:220px 1fr;gap:34px;align-items:center}.meet img{width:220px;height:220px;object-fit:cover;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.15)}
.cta{background:var(--green);color:#fff;text-align:center;padding:48px 0}.cta h2{color:#fff}.cta p{color:#e3f4ea;margin:0 0 18px}.cta .btn{margin:6px}
.formcard{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(15,42,71,.08)}
.formslot{min-height:200px}.fallback{background:var(--bg);border-radius:12px;padding:20px}.fallback p{margin:0 0 10px}
.checks{list-style:none;padding:0;margin:0 0 16px}.checks li{padding-left:28px;position:relative;margin:7px 0}
.checks li:before{content:"\\2713";position:absolute;left:0;color:var(--green);font-weight:800}
.hero .checks li:before{color:var(--mint)}
table.facts{width:100%;border-collapse:collapse}table.facts th,table.facts td{padding:11px 0;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.facts th{color:var(--mute);font-weight:600;width:42%;padding-right:12px}
.dealhead{display:grid;grid-template-columns:1.2fr .8fr;gap:30px;align-items:start}
.gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.gallery img{border-radius:12px;aspect-ratio:3/2;object-fit:cover;width:100%}.gallery.one{grid-template-columns:1fr}.caption{font-size:14px;color:var(--mute);margin:8px 2px 0}.gallery.one img{aspect-ratio:auto;object-fit:contain;background:#eef2f6}.gallery.one{gap:14px}
.noimg{aspect-ratio:3/2;border-radius:14px;background:linear-gradient(135deg,#e8eef4,#d5e0eb);display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--navy-2);gap:8px;font-weight:600}
.pricebox{background:var(--navy);color:#fff;border-radius:16px;padding:24px;position:sticky;top:90px}.pricebox .price{font-size:36px;font-weight:800;line-height:1.1}
.pricebox p{color:#dbe6f2;margin:6px 0 16px}.pricebox .btn{display:block;text-align:center;margin-top:10px}
.note{font-size:14px;color:var(--mute);background:#fff8e6;border:1px solid #f1dfae;border-radius:10px;padding:12px 14px}
details{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:10px 0}summary{font-weight:700;cursor:pointer}details p{margin:10px 0 0;color:var(--mute)}
.crumbs{font-size:14px;color:#b9c6d4;margin:0 0 10px}.crumbs a{color:#dbe6f2}
footer{background:#0b1f35;color:#b9c6d4;padding:40px 0 30px;font-size:15px}footer a{color:#dbe6f2}footer .cols{display:grid;grid-template-columns:2fr 1fr 1fr;gap:24px}
footer b{color:#fff}.verify .disclaimer,.verify .legal-links{margin:0 0 10px}.verify a{color:#cfe0f0}.verify{border-top:1px solid #1e3550;margin-top:24px;padding-top:16px;font-size:13px;color:#9fb0c2}
.stickycall{display:none}
@media(max-width:900px){.deals,.grid3,.paths{grid-template-columns:1fr 1fr}.steps{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.nav{display:none}.hero{padding:44px 0 40px}.hero h1{font-size:32px}h2{font-size:25px}
 .deals,.grid3,.grid2,.paths,.steps,footer .cols,.dealhead,.meet{grid-template-columns:1fr}.stats .wrap{grid-template-columns:1fr 1fr}
 .meet img{width:160px;height:160px}.top .btn{display:none}.pricebox{position:static}
 .stickycall{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:50}.stickycall a{flex:1;text-align:center;font-weight:800;padding:14px;text-decoration:none;color:#fff;background:var(--green)}
 .stickycall a+a{background:var(--navy)}body{padding-bottom:52px}}
"""

NAV = [("/current-deals/", "Current Deals"), ("/how-we-work/", "How We Work"),
       ("/join-buyers-list/", "Join the Buyers List"), ("/contact/", "Contact")]

LAND_SVG = ('<svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 20h18"/><path d="M5 20V9l7-5 7 5v11"/>'
            '<path d="M9 20v-6h6v6"/></svg>')
ICONS = {
    "deal": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "map": '<path d="M9 4l-6 2v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
}


def icon(k):
    return (f'<span class="ic"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[k]}</svg></span>')


def esc(s):
    return html.escape(str(s), quote=True)


def money(n):
    return f"${n:,.0f}" if n is not None else ""


VERIFY = ("Buyer to verify all information before closing, including price, size, zoning, buildability, utilities, "
          "repairs, rents and title. All numbers are estimates. American Equity Group LLC is a real estate investment "
          "company, not a real estate brokerage, and holds equitable interest in the properties it markets.")


def shell(slug, title, desc, body, schema=None, active=None):
    url = SITE + slug
    robots = "index,follow" if LIVE and slug != "/404.html" else "noindex,nofollow"
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s)}</script>' for s in [BUSINESS_SCHEMA] + (schema or []))
    nav = "".join(f'<a href="{B(u)}"{" aria-current=page" if u == active else ""}>{t}</a>' for u, t in NAV)
    css = CSS.replace("IMGBASE", BASE)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{SITE}/img/jax-skyline-hero.webp">
<link rel="icon" href="{B('/favicon.svg')}" type="image/svg+xml">
{ld}
<style>{css}</style></head><body>
<header class="top"><div class="wrap"><a class="logo" href="{B('/')}"><img src="{B('/img/american-equity-group-logo.webp')}" alt="American Equity Group logo" width="47" height="48"><span>{BRAND}<small>Jacksonville Off-Market Deals</small></span></a>
<nav class="nav" aria-label="Main">{nav}</nav><a class="btn sm" href="tel:{TEL}">{PHONE}</a></div></header>
<main>
{body}
</main>
<footer><div class="wrap cols"><div><b>{BRAND} LLC</b><br>Off-market rentals, flips and land in Jacksonville and North Florida.<br>
Call or text <a href="tel:{TEL}">{PHONE}</a><p>Veteran-owned and based in Jacksonville.</p></div>
<div><b>Buyers</b><br><a href="{B('/current-deals/')}">Current deals</a><br><a href="{B('/join-buyers-list/')}">Join the buyers list</a><br><a href="{B('/how-we-work/')}">How we work</a></div>
<div><b>Company</b><br><a href="{B('/contact/')}">Contact</a><br><a href="{B('/privacy-policy/')}">Privacy policy</a><br><a href="{B('/terms/')}">Terms of Use</a><br><a href="https://www.hud.gov/program_offices/fair_housing_equal_opp" target="_blank" rel="noopener">Equal Housing Opportunity</a></div></div>
<div class="wrap verify"><p class="disclaimer">American Equity Group is not a licensed real estate broker. For properties marketed under contract, we are selling our contractual or equitable interest in the property, not the property itself, and we may assign that interest for a fee. All information is believed accurate but not guaranteed. Buyers should do their own due diligence. Equal Housing Opportunity.</p><p class="legal-links"><a href="{B('/privacy-policy/')}">Privacy Policy</a> | <a href="{B('/terms/')}">Terms of Use</a> | <a href="https://www.hud.gov/program_offices/fair_housing_equal_opp" target="_blank" rel="noopener" title="Equal Housing Opportunity"><svg viewBox="0 0 40 40" width="28" height="28" aria-hidden="true" style="vertical-align:middle;margin-right:6px"><path d="M20 3 2 15v4h4v18h28V19h4v-4z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><rect x="12" y="20" width="16" height="3.5" fill="currentColor"/><rect x="12" y="27" width="16" height="3.5" fill="currentColor"/></svg>Equal Housing Opportunity</a></p><b>Buyer to verify.</b> {VERIFY}<br>© {datetime.date.today().year} American Equity Group LLC.</div></footer>
<div class="stickycall"><a href="tel:{TEL}">Call {PHONE}</a><a href="sms:{TEL}">Text us</a></div>
</body></html>"""


PAGES = {}


def page(slug, title, desc, body, schema=None):
    assert len(title) <= 65, (slug, title, len(title))
    assert 50 <= len(desc) <= 160, (slug, len(desc))
    assert body.count("<h1") == 1, (slug, "needs exactly one H1")
    PAGES[slug] = shell(slug, title, desc, body, schema, active=slug)


# ---------- deals ----------
DEALS = json.load(open(os.path.join(ROOT, "content", "deals.json")))
FORBIDDEN = {"seller", "seller_name", "seller_phone", "contract_price", "mortgage", "emd", "owner"}
for d in DEALS:
    bad = FORBIDDEN & {k.lower() for k in d}
    assert not bad, f"deal {d['slug']} carries private fields {bad}; never publish them"
    assert "emd" not in d.get("terms", "").lower(), f"deal {d['slug']}: no EMD in terms"
    assert d["status"] in ("Available", "Under Offer", "Sold"), d["status"]


def deal_url(d):
    return f"/deals/{d['slug']}/"


def area(d):
    return d["city"] + (f", FL {d['zip']}" if d.get("zip") else ", FL")


def deal_card(d):
    cls = d["status"].lower().replace(" ", "-")
    ph = (f'<img src="{B(d["photos"][0]["src"])}" alt="{esc(d["photos"][0]["alt"])}" loading="lazy" width="600" height="400">'
          if d.get("photos") else LAND_SVG)
    if d["type"] == "Land":
        sub = d.get("lot_size")
    else:
        bb = d.get("beds_baths", "").replace(" ", "").split("/")
        sub = d.get("card_sub") or " · ".join(x for x in [f"{bb[0]} bd / {bb[1]} ba" if len(bb) == 2 else "", f"{d['sqft']} sq ft" if d.get("sqft") else ""] if x)
    nums = ""
    if d.get("est_rent"):
        nums = f'<span class="meta">Est. rent {money(d["est_rent"])}/mo · Est. ARV {money(d.get("est_arv"))}</span>'
    return f"""<a class="deal" href="{B(deal_url(d))}"><div class="ph">{ph}<span class="badge {cls}">{esc(d['status'])}</span></div>
<div class="bd"><span class="price">{money(d['price'])}</span><span class="ln">{esc(d['type'])} · {esc(d['address'])}</span>
<span class="meta">{esc(area(d))} · {esc(d['county'])} County</span><span class="meta">{esc(sub)}</span>{nums}<span class="go">View deal →</span></div></a>"""


def deal_grid(deals, empty="No deals listed right now. Join the buyers list and you'll hear about the next one first."):
    if not deals:
        return f'<div class="empty">{empty}</div>'
    return '<div class="deals">' + "".join(deal_card(d) for d in deals) + "</div>"


available = [d for d in DEALS if d["status"] != "Sold"]
available.sort(key=lambda d: d.get("listed", ""), reverse=True)
available.sort(key=lambda d: d["status"] != "Available")
sold = [d for d in DEALS if d["status"] == "Sold"]


# ---------- shared blocks ----------
def cta(h="Get matched deals before they hit the full list.", p="Tell us what you buy. When a deal fits, you hear about it first."):
    return f"""<section class="cta"><div class="wrap"><h2>{h}</h2><p>{p}</p>
<a class="btn light" href="{B('/join-buyers-list/')}">Join the Buyers List</a><a class="btn ghost" href="tel:{TEL}">Call {PHONE}</a></div></section>"""


def form_block(area_hint=""):
    if BUYER_FORM_ID:
        f = BUYER_FORM_ID
        embed = (f'<iframe src="https://api.leadconnectorhq.com/widget/form/{f}" style="width:100%;height:1750px;border:none;border-radius:8px" '
                 f'id="inline-{f}" data-layout="{{\'id\':\'INLINE\'}}" data-trigger-type="alwaysShow" data-activation-type="alwaysActivated" '
                 f'data-deactivation-type="neverDeactivate" data-form-name="Cash Buyer Sign-Up" data-height="1750" '
                 f'data-layout-iframe-id="inline-{f}" data-form-id="{f}" title="Join the cash buyers list"></iframe>'
                 f'<script src="https://link.msgsndr.com/js/form_embed.js" defer></script>')
    else:
        embed = f"""<div class="fallback"><p><b>Text us to get on the list today.</b> Send your name, email, the areas you buy in,
your price range and what you buy (rentals, flips, land or multifamily) to <a href="sms:{TEL}"><b>{PHONE}</b></a>.</p>
<a class="btn" href="sms:{TEL}">Text {PHONE}</a> <a class="btn" style="background:var(--navy)" href="tel:{TEL}">Call</a></div>"""
    return f"""<div class="formcard" id="join"><h2 style="font-size:24px">Join the Cash Buyers List</h2>
<p style="color:var(--mute);margin:0 0 14px">Free. Takes about a minute. We only send deals that fit what you buy.</p>
<div class="formslot">{embed}</div>
<p style="font-size:13px;color:var(--mute);margin:12px 0 0">By signing up you agree to receive deal alerts by text from {PHONE} and by email.
Msg and data rates may apply. Reply STOP to opt out at any time.</p></div>"""


STEPS = [
    ("We find it", "We buy off-market houses and land straight from owners across North Florida."),
    ("You get the alert", "Matched buyers hear first by text and email, then the full list."),
    ("You lock it up", "First come, first served. Walk it, run your numbers, sign the assignment."),
    ("Close in 14 to 21 days", "Cash or hard money at a local title company."),
]


def steps():
    return '<ol class="steps">' + "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in STEPS) + "</ol>"


STATS = [("475+", "transactions since 2016"), ("7", "North Florida counties"), ("14–21", "days to close"), ("Veteran", "owned and operated")]


def stats():
    return '<section class="stats" aria-label="Track record"><div class="wrap">' + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in STATS) + "</div></section>"


# ---------- HOME ----------
page("/", "Jacksonville Off-Market Properties for Cash Buyers | AEG",
     "Off-market rentals, fix-and-flips and land in Jacksonville and North Florida. Join the cash buyers list and get matched deals first. Call (904) 685-8024.",
     f"""<section class="hero"><div class="wrap"><p class="eyebrow">For cash buyers and investors</p>
<h1>Off-Market Investment Properties in Jacksonville</h1>
<p class="lead">Rentals, fix-and-flips and land across Duval, Nassau, Clay and St. Johns, bought direct from owners and offered to our buyers before anyone else.</p>
<ul class="checks"><li>Deals sent to matched buyers first</li><li>Price, size and estimated numbers on every deal</li><li>Close in 14 to 21 days, cash or hard money</li></ul>
<div class="ctas"><a class="btn" href="{B('/join-buyers-list/')}">Join the Buyers List</a><a class="btn ghost" href="{B('/current-deals/')}">See Current Deals</a></div></div></section>
{stats()}
<section><div class="wrap"><p class="sec-eyebrow">Current deals</p><h2>Off-market deals available now</h2>
<p class="intro">New deals go up here the same day they go out to the buyers list. Buyers on the list hear first.</p>
{deal_grid(available[:6])}
<p style="margin-top:22px"><a class="btn" href="{B('/current-deals/')}">All current deals</a></p></div></section>
<section class="alt"><div class="wrap"><p class="sec-eyebrow">What we offer</p><h2>Deals for how you invest</h2>
<p class="intro">Tell us your strategy once. We match every new deal against it.</p>
<div class="paths"><div class="path"><h3>Rentals</h3><p>Turnkey and value-add single-family and small multifamily with estimated rents, so you can check the cash flow fast.</p><a href="{B('/join-buyers-list/')}">Get rental deals →</a></div>
<div class="path"><h3>Fix and flips</h3><p>Distressed houses below market with estimated ARV and repairs. Buyer verifies, then moves fast.</p><a href="{B('/join-buyers-list/')}">Get flip deals →</a></div>
<div class="path"><h3>Land</h3><p>Infill lots, beach lots and acreage for builders, developers and mobile home buyers.</p><a href="{B('/join-buyers-list/')}">Get land deals →</a></div></div></div></section>
<section><div class="wrap"><p class="sec-eyebrow">How it works</p><h2>From alert to closing</h2><p class="intro">Simple, fast, and the same every time.</p>{steps()}
<p style="margin-top:20px"><a href="{B('/how-we-work/')}">Read how we work →</a></p></div></section>
<section class="alt"><div class="wrap meet"><img src="{B('/img/james-stallworth.jpg')}" alt="James Stallworth, owner of American Equity Group, holding a SOLD sign" width="220" height="220" loading="lazy">
<div><p class="sec-eyebrow">Who you'll deal with</p><h2>Local, veteran-owned, and in the deals every day</h2>
<p>American Equity Group is owned by James Stallworth, a Navy veteran who has been buying houses across North Florida since 2016. We buy direct from owners, so the deals you see here are not on the MLS.</p>
<p>When you call {PHONE}, you reach our team, not a call center.</p></div></div></section>
{cta()}""")

# ---------- CURRENT DEALS ----------
sold_block = ""
if sold:
    sold_block = f"""<section class="alt"><div class="wrap"><h2>Recently sold</h2><p class="intro">Deals our buyers have closed.</p>{deal_grid(sold)}</div></section>"""
page("/current-deals/", "Current Off-Market Deals in Jacksonville FL | AEG",
     "Off-market houses, rentals and land for sale in Jacksonville and North Florida. Price, size and estimates on every deal. First come, first served.",
     f"""<section class="hero plain"><div class="wrap"><p class="eyebrow">Updated as deals go out</p><h1>Current Off-Market Deals</h1>
<p class="lead">Every deal here is under contract with us and offered by assignment. First come, first served. Buyers on the list get each deal before it posts.</p>
<div class="ctas"><a class="btn" href="{B('/join-buyers-list/')}">Get deals first</a></div></div></section>
<section><div class="wrap">{deal_grid(available)}
<p class="note" style="margin-top:24px">All figures are estimates. Buyer to verify everything, including size, zoning, utilities, repairs and rents, before closing.</p></div></section>
{sold_block}
{cta()}""",
     schema=[{"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
         {"@type": "ListItem", "position": i + 1, "url": SITE + deal_url(d), "name": d["title"]} for i, d in enumerate(available)]}])

# ---------- JOIN ----------
page("/join-buyers-list/", "Join Our Cash Buyers List in Jacksonville | AEG",
     "Get off-market Jacksonville deals that match what you buy: rentals, flips, land and multifamily. Free sign-up, deal alerts by text and email.",
     f"""<section class="hero plain"><div class="wrap"><p class="eyebrow">Free for investors</p><h1>Join the Cash Buyers List</h1>
<p class="lead">Tell us where you buy, your price range and your strategy. When a deal fits, you get it before the full list.</p></div></section>
<section><div class="wrap grid2" style="align-items:start"><div>
<h2>What you get</h2><ul class="checks"><li>Off-market deals in Duval, Nassau, Clay, St. Johns and nearby counties</li>
<li>Early "special alerts" when a deal matches your criteria</li><li>Price, photos, and estimated ARV, repairs and rent on each deal</li>
<li>Rentals, flips, land and small multifamily</li><li>No fees to join. Unsubscribe any time</li></ul>
<h3 style="margin-top:28px">New to investing?</h3><p>You're welcome here. Sign up, choose "first deal", and we'll send deals that suit a first purchase. Call us with questions any time. No jargon, no pressure.</p>
<h3 style="margin-top:28px">How matching works</h3><p>We match on area, price range, property type and strategy. Buyers who are ready now hear first.</p></div>
{form_block()}</div></section>""")

# ---------- HOW WE WORK ----------
FAQS = [
    ("Are these listed on the MLS?", "No. We buy direct from owners and market our contracts to our buyers, so these deals are off-market."),
    ("How does an assignment work?", "We have the property under contract. You buy our position in that contract with an assignment, and close with the owner at a title company. Your price includes our fee."),
    ("How fast do I need to close?", "Usually within 14 to 21 days. Cash and hard money both work. Ask about the timeline on each deal."),
    ("Can I see the property first?", "Yes. Call or text to set up a walk-through or get access details. We expect every buyer to do their own due diligence."),
    ("Are the ARV, repair and rent numbers guaranteed?", "No. They are our estimates to help you screen deals quickly. Verify them with your own contractor, agent and comps."),
    ("Do you promise zoning, buildability or title?", "No. On land especially, check zoning, buildability, utilities, size and title with the county and your title company before you close."),
]
page("/how-we-work/", "How Our Off-Market Deals Work | American Equity Group",
     "How buying an off-market deal from American Equity Group works: assignment contracts, 14 to 21 day closings, first come first served, buyer verifies.",
     f"""<section class="hero plain"><div class="wrap"><p class="eyebrow">How we work</p><h1>How Buying From Us Works</h1>
<p class="lead">Straightforward wholesale deals. We find the property, you verify it and close.</p></div></section>
<section><div class="wrap">{steps()}</div></section>
<section class="alt"><div class="wrap grid3">
<div class="box">{icon('deal')}<h3>Off-market</h3><p>We buy straight from owners through our own marketing. You won't find these on the MLS.</p></div>
<div class="box">{icon('list')}<h3>Assignment</h3><p>We sell our contract position by assignment. You close with the owner at a local title company.</p></div>
<div class="box">{icon('clock')}<h3>14 to 21 day closings</h3><p>Cash or hard money. Have your funding lined up before you lock up a deal.</p></div>
<div class="box">{icon('bolt')}<h3>First come, first served</h3><p>The first buyer to commit gets the deal. Matched buyers hear first, so sign up.</p></div>
<div class="box">{icon('shield')}<h3>Buyer verifies everything</h3><p>Our numbers are estimates. Check size, condition, zoning, utilities, rents and title yourself.</p></div>
<div class="box">{icon('map')}<h3>North Florida only</h3><p>Duval, Nassau, Clay, St. Johns, Baker, Putnam and Flagler counties.</p></div></div></section>
<section><div class="wrap" style="max-width:820px"><h2>Questions buyers ask</h2>
{''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQS)}</div></section>
{cta()}""",
     schema=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
         {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS]}])

# ---------- CONTACT ----------
page("/contact/", "Contact American Equity Group | (904) 685-8024",
     "Questions about a deal or getting on the buyers list? Call or text American Equity Group in Jacksonville at (904) 685-8024.",
     f"""<section class="hero plain"><div class="wrap"><p class="eyebrow">Contact</p><h1>Talk to Our Team</h1>
<p class="lead">Questions about a deal, a walk-through, or what we have coming up? Call or text.</p></div></section>
<section><div class="wrap grid2" style="align-items:start"><div class="box" style="text-align:center;padding:32px">
<p style="color:var(--mute);margin:0 0 4px">Call or text</p><p style="font-size:34px;font-weight:800;color:var(--navy);margin:0 0 18px">{PHONE}</p>
<a class="btn" href="tel:{TEL}">Call now</a> <a class="btn" style="background:var(--navy)" href="sms:{TEL}">Send a text</a>
<p style="margin-top:18px;font-size:15px">Mon to Sat, 8 AM to 7:30 PM. Leave a message after hours and we'll get back to you.</p></div>
<div><h2>When you reach out</h2><ul class="checks"><li>Tell us which deal, by street name, so we can pull it up fast</li>
<li>Have your funding ready: cash or hard money</li><li>Ask for photos, the parcel map or a walk-through</li></ul>
<p><a href="{B('/join-buyers-list/')}">Join the buyers list →</a></p></div></div></section>""")


# ---------- LEGAL ----------
def legal(h1, updated, sections):
    body = "".join(f"<h2 style=\"font-size:22px;margin-top:28px\">{h}</h2><p>{t}</p>" for h, t in sections)
    return f"""<section class="hero plain"><div class="wrap"><h1>{h1}</h1><p class="lead">Last updated: {updated}</p></div></section>
<section><div class="wrap" style="max-width:820px">{body}</div></section>"""

page("/privacy-policy/", "Privacy Policy | American Equity Group",
     "How American Equity Group collects and uses information from investors and buyers who use equitygroupjax.com or join our buyers list.",
     legal("Privacy Policy", "November 10, 2026", [
         ("Who we are", "American Equity Group LLC (\"we,\" \"us\") markets off-market real estate to investors. This policy explains what we collect on equitygroupjax.com and how we use it."),
         ("Information we collect", "Information you give us, such as your name, phone number, email and buying criteria (areas, price range, property types, funding and timeline), and basic usage data like pages visited and browser type."),
         ("How we use it", "To match you with properties that fit your criteria, send deal alerts you have agreed to receive, and respond to your questions. We do not sell your personal information."),
         ("Text messages", f"If you agree to receive texts from {PHONE}, message frequency varies and message and data rates may apply. Reply STOP to opt out or HELP for help. Consent is not a condition of any purchase. Mobile numbers and SMS consent are not shared with third parties or affiliates for marketing purposes."),
         ("Sharing", "We share information only with service providers who help us operate (for example our CRM, title companies and closing agents) or when required by law."),
         ("Your choices", f"You can ask us to update or delete your information or stop contacting you at any time. Call or text {PHONE}, or reply STOP to any text."),
         ("Contact us", f"American Equity Group LLC<br>4600 Touchton Road, Jacksonville, FL 32246<br>Call or text {PHONE}<br><a href=\"mailto:equitygroup904@gmail.com\">equitygroup904@gmail.com</a>"),
     ]))

page("/terms/", "Terms of Use | American Equity Group",
     "Terms for using equitygroupjax.com and receiving off-market deal information from American Equity Group LLC in Jacksonville, FL.",
     legal("Terms of Use", "November 10, 2026", [
         ("Using this site", "By using equitygroupjax.com you agree to these terms."),
         ("Deal information", "Property details, prices and numbers (including ARV, repairs and rents) are estimates provided for convenience. Buyer must verify all information, including size, zoning, buildability, utilities, condition and title, before closing. We make no promises about any of them."),
         ("Not an offer or advice", "Content on this site is general information, not legal, tax, investment or financial advice. A purchase happens only under a written agreement signed by both parties. Deals are offered first come, first served and may be withdrawn at any time."),
         ("We are not agents", "American Equity Group LLC is a real estate investment company, not a real estate brokerage, and holds equitable interest in the properties it markets."),
         ("Communications", "By joining our buyers list you agree that we may contact you by phone, text and email about properties."),
         ("Text messaging terms", f"If you check the SMS consent box on our forms, American Equity Group may text you at the number you provide about your buyer account, properties you ask about and, if you opt in to marketing texts, off-market deal alerts. Messages come from {PHONE}. Message frequency varies. Message and data rates may apply. Reply STOP to opt out at any time; you will get one message confirming you are unsubscribed. Reply HELP for help, or call or text {PHONE}. Carriers are not liable for delayed or undelivered messages. Consent to receive texts is not a condition of any purchase. See our <a href=\"/privacy-policy/\">Privacy Policy</a> for how we handle your information; mobile numbers and SMS consent are never shared with third parties or affiliates for marketing purposes."),
         ("Limitation of liability", "This site is provided \"as is.\" We are not liable for damages arising from its use."),
         ("Contact", f"American Equity Group LLC<br>4600 Touchton Road, Jacksonville, FL 32246<br>Call or text {PHONE}<br><a href=\"mailto:equitygroup904@gmail.com\">equitygroup904@gmail.com</a>"),
     ]))

# ---------- DEAL PAGES ----------
for d in DEALS:
    cls = d["status"].lower().replace(" ", "-")
    rows = [("Property type", d["type"]), ("Location", f"{d['address']}, {area(d)}"), ("County", d["county"] + " County")]
    if d["type"] == "Land":
        rows += [("Lot size", d.get("lot_size") or "Buyer to verify"), ("Zoning", d.get("zoning") or "Buyer to verify with county"),
                 ("Parcel ID", d.get("parcel_id") or "Ask us"), ("Utilities", d.get("utilities") or "Buyer to verify")]
    else:
        rows += [("Beds / baths", d.get("beds_baths", "")), ("Sq ft", d.get("sqft", "")), ("Parcel ID", d.get("parcel_id", ""))]
    for k, label in (("est_arv", "Est. ARV"), ("est_repairs", "Est. repairs"), ("est_rent", "Est. rent (per month)")):
        if d.get(k):
            rows.append((label, money(d[k]) + " (estimate)"))
    rows.append(("Terms", d["terms"]))
    facts = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in rows if b)
    if d.get("photos"):
        media = f'<div class="gallery{" one" if len(d["photos"]) <= 2 else ""}">' + "".join(f'<img src="{B(p["src"])}" alt="{esc(p["alt"])}" loading="lazy" width="600" height="400">' for p in d["photos"]) + "</div>"
        if d.get("photo_caption"):
            media += f'<p class="caption">{esc(d["photo_caption"])}</p>'
    else:
        media = f'<div class="noimg">{LAND_SVG}<span>Photos and parcel map on request</span></div>'
    bullets = "".join(f"<li>{esc(x)}</li>" for x in d.get("details", []))
    county_link = (f'<p style="margin-top:12px"><a href="{esc(d["county_record"])}" target="_blank" rel="noopener">View the county property appraiser record →</a></p>'
                   if d.get("county_record") else "")
    for extra in d.get("county_records_extra", []):
        county_link += f'<p style="margin-top:6px"><a href="{esc(extra["url"])}" target="_blank" rel="noopener">{esc(extra["label"])} →</a></p>'
    land_note = (" On land, buyer verifies zoning, buildability, utilities, size and title. We make no promises on any of them."
                 if d["type"] == "Land" else "")
    desc = f"{d['headline']} in {area(d)}, {d['county']} County. {money(d['price'])}, off-market, assignment. Call or text {PHONE}."
    if len(desc) > 160:
        desc = f"{d['type']} in {area(d)}. {money(d['price'])}, off-market. Call or text {PHONE}."
    offer_cta = (f'<a class="btn" href="sms:{TEL}">Text to make an offer</a><a class="btn ghost" href="tel:{TEL}">Call {PHONE}</a>'
                 if d["status"] != "Sold" else f'<a class="btn" href="{B("/join-buyers-list/")}">Get the next one first</a>')
    page(deal_url(d), d["title"], desc,
         f"""<section class="hero plain"><div class="wrap"><p class="crumbs"><a href="{B('/current-deals/')}">Current deals</a> / {esc(d['county'])} County</p>
<span class="badge {cls}" style="position:static;display:inline-block;margin-bottom:10px">{esc(d['status'])}</span>
<h1>{esc(d['title'])}</h1><p class="lead">{esc(d['headline'])}. {esc(d['address'])}, {esc(area(d))}.</p></div></section>
<section><div class="wrap dealhead"><div>{media}
<h2 style="margin-top:28px">Property details</h2><ul class="checks">{bullets}</ul>
<table class="facts">{facts}</table>
{county_link}<p class="note" style="margin-top:20px"><b>Buyer to verify.</b> All information and numbers are estimates.{land_note}</p></div>
<aside class="pricebox"><div class="price">{money(d['price'])}</div><p>{esc(d['type'])} · {esc(area(d))}<br>Off-market · Assignment · First come, first served</p>
{offer_cta}</aside></div></section>
{cta("Want deals like this before they post?")}""",
         schema=[{"@context": "https://schema.org", "@type": "Offer", "name": d["title"], "price": d["price"], "priceCurrency": "USD",
                  "availability": "https://schema.org/" + ("InStock" if d["status"] == "Available" else "SoldOut" if d["status"] == "Sold" else "LimitedAvailability"),
                  "url": SITE + deal_url(d),
                  "itemOffered": {"@type": "Place", "name": f"{d['address']}, {area(d)}",
                                  "address": {"@type": "PostalAddress", "streetAddress": d["address"], "addressLocality": d["city"],
                                              "addressRegion": "FL", "postalCode": d.get("zip", ""), "addressCountry": "US"}}}])

# ---------- 404 ----------
NOTFOUND = shell("/404.html", "Page not found | American Equity Group", "This page doesn't exist.",
                 f"""<section class="hero plain"><div class="wrap"><h1>That page isn't here</h1><p class="lead">The deal may have closed or moved.</p>
<div class="ctas"><a class="btn" href="{B('/current-deals/')}">See current deals</a><a class="btn ghost" href="{B('/')}">Home</a></div></div></section>""")


def write(rel, text):
    path = os.path.join(DIST, rel.lstrip("/"))
    if rel.endswith("/"):
        path = os.path.join(path, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    for slug, text in PAGES.items():
        assert "(904) 750" not in text and "7503565" not in text, f"{slug}: wrong phone number"
        write(slug, text)
    write("/404.html", NOTFOUND)
    shutil.copytree(os.path.join(ROOT, "img"), os.path.join(DIST, "img"))
    write("/favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1f8a4c"/>'
          '<path d="M14 34 32 18l18 16M20 30v16h24V30" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/></svg>')
    today = datetime.date.today().isoformat()
    urls = "".join(f"<url><loc>{SITE}{s}</loc><lastmod>{today}</lastmod></url>\n" for s in PAGES)
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("/robots.txt", (f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n") if LIVE else "User-agent: *\nDisallow: /\n")
    write("/.nojekyll", "")
    if LIVE:
        write("/CNAME", "equitygroupjax.com\n")
    print(f"built {len(PAGES)} pages + 404 into docs/ (BASE={BASE!r}, LIVE={LIVE})")


if __name__ == "__main__":
    main()

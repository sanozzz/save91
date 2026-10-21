"""Seed plan, investor version (21 Oct 2026). Name is a WORKING name (operator: "Keep name tentive (savemore/ save 91 etc)"). Landscape 16:9 pages, one claim per page.
Operator: "beautification of the document is required ... quality isnt good to be shareable with any VC".
Audience: seed investors. So no internal language (operator / judgement / file names / research IDs) on the pages;
sources are named in plain words; the internal critical review is NOT in this document.
Numbers: tables/seed_plans.csv, seed_people.csv, seed_sensitivity.csv (model/seed_plan.py).
Builds seed/Seed_Plan_investor.html and .pdf (Chrome headless)."""
import math
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TAB = HERE.parent / "tables"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

INK, NAVY, TEAL, BLUE, AMBER, SLATE = "#0b1f33", "#12355b", "#0f9d8a", "#2563eb", "#d97706", "#64748b"
TEAL_L, BLUE_L, AMBER_L, NAVY_L, LINE, BG = "#e7f6f4", "#eaf1fe", "#fdf3e3", "#e9eef5", "#e2e8f0", "#f8fafc"
RED, RED_L, MUTE = "#b42318", "#fef3f2", "#94a3b8"
NAVY2, NAVY3, NAVY4 = "#1d4f86", "#2b6cb0", "#5b8fc7"   # product and team; teal = acquisition; amber = doorstep pilot; slate = contingency/later
FONT = '"Avenir Next", "Helvetica Neue", Helvetica, Arial, sans-serif'

PL = pd.read_csv(TAB / "seed_plans.csv").set_index("plan")
P = PL.loc["pitch"]
LEAN = PL.loc["pitch_lean_costs"]
PEOPLE = pd.read_csv(TAB / "seed_people.csv")
SENS = pd.read_csv(TAB / "seed_sensitivity.csv")
INPUTS = pd.read_csv(TAB / "seed_inputs.csv")
FX = float(INPUTS.loc[INPUTS.input == "Planning rate", "value"].iloc[0])   # operator: Rs 95 per $
NAME = "Save91 / SaveMore"     # working name, not final
RAISE = 500_000
TP, ACQ = P.tp_24_usd, P.acq_usd
RES = RAISE - TP - ACQ
MAX_ACQ = RAISE - TP


def k(usd):
    return f"${usd / 1e3:.0f}k"


def ppl(n):
    n = float(n)
    if n >= 1e5:
        return f"{n / 1e5:.2f}".rstrip("0").rstrip(".") + " lakh"
    return f"{round(n, -2):,.0f}"


def rs(x):
    w = f"{abs(round(x)):.0f}"
    if len(w) > 3:
        head, tail = w[:-3], w[-3:]
        w = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1]) + "," + tail
    return "₹" + w


def usd_li(col):
    return P[col] / FX


# ---------- svg helpers (px units; the svg spans the 1152px content width) ----------
def svg(w, h, body):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" style="font-family:{FONT}">{body}</svg>'


def T(x, y, s, size=13, weight=500, fill=INK, anchor="start", ls=0):
    sp = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{sp}>{s}</text>'


def R(x, y, w, h, fill, stroke=None, r=10, sw=1.5, dash=False):
    st = f' stroke="{stroke}" stroke-width="{sw}"' + (' stroke-dasharray="6 5"' if dash else "") if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{st}/>'


def A(x1, y1, x2, y2, col=SLATE, w=2.2, dash=False):
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 11 * math.cos(a), y2 - 11 * math.sin(a)
    p1 = (hx - 5.5 * math.sin(a), hy + 5.5 * math.cos(a))
    p2 = (hx + 5.5 * math.sin(a), hy - 5.5 * math.cos(a))
    d = ' stroke-dasharray="6 5"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>'
            f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}"/>')


def page(n, section, kicker, title, lede, body, src=""):
    s = f'<div class="src">{src}</div>' if src else ""
    return f"""<section class="page">
<header class="ph"><span class="brand">{NAME} <em>· working name</em></span><span>{section}</span></header>
<div class="kicker">{kicker}</div><h1>{title}</h1>{f'<p class="lede">{lede}</p>' if lede else ''}
<div class="body">{body}</div>{s}
<footer class="pf"><span>Seed plan · October 2026 · Confidential</span><span>{n}</span></footer>
</section>"""


# ---------- page 1: cover ----------
def cover():
    share = lambda v: f"{v / RAISE:.0%}"
    tiles = [("$500k", "seed raise"), ("24 months", f"plan period, plus a {RES / RAISE:.0%} contingency"),
             (ppl(P.customers), f"sign-ups; ~{ppl(round(P.savers_won, -2))} start saving, ~{ppl(round(P.active_savers_m18, -2))} still saving at month 18"),
             ("5 people", "Piyush (CEO), Sandeep (CPTO) + 3 hires")]
    t = "".join(f'<div class="ctile"><div class="cbig">{a}</div><div class="csub">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle">Seed plan</div>
  <div class="ctag">Daily saving for India's self-employed, in mutual funds, in their own name. Online-first, with a doorstep pilot.</div>
  <div class="cmeta">Raising $500k · October 2026 · Confidential</div>
</div>
<div class="cright">
  <div class="cgrid">{t}</div>
  <div class="csplit">
    <div style="flex:{TP:.0f};background:{NAVY}">Product and team · {share(TP)}</div>
    <div style="flex:{ACQ:.0f};background:{TEAL}">Customer acquisition · {share(ACQ)}</div>
    <div style="flex:{RES:.0f};background:{SLATE}">Contingency · {share(RES)}</div>
  </div>
  <div class="cnote">Mostly to build the product. Revenue is not counted anywhere in this plan.</div>
</div>
</section>"""


# ---------- page 2: use of funds ----------
TP_ITEMS = [("Salaries: 2 founders + 3 hires", "Salaries"), ("App: build and running", "App and tech"),
            ("Office and fund-raising", "Office and fund-raising"), ("Setup, licences, compliance", "Licences and compliance"),
            ("Customer support", "Support"), ("Design while building", "Design (outsourced)")]
ACQ_ITEMS = [("Online sign-ups", "Online acquisition"), ("KYC checks", "KYC"), ("Doorstep pilot, 1 city", "Doorstep test arm")]


def funds_bar():
    W = 1152
    segs = [(TP, NAVY, "Product and team"), (ACQ, TEAL, "Customer acquisition"), (RES, SLATE, "Contingency")]
    s, x = [], 0
    for v, col, lab in segs:
        w = W * v / RAISE
        s.append(R(x, 0, w - 4, 64, col, r=12))
        s.append(T(x + 18, 28, lab.upper(), 12, 700, "#fff", ls=1.2))
        s.append(T(x + 18, 52, f"{k(v)} · {v / RAISE:.0%}", 19, 700, "#fff"))
        x += w
    return svg(W, 66, "".join(s))


def items(rows, col, total, note):
    top = max(usd_li(c) for _, c in rows)
    li = "".join(f'<div class="li"><span>{a}</span><div class="lbar"><i style="width:{usd_li(c) / top * 100:.0f}%;background:{col}"></i></div>'
                 f'<b>{k(usd_li(c)) if usd_li(c) >= 9_500 else f"${usd_li(c) / 1e3:.1f}k"}</b></div>' for a, c in rows)
    return f'<div class="fcol"><div class="ftot" style="color:{col}">{total}</div>{li}<div class="fnote">{note}</div></div>'


def p_funds():
    spare_2x = RAISE - TP - SENS.acq_usd.max()
    body = funds_bar() + '<div class="fcols">' + \
        items(TP_ITEMS, NAVY, f"Product and team · {k(TP)}", f"24 months. Salaries {k(P.salaries_24_usd)}, founders at $1,000 a month each.") + \
        items(ACQ_ITEMS, TEAL, f"Customer acquisition · {k(ACQ)}", f"{ppl(P.customers)} sign-ups in months 4–18; {rs(round(P.acq_per_saver, -1))} per saver won, online and doorstep blended (₹600 online).") + \
        f"""<div class="fcol"><div class="ftot" style="color:{SLATE}">Contingency · {k(RES)}</div>
<div class="rbox"><b>Covers the downside.</b> If a sign-up costs ₹200, not ₹100, acquisition costs {k(SENS.acq_usd.max())}
and the plan still fits in $500k, with about {k(spare_2x)} to spare.</div>
<div class="rbox"><b>Or buys time.</b> If the next round is late, it keeps the lean team and the savers served while the round closes.
The company plan raises in month 19 and scales from there; it does not count this reserve.</div></div>""" + "</div>"
    return page(2, "Use of funds", "THE $500K", f"The money builds the product first; {RES / RAISE:.0%} is held as contingency",
                "", body, f"All figures over 24 months, at a planning rate of ₹{FX:.0f} per $. Revenue is not included, so every number is a cost.")


# ---------- page 3: product ----------
PHASES = [("1", "Save", "Months 1–3 · live in month 4", NAVY, ["Sign-up with e-KYC and a bank check", "Daily saving from ₹100 into equity and debt funds (80/20)",
                                                               "One UPI Autopay mandate", "Withdraw any day; money back in 1–3 working days"]),
          ("2", "Habit", "Months 4–9", NAVY2, ["Goals, streaks and nudges", "Referrals (no cashback, by rule)", "Doorstep agent app for the pilot",
                                                "Savings analytics"]),
          ("3", "Offers", "Months 7–12", NAVY3, ["Loan offers from partner lenders", "Insurance through a partner", "Credit cards from issuers",
                                                   "Shown only when relevant"]),
          ("4", "Score and plan", "Months 10–18", NAVY4, ["Savings-record score", "AI money coach", "Wallet-like view; money stays in funds",
                                                          "Better offers for steady savers"])]


def phones():
    scr = [("Sign up", "mobile + PAN"), ("KYC", "Aadhaar + bank"), ("Daily amount", "from ₹100"), ("Autopay", "one UPI mandate"),
           ("Home", "saved · streak"), ("Withdraw", "any day")]
    s = []
    for i, (a, b) in enumerate(scr):
        x = 10 + i * 192
        s.append(R(x, 4, 128, 150, "#fff", LINE, 18, 1.6))
        s.append(R(x + 50, 12, 28, 5, LINE, r=2.5))
        s.append(f'<circle cx="{x + 64}" cy="58" r="20" fill="{NAVY_L}"/>' + T(x + 64, 65, str(i + 1), 18, 700, NAVY, "middle"))
        s.append(T(x + 64, 106, a, 14, 700, INK, "middle"))
        s.append(T(x + 64, 126, b, 11.5, 500, SLATE, "middle"))
        if i < 5:
            s.append(A(x + 136, 79, x + 184, 79, MUTE, 1.8))
    return svg(1152, 160, "".join(s))


def p_product():
    cards = "".join(f"""<div class="ph-card"><div class="ph-top" style="background:{col}"><span class="ph-n">{n}</span><div><div class="ph-h">{h}</div>
<div class="ph-m">{m}</div></div></div><ul>{''.join(f'<li><i style="color:{col}">✓</i>{f}</li>' for f in feats)}</ul></div>""" for n, h, m, col, feats in PHASES)
    body = f'<div class="phases">{cards}</div><div class="sub-h">THE FIRST APP: SIX SCREENS</div>{phones()}'
    return page(3, "Product", "WHAT THE MONEY BUILDS", "Four releases in 18 months, with customers using it from month 4",
                "", body)


# ---------- page 4: how money moves ----------
def flow():
    s = []
    nodes = [(0, 150, 190, "Saver's own", "bank account", BLUE, BLUE_L), (300, 150, 220, "Exchange clearing", "BSE StAR MF", TEAL, TEAL_L),
             (630, 150, 200, "Fund house", "the AMC", TEAL, TEAL_L), (940, 150, 200, "Units held", "in the saver's name", TEAL, TEAL_L)]
    for x, y, w, a, b, col, bg in nodes:
        s.append(R(x, y, w, 76, bg, col, 14, 1.8))
        s.append(T(x + w / 2, y + 34, a, 16, 700, col, "middle"))
        s.append(T(x + w / 2, y + 56, b, 13, 500, INK, "middle"))
    s.append(A(194, 188, 296, 188, TEAL, 2.6))
    s.append(T(245, 178, "daily", 12, 700, TEAL, "middle"))
    s.append(A(524, 188, 626, 188, TEAL, 2.6))
    s.append(A(834, 188, 936, 188, TEAL, 2.6))
    # app
    s.append(R(330, 18, 360, 74, NAVY, r=14))
    s.append(T(510, 50, "Our app · registered distributor", 16, 700, "#fff", "middle"))
    s.append(T(510, 74, "KYC, orders, dashboard, offers", 13, 500, "#c9d6e6", "middle"))
    s.append(A(410, 94, 410, 146, NAVY, 2.2, dash=True))
    s.append(T(420, 126, "sends orders", 12, 700, NAVY))
    s.append(A(730, 146, 676, 96, NAVY, 2.2))
    s.append(T(742, 112, "trail fee from the fund house:", 12, 700, NAVY))
    s.append(T(742, 128, "0.75% a year on equity, 0.35% on debt", 12, 500, NAVY))
    # withdraw loop
    s.append(f'<path d="M730 228 L730 276 L95 276 L95 238" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    s.append(f'<polygon points="95,228 89,241 101,241" fill="{BLUE}"/>')
    s.append(T(412, 268, "withdraw any day: back to the saver's bank in 1–3 working days", 12.5, 700, BLUE, "middle"))
    # lender
    s.append(R(630, 306, 200, 64, "#f1f5f9", SLATE, 14, 1.8))
    s.append(T(730, 334, "Partner lender", 15, 700, SLATE, "middle"))
    s.append(T(730, 354, "bank or NBFC", 12.5, 500, INK, "middle"))
    s.append(f'<path d="M630 338 L48 338 L48 238" fill="none" stroke="{SLATE}" stroke-width="2.4"/>')
    s.append(f'<polygon points="48,228 42,241 54,241" fill="{SLATE}"/>')
    s.append(T(340, 330, "loan paid straight to the saver's bank; the saver repays the lender", 12.5, 700, SLATE, "middle"))
    s.append(T(846, 344, "pays us a marketing fee", 12.5, 700, SLATE))
    # doorstep
    s.append(R(0, 18, 250, 74, AMBER_L, AMBER, 14, 1.6, dash=True))
    s.append(T(125, 48, "Doorstep agent (pilot)", 15, 700, AMBER, "middle"))
    s.append(T(125, 70, "signs savers up, sets the mandate", 12, 500, INK, "middle"))
    s.append(A(95, 94, 95, 146, AMBER, 2, dash=True))
    return svg(1152, 380, "".join(s))


def p_flow():
    chips = [("In the saver's name", "Units sit with the fund house, registered to the saver."), ("Never through us", "We hold no customer money, ever."),
             ("Paid by partners", "Fund houses and lenders pay us; we charge the saver nothing (the trail comes from the fund's own expense ratio).")]
    c = "".join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in chips)
    return page(4, "How it works", "THE MONEY FLOW", "Money moves from the saver's bank to the fund and back, never through us",
                "", flow() + f'<div class="chips3">{c}</div>',
                "Sources: SEBI (payments come from the investor's own account), BSE StAR MF (no transaction fee for distributors), "
                "fund-house disclosures (distributor trail).")


# ---------- page 5: regulatory path ----------
REG = [("Before launch · months 0–3", NAVY, NAVY_L, [("Company setup, ₹1.25 lakh", "includes AMFI distributor registration (₹40,000 + GST)"),
                                                   ("NISM exam for both founders", "₹1,500 + GST each; renewed every 3 years"),
                                                   ("BSE StAR MF access", "orders and SIP mandates; no transaction fee to distributors"),
                                                   ("3–5 fund houses", "empanelled for equity and debt funds"),
                                                   ("KYC and UPI Autopay partners", "e-KYC ₹3–7 a check (₹40 budgeted per KYC with KRA, PAN and bank checks); daily mandates allowed"),
                                                   ("Data protection", "consent flows and data kept in India")]),
       ("After launch · months 4–12", NAVY3, "#eef4fb", [("Loans as a DSA / lending service provider", "from month 7: partner lenders pay us per loan; RBI digital-lending rules apply (the borrower pays us nothing)"),
                                      ("Insurance through a partner", "from month 7; our own licence later"),
                                      ("Credit cards with issuers", "the issuer decides every card"),
                                      ("Two legal opinions first", "the marketing-partner model; any cash at the doorstep")]),
       ("With the next round", SLATE, "#f1f5f9", [("Become a lending service provider", "larger fees; first-loss cover capped at 5%"),
                                                 ("Own NBFC", "₹10 crore of capital; about 8–14 months or more"),
                                                 ("Insurance distribution licence", "under IRDAI's draft rules, once final")])]


def p_reg():
    cols = ""
    for head, col, bg, its in REG:
        cards = "".join(f'<div class="rcard" style="border-color:{col};background:{bg}"><b style="color:{col}">{a}</b><span>{b}</span></div>' for a, b in its)
        cols += f'<div class="rcol"><div class="rhead" style="background:{col}">{head}</div>{cards}{"<!--NEVER-->" if col == NAVY3 else ""}</div>'
    never = ["Hold customer money", "Offer cashback on funds or insurance", "Run lucky draws or savings circles", "Use anyone's data without consent"]
    nv = "".join(f'<div class="nv">✕ {n}</div>' for n in never)
    cols = cols.replace("<!--NEVER-->", f'<div class="never"><b>We will never</b>{nv}</div>')
    body = f'<div class="rcols">{cols}</div>'
    return page(5, "Regulatory path", "LICENCES AND TIE-UPS", "Day one needs no RBI licence; each later step adds one", "", body,
                "Sources: AMFI, NISM, RBI Digital Lending Directions 2025, RBI NBFC capital norms, IRDAI, Banning of Unregulated Deposit Schemes Act 2019, "
                "Digital Personal Data Protection Act 2023.")


# ---------- page 6: team ----------
def salary_bar():
    lean = PEOPLE[PEOPLE.team == "plan"]
    cols = {"Piyush (CEO)": NAVY, "Sandeep (CPTO)": NAVY2, "Engineer (full-stack + mobile)": NAVY3, "Ops + support executive": NAVY4,
            "Junior engineer": "#7fa7d6"}
    short = {"Piyush (CEO)": "Piyush", "Sandeep (CPTO)": "Sandeep", "Engineer (full-stack + mobile)": "Engineer",
             "Ops + support executive": "Ops", "Junior engineer": "Jr eng."}
    W, x0 = 1152, 0
    X = lambda v: (W - 120) * v / 100_000
    s, x = [], x0
    for r in lean.itertuples():
        w = X(r.cost_24_usd)
        s.append(R(x, 22, w - 3, 40, cols[r.role], r=6))
        s.append(T(x + w / 2, 47, f"{short[r.role]} {k(r.cost_24_usd)}", 12.5, 700, "#fff", "middle"))
        x += w
    cap = X(100_000)
    s.append(R(x, 22, cap - x, 40, "#fff", MUTE, 6, 1.2, dash=True))
    s.append(f'<line x1="{cap}" y1="14" x2="{cap}" y2="70" stroke="{RED}" stroke-width="3"/>')
    s.append(T(cap + 10, 47, "$100k cap", 14, 700, RED))
    s.append(T(0, 12, f"SALARIES OVER 24 MONTHS: {k(lean.cost_24_usd.sum())}", 11.5, 700, SLATE, ls=1.1))
    return svg(W, 72, "".join(s))


def p_team():
    def founder(name, title, owns, col):
        li = "".join(f"<li>{o}</li>" for o in owns)
        return f'<div class="fcard" style="border-top:5px solid {col}"><div class="fn">{name}</div><div class="ft" style="color:{col}">{title}</div><ul>{li}</ul></div>'

    def hire(role, when, pay, note, col):
        return f'<div class="hcard"><div><b>{role}</b><span>{note}</span></div><em style="background:{col}">{when} · {pay}</em></div>'
    left = founder("Piyush", "CEO · $1,000 a month", ["Growth: ads, referrals, brand", "Partnerships: fund houses, lenders, insurers",
                                                     "Fund-raising and investors", "Compliance and finance, with the CA and lawyer",
                                                     f"Runs the doorstep pilot ({int(P.agents)} agents)"], NAVY)
    right = founder("Sandeep", "CPTO · $1,000 a month", ["Product: roadmap, design, app", "Engineering: integrations, security",
                                                         "Data: the savings-record score, AI coach", "Product operations: KYC, mandates, support"], NAVY2)
    hires_ceo = hire(f"{int(P.agents)} doorstep agents (pilot)", "m4–18", "₹26k each", "in the customer budget, not salaries", AMBER) + \
        hire("CA and lawyer", "m1", "retainer", "in the compliance budget", SLATE)
    hires_cpto = hire("Engineer, full-stack + mobile", "m1", "₹1.1L", "builds the app with Sandeep", NAVY3) + \
        hire("Ops + support executive", "m4", "₹30k", "KYC, failed debits, withdrawals", NAVY4) + \
        hire("Junior engineer", "m7", "₹50k", "offers, agent app, the score", "#7fa7d6")
    body = f"""<div class="team"><div class="tcol">{left}<div class="rep">Works with</div>{hires_ceo}</div>
<div class="tcol">{right}<div class="rep">Reports to Sandeep</div>{hires_cpto}</div></div>{salary_bar()}"""
    return page(6, "Team", "FIVE PEOPLE", f"Five people, and {k(P.salaries_24_usd)} of salaries over 24 months",
                "", body, "Founders draw $1,000 a month each until the next round. Hire pay is monthly cost to company. Design is outsourced while the app is built.")


# ---------- page 7: customers ----------
def funnel():
    on_reg = P.online_registrations
    kyc = on_reg * 0.5
    on_sav = P.savers_won - P.doorstep_signups
    rows = [("Online sign-ups", on_reg, TEAL, "₹100 each"), ("Finish KYC", kyc, "#7fd1c6", "1 in 2"), ("Start saving, online", on_sav, "#0b7f70", "2 in 5 of KYC'd"),
            ("Doorstep savers", P.doorstep_signups, AMBER, f"{int(P.agents)} agents; saving starts at sign-up"), ("Savers won", P.savers_won, "#0b5d52", f"{P.doorstep_signups / P.savers_won:.0%} from the doorstep"),
            ("Still saving at month 18", P.active_savers_m18, "#0b6b5e", "")]
    s = []
    for i, (lab, v, col, note) in enumerate(rows):
        y = i * 52
        w = 330 * v / on_reg
        s.append(T(0, y + 22, lab, 13.5, 600))
        s.append(R(190, y + 4, max(w, 4), 28, col, r=6))
        s.append(T(190 + max(w, 4) + 10, y + 23, ppl(v), 14, 700, col))
        if note:
            s.append(T(712, y + 23, note, 11.5, 500, SLATE, "end"))
    return svg(720, 6 * 52, "".join(s))


def sens():
    s = [T(0, 12, "WHAT 1 LAKH SIGN-UPS COSTS IF ONE NUMBER MOVES", 11.5, 700, SLATE, ls=1.1)]
    labels = {"Agreed inputs": "Our estimate", "Online sign-up costs Rs 60 (referrals work)": "Sign-up costs ₹60",
              "Online sign-up costs Rs 200": "Sign-up costs ₹200", "1 in 10 sign-ups starts saving (Jar-like)": "1 in 10 sign-ups save",
              "3 in 10 sign-ups start saving": "3 in 10 sign-ups save"}
    X = lambda v: 105 * v / MAX_ACQ
    for i, r in SENS.iterrows():
        y = 26 + i * 34
        s.append(T(0, y + 17, labels[r.case], 12, 600 if i == 0 else 500))
        better = r.acq_per_saver <= SENS.acq_per_saver.iloc[0]   # judged by cost per saver won, not total spend
        col = NAVY if i == 0 else (TEAL if better else AMBER)
        s.append(R(160, y + 3, X(r.acq_usd), 20, col, r=5))
        s.append(T(420, y + 18, f"{k(r.acq_usd)} · {ppl(round(r.savers_won, -2))} savers", 11.5, 700, col, "end"))
    xm = 160 + X(MAX_ACQ)
    s.append(f'<line x1="{xm}" y1="22" x2="{xm}" y2="{28 + len(SENS) * 34}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(T(xm + 4, 42 + len(SENS) * 34, f"acquisition ceiling: {k(MAX_ACQ)}", 11, 700, RED, "middle"))
    s.append(T(0, 66 + len(SENS) * 34, "Plan: 1 in 5 sign-ups save. Fewer savers need fewer", 10.5, 500, SLATE))
    s.append(T(0, 81 + len(SENS) * 34, "doorstep agents, so that case costs a little less.", 10.5, 500, SLATE))
    return svg(420, 88 + len(SENS) * 34, "".join(s))


def p_customers():
    body = f"""<div class="gtm"><div class="gl"><div class="sub-h">THE FUNNEL, MONTHS 4–18</div>{funnel()}</div>
<div class="gr"><div class="kpis"><div class="kpi"><b>{rs(round(P.acq_per_saver, -1))}</b><span>to win a saver, all-in</span></div>
<div class="kpi"><b>{k(ACQ)}</b><span>for 1 lakh sign-ups</span></div></div>{sens()}</div></div>"""
    return page(7, "Customers", "1 LAKH SIGN-UPS", f"1 lakh sign-ups for {k(ACQ)}, and the plan holds even if they cost twice as much",
                "", body, "Install costs, vendor benchmarks: fintech median ₹75, wealth apps ₹100–300. Retention: of SBI MF's ₹250 daily SIPs started in FY26, "
                          "36% had stopped by year-end (about 38% still saving at a year): our online plan; 55% at the doorstep.")


# ---------- page 8: milestones ----------
def gantt():
    END = 24
    x0, W = 250, 1152
    w = (W - x0) / END
    X = lambda m: x0 + (m - 1) * w
    rows = [("Set up: company, AMFI, NISM", 1, 1, NAVY), ("Fund houses, exchange, KYC, mandates", 1, 3, NAVY),
            ("Release 1: Save", 1, 3, NAVY), ("Release 2: Habit", 4, 9, NAVY2), ("Release 3: Offers", 7, 12, NAVY3),
            ("Release 4: Score and plan", 10, 18, NAVY4), ("Keep building", 19, END, "#9fb8d6"),
            ("Online customers", 4, 18, TEAL), ("Doorstep pilot, 1 city", 4, 18, AMBER), ("Next round", 16, 21, INK)]
    s = []
    for m in range(1, END + 1):
        s.append(T(X(m) + w / 2, 12, str(m), 10.5, 600, MUTE, "middle"))
        if m % 3 == 1:
            s.append(f'<line x1="{X(m)}" y1="20" x2="{X(m)}" y2="{24 + len(rows) * 27}" stroke="{LINE}"/>')
    for i, (lab, a, b, col) in enumerate(rows):
        y = 22 + i * 27
        s.append(T(0, y + 15, lab, 12.5, 600))
        s.append(R(X(a) + 1, y + 3, (b - a + 1) * w - 2, 16, col, r=5))
    yb = 30 + len(rows) * 27
    for m, lab, col in ((4, "Launch", TEAL), (10, "6 months of data", AMBER), (16, "12 months of data", RED), (24, "Plan ends", SLATE)):
        xm = X(m) + w / 2
        s.append(f'<polygon points="{xm},{yb} {xm - 7},{yb + 10} {xm},{yb + 20} {xm + 7},{yb + 10}" fill="{col}"/>')
        s.append(T(xm + (10 if m == END else 0), yb + 36, lab, 11.5, 700, col, "end" if m == END else "middle"))
    return svg(W, yb + 42, "".join(s))


def p_milestones():
    # aligned with the online-first business case (online/Online_business_case.pdf): plan value -> the value that brings profit into year 5
    LV = pd.read_csv(TAB / "online_levers.csv").set_index("case")          # same numbers as the business case
    mo = lambda k: int(LV.loc[k]["EBITDA positive from month"])
    b = mo("Today's evidence")
    gates = [("Cost to win a saver", f"₹600 an online saver in the seed ({rs(round(P.acq_per_saver, -1))} blended with doorstep); ₹450 planned after; ₹300 (a competitor's figure) brings profit {b - mo('Cost to win Rs 300')} months sooner"),
             ("Still saving at 12 months", f"38% online is the plan; 45% brings profit {b - mo('45% still saving at a year')} months sooner"),
             ("Daily amount", f"₹100 is the plan; ₹200 brings profit {b - mo('Rs 200 a day')} months sooner"),
             ("Who borrows", f"35% of KYC'd users apply a year is the plan; at 10% profit comes {mo('10% apply for a loan a year') - b} months later"),
             ("Doorstep arm", "must clearly beat online's 38% still saving (55% is the plan) to stay")]
    g = "".join(f'<div class="gate"><span>{i + 1}</span><b>{a}</b><em>{b}</em></div>' for i, (a, b) in enumerate(gates))
    body = gantt() + f'<div class="sub-h" style="margin-top:6px">WHAT WE WILL PROVE BEFORE THE NEXT ROUND</div><div class="gates">{g}</div>'
    return page(8, "Milestones", "24 MONTHS", "Build, launch, prove, then raise on 12 months of data", "", body)


# ---------- page 9: assumptions ----------
ASSUME = [("Planning rate", f"₹{FX:.0f} per $", "Founders' planning rate"),
          ("Founders' pay", "$1,000 a month each", "Founders' decision, until the next round"),
          ("Hires (monthly cost to company)", "Engineer ₹1.1L · junior engineer ₹50k · ops ₹30k", "Our estimate"),
          ("Company setup", "₹1.25 lakh, one-time", "Includes AMFI registration, ₹40,000 + GST"),
          ("Compliance", "₹10 lakh a year", "CA, legal, renewals; our estimate"),
          ("App", "₹15 lakh to integrate, ₹1.5 lakh a month to run", "Our estimate"),
          ("Office", "₹75,000 a month", "Co-working"),
          ("Online sign-up", "₹100 each", "Our estimate; app installs cost ₹75 (fintech median) to ₹100–300 (wealth apps)"),
          ("Sign-up to saver", "1 in 2 finish KYC; 2 in 5 of them start saving", "Our estimate; the first thing the launch measures"),
          ("KYC", "₹40 per sign-up", "e-KYC ₹3–7, KRA upload ₹30, PAN and bank checks"),
          ("Still saving at 12 months", "38% online · 55% doorstep", "SBI MF's ₹250 daily SIP (36% stopped by ~6 months on average); savings apps' 24% is the downside"),
          ("Doorstep agent", "₹26,000 a month all-in; 100 sign-ups a month, saving from sign-up", "Our estimate, from field-sales practice"),
          ("Customer support", "₹5 per active saver a month", "Our estimate"),
          ("Revenue", "not counted", "Fund-house trail and partner fees are upside")]


def p_assume():
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in ASSUME)
    body = f'<table class="at"><tr><th>Assumption</th><th>Value</th><th>Basis</th></tr>{rows}</table>'
    return page(9, "Appendix", "ASSUMPTIONS", "Every number in this plan, and where it comes from", "", body)


CSS = f"""
@page {{ size: 13.333in 7.5in; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: #fff; }}
body {{ font-family: {FONT}; color: {INK}; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.page {{ width: 1280px; height: 720px; padding: 34px 64px 40px; position: relative; overflow: hidden; page-break-after: always; }}
.ph {{ display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: {SLATE}; letter-spacing: .14em;
      text-transform: uppercase; padding-bottom: 12px; border-bottom: 1px solid {LINE}; margin-bottom: 22px; }}
.brand {{ font-size: 15px; font-weight: 700; color: {NAVY}; letter-spacing: 0; text-transform: none; }}
.brand em {{ font-style: normal; font-weight: 500; color: {MUTE}; font-size: 12px; }}
.cwork {{ font-size: 13px; color: #9fb3cc; margin-top: 6px; }}
.brand b, .cbrand b {{ color: {TEAL}; }}
.kicker {{ font-size: 11.5px; font-weight: 700; color: {TEAL}; letter-spacing: .16em; margin-bottom: 6px; }}
h1 {{ font-size: 29px; font-weight: 600; line-height: 1.16; margin: 0 0 20px; letter-spacing: -.012em; max-width: 1060px; }}
.lede {{ font-size: 15px; color: #475569; margin: -10px 0 18px; }}
.pf {{ position: absolute; left: 64px; right: 64px; bottom: 16px; display: flex; justify-content: space-between; font-size: 12px; color: {SLATE}; }}
.src {{ position: absolute; left: 64px; right: 64px; bottom: 38px; font-size: 11px; color: {SLATE}; line-height: 1.4; }}
.sub-h {{ font-size: 11.5px; font-weight: 700; color: {SLATE}; letter-spacing: .1em; margin: 12px 0 8px; }}
/* cover */
.cover {{ padding: 0; display: flex; }}
.cleft {{ width: 520px; background: {NAVY}; color: #fff; padding: 64px 56px; display: flex; flex-direction: column; }}
.cbrand {{ font-size: 26px; font-weight: 700; }}
.ctitle {{ font-size: 64px; font-weight: 600; letter-spacing: -.02em; margin-top: 150px; line-height: 1; }}
.ctag {{ font-size: 18px; line-height: 1.5; color: #c9d6e6; margin-top: 20px; max-width: 400px; }}
.cmeta {{ margin-top: auto; font-size: 13px; color: #9fb3cc; letter-spacing: .04em; }}
.cright {{ flex: 1; padding: 64px 60px; display: flex; flex-direction: column; justify-content: center; background: {BG}; }}
.cgrid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
.ctile {{ background: #fff; border: 1px solid {LINE}; border-radius: 16px; padding: 26px 26px 22px; }}
.cbig {{ font-size: 40px; font-weight: 700; color: {NAVY}; letter-spacing: -.02em; }}
.csub {{ font-size: 14px; color: {SLATE}; margin-top: 4px; line-height: 1.4; }}
.csplit {{ display: flex; gap: 4px; margin-top: 30px; border-radius: 12px; overflow: hidden; }}
.csplit div {{ color: #fff; font-size: 13px; font-weight: 700; padding: 16px 14px; white-space: nowrap; }}
.cnote {{ font-size: 13px; color: {SLATE}; margin-top: 12px; }}
/* funds */
.fcols {{ display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 26px; margin-top: 22px; }}
.ftot {{ font-size: 17px; font-weight: 700; margin-bottom: 12px; }}
.li {{ display: grid; grid-template-columns: 190px 1fr 56px; align-items: center; gap: 10px; font-size: 14px; padding: 9px 0; border-bottom: 1px solid {LINE}; }}
.li b {{ text-align: right; }}
.lbar {{ height: 9px; background: {BG}; border-radius: 5px; overflow: hidden; }}
.lbar i {{ display: block; height: 100%; border-radius: 5px; }}
.fnote {{ font-size: 13px; color: {SLATE}; margin-top: 10px; line-height: 1.45; }}
.rbox {{ background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 15px 17px; font-size: 14px; line-height: 1.45; margin-bottom: 10px; }}
/* product */
.phases {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
.ph-card {{ border: 1px solid {LINE}; border-radius: 14px; overflow: hidden; background: #fff; }}
.ph-top {{ color: #fff; padding: 14px 16px; display: flex; gap: 12px; align-items: center; }}
.ph-n {{ width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,.22); display: flex; align-items: center; justify-content: center; font-weight: 700; }}
.ph-h {{ font-size: 17px; font-weight: 700; }} .ph-m {{ font-size: 11.5px; opacity: .85; }}
.ph-card ul {{ list-style: none; margin: 0; padding: 12px 16px 14px; }}
.ph-card li {{ font-size: 14.5px; padding: 8px 0; display: flex; gap: 8px; line-height: 1.35; }}
.ph-card li i {{ font-style: normal; font-weight: 700; }}
/* flow */
.chips3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 10px; }}
.chip {{ background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 12px 16px; font-size: 13px; line-height: 1.4; }}
.chip b {{ display: block; color: {NAVY}; font-size: 14px; margin-bottom: 2px; }}
/* regulatory */
.rcols {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; }}
.rhead {{ color: #fff; font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; padding: 9px 14px; border-radius: 10px; margin-bottom: 9px; }}
.rcard {{ border-left: 4px solid; border-radius: 8px; padding: 8px 12px; margin-bottom: 7px; font-size: 12px; line-height: 1.35; }}
.rcard b {{ display: block; font-size: 13.5px; }} .rcard span {{ color: #334155; }}
.never {{ background: {RED_L}; border: 1px solid #fecdca; border-radius: 10px; padding: 10px 12px; margin-top: 12px; }}
.never b {{ color: {RED}; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; display: block; margin-bottom: 4px; }}
.nv {{ color: {RED}; font-weight: 600; font-size: 12.5px; padding: 3px 0; }}
/* team */
.team {{ display: grid; grid-template-columns: 1fr 1fr; gap: 26px; margin-bottom: 14px; }}
.fcard {{ background: {BG}; border: 1px solid {LINE}; border-radius: 14px; padding: 14px 18px 8px; }}
.fn {{ font-size: 20px; font-weight: 700; }} .ft {{ font-size: 13px; font-weight: 700; margin-bottom: 4px; }}
.fcard ul {{ margin: 4px 0 4px 18px; padding: 0; columns: 2; column-gap: 22px; }}
.fcard li {{ font-size: 12.5px; padding: 2px 0; line-height: 1.35; break-inside: avoid; }}
.rep {{ font-size: 11px; font-weight: 700; color: {SLATE}; letter-spacing: .1em; text-transform: uppercase; margin: 16px 0 8px; }}
.hcard {{ display: flex; justify-content: space-between; align-items: center; border: 1px solid {LINE}; border-radius: 10px; padding: 8px 12px; margin-bottom: 6px; background: #fff; }}
.hcard b {{ font-size: 13.5px; display: block; }} .hcard span {{ font-size: 12px; color: {SLATE}; }}
.hcard em {{ font-style: normal; color: #fff; font-size: 12px; font-weight: 700; border-radius: 999px; padding: 4px 10px; white-space: nowrap; }}
/* customers */
.gtm {{ display: grid; grid-template-columns: 712px 1fr; gap: 26px; }}
.kpis {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }}
.kpi {{ background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 14px 16px; }}
.kpi b {{ display: block; font-size: 28px; color: {NAVY}; letter-spacing: -.01em; }} .kpi span {{ font-size: 12.5px; color: {SLATE}; }}
/* milestones */
.gates {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
.gate {{ border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px; background: {BG}; }}
.gate span {{ display: inline-flex; width: 24px; height: 24px; border-radius: 50%; background: {NAVY}; color: #fff; font-size: 12px; font-weight: 700;
             align-items: center; justify-content: center; margin-bottom: 6px; }}
.gate b {{ display: block; font-size: 13.5px; }} .gate em {{ font-style: normal; font-size: 12px; color: {SLATE}; }}
/* assumptions */
.at {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
.at th {{ text-align: left; font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: {SLATE}; border-bottom: 2px solid {NAVY}; padding: 6px 10px; }}
.at td {{ padding: 6.5px 10px; border-bottom: 1px solid {LINE}; }}
.at td:first-child {{ font-weight: 600; width: 26%; }} .at td:last-child {{ color: #475569; }}
"""


def build():
    pages = [cover(), p_funds(), p_product(), p_flow(), p_reg(), p_team(), p_customers(), p_milestones(), p_assume()]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Seed plan</title><style>{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')
    out = HERE / "Seed_Plan_investor.html"
    out.write_text(html)
    pdf = HERE / "Seed_Plan_investor.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, capture_output=True)
    for old in ("Seed_plan.pdf", "Seed_plan.html", "Save91_Seed_Plan.pdf", "Save91_Seed_Plan.html"):
        (HERE / old).unlink(missing_ok=True)
    print("wrote", pdf)


if __name__ == "__main__":
    build()

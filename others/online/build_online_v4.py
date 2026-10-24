"""Online_model_v4: the online-first plan deck (story + appendix). First built 21 Oct 2026 (operator: "remodel the excel sheet and
everything and check all inputs ... then the offline_v3 to turn it into online_v4 where 90% online and 10% offline").

REBASE 24 Oct (reviews/2026-10-24_rebase/BRIEF.md): the founders questioned every LTV input and fixed most of them at today's market
or a measured number (model/online_plan.py, "REBASE 24 Oct"). One case: the main case, the median of the LTV/CAC Monte Carlo
(model/ltv_odds.py; two inputs still drawn: still saving at 12 months, the debt fund's fee). The ladder and the levers say "what it
takes"; they are never alternative plans, and our old loan targets appear only as the upside end of the ladder.
Story (one point a page; every number read from the tables): the answer first (cross-sell alone in rupees and as a share of the
cost to win, before serving; LTV/CAC at 5 and 8 years net of serving; payback; the company not profitable by year 8; the two inputs
still to confirm in writing); the customer, product and money flow; one saver; the loan funnel; the odds; what it takes; the
financials; the four facts; what loans would have to bring; the seed. FIXES.md (24 Oct, sections A and B) applied. Appendix: inputs (fixed 24 Oct / drawn / unconfirmed), the
agreed product inputs, costs, seed budget, regulation, the main case and the "All upside" rung year by year, the Monte Carlo
tables, every lever, the input audit, the sheet check, the 24 Oct bridge with the decision list, the $1B test, and sources.

Numbers are read from tables/ (ltv_*.csv from model/ltv_odds.py, online_*.csv from model/online_plan.py under use_main_case(),
v4_toy_check.csv from model/v4_toy_check.py, research/*.csv), never retyped. Pages reuse online/build_online_case.py (bc),
ltv/odds_pages.py (od), ltv/build_ltv_deck.py (ld, via bc) and seed/build_seed_plan.py (sp); those belong to other builders, so
anything different is a local helper here. Builds online/Online_model_v4.html/.pdf (Chrome headless)."""
import csv
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "seed"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "model"))
import build_seed_plan as sp  # noqa: E402
import build_online_case as bc  # noqa: E402
import odds_pages as od  # noqa: E402  (on the path through build_online_case)

ld, lo, op = bc.ld, od.lo, od.op

TAB = ROOT / "tables"
INK, NAVY, TEAL, BLUE, AMBER, SLATE, MUTE, LINE, BG, RED = sp.INK, sp.NAVY, sp.TEAL, sp.BLUE, sp.AMBER, sp.SLATE, sp.MUTE, sp.LINE, sp.BG, sp.RED
NAVY2, NAVY3, NAVY4, LATE = sp.NAVY2, sp.NAVY3, sp.NAVY4, bc.LATE
T, R, A, svg, halo = sp.T, sp.R, sp.A, sp.svg, od.halo
x, usd, month, rs, cr, crn = od.x, od.usd, od.month, od.rs, od.cr, od.crn
FOOT = "Online model v4 · October 2026 · Confidential"

DIST = pd.read_csv(TAB / "dist_agreed_v1.csv").set_index("key")
DIST["name"] = DIST["name"].str.replace("his shop or home", "the saver's shop or home", regex=False)  # agreed file predates the neutral wording
AUDIT = TAB / "online_inputs_audit.csv"
SHEETCHK = TAB / "v4_toy_check.csv"
S5, S8, MAIN, CAC, X = od.S5, od.S8, od.MAIN, od.CAC, od.X
LEVEL = lo.LEVEL

# ---------------------------------------------------------------- page order (numbers for cross-references)
STORY = ["cover", "customer", "product", "flow", "unit", "funnel", "odds", "ladder", "financials", "prove", "fee", "seed"]
APPX = [("inputs", "Inputs: fixed on 24 Oct, drawn, or still unconfirmed"), ("product_in", "Agreed product inputs"), ("costs", "Costs and team"),
        ("seedbudget", "The seed budget"), ("reg", "Regulatory path"), ("year_main", "The main case, year by year"),
        ("year_top", "What it takes, the top rung, year by year (not a plan)"), ("mc", "The Monte Carlo: tables"),
        ("levers", "Every assumption tested around the main case"), ("audit", "Input audit"), ("sheet", "Spreadsheet check"),
        ("changes", "What changed on 24 Oct: the bridge and the decisions"), ("upside", "The upside: the $1B test, on the main case"),
        ("capture", "The upside: capturing 10 crore savers, year by year"), ("sources", "Loan and cross-sell sources"),
        ("debit_src", "Debit route and daily minimum sources")]
PN = {k: i + 1 for i, k in enumerate(STORY)}
PN["divider"] = len(STORY) + 1
PN.update({k: PN["divider"] + 1 + i for i, (k, _t) in enumerate(APPX)})
AN = {k: f"A{i + 1}" for i, (k, _t) in enumerate(APPX)}


def ref(k):
    """'A12, page 25' for an appendix page; 'page 8' for a story page."""
    return f"{AN[k]}, page {PN[k]}" if k in AN else f"page {PN[k]}"


def page(n, section, kicker, title, body, src=""):
    s = f'<div class="src">{src}</div>' if src else ""
    return f"""<section class="page">
<header class="ph"><span class="brand">{sp.NAME} <em>· working name</em></span><span>{section}</span></header>
<div class="kicker">{kicker}</div><h1>{title}</h1>
<div class="body">{body}</div>{s}
<footer class="pf"><span>{FOOT}</span><span>{n}</span></footer>
</section>"""


def repage(html, n, section=None, kicker=None):
    """Re-number a page built by another builder and give it this deck's footer (and, optionally, section and kicker prefix)."""
    html = re.sub(r'<footer class="pf"><span>[^<]*</span><span>[^<]*</span></footer>', f'<footer class="pf"><span>{FOOT}</span><span>{n}</span></footer>', html)
    if section:
        html = re.sub(r'(<header class="ph">.*?</span><span>)[^<]*(</span></header>)', rf"\g<1>{section}\2", html, count=1, flags=re.S)
    if kicker:
        html = html.replace('<div class="kicker">', f'<div class="kicker">{kicker} · ', 1)
    return html


def table(head, rows, widths=None, size=12, compact=False, cls=""):
    cg = "".join(f'<col style="width:{w}%">' for w in widths) if widths else ""
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    c = ("at compact" if compact else "at") + (f" {cls}" if cls else "")
    return f'<table class="{c}" style="font-size:{size}px"><colgroup>{cg}</colgroup><tr>{th}</tr>{tr}</table>'


def rupee(s):
    s = re.sub(r"\bRs (?=[a-z])", "₹ ", str(s))
    return re.sub(r"Rs ?(?=\d)", "₹", s).replace("Rs ", "₹").replace("(Rs)", "(₹)").replace("Rs,", "₹,")


def num(v, pct=False):
    v = float(v)
    if pct:
        return f"{v * 100:.2f}".rstrip("0").rstrip(".") + "%"
    if abs(v) >= 1000:
        return ind(v)
    return f"{v:g}"


def ind(v):
    """2,05,000 grouping (Indian), for whole numbers."""
    n = f"{abs(v):.0f}"
    head, tail = n[:-3], n[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    return ("−" if v < 0 else "") + (head + "," + tail if head else tail)


def indf(v, d):
    """Indian grouping with d decimals and a true minus: 142150.1 -> 1,42,150.1."""
    v = float(v)
    s = f"{abs(v):.{d}f}"
    whole, _, frac = s.partition(".")
    out = ind(float(whole)) + (f".{frac}" if d else "")
    return ("−" if v < -0.5 * 10 ** -d else "") + out


def clip(s, n):
    s = str(s)
    return s if len(s) <= n else s[:s.rfind(" ", 0, n)] + "…"


def pill(txt, col, bg):
    return (f'<span style="display:inline-block;background:{bg};color:{col};border-radius:999px;padding:1px 8px;font-weight:700;'
            f'font-size:10px;white-space:nowrap;margin:1px 3px 1px 0">{txt}</span>')


FIXED, DRAWN, UNCONF, OTHER = (NAVY, sp.NAVY_L), (TEAL, sp.TEAL_L), (AMBER, sp.AMBER_L), (SLATE, "#f1f5f9")


# ---------------------------------------------------------------- story
def by(m):
    """'month 64', or 'after month 96' for the 97 that means not by month 96."""
    m = int(float(m))
    return f"month {m}" if m <= 96 else "after month 96"


def need(r):
    """Money needed with '+' (at least) when EBITDA is still negative at month 96 (a ladder row)."""
    return od.floor_usd(r)


def levneed(case):
    """The same for a one-change-at-a-time row of the company (ltv_main_levers.csv)."""
    pm, m = od.levm(case)
    return usd(m) + ("" if pm else "+")


def cover():
    p10, p90 = od.q("Saver pays back in month (97 = not by 96)", "P10"), od.q("Saver pays back in month (97 = not by 96)", "P90")
    tiles = [(f"{rs(S5['cross-sell'])} cross-sell", f"loans and cards alone, per saver in 5 years ({rs(S8['cross-sell'])} in 8): {x(S5['cross-sell / CAC'])} and "
                                                    f"{x(S8['cross-sell / CAC'])} of the {rs(CAC)} to win a saver, before serving; less than the {rs(S5['serving'])} / "
                                                    f"{rs(S8['serving'])} to serve them, so alone it never pays back ({x(S5['cross-sell net of serving / CAC'])} after serving)"),
             (f"{od.XMED} LTV/CAC", f"with fund fees, net of serving: one online saver brings back {od.XMED} of its {rs(CAC)} cost in 5 years and {od.XMED8} in 8"),
             (f"Month {od.PAY}", f"when the saver pays back; 8 in 10 of 1,000 runs of the model (retention and the debt fund's fee picked at random in their "
                                 f"ranges) fall between {by(p10)} and {by(p90)}"),
             ("Not by year 8" if bc.no_profit(MAIN) else month(MAIN["EBITDA positive from month"]).capitalize(),
              f"for the company's EBITDA (operating profit before interest, tax and depreciation) to turn positive at {LEVEL:,} online savers a month; "
              f"it needs {need(MAIN)}, as the cash hole is still deepening at month 96")]
    t = "".join(f'<div class="ctile" style="padding:18px 22px 16px"><div class="cbig" style="font-size:29px">{a}</div><div class="csub" style="font-size:12.5px">{b}</div></div>'
                for a, b in tiles)
    r2 = od.R2
    three = (f"3× needs {float(od.LAD.loc['3×', 'upside position (0 main case, 1 all upside)']):.0%} of the way on every upside lever"
             if "3×" in od.LAD.index else "3× is out of reach on these levers")
    deb, fee = od.ltvl("We pay Rs 2 a debit, weekly"), od.ltvl("Equity fund fee 0.5%, not 0.75%")
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:50px">Daily saving, online first</div>
  <div class="ctag">For India's self-employed: ₹100 a day by UPI into mutual funds in the saver's own name; the app never holds money. 9 in 10 savers
  online, 1 in 10 at the doorstep. Business model v4, on the founders' 24 October inputs.</div>
  <div class="cmeta">October 2026 · Confidential · Piyush (CEO) and Sandeep (CPTO)</div>
</div>
<div class="cright" style="padding:44px 52px"><div class="cgrid" style="gap:14px">{t}</div>
<div class="cnote" style="margin-top:16px;font-size:12.5px;line-height:1.45"><b style="color:{NAVY}">At market numbers this is a fund-fee business; loans are a small
add-on.</b> LTV/CAC = what a saver brings in over 5 or 8 years, less the cost of serving them, divided by what it costs to win them: {rs(op.CAC)} at scale (the
founders' figure) plus our 10% contingency = {rs(CAC)}.</div>
<div class="cnote" style="margin-top:8px;font-size:12.5px;line-height:1.45"><b style="color:{AMBER}">Still to confirm in writing:</b> the main case assumes debits cost us
₹0 and a {od.pct(op.EQ_TRAIL, 2)} equity fund fee; ₹2 a weekly debit, or a 0.5% fee, would cut a saver to about {x(deb)} or {x(fee)}.</div>
<div class="cnote" style="margin-top:8px;font-size:12.5px;line-height:1.45"><b style="color:{NAVY}">What it takes</b> ({ref('ladder')}): 2× needs
₹{float(r2['saved a day Rs']):.0f} a day, {float(r2['still saving at 12 months']):.0%} still saving and loans most of the way to our old targets, for profit from
{month(r2['EBITDA positive from month'])} on {need(r2)}; {three}. Four facts decide most of it, all cheap to get ({ref('prove')}). What changed on 24 October:
{ref('changes')}.</div></div>
</section>"""


def p_customer(n):
    probs = [("Sold on “believe me”", "An investment person they know picks the product. Nothing is written down.", "A written rule they can see: why this fund, in one sentence."),
             ("Can't start small alone", "A small instalment happens today because someone comes to collect it.", "₹100 a day by UPI Autopay, set up in minutes; an agent for 1 in 10."),
             ("Forgotten after joining", "Nobody comes back to ask what else the saver needs.", "Streaks, nudges and an AI money coach in the app."),
             ("Saves a little, then stops", "Some keep saving; many drop off.", "Saving improves the offer: the longer the streak, the better the loan limit and rate (our proposal).")]
    cards = "".join(f"""<div class="ph-card"><div class="ph-top" style="background:{NAVY if i % 2 == 0 else NAVY2}"><span class="ph-n">{i + 1}</span>
<div><div class="ph-h">{a}</div></div></div><ul><li><i style="color:{RED}">✕</i>{b}</li><li><i style="color:{TEAL}">✓</i>{c}</li></ul></div>"""
                    for i, (a, b, c) in enumerate(probs))
    body = f"""<div class="phases">{cards}</div>
<div class="rbox" style="margin-top:20px;font-size:15px"><b>What savers think the product is:</b> a wallet they save into and then borrow from,
an overdraft-like line. Our answer keeps the money in funds in the saver's own name (the app never holds it) and lets saving improve the loan offer.</div>"""
    return page(n, "The customer", "THE SAVER'S PROBLEM, NOT OURS", "Anyone can sign up savers; a product built for how they save and borrow is still missing, and the market is big enough for more than one winner",
                body, "Sources: practitioner conversations, 17–18 Oct 2026 (customer problem notes; the wallet reading is the founders' own).")


def channel_bar():
    W = 1152
    s = [T(0, 14, "WHERE SAVERS COME FROM", 11.5, 700, SLATE, ls=1.1)]
    s.append(R(0, 26, W * 0.9 - 4, 56, TEAL, r=10))
    s.append(T(18, 52, "ONLINE · 90% OF SAVERS", 13, 800, "#fff", ls=1))
    s.append(T(18, 72, f"app, referrals and ads. Cost to win a saver (marketing + KYC, the identity check): {rs(op.CAC)} at scale (the founders' figure), "
                       f"{rs(op.SEED_CAC)} budgeted in the seed; + our 10% contingency", 12, 500, "#fff"))
    s.append(R(W * 0.9, 26, W * 0.1, 56, AMBER, r=10))
    s.append("".join(T(W * 0.95, 50 + i * 16.2, t, 12, 800, "#fff", "middle") for i, t in enumerate(["DOORSTEP", "10%"])))
    return svg(W, 90, "".join(s))


def p_product(n):
    cards = "".join(f"""<div class="ph-card"><div class="ph-top" style="background:{col}"><span class="ph-n">{k}</span><div><div class="ph-h">{h}</div>
<div class="ph-m">{m}</div></div></div><ul>{''.join(f'<li><i style="color:{col}">✓</i>{f}</li>' for f in feats)}</ul></div>""" for k, h, m, col, feats in sp.PHASES)
    body = f'<div class="phases">{cards}</div><div style="margin-top:16px">{channel_bar()}</div>'
    return page(n, "Product and channel", "WHAT WE BUILD", "Four releases in 18 months; 9 in 10 savers come online, 1 in 10 through a doorstep agent",
                body, f"Doorstep agents sign savers up and set the UPI mandate; they never handle cash. The pilot runs in NCR with {int(sp.P.agents)} agents; online is pan-India.")


def flow_v4():
    """The money flow on the 24 Oct route: the saver's bank -> the exchange (BSE StAR MF) or the fund house's own mandate -> the fund
    (likely one hybrid fund at Rs 100 a day) -> units in the saver's name. sp.flow() draws the exchange route only."""
    s = []
    nodes = [(0, 150, 190, "Saver's own", "bank account", BLUE, sp.BLUE_L),
             (290, 150, 254, "Exchange or fund house", "BSE StAR MF, or its own mandate", TEAL, sp.TEAL_L),
             (640, 150, 200, "The fund", "likely one hybrid fund", TEAL, sp.TEAL_L),
             (940, 150, 200, "Units held", "in the saver's name", TEAL, sp.TEAL_L)]
    for x0, y, w, a, b, col, bg in nodes:
        s.append(R(x0, y, w, 76, bg, col, 14, 1.8))
        s.append(T(x0 + w / 2, y + 34, a, 16, 700, col, "middle"))
        s.append(T(x0 + w / 2, y + 56, b, 13, 500, INK, "middle"))
    s.append(A(194, 188, 286, 188, TEAL, 2.6))
    s.append(T(240, 178, "₹100 a day", 12, 700, TEAL, "middle"))
    s.append(T(240, 206, "UPI Autopay", 11, 600, TEAL, "middle"))
    s.append(A(548, 188, 636, 188, TEAL, 2.6))
    s.append(A(844, 188, 936, 188, TEAL, 2.6))
    s.append(T(417, 246, "₹0 a debit to us (to confirm in writing)", 11.5, 700, TEAL, "middle"))
    # the app
    s.append(R(330, 18, 360, 74, NAVY, r=14))
    s.append(T(510, 50, "Our app · registered distributor", 16, 700, "#fff", "middle"))
    s.append(T(510, 74, "KYC, orders, dashboard, offers", 13, 500, "#c9d6e6", "middle"))
    s.append(A(417, 94, 417, 146, NAVY, 2.2, dash=True))
    s.append(T(427, 126, "sends orders", 12, 700, NAVY))
    s.append(A(740, 146, 690, 96, NAVY, 2.2))
    s.append(T(752, 112, "fund fee from the fund house:", 12, 700, NAVY))
    s.append(T(752, 128, f"{od.pct(op.EQ_TRAIL, 2)} a year on equity, less on debt (to confirm)", 12, 500, NAVY))
    # withdraw loop
    s.append(f'<path d="M740 228 L740 276 L95 276 L95 238" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    s.append(f'<polygon points="95,228 89,241 101,241" fill="{BLUE}"/>')
    s.append(T(418, 268, "withdraw any day: back in 1–3 working days (exit fees may apply in year 1)", 12.5, 700, BLUE, "middle"))
    # lender
    s.append(R(640, 306, 200, 64, "#f1f5f9", SLATE, 14, 1.8))
    s.append(T(740, 334, "Partner lender", 15, 700, SLATE, "middle"))
    s.append(T(740, 354, "bank or NBFC", 12.5, 500, INK, "middle"))
    s.append(f'<path d="M640 338 L48 338 L48 238" fill="none" stroke="{SLATE}" stroke-width="2.4"/>')
    s.append(f'<polygon points="48,228 42,241 54,241" fill="{SLATE}"/>')
    s.append(T(344, 330, "loan paid straight to the saver's bank; the saver repays the lender", 12.5, 700, SLATE, "middle"))
    s.append(T(856, 344, "pays us a referral fee", 12.5, 700, SLATE))
    # doorstep
    s.append(R(0, 18, 250, 74, sp.AMBER_L, AMBER, 14, 1.6, dash=True))
    s.append(T(125, 48, "Doorstep agent (pilot)", 15, 700, AMBER, "middle"))
    s.append(T(125, 70, "signs savers up, sets the mandate", 12, 500, INK, "middle"))
    s.append(A(95, 94, 95, 146, AMBER, 2, dash=True))
    return svg(1152, 380, "".join(s))


def p_flow(n):
    chips = [("In the saver's name, never through us", "Units sit with the fund house, registered to the saver. The app never holds anyone's money."),
             ("One hybrid fund at ₹100 a day", f"Daily minimums are about ₹100 a scheme, so ₹80 equity + ₹20 debt likely becomes one hybrid fund. The model's "
                                              f"80/20 blend earns us {od.pct(od.FEE_MAIN, 2)} a year, so that fund's fee must be about {od.pct(od.FEE_MAIN, 2)} or more."),
             ("Paid by partners", "Fund houses and lenders pay us; the saver pays us nothing. A regular plan costs the saver about 0.5–1% a year more than a "
                                  "direct plan; we say so up front.")]
    c = "".join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in chips)
    return page(n, "How it works", "THE MONEY FLOW", "Money goes from the saver's bank to a fund in their name, never through us",
                f'<div style="width:90%;margin:-6px auto 0">{flow_v4()}</div><div class="chips3" style="margin-top:4px">{c}</div>',
                f"UPI Autopay mandate: a standing debit the saver approves once. SIP: a standing order to invest on a schedule. SEBI: payments come from the "
                f"investor's own account. BSE StAR MF's exchange SIP is free to distributors (fund houses pay BSE); ₹0 a debit to us is not yet in writing "
                f"({ref('debit_src')}). NBFC = non-bank lender.")


def p_unit(n):
    return repage(bc.p_main_saver(n), n, "One saver")


FUNNEL_LABELS = {"sign-ups": "Sign-ups", "KYC'd users who see loan offers": "Their loan value, in savers' worth",
                 "still reachable at month 12": "Loan value left at month 12",
                 "personal + business loan applications, 5 years": "Personal + business applications (5 years)",
                 "personal + business loans (first + repeat), 5 years": "Personal + business loans (5 years)"}
KYCD = 100 * op.SIGNUPS_PER_SAVER * op.KYC_SHARE          # KYC'd people per 100 online savers won (half of the 5 sign-ups a saver)


def funnel_bars(F):
    W, x0, step = 600, 250, 33
    st = F[~F["stage"].str.startswith("type:")].reset_index(drop=True)
    assert list(st["stage"]) == list(FUNNEL_LABELS), list(st["stage"])
    rows = [(FUNNEL_LABELS[st["stage"][0]], float(st["per 100 savers won"][0])), ("KYC'd people who see offers", KYCD)]
    rows += [(FUNNEL_LABELS[k], float(v)) for k, v in zip(st["stage"][1:], st["per 100 savers won"][1:])]
    mx = max(v for _l, v in rows)
    cols = [SLATE, MUTE, NAVY, NAVY2, NAVY4, TEAL]
    s = [T(0, 14, "PER 100 ONLINE SAVERS WON", 11.5, 700, SLATE, ls=1.1)]
    for i, (lab, v) in enumerate(rows):
        y = 26 + i * step
        w = (W - x0 - 60) * v / mx
        s.append(T(0, y + 16, lab, 12, 600))
        s.append(R(x0, y + 2, max(w, 2), 21, cols[i], r=5))
        s.append(T(x0 + max(w, 2) + 8, y + 18, f"{v:,.0f}" if v >= 10 else f"{v:.1f}", 13.5, 800, cols[i]))
    return svg(W, 26 + len(rows) * step, "".join(s))


def p_loan_funnel(n):
    F = pd.read_csv(TAB / "ltv_main_funnel.csv")
    ty = F[F["stage"].str.startswith("type:")].copy()
    ty["stage"] = ty["stage"].str.replace("type: ", "", regex=False).str.replace("Personal + business", "Personal + business (with top-ups)", regex=False)
    tot = float(ty["our fees Rs per saver won"].sum())
    lent = float(ty["lent Rs per 100 savers won"].sum())
    nloans = float(ty["per 100 savers won"].sum())
    users = float(F.loc[F["stage"] == "KYC'd users who see loan offers", "per 100 savers won"].iloc[0])
    assert abs(users / 100 - op.LOAN_REACH) < 0.005 and abs(tot - float(S5["Loans (all referrals)"])) < 1, (users, tot, S5["Loans (all referrals)"])
    rows = [[r["stage"], f"{r['per 100 savers won']:.1f}", f"₹{ind(r['average loan Rs'])}", f"{r['payout at the start'] * 100:g}%", f"₹{r['our fees Rs per saver won']:,.0f}"]
            for _, r in ty.iterrows()]
    rows.append(["<b>All loans</b>", f"<b>{nloans:.0f}</b>", "", "", f"<b>₹{tot:,.0f}</b>"])
    tbl = table(["Loan type", "Loans per 100 savers won, 5 years", "Average loan", "Lender payout", "Our fees a saver won"], rows, [34, 19, 17, 13, 17], 12, compact=True)
    first = op.LOAN_APPLY * float(X["approved_first"])
    nonsave = KYCD - 100
    cd = float(ty.loc[ty["stage"] == "Consumer durable", "average loan Rs"].iloc[0])
    pm, money = od.levm("Loan funnel at our old targets")
    body = f"""<div style="display:flex;gap:26px;align-items:flex-start"><div style="flex:0 0 600px">{funnel_bars(F)}</div><div style="flex:1">{tbl}</div></div>
<div class="chips3" style="margin-top:6px">
<div class="chip"><b>About {KYCD / 100:g} KYC'd people a saver, worth {op.LOAN_REACH:.2f}</b>5 sign-ups a saver, half finish KYC (the identity check). The {nonsave / 100:g} who
never save fade within about 3 months, before lenders approve most new users: together worth {op.LOAN_REACH - 1:.2f} of a saver, a weight, not a head count.</div>
<div class="chip"><b>{od.val('apply')} apply a year, {od.val('approved')} approved</b>Today's market, no yearly rises: the founders' figure, between 11% (an app lender's new
applicants) and 25% (our past data). Repeats {od.val('repeat')}, gold {od.pct(op.GOLD_APPROVAL)}, home and property {od.pct(X['loan_home_approval'])}.</div>
<div class="chip"><b>{od.lakh(X['ticket'])} first loans, a {od.pct(X['fee'])} payout</b>As the lender's referral partner we earn {od.pct(X['fee'])} of each personal or business
loan, flat (the middle of the market's 1–3%), and 0.5–1% on gold, property and home loans. Repeats are {od.pct(X['ticket_growth'])} bigger a year.</div></div>
<div class="rbox" style="margin-top:8px;padding:8px 14px;font-size:12.5px"><b>What cross-selling can do:</b> all three loan numbers at our old targets together (applying
35%, approval 30%, yearly rises) give {x(od.ltvl('Loan funnel at our old targets'))} and profit from {month(pm) if pm else 'not by month 96'} on {usd(money)}
({ref('levers')}). Loan fees arrive early; fund fees build slowly with the balance.</div>"""
    assert abs(X["loan_home_approval"] - X["loan_lap_approval"]) < 1e-9
    title = (f"Of 100 online savers won, {nloans:.0f} loans worth ₹{lent / 1e5:,.0f} lakh follow in five years, earning us ₹{tot:,.0f} a saver; the "
             f"{nonsave:.0f} KYC'd sign-ups who never save add only {users - 100:.0f} savers' worth")
    return page(n, "Loans", "THE LOAN FUNNEL, MAIN CASE", title, body,
                f"Main case: the founders' 24 October market inputs. Top-ups: {od.pct(X['topup_share'])} a year at {od.pct(X['topup_size'])} of the loan. "
                f"Applications: 70% personal or business, 15% gold, 3% property, 2% home; durable ({od.lakh(cd)}) and two-wheeler loans go to savers only, outside "
                f"the funnel. Not counted: loans against savings (10% of applications). About 1 in {round(1 / first)} reachable users gets a first loan a year. "
                f"Benchmarks: {ref('sources')}.")


def p_odds(n):
    return page(n, "The odds", *od.p_odds())


def ladder_local():
    """The ladder page with its words read from tables/ltv_ladder.csv (od.ladder_svg() draws every rung the table has). Used when
    od.p_ladder()'s words disagree with the table (24 Oct: the rerun added a reachable 3x rung while odds_pages still said "out of reach")."""
    R1, R2, TOP, L3 = od.R1, od.R2, od.TOP, od.LAD.loc["3×"] if "3×" in od.LAD.index else None
    up = lambda r: float(r["upside position (0 main case, 1 all upside)"])
    pm, money = od.levm("Loan funnel at our old targets")
    loans_old = od.ltvl("Loan funnel at our old targets")
    three = (f"3× needs {up(L3):.0%} of the way on every lever: ₹{float(L3['saved a day Rs']):.0f} a day, {float(L3['still saving at 12 months']):.0%} still "
             f"saving, {float(L3['apply a year']):.0%} applying, {float(L3['first loans approved']):.0%} approved; profit from {month(L3['EBITDA positive from month'])} "
             f"on {need(L3)}." if L3 is not None else
             f"Even with every lever at its upside a saver returns {x(TOP['LTV/CAC 5y'])}: 3× is out of reach on these levers.")
    body = od.ladder_svg() + od.chips([
        ("One company, one main case", f"Every row is the same company: {LEVEL:,} online savers a month from month 30, the same team and cost to win. "
                                       "The rows say what would have to be true, not a second plan."),
        ("Five levers move together", f"From the main case to the upside: ₹{float(MAIN['saved a day Rs']):.0f} → ₹{float(TOP['saved a day Rs']):.0f} a day, "
                                      f"still saving → {float(TOP['still saving at 12 months']):.0%}, applying {float(MAIN['apply a year']):.0%} → "
                                      f"{float(TOP['apply a year']):.0%}, approval {float(MAIN['first loans approved']):.0%} → {float(TOP['first loans approved']):.0%}, "
                                      f"yearly rises none → {od.rises(TOP)}. 1× is {up(R1):.0%} of the way; 2× is {up(R2):.0%}. {three}"),
        ("No loan number gets there alone", f"All three loan numbers at our old targets together (applying 35%, approval 30%, yearly rises) give "
                                            f"{x(loans_old)} and profit from {month(pm) if pm else 'not by month 96'} on {usd(money)} ({ref('levers')}): loan "
                                            "fees arrive early, fund fees build slowly. The daily amount and how long savers keep saving do the most.")])
    tail = (f"3× needs nearly every upside lever ({up(L3):.0%} of the way)" if L3 is not None else "3× is out of reach")
    title = (f"What it takes: 2× needs ₹{float(R2['saved a day Rs']):.0f} a day, {float(R2['still saving at 12 months']):.0%} still saving and loans most of "
             f"the way to our old targets, for profit from {month(R2['EBITDA positive from month'])} on {need(R2)}; {tail}")
    src = ("Teal: a lever above the main case. Low and high end: still saving at 30% and 40% (the drop-off after a year on the same line), every other "
           "input at the main case. EBITDA: operating profit before interest, tax and depreciation. Money needed: the seed plus the deepest cash hole plus "
           "a ₹5 crore cash buffer, at ₹95 = $1; + means the hole is still deepening at month 96, so it is at least that. Doorstep savers (1 in 10) carry "
           "the same levers. Undiscounted.")
    return "WHAT IT TAKES: THE COMPANY AT EACH LTV/CAC", title, body, src


def p_ladder(n):
    k, title, body, src = od.p_ladder()
    text = re.sub(r"<[^>]+>", " ", title + body)
    if ("3×" in od.LAD.index) == ("out of reach" in text):        # the shared page's words disagree with the table
        k, title, body, src = ladder_local()
    return page(n, "What it takes", k, title, body, src)


def p_financials(n):
    return page(n, "The financials", *od.p_financials())


def p_prove(n):
    return page(n, "What decides it", *od.p_prove())


SHARED_WORDS = [   # FIXES B2 (24 Oct) wording, applied here only while a shared page still uses the old words
    ("The cost to win is measured and", "The cost to win is the founders' figure (held fixed), and")]


def shared_words(h):
    for a, b in SHARED_WORDS:
        h = h.replace(a, b)
    return h


def p_fee(n):
    title, body, src = ld.fee_test()
    return page(n, "What has to be true", "WHAT LOANS WOULD HAVE TO BRING", shared_words(title), shared_words(body), shared_words(src))


def p_seed(n):
    return repage(bc.p_seed_main(n), n, "What the seed proves")


# ---------------------------------------------------------------- appendix
def divider(n):
    items = " · ".join(f"<b>{AN[k]}</b> {t} (p{PN[k]})" for k, t in APPX)
    return page(n, "Appendix", "APPENDIX", "Inputs, year-by-year tables, the Monte Carlo and the checks behind every number",
                f'<div class="rbox" style="font-size:15px;line-height:1.9">{items}</div>'
                '<div class="rbox" style="font-size:13.5px;line-height:1.5;margin-top:14px"><b>One case.</b> Every page is the main case: the founders\' '
                '24 October inputs, with the two still-uncertain inputs at the median of 1,000 runs of the model. The ladder, the levers and the upside say what would '
                'have to be true; none of them is a second plan.</div>')


def a_inputs(n):
    d = lo.drawn(lo.at(od.T_MAIN))
    dl, dh = lo.drawn(lo.at(0.0)), lo.drawn(lo.at(1.0))
    F, D_, U, M_ = (lambda t: pill(t, *FIXED)), (lambda t: pill(t, *DRAWN)), (lambda t: pill(t, *UNCONF)), (lambda t: pill(t, *OTHER))
    fx = F("Fixed 24 Oct")
    c600 = od.LTVL.loc["Cost to win Rs 600 (our funnel)"]
    cd = float(pd.read_csv(TAB / "ltv_main_funnel.csv").set_index("stage").loc["type: Consumer durable", "average loan Rs"])
    rows = [
        ("Saved a day", f"₹{X['daily']:.0f} a day, ~{X['days']:.0f} debit days a month; +{od.pct(X['amount_growth'])} each year saved", fx,
         "Our product's floor. Bachatt's average is unknown; its minimums are lower (₹51 / ₹101 a day; ₹20, liquid fund)"),
        ("Still saving", f"{od.val('keep')} ({od.pct(X['r3'])} at month 3)", D_(f"Drawn {dl['r12']:.0%}–{dh['r12']:.0%}"),
         f"Bachatt's 30–40%; drop-off on one line ({dl['churn_late']:.1%} at {dl['r12']:.0%}, {dh['churn_late']:.1%} at {dh['r12']:.0%}, {op.churn_for(0.45):.1%} "
         "at 45%); SBI MF's ₹250 daily SIP ~38%"),
        ("Equity fund fee", f"{od.pct(op.EQ_TRAIL, 2)} a year on the 80% in equity (returns 10% a year)", U("Unconfirmed"), "Active equity funds; not yet in writing"),
        ("Debt fund fee", f"{od.val('trail')} on the 20% in debt (returns 7%): {od.pct(od.FEE_MAIN, 2)} blended", D_(f"Drawn {od.pct(dl['_debt_trail'], 2)}–{od.pct(dh['_debt_trail'], 2)}"),
         f"Liquid 0.10% to short-duration 0.35%; a hybrid fund at ₹100 a day must pay ~{od.pct(od.FEE_MAIN, 2)}+"),
        ("Each daily debit, to us", od.val("debit"), fx + U("Unconfirmed"), "BSE StAR MF's exchange SIP (free to distributors) or the fund house's mandate"),
        ("First personal / business loan", f"{od.lakh(X['ticket'])}; repeats {od.pct(X['ticket_growth'])} bigger a year; top-ups {od.pct(X['topup_share'])} a year at "
                                           f"{od.pct(X['topup_size'])}", fx, "Bachatt's number; our own research had ₹15k–58.5k"),
        ("Apply for a loan, a year", f"{od.val('apply')} of the users we can reach; no yearly rises", fx, "Today's market; no source for rises, so none"),
        ("Loans approved", f"{od.val('approved')} of first applications, {od.val('repeat')} of repeats; gold {od.pct(op.GOLD_APPROVAL)}, home and property "
                           f"{od.pct(X['loan_home_approval'])}", fx, "Founders' market figure: between 11% (an app lender's new applicants) and 25% (our past data)"),
        ("Home / property loan", od.val("home_lap"), fx, "Market: affordable home loans ₹6–15 lakh; small property loans ~₹3.9 lakh"),
        ("Lender payout", f"{od.val('payout')} on personal and business loans; 0.5–1% on gold, property, home", fx, "The middle of the market's 1–3%"),
        ("KYC'd non-savers", f"about {op.SIGNUPS_PER_SAVER * op.KYC_SHARE - 1:g} a saver, fading within ~3 months: worth {op.LOAN_REACH - 1:.2f} of a saver "
                             f"({op.LOAN_REACH:.2f} in all)", fx, "Lenders rarely approve a user in their first months"),
        ("Cards; small loans", f"{od.pct(X['card_share'])} of savers still saving at month 7 take a card (₹{X['card_fee']:,.0f}): {rs(S5['Cards'])} a saver won; "
                               f"durable ({od.lakh(cd)}) and two-wheeler loans, savers only", M_("Agreed"), "Card issuers; lender data"),
        ("Not counted", "recharge, bills, FD, NPS (not in the launch app); insurance; loans against savings; fund fees stop when a saver withdraws",
         fx, "Founders, 24 Oct; insurance's fixed fee not yet agreed"),
        ("Cost to win a saver", f"{rs(op.CAC)} at scale + 10% = {rs(CAC)}; the seed budgets {rs(op.SEED_CAC)} and measures it (at {rs(op.SEED_CAC)}: "
                                f"{x(od.ltvl('Cost to win Rs 600 (our funnel)'))} / {x(c600['LTV/CAC 96m'])}, {levneed('Cost to win Rs 600 (our funnel)')} needed)",
         M_("Founders' figure"), "“Fairly sorted”, the founders say; held fixed in the Monte Carlo"),
        ("Serving", f"₹{X['support_cost']:.0f} support a month per saver still saving; ₹{op.TECH_PER_SAVER:.0f} tech per KYC'd user reached; +10% contingency",
         M_("Our estimate"), "The 2 Oct costing"),
        ("Doorstep", "1 in 10 savers; 80% at month 3, 55% at a year", M_("Agreed"), "Founders (90% online); agreed street input")]
    assert abs(d["r12"] - float(MAIN["still saving at 12 months"])) < 0.001
    trs = [[f"<b>{a}</b>", b, c, e] for a, b, c, e in rows]
    return page(n, "Appendix", f"{AN['inputs']} · INPUTS", "Every input of the main case: fixed on 24 October, drawn, or still to confirm",
                table(["Input", "Main case", "Status", "Source"], trs, [15, 37, 12, 36], 9.5, compact=True, cls="inp"),
                f"Fixed: set by the founders (market figures, Bachatt, or our judgement). Drawn: picked at random within its range in each of the 1,000 runs; the "
                f"main case is the median ({ref('mc')}). Unconfirmed: in the main case, not yet in writing ({ref('prove')}). Agreed: {ref('product_in')}. At "
                f"{rs(op.SEED_CAC)}: one saver's LTV/CAC at 5 / 8 years and the company's money needed. ₹{op.FX:.0f} = $1.")


UNIT_SHORT = {"share of active savers with no housing loan running, a year": "of savers with no housing loan, a year",
              "share of the loan, at disbursal, none taken back": "of the loan, at disbursal",
              "share of the agreed take-up, months 1–6 (100% from month 7)": "of the full rate (100% from month 7)",
              "share of the agreed approval, months 1–6 (100% from month 7)": "of the full approval (100% from month 7)",
              "share of active savers without it, a year": "of savers without it, a year", "Rs an active saver a month": "₹ a saver a month"}

# the agreed product inputs that moved the earlier, plan-centred Monte Carlo most (online_mc.py, 22 Oct)
PRODUCT_KEYS = ["early_takeup_mult", "early_approval_mult", "loan_vehicle_ticket", "approval_growth", "loan_lap_approval", "takeup_growth",
                "amount_growth", "bills_ticket", "shop_comm", "fd_takeup", "support_cost", "life_term_takeup", "gold_renew", "two_wheeler_comm"]
# what the main case does with the ones the founders' 24 Oct decisions (or the 22 Oct review) switched off
PRODUCT_OFF = {"bills_ticket": ("bills_takeup", "off: not in the launch app"), "fd_takeup": ("fd_takeup", "off: not in the launch app"),
               "shop_comm": ("ins_partner_share", "not counted: a fixed insurance fee"), "life_term_takeup": ("ins_partner_share", "not counted: a fixed insurance fee"),
               "two_wheeler_comm": ("ins_partner_share", "not counted: a fixed insurance fee"), "gold_renew": ("gold_takeup", "off: no digital gold at launch")}


def a_product(n):
    keys = [k for k in PRODUCT_KEYS if k in DIST.index]
    rows = []
    for k in keys:
        d = DIST.loc[k]
        u = d["unit"] if isinstance(d["unit"], str) else ""
        p = ("share" in u) or ("relative" in u) or ("a year" == u.strip())
        nm = re.sub(r"\s*\([^)]*\)", "", str(d["name"]))
        nm = re.sub(r"\bhis\b", "the saver's", nm)
        conf = d["confidence"] if isinstance(d["confidence"], str) else ""
        u = UNIT_SHORT.get(u, re.sub(r"\s*\([^)]*\)", "", u))
        if k in PRODUCT_OFF:
            gate, txt = PRODUCT_OFF[k]
            assert float(X[gate]) == 0.0, (k, gate, X[gate])
            used = f'<span style="color:{SLATE}">{txt}</span>'
        elif abs(float(X[k]) - float(d["likely"])) > 1e-9:
            used = f"<b>{num(X[k], p) if float(X[k]) else 'none'}</b> (24 Oct)"
        else:
            used = "likely"
        rows.append([rupee(nm), num(d["low"], p), num(d["likely"], p), num(d["high"], p), rupee(u), used, conf.replace("Your number", "Founder-supplied")])
    return page(n, "Appendix", f"{AN['product_in']} · AGREED PRODUCT INPUTS", "The agreed product inputs that matter most (ranges agreed 16 Oct), and what the main case does with each",
                table(["Input", "Low", "Likely", "High", "Unit", "Main case", "Confidence"], rows, [33, 7, 7, 8, 18, 15, 12], 11, compact=True),
                "The inputs that moved the earlier Monte Carlo most. The main case holds each at its likely value unless the founders' 24 October decisions "
                "set it to none or switched the product off. The full list of agreed ranges travels with the model.")


def a_costs(n):
    rows = [["Founders", "₹95,000 ($1,000) a month each until month 18", "₹1.5 lakh a month each after the round (+10% statutory, +7% a year)"],
            ["Engineers", "1 from month 1 (₹1.1 lakh), 1 junior from month 7 (₹50k)", "3 + 1 per 2 lakh active savers, up to 40 (₹1.2 lakh)"],
            ["Operations and support", "1 from month 4 (₹30k)", "1 per 20,000 active savers, at least 2 (₹40k)"],
            ["Product, compliance, growth, finance, risk", "Founders, CA and lawyer", "1 each, scaling with savers and ad spend"],
            ["App and tech", "₹15 lakh to integrate, ₹1.5 lakh a month", f"₹1.5 lakh a month + ₹{op.TECH_PER_SAVER:.0f} per KYC'd user reached"],
            ["Payments (daily debits)", f"₹0 a debit in the model; the seed budget ({AN['seedbudget']}) carries ₹2 a weekly debit, to be safe",
             f"₹0 a debit through BSE StAR MF or the fund house's mandate, not yet in writing (₹2 a weekly debit: {levneed('We pay Rs 2 a debit, weekly')}, {AN['levers']})"],
            ["Office", "Co-working ₹75k a month", "₹1.5 lakh + ₹10k a head a month"],
            ["Compliance", "Setup ₹1.25 lakh; ₹10 lakh a year", "₹25 lakh a year"],
            ["Brand, design, fund-raising", "Design ₹1 lakh a month in months 1–3; ₹5 lakh to raise the seed", "Brand ₹2 lakh a month; ₹15 lakh for the next round"],
            ["Doorstep agents", "₹26,000 a month all-in; 100 sign-ups a month after a 3-month ramp", "1 team lead per 10 agents and 1 office per 15, once above 5 agents"],
            ["Contingency", "10% on every cost line (agreed)", "10% on every cost line (agreed)"],
            ["Cash timing", "Fund and partner fees arrive 2 months after they are earned (agreed)", "Same"]]
    return page(n, "Appendix", f"{AN['costs']} · COSTS AND TEAM", "Costs and team: the seed (months 1–18) and after the round",
                table(["Line", "Seed (months 1–18)", "After the round (month 19 on)"], rows, [22, 39, 39], 12, cls="tight"),
                f"Seed numbers are the seed plan's; later rules are our judgement on agreed salary inputs. The 10% contingency also applies to acquisition, so "
                f"{rs(op.CAC)} to win costs {rs(CAC)} in the company model. Tax 25% after losses carried forward; no interest on cash.")


def a_seed(n):
    return repage(sp.p_funds(), n, f"Appendix · {AN['seedbudget']} seed budget", AN["seedbudget"])


def a_reg(n):
    return repage(sp.p_reg(), n, f"Appendix · {AN['reg']} regulatory path", AN["reg"])


YEAR_LINES = [("Online savers won", "online savers won", "n"), ("Doorstep savers won", "doorstep savers won", "n"),
              ("Active savers (end)", "active savers (end)", "n"), ("Money saved, ₹ Cr (end)", "AUM Rs cr (end)", "cr"),
              ("Fund fees, ₹ Cr", "Fund trail Rs cr", "cr"), ("Personal + business loans, ₹ Cr", "Loan marketing fees Rs cr", "cr"),
              ("Other lenders' loans, ₹ Cr", "Other products Rs cr", "cr"), ("Cards, ₹ Cr", "Cards Rs cr", "cr"),
              ("<b>Revenue, ₹ Cr</b>", "Revenue Rs cr", "crb"), ("Acquisition, ₹ Cr", "Acquisition Rs cr", "cr"), ("Team, ₹ Cr", "Team Rs cr", "cr"),
              ("Other costs, ₹ Cr", "Other costs Rs cr", "cr"), ("<b>EBITDA, ₹ Cr</b>", "EBITDA Rs cr", "crb"), ("Cumulative EBITDA, ₹ Cr", "_cum", "cr"),
              ("PAT, ₹ Cr", "PAT Rs cr", "cr"), ("Heads (end)", "Heads (end)", "n"), ("Doorstep agents (end)", "Doorstep agents (end)", "n")]


def ycell(v, f):
    v = float(v)
    if f == "n":
        return ind(v)
    s = indf(v, 1) if abs(v) >= 10 else indf(v, 2)
    return f"<b>{s}</b>" if f == "crb" else s


def a_year(n, key, df, title, note=""):
    df = df.sort_values("year").copy()
    assert float(df["Insurance Rs cr"].abs().max()) < 1e-9, "insurance is not counted, so the table leaves it out"
    df["_cum"] = np.cumsum(df["EBITDA Rs cr"].astype(float))
    rows = [[lab] + [ycell(v, f) for v in df[c]] for lab, c, f in YEAR_LINES]
    return page(n, "Appendix", f"{AN[key]} · {title.split(':')[0].upper()}", f"{AN[key]} · {title}",
                table(["", *[f"Y{y}" for y in df["year"]]], rows, [24] + [9.5] * 8, 10.5, compact=True, cls="yr"),
                (note + " " if note else "") + "Money saved: savers' fund balance at year end. Other lenders' loans: gold, property, home, durable and vehicle "
                "loans; insurance is not counted. PAT: profit after tax (equal to EBITDA while past losses absorb the tax). Other costs include the 10% "
                "contingency. Undiscounted.")


def rung_year(rung):
    return od.LADY[od.LADY["rung"] == rung].sort_values("year")


def a_year_main(n):
    return a_year(n, "year_main", rung_year("Main case"), f"The main case: {LEVEL:,} online savers a month from month 30, year by year",
                  f"Main case: the founders' 24 October inputs; still saving at 12 months {od.val('keep').split(',')[0]} and the debt fund's fee "
                  f"{od.val('trail')}, the Monte Carlo median.")


def a_year_top(n):
    t = od.TOP
    return a_year(n, "year_top", rung_year("All upside"), f"The top rung ({x(t['LTV/CAC 5y'])}), every upside lever at once: what it takes, not a plan",
                  f"All five upside levers at once: ₹{float(t['saved a day Rs']):.0f} a day, {float(t['still saving at 12 months']):.0%} still saving "
                  f"({float(t['drop-off a month after 12']):.1%} a month after), applying {float(t['apply a year']):.0%}, approval {float(t['first loans approved']):.0%}, "
                  f"take-up +{float(t['take-up rise a year']):.0%} and approval +{float(t['approval rise a year']):.0%} a year (our old loan targets): EBITDA "
                  f"positive from {month(t['EBITDA positive from month'])} on {need(t)} ({ref('ladder')}).")


def a_mc(n):
    S = od.SUMM
    show = [("LTV/CAC, 5 years", "LTV/CAC, 5 years", x), ("LTV/CAC, 8 years", "LTV/CAC, 8 years", x),
            ("Saver pays back in month (97 = not by 96)", "Saver pays back", month),
            ("Company EBITDA positive from month (97 = not by 96)", "Company EBITDA positive from", month),
            ("Money needed, $M", "Money needed in all", lambda v: usd(v) + ("+" if od.NO_PROFIT else "")), ("Year 5 EBITDA, Rs crore", "Year 5 EBITDA", cr),
            ("Cumulative EBITDA to month 60, Rs crore", "Cumulative EBITDA, 5 years", cr), ("Cumulative EBITDA to month 96, Rs crore", "Cumulative EBITDA, 8 years", cr)]
    srows = [[lab] + [by(S.loc[k, p]) if f is month else f(float(S.loc[k, p])) for p in ("P10", "P50", "P90")] for k, lab, f in show]
    share = lambda k: (lambda v: f"{v:.1%}" if 0 < v < 0.01 else f"{v:.0%}")(float(S.loc[k, "P50"]))
    crow = [["LTV/CAC at least 1× in 5 years", share("chance LTV/CAC >= 1")],
            ["At least 2× / 3× in 5 years", f"{share('chance LTV/CAC >= 2')} / {share('chance LTV/CAC >= 3')}"],
            ["LTV/CAC at least 1× in 8 years", share("chance 8-year LTV/CAC >= 1")], ["The saver pays back by month 96", share("chance saver pays back by month 96")],
            ["Company EBITDA positive by month 96", share("chance EBITDA positive by month 96")],
            ["Cumulative EBITDA positive by month 96", share("chance cumulative EBITDA positive by month 96")]]
    left = table(["Across the 1,000 runs", "P10", "P50 (median)", "P90"], srows, [43, 19, 19, 19], 11, compact=True, cls="tight") + \
        '<div style="margin-top:10px"></div>' + table(["Share of the 1,000 runs (all else at the main case)", ""], crow, [78, 22], 11, compact=True, cls="tight")
    lab = {"keep": "Still saving at 12 months", "trail": "The debt fund's fee"}
    ends_ = {"keep": lambda d: f"{d['r12']:.0%}", "trail": lambda d: od.pct(d["_debt_trail"], 2)}
    lo_, hi_ = lo.drawn(lo.at(0.0)), lo.drawn(lo.at(1.0))
    drows = [[lab[k], ends_[k](lo_), x(r["median if low"]), ends_[k](hi_), x(r["median if high"]), f"{float(r['rank corr with LTV/CAC']):.2f}"]
             for k, r in od.DRV.iterrows()]
    right = (f'<div class="sub-h" style="margin-top:0">WHAT PINNING EACH INPUT IS WORTH: THE MEDIAN, 5 YEARS</div>'
             + table(["If the facts find…", "Low end", "Median", "High end", "Median", "Rank corr."], drows, [31, 13, 14, 13, 14, 15], 11, compact=True, cls="tight"))
    D = od.DRAWS
    r12 = np.array([lo.drawn({"keep": k, "trail": 0.0})["r12"] for k in D["keep"]])
    edges = np.linspace(lo_["r12"], hi_["r12"], 6)
    brows = []
    for i in range(5):
        m = (r12 >= edges[i] - 1e-12) & ((r12 < edges[i + 1]) if i < 4 else (r12 <= edges[i + 1] + 1e-12))
        g = D[m]
        brows.append([f"{edges[i] * 100:.0f}–{edges[i + 1] * 100:.0f}%", f"{int(m.sum())}", x(g["ltv_cac"].median()), x(g["ltv_cac_96"].median()),
                      by(g["payback"].median()), usd(g["money"].median()) + ("+" if od.NO_PROFIT else "")])
    assert sum(int(b[1]) for b in brows) == len(D)
    right += ('<div class="sub-h" style="margin-top:14px">THE RUNS BY STILL SAVING AT 12 MONTHS: MEDIANS</div>'
              + table(["Still saving", "Runs", "5 years", "8 years", "Saver pays back", "Money needed"], brows, [18, 12, 15, 15, 22, 18], 11, compact=True, cls="tight"))
    return page(n, "Appendix", f"{AN['mc']} · THE MONTE CARLO", "1,000 runs of the model on the value of a saver: the results, and what pinning each still-uncertain input is worth",
                od.two(left, right, 530),
                f"The Monte Carlo: we ran the model 1,000 times, picking still saving at 12 months ({lo_['r12']:.0%}–{hi_['r12']:.0%}, the drop-off after a year "
                f"{lo_['churn_late']:.1%} to {hi_['churn_late']:.1%}) and the debt fund's fee ({od.pct(lo_['_debt_trail'], 2)}–{od.pct(hi_['_debt_trail'], 2)}) at random "
                f"within their ranges; everything else is fixed by the founders, the cost to win at {rs(CAC)}. Median (P50): the middle run; P10 / P90: the 10th and "
                f"90th percentiles, so 8 in 10 runs fall between them (each measure on its own). Company at {LEVEL:,} online savers a month; +: the cash hole is "
                "still deepening at month 96. Rank corr.: how closely the input moves LTV/CAC (1 = fully).")


LEVER_NAMES = {**dict(bc.LEVERS), "Non-savers stay as long as savers": "KYC'd non-savers stay as long as savers",
               "Online only after m18": "Online only after month 18 (no doorstep)",
               # one definition of retention everywhere (FIXES B9): the drop-off after a year on the line through Bachatt's range
               "45% still saving at a year": f"45% still saving (then {op.churn_for(0.45):.1%} a month drop off)",
               "24% still saving at a year (savings apps)": f"24% still saving, like savings apps (then {op.churn_for(0.2415):.1%} a month)",
               "Credit-hungry: 45% stay + 50% apply": f"Credit-hungry: 45% still saving (then {op.churn_for(0.45):.1%} a month) and 50% applying"}
LEVER_SHORT = {"Rs 300 a day": "₹300 a day", "Rs 200 a day": "₹200 a day", "Credit-hungry: 45% stay + 50% apply": "credit-hungry savers",
               "Loan funnel at our old targets": "our old loan targets", "45% still saving at a year": "45% still saving"}


def a_levers(n):
    L = pd.read_csv(TAB / "ltv_main_levers.csv")
    assert L["case"].iloc[0] == "The main case"
    rows = []
    for i, r in L.iterrows():
        k = r["case"]
        lv = "The plan" if k == "The main case" else k
        ltv = x(od.ltvl(lv)) if lv in od.LTVL.index else "–"
        pm = str(r["EBITDA positive from month"])
        prof = "not by month 96" if pm.startswith("after") else f"month {int(float(pm))}"
        money = usd(r["money needed $M"]) + ("+" if pm.startswith("after") else "")
        cells = [LEVER_NAMES.get(k, rupee(k)), ltv, prof, money, crn(r["Y5 EBITDA Rs cr"]), crn(r["Y8 EBITDA Rs cr"]), f"{r['active savers m60'] / 1e5:.1f}"]
        rows.append([f"<b>{c}</b>" for c in cells] if i == 0 else cells)
    win = sorted(((int(float(r["EBITDA positive from month"])), r["case"]) for _, r in L.iterrows() if str(r["EBITDA positive from month"])[0].isdigit()))
    names = [LEVER_SHORT.get(c, rupee(c)) for _m, c in win]
    lst = ", ".join(names[:-1]) + (" or " if len(names) > 1 else "") + names[-1] if names else ""
    return page(n, "Appendix", f"{AN['levers']} · EVERY ASSUMPTION TESTED",
                (f"Every assumption tested, one at a time: only {lst} bring profit by month 96" if names else
                 "Every assumption we tested, one at a time around the main case: none brings profit by month 96"),
                table(["Assumption changed", "One saver, 5 years", "EBITDA positive", "Money needed", "Y5 EBITDA ₹ Cr", "Y8 EBITDA ₹ Cr", "Active savers, month 60 (lakh)"],
                      rows, [36, 10, 13, 11, 10, 10, 10], 10.5, compact=True, cls="tight"),
                f"One change at a time on the main case (first row); the company at {LEVEL:,} online savers a month from month 30. One saver, 5 years: the online "
                "saver's LTV/CAC with the same change (–: the change is to the company only). Money needed: the seed + the deepest cash hole (fees arrive 2 months "
                "late) + a ₹5 crore cash buffer, at ₹95 = $1; +: EBITDA is still negative at month 96, so at least that (run on, the main case's hole bottoms "
                "around year 12 at about $10.6M).")


def a_audit(n):
    a = pd.read_csv(AUDIT)
    vc = a["verdict"].fillna("").str.lower().value_counts()
    fixed = int(vc.get("mislabelled", 0) + vc.get("not supported", 0))
    lab = [("matches", "match their source"), ("judgement-labelled-as-such", "our judgement, labelled as such"),
           ("partly", "partly supported by their source"), ("target", "were targets: the loan funnel and the cost to win")]
    chips = "".join(f'<div class="kpi"><b>{int(vc.get(k, 0))}</b><span>{t}</span></div>' for k, t in lab) + \
        f'<div class="kpi"><b>{fixed}</b><span>wrong or unsourced: fixed or flagged below</span></div>'
    assert sum(int(vc.get(k, 0)) for k, _t in lab) + fixed == len(a)
    # what the audit found in the plan as first built (every 'mislabelled' or 'not supported' line), and the main case today
    rows = [["The loan funnel (applying 35%, the loan sizes, offers to every KYC'd sign-up, payout rising to 3%) was labelled as evidence",
             f"Replaced on 24 Oct by today's market: {od.val('apply')} apply, {od.val('approved')} approved, no yearly rises, {od.val('payout')}, "
             f"{od.lakh(X['ticket'])} first loans; our old targets appear only as the upside of what it takes"],
            ["No payment cost on debits; tech ₹1 a saver a month", f"₹{op.TECH_PER_SAVER:.0f} tech for every KYC'd user reached; debits ₹0 through BSE StAR MF or "
                                                                     f"the fund house (unconfirmed in writing), ₹2 a weekly debit tested ({AN['levers']})"],
            ["Insurance counted 75% of a broker's commission; the Choti SIP incentive and digital gold were counted",
             "Insurance: a fixed referral fee, not counted until agreed; Choti, digital gold, recharge, bills, FD and NPS off"],
            ["Cost to win in the seed was ₹550; the seed's own funnel gives ₹600 an online saver", f"{rs(op.CAC)} at scale (the founders' figure), held fixed; the seed budgets {rs(op.SEED_CAC)} and measures it"],
            ["The agreed 10% contingency on every cost line was missing", f"Added, inside EBITDA and on the LTV's cost to win ({rs(CAC)})"],
            ["The agreed 2-month delay before fees arrive in cash was missing", "Added to cash and money needed"],
            ["Compliance of ₹25 lakh a year after the seed is not an agreed input", f"Kept; {AN['costs']} marks post-round costs as our judgement"],
            ["Loan against property take-up (0.5%) and size had no source", f"Take-up rebuilt 21 Oct from lender data (3% of loan applicants, 1% payout); "
                                                                           f"size {od.lakh(X['loan_lap_ticket'])}, today's market (24 Oct)"]]
    body = f'<div class="kpis" style="grid-template-columns:repeat(5,1fr)">{chips}</div>' + \
        '<div class="sub-h" style="margin-top:14px">WHAT THE AUDIT FOUND, AND WHAT THE MAIN CASE DOES NOW</div>' + \
        table(["Finding", "The main case"], rows, [50, 50], 11, compact=True, cls="tight")
    return page(n, "Appendix", f"{AN['audit']} · INPUT AUDIT",
                f"All {len(a)} inputs were checked against their sources on 22 Oct; on 24 Oct the founders replaced the hopeful ones with market figures",
                body, f"An independent reviewer read each source row; the full {len(a)}-row table travels with the model. The 24 October decisions: "
                      f"{ref('inputs')} and {ref('changes')}.")


def a_sheet(n):
    raw = pd.read_csv(SHEETCHK, dtype=str)
    c = raw.copy()
    for k in ("sheet", "python", "gap", "gap_pct"):
        c[k] = pd.to_numeric(c[k], errors="coerce")
    c["ok"] = raw["ok"].str.strip().str.lower() == "true"
    pm = raw[raw["measure"].str.contains("positive")]
    same = int((pm["sheet"] == pm["python"]).sum())            # as text: a lever that never turns positive reads "after m96" on both
    ok, tot = int(c["ok"].sum()), len(c)
    rev = c[c["measure"].str.startswith("Revenue")]["gap_pct"].abs().max()
    chips = (f'<div class="kpi"><b>{ok} of {tot}</b><span>checks within target</span></div>'
             f'<div class="kpi"><b>{rev * 100:.2f}%</b><span>largest revenue gap, any year, any case</span></div>'
             f'<div class="kpi"><b>{same} of {len(pm)}</b><span>cases with the same profit month</span></div>')
    want = [("Revenue, year 5 (Rs crore)", "Revenue, year 5 (₹ Cr)"), ("EBITDA, year 5 (Rs crore)", "EBITDA, year 5 (₹ Cr)"),
            ("Revenue, year 8 (Rs crore)", "Revenue, year 8 (₹ Cr)"), ("EBITDA, year 8 (Rs crore)", "EBITDA, year 8 (₹ Cr)"),
            ("EBITDA positive from month", "EBITDA positive from"), ("Money needed (Rs crore)", "Money needed (₹ Cr)"),
            ("Active savers, month 60", "Active savers, month 60"), ("AUM month 60 (Rs crore)", "Money saved, month 60 (₹ Cr)")]

    def cell(case, m, k):
        r = raw[(raw["case"] == case) & (raw["measure"] == m)].iloc[0]
        v = str(r[k])
        if "positive" in m:
            return "not by month 96" if v.startswith("after") else f"month {int(float(v))}"
        v = float(v)
        return ind(v) if "savers" in m else (indf(v, 1) if abs(v) >= 10 else indf(v, 2))
    rows = [[lab, cell("20000", m, "sheet"), cell("20000", m, "python"), cell("150000", m, "sheet"), cell("150000", m, "python")] for m, lab in want]
    need = float(c[(c["case"] == "20000") & (c["measure"] == "Money needed (Rs crore)")]["python"].iloc[0]) * 1e7 / op.FX / 1e6
    assert abs(need - float(MAIN["money needed $M"])) < 0.05, (need, MAIN["money needed $M"])
    rows[5][0] = f"Money needed (₹ Cr; {usd(need)}{'+' if bc.no_profit(MAIN) else ''} at 20,000)"
    miss = c[~c["ok"]]
    body = f'<div class="kpis" style="grid-template-columns:repeat(3,1fr)">{chips}</div>' + \
        '<div class="sub-h" style="margin-top:14px">THE SHEET NEXT TO THE MODEL</div>' + \
        table(["Measure", "Main case, 20,000 a month: sheet", "… model", "1,50,000 a month: sheet", "… model"], rows, [32, 17, 17, 17, 17], 12, compact=True) + \
        (f'<div class="rbox" style="margin-top:12px">{len(miss)} checks are outside target; the largest gap is ₹{miss["gap"].abs().max():.2f} Cr.</div>' if len(miss) else "")
    nlev = raw.loc[raw["case"].str.startswith("lever") & (raw["case"] != "lever: The main case"), "case"].nunique()
    return page(n, "Appendix", f"{AN['sheet']} · SPREADSHEET CHECK", "The spreadsheet and the model give the same answers on the main case", body,
                f"Both plans (20,000 and 1,50,000 online savers a month): revenue and EBITDA in every year 1–8, profit month, money needed, active savers and money "
                f"saved at month 60. Each of the {nlev} assumption changes of {AN['levers']}: years 5 and 8 and the profit month. Every formula of the sheet's v4 "
                "tabs was evaluated on the founders' 24 October inputs and compared with the model.")


# the 24 Oct bridge, one decision a row (tables/ltv_bridge.csv): (a word in the table's step, name, was -> now and its source);
# a step the table adds later and this list lacks is shown in the table's own words
BRIDGE_TXT = [("contingency", "Serving carries our 10% contingency", "a correction: the cost of serving a saver now carries the 10% contingency, "
                                                                     "as the company model always did"),
              ("70k", "Personal and business loans: Bachatt's size", "₹1.7 lakh (drawn ₹50k–3 lakh) → ₹70k first loans, repeats 10% bigger a year plus "
                                                                       "top-ups · Bachatt's number; our research had ₹15k–58.5k"),
              ("today's market", "Apply and approval at today's market", "apply 27% → 20% a year; first loans approved 25% → 20%; yearly rises 2.4% / 4.8% → none"),
              ("Home", "Home and property loans at market sizes", "home ₹20.6 lakh → ₹12 lakh; property ₹14.6 lakh → ₹5 lakh"),
              ("payout", "Lender payout flat", "2%, rising 24% by year 5 → 2% flat · the middle of the market's 1–3%"),
              ("Non-savers", "KYC'd non-savers fade", "1.72 reached per saver, kept as long as savers → fade within ~3 months: 1.06 reached"),
              ("Recharge", "Products not in the launch app", "recharge, bills, FD and NPS: on → off"),
              ("Debits", "Debits at ₹0 to us (to confirm)", "₹2 a weekly debit → ₹0 through BSE StAR MF or the fund house's mandate · not yet in writing"),
              ("Still saving", "Still saving at 12 months: Bachatt's range", "36% → Bachatt's 30–40%, drawn (median 35%), the drop-off after a year moving "
                                                                             "with it; the debt fund's fee and repeat approval set to the main case")]


def bridge_rows(B):
    """(name, was -> now) for each step after the first, matched to BRIDGE_TXT by keyword."""
    out = []
    for step in B["step"].iloc[1:]:
        hit = [(nm, sub) for key, nm, sub in BRIDGE_TXT if key.lower() in step.lower()]
        out.append(hit[0] if hit else (rupee(step), ""))
    return out


def bridge_svg(W=1152):
    B = od.BRIDGE
    v0, vend = float(B["LTV/CAC 5y"].iloc[0]), float(B["LTV/CAC 5y"].iloc[-1])
    assert abs(vend - od.MED) < 0.005
    x0, x1_, top, rh = 640, 1010, 1.85, 36
    X_ = lambda v: x0 + (x1_ - x0) * v / top
    s = [T(0, 14, "THE DECISION: WAS (23 OCT) → NOW (24 OCT)", 11, 700, SLATE, ls=1), T(x0, 14, "ONE SAVER'S LTV/CAC, 5 YEARS", 11, 700, SLATE, ls=1),
         T(W, 14, "CHANGE", 11, 700, SLATE, "end", ls=1)]
    rows = [("Last week's main case (23 Oct)", f"8 years {x(B['LTV/CAC 8y'].iloc[0])}; pays back in {by(B['saver pays back in month'].iloc[0])}", 0.0, v0, "start")]
    prev, p8 = v0, float(B["LTV/CAC 8y"].iloc[0])
    for (nm, sub), (_, r) in zip(bridge_rows(B), B.iloc[1:].iterrows()):
        v, v8 = float(r["LTV/CAC 5y"]), float(r["LTV/CAC 8y"])
        # each change is the difference of the ROUNDED levels, so the labels add up to the two ends
        rows.append((nm, sub, prev, v, f"{round(v, 2) - round(prev, 2):+.2f}|8y {round(v8, 2) - round(p8, 2):+.2f}"))
        prev, p8 = v, v8
    rows.append(("The main case (24 Oct)", f"8 years {x(B['LTV/CAC 8y'].iloc[-1])}; pays back in {by(B['saver pays back in month'].iloc[-1])}", 0.0, vend, "end"))
    y = 24
    yb = 24 + len(rows) * rh
    s.append(f'<line x1="{X_(1):.1f}" y1="20" x2="{X_(1):.1f}" y2="{yb}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    for i, (nm, sub, a, b, tag) in enumerate(rows):
        ends = tag in ("start", "end")
        if tag == "end":
            s.append(R(-6, y + 1, W + 12, rh - 3, sp.NAVY_L, r=6))
        s.append(T(0, y + 16, nm, 13, 800 if ends else 700, NAVY))
        s.append(T(0, y + 31, sub.replace("Rs ", "₹"), 10.5, 500, SLATE))
        col = NAVY if ends else (TEAL if b > a else LATE)
        lo_, hi_ = sorted((X_(a), X_(b)))
        s.append(R(lo_, y + 9, max(hi_ - lo_, 2), 18, col, r=4))
        if not ends and i + 1 < len(rows) - 1:
            s.append(f'<line x1="{X_(b):.1f}" y1="{y + 27}" x2="{X_(b):.1f}" y2="{y + rh + 9}" stroke="{MUTE}" stroke-dasharray="2 2"/>')
        s.append(halo(T(hi_ + 6, y + 23, x(b), 12, 800 if ends else 600, col)))
        if ends:
            s.append(T(W, y + 24, x(b), 16, 800, NAVY, "end"))
        else:
            c5, c8 = tag.split("|")
            s.append(T(W, y + 18, c5.replace("-", "−"), 14, 800, col, "end"))
            s.append(T(W, y + 32, c8.replace("-", "−"), 10.5, 600, SLATE, "end"))
        y += rh
    s.append(T(X_(1), yb + 14, "1×", 11, 800, RED, "middle"))
    return svg(W, yb + 18, "".join(s))


def a_changes(n):
    B = od.BRIDGE
    lv = B["LTV/CAC 5y"].astype(float).round(2)
    ch = lv.diff()                                                  # from the rounded levels, so the steps add up to the two ends
    step = lambda key: float(ch[B["step"].str.contains(key, case=False, regex=False)].sum())
    loan2 = step("70k") + step("today's market")
    deb = step("Debits")
    title = (f"From the 23 October {x(lv.iloc[0])} to {x(lv.iloc[-1])} today: the ₹70k loan and market apply and approval did most of it ({loan2:+.2f}), "
             f"and ₹0 debits, still to confirm, won back {deb:+.2f}").replace("-", "−")
    return page(n, "Appendix", f"{AN['changes']} · WHAT CHANGED ON 24 OCTOBER", title, bridge_svg(),
                f"One decision at a time, in this order, each on top of the last (a different order moves the sizes a little). Unchanged on 24 October: the "
                f"equity fund fee {od.pct(op.EQ_TRAIL, 2)} (active funds, still to confirm in writing), ₹100 a day (our product's floor) and the cost to win "
                f"{rs(CAC)} (the founders' figure, with our 10% contingency), held throughout.")


def a_upside(n):
    return repage(bc.p_upside(n), n, "Appendix", AN["upside"])


def a_capture(n):
    cp = bc.CAPR
    pm = int(float(cp["EBITDA positive from month"]))
    turn = (f"EBITDA turns positive only in month {pm}, as sign-ups stop; year 8 as a whole is still {cr(cp['Y8 EBITDA Rs cr'])}"
            if pm <= 96 and float(cp["Y8 EBITDA Rs cr"]) < 0 else f"EBITDA positive from {month(pm)}")
    return a_year(n, "capture", pd.read_csv(TAB / "online_capture_10cr_yearly.csv"),
                  "The upside, not the plan: 10 crore savers on the main case, year by year",
                  f"The 10-crore path ({AN['upside']}): {bc.ppl(cp['online savers won a month (m30 on)'])} online savers won a month from month 30, each the main "
                  f"case's saver; a third of a 30 crore segment by month 96. {turn}; money needed ${float(cp['money needed $M']):,.0f}M.")


def a_sources(n):
    rows = []
    with (ROOT / "research" / "xs_funnel_2026-10-21.csv").open() as f:
        for r in csv.DictReader(f):
            m = r["metric"].replace("DSA payout", "Referral payout")
            src = r["source"].replace("DSA platforms", "Loan-agent platforms")
            rows.append([clip(m, 58), clip(rupee(r["value"]), 46), clip(src, 44), clip(r["as_of"], 14)])
    return page(n, "Appendix", f"{AN['sources']} · LOAN AND CROSS-SELL SOURCES", "Where the loan funnel's benchmarks come from (researched 21 Oct 2026)",
                table(["Measure", "Value", "Source", "As of"], rows, [37, 29, 25, 9], 9, compact=True, cls="xs"),
                "Referral payouts: loan-agent platforms' own pages (direct selling agents, the lenders' referral partners), indicative. Take rates: our "
                f"division of reported revenue by disbursals. The founders set the 24 October loan inputs from these ({ref('inputs')}).")


DEBIT_SRC = {   # research/tri_costs.csv TC-42..47, in plain words (no unexplained jargon on the page)
    "TC-42": ("Exchange SIP (XSIP) on BSE StAR MF: cost to the distributor", "Free of charge to distributors; several SIPs, for any fund house, can run under one mandate"),
    "TC-43": ("Who pays BSE for StAR MF orders", "Since 2018 fund houses pay BSE per transaction (26 of 37 agreed); no current fee schedule is public"),
    "TC-44": ("Daily SIPs through BSE StAR MF in practice", "A broker's help page: a daily exchange SIP exists; it cannot be paused, only cancelled"),
    "TC-45": ("Daily SIP minimum per scheme", "About ₹100 at most fund houses (₹500 at one, ₹10 at a passive fund); so ₹80 + ₹20 a day likely becomes one hybrid fund"),
    "TC-46": ("UPI payment fee on one-time fund purchases, from 15 Oct 2026", "0.02% (capped at ₹300) on lump sums, borne by the industry; recurring Autopay SIP debits carry none"),
    "TC-47": ("Bachatt's app listings (a benchmark)", "Daily saving from ₹51 or ₹101 a day (listings conflict); a liquid fund from ₹20 a day; UPI Autopay; personal loans")}


def a_debit_src(n):
    rows = []
    with (ROOT / "research" / "tri_costs.csv").open() as f:
        for r in csv.DictReader(f):
            if r["id"] in DEBIT_SRC:
                what, says = DEBIT_SRC[r["id"]]
                src = clip(re.sub(r"\s*[:;].*$", "", r["source_title"]), 48)
                rows.append([what, says, src, r["source_date"] if r["source_date"] != "n/a" else f"live page, read {r['accessed']}"])
    assert len(rows) == len(DEBIT_SRC), len(rows)
    return page(n, "Appendix", f"{AN['debit_src']} · DEBIT ROUTE SOURCES",
                "Why the main case puts debits at ₹0 and ₹100 a day into one hybrid fund, and why both still need confirming in writing",
                table(["What", "What the source says", "Source", "Date"], rows, [26, 40, 20, 14], 11.5, compact=True, cls="tight") +
                '<div class="rbox" style="margin-top:14px;font-size:13px"><b>Still open, asked in writing:</b> whether BSE StAR MF or the fund houses accept a ₹100 '
                'daily SIP through the exchange at ₹0 to us, and each fund house\'s distributor fee on its active equity funds. ₹0 to us holds only on the '
                'exchange route or the fund house\'s own mandate; a payment company of our own would charge its list price.</div>',
                f"Researched 24 October 2026. A ₹2 weekly debit would take one saver to {x(od.ltvl('We pay Rs 2 a debit, weekly'))} and the company to "
                f"{levneed('We pay Rs 2 a debit, weekly')} needed ({ref('levers')}).")


# ---------------------------------------------------------------- build
FNS = {"cover": lambda n: cover(), "customer": p_customer, "product": p_product, "flow": p_flow, "unit": p_unit, "funnel": p_loan_funnel,
       "odds": p_odds, "ladder": p_ladder, "financials": p_financials, "prove": p_prove, "fee": p_fee, "seed": p_seed, "divider": divider,
       "inputs": a_inputs, "product_in": a_product, "costs": a_costs, "seedbudget": a_seed, "reg": a_reg, "year_main": a_year_main,
       "year_top": a_year_top, "mc": a_mc, "levers": a_levers, "audit": a_audit, "sheet": a_sheet, "changes": a_changes, "upside": a_upside,
       "capture": a_capture, "sources": a_sources, "debit_src": a_debit_src}
STALE = ("1.75×", "7.7×", "₹3 lakh", "₹1.7 lakh", "35% apply", "2.5 KYC'd", "month 63", "$4.7M", "₹2 a debit", "our targets", "at our target",
         "2.75×", "3× is reachable", "chance of 3×")
# FIXES 24 Oct: words that must not appear on THIS deck's own pages (other builders' pages are reported, not failed)
SOFT = ("(measured)", "measured,", "measured)", "cost to win is measured", "so cautious", "₹5 crore floor", "chance of", "market or measured",
        "1.72 KYC'd")
OTHERS = {"unit", "odds", "financials", "prove", "fee", "seed", "seedbudget", "reg", "upside"}
BRIDGE_ONLY = ("1.75×", "₹1.7 lakh", "2.75×")      # the 23 Oct starting point, shown only on the bridge


def build():
    pages = []
    for k in STORY:
        pages.append(FNS[k](PN[k]))
    pages.append(divider(PN["divider"]))
    for k, _t in APPX:
        pages.append(FNS[k](PN[k]))
    assert len(pages) == PN[APPX[-1][0]]
    for i, h in enumerate(pages[1:], start=2):            # every page carries its own number
        assert f"<span>{i}</span></footer>" in h, i
    css = (sp.CSS + ".at.compact td { padding: 4px 8px; } .at.compact th { padding: 4px 8px; } .at.tight td { padding: 3px 8px; line-height: 1.3; }"
           + bc.CSS_EXTRA + ".at.yr td { padding: 2.5px 8px; line-height: 1.25; } .at.xs td { padding: 2px 8px; line-height: 1.2; } "
           ".at.xs th { padding: 3px 8px; } .at.inp td { padding: 2.5px 7px; line-height: 1.25; }")
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Online model v4</title><style>{css}</style></head>'
            f'<body>{"".join(pages)}</body></html>')
    html = re.sub(r"\bRs\.?\s?(?=\d)", "₹", html)
    # the checks the brief asks for, on the text of every page
    # a stale string that is also a CURRENT number read from the tables is allowed where that number is shown
    live = {usd(float(od.R2["money needed $M"]) - 0.5): {PN["seed"]},     # the seed page: the next round if the facts point to 2x
            "2.5 KYC'd": {PN["funnel"]}}                                     # FIXES B12: about 2.5 KYC'd people come with each saver (worth 1.06)
    key_of = {v: k for k, v in PN.items()}
    for i, h in enumerate(pages, start=1):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"\bRs\.?\s?(?=\d)", "₹", h)))
        for bad in STALE:
            if (bad in BRIDGE_ONLY and i == PN["changes"]) or i in live.get(bad, ()):
                continue
            assert bad.lower() not in text.lower(), (i, bad)
        for bad in SOFT:
            if bad.lower() in text.lower():
                j = text.lower().find(bad.lower())
                msg = f"page {i} ({key_of.get(i)}) has {bad!r}: …{text[max(0, j - 60):j + 40]}…"
                assert key_of.get(i) in OTHERS or (key_of.get(i) == "ladder" and "out of reach" not in text and od.p_ladder()[1] in h), msg
                print("note, another builder's page:", msg)
    text = re.sub(r"<[^>]+>", " ", html)
    for bad in ("Bueno", "BetterPlace", ".py", ".csv", "tables/", "nobody serves both", "clawback"):
        assert bad.lower() not in text.lower(), bad
    assert not re.search(r"\b(DSA|MDR|TER|NPV)\b", text), re.search(r".{40}\b(DSA|MDR|TER|NPV)\b.{40}", text).group(0)
    assert not re.search(r"\b(he|his|him|she|her|hers|himself|herself)\b", text, re.I), re.search(r".{40}\b(he|his|him|she|her|hers)\b.{40}", text, re.I).group(0)
    out = HERE / "Online_model_v4.html"
    out.write_text(html)
    pdf = HERE / "Online_model_v4.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, capture_output=True)
    print("wrote", pdf, len(pages), "pages")


if __name__ == "__main__":
    build()

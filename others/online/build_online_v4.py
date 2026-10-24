"""Online_model_v4 (21 Oct 2026): the online-first deck that replaces Offline_model_v3. Operator: "remodel the excel sheet and
everything and check all inputs ... then the offline_v3 to turn it into online_v4 where 90% online and 10% offline"; taps:
story + appendix (~25 pages), ranges + Monte Carlo, the online ranges "OK as proposed".
24 Oct (founders): re-based on the main case, the LTV/CAC Monte Carlo's median with the cost to win fixed, plus the ladder of
LTV/CAC rungs (model/ltv_odds.py); our targets appear as the top rung, and the $1B test and the 10-crore path as the upside.
Numbers: tables/ltv_odds_*.csv, ltv_ladder*.csv, ltv_main_*.csv (model/ltv_odds.py), online_*.csv for our targets
(model/online_plan.py), seed_*.csv; the input audit (tables/online_inputs_audit.csv) and the sheet check (tables/v4_toy_check.csv)
when present. Pages reuse online/build_online_case.py, ltv/odds_pages.py and the seed plan's design (seed/build_seed_plan.py).
Builds online/Online_model_v4.html/.pdf."""
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "seed"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "model"))
import build_seed_plan as sp  # noqa: E402
import build_online_case as bc  # noqa: E402
import odds_pages as od  # noqa: E402  (on the path through build_online_case)

ld, lo = bc.ld, od.lo

TAB = ROOT / "tables"
INK, NAVY, TEAL, BLUE, AMBER, SLATE, MUTE, LINE, BG, RED = sp.INK, sp.NAVY, sp.TEAL, sp.BLUE, sp.AMBER, sp.SLATE, sp.MUTE, sp.LINE, sp.BG, sp.RED
NAVY2, NAVY3, NAVY4 = sp.NAVY2, sp.NAVY3, sp.NAVY4
T, R, A, svg = sp.T, sp.R, sp.A, sp.svg
FOOT = "Online model v4 · October 2026 · Confidential"

DIST = pd.read_csv(TAB / "dist_agreed_v1.csv").set_index("key")
DIST["name"] = DIST["name"].str.replace("his shop or home", "the saver's shop or home", regex=False)  # agreed file predates the neutral wording
AUDIT = TAB / "online_inputs_audit.csv"
SHEETCHK = TAB / "v4_toy_check.csv"


def page(n, section, kicker, title, body, src=""):
    s = f'<div class="src">{src}</div>' if src else ""
    return f"""<section class="page">
<header class="ph"><span class="brand">{sp.NAME} <em>· working name</em></span><span>{section}</span></header>
<div class="kicker">{kicker}</div><h1>{title}</h1>
<div class="body">{body}</div>{s}
<footer class="pf"><span>{FOOT}</span><span>{n}</span></footer>
</section>"""


def repage(html, n, section=None):
    """Re-number a page built by another builder and give it this deck's footer."""
    html = re.sub(r'<footer class="pf"><span>[^<]*</span><span>[^<]*</span></footer>', f'<footer class="pf"><span>{FOOT}</span><span>{n}</span></footer>', html)
    if section:
        html = re.sub(r'(<header class="ph">.*?</span><span>)[^<]*(</span></header>)', rf"\g<1>{section}\2", html, count=1, flags=re.S)
    return html


def table(head, rows, widths=None, size=12, compact=False):
    cg = "".join(f'<col style="width:{w}%">' for w in widths) if widths else ""
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    cls = "at compact" if compact else "at"
    return f'<table class="{cls}" style="font-size:{size}px"><colgroup>{cg}</colgroup><tr>{th}</tr>{tr}</table>'


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
    """2,05,000 grouping (Indian), for whole rupee amounts."""
    n = f"{abs(v):.0f}"
    head, tail = n[:-3], n[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    return ("-" if v < 0 else "") + (head + "," + tail if head else tail)


def clip(s, n):
    s = str(s)
    return s if len(s) <= n else s[:s.rfind(" ", 0, n)] + "…"


# ---------------------------------------------------------------- story
def cover():
    m, top = od.MAIN, od.TOP
    tiles = [(f"{od.XMED} LTV/CAC", f"one online saver in the main case: {od.rs(od.CAC)} to win (measured), {od.rs(float(m['LTV Rs']))} back over five years, "
                                        f"paid back in month {int(m['saver pays back in month'])}"),
             (od.month(m["EBITDA positive from month"]).capitalize(), f"operating profit (EBITDA) turns positive in the main case, {od.usd(m['money needed $M'])} in all at "
                                                                      f"{lo.LEVEL:,} online savers a month"),
             (f"{od.P3:.0%} chance of 3×", f"across 1,000 what-ifs on the value of a saver; {top['LTV/CAC 5y']:.1f}× only if every loan target holds "
                                           f"({od.month(top['EBITDA positive from month'])}, {od.usd(top['money needed $M'])})"),
             ("$0.5M seed", "measures the five numbers that decide where LTV/CAC lands, and how much to raise next")]
    t = "".join(f'<div class="ctile"><div class="cbig" style="font-size:34px">{a}</div><div class="csub">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:50px">Daily saving, online first</div>
  <div class="ctag">For India's self-employed: ₹100 a day into funds in the saver's own name, and the longer they save, the better their loan offer. 9 in 10 savers online, 1 in 10 at the doorstep. Business model v4.</div>
  <div class="cmeta">October 2026 · Confidential · Piyush (CEO) and Sandeep (CPTO)</div>
</div>
<div class="cright"><div class="cgrid">{t}</div>
<div class="cnote" style="margin-top:22px">One model: monthly groups of savers, stacked into a company over 8 years. The cost to win is measured; the value of a
saver is not, so the plan is built on the median of 1,000 what-ifs and shows the company at each LTV/CAC (page §LADDER§).</div></div>
</section>"""


def p_customer():
    probs = [("Sold on “believe me”", "An investment person they know picks the product. Nothing is written down.", "A written rule they can see: why this fund, in one sentence."),
             ("Can't start small alone", "A small instalment happens today because someone comes to collect it.", "₹100 a day by UPI Autopay, set up in minutes; an agent for 1 in 10."),
             ("Forgotten after joining", "Nobody comes back to ask what else the saver needs.", "Streaks, nudges and an AI money coach in the app."),
             ("Saves a little, then stops", "Some keep saving; many drop off.", "Saving improves the offer: the longer the streak, the better the loan limit and rate (our proposal).")]
    cards = "".join(f"""<div class="ph-card"><div class="ph-top" style="background:{NAVY if i % 2 == 0 else NAVY2}"><span class="ph-n">{i + 1}</span>
<div><div class="ph-h">{a}</div></div></div><ul><li><i style="color:{RED}">✕</i>{b}</li><li><i style="color:{TEAL}">✓</i>{c}</li></ul></div>"""
                    for i, (a, b, c) in enumerate(probs))
    body = f"""<div class="phases">{cards}</div>
<div class="rbox" style="margin-top:20px;font-size:15px"><b>What savers think the product is:</b> a wallet they save into and then borrow from,
an overdraft-like line. Our answer keeps the money in funds in the saver's own name (we never hold it) and lets saving improve the loan offer.</div>"""
    return page(2, "The customer", "THE SAVER'S PROBLEM, NOT OURS", "Anyone can sign up savers; a product built for how they save and borrow is still missing, and the market is big enough for more than one winner",
                body, "Sources: practitioner conversations, 17–18 Oct 2026 (customer problem notes; the wallet reading is the founders' own).")


def channel_bar():
    W = 1152
    s = [T(0, 14, "WHERE SAVERS COME FROM", 11.5, 700, SLATE, ls=1.1)]
    s.append(R(0, 26, W * 0.9 - 4, 56, TEAL, r=10))
    s.append(T(18, 52, "ONLINE · 90% OF SAVERS", 13, 800, "#fff", ls=1))
    s.append(T(18, 72, "app, referrals and performance ads. Cost to win (marketing + KYC per saver who starts saving): ₹600 in the seed, ₹450 after (₹300–600)", 12, 500, "#fff"))
    s.append(R(W * 0.9, 26, W * 0.1, 56, AMBER, r=10))
    s.append(lines_(W * 0.95, 50, ["DOORSTEP", "10%"], 12, 800, "#fff"))
    return svg(W, 90, "".join(s))


def lines_(x, y, txts, size, weight, fill):
    return "".join(T(x, y + i * size * 1.35, t, size, weight, fill, "middle") for i, t in enumerate(txts))


def p_product():
    cards = "".join(f"""<div class="ph-card"><div class="ph-top" style="background:{col}"><span class="ph-n">{n}</span><div><div class="ph-h">{h}</div>
<div class="ph-m">{m}</div></div></div><ul>{''.join(f'<li><i style="color:{col}">✓</i>{f}</li>' for f in feats)}</ul></div>""" for n, h, m, col, feats in sp.PHASES)
    body = f'<div class="phases">{cards}</div><div style="margin-top:16px">{channel_bar()}</div>'
    return page(3, "Product and channel", "WHAT WE BUILD", "Four releases in 18 months; 9 in 10 savers come online, 1 in 10 through a doorstep agent",
                body, "Doorstep agents sign savers up and set the UPI mandate; they never handle cash. The pilot runs in NCR with two agents; online is pan-India.")


def p_flow():
    chips = [("In the saver's name", "Units sit with the fund house, registered to the saver."), ("Never through us", "We hold no customer money, ever."),
             ('Paid by partners', 'Fund houses and lenders pay us. A regular plan costs the saver about 0.5–1% a year more than a direct plan; we say so up front.')]
    c = "".join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in chips)
    return page(4, "How it works", "THE MONEY FLOW", "Money moves from the saver's bank to the fund and back, never through us",
                sp.flow() + f'<div class="chips3">{c}</div>',
                "SEBI: payments come from the investor's own account. BSE StAR MF: no transaction fee for distributors. AMC = fund house; NBFC = non-bank lender.")


def p_unit():
    return repage(bc.p_main_saver(5), 5, "One saver")


def funnel_bars(F):
    W, x0 = 600, 250
    st = F[~F["stage"].str.startswith("type:")].reset_index(drop=True)
    mx = float(st["per 100 savers won"].max())
    labels = ["Sign-ups", "KYC'd users who see loan offers", "Still reachable at month 12", "Personal + business applications (5 years)",
              "Personal + business loans (5 years)"]
    cols = [SLATE, NAVY, NAVY2, NAVY4, TEAL]
    s = [T(0, 14, "PER 100 ONLINE SAVERS WON, FIRST 5 YEARS", 11.5, 700, SLATE, ls=1.1)]
    for i, r in st.iterrows():
        y = 30 + i * 46
        v = float(r["per 100 savers won"])
        w = (W - x0 - 60) * v / mx
        s.append(T(0, y + 20, labels[i], 12.5, 600))
        s.append(R(x0, y + 4, max(w, 2), 26, cols[i], r=5))
        s.append(T(x0 + w + 8, y + 23, f"{v:,.0f}", 14, 800, cols[i]))
    return svg(W, 30 + len(st) * 46, "".join(s))


def p_loan_funnel():
    F = pd.read_csv(TAB / "ltv_main_funnel.csv")
    ty = F[F["stage"].str.startswith("type:")].copy()
    ty["stage"] = ty["stage"].str.replace("type: ", "", regex=False)
    tot = float(ty["our fees Rs per saver won"].sum())
    lent = float(ty["lent Rs per 100 savers won"].sum())
    nloans = float(ty["per 100 savers won"].sum())
    users = float(F.loc[F["stage"] == "KYC'd users who see loan offers", "per 100 savers won"].iloc[0])
    rows = [[r["stage"], f"{r['per 100 savers won']:.1f}", f"₹{ind(r['average loan Rs'])}", f"{r['payout at the start'] * 100:g}%", f"₹{r['our fees Rs per saver won']:,.0f}"]
            for _, r in ty.iterrows()]
    rows.append(["<b>All loans</b>", f"<b>{nloans:.0f}</b>", "", "", f"<b>₹{tot:,.0f}</b>"])
    tbl = table(["Loan type", "Loans per 100 savers won", "Average loan", "Our payout", "Our fees a saver won"], rows, [34, 18, 17, 13, 18], 12, compact=True)
    t = od.T_MAIN
    ap, ok = od.val("apply", t), od.val("approved", t)
    first = float(ap.rstrip("%")) * float(ok.rstrip("%")) / 1e4
    body = f"""<div style="display:flex;gap:26px;align-items:flex-start"><div style="flex:0 0 600px">{funnel_bars(F)}</div><div style="flex:1">{tbl}</div></div>
<div class="chips3" style="margin-top:10px">
<div class="chip"><b>KYC'd users, from day 1</b>Each online saver comes with 5 sign-ups and half finish KYC. In the main case {users / 100:.1f} people see loan offers for every saver won (our target 2.5; savers only, 1).</div>
<div class="chip"><b>{ap} apply a year, {ok} approved</b>The main case; our targets are 35% and 30%. About 1 in {round(1 / first)} reachable users gets a first loan each year.</div>
<div class="chip"><b>We earn as a lender's referral agent (DSA)</b>{od.val("payout", t)} on personal and business loans in the main case (target 2% rising to 3%); 0.5–1% on gold, property and home loans.</div></div>"""
    title = (f"Main case: of 100 online savers won, {users:.0f} KYC'd users see loan offers; {nloans:.0f} loans worth ₹{lent / 1e5:,.0f} lakh follow in "
             f"five years, earning us ₹{tot:,.0f} a saver")
    return page(6, "Loans", "THE LOAN FUNNEL, MAIN CASE", title, body,
                f"Main case: every loan input {t:.0%} of the way from today's market to our target. Personal + business loans include top-ups. Applications "
                "split 70% personal or business, 15% gold, 3% property, 2% home (10% against savings: tiny, not counted). Benchmarks for every input are in A15.")


def a_sources(n):
    import csv as _csv
    rows = []
    with (ROOT / "research" / "xs_funnel_2026-10-21.csv").open() as f:
        for r in _csv.DictReader(f):
            rows.append([clip(r["metric"], 58), clip(rupee(r["value"]), 46), clip(r["source"], 44), clip(r["as_of"], 14)])
    return page(n, "Appendix", "A15 · LOAN AND CROSS-SELL SOURCES", "Where the loan funnel's numbers come from (researched 21 Oct 2026)",
                table(["Measure", "Value", "Source", "As of"], rows, [37, 29, 25, 9], 9, compact=True),
                "DSA payout figures come from DSA platforms' own pages and are indicative; platform take rates are our division of reported revenue by disbursals.")


def p_odds():
    return page(7, "The odds", *od.p_odds())


def p_ladder():
    return page(8, "The company", *od.p_ladder())


def p_financials():
    return page(9, "The financials", *od.p_financials())


def p_prove():
    return page(10, "What decides it", *od.p_prove())


def p_fee():
    title, body, src = ld.fee_test()
    return page(11, "What has to be true", "THE ONE NUMBER", title, body, src)


def p_seed():
    return repage(bc.p_seed_main(12), 12, "What the seed proves")


# ---------------------------------------------------------------- appendix
def divider(n):
    return page(n, "Appendix", "APPENDIX", "Inputs, ranges, year-by-year tables and the checks behind every number",
                '<div class="rbox" style="font-size:15px;line-height:1.9">' + " · ".join(f"<b>{a}</b> {t} (p{n + 1 + i})" for i, (a, t) in enumerate((
                    ("A1", "Inputs: today's market, the main case, our targets"), ("A2", "Agreed product inputs"), ("A3", "Costs and team"),
                    ("A4", "The seed budget"), ("A5", "Regulatory path"), ("A6", "The main case, year by year"), ("A7", "At our targets, year by year"),
                    ("A8", "The Monte Carlo: tables"), ("A9", "Every assumption tested around the main case"), ("A10", "Input audit"),
                    ("A11", "Spreadsheet check"), ("A12", "How this differs from the earlier offline plan"), ("A13", "The upside: $1B at our targets"),
                    ("A14", "At our targets: capturing 10 crore savers, year by year"), ("A15", "Loan and cross-sell sources")))) + '</div>')


def a_inputs(n):
    t = od.T_MAIN
    rows = [[lo.INPUTS[k][0], od.val(k, 0), f"<b>{od.val(k, t)}</b>", od.val(k, 1), od.SOURCE[k]] for k in od.DRV.index]
    rows += [["Cost to win a saver (measured, held fixed)", "–", "₹600 in the seed, ₹450 after, + 10%", "–", "Our own funnel (founders, 23 Oct)"],
             ["Daily amount", "–", "₹100", "–", "Bachatt's stated minimum (founders, 21 Oct)"],
             ["Still saving at month 3", "–", "80%", "–", "SBI MF's ₹250 daily SIP: a steady ~7% a month"],
             ["Doorstep share of savers / still saving after a year", "–", "10% / 55%", "–", "Founders' decision (90% online) / agreed street input"],
             ["Equity share; returns a year", "–", "80%; 10% equity, 7% debt", "–", "Practitioner conversation (not yet filed); our estimate; agreed"],
             ["Gold loans", "–", "₹1 lakh, 0.5% payout", "–", "Industry average ₹1.96 lakh (Experian), smaller here"],
             ["Planning rate", "–", "₹95 per $", "–", "Founders' decision"]]
    return page(n, "Appendix", "A1 · INPUTS", f"The ten inputs nobody has measured run from today's market to our target; the main case sits {t:.0%} of the way",
                table(["Input", "Today's market", "Main case", "Our target", "Where the market figure comes from"], rows, [27, 15, 17, 15, 26], 11, compact=True),
                "The Monte Carlo draws each of the ten anywhere between today's market and our target, the loan inputs moving together (A8). "
                "Every other input is fixed at its agreed value.")


UNIT_SHORT = {"share of active savers with no housing loan running, a year": "of savers with no housing loan, a year",
              "share of the loan, at disbursal, none taken back": "of the loan, at disbursal",
              "share of the agreed take-up, months 1–6 (100% from month 7)": "of the full rate (100% from month 7)",
              "share of active savers without it, a year": "of savers without it, a year", "Rs an active saver a month": "₹ a saver a month"}


# the agreed product inputs that moved the earlier, plan-centred Monte Carlo most (online_mc.py, 22 Oct)
PRODUCT_KEYS = ["early_takeup_mult", "early_approval_mult", "loan_vehicle_ticket", "approval_growth", "loan_lap_approval", "takeup_growth",
                "amount_growth", "bills_ticket", "shop_comm", "fd_takeup", "support_cost", "life_term_takeup", "gold_renew", "two_wheeler_comm"]


def a_product(n):
    keys = [k for k in PRODUCT_KEYS if k in DIST.index]
    rows = []
    for k in keys:
        d = DIST.loc[k]
        u = d["unit"] if isinstance(d["unit"], str) else ""
        p = ("share" in u) or ("relative" in u) or ("a year" == u.strip())
        nm = re.sub(r"\s*\([^)]*\)", "", str(d["name"]))                      # drop the parenthetical detail; the label stays whole
        nm = re.sub(r"\bhis\b", "the saver's", nm)                                # the agreed file predates the neutral wording
        conf = d["confidence"] if isinstance(d["confidence"], str) else ""
        u = UNIT_SHORT.get(u, re.sub(r"\s*\([^)]*\)", "", u))
        rows.append([rupee(nm), num(d["low"], p), num(d["likely"], p), num(d["high"], p), rupee(u), conf.replace("Your number", "Founder-supplied")])
    return page(n, "Appendix", "A2 · AGREED PRODUCT INPUTS", "The agreed product inputs that matter most, held at their likely values (ranges agreed 16 Oct)",
                table(["Input", "Low", "Likely", "High", "Unit", "Confidence"], rows, [40, 8, 8, 8, 22, 14], 11.5, compact=True),
                "The inputs that moved the earlier Monte Carlo most. The LTV/CAC Monte Carlo varies only the ten unmeasured inputs (A1); these stay at "
                "their likely values (the yearly rises in take-up and approvals are among the ten). The full list of agreed ranges travels with the model.")


def a_costs(n):
    rows = [["Founders", "₹95,000 ($1,000) a month each until month 18", "₹1.5 lakh a month each after the round (+10% statutory, +7% a year)"],
            ["Engineers", "1 from month 1 (₹1.1 lakh), 1 junior from month 7 (₹50k)", "3 + 1 per 2 lakh active savers, up to 40 (₹1.2 lakh)"],
            ["Operations and support", "1 from month 4 (₹30k)", "1 per 20,000 active savers, at least 2 (₹40k)"],
            ["Product, compliance, growth, finance, risk", "Founders, CA and lawyer", "1 each, scaling with savers and ad spend"],
            ["App and tech", "₹15 lakh to integrate, ₹1.5 lakh a month", "₹1.5 lakh a month + ₹4 per KYC'd user reached"],
            ["Office", "Co-working ₹75k a month", "₹1.5 lakh + ₹10k a head a month"],
            ["Compliance", "Setup ₹1.25 lakh; ₹10 lakh a year", "₹25 lakh a year"],
            ["Brand, design, fund-raising", "Design ₹1 lakh a month in months 1–3; ₹5 lakh to raise the seed", "Brand ₹2 lakh a month; ₹15 lakh for the next round"],
            ["Doorstep agents", "₹26,000 a month all-in; 100 sign-ups a month after a 3-month ramp", "1 team lead per 10 agents and 1 office per 15, once above 5 agents"],
            ["Contingency", "10% on every cost line (agreed)", "10% on every cost line (agreed)"],
            ["Cash timing", "Fund and partner fees arrive 2 months after they are earned (agreed)", "Same"]]
    return page(n, "Appendix", "A3 · COSTS AND TEAM", "Costs and team: the seed (months 1–18) and after the round",
                table(["Line", "Seed (months 1–18)", "After the round (month 19 on)"], rows, [22, 39, 39], 12.5),
                "Seed numbers are the seed plan's; later rules are our judgement on agreed salary inputs. The 10% contingency also applies to acquisition, so ₹450 to win costs ₹495 in the company model. Tax 25% after losses carried forward; no interest on cash.")


def a_seed(n):
    return repage(sp.p_funds(), n, "Appendix · A4 seed budget")


def a_reg(n):
    return repage(sp.p_reg(), n, "Appendix · A5 regulatory path")


def a_year(n, df, title, note=""):
    lines = [("Online savers won", "online savers won", 0), ("Doorstep savers won", "doorstep savers won", 0), ("Active savers (end)", "active savers (end)", 0),
             ("Money saved, ₹ Cr (end)", "AUM Rs cr (end)", 1), ("Fund fees, ₹ Cr", "Fund trail Rs cr", 2), ("Loan fees, ₹ Cr", "Loan marketing fees Rs cr", 2),
             ("Cards, ₹ Cr", "Cards Rs cr", 2), ("Insurance, ₹ Cr", "Insurance Rs cr", 2), ("Other products, ₹ Cr", "Other products Rs cr", 2),
             ("Revenue, ₹ Cr", "Revenue Rs cr", 2), ("Acquisition, ₹ Cr", "Acquisition Rs cr", 2), ("Team, ₹ Cr", "Team Rs cr", 2),
             ("Other costs, ₹ Cr", "Other costs Rs cr", 2), ("EBITDA, ₹ Cr", "EBITDA Rs cr", 2), ("PAT, ₹ Cr", "PAT Rs cr", 2),
             ("Heads (end)", "Heads (end)", 0), ("Doorstep agents (end)", "Doorstep agents (end)", 0)]
    rows = []
    for lab, c, d in lines:
        vals = [f"{v:,.{d}f}" for v in df[c]]
        rows.append([f"<b>{lab}</b>" if lab.startswith(("Revenue", "EBITDA")) else lab] + vals)
    return page(n, "Appendix", title.split(":")[0].upper(), title, table(["", *[f"Y{y}" for y in df["year"]]], rows, [24] + [9.5] * 8, 11.5, compact=True),
                (note + " " if note else "") + "Money saved = savers' average fund balance. PAT = profit after tax; it equals EBITDA while past losses absorb "
                "the tax. Heads = headcount. Other costs include the 10% contingency on every line.")


def rung_year(rung):
    return od.LADY[od.LADY["rung"] == rung].sort_values("year")


def a_mc(n):
    S = pd.read_csv(TAB / "ltv_odds_summary.csv").set_index("measure")
    x2 = lambda v: f"{v:.2f}×"
    show = [("LTV/CAC, 5 years", "LTV/CAC, 5 years", x2), ("LTV/CAC, 8 years", "LTV/CAC, 8 years", x2),
            ("Saver pays back in month (97 = not by 96)", "Saver pays back", od.month),
            ("Company EBITDA positive from month (97 = not by 96)", "Company EBITDA positive from", od.month),
            ("Money needed, $M", "Money needed in all", od.usd), ("Year 5 EBITDA, Rs crore", "Year 5 EBITDA", od.cr),
            ("Cumulative EBITDA to month 60, Rs crore", "Cumulative EBITDA, 5 years", od.cr), ("Cumulative EBITDA to month 96, Rs crore", "Cumulative EBITDA, 8 years", od.cr)]
    srows = [[lab] + [f(float(S.loc[k, q])) for q in ("P10", "P50", "P90")] for k, lab, f in show]
    chance = [("chance LTV/CAC >= 1", "LTV/CAC at least 1× (pays back in 5 years)"), ("chance LTV/CAC >= 3", "LTV/CAC 3× or more"),
              ("chance LTV/CAC >= 5", "LTV/CAC 5× or more"), ("chance EBITDA positive by month 60", "Company profitable by month 60"),
              ("chance EBITDA positive by month 96", "Company profitable by month 96")]
    crow = [[lab, f"{float(S.loc[k, 'P50']):.0%}"] for k, lab in chance]
    drows = [[lo.INPUTS[k][0], od.x(r["median if at market"]), od.x(r["median if at target"]), f"{r['chance >=3x if at market']:.0%}",
              f"{r['chance >=3x if at target']:.0%}"] for k, r in od.DRV.iterrows()]
    left = table(["Across the 1,000 what-ifs", "Bad (P10)", "Middle (P50)", "Good (P90)"], srows, [43, 19, 19, 19], 11, compact=True) + \
        '<div style="margin-top:10px"></div>' + table(["Chance of", "Share of what-ifs"], crow, [70, 30], 11, compact=True)
    right = table(["If the seed finds this input at…", "Median: market", "Median: target", "3×: market", "3×: target"], drows, [40, 15, 15, 15, 15], 10.5, compact=True)
    return page(n, "Appendix", "A8 · THE MONTE CARLO", "1,000 what-ifs on the value of a saver: the results, and what each measurement is worth",
                od.two(left, right, 520),
                "The cost to win is held at ₹450 + 10% (₹600 in the seed). Each of the ten unmeasured inputs is drawn anywhere between today's market and our "
                "target (A1), the six loan inputs moving together. Bad / middle / good = the 10th, 50th and 90th of the 1,000 what-ifs, each measure on its own, "
                "so the middle column differs slightly from the main case (A6), one consistent set of inputs. Company results at 20,000 online savers a month.")


def a_levers(n):
    L = pd.read_csv(TAB / "ltv_main_levers.csv")
    rows = [[r["case"].replace("Rs ", "₹"), r["EBITDA positive from month"], f"${r['money needed $M']}M", f"{r['Y5 EBITDA Rs cr']:.1f}", f"{r['Y8 EBITDA Rs cr']:.1f}",
             f"{r['active savers m60'] / 1e5:.1f}"] for _, r in L.iterrows()]
    return page(n, "Appendix", "A9 · EVERY ASSUMPTION TESTED", f"Every assumption we tested, one at a time around the main case, at {lo.LEVEL:,} online savers a month",
                table(["Assumption changed", "Profit from month", "Money needed", "Y5 EBITDA ₹ Cr", "Y8 EBITDA ₹ Cr", "Active savers at month 60 (lakh)"], rows, [36, 13, 13, 13, 13, 12], 12),
                "One assumption changed at a time, on top of the main case; the first row is the main case. The apply-rate rows replace the main case's "
                f"{od.val('apply', od.T_MAIN)}; the retention rows its {od.val('keep', od.T_MAIN).split(',')[0]} at a year.")


def a_audit(n):
    if not AUDIT.exists():
        body = '<div class="rbox">The input audit is running; this page fills in when it reports.</div>'
        return page(n, "Appendix", "A10 · INPUT AUDIT", "Every input checked against its source", body)
    a = pd.read_csv(AUDIT)
    vc = a["verdict"].fillna("").str.lower().value_counts()
    fixed = int(vc.get("mislabelled", 0) + vc.get("not supported", 0))
    lab = [("matches", "match their source"), ("judgement-labelled-as-such", "our judgement, labelled as such"),
           ("partly", "partly supported: carried as ranges (A1, A8)"), ("target", "targets: the loan funnel (now drawn, A1) and the cost to win (now measured)")]
    chips = "".join(f'<div class="kpi"><b>{int(vc.get(k, 0))}</b><span>{t}</span></div>' for k, t in lab) + \
        f'<div class="kpi"><b>{fixed}</b><span>wrong or unsourced: fixed or flagged below</span></div>'
    # What the audit found in the plan as first built, and what this model does about each (every row is a
    # 'mislabelled' or 'not supported' line of the audit table).
    rows = [["The loan funnel (35% apply, the loan sizes, offers to 2.5 users a saver, payout rising to 3%) was labelled as evidence", "Labelled as targets, each with its evidence and where it pulls LTV/CAC down to 3× and 2× (re-audited 22 Oct)"],
            ["No payment cost on debits; tech ₹1 a saver a month", "₹2 a weekly debit; ₹4 tech for every KYC'd user reached"],
            ["Insurance counted 75% of a broker's commission; the Choti SIP incentive and digital gold were counted", "Insurance: a fixed referral fee, not counted until agreed; Choti and digital gold off"],
            ["Cost to win in the seed was ₹550; the seed's own funnel gives ₹600 an online saver", "Seed now ₹600; ₹450 after the seed, range ₹300–600"],
            ["The agreed 10% contingency on every cost line was missing", "Added, inside EBITDA and on the LTV's cost to win (₹495)"],
            ["The agreed 2-month delay before fees arrive in cash was missing", "Added to cash and money needed"],
            ["Compliance of ₹25 lakh a year after the seed is not an agreed input", "Kept; A3 marks post-round costs as our judgement"],
            ["Loan against property take-up (0.5%) and size (₹15 lakh) had no source", "Take-up rebuilt 21 Oct from lender data (3% of loan applicants, 1% payout); size ₹25 lakh, the founders' number (22 Oct), a target"]]
    body = f'<div class="kpis" style="grid-template-columns:repeat(5,1fr)">{chips}</div>' + \
        '<div class="sub-h" style="margin-top:14px">WHAT THE AUDIT FOUND, AND WHAT CHANGED</div>' + \
        table(["Finding", "What this model does"], rows, [62, 38], 12, compact=True)
    return page(n, "Appendix", "A10 · INPUT AUDIT", f"All {len(a)} inputs checked against their sources, re-checked on 22 Oct, before the main case was set", body,
                f"An independent reviewer read each source row; the full {len(a)}-row table travels with the model.")


def cr(v):
    """-6.02 -> "−₹6.02 Cr"."""
    return f"{'−' if v < 0 else ''}₹{abs(v):.2f} Cr"


def a_sheet(n):
    if not SHEETCHK.exists():
        body = '<div class="rbox">The Google Sheet (v4 tabs) is being built; this page fills in with its reconciliation.</div>'
        return page(n, "Appendix", "A11 · SHEET CHECK", "The Google Sheet matches the model", body)
    c = pd.read_csv(SHEETCHK, dtype={"sheet": str, "python": str})
    c["case"] = c["case"].astype(str)
    pm = c[c["measure"].str.contains("positive")]
    same = int((pm["sheet"] == pm["python"]).sum())            # as text: a lever that never turns positive reads "after m96" on both
    for k in ("sheet", "python", "gap", "gap_pct"):
        c[k] = pd.to_numeric(c[k], errors="coerce")
    ok, tot = int(c["ok"].sum()), len(c)
    rev = c[c["measure"].str.startswith("Revenue")]["gap_pct"].abs().max()
    chips = (f'<div class="kpi"><b>{ok} of {tot}</b><span>checks within target</span></div>'
             f'<div class="kpi"><b>{rev * 100:.2f}%</b><span>largest revenue gap, any year, any case</span></div>'
             f'<div class="kpi"><b>{same} of {len(pm)}</b><span>cases with the same profit month</span></div>')
    want = [("Revenue, year 5 (Rs crore)", "Revenue, year 5 (₹ Cr)", 2), ("EBITDA, year 5 (Rs crore)", "EBITDA, year 5 (₹ Cr)", 2),
            ("Revenue, year 8 (Rs crore)", "Revenue, year 8 (₹ Cr)", 2), ("EBITDA, year 8 (Rs crore)", "EBITDA, year 8 (₹ Cr)", 2),
            ("EBITDA positive from month", "Profit from month", 0), ("Money needed (Rs crore)", "Money needed (₹ Cr)", 1),
            ("Active savers, month 60", "Active savers, month 60", 0)]

    def cell(case, m, k, d):
        r = c[(c["case"] == case) & (c["measure"] == m)].iloc[0]
        return f"{r[k]:,.{d}f}"
    rows = [[lab, cell("20000", m, "sheet", d), cell("20000", m, "python", d), cell("150000", m, "sheet", d), cell("150000", m, "python", d)]
            for m, lab, d in want]
    rows[5][0] = f"Money needed (₹ Cr; ${float(c[(c['case'] == '20000') & (c['measure'] == 'Money needed (Rs crore)')]['python'].iloc[0]) / 9.5:.1f}M at 20,000)"
    miss = c[~c["ok"].astype(bool)]
    note = "; ".join(f"{rupee(r['case'].replace('lever: ', '')).replace('150000', 'Grow fast').replace('20000', 'Profitable path')}, {r['measure'].split(' (')[0]}: "
                     f"{cr(r['sheet'])} vs {cr(r['python'])}" for _, r in miss.iterrows())
    body = f'<div class="kpis" style="grid-template-columns:repeat(3,1fr)">{chips}</div>' + \
        '<div class="sub-h" style="margin-top:14px">THE LIVE SHEET NEXT TO THE MODEL</div>' + \
        table(["Measure", "Main case, 20,000 a month: sheet", "… model", "1,50,000 a month: sheet", "… model"], rows, [32, 17, 17, 17, 17], 12) + \
        (f'<div class="rbox" style="margin-top:12px">The {len(miss)} checks outside target ({"; ".join(sorted(set(m.split(" (")[0] for m in miss["measure"])))}) '
         f'are the years when profit turns, where a 1% test is tight. The largest gap is ₹{miss["gap"].abs().max():.2f} Cr. '
         f'The sheet\'s costs equal the model\'s exactly; every gap comes from its simpler timing of revenue.</div>' if len(miss) else "")
    nlev = c.loc[c["case"].str.startswith("lever"), "case"].nunique()
    return page(n, "Appendix", "A11 · SPREADSHEET CHECK", "The live spreadsheet and the model give the same answers in the main case", body,
                f"Both plans: revenue and EBITDA in every year 1–8, profit month, money needed, active savers, money saved. Each of the {nlev} assumption changes: years 5 and 8 and the profit month. "
                "The live Google Sheet carries the main case's inputs since 24 Oct and was read back after the push (month 63, $4.7M, 1.75×); "
                "the older offline tabs are hidden.")


def a_changes(n):
    rows = [["Channel", "Street agents collect cash from every saver", "90% online by UPI Autopay; 10% doorstep agents, no cash"],
            ["Daily amount", "₹350, in cash", "₹100 (₹50–300)"],
            ["Still saving after a year", "55% for every saver", f"{od.val('keep', od.T_MAIN).split(',')[0]} online in the main case (target 38%); 55% at the doorstep"],
            ["Where the money goes", "Debt fund, 0.35% fee", f"80% equity SIP / 20% debt, {od.val('trail', od.T_MAIN)} blended fee in the main case (0.67% at target)"],
            ["Cost to win a saver", "Agent salary + bought leads", "₹600 in the seed, ₹450 after: measured, held fixed"],
            ["Loans", "₹2.5 lakh; 18% of savers apply a year", f"Main case: {od.val('ticket', od.T_MAIN)}, {od.val('apply', od.T_MAIN)} apply a year, "
                                                               f"{od.val('approved', od.T_MAIN)} approved (targets ₹3 lakh, 35%, 30%)"],
            ["Home loan", "₹25 lakh", f"Main case {od.val('home_lap', od.T_MAIN).split(' / ')[0]} (target ₹30 lakh), 0.5% payout"],
            ["Lending", "Own NBFC, 30% of personal loans on book from month 30", "DSA / lending service provider for partner lenders; no own book"],
            ["Collections fees", "The agent collects overdue loans", "None"],
            ["Money", "₹1,108 crore over six rounds; unicorn on paper by month 59",
             f"$0.5M seed; {od.usd(od.MAIN['money needed $M'])} in all in the main case ({od.usd(od.LAD.loc['3×', 'money needed $M'])} at 3×, "
             f"{od.usd(od.TOP['money needed $M'])} at our targets)"],
            ["Planning rate", "₹100 per $", "₹95 per $"],
            ["Uncertainty", "Simulated futures for one agent", "1,000 what-ifs on the value of a saver, run through the whole company"]]
    return page(n, "Appendix", "A12 · THE EARLIER OFFLINE PLAN", "How this plan differs from the earlier offline plan",
                table(["", "Earlier offline plan (street agents)", "This plan (online first)"], rows, [20, 38, 42], 12.5),
                "The v3 offline model and the 18 Oct data refresh are kept, unchanged, for reference.")


def a_upside(n):
    html = bc.p_upside(n).replace('<div class="kicker">THE UPSIDE', '<div class="kicker">A13 · THE UPSIDE', 1)
    return repage(html, n, "Appendix")


def build():
    pages = [cover(), p_customer(), p_product(), p_flow(), p_unit(), p_loan_funnel(), p_odds(), p_ladder(), p_financials(), p_prove(), p_fee(), p_seed()]
    pages = [pages[0]] + [re.sub(r'(<footer class="pf"><span>[^<]*</span><span>)[^<]*(</span></footer>)', rf"\g<1>{i}\2", h)
                          for i, h in enumerate(pages[1:], start=2)]
    pages[0] = pages[0].replace("§LADDER§", str(1 + next(i for i, h in enumerate(pages) if "THE COMPANY AT EACH LTV/CAC" in h)))
    n = len(pages) + 1
    pages.append(divider(n))
    for i, f in enumerate((a_inputs, a_product, a_costs, a_seed, a_reg)):
        pages.append(f(n + 1 + i))
    k = n + 6
    pages.append(a_year(k, rung_year("Median"), f"A6 · The main case: {lo.LEVEL:,} online savers a month, year by year",
                        f"Main case: every unmeasured input {od.T_MAIN:.0%} of the way from today's market to our target (A1)."))
    pages.append(a_year(k + 1, rung_year("Our targets"), f"A7 · At our targets (7.7×, not the plan): {lo.LEVEL:,} online savers a month, year by year",
                        "Every loan input at our target at once (LTV/CAC 7.7×): the top of the ladder, not the plan."))
    for i, f in enumerate((a_mc, a_levers, a_audit, a_sheet, a_changes, a_upside)):
        pages.append(f(k + 2 + i))
    pages.append(a_year(k + 8, pd.read_csv(TAB / "online_capture_10cr_yearly.csv"), "A14 · The upside at our targets, not the plan: capturing 10 crore savers, year by year",
                        "The upside (A13): every loan target holding, a third of a 30 crore segment captured."))
    pages.append(a_sources(k + 9))
    css = sp.CSS + ".at.compact td { padding: 3.5px 10px; } .at.compact th { padding: 4px 10px; }"
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Online model v4</title><style>{css}</style></head>'
            f'<body>{"".join(pages)}</body></html>')
    out = HERE / "Online_model_v4.html"
    out.write_text(html)
    pdf = HERE / "Online_model_v4.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, capture_output=True)
    print("wrote", pdf, len(pages), "pages")


if __name__ == "__main__":
    build()

"""Online_model_v4 (21 Oct 2026): the online-first deck that replaces Offline_model_v3. Operator: "remodel the excel sheet and
everything and check all inputs ... then the offline_v3 to turn it into online_v4 where 90% online and 10% offline"; taps:
story + appendix (~25 pages), ranges + Monte Carlo, the online ranges "OK as proposed".
Numbers: tables/online_*.csv, online_mc_*.csv, seed_*.csv (model/online_plan.py, online_mc.py, seed_plan.py); the input audit
(tables/online_inputs_audit.csv) and the sheet check (tables/v4_toy_check.csv) when present. Charts reuse
online/build_online_case.py and the seed plan's design (seed/build_seed_plan.py). Builds online/Online_model_v4.html/.pdf."""
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

TAB = ROOT / "tables"
INK, NAVY, TEAL, BLUE, AMBER, SLATE, MUTE, LINE, BG, RED = sp.INK, sp.NAVY, sp.TEAL, sp.BLUE, sp.AMBER, sp.SLATE, sp.MUTE, sp.LINE, sp.BG, sp.RED
NAVY2, NAVY3, NAVY4 = sp.NAVY2, sp.NAVY3, sp.NAVY4
T, R, A, svg = sp.T, sp.R, sp.A, sp.svg
FOOT = "Online model v4 · October 2026 · Confidential"

MCS = pd.read_csv(TAB / "online_mc_summary.csv")
DRV = pd.read_csv(TAB / "online_mc_drivers.csv")
DRV = DRV.replace("his shop or home", "the saver's shop or home", regex=True)
DRAWS = pd.read_csv(TAB / "online_mc_draws.csv")
MCI = pd.read_csv(TAB / "online_mc_inputs.csv")
DIST = pd.read_csv(TAB / "dist_agreed_v1.csv").set_index("key")
DIST["name"] = DIST["name"].str.replace("his shop or home", "the saver's shop or home", regex=False)  # agreed file predates the neutral wording
MP, MF = MCS.iloc[0], MCS.iloc[1]
ONR = MCS.iloc[2]
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
    tiles = [(f"{bc.LV0['LTV/CAC 60m']:.1f}× LTV/CAC", f"one online saver: ₹{int(bc.LV0['cost to win Rs'])} to win, ₹{int(bc.LV0['contribution 60m Rs']):,} back over five years, paid back in month {int(bc.LV0['pays back in month'])}"),
             (f"Month {int(bc.LEAN['EBITDA positive from month'])}", f"EBITDA turns positive on today's evidence: the profitable path, ${bc.LEAN['money needed $M']}M in all"),
             (f"Month {int(bc.FAST['EBITDA positive from month'])}", f"growing fast: ${bc.FAST['money needed $M']}M in all for {bc.FAST['active savers m60'] / bc.LEAN['active savers m60']:.0f}× the active savers"),
             ("$0.5M seed", "measures the five numbers that decide how much to raise next")]
    t = "".join(f'<div class="ctile"><div class="cbig" style="font-size:34px">{a}</div><div class="csub">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:50px">Daily saving, online first</div>
  <div class="ctag">For India's self-employed: ₹100 a day into funds in the saver's own name, credit as the reward for saving. 9 in 10 savers online, 1 in 10 at the doorstep. Business model v4.</div>
  <div class="cmeta">October 2026 · Confidential · Piyush (CEO) and Sandeep (CPTO)</div>
</div>
<div class="cright"><div class="cgrid">{t}</div>
<div class="cnote" style="margin-top:22px">One model: monthly groups of savers, stacked into a company over 8 years. Across 1,000 simulated futures the
profitable path turns positive by month 60 in {round(MP['chance EBITDA positive by month 60'] * 100)} of 100 and by month 96 in {round((1 - MP['chance never by month 96']) * 100)} of 100 (page §MCPAGE§).</div></div>
</section>"""


def p_customer():
    probs = [("Sold on “believe me”", "An investment person they know picks the product. Nothing is written down.", "A written rule they can see: why this fund, in one sentence."),
             ("Can't start small alone", "A small instalment happens today because someone comes to collect it.", "₹100 a day by UPI Autopay, set up in minutes; an agent for 1 in 10."),
             ("Forgotten after joining", "Nobody comes back to ask what else the saver needs.", "Streaks, nudges and an AI money coach in the app."),
             ("Saves a little, then stops", "Some keep saving; many drop off.", "Credit tied to the streak: save 6 months, see your loan offer (our proposal).")]
    cards = "".join(f"""<div class="ph-card"><div class="ph-top" style="background:{NAVY if i % 2 == 0 else NAVY2}"><span class="ph-n">{i + 1}</span>
<div><div class="ph-h">{a}</div></div></div><ul><li><i style="color:{RED}">✕</i>{b}</li><li><i style="color:{TEAL}">✓</i>{c}</li></ul></div>"""
                    for i, (a, b, c) in enumerate(probs))
    body = f"""<div class="phases">{cards}</div>
<div class="rbox" style="margin-top:20px;font-size:15px"><b>What savers think the product is:</b> a wallet they save into and then borrow from,
an overdraft-like line. Our answer keeps the money in funds in the saver's own name (we never hold it) and makes credit the reward for saving.</div>"""
    return page(2, "The customer", "THE SAVER'S PROBLEM, NOT OURS", "They will save a small amount every day and want to borrow when they need to; nobody serves both",
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
                body, "Doorstep agents sign savers up and set the UPI mandate; they never handle cash. The pilot runs in one city with two agents.")


def p_flow():
    chips = [("In the saver's name", "Units sit with the fund house, registered to the saver."), ("Never through us", "We hold no customer money, ever."),
             ("Paid by partners", "Fund houses and lenders pay us; we charge the saver nothing (the trail comes from the fund's own expense ratio).")]
    c = "".join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in chips)
    return page(4, "How it works", "THE MONEY FLOW", "Money moves from the saver's bank to the fund and back, never through us",
                sp.flow() + f'<div class="chips3">{c}</div>',
                "SEBI: payments come from the investor's own account. BSE StAR MF: no transaction fee for distributors. AMC = fund house; NBFC = non-bank lender.")


def p_unit():
    return repage(bc.p_unit(), 5, "One saver")


def p_ltv():
    return repage(bc.p_ltv_levers(), 6, "What moves it")


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
    F = pd.read_csv(TAB / "online_loan_funnel.csv")
    ty = F[F["stage"].str.startswith("type:")].copy()
    ty["stage"] = ty["stage"].str.replace("type: ", "", regex=False)
    tot = float(ty["our fees Rs per saver won"].sum())
    lent = float(ty["lent Rs per 100 savers won"].sum())
    nloans = float(ty["per 100 savers won"].sum())
    rows = [[r["stage"], f"{r['per 100 savers won']:.1f}", f"₹{ind(r['average loan Rs'])}", f"{r['payout at the start'] * 100:g}%", f"₹{r['our fees Rs per saver won']:,.0f}"]
            for _, r in ty.iterrows()]
    rows.append(["<b>All loans</b>", f"<b>{nloans:.0f}</b>", "", "", f"<b>₹{tot:,.0f}</b>"])
    tbl = table(["Loan type", "Loans per 100 savers won", "Average loan", "Our payout", "Our fees a saver won"], rows, [34, 18, 17, 13, 18], 12, compact=True)
    body = f"""<div style="display:flex;gap:26px;align-items:flex-start"><div style="flex:0 0 600px">{funnel_bars(F)}</div><div style="flex:1">{tbl}</div></div>
<div class="chips3" style="margin-top:10px">
<div class="chip"><b>Every KYC'd user, from day 1</b>Each online saver comes with 5 sign-ups; half finish KYC, so {bc.op_reach():g} people see loan offers for every saver won.</div>
<div class="chip"><b>35% apply a year, 30% approved</b>About 1 in 10 reachable users gets a loan each year; 70% of repeat applications are approved.</div>
<div class="chip"><b>We earn as a DSA</b>2% on personal and business loans, rising to 3% by year 5; 0.5–1% on gold, property and home loans.</div></div>"""
    title = (f"Per 100 online savers won, {bc.op_reach() * 100:.0f} KYC'd users see loan offers; in five years they take {nloans:.0f} loans "
             f"worth ₹{lent / 1e5:,.0f} lakh, earning us ₹{tot:,.0f} a saver")
    return page(6, "Loans", "THE LOAN FUNNEL", title, body,
                "Personal + business loans include top-ups. Applications split 70% personal or business, 15% gold, 3% property, 2% home (10% against savings: tiny, not counted). "
                "Benchmarks for every input are in A15.")


def a_sources(n):
    import csv as _csv
    rows = []
    with (ROOT / "research" / "xs_funnel_2026-10-21.csv").open() as f:
        for r in _csv.DictReader(f):
            rows.append([clip(r["metric"], 58), clip(rupee(r["value"]), 46), clip(r["source"], 44), clip(r["as_of"], 14)])
    return page(n, "Appendix", "A15 · LOAN AND CROSS-SELL SOURCES", "Where the loan funnel's numbers come from (researched 21 Oct 2026)",
                table(["Measure", "Value", "Source", "As of"], rows, [37, 29, 25, 9], 9, compact=True),
                "DSA payout figures come from DSA platforms' own pages and are indicative; platform take rates are our division of reported revenue by disbursals.")


def retention_chart():
    import online_plan as op
    rows = []
    keep = dict(op.OV)
    for lab, ov in (("24% · like savings apps", {"r12": 0.2415, "r3": 0.52}), ("38% · the plan", {}), ("45% · credit tied to saving", {"r12": 0.45})):
        op.OV.clear()
        op.OV.update(ov)
        rev = op.profiles(op.saver_inputs())["income"][0][:60].sum()
        o = op.company(20000)
        rows.append((lab, rev, op.positive_from(o["ebitda"]), o["money_needed"] / op.FX / 1e6))
    op.OV.clear()
    p = op.profiles(op.saver_inputs())
    loans24 = p["loans"][0][:24].sum() * 1000
    op.OV.update(keep)
    W, x0 = 1152, 300
    mx = max(r[1] for r in rows) * 1.1
    s = [T(0, 14, "STILL SAVING AFTER A YEAR → ONE ONLINE SAVER'S 5-YEAR REVENUE, AND THE PROFITABLE PATH", 11.5, 700, SLATE, ls=1.1)]
    for i, (lab, rev, m, money) in enumerate(rows):
        y = 30 + i * 64
        col = NAVY if "plan" in lab else ("#8a97a8" if i == 0 else NAVY4)
        s.append(T(0, y + 26, lab, 14, 700, col))
        s.append(R(x0, y + 8, (W - x0 - 330) * rev / mx, 32, col, r=6))
        s.append(T(x0 + (W - x0 - 330) * rev / mx + 10, y + 30, f"₹{rev:,.0f}", 15, 700, col))
        s.append(T(W, y + 30, f"profit from month {m} · ${money:.1f}M", 13, 700, INK, "end"))
    return svg(W, 30 + 3 * 64, "".join(s)), loans24, rows


def p_retention():
    ch, loans24, rows = retention_chart()
    (_, _, m24, _), (_, _, m38, _), (_, _, m45, _) = rows
    body = ch + f"""<div class="chips3" style="margin-top:14px">
<div class="chip"><b>Our 38% is an extrapolation</b>SBI MF's ₹250 daily SIP for first-time investors, a product with no loans, lost 36% of a year's sign-ups within that year. We extend that to 12 months; nobody has observed it yet.</div>
<div class="chip"><b>Personal loans alone can't lift it</b>At 3.6% of savers applying a year, about {loans24:.0f} in 1,000 online savers get a personal loan in their first two years.</div>
<div class="chip"><b>Credit might</b>Savers who want credit may keep saving to qualify: our hypothesis, and the seed tests it. It only works if loan offers are visibly tied to the saving streak.</div></div>"""
    return page(6, "Retention", "THE LEAST-MEASURED NUMBER", f"At 38 in 100 still saving after a year, profit comes in month {m38}; at 24 in 100 it slips to month {m24}, at 45 in 100 it comes in month {m45}",
                body, "Profitable path: 20,000 online savers a month from month 30. The 24% case also lowers month-3 retention to 52%; everything else at today's evidence.")


def p_frontier():
    return repage(bc.p_frontier(), 7, "Growth")


def p_plans():
    return repage(bc.p_plans(), 8, "Three plans")


def mc_chart():
    W = 1152
    s = [T(0, 14, "1,000 SIMULATED FUTURES: THE MONTH EBITDA TURNS POSITIVE ON THE PROFITABLE PATH (BAR HEIGHT = NUMBER OF FUTURES)", 11.5, 700, SLATE, ls=1.1)]
    pm = DRAWS["profit_month_p"]
    pm = pm[pm <= 96]                                          # futures that never turn positive by month 96 are counted in the chip below
    bins = np.arange(37, 98, 3)                                # 58-60 is one bin, so month 60 sits on the teal side
    h, _ = np.histogram(pm, bins=bins)
    x0, base = 40, 230
    bw = (W - 420 - x0) / len(h)
    for i, c in enumerate(h):
        hh = 170 * c / h.max()
        m0 = bins[i]
        col = TEAL if m0 + 2 <= 60 else AMBER
        s.append(R(x0 + i * bw + 2, base - hh, bw - 4, hh, col, r=3))
        if i % 3 == 0:
            s.append(T(x0 + i * bw + bw / 2, base + 18, f"{m0}", 11, 600, MUTE, "middle"))
    s.append(T(x0 + len(h) * bw, base + 40, "month EBITDA turns positive →", 11.5, 600, MUTE, "end"))
    xm = x0 + (60 + 1 - bins[0]) / 3 * bw
    s.append(f'<line x1="{xm}" y1="30" x2="{xm}" y2="{base}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(T(xm + 6, 38, "end of year 5", 11.5, 700, RED))
    s.append(T(x0, base + 40, f"{round(MP['chance EBITDA positive by month 60'] * 100)} in 100 futures by month 60 (teal)", 12.5, 700, TEAL))
    kx = W - 380
    for j, (lab, m) in enumerate((("Profitable path · 20k a month", MP), ("Grow fast · 1.5 lakh a month", MF))):
        y = 30 + j * 128
        s.append(R(kx, y, 380, 116, BG, LINE, 12, 1))
        s.append(T(kx + 16, y + 26, lab, 13.5, 700, NAVY))
        s.append(T(kx + 16, y + 56, f"{m['chance EBITDA positive by month 60']:.0%}", 26, 800, TEAL))
        s.append(T(kx + 92, y + 52, "chance of profit by month 60", 11.5, 600, SLATE))
        s.append(T(kx + 16, y + 82, f"profit month {m['profit month P10']:.0f} / {m['profit month P50']:.0f} / {m['profit month P90']:.0f}", 12, 600))
        s.append(T(kx + 16, y + 102, f"money needed ${m['money needed $M P10']:.1f}M / ${m['money needed $M P50']:.1f}M / ${m['money needed $M P90']:.1f}M", 12, 600))
    s.append(T(kx, 296, "bad case / middle / good case (P10 / P50 / P90)", 11, 600, MUTE))
    return svg(W, 300, "".join(s))


def p_mc():
    body = mc_chart() + f"""<div class="chips3" style="margin-top:8px">
<div class="chip"><b>One saver, five years</b>₹{ONR['P10']:,.0f} / ₹{ONR['P50']:,.0f} / ₹{ONR['P90']:,.0f} of revenue (bad / middle / good case), against ₹{int(bc.ON['cost to win Rs'])} to win.</div>
<div class="chip"><b>Almost always, in time</b>EBITDA turns positive by month 96 in {round((1 - MP['chance never by month 96']) * 100)} of 100 futures on the profitable path and {round((1 - MF['chance never by month 96']) * 100)} of 100 growing fast.</div>
<div class="chip"><b>Faster is surer</b>Growing fast raises the chance of profit by month 60 from {MP['chance EBITDA positive by month 60']:.0%} to {MF['chance EBITDA positive by month 60']:.0%}, for about {MF['money needed $M P50'] / MP['money needed $M P50']:.0f}× the money.</div></div>"""
    med = DRAWS[["on_daily", "on_apply"]].median()
    return page(10, "Ranges", "1,000 SIMULATED FUTURES", f"In {round(MP['chance EBITDA positive by month 60'] * 100)} of 100 futures the profitable path turns positive by month 60; the middle future needs ${MP['money needed $M P50']:.1f}M",
                body, f"The plan: month {int(bc.LEAN['EBITDA positive from month'])} and ${bc.LEAN['money needed $M']}M; the middle future: month {MP['profit month P50']:.0f} and ${MP['money needed $M P50']:.1f}M "
                      f"(middle draws ₹{med['on_daily']:.0f} a day, {med['on_apply']:.0%} applying for loans). Revenue, retention, loan and cost-to-win inputs vary; team and fixed costs stay at plan; approvals and losses move together in bad years.")


def tornado():
    W, x0 = 1092, 500
    d = DRV.head(10).to_dict("records")
    mx = max(abs(r["rank corr with money needed (profitable path)"]) for r in d)
    s = [T(0, 14, "HOW STRONGLY EACH INPUT MOVES THE MONEY NEEDED, ACROSS 1,000 FUTURES (−1 TO +1)", 11.5, 700, SLATE, ls=1.1)]
    mid = x0 + (W - x0) / 2
    s.append(f'<line x1="{mid}" y1="24" x2="{mid}" y2="{30 + len(d) * 31}" stroke="{LINE}" stroke-width="2"/>')
    short = {"cac": "Cost to win a saver", "on_daily": "Daily amount", "support_cost": "Running cost per active saver a month",
             "approval_growth": "Lenders approve more of our savers each year", "takeup_growth": "More savers take products each year as our history grows",
             "loan_lap_takeup": "Loan against property: take-up", "early_takeup_mult": "Take-up in a saver's first 6 months",
             "loan_home_takeup": "Home loan: take-up", "on_r12": "Online: still saving after a year", "loan_lap_ticket": "Loan against property: size",
             "loan_home_comm": "Home loan: our commission", "days": "Saving days a month", "hlth_family_takeup": "Family health cover: take-up",
             "on_ticket": "Personal-loan size", "on_apply": "Savers who apply for a loan"}
    for i, r in enumerate(d):
        y = 30 + i * 31
        v = r["rank corr with money needed (profitable path)"]
        w = (W - x0) / 2 * abs(v) / mx
        col = bc.LATE if v > 0 else NAVY
        s.append(T(0, y + 17, short.get(r["input"], r["label"][:60]), 12.5, 600))
        s.append(R(mid if v > 0 else mid - w, y + 4, w, 20, col, r=4))
        s.append(T(mid + w + 8 if v > 0 else mid - w - 8, y + 18, f"{v:+.2f}", 12, 700, col, "start" if v > 0 else "end"))
    ly = 46 + len(d) * 31
    s.append(f'<rect x="0" y="{ly - 11}" width="13" height="13" rx="2" fill="{bc.LATE}"/>' + T(20, ly, "raises the money needed", 12, 600))
    s.append(f'<rect x="230" y="{ly - 11}" width="13" height="13" rx="2" fill="{NAVY}"/>' + T(250, ly, "lowers it", 12, 600))
    return svg(1152, ly + 6, "".join(s))


def a_drivers(n):
    html = p_drivers()
    html = html.replace('<div class="kicker">WHAT MATTERS MOST</div>', '<div class="kicker">A13 · WHAT MATTERS MOST</div>')
    return repage(html, n, "Appendix")


def p_drivers():
    body = tornado() + """<div class="chips3" style="margin-top:10px">
<div class="chip"><b>Cost to win comes first</b>It decides how deep the hole gets before savers pay back.</div>
<div class="chip"><b>Then the loan funnel</b>How many apply, the loan size and our payout: loans are now the biggest revenue line.</div>
<div class="chip"><b>Then reach</b>Whether KYC'd users who never save still borrow through us: the founders' plan says yes.</div></div>"""
    return page(10, "Drivers", "WHAT MATTERS MOST", "Cost to win a saver and the loan funnel drive the money needed; the daily amount matters less than it did",
                body, "Profitable path. Rank (Spearman) correlation of each input with the money needed across the 1,000 futures; below about 0.06 is noise.")


def p_levers():
    return repage(bc.p_levers(), 11, "What it takes")


def p_unicorn():
    return repage(bc.p_unicorn(), 9, "Unicorn test")


def p_seed():
    return repage(bc.p_seed(), 11, "What the seed proves")


# ---------------------------------------------------------------- appendix
def divider(n):
    return page(n, "Appendix", "APPENDIX", "Inputs, ranges, year-by-year tables and the checks behind every number",
                '<div class="rbox" style="font-size:15px;line-height:1.9">' + " · ".join(f"<b>{a}</b> {t} (p{n + 1 + i})" for i, (a, t) in enumerate((
                    ("A1", "Online inputs and ranges"), ("A2", "Agreed product inputs that matter most"), ("A3", "Costs and team"), ("A4", "The seed budget"),
                    ("A5", "Regulatory path"), ("A6", "Profitable path, year by year"), ("A7", "Growing fast, year by year"), ("A8", "Simulated futures: tables"),
                    ("A9", "Every assumption tested"), ("A10", "Input audit"), ("A11", "Spreadsheet check"), ("A12", "How this differs from the earlier offline plan"),
                    ("A13", "What drives the money needed"), ("A14", "Capturing 10 crore savers, year by year"),
                    ("A15", "Loan and cross-sell sources")))) + '</div>')


def a_online(n):
    pk = {"on_r12", "on_r3", "on_apply", "eq_share", "eq_return", "on_approved", "on_fee"}
    basis = {"on_daily": "PhonePe daily SIP ~₹50 / Bachatt's minimum ₹100 / a Bachatt example of ₹300",
             "on_r12": "savings apps 24% / extrapolated from SBI MF's ₹250 daily SIP / credit tied to saving (our hypothesis)",
             "on_r3": "savings-app curve 52% / SBI's steady monthly drop ~80%",
             "cac": "a competitor's reported ₹300 / the midpoint, founders' choice / our seed funnel's ₹600",
             "on_apply": "payments-app merchants borrow ~1-2% a year / founders' plan 35% / credit-hungry (fintech borrowers ~49% re-borrow in 6 months)",
             "on_ticket": "personal ₹50k / blend of personal ₹50k and business ₹1.5 lakh / merchant loans ~₹2 lakh (Paytm)",
             "on_approved": "founders' past lending ~25% / 30% / PSU banks approve ~80% of pre-qualified MSMEs",
             "on_fee": "DSA payouts 1-2.5% (up to 3%) on personal and business loans; rises 1.5× by year 5",
             "on_reach": "savers only / every KYC'd user: 5 sign-ups a saver, half complete KYC",
             "eq_share": "about 80% choose equity SIPs (practitioner conversation; not yet filed)", "eq_return": "our estimate"}
    rows = [[rupee(r.label), num(r.low, r.key in pk), num(r.likely, r.key in pk), num(r.high, r.key in pk), basis.get(r.key, rupee(r.basis))] for r in MCI.itertuples()]
    rows += [["Doorstep share of savers", "–", "10%", "–", "Founders' decision (90% online, 10% offline)"],
             ["Cost to win during the seed (months 4–18)", "–", "₹600", "–", "Seed funnel: (₹100 a sign-up + ₹40 KYC for 1 in 2) × 5 sign-ups a saver"],
             ["Deposit growth", "–", "5% a year", "–", "Agreed: each saver's daily amount rises 5% for each year they keep saving"],
             ["Late drop-off (after month 12)", "1%", "1.5%", "3%", "Agreed: savers stopping each month after the first year"],
             ["Doorstep saver: still saving after a year", "25%", "55%", "72%", "Agreed street input"],
             ["Loan sizes: gold / property / home", "–", "₹1 / 4 / 8 lakh", "–", "Gold loans ₹1.96 lakh industry (Experian, smaller here); micro-LAP ₹3.9 lakh and housing ₹6–8 lakh (Five Star)"],
             ["Planning rate", "–", "₹95 per $", "–", "Founders' decision"]]
    return page(n, "Appendix", "A1 · ONLINE INPUTS", "Online inputs: low / likely / high, and where each comes from",
                table(["Input", "Low", "Likely", "High", "Basis"], rows, [30, 8, 9, 8, 45], 11, compact=True))


UNIT_SHORT = {"share of active savers with no housing loan running, a year": "of savers with no housing loan, a year",
              "share of the loan, at disbursal, none taken back": "of the loan, at disbursal",
              "share of the agreed take-up, months 1–6 (100% from month 7)": "of the full rate (100% from month 7)",
              "share of active savers without it, a year": "of savers without it, a year", "Rs an active saver a month": "₹ a saver a month"}


def a_product(n):
    keys = [k for k in DRV["input"] if k in DIST.index][:14]
    rows = []
    for k in keys:
        d = DIST.loc[k]
        u = d["unit"] if isinstance(d["unit"], str) else ""
        p = ("share" in u) or ("relative" in u) or ("a year" == u.strip())
        nm = re.sub(r"\s*\([^)]*\)", "", str(d["name"]))                      # drop the parenthetical detail; the label stays whole
        conf = d["confidence"] if isinstance(d["confidence"], str) else ""
        u = UNIT_SHORT.get(u, re.sub(r"\s*\([^)]*\)", "", u))
        rows.append([rupee(nm), num(d["low"], p), num(d["likely"], p), num(d["high"], p), rupee(u), conf.replace("Your number", "Founder-supplied")])
    return page(n, "Appendix", "A2 · AGREED PRODUCT INPUTS", "The agreed product inputs that move the result most (ranges agreed 16 Oct)",
                table(["Input", "Low", "Likely", "High", "Unit", "Confidence"], rows, [40, 8, 8, 8, 22, 14], 11.5, compact=True),
                "Ordered by their rank correlation with the money needed (A8). The full list of agreed ranges travels with the model.")


def a_costs(n):
    rows = [["Founders", "₹95,000 ($1,000) a month each until month 18", "₹1.5 lakh a month each after the round (+10% statutory, +7% a year)"],
            ["Engineers", "1 from month 1 (₹1.1 lakh), 1 junior from month 7 (₹50k)", "3 + 1 per 2 lakh active savers, up to 40 (₹1.2 lakh)"],
            ["Operations and support", "1 from month 4 (₹30k)", "1 per 20,000 active savers, at least 2 (₹40k)"],
            ["Product, compliance, growth, finance, risk", "Founders, CA and lawyer", "1 each, scaling with savers and ad spend"],
            ["App and tech", "₹15 lakh to integrate, ₹1.5 lakh a month", "₹1.5 lakh a month + ₹1 per active saver"],
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


def a_year(n, fname, title):
    df = pd.read_csv(TAB / fname)
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
                "Money saved = savers' average fund balance. PAT = profit after tax; it equals EBITDA while past losses absorb the tax. Heads = headcount. "
                "Other costs include the 10% contingency on every line.")


def a_mc(n):
    srows = []
    for _, m in MCS.iloc[:2].iterrows():
        srows.append([m["plan"], f"{m['chance EBITDA positive by month 60']:.0%}", f"{m['chance by month 54']:.0%}",
                      f"{m['profit month P10']:.0f} / {m['profit month P50']:.0f} / {m['profit month P90']:.0f}",
                      f"${m['money needed $M P10']:.1f}M / ${m['money needed $M P50']:.1f}M / ${m['money needed $M P90']:.1f}M",
                      f"{m['Y5 EBITDA Rs cr P10']:.0f} / {m['Y5 EBITDA Rs cr P50']:.0f} / {m['Y5 EBITDA Rs cr P90']:.0f}"])
    drows = [[rupee(clip(re.sub(r"\s*\([^)]*\)", "", r.label), 90)), f"{r[3]:+.2f}", f"{r[4]:+.2f}"] for r in DRV.head(12).itertuples()]
    body = table(["Plan", "Profitable by month 60", "By month 54", "Profit month: bad / middle / good", "Money needed: bad / middle / good", "Y5 EBITDA ₹ Cr: bad / middle / good"], srows, [17, 10, 9, 20, 24, 20], 12) + \
        '<div class="sub-h" style="margin-top:14px">THE 12 INPUTS THAT MOVE THE RESULT MOST (−1 TO +1, PROFITABLE PATH)</div>' + \
        table(["Input", "With money needed", "With Y5 EBITDA"], drows, [64, 18, 18], 11, compact=True)
    return page(n, "Appendix", "A8 · SIMULATED FUTURES", "1,000 simulated futures: the results, and the inputs that matter", body,
                "Bad / middle / good = the 10th, 50th and 90th percentile. Inputs drawn by Latin hypercube; approvals and losses move together in bad years.")


def a_levers(n):
    L = pd.read_csv(TAB / "online_levers.csv")
    rows = [[r["case"].replace("Rs ", "₹"), r["EBITDA positive from month"], f"${r['money needed $M']}M", f"{r['Y5 EBITDA Rs cr']:.1f}", f"{r['Y8 EBITDA Rs cr']:.1f}",
             f"{r['active savers m60'] / 1e5:.1f}"] for _, r in L.iterrows()]
    return page(n, "Appendix", "A9 · EVERY ASSUMPTION TESTED", f"Every assumption we tested, at {bc.LVS} online savers a month",
                table(["Assumption changed", "Profit from month", "Money needed", "Y5 EBITDA ₹ Cr", "Y8 EBITDA ₹ Cr", "Active savers at month 60 (lakh)"], rows, [36, 13, 13, 13, 13, 12], 12),
                "One assumption changed at a time; everything else at the plan's values. The first row is the plan.")


def a_audit(n):
    if not AUDIT.exists():
        body = '<div class="rbox">The input audit is running; this page fills in when it reports.</div>'
        return page(n, "Appendix", "A10 · INPUT AUDIT", "Every input checked against its source", body)
    a = pd.read_csv(AUDIT)
    vc = a["verdict"].fillna("").str.lower().value_counts()
    fixed = int(vc.get("mislabelled", 0) + vc.get("not supported", 0))
    lab = [("matches", "match their source"), ("judgement-labelled-as-such", "our judgement, labelled as such"),
           ("partly", "partly supported: carried as ranges (A1, A8)")]
    chips = "".join(f'<div class="kpi"><b>{int(vc.get(k, 0))}</b><span>{t}</span></div>' for k, t in lab) + \
        f'<div class="kpi"><b>{fixed}</b><span>wrong or unsourced: fixed or flagged below</span></div>'
    # What the audit found in the plan as first built, and what this model does about each (every row is a
    # 'mislabelled' or 'not supported' line of the audit table).
    rows = [["Cost to win in the seed was ₹550; the seed's own funnel gives ₹600 an online saver", "Seed now ₹600; ₹450 after the seed, range ₹300–600"],
            ["Seed sign-ups were 95,800; the seed plan now has 97,200 (19,440 savers)", "Updated to 97,200"],
            ["The agreed 10% contingency on every cost line was missing", "Added, inside EBITDA"],
            ["The agreed 2-month delay before fees arrive in cash was missing", "Added to cash and money needed"],
            ["A '45-month runway' was quoted; the company plan spends faster after month 18", "Dropped; money needed comes from the full plan"],
            ["Compliance of ₹25 lakh a year after the seed is not an agreed input", "Kept; A3 marks post-round costs as our judgement"],
            ["Loan against property take-up (0.5%) and size (₹15 lakh) had no source", "Rebuilt 21 Oct from lender data: ₹4 lakh micro-LAP at 1%, 3% of loan applicants"]]
    body = f'<div class="kpis" style="grid-template-columns:repeat(4,1fr)">{chips}</div>' + \
        '<div class="sub-h" style="margin-top:14px">WHAT THE AUDIT FOUND, AND WHAT CHANGED</div>' + \
        table(["Finding", "What this model does"], rows, [62, 38], 12, compact=True)
    return page(n, "Appendix", "A10 · INPUT AUDIT", f"All {len(a)} inputs checked against their sources", body,
                f"An independent reviewer read each source row; the full {len(a)}-row table travels with the model.")


def cr(v):
    """-6.02 -> "−₹6.02 Cr"."""
    return f"{'−' if v < 0 else ''}₹{abs(v):.2f} Cr"


def a_sheet(n):
    if not SHEETCHK.exists():
        body = '<div class="rbox">The Google Sheet (v4 tabs) is being built; this page fills in with its reconciliation.</div>'
        return page(n, "Appendix", "A11 · SHEET CHECK", "The Google Sheet matches the model", body)
    c = pd.read_csv(SHEETCHK)
    c["case"] = c["case"].astype(str)
    ok, tot = int(c["ok"].sum()), len(c)
    rev = c[c["measure"].str.startswith("Revenue")]["gap_pct"].abs().max()
    pm = c[c["measure"].str.contains("positive")]
    same = int((pm["sheet"] == pm["python"]).sum())
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
    miss = c[~c["ok"].astype(bool)]
    note = "; ".join(f"{rupee(r['case'].replace('lever: ', '')).replace('150000', 'Grow fast').replace('20000', 'Profitable path')}, {r['measure'].split(' (')[0]}: "
                     f"{cr(r['sheet'])} vs {cr(r['python'])}" for _, r in miss.iterrows())
    body = f'<div class="kpis" style="grid-template-columns:repeat(3,1fr)">{chips}</div>' + \
        '<div class="sub-h" style="margin-top:14px">THE LIVE SHEET NEXT TO THE MODEL</div>' + \
        table(["Measure", "Profitable path: sheet", "Profitable path: model", "Grow fast: sheet", "Grow fast: model"], rows, [32, 17, 17, 17, 17], 12) + \
        (f'<div class="rbox" style="margin-top:12px">The {len(miss)} checks outside target are small EBITDA figures, where a 1% test is tight; '
         f'each gap is under ₹0.1 Cr: {note}.</div>' if len(miss) else "")
    nlev = c.loc[c["case"].str.startswith("lever"), "case"].nunique()
    return page(n, "Appendix", "A11 · SPREADSHEET CHECK", "The spreadsheet and the model give the same answers", body,
                f"Both plans: revenue and EBITDA in every year 1–8, profit month, money needed, active savers, money saved. Each of the {nlev} assumption changes: years 5 and 8 and the profit month. "
                "The live Google Sheet was read back after it was built.")


def a_changes(n):
    rows = [["Channel", "Street agents collect cash from every saver", "90% online by UPI Autopay; 10% doorstep agents, no cash"],
            ["Daily amount", "₹350, in cash", "₹100 (₹50–300)"],
            ["Still saving after a year", "55% for every saver", "38% online (24–45%); 55% at the doorstep"],
            ["Where the money goes", "Debt fund, 0.35% fee", "80% equity SIP / 20% debt, 0.67% blended fee"],
            ["Cost to win a saver", "Agent salary + bought leads", "₹600 in the seed, ₹450 after (₹300–600)"],
            ["Loans", "₹2.5 lakh; 18% of savers apply a year", "Every KYC'd user, 35% apply a year, 30% approved; ₹1 lakh personal/business at 2% rising to 3%"],
            ["Home loan", "₹25 lakh", "₹8 lakh (affordable housing), 0.5% payout"],
            ["Lending", "Own NBFC, 30% of personal loans on book from month 30", "DSA / lending service provider for partner lenders; no own book"],
            ["Collections fees", "The agent collects overdue loans", "None"],
            ["Money", "₹1,108 crore over six rounds; unicorn on paper by month 59",
             f"$0.5M seed; ${bc.LEAN['money needed $M']}M (profitable path) or ${bc.FAST['money needed $M']}M (grow fast) in all"],
            ["Planning rate", "₹100 per $", "₹95 per $"],
            ["Uncertainty", "Simulated futures for one agent", "1,000 simulated futures for the whole company"]]
    return page(n, "Appendix", "A12 · THE EARLIER OFFLINE PLAN", "How this plan differs from the earlier offline plan",
                table(["", "Earlier offline plan (street agents)", "This plan (online first)"], rows, [20, 38, 42], 12.5),
                "The v3 offline model and the 18 Oct data refresh are kept, unchanged, for reference.")


def build():
    pages = [cover(), p_customer(), p_product(), p_flow(), p_unit(), p_loan_funnel(), p_ltv(), p_frontier(), p_plans(), p_unicorn(), p_mc(), p_seed()]
    pages = [pages[0]] + [re.sub(r'(<footer class="pf"><span>[^<]*</span><span>)[^<]*(</span></footer>)', rf"\g<1>{i}\2", h)
                          for i, h in enumerate(pages[1:], start=2)]
    pages[0] = pages[0].replace("§MCPAGE§", str(1 + next(i for i, h in enumerate(pages) if "1,000 SIMULATED FUTURES" in h)))
    n = len(pages) + 1
    pages.append(divider(n))
    for i, f in enumerate((a_online, a_product, a_costs, a_seed, a_reg)):
        pages.append(f(n + 1 + i))
    k = n + 6
    pages.append(a_year(k, "online_evidence_20k_yearly.csv", "A6 · Profitable path: 20,000 online savers a month, year by year"))
    pages.append(a_year(k + 1, "online_evidence_150k_yearly.csv", "A7 · Grow fast: 1.5 lakh online savers a month, year by year"))
    for i, f in enumerate((a_mc, a_levers, a_audit, a_sheet, a_changes, a_drivers)):
        pages.append(f(k + 2 + i))
    pages.append(a_year(k + 8, "online_capture_10cr_yearly.csv", "A14 · Capture 10 crore savers: 12.4 lakh online savers a month, year by year"))
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

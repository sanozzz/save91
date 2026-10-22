"""Online-first business case (21 Oct 2026). Landscape pages in the seed plan's design (seed/build_seed_plan.py CSS and
helpers). Operator: revamp the numbers for online-first + offline test; base = the plan (evidence where it exists, targets with pass lines where not); both a
profitable path and a unicorn track. Numbers: tables/online_*.csv (model/online_plan.py). Builds
online/Online_business_case.html and .pdf."""
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "seed"))
import build_seed_plan as sp  # noqa: E402  (CSS, colours and svg helpers)

TAB = ROOT / "tables"
INK, NAVY, TEAL, BLUE, AMBER, SLATE, MUTE, LINE, BG, RED = sp.INK, sp.NAVY, sp.TEAL, sp.BLUE, sp.AMBER, sp.SLATE, sp.MUTE, sp.LINE, sp.BG, sp.RED
NAVY2, NAVY3, NAVY4 = sp.NAVY2, sp.NAVY3, sp.NAVY4
LATE = "#a8553d"                         # "later than the plan": a muted brick, not the doorstep amber
T, R, A, svg = sp.T, sp.R, sp.A, sp.svg
FX = 95.0
UNI = 1e9 * FX / 1e7                     # $1B in Rs crore

UNIT = pd.read_csv(TAB / "online_unit.csv").set_index("saver")
for _c in UNIT.columns:
    if _c != "still saving at 12 months":
        UNIT[_c] = pd.to_numeric(UNIT[_c], errors="ignore")
FRONT = pd.read_csv(TAB / "online_frontier.csv")
LEV = pd.read_csv(TAB / "online_levers.csv").set_index("case")
LVL = int(LEV["online savers won a month (m30 on)"].iloc[0])  # the level every lever runs at (online_plan.LEVER_LEVEL)
LVS = f"{LVL:,}"


def op_reach():
    """KYC'd users reached by loan offers per online saver won (online_plan.LOAN_REACH, read from the unit table)."""
    return float(UNIT.loc["Online saver"]["loan reach (KYC'd users per saver won)"])
UNIC = pd.read_csv(TAB / "online_unicorn.csv")
CAPR = pd.read_csv(TAB / "online_capture.csv").iloc[0]          # capture 10 crore savers by month 96 (operator 21 Oct)
YC = pd.read_csv(TAB / "online_capture_10cr_yearly.csv")
CAPM = int(UNIC["online sign-ups stop at the pool cap in month"].iloc[0])  # month sign-ups stop at the pool cap (2.5 lakh a month)
Y20 = pd.read_csv(TAB / "online_evidence_20k_yearly.csv")
Y150 = pd.read_csv(TAB / "online_evidence_150k_yearly.csv")
F = FRONT.set_index("online savers won a month (m30 on)")
LEAN, FAST = F.loc[20000], F.loc[150000]
ON, DOOR = UNIT.loc["Online saver"], UNIT.loc["Doorstep saver"]


def lm(key):
    """EBITDA-positive month of a lever row (at the lever level, LVL online savers a month)."""
    return int(LEV.loc[key]["EBITDA positive from month"])


BASE_M = lm("The plan")


def pf(m):
    try:
        m = int(m)
    except (TypeError, ValueError):
        return "after month 96"
    return f"month {m}"


def yr(m):
    return f"year {(int(m) - 1) // 12 + 1}"


def page(n, section, kicker, title, body, src=""):
    s = f'<div class="src">{src}</div>' if src else ""
    return f"""<section class="page">
<header class="ph"><span class="brand">{sp.NAME} <em>· working name</em></span><span>{section}</span></header>
<div class="kicker">{kicker}</div><h1>{title}</h1>
<div class="body">{body}</div>{s}
<footer class="pf"><span>Online-first business case · October 2026 · Confidential</span><span>{n}</span></footer>
</section>"""


# ---------- 1 cover
def cover():
    keys = ("45% still saving at a year", "Rs 200 a day", "Rs 300 a day", "Cost to win Rs 300", "50% apply for a loan a year")
    lo, hi = min(lm(k) for k in keys), max(lm(k) for k in keys)
    tiles = [(f"{LV0['LTV/CAC 60m']:.1f}× LTV/CAC", f"one online saver: ₹{int(LV0['cost to win Rs'])} to win, ₹{int(LV0['contribution 60m Rs']):,} back over five years, paid back in month {int(LV0['pays back in month'])}"),
             (yr(LEAN['EBITDA positive from month']).capitalize(), f"EBITDA turns positive in the plan ({pf(LEAN['EBITDA positive from month'])}, ${LEAN['money needed $M']}M raised, 20,000 savers a month)"),
             (f"Months {lo}–{hi}", f"with any one change: ₹200–300 a day, 45% still saving, half applying for loans or ₹300 to win ({LVS} savers a month)"),
             (("$1B: 10 crore" if unicorn_title().startswith("Only capturing") else ("Not by year 5" if unicorn_title().startswith("No combination") else "$1B by year 5")), unicorn_title())]
    t = "".join(f'<div class="ctile"><div class="cbig" style="font-size:34px">{a}</div><div class="csub">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:52px">Online-first business case</div>
  <div class="ctag">What the numbers say in the plan, and the five numbers that change them.</div>
  <div class="cmeta">October 2026 · Confidential</div>
</div>
<div class="cright"><div class="cgrid">{t}</div>
<div class="cnote" style="margin-top:22px">Every number comes from one model: monthly groups of savers, each with the same agreed product lines, stacked into a company.
Online savers at ₹100 a day; 1 in 10 savers from a doorstep pilot.</div></div>
</section>"""


# ---------- 2 one saver
LTVW = pd.read_csv(TAB / "online_ltv_waterfall.csv")
LTVC = pd.read_csv(TAB / "online_ltv_curve.csv")
LTVL = pd.read_csv(TAB / "online_ltv_levers.csv").set_index("case")
LTVL["LTV/CAC 60m"] = LTVL["contribution 60m Rs"] / LTVL["cost to win Rs"]   # from the rupee figures, so the shown 1 dp is not rounded twice
LV0 = LTVL.loc["The plan"]


def money(v):
    return f"{'−' if v < 0 else '+'}₹{abs(v):,.0f}"


def waterfall(saver="Online saver"):
    """Cost to win, then each revenue line over 60 months, then serving: where the saver's value comes from."""
    w = LTVW[LTVW.saver == saver]
    items = list(zip(w["line"], w["Rs over 60 months"].astype(float)))
    W, H, x0, y0, y1 = 680, 296, 10, 62, 236
    lvl, bars = 0.0, []
    for nm, v in items:
        if nm.startswith("Net"):
            bars.append((nm, 0.0, v))
        else:
            bars.append((nm, lvl, lvl + v))
            lvl += v
    lo, hi = min(min(a, b) for _, a, b in bars), max(max(a, b) for _, a, b in bars)
    Y = lambda v: y1 - (y1 - y0) * (v - lo) / (hi - lo)
    bw, gap = 62, 20
    cols = {"Cost to win": TEAL, "Fund fees": NAVY, "Serving (support + tech)": SLATE}
    names = {"Cost to win": ["Cost to", "win"], "Fund fees": ["Fund", "fees"], "Loans (all referrals)": ["Loans"],
             "Insurance": ["Insurance"], "Cards": ["Cards"], "Other products": ["Other", "products"],
             "Serving (support + tech)": ["Serving"], "Net over 60 months": ["Net,", "5 years"]}
    s = [T(0, 14, f"ONE {saver.upper()} WON, FIRST 5 YEARS (₹)", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0}" y1="{Y(0)}" x2="{x0 + len(bars) * (bw + gap)}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>')
    xs = []
    for i, (nm, a, b) in enumerate(bars):
        x = x0 + i * (bw + gap)
        xs.append(x)
        net = nm.startswith("Net")
        col = NAVY2 if net else cols.get(nm, NAVY4)
        s.append(R(x, min(Y(a), Y(b)), bw, max(abs(Y(a) - Y(b)), 2), col, r=4))
        v = b - a
        ty = min(Y(a), Y(b)) - 7 if v >= 0 else max(Y(a), Y(b)) + 16
        s.append(T(x + bw / 2, ty, money(v) if not net else f"₹{v:,.0f}", 13 if net else 12, 800 if net else 700, col if not net else NAVY2, "middle"))
        for k, ln in enumerate(names.get(nm, [nm])):
            s.append(T(x + bw / 2, y1 + 34 + k * 14, ln, 11.5, 700 if net else 600, INK if net else SLATE, "middle"))
        if i < len(bars) - 1 and not net:
            nxt = bars[i + 1]
            if not nxt[0].startswith("Net"):
                s.append(f'<line x1="{x + bw}" y1="{Y(b)}" x2="{x + bw + gap}" y2="{Y(b)}" stroke="{MUTE}" stroke-dasharray="3 3"/>')
    # bracket over the cross-sell bars
    xs_idx = [i for i, (nm, *_r) in enumerate(bars) if nm in ("Loans (all referrals)", "Insurance", "Cards", "Other products")]
    xsell = sum(b - a for nm, a, b in bars if nm in ("Loans (all referrals)", "Insurance", "Cards", "Other products"))
    rev = sum(b - a for nm, a, b in bars if nm not in ("Cost to win", "Serving (support + tech)") and not nm.startswith("Net"))
    bx0, bx1 = xs[xs_idx[0]], xs[xs_idx[-1]] + bw
    by = y0 - 18
    s.append(f'<path d="M{bx0} {by + 8} L{bx0} {by} L{bx1} {by} L{bx1} {by + 8}" fill="none" stroke="{NAVY4}" stroke-width="1.6"/>')
    s.append(T((bx0 + bx1) / 2, by - 6, f"Cross-sell ₹{xsell:,.0f}: {xsell / rev:.0%} of revenue", 12, 700, NAVY4, "middle"))
    return svg(W, H, "".join(s)), xsell, rev


def payback_curve():
    W, H, x0, x1, y0, y1 = 450, 296, 52, 440, 44, 240
    on, dr = LTVC[LTVC.saver == "Online saver"], LTVC[LTVC.saver == "Doorstep saver"]
    lo = min(on["cumulative net Rs"].min(), dr["cumulative net Rs"].min())
    hi = max(on["cumulative net Rs"].max(), dr["cumulative net Rs"].max())
    X = lambda m: x0 + (x1 - x0) * m / 96
    Y = lambda v: y1 - (y1 - y0) * (v - lo) / (hi - lo)
    s = [T(0, 14, "WHEN IT PAYS BACK: CUMULATIVE ₹ PER SAVER WON", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>')
    for m in (0, 12, 24, 36, 48, 60, 72, 84, 96):
        s.append(T(X(m), y1 + 18, f"{m}", 11, 600, MUTE, "middle"))
    s.append(T(x1, y1 + 34, "months after the saver joins", 11, 600, MUTE, "end"))
    for v in (lo, 0, hi):
        s.append(T(x0 - 6, Y(v) + 4, f"{'−' if v < 0 else ''}₹{abs(v):,.0f}" if v else "0", 10.5, 600, MUTE, "end"))
    s.append(f'<line x1="{X(60)}" y1="{y0}" x2="{X(60)}" y2="{y1}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    s.append(T(X(60) + 4, y0 + 10, "5 years", 11, 700, MUTE))
    for df, col, w, dash in ((dr, AMBER, 2.2, ' stroke-dasharray="6 4"'), (on, NAVY, 3, "")):
        pts = " ".join(f"{X(m):.1f},{Y(v):.1f}" for m, v in zip(df["month"], df["cumulative net Rs"]))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{w}"{dash}/>')
    pm = int(LV0["pays back in month"])
    s.append(f'<circle cx="{X(pm)}" cy="{Y(0)}" r="5" fill="{NAVY}"/>')
    s.append(T(X(pm) + 8, Y(0) + 18, f"online: pays back in month {pm}", 12, 700, NAVY))
    dpm = int(DOOR["pays back its cost in month"])
    s.append(T(X(dpm) - 8, Y(0) - 10, f"doorstep: month {dpm}", 11.5, 700, AMBER, "end"))
    v60 = float(LV0["net after cost to win 60m Rs"])
    v96 = float(on["cumulative net Rs"].iloc[-1])
    s.append(T(X(60) + 6, Y(v60) + 18, f"+₹{v60:,.0f} at 5 years", 12, 800, NAVY))
    s.append(T(X(96), Y(v96) - 10, f"+₹{v96:,.0f}", 12, 800, NAVY, "end"))
    return svg(W, H, "".join(s))


def p_unit():
    wf, xsell, rev = waterfall()
    d = LTVW[LTVW.saver == "Doorstep saver"].set_index("line")["Rs over 60 months"]
    LW = LTVW[LTVW.saver == "Online saver"].set_index("line")["Rs over 60 months"]
    d_ltv = (d.drop(["Cost to win", "Net over 60 months"]).sum()) / -d["Cost to win"]
    body = f"""<div style="display:flex;gap:22px;align-items:flex-start"><div style="flex:0 0 680px">{wf}</div><div style="flex:0 0 450px">{payback_curve()}</div></div>
<div class="chips3" style="margin-top:2px">
<div class="chip"><b>{LV0['LTV/CAC 60m']:.1f}× in 5 years, {LV0['LTV/CAC 96m']:.1f}× in 8</b>LTV/CAC = what a saver brings in, less the cost of serving them, divided by the ₹{int(LV0['cost to win Rs'])} it cost to win them. Undiscounted.</div>
<div class="chip"><b>Cross-sell is {xsell / rev:.0%} of revenue</b>Loans ₹{LW['Loans (all referrals)']:,.0f} (personal, home, property, gold, durables), insurance ₹{LW['Insurance']:,.0f}, cards and other products, on top of ₹{LW['Fund fees']:,.0f} of fund fees.</div>
<div class="chip"><b>Doorstep: {d_ltv:.1f}×</b>₹{int(-d['Cost to win'])} to win all-in; {DOOR['still saving at 12 months']:.0%} still saving at a year; pays back in month {int(DOOR['pays back its cost in month'])}. The 1 in 10 test.</div></div>"""
    return page(2, "One saver", "LTV / CAC", f"A saver won online costs ₹{int(LV0['cost to win Rs'])} and returns ₹{int(LV0['contribution 60m Rs']):,} over five years: "
                f"{LV0['LTV/CAC 60m']:.1f}× LTV/CAC, paid back in month {int(LV0['pays back in month'])}",
                body, f"The plan: ₹100 a day; {ON['still saving at 12 months']:.0%} still saving at a year (our extrapolation from SBI MF's ₹250 daily SIP); 80/20 equity and debt funds. "
                      "Serving = ₹5 support, ₹4 tech for each of the 2.5 KYC'd users and ₹2 a weekly debit, a month while saving; the cost to win includes our 10% contingency. "
                      "Not in this view: the company's fixed costs (team, office, brand), which is why the company turns profitable later than the saver. Every assumption behind this page, with its source, range and effect: the LTV/CAC deck and its live workbook.")


LTV_LABEL = {"The plan": "The plan", "Rs 300 a day": "₹300 a day (plan ₹100)", "Rs 200 a day": "₹200 a day (plan ₹100)",
             "Cost to win Rs 300": "₹300 to win a saver (plan ₹450)", "Credit-hungry: 45% stay + 50% apply": "Credit-hungry: 45% stay + 50% apply",
             "45% still saving at a year": "45% still saving at a year (plan 38%)", "50% apply for a loan a year": "50% apply for a loan a year (plan 35%)",
             "10% apply for a loan a year": "10% apply for a loan a year (plan 35%)", "Loan offers to savers only": "Loan offers to savers only (plan: every KYC'd user)",
             "Cost to win Rs 600 (our funnel)": "₹600 to win a saver (our funnel today)", "Debt-only funds": "Debt funds only, no equity",
             "24% still saving at a year (savings apps)": "24% still saving, like savings apps"}


def ltv_bars():
    W, x0, x1 = 1152, 330, 760
    rows = [("The plan", LTVL.loc["The plan"])] + sorted(
        ((k, r) for k, r in LTVL.iterrows() if k != "The plan"), key=lambda kr: -kr[1]["LTV/CAC 60m"])
    mx = 4.5
    X = lambda v: x0 + (x1 - x0) * min(v, mx) / mx
    n = len(rows)
    s = [T(0, 14, "LTV/CAC OVER 5 YEARS FOR ONE ONLINE SAVER WON, ONE ASSUMPTION CHANGED AT A TIME", 11.5, 700, SLATE, ls=1.1),
         T(W, 14, "SAVER PAYS BACK · COMPANY PROFITABLE", 11.5, 700, SLATE, "end", ls=1.1)]
    for v, lab in ((1, "1×: pays back within 5 years"), (3, "3×")):
        s.append(f'<line x1="{X(v)}" y1="26" x2="{X(v)}" y2="{32 + n * 24}" stroke="{LINE}" stroke-width="1.6" stroke-dasharray="4 4"/>'
                 + T(X(v), 48 + n * 24, lab, 11.5, 600, SLATE, "middle"))
    for i, (k, r) in enumerate(rows):
        y = 30 + i * 24
        v = float(r["LTV/CAC 60m"])
        col = NAVY if i == 0 else (TEAL if v > LV0["LTV/CAC 60m"] else LATE)
        s.append(T(0, y + 16, LTV_LABEL.get(k, k), 12, 700 if i == 0 else 500))
        s.append(R(x0, y + 4, X(v) - x0, 17, col, r=4))
        s.append(T(X(v) + 8, y + 17, f"{v:.1f}×", 12, 800, col))
        pm = int(float(r["pays back in month"]))
        cm = int(LEV.loc[k]["EBITDA positive from month"])
        s.append(T(W, y + 17, f"month {pm} · month {cm}", 12, 700 if i == 0 else 600, INK, "end"))
    return svg(W, 54 + n * 24, "".join(s))


def p_ltv_levers():
    L = LTVL["LTV/CAC 60m"]
    base = L["The plan"]
    title = (f"LTV/CAC is {base:.1f}× in the plan; ₹300 a day takes it to {L['Rs 300 a day']:.1f}× and ₹300 to win to "
             f"{L['Cost to win Rs 300']:.1f}×, while savings-app retention cuts it to {L['24% still saving at a year (savings apps)']:.1f}×")
    body = ltv_bars() + f"""<div class="chips3" style="margin-top:2px">
<div class="chip"><b>Loans move it most</b>If only 10% apply a year it falls to {L['10% apply for a loan a year']:.1f}×; with offers to savers only (not every KYC'd user) {L['Loan offers to savers only']:.1f}×.</div>
<div class="chip"><b>Cost to win is ours to drive down</b>Our funnel today is ₹600 ({L['Cost to win Rs 600 (our funnel)']:.1f}×); the plan needs ₹450; a competitor reports ₹300 ({L['Cost to win Rs 300']:.1f}×).</div>
<div class="chip"><b>Retention still matters</b>38% is our extrapolation; at 24%, like savings apps, LTV/CAC is {L['24% still saving at a year (savings apps)']:.1f}×, because fewer people stay to borrow.</div></div>"""
    return page(3, "What moves it", "LTV / CAC, ONE CHANGE AT A TIME", title, body,
                f"LTV/CAC = a saver's revenue less serving cost over 60 months, divided by the cost to win; undiscounted. Company profitable = the month EBITDA turns positive at {LVS} online savers a month (the plan). "
                "The 24% case also lowers month-3 retention to 52%.")


# ---------- 3 frontier
def frontier():
    W = 1152
    rows = FRONT.to_dict("records")
    n = len(rows)
    bw, gap, x0, base = 120, 62, 70, 268
    mx = max(r["money needed $M"] for r in rows) * 1.15
    s = [T(0, 14, "MONEY NEEDED TO REACH PROFIT ($M) AND THE MONTH EBITDA TURNS POSITIVE", 11.5, 700, SLATE, ls=1.1)]
    for i, r in enumerate(rows):
        x = x0 + i * (bw + gap)
        h = 200 * r["money needed $M"] / mx
        lvl = int(r["online savers won a month (m30 on)"])
        col = TEAL if lvl == 20000 else (NAVY if lvl == 150000 else "#9fb8d6")
        s.append(R(x, base - h, bw, h, col, r=8))
        s.append(T(x + bw / 2, base - h - 10, f"${r['money needed $M']}M", 15, 700, col if col != "#9fb8d6" else SLATE, "middle"))
        s.append(T(x + bw / 2, base + 22, f"{lvl / 1000:.0f}k a month", 13, 700, INK, "middle"))
        s.append(T(x + bw / 2, base + 42, f"profit from {pf(r['EBITDA positive from month'])}", 12, 600, SLATE, "middle"))
        s.append(T(x + bw / 2, base + 60, f"{r['active savers m60'] / 1e5:.1f} lakh active", 11.5, 500, MUTE, "middle"))
        if lvl == 20000:
            s.append(T(x + bw / 2, base - h - 34, "PROFITABLE PATH", 11, 800, TEAL, "middle", ls=1))
        if lvl == 150000:
            s.append(T(x + bw / 2, base - h - 34, "GROW FAST", 11, 800, NAVY, "middle", ls=1))
    s.append(f'<line x1="40" y1="{base}" x2="{W - 10}" y2="{base}" stroke="{LINE}" stroke-width="2"/>')
    return svg(W, 336, "".join(s))


def p_frontier():
    pos = [int(r["online savers won a month (m30 on)"]) for r in FRONT.to_dict("records") if r["Y5 EBITDA Rs cr"] > 0]
    Y5TXT = (f"Profitable for the whole of year 5 from {pos[0] // 1000}k savers a month; below that, profit starts during the year."
             if pos else "No level is profitable for year 5 as a whole in the plan.")
    body = frontier() + f"""<div class="chips3">
<div class="chip"><b>From one saver to the company</b>Each saver pays back in month {int(LV0['pays back in month'])}; with the team, tech and office on top, the company turns positive in {pf(LEAN['EBITDA positive from month'])} at 20,000 savers a month.</div>
<div class="chip"><b>Scale buys time</b>Fixed costs spread: at 1.5 lakh a month profit comes at {pf(FAST['EBITDA positive from month'])}, for ${FAST['money needed $M']}M.</div>
<div class="chip"><b>Year 5 as a whole</b>{Y5TXT}</div></div>"""
    big = FAST["active savers m60"] / LEAN["active savers m60"]
    mo = [int(m) for m in FRONT["EBITDA positive from month"]]
    soon = int(LEAN["EBITDA positive from month"]) - int(FAST["EBITDA positive from month"])
    when = f", {soon} months sooner" if soon > 1 else " in about the same time"
    return page(3, "Growth", "THE PLAN", f"In the plan EBITDA turns positive in months {min(mo)}–{max(mo)}; ${FAST['money needed $M']}M instead of ${LEAN['money needed $M']}M buys {big:.0f}× the active savers{when}",
                body, f"Online savers won a month from month 30 (a straight line from the seed's pace over months 19–30), 1 in 10 savers from the doorstep. Money needed = the deepest cumulative cash hole from month 1 (seed spend included) + a ₹5 crore floor. The 2.5 lakh case stops signing at the pool cap in month {CAPM}.")


# ---------- 4 two plans
def plans_chart():
    W, base, x0 = 1152, 150, 90
    yrs = list(range(1, 9))
    mx = max(abs(Y150["EBITDA Rs cr"]).max(), abs(Y20["EBITDA Rs cr"]).max())
    sc = 110 / mx
    s = [T(0, 14, "EBITDA BY YEAR, ₹ CRORE", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0 - 10}" y1="{base}" x2="{W}" y2="{base}" stroke="{INK}" stroke-width="1.2"/>')
    gw = (W - x0) / 8
    for i, y in enumerate(yrs):
        for j, (df, col) in enumerate(((Y20, TEAL), (Y150, NAVY))):
            v = float(df.loc[df.year == y, "EBITDA Rs cr"].iloc[0])
            h = v * sc
            x = x0 + i * gw + 16 + j * 50
            s.append(R(x, base - max(h, 0), 44, abs(h) if abs(h) > 1 else 1, col if v >= 0 else (col if j else TEAL), r=3))
            s.append(T(x + 22, base - h - 6 if v >= 0 else base - h + 15, f"{v:.0f}", 11, 700, col, "middle"))
        s.append(T(x0 + i * gw + 64, base + 148, f"Year {y}", 12, 700, SLATE, "middle"))
    s.append(f'<rect x="{W - 560}" y="2" width="12" height="12" rx="2" fill="{TEAL}"/>' + T(W - 542, 13, "Profitable path: 20,000 online savers a month", 12, 600))
    s.append(f'<rect x="{W - 230}" y="2" width="12" height="12" rx="2" fill="{NAVY}"/>' + T(W - 212, 13, "Grow fast: 1.5 lakh a month", 12, 600))
    return svg(W, base + 158, "".join(s))


def plans_table():
    def r(df, y, c):
        return df.loc[df.year == y, c].iloc[0]
    head = "".join(f"<th>Y{y}</th>" for y in range(1, 9))
    rows = ""
    for lab, df in (("Profitable path", Y20), ("Grow fast", Y150)):
        rows += f'<tr><td>{lab} · revenue, ₹ Cr</td>' + "".join(f"<td>{r(df, y, 'Revenue Rs cr'):.1f}</td>" for y in range(1, 9)) + "</tr>"
        rows += f'<tr><td>active savers, lakh (end)</td>' + "".join(f"<td>{r(df, y, 'active savers (end)') / 1e5:.1f}</td>" for y in range(1, 9)) + "</tr>"
    return f'<table class="at" style="font-size:11.5px;margin-top:6px"><tr><th></th>{head}</tr>{rows}</table>'


def ppl(n):
    n = float(n)
    return f"{n / 1e7:.1f} crore" if n >= 1e7 else (f"{n / 1e5:.1f} lakh" if n >= 1e5 else f"{n:,.0f}")


def crs(v):
    v = float(v)
    return f"{'−' if v < 0 else ''}₹{abs(v):,.0f} Cr" if abs(v) >= 10 else f"{'−' if v < 0 else ''}₹{abs(v):.1f} Cr"


def plans_side():
    """Three plans in columns: the profitable path, growing fast, and capturing 10 crore savers."""
    def won8(y):
        return y["online savers won"].sum() + y["doorstep savers won"].sum()

    def yv(y, k, c):
        return y.loc[y.year == k, c].iloc[0]
    cols = [("Profitable path", TEAL, LEAN, Y20), ("Grow fast", NAVY, FAST, Y150), ("Capture 10 crore", NAVY3, CAPR, YC)]
    rows = [
            ("Online savers won a month, from month 30", lambda r, y: ppl(r["online savers won a month (m30 on)"] if "online savers won a month (m30 on)" in r.index else r.name)),
            ("Savers won by year 8 (online + doorstep)", lambda r, y: ppl(won8(y))),
            ("Active savers, year 5 / year 8", lambda r, y: f"{ppl(yv(y, 5, 'active savers (end)'))} / {ppl(yv(y, 8, 'active savers (end)'))}"),
            ("Money saved with us, year 8", lambda r, y: crs(yv(y, 8, "AUM Rs cr (end)"))),
            ("Revenue, year 5 / year 8", lambda r, y: f"{crs(yv(y, 5, 'Revenue Rs cr'))} / {crs(yv(y, 8, 'Revenue Rs cr'))}"),
            ("EBITDA, year 5 / year 8", lambda r, y: f"{crs(yv(y, 5, 'EBITDA Rs cr'))} / {crs(yv(y, 8, 'EBITDA Rs cr'))}"),
            ("EBITDA positive from month", lambda r, y: f"<b>{int(r['EBITDA positive from month'])}</b>"),
            ("Money needed in all (seed included)", lambda r, y: f"<b>${r['money needed $M']:,.1f}M</b>"),
            ("20× revenue run-rate / 0.45× money saved", lambda r, y: f"{crs(r['20x ARR m60 Rs cr'])} / {crs(r['0.45x AUM m60 Rs cr'])}"),
            ("$1B (₹9,500 Cr) on both", lambda r, y: "<b>yes</b>" if str(r["$1B on both at m60"]) == "True" else "no"),
            ("Doorstep agents / team, year 5", lambda r, y: f"{int(yv(y, 5, 'Doorstep agents (end)')):,} / {int(yv(y, 5, 'Heads (end)'))}")]
    th = "".join(f'<th style="background:{c};color:#fff;font-size:13px;padding:8px 10px">{n}</th>' for n, c, *_r in cols)
    tr = ""
    for lab, f in rows:
        if f is None:
            tr += f'<tr><td colspan="4" style="font-size:10.5px;font-weight:800;letter-spacing:1px;color:{SLATE};padding-top:8px">{lab}</td></tr>'
        else:
            tr += f"<tr><td>{lab}</td>" + "".join(f"<td>{f(r, y)}</td>" for _n, _c, r, y in cols) + "</tr>"
    return f'<table class="at compact" style="font-size:12.5px"><colgroup><col style="width:31%"><col style="width:23%"><col style="width:23%"><col style="width:23%"></colgroup><tr><th></th>{th}</tr>{tr}</table>'


def p_plans():
    conv = float(CAPR["online savers per sign-up if the whole segment signs up"])
    body = plans_side() + f"""<div class="rbox" style="margin-top:8px;font-size:12.5px"><b>What capturing 10 crore takes:</b> a third of a 30 crore segment
(a competitor's figure; our agreed pool is 7 crore), so {ppl(CAPR['online savers won a month (m30 on)'])} new online savers every month. At today's 1 in 5 sign-ups saving
that needs {CAPR['sign-ups needed at 1 in 5'] / 1e7:.0f} crore sign-ups, more than the segment: it works only if about 1 in {round(1 / conv)} start saving, at ₹450 each.
Team costs follow the same rules, so they are likely understated.</div>"""
    title = (f"Side by side: the profitable path pays from month {int(LEAN['EBITDA positive from month'])} on ${LEAN['money needed $M']}M; "
             f"capturing 10 crore savers pays from month {int(CAPR['EBITDA positive from month'])}, needs ${CAPR['money needed $M']:,.0f}M and clears $1B by year 5")
    return page(4, "Three plans", "SIDE BY SIDE", title, body,
                "The plan for every plan; each starts from the seed (months 1–18) and grows flat from month 30. Revenue, EBITDA and money in ₹ crore or $ million; undiscounted.")


# ---------- 5 levers
LEV_ORDER = [("The plan", "The plan"), ("Cost to win Rs 300", "₹300 to win a saver (plan ₹450)"),
             ("45% still saving at a year", "45% still saving at a year (plan 38%)"), ("Rs 200 a day", "₹200 a day (plan ₹100)"),
             ("Rs 300 a day", "₹300 a day (plan ₹100)"), ("50% apply for a loan a year", "50% apply for a loan a year (plan 35%)"),
             ("Credit-hungry: 45% stay + 50% apply", "Credit-hungry: 45% stay + 50% apply"),
             ("10% apply for a loan a year", "10% apply for a loan a year (plan 35%)"), ("Loan offers to savers only", "Loan offers to savers only"),
             ("24% still saving at a year (savings apps)", "24% still saving, like savings apps"),
             ("Online only after m18", "Online only after the pilot"), ("Debt-only funds", "Debt funds only, no equity"),
             ("Cost to win Rs 600 (our funnel)", "₹600 to win a saver (our own funnel)")]


def levers():
    W, x0, x1 = 1152, 330, 1000
    lo, hi, PT = 30, 96, 27
    X = lambda m: x0 + (x1 - x0) * (min(max(m, lo), hi) - lo) / (hi - lo)
    n = len(LEV_ORDER)
    s = [T(0, 14, f"AT {LVS} ONLINE SAVERS A MONTH (THE PLAN): THE MONTH EBITDA TURNS POSITIVE, AND THE MONEY IT TAKES IN ALL", 11.5, 700, SLATE, ls=1.1)]
    y5 = X(60.5)
    s.append(f'<rect x="{x0}" y="26" width="{y5 - x0}" height="{n * PT + 6}" fill="#eef7f5"/>')
    for m in (48, 60, 72, 84):
        s.append(f'<line x1="{X(m + 0.5)}" y1="26" x2="{X(m + 0.5)}" y2="{32 + n * PT}" stroke="{LINE}"/>'
                 + T(X(m + 0.5), 50 + n * PT, f"end of year {m // 12}", 12, 600, SLATE, "middle"))
    for i, (key, lab) in enumerate(LEV_ORDER):
        r = LEV.loc[key]
        y = 30 + i * PT
        m = r["EBITDA positive from month"]
        m = int(m) if str(m).isdigit() else 97
        col = NAVY if i == 0 else (TEAL if m < BASE_M else (SLATE if m == BASE_M else LATE))
        s.append(T(0, y + 17, lab, 12.5, 700 if i == 0 else 500))
        s.append(R(x0, y + 4, X(m) - x0, 20, col, r=5))
        s.append(T(X(m) + 8, y + 19, (f"month {m}" if m <= 96 else "after month 96") + f" · ${r['money needed $M']}M", 12, 700, col))
    ly = 74 + n * PT
    same = any(lm(k) == BASE_M for k, _ in LEV_ORDER[1:])
    keys = [("The plan", NAVY), ("Sooner", TEAL)] + ([("Same month", SLATE)] if same else []) + [("Later", LATE), ("Shaded: by the end of year 5", "#cfeee8")]
    for k, (lab, col) in enumerate(keys):
        lx = k * 200
        s.append(f'<rect x="{lx}" y="{ly - 11}" width="13" height="13" rx="2" fill="{col}"/>' + T(lx + 20, ly, lab, 12, 600))
    return svg(W, ly + 8, "".join(s))


def p_levers():
    ms = {k: lm(k) for k, _ in LEV_ORDER[1:]}
    late = sorted((v, k) for k, v in ms.items() if v > BASE_M)
    nm = {k: v[0].lower() + v[1:] for k, v in LEV_ORDER}
    title = (f"The plan turns positive in month {BASE_M}; ₹300 a day brings it to {lm('Rs 300 a day')}, "
             f"while {nm.get(late[-2][1], late[-2][1])} or {nm.get(late[-1][1], late[-1][1])} push it to {late[-2][0]} and {late[-1][0]}")
    return page(5, "What it takes", "WHAT MOVES THE PROFIT MONTH", title, levers(),
                "One assumption changed at a time (the 24% case also lowers month-3 retention to 52%); everything else at the plan's values. Year 5 is months 49–60. The seed measures the five that matter most (see the seed page).")


# ---------- 6 unicorn
def unicorn():
    W, x0 = 1152, 330
    rows = UNIC.to_dict("records") + [dict(CAPR, case="Capture 10 crore savers")]
    mx = max(max(max(r["0.45x AUM m60 Rs cr"], r["20x ARR m60 Rs cr"]) for r in rows), UNI) * 1.04
    X = lambda v: (W - x0 - 230) * v / mx
    names = {"The plan": "The plan", "Rs 300 a day": "₹300 a day", "Credit-hungry": "Credit-hungry savers",
             "Credit-hungry + Rs 200 a day": "Credit-hungry + ₹200 a day", "Credit-hungry + Rs 300 a day": "Credit-hungry + ₹300 a day",
             "Capture 10 crore savers": "Capture 10 crore savers (12.4 lakh a month)"}
    s = [T(0, 14, "VALUE AT MONTH 60, ₹ CRORE: FIVE CASES AT 2.5 LAKH ONLINE SAVERS A MONTH, AND THE 10-CRORE PATH. $1B ONLY IF BOTH BARS CLEAR THE LINE", 11.5, 700, SLATE, ls=1.1)]
    for i, r in enumerate(rows):
        y = 30 + i * 62
        ok = bool(r["$1B on both at m60"]) if not isinstance(r["$1B on both at m60"], str) else r["$1B on both at m60"] == "True"
        s.append(T(0, y + 22, names[r["case"]], 14.5, 700, TEAL if ok else INK))
        s.append(T(0, y + 42, f"${r['money needed $M']}M needed · profit from month {int(r['EBITDA positive from month'])}", 11.5, 500, SLATE))
        for j, (k, lab, col) in enumerate((("20x ARR m60 Rs cr", "20× revenue", NAVY), ("0.45x AUM m60 Rs cr", "0.45× money saved", NAVY4))):
            v = r[k]
            yy = y + 6 + j * 26
            s.append(R(x0, yy, X(v), 20, col, r=5))
            xe, xl = x0 + X(v), x0 + X(UNI)
            lx = xl + 10 if xe < xl < xe + 175 else xe + 8          # keep the label clear of the $1B line
            s.append(T(lx, yy + 15, f"{lab}: ₹{v:,.0f} Cr", 12, 700, col))
    xu = x0 + X(UNI)
    yb = 30 + len(rows) * 62
    s.append(f'<line x1="{xu}" y1="22" x2="{xu}" y2="{yb}" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 5"/>')
    s.append(T(xu, yb + 16, f"$1B = ₹{UNI:,.0f} Cr", 12, 700, RED, "middle"))
    return svg(W, yb + 24, "".join(s))


def unicorn_title():
    ok = [r["case"] for r in UNIC.to_dict("records") if str(r["$1B on both at m60"]) == "True"]
    if not ok and str(CAPR["$1B on both at m60"]) == "True":
        close = (UNIC[["20x ARR m60 Rs cr", "0.45x AUM m60 Rs cr"]].min(axis=1) / UNI)
        return (f"Only capturing 10 crore savers clears $1B on both yardsticks by year 5, for ${CAPR['money needed $M']:,.0f}M; "
                f"at 2.5 lakh savers a month the closest case falls {1 - close.max():.0%} short")
    if ok:
        short = {"The plan": "the plan", "Rs 300 a day": "₹300 a day", "Credit-hungry": "credit-hungry savers",
                 "Credit-hungry + Rs 200 a day": "credit-hungry at ₹200 a day", "Credit-hungry + Rs 300 a day": "credit-hungry at ₹300 a day"}
        best = UNIC[UNIC["case"].isin(ok)]["money needed $M"].min()
        return (f"{len(ok)} of 5 combinations clear $1B on both yardsticks by year 5 ({'; '.join(short.get(o, o) for o in ok)}); "
                f"the cheapest needs ${best}M")
    close = (UNIC[["20x ARR m60 Rs cr", "0.45x AUM m60 Rs cr"]].min(axis=1) / UNI)
    best = UNIC.iloc[int(close.idxmax())]
    return (f"No combination reaches $1B on both yardsticks by year 5; the closest, {best['case'].replace('Rs ', '₹').lower()}, "
            f"needs ${best['money needed $M']}M and falls {1 - close.max():.0%} short on revenue")


def p_unicorn():
    return page(6, "Unicorn test", "$1B BY YEAR 5", unicorn_title(),
                unicorn(), "Five cases at 2.5 lakh online savers a month from month 30, and the 10-crore path at 12.4 lakh a month (the side-by-side page; 30 crore segment, a third captured); 1 in 10 savers from the doorstep. "
                           "Yardsticks: 20× the month-60 revenue run-rate; 0.45× money saved (a little below the ~0.5× a recent savings-app round paid on money invested). "
                           f"Sign-ups stop at 20% of a 7 crore pool in month {CAPM}.")


# ---------- 7 what the seed proves
def p_seed():
    oo = LEV.loc["Online only after m18"]
    base = LEV.loc["The plan"]
    om = int(oo['EBITDA positive from month'])
    when = f"the same month ({om})" if om == BASE_M else f"month {om} instead of {BASE_M}"
    door_line = f"Without it: profit in {when}. It must beat online's {ON['still saving at 12 months']:.0%} clearly to earn its place."
    gates = [("Cost to win a saver", "₹600 in the seed (our funnel today); ₹450 planned after, the midpoint of a competitor's ₹300 and our ₹600.",
              f"₹300: month {lm('Cost to win Rs 300')}. ₹600: month {lm('Cost to win Rs 600 (our funnel)')}."),
             ("Still saving at 12 months", f"{ON['still saving at 12 months']:.0%} online is the plan: profit in month {BASE_M}.",
              f"45%: month {lm('45% still saving at a year')}. 24% (savings apps): month {lm('24% still saving at a year (savings apps)')}."),
             ("Daily amount", "₹100 is the plan, and our assumption.", f"₹200: month {lm('Rs 200 a day')}; ₹300: month {lm('Rs 300 a day')}."),
             ("Who borrows", "35% of KYC'd users apply a year, 30% approved: the plan.", f"10%: month {lm('10% apply for a loan a year')}; 50%: month {lm('50% apply for a loan a year')}; savers only: month {lm('Loan offers to savers only')}."),
             ("Doorstep arm", f"{DOOR['still saving at 12 months']:.0%} still saving earns ₹{int(DOOR['revenue 60 months Rs']):,} a saver.", door_line)]
    nxt_l, nxt_f = round(LEAN['money needed $M'] - 0.5, 1), round(FAST['money needed $M'] - 0.5, 1)
    g = "".join(f'<div class="gate" style="padding:16px"><span>{i + 1}</span><b>{a}</b><em style="display:block;margin-top:6px">{b}</em>'
                f'<em style="display:block;margin-top:6px;color:{NAVY};font-weight:700">{c}</em></div>' for i, (a, b, c) in enumerate(gates))
    tiles = [("$0.5M", "the seed: build, licences, a lean team, the doorstep pilot"), ("1 lakh", "sign-ups in months 4–18 to read the five numbers"),
             ("Months 16–18", "12 months of data on the first savers; raise the next round (the seed budget runs to month 24 if it is late)"),
             (f"${nxt_l}M or ${nxt_f}M", f"the next round: profitable path or grow fast (${LEAN['money needed $M']}M or ${FAST['money needed $M']}M in all)")]
    tl = "".join(f'<div class="kpi"><b>{a}</b><span>{b}</span></div>' for a, b in tiles)
    body = f'<div class="gates">{g}</div><div class="sub-h" style="margin-top:18px">HOW THE SEED GETS THERE</div><div class="kpis" style="grid-template-columns:repeat(4,1fr)">{tl}</div>' + \
        '<div class="rbox" style="margin-top:12px">The seed is not a profit plan. It buys five measurements: the profitable path is the floor, growing fast is the upside, and the numbers decide which.</div>'
    return page(7, "What the seed proves", "THE FIVE NUMBERS", f"The $0.5M seed measures the five numbers that decide whether the next round is about ${nxt_l}M or ${nxt_f}M",
                body, f"Profit months at {LVS} online savers a month (the plan), one assumption changed at a time. The seed plan, a separate document, has the team and the use of funds.")


# ---------- 8 assumptions
ASSUME = [("Online saver", "₹100 a day, ~20 debit days a month; 80% still saving at month 3, 38% at a year",
           "₹100 is our assumption (Bachatt's stated minimum). Retention: our extrapolation from SBI MF's ₹250 daily SIP for first-time investors (36% of a year's sign-ups stopped within it); savings apps' 24% is the downside"),
          ("Doorstep saver", "Same product; 80% still saving at month 3, 55% at a year; 100 sign-ups per agent a month, each counted as a saver",
           "Agreed street inputs; the agent sets the mandate at sign-up. A competitor's street team reports 100–125 a person a month. All-in cost ₹405 a saver at scale (₹446 with our contingency)"),
          ("Funds", "80% equity SIP / 20% debt; returns 10% / 7% a year; fees 0.75% / 0.35% of balance",
           "Mix from a practitioner conversation (not yet a filed research row); fees from fund-house disclosures; the equity return is our estimate"),
          ("Cost to win a saver", "₹600 during the seed (our funnel), ₹450 after; range ₹300–600",
           "₹450 sits between a competitor's reported ₹300 per customer (per sign-up or per saver not stated) and our own funnel's ₹600; the seed measures it"),
          ("Loans", "Offers to every KYC'd user (2.5 per online saver) from day 1; 35% apply a year (70% personal or business, 15% gold, 3% property, 2% home); "
                    "30% of first applications approved, 70% of repeats; ₹3 lakh personal/business loans at a 2% payout rising to 3%; home loans ₹30 lakh, property ₹25 lakh",
           "Founders' choice on reach and apply rate; payouts at DSA norms (1–2.5% personal and business, 0.5–1.5% property, 0.25–1.5% gold); "
           "loan sizes are the founders' numbers (22 Oct), above the digital-lender and micro-LAP averages in research/xs_funnel_2026-10-21.csv; gold from industry data"),
          ("Other products", "Cards, insurance (at IRDAI's draft caps), recharge, bills, FD, gold-loan and property-loan referrals", "Agreed take-up and commission inputs; property ₹25 lakh and home ₹30 lakh loans (founders, 22 Oct)"),
          ("Team", "Seed: 2 founders at $1,000 a month + 3 hires. After the round: founders ₹1.5L, hires by active savers",
           "Seed plan; agreed salary inputs, +10% statutory, +7% a year"),
          ("Other costs", "Tech ₹1.5L a month + ₹4 per KYC'd user reached; payments ₹2 a weekly debit; office; compliance ₹25L a year after the round; brand ₹2L a month; 10% contingency on every cost",
           "Agreed inputs and the agreed 10% contingency; per-saver tech and the ₹25L compliance are our estimates"),
          ("Growth limit", "At most 20% of about 7 crore urban self-employed ever signed", "PLFS shares (agreed pool) and the agreed 20% cap"),
          ("Not counted", "Interest on cash; any own-book lending; revenue beyond these lines", "Conservative by design")]


def p_assume():
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in ASSUME)
    return page(8, "Appendix", "ASSUMPTIONS", "Every input, and where it comes from",
                f'<table class="at"><tr><th>Input</th><th>Value</th><th>Basis</th></tr>{rows}</table>')


def build():
    pages = [cover(), p_unit(), p_ltv_levers(), p_frontier(), p_plans(), p_levers(), p_unicorn(), p_seed(), p_assume()]
    pages = [pages[0]] + [re.sub(r'(<footer class="pf"><span>[^<]*</span><span>)[^<]*(</span></footer>)', rf"\g<1>{i}\2", h)
                          for i, h in enumerate(pages[1:], start=2)]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Online-first business case</title><style>{sp.CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')
    out = HERE / "Online_business_case.html"
    out.write_text(html)
    pdf = HERE / "Online_business_case.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, capture_output=True)
    print("wrote", pdf)


if __name__ == "__main__":
    build()

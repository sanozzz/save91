"""Online-first business case, rebased 24 Oct 2026 on the founders' market and measured inputs (model/online_plan.py, "REBASE 24
Oct"). Landscape pages in the seed plan's design (seed/build_seed_plan.py CSS and helpers).
One case: the main case, the LTV/CAC Monte Carlo's median (model/ltv_odds.py). "What it takes" (the ladder and the levers) says what
would have to be true; it is never a second plan, and our old loan targets appear only as the upside end of it.
Pages: the main-case saver, the odds, what it takes (the ladder, with profit month and money needed), the main-case financials, the
company's levers one at a time, the four facts and the seed, the assumptions, and an upside appendix (the $1B test, honestly).
Shared with the v4 plan deck (online/build_online_v4.py): p_main_saver(n), p_seed_main(n), p_upside(n) return finished pages;
the Monte Carlo pages come from ltv/odds_pages.py. Numbers: tables/ltv_*.csv and online_*.csv (all on the main case).
Builds online/Online_business_case.html and .pdf."""
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "seed"))
import build_seed_plan as sp  # noqa: E402  (CSS, colours and svg helpers)
sys.path.insert(0, str(ROOT / "ltv"))
sys.path.insert(0, str(ROOT / "model"))
import build_ltv_deck as ld  # noqa: E402  (the lender-fee test page and table helpers, shared with the LTV/CAC decks)
import odds_pages as od  # noqa: E402  (the main-case pages and tables, shared with the LTV/CAC deck)

TAB = ROOT / "tables"
INK, NAVY, TEAL, BLUE, AMBER, SLATE, MUTE, LINE, BG, RED = sp.INK, sp.NAVY, sp.TEAL, sp.BLUE, sp.AMBER, sp.SLATE, sp.MUTE, sp.LINE, sp.BG, sp.RED
NAVY2, NAVY3, NAVY4 = sp.NAVY2, sp.NAVY3, sp.NAVY4
LATE = "#a8553d"                         # "later than the main case": a muted brick, not the doorstep amber
T, R, A, svg = sp.T, sp.R, sp.A, sp.svg
halo, x, usd, month, rs = od.halo, od.x, od.usd, od.month, od.rs
FX = 95.0
UNI = 1e9 * FX / 1e7                     # $1B in Rs crore

UNIT = pd.read_csv(TAB / "online_unit.csv").set_index("saver")
DOOR = UNIT.loc["Doorstep saver"]
UNIC = pd.read_csv(TAB / "online_unicorn.csv")
CAPR = pd.read_csv(TAB / "online_capture.csv").iloc[0]          # capture 10 crore savers by month 96 (operator 21 Oct)
CAPM = int(UNIC["online sign-ups stop at the pool cap in month"].iloc[0])
LTVW = pd.read_csv(TAB / "online_ltv_waterfall.csv")
S5, S8, MAIN, CAC = od.S5, od.S8, od.MAIN, od.CAC


def page(n, section, kicker, title, body, src=""):
    s = f'<div class="src">{src}</div>' if src else ""
    return f"""<section class="page">
<header class="ph"><span class="brand">{sp.NAME} <em>· working name</em></span><span>{section}</span></header>
<div class="kicker">{kicker}</div><h1>{title}</h1>
<div class="body">{body}</div>{s}
<footer class="pf"><span>Online-first business case · October 2026 · Confidential</span><span>{n}</span></footer>
</section>"""


def ppl(n):
    n = float(n)
    return f"{n / 1e7:.1f} crore" if n >= 1e7 else (f"{n / 1e5:.1f} lakh" if n >= 1e5 else f"{n:,.0f}")


def no_profit(r):
    return int(float(r["EBITDA positive from month"])) > 96


# ---------- 1 cover: the cross-sell answer first (FIXES B1, B3)
def cover():
    cross = (f"Cross-selling alone (loans and cards) brings {rs(S5['cross-sell'])} per saver in 5 years and {rs(S8['cross-sell'])} in 8: "
             f"{x(S5['cross-sell / CAC'])} and {x(S8['cross-sell / CAC'])} of the {rs(CAC)} it costs to win a saver, before serving, and less than the "
             f"{rs(S5['serving'])} / {rs(S8['serving'])} it costs to serve them ({x(S5['cross-sell net of serving / CAC'])} after serving). Insurance, "
             "recharge, bills, FD and NPS are not counted.")
    tiles = [(f"{rs(S5['cross-sell'])} · {rs(S8['cross-sell'])}", cross),
             (f"{od.XMED} · {od.XMED8}", f"LTV/CAC with fund fees, 5 and 8 years: {od.GLOSS['ltv']}. A saver pays back in month {od.PAY}."),
             ("Not by year 8" if no_profit(MAIN) else month(MAIN["EBITDA positive from month"]).capitalize(),
              f"for the company's EBITDA to turn positive in the main case; it needs at least {usd(MAIN['money needed $M'])}, still rising at month 96"),
             (f"2× → {month(od.R2['EBITDA positive from month'])}", f"what it takes: ₹{float(od.R2['saved a day Rs']):.0f} a day, "
                                                                   f"{float(od.R2['still saving at 12 months']):.0%} still saving and loans most of the way "
                                                                   f"to our old targets, for profit on {od.floor_usd(od.R2)}")]
    t = "".join(f'<div class="ctile" style="padding:18px 20px 16px"><div class="cbig" style="font-size:30px">{a}</div><div class="csub" style="font-size:12.5px">{b}</div></div>'
                for a, b in tiles)
    conf = (f"Assumes debits cost us ₹{od.op.DEBIT_COST:.0f} and a {od.pct(od.op.EQ_TRAIL, 2)} equity fund fee, both still to be confirmed in writing: ₹2 a "
            f"weekly debit would cut a saver to about {x(od.ltvl('We pay Rs 2 a debit, weekly'))}, a 0.5% fee to about "
            f"{x(od.ltvl('Equity fund fee 0.5%, not 0.75%'))}.")
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:52px">Online-first business case</div>
  <div class="ctag">The company on the founders' inputs of 24 October: one main case, what is still uncertain, and what it would take.</div>
  <div class="cmeta">October 2026 · Confidential</div>
</div>
<div class="cright" style="padding:44px 48px"><div class="cgrid" style="gap:14px">{t}</div>
<div style="margin-top:14px;font-size:13px;line-height:1.45;border-left:6px solid {AMBER};background:{sp.AMBER_L};border-radius:10px;padding:9px 14px">
<b style="color:{AMBER}">To confirm in writing.</b> {conf}</div>
<div class="cnote" style="margin-top:10px;font-size:12.5px">Cost to win: {od.CAC_WORDS}. Online savers at ₹100 a day and 1 in 10 from a doorstep pilot.
Funds are bought in the saver's own name; the app never holds money.</div></div>
</section>"""


# ---------- 2 the main-case saver
def money(v):
    return f"{'−' if v < 0 else '+'}₹{abs(v):,.0f}"


def waterfall(saver="Online saver", items=None):
    """Cost to win, then each revenue line over 60 months, then serving: where the saver's value comes from."""
    if items is None:
        w = LTVW[LTVW.saver == saver]
        items = [(k, v) for k, v in zip(w["line"], w["Rs over 60 months"].astype(float)) if abs(v) >= 0.5 or k.startswith(("Cost", "Net"))]
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
    bw, gap = 68, 22
    cols = {"Cost to win": "#7d8796", "Fund fees": NAVY, "Serving (support + tech)": LATE}
    names = {"Cost to win": ["Cost to", "win"], "Fund fees": ["Fund", "fees"], "Loans (all referrals)": ["Loans"],
             "Insurance": ["Insurance"], "Cards": ["Cards"], "Other products": ["Other", "products"],
             "Serving (support + tech)": ["Serving"], "Net over 60 months": ["Net,", "5 years"]}
    s = [T(0, 14, f"ONE {saver.upper()} WON, FIRST 5 YEARS (₹)", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0}" y1="{Y(0)}" x2="{x0 + len(bars) * (bw + gap)}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>')
    xs = []
    for i, (nm, a, b) in enumerate(bars):
        xx = x0 + i * (bw + gap)
        xs.append(xx)
        net = nm.startswith("Net")
        col = NAVY2 if net else cols.get(nm, NAVY4)
        s.append(R(xx, min(Y(a), Y(b)), bw, max(abs(Y(a) - Y(b)), 2), col, r=4))
        v = b - a
        ty = min(Y(a), Y(b)) - 7 if v >= 0 else max(Y(a), Y(b)) + 16
        s.append(halo(T(xx + bw / 2, ty, money(v) if not net else f"{'−' if v < 0 else ''}₹{abs(v):,.0f}", 13 if net else 12.5,
                        800 if net else 700, col if not net else NAVY2, "middle")))
        for k, ln in enumerate(names.get(nm, [nm])):
            s.append(T(xx + bw / 2, y1 + 34 + k * 14, ln, 11.5, 700 if net else 600, INK if net else SLATE, "middle"))
        if i < len(bars) - 1 and not net and not bars[i + 1][0].startswith("Net"):
            s.append(f'<line x1="{xx + bw}" y1="{Y(b)}" x2="{xx + bw + gap}" y2="{Y(b)}" stroke="{MUTE}" stroke-dasharray="3 3"/>')
    cross = ("Loans (all referrals)", "Insurance", "Cards", "Other products")
    xs_idx = [i for i, (nm, *_r) in enumerate(bars) if nm in cross]
    xsell = sum(b - a for nm, a, b in bars if nm in cross)
    rev = sum(b - a for nm, a, b in bars if nm not in ("Cost to win", "Serving (support + tech)") and not nm.startswith("Net"))
    bx0, bx1 = xs[xs_idx[0]], xs[xs_idx[-1]] + bw
    by = y0 - 18
    s.append(f'<path d="M{bx0} {by + 8} L{bx0} {by} L{bx1} {by} L{bx1} {by + 8}" fill="none" stroke="{NAVY4}" stroke-width="1.6"/>')
    s.append(T((bx0 + bx1) / 2, by - 6, f"Cross-sell ₹{xsell:,.0f}: {xsell / rev:.0%} of revenue", 12, 700, NAVY4, "middle"))
    return svg(W, H, "".join(s)), xsell, rev


def case_saver(pos):
    """One online saver won with the drawn inputs at pos (a {input: position} dict, or one position t for both; the main case is
    od.T_MAIN): the waterfall lines over 60 months, the cumulative net curve (months 0-96) and the LTV/CAC summary."""
    op = od.op
    op.OV.clear()
    op.OV.update(od.lo.overrides(pos if isinstance(pos, dict) else od.lo.at(pos)))
    op._CACHE.clear()
    try:
        d, cum, v = op.ltv_view(op.saver_inputs(), op.CAC)
    finally:
        op.OV.clear()
        op._CACHE.clear()
    c = v["cost to win Rs"]
    items = [("Cost to win", -float(c))] + [(k, float(d[k][:60].sum())) for k in ("Fund fees", "Loans (all referrals)", "Insurance", "Cards", "Other products")
                                            if abs(float(d[k][:60].sum())) >= 0.5]
    items += [("Serving (support + tech)", -float(d["serving"][:60].sum())), ("Net over 60 months", float(cum[59] - c))]
    curve = [(m, float((cum[m - 1] if m else 0.0) - c)) for m in range(97)]
    return items, curve, v


MAIN_ITEMS, MAIN_CURVE, MAIN_V = case_saver(od.T_MAIN)
_, LOW_CURVE, LOW_V = case_saver({**od.lo.at(od.T_MAIN), "keep": 0.0})       # the ends move retention only (FIXES A3)
_, HIGH_CURVE, HIGH_V = case_saver({**od.lo.at(od.T_MAIN), "keep": 1.0})
assert abs(MAIN_V["contribution 60m Rs"] / MAIN_V["cost to win Rs"] - od.MED) < 0.01
assert abs(dict(MAIN_ITEMS)["Fund fees"] - float(S5["Fund fees"])) < 1, "the waterfall and tables/ltv_saver_split.csv disagree"


def payback_three():
    """Cumulative net per online saver won: the main case between the low and high ends of retention."""
    W, H, x0, x1, y0, y1 = 450, 296, 52, 440, 44, 240
    vals = [v for _m, v in MAIN_CURVE + LOW_CURVE + HIGH_CURVE]
    lo_, hi = min(vals), max(vals)
    X = lambda m: x0 + (x1 - x0) * m / 96
    Y = lambda v: y1 - (y1 - y0) * (v - lo_) / (hi - lo_)
    s = [T(0, 14, "WHEN IT PAYS BACK: CUMULATIVE ₹ PER SAVER WON", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>')
    for m in (0, 12, 24, 36, 48, 60, 72, 84, 96):
        s.append(T(X(m), y1 + 18, f"{m}", 11, 600, MUTE, "middle"))
    s.append(T(x1, y1 + 34, "months after the saver joins", 11, 600, MUTE, "end"))
    for v in (lo_, 0, hi):
        s.append(T(x0 - 6, Y(v) + 4, f"{'−' if v < 0 else ''}₹{abs(v):,.0f}" if v else "0", 10.5, 600, MUTE, "end"))
    s.append(f'<line x1="{X(60)}" y1="{y0}" x2="{X(60)}" y2="{y1}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    s.append(T(X(60) + 4, y0 + 10, "5 years", 11, 700, MUTE))
    for cv, col, w, dash in ((LOW_CURVE, "#9fb8d6", 2.0, ' stroke-dasharray="6 4"'), (HIGH_CURVE, "#9fb8d6", 2.0, ' stroke-dasharray="6 4"'),
                             (MAIN_CURVE, NAVY, 3, "")):
        pts = " ".join(f"{X(m):.1f},{Y(v):.1f}" for m, v in cv)
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{w}"{dash}/>')
    pm = MAIN_V["pays back in month"]
    if isinstance(pm, int):
        s.append(f'<circle cx="{X(pm)}" cy="{Y(0)}" r="5" fill="{NAVY}"/>')
        s.append(halo(T(X(pm) - 8, Y(0) + 20, f"main case: month {pm}", 12, 700, NAVY, "end")))
    s.append(halo(T(X(96), Y(HIGH_CURVE[96][1]) - 8, f"40% still saving: {rs(HIGH_CURVE[96][1])}", 11, 700, SLATE, "end")))
    s.append(halo(T(X(96), Y(LOW_CURVE[96][1]) + 16, f"30%: {'−' if LOW_CURVE[96][1] < 0 else ''}{rs(abs(LOW_CURVE[96][1]))}", 11, 700, SLATE, "end")))
    mlo, vlo = min(MAIN_CURVE, key=lambda mv: mv[1])                    # label the curve's low point (FIXES D2)
    s.append(f'<circle cx="{X(mlo):.1f}" cy="{Y(vlo):.1f}" r="4" fill="{NAVY}"/>')
    s.append(halo(T(X(mlo) + 6, Y(vlo) - 9, f"lowest −₹{abs(vlo):,.0f}, month {mlo}", 11, 700, NAVY)))
    v96 = MAIN_CURVE[96][1]
    s.append(halo(T(X(96), Y(v96) - 8, f"{'+' if v96 >= 0 else '−'}₹{abs(v96):,.0f}", 12, 800, NAVY, "end")))
    return svg(W, H, "".join(s))


def p_main_saver(n):
    wf, xsell, rev = waterfall(items=MAIN_ITEMS)
    serve = -dict(MAIN_ITEMS)["Serving (support + tech)"]
    X = od.X
    body = f"""<div style="display:flex;gap:22px;align-items:flex-start"><div style="flex:0 0 680px">{wf}</div><div style="flex:0 0 450px">{payback_three()}</div></div>
<div class="chips3" style="margin-top:2px">
<div class="chip"><b>{od.XMED} in 5 years, {od.XMED8} in 8</b>LTV/CAC: {od.GLOSS['ltv']} ({rs(CAC)}). Undiscounted.</div>
<div class="chip"><b>Cross-selling doesn't cover serving</b>Loans {rs(dict(MAIN_ITEMS)['Loans (all referrals)'])} and cards {rs(dict(MAIN_ITEMS)['Cards'])} bring {rs(xsell)}, less than the {rs(serve)} of serving: {x(S5['cross-sell / CAC'])} of the cost to win before serving, {x(S5['cross-sell net of serving / CAC'])} after. Fund fees bring the rest.</div>
<div class="chip"><b>Retention is the swing</b>At 30% still saving a year the saver returns {x(od.LOW['LTV/CAC 5y'])} and does not pay back by year 8; at 40%, {x(od.HIGH['LTV/CAC 5y'])}, paid back in month {int(od.HIGH['saver pays back in month'])}.</div></div>"""
    return page(n, "One saver", "LTV / CAC, THE MAIN CASE", f"A saver won online costs {rs(CAC)} and returns {rs(S5['net'])} over five years in the main case: "
                f"{od.XMED} LTV/CAC, paid back in month {od.PAY}",
                body, f"Main case: the Monte Carlo median ({od.val('keep')} still saving after a year, a {od.val('trail')} debt fund fee). ₹100 a day; 80/20 equity "
                      f"and debt funds. Serving = ₹{X['support_cost']:.0f} support a month per saver still saving and ₹{od.op.TECH_PER_SAVER:.0f} tech for each of the "
                      f"{od.op.LOAN_REACH:.2f} people reached ({od.GLOSS['kyc']}), plus the 10% contingency; debits ₹0. Cost to win ₹{od.op.CAC:.0f} + 10% = {rs(CAC)}; "
                      f"at ₹600 (₹660 with the contingency) a saver is about {x(od.ltvl('Cost to win Rs 600 (our funnel)'))} / "
                      f"{x(od.ltvl8('Cost to win Rs 600 (our funnel)'))} and the company needs {od.levm_usd('Cost to win Rs 600 (our funnel)')}. "
                      "Not in this view: the company's fixed costs (team, office, brand).")


# ---------- the shared main-case pages
def p_odds(n):
    return page(n, "What's uncertain", *od.p_odds())


def p_ladder(n):
    return page(n, "What it takes", *od.p_ladder())


def p_financials(n):
    return page(n, "The company", *od.p_financials())


def p_prove(n):
    return page(n, "What decides it", *od.p_prove())


# ---------- 6 the company's levers, one at a time (tables/ltv_main_levers.csv)
LEVERS = [("The main case", "The main case"), ("Rs 300 a day", "₹300 a day"), ("Rs 200 a day", "₹200 a day"),
          ("Loan funnel at our old targets", "Loans at our old targets: applying 35%, approval 30%, yearly rises"),
          ("Credit-hungry: 45% stay + 50% apply", "Credit-hungry: 45% still saving and 50% applying"),
          ("Cost to win Rs 300", "₹300 to win a saver"), ("50% apply for a loan a year", "50% apply for a loan a year"),
          ("45% still saving at a year", "45% still saving a year (1.0% a month stopping after)"), ("10% apply for a loan a year", "10% apply for a loan a year"),
          ("24% still saving at a year (savings apps)", "24% still saving, like savings apps"),
          ("Equity fund fee 0.5%, not 0.75%", "Equity fund fee 0.5%, not 0.75%"), ("We pay Rs 2 a debit, weekly", "We pay ₹2 for each weekly debit"),
          ("Cost to win Rs 600 (our funnel)", "₹600 to win a saver (our funnel today)"), ("Debt-only funds", "Debt funds only, no equity")]


def levers_svg(W=1152):
    rows = [(lab, *od.levm(k)) for k, lab in LEVERS]
    base = od.levm("The main case")[1]
    x0, x1, rh = 420, 900, 25
    mx = max(m for _l, _p, m in rows) * 1.05
    X = lambda v: x0 + (x1 - x0) * v / mx
    s = [T(0, 14, "ONE CHANGE AT A TIME FROM THE MAIN CASE", 11, 700, SLATE, ls=1),
         T(x0, 14, "MONEY NEEDED IN ALL, SEED INCLUDED", 11, 700, SLATE, ls=1), T(W, 14, "EBITDA POSITIVE FROM", 11, 700, SLATE, "end", ls=1)]
    y = 24
    for i, (lab, pm, m) in enumerate(rows):
        main = i == 0
        col = NAVY if main else (TEAL if pm else (LATE if m > base + 0.05 else SLATE))
        if main:
            s.append(R(-6, y, W + 12, rh - 1, sp.NAVY_L, r=6))
        s.append(T(0, y + 17, lab, 12.5, 800 if main else 600, NAVY if main else INK))
        s.append(R(x0, y + 5, X(m) - x0, 15, col, r=4))
        s.append(halo(T(X(m) + 8, y + 17, usd(m) + ("" if pm else "+"), 12.5, 800, col)))
        s.append(T(W, y + 17, month(pm) if pm else "not by month 96", 12.5, 800 if pm else 600, TEAL if pm else (NAVY if main else SLATE), "end"))
        y += rh
    s.insert(3, f'<line x1="{X(base):.1f}" y1="22" x2="{X(base):.1f}" y2="{y}" stroke="{NAVY}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    return svg(W, y + 6, "".join(s))


def p_main_levers(n):
    profit = [k for k, _l in LEVERS[1:] if od.levm(k)[0]]
    word = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}.get(len(profit), str(len(profit)))
    title = (f"{word} single changes bring profit by month 96; a ₹2 weekly debit or a 0.5% fund fee would push the money needed to "
             f"{od.levm_usd('We pay Rs 2 a debit, weekly')} or {od.levm_usd('Equity fund fee 0.5%, not 0.75%')}")
    return page(n, "What it takes", "THE COMPANY'S LEVERS, ONE AT A TIME", title, levers_svg(),
                "Each row changes one input of the main case, everything else held; the company as on the company page. 45% and 24% still saving "
                "and credit-hungry savers use one retention line (the drop-off after a year moves with it). Teal: profit by month 96; brick: more "
                f"money than the main case. {od.MONEY_NOTE}")


# ---------- 7 the four facts and the seed
def p_seed_main(n):
    gates = "".join(
        f'<div class="gate" style="padding:14px"><span>{i}</span><b style="font-size:13.5px">{name}</b>'
        f'<em style="display:block;margin-top:6px">{how}</em>'
        f'<em style="display:block;margin-top:6px;color:{NAVY};font-weight:700">'
        f'{" · ".join(f"{lab}: {x(v)}" for lab, v, _t in pts)}</em>'
        f'<em style="display:block;margin-top:4px;color:{NAVY4};font-weight:700">{comp}</em></div>'
        for i, (name, how, pts, comp) in enumerate(od.facts(), start=1))
    nxt, nxt2 = float(MAIN["money needed $M"]) - 0.5, float(od.R2["money needed $M"]) - 0.5      # read from the ladder (FIXES D5)
    tiles = [("$0.5M", "the seed: build, licences, a lean team, the doorstep pilot"),
             ("1 lakh", "sign-ups in months 4–18: our own retention curve, loan opt-in and approvals, and the cost to win"),
             ("Months 16–18", "12 months of data on the first savers; raise the next round (the seed budget runs to month 24 if it is late)"),
             (f"{usd(nxt)}+", f"the next round in the main case ({od.floor_usd(MAIN)} in all, less the seed); about {usd(nxt2)} at 2× "
                              f"({od.floor_usd(od.R2)} in all)")]
    tl = "".join(f'<div class="kpi"><b>{a}</b><span>{b}</span></div>' for a, b in tiles)
    body = (f'<div class="gates" style="grid-template-columns:repeat(4,1fr)">{gates}</div>'
            f'<div class="sub-h" style="margin-top:16px">THEN THE SEED MEASURES OUR OWN SAVERS</div>'
            f'<div class="kpis" style="grid-template-columns:repeat(4,1fr)">{tl}</div>')
    return page(n, "What the seed proves", "FOUR FACTS NOW, THEN THE SEED",
                "Four facts we can ask for now decide most of the answer; the $0.5M seed then measures our own savers, loan funnel and cost to win",
                body, "Each fact: one saver's 5-year LTV/CAC either way, from the main case; retention is the Monte Carlo median with still saving pinned "
                      "at 30%, then 40%. Next round: money needed in all, less the $0.5M seed. The seed plan, a separate document, has the team and the use of funds.")


# ---------- 8 assumptions
def assume_rows():
    X, op = od.X, od.op
    k = od.lo.drawn(od.lo.at(od.T_MAIN))
    return [
        ("Online saver", f"₹{X['daily']:.0f} a day, ~{X['days']:.0f} debit days a month; {X['r3']:.0%} still saving at month 3; 30–40% at a year "
                         f"(main case {k['r12']:.0%}), the drop-off after a year moving with it, 2.5%–1.5% a month (main case {k['churn_late']:.1%})",
         f"₹100 is {od.SOURCE['daily']}. Retention is Bachatt's own range, drawn; SBI MF's ₹250 daily SIP keeps about 38% at 12 months. "
         "45% still saving means 1.0% a month stopping after, the same line"),
        ("Doorstep saver", f"Same product; 80% still saving at month 3, {DOOR['still saving at 12 months']:.0%} at a year; 100 sign-ups per agent a month",
         f"Agreed street inputs; the agent sets the mandate at sign-up. All-in cost {rs(DOOR['cost to win Rs'] / 1.1)} a saver at scale "
         f"({rs(DOOR['cost to win Rs'])} with our contingency)"),
        ("Funds", f"80% equity SIP / 20% debt; returns 10% / 7% a year; our fee {od.pct(op.EQ_TRAIL, 2)} of the equity balance and 0.10–0.35% of the debt "
                  f"balance (main case {od.pct(od.DEBT_MAIN, 2)}), {od.val('blend')} blended",
         "Fund-house disclosures; the 0.75% on active equity funds is still to be confirmed in writing. If the ₹100 goes into one hybrid fund (daily "
         f"minimums are ~₹100 a scheme), its fee to us must be about {od.val('blend')} or more"),
        ("Cost to win a saver", f"₹{op.SEED_CAC:.0f} during the seed, ₹{op.CAC:.0f} after, plus our 10% contingency ({rs(CAC)}); held fixed",
         f"{od.CAC_WORDS}. At ₹600 after the seed the company needs {od.levm_usd('Cost to win Rs 600 (our funnel)')}"),
        ("Loans", f"Offers to KYC'd users from day 1 (about 2.5 per saver; non-savers fade within ~3 months, so {op.LOAN_REACH:.2f} in value); "
                  f"{od.pct(op.LOAN_APPLY)} apply a year (70% personal or business, 15% gold, 3% property, 2% home); {od.pct(X['approved_first'])} of first "
                  f"personal or business loans approved (gold {od.pct(op.GOLD_APPROVAL)}, home and property {od.pct(X['loan_home_approval'])}), "
                  f"{od.pct(X['approved_repeat'])} of repeats; no yearly rises; first loan {od.lakh(X['ticket'])}, repeats 10% bigger a year, top-ups "
                  f"{od.pct(X['topup_share'])} a year at {od.pct(X['topup_size'])}; lender payout {od.pct(X['fee'])} flat; home {od.lakh(X['loan_home_ticket'])}, "
                  f"property {od.lakh(X['loan_lap_ticket'])}",
         f"Founders, 24 Oct: ₹70k is Bachatt's number (our research had ₹15k–58.5k); 20% approval is {od.SOURCE['approved']}; payouts 1–3%; affordable "
         "home loans ₹6–15 lakh, small property loans about ₹3.9 lakh. We refer; the lender lends"),
        ("Other products", f"Cards: {od.pct(X['card_share'])} of savers still saving at month 7 take one, ₹{X['card_fee']:,.0f} a card; small loans outside the "
                           f"apply funnel: durables ({od.lakh(X['loan_cd_ticket'])}) and two-wheelers",
         "Not counted: insurance (a fixed referral fee, to be agreed), recharge, bills, FD and NPS (not in the launch app), loans against savings "
         "(10% of applications)"),
        ("Serving", f"₹{X['support_cost']:.0f} support a month per saver still saving; ₹{op.TECH_PER_SAVER:.0f} tech a month for each of the "
                    f"{op.LOAN_REACH:.2f} people reached; plus the 10% contingency; daily debits ₹0 to us",
         "BSE StAR MF's exchange SIP is free to distributors and fund houses pay BSE; ₹0 is still to be confirmed in writing (₹2 a weekly debit: "
         f"{od.levm_usd('We pay Rs 2 a debit, weekly')} needed)"),
        ("Team", "Seed: 2 founders at $1,000 a month + 3 hires. After the round: founders ₹1.5L, hires by active savers",
         "Seed plan; agreed salary inputs, +10% statutory, +7% a year"),
        ("Other costs", "Tech ₹1.5L a month; office; compliance ₹25L a year after the round; brand ₹2L a month; 10% contingency on every cost",
         "Agreed inputs and the agreed 10% contingency; the ₹25L compliance is our estimate"),
        ("Growth limit", "At most 20% of about 7 crore urban self-employed ever signed", "PLFS shares (agreed pool) and the agreed 20% cap"),
        ("Not counted", "Interest on cash; any lending on our own book; a saver who stops withdraws everything, so their fund fees stop",
         "Conservative by design")]


def p_assume(n=8):
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in assume_rows())
    return page(n, "Appendix", "ASSUMPTIONS", "Every input of the main case, and where it comes from",
                f'<table class="at compact tight" style="font-size:9.5px"><colgroup><col style="width:13%"><col style="width:47%"><col style="width:40%"></colgroup>'
                f'<tr><th>Input</th><th>Value</th><th>Basis</th></tr>{rows}</table>',
                f"{od.GLOSS['sip']}; {od.GLOSS['mandate']}; {od.GLOSS['kyc']}.")


# ---------- 9 the upside appendix: the $1B test, on the main case
UNI_NAMES = {"The plan": "The main case", "Rs 300 a day": "₹300 a day", "Credit-hungry": "Savers who want credit",
             "Credit-hungry + Rs 200 a day": "Want credit + ₹200 a day", "Credit-hungry + Rs 300 a day": "Want credit + ₹300 a day",
             "Capture 10 crore savers": "Capture 10 crore savers"}


def unicorn():
    W, x0 = 1152, 330
    rows = UNIC.to_dict("records") + [dict(CAPR, case="Capture 10 crore savers")]
    mx = max(max(max(r["0.45x AUM m60 Rs cr"], r["20x ARR m60 Rs cr"]) for r in rows), UNI) * 1.04
    X = lambda v: (W - x0 - 230) * v / mx
    s = [T(0, 14, "VALUE AT MONTH 60, ₹ CRORE, ON THE MAIN CASE: FIVE CASES AT 2.5 LAKH ONLINE SAVERS A MONTH, AND THE 10-CRORE PATH", 11.5, 700, SLATE, ls=1.1)]
    for i, r in enumerate(rows):
        y = 28 + i * 56
        ok = str(r["$1B on both at m60"]) == "True"
        pm = int(float(r["EBITDA positive from month"])) if str(r["EBITDA positive from month"]).replace(".", "").isdigit() else 97
        s.append(T(0, y + 22, UNI_NAMES[r["case"]], 14.5, 700, TEAL if ok else INK))
        cap = r["case"] == "Capture 10 crore savers"
        stop = " (sign-ups stop)" if (pm == CAPM and not cap) or (cap and pm <= 96) else ""
        s.append(T(0, y + 40, f"${r['money needed $M']:,.1f}M needed · EBITDA positive {month(pm)}{stop}", 11.5, 500, SLATE))
        for j, (k, lab, col) in enumerate((("20x ARR m60 Rs cr", "20× revenue", NAVY), ("0.45x AUM m60 Rs cr", "0.45× money saved", NAVY4))):
            v = r[k]
            yy = y + 6 + j * 24
            s.append(R(x0, yy, X(v), 20, col, r=5))
            s.append(halo(T(x0 + X(v) + 8, yy + 15, f"{lab}: ₹{v:,.0f} Cr", 12, 700, col)))
    xu = x0 + X(UNI)
    yb = 28 + len(rows) * 56
    s.insert(1, f'<line x1="{xu}" y1="22" x2="{xu}" y2="{yb}" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 5"/>')
    s.append(T(xu, yb + 16, f"$1B = ₹{UNI:,.0f} Cr", 12, 700, RED, "middle"))
    return svg(W, yb + 24, "".join(s))


def unicorn_title():
    ok = [r["case"] for r in UNIC.to_dict("records") if str(r["$1B on both at m60"]) == "True"]
    close = UNIC[["20x ARR m60 Rs cr", "0.45x AUM m60 Rs cr"]].min(axis=1) / UNI
    if ok:
        return (f"On the main case {len(ok)} of {len(UNIC)} cases at 2.5 lakh savers a month clear $1B on both yardsticks by year 5; the cheapest needs "
                f"${UNIC[UNIC['case'].isin(ok)]['money needed $M'].min():.1f}M")
    if str(CAPR["$1B on both at m60"]) == "True":
        return (f"At 2.5 lakh savers a month no case reaches $1B on both yardsticks by year 5; only capturing 10 crore savers does, "
                f"for ${CAPR['money needed $M']:,.0f}M and a third of the segment")
    return f"No path reaches $1B on both yardsticks by year 5 on the main case; the closest falls {1 - close.max():.0%} short"


def p_upside(n):
    conv = float(CAPR["online savers per sign-up if the whole segment signs up"])
    close = UNIC[["20x ARR m60 Rs cr", "0.45x AUM m60 Rs cr"]].min(axis=1) / UNI
    return page(n, "Appendix", "THE UPSIDE: THE $1B TEST, ON THE MAIN CASE", unicorn_title(), unicorn(),
                f"Not the plan. Five cases at 2.5 lakh online savers a month from month 30 (the closest falls {1 - close.max():.0%} short on revenue); sign-ups "
                f"stop at 20% of a 7 crore pool in month {CAPM}, so profit there is acquisition stopping, not the business. The 10-crore path wins "
                f"{ppl(CAPR['online savers won a month (m30 on)'])} online savers a month, so about 1 in {round(1 / conv)} of a 30 crore segment must start saving "
                f"(1 in 5 sign-ups do today); its EBITDA turns positive only as sign-ups stop at month 96, and year 8 is {od.cr(CAPR['Y8 EBITDA Rs cr'])}. "
                "Yardsticks: 20× the month-60 revenue run-rate; 0.45× money saved.")


# ---------- kept for the v4 plan deck: the lender-fee test on the main case
def p_fees(n=4):
    title, body, src = ld.fee_test()
    return page(n, "What has to be true", "WHAT LOANS WOULD HAVE TO BRING", title, body, src)


CSS_EXTRA = (".chips3 { margin-top: 10px !important; gap: 14px; } .chip { font-size: 12.5px; padding: 10px 14px; line-height: 1.4; } "
             ".chip b { font-size: 13.5px; } .at.fin td { padding: 2.5px 8px; } .at.fin th { padding: 3px 8px; }")
STALE = ("7.7×", "₹3 lakh", "₹1.7 lakh", "35% apply", "month 63", "$4.7M", "₹2 a debit", "our targets", "at our target", "1.75×",
         "0.78×", "1.37×", "month 73", "₹126", "2.87×", "$5.0M", "month 67", "3× is out of reach", "measured", "so the main case is cautious",
         "a floor", "THE ODDS", "THE FINANCIALS")
STALE_OK = {"0.78×": ("debt fund's fee moves",)}


def build():
    fns = [p_main_saver, p_odds, p_ladder, p_financials, p_main_levers, p_seed_main, p_assume]   # the $1B page is v4's only (FIXES D1)
    pages = [cover()] + [re.sub(r'(<footer class="pf"><span>[^<]*</span><span>)[^<]*(</span></footer>)', rf"\g<1>{i}\2", f(i))
                         for i, f in enumerate(fns, start=2)]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Online-first business case</title><style>{sp.CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>').replace("</style>", ".at.compact td { padding: 4px 8px; } .at.compact th { padding: 4px 8px; } .at.tight td { padding: 3px 8px; line-height: 1.3; }" + CSS_EXTRA + "</style>", 1)
    html = re.sub(r"\bRs\.?\s?(?=\d)", "₹", html)
    text = re.sub(r"<[^>]+>", " ", html)
    for bad in ("Bueno", "BetterPlace", ".py", ".csv", "tables/", "nobody serves both", "clawback") + STALE:
        for m in re.finditer(re.escape(bad), text, re.I if bad.lower() == bad else 0):
            ctx = text[max(0, m.start() - 220):m.end() + 20]
            assert any(ok in ctx for ok in STALE_OK.get(bad, ())), (bad, ctx)
    assert not re.search(r"\b(DSA|MDR|TER|NPV)\b", text), "unexplained jargon"
    assert not re.search(r"\b(he|his|him|she|her|hers)\b", text, re.I), "gendered word"
    out = HERE / "Online_business_case.html"
    out.write_text(html)
    pdf = HERE / "Online_business_case.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, capture_output=True)
    print("wrote", pdf, len(pages), "pages")


if __name__ == "__main__":
    build()

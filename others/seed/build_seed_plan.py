"""Seed plan, investor version (21 Oct 2026). Name is a WORKING name (operator: "Keep name tentive (savemore/ save 91 etc)"). Landscape 16:9 pages, one claim per page.
Operator: "beautification of the document is required ... quality isnt good to be shareable with any VC".
Audience: seed investors. So no internal language (operator / judgement / file names / research IDs) on the pages;
sources are named in plain words; the internal critical review is NOT in this document.
Numbers: tables/seed_plans.csv, seed_people.csv, seed_sensitivity.csv (model/seed_plan.py).
REBASE 24 Oct (reviews/2026-10-24_rebase/BRIEF.md): everything said about the business AFTER the seed is the main case
(ltv_saver_split, ltv_odds_summary, ltv_ladder, ltv_upside_levers, online_levers, online_ltv_levers, online_unit), read from
the tables by main_case(), never retyped. Story: the seed's job is to measure the facts that decide the business. One case;
the ladder and the levers are targets to prove, never other plans. The seed's own budget, team, timeline and ask are unchanged.
Other builders import this module as `sp` (CSS, colours, svg helpers, PHASES, flow, p_funds, p_reg): keep those names and
signatures stable, and keep import free of new work (main_case() is lazy).
Builds seed/Seed_Plan_investor.html and .pdf (Chrome headless)."""
import math
import re
import subprocess
from functools import lru_cache
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


# ---------- the main case after the seed (24 Oct rebase), read lazily so `import build_seed_plan` stays cheap ----------
def _half_up(v, places):
    from decimal import ROUND_HALF_UP, Decimal
    return Decimal(str(float(v))).quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP)


def x2(v):
    """LTV/CAC to 2 decimals, half up on the table's value (1.255 -> 1.26, as online_ltv_levers.csv rounds it)."""
    return f"{_half_up(v, 2)}×"


def pct(v):
    return f"{_half_up(float(v) * 100, 0)}%"


def pct1(v):
    """One decimal only where it matters (0.4045 -> 40.5%, 0.45 -> 45%)."""
    s = f"{_half_up(float(v) * 100, 1)}"
    return (s[:-2] if s.endswith(".0") else s) + "%"


def usdm(v, plus=False):
    """$M to 1 decimal, half up (8.09 -> $8.1M, 4.04 -> $4.0M); '+' = at least, where the company is still losing money at month 96."""
    return f"${_half_up(v, 1)}M" + ("+" if plus else "")


# FIXES.md B8 (lead, 24 Oct round 2): not in any table this builder reads
RUN_ON_FOOTNOTE = "if run on, the cash hole bottoms around year 12 at about $10.6M"


def _num(s):
    """'daily 125.6' / 'r12 0.4123' / '_apply 0.3862 (beyond the upside)' -> the first number; 'not reachable' -> None."""
    m = re.search(r"\s(\d+(?:\.\d+)?)", f" {s}")
    return float(m.group(1)) if m else None


def _ebitda(v):
    """Month the company turns EBITDA-positive, or None if not by month 96 ('after m96' / 97)."""
    v = str(v).strip()
    return None if v.startswith("after") or float(v) > 96 else int(float(v))


@lru_cache(maxsize=None)
def main_case():
    split = pd.read_csv(TAB / "ltv_saver_split.csv")
    sv = {y: split[(split.case == "Main case") & (split.years == y)].iloc[0] for y in ("5y", "8y")}
    odds = pd.read_csv(TAB / "ltv_odds_summary.csv").set_index("measure")
    lad = pd.read_csv(TAB / "ltv_ladder.csv").set_index("rung")
    up = pd.read_csv(TAB / "ltv_upside_levers.csv").set_index("lever")
    lv = pd.read_csv(TAB / "online_levers.csv").set_index("case")
    sl = pd.read_csv(TAB / "online_ltv_levers.csv").set_index("case")
    unit = pd.read_csv(TAB / "online_unit.csv").set_index("saver").loc["Online saver"]
    plan = lv.loc["The plan"]
    m = lad.loc["Main case"]
    assert _ebitda(plan["EBITDA positive from month"]) is None, "the seed plan says the main case is not EBITDA-positive by month 96"
    dr = pd.read_csv(TAB / "ltv_odds_drivers.csv").set_index("input").loc["trail"]
    lo, hi = _num(dr["low"]), _num(dr["high"])
    debt = lo + float(m["drawn position (0 low, 1 high)"]) * (hi - lo)     # the main case's debt-fund fee (use_main_case)
    old = "Loan funnel at our old targets"
    return {
        "sv5": sv["5y"], "sv8": sv["8y"], "cac": float(sv["5y"]["cost to win"]),
        "band": (float(lad.loc["Low end (30% still saving)", "LTV/CAC 5y"]), float(lad.loc["High end (40% still saving)", "LTV/CAC 5y"])),
        "debt_lo": lo, "debt_hi": hi, "debt": debt, "blend": 0.8 * 0.0075 + 0.2 * debt,   # 80/20 at a 0.75% equity fee (online_plan.py)
        "cac600": sl.loc["Cost to win Rs 600 (our funnel)"], "need600": float(lv.loc["Cost to win Rs 600 (our funnel)", "money needed $M"]),
        "old": sl.loc[old], "old_month": _ebitda(lv.loc[old, "EBITDA positive from month"]),
        "pay": int(odds.loc["Saver pays back in month (97 = not by 96)", "P50"]),
        "p10_5": odds.loc["LTV/CAC, 5 years", "P10"], "p90_5": odds.loc["LTV/CAC, 5 years", "P90"],
        "p10_8": odds.loc["LTV/CAC, 8 years", "P10"], "p90_8": odds.loc["LTV/CAC, 8 years", "P90"],
        "cum96": odds.loc["Cumulative EBITDA to month 96, Rs crore", "P50"],
        "level": int(plan["online savers won a month (m30 on)"]), "need": float(plan["money needed $M"]),
        "r12": float(unit["still saving at 12 months"]), "daily": float(m["saved a day Rs"]),
        "apply": float(m["apply a year"]), "approved": float(m["first loans approved"]),
        "lad": lad, "up": up, "sl": sl, "lv": lv,
        "daily_1x": _num(up.loc["daily", "alone for 1x (5y)"]), "keep_1x": _num(up.loc["keep_up", "alone for 1x (5y)"]),
        "daily_up": _num(up.loc["daily", "upside"]), "keep_up": _num(up.loc["keep_up", "upside"].split(";")[0]),
        "keep_up_drop": _num(up.loc["keep_up", "upside"].split(";")[1]),
        "apply_up": _num(up.loc["apply", "upside"]), "approved_up": _num(up.loc["approved", "upside"]),
        "debit2": sl.loc["We pay Rs 2 a debit, weekly"], "fee05": sl.loc["Equity fund fee 0.5%, not 0.75%"],
        "need_debit2": float(lv.loc["We pay Rs 2 a debit, weekly", "money needed $M"]),
        "need_fee05": float(lv.loc["Equity fund fee 0.5%, not 0.75%", "money needed $M"]),
    }


def active_m18():
    """Savers still saving at month 18: the seed's own monthly sign-ups (tables/seed_monthly_pitch.csv), with online savers
    kept at the main case's still-saving rate (online_unit.csv) on the seed model's steady monthly drop-off; the doorstep
    arm keeps its own 55%. (seed_plans.csv's active_savers_m18 used the 21 Oct 38%.)"""
    d = pd.read_csv(TAB / "seed_monthly_pitch.csv")
    s, act = main_case()["r12"] ** (1 / 12), 0.0
    for r in d[d.month <= 18].itertuples():
        act = act * s + r.new_online_savers
    return act + float(d.loc[d.month == 18, "active_offline"].iloc[0])


def debits_24_usd():
    """The seed budget's payments line: Rs 2 a weekly debit on every active saver (model/seed_plan.py DEBITS), 24 months."""
    d = pd.read_csv(TAB / "seed_monthly_pitch.csv")
    d = d[d.month <= 24]
    return float((d.active_online + d.active_offline).sum() * 2 * 52 / 12 / FX)


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
def cover_unconfirmed():
    """FIXES.md B3: the two unconfirmed inputs, said on the cover."""
    mc = main_case()
    return (f"The business case assumes debits cost us ₹0 and a 0.75% equity fund fee, both still to be confirmed in writing: "
            f"₹2 a weekly debit, or a 0.5% fee, would cut what a saver earns back in 5 years from {x2(mc['sv5']['LTV/CAC'])} of the "
            f"cost to win them to about {x2(mc['debit2']['LTV/CAC 60m'])} or {x2(mc['fee05']['LTV/CAC 60m'])}. The seed gets both in writing before launch.")


def cover():
    share = lambda v: f"{v / RAISE:.0%}"
    tiles = [("$500k", "seed raise"), ("24 months", f"plan period, plus a {RES / RAISE:.0%} contingency"),
             (ppl(P.customers), f"sign-ups; ~{ppl(round(P.savers_won, -2))} start saving, ~{ppl(round(active_m18(), -2))} still saving at month 18"),
             ("5 people", "Piyush (CEO), Sandeep (CPTO) + 3 hires")]
    t = "".join(f'<div class="ctile"><div class="cbig">{a}</div><div class="csub">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle">Seed plan</div>
  <div class="ctag">Daily saving for India's self-employed, in mutual funds, in their own name. Online-first across India, with a doorstep pilot in NCR.</div>
  <div class="cmeta">Raising $500k · October 2026 · Confidential</div>
</div>
<div class="cright">
  <div class="cgrid">{t}</div>
  <div class="csplit">
    <div style="flex:{TP:.0f};background:{NAVY}">Product and team · {share(TP)}</div>
    <div style="flex:{ACQ:.0f};background:{TEAL}">Customer acquisition · {share(ACQ)}</div>
    <div style="flex:{RES:.0f};background:{SLATE}">Contingency · {share(RES)}</div>
  </div>
  <div class="cnote">To build the product and measure the five facts that decide the business. Revenue is not counted anywhere in the seed budget.</div>
  <div class="cnote">{cover_unconfirmed()}</div>
</div>
</section>"""


# ---------- page 2: the seed's job (24 Oct rebase) ----------
def facts_chart():
    """One fact at a time from the main case: what it does to one saver's 5-year return (LTV/CAC)."""
    mc, up = main_case(), main_case()["up"]
    base = float(mc["sv5"]["LTV/CAC"])
    # FIXES.md B4 (fact 4 = the fee on the fund the Rs 100 goes into), B5 (Rs 100 = our floor), B9 (45% includes the 1.0% drop-off), B10
    rows = [("Average daily amount", f"₹{mc['daily']:.0f} a day, our product's floor", float(up.loc["daily", "LTV/CAC 5y at the upside alone"]),
             f"at ₹{mc['daily_up']:.0f} a day", f"₹{mc['daily_1x']:.0f} alone gives 1×"),
            ("Still saving at 12 months", f"{pct(mc['r12'])}: Bachatt's 30–40%", float(up.loc["keep_up", "LTV/CAC 5y at the upside alone"]),
             f"at {pct1(mc['keep_up'])}, {mc['keep_up_drop']:.1%} drop-off", f"{pct1(mc['keep_1x'])} alone gives 1×"),
            ("Debits cost us ₹0", "unconfirmed: BSE StAR MF / fund house", float(mc["debit2"]["LTV/CAC 60m"]),
             "at ₹2 a weekly debit", "so: ₹0 in writing"),
            ("Fee on the fund we use", f"unconfirmed: {mc['blend']:.2%} blended or better", float(mc["fee05"]["LTV/CAC 60m"]),
             "at 0.5% on equity", "so: the fee in writing"),
            ("The loan funnel", f"{pct(mc['apply'])} apply a year, {pct(mc['approved'])} approved", float(up.loc["apply", "LTV/CAC 5y at the upside alone"]),
             f"at {pct(mc['apply_up'])} applying", f"all three at old targets: {x2(mc['old']['LTV/CAC 60m'])}")]
    X = lambda v: 215 + v * 160
    top, rh = 34, 62
    s = [f'<line x1="{X(base)}" y1="{top - 6}" x2="{X(base)}" y2="{top + len(rows) * rh}" stroke="{NAVY}" stroke-width="2.4"/>',
         f'<line x1="{X(1)}" y1="{top - 6}" x2="{X(1)}" y2="{top + len(rows) * rh}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>',
         T(X(base) - 6, top - 12, f"main case {x2(base)}", 12, 700, NAVY, "end"), T(X(1) + 6, top - 12, "1× = cost paid back", 12, 700, RED)]
    for i, (name, sub, v, a1, a2) in enumerate(rows):
        y = top + i * rh
        col = TEAL if v > base else RED
        lo, hi = sorted((X(base), X(v)))
        s.append(T(0, y + 22, name, 14.5, 700))
        s.append(T(0, y + 41, sub, 12, 500, SLATE))
        s.append(R(lo, y + 12, hi - lo, 24, col, r=5))
        # a value just short of 1x would sit on the dashed 1x line: put it just past the line instead
        s.append(T(max(X(v), X(1) if v > 0.9 else 0) + 6, y + 29, x2(v), 13, 700, col) if v > base else T(X(v) - 6, y + 29, x2(v), 13, 700, col, "end"))
        s.append(T(545, y + 22, a1, 12.5, 700, col))
        s.append(T(545, y + 41, a2, 12, 500, SLATE))
    ya = top + len(rows) * rh
    s.append(f'<line x1="{X(0)}" y1="{ya}" x2="{X(1.8)}" y2="{ya}" stroke="{LINE}" stroke-width="1.5"/>')
    for t, lab in ((0, "0"), (0.5, "0.5×"), (1, "1×"), (1.5, "1.5×")):
        s.append(T(X(t), ya + 16, lab, 11, 600, MUTE, "middle"))
    return svg(720, ya + 22, "".join(s))


def p_job():
    mc = main_case()
    s5, s8 = mc["sv5"], mc["sv8"]
    # FIXES.md B1: the cross-sell answer first, in rupees, before and after serving; then the return with fund fees (net of serving)
    cross = (f"<b>Cross-selling alone</b> (loans and cards): {rs(s5['cross-sell'])} per saver in 5 years, {rs(s8['cross-sell'])} in 8. That is "
             f"{x2(s5['cross-sell / CAC'])} and {x2(s8['cross-sell / CAC'])} of the {rs(mc['cac'])} it costs to win a saver, before serving, and less "
             f"than the {rs(s5['serving'])} / {rs(s8['serving'])} it costs to serve them, so on its own it never pays back "
             f"({x2(s5['cross-sell net of serving / CAC']).replace('-', '−')} after serving). Insurance, recharge, bills, fixed deposits and pensions are not counted.")
    tiles = [(x2(s5["LTV/CAC"]), f"in 5 years: {rs(s5['net'])} back on the {rs(mc['cac'])} cost to win them"),
             (x2(s8["LTV/CAC"]), f"in 8 years: {rs(s8['net'])}"),
             (f"Month {mc['pay']}", "when a saver has paid back the cost to win them")]
    t = "".join(f'<div class="jt"><b>{a}</b><span>{b}</span></div>' for a, b in tiles)
    left = (f'<div class="jl"><div class="sub-h" style="margin-top:0">ONE SAVER, AT TODAY\'S MARKET NUMBERS</div><div class="jbox">{cross}</div>'
            f'<div class="sub-h">WITH FUND FEES, AFTER SERVING</div>{t}</div>')
    right = f'<div class="jr"><div class="sub-h" style="margin-top:0">WHAT EACH FACT DOES TO ONE SAVER\'S 5-YEAR RETURN, ONE AT A TIME</div>{facts_chart()}</div>'
    return page(2, "Why this seed", "THE SEED'S JOB", "The seed's job is to measure the five facts that decide the business",
                "Two of them can each lift a saver past 1× on their own. Two are still unconfirmed and must be put in writing. "
                "No single loan number reaches 1×.",
                f'<div class="job">{left}{right}</div>',
                "5-year return (LTV/CAC) = what a saver brings in over 5 years, less the cost of serving them, divided by what it costs to win them. Main case: "
                "inputs fixed by the founders on 24 October (market figures, Bachatt, or our judgement; appendix). We ran the model 1,000 times, picking "
                f"retention (Bachatt's 30–40%) and the debt fund's fee at random within their ranges: 8 in 10 draws give {x2(mc['p10_5'])}–{x2(mc['p90_5'])} "
                f"at 5 years and {x2(mc['p10_8'])}–{x2(mc['p90_8'])} at 8.")


# ---------- page 3: use of funds ----------
TP_ITEMS = [("Salaries: 2 founders + 3 hires", "Salaries"), ("App: build and running", "App and tech"),
            ("Office and fund-raising", "Office and fund-raising"), ("Setup, licences, compliance", "Licences and compliance"),
            ("Support, payments and per-user tech", "Support"), ("Design while building", "Design (outsourced)")]
ACQ_ITEMS = [("Online sign-ups", "Online acquisition"), ("KYC (identity) checks", "KYC"), ("Doorstep pilot, NCR", "Doorstep test arm")]


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
The company plan raises the next round in month 19, on the facts the seed has measured; it does not count this reserve.</div></div>""" + "</div>"
    return page(3, "Use of funds", "THE $500K", f"The money builds the product first; {RES / RAISE:.0%} is held as contingency",
                "", body, f"All figures over 24 months, at a planning rate of ₹{FX:.0f} per $. Revenue is not included, so every number is a cost.")


# ---------- page 3: product ----------
PHASES = [("1", "Save", "Months 1–3 · live in month 4", NAVY, ["Sign-up with e-KYC and a bank check", "Daily saving from ₹100, likely in one hybrid fund",
                                                               "One UPI Autopay mandate", "Withdraw any day: back in 1–3 working days; equity funds may charge an exit fee in year 1"]),
          ("2", "Habit", "Months 4–9", NAVY2, ["Goals, streaks and nudges", "Referrals (no cashback, by rule)", "Doorstep agent app for the pilot",
                                                "Savings analytics"]),
          ("3", "Offers", "Months 7–12", NAVY3, ["Loan offers for users who opt in; saving improves them", "Insurance via a broker (fixed fee)", "Credit cards from issuers",
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
    # phones scaled to 90% so the glossary line below them clears the last screen
    body = f'<div class="phases">{cards}</div><div class="sub-h">THE FIRST APP: SIX SCREENS</div><div style="width:90%">{phones()}</div>'
    return page(4, "Product", "WHAT THE MONEY BUILDS", "Four releases in 18 months, with customers using it from month 4",
                "", body, "KYC = the identity check every fund investor passes. UPI Autopay mandate = the saver's one-time permission for the daily debit. "
                          "SIP = a standing order to buy a fund, here every day.")


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
    s.append(T(742, 112, "fund fee from the fund house:", 12, 700, NAVY))
    s.append(T(742, 128, "0.75% a year on equity, less on debt (to confirm)", 12, 500, NAVY))
    # withdraw loop
    s.append(f'<path d="M730 228 L730 276 L95 276 L95 238" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    s.append(f'<polygon points="95,228 89,241 101,241" fill="{BLUE}"/>')
    s.append(T(412, 268, "withdraw any day: back in 1–3 working days (exit fees may apply in year 1)", 12.5, 700, BLUE, "middle"))
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
             ("Paid by partners", "Fund houses and lenders pay us. A regular plan costs the saver about 0.5–1% a year more than a direct plan; we say so up front.")]
    c = "".join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in chips)
    return page(5, "How it works", "THE MONEY FLOW", "Money moves from the saver's bank to the fund and back, never through us",
                "", flow() + f'<div class="chips3">{c}</div>',
                "Sources: SEBI (payments come from the investor's own account); BSE StAR MF (no fee to distributors; ₹0 a debit to us, to confirm in "
                "writing); fund-house disclosures.")


# ---------- page 5: regulatory path ----------
REG = [("Before launch · months 0–3", NAVY, NAVY_L, [("Company setup, ₹1.25 lakh", "includes AMFI distributor registration (₹40,000 + GST)"),
                                                   ("NISM exam for both founders", "₹1,500 + GST each; renewed every 3 years"),
                                                   ("BSE StAR MF access", "orders and daily SIP mandates; no transaction fee to distributors; ₹0 a debit to us, in writing"),
                                                   ("3–5 fund houses", "empanelled; the ₹100 daily minimum and the fee on the fund we use ({blend} blended or better), in writing"),
                                                   ("KYC and UPI Autopay partners", "e-KYC ₹3–7 a check (₹40 budgeted per KYC with KRA, PAN and bank checks); daily mandates allowed"),
                                                   ("Data protection", "consent flows and data kept in India")]),
       ("After launch · months 4–12", NAVY3, "#eef4fb", [("Loans as a lender's marketing partner", "from month 7: partner lenders pay us a fee per loan (a direct selling agent); RBI digital-lending rules apply (the borrower pays us nothing)"),
                                      ("Insurance through a broker partner", "from month 7, for a fixed referral fee; our own registration later"),
                                      ("Credit cards with issuers", "the issuer decides every card"),
                                      ("Legal opinions first", "lender-offer consent, the insurance fee, agent rules; agents never handle cash")]),
       ("With the next round", SLATE, "#f1f5f9", [("Deeper lender partnerships", "larger fees on a proven book; first-loss cover only with its own capital (up to 5% of loans, held as cash)"),
                                                 ("Own NBFC (non-bank lender)", "₹10 crore of capital; about 8–14 months or more"),
                                                 ("Insurance distribution licence", "under IRDAI's draft rules, once final")])]


def p_reg():
    cols, blend = "", f"{main_case()['blend']:.2%}"      # the main case's blended fund fee (FIXES.md B4)
    for head, col, bg, its in REG:
        cards = "".join(f'<div class="rcard" style="border-color:{col};background:{bg}"><b style="color:{col}">{a}</b>'
                        f'<span>{b.replace("{blend}", blend)}</span></div>' for a, b in its)
        cols += f'<div class="rcol"><div class="rhead" style="background:{col}">{head}</div>{cards}{"<!--NEVER-->" if col == NAVY3 else ""}</div>'
    never = ["Hold customer money", "Offer cashback on funds or insurance", "Run lucky draws or savings circles", "Use anyone's data without consent"]
    nv = "".join(f'<div class="nv">✕ {n}</div>' for n in never)
    cols = cols.replace("<!--NEVER-->", f'<div class="never"><b>We will never</b>{nv}</div>')
    body = f'<div class="rcols">{cols}</div>'
    return page(6, "Regulatory path", "LICENCES AND TIE-UPS", "Day one needs no RBI licence; each later step adds one", "", body,
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
    return page(7, "Team", "FIVE PEOPLE", f"Five people, and {k(P.salaries_24_usd)} of salaries over 24 months",
                "", body, "Founders draw $1,000 a month each until the next round. Hire pay is monthly cost to company. Design is outsourced while the app is built.")


# ---------- page 7: customers ----------
def funnel():
    on_reg = P.online_registrations
    kyc = on_reg * 0.5
    on_sav = P.savers_won - P.doorstep_signups
    rows = [("Online sign-ups", on_reg, TEAL, "₹100 each"), ("Finish KYC", kyc, "#7fd1c6", "1 in 2"), ("Start saving, online", on_sav, "#0b7f70", "2 in 5 of KYC'd"),
            ("Doorstep savers", P.doorstep_signups, AMBER, f"{int(P.agents)} agents; saving starts at sign-up"), ("Savers won", P.savers_won, "#0b5d52", f"{P.doorstep_signups / P.savers_won:.0%} from the doorstep"),
            ("Still saving at month 18", active_m18(), "#0b6b5e", "")]
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
    r12 = pct(main_case()["r12"])
    return page(8, "Customers", "1 LAKH SIGN-UPS", f"1 lakh sign-ups for {k(ACQ)}, and the plan holds even if they cost twice as much",
                "", body, "Install costs, vendor benchmarks: fintech median ₹75, wealth apps ₹100–300. Still saving at 12 months: "
                          f"{r12} online, the middle of Bachatt's 30–40% (SBI MF's ₹250 daily SIP agrees, about 38%), and the seed measures it; "
                          "55% at the doorstep.")


# ---------- page 8: milestones ----------
def gantt():
    END = 24
    x0, W = 250, 1152
    w = (W - x0) / END
    X = lambda m: x0 + (m - 1) * w
    rows = [("Set up: company, AMFI, NISM", 1, 1, NAVY), ("Fund houses, exchange, KYC, mandates", 1, 3, NAVY),
            ("Release 1: Save", 1, 3, NAVY), ("Release 2: Habit", 4, 9, NAVY2), ("Release 3: Offers", 7, 12, NAVY3),
            ("Release 4: Score and plan", 10, 18, NAVY4), ("Keep building", 19, END, "#9fb8d6"),
            ("Online customers", 4, 18, TEAL), ("Doorstep pilot, NCR", 4, 18, AMBER), ("Next round", 16, 21, INK)]
    s, rh = [], 18
    for m in range(1, END + 1):
        s.append(T(X(m) + w / 2, 12, str(m), 10.5, 600, MUTE, "middle"))
        if m % 3 == 1:
            s.append(f'<line x1="{X(m)}" y1="20" x2="{X(m)}" y2="{24 + len(rows) * rh}" stroke="{LINE}"/>')
    for i, (lab, a, b, col) in enumerate(rows):
        y = 22 + i * rh
        s.append(T(0, y + 13, lab, 12, 600))
        s.append(R(X(a) + 1, y + 3, (b - a + 1) * w - 2, 12, col, r=5))
    yb = 26 + len(rows) * rh
    for m, lab, col, anc, dx in ((3, "Terms in writing", NAVY, "end", 6), (4, "Launch", TEAL, "start", -6), (7, "3 months of data", "#0b7f70", "middle", 0),
                                 (10, "6 months of data", AMBER, "middle", 0), (16, "12 months of data", RED, "middle", 0), (24, "Plan ends", SLATE, "end", 10)):
        xm = X(m) + w / 2
        s.append(f'<polygon points="{xm},{yb} {xm - 7},{yb + 10} {xm},{yb + 20} {xm + 7},{yb + 10}" fill="{col}"/>')
        s.append(T(xm + dx, yb + 36, lab, 11.5, 700, col, anc))
    return svg(W, yb + 42, "".join(s))


def p_milestones():
    # 24 Oct rebase: the gates are the five facts that decide the business, each with its main-case value and the line from
    # the main case's levers (ltv_upside_levers.csv, online_ltv_levers.csv, online_levers.csv = the business case's numbers)
    mc = main_case()
    base = x2(mc["sv5"]["LTV/CAC"])
    need = usdm(mc["need"], plus=True)            # every lever row quoted here is still losing money at month 96 ("after m96")
    gates = [("By month 3, before launch", "₹0 debit cost, in writing (unconfirmed)", NAVY,
              f"From BSE StAR MF and the fund houses, likely one hybrid fund taking the whole ₹100. At ₹2 a weekly debit: "
              f"{x2(mc['debit2']['LTV/CAC 60m'])}, not {base}, and {usdm(mc['need_debit2'], True)} needed, not {need}."),
             ("By month 3, before launch", "The fee on our fund, in writing (unconfirmed)", NAVY,
              f"The fee on the fund the ₹100 goes into: {mc['blend']:.2%} blended or better (0.75% on equity, about "
              f"{mc['debt']:.2%} on debt, 80/20). At 0.5% on equity: {x2(mc['fee05']['LTV/CAC 60m'])}, {usdm(mc['need_fee05'], True)}."),
             ("Month 7: three months of savers", "The average daily amount", "#0b7f70",
              f"₹{mc['daily']:.0f} is our product's floor; Bachatt's average is unknown and its own minimums are lower. An average of "
              f"₹{mc['daily_1x']:.0f} gives 1× on its own."),
             ("Months 7 and 10, final at month 16", "Still saving at 12 months", AMBER,
              f"Early reads at 3 and 6 months, the full year at month 16. {pct(mc['r12'])} is the main case; "
              f"{pct1(mc['keep_1x'])} gives 1× on its own."),
             ("Months 7–16, from the first offers", "The real loan funnel", NAVY3,
              f"Who opts in, applies for a first loan and is approved. The main case: {pct(mc['apply'])} apply a year, "
              f"{pct(mc['approved'])} approved (the founders' market figure, between 11% and 25%)."),
             ("Months 4–18", "Cost to win, and the doorstep arm", SLATE,
              f"The seed budgets ₹600 an online saver ({rs(round(P.acq_per_saver, -1))} with the doorstep) and measures it; ₹450 at scale "
              f"is the founders' figure. The doorstep arm stays only if it clearly beats online's still-saving rate.")]
    g = "".join(f'<div class="fact" style="border-top-color:{col}"><i style="color:{col}">{when}</i><b>{a}</b><em>{b}</em></div>'
                for when, a, col, b in gates)
    body = gantt() + f'<div class="sub-h" style="margin-top:4px">WHAT THE SEED MEASURES, AND WHEN</div><div class="facts">{g}</div>'
    return page(9, "Milestones", "24 MONTHS", "Build, launch, measure the five facts, then raise on 12 months of data", "", body)


# ---------- page 10: the company after the seed (what it takes) ----------
def p_company():
    mc = main_case()
    lad = mc["lad"]
    rungs = [("Main case", "Main case: the plan", True), ("1×", "A saver worth 1×", False), ("2×", "A saver worth 2×", False),
             ("3×", "A saver worth 3×", False)]

    def bar(v):
        return (f'<svg viewBox="0 0 132 16" width="132" height="16" style="vertical-align:middle"><rect x="0" y="3" width="{min(v, 3.2) * 40:.1f}" height="10" rx="3" '
                f'fill="{TEAL if v >= 1 else NAVY}"/><line x1="40" y1="0" x2="40" y2="16" stroke="{RED}" stroke-width="1.6" stroke-dasharray="3 2"/></svg>')
    head = ("<tr><th></th><th>Saved a day</th><th>Still saving at 12 months</th><th>Apply for a loan a year</th><th>First loans approved</th>"
            "<th>One saver, 5 years</th><th>8 years</th><th>Saver pays back</th><th>Company EBITDA-positive</th><th>Money needed</th></tr>")
    rows = ""
    for key, label, is_main in rungs:
        r = lad.loc[key]
        e = _ebitda(r["EBITDA positive from month"])
        money = usdm(mc["need"] if is_main else float(r["money needed $M"]), plus=e is None)
        rows += (f'<tr class="{"main" if is_main else ""}"><td>{label}</td><td>₹{float(r["saved a day Rs"]):.0f}</td><td>{pct(r["still saving at 12 months"])}</td>'
                 f'<td>{pct(r["apply a year"])}</td><td>{pct(r["first loans approved"])}</td>'
                 f'<td>{bar(float(r["LTV/CAC 5y"]))} <b>{x2(r["LTV/CAC 5y"])}</b></td><td>{x2(r["LTV/CAC 8y"])}</td>'
                 f'<td>month {int(r["saver pays back in month"])}</td><td>{"not by month 96" if e is None else f"from month {e}"}</td><td>{money}</td></tr>')
    one, two, top = lad.loc["1×"], lad.loc["2×"], lad.loc["All upside"]
    lo, hi = mc["band"]
    notes = [("The main case is the plan", f"₹{mc['daily']:.0f} a day, {pct(mc['r12'])} still saving and today's loan market; across Bachatt's 30–40% "
              f"still saving it spans {x2(lo)}–{x2(hi)}. The other rows are targets the seed must prove, not other plans."),
             ("1× is not enough", f"At 1× the company still loses money at month 96 ({usdm(float(one['money needed $M']), True)}). How 1× comes "
              f"matters: all three loan numbers at our old targets give {x2(mc['old']['LTV/CAC 60m'])} and profit from month {mc['old_month']}, "
              "as loan fees arrive early and fund fees build slowly."),
             (f"{usdm(mc['need'], True)} is the least it needs", f"At the main case the cash hole is still deepening at month 96 (about "
              f"₹{abs(mc['cum96']):.0f} Cr of operating losses by then); {RUN_ON_FOOTNOTE}.")]
    nt = "".join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in notes)
    body = f'<table class="at lad">{head}{rows}</table><div class="chips3" style="margin-top:14px">{nt}</div>'
    return page(10, "After the seed", "WHAT THE NEXT ROUND NEEDS",
                f"At the main case the company isn't profitable within 8 years; a saver worth 2× brings profit from month {_ebitda(two['EBITDA positive from month'])}",
                f"At {mc['level']:,} online savers won a month from month 30, each saver earns back less than the cost to win them within 5 years, "
                "so growing faster deepens the loss.",
                body,
                f"Each row moves the five levers together from the main case towards all five at their upside (₹{float(top['saved a day Rs']):.0f} a day, "
                f"{pct1(top['still saving at 12 months'])} still saving with a {float(top['drop-off a month after 12']):.1%} drop-off a month after, "
                f"{pct(top['apply a year'])} applying, {pct(top['first loans approved'])} approved, yearly rises of {pct(top['take-up rise a year'])} and "
                f"{pct(top['approval rise a year'])}). Money needed = the seed + the deepest cash hole (fees arrive 2 months late) + a ₹5 crore cash buffer, "
                f"at ₹{FX:.0f} = $1; + = at least. EBITDA = operating profit before interest, tax and depreciation.")


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
          ("Still saving at 12 months", "{r12} online · 55% doorstep",   # {r12}: the main case's, filled in by p_assume()
           "Online: the middle of Bachatt's 30–40% (SBI MF's ₹250 daily SIP agrees, about 38%); doorstep: our street-savings estimate"),
          ("Doorstep agent", "₹26,000 a month all-in; 100 sign-ups a month, saving from sign-up", "Our estimate, from field-sales practice"),
          ("Customer support", "₹5 per active saver a month", "Our estimate"),
          ("Revenue", "not counted", "Fund fees and lender payouts would only add to the money")]


def p_assume():
    # 24 Oct rebase: online still-saving = the main case's; the payments line says what the budget carries and why
    rows = [(a, b.replace("{r12}", pct(main_case()["r12"])), c) for a, b, c in ASSUME]
    rows.insert([r[0] for r in rows].index("Customer support") + 1,
                ("Payments", f"₹2 a weekly debit, budgeted ({k(debits_24_usd())} over 24 months)",
                 "Kept until the main case's ₹0 a debit (unconfirmed) is in writing"))
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    body = f'<table class="at tight"><tr><th>Assumption</th><th>Value</th><th>Basis</th></tr>{tr}</table>'
    return page(11, "Appendix", "ASSUMPTIONS: THE SEED", "Every number in the seed budget, and where it comes from", "", body)


def p_main_inputs():
    mc = main_case()
    lad = mc["lad"]
    m = lad.loc["Main case"]
    drop = lambda rung: f"{pct1(lad.loc[rung, 'still saving at 12 months'])} ↔ {float(lad.loc[rung, 'drop-off a month after 12']):.1%}"
    reach = float(pd.read_csv(TAB / "online_unit.csv").set_index("saver").loc["Online saver", "loan reach (KYC'd users per saver won)"])
    c600 = mc["cac600"]
    unconf = "Unconfirmed; in writing, month 3"
    rows = [("Saved a day", f"₹{mc['daily']:.0f} a day, about 20 debit days a month",
             "Our product's floor; Bachatt's average is unknown, and its own minimums are lower (₹51/₹101 a day; ₹20 for its liquid fund)",
             "Seed measures it (month 7)"),
            ("Still saving at 12 months", f"{pct(mc['r12'])}, then about {float(m['drop-off a month after 12']):.0%} stop a month",
             f"Middle of Bachatt's 30–40% (SBI MF's ₹250 daily SIP agrees, about 38%); the drop-off moves with it: {drop('Low end (30% still saving)')}, "
             f"{drop('High end (40% still saving)')}, {drop('All upside')}", "Seed measures it (month 16)"),
            ("Each daily debit, cost to us", "₹0", "BSE StAR MF or the fund house's own mandate: free to distributors", unconf),
            ("Fee on the fund we use", f"0.75% a year on equity, about {mc['debt']:.2%} on debt ({mc['debt_lo']:.2%}–{mc['debt_hi']:.2%}); "
             f"80/20 = {mc['blend']:.2%} blended", f"If one hybrid fund takes the whole ₹100 (daily minimums are about ₹100 a fund), its fee must be "
             f"about {mc['blend']:.2%} or more", unconf),
            ("First personal or business loan", "₹70,000; repeats 10% bigger a year repaid, plus top-ups", "Bachatt's number", "Seed measures it (months 7–16)"),
            ("Apply for a loan", f"{pct(mc['apply'])} of the users we can reach, a year; no yearly rise", "The founders' market figure",
             "Seed measures it (months 7–16)"),
            ("First loans approved", f"{pct(mc['approved'])} for personal and business loans (gold 70%, home and property 45%); no yearly rise",
             "The founders' market figure, between 11% (an app lender's new applicants) and 25% (our own past data)", "Seed measures it (months 7–16)"),
            ("Lender payout; home and property loans", "2% of the loan, flat; ₹12 lakh home, ₹5 lakh against property", "Middle of the market's 1–3%; market sizes",
             "Market"),
            ("KYC'd users who don't save", f"About 1.5 come with each saver, see offers and fade within about 3 months: {reach - 1:.2f} of a saver",
             "Lenders rarely approve a user in their first months", "Our judgement"),
            ("Cost to win a saver", f"₹450 at scale + the 10% contingency = {rs(mc['cac'])}; the seed budgets ₹600 while the brand is new",
             f"₹450 is the founders' figure (they call it \"fairly sorted\"). At ₹600 for good ({rs(c600['cost to win Rs'])} with contingency): "
             f"{x2(c600['LTV/CAC 60m'])} / {x2(c600['LTV/CAC 96m'])}, {usdm(mc['need600'], True)}", "Founders' figure; the seed measures it"),
            ("Serving a saver", f"₹5 support a month per saver still saving + ₹4 tech per KYC'd user reached ({reach:.2f} a saver), + 10% contingency",
             "Our estimate", "Our judgement"),
            ("The company", f"{mc['level']:,} online savers won a month from month 30; 1 in 10 from doorstep agents",
             "Tax 25% after losses; no interest on cash counted", "Our plan")]
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)
    body = f'<table class="at tight four">{"<tr><th>Input</th><th>Main case</th><th>Basis</th><th>How sure</th></tr>"}{tr}</table>'
    return page(12, "Appendix", "ASSUMPTIONS: AFTER THE SEED", "The main case after the seed: every input, and how sure we are", "", body,
                f"Fixed by the founders on 24 October (market figures, Bachatt, or our judgement). Cards: 3% of savers still saving at month 7 take one "
                f"({rs(mc['sv5']['Cards'])} a saver won). Consumer-durable and two-wheeler loans sit outside the apply funnel. Not counted: insurance, recharge, "
                "bills, fixed deposits, pensions, loans against savings. A saver who stops withdraws everything. The app never holds money.")


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
.gate {{ border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px; background: {BG}; }}
.gate span {{ display: inline-flex; width: 24px; height: 24px; border-radius: 50%; background: {NAVY}; color: #fff; font-size: 12px; font-weight: 700;
             align-items: center; justify-content: center; margin-bottom: 6px; }}
.gate b {{ display: block; font-size: 13px; }} .gate em {{ font-style: normal; font-size: 11.5px; line-height: 1.35; color: {SLATE}; }}
/* assumptions */
.at {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
.at th {{ text-align: left; font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: {SLATE}; border-bottom: 2px solid {NAVY}; padding: 6px 10px; }}
.at td {{ padding: 6.5px 10px; border-bottom: 1px solid {LINE}; }}
.at td:first-child {{ font-weight: 600; width: 26%; }} .at td:last-child {{ color: #475569; }}
"""


# this document's own pages (24 Oct rebase); kept out of CSS, which other builders import as sp.CSS
SEED_CSS = f"""
.job {{ display: grid; grid-template-columns: 392px 1fr; gap: 40px; }}
.jt {{ background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 6px 16px 8px; margin-bottom: 7px; display: flex; align-items: baseline; gap: 14px; }}
.jt b {{ font-size: 27px; color: {NAVY}; letter-spacing: -.01em; white-space: nowrap; min-width: 120px; }} .jt span {{ font-size: 13px; color: {SLATE}; line-height: 1.35; }}
.jbox {{ border-left: 5px solid {AMBER}; background: {AMBER_L}; border-radius: 10px; padding: 10px 14px; font-size: 13px; line-height: 1.45; }}
.facts {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px 14px; }}
.fact {{ border: 1px solid {LINE}; border-top: 4px solid; border-radius: 10px; padding: 7px 12px 8px; background: {BG}; }}
.fact i {{ display: block; font-style: normal; font-size: 10.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }}
.fact b {{ display: block; font-size: 13.5px; margin: 1px 0 2px; }}
.fact em {{ display: block; font-style: normal; font-size: 12px; line-height: 1.38; color: #475569; }}
.at.lad {{ font-size: 13.5px; }} .at.lad th {{ font-size: 10.5px; letter-spacing: .06em; vertical-align: bottom; }}
.at.lad td {{ padding: 10px 10px; white-space: nowrap; }} .at.lad td:first-child {{ width: auto; }}
.at.lad tr.main td {{ background: {NAVY_L}; font-weight: 700; }}
.at.tight td {{ padding: 4.5px 10px; line-height: 1.3; }} .at.tight {{ font-size: 12px; }}
.at.four {{ font-size: 11.5px; }} .at.four td {{ padding: 4px 9px; }}
.at.four td:first-child {{ width: 16%; }} .at.four td:nth-child(2) {{ width: 27%; }} .at.four td:last-child {{ width: 19%; color: {NAVY}; font-weight: 600; }}
"""


def build():
    pages = [cover(), p_job(), p_funds(), p_product(), p_flow(), p_reg(), p_team(), p_customers(), p_milestones(), p_company(),
             p_assume(), p_main_inputs()]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Seed plan</title><style>{CSS}{SEED_CSS}</style></head>'
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

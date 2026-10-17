"""Deck v3: the simple, picture-first story on the cohort Monte Carlo (operator, 16 Oct 2026: "story in the deck should start
from the current problems of online model and what our offline approach proposes to solve and what our analysis says…
keep the story simple"; "Too much text. I want more pictures, charts, flowcharts explaining the story").

Brief: story/BRIEF_deck_v3_cohort_2026-10-16.md; story: story/STORYLINE_v3_2026-10-16.md; word budget and style:
story/BRIEF_final_v3_visual_2026-10-16.md section A (story pages <= 70 words including sources, title <= 12 words, one
takeaway line <= 14 words, sources <= 15 words; appendix pages <= 150 words, assumption grids and tables exempt).

Numbers: read at build time from the cohort model's tables (tables/cohort_*; a `_v2` file wins where one exists), the agreed
distributions (dist_agreed_v1.csv, dist_derived_v1.csv), story_unit.csv for the online figures, and the deck_v3_* tables
written by model/deck_v3_numbers.py (re-run here automatically when the Monte Carlo draws are newer than them).
Pictures: build_qr_visual (V) helpers; the online-cost appendix from build_final_deck_v2 (F2.a8); the assumption grids from
dist_proposal (DP.p_grid1..5). Writes Offline_model_v3.pdf (and its HTML in the scratchpad or the system temp folder).
"""
import csv
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build_qr_visual as V
import build_final_deck_v2 as F2
import dist_proposal as DP
import cohort_engine as E
from build_agent_slides import inr

ROOT = Path(__file__).resolve().parent.parent
T, R = ROOT / "tables", ROOT / "research"
PDF = ROOT / "Offline_model_v3.pdf"
if "--scratch" in sys.argv:          # a layout check only: never written over the deck
    PDF = Path("/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad/deck3_scratch.pdf")
S = Path("/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad")
OUT = Path(os.environ.get("DECK3_OUT", S if S.exists() else tempfile.gettempdir()))
SYS_PY = shutil.which("python3") or "/usr/bin/python3"
LIB = S / "lib" if (S / "lib" / "pypdfium2" / "__init__.py").exists() else Path.home() / ".cortado-render-lib"      # the render lib moved (17 Oct)
INK, MUTED, RULE, PAPER, THEM, US, GOOD, WARN, BAD, GREY = V.INK, V.MUTED, V.RULE, V.PAPER, V.THEM, V.US, V.GOOD, V.WARN, V.BAD, V.GREY
APP = F2.APP
COLS = F2.COLS


# ---------- tables (the latest run wins) ----------
def latest(name):
    v2 = T / f"{name}_v2.csv"
    return v2 if v2.exists() else T / f"{name}.csv"


def rows(name):
    return list(csv.DictReader(latest(name).open()))


PREVIEW = "--preview" in sys.argv       # build the non-metric pages before the cumulative P&L run lands; metric pages show a stub


def refresh_numbers():
    """deck_v3_*.csv are derived from the Monte Carlo draws: re-run deck_v3_numbers.py when the draws (or the engine) are newer."""
    draws, fan = latest("cohort_mc_draws"), T / "deck_v3_cum_fan.csv"
    newest = max(draws.stat().st_mtime, latest("cohort_det_monthly").stat().st_mtime, (Path(__file__).parent / "cohort_engine.py").stat().st_mtime)
    if not fan.exists() or fan.stat().st_mtime < newest:
        py = Path.home() / ".cortado-venv311/bin/python"
        r = subprocess.run([str(py if py.exists() else sys.executable), str(Path(__file__).parent / "deck_v3_numbers.py")])
        if r.returncode and not PREVIEW:
            raise SystemExit("deck_v3_numbers.py failed: the cumulative P&L tables are not ready")


refresh_numbers()
USED = set()


def tab(name):
    USED.add(latest(name).name)
    return rows(name)


SUMM = {r["measure"]: r for r in tab("cohort_mc_summary")}
MBT = tab("cohort_mc_must_be_true")
DRV = tab("cohort_mc_drivers")
XSM = tab("cohort_mc_crosssell")
BRIDGE = tab("cohort_bridge")
DETM = tab("cohort_det_monthly")
DETS = {r["measure"]: r for r in tab("cohort_det_summary")}
DETL = tab("cohort_det_lending")
CONTRACT = ("Cumulative P&L at 36 months", "Cumulative P&L at 60 months", "P(cumulative P&L at 36 months > 0)",
            "P(cumulative P&L at 60 months > 0)", "Payback month (cumulative P&L turns positive)", "Peak cash need (lowest cumulative P&L)", "Year-1 P&L")
MISSING = [m for m in CONTRACT if m not in SUMM] + ([] if latest("cohort_mc_cum_fan").exists() else ["tables/cohort_mc_cum_fan.csv"])
READY = not MISSING
if not READY and not PREVIEW:
    raise SystemExit("CUMULATIVE P&L NOT READY. cohort_mc_summary.csv / cohort_mc_cum_fan.csv lack: " + "; ".join(MISSING)
                     + ". The deck never falls back to NPV. Wait for the cohort re-run (or build with --preview).")
FAN = tab("cohort_mc_cum_fan") if READY else []
MUST = {r["key"]: r for r in tab("deck_v3_must")} if READY else {}
DIST = E.load_dists()[0]
if READY:
    if "cost_incentive" not in DETM[0] and "--scratch" not in sys.argv:
        raise SystemExit("cohort_det_monthly.csv has no cost_incentive column: the agent-pay re-run has not landed")
    if not any("ncentive" in k or "agent pay" in k.lower() for k in SUMM):
        raise SystemExit("cohort_mc_summary.csv carries no agent incentive row: the agent-pay re-run has not landed")
HOUSE = tab("deck_v3_housing")[0]
BYY = tab("deck_v3_by_year")
GATES = {r["key"]: r for r in tab("deck_v3_gates")}
HOOK = tab("deck_v3_hook")
AGR = {r["key"]: r for r in csv.DictReader((T / "dist_agreed_v1.csv").open())}
DER = {r["key"]: r for r in csv.DictReader((T / "dist_derived_v1.csv").open())}
SU = {r["channel"]: r for r in csv.DictReader((T / "story_unit.csv").open())}
SURV = list(csv.DictReader((T / "agent3_survival.csv").open()))
IVR = {r["id"]: r for r in csv.DictReader((R / "interview_arvinder_2026-10-15.csv").open())}


def cm(name, col="p50"):
    """A round-5 contract measure, by its exact name: never a prefix match, never NPV."""
    r = SUMM[name]
    return float(r[col] if r.get(col, "") != "" else r["value"])


def pnl_col(rows_, what, pattern):
    """The cumulative P&L column of a cohort table; fails loudly if the table still carries only NPV."""
    cols = list(rows_[0].keys()) if rows_ else []
    c = [k for k in cols if re.search(pattern, k, re.I) and "npv" not in k.lower()]
    if not c:
        raise SystemExit(f"{what}: no cumulative P&L column (has {cols}). The deck never falls back to NPV.")
    return c[0]


def dl(key, i=2):
    return float(DIST[key][i])


def sm(prefix, col="p50"):
    r = next(v for k, v in SUMM.items() if k.startswith(prefix))
    return float(r[col] if r[col] != "" else r["value"])


def dets(prefix):
    return float(next(v for k, v in DETS.items() if k.startswith(prefix))["value"])


def ag(key, col="likely"):
    return float(AGR[key][col])


def lakh(x, d=1, sign=False):
    s = "−" if x < 0 else ("+" if sign else "")
    return f"{s}₹{abs(x) / 1e5:.{d}f} lakh"


def of10(p):
    """'X of 10' futures; a share that rounds to 10 but is not every draw reads 'nearly 10'."""
    if round(p * 10) == 10 and p < 1:
        return "nearly 10"
    if round(p * 10) == 0 and p > 0:
        return "under 1"
    return str(round(p * 10))


def chance(p):
    """A share of futures: never print 100% unless every draw is positive."""
    return ">99%" if 0.995 <= p < 1 else pct(p)


def pct(p, d=0):
    return f"{p * 100:.{d}f}%"


def T_(x, y, s, size=14, weight=400, fill=INK, anchor="start", lh=None):
    return V.text(x, y, s, size, weight, fill, anchor, lh)


def halo(svg_text):
    return svg_text.replace("<text ", '<text stroke="#fff" stroke-width="5" stroke-linejoin="round" paint-order="stroke" ')


# ---------- headline numbers ----------
if READY:
    P60, P36 = cm("P(cumulative P&L at 60 months > 0)"), cm("P(cumulative P&L at 36 months > 0)")
    MED60, MED36 = cm("Cumulative P&L at 60 months"), cm("Cumulative P&L at 36 months")
    PAYBACK, PEAK = cm("Payback month (cumulative P&L turns positive)"), cm("Peak cash need (lowest cumulative P&L)")
    YEAR1 = cm("Year-1 P&L")
    MBT_COL = pnl_col([r for r in MBT if r["table"] == "r12 x sign-ups"], "cohort_mc_must_be_true.csv", r"(cum|pnl).*60.*(above|positive|>)|chance.*(cum|pnl).*60")
    DRV_COL = pnl_col(DRV, "cohort_mc_drivers.csv", r"swing.*(cum|pnl)|(cum|pnl).*swing")
    try:
        BR_COL = pnl_col(BRIDGE, "cohort_bridge.csv", r"^(?!change).*(cum|pnl).*60|^(?!change).*60.*(cum|pnl)")
    except SystemExit:
        # the bridge keeps its old column name; accept it ONLY if its last step IS the cumulative P&L at month 60 (undiscounted)
        cum60 = float(DETM[59]["cum_cash"])
        if not (abs(float(BRIDGE[-1]["npv60"]) - cum60) < 1.0 and abs(float(DETM[59]["cum_npv"]) - cum60) < 1.0):
            raise SystemExit("cohort_bridge.csv: npv60 is not the undiscounted cumulative P&L at month 60. The deck never falls back to NPV.")
        BR_COL = "npv60"
    MINE = {r["measure"]: r for r in tab("deck_v3_cum_summary")}           # the same measures, re-run here from the draws
    for name, tol in ((CONTRACT[1], 0.01), (CONTRACT[5], 0.01)):
        a, b = cm(name), float(MINE[name]["p50"])
        assert abs(a - b) <= tol * abs(b) + 1, f"{name}: cohort table {a:,.0f} vs re-run {b:,.0f}"
    assert abs(P60 - float(MINE[CONTRACT[3]]["value"])) < 0.01 and abs(P36 - float(MINE[CONTRACT[2]]["value"])) < 0.01
else:
    P60 = P36 = MED60 = MED36 = PAYBACK = PEAK = YEAR1 = None
DRAWS = int(sm("Draws", "value"))
N_PROD = len(E.PRODUCTS)
ONL_CAC, ONL_R12, ONL_KEPT = float(SU["online"]["cost_to_win"]), float(SU["online"]["still_saving_m12"]), float(SU["online"]["cost_per_saver_still_saving_m12"])
ONL_BACK = float(SU["online"]["value_36m"])
SAL_PER_SU = dets("Agent's salary per sign-up")
LEAD_PER_SU = dets("Online lead cost, 60 months") / sum(float(r["signups"]) for r in DETM)     # lead cost per sign-up, likely values
assert abs(LEAD_PER_SU - ag("online_lead_share") * ag("lead_cost")) < 0.5, (LEAD_PER_SU, ag("online_lead_share") * ag("lead_cost"))
WIN = SAL_PER_SU + LEAD_PER_SU
FEE_START = f"{ag('fee') * 100:.2f}".rstrip("0").rstrip(".") + "%"                      # round 9: a DSA's rate at the start
FEE_END = f"{ag('fee') * ag('fee_mult_end') * 100:.1f}%"                                 # ... rising in a straight line to month 60
FEE_TEXT = f"a DSA's {FEE_START}, rising to about {FEE_END} by year 5"
PR01 = next(r for r in csv.DictReader((R / "practitioner_2026-10-17.csv").open()) if r["id"] == "PR-01")
PR01_N = next(m.group(1) for v in PR01.values() for m in [re.search(r"onboard (\d+\+?)", str(v))] if m)
FUND_RATE = pct(float(HOOK[2]["rate"]))
VISITS = f"every {math.floor(ag('visit_every'))}–{math.ceil(ag('visit_every'))} days"
HEADLINE = (f"{of10(P60).capitalize()} of 10 futures in profit by month 60; {of10(P36)} by month 36." if READY else "Awaiting the cumulative P&L run.")


def stub(h=420):
    return V.svg(1000, h, f'<rect x="0" y="0" width="1000" height="{h}" rx="20" fill="#eceae5"/>'
                 + T_(500, h / 2, "Awaiting the cumulative P&L run", 26, 800, MUTED, "middle"))
assert abs(ONL_CAC - ag("online_cac")) < 0.01


# ---------- Part 1: online ----------
def p_online_cost():
    lo, mid, hi = ag("online_cac", "low"), ONL_CAC, ag("online_cac", "high")
    s = []
    flow = [("phone", "Ads and installs"), ("doc", "Sign-up")]
    for i, (ic, t) in enumerate(flow):
        x = i * 250
        s.append(f'<rect x="{x}" y="30" width="210" height="150" rx="16" fill="{PAPER}"/>' + V.icon(ic, x + 81, 52, 48, MUTED)
                 + T_(x + 105, 140, t, 19, 700, INK, "middle"))
        s.append(V.arrow(x + 214, 105, x + 246, 105, MUTED, 2.5))
    s.append(f'<rect x="500" y="10" width="500" height="190" rx="18" fill="#fff" stroke="{BAD}" stroke-width="3"/>')
    s.append(V.icon("coin", 530, 52, 92, BAD))
    s.append(T_(650, 118, inr(mid), 76, 800, BAD))
    s.append(T_(652, 160, "to win one saver who starts", 19, 600, INK))
    x0, x1, y = 60, 940, 330
    X = lambda v: x0 + (x1 - x0) * (math.log(v) - math.log(150)) / (math.log(2000) - math.log(150))
    s.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
    s.append(f'<rect x="{X(lo)}" y="{y - 14}" width="{X(hi) - X(lo)}" height="28" rx="14" fill="{V.TINT["bad"]}"/>')
    for v, lab, big in ((lo, "low", False), (mid, "likely", True), (hi, "high", False)):
        s.append(f'<circle cx="{X(v)}" cy="{y}" r="{11 if big else 7}" fill="{BAD}" stroke="#fff" stroke-width="3"/>')
        s.append(T_(X(v), y + 44, inr(v), 20 if big else 16, 800 if big else 600, BAD, "middle"))
        s.append(T_(X(v), y + 66, lab, 14, 400, MUTED, "middle"))
    s.append(T_(x0, y - 40, "THE RANGE, FROM THREE PUBLISHED SIGNALS", 13, 700, MUTED))
    return V.svg(1000, 410, "".join(s))


def p_online_keep():
    n = round(ONL_R12 * 100)
    s = []
    for k in range(100):
        r, c = divmod(k, 10)
        s.append(V.icon("person", c * 40, r * 40, 34, THEM if k < n else "#e3ded4"))
    s.append(T_(0, 436, f"{n} of 100", 30, 800, THEM) + T_(150, 436, "still save after a year", 17, 600, INK))
    app = [1.0] + [float(r["still_saving_evidence"]) for r in SURV][:12]
    x0, x1, y0, y1 = 520, 980, 40, 380
    X = lambda m: x0 + (x1 - x0) * m / 12
    Y = lambda v: y1 - (y1 - y0) * v
    for v in (0, 0.5, 1.0):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}"/>' + T_(x0 - 8, Y(v) + 5, f"{v * 100:.0f}", 13, 400, MUTED, "end"))
    for m in (0, 3, 6, 9, 12):
        s.append(T_(X(m), y1 + 22, str(m), 13, 400, MUTED, "middle"))
    s.append(T_((x0 + x1) / 2, y1 + 44, "months after sign-up", 13, 400, MUTED, "middle"))
    d = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(app))
    s.append(f'<path d="{d} L{X(12)},{Y(0)} L{X(0)},{Y(0)} Z" fill="{THEM}" opacity="0.12"/><path d="{d}" fill="none" stroke="{THEM}" stroke-width="4"/>')
    s.append(f'<circle cx="{X(12)}" cy="{Y(app[12])}" r="8" fill="{THEM}" stroke="#fff" stroke-width="3"/>')
    s.append(halo(T_(X(12) - 12, Y(app[12]) - 16, f"{app[12] * 100:.0f}", 22, 800, THEM, "end")))
    s.append(T_(x0, 20, "STILL SAVING, OF 100 APP SIGN-UPS", 13, 700, MUTED))
    assert abs(app[12] - ONL_R12) < 0.005
    return V.svg(1000, 470, "".join(s))


def p_online_kept():
    s = []
    base, top = 380, 40
    vmax = ONL_KEPT
    for i, (v, lab, sub, col) in enumerate(((ONL_KEPT, "Cost per saver kept", f"{inr(ONL_CAC)} ÷ {ONL_R12 * 100:.0f} of 100", BAD),
                                           (ONL_BACK, "What he earns back", "in 3 years", THEM))):
        x = 120 + i * 330
        h = (base - top) * v / vmax
        s.append(f'<rect x="{x}" y="{base - h}" width="200" height="{h}" rx="8" fill="{col}"/>')
        s.append(T_(x + 100, base - h - 16, inr(v), 40, 800, col, "middle"))
        s.append(T_(x + 100, base + 32, lab, 19, 700, INK, "middle") + T_(x + 100, base + 56, sub, 15, 400, MUTED, "middle"))
    s.append(f'<line x1="80" y1="{base}" x2="680" y2="{base}" stroke="{INK}" stroke-width="1.5"/>')
    s.append(f'<rect x="740" y="120" width="250" height="180" rx="18" fill="{V.TINT["bad"]}"/>')
    s.append(V.icon("broken", 835, 140, 60, BAD))
    s.append(T_(865, 240, "Never", 30, 800, BAD, "middle") + T_(865, 270, "earned back", 17, 600, BAD, "middle"))
    return V.svg(1000, 450, "".join(s))


# ---------- Part 2: our approach ----------
def p_hook():
    j, liq, ours, gain = HOOK
    daily = ag("daily")
    s = []
    x0, x1 = 250, 640
    vmax = float(ours["a_year"])
    X = lambda v: x0 + (x1 - x0) * v / vmax
    items = [("Janta deposit", "a bank savings rate", float(j["a_year"]), GREY),
             ("A liquid fund", "", float(liq["a_year"]), THEM), ("Our debt fund", "", float(ours["a_year"]), US)]
    s.append(T_(0, 18, "WHAT HIS SAVINGS EARN HIM, A YEAR", 13, 700, MUTED))
    for i, (lab, sub, v, col) in enumerate(items):
        y = 50 + i * 120
        s.append(T_(x0 - 18, y + 42 - (9 if sub else 0), lab, 20, 700, INK, "end"))
        if sub:
            s.append(T_(x0 - 18, y + 58, sub, 14, 400, MUTED, "end"))
        s.append(f'<rect x="{x0}" y="{y + 10}" width="{X(v) - x0}" height="56" rx="8" fill="{col}"/>')
        s.append(T_(X(v) - 14, y + 48, inr(v), 22, 800, "#fff", "end"))
    s.append(f'<rect x="690" y="40" width="310" height="330" rx="20" fill="{V.TINT["good"]}"/>')
    s.append(V.icon("jar", 805, 66, 80, GOOD))
    s.append(T_(845, 230, "+" + inr(float(gain["a_year"])), 52, 800, GOOD, "middle"))
    s.append(T_(845, 268, "more a year for him", 19, 700, GOOD, "middle"))
    s.append(T_(845, 296, f"on ₹{daily:.0f} a day", 16, 400, INK, "middle"))
    s.append(f'<rect x="745" y="316" width="200" height="34" rx="17" fill="{GOOD}"/>' + T_(845, 339, "free to the saver", 16, 800, "#fff", "middle"))
    assert abs(float(gain["a_year"]) - float(DER["gain_vs_janta"]["at_likely_values"])) < 1
    return V.svg(1000, 400, "".join(s))


def p_approach():
    s = []
    halves = [(0, "THE FLEET", "person", US, ["Signs him up", f"Collects {VISITS}", "Helps collect loans"]),
              (620, "THE APP", "phone", THEM, [f"~{FUND_RATE} on savings", "UPI"])]
    for x, head, ic, col, lines in halves:
        s.append(f'<rect x="{x}" y="0" width="380" height="270" rx="20" fill="{PAPER}"/><rect x="{x}" y="0" width="380" height="8" rx="4" fill="{col}"/>')
        s.append(V.icon(ic, x + 24, 26, 54, col) + T_(x + 92, 64, head, 24, 800, col))
        for k, ln in enumerate(lines):
            y = 128 + k * 48
            s.append(f'<circle cx="{x + 38}" cy="{y - 6}" r="7" fill="{col}"/>' + T_(x + 58, y, ln, 18, 600, INK))
    s.append(f'<circle cx="500" cy="135" r="86" fill="#fff" stroke="{INK}" stroke-width="2.5"/>' + V.icon("till", 451, 88, 98, INK))
    s.append(V.arrow(382, 135, 410, 135, INK, 3) + V.arrow(618, 135, 590, 135, INK, 3))
    s.append(f'<rect x="0" y="290" width="1000" height="56" rx="16" fill="#f6efe7"/>' + V.icon("phone", 18, 296, 44, US) + V.arrow(62, 318, 84, 318, US, 2.5)
             + V.icon("person", 86, 296, 44, US) + T_(146, 326, "Online leads, served offline: the agent closes and serves every saver", 18, 800, US))
    s.append(f'<rect x="0" y="358" width="1000" height="60" rx="16" fill="{V.TINT["good"]}"/>'
             + f'<circle cx="40" cy="388" r="18" fill="{GOOD}"/>' + T_(40, 395, "✓", 20, 800, "#fff", "middle")
             + T_(74, 395, f"A field-led savings fintech's agents onboard {PR01_N} a month (PR-01)", 18, 700, GOOD))
    return V.svg(1000, 422, "".join(s))


def p_cost_to_win():
    r12 = ag("r12")
    kept, onl_kept = WIN / r12, ONL_KEPT
    vmax = onl_kept
    base, top = 330, 40
    H = lambda v: (base - top) * v / vmax
    s = [T_(60, 18, "TO WIN A SAVER", 13, 700, MUTED), T_(560, 18, "PER SAVER STILL SAVING AFTER A YEAR", 13, 700, MUTED)]
    # to win: ours stacked (his time + online leads) vs online
    x = 60
    h1, h2 = H(SAL_PER_SU), H(LEAD_PER_SU)
    s.append(f'<rect x="{x}" y="{base - h1}" width="150" height="{h1}" fill="{US}"/>' + f'<rect x="{x}" y="{base - h1 - h2}" width="150" height="{h2}" fill="{COLS["cards"]}"/>')
    s.append(T_(x + 160, base - h1 / 2 + 5, f"{inr(SAL_PER_SU)} his time", 14, 800, US) + T_(x + 160, base - h1 - h2 / 2 + 5, f"{inr(LEAD_PER_SU)} online leads", 14, 800, COLS["cards"]))
    s.append(T_(x + 75, base - h1 - h2 - 12, inr(WIN), 26, 800, INK, "middle") + T_(x + 75, base + 24, "us", 15, 700, US, "middle"))
    x2 = 370
    h = H(ONL_CAC)
    s.append(f'<rect x="{x2}" y="{base - h}" width="150" height="{h}" fill="{APP}"/>' + T_(x2 + 75, base - h - 12, inr(ONL_CAC), 26, 800, APP, "middle")
             + T_(x2 + 75, base + 24, "online", 15, 700, APP, "middle"))
    # per saver kept
    for i, (v, lab, col, sub) in enumerate(((kept, "us", US, f"÷ {pct(r12)}"), (onl_kept, "online", APP, f"÷ {pct(ONL_R12)}"))):
        xx = 600 + i * 210
        h = H(v)
        s.append(f'<rect x="{xx}" y="{base - h}" width="150" height="{h}" fill="{col}"/>' + T_(xx + 75, base - h - 12, inr(v), 26, 800, col, "middle")
                 + T_(xx + 75, base + 24, lab, 15, 700, col, "middle") + T_(xx + 75, base + 44, sub, 13, 400, MUTED, "middle"))
    s.append(f'<line x1="40" y1="{base}" x2="510" y2="{base}" stroke="{INK}"/><line x1="580" y1="{base}" x2="990" y2="{base}" stroke="{INK}"/>')
    s.append(f'<rect x="0" y="390" width="1000" height="48" rx="14" fill="#f6efe7"/>' + V.icon("person", 14, 394, 40, US)
             + T_(64, 421, (f"Pay: {inr(dl('salary'))} + {pp(PAY_RATE)} of balance, capped at {inr(PAY_CAP)} a month" if PAY_CAP else
                            f"Pay: {inr(dl('salary'))} a month + {pp(PAY_RATE)} of his savers' balance"), 16, 700, US))
    return V.svg(1000, 442, "".join(s))


def p_cash_route():
    s = []
    nodes = [("person", INK, "He hands cash", "to our agent"), ("bank", US, "Deposited the same day", "in the fund's account"),
             ("doc", US, "Reconciliation", "sent to the fund"), ("phone", GOOD, "Next day: a message", "with his units")]
    w, gap = 220, 40
    for i, (ic, col, t, sub) in enumerate(nodes):
        x = i * (w + gap)
        s.append(f'<rect x="{x}" y="40" width="{w}" height="230" rx="18" fill="{PAPER}"/>' + V.icon(ic, x + w / 2 - 34, 66, 68, col)
                 + T_(x + w / 2, 186, t, 18, 800, INK, "middle") + T_(x + w / 2, 212, sub, 15, 400, MUTED, "middle"))
        s.append(f'<circle cx="{x + 26}" cy="66" r="15" fill="{col}"/>' + T_(x + 26, 71.5, str(i + 1), 14, 800, "#fff", "middle"))
        if i < len(nodes) - 1:
            s.append(V.arrow(x + w + 4, 155, x + w + gap - 4, 155, US, 3))
    s.append(f'<path d="M{w + gap},290 v14 h{2 * w + gap} v-14" fill="none" stroke="{WARN}" stroke-width="2.5"/>')
    s.append(V.badge(w + gap + w + gap / 2, 346, "warn", "legal opinion needed", 17))
    return V.svg(1000, 372, "".join(s))


GROUP_ICON = {"loans": ("coin", "Loans"), "cards": ("doc", "Cards"), "insurance": ("hands", "Insurance"),
              "investments": ("jar", "Investments"), "payments": ("phone", "Payments"), "other_loans": ("bank", "Other lenders")}


def p_marketplace():
    group = {p: g for p, g, *_ in DP.PRODUCTS}
    groups = {}
    for p, *_ in E.PRODUCTS:
        g = group.get(p, "other_loans" if p.startswith("loan_") else None)
        assert g, f"no group for product {p}"
        groups[g] = groups.get(g, 0) + 1
    assert "loan_home" in group or any(p == "loan_home" for p, *_ in E.PRODUCTS), "home loans missing from the engine"
    mfrom = int(dl("marketplace_from"))
    s = [f'<rect x="0" y="40" width="250" height="330" rx="20" fill="{PAPER}"/>', V.icon("till", 70, 70, 110, INK),
         T_(125, 230, "His shop", 22, 800, INK, "middle"), T_(125, 262, f"from month {mfrom}", 18, 700, US, "middle")]
    s.append(V.arrow(258, 205, 318, 205, US, 4))
    tiles = [("loans", [f"a DSA's {FEE_START},", f"rising to about {FEE_END} by year 5"]), ("cards", ["credit"])] + [
        (g, [f"{groups[g]} products"]) for g in ("insurance", "investments", "payments")]
    tiles.append(("other_loans", [f"home loans to {lakh(float(HOUSE['ticket_high']), 0)}", "loans against property"]))
    for k, (g, subs) in enumerate(tiles):
        r, c = divmod(k, 3)
        x, y = 330 + c * 225, 40 + r * 170
        ic, name = GROUP_ICON[g]
        big = len(subs) > 1
        s.append(f'<rect x="{x}" y="{y}" width="205" height="155" rx="16" fill="#fff" stroke="{US if big else RULE}" stroke-width="{2.5 if big else 2}"/>')
        s.append(V.icon(ic, x + (82 if big else 78), y + (10 if big else 16), 40 if big else 48, US) + T_(x + 102, y + (72 if big else 98), name, 19, 800, INK, "middle"))
        for j, sub in enumerate(subs):
            s.append(T_(x + 102, y + (124 if not big else 96 + j * 19), sub, 15 if not big else 13.5, 400 if j == 0 else 700, MUTED if j == 0 else US, "middle"))
    s.append(f'<rect x="330" y="384" width="655" height="44" rx="22" fill="{V.TINT["good"]}"/>')
    s.append(T_(657, 413, f"₹0 to us · {N_PROD} products", 18, 800, GOOD, "middle"))
    return V.svg(1000, 432, "".join(s))


def p_collect():
    early, p90 = ag("early_cured"), float(DER["share_90plus"]["at_likely_values"])
    fee_loan = float(DER["collections_per_loan"]["at_likely_values"])
    worst = ag("loss", "high")
    s = []
    s.append(f'<rect x="0" y="120" width="190" height="130" rx="16" fill="{PAPER}"/>' + V.icon("doc", 71, 136, 48, INK) + T_(95, 216, "100 loans", 20, 800, INK, "middle"))
    s.append(V.arrow(194, 185, 262, 185, MUTED, 2.5))
    s.append(f'<rect x="266" y="120" width="210" height="130" rx="16" fill="#fff" stroke="{WARN}" stroke-width="2.5"/>' + V.icon("broken", 347, 134, 48, WARN)
             + T_(371, 212, "fall behind", 19, 700, WARN, "middle"))
    s.append(V.arrow(480, 160, 560, 70, GOOD, 3) + V.arrow(480, 210, 560, 300, BAD, 3))
    s.append(f'<rect x="566" y="10" width="300" height="120" rx="16" fill="{V.TINT["good"]}"/>' + V.icon("person", 584, 36, 64, GOOD)
             + T_(664, 70, f"{early * 100:.0f}", 40, 800, GOOD) + T_(664, 104, "brought back early", 16, 700, GOOD))
    s.append(f'<rect x="566" y="240" width="300" height="120" rx="16" fill="{V.TINT["bad"]}"/>' + V.icon("bank", 584, 268, 60, BAD)
             + T_(664, 300, f"{p90 * 100:.0f}", 40, 800, BAD) + T_(664, 334, "go 90+ days bad", 16, 700, BAD))
    s.append(V.arrow(870, 70, 905, 160, GOOD, 2.5) + V.arrow(870, 300, 905, 210, BAD, 2.5))
    s.append(f'<rect x="900" y="140" width="100" height="90" rx="14" fill="{US}"/>' + T_(950, 182, inr(fee_loan), 22, 800, "#fff", "middle")
             + T_(950, 206, "a loan", 14, 600, "#fff", "middle"))
    s.append(f'<rect x="0" y="390" width="1000" height="50" rx="14" fill="{V.TINT["warn"]}"/>')
    s.append(T_(500, 422, f"Worst case: losses of {worst * 100:.0f}%, Paytm's level", 18, 800, WARN, "middle"))
    return V.svg(1000, 444, "".join(s))


# ---------- Part 3: what our analysis says ----------
def p_cohorts():
    s = []
    n, c = 12, 26
    x0, y0 = 40, 40
    for i in range(n):
        for j in range(n - i):
            op = 0.9 - 0.6 * j / n
            s.append(f'<rect x="{x0 + (i + j) * c}" y="{y0 + i * c}" width="{c - 3}" height="{c - 3}" rx="3" fill="{US}" opacity="{op:.2f}"/>')
    s.append(T_(x0, y0 - 14, "EVERY MONTH, A NEW COHORT", 13, 700, MUTED))
    s.append(T_(x0 - 10, y0 + 16, "1", 13, 700, MUTED, "end") + T_(x0 - 10, y0 + (n - 1) * c + 16, "60", 13, 700, MUTED, "end"))
    s.append(T_(x0 + n * c / 2, y0 + n * c + 28, "60 months of saving, loans and products", 15, 600, INK, "middle"))
    s.append(V.arrow(380, 190, 470, 190, US, 4))
    fx0, fx1, fy = 500, 980, 190
    import random
    rnd = random.Random(7)
    for k in range(60):
        end = fy - 150 + rnd.random() * 280
        mid = fy + 40 + rnd.random() * 30
        s.append(f'<path d="M{fx0},{fy + 40} Q{(fx0 + fx1) / 2},{mid + 40} {fx1},{end}" fill="none" stroke="{THEM}" stroke-width="1.4" opacity="0.28"/>')
    s.append(f'<rect x="{fx0}" y="{fy - 175}" width="250" height="60" rx="14" fill="#fff" stroke="{THEM}" stroke-width="2"/>')
    s.append(T_(fx0 + 125, fy - 135, f"{DRAWS:,} futures", 26, 800, THEM, "middle"))
    s.append(f'<rect x="0" y="390" width="1000" height="46" rx="14" fill="{PAPER}"/>' + T_(500, 420, "Every input is a distribution (A1–A3)", 18, 700, INK, "middle"))
    return V.svg(1000, 440, "".join(s))


def p_fan():
    if not READY:
        return stub()
    m = [int(r["month"]) for r in FAN]
    q = {k: [float(r[k]) for r in FAN] for k in ("p10", "p25", "p50", "p75", "p90")}
    x0, x1, y0, y1 = 70, 640, 34, 400
    vmin, vmax = min(min(q["p10"]), 0.0), max(q["p90"])
    span = vmax - vmin
    step = next(st for st in (100000, 200000, 400000, 500000, 1000000, 2000000, 5000000) if span / st <= 7)
    lo_t, hi_t = math.floor(vmin / step) * step, math.ceil(vmax / step) * step
    X = lambda t: x0 + (x1 - x0) * t / 60
    Y = lambda v: y1 - (y1 - y0) * (v - lo_t) / (hi_t - lo_t)
    s = []
    for v in range(int(lo_t), int(hi_t) + 1, step):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}" stroke-width="{1.5 if v == 0 else 1}"/>')
        s.append(T_(x0 - 8, Y(v) + 4, f"{v / 1e5:g}", 12, 400, MUTED, "end"))
    s.append(T_(x0 - 30, y0 - 16, "₹ lakh", 12, 700, MUTED, "start"))
    for t in (12, 24, 36, 48, 60):
        s.append(T_(X(t), y1 + 20, str(t), 12, 400, MUTED, "middle"))
    s.append(T_(x1, y1 + 38, "month", 12, 400, MUTED, "end"))
    band = lambda a, b: "M" + " L".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in zip([0] + m, [0] + q[a])) + " L" + " L".join(
        f"{X(t):.1f},{Y(v):.1f}" for t, v in reversed(list(zip([0] + m, [0] + q[b])))) + " Z"
    s.append(f'<path d="{band("p10", "p90")}" fill="{US}" opacity="0.16"/><path d="{band("p25", "p75")}" fill="{US}" opacity="0.28"/>')
    s.append(f'<path d="M{X(0)},{Y(0)} ' + " ".join(f"L{X(t):.1f},{Y(v):.1f}" for t, v in zip(m, q["p50"])) + f'" fill="none" stroke="{US}" stroke-width="3.5"/>')
    for t in (36, 60):
        s.append(f'<line x1="{X(t)}" y1="{y0}" x2="{X(t)}" y2="{y1}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    low = min(range(len(m)), key=lambda i: q["p50"][i])
    s.append(f'<circle cx="{X(m[low])}" cy="{Y(q["p50"][low])}" r="6" fill="#fff" stroke="{BAD}" stroke-width="3"/>')
    s.append(halo(T_(X(60) - 8, Y(q["p50"][-1]) - 10, lakh(q["p50"][-1]), 15, 800, US, "end")))
    tiles = [(f"{of10(P60)} of 10", "by month 60", GOOD), (f"{of10(P36)} of 10", "by month 36", WARN),
             (f"month {PAYBACK:.0f}", "payback", INK), (lakh(-PEAK), "peak cash need", BAD)]
    for i, (big, sub, col) in enumerate(tiles):
        y = 4 + i * 108
        s.append(f'<rect x="700" y="{y}" width="300" height="96" rx="16" fill="{PAPER}"/>' + T_(722, y + 50, big, 36, 800, col) + T_(722, y + 78, sub, 15, 600, MUTED))
    return V.svg(1000, 440, "".join(s))


def p_money():
    mo = [int(r["month"]) for r in DETM]
    f = lambda k: [float(r[k]) for r in DETM]
    lines = [("fund", "Fund", f("rev_fund")), ("origination", "Loan fees", f("rev_origination")),
             ("other", "Insurance and more", f("rev_crosssell")), ("cards", "Cards", f("rev_cards")),
             ("collections", "Collections", [a + b for a, b in zip(f("rev_dpd31_90"), f("rev_recovery90"))])]
    cost = f("cost_total")
    tot = [sum(v[i] for _, _, v in lines) for i in range(len(mo))]
    assert all(abs(t - i) < 1 for t, i in zip(tot, f("income")))
    x0, x1, y0, y1 = 70, 760, 20, 400
    vmax = max(max(tot), max(cost)) * 1.05
    step = 20000 if vmax > 60000 else 10000
    X = lambda t: x0 + (x1 - x0) * (t - 1) / 59
    Y = lambda v: y1 - (y1 - y0) * v / vmax
    s = []
    for v in range(0, int(vmax) + 1, step):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}"/>' + T_(x0 - 8, Y(v) + 4, f"{v / 1000:.0f}", 12, 400, MUTED, "end"))
    s.append(T_(x0 - 8, y0 - 4, "₹ thousand a month", 12, 700, MUTED, "start"))
    for t in (12, 24, 36, 48, 60):
        s.append(T_(X(t), y1 + 20, str(t), 12, 400, MUTED, "middle"))
    s.append(T_(x1, y1 + 38, "month", 12, 400, MUTED, "end"))
    cum = [0.0] * len(mo)
    ends = []
    for k, lab, v in lines:
        top_ = [c + a for c, a in zip(cum, v)]
        d = "M" + " L".join(f"{X(t):.1f},{Y(a):.1f}" for t, a in zip(mo, top_)) + " L" + " L".join(f"{X(t):.1f},{Y(a):.1f}" for t, a in reversed(list(zip(mo, cum)))) + " Z"
        s.append(f'<path d="{d}" fill="{COLS[k]}" opacity="0.9"/>')
        ends.append((lab, k, (cum[-1] + top_[-1]) / 2))
        cum = top_
    s.append(f'<path d="M' + " L".join(f"{X(t):.1f},{Y(c):.1f}" for t, c in zip(mo, cost)) + f'" fill="none" stroke="{BAD}" stroke-width="3.5" stroke-dasharray="8 4"/>')
    s.append(halo(T_(X(14), Y(cost[13]) - 12, "his cost", 15, 800, BAD)))
    for i, (lab, k, _v) in enumerate(reversed(ends)):
        y = Y(tot[-1]) + 10 + i * 26
        s.append(f'<rect x="{x1 + 12}" y="{y - 11}" width="12" height="12" rx="2" fill="{COLS[k]}"/>' + T_(x1 + 30, y, lab, 14, 700, INK))
    return V.svg(1000, 440, "".join(s))


def p_by_year():
    yrs = [int(r["year"]) for r in BYY]
    panels = [("approval_first", "Lender approval", pct, US), ("apply_a_year", "Savers who apply", pct, US),
              ("next_loan_after_years_repaid", "His next loan", lambda v: lakh(v, 2), US), ("topups", "Top-ups", lambda v: f"{v:.0f}", US),
              ("signups_a_month", "Sign-ups a month", lambda v: f"{v:.0f}", THEM), ("money_lent", "Money lent", lambda v: lakh(v, 0) if v < 1e7 else f"₹{v / 1e7:.1f} crore", THEM)]
    s = []
    W, H = 310, 200
    for k, (key, name, fmt, col) in enumerate(panels):
        r, c = divmod(k, 3)
        x, y = c * (W + 35), r * (H + 30)
        vals = [float(row[key]) for row in BYY]
        vmax = max(vals)
        s.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="14" fill="{PAPER}"/>' + T_(x + 16, y + 30, name, 17, 800, INK))
        bw, gap, base, top = 38, 16, y + H - 22, y + 70
        for i, v in enumerate(vals):
            bx = x + 30 + i * (bw + gap)
            h = max(3, (base - top) * v / vmax) if vmax > 0 else 3
            s.append(f'<rect x="{bx}" y="{base - h}" width="{bw}" height="{h}" rx="4" fill="{col}" opacity="{0.45 + 0.13 * i:.2f}"/>')
            if i in (0, len(vals) - 1):
                s.append(halo(T_(bx + bw / 2, base - h - 8, fmt(v), 13.5, 800, col, "middle")))
    s.append(T_(0, 2 * (H + 30) + 8, f"bars: years {yrs[0]} to {yrs[-1]}", 13, 600, MUTED))
    return V.svg(1000, 2 * (H + 30) + 14, "".join(s))


MUST_TAKE = ("Each bad end alone still leaves most futures positive." if READY and all(
    float(MUST[k]["chance_cum_pnl60_above_zero"]) >= 0.5 for k in ("signups_run", "ticket", "support_cost")) else "At its bad end, any one can sink an agent.")


def p_must():
    if not READY:
        return stub()
    cells = [r for r in MBT if r["table"] == "r12 x sign-ups"]
    rb = [b for b in dict.fromkeys(r["band"] for r in cells)]
    rb = [b for b in rb if any(r["band"] == b and r["few_draws"] != "yes" for r in cells)]
    sb = list(dict.fromkeys(r["second_band"] for r in cells))
    C = {(r["band"], r["second_band"]): r for r in cells}
    likely_r = next(b for b in rb if float(b.split("-")[0]) <= ag("r12") * 100 < float(b.split("-")[1].rstrip("%")))
    likely_s = next(b for b in sb if float(b.split("-")[0]) <= ag("signups_run") < float(b.split("-")[1]))
    x0, y0, cw, ch = 70, 20, 105, 44
    s = []
    for i, b in enumerate(reversed(rb)):
        for j, sbn in enumerate(sb):
            r = C[(b, sbn)]
            p = float(r[MBT_COL]) if r[MBT_COL] else None
            col = "#eceae5" if p is None else (V.TINT["bad"] if p < 0.5 else (V.TINT["warn"] if p < 0.8 else ("#e3f0e7" if p < 0.95 else "#bcdcc7")))
            fill2 = BAD if p is not None and p < 0.5 else (WARN if p is not None and p < 0.8 else GOOD)
            x, y = x0 + j * cw, y0 + i * ch
            s.append(f'<rect x="{x}" y="{y}" width="{cw - 4}" height="{ch - 4}" rx="6" fill="{col}"' + (' opacity="0.45"' if r["few_draws"] == "yes" else "") + "/>")
            if (b, sbn) == (likely_r, likely_s):
                s.append(f'<rect x="{x - 3}" y="{y - 3}" width="{cw + 2}" height="{ch + 2}" rx="8" fill="none" stroke="{INK}" stroke-width="3"/>')
                s.append(T_(x + cw / 2 - 2, y + ch / 2 + 4, f"likely {chance(p)}", 13, 800, fill2, "middle"))
    for i, b in enumerate(reversed(rb)):
        lo = b.split("-")[0]
        if int(lo) % 10 == 0:
            s.append(T_(x0 - 8, y0 + i * ch + ch / 2 + 2, f"{lo}%", 12, 600, MUTED, "end"))
    for j, sbn in enumerate(sb):
        s.append(T_(x0 + j * cw + cw / 2 - 2, y0 + len(rb) * ch + 14, sbn.replace("-", "–"), 12, 600, MUTED, "middle"))
    yb = y0 + len(rb) * ch + 36
    s.append(T_(x0, yb, "still saving at month 12 × sign-ups", 12, 600, MUTED))
    for k, (lab, c) in enumerate((("below 50%", V.TINT["bad"]), ("50–80%", V.TINT["warn"]), ("80–95%", "#e3f0e7"), ("95%+", "#bcdcc7"))):
        s.append(f'<rect x="{x0 + k * 105}" y="{yb + 14}" width="14" height="14" rx="3" fill="{c}"/>' + T_(x0 + k * 105 + 20, yb + 26, lab, 12, 600, INK))
    janta = re.search(r"(\d+) to (\d+)", IVR["IV-12"]["answer"])
    tiles = [("person", f"~{ag('signups_run'):.0f} sign-ups a month", f"field-led fintech: {PR01_N} (PR-01); janta agent: {janta.group(1)}–{janta.group(2)}",
              "worst tenth", MUST["signups_run"]),
             ("bank", f"{lakh(ag('ticket'))} loans", "", "worst tenth", MUST["ticket"]),
             ("coin", f"₹{ag('support_cost'):.0f} running cost", "", "worst tenth", MUST["support_cost"])]
    s.append(T_(1000, 14, "WORST TENTH", 12, 700, MUTED, "end"))
    for k, (ic, t, sub, bad, r) in enumerate(tiles):
        y = 24 + k * 136
        p = float(r["chance_cum_pnl60_above_zero"])
        s.append(f'<rect x="560" y="{y}" width="440" height="122" rx="16" fill="{PAPER}"/>' + V.icon(ic, 578, y + 18, 44, US) + T_(636, y + 46, t, 19, 800, INK))
        if sub:
            s.append(T_(636, y + 70, sub, 13.5, 400, MUTED))
        s.append(T_(986, y + 106, chance(p), 34, 800, GOOD if p >= 0.9 else (WARN if p >= 0.8 else BAD), "end"))
    return V.svg(1000, max(yb + 34, 430), "".join(s))


SHORT = {"ticket": "Loan size", "apply": "Savers who apply", "r12": "Still saving, month 12", "signups_run": "Sign-ups a month",
         "eligible": "Applicants eligible", "support_cost": "Running cost", "approved_first": "Lender approval", "fee": "Origination fee",
         "trail": "Fund commission", "takeup_growth": "Take-up growth", "daily": "Daily amount", "approval_growth": "Approval growth",
         "rollover": "Kept at term end", "loan_home_takeup": "Home-loan take-up", "loan_lap_takeup": "Property-loan take-up",
         "loan_home_comm": "Home-loan fee", "ins_partner_share": "Insurance share kept", "cash_cover": "Cash cover", "early_takeup_mult": "Early take-up", "loss": "Loan losses", "days": "Deposit days", "kyc_cost": "KYC cost"}


TSHORT = {"ticket": "loan size", "apply": "take-up", "r12": "retention", "signups_run": "sign-ups", "eligible": "eligibility",
          "support_cost": "running cost", "approved_first": "approval", "fee": "the fee", "trail": "the fund commission"}
TOP3 = [TSHORT.get(r["key"], r["key"]) for r in sorted(DRV, key=lambda r: -abs(float(r[DRV_COL])))[:3]] if READY else ["…"] * 3


def p_drivers(n=8):
    if not READY:
        return stub()
    d = sorted(DRV, key=lambda r: -abs(float(r[DRV_COL])))[:n]
    vmax = max(abs(float(r[DRV_COL])) for r in d)
    x0, x1 = 330, 900
    X = lambda v: x0 + (x1 - x0) * abs(v) / vmax
    s = [T_(x1, 12, "₹ lakh, best tenth vs worst tenth", 12, 600, MUTED, "end")]
    for i, r in enumerate(d):
        y = 30 + i * 50
        v = float(r[DRV_COL])
        col = GOOD if v > 0 else BAD
        s.append(T_(x0 - 16, y + 25, SHORT.get(r["key"], re.sub(r"\s*\(.*", "", r["input"]).split(":")[0][:28]), 18, 700, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y + 6}" width="{X(v) - x0}" height="28" rx="5" fill="{col}" opacity="{1 - 0.06 * i:.2f}"/>')
        s.append(T_(X(v) + 10, y + 27, f"{abs(v) / 1e5:.1f}", 16, 800, col))
    return V.svg(1000, 30 + n * 50 + 6, "".join(s))


def p_pilot():
    if not READY:
        return stub()
    g = GATES
    st = lambda key, fmt: "never" if g[key]["stop"] in ("", None) else fmt(float(g[key]["stop"]))
    items = [(3, "person", "Sign-ups a month", f"{float(g['signups_run']['go']):.0f}", st("signups_run", lambda v: f"{v:.0f}")),
             (6, "coin", "Loans per 100 savers", f"{float(g['loans_per_100_offered_year']['go']):.1f}", st("loans_per_100_offered_year", lambda v: f"{v:.1f}")),
             (12, "bank", "Loan size", lakh(float(g["ticket"]["go"])), st("ticket", lambda v: inr(round(v, -3)))),
             (12, "doc", "Running cost", f"₹{float(g['support_cost']['go']):.0f}", st("support_cost", lambda v: f"₹{v:.0f}")),
             (12, "hands", "Still saving", pct(float(g["r12"]["go"])), st("r12", pct))]
    s = []
    bw, gap = 186, 17
    xs = [i * (bw + gap) for i in range(len(items))]
    s.append(f'<line x1="{bw / 2}" y1="40" x2="{xs[-1] + bw / 2}" y2="40" stroke="{US}" stroke-width="4"/>')
    for mo in dict.fromkeys(it[0] for it in items):
        idx = [i for i, it in enumerate(items) if it[0] == mo]
        a, b = xs[idx[0]] + bw / 2, xs[idx[-1]] + bw / 2
        if b > a:
            s.append(f'<line x1="{a}" y1="24" x2="{b}" y2="24" stroke="{US}" stroke-width="2"/>')
        s.append(halo(T_((a + b) / 2, 18, f"month {mo}", 15, 800, US, "middle")))
    for i, (mo, ic, what, go, stop) in enumerate(items):
        x, cx = xs[i], xs[i] + bw / 2
        s.append(f'<circle cx="{cx}" cy="40" r="12" fill="{US}"/>')
        s.append(f'<rect x="{x}" y="66" width="{bw}" height="250" rx="16" fill="{PAPER}"/>' + V.icon(ic, x + bw / 2 - 22, 80, 44, US))
        s.append(T_(x + bw / 2, 150, what, 15, 800, INK, "middle"))
        s.append(f'<rect x="{x + 14}" y="172" width="{bw - 28}" height="56" rx="12" fill="{V.TINT["good"]}"/>' + T_(x + 32, 209, "✓", 22, 800, GOOD)
                 + T_(x + bw - 26, 210, go, 22, 800, GOOD, "end"))
        s.append(f'<rect x="{x + 14}" y="242" width="{bw - 28}" height="56" rx="12" fill="{V.TINT["bad"]}"/>' + T_(x + 32, 279, "✕", 22, 800, BAD)
                 + T_(x + bw - 26, 280, stop, 22, 800, BAD, "end"))
    s.append(f'<rect x="0" y="336" width="1000" height="92" rx="16" fill="#f6efe7"/>' + V.icon("coin", 22, 352, 60, US))
    s.append(T_(100, 380, "YEAR-1 P&L", 13, 700, US) + T_(100, 414, lakh(YEAR1), 30, 800, BAD if YEAR1 < 0 else GOOD))
    s.append(T_(760, 396, "✓", 22, 800, GOOD) + T_(788, 396, "go", 18, 700, GOOD) + T_(860, 396, "✕", 22, 800, BAD) + T_(888, 396, "stop", 18, 700, BAD))
    return V.svg(1000, 432, "".join(s))


# ---------- appendix ----------
def a_grid1():
    """dist_proposal's grid 1 without the discount rate: the deck shows cumulative P&L, undiscounted (round 5)."""
    return DP.grid([[("SAVER", ["daily", "days", "amount_growth", "r3", "r12", "churn_late"])],
                    [("AGENT", ["signups_run", "signup_growth", "ramp_months", "capacity", "upi_12", "kyc_cost"])],
                    [("FUND", ["trail", "trail_liquid", "fund_return", "rollover", "withdraw_m"]), ("COSTS", ["support_cost"])]],
                   [d for d in DP.OP_DECISIONS if d.key != "discount"])


def plain_src(key):
    ev = AGR[key]["evidence_points"].split(";")[0]
    ev = re.sub(r"\s*\([^)]*\)", "", ev).strip()
    return (ev[:62] + "…") if len(ev) > 63 else ev


def a_sources(part):
    items = DP.CORE + [d for d in DP.OP_DECISIONS if d.key != "discount"]
    new = [k for k in E.KEYS if k not in DP.I and not any(k.startswith(p + "_") for p, *_ in DP.PRODUCTS)]
    half = (len(items) + len(new) + 1) // 2
    items = items[:half] if part == 1 else items[half:]
    trs = []
    for i in items:
        val = i.shown if i.shape == "fixed" else i.v(i.likely)
        rng = "" if i.shape == "fixed" else i.rng_text()
        src = plain_src(i.key) if i.key in AGR and AGR[i.key]["evidence_points"] else i.src.split(";")[0]
        src = {"COHORT_INPUTS": "the agreed cohort inputs", "tables/inputs.csv": "your inputs sheet"}.get(src.strip(), src)
        if i.key == "fee":
            src = f"{FEE_TEXT} (operator, 17 Oct)"
        ids = ", ".join(DP.ID_RE.findall(i.src)) or ("operator" if "operator" in i.src else "judgement")
        trs.append(f'<tr><td><b>{html.escape(i.short)}</b></td><td class="n"><b>{html.escape(val)}</b> <span class="lh">{html.escape(rng)}</span></td>'
                   f'<td>{html.escape(src)}</td><td class="c"><svg width="12" height="12" viewBox="0 0 14 14">{DP.dot(7, 7, i.conf, 5.5)}</svg></td><td class="id">{html.escape(ids)}</td></tr>')
    if part == 2:
        for k in new:
            sh, lo, li, hi, src = DIST[k][:5]
            f = (lambda v: pct(v, 1).replace(".0%", "%")) if hi <= 1 else (lambda v: lakh(v, 0) if v >= 1e5 else inr(v))
            name = E.NAMES.get(k, k)
            trs.append(f'<tr><td><b>{html.escape(name[:34])}</b></td><td class="n"><b>{f(li)}</b> <span class="lh">{f(lo)}–{f(hi)}</span></td>'
                       f'<td>round 5–6 change notes, 16 Oct (operator taps)</td><td class="c"><svg width="12" height="12" viewBox="0 0 14 14">'
                       f'{DP.dot(7, 7, DP.OURS, 5.5)}</svg></td><td class="id">judgement</td></tr>')
    lg, _ = DP.legend(0, 12, 10.5)
    return (f'<div class="srct"><table><tr><th>Input</th><th class="n">Likely (low–high)</th><th>Where it comes from</th><th></th><th>ID</th></tr>{"".join(trs)}</table>'
            f'<div class="lg">{V.svg(560, 18, lg)}</div></div>')


def a_bridge():
    b = BRIDGE
    short = {"4": "Fund return 7% a year", "7": "UPI and extra cash collection", "10": "17 products replace ₹63 a year",
             "14": "Take-up and approvals grow", "15": "Loan size grows with repayment", "17": "Collections by overdue bucket",
             "18": "Running cost ₹5 a saver a month", "19": "Loan size ₹25,000–5 lakh"}

    by_text = {"Fund return": "4", "UPI share": "7", "Seventeen cross-sell": "10", "Take-up and approvals grow": "14", "Loan size grows": "15",
               "Collections by overdue": "17", "Running cost": "18", "Ticket range": "19"}
    short["10"] = "Products replace ₹63 a year"
    for prefix, lab_ in (("Sign-ups 100 a month", "Sign-ups 100 falling to 70"), ("Online leads", "Online leads, half at ₹250"),
                         ("Home-loan take-up", "Home-loan take-up 1.5%"), ("Fee starts", "Fee: DSA rate, rising")):
        by_text[prefix] = "t:" + prefix
        short["t:" + prefix] = lab_

    def lab(w, step=None):
        hit = next((k for k in by_text if w.startswith(k)), None)
        if hit:
            return short[by_text[hit]]
        w = re.split(r"[,(:]", w.replace("Rs ", "₹"))[0].strip().replace("v2 legacy setting", "Last deck")
        out = ""
        for t in w.split():
            if len(out) + len(t) + 1 > 28:
                break
            out = (out + " " + t).strip()
        return out
    if not READY:
        return stub(380)
    b = [r for i, r in enumerate(b) if i == 0 or abs(float(r[BR_COL]) - float(b[i - 1][BR_COL])) >= 1.0]   # a step that changes nothing is not drawn
    vals = [float(r[BR_COL]) for r in b]
    lo, hi = min(0.0, min(vals)), max(vals) * 1.05
    x0, x1 = 300, 860
    X = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    gap = 19.5
    n = len(b) + 1
    gap = min(gap, 470 / n)
    s = [f'<line x1="{X(0)}" y1="0" x2="{X(0)}" y2="{n * gap + 6}" stroke="{INK}" stroke-width="1.2"/>']
    assert abs(vals[-1] - float(DETM[59]["cum_cash"])) < 1.0, "the bridge does not end at this deck's cumulative P&L"
    for i in range(n):
        y = 4 + i * gap
        total = i in (0, n - 1)
        v = vals[i] if i < len(b) else vals[-1]
        prev = 0.0 if total else vals[i - 1]
        a0, a1 = sorted((prev, v))
        col = US if total else (GOOD if v >= prev else BAD)
        s.append(f'<rect x="{X(a0)}" y="{y}" width="{max(X(a1) - X(a0), 2)}" height="{gap - 5}" rx="3" fill="{col}"/>')
        s.append(T_(x0 - 10, y + 12, lab(b[i]["what"], b[i]["step"]) if i < len(b) else "This deck, likely values", 11, 700 if total else 500, INK, "end"))
        txt = lakh(v) if total else (f"{'+' if v >= prev else '−'}{abs(v - prev) / 1e5:.1f}" if abs(v - prev) >= 5000 else "")   # a step under ₹0.05 lakh: bar only
        s.append(T_(max(X(a1), X(0)) + 6, y + 12, txt, 10.5, 800, col))
    return V.svg(1000, n * gap + 10, "".join(s))


def a_loans():
    ap, el, apr = ag("apply"), ag("eligible"), ag("approved_first")
    l50, l10, l90 = sm("Loans per 100 savers offered"), sm("Loans per 100 savers offered", "p10"), sm("Loans per 100 savers offered", "p90")
    s = [T_(0, 16, "PER 100 SAVERS OFFERED THE MARKETPLACE, A YEAR (LIKELY)", 12.5, 700, US)]
    st = [("100 savers", "", 380), (f"{ap * 100:.0f} apply", "", 310), (f"{ap * el * 100:.1f} eligible", f"{el * 100:.0f}% of them", 250),
          (f"{ap * el * apr * 100:.1f} approved", f"{apr * 100:.0f}% of them", 200)]
    for i, (t, sub, w) in enumerate(st):
        y = 34 + i * 62
        s.append(f'<rect x="{200 - w / 2}" y="{y}" width="{w}" height="50" rx="10" fill="{US}" opacity="{1 - 0.15 * i:.2f}"/>' + T_(200, y + 25, t, 16, 800, "#fff", "middle"))
        if sub:
            s.append(T_(200, y + 42, sub, 11.5, 600, "#fff", "middle"))
    s.append(T_(200, 320, f"5-year average, Monte Carlo: {l50:.1f}", 18, 800, INK, "middle") + T_(200, 344, f"8 in 10 futures: {l10:.1f}–{l90:.1f}", 13.5, 600, MUTED, "middle"))
    s.append(T_(200, 368, "early months: take-up × 0.5, approval × 0.6", 12, 400, MUTED, "middle"))
    x0 = 470
    s.append(T_(x0, 16, "MONEY LENT THROUGH ONE AGENT, A YEAR (MEDIAN)", 12.5, 700, US))
    vals = [sm(f"Money lent per agent, year {y}") for y in range(1, 6)]
    vmax = max(vals)
    for i, v in enumerate(vals):
        bx, base = x0 + 20 + i * 98, 330
        h = 260 * v / vmax
        s.append(f'<rect x="{bx}" y="{base - h}" width="70" height="{h}" rx="6" fill="{THEM}"/>' + T_(bx + 35, base - h - 8, lakh(v, 0) if v < 1e7 else f"₹{v / 1e7:.1f} crore", 12.5, 800, THEM, "middle"))
        s.append(T_(bx + 35, base + 20, f"year {i + 1}", 12, 400, MUTED, "middle"))
    s.append(T_(x0 + 20, 374, f"Top-ups: {sm('Top-ups per 100 borrowers'):.1f} a year per 100 borrowers; repeat loans are rare in 5 years.", 12, 600, MUTED))
    return V.svg(1000, 384, "".join(s))


def a_xsell():
    r = [x for x in XSM if x["key"] not in ("total", "other_v2")]
    if READY:
        assert {"loan_home", "loan_lap"} <= {x["key"] for x in r}, "cohort_mc_crosssell.csv has no housing products yet"
    r.sort(key=lambda x: -float(x["p50"]))
    tot = next(x for x in XSM if x["key"] == "total")
    x0, x1 = 300, 640
    vmax = max(float(x["p50"]) for x in r)
    X = lambda v: x0 + (x1 - x0) * v / vmax
    s = []
    for i, x in enumerate(r):
        y = i * 21
        v = float(x["p50"])
        hl = x["key"] in ("loan_home", "loan_lap")
        s.append(T_(x0 - 10, y + 14, x["product"], 12, 800 if hl else 600, US if hl else INK, "end") + f'<rect x="{x0}" y="{y + 3}" width="{X(v) - x0}" height="15" rx="3" fill="{US if hl else COLS["other"]}"/>'
                 + T_(X(v) + 6, y + 15, f"₹{v:.0f}", 11.5, 800, INK))
    s.append(f'<rect x="700" y="0" width="300" height="150" rx="16" fill="{PAPER}"/>' + T_(720, 30, "BOOKED, A SAVER A YEAR", 12, 700, US)
             + T_(720, 88, f"₹{float(tot['p50']):.0f}", 52, 800, US) + T_(720, 116, f"8 in 10: ₹{float(tot['p10']):.0f}–{float(tot['p90']):.0f}", 14, 600, MUTED))
    inc = re.search(r"([\d,]+) to ([\d,]+)", IVR["IV-04"]["answer"])
    k = lambda t: f"₹{int(t.replace(',', '')) // 1000}k"
    lines = [f"{lakh(float(HOUSE['ticket']), 0)} home loan, {float(HOUSE['years']):.0f} years at {pct(float(HOUSE['rate']))}:",
             f"EMI about {inr(round(float(HOUSE['emi']), -2))} a month,", f"needs about {inr(round(float(HOUSE['income_needed']), -3))} of income.",
             f"Our interview: {k(inc.group(1))}–{k(inc.group(2))} (A11).", "Family income counts (operator)."]
    s.append(f'<rect x="700" y="166" width="300" height="{40 + 19 * len(lines)}" rx="16" fill="{V.TINT["warn"]}"/>' + T_(720, 192, "WHO QUALIFIES FOR A HOME LOAN", 12, 700, WARN))
    for j, ln in enumerate(lines):
        s.append(T_(720, 216 + j * 19, ln, 12.5, 600, INK))
    return V.svg(1000, max(len(r) * 21 + 6, 220 + 19 * len(lines)), "".join(s))


def a_collect():
    e, fe, rec, fb, loss, lw = ag("early_cured"), ag("fee_early"), ag("recovered"), ag("fee_b3"), ag("loss"), ag("loss", "high")
    p90 = sm("Implied share of loans that ever go 90+")
    d1, d2, y1c = sm("31-90 day collection fees"), sm("90+ recovery fees"), sm("Collection fees in the pilot year")
    s = []
    rows_ = [("person", GOOD, "31–90 days behind: the agent brings him back", f"{e * 100:.0f} in 100 loans × ₹{fe:,.0f} a case", f"₹{d1:.0f} a loan", "about 9 months after the loan"),
             ("bank", BAD, "90+ days bad: part is recovered", f"{p90 * 100:.1f} in 100 loans × {rec * 100:.0f}% recovered × fee ₹{fb:,.0f}", f"₹{d2:.0f} a loan", "about 18 months after the loan")]
    for i, (ic, col, t, how, big, when) in enumerate(rows_):
        y = i * 130
        s.append(f'<rect x="0" y="{y}" width="1000" height="114" rx="16" fill="{PAPER}"/>' + V.icon(ic, 20, y + 30, 54, col) + T_(96, y + 40, t, 18, 800, INK)
                 + T_(96, y + 68, how, 14, 400, MUTED) + T_(96, y + 92, when, 13, 400, MUTED) + T_(976, y + 70, big, 30, 800, col, "end"))
    s.append(f'<rect x="0" y="270" width="480" height="110" rx="16" fill="{V.TINT["warn"]}"/>' + T_(20, 300, "LOSSES FALL ON THE LENDER", 12, 700, WARN)
             + T_(20, 336, f"likely {loss * 100:.0f}%, worst {lw * 100:.0f}%", 22, 800, WARN) + T_(20, 362, "Paytm's 4.5–5% is our worst case", 13, 600, INK))
    s.append(f'<rect x="520" y="270" width="480" height="110" rx="16" fill="#fff" stroke="{RULE}" stroke-width="2"/>' + T_(540, 300, "IN THE PILOT YEAR", 12, 700, US)
             + T_(540, 340, f"₹{y1c:.0f}", 30, 800, US) + T_(540, 364, "collection fees are mostly year-2 money", 13, 600, MUTED))
    return V.svg(1000, 384, "".join(s))


def a_years():
    yrs = []
    for y in range(1, 6):
        part = DETM[12 * (y - 1):12 * y]
        f = lambda k: sum(float(r[k]) for r in part)
        yrs.append({"y": y, "savers": float(part[-1]["still_saving"]), "loans": f("loans"), "income": f("income"), "cost": f("cost_total"),
                    "net": f("net"), "cum": float(part[-1]["cum_cash"])})
    vmax = max(abs(r["net"]) for r in yrs)
    s = [T_(0, 16, "ONE AGENT, LIKELY VALUES: P&L EACH YEAR", 12.5, 700, US)]
    base = 170
    for i, r in enumerate(yrs):
        x = 180 + i * 165
        h = 130 * abs(r["net"]) / vmax
        col = GOOD if r["net"] >= 0 else BAD
        s.append(f'<rect x="{x}" y="{base - h if r["net"] >= 0 else base}" width="120" height="{h}" rx="6" fill="{col}"/>')
        s.append(T_(x + 60, (base - h - 8) if r["net"] >= 0 else (base + h + 18), lakh(r["net"], 1, True), 14, 800, col, "middle"))
    s.append(f'<line x1="160" y1="{base}" x2="980" y2="{base}" stroke="{INK}"/>')
    lines = [("Year", lambda r: f"Year {r['y']}"), ("Savers at year end", lambda r: f"{r['savers']:,.0f}"), ("Loans made", lambda r: f"{r['loans']:.0f}"),
             ("Income", lambda r: lakh(r["income"])), ("Cost", lambda r: lakh(r["cost"])), ("Cumulative P&L", lambda r: lakh(r["cum"]))]
    for j, (lab, fn) in enumerate(lines):
        y = 330 + j * 22
        s.append(T_(0, y, lab if j else "", 12.5, 700, MUTED))
        for i, r in enumerate(yrs):
            s.append(T_(240 + i * 165, y, fn(r), 13, 800 if j == 0 else 600, INK, "middle"))
    return V.svg(1000, 330 + len(lines) * 22, "".join(s))


INC = tab("cohort_incentive_sweep")
INC_BASE = next((r for r in INC if "(base)" in r["pay"]), None) or next(r for r in INC if "all 5 years" in r["pay"])
INC_UNCAP = next((r for r in INC if "uncapped" in r["pay"]), INC_BASE)
INC_LATER = next(r for r in INC if re.search(r"then [\d.]+%", r["pay"]) and not r["pay"].endswith(" 0%"))
PAY_RATE = float(re.search(r"([\d.]+)%", INC_BASE["pay"]).group(1)) / 100
PAY_LATE = float(re.search(r"then ([\d.]+)%", INC_LATER["pay"]).group(1)) / 100
if "agent_balance_pay" in DIST:                      # the engine's own input must say the same rate as the sweep
    assert abs(dl("agent_balance_pay") - PAY_RATE) < 1e-9, (dl("agent_balance_pay"), PAY_RATE)
PAY_SAVE = float(INC_BASE["incentive_m60_p50"]) - float(INC_LATER["incentive_m60_p50"])
assert abs((float(INC_UNCAP["incentive_m60_p50"]) - float(INC_LATER["incentive_m60_p50"])) / float(INC_UNCAP["incentive_m60_p50"])
           - (1 - PAY_LATE / PAY_RATE)) < 0.01                                  # uncapped month-60 pay scales with the rate
PAY_CAP = dl("incentive_cap") if "incentive_cap" in DIST else None
pp = lambda r: f"{r * 100:.2f}%"


def a_pay():
    s = []
    rows_ = INC
    x0a, x1a, x0b, x1b = 330, 590, 650, 900
    vmax = max(float(r["cum60_p50"]) for r in rows_)
    s.append(T_(x0a, 14, "IN PROFIT BY MONTH 60", 12, 700, MUTED) + T_(x0b, 14, "MEDIAN P&L AT MONTH 60", 12, 700, MUTED))
    for i, r in enumerate(rows_):
        y = 30 + i * 58
        base = r is INC_BASE
        col = US if base else THEM
        p60, med = float(r["p_cum60_pos"]), float(r["cum60_p50"])
        lab = (r["pay"].replace("+", "salary + ") if r["pay"].startswith("+") else r["pay"]).replace("Rs ", "₹").replace(" (base)", "")
        ll = F2.wrap(lab + (" (our base)" if base else ""), 34)
        for j, ln in enumerate(ll):
            s.append(T_(x0a - 14, y + 26 - 8 * (len(ll) - 1) + j * 16, ln, 13.5, 800 if base else 600, US if base else INK, "end"))
        s.append(f'<rect x="{x0a}" y="{y + 8}" width="{(x1a - x0a) * p60}" height="28" rx="5" fill="{col}" opacity="{1 if base else 0.75}"/>'
                 + T_(x0a + (x1a - x0a) * p60 + 8, y + 28, pct(p60), 14, 800, col))
        s.append(f'<rect x="{x0b}" y="{y + 8}" width="{max((x1b - x0b) * med / vmax, 2)}" height="28" rx="5" fill="{col}" opacity="{1 if base else 0.75}"/>'
                 + T_(x0b + (x1b - x0b) * med / vmax + 8, y + 28, lakh(med), 14, 800, col))
    y = 30 + len(rows_) * 58 + 16
    s.append(f'<rect x="0" y="{y}" width="1000" height="50" rx="14" fill="{V.TINT["good"]}"/>' + T_(500, y + 32,
             (f"From year 6, {pp(PAY_LATE)} instead of {pp(PAY_RATE)} saves about {inr(round(PAY_SAVE, -3))} a month per agent" if PAY_SAVE > 500 else
              f"With the cap, {pp(PAY_LATE)} after year 5 saves nothing: it pays {inr(round(-PAY_SAVE, -2))} more at month 60"), 17, 800, GOOD if PAY_SAVE > 500 else WARN, "middle"))
    s.append(T_(0, y + 78, f"Our base pays him about {lakh(float(INC_BASE['incentive_total60_p50']))} over 5 years on top of his salary (median).", 13, 600, MUTED))
    return V.svg(1000, y + 86, "".join(s))


SWEEP = tab("cohort_signups_sweep")
SWEEP_L = tab("cohort_signups_sweep_likely")


def breakeven_signups():
    """Sign-ups a month where cumulative P&L at month 60 crosses zero at the likely values (linear between sweep points)."""
    pts = [(float(r["signups_a_month"]), float(r["cum_pnl60"])) for r in SWEEP_L]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if va < 0 <= vb:
            return a + (b - a) * (-va) / (vb - va)
    raise SystemExit("cohort_signups_sweep_likely.csv: cumulative P&L at 60 never crosses zero")


def a_signups():
    at_base = [r for r in SWEEP if abs(float(r["signups_a_month"]) - ag("signups_run")) < 1e-9]
    if READY and at_base and abs(float(at_base[0]["p_cum60_pos"]) - P60) > 0.05:
        print(f"WARNING: cohort_signups_sweep.csv at {ag('signups_run'):.0f} sign-ups says {float(at_base[0]['p_cum60_pos']):.0%} in profit by "
              f"month 60; the base run says {P60:.0%}. The sweep predates a change (agent pay?): re-run it.")
    pts = [(float(r["signups_a_month"]), float(r["p_cum60_pos"]), float(r["p_cum36_pos"])) for r in SWEEP]
    base, be = ag("signups_run"), breakeven_signups()
    x0, x1, y0, y1 = 80, 760, 20, 360
    lo, hi = min(p[0] for p in pts), max(p[0] for p in pts)
    X = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    Y = lambda p: y1 - (y1 - y0) * p
    s = []
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}"/>' + T_(x0 - 8, Y(v) + 4, pct(v), 12, 400, MUTED, "end"))
    for p in pts:
        s.append(T_(X(p[0]), y1 + 20, f"{p[0]:.0f}", 12, 400, MUTED, "middle"))
    s.append(T_((x0 + x1) / 2, y1 + 42, "sign-ups a month, once up to speed", 13, 600, MUTED, "middle"))
    s.append(f'<rect x="{X(lo)}" y="{y0}" width="{X(be) - X(lo)}" height="{y1 - y0}" fill="{V.TINT["bad"]}" opacity="0.6"/>')
    room = X(be) - x0 > 110                                   # the break-even label sits left of its line only when there is room
    for v, lab, col, anchor, dx, dy in ((be, f"break-even ~{be:.0f}", BAD, "end" if room else "start", -6 if room else 6, 16),
                                         (base, f"our base {base:.0f}", US, "start", 6, y1 - y0 - 14)):
        s.append(f'<line x1="{X(v)}" y1="{y0}" x2="{X(v)}" y2="{y1}" stroke="{col}" stroke-width="2.5" stroke-dasharray="6 4"/>')
        s.append(halo(T_(X(v) + dx, y0 + dy, lab, 13, 800, col, anchor)))
    for idx, col, lab in ((1, GOOD, "in profit by month 60"), (2, WARN, "in profit by month 36")):
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(p[0]):.1f},{Y(p[idx]):.1f}" for i, p in enumerate(pts))
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.5"/>')
        s.extend(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[idx]):.1f}" r="4.5" fill="{col}"/>' for p in pts)
        s.append(T_(x1 + 12, Y(pts[-1][idx]) + 5, lab, 13.5, 800, col))
    at = next(p for p in pts if abs(p[0] - base) < 1e-9) if any(abs(p[0] - base) < 1e-9 for p in pts) else None
    if at:
        s.append(halo(T_(X(base) - 8, Y(at[1]) - 10, pct(at[1]), 15, 800, GOOD, "end")) + halo(T_(X(base) - 8, Y(at[2]) - 10, pct(at[2]), 15, 800, WARN, "end")))
    s.append(T_(x1 + 12, 300, "Shaded: the likely", 12, 600, BAD) + T_(x1 + 12, 316, "case loses money", 12, 600, BAD))
    return V.svg(1000, y1 + 50, "".join(s))


def a_interview():
    keep = ("IV-01", "IV-03", "IV-04", "IV-06", "IV-07", "IV-08", "IV-10", "IV-11", "IV-12", "IV-13")
    rs = lambda t: t.replace("Rs ", "₹")
    trs = "".join(f'<tr><td>{html.escape(rs(IVR[k]["question"]))}</td><td><b>{html.escape(rs(IVR[k]["answer"]))}</b></td></tr>' for k in keep)
    return f'<div class="ivt"><table><tr><th>Question</th><th>A janta agent\'s answer (15 Oct 2026)</th></tr>{trs}</table></div>'


def a_left_out():
    items = [("phone", INK, "Tele-sales and AI support", f"inside the ₹{dl('support_cost'):.0f} running cost"),
             ("person", INK, "Managers", "the founder in the pilot; team leads at scale are not counted"),
             ("bank", WARN, "Cash route", "needs a legal opinion"),
             ("doc", INK, "The customer app's build", "not yet costed"),
             ("doc", INK, "Partners' licences", f"our own fund-distributor code (ARN); insurance through a broker partner (we keep about "
                                               f"{pct(dl('ins_partner_share'))}); lenders' direct sourcing partner"),
             ("broken", BAD, "Rules risks", "IRDAI caps (in the base), SEBI on digital gold"),
             ("coin", GOOD, "Cash cover", f"fidelity and cash-in-transit insurance about {inr(dl('cash_cover'))} per agent a month (in the numbers)")]
    s = []
    for k, (ic, col, t, sub) in enumerate(items):
        r, c = divmod(k, 2)
        x, y = c * 510, r * 118
        s.append(f'<rect x="{x}" y="{y}" width="490" height="108" rx="16" fill="{PAPER}"/>' + V.icon(ic, x + 20, y + 30, 48, col)
                 + T_(x + 88, y + 36, t, 18, 800, INK))
        for j, ln in enumerate(F2.wrap(sub, 50)):
            s.append(T_(x + 88, y + 60 + j * 18, ln, 13.5, 400, MUTED))
    return V.svg(1000, 4 * 118, "".join(s))



# ---------- Part 4: the company (every number from tables/company_*) ----------
CL = {r["Line"]: r for r in tab("company_pnl_ladder_yearly")}
CFY = {r["Line"]: r for r in tab("company_cashflow_yearly")}
CMO = tab("company_monthly")
M18 = {r["Measure"]: r for r in tab("company_m18")}
BEC = {r["Measure"]: r for r in tab("company_breakeven_customers") if r["Plan"].startswith("Base")}
LEV = tab("company_levers")
FSC = tab("company_fleet_scenarios")
HCT = tab("company_headcount")
CMC = {r["Measure"]: r for r in tab("company_mc_summary")}
INPUTS_SHEET = json.load((T / "company_gsheet_spec.json").open())["sheets"][0]
USED.add("company_gsheet_spec.json")
YRS = (1, 2, 3, 4, 5)


def cy(line, y):
    return float(CL[line][f"Year {y}"])


def cmo(col, m):
    return float(CMO[m - 1][col])


def m18(name):
    return M18[name]["Value"]


def crore(x, d=1, sign=False):
    sg = "−" if x < 0 else ("+" if sign and x > 0 else "")
    return f"{sg}₹{abs(x) / 1e7:.{d}f} crore"


def money(x):
    """₹ lakh below a crore, ₹ crore above."""
    return crore(x) if abs(x) >= 1e7 else lakh(x)


def first_year(line, cond=lambda v: v > 0):
    return next((y for y in YRS if cond(cy(line, y))), None)


SEED, SERIES_A = float(CFY["Cash flow, financing: seed (lands at m0, shown in month 1)"]["Year 1"]), \
    sum(float(CFY["Cash flow, financing: Series A (end of month 18)"][f"Year {y}"]) for y in YRS)
A_MONTH = int(next(int(r["Month"]) for r in CMO if float(r["Cash flow, financing: Series A (end of month 18) (Rs)"]) > 0))
SEED_OUT, A_BY = int(float(m18("Month the seed alone runs out"))), int(float(m18("The Series A must close by month")))
AGENTS_A = int(float(m18("Agents working")))
CENTRAL_N = int(float(next(r for r in HCT if r["Department"] == "Central team")["Year 5"]))
FIELD_MGRS = int(sum(float(r["Year 5"]) for r in HCT if r["Department"] == "Field management"))
LOW = min((float(r["Closing cash, with the Series A (Rs)"]), int(r["Month"])) for r in CMO)
CASH60 = float(CMO[-1]["Closing cash, with the Series A (Rs)"])
CASH60_MC = [float(CMC["Cash at month 60, with the Series A"][k]) for k in ("P10", "Median (P50)", "P90")]
LADDER = (("Revenue, total", "Revenue", THEM), ("CM1 (transaction margin)", "CM1", "#4E9BD9"), ("CM2 (after serving the book)", "CM2", "#9b8f7d"),
          ("CM3 (after acquiring customers)", "CM3", COLS["cards"]), ("EBITDA", "EBITDA", US), ("PAT (net profit after tax)", "PAT", INK))
PAT_YEAR, EBITDA_YEAR, CM3_YEAR = first_year("PAT (net profit after tax)"), first_year("EBITDA"), first_year("CM3 (after acquiring customers)")
BE_SAVERS = float(BEC["Rule of thumb: break-even savers = central costs a month / mature CM3 per saver a month"]["Value"])
CENTRAL_M = float(BEC["Central costs a month, months 49-60"]["Value"])
CM3_SAVER = float(BEC["Mature CM3 per active saver a month (months 49-60)"]["Value"])
SAVERS60 = float(BEC["Active savers the plan has at m60"]["Value"])
assert abs(BE_SAVERS - CENTRAL_M / CM3_SAVER) < 1.0
ATTRITION = next(float(v) for k, v in INPUTS_SHEET["cells"].items() if k.startswith("B") and
                 str(INPUTS_SHEET["cells"].get("A" + k[1:], "")).startswith("Agents who leave a year"))
assert any(abs(float(r["Value that gets the plan to break-even by m48"]) - float(next(x for x in LEV if x["Lever"].startswith("Searched: take-up"))["Value needed for break-even by m48"].replace("x ", ""))) < 1e-9
           for r in tab("company_plan_assumption_needed") if r["Value that gets the plan to break-even by m48"][:1].isdigit())
NOT60 = lambda v: v in ("", None) or str(v).startswith("not") or str(v).startswith("never")


def lakhs(n):
    return f"{n / 1e5:.1f} lakh"


def c_plan():
    x0, x1, y0, y1 = 60, 700, 120, 330
    X = lambda m: x0 + (x1 - x0) * m / 60
    amax = max(float(r["Agents working"]) for r in CMO)
    Y = lambda a: y1 - (y1 - y0) * a / amax
    pts = [(0, 0.0)] + [(int(r["Month"]), float(r["Agents working"])) for r in CMO]
    s = [f'<path d="M{X(0)},{y1} ' + " ".join(f"L{X(m):.1f},{Y(a):.1f}" for m, a in pts) + f' L{X(60)},{y1} Z" fill="{US}" opacity="0.85"/>',
         f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}"/>']
    for m in (0, 12, 24, 36, 48, 60):
        s.append(T_(X(m), y1 + 20, str(m), 12, 400, MUTED, "middle"))
    steps = [(int(r["Month"]), int(float(r["Cities"]))) for i, r in enumerate(CMO) if i == 0 or r["Cities"] != CMO[i - 1]["Cities"]]
    for m, c in steps:
        s.append(f'<circle cx="{X(m)}" cy="{y1 + 44}" r="5" fill="{THEM}"/>' + T_(X(m) + 8, y1 + 49, f"{c}" + (" cities" if (m, c) == steps[-1] else ""), 12.5, 700, THEM))
    for m, lab, col, yy in ((0, f"Seed {crore(SEED, 0)}", GOOD, 30), (A_MONTH, f"Series A {crore(SERIES_A, 0)}", GOOD, 30)):
        s.append(f'<line x1="{X(m)}" y1="{yy + 8}" x2="{X(m)}" y2="{y1}" stroke="{col}" stroke-width="2.5"/>' + f'<path d="M{X(m)},{yy - 12} h16 l-5,9 l5,9 h-16 z" fill="{col}"/>'
                 + T_(X(m) + 22, yy + 2, lab, 15, 800, col))
    s.append(f'<rect x="{X(A_BY)}" y="70" width="{X(SEED_OUT) - X(A_BY) + 2}" height="{y1 - 70}" fill="{V.TINT["bad"]}"/>')
    s.append(T_(X(SEED_OUT) + 8, 86, f"must close by month {A_BY}; the seed runs out in month {SEED_OUT}", 12.5, 700, BAD))
    for k, (big, lab, col) in enumerate(((f"{AGENTS_A}", "agents", US), (f"{FIELD_MGRS}", "field managers", THEM), (f"{CENTRAL_N}", "central team", INK))):
        y = 40 + k * 100
        s.append(f'<rect x="760" y="{y}" width="240" height="86" rx="14" fill="{PAPER}"/>' + T_(780, y + 54, big, 38, 800, col) + T_(850, y + 52, lab, 16, 700, INK))
    return V.svg(1000, 400, "".join(s))


def c_pnl():
    vals = {k: [cy(k, y) for y in YRS] for k, *_ in LADDER}
    vmax, vmin = max(max(v) for v in vals.values()), min(min(v) for v in vals.values())
    x0, x1, y0, y1 = 120, 1000, 10, 230
    Y = lambda v: y0 + (y1 - y0) * (vmax - v) / (vmax - vmin)
    gw = (x1 - x0) / 5
    bw = (gw - 30) / len(LADDER)
    s = [f'<line x1="{x0 - 10}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>']
    for i, y in enumerate(YRS):
        for j, (k, lab, col) in enumerate(LADDER):
            v = vals[k][i]
            bx = x0 + i * gw + 15 + j * bw
            s.append(f'<rect x="{bx:.1f}" y="{min(Y(v), Y(0)):.1f}" width="{bw - 2:.1f}" height="{max(abs(Y(v) - Y(0)), 1):.1f}" fill="{col}"/>')
    ty = y1 + 30
    s.append(T_(0, ty, "₹ crore", 12, 700, MUTED))
    for i, y in enumerate(YRS):
        s.append(T_(x0 + i * gw + gw / 2, ty, f"Y{y}", 13, 800, INK, "middle"))
    for j, (k, lab, col) in enumerate(LADDER):
        yy = ty + 24 + j * 22
        s.append(f'<rect x="0" y="{yy - 11}" width="12" height="12" rx="2" fill="{col}"/>' + T_(18, yy, lab, 13, 800, INK))
        for i, y in enumerate(YRS):
            v = vals[k][i]
            s.append(T_(x0 + i * gw + gw / 2, yy, f"{'−' if v < 0 else ''}{abs(v) / 1e7:.1f}", 13, 700, BAD if v < 0 else INK, "middle"))
    return V.svg(1000, ty + 24 + len(LADDER) * 22, "".join(s))


def c_cash():
    m = [0] + [int(r["Month"]) for r in CMO]
    a = [0.0] + [float(r["Closing cash, with the Series A (Rs)"]) for r in CMO]
    so = [0.0] + [float(r["Closing cash, seed only (no Series A) (Rs)"]) for r in CMO]
    cut = next(i for i, v in enumerate(so) if i > A_MONTH and v < 0) + 3
    vmax = max(max(a), CASH60_MC[2])
    vmin = min(min(so[:cut]), 0)
    x0, x1, y0, y1 = 70, 820, 20, 380
    X = lambda t: x0 + (x1 - x0) * t / 60
    Y = lambda v: y1 - (y1 - y0) * (v - vmin) / (vmax - vmin)
    s = []
    step = 10 * 1e7
    v = 0.0
    while v <= vmax:
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}"/>' + T_(x0 - 8, Y(v) + 4, f"{v / 1e7:.0f}", 12, 400, MUTED, "end"))
        v += step
    s.append(T_(x0 - 30, y0 - 4, "₹ crore", 12, 700, MUTED))
    for t in (12, 24, 36, 48, 60):
        s.append(T_(X(t), y1 + 20, str(t), 12, 400, MUTED, "middle"))
    s.append(f'<path d="M' + " L".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in zip(m[:cut], so[:cut])) + f'" fill="none" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    s.append(halo(T_(X(cut - 1) + 6, Y(so[cut - 1]) + 16, "seed only", 13, 800, BAD)))
    s.append(f'<path d="M' + " L".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in zip(m, a)) + f'" fill="none" stroke="{US}" stroke-width="3.5"/>')
    for t, lab in ((0, f"seed {crore(SEED, 0)}"), (A_MONTH, f"Series A {crore(SERIES_A, 0)}")):
        s.append(f'<circle cx="{X(t)}" cy="{Y(a[t] if t else SEED)}" r="7" fill="{GOOD}"/>' + halo(T_(X(t) + 12, Y(a[t] if t else SEED) - 8, lab, 14, 800, GOOD)))
    lv, lm = LOW
    s.append(f'<circle cx="{X(lm)}" cy="{Y(lv)}" r="7" fill="#fff" stroke="{BAD}" stroke-width="3"/>' + f'<line x1="{X(lm)}" y1="{Y(lv) - 8}" x2="{X(6)}" y2="{Y(vmax * 0.42) + 6}" stroke="{BAD}" stroke-width="1.2"/>'
             + halo(T_(X(6) - 4, Y(vmax * 0.42), f"lowest {crore(lv)}, month {lm}", 13, 800, BAD, "middle")))
    lo, mid, hi = CASH60_MC
    s.append(f'<line x1="{X(60) + 14}" y1="{Y(lo)}" x2="{X(60) + 14}" y2="{Y(hi)}" stroke="{US}" stroke-width="6" opacity="0.35"/>')
    s.append(T_(X(60) + 26, Y(a[-1]) + 5, crore(a[-1]), 16, 800, US) + T_(X(60) + 26, Y(a[-1]) + 24, f"8 in 10: {lo / 1e7:.0f}–{hi / 1e7:.0f}", 12, 600, MUTED))
    return V.svg(1000, y1 + 30, "".join(s))


def c_m18():
    sv = float(m18("Savers still saving"))
    tiles = [("person", f"{sv:,.0f}" if sv < 1e5 else lakhs(sv), "savers"), ("jar", money(float(m18("Money in the fund (AUM)"))), "in the fund"),
             ("bank", money(float(m18("Money lent, months 1-18"))), "lent so far"), ("coin", money(float(m18("Revenue run-rate"))), "revenue a year, run-rate"),
             ("broken", money(float(m18("Burn in month 18"))), "burn a month"), ("hands", f"{AGENTS_A} · {int(float(m18('Cities')))}", "agents · cities"),
             ("doc", inr(float(m18("Cost to win a saver, per sign-up"))), "cost to win a saver")]
    s = []
    for k, (ic, big, lab) in enumerate(tiles):
        r, c = divmod(k, 4)
        x, y = c * 252, r * 200
        s.append(f'<rect x="{x}" y="{y}" width="236" height="180" rx="16" fill="{PAPER}"/>' + V.icon(ic, x + 18, y + 18, 40, US)
                 + T_(x + 18, y + 112, big, 30 if len(big) < 12 else 24, 800, US) + T_(x + 18, y + 146, lab, 15, 600, INK))
    return V.svg(1000, 380, "".join(s))


def c_customers():
    m = [int(r["Month"]) for r in CMO]
    sv = [float(r["Savers still saving"]) for r in CMO]
    x0, x1, y0, y1 = 70, 620, 30, 380
    vmax = max(max(sv), BE_SAVERS) * 1.1
    X = lambda t: x0 + (x1 - x0) * t / 60
    Y = lambda v: y1 - (y1 - y0) * v / vmax
    s = []
    for v in range(0, int(vmax) + 1, 50000):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}"/>' + T_(x0 - 8, Y(v) + 4, f"{v / 1e5:.1f}", 12, 400, MUTED, "end"))
    s.append(T_(x0 - 30, y0 - 12, "lakh savers", 12, 700, MUTED))
    for t in (12, 24, 36, 48, 60):
        s.append(T_(X(t), y1 + 20, str(t), 12, 400, MUTED, "middle"))
    s.append(f'<path d="M{X(0)},{Y(0)} ' + " ".join(f"L{X(t):.1f},{Y(v):.1f}" for t, v in zip(m, sv)) + f' L{X(60)},{Y(0)} Z" fill="{THEM}" opacity="0.18"/>')
    s.append(f'<path d="M{X(0)},{Y(0)} ' + " ".join(f"L{X(t):.1f},{Y(v):.1f}" for t, v in zip(m, sv)) + f'" fill="none" stroke="{THEM}" stroke-width="3.5"/>')
    s.append(f'<line x1="{x0}" y1="{Y(BE_SAVERS)}" x2="{x1}" y2="{Y(BE_SAVERS)}" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="7 4"/>')
    s.append(halo(T_(x0 + 8, Y(BE_SAVERS) - 8, f"break-even {lakhs(BE_SAVERS)}", 14, 800, BAD)))
    s.append(halo(T_(X(60) - 6, Y(sv[-1]) - 10, lakhs(sv[-1]), 14, 800, THEM, "end")))
    rows_ = [(lakh(CENTRAL_M), "central costs a month", INK), ("÷", "", MUTED), (f"₹{CM3_SAVER:.2f}", "per saver a month, after serving and acquiring", US),
             ("=", "", MUTED), (lakhs(BE_SAVERS), "savers to break even", BAD)]
    y = 50
    for big, lab, col in rows_:
        if lab:
            s.append(f'<rect x="680" y="{y}" width="320" height="70" rx="14" fill="{PAPER}"/>' + T_(700, y + 34, big, 26, 800, col)
                     + T_(700, y + 56, lab, 12.5, 600, MUTED))
            y += 78
        else:
            s.append(T_(840, y + 12, big, 22, 800, col, "middle"))
            y += 22
    return V.svg(1000, y1 + 30, "".join(s))


LEVER_SHORT = (("Searched: take-up multiple", "Take-up × {v}"), ("Searched: loan-size multiple", "Loan size × {v}"),
               ("Combination: take-up +25% and UPI 60%", "Take-up +25%, UPI 60%"), ("Market: all take-up hazards +25%", "Take-up +25%"),
               ("Market: sign-ups year-1 level 120", "Sign-ups 120 a month"), ("Market: still saving at month 12, 65%", "Still saving 65%"),
               ("Base", "Our base"))


def c_levers():
    pick = []
    for prefix, lab in LEVER_SHORT:
        r = next((x for x in LEV if x["Lever"].startswith(prefix)), None)
        if r:
            v = r["Value needed for break-even by m48"].replace("x ", "")
            pick.append((lab.format(v=v), r["EBITDA break-even month"]))
    x0, x1 = 300, 760
    lo, hi = 36, 60
    X = lambda mo: x0 + (x1 - x0) * (mo - lo) / (hi - lo)
    s = [T_(x0, 12, "EBITDA BREAK-EVEN MONTH", 12, 700, MUTED)]
    for i, (lab, mo) in enumerate(pick):
        y = 26 + i * 46
        base = lab == "Our base"
        s.append(T_(x0 - 12, y + 22, lab, 15, 800 if base else 600, INK, "end"))
        if NOT60(mo):
            s.append(f'<rect x="{x0}" y="{y + 6}" width="{X(hi) - x0}" height="24" rx="5" fill="url(#hatchc)"/>' + T_(X(hi) + 8, y + 24, "after 60", 14, 800, BAD))
        else:
            v = float(mo)
            s.append(f'<rect x="{x0}" y="{y + 6}" width="{X(v) - x0}" height="24" rx="5" fill="{GOOD if v <= 48 else WARN}"/>' + T_(X(v) + 8, y + 24, f"{v:.0f}", 14, 800, GOOD if v <= 48 else WARN))
    for t in (36, 48, 60):
        s.append(f'<line x1="{X(t)}" y1="22" x2="{X(t)}" y2="{26 + len(pick) * 46}" stroke="{RULE}" stroke-dasharray="3 3"/>' + T_(X(t), 40 + len(pick) * 46, str(t), 12, 400, MUTED, "middle"))
    g = next(r for r in FSC if r["Scenario"].startswith("Growth plan"))
    y = 70 + len(pick) * 46
    agents_g = re.search(r"to (\d+) by m60", g["Scenario"]).group(1)
    s.append(f'<rect x="0" y="{y}" width="1000" height="56" rx="14" fill="{V.TINT["warn"]}"/>' + T_(500, y + 35,
             f"The {agents_g}-agent plan: {crore(SERIES_A, 0)} funds it, but year-5 EBITDA is {crore(float(g['EBITDA year 5 (Rs)']))}", 16, 800, WARN, "middle"))
    defs = (f'<defs><pattern id="hatchc" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="7" height="7" fill="{V.TINT["bad"]}"/><line x1="0" y1="0" x2="0" y2="7" stroke="{BAD}" stroke-width="2" opacity="0.4"/></pattern></defs>')
    return V.svg(1000, y + 60, defs + "".join(s))


def c_one_line():
    g = GATES
    steps = [("hands", "Prove one agent", [f"one salaried agent, 12 months", f"stop below {float(g['signups_run']['stop']):.0f} sign-ups a month",
                                              f"or {pct(float(g['r12']['stop']))} still saving"], US),
             ("bank", "Build the company", [f"seed {crore(SEED, 0)}; {AGENTS_A} agents by month {A_MONTH}",
                                                f"Series A {crore(SERIES_A, 0)} by month {A_BY}",
                                                f"PAT positive in year {PAT_YEAR}" if PAT_YEAR else "PAT not positive by year 5"], THEM)]
    s = []
    for i, (ic, head, lines, col) in enumerate(steps):
        x = i * 520
        s.append(f'<rect x="{x}" y="0" width="480" height="300" rx="20" fill="{PAPER}"/><rect x="{x}" y="0" width="480" height="8" rx="4" fill="{col}"/>')
        s.append(V.icon(ic, x + 24, 30, 56, col) + T_(x + 96, 68, head, 24, 800, col))
        for k, ln in enumerate(lines):
            s.append(f'<circle cx="{x + 40}" cy="{136 + k * 52}" r="7" fill="{col}"/>' + T_(x + 60, 142 + k * 52, ln, 18, 600, INK))
        if i == 0:
            s.append(V.arrow(486, 150, 514, 150, INK, 3.5))
    return V.svg(1000, 304, "".join(s))


def cash_table(rows_, cols, fmt, widths=None, cls="ctab"):
    th = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    trs = "".join("<tr" + (' class="b"' if bold else "") + ">" + "".join(f"<td>{html.escape(str(c))}</td>" for c in cells) + "</tr>" for cells, bold in rows_)
    return f'<div class="{cls}"><table><tr>{th}</tr>{trs}</table></div>'


def lk(v):
    return f"{'−' if v < 0 else ''}{abs(v) / 1e5:,.1f}"


def a_ladder(part):
    lines = list(CL)
    cut = lines.index("CM3, share of revenue") + 1
    lines = lines[:cut] if part == 1 else lines[cut:]
    bold = lambda ln: not ln.startswith(("Revenue:", "Direct:", "Servicing:", "Acquisition:", "Central:", "Depreciation:")) and "share" not in ln
    rows_ = []
    for ln in lines:
        r = CL[ln]
        f = (lambda v: f"{float(v) * 100:.0f}%") if r["Unit"] == "share" else (lambda v: lk(float(v)))
        rows_.append(([ln.replace("Rs ", "₹"), *[f(r[f"Year {y}"]) for y in YRS], f(r["Five years"])], bold(ln)))
    return cash_table(rows_, ["₹ lakh", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Five years"], None)


def a_cashflow():
    rows_ = []
    for ln, r in CFY.items():
        month = "Month" in ln
        f = (lambda v: f"{float(v):.0f}") if month else (lambda v: lk(float(v)))
        rows_.append(([ln.replace("Rs ", "₹"), *[f(r[f"Year {y}"]) for y in YRS], f(r["Five years"])], ln.startswith(("Cash from", "Net change", "Closing"))))
    return cash_table(rows_, ["₹ lakh", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Five years"], None, cls="ctab cf")


def a_headcount():
    keep = [r for r in HCT if r["Role"] in ("Agents", "City managers", "Team leads") or r["Role"] == "Department total" or r["Department"] in ("Central team", "All")]
    rows_ = [([(r["Department"] if r["Role"] == "Department total" else (r["Role"] if r["Department"] not in ("Central team", "All") else r["Department"] + ", total")),
               *[f"{float(r[f'Year {y}']):.0f}" for y in YRS]], r["Department"] in ("Central team", "All")) for r in keep]
    return cash_table(rows_, ["People at year end", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"], None, cls="ctab hc")


def a_costs():
    cells = INPUTS_SHEET["cells"]
    rows = {}
    for k, v in cells.items():
        m = re.match(r"([A-Z]+)(\d+)", k)
        rows.setdefault(int(m.group(2)), {})[m.group(1)] = v
    out, stop = [], False
    for r in sorted(rows)[1:]:
        x = rows[r]
        a, b, c = str(x.get("A", "")), x.get("B", ""), str(x.get("C", ""))
        if a.startswith(("Worked out", "Cross-sell split")):
            stop = a.startswith("Worked out")
            if stop:
                break
            continue
        if a.startswith(("Cross-sell split:", "Point ", "Shape of the ramp", "Agents on the street", "Growth hires", "Seed", "Series A")) or a == "Role":
            continue
        if b in ("", None) and not c:
            out.append(([a, "", ""], True))
            continue
        if isinstance(b, (int, float)):
            unit = c
            if c in ("share", "a year") and float(b) < 1:
                val = f"{float(b) * 100:g}%"
            elif c.startswith(("Rs", "₹")) or (c in ("Founders", "Technology", "Compliance and operations", "Growth and marketing", "Finance and admin")):
                val = inr(float(b)) if float(b) < 1e7 else crore(float(b), 0)
                unit = re.sub(r"^(Rs|₹)\s*", "", c)
            else:
                val = f"{float(b):g}"
        else:
            val, unit = str(b), c
        out.append(([a.replace("Rs ", "₹"), val, unit], False))
    half = (len(out) + 1) // 2
    while half < len(out) and out[half][1]:
        half += 1
    return ('<div class="ccols">' + cash_table(out[:half], ["Input", "Value", ""], None, cls="ctab cc")
            + cash_table(out[half:], ["Input", "Value", ""], None, cls="ctab cc") + "</div>")



# ---------- Part 4: the unicorn track (every number from tables/unicorn_* and growth_frontier.csv) ----------
UY = {r["Line"]: r for r in tab("unicorn_yearly")}
URD = tab("unicorn_rounds")
UMS = {r["When"]: r for r in tab("unicorn_milestones")}
UMC = {r["Measure"]: r for r in tab("unicorn_mc_summary")}
UMO = tab("unicorn_monthly")
GFR = tab("growth_frontier")
UYRS = tuple(range(1, 9))
uy = lambda line, y: float(UY[line][f"Year {y}"])
um = lambda col, m: float(UMO[m - 1][col])
PLAN_TXT = UMC["Plan"]["Value"]
_pm = re.search(r"([\d,]+) agents by m18, \+([\d,]+) a month, cap ([\d,]+)", PLAN_TXT)
U_A18, U_STEP, U_CAP = (int(g.replace(",", "")) for g in _pm.groups())
assert abs(um("Agents working", 18) - U_A18) < 0.5 and abs(uy("Agents at year end", 5) - U_CAP) < 0.5
U_RAISED = sum(float(r["Amount (Rs)"]) for r in URD)
U_UNI = next(r for r in URD if r["Unicorn round"] == "yes")
U_FOUNDERS = float(U_UNI["Founders % after"])
U_EBITDA_M = next(i + 1 for i in range(len(UMO)) if all(float(x["EBITDA (Rs)"]) > 0 for x in UMO[i:]))
U_EBITDA_Y = (U_EBITDA_M - 1) // 12 + 1
U_WORST_Y = min(range(1, 6), key=lambda y: uy("EBITDA", y))
CHK_R = next(v for k, v in UMS.items() if k.startswith("UNICORN CHECK") and "Revenue lens" in k)
CHK_A = next(v for k, v in UMS.items() if k.startswith("UNICORN CHECK") and "AUM lens" in k)
MULT_R = float(re.search(r"\((\d+(?:\.\d+)?) x ARR\)", next(k for k in UMS if "Revenue lens" in k)).group(1))
MULT_A = float(re.search(r"\((\d+(?:\.\d+)?) x AUM\)", next(k for k in UMS if "AUM lens" in k)).group(1))
P_BOTH = float(UMC["P(both lenses >= $1B at m60)"]["Value"])
P_CASH96 = float(UMC["P(cash >= 0 through m96)"]["Value"])
THRESH = float(CHK_R["Threshold (Rs)"])
JUDGE = "our judgement, one comparable (Stable Money)"
OTHER = next(r for r in GFR if r["Set"].startswith("Year-5 EBITDA >= 0") and r["Rank"] == "1")
assert OTHER["PAT positive only because of interest"] == "no"


def cr(x, d=0):
    """₹ crore with Indian grouping, whole by default."""
    v = abs(x) / 1e7
    body = inr(round(v, d))[1:] if d == 0 else f"{v:,.{d}f}"
    return ("−" if x < 0 else "") + f"₹{body} crore"


def big_n(n):
    return f"{n / 1e7:.1f} crore" if n >= 1e7 else (f"{n / 1e5:.1f} lakh" if n >= 1e5 else f"{n:,.0f}")


def u_plan():
    rows_ = (("Agents", [uy("Agents at year end", y) for y in range(1, 6)], lambda v: f"{v:,.0f}", US),
             ("Cities", [uy("Cities at year end", y) for y in range(1, 6)], lambda v: f"{v:,.0f}", THEM),
             ("Savers", [uy("Active savers at year end", y) for y in range(1, 6)], big_n, GOOD))
    x0, cw = 170, 166
    s = []
    for i in range(5):
        s.append(T_(x0 + i * cw + cw / 2, 14, f"Year {i + 1}", 15, 800, INK, "middle"))
    for j, (lab, vals, f, col) in enumerate(rows_):
        y = 36 + j * 120
        vmax = max(vals)
        s.append(f'<rect x="0" y="{y}" width="1000" height="108" rx="14" fill="{PAPER}"/>' + T_(20, y + 60, lab, 19, 800, col))
        for i, v in enumerate(vals):
            h = max(3, 58 * v / vmax)
            bx = x0 + i * cw + 30
            s.append(f'<rect x="{bx}" y="{y + 96 - h}" width="{cw - 60}" height="{h}" rx="5" fill="{col}" opacity="{0.45 + 0.12 * i:.2f}"/>')
            s.append(T_(bx + (cw - 60) / 2, y + 96 - h - 8, f(v), 14, 800, col, "middle"))
    return V.svg(1000, 36 + 3 * 120, "".join(s))


def u_pnl():
    lines = (("Revenue, total", "Revenue", THEM), ("CM3", "CM3", COLS["cards"]), ("EBITDA", "EBITDA", US), ("PAT", "PAT", INK))
    vals = {k: [uy(k, y) for y in UYRS] for k, *_ in lines}
    vmax, vmin = max(max(v) for v in vals.values()), min(min(v) for v in vals.values())
    x0, x1, y0, y1 = 110, 1000, 10, 230
    Y = lambda v: y0 + (y1 - y0) * (vmax - v) / (vmax - vmin)
    gw = (x1 - x0) / len(UYRS)
    bw = (gw - 20) / len(lines)
    s = [f'<rect x="{x0 + 5 * gw}" y="0" width="{3 * gw}" height="{y1 + 150}" fill="#eceae5" opacity="0.7"/>',
         T_(x0 + 6.5 * gw, y1 + 140, "years 6–8: context", 12, 700, MUTED, "middle"),
         f'<line x1="{x0 - 10}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{INK}"/>']
    for i, y in enumerate(UYRS):
        for j, (k, lab, col) in enumerate(lines):
            v = vals[k][i]
            s.append(f'<rect x="{x0 + i * gw + 10 + j * bw:.1f}" y="{min(Y(v), Y(0)):.1f}" width="{bw - 2:.1f}" height="{max(abs(Y(v) - Y(0)), 1):.1f}" fill="{col}"/>')
    ty = y1 + 26
    s.append(T_(0, ty, "₹ crore", 12, 700, MUTED))
    for i, y in enumerate(UYRS):
        s.append(T_(x0 + i * gw + gw / 2, ty, f"Y{y}", 13, 800, INK, "middle"))
    for j, (k, lab, col) in enumerate(lines):
        yy = ty + 22 + j * 22
        s.append(f'<rect x="0" y="{yy - 11}" width="12" height="12" rx="2" fill="{col}"/>' + T_(18, yy, lab, 13, 800, INK))
        for i, y in enumerate(UYRS[:5]):
            v = vals[k][i]
            txt = f"{abs(v) / 1e7:.1f}" if abs(v) < 1e8 else inr(round(abs(v) / 1e7))[1:]
            s.append(T_(x0 + i * gw + gw / 2, yy, f"{'−' if v < 0 else ''}{txt}", 13, 700, BAD if v < 0 else INK, "middle"))
    return V.svg(1000, ty + 22 + len(lines) * 22 + 10, "".join(s))


def u_cash():
    m = [0] + [int(r["Month"]) for r in UMO]
    c = [0.0] + [float(r["Closing cash, with every round (Rs)"]) for r in UMO]
    vmax = max(c) * 1.08
    x0, x1, y0, y1 = 70, 960, 30, 380
    X = lambda t: x0 + (x1 - x0) * t / m[-1]
    Y = lambda v: y1 - (y1 - y0) * v / vmax
    s = []
    step = next(st for st in (100, 200, 250, 500, 1000) if vmax / 1e7 / st <= 6) * 1e7
    v = 0.0
    while v <= vmax:
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}"/>' + T_(x0 - 8, Y(v) + 4, inr(v / 1e7)[1:], 12, 400, MUTED, "end"))
        v += step
    s.append(T_(x0 - 30, y0 - 12, "₹ crore", 12, 700, MUTED))
    for t in range(12, m[-1] + 1, 12):
        s.append(T_(X(t), y1 + 20, str(t), 12, 400, MUTED, "middle"))
    s.append(f'<rect x="{X(60)}" y="{y0}" width="{X(m[-1]) - X(60)}" height="{y1 - y0}" fill="#eceae5" opacity="0.6"/>' + T_((X(60) + X(m[-1])) / 2, y0 + 16, "context", 12, 700, MUTED, "middle"))
    s.append(f'<path d="M' + " L".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in zip(m, c)) + f'" fill="none" stroke="{US}" stroke-width="3.5"/>')
    months = [int(r["Month"]) for r in URD]
    for k, r in enumerate(URD):
        t = months[k]
        v = c[t] if t else float(r["Amount (Rs)"])
        lab = f"{r['Round']} {cr(float(r['Amount (Rs)']))}"
        near_next = k + 1 < len(months) and months[k + 1] - t <= 8
        near_prev = k > 0 and t - months[k - 1] <= 8
        anchor, dx = ("end", -10) if near_next else (("start", 10) if near_prev or t == 0 else ("middle", 0))
        s.append(f'<circle cx="{X(t)}" cy="{Y(v)}" r="7" fill="{GOOD}" stroke="#fff" stroke-width="2"/>')
        s.append(halo(T_(X(t) + dx, Y(v) - 62 if t == 0 else Y(v) - 14, lab, 13, 800, GOOD, anchor)))
    return V.svg(1000, y1 + 30, "".join(s))


def u_rounds():
    n = len(URD)
    import math as _m
    posts = [float(r["Post-money (Rs)"]) for r in URD]
    lo, hi = _m.log10(min(posts)) - 0.3, _m.log10(max(posts)) + 0.15
    x0, cw, y0, y1 = 40, 150, 40, 300
    Y = lambda v: y1 - (y1 - y0) * (_m.log10(v) - lo) / (hi - lo)
    s = [f'<line x1="0" y1="{Y(THRESH)}" x2="{x0 + n * cw}" y2="{Y(THRESH)}" stroke="{BAD}" stroke-width="2" stroke-dasharray="6 4"/>',
         halo(T_(4, Y(THRESH) - 6, "$1B", 13, 800, BAD))]
    pts = []
    for i, r in enumerate(URD):
        x = x0 + i * cw + 30
        v = float(r["Post-money (Rs)"])
        s.append(f'<rect x="{x}" y="{Y(v)}" width="{cw - 60}" height="{y1 - Y(v)}" rx="5" fill="{THEM}" opacity="{0.5 + 0.08 * i:.2f}"/>')
        s.append(halo(T_(x + (cw - 60) / 2, Y(v) - 8, cr(v), 13, 800, THEM, "middle")))
        s.append(T_(x + (cw - 60) / 2, y1 + 22, r["Round"] + (" ★" if r["Unicorn round"] == "yes" else ""), 15, 800, INK, "middle")
                 + T_(x + (cw - 60) / 2, y1 + 40, f"month {r['Month']}", 12, 400, MUTED, "middle"))
        pts.append((x + (cw - 60) / 2, float(r["Founders % after"])))
    fy0, fy1 = 380, 470
    FY = lambda p: fy1 - (fy1 - fy0) * p
    s.append(T_(0, fy0 - 6, "FOUNDERS OWN", 12, 700, US))
    s.append(f'<path d="M' + " L".join(f"{x:.1f},{FY(p):.1f}" for x, p in pts) + f'" fill="none" stroke="{US}" stroke-width="3"/>')
    for x, p in pts:
        s.append(f'<circle cx="{x}" cy="{FY(p)}" r="5" fill="{US}"/>' + halo(T_(x, FY(p) - 10, pct(p, 1).replace(".0%", "%"), 13, 800, US, "middle")))
    return V.svg(1000, fy1 + 10, "".join(s))


def u_lenses():
    s = []
    vmax = max(float(CHK_R["Valuation on the lens (Rs)"]), float(CHK_A["Valuation on the lens (Rs)"])) * 1.1
    x0, x1 = 300, 780
    X = lambda v: x0 + (x1 - x0) * v / vmax
    items = [(f"{MULT_R:g} × ARR", f"ARR {cr(float(CHK_R['ARR (Rs)']))}", CHK_R, THEM), (f"{MULT_A:g} × AUM", f"AUM {cr(float(CHK_A['AUM (Rs)']))}", CHK_A, US)]
    for i, (lab, sub, r, col) in enumerate(items):
        y = 30 + i * 130
        v, mg = float(r["Valuation on the lens (Rs)"]), float(r["Margin over $1B (share)"])
        s.append(T_(x0 - 16, y + 30, lab, 22, 800, col, "end") + T_(x0 - 16, y + 54, sub, 14, 600, MUTED, "end"))
        s.append(f'<rect x="{x0}" y="{y + 6}" width="{X(v) - x0}" height="56" rx="8" fill="{col}"/>')
        s.append(T_(X(v) + 10, y + 42, cr(v), 18, 800, col) + T_(X(v) + 10, y + 64, f"+{mg * 100:.0f}% over $1B", 14, 800, GOOD))
    s.append(f'<line x1="{X(THRESH)}" y1="10" x2="{X(THRESH)}" y2="290" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="6 4"/>' + halo(T_(X(THRESH) + 6, 22, "$1B", 14, 800, BAD)))
    s.append(f'<rect x="0" y="300" width="480" height="96" rx="16" fill="{V.TINT["good"]}"/>' + T_(24, 350, pct(P_BOTH), 40, 800, GOOD)
             + T_(150, 342, "of futures clear both", 16, 700, GOOD) + T_(150, 364, "lenses at month 60", 16, 700, GOOD))
    s.append(f'<rect x="510" y="300" width="490" height="96" rx="16" fill="{V.TINT["warn"]}"/>' + T_(530, 340, "BOTH MULTIPLES ARE", 12, 700, WARN)
             + T_(530, 370, JUDGE, 15, 800, WARN))
    return V.svg(1000, 400, "".join(s))


def u_year5():
    tiles = [("person", f"{uy('Agents at year end', 5):,.0f}", "agents"), ("bank", f"{uy('Cities at year end', 5):,.0f}", "cities"),
             ("hands", big_n(uy("Active savers at year end", 5)), "savers"), ("jar", cr(uy("AUM at year end", 5)), "in the fund"),
             ("coin", cr(uy("ARR at year end (12 x the month's revenue)", 5)), "revenue a year, run-rate"),
             ("doc", cr(uy("Money lent in the year, personal loans incl. top-ups", 5)), "personal loans in year 5"),
             ("phone", f"{uy('Central team at year end', 5):,.0f}", "central team"),
             ("person", f"{max(uy('Peak agents hired in a month (growth and replacements)', y) for y in range(1, 6)):,.0f}", "hires in the peak month")]
    s = []
    for k, (ic, big, lab) in enumerate(tiles):
        r, c = divmod(k, 4)
        x, y = c * 252, r * 190
        s.append(f'<rect x="{x}" y="{y}" width="236" height="172" rx="16" fill="{PAPER}"/>' + V.icon(ic, x + 18, y + 18, 38, US)
                 + T_(x + 18, y + 104, big, 28 if len(big) < 12 else 22, 800, US) + T_(x + 18, y + 136, lab, 14.5, 600, INK))
    return V.svg(1000, 362, "".join(s))


def u_risk():
    worst = uy("EBITDA", U_WORST_Y)
    low96 = float(UMC["Lowest cash through m96"]["P10"])
    peak_h = max(uy("Peak agents hired in a month (growth and replacements)", y) for y in range(1, 6))
    tiles = [("broken", "Peak losses", f"EBITDA {cr(worst)} in year {U_WORST_Y}", BAD),
             ("person", "Running at scale", f"{uy('Cities at year end', 5):,.0f} cities · {peak_h:,.0f} hires a month · {uy('Central team at year end', 5):,.0f} central staff", WARN),
             ("pct", "Valuation is judgement", f"{MULT_R:g} × ARR and {MULT_A:g} × AUM: one comparable", WARN),
             ("coin", "The tails", f"cash lasts to month 96 in {pct(P_CASH96)}; a bad tenth needs {cr(-low96)}", BAD)]
    s = []
    for k, (ic, head, sub, col) in enumerate(tiles):
        r, c = divmod(k, 2)
        x, y = c * 510, r * 190
        s.append(f'<rect x="{x}" y="{y}" width="490" height="172" rx="16" fill="{PAPER}"/><rect x="{x}" y="{y}" width="8" height="172" rx="4" fill="{col}"/>'
                 + V.icon(ic, x + 28, y + 26, 48, col) + T_(x + 96, y + 54, head, 21, 800, INK))
        for j, ln in enumerate(F2.wrap(sub, 40)):
            s.append(T_(x + 96, y + 90 + j * 24, ln, 16, 700, col))
    return V.svg(1000, 362, "".join(s))


def u_other():
    o_raised = float(OTHER["Total raised, Series A at m18 (Rs)"])
    o_lens = MULT_A * float(OTHER["AUM at m60 (Rs)"])
    rows_ = [("Money raised by month 60", cr(U_RAISED), cr(o_raised)),
             ("Savers at month 60", big_n(uy("Active savers at year end", 5)), big_n(float(OTHER["Active savers at m60"]))),
             ("EBITDA positive from", f"month {U_EBITDA_M}", f"month {float(OTHER['EBITDA break-even month']):.0f}"),
             (f"{MULT_A:g} × AUM at month 60", cr(float(CHK_A["Valuation on the lens (Rs)"])), cr(o_lens))]
    s = [T_(600, 24, "UNICORN TRACK", 14, 800, US, "middle"), T_(860, 24, f"PROFITABLE, {OTHER['Agents at m18']} AGENTS", 14, 800, THEM, "middle")]
    for i, (lab, a, b) in enumerate(rows_):
        y = 44 + i * 82
        s.append(f'<rect x="0" y="{y}" width="1000" height="70" rx="14" fill="{PAPER if i % 2 == 0 else "#fff"}"/>' + T_(20, y + 42, lab, 18, 700, INK)
                 + T_(600, y + 44, a, 22, 800, US, "middle") + T_(860, y + 44, b, 22, 800, THEM, "middle"))
    return V.svg(1000, 44 + len(rows_) * 82, "".join(s))


def u_one_line():
    g = GATES
    steps = [("hands", "Prove one agent", ["one salaried agent, 12 months", f"stop below {float(g['signups_run']['stop']):.0f} sign-ups a month",
                                          f"or {pct(float(g['r12']['stop']))} still saving"], US),
             ("bank", "The unicorn track", [f"{U_A18} agents by month 18, +{U_STEP} a month", f"{cr(U_RAISED)} raised in {len(URD)} rounds",
                                            "unicorn on paper at month 60"], THEM)]
    s = []
    for i, (ic, head, lines, col) in enumerate(steps):
        x = i * 520
        s.append(f'<rect x="{x}" y="0" width="480" height="300" rx="20" fill="{PAPER}"/><rect x="{x}" y="0" width="480" height="8" rx="4" fill="{col}"/>')
        s.append(V.icon(ic, x + 24, 30, 56, col) + T_(x + 96, 68, head, 24, 800, col))
        for k, ln in enumerate(lines):
            s.append(f'<circle cx="{x + 40}" cy="{136 + k * 52}" r="7" fill="{col}"/>' + T_(x + 60, 142 + k * 52, ln, 18, 600, INK))
        if i == 0:
            s.append(V.arrow(486, 150, 514, 150, INK, 3.5))
    return V.svg(1000, 304, "".join(s))


def ua_rounds():
    rows_ = [([r["Round"], r["Month"], cr(float(r["Amount (Rs)"])), cr(float(r["Pre-money (Rs)"])), cr(float(r["Post-money (Rs)"])),
               pct(float(r["Dilution (new investors' share of post-money)"]), 1), pct(float(r["Founders % after"]), 1), pct(float(r["ESOP % after"]), 1),
               pct(float(r["Investors % after"]), 1), r["Priced on"].replace("Rs ", "₹")], r["Unicorn round"] == "yes") for r in URD]
    rows_.append((["Total", "", cr(U_RAISED), "", "", "", "", "", "", ""], True))
    return cash_table(rows_, ["Round", "Month", "Raised", "Pre-money", "Post-money", "Dilution", "Founders", "ESOP", "Investors", "Priced on"], None, cls="ctab cf")


def ua_ladder():
    keep = [k for k in UY if UY[k]["Unit"] == "Rs" and not k.startswith(("Money lent", "Revenue lens", "AUM lens", "AUM at", "ARR at", "Equity", "Closing"))]
    bold = lambda k: k in ("Revenue, total", "CM1", "CM2", "CM3", "EBITDA", "PAT")
    rows_ = [([k.replace("Rs ", "₹"), *[f"{'−' if uy(k, y) < 0 else ''}{abs(uy(k, y)) / 1e7:,.1f}" for y in UYRS]], bold(k)) for k in keep]
    return cash_table(rows_, ["₹ crore", *[f"Year {y}" for y in UYRS]], None)


def ua_cashflow():
    cols = [k for k in UMO[0] if k.startswith(("Cash flow,", "Cash from", "Net change"))]
    rows_ = []
    for k in cols:
        vals = [sum(float(r[k]) for r in UMO if int(r["Year"]) == y) for y in UYRS]
        rows_.append(([k.replace(" (Rs)", "").replace("Rs ", "₹"), *[f"{'−' if v < 0 else ''}{abs(v) / 1e7:,.1f}" for v in vals]], k.startswith(("Cash from", "Net change"))))
    close = [float(next(r for r in reversed(UMO) if int(r["Year"]) == y)["Closing cash, with every round (Rs)"]) for y in UYRS]
    assert all(abs(a - uy("Closing cash", y)) < 1.0 for a, y in zip(close, UYRS))
    rows_.append((["Closing cash", *[f"{v / 1e7:,.1f}" for v in close]], True))
    return cash_table(rows_, ["₹ crore", *[f"Year {y}" for y in UYRS]], None, cls="ctab cf")


def ua_headcount():
    deps = [k for k in UMO[0] if k.startswith("Central team: ")]
    yend = lambda y: next(r for r in reversed(UMO) if int(r["Year"]) == y)
    rows_ = [(["Agents", *[f"{float(yend(y)['Agents working']):,.0f}" for y in UYRS]], False),
             (["City managers", *[f"{float(yend(y)['City managers']):,.0f}" for y in UYRS]], False),
             (["Team leads", *[f"{float(yend(y)['Team leads']):,.0f}" for y in UYRS]], False)]
    rows_ += [([(lambda t: t[0].upper() + t[1:])(d.replace("Central team: ", "").replace("hr ", "HR ")), *[f"{float(yend(y)[d]):,.0f}" for y in UYRS]], False) for d in deps if "total" not in d]
    rows_.append((["Central team, total", *[f"{float(yend(y)['Central team, total']):,.0f}" for y in UYRS]], True))
    rows_.append((["Everyone", *[f"{float(yend(y)['Headcount, all (agents, field managers, central)']):,.0f}" for y in UYRS]], True))
    return cash_table(rows_, ["People at year end", *[f"Year {y}" for y in UYRS]], None, cls="ctab hc")


# ---------- assembly ----------
PAGES = []        # (kind, title, takeaway, sources)


def page(no, kicker, title, visual, takeaway="", sources="", kind="story"):
    PAGES.append((kind, title, takeaway, sources))
    total = "A12" if str(no).startswith("A") else str(N_STORY)
    pill = f"{no}" if str(no).startswith("A") else f"{no} / {total}"
    return (f'<section class="slide {kind}"><div class="kick"><span class="pg">{pill}</span>{kicker}</div><h1>{title}</h1>'
            f'<div class="vis">{visual}</div>' + (f'<div class="cap">{takeaway}</div>' if takeaway else "")
            + (f'<div class="src">{sources}</div>' if sources else "") + "</section>")


N_STORY = 25


def build():
    PAGES.clear()
    m60 = lakh(MED60) if READY else "…"
    st = [
        page(1, "Part 1 · Online", f"Online, winning one daily saver costs {inr(ONL_CAC)}.", p_online_cost(),
             f"An app pays {inr(ONL_CAC)} before he saves a rupee.", "Sources: A10. Table: story_unit.csv"),
        page(2, "Part 1 · Online", f"Only {round(ONL_R12 * 100)} in 100 still save a year later.", p_online_keep(),
             "Most app savers stop within months.", "Sources: A10. Tables: story_unit.csv, agent3_survival.csv"),
        page(3, "Part 1 · Online", f"Each saver kept costs {inr(ONL_KEPT)}; the app never earns it back.", p_online_kept(),
             "Online, the numbers do not close.", "Sources: A10. Table: story_unit.csv"),
        page(4, "Part 2 · Our approach", f"The hook: his savings earn about {FUND_RATE} in a debt fund.", p_hook(),
             f"Then an agent at his shop, {VISITS}.", "Sources: A1, A4. Tables: deck_v3_hook.csv, dist_derived_v1.csv"),
        page(5, "Part 2 · Our approach", "A fleet on the street, an app in his hand.", p_approach(),
             "The agent wins him; the app serves him.", "Sources: A1, PR-01."),
        page(6, "Part 2 · Our approach", f"Winning a saver costs {inr(WIN)}, not {inr(ONL_CAC)}.", p_cost_to_win(),
             f"Kept a year, he costs {inr(WIN / ag('r12'))}, not {inr(ONL_KEPT)}.", "Sources: A10, A14. Table: cohort_det_summary.csv"),
        page(7, "Part 2 · Our approach", "How his cash reaches his fund.", p_cash_route(),
             "Every rupee is matched, and confirmed to him the next day.", "Sources: A12 (cash route, cash cover)"),
        page(8, "Part 2 · Our approach", "From day one, a marketplace at no cost to us.", p_marketplace(),
             "Lenders and insurers decide; we list.", "Sources: A3, A7. Table: dist_agreed_v1.csv"),
        page(9, "Part 2 · Our approach", "The agent knows him, so he helps collect.", p_collect(),
             "Collection fees come from bringing late loans back.", "Sources: A8. Tables: dist_derived_v1.csv, dist_agreed_v1.csv"),
        page(10, "Part 3 · Analysis", f"We modelled every monthly cohort, {DRAWS:,} times.", p_cohorts(),
             "One agent, 60 monthly cohorts, every input drawn each time.", "Sources: A1–A4. Table: cohort_mc_summary.csv"),
        page(11, "Part 3 · Analysis", f"{of10(P60).capitalize() if READY else '…'} of 10 futures positive by month 60.", p_fan(),
             f"Median {m60} by month 60.", "Sources: A5, A9. Tables: cohort_mc_cum_fan.csv, cohort_mc_summary.csv"),
        page(12, "Part 3 · Analysis", "Where the money comes from, month by month.", p_money(),
             "Loans and the fund carry it; products add steadily.", "Sources: A6–A9. Table: cohort_det_monthly.csv"),
        page(13, "Part 3 · Analysis", "The longer he saves and repays, the more we earn.", p_by_year(),
             "Lenders see our pool repay, so rates rise each year.", "Sources: A2. Tables: deck_v3_by_year.csv, cohort_det_lending.csv"),
        page(14, "Part 3 · Analysis", "What must be true.", p_must(),
             MUST_TAKE, "Sources: A13. Table: cohort_mc_must_be_true.csv"),
        page(15, "Part 3 · Analysis", f"What could break it: {TOP3[0]}, {TOP3[1]} and {TOP3[2]}.", p_drivers(),
             "The pilot must measure these three first.", "Sources: A2. Table: cohort_mc_drivers.csv"),
        page(16, "Part 3 · Our answer", "Our answer: pilot one salaried agent for 12 months.", p_pilot(),
             HEADLINE, "Sources: A9. Tables: deck_v3_gates.csv, cohort_mc_summary.csv"),
        page(17, "Part 4 · The unicorn track", f"{U_A18:,} agents by month 18, then +{U_STEP} a month to {U_CAP:,}.", u_plan(),
             f"{big_n(uy('Active savers at year end', 5))} savers by month 60; lending stays with partners.", "Sources: A17. Table: unicorn_yearly.csv"),
        page(18, "Part 4 · The unicorn track", f"EBITDA turns positive in year {U_EBITDA_Y}, after peak losses in year {U_WORST_Y}.", u_pnl(),
             f"Year {U_WORST_Y} EBITDA is {cr(uy('EBITDA', U_WORST_Y))}: the price of the speed.", "Sources: A16. Table: unicorn_yearly.csv"),
        page(19, "Part 4 · The unicorn track", f"Cash and the rounds: {len(URD)} raises, {cr(U_RAISED)} in all.", u_cash(),
             "Each round lands before cash falls to six months of burn.", "Sources: A15, A17. Tables: unicorn_monthly.csv, unicorn_rounds.csv"),
        page(20, "Part 4 · The unicorn track", f"Founders keep {pct(U_FOUNDERS, 1)} at the unicorn round.", u_rounds(),
             f"No round dilutes more than {pct(max(float(r[chr(68) + 'ilution (new investors' + chr(39) + ' share of post-money)']) for r in URD))}; ESOP stays near 10%.",
             "Sources: A15. Table: unicorn_rounds.csv"),
        page(21, "Part 4 · The unicorn track", "Unicorn on paper at month 60: both lenses clear $1B.", u_lenses(),
             f"Margins of {float(CHK_R['Margin over $1B (share)']) * 100:.0f}% and {float(CHK_A['Margin over $1B (share)']) * 100:.0f}% over $1B.",
             "Tables: unicorn_milestones.csv, unicorn_mc_summary.csv"),
        page(22, "Part 4 · The unicorn track", "What it takes at year 5.", u_year5(),
             "A national field company, built in five years.", "Table: unicorn_yearly.csv"),
        page(23, "Part 4 · The unicorn track", "The risk: big losses, fast hiring, judgement multiples.", u_risk(),
             "Any one can stop the track.", "Tables: unicorn_yearly.csv, unicorn_mc_summary.csv"),
        page(24, "Part 4 · The unicorn track", "The other road: profitable by year 5, far smaller.", u_other(),
             f"The {OTHER['Agents at m18']}-agent plan raises far less and stays small.", "Tables: growth_frontier.csv, unicorn_yearly.csv"),
        page(25, "Summary", "The plan in one line: prove one agent, then the unicorn track.", u_one_line(),
             f"One agent: {of10(P60)} of 10 futures in profit by month 60.", "Sources: pages 16–24."),
    ]
    assert len(st) == N_STORY
    grid_src = "Table: dist_agreed_v1.csv. Dot: how sure we are."
    ap = [
        page("A1", "Appendix · assumptions", "The saver, the agent, the fund", a_grid1(), "", grid_src, "exempt"),
        page("A2", "Appendix · assumptions", "Loans, cards, collections and growth with history", DP.p_grid2(), "", grid_src, "exempt"),
        page("A3", "Appendix · assumptions (1 of 3)", "Insurance: take-up, premium and commission", DP.p_grid3(), "", grid_src, "exempt"),
        page("A3", "Appendix · assumptions (2 of 3)", "Investments: take-up, ticket and commission", DP.p_grid4(), "", grid_src, "exempt"),
        page("A3", "Appendix · assumptions (3 of 3)", "Payments and other lenders' loans", DP.p_grid5(), "", grid_src, "exempt"),
        page("A4", "Appendix · sources (1 of 2)", "Where each assumption comes from", a_sources(1), "", "Table: dist_agreed_v1.csv", "exempt"),
        page("A4", "Appendix · sources (2 of 2)", "Where each assumption comes from (continued)", a_sources(2), "", "Table: dist_agreed_v1.csv", "exempt"),
        page("A5", "Appendix · the bridge", "From the last deck to this one", a_bridge(), "",
             "Table: cohort_bridge.csv (month-60 P&L, ₹ lakh)", "appx"),
        page("A6", "Appendix · how many loans", "How many loans, and how much money lent", a_loans(), "",
             "Tables: cohort_mc_summary.csv, dist_agreed_v1.csv", "appx"),
        page("A7", "Appendix · cross-sell", f"{len([x for x in XSM if x['key'] not in ('total', 'other_v2')])} products: about ₹{float(next(x for x in XSM if x['key'] == 'total')['p50']):.0f} a saver a year, booked",
             a_xsell(), "", "Tables: cohort_mc_crosssell.csv (median of the draws), deck_v3_housing.csv; interview IV-04", "appx"),
        page("A8", "Appendix · collections", "Collection fees, by how late the loan is", a_collect(), "",
             "Tables: cohort_mc_summary.csv, dist_agreed_v1.csv", "appx"),
        page("A9", "Appendix · year by year", "Year by year for one agent, at the likely values", a_years(), "",
             "Table: cohort_det_monthly.csv", "appx"),
        page("A10", "Appendix · online cost method", f"How we estimate the online cost to win: {inr(ONL_CAC)} a saver", F2.a8(), "",
             "Tables: distributions.csv, story_unit.csv", "appx"),
        page("A11", "Appendix · the one interview", "One janta agent, 15 October 2026", a_interview(), "",
             "Research: the interview notes (identity withheld)", "appx"),
        page("A12", "Appendix · what is left out", "What is left out, and the open questions", a_left_out(), "",
             "Change notes, 16 Oct (rounds 5 and 6)", "appx"),
        page("A13", "Appendix · how many sign-ups", "How many sign-ups a month?", a_signups(), "",
             "Tables: cohort_signups_sweep.csv (a Monte Carlo at each point), cohort_signups_sweep_likely.csv (likely values)", "appx"),
        page("A14", "Appendix · paying the agent", "Paying the agent", a_pay(), "",
             "Table: cohort_incentive_sweep.csv (the base inputs, ways to pay him)", "appx"),
        page("A15", "Appendix · the unicorn track", "Rounds, valuations and the cap table", ua_rounds(), "",
             "Table: unicorn_rounds.csv (valuations are our judgement: lens multiples and step-ups)", "exempt"),
        page("A16", "Appendix · the unicorn track", "The P&L by year, years 1–8 (₹ crore)", ua_ladder(), "", "Table: unicorn_yearly.csv (years 6–8 are context)", "exempt"),
        page("A17", "Appendix · the unicorn track", "The cash-flow statement by year, years 1–8 (₹ crore)", ua_cashflow(), "", "Table: unicorn_monthly.csv, summed by year", "exempt"),
        page("A18", "Appendix · the unicorn track", "Headcount by department, at each year end", ua_headcount(), "", "Table: unicorn_monthly.csv", "exempt"),
        page("A19", "Appendix · the unicorn track", "Company cost assumptions", a_costs(), "",
             "Table: company_gsheet_spec.json (Company inputs; fleet and funding: A15, page 17)", "exempt"),
    ]
    css = V.CSS.replace("INK", INK).replace("MUTED", MUTED).replace("RULE", RULE).replace("US", US) + EXTRA
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Offline model v3</title><style>{css}</style></head>'
            f'<body>{"".join(st)}{"".join(ap)}</body></html>')


EXTRA = f"""
.ctab {{ width: 100%; }}
.ctab table {{ width: 100%; border-collapse: collapse; font-size: 7.6pt; }}
.ctab th {{ text-align: right; color: {MUTED}; font-size: 7.2pt; padding: 2px 6px; border-bottom: 1.5px solid {INK}; }}
.ctab td {{ text-align: right; padding: 1.6px 6px; border-bottom: 1px solid {RULE}; white-space: nowrap; }}
.ctab th:first-child, .ctab td:first-child {{ text-align: left; white-space: normal; }}
.ctab tr.b td {{ font-weight: 700; background: #f6efe7; }}
.ctab.hc table {{ font-size: 11pt; }} .ctab.hc td {{ padding: 4px 10px; }}
.ctab.cf table {{ font-size: 10pt; }} .ctab.cf td {{ padding: 4px 8px; }}
.ccols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: 100%; align-items: start; }}
.ctab.cc table {{ font-size: 7.1pt; }} .ctab.cc td {{ padding: 1.3px 4px; }} .ctab.cc td:nth-child(2) {{ font-weight: 700; }}
.ctab.cc td:nth-child(3) {{ color: {MUTED}; text-align: left; }}
.src {{ margin-top: 4px; }}
.exempt h1, .appx h1 {{ font-size: 20pt; margin-bottom: 8px; }}
.exempt .vis {{ align-items: flex-start; }}
.srct {{ width: 100%; font-size: 8.4pt; }}
.srct table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
.srct th {{ text-align: left; color: {MUTED}; font-size: 7.6pt; text-transform: uppercase; letter-spacing: .04em; padding: 2px 5px; border-bottom: 1.5px solid {INK}; }}
.srct td {{ padding: 2.6px 5px; border-bottom: 1px solid {RULE}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.srct th:nth-child(1), .srct td:nth-child(1) {{ width: 21%; }}
.srct th:nth-child(2), .srct td:nth-child(2) {{ width: 22%; }}
.srct th:nth-child(3), .srct td:nth-child(3) {{ width: 41%; }}
.srct th:nth-child(4), .srct td:nth-child(4) {{ width: 3%; }}
.srct th:nth-child(5), .srct td:nth-child(5) {{ width: 13%; color: {MUTED}; font-size: 7.4pt; }}
.srct .n {{ text-align: left; }} .srct .lh {{ color: {MUTED}; font-weight: 400; }}
.srct td.c svg {{ width: 12px; height: 12px; vertical-align: middle; }}
.srct .lg {{ margin-top: 6px; width: 560px; }}
.ivt {{ width: 100%; font-size: 12.5pt; }}
.ivt table {{ width: 100%; border-collapse: collapse; }}
.ivt th {{ text-align: left; color: {MUTED}; font-size: 9.5pt; text-transform: uppercase; padding: 4px 8px; border-bottom: 1.5px solid {INK}; }}
.ivt td {{ padding: 7px 8px; border-bottom: 1px solid {RULE}; }}
"""


# ---------- the word budget ----------
WORD = lambda t: [w for w in t.split() if re.search(r"\w", w)]


def check_words(pdf):
    code = ("import sys, json; sys.path.insert(0, sys.argv[2]); import pypdfium2 as p; d = p.PdfDocument(sys.argv[1]); "
            "print(json.dumps([d[i].get_textpage().get_text_range() for i in range(len(d))]))")
    out = subprocess.run([SYS_PY, "-c", code, str(pdf), str(LIB)], check=True, capture_output=True, text=True).stdout
    texts = json.loads(out)
    assert len(texts) == len(PAGES), f"{len(texts)} PDF pages vs {len(PAGES)} built"
    fails, table = [], []
    for k, (txt, (kind, title, take, src)) in enumerate(zip(texts, PAGES), 1):
        n, nt, nk, ns = len(WORD(txt)), len(WORD(title)), len(WORD(html.unescape(re.sub("<[^>]+>", " ", take)))), len(WORD(src))
        cap = {"story": 70, "appx": 150, "exempt": None}[kind]
        ok = (cap is None or n <= cap) and (kind != "story" or (nt <= 12 and nk <= 14 and ns <= 15))
        table.append((k, kind, n, nt, nk, ns, "OK" if ok else "OVER"))
        if not ok:
            fails.append(k)
    print(f"{'page':>4} {'kind':<7} {'words':>5} {'title':>5} {'take':>5} {'src':>4}")
    for r in table:
        print(f"{r[0]:>4} {r[1]:<7} {r[2]:>5} {r[3]:>5} {r[4]:>5} {r[5]:>4}  {r[6]}")
    for bad in ("Bueno", "BetterPlace", "Arvinder", "Singh", "Bareilly", "PNB", "Rs ", "r12", "_r0.", "NPV", "discount", "Discount"):
        for k, txt in enumerate(texts, 1):
            assert bad not in txt, (bad, k)
    return table, fails


def main():
    if not READY:
        print("PREVIEW: cumulative P&L not ready (" + "; ".join(MISSING) + "): metric pages are stubs")
    doc = build()
    OUT.mkdir(parents=True, exist_ok=True)
    src = OUT / "deck_v3.html"
    src.write_text(doc)
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", src.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {src}\nwrote {PDF}\ntables read: {', '.join(sorted(USED))}")
    _, fails = check_words(PDF)
    if fails:
        raise SystemExit(f"word budget broken on pages {fails}")


if __name__ == "__main__":
    main()

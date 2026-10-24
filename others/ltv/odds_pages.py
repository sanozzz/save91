"""The main-case pages shared by the one-saver LTV/CAC deck (ltv/build_ltv_simple.py), the business case
(online/build_online_case.py) and the v4 plan deck (online/build_online_v4.py). Rebased 24 Oct 2026; round 2 applies the merged
review fixes (reviews/2026-10-24_rebase/FIXES.md): serving carries the 10% contingency, one retention line everywhere, the
ladder's ends move retention only, 3x is reachable, the cost to win is the founders' figure (not "measured").

Two inputs are still drawn (model/ltv_odds.py): still saving at 12 months (Bachatt's 30-40%) and the debt fund's fee. Everything
else is fixed by the founders (market figures, Bachatt, or our judgement). The Monte Carlo median is the main case, the ONLY case.
"What it takes" moves five upside levers together from the main case; it is never an alternative plan.

Pages (each returns (kicker, title, body, source); the deck puts it in its own page frame):
  p_odds()           what is still uncertain: 1,000 draws at 5 and 8 years
  p_upside_levers()  what it takes, one lever at a time
  p_ladder()         what it takes, the ladder: the main case with its 30-40% band, then 1x, 2x, 3x, and the company at each
  p_company()        the company at the main case, as pictures (the one-saver deck's appendix)
  p_financials()     the company at the main case, year by year (the business case and the v4 deck)
  p_prove()          the four facts that decide it, and what each is worth
Numbers: tables/ltv_odds_*.csv, ltv_ladder*.csv, ltv_saver_split.csv, ltv_upside_levers.csv, ltv_main_levers.csv,
online_ltv_levers.csv (model/ltv_odds.py and model/online_plan.py under use_main_case()). Never retyped: read here."""
import re
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pandas as pd

import build_ltv_deck as ld
import ltv_odds as lo

op, sp = ld.op, ld.sp
T, R, svg, chips, two, table = ld.T, ld.R, ld.svg, ld.chips, ld.two, ld.table
INK, NAVY, TEAL, AMBER, SLATE, LINE, LATE, MUTE = ld.INK, ld.NAVY, ld.TEAL, ld.AMBER, ld.SLATE, ld.LINE, ld.LATE, ld.MUTE
NAVY2, NAVY3, NAVY4, RED = ld.NAVY2, ld.NAVY3, ld.NAVY4, ld.RED
rs, pct = ld.rs, ld.pct
MID = "#9fb3c8"
BAND = "#cfdcec"
TAB = ld.TAB


def x(v):
    """LTV/CAC to two decimals (founders 24 Oct), with a true minus."""
    return f"{float(v):.2f}×".replace("-", "−")


def usd(v):
    """$M to one decimal, rounding half up (8.25 -> $8.3M)."""
    return f"${Decimal(str(round(float(v), 2))).quantize(Decimal('0.1'), ROUND_HALF_UP)}M"


def month(m):
    m = int(float(m))
    return f"month {m}" if m <= 96 else "not by month 96"


def cr(v):
    """₹ crore: two decimals below 10, none above (founders 24 Oct)."""
    v = float(v)
    s = "−" if v < -0.005 else ""
    return f"{s}₹{abs(v):,.0f} Cr" if abs(v) >= 10 else f"{s}₹{abs(v):.2f} Cr"


def crn(v):
    """A ₹ crore number for a chart or table cell: two decimals below 10, one above."""
    v = float(v)
    s = "−" if v < -0.005 else ""
    return f"{s}{abs(v):.1f}" if abs(v) >= 10 else f"{s}{abs(v):.2f}"


def halo(t, w=4):
    """White outline behind an svg text so it reads over a line or a bar."""
    return t.replace("<text ", f'<text paint-order="stroke" stroke="white" stroke-width="{w}" stroke-linejoin="round" ', 1)


def rng(a, b):
    """An LTV/CAC range, two decimals: 0.60–0.93×."""
    return f"{float(a):.2f}–{float(b):.2f}×"


def lakh(v):
    return f"₹{v / 1e5:g} lakh" if v >= 1e5 else f"₹{v / 1e3:g}k"


def share(v):
    """A share of the 1,000 draws: one decimal below 1%, none above."""
    v = float(v)
    return f"{v:.1%}" if 0 < v < 0.01 else f"{v:.0%}"


def wrap(s, n):
    out, line = [], ""
    for w in str(s).split():
        if line and len(line) + 1 + len(w) > n:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    return out + ([line] if line else [])


def plainrs(s):
    return re.sub(r"\bRs\.?\s?(?=\d)", "₹", str(s))


# plain words at first use (FIXES B11)
GLOSS = {"ltv": "what a saver brings in over 5 or 8 years, less the cost of serving them, divided by what it costs to win them",
         "ebitda": "operating profit before interest, tax and depreciation",
         "kyc": "KYC'd: finished the identity check", "sip": "SIP: a regular instalment into a mutual fund",
         "mandate": "mandate: the saver's standing instruction to their bank to pay the daily amount",
         "mc": "we ran the model 1,000 times, picking retention and the debt fund's fee at random within their ranges",
         "median": "the median is the middle draw; 8 in 10 draws fall between the 10th and 90th percentiles"}


# ---------------------------------------------------------------------------------------------------------- the tables
DRAWS = pd.read_csv(TAB / "ltv_odds_draws.csv")
SUMM = pd.read_csv(TAB / "ltv_odds_summary.csv").set_index("measure")
DRV = pd.read_csv(TAB / "ltv_odds_drivers.csv").set_index("input")
LAD = pd.read_csv(TAB / "ltv_ladder.csv").set_index("rung")
LADY = pd.read_csv(TAB / "ltv_ladder_yearly.csv")
SPLIT = pd.read_csv(TAB / "ltv_saver_split.csv").set_index(["case", "years"])
UPL = pd.read_csv(TAB / "ltv_upside_levers.csv").set_index("lever")
BRIDGE = pd.read_csv(TAB / "ltv_bridge.csv")
LEVM = pd.read_csv(TAB / "ltv_main_levers.csv").set_index("case")
LTVL = pd.read_csv(TAB / "online_ltv_levers.csv").set_index("case")
FUN = pd.read_csv(TAB / "ltv_main_funnel.csv").set_index("stage")
FRONT = pd.read_csv(TAB / "online_frontier.csv").set_index("online savers won a month (m30 on)")

MAIN, LOW, HIGH = LAD.loc["Main case"], LAD.loc["Low end (30% still saving)"], LAD.loc["High end (40% still saving)"]
R1, R2, TOP = LAD.loc["1×"], LAD.loc["2×"], LAD.loc["All upside"]
R3 = LAD.loc["3×"] if "3×" in LAD.index else None
T_MAIN = float(MAIN["drawn position (0 low, 1 high)"])
S5, S8 = SPLIT.loc[("Main case", "5y")], SPLIT.loc[("Main case", "8y")]
L, L8 = DRAWS["ltv_cac"], DRAWS["ltv_cac_96"]
MED, MED8 = float(MAIN["LTV/CAC 5y"]), float(MAIN["LTV/CAC 8y"])
XMED, XMED8 = x(MED), x(MED8)
P1, P1_8 = float((L >= 1).mean()), float((L8 >= 1).mean())
P2, P3 = float((L >= 2).mean()), float((L >= 3).mean())
CAC = op.CAC * (1 + op.CONTINGENCY)
PAY = int(MAIN["saver pays back in month"])
N_DRAWS = len(DRAWS)


def q(measure, p):
    return float(SUMM.loc[measure, p])


Q5 = (q("LTV/CAC, 5 years", "P10"), q("LTV/CAC, 5 years", "P90"))
Q8 = (q("LTV/CAC, 8 years", "P10"), q("LTV/CAC, 8 years", "P90"))
QM = (q("Money needed, $M", "P10"), q("Money needed, $M", "P90"))
QP = (q("Saver pays back in month (97 = not by 96)", "P10"), q("Saver pays back in month (97 = not by 96)", "P90"))
NO_PROFIT = q("chance EBITDA positive by month 96", "P50") == 0.0


def ltvl(case):
    """5-year LTV/CAC of a one-change-at-a-time row of the main case's saver (online_ltv_levers.csv; its own two-decimal column, so a
    rupee figure rounded in the table is not rounded twice)."""
    return float(LTVL.loc[case, "LTV/CAC 60m"])


def ltvl8(case):
    return float(LTVL.loc[case, "LTV/CAC 96m"])


def levm(case):
    """(EBITDA positive month or None, money needed $M) of a one-change-at-a-time row of the company (ltv_main_levers.csv)."""
    r = LEVM.loc[case]
    m = r["EBITDA positive from month"]
    return (int(m) if str(m).isdigit() else None), float(r["money needed $M"])


def levm_usd(case):
    """Money needed for a lever row, '+' when the company is still losing money at month 96 (it needs at least this)."""
    pm, m = levm(case)
    return usd(m) + ("" if pm else "+")


def floor_usd(r):
    """Money needed of a ladder row; '+' when EBITDA is still negative at month 96 (the company needs at least this)."""
    return usd(r["money needed $M"]) + ("+" if int(float(r["EBITDA positive from month"])) > 96 else "")


def alone(k, tag="1x"):
    """The value one upside lever needs alone for 1x (or 2x), as a number (None if not reachable)."""
    s = str(UPL.loc[k, f"alone for {tag} (5y)"])
    m = re.search(r"\s([0-9.]+)", s)                      # "r12 0.4045" -> 0.4045
    return None if "not reachable" in s or not m else float(m.group(1))


def run_on(months=180):
    """The main-case company run on past month 96 (FIXES B8): the year the cash hole bottoms and the money needed then. The model's
    own company(), with its horizon lengthened for this one run and every module setting restored afterwards."""
    keep_m, keep_main = op.M, dict(op.MAIN)
    try:
        op.use_main_case()
        op.M = months
        op._CACHE.clear()
        o = op.company(lo.LEVEL, 1.0)
        cum = np.cumsum(o["cash_flow"])
        i = int(np.argmin(cum))
        return i // 12 + 1, (max(0.0, -float(cum.min())) + 5 * op.CR) / op.FX / 1e6
    finally:
        op.M = keep_m
        op.MAIN.clear()
        op.MAIN.update(keep_main)
        op._CACHE.clear()


RUN_YEAR, RUN_USD = run_on()

# the tables against each other and against the live model, so a stale table cannot reach a page
assert abs(MED - float(L.median())) < 0.01, (MED, float(L.median()))
assert abs(float(S5["LTV/CAC"]) - MED) < 0.001 and abs(float(S8["LTV/CAC"]) - MED8) < 0.01, (S5["LTV/CAC"], S8["LTV/CAC"])
assert abs(lo.saver(lo.at(T_MAIN))["ltv_cac"] - MED) < 0.005, "tables/ltv_ladder.csv is stale against model/ltv_odds.py"
assert abs(float(BRIDGE["LTV/CAC 5y"].iloc[-1]) - MED) < 0.005, BRIDGE.iloc[-1]
assert abs(ltvl("The plan") - MED) < 0.01 and abs(levm("The main case")[1] - float(MAIN["money needed $M"])) < 0.1
assert abs(CAC - float(S5["cost to win"])) < 0.5
assert abs(float(DRV.loc["keep", "median if low"]) - float(LOW["LTV/CAC 5y"])) < 0.01, "the ladder's ends should move retention only"
assert RUN_USD >= float(MAIN["money needed $M"]) - 0.05, (RUN_USD, MAIN["money needed $M"])

MAIN_IN = lo.overrides(lo.at(T_MAIN))
X = op.saver_inputs()
DEBT_MAIN = MAIN_IN["_debt_trail"]
FEE_MAIN = 0.8 * op.EQ_TRAIL + 0.2 * DEBT_MAIN

MONEY_NOTE = (f"Money needed = the seed + the deepest cash hole (fees arrive 2 months after they are earned) + a ₹5 crore cash buffer, at "
              f"₹{op.FX:.0f} = $1; + means the company is still losing money at month 96, so it needs at least this (if run on, the cash hole "
              f"bottoms around year {RUN_YEAR} at about {usd(RUN_USD)}).")
CAC_WORDS = (f"₹{op.CAC:.0f} at scale (the founders' figure; they call it 'fairly sorted') plus the 10% contingency = {rs(CAC)}. The seed budgets "
             f"₹{op.SEED_CAC:.0f} while the brand is new, and measures it")

# where each input comes from (founders 24 Oct; FIXES B), shared by the decks' input pages
SOURCE = {"daily": "our product's floor; Bachatt's average is unknown, and its own minimums are lower (₹51/₹101 a day; ₹20 for its liquid fund)",
          "keep": "Bachatt's own 30–40%; SBI MF's ₹250 daily SIP keeps about 38%",
          "trail": "a liquid fund (0.10%) to a short-duration fund (0.35%)",
          "eq_trail": "active equity funds; not yet confirmed in writing",
          "debit": "BSE StAR MF's exchange SIP is free to distributors and fund houses pay BSE; not yet confirmed in writing",
          "ticket": "Bachatt's number; our own research had ₹15k–58.5k",
          "apply": "the founders' market figure",
          "approved": "the founders' market figure, between 11% (an app lender's new applicants) and 25% (our own past data)",
          "repeat": "an app lender approves 74% of repeat borrowers", "rises": "no source found, so none",
          "home_lap": "market sizes: affordable home loans ₹6–15 lakh, small property loans about ₹3.9 lakh",
          "payout": "the middle of the market's 1–3%",
          "reach": "about 2.5 KYC'd people come with each saver, but non-savers fade within ~3 months: lenders rarely approve users that new",
          "products": "not in the launch app",
          "cac": CAC_WORDS}


def val(k, t=None):
    """An input in words at the main case. The two drawn inputs ('keep', 'trail') take a position t (0 low end, 1 high end);
    the inputs the founders fixed on 24 Oct ignore t."""
    t = T_MAIN if t is None else t
    if k in lo.INPUTS:
        v = lo.drawn({**lo.at(T_MAIN), k: t})
        if k == "keep":
            return f"{v['r12']:.0%}, then {v['churn_late']:.1%} stop a month"
        return pct(v["_debt_trail"], 2)
    fixed = {"daily": f"₹{X['daily']:.0f} a day", "ticket": f"{lakh(X['ticket'])} first loans", "apply": pct(op.LOAN_APPLY),
             "approved": pct(X["approved_first"]), "repeat": pct(X["approved_repeat"]), "rises": "none",
             "reach": f"{op.LOAN_REACH:.2f} per saver", "home_lap": f"{lakh(X['loan_home_ticket'])} / {lakh(X['loan_lap_ticket'])}",
             "payout": f"{pct(X['fee'])}, flat", "eq_trail": pct(op.EQ_TRAIL, 2), "debit": f"₹{op.DEBIT_COST:.0f}",
             "blend": pct(FEE_MAIN, 2)}
    return fixed[k]


# ---------------------------------------------------------------------------------------------------------- the odds
def hist_svg(series, lo_, hi_, step, ticks, head, right, qq, W=560, H=310):
    top, bot, x0, x1_ = 52, H - 70, 46, W - 6
    edges = np.arange(lo_, hi_ + step / 2, step)
    cnt, _ = np.histogram(np.clip(series, lo_, hi_ - 1e-9), bins=edges)
    frac = cnt / len(series)
    ymax = max(0.05, float(np.ceil(frac.max() * 20) / 20))             # the next 5% step above the tallest bar
    X_ = lambda v: x0 + (x1_ - x0) * (v - lo_) / (hi_ - lo_)
    Y = lambda f: bot - (bot - top) * f / ymax
    med = float(np.median(series))
    good = float(np.mean(series >= 1))
    out = [T(0, 16, head, 13, 800, NAVY, ls=1.1), T(W, 16, right, 14, 800, TEAL if good >= 0.5 else LATE, "end")]
    for f in np.arange(0, ymax + 1e-9, 0.05):
        out.append(f'<line x1="{x0}" y1="{Y(f):.1f}" x2="{x1_}" y2="{Y(f):.1f}" stroke="{LINE}" stroke-width="0.8"/>')
        out.append(T(x0 - 5, Y(f) + 4, f"{f:.0%}", 10.5, 600, MUTE, "end"))
    out.append(f'<text x="11" y="{(top + bot) / 2:.0f}" font-size="10.5" font-weight="700" fill="{SLATE}" text-anchor="middle" '
               f'transform="rotate(-90 11 {(top + bot) / 2:.0f})">share of 1,000 draws</text>')
    for i, f in enumerate(frac):
        col = TEAL if edges[i] >= 1 - 1e-9 else LATE
        out.append(R(X_(edges[i]) + 1, Y(f), X_(edges[i + 1]) - X_(edges[i]) - 2, bot - Y(f), col, r=2))
    out.append(f'<line x1="{x0}" y1="{bot}" x2="{x1_}" y2="{bot}" stroke="{INK}" stroke-width="1.2"/>')
    for v in ticks:
        out.append(T(X_(v), bot + 17, f"{v:g}×", 11.5, 600, SLATE, "middle"))
    xm, xo = X_(med), X_(1.0)
    out.append(f'<line x1="{xo:.1f}" y1="{top - 10}" x2="{xo:.1f}" y2="{bot}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="5 4"/>')
    lab_right = xo < W - 150
    out.append(halo(T(xo + (6 if lab_right else -6), top - 2, "1×: pays back the ₹495", 11.5, 700, RED, "start" if lab_right else "end")))
    out.append(f'<line x1="{xm:.1f}" y1="{top + 8}" x2="{xm:.1f}" y2="{bot}" stroke="{NAVY}" stroke-width="2.4"/>')
    out.append(halo(T(xm + 6, top + 20, f"main case {x(med)}", 13, 800, NAVY)))
    a, b = X_(qq[0]), X_(qq[1])
    yb = bot + 34
    out.append(f'<path d="M{a:.1f} {yb - 5} L{a:.1f} {yb} L{b:.1f} {yb} L{b:.1f} {yb - 5}" fill="none" stroke="{NAVY4}" stroke-width="1.6"/>')
    out.append(T((a + b) / 2, yb + 17, f"8 in 10 draws: {rng(*qq)}", 12, 700, NAVY4, "middle"))
    return svg(W, H, "".join(out))


def p_odds():
    k5, kt = DRV.loc["keep"], DRV.loc["trail"]
    left = hist_svg(L, 0.55, 1.05, 0.025, (0.6, 0.7, 0.8, 0.9, 1.0), "AFTER 5 YEARS", f"{share(P1)} of the draws reach 1×", Q5)
    right = hist_svg(L8, 0.85, 2.0, 0.05, (1.0, 1.2, 1.4, 1.6, 1.8, 2.0), "AFTER 8 YEARS", f"{share(P1_8)} reach 1×", Q8)
    body = two(left, right, 560) + chips([
        ("Two inputs are still uncertain", "Still saving at 12 months (Bachatt's 30–40%) and the debt fund's fee (0.10–0.35%). Everything else "
                                           "is fixed by the founders: market figures, Bachatt, or our judgement."),
        ("Retention decides it", f"At 30% still saving the median is {x(k5['median if low'])}; at 40%, {x(k5['median if high'])}. The debt fund's fee "
                                 f"moves it only from {x(kt['median if low'])} to {x(kt['median if high'])}. In 8 in 10 draws a saver pays back from "
                                 f"{month(QP[0])} to {month(QP[1])}."),
        ("The company, in every draw", ("EBITDA is not positive by month 96 in any of the 1,000 draws. " if NO_PROFIT else "")
         + f"8 in 10 draws need {usd(QM[0])}+ to {usd(QM[1])}+: the company is still losing money at month 96.")])
    title = f"What's still uncertain is mostly how long savers keep saving: {rng(*Q5)} at 5 years, {rng(*Q8)} at 8 (8 in 10 draws)"
    return ("WHAT'S UNCERTAIN", title, body,
            f"The Monte Carlo: {GLOSS['mc']}. {share(P1)} of the 1,000 draws reach 1× in 5 years, holding everything else at the main case "
            f"(cost to win {rs(CAC)}). The main case is the median draw; 8 in 10 draws fall between the 10th and 90th percentiles. Undiscounted.")


# ---------------------------------------------------------------------------------------------------------- what it takes
LEVER_TXT = {   # lever -> (name, main case -> upside, what it needs alone for 1x)
    "daily": ("Average saved a day", lambda: f"₹{X['daily']:.0f} (our product's floor) → ₹200",
              lambda v: f"₹{v:.0f} a day"),
    "keep_up": ("Still saving at 12 months", lambda: f"{MAIN_IN['r12']:.0%} → 45%, the drop-off after a year {MAIN_IN['churn_late']:.1%} → 1.0% a month",
                lambda v: f"{v:.1%} still saving"),
    "apply": ("Apply for a loan, a year", lambda: f"{pct(op.LOAN_APPLY)} (market) → 35% (our old target)",
              lambda v: f"{v:.0%} applying, beyond our old 35%"),
    "approved": ("First loans approved", lambda: f"{pct(X['approved_first'])} (market) → 30% (our old target)", None),
    "rises": ("Yearly rises in take-up and approval", lambda: "none → +5% and +10% a year (our old targets)", None)}


def levers_svg(W=1152):
    rows = sorted(UPL.index, key=lambda k: -float(UPL.loc[k, "LTV/CAC 5y at the upside alone"]))
    x0, x1_, top, rh = 430, 880, 1.8, 56
    X_ = lambda v: x0 + (x1_ - x0) * min(v, top) / top
    out = [T(0, 14, "THE LEVER: MAIN CASE → ITS UPSIDE", 11, 700, SLATE, ls=1),
           T(x0, 14, f"LTV/CAC, 5 YEARS, FROM THE MAIN CASE'S {XMED}", 11, 700, SLATE, ls=1), T(W, 14, "ALONE FOR 1×", 11, 700, SLATE, "end", ls=1),
           f'<line x1="{X_(1):.1f}" y1="24" x2="{X_(1):.1f}" y2="{30 + len(rows) * rh}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="5 4"/>']
    y = 30
    for k in rows:
        nm, sub, need = LEVER_TXT[k]
        v = float(UPL.loc[k, "LTV/CAC 5y at the upside alone"])
        a1 = alone(k)
        out.append(T(0, y + 20, nm, 15, 800, NAVY) + T(0, y + 39, sub(), 11.5, 500, SLATE))
        out.append(R(x0, y + 10, X_(MED) - x0, 26, "#d5dde8", r=5))
        out.append(R(X_(MED), y + 10, max(X_(v) - X_(MED), 3), 26, TEAL if v >= 1 else NAVY4, r=5))
        out.append(halo(T(X_(v) + 10, y + 29, x(v), 16, 800, TEAL if v >= 1 else NAVY4)))
        if a1 is None or need is None:
            txt, col = "can't reach 1× alone", LATE
        else:
            txt, col = need(a1), (TEAL if "beyond" not in need(a1) else AMBER)
        out.append(T(W, y + 29, txt, 13.5, 800, col, "end"))
        y += rh
    out.append(T(X_(1), y + 15, "1×", 12, 800, RED, "middle"))
    for v in (0.5, 1.5):
        out.append(T(X_(v), y + 15, f"{v:g}×", 11, 600, MUTE, "middle"))
    return svg(W, y + 22, "".join(out))


def p_upside_levers():
    d1, k1 = alone("daily"), alone("keep_up")
    old5 = ltvl("Loan funnel at our old targets")
    old_pm, old_m = levm("Loan funnel at our old targets")
    body = levers_svg() + chips([
        ("A bigger daily amount", f"Fund fees are paid on the balance, so the daily amount moves LTV/CAC most: ₹{d1:.0f} a day pays back the "
                                  f"₹495 in 5 years; ₹200 gives {x(UPL.loc['daily', 'LTV/CAC 5y at the upside alone'])}."),
        ("Longer saving", f"{k1:.1%} still saving at 12 months gives 1× on its own; 45%, the credit hook we hope for (with 1.0% a month stopping after), "
                          f"{x(UPL.loc['keep_up', 'LTV/CAC 5y at the upside alone'])}."),
        ("What cross-selling can do", f"No single loan number reaches 1×. All three at our old targets together give about {x(old5)} and bring "
                                      f"profit in {month(old_pm) if old_pm else 'not by month 96'}: loan fees arrive early, fund fees build slowly.")])
    title = (f"What it takes, one lever at a time: ₹{d1:.0f} a day or {k1:.1%} still saving takes a saver to 1×; "
             "no loan number does on its own")
    return ("WHAT IT TAKES: ONE LEVER AT A TIME", title, body,
            "Each row: one lever at its upside, everything else at the main case. Upside: ₹200 a day; 45% still saving; our old loan targets "
            "(applying 35%, approval 30%, take-up +5% and approval +10% a year). Alone for 1×: the value that lever needs on its own for a 5-year "
            f"LTV/CAC of 1× (cost to win {rs(CAC)}). Our old loan targets together: the company needs {levm_usd('Loan funnel at our old targets')}.")


RUNGS = [("Main case", "main case"), ("1×", ""), ("2×", ""), ("3×", "")]


def rises(r):
    a, b = float(r["take-up rise a year"]), float(r["approval rise a year"])
    if a == 0 and b == 0:
        return "none"
    f = lambda v: f"+{v * 100:.1f}".rstrip("0").rstrip(".") + "%"
    return f"{f(a)} / {f(b)}"


def ladder_svg(W=1152):
    rows = [(k, LAD.loc[k], nm) for k, nm in RUNGS if k in LAD.index]
    bx0, bx1, bmx = 96, 240, 3.2
    BX = lambda v: bx0 + (bx1 - bx0) * min(float(v), bmx) / bmx
    cols = [(272, "₹ A DAY"), (362, "STILL SAVING"), (488, "APPLY A YEAR"), (596, "APPROVED"), (680, "YEARLY RISES"),
            (818, "8 YEARS"), (922, "EBITDA POSITIVE"), (W, "MONEY NEEDED")]
    rh = 64
    out = [T(0, 14, "LTV/CAC, 5 YEARS", 10.5, 700, SLATE, ls=1)]
    out += [T(cx, 14, h, 10.5, 700, SLATE, "end" if cx == W else "start", ls=1) for cx, h in cols]
    y = 26
    for k, r, nm in rows:
        main = k == "Main case"
        if main:
            out.append(R(-8, y, W + 16, rh - 6, sp.NAVY_L, r=8))
        lv = float(r["LTV/CAC 5y"])
        col = NAVY if main else TEAL
        out.append(T(0, y + 30, x(lv), 22, 800, col))
        out.append(f'<line x1="{bx0}" y1="{y + 24}" x2="{bx1}" y2="{y + 24}" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
        if main:
            out.append(R(BX(LOW["LTV/CAC 5y"]), y + 17, BX(HIGH["LTV/CAC 5y"]) - BX(LOW["LTV/CAC 5y"]), 14, BAND, r=4))
            out.append(T(0, y + 48, f"{rng(LOW['LTV/CAC 5y'], HIGH['LTV/CAC 5y'])} at 30–40% still saving", 11, 700, NAVY4))
        out.append(f'<circle cx="{BX(lv):.1f}" cy="{y + 24}" r="6" fill="{col}"/>')
        out.append(f'<line x1="{BX(1):.1f}" y1="{y + 14}" x2="{BX(1):.1f}" y2="{y + 34}" stroke="{RED}" stroke-width="1.2"/>')
        keep = f"{float(r['still saving at 12 months']):.0%}" + (" (30–40%)" if main else "")
        vals = [(f"₹{float(r['saved a day Rs']):.0f}", float(r["saved a day Rs"]) != float(MAIN["saved a day Rs"])),
                (keep, abs(float(r["still saving at 12 months"]) - float(MAIN["still saving at 12 months"])) > 0.004),
                (f"{float(r['apply a year']):.0%}", abs(float(r["apply a year"]) - float(MAIN["apply a year"])) > 0.004),
                (f"{float(r['first loans approved']):.0%}", abs(float(r["first loans approved"]) - float(MAIN["first loans approved"])) > 0.004),
                (rises(r), rises(r) != rises(MAIN))]
        for (cx, _h), (v, moved) in zip(cols[:5], vals):
            out.append(T(cx, y + 30, v, 15, 800 if moved else 600, TEAL if moved else NAVY))
        out.append(T(cols[5][0], y + 30, x(r["LTV/CAC 8y"]), 15, 700, NAVY if main else INK))
        pm = int(float(r["EBITDA positive from month"]))
        out.append(T(cols[6][0], y + 30, month(pm), 15, 800, TEAL if pm <= 96 else LATE))
        out.append(T(W - 4, y + 30, floor_usd(r), 15, 800, NAVY if main else INK, "end"))
        if main:
            out.append(T(W - 4, y + 48, f"{usd(HIGH['money needed $M'])}+ to {usd(LOW['money needed $M'])}+ at 40–30%", 11, 700, NAVY4, "end"))
        y += rh
    return svg(W, y + 2, "".join(out))


def p_ladder():
    top = TOP
    body = ladder_svg() + chips([
        ("One company, one main case", f"Every row is the same company: {lo.LEVEL:,} online savers a month from month 30, the same team and cost to win. "
                                       "The rows say what would have to be true, not a second plan."),
        ("Five levers move together", "From the main case towards the upside: ₹100 → ₹200 a day, still saving → 45%, applying 20% → 35%, approval "
                                      "20% → 30%, yearly rises none → +5% / +10%. Teal: a lever above the main case."),
        ("Every lever at its upside", f"{x(top['LTV/CAC 5y'])}: the company turns positive in {month(top['EBITDA positive from month'])} on "
                                      f"{floor_usd(top)}.")])
    r3 = R3 if R3 is not None else TOP
    title = (f"What it takes: 2× needs ₹{float(R2['saved a day Rs']):.0f} a day and {float(R2['still saving at 12 months']):.0%} still saving, with loans most "
             f"of the way to our old targets, for profit from {month(R2['EBITDA positive from month'])}; 3× needs ₹{float(r3['saved a day Rs']):.0f} a day "
             f"and {float(r3['still saving at 12 months']):.0%}")
    return ("WHAT IT TAKES: THE COMPANY AT EACH LTV/CAC", title, body,
            "Band: the main case with still saving anywhere in Bachatt's 30–40%, every other input held. EBITDA: "
            f"{GLOSS['ebitda']}. {MONEY_NOTE} Doorstep savers (1 in 10) carry the same levers. Undiscounted.")


# ---------------------------------------------------------------------------------------------------------- the company
def main_years():
    return LADY[LADY["rung"] == "Main case"].sort_values("year")


def ebitda_svg(y_, W=600, H=250, total=True):
    vals = [float(v) for v in y_["EBITDA Rs cr"]]
    cum = np.cumsum(vals)
    up = max(max(vals), 0.0)
    dn = max(-min(vals), 0.0)
    room = H - 46 - (64 if total else 22)                     # header and year labels above, value labels and the cumulative row below
    sc = room / max(up + dn, 1e-9)
    base = 46 + up * sc + (16 if up > 0 else 0)
    gw = (W - 40) / 8
    out = [T(0, 14, "EBITDA (OPERATING PROFIT) BY YEAR, ₹ CRORE", 11, 700, SLATE, ls=1),
           f'<line x1="30" y1="{base:.1f}" x2="{W}" y2="{base:.1f}" stroke="{INK}" stroke-width="1.2"/>']
    for i, v in enumerate(vals):
        xx = 40 + i * gw
        h = v * sc
        out.append(R(xx, base - max(h, 0), gw - 18, max(abs(h), 1.5), TEAL if v >= 0 else LATE, r=3))
        out.append(T(xx + (gw - 18) / 2, base - h + 16 if v < 0 else base - h - 6, crn(v), 12, 800, TEAL if v >= 0 else LATE, "middle"))
        out.append(T(xx + (gw - 18) / 2, base - 8 if v < 0 else base + 16, f"Y{i + 1}", 11.5, 700, SLATE, "middle"))
        if total:
            out.append(T(xx + (gw - 18) / 2, H - 4, crn(cum[i]), 11.5, 700, NAVY, "middle"))
    if total:
        out.append(f'<line x1="30" y1="{H - 22}" x2="{W}" y2="{H - 22}" stroke="{LINE}"/>')
        out.append(T(0, H - 4, "Total", 11, 700, NAVY))
        out.append(T(W, H - 28, "CUMULATIVE EBITDA AT EACH YEAR END", 10, 700, NAVY, "end", ls=1))
    return svg(W, H, "".join(out))


def tiles(items, size=30, pad=11, gap=10):
    return "".join(f'<div style="background:{sp.BG};border:1px solid {LINE};border-radius:12px;padding:{pad}px 16px;margin-bottom:{gap}px">'
                   f'<div style="font-size:{size}px;font-weight:800;color:{c};letter-spacing:-.01em;line-height:1.1">{a}</div>'
                   f'<div style="font-size:12px;color:{SLATE};line-height:1.33;margin-top:2px">{b}</div></div>' for a, b, c in items)


def company_tiles(m=MAIN, y_=None):
    y_ = main_years() if y_ is None else y_
    y8 = float(y_["EBITDA Rs cr"].iloc[-1])
    return [("Not by month 96" if int(float(m["EBITDA positive from month"])) > 96 else month(m["EBITDA positive from month"]).capitalize(),
             f"EBITDA is still {cr(y8)} in year 8: the company does not turn profitable within 8 years.", LATE),
            (f"At least {usd(m['money needed $M'])}", f"money needed in all, seed included; still rising at month 96 (if run on, it bottoms "
                                                      f"around year {RUN_YEAR} at about {usd(RUN_USD)}).", NAVY),
            (cr(m["cumulative EBITDA 8y Rs cr"]), "EBITDA added up over 8 years, undiscounted.", NAVY)]


def frontier_line():
    lv = [10000, 20000, 40000, 80000]
    plus = lambda v: "+" if not str(FRONT.loc[v, "EBITDA positive from month"]).isdigit() else ""
    return ", ".join(f"{v // 1000}k a month {usd(FRONT.loc[v, 'money needed $M'])}{plus(v)}" for v in lv)


def p_company():
    y_ = main_years()
    m200 = levm("Rs 200 a day")
    body = two(ebitda_svg(y_, 600, 290), tiles(company_tiles(y_=y_)), 600) + chips([
        ("Why growing faster doesn't help", f"Each saver costs {rs(CAC)} and earns back {rs(float(S5['net']))} in 5 years, so more savers mean a deeper hole: "
                                            f"{frontier_line()}."),
        ("What would change it", f"₹200 a day: profit from {month(m200[0]) if m200[0] else 'not by month 96'} on {usd(m200[1])}. 2× (₹{float(R2['saved a day Rs']):.0f} a day, "
                                 f"{float(R2['still saving at 12 months']):.0%} still saving, loans most of the way to our old targets): "
                                 f"{month(R2['EBITDA positive from month'])} on {floor_usd(R2)}."),
        ("The shape", f"{lo.LEVEL:,} online savers a month from month 30 after the seed, 1 in 10 from the doorstep; {rs(op.SEED_CAC)} to win a saver in the seed, "
                      f"{rs(op.CAC)} after, plus our 10% contingency on every cost.")])
    title = ("At the main case the company does not turn profitable within 8 years: a saver earns back less than it costs in 5 years, "
             "so growing faster deepens the loss")
    return ("THE COMPANY AT THE MAIN CASE", title, body,
            f"EBITDA: {GLOSS['ebitda']}. {MONEY_NOTE} Undiscounted; tax on profit after losses carried forward.")


def p_financials():
    y_ = main_years()
    g = lambda c: [float(v) for v in y_[c]]
    loans = [a + b for a, b in zip(g("Loan marketing fees Rs cr"), g("Other products Rs cr"))]
    lines = [("Active savers at year end, lakh", [v / 1e5 for v in g("active savers (end)")], False),
             ("Revenue, ₹ Cr", g("Revenue Rs cr"), True),
             ("&nbsp;&nbsp;fund fees", g("Fund trail Rs cr"), False),
             ("&nbsp;&nbsp;loans (all lenders)", loans, False),
             ("&nbsp;&nbsp;cards", g("Cards Rs cr"), False),
             ("Cost to win savers, ₹ Cr", [-v for v in g("Acquisition Rs cr")], False),
             ("Team, ₹ Cr", [-v for v in g("Team Rs cr")], False),
             ("Other costs, ₹ Cr", [-v for v in g("Other costs Rs cr")], False),
             ("<b>EBITDA, ₹ Cr</b>", g("EBITDA Rs cr"), True),
             ("Cumulative EBITDA, ₹ Cr", list(np.cumsum(g("EBITDA Rs cr"))), False)]
    rows = [[lab] + [f"<b>{crn(v)}</b>" if bold else crn(v) for v in vs] for lab, vs, bold in lines]
    tb = table([""] + [f"Y{int(v)}" for v in y_["year"]], rows, [28] + [72 / 8] * 8, 11, compact=True, extra="fin")
    chart = ebitda_svg(y_, 600, 172, total=False)
    body = two(chart, tiles(company_tiles(y_=y_), 20, 6, 6), 600) + f'<div style="margin-top:4px">{tb}</div>'
    y8 = float(y_["EBITDA Rs cr"].iloc[-1])
    title = (f"The main case: EBITDA is still {cr(y8)} in year 8, so it is not positive by month 96; the company needs at least "
             f"{usd(MAIN['money needed $M'])}, and 8 years add up to {cr(MAIN['cumulative EBITDA 8y Rs cr'])}")
    return ("THE COMPANY, YEAR BY YEAR", title, body,
            f"{lo.LEVEL:,} online savers a month from month 30 after the seed, 1 in 10 from the doorstep; cost to win {rs(op.SEED_CAC)} in the seed and "
            f"{rs(op.CAC)} after. EBITDA: {GLOSS['ebitda']}. Loans: personal and business loans plus other lenders' gold, property, home, durable and "
            f"vehicle loans. Other costs: tech, payments, support, office, compliance, brand and the 10% contingency. {MONEY_NOTE}")


# ---------------------------------------------------------------------------------------------------------- the four facts
def facts():
    d1 = alone("daily")
    up = float(UPL.loc["daily", "LTV/CAC 5y at the upside alone"])
    keep = DRV.loc["keep"]
    deb, fee = ltvl("We pay Rs 2 a debit, weekly"), ltvl("Equity fund fee 0.5%, not 0.75%")
    m200 = levm("Rs 200 a day")
    return [("Bachatt's average daily amount", "Ask Bachatt for the average, not the minimum. ₹100 is our product's floor; Bachatt's own minimums "
                                               "are lower (₹51/₹101 a day; ₹20 for its liquid fund).",
             [("₹100", MED, "main"), (f"₹{d1:.0f}", 1.0, "even"), ("₹200", up, "up")],
             f"Company: ₹200 a day gives profit from {month(m200[0]) if m200[0] else 'not by month 96'} on {usd(m200[1])}."),
            ("Bachatt's exact share still saving at 12 months", "Ask Bachatt for its 12-month cohort curve; it has told us 30–40%.",
             [("30%", float(keep["median if low"]), "down"), (f"{MAIN_IN['r12']:.0%}", MED, "main"), ("40%", float(keep["median if high"]), "up")],
             f"{alone('keep_up'):.1%} alone gives 1×; 45% (1.0% a month stopping after) needs {levm_usd('45% still saving at a year')}."),
            ("Debits at ₹0 to us, in writing", "BSE StAR MF and the fund houses: a daily ₹100 debit on one mandate, at no cost to us.",
             [("₹2 a weekly debit", deb, "down"), ("₹0", MED, "main")],
             f"Company: paying ₹2 a weekly debit raises the money needed to {levm_usd('We pay Rs 2 a debit, weekly')}."),
            ("The fee on the fund the ₹100 goes into, in writing", f"{val('blend')} blended or better: 80% equity at {pct(op.EQ_TRAIL, 2)}, 20% debt at "
                                                                   f"~{pct(DEBT_MAIN, 2)}. Daily minimums are ~₹100 a scheme, so one hybrid fund must pay about "
                                                                   f"{val('blend')} or more.",
             [("0.5% on equity", fee, "down"), (val("blend"), MED, "main")],
             f"Company: at 0.5% on equity the money needed is {levm_usd('Equity fund fee 0.5%, not 0.75%')}.")]


def facts_svg(W=1152):
    x0, x1_, lo_, hi_, rh = 540, 1130, 0.3, 1.8, 98
    X_ = lambda v: x0 + (x1_ - x0) * (v - lo_) / (hi_ - lo_)
    out = [T(0, 14, "THE FACT, AND HOW CHEAPLY WE CAN GET IT", 11, 700, SLATE, ls=1), T(x0, 14, "ONE SAVER'S LTV/CAC, 5 YEARS, EITHER WAY", 11, 700, SLATE, ls=1)]
    y = 26
    for i, (name, how, pts, comp) in enumerate(facts(), start=1):
        out.append(f'<circle cx="14" cy="{y + 16}" r="13" fill="{NAVY}"/>' + T(14, y + 21, str(i), 13, 800, "white", "middle"))
        out.append(T(36, y + 21, name, 15, 800, NAVY))
        lines = wrap(how, 74)[:3]
        for j, ln in enumerate(lines):
            out.append(T(36, y + 40 + 15 * j, ln, 11.5, 500, INK))
        out.append(T(36, y + 40 + 15 * len(lines), comp, 11.5, 700, NAVY4))
        vs = [v for _l, v, _t in pts]
        out.append(f'<line x1="{X_(min(vs)):.1f}" y1="{y + 30}" x2="{X_(max(vs)):.1f}" y2="{y + 30}" stroke="{LINE}" stroke-width="7" stroke-linecap="round"/>')
        for lab, v, tag in pts:
            col = NAVY if tag == "main" else (NAVY4 if tag == "even" else (TEAL if v >= MED else LATE))
            out.append(f'<circle cx="{X_(v):.1f}" cy="{y + 30}" r="{8 if tag == "main" else 7}" fill="{"white" if tag == "main" else col}" stroke="{col}" stroke-width="3"/>')
            out.append(halo(T(X_(v), y + 15, lab, 12, 700, col, "middle")))
            out.append(halo(T(X_(v), y + 54, x(v), 13, 800, col, "middle")))
        y += rh
    grid = []
    for v in (0.5, 1.0, 1.5):
        grid.append(f'<line x1="{X_(v):.1f}" y1="22" x2="{X_(v):.1f}" y2="{y - 10}" stroke="{RED if v == 1 else LINE}" stroke-width="{1.6 if v == 1 else 1}" stroke-dasharray="4 4"/>')
        grid.append(T(X_(v), y + 4, f"{v:g}×", 11.5, 700, RED if v == 1 else MUTE, "middle"))
    return svg(W, y + 10, "".join(out[:2] + grid + out[2:]))


def p_prove():
    title = "Four facts decide most of the answer, and all four are cheap to get: two questions to Bachatt and two answers in writing"
    return ("THE FOUR FACTS TO GET NEXT", title, facts_svg(),
            f"Open circle: the main case ({XMED}). Retention: the Monte Carlo median with still saving pinned at 30%, then 40%. The other rows change one "
            "input at a time from the main case. None of the four needs the seed's money: two data requests and two confirmations in writing.")

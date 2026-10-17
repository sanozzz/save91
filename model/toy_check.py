"""Toy cohort model for Google Sheets: the SAME maths as the sheet formulas (model/toy_gsheet.py), in numpy, plus
the reconciliation against the full Python model (model/cohort_engine.py) and a replay of the sheet's formulas.

What it writes
  tables/toy_expected.csv  Summary cell -> the value the sheet should show at the likely inputs
  tables/toy_vs_full.csv   toy vs the full engine at the likely values, with the gap
Checks (asserts)
  - with take-up and approval growth at 0 the toy's loans, top-ups, cards and housing equal the full engine's exactly
    (only the calendar-year growth is approximated);
  - cumulative P&L at 60 months within +-5% of the full engine;
  - if tables/toy_gsheet_spec.json exists: every formula in it is parsed and evaluated by a small Google Sheets formula
    interpreter below (named ranges, spills, MMULT, MAKEARRAY, LAMBDA, SCAN, FILTER ...), and every Summary cell must
    equal this file's numpy value (1e-9 relative). That catches off-by-one rows, wrong names and bad syntax.

Toy mechanics (one saver's months 1-60 in year-1 terms on 'Per saver'; Monthly = sign-ups x that profile, summed over
cohorts, then x the calendar-year growth factors). The approximations, all of them:
  1. calendar growth applied to the month's total (take-up x approval factor of that calendar year); the full engine
     gives every cohort its own profile. Exact for lines booked at the moment of take-up (cards, housing, first loans)
     except for pool depletion, which item 2 corrects for loans;
  2. never-borrowed pool adjustment D(t): with growth, savers borrow sooner and the never-borrowed pool empties faster.
     D(t) = prod_{k<t} (1 - q f(k)) / (1 - q), q = full-rate first-loan chance a month, f = loan factor; loans in month t =
     f(t) D(t) x sum over cohorts c of S(c)/D(c) x loans per sign-up at his age (exact if q were the same at every age);
  3. top-ups take the loan factor of 20 months earlier (they come 13-35 months after the loan); collections take it of
     12 months earlier;
  4. collections: one fee per loan made (31-90 day fee + 90+ fee), paid 12 months after the loan (full engine: 9 and 18);
  5. the 17 non-housing cross-sell products are one Rs-per-active-saver-a-year input with the early factor, growing
     xs_growth (20%) for each full year he has saved (the full engine's money builds up with years saved: renewals,
     holdings), calibrated to the full engine's booked money over 60 months;
  6. repeat loans (0.2% of loans) take the first-loan calendar factor.
"""
import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohort_engine as ce  # noqa: E402

ROOT = HERE.parent
T = ROOT / "tables"
SPEC = T / "toy_gsheet_spec.json"
N = 60
TOPUP_LAG = 20          # calendar factor of the loan, months before the top-up
COLL_LAG = 12           # collections paid this many months after the loan
NON_HOUSING = tuple(p for p, *_ in ce.PRODUCTS if p not in ("loan_home", "loan_lap"))

# ---------------------------------------------------------------- inputs (name used in the sheet -> engine key)
# (name, plain label, unit, number format, engine key or None)
SECTIONS = [
    ("Sign-ups", [
        ("signups", "Sign-ups a month in year 1, once the agent is up to speed", "sign-ups a month", "num1", "signups_run"),
        ("ramp", "Months for a new agent to reach full speed (he starts at half speed)", "months", "num1", "ramp_months"),
        ("signup_decline_y5", "Sign-ups by month 49 as a share of the year-1 level (straight line from month 12, flat after)", "share",
         "pct", "signup_decline_y5"),
        ("online_lead_share", "Share of onboardings that start as bought online leads (served offline like any saver)", "share", "pct",
         "online_lead_share"),
        ("lead_cost", "Our cost per online lead the agent converts", "Rs a lead", "inr", "lead_cost"),
    ]),
    ("Still saving", [
        ("ret_m3", "Still saving at month 3", "share of sign-ups", "pct", "r3"),
        ("ret_m12", "Still saving at month 12", "share of sign-ups", "pct", "r12"),
        ("churn_late", "Monthly drop-off after month 12", "a month", "pct", "churn_late"),
    ]),
    ("Saving", [
        ("daily", "Daily amount at sign-up", "Rs a day", "inr", "daily"),
        ("deposit_days", "Deposit days a month", "days", "num1", "days"),
        ("amount_growth", "Daily amount grows at each yearly term start", "a year", "pct", "amount_growth"),
    ]),
    ("The fund", [
        ("rollover", "Share of the balance left in the fund at each term end", "share", "pct", "rollover"),
        ("withdraw_m", "Share of the balance withdrawn mid-term, each month", "a month", "pct", "withdraw_m"),
        ("fund_return", "Saver's net return on the fund", "a year", "pct", "fund_return"),
        ("trail", "Our fund commission (trail) on the average balance", "a year", "pct2", "trail"),
    ]),
    ("Cash visits", [
        ("upi_m12", "Share of active savers on UPI by his month 12 (0 at month 1, straight line)", "share", "pct", "upi_12"),
        ("capacity", "Cash visits one agent can make a day", "visits a day", "num0", "capacity"),
    ]),
    ("Marketplace timing and growth", [
        ("early_takeup", "Take-up factor in a saver's months 1-6 (loans, cards, cross-sell)", "x the full rate", "mult", "early_takeup_mult"),
        ("early_approval", "Approval factor in a saver's months 1-6 (first loans, cards, home loans, LAP)", "x the full rate", "mult",
         "early_approval_mult"),
        ("takeup_growth", "Every take-up rises each calendar year (cap 2x)", "a year", "pct", "takeup_growth"),
        ("approval_growth", "Approval rises each calendar year (cap 80% approval)", "a year", "pct", "approval_growth"),
    ]),
    ("Loans (partner lender)", [
        ("apply", "Savers with no loan running who apply, a year", "a year", "pct", "apply"),
        ("eligible", "Applicants eligible", "share", "pct", "eligible"),
        ("approved_first", "Approved, first loan", "share", "pct", "approved_first"),
        ("ticket", "Loan size", "Rs", "inr", "ticket"),
        ("fee", "Our origination fee at the start: a DSA's rate (first, repeat and top-up loans)", "of the loan", "pct3", "fee"),
        ("fee_mult_start", "Fee multiplier in company month 1 (x the DSA rate)", "x", "mult", "fee_mult_start"),
        ("fee_mult_end", "Fee multiplier reached in company month 60 (straight line from month 1)", "x", "mult", "fee_mult_end"),
        ("taken_back", "Share of our fees taken back", "share", "pct", "taken_back"),
        ("tenure", "Loan tenure (no new loan while one runs; he can re-apply after)", "months", "num0", "tenure"),
        ("ticket_growth", "Next loan bigger for each year repaid (repeat loans and top-ups, cap Rs 5 lakh)", "a year", "pct", "ticket_growth"),
        ("topup_share", "Borrowers with 12+ EMIs paid who take a top-up, a year", "a year", "pct", "topup_share"),
        ("topup_size", "Top-up size, share of the original loan", "share", "pct", "topup_size"),
        ("coll_per_loan", "Collection fees per loan made (31-90 days late and 90+ days bad)", "Rs a loan", "inr2", None),
    ]),
    ("Cards", [
        ("card_share", "Savers who get a card (once, over his first 6 marketplace months)", "share", "pct", "card_share"),
        ("card_fee", "Fee per card", "Rs a card", "inr", "card_fee"),
    ]),
    ("Cross-sell", [
        ("xs_other", "Insurance, investments, payments and other loans: Rs per active saver a year", "Rs a year", "inr1", None),
        ("xs_growth", "That cross-sell money grows for each full year he has saved", "a year", "pct", None),
        ("home_takeup", "Home loan (other lenders): savers who apply, a year", "a year", "pct", "loan_home_takeup"),
        ("home_approval", "Home loan: approval share", "share", "pct", "loan_home_approval"),
        ("home_ticket", "Home loan: loan size", "Rs", "inr", "loan_home_ticket"),
        ("home_fee", "Home loan: our fee, share of the loan", "of the loan", "pct2", "loan_home_comm"),
        ("lap_takeup", "Loan against property: savers who apply, a year", "a year", "pct", "loan_lap_takeup"),
        ("lap_approval", "Loan against property: approval share", "share", "pct", "loan_lap_approval"),
        ("lap_ticket", "Loan against property: loan size", "Rs", "inr", "loan_lap_ticket"),
        ("lap_fee", "Loan against property: our fee, share of the loan", "of the loan", "pct2", "loan_lap_comm"),
    ]),
    ("Costs", [
        ("salary", "Agent's salary a month", "Rs a month", "inr", "salary"),
        ("kyc", "Onboarding and KYC per sign-up", "Rs a sign-up", "inr", "kyc_cost"),
        ("running", "Running cost per active saver a month (support, app, cash-deposit charges)", "Rs a saver a month", "inr", "support_cost"),
        ("cash_cover", "Cash cover: fidelity and cash-in-transit insurance a month", "Rs a month", "inr", "cash_cover"),
        ("agent_pay", "Agent pay on his savers' average balance (company months 1-60)", "a year", "pct2", "agent_balance_pay"),
        ("incentive_cap", "Cap on that pay, per agent a month (round 10)", "Rs a month", "inr", "incentive_cap"),
    ]),
]
FIXED = [
    ("mkt_from", "First month of his saving at which he is offered loans, cards and cross-sell", "his month", "num0", "marketplace_from"),
    ("term", "Savings term", "months", "num0", "term"),
    ("approved_repeat", "Approved, repeat loan", "share", "pct", "approved_repeat"),
    ("visit_every", "Days between cash visits", "days", "num1", "visit_every"),
    ("extra_cost", "Extra capacity cost a month per 400 visits a day over capacity", "Rs a month", "inr", "extra_capacity_cost"),
    ("upi_ramp", "His month at which the UPI share reaches its month-12 level", "his month", "num0", "upi_ramp"),
]
# derived (grey on Inputs): name, label, unit, format, sheet formula (numpy twins in derived())
DERIVED = [
    ("fund_m", "Saver's net return a month", "a month", "pct3", "=(1+fund_return)^(1/12)-1"),
    ("apply_m", "Chance a saver with no loan running applies, a month", "a month", "pct3", "=1-(1-apply)^(1/12)"),
    ("tenure_m", "Loan tenure in whole months", "months", "num0", "=MAX(1,ROUND(tenure,0))"),
    ("repeat_ticket", "Repeat loan size (after the tenure repaid)", "Rs", "inr", "=MIN(500000,ticket*(1+ticket_growth)^(tenure_m/12))"),
    ("topup_amt", "Top-up size (after a year repaid)", "Rs", "inr", "=topup_size*ticket*(1+ticket_growth)"),
    ("topup_m", "Chance an eligible borrower takes a top-up, a month", "a month", "pct3", "=1-(1-topup_share)^(1/12)"),
    ("card_catchup", "Share of cards the early factors held back, issued in the next 6 months", "share", "pct",
     "=MAX(0,1-(MAX(0,MIN(6,7-mkt_from))*early_takeup*early_approval+6-MAX(0,MIN(6,7-mkt_from)))/6)"),
    ("home_m", "Home-loan application chance a month", "a month", "pct3", "=1-(1-home_takeup)^(1/12)"),
    ("lap_m", "LAP application chance a month", "a month", "pct3", "=1-(1-lap_takeup)^(1/12)"),
    ("loan_q", "First-loan chance a month at full rates (for the pool adjustment on Monthly)", "a month", "pct3",
     "=apply_m*eligible*MIN(0.8,approved_first)"),
]
ALL_INPUTS = [r for _s, rows in SECTIONS for r in rows] + FIXED
NEW_DEFAULTS = {"fee_mult_start": 1.0, "fee_mult_end": 1.5, "incentive_cap": 10000.0}     # round 9 keys, used only if the engine lacks them
XS_GROWTH = 0.20        # cross-sell per active saver grows this much for each full year saved (toy-only; coordinator 17 Oct)


def full_run(x=None):
    x = x or ce.likely_inputs()
    return ce.run(x)


def full_nonhousing(res):
    return float(sum(res["monthly"][f"rev_xs_{p}"][0] for p in NON_HOUSING).sum())


def likely_toy_inputs(xs_other=None):
    """Toy inputs at the agreed likely values. xs_other None -> calibrated (rounded to Rs 0.1)."""
    x = ce.likely_inputs()
    v = {n: float(x[k] if k in x else NEW_DEFAULTS[k]) for n, _l, _u, _f, k in ALL_INPUTS if k}
    res = full_run(x)
    v["coll_per_loan"] = round(float(res["out"]["collections_per_loan"][0]), 2)
    v["xs_growth"] = XS_GROWTH
    if xs_other is None:
        base = toy({**v, "xs_other": 1.0})["m"]["r_xs"].sum()
        xs_other = round(full_nonhousing(res) / base, 1)
    v["xs_other"] = float(xs_other)
    return v


def derived(v):
    d = {}
    d["fund_m"] = (1 + v["fund_return"]) ** (1 / 12) - 1
    d["apply_m"] = 1 - (1 - v["apply"]) ** (1 / 12)
    d["tenure_m"] = max(1, math.floor(v["tenure"] + 0.5))
    d["repeat_ticket"] = min(500000.0, v["ticket"] * (1 + v["ticket_growth"]) ** (d["tenure_m"] / 12))
    d["topup_amt"] = v["topup_size"] * v["ticket"] * (1 + v["ticket_growth"])
    d["topup_m"] = 1 - (1 - v["topup_share"]) ** (1 / 12)
    ne = max(0, min(6, 7 - v["mkt_from"]))
    d["card_catchup"] = max(0.0, 1 - (ne * v["early_takeup"] * v["early_approval"] + 6 - ne) / 6)
    d["home_m"] = 1 - (1 - v["home_takeup"]) ** (1 / 12)
    d["lap_m"] = 1 - (1 - v["lap_takeup"]) ** (1 / 12)
    d["loan_q"] = d["apply_m"] * v["eligible"] * min(0.8, v["approved_first"])
    return d


def toy(v, ages=N):
    """Per saver (ages 1..ages, year-1 terms; 60 for the toy, 96 for the company tabs) and Monthly (months 1-60), exactly as the sheet formulas."""
    NA = int(ages)
    v = {**v, **derived(v)}
    A = np.arange(1, NA + 1, dtype=float)
    p = {}
    s = np.ones(NA)
    for i in range(1, NA):
        a = A[i - 1]
        s[i] = s[i - 1] * (v["ret_m3"] ** (1 / 3) if a <= 3 else (v["ret_m12"] / v["ret_m3"]) ** (1 / 9) if a <= 12 else 1 - v["churn_late"])
    dep = v["daily"] * v["deposit_days"] * (1 + v["amount_growth"]) ** np.floor((A - 1) / v["term"])
    avg, end = np.zeros(NA), np.zeros(NA)
    for i in range(NA):
        avg[i] = 0.5 * dep[i] if i == 0 else end[i - 1] * (v["rollover"] if (A[i] - 1) % v["term"] == 0 else 1.0) * (1 - v["withdraw_m"]) + 0.5 * dep[i]
        end[i] = avg[i] * (1 + v["fund_m"]) + 0.5 * dep[i]
    upi = v["upi_m12"] * np.minimum(1.0, (A - 1) / (v["upi_ramp"] - 1))
    K = np.where(A < v["mkt_from"], 0.0, np.where(A <= 6, v["early_takeup"], 1.0))
    L = np.where(A <= 6, v["early_approval"], 1.0)
    M = v["apply_m"] * K
    Tn = v["tenure_m"]
    n0, e, first, rep = np.zeros(NA), np.zeros(NA), np.zeros(NA), np.zeros(NA)
    for i in range(NA):
        if i == 0:
            n0[i], e[i] = 1.0, 0.0
        else:
            n0[i] = (n0[i - 1] - first[i - 1]) * s[i] / s[i - 1]
            e[i] = (e[i - 1] - rep[i - 1]) * s[i] / s[i - 1]
            j = int(A[i]) - 1 - Tn                       # 1-based vintage back in the pool
            if j >= 1:
                e[i] += (first[j - 1] + rep[j - 1]) * s[i] / s[j - 1]
        first[i] = n0[i] * M[i] * v["eligible"] * min(0.8, v["approved_first"] * L[i])
        rep[i] = e[i] * M[i] * v["eligible"] * v["approved_repeat"]
    loans = first + rep
    u = v["topup_m"]
    W = np.zeros(NA)
    for i in range(1, NA):
        a = int(A[i])
        W[i] = (1 - u) * W[i - 1]
        if a >= 14 and Tn > 13:
            W[i] += loans[a - 13 - 1] / s[a - 13 - 1]
        if a >= Tn + 1 and Tn > 13:
            W[i] -= loans[a - Tn - 1] / s[a - Tn - 1] * (1 - u) ** (Tn - 13)
    topups = s * u * W
    mf = v["mkt_from"]
    cards = np.where((A >= mf) & (A <= mf + 5), v["card_share"] / 6 * s * np.minimum(2, K) * np.minimum(2, L),
                     np.where((A >= mf + 6) & (A <= mf + 11), v["card_share"] * v["card_catchup"] / 6 * s, 0.0))
    hous = {}
    for h in ("home", "lap"):
        H = v[f"{h}_m"] * K * np.minimum(0.8, v[f"{h}_approval"] * L)
        Nh = np.ones(NA)
        for i in range(1, NA):
            Nh[i] = Nh[i - 1] * (1 - H[i - 1])
        hous[h] = s * Nh * H
        p[f"{h}_chance"], p[f"{h}_never"] = H, Nh
    coll = np.zeros(NA)
    eq = loans + topups * v["topup_size"] * (1 + v["ticket_growth"])
    coll[COLL_LAG:] = v["coll_per_loan"] * eq[:-COLL_LAG]
    p.update(age=A, saving=s, dep_active=dep, deposits=s * dep, avg_active=avg, end_active=end, balance=s * avg, upi=upi,
             visits=s * (1 - upi) / v["visit_every"], trail=s * avg * v["trail"] / 12, takeup_f=K, approval_f=L, apply_chance=M,
             never=n0, back=e, apps=(n0 + e) * M, first=first, repeat=rep, loans=loans,
             lent=first * v["ticket"] + rep * v["repeat_ticket"], topup_pool=W, topups=topups, cards=cards,
             xs=s * v["xs_other"] / 12 * K * (1 + v["xs_growth"]) ** np.floor((A - 1) / 12), home=hous["home"], lap=hous["lap"], collect=coll, running=s * v["running"])
    # Monthly
    t = np.arange(1, N + 1, dtype=float)
    S = np.array([v["signups"] * (min(1.0, 0.5 + 0.5 * (k - 1) / v["ramp"]) if v["ramp"] > 0 else 1.0)
                  * (1.0 if k <= 12 else 1 + (v["signup_decline_y5"] - 1) * min(1.0, (k - 12) / 37)) for k in t])   # round 8
    y = np.floor((t - 1) / 12) + 1
    tf = np.where((1 + v["takeup_growth"]) ** (y - 1) > 2, 2.0, (1 + v["takeup_growth"]) ** (y - 1))
    af = (1 + v["approval_growth"]) ** (y - 1)
    cap = lambda share: np.where(share * af > 0.8, 0.8 / share, af)
    loanf = tf * cap(v["approved_first"])
    q = v["loan_q"]
    pool = np.cumprod((1 - q * loanf) / (1 - q)) * (1 - q) / (1 - q * loanf)
    Sadj = S / pool
    lf0 = loanf * pool
    lag = lambda f, k: f[np.maximum(1, t - k).astype(int) - 1]
    conv = lambda prof, vec: np.array([np.dot(vec[:k + 1][::-1], prof[:k + 1]) for k in range(N)])
    m = {"month": t, "year": y, "tf": tf, "af": af, "loanf": loanf, "cardf": tf * np.where(af > 2, 2.0, af),
         "homef": tf * cap(v["home_approval"]), "lapf": tf * cap(v["lap_approval"]), "pool": pool, "signups": S,
         "signups_adj": Sadj, "lf0": lf0, "lf12": lag(lf0, COLL_LAG), "lf20": lag(lf0, TOPUP_LAG)}
    m["savers"] = conv(p["saving"], S)
    m["deposits"] = conv(p["deposits"], S)
    m["balance"] = conv(p["balance"], S)
    m["visits"] = conv(p["visits"], S)
    m["loans"] = conv(p["loans"], Sadj) * lf0
    m["topups"] = conv(p["topups"], Sadj) * m["lf20"]
    m["lent"] = conv(p["lent"], Sadj) * lf0 + m["topups"] * v["topup_amt"]
    m["cards"] = conv(p["cards"], S) * m["cardf"]
    m["home"] = conv(p["home"], S) * m["homef"]
    m["lap"] = conv(p["lap"], S) * m["lapf"]
    m["r_fund"] = m["balance"] * v["trail"] / 12
    m["fee_rate"] = v["fee"] * (v["fee_mult_start"] + (v["fee_mult_end"] - v["fee_mult_start"]) * (t - 1) / 59)   # round 9 ramp
    m["r_fees"] = m["lent"] * m["fee_rate"] * (1 - v["taken_back"])
    m["r_coll"] = conv(p["collect"], Sadj) * m["lf12"]
    m["r_cards"] = m["cards"] * v["card_fee"]
    m["r_xs"] = conv(p["xs"], S) * tf
    m["r_house"] = m["home"] * v["home_ticket"] * v["home_fee"] + m["lap"] * v["lap_ticket"] * v["lap_fee"]
    m["income"] = m["r_fund"] + m["r_fees"] + m["r_coll"] + m["r_cards"] + m["r_xs"] + m["r_house"]
    m["c_salary"] = np.full(N, v["salary"])
    m["c_kyc"] = S * v["kyc"]
    m["c_running"] = m["savers"] * v["running"]
    m["c_cover"] = np.full(N, v["cash_cover"])
    m["c_agent"] = np.minimum(m["balance"] * v["agent_pay"] / 12, v["incentive_cap"])        # round 10: capped per agent
    m["c_extra"] = np.where(m["visits"] > v["capacity"], (m["visits"] - v["capacity"]) * v["extra_cost"] / 400, 0.0)
    m["c_leads"] = S * v["online_lead_share"] * v["lead_cost"]                                  # round 8: bought online leads
    m["cost"] = m["c_salary"] + m["c_kyc"] + m["c_running"] + m["c_cover"] + m["c_agent"] + m["c_extra"] + m["c_leads"]
    m["net"] = m["income"] - m["cost"]
    m["cum"] = np.cumsum(m["net"])
    return {"p": p, "m": m, "d": {k: v[k] for k in derived(v)}}


def payback(cum):
    if cum[-1] < 0:
        return "not within 60 months"
    neg = np.where(cum < 0)[0]
    return float(neg.max() + 2) if neg.size else 1.0


# Summary rows: (label, toy value from m, full-engine value from res, kind)  -- toy_gsheet.py writes the same rows
SUMMARY = [
    ("Cumulative P&L at month 12", lambda m: m["cum"][11], lambda r: r["monthly"]["cum_cash"][0][11], "inr"),
    ("Cumulative P&L at month 36", lambda m: m["cum"][35], lambda r: r["out"]["cum_pnl36"][0], "inr"),
    ("Cumulative P&L at month 60", lambda m: m["cum"][59], lambda r: r["out"]["cum_pnl60"][0], "inr"),
    ("Payback month (cumulative P&L stays at or above 0 from here)", lambda m: payback(m["cum"]),
     lambda r: r["out"]["payback_month"][0], "month"),
    ("Peak cash need (lowest cumulative P&L)", lambda m: min(0.0, m["cum"].min()), lambda r: r["out"]["peak_cash_need"][0], "inr"),
    ("Savers still saving, year-5 average (months 49-60)", lambda m: m["savers"][48:].mean(),
     lambda r: r["monthly"]["still_saving"][0][48:].mean(), "num1"),
    ("Money lent in year 5 (first, repeat and top-up loans)", lambda m: m["lent"][48:].sum(), lambda r: r["out"]["money_lent_y5"][0], "inr"),
    ("Loans made in year 5 (first and repeat)", lambda m: m["loans"][48:].sum(), lambda r: r["out"]["loans_y5"][0], "num1"),
    ("Money lent in 60 months", lambda m: m["lent"].sum(), lambda r: r["out"]["money_lent60"][0], "inr"),
    ("Revenue per active saver a year (60-month average)", lambda m: m["income"].sum() / (m["savers"].sum() / 12),
     lambda r: r["out"]["income_per_active_year"][0], "inr"),
    (None, None, None, None),
    ("Where the money comes from, 60 months", None, None, "head"),
    ("Fund trail", lambda m: m["r_fund"].sum(), lambda r: r["monthly"]["rev_fund"][0].sum(), "inr"),
    ("Loan fees (net of fees taken back)", lambda m: m["r_fees"].sum(), lambda r: r["monthly"]["rev_origination"][0].sum(), "inr"),
    ("Collection fees", lambda m: m["r_coll"].sum(),
     lambda r: (r["monthly"]["rev_dpd31_90"][0] + r["monthly"]["rev_recovery90"][0]).sum(), "inr"),
    ("Card fees", lambda m: m["r_cards"].sum(), lambda r: r["monthly"]["rev_cards"][0].sum(), "inr"),
    ("Insurance, investments, payments and other loans (lumped)", lambda m: m["r_xs"].sum(), full_nonhousing, "inr"),
    ("Home-loan and LAP fees", lambda m: m["r_house"].sum(),
     lambda r: (r["monthly"]["rev_xs_loan_home"][0] + r["monthly"]["rev_xs_loan_lap"][0]).sum(), "inr"),
    ("Income", lambda m: m["income"].sum(), lambda r: r["monthly"]["income"][0].sum(), "inr"),
    ("Costs", lambda m: m["cost"].sum(), lambda r: r["monthly"]["cost_total"][0].sum(), "inr"),
    ("Net (= cumulative P&L at month 60)", lambda m: m["net"].sum(), lambda r: r["monthly"]["net"][0].sum(), "inr"),
    ("  of the costs: online leads, 60 months", lambda m: m["c_leads"].sum(), lambda r: r["monthly"]["cost_leads"][0].sum(), "inr"),
    ("  of the costs: extra cash-collection capacity (helpers), 60 months", lambda m: m["c_extra"].sum(),
     lambda r: r["monthly"]["cost_extra_capacity"][0].sum(), "inr"),
]


# ---------------------------------------------------------------- a small Google Sheets formula interpreter
class SheetError(Exception):
    pass


TOK = re.compile(r"""(?P<ws>\s+)
 |(?P<num>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?)
 |(?P<str>"(?:[^"]|"")*")
 |(?P<ref>(?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?(?![A-Za-z0-9_(])
         |\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?(?![A-Za-z0-9_(]))
 |(?P<name>[A-Za-z_][A-Za-z0-9_.]*)
 |(?P<op><=|>=|<>|[-+*/^&=<>(),%])""", re.X)
FUNCS = {"IF", "MIN", "MAX", "SUM", "AVERAGE", "INT", "MOD", "ROUND", "INDEX", "AND", "OR", "SEQUENCE", "ARRAYFORMULA", "MMULT",
         "MAKEARRAY", "LAMBDA", "SCAN", "FILTER", "IFERROR", "ISNUMBER", "ABS", "LET", "ROUNDUP", "MATCH", "ROWS", "SUMIFS"}


def col_num(s):
    n = 0
    for ch in s:
        n = n * 26 + ord(ch.upper()) - 64
    return n


def col_name(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def parse_a1(a1):
    """'B3' -> (row, col); 'B2:C9' -> (r1, c1, r2, c2)."""
    parts = a1.replace("$", "").split(":")
    rc = []
    for ptxt in parts:
        mm = re.fullmatch(r"([A-Za-z]{1,3})(\d+)", ptxt)
        rc.append((int(mm.group(2)), col_num(mm.group(1))))
    return rc[0] if len(rc) == 1 else (*rc[0], *rc[1])


def tokenize(f):
    out, i = [], 0
    while i < len(f):
        mm = TOK.match(f, i)
        if not mm:
            raise SyntaxError(f"cannot tokenize at {f[i:i + 20]!r} in {f!r}")
        i = mm.end()
        kind = mm.lastgroup
        if kind != "ws":
            out.append((kind, mm.group(kind)))
    return out


class Parser:
    def __init__(self, toks, src):
        self.t, self.i, self.src = toks, 0, src

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self, val=None):
        tok = self.peek()
        if val is not None and tok[1] != val:
            raise SyntaxError(f"expected {val!r}, got {tok[1]!r} in {self.src!r}")
        self.i += 1
        return tok

    def parse(self):
        e = self.comparison()
        if self.i != len(self.t):
            raise SyntaxError(f"trailing tokens {self.t[self.i:]} in {self.src!r}")
        return e

    def comparison(self):
        e = self.concat()
        while self.peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
            op = self.take()[1]
            e = ("bin", op, e, self.concat())
        return e

    def concat(self):
        e = self.additive()
        while self.peek()[1] == "&":
            self.take()
            e = ("bin", "&", e, self.additive())
        return e

    def additive(self):
        e = self.term()
        while self.peek()[1] in ("+", "-"):
            op = self.take()[1]
            e = ("bin", op, e, self.term())
        return e

    def term(self):
        e = self.power()
        while self.peek()[1] in ("*", "/"):
            op = self.take()[1]
            e = ("bin", op, e, self.power())
        return e

    def power(self):
        e = self.unary()
        while self.peek()[1] == "^":
            self.take()
            e = ("bin", "^", e, self.unary())
        return e

    def unary(self):              # Sheets: unary minus binds tighter than ^ (-2^2 = 4)
        if self.peek()[1] in ("-", "+"):
            op = self.take()[1]
            return ("neg", self.unary()) if op == "-" else self.unary()
        return self.primary()

    def primary(self):
        kind, val = self.take()
        if kind == "num":
            return ("num", float(val))
        if kind == "str":
            return ("str", val[1:-1].replace('""', '"'))
        if kind == "ref":
            return ("ref", val)
        if kind == "name":
            if self.peek()[1] == "(":
                fn = val.upper()
                if fn not in FUNCS:
                    raise SyntaxError(f"unknown function {val} in {self.src!r}")
                self.take("(")
                args = []
                if self.peek()[1] != ")":
                    args.append(self.comparison())
                    while self.peek()[1] == ",":
                        self.take()
                        args.append(self.comparison())
                self.take(")")
                return ("call", fn, args)
            if val.upper() in ("TRUE", "FALSE"):
                return ("num", 1.0 if val.upper() == "TRUE" else 0.0)
            return ("name", val)
        if val == "(":
            e = self.comparison()
            self.take(")")
            return e
        raise SyntaxError(f"unexpected {val!r} in {self.src!r}")


def is_a1_like(name):
    return bool(re.fullmatch(r"[A-Za-z]{1,3}\d+", name) or re.fullmatch(r"[Rr]\d*[Cc]\d*", name)
                or name.upper() in ("TRUE", "FALSE"))


def valid_range_name(name):
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name)) and not is_a1_like(name) and name.upper() not in FUNCS


class Book:
    def __init__(self, spec):
        self.cells, self.names = {}, {}
        for sh in spec["sheets"]:
            self.cells[sh["title"]] = {parse_a1(a1): v for a1, v in sh["cells"].items()}
            for nm, rng in sh.get("named_ranges", {}).items():
                assert nm not in self.names, f"named range {nm} twice"
                assert valid_range_name(nm), f"named range {nm!r} is not a valid Sheets name"
                pr = parse_a1(rng)
                self.names[nm] = (sh["title"], *(pr if len(pr) == 4 else (*pr, *pr)))
        self.val, self.busy, self.done, self.ast, self.rcache = {}, set(), set(), {}, {}
        self.n_formulas = 0

    def formula_ast(self, f):
        if f not in self.ast:
            self.ast[f] = Parser(tokenize(f[1:]), f).parse()
        return self.ast[f]

    def cell(self, sh, r, c):
        key = (sh, r, c)
        if key in self.val:
            return self.val[key]
        raw = self.cells[sh].get((r, c))
        if raw is None:
            for (rr, cc), up in sorted(self.cells[sh].items(), key=lambda z: (-z[0][0], -z[0][1])):   # a 2-D spill from up-left
                if rr <= r and cc < c and isinstance(up, str) and up.startswith("=") and (sh, rr, cc) not in self.done:
                    self.cell(sh, rr, cc)
                    if key in self.val:
                        return self.val[key]
            for rr in range(r - 1, 0, -1):                      # a spill from a formula above in this column
                up = self.cells[sh].get((rr, c))
                if isinstance(up, str) and up.startswith("=") and (sh, rr, c) not in self.done:
                    self.cell(sh, rr, c)
                    if key in self.val:
                        return self.val[key]
                elif up is not None and not (isinstance(up, str) and up.startswith("=")):
                    break
            return None
        if isinstance(raw, str) and raw.startswith("="):
            if key in self.busy:
                raise SheetError(f"#REF! circular dependency at {sh}!{col_name(c)}{r}")
            self.busy.add(key)
            try:
                try:
                    res = self.ev(self.formula_ast(raw), {}, (sh, r, c))
                except SheetError as ex:
                    res = str(ex) if str(ex).startswith("#") else f"#ERROR {ex}"
            finally:
                self.busy.discard(key)
            self.done.add(key)
            if isinstance(res, np.ndarray):
                for i in range(res.shape[0]):
                    for j in range(res.shape[1]):
                        k2 = (sh, r + i, c + j)
                        if (i or j) and (self.cells[sh].get((r + i, c + j)) is not None or k2 in self.val):
                            raise SheetError(f"spill blocked at {sh}!{col_name(c + j)}{r + i}")
                        self.val[k2] = res[i, j]
                return self.val[key]
            self.val[key] = res
            return res
        self.val[key] = raw
        return raw

    def rng(self, sh, r1, c1, r2, c2):
        k = (sh, r1, c1, r2, c2)
        if k in self.rcache:
            return self.rcache[k]
        a = np.empty((r2 - r1 + 1, c2 - c1 + 1), dtype=object)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                v = self.cell(sh, r, c)
                a[r - r1, c - c1] = 0.0 if v is None else v
        self.rcache[k] = a
        return a

    def ref(self, txt, here):
        sh = here[0]
        if "!" in txt:
            sh, txt = txt.rsplit("!", 1)
            sh = sh.strip("'")
            if sh not in self.cells:
                raise SheetError(f"no sheet {sh}")
        pr = parse_a1(txt)
        if len(pr) == 2:
            v = self.cell(sh, *pr)
            return 0.0 if v is None else v
        return self.rng(sh, *pr)

    @staticmethod
    def num(x):
        if isinstance(x, np.ndarray):
            if x.dtype == object:
                try:
                    return x.astype(float)
                except (TypeError, ValueError):
                    first = next(z for z in x.ravel() if isinstance(z, str))
                    raise SheetError(first if first.startswith("#") else "#VALUE! text in arithmetic")
            return x
        if isinstance(x, str):
            raise SheetError(x if x.startswith("#") else f"#VALUE! text {x[:30]!r} in arithmetic")   # an error passes through as is
        return float(x)

    @staticmethod
    def flat(args):
        out = []
        for a in args:
            if isinstance(a, np.ndarray):
                out += [float(z) for z in a.ravel() if not isinstance(z, str)]
            elif not isinstance(a, str):
                out.append(float(a))
        return out

    def ev(self, n, env, here):
        k = n[0]
        if k == "num" or k == "str":
            return n[1]
        if k == "ref":
            return self.ref(n[1], here)
        if k == "name":
            if n[1] in env:
                return env[n[1]]
            if n[1] not in self.names:
                raise SheetError(f"#NAME? {n[1]}")
            sh, r1, c1, r2, c2 = self.names[n[1]]
            if (r1, c1) == (r2, c2):
                v = self.cell(sh, r1, c1)
                return 0.0 if v is None else v
            return self.rng(sh, r1, c1, r2, c2)
        if k == "neg":
            return -self.num(self.ev(n[1], env, here))
        if k == "bin":
            op = n[1]
            a, b = self.ev(n[2], env, here), self.ev(n[3], env, here)
            if not env.get("__arr__") and any(isinstance(z, np.ndarray) and z.size > 1 for z in (a, b)):
                raise SheetError("#VALUE! array arithmetic outside ARRAYFORMULA (Sheets reads one cell)")
            if op == "&":
                return f"{a}{b}"
            if op in ("=", "<>") and (isinstance(a, str) or isinstance(b, str)):
                return float((a == b) == (op == "="))
            a, b = self.num(a), self.num(b)
            with np.errstate(divide="ignore", invalid="ignore"):
                if op == "+":
                    r = a + b
                elif op == "-":
                    r = a - b
                elif op == "*":
                    r = a * b
                elif op == "/":
                    if np.any(np.asarray(b) == 0):
                        raise SheetError("#DIV/0!")
                    r = a / b
                elif op == "^":
                    r = np.power(a, b)
                else:
                    r = {"=": np.equal, "<>": np.not_equal, "<": np.less, ">": np.greater, "<=": np.less_equal,
                         ">=": np.greater_equal}[op](a, b).astype(float)
            if np.any(~np.isfinite(np.asarray(r, dtype=float))):
                raise SheetError("#NUM!")
            return r
        if k == "call":
            return self.call(n[1], n[2], env, here)
        raise SheetError(f"bad node {n}")

    def call(self, fn, args, env, here):
        E = lambda a: self.ev(a, env, here)
        if fn == "LAMBDA":
            params = [a[1] for a in args[:-1]]
            assert all(a[0] == "name" and not is_a1_like(a[1]) and a[1].lower() not in ("r", "c") for a in args[:-1]), args
            body = args[-1]
            return ("lambda", params, body, dict(env))
        if fn == "LET":
            e2 = dict(env)
            for i in range(0, len(args) - 1, 2):
                e2[args[i][1]] = self.ev(args[i + 1], e2, here)
            return self.ev(args[-1], e2, here)
        if fn in ("ARRAYFORMULA", "FILTER"):                 # array context: elementwise arithmetic is allowed
            env = {**env, "__arr__": True}
            E = lambda a: self.ev(a, env, here)
        if fn == "IF":
            c = E(args[0])
            if isinstance(c, np.ndarray):
                a = E(args[1])
                b = E(args[2]) if len(args) > 2 else 0.0
                return np.where(self.num(c) != 0, self.num(a), self.num(b))
            if isinstance(c, str):
                raise SheetError("#VALUE! IF on text")
            return E(args[1]) if c else (E(args[2]) if len(args) > 2 else 0.0)
        if fn == "IFERROR":
            try:
                v = E(args[0])
                if isinstance(v, str) and v.startswith("#"):
                    raise SheetError(v)
                return v
            except SheetError:
                return E(args[1])
        if fn == "ARRAYFORMULA":
            return E(args[0])
        vals = [E(a) for a in args]
        if fn in ("MIN", "MAX", "SUM", "AVERAGE"):
            f = self.flat(vals)
            if fn == "AVERAGE" and not f:
                raise SheetError("#DIV/0!")
            return {"MIN": min, "MAX": max, "SUM": sum, "AVERAGE": lambda z: sum(z) / len(z)}[fn](f) if f else 0.0
        if fn in ("AND", "OR"):
            f = [z != 0 for z in self.flat(vals)]
            return float(all(f) if fn == "AND" else any(f))
        if fn == "INT":
            return np.floor(self.num(vals[0]))
        if fn == "ABS":
            return np.abs(self.num(vals[0]))
        if fn == "MOD":
            a, b = self.num(vals[0]), self.num(vals[1])
            return a - b * np.floor(a / b)
        if fn == "ROUND":
            x, d = self.num(vals[0]), self.num(vals[1]) if len(vals) > 1 else 0.0
            return np.sign(x) * np.floor(np.abs(x) * 10 ** d + 0.5) / 10 ** d
        if fn == "ISNUMBER":
            return float(not isinstance(vals[0], str))
        if fn == "INDEX":
            a = vals[0]
            i = int(self.num(vals[1]))
            j = int(self.num(vals[2])) if len(vals) > 2 else None
            if not isinstance(a, np.ndarray):
                a = np.array([[a]], dtype=object)
            if j is None and a.shape[0] == 1 and a.shape[1] > 1:
                i, j = 1, i
            j = j or 1
            if i < 1 or j < 1 or i > a.shape[0] or j > a.shape[1]:
                raise SheetError(f"#REF! INDEX({i},{j}) outside {a.shape}")
            return a[i - 1, j - 1]
        if fn == "SEQUENCE":
            n_ = int(self.num(vals[0]))
            c_ = int(self.num(vals[1])) if len(vals) > 1 else 1
            st = self.num(vals[2]) if len(vals) > 2 else 1.0
            sp = self.num(vals[3]) if len(vals) > 3 else 1.0
            return (st + sp * np.arange(n_ * c_, dtype=float)).reshape(n_, c_)
        if fn == "ROUNDUP":
            x_, d_ = self.num(vals[0]), self.num(vals[1]) if len(vals) > 1 else 0.0
            return np.sign(x_) * np.ceil(np.abs(x_) * 10 ** d_ - 1e-12) / 10 ** d_
        if fn == "ROWS":
            return float(vals[0].shape[0]) if isinstance(vals[0], np.ndarray) else 1.0
        if fn == "MATCH":
            mode = int(self.num(vals[2])) if len(vals) > 2 else 1
            if isinstance(vals[0], str) and mode == 0:            # exact text match, case-insensitive (as Sheets)
                arr_ = vals[1].ravel() if isinstance(vals[1], np.ndarray) else np.array([vals[1]], dtype=object)
                hits = [i for i, z in enumerate(arr_) if isinstance(z, str) and z.lower() == vals[0].lower()]
                if not hits:
                    raise SheetError("#N/A MATCH")
                return float(hits[0] + 1)
            key_, arr = self.num(vals[0]), self.num(vals[1]).ravel()
            if mode == 0:
                hits = np.nonzero(arr == key_)[0]
            else:
                hits = np.nonzero(arr <= key_)[0][-1:]
            if hits.size == 0:
                raise SheetError("#N/A MATCH")
            return float(hits[0] + 1)
        if fn == "SUMIFS":
            tot, ok = self.num(vals[0]), np.ones(vals[0].shape, bool)
            for i in range(1, len(vals), 2):
                ok &= self.num(vals[i]) == self.num(vals[i + 1])
            return float(tot[ok].sum())
        if fn == "MMULT":
            a, b = self.num(vals[0]), self.num(vals[1])
            if a.shape[1] != b.shape[0]:
                raise SheetError("#VALUE! MMULT shapes")
            return a @ b
        if fn == "MAKEARRAY":
            nr, nc, lam = int(self.num(vals[0])), int(self.num(vals[1])), vals[2]
            assert lam[0] == "lambda" and len(lam[1]) == 2
            out = np.zeros((nr, nc))
            for i in range(nr):
                for j in range(nc):
                    out[i, j] = self.num(self.ev(lam[2], {**lam[3], lam[1][0]: float(i + 1), lam[1][1]: float(j + 1)}, here))
            return out
        if fn == "SCAN":
            acc, arr, lam = vals[0], self.num(vals[1]), vals[2]
            assert lam[0] == "lambda" and len(lam[1]) == 2
            out = np.zeros(arr.shape)
            for idx in np.ndindex(arr.shape):
                acc = self.num(self.ev(lam[2], {**lam[3], lam[1][0]: acc, lam[1][1]: float(arr[idx])}, here))
                out[idx] = acc
            return out
        if fn == "FILTER":
            a, c = vals[0], self.num(vals[1])
            sel = a[c.ravel() != 0]
            if sel.size == 0:
                raise SheetError("#N/A FILTER empty")
            return sel.reshape(-1, a.shape[1])
        raise SheetError(f"function {fn} not implemented")

    def evaluate_all(self):
        errs = []
        for sh, cells in self.cells.items():
            for (r, c), raw in cells.items():
                if isinstance(raw, str) and raw.startswith("="):
                    self.n_formulas += 1
                    v = self.cell(sh, r, c)
                    if isinstance(v, str) and v.startswith("#"):
                        errs.append(f"{sh}!{col_name(c)}{r}: {v}")
        return errs


def replay(spec_path=SPEC):
    spec = json.loads(Path(spec_path).read_text())
    book = Book(spec)
    errs = book.evaluate_all()
    return book, errs


# ---------------------------------------------------------------- main
def write(name, rows):
    with (T / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def reconcile():
    """Toy vs the full engine at the likely values -> (inputs, toy monthly, engine result, toy_vs_full rows, Summary expected)."""
    v = likely_toy_inputs()
    x = ce.likely_inputs()
    res = full_run(x)
    tm = toy(v)["m"]
    # 1. with calendar growth off the toy equals the full engine on loans, top-ups, cards and housing
    t0 = toy({**v, "takeup_growth": 0.0, "approval_growth": 0.0})["m"]
    f0 = ce.run({**x, "takeup_growth": 0.0, "approval_growth": 0.0})["monthly"]
    for a, b in (("savers", "still_saving"), ("balance", "balance"), ("loans", "loans"), ("topups", "topups"), ("lent", "money_lent"),
                 ("cards", "cards")):
        assert np.allclose(t0[a], f0[b][0], rtol=1e-9, atol=1e-9), a
    assert np.allclose(t0["r_house"], f0["rev_xs_loan_home"][0] + f0["rev_xs_loan_lap"][0], rtol=1e-9)
    # 2. reconciliation
    rows = []
    gap_note = {
        "Cumulative P&L at month 36": "lumped cross-sell grows 20% for each full year saved; the full model's builds up "
                                      "product by product (the % reads large because cumulative P&L is near 0 at month 36)",
        "Peak cash need (lowest cumulative P&L)": "cross-sell timing (see month 36)",
        "Collection fees": "one fee paid 12 months after the loan (full model: 9 and 18 months)",
        "Money lent in year 5 (first, repeat and top-up loans)": "calendar growth approximated with the pool adjustment",
        "Loans made in year 5 (first and repeat)": "calendar growth approximated with the pool adjustment",
    }
    expected = []
    for i, (label, ft, ff, kind) in enumerate(SUMMARY, start=2):
        if label is None or kind == "head":
            continue
        tv, fv = ft(tm), float(ff(res))
        expected.append({"cell": f"Summary!B{i}", "measure": label, "expected": tv})
        if isinstance(tv, str):
            gap, gp = "", ""
        else:
            gap, gp = tv - fv, (tv - fv) / abs(fv) if fv else ""
        if label in ("Cumulative P&L at month 36", "Cumulative P&L at month 60", "Payback month (cumulative P&L stays at or above 0 from here)",
                     "Peak cash need (lowest cumulative P&L)", "Savers still saving, year-5 average (months 49-60)", "Money lent in 60 months",
                     "Money lent in year 5 (first, repeat and top-up loans)", "Loans made in year 5 (first and repeat)", "Cumulative P&L at month 12",
                     "Revenue per active saver a year (60-month average)", "Collection fees", "Income", "Costs",
                     "  of the costs: online leads, 60 months", "  of the costs: extra cash-collection capacity (helpers), 60 months"):
            rows.append({"measure": label, "toy": tv, "full_model": fv, "gap": gap, "gap_pct": gp, "why": gap_note.get(label, "")})
    return v, tm, res, rows, expected


def main():
    v, tm, res, rows, expected = reconcile()
    write("toy_expected.csv", expected)
    write("toy_vs_full.csv", rows)
    c60 = next(r for r in rows if r["measure"] == "Cumulative P&L at month 60")
    assert abs(c60["gap_pct"]) <= 0.05, c60
    print(f"xs_other calibrated: Rs {v['xs_other']} per active saver a year (full model booked: "
          f"Rs {full_nonhousing(res) / (res['monthly']['still_saving'][0].sum() / 12):.1f}); collections per loan Rs {v['coll_per_loan']}")
    for r in rows:
        g, tv = r["gap_pct"], r["toy"]
        tvs = tv if isinstance(tv, str) else f"{tv:>14,.1f}"
        print(f"  {r['measure'][:58]:<58} toy {tvs:>14} full {r['full_model']:>14,.1f}  gap {'' if g == '' else f'{g:+.2%}'}")
    # 3. formula replay
    if SPEC.exists():
        book, errs = replay()
        assert not errs, errs[:10]
        bad = []
        for e in expected:
            r_, c_ = parse_a1(e["cell"].split("!")[1])
            got = book.cell("Summary", r_, c_)
            want = e["expected"]
            ok = got == want if isinstance(want, str) else (not isinstance(got, str) and abs(got - want) <= 1e-9 * max(1.0, abs(want)))
            if not ok:
                bad.append((e["cell"], e["measure"], got, want))
        assert not bad, bad
        # every Monthly line against numpy
        mcols = json.loads(SPEC.read_text())["_monthly_columns"]
        for key, col in mcols.items():
            got = np.array([float(book.cell("Monthly", r_, col_num(col))) for r_ in range(2, N + 2)])
            assert np.allclose(got, tm[key], rtol=1e-9, atol=1e-9), key
        print(f"formula replay: {book.n_formulas} formulas evaluated, 0 errors; {len(expected)} Summary cells and "
              f"{len(mcols)} Monthly lines equal the numpy toy")
        # the same away from the likely values: caps binding, marketplace from month 7, no ramp, extra capacity, no growth
        spec = json.loads(SPEC.read_text())
        at = next(s for s in spec["sheets"] if s["title"] == "Inputs")["named_ranges"]
        for ch in ({"approved_first": 0.5, "approval_growth": 0.2, "takeup_growth": 0.25, "mkt_from": 7},
                   {"ramp": 0.0, "tenure": 30.4, "signups": 60.0, "capacity": 300.0},
                   {"takeup_growth": 0.0, "approval_growth": 0.0, "rollover": 0.6, "upi_m12": 0.1}):
            s2 = json.loads(SPEC.read_text())
            c2 = next(s for s in s2["sheets"] if s["title"] == "Inputs")["cells"]
            c2.update({at[k]: val for k, val in ch.items()})
            b2 = Book(s2)
            assert not b2.evaluate_all(), ch
            m2 = toy({**v, **ch})["m"]
            for key, col in mcols.items():
                got = np.array([float(b2.cell("Monthly", r_, col_num(col))) for r_ in range(2, N + 2)])
                assert np.allclose(got, m2[key], rtol=1e-9, atol=1e-9), (ch, key)
        print("formula replay at 3 other input sets (caps binding, month-7 marketplace, no ramp, extra capacity): equal")
    return v, tm, res, rows, expected


if __name__ == "__main__":
    main()

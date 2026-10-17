"""Company model: from one agent's unit economics (model/cohort_engine.py) to company financial statements, 60 company months.

Operator, 17 Oct 2026: "Assume we create a company and have online + offline channel spend every month. Lets say we want to raise
$1m for seed ... in next 18 months do a bigger round. So how many people to hire which department, app cost, etc... we should
model everything" / "company financials with year level numbers and licence costs etc" / "bake in all other small to big costs" /
"i can look at my cm1,2,3 and revenue and ebitda and pat over month on month and rollup numbers and cashflow numbers".
Spec: story/BRIEF_company_model_2026-10-17.md, story/BRIEF_company_model_addendum_cm_ladder_2026-10-17.md (the CM ladder, the
agent-cost split, capex, the cash-flow statement), story/FIXES_company_round1_2026-10-17.md (scale costs, interest on cash,
licences, agent raises, the decline on the book's age, the Series A tests, the fleet scenarios) and
story/CHANGES_round10_company_base_2026-10-17.md (the base becomes the plan the operator chose: 80 agents by m18, then replace
leavers; pay on balance capped at Rs 10,000 a month; central lean hold; UPI 30%; Series A Rs 50 crore, operator: "50cr for
sure"). Later documents win.
Metric: undiscounted cumulative P&L and cash (no NPV).

How it works
  1. THE SAVER, from the agent unit. cohort_engine.age_profile() gives every line per sign-up over ages 1..60. Sign-ups made in
     company month m get the profile with cohort = m, so the pool-history inputs (take-up and approvals growing each company
     year, addendum 4) run on COMPANY calendar time. All agents share these profiles within a draw (market inputs are common).
  2. THE FLEET (round 10 base). Grow to 80 agents by m18 on the earlier ramp scaled to 80 (m3 7, m6 13, m9 27, m12 40, m15 60,
     m18 80; linear between, whole agents), then hire only to replace leavers. The earlier 60 -> 300 path is kept as the "growth
     plan" scenario. A growth hire opens a "book". 30% of agents leave a year, read as leavers in a
     year / average agents, so 2.5% a month, tracked in whole agents; who leaves is drawn at random (fixed seed). A leaver goes
     at the end of his month; his replacement starts the next month, inherits the book (10% of its savers stop at the handover).
  3. SIGN-UPS. Each agent draws his own signups_run and signup_decline_y5. His sign-ups in month t = signups_run x the ramp on HIS
     tenure (a replacement restarts the ramp) x the decline on the BOOK's age (fix 5: the decline reflects how busy the book keeps
     him, so a replacement inherits it). Both factors come from cohort_engine.signups(); for an agent who opened his own book
     they are the engine's sign-ups exactly.
  4. STACKING. A book's sign-ups in company month m are S_k(m). The handover factor f_k(t) = 0.9 ^ (handovers in book k before
     month t), so a cohort made in m carries f_k(t) / f_k(m) in month t. The company total of any per-sign-up line is
     sum over m <= t of B(m, t) x profile_m(t - m + 1),  B(m, t) = sum_k S_k(m) f_k(t) / f_k(m). Cash visits, balance and cash
     collected are worked per book the same way: helpers above each agent's capacity, the 0.25% pay on balance to whoever holds
     the book, and cash cover per agent.
  5. THE FEE RAMP (round 9) multiplies origination in company month t: fee x (1 + 0.5 (t - 1) / 59), on first and repeat loans
     and top-ups (paid at disbursal and linear in money lent, so exact on the month's company line).
  6. HIRING ORDER. Hire k always gets the k-th sign-up draw and leavers come from their own stream (make_fleet), so a change in
     later hiring never changes an earlier month; the plan triggers (lean hold ends; hiring doubles) rely on it (run_plan).

The P&L ladder (addendum): transaction -> serve -> acquire
  revenue      fund trail; personal-loan origination; top-ups; housing loans (home, LAP); other lenders' loans (gold, consumer,
               vehicle); cards; insurance (after the broker's share); investments (SIP, Choti SIP, NPS, digital gold, FD);
               payments (recharge, bills); collection fees (31-90 and 90+ days). Net of fees taken back; GST passes through.
  - direct     bureau pulls Rs 25 per personal-loan application and top-up (other lenders pull their own); fraud provision 0.05%
               of cash collected (deposits x the cash share, per cohort).                                         = CM1
  - servicing  the servicing share of agent cost (salary + pay on balance + Rs 3,000 statutory); helpers; cash cover = the larger
               of Rs 1,000 or 0.015% of the cash he collects, per agent a month (fix 1); running cost Rs 5 a saver; team
               leads; city managers; city offices.                                                                 = CM2
  - acquire    the acquisition share of agent cost; online leads; KYC; hiring kit Rs 12,000 per hire (replacements too); city
               launch Rs 3 lakh; brand marketing Rs 2 lakh a month.                                                = CM3
  - central    central team pay (+10% statutory, 7% raises each company year), including the scale roles of fix 1 (risk and
               fraud lead Rs 1.5 lakh from the month the fleet reaches 100 agents; cash reconciliation Rs 35,000 per 50 agents;
               HR and recruiting Rs 50,000 per 100 agents, both rounded up from the first agent; customer support lead Rs 60,000
               from the month the company has 50,000 savers); app cloud, SMS and KYC tools Rs 1.5 lakh a month; licences yearly
               Rs 10 lakh and one-time Rs 7.5 lakh (fix 3; expensed, month 1); HQ; travel; tools Rs 1,000 a central person;
               fund-raising costs when incurred; 10% contingency on every expensed line above it.             = EBITDA
  - depreciation  laptops (Rs 60,000 per central hire) and integrations (Rs 15 lakh over months 1-3), straight line over 36
               months from the month bought.                                                                       = EBIT
  + interest   5.5% a year (/12 a month) on the cash at the start of each month (the seed lands at m0, so month 1 earns on it;
               the Series A lands at the end of its month); no interest on a negative balance (fix 2).            = profit before tax
  - tax        25% of positive profit before tax after past losses, month by month, losses carried forward; paid in the month
               booked.                                                                                             = PAT
  Agent cost split: for each agent, by HIS tenure month k, acquisition share 50% for k = 1-12, then a straight line to 20% at
  k = 60; the rest is servicing; a replacement restarts at k = 1. Agent salary and statutory rise 7% each company year (fix 4;
  the statutory follows the pay). Pay on balance (round 10): 0.25% a year of his book's balance, capped at incentive_cap
  (Rs 10,000 a month per agent, the agreed key), the cap rising 7% a year with the salary.
  Central lean hold (round 10 base): after the launch team, no central hires until EBITDA first turns positive (engineer and ops
  scale-ups, risk lead, support lead wait), except the cash-reconciliation and HR executives that scale per agent; from the month
  after, the normal rules apply.

Cash flow: operating = PAT + depreciation - increase in commissions receivable (revenue arrives 2 months after it is earned)
+ (tax booked - tax paid = 0); investing = - laptops and integrations; financing = seed Rs 10 crore at m0 (shown in month 1)
+ Series A Rs 50 crore at the end of month 18 (operator, 17 Oct; its Rs 15 lakh cost sits in central costs, in the month it
closes).

Series A tests (fix 7), on the same operating lines with only the funding changed (treasury()):
  seed only        no Series A: the first month the month-end cash goes below 0 ("the seed runs out").
  close by month N the latest month the A (Rs 50 crore, Rs 15 lakh cost booked that month) can land at the end of without the
                   cash going below 0 in any month before it arrives.
  slips            the A at the end of month 21 and of month 24: the lowest month-end cash through month 60.
  smallest A       the smallest A at month 18 that keeps month-end cash at or above Rs 5 crore from month 18 to month 60 (by
                   bisection; months 1-17 are seed only, whatever the A).

Approximations: the 10% handover loss scales every later line of the inherited cohorts, including collection fees on loans made
before the handover (slightly understated); leaver counts are the expected rate in whole agents; the fee multiplier is held at
1.5x after company month 60 only in the run() offset check.

Writes tables/company_monthly.csv, company_yearly.csv, company_pnl_ladder_yearly.csv, company_cashflow_yearly.csv,
company_headcount.csv, company_m18.csv, company_fleet_scenarios.csv, company_breakeven_customers.csv, company_checks.csv and
company_README.md.
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import cohort_mc as MC             # noqa: E402  (ppf only)

T = E.T
M = 60
YEARS = 5
YEAR_CAP_AFTER_60 = 5            # 120-month runs: pool-history multipliers held at their month-60 (year-5) values


def set_horizon(months):
    """60 (the default) or 120 (BRIEF_growth_and_100m Part B). Beyond month 60: the take-up and approval growth held at year 5,
    the fee multiplier held at 1.5x, the agent pay rate 0.10% (cohort_engine's agreed rule after company month 60)."""
    global M, YEARS
    M, YEARS = int(months), int(months) // 12
SEED = 20261017
LAKH, CRORE = 1e5, 1e7

# ---------------------------------------------------------------- company inputs (brief, addendum and fix round 1, 17 Oct 2026)
GROWTH_POINTS = ((0, 0), (3, 5), (6, 10), (9, 20), (12, 30), (15, 45), (18, 60), (36, 150), (60, 300))   # the earlier base
BASE_A18, BASE_CENTRAL = 80, "lean hold"                                                            # round 10 base
FLEET_POINTS = tuple((m, n * BASE_A18 / 60) for m, n in GROWTH_POINTS[:7]) + ((60, BASE_A18),)
FLEET_SCENARIOS = (("Base: 80 agents by m18, then replace leavers", FLEET_POINTS, BASE_CENTRAL),
                   ("Growth plan: 60 agents at m18, growing to 300 by m60 (the earlier base)", GROWTH_POINTS, "as built"),
                   ("Hiring frozen at 60 agents after m18", GROWTH_POINTS[:7] + ((60, 60),), "as built"))
ATTRITION_YEAR = 0.30
HANDOVER_LOSS = 0.10
ACQ_SHARE_EARLY, ACQ_SHARE_M60, ACQ_FLAT_MONTHS = 0.50, 0.20, 12
CITY_LAUNCH, CITY_OFFICE, CITY_MANAGER_PAY, TEAM_LEAD_PAY = 3 * LAKH, 50000.0, 80000.0, 40000.0
AGENTS_PER_TEAM_LEAD, AGENTS_PER_CITY = 10, 50
CITY_STEPS = ((1, 1), (9, 2), (18, 3))           # (from month, cities); from month 18 also max(3, ceil(agents / 50))
CENTRAL = (  # role, department, pay a month in year-1 terms, ((from month, count), ...), +1 per 50 agents beyond 60 after m18
    ("Founders", "Founders", 1.5 * LAKH, ((1, 2),), False),
    ("Tech lead", "Technology", 2.5 * LAKH, ((1, 1),), False),
    ("Engineers", "Technology", 1.2 * LAKH, ((1, 2), (3, 3)), True),
    ("Product and design", "Technology", 1.5 * LAKH, ((2, 1),), False),
    ("Compliance and operations head", "Compliance and operations", 1.5 * LAKH, ((1, 1),), False),
    ("Operations executives", "Compliance and operations", 40000.0, ((3, 2),), True),
    ("Growth and marketing", "Growth and marketing", 1.2 * LAKH, ((3, 1),), False),
    ("Finance and admin", "Finance and admin", 70000.0, ((1, 1),), False),
)
SCALE_ROLES = (  # fix 1, operator "Add as proposed": role, department, pay a month in year-1 terms, rule
    ("Risk and fraud lead", "Risk and cash reconciliation", 1.5 * LAKH, "from the month the fleet reaches 100 agents"),
    ("Cash reconciliation executives", "Risk and cash reconciliation", 35000.0, "1 per 50 agents, rounded up from the first agent"),
    ("HR and recruiting executives", "HR and recruiting", 50000.0, "1 per 100 agents, rounded up from the first agent"),
    ("Customer support lead", "Customer support", 60000.0, "from the month the company has 50,000 savers"),
)
ALL_ROLES = tuple((r, d, p) for r, d, p, *_ in CENTRAL + SCALE_ROLES)
RISK_LEAD_AGENTS, CASH_REC_PER, HR_PER, SUPPORT_LEAD_SAVERS = 100, 50, 100, 50000
DEPARTMENTS = ("Founders", "Technology", "Compliance and operations", "Risk and cash reconciliation", "HR and recruiting",
               "Customer support", "Growth and marketing", "Finance and admin")
SCALE_AFTER, SCALE_BASE_AGENTS, SCALE_PER_AGENTS = 18, 60, 50
STATUTORY, RAISE, LAPTOP, TOOLS = 0.10, 0.07, 60000.0, 1000.0
AGENT_STATUTORY, AGENT_KIT = 3000.0, 12000.0
CASH_COVER_RATE = 0.00015                         # fix 1: cash cover = max(Rs 1,000, 0.015% of his cash collected), a month
APP_BASE, INTEGRATIONS, INTEGRATION_MONTHS = 1.5 * LAKH, 15 * LAKH, (1, 2, 3)
DEPRECIATION_MONTHS = 36
LICENCE_ONE_TIME = (("Company setup", 1 * LAKH), ("AMFI ARN and NISM", 0.5 * LAKH), ("Legal opinion on the cash route", 6 * LAKH))
LICENCE_YEARLY = (("Audit, CA and secretarial", 5 * LAKH), ("Infosec and DPDP", 3 * LAKH), ("Insurance and misc", 2 * LAKH))
HQ, TRAVEL, BRAND = 1.5 * LAKH, 1 * LAKH, 2 * LAKH
BUREAU, FRAUD, UPI_FEE = 25.0, 0.0005, 0.0
COMMISSION_LAG, TAX, CONTINGENCY = 2, 0.25, 0.10
INTEREST_RATE = 0.055                             # fix 2: a year, on the opening cash, /12 a month
SEED_ROUND, SEED_COST = 10 * CRORE, 5 * LAKH
SERIES_A, SERIES_A_COST, SERIES_A_MONTH = 50 * CRORE, 15 * LAKH, 18          # operator 17 Oct: "50cr for sure"
SLIP_MONTHS = (21, 24)
CASH_FLOOR_AFTER_A = 5 * CRORE                    # the smallest-A test
A_SEARCH_MAX, A_SEARCH_STEPS = 500 * CRORE, 34

INSURANCE = E.INSURANCE
INVESTMENTS = ("sip", "choti", "nps", "gold", "fd")
PAYMENTS = ("recharge", "bills")
HOUSING = ("loan_home", "loan_lap")
OTHER_LENDERS = ("loan_gold", "loan_cd", "loan_vehicle")
assert sorted(INSURANCE + INVESTMENTS + PAYMENTS + HOUSING + OTHER_LENDERS) == sorted(p for p, *_ in E.PRODUCTS)
PROFILE_LINES = ("still_saving", "fund_end", "balance", "deposits", "cash_deposits", "cash_visits_a_day", "applications", "topups",
                 "loans", "money_lent", "housing_lent", "rev_fund", "rev_orig_loans", "rev_orig_topups", "rev_housing",
                 "rev_other_lenders", "rev_cards", "rev_insurance", "rev_investments", "rev_payments", "rev_collections",
                 "income", "cost_kyc", "cost_support", "rev_dpd31_90", "rev_recovery90")   # the last two: the NBFC layer
REVENUE = (("rev_fund", "Fund trail"), ("rev_orig_loans", "Personal-loan origination (first and repeat loans)"),
           ("rev_orig_topups", "Top-up origination"), ("rev_housing", "Housing loans (home loans and LAP, other lenders)"),
           ("rev_other_lenders", "Other lenders' loans (gold, consumer, vehicle)"), ("rev_cards", "Cards"),
           ("rev_insurance", "Insurance (after the broker's share)"), ("rev_investments", "Investments (SIP, Choti SIP, NPS, digital gold, FD)"),
           ("rev_payments", "Payments (recharge, bills)"), ("rev_collections", "Collection fees (31-90 and 90+ days late)"))
DIRECT = (("cost_bureau", "Bureau pulls"), ("cost_fraud", "Fraud provision on cash collected"))
SERVICING = (("cost_agent_serv", "Agent cost, servicing share (salary, pay on balance, statutory)"),
             ("cost_helpers", "Helpers for cash visits above capacity"),
             ("cost_cash_cover", "Cash cover insurance (larger of Rs 1,000 or 0.015% of his cash, per agent)"),
             ("cost_support", "Running cost, Rs 5 a saver a month"), ("cost_team_leads", "Team leads, incl. statutory"),
             ("cost_city_managers", "City managers, incl. statutory"), ("cost_city_offices", "City offices"))
ACQUISITION = (("cost_agent_acq", "Agent cost, acquisition share"), ("cost_leads", "Online leads"), ("cost_kyc", "KYC"),
               ("cost_agent_kit", "Agent hiring and kit"), ("cost_city_launch", "City launch"), ("cost_brand", "Brand marketing"))
CENTRAL_COSTS = (*[(f"pay_{d}", f"Central team, {d.lower()}: pay incl. statutory") for d in DEPARTMENTS],
                 ("cost_app", "App cloud, SMS and KYC tools"), ("cost_licences_yearly", "Licences and compliance, yearly"),
                 ("cost_licences_once", "Licences and setup, one-time"), ("cost_hq", "Head office"), ("cost_travel", "Travel"),
                 ("cost_tools", "Tools for the central team"), ("cost_raise", "Fund-raising costs"))
DEPRECIATION = (("dep_laptops", "Depreciation: laptops"), ("dep_integrations", "Depreciation: app integrations"))


# ---------------------------------------------------------------- fleet
def fleet_target(points=FLEET_POINTS):
    """Agents working in company months 0..M (index = month), whole agents."""
    xs, ys = zip(*points)
    return np.floor(np.interp(np.arange(M + 1), xs, ys) + 0.5).astype(int)


def leaver_counts(target):
    """Leavers at the end of months 1..M: the expected 2.5% a month of agents working, tracked in whole agents."""
    cum = np.cumsum(ATTRITION_YEAR / 12 * target[1:])
    return np.diff(np.floor(cum + 1e-9), prepend=0.0).astype(int)


def plan_target(a18, h, step_after=None):
    """Agents working in months 0..M: the earlier ramp to m18 scaled to a18, then +h a month (+2h after step_after)."""
    xs, ys = zip(*GROWTH_POINTS[:7])
    t = np.arange(M + 1)
    v = np.interp(np.minimum(t, 18), xs, np.asarray(ys, float) * a18 / 60.0)
    v = np.where(t > 18, a18 + h * (t - 18) + (h * np.maximum(0, t - step_after) if step_after else 0), v)
    return np.floor(v + 0.5).astype(int)


def make_fleet(dists, target=None, seed=SEED, signup_factor=1.0, leavers=None):
    """Hires (growth and replacement): book, start month, month he left (0 = still working at month 60), and his own draws.
    Hire k always gets the k-th draw and leavers come from their own stream, so fleets that share their hiring to month X share
    every month up to X. signup_factor: the MC's common (market-level) sign-up factor, on top of each agent's own draw."""
    target = fleet_target() if target is None else target
    leavers = leaver_counts(target) if leavers is None else leavers
    rl = np.random.default_rng(seed)
    slot, start, left, current = [], [], [], []
    for t in range(1, M + 1):
        for _ in range(int(target[t] - target[t - 1])):
            current.append(len(start))
            slot.append(len(current) - 1)
            start.append(t)
            left.append(0)
        k = int(leavers[t - 1])
        if k:
            for s_ in rl.choice(len(current), size=k, replace=False):
                left[current[s_]] = t
                if t < M:                                  # the replacement starts next month and inherits the book
                    current[s_] = len(start)
                    slot.append(int(s_))
                    start.append(t + 1)
                    left.append(0)
    H = len(start)
    U = np.random.default_rng(seed + 1).random((H, 2))          # row k = hire k's draws, whatever the fleet size
    return {"slot": np.array(slot), "start": np.array(start), "left": np.array(left), "slots": len(current),
            "signups_run": MC.ppf(*dists["signups_run"][:4], U[:H, 0]) * signup_factor,
            "signup_decline_y5": MC.ppf(*dists["signup_decline_y5"][:4], U[:H, 1])}


def one_agent_fleet(x, start=1):
    """The reconciliation fleet: one agent at the likely sign-ups, hired in `start`, who never leaves."""
    return {"slot": np.array([0]), "start": np.array([start]), "left": np.array([0]), "slots": 1,
            "signups_run": np.array([float(np.mean(x["signups_run"]))]),
            "signup_decline_y5": np.array([float(np.mean(x["signup_decline_y5"]))])}


def acquisition_share(k):
    """Share of an agent's cost that is acquisition, by his tenure month k (0 = no agent)."""
    k = np.asarray(k, float)
    s = np.where(k <= ACQ_FLAT_MONTHS, ACQ_SHARE_EARLY,
                 ACQ_SHARE_EARLY + (ACQ_SHARE_M60 - ACQ_SHARE_EARLY) * (np.minimum(k, 60) - ACQ_FLAT_MONTHS) / (60 - ACQ_FLAT_MONTHS))
    return np.where(k > 0, s, 0.0)


# ---------------------------------------------------------------- the saver, in company calendar time
def market_profiles(x, D):
    """Per-sign-up lines for sign-ups made in each company month, laid on the company calendar: (D, lines, m, t)."""
    C = M
    xr = {k: np.repeat(E._col(x, k, D), C) for k in x}
    coh = np.tile(np.arange(1, C + 1), D)                     # company month of the sign-up: pool-history multipliers
    pr = E.age_profile(xr, legacy=False, cohort=coh, ages=M, year_cap=YEAR_CAP_AFTER_60 if M > E.AGES else None)
    R = D * C
    col = lambda k: E._col(xr, k, R)[:, None]
    fee_net = col("fee") * (1 - col("taken_back"))
    pr["rev_orig_loans"] = pr["money_lent_new"] * fee_net                     # = rev_origination split (checked)
    pr["rev_orig_topups"] = (pr["money_lent"] - pr["money_lent_new"]) * fee_net
    pr["cash_deposits"] = pr["deposits"] * (1 - pr["upi_share"])
    pr["housing_lent"] = pr["takeups_loan_home"] * col("loan_home_ticket") + pr["takeups_loan_lap"] * col("loan_lap_ticket")
    grp = lambda ps: sum(pr[f"rev_xs_{p}"] for p in ps)
    pr["rev_insurance"], pr["rev_investments"], pr["rev_payments"] = grp(INSURANCE), grp(INVESTMENTS), grp(PAYMENTS)
    pr["rev_housing"], pr["rev_other_lenders"] = grp(HOUSING), grp(OTHER_LENDERS) + pr["rev_other_v2"]
    pr["rev_collections"] = pr["rev_dpd31_90"] + pr["rev_recovery90"]
    L = len(PROFILE_LINES)
    P = np.stack([pr[k] for k in PROFILE_LINES], axis=1).reshape(D, C, L, M).transpose(0, 2, 1, 3)
    Pc = np.zeros((D, L, C, M))
    for m in range(C):
        Pc[:, :, m, m:] = P[:, :, m, :M - m]
    return Pc


def book_open_month(f):
    op = np.full(f["slots"], M + 1)
    np.minimum.at(op, f["slot"], f["start"])
    return op


def hire_signups(f, ramp):
    """Each hire's sign-ups by company month: signups_run x the ramp on his tenure x the decline on his book's age (fix 5).
    Returns sign-ups (H, M), the working mask and his tenure month (0 when not working)."""
    H = len(f["start"])
    ones = np.ones(H)
    ramp_f = E.signups({"signups_run": ones, "ramp_months": np.full(H, float(ramp)), "signup_decline_y5": ones}, months=M)
    decl_f = E.signups({"signups_run": ones, "ramp_months": np.zeros(H), "signup_decline_y5": f["signup_decline_y5"]}, months=M)
    t = np.arange(1, M + 1)[None, :]
    tau = t - f["start"][:, None]                              # his tenure, 0-based
    age = t - book_open_month(f)[f["slot"]][:, None]           # the book's age, 0-based
    end = np.where(f["left"] > 0, f["left"], M)[:, None]
    ok = (tau >= 0) & (t <= end)
    pick = lambda a, i: np.take_along_axis(a, np.clip(i, 0, M - 1), axis=1)
    S = np.where(ok, f["signups_run"][:, None] * pick(ramp_f, tau) * pick(decl_f, age), 0.0)
    return S, ok, np.where(ok, tau + 1, 0)


def handover_factor(f):
    """f_k(t) = 0.9 ^ (handovers in book k at month ends before t)."""
    Hc = np.zeros((f["slots"], M))
    ho = (f["left"] > 0) & (f["left"] < M)
    np.add.at(Hc, (f["slot"][ho], f["left"][ho]), 1.0)         # left at the end of month e: counts from month e + 1 (index e)
    return (1 - HANDOVER_LOSS) ** np.cumsum(Hc, axis=1)


# ---------------------------------------------------------------- the company layer
# ---------------------------------------------------------------- the city layer (BRIEF_city_saturation_2026-10-17; default off)
SAT_CAP, SAT_OPEN_HEADROOM = 0.20, 5000.0


def saturate(f, base, sat):
    """Cities have limits. base: each hire's sign-ups by month before saturation (H, M). sat: {"addressable": (C,) people,
    "cap": 0.20, "open_headroom": 5,000, "shape": "linear" | "square" | "late", "refill": the pool's growth a year (0),
    "max_new_per_month": cities that may open in a month (None = no limit), and for the PLANNED mode "launch": (C,) months
    (the fleet then carries f["book_city"])}. Sensitivities (sat_sensitivity.py): "late" = full speed to half the cap, then a
    straight line to zero at the cap; refill grows every city's pool (and so its cap) by (1 + refill)^(months / 12).
    AUTO: books (growth hires) are placed in the open city with the most remaining headroom per agent, (20% x addressable -
    cumulative sign-ups) / (its agents + 1); when even the best is below open_headroom, the next city in rank order opens and
    takes him. A replacement inherits his book, so he stays in its city. PLANNED: each book's city is given.
    Sign-ups in a city in month t = his own sign-ups x max(0, 1 - penetration / cap) (linear; "square": 1 - (pen / cap)^2),
    penetration = the city's cumulative sign-ups to t-1 / addressable; a city never goes past its cap (scaled in the month).
    Returns the saturated sign-ups (H, M), the city of each book (K,) and the history (cumulative and monthly sign-ups by city,
    cities open by month)."""
    Aaddr = np.asarray(sat["addressable"], float)
    cap0 = sat.get("cap", SAT_CAP) * Aaddr
    cap = cap0
    X = float(sat.get("open_headroom", SAT_OPEN_HEADROOM))
    shape = sat.get("shape", "linear")
    refill = float(sat.get("refill", 0.0))
    max_new = sat.get("max_new_per_month")
    Cn, K = len(Aaddr), f["slots"]
    preset = f.get("book_city")
    city = np.full(K, -1) if preset is None else np.asarray(preset).copy()
    opened = book_open_month(f)
    order = np.argsort(opened, kind="stable")
    n = np.zeros(Cn)
    cum = np.zeros(Cn)
    S = np.zeros_like(base)
    cum_h, sig_h, open_h, cap_h = np.zeros((Cn, M)), np.zeros((Cn, M)), np.zeros(M), np.zeros((Cn, M))
    open_n, ptr = 0, 0
    launch = np.asarray(sat["launch"], float) if preset is not None else None
    slot = f["slot"]
    for t in range(M):
        if refill:
            cap = cap0 * (1 + refill) ** (t / 12)
        new_this_month = 0
        if preset is None:
            while ptr < K and opened[order[ptr]] == t + 1:
                k = order[ptr]
                ptr += 1
                if open_n == 0:
                    b = 0
                    open_n = 1
                else:
                    hpa = (cap[:open_n] - cum[:open_n]) / (n[:open_n] + 1)
                    b = int(np.argmax(hpa))
                    if hpa[b] < X and open_n < Cn and (max_new is None or new_this_month < max_new):
                        b = open_n
                        open_n += 1
                        new_this_month += 1
                city[k] = b
                n[b] += 1
            open_h[t] = open_n
        else:
            open_h[t] = float((launch <= t + 1).sum())
        hc = city[slot]
        valid = (hc >= 0) & (base[:, t] > 0)
        pen = np.divide(cum, cap, out=np.ones(Cn), where=cap > 0)
        fac = np.clip(1 - pen ** 2 if shape == "square" else (2 * (1 - pen) if shape == "late" else 1 - pen), 0.0, 1.0)
        st = np.where(valid, base[:, t] * fac[np.maximum(hc, 0)], 0.0)
        tot = np.bincount(hc[valid], st[valid], minlength=Cn)
        rem = np.maximum(0.0, cap - cum)
        sc = np.where(tot > rem, np.divide(rem, tot, out=np.zeros(Cn), where=tot > 0), 1.0)
        st = np.where(valid, st * sc[np.maximum(hc, 0)], 0.0)
        S[:, t] = st
        sig = np.bincount(hc[valid], st[valid], minlength=Cn)
        cum = cum + sig
        cum_h[:, t], sig_h[:, t] = cum, sig
        cap_h[:, t] = cap
    return S, city, {"cum": cum_h, "signups": sig_h, "open": open_h, "cap": cap, "cap_by_month": cap_h, "addressable": Aaddr}


def make_city_fleet(dists, city_targets, seed=SEED, signup_factor=1.0):
    """PLANNED mode: each city's own fleet (agents by month, (C, M + 1)), attrition and replacement inside the city; merged
    into one fleet with the city of each book."""
    parts, slot_off = [], 0
    for c in np.nonzero(np.asarray(city_targets).max(axis=1) > 0)[0]:
        fc = make_fleet(dists, np.asarray(city_targets[c]).astype(int), seed + 7919 * (int(c) + 1), signup_factor)
        parts.append((c, fc, slot_off))
        slot_off += fc["slots"]
    cat = lambda k: np.concatenate([fc[k] for _c, fc, _o in parts])
    return {"slot": np.concatenate([fc["slot"] + off for _c, fc, off in parts]), "start": cat("start"), "left": cat("left"),
            "slots": slot_off, "signups_run": cat("signups_run"), "signup_decline_y5": cat("signup_decline_y5"),
            "book_city": np.concatenate([np.full(fc["slots"], c) for c, fc, _o in parts])}


def raise_mult():
    return (1 + RAISE) ** (np.arange(M) // 12)


def cities_by_month(agents):
    t = np.arange(1, M + 1)
    c = np.zeros(M)
    for frm, n in CITY_STEPS:
        c = np.where(t >= frm, n, c)
    return np.where(t >= CITY_STEPS[-1][0], np.maximum(c, np.ceil(agents / AGENTS_PER_CITY)), c)


def central_headcount(agents, savers, freeze_after=None, hold_until=None):
    """{role: (M,) headcount}. freeze_after: hold every central role at its size in that month (the levers).
    hold_until (the plan's "lean hold"): no central hires beyond the launch team in months <= hold_until (engineer and ops
    scale-ups, risk lead, support lead), except the cash-reconciliation and HR executives that scale per agent."""
    t = np.arange(1, M + 1)
    extra = np.where(t > SCALE_AFTER, np.floor(np.maximum(0, agents - SCALE_BASE_AGENTS) / SCALE_PER_AGENTS), 0)
    if hold_until:
        extra = np.where(t <= hold_until, 0, extra)
    out = {}
    for role, _dep, _pay, steps, scales in CENTRAL:
        n = np.zeros(M)
        for frm, k in steps:
            n = np.where(t >= frm, k, n)
        out[role] = n + (extra if scales else 0)
    out["Risk and fraud lead"] = np.maximum.accumulate(agents >= RISK_LEAD_AGENTS).astype(float)
    out["Cash reconciliation executives"] = np.ceil(agents / CASH_REC_PER)
    out["HR and recruiting executives"] = np.ceil(agents / HR_PER)
    out["Customer support lead"] = np.maximum.accumulate(savers >= SUPPORT_LEAD_SAVERS).astype(float)
    if hold_until:
        for r in ("Risk and fraud lead", "Customer support lead"):
            out[r] = np.where(t <= hold_until, 0.0, out[r])
    if freeze_after:
        out = {r: np.where(t > freeze_after, n[freeze_after - 1], n) for r, n in out.items()}
    return out


def straight_line(capex, months=DEPRECIATION_MONTHS):
    """Depreciation from the month bought, over `months` months."""
    dep = np.zeros(M)
    for u in np.nonzero(capex)[0]:
        dep[u:u + months] += capex[u] / months
    return dep


def company_layer(agents, hired, savers, freeze_after=None, hold_until=None, cities=None):
    """Field management, central team, app, licences, overheads, capex: (M,) arrays. cities: the city layer's cities open by
    month (saturation on); default the city rule."""
    rm = raise_mult() * (1 + STATUTORY)
    t = np.arange(1, M + 1)
    o = {}
    cities = cities_by_month(agents) if cities is None else np.asarray(cities, float)
    o["cities"], o["city_managers"], o["team_leads"] = cities, cities.copy(), np.ceil(agents / AGENTS_PER_TEAM_LEAD)
    o["cost_city_managers"] = o["city_managers"] * CITY_MANAGER_PAY * rm
    o["cost_team_leads"] = o["team_leads"] * TEAM_LEAD_PAY * rm
    o["cost_city_offices"] = cities * CITY_OFFICE
    o["cost_city_launch"] = np.diff(cities, prepend=0.0) * CITY_LAUNCH
    hc = central_headcount(agents, savers, freeze_after, hold_until)
    o["roles"] = hc
    for dep in DEPARTMENTS:
        roles = [(r, p) for r, d, p in ALL_ROLES if d == dep]
        o[f"hc_{dep}"] = sum(hc[r] for r, _ in roles)
        o[f"pay_{dep}"] = sum(hc[r] * p for r, p in roles) * rm
        o[f"joiners_{dep}"] = sum(np.maximum(0, np.diff(hc[r], prepend=0.0)) for r, _ in roles)
    o["hc_central"] = sum(o[f"hc_{d}"] for d in DEPARTMENTS)
    o["cost_central_pay"] = sum(o[f"pay_{d}"] for d in DEPARTMENTS)
    o["cost_tools"] = o["hc_central"] * TOOLS
    o["capex_laptops"] = sum(o[f"joiners_{d}"] for d in DEPARTMENTS) * LAPTOP
    o["capex_integrations"] = np.where(np.isin(t, INTEGRATION_MONTHS), INTEGRATIONS / len(INTEGRATION_MONTHS), 0.0)
    o["dep_laptops"], o["dep_integrations"] = straight_line(o["capex_laptops"]), straight_line(o["capex_integrations"])
    o["cost_app"] = np.full(M, APP_BASE)
    o["cost_licences_once"] = np.where(t == 1, sum(v for _, v in LICENCE_ONE_TIME), 0.0)
    o["cost_licences_yearly"] = np.full(M, sum(v for _, v in LICENCE_YEARLY) / 12)
    o["cost_hq"], o["cost_travel"], o["cost_brand"] = np.full(M, HQ), np.full(M, TRAVEL), np.full(M, BRAND)
    o["cost_raise_seed"] = np.where(t == 1, SEED_COST, 0.0)
    o["cost_raise_a"] = np.where(t == SERIES_A_MONTH, SERIES_A_COST, 0.0)
    o["cost_raise"] = o["cost_raise_seed"] + o["cost_raise_a"]
    o["cost_agent_kit"] = hired * AGENT_KIT
    return o


DEFAULT_OPTS = {"contingency": CONTINGENCY, "freeze_central_after": None, "pay_months": E.GROWTH_MONTHS, "pay_after": E.AGENT_PAY_AFTER,
                "central_hold_until": None, "incentive_cap": "agreed", "saturation": None}


def simulate(x, fleets, keep=False, opts=None, profiles=None):
    """x: market inputs {key: scalar or (D,)}; fleets: one fleet per draw. Returns {line: (D, M)}.
    opts (the levers; the defaults are the base): contingency rate, freeze_central_after (month), pay_months / pay_after (the
    0.25% pay on balance runs in company months 1..pay_months, then pay_after), central_hold_until (month, or one per draw),
    incentive_cap ("agreed" = the agent unit's incentive_cap key when x has it; a number = that cap; None = uncapped; Rs a month
    per agent in year-1 terms, rising with the 7% raises).
    profiles: market_profiles(x, D) computed once and reused (the plan search)."""
    op = {**DEFAULT_OPTS, **(opts or {})}
    D = len(fleets)
    Pc = market_profiles(x, D) if profiles is None else profiles
    li = {k: i for i, k in enumerate(PROFILE_LINES)}
    g = lambda k: E._col(x, k, D)
    ramp, cap, ecc, cover = g("ramp_months"), g("capacity"), g("extra_capacity_cost"), g("cash_cover")
    t = np.arange(1, M + 1)[None, :]
    rmul = raise_mult()
    pay_rate = np.where(t <= op["pay_months"], g("agent_balance_pay")[:, None], op["pay_after"])
    capv = op["incentive_cap"]
    if isinstance(capv, str):
        capv = g("incentive_cap") if "incentive_cap" in x else None
    elif capv is not None:
        capv = np.full(D, float(capv))
    eng_inc = np.zeros((D, M))
    tot = np.zeros((D, len(PROFILE_LINES), M))
    z = lambda: np.zeros((D, M))
    helpers, signups, agents, hired, left, agent_acq, incentive, cash_cover = z(), z(), z(), z(), z(), z(), z(), z()
    extras, city_out = [], []
    for d, f in enumerate(fleets):
        Sc, ok, ten = hire_signups(f, ramp[d])
        if op["saturation"] is not None:
            sat_d = op["saturation"]
            if "pool_scale" in sat_d:                          # the MC: each draw's pool size (pert 6.5/7.0/7.7 crore)
                sat_d = {**sat_d, "addressable": np.asarray(sat_d["addressable"], float) * float(np.asarray(sat_d["pool_scale"])[d])}
            Sc, book_city, sat_h = saturate(f, Sc, sat_d)
        Sk, tenure = np.zeros((f["slots"], M)), np.zeros((f["slots"], M))
        np.add.at(Sk, f["slot"], Sc)
        np.add.at(tenure, f["slot"], ten)                      # one agent per book per month: his tenure month
        fk = handover_factor(f)
        A = Sk / fk
        B = A.T @ fk                                           # B(m, t) = sum_k S_k(m) f_k(t) / f_k(m)
        tot[d] = np.einsum("mt,lmt->lt", B, Pc[d])
        book = lambda line: fk * (A @ Pc[d, li[line]])         # a per-sign-up line, per book
        V, Bal, CD = book("cash_visits_a_day"), book("balance"), book("cash_deposits")
        helpers[d] = np.maximum(0.0, V - cap[d]).sum(axis=0) * ecc[d] / E.HELPER_VISITS
        cash_cover[d] = np.where(tenure > 0, np.maximum(cover[d], CASH_COVER_RATE * CD), 0.0).sum(axis=0)
        inc_k = pay_rate[d] / 12 * Bal
        if capv is not None:                                   # capped per agent (book) a month, rising with the raises
            eng_inc[d] = (np.minimum(inc_k, capv[d]) * (tenure > 0)).sum(axis=0)     # the engine's flat cap (reconciliation)
            inc_k = np.minimum(inc_k, capv[d] * rmul) * (tenure > 0)
        else:
            eng_inc[d] = inc_k.sum(axis=0)
        cost_k = (float(g("salary")[d]) + AGENT_STATUTORY) * rmul * (tenure > 0) + inc_k
        agent_acq[d] = (acquisition_share(tenure) * cost_k).sum(axis=0)
        incentive[d] = inc_k.sum(axis=0)
        signups[d] = Sc.sum(axis=0)
        agents[d] = ok.sum(axis=0)
        hired[d] = np.bincount(f["start"], minlength=M + 1)[1:]
        left[d] = np.bincount(f["left"][f["left"] > 0], minlength=M + 1)[1:]
        if keep:
            extras.append({"Sc": Sc, "fk": fk, "V": V, "Bal": Bal, "CD": CD, "tenure": tenure})
        if op["saturation"] is not None:                       # per-city lines, summed over the books in each city
            Cn = len(sat_h["cap"])
            byc = lambda arr: (lambda out: (np.add.at(out, book_city, arr), out)[1])(np.zeros((Cn, M)))
            hc = book_city[f["slot"]]
            agents_c = np.zeros((Cn, M))
            np.add.at(agents_c, hc, ok.astype(float))
            helpers_k = np.maximum(0.0, V - cap[d]) * ecc[d] / E.HELPER_VISITS
            cover_k = np.where(tenure > 0, np.maximum(cover[d], CASH_COVER_RATE * CD), 0.0)
            city_out.append({**sat_h, "book_city": book_city, "agents": agents_c, "savers": byc(book("still_saving")),
                             "aum": byc(book("fund_end")), "income": byc(book("income")),
                             "orig": byc(book("rev_orig_loans") + book("rev_orig_topups")),
                             "bureau": byc(BUREAU * (book("applications") + book("topups"))), "fraud": byc(FRAUD * CD),
                             "support": byc(book("cost_support")), "helpers": byc(helpers_k), "cover": byc(cover_k),
                             "agent_serv": byc(cost_k * (1 - acquisition_share(tenure)))})
        else:
            city_out.append(None)
    o = {k: tot[:, i] for k, i in li.items()}
    fs, fe = g("fee_mult_start")[:, None], g("fee_mult_end")[:, None]
    o["fee_multiplier"] = fs + (fe - fs) * (np.minimum(t, E.MONTHS) - 1) / (E.MONTHS - 1) + 0 * signups   # held after month 60
    o["income_before_ramp"] = o["income"]
    o["rev_orig_loans"] = o["rev_orig_loans"] * o["fee_multiplier"]
    o["rev_orig_topups"] = o["rev_orig_topups"] * o["fee_multiplier"]
    o["revenue"] = sum(o[k] for k, _ in REVENUE)
    o.update(signups=signups, agents=agents, hired=hired, left=left, cost_helpers=helpers, cost_incentive=incentive,
             cost_cash_cover=cash_cover)
    o["cost_salary"] = g("salary")[:, None] * rmul * agents
    o["cost_agent_statutory"] = AGENT_STATUTORY * rmul * agents
    o["cost_leads"] = (g("online_lead_share") * g("lead_cost"))[:, None] * signups
    # the agent unit exactly as cohort_engine.run() prices it (flat salary, flat cash cover): for the reconciliation only
    o["_eng_salary"] = g("salary")[:, None] * agents
    o["_eng_cash_cover"] = cover[:, None] * agents
    o["_eng_incentive"], o["_incentive_cap"] = eng_inc, capv
    o["_eng_net"] = o["revenue"] - (o["_eng_salary"] + o["cost_helpers"] + o["cost_kyc"] + o["cost_support"] + o["_eng_cash_cover"]
                                    + o["_eng_incentive"] + o["cost_leads"])
    o["cost_bureau"] = BUREAU * (o["applications"] + o["topups"])
    o["cost_fraud"] = FRAUD * o["cash_deposits"]
    hold = op["central_hold_until"]
    hold_d = list(hold) if isinstance(hold, (list, tuple, np.ndarray)) else [hold] * D
    lay = [company_layer(agents[d], hired[d], o["still_saving"][d], op["freeze_central_after"], hold_d[d],
                         None if city_out[d] is None else city_out[d]["open"]) for d in range(D)]
    for k in lay[0]:
        if k != "roles":
            o[k] = np.stack([l_[k] for l_ in lay])
    o["roles"] = {r: np.stack([l_["roles"][r] for l_ in lay]) for r in lay[0]["roles"]}
    o["agent_cost"] = o["cost_salary"] + o["cost_agent_statutory"] + o["cost_incentive"]
    o["cost_agent_acq"] = agent_acq
    o["cost_agent_serv"] = o["agent_cost"] - agent_acq
    # the ladder to EBITDA
    blk = lambda lines: sum(o[k] for k, _ in lines)
    o["direct"] = blk(DIRECT)
    o["cm1"] = o["revenue"] - o["direct"]
    o["servicing"] = blk(SERVICING)
    o["cm2"] = o["cm1"] - o["servicing"]
    o["acquisition"] = blk(ACQUISITION)
    o["cm3"] = o["cm2"] - o["acquisition"]
    o["_contingency"] = op["contingency"]
    o["cost_contingency"] = op["contingency"] * (o["direct"] + o["servicing"] + o["acquisition"] + blk(CENTRAL_COSTS))
    o["central"] = blk(CENTRAL_COSTS) + o["cost_contingency"]
    o["ebitda"] = o["cm3"] - o["central"]
    o["ebitda_ex_a"] = o["ebitda"] + (1 + op["contingency"]) * o["cost_raise_a"]     # for the funding tests
    if op["saturation"] is not None:
        rmc = raise_mult() * (1 + STATUTORY)
        for d, co in enumerate(city_out):
            co["revenue"] = co["income"] + co["orig"] * (o["fee_multiplier"][d] - 1)
            opened_c = (co["agents"].cumsum(axis=1) > 0) if "launch" not in op["saturation"] else (
                np.asarray(op["saturation"]["launch"], float)[:, None] <= np.arange(1, M + 1)[None, :])
            share = np.divide(co["agents"], o["agents"][d][None, :], out=np.zeros_like(co["agents"]), where=o["agents"][d][None, :] > 0)
            co["team_leads"] = share * o["cost_team_leads"][d][None, :]
            co["city_mgmt"] = opened_c * (CITY_MANAGER_PAY * rmc[None, :] + CITY_OFFICE)
            co["cm2"] = (co["revenue"] - co["bureau"] - co["fraud"] - co["agent_serv"] - co["helpers"] - co["cover"] - co["support"]
                         - co["team_leads"] - co["city_mgmt"])
        o["_city"] = city_out
    o["depreciation"] = blk(DEPRECIATION)
    o["ebit"] = o["ebitda"] - o["depreciation"]
    o["opex"] = o["direct"] + o["servicing"] + o["acquisition"] + o["central"]
    o["received"] = z()
    o["received"][:, COMMISSION_LAG:] = o["revenue"][:, :-COMMISSION_LAG]
    o["receivable"] = sum(np.pad(o["revenue"], ((0, 0), (j, 0)))[:, :M] for j in range(COMMISSION_LAG))
    o["cf_receivable"] = -np.diff(o["receivable"], axis=1, prepend=0.0)
    o["cf_capex_laptops"], o["cf_capex_integrations"] = -o["capex_laptops"], -o["capex_integrations"]
    o["cf_investing"] = o["cf_capex_laptops"] + o["cf_capex_integrations"]
    o.update(treasury(o))
    o["cash_seed_only"] = treasury(o, a_size=0.0)["cash"]
    o["burn"] = -(o["cf_operating"] + o["cf_investing"])
    if keep:
        o["_extras"], o["_Pc"] = extras, Pc
    return o


def treasury(o, a_size=None, a_month=None, seed_size=None, rounds=None):
    """Interest, tax, PAT and the cash flow for a funding plan, on the operating lines of o. a_size: scalar or (D,); defaults:
    SERIES_A at SERIES_A_MONTH and SEED_ROUND. rounds (staged funding): [(month, amount[, book_cost])] after the seed, each landing
    at the end of its month and costing SERIES_A_COST (+ contingency) there when its amount is > 0 (or book_cost is True); a_size
    and a_month are then ignored and cf_series_a holds every round."""
    a_size = SERIES_A if a_size is None else a_size
    a_month = SERIES_A_MONTH if a_month is None else a_month
    seed_amt = SEED_ROUND if seed_size is None else seed_size
    D = o["ebitda"].shape[0]
    t = np.arange(1, M + 1)[None, :]
    if rounds is None:
        a = np.broadcast_to(np.asarray(a_size, float).reshape(-1), (D,))[:, None]
        ebitda = o["ebitda_ex_a"] - (1 + o["_contingency"]) * SERIES_A_COST * ((t == a_month) & (a > 0))
        series_a = np.where(t == a_month, a, 0.0)
    else:
        ebitda, series_a = o["ebitda_ex_a"].copy(), np.zeros((D, M))
        for rd in rounds:
            m_, amt = rd[0], np.broadcast_to(np.asarray(rd[1], float).reshape(-1), (D,))[:, None]
            book = (amt > 0) | (len(rd) > 2 and bool(rd[2]))
            ebitda = ebitda - (1 + o["_contingency"]) * SERIES_A_COST * ((t == m_) & book)
            series_a = series_a + np.where(t == m_, amt, 0.0)
    ebit = ebitda - o["depreciation"]
    seed = np.zeros((D, M))
    seed[:, 0] = seed_amt
    fin = seed + series_a
    fx = o.get("cf_fin_extra")                                # NBFC borrowings (nbfc.py); absent everywhere else
    r = {k: np.zeros((D, M)) for k in ("interest", "pbt", "tax", "losses_carried", "pat", "cf_operating", "net_change", "cash")}
    pool, prev = np.zeros(D), np.zeros(D)
    for i in range(M):
        opening = prev + (seed_amt if i == 0 else 0.0)        # the seed lands at m0; the Series A at the end of its month
        r["interest"][:, i] = INTEREST_RATE / 12 * np.maximum(0.0, opening)
        p = ebit[:, i] + r["interest"][:, i]
        use = np.minimum(pool, np.maximum(p, 0.0))
        r["tax"][:, i] = TAX * np.maximum(0.0, p - use)
        pool = pool - use + np.maximum(0.0, -p)
        r["losses_carried"][:, i] = pool
        r["pbt"][:, i] = p
        r["pat"][:, i] = p - r["tax"][:, i]
        r["cf_operating"][:, i] = r["pat"][:, i] + o["depreciation"][:, i] + o["cf_receivable"][:, i]
        r["net_change"][:, i] = r["cf_operating"][:, i] + o["cf_investing"][:, i] + fin[:, i] + (fx[:, i] if fx is not None else 0.0)
        prev = prev + r["net_change"][:, i]
        r["cash"][:, i] = prev
    r["cf_tax_timing"] = r["tax"] - r["tax"]                   # tax is paid in the month it is booked
    if fx is not None:
        r["cf_borrowings"] = fx
    r.update(cf_seed=seed, cf_series_a=series_a, cf_financing=fin, cum_pat=np.cumsum(r["pat"], axis=1),
             opening_cash=r["cash"] - r["net_change"], ebit_plan=ebit)
    return r


def first_positive(e):
    return np.where((e > 0).any(axis=1), (e > 0).argmax(axis=1) + 1, 0)


STEP_POSITIVE_MONTHS = 3


def step_month(e):
    """First month that closes a run of STEP_POSITIVE_MONTHS positive EBITDA months (0 = none)."""
    pos = e > 0
    run = pos[:, STEP_POSITIVE_MONTHS - 1:].copy()
    for j in range(1, STEP_POSITIVE_MONTHS):
        run &= pos[:, STEP_POSITIVE_MONTHS - 1 - j:M - j]
    return np.where(run.any(axis=1), run.argmax(axis=1) + STEP_POSITIVE_MONTHS, 0)


def run_plan(x, dists, target=None, a18=None, h=0, stepup=False, central=BASE_CENTRAL, opts=None, seeds=(SEED,), factors=None,
             keep=False, profiles=None, target_fn=None):
    """D draws (one fleet seed each) of a plan, with its triggers: the lean hold ends the month after EBITDA first turns positive;
    with stepup, hiring doubles after 3 positive months. The fleet is `target` (or plan_target(a18, h)); the default is the base.
    Each trigger is found on one run and applied on the next; the unchanged history is asserted."""
    D = len(seeds)
    factors = np.ones(D) if factors is None else np.asarray(factors, float)
    if target_fn is not None:                                  # target_fn(step month or None) -> agents by month
        mk = target_fn
    elif a18 is not None:
        mk = lambda step=None: plan_target(a18, h, step)
    else:
        mk = lambda step=None: fleet_target() if target is None else target
    Pc = market_profiles(x, D) if profiles is None else profiles
    targets = [mk() for _ in range(D)]
    fleets = [make_fleet(dists, targets[d], seeds[d], factors[d]) for d in range(D)]
    lean = central == "lean hold"
    hold = [M] * D
    base = dict(opts or {})
    sim = lambda: simulate(x, fleets, keep, {**base, "central_hold_until": list(hold) if lean else None}, Pc)
    o = sim()
    release = np.zeros(D, int)
    if lean:
        release = first_positive(o["ebitda"])
        if release.any():
            prev = o["ebitda"].copy()
            hold = [int(r) if r else M for r in release]
            o = sim()
            for d in np.nonzero(release)[0]:
                assert np.allclose(prev[d, :release[d]], o["ebitda"][d, :release[d]], rtol=1e-9, atol=1e-3), "lean-hold history moved"
    step = np.zeros(D, int)
    if stepup and (target_fn is not None or (h > 0 and a18 is not None)):
        step = step_month(o["ebitda"])
        step = np.where(step < M, step, 0)
        if step.any():
            prev = o["ebitda"].copy()
            for d in np.nonzero(step)[0]:
                targets[d] = mk(int(step[d]))
                fleets[d] = make_fleet(dists, targets[d], seeds[d], factors[d])
            o = sim()
            for d in np.nonzero(step)[0]:
                assert np.allclose(prev[d, :step[d]], o["ebitda"][d, :step[d]], rtol=1e-9, atol=1e-3), "step-up history moved"
    return o, fleets, targets, {"release": release, "step": step,
                                "opts": {**base, "central_hold_until": (hold[0] if lean else None)}}


TREASURY_KEYS = ("ebitda", "ebitda_ex_a", "depreciation", "cf_receivable", "cf_investing", "_contingency")


def stack_operating(outs):
    """The operating lines treasury() needs, from several single-draw runs, stacked as draws (for vectorised funding searches)."""
    st = {k: np.concatenate([o[k] for o in outs]) for k in TREASURY_KEYS if k != "_contingency"}
    st["_contingency"] = outs[0]["_contingency"]
    return st


def size_funding(o, round_months, floor=5 * CRORE, seed_step=1 * CRORE, round_step=5 * CRORE, hi=5000 * CRORE, steps=48):
    """The smallest seed (at m0, rounded up to seed_step) and staged rounds (each landing at the end of its month, rounded up to
    round_step) that keep month-end cash >= floor: the seed until the first round lands (that month's closing before it, with its
    cost booked), each round until the next one lands, the last to the end of the horizon. Interest on the cash is inside
    treasury(), so each bisection runs on the real month-by-month path: more cash earns more interest, and the search already
    sees it (no separate fixed-point loop is needed). Rounds that come out at 0 are dropped. Vectorised over draws.
    Returns seed (D,), [(month, amount (D,))], feasible (D,)."""
    D = o["ebitda"].shape[0]
    months = list(round_months)
    amts = [np.zeros(D) for _ in months]

    def cash(seed, k_amt=None, j=None):
        rds = [(m, (k_amt if i == j else amts[i]) if i <= (j if j is not None else -1) else 0.0, True) for i, m in enumerate(months)]
        return treasury(o, seed_size=seed, rounds=rds)["cash"]

    def bisect(ok_fn):
        lo, hi_ = np.zeros(D), np.full(D, hi)
        feas = ok_fn(hi_)
        zero_ok = ok_fn(lo)
        for _ in range(steps):
            mid = (lo + hi_) / 2
            g = ok_fn(mid)
            hi_, lo = np.where(g, mid, hi_), np.where(g, lo, mid)
        return np.where(zero_ok, 0.0, hi_), feas
    first = months[0] if months else M
    seed, f0 = bisect(lambda sd: cash(sd)[:, :first].min(axis=1) >= floor)
    seed = np.ceil(np.round(seed / seed_step, 9)) * seed_step
    feasible = f0.copy()
    for j, m in enumerate(months):
        end = months[j + 1] if j + 1 < len(months) else M
        a, fj = bisect(lambda v: cash(seed, v, j)[:, m - 1:end].min(axis=1) >= floor)
        amts[j] = np.ceil(np.round(a / round_step, 9)) * round_step
        feasible &= fj
    rounds = [(m, amts[i]) for i, m in enumerate(months)]
    return seed, rounds, feasible


# ---------------------------------------------------------------- funding tests and summaries
def stays_positive_from(v):
    """First month (1-based) from which v stays > 0 to month 60; NaN if never."""
    pos = v > 0
    stays = np.flip(np.logical_and.accumulate(np.flip(pos, axis=1), axis=1), axis=1)
    return np.where(stays.any(axis=1), stays.argmax(axis=1) + 1.0, np.nan)


def first_month(cond):
    return np.where(cond.any(axis=1), cond.argmax(axis=1) + 1.0, np.nan)


def funding_tests(o):
    """Seed run-out, the latest month the A can close, the slips and the smallest A. (D,) each."""
    D = o["ebitda"].shape[0]
    t = np.arange(1, M + 1)[None, :]
    out = {"seed_runout_month": first_month(o["cash_seed_only"] < 0)}
    ok_all = np.ones(D, bool)
    close_by = np.zeros(D)
    for n in range(1, M + 1):
        c = treasury(o, SERIES_A, n)["cash"] - SERIES_A * (t >= n)          # the cash before the A arrives
        ok_all &= (c[:, :n] >= 0).all(axis=1)
        close_by = np.where(ok_all, n, close_by)
    out["a_close_by_month"] = close_by
    for s in SLIP_MONTHS:
        c = treasury(o, SERIES_A, s)["cash"]
        out[f"slip{s}_min_cash"], out[f"slip{s}_min_month"] = c.min(axis=1), c.argmin(axis=1) + 1.0
        out[f"slip{s}_below0"] = (c < 0).any(axis=1)
    lo, hi = np.zeros(D), np.full(D, A_SEARCH_MAX)
    for _ in range(A_SEARCH_STEPS):
        mid = (lo + hi) / 2
        good = treasury(o, mid, SERIES_A_MONTH)["cash"][:, SERIES_A_MONTH - 1:].min(axis=1) >= CASH_FLOOR_AFTER_A
        hi, lo = np.where(good, mid, hi), np.where(good, lo, mid)
    out["smallest_a"] = hi
    out["smallest_a_found"] = treasury(o, hi, SERIES_A_MONTH)["cash"][:, SERIES_A_MONTH - 1:].min(axis=1) >= CASH_FLOOR_AFTER_A
    return out


def headline(o):
    """Per-draw headline measures, (D,) each."""
    pre = o["cash_seed_only"][:, :SERIES_A_MONTH]
    yr = lambda k, y: o[k][:, 12 * (y - 1):12 * y].sum(axis=1)
    return {
        "min_cash_seed_to_18": pre.min(axis=1), "min_cash_seed_to_18_month": pre.argmin(axis=1) + 1.0,
        "min_cash_60": o["cash"].min(axis=1), "min_cash_60_month": o["cash"].argmin(axis=1) + 1.0,
        "cash_positive_seed_to_18": (pre > 0).all(axis=1), "cash_positive_60": (o["cash"] > 0).all(axis=1),
        "extra_funding_before_a": np.maximum(0.0, -pre.min(axis=1)), "extra_funding_60": np.maximum(0.0, -o["cash"].min(axis=1)),
        "ebitda_breakeven_month": stays_positive_from(o["ebitda"]),
        "first_ebitda_positive_month": first_month(o["ebitda"] > 0),
        **{f"{k}_y{y}": yr(k, y) for k in ("revenue", "cm1", "cm2", "cm3", "ebitda", "interest", "pat") for y in range(1, 6)},
        "cum_pat_60": o["cum_pat"][:, -1], "cash_60": o["cash"][:, -1],
        "savers_m18": o["still_saving"][:, 17], "savers_m60": o["still_saving"][:, -1],
        "aum_m18": o["fund_end"][:, 17], "aum_m60": o["fund_end"][:, -1],
        "money_lent_to_m18": o["money_lent"][:, :18].sum(axis=1), "money_lent_60": o["money_lent"].sum(axis=1),
        "revenue_m18": o["revenue"][:, 17],
        **funding_tests(o),
    }


def month_text(v):
    return "never within 60 months" if np.isnan(v) else float(v)


# ---------------------------------------------------------------- tables
def write(name, rows):
    with (T / name).open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


R_ = "Rs"
# (key, plain words, unit, how a year rolls up: sum | end | start | pct:<numerator key> | pct_of:<num>:<den>)
LINES = [
    ("agents_start", "Agents at start of month", "agents", "start"), ("hired", "Agents hired (incl. replacements)", "agents", "sum"),
    ("left", "Agents who left (end of month)", "agents", "sum"), ("agents", "Agents working", "agents", "end"),
    ("cities", "Cities", "cities", "end"), ("city_managers", "City managers", "people", "end"), ("team_leads", "Team leads", "people", "end"),
    *[(f"hc_{d}", f"Central team: {d.lower()}", "people", "end") for d in DEPARTMENTS],
    ("hc_central", "Central team, total", "people", "end"), ("hc_total", "Headcount, all (agents, field managers, central)", "people", "end"),
    ("signups", "Sign-ups", "sign-ups", "sum"), ("still_saving", "Savers still saving", "savers", "end"),
    ("fund_end", "Money in the fund at month end (AUM)", R_, "end"), ("cash_deposits", "Cash collected from savers", R_, "sum"),
    ("cash_visits_a_day", "Cash visits a day, all agents", "visits a day", "end"),
    ("loans", "Personal loans made (first and repeat)", "loans", "sum"), ("topups", "Top-ups", "top-ups", "sum"),
    ("money_lent", "Money lent, personal loans incl. top-ups", R_, "sum"), ("housing_lent", "Home loans and LAP lent by other lenders", R_, "sum"),
    ("fee_multiplier", "Origination fee multiplier (round 9 ramp)", "x a DSA's rate", "end"),
    *[(k, f"Revenue: {nm}", R_, "sum") for k, nm in REVENUE], ("revenue", "Revenue, total", R_, "sum"),
    *[(k, f"Direct: {nm}", R_, "sum") for k, nm in DIRECT], ("direct", "Direct costs", R_, "sum"),
    ("cm1", "CM1 (transaction margin)", R_, "sum"), ("cm1_pct", "CM1, share of revenue", "share", "pct:cm1"),
    *[(k, f"Servicing: {nm}", R_, "sum") for k, nm in SERVICING], ("servicing", "Field servicing", R_, "sum"),
    ("cm2", "CM2 (after serving the book)", R_, "sum"), ("cm2_pct", "CM2, share of revenue", "share", "pct:cm2"),
    *[(k, f"Acquisition: {nm}", R_, "sum") for k, nm in ACQUISITION], ("acquisition", "Acquisition", R_, "sum"),
    ("cm3", "CM3 (after acquiring customers)", R_, "sum"), ("cm3_pct", "CM3, share of revenue", "share", "pct:cm3"),
    *[(k, f"Central: {nm}", R_, "sum") for k, nm in CENTRAL_COSTS],
    ("cost_contingency", "Central: contingency, 10% of every expensed line above", R_, "sum"), ("central", "Central costs", R_, "sum"),
    ("ebitda", "EBITDA", R_, "sum"), ("ebitda_pct", "EBITDA, share of revenue", "share", "pct:ebitda"),
    *[(k, nm, R_, "sum") for k, nm in DEPRECIATION], ("depreciation", "Depreciation", R_, "sum"),
    ("ebit", "EBIT", R_, "sum"), ("interest", "Interest on cash (other income)", R_, "sum"), ("pbt", "Profit before tax", R_, "sum"),
    ("tax", "Income tax", R_, "sum"), ("pat", "PAT (net profit after tax)", R_, "sum"),
    ("pat_pct", "PAT, share of revenue", "share", "pct:pat"), ("cum_pat", "Cumulative PAT", R_, "end"),
    ("losses_carried", "Tax losses carried forward", R_, "end"),
    ("cost_salary", "Memo: agent salaries (7% raise each company year)", R_, "sum"),
    ("cost_agent_statutory", "Memo: agent statutory", R_, "sum"),
    ("cost_incentive", "Memo: agent pay on his book's balance", R_, "sum"), ("agent_cost", "Memo: agent cost, total (split above)", R_, "sum"),
    ("acq_share", "Memo: acquisition share of agent cost", "share", "pct_of:cost_agent_acq:agent_cost"),
    ("opex", "Memo: cash out, costs paid (all expensed costs, paid in the month)", R_, "sum"),
    ("tax_paid", "Memo: cash out, income tax paid", R_, "sum"),
    ("cf_pat_line", "Cash flow, operating: PAT", R_, "sum"), ("cf_dep_line", "Cash flow, operating: add back depreciation", R_, "sum"),
    ("cf_receivable", "Cash flow, operating: less the increase in commissions receivable", R_, "sum"),
    ("cf_tax_timing", "Cash flow, operating: tax booked less tax paid (paid in the month booked)", R_, "sum"),
    ("cf_operating", "Cash from operations (includes interest received)", R_, "sum"),
    ("cf_capex_laptops", "Cash flow, investing: laptops", R_, "sum"), ("cf_capex_integrations", "Cash flow, investing: app integrations", R_, "sum"),
    ("cf_investing", "Cash from investing", R_, "sum"),
    ("cf_seed", "Cash flow, financing: seed (lands at m0, shown in month 1)", R_, "sum"),
    ("cf_series_a", "Cash flow, financing: Series A (end of month 18)", R_, "sum"),
    ("cf_financing", "Cash from financing", R_, "sum"), ("net_change", "Net change in cash", R_, "sum"),
    ("opening_cash", "Opening cash", R_, "start"), ("cash", "Closing cash, with the Series A", R_, "end"),
    ("cash_seed_only", "Closing cash, seed only (no Series A)", R_, "end"),
    ("received", "Memo: commissions received", R_, "sum"), ("receivable", "Memo: commissions earned, not yet received", R_, "end"),
    ("burn", "Memo: burn (cash used by operations and investing)", R_, "sum"),
]


def table_arrays(o):
    """o plus the derived display lines, (D, M) each."""
    sh = lambda a, b: np.divide(a, b, out=np.full_like(a, np.nan), where=b != 0)
    return {**o, "agents_start": o["agents"] - o["hired"], "hc_total": o["agents"] + o["hc_central"] + o["city_managers"] + o["team_leads"],
            **{f"{k}_pct": sh(o[k], o["revenue"]) for k in ("cm1", "cm2", "cm3", "ebitda", "pat")},
            "acq_share": sh(o["cost_agent_acq"], o["agent_cost"]), "cf_pat_line": o["pat"], "cf_dep_line": o["depreciation"],
            "tax_paid": o["tax"]}


def monthly_rows(o):
    a = table_arrays(o)
    return [{"Month": t + 1, "Year": t // 12 + 1, **{f"{nm} ({u})" if u == R_ else nm: float(a[k][0, t]) for k, nm, u, _r in LINES}}
            for t in range(M)]


def roll(a, k, how):
    v = a[k][0]
    if how == "sum":
        return [float(v[12 * y:12 * y + 12].sum()) for y in range(YEARS)]
    if how == "end":
        return [float(v[12 * y + 11]) for y in range(YEARS)]
    if how == "start":
        return [float(v[12 * y]) for y in range(YEARS)]
    if how.startswith("pct:"):
        num, den = roll(a, how[4:], "sum"), roll(a, "revenue", "sum")
    else:
        _, nk, dk = how.split(":")
        num, den = roll(a, nk, "sum"), roll(a, dk, "sum")
    return [n / d if d else float("nan") for n, d in zip(num, den)]


def roll_total(a, k, how):
    v = a[k][0]
    if how == "sum":
        return float(v.sum())
    if how == "end":
        return float(v[-1])
    if how == "start":
        return float(v[0])
    if how.startswith("pct:"):
        return float(a[how[4:]][0].sum() / a["revenue"][0].sum())
    _, nk, dk = how.split(":")
    return float(a[nk][0].sum() / a[dk][0].sum())


def year_row(a, k, nm, u, how, label="Line"):
    vals = roll(a, k, how)
    return {label: nm, "Unit": u, **{f"Year {y + 1}": vals[y] for y in range(YEARS)}, "Five years": roll_total(a, k, how),
            "How the year is formed": {"sum": "sum of the months", "end": "at year end", "start": "at year start"}.get(how, "ratio of the year's sums")}


def yearly_rows(o):
    a = table_arrays(o)
    return [year_row(a, k, nm, u, how) for k, nm, u, how in LINES]


def ladder_rows(o):
    """Investor-format P&L with CM1/CM2/CM3 as shares of revenue."""
    a = table_arrays(o)
    L = {k: (nm, u, how) for k, nm, u, how in LINES}
    keys = [*[k for k, _ in REVENUE], "revenue", *[k for k, _ in DIRECT], "direct", "cm1", "cm1_pct",
            *[k for k, _ in SERVICING], "servicing", "cm2", "cm2_pct", *[k for k, _ in ACQUISITION], "acquisition", "cm3", "cm3_pct",
            *[k for k, _ in CENTRAL_COSTS], "cost_contingency", "central", "ebitda", "ebitda_pct", *[k for k, _ in DEPRECIATION],
            "depreciation", "ebit", "interest", "pbt", "tax", "pat", "pat_pct", "cum_pat", "cash"]
    return [year_row(a, k, *L[k]) for k in keys]


def cashflow_rows(o):
    a = table_arrays(o)
    L = {k: (nm, u, how) for k, nm, u, how in LINES}
    keys = ["cf_pat_line", "cf_dep_line", "cf_receivable", "cf_tax_timing", "cf_operating", "cf_capex_laptops", "cf_capex_integrations",
            "cf_investing", "cf_seed", "cf_series_a", "cf_financing", "net_change", "opening_cash", "cash"]
    rows = [year_row(a, k, *L[k]) for k in keys]
    c = a["cash"][0]
    low = [float(c[12 * y:12 * y + 12].min()) for y in range(YEARS)]
    lowm = [float(12 * y + c[12 * y:12 * y + 12].argmin() + 1) for y in range(YEARS)]
    rows.append({"Line": "Lowest month-end cash in the year, with the Series A", "Unit": R_, **{f"Year {y + 1}": low[y] for y in range(YEARS)},
                 "Five years": float(c.min()), "How the year is formed": "lowest month end"})
    rows.append({"Line": "Month of that lowest cash", "Unit": "company month", **{f"Year {y + 1}": lowm[y] for y in range(YEARS)},
                 "Five years": float(c.argmin() + 1), "How the year is formed": "lowest month end"})
    return rows


def headcount_rows(o):
    end = lambda v: {f"Year {y + 1}": float(v[0, 12 * y + 11]) for y in range(YEARS)}
    rows = [{"Department": "Field agents", "Role": "Agents", **end(o["agents"])},
            {"Department": "Field management", "Role": "City managers", **end(o["city_managers"])},
            {"Department": "Field management", "Role": "Team leads", **end(o["team_leads"])}]
    for role, dep, _p in ALL_ROLES:
        rows.append({"Department": dep, "Role": role, **end(o["roles"][role])})
    for d in DEPARTMENTS:
        rows.append({"Department": d, "Role": "Department total", **end(o[f"hc_{d}"])})
    rows.append({"Department": "Central team", "Role": "Total", **end(o["hc_central"])})
    rows.append({"Department": "All", "Role": "Total headcount", **end(o["agents"] + o["hc_central"] + o["city_managers"] + o["team_leads"])})
    return [{**r, "Counted": "at year end (month 12, 24, ...)"} for r in rows]


def m18_rows(o, h):
    i = SERIES_A_MONTH - 1
    v = lambda k: float(o[k][0, i])
    acq = float(o["acquisition"][0, :i + 1].sum())
    su = float(o["signups"][0, :i + 1].sum())
    R = lambda measure, value, unit, how: {"Measure": measure, "Value": value, "Unit": unit, "How it is worked out": how}
    rows = [
        R("Savers still saving", v("still_saving"), "savers", "month 18"),
        R("Money in the fund (AUM)", v("fund_end"), R_, "end of month 18"),
        R("Money lent in month 18", v("money_lent"), R_, "personal loans: first, repeat and top-ups"),
        R("Money lent, months 1-18", float(o["money_lent"][0, :i + 1].sum()), R_, "personal loans: first, repeat and top-ups"),
        R("Revenue in month 18", v("revenue"), "Rs a month", "commissions earned"),
        R("Revenue run-rate", 12 * v("revenue"), "Rs a year", "month 18 x 12"),
        R("CM1 in month 18", v("cm1"), "Rs a month", ""), R("CM2 in month 18", v("cm2"), "Rs a month", ""),
        R("CM3 in month 18", v("cm3"), "Rs a month", ""),
        R("EBITDA in month 18", v("ebitda"), "Rs a month", "includes the Series A costs (Rs 15 lakh + 10% contingency)"),
        R("EBITDA in month 18 before the Series A costs", float(o["ebitda_ex_a"][0, i]), "Rs a month", ""),
        R("Burn in month 18", v("burn"), "Rs a month", "cash used by operations and investing in month 18 (negative = cash made)"),
        R("Average burn, months 1-18", float(o["burn"][0, :i + 1].sum()) / SERIES_A_MONTH, "Rs a month", "cash used, months 1-18, over 18"),
        R("Cash at the end of month 18, seed only", v("cash_seed_only"), R_, "no Series A"),
        R("Cash at the end of month 18, with the Series A", v("cash"), R_, f"with Rs {SERIES_A / CRORE:.0f} crore landing at the end of month 18"),
        R("Lowest cash, seed only, through m18", float(h["min_cash_seed_to_18"][0]), R_, f"in month {h['min_cash_seed_to_18_month'][0]:.0f}"),
        R("Lowest cash, with the Series A, through m60", float(h["min_cash_60"][0]), R_, f"in month {h['min_cash_60_month'][0]:.0f}"),
        R("Month the seed alone runs out", month_text(h["seed_runout_month"][0]), "company month",
          "first month-end below 0 with no Series A"),
        R("The Series A must close by month", float(h["a_close_by_month"][0]), "company month",
          f"the latest month-end it can land (Rs {SERIES_A / CRORE:.0f} crore, its Rs {SERIES_A_COST / LAKH:.0f} lakh cost booked that month) "
          "without cash going below 0 before"),
        *[r for s in SLIP_MONTHS for r in (
            R(f"Series A slips to month {s}: lowest cash through m60", float(h[f"slip{s}_min_cash"][0]), R_,
              f"in month {h[f'slip{s}_min_month'][0]:.0f}"),
            R(f"Series A slips to month {s}: cash goes below 0", "yes" if h[f"slip{s}_below0"][0] else "no", "", ""))],
        R("Smallest Series A at month 18 that keeps cash at or above Rs 5 crore through m60", float(h["smallest_a"][0]), R_,
          "searched; the floor applies from month 18 (months 1-17 are seed only)"),
        R("Headroom over the minimum A, likely values", SERIES_A - float(h["smallest_a"][0]), R_,
          f"Rs {SERIES_A / CRORE:.0f} crore less the smallest A above (company_mc.py adds the Monte Carlo p50 and p90 lines)"),
        R("Agents working", v("agents"), "agents", "month 18"),
        R("Cities", v("cities"), "cities", "month 18"),
        R("Headcount, all", v("agents") + v("hc_central") + v("city_managers") + v("team_leads"), "people", "agents, field managers, central team"),
        R("Sign-ups, months 1-18", su, "sign-ups", ""),
        R("Cost to win a saver, per sign-up", acq / su, "Rs a sign-up",
          "months 1-18: the acquisition block (the acquisition share of agent cost, online leads, KYC, kit, city launch, brand) over sign-ups"),
        R("Cost to win a saver, per saver still saving", acq / v("still_saving"), "Rs a saver", "the same cost over savers still saving in month 18"),
        R("Contribution per agent in month 18, CM2", v("cm2") / v("agents"), "Rs a month", "CM2 (after serving the book) per agent working"),
        R("Contribution per agent in month 18, CM3", v("cm3") / v("agents"), "Rs a month", "CM3 (after acquisition) per agent working"),
    ]
    return rows


def fleet_scenarios(x, dists):
    rows, outs = [], []
    for name, pts, central in FLEET_SCENARIOS:
        o, *_ = run_plan(x, dists, target=fleet_target(pts), central=central)
        h = headline(o)
        outs.append(o)
        rows.append({"Scenario": name, "Central team": central,
                     **{f"EBITDA year {y} (Rs)": float(h[f"ebitda_y{y}"][0]) for y in range(1, 6)},
                     "PAT, 60 months (Rs)": float(h["cum_pat_60"][0]),
                     f"Cash at month 60, with the Rs {SERIES_A / CRORE:.0f} crore Series A (Rs)": float(h["cash_60"][0]),
                     f"Lowest cash, with the Rs {SERIES_A / CRORE:.0f} crore Series A, through m60 (Rs)": float(h["min_cash_60"][0]),
                     "Smallest Series A at m18 keeping cash at or above Rs 5 crore through m60 (Rs)": float(h["smallest_a"][0]),
                     "Savers at month 60": float(h["savers_m60"][0]), "Agents at month 60": float(o["agents"][0, -1]),
                     "EBITDA break-even month (stays positive)": month_text(h["ebitda_breakeven_month"][0])})
    return rows, outs


def breakeven_customers(o, label):
    """How many customers it takes: the plan's numbers when EBITDA first turns positive (if it does), and the rule of thumb
    central costs a month / mature contribution per saver a month (mature = months 49-60)."""
    fp = int(first_positive(o["ebitda"])[0])
    be = stays_positive_from(o["ebitda"])[0]
    R_ = lambda m, v, u, how: {"Plan": label, "Measure": m, "Value": v, "Unit": u, "How it is worked out": how}
    last = slice(48, 60)
    sv = float(o["still_saving"][0, last].sum())
    cm3_m, cm2_m = float(o["cm3"][0, last].sum()) / sv, float(o["cm2"][0, last].sum()) / sv
    central_last = float(o["central"][0, last].mean())
    rows = [R_("Month EBITDA first turns positive", float(fp) if fp else "not within 60", "company month", "first month with EBITDA > 0"),
            R_("Month EBITDA turns positive and stays positive", "not within 60" if np.isnan(be) else float(be), "company month", "")]
    if fp:
        i = fp - 1
        v = lambda k: float(o[k][0, i])
        rows += [R_("Active savers when EBITDA first turns positive", v("still_saving"), "savers", "savers still saving in that month"),
                 R_("Agents then", v("agents"), "agents", ""), R_("Money in the fund (AUM) then", v("fund_end"), "Rs", "end of that month"),
                 R_("Central costs that month", v("central"), "Rs a month", "")]
    rows += [
        R_("Central costs a month, months 49-60", central_last, "Rs a month", "central team, app, licences, HQ, travel, tools, contingency"),
        R_("Mature CM3 per active saver a month (months 49-60)", cm3_m, "Rs a saver a month", "after direct, servicing and acquisition costs"),
        R_("Rule of thumb: break-even savers = central costs a month / mature CM3 per saver a month",
           central_last / cm3_m if cm3_m > 0 else "CM3 not positive", "savers", "with acquisition running at the plan's pace"),
        R_("Mature CM2 per active saver a month (months 49-60)", cm2_m, "Rs a saver a month", "after direct and servicing costs only"),
        R_("Rule of thumb if acquisition stopped: central costs / mature CM2 per saver", central_last / cm2_m if cm2_m > 0 else "CM2 not positive",
           "savers", "a floor: the book needed to carry the central team with no growth spend"),
        R_("Active savers the plan has at m60", float(o["still_saving"][0, -1]), "savers", ""),
        R_("Agents the plan has at m60", float(o["agents"][0, -1]), "agents", ""),
        R_("Money in the fund (AUM) at m60", float(o["fund_end"][0, -1]), "Rs", "")]
    return rows


def readme(o):
    lines = [
        "# Company model tables (written by model/company_model.py and model/company_mc.py; do not edit by hand)",
        "",
        "Rupee values are in rupees. Months are company months 1-60; year 1 = months 1-12. Spec: story/BRIEF_company_model_2026-10-17.md,",
        "the CM-ladder addendum and story/FIXES_company_round1_2026-10-17.md. One agent's economics come from model/cohort_engine.py.",
        "",
        "## Tables",
        "- company_monthly.csv: every line, month by month (fleet, headcount, savers, AUM, lending, the P&L ladder, the cash flow).",
        "- company_yearly.csv: the same lines by year (flows summed, stocks at year end).",
        "- company_pnl_ladder_yearly.csv: investor-format P&L: revenue, CM1, CM2, CM3 (with shares of revenue), EBITDA, interest, PAT.",
        "- company_cashflow_yearly.csv: operating, investing, financing, closing cash, the lowest cash and its month.",
        "- company_headcount.csv: headcount by department and role at each year end.",
        "- company_m18.csv: the Series A story at month 18, the seed run-out, the slips and the smallest Series A.",
        "- company_fleet_scenarios.csv: the growth J-curve: base (60 -> 300), hiring frozen at 60 after m18, frozen at 150 after m36.",
        "- company_mc_summary.csv: 2,000-draw Monte Carlo.",
        "- company_checks.csv: the reconciliations; every row must say Passes = True.",
        "",
        "## Staffing rules",
        f"- Agents (round 10 base): grow to {BASE_A18} by m18 ({', '.join(f'm{m} {n}' for m, n in zip(range(0, 19, 3), fleet_target()[0:19:3]))}), "
        f"then hire only to replace leavers; {ATTRITION_YEAR:.0%} leave a year, replaced the next month; the replacement inherits the "
        f"book ({HANDOVER_LOSS:.0%} of its savers stop). The growth plan (60 at m18, 300 by m60) is a scenario.",
        "- Central team (round 10 base): lean hold: after the launch team, no central hires until EBITDA first turns positive, except "
        "the cash-reconciliation and HR executives that scale per agent; then the rules below apply.",
        f"- Cities: 1 from m1, 2 from m9, 3 from m18, then one per {AGENTS_PER_CITY} agents (rounded up). One city manager per city; "
        f"one team lead per {AGENTS_PER_TEAM_LEAD} agents (rounded up).",
        "- Central team at the start: " + "; ".join(f"{r} {', '.join(f'{k} from m{m}' for m, k in st)}" for r, _d, _p, st, _s in CENTRAL) + ".",
        f"- Engineers and operations executives: +1 each per {SCALE_PER_AGENTS} agents beyond {SCALE_BASE_AGENTS}, after m{SCALE_AFTER} "
        "(rounded down; the 'beyond 60' applies to both).",
        "- " + "; ".join(f"{r}: {rule}" for r, _d, _p, rule in SCALE_ROLES) + ".",
        f"- Pay: +{STATUTORY:.0%} statutory on central and field-management pay; agents + Rs {AGENT_STATUTORY:,.0f} a month statutory; "
        f"everyone's pay (agents too, their statutory with it) rises {RAISE:.0%} each company year. Agent pay on balance: 0.25% a year of "
        "his book's balance, capped at Rs 10,000 a month per agent (the cap rises with the salary).",
        "",
        "## Money rules",
        "- Ladder: revenue - direct (bureau, fraud) = CM1; - field servicing = CM2; - acquisition = CM3; - central = EBITDA; - depreciation = EBIT;",
        f"  + interest on cash ({INTEREST_RATE:.1%} a year on the opening cash) = profit before tax; - tax ({TAX:.0%} after past losses) = PAT.",
        f"- Agent cost (salary, statutory, pay on balance) is split by his tenure: {ACQ_SHARE_EARLY:.0%} acquisition in months 1-12, falling "
        f"to {ACQ_SHARE_M60:.0%} at month 60.",
        f"- Laptops and integrations are capitalised over {DEPRECIATION_MONTHS} months; commissions arrive {COMMISSION_LAG} months after they are earned.",
        f"- Funding: seed Rs {SEED_ROUND / CRORE:.0f} crore at m0, Series A Rs {SERIES_A / CRORE:.0f} crore at the end of m{SERIES_A_MONTH}; "
        "their costs are expensed in central costs.",
    ]
    (T / "company_README.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------- checks
def checks(x, dists, o, h, fleet, scen_outs=None, target=None, opts=None):
    rows = []

    def add(name, expected, got, tol, note=""):
        e_, g_ = np.asarray(expected, float), np.asarray(got, float)
        gap = float(np.max(np.abs(g_ - e_)))
        scale = float(np.max(np.abs(e_))) or 1.0
        rows.append({"Check": name, "Largest gap": gap, "Largest gap as share of the biggest value": gap / scale,
                     "Tolerance (share)": tol, "Passes": bool(gap / scale <= tol), "Note": note})
    t = np.arange(1, M + 1)
    rm = raise_mult()
    op = {**DEFAULT_OPTS, **(opts or {})}
    target = fleet_target() if target is None else target
    # 1. one agent, no attrition, no central costs reproduces cohort_engine.run (fee ramp aligned to company months)
    pairs = (("signups", "signups"), ("still_saving", "still_saving"), ("balance", "balance"), ("fund_end", "fund_end"),
             ("money_lent", "money_lent"), ("rev_fund", "rev_fund"), ("rev_orig_loans+rev_orig_topups", "rev_origination"),
             ("rev_collections", "rev_dpd31_90+rev_recovery90"), ("rev_cards", "rev_cards"),
             ("rev_insurance+rev_investments+rev_payments+rev_housing+rev_other_lenders", "rev_crosssell"),
             ("revenue", "income"), ("_eng_salary", "cost_salary"), ("cost_helpers", "cost_extra_capacity"), ("cost_kyc", "cost_kyc"),
             ("cost_support", "cost_support"), ("_eng_cash_cover", "cost_cash_cover"), ("_eng_incentive", "cost_incentive"),
             ("cost_leads", "cost_leads"), ("_eng_net", "net"))
    pick = lambda d, ks: sum(d[k] for k in ks.split("+"))
    for start in (1, 13):
        c = simulate(x, [one_agent_fleet(x, start)], keep=True)
        r = E.run(x, start_month=start)["monthly"]
        n = M - start + 1
        for mine, theirs in pairs:
            add(f"One agent hired in month {start}, no attrition, no central costs: {mine} = cohort_engine.run(start_month={start}) {theirs}",
                pick(r, theirs)[0, :n], pick(c, mine)[0, start - 1:], 1e-9,
                ("the engine's default path" if start == 1 else "company months 13-60 against his tenure months 1-48")
                + ("; the engine prices pay flat and cover at Rs 1,000, so this is the company's agent unit before raises and the "
                   "0.015% cover" if mine.startswith("_eng") else ""))
        ten = np.arange(1, n + 1)
        add(f"One agent hired in month {start}: acquisition share of his cost follows his tenure (50% to month 12, 20% at month 60)",
            acquisition_share(ten) * (c["agent_cost"][0, start - 1:]), c["cost_agent_acq"][0, start - 1:], 1e-12)
        if start == 1:
            add("One agent hired in month 1: cumulative agent-unit P&L at month 60 = cohort_engine cum_cash", [r["cum_cash"][0, -1]],
                [c["_eng_net"][0].sum()], 1e-9)
            add("One agent: salary = the engine's Rs 20,000 x 1.07 ^ (company year - 1) (fix 4)", r["cost_salary"][0] * rm,
                c["cost_salary"][0], 1e-12)
            cd = c["_extras"][0]["CD"][0]
            add("One agent: cash cover = the larger of Rs 1,000 or 0.015% of his cash collected (fix 1)",
                np.maximum(float(x["cash_cover"]), CASH_COVER_RATE * cd), c["cost_cash_cover"][0], 1e-12,
                f"0.015% binds from month {first_month((CASH_COVER_RATE * cd > float(x['cash_cover']))[None])[0]:.0f}")
    # 2. headcount x pay reconciles to the people cost (a loop, independent of the vectorised build)
    central = field = agents_pay = 0.0
    for i in range(M):
        rmul = (1 + RAISE) ** (i // 12)
        for role, _d, pay in ALL_ROLES:
            central += o["roles"][role][0, i] * pay * rmul * (1 + STATUTORY)
        field += (o["city_managers"][0, i] * CITY_MANAGER_PAY + o["team_leads"][0, i] * TEAM_LEAD_PAY) * rmul * (1 + STATUTORY)
        agents_pay += o["agents"][0, i] * (float(x["salary"]) + AGENT_STATUTORY) * rmul
    add("Central team (incl. the scale roles): headcount x pay x raises x 1.10 = central pay cost, 60 months", [central],
        [o["cost_central_pay"][0].sum()], 1e-12)
    add("Field management: (city managers x 80,000 + team leads x 40,000) x raises x 1.10 = their cost, 60 months", [field],
        [(o["cost_city_managers"] + o["cost_team_leads"])[0].sum()], 1e-12)
    add("Agents: agents working x (salary + Rs 3,000) x raises = agent salaries + statutory, 60 months", [agents_pay],
        [(o["cost_salary"] + o["cost_agent_statutory"])[0].sum()], 1e-12)
    ag, sv = o["agents"][0], o["still_saving"][0]
    want = {"Risk and fraud lead": (np.maximum.accumulate(ag >= 100)).astype(float), "Cash reconciliation executives": np.ceil(ag / 50),
            "HR and recruiting executives": np.ceil(ag / 100), "Customer support lead": (np.maximum.accumulate(sv >= 50000)).astype(float)}
    if op["central_hold_until"]:
        for r in ("Risk and fraud lead", "Customer support lead"):
            want[r] = np.where(t <= op["central_hold_until"], 0.0, want[r])
    add("Scale roles follow their rules (risk lead from 100 agents; cash reconciliation 1 per 50; HR 1 per 100; support lead from "
        "50,000 savers)", np.concatenate([want[r] for r in want]), np.concatenate([o["roles"][r][0] for r in want]), 0.0,
        f"risk lead from month {first_month((ag >= 100)[None])[0]:.0f}; support lead from month {first_month((sv >= 50000)[None])[0]:.0f}")
    add("Agent cost: acquisition share + servicing share = salary + statutory + pay on balance, every month",
        o["agent_cost"][0], (o["cost_agent_acq"] + o["cost_agent_serv"])[0], 1e-12)
    ex = o["_extras"][0]
    add("Pay on balance: the books' balances add to the company balance", o["balance"][0], ex["Bal"].sum(axis=0), 1e-10)
    add("Cash collected: the books add to the company total", o["cash_deposits"][0], ex["CD"].sum(axis=0), 1e-10)
    add("Agents working each month = the agreed fleet path", target[1:], o["agents"][0], 0.0)
    if o["_incentive_cap"] is not None:
        cap0 = float(o["_incentive_cap"][0])
        pr = np.where(t <= op["pay_months"], float(x["agent_balance_pay"]), op["pay_after"])
        want_i = np.where(ex["tenure"] > 0, np.minimum(pr / 12 * ex["Bal"], cap0 * rm), 0.0)
        add("Pay on balance: each agent gets the smaller of 0.25%/12 of his book's balance and the cap (rising 7% a year)",
            want_i.sum(axis=0), o["cost_incentive"][0], 1e-12,
            f"cap Rs {cap0:,.0f} a month in year-1 terms; it binds in {int((pr / 12 * ex['Bal'] > cap0 * rm).sum())} agent-months")
    add("Every book has exactly one agent in every month after it opens", (o["agents"][0] > 0).astype(float),
        ((ex["tenure"] > 0).sum(axis=0) == o["agents"][0]).astype(float), 0.0)
    yrs = [o["left"][0, 12 * y:12 * y + 12].sum() / o["agents"][0, 12 * y:12 * y + 12].mean() for y in range(YEARS)]
    add("Agents who left a year / average agents working = 30% (years 1-5)", [ATTRITION_YEAR] * YEARS, yrs, 0.25,
        "whole agents: the small early fleet rounds the rate")
    # sign-ups: the ramp on his tenure, the decline on the book's age (independent formulas, not cohort_engine.signups)
    ramp, op = float(x["ramp_months"]), book_open_month(fleet)
    want_s = np.zeros_like(ex["Sc"])
    for hh in range(len(fleet["start"])):
        for i in range(M):
            tm = i + 1
            end = fleet["left"][hh] or M
            if fleet["start"][hh] <= tm <= end:
                k, b = tm - fleet["start"][hh] + 1, tm - op[fleet["slot"][hh]] + 1
                rf = min(1.0, 0.5 + 0.5 * (k - 1) / ramp) if ramp > 0 else 1.0
                dec = fleet["signup_decline_y5"][hh]
                df = 1.0 if b <= E.DECLINE_FROM else 1 + (dec - 1) * min(1.0, (b - E.DECLINE_FROM) / (E.DECLINE_TO - E.DECLINE_FROM))
                want_s[hh, i] = fleet["signups_run"][hh] * rf * df
    add("Sign-ups: each hire = his level x the ramp on his tenure x the decline on his BOOK's age (fix 5), every hire and month",
        want_s, ex["Sc"], 1e-12, f"{int(((fleet['start'] > op[fleet['slot']])).sum())} replacement hires inherit a book's age")
    # 3. the ladder
    add("Ladder: CM1 - servicing - acquisition - central = EBITDA, every month",
        (o["cm1"] - o["servicing"] - o["acquisition"] - o["central"])[0], o["ebitda"][0], 1e-12)
    add("Ladder: EBITDA - depreciation + interest - tax = PAT, every month",
        (o["ebitda"] - o["depreciation"] + o["interest"] - o["tax"])[0], o["pat"][0], 1e-12)
    add("Ladder: contingency = 10% of every expensed line above it", CONTINGENCY * (o["opex"] - o["cost_contingency"])[0],
        o["cost_contingency"][0], 1e-12, "the base is all expensed costs less the contingency itself")
    add("Licences one-time = Rs 7.5 lakh (fix 3)", [7.5 * LAKH], [o["cost_licences_once"][0].sum()], 1e-12)
    add("Depreciation: 60 months of depreciation + book value left at month 60 = capex",
        [(o["capex_laptops"] + o["capex_integrations"])[0].sum()],
        [o["depreciation"][0].sum() + sum(o[k][0, u] * max(0, DEPRECIATION_MONTHS - (M - u)) / DEPRECIATION_MONTHS
                                          for k in ("capex_laptops", "capex_integrations") for u in range(M))], 1e-12)
    opening = np.concatenate([[SEED_ROUND], o["cash"][0, :-1]])
    add("Interest = 5.5% / 12 x the cash at the start of the month (the seed counts from month 1)",
        INTEREST_RATE / 12 * np.maximum(0, opening), o["interest"][0], 1e-12)
    if o["losses_carried"][0, -1] == 0:
        add("Tax: with every past loss used by month 60, total tax = 25% of total profit before tax", [TAX * o["pbt"][0].sum()],
            [o["tax"][0].sum()], 1e-12)
    else:
        add("Tax: no tax while losses are still carried (none used up by month 60)", [0.0], [o["tax"][0].sum()], 0.0,
            f"losses carried at month 60: Rs {o['losses_carried'][0, -1]:,.0f}")
    # 4. cash
    add("Cash: closing(t) = closing(t - 1) + net change, every month", np.concatenate([[0.0], o["cash"][0, :-1]]) + o["net_change"][0],
        o["cash"][0], 1e-12)
    direct = o["received"] + o["interest"] - o["opex"] - o["tax"] - o["capex_laptops"] - o["capex_integrations"] + o["cf_financing"]
    add("Cash: the indirect statement = the direct one (commissions + interest received - costs - tax - capex + money raised)",
        direct[0], o["net_change"][0], 1e-12)
    want_c = o["cum_pat"] + np.cumsum(o["depreciation"] - o["capex_laptops"] - o["capex_integrations"] + o["cf_financing"], axis=1) - o["receivable"]
    add("Cash = cumulative PAT + depreciation - capex + money raised - commissions not yet received, every month", want_c[0], o["cash"][0], 1e-12)
    add("Cash: revenue earned in months 1-58 = commissions received in months 3-60", [o["revenue"][0, :M - COMMISSION_LAG].sum()],
        [o["received"][0].sum()], 1e-12)
    # 5. the Series A tests
    sa = float(h["smallest_a"][0])
    lo_ok = treasury(o, sa, SERIES_A_MONTH)["cash"][0, SERIES_A_MONTH - 1:].min()
    lo_less = treasury(o, sa - LAKH, SERIES_A_MONTH)["cash"][0, SERIES_A_MONTH - 1:].min()
    add("Smallest Series A: with it, the lowest cash from m18 to m60 is Rs 5 crore (to Rs 100)", [CASH_FLOOR_AFTER_A], [lo_ok], 1e-5,
        f"Rs 1 lakh less gives Rs {lo_less:,.0f}")
    add("Smallest Series A: Rs 1 lakh less breaks the Rs 5 crore floor", [1.0], [float(lo_less < CASH_FLOOR_AFTER_A)], 0.0)
    nby = int(h["a_close_by_month"][0])
    if nby < M:
        late = treasury(o, SERIES_A, nby + 1)["cash"][0] - SERIES_A * (t >= nby + 1)
        add(f"Series A close-by month {nby}: closing at month {nby + 1} instead lets cash go below 0 first", [1.0],
            [float((late[:nby + 1] < 0).any())], 0.0)
    add("Funding tests: the base plan through treasury() = the statements", o["cash"][0], treasury(o)["cash"][0], 0.0)
    if scen_outs:
        add("Fleet scenarios: the base scenario = the main run (EBITDA, every month)", o["ebitda"][0], scen_outs[0]["ebitda"][0], 0.0)
    # 6. stacking and totals
    Pc = o["_Pc"][0]
    li = {k: i for i, k in enumerate(PROFILE_LINES)}
    direct_s, direct_i = np.zeros(M), np.zeros(M)
    for hh in range(len(fleet["start"])):
        fk = ex["fk"][fleet["slot"][hh]]
        for m in np.nonzero(ex["Sc"][hh])[0]:
            w = ex["Sc"][hh, m] * fk[m:] / fk[m]
            direct_s[m:] += w * Pc[li["still_saving"], m, m:]
            direct_i[m:] += w * Pc[li["income"], m, m:]
    add("Stacking: savers summed hire by hire and cohort by cohort = the matrix total", direct_s, o["still_saving"][0], 1e-10)
    add("Stacking: revenue before the fee ramp, summed hire by hire = the matrix total", direct_i, o["income_before_ramp"][0], 1e-10)
    add("Cash visits a day: the books add to the company total", o["cash_visits_a_day"][0], ex["V"].sum(axis=0), 1e-10)
    add("Revenue lines add to revenue = engine income + the fee-ramp uplift",
        (o["income_before_ramp"] + (o["rev_orig_loans"] + o["rev_orig_topups"]) * (1 - 1 / o["fee_multiplier"]))[0], o["revenue"][0], 1e-10)
    a = table_arrays(o)
    sums = [k for k, _nm, _u, how in LINES if how == "sum"]
    add(f"Yearly = monthly: the five year columns add to the 60 months, all {len(sums)} summed lines",
        [a[k][0].sum() for k in sums], [sum(roll(a, k, "sum")) for k in sums], 1e-12)
    lad = {r["Line"]: r for r in ladder_rows(o)}
    add("Yearly ladder: revenue, CM1, CM2, CM3, EBITDA, interest, PAT (five years) = the monthly table",
        [o[k][0].sum() for k in ("revenue", "cm1", "cm2", "cm3", "ebitda", "interest", "pat")],
        [lad[nm]["Five years"] for nm in ("Revenue, total", "CM1 (transaction margin)", "CM2 (after serving the book)",
                                          "CM3 (after acquiring customers)", "EBITDA", "Interest on cash (other income)",
                                          "PAT (net profit after tax)")], 1e-12)
    cf = {r["Line"]: r for r in cashflow_rows(o)}
    add("Yearly cash flow: opening + net change = closing, each year",
        [cf["Opening cash"][f"Year {y}"] + cf["Net change in cash"][f"Year {y}"] for y in range(1, 6)],
        [cf["Closing cash, with the Series A"][f"Year {y}"] for y in range(1, 6)], 1e-12)
    return rows


def main():
    dists, _missing, _notes = E.load_dists()
    x = E.likely_inputs(dists)
    o, fleets, targets, info = run_plan(x, dists, central=BASE_CENTRAL, keep=True)
    fleet = fleets[0]
    h = headline(o)
    scen, scen_outs = fleet_scenarios(x, dists)
    ck = checks(x, dists, o, h, fleet, scen_outs, target=targets[0], opts=info["opts"])
    write("company_monthly.csv", monthly_rows(o))
    write("company_yearly.csv", yearly_rows(o))
    write("company_pnl_ladder_yearly.csv", ladder_rows(o))
    write("company_cashflow_yearly.csv", cashflow_rows(o))
    write("company_headcount.csv", headcount_rows(o))
    write("company_m18.csv", m18_rows(o, h))
    write("company_fleet_scenarios.csv", scen)
    write("company_breakeven_customers.csv", breakeven_customers(o, "Base: 80 agents by m18, then replace leavers"))
    write("company_checks.csv", ck)
    readme(o)
    print(f"hires {len(fleet['start'])} ({fleet['slots']} books); central hires released from month "
          f"{int(info['release'][0]) + 1 if info['release'][0] else 'never'}; checks passed {sum(r['Passes'] for r in ck)}/{len(ck)}")
    for r in ck:
        if not r["Passes"]:
            print("  FAIL", r["Check"], r["Largest gap"], r["Largest gap as share of the biggest value"])
    assert all(r["Passes"] for r in ck), "a check failed"
    return o


if __name__ == "__main__":
    main()

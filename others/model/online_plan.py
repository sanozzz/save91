"""Online-first company model (21 Oct 2026), 8-year horizon. The plan of record from 21 Oct; the street-fleet base stays in
tables/base_*.csv and the 18 Oct refresh in tables/refresh_*.csv.

Operator, 21 Oct: "based on the new approach and meeting with saket, we will be going online and building stuff. based on
the seed plan and our online first and offline test mode, we need to revamp our numbers and everytihing". Taps the same day:
  - an online saver puts in Rs 100 a day (Bachatt's stated minimum; ~20 debit days a month);
  - fund mix 80% equity SIP / 20% debt as the base (Bachatt conversation, F22), debt-only as a side case;
  - cost to win a saver: Rs 600 in the seed (its budgeted funnel), Rs 450 after (founder's judgement), Rs 300-600 range;
  - both a PROFITABLE path and a UNICORN track;
  - BASE = the plan: evidence where it exists, founder targets where it does not, each target shown with its evidence and
    3x pass line (founder's decision, 22 Oct) (loan marketplace: 35% apply a year, 2.5 KYC'd users reached a saver; Rs 100 a day); online retention 38% at a
    year (operator 21 Oct: SBI's Rs 250 daily SIP, no loans), 24% (savings apps) as the downside, 45% (credit hook) as the upside.
Reconciled with the seed plan: the seed budgets Rs 600 a saver while the brand is new (months 4-18); Rs 450 from month 19.
Critical review fixes (22 Oct, reviews/2026-10-21/CRITICAL_REVIEW.md; founder decisions the same day):
  - serving: tech Rs 4 a month for every KYC'd user reached (the 2 Oct costing), weekly debits at Rs 2 each until BSE StAR MF
    and the fund houses confirm a daily SIP on one mandate; the LTV's cost to win carries the plan's 10% contingency (Rs 495);
  - loan reach applies only to the 35% funnel (personal/business, gold, property, home); gold loans 70% approved;
  - insurance: a fixed referral fee through the broker, to be agreed, not counted (no share of a broker's commission);
    Choti SIP incentive and digital gold off (the daily SIP disqualifies Choti; no digital gold at launch).
Doorstep: operator 21 Oct, "90% online and 10% offline" (was 80/20) -> 1 in 10 savers from doorstep agents (55% still saving at
a year, agreed street retention); the online-only case stops them after the 18-month test.

How it works
  1. Per-saver age profiles from model/cohort_engine.py (agreed inputs, tables/dist_agreed_v1.csv) with the online overrides
     in saver_inputs(): fund trail, loan marketing fees, cards, 17 cross-sell products, active savers, AUM. One profile per
     calendar cohort (the agreed take-up and approval growth with the pool's history; held after year 5).
  2. Savers won a month: the seed plan for months 4-18 (97,200 online sign-ups, 1 in 5 save, + doorstep), then a straight
     ramp to a level by month 30, then growth g a year. Cumulative savers won are capped at 20% of a 7 crore pool (agreed).
  3. Costs: acquisition (CAC x online savers won; doorstep agents), team (the seed team to month 18, then headcount rules),
     tech, office, compliance, support, brand. EBITDA; tax 25% on profit after losses carried forward. Interest on cash is
     NOT counted (investment review F10).
  4. Money needed = seed + the deepest cumulative cash hole after it + a Rs 5 crore floor.
  5. Lenses at month 60 (as before; review F01-F03: close to one test): 20x revenue run-rate and 0.45x AUM; $1B at Rs 95.
Writes tables/online_unit.csv, online_frontier.csv, online_levers.csv, online_unicorn.csv, online_<case>_yearly.csv."""
import csv
import math
from pathlib import Path

import numpy as np

import cohort_engine as ce

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "tables"

FX = 95.0                          # operator 21 Oct
CR, LAKH = 1e7, 1e5
M = 96                             # 8 years
LAUNCH, SEED_END, RAMP_END = 4, 18, 30
UNICORN = 1e9 * FX
POOL, CAP = 7e7, 0.20              # agreed pool and city cap
SEED_CAC, CAC = 600.0, 450.0       # Rs per online saver won, all-in. Seed: the seed plan's own funnel (Rs 100 a sign-up + Rs 40 KYC
                                   # for 1 in 2, 1 in 5 save). After: operator 21 Oct "Rs 450 base, Rs 300-600 range" (audit: Rs 300 from
                                   # PR-02 is per "customer", undefined; our funnel says Rs 600)
CONTINGENCY = 0.10                 # agreed base convention (company_model.py): 10% on every expensed line, inside EBITDA
COMMISSION_LAG = 2                 # agreed base convention: revenue arrives 2 months after it is earned (cash only)

X0 = ce.likely_inputs(ce.load_dists()[0])
EQ_RETURN, DEBT_RETURN = 0.10, 0.07          # JUDGEMENT: equity 10% a year net (conservative); debt agreed 7%
EQ_TRAIL, DEBT_TRAIL = X0["sip_comm"], X0["trail"]   # agreed: equity SIP commission 0.75%; debt fund 0.35%
OV = {}                                       # lever overrides (what it takes); online saver only for r3 / r12
DOOR = {"r3": 0.80, "r12": X0["r12"]}        # doorstep saver retention (agreed street); the Monte Carlo draws it


def saver_inputs(mix="80/20", doorstep=False):
    x = dict(X0)
    eq = 0.8 if mix == "80/20" else 0.0
    x.update({
        "daily": 100.0, "days": 20.0,                         # operator: Rs 100 a day; agreed ~20 debit days
        "rollover": 1.0,                                      # an SIP has no yearly term payout (the street product did)
        "fund_return": eq * EQ_RETURN + (1 - eq) * DEBT_RETURN,
        "trail": eq * EQ_TRAIL + (1 - eq) * DEBT_TRAIL,
        "sip_takeup": 0.0 if eq else X0["sip_takeup"],        # the core balance IS the equity SIP in the 80/20 base
        # operator 21 Oct: online base 38% still saving at a year = SBI MF's Rs 250 daily SIP (first-time investors, no loans;
        # NG-033 / XO-05: 35.64% stopped at an average age of ~6 months -> a steady ~7% a month -> ~80% at month 3, ~38% at 12).
        # Savings apps (24%, r3 52%) are the downside; the credit hook (45%) the upside. Doorstep: agreed street 80% / 55%.
        "r3": DOOR["r3"] if doorstep else 0.80,
        "r12": DOOR["r12"] if doorstep else 0.38,
        "upi_12": 1.0, "upi_ramp": 2,                         # all UPI (refresh; Bachatt is 100% UPI)
        # loan funnel, operator 21 Oct + research/xs_funnel_2026-10-21.csv: 35% of reachable users apply for a loan a year, 70% of
        # them for personal or business loans (this funnel), 15% gold, 10% against their savings (tiny money, not counted), 3% LAP,
        # 2% home. 30% of first applications approved (eligibility inside it), 70% of repeats. Blended ticket Rs 3 lakh
        # (founder 22 Oct; research found smaller: digital NBFC personal Rs 18.8k-70k, XF-11; merchant loans Rs 50k-5 lakh, XF-09/10). DSA payout 2%
        # (XF-01/02), rising 1.5x by year 5 (company); tenure 12-24 months.
        "eligible": 1.0, "approved_first": 0.30, "approved_repeat": 0.70, **loan_mix(LOAN_APPLY),
        "ticket": 300000.0, "fee": 0.02, "tenure": 18.0,
        "loan_gold_ticket": 100000.0, "loan_gold_comm": 0.005,        # XF-12 (Rs 1.96 lakh industry, smaller for this segment), XF-05
        "loan_lap_ticket": 2500000.0, "loan_lap_comm": 0.01,          # founder 22 Oct (micro-LAP lenders Rs 3.9 lakh, XF-13), XF-04
        "loan_home_ticket": 3000000.0, "loan_home_comm": 0.005,       # founder 22 Oct (India average ~Rs 32 lakh, XL-29; affordable HFCs Rs 6-15 lakh), XF-03
        "fee_early": 0.0, "fee_b3": 0.0,                      # a marketing partner collects nothing
        "kyc_cost": 0.0,                                      # inside the all-in CAC / the doorstep cost
        **OFF_PRODUCTS,
    })
    x.update({k: v for k, v in OV.items() if not (doorstep and k in ("r12", "r3")) and not k.startswith("_")})
    return x


LINES = ("still_saving", "deposits", "balance", "loans", "money_lent_new", "cards", *ce.REVENUE, "income", "cost_support")
_CACHE = {}


def profiles(x):
    key = tuple(sorted((k, round(float(np.mean(v)), 9)) for k, v in x.items()))
    if key not in _CACHE:
        rows = {k: np.full(M, float(np.mean(v))) for k, v in x.items()}
        _CACHE[key] = ce.age_profile(rows, cohort=np.arange(1, M + 1), ages=M, year_cap=5)
    return _CACHE[key]


def calendar(prof, won):
    out = {k: np.zeros(M) for k in LINES}
    for c in range(M):
        if won[c] <= 0:
            continue
        for k in LINES:
            out[k][c:] += won[c] * prof[k][c, :M - c]
    return out


AGENT_SIGNUPS, RAMP = 100.0, (0.5, 2 / 3, 5 / 6)             # agreed signups_run; ramp_months 3
AGENT_COST = 20000 + 3000 + 2000 + 1000                      # salary + statutory + incentive (our estimate) + fidelity cover (agents never handle cash)
HIRE_KIT, AGENT_CHURN = 12000.0 + 3500.0, 0.30              # base_inputs kit + NISM V-A for each agent (REG-036/037)
LEAD_PAY, PER_LEAD = 40000 * 1.1, 10                          # field lead once agents > 5 (a founder below that)
CITY_OFFICE, PER_CITY = 50000.0, 15
DOOR_KYC = 40.0
SEED_ONLINE = 97200 * 0.5 * 0.4 / (SEED_END - LAUNCH + 1)     # seed plan at 90/10: 97,200 online sign-ups, 1 in 5 save = 19,440
DOOR_SHARE = 0.10
TECH_PER_SAVER = 4.0               # Rs a month per KYC'd user reached (the 2 Oct costing; was Rs 1, our judgement)
DEBIT_COST, DEBITS_A_MONTH = 2.0, 52 / 12   # weekly debits at Rs 2 (tri_costs base) until a daily SIP is confirmed in writing
GOLD_APPROVAL = 0.70               # gold loans are secured; the lender's call (our assumption)
OFF_PRODUCTS = {"ins_partner_share": 0.0, "choti_takeup": 0.0, "gold_takeup": 0.0}   # fixed insurance fee not counted; Choti, digital gold off
# Loan marketplace (operator 21 Oct): loan offers go to ANYONE KYC'd from day 1, and a KYC'd user who never saves stays reachable
# as long as a saver does. Online: 5 sign-ups a saver, half complete KYC -> 2.5 KYC'd users reached per online saver won.
# Doorstep: the agent signs a saver 1:1, so 1.0.
SIGNUPS_PER_SAVER, KYC_SHARE = 5.0, 0.5
LOAN_REACH = SIGNUPS_PER_SAVER * KYC_SHARE
LOAN_XS = ("loan_gold", "loan_cd", "loan_vehicle", "loan_home", "loan_lap")
LOAN_REACH_XS = ("loan_gold", "loan_home", "loan_lap")   # inside the 35% funnel: reach every KYC'd user; durables and vehicles: savers only
LOAN_APPLY = 0.35                                     # share of reachable users who apply for a loan a year (operator 21 Oct)
LOAN_MIX = {"apply": 0.70, "loan_gold_takeup": 0.15, "loan_lap_takeup": 0.03, "loan_home_takeup": 0.02}   # 10% against savings: not counted


def loan_mix(total):
    """The total apply rate split across the loan funnels: personal + business (the engine's 'apply'), gold, LAP, home.
    Gold is a once-only referral in the engine, so its approval is folded into its take-up."""
    out = {k: total * v for k, v in LOAN_MIX.items()}
    out["loan_gold_takeup"] *= GOLD_APPROVAL
    return out                                  # Rs a month per active saver (JUDGEMENT), a serving cost                                             # operator 21 Oct: 90% online, 10% offline (share of savers won)


def won_path(level, growth, doorstep_after=True):
    on = np.zeros(M)
    for t in range(LAUNCH, M + 1):
        if t <= SEED_END:
            on[t - 1] = SEED_ONLINE
        elif t <= RAMP_END:
            on[t - 1] = SEED_ONLINE + (level - SEED_ONLINE) * (t - SEED_END) / (RAMP_END - SEED_END)
        else:
            on[t - 1] = level * growth ** ((t - RAMP_END) / 12)
    share = DOOR_SHARE / (1 - DOOR_SHARE)                      # doorstep savers per online saver (1/9 at 10%)
    cum = np.cumsum(on * (1 + share))
    if (cum > POOL * CAP).any():
        i = int(np.argmax(cum > POOL * CAP))
        room = POOL * CAP - (cum[i - 1] if i else 0)
        on[i] *= max(room, 0) / (on[i] * (1 + share))
        on[i + 1:] = 0
    agents = np.zeros(M)
    for t in range(LAUNCH, M + 1):
        if t > SEED_END and not doorstep_after:
            break
        agents[t - 1] = max(1, math.ceil(on[t - 1] * share / AGENT_SIGNUPS)) if on[t - 1] > 0 else 0
    door, start = np.zeros(M), []
    for t in range(LAUNCH, M + 1):
        n = int(agents[t - 1])
        while len(start) < n:
            start.append(t)
        start = start[:n]
        door[t - 1] = sum(AGENT_SIGNUPS * (RAMP[t - s] if t - s < 3 else 1) for s in start)
    return on, door, agents


PAY = {"founder_seed": 1000 * FX, "engineer_seed": 110000, "ops_seed": 30000, "jr_eng_seed": 50000,     # seed plan (operator)
       "founder": 150000 * 1.1, "engineer": 120000 * 1.1, "product": 150000 * 1.1, "compliance": 150000 * 1.1,  # base_inputs
       "ops": 40000 * 1.1, "growth": 120000 * 1.1, "finance": 70000 * 1.1, "risk": 150000 * 1.1}             # + 10% statutory


def headcount(t, active, mkt):
    if t <= SEED_END:          # seed plan: Piyush (CEO), Sandeep (CPTO), engineer m1, ops m4, junior engineer m7
        return {"founder_seed": 2, "engineer_seed": 1, "ops_seed": 1 if t >= 4 else 0, "jr_eng_seed": 1 if t >= 7 else 0}
    return {"founder": 2,                                      # JUDGEMENT rules after the round
            "engineer": min(40, 3 + math.floor(active / 2e5)),
            "product": 1 + math.floor(active / 5e5),
            "compliance": 1,
            "ops": min(400, max(2, math.ceil(active / 2e4))),
            "growth": 1 + math.floor(mkt / 1e7),
            "finance": 1 + math.floor(active / 1e6),
            "risk": 1 if t >= 24 else 0}


def company(level, growth=1.0, cac=CAC, seed_cac=SEED_CAC, mix="80/20", doorstep_after=True, name=None):
    on, door, agents = won_path(level, growth, doorstep_after)
    Con, Cdo = calendar(profiles(saver_inputs(mix)), on), calendar(profiles(saver_inputs(mix, True)), door)
    for k in ("rev_origination", "loans", "money_lent_new", *(f"rev_xs_{q}" for q in LOAN_REACH_XS)):
        if k in Con:
            Con[k] = Con[k] * OV.get("_loan_reach", LOAN_REACH)  # KYC'd non-savers who came with the online saver also borrow
    L = {k: Con[k] + Cdo[k] for k in LINES}
    t = np.arange(1, M + 1)
    fee_mult = 1.0 + 0.5 * np.minimum(t - 1, 59) / 59          # agreed: DSA rate to 1.5x by month 60, held after
    ins = ("hlth_small", "hlth_family", "life_term", "accident", "two_wheeler", "device", "shop")
    rev = {"Fund trail": L["rev_fund"], "Loan marketing fees": L["rev_origination"] * fee_mult, "Cards": L["rev_cards"],
           "Insurance": sum(L[f"rev_xs_{p}"] for p in ins),
           "Other products": sum(L[f"rev_xs_{p}"] for p, *_ in ce.PRODUCTS if p not in ins)}
    revenue = sum(rev.values())
    active = L["still_saving"]
    cac_t = np.where(t <= SEED_END, seed_cac, cac)
    mkt = on * cac_t
    hires = np.r_[agents[0], np.maximum(np.diff(agents), 0)] + agents * AGENT_CHURN / 12
    big = agents > 5
    door_cost = agents * AGENT_COST + big * (np.ceil(agents / PER_LEAD) * LEAD_PAY + np.ceil(agents / PER_CITY) * CITY_OFFICE) \
        + hires * HIRE_KIT + door * DOOR_KYC
    people, heads = np.zeros(M), np.zeros(M)
    for i, tt in enumerate(t):
        h = headcount(tt, active[i], mkt[i])
        rf = (1.07 ** ((tt - SEED_END - 1) // 12)) if tt > SEED_END else 1.0
        people[i] = sum(PAY[r] * n for r, n in h.items()) * rf
        heads[i] = sum(h.values())
    reached = Con["still_saving"] * OV.get("_loan_reach", LOAN_REACH) + Cdo["still_saving"]   # KYC'd users who use the app
    tech = np.where(t <= 3, 1_500_000 / 3, 0) + 150000 + reached * TECH_PER_SAVER  # base_inputs + Rs 4 per KYC'd user reached
    payments = active * DEBIT_COST * DEBITS_A_MONTH
    office = np.where(t <= SEED_END, 75000, 150000 + heads * 10000)
    compliance = np.where(t == 1, 125000, 0) + np.where(t <= SEED_END, 1_000_000, 2_500_000) / 12
    brand = np.where(t > SEED_END, 200000, 0)
    design = np.where(t <= 3, 100000, 0)
    raise_cost = np.where(t == 1, 500000, 0) + np.where(t == SEED_END + 1, 1_500_000, 0)
    support = L["cost_support"] + payments
    contingency = CONTINGENCY * (mkt + door_cost + people + tech + office + compliance + brand + design + raise_cost + support)
    acquisition = mkt + door_cost
    opex = people + tech + office + compliance + brand + design + raise_cost + support + contingency
    ebitda = revenue - acquisition - opex
    tax, carry = np.zeros(M), 0.0
    for i in range(M):
        carry += ebitda[i]
        if carry > 0 and ebitda[i] > 0:
            tax[i] = 0.25 * min(ebitda[i], carry)
    pat = ebitda - tax
    received = np.r_[np.zeros(COMMISSION_LAG), revenue[:-COMMISSION_LAG]]
    cash_flow = pat - revenue + received                      # revenue is booked when earned, cash arrives 2 months later
    cum = np.cumsum(cash_flow)
    need = max(0.0, -cum.min()) + 5 * CR                      # the deepest cash hole + a Rs 5 crore floor
    return {"name": name, "level": level, "growth": growth, "cac": cac, "mix": mix, "doorstep_after": doorstep_after,
            "online_won": on, "door_won": door, "agents": agents, "active": active, "aum": L["balance"], "revenue": revenue,
            "rev": rev, "acquisition": acquisition, "people": people, "opex": opex, "ebitda": ebitda, "pat": pat,
            "heads": heads, "door_cost": door_cost, "loans": L["loans"], "lent": L["money_lent_new"], "money_needed": need, "contingency": contingency,
            "cash_flow": cash_flow}


def positive_from(v):
    neg = np.flatnonzero(v < 0)
    if not neg.size:
        return 1
    last = int(neg[-1]) + 1
    return last + 1 if last < len(v) else None


def lenses(o, month=60):
    return 20 * o["revenue"][month - 1] * 12, 0.45 * o["aum"][month - 1]


def row(o):
    l1, l2 = lenses(o)
    y = lambda a, k: a[12 * (k - 1):12 * k].sum()
    return {"case": o["name"], "online savers won a month (m30 on)": round(o["level"]), "growth a year": o["growth"],
            "savers won by m60": round(o["online_won"][:60].sum() + o["door_won"][:60].sum()),
            "active savers m60": round(o["active"][59]), "AUM m60 Rs cr": round(o["aum"][59] / CR),
            "Y5 revenue Rs cr": round(y(o["revenue"], 5) / CR, 1), "Y5 EBITDA Rs cr": round(y(o["ebitda"], 5) / CR, 1),
            "Y8 revenue Rs cr": round(y(o["revenue"], 8) / CR, 1), "Y8 EBITDA Rs cr": round(y(o["ebitda"], 8) / CR, 1),
            "EBITDA positive from month": positive_from(o["ebitda"]) or "after m96",
            "money needed $M": round(o["money_needed"] / FX / 1e6, 1),
            "20x ARR m60 Rs cr": round(l1 / CR), "0.45x AUM m60 Rs cr": round(l2 / CR), "$1B on both at m60": bool(min(l1, l2) >= UNICORN)}


def yearly(o):
    out = []
    for k in range(1, 9):
        s, e = slice(12 * (k - 1), 12 * k), 12 * k - 1
        r = {"year": k, "online savers won": round(o["online_won"][s].sum()), "doorstep savers won": round(o["door_won"][s].sum()),
             "active savers (end)": round(o["active"][e]), "AUM Rs cr (end)": round(o["aum"][e] / CR, 1)}
        for nm, v in o["rev"].items():
            r[f"{nm} Rs cr"] = round(v[s].sum() / CR, 3)
        r.update({"Revenue Rs cr": round(o["revenue"][s].sum() / CR, 3), "Acquisition Rs cr": round(o["acquisition"][s].sum() / CR, 3),
                  "Team Rs cr": round(o["people"][s].sum() / CR, 3),
                  "Other costs Rs cr": round((o["opex"][s].sum() - o["people"][s].sum()) / CR, 3),
                  "EBITDA Rs cr": round(o["ebitda"][s].sum() / CR, 3), "PAT Rs cr": round(o["pat"][s].sum() / CR, 3),
                  "Heads (end)": int(o["heads"][e]), "Doorstep agents (end)": int(o["agents"][e])})
        out.append(r)
    return out


def unit_rows():
    rows = []
    door_cac = unit_rows_door_cac()
    for nm, x, c, rch in (("Online saver", saver_inputs(), CAC, LOAN_REACH), ("Doorstep saver", saver_inputs(doorstep=True), door_cac, 1.0)):
        d = ltv_parts(x, rch)
        p, inc, serve = d["_p"], d["income"], d["serving"]
        cum = np.cumsum(inc - serve)
        c = c * (1 + CONTINGENCY)
        pay = int(np.argmax(cum >= c)) + 1 if (cum >= c).any() else None
        r = {"saver": nm, "cost to win Rs": round(c), "still saving at 12 months": round(float(p["still_saving"][0][12]), 3),
             "revenue 24 months Rs": round(inc[:24].sum()), "revenue 60 months Rs": round(inc[:60].sum()),
             "revenue 96 months Rs": round(inc.sum()), "support 60 months Rs": round(p["cost_support"][0][:60].sum()),
             "serving 60 months Rs": round(serve[:60].sum()), "pays back its cost in month": pay or "never",
             "fund trail 60m Rs": round(d["Fund fees"][:60].sum()), "loan fees 60m Rs": round(d["personal and business loans"][:60].sum()),
             "cards 60m Rs": round(d["Cards"][:60].sum()), "insurance 60m Rs": round(d["Insurance"][:60].sum())}
        r["other products and other lenders' loans 60m Rs"] = r["revenue 60 months Rs"] - r["fund trail 60m Rs"] - r["loan fees 60m Rs"] - r["cards 60m Rs"] - r["insurance 60m Rs"]
        r["all loan referrals 60m Rs"] = round(d["Loans (all referrals)"][:60].sum())
        r["loan reach (KYC'd users per saver won)"] = rch
        r["personal and business loans per saver won, 60m"] = round(float(p["loans"][0][:60].sum() * rch), 4)
        rows.append(r)
    return rows


LTV_INS = ("hlth_small", "hlth_family", "life_term", "accident", "two_wheeler", "device", "shop")


def ltv_parts(x, reach=None):
    """One saver won, months 1-96: revenue by line and serving cost. Loans count every KYC'd user reached with the saver (online
    LOAN_REACH, doorstep 1) and the company's loan-fee ramp (1x to 1.5x by month 60; a month-1 joiner's age = the calendar month)."""
    p = profiles(x)
    reach = OV.get("_loan_reach", LOAN_REACH) if reach is None else reach
    t = np.arange(1, M + 1)
    fee_mult = 1.0 + 0.5 * np.minimum(t - 1, 59) / 59
    orig0 = p["rev_origination"][0]
    xsl0 = sum(p[f"rev_xs_{q}"][0] for q in LOAN_XS)
    xsr0 = sum(p[f"rev_xs_{q}"][0] for q in LOAN_REACH_XS)
    ins = sum(p[f"rev_xs_{q}"][0] for q in LTV_INS)
    fund, cards, inc0 = p["rev_fund"][0], p["rev_cards"][0], p["income"][0]
    other = inc0 - fund - orig0 - xsl0 - ins - cards
    orig = orig0 * fee_mult * reach
    loan = orig + xsr0 * reach + (xsl0 - xsr0)
    serve = p["cost_support"][0] + p["still_saving"][0] * (TECH_PER_SAVER * reach + DEBIT_COST * DEBITS_A_MONTH)
    return {"Fund fees": fund, "Loans (all referrals)": loan, "Insurance": ins, "Cards": cards, "Other products": other,
            "personal and business loans": orig, "income": fund + loan + ins + cards + other, "serving": serve, "_p": p}


def ltv_view(x, cac, months=60, reach=None):
    cac = cac * (1 + CONTINGENCY)                             # the plan spends the cost to win plus its 10% contingency
    d = ltv_parts(x, reach)
    cum = np.cumsum(d["income"] - d["serving"])
    pay = int(np.argmax(cum >= cac)) + 1 if (cum >= cac).any() else None
    net = cum[months - 1]
    return d, cum, {"cost to win Rs": round(cac), "revenue 60m Rs": round(d["income"][:months].sum()), "serving 60m Rs": round(d["serving"][:months].sum()),
                    "contribution 60m Rs": round(net), "LTV/CAC 60m": round(net / cac, 2), "net after cost to win 60m Rs": round(net - cac),
                    "LTV/CAC 96m": round(cum[-1] / cac, 2), "pays back in month": pay or "after month 96"}


def ltv_tables():
    door_cac = unit_rows_door_cac()
    lines, curve = [], []
    for nm, x, c, rch in (("Online saver", saver_inputs(), CAC, LOAN_REACH), ("Doorstep saver", saver_inputs(doorstep=True), door_cac, 1.0)):
        d, cum, v = ltv_view(x, c, reach=rch)
        c = c * (1 + CONTINGENCY)
        lines.append({"saver": nm, "line": "Cost to win", "Rs over 60 months": -round(c)})
        for k in ("Fund fees", "Loans (all referrals)", "Insurance", "Cards", "Other products"):
            lines.append({"saver": nm, "line": k, "Rs over 60 months": round(float(d[k][:60].sum()))})
        lines.append({"saver": nm, "line": "Serving (support + tech)", "Rs over 60 months": -round(float(d["serving"][:60].sum()))})
        lines.append({"saver": nm, "line": "Net over 60 months", "Rs over 60 months": round(float(cum[59] - c))})
        for m in range(97):
            curve.append({"saver": nm, "month": m, "cumulative net Rs": round(float((cum[m - 1] if m else 0.0) - c), 1)})
    write("online_ltv_waterfall.csv", lines)
    write("online_ltv_curve.csv", curve)
    rows = []
    for nm, ov in LEVERS:
        OV.clear()
        OV.update(ov)
        rows.append({"case": nm, **ltv_view(saver_inputs(), CAC)[2]})
    OV.clear()
    for nm, cac in (("Cost to win Rs 300", 300.0), ("Cost to win Rs 600 (our funnel)", 600.0)):
        rows.append({"case": nm, **ltv_view(saver_inputs(), cac)[2]})
    rows.append({"case": "Debt-only funds", **ltv_view(saver_inputs("debt"), CAC)[2]})
    write("online_ltv_levers.csv", rows)
    write("online_loan_funnel.csv", loan_funnel_rows())
    return rows


def loan_funnel_rows():
    """Per 100 online savers won, first 60 months: who sees loan offers, how many apply and borrow, by loan type."""
    x = saver_inputs()
    p = profiles(x)
    t = np.arange(1, M + 1)
    fee_mult = 1.0 + 0.5 * np.minimum(t - 1, 59) / 59
    users = 100 * LOAN_REACH                                   # KYC'd users reached per 100 online savers won
    n = 60
    rows = [{"stage": "sign-ups", "per 100 savers won": 100 * SIGNUPS_PER_SAVER},
            {"stage": "KYC'd users who see loan offers", "per 100 savers won": users},
            {"stage": "still reachable at month 12", "per 100 savers won": users * float(p["still_saving"][0][12])},
            {"stage": "personal + business loan applications, 5 years", "per 100 savers won": users * float(p["applications"][0][:n].sum())},
            {"stage": "personal + business loans (first + repeat), 5 years", "per 100 savers won": users * float(p["loans"][0][:n].sum())}]
    types = [("Personal + business", float(p["loans"][0][:n].sum() + p["topups"][0][:n].sum()), float(p["money_lent_new"][0][:n].sum()),
              x["fee"], float((p["rev_origination"][0] * fee_mult)[:n].sum()), users)]
    for q, nm in (("loan_gold", "Gold"), ("loan_lap", "Loan against property"), ("loan_home", "Home"),
                  ("loan_cd", "Consumer durable"), ("loan_vehicle", "Two-wheeler / e-rickshaw")):
        k = float(p[f"takeups_{q}"][0][:n].sum())
        who = users if q in LOAN_REACH_XS else 100.0              # durables and vehicles: savers only
        types.append((nm, k, k * x[f"{q}_ticket"], x[f"{q}_comm"], float(p[f"rev_xs_{q}"][0][:n].sum()), who))
    for nm, k, lent, fee, rev, who in types:
        rows.append({"stage": f"type: {nm}", "per 100 savers won": who * k, "lent Rs per 100 savers won": who * lent,
                     "average loan Rs": lent / k if k else 0.0, "payout at the start": fee, "our fees Rs per saver won": who * rev / 100})
    cols = ["stage", "per 100 savers won", "lent Rs per 100 savers won", "average loan Rs", "payout at the start", "our fees Rs per saver won"]
    return [{c: r.get(c, "") for c in cols} for r in rows]


def unit_rows_door_cac():
    o = company(20000, 1.0, name="door cac")
    return float(o["door_cost"][30:].sum() / o["door_won"][30:].sum())


CAPTURE_POOL, CAPTURE_CAP, CAPTURE_TARGET = 30e7, 1 / 3, 1e8   # operator 21 Oct: capture 10 crore savers by month 96,
                                                             # a third of a 30 crore self-employed + small-business segment


def capture_plan():
    """The level (online savers won a month from month 30, flat) that wins 10 crore savers by month 96, run on a 30 crore pool capped at 1/3."""
    global POOL, CAP
    keep = (POOL, CAP)
    try:
        POOL, CAP = CAPTURE_POOL, 1.0
        lo, hi = 1e4, 1e8
        for _ in range(80):
            mid = (lo + hi) / 2
            on, door, _ag = won_path(mid, 1.0)
            lo, hi = (mid, hi) if (on + door).sum() < CAPTURE_TARGET * 0.9999 else (lo, mid)
        level = round(hi)
        POOL, CAP = CAPTURE_POOL, CAPTURE_CAP
        o = company(level, 1.0, name="Capture 10 crore savers")
    finally:
        POOL, CAP = keep
    return level, o


def write(name, rows):
    with (TAB / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


FRONTIER = (10000, 20000, 40000, 80000, 150000, 250000)
LEVER_LEVEL = 20000                                   # one change at a time, at the plan's own level (review 21 Oct)
LEVERS = (("The plan", {}), ("24% still saving at a year (savings apps)", {"r12": 0.2415, "r3": 0.52}),
          ("45% still saving at a year", {"r12": 0.45}), ("Rs 200 a day", {"daily": 200.0}),
          ("Rs 300 a day", {"daily": 300.0}), ("10% apply for a loan a year", loan_mix(0.10)),
          ("50% apply for a loan a year", loan_mix(0.50)), ("Loan offers to savers only", {"_loan_reach": 1.0}),
          ("Credit-hungry: 45% stay + 50% apply", {"r12": 0.45, **loan_mix(0.50)}))


def main():
    unit = unit_rows()
    write("online_unit.csv", unit)
    front = [row(company(lv, 1.0, name=f"{lv:,} online savers a month")) for lv in FRONTIER]
    write("online_frontier.csv", front)
    lev = []
    for nm, ov in LEVERS:
        OV.clear()
        OV.update(ov)
        lev.append(row(company(LEVER_LEVEL, 1.0, name=nm)))
    OV.clear()
    for nm, cac in (("Cost to win Rs 300", 300.0), ("Cost to win Rs 600 (our funnel)", 600.0)):
        lev.append(row(company(LEVER_LEVEL, 1.0, cac=cac, name=nm)))
    lev.append(row(company(LEVER_LEVEL, 1.0, mix="debt", name="Debt-only funds")))
    lev.append(row(company(LEVER_LEVEL, 1.0, doorstep_after=False, name="Online only after m18")))
    write("online_levers.csv", lev)
    ltv_tables()
    # unicorn test at a flat 2.5 lakh online savers a month: stays under the 20% pool cap through month 60 (numbers review:
    # a growing path hit the cap at m55 and its "profit from m55" was spend stopping, not the business)
    uni = []
    hungry = {"r12": 0.45, **loan_mix(0.50)}
    for nm, ov in (("The plan", {}), ("Rs 300 a day", {"daily": 300.0}), ("Credit-hungry", hungry),
                   ("Credit-hungry + Rs 200 a day", {**hungry, "daily": 200.0}),
                   ("Credit-hungry + Rs 300 a day", {**hungry, "daily": 300.0})):
        OV.clear()
        OV.update(ov)
        o = company(250000, 1.0, name=nm)
        r = row(o)
        stop = np.flatnonzero((np.arange(1, M + 1) > SEED_END) & (o["online_won"] <= 0))
        r["online sign-ups stop at the pool cap in month"] = int(stop[0]) + 1 if stop.size else "not by m96"
        uni.append(r)
    OV.clear()
    write("online_unicorn.csv", uni)
    level, o = capture_plan()
    r = row(o)
    on_tot, door_tot = float(o["online_won"].sum()), float(o["door_won"].sum())
    r.update({"online savers won a month (m30 on)": level, "savers won by m96": round(on_tot + door_tot),
              "sign-ups needed at 1 in 5": round(on_tot * 5 + door_tot),
              "online savers per sign-up if the whole segment signs up": round(on_tot / (CAPTURE_POOL - door_tot), 3),
              "segment": CAPTURE_POOL, "share captured": CAPTURE_CAP,
              "doorstep agents m60": int(o["agents"][59]), "heads m60": int(o["heads"][59])})
    write("online_capture.csv", [r])
    write("online_capture_10cr_yearly.csv", yearly(o))
    for nm, lv in (("evidence_20k", 20000), ("evidence_150k", 150000)):
        write(f"online_{nm}_yearly.csv", yearly(company(lv, 1.0, name=nm)))
    OV.update({"r12": 0.45, **loan_mix(0.50)})
    write("online_credit_hungry_80k_yearly.csv", yearly(company(80000, 1.0, name="credit hungry 80k")))
    OV.clear()
    keep = ("case", "saver", "EBITDA positive from month", "money needed $M", "Y5 EBITDA Rs cr", "Y8 EBITDA Rs cr", "active savers m60",
            "20x ARR m60 Rs cr", "0.45x AUM m60 Rs cr", "revenue 60 months Rs", "pays back its cost in month", "cost to win Rs",
            "$1B on both at m60")
    for f, rows in (("unit", unit), ("frontier", front), ("levers", lev), ("unicorn", uni)):
        print(f"== {f}")
        for r in rows:
            print({k: v for k, v in r.items() if k in keep})


if __name__ == "__main__":
    main()

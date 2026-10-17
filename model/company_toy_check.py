"""Company toy for Google Sheets, UNICORN TRACK (story/BRIEF_unicorn_plan_2026-10-17.md, operator 17 Oct 2026): the numpy twin of
the company tabs written by model/company_gsheet.py, the reconciliation against the full model (model/unicorn_plan.py ->
tables/unicorn_yearly.csv, unicorn_monthly.csv, unicorn_rounds.csv, unicorn_milestones.csv) and a replay of every company formula
through toy_check's Sheets interpreter (together with the toy tabs it reads).

The plan: 300 agents by month 18 on the earlier ramp, then +200 a month, capped at 7,500, then replace leavers only; the central
team "as built" (no lean hold); funding = the rounds table (seed at m0, rounds A-E at the end of their months); 96 company months.
Beyond month 60 (as the full model): take-up and approval growth held at their year-5 values, the fee multiplier held at 1.5x,
the agent pay rate 0.10% of balance (pay_after) instead of 0.25%.

How the toy stacks agents (all on the sheet, documented on README):
  * Per sign-up lines come from the toy's 'Per saver' tab (year-1 terms; ages 1-96, rows 62-97 extend the toy's 60) and the
    company's own calendar factors on 'Company monthly' (take-up and approval growth held after year 5, the never-borrowed pool
    adjustment, the fee ramp held after month 60); company month = toy month.
  * Books: a growth hire opens a book; the agents path is the hiring plan; 30% leave a year (whole agents, as the full model);
    a leaver's replacement inherits the book. Instead of drawing who leaves, every book carries the EXPECTED effect:
      - savers and every later line of a book's cohorts fall by the handover loss at the leave rate: x (1 - 10% x 2.5%) a month;
      - a book's sign-ups use the expected ramp of whoever holds it (a replacement restarts the ramp) and the decline on the
        book's age; its agent-cost split uses the expected acquisition share of the holder's tenure.
  * Book-level costs that are not linear (helpers above an agent's 400 visits a day, cash cover = max(Rs 1,000, 0.015% of his
    cash), the capped pay on balance) are worked on the average book of each age.
  * Every agent draws the LIKELY sign-up level and decline (the full model draws them per agent).
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohort_engine as ce  # noqa: E402
import company_model as C  # noqa: E402
import toy_check as tc  # noqa: E402

T = tc.T
N = 96                       # company months (the unicorn tables run to m96)
SPEC = T / "company_gsheet_spec.json"
LAKH, CRORE = 1e5, 1e7
INS, INV, PAY, OTH = ce.INSURANCE, ("sip", "choti", "nps", "gold", "fd"), ("recharge", "bills"), ("loan_gold", "loan_cd", "loan_vehicle")
YEAR_HOLD = 5                # take-up and approval growth held at this calendar year's value after it
LENS_MONTH = 60
UNICORN = 10_000 * CRORE
ROUNDS_CSV = T / "base_rounds.csv"
CITY_CSV = T / "base_city_plan.csv"
INPUTS_CSV = T / "base_inputs.csv"
OFFSETS = (0, 3, 6, 12, 24, 36, 48, 60, 72, 84)   # the City plan's tenure points (months after launch)


def rounds_table():
    """[(round, month, amount, pre-money, ESOP top-up 1/0)] from tables/base_rounds.csv (the full model's plan)."""
    out = []
    for r in csv.DictReader(ROUNDS_CSV.open()):
        out.append((r["Round"], float(r["Month"]), float(r["Amount (Rs)"]), float(r["Pre-money (Rs)"]),
                    1.0 if r["Round"] in ("Seed", "A", "B") else 0.0))
    out += [("(spare)", 0.0, 0.0, 0.0, 0.0)] * SPARE_ROUNDS
    return out


SPARE_ROUNDS = 2             # empty rows in the rounds table for the operator to add a round (month 0, amount 0 = unused)


def funding_inputs():
    """The blue inputs on 'Funding & cap table': name -> (value, label, unit, format, note)."""
    return {
        "arr_mult": (20.0, "Revenue lens: valuation = this x ARR (ARR = 12 x the month's revenue)", "x ARR", "mult", "OUR JUDGEMENT"),
        "aum_mult": (0.45, "AUM lens: valuation = this x AUM at month end", "x AUM", "mult2",
                     "OUR JUDGEMENT. SAV-03: Stable Money's Rs 2,507 crore post-money on about Rs 5,000 crore invested (SAV-02); that is "
                     "cumulative money invested, not AUM, so a rough proxy"),
        "pb_mult": (3.0, "Lens 3 (cross-check): valuation = this x NBFC book equity + arr_mult x fee ARR", "x equity", "mult",
                    "OUR JUDGEMENT: fintech NBFC price-to-book"),
        "unicorn": (UNICORN, "Unicorn threshold: $1B at Rs 100 a dollar", "Rs", "inr", "Rs 10,000 crore (the operator's Rs 100/$)"),
        "lens_month": (float(LENS_MONTH), "Month of the unicorn check", "month", "num0", "year 5 ends"),
        "esop_target": (0.10, "ESOP pool after a top-up round (share of the post-money)", "share", "pct", "created at the seed, topped up at A and B"),
        "unicorn_round": ("E", "The unicorn round (its name in the rounds table)", "round", "text", "the full model's E at m57"),
    }


def base_input(prefix):
    """A value from tables/base_inputs.csv, by the start of its Input text."""
    for r in csv.DictReader(INPUTS_CSV.open()):
        if r["Input"].startswith(prefix):
            return float(str(r["Value"]).replace(",", ""))
    raise KeyError(prefix)


def plan_params():
    """The base fleet path (tables/base_inputs.csv): agents at m18, hires a month after, the agent cap."""
    return base_input("Agents by month 18"), base_input("Hires a month after month 18"), base_input("Agent cap")


def city_plan():
    """[(city, rank, addressable, launch month, [agents at each tenure point])] from tables/base_city_plan.csv."""
    out = []
    for r in csv.DictReader(CITY_CSV.open()):
        pts = [float(r["Agents in the launch month"])] + [float(r[f"Agents at launch +{o_} months"]) for o_ in OFFSETS[1:]]
        out.append((r["City"], float(r["Rank"]), float(r["Addressable (urban self-employed)"]), float(r["Launch month"]), pts,
                    r["Month it nears its cap (95%; AUTO run, information only)"]))
    return out


def company_inputs():
    """Name -> (value, label, unit, format, note). Order = the 'Company inputs' tab."""
    a18, h, cap = plan_params()
    x = ce.likely_inputs()
    res = tc.full_run(x)
    fm = res["monthly"]
    grp = lambda ps: sum(fm[f"rev_xs_{q}"][0].sum() for q in ps)
    tot = grp(INS + INV + PAY + OTH)
    I = {}
    I["agents_m18"] = (a18, "Agents on the street at month 18 (the earlier ramp, scaled)", "agents", "num0", "base: 300 (check only: the company's agents are summed from the City plan)")
    I["hires_after"] = (h, "Growth hires a month after month 18", "agents a month", "num0", "base: 150 (check only)")
    I["agent_cap"] = (cap, "Agent cap: no growth hires beyond this many agents (leavers are always replaced)", "agents", "num0",
                      "base: 5,000 (check only)")
    I["attrition_y"] = (C.ATTRITION_YEAR, "Agents who leave a year (replaced the next month; the new agent inherits the book)", "a year", "pct", "")
    I["handover_loss"] = (C.HANDOVER_LOSS, "Savers who stop when their agent is replaced", "share", "pct", "")
    I["acq_early"] = (C.ACQ_SHARE_EARLY, "Acquisition share of an agent's cost, his months 1-12", "share", "pct", "the rest is servicing")
    I["acq_m60"] = (C.ACQ_SHARE_M60, "Acquisition share at his month 60 and after (straight line from month 12)", "share", "pct", "")
    I["acq_flat"] = (float(C.ACQ_FLAT_MONTHS), "Months the early share holds", "months", "num0", "")
    I["pay_months"] = (float(ce.GROWTH_MONTHS), "Agent pay on balance at the toy's rate (Inputs: agent_pay) in company months 1 to", "month", "num0",
                       "the full model's growth phase")
    I["pay_after"] = (ce.AGENT_PAY_AFTER, "Agent pay on balance after that month", "a year", "pct2", "agreed rule after company month 60")
    I["year_hold"] = (float(YEAR_HOLD), "Take-up and approval growth held after calendar year", "year", "num0", "as the full model's 96-month run")
    I["pool"] = (base_input("Addressable pool"), "Addressable pool: urban self-employed (information; the City plan carries each city's share)", "people", "inr",
                 "NG-002; estimate, not census. Our judgement")
    I["city_q"] = (base_input("Rank-size exponent q"), "Rank-size exponent q (information: how the City plan's addressable was estimated)", "", "f3",
                   "fitted so 4,000 towns add to the pool; NCR = 6.3% of urban India. Our judgement")
    I["city_cap"] = (base_input("City cap"), "City cap: most of a city's pool we can ever sign", "share of the city's pool", "pct", "operator tap: 20%")
    I["sat_power"] = (2.0, "Saturation curve: sign-ups x (1 - (penetration / cap) ^ this); 2 = the soft curve, 1 = a straight line", "power", "num0",
                      "lead's decision: soft. Our judgement")
    I["refill"] = (base_input("Pool refill"), "Pool refill: each city's pool (and cap) grows this much a year", "a year", "pct", "new shops, migrants. Our judgement")
    I["max_new_cities"] = (base_input("Most new cities a month"), "Most new cities a month (information: the City plan already keeps to it)", "cities a month",
                           "num0", "operational pace. Our judgement")
    I["open_headroom"] = (base_input("Open the next city"), "Open the next city when the best city's headroom a head is below (information: the AUTO rule behind the City plan)",
                          "sign-ups a head", "inr", "searched. Our judgement")
    I["city_launch"] = (C.CITY_LAUNCH, "City launch cost, once per new city", "Rs", "inr", "")
    I["city_office"] = (C.CITY_OFFICE, "City office a month", "Rs a month", "inr", "")
    I["city_mgr_pay"] = (C.CITY_MANAGER_PAY, "City manager pay a month (one per city)", "Rs a month", "inr", "plus statutory and 7% raises")
    I["team_lead_pay"] = (C.TEAM_LEAD_PAY, "Team lead pay a month", "Rs a month", "inr", "plus statutory and 7% raises")
    I["agents_per_tl"] = (float(C.AGENTS_PER_TEAM_LEAD), "Agents per team lead (rounded up)", "agents", "num0", "")
    I["scale_after"] = (float(C.SCALE_AFTER), "Engineers and ops executives scale only after month", "month", "num0", "")
    I["scale_base"] = (float(C.SCALE_BASE_AGENTS), "...beyond this many agents", "agents", "num0", "")
    I["scale_per"] = (float(C.SCALE_PER_AGENTS), "...+1 each per this many agents (rounded down)", "agents", "num0", "")
    I["risk_pay"], I["risk_agents"] = (150000.0, "Risk and fraud lead pay a month", "Rs a month", "inr", ""), (float(C.RISK_LEAD_AGENTS), "...from the month the fleet reaches", "agents", "num0", "")
    I["cashrec_pay"], I["cashrec_per"] = (35000.0, "Cash reconciliation executive pay a month", "Rs a month", "inr", ""), (float(C.CASH_REC_PER), "...one per this many agents (rounded up)", "agents", "num0", "")
    I["hr_pay"], I["hr_per"] = (50000.0, "HR and recruiting executive pay a month", "Rs a month", "inr", ""), (float(C.HR_PER), "...one per this many agents (rounded up)", "agents", "num0", "")
    I["support_pay"], I["support_savers"] = (60000.0, "Customer support lead pay a month", "Rs a month", "inr", ""), (float(C.SUPPORT_LEAD_SAVERS), "...from the month savers reach", "savers", "num0", "")
    I["lean_hold"] = (0.0, "Lean hold: no engineer/ops scale-ups, risk lead or support lead until EBITDA first turns positive (1 = on)", "1/0", "num0",
                      "base: off (central team as built)")
    I["statutory"] = (C.STATUTORY, "Statutory on central and field-management pay", "share", "pct", "")
    I["raise_rate"] = (C.RAISE, "Pay rise each company year (everyone, agents and the cap too)", "a year", "pct", "")
    I["laptop"], I["tools"] = (C.LAPTOP, "Laptop per central hire (capitalised)", "Rs", "inr", ""), (C.TOOLS, "Tools per central person a month", "Rs a month", "inr", "")
    I["agent_stat"], I["agent_kit"] = (C.AGENT_STATUTORY, "Agent statutory a month", "Rs a month", "inr", ""), (C.AGENT_KIT, "Hiring and kit per hire (replacements too)", "Rs", "inr", "")
    I["cash_cover_rate"] = (C.CASH_COVER_RATE, "Cash cover: share of his cash collected, if above the flat cover", "share", "pct3", "")
    I["app_base"] = (C.APP_BASE, "App cloud, SMS and KYC tools a month", "Rs a month", "inr", "")
    I["integrations"] = (C.INTEGRATIONS, "App integrations, months 1-3 (capitalised)", "Rs", "inr", "")
    I["dep_months"] = (float(C.DEPRECIATION_MONTHS), "Depreciation, straight line over", "months", "num0", "")
    I["lic_once"] = (sum(v for _, v in C.LICENCE_ONE_TIME), "Licences and setup, one-time (month 1)", "Rs", "inr", "")
    I["lic_year"] = (sum(v for _, v in C.LICENCE_YEARLY), "Licences and compliance a year", "Rs a year", "inr", "")
    I["hq"], I["travel"], I["brand"] = (C.HQ, "Head office a month", "Rs a month", "inr", ""), (C.TRAVEL, "Travel a month", "Rs a month", "inr", ""), (C.BRAND, "Brand marketing a month", "Rs a month", "inr", "")
    I["bureau"], I["fraud"] = (C.BUREAU, "Bureau pull per loan application and top-up", "Rs", "inr", ""), (C.FRAUD, "Fraud provision on cash collected", "share", "pct3", "")
    I["tax_rate"], I["contingency"] = (C.TAX, "Income tax after past losses", "share", "pct", ""), (C.CONTINGENCY, "Contingency on every expensed cost", "share", "pct", "")
    I["interest_rate"] = (C.INTEREST_RATE, "Interest on cash at the start of each month", "a year", "pct", "no interest on a negative balance")
    I["seed_cost"] = (C.SEED_COST, "Seed raise cost (month 1)", "Rs", "inr", "")
    I["round_cost"] = (C.SERIES_A_COST, "Raise cost of each later round, booked in its month (+ contingency)", "Rs", "inr", "")
    I["xs_ins"] = (grp(INS) / tot, "Cross-sell split: insurance (after the broker's share)", "share", "pct", "full model, 60-month money at the likely values")
    I["xs_inv"] = (grp(INV) / tot, "Cross-sell split: investments (SIP, Choti SIP, NPS, gold, FD)", "share", "pct", "")
    I["xs_pay"] = (grp(PAY) / tot, "Cross-sell split: payments (recharge, bills)", "share", "pct", "")
    I["xs_oth"] = (grp(OTH) / tot, "Cross-sell split: other lenders' loans (gold, consumer, vehicle)", "share", "pct", "")
    I["nb_licence_month"] = (base_input("NBFC-ICC acquired"), "NBFC-ICC acquired or built in company month", "month", "num0", "LEV-031; industry guide, not verified")
    I["nb_licence_cost"] = (base_input("Licence cost"), "NBFC licence cost, once (central costs)", "Rs", "inr", "LEV-031; industry guide, not verified")
    I["nb_nof"] = (base_input("Net owned funds"), "Net owned funds held as NBFC capital from the licence month", "Rs", "inr", "RBI minimum for an NBFC-ICC; published")
    I["nb_opex"] = (base_input("NBFC opex: credit"), "NBFC opex: credit, risk, compliance, treasury, a month from the licence month", "Rs a month", "inr", "Our judgement")
    I["nb_opex_500"] = (base_input("NBFC opex that scales"), "NBFC opex per Rs 500 crore of book, a month (pro rata)", "Rs a month", "inr", "Our judgement")
    I["nb_start"] = (base_input("On-book lending starts"), "On-book lending starts in company month", "month", "num0", "operator tap: NBFC from year 3")
    I["nb_share"] = (base_input("On-book share of personal-loan volume"), "On-book share of personal-loan volume (first, repeat, top-ups), flat from the start",
                     "share", "pct", "operator: '30% on book' (the best-quality part by credit score)")
    I["nb_loss"] = (base_input("Lifetime credit loss"), "Lifetime credit loss after recoveries, the agreed loss (likely)", "share of money lent", "pct",
                    "agreed input (likely 3%; Paytm worst 5%)")
    I["nb_loss_mult"] = (base_input("On-book loss as a multiple"), "On-book loss as a multiple of the agreed loss", "x", "mult2", "judgement: the top 30% by score")
    I["nb_yield"] = (base_input("Yield on the outstanding book"), "Yield on the outstanding book (the agreed EMI rate)", "a year", "pct", "LEV-012 25-28%; industry guide")
    I["nb_proc"] = (base_input("Processing fee at disbursal"), "Processing fee at disbursal, paid by the borrower", "share of the loan", "pct", "Our judgement")
    I["nb_cof"] = (base_input("Cost of borrowings"), "Cost of funds on borrowings", "a year", "pct", "LEV-014/015; industry guide, not verified")
    I["nb_leverage"] = (base_input("Borrowings at most"), "Borrowings at most this multiple of NBFC equity", "x equity", "mult", "LEV-023 (AUM/TNW 3.25x)")
    I["nb_floor_min"] = (0.15, "Capital floor: regulatory minimum (information; equity = book / (1 + leverage) = 25% holds above it)", "share of the book", "pct",
                         "published")
    I["nb_floor_op"] = (0.20, "Capital floor: operating floor (information)", "share of the book", "pct", "brief")
    plan = {"plan_m": [float(m) for m, _ in C.GROWTH_POINTS[:7]], "plan_s": [float(a) for _, a in C.GROWTH_POINTS[:7]]}
    role_tab = []
    for role, dep, pay, steps, scales in C.CENTRAL:
        (f1, c1), (f2, c2) = (steps[0], steps[-1])
        role_tab.append((role, dep, pay, float(c1), float(f1), float(c2), float(f2), 1.0 if scales else 0.0))
    return I, plan, role_tab


def calendar(v, g):
    """Company calendar factors, months 1..N (the toy's Monthly factors, held after year_hold; the fee ramp held after month 60)."""
    t = np.arange(1, N + 1, dtype=float)
    y = np.floor((t - 1) / 12) + 1
    yc = np.where(y > g("year_hold"), g("year_hold"), y)
    raw = (1 + v["takeup_growth"]) ** (yc - 1)
    tf = np.where(raw > 2, 2.0, raw)
    af = (1 + v["approval_growth"]) ** (yc - 1)
    cap = lambda share: np.where(share * af > 0.8, 0.8 / share, af)
    loanf = tf * cap(v["approved_first"])
    q = tc.derived(v)["loan_q"]
    pool = np.cumprod((1 - q * loanf) / (1 - q)) * (1 - q) / (1 - q * loanf)
    lf0 = loanf * pool
    lag = lambda f, k: f[np.maximum(1, t - k).astype(int) - 1]
    mt = {"yc": yc, "tf": tf, "af": af, "loanf": loanf, "cardf": tf * np.where(af > 2, 2.0, af), "homef": tf * cap(v["home_approval"]),
          "lapf": tf * cap(v["lap_approval"]), "pool": pool, "lf0": lf0, "lf12": lag(lf0, tc.COLL_LAG), "lf20": lag(lf0, tc.TOPUP_LAG)}
    mt["fee"] = v["fee"] * (v["fee_mult_start"] + (v["fee_mult_end"] - v["fee_mult_start"]) * (np.minimum(t, 60) - 1) / 59)
    mt["payrate"] = np.where(t <= g("pay_months"), v["agent_pay"], g("pay_after"))
    return mt


def cap_table(rounds, esop):
    """rounds: [(name, month, amount, pre, esop_flag)] -> rows with post, dilution, founders %, ESOP %, investors %."""
    f, e, vv = 1.0, 0.0, 0.0
    out = []
    for nm, m, amt, pre, fl in rounds:
        post = pre + amt
        dn = amt / post if post else 0.0
        if fl >= 0.5:
            rest = 1 - dn - esop
            f, vv, e = f / (f + vv) * rest, vv / (f + vv) * rest + dn, esop
        else:
            f, e, vv = f * (1 - dn), e * (1 - dn), vv * (1 - dn) + dn
        out.append({"round": nm, "month": m, "amount": amt, "pre": pre, "post": post, "dilution": dn, "founders": f, "esop": e,
                    "investors": vv})
    return out


def city_agents(cplan):
    """Agents by city and month (N, C): 0 before launch, straight lines between the tenure points, flat after, whole agents."""
    Cn = len(cplan)
    ag = np.zeros((N, Cn))
    for c, (_nm, _rk, _addr, L, pts, _note) in enumerate(cplan):
        for m in range(1, N + 1):
            dd = m - L
            if dd < 0:
                continue
            i = max(j for j in range(len(OFFSETS)) if OFFSETS[j] <= dd)
            val = pts[i] if i == len(OFFSETS) - 1 else pts[i] + (pts[i + 1] - pts[i]) * (dd - OFFSETS[i]) / (OFFSETS[i + 1] - OFFSETS[i])
            ag[m - 1, c] = math.floor(val + 0.5)
    return ag


def company(v, I, plan, role_tab, rounds, cplan=None):
    """The company tabs' maths. v: toy inputs; I: {name: value}; plan: ramp shape; role_tab: role rows; rounds: the rounds table;
    cplan: the City plan (None = the fleet path and the old city rule)."""
    T_ = tc.toy(v, N)
    p, d = T_["p"], T_["d"]
    g = lambda k: I[k]
    mt = calendar(v, g)
    t = np.arange(1, N + 1, dtype=float)
    pm, ps = plan["plan_m"], plan["plan_s"]
    o = {"month": t, "year": np.floor((t - 1) / 12) + 1}
    o.update({f"cal_{k}": val for k, val in mt.items()})

    def interp(m):
        i = max(j for j in range(len(pm)) if pm[j] <= m)
        return ps[i] if i == len(pm) - 1 else ps[i] + (ps[i + 1] - ps[i]) * (m - pm[i]) / (pm[i + 1] - pm[i])
    rnd = lambda z: math.floor(z + 0.5)
    o["fleet_path"] = np.array([rnd(min(g("agent_cap"), interp(m) * g("agents_m18") / ps[-1] if m <= 18
                                        else g("agents_m18") + g("hires_after") * (m - 18))) for m in t], float)
    # per book (book age 1..N)
    pr = g("attrition_y") / 12
    ho = 1 - g("handover_loss") * pr
    ramp = lambda k: (min(1.0, 0.5 + 0.5 * (k - 1) / v["ramp"]) if v["ramp"] > 0 else 1.0)
    share = lambda k: g("acq_early") if k <= g("acq_flat") else g("acq_early") + (g("acq_m60") - g("acq_early")) * (min(k, 60) - g("acq_flat")) / (60 - g("acq_flat"))
    wts = lambda b: [pr * (1 - pr) ** (k - 1) if k < b else (1 - pr) ** (b - 1) for k in range(1, b + 1)]
    cb = {"decline": np.array([1.0 if b <= 12 else 1 + (v["signup_decline_y5"] - 1) * min(1.0, (b - 12) / 37) for b in t]),
          "eramp": np.array([sum(w * ramp(k) for k, w in enumerate(wts(int(b)), 1)) for b in t]),
          "eshare": np.array([sum(w * share(k) for k, w in enumerate(wts(int(b)), 1)) for b in t])}
    cb["signups"] = v["signups"] * I.get("agent_level", 1.0) * cb["decline"] * cb["eramp"]
    convho = lambda prof, vec: np.array([sum(vec[c] * prof[i - c] * ho ** (i - c) for c in range(i + 1)) for i in range(N)])
    conv = lambda prof, vec: np.array([sum(vec[c] * prof[i - c] for c in range(i + 1)) for i in range(N)])
    cashdep_ps = p["deposits"] * (1 - p["upi"])
    cb["visits"], cb["balance"], cb["cashdep"] = convho(p["visits"], cb["signups"]), convho(p["balance"], cb["signups"]), convho(cashdep_ps, cb["signups"])
    # the cities: agents and new books by city from the City plan; sign-ups slowed by each city's penetration
    if cplan is not None:
        ag = city_agents(cplan)
        nbc = ag - np.vstack([np.zeros(ag.shape[1]), ag[:-1]])
        Cm = np.array([[cb["signups"][m - k] if m >= k else 0.0 for k in range(N)] for m in range(N)])
        U = Cm @ nbc
        addr = np.array([c[2] for c in cplan])
        capc = g("city_cap") * addr[None, :] * (1 + g("refill")) ** ((t[:, None] - 1) / 12)
        cum = np.zeros_like(U)
        for i in range(N):
            prev = cum[i - 1] if i else np.zeros(U.shape[1])
            fac = 1 - (prev / capc[i]) ** g("sat_power")
            fac = np.where(fac > 0, fac, 0.0)
            s_ = U[i] * fac
            rem = np.where(capc[i] - prev > 0, capc[i] - prev, 0.0)
            cum[i] = prev + np.where(s_ > rem, rem, s_)
        Sc = cum - np.vstack([np.zeros(cum.shape[1]), cum[:-1]])
        launch = np.array([c[3] for c in cplan])
        o["_city"] = {"agents": ag, "newbooks": nbc, "unsat": U, "cum": cum, "signups": Sc, "cap": capc, "addr": addr, "launch": launch}
        o["agents"] = ag.sum(axis=1)
        o["newbooks"] = nbc.sum(axis=1)
        o["signups"] = Sc.sum(axis=1)
        o["signups_unsat"] = U.sum(axis=1)
        o["cities"] = np.array([float((launch <= m).sum()) for m in t])
    else:
        o["agents"] = o["fleet_path"]
        o["newbooks"] = o["agents"] - np.concatenate([[0.0], o["agents"][:-1]])
        o["signups"] = conv(cb["signups"], o["newbooks"])
        o["signups_unsat"] = o["signups"]
        o["cities"] = np.where(t >= 18, np.maximum(3, np.ceil(o["agents"] / 50 - 1e-12)), np.where(t >= 9, 2.0, 1.0))
    A, NB = o["agents"], o["newbooks"]
    o["cumleave"] = np.cumsum(g("attrition_y") / 12 * A)
    fl = np.floor(o["cumleave"] + 1e-9)
    o["leavers"] = fl - np.concatenate([[0.0], fl[:-1]])
    o["hired"] = o["newbooks"] + np.concatenate([[0.0], o["leavers"][:-1]])
    o["teamleads"] = np.ceil(A / g("agents_per_tl") - 1e-12)
    o["rm"] = (1 + g("raise_rate")) ** (o["year"] - 1)
    o["extra"] = np.where(t > g("scale_after"), np.floor(np.where(A > g("scale_base"), A - g("scale_base"), 0) / g("scale_per")), 0.0)
    steps = np.array([[c2 if m >= f2 else (c1 if m >= f1 else 0.0) for (_r, _d, _p, c1, f1, c2, f2, _s) in role_tab] for m in t])
    pays = np.array([r[2] for r in role_tab])
    scal = np.array([r[7] for r in role_tab])
    o["risk_raw"] = (np.maximum.accumulate(A) >= g("risk_agents")).astype(float)
    o["cashrec"] = np.ceil(A / g("cashrec_per") - 1e-12)
    o["hr"] = np.ceil(A / g("hr_per") - 1e-12)
    # customers
    o["signups_adj"] = o["signups"] / mt["pool"]
    o["savers"] = convho(p["saving"], o["signups"])
    o["balance"] = convho(p["balance"], o["signups"])
    o["aum"] = convho(p["saving"] * p["end_active"], o["signups"])
    o["cashdep"] = convho(cashdep_ps, o["signups"])
    o["visits"] = convho(p["visits"], o["signups"])
    # the saturation ratio for the per-book costs: the books' balance, visits and cash as if every city were unsaturated, x this
    sr = lambda a, b: np.where(b > 0, a / np.where(b > 0, b, 1.0), 1.0)
    o["r_bal"] = sr(o["balance"], convho(p["balance"], o["signups_unsat"]))
    o["r_vis"] = sr(o["visits"], convho(p["visits"], o["signups_unsat"]))
    o["r_cd"] = sr(o["cashdep"], convho(cashdep_ps, o["signups_unsat"]))
    o["apps"] = convho(p["apps"], o["signups_adj"]) * mt["tf"] * mt["pool"]
    o["loans"] = convho(p["loans"], o["signups_adj"]) * mt["lf0"]
    o["topups"] = convho(p["topups"], o["signups_adj"]) * mt["lf20"]
    o["lent_new"] = convho(p["lent"], o["signups_adj"]) * mt["lf0"]
    o["lent"] = o["lent_new"] + o["topups"] * d["topup_amt"]
    o["home_n"] = convho(p["home"], o["signups"]) * mt["homef"]
    o["lap_n"] = convho(p["lap"], o["signups"]) * mt["lapf"]
    o["housing_lent"] = o["home_n"] * v["home_ticket"] + o["lap_n"] * v["lap_ticket"]
    o["support_raw"] = (np.maximum.accumulate(o["savers"]) >= g("support_savers")).astype(float)
    # the NBFC: a flat on-book share of personal-loan volume from the start month
    o["nb_share"] = np.where(t >= g("nb_start"), g("nb_share"), 0.0)
    o["nb_share12"] = np.where(t - tc.COLL_LAG >= g("nb_start"), g("nb_share"), 0.0)
    o["nb_disb"] = o["nb_share"] * o["lent"]
    # fee revenue (DSA origination on the off-book share only; collection fees on on-book loans are internal)
    o["r_fund"] = o["balance"] * v["trail"] / 12
    o["r_orig"] = o["lent_new"] * mt["fee"] * (1 - v["taken_back"]) * (1 - o["nb_share"])
    o["r_topup"] = o["topups"] * d["topup_amt"] * mt["fee"] * (1 - v["taken_back"]) * (1 - o["nb_share"])
    o["r_house"] = o["home_n"] * v["home_ticket"] * v["home_fee"] + o["lap_n"] * v["lap_ticket"] * v["lap_fee"]
    o["xs"] = convho(p["xs"], o["signups"]) * mt["tf"]
    for k in ("ins", "inv", "pay", "oth"):
        o[f"r_{k}"] = o["xs"] * g(f"xs_{k}")
    o["r_cards"] = convho(p["cards"], o["signups"]) * mt["cardf"] * v["card_fee"]
    o["r_coll"] = convho(p["collect"], o["signups_adj"]) * mt["lf12"] * (1 - o["nb_share12"])
    o["fee_rev"] = sum(o[k] for k in ("r_fund", "r_orig", "r_topup", "r_house", "r_ins", "r_inv", "r_pay", "r_oth", "r_cards", "r_coll"))
    # the book: each month's on-book loans amortise on the EMI schedule at the yield over the tenure
    iy = g("nb_yield") / 12
    Tn = tc.derived(v)["tenure_m"]
    frac = np.array([((1 + iy) ** Tn - (1 + iy) ** min(j, Tn)) / ((1 + iy) ** Tn - 1) if j <= Tn else 0.0 for j in range(N)])
    o["nb_book_gross"] = conv(frac, o["nb_disb"])
    lo = g("nb_loss") * g("nb_loss_mult")
    o["nb_book"] = (1 - lo) * o["nb_book_gross"]
    prev_ = lambda a: np.concatenate([[0.0], a[:-1]])
    o["nb_interest"] = iy * (1 - lo) * prev_(o["nb_book_gross"])
    lic = t >= g("nb_licence_month")
    o["nb_equity"] = np.where(lic, np.maximum(g("nb_nof"), o["nb_book"] / (1 + g("nb_leverage"))), 0.0)
    o["nb_borrow"] = np.maximum(0.0, o["nb_book"] - o["nb_equity"])
    o["nb_idle"] = np.maximum(0.0, o["nb_equity"] - o["nb_book"])
    o["nb_cof"] = g("nb_cof") / 12 * prev_(o["nb_borrow"])
    o["nb_nii"] = o["nb_interest"] - o["nb_cof"]
    o["nb_proc"] = g("nb_proc") * o["nb_disb"]
    o["nb_credit"] = lo * o["nb_disb"]
    o["nb_opex"] = np.where(lic, g("nb_opex") + g("nb_opex_500") * o["nb_book"] / (500 * CRORE), 0.0)
    o["nb_lic"] = np.where(t == g("nb_licence_month"), g("nb_licence_cost"), 0.0)
    o["revenue"] = o["fee_rev"] + o["nb_nii"] + o["nb_proc"]
    o["c_bureau"] = g("bureau") * (o["apps"] + o["topups"])
    o["c_fraud"] = g("fraud") * o["cashdep"]
    o["direct"] = o["c_bureau"] + o["c_fraud"]
    o["cm1"] = o["revenue"] - o["direct"] - o["nb_credit"]
    # servicing (per-book costs on the average book of each age, scaled by the saturation ratios)
    o["agent_base"] = A * (v["salary"] + g("agent_stat")) * o["rm"]
    cap = lambda i, j: min(mt["payrate"][i] / 12 * cb["balance"][i - j] * o["r_bal"][i], v["incentive_cap"] * o["rm"][i])
    o["incentive"] = np.array([sum(NB[j] * cap(i, j) for j in range(i + 1)) for i in range(N)])
    o["agent_acq"] = (o["rm"] * (v["salary"] + g("agent_stat")) * conv(cb["eshare"], NB)
                      + np.array([sum(NB[j] * cb["eshare"][i - j] * cap(i, j) for j in range(i + 1)) for i in range(N)]))
    o["agent_serv"] = o["agent_base"] + o["incentive"] - o["agent_acq"]
    hlp = lambda vv: (vv - v["capacity"]) * v["extra_cost"] / 400 if vv > v["capacity"] else 0.0
    cov = lambda cc: g("cash_cover_rate") * cc if g("cash_cover_rate") * cc > v["cash_cover"] else v["cash_cover"]
    o["helpers"] = np.array([sum(NB[j] * hlp(cb["visits"][i - j] * o["r_vis"][i]) for j in range(i + 1)) for i in range(N)])
    o["cover"] = np.array([sum(NB[j] * cov(cb["cashdep"][i - j] * o["r_cd"][i]) for j in range(i + 1)) for i in range(N)])
    o["running"] = o["savers"] * v["running"]
    rms = o["rm"] * (1 + g("statutory"))
    o["tl_cost"] = o["teamleads"] * g("team_lead_pay") * rms
    o["cm_cost"] = o["cities"] * g("city_mgr_pay") * rms
    o["office_cost"] = o["cities"] * g("city_office")
    o["servicing"] = o["agent_serv"] + o["helpers"] + o["cover"] + o["running"] + o["tl_cost"] + o["cm_cost"] + o["office_cost"]
    o["cm2"] = o["cm1"] - o["servicing"]
    o["leads"] = o["signups"] * v["online_lead_share"] * v["lead_cost"]
    o["kyc_cost"] = o["signups"] * v["kyc"]
    o["kit"] = o["hired"] * g("agent_kit")
    o["launch"] = (o["cities"] - np.concatenate([[0.0], o["cities"][:-1]])) * g("city_launch")
    o["brand_cost"] = np.full(N, g("brand"))
    o["acquisition"] = o["agent_acq"] + o["leads"] + o["kyc_cost"] + o["kit"] + o["launch"] + o["brand_cost"]
    o["cm3"] = o["cm2"] - o["acquisition"]
    # central: the held plan first (for the lean-hold trigger), then the final team
    o["app_cost"], o["lic_y"] = np.full(N, g("app_base")), np.full(N, g("lic_year") / 12)
    o["lic_o"] = np.where(t == 1, g("lic_once"), 0.0)
    o["hq_cost"], o["travel_cost"] = np.full(N, g("hq")), np.full(N, g("travel"))
    rc = {}
    for nm, m, amt, pre, _fl in rounds:
        if m >= 1 and amt > 0:
            rc[m] = rc.get(m, 0.0) + g("round_cost")
    o["raise_cost"] = np.where(t == 1, g("seed_cost"), 0.0) + np.array([rc.get(m, 0.0) for m in t])
    fixed = o["app_cost"] + o["lic_y"] + o["lic_o"] + o["hq_cost"] + o["travel_cost"] + o["raise_cost"] + o["nb_opex"] + o["nb_lic"]
    o["pay_held"] = (steps @ pays + o["cashrec"] * g("cashrec_pay") + o["hr"] * g("hr_pay")) * rms
    o["tools_held"] = (steps.sum(axis=1) + o["cashrec"] + o["hr"]) * g("tools")
    o["ebitda_held"] = o["cm3"] - ((o["pay_held"] + o["tools_held"] + fixed) * (1 + g("contingency"))
                                   + g("contingency") * (o["direct"] + o["servicing"] + o["acquisition"]))
    pos = np.nonzero(o["ebitda_held"] > 0)[0]
    hold = (float(pos[0] + 1) if pos.size else float(N)) if g("lean_hold") >= 0.5 else 0.0
    o["_hold"] = hold
    roles = steps + scal[None, :] * np.where(t > hold, o["extra"], 0.0)[:, None]
    o["risk"] = np.where(t > hold, o["risk_raw"], 0.0)
    o["support"] = np.where(t > hold, o["support_raw"], 0.0)
    allhc = np.column_stack([roles, o["risk"], o["cashrec"], o["hr"], o["support"]])
    o["hc_central"] = allhc.sum(axis=1)
    o["pay_central"] = (roles @ pays + o["risk"] * g("risk_pay") + o["cashrec"] * g("cashrec_pay") + o["hr"] * g("hr_pay")
                        + o["support"] * g("support_pay")) * rms
    o["joiners"] = np.maximum(0, allhc - np.vstack([np.zeros(allhc.shape[1]), allhc[:-1]])).sum(axis=1)
    o["tools_cost"] = o["hc_central"] * g("tools")
    o["contingency_cost"] = g("contingency") * (o["direct"] + o["servicing"] + o["acquisition"] + o["pay_central"] + fixed + o["tools_cost"])
    o["central"] = o["pay_central"] + fixed + o["tools_cost"] + o["contingency_cost"]
    o["ebitda"] = o["cm3"] - o["central"]
    o["capex_lap"] = o["joiners"] * g("laptop")
    o["capex_int"] = np.where(t <= 3, g("integrations") / 3, 0.0)
    capex = o["capex_lap"] + o["capex_int"]
    dm = int(g("dep_months"))
    o["depreciation"] = np.array([capex[max(0, i - dm + 1):i + 1].sum() / g("dep_months") for i in range(N)])
    o["ebit"] = o["ebitda"] - o["depreciation"]
    fee = o["fee_rev"]
    o["cf_receivable"] = -(fee - np.concatenate([[0.0, 0.0], fee[:-2]]))          # commissions arrive 2 months late (fees only)
    o["cf_book"] = -(o["nb_book"] - prev_(o["nb_book"])) - (o["nb_idle"] - prev_(o["nb_idle"]))
    o["cf_investing"] = -capex + o["cf_book"]
    o["cf_borrow"] = o["nb_borrow"] - prev_(o["nb_borrow"])
    seed0 = sum(amt for _n, m, amt, _p, _f in rounds if m < 1)
    o["cf_financing"] = np.array([sum(amt for _n, m, amt, _p, _f in rounds if max(1.0, m) == mm) for mm in t])
    r = {k: np.zeros(N) for k in ("opening", "interest", "pbt", "losses", "tax", "pat", "cfo", "net", "cash")}
    pool, prev = 0.0, 0.0
    for i in range(N):
        opening = prev + (seed0 if i == 0 else 0.0)
        r["opening"][i] = opening
        r["interest"][i] = g("interest_rate") / 12 * max(0.0, opening)
        pp = o["ebit"][i] + r["interest"][i]
        use = min(pool, max(pp, 0.0))
        r["tax"][i] = g("tax_rate") * max(0.0, pp - use)
        pool = pool - use + max(0.0, -pp)
        r["losses"][i], r["pbt"][i] = pool, pp
        r["pat"][i] = pp - r["tax"][i]
        r["cfo"][i] = r["pat"][i] + o["depreciation"][i] + o["cf_receivable"][i]
        r["net"][i] = r["cfo"][i] + o["cf_investing"][i] + o["cf_financing"][i] + o["cf_borrow"][i]
        prev += r["net"][i]
        r["cash"][i] = prev
    o.update(r)
    o["arr"] = 12 * o["revenue"]
    o["fee_arr"] = 12 * o["fee_rev"]
    o["rev_lens"] = I["arr_mult"] * o["arr"]
    o["aum_lens"] = I["aum_mult"] * o["aum"]
    o["book_lens"] = I["pb_mult"] * o["nb_equity"] + I["arr_mult"] * o["fee_arr"]
    o["_cb"] = cb
    return o


# ---------------------------------------------------------------- summary rows (label, value from o, full-model reference, kind)
def breakeven(e):
    if e[-1] <= 0:
        return "not within 96 months"
    neg = np.nonzero(e <= 0)[0]
    return float(neg.max() + 2) if neg.size else 1.0


def yr(a, y):
    return float(a[12 * (y - 1):12 * y].sum())


def ref_tables():
    mo = list(csv.DictReader((T / "base_monthly.csv").open()))
    col = lambda k: np.array([float(r[k]) for r in mo])
    return col


def lens(o, I):
    m = int(I["lens_month"]) - 1
    arr, aum = float(o["arr"][m]), float(o["aum"][m])
    return arr, aum, I["arr_mult"] * arr, I["aum_mult"] * aum


SUMMARY_HEADS = ("NBFC (on-book lending from month 30)", "UNICORN CHECK AT MONTH 60 (the three lenses are our judgement)",
                 "CASH, BREAK-EVEN AND FUNDING", "SCALE AND CITIES")


def summary_rows(o, I, rounds):
    """(label, value, full-model reference, kind) in 'Company summary' order (row 2 on)."""
    col = ref_tables()
    Fy = lambda k, y: float(col(k)[12 * (y - 1):12 * y].sum())
    F60 = lambda k, m=60: float(col(k)[m - 1])
    REV, EB, PAT = ("Revenue, total (fee revenue + net interest income + processing fees) (Rs)", "EBITDA (Rs)", "PAT (net profit after tax) (Rs)")
    f_cash, f_eb = col("Closing cash, with every round (Rs)"), col(EB)
    m = int(I["lens_month"])
    arr, aum = float(o["arr"][m - 1]), float(o["aum"][m - 1])
    l1, l2, l3 = float(o["rev_lens"][m - 1]), float(o["aum_lens"][m - 1]), float(o["book_lens"][m - 1])
    f_arr = 12 * F60(REV)
    f_fee_arr = 12 * F60("Fee revenue, total (distribution commissions and DSA fees) (Rs)")
    f_aum, f_eq = F60("Money in the fund at month end (AUM) (Rs)"), F60("NBFC: equity in the book (capital held) (Rs)")
    f1, f2, f3 = 20 * f_arr, 0.45 * f_aum, 3 * f_eq + 20 * f_fee_arr
    U_ = I["unicorn"]
    ct = cap_table(rounds, I["esop_target"])
    uni = next(r for r in ct if r["round"] == I["unicorn_round"])
    f_ct = {r["Round"]: r for r in csv.DictReader(ROUNDS_CSV.open())}
    cum_su = np.cumsum(o["signups"])
    f_cum = np.cumsum(col("Sign-ups"))
    rows = []
    for y in range(1, 9):
        rows.append((f"Revenue, year {y} (fees + net interest income + processing fees)", yr(o["revenue"], y), Fy(REV, y), "inr"))
    for y in range(1, 9):
        rows.append((f"EBITDA, year {y}", yr(o["ebitda"], y), Fy(EB, y), "inr"))
    for y in range(1, 9):
        rows.append((f"PAT, year {y}", yr(o["pat"], y), Fy(PAT, y), "inr"))
    rows += [
        (SUMMARY_HEADS[0], None, None, "head"),
        ("Fee revenue, year 5", yr(o["fee_rev"], 5), Fy("Fee revenue, total (distribution commissions and DSA fees) (Rs)", 5), "inr"),
        ("Net interest income, year 5", yr(o["nb_nii"], 5), Fy("NBFC: net interest income (Rs)", 5), "inr"),
        ("Processing fees, year 5", yr(o["nb_proc"], 5), Fy("NBFC: processing fees (2% of on-book loans) (Rs)", 5), "inr"),
        ("Credit cost (provisions), year 5", yr(o["nb_credit"], 5), Fy("Credit cost: expected-loss provisions on the book (Rs)", 5), "inr"),
        ("Loan book, net of provisions, month 60", float(o["nb_book"][59]), F60("NBFC: loan book, net of provisions (Rs)"), "inr"),
        ("NBFC equity (capital held), month 60", float(o["nb_equity"][59]), f_eq, "inr"),
        ("NBFC borrowings, month 60", float(o["nb_borrow"][59]), F60("NBFC: borrowings (Rs)"), "inr"),
        (SUMMARY_HEADS[1], None, None, "head"),
        ("ARR at month 60 (12 x the month's fees + NII + processing fees)", arr, f_arr, "inr"),
        ("AUM at month 60 (money in the fund, month end)", aum, f_aum, "inr"),
        ("Lens 1: arr_mult x ARR (20x agreed)", l1, f1, "inr"),
        ("Lens 2: aum_mult x AUM (0.45x agreed)", l2, f2, "inr"),
        ("Lens 3 (cross-check): pb_mult x NBFC equity + arr_mult x fee ARR (3x and 20x)", l3, f3, "inr"),
        ("Lens 1 margin over the threshold (Rs 10,000 crore)", l1 / U_ - 1, f1 / UNICORN - 1, "pct"),
        ("Lens 2 margin over the threshold", l2 / U_ - 1, f2 / UNICORN - 1, "pct"),
        ("Lens 3 margin over the threshold", l3 / U_ - 1, f3 / UNICORN - 1, "pct"),
        ("Unicorn on paper at month 60 (lenses 1 and 2 both clear)", "yes" if min(l1, l2) >= U_ else "no", "yes" if min(f1, f2) >= UNICORN else "no", "text"),
        (SUMMARY_HEADS[2], None, None, "head"),
        ("Lowest month-end cash, months 1-96", float(o["cash"].min()), float(f_cash.min()), "inr"),
        ("Month of the lowest cash", float(o["cash"].argmin() + 1), float(f_cash.argmin() + 1), "month"),
        ("Closing cash at month 60", float(o["cash"][59]), float(f_cash[59]), "inr"),
        ("Closing cash at month 96", float(o["cash"][-1]), float(f_cash[-1]), "inr"),
        ("EBITDA break-even month (stays positive from here)", breakeven(o["ebitda"]), breakeven(f_eb), "month"),
        ("Equity raised by month 60 (rounds table)", float(sum(r[2] for r in rounds if r[1] <= I["lens_month"])),
         float(sum(float(r["Amount (Rs)"]) for r in f_ct.values() if float(r["Month"]) <= 60)), "inr"),
        ("Founders' share after the unicorn round (E)", uni["founders"], float(f_ct["E"]["Founders % after"]), "pct"),
        (SUMMARY_HEADS[3], None, None, "head"),
        ("Savers still saving, month 60", float(o["savers"][59]), F60("Savers still saving"), "num0"),
        ("Agents working, month 60", float(o["agents"][59]), F60("Agents working"), "num0"),
        ("Cities open, month 60", float(o["cities"][59]), F60("Cities"), "num0"),
        ("Central team, month 60", float(o["hc_central"][59]), F60("Central team, total"), "num0"),
        ("Cumulative sign-ups to month 60", float(cum_su[59]), float(f_cum[59]), "num0"),
        ("National penetration at month 60 (cumulative sign-ups / the pool)", float(cum_su[59]) / I["pool"], float(f_cum[59]) / I["pool"], "pct"),
        ("Money lent in year 5, personal loans incl. top-ups (on and off our book)", yr(o["lent"], 5), Fy("Money lent, personal loans incl. top-ups (Rs)", 5), "inr"),
        ("Money lent in year 5, home loans and LAP (other lenders)", yr(o["housing_lent"], 5), Fy("Home loans and LAP lent by other lenders (Rs)", 5), "inr"),
    ]
    return rows


def write(name, rows):
    with (T / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def reconcile():
    v = tc.likely_toy_inputs()
    I, plan, role_tab = company_inputs()
    Iv = {k: val[0] for k, val in {**I, **funding_inputs()}.items()}
    rounds = rounds_table()
    o = company(v, Iv, plan, role_tab, rounds, city_plan())
    rows = []
    for label, val, ref, kind in summary_rows(o, Iv, rounds):
        if kind == "head":
            continue
        both = isinstance(val, float) and isinstance(ref, float)
        if both and kind in ("pct", "month"):
            gap, gk = val - ref, ("points" if kind == "pct" else "months")
        elif both and ref:
            gap, gk = (val - ref) / abs(ref), "share"
        else:
            gap, gk = "", ""
        rows.append({"measure": label, "toy": val, "full_model": "" if ref is None else ref, "gap_pct": gap, "gap_kind": gk})
    return v, Iv, plan, role_tab, rounds, o, rows


def funding_expected(o, Iv, rounds):
    """The 'Funding & cap table' cells company_gsheet.py lays out: {(row, col): value}."""
    ct = cap_table(rounds, Iv["esop_target"])
    return ct


def main():
    v, Iv, plan, role_tab, rounds, o, rows = reconcile()
    write("base_toy_vs_full.csv", rows)
    bad = [r for r in rows if r["measure"].startswith(("Revenue, year", "EBITDA, year")) and int(r["measure"].split("year ")[1][0]) <= 5
           and abs(r["gap_pct"]) > 0.10]
    fmt = lambda z: z if isinstance(z, str) else (f"{z:.4f}" if abs(z) < 5 else f"{z:,.0f}")
    for r in rows:
        g = r["gap_pct"]
        gs = "" if g == "" else {"share": f"{g:+.1%}", "points": f"{100 * g:+.1f}pt", "months": f"{g:+.0f} mo"}[r["gap_kind"]]
        print(f"  {r['measure'][:58]:<58} toy {fmt(r['toy']):>16} full {fmt(r['full_model']):>16} {gs}")
    print("revenue/EBITDA years 1-5 outside +-10%:", [r["measure"] for r in bad])
    if SPEC.exists():
        toy_spec = json.loads(tc.SPEC.read_text())
        co_spec = json.loads(SPEC.read_text())
        book = tc.Book({"sheets": toy_spec["sheets"] + co_spec["sheets"]})
        errs = book.evaluate_all()
        assert not errs, errs[:8]
        exp, bad2 = [], []
        srows = summary_rows(o, Iv, rounds)
        for i, (label, val, _ref, kind) in enumerate(srows, start=2):
            if kind == "head":
                continue
            got = book.cell("Company summary", i, 2)
            ok = got == val if isinstance(val, str) else (not isinstance(got, str) and abs(got - val) <= 1e-7 * max(1.0, abs(val)))
            exp.append({"cell": f"'Company summary'!B{i}", "measure": label, "expected": val})
            if not ok:
                bad2.append((i, label, got, val))
        assert not bad2, bad2[:5]
        for cell, label, val in co_spec["_funding_expected"]:
            r_, c_ = tc.parse_a1(cell)
            got = book.cell("Funding & cap table", r_, c_)
            ok = got == val if isinstance(val, str) else (not isinstance(got, str) and abs(got - val) <= 1e-7 * max(1.0, abs(val)))
            exp.append({"cell": f"'Funding & cap table'!{cell}", "measure": label, "expected": val})
            if not ok:
                bad2.append((cell, label, got, val))
        assert not bad2, bad2[:5]
        for key, col in co_spec["_monthly_columns"].items():
            got = np.array([float(book.cell("Company monthly", r, tc.col_num(col))) for r in range(2, N + 2)])
            assert np.allclose(got, o[key], rtol=1e-9, atol=1e-6), key
        write("base_toy_expected.csv", exp)
        print(f"company formula replay: {book.n_formulas} formulas (toy + company), 0 errors; {len(exp)} summary and funding cells and "
              f"{len(co_spec['_monthly_columns'])} monthly lines equal the numpy twin")
    return o, rows


if __name__ == "__main__":
    main()

"""Plan search: can the COMPANY be profitable by year 3-4, and what does it take? (operator, 17 Oct 2026)

Operator: "I want to make the company profitable by 3rd - 4th year. Plan accordingly. I dont want this to be a loss making
company. Cant we plan growth like that given huge tam. If yes, how many customers does it take etc.." and, on pay: "salary only
team is tough. i think some incentives have to be there over 20k salary" (tap: 0.25% of balance, capped at Rs 10,000 a month).

Only the levers the operator controls are searched; market inputs stay at the agreed likely values, and each agent keeps his own
sign-up draw as in the company model (company_model.py).
  (a) fleet: agents at m18 in {30, 45, 60, 80} (the base ramp to m18 scaled to that size); after m18, h more agents a month,
      h in {0, 2, 4, 6, 8, 10, 15}; optionally the hiring doubles once EBITDA has been positive for 3 months in a row.
  (b) agent pay: Rs 20,000 + 0.25% a year of his book's balance capped at Rs 10,000 a month per agent (the cap rises 7% a year
      with the salary) = the BASE and the only pay eligible for the recommended plan; caps of Rs 5,000 and Rs 15,000 =
      sensitivity; the uncapped 0.25% and salary only = reference only.
  (c) UPI push: UPI share at month 12 in {30% (agreed), 45%, 60%}: an operational target and a real assumption change, flagged.
  (d) central team: as built (scales with the fleet), or "lean hold": after the launch team, no central hires until EBITDA > 0
      (engineer and ops scale-ups, risk lead, support lead wait), except the cash-reconciliation and HR executives that scale
      per agent; from the month after EBITDA first turns positive the normal rules apply.
The triggers (hiring doubles; lean hold ends) depend on the plan's own EBITDA. Plans use fleets whose agents' draws follow the
hiring order (company_model.make_fleet), so a later change in hiring never changes an earlier month: each trigger is found on one run
and applied on the next, and the unchanged history is asserted.

Writes tables/company_plan_search.csv, company_plan_frontier.csv, company_plan_recommended_*.csv (the company model's tables
for the recommended plan, and its Monte Carlo) and, when no eligible plan breaks even by
m48, company_plan_assumption_needed.csv; company_plan_grid_edge.csv (a note: bigger fleets at m18 than the grid's 80).
"""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import cohort_mc as MC             # noqa: E402
import company_mc as CMC           # noqa: E402
import company_model as C          # noqa: E402

M = C.M
SEED = C.SEED
A18 = (30, 45, 60, 80)
HIRES = (0, 2, 4, 6, 8, 10, 15)
UPIS = (0.30, 0.45, 0.60)
UPI_AGREED = 0.30
CENTRALS = ("as built", "lean hold")
STEP_POSITIVE_MONTHS = 3
TARGET_BE, WINDOW_FROM = 48, 42
PAYS = {  # key: (plain words, input overrides, model options, role)
    "cap10": ("Rs 20,000 + 0.25% of balance, capped at Rs 10,000 a month", {}, {"incentive_cap": 10000.0}, "base (eligible)"),
    "cap5": ("Rs 20,000 + 0.25% of balance, capped at Rs 5,000 a month", {}, {"incentive_cap": 5000.0}, "sensitivity"),
    "cap15": ("Rs 20,000 + 0.25% of balance, capped at Rs 15,000 a month", {}, {"incentive_cap": 15000.0}, "sensitivity"),
    "uncapped": ("Rs 20,000 + 0.25% of balance, uncapped (5 years)", {}, {"incentive_cap": None}, "reference only"),
    "salary": ("Salary only, Rs 20,000", {"agent_balance_pay": 0.0}, {}, "reference only"),
}
ELIGIBLE_PAY = "cap10"
TAKEUP_KEYS = ("apply", "card_share", *[f"{p}_takeup" for p, *_ in E.PRODUCTS])


# ---------------------------------------------------------------- fleet for plans
plan_target, make_plan_fleet, first_positive, step_month = C.plan_target, C.make_fleet, C.first_positive, C.step_month


def run_plan(x, dists, plan, seeds, factors=None, keep=False, profiles=None):
    """plan = (a18, h, stepup, pay, upi, central): company_model.run_plan with that plan's pay and UPI. upi None = as x has it."""
    a18, h, stepup, pay, upi, central = plan
    _nm, over, popts, _role = PAYS[pay]
    xo = {**x, **over, "upi_12": upi} if upi is not None else {**x, **over}
    o, fleets, targets, info = C.run_plan(xo, dists, a18=a18, h=h, stepup=stepup, central=central, opts=popts, seeds=seeds,
                                          factors=factors, keep=keep, profiles=profiles)
    return o, fleets, targets, {**info, "x": xo}


# ---------------------------------------------------------------- the search
def plans():
    for a18 in A18:
        for h in HIRES:
            for stepup in ((False,) if h == 0 else (False, True)):
                for pay in PAYS:
                    for upi in UPIS:
                        for central in CENTRALS:
                            yield (a18, h, stepup, pay, upi, central)


def describe(plan):
    a18, h, stepup, pay, upi, central = plan
    return {"Agents at m18": a18, "Hires a month after m18": h,
            "Hiring doubles after 3 EBITDA-positive months": "yes" if stepup else "no",
            "Agent pay": PAYS[pay][0], "Pay option is": PAYS[pay][3],
            "UPI share at month 12 (target)": upi, "UPI push (an assumption change)": "no" if upi == UPI_AGREED else "yes",
            "Central team": central}


def metrics(o, d=0):
    yr = lambda k, y: float(o[k][d, 12 * (y - 1):12 * y].sum())
    be = C.stays_positive_from(o["ebitda"][d:d + 1])[0]
    fp = first_positive(o["ebitda"][d:d + 1])[0]
    return {"EBITDA break-even month (first positive and staying positive)": "not within 60" if np.isnan(be) else float(be),
            "First month EBITDA positive": float(fp) if fp else "not within 60",
            "Year-3 EBITDA (Rs)": yr("ebitda", 3), "Year-4 EBITDA (Rs)": yr("ebitda", 4),
            "Year-5 revenue (Rs)": yr("revenue", 5), "Year-5 EBITDA (Rs)": yr("ebitda", 5),
            **{f"Savers at m{m}": float(o["still_saving"][d, m - 1]) for m in (36, 48, 60)},
            **{f"Agents at m{m}": float(o["agents"][d, m - 1]) for m in (36, 48, 60)},
            "AUM at m60 (Rs)": float(o["fund_end"][d, -1]), "Money lent in year 5 (Rs)": yr("money_lent", 5),
            f"Cash at m60, with the Rs {C.SERIES_A / C.CRORE:.0f} crore Series A (Rs)": float(o["cash"][d, -1]),
            "Lowest cash, with the Series A, through m60 (Rs)": float(o["cash"][d].min()),
            "Cumulative PAT, 60 months (Rs)": float(o["cum_pat"][d, -1])}


TREASURY_KEYS = ("ebitda", "ebitda_ex_a", "depreciation", "cf_receivable", "cf_investing", "cash_seed_only")


def search(x, dists):
    profiles = {u: C.market_profiles({**x, "upi_12": u}, 1) for u in UPIS}
    rows, stack = [], {k: [] for k in TREASURY_KEYS}
    t0 = time.time()
    for i, plan in enumerate(plans()):
        o, _f, _t, info = run_plan(x, dists, plan, [SEED], profiles=profiles[plan[4]])
        for k in TREASURY_KEYS:
            stack[k].append(o[k][0])
        rows.append({"Plan": i + 1, **describe(plan),
                     "Hiring doubled from month": int(info["step"][0]) + 1 if info["step"][0] else "",
                     "Central scale-up hires released from month": (int(info["release"][0]) + 1 if info["release"][0] else "never")
                     if plan[5] == "lean hold" else "", **metrics(o), "_plan": plan})
    st = {k: np.array(v) for k, v in stack.items()}
    st["_contingency"] = C.CONTINGENCY
    ft = C.funding_tests(st)
    for i, r in enumerate(rows):
        r["Smallest Series A at m18 keeping cash at or above Rs 5 crore through m60 (Rs)"] = float(ft["smallest_a"][i])
        r["Month the seed alone runs out"] = float(ft["seed_runout_month"][i]) if not np.isnan(ft["seed_runout_month"][i]) else "not within 60"
    print(f"  searched {len(rows)} plans in {time.time() - t0:.0f} s")
    return rows


def be_num(r):
    v = r["EBITDA break-even month (first positive and staying positive)"]
    return 999.0 if isinstance(v, str) else v


def frontier(rows, limit):
    """Plans breaking even by `limit`, not beaten on both earlier break-even and more savers at m60."""
    c = sorted([r for r in rows if be_num(r) <= limit], key=lambda r: (-r["Savers at m60"], be_num(r)))
    out, best_be = [], 999.0
    for r in c:                                      # most savers first: keep a plan only if it breaks even earlier than all above
        if be_num(r) < best_be:
            out.append(r)
            best_be = be_num(r)
    return out


def pick(rows):
    """RECOMMENDED: eligible pay (Rs 10,000 cap), breaks even by m48, the most savers at m60; no UPI change if possible."""
    el = [r for r in rows if r["_plan"][3] == ELIGIBLE_PAY and be_num(r) <= TARGET_BE]
    for pool in ([r for r in el if r["_plan"][4] == UPI_AGREED], el):
        if pool:
            return max(pool, key=lambda r: (r["Savers at m60"], -be_num(r))), True
    el = [r for r in rows if r["_plan"][3] == ELIGIBLE_PAY]
    for pool in ([r for r in el if r["_plan"][4] == UPI_AGREED], el):
        if pool:
            return min(pool, key=lambda r: (be_num(r), -r["Year-5 EBITDA (Rs)"])), False


def public(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


# ---------------------------------------------------------------- the recommended plan in full
def full_run(x, dists, plan, prefix):
    o, fleets, targets, info = run_plan(x, dists, plan, [SEED], keep=True)
    h = C.headline(o)
    xo, opts, fleet, target = info["x"], info["opts"], fleets[0], targets[0]
    ck = C.checks(xo, dists, o, h, fleet, None, target=target, opts=opts)
    C.write(f"{prefix}_monthly.csv", C.monthly_rows(o))
    C.write(f"{prefix}_yearly.csv", C.yearly_rows(o))
    C.write(f"{prefix}_pnl_ladder_yearly.csv", C.ladder_rows(o))
    C.write(f"{prefix}_cashflow_yearly.csv", C.cashflow_rows(o))
    C.write(f"{prefix}_headcount.csv", C.headcount_rows(o))
    C.write(f"{prefix}_m18.csv", C.m18_rows(o, h))
    C.write(f"{prefix}_checks.csv", ck)
    bad = [r["Check"] for r in ck if not r["Passes"]]
    print(f"  recommended plan: checks passed {len(ck) - len(bad)}/{len(ck)}" + (f"; FAIL {bad}" if bad else ""))
    assert not bad
    return o, h, info


def plan_mc(x_unused, dists, plan, prefix, n=CMC.DRAWS):
    a18, h_, stepup, pay, upi, central = plan
    _nm, over, popts, _role = PAYS[pay]
    hcat, _x, redraws = CMC.run_mc(n, CMC.SEED, plan={"a18": a18, "h": h_, "stepup": stepup, "central": central, "opts": popts,
                                                      "over": over, "upi": None if upi == UPI_AGREED else upi})
    rows = CMC.summary(hcat, n, redraws)
    rows.insert(1, CMC.val_row("Plan", "", f"m18 {a18} agents; +{h_} a month after m18{' (doubling after 3 positive months)' if stepup else ''}; "
                               f"{PAYS[pay][0]}; UPI {upi:.0%}{' (push)' if upi != UPI_AGREED else ' (agreed, drawn)'}; central {central}"))
    C.write(f"{prefix}_mc_summary.csv", rows)
    return hcat, rows


def breakeven_customers(o, label):
    """How many customers it takes: the plan's own numbers when EBITDA first turns positive, and the rule of thumb
    central costs a month / mature contribution per saver a month (mature = the plan's last year, months 49-60)."""
    fp = int(first_positive(o["ebitda"])[0])
    be = C.stays_positive_from(o["ebitda"])[0]
    R = lambda m, v, u, how: {"Plan": label, "Measure": m, "Value": v, "Unit": u, "How it is worked out": how}
    last = slice(48, 60)
    sv = float(o["still_saving"][0, last].sum())
    cm3_m, cm2_m = float(o["cm3"][0, last].sum()) / sv, float(o["cm2"][0, last].sum()) / sv
    central_last = float(o["central"][0, last].mean())
    rows = [R("Month EBITDA first turns positive", float(fp) if fp else "not within 60", "company month", "first month with EBITDA > 0"),
            R("Month EBITDA turns positive and stays positive", "not within 60" if np.isnan(be) else float(be), "company month", "")]
    if fp:
        i = fp - 1
        v = lambda k: float(o[k][0, i])
        rows += [R("Active savers when EBITDA first turns positive", v("still_saving"), "savers", "savers still saving in that month"),
                 R("Agents then", v("agents"), "agents", ""), R("Savers per agent then", v("still_saving") / v("agents"), "savers an agent", ""),
                 R("Money in the fund (AUM) then", v("fund_end"), "Rs", "end of that month"),
                 R("Revenue that month", v("revenue"), "Rs a month", ""), R("Central costs that month", v("central"), "Rs a month", "")]
    rows += [
        R("Central costs a month, months 49-60", central_last, "Rs a month", "central team, app, licences, HQ, travel, tools, contingency"),
        R("Mature CM3 per active saver a month (months 49-60)", cm3_m, "Rs a saver a month", "after direct, servicing and acquisition costs"),
        R("Rule of thumb: break-even savers = central costs a month / mature CM3 per saver a month",
          central_last / cm3_m if cm3_m > 0 else "CM3 not positive", "savers", "with acquisition running at the plan's pace"),
        R("Mature CM2 per active saver a month (months 49-60)", cm2_m, "Rs a saver a month", "after direct and servicing costs only"),
        R("Rule of thumb if acquisition stopped: central costs / mature CM2 per saver", central_last / cm2_m if cm2_m > 0 else "CM2 not positive",
          "savers", "a floor: the book needed to carry the central team with no growth spend"),
        R("Active savers the plan has at m60", float(o["still_saving"][0, -1]), "savers", ""),
        R("Agents the plan has at m60", float(o["agents"][0, -1]), "agents", ""),
        R("Money in the fund (AUM) at m60", float(o["fund_end"][0, -1]), "Rs", "")]
    return rows


def grid_edge(x, dists):
    """Beyond the grid (a note): bigger fleets at m18, then little or no hiring; eligible pay, UPI 30%, lean hold."""
    rows, st, plist = [], {k: [] for k in TREASURY_KEYS}, []
    for a18 in (80, 100, 120, 150, 200):
        for h in (0, 2):
            plan = (a18, h, False, ELIGIBLE_PAY, UPI_AGREED, "lean hold")
            o, *_ = run_plan(x, dists, plan, [SEED])
            for k in TREASURY_KEYS:
                st[k].append(o[k][0])
            rows.append({**describe(plan), **metrics(o),
                         "Lowest cash, seed only, through m18 (Rs)": float(o["cash_seed_only"][0, :18].min())})
    st = {k: np.array(v) for k, v in st.items()}
    st["_contingency"] = C.CONTINGENCY
    ft = C.funding_tests(st)
    for i, r in enumerate(rows):
        r["Smallest Series A at m18 keeping cash at or above Rs 5 crore through m60 (Rs)"] = float(ft["smallest_a"][i])
        r["Month the seed alone runs out"] = float(ft["seed_runout_month"][i]) if not np.isnan(ft["seed_runout_month"][i]) else "not within 60"
    return rows


def assumption_needed(x, dists, plan):
    """The ONE market assumption, alone, that brings this plan to EBITDA break-even by m48: take-up (all hazards x k), or r12."""
    rows = []

    def be_of(xx):
        o, *_ = run_plan(xx, dists, plan, [SEED])
        v = C.stays_positive_from(o["ebitda"])[0]
        return 999.0 if np.isnan(v) else v
    found = None
    for k in np.round(np.arange(1.01, 2.501, 0.01), 2):
        b = be_of({**x, **{q: x[q] * k for q in TAKEUP_KEYS}})
        if b <= TARGET_BE:
            found = (k, b)
            break
    takeup_k = found[0] if found else None
    rows.append({"Market assumption": "All take-up hazards (loan apply, card share, the 17 products' take-up), times",
                 "Agreed likely value": 1.0, "Value that gets the plan to break-even by m48": found[0] if found else "not within x2.5",
                 "Break-even month at that value": found[1] if found else "", "Search": "steps of 0.01 from 1.01"})
    found = None
    for r12 in np.round(np.arange(0.555, float(x["r3"]) - 0.004, 0.005), 3):
        b = be_of({**x, "r12": r12})
        if b <= TARGET_BE:
            found = (r12, b)
            break
    rows.append({"Market assumption": "Still saving at month 12 (r12)", "Agreed likely value": float(x["r12"]),
                 "Value that gets the plan to break-even by m48": found[0] if found else f"not below r3 ({float(x['r3']):.0%})",
                 "Break-even month at that value": found[1] if found else "", "Search": "steps of 0.5 points from 55.5%"})
    return rows, takeup_k


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    rows = search(x, dists)
    C.write("company_plan_search.csv", [public(r) for r in rows])
    rec, by48 = pick(rows)
    fr = []
    eligible = [r for r in rows if r["_plan"][3] == ELIGIBLE_PAY]
    for limit in (36, 48, 60):
        for label, pool in ((f"Breaks even by m{limit}, eligible pay (Rs 10,000 cap)", eligible), (f"Breaks even by m{limit}, all pay options", rows)):
            f = frontier(pool, limit)
            if not f:
                fr.append({"Set": label, "Rank by savers at m60": "", "Plan": f"no plan in the search breaks even by m{limit}"})
            fr += [{"Set": label, "Rank by savers at m60": j + 1, **public(r)} for j, r in enumerate(f)]
    fr.append({"Set": "RECOMMENDED" if by48 else "Closest eligible plan: no eligible plan breaks even by m48 (Rs 10,000 cap, UPI 30%)",
               "Rank by savers at m60": "", **public(rec)})
    cols = list(dict.fromkeys(k for r in fr for k in r))
    C.write("company_plan_frontier.csv", [{k: r.get(k, "") for k in cols} for r in fr])
    plan = rec["_plan"]
    print(f"  recommended (breaks even by m48: {by48}): plan {rec['Plan']} {describe(plan)} -> BE "
          f"{rec['EBITDA break-even month (first positive and staying positive)']}, savers m60 {rec['Savers at m60']:,.0f}")
    prefix = "company_plan_recommended"
    o, h, info = full_run(x, dists, plan, prefix)
    hm, mc_rows = plan_mc(x, dists, plan, prefix)
    label = f"Plan {rec['Plan']} at the agreed values"
    bc = breakeven_customers(o, label)
    if not by48:
        an, k = assumption_needed(x, dists, plan)
        C.write("company_plan_assumption_needed.csv", an)
        for r in an:
            print("  ", r)
        if k:
            ok, *_ = run_plan({**x, **{q: x[q] * k for q in TAKEUP_KEYS}}, dists, plan, [SEED])
            bc += breakeven_customers(ok, f"Plan {rec['Plan']} with every take-up x {k:.2f}")
    C.write("company_plan_breakeven_customers.csv", bc)
    C.write("company_plan_grid_edge.csv", grid_edge(x, dists))
    for r in mc_rows[:6]:
        print("  MC", r["Measure"], r["Value"], r["Note"][:70])
    return rows, rec


if __name__ == "__main__":
    main()

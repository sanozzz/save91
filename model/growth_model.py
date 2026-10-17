"""Part A of story/BRIEF_growth_and_100m_2026-10-17.md: the maximum-growth plan with year-5 PAT >= 0, funding sized by the model.

Operator: "cant we scale more faster and figure what we need to raise to be PAT Positive in 5th year with maximum growth. It might
mean different seed + series A raise."

Market inputs at the agreed likely values (each agent keeps his own sign-up draw); pay Rs 20,000 + 0.25% of balance capped at
Rs 10,000 a month (the agreed key; cap and salary rise 7% a year); every cost rule as built, central team AS BUILT (it scales with
the fleet), contingency, tax, 5.5% interest on cash, the 2-month commission lag.

Search: agents at m18 in {80, 100, 120, 150, 200} (the earlier ramp scaled to that size); then h agents a month, h in
{0, 5, 10, 15, 20, 30}; optionally a faster rate once EBITDA > 0: after 3 positive months in a row, max(2h, 10) a month.
Funding, sized per plan by company_model.size_funding (bisection on the month-by-month cash, interest included, so the
circularity "more cash, more interest, higher PAT" is solved on the real path):
  seed at m0  the smallest that keeps month-end cash >= Rs 5 crore until the Series A lands (its cost booked), rounded up to Rs 1 crore;
  Series A    at m18 (also sized at m15 and m21), the smallest that keeps cash >= Rs 5 crore through m60, rounded up to Rs 5 crore.
Constraint: year-5 PAT >= 0 (with the m18 funding). Objective: the most active savers at m60; tie-break year-5 revenue.

Writes tables/growth_search.csv, growth_frontier.csv, growth_recommended_* (the company base formats, a Series A timing table, a
Monte Carlo summary and checks). The company base tables are not touched.
"""
import contextlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_mc as CMC           # noqa: E402
import company_model as C          # noqa: E402

A18 = (80, 100, 120, 150, 200)
HIRES = (0, 5, 10, 15, 20, 30)
FASTER_MIN = 10
CENTRAL = "as built"
A_MONTHS = (15, 18, 21)
MAIN_A = 18
PREFIX = "growth_recommended"
CR = C.CRORE


def target_fn(a18, h, faster):
    xs, ys = zip(*C.GROWTH_POINTS[:7])
    h2 = max(2 * h, FASTER_MIN) if faster else h

    def tf(step=None):
        t = np.arange(C.M + 1)
        v = np.interp(np.minimum(t, 18), xs, np.asarray(ys, float) * a18 / 60.0)
        v = np.where(t > 18, a18 + h * (t - 18) + ((h2 - h) * np.maximum(0, t - step) if step else 0), v)
        return np.floor(v + 0.5).astype(int)
    return tf, h2


def plan_name(a18, h, faster):
    h2 = max(2 * h, FASTER_MIN)
    return f"{a18} agents by m18, then +{h} a month" + (f", +{h2} a month once EBITDA has been positive 3 months" if faster else "")


@contextlib.contextmanager
def funding(seed, a, a_month=MAIN_A):
    """Run the company model's statements with this plan's seed and Series A (restored afterwards)."""
    old = (C.SEED_ROUND, C.SERIES_A, C.SERIES_A_MONTH)
    C.SEED_ROUND, C.SERIES_A, C.SERIES_A_MONTH = float(seed), float(a), int(a_month)
    try:
        yield
    finally:
        C.SEED_ROUND, C.SERIES_A, C.SERIES_A_MONTH = old


def search(x, dists):
    plans, outs, infos = [], [], []
    for a18 in A18:
        for h in HIRES:
            for faster in (False, True):
                tf, _h2 = target_fn(a18, h, faster)
                o, fleets, targets, info = C.run_plan(x, dists, target_fn=tf, stepup=faster, central=CENTRAL)
                plans.append((a18, h, faster))
                outs.append(o)
                infos.append((info, targets[0]))
    st = C.stack_operating(outs)
    sized = {am: C.size_funding(st, [am]) for am in A_MONTHS}
    seed, rounds, feas = sized[MAIN_A]
    tr = C.treasury(st, seed_size=seed, rounds=rounds)
    yr = lambda arr, y: arr[:, 12 * (y - 1):12 * y].sum(axis=1)
    rows = []
    for i, (a18, h, faster) in enumerate(plans):
        o, (info, tgt) = outs[i], infos[i]
        be = C.stays_positive_from(o["ebitda"])[0]
        ebit5, pat5 = float(yr(tr["ebit_plan"], 5)[i]), float(yr(tr["pat"], 5)[i])
        rows.append({
            "Plan": i + 1, "Fleet path": plan_name(a18, h, faster), "Agents at m18": a18, "Hires a month after m18": h,
            "Faster hiring once EBITDA is positive": f"yes, {max(2 * h, FASTER_MIN)} a month" if faster else "no",
            "Faster hiring from month": int(info["step"][0]) + 1 if info["step"][0] else "",
            "Agents at m60": float(o["agents"][0, -1]), "Active savers at m60": float(o["still_saving"][0, -1]),
            "AUM at m60 (Rs)": float(o["fund_end"][0, -1]),
            **{f"Year-{y} revenue (Rs)": float(yr(o["revenue"], y)[0]) for y in (3, 4, 5)},
            **{f"Year-{y} EBITDA (Rs)": float(yr(o["ebitda"], y)[0]) for y in (3, 4, 5)},
            "Year-5 interest on cash (Rs)": float(yr(tr["interest"], 5)[i]), "Year-5 EBIT (Rs)": ebit5, "Year-5 PAT (Rs)": pat5,
            "Year-5 PAT at or above 0": "yes" if pat5 >= 0 else "no",
            "PAT positive only because of interest": "yes" if (pat5 >= 0 and ebit5 < 0) else ("no" if pat5 >= 0 else ""),
            "EBITDA break-even month": "not within 60" if np.isnan(be) else float(be),
            **{f"Seed at m0, Series A at m{am} (Rs)": float(sized[am][0][i]) for am in A_MONTHS},
            **{f"Series A at m{am} (Rs)": float(sized[am][1][0][1][i]) for am in A_MONTHS},
            "Total raised, Series A at m18 (Rs)": float(seed[i] + rounds[0][1][i]),
            "Lowest cash through m60, Series A at m18 (Rs)": float(tr["cash"][i].min()),
            "Cash at m60, Series A at m18 (Rs)": float(tr["cash"][i, -1]),
            "Funding feasible within the search ceiling": "yes" if feas[i] else "no",
            "_plan": (a18, h, faster), "_seed": float(seed[i]), "_a": float(rounds[0][1][i]),
        })
    return rows


def public(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def full(x, dists, rec, all_rows):
    a18, h, faster = rec["_plan"]
    tf, _ = target_fn(a18, h, faster)
    with funding(rec["_seed"], rec["_a"]):
        o, fleets, targets, info = C.run_plan(x, dists, target_fn=tf, stepup=faster, central=CENTRAL, keep=True)
        hd = C.headline(o)
        ck = C.checks(x, dists, o, hd, fleets[0], None, target=targets[0], opts=info["opts"])
        pat5 = float(o["pat"][0, 48:].sum())
        ck.append({"Check": "Funding sized by the model: year-5 PAT with this seed and Series A = the search row", "Largest gap":
                   abs(pat5 - rec["Year-5 PAT (Rs)"]), "Largest gap as share of the biggest value": abs(pat5 - rec["Year-5 PAT (Rs)"]) / abs(pat5),
                   "Tolerance (share)": 1e-9, "Passes": abs(pat5 - rec["Year-5 PAT (Rs)"]) <= 1e-9 * abs(pat5), "Note": ""})
        lo = float(o["cash"][0, MAIN_A - 1:].min())
        ck.append({"Check": "Funding sized by the model: cash from m18 to m60 stays at or above Rs 5 crore", "Largest gap": max(0.0, 5 * CR - lo),
                   "Largest gap as share of the biggest value": max(0.0, 5 * CR - lo) / (5 * CR), "Tolerance (share)": 0.0,
                   "Passes": lo >= 5 * CR, "Note": f"lowest Rs {lo:,.0f}"})
        lo_pre = float(o["cash_seed_only"][0, :MAIN_A - 1].min())
        ck.append({"Check": "Funding sized by the model: the seed keeps cash at or above Rs 5 crore until the Series A", "Largest gap":
                   max(0.0, 5 * CR - lo_pre), "Largest gap as share of the biggest value": max(0.0, 5 * CR - lo_pre) / (5 * CR),
                   "Tolerance (share)": 0.0, "Passes": lo_pre >= 5 * CR, "Note": f"lowest Rs {lo_pre:,.0f} (months 1-17)"})
        C.write(f"{PREFIX}_monthly.csv", C.monthly_rows(o))
        C.write(f"{PREFIX}_yearly.csv", C.yearly_rows(o))
        C.write(f"{PREFIX}_pnl_ladder_yearly.csv", C.ladder_rows(o))
        C.write(f"{PREFIX}_cashflow_yearly.csv", C.cashflow_rows(o))
        C.write(f"{PREFIX}_headcount.csv", C.headcount_rows(o))
        C.write(f"{PREFIX}_m18.csv", C.m18_rows(o, hd))
        C.write(f"{PREFIX}_checks.csv", ck)
        hm, _x, redraws = CMC.run_mc(plan={"target_fn": tf, "stepup": faster, "central": CENTRAL})
        rows = [r for r in CMC.summary(hm, CMC.DRAWS, redraws) if "lean hold" not in r["Measure"]]   # central is as built here
        extra = [CMC.share_row("P(year-5 PAT >= 0)", hm["pat_y5"] >= 0, CMC.DRAWS, f"seed Rs {rec['_seed'] / CR:.0f} crore, "
                               f"Series A Rs {rec['_a'] / CR:.0f} crore at m18, fixed in every draw"),
                 CMC.share_row("P(year-5 EBITDA >= 0)", hm["ebitda_y5"] >= 0, CMC.DRAWS),
                 CMC.share_row("P(cash >= 0 through m60)", hm["cash_positive_60"] > 0, CMC.DRAWS, "every month end 1-60")]
        rows = rows[:1] + [CMC.val_row("Plan", "", rec["Fleet path"] + f"; central as built; seed Rs {rec['_seed'] / CR:.0f} crore; "
                                       f"Series A Rs {rec['_a'] / CR:.0f} crore at m18")] + extra + rows[1:]
        C.write(f"{PREFIX}_mc_summary.csv", rows)
    timing = [{"Series A closes at": f"m{am}", "Seed at m0 (Rs)": rec[f"Seed at m0, Series A at m{am} (Rs)"],
               "Series A (Rs)": rec[f"Series A at m{am} (Rs)"],
               "Total raised (Rs)": rec[f"Seed at m0, Series A at m{am} (Rs)"] + rec[f"Series A at m{am} (Rs)"],
               "Rule": "seed: cash >= Rs 5 crore until the A lands, rounded up to Rs 1 crore; A: cash >= Rs 5 crore through m60, "
                       "rounded up to Rs 5 crore"} for am in A_MONTHS]
    C.write(f"{PREFIX}_series_a_timing.csv", timing)
    bad = [r["Check"] for r in ck if not r["Passes"]]
    print(f"  recommended: checks passed {len(ck) - len(bad)}/{len(ck)}" + (f"; FAIL {bad}" if bad else ""))
    assert not bad
    return o, hm, rows


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    rows = search(x, dists)
    C.write("growth_search.csv", [public(r) for r in rows])
    ok = sorted([r for r in rows if r["Year-5 PAT (Rs)"] >= 0], key=lambda r: (-r["Active savers at m60"], -r["Year-5 revenue (Rs)"]))
    okE = sorted([r for r in rows if r["Year-5 EBITDA (Rs)"] >= 0], key=lambda r: (-r["Active savers at m60"], -r["Year-5 revenue (Rs)"]))
    fr = [{"Set": "Year-5 PAT >= 0 (Series A at m18), most savers at m60 first", "Rank": j + 1, **public(r)} for j, r in enumerate(ok)]
    fr += ([{"Set": "Year-5 EBITDA >= 0, most savers at m60 first", "Rank": j + 1, **public(r)} for j, r in enumerate(okE)]
           or [{"Set": "Year-5 EBITDA >= 0", "Rank": "", "Plan": "no plan in the search has year-5 EBITDA >= 0"}])
    if not ok:
        fr.insert(0, {"Set": "Year-5 PAT >= 0", "Rank": "", "Plan": "no plan in the search has year-5 PAT >= 0"})
    rec = ok[0] if ok else max(rows, key=lambda r: r["Year-5 PAT (Rs)"])
    for r in fr:
        r["Recommended"] = "RECOMMENDED" if r.get("Plan") == rec["Plan"] and r["Set"].startswith("Year-5 PAT") else ""
    cols = list(dict.fromkeys(k for r in fr for k in r))
    C.write("growth_frontier.csv", [{k: r.get(k, "") for k in cols} for r in fr])
    print(f"  {len(rows)} plans; {len(ok)} with year-5 PAT >= 0; {len(okE)} with year-5 EBITDA >= 0; recommended plan {rec['Plan']}: "
          f"{rec['Fleet path']}, savers m60 {rec['Active savers at m60']:,.0f}, PAT y5 {rec['Year-5 PAT (Rs)'] / CR:.2f} cr, "
          f"EBITDA y5 {rec['Year-5 EBITDA (Rs)'] / CR:.2f} cr, seed {rec['_seed'] / CR:.0f} cr, A {rec['_a'] / CR:.0f} cr")
    full(x, dists, rec, rows)
    return rows, rec


if __name__ == "__main__":
    main()

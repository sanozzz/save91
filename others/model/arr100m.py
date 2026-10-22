"""Part B of story/BRIEF_growth_and_100m_2026-10-17.md: the path to $100M ARR (Rs 1,000 crore a year at Rs 100/$; Rs 850 crore at
Rs 85/$). ARR = 12 x the month's revenue. Operator: "What does it takes for us to reach $100mil revenue" / "how many users".

1. Steady state: one mature agent (cohort_engine, likely values, tenure 60): savers, revenue a saver a year, AUM a saver, money
   lent a saver a year; so the savers, agents and AUM that Rs 1,000 crore of revenue takes. Compared with the company model's
   own numbers at the month the recommended path reaches it (younger books, handovers).
2. The company model over 120 months (company_model.set_horizon(120); cohort_engine profiles of 120 ages). Beyond month 60 the
   take-up and approval growth are held at their year-5 values (year_cap 5; the 2x / 80% caps bind anyway), the fee multiplier is
   held at 1.5x, and the agent pay rate is 0.10% of balance (the agreed rule after company month 60), still capped at Rs 10,000
   rising 7% a year; every other rule as built (central team scaling, cities 1 per 50 agents after m18, contingency, tax,
   interest, the commission lag). Each agent keeps his own sign-up draw; market inputs at the likely values.
3. Fleet paths: the earlier ramp scaled to a18 by m18; then h1 agents a month; once EBITDA has been positive 3 months, h2 a month;
   capped at N agents (then replace leavers only). Search a18 in {100, 200}, h1 in {25, 50, 75, 100, 150, 200}, h2 in {h1, 2 h1},
   N in {5,000, 7,500, 10,000, 15,000}.
4. Funding per path (company_model.size_funding): seed at m0 (rounded up to Rs 1 crore) and rounds at m18, m36 and m60 (rounded
   up to Rs 5 crore), each the smallest keeping month-end cash >= Rs 5 crore until the next round lands (the last one to m120);
   each later round costs Rs 15 lakh (+ contingency), as the Series A (an approximation: large rounds cost more).
5. For each target year (7, 8, 10): among the paths reaching Rs 1,000 crore ARR by then, the one with the least total equity.

Writes tables/arr100m_steady_state.csv, arr100m_paths.csv, arr100m_recommended_yearly.csv and arr100m_checks.csv.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402

CR = C.CRORE
TARGET, ALT = 1000 * CR, 850 * CR
YEARS_TARGET = (7, 8, 10)
ROUND_MONTHS = (18, 36, 60)
A18 = (100, 200)
H1 = (25, 50, 75, 100, 150, 200)
CAPS = (5000, 7500, 10000, 15000)
CENTRAL = "as built"


def path_fn(a18, h1, h2, cap):
    xs, ys = zip(*C.GROWTH_POINTS[:7])

    def tf(step=None):
        t = np.arange(C.M + 1)
        v = np.interp(np.minimum(t, 18), xs, np.asarray(ys, float) * a18 / 60.0)
        v = np.where(t > 18, a18 + h1 * (t - 18) + ((h2 - h1) * np.maximum(0, t - step) if step else 0), v)
        return np.floor(np.minimum(v, cap) + 0.5).astype(int)
    return tf


def steady_state(x, rec_o=None, rec_month=None):
    r = E.run(x)["monthly"]
    s60 = float(r["still_saving"][0, 59])
    last = slice(48, 60)
    avg_s = float(r["still_saving"][0, last].mean())
    rev = float(r["income"][0, 59]) * 12 / s60
    aum_end, aum_avg = float(r["fund_end"][0, 59]) / s60, float(r["balance"][0, 59]) / s60
    lent = float(r["money_lent"][0, last].sum()) / avg_s
    house = (float(r["takeups_loan_home"][0, last].sum()) * float(x["loan_home_ticket"])
             + float(r["takeups_loan_lap"][0, last].sum()) * float(x["loan_lap_ticket"])) / avg_s
    rows = [{"Measure": "Savers in one mature agent's book (tenure 60)", "Value": s60, "Unit": "savers", "Source": "cohort_engine.run, likely values"},
            {"Measure": "Revenue a saver a year (month-60 run rate)", "Value": rev, "Unit": "Rs", "Source": "12 x income in month 60 / savers"},
            {"Measure": "AUM a saver, month end", "Value": aum_end, "Unit": "Rs", "Source": "fund at month end / savers"},
            {"Measure": "AUM a saver, average balance in the month", "Value": aum_avg, "Unit": "Rs", "Source": "the lead's ~Rs 61,000 is closer to this"},
            {"Measure": "Personal loans lent a saver a year (months 49-60)", "Value": lent, "Unit": "Rs", "Source": "first, repeat and top-ups"},
            {"Measure": "Home loans and LAP lent a saver a year (months 49-60)", "Value": house, "Unit": "Rs", "Source": "other lenders' books"}]
    for label, tgt in (("Rs 1,000 crore ($100M at Rs 100)", TARGET), ("Rs 850 crore ($100M at Rs 85)", ALT)):
        sv = tgt / rev
        rows += [{"Measure": f"{label}: active savers needed", "Value": sv, "Unit": "savers", "Source": "target / revenue a saver"},
                 {"Measure": f"{label}: mature agents needed", "Value": sv / s60, "Unit": "agents", "Source": "savers / savers an agent"},
                 {"Measure": f"{label}: AUM (month end)", "Value": sv * aum_end, "Unit": "Rs", "Source": "savers x AUM a saver"},
                 {"Measure": f"{label}: personal loans lent a year", "Value": sv * lent, "Unit": "Rs", "Source": ""},
                 {"Measure": f"{label}: home loans and LAP lent a year", "Value": sv * house, "Unit": "Rs", "Source": ""}]
    if rec_o is not None and rec_month:
        i = rec_month - 1
        sv, ag = float(rec_o["still_saving"][0, i]), float(rec_o["agents"][0, i])
        rows += [{"Measure": f"Company model, recommended path, month {rec_month} (ARR first reaches Rs 1,000 crore): active savers", "Value": sv,
                  "Unit": "savers", "Source": "arr100m_recommended_yearly.csv"},
                 {"Measure": "  agents then", "Value": ag, "Unit": "agents", "Source": ""},
                 {"Measure": "  savers an agent then", "Value": sv / ag, "Unit": "savers", "Source": "younger books, handovers"},
                 {"Measure": "  revenue a saver a year then", "Value": 12 * float(rec_o["revenue"][0, i]) / sv, "Unit": "Rs", "Source": ""},
                 {"Measure": "  AUM then", "Value": float(rec_o["fund_end"][0, i]), "Unit": "Rs", "Source": ""}]
    return rows


def first_month(cond):
    return int(cond.argmax() + 1) if cond.any() else 0


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    o60, *_ = C.run_plan(x, dists, central=C.BASE_CENTRAL)          # the 60-month base, for the horizon check
    C.set_horizon(120)
    o120b, *_ = C.run_plan(x, dists, central=C.BASE_CENTRAL)
    paths, outs = [], []
    for a18 in A18:
        for h1 in H1:
            for h2 in sorted({h1, 2 * h1}):
                for cap in CAPS:
                    o, fleets, targets, info = C.run_plan(x, dists, target_fn=path_fn(a18, h1, h2, cap), stepup=h2 != h1, central=CENTRAL)
                    paths.append((a18, h1, h2, cap, int(info["step"][0]) + 1 if info["step"][0] else 0))
                    outs.append(o)
    st = C.stack_operating(outs)
    seed, rounds, feas = C.size_funding(st, ROUND_MONTHS)
    tr = C.treasury(st, seed_size=seed, rounds=rounds)
    rows = []
    for i, (a18, h1, h2, cap, stepm) in enumerate(paths):
        o = outs[i]
        arr = 12 * o["revenue"][0]
        m1000, m850 = first_month(arr >= TARGET), first_month(arr >= ALT)
        burn = -(tr["cf_operating"][i] + o["cf_investing"][0])
        be = C.stays_positive_from(o["ebitda"])[0]
        total = float(seed[i] + sum(r[1][i] for r in rounds))
        rows.append({"Path": i + 1, "Agents at m18": a18, "Hires a month after m18": h1, "Hires a month once EBITDA is positive": h2,
                     "Faster hiring from month": stepm or "", "Agent cap": cap,
                     "Month ARR first reaches Rs 1,000 crore": m1000 or "not within 120", "Year": (m1000 - 1) // 12 + 1 if m1000 else "",
                     "Month ARR first reaches Rs 850 crore": m850 or "not within 120",
                     "EBITDA break-even month (stays positive)": "not within 120" if np.isnan(be) else float(be),
                     "First month EBITDA positive": first_month(o["ebitda"][0] > 0) or "not within 120",
                     "Seed at m0 (Rs)": float(seed[i]), **{f"Round at m{m} (Rs)": float(r[1][i]) for m, r in zip(ROUND_MONTHS, rounds)},
                     "Total equity raised (Rs)": total, "Peak monthly burn (Rs)": float(burn.max()), "Month of peak burn": int(burn.argmax() + 1),
                     "Lowest cash (Rs)": float(tr["cash"][i].min()), "Cash at m120 (Rs)": float(tr["cash"][i, -1]),
                     "ARR at m120 (Rs)": float(arr[-1]), "Agents at m120": float(o["agents"][0, -1]),
                     "Active savers at m120": float(o["still_saving"][0, -1]), "Funding feasible within the search ceiling": "yes" if feas[i] else "no",
                     "_i": i})
    picks = {}
    for y in YEARS_TARGET:
        ok = [r for r in rows if isinstance(r["Month ARR first reaches Rs 1,000 crore"], int) and r["Month ARR first reaches Rs 1,000 crore"] <= 12 * y]
        picks[y] = min(ok, key=lambda r: (r["Total equity raised (Rs)"], r["Month ARR first reaches Rs 1,000 crore"])) if ok else None
    fastest = min((r["Month ARR first reaches Rs 1,000 crore"] for r in rows if isinstance(r["Month ARR first reaches Rs 1,000 crore"], int)), default=None)
    for r in rows:
        r["Least equity for year"] = ", ".join(str(y) for y in YEARS_TARGET if picks[y] is not None and picks[y]["Path"] == r["Path"])
    rec_year = 8 if picks.get(8) else next(y for y in YEARS_TARGET if picks[y])
    rec = picks[rec_year]
    for r in rows:
        r["Recommended"] = "RECOMMENDED" if r["Path"] == rec["Path"] else ""
    C.write("arr100m_paths.csv", [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])
    # the recommended path, years 1-10
    i = rec["_i"]
    o = outs[i]
    yr = lambda arr, y: float(arr[12 * (y - 1):12 * y].sum())
    end = lambda arr, y: float(arr[12 * y - 1])
    fin = tr["cf_financing"][i]
    burn = -(tr["cf_operating"][i] + o["cf_investing"][0])
    yearly = []
    for y in range(1, 11):
        yearly.append({"Year": y, "Revenue (Rs)": yr(o["revenue"][0], y), "ARR at year end (Rs)": 12 * end(o["revenue"][0], y),
                       "CM1 (Rs)": yr(o["cm1"][0], y), "CM2 (Rs)": yr(o["cm2"][0], y), "CM3 (Rs)": yr(o["cm3"][0], y),
                       "EBITDA (Rs)": yr(tr["ebit_plan"][i] + o["depreciation"][0], y), "Interest on cash (Rs)": yr(tr["interest"][i], y),
                       "PAT (Rs)": yr(tr["pat"][i], y), "Equity raised in the year (Rs)": yr(fin, y), "Cash at year end (Rs)": end(tr["cash"][i], y),
                       "Peak monthly burn in the year (Rs)": float(burn[12 * (y - 1):12 * y].max()),
                       "Agents at year end": end(o["agents"][0], y), "Active savers at year end": end(o["still_saving"][0], y),
                       "AUM at year end (Rs)": end(o["fund_end"][0], y), "Personal loans lent in the year (Rs)": yr(o["money_lent"][0], y),
                       "Home loans and LAP lent in the year (Rs)": yr(o["housing_lent"][0], y), "Cities at year end": end(o["cities"][0], y),
                       "Central team at year end": end(o["hc_central"][0], y),
                       "Headcount at year end, all": end(o["agents"][0] + o["hc_central"][0] + o["city_managers"][0] + o["team_leads"][0], y)})
    C.write("arr100m_recommended_yearly.csv", yearly)
    C.write("arr100m_steady_state.csv", steady_state(x, o, rec["Month ARR first reaches Rs 1,000 crore"]))
    # per target year summary (into the paths file's companion rows)
    summ = []
    for y in YEARS_TARGET:
        p = picks[y]
        if p is None:
            summ.append({"Target": f"Rs 1,000 crore ARR by year {y}", "Path": "no path in the search"})
            continue
        j, oo = p["_i"], outs[p["_i"]]
        mm = p["Month ARR first reaches Rs 1,000 crore"]
        k = mm - 1
        yy = (mm - 1) // 12 + 1
        summ.append({"Target": f"Rs 1,000 crore ARR by year {y}", "Path": p["Path"],
                     "Fleet": f"{p['Agents at m18']} by m18, +{p['Hires a month after m18']} a month, +{p['Hires a month once EBITDA is positive']} once EBITDA "
                              f"is positive, cap {p['Agent cap']:,}",
                     "Month reached": mm, "Agents then": float(oo["agents"][0, k]), "Active savers then": float(oo["still_saving"][0, k]),
                     "AUM then (Rs)": float(oo["fund_end"][0, k]),
                     "Personal loans lent in that year (Rs)": yr(oo["money_lent"][0], yy), "Home loans and LAP lent in that year (Rs)": yr(oo["housing_lent"][0], yy),
                     "Cities then": float(oo["cities"][0, k]), "Central team then": float(oo["hc_central"][0, k]),
                     "Total equity (Rs)": p["Total equity raised (Rs)"],
                     "Raised when": "; ".join([f"m0 Rs {p['Seed at m0 (Rs)'] / CR:,.0f} crore"] + [f"m{m} Rs {p[f'Round at m{m} (Rs)'] / CR:,.0f} crore"
                                                                                                     for m in ROUND_MONTHS if p[f"Round at m{m} (Rs)"] > 0]),
                     "Peak monthly burn (Rs)": p["Peak monthly burn (Rs)"], "EBITDA turns positive (stays)": p["EBITDA break-even month (stays positive)"],
                     **{f"Revenue year {q} (Rs)": yr(oo["revenue"][0], q) for q in range(1, 11)},
                     **{f"EBITDA year {q} (Rs)": yr(tr["ebit_plan"][j] + oo["depreciation"][0], q) for q in range(1, 11)},
                     **{f"PAT year {q} (Rs)": yr(tr["pat"][j], q) for q in range(1, 11)}})
    C.write("arr100m_targets.csv", summ)
    # checks
    ck = []

    def add(name, ok, note=""):
        ck.append({"Check": name, "Passes": bool(ok), "Note": note})
    for k in ("revenue", "ebitda", "still_saving", "cash", "pat"):
        g = float(np.max(np.abs(o60[k][0] - o120b[k][0, :60])))
        add(f"120-month horizon: months 1-60 of the base = the 60-month base ({k})", g <= 1e-9 * float(np.max(np.abs(o60[k][0]))), f"largest gap {g:.3g}")
    add("Beyond month 60 the fee multiplier is held at 1.5x", np.allclose(o120b["fee_multiplier"][0, 59:], 1.5))
    lo = tr["cash"][:, 0:].min(axis=1)
    add("Every path's sized funding keeps month-end cash >= Rs 5 crore through m120", bool((lo >= 5 * CR - 1).all()), f"lowest Rs {lo.min():,.0f}")
    add("Funding search feasible for every path (ceiling Rs 5,000 crore a round)", bool(feas.all()))
    j = rec["_i"]
    add("Recommended path: the treasury's cash = cumulative PAT + depreciation - capex + equity - receivable",
        np.allclose(tr["cash"][j], np.cumsum(tr["pat"][j] + o["depreciation"][0] + o["cf_investing"][0] + tr["cf_financing"][j]) - o["receivable"][0], rtol=1e-9, atol=1.0))
    add("Recommended path reaches Rs 1,000 crore ARR", isinstance(rec["Month ARR first reaches Rs 1,000 crore"], int), f"month {rec['Month ARR first reaches Rs 1,000 crore']}")
    C.write("arr100m_checks.csv", ck)
    print(f"  {len(rows)} paths; fastest month to Rs 1,000 crore ARR: {fastest}; checks {sum(c['Passes'] for c in ck)}/{len(ck)}")
    for s_ in summ:
        print("  ", s_.get("Target"), "| path", s_.get("Path"), "|", s_.get("Fleet", ""), "| month", s_.get("Month reached"), "| equity cr",
              round(s_.get("Total equity (Rs)", 0) / CR), "|", s_.get("Raised when", ""))
    assert all(c["Passes"] for c in ck)
    return rows


if __name__ == "__main__":
    main()

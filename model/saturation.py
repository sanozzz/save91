"""Cities have limits: the city layer in the company model (story/BRIEF_city_saturation_2026-10-17.md, operator 17 Oct 2026).

Operator: "So we now need to marry the model with the real world. We can't outgrow a city. I believe we have some 30cr people
that we have in this segment" / "this need to marry our model and has to be an input to the cities we grow over time. We need
to plan for this too". Taps: TAM = urban self-employed; city cap = 20%; city data = estimate (rank-size).

THE POOL. Urban self-employed (own-account workers, employers, helpers): pert 6.5 / 7.0 / 7.7 crore, likely 7.0 crore (NG-002:
40.4% of urban workers are self-employed, 34.0% own-account or employer; urban workers about 19 crore = urban population about 52
crore x work participation about 37%, the lead's estimate). The operator's 30 crore is context only (SEG-02: e-Shram 31.9 crore
unorganised workers; NG-003: 34.6 crore self-employed including rural).
CITIES (ESTIMATE, NOT CENSUS). About 4,000 urban centres on a rank-size curve, share(r) proportional to r^-q, rank 1 = NCR at 6.3%
of urban India (about 3.3 crore of about 52 crore), q fitted so the 4,000 shares add to 1. A fleet serves only the top 500
("Class I", population >= 1 lakh). Names for the top 15 in the brief's order; then "City 16", ... Sizes come from the curve.
THE CITY LAYER (company_model.saturate; default off, so every other table is unchanged):
  cap        each city's cumulative sign-ups <= 20% of its addressable pool;
  slowdown   an agent's sign-ups x max(0, 1 - penetration / 20%) (straight line to zero at the cap, judgement); the softer
             1 - (penetration / 20%)^2 is a sensitivity;
  AUTO       cities open in rank order; each new book goes to the open city with the most remaining headroom per agent; the
             next city opens when even the best is below 5,000 sign-ups a head (an agent's 5-year sign-ups); replacements stay;
  PLANNED    tables/city_plan.csv (editable: launch month; agents in the launch month and at +3, +6, +12, +24, +36 months, then
             yearly to +84,
             straight lines between, flat after) replaces the fleet path; attrition and replacements happen inside each city;
             the same slowdown;
  costs      launch Rs 3 lakh, an office and a city manager per open city, as before.
RUNS: 1 the current unicorn plan with saturation on, nothing else changed (its fleet path and its funding); 2 the re-plan under
saturation (fleet path, the city-opening threshold; rounds re-priced with unicorn_plan's rules); 3 NCR alone; 4 the profitable
plans of growth_model (200 agents) with saturation. The AUTO rollout of the re-plan is written to tables/city_plan.csv, then
re-run in PLANNED mode from that file (it must reproduce AUTO within 1%).

Writes tables/cities.csv, city_plan.csv, city_plan_warnings.csv and sat_*.csv.
"""
import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import growth_model as G           # noqa: E402
import unicorn_plan as U           # noqa: E402

CR, LAKH = C.CRORE, C.LAKH
POOL = 7.0 * CR
POOL_RANGE = (6.5 * CR, 7.0 * CR, 7.7 * CR)
N_TOWNS, CLASS_I, NCR_SHARE = 4000, 500, 0.063
NAMES = ("NCR", "Mumbai MMR", "Kolkata", "Bengaluru", "Chennai", "Hyderabad", "Ahmedabad", "Pune", "Surat", "Jaipur", "Lucknow",
         "Kanpur", "Nagpur", "Indore", "Patna")
CAP, OPEN_HEADROOM = C.SAT_CAP, C.SAT_OPEN_HEADROOM
PEN_FLAG = 0.10                    # informational: a city opened before the previous rank is 10% penetrated (half its cap)
OFFSETS = (0, 3, 6, 12, 24, 36, 48, 60, 72, 84)   # the brief's +6/+12/+24/+36, plus the launch month and +3 (a new city takes a
                                                  # lump of agents at once) and yearly points to the horizon (AUTO cities keep
                                                  # growing past +36 while they have headroom); without them the replay misses


def col(o_):
    return "Agents in the launch month" if o_ == 0 else f"Agents at launch +{o_} months"
HORIZON = 96
UNICORN_PLAN = (300, 200, 7500)    # the current unicorn plan (unicorn_rounds.csv)
REPLAN_GRID = ((100, 200, 300), (50, 100, 150, 200, 300), (3000, 5000, 7500, 10000, 15000), (5000.0, 10000.0, 25000.0))
PROFITABLE = ((200, 0, False, "Plan 49: 200 agents by m18, then replace leavers (EBITDA-positive in year 5)"),
              (200, 0, True, "Plan 50: 200 agents by m18, +10 a month once EBITDA is positive (the max-growth plan)"))
REPRO_TOL = 0.01


# ---------------------------------------------------------------- cities
def city_curve():
    r = np.arange(1, N_TOWNS + 1)
    q = brentq(lambda qq: (r ** -qq).sum() * NCR_SHARE - 1.0, 0.2, 2.0)
    share = NCR_SHARE * r ** -q
    return q, share


def cities_table(q, share):
    rows = []
    for i, s_ in enumerate(share):
        rows.append({"Rank": i + 1, "City": NAMES[i] if i < len(NAMES) else f"City {i + 1}", "Share of the national pool": s_,
                     "Addressable (urban self-employed)": s_ * POOL, "Cap: 20% of addressable (sign-ups)": CAP * s_ * POOL,
                     "Served (Class I, top 500)": "yes" if i < CLASS_I else "no",
                     "Basis": f"estimate, not census: rank-size curve, q = {q:.4f}, NCR = 6.3% of urban India; pool 7.0 crore"})
    return rows


def sat_cfg(addr, X=OPEN_HEADROOM, shape="linear", launch=None):
    c = {"addressable": addr, "cap": CAP, "open_headroom": X, "shape": shape}
    if launch is not None:
        c["launch"] = launch
    return c


# ---------------------------------------------------------------- runs
def run(x, dists, sat, target_fn=None, target=None, fleet=None, central="as built", stepup=False, keep=False):
    """One deterministic run with the city layer. fleet: a PLANNED-mode fleet (bypasses run_plan's fleet builder)."""
    opts = {"saturation": sat}
    if fleet is None:
        o, fleets, targets, info = C.run_plan(x, dists, target_fn=target_fn, target=target, central=central, stepup=stepup,
                                              opts=opts, keep=keep)
        return o, fleets[0]
    o = C.simulate(x, [fleet], keep, {**opts, "central_hold_until": None})
    return o, fleet


def funded(o, seed_amt, rds):
    return U.apply_funding(o, seed_amt, rds)


def lens(o, m):
    rl, al, arr, aum = U.lens_values(o, m)
    return rl, al, arr, aum


def first_unicorn_month(o):
    arr = 12 * o["revenue"][0]
    aum = o["fund_end"][0]
    ok = (U.ARR_MULT * arr >= U.UNICORN) & (U.AUM_MULT * aum >= U.UNICORN)
    return int(ok.argmax() + 1) if ok.any() else 0


def plan_and_price(o, unicorn_month=None):
    """unicorn_plan's rounds on this path; the unicorn window moves to the 7 months ending at the unicorn month if later than m60."""
    keep = U.UNICORN_WINDOW
    if unicorn_month and unicorn_month > keep[1]:
        U.UNICORN_WINDOW = (unicorn_month - 6, unicorn_month)
    try:
        seed, rounds = U.plan_rounds(o)
    finally:
        U.UNICORN_WINDOW = keep
    rds = [(r["Month"], r["Amount"]) for r in rounds]
    return seed, rounds, rds, U.cap_table(seed, rounds), funded(o, seed["Amount"], rds)


def yearly(run_name, of, sat, extra=None):
    """Long format: one row per measure, Year 1..Y, and the m60 lens values."""
    co = of["_city"][0]
    Y = C.M // 12
    e = lambda arr: [float(arr[12 * y + 11]) for y in range(Y)]
    s = lambda arr: [float(arr[12 * y:12 * y + 12].sum()) for y in range(Y)]
    cum = co["cum"].sum(axis=0)
    class1 = float(sat["addressable"][:CLASS_I].sum())
    rl, al, arr, aum = lens(of, 60)
    rows = []

    def add(m, u, vals, at60="", note=""):
        rows.append({"Run": run_name, "Measure": m, "Unit": u, **{f"Year {y + 1}": vals[y] for y in range(Y)}, "At m60": at60, "Note": note})
    add("Sign-ups in the year", "sign-ups", s(of["signups"][0]))
    add("Cumulative sign-ups at year end", "sign-ups", e(cum), float(cum[59]))
    add("Active savers at year end", "savers", e(of["still_saving"][0]), float(of["still_saving"][0, 59]))
    add("AUM at year end", "Rs", e(of["fund_end"][0]), aum)
    add("ARR at year end (12 x the month's revenue)", "Rs", [12 * v for v in e(of["revenue"][0])], arr)
    add("Revenue in the year", "Rs", s(of["revenue"][0]))
    add("EBITDA in the year", "Rs", s(of["ebitda"][0]))
    add("PAT in the year", "Rs", s(of["pat"][0]))
    add("Equity raised in the year", "Rs", s(of["cf_financing"][0]))
    add("Cash at year end", "Rs", e(of["cash"][0]), float(of["cash"][0, 59]), f"lowest Rs {float(of['cash'][0].min()):,.0f} (month {int(of['cash'][0].argmin()) + 1})")
    add("Agents at year end", "agents", e(of["agents"][0]))
    add("Cities open at year end", "cities", e(co["open"]), float(co["open"][59]))
    add("National penetration (cumulative sign-ups / 7.0 crore)", "share", [v / POOL for v in e(cum)], float(cum[59]) / POOL)
    add("Class I penetration (cumulative sign-ups / the top-500 pool)", "share", [v / class1 for v in e(cum)], float(cum[59]) / class1)
    add("NCR penetration", "share", [v / float(sat["addressable"][0]) for v in e(co["cum"][0])], float(co["cum"][0, 59]) / float(sat["addressable"][0]))
    add("m60 lens check: revenue lens (20 x ARR; our judgement)", "Rs", [""] * Y, rl, f"margin over $1B {rl / U.UNICORN - 1:+.1%}; {'clears' if rl >= U.UNICORN else 'FAILS'}")
    add("m60 lens check: AUM lens (0.45 x AUM; our judgement)", "Rs", [""] * Y, al, f"margin over $1B {al / U.UNICORN - 1:+.1%}; {'clears' if al >= U.UNICORN else 'FAILS'}")
    for k, v in (extra or {}).items():
        add(k, "", [""] * Y, v)
    return rows


def ncr_rows(run_name, of, sat):
    co = of["_city"][0]
    Y = C.M // 12
    A0 = float(sat["addressable"][0])
    pen = co["cum"][0] / A0
    hit95 = int((pen >= 0.95 * CAP).argmax() + 1) if (pen >= 0.95 * CAP).any() else "not within the horizon"
    hit99 = int((pen >= 0.99 * CAP).argmax() + 1) if (pen >= 0.99 * CAP).any() else "not within the horizon"
    rows = []
    for y in range(Y):
        i = 12 * y + 11
        rows.append({"Run": run_name, "Year": y + 1, "Agents in NCR at year end": float(co["agents"][0, i]),
                     "Sign-ups in the year": float(co["signups"][0, 12 * y:12 * y + 12].sum()), "Cumulative sign-ups": float(co["cum"][0, i]),
                     "Active savers at year end": float(co["savers"][0, i]), "AUM at year end (Rs)": float(co["aum"][0, i]),
                     "Penetration (cumulative sign-ups / addressable)": float(pen[i]), "Cap (penetration)": CAP,
                     "Addressable (people)": A0, "Month NCR reaches 95% of its cap": hit95, "Month NCR reaches 99% of its cap": hit99})
    return rows


def penetration_rows(run_name, of, sat, top=30):
    co = of["_city"][0]
    Y = C.M // 12
    rows = []
    for c in range(top):
        rows.append({"Run": run_name, "Rank": c + 1, "City": NAMES[c] if c < len(NAMES) else f"City {c + 1}",
                     "Addressable": float(sat["addressable"][c]),
                     **{f"Penetration, year {y + 1}": float(co["cum"][c, 12 * y + 11] / sat["addressable"][c]) for y in range(Y)},
                     **{f"Agents, year {y + 1}": float(co["agents"][c, 12 * y + 11]) for y in range(Y)}})
    return rows


def city_yearly(run_name, of, sat):
    co = of["_city"][0]
    Y = C.M // 12
    rows = []
    opened = np.nonzero(co["agents"].max(axis=1) > 0)[0]
    for c in opened:
        for y in range(Y):
            i, sl = 12 * y + 11, slice(12 * y, 12 * y + 12)
            rows.append({"Run": run_name, "Rank": int(c) + 1, "City": NAMES[c] if c < len(NAMES) else f"City {c + 1}", "Year": y + 1,
                         "Agents at year end": float(co["agents"][c, i]), "Sign-ups in the year": float(co["signups"][c, sl].sum()),
                         "Active savers at year end": float(co["savers"][c, i]), "AUM at year end (Rs)": float(co["aum"][c, i]),
                         "Revenue in the year (Rs)": float(co["revenue"][c, sl].sum()),
                         "Penetration at year end": float(co["cum"][c, i] / sat["addressable"][c]),
                         "City contribution, CM2 in the year (Rs)": float(co["cm2"][c, sl].sum())})
    return rows


# ---------------------------------------------------------------- the city plan (PLANNED mode)
def plan_from_auto(of, sat, note):
    co = of["_city"][0]
    rows = []
    M = C.M
    for c in np.nonzero(co["agents"].max(axis=1) > 0)[0]:
        L = int(np.argmax(co["agents"][c] > 0) + 1)
        pts = {o_: float(co["agents"][c, min(M, L + o_) - 1]) for o_ in OFFSETS}
        rows.append({"City": NAMES[c] if c < len(NAMES) else f"City {c + 1}", "Rank": int(c) + 1,
                     "Addressable (urban self-employed)": float(sat["addressable"][c]),
                     "Cap: 20% of addressable (sign-ups)": float(CAP * sat["addressable"][c]),
                     "Launch month": L, **{col(o_): round(pts[o_]) for o_ in OFFSETS},
                     "Month it nears its cap (95%; AUTO run, information only)": (
                         int(np.argmax(co["cum"][c] >= 0.95 * co.get("cap_by_month", co["cap"][:, None])[c]) + 1)
                         if (co["cum"][c] >= 0.95 * co.get("cap_by_month", co["cap"][:, None])[c]).any() else f"not by m{C.M}"),
                     "Notes": note})
    return rows


def read_plan(path):
    return list(csv.DictReader(Path(path).open()))


def plan_targets(plan, n_cities):
    """Agents by month for each city, (C, M + 1): 0 before launch, straight lines through launch +6/+12/+24/+36, flat after."""
    M = C.M
    tg = np.zeros((n_cities, M + 1))
    launch = np.full(n_cities, np.inf)
    t = np.arange(M + 1)
    for r in plan:
        c = int(r["Rank"]) - 1
        L = int(float(r["Launch month"]))
        xs = [L - 1] + [L + o_ for o_ in OFFSETS]
        ys = [0.0] + [float(r[col(o_)]) for o_ in OFFSETS]
        tg[c] = np.floor(np.interp(t, xs, ys) + 0.5)
        launch[c] = L
    return tg, launch


def plan_warnings(plan, of, sat, per_agent_5y):
    co = of["_city"][0]
    out = []
    byrank = {int(r["Rank"]): r for r in plan}
    for r in plan:
        c = int(r["Rank"]) - 1
        L = int(float(r["Launch month"]))
        peak = max(float(r[col(o_)]) for o_ in OFFSETS)
        cap = CAP * float(sat["addressable"][c])
        signed_before = float(co["cum"][c, L - 2]) if L >= 2 else 0.0
        need = peak * per_agent_5y
        if need > cap - signed_before:
            out.append({"City": r["City"], "Rank": c + 1, "Kind": "would outgrow its headroom",
                        "Detail": f"{peak:,.0f} agents x {per_agent_5y:,.0f} expected 5-year sign-ups each = {need:,.0f} > remaining cap "
                                  f"{cap - signed_before:,.0f}; the slowdown will hold them back", "Severity": "warning"})
        prev = byrank.get(c)                                   # the previous rank (rank c, i.e. index c - 1)
        if c > 0 and prev is not None:
            pen_prev = float(co["cum"][c - 1, L - 1] / sat["addressable"][c - 1]) if L >= 1 else 0.0
            if pen_prev < PEN_FLAG:
                out.append({"City": r["City"], "Rank": c + 1, "Kind": "opened before the previous rank is 10% penetrated",
                            "Detail": f"{prev['City']} is {pen_prev:.1%} penetrated in month {L}", "Severity": "information"})
    return out or [{"City": "", "Rank": "", "Kind": "none", "Detail": "no warnings", "Severity": ""}]


# ---------------------------------------------------------------- main
def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, share = city_curve()
    C.write("cities.csv", cities_table(q, share))
    addr = share[:CLASS_I] * POOL
    per_agent_5y = float(E.run(x)["out"]["signups60"][0])
    C.set_horizon(HORIZON)
    checks = []

    def chk(name, ok, note=""):
        checks.append({"Check": name, "Passes": bool(ok), "Note": note})
    chk("City curve: the 4,000 shares add to 1 and NCR is 6.3%", abs(share.sum() - 1) < 1e-9 and abs(share[0] - NCR_SHARE) < 1e-12,
        f"q = {q:.4f}; top 50 {share[:50].sum():.1%}, top 150 {share[:150].sum():.1%}, top 500 {share[:500].sum():.1%}")

    # run 1: the current unicorn plan with saturation, its funding fixed
    rnd = list(csv.DictReader((C.T / "unicorn_rounds.csv").open()))
    seed_amt = float(rnd[0]["Amount (Rs)"])
    rds_fixed = [(int(r["Month"]), float(r["Amount (Rs)"])) for r in rnd[1:]]
    a18, h, cap = UNICORN_PLAN
    tf = U.path_fn(a18, h, cap)
    o_un, _ = run(x, dists, None, target_fn=tf)
    o_inf, _ = run(x, dists, sat_cfg(np.full(CLASS_I, np.inf)), target_fn=tf)
    chk("City layer with an unlimited pool: sign-ups = the model without it, every month", np.allclose(o_inf["signups"], o_un["signups"], rtol=1e-12, atol=1e-9))
    rows_asis = []
    o1 = None
    for shape in ("linear", "square"):
        sat = sat_cfg(addr, shape=shape)
        o, fl = run(x, dists, sat, target_fn=tf)
        of = funded(o, seed_amt, rds_fixed)
        nm = f"1. Current unicorn plan with saturation ({'straight-line slowdown' if shape == 'linear' else 'softer slowdown, sensitivity'})"
        rows_asis += yearly(nm, of, sat)
        if shape == "linear":
            o1, sat1, fl1 = of, sat, fl
    rows_asis = yearly("0. Current unicorn plan without saturation (unicorn_yearly.csv)", funded(
        {**o_un, "_city": [{"cum": np.zeros((CLASS_I, C.M)), "open": o_un["cities"][0], "signups": np.zeros((CLASS_I, C.M))}]},
        seed_amt, rds_fixed), sat_cfg(addr))[:12] + rows_asis
    C.write("sat_unicorn_asis_yearly.csv", rows_asis)
    co1 = o1["_city"][0]
    chk("Run 1: no city's cumulative sign-ups exceed its cap", bool((co1["cum"][:, -1] <= co1["cap"] * (1 + 1e-12) + 1e-6).all()),
        f"most-penetrated city at {float((co1['cum'][:, -1] / sat1['addressable']).max()):.2%}")
    chk("Run 1: every book is in a city and city agents add to the company's agents, every month",
        bool((co1["book_city"] >= 0).all()) and np.allclose(co1["agents"].sum(axis=0), o1["agents"][0]))
    chk("Run 1: city sign-ups add to the company's sign-ups, every month", np.allclose(co1["signups"].sum(axis=0), o1["signups"][0], rtol=1e-12, atol=1e-6))
    chk("Run 1: city savers, AUM and revenue add to the company's", all(np.allclose(co1[a].sum(axis=0), o1[b][0], rtol=1e-9, atol=1e-3)
                                                                       for a, b in (("savers", "still_saving"), ("aum", "fund_end"), ("revenue", "revenue"))))
    chk("Run 1: city CM2 adds to the company's CM2, every month", np.allclose(co1["cm2"].sum(axis=0), o1["cm2"][0], rtol=1e-9, atol=1e-2))

    # run 2: the re-plan under saturation (AUTO)
    res = []
    for a18_ in REPLAN_GRID[0]:
        for h_ in REPLAN_GRID[1]:
            for cap_ in REPLAN_GRID[2]:
                for X in REPLAN_GRID[3]:
                    sat = sat_cfg(addr, X=X)
                    o, _ = run(x, dists, sat, target_fn=U.path_fn(a18_, h_, cap_))
                    um = first_unicorn_month(o)
                    seed, rounds, rds, ct, of = plan_and_price(o, um)
                    rl, al, arr, aum = lens(of, 60)
                    rl96, al96, arr96, aum96 = lens(of, C.M)
                    arr_m, aum_m = 12 * o["revenue"][0], o["fund_end"][0]
                    fr = int((U.ARR_MULT * arr_m >= U.UNICORN).argmax() + 1) if (U.ARR_MULT * arr_m >= U.UNICORN).any() else "not within 96"
                    fa = int((U.AUM_MULT * aum_m >= U.UNICORN).argmax() + 1) if (U.AUM_MULT * aum_m >= U.UNICORN).any() else "not within 96"
                    eq60 = seed["Amount"] + sum(r["Amount"] for r in rounds if r["Month"] <= 60)
                    eq_um = seed["Amount"] + sum(r["Amount"] for r in rounds if um and r["Month"] <= um) if um else ""
                    res.append({"Agents at m18": a18_, "Hires a month after m18": h_, "Agent cap": cap_, "Open a city below this headroom a head": X,
                                "ARR at m60 (Rs)": arr, "AUM at m60 (Rs)": aum, "Revenue lens at m60 (Rs)": rl, "AUM lens at m60 (Rs)": al,
                                "Both lenses >= $1B at m60": "yes" if min(rl, al) >= U.UNICORN else "no",
                                "AUM lens >= $1B at m60": "yes" if al >= U.UNICORN else "no",
                                "First month both lenses >= $1B": um or "not within 96", "First month revenue lens >= $1B": fr,
                                "First month AUM lens >= $1B": fa, "ARR at m96 (Rs)": arr96, "Revenue lens at m96 (Rs)": rl96,
                                "AUM lens at m96 (Rs)": al96, "Equity raised by m60 (Rs)": eq60,
                                "Equity raised by the unicorn month (Rs)": eq_um, "Equity raised by m96 (Rs)": seed["Amount"] + sum(r["Amount"] for r in rounds),
                                "Cash stays at or above 0 through m96": "yes" if of["cash"][0].min() >= 0 else "no",
                                "Cities open at m60": float(of["_city"][0]["open"][59]), "Active savers at m60": float(of["still_saving"][0, 59]),
                                "Year-5 EBITDA (Rs)": float(of["ebitda"][0, 48:60].sum()),
                                "Founders % after the last round by m60": next((r["Founders %"] for r in reversed(ct) if r["Month"] <= 60), ""),
                                "_key": (a18_, h_, cap_, X)})
    feasible = [r for r in res if r["Both lenses >= $1B at m60"] == "yes" and r["Cash stays at or above 0 through m96"] == "yes"]
    aum_only = [r for r in res if r["AUM lens >= $1B at m60"] == "yes" and r["Cash stays at or above 0 through m96"] == "yes"]
    reach = [r for r in res if isinstance(r["First month both lenses >= $1B"], int) and r["Cash stays at or above 0 through m96"] == "yes"]
    best_aum = min(aum_only, key=lambda r: (r["Equity raised by m60 (Rs)"], r["Equity raised by m96 (Rs)"])) if aum_only else None
    if feasible:
        rec = min(feasible, key=lambda r: (r["Equity raised by m60 (Rs)"], r["Equity raised by m96 (Rs)"]))
        rec_role = "RECOMMENDED: least equity, both lenses >= $1B at m60 under saturation"
    elif reach:
        um_best = min(r["First month both lenses >= $1B"] for r in reach)
        cand = [r for r in reach if r["First month both lenses >= $1B"] == um_best]
        rec = min(cand, key=lambda r: (r["Equity raised by the unicorn month (Rs)"], r["Equity raised by m96 (Rs)"]))
        rec_role = "RECOMMENDED (no plan is a unicorn on paper at m60): the earliest month both lenses clear, least equity by then"
    elif best_aum is not None:
        rec = best_aum
        rec_role = "RECOMMENDED (no plan clears both lenses by m96): (a) the least-equity AUM-lens-only unicorn at m60"
    else:
        rec = max(res, key=lambda r: min(r["Revenue lens at m60 (Rs)"], r["AUM lens at m60 (Rs)"]))
        rec_role = "RECOMMENDED (nothing clears): the highest lower lens at m60"
    top_rl = max(res, key=lambda r: r["Revenue lens at m60 (Rs)"])
    top_al = max(res, key=lambda r: r["AUM lens at m60 (Rs)"])
    for r in res:
        r["Role"] = "; ".join(l for l, p in ((rec_role, rec), ("(a) least-equity AUM-lens-only unicorn at m60", best_aum if best_aum is not rec else None),
                                             ("(b) highest revenue-lens valuation at m60", top_rl), ("(b) highest AUM-lens valuation at m60", top_al))
                              if p is not None and p is r)
    C.write("sat_unicorn_replan_search.csv", [{k: v for k, v in r.items() if not k.startswith("_")} for r in res])
    a18r, hr, capr, Xr = rec["_key"]
    sat2 = sat_cfg(addr, X=Xr)
    o2, fl2 = run(x, dists, sat2, target_fn=U.path_fn(a18r, hr, capr))
    um2 = first_unicorn_month(o2)
    seed2, rounds2, rds2, ct2, of2 = plan_and_price(o2, um2)
    extra = {"First month both lenses >= $1B (the unicorn month)": um2 or "not within 96",
             "Revenue lens at the unicorn month (Rs)": lens(of2, um2)[0] if um2 else "", "AUM lens at the unicorn month (Rs)": lens(of2, um2)[1] if um2 else ""}
    C.write("sat_unicorn_replan_yearly.csv", yearly(f"2. Re-plan under saturation (AUTO): {a18r} agents by m18, +{hr} a month, cap {capr:,}, "
                                                    f"open a city below {Xr:,.0f} headroom a head", of2, sat2, extra))
    C.write("sat_unicorn_replan_rounds.csv", [{"Round": r["Round"], "Month": r["Month"], "Amount (Rs)": r["Amount"], "Pre-money (Rs)": r["Pre"],
                                               "Post-money (Rs)": r["Post"], "Dilution (new investors' share of post-money)": r["Dilution"],
                                               "Founders % after": r["Founders %"], "ESOP % after": r["ESOP %"], "Investors % after": r["Investors %"],
                                               "Priced on": r["Lens"], "Why this month": r["Why"],
                                               "Capped at 25% dilution": "yes" if r["Capped"] else "no",
                                               "Unicorn round": "yes" if r["Round"] == "E" else "",
                                               "Basis": "unicorn_plan.py rules (step-ups, lenses, 25% cap); valuations are our judgement"} for r in ct2])
    # the AUTO rollout -> tables/city_plan.csv, then PLANNED from that file
    plan_rows = plan_from_auto(of2, sat2, "starting plan: the AUTO rollout of the re-plan under saturation; edit the launch month and agents")
    C.write("city_plan.csv", plan_rows)
    plan = read_plan(C.T / "city_plan.csv")
    tg, launch = plan_targets(plan, CLASS_I)
    fleetP = C.make_city_fleet(dists, tg)
    satP = sat_cfg(addr, X=Xr, launch=launch)
    oP, _ = run(x, dists, satP, fleet=fleetP)
    ofP = funded(oP, seed2["Amount"], rds2)
    rep = []
    for nm, k, how in (("Cumulative sign-ups to m60", "signups", "sum60"), ("Active savers at m60", "still_saving", "m60"), ("AUM at m60", "fund_end", "m60"),
                       ("ARR at m60", "revenue", "m60x12"), ("Revenue, years 1-5", "revenue", "sum60"), ("Agents at m60", "agents", "m60"),
                       ("Revenue, years 1-8", "revenue", "sum"), ("Active savers at m96", "still_saving", "m96")):
        f_ = {"sum60": lambda a: float(a[0, :60].sum()), "m60": lambda a: float(a[0, 59]), "m60x12": lambda a: 12 * float(a[0, 59]),
              "sum": lambda a: float(a[0].sum()), "m96": lambda a: float(a[0, -1])}[how]
        va, vp = f_(of2[k]), f_(ofP[k])
        rep.append({"Measure": nm, "AUTO": va, "PLANNED (from city_plan.csv)": vp, "Gap (share)": vp / va - 1, "Within 1%": "yes" if abs(vp / va - 1) <= REPRO_TOL else "no"})
    e5a, e5p = float(of2["ebitda"][0, 48:60].sum()), float(ofP["ebitda"][0, 48:60].sum())
    rep.append({"Measure": "Year-5 EBITDA (gap as a share of year-5 revenue)", "AUTO": e5a, "PLANNED (from city_plan.csv)": e5p,
                "Gap (share)": (e5p - e5a) / float(of2["revenue"][0, 48:60].sum()), "Within 1%": "yes" if abs(e5p - e5a) <= REPRO_TOL * float(of2["revenue"][0, 48:60].sum()) else "no"})
    C.write("sat_planned_vs_auto.csv", rep)
    chk("PLANNED mode from city_plan.csv reproduces AUTO within 1% (sign-ups, savers, AUM, ARR, revenue, agents, year-5 EBITDA)",
        all(r["Within 1%"] == "yes" for r in rep), "; ".join(f"{r['Measure']} {r['Gap (share)']:+.2%}" for r in rep))
    coP = ofP["_city"][0]
    chk("PLANNED: city agents add to the company's agents and follow the plan", np.allclose(coP["agents"].sum(axis=0), ofP["agents"][0])
        and np.allclose(coP["agents"].sum(axis=0), tg[:, 1:].sum(axis=0)))
    chk("PLANNED: no city's cumulative sign-ups exceed its cap", bool((coP["cum"][:, -1] <= coP["cap"] * (1 + 1e-12) + 1e-6).all()))
    chk("PLANNED: city CM2 adds to the company's CM2", np.allclose(coP["cm2"].sum(axis=0), ofP["cm2"][0], rtol=1e-9, atol=1e-2))
    C.write("city_plan_warnings.csv", plan_warnings(plan, ofP, satP, per_agent_5y))
    C.write("sat_city_yearly.csv", city_yearly("Re-plan, PLANNED mode (city_plan.csv)", ofP, satP))
    C.write("sat_cities_open_by_month.csv", [{"Month": t + 1, "Run 1: current unicorn plan with saturation": float(co1["open"][t]),
                                              "Re-plan, AUTO": float(of2["_city"][0]["open"][t]), "Re-plan, PLANNED (city_plan.csv)": float(coP["open"][t])}
                                             for t in range(C.M)])
    C.write("sat_ncr.csv", ncr_rows("1. Current unicorn plan with saturation", o1, sat1) + ncr_rows("2. Re-plan, PLANNED (city_plan.csv)", ofP, satP))
    C.write("sat_city_penetration.csv", penetration_rows("1. Current unicorn plan with saturation", o1, sat1)
            + penetration_rows("2. Re-plan, PLANNED (city_plan.csv)", ofP, satP))

    # run 4: the profitable plans (60 months), funding as sized in growth_model, and re-sized with saturation
    C.set_horizon(60)
    gs = {(int(r["Agents at m18"]), int(r["Hires a month after m18"]), r["Faster hiring once EBITDA is positive"] != "no"): r
          for r in csv.DictReader((C.T / "growth_search.csv").open())}
    prow = []
    for a18p, hp, faster, label in PROFITABLE:
        g = gs[(a18p, hp, faster)]
        seed_g, a_g = float(g["Seed at m0, Series A at m18 (Rs)"]), float(g["Series A at m18 (Rs)"])
        tfp, _ = G.target_fn(a18p, hp, faster)
        variants = [(False, None), (True, OPEN_HEADROOM)] + ([(True, 10000.0), (True, 25000.0), (True, 50000.0)] if not faster else [])
        for sat_on, Xp in variants:
            sat = sat_cfg(addr, X=Xp) if sat_on else None
            o, fl = run(x, dists, sat, target_fn=tfp, central=G.CENTRAL, stepup=faster)
            tr = C.treasury(o, seed_size=seed_g, rounds=[(18, a_g)])
            sd, rr, feas = C.size_funding(o, [18])
            tr2 = C.treasury(o, seed_size=sd, rounds=rr)
            co = o.get("_city", [None])[0]
            for y in range(5):
                sl = slice(12 * y, 12 * y + 12)
                prow.append({"Plan": label, "Saturation": f"on, open a city below {Xp:,.0f} headroom a head" if sat_on else "off", "Year": y + 1,
                             "Revenue (Rs)": float(o["revenue"][0, sl].sum()), "EBITDA (Rs)": float(o["ebitda"][0, sl].sum()),
                             "PAT with its growth_model funding (Rs)": float(tr["pat"][0, sl].sum()),
                             "Cash at year end, growth_model funding (Rs)": float(tr["cash"][0, 12 * y + 11]),
                             "Active savers at year end": float(o["still_saving"][0, 12 * y + 11]),
                             "Sign-ups in the year": float(o["signups"][0, sl].sum()), "Agents at year end": float(o["agents"][0, 12 * y + 11]),
                             "Cities open at year end": float(o["cities"][0, 12 * y + 11]),
                             "NCR penetration at year end": float(co["cum"][0, 12 * y + 11] / addr[0]) if co is not None else "",
                             "Funding (growth_model): seed + Series A at m18 (Rs)": seed_g + a_g,
                             "Funding re-sized for this run: seed + Series A (Rs)": float(sd[0] + rr[0][1][0]),
                             "PAT with re-sized funding (Rs)": float(tr2["pat"][0, sl].sum())})
    C.write("sat_profitable_yearly.csv", prow)
    C.set_horizon(HORIZON)
    C.write("sat_checks.csv", checks)
    print(f"  q = {q:.4f}; top 50 {share[:50].sum():.1%}, top 150 {share[:150].sum():.1%}, top 500 {share[:500].sum():.1%}; "
          f"Class I pool {addr.sum() / CR:.2f} crore; per-agent 5-year sign-ups {per_agent_5y:,.0f}")
    print(f"  re-plan: feasible at m60: {bool(feasible)}; recommended {rec['_key']} unicorn month {rec['First month both lenses >= $1B']}; "
          f"AUM-only best: {best_aum['_key'] if best_aum else None}; top revenue lens {top_rl['Revenue lens at m60 (Rs)'] / CR:,.0f} cr {top_rl['_key']}; "
          f"top AUM lens {top_al['AUM lens at m60 (Rs)'] / CR:,.0f} cr {top_al['_key']}")
    print(f"  checks {sum(c['Passes'] for c in checks)}/{len(checks)}")
    for c in checks:
        if not c["Passes"]:
            print("  FAIL", c["Check"], c["Note"])
    return checks


if __name__ == "__main__":
    main()

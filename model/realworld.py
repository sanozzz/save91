"""The locked real-world setting, and the NBFC test (story/BRIEF_realworld_lock_and_nbfc_2026-10-17.md; operator taps "Lock
real-world setting" and "Test NBFC from year 3").

THE REAL-WORLD SETTING (locked for every run here; the earlier scripts keep their own defaults, so their tables are unchanged):
the city layer ON, soft saturation 1 - (pen/cap)^2, the pool refilling 3% a year, at most 4 new cities a month, a 20% city cap,
the urban self-employed pool 7.0 crore (pert 6.5/7.0/7.7) on the rank-size estimate, about 500 Class I cities.
  rw profitable  growth_model's 200-agent plan (200 by m18, then replace leavers; central as built), cities by the AUTO rule
                 (opening threshold 5,000 or 10,000 headroom a head, the better year-5 PAT), 60 months; funding sized by the
                 CAPPED rule below (fixes the seed, which diluted 31% at Rs 40 crore pre-money).
  rw unicorn     the best unicorn attempt (AUM lens only) of sat_sensitivity under this setting, 96 months, unicorn_plan's rounds.
CAPPED FUNDING (the profitable plans): the seed is the smallest that keeps month-end cash >= Rs 5 crore to m18, rounded up to
Rs 1 crore, but at most Rs 40 crore pre-money / 3 (25% dilution); each later round closes in the first month cash would fall
below Rs 5 crore, sized as the smallest that keeps cash >= Rs 5 crore to the horizon (rounded up to Rs 5 crore) and capped at
25% dilution of a pre-money = the higher of the step-up on the previous post-money (A 3.0x, B 3.0x, C 2.5x, D 2.0x, then 1.5x)
and the lens on that month's metrics (A: 25 x ARR or 0.45 x AUM; later 20x), never below the previous post. ESOP 10% at the
seed, A and B (unicorn_plan.cap_table).
NBFC (nbfc.py): NB1 the rw profitable plan + NBFC from m30; NB2 the least-equity unicorn on paper at m60 (lenses 1 and 2) with
the NBFC, searched on saturation.py's grid under the real-world setting, unicorn_plan's rounds; NB3 = NB2's path with an 80%
on-book share (rounds re-planned).

Writes tables/rw_profitable_{yearly,monthly,rounds,city_plan}.csv, rw_unicorn_{...}.csv, rw_checks.csv and
nbfc_{inputs,yearly,rounds,lenses,checks}.csv.
"""
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import growth_model as G           # noqa: E402
import nbfc as NB                  # noqa: E402
import saturation as S             # noqa: E402
import unicorn_plan as U           # noqa: E402

CR = C.CRORE
RW = {"shape": "square", "refill": 0.03, "max_new_per_month": 4, "cap": 0.20}
FLOOR = 5 * CR
PROFIT_X = (5000.0, 10000.0)
LATER_STEP = 1.5


def rw_cfg(addr, X=S.OPEN_HEADROOM):
    c = S.sat_cfg(addr, X=X, shape=RW["shape"])
    c.update(refill=RW["refill"], max_new_per_month=RW["max_new_per_month"], cap=RW["cap"])
    return c


def capped_rounds(o, a_by=18):
    """The CAPPED funding rule on one path (module docstring). Returns the seed and the rounds as cap-table dicts."""
    M = C.M
    cash = lambda sd, rds: C.treasury(o, seed_size=sd, rounds=rds)["cash"][0]

    def bisect(ok, hi=5000 * CR, steps=46):
        lo = 0.0
        if ok(lo):
            return 0.0
        for _ in range(steps):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if ok(mid) else (mid, hi)
        return hi
    need = U.ceil_to(bisect(lambda sd: cash(sd, [(a_by, 0.0, True)])[:a_by].min() >= FLOOR), CR)
    cap_seed = U.floor_to(U.SEED_PRE / 3, CR)
    seed = {"Round": "Seed", "Month": 0, "Amount": min(need, cap_seed), "Pre": U.SEED_PRE, "Lens": "fixed Rs 40 crore",
            "Why": "start", "Capped": need > cap_seed, "Wanted": need}
    rounds, prev_post, k = [], U.SEED_PRE + seed["Amount"], 0
    while k < 20:
        rds = [(r["Month"], r["Amount"]) for r in rounds]
        c = cash(seed["Amount"], rds)
        last = rounds[-1]["Month"] if rounds else 0
        below = np.nonzero(c[last:] < FLOOR)[0]
        if below.size == 0:
            break
        t = int(last + below[0] + 1)
        stage = U.LETTERS[k]
        step = U.STEP_UP.get(stage, LATER_STEP)
        rl, al, arr, aum = U.lens_values(o, t, 0, stage)
        stepped = step * prev_post
        pre = max(stepped, rl, al, prev_post)
        want = U.ceil_to(bisect(lambda a: cash(seed["Amount"], rds + [(t, a)])[t - 1:].min() >= FLOOR), 5 * CR)
        cap_amt = U.floor_to(pre / 3, CR)
        amt = min(want, cap_amt)
        rounds.append({"Round": stage, "Month": t, "Amount": amt, "Pre": pre,
                       "Lens": f"step-up {step:g}x" if stepped >= max(rl, al) else ("revenue lens" if rl >= al else "AUM lens"),
                       "Why": "cash would fall below Rs 5 crore", "Capped": want > cap_amt, "Wanted": want})
        prev_post, k = pre + amt, k + 1
        if amt <= 0:
            break
    return seed, rounds


def rounds_rows(run, ct):
    return [{"Run": run, "Round": r["Round"], "Month": r["Month"], "Amount (Rs)": r["Amount"], "Pre-money (Rs)": r["Pre"],
             "Post-money (Rs)": r["Post"], "Dilution (new investors' share of post-money)": r["Dilution"],
             "Founders % after": r["Founders %"], "ESOP % after": r["ESOP %"], "Investors % after": r["Investors %"],
             "Priced on": r["Lens"], "Why this month": r["Why"], "Capped at 25% dilution": "yes" if r["Capped"] else "no",
             "Basis": "valuations are our judgement (step-ups and lenses)"} for r in ct]


def yearly_rows(run, of, sat):
    co = of["_city"][0]
    Y = C.M // 12
    s = lambda a: [float(a[0, 12 * y:12 * y + 12].sum()) for y in range(Y)]
    e = lambda a: [float(a[0, 12 * y + 11]) for y in range(Y)]
    capm = co["cap_by_month"]
    pool_m = capm / RW["cap"]
    cum = co["cum"].sum(axis=0)
    rows = []

    def add(m, u, vals):
        rows.append({"Run": run, "Line": m, "Unit": u, **{f"Year {y + 1}": vals[y] for y in range(Y)}})
    nb = "nbfc_book" in of
    for k, nm in C.REVENUE:
        add(f"Revenue: {nm}", "Rs", s(of[k]))
    if nb:
        add("Fee revenue, total", "Rs", s(of["fee_revenue"]))
        add("NBFC: interest income", "Rs", s(of["nbfc_interest"]))
        add("NBFC: cost of funds", "Rs", s(of["nbfc_cost_of_funds"]))
        add("NBFC: net interest income", "Rs", s(of["nbfc_nii"]))
        add("NBFC: processing fees", "Rs", s(of["nbfc_processing"]))
    add("Revenue, total", "Rs", s(of["revenue"]))
    add("Direct costs", "Rs", s(of["direct"]))
    if nb:
        add("NBFC: credit cost (expected-loss provisions)", "Rs", s(of["nbfc_credit_cost"]))
    for k, nm in (("cm1", "CM1"), ("cm2", "CM2"), ("cm3", "CM3"), ("central", "Central costs"), ("ebitda", "EBITDA"),
                  ("depreciation", "Depreciation"), ("interest", "Interest on cash"), ("tax", "Income tax"), ("pat", "PAT")):
        add(nm, "Rs", s(of[k]))
    if nb:
        add("NBFC: opex and licence (in central costs)", "Rs", s(of["nbfc_central"]))
    add("Equity raised", "Rs", s(of["cf_financing"]))
    if nb:
        add("NBFC: borrowings at year end", "Rs", e(of["nbfc_borrowings"]))
        add("NBFC: loan book at year end (net of provisions)", "Rs", e(of["nbfc_book"]))
        add("NBFC: equity in the book at year end", "Rs", e(of["nbfc_equity"]))
        add("NBFC: on-book loans disbursed in the year", "Rs", s(of["nbfc_disbursed"]))
        add("NBFC: on-book share of personal-loan volume at year end", "share", e(of["nbfc_share"]))
    add("Cash at year end", "Rs", e(of["cash"]))
    add("Lowest month-end cash in the year", "Rs", [float(of["cash"][0, 12 * y:12 * y + 12].min()) for y in range(Y)])
    add("Agents at year end", "agents", e(of["agents"]))
    add("Cities open at year end", "cities", [float(co["open"][12 * y + 11]) for y in range(Y)])
    add("Central team at year end", "people", e(of["hc_central"]))
    add("Sign-ups in the year", "sign-ups", s(of["signups"]))
    add("Active savers at year end", "savers", e(of["still_saving"]))
    add("AUM at year end", "Rs", e(of["fund_end"]))
    add("ARR at year end (12 x the month's revenue)", "Rs", [12 * v for v in e(of["revenue"])])
    add("Money lent in the year, personal loans incl. top-ups (all, on and off book)", "Rs", s(of["money_lent"]))
    add("Money lent in the year, home loans and LAP (other lenders)", "Rs", s(of["housing_lent"]))
    nat = S.POOL * (1 + RW["refill"]) ** (np.arange(C.M) / 12)          # the national pool, refilling as the city pools do
    add("National penetration at year end (cumulative sign-ups / the growing national pool)", "share",
        [float(cum[12 * y + 11] / nat[12 * y + 11]) for y in range(Y)])
    add("NCR penetration at year end (of its growing pool)", "share", [float(co["cum"][0, 12 * y + 11] / pool_m[0, 12 * y + 11]) for y in range(Y)])
    return rows


def summary_row(run, of, ct, feasible, path, horizon):
    L = NB.lenses(of)
    eq60 = sum(r["Amount"] for r in ct if r["Month"] <= 60)
    be = C.stays_positive_from(of["ebitda"])[0]
    return {"Run": run, "Feasible": feasible, "Path": path, "Horizon": horizon, "Total raised by m60 (Rs)": eq60,
            "Total raised (Rs)": sum(r["Amount"] for r in ct),
            "Founders % after the last round by m60": next((r["Founders %"] for r in reversed(ct) if r["Month"] <= 60), ""),
            "Active savers at m60": float(of["still_saving"][0, 59]), "AUM at m60 (Rs)": L["AUM"],
            "Loan book at m60 (Rs)": float(of["nbfc_book"][0, 59]) if "nbfc_book" in of else 0.0, "NBFC equity at m60 (Rs)": L["NBFC equity"],
            "ARR at m60 (Rs)": L["ARR"], "Fee ARR at m60 (Rs)": L["Fee ARR"],
            **{k: L[k] for k in ("Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)", "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
            **{f"{k} margin over $1B": L[k] / U.UNICORN - 1 for k in ("Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)", "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
            "EBITDA break-even month (stays positive)": "not within the horizon" if np.isnan(be) else float(be),
            **{f"EBITDA year {y} (Rs)": float(of["ebitda"][0, 12 * (y - 1):12 * y].sum()) for y in range(1, 6)},
            **{f"PAT year {y} (Rs)": float(of["pat"][0, 12 * (y - 1):12 * y].sum()) for y in range(1, 6)},
            "Lowest cash (Rs)": float(of["cash"][0].min()), "Month of the lowest cash": int(of["cash"][0].argmin() + 1),
            "Cities open at m60": float(of["_city"][0]["open"][59])}


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, share = S.city_curve()
    addr = share[:S.CLASS_I] * S.POOL
    rwchk, nbchk = [], []
    add = lambda lst, name, ok, note="": lst.append({"Check": name, "Passes": bool(ok), "Note": note})

    # ---- 1a. rw profitable (60 months), capped funding
    C.set_horizon(60)
    tfp, _ = G.target_fn(200, 0, False)
    best = None
    for X in PROFIT_X:
        sat = rw_cfg(addr, X)
        o, fl = S.run(x, dists, sat, target_fn=tfp, central=G.CENTRAL)
        seed, rounds = capped_rounds(o)
        rds = [(r["Month"], r["Amount"]) for r in rounds]
        of = U.apply_funding(o, seed["Amount"], rds)
        pat5 = float(of["pat"][0, 48:60].sum())
        if best is None or pat5 > best[0]:
            best = (pat5, X, o, of, seed, rounds, sat)
    pat5, Xp, op_, ofp, seedp, roundsp, satp = best
    ctp = U.cap_table(seedp, roundsp)
    prof_path = f"200 agents by m18, then replace leavers; central as built; open a city below {Xp:,.0f} headroom a head (at most 4 a month)"
    C.write("rw_profitable_yearly.csv", yearly_rows("rw profitable: " + prof_path, ofp, satp))
    C.write("rw_profitable_monthly.csv", U.monthly_rows(ofp))
    C.write("rw_profitable_rounds.csv", rounds_rows("rw profitable", ctp))
    C.write("rw_profitable_city_plan.csv", S.plan_from_auto(ofp, satp, "real-world default: AUTO rollout of the profitable plan; edit freely"))
    add(rwchk, "rw profitable: every round dilutes at most 25% (the seed fixed)", all(r["Dilution"] <= 0.25 + 1e-12 for r in ctp),
        "; ".join(f"{r['Round']} {r['Dilution']:.1%}" for r in ctp))
    add(rwchk, "rw profitable: cash stays at or above Rs 5 crore after the seed", float(ofp["cash"][0].min()) >= FLOOR - 1, f"lowest Rs {float(ofp['cash'][0].min()):,.0f}")
    add(rwchk, "rw profitable: cap table sums to 100% after every round", all(abs(r["Founders %"] + r["ESOP %"] + r["Investors %"] - 1) < 1e-12 for r in ctp))
    co = ofp["_city"][0]
    add(rwchk, "rw profitable: at most 4 new cities a month", float(np.diff(co["open"], prepend=0).max()) <= 4)
    add(rwchk, "rw profitable: no city past its (growing) cap", bool((co["cum"] <= co["cap_by_month"] * (1 + 1e-12) + 1e-6).all()))
    add(rwchk, "rw profitable: city CM2 adds to the company's CM2", np.allclose(co["cm2"].sum(axis=0), op_["cm2"][0], rtol=1e-9, atol=1e-2))

    # ---- 1b. rw unicorn attempt (96 months): sat_sensitivity's AUM-only path for this setting
    C.set_horizon(S.HORIZON)
    import csv
    sens = [r for r in csv.DictReader((C.T / "sat_sensitivity.csv").open())
            if r["Combination"].startswith("Soft curve + 3% refill + 4 cities") and r["Plan"].startswith("(a)")][0]
    mt = re.match(r"(\d+) by m18, \+(\d+) a month, cap ([\d,]+), open a city below ([\d,]+)", sens["Path"])
    a18, h, capn, Xu = [float(v.replace(",", "")) for v in mt.groups()]
    a18, h, capn = int(a18), int(h), int(capn)
    satu = rw_cfg(addr, Xu)
    ou, _ = S.run(x, dists, satu, target_fn=U.path_fn(a18, h, capn))
    seedu, roundsu, rdsu, ctu, ofu = S.plan_and_price(ou, S.first_unicorn_month(ou))
    uni_path = f"{a18} agents by m18, +{h} a month, cap {capn:,}; open a city below {Xu:,.0f} headroom a head (at most 4 a month)"
    C.write("rw_unicorn_yearly.csv", yearly_rows("rw unicorn attempt (AUM lens only): " + uni_path, ofu, satu))
    C.write("rw_unicorn_monthly.csv", U.monthly_rows(ofu))
    C.write("rw_unicorn_rounds.csv", rounds_rows("rw unicorn attempt", ctu))
    C.write("rw_unicorn_city_plan.csv", S.plan_from_auto(ofu, satu, "real-world default: AUTO rollout of the unicorn attempt; edit freely"))
    add(rwchk, "rw unicorn: reproduces sat_sensitivity's row (total raised by m60)",
        abs(sum(r["Amount"] for r in ctu if r["Month"] <= 60) - float(sens["Total raised by m60 (Rs)"])) < 1, sens["Total raised by m60 (Rs)"])
    add(rwchk, "rw unicorn: cash stays at or above 0 through m96", float(ofu["cash"][0].min()) >= 0)
    C.write("rw_checks.csv", rwchk)

    # ---- 2. NBFC
    C.write("nbfc_inputs.csv", [{"Input": k, "Value": (float(np.mean(x["rate"])) if k == "yield" else float(np.mean(x["loss"])) if k == "loss" else v),
                                 "Unit": u, "What it is": w, "Basis": b} for k, v, u, w, b in NB.NBFC_INPUTS])
    summ, yr_rows, rnd_rows = [], [], []
    # NB1: the rw profitable plan + NBFC from m30 (60 months), capped funding
    C.set_horizon(60)
    o1n = NB.apply_nbfc(op_, x)
    s1, r1 = capped_rounds(o1n)
    of1 = NB.funded(o1n, s1["Amount"], [(r["Month"], r["Amount"]) for r in r1])
    ct1 = U.cap_table(s1, r1)
    e1 = C.stays_positive_from(of1["ebitda"])[0]
    feas1 = (not np.isnan(e1)) and e1 <= 60 and float(of1["pat"][0, 48:60].sum()) >= 0
    summ.append({**summary_row("NB1: rw profitable + NBFC from m30", of1, ct1, "yes" if feas1 else "no", prof_path, "60 months"),
                 "Year-5 revenue added by the book vs rw profitable (Rs)": float(of1["revenue"][0, 48:60].sum() - ofp["revenue"][0, 48:60].sum()),
                 "Year-5 PAT added by the book vs rw profitable (Rs)": float(of1["pat"][0, 48:60].sum() - ofp["pat"][0, 48:60].sum())})
    summ.append(summary_row("rw profitable (no NBFC), for comparison", {**ofp, "nbfc_equity": np.zeros_like(ofp["revenue"])}, ctp,
                            "yes" if float(ofp["pat"][0, 48:60].sum()) >= 0 else "no", prof_path, "60 months"))
    yr_rows += yearly_rows("NB1: rw profitable + NBFC from m30", of1, satp)
    rnd_rows += rounds_rows("NB1", ct1)
    nb_checks(nbchk, "NB1", of1, ct1, add)
    # NB2: the least-equity unicorn on paper at m60 (lenses 1 and 2) with the NBFC, real-world setting, 96 months
    C.set_horizon(S.HORIZON)
    cands = []
    for a18_ in S.REPLAN_GRID[0]:
        for h_ in S.REPLAN_GRID[1]:
            for cap_ in S.REPLAN_GRID[2]:
                for X in S.REPLAN_GRID[3]:
                    sat = rw_cfg(addr, X)
                    o, _ = S.run(x, dists, sat, target_fn=U.path_fn(a18_, h_, cap_))
                    on = NB.apply_nbfc(o, x)
                    L = NB.lenses(on)
                    seed, rounds = U.plan_rounds(on)
                    rds = [(r["Month"], r["Amount"]) for r in rounds]
                    of = NB.funded(on, seed["Amount"], rds)
                    ok = min(L["Lens 1 (20 x ARR)"], L["Lens 2 (0.45 x AUM)"]) >= U.UNICORN and float(of["cash"][0].min()) >= 0
                    eq60 = seed["Amount"] + sum(r["Amount"] for r in rounds if r["Month"] <= 60)
                    cands.append((ok, eq60, min(L["Lens 1 (20 x ARR)"], L["Lens 2 (0.45 x AUM)"]), (a18_, h_, cap_, X), of, seed, rounds, sat))
    feas = [cd for cd in cands if cd[0]]
    pick2 = min(feas, key=lambda cd: cd[1]) if feas else max(cands, key=lambda cd: cd[2])
    _ok2, _eq2, _m2, key2, of2, s2, r2, sat2 = pick2
    ct2 = U.cap_table(s2, r2)
    path2 = f"{key2[0]} agents by m18, +{key2[1]} a month, cap {key2[2]:,}; open a city below {key2[3]:,.0f} headroom a head (at most 4 a month)"
    summ.append(summary_row("NB2: least-equity unicorn on paper at m60 (lenses 1 and 2) + NBFC from m30", of2, ct2,
                            "yes" if feas else "no: best attempt shown", path2, "96 months"))
    yr_rows += yearly_rows("NB2: unicorn attempt + NBFC from m30", of2, sat2)
    rnd_rows += rounds_rows("NB2", ct2)
    nb_checks(nbchk, "NB2", of2, ct2, add)
    add(nbchk, f"NB2: {len(feas)} of {len(cands)} paths clear lenses 1 and 2 at m60 with cash >= 0", True)
    # NB3: NB2's path with an 80% on-book share
    o3, _ = S.run(x, dists, sat2, target_fn=U.path_fn(key2[0], key2[1], key2[2]))
    o3n = NB.apply_nbfc(o3, x, {"share_full": 0.80})
    s3, r3 = U.plan_rounds(o3n)
    of3 = NB.funded(o3n, s3["Amount"], [(r["Month"], r["Amount"]) for r in r3])
    ct3 = U.cap_table(s3, r3)
    L3 = NB.lenses(of3)
    feas3 = min(L3["Lens 1 (20 x ARR)"], L3["Lens 2 (0.45 x AUM)"]) >= U.UNICORN and float(of3["cash"][0].min()) >= 0
    summ.append(summary_row("NB3: NB2's path with an 80% on-book share", of3, ct3, "yes" if feas3 else "no", path2, "96 months"))
    yr_rows += yearly_rows("NB3: NB2 path, 80% on-book", of3, sat2)
    rnd_rows += rounds_rows("NB3", ct3)
    nb_checks(nbchk, "NB3", of3, ct3, add)
    cols = list(dict.fromkeys(k for r in summ for k in r))
    C.write("nbfc_lenses.csv", [{k: r.get(k, "") for k in cols} for r in summ])
    ycols = list(dict.fromkeys(k for r in yr_rows for k in r))
    C.write("nbfc_yearly.csv", [{k: r.get(k, "") for k in ycols} for r in yr_rows])     # NB1 runs 5 years, NB2/NB3 8
    C.write("nbfc_rounds.csv", rnd_rows)
    C.write("nbfc_checks.csv", nbchk)
    C.set_horizon(60)
    for r in summ:
        print(f"  {r['Run'][:60]:<60} {r['Feasible']:<24} raised60 {r['Total raised by m60 (Rs)'] / CR:8,.0f} cr  L1 {r['Lens 1 (20 x ARR) margin over $1B']:+.1%} "
              f"L2 {r['Lens 2 (0.45 x AUM) margin over $1B']:+.1%}  book {r['Loan book at m60 (Rs)'] / CR:8,.0f}  eq {r['NBFC equity at m60 (Rs)'] / CR:6,.0f}  "
              f"PAT5 {r['PAT year 5 (Rs)'] / CR:7.2f}  low cash {r['Lowest cash (Rs)'] / CR:7.1f}")
    bad = [c["Check"] for c in rwchk + nbchk if not c["Passes"]]
    print(f"  checks: rw {sum(c['Passes'] for c in rwchk)}/{len(rwchk)}, nbfc {sum(c['Passes'] for c in nbchk)}/{len(nbchk)}" + (f"; FAIL {bad}" if bad else ""))
    return summ


def nb_checks(lst, run, of, ct, add):
    sh = of["nbfc_share"][0]
    lending = of["nbfc_book"][0] > 0
    add(lst, f"{run}: ladder: revenue - direct - credit cost - servicing - acquisition - central = EBITDA",
        np.allclose(of["revenue"] - of["direct"] - of["nbfc_credit_cost"] - of["servicing"] - of["acquisition"] - of["central"], of["ebitda"], rtol=1e-12, atol=1e-6))
    add(lst, f"{run}: revenue = fee revenue + NII + processing fees", np.allclose(of["fee_revenue"] + of["nbfc_nii"] + of["nbfc_processing"], of["revenue"], rtol=1e-12, atol=1e-6))
    add(lst, f"{run}: the book is funded: net book = equity deployed + borrowings",
        np.allclose(of["nbfc_book"], of["nbfc_equity"] - of["nbfc_idle_capital"] + of["nbfc_borrowings"], rtol=1e-12, atol=1e-3))
    add(lst, f"{run}: capital at least 20% of the book and borrowings at most 3x equity while lending",
        bool((of["nbfc_capital_ratio"][0][lending] >= 0.20 - 1e-12).all() and (of["nbfc_leverage"][0][lending] <= 3 + 1e-9).all()),
        f"capital {np.nanmin(of['nbfc_capital_ratio'][0][lending]) if lending.any() else float('nan'):.1%} at the lowest")
    add(lst, f"{run}: processing fees = 2% and credit cost = loss x on-book disbursals",
        np.allclose(of["nbfc_processing"], 0.02 * of["nbfc_disbursed"]) and np.allclose(of["nbfc_credit_cost"], of["_nbfc_loss"] * of["nbfc_disbursed"]))
    add(lst, f"{run}: on-book share 0 before m30, 10% at m30, full from m54", sh[28] == 0 and abs(sh[29] - 0.10) < 1e-12 and abs(sh[53] - of["_nbfc_cfg"]["share_full"]) < 1e-12)
    prev = np.concatenate([[0.0], of["cash"][0, :-1]])
    add(lst, f"{run}: cash roll: closing = previous + net change", np.allclose(prev + of["net_change"][0], of["cash"][0], rtol=1e-12, atol=1e-3))
    add(lst, f"{run}: cash stays at or above 0", float(of["cash"][0].min()) >= 0, f"lowest Rs {float(of['cash'][0].min()):,.0f}")
    add(lst, f"{run}: cap table sums to 100% and no round dilutes more than 25%",
        all(abs(r["Founders %"] + r["ESOP %"] + r["Investors %"] - 1) < 1e-12 and r["Dilution"] <= 0.25 + 1e-12 for r in ct))


if __name__ == "__main__":
    main()

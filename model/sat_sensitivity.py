"""Three sensitivities of the city layer (coordinator, 17 Oct 2026: "the current setup is harsher than reality").

  S1 curve   linear (1 - pen/cap, the current), soft (1 - (pen/cap)^2), late (full speed to half the cap, then a straight line
             to zero at the cap);
  S2 refill  the addressable pool (and each city's cap) grows 0%, 3% or 5% a year (new shops, migrants, people entering
             self-employment);
  S3 pace    at most 2, 4 or 8 new cities a month (the current AUTO rule has no limit and opens 500 in m16-m23).
For each combination: (a) the unicorn re-plan, the same grid and rules as saturation.py (least equity with both lenses >= $1B
at m60; else the least-equity AUM-lens-only unicorn; 96 months; rounds priced by unicorn_plan.py); (b) the profitable plan of
growth_model (200 agents by m18, then replace leavers; central as built; 60 months), with the city-opening threshold 5,000 or
10,000 headroom a head (the better PAT) and funding re-sized (growth_model's rule); its rounds priced like unicorn_plan's for
the founders' share (seed Rs 40 crore pre, A at the higher of 3x the seed post and the lens).

Writes tables/sat_sensitivity.csv.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import growth_model as G           # noqa: E402
import saturation as S             # noqa: E402
import unicorn_plan as U           # noqa: E402

CR = C.CRORE
COMBOS = (  # name, curve, refill, max new cities a month (None = no limit)
    ("Current: linear, no refill, no pace limit", "linear", 0.0, None),
    ("Soft curve + 3% refill + 4 cities a month", "square", 0.03, 4),
    ("Late curve + 5% refill + 4 cities a month", "late", 0.05, 4),
    ("Soft curve + no refill + 2 cities a month", "square", 0.0, 2),
    ("Linear + no refill + 4 cities a month (pace alone)", "linear", 0.0, 4),
    ("Soft curve alone (no refill, no pace limit)", "square", 0.0, None),
    ("Late curve alone (no refill, no pace limit)", "late", 0.0, None),
    ("3% refill alone (linear, no pace limit)", "linear", 0.03, None),
    ("Late curve + 3% refill + 4 cities a month", "late", 0.03, 4),
)
PROFIT_X = (5000.0, 10000.0)


def cfg(addr, curve, refill, pace, X=S.OPEN_HEADROOM):
    c = S.sat_cfg(addr, X=X, shape=curve)
    c["refill"] = refill
    c["max_new_per_month"] = pace
    return c


def be_text(o):
    v = C.stays_positive_from(o["ebitda"])[0]
    return "not within the horizon" if np.isnan(v) else float(v)


def replan(x, dists, addr, curve, refill, pace):
    best_both, best_aum = None, None
    for a18 in S.REPLAN_GRID[0]:
        for h in S.REPLAN_GRID[1]:
            for capn in S.REPLAN_GRID[2]:
                for X in S.REPLAN_GRID[3]:
                    sat = cfg(addr, curve, refill, pace, X)
                    o, _ = S.run(x, dists, sat, target_fn=U.path_fn(a18, h, capn))
                    rl, al, arr, aum = S.lens(o, 60)
                    if al < U.UNICORN:
                        continue
                    um = S.first_unicorn_month(o)
                    seed, rounds, rds, ct, of = S.plan_and_price(o, um)
                    if of["cash"][0].min() < 0:
                        continue
                    eq60 = seed["Amount"] + sum(r["Amount"] for r in rounds if r["Month"] <= 60)
                    item = (eq60, seed["Amount"] + sum(r["Amount"] for r in rounds), (a18, h, capn, X), of, ct, sat)
                    if rl >= U.UNICORN and (best_both is None or item[:2] < best_both[:2]):
                        best_both = item
                    if best_aum is None or item[:2] < best_aum[:2]:
                        best_aum = item
    return best_both, best_aum


def row(combo, plan_kind, feasible, path, raised, founders, of, horizon_note, extra=None):
    rl, al, arr, aum = S.lens(of, 60)
    co = of.get("_city", [None])[0]
    return {"Combination": combo[0], "Saturation curve": {"linear": "linear (current)", "square": "soft", "late": "late"}[combo[1]],
            "Pool refill a year": combo[2], "Most new cities a month": combo[3] if combo[3] else "no limit", "Plan": plan_kind,
            "Feasible": feasible, "Path": path, "Total raised by m60 (Rs)": raised, "Founders % (after the last round by m60)": founders,
            "Active savers at m60": float(of["still_saving"][0, 59]), "ARR at m60 (Rs)": arr, "AUM at m60 (Rs)": aum,
            "Revenue lens margin over $1B at m60": rl / U.UNICORN - 1, "AUM lens margin over $1B at m60": al / U.UNICORN - 1,
            "EBITDA break-even month (stays positive)": be_text(of), "Cities open at m60": float(co["open"][59]) if co else float(of["cities"][0, 59]),
            "Year-5 EBITDA (Rs)": float(of["ebitda"][0, 48:60].sum()), "Year-5 PAT (Rs)": float(of["pat"][0, 48:60].sum()),
            "Horizon": horizon_note, **(extra or {})}


def price_two_rounds(seed_amt, a_amt, o):
    """Founders' share for a seed + Series A plan, priced like unicorn_plan (seed Rs 40 crore pre; A at the higher of 3x the
    seed post and the m18 lens), with the 10% ESOP at both; no dilution cap (reported)."""
    rl, al, *_ = U.lens_values(o, 18, 0, "A")
    seed = {"Round": "Seed", "Month": 0, "Amount": seed_amt, "Pre": U.SEED_PRE}
    a = {"Round": "A", "Month": 18, "Amount": a_amt, "Pre": max(U.STEP_UP["A"] * (U.SEED_PRE + seed_amt), rl, al)}
    ct = U.cap_table(seed, [a] if a_amt > 0 else [])
    return ct[-1]["Founders %"], max(r["Dilution"] for r in ct)


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, share = S.city_curve()
    addr = share[:S.CLASS_I] * S.POOL
    rows = []
    for combo in COMBOS:
        name, curve, refill, pace = combo
        C.set_horizon(S.HORIZON)
        both, aum_only = replan(x, dists, addr, curve, refill, pace)
        pick = both or aum_only
        if pick is None:
            rows.append({"Combination": name, "Plan": "(a) unicorn re-plan", "Feasible": "no: not even the AUM lens at m60"})
        else:
            eq60, _eq96, key, of, ct, sat = pick
            founders = next((r["Founders %"] for r in reversed(ct) if r["Month"] <= 60), "")
            rows.append(row(combo, "(a) unicorn re-plan", "yes: both lenses" if both else "AUM lens only", f"{key[0]} by m18, +{key[1]} a month, cap {key[2]:,}, "
                            f"open a city below {key[3]:,.0f} a head", eq60, founders, of, "96 months"))
        C.set_horizon(60)
        tfp, _ = G.target_fn(200, 0, False)
        best = None
        for X in PROFIT_X:
            sat = cfg(addr, curve, refill, pace, X)
            o, _ = S.run(x, dists, sat, target_fn=tfp, central=G.CENTRAL)
            sd, rr, feas = C.size_funding(o, [18])
            of = dict(o)
            of.update(C.treasury(o, seed_size=sd, rounds=rr))
            pat5 = float(of["pat"][0, 48:60].sum())
            if best is None or pat5 > best[0]:
                best = (pat5, X, of, float(sd[0]), float(rr[0][1][0]))
        pat5, X, of, sd, ra = best
        fp, maxdil = price_two_rounds(sd, ra, of)
        rows.append(row(combo, "(b) profitable plan: 200 agents by m18, then replace leavers", "yes: year-5 PAT >= 0" if pat5 >= 0 else "no: year-5 PAT < 0",
                        f"200 by m18, replace leavers; open a city below {X:,.0f} a head", sd + ra, fp, of, "60 months",
                        {"PAT positive only because of interest": "yes" if pat5 >= 0 and float((of['ebitda'] - of['depreciation'])[0, 48:60].sum()) < 0 else "",
                         "Largest round dilution (no cap applied)": maxdil, "Seed (Rs)": sd, "Series A at m18 (Rs)": ra}))
        print(f"  {name}: (a) {rows[-2].get('Feasible')} {rows[-2].get('Path', '')} | (b) {rows[-1]['Feasible']} PAT y5 {pat5 / CR:.2f} cr", flush=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    C.write("sat_sensitivity.csv", [{k: r.get(k, "") for k in cols} for r in rows])
    C.set_horizon(60)
    return rows


if __name__ == "__main__":
    main()

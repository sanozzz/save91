"""Is tables/base_city_plan.csv complete enough to drive the model (the Google Sheet's "City plan" tab)? Re-run the base fleet in
PLANNED mode from the file (saturation.py's reader; each city's own agents and attrition) and compare the volumes with the AUTO run
that wrote it. The NBFC layer does not change volumes, so the operating model is compared directly.

Writes tables/base_city_plan_check.csv.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import realworld as RWm            # noqa: E402
import saturation as S             # noqa: E402
import unicorn_plan as U           # noqa: E402

BASE_PATH = (300, 150, 5000, 25000.0)
REQUIRED = ("City", "Rank", "Addressable (urban self-employed)", "Launch month", "Agents in the launch month",
            *[f"Agents at launch +{o} months" for o in S.OFFSETS if o])


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, sh = S.city_curve()
    addr = sh[:S.CLASS_I] * S.POOL
    C.set_horizon(96)
    a18, h, cap, X = BASE_PATH
    sat = RWm.rw_cfg(addr, X)
    oa, _ = S.run(x, dists, sat, target_fn=U.path_fn(a18, h, cap))
    plan = S.read_plan(C.T / "base_city_plan.csv")
    missing = [c for c in REQUIRED if c not in plan[0]]
    blanks = sum(1 for r in plan for c in REQUIRED if c in r and str(r[c]).strip() == "")
    opened = int((oa["_city"][0]["agents"].max(axis=1) > 0).sum())
    tg, launch = S.plan_targets(plan, S.CLASS_I)
    op_, _ = S.run(x, dists, {**sat, "launch": launch}, fleet=C.make_city_fleet(dists, tg))
    rows = [{"Measure": "Columns the City plan tab needs, present", "AUTO": "", "PLANNED (from base_city_plan.csv)": "",
             "Gap (share)": "", "Within 1%": "yes" if not missing else "no: missing " + ", ".join(missing)},
            {"Measure": "Blank cells in those columns", "AUTO": "", "PLANNED (from base_city_plan.csv)": blanks, "Gap (share)": "", "Within 1%": "yes" if blanks == 0 else "no"},
            {"Measure": "Cities in the plan / cities the AUTO run opened", "AUTO": opened, "PLANNED (from base_city_plan.csv)": len(plan),
             "Gap (share)": len(plan) / opened - 1, "Within 1%": "yes" if len(plan) == opened else "no"}]
    for nm, k, f in (("Cumulative sign-ups to m60", "signups", lambda a: float(a[0, :60].sum())), ("Active savers at m60", "still_saving", lambda a: float(a[0, 59])),
                     ("AUM at m60", "fund_end", lambda a: float(a[0, 59])), ("Agents at m60", "agents", lambda a: float(a[0, 59])),
                     ("Revenue before the NBFC, years 1-5", "revenue", lambda a: float(a[0, :60].sum())),
                     ("Revenue before the NBFC, years 1-8", "revenue", lambda a: float(a[0].sum()))):
        va, vp = f(oa[k]), f(op_[k])
        rows.append({"Measure": nm, "AUTO": va, "PLANNED (from base_city_plan.csv)": vp, "Gap (share)": vp / va - 1, "Within 1%": "yes" if abs(vp / va - 1) <= 0.01 else "no"})
    C.write("base_city_plan_check.csv", rows)
    C.set_horizon(60)
    for r in rows:
        print("  ", r["Measure"], r["Gap (share)"], r["Within 1%"])
    return rows


if __name__ == "__main__":
    main()

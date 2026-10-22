"""Sign-ups target sweep: every input drawn from the agreed distributions, sign-ups a month (once up to speed) fixed at each target.
Writes tables/cohort_signups_sweep.csv (Monte Carlo) and tables/cohort_signups_sweep_likely.csv (all else at likely values)."""
import sys, time, csv
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "model"))
import cohort_engine as E
import cohort_mc as M

N = 2000
TARGETS = [40, 60, 80, 100, 120, 150]
t0 = time.time()
base, _ = M.sample(N, seed=M.SEED)
rows = []
for s in TARGETS:
    x = {k: v.copy() for k, v in base.items()}
    x["signups_run"] = np.full(N, float(s))
    o = M.simulate(x)
    c60, c36, pb, pk = o["cum_pnl60"], o["cum_pnl36"], o["payback_month"], o["peak_cash_need"]
    rows.append({"signups_a_month": s, "salary_per_signup": 240000 / (12 * s),
                 "p_cum60_pos": float((c60 > 0).mean()), "p_cum36_pos": float((c36 > 0).mean()),
                 "cum60_p10": float(np.percentile(c60, 10)), "cum60_p50": float(np.percentile(c60, 50)), "cum60_p90": float(np.percentile(c60, 90)),
                 "cum36_p50": float(np.percentile(c36, 50)),
                 "payback_p50": float(np.nanpercentile(pb, 50)) if np.isfinite(pb).any() else None,
                 "never_pays_back_60": float(np.isnan(pb).mean()),
                 "peak_cash_need_p50": float(np.percentile(pk, 50)),
                 "visits_peak_p50": float(np.percentile(o["visits_peak"], 50))})
    print(s, round(time.time() - t0), "s", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
with (R / "tables" / "cohort_signups_sweep.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
# all else at likely values: the break-even sign-ups for cumulative P&L at 36 and 60 months
xl = E.likely_inputs()
lik = []
for s in range(20, 161, 10):
    x = {k: np.atleast_1d(np.asarray(v, float)) for k, v in xl.items()}
    x["signups_run"] = np.array([float(s)])
    o = E.run(x)["out"]
    lik.append({"signups_a_month": s, "cum_pnl36": float(o["cum_pnl36"][0]), "cum_pnl60": float(o["cum_pnl60"][0]),
                "payback_month": float(o["payback_month"][0]), "peak_cash_need": float(o["peak_cash_need"][0]),
                "visits_peak": float(o["visits_peak"][0])})
with (R / "tables" / "cohort_signups_sweep_likely.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(lik[0])); w.writeheader(); w.writerows(lik)
for r in lik:
    print("likely", r["signups_a_month"], {k: (round(v) if v == v else None) for k, v in r.items() if k != "signups_a_month"})
print("done", round(time.time() - t0), "s")

"""Agent pay: Rs 20,000 salary + a share of his savers' balance (operator, 16 Oct 2026: "salary plus 0.25% of balance initially.
Afterwards when balances and customers are with us and growth isnt a problem, i can have less incentive").
Incentive = rate a year x average balance his savers hold that month / 12, on top of salary. Every other input drawn from
tables/dist_agreed_v1.csv (sign-ups 20/30/45). Writes tables/cohort_incentive_sweep.csv and cohort_incentive_likely.csv."""
import csv, sys, time
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "model"))
import cohort_engine as E
import cohort_mc as M

N, CH = 3000, 250
PAYS = [("salary only", 0.0, 0, 0.0, None), ("+0.25% of balance, capped at Rs 10,000 a month (base)", 0.0025, 60, 0.0025, 10000.0),
        ("+0.25% of balance, all 5 years, uncapped", 0.0025, 60, 0.0025, None),
        ("+0.25% for 2 years, then 0.10%", 0.0025, 24, 0.0010, None), ("+0.25% for 1 year, then 0.10%", 0.0025, 12, 0.0010, None),
        ("+0.25% for 2 years, then 0%", 0.0025, 24, 0.0, None)]


def rates(r1, months1, r2):
    t = np.arange(1, 61)
    return np.where(t <= months1, r1, r2)


def runs(x):
    n = len(x["r12"])
    bal, net = np.empty((n, 60)), np.empty((n, 60))
    for s in range(0, n, CH):
        m = E.run({k: v[s:s + CH] for k, v in x.items()})["monthly"]
        bal[s:s + CH] = m["balance"]
        net[s:s + CH] = m["net"] + m.get("cost_incentive", 0.0)   # the engine already pays 0.25% (round 7): add it back, then apply each pay option
    return bal, net


def summarise(name, bal, net, r, cap=None):
    inc = bal * r[None, :] / 12
    if cap is not None:
        inc = np.minimum(inc, cap)
    cum = np.cumsum(net - inc, axis=1)
    pos = cum >= 0
    stays = np.flip(np.logical_and.accumulate(np.flip(pos, axis=1), axis=1), axis=1)
    pb = np.where(stays.any(axis=1), stays.argmax(axis=1) + 1.0, np.nan)
    return {"pay": name, "p_cum60_pos": float((cum[:, 59] > 0).mean()), "p_cum36_pos": float((cum[:, 35] > 0).mean()),
            "cum60_p10": float(np.percentile(cum[:, 59], 10)), "cum60_p50": float(np.percentile(cum[:, 59], 50)),
            "cum60_p90": float(np.percentile(cum[:, 59], 90)), "cum36_p50": float(np.percentile(cum[:, 35], 50)),
            "payback_p50": float(np.nanmedian(pb)) if np.isfinite(pb).any() else None, "never_pays_back_60": float(np.isnan(pb).mean()),
            "peak_cash_need_p50": float(np.percentile(np.minimum(0, cum.min(axis=1)), 50)),
            "incentive_m12_p50": float(np.median(inc[:, 11])), "incentive_m24_p50": float(np.median(inc[:, 23])),
            "incentive_m60_p50": float(np.median(inc[:, 59])), "incentive_total60_p50": float(np.median(inc.sum(axis=1)))}


t0 = time.time()
x, _ = M.sample(N, seed=M.SEED)
bal, net = runs(x)
rows = [summarise(n, bal, net, rates(a, b, c), cap) for n, a, b, c, cap in PAYS]
xl = {k: np.atleast_1d(np.asarray(v, float)) for k, v in E.likely_inputs().items()}
lb, ln = runs(xl)
lik = [summarise(n, lb, ln, rates(a, b, c), cap) for n, a, b, c, cap in PAYS]
for name, data in (("cohort_incentive_sweep.csv", rows), ("cohort_incentive_likely.csv", lik)):
    with (R / "tables" / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
for r in rows:
    print("MC   ", {k: (round(v, 3) if isinstance(v, float) and abs(v) < 10 else (round(v) if isinstance(v, float) else v)) for k, v in r.items()})
for r in lik:
    print("LIKELY", {k: (round(v) if isinstance(v, float) and abs(v) >= 10 else v) for k, v in r.items()})
print(round(time.time() - t0), "s")

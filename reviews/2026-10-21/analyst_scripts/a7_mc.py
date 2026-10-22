import numpy as np, time, ltv_book as lb, online_plan as op, online_mc as om, cohort_mc as MC
from scipy import stats
xm = om.sample()
def pert_cdf(x, lo, li, hi):
    a, b = 1 + 4*(li-lo)/(hi-lo), 1 + 4*(hi-li)/(hi-lo)
    return np.clip(stats.beta.cdf((x-lo)/(hi-lo), a, b), 1e-9, 1-1e-9)
NEW = {"on_apply": (0.02, 0.10, 0.35), "on_ticket": (18800, 58522, 150000), "on_reach": (1.0, 1.5, 2.5),
       "on_r12": (0.24, 0.30, 0.45), "on_r3": (0.52, 0.70, 0.85), "on_approved": (0.11, 0.25, 0.35),
       "on_fee": (0.01, 0.015, 0.025), "cac": (300, 600, 800)}
def remap(keys):
    x = {k: v.copy() for k, v in xm.items()}
    for k in keys:
        _, lo, li, hi = om.ONLINE[k][:4]
        u = pert_cdf(x[k], lo, li, hi)
        x[k] = MC.ppf("pert", *NEW[k], u)
    bad = x["on_r12"] >= x["on_r3"]; x["on_r12"][bad] = x["on_r3"][bad] - 0.05
    return x
def online(x, i, tech=1.0):
    pp = {k: float(x[k][i]) for k in lb.ALLSPEC}
    lb.apply_params(pp); op.TECH_PER_SAVER = tech
    d = op.ltv_parts(op.saver_inputs(), pp["on_reach"])
    lt = d["income"][:60].sum() - d["serving"][:60].sum()
    op.TECH_PER_SAVER = 1.0; lb.reset()
    return lt / pp["cac"]
def summ(name, x, tech=1.0, n=1000):
    t = time.time(); r = np.array([online(x, i, tech) for i in range(n)])
    print(f"{name:<58} P10 {np.percentile(r,10):.2f} P50 {np.median(r):.2f} P90 {np.percentile(r,90):.2f}  >=3x {np.mean(r>=3):.0%}  <1x {np.mean(r<1):.0%}  ({time.time()-t:.0f}s)")
summ("published ranges (check: should be 2.58 / 3.79 / 5.69, 77%)", xm)
summ("published ranges + tech Rs4 + Rs2 x 20 debits", xm, tech=44.0)
summ("re-centred on folder evidence: all 8 big inputs", remap(list(NEW)))
summ("re-centred: loan funnel only (apply, ticket, reach, approval, fee)", remap(["on_apply","on_ticket","on_reach","on_approved","on_fee"]))
summ("re-centred: retention + CAC only", remap(["on_r12","on_r3","cac"]))

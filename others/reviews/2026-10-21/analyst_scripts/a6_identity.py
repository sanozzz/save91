import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad/analyst")
from a4_costs import run, p
import numpy as np, ltv_book as lb
# CAC = s*(100 + 0.5*40) at the seed's own cost per sign-up -> reach = 0.5*s
for cac in (300.0, 450.0, 600.0):
    s = cac/120.0; p(f"CAC {cac:.0f} via conversion: {s:.2f} sign-ups/saver -> reach {0.5*s:.3f}", run(cac=cac, reach=0.5*s))
# copula inertness: loss has no revenue effect
base = lb.base_params()
for L in (0.015, 0.05):
    on, dr, _ = lb.evaluate({**base, "loss": L}, door_cac=False); print("loss", L, "online LTV/CAC", round(on["ltvcac"],6), "door", round(dr["ltvcac"],6))
on, dr, _ = lb.evaluate({**base, "approved_first": 0.2}, door_cac=False); print("approved_first (agreed street key) 0.20 -> online", round(on["ltvcac"],6), "door", round(dr["ltvcac"],6))
# MC draws: correlations and shares
import csv
rows = list(csv.DictReader(open("tables/ltv_mc_draws.csv")))
v = lambda k: np.array([float(r[k]) for r in rows])
print("share apply<20%:", (v("on_apply")<0.20).mean(), " apply<10.5%:", (v("on_apply")<0.105).mean(), " ticket<58.5k:", (v("on_ticket")<58522).mean(), " reach<1.5:", (v("on_reach")<1.5).mean(), " r12<0.30:", (v("on_r12")<0.30).mean())
print("mean daily", v("on_daily").mean(), "mean apply", v("on_apply").mean(), "mean reach", v("on_reach").mean(), "mean ticket", v("on_ticket").mean(), "mean r12", v("on_r12").mean())
from scipy import stats
for a,b in (("on_apply","on_ticket"),("on_apply","on_approved"),("cac","on_reach"),("on_apply","on_r12")):
    print("spearman", a, b, round(stats.spearmanr(v(a), v(b)).statistic,3))
ltv = v("on_ltv60"); co = v("co_profit"); mon = v("co_money")
print("LTV<3 share", (ltv<3).mean(), "median profit month | <3", np.median(co[ltv<3]), "money", np.median(mon[ltv<3]), "| >=3", np.median(co[ltv>=3]), np.median(mon[ltv>=3]))
print("co profit >60 share", (co>60).mean(), "never by 96", (co>96).mean())

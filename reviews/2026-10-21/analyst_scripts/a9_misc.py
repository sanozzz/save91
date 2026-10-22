import numpy as np, online_plan as op, ltv_book as lb, online_mc as om, cohort_engine as ce
x = op.saver_inputs(); p = op.profiles(x)
s = p["still_saving"][0]; fe = p["fund_end"][0]/np.where(s>0, s, 1)  # per active saver end balance
stopped = np.r_[0, s[:-1]-s[1:]]
rm = (1+x["fund_return"])**(1/12)-1
for red in (0.0, 0.02, 0.05):
    D = np.zeros(op.M); 
    for a in range(1, op.M):
        D[a] = D[a-1]*(1+rm)*(1-red) + stopped[a]*fe[a-1]
    tr = D*x["trail"]/12
    print(f"trail on stopped savers' balances, redemption {red:.0%}/month: +Rs{tr[:60].sum():.0f} over 5y -> LTV/CAC {(1845.3+tr[:60].sum())/450:.2f}x")
# A6 line definitions vs LTV waterfall
o = op.company(20000)
y5 = slice(48, 60); ol = sum(o["rev"]["Other products"][y5].sum() for _ in [0])
otherloans = None
print("A6 Y5 'Loan fees' cr", round(o["rev"]["Loan marketing fees"][y5].sum()/op.CR,2), "'Other products' cr", round(o["rev"]["Other products"][y5].sum()/op.CR,2), "revenue", round(o["revenue"][y5].sum()/op.CR,2))
# median vs plan: each online key at its PERT median, one at a time
from scipy import stats
base = lb.base_params(); b = lb.evaluate(base, door_cac=False)[0]["ltvcac"]
for k, v in om.ONLINE.items():
    sh, lo, li, hi = v[:4]; a_, b_ = 1+4*(li-lo)/(hi-lo), 1+4*(hi-li)/(hi-lo)
    med = lo + (hi-lo)*stats.beta.median(a_, b_)
    pp = {**base, k: med}
    if k == "on_r12" and pp["on_r12"] >= pp["on_r3"]: pass
    r = lb.evaluate(pp, door_cac=False)[0]["ltvcac"]
    print(f"{k:<12} likely {li:<8g} median {med:10.4g}  LTV/CAC {r:.3f} ({r-b:+.3f})")
for k in ("churn_late","takeup_growth","withdraw_m","support_cost","early_takeup_mult"):
    sh, lo, li, hi = lb.ALLSPEC[k]; a_, b_ = 1+4*(li-lo)/(hi-lo), 1+4*(hi-li)/(hi-lo)
    med = lo + (hi-lo)*stats.beta.median(a_, b_); r = lb.evaluate({**base, k: med}, door_cac=False)[0]["ltvcac"]
    print(f"{k:<12} likely {li:<8g} median {med:10.4g}  LTV/CAC {r:.3f} ({r-b:+.3f})")

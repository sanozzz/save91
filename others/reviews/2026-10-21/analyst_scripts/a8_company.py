import numpy as np, online_plan as op, ltv_book as lb, online_mc as om
def recompute(o, d_rev=None, d_cost=None):
    rev = o["revenue"] + (0 if d_rev is None else d_rev); e = o["ebitda"] + (0 if d_rev is None else d_rev) - (0 if d_cost is None else d_cost)
    tax, carry = np.zeros(op.M), 0.0
    for i in range(op.M):
        carry += e[i]
        if carry > 0 and e[i] > 0: tax[i] = 0.25*min(e[i], carry)
    rec = np.r_[np.zeros(2), rev[:-2]]; cf = e - tax - rev + rec
    return op.positive_from(e) or 97, (max(0, -np.cumsum(cf).min()) + 5*op.CR)/op.FX/1e6, e[48:60].sum()/op.CR
t = np.arange(1, op.M+1); fm = 1 + 0.5*np.minimum(t-1, 59)/59
o = op.company(20000); print("plan", recompute(o))
lmf = o["rev"]["Loan marketing fees"]; noramp = lmf/fm - lmf
print("fee ramp off (flat 2%)", recompute(o, d_rev=noramp))
op.OV.update({"takeup_growth":0.0, "approval_growth":0.0}); op._CACHE.clear()
o2 = op.company(20000); print("takeup+approval growth off", recompute(o2))
lmf2 = o2["rev"]["Loan marketing fees"]; print("growth off + ramp off", recompute(o2, d_rev=lmf2/fm - lmf2))
op.OV.clear(); op._CACHE.clear()
# team x2 after the seed (people cost double from month 19), with contingency
people_extra = np.where(t > op.SEED_END, o["people"], 0) * 1.1
print("team cost x2 after the round", recompute(o, d_cost=people_extra))
# seed-phase spend, months 1-18
cf = o["cash_flow"]; print("cum cash month 18 (Rs cr)", round(np.cumsum(cf)[17]/op.CR, 2), "= $M", round(-np.cumsum(cf)[17]/op.FX/1e6, 3))
print("opex+acq months 1-18 $M", round((o["acquisition"][:18].sum()+o["opex"][:18].sum())/op.FX/1e6, 3), "revenue m1-18 Rs cr", round(o["revenue"][:18].sum()/op.CR,3))
print("active savers month 18", round(o["active"][17]), "online won m4-18", round(o["online_won"][:18].sum()), "door won", round(o["door_won"][:18].sum()))
print("deepest hole month", int(np.argmin(np.cumsum(cf)))+1, "first month cash flow >0:", int(np.argmax(cf>0))+1)
# non-saver serving at company level: 1.5 x active x Rs6 x 1.1
print("non-saver serving 1.5 x Rs6", recompute(o, d_cost=1.5*o["active"]*6*1.1))
# heads and people at m60
print("heads m60", o["heads"][59], "people Y5 Rs cr", round(o["people"][48:60].sum()/op.CR,2), "revenue Y5", round(o["revenue"][48:60].sum()/op.CR,2))

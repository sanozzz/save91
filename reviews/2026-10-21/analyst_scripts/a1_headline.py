import numpy as np, ltv_book as lb, online_plan as op
base = lb.base_params()
on, dr, dc = lb.evaluate(base, door_cac=False)
print("online LTV/CAC 5y", round(on["ltvcac"],3), "8y", round(on["ltvcac96"],3), "pay", on["pay"], "LTV", round(on["ltv"],1), "rev", round(on["rev"],1))
for k in ("fund","pb","ol","ins","cards","oth","serve"): print("  on",k, round(on[k],1))
print("door LTV/CAC 5y", round(dr["ltvcac"],3), "pay", dr["pay"], "cac", round(dc,1), "LTV", round(dr["ltv"],1))
for k in ("fund","pb","ol","ins","cards","oth","serve"): print("  dr",k, round(dr[k],1))
print("s12 on", on["s12"], "door", dr["s12"])
o = op.company(20000)
print("profit month", op.positive_from(o["ebitda"]), "money $M", o["money_needed"]/op.FX/1e6)
print("Y5 EBITDA cr", o["ebitda"][48:60].sum()/op.CR, "Y8", o["ebitda"][84:96].sum()/op.CR)
cum = np.cumsum(o["cash_flow"]); print("deepest hole month", int(np.argmin(cum))+1, cum.min()/op.CR)
# ltv_view check
d,c,v = op.ltv_view(op.saver_inputs(), op.CAC); print(v)

import numpy as np, online_plan as op
x = op.saver_inputs(); d = op.ltv_parts(x); p = d["_p"]
cdv = sum(p[f"rev_xs_{q}"][0][:60].sum() for q in ("loan_cd","loan_vehicle"))
gold = p["rev_xs_loan_gold"][0][:60].sum()
print("cd+vehicle per saver (x1)", round(cdv,1), "x2.5", round(cdv*2.5,1), "-> removing the 1.5 extra:", round(1845.3-1.5*cdv,0), round((1845.3-1.5*cdv)/450,2))
print("gold per saver x2.5", round(gold*2.5,1), "; at 70% approval:", round((1845.3-0.3*gold*2.5)/450,2))
print("both", round((1845.3-1.5*cdv-0.3*gold*2.5)/450,2))
# doorstep CAC incl contingency
print("doorstep LTV/CAC at 404*1.1:", round(1549.7/(404.2*1.1),2))

import numpy as np, online_plan as op
o = op.company(20000)
lent = o["lent"]  # personal+business money lent (first+repeat), incl. reach multiplier
print("P+B disbursals Y5 Rs cr", round(lent[48:60].sum()/op.CR,1), " trailing-18m at m60 Rs cr", round(lent[42:60].sum()/op.CR,1))
print("5% DLG on trailing 18m disbursals at m60: Rs cr", round(0.05*lent[42:60].sum()/op.CR,1), "= $M", round(0.05*lent[42:60].sum()/op.FX/1e6,2))
print("3% a year of money lent paid out under a DLG (TC-41) in Y5: Rs cr", round(0.03*lent[48:60].sum()/op.CR,1))
print("Y5 personal+business payout revenue Rs cr", round(o["rev"]["Loan marketing fees"][48:60].sum()/op.CR,2))

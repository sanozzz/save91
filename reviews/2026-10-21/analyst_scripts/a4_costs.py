import numpy as np, online_plan as op
def run(ov=None, tech=1.0, cac=450.0, reach=None, gst=1.0, level=20000):
    op.OV.clear(); op._CACHE.clear(); op.OV.update(ov or {})
    if reach is not None: op.OV["_loan_reach"] = reach
    op.TECH_PER_SAVER = tech
    d = op.ltv_parts(op.saver_inputs())
    inc = d["income"]/gst; sv = d["serving"]
    lt = inc[:60].sum() - sv[:60].sum(); cum = np.cumsum(inc - sv) - cac
    pay = int(np.argmax(cum >= 0)) + 1 if (cum >= 0).any() else 97
    o = op.company(level, 1.0, cac=cac)
    if gst != 1.0:   # revenue net of GST: recompute EBITDA, tax, cash
        rev = o["revenue"]; e = o["ebitda"] - rev*(1-1/gst)
        tax, carry = np.zeros(op.M), 0.0
        for i in range(op.M):
            carry += e[i]
            if carry > 0 and e[i] > 0: tax[i] = 0.25*min(e[i], carry)
        r2 = rev/gst; rec = np.r_[np.zeros(2), r2[:-2]]
        cf = e - tax - r2 + rec; need = max(0, -np.cumsum(cf).min()) + 5*op.CR
        pm = op.positive_from(e); y5 = e[48:60].sum()/op.CR
    else:
        pm = op.positive_from(o["ebitda"]); need = o["money_needed"]; y5 = o["ebitda"][48:60].sum()/op.CR
    op.OV.clear(); op._CACHE.clear(); op.TECH_PER_SAVER = 1.0
    return lt/cac, pay, pm or 97, need/op.FX/1e6, y5
def p(name, r): print(f"{name:<66} {r[0]:5.2f}x pay {r[1]:>3}  | co profit m{r[2]:>3}  need ${r[3]:5.2f}M  Y5 EBITDA {r[4]:6.1f} cr")
p("plan", run())
p("tech Rs4 (folder's 2 Oct base) instead of Rs1", run(tech=4))
for cd in (0.5, 2.0, 5.9):
    p(f"tech Rs4 + 20 daily debits at Rs{cd}", run(tech=4+20*cd))
p("tech Rs4 + weekly debits (4/month) at Rs2", run(tech=4+4*2))
p("revenue net of 18% GST (if payouts are GST-inclusive)", run(gst=1.18))
EV = {"apply3.6%": op.loan_mix(0.036), "apply 10%": op.loan_mix(0.10)}
p("apply 3.6% a year", run(op.loan_mix(0.036)))
p("ticket Rs25,000 (founder's own Rs10-25k; XL-42 Rs25.6k)", run({"ticket":25000.0}))
p("ticket Rs58,522 (XL-29 bureau average)", run({"ticket":58522.0}))
p("first approval 25% (founder's past lending, XF-24)", run({"approved_first":0.25}))
p("r12 24% + r3 52% (savings apps)", run({"r12":0.2415,"r3":0.52}))
p("reach 1.0 (savers only)", run(reach=1.0))
p("DSA payout 1.5% (mid of XF-01 1-2.5%... and lsp_fee base 1.5%)", run({"fee":0.015}))

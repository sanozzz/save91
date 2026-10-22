import numpy as np, ltv_book as lb, online_plan as op, cohort_engine as ce
base = lb.base_params()
def ltv(over=None, cac=None, door=False, extra_ov=None):
    pp = {**base, **(over or {})}
    if cac is not None: pp["cac"] = cac
    lb.apply_params(pp)
    if extra_ov: op.OV.update(extra_ov); op._CACHE.clear()
    d = op.ltv_parts(op.saver_inputs(), pp["on_reach"])
    inc, sv = d["income"], d["serving"]
    lt = inc[:60].sum() - sv[:60].sum()
    cum = np.cumsum(inc - sv) - pp["cac"]
    pay = int(np.argmax(cum >= 0)) + 1 if (cum >= 0).any() else 97
    out = dict(ltv=lt, ratio=lt/pp["cac"], pay=pay, loans=d["Loans (all referrals)"][:60].sum(), fund=d["Fund fees"][:60].sum(), sv=sv[:60].sum(), s=d["_p"]["still_saving"][0][:60].sum())
    lb.reset(); return out
def show(name, r): print(f"{name:<60} LTV {r['ltv']:7.0f}  LTV/CAC {r['ratio']:.2f}x  pay {r['pay']}")
b = ltv(); show("base", b)
print("sum of still-saving months (60m):", round(b["s"],2), "serving", round(b["sv"],1))
# 1 contingency-consistent CAC
show("CAC 495 (company model pays 450 x 1.1)", ltv(cac=495))
# 2 serving for 1.5 non-saver KYC'd users at same Rs6/month while reachable
r = ltv(); ns = 1.5*r["sv"]; print(f"{'non-saver serving 1.5x6/m':<60} LTV {r['ltv']-ns:7.0f}  LTV/CAC {(r['ltv']-ns)/450:.2f}x")
print(f"{'both of the above':<60} LTV/CAC {(r['ltv']-ns)/495:.2f}x")
# 3 product proposition: offers after 6 months of saving, savers only
show("offers from age 7, all products (marketplace_from=7)", ltv(extra_ov={"marketplace_from":7}))
show("offers from age 7 + savers only (reach 1)", ltv({"on_reach":1.0}, extra_ov={"marketplace_from":7}))
# 4 growth factors off / fee ramp off
show("takeup_growth=0, approval_growth=0", ltv({"takeup_growth":0.0,"approval_growth":0.0}))

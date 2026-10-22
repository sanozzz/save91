import numpy as np, online_plan as op
def recompute(o, d_cost):
    e = o["ebitda"] - d_cost; rev = o["revenue"]
    tax, carry = np.zeros(op.M), 0.0
    for i in range(op.M):
        carry += e[i]
        if carry > 0 and e[i] > 0: tax[i] = 0.25*min(e[i], carry)
    rec = np.r_[np.zeros(2), rev[:-2]]; cf = e - tax - rev + rec
    return op.positive_from(e) or 97, (max(0, -np.cumsum(cf).min()) + 5*op.CR)/op.FX/1e6, e[48:60].sum()/op.CR
def stack(name, saver_extra, nonsaver, ov=None, reach=None):
    op.OV.clear(); op._CACHE.clear(); op.OV.update(ov or {})
    if reach is not None: op.OV["_loan_reach"] = reach
    rch = op.OV.get("_loan_reach", op.LOAN_REACH)
    d = op.ltv_parts(op.saver_inputs()); s = d["_p"]["still_saving"][0][:60].sum()
    ltv = d["income"][:60].sum() - d["serving"][:60].sum() - s*saver_extra - (rch-1)*s*nonsaver
    o = op.company(20000)
    extra = o["active"]*saver_extra*1.1 + o["active"]*(rch-1)*nonsaver*1.1   # doorstep share small; applied to all active (slight overstatement)
    pm, need, y5 = recompute(o, extra)
    print(f"{name:<74} LTV {ltv:6.0f}  /450 {ltv/450:.2f}x  /495 {ltv/495:.2f}x | co m{pm} ${need:.2f}M Y5 {y5:.1f} cr")
    op.OV.clear(); op._CACHE.clear()
stack("A: tech Rs4 (folder base) + non-saver tech Rs4", 3, 4)
stack("B: A + weekly debits at Rs2 (Rs8/month)", 11, 4)
stack("B': A + daily debits at Rs0.5 (Rs10/month, the folder's 'must sign' price)", 13, 4)
stack("C: B + non-savers also cost support Rs5 (Rs9)", 11, 9)
stack("D: B + product as described (offers from age 7, savers only)", 11, 0, ov={"marketplace_from":7}, reach=1.0)

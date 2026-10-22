import numpy as np, ltv_book as lb, online_plan as op, cohort_engine as ce
def cohort_ltv(c, cac, reach=2.5, ramp=True, n=60):
    x = op.saver_inputs(); p = op.profiles(x)
    t = np.arange(c, c+op.M)  # calendar months for ages 1..
    fm = (1.0 + 0.5*np.minimum(t-1, 59)/59) if ramp else np.ones(op.M)
    i = c-1; L = op.M - i
    g = lambda k: p[k][i, :L]
    orig = g("rev_origination")*fm[:L]*reach
    xsl = sum(g(f"rev_xs_{q}") for q in op.LOAN_XS)*reach
    other = g("income") - g("rev_origination") - sum(g(f"rev_xs_{q}") for q in op.LOAN_XS)
    inc = orig + xsl + other
    serve = g("cost_support") + g("still_saving")*op.TECH_PER_SAVER
    nn = min(n, L)
    lt = inc[:nn].sum() - serve[:nn].sum()
    cum = np.cumsum(inc - serve) - cac
    pay = int(np.argmax(cum >= 0)) + 1 if (cum >= 0).any() else None
    return lt, lt/cac, pay, nn
for c, cac, lab in ((1,450,"month-1 joiner at 450 (the headline)"),(4,600,"first real cohort, month 4, seed CAC 600"),(12,600,"seed cohort month 12 at 600"),(19,450,"first post-seed cohort, month 19 at 450"),(31,450,"month-31 joiner at 450")):
    lt, r, pay, nn = cohort_ltv(c, cac)
    print(f"{lab:<48} LTV {lt:6.0f} LTV/CAC {r:.2f}x pay {pay} (horizon {nn})")
lt, r, pay, nn = cohort_ltv(1, 450, ramp=False); print(f"{'month-1, DSA payout flat 2% (no 1.5x ramp)':<48} LTV {lt:6.0f} LTV/CAC {r:.2f}x pay {pay}")
lt, r, pay, nn = cohort_ltv(19, 450, ramp=False); print(f"{'month-19, payout flat 2%':<48} LTV {lt:6.0f} LTV/CAC {r:.2f}x pay {pay}")
# fee ramp + growth both off for month-1 joiner
op.OV.update({"takeup_growth":0.0,"approval_growth":0.0}); op._CACHE.clear()
lt, r, pay, nn = cohort_ltv(1, 450, ramp=False); print(f"{'month-1: no ramp, no takeup/approval growth':<48} LTV {lt:6.0f} LTV/CAC {r:.2f}x pay {pay}")
op.OV.clear(); op._CACHE.clear()

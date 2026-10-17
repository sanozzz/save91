"""Numbers for checkpoint 1: both product designs x bear/base/bull, lending-first, tornado, what-has-to-be-true."""
import csv
import engine as E

DESIGNS = [(None, "Daily debit (as briefed)"), ("weekly_payday", "Weekly debit on payout day")]
rows = []
for var, label in DESIGNS:
    for s in E.SCENARIOS:
        p, cr, o, ch = E.run(s, variant=var)
        pr = E.path(p, o)
        rows.append({"design": label, "scenario": s, "cac": o["cac"], "payback": o["payback_months"] or "none in 60",
                     "ltv36": o["ltv36"], "ltv60": o["ltv60"], "ltv36_cac": o["ltv36_cac"], "ltv60_cac": o["ltv60_cac"],
                     **{f"rev_pa_y{y}": o[f"y{y}_rev_per_active"] for y in range(1, 6)},
                     **{f"cm_pa_y{y}": o[f"y{y}_cm_per_active"] for y in range(1, 6)},
                     "path_y10_usd_m": pr[-1]["rev_usd_m"], "path_y10_active_m": pr[-1]["active"] / 1e6,
                     "peak_capital_cr": max(0, -min(r["cum_cash"] for r in pr)) / 1e7})
for s in E.SCENARIOS:
    p = E.load_inputs(s)
    _, lo = E.lending_first(E.load_lf(s), p["disc_rate"])
    rows.append({"design": "Lending-first (Bueno as run)", "scenario": s, "cac": lo["cac"], "payback": lo["payback_months"] or "none in 60",
                 "ltv36": lo["ltv36"], "ltv60": lo["ltv60"], "ltv36_cac": lo["ltv36_cac"], "ltv60_cac": lo["ltv60_cac"]})
with open("../tables/checkpoint1.csv", "w", newline="") as f:
    keys = list(dict.fromkeys(k for r in rows for k in r))
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['design']:<30} {r['scenario']:<5} CAC {r['cac']:6.0f}  payback {str(r['payback']):>11}  LTV60 {r['ltv60']:7.0f}  LTV60/CAC {r['ltv60_cac']:5.2f}  "
          + ("rev/active " + "/".join(f"{r[f'rev_pa_y{y}']:.0f}" for y in range(1, 6)) + f"  cm/active y2 {r['cm_pa_y2']:.0f}  $M y10 {r['path_y10_usd_m']:.0f}  cap {r['peak_capital_cr']:.0f}cr" if 'rev_pa_y1' in r else ""))

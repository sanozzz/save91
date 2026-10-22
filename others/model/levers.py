"""Checkpoint 1b: test the four structural levers on the founder's chosen (daily) design.

Writes tables/levers_results.csv. Every lever is either a switch in tables/inputs.csv
(dlg_on, nbfc_on, gold_on) or a variant in tables/variants.csv (blue_collar).
Own NBFC starts in calendar year 3: cohort economics use nbfc_on=1, and the
10-year path switches to them from year 3 (with the Rs 10 crore minimum).
"""
import csv

import engine as E

OFF = {"dlg_on": 0, "nbfc_on": 0, "gold_on": 0}   # every row sets all three switches explicitly
LEVERS = [  # (label, overrides, variant, own-NBFC switch year); all rows use the 50/50 gig / non-gig mix unless stated
    ("As briefed (daily)", {**OFF}, None, None),
    ("A. Take 5% of loan losses", {**OFF, "dlg_on": 1}, None, None),
    ("B. Own NBFC from year 3", {**OFF, "nbfc_on": 1}, None, 3),
    ("C. Add digital gold", {**OFF, "gold_on": 1}, None, None),
    ("A + C (the plan)", {**OFF, "dlg_on": 1, "gold_on": 1}, None, None),
    ("B + C", {**OFF, "nbfc_on": 1, "gold_on": 1}, None, 3),
    ("A + C, gig only", {**OFF, "dlg_on": 1, "gold_on": 1, "mix_gig": 1.0}, None, None),
]


def has_variant(name):
    return any(r["variant"] == name for r in E._read("variants.csv"))


def evaluate(ov, variant, switch_year, s):
    p, rows, out, _ = E.run(s, ov, variant)
    if switch_year:
        # years before the switch run as a partner-lender (LSP) business
        pre_ov = {**ov, "nbfc_on": 0}
        p0, _, out0, _ = E.run(s, pre_ov, variant)
        pr = E.path(p0, out0, alt=(p, out), switch_year=switch_year)
    else:
        pr = E.path(p, out)
    first100 = next((r["year"] for r in pr if r["rev_usd_m"] >= 100), None)
    return {
        "cac": out["cac"], "payback": out["payback_months"], "ltv60": out["ltv60"], "ltv60_cac": out["ltv60_cac"],
        "rev_pa_y2": out["y2_rev_per_active"], "cm_pa_y2": out["y2_cm_per_active"],
        "capital_per_rev_y1": out["capital_per_rev"],
        "y10_usd_m": pr[-1]["rev_usd_m"], "y10_active_m": pr[-1]["active"] / 1e6,
        "first_year_100m": first100,
        "peak_capital_cr": max(0.0, -min(r["cum_cash"] for r in pr)) / 1e7,
    }


def main():
    out_rows = []
    for name, ov, variant, sy in LEVERS:
        if variant and not has_variant(variant):
            print(f"skip {name}: variant {variant} not defined yet")
            continue
        for s in E.SCENARIOS:
            r = {"lever": name, "scenario": s, **evaluate(ov, variant, sy, s)}
            out_rows.append(r)
    with open(E.TABLES / "levers_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"{'lever':<28} {'scen':<5} {'CAC':>5} {'payback':>8} {'LTV60/CAC':>9} {'rev/act y2':>10} {'cm/act y2':>9} {'Y10 $M':>7} {'$100M yr':>8} {'peak cap cr':>11}")
    for r in out_rows:
        print(f"{r['lever']:<28} {r['scenario']:<5} {r['cac']:5.0f} {str(r['payback']):>8} {r['ltv60_cac']:9.2f} {r['rev_pa_y2']:10.0f} {r['cm_pa_y2']:9.0f} "
              f"{r['y10_usd_m']:7.0f} {str(r['first_year_100m']):>8} {r['peak_capital_cr']:11.0f}")


if __name__ == "__main__":
    main()

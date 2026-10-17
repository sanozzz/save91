import engine as E
V = "weekly_payday"
print("Tornado, weekly design, LTV60/CAC (base = %.2f):" % E.run("base", variant=V)[2]["ltv60_cac"])
tor = E.tornado(variant=V)
for r in tor[:10]:
    print(f"  {r['input']:<16} bear {r['bear_value']:<8g} -> {r['metric_at_bear']:6.2f} | bull {r['bull_value']:<8g} -> {r['metric_at_bull']:6.2f} | swing {r['swing']:.2f}")
bull = E.load_inputs("bull", E.load_variant(V, "bull"))
print("\nTop-N inputs at bull, rest at base:")
for n in (3, 5, 7):
    ov = {r["input"]: bull[r["input"]] for r in tor[:n]}
    o = E.run("base", ov, V)[2]
    print(f"  top {n} ({', '.join(ov)}): LTV60/CAC {o['ltv60_cac']:.2f}  payback {o['payback_months']}  rev/active y2 {o['y2_rev_per_active']:.0f}")
print("\nSingle input needed for LTV60/CAC = 3 (all else base, weekly):")
extra = E.load_variant(V, "base")
base = E.load_inputs("base", extra)
for k, hi in [("loan_apply", 1.0), ("lsp_fee", 0.5), ("ins_uptake", 1.0), ("card_uptake", 1.0), ("card_fee", 50000),
              ("ret_m24", 0.99), ("cost_support", 0), ("cac_mult", 0), ("ins_premium", 100000), ("loan_eligible", 1.0)]:
    lo = 0.0
    x = E.solve_for(k, 3.0, scenario="base", lo=min(base[k], hi), hi=max(base[k], hi), extra=extra)
    print(f"  {k:<14} base {base[k]:<8g} needs {x if x is None else round(x, 4)}")

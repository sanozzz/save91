"""One customer, start to finish: what they are worth with EVERYTHING we could sell them, and when
we get back what it cost to win them.

Month by month for one customer won (a cohort divided by its size):
  savings revenue   gold margin, fund trail, FD fee (the model's own lines)
  cross-sell        every product in tables/crosssell_map.csv (loans, mutual funds and SIPs,
                    insurance, pension, cards, bills, recharge), per ACTIVE saver a year / 12,
                    from month 1. This REPLACES the model's own loan, card, SIP and insurance
                    lines so nothing is counted twice. Gross commission: the cost of selling is
                    not deducted (generous).
  cost to serve     debit fees, support and tech, fraud (the model's own lines)
Lifetime value (LTV) = discounted contribution over 5 years. Payback = the first month the
undiscounted running total covers the cost to win (CAC). The curve runs 10 years.

Check: with the model's own lines left in, LTV must equal the engine's ltv60 exactly.

Writes tables/ltv_cases.csv (one row per case) and tables/ltv_curve.csv (month by month).
"""
import csv

import numpy as np

import engine as E
import mc

T = E.TABLES
HORIZON = 120
MODEL_XS_REV = ("rev_loans", "rev_cards", "rev_sip", "rev_mf_incentive", "rev_insurance")
MODEL_XS_COST = ("cost_loans", "cost_cards", "cost_insurance")
SAVINGS_REV = ("rev_liquid", "rev_fd", "rev_gold")
SERVE_COST = ("cost_payments", "cost_service", "cost_fraud")


def xs_total(col):
    return next(float(r[col]) for r in csv.DictReader(open(T / "crosssell_map.csv")) if r["product"] == "TOTAL all cross-sell")


def evidence_overrides():
    c = mc.centre(mc.load_dists())
    o = mc.to_overrides({k: np.asarray([v]) for k, v in c.items()})
    return {k: float(np.ravel(v)[0]) for k, v in o.items()}


def customer(ov, xs_year=None):
    """xs_year None: keep the model's own cross-sell lines; a number: replace them with that many
    rupees per active saver a year."""
    E.MONTHS = HORIZON
    try:
        p, rows, out, _ = E.run("base", ov)
    finally:
        E.MONTHS = 60
    N = p["cohort_size"]
    dm = (1 + p["disc_rate"]) ** (1 / 12) - 1
    curve, cum = [], -out["cac"]
    parts = {"savings": 0.0, "cross_sell": 0.0, "serve": 0.0}
    payback = None
    for r in rows:
        t = r["month"]
        sav = sum(r[k] for k in SAVINGS_REV) / N
        if xs_year is None:
            xs = (sum(r[k] for k in MODEL_XS_REV) - sum(r[k] for k in MODEL_XS_COST)) / N
        else:
            xs = r["active"] / N * xs_year / 12
        serve = sum(r[k] for k in SERVE_COST) / N
        net = sav + xs - serve
        cum += net
        if payback is None and cum >= 0:
            payback = t
        if t <= 60:
            d = (1 + dm) ** t
            parts["savings"] += sav / d
            parts["cross_sell"] += xs / d
            parts["serve"] += serve / d
        curve.append({"month": t, "active": r["active"] / N, "monthly_net": net, "cum_net_undiscounted": cum})
    ltv = parts["savings"] + parts["cross_sell"] - parts["serve"]
    return {"cac": out["cac"], "ltv60": ltv, "engine_ltv60": out["ltv60"], "net60": ltv - out["cac"], "payback_month": payback or "",
            "savings_pv": parts["savings"], "cross_sell_pv": parts["cross_sell"], "serve_pv": parts["serve"],
            "cum_net_m120": cum, "active_m12": rows[11]["active"] / N}, curve


def main():
    ev = evidence_overrides()
    cases = {
        "plan_as_is": ({}, None),                              # the founder's plan, its own cross-sell lines
        "evidence_savings_only": (ev, 0.0),
        "evidence_everything_mid": (ev, xs_total("mid")),
        "evidence_everything_best": (ev, xs_total("high")),
        "plan_everything_mid": ({}, xs_total("mid")),
    }
    rows, curves = [], []
    for name, (ov, xs) in cases.items():
        res, cur = customer(ov, xs)
        if xs is None:
            assert abs(res["ltv60"] - res["engine_ltv60"]) < 1e-6, (name, res["ltv60"], res["engine_ltv60"])
        rows.append({"case": name, "cross_sell_per_active_year": "" if xs is None else xs, **res})
        curves += [{"case": name, **c} for c in cur]
        print(f"{name:<28} CAC {res['cac']:>6.0f}  LTV5y {res['ltv60']:>7.0f} (savings {res['savings_pv']:>5.0f} + cross-sell {res['cross_sell_pv']:>5.0f} - serve {res['serve_pv']:>5.0f})"
              f"  net {res['net60']:>7.0f}  payback {res['payback_month'] or 'never (10y)'}")
    # the engine check on the evidence middle with the model's own lines
    res, _ = customer(ev, None)
    assert abs(res["ltv60"] - res["engine_ltv60"]) < 1e-6
    rows.append({"case": "evidence_model_lines", "cross_sell_per_active_year": "", **res})
    print(f"{'evidence_model_lines':<28} CAC {res['cac']:>6.0f}  LTV5y {res['ltv60']:>7.0f}  cross-sell {res['cross_sell_pv']:.0f}  (engine check passed)")
    mc.write("ltv_cases.csv", rows)
    mc.write("ltv_curve.csv", curves)


if __name__ == "__main__":
    main()

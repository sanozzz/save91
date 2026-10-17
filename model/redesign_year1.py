"""Year-one view of the redesign target case (the money slide in the Save91 deck).

Same inputs as redesign_deck.py's target case (win for Rs 250, 1 in 5 proven savers take a
partner loan a year, proven savers keep borrowing, evidence middle for everything else).
Writes tables/redesign_year1.csv: per shop owner WON, the parts earned in months 1-12,
undiscounted (cash in year one), plus the 60-month discounted parts as a cross-check
against tables/redesign_deck.csv. Nothing else is changed.
"""
import csv

import numpy as np

import engine as E
import mc
import redesign as R

TARGET_CAC, TARGET_TAKEUP = 250.0, 0.20


def parts_by_window(ov, x, months, discount, graduate=True, seg="ng"):
    """R.customer's month loop, limited to `months` and optionally undiscounted."""
    o = R.design_overrides({**ov, "trail_liquid": x["fund_trail"]}, seg)
    p, rows, out, _ = E.run("base", o)
    N = p["cohort_size"]
    dm = (1 + p["disc_rate"]) ** (1 / 12) - 1
    per_loan = x["wc_ticket"] * x["wc_fee"] * (1 - x["wc_clawback"]) - p["loan_ops_cost"]
    parts = dict(savings=0.0, loans=0.0, other=0.0, serve=0.0, loans_taken=0.0)
    s6 = rows[R.LOAN_START - 1]["active"] / N
    for r in rows:
        t = r["month"]
        if t > months:
            break
        a = r["active"] / N
        pool = max(a, s6 * (1 - p["churn_late"]) ** (t - R.LOAN_START)) if (graduate and t >= R.LOAN_START) else a
        sav = (r["rev_liquid"] + r["rev_fd"] + r["rev_gold"]) / N
        inc = r["contributions"] / N * 0.01 * x["incentive_share"] if t <= 12 else 0.0
        nl = pool * x["wc_loans_year"] / 12 if t >= R.LOAN_START else 0.0
        other = a * x["xs_other"] / 12
        serve = (r["cost_payments"] + r["cost_service"] + r["cost_fraud"]) / N
        d = (1 + dm) ** t if discount else 1.0
        parts["savings"] += (sav + inc) / d
        parts["loans"] += nl * per_loan / d
        parts["other"] += other / d
        parts["serve"] += serve / d
        parts["loans_taken"] += nl
    still_m12 = rows[11]["active"] / N
    return parts, out["cac"], still_m12


def main():
    dists = mc.load_dists()
    med = {r["input"]: float(mc.ppf(r, 0.5)) for r in R.new_rows()}
    cen = {**mc.centre(dists), "cac_target@ng": TARGET_CAC}
    co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in cen.items()}).items()}
    x = {**med, "wc_loans_year": TARGET_TAKEUP}

    full = R.customer(co, x, graduate=True)
    p60, cac, _ = parts_by_window(co, x, 60, discount=True)
    net60 = p60["savings"] + p60["loans"] + p60["other"] - p60["serve"] - cac
    assert abs(net60 - full["net"]) < 0.01, (net60, full["net"])          # same engine, same answer

    deck = {r["metric"]: float(r["value"]) for r in csv.DictReader(open(E.TABLES / "redesign_deck.csv"))}
    assert abs(full["net"] - deck["target_net"]) < 0.5, (full["net"], deck["target_net"])

    y1, _, still = parts_by_window(co, x, 12, discount=False)
    contrib1 = y1["savings"] + y1["loans"] + y1["other"] - y1["serve"]
    out = [("y1_savings", y1["savings"]), ("y1_loans", y1["loans"]), ("y1_other", y1["other"]), ("y1_serve", y1["serve"]),
           ("y1_contribution", contrib1), ("y1_cac", cac), ("y1_cumulative_after_cac", contrib1 - cac),
           ("y1_loans_per_owner_won", y1["loans_taken"]), ("y1_still_saving_m12", still),
           ("check_net60_discounted", net60), ("check_target_net_in_deck", deck["target_net"])]
    mc.write("redesign_year1.csv", [{"metric": k, "value": v} for k, v in out])
    for k, v in out:
        print(f"{k:<28}{v:,.2f}")


if __name__ == "__main__":
    main()

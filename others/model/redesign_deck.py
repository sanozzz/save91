"""Numbers the redesign slides quote, computed once into tables (the deck recomputes nothing).

  tables/redesign_grid.csv   share of futures that pay back, by cost to win a shopkeeper (fixed)
                             x loans a year per proven saver (fixed); proven savers keep borrowing
  tables/redesign_deck.csv   the target case at the evidence middle (win for Rs 250, 1 in 5 borrow
                             a year, proven savers keep borrowing): waterfall parts and payback;
                             what one loan earns; what five years of one saver's savings earn
"""
import csv

import numpy as np

import engine as E
import mc
import redesign as R

T = E.TABLES
CACS = (150.0, 250.0, 400.0, 500.0)
TAKEUPS = (0.05, 0.10, 0.20, 0.30)
DRAWS = 2000
TARGET_CAC, TARGET_TAKEUP = 250.0, 0.20


def main():
    dists = mc.load_dists()
    base = mc.sample(dists, DRAWS, 0.0, np.random.default_rng(mc.SEED))
    newd = R.draw_new(np.random.default_rng(mc.SEED + 1), DRAWS)
    grid = []
    for cac in CACS:
        b = {**base, "cac_target@ng": np.full(DRAWS, cac)}
        ovs = mc.to_overrides(b)
        for lam in TAKEUPS:
            net = np.empty(DRAWS)
            for i in range(DRAWS):
                o = {k: float(np.ravel(v)[i]) if np.size(v) > 1 else float(np.ravel(v)[0]) for k, v in ovs.items()}
                x = {k: float(v[i]) for k, v in newd.items()}
                x["wc_loans_year"] = lam
                net[i] = R.customer(o, x, graduate=True)["net"]
            grid.append({"cac": cac, "loans_year": lam, "p_net_pos": float((net > 0).mean()), "net_p50": float(np.median(net))})
            print(f"cost to win {cac:>4.0f}, take-up {lam:.2f}: pays back in {grid[-1]['p_net_pos']:.0%} of futures")
    mc.write("redesign_grid.csv", grid)

    # the target case at the evidence middle
    med = {r["input"]: float(mc.ppf(r, 0.5)) for r in R.new_rows()}
    cen = {**mc.centre(dists), "cac_target@ng": TARGET_CAC}
    co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in cen.items()}).items()}
    c = R.customer(co, {**med, "wc_loans_year": TARGET_TAKEUP}, graduate=True)
    p = E.load_inputs("base", R.design_overrides(co), "ng")
    one_loan = med["wc_ticket"] * med["wc_fee"] * (1 - med["wc_clawback"]) - p["loan_ops_cost"]
    # five years of one saver who stays: the fund trail on their balance (undiscounted)
    pp, rows, _, _ = E.run("base", R.design_overrides({**co, "trail_liquid": med["fund_trail"]}))
    stayer_trail = sum(r["rev_liquid"] / r["active"] for r in rows if r["active"] > 0)
    out = [("target_cac", c["cac"]), ("target_savings", c["pv_savings"] + c["pv_incentive"]), ("target_loans", c["pv_loans"]),
           ("target_other", c["pv_other"]), ("target_serve", c["pv_serve"]), ("target_net", c["net"]), ("target_payback", c["payback"] or 0),
           ("target_loans_per_customer", c["loans_per_customer"]), ("one_loan", one_loan), ("loan_ticket_mid", med["wc_ticket"]),
           ("loan_fee_mid", med["wc_fee"]), ("stayer_trail_5y", stayer_trail), ("target_takeup", TARGET_TAKEUP)]
    mc.write("redesign_deck.csv", [{"metric": k, "value": v} for k, v in out])
    for k, v in out:
        print(f"{k:<28}{v:,.2f}")


if __name__ == "__main__":
    main()

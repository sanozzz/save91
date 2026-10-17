"""The flip: what MINIMUM amount per debit (multiples of Rs 50) makes one saver break even?

For each amount, every saver in both halves saves exactly that amount per successful debit
(a minimum treated as the amount, so savers who save more are not counted). Everything else is
held where it was, so the answer is MECHANICAL: it does not include the savers a higher minimum
would lose, the extra bounced debits, or the higher cost to win each saver. Those are reported
alongside as what the amount means against a worker's income.

Payment price: flat list price has a step (Rs 5.90 a debit up to Rs 1,000, Rs 17.70 above, incl.
GST; mc.flat_fee), or a percentage of the debit. The plan case keeps the plan's own Rs 2 a debit.

Writes:
  tables/flip_amount.csv     net value per saver by amount, per case
  tables/flip_breakeven.csv  the first Rs 50 step at which each case breaks even, and what that is a month
  tables/flip_mc.csv         Monte Carlo by amount (2,000 draws each, the same draws at every amount)
"""
import csv
import sys

import numpy as np

import engine as E
import mc

T = E.TABLES
STEP = 50
AMOUNTS = list(range(STEP, 8001, STEP))
MC_AMOUNTS = list(range(STEP, 1001, STEP)) + list(range(1250, 5001, 250))
MC_DRAWS = 2000
INCOME = {"gig": 18761.0, "ng": 23012.0}   # rider_net (INC-01, IDinsight 2024); se_urban_income (NG-005, PLFS 2025)


def with_amount(d, a, design="daily", wk=None):
    """Set the amount per successful debit. For the weekly design mc.to_overrides rescales the
    daily amount by daily/weekly successes, so feed it the daily equivalent of a weekly debit."""
    d = dict(d)
    for s in ("gig", "ng"):
        d[f"daily_amount@{s}"] = float(a) if design == "daily" else float(a) * wk / float(d[f"debits_success@{s}"])
    return d


def ev(d, design="daily"):
    o = mc.to_overrides({k: np.asarray([v]) for k, v in d.items()}, design)
    return mc.evaluate({k: float(np.ravel(v)[0]) for k, v in o.items()})


def corner(dists, base, a, design="daily", wk=None):
    """Best case AT THIS AMOUNT: every input at whichever of its 10th/90th percentile helps more,
    judged at this amount and pricing (the helpful direction of debit counts flips with the amount)."""
    c = with_amount(base, a, design, wk)
    fav = dict(c)
    for r in dists:
        k = mc.key(r)
        if r["dist"] == "bernoulli" or k.startswith("daily_amount") or (design == "weekly" and k == "wk_success"):
            continue
        lo, hi = float(mc.ppf(r, 0.1)), float(mc.ppf(r, 0.9))
        n_lo = ev(with_amount({**c, k: lo}, a, design, wk), design)["net"]
        n_hi = ev(with_amount({**c, k: hi}, a, design, wk), design)["net"]
        fav[k] = hi if n_hi >= n_lo else lo
    return with_amount(fav, a, design, wk)


def plan_net(a):
    p, rows, out, _ = E.run("base", {"daily_amount@gig": float(a), "daily_amount@ng": float(a)})
    return out["ltv60"] - out["cac"], out


def sweep(dists):
    c = mc.centre(dists)
    wk = float(c["wk_success"])
    base = {"flat_failed_free": {**c, "pay_flat": 1.0, "fail_billed": 0.0},
            "flat_failed_billed": {**c, "pay_flat": 1.0, "fail_billed": 1.0},
            "percent": {**c, "pay_flat": 0.0}}
    rows = []
    for a in AMOUNTS:
        for nm, b in base.items():
            r = ev(with_amount(b, a))
            rows.append({"case": f"evidence_{nm}", "design": "daily", "amount": a, "net": r["net"], "ltv60": r["ltv60"], "cac": r["cac"]})
        n, out = plan_net(a)
        rows.append({"case": "plan", "design": "daily", "amount": a, "net": n, "ltv60": out["ltv60"], "cac": out["cac"]})
        r = ev(with_amount(base["flat_failed_free"], a, "weekly", wk), "weekly")
        rows.append({"case": "evidence_flat_failed_free", "design": "weekly", "amount": a, "net": r["net"], "ltv60": r["ltv60"], "cac": r["cac"]})
        if a <= 3000 or a % 250 == 0:
            for nm in ("flat_failed_free", "percent"):
                r = ev(corner(dists, base[nm], a), "daily")
                rows.append({"case": f"best_case_{nm}", "design": "daily", "amount": a, "net": r["net"], "ltv60": r["ltv60"], "cac": r["cac"]})
    return rows, c, wk


def breakevens(rows, c, wk):
    succ = {s: float(c[f"debits_success@{s}"]) for s in ("gig", "ng")}
    plan_succ = {s: E.load_inputs("base", segment=s)["debits_success"] for s in ("gig", "ng")}
    be = []
    for case, design in sorted({(r["case"], r["design"]) for r in rows}):
        rs = sorted((r for r in rows if r["case"] == case and r["design"] == design), key=lambda r: r["amount"])
        hit = next((r["amount"] for r in rs if r["net"] >= 0), None)
        s = plan_succ if case == "plan" else succ
        per_month = {g: (hit * (wk if design == "weekly" else s[g]) if hit else None) for g in ("gig", "ng")}
        be.append({"case": case, "design": design, "breakeven_amount": hit or "",
                   "debits_gig": wk if design == "weekly" else s["gig"], "debits_ng": wk if design == "weekly" else s["ng"],
                   "monthly_gig": per_month["gig"] or "", "monthly_ng": per_month["ng"] or "",
                   "share_income_gig": per_month["gig"] / INCOME["gig"] if hit else "",
                   "share_income_ng": per_month["ng"] / INCOME["ng"] if hit else "",
                   "best_net_at_or_below_1000": max(r["net"] for r in rs if r["amount"] <= 1000),
                   "amount_of_best_at_or_below_1000": max((r for r in rs if r["amount"] <= 1000), key=lambda r: r["net"])["amount"]})
    return be


def monte_carlo(dists):
    rng = np.random.default_rng(mc.SEED)
    draws = mc.sample(dists, MC_DRAWS, 0.0, rng)
    flat = np.asarray(draws["pay_flat"])
    out = []
    for a in MC_AMOUNTS:
        dd = {**draws, "daily_amount@gig": np.full(MC_DRAWS, float(a)), "daily_amount@ng": np.full(MC_DRAWS, float(a))}
        ov = mc.to_overrides(dd)
        net = np.array([mc.evaluate({k: float(np.ravel(v)[i]) if np.size(v) > 1 else float(np.ravel(v)[0]) for k, v in ov.items()})["net"]
                        for i in range(MC_DRAWS)])
        out.append({"amount": a, "p_pos": float((net > 0).mean()), "p50": float(np.median(net)),
                    "p5": float(np.percentile(net, 5)), "p95": float(np.percentile(net, 95)),
                    "p_pos_flat": float((net[flat == 1] > 0).mean()), "p_pos_percent": float((net[flat == 0] > 0).mean()),
                    "p50_flat": float(np.median(net[flat == 1])), "p50_percent": float(np.median(net[flat == 0]))})
        print(f"Rs {a:>5}: P(profit) {out[-1]['p_pos']:.1%}  flat {out[-1]['p_pos_flat']:.1%}  percent {out[-1]['p_pos_percent']:.1%}  P50 {out[-1]['p50']:,.0f}", flush=True)
    mc.write("flip_mc.csv", out)


def main():
    dists = mc.load_dists()
    rows, c, wk = sweep(dists)
    mc.write("flip_amount.csv", rows)
    be = breakevens(rows, c, wk)
    mc.write("flip_breakeven.csv", be)
    for b in be:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in b.items()}, flush=True)
    if "--no-mc" not in sys.argv:
        monte_carlo(dists)


if __name__ == "__main__":
    main()

"""The redesign (operator, 2 Oct 2026): shopkeepers save daily into debt funds; the saving is the
filter, and the money is in Rs 1-2 lakh unsecured loans that partner lenders make to the good
savers. Same engine, same evidence ranges and same Monte Carlo as the original test.

Design (fixed):
  shopkeepers only (mix_gig 0)
  saving: daily SIPs into debt funds through the exchange MF platform. The fund house pays the
          platform, the distributor pays nothing per debit (XB-01), so debit, failure and notice
          costs are 0. No digital gold (gold_on 0) and no FDs (fd_share 0): we earn the
          distributor trail on the fund balance.
  the model's own small secured loans, FD card, SIP and insurance lines are switched off and
  replaced by: (a) the unsecured-loan engine below, (b) everything else from the cross-sell map
  (non-loan products plus gold, home, vehicle, phone and card loans).
Unsecured loans (from month 6, active savers only):
  loans a year per active saver x ticket x referral fee x (1 - clawback) - ops cost per loan.
  Lenders underwrite and carry the credit risk (XB-06); we earn a referral fee (XL rows) that is
  clawed back on early defaults (XB-07, XL-13).
SEBI new-investor bonus: 1% of first-year SIPs for the share of savers who qualify (XB-05).

Writes tables/redesign_distributions.csv, redesign_centre.csv, redesign_mc.csv,
redesign_drivers.csv, redesign_by_takeup.csv.
"""
import csv
import math

import numpy as np
from scipy import stats

import engine as E
import mc

T = E.TABLES
N_DRAWS = 10000
LOAN_START = 6

NEW = [  # input, dist, low, mode, high, basis, evidence
    ("wc_loans_year", "triangular", 0.02, 0.08, 0.20, "unsecured loans a year per active saver: ordinary fintech users ~3.6% take any product a year; riders 6% ever took a digital loan; Paytm's engaged device merchants at most ~20% a year; mode near the middle (geometric mean)", "XL-04, XL-37, TB-31, XB-06"),
    ("wc_ticket", "triangular", 50000, 150000, 250000, "Rs per loan: Paytm merchant loans averaged ~Rs 2.05 lakh; Bachatt lends up to Rs 5 lakh; founder's idea up to Rs 2 lakh; smaller shops borrow less", "XB-08, XB-10, founder"),
    ("wc_fee", "triangular", 0.01, 0.02, 0.03, "referral fee as a share of the loan: lead-based sourcing pays 1-3%; Paisabazaar earns at most 4.6% incl. cards", "XL-13, XL-41, XL-42, XL-45, XL-09"),
    ("wc_clawback", "triangular", 0.0, 0.025, 0.05, "share of fees clawed back on early defaults: merchant-loan ECL 4.5-5% (lenders' books)", "XB-07, XL-13, XL-21, XL-47"),
    ("fund_trail", "triangular", 0.002, 0.003, 0.005, "distributor trail on debt funds, regular minus direct plan", "XB-04"),
    ("incentive_share", "uniform", 0.0, 0.25, 0.5, "share of savers who are new B30 or women investors in eligible (non-liquid, non-low-duration) funds", "XB-05"),
    ("xs_other", "lognormal", 14.0, 106.0, 802.0, "everything else per active saver a year (insurance, funds, pension, bills, recharge, gold/home/vehicle/phone loans, FD card): the cross-sell map without personal and business loans; P5 = all low, P95 = all at their best", "crosssell_map.csv"),
]


def new_rows():
    out = []
    for i, d, lo, mo, hi, basis, ev in NEW:
        out.append({"input": i, "segment": "all", "dist": d, "low": lo, "mode": mo if d != "lognormal" else round(math.sqrt(lo * hi), 4),
                    "high": hi, "params": "", "sign": 1, "group": "redesign", "status": "triangulated", "basis": basis, "evidence": ev})
    return out


def design_overrides(ov, seg="ng"):
    o = dict(ov)
    o.update({"mix_gig": 1.0 if seg == "gig" else 0.0, "gold_on": 0.0, "fd_share": 0.0, "cost_notice": 0.0,
              f"cost_debit@{seg}": 0.0, f"cost_failed@{seg}": 0.0,
              "loan_apply": 0.0, "card_uptake": 0.0, "sip_uptake": 0.0, f"ins_uptake@{seg}": 0.0})
    return o


def customer(ov, x, graduate=False, seg="ng"):
    """One customer won under the redesign. ov: engine overrides; x: the new inputs.
    graduate: savers who saved LOAN_START months stay reachable as borrowers after they stop
    saving, leaving at the late-churn rate (else loans flow only to savers still saving)."""
    o = design_overrides({**ov, "trail_liquid": x["fund_trail"]}, seg)
    p, rows, out, _ = E.run("base", o)
    N = p["cohort_size"]
    dm = (1 + p["disc_rate"]) ** (1 / 12) - 1
    per_loan = x["wc_ticket"] * x["wc_fee"] * (1 - x["wc_clawback"]) - p["loan_ops_cost"]
    parts = dict(savings=0.0, incentive=0.0, loans=0.0, other=0.0, serve=0.0, loans_unit=0.0)
    cum, payback, n_loans = -out["cac"], None, 0.0
    s6 = rows[LOAN_START - 1]["active"] / N
    for r in rows:
        t = r["month"]
        a = r["active"] / N
        pool = max(a, s6 * (1 - p["churn_late"]) ** (t - LOAN_START)) if (graduate and t >= LOAN_START) else a
        sav = (r["rev_liquid"] + r["rev_fd"] + r["rev_gold"]) / N
        inc = r["contributions"] / N * 0.01 * x["incentive_share"] if t <= 12 else 0.0
        nl = pool * x["wc_loans_year"] / 12 if t >= LOAN_START else 0.0
        unit = pool / 12 * per_loan if t >= LOAN_START else 0.0       # value per unit of loans_year
        loans = nl * per_loan
        other = a * x["xs_other"] / 12
        serve = (r["cost_payments"] + r["cost_service"] + r["cost_fraud"]) / N
        net = sav + inc + loans + other - serve
        d = (1 + dm) ** t
        for k, v in (("savings", sav), ("incentive", inc), ("loans", loans), ("other", other), ("serve", serve), ("loans_unit", unit)):
            parts[k] += v / d
        n_loans += nl
        cum += net
        if payback is None and cum >= 0:
            payback = t
    ltv = parts["savings"] + parts["incentive"] + parts["loans"] + parts["other"] - parts["serve"]
    return {"cac": out["cac"], "ltv60": ltv, "net": ltv - out["cac"], "payback": payback, "loans_per_customer": n_loans,
            "still_m12": rows[11]["active"] / N, **{f"pv_{k}": v for k, v in parts.items()}}


def draw_new(rng, n):
    u = {i: rng.uniform(size=n) for i, *_ in NEW}
    rows = {r["input"]: r for r in new_rows()}
    return {i: np.array([float(mc.ppf(rows[i], v)) for v in u[i]]) for i in u}


def main():
    dists = mc.load_dists()
    nr = new_rows()
    mc.write("redesign_distributions.csv", nr)
    med = {r["input"]: float(mc.ppf(r, 0.5)) for r in nr}

    # evidence middle
    cen = mc.centre(dists)
    co = mc.to_overrides({k: np.asarray([v]) for k, v in cen.items()})
    co = {k: float(np.ravel(v)[0]) for k, v in co.items()}
    c = customer(co, med)
    be = max(0.0, -(c["net"] - c["pv_loans"])) / c["pv_loans_unit"] if c["pv_loans_unit"] > 0 else float("nan")
    centre = [{"metric": k, "value": v} for k, v in c.items() if v is not None] + [
        {"metric": "breakeven_loans_year", "value": be}, {"metric": "payback_month", "value": c["payback"] or 0},
        *[{"metric": f"median_{k}", "value": v} for k, v in med.items()]]
    mc.write("redesign_centre.csv", centre)
    print(f"evidence middle: CAC {c['cac']:.0f}; savings {c['pv_savings']:.0f} + bonus {c['pv_incentive']:.0f} + loans {c['pv_loans']:.0f} + other {c['pv_other']:.0f} "
          f"- serve {c['pv_serve']:.0f} = {c['ltv60']:.0f}; net {c['net']:.0f}; payback {c['payback'] or 'beyond 5y'}; loans per customer won {c['loans_per_customer']:.2f}; "
          f"break-even loans a year per active saver {be:.3f}")

    # Monte Carlo
    rng = np.random.default_rng(mc.SEED)
    base = mc.sample(dists, N_DRAWS, 0.0, rng)
    ovs = mc.to_overrides(base)
    newd = draw_new(np.random.default_rng(mc.SEED + 1), N_DRAWS)
    res = {k: np.empty(N_DRAWS) for k in ("net", "ltv60", "cac", "pv_loans", "loans_per_customer")}
    pay = np.empty(N_DRAWS)
    for i in range(N_DRAWS):
        o = {k: float(np.ravel(v)[i]) if np.size(v) > 1 else float(np.ravel(v)[0]) for k, v in ovs.items()}
        x = {k: float(v[i]) for k, v in newd.items()}
        r = customer(o, x)
        for k in res:
            res[k][i] = r[k]
        pay[i] = r["payback"] or 999
    net = res["net"]
    summ = [{"metric": "p_net_pos", "value": float((net > 0).mean())}, {"metric": "p_payback_le_36", "value": float((pay <= 36).mean())},
            {"metric": "p_payback_le_60", "value": float((pay <= 60).mean())}, {"metric": "net_mean", "value": float(net.mean())}]
    summ += [{"metric": f"net_p{q}", "value": float(np.percentile(net, q))} for q in (5, 10, 25, 50, 75, 90, 95)]
    summ += [{"metric": f"payback_p{q}", "value": float(np.percentile(pay, q))} for q in (25, 50)]
    mc.write("redesign_mc.csv", summ)
    print({d["metric"]: round(d["value"], 3) for d in summ})

    # drivers: rank regression of net on the inputs that vary
    keys = [k for k in list(base) + list(newd) if np.std((base | newd)[k]) > 0]
    allx = base | newd
    y = stats.rankdata(net)
    X = np.column_stack([stats.rankdata(allx[k]) for k in keys])
    Xs = (X - X.mean(0)) / X.std(0)
    ys = (y - y.mean()) / y.std()
    beta, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
    share = beta ** 2 / (beta ** 2).sum()
    drv = sorted(({"input": k, "variance_share": float(s), "spearman": float(stats.spearmanr(allx[k], net).statistic)} for k, s in zip(keys, share)),
                 key=lambda d: -d["variance_share"])
    mc.write("redesign_drivers.csv", drv)
    print("drivers:", [(d["input"], round(d["variance_share"], 2)) for d in drv[:8]])

    # odds at fixed take-up of the unsecured loan (everything else drawn)
    by = []
    for lam in (0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30):
        nn = np.empty(2000)
        for i in range(2000):
            o = {k: float(np.ravel(v)[i]) if np.size(v) > 1 else float(np.ravel(v)[0]) for k, v in ovs.items()}
            x = {k: float(v[i]) for k, v in newd.items()}
            x["wc_loans_year"] = lam
            nn[i] = customer(o, x)["net"]
        by.append({"loans_year": lam, "p_net_pos": float((nn > 0).mean()), "net_p50": float(np.median(nn))})
        print(f"  take-up {lam:.2f}: P(profit) {by[-1]['p_net_pos']:.0%}, median net {by[-1]['net_p50']:,.0f}")
    mc.write("redesign_by_takeup.csv", by)


if __name__ == "__main__":
    main()

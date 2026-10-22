"""Monte Carlo on the lend-ourselves model: how likely is a customer to pay back, and what decides it?

Every uncertain input is drawn from its evidence range. Customer-side inputs (retention, cost to win,
amounts, support and tech, fund trail, other products) come from the same tables as before
(distributions.csv via mc.sample; redesign_distributions.csv via redesign.draw_new). Lending inputs
are new (tables/lmc_distributions.csv):
  credit_cost   bad-loan losses, share of loan balance a year: 3% / 6% / 10% (savers-safer thesis;
                ICRA steady state 4-6%; digital lenders today 7-10%: LEV-020..029)
  running_cost  running cost excluding winning customers, a year: 3% / 5% / 8% (LEV-018, 019, 026,
                with marketing taken out)
  cost_of_funds 12% / 14% / 16% (LEV-014..016, LEV-062)
  rate          interest a year: 22% / 26% / 30% (Moneyview on-book yield 25-28%, LEV-012)
  fee           processing fee: 2% / 2.5% / 4% (LEV-011, inputs nbfc_proc_fee)
  takeup        proven savers borrowing a year: 5% / 20% / 50% (fintech users ~4%; Paytm's engaged
                merchants up to ~20%; Brazil payroll 20% in year one; founder expects more)
  loan size     shopkeepers 50k / 1.5 lakh / 2.5 lakh over 12 months; drivers 50k / 1 lakh / 2 lakh over 18
All triangular, drawn independently (a real risk not modelled: more borrowing could mean riskier
borrowers). Writes tables/lmc_distributions.csv, lmc_summary.csv, lmc_drivers.csv, lmc_hist.csv.
"""
import numpy as np
from scipy import stats

import mc
import redesign as R

N = 10000
LEND = [  # input, low, mode, high, basis, evidence
    ("credit_cost", 0.03, 0.06, 0.10, "bad-loan losses, share of loan balance a year", "LEV-020, LEV-021, LEV-022, LEV-026, LEV-029, founder"),
    ("running_cost", 0.03, 0.05, 0.08, "running cost a year, excluding winning customers", "LEV-018, LEV-019, LEV-026"),
    ("cost_of_funds", 0.12, 0.14, 0.16, "what we pay to borrow, a year", "LEV-014, LEV-015, LEV-016, LEV-062"),
    ("rate", 0.22, 0.26, 0.30, "interest charged a year", "LEV-012, inputs nbfc_apr"),
    ("fee", 0.02, 0.025, 0.04, "processing fee, share of the loan", "LEV-011, inputs nbfc_proc_fee"),
    ("takeup", 0.05, 0.20, 0.50, "proven savers taking a loan each year", "TB-31, XB-06, LS-06, founder"),
]
SEGS = {"shopkeepers": ("ng", (50000.0, 150000.0, 250000.0), 12), "drivers": ("gig", (50000.0, 100000.0, 200000.0), 18),
        "salaried": ("ng", (50000.0, 100000.0, 200000.0), 18)}
# salaried workers reached through employers or staffing firms (operator, 3 Oct 2026): what differs
SALARIED_RET = (10.3, 15.4)          # month-12 still saving ~ Beta, mean 0.40: staffing exits ~21%/quarter, tenure 21 months (SG-06, SG-07)
SALARIED_RATE = (0.18, 0.24, 0.30)   # more lenders compete for salaried borrowers (Moneyview from 14% for prime, LEV-011; digital yields 25-28%, LEV-012)
SALARIED_CACS = (100.0, 250.0, 500.0)  # no published employer-channel cost (SG-43): shown at fixed values too


def tri(u, lo, mo, hi):
    c = (mo - lo) / (hi - lo)
    return stats.triang.ppf(u, c, loc=lo, scale=hi - lo)


def loan_net(T, n, apr, fee, cof, credit, running):
    i = apr / 12
    emi = T * i / (1 - (1 + i) ** -n)
    b, s = T, 0.0
    for _ in range(n):
        s += b
        b -= emi - b * i
    yrs = s / n * n / 12
    return emi * n - T + fee * T - (cof + credit + running) * yrs


def main():
    dists = mc.load_dists()
    rows = [{"input": i, "dist": "triangular", "low": lo, "mode": mo, "high": hi, "basis": b, "evidence": e} for i, lo, mo, hi, b, e in LEND]
    rows.append({"input": "rate_salaried", "dist": "triangular", "low": SALARIED_RATE[0], "mode": SALARIED_RATE[1], "high": SALARIED_RATE[2],
                 "basis": "salaried: interest charged a year (more lenders compete)", "evidence": "LEV-011, LEV-012"})
    rows.append({"input": "ret_m12_salaried", "dist": "beta", "low": float(stats.beta.ppf(0.05, *SALARIED_RET)), "mode": SALARIED_RET[0] / sum(SALARIED_RET),
                 "high": float(stats.beta.ppf(0.95, *SALARIED_RET)), "basis": "salaried: still saving at month 12", "evidence": "SG-06, SG-07"})
    for seg, (_, (lo, mo, hi), n) in SEGS.items():
        rows.append({"input": f"loan_size_{seg}", "dist": "triangular", "low": lo, "mode": mo, "high": hi, "basis": f"{seg}: loan size, {n} months", "evidence": "XB-08, XB-10, SG rows, founder"})
    mc.write("lmc_distributions.csv", rows)

    summary, drivers, hist = [], [], []
    for seg, (eng, (tlo, tmo, thi), months) in SEGS.items():
        base = mc.sample(dists, N, 0.0, np.random.default_rng(mc.SEED))
        newd = R.draw_new(np.random.default_rng(mc.SEED + 1), N)
        rng = np.random.default_rng(mc.SEED + 11)
        lend = {i: tri(rng.uniform(size=N), lo, mo, hi) for i, lo, mo, hi, *_ in LEND}
        lend["loan_size"] = tri(rng.uniform(size=N), tlo, tmo, thi)
        if seg == "salaried":
            base["ret_m12@ng"] = stats.beta.ppf(np.random.default_rng(mc.SEED + 7).uniform(size=N), *SALARIED_RET)
            lend["rate"] = tri(np.random.default_rng(mc.SEED + 12).uniform(size=N), *SALARIED_RATE)
        ovs = mc.to_overrides(base)
        net = np.empty(N)
        pay = np.empty(N)
        for k in range(N):
            o = {key: float(np.ravel(v)[k]) if np.size(v) > 1 else float(np.ravel(v)[0]) for key, v in ovs.items()}
            T = float(lend["loan_size"][k])
            per = loan_net(T, months, lend["rate"][k], lend["fee"][k], lend["cost_of_funds"][k], lend["credit_cost"][k], lend["running_cost"][k])
            x = {key: float(v[k]) for key, v in newd.items()}
            x.update({"wc_ticket": T, "wc_fee": (per + o.get("loan_ops_cost", 100.0)) / T, "wc_clawback": 0.0, "wc_loans_year": float(lend["takeup"][k])})
            r = R.customer(o, x, graduate=True, seg=eng)
            net[k], pay[k] = r["net"], r["payback"] or 999
        cc = lend["credit_cost"]
        row = {"segment": seg, "p_pays_back": float((net > 0).mean()), "p_payback_le_24": float((pay <= 24).mean()),
               "p_pays_back_if_losses_le_4pct": float((net[cc <= 0.04] > 0).mean()), "p_pays_back_if_losses_ge_7pct": float((net[cc >= 0.07] > 0).mean()),
               "share_draws_losses_le_4pct": float((cc <= 0.04).mean()), "mean": float(net.mean())}
        row.update({f"p{q}": float(np.percentile(net, q)) for q in (5, 10, 25, 50, 75, 90, 95)})
        summary.append(row)
        print(f"{seg}: pays back in {row['p_pays_back']:.0%} of futures (within 2 years {row['p_payback_le_24']:.0%}); "
              f"if losses <= 4%: {row['p_pays_back_if_losses_le_4pct']:.0%}; if losses >= 7%: {row['p_pays_back_if_losses_ge_7pct']:.0%}; "
              f"median {row['p50']:,.0f}, P5 {row['p5']:,.0f}, P95 {row['p95']:,.0f}")
        allx = {**{k: v for k, v in base.items() if np.std(v) > 0}, **newd, **lend}
        allx.pop("wc_loans_year", None); allx.pop("wc_ticket", None); allx.pop("wc_fee", None); allx.pop("wc_clawback", None)
        keys = [k for k in allx if np.std(allx[k]) > 0]
        X = np.column_stack([stats.rankdata(allx[k]) for k in keys])
        Xs = (X - X.mean(0)) / X.std(0)
        y = stats.rankdata(net)
        ys = (y - y.mean()) / y.std()
        beta, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
        share = beta ** 2 / (beta ** 2).sum()
        for k_, s_ in sorted(zip(keys, share), key=lambda z: -z[1]):
            drivers.append({"segment": seg, "input": k_, "variance_share": float(s_), "spearman": float(stats.spearmanr(allx[k_], net).statistic)})
        print("   drivers:", [(d["input"], round(d["variance_share"], 2)) for d in drivers if d["segment"] == seg][:7])
        if seg == "salaried":
            for cac in SALARIED_CACS:
                bb = {**base, "cac_target@ng": np.full(N, cac)}
                ovc = mc.to_overrides(bb)
                nc = np.empty(N)
                for k in range(N):
                    o = {key: float(np.ravel(v)[k]) if np.size(v) > 1 else float(np.ravel(v)[0]) for key, v in ovc.items()}
                    T = float(lend["loan_size"][k])
                    per = loan_net(T, months, lend["rate"][k], lend["fee"][k], lend["cost_of_funds"][k], lend["credit_cost"][k], lend["running_cost"][k])
                    x = {key: float(v[k]) for key, v in newd.items()}
                    x.update({"wc_ticket": T, "wc_fee": (per + o.get("loan_ops_cost", 100.0)) / T, "wc_clawback": 0.0, "wc_loans_year": float(lend["takeup"][k])})
                    nc[k] = R.customer(o, x, graduate=True, seg=eng)["net"]
                row[f"p_pays_back_cac_{int(cac)}"] = float((nc > 0).mean())
                row[f"p50_cac_{int(cac)}"] = float(np.median(nc))
                print(f"   salaried, cost to win fixed at Rs {cac:.0f}: pays back in {row[f'p_pays_back_cac_{int(cac)}']:.0%}; median {row[f'p50_cac_{int(cac)}']:,.0f}")
        lo, hi = np.percentile(net, [1, 99])
        edges = np.linspace(lo, hi, 31)
        cnt, _ = np.histogram(np.clip(net, lo, hi), bins=edges)
        hist += [{"segment": seg, "lo": float(a), "hi": float(b), "share": float(c / N)} for a, b, c in zip(edges[:-1], edges[1:], cnt)]
    mc.write("lmc_summary.csv", summary)
    mc.write("lmc_drivers.csv", drivers)
    mc.write("lmc_hist.csv", hist)


if __name__ == "__main__":
    main()

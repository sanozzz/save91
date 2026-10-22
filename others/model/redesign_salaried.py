"""The redesign for SALARIED blue-collar workers reached through employers (operator, 2 Oct 2026).

Same engine and evidence ranges as model/redesign.py; what differs (research/segments.csv):
  saving        deducted from pay into a debt fund each payday: no fee per debit (SG-08 is a SEBI
                draft for employer-paid MF units; salary advances are already repaid by deduction, SG-40)
  staying       month-12 still saving ~ Beta, mean 0.40, 5-95% about 0.25-0.56: staffing firms lose
                ~21% of staff a quarter (0.79^4 = 0.39 a year, SG-06); average blue-collar tenure
                21 months (~0.56 a year, SG-07); saving can also lapse while employed (no data)
  loan size     Rs 50,000 / 1.5 lakh / 2.5 lakh: a Rs 18-26k salary carries Rs 1.7-2.5 lakh under the
                50% rule (SG-22, SG-14); actual salary advances are Rs 5-20k (SG-40), so demand for
                Rs 1.5 lakh is not observed
  moving jobs   'account moves with the worker' = proven savers keep borrowing after they stop
                saving (graduate=True); job-tied = loans stop when they leave (graduate=False)
  cost to win   no published figure for the employer channel (SG-43): the Monte Carlo keeps the
                consumer evidence (Rs 186-1,340); the grid shows fixed values
Writes tables/rs_distributions.csv, rs_variants.csv, rs_grid.csv, rs_deck.csv, rs_drivers.csv and
the final tables/segment_value.csv (every segment on one yardstick).
"""
import numpy as np
from scipy import stats

import engine as E
import mc
import redesign as R

N = 4000
GRID_N = 2000
RET_A, RET_B = 10.3, 15.4
TICKET = ("triangular", 50000.0, 150000.0, 250000.0)
CACS = (100.0, 250.0, 400.0, 500.0)
TAKEUPS = (0.05, 0.10, 0.20, 0.30)
TARGET_CAC, TARGET_TAKEUP = 250.0, 0.20


def ret_draws(rng, n):
    return stats.beta.ppf(rng.uniform(size=n), RET_A, RET_B)


def ticket_draws(rng, n):
    row = {"dist": TICKET[0], "low": TICKET[1], "mode": TICKET[2], "high": TICKET[3], "params": ""}
    return np.array([float(mc.ppf(row, u)) for u in rng.uniform(size=n)])


def run(base, newd, n, graduate, cac=None, takeup=None, cap=None):
    b = dict(base)
    if cac is not None:
        b["cac_target@ng"] = np.full(n, cac)
    if cap is not None:
        b["cac_target@ng"] = np.minimum(b["cac_target@ng"], cap)
    ovs = mc.to_overrides(b)
    net, pay = np.empty(n), np.empty(n)
    for i in range(n):
        o = {k: float(np.ravel(v)[i]) if np.size(v) > 1 else float(np.ravel(v)[0]) for k, v in ovs.items()}
        x = {k: float(v[i]) for k, v in newd.items()}
        if takeup is not None:
            x["wc_loans_year"] = takeup
        r = R.customer(o, x, graduate=graduate)
        net[i], pay[i] = r["net"], r["payback"] or 999
    return net, pay


def main():
    dists = mc.load_dists()
    mean, p5, p95 = RET_A / (RET_A + RET_B), stats.beta.ppf(0.05, RET_A, RET_B), stats.beta.ppf(0.95, RET_A, RET_B)
    mc.write("rs_distributions.csv", [
        {"input": "ret_m12_salaried", "dist": "beta", "low": p5, "mode": mean, "high": p95, "params": f"{RET_A};{RET_B}",
         "basis": "still saving at month 12: staffing exits ~21%/quarter (0.39 a year); average blue-collar tenure 21 months (~0.56)", "evidence": "SG-06, SG-07"},
        {"input": "wc_ticket_salaried", "dist": TICKET[0], "low": TICKET[1], "mode": TICKET[2], "high": TICKET[3], "params": "",
         "basis": "Rs 18-26k pay carries Rs 1.7-2.5 lakh under the 50% rule; actual salary advances Rs 5-20k", "evidence": "SG-22, SG-14, SG-40"}])
    print(f"salaried retention at 12 months: mean {mean:.2f}, 5-95% {p5:.2f}-{p95:.2f}")

    rng = np.random.default_rng(mc.SEED)
    base = mc.sample(dists, N, 0.0, rng)
    base["ret_m12@ng"] = ret_draws(np.random.default_rng(mc.SEED + 7), N)
    newd = R.draw_new(np.random.default_rng(mc.SEED + 1), N)
    newd["wc_ticket"] = ticket_draws(np.random.default_rng(mc.SEED + 8), N)

    steps = [("loans stop when they change jobs", False, None, None),
             ("account moves with the worker", True, None, None),
             ("account moves, 1 in 5 borrow a year", True, 0.20, None),
             ("account moves, win via employer for Rs 250", True, None, 250.0),
             ("account moves, 1 in 5 borrow, win for Rs 250", True, 0.20, 250.0)]
    var = []
    for lab, g, lam, cap in steps:
        net, pay = run(base, newd, N, g, takeup=lam, cap=cap)
        var.append({"case": lab, "p_net_pos": float((net > 0).mean()), "net_p50": float(np.median(net)), "p_payback_le_36": float((pay <= 36).mean())})
        print(f"{lab:<48} pays back in {var[-1]['p_net_pos']:.0%} of futures; median {var[-1]['net_p50']:,.0f}")
    mc.write("rs_variants.csv", var)

    # drivers of the portable design
    net, _ = run(base, newd, N, True)
    allx = base | newd
    keys = [k for k in allx if np.std(allx[k]) > 0]
    X = np.column_stack([stats.rankdata(allx[k]) for k in keys])
    Xs = (X - X.mean(0)) / X.std(0)
    y = stats.rankdata(net)
    ys = (y - y.mean()) / y.std()
    beta, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
    share = beta ** 2 / (beta ** 2).sum()
    drv = sorted(({"input": k, "variance_share": float(s)} for k, s in zip(keys, share)), key=lambda d: -d["variance_share"])
    mc.write("rs_drivers.csv", drv)
    print("drivers:", [(d["input"], round(d["variance_share"], 2)) for d in drv[:6]])

    # grid: fixed cost to win x fixed take-up, account moves with the worker
    grid = []
    gb, gn = {k: v[:GRID_N] for k, v in base.items()}, {k: v[:GRID_N] for k, v in newd.items()}
    for cac in CACS:
        for lam in TAKEUPS:
            net, _ = run(gb, gn, GRID_N, True, cac=cac, takeup=lam)
            grid.append({"cac": cac, "loans_year": lam, "p_net_pos": float((net > 0).mean()), "net_p50": float(np.median(net))})
    mc.write("rs_grid.csv", grid)
    print("grid:", [(g["cac"], g["loans_year"], round(g["p_net_pos"], 2)) for g in grid])

    # target case and today's evidence, at the evidence middle with salaried retention and ticket
    med = {r["input"]: float(mc.ppf(r, 0.5)) for r in R.new_rows()}
    med["wc_ticket"] = float(mc.ppf({"dist": TICKET[0], "low": TICKET[1], "mode": TICKET[2], "high": TICKET[3], "params": ""}, 0.5))
    ret_med = float(stats.beta.ppf(0.5, RET_A, RET_B))
    out = []
    for name, cac, lam in (("target", TARGET_CAC, TARGET_TAKEUP), ("today", None, None)):
        cen = {**mc.centre(dists), "ret_m12@ng": ret_med}
        if cac is not None:
            cen["cac_target@ng"] = cac
        co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in cen.items()}).items()}
        x = dict(med)
        if lam is not None:
            x["wc_loans_year"] = lam
        c = R.customer(co, x, graduate=True)
        out += [(f"{name}_cac", c["cac"]), (f"{name}_savings", c["pv_savings"] + c["pv_incentive"]), (f"{name}_loans", c["pv_loans"]),
                (f"{name}_other", c["pv_other"]), (f"{name}_serve", c["pv_serve"]), (f"{name}_net", c["net"]), (f"{name}_ltv", c["ltv60"]),
                (f"{name}_payback", c["payback"] or 0), (f"{name}_still_m12", c["still_m12"])]
    out += [("ret_m12_mean", mean), ("ticket_mid", med["wc_ticket"]), ("takeup_mid", med["wc_loans_year"])]
    mc.write("rs_deck.csv", [{"metric": k, "value": v} for k, v in out])
    for k, v in out:
        print(f"  {k:<22}{v:,.2f}")

    # one yardstick for every segment (most we can pay to win one), salaried at its own retention
    import segment_value as S
    S.SEGMENTS = [s for s in S.SEGMENTS if not s[0].startswith("Salaried")] + [
        ("Salaried workers via employers", "ng", med["wc_ticket"], ret_med, True, "SG-22, SG-14, SG-06, SG-07; account moves with the worker"),
        ("Salaried, loans stop when they change jobs", "ng", med["wc_ticket"], ret_med, False, "as above, loans tied to one employer")]
    S.main()


if __name__ == "__main__":
    main()

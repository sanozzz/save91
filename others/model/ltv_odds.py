"""The LTV/CAC Monte Carlo and the LTV/CAC ladder (23 Oct 2026). Founders, 23 Oct: "LTV/CAC is the biggest input driver of the
business. We should do monte carlo on that ... and then build financial that we are showing"; "CAC is fairly sorted and measured
while LTV isn't". So the cost to win stays at the plan (Rs 600 in the seed, Rs 450 after, plus the 10% contingency) and only the
value of a saver is drawn.

Ranges (founders' choice, 23 Oct: "anywhere market to plan"): each unmeasured input is equally likely anywhere between today's
market (the LTV deck's market column, the middle of the evidence in reviews/2026-10-23_ltv_cac_check) and our target (the plan).
The loan inputs move together (Gaussian copula, 0.5): savers who want credit apply more, borrow more, are approved more and opt in
to offers. Each draw runs one online saver (5- and 8-year LTV/CAC, payback) and the company on the profitable path (20,000 online
savers a month from month 30).

The ladder (founders' choice, 23 Oct: "ladder by LTV/CAC"): every input the same share of the way from market to target, solved
for each LTV/CAC rung, then run through the company. The Monte Carlo median rung is the main case for the financials.

Writes tables/ltv_odds_draws.csv, ltv_odds_summary.csv, ltv_odds_drivers.csv, ltv_ladder.csv, ltv_ladder_yearly.csv."""
import csv

import numpy as np
from scipy import stats
from scipy.optimize import brentq
from scipy.stats import qmc

import online_plan as op

N, SEED = 1000, 20261023
LEVEL = 20000                      # the profitable path
LINK = 0.5                         # rank correlation among the loan inputs
X = op.saver_inputs()              # our targets (the plan)
# key: (label, {model input: (today's market, our target)}, a loan input?); "_apply" is the total apply rate (op.loan_mix)
INPUTS = {
    "ticket": ("Average personal or business loan", {"ticket": (50000.0, X["ticket"])}, True),
    "apply": ("Reachable users who apply for a loan, a year", {"_apply": (0.20, op.LOAN_APPLY)}, True),
    "reach": ("Loan offers to KYC'd users who never save", {"_loan_reach": (1.0, op.LOAN_REACH)}, True),
    "approved": ("First applications approved", {"approved_first": (0.20, X["approved_first"])}, True),
    "rises": ("Yearly rises in take-up and approvals", {"takeup_growth": (0.0, X["takeup_growth"]),
                                                        "approval_growth": (0.0, X["approval_growth"])}, True),
    "home_lap": ("Home and property loan size", {"loan_home_ticket": (1.2e6, X["loan_home_ticket"]),
                                                 "loan_lap_ticket": (5e5, X["loan_lap_ticket"])}, True),
    "payout": ("Lender payout rising by year 5", {"_payout_rise": (0.0, op.PAYOUT_RISE)}, False),
    "keep": ("Still saving after a year, and after", {"r12": (0.35, X["r12"]), "churn_late": (0.025, X["churn_late"])}, False),
    "trail": ("Our share of fund fees", {"trail": (0.0062, X["trail"])}, False),
    "repeat": ("Repeat applications approved", {"approved_repeat": (0.735, X["approved_repeat"])}, False),
}
KEYS = list(INPUTS)
RUNGS = (("Today's market", 0.0), ("1×", 1.0), ("2×", 2.0), ("Median", None), ("3×", 3.0), ("5×", 5.0), ("Our targets", 1.0))


def overrides(pos):
    """Model overrides with input k at position pos[k] (0 = today's market, 1 = our target)."""
    ov = {}
    for k, (_lab, params, _loan) in INPUTS.items():
        for p, (mk, tg) in params.items():
            v = mk + (tg - mk) * float(pos[k])
            ov.update(op.loan_mix(v) if p == "_apply" else {p: v})
    return ov


def saver(pos):
    op.OV.clear()
    op._CACHE.clear()
    op.OV.update(overrides(pos))
    try:
        v = op.ltv_view(op.saver_inputs(), op.CAC)[2]
        pay = v["pays back in month"]
        return {"ltv_cac": v["contribution 60m Rs"] / v["cost to win Rs"], "ltv_cac_96": v["LTV/CAC 96m"],
                "payback": pay if isinstance(pay, int) else 97, "ltv": v["contribution 60m Rs"]}
    finally:
        op.OV.clear()
        op._CACHE.clear()


def firm(pos, name=None):
    op.OV.clear()
    op._CACHE.clear()
    op.OV.update(overrides(pos))
    try:
        return op.company(LEVEL, 1.0, name=name)
    finally:
        op.OV.clear()
        op._CACHE.clear()


def pnl(o):
    """Undiscounted cumulative P&L (founders: never NPV): EBITDA positive from, money needed, cumulative EBITDA at 3/5/8 years."""
    cum = np.cumsum(o["ebitda"])
    pm = op.positive_from(o["ebitda"])
    return {"profit_month": pm if pm is not None else 97, "money": o["money_needed"] / op.FX / 1e6,
            "cum_pnl_m": int(np.argmax(cum > 0)) + 1 if (cum > 0).any() else 97,
            "y5_rev": o["revenue"][48:60].sum() / op.CR, "y5_ebitda": o["ebitda"][48:60].sum() / op.CR,
            "y8_ebitda": o["ebitda"][84:96].sum() / op.CR, "cum3": cum[35] / op.CR, "cum5": cum[59] / op.CR, "cum8": cum[95] / op.CR,
            "active60": o["active"][59]}


def sample(n=N, seed=SEED):
    U = qmc.LatinHypercube(d=len(KEYS), seed=seed).random(n)
    loan = [i for i, k in enumerate(KEYS) if INPUTS[k][2]]
    C = np.full((len(loan), len(loan)), LINK)
    np.fill_diagonal(C, 1.0)
    U[:, loan] = stats.norm.cdf(stats.norm.ppf(U[:, loan]) @ np.linalg.cholesky(C).T)
    return {k: U[:, i] for i, k in enumerate(KEYS)}


def at(t):
    return {k: t for k in KEYS}


def solve(target):
    """The common position t (every input the same share of the way from market to target) giving this LTV/CAC."""
    f = lambda t: saver(at(t))["ltv_cac"] - target
    lo, hi = f(0.0), f(1.0)
    if lo > 0 or hi < 0:
        return None
    return brentq(f, 0.0, 1.0, xtol=1e-5)


def pct(v, qs=(10, 50, 90)):
    return {f"P{q}": round(float(np.percentile(v, q)), 3) for q in qs}


def write(name, rows):
    with (op.TAB / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    u = sample()
    draws = []
    for i in range(N):
        pos = {k: u[k][i] for k in KEYS}
        draws.append({**{k: round(float(pos[k]), 5) for k in KEYS}, **saver(pos), **pnl(firm(pos))})
    D = {k: np.array([d[k] for d in draws], dtype=float) for k in draws[0]}
    write("ltv_odds_draws.csv", [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()} for d in draws])
    med = float(np.median(D["ltv_cac"]))

    summ = [{"measure": lab, **pct(D[k]), "mean": round(float(D[k].mean()), 3)} for k, lab in (
        ("ltv_cac", "LTV/CAC, 5 years"), ("ltv_cac_96", "LTV/CAC, 8 years"), ("payback", "Saver pays back in month (97 = not by 96)"),
        ("profit_month", "Company EBITDA positive from month (97 = not by 96)"), ("money", "Money needed, $M"),
        ("y5_ebitda", "Year 5 EBITDA, Rs crore"), ("cum5", "Cumulative EBITDA to month 60, Rs crore"),
        ("cum8", "Cumulative EBITDA to month 96, Rs crore"))]
    for lab, v in (("chance LTV/CAC >= 1", (D["ltv_cac"] >= 1).mean()), ("chance LTV/CAC >= 2", (D["ltv_cac"] >= 2).mean()),
                   ("chance LTV/CAC >= 3", (D["ltv_cac"] >= 3).mean()), ("chance LTV/CAC >= 5", (D["ltv_cac"] >= 5).mean()),
                   ("chance LTV/CAC >= our targets", (D["ltv_cac"] >= saver(at(1.0))["ltv_cac"] - 1e-9).mean()),
                   ("chance EBITDA positive by month 60", (D["profit_month"] <= 60).mean()),
                   ("chance EBITDA positive by month 96", (D["profit_month"] <= 96).mean()),
                   ("chance cumulative EBITDA positive by month 96", (D["cum8"] > 0).mean())):
        summ.append({"measure": lab, "P10": "", "P50": round(float(v), 3), "P90": "", "mean": ""})
    write("ltv_odds_summary.csv", summ)

    # what proving each input buys: the same draws with that one input fixed at today's market, then at our target
    drv = []
    for k in KEYS:
        res = {}
        for tag, val in (("market", 0.0), ("target", 1.0)):
            l = np.array([saver({**{j: u[j][i] for j in KEYS}, k: val})["ltv_cac"] for i in range(N)])
            res[tag] = l
        drv.append({"input": k, "label": INPUTS[k][0],
                    "market": "; ".join(f"{p} {mk:g}" for p, (mk, _t) in INPUTS[k][1].items()),
                    "target": "; ".join(f"{p} {tg:g}" for p, (_m, tg) in INPUTS[k][1].items()),
                    "median if at market": round(float(np.median(res["market"])), 3),
                    "median if at target": round(float(np.median(res["target"])), 3),
                    "chance >=3x if at market": round(float((res["market"] >= 3).mean()), 3),
                    "chance >=3x if at target": round(float((res["target"] >= 3).mean()), 3),
                    "chance >=1x if at market": round(float((res["market"] >= 1).mean()), 3),
                    "chance >=1x if at target": round(float((res["target"] >= 1).mean()), 3),
                    "rank corr with LTV/CAC": round(float(stats.spearmanr(u[k], D["ltv_cac"]).statistic), 3)})
    drv.sort(key=lambda r: -(r["median if at target"] - r["median if at market"]))
    write("ltv_odds_drivers.csv", drv)

    ladder, yearly = [], []
    for name, target in RUNGS:
        t = 1.0 if name == "Our targets" else (0.0 if name == "Today's market" else solve(med if target is None else target))
        if t is None:
            continue
        s = saver(at(t))
        o = firm(at(t), name=name)
        p = pnl(o)
        ladder.append({"rung": name, "position (0 market, 1 targets)": round(t, 4), "LTV/CAC 5y": round(s["ltv_cac"], 3),
                       "LTV/CAC 8y": s["ltv_cac_96"], "LTV Rs": s["ltv"], "saver pays back in month": s["payback"],
                       "chance of at least this": round(float((D["ltv_cac"] >= s["ltv_cac"] - 1e-9).mean()), 3),
                       "EBITDA positive from month": p["profit_month"], "cumulative EBITDA positive from month": p["cum_pnl_m"],
                       "money needed $M": round(p["money"], 2), "Y5 revenue Rs cr": round(p["y5_rev"], 1),
                       "Y5 EBITDA Rs cr": round(p["y5_ebitda"], 1), "Y8 EBITDA Rs cr": round(p["y8_ebitda"], 1),
                       "cumulative EBITDA 3y Rs cr": round(p["cum3"], 1), "cumulative EBITDA 5y Rs cr": round(p["cum5"], 1),
                       "cumulative EBITDA 8y Rs cr": round(p["cum8"], 1), "active savers m60": round(p["active60"])})
        yearly += [{"rung": name, **r} for r in op.yearly(o)]
    write("ltv_ladder.csv", ladder)
    write("ltv_ladder_yearly.csv", yearly)

    for s in summ:
        print(s)
    print("drivers:")
    for d in drv:
        print({k: d[k] for k in ("input", "median if at market", "median if at target", "chance >=3x if at market", "chance >=3x if at target")})
    print("ladder:")
    for r in ladder:
        print(r)


if __name__ == "__main__":
    main()

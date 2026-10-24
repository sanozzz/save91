"""The LTV/CAC Monte Carlo and the "what it takes" ladder (rebased 24 Oct 2026).

Founders, 23 Oct: "LTV/CAC is the biggest input driver of the business. We should do monte carlo on that ... and then build financial
that we are showing"; "CAC is fairly sorted and measured while LTV isn't". So the cost to win stays at the plan (Rs 600 in the seed,
Rs 450 after, plus the 10% contingency) and only the value of a saver is drawn.

24 Oct: the founders questioned every LTV input ("question hard and critically") and fixed most of them at today's market or a
measured number (online_plan's docstring): Rs 70k first loans, market apply and approval, market payouts, home/LAP at market sizes,
debits at Rs 0 through the exchange, no recharge/bills/FD/NPS. What is still uncertain is DRAWN, each input equally likely anywhere
in its range:
  - still saving at 12 months: Bachatt's own 30-40%, with the monthly drop-off after a year moving with it (2.5% -> 1.5%);
  - the debt fund's fee: 0.10% (liquid) -> 0.35% (short duration).
The Monte Carlo median is the MAIN CASE for the financials.

The ladder is now "what it takes": from the main case, five upside levers move together the same share of the way to their upside
(u = 0 main case, 1 all upside), solved for 1x, 2x and 3x and run through the company:
  - the average saved a day: Rs 100 (the product minimum) -> Rs 200;
  - still saving at 12 months -> 45% (the credit hook), the drop-off after on the same line as Bachatt's range (-> 1.0% a month);
  - reachable users who apply for a loan a year: 20% (market) -> 35% (our old target);
  - first loans approved: 20% (market) -> 30% (our old target; the savings record shared with lenders);
  - yearly rises in take-up and approval: none -> 5% / 10% a year (our old targets).
Not on the ladder (founders fixed them): the loan size, payouts, home/LAP sizes, non-saver reach, the products not in the launch app.

Writes tables/ltv_odds_draws.csv, ltv_odds_summary.csv, ltv_odds_drivers.csv, ltv_upside_levers.csv, ltv_ladder.csv,
ltv_ladder_yearly.csv, ltv_saver_split.csv, ltv_main_levers.csv, ltv_main_funnel.csv."""
import csv

import numpy as np
from scipy import stats
from scipy.optimize import brentq
from scipy.stats import qmc

import online_plan as op

N, SEED = 1000, 20261024
LEVEL = 20000                      # the profitable path
# key: (label, {model input: (low end, high end)})
INPUTS = {
    "keep": ("Still saving at 12 months (Bachatt 30-40%), and the drop-off after", {"r12": (0.30, 0.40), "churn_late": (0.025, 0.015)}),
    "trail": ("Our share of the debt fund's fee", {"_debt_trail": (0.0010, op.DEBT_TRAIL)}),
}
KEYS = list(INPUTS)
# key: (label, {model input: (main case, upside)}); None = the main case's own value; "_apply" is the total apply rate (op.loan_mix)
UPSIDE = {
    "daily": ("Average saved a day (Rs)", {"daily": (100.0, 200.0)}),
    "keep_up": ("Still saving at 12 months", {"r12": (None, 0.45), "churn_late": (None, 0.010)}),   # on the drawn range's line (30% 2.5%, 40% 1.5%)
    "apply": ("Reachable users who apply for a loan, a year", {"_apply": (op.LOAN_APPLY, 0.35)}),
    "approved": ("First loans approved", {"approved_first": (0.20, 0.30)}),
    "rises": ("Yearly rises in loan take-up and approval", {"takeup_growth": (0.0, 0.05), "approval_growth": (0.0, 0.10)}),
}
UKEYS = list(UPSIDE)
CAPS = {"r12": 0.90, "churn_late": 0.0, "approved_first": 0.80, "_apply": 0.90}   # where an extrapolated lever stops


def drawn(pos):
    """The drawn inputs' values with input k at position pos[k] (0 = low end, 1 = high end)."""
    return {p: lo + (hi - lo) * float(pos[k]) for k, (_lab, params) in INPUTS.items() for p, (lo, hi) in params.items()}


def overrides(pos, up=None):
    """Model overrides: the drawn inputs at pos, then each upside lever k up[k] of the way from the main case to its upside."""
    v = drawn(pos)
    for k, (_lab, params) in UPSIDE.items():
        u = float((up or {}).get(k, 0.0))
        for p, (lo, hi) in params.items():
            lo = v[p] if lo is None else lo
            x = lo + (hi - lo) * u
            v[p] = min(x, CAPS[p]) if p in CAPS and hi > lo else (max(x, CAPS[p]) if p in CAPS else x)
    ov = {}
    for p, x in v.items():
        ov.update(op.loan_mix(x) if p == "_apply" else {p: x})
    return ov


def saver(pos, up=None):
    op.OV.clear()
    op._CACHE.clear()
    op.OV.update(overrides(pos, up))
    try:
        _d, cum, v = op.ltv_view(op.saver_inputs(), op.CAC)
        pay = v["pays back in month"]
        cac = op.CAC * (1 + op.CONTINGENCY)
        return {"ltv_cac": float(cum[59]) / cac, "ltv_cac_96": round(float(cum[-1]) / cac, 2),     # unrounded rupees (24 Oct)
                "payback": pay if isinstance(pay, int) else 97, "ltv": v["contribution 60m Rs"]}
    finally:
        op.OV.clear()
        op._CACHE.clear()


def split(pos, up=None):
    """One online saver won: revenue lines, serving and LTV/CAC over 5 and 8 years; cross-sell = loans + cards + insurance + other."""
    op.OV.clear()
    op._CACHE.clear()
    op.OV.update(overrides(pos, up))
    try:
        d = op.ltv_parts(op.saver_inputs())
    finally:
        op.OV.clear()
        op._CACHE.clear()
    cac = op.CAC * (1 + op.CONTINGENCY)
    out = {}
    for m, tag in ((60, "5y"), (96, "8y")):
        s = {k: float(d[k][:m].sum()) for k in ("Fund fees", "Loans (all referrals)", "Cards", "Insurance", "Other products", "serving")}
        cross = s["Loans (all referrals)"] + s["Cards"] + s["Insurance"] + s["Other products"]
        out[tag] = {**s, "cross-sell": cross, "net": s["Fund fees"] + cross - s["serving"], "cost to win": cac,
                    "LTV/CAC": (s["Fund fees"] + cross - s["serving"]) / cac, "cross-sell / CAC": cross / cac,
                    "cross-sell net of serving / CAC": (cross - s["serving"]) / cac, "fund fees / CAC": s["Fund fees"] / cac}
    return out


def firm(pos, up=None, name=None):
    op.OV.clear()
    op._CACHE.clear()
    op.OV.update(overrides(pos, up))
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
    return {k: U[:, i] for i, k in enumerate(KEYS)}


def at(t):
    return {k: t for k in KEYS}


def up_at(u, keys=None):
    return {k: u for k in (keys or UKEYS)}


def solve(target):
    """The common drawn position t (every drawn input the same share of the way from low to high) giving this LTV/CAC."""
    f = lambda t: saver(at(t))["ltv_cac"] - target
    lo, hi = f(0.0), f(1.0)
    if lo > 0 or hi < 0:
        return None
    return brentq(f, 0.0, 1.0, xtol=1e-5)


def solve_up(target, t, keys=None, top=1.0, measure="ltv_cac"):
    """The share u of the way to the upside (the given levers together, the rest at the main case) giving this LTV/CAC."""
    f = lambda u: saver(at(t), up_at(u, keys))[measure] - target
    lo, hi = f(0.0), f(top)
    if lo >= 0:
        return 0.0
    if hi < 0:
        return None
    return brentq(f, 0.0, top, xtol=1e-5)


def lever_values(pos, up):
    """The headline inputs at a rung, in words for the decks."""
    o = overrides(pos, up)
    return {"saved a day Rs": round(op.saver_inputs()["daily"] if "daily" not in o else o["daily"]),
            "still saving at 12 months": round(o["r12"], 4), "drop-off a month after 12": round(o["churn_late"], 4),
            "apply a year": round(o.get("apply", op.LOAN_APPLY * op.LOAN_MIX["apply"]) / op.LOAN_MIX["apply"], 4),
            "first loans approved": round(o.get("approved_first", 0.20), 4),
            "take-up rise a year": round(o.get("takeup_growth", 0.0), 4), "approval rise a year": round(o.get("approval_growth", 0.0), 4)}


def pct(v, qs=(10, 50, 90)):
    return {f"P{q}": round(float(np.percentile(v, q)), 3) for q in qs}


def write(name, rows):
    with (op.TAB / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main_tables():
    """The plan's levers (online_plan.LEVERS, the two costs to win, debt-only funds, online only) and the loan funnel, around the main case."""
    op.use_main_case()
    try:
        lev = []
        for nm, ov in op.LEVERS:
            op.OV.clear()
            op.OV.update(ov)
            lev.append(op.row(op.company(LEVEL, 1.0, name="The main case" if nm == "The plan" else nm)))
        op.OV.clear()
        for nm, cac in (("Cost to win Rs 300", 300.0), ("Cost to win Rs 600 (our funnel)", 600.0)):
            lev.append(op.row(op.company(LEVEL, 1.0, cac=cac, name=nm)))
        lev.append(op.row(op.company(LEVEL, 1.0, mix="debt", name="Debt-only funds")))
        lev.append(op.row(op.company(LEVEL, 1.0, doorstep_after=False, name="Online only after m18")))
        write("ltv_main_levers.csv", lev)
        write("ltv_main_funnel.csv", op.loan_funnel_rows())
    finally:
        op.OV.clear()
        op.use_main_case(False)


def upside_levers(t):
    """Each upside lever alone from the main case: its LTV/CAC at the upside, and the value it needs alone for 1x and 2x (5 years)."""
    rows = []
    for k in UKEYS:
        lab, params = UPSIDE[k]
        s = saver(at(t), {k: 1.0})
        row = {"lever": k, "label": lab,
               "main case": "; ".join(f"{p} {overrides(at(t))[p if p != '_apply' else 'apply'] / (op.LOAN_MIX['apply'] if p == '_apply' else 1):g}" for p in params),
               "upside": "; ".join(f"{p} {hi:g}" for p, (_lo, hi) in params.items()),
               "LTV/CAC 5y at the upside alone": round(s["ltv_cac"], 3), "LTV/CAC 8y at the upside alone": s["ltv_cac_96"],
               "pays back in month at the upside alone": s["payback"]}
        for target, tag in ((1.0, "1x"), (2.0, "2x")):
            u = solve_up(target, t, [k], top=3.0)
            if u is None:
                row[f"alone for {tag} (5y)"] = "not reachable"
            else:
                o = overrides(at(t), {k: u})
                p0 = next(iter(params))
                val = o["apply"] / op.LOAN_MIX["apply"] if p0 == "_apply" else o[p0]
                row[f"alone for {tag} (5y)"] = f"{p0} {val:.4g}" + (" (beyond the upside)" if u > 1 else "")
        rows.append(row)
    return rows


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
                   ("chance LTV/CAC >= 3", (D["ltv_cac"] >= 3).mean()),
                   ("chance 8-year LTV/CAC >= 1", (D["ltv_cac_96"] >= 1).mean()),
                   ("chance saver pays back by month 96", (D["payback"] <= 96).mean()),
                   ("chance EBITDA positive by month 60", (D["profit_month"] <= 60).mean()),
                   ("chance EBITDA positive by month 96", (D["profit_month"] <= 96).mean()),
                   ("chance cumulative EBITDA positive by month 96", (D["cum8"] > 0).mean())):
        summ.append({"measure": lab, "P10": "", "P50": round(float(v), 3), "P90": "", "mean": ""})
    write("ltv_odds_summary.csv", summ)

    # what pinning each drawn input buys: the same draws with that one input at its low end, then its high end
    drv = []
    for k in KEYS:
        res = {}
        for tag, val in (("low", 0.0), ("high", 1.0)):
            res[tag] = np.array([saver({**{j: u[j][i] for j in KEYS}, k: val})["ltv_cac"] for i in range(N)])
        drv.append({"input": k, "label": INPUTS[k][0],
                    "low": "; ".join(f"{p} {lo:g}" for p, (lo, _h) in INPUTS[k][1].items()),
                    "high": "; ".join(f"{p} {hi:g}" for p, (_l, hi) in INPUTS[k][1].items()),
                    "median if low": round(float(np.median(res["low"])), 3), "median if high": round(float(np.median(res["high"])), 3),
                    "rank corr with LTV/CAC": round(float(stats.spearmanr(u[k], D["ltv_cac"]).statistic), 3)})
    drv.sort(key=lambda r: -(r["median if high"] - r["median if low"]))
    write("ltv_odds_drivers.csv", drv)

    t_main = solve(med)
    write("ltv_upside_levers.csv", upside_levers(t_main))

    ends = {"Low end (30% still saving)": {**at(t_main), "keep": 0.0}, "Main case": at(t_main),   # the ends move retention only
            "High end (40% still saving)": {**at(t_main), "keep": 1.0}}
    sp = []
    for name, pos in ends.items():
        for tag, s in split(pos).items():
            sp.append({"case": name, "years": tag, **{k: round(v, 3) for k, v in s.items()}})
    write("ltv_saver_split.csv", sp)

    rungs = [(name, pos, 0.0) for name, pos in ends.items()]
    for target, tag in ((1.0, "1×"), (2.0, "2×"), (3.0, "3×")):
        uu = solve_up(target, t_main)
        if uu is not None:
            rungs.append((tag, at(t_main), uu))
    rungs.append(("All upside", at(t_main), 1.0))
    rungs.sort(key=lambda r: saver(r[1], up_at(r[2]))["ltv_cac"])
    ladder, yearly = [], []
    for name, pos, uu in rungs:
        s = saver(pos, up_at(uu))
        o = firm(pos, up_at(uu), name=name)
        p = pnl(o)
        ladder.append({"rung": name, "drawn position (0 low, 1 high)": round(t_main, 4),
                       "retention position (0 = 30%, 1 = 40%)": round(pos["keep"], 4),
                       "upside position (0 main case, 1 all upside)": round(uu, 4),
                       **lever_values(pos, up_at(uu)),
                       "LTV/CAC 5y": round(s["ltv_cac"], 3), "LTV/CAC 8y": s["ltv_cac_96"], "LTV Rs": s["ltv"], "saver pays back in month": s["payback"],
                       "chance of at least this": round(float((D["ltv_cac"] >= s["ltv_cac"] - 1e-9).mean()), 3),
                       "EBITDA positive from month": p["profit_month"], "cumulative EBITDA positive from month": p["cum_pnl_m"],
                       "money needed $M": round(p["money"], 2), "Y5 revenue Rs cr": round(p["y5_rev"], 1),
                       "Y5 EBITDA Rs cr": round(p["y5_ebitda"], 1), "Y8 EBITDA Rs cr": round(p["y8_ebitda"], 1),
                       "cumulative EBITDA 3y Rs cr": round(p["cum3"], 1), "cumulative EBITDA 5y Rs cr": round(p["cum5"], 1),
                       "cumulative EBITDA 8y Rs cr": round(p["cum8"], 1), "active savers m60": round(p["active60"])})
        yearly += [{"rung": name, **r} for r in op.yearly(o)]
    write("ltv_ladder.csv", ladder)
    write("ltv_ladder_yearly.csv", yearly)
    main_tables()

    for s in summ:
        print(s)
    print("drivers:", *drv, sep="\n")
    print("upside levers:", *upside_levers(t_main), sep="\n")
    print("split:", *sp, sep="\n")
    print("ladder:")
    for r in ladder:
        print(r)


if __name__ == "__main__":
    main()

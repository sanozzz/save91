"""What moves the COMPANY's EBITDA break-even, on the round-10 base (story/CHANGES_round10_company_base_2026-10-17.md).

Every row is the deterministic company model (company_model.run_plan) at the likely values with each agent's own sign-up draw:
the base is 80 agents by m18 then replace leavers, pay on balance capped at Rs 10,000 a month, central lean hold (released the
month after EBITDA first turns positive), UPI 30%, Series A Rs 50 crore at m18. Each row changes only what it says:
  market     sign-ups year-1 level 120 (every agent's draw x 1.2); every take-up hazard x 1.25 (loan apply, card share, the 17
             products' take-up, as cohort_engine defines them); personal-loan size x 1.2 (the Rs 5 lakh repeat cap stays);
             still saving at month 12 = 65%.
  operator   UPI push to 60% at month 12 (an assumption change); no contingency; pay caps Rs 5,000 / Rs 15,000 (sensitivity);
             salary only (reference: not acceptable to the operator); 100 or 120 agents by m18, then replace leavers.
  searched   the ONE market value, alone, that brings the base to EBITDA break-even (first positive and staying positive) by m48:
             the take-up multiple (steps of 0.01), still saving at month 12 (steps of 0.5 points, below r3 = 80%) and the
             loan-size multiple (steps of 0.01).

Writes tables/company_levers.csv.
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402

TAKEUP_KEYS = ("apply", "card_share", *[f"{p}_takeup" for p, *_ in E.PRODUCTS])
TARGET_BE = 48
A_LABEL = f"Cash at m60, with the Rs {C.SERIES_A / C.CRORE:.0f} crore Series A (Rs)"
SMALLEST_A = "Smallest Series A at m18 keeping cash at or above Rs 5 crore through m60 (Rs)"


def run(x, dists, over=None, opts=None, sf=1.0, a18=C.BASE_A18):
    o, *_ = C.run_plan({**x, **(over or {})}, dists, a18=a18, h=0, central=C.BASE_CENTRAL, opts=opts, factors=[sf])
    return o


def be_month(o):
    v = C.stays_positive_from(o["ebitda"])[0]
    return 999.0 if np.isnan(v) else float(v)


def row(name, what, o, base_y5, value_needed=""):
    h = C.headline(o)
    fp = int(C.first_positive(o["ebitda"])[0])
    y5 = float(h["ebitda_y5"][0])
    be = be_month(o)
    return {"Lever": name, "What changes": what, "Value needed for break-even by m48": value_needed,
            "Year-5 EBITDA (Rs)": y5, "Change in year-5 EBITDA vs base (Rs)": y5 - (y5 if base_y5 is None else base_y5),
            "EBITDA break-even month": "not within 60" if be > 60 else be,
            "First month EBITDA positive": fp if fp else "not within 60",
            "Active savers when EBITDA first turns positive": float(o["still_saving"][0, fp - 1]) if fp else "",
            "Agents then": float(o["agents"][0, fp - 1]) if fp else "",
            A_LABEL: float(h["cash_60"][0]), SMALLEST_A: float(h["smallest_a"][0]),
            "Cumulative PAT, 60 months (Rs)": float(h["cum_pat_60"][0])}


def search(x, dists, label, grid, make):
    for v in grid:
        o = run(x, dists, make(v))
        if be_month(o) <= TARGET_BE:
            return v, o
    return None, None


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    o = run(x, dists)
    rows = [row("Base", f"80 agents by m18 then replace leavers; cap Rs 10,000; lean hold; UPI 30%; Series A Rs {C.SERIES_A / C.CRORE:.0f} crore",
                o, None)]
    base_y5 = rows[0]["Year-5 EBITDA (Rs)"]
    lad = {r["Line"]: r for r in csv.DictReader((C.T / "company_pnl_ladder_yearly.csv").open())}
    assert abs(base_y5 - float(lad["EBITDA"]["Year 5"])) <= 1e-6 * abs(base_y5), "base row != company_model"
    levers = [
        ("Market: sign-ups year-1 level 120", "every agent's own draw x 1.2", {}, {}, 1.2, C.BASE_A18),
        ("Market: all take-up hazards +25%", "loan apply, card share, the 17 products' take-up x 1.25", {k: x[k] * 1.25 for k in TAKEUP_KEYS}, {}, 1.0, C.BASE_A18),
        ("Market: loan size +20%", f"personal-loan ticket Rs {x['ticket']:,.0f} -> Rs {x['ticket'] * 1.2:,.0f}", {"ticket": x["ticket"] * 1.2}, {}, 1.0, C.BASE_A18),
        ("Market: still saving at month 12, 65%", f"r12 {x['r12']:.0%} -> 65%", {"r12": 0.65}, {}, 1.0, C.BASE_A18),
        ("Operator: UPI push to 60% at month 12 (an assumption change)", "upi_12 30% -> 60%", {"upi_12": 0.60}, {}, 1.0, C.BASE_A18),
        ("Operator: no contingency", "contingency 10% -> 0", {}, {"contingency": 0.0}, 1.0, C.BASE_A18),
        ("Operator: pay cap Rs 5,000 (sensitivity)", "cap Rs 10,000 -> Rs 5,000 a month", {}, {"incentive_cap": 5000.0}, 1.0, C.BASE_A18),
        ("Operator: pay cap Rs 15,000 (sensitivity)", "cap Rs 10,000 -> Rs 15,000 a month", {}, {"incentive_cap": 15000.0}, 1.0, C.BASE_A18),
        ("Operator: salary only (reference; not acceptable)", "no pay on balance", {"agent_balance_pay": 0.0}, {}, 1.0, C.BASE_A18),
        ("Operator: 100 agents by m18, then replace leavers", "fleet 80 -> 100 at m18", {}, {}, 1.0, 100),
        ("Operator: 120 agents by m18, then replace leavers", "fleet 80 -> 120 at m18", {}, {}, 1.0, 120),
        ("Combination: take-up +25% and UPI 60%", "two of the above", {**{k: x[k] * 1.25 for k in TAKEUP_KEYS}, "upi_12": 0.60}, {}, 1.0, C.BASE_A18),
        ("Combination: take-up +25% and loan size +20%", "two of the above", {**{k: x[k] * 1.25 for k in TAKEUP_KEYS}, "ticket": x["ticket"] * 1.2},
         {}, 1.0, C.BASE_A18),
    ]
    for name, what, over, opts, sf, a18 in levers:
        rows.append(row(name, what, run(x, dists, over, opts, sf, a18), base_y5))
    searches = [
        ("Searched: take-up multiple for break-even by m48", "every take-up hazard x k (k from 1.01, steps of 0.01)",
         np.round(np.arange(1.01, 2.501, 0.01), 2), lambda k: {q: x[q] * k for q in TAKEUP_KEYS}, lambda v: f"x {v:.2f}"),
        ("Searched: still saving at month 12 for break-even by m48", "r12 from 55.5%, steps of 0.5 points (must stay below r3 = 80%)",
         np.round(np.arange(0.555, float(x["r3"]) - 0.004, 0.005), 3), lambda v: {"r12": v}, lambda v: f"{v:.1%}"),
        ("Searched: loan-size multiple for break-even by m48", "personal-loan ticket x k (k from 1.01, steps of 0.01)",
         np.round(np.arange(1.01, 2.001, 0.01), 2), lambda k: {"ticket": x["ticket"] * k}, lambda v: f"x {v:.2f}"),
    ]
    for name, what, grid, make, fmt in searches:
        v, o = search(x, dists, name, grid, make)
        if v is None:
            rows.append({"Lever": name, "What changes": what, "Value needed for break-even by m48": "not reachable in the search range"})
        else:
            rows.append(row(name, what, o, base_y5, fmt(v)))
    cols = list(dict.fromkeys(k for r in rows for k in r))
    C.write("company_levers.csv", [{k: r.get(k, "") for k in cols} for r in rows])
    for r in rows:
        print(f"  {r['Lever'][:62]:<62} {r.get('Value needed for break-even by m48', '')!s:>10} y5 EBITDA "
              f"{r.get('Year-5 EBITDA (Rs)', float('nan')) / 1e7:7.2f} cr  BE {r.get('EBITDA break-even month', '')!s:>14}  "
              f"savers at first positive {r.get('Active savers when EBITDA first turns positive', '')!s:>10.10}")
    return rows


if __name__ == "__main__":
    main()

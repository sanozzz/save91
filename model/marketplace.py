"""Cross-sell over time through a loan marketplace (operator, 16 Oct 2026): "these customers will also take loans,
insurance, credit cards over time. There would be a yearly application rate, then eligibility based on lender
(assume we build a paisabazaar.com where we help them get the best loan and tenure), we make our money through loan
origination fee + on collections in case NPA recovered".

Per proven saver (saved 6+ months, still saving) per year, low / middle / high (moved together):
  apply         10 / 20 / 35%   applies for a loan (XL-42 Kissht 17.5% ever borrowed; LS-06 Brazil 20% year one; founder 35%)
  eligible      30 / 50 / 70%   can carry a Rs 2.5 lakh EMI under the 50% rule (XB-09, interview incomes)
  approved      25 / 35 / 50%   through a marketplace of several lenders (single lender: founder's past data 25%); judgement, untested
  ticket        Rs 2.5 lakh (operator)
  origination   1 / 2 / 3% of the loan (operator 1%; DSA payouts 1-3%, LEV-009; Paisabazaar <= 4.7% incl. card fees, LEV-065)
  taken back    5 / 2.5 / 0% of origination fees (XL-13)
  collections   loans that go 90+ days bad 3.6 / 5 / 7% (CRIF >Rs 50k peak 3.6%, MAC-03), half the loan still owed when they do
                (judgement), 30 / 32.5 / 35% of that recovered (XB-07 Paytm), our fee 5 / 10 / 15% of what is recovered
                (NABARD tender pays non-SARFAESI agents 5-7%; unsecured judgement, unverified); paid ~18 months after disbursal
  other         insurance and other products Rs 8 / 63 / 259 a saver a year (XO-39), all savers
  cards         5% of sign-ups (operator) x Rs 500 / 1,250 / 2,000 (BM-08, unverified), in the month he joins
Savings, agent pay, retention, discount and horizon as model/agent_npv.py. Writes tables/mkt_inputs.csv, mkt_npv.csv,
mkt_ltv.csv, mkt_breakeven.csv.
"""
import csv
from pathlib import Path

import agent_npv as N

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
TICKET = 250000.0
CASES = {  # name: apply, eligible, approved, origination, taken_back, npa, recovered, fee_on_recovered, other, card_fee
    "low": (0.10, 0.30, 0.25, 0.01, 0.05, 0.036, 0.30, 0.05, 8.0, 500.0),
    "middle": (0.20, 0.50, 0.35, 0.02, 0.025, 0.05, 0.325, 0.10, 63.0, 1250.0),
    "high": (0.35, 0.70, 0.50, 0.03, 0.0, 0.07, 0.35, 0.15, 259.0, 2000.0),
}
OWED_AT_DEFAULT, COLLECT_LAG = 0.5, 1.20 ** -1.5
CARD_SHARE = 0.05
R12S = (0.30, 0.40, 0.55, 0.70)
PAYS = ("salary only", "salary + 0.5% a year of balance")


def pv_exposure(r12, months):
    c = 1 - r12 ** (1 / 12)
    pv_sy = pv_py = pv_signups = 0.0
    for t in range(months):
        active = sum(N.SIGNUPS_M * (1 - c) ** (t - m) for m in range(t + 1))
        proven = sum(N.SIGNUPS_M * (1 - c) ** (t - m) for m in range(t + 1) if t - m + 1 > 6)
        d = (1 + N.DISC_M) ** (t + 1)
        pv_sy += active / 12 / d
        pv_py += proven / 12 / d
        pv_signups += N.SIGNUPS_M / d
    return pv_sy, pv_py, pv_signups


def per_loan(case):
    a, e, ap, orig, back, npa, rec, fee, other, card = CASES[case]
    return {"loans_per_100_proven": 100 * a * e * ap, "origination": TICKET * orig * (1 - back),
            "collections": TICKET * npa * OWED_AT_DEFAULT * rec * fee * COLLECT_LAG}


def npv(r12, months, pay, case):
    a, e, ap, orig, back, npa, rec, fee, other, card = CASES[case]
    base = N.run(r12, months, pay)
    pv_sy, pv_py, pv_su = pv_exposure(r12, months)
    pl = per_loan(case)
    loans = pv_py * a * e * ap
    parts = {"savings": base["pv_revenue"], "other_products": other * pv_sy, "cards": CARD_SHARE * card * pv_su,
             "loan_origination": loans * pl["origination"], "loan_collections": loans * pl["collections"]}
    income = sum(parts.values())
    return {"pv_cost": base["pv_cost"], "pv_income": income, "npv": income - base["pv_cost"], **{f"pv_{k}": v for k, v in parts.items()},
            "signups": N.SIGNUPS_M * months}


def breakeven(months, pay, case):
    if npv(0.95, months, pay, case)["npv"] < 0:
        return None
    lo, hi = 0.05, 0.95
    if npv(lo, months, pay, case)["npv"] >= 0:
        return lo
    for _ in range(50):
        m = (lo + hi) / 2
        if npv(m, months, pay, case)["npv"] < 0:
            lo = m
        else:
            hi = m
    return hi


def main():
    with (T / "mkt_inputs.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "low", "middle", "high"])
        names = ["applies a year", "eligible", "approved (marketplace)", "origination fee", "fees taken back", "loans going 90+ days bad",
                 "recovered of what is owed", "our fee on what is recovered", "other products Rs a saver a year", "card fee Rs"]
        for i, nm in enumerate(names):
            w.writerow([nm, CASES["low"][i], CASES["middle"][i], CASES["high"][i]])
        for k in ("loans_per_100_proven", "origination", "collections"):
            w.writerow([k, per_loan("low")[k], per_loan("middle")[k], per_loan("high")[k]])
    rows, ltv, be = [], [], []
    for months in (36, 60):
        for pay in PAYS:
            for case in CASES:
                for r in R12S:
                    x = npv(r, months, pay, case)
                    rows.append({"years": months // 12, "pay": pay, "case": case, "r12": r, **x})
                b = breakeven(months, pay, case)
                be.append({"years": months // 12, "pay": pay, "case": case, "breakeven_r12": b if b is not None else "not reachable"})
    for r in R12S:  # per customer won, 5 years, salary only, middle case
        x = npv(r, 60, "salary only", "middle")
        su = x["signups"]
        ltv.append({"r12": r, "cost_per_signup": x["pv_cost"] / su, **{k.replace("pv_", "per_signup_"): v / su for k, v in x.items() if k.startswith("pv_") and k != "pv_cost"}})
    for name, data in (("mkt_npv.csv", rows), ("mkt_ltv.csv", ltv), ("mkt_breakeven.csv", be)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    for k in ("low", "middle", "high"):
        pl = per_loan(k)
        print(f"{k:<7} loans/100 proven/yr {pl['loans_per_100_proven']:.2f} | per loan: origination {pl['origination']:,.0f}, collections {pl['collections']:,.0f}")
    for x in rows:
        if x["case"] == "middle" or x["r12"] in (0.30, 0.70):
            print(f"{x['years']}y {x['pay']:<32} {x['case']:<6} R12 {x['r12']:.0%}: NPV {x['npv']:>11,.0f} | income: savings {x['pv_savings']:>9,.0f} other {x['pv_other_products']:>9,.0f} "
                  f"cards {x['pv_cards']:>8,.0f} origination {x['pv_loan_origination']:>9,.0f} collections {x['pv_loan_collections']:>7,.0f} | cost {x['pv_cost']:>10,.0f}")
    for b in be:
        v = b["breakeven_r12"]
        print(f"BREAK-EVEN {b['years']}y {b['pay']:<32} {b['case']:<6}: {v if isinstance(v, str) else f'{v:.1%}'}")
    for l in ltv:
        print(f"LTV 5y per customer won, salary, middle, R12 {l['r12']:.0%}: cost {l['cost_per_signup']:.0f} | savings {l['per_signup_savings']:.0f} other {l['per_signup_other_products']:.0f} "
              f"cards {l['per_signup_cards']:.0f} origination {l['per_signup_loan_origination']:.0f} collections {l['per_signup_loan_collections']:.0f} | total {l['per_signup_income']:.0f}")


if __name__ == "__main__":
    main()

"""Lending ourselves (operator, 2 Oct 2026): savings is the hook and need not pay; we lend from our
own NBFC (or co-lend, keeping at least 10% of each loan, LS-01) and earn the interest.

Per loan (amortising, monthly), in the way lenders report (shares of the average loan balance a year):
  interest  = EMI x months - loan;  fee = processing fee x loan
  funding   = cost of borrowing (14%; Moneyview / Kissht / KreditBee 13-15%, LEV-014..016, LEV-062)
  losses    = credit cost a year: 3% if savers really are safer (founder's thesis, untested) /
              6% industry steady state (ICRA 4-6%, LEV-020) / 9% digital lenders today (KreditBee 7.7%,
              Kissht 8.5-9%, Groww 7%, Stashfin 9.9% of disbursal: LEV-021, 022, 026, 029)
  running   = operating cost a year EXCLUDING winning customers (counted separately as the cost to win):
              3% / 5% / 8% (digital lenders report 9-16% INCLUDING marketing: KreditBee 9.6%, Kissht
              14.5-16%, Stashfin 8.8%: LEV-018, 019, 026)
  net       = interest + fee - funding - losses - running
Cross-check: digital lenders earn 1-4% a year on their loan book after everything (LEV-027).
Referral (the earlier redesign) is shown alongside: 2% of the loan, less 2.5% clawback.

Per customer: the redesign's customer (saving into debt funds, no fee per debit; proven savers keep
borrowing after they stop saving), with the per-loan value above. Evidence middle otherwise.
Equity is NOT charged in the per-loan net: capital needed is reported separately (a third of the
book, KreditBee AUM/TNW 3.25x, LEV-023), with the NBFC's own fixed cost (Rs 8 crore a year, inputs).

Writes tables/lend_loan.csv, lend_customer.csv, lend_scale.csv.
"""
import numpy as np

import mc
import redesign as R

SEGS = [  # name, engine segment, loan, months, yearly rate, fee
    ("Delivery riders", "gig", 25000.0, 6, 0.30, 0.03),
    ("Drivers and home-service workers", "gig", 100000.0, 18, 0.26, 0.03),
    ("Shopkeepers", "ng", 150000.0, 12, 0.26, 0.025),
]
COF = 0.14
CREDIT = {"savers safer": 0.03, "industry steady state": 0.06, "industry today": 0.09}
RUNNING = {"savers safer": 0.03, "industry steady state": 0.05, "industry today": 0.08}
CASES = tuple(CREDIT)
TAKEUPS = (0.10, 0.20, 0.35, 0.50)
EQUITY_SHARE, NBFC_FIXED = 1 / 3, 5e7      # inputs.csv nbfc_fixed_cr: 8 / 5 / 3 crore (bear / base / bull)


def loan(T, n, apr, fee, case, cof=COF):
    i = apr / 12
    emi = T * i / (1 - (1 + i) ** -n)
    b, opening = T, []
    for _ in range(n):
        opening.append(b)
        b -= emi - b * i
    avg = sum(opening) / n
    yrs = avg * n / 12                                   # rupee-years of loan balance
    interest = emi * n - T
    funding = cof * yrs
    losses = CREDIT[case] * yrs
    running = RUNNING[case] * yrs
    net = interest + fee * T - funding - losses - running
    margin = interest + fee * T - funding - running
    return {"emi": emi, "interest": interest, "fee": fee * T, "funding": funding, "losses": losses, "running": running,
            "avg_balance": avg, "balance_years": yrs, "net": net, "return_on_book": net / yrs,
            "breakeven_credit_cost": margin / yrs, "capital": EQUITY_SHARE * avg}


def main():
    dists = mc.load_dists()
    med = {r["input"]: float(mc.ppf(r, 0.5)) for r in R.new_rows()}
    cen = mc.centre(dists)
    loans, cust, scale = [], [], []
    for name, seg, T, n, apr, fee in SEGS:
        ref = T * 0.02 * (1 - 0.025)
        for case in CASES:
            L = loan(T, n, apr, fee, case)
            loans.append({"segment": name, "loan": T, "months": n, "rate": apr, "case": case, **L, "referral_net": ref})
        print(f"{name}: one Rs {T:,.0f} loan over {n} months at {apr:.0%}: lend ourselves earns "
              + ", ".join(f"{loan(T, n, apr, fee, c)['net']:,.0f} ({c}; {loan(T, n, apr, fee, c)['return_on_book']:.1%} of book a year)" for c in CASES)
              + f"; referral {ref:,.0f}.")
        for cac in (None, 250.0):
            c = dict(cen)
            if cac is not None:
                c[f"cac_target@{seg}"] = cac
            co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in c.items()}).items()}
            for mode in ("lend", "referral"):
                for pd in (CASES if mode == "lend" else (None,)):
                    per = loan(T, n, apr, fee, pd)["net"] + 100.0 if mode == "lend" else ref + 100.0   # engine subtracts its Rs 100 handling cost
                    for lam in TAKEUPS:
                        x = {**med, "wc_ticket": T, "wc_fee": per / T, "wc_clawback": 0.0, "wc_loans_year": lam}
                        r = R.customer(co, x, graduate=True, seg=seg)
                        cust.append({"segment": name, "mode": mode, "default": pd if pd is not None else "", "takeup": lam,
                                     "cac": r["cac"], "worth_before_cac": r["ltv60"], "net": r["net"], "payback": r["payback"] or "",
                                     "loans_per_customer": r["loans_per_customer"], "cac_case": "evidence" if cac is None else "250"})
        # scale: customers a year needed for the NBFC's fixed cost, at 5% default and 1 in 5 borrowing (evidence cost to win)
        row = next(r for r in cust if r["segment"] == name and r["mode"] == "lend" and r["default"] == "industry steady state" and r["takeup"] == 0.20 and r["cac_case"] == "evidence")
        need = NBFC_FIXED / row["net"] if row["net"] > 0 else float("nan")
        lpc = row["loans_per_customer"]
        cap_per_customer = lpc * EQUITY_SHARE * loan(T, n, apr, fee, "industry steady state")["avg_balance"] * n / 60     # equity tied up, averaged over 5 years
        scale.append({"segment": name, "net_per_customer": row["net"], "customers_for_fixed_cost": need, "loans_per_customer_5y": lpc,
                      "equity_per_customer_avg": cap_per_customer})

    # one shopkeeper, worked through: savers repay better, 1 in 5 borrow a year, today's cost to win
    name, seg, T, n, apr, fee = SEGS[2]
    co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in cen.items()}).items()}
    tgt = []
    for case in CASES:
        per = loan(T, n, apr, fee, case)["net"] + 100.0
        r = R.customer(co, {**med, "wc_ticket": T, "wc_fee": per / T, "wc_clawback": 0.0, "wc_loans_year": 0.20}, graduate=True, seg=seg)
        tgt.append({"case": case, "cac": r["cac"], "savings": r["pv_savings"] + r["pv_incentive"], "loans": r["pv_loans"], "other": r["pv_other"],
                    "serve": r["pv_serve"], "net": r["net"], "payback": r["payback"] or "", "still_m12": r["still_m12"]})
    mc.write("lend_target.csv", tgt)
    mc.write("lend_loan.csv", loans)
    mc.write("lend_customer.csv", cust)
    mc.write("lend_scale.csv", scale)
    print()
    for name, *_ in SEGS:
        for cc in ("evidence", "250"):
            print(f"{name} (cost to win: {cc})")
            for pd in CASES:
                vals = [r for r in cust if r["segment"] == name and r["mode"] == "lend" and r["default"] == pd and r["cac_case"] == cc]
                print(f"   lend, {pd:<22}: net per customer " + "  ".join(f"{v['takeup']:.0%}: {v['net']:>6,.0f} (pb {v['payback'] or '-'})" for v in vals))
            vals = [r for r in cust if r["segment"] == name and r["mode"] == "referral" and r["cac_case"] == cc]
            print("   referral:            " + "  ".join(f"{v['takeup']:.0%}: {v['net']:>6,.0f}" for v in vals))
    for s in scale:
        print(s)


if __name__ == "__main__":
    main()

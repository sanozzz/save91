"""Reconcile the two cross-sell numbers (COHORT_RERUN_agreed_2026-10-16.md, section 5):
  - Rs 239: tables/dist_derived_v1.csv `xsell_total`, the p50 of model/dist_proposal.xsell(): money per proven saver a year
    "once holdings settle" (steady-state holders h = t / (1 - r + t), lapsed holders buy again, SIP balances mature, one-off
    products bought every year by t of savers, saver churn not counted).
  - Rs 166: tables/cohort_mc_summary.csv, the p50 of the cohort model's money booked in 60 months / years of savers offered
    the marketplace, over one agent's growing book (holdings start at zero, most savers are young, a holder who stops saving
    lapses, one-off products sold once per saver).
At the likely values, by product: the sheet's settled figure, the cohort model's 60-month book, one cohort's ages 37-60
(holdings have had 3 years to build), and the first-year-only method behind the old Rs 63 (XO-39).
Writes tables/cohort_crosssell_reconcile.csv.
"""
import csv

import cohort_engine as E
import dist_proposal as DP


def main():
    x = E.likely_inputs()
    settled, first = DP.xsell(x), DP.xsell(x, first_year=True)
    res = E.run(x)
    m, p = res["monthly"], res["profile"]
    book_years = m["proven"][0].sum() / 12
    mature = slice(36, 60)
    mature_years = p["proven"][0][mature].sum() / 12
    rows = []
    for pr, kind, nm, _d in E.PRODUCTS:
        rows.append({"product": nm, "kind": kind, "sheet_settled_rs": settled[pr],
                     "cohort_60_month_book_rs": m[f"rev_xs_{pr}"][0].sum() / book_years,
                     "one_cohort_ages_37_60_rs": p[f"rev_xs_{pr}"][0][mature].sum() / mature_years, "first_year_only_rs": first[pr]})
    tot = {k: sum(r[k] for r in rows) for k in ("sheet_settled_rs", "cohort_60_month_book_rs", "one_cohort_ages_37_60_rs", "first_year_only_rs")}
    rows.append({"product": "All 17, at the likely values", "kind": "", **tot})
    der = {r["key"]: r for r in csv.DictReader((E.T / "dist_derived_v1.csv").open())}
    mc = {r["measure"]: r for r in csv.DictReader((E.T / "cohort_mc_summary.csv").open())}
    mc_xs = next(v for k, v in mc.items() if k.startswith("Cross-sell money"))
    rows.append({"product": "All 17, Monte Carlo p50", "kind": "", "sheet_settled_rs": float(der["xsell_total"]["p50"]),
                 "cohort_60_month_book_rs": float(mc_xs["p50"]), "one_cohort_ages_37_60_rs": "",
                 "first_year_only_rs": float(der["xsell_total_first_year"]["p50"]) if "xsell_total_first_year" in der else ""})
    rows.append({"product": "What it measures", "kind": "",
                 "sheet_settled_rs": "a year once holdings settle (steady state; churn ignored; lapsed holders re-buy; one-offs every year)",
                 "cohort_60_month_book_rs": "money booked in months 1-60 / saver-years offered the marketplace (what the NPV contains)",
                 "one_cohort_ages_37_60_rs": "the same model, a saver who has stayed 3+ years",
                 "first_year_only_rs": "take-up x ticket x first-year commission (the method behind the old Rs 63)"})
    E.write("cohort_crosssell_reconcile.csv", rows)
    for r in rows[-3:-1]:
        print(r)


if __name__ == "__main__":
    main()

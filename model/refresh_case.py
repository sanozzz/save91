"""Refresh case, 18 Oct 2026. Writes tables/refresh_*.csv. Does not touch tables/base_*.csv.

Same fleet path as the published base (300 agents by month 18, +150 a month, cap 5,000,
open a city below 25,000 headroom a head). The city search is not re-run: this is the
old operating shape with the inputs the folder can already support.

Changed, because a number exists:
  personal-loan ticket   ₹58,522     XL-29 (CRIF national average). XL-42's ₹25,557 is the
                                     lower segment anchor and is not used here.
  home-loan ticket       ₹11.8 lakh  XL-25 (Home First ATS)
  apply rate             3.6% a year the review's reading of XL-04 (0.93% of Paytm monthly
                                     users are key financial-services customers in a quarter,
                                     times four). It is an annualised stock, not a measured
                                     apply hazard.
  NBFC borrowings        1.16× equity LEV-023 gearing. The old 3× was a choice.
  UPI by month 12        100%        Bachatt conversation (PR-02's sitting; collection note).
                                     Residual cash in smaller cities was not given a share,
                                     so it is not in this run.
  bought-lead cost       ₹300        Saket Khandelwal, both channels (PR-02). This prices
                                     the bought half only. Agent salary is unchanged, and
                                     half of sign-ups are still bought leads, because the
                                     online 1 to 1.5 lakh had no period.

Left as in the published base, because the number was not given:
  ₹350 a day, 55% still saving at month 12, the debt fund at 0.35% and 7%,
  sign-ups per agent, the 5,000-agent cap, on-book share 30% and loss 0.6×.
  No OD++ limit, no wallet balance, no 80/20 trail.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import nbfc as NB                  # noqa: E402
import saturation as S             # noqa: E402
import base_plan as B              # noqa: E402
import unicorn_plan as U           # noqa: E402

CR = C.CRORE
PATH = (300, 150, 5000, 25000.0)     # tables/base_lenses.csv, the published path
LOAN = {"ticket": 58522.0, "loan_home_ticket": 1180000.0, "apply": 0.036}
FULL = {**LOAN, "upi_12": 1.0, "lead_cost": 300.0}


def metrics(of, ct):
    def yr(k):
        return float(of[k][0, 48:60].sum()) / CR
    L = NB.lenses(of, 60)
    be = C.stays_positive_from(of["ebitda"])[0]
    fc = B.first_clear(of)
    return {
        "Year-5 revenue (Rs crore)": yr("revenue"),
        "Year-5 fee revenue (Rs crore)": yr("fee_revenue"),
        "Year-5 net interest (Rs crore)": yr("nbfc_nii"),
        "Year-5 processing fees (Rs crore)": yr("nbfc_processing"),
        "Year-5 EBITDA (Rs crore)": yr("ebitda"),
        "Year-5 EBIT (Rs crore)": yr("ebit"),
        "Year-5 interest on cash (Rs crore)": yr("interest"),
        "Year-5 PAT (Rs crore)": yr("pat"),
        "ARR at m60 (Rs crore)": L["ARR"] / CR,
        "Fee ARR at m60 (Rs crore)": L["Fee ARR"] / CR,
        "AUM at m60 (Rs crore)": L["AUM"] / CR,
        "Lens 1 at m60 (Rs crore)": L["Lens 1 (20 x ARR)"] / CR,
        "Lens 2 at m60 (Rs crore)": L["Lens 2 (0.45 x AUM)"] / CR,
        "Lens 3 at m60 (Rs crore)": L["Lens 3 (3 x NBFC equity + 20 x fee ARR)"] / CR,
        "Active savers at m60 (lakh)": float(of["still_saving"][0, 59]) / 1e5,
        "Loan book at m60, net (Rs crore)": float(of["nbfc_book"][0, 59]) / CR,
        "NBFC equity at m60 (Rs crore)": float(of["nbfc_equity"][0, 59]) / CR,
        "NBFC borrowings at m60 (Rs crore)": float(of["nbfc_borrowings"][0, 59]) / CR,
        "Borrowings / equity at m60": float(of["nbfc_leverage"][0, 59]),
        "Lowest cash (Rs crore)": float(of["cash"][0].min()) / CR,
        "Total raised (Rs crore)": sum(r["Amount"] for r in ct) / CR,
        "EBITDA stays positive from month": "" if np.isnan(be) else int(be),
        "First month lenses 1 and 2 both clear": fc or "not to m96",
        "Rounds": "; ".join(f"{r['Round']} m{r['Month']} Rs {r['Amount'] / CR:,.1f} cr" for r in ct),
    }


def run_case(x0, dists, addr, overrides, leverage):
    x = dict(x0)
    x.update(overrides)
    cfg = {**B.SCcfg(), "leverage": leverage}
    of, seed, rounds, rds, ct, sat, _fl = B.evaluate(x, dists, addr, PATH, cfg=cfg)
    return of, seed, rounds, rds, ct, sat, x, cfg


def write_full(of, seed, rounds, rds, ct, sat, x, cfg, dists, addr):
    C.write("refresh_monthly.csv", B.monthly(of))
    C.write("refresh_yearly.csv", B.yearly(of))
    C.write("refresh_headcount.csv", C.headcount_rows(of))
    C.write("refresh_rounds.csv", __import__("realworld").rounds_rows("Refresh", ct))
    C.write("refresh_city_plan.csv", S.plan_from_auto(
        of, sat, "refresh: the published fleet path, with the 18 Oct input changes. Not a new city search."))
    fc = B.first_clear(of)
    lens_rows = []
    for m in sorted({48, 54, 60, 72, 84, 96} | ({fc} if fc else set())):
        Lm = NB.lenses(of, m)
        lens_rows.append({
            "Month": m,
            "Note": "the month-60 check" if m == 60 else ("first month lenses 1 and 2 both clear" if m == fc else ""),
            **{k: Lm[k] for k in ("ARR", "Fee ARR", "AUM", "NBFC equity", "Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)",
                                  "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
            **{f"{k} margin over $1B": Lm[k] / U.UNICORN - 1 for k in
               ("Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)", "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
            "Lenses 1 and 2 both clear $1B": "yes" if B.clears(of, m) else "no",
            "Fleet path": B.path_text(PATH),
            "Path choice": "the published base path, not re-searched",
            "Basis": "18 Oct refresh. Lens 3 and fee ARR are the figures to read beside lenses 1 and 2.",
        })
    C.write("refresh_lenses.csv", lens_rows)
    ck = B.checks(of, ct, sat, x, cfg)
    # Below the Rs 10 crore NOF the equity sits idle and borrowings are 0, so the average
    # over every lending month is not 1.16x. The multiple applies once the book exceeds NOF.
    nof = 10 * CR
    big = of["nbfc_book"][0] > nof
    lev_big = of["nbfc_leverage"][0][big]
    ck.append({"Check": "Borrowings / equity is 1.16x once the book exceeds the Rs 10 crore NOF",
               "Passes": bool(big.any() and np.allclose(lev_big, 1.16, atol=0.01)),
               "Note": f"at m60 {float(of['nbfc_leverage'][0, 59]):.3f}x. Months under the NOF hold equity idle and borrowings at 0."})
    C.write("refresh_checks.csv", ck)
    print(f"  checks {sum(c['Passes'] for c in ck)}/{len(ck)}", flush=True)
    bad = [c["Check"] for c in ck if not c["Passes"]]
    if bad:
        print("  FAIL:", bad, flush=True)
    print("  MC starting", flush=True)
    pinned = dict(dists)
    for k, v in FULL.items():
        sh, _lo, _li, _hi, src = pinned[k]
        pinned[k] = (sh, v, v, v, src)
    C.write("refresh_mc_summary.csv", B.mc(pinned, addr, PATH, seed["Amount"], rds, cfg))


def main():
    dists = E.load_dists()[0]
    x0 = E.likely_inputs(dists)
    _q, share = S.city_curve()
    addr = share[:S.CLASS_I] * S.POOL
    C.set_horizon(B.HORIZON)
    cases = [
        ("Published path, old inputs", {}, 3.0),
        ("Loans and leverage only", LOAN, 1.16),
        ("Loans, leverage, UPI 100%", {**LOAN, "upi_12": 1.0}, 1.16),
        ("Refresh", FULL, 1.16),
    ]
    rows, last = [], None
    for name, over, lev in cases:
        print(f"running {name}", flush=True)
        of, seed, rounds, rds, ct, sat, x, cfg = run_case(x0, dists, addr, over, lev)
        row = {"Case": name, **metrics(of, ct)}
        rows.append(row)
        print(f"  Y5 revenue {row['Year-5 revenue (Rs crore)']:.2f} cr | EBITDA {row['Year-5 EBITDA (Rs crore)']:.2f} | "
              f"PAT {row['Year-5 PAT (Rs crore)']:.2f} | lens1 {row['Lens 1 at m60 (Rs crore)']:.0f} | "
              f"lens2 {row['Lens 2 at m60 (Rs crore)']:.0f} | lens3 {row['Lens 3 at m60 (Rs crore)']:.0f} | "
              f"raised {row['Total raised (Rs crore)']:.0f} | cash low {row['Lowest cash (Rs crore)']:.2f}", flush=True)
        last = (of, seed, rounds, rds, ct, sat, x, cfg)
    C.write("refresh_bridge.csv", rows)
    write_full(*last, dists, addr)
    C.set_horizon(60)
    print("wrote tables/refresh_*", flush=True)


if __name__ == "__main__":
    main()

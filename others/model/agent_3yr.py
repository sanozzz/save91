"""One street agent over three years (operator, 16 Oct 2026): "assume they are able to service and acquire
1000 users in a year and they are able to go up to 3K in total in 3 years. they do 2-3 days in collection".

Read as: the agent signs 1,000 savers a year, spread evenly over the months, for 3 years; he collects from
each saver every 2-3 days (2.5 on average) instead of daily; a saver still puts in Rs 350 a day, collected
less often. Two views of who stays:
  all_stay   the operator's assumption: every saver keeps saving (book 1,000 / 2,000 / 3,000)
  evidence   our model's retention curve at today's evidence (engine.survival, shopkeepers): 24 of 100
             still saving after 12 months
Costs and revenues as in model/invert_deposit_cost.py (same evidence rows). Writes tables/agent3_monthly.csv,
tables/agent3_years.csv.
"""
import csv
from pathlib import Path

import numpy as np

import engine as E
import mc
import redesign as R

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
AGENT = 400000.0            # Rs a year (operator)
SIGNUPS = 1000.0            # a year (operator)
YEARS = 3
EVERY = 2.5                 # days between collections (operator: 2-3)
CAPACITY = 400              # collections one person makes a day: top of Arvinder's 200-400 book (interview)
DAYS_M = 20                 # deposit days a month (240 a year, as before)
DAILY = (350.0, 100.0)      # Rs a day: Arvinder's middle customer; our model's saver
TRAIL, HOLD = 0.0035, 0.5   # XB-04 middle; average balance = half a year's deposits (yearly terms, as janta deposits)
OTHER = 63.0                # XO-39 middle, Rs per active saver a year
REFER = 150000 * 0.02 * (1 - 0.025)                                   # XL-13, as invert_deposit_cost
LEND = next(float(r["net"]) for r in csv.DictReader((T / "lend_loan.csv").open())
            if r["segment"] == "Shopkeepers" and r["case"] == "industry steady state")
EVIDENCE_LOANS = 0.03       # XL-48 middle: approved loans per active saver a year
# operator, 16 Oct 2026: "the pool we have can get an avg loan of 2.5 lacs and credit card ... 5% of the savers;
# we get 1% of the loan origination fee from our lender"
LOAN25, FEE25 = 250000.0, 0.01          # Rs 2,500 a loan; no clawback stated (lenders often take it back if a loan closes or defaults in 6 months, XL-13)
CARD_SHARE = 0.05                       # of each year's sign-ups, one card each, paid once
CARD_FEE = (500.0, 1250.0, 2000.0)      # BM-08: Rs 500-2,000 per approved card (affiliate guides; unverified)
INCOME = (20000.0, 40000.0)             # Arvinder's customers earn Rs 20-40k a month (interview, 15 Oct 2026)
FOIR = 0.5                              # lenders' 50% rule: instalments up to half of income (SG-22, SG-14)
JANTA_CHURN = (10 / 200, 8 / 300, 6 / 400)   # share of a janta book leaving each month: worst / middle / best
PROVEN_AFTER = 6                        # months of saving before we offer a loan (redesign.LOAN_START)
# loan funnel, per proven saver per year: low / mid / high (judgement ranges anchored on the evidence named)
ELIGIBLE = (0.30, 0.50, 0.70)   # can carry a Rs 2.5 lakh EMI: 36-month EMI Rs 10,073 fits the 50% rule above Rs 20,146 income;
                                # his customers earn Rs 20-40k; 41% of small-business borrowers already carry a loan (XB-09); thin files rarely get 2.5 lakh unsecured
APPLY = (0.10, 0.20, 0.35)      # want a loan this year: Kissht 17.5% of registered ever borrowed (XL-42); Brazil payroll 20% in year one (LS-06);
                                # the founder expects 35% (deck's 35% case); Paytm ~3.7% of users a year take a financial product (XL-04)
APPROVE = (0.15, 0.25, 0.40)    # lender says yes: the founder's past lending data 25%
CLAWBACK = (0.05, 0.025, 0.0)   # share of fees taken back when loans close or default in 6 months (XL-13; model 2.5%)
TRAIL3 = (0.002, 0.0035, 0.005) # XB-04
OTHER3 = (8.0, 63.0, 259.0)     # XO-39


def survival_curve(months):
    """Share of a cohort still saving in month t = 1..months, at today's evidence (shopkeepers)."""
    dists = mc.load_dists()
    cen = mc.centre(dists)
    co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in cen.items()}).items()}
    p = E.load_inputs("base", R.design_overrides(co), "ng")
    return [E.survival(p, t) for t in range(1, months + 1)]


def main():
    n = 12 * YEARS
    # janta-like: Arvinder's book gains 6-10 and loses 6-10 a month on 200-400 customers (interview, 15 Oct 2026);
    # a steady monthly loss of 8 / 300 (middle; 10 / 200 worst, 6 / 400 best), applied to every saver from month 1
    surv = {"all_stay": [1.0] * n, "janta": [(1 - JANTA_CHURN[1]) ** t for t in range(1, n + 1)], "evidence": survival_curve(n)}
    per_month = SIGNUPS / 12
    monthly, years = [], []
    for view, s in surv.items():
        active = [sum(per_month * s[t - m] for m in range(t + 1)) for t in range(n)]       # cohort m joins in month m
        proven = [sum(per_month * s[t - m] for m in range(t + 1) if t - m + 1 > PROVEN_AFTER) for t in range(n)]
        for t in range(n):
            monthly.append({"view": view, "month": t + 1, "signed_to_date": per_month * (t + 1), "active": active[t], "proven": proven[t],
                            "collections_a_day": active[t] / EVERY})
        for y in range(YEARS):
            sl = active[12 * y: 12 * (y + 1)]
            saver_years = sum(sl) / 12
            end = sl[-1]
            row = {"view": view, "year": y + 1, "signed": SIGNUPS, "active_end": end, "saver_years": saver_years,
                   "proven_saver_years": sum(proven[12 * y: 12 * (y + 1)]) / 12,
                   "collections_a_day_end": end / EVERY, "upi_share_needed_end": max(0.0, 1 - CAPACITY * EVERY / end) if end else 0.0}
            for d in DAILY:
                dep = saver_years * d * DAYS_M * 12
                paid = TRAIL * HOLD * dep + OTHER * saver_years
                gap = AGENT - paid
                tag = f"_{d:.0f}"
                row.update({f"deposits{tag}": dep, f"cost_pct{tag}": AGENT / dep, f"fund{tag}": TRAIL * HOLD * dep, f"other{tag}": OTHER * saver_years,
                            f"paid_back{tag}": paid, f"gap{tag}": gap,
                            f"refer_loans{tag}": max(gap, 0) / REFER, f"lend_loans{tag}": max(gap, 0) / LEND,
                            f"refer_per_saver{tag}": max(gap, 0) / REFER / saver_years, f"lend_per_saver{tag}": max(gap, 0) / LEND / saver_years})
            years.append(row)
        # three-year total
        tot = {"view": view, "year": "1-3", "signed": SIGNUPS * YEARS, "active_end": years[-1]["active_end"],
               "saver_years": sum(r["saver_years"] for r in years if r["view"] == view),
               "proven_saver_years": sum(r["proven_saver_years"] for r in years if r["view"] == view),
               "collections_a_day_end": years[-1]["collections_a_day_end"], "upi_share_needed_end": years[-1]["upi_share_needed_end"]}
        for d in DAILY:
            tag = f"_{d:.0f}"
            rs = [r for r in years if r["view"] == view and r["year"] != "1-3"]
            dep = sum(r[f"deposits{tag}"] for r in rs)
            paid = sum(r[f"paid_back{tag}"] for r in rs)
            gap = AGENT * YEARS - paid
            tot.update({f"deposits{tag}": dep, f"cost_pct{tag}": AGENT * YEARS / dep, f"fund{tag}": sum(r[f"fund{tag}"] for r in rs),
                        f"other{tag}": sum(r[f"other{tag}"] for r in rs), f"paid_back{tag}": paid, f"gap{tag}": gap,
                        f"refer_loans{tag}": max(gap, 0) / REFER, f"lend_loans{tag}": max(gap, 0) / LEND,
                        f"refer_per_saver{tag}": max(gap, 0) / REFER / tot["saver_years"], f"lend_per_saver{tag}": max(gap, 0) / LEND / tot["saver_years"]})
        years.append(tot)
    loans25 = []
    for r in years:
        cards = CARD_SHARE * r["signed"]
        row = {"view": r["view"], "year": r["year"], "saver_years": r["saver_years"], "active_end": r["active_end"], "cards": cards}
        for i, k in enumerate(("low", "mid", "high")):
            gap = r["gap_350"] - cards * CARD_FEE[i]
            row[f"card_income_{k}"] = cards * CARD_FEE[i]
            row[f"gap_after_cards_{k}"] = gap
            row[f"loans_{k}"] = max(gap, 0) / (LOAN25 * FEE25)
            row[f"loans_per_saver_{k}"] = max(gap, 0) / (LOAN25 * FEE25) / r["saver_years"]
        row["loan_value_mid"] = row["loans_mid"] * LOAN25
        row["gap_before_cards"] = r["gap_350"]
        loans25.append(row)
    emi = []
    for n in (12, 24, 36):
        i = 0.26 / 12
        e = LOAN25 * i / (1 - (1 + i) ** -n)
        emi.append({"months": n, "emi": e, "times_monthly_saving": e / (DAILY[0] * DAYS_M),
                    "share_of_income_low": e / INCOME[1], "share_of_income_high": e / INCOME[0],
                    "fits_50pct_rule_at_20k": e <= FOIR * INCOME[0], "fits_50pct_rule_at_40k": e <= FOIR * INCOME[1]})
    funnel = []
    for r in years:
        row = {"view": r["view"], "year": r["year"], "signed": r["signed"], "saver_years": r["saver_years"], "proven_saver_years": r["proven_saver_years"]}
        dep = r["deposits_350"]
        cost = AGENT * (YEARS if r["year"] == "1-3" else 1)
        for i, k in enumerate(("low", "mid", "high")):
            rate = ELIGIBLE[i] * APPLY[i] * APPROVE[i]
            loans = r["proven_saver_years"] * rate
            per_loan = LOAN25 * FEE25 * (1 - CLAWBACK[i])
            cards = CARD_SHARE * r["signed"]
            parts = {"fund": TRAIL3[i] * HOLD * dep, "other": OTHER3[i] * r["saver_years"], "cards": cards * CARD_FEE[i], "loanfees": loans * per_loan}
            total = sum(parts.values())
            needed = max(cost - (total - parts["loanfees"]), 0) / per_loan
            row.update({f"loan_rate_{k}": rate, f"loans_{k}": loans, f"loans_needed_{k}": needed, f"per_loan_{k}": per_loan,
                        **{f"{p}_{k}": v for p, v in parts.items()}, f"income_{k}": total, f"result_{k}": total - cost,
                        f"covered_{k}": total / cost, f"loan_value_{k}": loans * LOAN25,
                        f"affordable_agent_cost_a_year_{k}": total / (YEARS if r["year"] == "1-3" else 1)})
        funnel.append(row)
    with (T / "agent3_funnel.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(funnel[0]))
        w.writeheader()
        w.writerows(funnel)
    with (T / "agent3_funnel_inputs.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "low", "mid", "high", "basis"])
        w.writerow(["proven saver: saving 6+ months and still saving", "", "", "", "redesign.LOAN_START; retention curve"])
        w.writerow(["can carry a Rs 2.5 lakh EMI (eligible)", *ELIGIBLE, "36-month EMI Rs 10,073 needs about Rs 20,145+ income at the 50% rule; customers earn Rs 20-40k; 41% already have a loan (XB-09)"])
        w.writerow(["applies in a year", *APPLY, "Kissht 17.5% ever borrowed (XL-42); Brazil payroll 20% year one (LS-06); founder 35%; Paytm ~3.7% a year (XL-04)"])
        w.writerow(["lender approves", *APPROVE, "founder's past lending data: 25%"])
        w.writerow(["approved loans per proven saver a year", *(ELIGIBLE[i] * APPLY[i] * APPROVE[i] for i in range(3)), "product of the three; evidence middle 3% (XL-48)"])
        w.writerow(["fee kept per loan (Rs)", *(LOAN25 * FEE25 * (1 - CLAWBACK[i]) for i in range(3)), "1% of Rs 2.5 lakh, less 5% / 2.5% / 0% taken back (XL-13)"])
        w.writerow(["credit cards (share of sign-ups, once)", CARD_SHARE, CARD_SHARE, CARD_SHARE, "operator: 5% of savers"])
        w.writerow(["card fee (Rs)", *CARD_FEE, "BM-08: Rs 500-2,000 per approved card (unverified)"])
    for r in funnel:
        print(f"{r['view']:<9} Y{r['year']:<4} proven-yrs {r['proven_saver_years']:>6,.0f} | loans L/M/H {r['loans_low']:>4.0f}/{r['loans_mid']:>4.0f}/{r['loans_high']:>4.0f} "
              f"needed M {r['loans_needed_mid']:>4.0f} | income M {r['income_mid']:>9,.0f} result L/M/H {r['result_low']:>10,.0f}/{r['result_mid']:>10,.0f}/{r['result_high']:>10,.0f} "
              f"covered M {r['covered_mid']:.0%}")
    # the retention at which one agent breaks even over 3 years (middle case, Rs 350 a day): blend the evidence curve
    # towards "everyone stays" by a share alpha, find alpha where income = cost
    ev = surv["evidence"]
    def three_year(alpha):
        sc = [e + alpha * (1 - e) for e in ev]
        act = [sum(per_month * sc[t - m] for m in range(t + 1)) for t in range(n)]
        prov = [sum(per_month * sc[t - m] for m in range(t + 1) if t - m + 1 > PROVEN_AFTER) for t in range(n)]
        sy, py = sum(act) / 12, sum(prov) / 12
        dep = sy * DAILY[0] * DAYS_M * 12
        inc = (TRAIL3[1] * HOLD * dep + OTHER3[1] * sy + CARD_SHARE * SIGNUPS * YEARS * CARD_FEE[1]
               + py * ELIGIBLE[1] * APPLY[1] * APPROVE[1] * LOAN25 * FEE25 * (1 - CLAWBACK[1]))
        return inc - AGENT * YEARS, sc, act
    lo_a, hi_a = 0.0, 1.0
    for _ in range(60):
        mid_a = (lo_a + hi_a) / 2
        if three_year(mid_a)[0] < 0:
            lo_a = mid_a
        else:
            hi_a = mid_a
    _, sc, act = three_year(hi_a)
    be = [{"alpha": hi_a, "still_saving_m12": sc[11], "still_saving_m24": sc[23], "still_saving_m36": sc[35], "active_end": act[-1],
           "evidence_m12": ev[11], "evidence_m24": ev[23], "evidence_m36": ev[35]}]
    with (T / "agent3_breakeven.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(be[0]))
        w.writeheader()
        w.writerows(be)
    with (T / "agent3_survival.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "still_saving_evidence", "still_saving_breakeven", "still_saving_janta_mid", "still_saving_janta_worst", "still_saving_janta_best"])
        for t in range(n):
            w.writerow([t + 1, ev[t], sc[t], *((1 - c) ** (t + 1) for c in (JANTA_CHURN[1], JANTA_CHURN[0], JANTA_CHURN[2]))])
    print(f"BREAK-EVEN retention: {sc[11]:.1%} still saving at 12 months ({sc[23]:.1%} at 24, {sc[35]:.1%} at 36), active end {act[-1]:,.0f}; "
          f"evidence {ev[11]:.1%}/{ev[23]:.1%}/{ev[35]:.1%}; month 1/3/6 evidence {ev[0]:.1%}/{ev[2]:.1%}/{ev[5]:.1%}")
    for name, rows in (("agent3_loans25.csv", loans25), ("agent3_emi.csv", emi)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    for r in loans25:
        print(f"{r['view']:<9} Y{r['year']:<4} gap {r['gap_before_cards']:>10,.0f} cards {r['cards']:.0f} x1,250 = {r['card_income_mid']:>8,.0f} -> gap {r['gap_after_cards_mid']:>10,.0f} "
              f"-> {r['loans_mid']:>5.0f} loans of 2.5L ({r['loans_per_saver_mid']:.3f}/saver-yr) [card fee 500: {r['loans_low']:.0f}, 2000: {r['loans_high']:.0f}]")
    for e in emi:
        print(f"EMI {e['months']}m {e['emi']:,.0f} = {e['times_monthly_saving']:.1f}x saving, {e['share_of_income_low']:.0%}-{e['share_of_income_high']:.0%} of income")
    for name, rows in (("agent3_monthly.csv", monthly), ("agent3_years.csv", years)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"evidence survival: m12 {surv['evidence'][11]:.3f}, m24 {surv['evidence'][23]:.3f}, m36 {surv['evidence'][35]:.3f}")
    for r in years:
        print(f"{r['view']:<9} Y{r['year']:<4} active end {r['active_end']:>6,.0f} saver-yrs {r['saver_years']:>6,.0f} "
              f"collect/day {r['collections_a_day_end']:>5,.0f} UPI needed {r['upi_share_needed_end']:.0%} | Rs350: dep {r['deposits_350'] / 1e7:5.2f} cr "
              f"cost {r['cost_pct_350']:.2%} paid {r['paid_back_350']:>9,.0f} gap {r['gap_350']:>10,.0f} refer {r['refer_loans_350']:>5.0f} "
              f"({r['refer_per_saver_350']:.3f}/saver) lend {r['lend_loans_350']:>4.0f} ({r['lend_per_saver_350']:.3f}) | Rs100: cost {r['cost_pct_100']:.2%} "
              f"gap {r['gap_100']:>10,.0f} refer/saver {r['refer_per_saver_100']:.3f} lend/saver {r['lend_per_saver_100']:.3f}")


if __name__ == "__main__":
    main()

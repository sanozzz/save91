"""Stress test of the offline model (operator, 16 Oct 2026):
  1. fleet guy salary: Rs 20,000 a month + 1% of savings
  2. key assumption = retention: bear 30-40% still saving after 12 months, best 70% (like janta deposit); other assumptions too

Agent pay, read two ways (the operator wrote "1% of savings"):
  collected   1% of every rupee he collects (janta-style commission on collections)   <- main reading
  balance     1% a year of the balance his savers hold (asset-based)                  <- alternative
Retention: still saving after 12 months = R12; a steady monthly drop-off c = 1 - R12^(1/12) (the same every month, as the
janta book: 8 of 300 a month gives 72% at 12 months). R12 tested: 30, 40 (bear), 55 (our middle), 70 (best).
Everything else as in model/agent_3yr.py, with low / middle / high values (see INPUTS). One agent, 3 years, 1,000
sign-ups a year joining at the start of each month; per customer won, his first 36 months.
Writes tables/scn_inputs.csv, scn_retention.csv, scn_oneway.csv, scn_combined.csv, scn_breakeven.csv, scn_customer.csv.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
YEARS, N_MONTHS, DAYS_M, HOLD, PROVEN, EVERY, CAPACITY = 3, 36, 20, 0.5, 6, 2.5, 400
FIXED_PAY = 20000.0 * 12            # Rs a year (operator)
COMMISSION = 0.01                   # 1% of savings (operator)
LOAN, FEE = 250000.0, 0.01          # operator: average loan Rs 2.5 lakh, 1% origination fee to us
CARD_SHARE = 0.05                   # operator: 5% of savers get a card

INPUTS = {  # name: (low, middle, high, basis)
    "daily": (200.0, 350.0, 500.0, "Rs a day per saver: Arvinder's customers Rs 200-500 (interview, 15 Oct 2026)"),
    "signups": (750.0, 1000.0, 1250.0, "sign-ups per agent a year: operator 1,000; +/-25% is our range"),
    "trail": (0.002, 0.0035, 0.005, "fund commission a year on the balance (XB-04)"),
    "other": (8.0, 63.0, 259.0, "other products, Rs per saver a year (XO-39)"),
    "card_fee": (500.0, 1250.0, 2000.0, "Rs per card, 5% of sign-ups (BM-08, unverified)"),
    "loan_rate": (0.0045, 0.025, 0.098, "loans per proven saver a year: eligible x apply x approved (tables/agent3_funnel_inputs.csv)"),
    "clawback": (0.05, 0.025, 0.0, "share of loan fees taken back (XL-13)"),
}
R12S = (0.30, 0.40, 0.55, 0.70)
ONLINE_CAC = (186.0, 499.2394, 1340.0)          # tables/distributions.csv cac_target@ng
ONLINE_R12 = 0.2415                             # our model's evidence (tables/agent3_survival.csv, month 12)


def mid(name):
    return INPUTS[name][1]


def run(r12, pay="collected", commission=COMMISSION, **over):
    x = {k: v[1] for k, v in INPUTS.items()}
    x.update(over)
    c = 1 - r12 ** (1 / 12)
    surv = [(1 - c) ** t for t in range(1, N_MONTHS + 1)]
    per_month = x["signups"] / 12
    active = [sum(per_month * surv[t - m] for m in range(t + 1)) for t in range(N_MONTHS)]
    proven = [sum(per_month * surv[t - m] for m in range(t + 1) if t - m + 1 > PROVEN) for t in range(N_MONTHS)]
    per_loan = LOAN * FEE * (1 - x["clawback"])
    years = []
    for y in range(YEARS):
        act = active[12 * y: 12 * (y + 1)]
        sy, py = sum(act) / 12, sum(proven[12 * y: 12 * (y + 1)]) / 12
        dep = sy * x["daily"] * DAYS_M * 12
        bal = HOLD * dep
        comm = commission * (dep if pay == "collected" else bal)
        cost = FIXED_PAY + comm
        inc = {"fund": x["trail"] * bal, "other": x["other"] * sy, "cards": CARD_SHARE * x["signups"] * x["card_fee"], "loans": py * x["loan_rate"] * per_loan}
        years.append({"year": y + 1, "saver_years": sy, "proven_saver_years": py, "active_end": act[-1], "deposits": dep, "commission": comm,
                      "cost": cost, "income": sum(inc.values()), **inc, "result": sum(inc.values()) - cost,
                      "collections_a_day_end": act[-1] / EVERY, "upi_needed_end": max(0.0, 1 - CAPACITY * EVERY / act[-1]) if act[-1] else 0.0})
    tot = {k: sum(r[k] for r in years) for k in ("saver_years", "proven_saver_years", "deposits", "commission", "cost", "income", "fund", "other", "cards", "loans", "result")}
    tot.update({"active_end": years[-1]["active_end"], "covered": tot["income"] / tot["cost"], "cost_pct_of_deposits": tot["cost"] / tot["deposits"]})
    # one customer won, his first 36 months
    sm = sum(surv)
    cust_dep = sm * x["daily"] * DAYS_M
    cust_comm = commission * (cust_dep if pay == "collected" else HOLD * cust_dep)
    cust_inc = x["trail"] * HOLD * cust_dep + x["other"] * sm / 12 + CARD_SHARE * x["card_fee"] + sum(surv[PROVEN:]) / 12 * x["loan_rate"] * per_loan
    cac = FIXED_PAY / x["signups"]
    return years, tot, {"cost_to_win": cac, "saver_months": sm, "deposits": cust_dep, "commission": cust_comm, "income": cust_inc,
                        "net": cust_inc - cust_comm - cac, "income_per_saver_year": cust_inc / (sm / 12), "commission_per_saver_year": cust_comm / (sm / 12)}


def breakeven_commission(r12, pay="collected", **over):
    lo, hi = 0.0, 0.05
    for _ in range(60):
        m = (lo + hi) / 2
        if run(r12, pay, m, **over)[1]["result"] > 0:
            lo = m
        else:
            hi = m
    return lo


def main():
    with (T / "scn_inputs.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["input", "low", "middle", "high", "basis"])
        w.writerow(["still saving after 12 months", "30% / 40% (bear)", "55% (our middle)", "70% (best, janta-like)", "operator, 16 Oct 2026; steady monthly drop-off"])
        w.writerow(["agent pay", "", "Rs 20,000 a month + 1% of savings", "", "operator, 16 Oct 2026"])
        for k, (lo, m, hi, b) in INPUTS.items():
            w.writerow([k, lo, m, hi, b])

    ret = []
    for pay in ("collected", "balance", "none"):
        for r in R12S:
            ys, t, cu = run(r, "collected", 0.0) if pay == "none" else run(r, pay)
            ret.append({"pay": pay, "r12": r, **{f"y{y['year']}_result": y["result"] for y in ys}, **{f"tot_{k}": v for k, v in t.items()},
                        **{f"cust_{k}": v for k, v in cu.items()}})
    mid_r = 0.55
    oneway = []
    base = run(mid_r)[1]["result"]
    for k in INPUTS:
        lo, hi = run(mid_r, **{k: INPUTS[k][0]})[1]["result"], run(mid_r, **{k: INPUTS[k][2]})[1]["result"]
        oneway.append({"input": k, "low_value": INPUTS[k][0], "high_value": INPUTS[k][2], "result_at_low": lo, "result_at_high": hi, "base_result": base, "swing": abs(hi - lo)})
    for r in R12S:
        pass
    lo_r, hi_r = run(0.30)[1]["result"], run(0.70)[1]["result"]
    oneway.append({"input": "r12", "low_value": 0.30, "high_value": 0.70, "result_at_low": lo_r, "result_at_high": hi_r, "base_result": base, "swing": abs(hi_r - lo_r)})
    for pay_variant, kwargs in (("pay: 1% a year of balance", {"pay": "balance"}), ("pay: no commission", {"commission": 0.0})):
        v = run(mid_r, **kwargs)[1]["result"]
        oneway.append({"input": pay_variant, "low_value": "", "high_value": "", "result_at_low": v, "result_at_high": v, "base_result": base, "swing": abs(v - base)})
    oneway.sort(key=lambda r: -r["swing"])

    low = {k: v[0] for k, v in INPUTS.items()}
    high = {k: v[2] for k, v in INPUTS.items()}
    combos = [("All bad", 0.30, low), ("Bear retention, rest middle", 0.40, {}), ("Middle", 0.55, {}),
              ("Best retention, rest middle", 0.70, {}), ("All good", 0.70, high)]
    comb = []
    for name, r, over in combos:
        ys, t, cu = run(r, **over)
        comb.append({"case": name, "r12": r, **{f"y{y['year']}_result": y["result"] for y in ys}, **{f"tot_{k}": v for k, v in t.items()},
                     **{f"cust_{k}": v for k, v in cu.items()}, "max_commission_collected": breakeven_commission(r, **over)})
    be = [{"r12": r, "max_commission_on_collections": breakeven_commission(r), "max_commission_on_balance": breakeven_commission(r, "balance"),
           "max_commission_on_collections_paytm_fee": breakeven_commission(r, FEE_X=None) if False else None} for r in R12S]
    for b in be:
        b.pop("max_commission_on_collections_paytm_fee")
    cust = []
    for name, cac, r12 in (("online", ONLINE_CAC[1], ONLINE_R12), ("street_30", None, 0.30), ("street_40", None, 0.40), ("street_55", None, 0.55), ("street_70", None, 0.70)):
        _, _, cu = run(r12)
        if cac is not None:
            cu = {**cu, "cost_to_win": cac, "commission": 0.0, "net": cu["income"] - cac, "commission_per_saver_year": 0.0}
        cust.append({"channel": name, "r12": r12, **cu})

    # the same tests with the agent on salary only (no commission on savings)
    base_f = run(mid_r, commission=0.0)[1]["result"]
    oneway_f = []
    for k in INPUTS:
        lo, hi = run(mid_r, commission=0.0, **{k: INPUTS[k][0]})[1]["result"], run(mid_r, commission=0.0, **{k: INPUTS[k][2]})[1]["result"]
        oneway_f.append({"input": k, "low_value": INPUTS[k][0], "high_value": INPUTS[k][2], "result_at_low": lo, "result_at_high": hi, "base_result": base_f, "swing": abs(hi - lo)})
    lo_r, hi_r = run(0.30, commission=0.0)[1]["result"], run(0.70, commission=0.0)[1]["result"]
    oneway_f.append({"input": "r12", "low_value": 0.30, "high_value": 0.70, "result_at_low": lo_r, "result_at_high": hi_r, "base_result": base_f, "swing": abs(hi_r - lo_r)})
    oneway_f.sort(key=lambda r: -r["swing"])
    comb_f = []
    for name, r, over in combos:
        ys, t, cu = run(r, commission=0.0, **over)
        comb_f.append({"case": name, "r12": r, **{f"y{y['year']}_result": y["result"] for y in ys}, **{f"tot_{k}": v for k, v in t.items()},
                       **{f"cust_{k}": v for k, v in cu.items()}})
    # exact retention at which a salaried agent breaks even over 3 years, and the visit load / UPI share by retention
    def be_r12(**kw):
        lo, hi = 0.05, 0.95
        for _ in range(60):
            m = (lo + hi) / 2
            if run(m, commission=0.0, **kw)[1]["result"] < 0:
                lo = m
            else:
                hi = m
        return hi
    global FEE
    fee0 = FEE
    sal = []
    for r in R12S:
        ys, t, cu = run(r, commission=0.0)
        FEE = 0.045
        ys_p, t_p, cu_p = run(r, commission=0.0)
        FEE = fee0
        sal.append({"r12": r, "result_1pct_fee": t["result"], "covered_1pct_fee": t["covered"], "result_paytm_fee": t_p["result"], "covered_paytm_fee": t_p["covered"],
                    "savers_end_y3": ys[2]["active_end"], "collections_a_day_end_y3": ys[2]["collections_a_day_end"], "upi_needed_end_y3": ys[2]["upi_needed_end"],
                    "cust_net_1pct_fee": cu["net"], "cust_net_paytm_fee": cu_p["net"]})
    FEE = 0.045
    be_p = be_r12()
    FEE = fee0
    be_s = be_r12()
    with (T / "scn_salary_summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sal[0]))
        w.writeheader()
        w.writerows(sal)
    with (T / "scn_salary_breakeven.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value", "from"])
        w.writerow(["breakeven_r12_salary_1pct_fee", be_s, "still saving after 12 months at which one salaried agent breaks even over 3 years, middle inputs"])
        w.writerow(["breakeven_r12_salary_paytm_fee", be_p, "the same with a Paytm-like 4.5% loan fee"])
    print(f"SALARY break-even still saving at 12 months: {be_s:.1%} (1% loan fee), {be_p:.1%} (4.5% loan fee)")
    for x in sal:
        print(f"  R12 {x['r12']:.0%}: 1% fee {x['result_1pct_fee']:>10,.0f} ({x['covered_1pct_fee']:.0%}) | 4.5% fee {x['result_paytm_fee']:>10,.0f} ({x['covered_paytm_fee']:.0%}) | "
              f"savers y3 {x['savers_end_y3']:,.0f}, collections/day {x['collections_a_day_end_y3']:.0f}, UPI needed {x['upi_needed_end_y3']:.0%}")
    for name, rows in (("scn_oneway_salary.csv", oneway_f), ("scn_combined_salary.csv", comb_f)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print("SALARY ONLY: ONE AT A TIME (R12 55%)")
    for o in oneway_f:
        print(f"  {o['input']:<10} low {o['result_at_low']:>10,.0f} high {o['result_at_high']:>10,.0f} swing {o['swing']:>9,.0f}")
    print("SALARY ONLY: COMBINED")
    for c in comb_f:
        print(f"  {c['case']:<30} R12 {c['r12']:.0%}: 3y {c['tot_result']:>10,.0f} covered {c['tot_covered']:.0%} y1/y2/y3 {c['y1_result']:,.0f}/{c['y2_result']:,.0f}/{c['y3_result']:,.0f} cust net {c['cust_net']:,.0f}")
    for name, rows in (("scn_retention.csv", ret), ("scn_oneway.csv", oneway), ("scn_combined.csv", comb), ("scn_breakeven.csv", be), ("scn_customer.csv", cust)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    print("RETENTION SWEEP (agent, 3 years, middle other inputs)")
    for r in ret:
        print(f"  pay={r['pay']:<9} R12 {r['r12']:.0%}: income {r['tot_income']:>10,.0f} cost {r['tot_cost']:>10,.0f} (commission {r['tot_commission']:>9,.0f}) "
              f"result {r['tot_result']:>11,.0f} covered {r['tot_covered']:.0%} | savers end {r['tot_active_end']:>5,.0f} | per customer: income {r['cust_income']:>6,.0f} "
              f"commission {r['cust_commission']:>6,.0f} CAC {r['cust_cost_to_win']:.0f} net {r['cust_net']:>7,.0f} | per saver-yr income {r['cust_income_per_saver_year']:.0f} vs commission {r['cust_commission_per_saver_year']:.0f}")
    print("ONE AT A TIME (R12 55%), 3-year result")
    for o in oneway:
        print(f"  {o['input']:<28} low {o['result_at_low']:>11,.0f} high {o['result_at_high']:>11,.0f} swing {o['swing']:>10,.0f}")
    print("COMBINED")
    for c in comb:
        print(f"  {c['case']:<30} R12 {c['r12']:.0%}: result {c['tot_result']:>11,.0f} covered {c['tot_covered']:.0%} y1/y2/y3 {c['y1_result']:,.0f}/{c['y2_result']:,.0f}/{c['y3_result']:,.0f} "
              f"| max commission on collections {c['max_commission_collected']:.3%}")
    print("MAX COMMISSION the business can pay (middle other inputs)")
    for b in be:
        print(f"  R12 {b['r12']:.0%}: on collections {b['max_commission_on_collections']:.3%}, on balance {b['max_commission_on_balance']:.3%} a year")
    print("PER CUSTOMER WON")
    for c in cust:
        print(f"  {c['channel']:<10} R12 {c['r12']:.0%}: cost to win {c['cost_to_win']:>6,.0f} income {c['income']:>6,.0f} commission {c['commission']:>6,.0f} net {c['net']:>7,.0f}")


if __name__ == "__main__":
    main()

"""Invert the question (operator, 16 Oct 2026): if collecting deposits costs Bachatt 1.5% of the money
deposited, how much must each saver buy (loans, insurance, ...) to pay for it?

Everything is per ACTIVE saver per year unless a row says otherwise. Inputs are evidence rows already in
research/ (ids in each row) and our own model tables (tables/lend_loan.csv, lend_funnel.csv,
lend_breakeven.csv). Writes tables/invert_units.csv, invert_stack.csv, invert_sized.csv, invert_notes.csv.

Assumptions that are ours, not evidence:
  COST = 1.5% of money deposited (the operator's premise)
  DEBITS = 240 successful daily debits a year: Bachatt's 2M fund purchases in Feb 2026 / ~1 lakh daily
           savers = ~20 a month (our estimate, janta_pipe/storyline.md B1)
  HOLD = 0.5: average balance in year one = half the year's deposits (nothing withdrawn); a liquid fund
         can be emptied any day, so this is generous
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
COST, DEBITS, HOLD = 0.015, 240, 0.5
SIZES = [("Bachatt minimum", 51.0), ("our model saver", 100.0), ("Arvinder's middle customer", 350.0)]
REF_FEE, CLAWBACK = (0.01, 0.02, 0.025), 0.025          # XL-13: 1-2.5% of the loan, taken back if it closes or defaults in 6 months
TRAIL = (0.002, 0.0035, 0.005)                           # XB-04: 0.2-0.5% of balance a year (debt funds)
RATE, MONTHS = 0.26, 12                                  # our shop-loan terms (lend_self.SEGS)

loan_net = {(r["segment"], r["case"]): float(r["net"]) for r in csv.DictReader((T / "lend_loan.csv").open())}
funnel = next(r for r in csv.DictReader((T / "lend_funnel.csv").open()) if abs(float(r["takeup"]) - 0.2) < 1e-9)
cac = next(float(r["today"]) for r in csv.DictReader((T / "lend_breakeven.csv").open()) if r["number"] == "cost_to_win")


def annuity(n, apr):
    i = apr / 12
    return (1 - (1 + i) ** -n) / i


# one unit of each product: what it earns us, low / mid / high, with the evidence
SHOP = loan_net[("Shopkeepers", "industry steady state")]
UNITS = [
    ("Refer a personal loan (Rs 25,557)", [25557 * f * (1 - CLAWBACK) for f in REF_FEE], "per loan disbursed", "XL-42 ticket; XL-13 fee"),
    ("Refer a shop loan (Rs 1.5 lakh)", [150000 * f * (1 - CLAWBACK) for f in REF_FEE], "per loan disbursed", "lend_self ticket; XL-13 fee"),
    ("Lend a shop loan ourselves (Rs 1.5 lakh, 12 months, 26%)",
     [loan_net[("Shopkeepers", "industry today")], SHOP, loan_net[("Shopkeepers", "savers safer")]],
     "per loan, after funding, losses and running cost", "tables/lend_loan.csv (losses 9% / 6% / 3%)"),
    ("Accident or hospital-cash policy", [0.10 * 300, 0.15 * 800, 0.20 * 1500], "first-year commission per policy", "xs_other_summary: XO-19, XO-30, XO-35"),
    ("Small term-life policy", [0.075 * 500, 0.25 * 1000, 0.30 * 2000], "first-year commission per policy", "xs_other_summary: XO-20"),
    ("Two-wheeler insurance", [0.025 * 714, 0.0475 * 1000, 0.0905 * 1200], "commission per policy a year", "xs_other_summary: XO-18, XO-21"),
]
# how many units the evidence says get sold, per active saver per year (low / mid / high)
SOLD = {
    "Refer a personal loan (Rs 25,557)": ((0.01, 0.03, 0.08), "XL-48: approved loans per saver a year"),
    "Refer a shop loan (Rs 1.5 lakh)": ((0.01, 0.03, 0.20), "XL-48 low/mid; 0.20 = our model's take-up (Paytm's engaged shops)"),
    "Lend a shop loan ourselves (Rs 1.5 lakh, 12 months, 26%)": ((0.01, 0.03, 0.20), "as above"),
    "Accident or hospital-cash policy": ((0.02, 0.06, 0.15), "xs_other_summary take-up"),
    "Small term-life policy": ((0.01, 0.03, 0.06), "xs_other_summary take-up"),
    "Two-wheeler insurance": ((0.05, 0.15, 0.30), "xs_other_summary take-up"),
}


def main():
    units = []
    for name, (lo, mid, hi), per, src in UNITS:
        row = {"product": name, "earns_low": lo, "earns_mid": mid, "earns_high": hi, "per": per, "source": src,
               "sold_low": SOLD[name][0][0], "sold_mid": SOLD[name][0][1], "sold_high": SOLD[name][0][2], "sold_source": SOLD[name][1]}
        for label, a in SIZES:
            need = COST * DEBITS * a
            row[f"need_per_year_at_{a:.0f}"] = need / mid if mid > 0 else float("inf")
        row["earns_safe_case"] = loan_net[("Shopkeepers", "savers safer")] if name.startswith("Lend") else ""
        row["short_by_at_100"] = row["need_per_year_at_100"] / row["sold_mid"]
        units.append(row)

    stack = []
    for label, a in SIZES:
        dep = DEBITS * a
        cost = COST * dep
        trail = [t * HOLD * dep for t in TRAIL]
        stack.append({"saver": label, "per_day": a, "deposits_a_year": dep, "cost_a_year": cost,
                      "trail_low": trail[0], "trail_mid": trail[1], "trail_high": trail[2],
                      "nonloan_low": 8.0, "nonloan_mid": 63.0, "nonloan_high": 259.0,          # XO-39, per active saver a year
                      "loanref_low": 1.5, "loanref_mid": 15.0, "loanref_high": 140.0,          # XL-48, per active saver a year
                      "years_money_must_stay_low": COST / TRAIL[2], "years_money_must_stay_high": COST / TRAIL[0]})
    for s in stack:
        for k in ("low", "mid", "high"):
            s[f"total_{k}"] = s[f"trail_{k}"] + s[f"nonloan_{k}"] + s[f"loanref_{k}"]
            s[f"covered_{k}"] = s[f"total_{k}"] / s["cost_a_year"]

    # loans sized to what the saver already puts away: the EMI equals their monthly saving
    shop_net_share = SHOP / 150000
    safe_net_share = loan_net[("Shopkeepers", "savers safer")] / 150000
    sized = []
    for label, a in SIZES:
        monthly = a * DEBITS / 12
        ticket = monthly * annuity(MONTHS, RATE)
        cost = COST * DEBITS * a
        ref = ticket * REF_FEE[1] * (1 - CLAWBACK)
        sized.append({"saver": label, "per_day": a, "monthly_saving": monthly, "loan_they_can_repay": ticket, "cost_a_year": cost,
                      "refer_earns": ref, "refer_loans_needed_a_year": cost / ref,
                      "lend_earns_normal": ticket * shop_net_share, "lend_loans_needed_normal": cost / (ticket * shop_net_share),
                      "lend_earns_safe": ticket * safe_net_share, "lend_loans_needed_safe": cost / (ticket * safe_net_share),
                      "shop_loan_in_months_of_saving": 150000 / monthly})

    # how big each loan must be for the 1.5% to be paid at a given borrowing rate (Rs 100 a day saver)
    cost100 = COST * DEBITS * 100
    shares = {"refer": REF_FEE[1] * (1 - CLAWBACK), "lend": shop_net_share}
    size_rows = []
    for takeup, label in ((0.03, "evidence middle: 3 in 100 savers a year"), (0.20, "our model: 20 in 100 savers a year")):
        for mode in ("refer", "lend"):
            size_rows.append({"takeup": takeup, "takeup_label": label, "mode": mode, "share_of_loan_earned": shares[mode],
                              "loan_size_needed": cost100 / (takeup * shares[mode]),
                              "times_what_saving_supports": cost100 / (takeup * shares[mode]) / sized[1]["loan_they_can_repay"]})
    with (T / "invert_loan_size.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(size_rows[0]))
        w.writeheader()
        w.writerows(size_rows)
    for z in size_rows:
        print(f"take-up {z['takeup']:.2f} {z['mode']:<6} loan needed {z['loan_size_needed']:>9,.0f} = {z['times_what_saving_supports']:.1f}x what saving supports")

    still_12 = float(funnel["saving_m12"]) / 100
    notes = [
        ("cost_to_win", cac, "tables/lend_breakeven.csv (today's evidence)"),
        ("still_saving_at_12m", still_12, "tables/lend_funnel.csv"),
        ("cost_to_win_per_saver_still_saving", cac / still_12, "cost_to_win / still_saving_at_12m"),
        ("years_of_1.5pct_at_100", cac / still_12 / (COST * DEBITS * 100), "per saver still saving, at Rs 100 a day"),
        ("loans_per_customer_won_per_year", float(funnel["loans_5y_per_100"]) / 100 / 5, "tables/lend_funnel.csv at 20% take-up"),
        ("gold_commission_on_flow", 0.024, "LEV-036: Jar earns ~2.4% of each gold purchase"),
    ]
    for name, rows in (("invert_units.csv", units), ("invert_stack.csv", stack), ("invert_sized.csv", sized)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    with (T / "invert_notes.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value", "from"])
        w.writerows(notes)

    for r in units:
        print(f"{r['product'][:46]:<46} earns {r['earns_mid']:>7,.0f} | need/yr at 51/100/300: "
              + " / ".join(f"{r[f'need_per_year_at_{a:.0f}']:.2f}" for _, a in SIZES) + f" | sold mid {r['sold_mid']:.2f}")
    for s in stack:
        print(f"{s['saver']:<28} deposits {s['deposits_a_year']:>7,.0f} cost {s['cost_a_year']:>6,.0f} | trail {s['trail_low']:.0f}-{s['trail_high']:.0f} | "
              f"total low/mid/high {s['total_low']:.0f}/{s['total_mid']:.0f}/{s['total_high']:.0f} = {s['covered_low']:.0%}/{s['covered_mid']:.0%}/{s['covered_high']:.0%}")
    for z in sized:
        print(f"{z['saver']:<28} saves {z['monthly_saving']:>6,.0f}/m -> loan {z['loan_they_can_repay']:>7,.0f}; refer needs {z['refer_loans_needed_a_year']:.2f}/yr; "
              f"lend needs {z['lend_loans_needed_normal']:.2f} (normal) {z['lend_loans_needed_safe']:.2f} (safe); Rs 1.5L = {z['shop_loan_in_months_of_saving']:.0f} months of saving")
    for k, val, frm in notes:
        print(f"{k:<38}{val:>10,.3f}  {frm}")
    agent(units, shop_net_share)


# ---------- one street agent (operator, 16 Oct 2026: "the fleet on street guy ... roughly 4L per year") ----------
AGENT = 400000.0                      # Rs a year, all in (operator)
BOOK, BOOK_RANGE = 300, (200, 400)    # savers one agent can visit daily: Arvinder's book, 200-400 (interview 15 Oct 2026)
DAILY, DAILY_RANGE = 350.0, (200.0, 500.0)   # what each of his customers puts in a day: Rs 200-500 (same interview)
OTHER = (8.0, 63.0, 259.0)            # all non-loan products, Rs per active saver a year (XO-39)
SOLD_LOANS = (0.03, 0.20)             # loans per saver a year: evidence middle (XL-48) / our model's take-up


def agent(units, shop_net_share):
    deposits = BOOK * DAILY * DEBITS
    book = [{"saver_puts_in_a_day": a, "deposits_a_year": a * DEBITS, "savers_needed_for_1_5pct": AGENT / (COST * DEBITS * a),
             "cost_pct_at_300_savers": AGENT / (BOOK * a * DEBITS)} for a in (51.0, 100.0, DAILY, DAILY_RANGE[1])]
    bal = HOLD * deposits
    stack = {"deposits_a_year": deposits, "cost_pct": AGENT / deposits, "balance": bal}
    for i, k in enumerate(("low", "mid", "high")):
        stack[f"fund_{k}"] = TRAIL[i] * bal
        stack[f"other_{k}"] = OTHER[i] * BOOK
        stack[f"nonloan_{k}"] = stack[f"fund_{k}"] + stack[f"other_{k}"]
        stack[f"covered_{k}"] = stack[f"nonloan_{k}"] / AGENT
        stack[f"gap_{k}"] = AGENT - stack[f"nonloan_{k}"]
        stack[f"gap_per_saver_{k}"] = stack[f"gap_{k}"] / BOOK
    gap = stack["gap_mid"]
    fill = []
    for r in units:
        evid = r["sold_mid"]
        n = gap / r["earns_mid"] if r["earns_mid"] > 0 else float("inf")
        fill.append({"product": r["product"], "earns_per_unit": r["earns_mid"], "units_per_agent_a_year": n,
                     "per_saver_a_year": n / BOOK, "evidence_per_saver_a_year": evid, "short_by": n / BOOK / evid})
    safe = next(r for r in units if r["product"].startswith("Lend"))["earns_safe_case"]
    fill.append({"product": "Lend a shop loan ourselves, losses 3% (savers really safer)", "earns_per_unit": safe,
                 "units_per_agent_a_year": gap / safe, "per_saver_a_year": gap / safe / BOOK, "evidence_per_saver_a_year": 0.03,
                 "short_by": gap / safe / BOOK / 0.03})
    monthly = DAILY * DEBITS / 12
    can_repay = monthly * annuity(MONTHS, RATE)
    size = [{"loans_per_saver_a_year": t, "loan_size_needed": stack["gap_per_saver_mid"] / (t * shop_net_share),
             "saver_can_repay_12m": can_repay, "times": stack["gap_per_saver_mid"] / (t * shop_net_share) / can_repay} for t in SOLD_LOANS]
    still_12 = float(funnel["saving_m12"]) / 100
    extra = [("signups_to_keep_book", BOOK / still_12, "BOOK / still saving at 12 months (tables/lend_funnel.csv)"),
             ("signups_per_working_day", BOOK / still_12 / DEBITS, "over 240 working days"),
             ("monthly_saving_middle_customer", monthly, "DAILY x 240 / 12"),
             ("loss_9pct_net_per_loan", loan_net[("Shopkeepers", "industry today")], "tables/lend_loan.csv"),
             ("loss_6pct_net_per_loan", loan_net[("Shopkeepers", "industry steady state")], "tables/lend_loan.csv"),
             ("loss_3pct_net_per_loan", loan_net[("Shopkeepers", "savers safer")], "tables/lend_loan.csv"),
             ("loans_needed_6pct", gap / loan_net[("Shopkeepers", "industry steady state")], "gap_mid / net"),
             ("loans_needed_3pct", gap / loan_net[("Shopkeepers", "savers safer")], "gap_mid / net")]
    for name, rows in (("invert_agent_book.csv", book), ("invert_agent_stack.csv", [stack]), ("invert_agent_fill.csv", fill),
                       ("invert_agent_loan_size.csv", size)):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    with (T / "invert_agent_notes.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value", "from"])
        w.writerows(extra)
    print("\nAGENT Rs 4L/yr, book 300 x Rs 350 x 240:", f"deposits {deposits:,.0f}, cost {stack['cost_pct']:.2%}")
    for b_ in book:
        print(f"  Rs {b_['saver_puts_in_a_day']:.0f}/day: savers needed for 1.5% = {b_['savers_needed_for_1_5pct']:,.0f}; cost at 300 savers = {b_['cost_pct_at_300_savers']:.2%}")
    print("  non-loan pays back low/mid/high:", " / ".join(f"{stack[f'nonloan_{k}']:,.0f} ({stack[f'covered_{k}']:.0%})" for k in ("low", "mid", "high")),
          f"| gap mid {gap:,.0f} = {stack['gap_per_saver_mid']:,.0f}/saver")
    for f_ in fill:
        print(f"  {f_['product'][:52]:<52} {f_['units_per_agent_a_year']:>7,.1f}/agent {f_['per_saver_a_year']:.3f}/saver vs {f_['evidence_per_saver_a_year']} -> {f_['short_by']:.1f}x")
    for z in size:
        print(f"  at {z['loans_per_saver_a_year']:.2f} loans/saver/yr each loan must be {z['loan_size_needed']:,.0f} = {z['times']:.1f}x what saving repays ({z['saver_can_repay_12m']:,.0f})")
    for k, val, frm in extra:
        print(f"  {k:<32}{val:>12,.1f}")


if __name__ == "__main__":
    main()

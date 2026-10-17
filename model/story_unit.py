"""Per-customer view for the story (operator, 16 Oct 2026): "Whole game is that we are able to acquire and build a
relationship ... better than any online model. Take into account a CAC of online for this customer and what we
acquire him for and then what we make over time."

Same customer and same products in both channels (Rs 350 a day; fund commission, other products, cards, loans as
in model/agent_3yr.py middle case). Only two things differ:
  cost to win   online: Rs 499 per activated saver (tables/distributions.csv cac_target@ng, Rs 186-1,340:
                Groww Rs 796-1,374 with 83% organic, finance-app installs Rs 100-300, Jar/Stable Money Rs 249 if half
                of sign-ups save); street: Rs 4,00,000 a year / 1,000 sign-ups = Rs 400, which also pays for collection
  who stays     online: our model's evidence curve (24.2% still saving at 12 months); street: Arvinder's janta book
                (8 of 300 leave a month: 72.3% at 12 months); plus a stress case: street cost, online retention
Value is undiscounted, per customer won, over his first 36 months. Writes tables/story_unit.csv, story_unit_curve.csv.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
SURV = list(csv.DictReader((T / "agent3_survival.csv").open()))
FUN = {(r["view"], r["year"]): r for r in csv.DictReader((T / "agent3_funnel.csv").open())}
INP = {r["step"]: r for r in csv.DictReader((T / "agent3_funnel_inputs.csv").open())}
CAC_ONLINE, CAC_ONLINE_RANGE = 499.2394, (186.0, 1340.0)   # tables/distributions.csv cac_target@ng
CAC_STREET = 400000.0 / 1000.0                               # operator: Rs 4 lakh a year, 1,000 sign-ups a year
DAILY, DAYS = 350.0, 240
FUND_A_YEAR = 0.0035 * 0.5 * DAILY * DAYS                     # 0.35% on half a year's deposits (XB-04): Rs 147
OTHER_A_YEAR = 63.0                                           # XO-39 middle
LOAN_RATE = float(INP["approved loans per proven saver a year"]["mid"])   # 2.5% a year
LOAN_FEE = float(INP["fee kept per loan (Rs)"]["mid"])                    # Rs 2,437.5
CARD = 0.05 * 1250.0                                          # 5% of savers get a card, Rs 1,250 each, once
PROVEN = 6


PAYTM_FEE_X = 4.5      # Paytm-like: 4.5% of each loan instead of our 1% (SE-05 / XL-07), by collecting and taking part of the risk (DLG, SE-04)


def run(curve_key, fee_x=1.0):
    s = [float(r[curve_key]) for r in SURV]
    cum, rows = CARD, []
    parts = {"fund": 0.0, "other": 0.0, "loans": 0.0, "cards": CARD}
    for t, st in enumerate(s, start=1):
        parts["fund"] += st * FUND_A_YEAR / 12
        parts["other"] += st * OTHER_A_YEAR / 12
        if t > PROVEN:
            parts["loans"] += st * LOAN_RATE * LOAN_FEE * fee_x / 12
        cum = sum(parts.values())
        rows.append((t, cum))
    return s, parts, rows


def main():
    channels = [("online", "An app", CAC_ONLINE, "still_saving_evidence", 1.0),
                ("street", "Our street agent", CAC_STREET, "still_saving_janta_mid", 1.0),
                ("street_stress", "Street agent, if savers drop off like an app's", CAC_STREET, "still_saving_evidence", 1.0),
                ("street_paytm_fee", "Street agent, earning a Paytm-like 4.5% per loan", CAC_STREET, "still_saving_janta_mid", PAYTM_FEE_X)]
    out, curves = [], {}
    for key, label, cac, ck, fx in channels:
        s, parts, rows = run(ck, fx)
        value = sum(parts.values())
        pay = next((t for t, c in rows if c >= cac), None)
        out.append({"channel": key, "label": label, "cost_to_win": cac, "still_saving_m12": s[11],
                    "cost_per_saver_still_saving_m12": cac / s[11], "saver_months_36": sum(s),
                    "value_fund": parts["fund"], "value_other": parts["other"], "value_loans": parts["loans"], "value_cards": parts["cards"],
                    "value_36m": value, "value_per_rupee_of_cost": value / cac, "payback_month": pay if pay else ""})
        curves[key] = rows
    with (T / "story_unit.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    with (T / "story_unit_curve.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", *curves])
        for i in range(36):
            w.writerow([i + 1, *(curves[k][i][1] for k in curves)])
    # the closest comparator (operator, 16 Oct 2026: "look at customers of Paytm, they come the closest to us")
    rent_month = 90.0                         # QM-10 note / Inc42: Paytm earned Rs 90 per device a month in Q4 FY24 (floor Rs 80, target Rs 100)
    ticket, take = 205000.0, (0.045, 0.05)    # XB-08 ticket; XL-07 take rate 4.5-5% (above 5% with DLG)
    paytm = [("paytm_cost_to_win_upto", 5000.0, "QM-13 / NG-043: sales and service staff cost per net device added (upper bound; includes servicing)"),
             ("paytm_devices_dec23_cr", 1.06, "QM-06"), ("paytm_devices_mar24_cr", 1.07, "QM-07"), ("paytm_devices_jun26_cr", 1.57, "QM-09"),
             ("paytm_rent_a_month", rent_month, "QM-10 note (Inc42, Q4 FY24)"), ("paytm_rent_a_year", rent_month * 12, "x 12"),
             ("paytm_loan_ticket", ticket, "XB-08"), ("paytm_fee_per_loan_low", ticket * take[0], "XL-07 4.5%"), ("paytm_fee_per_loan_high", ticket * take[1], "XL-07 5%"),
             ("paytm_losses_low", 0.045, "QM-22"), ("paytm_losses_high", 0.05, "QM-22"),
             ("our_income_per_saver_year", FUND_A_YEAR + OTHER_A_YEAR, "fund Rs 147 + other products Rs 63"),
             ("our_fee_per_loan", LOAN_FEE / (1 - 0.025), "1% of Rs 2.5 lakh (before any fee taken back)"),
             ("rent_vs_our_income", rent_month * 12 / (FUND_A_YEAR + OTHER_A_YEAR), "ratio"),
             ("paytm_fee_vs_ours_low", ticket * take[0] / (LOAN_FEE / (1 - 0.025)), "ratio"), ("paytm_fee_vs_ours_high", ticket * take[1] / (LOAN_FEE / (1 - 0.025)), "ratio"),
             ("paytm_cost_vs_ours", 5000.0 / CAC_STREET, "ratio")]
    # one agent, janta-like retention, middle case: what a Paytm-like 4.5% fee does to his 3 years
    fun = FUN[("janta", "1-3")]
    inc = float(fun["income_mid"]) - float(fun["loanfees_mid"]) + PAYTM_FEE_X * float(fun["loanfees_mid"])
    paytm += [("agent_covered_janta_1pct", float(fun["covered_mid"]), "tables/agent3_funnel.csv"),
              ("agent_covered_janta_paytm_fee", inc / 1200000.0, "income with loan fees x 4.5, over Rs 12 lakh"),
              ("agent_income_janta_paytm_fee", inc, "Rs over 3 years")]
    with (T / "story_paytm.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value", "from"])
        w.writerows(paytm)
    for k, v, _ in paytm:
        print(f"  {k:<28}{v:>12,.2f}")
    for r in out:
        print(f"{r['label']:<48} win Rs {r['cost_to_win']:>6,.0f} | 12m {r['still_saving_m12']:.1%} | per saver kept Rs {r['cost_per_saver_still_saving_m12']:>6,.0f} | "
              f"3y value Rs {r['value_36m']:>5,.0f} (fund {r['value_fund']:.0f}, other {r['value_other']:.0f}, loans {r['value_loans']:.0f}, cards {r['value_cards']:.0f}) "
              f"= {r['value_per_rupee_of_cost']:.2f}x | payback month {r['payback_month'] or 'not in 3 yrs'}")
    print(f"online cost-to-win range {CAC_ONLINE_RANGE}: per saver kept Rs {CAC_ONLINE_RANGE[0] / out[0]['still_saving_m12']:,.0f}-{CAC_ONLINE_RANGE[1] / out[0]['still_saving_m12']:,.0f}")


if __name__ == "__main__":
    main()

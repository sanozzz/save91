"""Derived numbers for the QR-moat test, computed once into tables/qr_moat_numbers.csv.

Reads research/qr_moat.csv (evidence, one row per number) and the deck's own model outputs
(tables/lend_breakeven.csv, tables/lend_salaried.csv). The PDF builder quotes only this table and the
evidence table; it recomputes nothing.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = {r["id"]: r for r in csv.DictReader((ROOT / "research" / "qr_moat.csv").open())}
BE = {r["number"]: r for r in csv.DictReader((ROOT / "tables" / "lend_breakeven.csv").open())}
SAL = list(csv.DictReader((ROOT / "tables" / "lend_salaried.csv").open()))
SHOP_LOAN = 150000.0        # lend_self.SEGS: shopkeepers borrow Rs 1.5 lakh over 12 months
SAVE_PER_DAY = 100.0        # PhonePe's Daily RD minimum (QM-33), also a round daily-saving amount


def v(i, col="value"):
    return float(EV[i][col])


def sal(rate, case):
    return next(float(r["net"]) for r in SAL if r["cac_case"] == "evidence" and abs(float(r["rate"]) - rate) < 1e-9 and r["case"] == case)


def main():
    rows = [
        ("qr_per_merchant", v("QM-01") / v("QM-02"), "QM-01 / QM-02", "QR codes per merchant (gross; not all active)"),
        ("qr_codes_cr", v("QM-01"), "QM-01", "UPI QR codes, crore"),
        ("phonepe_people", v("QM-12") + v("QM-12", "value_high"), "QM-12 + QM-12 high", "PhonePe field staff plus commissioned agents"),
        ("paytm_share_dec23", v("QM-15"), "QM-15", "Paytm app share of UPI payments, Dec 2023, %"),
        ("paytm_share_dec24", v("QM-16"), "QM-16", "the same, Dec 2024, %"),
        ("paytm_share_drop", 1 - v("QM-16") / v("QM-15"), "1 - QM-16 / QM-15", "fall in Paytm's share of UPI payments"),
        ("paytm_dev_dec23", v("QM-06"), "QM-06", "Paytm device merchants, crore"),
        ("paytm_dev_mar24", v("QM-07"), "QM-07", ""),
        ("paytm_dev_mar26", v("QM-08"), "QM-08", ""),
        ("paytm_dev_jun26", v("QM-09"), "QM-09", ""),
        ("paytm_dev_shock_change", v("QM-07") / v("QM-06") - 1, "QM-07 / QM-06 - 1", "change in device merchants through the shock quarter"),
        ("paytm_dev_since", v("QM-09") / v("QM-07") - 1, "QM-09 / QM-07 - 1", "growth in device merchants since the shock"),
        ("paytm_ml_q3fy24", v("QM-17"), "QM-17", "Paytm merchant loans, Rs crore a quarter"),
        ("paytm_ml_q4fy24", v("QM-18"), "QM-18", ""),
        ("paytm_ml_drop", 1 - v("QM-18") / v("QM-17"), "1 - QM-18 / QM-17", "fall in Paytm merchant loans in one quarter"),
        ("phonepe_ml_fy23", v("QM-27"), "QM-27", "PhonePe merchant loans, Rs crore"),
        ("phonepe_ml_fy24", v("QM-28"), "QM-28", ""),
        ("phonepe_ml_fy25", v("QM-29"), "QM-29", ""),
        ("phonepe_ml_h1fy26", v("QM-30"), "QM-30", "Apr-Sep 2025"),
        ("phonepe_ml_h1fy25", v("QM-30", "value_high"), "QM-30 (value_high)", "Apr-Sep 2024"),
        ("phonepe_ml_fy25_x", v("QM-29") / v("QM-28"), "QM-29 / QM-28", "PhonePe FY25 merchant loans vs FY24"),
        ("phonepe_ml_h1_x", v("QM-30") / v("QM-30", "value_high"), "QM-30 / QM-30 high", "PhonePe H1 FY26 vs H1 FY25"),
        ("paytm_ecl_low", v("QM-22") / 100, "QM-22", "Paytm-sourced merchant loans, expected loss"),
        ("paytm_ecl_high", v("QM-22", "value_high") / 100, "QM-22 (value_high)", ""),
        ("be_losses", float(BE["losses"]["breakeven"]), "lend_breakeven.csv", "losses a shopkeeper can carry and still pay back"),
        ("losses_today", float(BE["losses"]["today"]), "lend_breakeven.csv", "losses assumed today (industry steady state)"),
        ("be_cost", float(BE["cost_to_win"]["breakeven"]), "lend_breakeven.csv", "most we can pay to win a shopkeeper"),
        ("cost_today", float(BE["cost_to_win"]["today"]), "lend_breakeven.csv", ""),
        ("be_takeup", float(BE["takeup"]["breakeven"]), "lend_breakeven.csv", "fewest proven savers who must borrow each year"),
        ("takeup_today", float(BE["takeup"]["today"]), "lend_breakeven.csv", ""),
        ("be_rate", float(BE["rate"]["breakeven"]), "lend_breakeven.csv", "lowest rate that still pays back"),
        ("rate_today", float(BE["rate"]["today"]), "lend_breakeven.csv", ""),
        ("value_today", float(BE["today"]["value_at_low"]), "lend_breakeven.csv", "one shopkeeper at today's evidence, Rs"),
        ("headroom_vs_paytm", float(BE["losses"]["breakeven"]) - v("QM-22", "value_high") / 100, "be_losses - QM-22 high", "room between Paytm's losses and our break-even"),
        ("autopay_fail_low", v("QM-26") / 100, "QM-26", "UPI Autopay debits that failed, by bank, Aug 2025 (low end)"),
        ("autopay_fail_high", v("QM-26", "value_high") / 100, "QM-26 (value_high)", "the same (high end)"),
        ("digital_losses_low", v("QM-40") / 100, "QM-40", "losses at digital lenders without the till (low end)"),
        ("digital_losses_high", v("QM-40", "value_high") / 100, "QM-40 (value_high)", "the same (high end)"),
        ("aa_lakh_cr", v("QM-24"), "QM-24", "Account Aggregator lending FY26, Rs lakh crore"),
        ("aa_share_value", v("QM-25") / 100, "QM-25", ""),
        ("sal_safe_24", sal(0.24, "savers safer"), "lend_salaried.csv", "salaried, 24% rate, losses 3%: value per customer, Rs"),
        ("sal_normal_24", sal(0.24, "industry steady state"), "lend_salaried.csv", "salaried, 24% rate, losses 6%"),
        ("save_year", SAVE_PER_DAY * 365, "Rs 100 x 365", "a year of Rs 100 a day, if every debit succeeds"),
        ("save_year_share_of_loan", SAVE_PER_DAY * 365 / SHOP_LOAN, "save_year / Rs 1.5 lakh", "that year's savings as a share of one shopkeeper loan"),
        # Bachatt's filter, and what self-selection does to one shopkeeper if we hold the loan.
        # value_at_low / value_at_high move ONLY the loss rate (3% and 10%); every other input stays at today's evidence.
        ("bachatt_users", v("QM-41") * 1_000_000, "QM-41 x 1e6", "Bachatt users, company claim"),
        ("bachatt_txns", v("QM-42") * 1_000_000, "QM-42 x 1e6", "Bachatt fund purchases in Feb 2026"),
        ("debits_per_saver", v("QM-43"), "QM-43", "assumed fund purchases a month per daily saver"),
        ("bachatt_daily_savers", v("QM-42") * 1_000_000 / v("QM-43"), "QM-42 x 1e6 / QM-43", "daily savers implied by the February purchases"),
        ("bachatt_saver_share", (v("QM-42") * 1_000_000 / v("QM-43")) / (v("QM-41") * 1_000_000), "daily savers / QM-41", "implied daily savers as a share of claimed users"),
        ("bachatt_loan_cap", v("QM-44"), "QM-44", "largest loan Bachatt says its partners offer"),
        ("bachatt_raised", v("QM-45"), "QM-45", "seed plus Series A, USD million"),
        ("value_if_losses_3", float(BE["losses"]["value_at_low"]), "lend_breakeven.csv losses value_at_low", "one shopkeeper if losses are 3% and nothing else changes, Rs"),
        ("value_if_losses_10", float(BE["losses"]["value_at_high"]), "lend_breakeven.csv losses value_at_high", "one shopkeeper if losses are 10% and nothing else changes, Rs"),
    ]
    assert abs(float(BE["losses"]["range_low"]) - 0.03) < 1e-9, BE["losses"]["range_low"]
    assert abs(float(BE["losses"]["range_high"]) - 0.10) < 1e-9, BE["losses"]["range_high"]
    out = ROOT / "tables" / "qr_moat_numbers.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value", "from", "what"])
        w.writerows(rows)
    for k, val, frm, _ in rows:
        print(f"{k:<26}{val:>14,.4f}   {frm}")


if __name__ == "__main__":
    main()

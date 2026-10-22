"""What a customer who STAYS does, and how many loans they would need to take.

Two designs, both at the evidence middle (every uncertain input at the middle of its range):
  as_designed   daily debits through a payment company; half the money in digital gold
  fund_rails    Bachatt-style: daily SIPs into debt funds through the exchange MF platform, where
                the fund house pays the platform and the distributor pays nothing per debit
                (cafemutual: BSE Star MF charges AMCs, not distributors); no digital gold, so no
                gold margin; we earn the distributor trail on the fund balance (debt funds pay
                0.2-0.5% a year; 0.3% used). The SEBI new-investor bonus (1% of first-year SIPs,
                cap Rs 2,000, only new B30 or women investors, not liquid/low-duration funds) is
                left out: who qualifies is unknown.
Both add everything else we could sell (tables/crosssell_map.csv, middle case) via ltv.customer.

For each design:
  stayer_*      a saver who stays all 5 years (sums of per-active-saver monthly values)
  customer_*    one customer won, 5 years discounted, after the cost to win them (ltv.py)
  loans_needed  working-capital loans per ACTIVE saver per year, at Rs 50,000 and a 2% referral
                fee (Rs 1,000 a loan), that would bring one customer won to break-even

Writes tables/stayer_designs.csv.
"""
import csv

import engine as E
import ltv
import mc

T = E.TABLES
WC_TICKET, WC_FEE = 50000.0, 0.02          # working-capital loan referred to a lender: XL rows (1-3% fee, Rs 50k-2L)
FUND_TRAIL = 0.003                         # debt-fund distributor trail, middle of 0.2-0.5%


def designs():
    ev = ltv.evidence_overrides()
    fund = {**ev, "gold_on": 0.0, "trail_liquid": FUND_TRAIL, "cost_notice": 0.0}
    for s in ("gig", "ng"):
        fund[f"cost_debit@{s}"] = 0.0
        fund[f"cost_failed@{s}"] = 0.0
    return {"as_designed": ev, "fund_rails": fund}


def stayer(ov):
    p, rows, out, _ = E.run("base", ov)
    A = [r["active"] for r in rows]
    per = lambda k: sum(r[k] / a for r, a in zip(rows, A) if a > 0)
    rev = sum(per(k) for k in ("rev_gold", "rev_liquid", "rev_fd", "rev_loans", "rev_insurance", "rev_cards", "rev_sip", "rev_mf_incentive"))
    cost = sum(per(k) for k in ("cost_payments", "cost_service", "cost_fraud", "cost_loans", "cost_insurance", "cost_cards"))
    N = p["cohort_size"]
    dm = (1 + p["disc_rate"]) ** (1 / 12) - 1
    pv_active_years = sum(r["active"] / N / 12 / (1 + dm) ** r["month"] for r in rows)
    return {"stayer_saved": per("contributions"), "stayer_balance_y5": rows[59]["bal_active"] / A[59], "stayer_loans": per("loans"),
            "stayer_borrowed": per("disbursal"), "stayer_avg_loan": per("disbursal") / per("loans") if per("loans") else 0.0,
            "stayer_revenue": rev, "stayer_cost": cost, "stayer_net": rev - cost, "stayer_debit_fees": per("cost_payments"),
            "pv_active_years": pv_active_years, "still_m12": A[11] / N, "still_m60": A[59] / N}


def main():
    xs = ltv.xs_total("mid")
    out = []
    for name, ov in designs().items():
        s = stayer(ov)
        c, _ = ltv.customer(ov, xs)
        need = max(0.0, -c["net60"]) / (s["pv_active_years"] * WC_TICKET * WC_FEE)
        row = {"design": name, **s, "customer_cac": c["cac"], "customer_ltv60": c["ltv60"], "customer_net60": c["net60"],
               "customer_payback": c["payback_month"], "customer_savings_pv": c["savings_pv"], "customer_cross_sell_pv": c["cross_sell_pv"],
               "customer_serve_pv": c["serve_pv"], "wc_loans_needed_per_active_year": need, "wc_ticket": WC_TICKET, "wc_fee": WC_FEE}
        out.append(row)
        print(f"\n{name}: stayer saves {s['stayer_saved']:,.0f}, takes {s['stayer_loans']:.2f} loans (avg {s['stayer_avg_loan']:,.0f}), "
              f"earns us {s['stayer_revenue']:,.0f}, costs {s['stayer_cost']:,.0f} (debit fees {s['stayer_debit_fees']:,.0f}) -> {s['stayer_net']:,.0f}")
        print(f"  customer won: CAC {c['cac']:.0f}, savings {c['savings_pv']:.0f} + cross-sell {c['cross_sell_pv']:.0f} - serve {c['serve_pv']:.0f} "
              f"= {c['ltv60']:.0f}; net {c['net60']:.0f}; payback {c['payback_month'] or 'never'}")
        print(f"  break-even needs {need:.2f} working-capital loans of Rs {WC_TICKET:,.0f} per active saver a year "
              f"(= {need * 5:.1f} over 5 years for a stayer); active-years per customer won {s['pv_active_years']:.2f}")
    mc.write("stayer_designs.csv", out)


if __name__ == "__main__":
    main()

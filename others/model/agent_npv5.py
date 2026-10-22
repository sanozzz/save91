"""5-year NPV of one street agent, savings only (operator, 16 Oct 2026: "calculate 5 year NPV of the agent. Assume no
loans and no insurance, no cross sell nothing. That is what it costs us to acquire and service the customer").

Revenue: fund commission only. Cost: the agent (acquires AND services). Everything else as model/scenarios.py:
  agent        Rs 20,000 a month (operator); the "+1% of collections" variant shown separately
  sign-ups     1,000 a year, joining at the start of each month, for all 5 years
  saver        Rs 350 a day x 20 deposit days a month = Rs 7,000 a month
  who stays    still saving after 12 months R12 = 30 / 40 / 55 / 70%; steady monthly drop-off c = 1 - R12^(1/12)
  balance      'yearly terms': average balance = half a year's deposits (Rs 42,000), as janta accounts close at term end
               'builds up': each saver's balance grows by Rs 7,000 a month while he saves; he withdraws when he stops
  commission   0.35% a year on the balance (XB-04, debt fund, middle); 'liquid fund' variant 0.08% (tables/inputs.csv trail_liquid)
  discount     20% a year (tables/inputs.csv disc_rate), monthly
Writes tables/npv5.csv.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
MONTHS, SIGNUPS_M, MONTHLY_SAVE, PAY_M = 60, 1000 / 12, 350 * 20, 20000.0
DISC_M = 1.20 ** (1 / 12) - 1
CAPACITY, EVERY = 400, 2.5


def run(r12, balance="yearly", trail=0.0035, commission=0.0):
    c = 1 - r12 ** (1 / 12)
    pv_cost = pv_rev = 0.0
    signed = 0.0
    end_active = 0.0
    # cohort joining in month m (0-based): in month t (>= m) it has saved k = t - m + 1 months; share still saving (1-c)^(k-1)
    for t in range(MONTHS):
        active = 0.0
        rev = 0.0
        for m in range(t + 1):
            k = t - m + 1
            share = (1 - c) ** (k - 1)          # the month he joins, everyone saves
            n = SIGNUPS_M * share
            active += n
            bal = (MONTHLY_SAVE * 12 * 0.5) if balance == "yearly" else MONTHLY_SAVE * k
            rev += n * bal * trail / 12
        cost = PAY_M + commission * active * MONTHLY_SAVE
        d = (1 + DISC_M) ** (t + 1)
        pv_cost += cost / d
        pv_rev += rev / d
        signed += SIGNUPS_M
        end_active = active
    return {"pv_cost": pv_cost, "pv_revenue": pv_rev, "npv": pv_rev - pv_cost, "signed": signed,
            "pv_cost_per_signup": pv_cost / signed, "pv_revenue_per_signup": pv_rev / signed,
            "cross_sell_pv_needed_per_signup": max(pv_cost - pv_rev, 0) / signed, "savers_end_y5": end_active,
            "collections_a_day_end": end_active / EVERY, "upi_needed_end": max(0.0, 1 - CAPACITY * EVERY / end_active)}


def main():
    cases = [("salary, yearly terms", {}), ("salary, savings build up", {"balance": "build"}),
             ("salary, liquid fund (0.08%)", {"trail": 0.0008}), ("salary + 1% of collections, yearly terms", {"commission": 0.01})]
    out = []
    for name, kw in cases:
        for r in (0.30, 0.40, 0.55, 0.70):
            out.append({"case": name, "r12": r, **run(r, **kw)})
    with (T / "npv5.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for x in out:
        print(f"{x['case']:<42} R12 {x['r12']:.0%}: PV cost {x['pv_cost']:>10,.0f} PV rev {x['pv_revenue']:>10,.0f} NPV {x['npv']:>11,.0f} | per sign-up: cost {x['pv_cost_per_signup']:>5,.0f} "
              f"rev {x['pv_revenue_per_signup']:>5,.0f} cross-sell needed {x['cross_sell_pv_needed_per_signup']:>5,.0f} | savers y5 {x['savers_end_y5']:>5,.0f} UPI {x['upi_needed_end']:.0%}")


if __name__ == "__main__":
    main()

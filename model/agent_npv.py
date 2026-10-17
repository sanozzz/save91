"""3-year and 5-year NPV of one street agent, and what it takes to make each positive (operator, 16 Oct 2026):
  "calculate 5 year NPV of the agent. Assume no loans and no insurance, no cross sell nothing"
  "what does it take for us to make sure we are 3 year NPV positive and 5 year NPV positive from this fleet guy"
  agent pay: "20K + 0.5% of balance"  -> read as Rs 20,000 a month + 0.5% a year of the balance his savers hold

Savings-only revenue (fund commission) against the agent's full cost (he both acquires and services), then the
cross-sell each saver must add for NPV >= 0: per saver per year (any product), and as Rs 2.5 lakh loans per 100
proven savers (saved 6+ months) a year, at our 1% fee and at a Paytm-like 4.5% (both less 2.5% taken back).
Same saver and sign-ups as model/agent_npv5.py: Rs 7,000 a month saved, 1,000 sign-ups a year for every year of the
horizon, steady monthly drop-off from R12 = still saving after 12 months; discount 20% a year (tables/inputs.csv).
Balance: 'yearly terms' = half a year's deposits on average (base); 'builds up' = grows Rs 7,000 a month while saving.
Fund commission 0.35% a year on the balance (XB-04 middle). Writes tables/npv_agent.csv and tables/npv_takes.csv.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
SIGNUPS_M, MONTHLY_SAVE, PAY_M = 1000 / 12, 350 * 20, 20000.0
DISC_M = 1.20 ** (1 / 12) - 1
TRAIL = 0.0035
FEE_1, FEE_PAYTM = 250000 * 0.01 * 0.975, 250000 * 0.045 * 0.975
EVIDENCE_LOANS = (0.45, 2.5, 9.8)     # per 100 proven savers a year: low / middle / high (tables/agent3_funnel_inputs.csv)
PAYS = {"salary only": (0.0, None), "salary + 0.5% a year of balance": (0.005, "balance"), "salary + 1% of collections": (0.01, "collected")}
R12S = (0.30, 0.40, 0.55, 0.70)


def run(r12, months, pay, balance="yearly", trail=TRAIL):
    rate, base = PAYS[pay]
    c = 1 - r12 ** (1 / 12)
    pv = {"cost": 0.0, "revenue": 0.0, "saver_years": 0.0, "proven_saver_years": 0.0}
    active_end = 0.0
    for t in range(months):
        active = proven = bal_total = 0.0
        for m in range(t + 1):
            k = t - m + 1
            n = SIGNUPS_M * (1 - c) ** (k - 1)
            active += n
            if k > 6:
                proven += n
            bal_total += n * ((MONTHLY_SAVE * 12 * 0.5) if balance == "yearly" else MONTHLY_SAVE * k)
        comm = 0.0 if base is None else (rate / 12 * bal_total if base == "balance" else rate * active * MONTHLY_SAVE)
        d = (1 + DISC_M) ** (t + 1)
        pv["cost"] += (PAY_M + comm) / d
        pv["revenue"] += bal_total * trail / 12 / d
        pv["saver_years"] += active / 12 / d
        pv["proven_saver_years"] += proven / 12 / d
        active_end = active
    npv = pv["revenue"] - pv["cost"]
    gap = max(-npv, 0.0)
    return {"pv_cost": pv["cost"], "pv_revenue": pv["revenue"], "npv": npv, "savers_end": active_end,
            "cross_sell_per_saver_year_needed": gap / pv["saver_years"],
            "loans_per_100_proven_needed_1pct": 100 * gap / (pv["proven_saver_years"] * FEE_1),
            "loans_per_100_proven_needed_paytm": 100 * gap / (pv["proven_saver_years"] * FEE_PAYTM)}


OTHER_MID, CARD_PER_SIGNUP = 63.0, 0.05 * 1250.0     # XO-39 middle; 5% of sign-ups x Rs 1,250 (BM-08, unverified)


def npv_mix(r12, months, pay, loans_per_100=2.5, fee=FEE_1, other=OTHER_MID, card=CARD_PER_SIGNUP, balance="yearly"):
    """NPV with the middle cross-sell: other products per saver-year, a card fee per sign-up (paid in the month he joins),
    and loans per 100 proven savers a year at the given fee."""
    base = run(r12, months, pay, balance)
    rate, _ = PAYS[pay]
    c = 1 - r12 ** (1 / 12)
    pv_sy = pv_py = pv_cards = 0.0
    for t in range(months):
        active = sum(SIGNUPS_M * (1 - c) ** (t - m) for m in range(t + 1))
        proven = sum(SIGNUPS_M * (1 - c) ** (t - m) for m in range(t + 1) if t - m + 1 > 6)
        d = (1 + DISC_M) ** (t + 1)
        pv_sy += active / 12 / d
        pv_py += proven / 12 / d
        pv_cards += SIGNUPS_M * card / d
    return base["npv"] + other * pv_sy + pv_cards + pv_py * loans_per_100 / 100 * fee


def breakeven_r12(months, pay, **kw):
    if npv_mix(0.95, months, pay, **kw) < 0:
        return None
    lo, hi = 0.05, 0.95
    for _ in range(50):
        m = (lo + hi) / 2
        if npv_mix(m, months, pay, **kw) < 0:
            lo = m
        else:
            hi = m
    return hi


def loans_needed_with_mix(r12, months, pay, fee=FEE_1):
    lo, hi = 0.0, 300.0
    if npv_mix(r12, months, pay, 0.0, fee) >= 0:
        return 0.0
    for _ in range(60):
        m = (lo + hi) / 2
        if npv_mix(r12, months, pay, m, fee) < 0:
            lo = m
        else:
            hi = m
    return hi


def main():
    out = []
    for months in (36, 60):
        for pay in PAYS:
            for bal in ("yearly", "build"):
                for r in R12S:
                    out.append({"years": months // 12, "pay": pay, "balance": bal, "r12": r, **run(r, months, pay, bal)})
    with (T / "npv_agent.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    takes = []
    for months in (36, 60):
        for pay in PAYS:
            for r in R12S:
                takes.append({"years": months // 12, "pay": pay, "r12": r,
                              "npv_savings_only": run(r, months, pay)["npv"],
                              "npv_middle_mix": npv_mix(r, months, pay),
                              "npv_middle_mix_paytm_fee": npv_mix(r, months, pay, fee=FEE_PAYTM),
                              "loans_per_100_needed_on_top_of_products_1pct": loans_needed_with_mix(r, months, pay),
                              "loans_per_100_needed_on_top_of_products_paytm": loans_needed_with_mix(r, months, pay, FEE_PAYTM)})
            be1, bep = breakeven_r12(months, pay), breakeven_r12(months, pay, fee=FEE_PAYTM)
            takes.append({"years": months // 12, "pay": pay, "r12": "break-even", "npv_savings_only": "", "npv_middle_mix": be1 if be1 else "not reachable",
                          "npv_middle_mix_paytm_fee": bep if bep else "not reachable", "loans_per_100_needed_on_top_of_products_1pct": "",
                          "loans_per_100_needed_on_top_of_products_paytm": ""})
    with (T / "npv_takes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(takes[0]))
        w.writeheader()
        w.writerows(takes)
    print("WHAT IT TAKES (yearly terms; middle mix = products Rs 63 a saver-year + cards + 2.5 loans per 100 proven a year)")
    for t in takes:
        if t["r12"] == "break-even":
            f1 = t["npv_middle_mix"]
            fp = t["npv_middle_mix_paytm_fee"]
            print(f"  {t['years']}y {t['pay']:<32} BREAK-EVEN still saving at 12m: 1% fee {f1 if isinstance(f1, str) else f'{f1:.1%}'}; Paytm-like fee {fp if isinstance(fp, str) else f'{fp:.1%}'}")
        else:
            print(f"  {t['years']}y {t['pay']:<32} R12 {t['r12']:.0%}: savings only {t['npv_savings_only']:>11,.0f} | middle mix {t['npv_middle_mix']:>11,.0f} | "
                  f"with Paytm fee {t['npv_middle_mix_paytm_fee']:>11,.0f} | loans/100 needed on top of products: 1% {t['loans_per_100_needed_on_top_of_products_1pct']:>5.1f}, "
                  f"4.5% {t['loans_per_100_needed_on_top_of_products_paytm']:>4.1f}")
    for x in out:
        if x["balance"] == "yearly" or x["pay"] == "salary + 0.5% a year of balance":
            print(f"{x['years']}y {x['pay']:<32} {x['balance']:<6} R12 {x['r12']:.0%}: PV cost {x['pv_cost']:>10,.0f} rev {x['pv_revenue']:>9,.0f} NPV {x['npv']:>11,.0f} | "
                  f"cross-sell/saver-yr {x['cross_sell_per_saver_year_needed']:>5,.0f} | loans/100 proven/yr: 1% {x['loans_per_100_proven_needed_1pct']:>5.1f}, "
                  f"4.5% {x['loans_per_100_proven_needed_paytm']:>4.1f} | savers end {x['savers_end']:>5,.0f}")


if __name__ == "__main__":
    main()

"""Write tables/distributions.csv: the Monte Carlo's view of every uncertain input.

Triangulated rows come from research/tri_costs_summary.md and tri_behaviour_summary.md
(evidence row ids in `evidence`). Inputs the research did not reach keep a PROVISIONAL
range (bear/base/bull widened by half a range, mc_seed.py). Founder decisions and
product design stay fixed.

dist: triangular (low, mode, high) | lognormal (low = P5, high = P95, mode = median) |
beta (params 'a;b'; low/mode/high = P5/mean/P95, for display) | uniform (low, high) |
bernoulli (params = probability of 1) | derived (computed from other draws in mc.py).
Special draws that are not model inputs: ret_m24_ratio, cac_target, pay_flat, pay_pct,
fail_billed (mc.py turns them into engine inputs).
"""
import csv
import math

from scipy import stats

import engine as E
import mc_seed

OUT = E.TABLES / "distributions.csv"
FIELDS = ["input", "segment", "dist", "low", "mode", "high", "params", "sign", "group", "status", "basis", "evidence"]


def tri(i, seg, lo, mo, hi, basis, ev, group="independent", sign=1):
    return dict(input=i, segment=seg, dist="triangular", low=lo, mode=mo, high=hi, params="", sign=sign, group=group,
                status="triangulated", basis=basis, evidence=ev)


def logn(i, seg, p5, p95, basis, ev, group="independent", sign=1):
    return dict(input=i, segment=seg, dist="lognormal", low=p5, mode=round(math.sqrt(p5 * p95), 4), high=p95, params="",
                sign=sign, group=group, status="triangulated", basis=basis, evidence=ev)


def beta(i, seg, a, b, basis, ev, group="independent", sign=1):
    return dict(input=i, segment=seg, dist="beta", low=round(stats.beta.ppf(0.05, a, b), 4), mode=round(a / (a + b), 4),
                high=round(stats.beta.ppf(0.95, a, b), 4), params=f"{a};{b}", sign=sign, group=group, status="triangulated",
                basis=basis, evidence=ev)


def uni(i, seg, lo, hi, basis, ev, status="triangulated"):
    return dict(input=i, segment=seg, dist="uniform", low=lo, mode=(lo + hi) / 2, high=hi, params="", sign=1,
                group="independent", status=status, basis=basis, evidence=ev)


def bern(i, p, basis, ev, status="assumption"):
    return dict(input=i, segment="all", dist="bernoulli", low=0, mode=p, high=1, params=str(p), sign=1, group="independent",
                status=status, basis=basis, evidence=ev)


def derived(i, seg, basis):
    return dict(input=i, segment=seg, dist="derived", low="", mode="", high="", params="", sign=1, group="retention",
                status="triangulated", basis=basis, evidence="")


EVIDENCE = [
    # ---- payments: one pricing switch drives debit and failure costs together
    bern("pay_flat", 0.5, "payment pricing: 1 = flat list price Rs 5 + 18% GST per debit (Cashfree, Zoho); 0 = a % of the debit (Razorpay reported, PhonePe PG 1.99%). Which a new app gets is unknown: 50/50 is an assumption", "TC-02, TC-06, TC-15, TC-16, TC-17"),
    tri("pay_pct", "all", 0.015, 0.02, 0.034, "percentage pricing: share of each debit, incl. GST", "TC-15, TC-16, TC-17"),
    bern("fail_billed", 0.5, "under flat pricing, are failed debits billed at Rs 5.90? No payment company says; 50/50", "TC-05, TC-15"),
    uni("cost_notice", "all", 0.0, 0.15, "pre-debit notice triggered through the payment company; whether billed is unknown", "TC-03, REG-048"),
    # ---- savings revenue
    tri("gold_margin", "all", 0.005, 0.0125, 0.024, "only figure is Jar's ~2.4% (case study); a newcomer gets less of a 2-3% spread", "TC-13, TC-18, TC-19, LEV-036"),
    tri("trail_liquid", "all", 0.00025, 0.0005, 0.001, "trail actually paid: ~0.05% at 5 of 6 fund houses", "TC-21, TC-22"),
    tri("fd_fee", "all", 0.001, 0.003, 0.006, "RBI allows only a sourcing fee for deposits; Stable Money implies <= 0.3-0.4%", "TC-24, TC-25, BM-03"),
    # ---- insurance
    tri("ins_premium", "all", 300, 800, 1500, "what this group buys: accident cover Rs 50-100, hospital cash from ~Rs 799, the IRDAI Bima Vistaar bundle Rs 1,500 (the top); riders already get ~Rs 2,100 of free cover (updated 2 Oct 2026 from Rs 500/1,500/3,500)", "TC-26, TC-27, TC-28, XO-30, XO-34, XO-35"),
    tri("ins_comm_first", "all", 0.05, 0.10, 0.15, "draft caps 15% / 5% with a loan / 2.5-5% group; Bima Vistaar pays 10%", "TC-29, TC-30, REG-054"),
    tri("ins_comm_renew", "all", 0.025, 0.04, 0.05, "draft cap 5%; 2.5% if sold with a loan", "TC-30"),
    tri("ins_uptake", "gig", 0.002, 0.008, 0.025, "PhonePe ~1-2% of users a YEAR; Paytm <1% a quarter for all products; riders have free platform cover", "TB-25, TB-26, TB-27, TB-31, TB-41", "engagement"),
    tri("ins_uptake", "ng", 0.002, 0.012, 0.025, "as gig, but no platform cover", "TB-25, TB-26, TB-31, TB-41", "engagement"),
    beta("ins_persist", "all", 4.5, 5.5, "voluntary micro-insurance renewal 23% -> 46% after redesign; auto-debited PMJJBY/PMSBY 51-70%", "TB-23, TB-24, TB-41", "engagement"),
    # ---- lending
    tri("lsp_fee", "all", 0.0075, 0.015, 0.025, "lead-based sourcing pays 1-3%", "TC-34, LEV-009"),
    tri("dlg_fee_uplift", "all", 0.025, 0.045, 0.07, "uplift prices ~3% losses (Moneyview's cover paid 2.9-3.4%); low losses invite a lower uplift", "TC-41"),
    tri("secured_fee", "all", 0.0025, 0.0075, 0.02, "bank margin on loans against FD 1-2% a year, fees nil-0.5%; no lender found for Rs 2-6k secured loans (founder's 2% is the top)", "TC-31, TC-32, TC-33"),
    tri("loan_apply", "all", 0.005, 0.015, 0.04, "Paytm ~0.9% of users take any product a quarter; Moneyview 8%, GCash 11% ever borrowed; secured-on-own-savings demand weak", "TB-08, TB-31, TB-33, TB-44, LEND-04", "engagement"),
    tri("loan_repeat", "all", 0.30, 0.50, 0.65, "repeat share >50% (Paytm merchant), ~73% (Kissht), 68% PM SVANidhi second loan", "TB-31, TB-43, NG-014", "engagement"),
    tri("ladder_dpd90", "all", 0.005, 0.015, 0.03, "founder's repeat-loan rate 1-2%; no Indian study shows savers default less", "founder, TB-30", "independent"),
    uni("card_uptake", "all", 0.005, 0.03, "no data on FD-secured card take-up: unevidenced", "TB-35, BM-08", status="unevidenced"),
    # ---- running costs
    logn("cost_support", "all", 2.4, 15, "a support contact costs Rs 50-150; Groww non-tech opex Rs 32 per active user (upper bound); no direct data", "TC-37, TC-38"),
    tri("cost_tech", "all", 2, 4, 10, "Jar cloud Rs 0.6-0.8 per registered user; Groww Rs 28.6 tech + transaction per active user", "TC-20, TC-36"),
    tri("cost_fraud", "all", 0.0002, 0.0005, 0.002, "98.5% of fraud value is in payments over Rs 10,000; system ~0.01% of value", "TC-40"),
    # ---- savers' behaviour
    beta("ret_m12", "gig", 4, 16, "small Indian SIPs ~38% at 12m (ceiling); RCTs 3-45%; Jar actives 4-7% of registered; Zomato rider churn high", "TB-01..TB-08, TB-11, TB-12, TB-16, NG-033", "retention"),
    beta("ret_m12", "ng", 5, 15, "as gig, without platform churn", "TB-01..TB-08, TB-11, NG-033", "retention"),
    tri("ret_m24_ratio", "all", 0.4, 0.6, 0.8, "month 24 as a share of month 12: churn flattens after year one (Acorns, SIP vintages, PMJJBY)", "TB-01, TB-02, TB-11, TB-23"),
    derived("ret_m1", "all", "base curve shape scaled to the month-12 draw"),
    derived("ret_m3", "all", "base curve shape scaled to the month-12 draw"),
    derived("ret_m6", "all", "base curve shape scaled to the month-12 draw"),
    derived("ret_m24", "all", "month-12 draw x ret_m24_ratio"),
    tri("churn_late", "all", 0.008, 0.015, 0.03, "Acorns ~1-1.3% monthly churn after year one", "TB-11", "retention", -1),
    logn("daily_amount", "gig", 20, 65, "Jar average purchase ~Rs 64 incl. lump sums; Gullak ~Rs 580 a month; most riders have no buffer", "TB-15, TB-17, TB-40", "engagement"),
    logn("daily_amount", "ng", 25, 110, "Bachatt Rs 51-200 is a product minimum, not behaviour; vendors save more", "TB-40, BAC-05, NG-031", "engagement"),
    tri("debits_success", "gig", 10, 17, 24, "NACH ~69% success by count (salaried EMIs); UPI Autopay 55-90% of attempts failed at major banks, mostly low balance", "TB-13, TB-36, TC-05, LEV-040", "engagement"),
    tri("debits_success", "ng", 12, 19, 25, "as gig; daily UPI receipts help", "TB-13, TB-36, TC-05", "engagement"),
    tri("wk_success", "all", 3.0, 3.9, 4.3, "WEEKLY design only: successful debits a month when one debit lands just after payout day (variants.csv)", "variants.csv weekly_payday", "engagement"),
    logn("cac_target", "gig", 168, 1206, "CAC per activated saver, Rs: Groww Rs 796-1,374 with 83% organic; finance-app CPI Rs 100-300; Jar/Stable Money clear Rs 249 only if half of sign-ups save", "TB-18..TB-22, TB-37, TB-38, BM-04, BM-05"),
    logn("cac_target", "ng", 186, 1340, "as gig x 1.1: no payments firm publishes merchant acquisition cost", "TB-18..TB-22, NG-043"),
]

# Retention points and debit costs are produced from the draws above; their own rows are replaced.
REPLACED = {("cost_debit", "all"), ("cost_failed", "all"), ("cac_mult", "gig"), ("cac_mult", "ng"),
            ("ret_m1", "gig"), ("ret_m1", "ng"), ("ret_m3", "gig"), ("ret_m3", "ng"), ("ret_m6", "gig"), ("ret_m6", "ng"),
            ("ret_m24", "gig"), ("ret_m24", "ng"), ("ret_m12", "gig"), ("ret_m12", "ng"),
            ("daily_amount", "gig"), ("daily_amount", "ng"), ("debits_success", "gig"), ("debits_success", "ng"),
            ("ins_uptake", "all"), ("churn_late", "gig"), ("churn_late", "ng"), ("churn_late", "all"), ("secured_fee", "all")}


def main():
    mc_seed.main()                      # provisional rows for everything
    prov = list(csv.DictReader(open(OUT)))
    have = {(r["input"], r["segment"]) for r in EVIDENCE}
    have_inputs = {r["input"] for r in EVIDENCE}
    rows = []
    for r in prov:
        k = (r["input"], r["segment"])
        if k in have or k in REPLACED or (r["input"] in have_inputs and r["segment"] in ("gig", "ng", "all")):
            continue
        r["params"] = ""
        rows.append(r)
    rows += EVIDENCE
    rows.sort(key=lambda r: (r["status"] != "triangulated", r["input"], r["segment"]))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(Counter(r["status"] for r in rows))


if __name__ == "__main__":
    main()

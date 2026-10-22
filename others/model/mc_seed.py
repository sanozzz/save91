"""Seed tables/distributions.csv from the inputs table: one row per uncertain input
(per segment where the self-employed half differs), PROVISIONAL until triangulated.

Rule for a provisional row: a triangular distribution with its mode at the base value
and its ends half a range past bear and bull, because bear and bull were written as
plausible cases, not hard limits. Founder decisions and product-design timings are
held fixed (listed with dist = fixed). Rows already marked 'triangulated' are kept.
"""
import csv

import engine as E

OUT = E.TABLES / "distributions.csv"
FIELDS = ["input", "segment", "dist", "low", "mode", "high", "params", "sign", "group", "status", "basis", "evidence"]

# Held fixed: founder decisions, product design, accounting conventions.
FIXED = {"gold_share", "gold_on", "dlg_on", "nbfc_on", "dlg_cap", "secured_ltv", "secured_fee", "part_unsec_multiple",
         "mix_gig", "disc_rate", "usd_inr", "cohort_size", "loan_start", "ins_start", "fd_start", "card_start",
         "unsec_start", "sip_start", "loan_tenor", "debits_scheduled", "loan_ticket", "loan_stepup", "loan_dpd90",
         "nbfc_apr", "nbfc_cof", "nbfc_equity", "nbfc_nof_cr", "nbfc_fixed_cr", "nbfc_proc_fee"}
RETENTION = {"ret_m1": 1, "ret_m3": 1, "ret_m6": 1, "ret_m12": 1, "ret_m24": 1, "churn_late": -1}
ENGAGEMENT = {"daily_amount": 1, "debits_success": 1, "amount_growth": 1, "withdraw_rate": -1, "ins_uptake": 1,
              "loan_apply": 1, "card_uptake": 1, "sip_uptake": 1, "loan_repeat": 1, "ins_persist": 1}


def bounds(unit, name):
    u = (unit or "").lower()
    if u.startswith("share") or "share" in name.lower() or u in ("per year",):
        return 0.0, 1.0
    return 0.0, None


def main():
    old = {}
    if OUT.exists():
        for r in csv.DictReader(open(OUT)):
            old[(r["input"], r["segment"])] = r
    rows = []
    for r in csv.DictReader(open(E.TABLES / "inputs.csv")):
        i = r["id"]
        segs = [("all", r["bear"], r["base"], r["bull"])]
        if any(r.get(f"ng_{s}", "") for s in ("bear", "base", "bull")):
            ng = [r.get(f"ng_{s}") or r[s] for s in ("bear", "base", "bull")]
            segs = [("gig", r["bear"], r["base"], r["bull"]), ("ng", *ng)]
        for seg, bear, base, bull in segs:
            if (i, seg) in old and old[(i, seg)]["status"] == "triangulated":
                rows.append(old[(i, seg)])
                continue
            b0, b1, b2 = float(bear), float(base), float(bull)
            group = "retention" if i in RETENTION else ("engagement" if i in ENGAGEMENT else "independent")
            sign = RETENTION.get(i, ENGAGEMENT.get(i, 1))
            if i in FIXED or b0 == b2:
                rows.append(dict(params="", input=i, segment=seg, dist="fixed", low=b1, mode=b1, high=b1, sign=sign, group="fixed",
                                 status="fixed", basis="founder decision, product design or convention" if i in FIXED else "no range given", evidence=""))
                continue
            lo, hi = min(b0, b2), max(b0, b2)
            half = (hi - lo) / 2
            lo2, hi2 = lo - half, hi + half
            dlo, dhi = bounds(r["unit"], r["name"])
            lo2 = max(lo2, dlo)
            hi2 = min(hi2, dhi) if dhi is not None else hi2
            if i == "debits_success":
                hi2 = min(hi2, 30.0)
            rows.append(dict(params="", input=i, segment=seg, dist="triangular", low=round(lo2, 6), mode=b1, high=round(hi2, 6),
                             sign=sign, group=group, status="provisional",
                             basis="bear/base/bull widened by half a range each side", evidence=r.get("source", "")))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    n = sum(1 for r in rows if r["dist"] != "fixed")
    print(f"wrote {len(rows)} rows ({n} uncertain) to {OUT}")


if __name__ == "__main__":
    main()

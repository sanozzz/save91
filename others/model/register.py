"""Write tables/assumption_register.csv: every uncertain input, the founder plan's value, the
evidence distribution, where the plan sits in it, a verdict and how much it matters.

plan_favourable_pct = the share of the evidence distribution the plan's value is MORE
OPTIMISTIC than, where 'optimistic' is the direction of the plan's own best case (bull vs bear
in inputs.csv: more retention, lower costs, higher fees). Payment cost is not scored here: the
evidence is two price shapes (flat Rs 5.90 or ~2% of the debit) and the plan's Rs 2 sits between. Verdict: >= 80% 'plan optimistic'; 60-80% 'plan leans optimistic';
<= 20% 'plan cautious'; else 'plan within evidence'.
"""
import csv

import numpy as np
from scipy import stats

import engine as E
import mc

NAMES = {
    "pay_flat": "Payment pricing: flat Rs 5 + GST per debit (1) or a % of the debit (0)",
    "pay_pct": "Payment fee as a share of each debit (percentage pricing)",
    "fail_billed": "Failed debits billed at the flat price? (flat pricing only)",
    "ret_m12": "Share of savers still saving at month 12",
    "ret_m24_ratio": "Month-24 retention as a share of month-12",
    "cac_target": "Cost to win a saver who makes a first debit (Rs)",
    "wk_success": "Weekly design: successful debits a month",
}


def cdf(r, x):
    lo, mo, hi = r["low"], r["mode"], r["high"]
    if r["dist"] == "triangular":
        c = 0.5 if hi == lo else (mo - lo) / (hi - lo)
        return float(stats.triang.cdf(x, c, loc=lo, scale=hi - lo))
    if r["dist"] == "uniform":
        return float(np.clip((x - lo) / (hi - lo), 0, 1))
    if r["dist"] == "lognormal":
        import math
        mu = (math.log(lo) + math.log(hi)) / 2
        sg = (math.log(hi) - math.log(lo)) / (2 * 1.6448536)
        return float(stats.norm.cdf((math.log(max(x, 1e-9)) - mu) / sg))
    if r["dist"] == "beta":
        a, b = (float(v) for v in r["params"].split(";"))
        return float(stats.beta.cdf(x, a, b))
    return float("nan")


def plan_value(r):
    i, seg = r["input"], r["segment"]
    s = "ng" if seg == "ng" else "gig"
    p = E.load_inputs("base", segment=s)
    if i == "cac_target":
        return E.blended_cac(p, E.load_channels(), s)[0]
    if i == "ret_m24_ratio":
        return p["ret_m24"] / p["ret_m12"]
    if i in ("pay_flat", "pay_pct", "fail_billed", "wk_success"):
        return None
    return p.get(i)


OPTIMISTIC_HIGHER = {"cac_target": False, "ret_m12": True, "ret_m24_ratio": True, "wk_success": True}


def higher_is_optimistic(i):
    if i in OPTIMISTIC_HIGHER:
        return OPTIMISTIC_HIGHER[i]
    for r in csv.DictReader(open(E.TABLES / "inputs.csv")):
        if r["id"] == i:
            return float(r["bull"]) >= float(r["bear"])
    return True


def main():
    names = {r["id"]: r["name"] for r in csv.DictReader(open(E.TABLES / "inputs.csv"))}
    oat = {r["input"]: r for r in csv.DictReader(open(E.TABLES / "sens_oat.csv"))}
    drv = {r["input"]: r for r in csv.DictReader(open(E.TABLES / "mc_drivers.csv")) if r["variant"] == "independent"}
    out = []
    for r in csv.DictReader(open(E.TABLES / "distributions.csv")):
        if r["dist"] in ("fixed", "derived"):
            continue
        for k in ("low", "mode", "high"):
            r[k] = float(r[k])
        k = mc.key(r)
        pv = plan_value(r)
        o = oat.get(k)
        higher_helps = higher_is_optimistic(r["input"])
        fav = ""
        verdict = "no plan value"
        if pv is not None and r["dist"] != "bernoulli":
            pct = cdf(r, pv)
            fav = pct if higher_helps else 1 - pct
            verdict = ("plan optimistic" if fav >= 0.8 else "plan leans optimistic" if fav >= 0.6
                       else "plan cautious" if fav <= 0.2 else "plan within evidence")
        out.append({"input": r["input"], "segment": r["segment"], "assumption": NAMES.get(r["input"], names.get(r["input"], r["input"])),
                    "plan_value": "" if pv is None else pv, "dist": r["dist"], "low": r["low"], "mode": r["mode"], "high": r["high"],
                    "plan_favourable_pct": fav, "verdict": verdict, "status": r["status"], "evidence": r["evidence"], "basis": r["basis"],
                    "variance_share": float(drv[k]["variance_share"]) if k in drv else "",
                    "swing_rs": float(o["swing"]) if o else ""})
    out.sort(key=lambda x: -(x["variance_share"] or 0))
    with open(E.TABLES / "assumption_register.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print(Counter(x["verdict"] for x in out), Counter(x["status"] for x in out))
    for x in out[:16]:
        print(f"{x['input']:<16}{x['segment']:<5} plan {x['plan_value'] if x['plan_value']=='' else round(float(x['plan_value']),4)!s:<10} "
              f"evidence {x['low']:.4g}/{x['mode']:.4g}/{x['high']:.4g}  fav {x['plan_favourable_pct'] if x['plan_favourable_pct']=='' else round(x['plan_favourable_pct'],2)!s:<5} {x['verdict']:<22} {x['status']}")


if __name__ == "__main__":
    main()

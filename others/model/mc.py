"""Monte Carlo and sensitivity over the model's uncertain inputs.

Reads tables/distributions.csv (one row per uncertain input, per segment where the
self-employed half differs), draws N_DRAWS input sets with a fixed seed, runs the
reference engine on each, and writes:

  tables/mc_summary.csv    percentiles and probabilities of each output, per variant
  tables/mc_drivers.csv    which inputs drive net value per saver (rank correlation, variance share)
  tables/mc_hist.csv       histogram of net value per saver, for the chart
  tables/mc_quintiles.csv  odds of a positive saver when a driver sits in its worst / best fifth
  tables/sens_oat.csv      one-at-a-time swings (P10..P90 of each input, others at base) and break-evens
  tables/sens_grid.csv     net value per saver over debit cost x retention level
  tables/mc_samples_<variant>.csv  every draw (inputs and outputs), for audit

Two variants: 'independent' (inputs independent, except the retention curve moves as
one) and 'correlated' (an engagement factor links retention, amounts and take-up:
savers who stay also save more and buy more, which fattens both tails).

Primary metric: NET value per activated saver = LTV (60 months, discounted) - CAC.
The LTV/CAC ratio is reported too, but it misleads when LTV is negative (a cheaper
CAC makes a negative ratio MORE negative), so the odds are stated on net value and
on P(LTV/CAC >= 3).
"""
from __future__ import annotations

import csv
import math

import numpy as np
from scipy import stats

import engine as E

N_DRAWS = 10_000
SEED = 20261002
RHO_SEG = 0.7                       # gig and self-employed retention move together, not identically
VARIANTS = {"independent": (0.0, "daily"), "correlated": (0.5, "daily"), "weekly": (0.0, "weekly")}
T = E.TABLES


def load_dists():
    rows = []
    for r in csv.DictReader(open(T / "distributions.csv")):
        if r["dist"] in ("fixed", "derived"):
            continue
        for k in ("low", "mode", "high"):
            r[k] = float(r[k])
        r["sign"] = int(float(r["sign"]))
        rows.append(r)
    return rows


def ppf(r, u):
    lo, mo, hi = r["low"], r["mode"], r["high"]
    if r["dist"] == "triangular":
        c = 0.5 if hi == lo else (mo - lo) / (hi - lo)
        return stats.triang.ppf(u, c, loc=lo, scale=hi - lo)
    if r["dist"] == "uniform":
        return lo + u * (hi - lo)
    if r["dist"] == "bernoulli":
        return (np.asarray(u) < float(r["params"])).astype(float)
    if r["dist"] == "beta":
        a, b = (float(x) for x in r["params"].split(";"))
        return stats.beta.ppf(u, a, b)
    if r["dist"] == "lognormal":       # low = P5, high = P95, mode unused (median = geometric mean of P5, P95)
        mu = (math.log(lo) + math.log(hi)) / 2
        sigma = (math.log(hi) - math.log(lo)) / (2 * 1.6448536)
        return np.exp(mu + sigma * stats.norm.ppf(u))
    raise ValueError(r["dist"])


def key(r):
    return r["input"] if r["segment"] == "all" else f"{r['input']}@{r['segment']}"


def sample(dists, n, rho, rng):
    eng = rng.standard_normal(n)
    common = rng.standard_normal(n)
    ret = {s: math.sqrt(RHO_SEG) * common + math.sqrt(1 - RHO_SEG) * rng.standard_normal(n) for s in ("gig", "ng")}
    ret["all"] = ret["gig"]
    out = {}
    for r in dists:
        if r["input"] == "ret_m24_ratio":
            z = rng.standard_normal(n)
            out[key(r)] = ppf(r, stats.norm.cdf(z))
            continue
        if r["group"] == "retention":
            z = math.sqrt(rho) * eng + math.sqrt(1 - rho) * ret[r["segment"]]
        elif r["group"] == "engagement":
            z = math.sqrt(rho) * eng + math.sqrt(1 - rho) * rng.standard_normal(n)
        else:
            z = rng.standard_normal(n)
        u = stats.norm.cdf(r["sign"] * z)
        out[key(r)] = ppf(r, u)
    # a retention curve can't rise: month m is at most month m-1
    for seg in ("", "@gig", "@ng"):
        prev = None
        for m in ("ret_m1", "ret_m3", "ret_m6", "ret_m12", "ret_m24"):
            k = m + seg
            if k in out:
                if prev is not None:
                    out[k] = np.minimum(out[k], out[prev])
                prev = k
    return out


# Flat list price per UPI Autopay debit incl. 18% GST: Rs 5 up to Rs 1,000 a debit, Rs 15 above
# (Cashfree and Zoho Payments list prices, TC-02 and TC-06).
FLAT_FEE_LOW, FLAT_FEE_HIGH, FLAT_TIER = 5.9, 17.7, 1000.0


def flat_fee(amount):
    return np.where(np.asarray(amount, dtype=float) > FLAT_TIER, FLAT_FEE_HIGH, FLAT_FEE_LOW)


_CAC = {}


def cac_parts(seg):
    """(fixed part, acquisition part) of the segment's blended CAC: CAC = fixed + acquisition x cac_mult."""
    if seg not in _CAC:
        chans = E.load_channels()
        p = E.load_inputs("base", segment=seg)
        c0 = E.blended_cac({**p, "cac_mult": 0.0}, chans, seg)[0]
        c1 = E.blended_cac({**p, "cac_mult": 1.0}, chans, seg)[0]
        _CAC[seg] = (c0, c1 - c0)
    return _CAC[seg]


def to_overrides(d, design="daily"):
    """Turn one draw (or a dict of arrays) of the distribution table into engine overrides.
    - ret_m12@seg sets the curve: months 1-6 keep the base shape (base^g, g fitted so month 12
      matches), month 24 = month 12 x ret_m24_ratio (the evidence: quitting slows after year one).
    - cac_target@seg is CAC in rupees; it becomes cac_mult@seg via the segment's channel mix."""
    ov = {k: v for k, v in d.items() if not k.startswith(("ret_m24_ratio", "cac_target", "ret_m12", "pay_", "fail_billed", "wk_success"))}
    for seg in ("gig", "ng"):
        k12 = f"ret_m12@{seg}"
        if k12 in d:
            b = E.load_inputs("base", segment=seg)
            m12 = np.clip(d[k12], 0.01, 0.95)
            g = np.log(m12) / math.log(b["ret_m12"])
            for m in ("ret_m1", "ret_m3", "ret_m6"):
                ov[f"{m}@{seg}"] = b[m] ** g
            ov[k12] = m12
            ov[f"ret_m24@{seg}"] = m12 * d.get("ret_m24_ratio", b["ret_m24"] / b["ret_m12"])
        if design == "weekly":   # one debit a week after payout; the same money a month, fewer, larger debits
            b0 = E.load_inputs("base", segment=seg)
            s_d = np.asarray(d.get(f"debits_success@{seg}", b0["debits_success"]))
            a_d = np.asarray(d.get(f"daily_amount@{seg}", b0["daily_amount"]))
            s_w = np.asarray(d["wk_success"])
            d = {**d, f"daily_amount@{seg}": a_d * s_d / s_w}
            ov[f"daily_amount@{seg}"] = d[f"daily_amount@{seg}"]
            ov[f"debits_success@{seg}"] = s_w
            ov["debits_scheduled"] = 4.33
        if "pay_flat" in d:      # one pricing switch sets debit and failure costs together
            amt = d.get(f"daily_amount@{seg}", E.load_inputs("base", segment=seg)["daily_amount"])
            flat = np.asarray(d["pay_flat"])
            fee = flat_fee(amt)
            ov[f"cost_debit@{seg}"] = np.where(flat == 1, fee, np.asarray(d["pay_pct"]) * amt)
            ov[f"cost_failed@{seg}"] = np.where(flat == 1, fee * np.asarray(d["fail_billed"]), 0.0)
        kc = f"cac_target@{seg}"
        if kc in d:
            fixed, acq = cac_parts(seg)
            ov[f"cac_mult@{seg}"] = np.maximum(0.05, (d[kc] - fixed) / acq)
    return ov


def evaluate(ov):
    p, rows, out, _ = E.run("base", ov)
    path = E.path(p, out)
    y10 = path[-1]["rev_usd_m"]
    peak = max(0.0, -min(r["cum_cash"] for r in path)) / 1e7
    pb = out["payback_months"] or 61
    return {"cac": out["cac"], "ltv60": out["ltv60"], "net": out["ltv60"] - out["cac"], "ratio": out["ltv60_cac"],
            "payback": pb, "rev_pa_y2": out["y2_rev_per_active"], "y10_usd_m": y10, "peak_cr": peak}


METRICS = ["net", "ratio", "ltv60", "cac", "payback", "rev_pa_y2", "y10_usd_m", "peak_cr"]
PCTS = [5, 10, 25, 50, 75, 90, 95]


def run_variant(name, rho, dists, design="daily"):
    rng = np.random.default_rng(SEED)
    draws = sample(dists, N_DRAWS, rho, rng)
    keys = list(draws)
    res = {m: np.empty(N_DRAWS) for m in METRICS}
    ovs = to_overrides(draws, design)
    okeys = list(ovs)
    for i in range(N_DRAWS):
        o = evaluate({k: float(np.asarray(ovs[k])[i] if np.ndim(ovs[k]) else ovs[k]) for k in okeys})
        for m in METRICS:
            res[m][i] = o[m]
    with open(T / f"mc_samples_{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw"] + keys + METRICS)
        for i in range(N_DRAWS):
            w.writerow([i] + [f"{draws[k][i]:.6g}" for k in keys] + [f"{res[m][i]:.6g}" for m in METRICS])
    return draws, res


def ranks(a):
    return stats.rankdata(a)


def main():
    dists = load_dists()
    base = evaluate({})
    cen = ev(centre(dists))
    summary, drivers, hist, quint = [], [], [], []
    for name, (rho, design) in VARIANTS.items():
        draws, res = run_variant(name, rho, dists, design)
        if design == "weekly":
            cen_w = evaluate({k: float(np.ravel(v)[0]) for k, v in to_overrides({k: np.asarray([v]) for k, v in centre(dists).items()}, "weekly").items()})
        for m in METRICS:
            v = res[m]
            row = {"variant": name, "metric": m, "base_case": base[m], "evidence_centre": (cen_w if design == "weekly" else cen)[m], "mean": float(v.mean())}
            row.update({f"p{q}": float(np.percentile(v, q)) for q in PCTS})
            summary.append(row)
        probs = {
            "p_net_pos": (res["net"] > 0).mean(),
            "p_ratio_ge1": (res["ratio"] >= 1).mean(),
            "p_ratio_ge3": (res["ratio"] >= 3).mean(),
            "p_payback_le24": (res["payback"] <= 24).mean(),
            "p_y10_ge100": (res["y10_usd_m"] >= 100).mean(),
            "p_y10_ge50": (res["y10_usd_m"] >= 50).mean(),
        }
        for k, v in probs.items():
            summary.append({"variant": name, "metric": k, "mean": float(v)})
        # drivers of net value: Spearman rank correlation, and each input's share of the variance
        # explained by a linear model on ranks (standardised coefficients squared, normalised)
        keys = list(draws)
        y = ranks(res["net"])
        X = np.column_stack([ranks(draws[k]) for k in keys])
        Xs = (X - X.mean(0)) / X.std(0)
        ys = (y - y.mean()) / y.std()
        beta, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
        r2 = 1 - ((ys - Xs @ beta) ** 2).sum() / (ys ** 2).sum()
        share = beta ** 2 / (beta ** 2).sum()
        for j, k in enumerate(keys):
            rho_s = stats.spearmanr(draws[k], res["net"]).statistic
            drivers.append({"variant": name, "input": k, "spearman": float(rho_s), "variance_share": float(share[j]),
                            "rank_model_r2": float(r2)})
        # histogram of net value per saver
        lo, hi = np.percentile(res["net"], [1, 99])
        edges = np.linspace(lo, hi, 31)
        counts, _ = np.histogram(np.clip(res["net"], lo, hi), bins=edges)
        for a, b, c in zip(edges[:-1], edges[1:], counts):
            hist.append({"variant": name, "lo": float(a), "hi": float(b), "share": float(c / N_DRAWS)})
        # what moves the odds: P(net > 0) when each top driver sits in its worst or best fifth
        top = sorted((d for d in drivers if d["variant"] == name), key=lambda d: -d["variance_share"])[:8]
        for d in top:
            v = draws[d["input"]]
            good = v >= np.percentile(v, 80) if d["spearman"] > 0 else v <= np.percentile(v, 20)
            bad = v <= np.percentile(v, 20) if d["spearman"] > 0 else v >= np.percentile(v, 80)
            quint.append({"variant": name, "input": d["input"], "p_net_pos_worst_fifth": float((res["net"][bad] > 0).mean()),
                          "p_net_pos_best_fifth": float((res["net"][good] > 0).mean()),
                          "p_ratio_ge3_best_fifth": float((res["ratio"][good] >= 3).mean())})
        print(f"{name}: net P50 {np.percentile(res['net'], 50):.0f}  P(net>0) {probs['p_net_pos']:.1%}  "
              f"P(LTV/CAC>=3) {probs['p_ratio_ge3']:.1%}  y10 P50 ${np.percentile(res['y10_usd_m'], 50):.0f}M  rank R2 {r2:.2f}")
    write("mc_summary.csv", summary)
    write("mc_drivers.csv", drivers)
    write("mc_hist.csv", hist)
    write("mc_quintiles.csv", quint)
    sensitivity(dists)


def write(name, rows):
    fields = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(T / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def centre(dists):
    """The evidence centre: each draw at its median; payment pricing at the cheaper (percentage) shape."""
    d = {}
    for r in dists:
        d[key(r)] = 0.0 if r["dist"] == "bernoulli" else float(ppf(r, 0.5))
    return d


def ev(d):
    o = to_overrides({k: np.asarray([v]) for k, v in d.items()})
    return evaluate({k: float(np.ravel(v)[0]) for k, v in o.items()})


def centre_tables(dists):
    """Evidence-centre detail per saver (daily and weekly designs), the revenue a saver-year would
    need to break even, and the favourable corner (every input at its helpful 90th percentile)."""
    c = centre(dists)
    out_rows = []
    for design in ("daily", "weekly"):
        ov = to_overrides({k: np.asarray([v]) for k, v in c.items()}, design)
        ov = {k: float(np.ravel(v)[0]) for k, v in ov.items()}
        p, rows, out, _ = E.run("base", ov)
        N = p["cohort_size"]
        dm = (1 + p["disc_rate"]) ** (1 / 12) - 1
        put = lambda m, v: out_rows.append({"design": design, "metric": m, "value": float(v)})
        put("net", out["ltv60"] - out["cac"]); put("ltv60", out["ltv60"]); put("cac", out["cac"])
        put("rev_pa_y2", out["y2_rev_per_active"])
        for k, v in out.items():
            if k.startswith("y2_rev_per_active::"):
                put("rev_pa_y2::" + k.split("::")[1], v)
        st = E.story(p, rows, out)
        cost_y2 = sum(st[f"y2_cost_{s_}"] for s_ in E.COST_LINES)
        put("cost_pa_y2", cost_y2)
        for s_ in E.COST_LINES:
            put(f"cost_pa_y2::{s_}", st[f"y2_cost_{s_}"])
        put("saved_pm_y2", rows[12]["contributions"] / rows[12]["active"])
        for m in (1, 3, 6, 12, 24):
            put(f"still_m{m}", rows[m - 1]["survival"])
        for k in ("borrow_60", "reach3", "reach5", "sec_start", "sec_m12", "rev60_gold", "rev60_loans", "rev60_ins"):
            put(k, st[k])
        pv_act = sum(r["active"] / N / 12 / (1 + dm) ** r["month"] for r in rows)
        pv_rev = sum(r["revenue"] / N / (1 + dm) ** r["month"] for r in rows)
        pv_cost = sum(r["cost"] / N / (1 + dm) ** r["month"] for r in rows)
        put("pv_active_years", pv_act); put("pv_active_months", pv_act * 12)
        put("rev_per_active_year", pv_rev / pv_act); put("cost_per_active_year", pv_cost / pv_act)
        need = (out["cac"] + pv_cost) / pv_act
        put("rev_needed_per_active_year", need); put("rev_needed_multiple", need / (pv_rev / pv_act))
        if design == "daily":       # what one daily debit earns and costs (gig half)
            g = E.load_inputs("base", segment="gig")
            amt = ov.get("daily_amount@gig", g["daily_amount"])
            put("debit_amount_gig", amt)
            put("gold_per_debit", amt * g["gold_share"] * ov.get("gold_margin", g["gold_margin"]))
            put("cost_per_debit_pct", float(ppf([r for r in dists if r["input"] == "pay_pct"][0], 0.5)) * amt)
            put("cost_per_debit_flat", 5.9)
        if design == "daily":       # what would have to change: remove costs one at a time from the centre
            steps = [("free_debits", {"cost_debit@gig": 0.0, "cost_debit@ng": 0.0, "cost_failed@gig": 0.0, "cost_failed@ng": 0.0, "cost_notice": 0.0}),
                     ("free_acquisition", {"cac_mult@gig": 0.0, "cac_mult@ng": 0.0, "__cac0": 1}),
                     ("free_support_tech", {"cost_support": 0.0, "cost_tech": 0.0})]
            cur = dict(ov)
            for name, chg in steps:
                cur.update({k: v for k, v in chg.items() if not k.startswith("__")})
                p2, rows2, out2, _ = E.run("base", cur)
                cac = 0.0 if any("__cac0" in c for _, c in steps[:[n for n, _ in steps].index(name) + 1]) else out2["cac"]
                put(f"whatif_{name}", out2["ltv60"] - cac)
                put(f"whatif_{name}_rev_pa_y2", out2["y2_rev_per_active"])
            put("active_months_5y", sum(r["survival"] for r in rows))
    # favourable corner (daily): every draw at its helpful 90th percentile, cheaper pricing, failures free
    oat = {r["input"]: r for r in csv.DictReader(open(T / "sens_oat.csv"))}
    fav = {}
    for r in dists:
        k = key(r)
        if r["dist"] == "bernoulli":
            fav[k] = 0.0
        else:
            o = oat[k]
            fav[k] = float(o["p90_value"]) if float(o["net_at_p90"]) >= float(o["net_at_p10"]) else float(o["p10_value"])
    res = ev(fav)
    for m in ("net", "ltv60", "cac", "rev_pa_y2"):
        out_rows.append({"design": "corner", "metric": m, "value": float(res[m])})
    write("ev_centre.csv", out_rows)


def sensitivity(dists):
    """One at a time: each input at the 10th and 90th percentile of its distribution, all else at
    base; and the value at which the average saver breaks even (net = 0), searched over 0.25x..4x
    the distribution's range."""
    c = centre(dists)
    base = ev(c)["net"]
    rows = []
    for r in dists:
        k = key(r)
        if r["dist"] == "bernoulli":
            lo_v, hi_v = 0.0, 1.0
        else:
            lo_v, hi_v = float(ppf(r, 0.10)), float(ppf(r, 0.90))
        n_lo, n_hi = ev({**c, k: lo_v})["net"], ev({**c, k: hi_v})["net"]
        rows.append({"input": k, "p10_value": lo_v, "base_value": c[k], "p90_value": hi_v,
                     "net_at_p10": n_lo, "net_at_base": base, "net_at_p90": n_hi, "swing": abs(n_hi - n_lo),
                     "breakeven_value": "" if r["dist"] == "bernoulli" else breakeven(k, r, c)})
    rows.sort(key=lambda x: -x["swing"])
    write("sens_oat.csv", rows)
    # two-way grid: debit cost x retention level (the whole curve, both halves, at one percentile)
    rets = [r for r in dists if r["group"] == "retention"]
    grid = []
    for cd in (0.25, 0.5, 1.0, 2.0, 3.0, 5.9):
        for q in (0.1, 0.25, 0.5, 0.75, 0.9):
            d = dict(c)
            for r in rets:
                d[key(r)] = float(ppf(r, q if r["sign"] > 0 else 1 - q))
            o = to_overrides({k: np.asarray([v]) for k, v in d.items()})
            o = {k: float(np.ravel(v)[0]) for k, v in o.items()}
            o["cost_debit@gig"] = o["cost_debit@ng"] = cd
            o["cost_failed@gig"] = o["cost_failed@ng"] = 0.0
            res = evaluate(o)
            grid.append({"cost_debit": cd, "retention_percentile": q, "ret_m12_gig": d.get("ret_m12@gig"),
                         "net": res["net"], "ratio": res["ratio"]})
    write("sens_grid.csv", grid)
    greedy()
    centre_tables(dists)


def greedy():
    """How many inputs must move to their best-case value before the average saver breaks even?
    Each step moves the one input (both halves) that helps net value most."""
    base, bull = E.load_inputs("base"), E.load_inputs("bull")
    base_n, bull_n = E.load_inputs("base", segment="ng"), E.load_inputs("bull", segment="ng")
    diff = [k for k in base if base[k] != bull[k] or base_n[k] != bull_n[k]]
    cur, rows = {}, []
    start = evaluate({})["net"]
    while True:
        best = None
        for k in diff:
            if any(c.startswith(k + "@") for c in cur):
                continue
            ov = dict(cur)
            ov.update(E.scenario_values("bull", [k]))
            v = evaluate(ov)["net"]
            if best is None or v > best[1]:
                best = (k, v)
        if best is None:
            break
        cur.update(E.scenario_values("bull", [best[0]]))
        rows.append({"step": len(rows) + 1, "input": best[0], "net_after": best[1], "net_start": start})
        if best[1] > 0:
            break
    write("mc_greedy.csv", rows)
    return rows


def breakeven(k, r, c):
    f = lambda x: ev({**c, k: x})["net"]
    span = max(r["high"] - r["low"], abs(r["mode"]) * 0.5, 1e-6)
    a, b = max(1e-4, r["low"] - 4 * span), r["high"] + 4 * span
    if 0 <= r["low"] and r["high"] <= 1:          # a share: keep it inside (0, 1)
        b = min(b, 0.9999)
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return ""
    for _ in range(40):
        m = (a + b) / 2
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return (a + b) / 2


if __name__ == "__main__":
    import sys
    if "--sens-only" in sys.argv:
        sensitivity(load_dists())
    else:
        main()

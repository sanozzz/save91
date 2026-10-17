"""Monte Carlo around every input of the cohort model (operator, 16 Oct 2026: "cohort level modeling needs to happen with
Monte Carlo around input assumptions" ... "everything is a distribution").

10,000 draws, fixed seed. Every input is sampled from its row in cohort_engine.DIST_FILE (by `key`: shape, low, likely,
high): triangular; PERT (beta-PERT, lambda = 4); lognormal (low = P5, likely = median, high = P95); beta (likely = mean,
low/high = P5/P95, matched by the spread); fixed. Sampling is by inverse CDF of uniforms, so a copula can be laid on top.
The uniforms are a Latin hypercube (stratified Monte Carlo: each input's 10,000 draws cover its 10,000 equal-probability
slices once, in random order), which cuts the sampling noise of the median about five-fold against plain random draws;
`--plain` switches to plain draws. r12 < r3 is enforced by redrawing both for the draws that break it.

Bad years (agreed with the operator 16 Oct; the BASE run): approvals and losses move together through a Gaussian copula,
rho = corr_approved_loss from the distribution file (-0.5) between each of approved_first / approved_repeat and loss. The
two approvals are linked only through that bad-year factor, so their own rho is rho^2 = +0.25. `--indep` runs the inputs
independently as a side output (file names end _indep).

Writes tables/cohort_mc_draws.csv, cohort_mc_summary.csv, cohort_mc_drivers.csv, cohort_mc_by_r12.csv,
cohort_mc_convergence.csv, cohort_mc_crosssell.csv (money per saver offered the marketplace, a year, by product), cohort_mc_inputs.csv
(the distribution each key was sampled from, and where it came from) and cohort_mc_must_be_true.csv (chance and median
NPV60 by band of sign-ups, late drop-off and r12, and r12 x sign-ups). With --indep: the same names with _indep.
"""
import csv
import sys
from datetime import date

import numpy as np
from scipy import stats
from scipy.stats import qmc

import cohort_engine as E

DRAWS = 10_000
SEED = 20261016
CHUNK = 2_500
CHUNK_COHORTS = 125          # with calendar growth every draw carries 60 cohort profiles: smaller chunks
RHO_BAD_YEAR = -0.5
COPULA_KEYS = ("approved_first", "approved_repeat", "loss")
PCTS = (5, 10, 25, 50, 75, 90, 95)
XS_KEYS = tuple(f"xs_{p}_per_offered_year" for p, *_ in E.PRODUCTS)
OUT_KEYS = ("npv36", "npv60", "payback_month", "cum_pnl36", "cum_pnl60", "peak_cash_need", "npv36_legacy20", "npv60_legacy20",
            "housing_loans60", "housing_lent60", "housing_fees60", "incentive_total60", "incentive_m12", "incentive_m60",
            "lead_cost60", "savers_m12", "signups_m60", "value_per_signup", "year1_cash", "cum_cash60", "loans_per_100_offered_year",
            "first_loans_per_100_offered_year", "repeat_share_of_loans", "savers_m60", "offered_m60", "visits_peak", "upi_share_m60",
            "upi_share_needed_m60", "extra_capacity_m60", "extra_capacity_total60", "extra_capacity_pv60", "first_extra_capacity_month",
            "p90", "early_plus_p90", "dpd31_90_per_loan", "rec90_per_loan", "collections_per_loan", "year1_collections",
            "xs_total_per_offered_year", *XS_KEYS, "income_per_active_year", "income_per_active_year_m60",
            "topups60", "topups_per_100_borrowers_year", "topups_per_100_loans", "money_lent60",
            *[f"money_lent_y{y}" for y in range(1, 6)], *[f"avg_ticket_y{y}" for y in range(1, 6)],
            "pv60_rev_fund", "pv60_rev_origination", "pv60_rev_dpd31_90", "pv60_rev_recovery90", "pv60_rev_cards", "pv60_rev_crosssell",
            "pv60_cost_extra_capacity", "pv60_cost_kyc", "tenure_months")


def ppf(shape, lo, li, hi, u):
    """Inverse CDF of one input's distribution at uniforms u."""
    if shape == "fixed" or hi == lo:
        return np.full_like(u, li)
    if shape == "triangular":
        return stats.triang.ppf(u, (li - lo) / (hi - lo), loc=lo, scale=hi - lo)
    if shape == "pert":
        a, b = 1 + 4 * (li - lo) / (hi - lo), 1 + 4 * (hi - li) / (hi - lo)
        return lo + (hi - lo) * stats.beta.ppf(u, a, b)
    if shape == "lognormal":
        return np.exp(np.log(li) + (np.log(hi) - np.log(lo)) / (2 * 1.6448536) * stats.norm.ppf(u))
    if shape == "beta":
        sd = (hi - lo) / (2 * 1.6448536)
        k = li * (1 - li) / sd ** 2 - 1
        return stats.beta.ppf(u, li * k, (1 - li) * k)
    raise ValueError(shape)


def bad_year_rho():
    """corr_approved_loss from the distribution file (kind = decision); RHO_BAD_YEAR if the file has none."""
    for r in csv.DictReader(E.DIST_FILE.open()):
        if r["key"] == "corr_approved_loss":
            return float(r["likely"])
    return RHO_BAD_YEAR


def sample(n, seed=SEED, correlate=True, dists=None, plain=False):
    dists = dists or E.load_dists()[0]
    rng = np.random.default_rng(seed + 1_000_003)
    keys = list(E.KEYS)
    U = np.random.default_rng(seed).random((n, len(keys))) if plain else qmc.LatinHypercube(d=len(keys), seed=seed).random(n)
    if correlate:                       # Gaussian copula: independent normals -> correlated normals -> uniforms
        r = bad_year_rho()
        cov = np.array([[1, r * r, r], [r * r, 1, r], [r, r, 1]])
        cols = [keys.index(k) for k in COPULA_KEYS]
        z = stats.norm.ppf(U[:, cols]) @ np.linalg.cholesky(cov).T
        U[:, cols] = stats.norm.cdf(z)
    x = {k: ppf(*dists[k][:4], U[:, i]) for i, k in enumerate(keys)}
    bad = x["r12"] >= x["r3"]
    redraws = 0
    while bad.any():
        redraws += int(bad.sum())
        for k in ("r3", "r12"):
            x[k][bad] = ppf(*dists[k][:4], rng.random(int(bad.sum())))
        bad = x["r12"] >= x["r3"]
    return x, redraws


def simulate(x):
    n = len(x["r12"])
    out = {k: np.empty(n) for k in OUT_KEYS}
    out["_cum"] = np.empty((n, E.MONTHS))                       # cumulative P&L by month, for the fan
    ch = CHUNK_COHORTS if E.calendar_growth(x) else CHUNK
    for s in range(0, n, ch):
        part = {k: v[s:s + ch] for k, v in x.items()}
        res = E.run(part)
        for k in OUT_KEYS:
            out[k][s:s + ch] = res["out"][k]
        out["_cum"][s:s + ch] = res["monthly"]["cum_cash"]
    return out


def pct_row(name, unit, v, note=""):
    v = np.asarray(v, float)
    q = np.percentile(v, PCTS)
    return {"measure": name, "unit": unit, **{f"p{p}": q[i] for i, p in enumerate(PCTS)}, "mean": v.mean(), "value": "", "note": note}


def val_row(name, unit, value, note=""):
    return {"measure": name, "unit": unit, **{f"p{p}": "" for p in PCTS}, "mean": "", "value": value, "note": note}


def summary(x, o, n, correlate, missing, redraws, plain=False):
    pb = np.where(np.isnan(o["payback_month"]), 999.0, o["payback_month"])     # 999 = never within 60 months
    pbq = {p: np.percentile(pb, p, method="lower") for p in (10, 50, 90)}
    show = lambda v: "never within 60 months" if v > 60 else float(v)
    paid = pb <= 60
    rows = [  # round 5 contract: these measure names are read by the deck builder
        pct_row("Cumulative P&L at 36 months", "Rs, undiscounted", o["cum_pnl36"]),
        pct_row("Cumulative P&L at 60 months", "Rs, undiscounted", o["cum_pnl60"]),
        val_row("P(cumulative P&L at 36 months > 0)", "share of draws", (o["cum_pnl36"] > 0).mean()),
        val_row("P(cumulative P&L at 60 months > 0)", "share of draws", (o["cum_pnl60"] > 0).mean()),
        {"measure": "Payback month (cumulative P&L turns positive)", "unit": "month", **{f"p{p}": "" for p in PCTS},
         "p10": show(pbq[10]), "p50": show(pbq[50]), "p90": show(pbq[90]), "mean": "", "value": "",
         "note": "the first month from which cumulative P&L stays positive; draws that never get there count as later than month 60"},
        pct_row("Peak cash need (lowest cumulative P&L)", "Rs", o["peak_cash_need"], "negative: the cash one agent needs before paying back is its size"),
        pct_row("Year-1 P&L", "Rs", o["year1_cash"], "months 1-12"),
        val_row("Share of draws that never pay back within 60 months", "share of draws", 1 - paid.mean()),
        pct_row("NPV (legacy, 20% discount): NPV at 36 months", "Rs", o["npv36_legacy20"], "kept for reference only"),
        pct_row("NPV (legacy, 20% discount): NPV at 60 months", "Rs", o["npv60_legacy20"], "kept for reference only"),
        pct_row("Value per sign-up, his first 5 years (undiscounted)", "Rs", o["value_per_signup"], "a month-1 sign-up, before the agent's salary"),
        pct_row("Home loans and LAP made per agent in 60 months", "loans", o["housing_loans60"], "other lenders' loans; we earn the sourcing fee"),
        pct_row("Home-loan and LAP money per agent in 60 months", "Rs", o["housing_lent60"], "lent by other lenders, on their books"),
        pct_row("Our fees on home loans and LAP per agent in 60 months", "Rs", o["housing_fees60"]),
        pct_row("Agent pay on balance per agent in 60 months", "Rs", o["incentive_total60"], "0.25% a year of his savers' average balance"),
        pct_row("Agent pay on balance in month 60", "Rs a month", o["incentive_m60"]),
        pct_row("Online lead cost per agent in 60 months", "Rs", o["lead_cost60"], "online_lead_share x lead_cost x sign-ups"),
        pct_row("Helper cost (extra cash-collection capacity) per agent in 60 months", "Rs", o["extra_capacity_total60"],
                "Rs 20,000 a month per 400 cash visits a day above one agent's 400, pro-rata"),
        pct_row("Savers still saving at month 60", "savers", o["savers_m60"]),
        pct_row("Sign-ups in month 60", "sign-ups a month", o["signups_m60"]),
        pct_row("Loans per 100 savers offered the marketplace, a year (first + repeat)", "loans", o["loans_per_100_offered_year"]),
        pct_row("First loans per 100 savers offered the marketplace, a year", "loans", o["first_loans_per_100_offered_year"]),
        pct_row("Repeat loans as a share of all loans (60 months)", "share", np.nan_to_num(o["repeat_share_of_loans"])),
        pct_row("UPI share needed at month 60 to stay within one agent's cash visits", "share", o["upi_share_needed_m60"]),
        pct_row("UPI share at month 60 (modelled)", "share", o["upi_share_m60"]),
        pct_row("Peak cash visits a day", "visits a day", o["visits_peak"]),
        val_row("Share of draws that need extra cash-collection capacity", "share of draws", (o["extra_capacity_total60"] > 0).mean()),
        pct_row("Extra capacity cost in month 60", "Rs a month", o["extra_capacity_m60"]),
        pct_row("Extra capacity cost, 60 months, discounted", "Rs", o["extra_capacity_pv60"]),
        pct_row("Cross-sell money per saver offered the marketplace, a year, all 17 products", "Rs", o["xs_total_per_offered_year"],
                "against the old Rs 63 (XO-39); by product in cohort_mc_crosssell.csv"),
        pct_row("31-90 day collection fees per loan made", "Rs a loan", o["dpd31_90_per_loan"], "early_cured x fee_early, paid about 9 months after the loan"),
        pct_row("90+ recovery fees per loan made", "Rs a loan", o["rec90_per_loan"], "p90 x recovered x fee_b3, paid about 18 months after the loan"),
        pct_row("Implied share of loans that ever go 90+ days bad (p90)", "share of loans", o["p90"],
                "p90 = loss / (0.5 x (1 - recovered)); CRIF NG-015 10.2% (self-employed, < Rs 10 lakh, peak), MAC-03 3.6%"),
        pct_row("Early brought back + p90", "share of loans", o["early_plus_p90"], "page check: at most 50%"),
        val_row("Share of draws where early brought back + p90 is above 50%", "share of draws", (o["early_plus_p90"] > E.EARLY_P90_CAP).mean()),
        pct_row("Collection fees in the pilot year", "Rs", o["year1_collections"], "fees arrive 9 and 18 months after a loan: mostly year-2+ money"),
        pct_row("All-in revenue per active saver a year (60-month average)", "Rs", o["income_per_active_year"],
                "fund + loans + cards + products + collections; Paytm XO-11: Rs 407 a monthly user a year from financial services"),
        pct_row("All-in revenue per active saver a year, month-60 run rate", "Rs", o["income_per_active_year_m60"]),
        pct_row("Top-ups per 100 borrowers a year", "top-ups", o["topups_per_100_borrowers_year"], "borrowers still saving with a loan running"),
        pct_row("Money lent per agent in 60 months", "Rs", o["money_lent60"], "first, repeat and top-up loans"),
        *[pct_row(f"Money lent per agent, year {y}", "Rs", o[f"money_lent_y{y}"]) for y in range(1, 6)],
        *[pct_row(f"Average ticket of first and repeat loans, year {y}", "Rs", np.nan_to_num(o[f"avg_ticket_y{y}"], nan=0.0)) for y in range(1, 6)],
        val_row("Draws", "count", n, f"seed {SEED}; {'plain random' if plain else 'Latin hypercube'} sampling; correlation "
                f"{'ON (bad years linked, rho %g, agreed)' % bad_year_rho() if correlate else 'OFF (inputs independent)'}; "
                f"{redraws} r3/r12 pairs redrawn to keep r12 < r3"),
        val_row("Distribution file", "", E.DIST_FILE.name, f"read {date.today().isoformat()}; {len(missing)} of {len(E.KEYS)} keys "
                f"from the fallback (COHORT_INPUTS and addenda), listed in cohort_mc_inputs.csv; fund commission: {E.FUND} fund"),
    ]
    return rows


def drivers(x, o):
    rows = []
    y = o["cum_pnl60"]                                   # round 5: cumulative P&L at 60 months (equals npv60 at discount 0)
    for k in E.KEYS:
        v = x[k]
        if np.ptp(v) == 0:
            continue
        rho = stats.spearmanr(v, y).statistic
        lo, hi = np.percentile(v, (10, 90))
        top, bot = y[v >= hi].mean(), y[v <= lo].mean()
        rows.append({"key": k, "input": E.NAMES[k], "spearman_with_npv60": rho, "swing_npv60_top_minus_bottom_decile": top - bot,
                     "spearman_with_cum_pnl60": rho, "swing_cum_pnl60_top_minus_bottom_decile": top - bot,
                     "mean_npv60_bottom_decile": bot, "mean_npv60_top_decile": top, "input_p10": lo, "input_p90": hi})
    rows.sort(key=lambda r: -abs(r["spearman_with_npv60"]))
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


def by_r12(x, o):
    rows = []
    for lo in range(25, 75, 5):
        m = (x["r12"] >= lo / 100) & (x["r12"] < (lo + 5) / 100)
        n = int(m.sum())
        rows.append({"r12_band": f"{lo}-{lo + 5}", "still_saving_at_month_12": f"{lo}% to {lo + 5}%", "draws": n,
                     "chance_cum_pnl60_above_zero": (o["cum_pnl60"][m] > 0).mean() if n else "", "median_cum_pnl60": np.median(o["cum_pnl60"][m]) if n else "",
                     "chance_npv60_above_zero": (o["npv60"][m] > 0).mean() if n else "", "median_npv60": np.median(o["npv60"][m]) if n else "",
                     "chance_npv36_above_zero": (o["npv36"][m] > 0).mean() if n else "", "median_npv36": np.median(o["npv36"][m]) if n else ""})
    return rows


def convergence(o10, o5_indep):
    """5,000 vs 10,000 draws. P(NPV > 0) in percentage points. The median in two units: % of the 10,000-draw median,
    and its percentile rank in the 10,000 draws minus 50 (percentile points: the same unit as P(NPV > 0))."""
    rows = []
    rank = lambda big, v: 100 * (big < v).mean() - 50
    for name, a10, a5n, a5i in (
            ("median NPV at 36 months (Rs)", np.median(o10["npv36"]), np.median(o10["npv36"][:5000]), np.median(o5_indep["npv36"])),
            ("median NPV at 60 months (Rs)", np.median(o10["npv60"]), np.median(o10["npv60"][:5000]), np.median(o5_indep["npv60"])),
            ("chance NPV at 36 months above zero (points)", 100 * (o10["npv36"] > 0).mean(), 100 * (o10["npv36"][:5000] > 0).mean(), 100 * (o5_indep["npv36"] > 0).mean()),
            ("chance NPV at 60 months above zero (points)", 100 * (o10["npv60"] > 0).mean(), 100 * (o10["npv60"][:5000] > 0).mean(), 100 * (o5_indep["npv60"] > 0).mean())):
        is_p = "points" in name
        spread = np.percentile(o10["npv60" if "60" in name else "npv36"], 90) - np.percentile(o10["npv60" if "60" in name else "npv36"], 10)
        d_n, d_i = a5n - a10, a5i - a10
        rel = lambda d: d if is_p else 100 * d / abs(a10)
        big = o10["npv60" if "60" in name else "npv36"]
        rk = ("", "") if is_p else (rank(big, a5n), rank(big, a5i))
        rows.append({"measure": name, "draws_10000": a10, "first_5000_of_them": a5n, "independent_5000": a5i,
                     "rank_shift_first_5000_points": rk[0], "rank_shift_independent_5000_points": rk[1],
                     "diff_first_5000": d_n, "diff_independent_5000": d_i,
                     "diff_first_5000_points": rel(d_n), "diff_independent_5000_points": rel(d_i),
                     "diff_independent_as_pct_of_p10_p90_spread": "" if is_p else 100 * d_i / spread,
                     "within_1_point_first_5000": abs(rel(d_n)) <= 1, "within_1_point_independent_5000": abs(rel(d_i)) <= 1,
                     "note": "points = percentage points" if is_p else "points = % of the 10,000-draw median"})
    return rows


def crosssell_table(o):
    rows = []
    for p, kind, nm, _d in E.PRODUCTS + [("total", "", "All 17 products", None)]:
        v = o[f"xs_{p}_per_offered_year"]
        q = np.percentile(v, (10, 50, 90))
        rows.append({"product": nm, "key": p, "kind": kind, "p10": q[0], "p50": q[1], "p90": q[2], "mean": v.mean(),
                     "unit": "Rs a saver offered a year (money in 60 months / years of savers offered the marketplace)"})
    rows.append({"product": "Old single line (XO-39 middle)", "key": "other_v2", "kind": "", "p10": "", "p50": 63.0, "p90": "", "mean": "",
                 "unit": "Rs a saver a year"})
    return rows


def inputs_table(dists, missing, notes):
    return [{"key": k, "input": E.NAMES[k], "shape": v[0], "low": v[1], "likely": v[2], "high": v[3],
             "from": "fallback (COHORT_INPUTS / addenda)" if k in missing else ("code (operator decision)" if "enforced" in notes.get(k, "") or "addendum used" in notes.get(k, "") else E.DIST_FILE.name),
             "note": notes.get(k, ""), "source": v[4]} for k, v in dists.items()]


BANDS = {  # key: (plain name, [(label, low, high)]) with high inclusive only for the last band
    "signups_run": ("Sign-ups a month", [("60-80", 60, 80), ("80-100", 80, 100), ("100-120", 100, 120), ("120-150", 120, 150)]),
    "churn_late": ("Monthly drop-off after month 12", [("1.0-1.5%", .010, .015), ("1.5-2.0%", .015, .020), ("2.0-2.5%", .020, .025),
                                                       ("2.5-3.0%", .025, .030)]),
    "r12": ("Still saving at month 12", [(f"{lo}-{lo + 5}%", lo / 100, (lo + 5) / 100) for lo in range(25, 75, 5)]),
    "takeup_growth": ("Take-up growth a year", [("0-5%", 0.0, 0.05), ("5-10%", 0.05, 0.10), ("10-20%", 0.10, 0.20)]),
    "approval_growth": ("Approval growth a year", [("0-5%", 0.0, 0.05), ("5-10%", 0.05, 0.10), ("10-20%", 0.10, 0.20)]),
}


def _in(v, lo, hi, last):
    return (v >= lo) & ((v <= hi) if last else (v < hi))


def must_be_true(x, o):
    rows = []
    cell = lambda m: {"draws": int(m.sum()), "chance_npv60_above_zero": (o["npv60"][m] > 0).mean() if m.any() else "",
                      "median_npv60": float(np.median(o["npv60"][m])) if m.any() else "",
                      "chance_npv36_above_zero": (o["npv36"][m] > 0).mean() if m.any() else "",
                      "few_draws": "yes" if m.sum() < 50 else "",
                      "chance_cum_pnl60_above_zero": (o["cum_pnl60"][m] > 0).mean() if m.any() else "",
                      "median_cum_pnl60": float(np.median(o["cum_pnl60"][m])) if m.any() else "",
                      "chance_cum_pnl36_above_zero": (o["cum_pnl36"][m] > 0).mean() if m.any() else ""}
    for k, (nm, bands) in BANDS.items():
        for i, (lab, lo, hi) in enumerate(bands):
            m = _in(x[k], lo, hi, i == len(bands) - 1)
            rows.append({"table": f"by {nm.lower()}", "input": nm, "band": lab, "second_input": "", "second_band": "", **cell(m)})
    rb, sb = BANDS["r12"][1], BANDS["signups_run"][1]
    for i, (rl, rlo, rhi) in enumerate(rb):
        mr = _in(x["r12"], rlo, rhi, i == len(rb) - 1)
        for j, (sl, slo, shi) in enumerate(sb):
            m = mr & _in(x["signups_run"], slo, shi, j == len(sb) - 1)
            rows.append({"table": "r12 x sign-ups", "input": "Still saving at month 12", "band": rl, "second_input": "Sign-ups a month",
                         "second_band": sl, **cell(m)})
    return rows


def main(correlate=True, plain=False, marketplace_from=None):
    sfx = ("" if correlate else "_indep") + ("_plain" if plain else "") + (f"_mkt{marketplace_from}" if marketplace_from else "")
    dists, missing, aliased = E.load_dists()
    if marketplace_from:                           # side run: the same draws with the marketplace opening later
        dists = {**dists, "marketplace_from": ("fixed", marketplace_from, marketplace_from, marketplace_from, "side run")}
    E.write(f"cohort_mc_inputs{sfx}.csv", inputs_table(dists, missing, aliased))
    x, redraws = sample(DRAWS, SEED, correlate, dists, plain)
    o = simulate(x)
    x5, _ = sample(5000, SEED + 1, correlate, dists, plain)
    o5 = simulate(x5)
    E.write(f"cohort_mc_draws{sfx}.csv", [{"draw": i + 1, **{k: float(x[k][i]) for k in E.KEYS}, **{k: float(o[k][i]) for k in OUT_KEYS}}
                                         for i in range(DRAWS)])
    q = np.percentile(o["_cum"], (10, 25, 50, 75, 90), axis=0)
    E.write(f"cohort_mc_cum_fan{sfx}.csv", [{"month": t + 1, "p10": q[0, t], "p25": q[1, t], "p50": q[2, t], "p75": q[3, t], "p90": q[4, t],
                                            "mean": float(o["_cum"][:, t].mean()), "unit": "Rs, cumulative P&L, undiscounted"}
                                           for t in range(E.MONTHS)])
    summ = summary(x, o, DRAWS, correlate, missing, redraws, plain)
    E.write(f"cohort_mc_summary{sfx}.csv", summ)
    drv = drivers(x, o)
    E.write(f"cohort_mc_drivers{sfx}.csv", drv)
    br = by_r12(x, o)
    E.write(f"cohort_mc_by_r12{sfx}.csv", br)
    conv = convergence(o, o5)
    E.write(f"cohort_mc_convergence{sfx}.csv", conv)
    xs = crosssell_table(o)
    E.write(f"cohort_mc_crosssell{sfx}.csv", xs)
    mbt = must_be_true(x, o)
    E.write(f"cohort_mc_must_be_true{sfx}.csv", mbt)
    print(f"{DIST_NOTE(missing, aliased)}; correlation {'ON' if correlate else 'OFF'}; redraws {redraws}")
    print(f"  {len(missing)} fallback keys; notes {aliased}")
    for r in summ:
        if r["value"] != "":
            print(f"  {r['measure']:<70} {r['value']}")
        else:
            print(f"  {r['measure']:<70} p10 {r['p10']!s:>12.12} p50 {r['p50']!s:>12.12} p90 {r['p90']!s:>12.12} mean {r['mean']!s:>12.12}")
    for r in xs:
        print(f"  xs {r['product']:<40} p10 {r['p10']!s:>8.8} p50 {r['p50']!s:>8.8} p90 {r['p90']!s:>8.8}")
    for r in drv[:12]:
        print(f"  driver {r['rank']:>2} {r['key']:<16} rho {r['spearman_with_npv60']:+.3f}  swing {r['swing_npv60_top_minus_bottom_decile']:>12,.0f}")
    for r in br:
        print(f"  r12 {r['r12_band']}: n {r['draws']:>5}  P(NPV60>0) {r['chance_npv60_above_zero'] if r['draws'] else float('nan'):.2f}  median NPV60 "
              f"{r['median_npv60'] if r['draws'] else float('nan'):>12,.0f}")
    for r in conv:
        print(f"  conv {r['measure']:<45} 10k {r['draws_10000']:>12,.2f} | first 5k {r['first_5000_of_them']:>12,.2f} ({r['diff_first_5000_points']:+.2f}) "
              f"| indep 5k {r['independent_5000']:>12,.2f} ({r['diff_independent_5000_points']:+.2f})"
              + (f" | rank shift {r['rank_shift_first_5000_points']:+.2f} / {r['rank_shift_independent_5000_points']:+.2f}" if r['rank_shift_first_5000_points'] != "" else ""))
    return summ, drv, br, conv


def DIST_NOTE(missing, aliased):
    return f"distributions {E.DIST_FILE.name}"


if __name__ == "__main__":
    av = sys.argv[1:]
    mkt = int(av[av.index("--marketplace-from") + 1]) if "--marketplace-from" in av else None
    main(correlate="--indep" not in av, plain="--plain" in av, marketplace_from=mkt)

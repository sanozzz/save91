"""Monte Carlo of the company model (model/company_model.py): 2,000 draws, fixed seed.

Per draw:
  - market inputs (retention, saving, fund, take-ups, approvals, loan sizes, fees, losses, costs per saver, the agent's capacity
    and ramp, and so on: every cohort_engine key) are drawn ONCE, common to all agents, with cohort_mc.sample(): Latin hypercube
    on the agreed distributions (tables/dist_agreed_v1.csv), approvals and losses linked by the bad-year copula (rho -0.5);
  - a COMMON sign-up factor (fix 6): that draw's market-level signups_run over its likely value (PERT 60/100/150 -> 0.6 to 1.5),
    scaling every agent in the draw: a good or bad market for opening accounts moves the whole fleet together;
  - on top of it, every agent (each growth hire and each replacement, about 490 a draw) draws his OWN sign-up level and decline
    from their agreed distributions. No agent types are needed: the per-sign-up lines do not depend on the agent, so each
    agent's own sign-up stream enters the stacking exactly (company_model.simulate); helpers, cash cover and pay on balance are
    worked per book;
  - attrition: the same 2.5% a month in whole agents as the deterministic run, with WHO leaves drawn afresh in each draw.
The company inputs (fleet path, team, costs, funding) are the agreed point values in company_model.py: the round-10 base (80
agents by m18 then replace leavers, pay on balance capped at Rs 10,000, central lean hold with its trigger worked per draw, UPI
30% as drawn, Series A Rs 50 crore). Each draw's fleet has its own seed (FLEET_SEED + draw). The Series A tests
(seed run-out, the latest close, the m21 and m24 slips, the smallest A) are run per draw on that draw's operating lines.

Writes tables/company_mc_summary.csv, and adds the Monte Carlo headroom lines (Series A less the smallest A, at the p50 and
the p90 need) to tables/company_m18.csv, which company_model.py writes first.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import cohort_mc as MC             # noqa: E402
import company_model as C          # noqa: E402

DRAWS = 2_000
SEED = 20261017
CHUNK = 100
PCTS = (10, 50, 90)


FLEET_SEED = SEED + 10_000             # draw d's fleet seed = FLEET_SEED + d


def run_mc(n=DRAWS, seed=SEED, plan=None):
    """plan: company_model.run_plan keyword arguments plus "upi" (None = the market draw stands; a number = an operational
    target fixed in every draw) and "over" (input overrides). Default: the round-10 base."""
    plan = dict(plan or {"central": C.BASE_CENTRAL})
    upi, over = plan.pop("upi", None), plan.pop("over", {})
    dists = E.load_dists()[0]
    x, redraws = MC.sample(n, seed, correlate=True, dists=dists)
    factor = x["signups_run"] / dists["signups_run"][2]       # the common sign-up factor
    out = {}
    for s in range(0, n, CHUNK):
        part = {k: v[s:s + CHUNK] for k, v in x.items()}
        D = len(part["r12"])
        part = {**part, **over, **({"upi_12": np.full(D, upi)} if upi is not None else {})}
        o, fleets, _t, info = C.run_plan(part, dists, seeds=[FLEET_SEED + s + d for d in range(D)], factors=factor[s:s + D], **plan)
        h = C.headline(o)
        h["agents_hired_60"] = o["hired"].sum(axis=1)
        h["mean_signups_run_of_hires"] = np.array([f["signups_run"].mean() for f in fleets])
        h["signup_factor"] = factor[s:s + D]
        h["central_released"] = (info["release"] > 0).astype(float)
        for k, v in h.items():
            out.setdefault(k, []).append(np.asarray(v, float))
        print(f"  draws {s + D}/{n}", flush=True)
    return {k: np.concatenate(v) for k, v in out.items()}, x, redraws


def pct_row(name, unit, v, note=""):
    q = np.percentile(np.asarray(v, float), PCTS)
    return {"Measure": name, "Unit": unit, "P10": q[0], "Median (P50)": q[1], "P90": q[2], "Mean": float(np.mean(v)), "Value": "",
            "Note": note}


def val_row(name, unit, value, note=""):
    return {"Measure": name, "Unit": unit, "P10": "", "Median (P50)": "", "P90": "", "Mean": "", "Value": value, "Note": note}


def share_row(name, flags, n, note=""):
    """A share of draws, quoted with its 95% sampling margin."""
    p = float(np.mean(flags))
    pct, pp = 100 * p, 100 * 1.96 * np.sqrt(p * (1 - p) / n)
    txt = f"about {pct:.0f}% +/- {max(1, round(pp)):.0f}pp" if 2 <= pct <= 98 else f"about {pct:.1f}% +/- {pp:.1f}pp"
    return val_row(name, "share of draws", p, f"{txt} (95% sampling margin, {n:,} draws)" + (f"; {note}" if note else ""))


def month_row(name, v, note):
    """Month measures with 'never' draws counted as later than month 60."""
    w = np.where(np.isnan(v), 999.0, v)
    q = [np.percentile(w, p, method="lower") for p in PCTS]
    show = lambda m: "never within 60 months" if m > 60 else float(m)
    return {"Measure": name, "Unit": "company month", "P10": show(q[0]), "Median (P50)": show(q[1]), "P90": show(q[2]), "Mean": "",
            "Value": "", "Note": note}


def summary(h, n, redraws):
    be = h["ebitda_breakeven_month"]
    rows = [
        val_row("Draws", "draws", n, f"seed {SEED}; market inputs Latin hypercube with the bad-year copula; r12 < r3 redraws {redraws}"),
        pct_row("Common sign-up factor (all agents in a draw)", "x each agent's own draw", h["signup_factor"],
                "the draw's market-level signups_run over 100 (fix 6)"),
        share_row("P(cash stays above 0, seed only, through m18)", h["cash_positive_seed_to_18"], n, "every month end 1-18, no Series A"),
        pct_row("Lowest cash, seed only, through m18", "Rs", h["min_cash_seed_to_18"], "negative = the gap"),
        month_row("Month of the lowest cash, seed only, through m18", h["min_cash_seed_to_18_month"], ""),
        month_row("Month the seed alone runs out", h["seed_runout_month"], "first month-end below 0 with no Series A"),
        month_row("The Series A must close by month", h["a_close_by_month"],
                  f"the latest month-end the Rs {C.SERIES_A / C.CRORE:.0f} crore can land without cash going below 0 before it"),
        *[r for s in C.SLIP_MONTHS for r in (
            pct_row(f"Series A slips to month {s}: lowest cash through m60", "Rs", h[f"slip{s}_min_cash"]),
            share_row(f"Series A slips to month {s}: P(cash goes below 0)", h[f"slip{s}_below0"], n))],
        pct_row(f"Headroom over the minimum A: Rs {C.SERIES_A / C.CRORE:.0f} crore less the smallest A", "Rs", C.SERIES_A - h["smallest_a"],
                "P10 = the headroom when the need is at its P90 (the tight case)"),
        pct_row("Smallest Series A at month 18 that keeps cash at or above Rs 5 crore through m60", "Rs", h["smallest_a"],
                f"searched per draw; found in {h['smallest_a_found'].mean():.0%} of draws (search ceiling Rs {C.A_SEARCH_MAX / C.CRORE:.0f} crore)"),
        share_row("P(cash stays above 0, with the Series A, through m60)", h["cash_positive_60"], n,
                  f"seed Rs 10 crore + Series A Rs {C.SERIES_A / C.CRORE:.0f} crore at m18; every month end 1-60"),
        pct_row("Lowest cash, with the Series A, through m60", "Rs", h["min_cash_60"], ""),
        month_row("Month of the lowest cash, with the Series A, through m60", h["min_cash_60_month"], ""),
        pct_row(f"Extra funding needed to month 60, beyond the seed and the Rs {C.SERIES_A / C.CRORE:.0f} crore A", "Rs", h["extra_funding_60"], "0 = none"),
        share_row("Share of draws that need extra funding to month 60", h["extra_funding_60"] > 0, n),
        *[share_row(f"P(EBITDA break-even by m{m})", np.nan_to_num(be, nan=999) <= m, n, "first month positive and staying positive")
          for m in (36, 42, 48)],
        share_row("P(EBITDA breaks even within 60 months)", ~np.isnan(be), n, "EBITDA stays positive from some month to month 60"),
        month_row("EBITDA break-even month", be, "the first month from which monthly EBITDA stays positive to month 60"),
        month_row("First month with positive EBITDA", h["first_ebitda_positive_month"], "may dip again later"),
        *[pct_row(f"Year-5 {nm}", "Rs", h[f"{k}_y5"], "months 49-60") for k, nm in
          (("revenue", "revenue"), ("cm1", "CM1"), ("cm2", "CM2"), ("cm3", "CM3"), ("ebitda", "EBITDA"),
           ("interest", "interest on cash"), ("pat", "PAT"))],
        *[pct_row(f"Year-{y} revenue", "Rs", h[f"revenue_y{y}"]) for y in range(1, 5)],
        *[pct_row(f"Year-{y} EBITDA", "Rs", h[f"ebitda_y{y}"]) for y in range(1, 5)],
        pct_row("Cumulative PAT at month 60", "Rs", h["cum_pat_60"], "undiscounted"),
        pct_row("Cash at month 60, with the Series A", "Rs", h["cash_60"], ""),
        pct_row("Savers still saving at month 18", "savers", h["savers_m18"]),
        pct_row("Savers still saving at month 60", "savers", h["savers_m60"]),
        pct_row("Money in the fund (AUM) at month 18", "Rs", h["aum_m18"]),
        pct_row("Money in the fund (AUM) at month 60", "Rs", h["aum_m60"]),
        pct_row("Money lent, months 1-18", "Rs", h["money_lent_to_m18"], "personal loans incl. top-ups"),
        pct_row("Money lent, 60 months", "Rs", h["money_lent_60"], "personal loans incl. top-ups"),
        pct_row("Revenue in month 18", "Rs a month", h["revenue_m18"]),
        pct_row("Agents hired in 60 months, incl. replacements", "agents", h["agents_hired_60"]),
        pct_row("Average year-1 sign-up level of the agents hired", "sign-ups a month", h["mean_signups_run_of_hires"],
                "each agent's own draw x the common factor"),
        share_row("Share of draws where the lean hold ends (EBITDA turns positive) within 60 months", h["central_released"] > 0, n),
    ]
    return rows


def add_headroom_to_m18(h):
    """company_m18.csv: the headroom over the minimum A at the median and the p90 need (Monte Carlo)."""
    import csv
    path = C.T / "company_m18.csv"
    rows = [r for r in csv.DictReader(path.open()) if not r["Measure"].startswith("Headroom over the minimum A, Monte Carlo")]
    need50, need90 = np.percentile(h["smallest_a"], (50, 90))
    i = next(j for j, r in enumerate(rows) if r["Measure"].startswith("Headroom over the minimum A")) + 1
    rows[i:i] = [{"Measure": "Headroom over the minimum A, Monte Carlo p50", "Value": C.SERIES_A - need50, "Unit": "Rs",
                  "How it is worked out": f"Rs {C.SERIES_A / C.CRORE:.0f} crore less the median smallest A (Rs {need50:,.0f})"},
                 {"Measure": "Headroom over the minimum A, Monte Carlo p90", "Value": C.SERIES_A - need90, "Unit": "Rs",
                  "How it is worked out": f"Rs {C.SERIES_A / C.CRORE:.0f} crore less the p90 smallest A (Rs {need90:,.0f}): the tight case"}]
    C.write("company_m18.csv", rows)


def main():
    h, _x, redraws = run_mc()
    rows = summary(h, DRAWS, redraws)
    C.write("company_mc_summary.csv", rows)
    add_headroom_to_m18(h)
    for r in rows:
        if r["Value"] != "":
            print(f"  {r['Measure']:<84} {r['Value']}  {r['Note'][:60]}")
        else:
            print(f"  {r['Measure'][:84]:<84} p10 {r['P10']!s:>14.14} p50 {r['Median (P50)']!s:>14.14} p90 {r['P90']!s:>14.14}")
    return rows


if __name__ == "__main__":
    main()

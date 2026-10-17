"""Numbers for deck v3 that no cohort table holds yet, computed with the cohort engine (never typed by hand).

Reads the latest cohort Monte Carlo (tables/cohort_mc_draws_v2.csv if it exists, else cohort_mc_draws.csv), the agreed
distributions (tables/dist_agreed_v1.csv via cohort_engine.load_dists) and dist_derived_v1.csv. Writes:
  Round 5 (operator 16 Oct: "We need to show the numbers in cumulative PnL basis"): every measure is CUMULATIVE P&L,
  undiscounted (the engine's cum_cash), never NPV.
  tables/deck_v3_cum_fan.csv      cumulative P&L of one agent by month, p10..p90 over the draws (each draw re-run through
                                  cohort_engine.run): a cross-check of the cohort agent's cohort_mc_cum_fan.csv
  tables/deck_v3_cum_summary.csv  the round-5 headline measures under the same names as cohort_mc_summary.csv (cross-check)
  tables/deck_v3_cum_cells.csv, deck_v3_cum_drivers.csv   r12 x sign-ups cells and input swings on cumulative P&L at 60
  tables/deck_v3_housing.csv      the home-loan EMI caveat at the likely ticket
  tables/deck_v3_must.csv     chance the 5-year NPV is above zero at the bad end of the three must-be-true inputs
  tables/deck_v3_by_year.csv  year 1-5 at the likely values: approval, apply rate, next loan size, top-ups, sign-ups, money lent
  tables/deck_v3_gates.csv    pilot gates: go = the agreed likely value; stop = where the 5-year NPV at the likely values
                              of everything else crosses zero (bisection on the engine)
  tables/deck_v3_hook.csv     what ₹42,000 held earns him a year: janta deposit, liquid fund, our debt fund
Run: ~/.cortado-venv311/bin/python model/deck_v3_numbers.py
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E  # noqa: E402

T = E.T


def latest(name):
    """tables/<name>_v2.csv when the final run wrote one, else tables/<name>.csv."""
    v2 = T / f"{name}_v2.csv"
    return v2 if v2.exists() else T / f"{name}.csv"


def read_draws():
    path = latest("cohort_mc_draws")
    with path.open() as f:
        head = next(csv.reader(f))
    missing = [k for k in E.KEYS if k not in head]
    if missing:
        raise SystemExit(f"{path.name} is older than cohort_engine (no {', '.join(missing[:5])}...): wait for the cohort re-run")
    data = np.genfromtxt(path, delimiter=",", skip_header=1)
    cols = {h: data[:, i] for i, h in enumerate(head)}
    return path, cols


def cum_pnl(cols):
    """Cumulative P&L (undiscounted: the engine's cum_cash) by month for every draw, re-run through the engine."""
    x = {k: cols[k] for k in E.KEYS}
    n = len(x["r12"])
    cum = np.empty((n, E.MONTHS))
    ch = 125 if E.calendar_growth(x) else 2500
    for s in range(0, n, ch):
        part = {k: v[s:s + ch] for k, v in x.items()}
        cum[s:s + ch] = E.run(part)["monthly"]["cum_cash"]
    stored = next((c for c in ("cum_pnl60", "cum_cash60") if c in cols), None)
    if stored is None:
        raise SystemExit("draws file has no cumulative P&L column (cum_pnl60 / cum_cash60): cannot check the re-run")
    assert np.allclose(cum[:, 59], cols[stored], rtol=1e-6, atol=1.0), "re-run does not match the stored draws"
    return cum


def payback(cum):
    """First month cumulative P&L turns positive and stays positive; nan if not by month 60."""
    neg = cum <= 0
    last_neg = np.where(neg.any(axis=1), E.MONTHS - 1 - np.argmax(neg[:, ::-1], axis=1), -1)
    return np.where(last_neg < E.MONTHS - 1, last_neg + 2.0, np.nan)


def fan(cum):
    q = np.percentile(cum, (10, 25, 50, 75, 90), axis=0)
    lik = E.run(E.likely_inputs())["monthly"]["cum_cash"][0]
    return [{"month": t + 1, "p10": q[0, t], "p25": q[1, t], "p50": q[2, t], "p75": q[3, t], "p90": q[4, t], "likely": lik[t],
             "share_above_zero": (cum[:, t] > 0).mean()} for t in range(E.MONTHS)]


def cum_summary(cum):
    pbx = np.where(np.isnan(payback(cum)), 999.0, payback(cum))
    row = lambda name, v: {"measure": name, **{f"p{p}": float(np.percentile(v, p)) for p in (10, 50, 90)}, "mean": float(np.mean(v)), "value": ""}
    val = lambda name, v: {"measure": name, "p10": "", "p50": "", "p90": "", "mean": "", "value": float(v)}
    return [row("Cumulative P&L at 36 months", cum[:, 35]), row("Cumulative P&L at 60 months", cum[:, 59]),
            val("P(cumulative P&L at 36 months > 0)", (cum[:, 35] > 0).mean()), val("P(cumulative P&L at 60 months > 0)", (cum[:, 59] > 0).mean()),
            {**row("Payback month (cumulative P&L turns positive)", pbx), "mean": ""}, row("Peak cash need (lowest cumulative P&L)", cum.min(axis=1)),
            row("Year-1 P&L", cum[:, 11])]


def bands():
    """The r12 and sign-ups bands of the cohort run's own must-be-true table (they move when the inputs move)."""
    rows = [r for r in csv.DictReader(latest("cohort_mc_must_be_true").open()) if r["table"] == "r12 x sign-ups"]
    num = lambda t: [float(v) for v in t.rstrip("%").split("-")]
    rb = [(b, num(b)[0] / 100, num(b)[1] / 100) for b in dict.fromkeys(r["band"] for r in rows)]
    sb = [(b, *num(b)) for b in dict.fromkeys(r["second_band"] for r in rows)]
    return rb, sb


def cells(cols, cum60):
    rows = []
    BANDS_R12, BANDS_SU = bands()
    inb = lambda v, lo, hi, last: (v >= lo) & ((v <= hi) if last else (v < hi))
    for i, (rl, rlo, rhi) in enumerate(BANDS_R12):
        mr = inb(cols["r12"], rlo, rhi, i == len(BANDS_R12) - 1)
        for j, (sl, slo, shi) in enumerate(BANDS_SU):
            m = mr & inb(cols["signups_run"], slo, shi, j == len(BANDS_SU) - 1)
            rows.append({"band": rl, "second_band": sl, "draws": int(m.sum()),
                         "chance_cum_pnl60_above_zero": (cum60[m] > 0).mean() if m.any() else "", "few_draws": "yes" if m.sum() < 50 else ""})
    return rows


def drivers(cols, cum60):
    rows = []
    for k in E.KEYS:
        v = cols[k]
        if np.ptp(v) == 0:
            continue
        lo, hi = np.percentile(v, (10, 90))
        rows.append({"key": k, "input": E.NAMES.get(k, k), "swing_cum_pnl60_top_minus_bottom_decile": cum60[v >= hi].mean() - cum60[v <= lo].mean()})
    rows.sort(key=lambda r: -abs(r["swing_cum_pnl60_top_minus_bottom_decile"]))
    return rows


def must(cols, cum):
    pnl = cum[:, 59]
    t_lo, s_hi = np.percentile(cols["ticket"], 10), np.percentile(cols["support_cost"], 90)
    su_lo = np.percentile(cols["signups_run"], 10)
    rows = [("all", "every draw", "", np.ones_like(pnl, bool)),
            ("signups_run", "sign-ups in the worst 1 in 10 draws", su_lo, cols["signups_run"] <= su_lo),
            ("ticket", "loan size in its worst 1 in 10 draws", t_lo, cols["ticket"] <= t_lo),
            ("support_cost", "running cost in its worst 1 in 10 draws", s_hi, cols["support_cost"] >= s_hi)]
    return [{"key": k, "bad_end": what, "threshold": thr, "draws": int(m.sum()), "chance_cum_pnl60_above_zero": (pnl[m] > 0).mean(),
             "median_cum_pnl60": float(np.median(pnl[m])), "chance_cum_pnl36_above_zero": (cum[m, 35] > 0).mean()} for k, what, thr, m in rows]


HOME_RATE, HOME_YEARS, EMI_RULE = 0.09, 20, 0.5     # round-5 change note: "over 20 years at about 9%", "a 50% EMI-to-income rule"


def housing(dists):
    """The A-page eligibility caveat for a home loan at the likely ticket."""
    t = dists["loan_home_ticket"][2]
    i = HOME_RATE / 12
    emi = t * i / (1 - (1 + i) ** (-12 * HOME_YEARS))
    return [{"ticket": t, "rate": HOME_RATE, "years": HOME_YEARS, "emi": emi, "income_needed": emi / EMI_RULE, "ticket_high": dists["loan_home_ticket"][3],
             "lap_ticket_high": dists["loan_lap_ticket"][3]}]


def by_year(x, d):
    res = E.run(x)
    m, o = res["monthly"], res["out"]
    rows = []
    for y in range(1, 6):
        g = y - 1
        rows.append({"year": y,
                     "approval_first": min(E.APPROVAL_CAP, x["approved_first"] * (1 + x["approval_growth"]) ** g),
                     "apply_a_year": x["apply"] * min(E.TAKEUP_CAP, (1 + x["takeup_growth"]) ** g),
                     "next_loan_after_years_repaid": min(E.TICKET_CAP, x["ticket"] * (1 + x["ticket_growth"]) ** g),
                     "topups": float(o[f"topups_y{y}"][0]),
                     "signups_a_month": float(m["signups"][0, 12 * g:12 * y].mean()),
                     "money_lent": float(o[f"money_lent_y{y}"][0]),
                     "loans": float(o[f"loans_y{y}"][0])})
    return rows


def pnl_at(res, month):
    return res["monthly"]["cum_cash"][:, month - 1]


def solve(x, key, lo, hi, month=60, scale_keys=None, n=4):
    """Value of `key` (or a common multiplier on scale_keys) where the measure crosses zero, others at likely."""
    for _ in range(n):
        vals = np.linspace(lo, hi, 41)
        xx = {k: np.full(41, v, float) for k, v in x.items()}
        if scale_keys:
            for k in scale_keys:
                xx[k] = x[k] * vals
        else:
            xx[key] = vals
        y = pnl_at(E.run(xx), month)
        s = np.sign(y)
        idx = np.where(s[:-1] != s[1:])[0]
        if not len(idx):
            return None, None
        i = idx[0]
        lo, hi = vals[i], vals[i + 1]
    v = (lo + hi) / 2
    xx = dict(x)
    if scale_keys:
        for k in scale_keys:
            xx[k] = x[k] * v
    else:
        xx[key] = v
    return v, {k: float(a[0]) for k, a in E.run(xx)["out"].items()}


def gates(x):
    res0 = E.run(x)
    base = {k: float(a[0]) for k, a in res0["out"].items()}
    base["cum_pnl60"] = float(pnl_at(res0, 60)[0])
    rows = []
    v, _ = solve(x, "signups_run", 10, x["signups_run"])
    rows.append({"gate": 1, "when": "months 1-3", "what": "sign-ups a month", "key": "signups_run", "go": x["signups_run"], "stop": v})
    k, o = solve(x, None, 0.05, 1.0, scale_keys=("apply",))
    rows.append({"gate": 2, "when": "months 1-6", "what": "loans per 100 savers offered, a year", "key": "loans_per_100_offered_year",
                 "go": base["loans_per_100_offered_year"], "stop": o["loans_per_100_offered_year"] if o else None, "apply_multiplier": k})
    v, _ = solve(x, "r12", 0.05, x["r12"])
    v36, _ = solve(x, "r12", x["r12"], min(0.79, x["r3"] - 0.01), month=36)
    rows.append({"gate": 3, "when": "month 12", "what": "still saving at month 12", "key": "r12", "go": x["r12"], "stop": v, "for_3_year_payback": v36})
    v, _ = solve(x, "ticket", 10000, x["ticket"])
    rows.append({"gate": 4, "when": "months 1-12", "what": "loan size lenders give", "key": "ticket", "go": x["ticket"], "stop": v})
    v, _ = solve(x, "support_cost", x["support_cost"], 60)
    rows.append({"gate": 5, "when": "month 12", "what": "running cost per active saver a month", "key": "support_cost", "go": x["support_cost"], "stop": v})
    for r in rows:
        r.setdefault("apply_multiplier", "")
        r.setdefault("for_3_year_payback", "")
        r["cum_pnl60_at_go"] = base["cum_pnl60"]
    return rows


def hook(dists):
    der = {r["key"]: r for r in csv.DictReader((T / "dist_derived_v1.csv").open())}
    agreed = {r["key"]: r for r in csv.DictReader(E.DIST_FILE.open())}
    fr = float(agreed["fund_return"]["likely"])
    bal = float(der["fund_return_on_balance"]["at_likely_values"]) / fr
    jr = float(agreed["janta_rate"]["likely"])
    lq = re.search(r"liquid funds (\d+(?:\.\d+)?)–(\d+(?:\.\d+)?)%", agreed["fund_return"]["evidence_points"])
    llo, lhi = float(lq.group(1)) / 100, float(lq.group(2)) / 100
    gain = float(der["gain_vs_janta"]["at_likely_values"])
    assert abs(gain - bal * (fr - jr)) < 1.0
    return [{"what": "janta deposit (public-sector bank savings rate)", "rate": jr, "rate_high": "", "a_year": bal * jr, "balance": bal},
            {"what": "a liquid fund", "rate": llo, "rate_high": lhi, "a_year": bal * (llo + lhi) / 2, "balance": bal},
            {"what": "our debt fund", "rate": fr, "rate_high": "", "a_year": bal * fr, "balance": bal},
            {"what": "gain against a janta deposit", "rate": fr - jr, "rate_high": "", "a_year": gain, "balance": bal}]


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    E.write("deck_v3_hook.csv", hook(dists))
    E.write("deck_v3_housing.csv", housing(dists))
    E.write("deck_v3_by_year.csv", by_year(x, dists))
    E.write("deck_v3_gates.csv", gates(x))
    path, cols = read_draws()
    cum = cum_pnl(cols)
    E.write("deck_v3_must.csv", must(cols, cum))
    E.write("deck_v3_cum_fan.csv", fan(cum))
    E.write("deck_v3_cum_summary.csv", cum_summary(cum))
    E.write("deck_v3_cum_cells.csv", cells(cols, cum[:, 59]))
    E.write("deck_v3_cum_drivers.csv", drivers(cols, cum[:, 59]))
    old = T / "deck_v3_fan.csv"
    if old.exists():
        old.unlink()                     # round 4's NPV fan, replaced by deck_v3_cum_fan.csv
    print(f"read {path.name}; wrote deck_v3_hook, _housing, _by_year, _gates, _must, _cum_fan, _cum_summary, _cum_cells, _cum_drivers")


if __name__ == "__main__":
    main()

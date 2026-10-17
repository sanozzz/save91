"""On-book share 15% / 30% / 50%, with the fleet sized to the city pool (operator tap "Test 15/30/50%").

The lead's diagnosis of base_plan.py: its 7,500-agent fleet outgrows the city pool (savers peak at about 40 lakh in year 5, then
fall) and adds cost with no savers. So, per on-book share (top-quality selection; flat from m30, as the base):
  share      15%, 30%, 50% of personal-loan volume (first, repeat and top-ups) on our book from m30;
  loss       on-book lifetime loss = 0.5x / 0.6x / 0.75x the agreed `loss` (JUDGEMENT: the larger the share, the further down the
             credit-score ranking it reaches);
  fleet      300 agents by m18 (the earlier ramp scaled to 300), then h a month, h in {100, 150, 200}, to a cap in {2,000, 3,000,
             4,000, 5,000}; the city-opening threshold 10,000 or 25,000 headroom a head (searched; not part of the locked
             setting); the locked real-world city setting (soft curve, 3% refill, at most 4 new cities a month, 20% cap);
  objective  the HIGHEST value at m60 of the lower of lens 1 (20 x ARR) and lens 2 (0.45 x AUM), among paths with EBITDA positive
             for good by m60 and cash >= 0 through m96; if none, by m72 (said so); then by m96; then any.
Everything else as base_plan.py (nbfc.py economics, unicorn_plan's rounds, 96 months). The chosen path per share is written as a
full base set: tables/base15_*, base30_*, base50_* (base_plan's formats), with a 1,000-draw MC; tables/share_compare.csv.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import nbfc as NB                  # noqa: E402
import realworld as RWm            # noqa: E402
import saturation as S             # noqa: E402
import base_plan as B              # noqa: E402
import unicorn_plan as U           # noqa: E402

CR = C.CRORE
SHARES = ((0.15, 0.50), (0.30, 0.60), (0.50, 0.75))     # (on-book share, loss multiple: judgement)
A18, HIRES, CAPS, XS = 300, (100, 150, 200), (2000, 3000, 4000, 5000), (10000.0, 25000.0)
DEADLINES = (60, 72, 96)


def cfg_for(share, lm):
    return {"share_start": share, "share_full": share, "share_start_month": 30, "share_full_month": 30, "loss_mult": lm}


PATHS = [(A18, h, cap, X) for h in HIRES for cap in CAPS for X in XS]


def setup():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, sh = S.city_curve()
    addr = sh[:S.CLASS_I] * S.POOL
    C.set_horizon(B.HORIZON)
    sims = {p: S.run(x, dists, RWm.rw_cfg(addr, p[3]), target_fn=U.path_fn(p[0], p[1], p[2]))[0] for p in PATHS}
    return dists, x, addr, sims                          # the fleet and cities do not depend on the share: simulated once


def main():
    dists, x, addr, sims = setup()
    rows = [run_share(dists, x, addr, sims, share, lm, f"base{int(round(share * 100))}") for share, lm in SHARES]
    C.write("share_compare.csv", rows)
    C.set_horizon(60)
    return rows


def run_share(dists, x, addr, sims, share, lm, tag):
    """One on-book share: the search on PATHS, the chosen path's full base set written as {tag}_*, and its comparison row."""
    paths = PATHS
    cfg = cfg_for(share, lm)
    res = []
    for p in paths:
        of, seed, rounds, rds, ct, sat, _fl = B.evaluate(x, dists, addr, p, cfg=cfg, o=sims[p])
        L = NB.lenses(of, 60)
        be = C.stays_positive_from(of["ebitda"])[0]
        res.append({"path": p, "of": of, "seed": seed, "rounds": rounds, "rds": rds, "ct": ct, "sat": sat,
                    "lower": min(L["Lens 1 (20 x ARR)"], L["Lens 2 (0.45 x AUM)"]), "be": be, "cash_ok": of["cash"][0].min() >= 0})
    pick, rule = None, ""
    for dl in DEADLINES:
        ok = [r for r in res if r["cash_ok"] and not np.isnan(r["be"]) and r["be"] <= dl]
        if ok:
            pick = max(ok, key=lambda r: r["lower"])
            rule = (f"EBITDA positive for good by m{dl}" + ("" if dl == 60 else f" (relaxed: no path has it by m{DEADLINES[DEADLINES.index(dl) - 1]})")
                    + f"; {len(ok)} of {len(res)} paths qualify")
            break
    if pick is None:
        pick = max(res, key=lambda r: r["lower"])
        rule = "no path turns EBITDA positive for good by m96; the highest lower lens regardless"
    of, ct, p, sat, rds, seed = pick["of"], pick["ct"], pick["path"], pick["sat"], pick["rds"], pick["seed"]
    L = NB.lenses(of, 60)
    C.write(f"{tag}_monthly.csv", B.monthly(of))
    C.write(f"{tag}_yearly.csv", B.yearly(of))
    C.write(f"{tag}_headcount.csv", C.headcount_rows(of))
    C.write(f"{tag}_rounds.csv", RWm.rounds_rows(f"{share:.0%} on our book", ct))
    C.write(f"{tag}_city_plan.csv", S.plan_from_auto(of, sat, f"{share:.0%} on-book plan: AUTO rollout under the real-world setting; edit freely"))
    fc = B.first_clear(of)
    lens_rows = []
    for m in sorted({48, 54, 60, 72, 84, 96} | ({fc} if fc else set())):
        Lm = NB.lenses(of, m)
        lens_rows.append({"Month": m, "Note": "the unicorn-on-paper check" if m == 60 else ("first month lenses 1 and 2 both clear" if m == fc else ""),
                          **{k: Lm[k] for k in ("ARR", "Fee ARR", "AUM", "NBFC equity", "Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)",
                                                 "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
                          **{f"{k} margin over $1B": Lm[k] / U.UNICORN - 1 for k in ("Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)", "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
                          "Lenses 1 and 2 both clear $1B": "yes" if B.clears(of, m) else "no", "Fleet path": B.path_text(p), "Path choice": rule,
                          "Basis": "our judgement (multiples)"})
    C.write(f"{tag}_lenses.csv", lens_rows)
    ck = B.checks(of, ct, sat, x, cfg)
    C.write(f"{tag}_checks.csv", ck)
    mc_rows = B.mc(dists, addr, p, seed["Amount"], rds, cfg)
    C.write(f"{tag}_mc_summary.csv", mc_rows)
    mcv = {r["Measure"]: r["Value"] for r in mc_rows}
    yr = lambda k: float(of[k][0, 48:60].sum())
    row = ({"On-book share": share, "On-book loss, multiple of the agreed loss (judgement)": lm,
                 "On-book loss (likely)": lm * float(np.mean(x["loss"])), "Fleet path": B.path_text(p), "Agent cap": p[2],
                 "Path choice": rule, "Total raised (Rs)": sum(r["Amount"] for r in ct),
                 "Rounds": "; ".join(f"{r['Round']} m{r['Month']} Rs {r['Amount'] / CR:,.0f} crore (pre {r['Pre'] / CR:,.0f})" for r in ct),
                 "Founders % after the last round": ct[-1]["Founders %"],
                 "Active savers at m60": float(of["still_saving"][0, 59]), "Peak active savers": float(of["still_saving"][0].max()),
                 "Month of the peak": int(of["still_saving"][0].argmax() + 1), "AUM at m60 (Rs)": L["AUM"],
                 "Loan book at m60 (Rs)": float(of["nbfc_book"][0, 59]), "NBFC equity at m60 (Rs)": float(of["nbfc_equity"][0, 59]),
                 "NBFC borrowings at m60 (Rs)": float(of["nbfc_borrowings"][0, 59]),
                 "Lens 1 at m60 (Rs)": L["Lens 1 (20 x ARR)"], "Lens 2 at m60 (Rs)": L["Lens 2 (0.45 x AUM)"],
                 "Lens 3 at m60 (Rs)": L["Lens 3 (3 x NBFC equity + 20 x fee ARR)"],
                 "Unicorn on paper at m60 (lenses 1 and 2)": "yes" if B.clears(of, 60) else "no",
                 "First month lenses 1 and 2 both clear": fc or "not to m96",
                 "EBITDA break-even month (stays positive)": "not within m96" if np.isnan(pick["be"]) else float(pick["be"]),
                 "Year-5 revenue (Rs)": yr("revenue"), "Year-5 EBITDA (Rs)": yr("ebitda"), "Year-5 PAT (Rs)": yr("pat"),
                 "Year-5 credit cost (Rs)": yr("nbfc_credit_cost"), "Lowest cash (Rs)": float(of["cash"][0].min()),
                 "MC: P(lenses 1 and 2 both >= $1B at m60)": mcv["P(lenses 1 and 2 both >= $1B at m60)"],
                 "MC: P(EBITDA positive for good by m60)": mcv["P(EBITDA positive for good by m60)"],
                 "MC: P(cash >= 0 through m96)": mcv["P(cash >= 0 through m96)"],
                 "Checks passed": f"{sum(c['Passes'] for c in ck)}/{len(ck)}"})
    print(f"  {share:.0%} -> {tag}_*: {B.path_text(p)} | {rule} | lower lens {pick['lower'] / U.UNICORN - 1:+.1%} | checks {row['Checks passed']}", flush=True)
    return row


if __name__ == "__main__":
    main()

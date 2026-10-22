"""The base's path search, written out (companion to base_plan.py): every path on base_plan.GRID under the base settings (15% of
personal-loan volume on our book from m30 at half the agreed loss; the locked real-world city setting; unicorn_plan's rounds),
with lenses 1, 2 and 3 at m60, the first month lenses 1 and 2 both clear $1B (to m96), the equity raised and the lowest cash.

Writes tables/base15_grid_search.csv (the superseded 15% base's search; the authoritative base is 30% on book).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import company_model as C          # noqa: E402
import nbfc as NB                  # noqa: E402
import saturation as S             # noqa: E402
import base_plan as B              # noqa: E402
import unicorn_plan as U           # noqa: E402


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, share = S.city_curve()
    addr = share[:S.CLASS_I] * S.POOL
    C.set_horizon(B.HORIZON)
    rows = []
    paths = [B.NB2_PATH] + [(a, h, c, X) for a in B.GRID[0] for h in B.GRID[1] for c in B.GRID[2] for X in B.GRID[3]]
    seen = set()
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        of, seed, rounds, rds, ct, sat, fl = B.evaluate(x, dists, addr, p)
        L = NB.lenses(of, 60)
        fc = B.first_clear(of)
        l1 = 240 * of["revenue"][0]
        l2 = 0.45 * of["fund_end"][0]
        rows.append({"Path": B.path_text(p), "NB2's path": "yes" if p == B.NB2_PATH else "",
                     "Lens 1 at m60 (Rs)": L["Lens 1 (20 x ARR)"], "Lens 2 at m60 (Rs)": L["Lens 2 (0.45 x AUM)"],
                     "Lens 3 at m60 (Rs)": L["Lens 3 (3 x NBFC equity + 20 x fee ARR)"],
                     "Lens 1 margin at m60": L["Lens 1 (20 x ARR)"] / U.UNICORN - 1, "Lens 2 margin at m60": L["Lens 2 (0.45 x AUM)"] / U.UNICORN - 1,
                     "Highest lens 1 to m96 (Rs)": float(l1.max()), "Month of the highest lens 1": int(l1.argmax() + 1),
                     "Highest lens 2 to m96 (Rs)": float(l2.max()),
                     "First month lenses 1 and 2 both clear $1B": fc or "not to m96",
                     "Equity raised by m60 (Rs)": seed["Amount"] + sum(r["Amount"] for r in rounds if r["Month"] <= 60),
                     "Equity raised by m96 (Rs)": seed["Amount"] + sum(r["Amount"] for r in rounds),
                     "Lowest cash (Rs)": float(of["cash"][0].min()), "ARR at m60 (Rs)": L["ARR"], "AUM at m60 (Rs)": L["AUM"],
                     "Loan book at m60 (Rs)": float(of["nbfc_book"][0, 59])})
        print(f"  {B.path_text(p)[:70]:<70} L1 {rows[-1]['Lens 1 margin at m60']:+.1%} L2 {rows[-1]['Lens 2 margin at m60']:+.1%} first {rows[-1]['First month lenses 1 and 2 both clear $1B']}", flush=True)
    C.write("base15_grid_search.csv", rows)
    C.set_horizon(60)
    return rows


if __name__ == "__main__":
    main()

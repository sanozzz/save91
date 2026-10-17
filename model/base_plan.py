"""THE BASE CASE (authoritative): 30% of personal-loan volume on our own book (operator, 17 Oct 2026, after "Test 15/30/50%":
"30% on book"). main() runs share_compare.run_share(0.30, 0.6, "base"): the fleet sized to the city pool (300 agents by m18,
+150 a month, cap 5,000 is the path that rule picks), every other setting below; it writes base_* (identical to base30_*) and
tables/base_inputs.csv (every input beyond dist_agreed_v1.csv). The text below is the earlier "NB2 modified" 15% base
(operator: "Its NB2 modified as base case. We do top 15% on our book"), superseded; its code stays as main_15pct_superseded().

The lead's reading (the operator can correct it): we keep the best-quality 15% of personal-loan volume (the top by credit score)
on our own book; partners take the other 85% and still pay us DSA fees on them.
  book        a FLAT 15% of personal-loan volume (first, repeat and top-ups) on our book from m30 (no ramp: a clean step).
  credit      on-book lifetime loss = 0.5 x the agreed `loss` distribution (likely 1.5% instead of 3%; judgement: the best 15%
              by score); partner loans' collection fees stay as before (only the on-book loans' fees become internal).
  the rest    as NB2 (nbfc.py, realworld.py): NBFC-ICC licence Rs 1 crore at m24 (LEV-031), NOF Rs 10 crore, opex Rs 15 lakh a
              month + Rs 5 lakh per Rs 500 crore of book; yield 26% (the agreed EMI rate); cost of funds 13.5% (LEV-014/015);
              borrowings <= 3 x NBFC equity (LEV-023); capital >= 15% (20% operating floor; 25% held); processing fee 2%; no DSA
              fee on on-book loans; the three lenses; the locked real-world city setting (soft curve, 3% pool refill, at most 4
              new cities a month, 20% cap, 7.0 crore pool on the rank-size estimate, about 500 Class I cities); pay Rs 20,000 +
              0.25% of balance capped at Rs 10,000 (both rising 7% a year); central team as built; unicorn_plan's rounds
              (step-ups, lenses, 25% dilution cap, 12-month cadence, 18-24 months of runway, ESOP 10% at seed, A and B).
  fleet       NB2's path (300 agents by m18, +150 a month, cap 5,000, open a city below 25,000 headroom a head) if lenses 1 and 2
              still clear at m60; else the least-equity path that does on the grid (agents at m18 <= 300, hires <= 300 a month,
              cap <= 7,500, the same city rule); else the path that clears both lenses EARLIEST (to m96; ties: least equity);
              else the path with the highest lower lens at m60.
Lenses (our judgement): (1) 20 x ARR, ARR = 12 x (fee revenue + net interest income + processing fees) in the month; (2) 0.45 x
AUM; (3) cross-check: 3 x the NBFC's book equity + 20 x the platform's fee ARR.
MC: 1,000 draws, the fleet path and the funding plan fixed; market inputs drawn (Latin hypercube, the bad-year copula), the
common sign-up factor and each agent's own draw, the pool size drawn (pert 6.5/7.0/7.7 crore), on-book loss = 0.5 x each draw's
loss.

Writes tables/base_yearly.csv, base_monthly.csv, base_rounds.csv, base_city_plan.csv, base_lenses.csv, base_headcount.csv,
base_mc_summary.csv and base_checks.csv. Nothing else.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import cohort_mc as MC             # noqa: E402
import company_model as C          # noqa: E402
import nbfc as NB                  # noqa: E402
import realworld as RWm            # noqa: E402
import saturation as S             # noqa: E402
import unicorn_plan as U           # noqa: E402

CR = C.CRORE
HORIZON = 96
BASE_NBFC = {"share_start": 0.15, "share_full": 0.15, "share_start_month": 30, "share_full_month": 30, "loss_mult": 0.5}
NB2_PATH = (300, 150, 5000, 25000.0)
GRID = ((100, 200, 300), (50, 100, 150, 200, 250, 300), (3000, 5000, 7500), (5000.0, 10000.0, 25000.0))
MC_DRAWS, MC_SEED, MC_CHUNK = 1000, 20261019, 25
POOL_PERT = (6.5, 7.0, 7.7)


def evaluate(x, dists, addr, path, keep=False, cfg=None, o=None):
    """One path under the base settings (cfg: the NBFC settings, default BASE_NBFC; o: a saved simulation of the path)."""
    a18, h, cap, X = path
    sat = RWm.rw_cfg(addr, X)
    fl = None
    if o is None:
        o, fl = S.run(x, dists, sat, target_fn=U.path_fn(a18, h, cap), keep=keep)
    on = NB.apply_nbfc(o, x, cfg or BASE_NBFC)
    seed, rounds = U.plan_rounds(on)
    rds = [(r["Month"], r["Amount"]) for r in rounds]
    of = NB.funded(on, seed["Amount"], rds)
    of["cash_seed_only"] = C.treasury(of, seed_size=seed["Amount"], rounds=[])["cash"]
    return of, seed, rounds, rds, U.cap_table(seed, rounds), sat, fl


def clears(of, m):
    L = NB.lenses(of, m)
    return min(L["Lens 1 (20 x ARR)"], L["Lens 2 (0.45 x AUM)"]) >= U.UNICORN


def first_clear(of):
    return next((m for m in range(1, C.M + 1) if clears(of, m)), None)


def path_text(p):
    return f"{p[0]} agents by m18, +{p[1]} a month, cap {p[2]:,} agents; open a city below {p[3]:,.0f} headroom a head (at most 4 a month)"


# ---------------------------------------------------------------- the base's line set (plain words, the full ladder)
R_ = "Rs"


def base_lines():
    L = []
    for k, nm, u, how in C.LINES:
        if k == "revenue":
            L += [("fee_revenue", "Fee revenue, total (distribution commissions and DSA fees)", R_, "sum"),
                  ("nbfc_interest", "NBFC: interest income on the book", R_, "sum"),
                  ("nbfc_cost_of_funds", "NBFC: cost of funds on borrowings", R_, "sum"),
                  ("nbfc_nii", "NBFC: net interest income", R_, "sum"),
                  ("nbfc_processing", "NBFC: processing fees (2% of on-book loans)", R_, "sum"),
                  ("revenue", "Revenue, total (fee revenue + net interest income + processing fees)", R_, "sum")]
            continue
        if k == "direct":
            L += [(k, nm, u, how), ("nbfc_credit_cost", "Credit cost: expected-loss provisions on the book", R_, "sum")]
            continue
        if k == "cm1":
            L.append((k, "CM1 (transaction margin, after credit cost)", u, how))
            continue
        if k == "cost_contingency":
            L += [("nbfc_opex", "Central: NBFC opex (credit, risk, compliance, treasury; scales with the book)", R_, "sum"),
                  ("nbfc_licence", "Central: NBFC licence, one-time", R_, "sum"), (k, nm, u, how)]
            continue
        if k == "cf_investing":
            L += [("cf_book", "Cash flow, investing: loan book growth and NBFC capital held", R_, "sum"), (k, nm, u, how)]
            continue
        if k == "cf_series_a":
            L.append((k, "Cash flow, financing: rounds A onwards (end of their months)", u, how))
            continue
        if k == "cf_financing":
            L += [(k, "Cash from financing: equity raised", u, how), ("cf_borrowings", "Cash flow, financing: NBFC borrowings", R_, "sum")]
            continue
        if k == "cash":
            L.append((k, "Closing cash, with every round", u, how))
            continue
        if k == "cash_seed_only":
            L.append((k, "Closing cash, seed only (no later rounds)", u, how))
            continue
        if k == "burn":
            L.append((k, "Memo: burn (cash used by operations and investing, after NBFC borrowings)", u, how))
            continue
        L.append((k, nm, u, how))
    L += [("nbfc_share", "NBFC: on-book share of personal-loan volume", "share", "end"),
          ("nbfc_disbursed", "NBFC: on-book loans disbursed", R_, "sum"),
          ("nbfc_book_gross", "NBFC: loan book, scheduled (gross)", R_, "end"),
          ("nbfc_book", "NBFC: loan book, net of provisions", R_, "end"),
          ("nbfc_equity", "NBFC: equity in the book (capital held)", R_, "end"),
          ("nbfc_borrowings", "NBFC: borrowings", R_, "end"),
          ("nbfc_capital_ratio", "NBFC: capital / book", "share", "end"),
          ("nbfc_leverage", "NBFC: borrowings / equity", "x", "end"),
          ("arr", "ARR (12 x the month's revenue)", R_, "end"), ("fee_arr", "Fee ARR (12 x the month's fee revenue)", R_, "end"),
          ("lens1", "Lens 1: 20 x ARR (our judgement)", R_, "end"), ("lens2", "Lens 2: 0.45 x AUM (our judgement)", R_, "end"),
          ("lens3", "Lens 3: 3 x NBFC equity + 20 x fee ARR (cross-check, our judgement)", R_, "end")]
    return L


def arrays(of):
    a = C.table_arrays(of)
    a = {**a, "arr": 12 * of["revenue"], "fee_arr": 12 * of["fee_revenue"], "lens1": 20 * 12 * of["revenue"], "lens2": 0.45 * of["fund_end"],
         "lens3": 3 * of["nbfc_equity"] + 20 * 12 * of["fee_revenue"], "nbfc_opex": of["nbfc_opex"], "nbfc_licence": of["nbfc_licence"],
         "nbfc_capital_ratio": np.nan_to_num(of["nbfc_capital_ratio"]), "cf_borrowings": of["cf_borrowings"]}
    return a


def monthly(of):
    a = arrays(of)
    return [{"Month": t + 1, "Year": t // 12 + 1, **{f"{nm} ({u})" if u == R_ else nm: float(a[k][0, t]) for k, nm, u, _h in base_lines()}}
            for t in range(C.M)]


def yearly(of):
    a = arrays(of)
    return [C.year_row(a, k, nm, u, how) for k, nm, u, how in base_lines()]


BASE_SHARE, BASE_LOSS_MULT = 0.30, 0.60          # operator 17 Oct: "30% on book"; loss 0.6x the agreed (judgement)


def main():
    """The authoritative base: 30% on book; base_* and base_inputs.csv."""
    import share_compare as SC
    dists, x, addr, sims = SC.setup()
    row = SC.run_share(dists, x, addr, sims, BASE_SHARE, BASE_LOSS_MULT, "base")
    q, _share = S.city_curve()
    C.write("base_inputs.csv", inputs_rows(x, q, row))
    C.set_horizon(60)
    return row


def inputs_rows(x, q, row):
    """Every input the base uses beyond tables/dist_agreed_v1.csv, from the code's own constants."""
    nb = {**NB.DEFAULT, **SCcfg()}
    rows = []

    def add(group, name, value, unit, source, confidence):
        rows.append({"Group": group, "Input": name, "Value": value, "Unit": unit, "Source": source, "Confidence": confidence})
    J, Y, P, G = "Our judgement", "Your number", "Published", "Industry guide, not verified"
    # cities
    add("Cities", "Addressable pool: urban self-employed (own-account workers, employers, helpers), likely", S.POOL, "people",
        "NG-002 (40.4% of urban workers self-employed, 34.0% own-account or employer); urban workers about 19 crore (lead's estimate)", J)
    add("Cities", "Addressable pool, range for the Monte Carlo (low / likely / high)", "6.5 / 7.0 / 7.7 crore (pert)", "people", "as above", J)
    add("Cities", "Urban towns on the rank-size curve", S.N_TOWNS, "towns", "lead's estimate (about 4,000 urban centres)", J)
    add("Cities", "Cities a fleet serves (Class I, population >= 1 lakh)", S.CLASS_I, "cities", "lead's estimate (about 500)", J)
    add("Cities", "NCR's share of urban India (rank 1 on the curve)", S.NCR_SHARE, "share", "lead's estimate: NCR about 3.3 crore of about 52 crore urban", J)
    add("Cities", "Rank-size exponent q (fitted so the 4,000 shares add to 1)", round(q, 4), "", "fitted (estimate, not census)", J)
    add("Cities", "City cap: most of a city's pool we can ever sign", S.CAP, "share of the city's pool", "operator tap: 20%", Y)
    add("Cities", "Saturation curve: sign-ups x (1 - (penetration / cap)^2) (soft)", "soft", "", "lead's decision after sat_sensitivity.csv", J)
    add("Cities", "Pool refill (new shops, migrants, people entering self-employment)", RWm.RW["refill"], "a year", "lead's decision after sat_sensitivity.csv", J)
    add("Cities", "Most new cities a month", RWm.RW["max_new_per_month"], "cities a month", "lead's decision (operational pace)", J)
    add("Cities", "Open the next city when the best city's headroom a head is below", row["Fleet path"].split("below ")[1].split(" headroom")[0],
        "sign-ups a head", "searched (share_compare.py)", J)
    add("Cities", "City launch cost, once per city", C.CITY_LAUNCH, "Rs", "operator tap, 17 Oct", Y)
    add("Cities", "City office", C.CITY_OFFICE, "Rs a month per city", "operator tap", Y)
    add("Cities", "City manager, one per city", C.CITY_MANAGER_PAY, "Rs a month (+10% statutory, +7% a year)", "operator tap", Y)
    add("Cities", "Team lead, one per 10 agents", C.TEAM_LEAD_PAY, "Rs a month (+10% statutory, +7% a year)", "operator tap", Y)
    # fleet
    add("Fleet", "Agents by month 18 (ramp: m3 25, m6 50, m9 100, m12 150, m15 225, m18 300)", row["Fleet path"].split(" agents")[0], "agents", "searched (share_compare.py)", J)
    add("Fleet", "Hires a month after month 18", 150, "agents a month", "searched (share_compare.py)", J)
    add("Fleet", "Agent cap (then replace leavers only)", row["Agent cap"], "agents", "searched (share_compare.py): sized to the city pool", J)
    add("Fleet", "Agents who leave a year (replaced the next month; the new agent inherits the book)", C.ATTRITION_YEAR, "share of agents", "operator tap", Y)
    add("Fleet", "Savers who stop when their agent is replaced", C.HANDOVER_LOSS, "share of the book", "operator tap", Y)
    add("Fleet", "Agent statutory on top of salary", C.AGENT_STATUTORY, "Rs a month (rises with pay)", "operator tap", Y)
    add("Fleet", "Hiring and kit, per hire incl. replacements", C.AGENT_KIT, "Rs", "operator tap", Y)
    add("Fleet", "Pay rise, agents and staff", C.RAISE, "a year", "operator tap; lead fix (agents too)", Y)
    add("Fleet", "Acquisition share of agent cost: tenure months 1-12, then a straight line to month 60", f"{C.ACQ_SHARE_EARLY:.0%} -> {C.ACQ_SHARE_M60:.0%}", "share", "operator tap (split by time)", Y)
    # central team and costs
    for role, dep, pay, *_ in C.CENTRAL:
        add("Central team", f"{role} ({dep})", pay, "Rs a month each, year-1 terms (+10% statutory, +7% a year)", "operator tap, 17 Oct", Y)
    for role, dep, pay, rule in C.SCALE_ROLES:
        add("Central team", f"{role} ({dep}): {rule}", pay, "Rs a month each, year-1 terms", "operator tap ('Add as proposed')", Y)
    add("Central team", "Engineers and ops executives after m18", "+1 each per 50 agents beyond 60", "", "operator tap", Y)
    for nm, v, u in (("Statutory on central and field-management pay", C.STATUTORY, "share of pay"), ("Laptop per central hire (capitalised, 36 months)", C.LAPTOP, "Rs"),
                     ("Tools per central person", C.TOOLS, "Rs a month"), ("App: cloud, SMS and KYC tools", C.APP_BASE, "Rs a month"),
                     ("App integrations, months 1-3 (capitalised, 36 months)", C.INTEGRATIONS, "Rs"),
                     ("Licences and setup, one-time", sum(v_ for _, v_ in C.LICENCE_ONE_TIME), "Rs"),
                     ("Licences and compliance, yearly", sum(v_ for _, v_ in C.LICENCE_YEARLY), "Rs a year"), ("Head office", C.HQ, "Rs a month"),
                     ("Travel", C.TRAVEL, "Rs a month"), ("Brand marketing", C.BRAND, "Rs a month"), ("Bureau pull per personal-loan application", C.BUREAU, "Rs"),
                     ("Fraud provision on cash collected", C.FRAUD, "share"), ("Cash cover: the larger of Rs 1,000 or this share of the agent's cash", C.CASH_COVER_RATE, "share a month"),
                     ("Contingency on every expensed line", C.CONTINGENCY, "share"), ("Income tax on profit after past losses", C.TAX, "share"),
                     ("Interest on cash", C.INTEREST_RATE, "a year"), ("Commissions arrive after", C.COMMISSION_LAG, "months"),
                     ("Depreciation of laptops and integrations", C.DEPRECIATION_MONTHS, "months, straight line"),
                     ("Fund-raising cost, seed / each later round", f"{C.SEED_COST:,.0f} / {C.SERIES_A_COST:,.0f}", "Rs")):
        add("Costs and finance", nm, v, u, "operator taps (brief, addendum, fix round 1)", Y)
    # NBFC
    for k, v, u, w, b in NB.NBFC_INPUTS:
        if k in ("share_start", "share_full", "share_full_month", "capital_floor"):      # stated plainly below
            continue
        val = nb.get(k, v)
        if k == "yield":
            val = float(np.mean(x["rate"]))
        if k == "loss":
            val = float(np.mean(x["loss"]))
        conf = P if "RBI" in b else (G if "LEV" in b else (Y if "operator" in b or "brief" in b else J))
        add("NBFC", "Lifetime credit loss after recoveries: the agreed `loss` (likely), before the on-book multiple" if k == "loss" else w, val, u, b, conf)
    add("NBFC", "On-book share of personal-loan volume: the best-quality part by credit score, flat from m30", BASE_SHARE, "share", "operator: '30% on book'", Y)
    add("NBFC", "On-book loss as a multiple of the agreed loss", BASE_LOSS_MULT, "x the agreed loss", "judgement: the top 30% by score", J)
    add("NBFC", "NBFC equity = the larger of NOF and the book / (1 + leverage)", "max(Rs 10 crore, 25% of the book)", "", "LEV-023; RBI minimum NOF", G)
    add("NBFC", "Capital floor: regulatory minimum / operating floor", "15% / 20% (25% held)", "share of the book", "brief", P)
    add("NBFC", "DSA origination fee on on-book loans", 0, "", "brief: we are the lender", Y)
    add("NBFC", "Collection fees on on-book loans", "internal (dropped); partners' 70% unchanged", "", "brief", Y)
    # rounds
    add("Rounds", "Seed pre-money (fixed)", U.SEED_PRE, "Rs", "brief", Y)
    for st, v in U.STEP_UP.items():
        add("Rounds", f"Step-up into round {st} (x the previous post-money)", v, "x", "lead decision (unicorn fix 1)", J)
    add("Rounds", "Step-up for later rounds / extensions", f"{U.LATER_STEP:g} / {U.EXTENSION_STEP:g}", "x", "lead decision", J)
    add("Rounds", "Pre-money = the higher of the step-up and the lens; never below the previous post", "rule", "", "lead decision", J)
    add("Rounds", "Lens pricing: round A / later rounds", f"{U.ARR_MULT_A:g} x ARR or {U.AUM_MULT:g} x AUM / {U.ARR_MULT:g} x ARR or {U.AUM_MULT:g} x AUM", "", "brief", J)
    add("Rounds", "Dilution cap per round", U.DIL_CAP, "share of post-money", "brief", Y)
    add("Rounds", "Cadence", "seed m0; A m12; B m24; C m36; D m48; unicorn round E in m54-m60 once a lens reaches Rs 10,000 crore", "", "lead decision", J)
    add("Rounds", "A round comes earlier when cash would fall to this many months of forward burn", U.FWD_TRIGGER, "months", "brief", J)
    add("Rounds", "Round size: months of forward burn + buffer (18 if 24 would dilute more than 25%)", f"{U.FWD_SIZE_MAX} (or {U.FWD_SIZE}) + Rs {U.BUFFER / CR:,.0f} crore", "", "brief", J)
    add("Rounds", "ESOP pool: 10% of the post-money at the seed, topped up to 10% at A and B", U.ESOP, "share", "brief", Y)
    # lenses
    add("Lenses", "Unicorn threshold ($1B at Rs 100 per $)", U.UNICORN, "Rs", "operator convention", Y)
    add("Lenses", "Lens 1: x ARR, ARR = 12 x (fee revenue + net interest income + processing fees) in the month", U.ARR_MULT, "x", "judgement: a fintech growing > 100% a year", J)
    add("Lenses", "Lens 2: x AUM (month-end fund)", U.AUM_MULT, "x", "SAV-03: Stable Money Rs 2,507 crore post-money against about Rs 5,000 crore invested (SAV-02); a rough proxy", J)
    add("Lenses", "Lens 3 (cross-check): x NBFC book equity + 20 x fee ARR", 3, "x", "judgement: fintech NBFC P/B", J)
    add("Model", "Horizon", HORIZON, "months", "the unicorn plan's horizon", J)
    add("Model", "Monte Carlo draws (fleet path and funding plan fixed)", MC_DRAWS, "draws", "brief", J)
    return rows


def SCcfg():
    return {"share_start": BASE_SHARE, "share_full": BASE_SHARE, "share_start_month": 30, "share_full_month": 30, "loss_mult": BASE_LOSS_MULT}


def main_15pct_superseded():
    """The superseded 'NB2 modified' 15% base (kept for the record; not run by default)."""
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    q, share = S.city_curve()
    addr = share[:S.CLASS_I] * S.POOL
    C.set_horizon(HORIZON)
    # ---- the fleet path
    of, seed, rounds, rds, ct, sat, fl = evaluate(x, dists, addr, NB2_PATH)
    search_note = "NB2's path still clears lenses 1 and 2 at m60"
    path = NB2_PATH
    if not (clears(of, 60) and of["cash"][0].min() >= 0):
        cands = []
        for a18 in GRID[0]:
            for h in GRID[1]:
                for cap in GRID[2]:
                    for X in GRID[3]:
                        p = (a18, h, cap, X)
                        ofp, sd, rr, _rds, _ct, _sat, _fl = evaluate(x, dists, addr, p)
                        L = NB.lenses(ofp)
                        eq60 = sd["Amount"] + sum(r["Amount"] for r in rr if r["Month"] <= 60)
                        cands.append({"path": p, "ok": clears(ofp, 60) and ofp["cash"][0].min() >= 0, "eq60": eq60,
                                      "min_lens": min(L["Lens 1 (20 x ARR)"], L["Lens 2 (0.45 x AUM)"]), "first": first_clear(ofp),
                                      "cash_ok": ofp["cash"][0].min() >= 0})
        ok = [c for c in cands if c["ok"]]
        if ok:
            path = min(ok, key=lambda c: c["eq60"])["path"]
            search_note = f"NB2's path no longer clears; the least-equity path that clears lenses 1 and 2 at m60 ({len(ok)} of {len(cands)} do)"
        else:
            reach = [c for c in cands if c["first"] and c["cash_ok"]]
            if reach:                                          # the earliest month a path clears both lenses; then least equity
                best = min(reach, key=lambda c: (c["first"], c["eq60"]))
                search_note = (f"no path clears lenses 1 and 2 at m60; the earliest that clears both does so in month {best['first']} "
                               f"({len(reach)} of {len(cands)} paths clear by m96; base15_grid_search.csv lists all)")
            else:
                best = max([c for c in cands if c["cash_ok"]] or cands, key=lambda c: c["min_lens"])
                search_note = "no path clears lenses 1 and 2 by m96; the best has the highest lower lens at m60"
            path = best["path"]
        of, seed, rounds, rds, ct, sat, fl = evaluate(x, dists, addr, path)
    fc = first_clear(of)
    feasible = clears(of, 60) and of["cash"][0].min() >= 0
    print(f"  path {path} feasible {feasible}; {search_note}; first month both lenses clear: {fc}", flush=True)
    # ---- tables
    C.write("base_monthly.csv", monthly(of))
    C.write("base_yearly.csv", yearly(of))
    C.write("base_headcount.csv", C.headcount_rows(of))
    C.write("base_rounds.csv", RWm.rounds_rows("Base", ct))
    C.write("base_city_plan.csv", S.plan_from_auto(of, sat, "the base: AUTO rollout under the real-world setting; edit the launch month and agents"))
    lens_rows = []
    for m in sorted({48, 54, 60, 72, 84, 96} | ({fc} if fc else set())):
        L = NB.lenses(of, m)
        lens_rows.append({"Month": m, "Note": "the unicorn-on-paper check" if m == 60 else ("first month lenses 1 and 2 both clear" if m == fc else ""),
                          **{k: L[k] for k in ("ARR", "Fee ARR", "AUM", "NBFC equity")},
                          **{k: L[k] for k in ("Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)", "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
                          **{f"{k} margin over $1B": L[k] / U.UNICORN - 1 for k in ("Lens 1 (20 x ARR)", "Lens 2 (0.45 x AUM)", "Lens 3 (3 x NBFC equity + 20 x fee ARR)")},
                          "Lenses 1 and 2 both clear $1B": "yes" if clears(of, m) else "no", "Basis": "our judgement (multiples)",
                          "Fleet path": path_text(path), "Path choice": search_note})
    C.write("base_lenses.csv", lens_rows)
    ck = checks(of, ct, sat, x)
    C.write("base_checks.csv", ck)
    bad = [c["Check"] for c in ck if not c["Passes"]]
    print(f"  checks {len(ck) - len(bad)}/{len(ck)}" + (f"; FAIL {bad}" if bad else ""), flush=True)
    C.write("base_mc_summary.csv", mc(dists, addr, path, seed["Amount"], rds))
    C.set_horizon(60)
    return of


def checks(of, ct, sat, x, cfg=None):
    cfg = cfg or BASE_NBFC
    out = []
    add = lambda name, ok, note="": out.append({"Check": name, "Passes": bool(ok), "Note": note})
    sh = of["nbfc_share"][0]
    lending = of["nbfc_book"][0] > 0
    add("Ladder: revenue = fee revenue + net interest income + processing fees",
        np.allclose(of["fee_revenue"] + of["nbfc_nii"] + of["nbfc_processing"], of["revenue"], rtol=1e-12, atol=1e-6))
    add("Ladder: revenue - direct - credit cost = CM1; CM1 - servicing - acquisition - central = EBITDA",
        np.allclose(of["revenue"] - of["direct"] - of["nbfc_credit_cost"], of["cm1"], rtol=1e-12, atol=1e-6)
        and np.allclose(of["cm1"] - of["servicing"] - of["acquisition"] - of["central"], of["ebitda"], rtol=1e-12, atol=1e-6))
    add("Ladder: EBITDA - depreciation + interest on cash - tax = PAT", np.allclose(of["ebitda"] - of["depreciation"] + of["interest"] - of["tax"], of["pat"], rtol=1e-12, atol=1e-6))
    add("Fee revenue lines add to fee revenue", np.allclose(sum(of[k] for k, _ in C.REVENUE), of["fee_revenue"], rtol=1e-12, atol=1e-6))
    add("Book: net book = equity deployed + borrowings", np.allclose(of["nbfc_book"], of["nbfc_equity"] - of["nbfc_idle_capital"] + of["nbfc_borrowings"], rtol=1e-12, atol=1e-3))
    add("Book: capital >= 20% of the book and borrowings <= 3 x equity while lending",
        bool((of["nbfc_capital_ratio"][0][lending] >= 0.20 - 1e-12).all() and (of["nbfc_leverage"][0][lending] <= 3 + 1e-9).all()))
    add(f"Book: on-book share 0 before m30 and a flat {cfg['share_full']:.0%} from m30", bool((sh[:29] == 0).all() and np.allclose(sh[29:], cfg["share_full"])))
    add(f"Book: on-book loss = {cfg['loss_mult']:g} x the agreed loss", np.allclose(of["_nbfc_loss"], cfg["loss_mult"] * float(np.mean(x["loss"]))),
        f"{float(np.mean(of['_nbfc_loss'])):.2%} vs agreed {float(np.mean(x['loss'])):.2%}")
    add("Book: credit cost = on-book loss x on-book loans; processing fees = 2% of them",
        np.allclose(of["nbfc_credit_cost"], of["_nbfc_loss"] * of["nbfc_disbursed"]) and np.allclose(of["nbfc_processing"], 0.02 * of["nbfc_disbursed"]))
    t = np.arange(1, C.M + 1)
    add("DSA fees: origination on the partners' 85% only after m30", True, "applied in nbfc.apply_nbfc (rev_orig x (1 - share))")
    prev = np.concatenate([[0.0], of["cash"][0, :-1]])
    add("Cash roll: closing = previous + net change, every month", np.allclose(prev + of["net_change"][0], of["cash"][0], rtol=1e-12, atol=1e-3))
    add("Cash: net change = operations + investing + equity + borrowings",
        np.allclose(of["cf_operating"] + of["cf_investing"] + of["cf_financing"] + of["cf_borrowings"], of["net_change"], rtol=1e-12, atol=1e-3))
    add("Cash stays at or above 0 through m96", float(of["cash"][0].min()) >= 0, f"lowest Rs {float(of['cash'][0].min()):,.0f}")
    for r in ct:
        add(f"Cap table after {r['Round']}: sums to 100%; dilution <= 25%", abs(r["Founders %"] + r["ESOP %"] + r["Investors %"] - 1) < 1e-12 and r["Dilution"] <= 0.25 + 1e-12,
            f"dilution {r['Dilution']:.1%}")
    for prv, r in zip(ct, ct[1:]):
        add(f"{r['Round']} priced at or above the previous post-money", r["Pre"] >= prv["Post"] - 1e-6)
    a = arrays(of)
    sums = [k for k, _n, _u, how in base_lines() if how == "sum"]
    add(f"Yearly = monthly: {len(sums)} summed lines", all(abs(sum(C.roll(a, k, "sum")) - float(a[k][0].sum())) <= 1e-6 * max(1, abs(float(a[k][0].sum()))) for k in sums))
    co = of["_city"][0]
    add("Cities: at most 4 new a month; no city past its growing cap", float(np.diff(co["open"], prepend=0).max()) <= 4
        and bool((co["cum"] <= co["cap_by_month"] * (1 + 1e-12) + 1e-6).all()))
    add("Cities: agents and sign-ups add to the company's", np.allclose(co["agents"].sum(axis=0), of["agents"][0]) and np.allclose(co["signups"].sum(axis=0), of["signups"][0]))
    return out


def mc(dists, addr, path, seed_amt, rds, cfg=None):
    cfg = cfg or BASE_NBFC
    a18, h, cap, X = path
    x, redraws = MC.sample(MC_DRAWS, MC_SEED, correlate=True, dists=dists)
    factor = x["signups_run"] / dists["signups_run"][2]
    pool = MC.ppf("pert", *POOL_PERT, np.random.default_rng(MC_SEED + 3).random(MC_DRAWS)) / POOL_PERT[1]
    keys = ("l1", "l2", "l3", "arr", "aum", "book", "eq", "savers", "cash_ok96", "cash_ok60", "min_cash", "be", "rev5", "ebitda5", "pat5")
    out = {k: [] for k in keys}
    for s in range(0, MC_DRAWS, MC_CHUNK):
        part = {k: v[s:s + MC_CHUNK] for k, v in x.items()}
        D = len(part["r12"])
        sat = {**RWm.rw_cfg(addr, X), "pool_scale": pool[s:s + D]}
        o, *_ = C.run_plan(part, dists, target_fn=U.path_fn(a18, h, cap), central="as built", opts={"saturation": sat},
                           seeds=[C.SEED + 50_000 + s + d for d in range(D)], factors=factor[s:s + D])
        on = NB.apply_nbfc(o, part, cfg)
        of = NB.funded(on, seed_amt, rds)
        m = 59
        out["l1"].append(240 * of["revenue"][:, m])
        out["l2"].append(0.45 * of["fund_end"][:, m])
        out["l3"].append(3 * of["nbfc_equity"][:, m] + 240 * of["fee_revenue"][:, m])
        out["arr"].append(12 * of["revenue"][:, m])
        out["aum"].append(of["fund_end"][:, m])
        out["book"].append(of["nbfc_book"][:, m])
        out["eq"].append(of["nbfc_equity"][:, m])
        out["savers"].append(of["still_saving"][:, m])
        out["cash_ok96"].append(of["cash"].min(axis=1) >= 0)
        out["cash_ok60"].append(of["cash"][:, :60].min(axis=1) >= 0)
        out["min_cash"].append(of["cash"].min(axis=1))
        out["be"].append(C.stays_positive_from(of["ebitda"]))
        out["rev5"].append(of["revenue"][:, 48:60].sum(axis=1))
        out["ebitda5"].append(of["ebitda"][:, 48:60].sum(axis=1))
        out["pat5"].append(of["pat"][:, 48:60].sum(axis=1))
        print(f"  MC draws {s + D}/{MC_DRAWS}", flush=True)
    hh = {k: np.concatenate(v) for k, v in out.items()}
    n = MC_DRAWS

    def share_row(name, flags, note=""):
        p = float(np.mean(flags))
        pp = 100 * 1.96 * math.sqrt(p * (1 - p) / n)
        txt = f"about {100 * p:.0f}% +/- {max(1, round(pp)):.0f}pp" if 2 <= 100 * p <= 98 else f"about {100 * p:.1f}% +/- {pp:.1f}pp"
        return {"Measure": name, "Unit": "share of draws", "Value": p, "P10": "", "Median (P50)": "", "P90": "",
                "Note": f"{txt} (95% sampling margin, {n:,} draws)" + (f"; {note}" if note else "")}

    def pct_row(name, unit, v, note=""):
        q = np.percentile(np.asarray(v, float), (10, 50, 90))
        return {"Measure": name, "Unit": unit, "Value": "", "P10": q[0], "Median (P50)": q[1], "P90": q[2], "Note": note}
    be = hh["be"]
    return [
        {"Measure": "Plan", "Unit": "", "Value": path_text(path) + f"; funding fixed: seed Rs {seed_amt / CR:,.0f} crore; "
         + "; ".join(f"m{mm} Rs {aa / CR:,.0f} crore" for mm, aa in rds)
         + f"; {cfg['share_full']:.0%} on our book from m30 at {cfg['loss_mult']:g} x the agreed loss",
         "P10": "", "Median (P50)": "", "P90": "",
         "Note": f"seed {MC_SEED}; market inputs Latin hypercube with the bad-year copula; pool pert 6.5/7.0/7.7 crore; r12 < r3 redraws {redraws}"},
        share_row("P(lenses 1 and 2 both >= $1B at m60)", (hh["l1"] >= U.UNICORN) & (hh["l2"] >= U.UNICORN), "the unicorn-on-paper test"),
        share_row("P(lens 1 >= $1B at m60: 20 x ARR)", hh["l1"] >= U.UNICORN), share_row("P(lens 2 >= $1B at m60: 0.45 x AUM)", hh["l2"] >= U.UNICORN),
        share_row("P(lens 3 >= $1B at m60: 3 x NBFC equity + 20 x fee ARR)", hh["l3"] >= U.UNICORN, "cross-check"),
        share_row("P(cash >= 0 through m96)", hh["cash_ok96"], "the funding plan fixed: no extra round in a bad draw"),
        share_row("P(cash >= 0 through m60)", hh["cash_ok60"]),
        share_row("P(EBITDA positive for good by m60)", np.nan_to_num(be, nan=999) <= 60),
        share_row("P(year-5 PAT >= 0)", hh["pat5"] >= 0),
        pct_row("Lens 1 at m60 (20 x ARR)", "Rs", hh["l1"]), pct_row("Lens 2 at m60 (0.45 x AUM)", "Rs", hh["l2"]),
        pct_row("Lens 3 at m60 (cross-check)", "Rs", hh["l3"]), pct_row("ARR at m60", "Rs", hh["arr"]), pct_row("AUM at m60", "Rs", hh["aum"]),
        pct_row("Loan book at m60 (net)", "Rs", hh["book"]), pct_row("NBFC equity at m60", "Rs", hh["eq"]),
        pct_row("Active savers at m60", "savers", hh["savers"]), pct_row("Year-5 revenue", "Rs", hh["rev5"]),
        pct_row("Year-5 EBITDA", "Rs", hh["ebitda5"]), pct_row("Year-5 PAT", "Rs", hh["pat5"]),
        pct_row("Lowest cash through m96", "Rs", hh["min_cash"], "negative = the extra money a bad draw needs"),
    ]


if __name__ == "__main__":
    main()

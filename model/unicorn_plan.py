"""The unicorn plan: "unicorn on paper" by year 5 (story/BRIEF_unicorn_plan_2026-10-17.md, operator 17 Oct 2026).

Operator: "So i want to be a unicorn by year 5..." / "ignore the nbfc angle till 5 year" (distribution only, no own-book lending) /
"assume we can raise as much as possible if everything keeps holding, decide when to raise and how much and then work backwards
to make us unicorn on paper by year 5".

Basis Rs 100/$. Market inputs at the agreed likely values (each agent keeps his own sign-up draw); pay Rs 20,000 + 0.25% of
balance capped at Rs 10,000 a month (agreed key; both rise 7% a year); every cost rule as built, central team as built. The
company model runs 96 months (company_model.set_horizon(96)): beyond month 60 the take-up and approval growth are held at
year 5, the fee multiplier at 1.5x, and the agent pay rate is the agreed 0.10% after company month 60.

UNICORN ON PAPER at m60 = BOTH lenses >= $1B (Rs 10,000 crore); both are OUR JUDGEMENT:
  revenue lens  20 x ARR at m60 (ARR = 12 x month-60 revenue)   -> ARR >= Rs 500 crore;
  AUM lens      0.45 x AUM at m60 (month-end fund)               -> AUM >= Rs 22,222 crore. Basis SAV-03: Stable Money's
                Rs 2,507 crore post-money against about Rs 5,000 crore invested (SAV-02); that is CUMULATIVE money invested,
                not AUM, so the ratio is a rough proxy.
FLEET SEARCH: the earlier ramp scaled to a18 agents by m18, then h agents a month, capped at N (then replace leavers only).
Objective: the LEAST equity raised by m60 with both lenses clearing at m60; tie-break the least equity by m96. Also reported:
the least-equity path clearing the AUM lens alone, and the least-equity path clearing both lenses by m54.
FUNDING RULE (per path, on that path's own operating lines; unicorn fix 1, decided by the lead under the operator's "decide when
to raise and how much"; every multiple below is OUR JUDGEMENT):
  cadence  seed at m0; A m12, B m24, C m36, D m48; the unicorn round E in m54-m60, in the first month the lens value is at least
           Rs 10,000 crore; later rounds (F, ...) only when cash needs them. A round comes EARLIER, at the end of the month cash
           would fall to 6 months of forward burn; a cash-forced round between D and E is an extension (D-2, ...).
  price    pre-money = the HIGHER of (a) the step-up on the previous round's post-money (seed -> A 3.0x, A -> B 3.0x, B -> C 2.5x,
           C -> D 2.0x, D -> E 1.5x, later 1.5x, extensions 1.0x) and (b) the lens on that month's metrics (A: 25 x ARR or 0.45 x
           AUM; later: 20 x ARR or 0.45 x AUM), and never below the previous post-money. The seed is Rs 40 crore pre-money.
  size     24 months of forward burn + a Rs 10 crore buffer (rounded up to Rs 5 crore; the seed to Rs 1 crore) when that dilutes at
           most 25%, else 18 months + Rs 10 crore, else the 25% cap (pre-money / 3, rounded down to Rs 1 crore). Forward burn =
           costs paid + capex - commissions received (interest and tax left out: conservative).
  costs    the seed's Rs 5 lakh; Rs 15 lakh a later round (+ contingency), as the Series A (large rounds cost more in reality).
ROBUSTNESS (fix 2): the recommended path is the least equity raised by m60 that clears BOTH lenses with at least a +10% margin at
m60 at the likely values (the +20% path is reported for comparison).
CAP TABLE: founders 100% before the seed; an ESOP pool of 10% of the post-money created at the seed (out of the founders) and
topped up to 10% at A and B (out of the founders and earlier investors, pro rata); later rounds dilute everyone.

Writes tables/unicorn_search.csv, unicorn_rounds.csv, unicorn_yearly.csv, unicorn_monthly.csv, unicorn_milestones.csv,
unicorn_mc_summary.csv, unicorn_sizing_sensitivity.csv and unicorn_checks.csv. Nothing else is touched.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E          # noqa: E402
import cohort_mc as MC             # noqa: E402
import company_model as C          # noqa: E402

HORIZON = 96
CR = C.CRORE
UNICORN = 10_000 * CR
ARR_MULT_A, ARR_MULT, AUM_MULT = 25.0, 20.0, 0.45
ARR_NEED, AUM_NEED = UNICORN / ARR_MULT, UNICORN / AUM_MULT
SEED_PRE, DIL_CAP, BUFFER = 40 * CR, 0.25, 10 * CR
FWD_TRIGGER, FWD_SIZE, FWD_SIZE_MAX = 6, 18, 24
SCHEDULE = (("A", 12), ("B", 24), ("C", 36), ("D", 48))
STEP_UP = {"A": 3.0, "B": 3.0, "C": 2.5, "D": 2.0, "E": 1.5}
LATER_STEP, EXTENSION_STEP = 1.5, 1.0
UNICORN_WINDOW = (54, 60)
MARGIN, MARGIN_ALT = 0.10, 0.20
ESOP, ESOP_ROUNDS = 0.10, ("Seed", "A", "B")
LENS_MONTH = 60
CENTRAL = "as built"
A18 = (100, 150, 200, 250, 300)
HIRES = (100, 110, 120, 130, 140, 150, 175, 200)
CAPS = (7500, 10000, 15000)
REFINED = ((200, 225, 250, 275, 300), (140, 150, 160, 170, 180, 190, 200), (7500,))   # unicorn fix 3: around the grid edge
MC_DRAWS, MC_SEED, MC_CHUNK = 1000, 20261018, 25
LETTERS = "ABCDEFGHIJKLMNOP"


def path_fn(a18, h, cap):
    xs, ys = zip(*C.GROWTH_POINTS[:7])

    def tf(step=None):
        t = np.arange(C.M + 1)
        v = np.interp(np.minimum(t, 18), xs, np.asarray(ys, float) * a18 / 60.0)
        v = np.where(t > 18, a18 + h * (t - 18), v)
        return np.floor(np.minimum(v, cap) + 0.5).astype(int)
    return tf


def lens_values(o, m, d=0, stage=None):
    """(revenue-lens value, AUM-lens value) in month m (1-based); stage A prices the revenue lens at 25x."""
    arr = 12 * float(o["revenue"][d, m - 1])
    aum = float(o["fund_end"][d, m - 1])
    return (ARR_MULT_A if stage == "A" else ARR_MULT) * arr, AUM_MULT * aum, arr, aum


def operating_burn(o, d=0):
    """Cash used each month by operations and investing before interest and tax (round costs not included)."""
    fx = o.get("cf_fin_extra")                                # NBFC borrowings fund most of the book (nbfc.py)
    return -(o["ebitda_ex_a"][d] + o["cf_receivable"][d] + o["cf_investing"][d] + (fx[d] if fx is not None else 0.0))


def ceil_to(v, step):
    return math.ceil(round(v / step, 9)) * step


def floor_to(v, step):
    return math.floor(round(v / step, 9)) * step


def size_round(fwd, t, pre, step):
    """24 months of forward burn + buffer if that dilutes <= 25%, else 18 months, else the cap. Returns amount, wanted, capped."""
    w24 = ceil_to(fwd(t, FWD_SIZE_MAX) + BUFFER, step)
    if w24 / (pre + w24) <= DIL_CAP + 1e-12:
        return w24, w24, False
    w18 = ceil_to(fwd(t, FWD_SIZE) + BUFFER, step)
    if w18 / (pre + w18) <= DIL_CAP + 1e-12:
        return w18, w18, False
    return floor_to(pre / 3, CR), w18, True


def plan_rounds(o, d=0, max_rounds=30):
    """The funding rule on one path (see the module docstring). Returns the seed and the rounds as dicts."""
    M = C.M
    burn = operating_burn(o, d)
    fwd = lambda t, n: max(0.0, float(burn[t:t + n].sum()))        # months t+1..t+n
    amt, want, capped = size_round(fwd, 0, SEED_PRE, CR)
    seed = {"Round": "Seed", "Month": 0, "Amount": amt, "Pre": SEED_PRE, "Lens": "fixed Rs 40 crore", "Why": "start",
            "Capped": capped, "Wanted": want, "Step-up pre (Rs)": "", "Lens value (Rs)": ""}
    rounds, last, prev_post = [], 0, SEED_PRE + amt
    pending = list(SCHEDULE)
    unicorn_done, n_ext, n_later = False, 0, 0
    while len(rounds) < max_rounds:
        rds = [(r["Month"], r["Amount"]) for r in rounds]
        cash = C.treasury(o, seed_size=seed["Amount"], rounds=rds)["cash"][d]
        trig = next((t for t in range(last + 1, M) if cash[t - 1] <= fwd(t, FWD_TRIGGER)), None)
        if pending:
            stage, sched = pending[0]
            t, why = (trig, "cash would fall to 6 months of forward burn") if (trig and trig < sched) else (max(sched, last + 1), f"cadence (m{sched})")
            step_x = STEP_UP[stage]
            pending.pop(0)
        elif not unicorn_done:
            lo, hi = UNICORN_WINDOW
            tu = next((u for u in range(max(lo, last + 1), hi + 1) if max(lens_values(o, u, d, "E")[:2]) >= UNICORN), None)
            if trig and (tu is None or trig < tu) and trig < hi:
                n_ext += 1
                stage, t, why, step_x = f"D-{n_ext + 1}", trig, "cash would fall to 6 months of forward burn (extension)", EXTENSION_STEP
            else:
                unicorn_done = True
                if tu is None:
                    continue
                stage, t, why, step_x = "E", tu, "unicorn round: the lens value first reaches Rs 10,000 crore", STEP_UP["E"]
        else:
            if trig is None:
                break
            n_later += 1
            stage, t, why, step_x = LETTERS[4 + n_later], trig, "cash would fall to 6 months of forward burn", LATER_STEP
        if t is None or t >= M:
            break
        rl, al, arr, aum = lens_values(o, t, d, stage.split("-")[0])
        stepped = step_x * prev_post
        pre = max(stepped, rl, al, prev_post)
        amt, want, capped = size_round(fwd, t, pre, 5 * CR)
        if amt <= 0:
            break
        rounds.append({"Round": stage, "Month": t, "Amount": amt, "Pre": pre,
                       "Lens": f"step-up {step_x:g}x" if stepped >= max(rl, al) else ("revenue lens" if rl >= al else "AUM lens"),
                       "Why": why, "Capped": capped, "Wanted": want, "ARR": arr, "AUM": aum,
                       "Step-up pre (Rs)": stepped, "Lens value (Rs)": max(rl, al)})
        prev_post, last = pre + amt, t
    return seed, rounds


def cap_table(seed, rounds):
    f, e, v = 1.0, 0.0, 0.0
    rows = []
    for r in [seed] + rounds:
        post = r["Pre"] + r["Amount"]
        dnew = r["Amount"] / post
        if r["Round"] in ESOP_ROUNDS:
            rest = 1.0 - dnew - ESOP
            fv = f + v
            f, v, e = f / fv * rest, v / fv * rest + dnew, ESOP
        else:
            f, e, v = f * (1 - dnew), e * (1 - dnew), v * (1 - dnew) + dnew
        rows.append({**r, "Post": post, "Dilution": dnew, "Founders %": f, "ESOP %": e, "Investors %": v})
    return rows


def apply_funding(o, seed_amt, rds):
    """o with the plan's funding: fund-raising costs, contingency, central, EBITDA re-stated; interest, tax and cash from it."""
    o = dict(o)
    t = np.arange(1, C.M + 1)[None, :]
    o["cost_raise"] = o["cost_raise_seed"] + sum(C.SERIES_A_COST * (t == m) for m, a in rds if a > 0)
    cen_ex = sum(o[k] for k, _ in C.CENTRAL_COSTS)
    o["cost_contingency"] = C.CONTINGENCY * (o["direct"] + o["servicing"] + o["acquisition"] + cen_ex)
    o["central"] = cen_ex + o["cost_contingency"]
    o["ebitda"] = o["cm3"] - o["central"]
    o["ebit"] = o["ebitda"] - o["depreciation"]
    o["opex"] = o["direct"] + o["servicing"] + o["acquisition"] + o["central"]
    tr = C.treasury(o, seed_size=seed_amt, rounds=rds)
    assert np.allclose(tr["ebit_plan"], o["ebit"], rtol=1e-12, atol=1e-6)
    o.update(tr)
    o["cash_seed_only"] = C.treasury(o, seed_size=seed_amt, rounds=[])["cash"]
    o["burn"] = -(o["cf_operating"] + o["cf_investing"])
    return o


def evaluate(x, dists, a18, h, cap, keep=False):
    o, fleets, targets, _info = C.run_plan(x, dists, target_fn=path_fn(a18, h, cap), central=CENTRAL, keep=keep)
    seed, rounds = plan_rounds(o)
    rds = [(r["Month"], r["Amount"]) for r in rounds]
    of = apply_funding(o, seed["Amount"], rds)
    ct = cap_table(seed, rounds)
    return o, of, seed, rounds, ct, fleets[0], targets[0]


def search(x, dists, grids=(("coarse", (A18, HIRES, CAPS)), ("refined", REFINED))):
    rows, seen = [], set()
    plan = [(g, a18, h, cap) for g, (aa, hh, cc) in grids for a18 in aa for h in hh for cap in cc]
    for grid, a18, h, cap in plan:
        if (a18, h, cap) in seen:
            continue
        seen.add((a18, h, cap))
        o, of, seed, rounds, ct, _f, _t = evaluate(x, dists, a18, h, cap)
        rl, al, arr, aum = lens_values(of, LENS_MONTH)
        rl54, al54, *_ = lens_values(of, 54)
        eq60 = seed["Amount"] + sum(r["Amount"] for r in rounds if r["Month"] <= LENS_MONTH)
        eq96 = seed["Amount"] + sum(r["Amount"] for r in rounds)
        cash = of["cash"][0]
        uni = next((r for r in ct if r["Round"] == "E"), None)
        hires = of["hired"][0]
        rows.append({"Path": len(rows) + 1, "Grid": grid, "Agents at m18": a18, "Hires a month after m18": h, "Agent cap": cap,
                     "Peak agents hired in a month (growth and replacements)": float(hires.max()),
                     "Month of the peak hiring": int(hires.argmax() + 1),
                     "Agents at m60": float(of["agents"][0, 59]), "ARR at m60 (Rs)": arr, "AUM at m60 (Rs)": aum,
                     "Revenue lens at m60 (Rs, 20 x ARR)": rl, "AUM lens at m60 (Rs, 0.45 x AUM)": al,
                     "Both lenses >= $1B at m60": "yes" if min(rl, al) >= UNICORN else "no",
                     "AUM lens >= $1B at m60": "yes" if al >= UNICORN else "no",
                     "Revenue lens >= $1B at m60": "yes" if rl >= UNICORN else "no",
                     "Both lenses >= $1B at m54": "yes" if min(rl54, al54) >= UNICORN else "no",
                     "Equity raised by m60 (Rs)": eq60, "Equity raised by m96 (Rs)": eq96, "Rounds": 1 + len(rounds),
                     "Rounds capped at 25% dilution": sum(r["Capped"] for r in [seed] + rounds),
                     "Unicorn round (E) month": uni["Month"] if uni else "none",
                     "Founders % after the unicorn round (E)": uni["Founders %"] if uni else "",
                     "Revenue lens margin over $1B at m60": rl / UNICORN - 1, "AUM lens margin over $1B at m60": al / UNICORN - 1,
                     "Both lenses >= $1B + 10% at m60": "yes" if min(rl, al) >= UNICORN * (1 + MARGIN) else "no",
                     "Both lenses >= $1B + 20% at m60": "yes" if min(rl, al) >= UNICORN * (1 + MARGIN_ALT) else "no",
                     "Cash stays at or above 0 through m96": "yes" if cash.min() >= 0 else "no",
                     "Lowest cash (Rs)": float(cash.min()),
                     "EBITDA turns positive and stays (month)": "not within 96" if np.isnan(C.stays_positive_from(of["ebitda"])[0])
                     else float(C.stays_positive_from(of["ebitda"])[0])})
    return rows


def pick(rows, cond):
    ok = [r for r in rows if cond(r) and r["Cash stays at or above 0 through m96"] == "yes"]
    return min(ok, key=lambda r: (r["Equity raised by m60 (Rs)"], r["Equity raised by m96 (Rs)"])) if ok else None


def yearly_table(of):
    a = C.table_arrays(of)
    Y = C.M // 12
    s = lambda k: [float(a[k][0, 12 * y:12 * y + 12].sum()) for y in range(Y)]
    e = lambda k: [float(a[k][0, 12 * y + 11]) for y in range(Y)]
    rows = []

    def add(line, unit, vals, note=""):
        rows.append({"Line": line, "Unit": unit, **{f"Year {y + 1}": vals[y] for y in range(Y)},
                     "Note": note or ("years 6-8 are context" if Y > 5 else "")})
    for k, nm in C.REVENUE:
        add(f"Revenue: {nm}", "Rs", s(k))
    add("Revenue, total", "Rs", s("revenue"))
    for k, nm in (("cm1", "CM1"), ("cm2", "CM2"), ("cm3", "CM3"), ("ebitda", "EBITDA"), ("depreciation", "Depreciation"),
                  ("interest", "Interest on cash"), ("tax", "Income tax"), ("pat", "PAT")):
        add(nm, "Rs", s(k))
    add("Equity raised", "Rs", s("cf_financing"))
    add("Closing cash", "Rs", e("cash"))
    add("Agents at year end", "agents", e("agents"))
    add("Agents hired in the year (growth and replacements)", "agents", s("hired"))
    add("Peak agents hired in a month (growth and replacements)", "agents", [float(a["hired"][0, 12 * y:12 * y + 12].max()) for y in range(Y)])
    add("Agents who left in the year", "agents", s("left"))
    add("Cities at year end", "cities", e("cities"))
    add("New cities opened in the year", "cities", [float(a["cities"][0, 12 * y + 11] - (a["cities"][0, 12 * y - 1] if y else 0.0)) for y in range(Y)])
    add("Central team at year end", "people", e("hc_central"))
    add("Active savers at year end", "savers", e("still_saving"))
    add("AUM at year end", "Rs", e("fund_end"))
    add("ARR at year end (12 x the month's revenue)", "Rs", [12 * v for v in e("revenue")])
    add("Money lent in the year, personal loans incl. top-ups", "Rs", s("money_lent"))
    add("Money lent in the year, home loans and LAP (other lenders)", "Rs", s("housing_lent"))
    add("Revenue lens at year end (20 x ARR; our judgement)", "Rs", [ARR_MULT * 12 * v for v in e("revenue")])
    add("AUM lens at year end (0.45 x AUM; our judgement, SAV-03 proxy)", "Rs", [AUM_MULT * v for v in e("fund_end")])
    return rows


def monthly_rows(of):
    rows = C.monthly_rows(of)
    ren = {"Cash flow, financing: Series A (end of month 18) (Rs)": "Cash flow, financing: rounds A onwards (end of their months) (Rs)",
           "Closing cash, seed only (no Series A) (Rs)": "Closing cash, seed only (no later rounds) (Rs)",
           "Closing cash, with the Series A (Rs)": "Closing cash, with every round (Rs)"}
    out = []
    for r in rows:
        r2 = {ren.get(k, k): v for k, v in r.items()}
        m = r2["Month"] - 1
        r2["ARR (12 x the month's revenue) (Rs)"] = 12 * float(of["revenue"][0, m])
        r2["Revenue lens (20 x ARR; judgement) (Rs)"] = ARR_MULT * 12 * float(of["revenue"][0, m])
        r2["AUM lens (0.45 x AUM; judgement) (Rs)"] = AUM_MULT * float(of["fund_end"][0, m])
        out.append(r2)
    return out


def milestones(of, ct):
    rows = []
    for r in ct:
        m = max(1, r["Month"])
        rl, al, arr, aum = lens_values(of, m, 0, r["Round"].split("-")[0])
        rows.append({"When": f"{r['Round']} round, month {r['Month']}", "Month": r["Month"], "Agents": float(of["agents"][0, m - 1]),
                     "Active savers": float(of["still_saving"][0, m - 1]), "AUM (Rs)": aum, "ARR (Rs)": arr,
                     "Revenue that month (Rs)": float(of["revenue"][0, m - 1]), "EBITDA that month (Rs)": float(of["ebitda"][0, m - 1]),
                     "Cash at month end before the round lands (Rs)": float(of["cash"][0, m - 1] - (r["Amount"] if r["Month"] else 0.0)),
                     "Revenue lens (Rs)": rl if r["Month"] else "", "AUM lens (Rs)": al if r["Month"] else "",
                     "Pre-money used (Rs)": r["Pre"], "Lens used": r["Lens"]})
    rl, al, arr, aum = lens_values(of, LENS_MONTH)
    for nm, val, need, metric, mval in (("Revenue lens (20 x ARR)", rl, ARR_NEED, "ARR", arr), ("AUM lens (0.45 x AUM)", al, AUM_NEED, "AUM", aum)):
        rows.append({"When": f"UNICORN CHECK at m60: {nm}", "Month": LENS_MONTH, "Agents": float(of["agents"][0, 59]),
                     "Active savers": float(of["still_saving"][0, 59]), "AUM (Rs)": aum, "ARR (Rs)": arr,
                     "Revenue that month (Rs)": float(of["revenue"][0, 59]), "EBITDA that month (Rs)": float(of["ebitda"][0, 59]),
                     "Valuation on the lens (Rs)": val, "Threshold (Rs)": UNICORN, "Margin over $1B (share)": val / UNICORN - 1,
                     "Metric needed for $1B": f"{metric} Rs {need:,.0f}", "Clears": "yes" if val >= UNICORN else "no", "Basis": "our judgement"})
    cols = list(dict.fromkeys(k for r in rows for k in r))
    return [{k: r.get(k, "") for k in cols} for r in rows]


def checks(of, ct, rec, x, dists, o96_prefix_ok):
    rows = []

    def add(name, ok, note=""):
        rows.append({"Check": name, "Passes": bool(ok), "Note": note})
    o = of
    add("Ladder: CM1 - servicing - acquisition - central = EBITDA, every month",
        np.allclose(o["cm1"] - o["servicing"] - o["acquisition"] - o["central"], o["ebitda"], rtol=1e-12, atol=1e-6))
    add("Ladder: EBITDA - depreciation + interest - tax = PAT, every month",
        np.allclose(o["ebitda"] - o["depreciation"] + o["interest"] - o["tax"], o["pat"], rtol=1e-12, atol=1e-6))
    add("Ladder: revenue lines add to revenue", np.allclose(sum(o[k] for k, _ in C.REVENUE), o["revenue"], rtol=1e-12, atol=1e-6))
    prev = np.concatenate([[0.0], o["cash"][0, :-1]])
    add("Cash roll: closing(t) = closing(t - 1) + net change, every month", np.allclose(prev + o["net_change"][0], o["cash"][0], rtol=1e-12, atol=1e-3))
    direct = o["received"] + o["interest"] - o["opex"] - o["tax"] - o["capex_laptops"] - o["capex_integrations"] + o["cf_financing"]
    add("Cash: the indirect statement = the direct one", np.allclose(direct, o["net_change"], rtol=1e-12, atol=1e-3))
    raised = sum(r["Amount"] for r in ct)
    add("Cash flow: equity in the statements = the rounds table", abs(float(o["cf_financing"][0].sum()) - raised) <= 1e-3, f"Rs {raised:,.0f}")
    add("Cash stays at or above 0 through m96", float(o["cash"][0].min()) >= 0, f"lowest Rs {float(o['cash'][0].min()):,.0f}")
    for r in ct:
        tot = r["Founders %"] + r["ESOP %"] + r["Investors %"]
        add(f"Cap table after the {r['Round']} round sums to 100%", abs(tot - 1) <= 1e-12, f"{tot:.12f}")
        add(f"{r['Round']} round dilution at most 25%", r["Dilution"] <= DIL_CAP + 1e-12, f"{r['Dilution']:.1%}")
    for prev, r in zip(ct, ct[1:]):
        add(f"{r['Round']} round priced at or above the previous post-money (no down round)", r["Pre"] >= prev["Post"] - 1e-6,
            f"pre Rs {r['Pre']:,.0f} vs previous post Rs {prev['Post']:,.0f}")
    uni = next((r for r in ct if r["Round"] == "E"), None)
    add("Unicorn round (E) in m54-m60 with pre-money at or above Rs 10,000 crore", uni is not None and 54 <= uni["Month"] <= 60
        and uni["Pre"] >= UNICORN, f"month {uni['Month']}, pre Rs {uni['Pre']:,.0f}" if uni else "no E round")
    rl_, al_, *_ = lens_values(of, LENS_MONTH)
    add("Both lenses clear $1B with at least a 10% margin at m60 (the robustness rule)", min(rl_, al_) >= UNICORN * (1 + MARGIN),
        f"revenue lens {rl_ / UNICORN - 1:+.1%}, AUM lens {al_ / UNICORN - 1:+.1%}")
    for r in ct:
        if r["Round"] in ESOP_ROUNDS:
            add(f"ESOP at 10% after the {r['Round']} round", abs(r["ESOP %"] - ESOP) <= 1e-12)
    a = C.table_arrays(o)
    sums = [k for k, _n, _u, how in C.LINES if how == "sum"]
    add(f"Yearly = monthly: {len(sums)} summed lines, years 1-{C.M // 12}",
        all(abs(sum(float(a[k][0, 12 * y:12 * y + 12].sum()) for y in range(C.M // 12)) - float(a[k][0].sum())) <= 1e-6 * max(1, abs(float(a[k][0].sum()))) for k in sums))
    rl, al, arr, aum = lens_values(o, LENS_MONTH)
    add("Lens arithmetic: 20 x ARR >= Rs 10,000 crore exactly when ARR >= Rs 500 crore", (rl >= UNICORN) == (arr >= ARR_NEED))
    add("Lens arithmetic: 0.45 x AUM >= Rs 10,000 crore exactly when AUM >= Rs 22,222 crore", (al >= UNICORN) == (aum >= AUM_NEED))
    add("96-month horizon: months 1-60 of the recommended path = the same path run over 60 months (revenue, EBITDA, savers)", o96_prefix_ok)
    return rows


def prefix_check(x, dists, a18, h, cap, o96):
    C.set_horizon(60)
    try:
        o60, *_ = C.run_plan(x, dists, target_fn=path_fn(a18, h, cap), central=CENTRAL)
    finally:
        C.set_horizon(HORIZON)
    return all(np.allclose(o60[k][0], o96[k][0, :60], rtol=1e-9, atol=1e-3) for k in ("revenue", "cm3", "ebitda", "still_saving", "agents", "fund_end"))


def mc(dists, a18, h, cap, seed_amt, rds):
    """1,000 draws; the fleet path and the funding plan fixed; market inputs drawn (Latin hypercube, the bad-year copula); the
    common sign-up factor and each agent's own draw as in company_mc."""
    x, redraws = MC.sample(MC_DRAWS, MC_SEED, correlate=True, dists=dists)
    factor = x["signups_run"] / dists["signups_run"][2]
    keys = ("rl", "al", "arr", "aum", "cash_ok", "cash_ok60", "min_cash", "pat_y5", "ebitda_y5")
    out = {k: [] for k in keys}
    for s in range(0, MC_DRAWS, MC_CHUNK):
        part = {k: v[s:s + MC_CHUNK] for k, v in x.items()}
        D = len(part["r12"])
        o, *_ = C.run_plan(part, dists, target_fn=path_fn(a18, h, cap), central=CENTRAL,
                           seeds=[C.SEED + 30_000 + s + d for d in range(D)], factors=factor[s:s + D])
        tr = C.treasury(o, seed_size=seed_amt, rounds=rds)
        arr = 12 * o["revenue"][:, LENS_MONTH - 1]
        aum = o["fund_end"][:, LENS_MONTH - 1]
        out["rl"].append(ARR_MULT * arr)
        out["al"].append(AUM_MULT * aum)
        out["arr"].append(arr)
        out["aum"].append(aum)
        out["cash_ok"].append(tr["cash"].min(axis=1) >= 0)
        out["cash_ok60"].append(tr["cash"][:, :60].min(axis=1) >= 0)
        out["min_cash"].append(tr["cash"].min(axis=1))
        out["pat_y5"].append(tr["pat"][:, 48:60].sum(axis=1))
        out["ebitda_y5"].append((tr["ebit_plan"] + o["depreciation"])[:, 48:60].sum(axis=1))
        print(f"  MC draws {s + D}/{MC_DRAWS}", flush=True)
    h_ = {k: np.concatenate(v) for k, v in out.items()}
    n = MC_DRAWS

    def share(name, flags, note=""):
        p = float(np.mean(flags))
        pp = 100 * 1.96 * math.sqrt(p * (1 - p) / n)
        txt = f"about {100 * p:.0f}% +/- {max(1, round(pp)):.0f}pp" if 2 <= 100 * p <= 98 else f"about {100 * p:.1f}% +/- {pp:.1f}pp"
        return {"Measure": name, "Unit": "share of draws", "Value": p, "P10": "", "Median (P50)": "", "P90": "",
                "Note": f"{txt} (95% sampling margin, {n:,} draws)" + (f"; {note}" if note else "")}

    def pct(name, unit, v, note=""):
        q = np.percentile(v, (10, 50, 90))
        return {"Measure": name, "Unit": unit, "Value": "", "P10": q[0], "Median (P50)": q[1], "P90": q[2], "Note": note}
    both = (h_["rl"] >= UNICORN) & (h_["al"] >= UNICORN)
    return [
        {"Measure": "Plan", "Unit": "", "Value": f"{a18} agents by m18, +{h} a month, cap {cap:,}; funding fixed: seed Rs {seed_amt / CR:,.0f} crore; "
         + "; ".join(f"m{m} Rs {a / CR:,.0f} crore" for m, a in rds), "P10": "", "Median (P50)": "", "P90": "",
         "Note": f"seed {MC_SEED}; market inputs Latin hypercube with the bad-year copula; r12 < r3 redraws {redraws}"},
        share("P(both lenses >= $1B at m60)", both, "20 x ARR and 0.45 x AUM, both our judgement"),
        share("P(AUM lens >= $1B at m60)", h_["al"] >= UNICORN), share("P(revenue lens >= $1B at m60)", h_["rl"] >= UNICORN),
        share("P(cash >= 0 through m96)", h_["cash_ok"], "the funding plan fixed: no extra rounds in a bad draw"),
        share("P(cash >= 0 through m60)", h_["cash_ok60"]),
        pct("Revenue-lens valuation at m60 (20 x ARR)", "Rs", h_["rl"]), pct("AUM-lens valuation at m60 (0.45 x AUM)", "Rs", h_["al"]),
        pct("ARR at m60", "Rs", h_["arr"]), pct("AUM at m60", "Rs", h_["aum"]),
        pct("Lowest cash through m96", "Rs", h_["min_cash"], "negative = the extra money a bad draw needs"),
        pct("Year-5 EBITDA", "Rs", h_["ebitda_y5"]), pct("Year-5 PAT", "Rs", h_["pat_y5"]),
    ]


def main():
    dists = E.load_dists()[0]
    x = E.likely_inputs(dists)
    C.set_horizon(HORIZON)
    rows = search(x, dists)
    rec = pick(rows, lambda r: r["Both lenses >= $1B + 10% at m60"] == "yes")
    alt20 = pick(rows, lambda r: r["Both lenses >= $1B + 20% at m60"] == "yes")
    thin = pick(rows, lambda r: r["Both lenses >= $1B at m60"] == "yes")
    aum_only = pick(rows, lambda r: r["AUM lens >= $1B at m60"] == "yes" and r["Revenue lens >= $1B at m60"] == "no")
    fast = pick(rows, lambda r: r["Both lenses >= $1B at m54"] == "yes")
    for r in rows:
        r["Role"] = "; ".join(lbl for lbl, p in (("RECOMMENDED: least equity by m60, both lenses >= $1B + 10% at m60", rec),
                                                  ("least equity with both lenses >= $1B + 20% at m60 (comparison)", alt20),
                                                  ("least equity with both lenses just >= $1B at m60 (no margin)", thin),
                                                  ("least equity clearing the AUM lens only", aum_only),
                                                  ("least equity clearing both lenses by m54", fast)) if p is not None and p["Path"] == r["Path"])
    C.write("unicorn_search.csv", rows)
    assert rec is not None, "no path clears both lenses at m60 with a 10% margin and cash >= 0"
    a18, h, cap = rec["Agents at m18"], rec["Hires a month after m18"], rec["Agent cap"]
    o, of, seed, rounds, ct, fleet, target = evaluate(x, dists, a18, h, cap)
    rds = [(r["Month"], r["Amount"]) for r in rounds]
    uni = next((r for r in ct if r["Round"] == "E"), None)
    C.write("unicorn_rounds.csv", [{"Round": r["Round"], "Month": r["Month"], "Amount (Rs)": r["Amount"], "Pre-money (Rs)": r["Pre"],
                                    "Post-money (Rs)": r["Post"], "Dilution (new investors' share of post-money)": r["Dilution"],
                                    "Founders % after": r["Founders %"], "ESOP % after": r["ESOP %"], "Investors % after": r["Investors %"],
                                    "Priced on": r["Lens"], "Step-up pre-money (Rs)": r["Step-up pre (Rs)"], "Lens value (Rs)": r["Lens value (Rs)"],
                                    "Why this month": r["Why"],
                                    "Capped at 25% dilution": "yes (wanted Rs {:,.0f})".format(r["Wanted"]) if r["Capped"] else "no",
                                    "Unicorn round": "yes" if r is uni else "",
                                    "Basis": "valuations are our judgement (lens multiples and step-ups)"} for r in ct])
    C.write("unicorn_yearly.csv", yearly_table(of))
    C.write("unicorn_monthly.csv", monthly_rows(of))
    C.write("unicorn_milestones.csv", milestones(of, ct))
    ok = prefix_check(x, dists, a18, h, cap, o)
    ck = checks(of, ct, rec, x, dists, ok)
    C.write("unicorn_checks.csv", ck)
    bad = [c["Check"] for c in ck if not c["Passes"]]
    print(f"  {len(rows)} paths; recommended path {rec['Path']}: {a18} by m18, +{h} a month, cap {cap}; equity by m60 Rs "
          f"{rec['Equity raised by m60 (Rs)'] / CR:,.0f} crore; checks {len(ck) - len(bad)}/{len(ck)}" + (f" FAIL {bad}" if bad else ""))
    for p, lbl in ((alt20, "both +20%"), (thin, "both, no margin"), (aum_only, "AUM lens only"), (fast, "both by m54")):
        if p:
            print(f"  {lbl}: path {p['Path']} {p['Agents at m18']} +{p['Hires a month after m18']} cap {p['Agent cap']}: equity by m60 Rs "
                  f"{p['Equity raised by m60 (Rs)'] / CR:,.0f} crore")
    for r in ct:
        print(f"  {r['Round']:>4} m{r['Month']:>2} Rs {r['Amount'] / CR:>7,.0f} cr pre {r['Pre'] / CR:>8,.0f} post {r['Post'] / CR:>8,.0f} "
              f"dil {r['Dilution']:.1%} founders {r['Founders %']:.1%} {'CAPPED' if r['Capped'] else ''} {r['Why']}")
    assert not bad
    sens = []
    for months, label in ((FWD_SIZE_MAX, "24 months of forward burn when dilution allows, else 18 (the plan)"),
                          (FWD_SIZE, "18 months of forward burn always (the low end)")):
        keep_max = globals()["FWD_SIZE_MAX"]
        globals()["FWD_SIZE_MAX"] = months
        try:
            _o, of2, sd2, rd2, ct2, *_ = evaluate(x, dists, a18, h, cap)
        finally:
            globals()["FWD_SIZE_MAX"] = keep_max
        e2 = next((r for r in ct2 if r["Round"] == "E"), None)
        sens.append({"Round sizing": label, "Equity raised by m60 (Rs)": sd2["Amount"] + sum(r["Amount"] for r in rd2 if r["Month"] <= LENS_MONTH),
                     "Equity raised by m96 (Rs)": sd2["Amount"] + sum(r["Amount"] for r in rd2),
                     "Founders % after the unicorn round": e2["Founders %"] if e2 else "", "Lowest cash through m96 (Rs)": float(of2["cash"][0].min()),
                     "Path": f"{a18} by m18, +{h} a month, cap {cap:,}"})
    C.write("unicorn_sizing_sensitivity.csv", sens)
    C.write("unicorn_mc_summary.csv", mc(dists, a18, h, cap, seed["Amount"], rds))
    return rows


if __name__ == "__main__":
    main()

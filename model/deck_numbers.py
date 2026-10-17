"""Every number the deck quotes, computed from the engine and the research tables.

Writes tables/deck_numbers.csv: id, value, display, unit, population, source.
The slides quote `display` strings only; check_deck.py confirms every number on a
slide appears here (or is a date or a slide/lever label).
"""
import csv
import re

import engine as E

OUT = E.TABLES / "deck_numbers.csv"
rows = []


def add(id, value, display, unit, population, source):
    rows.append({"id": id, "value": value, "display": display, "unit": unit, "population": population, "source": source})


def inr(x):
    s = f"{abs(x):,.0f}"
    return ("−₹" if x < 0 else "₹") + s


def cr(x, d=1):
    return ("−₹" if x < 0 else "₹") + f"{abs(x):,.{d}f} crore"


def x1(v):
    return (f"−{abs(v):.1f}" if v < 0 else f"{v:.1f}")


MODEL = "model: savings_first_model.xlsx (engine.py), 30 Sep 2026"
PLAN = "plan = daily saving + 5% loss cover + gold"

# ---------------------------------------------------------------- plan, three scenarios
res = {s: E.run(s) for s in E.SCENARIOS}
for s, (p, crow, o, ch) in res.items():
    add(f"plan_{s}_cac", o["cac"], inr(o["cac"]), "INR per activated saver", f"{PLAN}, {s}; fully loaded", MODEL)
    add(f"plan_{s}_payback", o["payback_months"], f"{o['payback_months']} months" if o["payback_months"] else "never (60 months)",
        "months", f"{PLAN}, {s}; undiscounted", MODEL)
    for k in ("ltv36", "ltv60"):
        add(f"plan_{s}_{k}", o[k], inr(o[k]), "INR per activated saver", f"{PLAN}, {s}; contribution margin discounted 20%/yr", MODEL)
        add(f"plan_{s}_{k}_cac", o[f"{k}_cac"], x1(o[f"{k}_cac"]), "ratio", f"{PLAN}, {s}", MODEL)
    add(f"plan_{s}_cap_per_rev", o["capital_per_rev"], f"₹{o['capital_per_rev']:.2f}", "INR per INR 1 of yr-1 revenue",
        f"{PLAN}, {s}; guarantee deposits", MODEL)
    for y in range(1, 6):
        add(f"plan_{s}_rev_pa_y{y}", o[f"y{y}_rev_per_active"], inr(o[f"y{y}_rev_per_active"]), "INR per active saver per year",
            f"{PLAN}, {s}; cohort year {y}; gross revenue to us", MODEL)
        add(f"plan_{s}_cm_pa_y{y}", o[f"y{y}_cm_per_active"], inr(o[f"y{y}_cm_per_active"]), "INR per active saver per year",
            f"{PLAN}, {s}; cohort year {y}; contribution margin", MODEL)
        for line in E.REV_LINES:
            v = o[f"y{y}_rev_per_active::{line}"]
            add(f"plan_{s}_rev_pa_y{y}::{line}", v, inr(v), "INR per active saver per year", f"{PLAN}, {s}; cohort year {y}; {line}", MODEL)
    pr = E.path(p, o)
    for r in pr:
        add(f"plan_{s}_path_y{r['year']}_usd_m", r["rev_usd_m"], f"${r['rev_usd_m']:.0f}M", "USD million",
            f"{PLAN}, {s}; calendar year {r['year']}; revenue at Rs {p['usd_inr']}/USD", MODEL + " + inputs_path.csv")
        add(f"plan_{s}_path_y{r['year']}_active_m", r["active"] / 1e6, f"{r['active'] / 1e6:.1f}M", "million active savers",
            f"{PLAN}, {s}; calendar year {r['year']}; average in year", MODEL)
        need = max(0.0, -min(x["cum_cash"] for x in pr[:r["year"]])) / 1e7
        add(f"plan_{s}_need_y{r['year']}_cr", need, cr(need), "INR crore", f"{PLAN}, {s}; capital needed to reach end of year {r['year']}", MODEL)
    peak = max(0.0, -min(x["cum_cash"] for x in pr)) / 1e7
    add(f"plan_{s}_peak_cr", peak, cr(peak, 0), "INR crore", f"{PLAN}, {s}; peak capital over 10 years", MODEL)
    y1 = pr[0]
    for k in ("rev", "cm", "cac_spend", "fixed_opex", "capital", "cash"):
        add(f"plan_{s}_y1_{k}_cr", y1[k] / 1e7, cr(y1[k] / 1e7), "INR crore", f"{PLAN}, {s}; calendar year 1 (pilot: 25,000 savers)", MODEL)
    for m in (1, 3, 6, 12, 24):
        r = crow[m - 1]
        add(f"plan_{s}_m{m}_still", r["survival"], f"{r['survival']:.0%}", "share of activated savers", f"{s}; month {m}", MODEL)
        add(f"plan_{s}_m{m}_borrowed", r["borrowed_share"], f"{r['borrowed_share']:.0%}", "share of active savers", f"{s}; month {m}", MODEL)
        add(f"plan_{s}_m{m}_insured", r["insured_share"], f"{r['insured_share']:.0%}", "share of active savers", f"{s}; month {m}", MODEL)
        add(f"plan_{s}_m{m}_saved", r["contributions"] / r["active"], inr(r["contributions"] / r["active"]), "INR per active saver per month",
            f"{s}; month {m}", MODEL)
    add(f"plan_{s}_serve_month", None, None, "", "", "")
rows[:] = [r for r in rows if r["display"] is not None]

# ---------------------------------------------------------------- by segment (gig / non-gig halves of the plan)
for s_ in E.SCENARIOS:
    _, _, o, _ = E.run(s_)
    for seg, so in o["seg"].items():
        c = o["seg_cac"][seg]
        add(f"seg_{seg}_{s_}_cac", c, inr(c), "INR per activated saver", f"{PLAN}, {seg} half, {s_}", MODEL)
        add(f"seg_{seg}_{s_}_ltv60_cac", so["ltv60_cac"], x1(so["ltv60_cac"]), "ratio", f"{PLAN}, {seg} half, {s_}", MODEL)
        add(f"seg_{seg}_{s_}_still_m12", so["m12_still"], f"{so['m12_still']:.0%}", "share of activated savers", f"{PLAN}, {seg} half, {s_}, month 12", MODEL)
        add(f"seg_{seg}_{s_}_rev_pa_y2", so["y2_rev_per_active"], inr(so["y2_rev_per_active"]), "INR per active saver per year", f"{PLAN}, {seg} half, {s_}, year 2", MODEL)

# ---------------------------------------------------------------- as briefed (no levers) and each lever
for r in csv.DictReader(open(E.TABLES / "levers_results.csv")):
    key = r["lever"].split(".")[0].split(" (")[0].strip().replace(" ", "").replace(",", "")
    v = float(r["ltv60_cac"])
    add(f"lever_{key}_{r['scenario']}_ltv60_cac", v, x1(v), "ratio", f"lever {r['lever']}, {r['scenario']}", "levers.py / Levers tab")
    y10 = float(r["y10_usd_m"])
    add(f"lever_{key}_{r['scenario']}_y10", y10, f"${y10:.0f}M", "USD million", f"lever {r['lever']}, {r['scenario']}, year 10", "levers.py / Levers tab")
    fy = r["first_year_100m"]
    add(f"lever_{key}_{r['scenario']}_first100", fy, f"year {int(float(fy))}" if fy not in ("", "None") else "not within 10 years", "year",
        f"lever {r['lever']}, {r['scenario']}", "levers.py / Levers tab")

# ---------------------------------------------------------------- lending-first (Bueno as run)
for s in E.SCENARIOS:
    p = E.load_inputs(s)
    _, lo = E.lending_first(E.load_lf(s), p["disc_rate"])
    for k in ("cac_per_applicant", "cac", "cac_per_good_borrower", "first_loan_contribution", "ltv36", "ltv60", "y1_rev_per_borrower", "y1_cm_per_borrower"):
        add(f"lf_{s}_{k}", lo[k], inr(lo[k]), "INR per borrower (or applicant)", f"Bueno-style lending-first, {s}", MODEL + " + founder data")
    for k in ("ltv36_cac", "ltv60_cac"):
        add(f"lf_{s}_{k}", lo[k], x1(lo[k]), "ratio", f"Bueno-style lending-first, {s}", MODEL + " + founder data")
    add(f"lf_{s}_cap_per_rev", lo["capital_per_rev"], f"₹{lo['capital_per_rev']:.2f}", "INR equity per INR 1 of yr-1 revenue",
        f"lending-first through our own NBFC, {s}", MODEL)
    add(f"lf_{s}_payback", lo["payback_months"], f"{lo['payback_months']} months" if lo["payback_months"] else "never (60 months)", "months",
        f"Bueno-style lending-first, {s}", MODEL)

# ---------------------------------------------------------------- lending-first: one first loan, line by line (base)
q = E.load_lf("base")
interest, _ = E.amortised(q["lf_ticket"], q["lf_irr"], int(q["lf_tenor"]))
cof, _ = E.amortised(q["lf_ticket"], q["lf_cof"], int(q["lf_tenor"]))
parts = {
    "interest_received": interest * (1 - q["lf_dpd90_first"]),
    "paid_to_nbfc": -cof,
    "losses": -q["lf_dpd90_first"] * q["lf_ead"] * q["lf_lgd"] * q["lf_ticket"] * q["lf_risk_share"],
    "collection": -q["lf_collection"],
    "ops": -q["lf_ops_cost"],
    "platform_fee": -q["lf_platform_share"] * q["lf_platform_fee"],
}
for k, v in parts.items():
    add(f"lf_base_loan_{k}", v, inr(v), "INR per first loan", f"one Rs {q['lf_ticket']:,.0f} 3-month first loan, base", MODEL + " + founder data")
add("lf_base_loan_total", sum(parts.values()), inr(sum(parts.values())), "INR per first loan", "one first loan, base", MODEL)
approved = q["lf_applicants"] * q["lf_approval"]
add("lf_funnel_applicants", q["lf_applicants"], f"{q['lf_applicants']:,.0f}", "applicants", "Bueno-style cohort", "founder data")
add("lf_funnel_approved", approved, f"{approved:,.0f}", "borrowers", "Bueno-style cohort", "founder data (25% approved)")
add("lf_funnel_repaid", approved * (1 - q["lf_dpd90_first"]), f"{approved * (1 - q['lf_dpd90_first']):,.0f}", "borrowers", "first loan not 90+ late", "founder data")
for s in E.SCENARIOS:
    p_ = E.load_inputs(s)
    o = E.run(s)[2]
    _, lo = E.lending_first(E.load_lf(s), p_["disc_rate"])
    add(f"plan_{s}_net_per_customer", o["ltv60"] - o["cac"], inr(o["ltv60"] - o["cac"]), "INR per activated saver", f"{PLAN}, {s}: LTV60 minus CAC", MODEL)
    add(f"lf_{s}_net_per_customer", lo["ltv60"] - lo["cac"], inr(lo["ltv60"] - lo["cac"]), "INR per borrower", f"lending-first, {s}: LTV60 minus CAC", MODEL)

# ---------------------------------------------------------------- channels (base)
chs = []
for seg in E.SEGMENTS:
    p = E.load_inputs("base", segment=seg)
    cac_s, rows_s = E.blended_cac(p, E.load_channels(), seg)
    chs += rows_s
    add(f"seg_{seg}_channel_cac", cac_s, inr(cac_s), "INR per activated saver", f"blended channel CAC, {seg} half, base", MODEL)
for c in chs:
    add(f"ch_{c['channel']}_cac", c["cac"], inr(c["cac"]), "INR per activated saver", f"channel {c['label']}, base", MODEL + " Funnel & CAC")
    add(f"ch_{c['channel']}_i2a", c["install_to_active"], f"{c['install_to_active']:.0%}", "share of installs", f"channel {c['label']}, base", MODEL)

# ---------------------------------------------------------------- what has to be true (groups), plan
base, bull = E.load_inputs("base"), E.load_inputs("bull")
base_n, bull_n = E.load_inputs("base", segment="ng"), E.load_inputs("bull", segment="ng")
diff = [k for k in base if base[k] != bull[k] or base_n[k] != bull_n[k]]
G = {
    "cross_sell": [k for k in diff if k.startswith(("loan_", "card_", "unsec_", "sip_", "ins_", "gold_", "lsp_", "dlg_", "fd_", "trail_", "nbfc_", "service_", "ladder_", "secured_", "part_"))],
    "debit_cost": ["cost_debit", "cost_failed", "cost_notice"],
    "retention": ["ret_m1", "ret_m3", "ret_m6", "ret_m12", "ret_m24", "churn_late"],
    "amount": ["daily_amount", "debits_success", "amount_growth", "withdraw_rate", "leaver_withdraw", "dormant_withdraw"],
    "cac": ["cac_mult"],
    "serve": ["cost_support", "cost_tech", "cost_rewards", "cost_fraud"],
}
for g, ks in G.items():
    ks = [k for k in ks if k in diff]
    # each segment gets ITS OWN base / bull values (scenario_values sets key@gig and key@ng)
    v = E.run("bull", E.scenario_values("base", ks))[2]["ltv60_cac"]
    add(f"wtbt_all_bull_except_{g}", v, x1(v), "ratio", f"{PLAN}: every input at bull except the '{g}' group at base", MODEL)
    v1 = E.run("base", E.scenario_values("bull", ks))[2]["ltv60_cac"]
    add(f"wtbt_only_{g}_bull", v1, x1(v1), "ratio", f"{PLAN}: only the '{g}' group at bull, rest base", MODEL)

# ---------------------------------------------------------------- story deck (Outputs tab, story block)
STORY_SRC = MODEL + ", Outputs tab (story block)"
for s in E.SCENARIOS:
    p, crow, o, _ = res[s]
    st = E.story(p, crow, o)
    lo = E.lending_first(E.load_lf(s), p["disc_rate"])[1]
    for y in (1, 2):
        for slug in E.COST_LINES:
            v = st[f"y{y}_cost_{slug}"]
            add(f"story_{s}_cost_pa_y{y}_{slug}", v, inr(v), "INR per active saver per year", f"{PLAN}, {s}; cohort year {y}; cost line {slug}", STORY_SRC)
        tot = sum(st[f"y{y}_cost_{slug}"] for slug in E.COST_LINES)
        add(f"story_{s}_cost_pa_y{y}", tot, inr(tot), "INR per active saver per year", f"{PLAN}, {s}; cohort year {y}; all variable cost", STORY_SRC)
        other = tot - st[f"y{y}_cost_pay"] - st[f"y{y}_cost_service"]
        add(f"story_{s}_cost_pa_y{y}_other", other, inr(other), "INR per active saver per year",
            f"{PLAN}, {s}; cohort year {y}; loans, cards, insurance and fraud costs", STORY_SRC)
    for n in (12, 24, 60):
        v = st[f"borrow_{n}"]
        add(f"story_{s}_borrow_{n}", v, f"{v:.0%}" if v >= 0.095 else f"{v:.1%}", "share of activated savers",
            f"{PLAN}, {s}; took a first loan by month {n}", STORY_SRC)
    one_in = round(1 / st["borrow_60"])
    add(f"story_{s}_borrow_60_one_in", one_in, f"1 in {one_in}", "activated savers per first-time borrower",
        f"{PLAN}, {s}; within 60 months", STORY_SRC)
    add(f"story_{s}_cac_per_borrower", st["cac_per_borrower"], inr(st["cac_per_borrower"]), "INR per saver who ever borrows",
        f"{PLAN}, {s}; CAC per activated saver ÷ share who borrow within 60 months", STORY_SRC)
    x = st["cac_per_borrower"] / lo["cac"]
    add(f"story_{s}_borrower_cost_x_lf", x, f"{x:.0f}" if x >= 3 else f"{x:.1f}", "times",
        f"{s}; save-first CAC per saver who ever borrows ÷ lend-first CAC per borrower", STORY_SRC + " + founder data")
    for k in ("reach3", "reach5"):
        v = st[k]
        add(f"story_{s}_{k}", v, f"{v:.1%}" if v < 0.095 else f"{v:.0%}", "share of activated savers",
            f"{PLAN}, {s}; reached loan {k[-1]} on the ladder within 60 months", STORY_SRC)
    for k in ("sec_start", "sec_m12"):
        add(f"story_{s}_{k}", st[k], inr(st[k]), "INR per loan", f"{PLAN}, {s}; secured loan size ({'when loans start' if k == 'sec_start' else 'month 12'})", STORY_SRC)
        fee = st[k] * p["secured_fee"]
        add(f"story_{s}_{k}_fee", fee, inr(fee), "INR per loan", f"{PLAN}, {s}; our revenue on that secured loan at secured_fee", STORY_SRC)
    for slug in E.STORY_REV:
        v = st[f"rev60_{slug}"]
        add(f"story_{s}_rev60_{slug}", v, f"{v:.0%}", "share of 60-month revenue", f"{PLAN}, {s}; one cohort, undiscounted", STORY_SRC)

# ---------------------------------------------------------------- uncertainty: evidence centre, Monte Carlo, sensitivity, register
MCSRC = "model/mc.py over tables/distributions.csv (10,000 draws, seed 20261002), 2 Oct 2026"


def rd(name):
    return list(csv.DictReader(open(E.TABLES / name)))


def pct0(v):
    return f"{v:.0%}" if v >= 0.095 or v == 0 else f"{v:.1%}"


for r in rd("ev_centre.csv"):
    d, m, v = r["design"], r["metric"], float(r["value"])
    i = f"ev_{d}_{m}"
    if m in ("net", "ltv60", "cac", "rev_pa_y2", "cost_pa_y2", "saved_pm_y2", "sec_start", "sec_m12", "rev_per_active_year",
             "cost_per_active_year", "rev_needed_per_active_year") or m.startswith(("rev_pa_y2::", "cost_pa_y2::", "whatif_")):
        disp = inr(v)
    elif m in ("gold_per_debit", "cost_per_debit_pct", "cost_per_debit_flat"):
        disp = f"₹{v:.2f}"
    elif m == "debit_amount_gig":
        disp = inr(v)
    elif m.startswith(("still_m", "borrow_", "reach", "rev60_")):
        disp = pct0(v)
    elif m == "active_months_5y":
        disp = f"{v:.0f} months"
    elif m == "pv_active_months":
        disp = f"{v:.0f} months"
    elif m == "rev_needed_multiple":
        disp = f"{v:.0f}"
    else:
        disp = f"{v:.2f}"
    add(i, v, disp, "see metric", f"evidence centre ({d}): every input at the middle of its evidence range; {m}", MCSRC)
for r in rd("mc_summary.csv"):
    v_, m = r["variant"], r["metric"]
    if r.get("p50"):
        for q in ("p5", "p50", "p95", "mean"):
            x = float(r[q])
            disp = inr(x) if m in ("net", "ltv60", "cac", "rev_pa_y2") else (f"${x:.0f}M" if m == "y10_usd_m" else f"{x:.1f}")
            add(f"mc_{v_}_{m}_{q}", x, disp, m, f"Monte Carlo ({v_}), {q} across 10,000 draws", MCSRC)
    else:
        x = float(r["mean"])
        add(f"mc_{v_}_{m}", x, f"{round(x * 10000):,} of 10,000", "draws", f"Monte Carlo ({v_}): draws meeting {m}", MCSRC)
GROUPS = {"payment pricing": ("pay_", "fail_billed", "cost_notice"), "cost to win a saver": ("cac_target",),
          "retention": ("ret_", "churn_late"), "debits and amounts": ("debits_success", "daily_amount", "wk_success")}
for v_ in ("independent", "weekly"):
    D = [r for r in rd("mc_drivers.csv") if r["variant"] == v_]
    used = 0.0
    for g, pre in GROUPS.items():
        x = sum(float(r["variance_share"]) for r in D if r["input"].startswith(pre))
        used += x
        add(f"mc_{v_}_drv_{g.replace(' ', '_')}", x, f"{x:.0%}", "share of variance", f"Monte Carlo ({v_}): share of the spread in net value explained by {g}", MCSRC)
    add(f"mc_{v_}_drv_everything_else", 1 - used, f"{1 - used:.0%}", "share of variance", f"Monte Carlo ({v_}): all other inputs", MCSRC)
for v_ in ("independent", "correlated", "weekly"):
    import csv as _csv
    nets = [float(r["net"]) for r in _csv.DictReader(open(E.TABLES / f"mc_samples_{v_}.csv"))]
    add(f"mc_{v_}_net_max", max(nets), inr(max(nets)), "INR per saver", f"Monte Carlo ({v_}): the single best of 10,000 draws", MCSRC)
G = rd("mc_greedy.csv")
add("plan_greedy_steps", len(G), f"{len(G)}", "inputs", "founder plan: inputs moved to their best case, most helpful first, until the average saver breaks even", MCSRC)
for r in G:
    add(f"plan_greedy_{r['step']}", float(r["net_after"]), inr(float(r["net_after"])), "INR per saver", f"founder plan: net value after step {r['step']} ({r['input']})", MCSRC)
for r in rd("sens_grid.csv"):
    q = int(round(float(r["retention_percentile"]) * 100))
    add(f"grid_{r['cost_debit'].replace('.', '_')}_{q}", float(r["net"]), inr(float(r["net"])), "INR per saver",
        f"evidence centre with debit cost Rs {r['cost_debit']} and retention at its {q}th percentile", MCSRC)
for r in rd("sens_oat.csv"):
    k = r["input"].replace("@", "_")
    for c_ in ("net_at_p10", "net_at_p90"):
        add(f"oat_{k}_{c_}", float(r[c_]), inr(float(r[c_])), "INR per saver", f"evidence centre, {r['input']} at its {c_[-3:]}", MCSRC)
REG = rd("assumption_register.csv")
tri_ = [r for r in REG if r["status"] == "triangulated" and r["plan_value"] != ""]
for vd in ("plan optimistic", "plan leans optimistic", "plan within evidence", "plan cautious"):
    n_ = sum(1 for r in tri_ if r["verdict"] == vd)
    add(f"reg_{vd.replace(' ', '_')}", n_, f"{n_}", "inputs", f"triangulated inputs with a plan value where the verdict is '{vd}'", "model/register.py")
n_opt = sum(1 for r in tri_ if r["verdict"] in ("plan optimistic", "plan leans optimistic"))
add("reg_any_optimistic", n_opt, f"{n_opt}", "inputs", "triangulated inputs with a plan value where the plan is optimistic or leans optimistic", "model/register.py")
add("reg_checked", len(tri_), f"{len(tri_)}", "inputs", "triangulated inputs that have a plan value to compare", "model/register.py")
add("reg_triangulated", len([r for r in REG if r["status"] == "triangulated"]), f"{len([r for r in REG if r['status'] == 'triangulated'])}", "inputs", "inputs checked against independent sources", "model/register.py")
add("reg_provisional", len([r for r in REG if r["status"] == "provisional"]), f"{len([r for r in REG if r['status'] == 'provisional'])}", "inputs", "inputs with no independent check yet", "model/register.py")
add("reg_total", len(REG), f"{len(REG)}", "inputs", "uncertain inputs in the Monte Carlo", "model/register.py")
for r in REG:
    k = f"reg_{r['input']}_{r['segment']}"
    if r["plan_favourable_pct"] != "":
        x = float(r["plan_favourable_pct"])
        add(k + "_fav", x, f"{x:.0%}", "share", f"share of the evidence distribution the plan's {r['input']} ({r['segment']}) is more optimistic than", "model/register.py")

# ---- the flip: the daily minimum that makes one saver break even (model/flip.py)
FLIPSRC = "model/flip.py over tables/distributions.csv, 2 Oct 2026"
FLIP_ID = {("plan", "daily"): "plan", ("best_case_flat_failed_free", "daily"): "best_flat", ("best_case_percent", "daily"): "best_pct",
           ("evidence_flat_failed_free", "daily"): "ev_flat", ("evidence_flat_failed_billed", "daily"): "ev_flat_billed",
           ("evidence_percent", "daily"): "ev_pct", ("evidence_flat_failed_free", "weekly"): "ev_flat_weekly"}
for r in rd("flip_breakeven.csv"):
    fid = FLIP_ID[(r["case"], r["design"])]
    pop = f"{r['case']} ({r['design']} debits): every saver puts in exactly this amount per successful debit"
    if r["breakeven_amount"]:
        a_ = float(r["breakeven_amount"])
        add(f"flip_{fid}_amount", a_, inr(a_), "INR per debit", "smallest Rs 50 step that breaks even; " + pop, FLIPSRC)
        for g in ("gig", "ng"):
            m_ = float(r[f"monthly_{g}"])
            add(f"flip_{fid}_monthly_{g}", m_, inr(m_), "INR per month", f"break-even amount x successful debits a month ({g}); " + pop, FLIPSRC)
            sh = float(r[f"share_income_{g}"])
            add(f"flip_{fid}_income_{g}", sh, f"{sh:.0%}", "share of income",
                f"break-even monthly saving as a share of {'a full-time rider’s net income (Rs 18,761, IDinsight 2024)' if g == 'gig' else 'urban self-employed mean earnings (Rs 23,012, PLFS 2025)'}; " + pop, FLIPSRC)
        add(f"flip_{fid}_debits_gig", float(r["debits_gig"]), f"{float(r['debits_gig']):.0f}", "debits per month", "successful debits a month (gig); " + pop, FLIPSRC)
    else:
        add(f"flip_{fid}_amount", 0.0, "never", "INR per debit", "no amount up to Rs 8,000 breaks even; " + pop, FLIPSRC)
    b_ = float(r["best_net_at_or_below_1000"])
    add(f"flip_{fid}_best_upto_1000", b_, inr(b_), "INR per saver", "best net value per saver at any amount up to Rs 1,000; " + pop, FLIPSRC)
for r in rd("flip_mc.csv"):
    a_ = int(float(r["amount"]))
    add(f"flipmc_{a_}_amount", float(a_), inr(a_), "INR per debit", "daily minimum tested in the Monte Carlo by amount", FLIPSRC)
    for k in ("p_pos", "p_pos_flat", "p_pos_percent"):
        x = float(r[k])
        add(f"flipmc_{a_}_{k}", x, f"{x:.1%}" if 0 < x < 0.1 else f"{x:.0%}", "share of draws",
            f"Monte Carlo, 2,000 draws, every saver at Rs {a_} a debit: share of futures with net value > 0" + {"p_pos": "", "p_pos_flat": " (flat-fee draws)", "p_pos_percent": " (percentage-fee draws)"}[k], FLIPSRC)

# ---- cross-sell map (tables/crosssell_map.csv from research/xs_lending.csv and xs_other.csv)
EVC = {(r["design"], r["metric"]): float(r["value"]) for r in rd("ev_centre.csv")}


def V_EV(m):
    return EVC[("daily", m)]


XSSRC = "tables/crosssell_map.csv (research/xs_lending.csv, xs_other.csv), 2 Oct 2026"
XS = rd("crosssell_map.csv")
for r in XS:
    slug = re.sub(r"[^a-z0-9]+", "_", r["product"].lower()).strip("_")[:40]
    for k, col in (("low", "rs_per_active_saver_year_low"), ("mid", "mid"), ("high", "high")):
        if r[col] != "":
            x = float(r[col])
            add(f"xs_{slug}_{k}", x, inr(x) if x >= 10 or x == 0 else f"₹{x:.1f}".replace(".0", ""), "INR per active saver a year",
                f"{r['product']}: take rate x ticket x take-up ({k} case; take-up is the researchers' estimate)", XSSRC)
keep = V_EV("gold_per_debit") / V_EV("debit_amount_gig")
add("ev_keep_share", keep, f"{keep:.2%}".replace("0%", "%") if keep < 0.01 else f"{keep:.1%}", "share of each rupee saved",
    "evidence middle: gold margin on the half of each debit that goes to gold (fund and FD fees add little)", MCSRC)
gm = keep / E.load_inputs("base", segment="gig")["gold_share"]
add("ev_gold_margin", gm, f"{gm:.2%}".rstrip("0").rstrip("."), "share of gold bought", "evidence middle: our margin on gold bought (median of its evidence range)", MCSRC)
npx = sum(1 for r in XS if not r["product"].startswith("TOTAL") and "guarantee" not in r["product"])
add("xs_product_count", npx, f"{npx}", "product lines", "product lines priced in tables/crosssell_map.csv (excluding the guaranteed-loan variant)", XSSRC)
gap = V_EV("rev_needed_per_active_year") - V_EV("rev_per_active_year")
add("xs_gap", gap, inr(gap), "INR per active saver a year", "evidence middle: revenue needed per active saver-year to break even, minus revenue today (both discounted)", MCSRC)
tot = next(float(r["mid"]) for r in XS if r["product"] == "TOTAL all cross-sell")
add("xs_share_of_gap", tot / gap, f"{tot / gap:.0%}", "share", "middle-case cross-sell revenue as a share of the gap per active saver-year", XSSRC)
hi = next(float(r["high"]) for r in XS if r["product"] == "TOTAL all cross-sell")
add("xs_high_share_of_gap", hi / gap, f"{hi / gap:.0%}", "share", "every product at its best case at once, as a share of the gap", XSSRC)
for k, fee in (("hi", 15000.0), ("mid", 5500.0)):
    x = gap / fee
    add(f"xs_home_need_{k}", x, f"{x:.0%}", "share of savers a year",
        f"share of active savers who would need a home loan through the app every year to close the gap alone, at Rs {fee:,.0f} earned per loan", XSSRC)

# ---- one customer, everything sold: lifetime value and payback (model/ltv.py)
LTVSRC = "model/ltv.py: engine cohort per customer won + tables/crosssell_map.csv, 2 Oct 2026"
for r in rd("ltv_cases.csv"):
    c = r["case"]
    pop = f"one customer won ({c}): 5 years, discounted; cross-sell per active saver a year from month 1, before selling costs"
    for k in ("cac", "ltv60", "net60", "savings_pv", "cross_sell_pv", "serve_pv"):
        x = float(r[k])
        add(f"ltv_{c}_{k}", x, inr(x), "INR per customer won", f"{k}; " + pop, LTVSRC)
    x = float(r["net60"])
    add(f"ltv_{c}_loss", -x, inr(abs(x)), "INR per customer won", "loss per customer over 5 years (positive number); " + pop, LTVSRC)
    pb = r["payback_month"]
    add(f"ltv_{c}_payback", float(pb) if pb else 0.0, f"month {pb}" if pb else "never", "month",
        "first month the undiscounted running total covers the cost to win (10-year horizon); " + pop, LTVSRC)
    if pb:
        add(f"ltv_{c}_payback_years", float(pb) / 12, f"{float(pb) / 12:.1f} years", "years", "payback in years; " + pop, LTVSRC)

# ---- the redesign: shopkeepers, fund route, unsecured loans to proven savers (model/redesign.py, redesign_deck.py)
RDSRC = "model/redesign.py and redesign_deck.py over distributions.csv + redesign_distributions.csv, 2 Oct 2026"
in100 = lambda x: "over 99 in 100" if x >= 0.995 else f"{round(x * 100)} in 100"
add("rd_original_p", 0.0, "none", "share of futures", "original design: futures in which a customer pays back (0 of 10,000)", MCSRC)
VSLUG = {"loans only while saving": "base", "proven savers keep borrowing": "grad", "proven savers keep borrowing, take-up 20%": "grad_20",
         "proven savers keep borrowing, cost to win at most Rs 250": "grad_cac250", "proven savers keep borrowing, take-up 20%, cost to win at most Rs 250": "best"}
for r in rd("redesign_variants.csv"):
    k = VSLUG[r["case"]]
    x = float(r["p_net_pos"])
    add(f"rd_var_{k}_p", x, in100(x), "share of futures", f"redesign ({r['case']}): futures in which a customer pays back within 5 years, 4,000 draws", RDSRC)
    add(f"rd_var_{k}_net_p50", float(r["net_p50"]), inr(float(r["net_p50"])), "INR per customer won", f"redesign ({r['case']}): median net per customer", RDSRC)
TK = {0.05: "1 in 20", 0.1: "1 in 10", 0.2: "1 in 5", 0.3: "3 in 10"}
for r in rd("redesign_grid.csv"):
    c_, l_ = float(r["cac"]), round(float(r["loans_year"]), 2)
    x = float(r["p_net_pos"])
    add(f"rd_grid_{int(c_)}_{int(round(l_ * 100))}_p", x, in100(x), "share of futures",
        f"redesign, proven savers keep borrowing: cost to win Rs {c_:.0f}, {TK[l_]} proven savers borrowing a year; futures that pay back (2,000 draws)", RDSRC)
for c_ in (150, 250, 400, 500):
    add(f"rd_grid_cac_{c_}", float(c_), inr(c_), "INR per customer won", "cost to win a shopkeeper tested in the redesign grid", RDSRC)
for l_, t_ in TK.items():
    add(f"rd_grid_takeup_{int(round(l_ * 100))}", l_, t_, "loans a year per proven saver", "share of proven savers taking a loan each year, tested in the redesign grid", RDSRC)
D = {r["metric"]: float(r["value"]) for r in rd("redesign_deck.csv")}
for k in ("target_cac", "target_savings", "target_loans", "target_other", "target_serve", "target_net", "one_loan", "stayer_trail_5y"):
    add(f"rd_{k}", D[k], inr(D[k]), "INR", f"redesign target case ({k}): win for Rs 250, 1 in 5 proven savers borrow a year, evidence middle otherwise; 5 years discounted (one_loan and stayer_trail undiscounted)", RDSRC)
add("rd_target_payback", D["target_payback"], f"month {D['target_payback']:.0f}", "month", "redesign target case: first month the running total covers the cost to win", RDSRC)
add("rd_loan_ticket", D["loan_ticket_mid"], f"₹{D['loan_ticket_mid'] / 1e5:.1f} lakh", "INR per loan", "middle of the unsecured-loan ticket range (Rs 50,000-2.5 lakh)", RDSRC)
add("rd_loan_fee", D["loan_fee_mid"], f"{D['loan_fee_mid']:.0%}", "share of loan", "middle of the referral-fee range (1-3%)", RDSRC)
C = {r["metric"]: float(r["value"]) for r in rd("redesign_centre.csv")}
add("rd_centre_net", C["net"], inr(C["net"]), "INR per customer won", "redesign at the evidence middle, loans only while saving", RDSRC)
add("rd_centre_cac", C["cac"], inr(C["cac"]), "INR per customer won", "cost to win a shopkeeper at the evidence middle", RDSRC)
add("rd_centre_ltv", C["ltv60"], inr(C["ltv60"]), "INR per customer won", "redesign at the evidence middle: worth before the cost to win", RDSRC)
add("rd_centre_takeup", C["median_wc_loans_year"], f"about 1 in {1 / C['median_wc_loans_year']:.0f}", "loans a year per active saver", "middle of the take-up range for the unsecured loan", RDSRC)
M = {r["metric"]: float(r["value"]) for r in rd("redesign_mc.csv")}
add("rd_mc_p", M["p_net_pos"], in100(M["p_net_pos"]), "share of futures", "redesign, loans only while saving: futures that pay back (10,000 draws)", RDSRC)
DR = {r["input"]: float(r["variance_share"]) for r in rd("redesign_drivers.csv")}
add("rd_drv_cac", DR["cac_target@ng"], f"{DR['cac_target@ng']:.0%}", "share of variance", "redesign: share of the spread explained by the cost to win a shopkeeper", RDSRC)
add("rd_drv_takeup", DR["wc_loans_year"], f"{DR['wc_loans_year']:.0%}", "share of variance", "redesign: share of the spread explained by loan take-up (loans only while saving)", RDSRC)
for r in rd("redesign_distributions.csv"):
    for k in ("low", "mode", "high"):
        v = float(r[k])
        disp = (f"{v:.1%}".replace(".0%", "%") if v < 1 else (f"₹{v / 1e5:.1f} lakh" if v >= 1e5 else (f"₹{v:,.0f}" if r["input"] in ("wc_ticket", "xs_other") else f"{v:g}")))
        add(f"rdd_{r['input']}_{k}", v, disp, "see input", f"redesign input {r['input']} ({k}); {r['basis']}", "tables/redesign_distributions.csv")

# ---- the salaried redesign (model/redesign_salaried.py) and every segment on one yardstick
RSSRC = "model/redesign_salaried.py over distributions.csv, redesign_distributions.csv, rs_distributions.csv, 2 Oct 2026"
RSV = {"loans stop when they change jobs": "job", "account moves with the worker": "port", "account moves, 1 in 5 borrow a year": "port_20",
       "account moves, win via employer for Rs 250": "port_cac250", "account moves, 1 in 5 borrow, win for Rs 250": "best"}
for r in rd("rs_variants.csv"):
    k = RSV[r["case"]]
    x = float(r["p_net_pos"])
    add(f"rs_var_{k}_p", x, in100(x), "share of futures", f"salaried redesign ({r['case']}): futures in which a worker pays back within 5 years, 4,000 draws", RSSRC)
    add(f"rs_var_{k}_net_p50", float(r["net_p50"]), inr(float(r["net_p50"])), "INR per worker won", f"salaried redesign ({r['case']}): median net per worker", RSSRC)
for r in rd("rs_grid.csv"):
    c_, l_ = float(r["cac"]), round(float(r["loans_year"]), 2)
    x = float(r["p_net_pos"])
    add(f"rs_grid_{int(c_)}_{int(round(l_ * 100))}_p", x, in100(x), "share of futures",
        f"salaried redesign, account moves with the worker: cost to win Rs {c_:.0f}, {TK[l_]} borrowing a year; futures that pay back (2,000 draws)", RSSRC)
add("rs_grid_cac_100", 100.0, inr(100), "INR per worker won", "cost to win a worker tested in the salaried grid", RSSRC)
RD = {r["metric"]: float(r["value"]) for r in rd("rs_deck.csv")}
for k in ("target_cac", "target_savings", "target_loans", "target_other", "target_serve", "target_net", "target_ltv",
          "today_cac", "today_net", "today_ltv", "today_loans"):
    add(f"rs_{k}", RD[k], inr(RD[k]), "INR per worker won", f"salaried redesign ({k}): evidence middle, account moves with the worker; target = win for Rs 250 and 1 in 5 borrow a year; 5 years discounted", RSSRC)
add("rs_target_payback", RD["target_payback"], f"month {RD['target_payback']:.0f}", "month", "salaried target case: first month the running total covers the cost to win", RSSRC)
add("rs_today_payback", RD["today_payback"], f"month {RD['today_payback']:.0f}" if RD["today_payback"] else "never", "month", "salaried redesign at today's evidence: payback within 5 years", RSSRC)
add("rs_ret_m12", RD["ret_m12_mean"], f"about {RD['ret_m12_mean']:.0%}", "share", "salaried workers still saving at month 12 (mean of the evidence range: staffing exits and blue-collar tenure)", RSSRC)
add("rs_takeup_mid", RD["takeup_mid"], f"about 1 in {1 / RD['takeup_mid']:.0f}", "loans a year", "middle of the take-up range", RSSRC)
DRS = {r["input"]: float(r["variance_share"]) for r in rd("rs_drivers.csv")}
add("rs_drv_cac", DRS["cac_target@ng"], f"{DRS['cac_target@ng']:.0%}", "share of variance", "salaried redesign: share of the spread explained by the cost to win a worker", RSSRC)
for r in rd("rs_distributions.csv"):
    for k in ("low", "mode", "high"):
        v = float(r[k])
        disp = f"{v:.0%}" if v < 1 else f"₹{v / 1e5:.1f} lakh" if v >= 1e5 else f"₹{v:,.0f}"
        add(f"rsd_{r['input']}_{k}", v, disp, "see input", f"salaried input {r['input']} ({k}); {r['basis']}", "tables/rs_distributions.csv")
SEGK = {"Delivery riders": "riders", "Drivers and home-service workers": "drivers", "Shopkeepers": "shopkeepers",
        "Salaried workers via employers": "salaried", "Salaried, loans stop when they change jobs": "salaried_job"}
for r in rd("segment_value.csv"):
    k = SEGK.get(r["segment"])
    if not k:
        continue
    for t in ("10", "20"):
        x = float(r[f"max_cac_{t}"])
        add(f"seg_{k}_{t}", x, inr(x), "INR per customer won",
            f"{r['segment']}: the most we could pay to win one and break even, if {'1 in 10' if t == '10' else '1 in 5'} borrow a year (redesign, evidence middle)", "model/segment_value.py")
    add(f"seg_{k}_loan", float(r["loan_size"]), (f"₹{float(r['loan_size']) / 1e5:.1f} lakh" if float(r["loan_size"]) >= 1e5 else inr(float(r["loan_size"]))),
        "INR per loan", f"{r['segment']}: loan size used", "model/segment_value.py")

# ---- lending ourselves (model/lend_self.py)
LSRC = "model/lend_self.py: own-book lending at reported loss and running-cost rates, 2 Oct 2026"
CK = {"savers safer": "safe", "industry steady state": "normal", "industry today": "today"}
SK = {"Delivery riders": "riders", "Drivers and home-service workers": "drivers", "Shopkeepers": "shop"}
for r in rd("lend_loan.csv"):
    k = f"ln_{SK[r['segment']]}_{CK[r['case']]}"
    add(k, float(r["net"]), inr(float(r["net"])), "INR per loan", f"{r['segment']}: one loan lent ourselves, {r['case']} (net of funding, losses, running cost)", LSRC)
    add(k + "_rob", float(r["return_on_book"]), f"{float(r['return_on_book']):.1%}", "share of loan book a year", f"{r['segment']}, {r['case']}: net per loan as a share of the loan balance a year", LSRC)
    add(f"ln_{SK[r['segment']]}_ref", float(r["referral_net"]), inr(float(r["referral_net"])), "INR per loan", f"{r['segment']}: one loan referred at 2% less clawback", LSRC)
    add(f"ln_{SK[r['segment']]}_size", float(r["loan"]), (f"₹{float(r['loan']) / 1e5:g} lakh" if float(r["loan"]) >= 1e5 else inr(float(r["loan"]))), "INR per loan", f"{r['segment']}: loan size modelled", LSRC)
for r in rd("lend_customer.csv"):
    if r["mode"] != "lend" or r["cac_case"] != "evidence":
        continue
    k = f"lc_{SK[r['segment']]}_{CK[r['default']]}_{int(round(float(r['takeup']) * 100))}"
    add(k, float(r["net"]), inr(float(r["net"])), "INR per customer won",
        f"{r['segment']}, lending ourselves, {r['default']}, {float(r['takeup']):.0%} of proven savers borrowing a year, today's cost to win; 5 years discounted", LSRC)
    add(k + "_pb", float(r["payback"]) if r["payback"] else 0.0, f"month {r['payback']}" if r["payback"] else "never", "month", "payback month (5-year horizon); " + k, LSRC)
for t in (10, 20, 35, 50):
    add(f"lc_takeup_{t}", t / 100, {10: "1 in 10", 20: "1 in 5", 35: "35%", 50: "half"}[t], "share of proven savers borrowing a year", "borrowing level tested", LSRC)
for c_, cr_, rn_ in (("safe", 0.03, 0.03), ("normal", 0.06, 0.05), ("today", 0.09, 0.08)):
    add(f"lend_credit_{c_}", cr_, f"{cr_:.0%}", "share of loan book a year", f"bad-loan losses a year assumed in the '{c_}' case", LSRC)
    add(f"lend_running_{c_}", rn_, f"{rn_:.0%}", "share of loan book a year", f"running cost a year (excluding winning customers) in the '{c_}' case", LSRC)
LT = {r["case"]: r for r in rd("lend_target.csv")}
for c, r in LT.items():
    for f in ("cac", "savings", "loans", "other", "serve", "net"):
        add(f"lt_{CK[c]}_{f}", float(r[f]), inr(float(r[f])), "INR per shopkeeper won", f"one shopkeeper, lending ourselves, {c}, 1 in 5 borrowing a year: {f}; 5 years discounted", LSRC)
    add(f"lt_{CK[c]}_pb", float(r["payback"]) if r["payback"] else 0.0, f"month {r['payback']}" if r["payback"] else "never", "month", f"one shopkeeper, {c}: payback month", LSRC)
for r in rd("lend_scale.csv"):
    for cr in (3, 5, 8):
        v = r[f"customers_a_year_for_{cr}cr"]
        if v != "":
            x = float(v)
            disp = f"about {x / 1e5:.1f} lakh" if x >= 1e5 else f"about {round(x, -3):,.0f}"
            add(f"sc_{SK[r['segment']]}_{CK[r['case']]}_{int(round(float(r['takeup']) * 100))}_{cr}", x, disp, "customers a year",
                f"{r['segment']}, {r['case']}, {float(r['takeup']):.0%} borrowing: customers won a year to cover an NBFC fixed cost of Rs {cr} crore", LSRC)

# ---- lending Monte Carlo, funnel and prize (model/lend_mc.py, lend_self.py)
LMSRC = "model/lend_mc.py: 10,000 futures per customer group, every input from its evidence range, 2 Oct 2026"
SGK = {"shopkeepers": "shop", "drivers": "drivers", "salaried": "sal"}
for r in rd("lmc_summary.csv"):
    k = SGK[r["segment"]]
    for f_, lab in (("p_pays_back", ""), ("p_payback_le_24", "_2y"), ("p_pays_back_if_losses_le_4pct", "_low"), ("p_pays_back_if_losses_ge_7pct", "_high")):
        x = float(r[f_])
        add(f"lmc_{k}_p{lab}", x, in100(x), "share of futures", f"{r['segment']}: {f_} (lending ourselves, Monte Carlo)", LMSRC)
    for q in ("p5", "p50", "p95"):
        add(f"lmc_{k}_{q}", float(r[q]), inr(float(r[q])), "INR per customer won", f"{r['segment']}: {q} of value per customer won (5 years, discounted)", LMSRC)
    for cac in (100, 250, 500):
        if r.get(f"p_pays_back_cac_{cac}", "") != "":
            x = float(r[f"p_pays_back_cac_{cac}"])
            add(f"lmc_{k}_cac{cac}_p", x, in100(x), "share of futures", f"{r['segment']}: futures that pay back with the cost to win fixed at Rs {cac}", LMSRC)
            add(f"lmc_cac_{cac}", float(cac), inr(cac), "INR per customer won", "cost to win tested at a fixed value", LMSRC)
DRL = {"cac_target@ng": "cost to win", "cac_target@gig": "cost to win", "takeup": "how many borrow", "rate": "the rate we charge",
       "credit_cost": "losses", "running_cost": "running cost", "loan_size": "loan size", "ret_m12@ng": "how long they save", "ret_m12@gig": "how long they save",
       "cost_of_funds": "what we pay to borrow", "fee": "processing fee", "xs_other": "other products"}
for r in rd("lmc_drivers.csv"):
    k = SGK[r["segment"]]
    own = "@gig" if r["segment"] == "drivers" else "@ng"
    if "@" in r["input"] and not r["input"].endswith(own):
        continue
    if r["input"] in DRL:
        x = float(r["variance_share"])
        nm = DRL[r["input"]].replace(" ", "_")
        add(f"lmd_{k}_{nm}", x, f"{x:.0%}", "share of the spread", f"{r['segment']}: share of the spread in value per customer explained by {DRL[r['input']]}", LMSRC)
for r in rd("lmc_distributions.csv"):
    for f_ in ("low", "mode", "high"):
        v = float(r[f_])
        disp = f"{v:.1%}".replace(".0%", "%") if v < 1 else (f"₹{v / 1e5:g} lakh" if v >= 1e5 else inr(v))
        add(f"lmi_{r['input']}_{f_}", v, disp, "see input", f"lending Monte Carlo input {r['input']} ({f_}); {r['basis']}", "tables/lmc_distributions.csv")
for k_, v_, d_ in (("pl_cac", 500.0, "₹500"), ("pl_rate", 0.26, "26%"), ("pl_losses", 0.04, "4%")):
    add(k_, v_, d_, "pass line", f"pilot pass line: {k_}", LSRC)
add("pz_5_share", 500000 / 5.36e7, "about 1%", "share a year", "5 lakh shopkeepers as a share of the 5.36 crore micro enterprises on Udyam", LSRC)
LSS = {"savers safer": "safe", "industry steady state": "normal", "industry today": "today"}
for r in rd("lend_salaried.csv"):
    k = f"ls_{'ev' if r['cac_case'] == 'evidence' else 'c250'}_{LSS[r['case']]}_{int(round(float(r['rate']) * 100))}"
    add(k, float(r["net"]), inr(float(r["net"])), "INR per salaried worker won",
        f"salaried worker via employer: {r['case']}, rate {float(r['rate']):.0%}, 1 in 5 borrowing, cost to win {r['cac_case']}; 5 years discounted", LSRC)
for rt in (22, 24, 26, 28):
    add(f"ls_rate_{rt}", rt / 100, f"{rt}%", "interest a year", "rate tested for salaried loans", LSRC)
BESRC = "break-even search, one number at a time, others at today's evidence (shopkeepers, normal losses), 3 Oct 2026"
def _fmt_be(k, v):
    if k == "cost_to_win":
        return inr(v)
    return (f"{v:.1%}".replace(".0%", "%")) if k in ("rate", "losses") else f"{v:.0%}"
for r in rd("lend_breakeven.csv"):
    k = r["number"]
    if k == "today":
        continue
    for f_, lab in (("today", "today"), ("breakeven", ""), ("range_low", "lo"), ("range_high", "hi")):
        v = float(r[f_])
        add(f"be_{k}" + (f"_{lab}" if lab else ""), v, _fmt_be(k, v), "see number", f"shopkeepers: {k} {f_}", BESRC)
    for f_, lab in (("value_at_low", "lo_val"), ("value_at_high", "hi_val")):
        v = float(r[f_])
        add(f"be_{k}_{lab}", v, inr(v), "INR per shopkeeper won", f"shopkeepers: value with {k} at the {lab.split('_')[0]} end of its range, others at today's evidence", BESRC)
FN = rd("lend_funnel.csv")
add("fn_m6", float(FN[0]["saving_m6"]), f"{float(FN[0]['saving_m6']):.0f}", "of 100 won", "shopkeepers still saving at 6 months, of 100 won (evidence middle)", LSRC)
add("fn_m12", float(FN[0]["saving_m12"]), f"{float(FN[0]['saving_m12']):.0f}", "of 100 won", "shopkeepers still saving at 12 months, of 100 won", LSRC)
for r in FN:
    t = int(round(float(r["takeup"]) * 100))
    add(f"fn_loans_{t}", float(r["loans_5y_per_100"]), f"{float(r['loans_5y_per_100']):.0f}", "loans per 100 won", f"loans over five years per 100 shopkeepers won, {t}% of proven savers borrowing a year", LSRC)
for r in rd("lend_prize.csv"):
    n_ = int(float(r["won_a_year"]))
    k = {100000: "1", 500000: "5", 1000000: "10"}[n_]
    add(f"pz_{k}_won", float(n_), f"{n_ / 1e5:g} lakh", "shopkeepers a year", "illustrative scale: shopkeepers won a year", LSRC)
    for f_, lab in (("lent_a_year_cr", "lent"), ("avg_book_cr", "book"), ("equity_own_book_cr", "eq_own"), ("equity_colend_cr", "eq_co"),
                    ("value_a_year_median_cr", "val_med"), ("value_a_year_savers_safer_cr", "val_safe")):
        x = float(r[f_])
        add(f"pz_{k}_{lab}", x, ("−" if x < 0 else "") + f"₹{abs(x):,.0f} crore", "INR crore", f"at {n_:,} shopkeepers won a year: {f_} (1 in 5 borrowing; value after an NBFC fixed cost of Rs 5 crore)", LSRC)

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "value", "display", "unit", "population", "source"])
    w.writeheader()
    w.writerows(rows)
print(f"wrote {len(rows)} numbers to {OUT}")

"""Independent rebuild of ONE online saver's LTV/CAC (Agent A, "recalculate", 23 Oct 2026).

Does NOT import the model. Input VALUES are read from others/tables/ltv_inputs.csv (the workbook's input table); the founders'
switches that live only in code are restated here with the file:line they come from. The MECHANICS are re-derived from the
engine's docstring (cohort_engine.py:19-71) and the deck's appendix A11, written fresh, month by month, for a saver who
joins in business month 1 (the deck's saver).

Run from the repo root:  ~/.cortado-venv311/bin/python others/reviews/2026-10-23_ltv_cac_check/recalc.py
Writes recalc_reconcile.csv, recalc_findings.csv, recalc_affordability.csv, recalc_monthly.csv next to this file.
"""
import csv
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                       # .../savings-first-deck
TAB = REPO / "others" / "tables"
N = 96                                       # months 1..96; the 5-year view uses the first 60

# ---------------------------------------------------------------- inputs: values from the table, switches from the code
V = {r["key"]: float(r["value"]) for r in csv.DictReader((TAB / "ltv_inputs.csv").open()) if r["value"] not in ("", None)}
V.update({"sip_takeup": 0.0})   # online_plan.py:73: the extra equity SIP is off in the 80/20 base (the table still shows 10%)

# The founders' numbers (brief; final/3_LTV_CAC_one_saver.pdf p3, p11, p12; tables/online_unit.csv, online_loan_funnel.csv)
TARGET = {"Cost to win": -495, "Fund trail": 531, "Personal + business loans": 2802, "Gold": 73, "Property (LAP)": 561,
          "Home": 225, "Durables": 13, "Vehicles": 13, "Other lenders' loans": 884, "Cards": 18,
          "Recharge, bills, FD, NPS": 78, "Insurance": 0, "Serving": -501, "LTV (revenue less serving)": 3813,
          "LTV/CAC": 7.70, "Payback month": 12}
REV_LINES = ("Fund trail", "Personal + business loans", "Other lenders' loans", "Cards", "Recharge, bills, FD, NPS", "Insurance")


def P(**over):
    x = dict(V)
    x.update(over)
    return x


def curve(x, r3, r12, a):
    """Share still saving (or still reachable) at the START of each month: s(1) = 1, s(4) = r3, s(13) = r12, then churn_late."""
    h = np.where(a <= 3, 1 - r3 ** (1 / 3), np.where(a <= 12, 1 - (r12 / r3) ** (1 / 9), x["churn_late"]))
    s = np.ones(a.size)
    for i in range(1, a.size):
        s[i] = s[i - 1] * (1 - h[i - 1])
    return s


def pb_loans(x, q, hz, appr1, persistent=False):
    """Personal + business loans for one population on the reach curve q (share of that population still reachable).
    States: never borrowed (n0), repaid and free (e), repaying (out of the pool for the tenure). Returns first, repeat, top-ups
    as shares of that population, and applications."""
    T = int(round(x["tenure"]))
    first, rep, apps, e = (np.zeros(N) for _ in range(4))
    if persistent:      # each user has a fixed score u; approved first time iff u < the month's approval bar
        U = (np.arange(4000) + 0.5) / 4000
        n0u = np.ones(U.size)                      # never borrowed, as a share of those still reachable, by score
    n0 = 1.0                                       # never borrowed, as a share of the population
    for i in range(N):
        if persistent:
            fu = n0u * hz[i] * (U < appr1[i])
            first[i] = q[i] * fu.mean()
            n0 = q[i] * n0u.mean()
        else:
            first[i] = n0 * hz[i] * x["eligible"] * appr1[i]
        rep[i] = e[i] * hz[i] * x["eligible"] * x["approved_repeat"]
        apps[i] = (n0 + e[i]) * hz[i]
        if i + 1 < N:
            sig = q[i + 1] / q[i]
            if persistent:
                n0u = n0u - fu
            else:
                n0 = (n0 - first[i]) * sig
            j = i - T                               # a loan made in month j+1 is free again in month j+T+2
            back = (first[j] + rep[j]) * q[i + 1] / q[j] if j >= 0 else 0.0
            e[i + 1] = (e[i] - rep[i]) * sig + back
    loans = first + rep
    u = 1 - (1 - x["topup_share"]) ** (1 / 12)
    lag = int(x["topup_lag"])
    top = np.zeros(N)
    for i in range(N):                              # survivors of a loan made in month L, from L+13 to L+T-1, at most one each
        for L in range(max(0, i - T + 1), i - lag + 1):
            top[i] += loans[L] * q[i] / q[L] * (1 - u) ** (i - L - lag) * u
    return first, rep, top, apps


def saver(x, cohort=1, nonsaver=None, persistent=False, repeat_paid=True, lag=0, gst_inclusive=False):
    """Revenue and serving per online saver won, months 1..N.

    cohort: business month the saver joins (1 = the deck's saver); drives the yearly growth factors and the payout ramp.
    nonsaver: None = the non-savers stay reachable on the SAVER's curve (the plan); a (r3, r12) pair = their own curve;
              an array = their reachable share by month.
    persistent: a user a lender rejects stays rejected (approval belongs to the person, not a fresh draw each month).
    repeat_paid: False = no payout on repeat loans and top-ups.
    lag: months from earning a fee to the cash (the company model uses 2).
    gst_inclusive: every quoted payout and trail includes 18% GST (our revenue = quote / 1.18).
    """
    a = np.arange(1, N + 1)
    cal = cohort + a - 1
    year = np.minimum((cal - 1) // 12 + 1, x["year_cap"])
    early = a <= x["early_months"]
    reach = x["reach_on"]
    s = curve(x, x["r3_on"], x["r12_on"], a)
    if nonsaver is None:
        ns = s
    elif isinstance(nonsaver, tuple):
        ns = curve(x, nonsaver[0], nonsaver[1], a)
    else:
        ns = np.asarray(nonsaver, dtype=float)
    pops = ((s, 1.0), (ns, reach - 1.0))            # the saver, and the other KYC'd users who came with them
    reach_curve = s + ns * (reach - 1.0)

    tf = np.minimum(x["takeup_cap"], np.where(early, x["early_takeup_mult"], 1.0) * (1 + x["takeup_growth"]) ** (year - 1))
    ea = np.where(early, x["early_approval_mult"], 1.0)
    ag = (1 + x["approval_growth"]) ** (year - 1)
    appr1 = np.minimum(x["approval_cap"], x["approved_first"] * ea * ag)
    o = {"still saving": s, "reach curve": reach_curve}

    # ---- the fund
    eq = x["eq_share"]
    trail = eq * x["eq_trail"] + (1 - eq) * x["debt_trail"]
    rm = (1 + eq * x["eq_return"] + (1 - eq) * x["debt_return"]) ** (1 / 12) - 1
    dep = x["daily"] * x["days"] * (1 + x["amount_growth"]) ** ((a - 1) // x["term"])
    start, avg = 0.0, np.zeros(N)
    for i in range(N):
        kept = start * (1 - x["withdraw_m"])
        avg[i] = kept + dep[i] / 2
        start = kept + dep[i] + avg[i] * rm
    o["balance"] = avg
    o["Fund trail"] = s * avg * trail / 12

    # ---- personal + business loans
    hz = (1 - (1 - x["loan_apply"] * x["mix_pb"]) ** (1 / 12)) * tf
    T = int(round(x["tenure"]))
    rep_ticket = min(x["ticket_cap"], x["ticket"] * (1 + x["ticket_growth"]) ** (T / 12))
    top_amt = x["topup_size"] * x["ticket"] * (1 + x["ticket_growth"])
    ramp = 1 + (x["fee_mult_end"] - 1) * np.minimum(cal - 1, 59) / 59
    pay = x["fee"] * ramp * (1 - x["taken_back"])
    f_, r_, t_, ap_ = (np.zeros(N) for _ in range(4))
    for curve_, w in pops:
        f1, r1, t1, a1 = pb_loans(x, curve_, hz, appr1, persistent)
        f_, r_, t_, ap_ = f_ + w * f1, r_ + w * r1, t_ + w * t1, ap_ + w * a1
    lent = f_ * x["ticket"] + r_ * rep_ticket + t_ * top_amt
    o.update({"P+B first (count)": f_, "P+B repeat (count)": r_, "P+B top-ups (count)": t_, "P+B applications": ap_,
              "P+B lent": lent, "ramp": ramp})
    o["P+B first loans"] = f_ * x["ticket"] * pay
    o["P+B repeat loans"] = r_ * rep_ticket * pay
    o["P+B top-ups"] = t_ * top_amt * pay
    o["Personal + business loans"] = o["P+B first loans"] + (o["P+B repeat loans"] + o["P+B top-ups"] if repeat_paid else 0.0)

    # ---- one-off referrals: a monthly chance among users who never took one; once taken, out of that product's pool
    def once(takeup_year, ticket, comm, on, approval=None):
        H = (1 - (1 - takeup_year) ** (1 / 12)) * tf
        if approval is not None:
            H = H * np.minimum(x["approval_cap"], approval * ea * ag)
        never = np.r_[1.0, np.cumprod(1 - H[:-1])]
        buys = on * never * H
        return buys, buys * ticket * comm

    o["gold (count)"], o["Gold"] = once(x["loan_apply"] * x["mix_gold"] * x["gold_approval"], x["loan_gold_ticket"], x["loan_gold_comm"], reach_curve)
    o["LAP (count)"], o["Property (LAP)"] = once(x["loan_apply"] * x["mix_lap"], x["loan_lap_ticket"], x["loan_lap_comm"], reach_curve, x["loan_lap_approval"])
    o["home (count)"], o["Home"] = once(x["loan_apply"] * x["mix_home"], x["loan_home_ticket"], x["loan_home_comm"], reach_curve, x["loan_home_approval"])
    o["durables (count)"], o["Durables"] = once(x["loan_cd_takeup"], x["loan_cd_ticket"], x["loan_cd_comm"], s)
    o["vehicles (count)"], o["Vehicles"] = once(x["loan_vehicle_takeup"], x["loan_vehicle_ticket"], x["loan_vehicle_comm"], s)
    o["Other lenders' loans"] = o["Gold"] + o["Property (LAP)"] + o["Home"] + o["Durables"] + o["Vehicles"]

    # ---- cards: 3% of savers, months 1-6 at the early factors; what those factors held back is issued in months 7-12
    cards = np.zeros(N)
    cards[:6] = (s * x["card_share"] / 6 * tf * np.minimum(x["takeup_cap"], ea * ag))[:6]
    held = max(0.0, 1 - float(np.mean((np.where(early, x["early_takeup_mult"], 1) * ea)[:6])))
    cg = np.minimum(x["takeup_cap"], (1 + x["takeup_growth"]) ** (year - 1)) * np.minimum(x["takeup_cap"], ag)
    cards[6:12] = (s * x["card_share"] * held / 6 * cg)[6:12]
    o["Cards"] = cards * x["card_fee"]

    # ---- everyday products, savers only
    _, nps = once(x["nps_takeup"], x["nps_ticket"], x["nps_comm"], s)
    _, fd = once(x["fd_takeup"], x["fd_ticket"], x["fd_comm"], s)

    def habit(takeup_year, per_year):
        H = (1 - (1 - takeup_year) ** (1 / 12)) * tf
        never = np.r_[1.0, np.cumprod(1 - H[:-1])]
        return s * np.cumsum(never * H) * per_year / 12      # holders renew 100% while saving

    o["Recharge, bills, FD, NPS"] = nps + fd + habit(x["recharge_takeup"], x["recharge_ticket"] * x["recharge_comm"]) \
        + habit(x["bills_takeup"], x["bills_ticket"] * x["bills_comm"])
    o["Insurance"] = np.zeros(N)                                # a fixed referral fee, to be agreed: 0 (founders' decision)

    # ---- serving
    o["Serving"] = -(s * (x["support_cost"] + x["debit_cost"] * x["debits_month"]) + reach_curve * x["tech"])

    rev = sum(o[k] for k in REV_LINES)
    if gst_inclusive:
        rev = rev / 1.18
    if lag:
        rev = np.r_[np.zeros(lag), rev[:-lag]]
    o["Revenue"] = rev
    o["Net"] = rev + o["Serving"]
    return o


def summarise(o, x=None, cac_pre=None, serve_mult=1.0, extra=None, months=60):
    x = x or V
    cac = (x["cac_on"] if cac_pre is None else cac_pre) * (1 + x["contingency"])
    net = o["Revenue"] + o["Serving"] * serve_mult - (0.0 if extra is None else extra)
    cum = np.cumsum(net)
    pay = int(np.argmax(cum >= cac)) + 1 if (cum >= cac).any() else None
    return {"cac": cac, "ltv60": float(cum[months - 1]), "x60": float(cum[months - 1] / cac), "x96": float(cum[-1] / cac), "payback": pay}


def emi(p, rate, n):
    r = rate / 12
    return p * r / (1 - (1 + r) ** -n)


def max_loan(e_, rate, n):
    r = rate / 12
    return e_ * (1 - (1 + r) ** -n) / r


def write(name, rows):
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with (HERE / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def main():
    base = saver(P())
    S = summarise(base)
    m = slice(0, 60)

    # ---------------------------------------------------------- 1. reconciliation
    mine = {"Cost to win": -S["cac"]}
    for k in ("Fund trail", "Personal + business loans", "Gold", "Property (LAP)", "Home", "Durables", "Vehicles",
              "Other lenders' loans", "Cards", "Recharge, bills, FD, NPS", "Insurance", "Serving"):
        mine[k] = float(base[k][m].sum())
    mine.update({"LTV (revenue less serving)": S["ltv60"], "LTV/CAC": S["x60"], "Payback month": S["payback"]})
    rows = []
    for k, t in TARGET.items():
        v = mine[k]
        if k == "Payback month":
            ok, gap = v == t, f"{v - t:+d} months"
        elif t == 0:
            ok, gap = abs(v) < 0.5, f"{v:+.2f} Rs"
        else:
            g = (round(v, 2 if k == "LTV/CAC" else 0) - t) / abs(t)
            ok, gap = abs(g) <= 0.01, f"{g:+.2%}"
        rows.append({"line": k, "founders": t, "recalc": round(v, 2), "gap (rounded recalc vs founders)": gap, "within 1%": "yes" if ok else "NO"})
    write("recalc_reconcile.csv", rows)
    print("== Reconciliation (one online saver won, months 1-60, Rs)")
    for r in rows:
        print(f"  {r['line']:<28} founders {r['founders']:>8}  recalc {r['recalc']:>10.2f}  {r['gap (rounded recalc vs founders)']:>10}  {r['within 1%']}")
    print(f"  8 years: LTV/CAC {S['x96']:.2f} (deck 12.16); revenue 96m {float(base['Revenue'].sum()):,.0f} (deck 6,642)")

    # ---------------------------------------------------------- underneath
    rev60 = float(base["Revenue"][m].sum())
    lent = float(base["P+B lent"][m].sum())
    nf, nr, nt = (float(base[k][m].sum()) for k in ("P+B first (count)", "P+B repeat (count)", "P+B top-ups (count)"))
    napps = float(base["P+B applications"][m].sum())
    w_ramp = float((base["P+B lent"] * base["ramp"])[m].sum() / lent)
    sm = float(base["still saving"][m].sum())
    loans_line = mine["Personal + business loans"] + mine["Other lenders' loans"]
    ns_gross = 1.5 / 2.5 * (mine["Personal + business loans"] + mine["Gold"] + mine["Property (LAP)"] + mine["Home"])
    print("\n== Underneath the plan")
    print(f"  saver-months in 5 years {sm:.2f}; serving at full strength Rs {V['support_cost'] + V['tech'] * 2.5 + V['debit_cost'] * V['debits_month']:.2f} a month")
    print(f"  revenue 60m {rev60:,.0f}; loans {loans_line:,.0f} = {loans_line / rev60:.1%}; all but the fund {(rev60 - mine['Fund trail']) / rev60:.1%}")
    print(f"  P+B per 100 savers won: {100 * nf:.1f} first + {100 * nr:.1f} repeat + {100 * nt:.1f} top-ups; {100 * napps:.1f} applications")
    print(f"  P+B lent per saver won Rs {lent:,.0f}; payout ramp weighted by money {w_ramp:.3f}x -> average payout {0.02 * w_ramp * 0.975:.2%}")
    print(f"  P+B revenue split: first {float(base['P+B first loans'][m].sum()):,.0f}, repeat {float(base['P+B repeat loans'][m].sum()):,.0f}, "
          f"top-ups {float(base['P+B top-ups'][m].sum()):,.0f}")
    print(f"  loans from the 1.5 non-savers: Rs {ns_gross:,.0f} gross, Rs {ns_gross - 1.5 * V['tech'] * sm:,.0f} after their tech "
          f"= {(ns_gross - 1.5 * V['tech'] * sm) / S['ltv60']:.0%} of LTV")
    print(f"  LAP + home: Rs {mine['Property (LAP)'] + mine['Home']:,.0f} = {(mine['Property (LAP)'] + mine['Home']) / rev60:.1%} of revenue; "
          f"LAP loans per 100 savers {100 * float(base['LAP (count)'][m].sum()):.2f}, home {100 * float(base['home (count)'][m].sum()):.2f}")
    cac = S["cac"]
    print(f"  cost to win as a share of money lent (P+B + LAP + home + gold): {cac / (lent + float((base['LAP (count)'] * 2.5e6 + base['home (count)'] * 3e6 + base['gold (count)'] * 1e5)[m].sum())):.2%}"
          f"; of P+B money lent {cac / lent:.2%}")
    a = np.arange(1, 61)
    yr = np.minimum((a - 1) // 12 + 1, 5)
    ap = np.minimum(0.8, 0.3 * np.where(a <= 6, 0.6, 1.0) * 1.1 ** (yr - 1))
    tfa = np.minimum(2, np.where(a <= 6, 0.5, 1.0) * 1.05 ** (yr - 1))
    print("  first-loan approval in month 12/24/36/48/60: " + ", ".join(f"{float(ap[k - 1]):.1%}" for k in (12, 24, 36, 48, 60))
          + "; apply rate a year: " + ", ".join(f"{1 - (1 - (1 - 0.65 ** (1 / 12)) * float(tfa[k - 1])) ** 12:.1%}" for k in (12, 24, 36, 48, 60)))

    # ---------------------------------------------------------- 2. findings, one change at a time
    F = []

    def add(fid, what, kind, o=None, x=None, cac_pre=None, serve_mult=1.0, extra=None, where=""):
        r = summarise(base if o is None else o, x, cac_pre, serve_mult, extra)
        F.append({"id": fid, "finding": what, "kind": kind, "where": where, "LTV 60m Rs": round(r["ltv60"]),
                  "cost to win Rs": round(r["cac"]), "LTV/CAC 60m": round(r["x60"], 2), "effect (x)": round(r["x60"] - S["x60"], 2),
                  "LTV/CAC 96m": round(r["x96"], 2), "payback month": r["payback"] or "never"})

    a96 = np.arange(1, N + 1)
    sv = base["still saving"]
    ns_support = sv * 1.5 * V["support_cost"]
    app_curve = curve(V, 0.52, 0.2415, a96)
    three = np.where(a96 <= 3, 1.0, 1e-12)          # reachable months 1-3, then (as good as) gone

    add("F0", "The plan, rebuilt", "-")
    add("F1a", "The first real cohort joins at launch (business month 4) at the seed's Rs 600 to win", "inconsistency",
        saver(P(), cohort=4), cac_pre=600.0, where="online_plan.py:49,52 vs :332 (row 0 = a month-1 joiner) and :346 (Rs 450)")
    add("F1b", "A saver won after the seed (month 19) at Rs 450", "inconsistency (cuts the other way)", saver(P(), cohort=19),
        where="same; the payout ramp and the yearly growth have moved on by month 19")
    add("F2", "Serving carries the plan's 10% contingency, as the cost to win does", "inconsistency", serve_mult=1.1,
        where="online_plan.py:236 (company: 10% on support, tech, debits) vs :340,:346 (LTV: cost to win only)")
    add("F3", "Fees arrive 2 months after they are earned", "judgement (timing)", saver(P(), lag=2),
        where="online_plan.py:56,246 (company cash) vs :338 (LTV books on disbursal)")
    add("F4", "Every quoted payout and trail includes 18% GST", "judgement (basis)", saver(P(), gst_inclusive=True),
        where="deck p2 'Fees are quoted before GST and TDS'; no lender or fund-house letter in the folder")
    add("F5a", "Non-savers stay reachable on the savings-app curve (52% at month 3, 24% at 12), not the savers' 80%/38%", "judgement",
        saver(P(), nonsaver=(0.52, 0.2415)), where="online_plan.py:132-136, 205, 339")
    add("F5b", "Non-savers reachable for their first 3 months only", "judgement (severe)", saver(P(), nonsaver=three),
        where="same")
    add("F5c", "Offers to savers only (reach 1)", "the founders' own lever", saver(P(reach_on=1.0)), where="deck p9: 3.5x")
    add("F6", "Support for non-savers: Rs 5 a month each while reachable", "missing cost", extra=ns_support,
        where="online_plan.py:340 (support per saver still saving only)")
    add("F7", "A user a lender rejects stays rejected (approval is the person's, not a fresh 30% draw each month)",
        "hidden assumption", saver(P(), persistent=True), where="cohort_engine.py:476-487")
    add("F8", "No payout on repeat loans and top-ups (the lender already has the borrower)", "judgement",
        saver(P(), repeat_paid=False), where="cohort_engine.py:520-523, 560")
    add("F9a", "Clawbacks 5% of payouts (top of the plan's range)", "judgement", saver(P(taken_back=0.05)), where="ltv_inputs taken_back")
    add("F9b", "Clawbacks 10% of payouts", "judgement", saver(P(taken_back=0.10)), where="XL-47: taken back if closed or bad within 6 months")
    add("F10a", "Take-up does not rise 5% a business year", "hidden assumption", saver(P(takeup_growth=0.0)), where="cohort_engine.py:447-449")
    add("F10b", "Approvals do not rise 10% a business year", "hidden assumption", saver(P(approval_growth=0.0)), where="cohort_engine.py:448-450")
    add("F10c", "Both flat: 35% apply and 30% approved, as the summary states them", "hidden assumption",
        saver(P(takeup_growth=0.0, approval_growth=0.0)), where="same")
    add("F11", "The payout stays at 2% (no rise to 3%)", "judgement (no source for the rise)", saver(P(fee_mult_end=1.0)),
        where="online_plan.py:331; audit: 'the rise to 3% has no source'")
    add("F12", "Rs 450 comes from better conversion (1 in 3.75 save), so reach is 1.875 not 2.5", "inconsistency (linked inputs)",
        saver(P(reach_on=1.875)), where="deck p5: Rs 450 needs Rs 70 a sign-up OR 1 in 3.75 saving; online_plan.py:135")
    # an illustrative bundle of missing variable costs (my assumptions, not evidence)
    nloans = base["P+B first (count)"] + base["P+B repeat (count)"] + base["P+B top-ups (count)"] + base["gold (count)"] \
        + base["LAP (count)"] + base["home (count)"]
    rekyc = np.zeros(N)
    rekyc[24] = 20.0 * float(base["reach curve"][24])
    bundle = 250.0 * nloans + 30.0 * base["P+B applications"] + rekyc + ns_support
    add("F13", "Missing variable costs (my illustration): Rs 250 a loan (grievances, KFS, disputes, fraud checks), Rs 30 an "
        "application (bureau, consent), a Rs 20 e-KYC re-check at year 2, Rs 5 support for non-savers", "missing cost",
        extra=bundle, where="none of these is in online_plan.py:338-342")
    comb = saver(P(takeup_growth=0.0, approval_growth=0.0), lag=2, nonsaver=(0.52, 0.2415))
    add("F14", "A careful investor's view, no input changed: F2 + F3 + F5a + F6 + F10c", "combination", comb, serve_mult=1.1,
        extra=app_curve * 1.5 * V["support_cost"], where="-")
    comb2 = saver(P(takeup_growth=0.0, approval_growth=0.0), lag=2, nonsaver=(0.52, 0.2415), persistent=True)
    add("F15", "F14 + rejected users stay rejected (F7)", "combination", comb2, serve_mult=1.1,
        extra=app_curve * 1.5 * V["support_cost"], where="-")
    flat = saver(P(takeup_growth=0.0, approval_growth=0.0, fee_mult_end=1.0))
    add("F16a", "No unsourced rises: payout flat at 2%, take-up and approvals flat (the cohort then no longer matters)",
        "hidden assumption + judgement", flat, where="F10c + F11")
    add("F16b", "F16a for a seed-era saver at the seed's Rs 600 to win", "combination", flat, cac_pre=600.0, where="F16a + F1a")
    # loan sizes tested against the folder's own income evidence (a test of arithmetic, not a different choice)
    inc, foir = 30000.0, 0.5
    pb_cap = round(max_loan(inc * foir, 0.24, 18), -3)
    home_cap = round(max_loan(inc * foir, 0.10, 240), -4)
    lap_cap = round(max_loan(inc * foir, 0.14, 180), -4)
    add("F17a", f"Personal + business loans sized to what Rs 30,000 a month repays in 18 months (FOIR 50%, 24%): Rs {pb_cap:,.0f}",
        "affordability test", saver(P(ticket=pb_cap)), where="IV-04 typical customer Rs 20-40k; REG-077")
    add("F17b", f"... and home Rs {home_cap:,.0f} (20 yrs, 10%), property Rs {lap_cap:,.0f} (15 yrs, 14%) on the same income",
        "affordability test", saver(P(ticket=pb_cap, loan_home_ticket=home_cap, loan_lap_ticket=lap_cap)), where="same")
    write("recalc_findings.csv", F)
    bal = base["balance"]
    print(f"\n  balance per saver still saving: month 24 Rs {float(bal[23]):,.0f}, month 60 Rs {float(bal[59]):,.0f}; "
          f"deposits per saver won over 5 yrs Rs {float((base['still saving'] * V['daily'] * V['days'] * (1 + V['amount_growth']) ** ((a96 - 1) // 12))[:60].sum()):,.0f}")
    print(f"  opt-in arithmetic: if exactly O of KYC'd users opt in, those who do must apply at 35%/O a year: "
          + ", ".join(f"O={o_:.0%} -> {0.35 / o_:.0%}" for o_ in (0.35, 0.5, 0.7, 1.0))
          + f"; by year 5 the rate is ~{0.35 * 1.05 ** 4:.1%} with take-up growth")
    print("\n== Findings (one change at a time from the plan)")
    for r in F:
        print(f"  {r['id']:<5} {r['LTV/CAC 60m']:>6.2f}x ({r['effect (x)']:+.2f})  pays back {str(r['payback month']):>5}  {r['finding'][:105]}")
    print(f"  F6 adds Rs {float(ns_support[m].sum()):.0f}; F13 bundle Rs {float(bundle[m].sum()):.0f} "
          f"(loans {float(nloans[m].sum()):.3f}, applications {float(base['P+B applications'][m].sum()):.3f} per saver won)")

    # ---------------------------------------------------------- 3. affordability
    A = []
    for nm, amt, rates, months in (("Personal + business, Rs 3 lakh, 18 months", 300000, (0.18, 0.24, 0.30, 0.36), 18),
                                    ("Home, Rs 30 lakh, 20 years", 3000000, (0.085, 0.10, 0.12), 240),
                                    ("Home, Rs 30 lakh, 15 years", 3000000, (0.085, 0.10, 0.12), 180),
                                    ("Property (LAP), Rs 25 lakh, 15 years", 2500000, (0.11, 0.14, 0.18), 180),
                                    ("Property (LAP), Rs 25 lakh, 10 years", 2500000, (0.11, 0.14, 0.18), 120)):
        for r in rates:
            e_ = emi(amt, r, months)
            A.append({"case": nm, "rate a year": r, "EMI Rs a month": round(e_), "income needed, FOIR 50%": round(e_ / 0.5),
                      "income needed, FOIR 40%": round(e_ / 0.4), "EMI as a multiple of the Rs 2,000 saved a month": round(e_ / 2000, 1)})
    for inc, src in ((23012, "urban self-employed average, NG-005"), (30000, "middle of a typical customer, IV-04"),
                     (34868, "Delhi urban self-employed, NG-006"), (40000, "top of a typical customer, IV-04")):
        for r in (0.24, 0.30):
            for foir in (0.4, 0.5):
                A.append({"case": f"Largest 18-month loan on Rs {inc:,} a month ({src}), no other debt", "rate a year": r,
                          "FOIR": foir, "largest loan Rs": round(max_loan(inc * foir, r, 18), -3)})
    write("recalc_affordability.csv", A)
    print("\n== Affordability")
    for r in A:
        print("  " + "; ".join(f"{k}: {v}" for k, v in r.items()))

    # ---------------------------------------------------------- 4. month by month, for the record
    keys = ("still saving", "reach curve", "balance", "Fund trail", "P+B first loans", "P+B repeat loans", "P+B top-ups", "Gold",
            "Property (LAP)", "Home", "Durables", "Vehicles", "Cards", "Recharge, bills, FD, NPS", "Revenue", "Serving", "Net")
    cum = np.cumsum(base["Net"]) - S["cac"]
    write("recalc_monthly.csv", [{"month": i + 1, **{k: round(float(base[k][i]), 4) for k in keys},
                                  "cumulative after the cost to win": round(float(cum[i]), 2)} for i in range(N)])


if __name__ == "__main__":
    main()

"""Writes tables/v4_gsheet_spec.json: the v4 tabs of the Google Sheet (21 Oct 2026), the online-first plan of record
(model/online_plan.py, company() and saver_inputs()), as live formulas plus value tabs. Since 24 Oct the inputs are the main case,
the LTV/CAC Monte Carlo's median (model/v4_toy_check.py calls online_plan.use_main_case(); model/ltv_odds.py).

  {"sheets": [{"title", "sheetId", "cells": {"A1": value or "=formula"}, "named_ranges": {name: "B3"}, "formats": {...}}],
   "_monthly_columns": {numpy key: column}, "_per_saver_columns": {...}, "_summary_live": {...}, "_yearly_live": {...}, "_meta": {...}}

Tabs (sheetIds 201-208): v4 README, v4 Inputs, v4 Per saver, v4 Monthly, v4 Yearly, v4 Summary, v4 Levers, v4 Monte Carlo.
Also rewrites the texts of 'Start here' (sheetId 200) in tables/v4_start_here.json. Every headline number in a text cell is read
from the tables (headline()), never retyped; LTV/CAC shows at 2 decimals.
The maths, its numpy twin and the checks: model/v4_toy_check.py (run this file first, then that one).
REBASE 24 Oct: v4 Monte Carlo shows the new ltv_odds.py (2 drawn inputs, 5 upside levers): the summary, one saver's split at 5 and
8 years (fund fees vs cross-sell), the bridge from 23 Oct, the "what it takes" ladder, each upside lever alone and the drawn inputs.

Sheets syntax (as model/toy_gsheet.py): en_GB comma separators; every v4 named range starts with v_ (no clash with the 430
names of the older tabs; none is a cell reference or a function name); MAKEARRAY / SCAN / MMULT / SEQUENCE / LAMBDA / LET;
LAMBDA and LET names avoid r, c and anything that reads as a cell (ag_b1, not agm1); no MIN / MAX / AND / INDEX on arrays inside
ARRAYFORMULA (caps are IF(x>cap,cap,x), conditions multiply); INDEX positions are guarded with MAX(1, ...) even inside IF.
"""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ltv_odds as lo  # noqa: E402
import online_plan as op  # noqa: E402
import toy_check as tc  # noqa: E402
import v4_toy_check as vt  # noqa: E402

T = vt.T
OUT = vt.SPEC
P = vt.PFX
M = vt.M
LAST = M + 1                      # last data row on Per saver and Monthly (rows 2-97 = ages / months 1-96)
NP = len(vt.product_rows())       # 19 products
RUN_DATE = vt.RUN_DATE
SHEET_IDS = {"v4 README": 201, "v4 Inputs": 202, "v4 Per saver": 203, "v4 Monthly": 204, "v4 Yearly": 205, "v4 Summary": 206,
             "v4 Levers": 207, "v4 Monte Carlo": 208}
FMT = {"pct": "0.0%", "pct2": "0.00%", "pct3": "0.000%", "inr": "#,##0", "inr1": "#,##0.0", "inr2": "#,##0.00", "num0": "0",
       "num1": "0.0", "mult": "0.00", "f3": "0.000", "share": "0.00000", "cr": "#,##0.00", "f6": "0.000000"}
col = tc.col_name


def n(s):
    """'{p}x' -> 'v_x' in a formula template."""
    return s.replace("{p}", P)


# ---------------------------------------------------------------- v4 Inputs
def inputs_sheet():
    cells = {"A1": "Input", "B1": "Value", "C1": "Unit", "D1": "Source / basis", "E1": "Name in formulas"}
    names, fm = {}, {"number": {}, "blue_font": [], "grey_font": [], "bold_rows": [1], "freeze_rows": 1, "wrap_rows": [],
                     "col_widths": {"A": 520, "B": 120, "C": 130, "D": 560, "E": 170}}
    r = 2
    for sec, rows in vt.input_sections():
        cells[f"A{r}"] = sec
        fm["bold_rows"].append(r)
        r += 1
        for key, label, unit, f, val, basis in rows:
            cells.update({f"A{r}": label, f"B{r}": val, f"C{r}": unit, f"D{r}": basis, f"E{r}": P + key})
            names[P + key] = f"B{r}"
            fm["number"][f"B{r}"] = FMT[f]
            fm["blue_font"].append(f"B{r}")
            if sec.startswith("Scenario"):
                fm["bold_rows"].append(r)
            r += 1
    r += 1
    cells[f"A{r}"] = "Worked out from the inputs (formulas; do not type here)"
    fm["bold_rows"].append(r)
    r += 1
    for key, label, unit, f, formula in vt.DERIVED:
        cells.update({f"A{r}": label, f"B{r}": n(formula), f"C{r}": unit, f"D{r}": "Worked out", f"E{r}": P + key})
        names[P + key] = f"B{r}"
        fm["number"][f"B{r}"] = FMT[f]
        fm["grey_font"].append(f"B{r}")
        r += 1
    # the product table
    r += 1
    cells[f"A{r}"] = (f"Cross-sell: the {NP} products (the Python engine's PRODUCTS at the online values; blue = inputs, grey = "
                      "worked out). Every product is offered from his month 1; take-up hazards apply to active savers who never held it.")
    fm["bold_rows"].append(r)
    r += 1
    hdr = ["Product", "Kind (see the note at the right)", "Take-up a year", "Ticket (₹)", "Our commission", "Renews / continues a year",
           "Renewal commission", "Approval share (home loan, LAP)", "Insurance group (1 = yes; partner share applies)",
           "Home loan / LAP (formula)", "Money booked at take-up, ₹ a take-up (formula)",
           "Calendar lag of its later money, months (formula)", "Take-up chance a month, his months 1-6 (formula)",
           "Take-up chance a month, from his month 7 (formula)", "Kind",
           "Loan offered to the KYC'd users who never save (1 = yes: gold, property, home; 22 Oct)"]
    for j, h in enumerate(hdr):
        cells[f"{col(j + 1)}{r}"] = h
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    r0 = r
    for i, pr in enumerate(vt.product_rows()):
        rr = r0 + i
        cells[f"A{rr}"], cells[f"B{rr}"] = pr["name"], pr["kind"]
        for c_, key in (("C", "takeup"), ("D", "ticket"), ("E", "comm"), ("F", "renew"), ("G", "rcomm"), ("H", "appr")):
            if pr.get(key) is not None:
                cells[f"{c_}{rr}"] = pr[key]
                fm["blue_font"].append(f"{c_}{rr}")
        cells[f"I{rr}"] = pr["ins"]
        fm["blue_font"].append(f"I{rr}")
        if pr.get("takeup_formula"):
            cells[f"C{rr}"] = n("=IF({p}eq_share>0,0,{p}sip_takeup_debt)")
            fm["blue_font"].remove(f"C{rr}")
            fm["grey_font"].append(f"C{rr}")
        if pr.get("rcomm_same"):
            cells[f"G{rr}"] = f"=E{rr}"
            fm["blue_font"].remove(f"G{rr}")
            fm["grey_font"].append(f"G{rr}")
        words = vt.ce.PARAM_WORDS_BY.get(pr["p"], {})
        units = "; ".join(f"{'ticket' if q == 'ticket' else 'commission' if q == 'comm' else 'renews'} = {w}"
                          for q, w in words.items() if q in ("ticket", "comm", "renew"))
        cells[f"O{rr}"] = text(vt.KIND_WORDS[pr["kind"]] + (f" ({units})" if units else ""))
        cells[f"P{rr}"] = pr["loan"]
        fm["blue_font"].append(f"P{rr}")
    rl = r0 + NP - 1
    for nm, c_ in (("pr_name", "A"), ("pr_kind", "B"), ("pr_takeup", "C"), ("pr_ticket", "D"), ("pr_comm", "E"), ("pr_renew", "F"),
                   ("pr_rcomm", "G"), ("pr_appr", "H"), ("pr_ins", "I"), ("pr_house", "J"), ("pr_book", "K"), ("pr_lag", "L"),
                   ("pr_he", "M"), ("pr_hf", "N"), ("pr_loan", "P")):
        names[P + nm] = f"{c_}{r0}:{c_}{rl}"
    K = lambda p_: f'INDEX({P}pr_kind,{p_})'
    cells[f"J{r0}"] = f'=MAKEARRAY({NP},1,LAMBDA(p,z,IF({K("p")}="secured",1,0)))'
    cells[f"K{r0}"] = n(f'=MAKEARRAY({NP},1,LAMBDA(p,z,IF(OR({K("p")}="once",{K("p")}="secured",{K("p")}="ins"),'
                        'INDEX({p}pr_ticket,p)*INDEX({p}pr_comm,p)*IF(INDEX({p}pr_ins,p)=1,{p}ins_share,1),0)))')
    cells[f"L{r0}"] = n(f'=MAKEARRAY({NP},1,LAMBDA(p,z,IF({K("p")}="ins",12,IF({K("p")}="bonus",24,'
                        f'IF(OR({K("p")}="flow",{K("p")}="flow_year",{K("p")}="trail"),{{p}}lag_hold,0)))))')
    cells[f"M{r0}"] = n(f'=MAKEARRAY({NP},1,LAMBDA(p,z,(1-(1-INDEX({{p}}pr_takeup,p))^(1/12))*{{p}}tf_e*'
                        f'IF({K("p")}="secured",MIN(0.8,INDEX({{p}}pr_appr,p)*{{p}}early_approval*{{p}}ma_hold),1)))')
    cells[f"N{r0}"] = n(f'=MAKEARRAY({NP},1,LAMBDA(p,z,(1-(1-INDEX({{p}}pr_takeup,p))^(1/12))*{{p}}tf_f*'
                        f'IF({K("p")}="secured",MIN(0.8,INDEX({{p}}pr_appr,p)*{{p}}ma_hold),1)))')
    fm["grey_font"] += [f"{c_}{r0}:{c_}{rl}" for c_ in "JKLMN"]
    fm["number"].update({f"C{r0}:C{rl}": "0.0%", f"D{r0}:D{rl}": "#,##0", f"E{r0}:E{rl}": "0.00%", f"F{r0}:F{rl}": "0%",
                         f"G{r0}:G{rl}": "0.00%", f"H{r0}:H{rl}": "0%", f"I{r0}:J{rl}": "0", f"K{r0}:K{rl}": "#,##0.00",
                         f"L{r0}:L{rl}": "0", f"M{r0}:N{rl}": "0.0000%", f"P{r0}:P{rl}": "0"})
    fm["col_widths"].update({"F": 110, "G": 110, "H": 110, "I": 110, "J": 100, "K": 130, "L": 110, "M": 120, "N": 120, "O": 420})
    r = rl + 2
    notes = [
        "Kinds (the engine's): once = commission at take-up (device insurance, NPS, FD, gold / consumer-durable / vehicle loans); "
        "secured = home loan or LAP, applications x approval (approval grows with the calendar, cap 80%), our fee at disbursal; "
        "ins = first-year commission at take-up, then the renewal commission each year x renews^years while he still saves; "
        "bonus = Choti SIP ₹500 at month 24 if the SIP survives; flow = digital gold, buys a month x commission while he holds it; "
        "flow_year = recharge and bills, a year's spend / 12 x commission while he holds it; trail = the SIP cross-sell trail "
        "(0 while the core balance is the equity SIP).",
        "Insurance money would reach us through a broker partner (ins_share; 0 since 22 Oct: a fixed referral fee, not counted). A saver who stops saving lapses his policies and "
        "holdings (the engine's conservative rule).",
        "Calendar lag (Monthly only): money booked at take-up takes this month's calendar factor; insurance renewals take the factor "
        "of 12 months earlier, the Choti bonus 24, holdings lag_hold (6). See README, 'How the sheet works'.",
    ]
    for t_ in notes:
        cells[f"A{r}"] = t_
        r += 1
    # inputs added after the product table (21 Oct) so that no earlier row or named range moves
    r += 1
    sec, rows = vt.EXTRA_INPUTS
    cells[f"A{r}"] = sec
    fm["bold_rows"].append(r)
    r += 1
    for key, label, unit, f, val, basis in rows:
        cells.update({f"A{r}": label, f"B{r}": val, f"C{r}": unit, f"D{r}": basis, f"E{r}": P + key})
        names[P + key] = f"B{r}"
        fm["number"][f"B{r}"] = FMT[f]
        fm["blue_font"].append(f"B{r}")
        r += 1
    return {"title": "v4 Inputs", "cells": cells, "named_ranges": names, "formats": fm}


# ---------------------------------------------------------------- v4 Per saver
def per_saver_columns():
    """[(key, header, kind, formula | (row-2 value, template), format)] in column order; kind spill|row|block."""
    cols = [("age", "His month (age). Rows 2-97 = his months 1-96", "spill", f"=SEQUENCE({M})", "num0")]
    for sv, nm in (("on", "Online saver"), ("door", "Doorstep saver")):
        s = f"{P}s_{sv}"
        r3, r12 = (f"{P}on_r3", f"{P}on_r12") if sv == "on" else (f"{P}door_r3", f"{P}door_r12")
        cols += [
            (f"s_{sv}", f"{nm}: still saving (share of those who joined)", "spill",
             f"=ARRAYFORMULA({r3}^(IF({P}age-1>3,3,{P}age-1)/3)*({r12}/{r3})^(IF({P}age-4>9,9,IF({P}age-4<0,0,{P}age-4))/9)"
             f"*(1-{P}churn_late)^IF({P}age-13>0,{P}age-13,0))", "share"),
            (f"{sv}_dep", f"{nm}: deposits per saver who joined (₹)", "spill", f"=ARRAYFORMULA({s}*{P}dep)", "inr2"),
            (f"{sv}_bal", f"{nm}: average fund balance per saver who joined (₹)", "spill", f"=ARRAYFORMULA({s}*{P}bavg)", "inr2"),
            (f"{sv}_trail", f"{nm}: fund trail (₹)", "spill", f"=ARRAYFORMULA({s}*{P}trail_pa)", "inr2"),
            (f"{sv}_loanfee", f"{nm}: loan referral fees at the lender payout (₹; Monthly adds the payout ramp, flat in the main case)", "spill",
             f"=ARRAYFORMULA({s}*{P}loanfee_pa)", "inr2"),
            (f"{sv}_cards", f"{nm}: card fees (₹)", "spill", f"=ARRAYFORMULA({s}*{P}cardfee_pa)", "inr2"),
            (f"{sv}_ins", f"{nm}: insurance (₹)", "spill", f"=ARRAYFORMULA({s}*{P}ins_pa)", "inr2"),
            (f"{sv}_oth", f"{nm}: other products incl. home loans and LAP (₹)", "spill",
             f"=ARRAYFORMULA({s}*({P}oth_pa+{P}house_pa))", "inr2"),
            (f"{sv}_rev", f"{nm}: revenue (₹)", "spill",
             f"=ARRAYFORMULA({P}{sv}_trail+{P}{sv}_loanfee+{P}{sv}_cards+{P}{sv}_ins+{P}{sv}_oth)", "inr2"),
            (f"{sv}_supp", f"{nm}: serving: support, tech for every KYC'd user reached, payments, with the 10% contingency (₹)", "spill",
             f"=ARRAYFORMULA({s}*({P}support+{P}tech_per_saver*{P + 'loan_reach' if sv == 'on' else '1'}+{P}debit_cost*{P}debits_month)"
             f"*(1+{P}contingency))", "inr2"),
            (f"{sv}_cum", f"{nm}: revenue less serving, cumulative (₹; compare with the cost to win them)", "spill",
             f"=ARRAYFORMULA(SCAN(0,{P}{sv}_rev-{P}{sv}_supp,LAMBDA(acc,x,acc+x)))", "inr2"),
        ]
    cols += [
        ("dep", "PER ACTIVE SAVER (both savers): deposit a month (₹)", "spill",
         n("=ARRAYFORMULA({p}daily*{p}deposit_days*(1+{p}amount_growth)^INT(({p}age-1)/{p}term))"), "inr2"),
        ("endbal", "Per active saver: fund balance at month end (₹)", "spill",
         n("=SCAN(0,{p}age,LAMBDA(acc,a,(acc*IF(MOD(a-1,{p}term)=0,{p}rollover,1)*(1-{p}withdraw_m)+0.5*INDEX({p}dep,a))"
           "*(1+{p}fund_m)+0.5*INDEX({p}dep,a)))"), "inr2"),
        ("bavg", "Per active saver: average fund balance (₹)", "spill", n("=ARRAYFORMULA(({p}endbal-0.5*{p}dep)/(1+{p}fund_m))"), "inr2"),
        ("trail_pa", "Per active saver: fund trail (₹)", "spill", n("=ARRAYFORMULA({p}bavg*{p}trail/12)"), "rs4"),
        ("tf", "Take-up factor (early months; held calendar year)", "spill", n("=ARRAYFORMULA(IF({p}age<=6,{p}tf_e,{p}tf_f))"), "f3"),
        ("q1", "First-loan chance a month (never borrowed)", "spill",
         n("=ARRAYFORMULA({p}apply_m*{p}tf*{p}eligible*IF({p}age<=6,{p}af_e,{p}af_f))"), "share"),
        ("n0", "Never borrowed (share of active savers)", "spill",
         n("=ARRAYFORMULA((1-{p}q1e)^IF({p}age-1>6,6,{p}age-1)*(1-{p}q1f)^IF({p}age-7>0,{p}age-7,0))"), "share"),
        ("first", "First loans per active saver", "spill", n("=ARRAYFORMULA({p}n0*{p}q1)"), "f6"),
    ]
    cols += [  # row by row: the repaid pool reads the loans of tenure + 1 months earlier
        ("back", "Repaid and back in the pool (share of active savers; row by row)", "row", None, "f6"),
        ("repeat", "Repeat loans per active saver (row by row)", "row", None, "f6"),
        ("loans", "Loans per active saver, first + repeat (row by row)", "row", None, "f6"),
    ]
    cols += [
        ("tpool", "Top-up pool: loans with 12+ EMIs paid and EMIs left, per active saver", "spill",
         n(f"=MAKEARRAY({M},1,LAMBDA(a,z,IF({{p}}tenure_m>13,1,0)*IF(a<14,0,SUM(MAKEARRAY(MAX(1,{{p}}tenure_m-13),1,LAMBDA(k,y,"
           "IF(a-12-k>=1,INDEX({p}loans,MAX(1,a-12-k))*(1-{p}topup_m)^(k-1),0)))))))"), "f6"),
        ("topups", "Top-ups per active saver", "spill", n("=ARRAYFORMULA({p}topup_m*{p}tpool)"), "f6"),
        ("lent", "Money lent per active saver: first, repeat and top-up loans (₹)", "spill",
         n("=ARRAYFORMULA({p}first*{p}ticket+{p}repeat*{p}rep_ticket+{p}topups*{p}topup_amt)"), "inr2"),
        ("loanfee_pa", "Per active saver: loan referral fees at the lender payout (₹)", "spill",
         n("=ARRAYFORMULA({p}lent*{p}fee*(1-{p}taken_back))"), "rs4"),
        ("cards", "Cards per active saver", "spill",
         n("=ARRAYFORMULA(IF({p}age<=6,{p}card_share/6*{p}tf*{p}card_ae,IF({p}age<=12,{p}card_share*{p}card_catchup/6*{p}card_cg,0)))"), "f6"),
        ("cardfee_pa", "Per active saver: card fees (₹)", "spill", n("=ARRAYFORMULA({p}cards*{p}card_fee)"), "rs4"),
        ("ins_pa", "Per active saver: insurance (₹)", "spill", n("=MMULT({p}prodmoney,{p}pr_ins)"), "rs4"),
        ("house_pa", "Per active saver: home loans and LAP (₹)", "spill", n("=MMULT({p}prodmoney,{p}pr_house)"), "rs4"),
        ("oth_pa", "Per active saver: other products, not home loans or LAP (₹)", "spill",
         n(f"=ARRAYFORMULA(MMULT({{p}}prodmoney,SEQUENCE({NP},1,1,0))-{{p}}ins_pa-{{p}}house_pa)"), "rs4"),
        ("support_pa", "Per active saver: support cost (₹)", "spill", n("=ARRAYFORMULA({p}support+0*{p}age)"), "rs4"),
        ("rev_pa", "Per active saver: revenue at the held calendar year (₹)", "spill",
         n("=ARRAYFORMULA({p}trail_pa+{p}loanfee_pa+{p}cardfee_pa+{p}ins_pa+{p}house_pa+{p}oth_pa)"), "rs4"),
    ]
    G = lambda a_, p_="p": f"INDEX({P}takeups,{a_},{p_})"
    money = (f"=MAKEARRAY({M},{NP},LAMBDA(a,p,LET(kd,INDEX({P}pr_kind,p),tk,INDEX({P}pr_ticket,p),"
             f"sh,IF(INDEX({P}pr_ins,p)=1,{P}ins_share,1),sh*IF(OR(kd=\"once\",kd=\"secured\"),{G('a')}*tk*INDEX({P}pr_comm,p),"
             f"IF(kd=\"ins\",{G('a')}*tk*INDEX({P}pr_comm,p)+SUM(MAKEARRAY(7,1,LAMBDA(k,y,IF(a-12*k>=1,"
             f"{G('MAX(1,a-12*k)')}*INDEX({P}pr_renew,p)^k*tk*INDEX({P}pr_rcomm,p),0)))),"
             f"IF(kd=\"bonus\",IF(a>24,{G('MAX(1,a-24)')}*INDEX({P}pr_renew,p)*tk,0),"
             f"SUM(MAKEARRAY(a,1,LAMBDA(j,y,{G('j')}*INDEX({P}pr_renew,p)^((a-j)/12)*IF(kd=\"trail\",(a-j+0.5)*tk*INDEX({P}pr_comm,p)/12,"
             f"IF(kd=\"flow_year\",tk*INDEX({P}pr_comm,p)/12,tk*INDEX({P}pr_comm,p))))))))))))")
    cols += [
        ("takeups", "Take-ups per active saver, by product ->", "block",
         f"=MAKEARRAY({M},{NP},LAMBDA(a,p,IF(a<=6,(1-INDEX({P}pr_he,p))^(a-1)*INDEX({P}pr_he,p),"
         f"(1-INDEX({P}pr_he,p))^6*(1-INDEX({P}pr_hf,p))^(a-7)*INDEX({P}pr_hf,p))))", "f6"),
        ("prodmoney", "Money per active saver, by product (₹) ->", "block", money, "rs4"),
        ("prodnow", "Of which booked at take-up (₹) ->", "block",
         f"=MAKEARRAY({M},{NP},LAMBDA(a,p,INDEX({P}takeups,a,p)*INDEX({P}pr_book,p)))", "rs4"),
    ]
    return cols


def per_saver_sheet():
    cols = per_saver_columns()
    letters, c = {}, 1
    for key, _h, kind, _f, _nf in cols:
        letters[key] = col(c)
        c += NP if kind == "block" else 1
    cells, names = {}, {}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "wrap_rows": [1], "col_widths": {"A": 90},
          "copy_down": {"from_row": 3, "to_rows": [4, LAST], "cols": [letters["back"], letters["loans"]]}}
    nfmt = dict(FMT, rs4="#,##0.0000")
    pnames = [p["name"] for p in vt.product_rows()]
    for key, h, kind, f, nf in cols:
        L = letters[key]
        if kind == "block":
            last = col(tc.col_num(L) + NP - 1)
            names[P + key] = f"{L}2:{last}{LAST}"
            for j, pn in enumerate(pnames):
                cells[f"{col(tc.col_num(L) + j)}1"] = f"{h.split(' ->')[0]}: {pn}"
            cells[f"{L}2"] = f
            fm["number"][f"{L}2:{last}{LAST}"] = nfmt[nf]
            continue
        cells[f"{L}1"] = h
        names[P + key] = f"{L}2:{L}{LAST}"
        fm["number"][f"{L}2:{L}{LAST}"] = nfmt[nf]
        if kind == "spill":
            cells[f"{L}2"] = f
    A_, B_, R_, LO, F_, TF = (letters[k] for k in ("age", "back", "repeat", "loans", "first", "tf"))
    for r in range(2, LAST + 1):        # row order (keeps the interpreter's recursion shallow)
        p = r - 1
        cells[f"{B_}{r}"] = 0 if r == 2 else (f"={B_}{p}-{R_}{p}+IF({A_}{r}-1-{P}tenure_m>=1,INDEX({LO}$2:{LO}{p},"
                                              f"MAX(1,{A_}{r}-1-{P}tenure_m)),0)")
        cells[f"{R_}{r}"] = f"={B_}{r}*{P}apply_m*{TF}{r}*{P}eligible*{P}approved_repeat"
        cells[f"{LO}{r}"] = f"={F_}{r}+{R_}{r}"
    return {"title": "v4 Per saver", "cells": cells, "named_ranges": names, "formats": fm}, letters


# ---------------------------------------------------------------- v4 Monthly
AMAT = (f"MAKEARRAY({M},{M},LAMBDA(m,a,IF(m>=a,INDEX({P}on_won,MAX(1,m-a+1))*INDEX({P}s_on,a)"
        f"+INDEX({P}door_won,MAX(1,m-a+1))*INDEX({P}s_door,a),0)))")
AON = (f"MAKEARRAY({M},{M},LAMBDA(m,a,IF(m>=a,INDEX({P}on_won,MAX(1,m-a+1))*INDEX({P}s_on,a),0)))")


def monthly_columns():
    flater = f"MAKEARRAY({M},{NP},LAMBDA(m,p,INDEX({P}f_t,MAX(1,m-INDEX({P}pr_lag,p)))))"
    fdiff = (f"MAKEARRAY({M},{NP},LAMBDA(m,p,IF(INDEX({P}pr_house,p)=1,INDEX({P}f_ta,m),INDEX({P}f_t,m))"
             f"-INDEX({P}f_t,MAX(1,m-INDEX({P}pr_lag,p)))))")
    return [
        ("month", "Month", f"=SEQUENCE({M})", "num0"),
        ("year", "Year", n("=ARRAYFORMULA(INT(({p}month-1)/12)+1)"), "num0"),
        ("yc", "Calendar year for take-up and approval growth (held after year_hold)", n("=ARRAYFORMULA(IF({p}year>{p}year_hold,{p}year_hold,{p}year))"), "num0"),
        ("f_t", "Take-up factor, relative to the held year (Per saver is at the held year)",
         n("=ARRAYFORMULA((1+{p}takeup_growth)^({p}yc-1)/{p}mt_hold)"), "f3"),
        ("f_ta", "Take-up x approval factor, relative to the held year (loan fees, cards, home loans, LAP)",
         n("=ARRAYFORMULA({p}f_t*(1+{p}approval_growth)^({p}yc-1)/{p}ma_hold)"), "f3"),
        ("feemult", "Lender payout multiplier (the payout x this; straight line to month 60, held; 1 = flat)",
         n("=ARRAYFORMULA({p}fee_mult_start+({p}fee_mult_end-{p}fee_mult_start)*(IF({p}month>60,60,{p}month)-1)/59)"), "f3"),
        ("raw", "Online savers won before the pool cap: seed level, straight line to the plan level by ramp_end, then x growth a year",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,IF(m<{{p}}launch,0,IF(m<={{p}}seed_end,{{p}}seed_online,IF(m<={{p}}ramp_end,{{p}}seed_online"
           "+({p}level-{p}seed_online)*(m-{p}seed_end)/({p}ramp_end-{p}seed_end),{p}level*{p}growth^((m-{p}ramp_end)/12))))))"), "num0"),
        ("cumraw", "Savers won to date before the cap, incl. the doorstep share", n("=SCAN(0,{p}raw,LAMBDA(acc,x,acc+x*(1+{p}door_ratio)))"), "num0"),
        ("on_won", "Online savers won (stop once all savers won reach pool_cap x pool)",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,MAX(0,MIN(INDEX({{p}}raw,m),({{p}}pool*{{p}}pool_cap-IF(m=1,0,INDEX({{p}}cumraw,MAX(1,m-1))))"
           "/(1+{p}door_ratio)))))"), "num0"),
        ("agents", "Doorstep agents (enough for 1 in 9 of the online savers won; at least 1)",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,IF(OR(m<{{p}}launch,AND(m>{{p}}seed_end,{{p}}door_after<0.5),INDEX({{p}}on_won,m)<=0),0,"
           "MAX(1,ROUNDUP(INDEX({p}on_won,m)*{p}door_ratio/{p}agent_signups,0)))))"), "num0"),
        ("door_won", "Doorstep savers won (each new agent at 50%, 67%, 83% of full speed in his first three months)",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,LET(ag_now,INDEX({{p}}agents,m),ag_b1,IF(m>1,INDEX({{p}}agents,MAX(1,m-1)),0),"
           "ag_b2,IF(m>2,INDEX({p}agents,MAX(1,m-2)),0),ag_b3,IF(m>3,INDEX({p}agents,MAX(1,m-3)),0),"
           "{p}agent_signups*(ag_now-(1-{p}agent_ramp1)*MAX(0,ag_now-ag_b1)-(1-{p}agent_ramp2)*MAX(0,MIN(ag_now,ag_b1)-ag_b2)"
           "-(1-{p}agent_ramp3)*MAX(0,MIN(ag_now,ag_b1,ag_b2)-ag_b3)))))"), "num0"),
        ("won", "All savers won", n("=ARRAYFORMULA({p}on_won+{p}door_won)"), "num0"),
        ("active", "Active savers (each month's savers won x still saving at their age)", f"=MMULT({AMAT},SEQUENCE({M},1,1,0))", "num0"),
        ("aum", "AUM: average fund balance (₹)", f"=MMULT({AMAT},{P}bavg)", "inr"),
        ("r_fund", "Revenue: fund trail (₹)", n("=ARRAYFORMULA({p}aum*{p}trail/12)"), "inr"),
        ("r_loan", "Revenue: loan marketing fees (₹)", f"=ARRAYFORMULA(MMULT({AMAT},{P}loanfee_pa)*{P}f_ta*{P}feemult)", "inr"),
        ("r_cards", "Revenue: cards (₹)", f"=ARRAYFORMULA(MMULT({AMAT},{P}cardfee_pa)*{P}f_ta)", "inr"),
        ("r_ins", "Revenue: insurance (₹)", n("=MMULT({p}xs,{p}pr_ins)"), "inr"),
        ("r_oth", "Revenue: other products incl. home loans and LAP (₹)", n("=ARRAYFORMULA(MMULT({p}xs,1-{p}pr_ins))"), "inr"),
        ("revenue", "Revenue (₹)", n("=ARRAYFORMULA({p}r_fund+{p}r_loan+{p}r_cards+{p}r_ins+{p}r_oth+{p}r_reach)"), "inr"),
        ("mkt", "Acquisition: cost to win online savers (seed CAC to seed_end, then CAC) (₹)",
         n("=ARRAYFORMULA({p}on_won*IF({p}month<={p}seed_end,{p}seed_cac,{p}cac_rs))"), "inr"),
        ("hires", "Doorstep agents hired (new + replacements)",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,MAX(0,INDEX({{p}}agents,m)-IF(m>1,INDEX({{p}}agents,MAX(1,m-1)),0))"
           "+INDEX({p}agents,m)*{p}agent_churn/12))"), "num1"),
        ("door_cost", "Acquisition: doorstep agents, field leads, city offices, kits, KYC (₹)",
         n("=ARRAYFORMULA({p}agents*{p}agent_cost+IF({p}agents>{p}big_from,ROUNDUP({p}agents/{p}per_lead,0)*{p}lead_pay"
           "+ROUNDUP({p}agents/{p}per_city,0)*{p}city_office,0)+{p}hires*{p}hire_kit+{p}door_won*{p}door_kyc)"), "inr"),
        ("acquisition", "Acquisition (₹)", n("=ARRAYFORMULA({p}mkt+{p}door_cost)"), "inr"),
        ("rf", "Pay rise factor (+raise_rate each year after the seed)",
         n("=ARRAYFORMULA(IF({p}month>{p}seed_end,(1+{p}raise_rate)^INT(({p}month-{p}seed_end-1)/12),1))"), "f3"),
        ("seed_heads", "Seed team (2 founders, an engineer, ops from ops_from, junior engineer from jr_from)",
         n("=ARRAYFORMULA(IF({p}month>{p}seed_end,0,3+IF({p}month>={p}ops_from,1,0)+IF({p}month>={p}jr_from,1,0)))"), "num0"),
        ("seed_pay", "Seed team pay (₹)",
         n("=ARRAYFORMULA(IF({p}month>{p}seed_end,0,2*{p}pay_founder_seed+{p}pay_eng_seed+IF({p}month>={p}ops_from,{p}pay_ops_seed,0)"
           "+IF({p}month>={p}jr_from,{p}pay_jr_seed,0)))"), "inr"),
        ("eng", "Engineers (after the seed)",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,IF(m>{{p}}seed_end,MIN({{p}}eng_cap,{{p}}eng_base+INT(INDEX({{p}}active,m)/{{p}}eng_per)),0)))"), "num0"),
        ("product", "Product", n("=ARRAYFORMULA(IF({p}month>{p}seed_end,1+INT({p}active/{p}product_per),0))"), "num0"),
        ("ops", "Ops",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,IF(m>{{p}}seed_end,MIN({{p}}ops_cap,MAX({{p}}ops_min,ROUNDUP(INDEX({{p}}active,m)/{{p}}ops_per,0))),0)))"),
         "num0"),
        ("growth_hc", "Growth", n("=ARRAYFORMULA(IF({p}month>{p}seed_end,1+INT({p}mkt/{p}growth_per),0))"), "num0"),
        ("finance", "Finance", n("=ARRAYFORMULA(IF({p}month>{p}seed_end,1+INT({p}active/{p}finance_per),0))"), "num0"),
        ("risk", "Risk", n("=ARRAYFORMULA(IF(({p}month>{p}seed_end)*({p}month>={p}risk_from),1,0))"), "num0"),
        ("heads", "Heads (seed team, or 2 founders + compliance + the scaling roles)",
         n("=ARRAYFORMULA({p}seed_heads+IF({p}month>{p}seed_end,3,0)+{p}eng+{p}product+{p}ops+{p}growth_hc+{p}finance+{p}risk)"), "num0"),
        ("team", "Team (₹)",
         n("=ARRAYFORMULA(({p}seed_pay+IF({p}month>{p}seed_end,2*{p}pay_founder+{p}pay_compliance,0)+{p}eng*{p}pay_engineer"
           "+{p}product*{p}pay_product+{p}ops*{p}pay_ops+{p}growth_hc*{p}pay_growth+{p}finance*{p}pay_finance+{p}risk*{p}pay_risk)*{p}rf)"), "inr"),
        ("tech", "Other: tech (₹; per KYC'd user reached: active savers + (loan_reach - 1) x online active savers)",
         n("=ARRAYFORMULA(IF({p}month<=3,{p}tech_build/3,0)+{p}tech_base+({p}active+({p}loan_reach-1)*{p}active_on)*{p}tech_per_saver)"), "inr"),
        ("office", "Other: office (₹)", n("=ARRAYFORMULA(IF({p}month>{p}seed_end,{p}office_base+{p}heads*{p}office_per_head,{p}office_seed))"), "inr"),
        ("compliance", "Other: compliance (₹)",
         n("=ARRAYFORMULA(IF({p}month=1,{p}comp_setup,0)+IF({p}month>{p}seed_end,{p}comp_year,{p}comp_seed_year)/12)"), "inr"),
        ("brand", "Other: brand (₹)", n("=ARRAYFORMULA(IF({p}month>{p}seed_end,{p}brand,0))"), "inr"),
        ("design", "Other: design (₹)", n("=ARRAYFORMULA(IF({p}month<=3,{p}design,0))"), "inr"),
        ("raise", "Other: fund-raising (₹)",
         n("=ARRAYFORMULA(IF({p}month=1,{p}raise_seed,0)+IF({p}month={p}seed_end+1,{p}raise_round,0))"), "inr"),
        ("support", "Other: support and payments (₹; support + debit_cost x debits_month per active saver)",
         n("=ARRAYFORMULA({p}active*({p}support+{p}debit_cost*{p}debits_month))"), "inr"),
        ("other", "Other costs (₹)",
         n("=ARRAYFORMULA({p}c_tech+{p}c_office+{p}c_compliance+{p}c_brand+{p}c_design+{p}c_raise+{p}c_support)"), "inr"),
        ("contingency", "Contingency (10%): contingency x every expensed line (acquisition, team, other costs) (₹)",
         n("=ARRAYFORMULA({p}contingency*({p}mkt+{p}door_cost+{p}team+{p}c_tech+{p}c_office+{p}c_compliance+{p}c_brand+{p}c_design"
           "+{p}c_raise+{p}c_support))"), "inr"),
        ("ebitda", "EBITDA (₹)", n("=ARRAYFORMULA({p}revenue-{p}acquisition-{p}team-{p}other-{p}c_contingency)"), "inr"),
        ("cum_ebitda", "Cumulative EBITDA (losses carried forward) (₹)", n("=SCAN(0,{p}ebitda,LAMBDA(acc,x,acc+x))"), "inr"),
        ("tax", "Tax (₹)", n("=ARRAYFORMULA(IF(({p}cum_ebitda>0)*({p}ebitda>0),{p}tax_rate*IF({p}ebitda<{p}cum_ebitda,{p}ebitda,{p}cum_ebitda),0))"), "inr"),
        ("pat", "PAT (₹)", n("=ARRAYFORMULA({p}ebitda-{p}tax)"), "inr"),
        ("received", "Cash received from revenue: the revenue of comm_lag months earlier (₹)",
         n(f"=MAKEARRAY({M},1,LAMBDA(m,z,IF(m>{{p}}comm_lag,INDEX({{p}}revenue,MAX(1,m-{{p}}comm_lag)),0)))"), "inr"),
        ("cash_flow", "Cash flow: PAT - revenue + cash received (₹)", n("=ARRAYFORMULA({p}pat-{p}revenue+{p}received)"), "inr"),
        ("cum", "Cumulative cash (₹; no interest on cash; money needed = its deepest hole + the cash buffer)",
         n("=SCAN(0,{p}cash_flow,LAMBDA(acc,x,acc+x))"), "inr"),
        ("lens1", "Lens 1: arr_mult x 12 x the month's revenue (₹)", n("=ARRAYFORMULA({p}arr_mult*12*{p}revenue)"), "inr"),
        ("lens2", "Lens 2: aum_mult x AUM (₹)", n("=ARRAYFORMULA({p}aum_mult*{p}aum)"), "inr"),
        ("xs", "Cross-sell money this month, by product (₹) ->",
         f"=ARRAYFORMULA(MMULT({AMAT},{P}prodmoney)*{flater}+MMULT({AMAT},{P}prodnow)*{fdiff})", "inr"),
        ("r_reach", "Revenue: loans to KYC'd users who came with online savers and never save: (loan_reach - 1) x the online savers' loan money (₹)",
         f"=ARRAYFORMULA(({P}loan_reach-1)*(MMULT({AON},{P}loanfee_pa)*{P}f_ta*{P}feemult"
         f"+MMULT(MMULT({AON},{P}prodmoney)*{flater}+MMULT({AON},{P}prodnow)*{fdiff},{P}pr_loan)))", "inr"),
        ("active_on", "Online active savers (the online cohorts x still saving; the base of the KYC'd users who see loan offers)",
         f"=MMULT({AON},SEQUENCE({M},1,1,0))", "num0"),
    ]


MONTHLY_NAME = {k: f"c_{k}" for k in ("tech", "office", "compliance", "brand", "design", "raise", "support", "contingency")}


def monthly_sheet():
    cols = monthly_columns()
    letters, c = {}, 1
    for key, *_r in cols:
        letters[key] = col(c)
        c += NP if key == "xs" else 1
    cells, names = {}, {}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "wrap_rows": [1], "col_widths": {"A": 70}}
    pnames = [p["name"] for p in vt.product_rows()]
    for key, h, f, nf in cols:
        L = letters[key]
        nm = P + MONTHLY_NAME.get(key, key)
        if key == "xs":
            last = col(tc.col_num(L) + NP - 1)
            names[nm] = f"{L}2:{last}{LAST}"
            for j, pn in enumerate(pnames):
                cells[f"{col(tc.col_num(L) + j)}1"] = f"Cross-sell this month: {pn} (₹)"
            fm["number"][f"{L}2:{last}{LAST}"] = FMT[nf]
        else:
            cells[f"{L}1"] = h
            names[nm] = f"{L}2:{L}{LAST}"
            fm["number"][f"{L}2:{L}{LAST}"] = FMT[nf]
        cells[f"{L}2"] = f
    return {"title": "v4 Monthly", "cells": cells, "named_ranges": names, "formats": fm}, letters


# ---------------------------------------------------------------- v4 Yearly
def yearly_sheet():
    cells = {"A1": "Line (₹ crore unless a count)", "J1": "Years 1-8"}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "col_widths": {"A": 470}}
    live = {}
    for y in range(1, 9):
        cells[f"{col(y + 1)}1"] = y
    for i, (label, key, how, scale) in enumerate(vt.YEARLY, start=2):
        cells[f"A{i}"] = label
        nm = P + MONTHLY_NAME.get(key, key)
        div = "/1E7" if scale != 1 else ""
        for y in range(1, 9):
            c_ = col(y + 1)
            cells[f"{c_}{i}"] = f"=SUMIFS({nm},{P}year,{c_}$1){div}" if how == "sum" else f"=INDEX({nm},12*{c_}$1){div}"
            live[f"{c_}{i}"] = (key, y)
        if how == "sum":
            cells[f"J{i}"] = f"=SUM({nm}){div}"
            live[f"J{i}"] = (key, 0)
        fm["number"][f"B{i}:J{i}"] = "#,##0.00" if scale != 1 else "#,##0"
        if label.startswith(("Revenue (", "EBITDA", "PAT")):
            fm["bold_rows"].append(i)
    return {"title": "v4 Yearly", "cells": cells, "named_ranges": {}, "formats": fm}, live


# ---------------------------------------------------------------- v4 Summary
SUMMARY_FORMULAS = {
    "Revenue, year 5 (₹ crore)": "=SUMIFS({p}revenue,{p}year,5)/1E7",
    "EBITDA, year 5 (₹ crore)": "=SUMIFS({p}ebitda,{p}year,5)/1E7",
    "Revenue, year 8 (₹ crore)": "=SUMIFS({p}revenue,{p}year,8)/1E7",
    "EBITDA, year 8 (₹ crore)": "=SUMIFS({p}ebitda,{p}year,8)/1E7",
    "EBITDA positive from month (stays at or above 0 from here)":
        '=IF(INDEX({p}ebitda,96)<0,"after m96",IFERROR(MAX(FILTER({p}month,{p}ebitda<0))+1,1))',
    "Money needed: deepest cumulative cash hole + the ₹5 crore cash buffer (₹ crore)": "=(MAX(0,-MIN({p}cum))+{p}floor)/1E7",
    "Money needed ($ million)": "=(MAX(0,-MIN({p}cum))+{p}floor)/{p}rs_per_usd/1E6",
    "Active savers, month 60": "=INDEX({p}active,60)",
    "AUM (average fund balance), month 60 (₹ crore)": "=INDEX({p}aum,60)/1E7",
    "Savers won by month 60 (online + doorstep)": "=SUM(FILTER({p}won,{p}month<=60))",
    "Lens 1 at month 60: 20 x revenue run-rate (₹ crore)": "=INDEX({p}lens1,{p}lens_month)/1E7",
    "Lens 2 at month 60: 0.45 x AUM (₹ crore)": "=INDEX({p}lens2,{p}lens_month)/1E7",
}
KIND = {"EBITDA positive from month (stays at or above 0 from here)": "month", "Active savers, month 60": "count",
        "Savers won by month 60 (online + doorstep)": "count", "Money needed ($ million)": "usd"}
NOTES = {"EBITDA, year 5 (₹ crore)": "Near break-even EBITDA can be small: then read the gap in ₹ crore (column G), not as a %",
         "Money needed: deepest cumulative cash hole + the ₹5 crore cash buffer (₹ crore)":
             "Cumulative cash = PAT with revenue's cash arriving comm_lag (2) months late; Monthly 'Cumulative cash'",
         "EBITDA positive from month (stays at or above 0 from here)": "Gap in months",
         "Lens 1 at month 60: 20 x revenue run-rate (₹ crore)": "$1B = ₹9,500 crore at ₹95; OUR JUDGEMENT multiples (v4 Inputs)"}


def summary_sheet(recon):
    v0 = vt.base_inputs()
    py = {lv: vt.measures(vt.engine_monthly(op.company(lv, 1.0)), v0) for lv in vt.LEVELS}
    cells = {"A1": f"v4 Summary: the live sheet (column B) next to the Python model's {RUN_DATE} run (columns C and D, fixed values)",
             "A2": "Plan level now (online savers won a month from month 30; change it on v4 Inputs)", "B2": f"={P}level",
             "A3": "Growth a year after month 30, now", "B3": f"={P}growth",
             "A4": ("Column E picks the Python value at your plan level when growth is 1.0. The gap (F, G) is meaningful only while every "
                    "other blue input is at its main-case value; the sheet's own error at those values is in the reconciliation below.")}
    fm = {"number": {"B2": "#,##0", "B3": "0.00"}, "bold_rows": [1, 6], "freeze_rows": 0, "wrap_rows": [4, 6],
          "col_widths": {"A": 470, "B": 150, "C": 160, "D": 160, "E": 160, "F": 90, "G": 110, "H": 430}}
    hdr = ["Measure", "Sheet, live (current scenario)", "Python model, 20,000 a month (fixed)", "Python model, 1,50,000 a month (fixed)",
           "Python at the scenario's plan level", "Gap (sheet vs Python, %)", "Gap (sheet - Python)", "Note"]
    for j, h in enumerate(hdr):
        cells[f"{col(j + 1)}6"] = h
    live = {}
    r = 7
    for label, f in SUMMARY_FORMULAS.items():
        cells[f"A{r}"] = label
        cells[f"B{r}"] = n(f)
        live[f"B{r}"] = label
        cells[f"C{r}"], cells[f"D{r}"] = py[20000][label], py[150000][label]
        cells[f"E{r}"] = (f'=IF(AND({P}level=20000,{P}growth=1),C{r},IF(AND({P}level=150000,{P}growth=1),D{r},""))')
        kind = KIND.get(label, "money")
        if kind == "month":
            cells[f"G{r}"] = f'=IFERROR(B{r}-E{r},"")'
            fm["number"][f"G{r}"] = "+0;-0;0"
        else:
            cells[f"F{r}"] = f'=IFERROR((B{r}-E{r})/ABS(E{r}),"")'
            cells[f"G{r}"] = f'=IFERROR(B{r}-E{r},"")'
            fm["number"][f"F{r}"] = "+0.00%;-0.00%;0.00%"
            fm["number"][f"G{r}"] = {"count": "+#,##0;-#,##0;0", "usd": "+0.00;-0.00;0.00"}.get(kind, "+#,##0.000;-#,##0.000;0.000")
        fm["number"][f"B{r}:E{r}"] = {"month": "0", "count": "#,##0", "usd": "0.00"}.get(kind, "#,##0.00")
        if label in NOTES:
            cells[f"H{r}"] = NOTES[label]
        r += 1
    # the $1B check (text)
    cells[f"A{r}"] = "$1B on both lenses at month 60?"
    cells[f"B{r}"] = n('=IF(MIN(INDEX({p}lens1,{p}lens_month),INDEX({p}lens2,{p}lens_month))>=1E9*{p}rs_per_usd,"yes","no")')
    for c_, lv in (("C", 20000), ("D", 150000)):
        l1, l2 = op.lenses(op.company(lv, 1.0))
        cells[f"{c_}{r}"] = "yes" if min(l1, l2) >= op.UNICORN else "no"
    cells[f"E{r}"] = f'=IF(AND({P}level=20000,{P}growth=1),C{r},IF(AND({P}level=150000,{P}growth=1),D{r},""))'
    cells[f"G{r}"] = f'=IF(E{r}="","",IF(B{r}=E{r},"same","differs"))'
    yes_row = r
    # the reconciliation (values)
    r += 2
    cells[f"A{r}"] = (f"Reconciliation at the main case's inputs, {RUN_DATE} (model/v4_toy_check.py, tables/v4_toy_check.csv): the sheet's formulas "
                      "(numpy twin, replayed formula by formula) vs the Python model. Values, fixed.")
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    for j, h in enumerate(["Plan", "Measure", "Sheet", "Python", "Gap", "Gap %", "Target", "Within target"]):
        cells[f"{col(j + 1)}{r}"] = h
    fm["bold_rows"].append(r)
    r += 1
    rec0 = r
    for row in recon:
        if str(row["case"]).startswith("lever"):
            continue
        cells[f"A{r}"] = f"{int(row['case']):,} a month"
        cells[f"B{r}"] = row["measure"].replace("Rs crore", "₹ crore")
        cells[f"C{r}"], cells[f"D{r}"] = row["sheet"], row["python"]
        if row["gap"] != "":
            cells[f"E{r}"] = row["gap"]
        if row["gap_pct"] not in ("", None):
            cells[f"F{r}"] = row["gap_pct"]
        cells[f"G{r}"], cells[f"H{r}"] = text(row["target"]), "yes" if row["ok"] else "NO"
        r += 1
    fm["number"].update({f"C{rec0}:E{r - 1}": "#,##0.000", f"F{rec0}:F{r - 1}": "+0.00%;-0.00%;0.00%"})
    lev = [x for x in recon if str(x["case"]).startswith("lever")]
    r += 1
    cells[f"A{r}"] = (f"Levers (v4 Levers, all at {LVS} a month, typed into v4 Inputs): {sum(x['ok'] for x in lev)} of {len(lev)} "
                      f"checks within target; worst revenue gap {max(abs(x['gap_pct']) for x in lev if 'Revenue' in x['measure']):.2%}, "
                      f"worst year-5 EBITDA gap {max(abs(x['gap']) for x in lev if 'EBITDA, year 5' in x['measure']):.2f} ₹ crore; "
                      + (lambda g: "profit month equal in every lever." if g == 0 else f"profit month within {g:.0f} of the model's in every lever.")(
                          max(abs(x["gap"]) for x in lev if "month" in x["measure"] and not isinstance(x["gap"], str))))
    fm["wrap_rows"].append(r)
    return {"title": "v4 Summary", "cells": cells, "named_ranges": {}, "formats": fm}, live, yes_row


# ---------------------------------------------------------------- value tabs
def read(name):
    return list(csv.DictReader((T / name).open()))


def num(x):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return x
    return int(f) if f.is_integer() and abs(f) < 1e15 else f


def text(s):
    s = re.sub(r"\bRs\b", "₹", re.sub(r"Rs ?(?=\d)", "₹", str(s)))
    return ("'" + s) if s[:1] in "=+-@" else s


LVS = f"{op.LEVER_LEVEL:,}"


def _pc(x):
    """0.2 -> '20%', 0.2415 -> '24.15%', 0.0105 -> '1.05%' (as typed into v4 Inputs)."""
    return f"{round(100 * x, 4):g}%"


TRY_WORDS = {  # v4 Inputs cell -> (words, value in words)
    "on_r12": ("online still saving at month 12", _pc), "on_r3": ("online still saving at month 3", _pc),
    "churn_late": ("both savers' drop-off a month after month 12", _pc),
    "daily": ("daily amount", lambda x: f"₹{x:,.0f}"), "apply": ("apply (personal + business loans)", _pc),
    "approved_first": ("approved, first loan", _pc), "takeup_growth": ("take-up rise a year", _pc),
    "approval_growth": ("approval rise a year", _pc), "loan_reach": ("loan reach (end of v4 Inputs)", lambda x: f"{x:g}"),
    "debit_cost": ("payment cost per debit (end of v4 Inputs)", lambda x: f"₹{x:g}"),
    "debits_month": ("debits a month", lambda x: "52/12 (weekly)" if abs(x - 52 / 12) < 1e-9 else f"{x:g}"),
    "eq_trail": ("our trail on equity SIP balances", _pc), "cac_rs": ("cost to win after the seed", lambda x: f"₹{x:,.0f}"),
    "eq_share": ("equity share", lambda x: f"{x:g} (the SIP cross-sell switches on by itself)" if x == 0 else _pc(x)),
    "door_after": ("doorstep after the test", lambda x: f"{x:g}"),
}
PRODUCT_WORDS = {"loan_gold": "gold loan", "loan_lap": "LAP", "loan_home": "home loan"}


def lever_try(name):
    """'Try it live' text from the very cells the reconciliation types into v4 Inputs (v4_toy_check.LEVER_MAP)."""
    ch = vt.LEVER_MAP[name]
    if not ch:
        return f"Plan level {LVS}; every other input as on v4 Inputs (the main case)"
    parts, prods = [], []
    for k, x in ch.items():
        if k.startswith("takeup:"):
            prods.append(f"{PRODUCT_WORDS.get(k[7:], k[7:])} {_pc(x)}")
        else:
            w, f = TRY_WORDS[k]
            parts.append(f"{w} {f(x)}")
    if prods:
        parts.append("product table take-ups: " + ", ".join(prods))
    return f"Plan level {LVS}; " + "; ".join(parts)


def levers_sheet(recon):
    data = read("ltv_main_levers.csv")
    cols = list(data[0])
    lev = [x for x in recon if str(x["case"]).startswith("lever")]
    worst = max(abs(x["gap_pct"]) for x in lev if "Revenue" in x["measure"])
    pm = max(abs(x["gap"]) for x in lev if "month" in x["measure"] and not isinstance(x["gap"], str))
    missing = sorted(set(r["case"] for r in data) - set(vt.LEVER_MAP))
    assert not missing, f"lever rows the sheet does not replay (v4_toy_check.LEVER_CASES): {missing}"
    cells = {"A1": (f"Levers around the main case at {LVS} online savers a month from month 30 (tables/ltv_main_levers.csv, model/ltv_odds.py, "
                    f"run {RUN_DATE}): one change at a time on top of the main case. Pasted values from the Python model; editing them changes nothing. "
                    "To try one live, type the inputs in the last column into v4 Inputs: the sheet reproduces every lever within "
                    f"{worst:.2%} on revenue and {'the same profit month' if pm == 0 else f'the profit month within {pm:.0f}'} (tables/v4_toy_check.csv).")}
    fm = {"number": {}, "bold_rows": [1, 2], "freeze_rows": 2, "freeze_cols": 1, "wrap_rows": [1, 2],
          "col_widths": {"A": 330, col(len(cols) + 1): 520}}
    for j, h in enumerate(cols + ["Try it live on v4 Inputs"]):
        cells[f"{col(j + 1)}2"] = text(h)
    for i, row in enumerate(data, start=3):
        for j, c_ in enumerate(cols):
            val = row[c_]
            cells[f"{col(j + 1)}{i}"] = (text(val) if j == 0 else ("yes" if val == "True" else "no" if val == "False" else num(val)))
        cells[f"{col(len(cols) + 1)}{i}"] = lever_try(row["case"])
    fm["number"][f"B3:{col(len(cols))}{len(data) + 2}"] = "#,##0.0##"
    mc_ = col(1 + cols.index("money needed $M"))
    for i, row in enumerate(data, start=3):           # money needed '+' (at least) while the company still loses money at month 96
        if row["EBITDA positive from month"] == "after m96":
            fm["number"][f"{mc_}{i}"] = '#,##0.0"+"'
    return {"title": "v4 Levers", "cells": cells, "named_ranges": {}, "formats": fm}


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _x(v):
    """LTV/CAC at 2 decimals, e.g. 0.78×."""
    return f"{float(v):.2f}×"


def _pct_words(x):
    """0.35 -> '35%', 0.349445 -> '34.9%', 0.4123 -> '41.2%'."""
    x = 100 * float(x)
    return f"{x:.0f}%" if abs(x - round(x)) < 0.05 else f"{x:.1f}%"


def _month(v, never="not by month 96"):
    """97 = not by month 96 (ltv_odds.py's code) -> words; else the month as a number."""
    f = _f(v)
    return never if f is None or f >= 97 else int(round(f))


def human_params(s):
    """'r12 0.4123; churn_late 0.015' / 'daily 125.6 (beyond the upside)' / 'not reachable' -> words for the sheet."""
    if s.strip() == "not reachable":
        return "not reachable"
    beyond = " (beyond the upside)" if "(beyond the upside)" in s else ""
    s = s.replace(" (beyond the upside)", "")
    kv = {}
    for part in s.split(";"):
        p, v = part.strip().rsplit(" ", 1)
        kv[p] = float(v)
    out = []
    if "daily" in kv:
        out.append(f"₹{kv['daily']:,.0f} a day")
    if "r12" in kv:
        out.append(f"{_pct_words(kv['r12'])} still saving at 12 months")
    if "churn_late" in kv:
        out.append(f"drop-off after {_pct_words(kv['churn_late'])} a month")
    if "_apply" in kv:
        out.append(f"{_pct_words(kv['_apply'])} apply for a loan a year")
    if "approved_first" in kv:
        out.append(f"{_pct_words(kv['approved_first'])} of first loans approved")
    if "takeup_growth" in kv or "approval_growth" in kv:
        tg, ag = kv.get("takeup_growth", 0.0), kv.get("approval_growth", 0.0)
        out.append("no yearly rises" if tg == 0 and ag == 0 else f"take-up +{_pct_words(tg)} and approval +{_pct_words(ag)} a year")
    if "_debt_trail" in kv:
        out.append(f"debt fund fee {100 * kv['_debt_trail']:.2f}%")
    return ", ".join(out) + beyond


def _range_words(params):
    """A drawn input's range in words: {'r12': (0.30, 0.40), 'churn_late': (0.025, 0.015)} -> '30% to 40%, drop-off after 2.5% to 1.5% a month'."""
    out = []
    for p, (a, b) in params.items():
        if p == "r12":
            out.append(f"{_pct_words(a)} to {_pct_words(b)}")
        elif p == "churn_late":
            out.append(f"drop-off after {_pct_words(a)} to {_pct_words(b)} a month")
        elif p.endswith("_trail"):
            out.append(f"{100 * a:.2f}% to {100 * b:.2f}% a year")
        else:
            out.append(f"{p.lstrip('_')} {a:g} to {b:g}")
    return ", ".join(out)


def _share(x):
    """A share of the 1,000 draws in words: 0.003 -> '0.3%', 0.903 -> '90%'."""
    x = float(x)
    return f"{x:.1%}" if 0 < x < 0.01 else f"{x:.0%}"


def _minus(s):
    return s.replace("-", "−")


def headline():
    """The headline numbers, read from the tables (never retyped): the main case's split, the Monte Carlo, the ladder, the levers.
    Wording rules (reviews/2026-10-24_rebase/FIXES.md section B): cross-sell in rupees, before and after serving; the cost to win is
    the founders' figure; shares of the 1,000 draws, not chances; money needed '+' while the company still loses money at month 96."""
    summ = {r["measure"]: r for r in read("ltv_odds_summary.csv")}
    sp = {(r["case"], r["years"]): r for r in read("ltv_saver_split.csv")}
    lad = {r["rung"]: r for r in read("ltv_ladder.csv")}
    ups = {r["lever"]: r for r in read("ltv_upside_levers.csv")}
    lev = {r["case"]: r for r in read("ltv_main_levers.csv")}
    sl = {r["case"]: r for r in read("online_ltv_levers.csv")}          # one saver at each lever
    br = read("ltv_bridge.csv")
    m5, m8 = sp[("Main case", "5y")], sp[("Main case", "8y")]
    s = lambda k, q="P50": summ[k][q]
    losing = float(s("chance EBITDA positive by month 96")) == 0      # every draw still loses money at month 96
    plus = "+" if losing else ""
    rs = lambda v: f"₹{float(v):,.0f}"
    xn5, xn8 = _minus(_x(m5["cross-sell net of serving / CAC"])), _minus(_x(m8["cross-sell net of serving / CAC"]))
    v = vt.base_inputs()
    h = {"l5": _x(m5["LTV/CAC"]), "l8": _x(m8["LTV/CAC"]), "x5": _x(m5["cross-sell / CAC"]), "x8": _x(m8["cross-sell / CAC"]),
         "xn5": xn5, "xn8": xn8, "xn": xn5 if xn5 == xn8 else f"{xn5} in 5 years, {xn8} in 8",
         "xs5": rs(m5["cross-sell"]), "xs8": rs(m8["cross-sell"]), "sv5": rs(m5["serving"]), "sv8": rs(m8["serving"]),
         "f5": _x(m5["fund fees / CAC"]), "f8": _x(m8["fund fees / CAC"]),
         "cac": rs(m5["cost to win"]), "cac0": rs(op.CAC), "seed_cac": rs(op.SEED_CAC), "pb": _month(lad["Main case"]["saver pays back in month"]),
         "l5_p10": f"{float(s('LTV/CAC, 5 years', 'P10')):.2f}", "l5_p90": _x(s("LTV/CAC, 5 years", "P90")),
         "l8_p10": f"{float(s('LTV/CAC, 8 years', 'P10')):.2f}", "l8_p90": _x(s("LTV/CAC, 8 years", "P90")),
         "ch1_5": _share(s("chance LTV/CAC >= 1")), "ch1_8": _share(s("chance 8-year LTV/CAC >= 1")),
         "pb_p10": _month(s("Saver pays back in month (97 = not by 96)", "P10")),
         "pb_p90": _month(s("Saver pays back in month (97 = not by 96)", "P90")),
         "money": f"${float(s('Money needed, $M')):.1f}M{plus}", "money_p10": f"${float(s('Money needed, $M', 'P10')):.1f}M",
         "money_p90": f"${float(s('Money needed, $M', 'P90')):.1f}M", "plus": plus, "losing": losing,
         "ebitda96": float(s("chance EBITDA positive by month 96")), "cum8": float(s("Cumulative EBITDA to month 96, Rs crore")),
         "bridge0": _x(br[0]["LTV/CAC 5y"]), "bridge1": _x(br[-1]["LTV/CAC 5y"]),
         "d1": ups["daily"]["alone for 1x (5y)"], "r1": ups["keep_up"]["alone for 1x (5y)"],
         "three": "3×" in lad, "lad": lad,
         # the two unconfirmed inputs and the cost to win, one saver at each lever (tables/online_ltv_levers.csv)
         "debit2": _x(sl["We pay Rs 2 a debit, weekly"]["LTV/CAC 60m"]), "fee05": _x(sl["Equity fund fee 0.5%, not 0.75%"]["LTV/CAC 60m"]),
         "cac600_5": _x(sl["Cost to win Rs 600 (our funnel)"]["LTV/CAC 60m"]), "cac600_8": _x(sl["Cost to win Rs 600 (our funnel)"]["LTV/CAC 96m"]),
         "cac600_rs": rs(sl["Cost to win Rs 600 (our funnel)"]["cost to win Rs"]),
         "cac600_money": f"${float(lev['Cost to win Rs 600 (our funnel)']['money needed $M']):.1f}M"
                         + ("+" if lev["Cost to win Rs 600 (our funnel)"]["EBITDA positive from month"] == "after m96" else ""),
         "old5": _x(sl["Loan funnel at our old targets"]["LTV/CAC 60m"]),
         "old_pm": lev["Loan funnel at our old targets"]["EBITDA positive from month"].replace("after m96", "after month 96"),
         "blend": f"{100 * (v['eq_share'] * v['eq_trail'] + (1 - v['eq_share']) * v['debt_trail']):.2f}%"}
    h["ebitda_words"] = ("is not EBITDA positive by month 96 in any of the 1,000 draws" if h["ebitda96"] == 0 else
                         f"is EBITDA positive by month 96 in only {_share(h['ebitda96'])} of the 1,000 draws")
    p0 = lambda x: f"{float(x):.0%}"
    h["d1w"] = human_params(h["d1"]).split(",")[0]
    h["r1w"] = f"{_pct_words(h['r1'].split()[1])} still saving at 12 months"
    two = lad.get("2×")
    h["two"] = (f"2× needs {human_params('daily ' + two['saved a day Rs'])}, {p0(two['still saving at 12 months'])} still saving, "
                f"{p0(two['apply a year'])} applying for a loan a year and {p0(two['first loans approved'])} of first loans approved; "
                f"the company then turns EBITDA positive from month {_month(two['EBITDA positive from month'])} on "
                f"${float(two['money needed $M']):.1f}M") if two else "2× is not reachable on these levers"
    three = lad.get("3×")
    h["three_words"] = (f"3× needs {human_params('daily ' + three['saved a day Rs'])}, {p0(three['still saving at 12 months'])} still saving, "
                        f"{p0(three['apply a year'])} applying and {p0(three['first loans approved'])} approved (EBITDA positive from month "
                        f"{_month(three['EBITDA positive from month'])}, ${float(three['money needed $M']):.1f}M)") if three else \
        "3× is out of reach on these levers"
    # FIXES.md B1: the cross-sell answer in rupees, before and after serving
    h["cross"] = (f"Cross-selling alone (loans and cards): {h['xs5']} per saver in 5 years, {h['xs8']} in 8. That is {h['x5']} and {h['x8']} "
                  f"of the {h['cac']} it costs to win a saver, and less than the {h['sv5']} / {h['sv8']} it costs to serve them, so on its "
                  f"own it never pays back ({h['xn']} after serving). Insurance, recharge, bills, FD and NPS are not counted.")
    h["with_funds"] = (f"With fund fees, {h['l5']} in 5 years and {h['l8']} in 8; pays back "
                       + (f"in month {h['pb']}." if isinstance(h["pb"], int) else "after month 96."))
    # B2: the cost to win
    h["cac_words"] = (f"{h['cac0']} at scale (the founders' figure; they call it 'fairly sorted') plus the 10% contingency = {h['cac']}. "
                      f"The seed budgets {h['seed_cac']} while the brand is new, and measures it.")
    # B3: unconfirmed inputs
    h["unconfirmed"] = (f"Assumes debits cost us ₹0 and a {100 * v['eq_trail']:.2f}% equity fund fee, both still to be confirmed in writing "
                        f"(₹2 a weekly debit would cut a saver to about {h['debit2']} at 5 years, a 0.5% fee to about {h['fee05']}).")
    # B4 / B5-B7: the four facts
    h["facts"] = (f"The four facts that decide it, all cheap to get: Bachatt's average daily amount; Bachatt's exact 12-month retention; the "
                  f"₹0 debit cost in writing (BSE StAR MF or the fund houses); the fee on the fund the ₹100 goes into, in writing "
                  f"({h['blend']} blended or better: the model uses {v['eq_share']:.0%} equity at {100 * v['eq_trail']:.2f}% and the rest "
                  f"in debt at {100 * v['debt_trail']:.2f}%, and daily minimums of ~₹100 a scheme likely mean one hybrid fund).")
    h["glossary"] = ("Words: LTV/CAC = what a saver brings in over 5 or 8 years, less the cost of serving them, divided by what it costs to "
                     "win them. EBITDA = operating profit before interest, tax and depreciation. KYC'd = identity-checked. SIP = a regular "
                     "investment into a mutual fund (here daily). Mandate = the saver's standing instruction for the debit. The Monte Carlo = "
                     "we ran the model 1,000 times, picking retention and the debt fund's fee at random within their ranges; the median is "
                     "the middle run, and P10-P90 is the range 8 in 10 runs fall in. Money needed = the seed + the deepest cash hole (fees "
                     "arrive 2 months late) + a ₹5 crore cash buffer, at ₹95 = $1; '+' = at least, as the company is still losing money "
                     "at month 96.")
    return h


LADDER_COLS = [("rung", "Rung", None), ("upside position (0 main case, 1 all upside)", "Share of the way to the upside (0 = main case)", "0%"),
               ("saved a day Rs", "Saved a day, ₹", "#,##0"), ("still saving at 12 months", "Still saving at 12 months", "0.0%"),
               ("apply a year", "Apply for a loan a year", "0.0%"), ("first loans approved", "First loans approved", "0.0%"),
               ("rises", "Yearly rises: take-up / approval", None), ("LTV/CAC 5y", "LTV/CAC, 5 years", "0.00"),
               ("LTV/CAC 8y", "LTV/CAC, 8 years", "0.00"), ("saver pays back in month", "Saver pays back in month", "0"),
               ("chance of at least this", "Share of the 1,000 draws at least this high (everything else at the main case)", "0.0%"),
               ("EBITDA positive from month", "Company EBITDA positive from month", "0"), ("money needed $M", "Money needed, $M ('+' = at least: still losing money at month 96)", "0.00"),
               ("cumulative EBITDA 8y Rs cr", "Cumulative EBITDA, 8 years, ₹ crore", "#,##0.0")]
SPLIT_ROWS = [("Fund fees", "Fund fees (₹)", "rs"), ("Loans (all referrals)", "Loans: every referral (₹)", "rs"), ("Cards", "Cards (₹)", "rs"),
              ("Insurance", "Insurance (₹; a fixed referral fee, not counted)", "rs"),
              ("Other products", "Other products (₹; recharge, bills, FD and NPS are not in the launch app)", "rs"),
              ("cross-sell", "Cross-sell: loans + cards + insurance + other products (₹)", "rs"),
              ("serving", "Serving: support, tech, payments, with the 10% contingency (₹)", "neg"),
              ("net", "LTV: fund fees + cross-sell - serving (₹)", "rs"),
              ("cost to win", "Cost to win, with the 10% contingency (₹)", "rs"), ("LTV/CAC", "LTV/CAC", "x"),
              ("fund fees / CAC", "Fund fees alone / cost to win (before serving)", "x"),
              ("cross-sell / CAC", "Cross-sell alone / cost to win (before serving)", "x"),
              ("cross-sell net of serving / CAC", "Cross-sell after serving / cost to win", "x")]
SPLIT_CASES = [("Main case", "Main case"), ("Low end (30% still saving)", "Low end (30% still saving)"),
               ("High end (40% still saving)", "High end (40% still saving)")]


def mc_sheet():
    summ, lad, drv = read("ltv_odds_summary.csv"), read("ltv_ladder.csv"), read("ltv_odds_drivers.csv")
    sp = {(r["case"], r["years"]): r for r in read("ltv_saver_split.csv")}
    br, ups = read("ltv_bridge.csv"), read("ltv_upside_levers.csv")
    h = headline()
    t = vt.MAIN_T
    drawn = "; ".join(f"{lab.split(' (')[0].lower()} ({_range_words(params)})" for lab, params in lo.INPUTS.values())
    cells = {"A1": (f"The LTV/CAC Monte Carlo (model/ltv_odds.py, run {RUN_DATE}): we ran the model {lo.N:,} times (Latin-hypercube draws, seed "
                    f"{lo.SEED}), picking the two still-uncertain inputs at random, each equally likely anywhere in its range: {drawn}. "
                    "Everything else is fixed by the founders (market figures, Bachatt, or our judgement; v4 README). The cost to win is held: "
                    f"{h['cac_words']} Each draw runs one online saver and the company at {lo.LEVEL:,} online savers a month. "
                    "The main case on v4 Inputs is the median. Pasted values, not live."),
             "A2": (f"The main case. {h['cross']} {h['with_funds']} At market numbers this is a fund-fee business; loans are a small add-on. "
                    f"The company {h['ebitda_words']}; money needed {h['money']} (8 in 10 draws {h['money_p10']}-{h['money_p90']}; at least, "
                    f"because the cash hole is still deepening at month 96). {h['unconfirmed']}")}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 0, "wrap_rows": [1, 2],
          "col_widths": {"A": 420, **{col(j): 130 for j in range(2, 15)}}}
    r = 4
    # 1. across the draws
    cells.update({f"A{r}": f"Across the {lo.N:,} draws (8 in 10 fall between P10 and P90)", f"B{r}": "P10", f"C{r}": "P50 (median)", f"D{r}": "P90"})
    fm["bold_rows"].append(r)
    r += 1
    for x in summ:
        lab = x["measure"].replace(" (97 = not by 96)", "").replace(">=", "≥")
        if lab.startswith("chance "):
            lab = "Share of the 1,000 draws with " + lab[len("chance "):] + (" at 5 years" if lab.startswith("chance LTV/CAC") else "")
        if lab.startswith("Money needed") and h["losing"]:
            lab += " (at least: still losing money at month 96)"
        cells[f"A{r}"] = text(lab)
        if x["P10"] != "":
            if "month" in x["measure"] and "97" in x["measure"]:
                cells.update({f"{c_}{r}": _month(x[q]) for c_, q in (("B", "P10"), ("C", "P50"), ("D", "P90"))})
                fm["number"][f"B{r}:D{r}"] = "0"
            else:
                cells.update({f"B{r}": num(x["P10"]), f"C{r}": num(x["P50"]), f"D{r}": num(x["P90"])})
                fm["number"][f"B{r}:D{r}"] = ('0.00"+"' if "$M" in x["measure"] and h["losing"] else
                                              "0.00" if "LTV/CAC" in x["measure"] or "$M" in x["measure"] else "#,##0.00")
        else:
            cells[f"C{r}"] = num(x["P50"])
            fm["number"][f"C{r}"] = "0.0%"
        r += 1
    # 2. one saver: where the money comes from
    r += 1
    cells[f"A{r}"] = ("One online saver won: where the money comes from (tables/ltv_saver_split.csv). The main case and the two ends of the "
                      "drawn range of still saving at 12 months; ₹ per saver won, undiscounted")
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    hdr = ["Line"] + [f"{nm}, {y}" for _k, nm in SPLIT_CASES for y in ("5 years", "8 years")]
    for j, hh in enumerate(hdr):
        cells[f"{col(j + 1)}{r}"] = hh
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    for key, lab, kind in SPLIT_ROWS:
        cells[f"A{r}"] = text(lab)
        j = 2
        for ck, _nm in SPLIT_CASES:
            for y in ("5y", "8y"):
                v = float(sp[(ck, y)][key])
                cells[f"{col(j)}{r}"] = num(round(-v if kind == "neg" else v, 3 if kind == "x" else 0)) + 0
                j += 1
        fm["number"][f"B{r}:G{r}"] = "0.00" if kind == "x" else "#,##0;-#,##0;0"
        if key in ("net", "LTV/CAC", "cross-sell / CAC"):
            fm["bold_rows"].append(r)
        r += 1
    # 3. the bridge
    r += 1
    cells[f"A{r}"] = (f"From the 23 October {h['bridge0']} to {h['bridge1']} today: a correction, then the founders' 24 Oct decisions, one at a time "
                      "(tables/ltv_bridge.csv, model/ltv_bridge.py)")
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    for j, hh in enumerate(["Step", "LTV/CAC, 5 years", "Change, 5 years", "LTV/CAC, 8 years", "Change, 8 years", "Saver pays back in month"]):
        cells[f"{col(j + 1)}{r}"] = hh
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    b0 = r
    for x in br:
        cells[f"A{r}"] = text(x["step"] + (" (to confirm in writing)" if x["step"].startswith("Debits at") else ""))
        cells[f"B{r}"], cells[f"D{r}"] = num(x["LTV/CAC 5y"]), num(x["LTV/CAC 8y"])
        if x["change 5y"] != "":
            cells[f"C{r}"], cells[f"E{r}"] = num(x["change 5y"]), num(x["change 8y"])
        cells[f"F{r}"] = _month(x["saver pays back in month"])
        r += 1
    fm["number"].update({f"B{b0}:B{r - 1}": "0.00", f"D{b0}:D{r - 1}": "0.00", f"C{b0}:C{r - 1}": "+0.00;-0.00;0.00",
                         f"E{b0}:E{r - 1}": "+0.00;-0.00;0.00", f"F{b0}:F{r - 1}": "0"})
    # 4. the ladder
    r += 1
    up1 = lad[-1] if lad[-1]["rung"] == "All upside" else next(x for x in lad if x["rung"] == "All upside")
    cells[f"A{r}"] = ("What it takes (tables/ltv_ladder.csv): from the main case, the five upside levers move together the same share of the "
                      f"way to their upside (all upside: {human_params('daily ' + up1['saved a day Rs'])}, "
                      f"{_pct_words(up1['still saving at 12 months'])} still saving (drop-off {_pct_words(up1['drop-off a month after 12'])} a month), "
                      f"{_pct_words(up1['apply a year'])} apply, {_pct_words(up1['first loans approved'])} approved, take-up +"
                      f"{_pct_words(up1['take-up rise a year'])} and approval +{_pct_words(up1['approval rise a year'])} a year: the loan funnel "
                      "at our old targets). The low and high ends move only the drawn still saving. Not other plans: what each multiple needs."
                      + ("" if h["three"] else " 3× is not reachable on these levers."))
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    for j, (_k, hh, _f) in enumerate(LADDER_COLS):
        cells[f"{col(j + 1)}{r}"] = hh
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    l0 = r
    for x in lad:
        for j, (k, _hh, _f) in enumerate(LADDER_COLS):
            c_ = f"{col(j + 1)}{r}"
            if k == "rung":
                cells[c_] = text(x[k])
            elif k == "rises":
                tg, ag = float(x["take-up rise a year"]), float(x["approval rise a year"])
                cells[c_] = "none" if tg == 0 and ag == 0 else f"{100 * tg:.1f}% / {100 * ag:.1f}%"
            elif k in ("saver pays back in month", "EBITDA positive from month"):
                cells[c_] = _month(x[k])
            else:
                cells[c_] = num(x[k])
        if x["rung"] == "Main case":
            fm["bold_rows"].append(r)
        r += 1
    for j, (_k, _hh, f_) in enumerate(LADDER_COLS):
        if f_:
            fm["number"][f"{col(j + 1)}{l0}:{col(j + 1)}{r - 1}"] = f_
    mcol = col(1 + [k for k, _hh, _f in LADDER_COLS].index("money needed $M"))
    for i, x in enumerate(lad):                       # money needed '+' (at least) while the company still loses money at month 96
        if _month(x["EBITDA positive from month"]) == "not by month 96":
            fm["number"][f"{mcol}{l0 + i}"] = '0.00"+"'
    # 5. the upside levers one at a time
    r += 1
    cells[f"A{r}"] = ("Each upside lever alone, from the main case (tables/ltv_upside_levers.csv): its LTV/CAC at the upside, and what it needs "
                      "on its own for 1× and 2× at 5 years")
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    for j, hh in enumerate(["Lever", "Main case", "Upside", "LTV/CAC, 5 years, at the upside alone", "LTV/CAC, 8 years, at the upside alone",
                            "Saver pays back in month, at the upside alone", "Alone for 1× at 5 years", "Alone for 2× at 5 years"]):
        cells[f"{col(j + 1)}{r}"] = hh
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    u0 = r
    for x in ups:
        cells.update({f"A{r}": text(x["label"]), f"B{r}": human_params(x["main case"]), f"C{r}": human_params(x["upside"]),
                      f"D{r}": num(x["LTV/CAC 5y at the upside alone"]), f"E{r}": num(x["LTV/CAC 8y at the upside alone"]),
                      f"F{r}": _month(x["pays back in month at the upside alone"]), f"G{r}": human_params(x["alone for 1x (5y)"]),
                      f"H{r}": human_params(x["alone for 2x (5y)"])})
        r += 1
    fm["number"].update({f"D{u0}:E{r - 1}": "0.00", f"F{u0}:F{r - 1}": "0"})
    # 6. the drawn inputs and what pinning each is worth
    r += 1
    cells[f"A{r}"] = (f"The {len(lo.INPUTS)} drawn inputs (model/ltv_odds.py INPUTS) and what measuring each is worth (tables/ltv_odds_drivers.csv): "
                      f"the same {lo.N:,} draws with one input at its low end, then its high end; the other still drawn")
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    for j, hh in enumerate(["Input", "Key", "Low end", f"Main case ({t:.0%} of the way)", "High end", "Median LTV/CAC (5 years) if at the low end",
                            "Median LTV/CAC (5 years) if at the high end", "Rank correlation with LTV/CAC"]):
        cells[f"{col(j + 1)}{r}"] = hh
    fm["bold_rows"].append(r)
    fm["wrap_rows"].append(r)
    r += 1
    d0 = r
    dv = {x["input"]: x for x in drv}
    for k, (lab, params) in lo.INPUTS.items():
        words = lambda pos: human_params("; ".join(f"{p} {a + (b - a) * pos:g}" for p, (a, b) in params.items()))
        cells.update({f"A{r}": text(lab), f"B{r}": k, f"C{r}": words(0.0), f"D{r}": words(t), f"E{r}": words(1.0),
                      f"F{r}": num(dv[k]["median if low"]), f"G{r}": num(dv[k]["median if high"]), f"H{r}": num(dv[k]["rank corr with LTV/CAC"])})
        r += 1
    fm["number"].update({f"F{d0}:H{r - 1}": "0.00"})
    return {"title": "v4 Monte Carlo", "cells": cells, "named_ranges": {}, "formats": fm}


# ---------------------------------------------------------------- v4 README
def founders_inputs_words():
    """The 24 Oct founders' inputs as the sheet carries them (v4 Inputs values, never retyped)."""
    v, x = vt.base_inputs(), vt.X_ON
    lakh = lambda rs: f"₹{rs / 1e5:g} lakh"
    return (f"personal and business loans ₹{v['ticket']:,.0f} for a first loan (Bachatt's number), repeats {v['ticket_growth']:.0%} bigger "
            f"for each year repaid, plus top-ups; {_pct_words(v['apply'] / op.LOAN_MIX['apply'])} of reachable users apply for a loan a year and "
            f"{_pct_words(v['approved_first'])} of first applications are approved (the founders' market figure, between 11% and 25%; gold "
            f"loans {op.GOLD_APPROVAL:.0%}, home and property {x['loan_home_approval']:.0%}), "
            + ("no yearly rises" if v["takeup_growth"] == 0 and v["approval_growth"] == 0 else
               f"take-up +{_pct_words(v['takeup_growth'])} and approval +{_pct_words(v['approval_growth'])} a year")
            + f"; home loans {lakh(x['loan_home_ticket'])} and property loans {lakh(x['loan_lap_ticket'])} (market sizes); lender payout "
            f"{_pct_words(v['fee'])}" + (" flat" if v["fee_mult_end"] == 1 else f" rising {v['fee_mult_end']:.2f}x by month 60")
            + f"; KYC'd non-savers fade within ~3 months (loan reach {v['loan_reach']:.2f}); recharge, bills, FD and NPS off (not in the launch "
            f"app); debits ₹{v['debit_cost']:g} to us through BSE StAR MF or the fund house (still to be confirmed in writing); equity fund "
            f"fee {100 * v['eq_trail']:.2f}% (still to be confirmed in writing); ₹{v['daily']:,.0f} a day, our product's floor (Bachatt's "
            "average is unknown, and its own minimums are lower: ₹51 / ₹101 a day, ₹20 for its liquid fund)")


def founders_inputs_short():
    v, x = vt.base_inputs(), vt.X_ON
    return (f"₹{v['ticket'] / 1000:.0f}k first loans, {v['apply'] / op.LOAN_MIX['apply']:.0%} apply and {v['approved_first']:.0%} approved, "
            f"home ₹{x['loan_home_ticket'] / 1e5:g} lakh and property ₹{x['loan_lap_ticket'] / 1e5:g} lakh, lender payout {v['fee']:.0%} flat, "
            f"debits ₹{v['debit_cost']:g}, no recharge, bills, FD or NPS")


def recon_words(recon):
    """The README's reconciliation sentence: equal at the main case (no yearly rises), the levers' worst gap named."""
    base = [r for r in recon if not str(r["case"]).startswith("lever")]
    lev = [r for r in recon if str(r["case"]).startswith("lever")]
    worst = max((r for r in lev if "Revenue" in r["measure"]), key=lambda r: abs(r["gap_pct"]))
    num_gap = max(abs(r["gap_pct"]) for r in base if r["gap_pct"] not in ("", None))
    months = all(r["ok"] for r in base if "month" in r["measure"])
    head = ("Equal to the Python model at 20,000 and 1,50,000 a month: revenue and EBITDA in every year, money needed, active savers, "
            "AUM and the lens at month 60 (largest gap {}); the profit month {}. The main case has no yearly rises, so the sheet's one "
            "approximation (calendar growth) does not bite.".format("under 0.01%" if num_gap < 1e-4 else f"{num_gap:.2%}",
                                                                   "the same" if months else "differs: see v4 Summary"))
    return (head + f" The {len(vt.LEVER_MAP)} levers: {sum(x['ok'] for x in lev)} of {len(lev)} checks within target; worst revenue gap "
            f"{abs(worst['gap_pct']):.2%} ({text(worst['case'].replace('lever: ', ''))}).")


def readme_sheet(recon, counts, n_names):
    rec = {(r["case"], r["measure"]): r for r in recon}
    g = lambda lv, ms: rec[(lv, ms)]
    pct = lambda lv, ms: f"{g(lv, ms)['gap_pct']:+.2%}"
    yr_rev = max(abs(r["gap_pct"]) for r in recon if not str(r["case"]).startswith("lever") and r["measure"].startswith("Revenue, year"))
    pm = lambda lv, k: (lambda s_: f"month {s_:.0f}" if not isinstance(s_, str) else s_.replace("after m96", "after month 96"))(g(lv, "EBITDA positive from month")[k])
    lev = [x for x in recon if str(x["case"]).startswith("lever")]
    h = headline()
    L = [
        (f"v4: the online-first plan, live (the main case, {RUN_DATE})", "bold"),
        ("The 'v4' tabs mirror model/online_plan.py (company() and saver_inputs()) at the MAIN CASE, the only case. On 24 Oct the founders "
         "questioned every input of a saver's value; two are still uncertain, still saving at 12 months (Bachatt's 30-40%) and our share of "
         "the debt fund's fee, and sit at the median of the LTV/CAC Monte Carlo (model/ltv_odds.py, v4 Monte Carlo). Everything else is "
         f"fixed by the founders (market figures, Bachatt, or our judgement). Cost to win: {h['cac_words']} The ladder and the levers show "
         "what it takes; they are not other plans. Savers won online pan-India (₹100 a day, our product's floor; 80% equity SIP / 20% debt), "
         f"1 in 10 from doorstep agents in NCR, 96 months, 8 years. Built {RUN_DATE}. {h['glossary']}", ""),
        (f"THE ANSWER (main case; v4 LTV live, v4 Monte Carlo). {h['cross']} {h['with_funds']} At market numbers this is a fund-fee "
         f"business; loans are a small add-on. All three loan numbers at our old targets together (lever 'Loan funnel at our old targets') "
         f"give about {h['old5']} at 5 years and bring profit from month {h['old_pm']}, because loan fees arrive early while fund fees build slowly. "
         f"The company at {lo.LEVEL:,} online savers a month {h['ebitda_words']}; money needed {h['money']} (at least: the cash "
         f"hole is still deepening at month 96). What it takes: {h['d1w']} alone, or {h['r1w']} alone, takes a saver to 1× at 5 years; no "
         f"single loan lever does. {h['two']}. {h['three_words'][0].upper() + h['three_words'][1:]}. {h['unconfirmed']}", ""),
        (f"24 OCT FOUNDERS' INPUTS (each a blue cell on v4 Inputs, its source in column D): {founders_inputs_words()}. Kept from 22 Oct: a 10% "
         "contingency on every cost line, serving included; support ₹5 a month per saver still saving and tech ₹4 a month per KYC'd user "
         f"reached (only the tech scales with the loan reach); insurance not counted. Cost to win ₹600: {h['cac600_rs']} with the "
         f"contingency, a saver about {h['cac600_5']} / {h['cac600_8']} at 5 / 8 years and the company {h['cac600_money']}. {h['facts']}", ""),
        ("The OLDER tabs (Inputs, Per saver, Monthly, Summary, Assumptions, Monte Carlo, Sign-ups, Agent pay, Sensitivity and the "
         "Company / City tabs) are the SUPERSEDED street-fleet model of 16-18 Oct. They are HIDDEN since 22 Oct (View > Hidden sheets "
         "to see them); do not use them for the plan. No v4 formula reads them, and no v4 name clashes with theirs (every v4 name "
         "starts with v_).", ""),
        ("", ""),
        ("How to use it", "bold"),
        ("1. Change the BLUE cells on 'v4 Inputs'. The three scenario cells are at the top: online savers won a month from month 30 "
         "(20,000 = the main case; 1,50,000 = grow fast), growth a year after month 30 (1.0 = flat; 1.2 = +20% a year), and "
         "doorstep after the 18-month test (1 = yes, 0 = online only). Per saver, Monthly, Yearly, Summary and v4 LTV recalculate.", ""),
        ("2. Grey cells are worked out from the blue ones; do not type there, or anywhere on Per saver, Monthly or Yearly.", ""),
        (f"3. 'v4 Summary' puts the live answer next to the Python model's {RUN_DATE} run at 20,000 and 1,50,000 a month (fixed values). "
         "Column E picks the Python value at your plan level (growth 1.0); the gap is meaningful while the other inputs are at the "
         "main case's values.", ""),
        (f"4. To try a lever (v4 Levers), type the inputs in its last column into v4 Inputs; the sheet reproduces each of the {len(vt.LEVER_MAP)} "
         "levers, the ₹2 debit and the 0.5% fund fee included.", ""),
        ("", ""),
        ("Tabs", "bold"),
        ("v4 Inputs: every input with its value, unit and source (blue), the worked-out values (grey) and the 19 cross-sell products.", ""),
        ("v4 Per saver: one saver's months 1-96. For the online and the doorstep saver: still saving, deposits, balance, fund trail, "
         "loan fees, cards, insurance, other products, serving (support, tech, payments) and cumulative revenue less serving. To the right, the machinery "
         "shared by both savers (per active saver): the fund balance, the loan states, top-ups, cards and every product's take-ups "
         "and money.", ""),
        ("v4 Monthly: months 1-96: savers won (online path, pool cap, doorstep agents and their ramp), active savers, AUM, revenue "
         "by line, acquisition, the team by role, other costs, EBITDA, tax after losses carried forward, PAT, cumulative cash, the "
         "two lenses and each product's money.", ""),
        ("v4 Yearly: years 1-8 (SUMIFS on Monthly), ₹ crore.", ""),
        ("v4 Summary: the headline measures, live, next to the Python run; the reconciliation table. v4 LTV: one saver won, live: the "
         "cost to win, each product line, serving, LTV/CAC at 5 and 8 years, cross-selling alone and the payback month.", ""),
        ("v4 Levers, v4 Monte Carlo: pasted values from the Python model (tables/ltv_main_levers.csv; ltv_odds_summary.csv, "
         "ltv_saver_split.csv, ltv_bridge.csv, ltv_ladder.csv, ltv_upside_levers.csv, ltv_odds_drivers.csv), "
         f"run {RUN_DATE}. They do not move.", ""),
        ("", ""),
        ("How the sheet works", "bold"),
        ("Per active saver: every line except 'still saving' is the same for the online and the doorstep saver (take-ups, loan states "
         "and cross-sell all scale with still saving in the Python engine), so Per saver works it once, and each saver's lines are "
         "his still-saving curve x those per-active lines.", ""),
        ("Cohorts: each Monthly line = the sum over every month's savers won of (still saving at their age x the per-active line at "
         "that age): one MMULT of a 96 x 96 matrix (month x age) per line, online and doorstep savers together.", ""),
        ("Products: each of the 19 products is worked in closed form: take-ups = never-held x the monthly hazard (early factor in his "
         "months 1-6; home loans and LAP x approval), money = take-ups x the kind's rule (commission at take-up, renewals each year, "
         "the Choti bonus at month 24, monthly holdings for gold, recharge and bills).", ""),
        ("", ""),
        ("Simplifications (each measured against the Python model; model/v4_toy_check.py)", "bold"),
        ("1. Calendar growth. The main case has no yearly rises in take-up or approval (founders 24 Oct), so the sheet is exact there. "
         "With rises on (the 'Loan funnel at our old targets' lever, the ladder's upside) Python gives every month's cohort its own "
         "profile; the sheet computes one profile at the held year (exact for every cohort from month 49) and scales each month by that "
         "month's factor relative to the held year: take-up for insurance and other products, take-up x approval for loan fees, cards, "
         "home loans and LAP.", ""),
        ("2. Timing of the later money: money booked at take-up takes this month's factor; insurance renewals the factor of 12 months "
         "earlier, the Choti bonus 24 months earlier, holdings (gold, recharge, bills) 6 months earlier (lag_hold, a sheet-only "
         "calibration: holdings build from take-ups spread over his life, and the never-held pool offsets part of the lag; "
         "0 = this month's factor, 6 tracks the Python model best).", ""),
        ("3. Loan fees take the take-up x approval factor of the month for first loans, repeats and top-ups alike.", ""),
        ("4. Fixed in the sheet as in the Python plan: the marketplace opens in his month 1; early factors in months 1-6; a stopper "
         "lapses his policies and holdings; no interest on cash.", ""),
        ("Costs and cash, exactly as the Python plan: a 10% contingency on every expensed line inside EBITDA (contingency), and on serving "
         "in the per-saver views (v4 Per saver, v4 LTV); revenue booked when earned but its cash 2 months later (comm_lag), so cash flow = "
         "PAT - revenue + cash received; money needed = the deepest cumulative cash hole + a ₹5 crore cash buffer, at ₹95 = $1. Each is a "
         "blue input on v4 Inputs.", ""),
        ("", ""),
        (f"Reconciliation at the main case's inputs, {RUN_DATE} (full table on v4 Summary and tables/v4_toy_check.csv)", "bold"),
        (recon_words(recon), ""),
        (f"Checks: model/v4_toy_check.py replays all {sum(counts.values()):,} formulas of the v4 tabs through a Google Sheets "
         f"formula interpreter (0 errors) and matches every Monthly and Per saver line, every Yearly cell and every Summary cell to "
         "its numpy twin at the base and at three other scenarios; the per-active profile equals the Python engine's month-49+ "
         f"cohorts to 1e-9. {n_names} named ranges.", ""),
    ]
    cells, fm = {}, {"bold_rows": [], "wrap_rows": [], "col_widths": {"A": 1000}, "number": {}}
    for r, (t_, style) in enumerate(L, start=1):
        if t_:
            cells[f"A{r}"] = t_
            fm["wrap_rows"].append(r)
        if style == "bold":
            fm["bold_rows"].append(r)
    return {"title": "v4 README", "cells": cells, "named_ranges": {}, "formats": fm}


# ---------------------------------------------------------------- 'Start here' (sheetId 200, the first tab; tables/v4_start_here.json)
START = T / "v4_start_here.json"


def start_here():
    """The first tab's texts: the main case in a few lines, live from v4 LTV / v4 Summary where the sheet has the number, the rest
    read from the tables (FIXES.md section B wording). Keeps the file's other keys (layout, the 22 Oct sheet changes)."""
    sh = json.loads(START.read_text())
    h = headline()
    c = sh["cells"]
    L = "'v4 LTV'!"
    neg = '"0.00;−0.00"'
    c["A2"] = (f"Updated {RUN_DATE}, on the founders' 24 Oct inputs. Savers put away ₹100 a day by UPI into mutual funds in their own name "
               "(80% equity, 20% debt); we earn fund fees and, as a loan marketplace, referral fees from lenders. 9 in 10 savers come online, "
               f"pan-India; 1 in 10 through doorstep agents in NCR. The app never holds anyone's money. {h['unconfirmed']}")
    c["A5"] = "v4 README: the answer, the founders' 24 Oct inputs, what the model does and how to use it."
    c["A7"] = ("v4 Summary: the headline numbers, live, next to the Python model.   v4 LTV: one saver's value against the cost to win "
               "them, live, with cross-selling alone.")
    c["A8"] = ("v4 Levers, v4 Monte Carlo: one change at a time on the company; the main case's range, where a saver's money comes from, "
               "the bridge from 23 Oct and what it takes (fixed values from the Python model).")
    c["A11"] = (f'="Cross-selling alone (loans and cards): ₹"&TEXT(SUM({L}B7:B10),"#,##0")&" per saver in 5 years, ₹"'
                f'&TEXT(SUM({L}D7:D10),"#,##0")&" in 8. That is "&TEXT({L}B19,"0.00")&"× and "&TEXT({L}D19,"0.00")&"× of the ₹"'
                f'&TEXT(-{L}B5,"#,##0")&" it costs to win a saver, and less than the ₹"&TEXT(-{L}B11,"#,##0")&" / ₹"&TEXT(-{L}D11,"#,##0")'
                f'&" it costs to serve them, so on its own it never pays back ("&TEXT((SUM({L}B7:B10)+{L}B11)/-{L}B5,{neg})'
                f'&"× after serving). With fund fees, "&TEXT({L}B17,"0.00")&"× in 5 years and "&TEXT({L}D17,"0.00")&"× in 8; pays back "'
                f'&IF(ISNUMBER({L}B18),"in month "&{L}B18,"after month 96")&"."')
    c["A12"] = ("=\"The company: \"&IF(ISNUMBER('v4 Summary'!B11),\"EBITDA positive from month \"&'v4 Summary'!B11,"
                "\"EBITDA not positive by month 96\")&\"; year-5 EBITDA \"&IF('v4 Summary'!B8<0,\"−₹\",\"₹\")"
                "&TEXT(ABS('v4 Summary'!B8),IF(ABS('v4 Summary'!B8)<10,\"0.00\",\"0.0\"))&\" crore; money needed $\""
                "&TEXT('v4 Summary'!B13,\"0.0\")&\"M\"&IF(INDEX(v_cash_flow,96)<0,"
                "\"+ (at least: the company is still losing money at month 96)\",\"\")&\", at ₹\"&TEXT(v_rs_per_usd,\"0\")&\" = $1.\"")
    c["A13"] = (f"The main case is the median of the LTV/CAC Monte Carlo (v4 Monte Carlo). Two inputs are still uncertain: still saving at "
                f"12 months (Bachatt's 30-40%) and our share of the debt fund's fee. Everything else is fixed by the founders (market figures, "
                f"Bachatt, or our judgement: {founders_inputs_short()}; the full list is on v4 README). Cost to win: {h['cac_words']} "
                f"{h['ch1_5']} of the 1,000 draws reach 1× at 5 years, holding everything else at the main case; {h['ch1_8']} by 8 years. "
                f"8 in 10 draws: {h['l5_p10']}-{h['l5_p90']} at 5 years, {h['l8_p10']}-{h['l8_p90']} at 8. The company {h['ebitda_words']}. "
                "At market numbers this is a fund-fee business; loans are a small add-on.")
    c["A14"] = (f"What it takes (v4 Monte Carlo; not another plan): {h['d1w']} alone, or {h['r1w']} alone, takes a saver to 1× at 5 years; "
                f"no single loan lever does. {h['two']}. {h['three_words'][0].upper() + h['three_words'][1:]}. {h['facts']}")
    c["A15"] = h["glossary"]
    return sh


# ---------------------------------------------------------------- main
NEUTRAL = [("An agent's speed in his first month", "An agent's speed in the first month"),
           ("in his first three months", "in their first three months"),
           ("His daily amount steps up each year he saves", "A saver's daily amount steps up each year they save"),
           ("His month (age). Rows 2-97 = his months 1-96", "Saver's month (age). Rows 2-97 = months 1-96"),
           ("the cost to win him", "the cost to win them"), ("while he saves", "while they save"),
           ("while he holds it", "while they hold it"), ("he still saves", "they still save"), ("he holds it", "they hold it"),
           ("each year he has repaid", "each year they have repaid"), ("His next loan", "A saver's next loan"),
           ("in his daily amount", "in the daily amount"), ("accruing to his balance", "accruing to the balance"),
           ("his shop or home", "the saver's shop or home"), ("his original ticket", "the original ticket"),
           ("lapses his policies", "lapses their policies"), ("his life", "their life"),
           ("his still-saving curve", "the still-saving curve")]


def neutral(text):
    """Investor-facing labels name no gender: 'his month 7' -> 'the saver's month 7' (operator review rule)."""
    for a, b in NEUTRAL:
        text = text.replace(a, b)
    text = re.sub(r"\bhis (second|third) month\b", r"the \1 month", text)
    text = re.sub(r"\bhis (months?) ", r"the saver's \1 ", text)
    return text


def formulas_in(sh):
    return sum(1 for val in sh["cells"].values() if isinstance(val, str) and val.startswith("="))


def main():
    recon = vt.reconcile()
    inp = inputs_sheet()
    ps, ps_letters = per_saver_sheet()
    mon, mon_letters = monthly_sheet()
    yr, ylive = yearly_sheet()
    summ, slive, yes_row = summary_sheet(recon)
    sheets = [inp, ps, mon, yr, summ, levers_sheet(recon), mc_sheet()]
    counts = {sh["title"]: formulas_in(sh) for sh in sheets}
    all_names = {}
    for sh in sheets:
        for nm in sh["named_ranges"]:
            assert tc.valid_range_name(nm) and nm.startswith(P), nm
            assert nm not in all_names, f"named range {nm} twice"
            all_names[nm] = sh["title"]
    old = set()
    for f in ("toy_gsheet_spec.json", "company_gsheet_spec.json"):
        if (T / f).exists():
            for sh in json.loads((T / f).read_text())["sheets"]:
                old |= set(sh.get("named_ranges", {}))
    assert not (set(all_names) & old), set(all_names) & old
    sheets.insert(0, readme_sheet(recon, counts, len(all_names)))
    start = start_here()
    for sh in sheets + [start]:
        sh["sheetId"] = SHEET_IDS.get(sh["title"], sh.get("sheetId"))
        sh["cells"] = {a1: neutral(v) if isinstance(v, str) and not v.startswith("=") else v for a1, v in sh["cells"].items()}
        for a1, val in sh["cells"].items():
            if isinstance(val, str) and not val.startswith("="):
                assert not re.search(r"\b(his|he|him|His|He|Him)\b", val), (sh["title"], a1, val)
            if isinstance(val, str) and not val.startswith("="):
                assert val[:1] not in "+-@", (sh["title"], a1, val)        # Sheets would read these as formulas
            if isinstance(val, float):
                assert np.isfinite(val), (sh["title"], a1)
        for val in sh["cells"].values():
            if isinstance(val, str) and val.startswith("="):
                assert len(val) < 50000
    counts = {sh["title"]: formulas_in(sh) for sh in sheets}
    mkeys = {k: mon_letters[k] for k, *_r in monthly_columns() if k != "xs"}
    pkeys = {k: ps_letters[k] for k, _h, kind, _f, _nf in per_saver_columns() if kind != "block" and k != "age"}
    spec = {"sheets": sheets, "_monthly_columns": mkeys, "_per_saver_columns": pkeys,
            "_blocks": {"v4 Per saver": {k: ps_letters[k] for k in ("takeups", "prodmoney", "prodnow")}, "v4 Monthly": {"xs": mon_letters["xs"]}},
            "_summary_live": slive, "_yearly_live": {k: list(v) for k, v in ylive.items()}, "_summary_text_cell": f"B{yes_row}",
            "_meta": {"built": RUN_DATE, "spreadsheet_locale": "en_GB (comma separators)", "formulas_per_sheet": counts,
                      "cells_per_sheet": {sh["title"]: len(sh["cells"]) for sh in sheets}, "named_ranges": len(all_names),
                      "push_order": ["add the 8 tabs (sheetIds 201-208)", "create every named range (all tabs)", "v4 Inputs",
                                     "v4 Per saver", "v4 Monthly", "v4 Yearly", "v4 Summary", "v4 README", "v4 Levers",
                                     "v4 Monte Carlo", "formats"],
                      "values_not_formulas": ["v4 Inputs blue cells", "v4 Summary columns C and D and the reconciliation block",
                                              "v4 Levers", "v4 Monte Carlo", "v4 README"],
                      "named_range_prefix": P, "months": M}}
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    START.write_text(json.dumps(start, ensure_ascii=False, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB); formulas per tab {counts}; named ranges {len(all_names)}; and {START.name}")


if __name__ == "__main__":
    main()

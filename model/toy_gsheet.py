"""Writes tables/toy_gsheet_spec.json: the toy cohort model as Google Sheets cells (live formulas) plus value tabs.

  {"sheets": [{"title", "sheetId", "cells": {"A1": value or "=formula"}, "named_ranges": {name: "B3"}, "formats": {...}}],
   "_monthly_columns": {numpy key: column}, "_meta": {...}}

Maths: model/toy_check.py (the numpy twin, the reconciliation with model/cohort_engine.py and a replay of every formula
here through a small Sheets interpreter). Run this, then `python model/toy_check.py`.

Sheets syntax used: comma separators (the file's locale is en_GB), named ranges with no spaces that are not cell
references (so r3/r12/upi12 are ret_m3/ret_m12/upi_m12) and not function names (days -> deposit_days),
MAKEARRAY(rows, cols, LAMBDA(row, col, ...)), SCAN(init, range, LAMBDA(acc, value, ...)), MMULT, SEQUENCE, FILTER,
ARRAYFORMULA. LAMBDA parameters avoid r and c. Inside ARRAYFORMULA no MIN/MAX/INDEX on arrays (they aggregate):
caps are IF(x>cap, cap, x); lagged factors are MAKEARRAY(60, 1, LAMBDA(m, k, INDEX(range, MAX(1, m-12)))).
"""
import csv
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohort_engine as ce  # noqa: E402
import toy_check as tc  # noqa: E402

T = tc.T
OUT = T / "toy_gsheet_spec.json"
RUN_DATE = "17 Oct 2026"
SHEET_IDS = {"README": 0, "Inputs": 101, "Per saver": 102, "Monthly": 103, "Summary": 104, "Assumptions": 105, "Monte Carlo": 106,
             "Sign-ups": 107, "Agent pay": 108, "Sensitivity": 109}
FMT = {"pct": "0.0%", "pct2": "0.00%", "pct3": "0.000%", "inr": "#,##0", "inr1": "#,##0.0", "inr2": "#,##0.00", "num0": "0",
       "num1": "0.0", "mult": "0.00", "share": "0.00000", "rs2": "#,##0.00", "f3": "0.000"}


def rupee(s):
    """Rs 5 lakh -> ₹5 lakh; Rs a day -> ₹ a day."""
    return re.sub(r"Rs ?(?=\d)", "₹", s).replace("Rs", "₹")


def sig(x, n=4):
    """Round for a value tab: whole rupees above 100, else n significant digits."""
    if x in ("", None):
        return ""
    try:
        f = float(x)
    except ValueError:
        return x
    if math.isnan(f):
        return ""
    if abs(f) >= 100:
        return round(f)
    if f == 0:
        return 0
    return round(f, n - 1 - int(math.floor(math.log10(abs(f)))))


def read_csv(name):
    return list(csv.DictReader((T / name).open()))


# ---------------------------------------------------------------- Inputs
def inputs_sheet(v, dist, res):
    cells, names, fm = {}, {}, {"number": {}, "blue_font": [], "grey_font": [], "bold_rows": [1], "freeze_rows": 1,
                                         "col_widths": {"A": 470, "B": 110, "C": 150, "D": 90, "E": 90, "F": 700, "G": 130}}
    hdr = ["Input", "Value", "Unit", "Low", "High", "Source and confidence (tables/dist_agreed_v1.csv)", "Name in formulas"]
    for j, h in enumerate(hdr):
        cells[f"{chr(65 + j)}1"] = h
    x = ce.likely_inputs()
    nh_lo_hi = {}
    for side, col in (("low", 1), ("high", 3)):
        dd = ce.load_dists()[0]
        xs = dict(x)
        for p in tc.NON_HOUSING:
            for k in [k for k in ce.KEYS if k.startswith(p + "_")]:
                xs[k] = dd[k][col]
        nh_lo_hi[side] = tc.full_nonhousing(ce.run(xs))
    nh = tc.full_nonhousing(res)
    act_years = res["monthly"]["still_saving"][0].sum() / 12
    offered_years = res["monthly"]["proven"][0].sum() / 12

    def coll(lo):
        d = {k: dist[k][1 if lo else 3] for k in ("early_cured", "fee_early", "loss", "recovered", "fee_b3")}
        return d["early_cured"] * d["fee_early"] + d["loss"] / (0.5 * (1 - d["recovered"])) * d["recovered"] * d["fee_b3"]

    special = {
        "xs_other": (round(v["xs_other"] * nh_lo_hi["low"] / nh, 1), round(v["xs_other"] * nh_lo_hi["high"] / nh, 1),
                     f"Calibrated so the toy books the full model's money from the 17 non-housing products over 60 months at the likely "
                     f"values: ₹{nh:,.0f} (₹{nh / act_years:.1f} per active saver a year; "
                     f"insurance at 75% partner share, NPS, FD, gold, SIP, recharge, bills, gold/consumer/vehicle loans). The toy's value "
                     f"(₹{v['xs_other']}) is his first year saved; it grows by xs_growth each full year saved, and the early-months "
                     f"factor and calendar growth are applied to it. Re-calibrate it if you change xs_growth. "
                     f"Low/high: every product's inputs at their low/high in the full model."),
        "xs_growth": (0.10, 0.30,
                      "Toy-only, our judgement. The full model's cross-sell money builds up with years saved (renewals, holdings, "
                      "products offered later). 20% for each full year saved tracks it: at 20% the toy's cumulative P&L at month 36 is "
                      "within about ₹1k of the full model's; at 0% (cross-sell booked evenly) it runs about ₹42k ahead."),
        "coll_per_loan": (round(coll(True), 2), round(coll(False), 2),
                          "Full model, per loan made: 31-90 days late 20% brought back × ₹450 = ₹90; 90+ days bad p90 9.2% "
                          "(= loss 3% ÷ (owed 50% × (1 − recovered 35%))) × recovered 35% × ₹2,500 = ₹80.8. Low/high: every part "
                          "at its low/high. Toy pays it 12 months after the loan (full model: 9 and 18 months)."),
    }
    r = 2
    blocks = [(s, rows, "input") for s, rows in tc.SECTIONS] + [("Fixed in the full model, or too small to matter here", tc.FIXED, "fixed")]
    for sec, rows, kind in blocks:
        cells[f"A{r}"] = sec
        fm["bold_rows"].append(r)
        r += 1
        for name, label, unit, f, key in rows:
            cells[f"A{r}"], cells[f"B{r}"], cells[f"C{r}"], cells[f"G{r}"] = rupee(label), v[name], rupee(unit), name
            if name in special:
                lo, hi, src = special[name]
            else:
                d = dist[key]
                lo, hi = d[1], d[3]
                row = DIST_ROWS.get(key)
                if row:
                    ev = row["evidence_points"].strip()
                    src = f"{row['confidence']}. " + (f"{ev} " if ev else "") + f"[{row['source_ids']}]"
                else:
                    src = "Fixed in the full model (no row in the distribution file)"
                if name == "approved_repeat":
                    src = "Repeat loans are 0.2% of loans at the likely values. " + src
                if name == "upi_ramp":
                    src = "Fixed in the full model: the UPI share climbs in a straight line from 0 at his month 1 to its level at this month."
            cells[f"D{r}"], cells[f"E{r}"], cells[f"F{r}"] = lo, hi, src
            names[name] = f"B{r}"
            for c in "BDE":
                fm["number"][f"{c}{r}"] = FMT[f]
            fm["blue_font"].append(f"B{r}")
            r += 1
    r += 1
    cells[f"A{r}"] = "Worked out from the inputs (formulas; do not type here)"
    fm["bold_rows"].append(r)
    r += 1
    for name, label, unit, f, formula in tc.DERIVED:
        cells[f"A{r}"], cells[f"B{r}"], cells[f"C{r}"], cells[f"G{r}"] = rupee(label), formula, rupee(unit), name
        cells[f"F{r}"] = "Worked out"
        names[name] = f"B{r}"
        fm["number"][f"B{r}"] = FMT[f]
        fm["grey_font"].append(f"B{r}")
        r += 1
    return {"title": "Inputs", "cells": cells, "named_ranges": names, "formats": fm}


# ---------------------------------------------------------------- Per saver
PS = [  # col, header, row-2 formula (None = same as the template), template for row r ({r}, {p} = r - 1), named range, format
    ("B", "Still saving (share of sign-ups)", "=1",
     "=B{p}*IF(A{p}<=3,ret_m3^(1/3),IF(A{p}<=12,(ret_m12/ret_m3)^(1/9),1-churn_late))", "ps_saving", "share"),
    ("C", "Deposit a month while saving (₹)", None, "=daily*deposit_days*(1+amount_growth)^INT((A{r}-1)/term)", None, "rs2"),
    ("D", "Deposits per sign-up (₹)", None, "=B{r}*C{r}", "ps_deposits", "rs2"),
    ("E", "Average fund balance per saver (₹)", "=0.5*C2",
     "=F{p}*IF(MOD(A{r}-1,term)=0,rollover,1)*(1-withdraw_m)+0.5*C{r}", None, "rs2"),
    ("F", "Fund balance per saver at month end (₹)", None, "=E{r}*(1+fund_m)+0.5*C{r}", "ps_endbal", "rs2"),
    ("G", "Average balance per sign-up (₹; also the agent-pay base)", None, "=B{r}*E{r}", "ps_balance", "rs2"),
    ("H", "UPI share of his savers", None, "=upi_m12*MIN(1,(A{r}-1)/(upi_ramp-1))", "ps_upi", "f3"),
    ("I", "Cash visits a day per sign-up", None, "=B{r}*(1-H{r})/visit_every", "ps_visits", "share"),
    ("J", "Fund trail per sign-up (₹)", None, "=G{r}*trail/12", None, "rs2"),
    ("K", "Take-up factor (0 before the marketplace; early factor in months 1-6)", None,
     "=IF(A{r}<mkt_from,0,IF(A{r}<=6,early_takeup,1))", None, "f3"),
    ("L", "Approval factor (early factor in months 1-6)", None, "=IF(A{r}<=6,early_approval,1)", None, "f3"),
    ("M", "Chance a saver with no loan running applies, this month", None, "=apply_m*K{r}", None, "share"),
    ("N", "Never borrowed (share of sign-ups)", "=1", "=(N{p}-Q{p})*B{r}/B{p}", None, "share"),
    ("O", "Repaid and back in the pool (share of sign-ups)", "=0",
     "=(O{p}-R{p})*B{r}/B{p}+IF(A{r}-1-tenure_m>=1,(INDEX(Q$2:Q{p},A{r}-1-tenure_m)+INDEX(R$2:R{p},A{r}-1-tenure_m))"
     "*B{r}/INDEX(B$2:B{p},A{r}-1-tenure_m),0)", None, "share"),
    ("P", "Loan applications per sign-up", None, "=(N{r}+O{r})*M{r}", "ps_apps", "share"),
    ("Q", "First loans per sign-up", None, "=N{r}*M{r}*eligible*MIN(0.8,approved_first*L{r})", None, "share"),
    ("R", "Repeat loans per sign-up", None, "=O{r}*M{r}*eligible*approved_repeat", None, "share"),
    ("S", "Loans per sign-up (first + repeat)", None, "=Q{r}+R{r}", "ps_loans", "share"),
    ("T", "Money lent per sign-up, new loans (₹)", None, "=Q{r}*ticket+R{r}*repeat_ticket", "ps_lent", "rs2"),
    ("U", "Top-up pool: loans with 12+ EMIs paid and EMIs left, per saver still saving", "=0",
     "=(1-topup_m)*U{p}+IF(AND(A{r}>=14,tenure_m>13),INDEX(S$2:S{p},A{r}-13)/INDEX(B$2:B{p},A{r}-13),0)"
     "-IF(AND(A{r}>=tenure_m+1,tenure_m>13),INDEX(S$2:S{p},A{r}-tenure_m)/INDEX(B$2:B{p},A{r}-tenure_m)*(1-topup_m)^(tenure_m-13),0)",
     None, "share"),
    ("V", "Top-ups per sign-up", None, "=B{r}*topup_m*U{r}", "ps_topups", "share"),
    ("W", "Cards per sign-up", None,
     "=IF(AND(A{r}>=mkt_from,A{r}<=mkt_from+5),card_share/6*B{r}*MIN(2,K{r})*MIN(2,L{r}),"
     "IF(AND(A{r}>=mkt_from+6,A{r}<=mkt_from+11),card_share*card_catchup/6*B{r},0))", "ps_cards", "share"),
    ("X", "Cross-sell per sign-up, 17 products lumped (₹)", None, "=B{r}*xs_other/12*K{r}*(1+xs_growth)^INT((A{r}-1)/12)", "ps_xs", "rs2"),
    ("Y", "Home-loan chance this month (apply × approval)", None, "=home_m*K{r}*MIN(0.8,home_approval*L{r})", None, "share"),
    ("Z", "Never had a home loan", "=1", "=Z{p}*(1-Y{p})", None, "f3"),
    ("AA", "Home loans per sign-up", None, "=B{r}*Z{r}*Y{r}", "ps_home", "share"),
    ("AB", "LAP chance this month (apply × approval)", None, "=lap_m*K{r}*MIN(0.8,lap_approval*L{r})", None, "share"),
    ("AC", "Never had a LAP", "=1", "=AC{p}*(1-AB{p})", None, "f3"),
    ("AD", "LAP loans per sign-up", None, "=B{r}*AC{r}*AB{r}", "ps_lap", "share"),
    ("AE", "Collection fees per sign-up, paid 12 months after the loan (₹)", None,
     "=IF(A{r}>12,coll_per_loan*(INDEX(S$2:S{r},A{r}-12)+INDEX(V$2:V{r},A{r}-12)*topup_size*(1+ticket_growth)),0)", "ps_collect", "rs2"),
    ("AF", "Running cost per sign-up (₹)", None, "=B{r}*running", None, "rs2"),
]


PS_AGES = 96          # rows 2-61 = the toy's ages 1-60 (ps_* names); rows 62-97 = ages 61-96, read only by the company tabs (sv_* names)


def per_saver_sheet():
    cells, names = {"A1": "His month (age). Ages 1-60 feed the toy; ages 61-96 (rows 62-97) feed only the company tabs",
                    "A2": f"=SEQUENCE({PS_AGES})"}, {}
    last = PS_AGES + 1
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "wrap_rows": [1], "col_widths": {"A": 80},
          "copy_down": {"from_row": 3, "to_rows": [4, last], "cols": ["B", "AF"]}}
    for col, hdr, f2, tmpl, nm, f in PS:
        cells[f"{col}1"] = hdr
        cells[f"{col}2"] = f2 if f2 else tmpl.format(r=2, p=1)
        for r in range(3, last + 1):
            cells[f"{col}{r}"] = tmpl.format(r=r, p=r - 1)
        if nm:
            names[nm] = f"{col}2:{col}61"
            names["sv_" + nm[3:]] = f"{col}2:{col}{last}"
        fm["number"][f"{col}2:{col}{last}"] = FMT[f]
    return {"title": "Per saver", "cells": cells, "named_ranges": names, "formats": fm}


# ---------------------------------------------------------------- Monthly
def mm(ps, vec):
    return f"MMULT(MAKEARRAY(60,60,LAMBDA(m,k,IF(m>=k,INDEX({ps},m-k+1),0))),{vec})"


MONTHLY = [  # col, header, formula (row 2, spills 60 rows), named range, numpy key, format
    ("A", "Month", "=SEQUENCE(60)", "m_month", "month", "num0"),
    ("B", "Calendar year", "=ARRAYFORMULA(INT((m_month-1)/12)+1)", "m_year", "year", "num0"),
    ("C", "Sign-ups (year-1 level after the ramp; straight line to signup_decline_y5 of it from month 12 to month 49)",
     "=MAKEARRAY(60,1,LAMBDA(m,k,signups*IF(ramp>0,MIN(1,0.5+0.5*(m-1)/ramp),1)"
     "*IF(m<=12,1,1+(signup_decline_y5-1)*MIN(1,(m-12)/37))))", "m_signups", "signups", "num1"),
    ("D", "Take-up growth factor (cap 2x)", "=ARRAYFORMULA(IF((1+takeup_growth)^(m_year-1)>2,2,(1+takeup_growth)^(m_year-1)))", "m_tf", "tf", "f3"),
    ("E", "Approval growth factor", "=ARRAYFORMULA((1+approval_growth)^(m_year-1))", "m_af", "af", "f3"),
    ("F", "Loan factor (take-up × first-loan approval, approval cap 80%)",
     "=ARRAYFORMULA(m_tf*IF(approved_first*m_af>0.8,0.8/approved_first,m_af))", "m_loanf", "loanf", "f3"),
    ("G", "Card factor", "=ARRAYFORMULA(m_tf*IF(m_af>2,2,m_af))", "m_cardf", "cardf", "f3"),
    ("H", "Home-loan factor", "=ARRAYFORMULA(m_tf*IF(home_approval*m_af>0.8,0.8/home_approval,m_af))", "m_homef", "homef", "f3"),
    ("I", "LAP factor", "=ARRAYFORMULA(m_tf*IF(lap_approval*m_af>0.8,0.8/lap_approval,m_af))", "m_lapf", "lapf", "f3"),
    ("J", "Never-borrowed pool adjustment (1 = no growth)",
     "=ARRAYFORMULA(SCAN(1,m_loanf,LAMBDA(acc,f,acc*(1-loan_q*f)/(1-loan_q)))*(1-loan_q)/(1-loan_q*m_loanf))", "m_pool", "pool", "f3"),
    ("K", "Sign-ups ÷ pool adjustment (for the loan lines)", "=ARRAYFORMULA(m_signups/m_pool)", "m_signups_adj", "signups_adj", "num1"),
    ("L", "Loan line factor, this month", "=ARRAYFORMULA(m_loanf*m_pool)", "m_lf0", "lf0", "f3"),
    ("M", "Loan line factor, 12 months earlier (collections)", "=MAKEARRAY(60,1,LAMBDA(m,k,INDEX(m_lf0,MAX(1,m-12))))", "m_lf12", "lf12", "f3"),
    ("N", "Loan line factor, 20 months earlier (top-ups)", "=MAKEARRAY(60,1,LAMBDA(m,k,INDEX(m_lf0,MAX(1,m-20))))", "m_lf20", "lf20", "f3"),
    ("O", "Active savers", "=" + mm("ps_saving", "m_signups"), "m_savers", "savers", "num1"),
    ("P", "Deposits (₹)", "=" + mm("ps_deposits", "m_signups"), "m_deposits", "deposits", "inr"),
    ("Q", "Average fund balance (₹)", "=" + mm("ps_balance", "m_signups"), "m_balance", "balance", "inr"),
    ("R", "Cash visits a day", "=" + mm("ps_visits", "m_signups"), "m_visits", "visits", "num1"),
    ("S", "Loans (first + repeat)", f"=ARRAYFORMULA({mm('ps_loans', 'm_signups_adj')}*m_lf0)", "m_loans", "loans", "f3"),
    ("T", "Top-ups", f"=ARRAYFORMULA({mm('ps_topups', 'm_signups_adj')}*m_lf20)", "m_topups", "topups", "f3"),
    ("U", "Money lent (₹)", f"=ARRAYFORMULA({mm('ps_lent', 'm_signups_adj')}*m_lf0+m_topups*topup_amt)", "m_lent", "lent", "inr"),
    ("V", "Cards", f"=ARRAYFORMULA({mm('ps_cards', 'm_signups')}*m_cardf)", "m_cards", "cards", "f3"),
    ("W", "Home loans (other lenders)", f"=ARRAYFORMULA({mm('ps_home', 'm_signups')}*m_homef)", "m_home", "home", "f3"),
    ("X", "LAP loans (other lenders)", f"=ARRAYFORMULA({mm('ps_lap', 'm_signups')}*m_lapf)", "m_lap", "lap", "f3"),
    ("Y", "Revenue: fund trail (₹)", "=ARRAYFORMULA(m_balance*trail/12)", "m_r_fund", "r_fund", "inr"),
    ("Z", "Fee rate this month (DSA rate x a multiplier rising from month 1 to month 60)",
     "=ARRAYFORMULA(fee*(fee_mult_start+(fee_mult_end-fee_mult_start)*(m_month-1)/59))", "m_fee", "fee_rate", "pct3"),
    ("Z", "Revenue: loan fees (₹)", "=ARRAYFORMULA(m_lent*m_fee*(1-taken_back))", "m_r_fees", "r_fees", "inr"),
    ("AA", "Revenue: collection fees (₹)", f"=ARRAYFORMULA({mm('ps_collect', 'm_signups_adj')}*m_lf12)", "m_r_coll", "r_coll", "inr"),
    ("AB", "Revenue: card fees (₹)", "=ARRAYFORMULA(m_cards*card_fee)", "m_r_cards", "r_cards", "inr"),
    ("AC", "Revenue: insurance, investments, payments, other loans (₹)", f"=ARRAYFORMULA({mm('ps_xs', 'm_signups')}*m_tf)", "m_r_xs", "r_xs", "inr"),
    ("AD", "Revenue: home-loan and LAP fees (₹)", "=ARRAYFORMULA(m_home*home_ticket*home_fee+m_lap*lap_ticket*lap_fee)", "m_r_house",
     "r_house", "inr"),
    ("AE", "Income (₹)", "=ARRAYFORMULA(m_r_fund+m_r_fees+m_r_coll+m_r_cards+m_r_xs+m_r_house)", "m_income", "income", "inr"),
    ("AF", "Cost: salary (₹)", "=ARRAYFORMULA(salary+0*m_month)", "m_c_salary", "c_salary", "inr"),
    ("AG", "Cost: KYC (₹)", "=ARRAYFORMULA(m_signups*kyc)", "m_c_kyc", "c_kyc", "inr"),
    ("AH", "Cost: running (₹)", "=ARRAYFORMULA(m_savers*running)", "m_c_running", "c_running", "inr"),
    ("AI", "Cost: cash cover (₹)", "=ARRAYFORMULA(cash_cover+0*m_month)", "m_c_cover", "c_cover", "inr"),
    ("AJ", "Cost: agent pay on balance, capped (₹)",
     "=ARRAYFORMULA(IF(m_balance*agent_pay/12>incentive_cap,incentive_cap,m_balance*agent_pay/12))", "m_c_agent", "c_agent", "inr"),
    ("AK", "Cost: extra cash-collection capacity (₹)", "=ARRAYFORMULA(IF(m_visits>capacity,(m_visits-capacity)*extra_cost/400,0))",
     "m_c_extra", "c_extra", "inr"),
    ("AL", "Cost: online leads (₹)", "=ARRAYFORMULA(m_signups*online_lead_share*lead_cost)", "m_c_leads", "c_leads", "inr"),
    ("AM", "Costs (₹)", "=ARRAYFORMULA(m_c_salary+m_c_kyc+m_c_running+m_c_cover+m_c_agent+m_c_extra+m_c_leads)", "m_cost", "cost", "inr"),
    ("AN", "Net (₹)", "=ARRAYFORMULA(m_income-m_cost)", "m_net", "net", "inr"),
    ("AO", "Cumulative P&L (₹)", "=SCAN(0,m_net,LAMBDA(acc,v,acc+v))", "m_cum", "cum", "inr"),
]


MONTHLY = [(tc.col_name(i + 1), *row[1:]) for i, row in enumerate(MONTHLY)]   # letters follow the order (round 9 inserted one)


def monthly_sheet():
    cells, names = {}, {}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "wrap_rows": [1], "col_widths": {}}
    for col, hdr, f, nm, _key, nf in MONTHLY:
        cells[f"{col}1"], cells[f"{col}2"] = hdr, f
        names[nm] = f"{col}2:{col}61"
        fm["number"][f"{col}2:{col}61"] = FMT[nf]
    return {"title": "Monthly", "cells": cells, "named_ranges": names, "formats": fm}


# ---------------------------------------------------------------- Summary
SUMMARY_FORMULAS = {
    "Cumulative P&L at month 12": "=INDEX(m_cum,12)",
    "Cumulative P&L at month 36": "=INDEX(m_cum,36)",
    "Cumulative P&L at month 60": "=INDEX(m_cum,60)",
    "Payback month (cumulative P&L stays at or above 0 from here)":
        '=IF(INDEX(m_cum,60)<0,"not within 60 months",IFERROR(MAX(FILTER(m_month,m_cum<0))+1,1))',
    "Peak cash need (lowest cumulative P&L)": "=MIN(0,MIN(m_cum))",
    "Savers still saving, year-5 average (months 49-60)": "=AVERAGE(Monthly!O50:O61)",
    "Money lent in year 5 (first, repeat and top-up loans)": "=SUM(Monthly!U50:U61)",
    "Loans made in year 5 (first and repeat)": "=SUM(Monthly!S50:S61)",
    "Money lent in 60 months": "=SUM(m_lent)",
    "Revenue per active saver a year (60-month average)": "=SUM(m_income)/(SUM(m_savers)/12)",
    "Fund trail": "=SUM(m_r_fund)",
    "Loan fees (net of fees taken back)": "=SUM(m_r_fees)",
    "Collection fees": "=SUM(m_r_coll)",
    "Card fees": "=SUM(m_r_cards)",
    "Insurance, investments, payments and other loans (lumped)": "=SUM(m_r_xs)",
    "Home-loan and LAP fees": "=SUM(m_r_house)",
    "Income": "=SUM(m_income)",
    "Costs": "=SUM(m_cost)",
    "Net (= cumulative P&L at month 60)": "=SUM(m_net)",
    "  of the costs: online leads, 60 months": "=SUM(m_c_leads)",
    "  of the costs: extra cash-collection capacity (helpers), 60 months": "=SUM(m_c_extra)",
}


def summary_sheet(res, gaps):
    cells = {"A1": "Measure", "B1": "Toy (live, from Inputs)", "C1": f"Full Python model at the likely values ({RUN_DATE}, fixed)",
             "D1": "Toy minus full", "E1": "Gap", "F1": "Why the toy differs at the likely values"}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "wrap_rows": [1], "col_widths": {"A": 430, "B": 150, "C": 170, "D": 130, "E": 80, "F": 520}}
    for i, (label, _ft, ff, kind) in enumerate(tc.SUMMARY, start=2):
        if label is None:
            continue
        cells[f"A{i}"] = label
        if kind == "head":
            fm["bold_rows"].append(i)
            continue
        cells[f"B{i}"] = SUMMARY_FORMULAS[label]
        cells[f"C{i}"] = float(ff(res))
        cells[f"D{i}"] = f'=IFERROR(B{i}-C{i},"")'
        cells[f"E{i}"] = "" if kind == "month" else f'=IFERROR((B{i}-C{i})/ABS(C{i}),"")'
        cells[f"F{i}"] = gaps.get(label, "") + (" (difference in months)" if kind == "month" else "")
        nf = {"inr": FMT["inr"], "num1": FMT["num1"], "month": FMT["num0"]}[kind]
        for c in "BCD":
            fm["number"][f"{c}{i}"] = nf
        fm["number"][f"E{i}"] = "0.0%"
    return {"title": "Summary", "cells": cells, "named_ranges": {}, "formats": fm}


# ---------------------------------------------------------------- value tabs
def table_sheet(title, note, headers, rows, widths=None, numfmt=None):
    cells = {"A1": note}
    for j, h in enumerate(headers):
        cells[f"{tc.col_name(j + 1)}2"] = h
    for i, row in enumerate(rows, start=3):
        for j, val in enumerate(row):
            if val not in ("", None):
                cells[f"{tc.col_name(j + 1)}{i}"] = val
    fm = {"bold_rows": [1, 2], "freeze_rows": 2, "wrap_rows": [2], "col_widths": widths or {}, "number": numfmt or {}}
    return {"title": title, "cells": cells, "named_ranges": {}, "formats": fm}


DIST_ROWS = {r["key"]: r for r in read_csv("dist_agreed_v1.csv")}


def assumptions_sheet():
    cols = ["group", "name", "kind", "shape", "low", "likely", "high", "p10", "p50", "p90", "unit", "confidence", "source_ids"]
    rows = [[sig(r[c]) if c in ("low", "likely", "high", "p10", "p50", "p90") else r[c] for c in cols] for r in read_csv("dist_agreed_v1.csv")]
    return table_sheet("Assumptions", f"Agreed input distributions (tables/dist_agreed_v1.csv, agreed {RUN_DATE}, round 10): what the full Python model "
                                      "reads. Pasted values; editing them changes nothing.",
                       ["Group", "Input", "Kind", "Shape", "Low", "Likely", "High", "P10", "P50", "P90", "Unit", "Confidence", "Sources"], rows,
                       {"B": 380, "L": 130, "M": 160})


def mc_sheet():
    rows = [[r["measure"], r["unit"], *[sig(r[c]) for c in ("p5", "p10", "p25", "p50", "p75", "p90", "p95", "mean", "value")], r["note"]]
            for r in read_csv("cohort_mc_summary.csv")]
    return table_sheet("Monte Carlo", f"Monte Carlo of the full Python model (tables/cohort_mc_summary.csv): 10,000 draws, seed 20261016, "
                                      f"run {RUN_DATE}. Pasted values, not live.",
                       ["Measure", "Unit", "P5", "P10", "P25", "P50", "P75", "P90", "P95", "Mean", "Value", "Note"], rows,
                       {"A": 420, "L": 400}, {"C3:K60": "#,##0.####"})


SWEEP_HDR = {"signups_a_month": "Sign-ups a month", "salary_per_signup": "Salary per sign-up (₹)", "pay": "Agent pay",
             "p_cum60_pos": "P(cumulative P&L at 60 > 0)", "p_cum36_pos": "P(cumulative P&L at 36 > 0)",
             "cum60_p10": "Cumulative P&L at 60, P10 (₹)", "cum60_p50": "Cumulative P&L at 60, P50 (₹)",
             "cum60_p90": "Cumulative P&L at 60, P90 (₹)", "cum36_p50": "Cumulative P&L at 36, P50 (₹)", "payback_p50": "Payback month, P50",
             "never_pays_back_60": "Share never paying back in 60 months", "peak_cash_need_p50": "Peak cash need, P50 (₹)",
             "visits_peak_p50": "Peak cash visits a day, P50", "incentive_m12_p50": "Agent pay in month 12, P50 (₹)",
             "incentive_m24_p50": "Agent pay in month 24, P50 (₹)", "incentive_m60_p50": "Agent pay in month 60, P50 (₹)",
             "incentive_total60_p50": "Agent pay over 60 months, P50 (₹)"}


def sweep_sheet(title, fname, note):
    data = read_csv(fname)
    cols = list(data[0])
    # Sheets reads text that starts with "+" as a formula (#ERROR!), so "+0.25% ..." is written "salary +0.25% ..."
    rows = [[sig(r[c]) if c != "pay" else ("salary " + r[c] if r[c].startswith(("+", "=")) else r[c]) for c in cols] for r in data]
    return table_sheet(title, note, [SWEEP_HDR.get(c, c) for c in cols], rows, {"A": 230}, {"B3:Q20": "#,##0.###"})


def sensitivity_sheet():
    data = read_csv("cohort_mc_drivers.csv")
    data.sort(key=lambda r: -float(r["swing_cum_pnl60_top_minus_bottom_decile"]))
    rows = [[i, r["input"], r["key"], round(float(r["swing_cum_pnl60_top_minus_bottom_decile"])), sig(r["spearman_with_cum_pnl60"], 3),
             sig(r["input_p10"]), sig(r["input_p90"])] for i, r in enumerate(data, start=1)]
    return table_sheet("Sensitivity", f"Which inputs move cumulative P&L at 60 months, from the Monte Carlo of the full Python model "
                                      f"(tables/cohort_mc_drivers.csv, run {RUN_DATE}): mean of the draws where the input is in its top 10% "
                                      f"minus its bottom 10%. Negative = a higher value lowers the P&L. Spearman below about 0.02 is noise.",
                       ["Rank", "Input", "Key", "Swing in cumulative P&L at 60 months (₹)", "Spearman with cumulative P&L at 60",
                        "Input P10", "Input P90"], rows, {"B": 520, "D": 200, "E": 170}, {"D3:D110": "#,##0", "F3:G110": "#,##0.####"})


def ct_rounds():
    import company_toy_check as ct          # noqa: E402  (the company twin; imported late, it imports this module's sibling)
    return ct.rounds_table()


def readme_sheet(recon, n_formulas, v):
    gap36 = next(r["gap"] for r in recon if r["measure"] == "Cumulative P&L at month 36")
    L = [
        ("Save4More: toy cohort model of one street agent, 60 months", "bold"),
        (f"Built {RUN_DATE} from the full Python model (model/cohort_engine.py) at the agreed likely values (Assumptions tab). "
         "Metric: undiscounted cumulative P&L. Round 8 (17 Oct): sign-ups 100 a month in year 1, falling in a straight line to 70% of that "
         "by month 49; half of onboardings start as bought online leads (₹250 each) and are served offline like any saver; the old +10% a "
         "year sign-up growth is gone. Round 9 (17 Oct): the loan origination fee starts at a DSA's rate (1.75%) and rises in a straight line "
         "to 1.5x by company month 60 (Monthly column Z); home loans and LAP unchanged. Round 10 (17 Oct): the agent's 0.25% pay on balance "
         "is capped at ₹10,000 a month (incentive_cap).", ""),
        ("", ""),
        ("How to play", "bold"),
        ("Change the blue cells in column B of Inputs. Per saver, Monthly and Summary recalculate. Low and high are the agreed range.", ""),
        ("Grey cells at the bottom of Inputs are worked out from the blue ones; do not type there. Do not type on Per saver or Monthly.", ""),
        ("Summary column B is live; column C is the full Python model at the likely values and does not move, so the gap shows how far "
         "your change has moved the answer (plus the toy's own small error at the likely values, shown in column F).", ""),
        ("", ""),
        ("Tabs", "bold"),
        ("Inputs: the 51 inputs (blue), 6 rarely-changed ones and the worked-out values. Every input has a name used in the formulas.", ""),
        ("Per saver: one sign-up's months 1-60 (his age): still saving, deposits, fund balance, UPI and cash visits, fund trail, loans "
         "(never borrowed, back in the pool after repaying, applications, first and repeat loans, money lent), top-ups, cards, "
         "cross-sell, home loans and LAP, collections and running cost. Calendar year 1 terms.", ""),
        ("Monthly: months 1-60. Each total line is one formula: the sum over every month's sign-ups of the Per saver line at their age "
         "(MMULT of a 60 x 60 cohort matrix with the sign-ups), times the calendar-year growth factor for that line. Then revenue, "
         "costs, net and cumulative P&L.", ""),
        ("Summary: cumulative P&L at 12, 36 and 60 months, payback month, peak cash need, year-5 savers, money lent and loans, revenue "
         "per active saver, and where the money comes from.", ""),
        ("Assumptions, Monte Carlo, Sign-ups, Agent pay, Sensitivity: pasted values from the full Python model, run "
         f"{RUN_DATE} (Monte Carlo: 10,000 draws, seed 20261016). They do not change when you edit Inputs.", ""),
        ("", ""),
        ("The toy is a simplification of the full model", "bold"),
        ("1. Calendar growth. Take-up (+5% a year) and approval (+10% a year) grow by calendar year. The full model gives every month's "
         "sign-ups its own profile; the toy computes one profile in year-1 terms and multiplies each month's total by that month's factor. "
         "Exact for anything booked at take-up (cards, home loans, LAP, first loans) apart from item 2.", ""),
        ("2. Never-borrowed pool. With growth, savers borrow sooner, so the pool who never borrowed empties faster. Monthly column J "
         "corrects the loan lines for it (1 = no growth). With growth set to 0 the toy's loans, top-ups, cards and housing equal the "
         "full model's exactly.", ""),
        ("3. Top-ups (13-35 months after the loan) take the loan factor of 20 months earlier; collections that of 12 months earlier.", ""),
        ("4. Collections: one fee per loan made (31-90 days late and 90+ days bad, ₹170.77), paid 12 months after the loan; the full "
         "model pays the two parts after 9 and 18 months.", ""),
        (f"5. The 17 non-housing products (insurance, SIP, NPS, FD, gold, recharge, bills, gold / consumer / vehicle loans) are one input, "
         f"₹{v['xs_other']} per active saver a year in his first year saved, growing {v['xs_growth']:.0%} for each full year he has saved "
         f"(xs_growth), calibrated to the full model's 60-month money. The full model's money builds up with years saved product by "
         f"product (renewals, holdings); the 20% step tracks it: the toy is within about ₹{abs(gap36) / 1000:,.1f}k of it at month 36 and "
         f"pays back in the same month. At 0% growth the toy books cross-sell evenly and runs about ₹42k ahead at month 36.", ""),
        ("6. Repeat loans (0.2% of loans) take the first-loan factor. Home loans and LAP are modelled as in the full model.", ""),
        ("", ""),
        ("Reconciliation at the likely values (toy vs full Python model)", "bold"),
    ]
    cells, fm = {}, {"bold_rows": [], "wrap_rows": [], "col_widths": {"A": 900, "B": 140, "C": 140, "D": 90, "E": 420}, "number": {}}
    r = 1
    for text, style in L:
        if text:
            cells[f"A{r}"] = text
        if style == "bold":
            fm["bold_rows"].append(r)
        r += 1
    for j, h in enumerate(["Measure", "Toy", "Full model", "Gap", "Why"]):
        cells[f"{chr(65 + j)}{r}"] = h
    fm["bold_rows"].append(r)
    r += 1
    for row in recon:
        cells[f"A{r}"] = row["measure"]
        cells[f"B{r}"] = row["toy"] if isinstance(row["toy"], str) else round(row["toy"], 1)
        cells[f"C{r}"] = round(row["full_model"], 1)
        if row["gap_pct"] != "":
            cells[f"D{r}"] = round(row["gap_pct"], 4)
        if row["why"]:
            cells[f"E{r}"] = row["why"]
        fm["number"][f"B{r}:C{r}"] = "#,##0"
        fm["number"][f"D{r}"] = "0.0%"
        r += 1
    r += 1
    cells[f"A{r}"] = (f"Checks: model/toy_check.py replays all {n_formulas} formulas of this workbook through a Sheets formula interpreter and "
                      f"matches every Summary cell to its numpy twin; the toy-vs-full table is tables/toy_vs_full.csv.")
    co = T / "base_toy_vs_full.csv"                     # the company tabs (model/company_gsheet.py), THE BASE
    old = T / "company_toy_vs_full.csv"                  # the round-10 plan's reconciliation, kept for reference
    uni = T / "unicorn_toy_vs_full.csv"                  # the unicorn track's reconciliation, kept for reference
    if co.exists():
        r += 2
        cr = lambda z: f"₹{z / 1e7:,.0f} crore"
        rd = [(nm, m, a) for nm, m, a, _p, _e in ct_rounds() if a > 0]
        rtxt = "; ".join(f"{nm} {cr(a)} at month {m:.0f}" for nm, m, a in rd)
        lines = [
            ("Company tabs: THE BASE (final; tables/base_*, model/base_plan.py): 30% of personal-loan volume on our own NBFC book from "
             "month 30, and the real-world city limits", "bold"),
            ("The plan: 172 cities opened in rank order (City plan tab), 300 agents by month 18, then +150 a month, capped at 5,000; "
             "each city's sign-ups slow as it fills: x (1 - (cumulative / cap)^2), cap = 20% of the city's urban self-employed pool, "
             "growing 3% a year; the central team as built; funding = the rounds table: " + rtxt + "; 96 company months.", ""),
            ("Tabs: Company inputs (fleet path as a check, cities, costs, NBFC, the ROUNDS table; blue). City plan: 172 cities (blue: "
             "city, rank, addressable, launch month, agents at each tenure point) with each city's penetration and slowdown at months "
             "60 and 96. City by month: 96 months x 172 cities (agents, new books, sign-ups before the slowdown, the cap, cumulative "
             "sign-ups, sign-ups). Company per book, Company monthly (the company's agents and sign-ups are summed from the cities; "
             "NBFC lines: on-book loans, book, interest, cost of funds, NII, processing fees, provisions, equity, borrowings), "
             "Company yearly (years 1-8), Funding & cap table (cap table; the three lenses at month 60), Company summary.", ""),
            ("Every city is modelled individually (no aggregate): the slowdown runs row by row over the 96 months, vectorised across "
             "the 172 cities. Each book's agent works at the fleet's average sign-up level (agent_level, the agreed distribution's mean, "
             "1.017 x the likely 100). The per-book costs (capped pay on balance, helpers, cash cover) use the average book of each "
             "age, scaled by the company's ratio of saturated to unsaturated balance, visits and cash (one ratio for all cities: an "
             "approximation). The NBFC as the full model (nbfc.py): EMIs at the 26% yield over 36 months, provisions of 0.6 x the "
             "agreed 3% loss at disbursal, equity = the larger of ₹10 crore NOF and 25% of the book, borrowings the rest at 13.5%.", ""),
            ("The unicorn check (Funding & cap table): lens 1 = 20 x ARR (ARR = 12 x month-60 fees + NII + processing fees), lens 2 "
             "= 0.45 x AUM, both against ₹10,000 crore; lens 3 (cross-check) = 3 x NBFC equity + 20 x fee ARR. All multiples are OUR "
             "JUDGEMENT and blue inputs there.", ""),
            ("Where the toy and the full model part: the full model opens cities AUTOMATICALLY (each hire to the city with the most "
             "headroom); the City plan records that rollout at tenure points, and its straight lines put about 7.5% more agents in year "
             "2. The full model run on the same City plan gives year-2 revenue +9.2% and year-5 EBITDA -₹9.0 crore (vs -₹7.9 crore "
             "AUTO); the toy is within 1% of that run's revenue in every year.", ""),
        ]
        if uni.exists():
            u = {row["measure"]: row for row in csv.DictReader(uni.open())}
            lines.append((
                "Earlier plan 2, kept for reference: the unicorn track (no NBFC, no city limits): 300 agents by month 18, +200 a month, "
                "cap 7,500; rounds ₹1,308 crore by month 60. Full model: year-5 revenue "
                f"₹{float(u['Revenue, year 5']['full_model']) / 1e7:,.0f} crore, year-5 EBITDA ₹{float(u['EBITDA, year 5']['full_model']) / 1e7:,.0f} crore; "
                "the toy matched it within 1.7% on revenue and 0.8% on EBITDA in years 1-5 (tables/unicorn_toy_vs_full.csv).", ""))
        if old.exists():
            orow = {row["measure"]: row for row in csv.DictReader(old.open())}
            f5 = lambda k: float(orow[k]["full_model"])
            lines.append((
                "Earlier plan 1, kept for reference (round 10): 80 agents by month 18, then replace leavers; central lean hold; seed "
                f"₹10 crore + Series A ₹50 crore at month 18; year-5 revenue ₹{f5('Revenue, year 5') / 1e7:,.2f} crore, year-5 EBITDA "
                f"−₹{-f5('EBITDA, year 5') / 1e7:,.2f} crore (tables/company_toy_vs_full.csv).", ""))
        lines.append(("Company reconciliation (toy vs the full base model, tables/base_toy_vs_full.csv; years 6-8 are context)", "bold"))
        for text, style in lines:
            cells[f"A{r}"] = text
            if style == "bold":
                fm["bold_rows"].append(r)
            r += 1
        for j, h in enumerate(["Measure", "Toy", "Full model", "Gap"]):
            cells[f"{chr(65 + j)}{r}"] = h
        fm["bold_rows"].append(r)
        r += 1
        keep = ("Revenue, year", "EBITDA, year", "PAT, year 5", "Net interest income, year 5", "Loan book", "NBFC equity",
                "ARR at month 60", "AUM at month 60", "Lens 1:", "Lens 2:", "Lens 3 (", "Unicorn on paper", "Lowest month-end cash",
                "Closing cash at month 60", "EBITDA break-even", "Savers still saving, month 60", "Cumulative sign-ups", "Founders' share")
        for row in csv.DictReader(co.open()):
            if not row["measure"].startswith(keep):
                continue
            cells[f"A{r}"] = rupee(row["measure"])
            for col, key in (("B", "toy"), ("C", "full_model")):
                try:
                    cells[f"{col}{r}"] = round(float(row[key]), 4 if abs(float(row[key])) < 5 else 1)
                except ValueError:
                    cells[f"{col}{r}"] = row[key]
            pc = row["measure"].startswith("Founders'")
            fm["number"][f"B{r}:C{r}"] = "0.0%" if pc else "#,##0"
            if row["gap_pct"] not in ("", None):
                cells[f"D{r}"] = round(float(row["gap_pct"]), 4)
                fm["number"][f"D{r}"] = {"points": "+0.0%;-0.0%", "months": "+0;-0;0"}.get(row["gap_kind"], "0.0%")
            r += 1
    return {"title": "README", "cells": cells, "named_ranges": {}, "formats": fm}


def main():
    dist = ce.load_dists()[0]
    v = tc.likely_toy_inputs()
    res = tc.full_run()
    recon = tc.reconcile()[3]                                 # toy vs full (static on README)
    gaps = {r["measure"]: r["why"] for r in recon}
    gaps.update({"Insurance, investments, payments and other loans (lumped)": "calibrated to the full model's 60-month money",
                 "Loan fees (net of fees taken back)": "calendar growth approximated with the pool adjustment",
                 "Money lent in 60 months": "calendar growth approximated with the pool adjustment",
                 "Cumulative P&L at month 12": "cross-sell timing: one lumped line growing 20% a year saved",
                 "Cumulative P&L at month 60": "within 0.5%: small offsets from items 2-5 on README",
                 "Net (= cumulative P&L at month 60)": "within 0.5%: small offsets from items 2-5 on README",
                 "Home-loan and LAP fees": "pool depletion for housing not adjusted (small)"})
    sheets = [inputs_sheet(v, dist, res), per_saver_sheet(), monthly_sheet(), summary_sheet(res, gaps), assumptions_sheet(), mc_sheet(),
              sweep_sheet("Sign-ups", "cohort_signups_sweep.csv", f"Sign-ups sweep of the full Python model's Monte Carlo "
                                                                   f"(tables/cohort_signups_sweep.csv, run {RUN_DATE}). Pasted values."),
              sweep_sheet("Agent pay", "cohort_incentive_sweep.csv", f"Agent pay on balance, options compared in the full Python model's Monte "
                                                                     f"Carlo (tables/cohort_incentive_sweep.csv, run {RUN_DATE}). Pasted values."),
              sensitivity_sheet()]
    n_formulas = sum(1 for sh in sheets for val in sh["cells"].values() if isinstance(val, str) and val.startswith("="))
    sheets.insert(0, readme_sheet(recon, n_formulas, v))
    for sh in sheets:
        sh["sheetId"] = SHEET_IDS[sh["title"]]
        for nm in sh["named_ranges"]:
            assert tc.valid_range_name(nm), nm
    spec = {"sheets": sheets, "_monthly_columns": {key: col for col, _h, _f, _n, key, _nf in MONTHLY},
            "_meta": {"built": RUN_DATE, "spreadsheet_locale": "en_GB (comma separators)", "per_sheet_formulas":
                      {sh["title"]: sum(1 for val in sh["cells"].values() if isinstance(val, str) and val.startswith("=")) for sh in sheets}}}
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB); formulas per sheet: {spec['_meta']['per_sheet_formulas']}")


if __name__ == "__main__":
    main()

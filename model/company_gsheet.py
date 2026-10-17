"""Writes tables/company_gsheet_spec.json: the company tabs of the Google Sheet toy, THE BASE (tables/base_*: 30% of personal-loan
volume on our own book from m30, the real-world city setting), all live formulas. Earlier: the unicorn track (no NBFC, no cities).

  City plan             172 cities (blue): city, rank, addressable, launch month, agents at each tenure point; per city, the
                        penetration and the soft slowdown 1 - (pen / cap)^2 at months 60 and 96
  City by month         96 months x 172 cities: agents, new books, sign-ups before the slowdown, the city cap (growing with the
                        pool refill), cumulative sign-ups after the slowdown and the cap, sign-ups

  Company inputs        the fleet path (300 by m18, +200 a month, cap 7,500), the team table, costs, and the ROUNDS table
                        (round, month, amount, pre-money; blue cells; named ranges)
  Company per book      one book (an agent's territory) by its age 1-96: expected ramp, cost split, sign-ups, visits, balance,
                        cash, helpers, cash cover
  Company monthly       months 1-96: calendar factors, fleet, headcount, savers, lending, the P&L ladder (revenue by line, CM1,
                        CM2, CM3, EBITDA, depreciation, interest, tax, PAT), the cash flow and the two valuation lenses
  Company yearly        SUMIFS roll-ups, years 1-8
  Funding & cap table   post-money, dilution and the cap table after each round; the month-60 unicorn check (20 x ARR and
                        0.45 x AUM against Rs 10,000 crore; the multiples are blue inputs, our judgement)
  Company summary       the toy vs the full model (tables/unicorn_*.csv): revenue, EBITDA, PAT by year, the unicorn check, cash,
                        break-even and scale at m60

Every company line reads the toy's 'Per saver' tab (ages 1-96; sv_* names) and stacks it over the hiring plan with one
MMULT(MAKEARRAY(...)) per line. The numpy twin and the checks: model/company_toy_check.py.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import company_toy_check as ct  # noqa: E402
import toy_check as tc  # noqa: E402

T = tc.T
OUT = ct.SPEC
N = ct.N
LAST = N + 1                       # last data row on the monthly and per-book tabs
SHEET_IDS = {"Company inputs": 110, "City plan": 116, "City by month": 117, "Company per book": 111, "Company monthly": 112,
             "Company yearly": 113, "Funding & cap table": 115, "Company summary": 114}
NC = 172                           # cities in the City plan
FMT = {"pct": "0.0%", "pct2": "0.00%", "pct3": "0.000%", "inr": "#,##0", "num0": "0", "num1": "0.0", "f3": "0.000",
       "share": "0.00000", "rs2": "#,##0.00", "mult": "0.0", "mult2": "0.00", "text": None}
SECTION_BEFORE = {"agents_m18": "Fleet path (base: 300 agents by month 18, then +150 a month, capped at 5,000). CHECK ONLY: the company's agents are summed from the City plan tab",
                  "agent_level": "Fleet",
                  "pay_months": "Months 61-96 (as the full model's 96-month run)",
                  "pool": "Cities (the City plan tab holds each city's addressable pool, launch month and agents)",
                  "city_launch": "City costs and field management", "scale_after": "Central team: scaling rules (as built, no lean hold)",
                  "statutory": "Pay extras", "app_base": "App, licences, overheads and small costs", "tax_rate": "Finance",
                  "seed_cost": "Fund-raising costs (the rounds themselves are in the table below)",
                  "xs_ins": "Cross-sell split (the toy lumps the 17 non-housing products into one line)",
                  "nb_licence_month": "NBFC: our own book of personal loans (base: 30% of volume from month 30)"}
rs = lambda z: re.sub(r"Rs ?(?=\d)", "₹", z).replace("Rs", "₹") if isinstance(z, str) else z


def inputs_sheet(I, plan, role_tab, rounds):
    cells, names = {"A1": "Input", "B1": "Value", "C1": "Unit", "D1": "Note", "E1": "Name in formulas"}, {}
    fm = {"number": {}, "blue": [], "grey": [], "bold_rows": [1], "freeze_rows": 1,
          "col_widths": {"A": 520, "B": 130, "C": 150, "D": 330, "E": 150, "F": 120, "G": 130, "H": 150}}
    r = 2
    cells[f"A{r}"] = "Hiring plan"
    fm["bold_rows"].append(r)
    r += 1
    cells.update({f"A{r}": "Shape of the ramp to month 18 (the full model's path), scaled so month 18 = 'agents at month 18'",
                  f"B{r}": "Month", f"C{r}": "Agents (shape)"})
    fm["bold_rows"].append(r)
    r += 1
    r0 = r
    for i, (m, s) in enumerate(zip(plan["plan_m"], plan["plan_s"]), 1):
        cells[f"A{r}"], cells[f"B{r}"], cells[f"C{r}"] = f"Point {i}", m, s
        fm["blue"] += [f"B{r}", f"C{r}"]
        r += 1
    names["plan_m"], names["plan_s"] = f"B{r0}:B{r - 1}", f"C{r0}:C{r - 1}"
    for k, (val, label, unit, f, note) in I.items():
        if k in SECTION_BEFORE:
            cells[f"A{r}"] = SECTION_BEFORE[k]
            fm["bold_rows"].append(r)
            r += 1
        cells[f"A{r}"], cells[f"B{r}"], cells[f"C{r}"], cells[f"E{r}"] = rs(label), val, rs(unit), k
        if note:
            cells[f"D{r}"] = rs(note)
        names[k] = f"B{r}"
        if FMT[f]:
            fm["number"][f"B{r}"] = FMT[f]
        fm["blue"].append(f"B{r}")
        r += 1
    # the rounds table
    r += 1
    cells[f"A{r}"] = ("Funding: the ROUNDS table (blue; from tables/base_rounds.csv, the full model's plan; valuations are our "
                      "judgement). Keep rows in date order; a spare row (amount 0) is ignored. Month 0 = before month 1 (the seed).")
    fm["bold_rows"].append(r)
    r += 1
    for j, h in enumerate(["Round", "Month it lands (end of month; 0 = before month 1)", "Amount (₹)", "Pre-money (₹)",
                           "ESOP topped up to the target at this round (1 = yes)", "Cash lands in company month (formula)",
                           "Raise cost booked that month (₹, formula)"]):
        cells[f"{tc.col_name(j + 1)}{r}"] = h
    fm["bold_rows"].append(r)
    fm.setdefault("wrap_rows", []).append(r)
    r += 1
    r0 = r
    for nm, m, amt, pre, esop in rounds:
        cells.update({f"A{r}": nm, f"B{r}": m, f"C{r}": amt, f"D{r}": pre, f"E{r}": esop,
                      f"F{r}": f"=MAX(1,B{r})", f"G{r}": f"=IF(AND(B{r}>=1,C{r}>0),round_cost,0)"})
        fm["blue"] += [f"A{r}", f"B{r}", f"C{r}", f"D{r}", f"E{r}"]
        fm["grey"] += [f"F{r}", f"G{r}"]
        fm["number"].update({f"B{r}": "0", f"C{r}": "#,##0", f"D{r}": "#,##0", f"E{r}": "0", f"F{r}": "0", f"G{r}": "#,##0"})
        r += 1
    for nm, col in (("rd_name", "A"), ("rd_month", "B"), ("rd_amount", "C"), ("rd_pre", "D"), ("rd_esop", "E"), ("rd_land", "F"),
                    ("rd_cost", "G")):
        names[nm] = f"{col}{r0}:{col}{r - 1}"
    # the launch team
    r += 1
    cells[f"A{r}"] = "Central team: the launch team (pay a month; count from a month, then a later count)"
    fm["bold_rows"].append(r)
    r += 1
    for j, h in enumerate(["Role", "Pay a month", "Department", "Count first", "From month", "Count later", "From month",
                           "Scales after m18 (1 = yes)"]):
        cells[f"{tc.col_name(j + 1)}{r}"] = h
    fm["bold_rows"].append(r)
    r += 1
    r0 = r
    for role, dep, pay, c1, f1, c2, f2, sc in role_tab:
        for j, val in enumerate([role, pay, dep, c1, f1, c2, f2, sc]):
            cells[f"{tc.col_name(j + 1)}{r}"] = val
        fm["blue"] += [f"B{r}", f"D{r}", f"E{r}", f"F{r}", f"G{r}", f"H{r}"]
        fm["number"][f"B{r}"] = FMT["inr"]
        r += 1
    for nm, col in (("role_pay", "B"), ("role_c1", "D"), ("role_f1", "E"), ("role_c2", "F"), ("role_f2", "G"), ("role_scale", "H")):
        names[nm] = f"{col}{r0}:{col}{r - 1}"
    r += 1
    cells[f"A{r}"] = "Worked out (formulas; do not type here)"
    fm["bold_rows"].append(r)
    r += 1
    for k, label, f, fmt in (("p_rep", "Chance a book's agent is replaced, a month", "=attrition_y/12", "pct3"),
                             ("ho_keep", "Share of a book's savers kept through a month of handovers", "=1-handover_loss*p_rep", "share"),
                             ("seed_amt", "Cash at the start of month 1 (rounds at month 0)", "=SUMIFS(rd_amount,rd_month,0)", "inr"),
                             ("nb_iy", "NBFC: yield a month", "=nb_yield/12", "pct3"),
                             ("nb_lo", "NBFC: on-book lifetime loss (agreed loss x the on-book multiple)", "=nb_loss*nb_loss_mult", "pct2")):
        cells[f"A{r}"], cells[f"B{r}"], cells[f"E{r}"] = label, f, k
        names[k] = f"B{r}"
        fm["number"][f"B{r}"] = FMT[fmt]
        fm["grey"].append(f"B{r}")
        r += 1
    return {"title": "Company inputs", "cells": cells, "named_ranges": names, "formats": fm}


LASTC = tc.col_name(1 + NC)        # the last city column on 'City by month'
CM_BLOCKS = (  # key, title, first row (data), formula in B<first row>
    ("agents", "Agents by city (straight lines between the City plan's tenure points; 0 before launch; whole agents)"),
    ("newbooks", "New books by city (growth hires: the month's increase in agents)"),
    ("unsat", "Sign-ups by city before the slowdown (the books' sign-ups at the agents' own level)"),
    ("cap", "City cap: city_cap x addressable, growing with the pool refill"),
    ("cum", "Cumulative sign-ups by city, after the slowdown 1 - (cumulative / cap) ^ sat_power and the cap"),
    ("signups", "Sign-ups by city"),
)


def cm_rows(i):
    """First and last data row of block i on 'City by month' (a title row, 96 months, a blank row)."""
    r0 = 3 + i * (N + 2)
    return r0, r0 + N - 1


def city_plan_sheet(cplan):
    cells, names = {}, {}
    fm = {"number": {}, "blue": [], "grey": [], "bold_rows": [1, 2], "freeze_rows": 2, "freeze_cols": 1, "wrap_rows": [1],
          "col_widths": {"A": 150, "P": 150, "Q": 110, "R": 130, "S": 110, "T": 110, "U": 110, "V": 110}}
    hdr = ["City", "Rank", "Addressable (urban self-employed; estimate, not census)", "Cap: city_cap x addressable (sign-ups)",
           "Launch month"] + [("Agents in the launch month" if o_ == 0 else f"Agents at launch +{o_} months") for o_ in ct.OFFSETS] + [
           "Month it nears its cap (95%; the full model's AUTO run, information)", "Agents, month 60", "Cumulative sign-ups to month 60",
           "Penetration after month 60 (cumulative / the refilled pool)", "Slowdown after month 60: 1 - (pen / cap) ^ sat_power",
           "Penetration after month 96", "Slowdown after month 96"]
    for j, h in enumerate(hdr):
        cells[f"{tc.col_name(j + 1)}1"] = h
    cells["A2"] = "Tenure point (months after launch) ->"
    for j, o_ in enumerate(ct.OFFSETS):
        cells[f"{tc.col_name(6 + j)}2"] = float(o_)
        fm["grey"].append(f"{tc.col_name(6 + j)}2")
    r0 = 3
    for i, (nm, rk, addr, L, pts, note) in enumerate(cplan):
        r = r0 + i
        cells.update({f"A{r}": nm, f"B{r}": rk, f"C{r}": addr, f"D{r}": f"=city_cap*C{r}", f"E{r}": L})
        for j, a in enumerate(pts):
            cells[f"{tc.col_name(6 + j)}{r}"] = a
        cells[f"P{r}"] = float(note) if str(note).replace(".", "").isdigit() else note
    rl = r0 + len(cplan) - 1
    fm["blue"] += [f"{c}{r}" for c in "ABCE" for r in range(r0, rl + 1)] + [f"{tc.col_name(6 + j)}{r}" for j in range(10) for r in range(r0, rl + 1)]
    fm["grey"] += [f"D{r}" for r in range(r0, rl + 1)]
    names.update({"cp_city": f"A{r0}:A{rl}", "cp_addr": f"C{r0}:C{rl}", "cp_launch": f"E{r0}:E{rl}", "cp_pts": f"F{r0}:O{rl}", "cp_off": "F2:O2"})
    n = len(cplan)
    cells[f"Q{r0}"] = f"=MAKEARRAY({n},1,LAMBDA(ci,z,INDEX(cm_agents,60,ci)))"
    cells[f"R{r0}"] = f"=MAKEARRAY({n},1,LAMBDA(ci,z,INDEX(cm_cum,60,ci)))"
    cells[f"S{r0}"] = f"=MAKEARRAY({n},1,LAMBDA(ci,z,INDEX(cm_cum,60,ci)/(INDEX(cp_addr,ci)*(1+refill)^(60/12))))"
    cells[f"T{r0}"] = f"=ARRAYFORMULA(IF(1-(S{r0}:S{rl}/city_cap)^sat_power>0,1-(S{r0}:S{rl}/city_cap)^sat_power,0))"
    cells[f"U{r0}"] = f"=MAKEARRAY({n},1,LAMBDA(ci,z,INDEX(cm_cum,{N},ci)/(INDEX(cp_addr,ci)*(1+refill)^({N}/12))))"
    cells[f"V{r0}"] = f"=ARRAYFORMULA(IF(1-(U{r0}:U{rl}/city_cap)^sat_power>0,1-(U{r0}:U{rl}/city_cap)^sat_power,0))"
    fm["number"].update({f"B{r0}:B{rl}": "0", f"C{r0}:D{rl}": "#,##0", f"E{r0}:E{rl}": "0", f"F{r0}:O{rl}": "#,##0", "F2:O2": "0",
                         f"P{r0}:P{rl}": "0", f"Q{r0}:R{rl}": "#,##0", f"S{r0}:S{rl}": "0.0%", f"T{r0}:T{rl}": "0.00", f"U{r0}:U{rl}": "0.0%",
                         f"V{r0}:V{rl}": "0.00"})
    return {"title": "City plan", "cells": cells, "named_ranges": names, "formats": fm}


def city_month_sheet(n):
    cells, names = {"A1": "Month", "B1": f"=MAKEARRAY(1,{n},LAMBDA(z,ci,INDEX(cp_city,ci)))"}, {}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "col_widths": {"A": 90}, "copy_rows": {}}
    last = tc.col_name(1 + n)
    rng = lambda i, r_a=None, r_b=None: (lambda a, b: f"B{a}:{last}{b}")(*(cm_rows(i) if r_a is None else (r_a, r_b)))
    for i, (key, title) in enumerate(CM_BLOCKS):
        r0, r1 = cm_rows(i)
        cells[f"A{r0 - 1}"] = title
        fm["bold_rows"].append(r0 - 1)
        cells[f"A{r0}"] = f"=SEQUENCE({N})"
        names[f"cm_{key}"] = rng(i)
        fm["number"][rng(i)] = "#,##0"
    (a0, _), (n0, _), (u0, _), (c0, _), (k0, k1), (s0, _) = [cm_rows(i) for i in range(6)]
    cells[f"B{a0}"] = (f"=MAKEARRAY({N},{n},LAMBDA(m,ci,LET(dd,m-INDEX(cp_launch,ci),IF(dd<0,0,LET(i,MATCH(dd,cp_off,1),j,MIN(i+1,10),"
                       "ROUND(IF(i>=10,INDEX(cp_pts,ci,10),INDEX(cp_pts,ci,i)+(INDEX(cp_pts,ci,j)-INDEX(cp_pts,ci,i))*(dd-INDEX(cp_off,i))"
                       "/MAX(1,INDEX(cp_off,j)-INDEX(cp_off,i))),0))))))")
    cells[f"B{n0}"] = f"=MAKEARRAY({N},{n},LAMBDA(m,ci,INDEX(cm_agents,m,ci)-IF(m=1,0,INDEX(cm_agents,m-1,ci))))"
    cells[f"B{u0}"] = f"=MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,INDEX(cb_signups,m-k+1),0))),cm_newbooks)"
    cells[f"B{c0}"] = f"=MAKEARRAY({N},{n},LAMBDA(m,ci,city_cap*INDEX(cp_addr,ci)*(1+refill)^((m-1)/12)))"
    # cumulative sign-ups: row by row (each row reads the row above), vectorised across the cities
    row = lambda r: f"B{r}:{last}{r}"
    cells[f"B{k0}"] = f"=ARRAYFORMULA(IF({row(u0)}>{row(c0)},{row(c0)},{row(u0)}))"
    for r in range(k0 + 1, k1 + 1):
        dr = r - k0
        U_, CP, PV = row(u0 + dr), row(c0 + dr), row(r - 1)
        fac = f"IF(1-({PV}/{CP})^sat_power>0,1-({PV}/{CP})^sat_power,0)"
        rem = f"IF({CP}-{PV}>0,{CP}-{PV},0)"
        cells[f"B{r}"] = f"=ARRAYFORMULA({PV}+IF({U_}*{fac}>{rem},{rem},{U_}*{fac}))"
    cells[f"B{s0}"] = f"=MAKEARRAY({N},{n},LAMBDA(m,ci,INDEX(cm_cum,m,ci)-IF(m=1,0,INDEX(cm_cum,m-1,ci))))"
    fm["copy_rows"] = {"from_row": k0 + 1, "to_rows": [k0 + 2, k1], "cols": ["B", "B"]}
    return {"title": "City by month", "cells": cells, "named_ranges": names, "formats": fm}


def wsum(b, body):
    """Expected value over the tenure of whoever holds a book of age b (a replacement restarts at tenure 1)."""
    return (f"SUM(MAKEARRAY({b},1,LAMBDA(k,y,({body})*IF(k<{b},p_rep*(1-p_rep)^(k-1),(1-p_rep)^({b}-1)))))")


def conv_ho(ps, vec):
    return f"MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,{ps}*ho_keep^(m-k),0))),{vec})"


def conv_nb(cb):
    return f"MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,INDEX({cb},m-k+1),0))),co_newbooks)"


PB = [  # key, header, formula, format
    ("age", "Book's age (months since it opened)", f"=SEQUENCE({N})", "num0"),
    ("decline", "Sign-up decline on the book's age", f"=MAKEARRAY({N},1,LAMBDA(b,z,IF(b<=12,1,1+(signup_decline_y5-1)*MIN(1,(b-12)/37))))", "f3"),
    ("eramp", "Expected ramp of whoever holds the book", f"=MAKEARRAY({N},1,LAMBDA(b,z," + wsum("b", "IF(ramp>0,MIN(1,0.5+0.5*(k-1)/ramp),1)") + "))", "f3"),
    ("eshare", "Expected acquisition share of his cost",
     f"=MAKEARRAY({N},1,LAMBDA(b,z," + wsum("b", "IF(k<=acq_flat,acq_early,acq_early+(acq_m60-acq_early)*(MIN(k,60)-acq_flat)/(60-acq_flat))") + "))", "f3"),
    ("signups", "Sign-ups a month (before any city slowdown)", "=ARRAYFORMULA(signups*agent_level*cb_decline*cb_eramp)", "num1"),
    ("visits", "Cash visits a day", "=" + conv_ho("INDEX(sv_visits,m-k+1)", "cb_signups"), "num1"),
    ("balance", "Average balance of his savers (₹)", "=" + conv_ho("INDEX(sv_balance,m-k+1)", "cb_signups"), "inr"),
    ("cashdep", "Cash collected a month (₹)", "=" + conv_ho("INDEX(sv_deposits,m-k+1)*(1-INDEX(sv_upi,m-k+1))", "cb_signups"), "inr"),
    ("helpers", "Helpers above his visit capacity (₹ a month)", "=ARRAYFORMULA(IF(cb_visits>capacity,(cb_visits-capacity)*extra_cost/400,0))", "inr"),
    ("cover", "Cash cover (₹ a month)", "=ARRAYFORMULA(IF(cash_cover_rate*cb_cashdep>cash_cover,cash_cover_rate*cb_cashdep,cash_cover))", "inr"),
]


def perbook_sheet():
    cells, names, fm = {}, {}, {"number": {}, "bold_rows": [1], "freeze_rows": 1, "wrap_rows": [1], "col_widths": {"A": 90}}
    for i, (k, h, f, nf) in enumerate(PB, 1):
        c = tc.col_name(i)
        cells[f"{c}1"], cells[f"{c}2"] = h, f
        names[f"cb_{k}"] = f"{c}2:{c}{LAST}"
        fm["number"][f"{c}2:{c}{LAST}"] = FMT[nf]
    return {"title": "Company per book", "cells": cells, "named_ranges": names, "formats": fm}


def monthly_columns(role_tab):
    """[(key, header, kind, formula or (row-2 template, generic template), format)] in column order; kind spill|row|multi."""
    cap = "MIN(INDEX(co_cal_payrate,m)/12*INDEX(cb_balance,m-k+1)*INDEX(co_r_bal,m),incentive_cap*INDEX(co_rm,m))"
    ones = f"SEQUENCE({NC},1,1,0)"
    capf = lambda share: f"IF({share}*co_cal_af>0.8,0.8/{share},co_cal_af)"
    cols = [
        ("month", "Company month", "spill", f"=SEQUENCE({N})", "num0"),
        ("year", "Company year", "spill", "=ARRAYFORMULA(INT((co_month-1)/12)+1)", "num0"),
        # calendar factors (the toy's 'Monthly' factors, held after year_hold; the fee ramp held after month 60)
        ("cal_yc", "Calendar year for the growth factors (held after year_hold)", "spill",
         "=ARRAYFORMULA(IF(co_year>year_hold,year_hold,co_year))", "num0"),
        ("cal_tf", "Take-up growth factor (cap 2x)", "spill",
         "=ARRAYFORMULA(IF((1+takeup_growth)^(co_cal_yc-1)>2,2,(1+takeup_growth)^(co_cal_yc-1)))", "f3"),
        ("cal_af", "Approval growth factor", "spill", "=ARRAYFORMULA((1+approval_growth)^(co_cal_yc-1))", "f3"),
        ("cal_loanf", "Loan factor (take-up x first-loan approval, cap 80%)", "spill", f"=ARRAYFORMULA(co_cal_tf*{capf('approved_first')})", "f3"),
        ("cal_cardf", "Card factor", "spill", "=ARRAYFORMULA(co_cal_tf*IF(co_cal_af>2,2,co_cal_af))", "f3"),
        ("cal_homef", "Home-loan factor", "spill", f"=ARRAYFORMULA(co_cal_tf*{capf('home_approval')})", "f3"),
        ("cal_lapf", "LAP factor", "spill", f"=ARRAYFORMULA(co_cal_tf*{capf('lap_approval')})", "f3"),
        ("cal_pool", "Never-borrowed pool adjustment", "spill",
         "=ARRAYFORMULA(SCAN(1,co_cal_loanf,LAMBDA(acc,f,acc*(1-loan_q*f)/(1-loan_q)))*(1-loan_q)/(1-loan_q*co_cal_loanf))", "f3"),
        ("cal_lf0", "Loan line factor, this month", "spill", "=ARRAYFORMULA(co_cal_loanf*co_cal_pool)", "f3"),
        ("cal_lf12", "Loan line factor, 12 months earlier (collections)", "spill", f"=MAKEARRAY({N},1,LAMBDA(m,k,INDEX(co_cal_lf0,MAX(1,m-12))))", "f3"),
        ("cal_lf20", "Loan line factor, 20 months earlier (top-ups)", "spill", f"=MAKEARRAY({N},1,LAMBDA(m,k,INDEX(co_cal_lf0,MAX(1,m-20))))", "f3"),
        ("cal_fee", "Loan fee rate this month (the round-9 ramp, held at month 60)", "spill",
         "=ARRAYFORMULA(fee*(fee_mult_start+(fee_mult_end-fee_mult_start)*(IF(co_month>60,60,co_month)-1)/59))", "pct3"),
        ("cal_payrate", "Agent pay rate on balance this month (a year)", "spill", "=ARRAYFORMULA(IF(co_month<=pay_months,agent_pay,pay_after))", "pct2"),
        # the fleet
        ("agents", "Agents working (summed from the City plan)", "spill", f"=ARRAYFORMULA(MMULT(cm_agents,{ones}))", "num0"),
        ("fleet_path", "Check: the fleet path from Company inputs (300 by m18, +150 a month, cap 5,000)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,ROUND(MIN(agent_cap,IF(m<=18,LET(i,MATCH(m,plan_m,1),IF(i>=ROWS(plan_m),INDEX(plan_s,i),INDEX(plan_s,i)"
         "+(INDEX(plan_s,i+1)-INDEX(plan_s,i))*(m-INDEX(plan_m,i))/(INDEX(plan_m,i+1)-INDEX(plan_m,i))))*agents_m18/INDEX(plan_s,"
         "ROWS(plan_s)),agents_m18+hires_after*(m-18))),0)))", "num0"),
        ("newbooks", "New books (growth hires, summed from the cities)", "spill", f"=ARRAYFORMULA(MMULT(cm_newbooks,{ones}))", "num0"),
        ("cumleave", "Expected leavers to date", "spill", "=SCAN(0,co_agents,LAMBDA(acc,v,acc+attrition_y/12*v))", "num1"),
        ("leavers", "Agents who leave (end of month, whole agents)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,INT(INDEX(co_cumleave,m)+1E-9)-IF(m=1,0,INT(INDEX(co_cumleave,m-1)+1E-9))))", "num0"),
        ("hired", "Agents hired (growth + replacements)", "spill", f"=MAKEARRAY({N},1,LAMBDA(m,k,INDEX(co_newbooks,m)+IF(m=1,0,INDEX(co_leavers,m-1))))", "num0"),
        ("cities", "Cities open (launched by this month, City plan)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,SUM(MAKEARRAY({NC},1,LAMBDA(ci,z,IF(INDEX(cp_launch,ci)<=m,1,0))))))", "num0"),
        ("teamleads", "Team leads", "spill", "=ARRAYFORMULA(ROUNDUP(co_agents/agents_per_tl,0))", "num0"),
        ("rm", "Pay rise factor (7% a company year)", "spill", "=ARRAYFORMULA((1+raise_rate)^(co_year-1))", "f3"),
        ("extra", "Engineer and ops scale-up (each), before any lean hold", "spill",
         "=ARRAYFORMULA(IF(co_month>scale_after,INT(IF(co_agents>scale_base,co_agents-scale_base,0)/scale_per),0))", "num0"),
        ("hc_steps", "Launch team by role (no scale-ups) ->", "multi",
         f"=MAKEARRAY({N},8,LAMBDA(m,j,IF(m>=INDEX(role_f2,j),INDEX(role_c2,j),IF(m>=INDEX(role_f1,j),INDEX(role_c1,j),0))))", "num0"),
        ("risk_raw", "Risk lead if no hold", "spill", "=ARRAYFORMULA(IF(SCAN(0,co_agents,LAMBDA(acc,v,MAX(acc,v)))>=risk_agents,1,0))", "num0"),
        ("hc_roles", "Central team by role, final ->", "multi",
         f"=MAKEARRAY({N},8,LAMBDA(m,j,INDEX(co_hc_steps,m,j)+INDEX(role_scale,j)*IF(m>co_hold,INDEX(co_extra,m),0)))", "num0"),
        ("risk", "Risk and fraud lead", "spill", "=ARRAYFORMULA(IF(co_month>co_hold,co_risk_raw,0))", "num0"),
        ("cashrec", "Cash reconciliation executives", "spill", "=ARRAYFORMULA(ROUNDUP(co_agents/cashrec_per,0))", "num0"),
        ("hr", "HR and recruiting executives", "spill", "=ARRAYFORMULA(ROUNDUP(co_agents/hr_per,0))", "num0"),
        ("support", "Customer support lead", "spill", "=ARRAYFORMULA(IF(co_month>co_hold,co_support_raw,0))", "num0"),
        ("hc_central", "Central team, total", "spill", "=ARRAYFORMULA(MMULT(co_hc_roles,SEQUENCE(8,1,1,0))+co_risk+co_cashrec+co_hr+co_support)", "num0"),
        ("pay_central", "Central team pay incl. statutory (₹)", "spill",
         "=ARRAYFORMULA((MMULT(co_hc_roles,role_pay)+co_risk*risk_pay+co_cashrec*cashrec_pay+co_hr*hr_pay+co_support*support_pay)*co_rm*(1+statutory))", "inr"),
        ("pay_held", "Central pay if a lean hold ran all 96 months (₹)", "spill",
         "=ARRAYFORMULA((MMULT(co_hc_steps,role_pay)+co_cashrec*cashrec_pay+co_hr*hr_pay)*co_rm*(1+statutory))", "inr"),
        ("tools_held", "Tools if held (₹)", "spill", "=ARRAYFORMULA((MMULT(co_hc_steps,SEQUENCE(8,1,1,0))+co_cashrec+co_hr)*tools)", "inr"),
        ("joiners", "Central joiners (laptops)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,z,SUM(MAKEARRAY(1,12,LAMBDA(q,j,MAX(0,INDEX(co_hc_all,m,j)-IF(m=1,0,INDEX(co_hc_all,m-1,j))))))))", "num0"),
        # customers and lending
        ("signups", "Sign-ups (summed from the cities, after the city slowdown)", "spill", f"=ARRAYFORMULA(MMULT(cm_signups,{ones}))", "num0"),
        ("signups_unsat", "Sign-ups before the city slowdown", "spill", f"=ARRAYFORMULA(MMULT(cm_unsat,{ones}))", "num0"),
        ("signups_adj", "Sign-ups / pool adjustment (loan lines)", "spill", "=ARRAYFORMULA(co_signups/co_cal_pool)", "num0"),
        ("savers", "Savers still saving", "spill", "=" + conv_ho("INDEX(sv_saving,m-k+1)", "co_signups"), "num0"),
        ("support_raw", "Support lead if no hold", "spill",
         "=ARRAYFORMULA(IF(SCAN(0,co_savers,LAMBDA(acc,v,MAX(acc,v)))>=support_savers,1,0))", "num0"),
        ("balance", "Average fund balance (₹)", "spill", "=" + conv_ho("INDEX(sv_balance,m-k+1)", "co_signups"), "inr"),
        ("aum", "Money in the fund at month end, AUM (₹)", "spill", "=" + conv_ho("INDEX(sv_saving,m-k+1)*INDEX(sv_endbal,m-k+1)", "co_signups"), "inr"),
        ("cashdep", "Cash collected from savers (₹)", "spill", "=" + conv_ho("INDEX(sv_deposits,m-k+1)*(1-INDEX(sv_upi,m-k+1))", "co_signups"), "inr"),
        ("visits", "Cash visits a day, all agents", "spill", "=" + conv_ho("INDEX(sv_visits,m-k+1)", "co_signups"), "num0"),
        ("bal_u", "Average fund balance if no city slowed (₹)", "spill", "=" + conv_ho("INDEX(sv_balance,m-k+1)", "co_signups_unsat"), "inr"),
        ("vis_u", "Cash visits a day if no city slowed", "spill", "=" + conv_ho("INDEX(sv_visits,m-k+1)", "co_signups_unsat"), "num0"),
        ("cd_u", "Cash collected if no city slowed (₹)", "spill", "=" + conv_ho("INDEX(sv_deposits,m-k+1)*(1-INDEX(sv_upi,m-k+1))", "co_signups_unsat"), "inr"),
        ("r_bal", "Saturation ratio for the per-book costs: balance / balance if no city slowed", "spill",
         "=ARRAYFORMULA(IF(co_bal_u>0,co_balance/IF(co_bal_u>0,co_bal_u,1),1))", "f3"),
        ("r_vis", "...visits / visits if no city slowed", "spill", "=ARRAYFORMULA(IF(co_vis_u>0,co_visits/IF(co_vis_u>0,co_vis_u,1),1))", "f3"),
        ("r_cd", "...cash collected / cash if no city slowed", "spill", "=ARRAYFORMULA(IF(co_cd_u>0,co_cashdep/IF(co_cd_u>0,co_cd_u,1),1))", "f3"),
        ("apps", "Loan applications", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_apps,m-k+1)", "co_signups_adj") + "*co_cal_tf*co_cal_pool)", "num1"),
        ("loans", "Personal loans (first and repeat)", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_loans,m-k+1)", "co_signups_adj") + "*co_cal_lf0)", "num1"),
        ("topups", "Top-ups", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_topups,m-k+1)", "co_signups_adj") + "*co_cal_lf20)", "num1"),
        ("lent_new", "Money lent, new loans (₹)", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_lent,m-k+1)", "co_signups_adj") + "*co_cal_lf0)", "inr"),
        ("lent", "Money lent incl. top-ups (₹)", "spill", "=ARRAYFORMULA(co_lent_new+co_topups*topup_amt)", "inr"),
        ("home_n", "Home loans (other lenders)", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_home,m-k+1)", "co_signups") + "*co_cal_homef)", "num1"),
        ("lap_n", "LAP loans (other lenders)", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_lap,m-k+1)", "co_signups") + "*co_cal_lapf)", "num1"),
        ("housing_lent", "Home loans and LAP lent by other lenders (₹)", "spill", "=ARRAYFORMULA(co_home_n*home_ticket+co_lap_n*lap_ticket)", "inr"),
        # the NBFC's share of personal-loan volume
        ("nb_share", "NBFC: on-book share of personal-loan volume", "spill", "=ARRAYFORMULA(IF(co_month>=nb_start,nb_share,0))", "pct"),
        ("nb_share12", "NBFC: on-book share 12 months earlier (the loans collection fees come from)", "spill",
         "=ARRAYFORMULA(IF(co_month-12>=nb_start,nb_share,0))", "pct"),
        ("nb_disb", "NBFC: on-book loans disbursed (₹)", "spill", "=ARRAYFORMULA(co_nb_share*co_lent)", "inr"),
        # fee revenue
        ("r_fund", "Revenue: fund trail (₹)", "spill", "=ARRAYFORMULA(co_balance*trail/12)", "inr"),
        ("r_orig", "Revenue: personal-loan origination, DSA fees on the partners' share (₹)", "spill",
         "=ARRAYFORMULA(co_lent_new*co_cal_fee*(1-taken_back)*(1-co_nb_share))", "inr"),
        ("r_topup", "Revenue: top-up origination, partners' share (₹)", "spill", "=ARRAYFORMULA(co_topups*topup_amt*co_cal_fee*(1-taken_back)*(1-co_nb_share))", "inr"),
        ("r_house", "Revenue: home loans and LAP (₹)", "spill",
         "=ARRAYFORMULA(co_home_n*home_ticket*home_fee+co_lap_n*lap_ticket*lap_fee)", "inr"),
        ("xs", "Cross-sell, 17 products (₹)", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_xs,m-k+1)", "co_signups") + "*co_cal_tf)", "inr"),
        ("r_ins", "Revenue: insurance (₹)", "spill", "=ARRAYFORMULA(co_xs*xs_ins)", "inr"),
        ("r_inv", "Revenue: investments (₹)", "spill", "=ARRAYFORMULA(co_xs*xs_inv)", "inr"),
        ("r_pay", "Revenue: payments (₹)", "spill", "=ARRAYFORMULA(co_xs*xs_pay)", "inr"),
        ("r_oth", "Revenue: other lenders' loans (₹)", "spill", "=ARRAYFORMULA(co_xs*xs_oth)", "inr"),
        ("r_cards", "Revenue: cards (₹)", "spill", "=ARRAYFORMULA(" + conv_ho("INDEX(sv_cards,m-k+1)", "co_signups") + "*co_cal_cardf*card_fee)", "inr"),
        ("r_coll", "Revenue: collection fees, partners' loans (₹)", "spill",
         "=ARRAYFORMULA(" + conv_ho("INDEX(sv_collect,m-k+1)", "co_signups_adj") + "*co_cal_lf12*(1-co_nb_share12))", "inr"),
        ("fee_rev", "Fee revenue, total (₹)", "spill",
         "=ARRAYFORMULA(co_r_fund+co_r_orig+co_r_topup+co_r_house+co_r_ins+co_r_inv+co_r_pay+co_r_oth+co_r_cards+co_r_coll)", "inr"),
        # the book
        ("nb_book_gross", "NBFC: loan book, scheduled (gross; EMIs at the yield over the tenure) (₹)", "spill",
         f"=MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(AND(m>=k,m-k<=tenure_m),((1+nb_iy)^tenure_m-(1+nb_iy)^(m-k))/((1+nb_iy)^tenure_m-1),0))),co_nb_disb)", "inr"),
        ("nb_book", "NBFC: loan book, net of provisions (₹)", "spill", "=ARRAYFORMULA((1-nb_lo)*co_nb_book_gross)", "inr"),
        ("nb_interest", "NBFC: interest income on the book (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,IF(m=1,0,nb_iy*(1-nb_lo)*INDEX(co_nb_book_gross,m-1))))", "inr"),
        ("nb_equity", "NBFC: equity in the book (capital held: the larger of NOF and book / (1 + leverage)) (₹)", "spill",
         "=ARRAYFORMULA(IF(co_month>=nb_licence_month,IF(co_nb_book/(1+nb_leverage)>nb_nof,co_nb_book/(1+nb_leverage),nb_nof),0))", "inr"),
        ("nb_borrow", "NBFC: borrowings (₹)", "spill", "=ARRAYFORMULA(IF(co_nb_book-co_nb_equity>0,co_nb_book-co_nb_equity,0))", "inr"),
        ("nb_idle", "NBFC: capital held but not yet lent (₹)", "spill", "=ARRAYFORMULA(IF(co_nb_equity-co_nb_book>0,co_nb_equity-co_nb_book,0))", "inr"),
        ("nb_cof", "NBFC: cost of funds on borrowings (₹)", "spill", f"=MAKEARRAY({N},1,LAMBDA(m,k,IF(m=1,0,nb_cof/12*INDEX(co_nb_borrow,m-1))))", "inr"),
        ("nb_nii", "NBFC: net interest income (₹)", "spill", "=ARRAYFORMULA(co_nb_interest-co_nb_cof)", "inr"),
        ("nb_proc", "NBFC: processing fees (₹)", "spill", "=ARRAYFORMULA(nb_proc*co_nb_disb)", "inr"),
        ("revenue", "Revenue, total: fees + net interest income + processing fees (₹)", "spill", "=ARRAYFORMULA(co_fee_rev+co_nb_nii+co_nb_proc)", "inr"),
        ("c_bureau", "Direct: bureau pulls (₹)", "spill", "=ARRAYFORMULA(bureau*(co_apps+co_topups))", "inr"),
        ("c_fraud", "Direct: fraud provision (₹)", "spill", "=ARRAYFORMULA(fraud*co_cashdep)", "inr"),
        ("direct", "Direct costs (₹)", "spill", "=ARRAYFORMULA(co_c_bureau+co_c_fraud)", "inr"),
        ("nb_credit", "Credit cost: expected-loss provisions on the book (₹)", "spill", "=ARRAYFORMULA(nb_lo*co_nb_disb)", "inr"),
        ("cm1", "CM1, after credit cost (₹)", "spill", "=ARRAYFORMULA(co_revenue-co_direct-co_nb_credit)", "inr"),
        ("agent_base", "Memo: agent salary + statutory (₹)", "spill", "=ARRAYFORMULA(co_agents*(salary+agent_stat)*co_rm)", "inr"),
        ("incentive", "Memo: agent pay on balance, capped per agent (₹)", "spill",
         f"=MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,{cap},0))),co_newbooks)", "inr"),
        ("agent_acq", "Agent cost, acquisition share (₹)", "spill",
         "=ARRAYFORMULA(co_rm*(salary+agent_stat)*" + conv_nb("cb_eshare")
         + f"+MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,INDEX(cb_eshare,m-k+1)*{cap},0))),co_newbooks))", "inr"),
        ("agent_serv", "Servicing: agent cost, servicing share (₹)", "spill", "=ARRAYFORMULA(co_agent_base+co_incentive-co_agent_acq)", "inr"),
        ("helpers", "Servicing: helpers for cash visits (per book, x the visits ratio) (₹)", "spill",
         f"=MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,LET(vv,INDEX(cb_visits,m-k+1)*INDEX(co_r_vis,m),IF(vv>capacity,(vv-capacity)*extra_cost/400,0)),0))),co_newbooks)", "inr"),
        ("cover", "Servicing: cash cover (per book, x the cash ratio) (₹)", "spill",
         f"=MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(m>=k,LET(cc,INDEX(cb_cashdep,m-k+1)*INDEX(co_r_cd,m),IF(cash_cover_rate*cc>cash_cover,cash_cover_rate*cc,cash_cover)),0))),co_newbooks)", "inr"),
        ("running", "Servicing: running cost per saver (₹)", "spill", "=ARRAYFORMULA(co_savers*running)", "inr"),
        ("tl_cost", "Servicing: team leads (₹)", "spill", "=ARRAYFORMULA(co_teamleads*team_lead_pay*co_rm*(1+statutory))", "inr"),
        ("cm_cost", "Servicing: city managers (₹)", "spill", "=ARRAYFORMULA(co_cities*city_mgr_pay*co_rm*(1+statutory))", "inr"),
        ("office_cost", "Servicing: city offices (₹)", "spill", "=ARRAYFORMULA(co_cities*city_office)", "inr"),
        ("servicing", "Field servicing (₹)", "spill",
         "=ARRAYFORMULA(co_agent_serv+co_helpers+co_cover+co_running+co_tl_cost+co_cm_cost+co_office_cost)", "inr"),
        ("cm2", "CM2 (₹)", "spill", "=ARRAYFORMULA(co_cm1-co_servicing)", "inr"),
        ("leads", "Acquisition: online leads (₹)", "spill", "=ARRAYFORMULA(co_signups*online_lead_share*lead_cost)", "inr"),
        ("kyc_cost", "Acquisition: KYC (₹)", "spill", "=ARRAYFORMULA(co_signups*kyc)", "inr"),
        ("kit", "Acquisition: agent hiring and kit (₹)", "spill", "=ARRAYFORMULA(co_hired*agent_kit)", "inr"),
        ("launch", "Acquisition: city launch (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,(INDEX(co_cities,m)-IF(m=1,0,INDEX(co_cities,m-1)))*city_launch))", "inr"),
        ("brand_cost", "Acquisition: brand marketing (₹)", "spill", "=ARRAYFORMULA(brand+0*co_month)", "inr"),
        ("acquisition", "Acquisition (₹)", "spill", "=ARRAYFORMULA(co_agent_acq+co_leads+co_kyc_cost+co_kit+co_launch+co_brand_cost)", "inr"),
        ("cm3", "CM3 (₹)", "spill", "=ARRAYFORMULA(co_cm2-co_acquisition)", "inr"),
        ("app_cost", "Central: app cloud, SMS, KYC tools (₹)", "spill", "=ARRAYFORMULA(app_base+0*co_month)", "inr"),
        ("lic_y", "Central: licences, yearly (₹)", "spill", "=ARRAYFORMULA(lic_year/12+0*co_month)", "inr"),
        ("lic_o", "Central: licences, one-time (₹)", "spill", "=ARRAYFORMULA(IF(co_month=1,lic_once,0))", "inr"),
        ("hq_cost", "Central: head office (₹)", "spill", "=ARRAYFORMULA(hq+0*co_month)", "inr"),
        ("travel_cost", "Central: travel (₹)", "spill", "=ARRAYFORMULA(travel+0*co_month)", "inr"),
        ("raise_cost", "Central: fund-raising costs (seed cost in month 1; each later round in its month) (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,IF(m=1,seed_cost,0)+SUMIFS(rd_cost,rd_month,m)))", "inr"),
        ("nb_opex", "Central: NBFC opex (credit, risk, compliance, treasury; scales with the book) (₹)", "spill",
         "=ARRAYFORMULA(IF(co_month>=nb_licence_month,nb_opex+nb_opex_500*co_nb_book/5000000000,0))", "inr"),
        ("nb_lic", "Central: NBFC licence, one-time (₹)", "spill", "=ARRAYFORMULA(IF(co_month=nb_licence_month,nb_licence_cost,0))", "inr"),
        ("ebitda_held", "EBITDA if a lean hold ran all 96 months (sets the hold when lean_hold = 1) (₹)", "spill",
         "=ARRAYFORMULA(co_cm3-((co_pay_held+co_tools_held+co_app_cost+co_lic_y+co_lic_o+co_hq_cost+co_travel_cost+co_raise_cost+co_nb_opex+co_nb_lic)*(1+contingency)"
         "+contingency*(co_direct+co_servicing+co_acquisition)))", "inr"),
        ("tools_cost", "Central: tools (₹)", "spill", "=ARRAYFORMULA(co_hc_central*tools)", "inr"),
        ("contingency_cost", "Central: contingency (₹)", "spill",
         "=ARRAYFORMULA(contingency*(co_direct+co_servicing+co_acquisition+co_pay_central+co_app_cost+co_lic_y+co_lic_o+co_hq_cost+co_travel_cost"
         "+co_raise_cost+co_nb_opex+co_nb_lic+co_tools_cost))", "inr"),
        ("central", "Central costs (₹)", "spill",
         "=ARRAYFORMULA(co_pay_central+co_app_cost+co_lic_y+co_lic_o+co_hq_cost+co_travel_cost+co_raise_cost+co_nb_opex+co_nb_lic+co_tools_cost+co_contingency_cost)", "inr"),
        ("ebitda", "EBITDA (₹)", "spill", "=ARRAYFORMULA(co_cm3-co_central)", "inr"),
        ("capex_lap", "Capex: laptops (₹)", "spill", "=ARRAYFORMULA(co_joiners*laptop)", "inr"),
        ("capex_int", "Capex: app integrations (₹)", "spill", "=ARRAYFORMULA(IF(co_month<=3,integrations/3,0))", "inr"),
        ("depreciation", "Depreciation (₹)", "spill",
         f"=ARRAYFORMULA(MMULT(MAKEARRAY({N},{N},LAMBDA(m,k,IF(AND(m>=k,m-k<dep_months),1/dep_months,0))),co_capex_lap+co_capex_int))", "inr"),
        ("ebit", "EBIT (₹)", "spill", "=ARRAYFORMULA(co_ebitda-co_depreciation)", "inr"),
        ("cf_receivable", "Cash flow: less increase in commissions receivable (fee revenue arrives 2 months late) (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,-(INDEX(co_fee_rev,m)-IF(m>2,INDEX(co_fee_rev,m-2),0))))", "inr"),
        ("cf_book", "Cash flow, investing: loan book growth and NBFC capital held (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,-(INDEX(co_nb_book,m)-IF(m=1,0,INDEX(co_nb_book,m-1)))-(INDEX(co_nb_idle,m)-IF(m=1,0,INDEX(co_nb_idle,m-1)))))", "inr"),
        ("cf_investing", "Cash from investing (₹)", "spill", "=ARRAYFORMULA(-(co_capex_lap+co_capex_int)+co_cf_book)", "inr"),
        ("cf_borrow", "Cash flow, financing: NBFC borrowings (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,INDEX(co_nb_borrow,m)-IF(m=1,0,INDEX(co_nb_borrow,m-1))))", "inr"),
        ("cf_financing", "Cash from financing: equity, the rounds landing this month (₹)", "spill",
         f"=MAKEARRAY({N},1,LAMBDA(m,k,SUMIFS(rd_amount,rd_land,m)))", "inr"),
        ("arr", "ARR (12 x the month's fees + NII + processing fees) (₹)", "spill", "=ARRAYFORMULA(12*co_revenue)", "inr"),
        ("fee_arr", "Fee ARR (12 x the month's fee revenue) (₹)", "spill", "=ARRAYFORMULA(12*co_fee_rev)", "inr"),
        ("rev_lens", "Lens 1: arr_mult x ARR (our judgement) (₹)", "spill", "=ARRAYFORMULA(arr_mult*co_arr)", "inr"),
        ("aum_lens", "Lens 2: aum_mult x AUM (our judgement) (₹)", "spill", "=ARRAYFORMULA(aum_mult*co_aum)", "inr"),
        ("book_lens", "Lens 3 (cross-check): pb_mult x NBFC equity + arr_mult x fee ARR (our judgement) (₹)", "spill",
         "=ARRAYFORMULA(pb_mult*co_nb_equity+arr_mult*co_fee_arr)", "inr"),
        # the treasury: row by row (interest on the opening cash, tax after past losses)
        ("opening", "Opening cash (₹; month 1 = the rounds at month 0)", "row", ("=seed_amt", "={cash}{p}"), "inr"),
        ("interest", "Interest on cash (₹)", "row", ("=interest_rate/12*MAX(0,{opening}{r})", "=interest_rate/12*MAX(0,{opening}{r})"), "inr"),
        ("pbt", "Profit before tax (₹)", "row", ("={ebit}{r}+{interest}{r}", "={ebit}{r}+{interest}{r}"), "inr"),
        ("losses", "Tax losses carried forward (₹)", "row",
         ("=MAX(0,-{pbt}{r})", "={losses}{p}-MIN({losses}{p},MAX({pbt}{r},0))+MAX(0,-{pbt}{r})"), "inr"),
        ("tax", "Income tax (₹)", "row", ("=tax_rate*MAX(0,{pbt}{r})", "=tax_rate*MAX(0,{pbt}{r}-MIN({losses}{p},MAX({pbt}{r},0)))"), "inr"),
        ("pat", "PAT (₹)", "row", ("={pbt}{r}-{tax}{r}", "={pbt}{r}-{tax}{r}"), "inr"),
        ("cfo", "Cash from operations (₹)", "row", ("={pat}{r}+{depreciation}{r}+{cf_receivable}{r}", "={pat}{r}+{depreciation}{r}+{cf_receivable}{r}"), "inr"),
        ("net", "Net change in cash (₹)", "row", ("={cfo}{r}+{cf_investing}{r}+{cf_financing}{r}+{cf_borrow}{r}",
                                                  "={cfo}{r}+{cf_investing}{r}+{cf_financing}{r}+{cf_borrow}{r}"), "inr"),
        ("cash", "Closing cash, with every round (₹)", "row", ("={net}{r}", "={cash}{p}+{net}{r}"), "inr"),
    ]
    return cols


def monthly_sheet(role_tab):
    cols = monthly_columns(role_tab)
    letters, c = {}, 1
    for key, _h, kind, _f, _nf in cols:
        letters[key] = tc.col_name(c)
        c += 8 if kind == "multi" else 1
    cells, names = {}, {}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "freeze_cols": 1, "wrap_rows": [1], "col_widths": {},
          "copy_down": {"from_row": 3, "to_rows": [4, LAST]}}
    rowkeys = []
    for key, h, kind, f, nf in cols:
        L = letters[key]
        if kind == "multi":
            names[f"co_{key}"] = f"{L}2:{tc.col_name(tc.col_num(L) + 7)}{LAST}"
            for j, rr in enumerate(role_tab):
                cc = tc.col_name(tc.col_num(L) + j)
                cells[f"{cc}1"] = f"{h.split(' ->')[0]}: {rr[0]}"
                fm["number"][f"{cc}2:{cc}{LAST}"] = FMT[nf]
            cells[f"{L}2"] = f
            continue
        cells[f"{L}1"] = h
        names[f"co_{key}"] = f"{L}2:{L}{LAST}"
        fm["number"][f"{L}2:{L}{LAST}"] = FMT[nf]
        if kind == "spill":
            cells[f"{L}2"] = f
        else:
            rowkeys.append(key)
            t2, tg = f
            for r in range(2, LAST + 1):
                tmpl = t2 if r == 2 else tg
                cells[f"{L}{r}"] = tmpl.format(r=r, p=r - 1, **letters)
    first_role = letters["hc_roles"]
    names["co_hc_all"] = f"{first_role}2:{letters['support']}{LAST}"
    fm["row_cols"] = [letters[k] for k in rowkeys]
    return {"title": "Company monthly", "cells": cells, "named_ranges": names, "formats": fm}, letters


YEARLY = [  # label, named range, how (sum|end|pct)
    ("Agents working (year end)", "co_agents", "end"), ("Agents hired (growth + replacements)", "co_hired", "sum"),
    ("Agents who left", "co_leavers", "sum"), ("Cities open (year end)", "co_cities", "end"), ("Central team (year end)", "co_hc_central", "end"),
    ("Team leads (year end)", "co_teamleads", "end"), ("Sign-ups", "co_signups", "sum"), ("Savers still saving (year end)", "co_savers", "end"),
    ("AUM (year end, ₹)", "co_aum", "end"), ("Money lent, personal loans incl. top-ups (₹)", "co_lent", "sum"),
    ("Money lent, home loans and LAP by other lenders (₹)", "co_housing_lent", "sum"),
    ("Revenue: fund trail", "co_r_fund", "sum"), ("Revenue: personal-loan origination", "co_r_orig", "sum"),
    ("Revenue: top-up origination", "co_r_topup", "sum"), ("Revenue: home loans and LAP", "co_r_house", "sum"),
    ("Revenue: other lenders' loans", "co_r_oth", "sum"), ("Revenue: cards", "co_r_cards", "sum"), ("Revenue: insurance", "co_r_ins", "sum"),
    ("Revenue: investments", "co_r_inv", "sum"), ("Revenue: payments", "co_r_pay", "sum"), ("Revenue: collection fees", "co_r_coll", "sum"),
    ("Fee revenue, total", "co_fee_rev", "sum"), ("NBFC: interest income", "co_nb_interest", "sum"), ("NBFC: cost of funds", "co_nb_cof", "sum"),
    ("NBFC: net interest income", "co_nb_nii", "sum"), ("NBFC: processing fees", "co_nb_proc", "sum"),
    ("Revenue, total (fees + net interest income + processing fees)", "co_revenue", "sum"), ("Direct costs", "co_direct", "sum"),
    ("Credit cost: provisions on the book", "co_nb_credit", "sum"), ("CM1 (after credit cost)", "co_cm1", "sum"), ("CM1, share of revenue", "co_cm1", "pct"),
    ("Field servicing", "co_servicing", "sum"), ("CM2", "co_cm2", "sum"), ("CM2, share of revenue", "co_cm2", "pct"),
    ("Acquisition", "co_acquisition", "sum"), ("CM3", "co_cm3", "sum"), ("CM3, share of revenue", "co_cm3", "pct"),
    ("Central costs", "co_central", "sum"), ("  of which central team pay", "co_pay_central", "sum"), ("  of which NBFC opex", "co_nb_opex", "sum"),
    ("  of which NBFC licence", "co_nb_lic", "sum"), ("EBITDA", "co_ebitda", "sum"),
    ("EBITDA, share of revenue", "co_ebitda", "pct"), ("Depreciation", "co_depreciation", "sum"), ("EBIT", "co_ebit", "sum"),
    ("Interest on cash", "co_interest", "sum"), ("Profit before tax", "co_pbt", "sum"), ("Income tax", "co_tax", "sum"), ("PAT", "co_pat", "sum"),
    ("Cash from operations", "co_cfo", "sum"), ("Cash from investing (incl. the loan book and NBFC capital)", "co_cf_investing", "sum"),
    ("  of which the loan book and NBFC capital", "co_cf_book", "sum"), ("Cash from financing: equity raised", "co_cf_financing", "sum"),
    ("Cash from financing: NBFC borrowings", "co_cf_borrow", "sum"), ("Net change in cash", "co_net", "sum"),
    ("Closing cash, with every round (year end)", "co_cash", "end"),
    ("NBFC: loan book, net (year end)", "co_nb_book", "end"), ("NBFC: equity in the book (year end)", "co_nb_equity", "end"),
    ("NBFC: borrowings (year end)", "co_nb_borrow", "end"),
    ("ARR at year end (12 x December's fees + NII + processing fees)", "co_arr", "end"), ("Lens 1 at year end (our judgement)", "co_rev_lens", "end"),
    ("Lens 2 at year end (our judgement)", "co_aum_lens", "end"), ("Lens 3 at year end (cross-check; our judgement)", "co_book_lens", "end"),
]
YEARS = N // 12


def yearly_sheet():
    cells = {"A1": "Line (₹ unless stated). Years 6-8 are context; the unicorn check is at month 60",
             f"{tc.col_name(YEARS + 2)}1": "Years 1-5", f"{tc.col_name(YEARS + 3)}1": f"Years 1-{YEARS}"}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "wrap_rows": [1], "col_widths": {"A": 400}}
    for y in range(1, YEARS + 1):
        cells[f"{tc.col_name(y + 1)}1"] = y
    c5, cN = tc.col_name(YEARS + 2), tc.col_name(YEARS + 3)
    for i, (label, nm, how) in enumerate(YEARLY, start=2):
        cells[f"A{i}"] = label
        for y in range(1, YEARS + 1):
            c = tc.col_name(y + 1)
            if how == "sum":
                cells[f"{c}{i}"] = f"=SUMIFS({nm},co_year,{c}$1)"
            elif how == "end":
                cells[f"{c}{i}"] = f"=INDEX({nm},12*{c}$1)"
            else:
                cells[f"{c}{i}"] = f"=IFERROR(SUMIFS({nm},co_year,{c}$1)/SUMIFS(co_revenue,co_year,{c}$1),\"\")"
        if how == "sum":
            cells[f"{c5}{i}"], cells[f"{cN}{i}"] = f"=SUM(FILTER({nm},co_year<=5))", f"=SUM({nm})"
        elif how == "end":
            cells[f"{c5}{i}"], cells[f"{cN}{i}"] = f"=INDEX({nm},60)", f"=INDEX({nm},{N})"
        else:
            cells[f"{c5}{i}"] = f"=IFERROR(SUM(FILTER({nm},co_year<=5))/SUM(FILTER(co_revenue,co_year<=5)),\"\")"
            cells[f"{cN}{i}"] = f"=IFERROR(SUM({nm})/SUM(co_revenue),\"\")"
        fm["number"][f"B{i}:{cN}{i}"] = "0.0%" if how == "pct" else "#,##0"
    return {"title": "Company yearly", "cells": cells, "named_ranges": {}, "formats": fm}


def funding_sheet(o, Iv, rounds):
    """Post-money, dilution and the cap table after each round; the unicorn check. Returns (sheet, expected cells)."""
    FI = ct.funding_inputs()
    ctab = ct.cap_table(rounds, Iv["esop_target"])
    full = {r["Round"]: r for r in ct.csv.DictReader(ct.ROUNDS_CSV.open())}
    L60 = next(r for r in ct.csv.DictReader((T / "base_lenses.csv").open()) if r["Month"] == "60")
    cells, names, exp = {}, {}, []
    fm = {"number": {}, "blue": [], "grey": [], "bold_rows": [1, 3], "wrap_rows": [3], "freeze_rows": 0,
          "col_widths": {"A": 430, "B": 150, "C": 170, "D": 170, "E": 170, "F": 150, "G": 110, "H": 120, "I": 110, "J": 120, "K": 100,
                         "L": 200, "M": 150}}
    cells["A1"] = ("Funding and cap table (the base: tables/base_rounds.csv). The rounds are the blue table on 'Company inputs'. "
                   "Founders start at 100%; the ESOP pool is set to its target at a top-up round (out of founders and earlier investors, "
                   "pro rata); other rounds dilute everyone. Valuations and the three lens multiples are OUR JUDGEMENT.")
    hdr = ["Round", "Month", "Amount (₹)", "Pre-money (₹)", "Post-money (₹)", "Dilution (new investors' share of post-money)",
           "ESOP top-up (1 = yes)", "Founders % after", "ESOP % after", "Investors % after", "Adds to 100%",
           "Lens value that month: the higher of lenses 1 and 2 (₹)", "Full model: founders % after (fixed)"]
    for j, h in enumerate(hdr):
        cells[f"{tc.col_name(j + 1)}3"] = h
    cells.update({"A4": "Before the seed", "H4": 1.0, "I4": 0.0, "J4": 0.0, "K4": "=SUM(H4:J4)"})
    for c in "HIJK":
        fm["number"][f"{c}4"] = "0.0%"
    r0 = 5
    for i, (row, rd) in enumerate(zip(ctab, rounds), 1):
        r, p = r0 + i - 1, r0 + i - 2
        cells.update({
            f"A{r}": f"=INDEX(rd_name,{i})", f"B{r}": f"=INDEX(rd_month,{i})", f"C{r}": f"=INDEX(rd_amount,{i})",
            f"D{r}": f"=INDEX(rd_pre,{i})", f"E{r}": f"=D{r}+C{r}", f"F{r}": f"=IFERROR(C{r}/E{r},0)", f"G{r}": f"=INDEX(rd_esop,{i})",
            f"H{r}": f"=IF(G{r}>=0.5,H{p}/(H{p}+J{p})*(1-F{r}-esop_target),H{p}*(1-F{r}))",
            f"I{r}": f"=IF(G{r}>=0.5,esop_target,I{p}*(1-F{r}))",
            f"J{r}": f"=IF(G{r}>=0.5,J{p}/(H{p}+J{p})*(1-F{r}-esop_target)+F{r},J{p}*(1-F{r})+F{r})",
            f"K{r}": f"=H{r}+I{r}+J{r}",
            f"L{r}": f"=IF(B{r}>=1,MAX(arr_mult*12*INDEX(co_revenue,B{r}),aum_mult*INDEX(co_aum,B{r})),\"\")"})
        if rd[0] in full:
            cells[f"M{r}"] = float(full[rd[0]]["Founders % after"])
        fm["number"].update({f"B{r}": "0", f"C{r}:E{r}": "#,##0", f"F{r}": "0.0%", f"G{r}": "0", f"H{r}:K{r}": "0.0%", f"L{r}": "#,##0",
                             f"M{r}": "0.0%"})
        m = int(rd[1])
        lv = max(Iv["arr_mult"] * o["arr"][m - 1], Iv["aum_mult"] * o["aum"][m - 1]) if m >= 1 else ""
        exp += [(f"E{r}", f"{rd[0]}: post-money", row["post"]), (f"F{r}", f"{rd[0]}: dilution", row["dilution"]),
                (f"H{r}", f"{rd[0]}: founders % after", row["founders"]), (f"I{r}", f"{rd[0]}: ESOP % after", row["esop"]),
                (f"J{r}", f"{rd[0]}: investors % after", row["investors"]),
                (f"K{r}", f"{rd[0]}: adds to 100%", row["founders"] + row["esop"] + row["investors"]),
                (f"L{r}", f"{rd[0]}: lens value that month", float(lv) if lv != "" else "")]
    r_last = r0 + len(rounds) - 1
    for nm, col in (("fc_post", "E"), ("fc_dil", "F"), ("fc_founders", "H"), ("fc_esop", "I"), ("fc_investors", "J")):
        names[nm] = f"{col}{r0}:{col}{r_last}"
    # the blue inputs for the check
    r = r_last + 2
    cells[f"A{r}"] = "Inputs for the unicorn check (blue)"
    cells.update({f"B{r}": "Value", f"C{r}": "Unit", f"D{r}": "Note", f"E{r}": "Name in formulas"})
    fm["bold_rows"].append(r)
    r += 1
    for k, (val, label, unit, f, note) in FI.items():
        cells.update({f"A{r}": rs(label), f"B{r}": val, f"C{r}": rs(unit), f"D{r}": rs(note), f"E{r}": k})
        names[k] = f"B{r}"
        fm["blue"].append(f"B{r}")
        if FMT[f]:
            fm["number"][f"B{r}"] = FMT[f]
        r += 1
    # the check
    r += 1
    cells.update({f"A{r}": "The unicorn check at the check month (formulas)", f"B{r}": "Toy (live)",
                  f"C{r}": "Full model (tables/base_lenses.csv, month 60, fixed)", f"D{r}": "Gap"})
    fm["bold_rows"].append(r)
    r += 1
    m_ = int(Iv["lens_month"]) - 1
    arr, fee_arr, aum, eq = (float(o[k][m_]) for k in ("arr", "fee_arr", "aum", "nb_equity"))
    l1, l2, l3 = (float(o[k][m_]) for k in ("rev_lens", "aum_lens", "book_lens"))
    U = Iv["unicorn"]
    F_ = lambda k: float(L60[k])
    uni = next(x for x in ctab if x["round"] == Iv["unicorn_round"])
    raised = float(sum(x[2] for x in rounds if x[1] <= Iv["lens_month"]))
    yn = lambda z: "yes" if z >= U else "no"
    CK = [  # name, label, formula, value, full-model reference, format, gap kind
        ("fc_arr", "ARR: 12 x the month's fees + net interest income + processing fees (₹)", "=12*INDEX(co_revenue,lens_month)", arr, F_("ARR"), "#,##0", "share"),
        ("fc_fee_arr", "Fee ARR: 12 x the month's fee revenue (₹)", "=12*INDEX(co_fee_rev,lens_month)", fee_arr, F_("Fee ARR"), "#,##0", "share"),
        ("fc_aum", "AUM: money in the fund at month end (₹)", "=INDEX(co_aum,lens_month)", aum, F_("AUM"), "#,##0", "share"),
        ("fc_nb_equity", "NBFC equity in the book (₹)", "=INDEX(co_nb_equity,lens_month)", eq, F_("NBFC equity"), "#,##0", "share"),
        ("fc_rev_lens", "Lens 1: arr_mult x ARR (₹; our judgement)", "=arr_mult*fc_arr", l1, F_("Lens 1 (20 x ARR)"), "#,##0", "share"),
        ("fc_aum_lens", "Lens 2: aum_mult x AUM (₹; our judgement)", "=aum_mult*fc_aum", l2, F_("Lens 2 (0.45 x AUM)"), "#,##0", "share"),
        ("fc_book_lens", "Lens 3 (cross-check): pb_mult x NBFC equity + arr_mult x fee ARR (₹; our judgement)", "=pb_mult*fc_nb_equity+arr_mult*fc_fee_arr",
         l3, F_("Lens 3 (3 x NBFC equity + 20 x fee ARR)"), "#,##0", "share"),
        (None, "Unicorn threshold (₹)", "=unicorn", U, ct.UNICORN, "#,##0", None),
        ("fc_rev_margin", "Lens 1 margin over the threshold", "=fc_rev_lens/unicorn-1", l1 / U - 1, F_("Lens 1 (20 x ARR) margin over $1B"), "0.0%", "points"),
        ("fc_aum_margin", "Lens 2 margin over the threshold", "=fc_aum_lens/unicorn-1", l2 / U - 1, F_("Lens 2 (0.45 x AUM) margin over $1B"), "0.0%", "points"),
        ("fc_book_margin", "Lens 3 margin over the threshold", "=fc_book_lens/unicorn-1", l3 / U - 1,
         F_("Lens 3 (3 x NBFC equity + 20 x fee ARR) margin over $1B"), "0.0%", "points"),
        (None, "ARR needed for the threshold on lens 1 (₹)", "=unicorn/arr_mult", U / Iv["arr_mult"], ct.UNICORN / 20, "#,##0", None),
        (None, "AUM needed for the threshold on lens 2 (₹)", "=unicorn/aum_mult", U / Iv["aum_mult"], ct.UNICORN / 0.45, "#,##0", None),
        (None, "Lens 1 clears the threshold?", '=IF(fc_rev_lens>=unicorn,"yes","no")', yn(l1), yn(F_("Lens 1 (20 x ARR)")), None, "text"),
        (None, "Lens 2 clears the threshold?", '=IF(fc_aum_lens>=unicorn,"yes","no")', yn(l2), yn(F_("Lens 2 (0.45 x AUM)")), None, "text"),
        (None, "Lens 3 (cross-check) clears the threshold?", '=IF(fc_book_lens>=unicorn,"yes","no")', yn(l3),
         yn(F_("Lens 3 (3 x NBFC equity + 20 x fee ARR)")), None, "text"),
        ("fc_both", "UNICORN ON PAPER at the check month (lenses 1 and 2 both clear)?", '=IF(AND(fc_rev_lens>=unicorn,fc_aum_lens>=unicorn),"yes","no")',
         yn(min(l1, l2)), L60["Lenses 1 and 2 both clear $1B"], None, "text"),
        ("fc_raised", "Equity raised by the check month (₹)", "=SUM(FILTER(rd_amount,rd_month<=lens_month))", raised,
         sum(float(x["Amount (Rs)"]) for x in full.values() if float(x["Month"]) <= 60), "#,##0", "share"),
        (None, "Equity raised, every round in the table (₹)", "=SUM(rd_amount)", float(sum(x[2] for x in rounds)),
         sum(float(x["Amount (Rs)"]) for x in full.values()), "#,##0", "share"),
        ("fc_founders_uni", "Founders' share after the unicorn round", "=INDEX(fc_founders,MATCH(unicorn_round,rd_name,0))", uni["founders"],
         float(full["E"]["Founders % after"]), "0.0%", "points"),
        (None, "Post-money of the unicorn round (₹)", "=INDEX(fc_post,MATCH(unicorn_round,rd_name,0))", uni["post"],
         float(full["E"]["Post-money (Rs)"]), "#,##0", "share"),
    ]
    for nm, label, f, val, ref, nf, gk in CK:
        cells.update({f"A{r}": label, f"B{r}": f, f"C{r}": ref})
        if gk == "share":
            cells[f"D{r}"] = f'=IFERROR((B{r}-C{r})/ABS(C{r}),"")'
            fm["number"][f"D{r}"] = "0.0%"
        elif gk == "points":
            cells[f"D{r}"] = f"=B{r}-C{r}"
            fm["number"][f"D{r}"] = '+0.0%;-0.0%'
        elif gk == "text":
            cells[f"D{r}"] = f'=IF(B{r}=C{r},"same","differs")'
        if nf:
            fm["number"][f"B{r}:C{r}"] = nf
        if nm:
            names[nm] = f"B{r}"
        exp.append((f"B{r}", label, val))
        r += 1
    return {"title": "Funding & cap table", "cells": cells, "named_ranges": names, "formats": fm}, exp


def summary_sheet(o, Iv, rounds, letters):
    rows = ct.summary_rows(o, Iv, rounds)
    cells = {"A1": "Measure (the base)", "B1": "Toy (live)", "C1": "Full model (tables/base_*.csv, fixed)", "D1": "Gap", "E1": "Note"}
    fm = {"number": {}, "bold_rows": [1], "freeze_rows": 1, "wrap_rows": [1], "col_widths": {"A": 470, "B": 170, "C": 200, "D": 90, "E": 380}}
    F = {}
    for y in range(1, YEARS + 1):
        F[f"Revenue, year {y} (fees + net interest income + processing fees)"] = f"=SUMIFS(co_revenue,co_year,{y})"
        F[f"EBITDA, year {y}"] = f"=SUMIFS(co_ebitda,co_year,{y})"
        F[f"PAT, year {y}"] = f"=SUMIFS(co_pat,co_year,{y})"
    F.update({
        "Fee revenue, year 5": "=SUMIFS(co_fee_rev,co_year,5)",
        "Net interest income, year 5": "=SUMIFS(co_nb_nii,co_year,5)",
        "Processing fees, year 5": "=SUMIFS(co_nb_proc,co_year,5)",
        "Credit cost (provisions), year 5": "=SUMIFS(co_nb_credit,co_year,5)",
        "Loan book, net of provisions, month 60": "=INDEX(co_nb_book,60)",
        "NBFC equity (capital held), month 60": "=INDEX(co_nb_equity,60)",
        "NBFC borrowings, month 60": "=INDEX(co_nb_borrow,60)",
        "ARR at month 60 (12 x the month's fees + NII + processing fees)": "=fc_arr",
        "AUM at month 60 (money in the fund, month end)": "=fc_aum",
        "Lens 1: arr_mult x ARR (20x agreed)": "=fc_rev_lens",
        "Lens 2: aum_mult x AUM (0.45x agreed)": "=fc_aum_lens",
        "Lens 3 (cross-check): pb_mult x NBFC equity + arr_mult x fee ARR (3x and 20x)": "=fc_book_lens",
        "Lens 1 margin over the threshold (Rs 10,000 crore)": "=fc_rev_margin",
        "Lens 2 margin over the threshold": "=fc_aum_margin",
        "Lens 3 margin over the threshold": "=fc_book_margin",
        "Unicorn on paper at month 60 (lenses 1 and 2 both clear)": "=fc_both",
        "Lowest month-end cash, months 1-96": "=MIN(co_cash)",
        "Month of the lowest cash": "=MATCH(MIN(co_cash),co_cash,0)",
        "Closing cash at month 60": "=INDEX(co_cash,60)",
        f"Closing cash at month {N}": f"=INDEX(co_cash,{N})",
        "EBITDA break-even month (stays positive from here)":
            f'=IF(INDEX(co_ebitda,{N})<=0,"not within {N} months",IFERROR(MAX(FILTER(co_month,co_ebitda<=0))+1,1))',
        "Equity raised by month 60 (rounds table)": "=fc_raised",
        "Founders' share after the unicorn round (E)": "=fc_founders_uni",
        "Savers still saving, month 60": "=INDEX(co_savers,60)",
        "Agents working, month 60": "=INDEX(co_agents,60)",
        "Cities open, month 60": "=INDEX(co_cities,60)",
        "Central team, month 60": "=INDEX(co_hc_central,60)",
        "Cumulative sign-ups to month 60": "=SUM(FILTER(co_signups,co_month<=60))",
        "National penetration at month 60 (cumulative sign-ups / the pool)": "=SUM(FILTER(co_signups,co_month<=60))/pool",
        "Money lent in year 5, personal loans incl. top-ups (on and off our book)": "=SUMIFS(co_lent,co_year,5)",
        "Money lent in year 5, home loans and LAP (other lenders)": "=SUMIFS(co_housing_lent,co_year,5)",
    })
    notes = {"EBITDA, year 5": "EBITDA is near 0 in year 5 (under 2% of revenue), so a small gap reads as a large %",
             "Revenue, year 2 (fees + net interest income + processing fees)": "the City plan's straight lines put more agents in year 2 than the full model's AUTO rollout (+7.5%); the full model run on the same City plan is +9.2%",
             "Lowest month-end cash, months 1-96": "before the A round lands at the end of month 9",
             "Unicorn on paper at month 60 (lenses 1 and 2 both clear)": "details and the multiples (blue): 'Funding & cap table'; lens 2 clears by under 1%"}
    hold_row = len(rows) + 3
    for i, (label, _val, ref, kind) in enumerate(rows, start=2):
        cells[f"A{i}"] = rs(label)
        if kind == "head":
            fm["bold_rows"].append(i)
            continue
        cells[f"B{i}"] = F[label]
        if ref is not None:
            cells[f"C{i}"] = ref
            if kind == "pct":
                cells[f"D{i}"] = f"=B{i}-C{i}"
                fm["number"][f"D{i}"] = '+0.0%;-0.0%'
            elif kind == "text":
                cells[f"D{i}"] = f'=IF(B{i}=C{i},"same","differs")'
            elif kind == "month":
                cells[f"D{i}"] = f'=IFERROR(B{i}-C{i},"")'
                fm["number"][f"D{i}"] = "+0;-0;0"
            else:
                cells[f"D{i}"] = f'=IFERROR((B{i}-C{i})/ABS(C{i}),"")'
                fm["number"][f"D{i}"] = "0.0%"
        if label in notes:
            cells[f"E{i}"] = notes[label]
        nf = {"inr": "#,##0", "num0": "#,##0", "month": "0", "pct": "0.0%", "text": None}[kind]
        if nf:
            fm["number"][f"B{i}:C{i}"] = nf
    cells[f"A{hold_row}"] = "Lean hold ends after month (0 = no hold; the base runs the central team as built)"
    cells[f"B{hold_row}"] = f"=IF(lean_hold>=0.5,IFERROR(INDEX(FILTER(co_month,co_ebitda_held>0),1),{N}),0)"
    fm["number"][f"B{hold_row}"] = "0"
    names = {"co_hold": f"B{hold_row}"}
    return {"title": "Company summary", "cells": cells, "named_ranges": names, "formats": fm}, hold_row


def main():
    v, Iv, plan, role_tab, rounds, o, _rows = ct.reconcile()
    I, _p, _r = ct.company_inputs()
    inp = inputs_sheet(I, plan, role_tab, rounds)
    mon, letters = monthly_sheet(role_tab)
    fund, fexp = funding_sheet(o, Iv, rounds)
    summ, hold_row = summary_sheet(o, Iv, rounds, letters)
    cplan = ct.city_plan()
    sheets = [inp, city_plan_sheet(cplan), city_month_sheet(len(cplan)), perbook_sheet(), mon, yearly_sheet(), fund, summ]
    for sh in sheets:
        sh["sheetId"] = SHEET_IDS[sh["title"]]
        for nm in sh["named_ranges"]:
            assert tc.valid_range_name(nm), nm
    keys = {k: letters[k] for k, _h, kind, _f, _nf in monthly_columns(role_tab) if kind != "multi"}
    spec = {"sheets": sheets, "_monthly_columns": keys, "_funding_expected": fexp, "_hold_cell": f"B{hold_row}",
            "_meta": {"formulas": {sh["title"]: sum(1 for val in sh["cells"].values() if isinstance(val, str) and val.startswith("="))
                                   for sh in sheets}, "monthly_last_col": tc.col_name(max(tc.col_num(c) for c in letters.values())),
                      "months": N}}
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB); formulas {spec['_meta']['formulas']}; last monthly column "
          f"{spec['_meta']['monthly_last_col']}")


if __name__ == "__main__":
    main()

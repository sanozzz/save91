"""Build Cohort_model.xlsx: the deterministic cohort model (model/cohort_engine.py) with live formulas, at the likely
value of every input, for the operator to open and change. Then recalculate it and reconcile it with Python.

Sheets
  Read me             what to edit, how the sheets flow, the approximations
  Inputs              every input: likely value (blue; yellow = operator decision or open choice), low / high alongside,
                      a cell comment with its source; derived values below (formulas). Every input is a defined name in_<key>.
  Retention curve     ages 1-60 from r3, r12 and churn_late
  Age profile         one sign-up's lines by age (formulas on Inputs and Retention curve)
  Cross-sell profile  the 17 products by age
  Sign-ups by age     month t's sign-ups of each age: the cohort convolution's weights (60 x 60)
  Monthly             months 1-60: every line = SUMPRODUCT(sign-ups by age for month t, the age profile); P&L, discount, NPV
  Cohort triangle     savers still saving by cohort (rows) x calendar month (columns)
  Summary             NPV 36 / 60, payback, value per sign-up and the rest as formulas; the Monte Carlo block as values

Recalculation: the xlsx skill's scripts/recalc.py needs LibreOffice (soffice), which is not installed on this machine, so the
workbook is recalculated with the `formulas` library (as model/verify.py does for savings_first_model.xlsx); the file is
saved with "recalculate on open" so Excel / Numbers / Sheets compute it when opened. Writes tables/cohort_xlsx_check.csv.
Run with the project .venv (openpyxl + formulas): .venv/bin/python model/build_cohort_xlsx.py
"""
import csv
import shutil
import sys
import warnings
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort_engine as E  # noqa: E402

ROOT = E.ROOT
OUT = ROOT / "Cohort_model.xlsx"
S_DIR = Path("/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad/cohort")
A = E.AGES
AP_CWIN_COL = "P"                         # Age profile column of the card-window helper (asserted when the sheet is built)
FIRST, LAST = 2, A + 1                    # data rows on every by-age / by-month sheet

F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF")
BLACK = Font(name=F, size=10, color="000000")
GREEN = Font(name=F, size=10, color="008000")
GREY = Font(name=F, size=9, color="808080", italic=True)
BOLD = Font(name=F, size=10, bold=True)
HEAD = Font(name=F, size=10, bold=True, color="FFFFFF")
TITLE = Font(name=F, size=14, bold=True)
HFILL = PatternFill("solid", fgColor="44546A")
YELLOW = PatternFill("solid", fgColor="FFFF00")
LIGHT = PatternFill("solid", fgColor="F2F2F2")
MCFILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Border(bottom=Side(style="thin", color="BFBFBF"))
RS = '#,##0;(#,##0);"-"'
RS2 = '#,##0.00;(#,##0.00);"-"'
PCT = '0.0%;(0.0%);"-"'
PCT2 = '0.00%;(0.00%);"-"'
NUM = '#,##0.0;(#,##0.0);"-"'
NUM4 = '0.0000;(0.0000);"-"'
WRAP = Alignment(wrap_text=True, vertical="top")

GROUPS = [  # (group label, keys)
    ("Sign-ups", ["signups_run", "ramp_months"]),
    ("Retention", ["r3", "r12", "churn_late"]),
    ("Saving", ["daily", "days", "amount_growth"]),
    ("The fund", ["term", "rollover", "withdraw_m", "trail", "fund_return"]),
    ("Early months (a saver's months 1-6)", ["early_takeup_mult", "early_approval_mult"]),
    ("Growth with the pool's history (addendum 4)", ["signup_growth", "takeup_growth", "approval_growth", "ticket_growth", "topup_share", "topup_size"]),
    ("UPI and cash visits", ["upi_12", "upi_ramp", "visit_every", "capacity", "extra_capacity_cost"]),
    ("Loans", ["apply", "eligible", "approved_first", "approved_repeat", "tenure", "ticket", "fee", "taken_back", "rate", "loss", "leaver_loan"]),
    ("Overdue loans (per account)", ["owed", "recovered", "early_cured", "fee_early", "fee_b3"]),
    ("Cards", ["card_share", "card_fee"]),
    *[(f"Cross-sell: {nm}", [k for k in E.PRODUCT_KEYS if k.startswith(p + "_")]) for p, _k, nm, _d in E.PRODUCTS],
    ("Costs and money terms", ["salary", "agent_balance_pay", "kyc_cost", "support_cost", "cash_cover", "ins_partner_share", "discount",
                               "marketplace_from"]),
]
STRUCTURE = [  # engine constants shown as inputs: key, name, value, unit, note
    ("helper_visits", "Visits a day the extra capacity cost buys", E.HELPER_VISITS, "visits a day", "COHORT_INPUTS 5: Rs 20,000 a month per 400 visits a day, pro-rata"),
    ("dpd_lag", "Months from a loan to its 31-90 day fees", E.DPD_LAG, "months", "addendum 2: about 9 months after disbursal"),
    ("rec_lag", "Months from a loan to its 90+ fees", E.REC_LAG, "months", "COHORT_INPUTS 6 / addendum 2: about 18 months after disbursal"),
    ("card_months", "Months over which cards are issued (from the first marketplace month)", E.CARD_MONTHS, "months",
     "Operator 16 Oct: issued once, spread evenly over months 1-6"),
    ("choti_months", "Month of the SIP at which the Choti incentive is paid", E.CHOTI_MONTHS, "months", "addendum 1: paid at month 24 of the SIP"),
    ("legacy_discount", "Discount rate for the legacy NPV rows only (the model is undiscounted)", E.LEGACY_DISCOUNT, "a year",
     "Round 5: 'we dont need to have a discount rate as of now. Let VC calculate it' - cumulative P&L; 20% kept for reference"),
    ("agent_pay_after", "Agent pay on balance after the growth phase, a year", E.AGENT_PAY_AFTER, "share of balance a year",
     "Round 7: 0.10% from company month 61 (outside the 60-month horizon)"),
    ("growth_months", "Growth phase (company months at the full agent pay on balance)", E.GROWTH_MONTHS, "months", "Round 7"),
    ("signup_cap", "Sign-ups a month, at most", E.SIGNUP_CAP, "sign-ups a month", "Addendum 4 cap"),
    ("takeup_cap", "Take-up (and card approval) factor, at most", E.TAKEUP_CAP, "x the agreed rate", "Addendum 4 cap: 2x the agreed rate"),
    ("approval_cap", "First-loan approval, at most", E.APPROVAL_CAP, "share", "Addendum 4 cap: 80% absolute (XL-41 Kissht repeat 74%)"),
    ("ticket_cap", "Repeat loan size, at most", E.TICKET_CAP, "Rs", "Addendum 4 cap: Rs 5 lakh (XL-12 Bachatt up to Rs 5 lakh)"),
    ("topup_lag", "Months after a loan before a top-up (12 EMIs paid)", E.TOPUP_LAG, "months", "Addendum 4: borrowers with 12+ EMIs paid"),
    ("early_months", "A saver's early months (the early take-up and approval factors apply)", E.EARLY_MONTHS, "months",
     "Operator 16 Oct: months 1-6 can have low take-up and approval rates; 1.0 from month 7"),
]
OPEN_OR_DECIDED = {"r12", "trail", "card_share", "tenure", "signups_run"}
SHARE_KEYS = {"r3", "r12", "churn_late", "amount_growth", "rollover", "withdraw_m", "trail", "upi_12", "apply", "eligible", "approved_first",
              "approved_repeat", "fee", "taken_back", "rate", "loss", "owed", "early_cured", "recovered", "card_share", "discount",
              "fund_return", "early_takeup_mult", "early_approval_mult", "signup_growth", "takeup_growth", "approval_growth",
              "ticket_growth", "topup_share", "topup_size"}


def fmt_for(k):
    if k in ("trail", "agent_balance_pay") or k.endswith("_comm") and k not in ("bills_comm", "nps_comm"):
        return PCT2
    if k in SHARE_KEYS or k.endswith(("_takeup", "_renew", "_approval")) or k == "ins_partner_share":
        return PCT
    return RS2 if k in ("bills_comm",) else '#,##0.##'


def unit_for(k):
    if k in SHARE_KEYS or k.endswith(("_takeup", "_renew", "_comm")) and k not in ("bills_comm", "nps_comm"):
        return "share" if not k.endswith(("_takeup", "apply")) else "share a year"
    return {"signups_run": "sign-ups a month", "ramp_months": "months", "daily": "Rs a day", "days": "days a month", "term": "months",
            "upi_ramp": "age (months)", "visit_every": "days", "capacity": "visits a day", "extra_capacity_cost": "Rs a month",
            "tenure": "months", "ticket": "Rs", "leaver_loan": "1 = yes", "fee_early": "Rs an account",
            "fee_b3": "Rs an account", "card_fee": "Rs a card", "salary": "Rs a month", "kyc_cost": "Rs a sign-up",
            "support_cost": "Rs an active saver a month", "marketplace_from": "age (month)", "bills_ticket": "bills a year",
            "bills_comm": "Rs a bill", "nps_comm": "share of the ticket", "cash_cover": "Rs an agent a month",
            "ins_partner_share": "share", "agent_balance_pay": "share of balance a year", "loan_home_approval": "share", "loan_lap_approval": "share"}.get(k, "Rs")


def hdr(ws, row, labels, widths=None):
    for j, t in enumerate(labels, 1):
        c = ws.cell(row, j, t)
        c.font, c.fill, c.alignment = HEAD, HFILL, Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[row].height = 54
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[L(j)].width = w


def name(wb, nm, sheet, cell):
    wb.defined_names[nm] = DefinedName(nm, attr_text=f"'{sheet}'!${''.join(ch for ch in cell if ch.isalpha())}${''.join(ch for ch in cell if ch.isdigit())}")


# ---------------------------------------------------------------- build
def build(dists, missing, notes):
    wb = Workbook()
    wb.calculation.fullCalcOnLoad = True
    readme = wb.active
    readme.title = "Read me"

    # ---------------- Inputs
    ws = wb.create_sheet("Inputs")
    hdr(ws, 1, ["Group", "Input", "Likely (edit me)", "Low", "High", "Shape", "Unit", "Key", "Where the number comes from"],
        [26, 52, 15, 11, 11, 11, 20, 24, 90])
    r = 2
    for g, keys in GROUPS:
        ws.cell(r, 1, g).font = BOLD
        ws.cell(r, 1).fill = LIGHT
        for j in range(2, 10):
            ws.cell(r, j).fill = LIGHT
        r += 1
        for k in keys:
            sh, lo, li, hi, src = dists[k]
            ws.cell(r, 1, "").font = BLACK
            ws.cell(r, 2, E.NAMES[k]).font = BLACK
            c = ws.cell(r, 3, li)
            c.font, c.number_format = BLUE, fmt_for(k)
            if k in OPEN_OR_DECIDED:
                c.fill = YELLOW
            for j, v in ((4, lo), (5, hi)):
                cc = ws.cell(r, j, v)
                cc.font, cc.number_format = GREY, fmt_for(k)
            ws.cell(r, 6, sh).font = GREY
            ws.cell(r, 7, unit_for(k)).font = GREY
            ws.cell(r, 8, k).font = GREY
            where = ("Fallback: COHORT_INPUTS / addenda (not yet in the distribution file)" if k in missing else
                     f"{E.DIST_FILE.name}" + (f" ({notes[k]})" if k in notes else ""))
            if k in notes and ("enforced" in notes[k] or "addendum used" in notes[k]):
                where = f"Operator decision / addendum, enforced in model/cohort_engine.py ({notes[k]})"
            ws.cell(r, 9, where).font = GREY
            ctext = f"Source: {src[:700]}\nShape {sh}, low {lo:g} / likely {li:g} / high {hi:g}.\n{where}"
            c.comment = Comment(ctext, "cohort model", width=420, height=160)
            name(wb, f"in_{k}", "Inputs", f"C{r}")
            r += 1
    ws.cell(r, 1, "Model structure (fixed)").font = BOLD
    for j in range(1, 10):
        ws.cell(r, j).fill = LIGHT
    r += 1
    for k, nm, v, u, note in STRUCTURE:
        ws.cell(r, 2, nm).font = BLACK
        c = ws.cell(r, 3, v)
        c.font, c.number_format = BLUE, '#,##0'
        c.comment = Comment(f"Source: {note}. A fixed part of the model, not sampled in the Monte Carlo.", "cohort model", width=360, height=80)
        ws.cell(r, 6, "fixed").font = GREY
        ws.cell(r, 7, u).font = GREY
        ws.cell(r, 8, k).font = GREY
        ws.cell(r, 9, note).font = GREY
        name(wb, f"in_{k}", "Inputs", f"C{r}")
        r += 1
    r += 1
    ws.cell(r, 1, "Derived (formulas: do not type here)").font = BOLD
    for j in range(1, 10):
        ws.cell(r, j).fill = LIGHT
    r += 1
    derived = [
        ("d_dm", "Monthly discount rate (0: cumulative P&L)", "=(1+in_discount)^(1/12)-1", PCT2),
        ("d_dm20", "Monthly discount rate for the legacy NPV rows", "=(1+in_legacy_discount)^(1/12)-1", PCT2),
        ("d_rm", "Saver's net return, monthly", "=(1+in_fund_return)^(1/12)-1", PCT2),
        ("d_h1", "Monthly drop-off, months 1-3", "=1-in_r3^(1/3)", PCT2),
        ("d_h2", "Monthly drop-off, months 4-12", "=1-(in_r12/in_r3)^(1/9)", PCT2),
        ("d_hz", "Monthly loan-application hazard", "=1-(1-in_apply)^(1/12)", PCT2),
        ("d_q1", "Monthly first-loan rate (hazard x eligible x approved)", "=d_hz*in_eligible*in_approved_first", PCT2),
        ("d_q2", "Monthly repeat-loan rate", "=d_hz*in_eligible*in_approved_repeat", PCT2),
        ("d_T", "Loan tenure in whole months", "=MAX(1,ROUND(in_tenure,0))", '0'),
        ("d_emi", "EMI on one loan (Rs a month)", "=in_ticket*(in_rate/12)/(1-(1+in_rate/12)^(-d_T))", RS2),
        ("d_paid", "Share of EMIs paid as scheduled", "=1-in_loss/(1-in_recovered)", PCT),
        ("d_orig", "Origination fee kept, per loan (Rs)", "=in_ticket*in_fee*(1-in_taken_back)", RS2),
        ("d_p90", "Implied share of loans that ever go 90+ days bad (CRIF NG-015 10.2%, MAC-03 3.6%)", "=in_loss/(in_owed*(1-in_recovered))", PCT),
        ("d_check", "Early brought back + p90 (page check: at most 50%)", "=in_early_cured+d_p90", PCT),
        ("d_check_flag", "Page check", '=IF(d_check>0.5,"FLAG: above 50%","ok")', None),
        ("d_dpd", "31-90 day fees per loan made (Rs)", "=in_early_cured*in_fee_early", RS2),
        ("d_rec", "90+ recovery fees per loan made (Rs)", "=d_p90*in_recovered*in_fee_b3", RS2),
        ("d_cured", "Accounts brought back at 31-90 days, per loan", "=in_early_cured", NUM4),
        ("d_card_rem", "Card share held back by the early factors, issued in the next 6 months",
         f"=MAX(0,1-SUM('Age profile'!${AP_CWIN_COL}${FIRST}:${AP_CWIN_COL}${LAST})/in_card_months)", PCT),
        ("d_u", "Monthly top-up hazard (borrowers with 12+ EMIs paid)", "=1-(1-in_topup_share)^(1/12)", PCT2),
        ("d_udrop", "Top-up window helper: (1 - hazard)^(tenure - 13)", "=(1-d_u)^MAX(0,d_T-in_topup_lag)", NUM4),
        ("d_rep_ticket", "Repeat loan size after his loan is repaid (Rs)", "=MIN(in_ticket_cap,in_ticket*(1+in_ticket_growth)^(d_T/12))", RS),
        ("d_topup_amt", "Top-up size (Rs; a year repaid)", "=in_topup_size*in_ticket*(1+in_ticket_growth)", RS),
        ("d_topup_ratio", "Top-up size as a share of the base ticket (collections pro rata)", "=d_topup_amt/in_ticket", PCT),
        ("d_recd", "Accounts recovered after 90 days, per loan", "=d_p90*in_recovered", NUM4),
    ]
    for p, kind, nm, _d in E.PRODUCTS:
        derived.append((f"d_hz_{p}", f"{nm}: monthly take-up hazard", f"=1-(1-in_{p}_takeup)^(1/12)", PCT2))
        if kind in ("flow", "flow_year", "trail"):
            derived.append((f"d_rho_{p}", f"{nm}: monthly persistence", f"=in_{p}_renew^(1/12)", NUM4))
    for nm_, lab, f, fm in derived:
        ws.cell(r, 2, lab).font = BLACK
        c = ws.cell(r, 3, f)
        c.font = BLACK
        if fm:
            c.number_format = fm
        ws.cell(r, 8, nm_).font = GREY
        name(wb, nm_, "Inputs", f"C{r}")
        r += 1
    ws.freeze_panes = "C2"

    # ---------------- Retention curve
    rc = wb.create_sheet("Retention curve")
    hdr(rc, 1, ["Age (month since sign-up)", "Monthly drop-off after this month", "Still saving (share of sign-ups)", "Stopped this month"], [14, 18, 18, 16])
    for a in range(1, A + 1):
        i = a + 1
        rc.cell(i, 1, a).font = BLACK
        rc.cell(i, 2, f"=IF(A{i}<=3,d_h1,IF(A{i}<=12,d_h2,in_churn_late))").number_format = PCT2
        rc.cell(i, 3, 1 if a == 1 else f"=C{i - 1}*(1-B{i - 1})").number_format = PCT
        rc.cell(i, 4, 0 if a == 1 else f"=C{i - 1}-C{i}").number_format = PCT2
        if a == 1:
            rc.cell(i, 3).font = BLACK
    rc.cell(LAST + 2, 1, "Months 1-3 drop at d_h1 (so month 4 = r3), months 4-12 at d_h2 (so month 13 = r12), then churn_late. "
                         "'Still saving at month m' = survived m monthly drop-offs (the v2 convention).").font = GREY
    rc.freeze_panes = "B2"

    # ---------------- Age profile (cohort-independent lines: retention, saving, the fund, UPI, KYC)
    ap = wb.create_sheet("Age profile")
    cols = [  # (id, header, formula template, number format); {r} row, {p} previous row, {c[X]} = column letter of id X
        ("age", "Age (month since sign-up)", "{age}", '0'),
        ("s", "Still saving", "='Retention curve'!C{r}", PCT),
        ("stop", "Stopped this month", "='Retention curve'!D{r}", PCT2),
        ("dps", "Deposit per active saver (Rs)", "=in_daily*in_days*(1+in_amount_growth)^INT(({c[age]}{r}-1)/in_term)", RS),
        ("dep", "Deposits (Rs)", "={c[s]}{r}*{c[dps]}{r}", RS),
        ("bs", "Balance at the month's start, per active saver (Rs)",
         "=IF({c[age]}{r}=1,0,{c[be]}{p}*IF(MOD({c[age]}{r}-1,in_term)=0,in_rollover,1))", RS),
        ("be", "Balance at the month's end, per active saver, with his return (Rs)",
         "={c[bs]}{r}*(1-in_withdraw_m)+{c[dps]}{r}+({c[bs]}{r}*(1-in_withdraw_m)+0.5*{c[dps]}{r})*d_rm", RS),
        ("bal", "Average balance in the fund (Rs)", "={c[s]}{r}*({c[bs]}{r}*(1-in_withdraw_m)+0.5*{c[dps]}{r})", RS),
        ("wd", "Withdrawn this month (Rs)",
         "={c[s]}{r}*in_withdraw_m*{c[bs]}{r}+IF({c[age]}{r}=1,0,{c[stop]}{r}*{c[be]}{p}+IF(MOD({c[age]}{r}-1,in_term)=0,{c[s]}{r}*(1-in_rollover)*{c[be]}{p},0))", RS),
        ("upi", "Share on UPI", "=in_upi_12*MIN(1,({c[age]}{r}-1)/(in_upi_ramp-1))", PCT),
        ("cash", "Cash savers", "={c[s]}{r}*(1-{c[upi]}{r})", PCT),
        ("vis", "Cash visits a day", "={c[cash]}{r}/in_visit_every", NUM4),
        ("prov", "Savers offered the marketplace (still saving)", "=IF({c[age]}{r}>=in_marketplace_from,{c[s]}{r},0)", PCT),
        ("emt", "Early take-up factor", "=IF({c[age]}{r}<=in_early_months,in_early_takeup_mult,1)", '0.00'),
        ("ema", "Early approval factor", "=IF({c[age]}{r}<=in_early_months,in_early_approval_mult,1)", '0.00'),
        ("cwin", "Card window: early factors in the first card months (helper)",
         "=IF(AND({c[age]}{r}>=in_marketplace_from,{c[age]}{r}<in_marketplace_from+in_card_months),{c[emt]}{r}*{c[ema]}{r},0)", '0.00'),
        ("r_fund", "Fund commission (Rs)", "={c[bal]}{r}*in_trail/12", RS2),
        ("kyc", "KYC cost (Rs)", "=IF({c[age]}{r}=1,in_kyc_cost,0)", RS2),
        ("sup", "Support cost (Rs)", "={c[s]}{r}*in_support_cost", RS2),
        ("df", "Discount factor at his age", "=1/(1+d_dm)^({c[age]}{r}-1)", NUM4),
        ("valb", "Fund commission less KYC and support, discounted to his sign-up month (Rs)",
         "=({c[r_fund]}{r}-{c[kyc]}{r}-{c[sup]}{r})*{c[df]}{r}", RS2),
    ]
    C = {cid: L(j) for j, (cid, *_rest) in enumerate(cols, 1)}
    assert C["cwin"] == AP_CWIN_COL, C["cwin"]
    hdr(ap, 1, [h for _i, h, *_r in cols], [9] + [13] * (len(cols) - 1))
    for a in range(1, A + 1):
        i = a + 1
        for j, (cid, _h, f, fm) in enumerate(cols, 1):
            v = a if cid == "age" else f.format(c=C, r=i, p=i - 1)
            c = ap.cell(i, j, v)
            c.font, c.number_format = (GREEN if cid in ("s", "stop") else BLACK), fm
    ap.cell(LAST + 2, 1, "Per sign-up. The marketplace lines (loans, top-ups, cards, the 17 products, collections) depend on the calendar "
                         "year as well as his age, because take-up and approvals grow with the pool's history: they are on 'Cohort x age'.").font = GREY
    ap.freeze_panes = "B2"

    # ---------------- Cohort x age: the marketplace lines, one row per (cohort, age), in absolute numbers (x the cohort's sign-ups)
    cx = wb.create_sheet("Cohort x age")
    mf = "in_marketplace_from"
    APR = lambda cid: f"'Age profile'!${C[cid]}${FIRST}:${C[cid]}${LAST}"
    G1 = {}   # age-1 overrides: lags look only at earlier ages of the same cohort, none exist at age 1
    kc = [  # (id, header, template, fmt)
        ("co", "Sign-up month (cohort)", "{co}", '0'), ("ag", "Age", "{ag}", '0'),
        ("cm", "Calendar month", "={k[co]}{r}+{k[ag]}{r}-1", '0'), ("yr", "Calendar year", "=INT(({k[cm]}{r}-1)/12)+1", '0'),
        ("su", "Cohort's sign-ups", "=INDEX(Monthly!$B${first}:$B${last},{k[co]}{r})", NUM),
        ("s", "Still saving", "={k[su]}{r}*INDEX(" + APR("s") + ",{k[ag]}{r})", NUM),
        ("tf", "Take-up factor (early months x pool history, cap)",
         "=MIN(in_takeup_cap,INDEX(" + APR("emt") + ",{k[ag]}{r})*(1+in_takeup_growth)^({k[yr]}{r}-1))", '0.000'),
        ("af", "First-loan approval (cap 80%)",
         "=MIN(in_approval_cap,in_approved_first*INDEX(" + APR("ema") + ",{k[ag]}{r})*(1+in_approval_growth)^({k[yr]}{r}-1))", PCT),
        ("cf", "Card factor (take-up x approval)",
         "={k[tf]}{r}*MIN(in_takeup_cap,INDEX(" + APR("ema") + ",{k[ag]}{r})*(1+in_approval_growth)^({k[yr]}{r}-1))", '0.000'),
        ("n0", "No loan yet", "=({k[n0]}{p}-{k[f1]}{p})*{k[s]}{r}/{k[s]}{p}", NUM4),
        ("e", "Repaid a loan, can apply for a repeat",
         "=({k[e]}{p}-{k[rp]}{p})*{k[s]}{r}/{k[s]}{p}+SUMIFS({k[lps]}{fr}:{k[lps]}{p},{k[ag]}{fr}:{k[ag]}{p},{k[ag]}{r}-1-d_T)*{k[s]}{r}", NUM4),
        ("f1", "First loans", "=IF({k[ag]}{r}>=" + mf + ",{k[n0]}{r}*d_hz*{k[tf]}{r}*in_eligible*{k[af]}{r},0)", NUM4),
        ("rp", "Repeat loans", "=IF({k[ag]}{r}>=" + mf + ",{k[e]}{r}*d_hz*{k[tf]}{r}*in_eligible*in_approved_repeat,0)", NUM4),
        ("ln", "Loans made", "={k[f1]}{r}+{k[rp]}{r}", NUM4),
        ("lps", "Loans per active saver (helper)", "={k[ln]}{r}/{k[s]}{r}", '0.000000'),
        ("wl", "Savers with a loan running", "={k[s]}{r}-{k[n0]}{r}-{k[e]}{r}", NUM4),
        ("apps", "Loan applications", "=IF({k[ag]}{r}>=" + mf + ",({k[n0]}{r}+{k[e]}{r})*d_hz*{k[tf]}{r},0)", NUM4),
        ("due", "Loans with an EMI due", "=SUMIFS({k[ln]}{fr}:{k[ln]}{lr},{k[ag]}{fr}:{k[ag]}{lr},\">=\"&({k[ag]}{r}-d_T),{k[ag]}{fr}:{k[ag]}{lr},\"<=\"&({k[ag]}{r}-1))", NUM4),
        ("tw", "Top-up window (helper)",
         "=(1-d_u)*{k[tw]}{p}+IF(d_T>in_topup_lag,SUMIFS({k[lps]}{fr}:{k[lps]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-in_topup_lag)"
         "-d_udrop*SUMIFS({k[lps]}{fr}:{k[lps]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-d_T),0)", '0.000000'),
        ("tu", "Top-ups", "={k[s]}{r}*d_u*{k[tw]}{r}", NUM4),
        ("lentn", "Money lent, first and repeat loans (Rs)", "={k[f1]}{r}*in_ticket+{k[rp]}{r}*d_rep_ticket", RS),
        ("lent", "Money lent, with top-ups (Rs)", "={k[lentn]}{r}+{k[tu]}{r}*d_topup_amt", RS),
        ("leq", "Loans for collections (top-ups pro rata)", "={k[ln]}{r}+{k[tu]}{r}*d_topup_ratio", NUM4),
        ("cur", "Overdue accounts brought back, 31-90 days",
         "=SUMIFS({k[leq]}{fr}:{k[leq]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-in_dpd_lag)*d_cured", NUM4),
        ("rcd", "Overdue accounts recovered, 90+",
         "=SUMIFS({k[leq]}{fr}:{k[leq]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-in_rec_lag)*d_recd", NUM4),
        ("cards", "Cards issued (the share held back by the early factors follows in the next 6 months)",
         "=IF(AND({k[ag]}{r}>=" + mf + ",{k[ag]}{r}<" + mf + "+in_card_months),in_card_share/in_card_months*{k[s]}{r}*{k[cf]}{r},"
         "IF(AND({k[ag]}{r}>=" + mf + "+in_card_months,{k[ag]}{r}<" + mf + "+2*in_card_months),in_card_share*d_card_rem/in_card_months*{k[s]}{r}"
         "*MIN(in_takeup_cap,(1+in_takeup_growth)^({k[yr]}{r}-1))*MIN(in_takeup_cap,(1+in_approval_growth)^({k[yr]}{r}-1)),0))", NUM4),
        ("r_orig", "Origination fees net of taken back (Rs)", "={k[lent]}{r}*in_fee*(1-in_taken_back)", RS2),
        ("r_dpd", "31-90 day collection fees (Rs)",
         "=SUMIFS({k[leq]}{fr}:{k[leq]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-in_dpd_lag)*d_dpd", RS2),
        ("r_rec", "90+ recovery fees (Rs)", "=SUMIFS({k[leq]}{fr}:{k[leq]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-in_rec_lag)*d_rec", RS2),
        ("r_cards", "Card fees (Rs)", "={k[cards]}{r}*in_card_fee", RS2),
    ]
    G1.update({"n0": "={k[su]}{r}", "e": 0, "tw": 0})
    H = lambda p_, rr="{r}": "IF({k[ag]}" + rr + ">=" + mf + f",d_hz_{p_}*{{k[tf]}}" + rr + ",0)"
    rev_ids = {}
    for p_, kind, nm, d in E.PRODUCTS:
        kc.append((f"{p_}_n", f"{nm}: never held it (share of active savers)", "={k[" + p_ + "_n]}{p}*(1-" + H(p_, "{p}") + ")", NUM4))
        G1[f"{p_}_n"] = 1
        T_, C_ = f"in_{p_}_ticket", f"in_{p_}_comm"
        C_ = C_ + ("*in_ins_partner_share" if p_ in E.INSURANCE else "")      # round 6: insurance through a broker partner
        if kind == "secured":                     # applications x approval (cap 80%); the approved leave the pool
            kc[-1] = (f"{p_}_n", f"{nm}: never had one (share of active savers)",
                      "={k[" + p_ + "_n]}{p}*(1-" + H(p_, "{p}") + "*{k[" + p_ + "_a]}{p})", NUM4)
            kc.append((f"{p_}_a", f"{nm}: approval (cap 80%)",
                       "=MIN(in_approval_cap,in_" + p_ + "_approval*INDEX(" + APR("ema") + ",{k[ag]}{r})*(1+in_approval_growth)^({k[yr]}{r}-1))", PCT))
            kc.append((f"{p_}_rev", f"{nm} (Rs)", "={k[s]}{r}*{k[" + p_ + "_n]}{r}*" + H(p_) + "*{k[" + p_ + "_a]}{r}*" + f"{T_}*{C_}", RS2))
        elif kind == "once":
            kc.append((f"{p_}_rev", f"{nm} (Rs)", "={k[s]}{r}*{k[" + p_ + "_n]}{r}*" + H(p_) + f"*{T_}*{C_}", RS2))
        elif kind in ("ins", "bonus"):
            kc.append((f"{p_}_g", f"{nm}: take-ups per active saver", "={k[" + p_ + "_n]}{r}*" + H(p_), '0.000000'))
            if kind == "ins":
                rcm = (f"in_{p_}_renew_comm*in_ins_partner_share" if f"{p_}_renew_comm" in E.FALLBACK else C_)
                lags = "+".join(f"in_{p_}_renew^{k_}*SUMIFS({{k[{p_}_g]}}{{fr}}:{{k[{p_}_g]}}{{lr}},{{k[ag]}}{{fr}}:{{k[ag]}}{{lr}},{{k[ag]}}{{r}}-{12 * k_})"
                                for k_ in range(1, A // 12))
                kc.append((f"{p_}_rev", f"{nm} (Rs)", "={k[s]}{r}*{k[" + p_ + "_g]}{r}*" + f"{T_}*{C_}" + "+{k[s]}{r}*" + f"{T_}*{rcm}*({lags})", RS2))
            else:
                kc.append((f"{p_}_rev", f"{nm} (Rs)", "={k[s]}{r}*SUMIFS({k[" + p_ + "_g]}{fr}:{k[" + p_ + "_g]}{lr},{k[ag]}{fr}:{k[ag]}{lr},{k[ag]}{r}-in_choti_months)*"
                           + f"in_{p_}_renew*{T_}", RS2))
        else:
            kc.append((f"{p_}_R", f"{nm}: holders per active saver", "={k[" + p_ + "_R]}{p}*d_rho_" + p_ + "+{k[" + p_ + "_n]}{r}*" + H(p_), NUM4))
            G1[f"{p_}_R"] = "={k[" + p_ + "_n]}{r}*" + H(p_)
            if kind == "trail":
                kc.append((f"{p_}_Q", f"{nm}: SIP months held per active saver (helper)", "=d_rho_" + p_ + "*({k[" + p_ + "_Q]}{p}+{k[" + p_ + "_R]}{p})", NUM4))
                G1[f"{p_}_Q"] = 0
                kc.append((f"{p_}_rev", f"{nm} (Rs)", "={k[s]}{r}*" + T_ + "*({k[" + p_ + "_Q]}{r}+0.5*{k[" + p_ + "_R]}{r})*" + C_ + "/12", RS2))
            else:
                per = "/12" if kind == "flow_year" else ""
                kc.append((f"{p_}_rev", f"{nm} (Rs)", "={k[s]}{r}*{k[" + p_ + "_R]}{r}*" + f"{T_}*{C_}{per}", RS2))
        rev_ids[p_] = f"{p_}_rev"
    kc.append(("mk", "Marketplace income (Rs)", "=" + "+".join("{k[" + c_ + "]}{r}" for c_ in ["r_orig", "r_dpd", "r_rec", "r_cards"] + list(rev_ids.values())), RS2))
    K = {cid: L(j) for j, (cid, *_rest) in enumerate(kc, 1)}
    hdr(cx, 1, [h for _i, h, *_r in kc], [8, 6, 8, 8] + [12] * (len(kc) - 4))
    r = FIRST
    for co in range(1, E.MONTHS + 1):
        fr, lr = r, r + E.MONTHS - co
        for ag in range(1, E.MONTHS - co + 2):
            for j, (cid, _h, f, fm) in enumerate(kc, 1):
                tpl = G1.get(cid, f) if ag == 1 else f
                if cid == "co":
                    v = co
                elif cid == "ag":
                    v = ag
                elif isinstance(tpl, (int, float)):
                    v = tpl
                else:
                    v = tpl.format(k=K, r=r, p=r - 1, fr=fr, lr=lr, first=FIRST, last=LAST)
                c = cx.cell(r, j, v)
                c.font = GREEN if cid in ("su", "s") else BLACK
                c.number_format = fm
            r += 1
    CX_LAST = r - 1
    cx.freeze_panes = "C2"

    # ---------------- Sign-ups by age
    sa = wb.create_sheet("Sign-ups by age")
    sa.cell(1, 1, "Age \\ month").font = HEAD
    sa.cell(1, 1).fill = HFILL
    for t in range(1, E.MONTHS + 1):
        c = sa.cell(1, t + 1, t)
        c.font, c.fill = HEAD, HFILL
        sa.column_dimensions[L(t + 1)].width = 7
    for a in range(1, A + 1):
        i = a + 1
        sa.cell(i, 1, a).font = BOLD
        for t in range(1, E.MONTHS + 1):
            col = L(t + 1)
            c = sa.cell(i, t + 1, f"=IF($A{i}<={col}$1,INDEX(Monthly!$B${FIRST}:$B${LAST},{col}$1-$A{i}+1),0)")
            c.font, c.number_format = BLACK, '0.0;-0.0;"-"'
    sa.cell(LAST + 2, 1, "Cell (age a, month t) = the sign-ups of the cohort that is age a in month t (sign-ups of month t - a + 1). "
                         "Monthly totals of the age-profile lines = SUMPRODUCT of a month's column here with an age-profile column.").font = GREY
    sa.freeze_panes = "B2"

    # ---------------- Monthly
    mo = wb.create_sheet("Monthly")
    mlines = [  # (id, header, kind, ref, fmt): 'ap' = Age profile column, 'cx' = Cohort x age column (SUMIFS by calendar month), 'f' = formula
        ("m", "Month", "f", "{t}", '0'),
        ("su", "Sign-ups", "f", "=MIN(in_signup_cap,in_signups_run*IF(in_ramp_months>0,MIN(1,0.5+0.5*({M[m]}{r}-1)/in_ramp_months),1)"
                                "*(1+in_signup_growth)^INT(({M[m]}{r}-1)/12))", NUM),
        ("s", "Savers still saving", "ap", "s", NUM), ("stop", "Stopped this month", "ap", "stop", NUM),
        ("prov", "Savers offered the marketplace", "ap", "prov", NUM), ("cash", "Cash savers", "ap", "cash", NUM),
        ("vis", "Cash visits a day", "ap", "vis", NUM),
        ("upi", "Share on UPI", "f", "=IF({M[s]}{r}>0,1-{M[cash]}{r}/{M[s]}{r},0)", PCT),
        ("upin", "UPI share needed to stay within one agent's visits", "f", "=IF({M[s]}{r}>0,MAX(0,1-in_capacity*in_visit_every/{M[s]}{r}),0)", PCT),
        ("dep", "Deposits (Rs)", "ap", "dep", RS), ("bal", "Average balance in the fund (Rs)", "ap", "bal", RS),
        ("apps", "Loan applications", "cx", "apps", NUM), ("f1", "First loans", "cx", "f1", '0.00'), ("rp", "Repeat loans", "cx", "rp", '0.00'),
        ("ln", "Loans made", "cx", "ln", '0.00'), ("tu", "Top-ups", "cx", "tu", '0.00'),
        ("lentn", "Money lent, first and repeat loans (Rs)", "cx", "lentn", RS), ("lent", "Money lent, with top-ups (Rs)", "cx", "lent", RS),
        ("wl", "Savers with a loan running", "cx", "wl", NUM),
        ("due", "Loans with an EMI due", "cx", "due", NUM), ("cur", "Overdue accounts brought back, 31-90 days", "cx", "cur", '0.00'),
        ("rcd", "Overdue accounts recovered, 90+", "cx", "rcd", '0.00'), ("cards", "Cards issued", "cx", "cards", '0.00'),
        ("r_fund", "Fund commission (Rs)", "ap", "r_fund", RS), ("r_orig", "Origination fees net of taken back (Rs)", "cx", "r_orig", RS),
        ("r_dpd", "31-90 day collection fees (Rs)", "cx", "r_dpd", RS), ("r_rec", "90+ recovery fees (Rs)", "cx", "r_rec", RS),
        ("r_cards", "Card fees (Rs)", "cx", "r_cards", RS),
        *[(f"x_{p_}", f"{nm} (Rs)", "cx", rev_ids[p_], RS) for p_, _k, nm, _d in E.PRODUCTS],
        ("inc", "Income (Rs)", "f", "=SUM({M[r_fund]}{r}:{M[x_loan_vehicle]}{r})", RS),
        ("c_sal", "Salary (Rs)", "f", "=in_salary", RS),
        ("c_cap", "Extra cash-collection capacity (Rs)", "f", "=MAX(0,{M[vis]}{r}-in_capacity)*in_extra_capacity_cost/in_helper_visits", RS),
        ("c_kyc", "KYC (Rs)", "ap", "kyc", RS), ("c_sup", "Running cost: support, app, cash deposits (Rs)", "ap", "sup", RS),
        ("c_cov", "Cash cover: fidelity and cash-in-transit insurance (Rs)", "f", "=in_cash_cover", RS),
        ("c_inc", "Agent pay on balance (Rs)", "f", "=IF({M[m]}{r}<=in_growth_months,in_agent_balance_pay,in_agent_pay_after)/12*{M[bal]}{r}", RS),
        ("cost", "Costs (Rs)", "f", "={M[c_sal]}{r}+{M[c_cap]}{r}+{M[c_kyc]}{r}+{M[c_sup]}{r}+{M[c_cov]}{r}+{M[c_inc]}{r}", RS),
        ("net", "Net cash (Rs)", "f", "={M[inc]}{r}-{M[cost]}{r}", RS),
        ("df", "Discount factor", "f", "=1/(1+d_dm)^{M[m]}{r}", NUM4),
        ("pv", "Net, discounted (Rs)", "f", "={M[net]}{r}*{M[df]}{r}", RS),
        ("cnpv", "Cumulative NPV (Rs)", "f", "=IF({M[m]}{r}=1,{M[pv]}{r},{M[cnpv]}{p}+{M[pv]}{r})", RS),
        ("ccash", "Cumulative P&L (Rs)", "f", "=IF({M[m]}{r}=1,{M[net]}{r},{M[ccash]}{p}+{M[net]}{r})", RS),
        ("stay", "Cumulative P&L positive from here to month 60? (1 = yes)", "f", "=IF(AND({M[ccash]}{r}>=0,{M[stay]}{n}=1),1,0)", '0'),
        ("pb", "Paid back? (month if positive from here on, else 999)", "f", "=IF({M[stay]}{r}=1,{M[m]}{r},999)", '0'),
        ("df20", "Legacy discount factor (20% a year)", "f", "=1/(1+d_dm20)^{M[m]}{r}", NUM4),
    ]
    M = {cid: L(j) for j, (cid, *_rest) in enumerate(mlines, 1)}
    hdr(mo, 1, [h for _i, h, *_r in mlines], [7] + [12] * (len(mlines) - 1))
    for t in range(1, E.MONTHS + 1):
        i = t + 1
        sc = L(t + 1)
        for j, (cid, _h, kind, ref, fm) in enumerate(mlines, 1):
            if kind == "ap":
                v = f"=SUMPRODUCT('Sign-ups by age'!{sc}${FIRST}:{sc}${LAST},'Age profile'!{C[ref]}${FIRST}:{C[ref]}${LAST})"
            elif kind == "cx":
                v = (f"=SUMIFS('Cohort x age'!${K[ref]}${FIRST}:${K[ref]}${CX_LAST},'Cohort x age'!${K['cm']}${FIRST}:${K['cm']}${CX_LAST},"
                     f"{M['m']}{i})")
            elif cid == "m":
                v = t
            elif cid == "stay" and t == E.MONTHS:
                v = f"=IF({M['ccash']}{i}>=0,1,0)"
            else:
                v = ref.format(M=M, r=i, p=i - 1, n=i + 1, t=t)
            c = mo.cell(i, j, v)
            c.font, c.number_format = (GREEN if kind in ("ap", "cx") else BLACK), fm
    tr = LAST + 1
    mo.cell(tr, 1, "Total").font = BOLD
    for j, (cid, *_r) in enumerate(mlines, 1):
        if cid not in ("m", "upi", "upin", "df", "df20", "cnpv", "ccash", "stay", "pb", "s", "prov", "cash", "vis", "wl", "due", "bal"):
            c = mo.cell(tr, j, f"=SUM({L(j)}{FIRST}:{L(j)}{LAST})")
            c.font, c.number_format = BOLD, mlines[j - 1][4]
    mo.freeze_panes = "B2"

    # ---------------- Cohort triangle
    ct = wb.create_sheet("Cohort triangle")
    ct.cell(1, 1, "Sign-up month \\ calendar month").font = HEAD
    ct.cell(1, 1).fill = HFILL
    ct.column_dimensions["A"].width = 16
    for t in range(1, E.MONTHS + 1):
        c = ct.cell(1, t + 1, t)
        c.font, c.fill = HEAD, HFILL
        ct.column_dimensions[L(t + 1)].width = 6
    for co in range(1, E.MONTHS + 1):
        i = co + 1
        ct.cell(i, 1, co).font = BOLD
        for t in range(1, E.MONTHS + 1):
            col = L(t + 1)
            c = ct.cell(i, t + 1, f"=IF({col}$1>=$A{i},INDEX(Monthly!${M['su']}${FIRST}:${M['su']}${LAST},$A{i})*INDEX('Age profile'!${C['s']}${FIRST}:${C['s']}${LAST},{col}$1-$A{i}+1),\"\")")
            c.font, c.number_format = BLACK, '0;-0;"-"'
    ct.cell(LAST + 1, 1, "Total savers").font = BOLD
    ct.cell(LAST + 2, 1, "Check: Monthly").font = GREY
    for t in range(1, E.MONTHS + 1):
        col = L(t + 1)
        ct.cell(LAST + 1, t + 1, f"=SUM({col}{FIRST}:{col}{LAST})").number_format = '#,##0'
        ct.cell(LAST + 2, t + 1, f"=Monthly!{M['s']}{t + 1}-{col}{LAST + 1}").number_format = '0.000;-0.000;"-"'
    ct.conditional_formatting.add(f"B{FIRST}:{L(E.MONTHS + 1)}{LAST}",
                                  ColorScaleRule(start_type="min", start_color="FFFFFF", end_type="max", end_color="5B9BD5"))
    ct.cell(LAST + 4, 1, "Each row is one month's sign-ups; each cell is how many of them are still saving in that calendar month. "
                         "Row 1 = the agent's first month. Read down a column for that month's book, across a row for one cohort's decay.").font = GREY
    ct.freeze_panes = "B2"

    # ---------------- Summary
    sm = wb.create_sheet("Summary", 1)
    sm.column_dimensions["A"].width = 66
    for j in range(2, 12):
        sm.column_dimensions[L(j)].width = 14
    sm.cell(1, 1, "One street agent, 60 months: cumulative P&L at the likely values (undiscounted)").font = TITLE
    sm.cell(2, 1, f"Every number in this first block is a formula on the other sheets; change a blue cell on Inputs and it moves. "
                  f"Built {date.today().isoformat()} by model/build_cohort_xlsx.py.").font = GREY
    hdr_row = 4
    for j, t in enumerate(["Measure", "Value", "Unit"], 1):
        c = sm.cell(hdr_row, j, t)
        c.font, c.fill = HEAD, HFILL
    mr = lambda cid: f"Monthly!{M[cid]}{FIRST}:{M[cid]}{LAST}"
    proven_years = f"(SUM({mr('prov')})/12)"
    S = [  # id, label, formula, fmt, unit
        ("npv36", "Cumulative P&L at 36 months", f"=INDEX({mr('ccash')},36)", RS, "Rs, undiscounted (operator, round 5)"),
        ("npv60", "Cumulative P&L at 60 months", f"=INDEX({mr('ccash')},60)", RS, "Rs, undiscounted"),
        ("payback", "Payback month (cumulative P&L turns positive)", f'=IF(MIN({mr("pb")})>60,"never within 60 months",MIN({mr("pb")}))', '0',
         "month (and stays positive)"),
        ("peak", "Peak cash need (lowest cumulative P&L)", f"=MIN(0,MIN({mr('ccash')}))", RS, "Rs (negative: the cash needed is its size)"),
        ("l20_36", "NPV (legacy, 20% discount): NPV at 36 months",
         f"=SUMPRODUCT(Monthly!{M['net']}{FIRST}:{M['net']}{FIRST + 35},Monthly!{M['df20']}{FIRST}:{M['df20']}{FIRST + 35})", RS, "Rs, reference only"),
        ("l20_60", "NPV (legacy, 20% discount): NPV at 60 months", f"=SUMPRODUCT({mr('net')},{mr('df20')})", RS, "Rs, reference only"),
        ("hfees", "Our fees on home loans and LAP in 60 months", f"=SUM({mr('x_loan_home')})+SUM({mr('x_loan_lap')})", RS, "Rs"),
        ("inc60", "Agent pay on balance, 60 months", f"=SUM({mr('c_inc')})", RS, "Rs (0.25% a year of his savers' balance)"),
        ("value", "Value per sign-up, his first 5 years, discounted to his sign-up month (a month-1 sign-up)",
         f"=SUM('Age profile'!{C['valb']}{FIRST}:{C['valb']}{LAST})+SUMPRODUCT('Cohort x age'!{K['mk']}{FIRST}:{K['mk']}{LAST},"
         f"'Age profile'!{C['df']}{FIRST}:{C['df']}{LAST})/INDEX(Monthly!{M['su']}{FIRST}:{M['su']}{LAST},1)", RS, "Rs (before the agent's salary)"),
        ("salary_su", "Agent's salary per sign-up (for comparison)", "=in_salary/in_signups_run", RS, "Rs"),
        ("year1", "Year-1 P&L (months 1-12)", f"=SUM(Monthly!{M['net']}{FIRST}:{M['net']}{FIRST + 11})", RS, "Rs"),
        ("cash60", "Cumulative cash at month 60", f"=INDEX({mr('ccash')},60)", RS, "Rs"),
        ("savers60", "Savers still saving at month 60", f"=INDEX({mr('s')},60)", '#,##0', "savers"),
        ("visits_peak", "Peak cash visits a day", f"=MAX({mr('vis')})", '#,##0', "visits a day"),
        ("upi60", "Share of savers on UPI at month 60", f"=INDEX({mr('upi')},60)", PCT, "share"),
        ("upin60", "UPI share needed at month 60 to stay within one agent's visits", f"=INDEX({mr('upin')},60)", PCT, "share"),
        ("cap60", "Extra capacity cost in month 60", f"=INDEX({mr('c_cap')},60)", RS, "Rs a month"),
        ("cap_tot", "Extra capacity cost, 60 months, not discounted", f"=SUM({mr('c_cap')})", RS, "Rs"),
        ("cap_pv", "Extra capacity cost, 60 months, discounted", f"=SUMPRODUCT({mr('c_cap')},{mr('df')})", RS, "Rs"),
        ("loans100", "Loans per 100 savers offered the marketplace, a year (first + repeat)", f"=100*SUM({mr('ln')})/{proven_years}", '0.00', "loans"),
        ("loans60", "Loans made in 60 months", f"=SUM({mr('ln')})", '#,##0.0', "loans"),
        ("p90", "Implied share of loans that ever go 90+ days bad (p90)", "=d_p90", PCT, "CRIF NG-015 10.2%; MAC-03 3.6%"),
        ("check", "Early brought back + p90", "=d_check", PCT, "page check: at most 50%"),
        ("checkflag", "Page check", "=d_check_flag", None, ""),
        ("dpd_loan", "31-90 day collection fees per loan made", "=d_dpd", RS2, "Rs a loan, paid ~9 months after the loan"),
        ("rec_loan", "90+ recovery fees per loan made", "=d_rec", RS2, "Rs a loan, paid ~18 months after the loan"),
        ("xs_total", "Cross-sell money per saver offered the marketplace, a year, all 17 products (old: Rs 63)",
         "=(" + "+".join(f"SUM({mr('x_' + p)})" for p, *_ in E.PRODUCTS) + f")/{proven_years}", RS2, "Rs a saver offered, a year (60-month book)"),
        *[(f"xs_{p}", f"   {nm}", f"=SUM({mr('x_' + p)})/{proven_years}", RS2, "Rs a saver offered, a year") for p, _k, nm, _d in E.PRODUCTS],
        ("allin", "All-in revenue per active saver a year, 60-month average", f"=SUM({mr('inc')})/(SUM({mr('s')})/12)", RS, "Rs (fund + loans + cards + products + collections)"),
        ("allin60", "All-in revenue per active saver a year, month-60 run rate", f"=12*INDEX({mr('inc')},60)/INDEX({mr('s')},60)", RS, "Rs"),
        ("tu100", "Top-ups per 100 borrowers a year (still saving, loan running)", f"=100*SUM({mr('tu')})/(SUM({mr('wl')})/12)", '0.00', "top-ups"),
        ("lent60", "Money lent in 60 months (first, repeat and top-up loans)", f"=SUM({mr('lent')})", RS, "Rs"),
        ("cards60", "Cards issued in 60 months", f"=SUM({mr('cards')})", '#,##0.0', "cards"),
        *[(f"lent_y{y}", f"   money lent in year {y}", f"=SUM(Monthly!{M['lent']}{FIRST + 12 * (y - 1)}:{M['lent']}{FIRST + 12 * y - 1})", RS, "Rs")
          for y in range(1, 6)],
        *[(f"tick_y{y}", f"   average ticket of first and repeat loans, year {y}",
           f"=IF(SUM(Monthly!{M['ln']}{FIRST + 12 * (y - 1)}:{M['ln']}{FIRST + 12 * y - 1})>0,SUM(Monthly!{M['lentn']}{FIRST + 12 * (y - 1)}:"
           f"{M['lentn']}{FIRST + 12 * y - 1})/SUM(Monthly!{M['ln']}{FIRST + 12 * (y - 1)}:{M['ln']}{FIRST + 12 * y - 1}),0)", RS, "Rs") for y in range(1, 6)],
        ("pv_inc", "Income, 60 months, discounted", f"=SUMPRODUCT({mr('inc')},{mr('df')})", RS, "Rs"),
        ("pv_cost", "Costs, 60 months, discounted", f"=SUMPRODUCT({mr('cost')},{mr('df')})", RS, "Rs"),
    ]
    srow = {}
    for k, (sid, lab, f, fm, u) in enumerate(S):
        i = hdr_row + 1 + k
        sm.cell(i, 1, lab).font = BOLD if sid in ("npv36", "npv60", "payback", "value") else BLACK
        c = sm.cell(i, 2, f)
        c.font = BOLD if sid in ("npv36", "npv60", "payback", "value") else BLACK
        if fm:
            c.number_format = fm
        sm.cell(i, 3, u).font = GREY
        srow[sid] = i
    return wb, sm, hdr_row + 1 + len(S) + 2, srow, (C, K, M)


def mc_block(sm, r0):
    """The Monte Carlo results, pasted as values (no formulas)."""
    t = E.T
    summ = list(csv.DictReader((t / "cohort_mc_summary.csv").open()))
    drv = list(csv.DictReader((t / "cohort_mc_drivers.csv").open()))
    by = list(csv.DictReader((t / "cohort_mc_by_r12.csv").open()))
    xs = list(csv.DictReader((t / "cohort_mc_crosssell.csv").open()))
    draws = next(r for r in summ if r["measure"] == "Draws")
    r = r0
    c = sm.cell(r, 1, f"Monte Carlo results (pasted from model/cohort_mc.py, 10,000 draws, {date.today().strftime('%d %b %Y')})")
    c.font = Font(name=F, size=12, bold=True)
    for j in range(1, 12):
        sm.cell(r, j).fill = MCFILL
    r += 1
    sm.cell(r, 1, "VALUES ONLY: these do not recalculate when you change Inputs. Re-run model/cohort_mc.py, then this builder, to refresh them. "
                  f"{draws['note']}").font = GREY
    r += 2
    heads = ["Measure", "p5", "p10", "p25", "p50", "p75", "p90", "p95", "mean", "value", "unit"]
    for j, h in enumerate(heads, 1):
        cc = sm.cell(r, j, h)
        cc.font, cc.fill = HEAD, HFILL
    r += 1
    for row in summ:
        if row["measure"] in ("Draws", "Distribution file"):
            continue
        sm.cell(r, 1, row["measure"]).font = BLACK
        share = row["unit"].startswith("share")
        for j, k in enumerate(heads[1:10], 2):
            v = row[k]
            if v in ("", None):
                continue
            try:
                v = float(v)
            except ValueError:
                pass
            cc = sm.cell(r, j, v)
            cc.font = BLACK
            if isinstance(v, float):
                cc.number_format = PCT if share else ('#,##0.00' if abs(v) < 100 else RS)
        sm.cell(r, 11, row["unit"]).font = GREY
        r += 1
    r += 1
    sm.cell(r, 1, "Chance the 5-year NPV is above zero, by still saving at month 12 (every other input still varies)").font = BOLD
    r += 1
    for j, h in enumerate(["Still saving at month 12", "draws", "chance NPV60 > 0", "median NPV60 (Rs)", "chance NPV36 > 0", "median NPV36 (Rs)"], 1):
        cc = sm.cell(r, j, h)
        cc.font, cc.fill = HEAD, HFILL
    r += 1
    for row in by:
        sm.cell(r, 1, row["still_saving_at_month_12"]).font = BLACK
        for j, k, fm in ((2, "draws", '0'), (3, "chance_npv60_above_zero", PCT), (4, "median_npv60", RS), (5, "chance_npv36_above_zero", PCT), (6, "median_npv36", RS)):
            if row[k] != "":
                sm.cell(r, j, float(row[k])).number_format = fm
        r += 1
    r += 1
    sm.cell(r, 1, "What moves the 5-year NPV most (rank correlation; swing = mean NPV60 in the input's top 10% of draws minus its bottom 10%)").font = BOLD
    r += 1
    for j, h in enumerate(["Input", "rank correlation", "swing (Rs)"], 1):
        cc = sm.cell(r, j, h)
        cc.font, cc.fill = HEAD, HFILL
    r += 1
    for row in drv[:12]:
        sm.cell(r, 1, row["input"]).font = BLACK
        sm.cell(r, 2, float(row["spearman_with_npv60"])).number_format = '+0.00;-0.00'
        sm.cell(r, 3, float(row["swing_npv60_top_minus_bottom_decile"])).number_format = RS
        r += 1
    r += 1
    sm.cell(r, 1, "Cross-sell money per saver offered the marketplace, a year, by product (Rs, 60-month book)").font = BOLD
    r += 1
    for j, h in enumerate(["Product", "p10", "p50", "p90", "mean"], 1):
        cc = sm.cell(r, j, h)
        cc.font, cc.fill = HEAD, HFILL
    r += 1
    for row in xs:
        sm.cell(r, 1, row["product"]).font = BLACK
        for j, k in ((2, "p10"), (3, "p50"), (4, "p90"), (5, "mean")):
            if row[k] != "":
                sm.cell(r, j, float(row[k])).number_format = RS2
        r += 1
    return r


def readme(wb, missing, notes, srow):
    ws = wb["Read me"]
    ws.column_dimensions["A"].width = 120
    lines = [
        ("Cohort model: one street agent, 60 months, one cohort of sign-ups a month", TITLE),
        ("", BLACK),
        ("WHAT TO EDIT", BOLD),
        ("Only the BLUE cells on the Inputs sheet (column C, 'Likely'). Yellow-filled blue cells are operator decisions or open choices "
         "(still saving at month 12, the fund commission, card share, loan tenure, sign-ups). Low / High / Shape beside them are the "
         "Monte Carlo ranges, shown for reference; the formulas use only the Likely column. Every cell comment says where the number comes from.", WRAP),
        ("Example: to test 40 of 100 still saving at month 12, type 0.40 into 'Still saving at month 12'; the Summary NPVs move at once.", BLACK),
        ("Black = formulas. Green = a link to another sheet. Nothing else should be typed over.", BLACK),
        ("", BLACK),
        ("HOW THE SHEETS FLOW", BOLD),
        ("Inputs -> Retention curve (ages 1-60) -> Age profile (one sign-up's saving, fund, UPI and KYC lines by age) -> Sign-ups by age "
         "(which cohort is which age in each month) -> Cohort x age (the marketplace lines - loans, top-ups, cards, the 17 products and "
         "collections - one row per cohort and age, because take-up and approvals grow with the calendar year) -> Monthly (age-profile "
         "lines = SUMPRODUCT with Sign-ups by age; marketplace lines = SUMIFS of Cohort x age by calendar month; then salary, extra "
         "capacity, KYC, the P&L, the discount factor and NPV) -> Summary. Cohort triangle shows savers still saving by cohort and month.", WRAP),
        ("", BLACK),
        ("HOW IT IS BUILT (approximations, also in model/cohort_engine.py)", BOLD),
        ("Retention: drop-off at a steady monthly rate within months 1-3 (to r3), 4-12 (to r12), then churn_late. A saver who stops "
         "withdraws his whole balance. The balance builds over a 12-month term; at a term end the rollover share stays, the rest is paid out; "
         "a share is withdrawn mid-term each month.", WRAP),
        ("Marketplace: loans, cards and all 17 products are offered from month 1 (Inputs: first month a saver is offered; the operator, "
         "16 Oct: 'the marketplace opens as soon as possible... It's not at our cost'). There is no marketplace cost line: costs are salary, "
         "extra capacity, KYC per sign-up and support (0).", WRAP),
        ("Loans: savers offered the marketplace (still saving) with no loan running apply at a monthly hazard; first loans use the first-loan approval, "
         "repeat loans the repeat approval. A borrower is out of the applicant pool while his loan runs (tenure rounded to whole months) and "
         "returns, if still saving, the month after it ends. Churn does not depend on having a loan. A saver who stops keeps paying, gets no repeat.", WRAP),
        ("Overdue loans: p90 = loss / (owed x (1 - recovered)) is the share of loans that ever go 90+ days bad. Fees per loan made = "
         "early_cured x fee_early, paid ~9 months after the loan, plus p90 x recovered x fee_b3, paid ~18 months after; fees due after "
         "month 60 are not counted. The lender carries the loss itself. Insurance commissions sit at the IRDAI draft distributor caps.", WRAP),
        ("Cross-sell: 17 products, each with a yearly take-up hazard among savers offered, still saving, who never held it (a lapsed holder is "
         "not sold it again). Insurance pays a first-year commission and renewals; SIP, gold, recharge and bills earn while the holder "
         "continues; renewals and flows are counted only while he is still saving (conservative).", WRAP),
        ("Cards: card share, issued once, evenly over the first 6 marketplace months (months 1-6) to those still saving, under the early "
         "factors; the share those factors held back is issued over months 7-12 at full rates (review fix).", WRAP),
        ("Early months: in a saver's months 1-6 every take-up (loan applications, cards, the 17 products) is multiplied by the early "
         "take-up factor, and first-loan and card approval by the early approval factor; both are 1 from month 7.", WRAP),
        ("Basis (round 5): undiscounted cumulative P&L - the operator: 'we dont need to have a discount rate as of now. Let VC calculate "
         "it.' The discount input is 0; the 'NPV (legacy, 20% discount)' rows are for reference only. Payback = the first month from which "
         "cumulative P&L stays positive; peak cash need = its lowest point.", WRAP),
        ("Housing (round 5-6): home loans and loans against property from other lenders, once per saver, take-up x an approval share "
         "(cap 80%), fee at disbursal, no collections. Cash cover (fidelity and cash-in-transit insurance) is a cost per agent a month. "
         "Insurance commissions reach us through a broker partner, who keeps a share.", WRAP),
        ("Fund return: the saver's net return accrues each month on his average balance; rollover and withdrawals include it, so it "
         "raises the money in the fund and the commission on it.", WRAP),
        ("Growth with the pool's history (addendum 4): sign-ups grow each year from year 2 (cap 100 a month); every take-up rises each "
         "calendar year (cap 2x) and first-loan and card approval too (first-loan approval capped at 80%); a repeat loan is bigger by the "
         "ticket growth for each year of the loan he repaid (cap Rs 5 lakh); a top-up (share of borrowers with 12+ EMIs paid, still "
         "saving, at most one per loan, sized after one year repaid) earns the origination fee and adds to collections pro rata. "
         "On 'Cohort x age' the lag look-ups range over the cohort's own rows; only the repeat-loan pool looks at rows above it "
         "(that column feeds the loans it looks up), and the first row of each cohort holds its starting values.", WRAP),
        ("Capacity: cash visits a day = cash savers / days between visits; above one agent's capacity the extra cost is Rs 20,000 a month per "
         "400 visits a day, pro-rata.", WRAP),
        ("", BLACK),
        ("CHECKS", BOLD),
        ("model/cohort_engine.py computes the same model in Python; tables/cohort_xlsx_check.csv records that this workbook matches it. "
         "With legacy=True the engine reproduces the v2 deck's NPVs exactly (tables/cohort_legacy_check.csv).", WRAP),
        ("Recalculation note: the workbook is saved with 'recalculate on open'. It was verified with the Python 'formulas' engine "
         "because LibreOffice is not installed on the build machine.", WRAP),
        (f"Inputs not yet in {E.DIST_FILE.name} (taken from COHORT_INPUTS and its addenda): {len(missing)} keys"
         + (f", e.g. {', '.join(missing[:6])}" if missing else "") + ".", WRAP),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = ws.cell(i, 1, t)
        if isinstance(f, Alignment):
            c.font, c.alignment = BLACK, f
        else:
            c.font = f


# ---------------------------------------------------------------- recalc + reconcile
def recalc(path):
    import formulas
    warnings.filterwarnings("ignore")
    sol = formulas.ExcelModel().loads(str(path)).finish().calculate()
    vals = {}
    for k, v in sol.items():
        if "!" not in k or ":" in k.split("!")[1]:
            continue
        sheet, cell = k.split("]", 1)[1].rsplit("!", 1)
        try:
            vv = v.value[0][0]
        except Exception:
            vv = v
        vals[(sheet.strip("'").upper(), cell)] = vv
    return vals


def main():
    dists, missing, notes = E.load_dists()
    x = E.likely_inputs(dists)
    wb, sm, r0, srow, (C, K, M) = build(dists, missing, notes)
    mc_block(sm, r0)
    readme(wb, missing, notes, srow)
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 90
    tmp = S_DIR / "Cohort_model_build.xlsx"
    S_DIR.mkdir(parents=True, exist_ok=True)
    wb.save(tmp)
    vals = recalc(tmp)
    errs = [(s, c, v) for (s, c), v in vals.items() if isinstance(v, str) and v.startswith("#")]
    errs += [(s, c, str(v)) for (s, c), v in vals.items() if type(v).__name__ in ("XlError",) or str(v).startswith("#")]
    errs = sorted(set(errs))
    n_formulas = sum(1 for ws in wb.worksheets for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("="))
    py = E.run(x)
    o = {k: float(v[0]) for k, v in py["out"].items()}
    g = lambda sid: vals.get(("SUMMARY", f"B{srow[sid]}"))
    num = lambda v: float(v) if not isinstance(v, str) else float("nan")
    checks = [("npv36", "Cumulative P&L at 36 months", o["cum_pnl36"]), ("npv60", "Cumulative P&L at 60 months", o["cum_pnl60"]),
              ("peak", "Peak cash need", o["peak_cash_need"]), ("l20_36", "NPV (legacy, 20% discount) at 36 months", o["npv36_legacy20"]),
              ("l20_60", "NPV (legacy, 20% discount) at 60 months", o["npv60_legacy20"]),
              ("hfees", "Fees on home loans and LAP", o["housing_fees60"]), ("inc60", "Agent pay on balance, 60 months", o["incentive_total60"]),
              ("payback", "Payback month", o["payback_month"]), ("value", "Value per sign-up (5 years, discounted)", o["value_per_signup"]),
              ("year1", "Pilot year-1 cash", o["year1_cash"]), ("cash60", "Cumulative cash at month 60", o["cum_cash60"]),
              ("savers60", "Savers at month 60", o["savers_m60"]), ("visits_peak", "Peak cash visits a day", o["visits_peak"]),
              ("upi60", "UPI share at month 60", o["upi_share_m60"]), ("upin60", "UPI share needed at month 60", o["upi_share_needed_m60"]),
              ("cap_pv", "Extra capacity cost, discounted", o["extra_capacity_pv60"]), ("loans100", "Loans per 100 savers offered a year", o["loans_per_100_offered_year"]),
              ("dpd_loan", "31-90 day fees per loan", o["dpd31_90_per_loan"]), ("rec_loan", "90+ fees per loan", o["rec90_per_loan"]),
              ("xs_total", "Cross-sell per saver offered a year", o["xs_total_per_offered_year"]),
              ("allin", "All-in revenue per active saver a year", o["income_per_active_year"]),
              ("allin60", "All-in revenue per active saver a year, month 60", o["income_per_active_year_m60"]),
              ("tu100", "Top-ups per 100 borrowers a year", o["topups_per_100_borrowers_year"]),
              ("lent60", "Money lent in 60 months", o["money_lent60"]), ("cards60", "Cards issued in 60 months", o["cards60"]),
              *[(f"lent_y{y}", f"Money lent in year {y}", o[f"money_lent_y{y}"]) for y in range(1, 6)],
              *[(f"tick_y{y}", f"Average ticket, year {y}", o[f"avg_ticket_y{y}"]) for y in range(2, 6)],
              ("pv_inc", "Income, discounted", o["pv_income60"]), ("pv_cost", "Costs, discounted", o["pv_cost60"])]
    rows = []
    for sid, lab, pv in checks:
        xv = num(g(sid))
        d = (xv - pv) / abs(pv) * 100 if pv else (0.0 if xv == pv else float("inf"))
        rows.append({"measure": lab, "excel": xv, "python": pv, "difference_pct": d, "within_0_5pct": abs(d) <= 0.5})
    # every Monthly line, month by month
    mcols = {"s": "still_saving", "inc": "income", "net": "net", "cnpv": "cum_npv", "c_cap": "cost_extra_capacity", "ln": "loans",
             "tu": "topups", "lent": "money_lent", "r_orig": "rev_origination", "x_hlth_family": "rev_xs_hlth_family", "x_recharge": "rev_xs_recharge"}
    worst = 0.0
    for cid, pk in mcols.items():
        if pk is None or cid not in M:
            continue
        for t in range(1, E.MONTHS + 1):
            xv, pv = num(vals.get(("MONTHLY", f"{M[cid]}{t + 1}"))), float(py["monthly"][pk][0, t - 1])
            if abs(pv) > 1:
                worst = max(worst, abs(xv - pv) / abs(pv) * 100)
    rows.append({"measure": "Worst monthly gap (savers, income, net, cumulative NPV, extra capacity), months 1-60", "excel": "", "python": "",
                 "difference_pct": worst, "within_0_5pct": worst <= 0.5})
    tri = max(abs(num(vals.get(("COHORT TRIANGLE", f"{L(t + 1)}{LAST + 2}")))) for t in range(1, E.MONTHS + 1))
    rows.append({"measure": "Cohort triangle total minus Monthly savers (largest gap, savers)", "excel": tri, "python": 0.0,
                 "difference_pct": "", "within_0_5pct": tri < 1e-6})
    rows.append({"measure": f"Formula errors after recalculation ({n_formulas} formulas)", "excel": len(errs), "python": 0, "difference_pct": "",
                 "within_0_5pct": len(errs) == 0})
    E.write("cohort_xlsx_check.csv", rows)
    shutil.copy(tmp, OUT)
    print(f"wrote {OUT} ({n_formulas} formulas); errors {len(errs)} {errs[:10]}")
    for r in rows:
        print(f"  {r['measure']:<90} excel {r['excel']!s:>18.18} python {r['python']!s:>18.18} diff% {r['difference_pct']!s:>10.10} ok {r['within_0_5pct']}")
    assert all(r["within_0_5pct"] for r in rows), "reconciliation failed"


if __name__ == "__main__":
    main()

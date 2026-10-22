"""Build savings_first_model.xlsx from the frozen input tables.

Every model cell is a live formula. The workbook mirrors engine.py line for
line; verify.py recalculates the workbook for bear/base/bull and asserts it
matches the engine.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

import engine

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "model" / "savings_first_model.xlsx"
M = engine.MONTHS

# ---------------------------------------------------------------- styles
F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF")
BLACK = Font(name=F, size=10, color="000000")
GREEN = Font(name=F, size=10, color="008000")
BOLD = Font(name=F, size=10, bold=True)
TITLE = Font(name=F, size=14, bold=True)
NOTE = Font(name=F, size=9, italic=True, color="555555")
HEAD = Font(name=F, size=10, bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
SEC_FILL = PatternFill("solid", fgColor="D9E1F2")
YELLOW = PatternFill("solid", fgColor="FFFF00")
THIN = Border(bottom=Side(style="thin", color="BBBBBB"))
WRAP = Alignment(wrap_text=True, vertical="top")

INR = '#,##0;(#,##0);"-"'
INR2 = '#,##0.00;(#,##0.00);"-"'
PCT = '0.0%;(0.0%);"-"'
MULT = '0.00"x";(0.00"x");"-"'
NUM = '#,##0.0;(#,##0.0);"-"'


def style_row(ws, r, n, font=BLACK, fmt=None, fill=None):
    for c in range(1, n + 1):
        cell = ws.cell(r, c)
        cell.font = font
        if fmt:
            cell.number_format = fmt
        if fill:
            cell.fill = fill


def header(ws, r, labels, widths=None):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(r, i, lab)
        c.font, c.fill, c.alignment = HEAD, HEAD_FILL, Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[L(i)].width = w


def section(ws, r, text, ncols):
    ws.cell(r, 1, text).font = BOLD
    for c in range(1, ncols + 1):
        ws.cell(r, c).fill = SEC_FILL


def add_name(wb, name, ref):
    wb.defined_names[name] = DefinedName(name, attr_text=ref)


def read_csv(name):
    with open(ROOT / "tables" / name, newline="") as f:
        return list(csv.DictReader(f))


NG_NAMES: set[str] = set()
_NAME = re.compile(r"\b([a-z][a-z0-9_]*)\b")


def to_ng(formula):
    """Point every input (and derived) name in a formula at its non-gig LIVE cell."""
    return _NAME.sub(lambda m: m.group(1) + "_ng" if m.group(1) in NG_NAMES else m.group(1), formula)


def is_pending(row):
    b = (row.get("basis") or "").lower()
    return "pending" in b or "pilot must prove" in b or "unverified" in b


# ---------------------------------------------------------------- Inputs
def build_inputs(wb):
    ws = wb.active
    ws.title = "Inputs"
    ws["A1"] = "Inputs: every assumption, one row each"
    ws["A1"].font = TITLE
    ws["A2"] = "Scenario (1 = bear, 2 = base, 3 = bull)"
    ws["A2"].font = BOLD
    ws["C2"] = 2
    ws["C2"].font, ws["C2"].fill = Font(name=F, size=11, bold=True, color="0000FF"), YELLOW
    ws["D2"] = '=CHOOSE(scenario,"Bear","Base","Bull")'
    ws["D2"].font = BOLD
    add_name(wb, "scenario", "Inputs!$C$2")
    ws["A3"] = ("Blue = typed input. Black = formula. Green = link to another sheet. "
                "Yellow row = waiting on research, or a claim the pilot must prove. "
                "Every model cell uses the LIVE column, which follows the scenario switch in C2. "
                "Channel inputs sit on 'Funnel & CAC'; yearly growth inputs on 'Path to $100M'.")
    ws["A3"].font = NOTE
    ws.merge_cells("A3:L3")
    ws.row_dimensions[3].height = 30
    ws["A3"].alignment = WRAP
    cols = ["id", "Assumption", "Bear", "Base", "Bull", "LIVE (gig)", "Non-gig bear", "Non-gig base", "Non-gig bull",
            "LIVE (non-gig)", "Unit", "Population", "Basis", "Non-gig basis", "Source", "As of", "Notes"]
    header(ws, 5, cols, [18, 46, 10, 10, 10, 11, 10, 10, 10, 11, 20, 30, 26, 26, 30, 11, 50])
    r = 6
    for table, title in (("inputs.csv", "Savings-first model (non-gig columns blank = same as gig)"), ("inputs_lending_first.csv", "Lending-first comparison (Bueno-style)")):
        section(ws, r, title, 17)
        r += 1
        last_sec = None
        for row in read_csv(table):
            if row["section"] != last_sec and table == "inputs.csv":
                ws.cell(r, 2, row["section"]).font = Font(name=F, size=10, bold=True, italic=True)
                r += 1
                last_sec = row["section"]
            ngv = [row.get(k, "") for k in ("ng_bear", "ng_base", "ng_bull")]
            ngv = [float(x) if x not in ("", None) else None for x in ngv]
            vals = [row["id"], row["name"], float(row["bear"]), float(row["base"]), float(row["bull"]),
                    f"=CHOOSE(scenario,C{r},D{r},E{r})", ngv[0], ngv[1], ngv[2],
                    f'=IF(H{r}="",F{r},CHOOSE(scenario,G{r},H{r},I{r}))',
                    row["unit"], row["population"], row["basis"], row.get("ng_basis", ""),
                    row["source"], row["as_of"], row["notes"]]
            for i, v in enumerate(vals, 1):
                c = ws.cell(r, i, v)
                c.font = BLUE if i in (3, 4, 5, 7, 8, 9) else BLACK
                c.alignment = Alignment(vertical="top", wrap_text=i in (2, 12, 17))
            nums = [float(row[k]) for k in ("bear", "base", "bull")] + [x for x in ngv if x is not None]
            fmt = PCT if (row["unit"].startswith("share") or row["unit"].startswith("per year")
                          or row["unit"] == "annual IRR") else ('#,##0' if all(v == int(v) for v in nums) else '#,##0.00')
            for i in (3, 4, 5, 6, 7, 8, 9, 10):
                ws.cell(r, i).number_format = fmt
            ws.cell(r, 6).font = BOLD
            ws.cell(r, 10).font = BOLD
            if is_pending(row) or "pending" in (row.get("ng_basis", "") or "").lower() or "unverified" in (row.get("ng_basis", "") or "").lower():
                for i in range(1, 18):
                    ws.cell(r, i).fill = YELLOW
            add_name(wb, row["id"], f"Inputs!$F${r}")
            if table == "inputs.csv":
                add_name(wb, row["id"] + "_ng", f"Inputs!$J${r}")
                NG_NAMES.add(row["id"])
            r += 1
        r += 1
    section(ws, r, "Derived from the inputs above (formulas; do not type here)", 17)
    r += 1
    derived = [
        ("loan_lost", "Share of UNSECURED money lent never recovered = 90+ late (ladder) × still owed × not recovered",
         "=ladder_dpd90*loan_ead*loan_lgd", PCT),
        ("nbfc_int_r", "Own NBFC: interest on ₹1 lent over the loan's life", "=PMT(nbfc_apr/12,loan_tenor,-1)*loan_tenor-1", PCT),
        ("nbfc_cof_r", "Own NBFC: borrowing cost on ₹1 lent over the loan's life", "=PMT(nbfc_cof/12,loan_tenor,-1)*loan_tenor-1", PCT),
        ("nbfc_avg_frac", "Own NBFC: average balance over the loan's life, as a share of the loan",
         "=((1+nbfc_apr/12)^loan_tenor-((1+nbfc_apr/12)^loan_tenor-1)/(loan_tenor*nbfc_apr/12))/((1+nbfc_apr/12)^loan_tenor-1)", PCT),
    ]
    for nm, lab, f, fmt in derived:
        ws.cell(r, 1, nm).font = BLACK
        ws.cell(r, 2, lab).font = BLACK
        ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
        c = ws.cell(r, 6, f)
        c.font, c.number_format = BOLD, fmt
        c = ws.cell(r, 10, to_ng(f))
        c.font, c.number_format = BOLD, fmt
        add_name(wb, nm, f"Inputs!$F${r}")
        add_name(wb, nm + "_ng", f"Inputs!$J${r}")
        NG_NAMES.add(nm)
        r += 1
    for nm, lab, f, fmt in [("seg_n_gig", "Gig savers in one cohort", "=cohort_size*mix_gig", INR),
                            ("seg_n_ng", "Non-gig savers in one cohort", "=cohort_size*(1-mix_gig)", INR),
                            ("churn_path", "Late monthly churn, mix-weighted (path after year 5)", "=mix_gig*churn_late+(1-mix_gig)*churn_late_ng", PCT)]:
        ws.cell(r, 1, nm).font = BLACK
        ws.cell(r, 2, lab).font = BLACK
        c = ws.cell(r, 6, f)
        c.font, c.number_format = BOLD, fmt
        add_name(wb, nm, f"Inputs!$F${r}")
        r += 1
    ws.freeze_panes = "C6"
    return ws


# ---------------------------------------------------------------- Funnel & CAC
CH_INPUTS = [("mix", "Share of its segment", PCT), ("cost_per_install", "Cost per install (₹)", INR),
             ("p_install_kyc", "Install → KYC", PCT), ("p_kyc_mandate", "KYC → mandate", PCT),
             ("p_mandate_debit", "Mandate → first debit", PCT), ("kyc_cost", "KYC cost per KYC (₹)", INR),
             ("mandate_cost", "Mandate cost per mandate (₹)", INR), ("reward", "Joining reward (₹)", INR),
             ("referral_cost", "Referral bonus (₹)", INR), ("partner_fee", "Partner fee (₹)", INR)]


def build_funnel(wb):
    ws = wb.create_sheet("Funnel & CAC")
    ws["A1"] = "Funnel & CAC: fully loaded cost per ACTIVATED saver (first successful auto-debit), by channel"
    ws["A1"].font = TITLE
    ws["A2"] = ("CAC per activated saver = cost per install × scenario multiplier ÷ (install→activated) "
                "+ KYC cost ÷ (KYC→activated) + mandate cost ÷ (mandate→first debit) + reward + referral bonus + partner fee.")
    ws["A2"].font = NOTE
    labels = ["Channel"] + [x[1] for x in CH_INPUTS] + ["Install → activated", "Acquisition per activated (₹)",
                                                        "KYC per activated (₹)", "Mandate per activated (₹)",
                                                        "Rewards + referral + partner (₹)", "CAC per activated saver (₹)", "Basis", "Notes"]
    header(ws, 4, labels + ["Install weight (share of all savers ÷ install→activated)"], [44] + [11] * 16 + [22, 50, 14])
    ws.row_dimensions[4].height = 45
    chans = read_csv("channels.csv")
    first = 5
    seg_rows = {"gig": [], "nongig": []}
    for j, ch in enumerate(chans):
        r = first + j
        seg = ch.get("segment", "gig")
        seg_rows[seg].append(r)
        ws.cell(r, 1, ("Gig · " if seg == "gig" else "Non-gig · ") + ch["label"]).font = BLACK
        for i, (k, _, fmt) in enumerate(CH_INPUTS, 2):
            c = ws.cell(r, i, float(ch[k]))
            c.font, c.number_format = BLUE, fmt
        # B mix, C cpi, D i2k, E k2m, F m2d, G kyc, H mandate, I reward, J referral, K partner
        f = {
            12: f"=D{r}*E{r}*F{r}",
            13: f"=C{r}*{'cac_mult' if seg == 'gig' else 'cac_mult_ng'}/L{r}",
            14: f"=G{r}/(E{r}*F{r})",
            15: f"=H{r}/F{r}",
            16: f"=I{r}+J{r}+K{r}",
            17: f"=M{r}+N{r}+O{r}+P{r}",
        }
        for col, formula in f.items():
            c = ws.cell(r, col, formula)
            c.font, c.number_format = BLACK, (PCT if col == 12 else INR)
        ws.cell(r, 17).font = BOLD
        c = ws.cell(r, 20, f"=B{r}*{'mix_gig' if seg == 'gig' else '(1-mix_gig)'}/L{r}")
        c.font, c.number_format = NOTE, INR2
        ws.cell(r, 18, ch["basis"]).font = BLACK
        ws.cell(r, 19, ch["notes"]).font = NOTE
        if is_pending(ch):
            for col in range(2, 12):
                ws.cell(r, col).fill = YELLOW
    last = first + len(chans) - 1
    br = last + 1
    for seg, nm, lab in (("gig", "cac_gig", "Gig blended (channel mix)"), ("nongig", "cac_ng", "Non-gig blended (channel mix)")):
        a, b = min(seg_rows[seg]), max(seg_rows[seg])
        ws.cell(br, 1, lab).font = BOLD
        ws.cell(br, 2, f"=SUM(B{a}:B{b})").number_format = PCT
        for col in (13, 14, 15, 16, 17):
            c = ws.cell(br, col, f"=SUMPRODUCT($B${a}:$B${b},{L(col)}{a}:{L(col)}{b})/$B${br}")
            c.number_format, c.font = INR, BOLD
        ws.cell(br, 12, f"=SUMPRODUCT($B${a}:$B${b},L{a}:L{b})/$B${br}").number_format = PCT
        add_name(wb, nm, f"'Funnel & CAC'!$Q${br}")
        for col in range(1, 20):
            ws.cell(br, col).border = Border(top=Side(style="thin"))
        br += 1
    ws.cell(br, 1, "All savers (segment mix from Inputs)").font = BOLD
    c = ws.cell(br, 17, "=mix_gig*cac_gig+(1-mix_gig)*cac_ng")
    c.number_format, c.font = INR, BOLD
    add_name(wb, "cac_blended", f"'Funnel & CAC'!$Q${br}")

    # Funnel per 1,000 installs (blended) and retention
    r = br + 3
    ws.cell(r, 1, "The funnel for 1,000 installs across both segments, and how many are still saving later").font = BOLD
    r += 1
    header(ws, r, ["Stage", "People", "Share of installs"])
    T_ = f"$T${first}:$T${last}"
    stages = [("Installs", "=1000"),
              ("KYC done", f"=1000*SUMPRODUCT({T_},D{first}:D{last})/SUM({T_})"),
              ("Mandate set up", f"=1000*SUMPRODUCT({T_},D{first}:D{last},E{first}:E{last})/SUM({T_})"),
              ("First auto-debit (activated saver)", f"=1000*SUMPRODUCT({T_},L{first}:L{last})/SUM({T_})")]
    rows = {}
    for i, (lab, fml) in enumerate(stages):
        rr = r + 1 + i
        ws.cell(rr, 1, lab).font = BLACK
        ws.cell(rr, 2, fml).number_format = INR
        ws.cell(rr, 3, f"=B{rr}/$B${r + 1}").number_format = PCT
        rows[lab] = rr
    act = rows["First auto-debit (activated saver)"]
    for i, (lab, nm) in enumerate([("Still saving, month 1", "ret_m1"), ("Still saving, month 3", "ret_m3"),
                                   ("Still saving, month 6", "ret_m6"), ("Still saving, month 12", "ret_m12"),
                                   ("Still saving, month 24", "ret_m24")]):
        rr = act + 1 + i
        ws.cell(rr, 1, lab).font = BLACK
        c = ws.cell(rr, 2, f"=B{act}*(mix_gig*{nm}+(1-mix_gig)*{nm}_ng)")
        c.number_format, c.font = INR, GREEN
        ws.cell(rr, 3, f"=B{rr}/$B${r + 1}").number_format = PCT
    ws.freeze_panes = "B5"
    return br


# ---------------------------------------------------------------- Cohort
SURV = ("=IF({t}<=1,ret_m1^{t},IF({t}<=3,ret_m1*(ret_m3/ret_m1)^(({t}-1)/2),"
        "IF({t}<=6,ret_m3*(ret_m6/ret_m3)^(({t}-3)/3),IF({t}<=12,ret_m6*(ret_m12/ret_m6)^(({t}-6)/6),"
        "IF({t}<=24,ret_m12*(ret_m24/ret_m12)^(({t}-12)/12),ret_m24*(1-churn_late)^({t}-24))))))")

# (key, label, unit, month-0 value or None, formula template, number format)
COHORT = [
    ("#", "Savers"),
    ("S", "Share of activated savers still saving", "share", 1, SURV, PCT),
    ("A", "Active savers", "savers", None, "=cohort_size*{S}", INR),
    ("per_saver", "Money saved per active saver", "₹ per month", None,
     "=daily_amount*(1+amount_growth)^INT(({t}-1)/12)*debits_success", INR),
    ("C", "Money saved (contributions)", "₹", None, "={A}*{per_saver}", INR),
    ("#", "Balances (money sits with the fund house or bank, never with us)"),
    ("keep", "Share of last month's savers still saving", "share", None, "={S}/{S@p}", PCT),
    ("grown", "Last month's active balance after returns", "₹", None, "={Pa@p}*(1+fund_yield/12)", INR),
    ("stay", "…belonging to savers who stay", "₹", None, "={grown}*{keep}", INR),
    ("leave", "…belonging to savers who stop this month", "₹", None, "={grown}*(1-{keep})", INR),
    ("Pa", "Balance of active savers", "₹", 0, "={stay}*(1-withdraw_rate)+{C}", INR),
    ("D", "Balance left behind by savers who stopped", "₹", 0,
     "={D@p}*(1+fund_yield/12)*(1-dormant_withdraw)+{leave}*(1-leaver_withdraw)", INR),
    ("W", "Withdrawals", "₹", None,
     "={stay}*withdraw_rate+{leave}*leaver_withdraw+{D@p}*(1+fund_yield/12)*dormant_withdraw", INR),
    ("aum", "Total savings balance", "₹", 0, "={Pa}+{D}", INR),
    ("gold", "…held in digital gold (lever)", "₹", 0, "={aum}*gold_on*gold_share", INR),
    ("fd", "…held in bank FDs", "₹", 0, "=IF({t}>=fd_start,({aum}-{gold})*fd_share,0)", INR),
    ("liquid", "…held in the liquid fund", "₹", 0, "={aum}-{gold}-{fd}", INR),
    ("#", "Loans through partner lenders (we are the loan service provider; the lender's money)"),
    ("B", "Share of active savers who have borrowed", "share", 0,
     "=IF({t}>=loan_start,{B@p}+(loan_eligible-{B@p})*loan_apply*loan_approval,0)", PCT),
    ("newb", "Loan 1 (secured against savings): first loans", "loans", 0,
     "=IF({t}>=loan_start,{A}*(loan_eligible-{B@p})*loan_apply*loan_approval,0)", NUM),
    ("r2", "Loan 2 (secured): repaid loan 1, still saving, borrowed again", "loans", 0,
     "=IF({t}>loan_tenor,loan_repeat*(1-ladder_dpd90)*INDEX({row:newb},1,{t}-loan_tenor+1)*{S}/INDEX({row:S},1,{t}-loan_tenor+1),0)", NUM),
    ("r3", "Loan 3 (part secured)", "loans", 0,
     "=IF({t}>loan_tenor,loan_repeat*(1-ladder_dpd90)*INDEX({row:r2},1,{t}-loan_tenor+1)*{S}/INDEX({row:S},1,{t}-loan_tenor+1),0)", NUM),
    ("r4", "Loan 4 (part secured)", "loans", 0,
     "=IF({t}>loan_tenor,loan_repeat*(1-ladder_dpd90)*INDEX({row:r3},1,{t}-loan_tenor+1)*{S}/INDEX({row:S},1,{t}-loan_tenor+1),0)", NUM),
    ("r5new", "…first unsecured loans (loan 5)", "loans", 0,
     "=IF({t}>loan_tenor,loan_repeat*(1-ladder_dpd90)*INDEX({row:r4},1,{t}-loan_tenor+1)*{S}/INDEX({row:S},1,{t}-loan_tenor+1),0)", NUM),
    ("r5", "Loans 5+ (unsecured)", "loans", 0,
     "=IF({t}>loan_tenor,{r5new}+loan_repeat*(1-ladder_dpd90)*INDEX({row:r5},1,{t}-loan_tenor+1)*{S}/INDEX({row:S},1,{t}-loan_tenor+1),0)", NUM),
    ("rep", "Repeat loans (loans 2+)", "loans", 0, "={r2}+{r3}+{r4}+{r5}", NUM),
    ("loans", "All loans", "loans", 0, "={newb}+{rep}", NUM),
    ("lend", "Savings that can back a loan, per active saver (fund + FD; gold cannot)", "₹", 0,
     "=IF({A}>0,{Pa}/{A},0)*(1-gold_on*gold_share)", INR),
    ("sec", "Secured loan size (secured_ltv of that)", "₹", 0, "=secured_ltv*{lend}", INR),
    ("disb_sec", "Secured money lent (loans 1-4)", "₹", 0, "=({newb}+{r2}+{r3}+{r4})*{sec}", INR),
    ("disb_uns", "Unsecured money lent (top-ups on loans 3-4, all of loans 5+)", "₹", 0,
     "=({r3}+{r4})*{sec}*part_unsec_multiple+{r5}*loan_ticket", INR),
    ("disb", "Money lent (by partners, or by our NBFC if that lever is on)", "₹", 0, "={disb_sec}+{disb_uns}", INR),
    ("roll", "Unsecured money lent in the last loan-length months (sets the guarantee deposit)", "₹", 0,
     "={roll@p}+{disb_uns}-IF({t}>loan_tenor,INDEX({row:disb_uns},1,{t}-loan_tenor+1),0)", INR),
    ("roll_all", "All money lent in the last loan-length months (an own NBFC's book)", "₹", 0,
     "={roll_all@p}+{disb}-IF({t}>loan_tenor,INDEX({row:disb},1,{t}-loan_tenor+1),0)", INR),
    ("cap", "Capital locked: guarantee deposit, or NBFC equity for the loan book", "₹", 0,
     "=IF(nbfc_on=1,nbfc_equity*nbfc_avg_frac*{roll_all},dlg_on*dlg_cap*{roll})", INR),
    ("#", "Cards (issued by a partner bank)"),
    ("K", "Share of active savers with an FD-secured card", "share", 0,
     "=IF({t}>=card_start,{K@p}*(1-card_churn)+(card_eligible*(1-gold_on*gold_share)-{K@p})*card_uptake,0)", PCT),
    ("newc", "New FD-secured cards (only FD money, not gold, can back a card)", "cards", 0,
     "=IF({t}>=card_start,{A}*(card_eligible*(1-gold_on*gold_share)-{K@p})*card_uptake,0)", NUM),
    ("holders", "Card holders", "cards", 0, "={A}*{K}", NUM),
    ("U", "Share moved to an unsecured card", "share", 0,
     "=IF({t}>=unsec_start,{U@p}+MAX(0,{K@p}-{U@p})*unsec_grad,{U@p})", PCT),
    ("newu", "New unsecured cards", "cards", 0, "={A}*({U}-{U@p})", NUM),
    ("#", "Equity SIPs beyond the daily savings"),
    ("Q", "Share of active savers with an equity SIP", "share", 0,
     "=IF({t}>=sip_start,{Q@p}*(1-sip_stop)+(sip_eligible-{Q@p})*sip_uptake,0)", PCT),
    ("news", "New SIPs", "SIPs", 0, "=IF({t}>=sip_start,{A}*(sip_eligible-{Q@p})*sip_uptake,0)", NUM),
    ("sipaum", "SIP balance", "₹", 0, "={sipaum@p}*(1+sip_return/12)*(1-sip_redeem)+{A}*{Q}*sip_amount", INR),
    ("#", "Insurance (annual policies from partner insurers)"),
    ("I", "Share of active savers ever insured", "share", 0,
     "=IF({t}>=ins_start,{I@p}+(ins_eligible-{I@p})*ins_uptake,0)", PCT),
    ("newp", "New policies", "policies", 0, "=IF({t}>=ins_start,{A}*(ins_eligible-{I@p})*ins_uptake,0)", NUM),
    ("renew", "Renewed policies", "policies", 0,
     "=IF({t}>12,(INDEX({row:newp},1,{t}-12+1)+INDEX({row:renew},1,{t}-12+1))*ins_persist,0)", NUM),
    ("#", "Revenue"),
    ("rev_liquid", "Liquid-fund trail commission", "₹", 0, "={liquid}*trail_liquid/12", INR),
    ("rev_fd", "FD distribution fee", "₹", 0, "={fd}*fd_fee/12", INR),
    ("rev_gold", "Margin on digital gold bought (lever)", "₹", 0, "={C}*gold_on*gold_share*gold_margin", INR),
    ("rev_loans", "Loans: sourcing fee, or net interest if own NBFC", "₹", 0,
     "=IF(nbfc_on=1,{disb}*(nbfc_int_r*(1-ladder_dpd90)+nbfc_proc_fee-nbfc_cof_r),{disb_sec}*secured_fee+{disb_uns}*(lsp_fee+dlg_on*dlg_fee_uplift))", INR),
    ("rev_cards", "Card fees and interchange share", "₹", 0,
     "={newc}*card_fee+{holders}*card_spend*card_ic_share+{newu}*unsec_fee", INR),
    ("rev_sip", "SIP trail commission", "₹", 0, "={sipaum}*trail_equity/12", INR),
    ("rev_inc", "First-time investor incentive", "₹", 0, "={news}*first_time_share*mf_incentive", INR),
    ("rev_ins", "Insurance commission", "₹", 0, "=({newp}*ins_comm_first+{renew}*ins_comm_renew)*ins_premium", INR),
    ("revenue", "Total revenue", "₹", 0, "={rev_liquid}+{rev_fd}+{rev_gold}+{rev_loans}+{rev_cards}+{rev_sip}+{rev_inc}+{rev_ins}", INR),
    ("#", "Variable cost"),
    ("cost_loans", "Loans: our cost (+ losses we bear under a guarantee or own NBFC)", "₹", 0,
     "=IF(nbfc_on=1,{disb_uns}*loan_lost+{loans}*(loan_ops_cost+service_cost),{loans}*loan_ops_cost+dlg_on*(MIN(loan_lost,dlg_cap)*{disb_uns}+({r3}+{r4}+{r5})*service_cost))", INR),
    ("cost_cards", "Cards: our cost", "₹", 0, "=({newc}+{newu})*card_ops_cost", INR),
    ("cost_ins", "Insurance: our cost", "₹", 0, "={newp}*ins_ops_cost", INR),
    ("cost_pay", "Debits, pre-debit notices and failed debits", "₹", 0,
     "={A}*(debits_success*cost_debit+debits_scheduled*cost_notice+MAX(0,debits_scheduled-debits_success)*cost_failed)", INR),
    ("cost_service", "Support, tech and streak rewards", "₹", 0, "={A}*(cost_support+cost_tech+cost_rewards)", INR),
    ("cost_fraud", "Fraud", "₹", 0, "={C}*cost_fraud", INR),
    ("cost", "Total variable cost", "₹", 0,
     "={cost_loans}+{cost_cards}+{cost_ins}+{cost_pay}+{cost_service}+{cost_fraud}", INR),
    ("#", "Contribution"),
    ("cm", "Contribution margin (revenue − variable cost)", "₹", 0, "={revenue}-{cost}", INR),
    ("cm_per", "…per activated saver", "₹", 0, "={cm}/cohort_size", INR2),
    ("cum", "Cumulative contribution per activated saver", "₹", 0, "={cum@p}+{cm_per}", INR2),
    ("dcm", "Discounted contribution per activated saver", "₹", 0, "={cm_per}/(1+disc_rate)^({t}/12)", INR2),
    ("pb", "Payback flag (month if cumulative ≥ CAC, else 999)", "month", None, "=IF({cum}>=cac_blended,{t},999)", "0"),
]

TOKEN = re.compile(r"\{(row:)?(\w+)(@p)?\}")


def render(tmpl, col, rowmap, month_row):
    """Replace {X}, {X@p} and {row:X} with cell references for month column `col`."""
    prev = L(col - 1)

    def sub(m):
        rng, key, p = m.group(1), m.group(2), m.group(3)
        if key == "t":
            return f"{L(col)}${month_row}"
        r = rowmap[key]
        if rng:  # month 0 up to the PREVIOUS month: avoids a circular reference
            return f"$C${r}:{prev}${r}"
        return f"{prev if p else L(col)}{r}"

    return TOKEN.sub(sub, tmpl)


def month_cols(year):
    """Column letters of the first and last month of cohort year `year` (month m sits in column 3+m)."""
    return L(3 + (year - 1) * 12 + 1), L(3 + year * 12)


SEG_SHEET = {"gig": "Cohort gig", "ng": "Cohort non-gig"}


def seg_formula(f, seg):
    """Segment version of a cohort formula: its own saver count and CAC, and (non-gig) its own inputs."""
    f = f.replace("cohort_size", "seg_n_gig" if seg == "gig" else "seg_n_ng")
    f = f.replace("cac_blended", "cac_gig" if seg == "gig" else "cac_ng")
    return to_ng(f) if seg == "ng" else f


def build_cohort(wb, seg="gig"):
    ws = wb.create_sheet(SEG_SHEET[seg])
    who = "GIG savers (app delivery and ride)" if seg == "gig" else "NON-GIG savers (shopkeepers, self-employed trades, workers outside the apps, small business owners)"
    ws["A1"] = f"Cohort: the {who} in one monthly cohort, followed for 60 months (scenario from Inputs!C2)"
    ws["A1"].font = TITLE
    ws["A2"] = ("Month 0 (column C) holds the starting state. Loan, card and insurance economics are booked in the month "
                "the loan, card or policy is issued. Numbers are for the whole cohort unless the row says 'per activated saver'.")
    ws["A2"].font = NOTE
    month_row = 4
    ws.cell(month_row, 1, "Month of cohort life").font = BOLD
    ws.cell(month_row, 2, "unit").font = BOLD
    for m in range(0, M + 1):
        c = ws.cell(month_row, 3 + m, m)
        c.font, c.fill = HEAD, HEAD_FILL
    ws.column_dimensions["A"].width = 52
    ws.column_dimensions["B"].width = 12
    for m in range(0, M + 1):
        ws.column_dimensions[L(3 + m)].width = 10
    rowmap, r = {}, month_row + 1
    for item in COHORT:
        if item[0] == "#":
            section(ws, r, item[1], 3 + M)
            r += 1
            continue
        rowmap[item[0]] = r
        r += 1
    for item in COHORT:
        if item[0] == "#":
            continue
        key, label, unit, m0, tmpl, fmt = item
        rr = rowmap[key]
        ws.cell(rr, 1, label).font = BOLD if key in ("revenue", "cost", "cm", "A") else BLACK
        ws.cell(rr, 2, unit).font = NOTE
        if m0 is not None:
            ws.cell(rr, 3, m0).font = BLUE
            ws.cell(rr, 3).number_format = fmt
        for m in range(1, M + 1):
            col = 3 + m
            c = ws.cell(rr, col, seg_formula(render(tmpl, col, rowmap, month_row), seg))
            c.number_format = fmt
            c.font = BOLD if key in ("revenue", "cost", "cm") else BLACK
    ws.freeze_panes = "C5"
    return rowmap


TOTAL_ROWS = [  # key, label, formula template ({g} and {n} = the same cell in each segment sheet), format
    ("A", "Active savers (both segments)", "='Cohort gig'!{c}{r}+'Cohort non-gig'!{c}{r}", INR),
    ("revenue", "Total revenue", "='Cohort gig'!{c}{r}+'Cohort non-gig'!{c}{r}", INR),
    ("cost", "Total variable cost", "='Cohort gig'!{c}{r}+'Cohort non-gig'!{c}{r}", INR),
    ("cm", "Contribution margin", "='Cohort gig'!{c}{r}+'Cohort non-gig'!{c}{r}", INR),
    ("cap", "Capital locked", "='Cohort gig'!{c}{r}+'Cohort non-gig'!{c}{r}", INR),
]


def build_total(wb, rowmap):
    ws = wb.create_sheet("Cohort total")
    ws["A1"] = "Cohort total: gig + non-gig savers in one monthly cohort of `cohort_size` activated savers"
    ws["A1"].font = TITLE
    ws["A2"] = "Adds the two segment sheets month by month. LTV, payback and the path use these rows."
    ws["A2"].font = NOTE
    month_row = 4
    ws.cell(month_row, 1, "Month of cohort life").font = BOLD
    for m in range(0, M + 1):
        c = ws.cell(month_row, 3 + m, m)
        c.font, c.fill = HEAD, HEAD_FILL
    ws.column_dimensions["A"].width = 52
    for m in range(0, M + 1):
        ws.column_dimensions[L(3 + m)].width = 10
    tmap, r = {}, month_row + 1
    for key, label, tmpl, fmt in TOTAL_ROWS:
        tmap[key] = r
        ws.cell(r, 1, label).font = BOLD if key in ("revenue", "cm") else BLACK
        for m in range(0, M + 1):
            col = 3 + m
            c = ws.cell(r, col, tmpl.format(c=L(col), r=rowmap[key]))
            c.number_format, c.font = fmt, GREEN
        r += 1
    extra = [("cm_per", "…per activated saver", "={cm}/cohort_size", INR2, 0),
             ("cum", "Cumulative contribution per activated saver", "={cum@p}+{cm_per}", INR2, 0),
             ("dcm", "Discounted contribution per activated saver", "={cm_per}/(1+disc_rate)^({t}/12)", INR2, 0),
             ("pb", "Payback flag (month if cumulative ≥ blended CAC, else 999)", "=IF({cum}>=cac_blended,{t},999)", "0", None)]
    for key, *_ in extra:
        tmap[key] = r
        r += 1
    for key, label, tmpl, fmt, m0 in extra:
        rr = tmap[key]
        ws.cell(rr, 1, label).font = BLACK
        if m0 is not None:
            ws.cell(rr, 3, m0)
        for m in range(1, M + 1):
            col = 3 + m
            c = ws.cell(rr, col, render(tmpl, col, tmap, month_row))
            c.number_format = fmt
    ws.freeze_panes = "C5"
    return tmap


# ---------------------------------------------------------------- Revenue lines / Cost to serve
REV_LINES = [
    ("Savings: liquid fund", ["rev_liquid"], "Trail commission on the liquid-fund balance (regular plan). Balance × trail ÷ 12.",
     "trail_liquid"),
    ("Savings: FDs", ["rev_fd"], "Distribution fee from partner banks on FDs booked through us, taken as a yearly % of the FD balance.",
     "fd_fee"),
    ("Savings: gold", ["rev_gold"], "Lever: margin on the share of each rupee saved that goes into digital gold.", "gold_margin"),
    ("Loans (partner)", ["rev_loans"], "Sourcing fee as a % of money the partner lends; we hold no loan book. "
     "With a guarantee (dlg_on) the fee rises and we bear losses up to the 5% cap. With our own NBFC (nbfc_on) "
     "this line is net interest + processing fee − our borrowing cost.", "lsp_fee"),
    ("Cards", ["rev_cards"], "Fee per FD-secured card issued, plus a share of card spend; later a fee per unsecured card.",
     "card_fee"),
    ("SIPs", ["rev_sip", "rev_inc"], "Trail on equity SIP balances, plus any one-time incentive for first-time investors.",
     "trail_equity"),
    ("Insurance", ["rev_ins"], "Commission on first-year and renewal premiums at the capped rates.", "ins_comm_first"),
]
COST_LINES = [
    ("Debits, notices, failed debits", ["cost_pay"], "Per successful debit + per pre-debit notice (every scheduled debit) + per failed debit."),
    ("Support, tech, streak rewards", ["cost_service"], "Per active saver per month."),
    ("Fraud", ["cost_fraud"], "Share of money saved."),
    ("Loans: our cost", ["cost_loans"], "Per loan, plus guarantee losses if we give one."),
    ("Cards: our cost", ["cost_cards"], "Per card issued."),
    ("Insurance: our cost", ["cost_ins"], "Per new policy."),
]


def yearly_block(ws, r0, lines, rowmap, title, per_active_title):
    """Writes cohort-year totals and per-active-saver values; returns {line: row of per-active values}."""
    ws.cell(r0, 1, title).font = BOLD
    header(ws, r0 + 1, ["Line", "How it is calculated", "Key input (LIVE)"] + [f"Cohort year {y}" for y in range(1, 6)])
    out = {}
    for i, (name, keys, how, *key_input) in enumerate(lines):
        r = r0 + 2 + i
        ws.cell(r, 1, name).font = BLACK
        ws.cell(r, 2, how).font = NOTE
        ws.cell(r, 2).alignment = WRAP
        if key_input:
            c = ws.cell(r, 3, f"={key_input[0]}")
            c.font, c.number_format = GREEN, '0.00%'
        for y in range(1, 6):
            a, b = month_cols(y)
            f = "+".join(f"SUM('{sh}'!{a}{rowmap[k]}:{b}{rowmap[k]})" for k in keys for sh in SEG_SHEET.values())
            c = ws.cell(r, 3 + y, "=" + f)
            c.number_format, c.font = INR, GREEN
        out[name] = r
    tr = r0 + 2 + len(lines)
    ws.cell(tr, 1, "Total").font = BOLD
    for y in range(1, 6):
        c = ws.cell(tr, 3 + y, f"=SUM({L(3 + y)}{r0 + 2}:{L(3 + y)}{tr - 1})")
        c.number_format, c.font = INR, BOLD
    # per active saver
    pr0 = tr + 2
    ws.cell(pr0, 1, per_active_title).font = BOLD
    header(ws, pr0 + 1, ["Line", "", ""] + [f"Cohort year {y}" for y in range(1, 6)])
    ar = pr0 + 2
    ws.cell(ar, 1, "Average active savers in the year").font = NOTE
    for y in range(1, 6):
        a, b = month_cols(y)
        c = ws.cell(ar, 3 + y, "=(" + "+".join(f"SUM('{sh}'!{a}{rowmap['A']}:{b}{rowmap['A']})" for sh in SEG_SHEET.values()) + ")/12")
        c.number_format, c.font = INR, GREEN
    per = {}
    for i, (name, *_rest) in enumerate(lines):
        r = ar + 1 + i
        ws.cell(r, 1, name).font = BLACK
        for y in range(1, 6):
            c = ws.cell(r, 3 + y, f"={L(3 + y)}{out[name]}/{L(3 + y)}${ar}")
            c.number_format = INR
        per[name] = r
    ptr = ar + 1 + len(lines)
    ws.cell(ptr, 1, "Total").font = BOLD
    for y in range(1, 6):
        c = ws.cell(ptr, 3 + y, f"=SUM({L(3 + y)}{ar + 1}:{L(3 + y)}{ptr - 1})")
        c.number_format, c.font = INR, BOLD
    return out, per, tr, ptr, ar


def build_revenue(wb, rowmap):
    ws = wb.create_sheet("Revenue lines")
    ws["A1"] = "Revenue lines: each line's mechanics, by cohort year (cohort of activated savers, gross revenue to us)"
    ws["A1"].font = TITLE
    for col, w in zip("ABCDEFGH", [30, 70, 14, 14, 14, 14, 14, 14]):
        ws.column_dimensions[col].width = w
    tot, per, tr, ptr, ar = yearly_block(ws, 3, REV_LINES, rowmap, "Revenue per cohort (₹)",
                                         "Revenue per ACTIVE saver per year (₹) = cohort revenue ÷ average active savers that year")
    return {"per": per, "total_row": tr, "per_total_row": ptr, "active_row": ar}


def build_costs(wb, rowmap):
    ws = wb.create_sheet("Cost to serve")
    ws["A1"] = "Cost to serve: variable cost by line and cohort year (cohort of activated savers)"
    ws["A1"].font = TITLE
    for col, w in zip("ABCDEFGH", [32, 70, 14, 14, 14, 14, 14, 14]):
        ws.column_dimensions[col].width = w
    tot, per, tr, ptr, ar = yearly_block(ws, 3, COST_LINES, rowmap, "Variable cost per cohort (₹)",
                                         "Variable cost per ACTIVE saver per year (₹)")
    r = ptr + 3
    ws.cell(r, 1, "Cost to serve one active saver for one month (₹), before any cross-sell").font = BOLD
    items = [("Successful debits", "=debits_success*cost_debit"),
             ("Pre-debit notices (one per scheduled debit)", "=debits_scheduled*cost_notice"),
             ("Failed debits", "=MAX(0,debits_scheduled-debits_success)*cost_failed"),
             ("Support", "=cost_support"), ("Tech and cloud", "=cost_tech"), ("Streak rewards", "=cost_rewards")]
    for i, (lab, f) in enumerate(items):
        ws.cell(r + 1 + i, 1, lab).font = BLACK
        c = ws.cell(r + 1 + i, 4, f)
        c.number_format, c.font = INR2, GREEN
    tr2 = r + 1 + len(items)
    ws.cell(tr2, 1, "Total per active saver per month").font = BOLD
    c = ws.cell(tr2, 4, f"=SUM(D{r + 1}:D{tr2 - 1})")
    c.number_format, c.font = INR2, BOLD
    ws.cell(tr2 + 1, 1, "…per year").font = BOLD
    c = ws.cell(tr2 + 1, 4, f"=D{tr2}*12")
    c.number_format, c.font = INR, BOLD
    add_name(wb, "serve_cost_month", f"'Cost to serve'!$D${tr2}")
    return {"per_total_row": ptr, "per": per}


# ---------------------------------------------------------------- Lending-first
LF = [
    ("t", None),
    ("first", "=IF({t}=1,borrowers_lf,0)"),
    ("rep", "=IF({t}>lf_tenor,lf_repeat*((1-lf_dpd90_first)*INDEX({row:first},1,{t}-lf_tenor+1)+(1-lf_dpd90_repeat)*INDEX({row:rep},1,{t}-lf_tenor+1)),0)"),
    ("revenue", "={first}*(lf_interest*(1-lf_dpd90_first)-lf_cof_loan)+{rep}*(lf_interest*(1-lf_dpd90_repeat)-lf_cof_loan)"),
    ("losses", "=({first}*lf_dpd90_first+{rep}*lf_dpd90_repeat)*lf_ead*lf_lgd*lf_ticket*lf_risk_share"),
    ("cost", "={losses}+({first}+{rep})*lf_fixed"),
    ("cm", "={revenue}-{cost}"),
    ("book", "=({first}+{rep})*lf_ticket*lf_avg_frac*lf_tenor"),
    ("cm_per", "={cm}/borrowers_lf"),
    ("cum", "={cum@p}+{cm_per}"),
    ("dcm", "={cm_per}/(1+disc_rate)^({t}/12)"),
    ("pb", "=IF({cum}>=lf_cac,{t},999)"),
]
LF_LABELS = {"t": "Month", "first": "First loans", "rep": "Repeat loans",
             "revenue": "Net revenue (interest and fees received − paid to NBFC)", "losses": "Default losses we bear",
             "cost": "Total cost (losses + collection + ops + platform fee)", "cm": "Contribution margin",
             "book": "Loan-months of balance started (for capital)", "cm_per": "…per disbursed borrower",
             "cum": "Cumulative per disbursed borrower", "dcm": "Discounted per disbursed borrower",
             "pb": "Payback flag"}


def build_lending_first(wb):
    ws = wb.create_sheet("Lending-first")
    ws["A1"] = "Lending-first comparison: a Bueno-style cohort of 1,000 applicants, from founder data"
    ws["A1"].font = TITLE
    ws["A2"] = ("As Bueno ran it: a partner NBFC lent, we paid it a fixed yearly return and bore ALL default losses. "
                "RBI now caps a loan service provider's loss guarantee at 5% of the portfolio, so this exact structure "
                "would need our own NBFC today (see capital row).")
    ws["A2"].font = NOTE
    ws.merge_cells("A2:J2")
    ws["A2"].alignment = WRAP
    ws.row_dimensions[2].height = 30
    ws.column_dimensions["A"].width = 52
    ws.column_dimensions["B"].width = 14
    per_loan = [
        ("Borrowers (applicants × approval)", "borrowers_lf", "=lf_applicants*lf_approval", INR),
        ("Interest and fees per loan, contract (₹)", "lf_interest", "=PMT(lf_irr/12,lf_tenor,-lf_ticket)*lf_tenor-lf_ticket", INR),
        ("Paid to NBFC per loan (₹)", "lf_cof_loan", "=PMT(lf_cof/12,lf_tenor,-lf_ticket)*lf_tenor-lf_ticket", INR),
        ("Average balance as share of loan", "lf_avg_frac",
         "=((1+lf_irr/12)^lf_tenor-((1+lf_irr/12)^lf_tenor-1)/(lf_tenor*lf_irr/12))/((1+lf_irr/12)^lf_tenor-1)", PCT),
        ("Fixed cost per loan: collection + ops + platform fee (₹)", "lf_fixed",
         "=lf_collection+lf_ops_cost+lf_platform_share*lf_platform_fee", INR),
        ("Contribution of a FIRST loan (₹)", "lf_first_cm",
         "=lf_interest*(1-lf_dpd90_first)-lf_cof_loan-lf_dpd90_first*lf_ead*lf_lgd*lf_ticket*lf_risk_share-lf_fixed", INR),
        ("Contribution of a REPEAT loan (₹)", "lf_rep_cm",
         "=lf_interest*(1-lf_dpd90_repeat)-lf_cof_loan-lf_dpd90_repeat*lf_ead*lf_lgd*lf_ticket*lf_risk_share-lf_fixed", INR),
        ("CAC per applicant, fully loaded (₹)", "lf_cac_app", "=lf_cost_per_applicant+lf_underwrite_cost", INR),
        ("CAC per disbursed borrower (₹)", "lf_cac", "=lf_cac_app/lf_approval", INR),
        ("CAC per good borrower (₹) = CAC per applicant ÷ (approval × share who repay)", "lf_cac_good",
         "=lf_cac_app/(lf_approval*(1-lf_dpd90_first))", INR),
    ]
    r = 4
    section(ws, r, "Per-loan economics (scenario from Inputs!C2)", 3)
    for i, (lab, nm, f, fmt) in enumerate(per_loan):
        rr = r + 1 + i
        ws.cell(rr, 1, lab).font = BLACK
        c = ws.cell(rr, 2, f)
        c.number_format, c.font = fmt, BOLD if nm in ("lf_first_cm", "lf_cac") else BLACK
        add_name(wb, nm, f"'Lending-first'!$B${rr}")
    mr = r + len(per_loan) + 3
    ws.cell(mr - 1, 1, "Monthly cohort (month 0 in column C)").font = BOLD
    rowmap = {}
    for i, (k, _) in enumerate(LF):
        rowmap[k] = mr + i
    for k, tmpl in LF:
        rr = rowmap[k]
        ws.cell(rr, 1, LF_LABELS[k]).font = BOLD if k in ("cm",) else BLACK
        for m in range(0, M + 1):
            col = 3 + m
            if k == "t":
                c = ws.cell(rr, col, m)
                c.font, c.fill = HEAD, HEAD_FILL
                continue
            if m == 0:
                ws.cell(rr, col, 0).font = BLUE
                continue
            f = TOKEN.sub(lambda mm: (f"{L(col)}${rowmap['t']}" if mm.group(2) == "t" else
                                      (f"$C${rowmap[mm.group(2)]}:{L(col - 1)}${rowmap[mm.group(2)]}" if mm.group(1) else
                                       f"{L(col - 1) if mm.group(3) else L(col)}{rowmap[mm.group(2)]}")), tmpl)
            c = ws.cell(rr, col, f)
            c.number_format = "0" if k == "pb" else (INR2 if k in ("cm_per", "cum", "dcm") else INR)
    for m in range(0, M + 1):
        ws.column_dimensions[L(3 + m)].width = max(ws.column_dimensions[L(3 + m)].width or 0, 10)
    # outputs
    orow = rowmap["pb"] + 3
    section(ws, orow, "Lending-first outputs (per disbursed borrower)", 3)
    a1, b1 = month_cols(1)
    outs = [
        ("CAC payback (months)", "lf_payback", f'=IF(MIN(D{rowmap["pb"]}:{L(3 + M)}{rowmap["pb"]})=999,"not within 60 months",MIN(D{rowmap["pb"]}:{L(3 + M)}{rowmap["pb"]}))', "0"),
        ("LTV, 36 months (₹, discounted)", "lf_ltv36", f"=SUM(D{rowmap['dcm']}:{L(3 + 36)}{rowmap['dcm']})", INR),
        ("LTV, 60 months (₹, discounted)", "lf_ltv60", f"=SUM(D{rowmap['dcm']}:{L(3 + 60)}{rowmap['dcm']})", INR),
        ("LTV/CAC, 36 months", "lf_ltv36_cac", "=lf_ltv36/lf_cac", MULT),
        ("LTV/CAC, 60 months", "lf_ltv60_cac", "=lf_ltv60/lf_cac", MULT),
        ("Year-1 net revenue per borrower (₹)", "lf_y1_rev", f"=SUM({a1}{rowmap['revenue']}:{b1}{rowmap['revenue']})/borrowers_lf", INR),
        ("Year-1 contribution per borrower (₹)", "lf_y1_cm", f"=SUM({a1}{rowmap['cm']}:{b1}{rowmap['cm']})/borrowers_lf", INR),
        ("Equity locked per ₹1 of yearly net revenue, if run through our own NBFC", "lf_cap_per_rev",
         f"=IFERROR(lf_equity_ratio*SUM({a1}{rowmap['book']}:{b1}{rowmap['book']})/12/SUM({a1}{rowmap['revenue']}:{b1}{rowmap['revenue']}),0)", INR2),
    ]
    for i, (lab, nm, f, fmt) in enumerate(outs):
        rr = orow + 1 + i
        ws.cell(rr, 1, lab).font = BLACK
        c = ws.cell(rr, 2, f)
        c.number_format, c.font = fmt, BOLD
        add_name(wb, nm, f"'Lending-first'!$B${rr}")
    ws.freeze_panes = "C4"


# ---------------------------------------------------------------- Path to $100M
def build_path(wb):
    ws = wb.create_sheet("Path to $100M")
    ws["A1"] = "Path to $100M revenue: savers acquired × revenue per saver by cohort year × product mix"
    ws["A1"].font = TITLE
    ws["A2"] = ("Savers acquired evenly through a year spend half a year in their first cohort year, so calendar year Y "
                "gets 0.5 × v(Y−c) + 0.5 × v(Y−c+1) from the cohort acquired in year c. After cohort year 5, values "
                "decay by (1 − monthly late churn)^12 a year. Volumes are the same in every scenario; the scenario changes the unit economics.")
    ws["A2"].font = NOTE
    ws.merge_cells("A2:L2")
    ws["A2"].alignment = WRAP
    ws.row_dimensions[2].height = 42
    ws.column_dimensions["A"].width = 48
    for i in range(2, 14):
        ws.column_dimensions[L(i)].width = 13
    Y = engine.PATH_YEARS
    plan = read_csv("inputs_path.csv")
    r = 4
    header(ws, r, ["Growth inputs"] + [f"Year {y}" for y in range(1, Y + 1)] + ["Basis"])
    rows = {}
    for i, (k, lab, fmt) in enumerate([("new_activated", "New activated savers", INR),
                                       ("cac_scale", "CAC multiplier as channels saturate", MULT),
                                       ("fixed_opex_cr", "Fixed opex: team, tech, office (₹ crore)", NUM)]):
        rr = r + 1 + i
        rows[k] = rr
        ws.cell(rr, 1, lab).font = BLACK
        for y in range(1, Y + 1):
            c = ws.cell(rr, 1 + y, float(plan[y - 1][k]))
            c.font, c.number_format = BLUE, fmt
        ws.cell(rr, 2 + Y, plan[0]["basis"]).font = NOTE
    # cohort-year curves k = 0..Y
    cr = r + 6
    header(ws, cr, ["Per activated saver, by cohort year k"] + [f"k={k}" for k in range(0, Y + 1)])
    curve_rows = {}
    src = {"rev": ("Revenue (₹)", "y{k}_rev_act"), "cm": ("Contribution (₹)", "y{k}_cm_act"),
           "active": ("Active savers per activated (avg in year)", "y{k}_active_per"),
           "capital": ("Capital locked per activated (₹, avg in year)", "y{k}_cap_act")}
    for i, key in enumerate(("rev", "cm", "active", "capital")):
        rr = cr + 1 + i
        curve_rows[key] = rr
        ws.cell(rr, 1, src[key][0]).font = BLACK
        for k in range(0, Y + 1):
            col = 2 + k
            if k == 0:
                f = "=0"
            elif k <= 5:
                f = "=" + src[key][1].format(k=k)
            else:
                f = f"={L(2 + 5)}{rr}*(1-churn_path)^(12*{k - 5})"
            c = ws.cell(rr, col, f)
            c.font = GREEN if 1 <= k <= 5 else BLACK
            c.number_format = INR2 if key == "active" else INR
    # calendar-year build-up
    blocks = {}
    br = cr + 7
    for key, title in (("rev", "Revenue (₹) by acquisition-year cohort (rows) and calendar year (columns)"),
                       ("cm", "Contribution (₹) by cohort and calendar year"),
                       ("active", "Active savers by cohort and calendar year"),
                       ("capital", "Capital locked (₹) by cohort and calendar year")):
        header(ws, br, [title] + [f"Year {y}" for y in range(1, Y + 1)])
        ws.row_dimensions[br].height = 30
        for c_ in range(1, Y + 1):
            rr = br + c_
            ws.cell(rr, 1, f"Cohort acquired in year {c_}").font = NOTE
            for y in range(1, Y + 1):
                col = 1 + y
                vrow = curve_rows[key]
                rng = f"$B${vrow}:${L(2 + Y)}${vrow}"
                f = (f"=${L(1 + c_)}${rows['new_activated']}*0.5*(INDEX({rng},1,{y - c_ + 1})+INDEX({rng},1,{y - c_ + 2}))"
                     if c_ <= y else 0)
                cell = ws.cell(rr, col, f)
                cell.number_format = INR
        tr = br + Y + 1
        ws.cell(tr, 1, "Total").font = BOLD
        for y in range(1, Y + 1):
            c = ws.cell(tr, 1 + y, f"=SUM({L(1 + y)}{br + 1}:{L(1 + y)}{tr - 1})")
            c.number_format, c.font = INR, BOLD
        blocks[key] = tr
        br = tr + 2
    # summary
    sr = br
    header(ws, sr, ["Summary"] + [f"Year {y}" for y in range(1, Y + 1)])
    lines = [
        ("rev", "Revenue (₹ crore)", lambda c: f"={c}{blocks['rev']}/10000000", NUM),
        ("rev_usd", "Revenue ($ million)", lambda c: f"={c}{blocks['rev']}/usd_inr/1000000", NUM),
        ("active", "Active savers (million, average in year)", lambda c: f"={c}{blocks['active']}/1000000", INR2),
        ("rpa", "Revenue per active saver (₹ per year)", lambda c: f"=IFERROR({c}{blocks['rev']}/{c}{blocks['active']},0)", INR),
        ("cm", "Contribution (₹ crore)", lambda c: f"={c}{blocks['cm']}/10000000", NUM),
        ("cac", "Acquisition spend (₹ crore)", lambda c: f"={c}{rows['new_activated']}*cac_blended*{c}{rows['cac_scale']}/10000000", NUM),
        ("opex", "Fixed opex, plus NBFC overhead if that lever is on (₹ crore)",
         lambda c: f"={c}{rows['fixed_opex_cr']}+IF(nbfc_on=1,nbfc_fixed_cr,0)", NUM),
        ("capital", "Capital locked: guarantee deposits or NBFC equity, incl. ₹10 cr minimum (₹ crore)",
         lambda c: f"=IF(nbfc_on=1,MAX(nbfc_nof_cr,{c}{blocks['capital']}/10000000),{c}{blocks['capital']}/10000000)", NUM),
        ("capinc", "Increase in capital locked (₹ crore)", None, NUM),
        ("cash", "Cash flow (₹ crore)", lambda c: f"={c}{{cm}}-{c}{{cac}}-{c}{{opex}}-{c}{{capinc}}", NUM),
        ("cum", "Cumulative cash (₹ crore)", None, NUM),
        ("need", "Capital needed to reach this year-end (₹ crore)", None, NUM),
        ("hit", "Flag: revenue ≥ $100M (year, else 99)", None, "0"),
    ]
    lrow = {}
    for i, (k, *_r) in enumerate(lines):
        lrow[k] = sr + 1 + i
    for k, lab, fn, fmt in lines:
        rr = lrow[k]
        ws.cell(rr, 1, lab).font = BOLD if k in ("rev_usd", "need") else BLACK
        for y in range(1, Y + 1):
            c = L(1 + y)
            if k == "cum":
                f = f"={c}{lrow['cash']}" if y == 1 else f"={L(y)}{rr}+{c}{lrow['cash']}"
            elif k == "need":
                f = f"=MAX(0,-MIN($B${lrow['cum']}:{c}{lrow['cum']}))"
            elif k == "capinc":
                f = f"={c}{lrow['capital']}" if y == 1 else f"={c}{lrow['capital']}-{L(y)}{lrow['capital']}"
            elif k == "hit":
                f = f"=IF({c}{lrow['rev_usd']}>=100,{y},99)"
            else:
                f = fn(c)
                f = f.replace("{cm}", str(lrow["cm"])).replace("{cac}", str(lrow["cac"])).replace(
                    "{opex}", str(lrow["opex"])).replace("{rev_usd}", str(lrow["rev_usd"])).replace("{capinc}", str(lrow["capinc"]))
            cell = ws.cell(rr, 1 + y, f)
            cell.number_format = fmt
            cell.font = BOLD if k in ("rev_usd", "need") else BLACK
    fr = lrow["hit"] + 2
    ws.cell(fr, 1, "First year revenue reaches $100M").font = BOLD
    c = ws.cell(fr, 2, f'=IF(MIN(B{lrow["hit"]}:{L(1 + Y)}{lrow["hit"]})=99,"not within 10 years",MIN(B{lrow["hit"]}:{L(1 + Y)}{lrow["hit"]}))')
    c.font = BOLD
    add_name(wb, "path_year_100m", f"'Path to $100M'!$B${fr}")
    ws.cell(fr + 1, 1, "Peak capital needed over 10 years (₹ crore)").font = BOLD
    c = ws.cell(fr + 1, 2, f"={L(1 + Y)}{lrow['need']}")
    c.font, c.number_format = BOLD, NUM
    add_name(wb, "path_peak_capital", f"'Path to $100M'!$B${fr + 1}")
    for y in range(1, Y + 1):
        add_name(wb, f"path_rev_usd_y{y}", f"'Path to $100M'!${L(1 + y)}${lrow['rev_usd']}")
        add_name(wb, f"path_active_y{y}", f"'Path to $100M'!${L(1 + y)}${lrow['active']}")
        add_name(wb, f"path_need_y{y}", f"'Path to $100M'!${L(1 + y)}${lrow['need']}")
    ws.freeze_panes = "B5"


# ---------------------------------------------------------------- Outputs
def build_outputs(wb, rowmap, rev, cost, segmap):
    ws = wb.create_sheet("Outputs", 1)
    ws["A1"] = "Outputs: the only numbers the deck quotes"
    ws["A1"].font = TITLE
    ws["A2"] = '="Scenario shown: "&CHOOSE(scenario,"Bear","Base","Bull")&" (switch at Inputs!C2). LTV is on contribution margin, discounted at "&TEXT(disc_rate,"0%")&" a year. CAC is fully loaded, per activated saver."'
    ws["A2"].font = BOLD
    for col, w in zip("ABCDEFGH", [60, 16, 16, 16, 16, 16, 16, 40]):
        ws.column_dimensions[col].width = w
    r = 4
    header(ws, r, ["Metric", "Savings-first", "Lending-first (Bueno-style)", "", "", "", "", "Population / definition"])
    ws.row_dimensions[r].height = 30
    pbr = rowmap["pb"]
    items = [
        ("CAC (₹)", "=cac_blended", "=lf_cac", INR, "Savings: per activated saver. Lending: per disbursed borrower."),
        ("CAC per good borrower (₹)", None, "=lf_cac_good", INR, "Per applicant ÷ (approval × share who repay the first loan)"),
        ("CAC payback (months)", f"=IF(MIN('Cohort total'!D{pbr}:{L(3 + M)}{pbr})=999,\"not within 60 months\",MIN('Cohort total'!D{pbr}:{L(3 + M)}{pbr}))",
         "=lf_payback", "0", "Months until cumulative contribution (undiscounted) covers CAC"),
        ("LTV, 36 months (₹)", f"=SUM('Cohort total'!D{rowmap['dcm']}:{L(3 + 36)}{rowmap['dcm']})", "=lf_ltv36", INR, "Discounted contribution margin"),
        ("LTV, 60 months (₹)", f"=SUM('Cohort total'!D{rowmap['dcm']}:{L(3 + 60)}{rowmap['dcm']})", "=lf_ltv60", INR, "Discounted contribution margin"),
        ("LTV/CAC, 36 months", "=B8/B5", "=lf_ltv36_cac", MULT, ""),
        ("LTV/CAC, 60 months", "=B9/B5", "=lf_ltv60_cac", MULT, ""),
        ("Year-1 contribution per activated saver / per borrower (₹)",
         f"=SUM('Cohort total'!D{rowmap['cm_per']}:O{rowmap['cm_per']})", "=lf_y1_cm", INR, "Undiscounted"),
        ("Capital locked per ₹1 of yearly revenue (₹)",
         f"=IFERROR(SUM('Cohort total'!D{rowmap['cap']}:O{rowmap['cap']})/12/SUM('Cohort total'!D{rowmap['revenue']}:O{rowmap['revenue']}),0)",
         "=lf_cap_per_rev", INR2, "Year 1, average capital locked ÷ revenue. Savings-first: guarantee deposit or NBFC equity (0 with neither lever). Lending-first: equity to hold the book in our own NBFC."),
    ]
    names = ["out_cac", "out_cac_good", "out_payback", "out_ltv36", "out_ltv60", "out_ltv36_cac", "out_ltv60_cac", "out_y1_cm", "out_cap_per_rev"]
    for i, (lab, fs, fl, fmt, pop) in enumerate(items):
        rr = r + 1 + i
        ws.cell(rr, 1, lab).font = BLACK
        if fs:
            c = ws.cell(rr, 2, fs)
            c.number_format, c.font = fmt, Font(name=F, size=10, bold=True, color="008000")
        c = ws.cell(rr, 3, fl)
        c.number_format, c.font = fmt, GREEN
        ws.cell(rr, 8, pop).font = NOTE
        add_name(wb, names[i], f"Outputs!$B${rr}")
    # yearly per active saver
    r = r + len(items) + 3
    ws.cell(r, 1, "Savings-first, per ACTIVE saver per year (₹), by cohort year: stacked by product").font = BOLD
    header(ws, r + 1, ["Revenue line"] + [f"Year {y}" for y in range(1, 6)] + ["", "Population"])
    k = r + 2
    for name, rr_src in rev["per"].items():
        ws.cell(k, 1, name).font = BLACK
        for y in range(1, 6):
            c = ws.cell(k, 1 + y, f"='Revenue lines'!{L(3 + y)}{rr_src}")
            c.number_format, c.font = INR, GREEN
        ws.cell(k, 8, "per active saver, cohort year").font = NOTE
        k += 1
    extra = [("Revenue per active saver", f"'Revenue lines'!{{c}}{rev['per_total_row']}", "rev_pa"),
             ("Variable cost per active saver", f"'Cost to serve'!{{c}}{cost['per_total_row']}", "cost_pa")]
    for lab, tmpl, nm in extra:
        ws.cell(k, 1, lab).font = BOLD
        for y in range(1, 6):
            c = ws.cell(k, 1 + y, "=" + tmpl.format(c=L(3 + y)))
            c.number_format, c.font = INR, Font(name=F, size=10, bold=True, color="008000")
            add_name(wb, f"y{y}_{nm}", f"Outputs!${L(1 + y)}${k}")
        k += 1
    ws.cell(k, 1, "Contribution margin per active saver").font = BOLD
    for y in range(1, 6):
        c = ws.cell(k, 1 + y, f"={L(1 + y)}{k - 2}-{L(1 + y)}{k - 1}")
        c.number_format, c.font = INR, BOLD
        add_name(wb, f"y{y}_cm_pa", f"Outputs!${L(1 + y)}${k}")
    k += 3
    ws.cell(k, 1, "Savings-first, per ACTIVATED saver (the cohort's starting 1,000), by cohort year").font = BOLD
    header(ws, k + 1, ["Metric"] + [f"Year {y}" for y in range(1, 6)])
    for i, (lab, row_key, nm) in enumerate([("Revenue per activated saver (₹)", "revenue", "rev_act"),
                                            ("Contribution per activated saver (₹)", "cm", "cm_act")]):
        rr = k + 2 + i
        ws.cell(rr, 1, lab).font = BLACK
        for y in range(1, 6):
            a, b = month_cols(y)
            c = ws.cell(rr, 1 + y, f"=SUM('Cohort total'!{a}{rowmap[row_key]}:{b}{rowmap[row_key]})/cohort_size")
            c.number_format, c.font = INR, GREEN
            add_name(wb, f"y{y}_{nm}", f"Outputs!${L(1 + y)}${rr}")
    rr = k + 4
    ws.cell(rr, 1, "Capital locked per activated saver, average in year (₹)").font = BLACK
    for y in range(1, 6):
        a, b = month_cols(y)
        c = ws.cell(rr, 1 + y, f"=SUM('Cohort total'!{a}{rowmap['cap']}:{b}{rowmap['cap']})/12/cohort_size")
        c.number_format, c.font = INR2, GREEN
        add_name(wb, f"y{y}_cap_act", f"Outputs!${L(1 + y)}${rr}")
    rr += 1
    ws.cell(rr, 1, "Average active savers per activated saver").font = BLACK
    for y in range(1, 6):
        a, b = month_cols(y)
        c = ws.cell(rr, 1 + y, f"=SUM('Cohort total'!{a}{rowmap['A']}:{b}{rowmap['A']})/12/cohort_size")
        c.number_format, c.font = INR2, GREEN
        add_name(wb, f"y{y}_active_per", f"Outputs!${L(1 + y)}${rr}")
    k = rr + 3
    ws.cell(k, 1, "By segment (per activated saver of that segment, base on the scenario switch)").font = BOLD
    header(ws, k + 1, ["Metric", "Gig", "Non-gig"])
    pbs = segmap["pb"]
    seg_lines = [
        ("CAC (₹)", "cac", lambda sh, sg: f"=cac_{'gig' if sg == 'gig' else 'ng'}", INR),
        ("LTV, 60 months (₹)", "ltv60", lambda sh, sg: f"=SUM('{sh}'!D{segmap['dcm']}:{L(3 + 60)}{segmap['dcm']})", INR),
        ("LTV/CAC, 60 months", "ltv60_cac", None, MULT),
        ("CAC payback (months)", "payback", lambda sh, sg: f'=IF(MIN(\'{sh}\'!D{pbs}:{L(3 + M)}{pbs})=999,"not within 60 months",MIN(\'{sh}\'!D{pbs}:{L(3 + M)}{pbs}))', "0"),
        ("Revenue per active saver, year 2 (₹)", "rev_pa_y2",
         lambda sh, sg: f"=SUM('{sh}'!P{segmap['revenue']}:AA{segmap['revenue']})/(SUM('{sh}'!P{segmap['A']}:AA{segmap['A']})/12)", INR),
        ("Still saving at month 12", "still_m12", lambda sh, sg: f"='{sh}'!{L(3 + 12)}{segmap['S']}", PCT),
    ]
    for i, (lab, key, fn, fmt) in enumerate(seg_lines):
        rr2 = k + 2 + i
        ws.cell(rr2, 1, lab).font = BLACK
        for j, (sg, sh) in enumerate((("gig", "Cohort gig"), ("ng", "Cohort non-gig"))):
            col = 2 + j
            if key == "ltv60_cac":
                f = f"={L(col)}{rr2 - 1}/{L(col)}{k + 2}"
            else:
                f = fn(sh, sg)
            c = ws.cell(rr2, col, f)
            c.number_format, c.font = fmt, GREEN
            add_name(wb, f"seg_{sg}_{key}", f"Outputs!${L(col)}${rr2}")
    k = k + 3 + len(seg_lines)
    ws.cell(k, 1, "Path to $100M (see that tab)").font = BOLD
    for i, (lab, f, fmt) in enumerate([("First year revenue reaches $100M", "=path_year_100m", "0"),
                                       ("Revenue in year 5 ($ million)", "=path_rev_usd_y5", NUM),
                                       ("Revenue in year 10 ($ million)", "=path_rev_usd_y10", NUM),
                                       ("Active savers in year 10 (million)", "=path_active_y10", INR2),
                                       ("Capital needed to reach year 2 (₹ crore)", "=path_need_y2", NUM),
                                       ("Capital needed to reach year 5 (₹ crore)", "=path_need_y5", NUM),
                                       ("Peak capital needed over 10 years (₹ crore)", "=path_peak_capital", NUM)]):
        ws.cell(k + 1 + i, 1, lab).font = BLACK
        c = ws.cell(k + 1 + i, 2, f)
        c.number_format, c.font = fmt, GREEN
    build_story_block(wb, ws, k + 10, cost, segmap)
    ws.freeze_panes = "A4"


COST_SLUG = {"Debits, notices, failed debits": "pay", "Support, tech, streak rewards": "service", "Fraud": "fraud",
             "Loans: our cost": "loans", "Cards: our cost": "cards", "Insurance: our cost": "ins"}


def build_story_block(wb, ws, k, cost, segmap):
    """The story deck's numbers: what a saver costs by line, how many ever borrow, and which lines earn."""
    ws.cell(k, 1, "Story deck: what an active saver costs us per year (₹), by line and cohort year").font = BOLD
    header(ws, k + 1, ["Cost line"] + [f"Year {y}" for y in range(1, 6)] + ["", "Population"])
    r = k + 2
    for name, rr_src in cost["per"].items():
        ws.cell(r, 1, name).font = BLACK
        for y in range(1, 6):
            c = ws.cell(r, 1 + y, f"='Cost to serve'!{L(3 + y)}{rr_src}")
            c.number_format, c.font = INR, GREEN
            add_name(wb, f"y{y}_cost_{COST_SLUG[name]}", f"Outputs!${L(1 + y)}${r}")
        ws.cell(r, 8, "per active saver, cohort year").font = NOTE
        r += 1
    r += 2
    ws.cell(r, 1, "Story deck: how many savers ever borrow, and what each borrower costs to find").font = BOLD
    header(ws, r + 1, ["Metric", "Value", "", "", "", "", "", "Population / definition"])
    both = lambda row, n: "+".join(f"SUM('{sh}'!D{segmap[row]}:{L(3 + n)}{segmap[row]})" for sh in SEG_SHEET.values())
    items = [(f"Activated savers who took a first loan by month {n}", f"=({both('newb', n)})/cohort_size", PCT, f"story_borrow_{n}",
              "first loans ÷ activated savers (both halves)") for n in (12, 24, 60)]
    items.append(("CAC per saver who ever borrows (₹)", f"=cac_blended/B{r + 4}", INR, "story_cac_per_borrower",
                  "CAC per activated saver ÷ share who took a first loan within 60 months"))
    for n_, row, lab in ((3, "r3", "Activated savers who reached loan 3 (part secured) within 60 months"),
                         (5, "r5new", "Activated savers who reached loan 5 (first unsecured) within 60 months")):
        items.append((lab, f"=({both(row, 60)})/cohort_size", PCT, f"story_reach{n_}", "loans on that rung ÷ activated savers (both halves)"))
    at = lambda row, sh, m: f"INDEX('{sh}'!$D${segmap[row]}:${L(3 + M)}${segmap[row]},1,{m})"
    for nm, m, lab in (("story_sec_start", "loan_start", "Secured loan size when loans start (₹, average active saver)"),
                       ("story_sec_m12", "12", "Secured loan size at month 12 (₹, average active saver)")):
        num = "+".join(f"{at('sec', sh, m)}*{at('A', sh, m)}" for sh in SEG_SHEET.values())
        den = "+".join(at("A", sh, m) for sh in SEG_SHEET.values())
        items.append((lab, f"=({num})/({den})", INR, nm, "secured_ltv × fund + FD money per active saver, active-weighted across halves"))
    for slug, row, lab in (("gold", "rev_gold", "digital gold"), ("loans", "rev_loans", "loans"), ("ins", "rev_ins", "insurance")):
        items.append((f"Share of 60-month revenue from {lab}", f"=({both(row, 60)})/({both('revenue', 60)})", PCT,
                      f"story_rev60_{slug}", "cohort revenue over 60 months, undiscounted"))
    for i, (lab, f, fmt, nm, pop) in enumerate(items):
        rr = r + 2 + i
        ws.cell(rr, 1, lab).font = BLACK
        c = ws.cell(rr, 2, f)
        c.number_format, c.font = fmt, GREEN
        ws.cell(rr, 8, pop).font = NOTE
        add_name(wb, nm, f"Outputs!$B${rr}")


# ---------------------------------------------------------------- Sensitivity (static, from engine)
def build_sensitivity(wb):
    ws = wb.create_sheet("Sensitivity")
    ws["A1"] = "Sensitivity: bear / base / bull, and the inputs that move LTV/CAC most"
    ws["A1"].font = TITLE
    ws["A2"] = ("These values are written by engine.py (the same logic as the live sheets). To see any scenario live, "
                "set Inputs!C2; verify.py checks the live workbook reproduces this table for all three scenarios.")
    ws["A2"].font = NOTE
    for col, w in zip("ABCDEFGH", [44, 14, 14, 14, 14, 14, 14, 14]):
        ws.column_dimensions[col].width = w
    header(ws, 4, ["Metric", "Bear", "Base", "Bull"])
    res = {s: engine.run(s) for s in engine.SCENARIOS}
    lfs = {s: engine.lending_first(engine.load_lf(s), res[s][0]["disc_rate"])[1] for s in engine.SCENARIOS}
    metrics = [("CAC per activated saver (₹)", lambda s: res[s][2]["cac"], INR),
               ("CAC payback (months; blank = not within 60)", lambda s: res[s][2]["payback_months"], "0"),
               ("LTV 36 months (₹)", lambda s: res[s][2]["ltv36"], INR),
               ("LTV 60 months (₹)", lambda s: res[s][2]["ltv60"], INR),
               ("LTV/CAC 36 months", lambda s: res[s][2]["ltv36_cac"], MULT),
               ("LTV/CAC 60 months", lambda s: res[s][2]["ltv60_cac"], MULT)] + [
              (f"Revenue per active saver, year {y} (₹)", (lambda y: lambda s: res[s][2][f"y{y}_rev_per_active"])(y), INR) for y in range(1, 6)] + [
              ("Lending-first CAC per borrower (₹)", lambda s: lfs[s]["cac"], INR),
              ("Lending-first LTV/CAC 60 months", lambda s: lfs[s]["ltv60_cac"], MULT)]
    for i, (lab, fn, fmt) in enumerate(metrics):
        rr = 5 + i
        ws.cell(rr, 1, lab).font = BLACK
        for j, s in enumerate(engine.SCENARIOS):
            v = fn(s)
            c = ws.cell(rr, 2 + j, v)
            c.number_format = fmt
    tr = 5 + len(metrics) + 2
    ws.cell(tr, 1, "Tornado: LTV/CAC (60 months) when ONE input moves from its bear to its bull value, all else at base").font = BOLD
    header(ws, tr + 1, ["Input", "Bear value", "Base value", "Bull value", "LTV/CAC at bear", "LTV/CAC at bull", "Swing"])
    for i, row in enumerate(engine.tornado()[:12]):
        rr = tr + 2 + i
        ws.cell(rr, 1, row["input"])
        for j, k in enumerate(["bear_value", "base_value", "bull_value", "metric_at_bear", "metric_at_bull", "swing"]):
            c = ws.cell(rr, 2 + j, row[k])
            c.number_format = MULT if j >= 3 else "General"


# ---------------------------------------------------------------- Levers (static, from levers.py)
def build_levers(wb):
    src = ROOT / "tables" / "levers_results.csv"
    ws = wb.create_sheet("Levers")
    ws["A1"] = "Levers: can a structural change make the base case add up? (daily design, as chosen 30 Sep 2026)"
    ws["A1"].font = TITLE
    ws["A2"] = ("Written by levers.py from the same engine. Levers A-C are switches on Inputs (dlg_on, nbfc_on, gold_on): "
                "set one to 1 and the live sheets reproduce its row (verify.py checks gold, NBFC and guarantee at base). "
                "Lever D (blue-collar) is a set of input changes listed in tables/variants.csv. Own NBFC starts in calendar year 3.")
    ws["A2"].font = NOTE
    ws.merge_cells("A2:L2")
    ws["A2"].alignment = WRAP
    ws.row_dimensions[2].height = 42
    if not src.exists():
        ws["A4"] = "Run levers.py first."
        return
    rows = list(csv.DictReader(open(src, newline="")))
    cols = [("lever", "Lever", None, 30), ("scenario", "Scenario", None, 9), ("cac", "CAC (₹)", INR, 10),
            ("payback", "Payback (months)", "0", 10), ("ltv60_cac", "LTV/CAC, 60 m", MULT, 10),
            ("rev_pa_y2", "Revenue per active saver, yr 2 (₹)", INR, 13), ("cm_pa_y2", "Contribution per active saver, yr 2 (₹)", INR, 13),
            ("capital_per_rev_y1", "Capital locked per ₹1 revenue, yr 1", INR2, 12), ("y10_usd_m", "Revenue in year 10 ($M)", NUM, 11),
            ("y10_active_m", "Active savers, year 10 (M)", INR2, 11), ("first_year_100m", "First year ≥ $100M", "0", 10),
            ("peak_capital_cr", "Peak capital needed, 10 yrs (₹ cr)", INR, 13)]
    header(ws, 4, [c[1] for c in cols], [c[3] for c in cols])
    ws.row_dimensions[4].height = 45
    for i, r in enumerate(rows):
        for j, (k, _, fmt, _) in enumerate(cols, 1):
            v = r[k]
            if k not in ("lever", "scenario"):
                v = float(v) if v not in ("", "None") else None
            c = ws.cell(5 + i, j, v)
            c.font = BOLD if r["scenario"] == "base" else BLACK
            if fmt:
                c.number_format = fmt
    ws.freeze_panes = "C5"


# ---------------------------------------------------------------- Sources
def build_sources(wb):
    ws = wb.create_sheet("Sources")
    ws["A1"] = "Sources: every link, when it was read, and what it supports"
    ws["A1"].font = TITLE
    cols = ["id", "Topic", "Claim", "Value", "Unit", "Population", "As of", "Gross / net", "Source", "URL",
            "Source date", "Accessed", "Verdict", "Notes"]
    header(ws, 3, cols, [16, 16, 50, 14, 14, 28, 11, 10, 30, 40, 11, 11, 12, 50])
    r = 4
    for f in ("market_benchmarks.csv", "regulation_rails.csv", "own_checks.csv", "levers.csv"):
        p = ROOT / "research" / f
        if not p.exists():
            continue
        with open(p, newline="") as fh:
            for row in csv.DictReader(fh):
                vals = [row.get(k, "") for k in ("id", "topic", "claim", "value", "unit", "population", "as_of",
                                                  "gross_or_net", "source_title", "source_url", "source_date",
                                                  "accessed", "verdict", "notes")]
                for i, v in enumerate(vals, 1):
                    c = ws.cell(r, i, v)
                    c.font, c.alignment = BLACK, Alignment(vertical="top", wrap_text=i in (3, 6, 14))
                r += 1
    ws.cell(r + 1, 1, "Founder data (Sandeep Arora, confirmed 2026-09-30): see tables/inputs_founder_bueno.csv").font = NOTE
    ws.freeze_panes = "A4"


def main():
    wb = Workbook()
    build_inputs(wb)
    build_funnel(wb)
    rowmap = build_cohort(wb, "gig")
    build_cohort(wb, "ng")
    tmap = build_total(wb, rowmap)
    rev = build_revenue(wb, rowmap)
    cost = build_costs(wb, rowmap)
    build_lending_first(wb)
    build_path(wb)
    build_outputs(wb, tmap, rev, cost, rowmap)
    build_sensitivity(wb)
    build_levers(wb)
    build_sources(wb)
    import mc_sheets
    extra = mc_sheets.build(wb)
    later = mc_sheets.build_redesign(wb)
    order = ["Inputs", "Funnel & CAC", "Cohort gig", "Cohort non-gig", "Cohort total", "Revenue lines", "Cost to serve", "Outputs", "Lending-first",
             "Sensitivity", *extra, *later, "Levers", "Path to $100M", "Sources"]
    wb._sheets = [wb[n] for n in order]
    wb.save(OUT)
    print(f"wrote {OUT}")
    return rowmap


if __name__ == "__main__":
    main()

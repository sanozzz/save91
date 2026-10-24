"""The 'v4 LTV' tab of the Google Sheet: one saver won -- cost to win, what each product line brings in over 5 and 8 years,
serving cost, LTV/CAC and the payback month -- as LIVE formulas on top of the v4 tabs (v4 Inputs -> v4 Per saver -> v4 Monthly),
plus a waterfall chart and a payback curve. A saver who joins in month 1: each month's per-active line at that month's calendar
factor, exactly as v4 Monthly applies it to every cohort.

Writes tables/v4_ltv_tab_spec.json and, into <out_dir>, the connector payloads:
  ltv_setup.json   addSheet + named ranges (send first)
  ltv_cells_NN.json  {"range", "formulas"} blocks for update_formulas (null = leave the cell alone, so spills stay empty)
  ltv_finish.json  formats + the two charts (send last)
Also prints the numpy-twin values the live sheet must show (checked after the push by reading the tab back).
Usage: python model/v4_ltv_tab.py <out_dir>
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
import v4_toy_check as vt  # noqa: E402

T = ROOT / "tables"
SID, TITLE = 209, "v4 LTV"
R0, R1 = 32, 127                        # monthly block: ages 1-96
R60 = R0 + 59                           # age 60
LOAN_FLAG = [0] * 14 + [1] * 5          # product order of v4 Inputs A155:A173: the last five are loans
GRID = {"startRowIndex": 0, "endRowIndex": 0}


def col(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def ci(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def cells():
    c = {}
    c["A1"] = "v4 LTV: one saver won -- the cost to win them, what each product line brings in, serving cost, LTV/CAC and the month they pay back (LIVE)"
    c["A2"] = ("Every number on this tab recalculates from the blue cells on v4 Inputs, through v4 Per saver and v4 Monthly. A saver who joins in month 1, "
               "each month at that month's calendar take-up and approval factors (as v4 Monthly). Revenue is undiscounted; serving = support, tech for every KYC'd user "
               "reached and payments (debit cost x debits a month); the cost to win includes the 10% contingency; the company's fixed costs (team, office, brand) "
               "are not in this view. Columns G-I: the Python model at the main case, 24 Oct (fixed values).")
    head = ["Line (₹ per saver won)", "Online saver, 5 years", "Doorstep saver, 5 years", "Online saver, 8 years", "Doorstep saver, 8 years", None,
            "Python model: online, 5 years (main case, 24 Oct, fixed)", "Python model: doorstep, 5 years (main case, 24 Oct, fixed)", "Gap, online (sheet - Python)"]
    for j, h in enumerate(head):
        if h:
            c[f"{col(j)}4"] = h
    on = {"fund": "C", "pl": "D", "ol": "E", "ins": "F", "cards": "G", "oth": "H", "rev": "I", "serve": "J", "cum": "K"}
    dr = {"fund": "M", "pl": "N", "ol": "O", "ins": "P", "cards": "Q", "oth": "R", "rev": "S", "serve": "T", "cum": "U"}

    def sm(letter, last):
        return f"SUM({letter}{R0}:{letter}{last})"
    lines = [("Cost to win", None), ("Fund fees", ["fund"]), ("Loans (all referrals: personal, home, property, gold, durables, vehicles)", ["pl", "ol"]),
             ("Insurance", ["ins"]), ("Cards", ["cards"]), ("Other products (recharge, bills, FD, NPS)", ["oth"]), ("Serving (support, tech, payments)", ["serve"])]
    for i, (lab, keys) in enumerate(lines):
        r = 5 + i
        c[f"A{r}"] = lab
        for colx, mp, last in (("B", on, R60), ("C", dr, R60), ("D", on, R1), ("E", dr, R1)):
            if keys is None:
                c[f"{colx}{r}"] = f"=-{'B' if mp is on else 'C'}20"
            elif keys == ["serve"]:
                c[f"{colx}{r}"] = "=-" + sm(mp["serve"], last)
            else:
                c[f"{colx}{r}"] = "=" + "+".join(sm(mp[k], last) for k in keys)
    c["A12"] = "Net after the cost to win"
    for x in "BCDE":
        c[f"{x}12"] = f"=SUM({x}5:{x}11)"
    c["A14"] = "Revenue (fund fees + cross-sell)"
    c["A15"] = "Cross-sell share of revenue"
    c["A16"] = "LTV: revenue less serving"
    c["A17"] = "LTV/CAC (LTV / cost to win)"
    c["A18"] = "Pays back in month (cumulative revenue less serving reaches the cost to win)"
    for x in "BCDE":
        c[f"{x}14"] = f"=SUM({x}6:{x}10)"
        c[f"{x}15"] = f"=IFERROR(SUM({x}7:{x}10)/{x}14,0)"
        c[f"{x}16"] = f"={x}14+{x}11"
        c[f"{x}17"] = f"=IFERROR({x}16/-{x}5,0)"
    c["B18"] = f'=IFERROR(MATCH(TRUE,ARRAYFORMULA(K{R0}:K{R1}>=0),0),"after month 96")'
    c["C18"] = f'=IFERROR(MATCH(TRUE,ARRAYFORMULA(U{R0}:U{R1}>=0),0),"after month 96")'
    c["A20"] = ("Cost to win used, with the 10% contingency: online = cost to win after the seed (v4 Inputs); doorstep = all-in at scale from v4 Monthly, "
                "months 31-96 (agents, leads, offices, kits, churn, KYC)")
    c["B20"] = "=v_cac_rs*(1+v_contingency)"
    c["C20"] = "=IFERROR(SUMPRODUCT((v_month>=31)*v_door_cost)/SUMPRODUCT((v_month>=31)*v_door_won),v_door_cac)*(1+v_contingency)"
    # Python, fixed
    W = {(row["saver"], row["line"]): float(row["Rs over 60 months"]) for row in vt.op.ltv_lines()[0]}   # the main case (vt sets it)
    lv = vt.op.ltv_view(vt.op.saver_inputs(), vt.op.CAC)[2]
    py_lines = ["Cost to win", "Fund fees", "Loans (all referrals)", "Insurance", "Cards", "Other products", "Serving (support + tech)", "Net over 60 months"]
    for i, ln in enumerate(py_lines):
        r = 5 + i
        c[f"G{r}"] = W[("Online saver", ln)]
        c[f"H{r}"] = W[("Doorstep saver", ln)]
        c[f"I{r}"] = f"=B{r}-G{r}"
    c["G14"], c["H14"] = sum(W[("Online saver", k)] for k in py_lines[1:6]), sum(W[("Doorstep saver", k)] for k in py_lines[1:6])
    c["G15"] = sum(W[("Online saver", k)] for k in py_lines[2:6]) / c["G14"]
    c["H15"] = sum(W[("Doorstep saver", k)] for k in py_lines[2:6]) / c["H14"]
    c["G16"], c["H16"] = c["G14"] + W[("Online saver", "Serving (support + tech)")], c["H14"] + W[("Doorstep saver", "Serving (support + tech)")]
    c["G17"], c["H17"] = c["G16"] / -W[("Online saver", "Cost to win")], c["H16"] / -W[("Doorstep saver", "Cost to win")]
    c["G18"] = int(float(lv["pays back in month"]))
    for r in (14, 15, 16, 17, 18):
        c[f"I{r}"] = f"=IFERROR(B{r}-G{r},\"\")"
    c["A21"] = ("Loans count every KYC'd user who came with the saver and opted in (v_loan_reach, end of v4 Inputs; online 2.5, doorstep 1): personal and "
                "business loans and the gold, property and home loans (v4 Inputs column P); the saver alone takes the durable and vehicle loans. Plus the loan-fee ramp (v4 Monthly).")
    c["A22"] = "How to read it: change a blue cell on v4 Inputs (daily amount, still saving at month 12, cost to win, loan apply rate, equity share ...) and the waterfall and the payback curve on the right move."
    # monthly block
    c["A30"] = "Month by month, a saver who joins in month 1 (₹ per saver won; the 5-year totals above sum ages 1-60, the 8-year totals ages 1-96)"
    hdr = ["Month after joining", "Online: still saving", "Online: fund fees", "Online: personal-loan fees", "Online: other loan referrals", "Online: insurance",
           "Online: cards", "Online: other products", "Online: revenue", "Online: serving", "Online: cumulative net after the cost to win",
           "Doorstep: still saving", "Doorstep: fund fees", "Doorstep: personal-loan fees", "Doorstep: other loan referrals", "Doorstep: insurance",
           "Doorstep: cards", "Doorstep: other products", "Doorstep: revenue", "Doorstep: serving", "Doorstep: cumulative net after the cost to win"]
    for j, h in enumerate(hdr):
        c[f"{col(j)}31"] = h
    rng = lambda x: f"{x}{R0}:{x}{R1}"
    xs_tot, xs_loan, xs_ins = "MMULT(v_l_xs1,SEQUENCE(19,1,1,0))", "MMULT(v_l_xs1,v_l_loan)", "MMULT(v_l_xs1,v_pr_ins)"
    xs_reach = "MMULT(v_l_xs1,v_pr_loan)"          # the loans the KYC'd non-savers see too
    for sv, s, L, rch in (("on", "v_s_on", "B", "*v_loan_reach"), ("door", "v_s_door", "L", "")):
        k = ci(L)
        c[f"{col(k)}{R0}"] = f"=ARRAYFORMULA({s})"
        c[f"{col(k + 1)}{R0}"] = f"=ARRAYFORMULA(v_{sv}_trail)"
        c[f"{col(k + 2)}{R0}"] = f"=ARRAYFORMULA(v_{sv}_loanfee*v_f_ta*v_feemult{rch})"
        c[f"{col(k + 3)}{R0}"] = f"=ARRAYFORMULA({s}*({xs_reach}{rch}+{xs_loan}-{xs_reach}))" if rch else f"=ARRAYFORMULA({s}*{xs_loan})"
        c[f"{col(k + 4)}{R0}"] = f"=ARRAYFORMULA({s}*{xs_ins})"
        c[f"{col(k + 5)}{R0}"] = f"=ARRAYFORMULA(v_{sv}_cards*v_f_ta)"
        c[f"{col(k + 6)}{R0}"] = f"=ARRAYFORMULA({s}*({xs_tot}-{xs_loan}-{xs_ins}))"
        c[f"{col(k + 7)}{R0}"] = "=ARRAYFORMULA(" + "+".join(rng(col(k + j)) for j in range(1, 7)) + ")"
        c[f"{col(k + 8)}{R0}"] = f"=ARRAYFORMULA({s}*(v_support+v_tech_per_saver{rch}+v_debit_cost*v_debits_month))"
        cac = "B20" if sv == "on" else "C20"
        c[f"{col(k + 9)}{R0}"] = f"=ARRAYFORMULA(SCAN(-{cac},{rng(col(k + 7))}-{rng(col(k + 8))},LAMBDA(acc,x,acc+x)))"
    c[f"A{R0}"] = "=SEQUENCE(96)"
    # helper: loan flags and the per-active product money of a month-1 joiner
    c["W30"] = "Helper (formulas; the loan flag is an input)"
    c["W31"], c["X31"] = "Product", "Loan product (1 = yes)"
    c[f"W{R0}"] = "=ARRAYFORMULA(v_pr_name)"
    for i, v in enumerate(LOAN_FLAG):
        c[f"X{R0 + i}"] = float(v)
    c["Z30"] = "Per active saver who joined in month 1: each product's money at that month's calendar factor (the v4 Monthly rule for one cohort)"
    c["Z31"] = "=TRANSPOSE(v_pr_name)"
    c[f"Z{R0}"] = ("=ARRAYFORMULA(v_prodmoney*MAKEARRAY(96,19,LAMBDA(m,p,INDEX(v_f_t,MAX(1,m-INDEX(v_pr_lag,p)))))"
                   "+v_prodnow*MAKEARRAY(96,19,LAMBDA(m,p,IF(INDEX(v_pr_house,p)=1,INDEX(v_f_ta,m),INDEX(v_f_t,m))-INDEX(v_f_t,MAX(1,m-INDEX(v_pr_lag,p))))))")
    return c


NAMED = {"v_l_xs1": f"Z{R0}:AR{R1}", "v_l_loan": f"X{R0}:X{R0 + 18}"}


def grid(ref):
    a, b = (ref.split(":") + [ref])[:2]
    import re
    m1, m2 = re.fullmatch(r"([A-Z]+)(\d+)", a), re.fullmatch(r"([A-Z]+)(\d+)", b)
    return {"sheetId": SID, "startRowIndex": int(m1.group(2)) - 1, "endRowIndex": int(m2.group(2)),
            "startColumnIndex": ci(m1.group(1)), "endColumnIndex": ci(m2.group(1)) + 1}


def fmt(ref, pattern):
    return {"repeatCell": {"range": grid(ref), "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": pattern}}},
                           "fields": "userEnteredFormat.numberFormat"}}


def style(ref, **kw):
    f, fields = {}, []
    if "bold" in kw:
        f.setdefault("textFormat", {})["bold"] = True
        fields.append("userEnteredFormat.textFormat.bold")
    if "rgb" in kw:
        r, g, b = kw["rgb"]
        f.setdefault("textFormat", {})["foregroundColorStyle"] = {"rgbColor": {"red": r, "green": g, "blue": b}}
        fields.append("userEnteredFormat.textFormat.foregroundColorStyle")
    if "wrap" in kw:
        f["wrapStrategy"] = "WRAP"
        fields.append("userEnteredFormat.wrapStrategy")
    if "fill" in kw:
        r, g, b = kw["fill"]
        f["backgroundColorStyle"] = {"rgbColor": {"red": r, "green": g, "blue": b}}
        fields.append("userEnteredFormat.backgroundColorStyle")
    return {"repeatCell": {"range": grid(ref), "cell": {"userEnteredFormat": f}, "fields": ",".join(fields)}}


def width(c0, c1, px):
    return {"updateDimensionProperties": {"range": {"sheetId": SID, "dimension": "COLUMNS", "startIndex": ci(c0), "endIndex": ci(c1) + 1},
                                          "properties": {"pixelSize": px}, "fields": "pixelSize"}}


def src(ref):
    return {"sourceRange": {"sources": [grid(ref)]}}


def finish():
    navy, teal, slate, amber = (0.06, 0.2, 0.36), (0.06, 0.62, 0.54), (0.39, 0.45, 0.55), (0.85, 0.47, 0.04)
    reqs = [fmt("B5:E14", "#,##0;-#,##0;0"), fmt("G5:I14", "#,##0;-#,##0;0"), fmt("B15:I15", "0%"), fmt("B16:I16", "#,##0;-#,##0;0"),
            fmt("B17:I17", '0.00"×"'), fmt("B18:I18", "0"), fmt("B20:C20", "#,##0"),
            fmt(f"A{R0}:A{R1}", "0"), fmt(f"B{R0}:B{R1}", "0.000"), fmt(f"L{R0}:L{R1}", "0.000"),
            fmt(f"C{R0}:K{R1}", "#,##0.00"), fmt(f"M{R0}:U{R1}", "#,##0.00"), fmt(f"Z{R0}:AR{R1}", "0.0000"), fmt(f"X{R0}:X{R0 + 18}", "0"),
            style("A1:Z1", bold=True), style("A4:I4", bold=True, wrap=True), style("A12:I12", bold=True), style("A17:I17", bold=True),
            style("A30:AR31", bold=True), style("A31:AR31", wrap=True),
            style("B5:E18", fill=(0.93, 0.97, 0.96)), style(f"X{R0}:X{R0 + 18}", rgb=(0, 0, 1)), style("G5:H18", rgb=(0.45, 0.45, 0.45)),
            width("A", "A", 430), width("B", "E", 130), width("G", "I", 150),
            {"updateSheetProperties": {"properties": {"sheetId": SID, "gridProperties": {"frozenRowCount": 4}}, "fields": "gridProperties.frozenRowCount"}}]
    wf = {"addChart": {"chart": {"spec": {"title": "One online saver won: first 5 years (₹, live)", "waterfallChart": {
        "domain": {"data": src("A5:A11")},
        "series": [{"data": src("B5:B11"), "customSubtotals": [{"subtotalIndex": 6, "label": "Net, 5 years", "dataIsSubtotal": False}],
                    "positiveColumnsStyle": {"color": {"red": navy[0], "green": navy[1], "blue": navy[2]}},
                    "negativeColumnsStyle": {"color": {"red": teal[0], "green": teal[1], "blue": teal[2]}},
                    "subtotalColumnsStyle": {"color": {"red": slate[0], "green": slate[1], "blue": slate[2]}}}],
        "stackedType": "STACKED", "connectorLineStyle": {"width": 1}}},
        "position": {"overlayPosition": {"anchorCell": {"sheetId": SID, "rowIndex": 2, "columnIndex": ci("K")}, "widthPixels": 600, "heightPixels": 340}}}}}
    line = {"addChart": {"chart": {"spec": {"title": "When a saver pays back: cumulative ₹ after the cost to win (live)", "basicChart": {
        "chartType": "LINE", "legendPosition": "BOTTOM_LEGEND", "headerCount": 1,
        "axis": [{"position": "BOTTOM_AXIS", "title": "Months after the saver joins"}, {"position": "LEFT_AXIS", "title": "₹ per saver won"}],
        "domains": [{"domain": src(f"A31:A{R1}")}],
        "series": [{"series": src(f"K31:K{R1}"), "targetAxis": "LEFT_AXIS", "color": {"red": navy[0], "green": navy[1], "blue": navy[2]}},
                   {"series": src(f"U31:U{R1}"), "targetAxis": "LEFT_AXIS", "color": {"red": amber[0], "green": amber[1], "blue": amber[2]}}]}},
        "position": {"overlayPosition": {"anchorCell": {"sheetId": SID, "rowIndex": 2, "columnIndex": ci("S")}, "widthPixels": 600, "heightPixels": 340}}}}}
    return reqs + [wf, line]


def twin():
    """The values the live tab must show at the main case's inputs (numpy twin of every v4 formula)."""
    v = vt.base_inputs()
    ps, m = vt.sheet(v)
    t = np.arange(1, 97)
    lag = ps["pr_lag"]
    Fl = np.stack([m["f_t"][np.maximum(1, t - int(L)) - 1] for L in lag], axis=1)
    Fn = np.where(ps["pr_house"][None, :] == 1, m["f_ta"][:, None], m["f_t"][:, None])
    xs1 = ps["prodmoney"] * Fl + ps["prodnow"] * (Fn - Fl)
    flag = np.array(LOAN_FLAG, float)
    door_cac = float(m["door_cost"][30:].sum() / m["door_won"][30:].sum()) * (1 + v["contingency"])
    out = {}
    for sv, cac, rch in (("on", v["cac_rs"] * (1 + v["contingency"]), v["loan_reach"]), ("door", door_cac, 1.0)):
        s = ps[f"s_{sv}"]
        fund, pl, cards = ps[f"{sv}_trail"], ps[f"{sv}_loanfee"] * m["f_ta"] * m["feemult"] * rch, ps[f"{sv}_cards"] * m["f_ta"]
        ins, ol = s * (xs1 @ ps["pr_ins"]), s * ((xs1 @ ps["pr_loan"]) * rch + xs1 @ flag - xs1 @ ps["pr_loan"])
        oth = s * (xs1.sum(1)) - ins - s * (xs1 @ flag)          # other products: the unscaled loan money comes out
        rev, serve = fund + pl + ol + ins + cards + oth, s * (v["support"] + v["tech_per_saver"] * rch + v["debit_cost"] * v["debits_month"])
        cum = np.cumsum(rev - serve) - cac
        out[sv] = {"cost to win": cac, "revenue 60": rev[:60].sum(), "net 60": cum[59], "LTV/CAC 60": (cum[59] + cac) / cac,
                   "LTV/CAC 96": (cum[-1] + cac) / cac, "pays back": int(np.argmax(cum >= 0)) + 1}
    return out


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    c = cells()
    setup = [{"addSheet": {"properties": {"sheetId": SID, "title": TITLE, "index": 24, "gridProperties": {"rowCount": 140, "columnCount": 48},
                                          "tabColorStyle": {"rgbColor": {"red": 0.06, "green": 0.62, "blue": 0.54}}}}}]
    setup += [{"addNamedRange": {"namedRange": {"name": nm, "range": grid(ref)}}} for nm, ref in NAMED.items()]
    (out / "ltv_setup.json").write_text(json.dumps(setup, ensure_ascii=False))
    # dense blocks for update_formulas
    blocks = [("A1:I22", 1, 22, "A", "I"), (f"A30:U{R0 + 18}", 30, R0 + 18, "A", "U"), (f"W30:Z{R0 + 18}", 30, R0 + 18, "W", "Z")]
    for n, (ref, r0, r1, c0, c1) in enumerate(blocks, 1):
        rows = []
        for r in range(r0, r1 + 1):
            rows.append([c.get(f"{col(j)}{r}") for j in range(ci(c0), ci(c1) + 1)])
        (out / f"ltv_cells_{n:02d}.json").write_text(json.dumps({"range": f"'{TITLE}'!{ref}", "formulas": rows}, ensure_ascii=False))
    placed = {f"{col(j)}{r}" for _ref, r0, r1, c0, c1 in blocks for r in range(r0, r1 + 1) for j in range(ci(c0), ci(c1) + 1)}
    missing = sorted(k for k in c if k not in placed)
    assert not missing, missing
    (out / "ltv_finish.json").write_text(json.dumps(finish(), ensure_ascii=False))
    tw = twin()
    spec = {"title": TITLE, "sheetId": SID, "cells": c, "named_ranges": NAMED, "_expected_twin": tw}
    (T / "v4_ltv_tab_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    print(f"{len(c)} cells, {sum(1 for v in c.values() if isinstance(v, str) and v.startswith('='))} formulas; blocks {[b[0] for b in blocks]}")
    for sv, d in tw.items():
        print(sv, {k: round(x, 3) for k, x in d.items()})


if __name__ == "__main__":
    main()

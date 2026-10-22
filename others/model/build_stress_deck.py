"""The stress-tested story (operator, 16 Oct 2026: "fleet guy salary 20K + 1% of savings; model retention 30-40% bear,
70% best, other assumptions; post that ask an agent to synthesize the story (be very very precise)").

Titles, kickers and captions are read from story/storyline_2026-10-16.csv (written by the synthesis agent; every cited
number verified against its table). Two pages get the three numbers the agent could not source, now computed in
model/scenarios.py (tables/scn_salary_breakeven.csv, scn_salary_summary.csv): page 10 and appendix A11.
Pictures draw only from tables/scn_*.csv, story_*.csv and research/. Writes brief/qr_moat/stress_deck.html and
Offline_model_stress_test.pdf.
"""
import csv
import re
import subprocess
from pathlib import Path

import build_qr_visual as V
import build_agent3_slides as A3
import build_offline_deck as OD
from build_agent_slides import inr, pct

ROOT = Path(__file__).resolve().parent.parent
T, R = ROOT / "tables", ROOT / "research"
PDF = ROOT / "Offline_model_stress_test.pdf"
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD
APP = "#7a8796"
SL = {r["page"]: r for r in csv.DictReader((ROOT / "story" / "storyline_2026-10-16.csv").open())}


def rows(name):
    return list(csv.DictReader((T / name).open()))


RET = rows("scn_retention.csv")
ONE_S = rows("scn_oneway_salary.csv")
ONE_P = rows("scn_oneway.csv")
COMB = {r["case"]: r for r in rows("scn_combined.csv")}
COMB_S = {r["case"]: r for r in rows("scn_combined_salary.csv")}
BE = {float(r["r12"]): r for r in rows("scn_breakeven.csv")}
CUST = {r["channel"]: r for r in rows("scn_customer.csv")}
SAL = {float(r["r12"]): r for r in rows("scn_salary_summary.csv")}
SBE = {r["key"]: float(r["value"]) for r in rows("scn_salary_breakeven.csv")}
SU = {r["channel"]: r for r in rows("story_unit.csv")}
PT = {r["key"]: float(r["value"]) for r in rows("story_paytm.csv")}
INP = rows("scn_inputs.csv")
R12S = (0.3, 0.4, 0.55, 0.7)


def ret(pay, r12, col):
    return float(next(r for r in RET if r["pay"] == pay and abs(float(r["r12"]) - r12) < 1e-9)[col])


def lakh(x, d=2):
    return ("−" if x < 0 else "") + f"₹{abs(x) / 1e5:.{d}f} lakh"


ONLINE_CAC = float(SU["online"]["cost_to_win"])
ONLINE_KEPT = float(SU["online"]["cost_per_saver_still_saving_m12"])
ONLINE_R12 = float(SU["online"]["still_saving_m12"])
CAC = ret("none", 0.55, "cust_cost_to_win")


def hbars(items, x0, x1, vmax, y0=30, gap=44, h=26, fmt=inr, label_w=None):
    """Horizontal bars: items = (label, value, colour). Bars start at x0; negative values drawn leftwards from a zero line."""
    s = []
    X = lambda v: x0 + (x1 - x0) * v / vmax
    for i, (lab, v, col) in enumerate(items):
        y = y0 + i * gap
        s.append(V.text(x0 - 12, y + h - 8, lab, 13, 700, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y}" width="{max(X(v) - x0, 2)}" height="{h}" rx="5" fill="{col}"/>')
        s.append(V.text(X(v) + 8, y + h - 8, fmt(v), 14, 800, col))
    return "".join(s)


# ---------- main pictures ----------
def p2():
    cards = [("H1", "Win him for less", "person", inr(CAC) + " a saver", "₹20,000 a month ÷ 83 sign-ups a month", f"online: {inr(ONLINE_CAC)}"),
             ("H2", "Keep him saving with the visit", "hands", f"{SBE['breakeven_r12_salary_1pct_fee'] * 100:.0f}+ of 100",
              "still saving after a year: where a salaried agent breaks even", f"online: {ONLINE_R12 * 100:.0f} of 100"),
             ("H3", "Earn enough to pay for him", "bank", pct(ret("none", 0.55, "tot_covered")),
              "of his salary paid by his savers over 3 years, at 55 in 100 still saving", "online: never earns back its cost")]
    s = []
    for i, (h, t, ic, big, sub, vs) in enumerate(cards):
        x = i * 300
        s.append(f'<rect x="{x}" y="0" width="282" height="300" rx="18" fill="{V.PAPER}"/><rect x="{x}" y="0" width="282" height="8" rx="4" fill="{US}"/>')
        s.append(f'<circle cx="{x + 36}" cy="46" r="20" fill="{US}"/>' + V.text(x + 36, 52, h, 14, 800, "#fff", "middle"))
        s.append(V.icon(ic, x + 212, 24, 48, US))
        s.append(V.text(x + 20, 106, t, 17, 800, INK))
        s.append(V.text(x + 20, 178, big, 30, 800, US))
        words, line, out = sub.split(), "", []
        for w in words:
            if len(line) + len(w) > 36:
                out.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        out.append(line)
        for k, ln in enumerate(out):
            s.append(V.text(x + 20, 204 + k * 16, ln, 12, 400, MUTED))
        s.append(f'<rect x="{x + 20}" y="258" width="242" height="28" rx="14" fill="{V.TINT["bad"]}"/>' + V.text(x + 141, 277, vs, 12.5, 700, BAD, "middle"))
    return V.svg(882, 304, "".join(s))


def p3():
    iv = OD.IV
    facts = [("coin", f"Saves ₹{iv['IV-03'].replace('Rs ', '').replace(' to ', '–')} a day, in cash, with a janta agent"),
             ("phone", f"{iv['IV-06'].replace(' or ', '–')} in 10 have UPI, yet {iv['IV-07'].replace(' or more', '+')} of every ₹100 is cash: “{iv['IV-08'].lower()}”"),
             ("bank", "Asks his agent about loans and insurance"),
             ("hands", f"6–10 join and 6–10 leave a month on a book of {iv['IV-01'].replace(' customers', '').replace(' to ', '–')}")]
    s = []
    for i, (ic, t) in enumerate(facts):
        y = 10 + i * 66
        s.append(V.icon(ic, 0, y, 36, US))
        s.append(V.text(48, y + 24, t, 14, 600, INK))
    for j, (lab, kept, col) in enumerate((("One janta agent's book", round(float(SU["street"]["still_saving_m12"]) * 100), US),
                                          ("An app", round(ONLINE_R12 * 100), APP))):
        x = 520 + j * 190
        s.append(V.text(x, 14, lab, 13, 800, col))
        s.append(OD.SD.dots(x, 26, kept, col, 12, 4))
        s.append(V.text(x, 204, f"{kept} of 100", 22, 800, col))
        s.append(V.text(x, 222, "still saving after a year", 11.5, 400, MUTED))
    return V.svg(900, 262, "".join(s))


def p4():
    svg = OD.p_loop()
    svg = svg.replace(f"KYC and a savings mandate: {inr(float(SU['street']['cost_to_win']))}", f"KYC and a savings mandate: {inr(CAC)}")
    return svg.replace(f"missed-debit follow-ups, the switch to UPI, loan pre-checks: about {inr(OD.CUT)} a year of his work",
                       "missed-debit follow-ups, the switch to UPI, loan pre-checks; their cost is not yet in these numbers")


def p5():
    items = [("Online, an app", ONLINE_KEPT, APP)] + [(f"Street, {int(r * 100)} of 100 still saving", CAC / r, US) for r in R12S]
    s = [V.text(0, 14, "WHAT EACH SAVER STILL SAVING AFTER A YEAR COSTS TO WIN", 12.5, 700, US), hbars(items, 300, 800, 2200, y0=34)]
    x770 = 300 + 500 * (186 / ONLINE_R12) / 2200
    s.append(f'<line x1="{x770}" y1="28" x2="{x770}" y2="236" stroke="{APP}" stroke-width="2" stroke-dasharray="4 3"/>')
    s.append(V.text(x770, 252, f"dashed line: the cheapest online estimate, {inr(186 / ONLINE_R12)} per saver kept", 11.5, 700, APP, "middle"))
    return V.svg(900, 262, "".join(s))


def p6():
    head = [("speaker", THEM, "Paytm"), ("person", US, "Us, salaried street agent")]
    th = "".join(f'<th><div class="ph">{V.svg(34, 34, V.icon(ic, 0, 0, 32, c))}<span style="color:{c}">{t}</span></div></th>' for ic, c, t in head)
    rws = [("Round 1", "Win him", f"up to ~{inr(PT['paytm_cost_to_win_upto'])} a device (an upper bound)", f"{inr(CAC)} a saver", "good",
            f"Us, up to {PT['paytm_cost_to_win_upto'] / CAC:.1f}× cheaper"),
           ("Round 2", "Keep him", "a box on the counter", f"the visit; we need {SBE['breakeven_r12_salary_1pct_fee'] * 100:.0f}+ of 100 still saving", "warn", "Open: the pilot decides"),
           ("Round 3", "Earn from him", f"{inr(PT['paytm_rent_a_year'])} a year rent; {inr(PT['paytm_fee_per_loan_low'])}+ a loan",
            f"{inr(PT['our_income_per_saver_year'])} a year; {inr(PT['our_fee_per_loan'])} a loan", "bad", f"Paytm, {PT['rent_vs_our_income']:.1f}× more a year")]
    mark = {"good": "✓", "warn": "?", "bad": "✕"}
    body = "".join(f'<tr><td class="rl"><span class="rn">{a}</span><br>{b}</td><td>{c}</td><td class="us">{d}</td><td><span class="chip {k}"><span>{mark[k]}</span>{e}</span></td></tr>'
                   for a, b, c, d, k, e in rws)
    return (f'<div class="stack"><table class="ptab score"><colgroup><col style="width:16%"><col style="width:30%"><col style="width:30%"><col style="width:24%"></colgroup>'
            f'<tr><th></th>{th}<th>Who is ahead</th></tr>{body}</table></div>')


def p7():
    vals = [(f"{int(r * 100)} of 100 still saving", ret("collected", r, "tot_result")) for r in R12S] + [("Everything goes our way", float(COMB["All good"]["tot_result"]))]
    w, x0, x1 = 900, 260, 860
    vmin = -2950000
    X = lambda v: x0 + (x1 - x0) * v / vmin
    s = [V.text(0, 14, "ONE AGENT, 3 YEARS, ON ₹20,000 A MONTH + 1% OF WHAT HE COLLECTS", 12.5, 700, US),
         f'<line x1="{x0}" y1="28" x2="{x0}" y2="250" stroke="{INK}" stroke-width="1.5"/>', V.text(x0, 264, "₹0", 11, 400, MUTED, "middle")]
    for i, (lab, v) in enumerate(vals):
        y = 36 + i * 44
        s.append(V.text(x0 - 12, y + 18, lab, 13, 700, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y}" width="{X(v) - x0}" height="26" rx="5" fill="{BAD}" opacity="{0.55 + 0.1 * i}"/>')
        s.append(V.text(X(v) + 8, y + 18, lakh(v), 14, 800, BAD))
    return V.svg(w, 270, "".join(s))


def p8():
    comm = float(CUST["street_55"]["commission_per_saver_year"])
    inc = float(CUST["street_55"]["income_per_saver_year"])
    bal = ret("balance", 0.55, "cust_commission_per_saver_year")
    base, top, w = 250, 30, 900
    Y = lambda v: base - (base - top) * v / 900
    s = [V.text(0, 14, "ONE SAVER, ONE YEAR (₹350 A DAY, 55 OF 100 STILL SAVING)", 12.5, 700, US),
         f'<line x1="40" y1="{base}" x2="620" y2="{base}" stroke="{INK}" stroke-width="1.2"/>']
    for x, v, col, lab in ((90, comm, BAD, "the agent's 1% of collections"), (330, inc, GOOD, "what the saver earns us")):
        s.append(f'<rect x="{x}" y="{Y(v)}" width="150" height="{base - Y(v)}" rx="6" fill="{col}"/>')
        s.append(V.text(x + 75, Y(v) - 10, inr(v), 24, 800, col, "middle"))
        s.append(V.text(x + 75, base + 22, lab, 13, 700, INK, "middle"))
    s.append(f'<line x1="84" y1="{Y(bal)}" x2="246" y2="{Y(bal)}" stroke="#fff" stroke-width="2.5" stroke-dasharray="6 4"/>')
    s.append(V.text(165, Y(bal) - 22, f"{inr(bal)} if it means", 11.5, 700, "#fff", "middle"))
    s.append(V.text(165, Y(bal) - 8, "1% a year of balance", 11.5, 700, "#fff", "middle"))
    s.append(f'<rect x="660" y="60" width="240" height="140" rx="14" fill="{V.TINT["bad"]}"/>')
    s.append(V.text(780, 120, f"{comm / inc:.1f}×", 40, 800, BAD, "middle"))
    s.append(V.text(780, 150, "more going out", 14, 700, BAD, "middle"))
    s.append(V.text(780, 168, "than coming in", 14, 700, BAD, "middle"))
    return V.svg(w, 280, "".join(s))


def p9():
    items = [(f"{int(r * 100)} of 100 still saving", float(BE[r]["max_commission_on_collections"]) * 100, US) for r in R12S]
    items.append(("Everything goes our way", float(COMB["All good"]["max_commission_collected"]) * 100, GOOD))
    x0, x1, vmax = 300, 820, 1.1
    s = [V.text(0, 14, "THE MOST COMMISSION ON COLLECTIONS THE BUSINESS CAN PAY, ON TOP OF ₹20,000 A MONTH", 12.5, 700, US)]
    X = lambda v: x0 + (x1 - x0) * v / vmax
    s.append(f'<line x1="{X(1)}" y1="28" x2="{X(1)}" y2="252" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    s.append(V.text(X(1), 268, "the proposed 1%", 12.5, 800, BAD, "middle"))
    s.append(hbars(items, x0, x1, vmax, y0=34, fmt=lambda v: f"{v:.2f}%" if v > 0 else "nothing"))
    return V.svg(900, 276, "".join(s))


def p10():
    w, x0, x1, y0, y1 = 900, 80, 600, 30, 250
    X = lambda r: x0 + (x1 - x0) * (r - 0.3) / 0.4
    Y = lambda v: y0 + (y1 - y0) * (600000 - v) / (600000 + 2600000)
    s = [V.text(0, 14, "ONE AGENT'S 3-YEAR RESULT, BY HOW MANY ARE STILL SAVING AFTER A YEAR", 12.5, 700, US)]
    for v in (500000, 0, -1000000, -2000000):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}" stroke-width="{1.4 if v == 0 else 1}"/>')
        s.append(V.text(x0 - 8, Y(v) + 4, lakh(v, 0) if v else "₹0", 11, 400, MUTED, "end"))
    for r in R12S:
        s.append(V.text(X(r), y1 + 20, f"{int(r * 100)} of 100", 12, 400, MUTED, "middle"))
    lines = (("none", GOOD, "salary only"), ("balance", "#b7835a", "1% a year of his balance"), ("collected", BAD, "1% of what he collects"))
    for pay, col, lab in lines:
        pts = [(r, ret(pay, r, "tot_result")) for r in R12S]
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(r):.1f},{Y(v):.1f}" for i, (r, v) in enumerate(pts))
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.5"/>')
        for r, v in pts:
            s.append(f'<circle cx="{X(r)}" cy="{Y(v)}" r="5" fill="{col}" stroke="#fff" stroke-width="2"/>')
        r, v = pts[-1]
        s.append(V.text(X(r) + 12, Y(v) + 5, f"{lab}: {lakh(v)}", 12.5, 800, col))
    be = SBE["breakeven_r12_salary_1pct_fee"]
    s.append(f'<circle cx="{X(be)}" cy="{Y(0)}" r="7" fill="#fff" stroke="{GOOD}" stroke-width="3"/>')
    s.append(V.text(X(be), Y(0) - 14, f"breaks even at {be * 100:.1f} of 100", 12.5, 800, GOOD, "middle"))
    return V.svg(w, 276, "".join(s))


def p11():
    nice = {"other": "Insurance and other products a saver (₹8 → ₹259 a year)", "signups": "Sign-ups a year (750 → 1,250)",
            "r12": "Still saving after a year (30 → 70 of 100)", "loan_rate": "Loans taken (0.45 → 9.8 per 100 a year)",
            "daily": "Daily amount (₹200 → ₹500)", "trail": "Fund commission (0.20% → 0.50%)", "card_fee": "Card fee (₹500 → ₹2,000, unverified)",
            "clawback": "Loan fees taken back (5% → 0%)"}
    base = float(ONE_S[0]["base_result"])
    x0, x1 = 420, 880
    lo_all = min(min(float(r["result_at_low"]), float(r["result_at_high"])) for r in ONE_S)
    hi_all = max(max(float(r["result_at_low"]), float(r["result_at_high"])) for r in ONE_S)
    X = lambda v: x0 + (x1 - x0) * (v - lo_all) / (hi_all - lo_all)
    s = [V.text(0, 14, "ONE AGENT, 3 YEARS, SALARY ONLY: EACH ASSUMPTION MOVED ALONE FROM THE MIDDLE CASE", 12.5, 700, US)]
    s.append(f'<line x1="{X(base)}" y1="24" x2="{X(base)}" y2="{30 + 31 * len(ONE_S)}" stroke="{INK}" stroke-width="1.5"/>')
    s.append(V.text(X(base), 34 + 31 * len(ONE_S) + 10, f"middle case {lakh(base)}", 11.5, 700, INK, "middle"))
    s.append(f'<line x1="{X(0)}" y1="24" x2="{X(0)}" y2="{30 + 31 * len(ONE_S)}" stroke="{BAD}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    for i, r in enumerate(ONE_S):
        y = 30 + i * 31
        a, b = sorted((float(r["result_at_low"]), float(r["result_at_high"])))
        s.append(V.text(x0 - 10, y + 15, nice[r["input"]], 11.5, 600, INK, "end"))
        if a < 0:
            s.append(f'<rect x="{X(a)}" y="{y + 3}" width="{X(min(b, 0)) - X(a)}" height="18" rx="3" fill="{BAD}"/>')
        if b > 0:
            s.append(f'<rect x="{X(max(a, 0))}" y="{y + 3}" width="{X(b) - X(max(a, 0))}" height="18" rx="3" fill="{GOOD}"/>')
    return V.svg(900, 70 + 31 * len(ONE_S), "".join(s))


def p12():
    lo_sign = next(r for r in ONE_S if r["input"] == "signups")
    lo_other = next(r for r in ONE_S if r["input"] == "other")
    be = SBE["breakeven_r12_salary_1pct_fee"]
    marks = [("Months 1–3", "Sign-ups", "about 83 a month (1,000 a year)", f"below 62 a month: 3 years lose {inr(-float(lo_sign['result_at_low']))}"),
             ("From month 7", "Insurance and other products", "about ₹63 a saver a year", f"at ₹8: 3 years lose {inr(-float(lo_other['result_at_low']))}"),
             ("Month 12", "Still saving after a year", f"55 or more of 100 (+{inr(ret('none', 0.55, 'tot_result'))} over 3 years)",
              f"below {be * 100:.0f} of 100: he does not pay for himself")]
    s = [f'<line x1="40" y1="60" x2="860" y2="60" stroke="{US}" stroke-width="4"/>']
    for i, (when, what, ok, stop) in enumerate(marks):
        x = 40 + i * 410
        s.append(f'<circle cx="{x}" cy="60" r="14" fill="{US}"/>' + V.text(x, 66, str(i + 1), 14, 800, "#fff", "middle"))
        s.append(V.text(x, 30, when, 15, 800, US, "middle"))
        bx = max(0, min(x - 135, 630))
        s.append(f'<rect x="{bx}" y="90" width="270" height="170" rx="14" fill="{V.PAPER}"/>')
        s.append(V.text(bx + 14, 120, what, 15.5, 800, INK))
        s.append(V.badge(bx + 14, 156, "good", "pass", 13, "start") + V.text(bx + 76, 158, ok if len(ok) < 30 else ok[:ok.rfind(" ", 0, 30)], 12, 600, GOOD))
        if len(ok) >= 30:
            s.append(V.text(bx + 76, 174, ok[ok.rfind(" ", 0, 30) + 1:], 12, 600, GOOD))
        s.append(V.badge(bx + 14, 214, "bad", "stop", 13, "start") + V.text(bx + 76, 216, stop if len(stop) < 30 else stop[:stop.rfind(" ", 0, 30)], 12, 600, BAD))
        if len(stop) >= 30:
            s.append(V.text(bx + 76, 232, stop[stop.rfind(" ", 0, 30) + 1:], 12, 600, BAD))
    return V.svg(900, 266, "".join(s))


# ---------- appendix tables ----------
NICE = {"daily": "Daily amount a saver puts in", "signups": "Sign-ups per agent a year", "trail": "Fund commission a year, on the balance",
        "other": "Insurance and other products, a saver a year", "card_fee": "Card fee (5% of sign-ups get a card)",
        "loan_rate": "Loans per proven saver a year", "clawback": "Loan fees taken back", "r12": "Still saving after a year",
        "pay: no commission": "Pay: salary only (no commission)", "pay: 1% a year of balance": "Pay: 1% a year of balance"}


def fmtv(k, v):
    if v in ("", None):
        return ""
    try:
        x = float(v)
    except ValueError:
        return v
    if k == "daily" or k == "card_fee" or k == "other":
        return inr(x)
    if k == "signups":
        return f"{x:,.0f}"
    if k in ("trail", "clawback", "loan_rate", "r12"):
        return f"{x * 100:.2f}%".replace(".00%", "%")
    return f"{x:,.2f}"


def table(head, body, widths, text_cols=()):
    cg = "".join(f'<col style="width:{w}%">' for w in widths)
    cls = lambda i: "" if i == 0 or i in text_cols else "n"
    th = "".join(f'<th class="{cls(i)}">{h}</th>' for i, h in enumerate(head))
    tb = "".join("<tr>" + "".join(f'<td class="{cls(i)}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in body)
    return f'<table class="tbl at2"><colgroup>{cg}</colgroup><tr>{th}</tr>{tb}</table>'


def a1():
    body = [[NICE.get(r["input"], r["input"].capitalize()), fmtv(r["input"], r["low"]), fmtv(r["input"], r["middle"]), fmtv(r["input"], r["high"]),
             re.sub(r"Rs (?=\d)", "₹", r["basis"]).replace("Rs a day", "rupees a day").replace("Rs per", "rupees per")] for r in INP]
    return table(["Input", "Low", "Middle", "High", "Where it comes from"], body, [24, 12, 16, 12, 36], text_cols=(4,))


def a2():
    body = []
    for pay, lab in (("collected", "1% of collections"), ("balance", "1% a year of balance"), ("none", "salary only")):
        for r in R12S:
            body.append([f"{lab}, {int(r * 100)} of 100", *(inr(ret(pay, r, f"y{y}_result")) for y in (1, 2, 3)), inr(ret(pay, r, "tot_result"))])
    return table(["Pay, still saving after a year", "Year 1", "Year 2", "Year 3", "3 years"], body, [40, 15, 15, 15, 15])


def a3():
    body = [["Online, an app", inr(float(CUST["online"]["cost_to_win"])), inr(float(CUST["online"]["income"])), "₹0", inr(float(CUST["online"]["net"]))]]
    for r in R12S:
        body.append([f"Street, salary only, {int(r * 100)} of 100", inr(ret("none", r, "cust_cost_to_win")), inr(ret("none", r, "cust_income")), "₹0", inr(ret("none", r, "cust_net"))])
    for r in R12S:
        c = CUST[f"street_{int(r * 100)}"]
        body.append([f"Street, 1% of collections, {int(r * 100)} of 100", inr(float(c["cost_to_win"])), inr(float(c["income"])), inr(float(c["commission"])), inr(float(c["net"]))])
    return table(["Per saver won, his first 3 years", "Cost to win", "Earns us", "Commission", "Net"], body, [40, 15, 15, 15, 15])


def a4():
    body = [[NICE.get(r["input"], r["input"]), fmtv(r["input"], r["low_value"]), fmtv(r["input"], r["high_value"]),
             inr(float(r["result_at_low"])), inr(float(r["result_at_high"]))] for r in ONE_P]
    return table(["Input (proposed pay, 55 of 100)", "Low", "High", "3 years at low", "3 years at high"], body, [34, 12, 12, 21, 21])


def a5():
    body = []
    for case in COMB:
        body.append([case, inr(float(COMB_S[case]["tot_result"])), pct(float(COMB_S[case]["tot_covered"])), inr(float(COMB[case]["tot_result"])), pct(float(COMB[case]["tot_covered"]))])
    return table(["Case", "Salary only: 3 years", "covered", "Proposed pay: 3 years", "covered"], body, [32, 18, 14, 22, 14])


def a6():
    body = [[f"{int(r * 100)} of 100", inr(ret("balance", r, "tot_result")), pct(ret("balance", r, "tot_covered")),
             f"{float(BE[r]['max_commission_on_balance']) * 100:.3f}% a year"] for r in R12S]
    return table(["Still saving after a year", "3 years on 1% of balance", "covered", "Most we can afford on balance"], body, [28, 26, 16, 30])


def a7():
    keys = (("tot_fund", "Fund commission"), ("tot_cards", "Credit cards (fee unverified)"), ("tot_other", "Insurance and other products"), ("tot_loans", "Loan fees"))
    total = ret("none", 0.55, "tot_income")
    body = [[lab, inr(ret("none", 0.55, k)), pct(ret("none", 0.55, k) / total, 1)] for k, lab in keys]
    body.append(["<b>Total, 3 years</b>", f"<b>{inr(total)}</b>", "<b>100%</b>"])
    return table(["Where one agent's income comes from (55 of 100, salary only)", "3 years", "share"], body, [56, 22, 22])


def a10():
    body = [[r["question"], r["answer"]] for r in csv.DictReader((R / "interview_arvinder_2026-10-15.csv").open())]
    return table(["Question", "Arvinder's answer (15 Oct 2026)"], body, [40, 60])


def a11():
    body = [[f"{int(r * 100)} of 100", inr(float(SAL[r]["result_1pct_fee"])), pct(float(SAL[r]["covered_1pct_fee"])),
             inr(float(SAL[r]["result_paytm_fee"])), pct(float(SAL[r]["covered_paytm_fee"])), f"{float(SAL[r]['upi_needed_end_y3']) * 100:.0f}%"] for r in R12S]
    tb = table(["Still saving after a year", "Salary, 1% loan fee", "covered", "Salary, Paytm-like 4.5% fee", "covered", "Must pay by UPI, year 3"],
               body, [22, 16, 11, 20, 11, 20])
    note = (f'<div class="tn">Break-even: {SBE["breakeven_r12_salary_1pct_fee"] * 100:.1f} of 100 still saving at a 1% loan fee; '
            f'{SBE["breakeven_r12_salary_paytm_fee"] * 100:.1f} of 100 at a Paytm-like 4.5% fee, earned by collecting instalments on the visit and sharing first losses '
            f'(Paytm earns 4.5–5% a loan, SE-05; RBI caps first-loss cover at 5%, SE-04). Still not in any number: tele-sales, the AI agent, the office, KYC.</div>')
    return tb + note


def a12():
    body = [["Agent cost", "₹4 lakh a year, flat", "₹20,000 a month (+1% of collections tested)"],
            ["Cost to win a saver", inr(float(SU["street"]["cost_to_win"])), inr(CAC)],
            ["Retention", "one case: 72 of 100 (janta book)", "30, 40, 55, 70 of 100"],
            ["Payback", f"month {SU['street']['payback_month']} (14 with a Paytm-like fee)", "replaced by the agent's 3-year result on each pay"]]
    return table(["", "Last deck", "This deck"], body, [24, 36, 40])


# ---------- assembly ----------
def sources(page_id):
    files = sorted(set(re.findall(r"((?:tables|research|story)/[\w\-.]+\.csv)", SL[page_id]["numbers"] + " " + SL[page_id]["appendix_refs"])))
    return "Sources: " + ", ".join(files) + ". Built by model/scenarios.py and model/build_stress_deck.py; story text from story/storyline_2026-10-16.csv."


def page(pid, label, total, body, title=None, caption=None, extra=""):
    r = SL[pid]
    t = title or r["title"]
    c = caption or r["caption"]
    return (f'<section class="slide"><div class="kick"><span class="pg">{label} / {total}</span>{r["kicker"]}</div><h1>{t}</h1>'
            f'<div class="vis">{body}</div><div class="cap">{c}</div><div class="foot">{sources(pid)}{extra}</div></section>')


def build():
    be, bep = SBE["breakeven_r12_salary_1pct_fee"], SBE["breakeven_r12_salary_paytm_fee"]
    main = [("1", OD.p_problem()), ("2", p2()), ("3", p3()), ("4", p4()), ("5", p5()), ("6", p6()), ("7", p7()), ("8", p8()), ("9", p9()), ("10", p10()), ("11", p11()), ("12", p12())]
    titles = {"10": (f"On salary alone, retention decides: he breaks even at {be * 100:.1f} of 100 still saving after a year. The bear case (30–40) loses up to "
                     f"{lakh(-ret('none', 0.3, 'tot_result'))}; the best case (70, from one interview) makes {lakh(ret('none', 0.7, 'tot_result'))}."),
              }
    caps = {"10": (f"Better retention makes both 1% pays worse and salary pay better. With a Paytm-like 4.5% loan fee the break-even falls to {bep * 100:.1f} of 100, "
                   "inside the bear case (appendix A11).")}
    pages = [page(pid, pid, 12, body, titles.get(pid), caps.get(pid)) for pid, body in main]
    appx = {"A1": a1(), "A2": a2(), "A3": a3(), "A4": a4(), "A5": a5(), "A6": a6(), "A7": a7(), "A8": OD.SD.s_paytm(), "A9": OD.p_problem(),
            "A10": a10(), "A11": a11(), "A12": a12()}
    a11_title = (f"What the stress test leaves out, now partly run: a Paytm-like 4.5% loan fee lowers the break-even to {bep * 100:.1f} of 100 still saving; "
                 "tele-sales, the AI agent and the office are still not counted.")
    for pid, body in appx.items():
        pages.append(page(pid, pid, "A12", f'<div class="col" style="width:100%">{body}</div>', a11_title if pid == "A11" else None,
                          "The Paytm-like fee is now run under salary pay; the support costs still need modelling before the pilot budget is set." if pid == "A11" else None,
                          extra=" A8 still shows the old ₹400 street cost to win; this deck's is ₹240." if pid == "A8" else ""))
    css = A3.CSS + A3.EXTRA_CSS + OD.SD.STORY_CSS + OD.CSS_EXTRA
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Offline model stress test</title><style>{css}</style></head><body>{"".join(pages)}</body></html>'


def main():
    out = ROOT / "brief" / "qr_moat" / "stress_deck.html"
    out.write_text(build())
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

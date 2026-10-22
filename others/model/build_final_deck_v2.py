"""The final deck, v2: the tight story with the money each product makes, assumptions in the appendix
(operator, 16 Oct 2026: "Story should carry tight assumptions, money we can make on credit card etc. show that...build a
tight story. show those assumptions in appendix"). Brief: story/BRIEF_final_v2_2026-10-16.md; fix round 1:
story/FIXES_v2_round1.md (story order, one number per title, whole numbers in the main story, yearly vs one-off money,
capacity and UPI gate, short footers).

Every number on a page is read from a table that a script writes: model/crosssell_money.py (tables/xs_*_v2.csv,
pilot_rules_v2.csv), model/story_unit.py (story_unit.csv, story_paytm.csv), tables/distributions.csv and the
research/ files. Reuses the pictures of build_stress_deck (SX) and build_offline_deck (SX.OD) where their numbers
still hold, the helpers of build_qr_visual (V) and the CSS of build_final_deck. Writes brief/qr_moat/final_deck_v2.html
and Offline_model_final_v2.pdf (Offline_model_final.pdf is left untouched).
"""
import csv
import math
import re
import subprocess
from pathlib import Path

import build_qr_visual as V
import build_stress_deck as SX
import build_final_deck as FD
from build_agent_slides import inr

ROOT = Path(__file__).resolve().parent.parent
T, R = ROOT / "tables", ROOT / "research"
PDF = ROOT / "Offline_model_final_v2.pdf"
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD
APP, GREY, PAPER = SX.APP, V.GREY, V.PAPER
COLS = {"fund": "#1F64A8", "origination": "#8A3B08", "other": "#4E9BD9", "cards": "#B08A2E", "collections": "#9b8f7d"}
COL_OF = {"good": GOOD, "warn": WARN, "bad": BAD}
TOTAL = 14
NA = 11
SAL, BAL, COLL = "salary only", "salary + 0.5% a year of balance", "salary + 1% of collections"
MID = "fee 2.625% (1.5 × a DSA)"
R12S = (0.3, 0.4, 0.55, 0.7)


def rows(name):
    return list(csv.DictReader((T / name).open()))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


INP = {r["key"]: r for r in rows("xs_inputs_v2.csv")}
MONEY = {r["product"]: r for r in rows("xs_money_v2.csv")}
NPVR = rows("xs_npv_v2.csv")
BER = {(int(r["years"]), r["pay"], r["case"]): num(r["breakeven_r12"]) for r in rows("xs_breakeven_v2.csv")}
EFF = {r["step"]: r for r in rows("xs_fix_effects_v2.csv")}
ONE = rows("xs_oneway_v2.csv")
PR = {r["key"]: num(r["value"]) for r in rows("pilot_rules_v2.csv")}
YRS = rows("xs_years_v2.csv")
BENCH = rows("xs_benchmarks_v2.csv")
OB = rows("xs_other_build_v2.csv")
P2 = {r["key"]: float(r["value"]) for r in rows("xs_paytm_v2.csv")}
CHG = rows("xs_changes_v2.csv")
EVD = {r["key"]: r for r in rows("xs_evidence_v2.csv")}
CHK = {r["key"]: float(r["value"]) for r in rows("xs_checks_v2.csv")}
CURVE = [(float(r["r12"]), float(r["npv3_salary"]), float(r["npv5_salary"])) for r in rows("xs_npv_curve_v2.csv")]
PT = SX.PT
IVR = list(csv.DictReader((R / "interview_arvinder_2026-10-15.csv").open()))
CACD = next(r for r in csv.DictReader((T / "distributions.csv").open()) if r["input"] == "cac_target" and r["segment"] == "ng")
CACG = next(r for r in csv.DictReader((T / "distributions.csv").open()) if r["input"] == "cac_target" and r["segment"] == "gig")


def npv(years, pay, r, col="npv"):
    return float(next(x for x in NPVR if x["years"] == str(years) and x["pay"] == pay and abs(float(x["r12"]) - r) < 1e-9)[col])


def m(product, col):
    return float(MONEY[product][col])


def ip(key, col="middle"):
    return float(INP[key][col])


def ev(key):
    return EVD[key]["says"]


def evi(key):
    return EVD[key]["source_ids"]


def yr(r, y, col):
    return float(next(x for x in YRS if abs(float(x["r12"]) - r) < 1e-9 and x["year"] == str(y))[col])


def lakh(x, d=2, sign=True):
    return ("−" if x < 0 else ("+" if sign else "")) + f"₹{abs(x) / 1e5:.{d}f} lakh"


def sinr(x):
    """Signed whole rupees, Indian grouping (main story: whole numbers only)."""
    return ("+" if x >= 0 else "") + inr(x)


def of100(x, d=1):
    return f"{x * 100:.{d}f} of 100"


def up(x):
    return math.ceil(x * 100 - 1e-9)


def pc(x):
    return (f"{x * 100:.3f}".rstrip("0").rstrip(".")) + "%"


def wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if line and len(line) + 1 + len(w) > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    out.append(line)
    return out


def halo(svg_text):
    return svg_text.replace("<text ", '<text stroke="#fff" stroke-width="5" stroke-linejoin="round" paint-order="stroke" ')


# ---------- headline numbers ----------
BE5, BE3 = BER[(5, SAL, MID)], BER[(3, SAL, MID)]
BE5_BAL, BE3_BAL = BER[(5, BAL, MID)], BER[(3, BAL, MID)]
BE5_SAV = BER[(5, SAL, "savings only (no cross-sell)")]
BE5_LOWF, BE5_750 = BER[(5, SAL, "low funnel (10% x 30% x 25%)")], BER[(5, SAL, "750 sign-ups a year")]
CAC = m("cost_to_win_and_serve", "pv5_per_customer_won_r0.55")
ONLINE_CAC, ONLINE_KEPT, ONLINE_R12 = SX.ONLINE_CAC, SX.ONLINE_KEPT, SX.ONLINE_R12
assert abs(CAC - SX.CAC) < 1e-9 and abs(m("cost_to_win_and_serve", "pv5_per_customer_online") - ONLINE_CAC) < 1e-6
FUND_YR = m("fund", "a_year_per_proven_saver")
FEE_LOAN = ip("fee_per_loan")
COLL_LOAN = ip("coll_per_loan")
LOANS100 = ip("loans_per_100")
P100 = {k: m(k, "a_year_per_100_proven") for k in ("fund", "origination", "collections", "cards", "other")}
MKT_YEAR, MKT_ONCE = m("marketplace_yearly", "a_year_per_100_proven"), m("marketplace_once", "a_year_per_100_proven")
assert abs(MKT_YEAR - P100["origination"] - P100["collections"] - P100["other"]) < 1e-6 and abs(MKT_ONCE - P100["cards"]) < 1e-9
CUST = {r: {k: m(k, f"pv5_per_customer_won_r{r}") for k in ("fund", "origination", "collections", "cards", "other", "total")} for r in R12S}
ONL = {k: m(k, "pv5_per_customer_online") for k in ("fund", "origination", "collections", "cards", "other", "total")}
PILOT = {r: PR[f"pilot_year1_result_r{r}"] for r in R12S}
PILOT_INC = {r: PR[f"pilot_year1_income_r{r}"] for r in R12S}
NPV5 = {r: npv(5, SAL, r) for r in R12S}
NPV3 = {r: npv(3, SAL, r) for r in R12S}
SAV5 = {r: npv(5, SAL, r, "npv_savings_only") for r in R12S}
CARD_FEE, CARD_SHARE = ip("card_fee"), ip("card_share")
OTHER = ip("other")
BAL_YR = 0.005 * ip("balance")                       # 0.5% a year of the Rs 42,000 he holds on average
COL_YR = 0.01 * ip("daily") * ip("days") * 12        # 1% of a year's collections
COST_PILOT = PR["pilot_salary_12m"]
INS_LINES = sum(float(r["middle"]) for r in OB if r["product"] in ("Accident, hospital cash, small health", "Term life (small cover)", "Two-wheeler insurance", "Mobile insurance"))
SAL_M, SU_YR = ip("agent_pay"), ip("signups")
TICKET_TXT = f"₹{ip('ticket') / 1e5:g} lakh"
JANTA = float(SX.SU["street"]["still_saving_m12"])
BEAR, RANGE = f"{R12S[0] * 100:.0f}–{R12S[1] * 100:.0f}", f"{R12S[0] * 100:.0f}–{R12S[-1] * 100:.0f}"
CAC_MULT = float(re.search(r"x ([\d.]+)", CACD["basis"]).group(1))
MULT_PCT = f"{(CAC_MULT - 1) * 100:.0f}%"
PAYTM_TAKE = (PT["paytm_fee_per_loan_low"] / PT["paytm_loan_ticket"], PT["paytm_fee_per_loan_high"] / PT["paytm_loan_ticket"])
G3, G6, G12, G12_3 = (int(PR[k]) for k in ("go_m3_of_100", "go_m6_of_100", "go_m12_of_100", "go_m12_3y_of_100"))
STOP_SU = int(PR["signups_stop_a_month"])
CAPV, CASH_SAVERS = PR["capacity_visits_a_day"], PR["cash_savers_one_agent"]
UPI_Y2, UPI_Y5, UPI_Y5_70 = PR["upi_share_needed_end_y2_r0.55"], PR["upi_share_needed_end_y5_r0.55"], PR["upi_share_needed_end_y5_r0.7"]
VISITS_M12 = PR["pilot_cash_visits_a_day_m12_r0.55"]
V2_55 = yr(0.55, 2, "cash_visits_a_day_end")
CARDS_STEADY = yr(0.55, 5, "cards")                  # one agent's card money a year once his book is steady (A6)
for r in R12S:
    assert abs(PR[f"npv5_per_agent_r{r}"] - NPV5[r]) < 1e-6
assert G12 == up(BE5) and G12_3 == up(BE3) and abs(yr(0.55, 4, "cards") - CARDS_STEADY) < 1e-6
BASE_FOOT = "Base case and sources: A1."


# ---------- 1 · key conclusions ----------
def p_conclusions():
    cards = [
        ("phone", "Online is costly to keep", inr(ONLINE_KEPT), "per saver still saving after a year."),
        ("person", "The street wins him for less", inr(CAC), f"a saver: {inr(SAL_M)} a month × 12 ÷ {SU_YR:,.0f} sign-ups a year."),
        ("coin", "Savings alone do not pay", inr(FUND_YR), "a saver a year from the fund: too little for his salary."),
        ("bank", "Products can pay for him", inr(MKT_YEAR), f"a year per 100 proven savers, plus {inr(MKT_ONCE)} once from cards."),
        ("hands", "Retention decides", f"{G12} of 100", "still saving after a year makes one agent's 5-year NPV positive."),
    ]
    cells = "".join(f'<div class="cc"><div class="ch">{V.svg(40, 40, V.icon(ic, 0, 0, 38, US))}<div class="ct">{t}</div></div>'
                    f'<div class="cn">{big}</div><div class="cs">{sub}</div></div>' for ic, t, big, sub in cards)
    verdict = (f'<div class="verdict"><div class="vh">✓ Our final thought: pilot it, small and on salary</div>'
               f'<div class="vb">One salaried agent for 12 months; it can cost {inr(-PILOT[0.7])}–{inr(-PILOT[0.3])} net. Stop if fewer than {G3} of 100 still save at '
               f'month 3 or {G6} at month 6; scale only at {G12}+ at month 12.</div></div>')
    gloss = (f'<div class="gloss">NPV = today\'s value of income minus cost, discounted {pc(ip("discount"))} a year. '
             f'Bear case = {BEAR} of 100 still saving after a year.</div>')
    return f'<div class="stack big1"><div class="cgrid5">{cells}</div>{verdict}{gloss}</div>'


# ---------- 2 · the problem (build_offline_deck's picture, its value line updated) ----------
def p_problem():
    svg = SX.OD.p_problem()
    old1 = f"and he earns back only {inr(SX.OD.u('online', 'value_36m'))}"
    old2 = "in his first 3 years: the app"
    assert old1 in svg and old2 in svg
    return svg.replace(old1, f"and he earns back only {inr(ONL['total'])}").replace(old2, "over 5 years: the app")


# ---------- 3 · our hypothesis ----------
def p_hypothesis():
    rows_ = [("H1", "Win him for less", "person", f"{inr(CAC)} a saver", "his salary ÷ his sign-ups; his visits come from the same salary",
              f"online: {inr(ONLINE_CAC)}"),
             ("H2", "Keep him saving with the visit", "hands", f"{G12}+ of 100", "still saving after a year: where one agent breaks even over 5 years",
              f"online: {ONLINE_R12 * 100:.0f} of 100"),
             ("H3", "Earn more than he costs", "bank", inr(CUST[0.55]["total"]), f"one customer's 5 years at 55 of 100 still saving, against his {inr(CAC)} cost",
              f"online: {inr(ONL['total'])} back on {inr(ONLINE_CAC)}")]
    s = []
    for i, (h, t, ic, big, sub, vs) in enumerate(rows_):
        x = i * 300
        s.append(f'<rect x="{x}" y="0" width="282" height="300" rx="18" fill="{PAPER}"/><rect x="{x}" y="0" width="282" height="8" rx="4" fill="{US}"/>')
        s.append(f'<circle cx="{x + 36}" cy="46" r="20" fill="{US}"/>' + V.text(x + 36, 52, h, 14, 800, "#fff", "middle"))
        s.append(V.icon(ic, x + 212, 24, 48, US))
        for k, ln in enumerate(wrap(t, 24)):
            s.append(V.text(x + 20, 104 + k * 22, ln, 17, 800, INK))
        s.append(V.text(x + 20, 182, big, 30, 800, US))
        for k, ln in enumerate(wrap(sub, 38)):
            s.append(V.text(x + 20, 206 + k * 16, ln, 12, 400, MUTED))
        s.append(f'<rect x="{x + 20}" y="258" width="242" height="28" rx="14" fill="{V.TINT["bad"]}"/>' + V.text(x + 141, 277, vs, 12.5, 700, BAD, "middle"))
    return V.svg(882, 304, "".join(s))


# ---------- 4 · the model ----------
def box(x, y, w, h, ic, title, sub, money=None, money_col=GOOD, hl=False, note=None):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#fff" stroke="{US if hl else RULE}" stroke-width="{2.5 if hl else 1.5}"/>',
         V.icon(ic, x + 12, y + 12, 34, US), V.text(x + 54, y + 34, title, 14.5, 800, INK)]
    for k, ln in enumerate(sub):
        s.append(V.text(x + 14, y + 64 + k * 16, ln, 12, 400, MUTED))
    yy = y + 64 + len(sub) * 16 + 4
    for k, ln in enumerate(money or []):
        s.append(V.text(x + 14, yy + k * 16, ln, 12.5, 800, money_col))
    if note:
        s.append(V.text(x + w - 12, y + h - 9, note, 10.5, 700, WARN, "end"))
    return "".join(s)


def p_model():
    s = []
    top = [("person", "Sign-up at his shop", ["KYC and a savings mandate"], [f"costs {inr(CAC)} of agent time"], BAD),
           ("hands", "Visit every 2–3 days", [f"collects ₹{ip('daily'):.0f} a day in cash", f"up to {CAPV:.0f} visits a day"], None, INK),
           ("jar", "A fund in his name", ["builds over each yearly term;", "the app never holds money"], [f"we earn {pc(ip('trail'))} a year: {inr(FUND_YR)}"], GOOD),
           ("phone", "Move him to UPI", [f"{CAPV:.0f} visits a day reach {CASH_SAVERS:,.0f}", "savers on cash; the rest need UPI"], None, GOOD)]
    for i, (ic, t, sub, money, col) in enumerate(top):
        x = i * 232
        s.append(box(x, 0, 204, 124, ic, t, sub, money, col, hl=(i == 1)))
        if i < 3:
            s.append(V.arrow(x + 206, 62, x + 230, 62))
    s.append(V.arrow(450, 126, 450, 150, US, 2.5))
    s.append(f'<rect x="250" y="152" width="400" height="36" rx="18" fill="{US}"/>' +
             V.text(450, 176, f"Month {int(ip('proven_after')) + 1}: a proven saver (saved {int(ip('proven_after'))}+ months)", 15, 800, "#fff", "middle"))
    s.append(V.arrow(450, 190, 450, 212, US, 2.5))
    s.append(f'<rect x="0" y="214" width="900" height="38" rx="12" fill="{PAPER}"/>' + V.icon("bank", 14, 218, 30, US) +
             V.text(56, 239, "Our marketplace: the best offer from several lenders, card issuers and insurers", 14.5, 800, INK))
    prods = [("coin", "Loans", [f"{ip('apply') * 100:.0f} in 100 apply, {ip('apply') * ip('eligible') * 100:.0f} are eligible, {LOANS100:.1f} approved a year"],
              [f"{inr(FEE_LOAN)} a loan ({pc(ip('fee'))} of {TICKET_TXT},", f"less {pc(ip('taken_back'))} taken back)", f"+{inr(COLL_LOAN)} a loan on average,",
               "from recovery fees"], "judgement, untested"),
             ("doc", "Credit cards", [f"{CARD_SHARE * 100:.0f} in 100 proven savers, once,", "if the issuer accepts him"], [f"{inr(CARD_FEE)} a card"], "fee unverified"),
             ("hands", "Insurance and more", ["accident, life, two-wheeler cover,", "recharge, bills, small SIPs"], [f"{inr(OTHER)} a saver a year"], "judgement")]
    for i, (ic, t, sub, money, note) in enumerate(prods):
        x = i * 306
        s.append(V.arrow(x + 144, 254, x + 144, 268, MUTED, 2))
        s.append(box(x, 270, 288, 162, ic, t, sub if i else wrap(sub[0], 38), money, GOOD, note=note))
    s.append(f'<rect x="0" y="444" width="900" height="50" rx="10" fill="{V.TINT["warn"]}"/>')
    s.append(V.text(450, 464, f"The NPV counts one salary for his whole book: that holds only if {UPI_Y5 * 100:.0f} of 100 move to UPI by year 5 "
                    f"(at 55 still saving; {UPI_Y5_70 * 100:.0f} at 70).", 12.5, 800, WARN, "middle"))
    s.append(V.text(450, 484, "It assumes savers on UPI stay and earn as cash savers do; the pilot's UPI-only group tests this.", 12, 600, WARN, "middle"))
    return V.svg(900, 498, "".join(s))


# ---------- 5 · H1 ----------
def p_h1():
    items = [("Online, an app", ONLINE_KEPT, APP)] + [(f"Street, {r * 100:.0f} of 100 still saving", CAC / r, US) for r in R12S]
    x0, x1, vmax = 300, 800, 2200
    X = lambda v: x0 + (x1 - x0) * v / vmax
    cheap = float(CACD["low"]) / ONLINE_R12
    gap, h = 74, 44
    yb = 34 + gap * len(items)
    s = [V.text(0, 14, "WHAT EACH SAVER STILL SAVING AFTER A YEAR COSTS TO WIN", 12.5, 700, US),
         f'<line x1="{X(cheap)}" y1="28" x2="{X(cheap)}" y2="{yb - 16}" stroke="{APP}" stroke-width="2" stroke-dasharray="4 3"/>']
    for i, (lab, v, col) in enumerate(items):
        y = 34 + i * gap
        s.append(V.text(x0 - 14, y + 25, lab, 14.5, 700, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y}" width="{X(v) - x0}" height="{h}" rx="6" fill="{col}"/>')
        s.append(halo(V.text(X(v) + 10, y + 26, inr(v), 17, 800, col)))
    s.append(V.text(X(cheap), yb + 2, f"dashed line: the cheapest online estimate, {inr(cheap)} per saver kept", 12.5, 700, APP, "middle"))
    return V.svg(900, yb + 10, "".join(s))


# ---------- 7 · H3 part 1: savings alone ----------
def p_savings_alone():
    s = [f'<rect x="0" y="0" width="330" height="390" rx="16" fill="{PAPER}"/>', V.text(22, 34, "ONE SAVER, ONE YEARLY TERM", 12.5, 700, US)]
    steps = [(f"₹{ip('daily'):.0f} a day × {ip('days'):.0f} days", inr(ip("daily") * ip("days")), "into his fund a month", INK),
             ("it builds up, paid out at term end", inr(ip("balance")), "held on average", INK),
             (f"× {pc(ip('trail'))} a year fund commission", inr(FUND_YR), "to us, a year", US)]
    for i, (lab, big, sub, col) in enumerate(steps):
        y = 70 + i * 104
        s.append(V.text(22, y, lab, 13, 600, MUTED))
        s.append(V.text(22, y + 42, big, 32, 800, col))
        s.append(V.text(22 + len(big) * 19 + 12, y + 40, sub, 13, 700, col))
        if i < 2:
            s.append(V.arrow(40, y + 54, 40, y + 80, MUTED, 2))
    x0, base = 400, 70
    vmin = min(SAV5.values()) * 1.12
    Y = lambda v: base + (350 - base) * v / vmin
    s.append(V.text(x0, 14, "ONE AGENT'S 5-YEAR NPV ON SAVINGS ALONE", 12.5, 700, US) + V.text(x0, 34, "still saving after a year:", 11.5, 400, MUTED))
    s.append(f'<line x1="{x0}" y1="{base}" x2="900" y2="{base}" stroke="{INK}" stroke-width="1.5"/>' + V.text(x0 - 6, base + 4, "₹0", 11, 400, MUTED, "end"))
    for i, r in enumerate(R12S):
        x = x0 + 30 + i * 125
        v = SAV5[r]
        s.append(V.text(x + 45, base - 12, f"{r * 100:.0f} of 100", 13, 700, INK, "middle"))
        s.append(f'<rect x="{x}" y="{base}" width="90" height="{Y(v) - base}" rx="5" fill="{BAD}" opacity="{0.95 - 0.12 * i}"/>')
        s.append(V.text(x + 45, Y(v) + 20, inr(v), 14, 800, BAD, "middle"))
    return V.svg(900, 392, "".join(s))


# ---------- 8 · H3 part 2: where the money comes from ----------
def p_marketplace_money():
    s = [V.text(0, 14, "THE LOAN FUNNEL: 100 PROVEN SAVERS, ONE YEAR", 12.5, 700, US)]
    steps = [("100 proven savers", "", 360), (f"{ip('apply') * 100:.0f} apply", f"{ip('apply') * 100:.0f}% a year", 300),
             (f"{ip('apply') * ip('eligible') * 100:.0f} are eligible", f"{ip('eligible') * 100:.0f}% of them", 240),
             (f"{LOANS100:.1f} are approved", f"{ip('approved') * 100:.0f}% of them", 190)]
    for i, (lab, sub, w) in enumerate(steps):
        y = 30 + i * 58
        s.append(f'<rect x="{190 - w / 2}" y="{y}" width="{w}" height="46" rx="10" fill="{US}" opacity="{1 - 0.15 * i}"/>')
        s.append(V.text(190, y + 22, lab, 15, 800, "#fff", "middle"))
        if sub:
            s.append(V.text(190, y + 39, sub, 11.5, 600, "#fff", "middle"))
    s.append(V.arrow(190, 264, 190, 290, US, 2.5))
    s.append(V.text(190, 312, f"× {inr(FEE_LOAN)} a loan", 15, 700, INK, "middle"))
    s.append(V.text(190, 350, f"= {inr(P100['origination'])} a year", 28, 800, US, "middle"))
    s.append(V.text(190, 376, "apply, eligible and approved rates:", 11.5, 700, WARN, "middle") + V.text(190, 391, "our judgement, untested", 11.5, 700, WARN, "middle"))
    x0, x1 = 430, 760
    X = lambda v: x0 + (x1 - x0) * v / P100["origination"]
    s.append(V.text(x0, 14, "RUPEES FROM THE SAME 100 PROVEN SAVERS", 12.5, 700, US))
    items = [("origination", "Loan origination fees, a year", f"{LOANS100:.1f} loans × {inr(FEE_LOAN)}"),
             ("other", "Insurance and other products, a year", f"100 × {inr(OTHER)} (judgement)"),
             ("collections", "Recovery fees on bad loans, a year", "small"),
             ("cards", "Credit cards, once", "if issuers accept him: most cards need income proof")]
    for i, (k, lab, sub) in enumerate(items):
        y = 34 + i * 62
        s.append(V.text(x0, y + 12, lab, 13, 800, INK))
        s.append(V.text(x0, y + 27, sub, 11, 600 if k == "cards" else 400, WARN if k == "cards" else MUTED))
        fill = "url(#once)" if k == "cards" else COLS[k]
        s.append(f'<rect x="{x0}" y="{y + 33}" width="{max(X(P100[k]) - x0, 3)}" height="20" rx="5" fill="{fill}"/>')
        s.append(V.text(X(P100[k]) + 8, y + 49, inr(P100[k]) + (" once" if k == "cards" else ""), 14.5, 800, COLS[k]))
    y = 34 + 4 * 62 + 4
    s.append(f'<line x1="{x0}" y1="{y}" x2="900" y2="{y}" stroke="{INK}" stroke-width="1"/>')
    s.append(V.text(x0, y + 24, "The marketplace", 14, 800, INK) + V.text(900, y + 24, f"{inr(MKT_YEAR)} a year + {inr(MKT_ONCE)} once", 15.5, 800, US, "end"))
    s.append(V.text(x0, y + 48, f"The fund on the same savers (page 7): {inr(P100['fund'])} a year", 12, 700, MUTED))
    defs = (f'<defs><pattern id="once" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="7" height="7" fill="#e9dcb8"/><line x1="0" y1="0" x2="0" y2="7" stroke="{COLS["cards"]}" stroke-width="3"/></pattern></defs>')
    return V.svg(900, 398, defs + "".join(s))


# ---------- 9 · one customer won ----------
def p_customer():
    base, top, vmax = 330, 40, 800.0
    Y = lambda v: base - (base - top) * v / vmax
    s = [V.text(0, 14, "WHAT ONE CUSTOMER WON CAN EARN US OVER HIS FIRST 5 YEARS, BY PRODUCT (DISCOUNTED)", 12.5, 700, US)]
    for v in (0, 200, 400, 600, 800):
        s.append(f'<line x1="60" y1="{Y(v)}" x2="900" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}" stroke-width="{1.3 if v == 0 else 1}"/>')
        s.append(V.text(52, Y(v) + 4, inr(v), 11, 400, MUTED, "end"))
    cols = [("An app", f"{ONLINE_R12 * 100:.0f} of 100 still saving", ONL, ONLINE_CAC)] + [
        ("Street", f"{r * 100:.0f} of 100 still saving", CUST[r], CAC) for r in R12S]
    order = ("fund", "origination", "other", "cards", "collections")
    for i, (who, sub, v, cost) in enumerate(cols):
        x = 100 + i * 160 + (0 if i == 0 else 20)
        w = 104
        y = base
        for k in order:
            hh = (base - top) * v[k] / vmax
            s.append(f'<rect x="{x}" y="{y - hh}" width="{w}" height="{hh}" fill="{COLS[k]}"/>')
            if hh >= 18:
                s.append(V.text(x + w / 2, y - hh / 2 + 4, inr(v[k]), 11, 700, "#fff", "middle"))
            elif k == "cards" and hh >= 10.5:
                s.append(V.text(x + w / 2, y - hh / 2 + 3.5, f"cards {inr(v[k])}", 9.5, 800, "#fff", "middle"))
            elif k == "cards":
                s.append(V.text(x + w + 5, y - hh / 2 + 4, f"cards {inr(v[k])}", 10.5, 800, COLS["cards"]))
            y -= hh
        gap = v["total"] - cost
        s.append(V.text(x + w / 2, y - 26, inr(v["total"]), 16, 800, INK, "middle"))
        s.append(V.text(x + w / 2, y - 10, f"{sinr(gap)} vs its cost" if i == 0 else f"{sinr(gap)} vs his cost", 11.5, 800, BAD if gap < 0 else GOOD, "middle"))
        s.append(f'<line x1="{x - 8}" y1="{Y(cost)}" x2="{x + w + 8}" y2="{Y(cost)}" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="6 3"/>')
        s.append(V.text(x + w / 2, base + 20, who, 13, 800, APP if i == 0 else US, "middle"))
        s.append(V.text(x + w / 2, base + 36, sub, 11, 400, MUTED, "middle"))
    s.append(f'<line x1="60" y1="386" x2="84" y2="386" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="6 3"/>' +
             V.text(90, 390, f"what he cost to win and serve: {inr(ONLINE_CAC)} online, {inr(CAC)} on the street", 11.5, 700, BAD))
    lx = 470
    for k in order:
        lab = {"fund": "fund", "origination": "loan fees", "other": "insurance and more", "cards": "cards", "collections": "recoveries"}[k]
        s.append(f'<rect x="{lx}" y="378" width="12" height="12" rx="2" fill="{COLS[k]}"/>' + V.text(lx + 17, 389, lab, 11.5, 400, MUTED))
        lx += 17 + len(lab) * 6.3 + 16
    s.append(V.text(900, 412, "Loan funnel and insurance take-up are our judgement; the card fee is unverified (A1).", 11, 700, WARN, "end"))
    return V.svg(900, 418, "".join(s))


# ---------- 10 · Paytm ----------
def p_paytm():
    head = [("speaker", THEM, "Paytm"), ("person", US, "Us, salaried street agent")]
    th = "".join(f'<th><div class="ph">{V.svg(34, 34, V.icon(ic, 0, 0, 32, c))}<span style="color:{c}">{t}</span></div></th>' for ic, c, t in head)
    about = int(P2["paytm_cost_vs_ours_about"])
    ratio = P2["rent_vs_our_all_in"]
    rws = [("Round 1", "Win him", f"up to ~{inr(PT['paytm_cost_to_win_upto'])} a device (an upper bound)", f"{inr(CAC)} a saver", "good", f"Us, about {about}× cheaper"),
           ("Round 2", "Keep him", "a box on the counter", f"the visit; we need {G12}+ of 100 still saving", "warn", "Open: the pilot decides"),
           ("Round 3", "Earn from him", f"{inr(PT['paytm_rent_a_year'])} a year in device rent, plus loan fees collected from the till",
            f"{inr(P2['our_all_in_per_proven_saver_year'])} a year all-in per proven saver, plus {inr(math.floor(P2['our_card_once_per_proven_saver']))} once from cards", "bad",
            f"Paytm: over {math.floor(ratio)}× a year")]
    mark = {"good": "✓", "warn": "?", "bad": "✕"}
    body = "".join(f'<tr><td class="rl"><span class="rn">{a}</span><br>{b}</td><td>{c}</td><td class="us">{d}</td><td><span class="chip {k}"><span>{mark[k]}</span>{e}</span></td></tr>'
                   for a, b, c, d, k, e in rws)
    return (f'<div class="stack"><table class="ptab score bigt"><colgroup><col style="width:14%"><col style="width:30%"><col style="width:30%"><col style="width:26%"></colgroup>'
            f'<tr><th></th>{th}<th>Who is ahead</th></tr>{body}</table></div>')


# ---------- 11 · the pay rule ----------
def p_pay_rule():
    x0, x1 = 330, 860
    X = lambda v: x0 + (x1 - x0) * v
    s = [f'<rect x="{X(0.3)}" y="40" width="{X(0.4) - X(0.3)}" height="300" fill="{V.TINT["warn"]}"/>',
         V.text(X(R12S[0]) + 4, 30, f"bear case: {BEAR}", 11.5, 700, WARN)]
    for v, lab, col, anchor in ((ONLINE_R12, f"online: {ONLINE_R12 * 100:.0f}", APP, "end"), (JANTA, f"one janta book: {JANTA * 100:.0f}", US, "start")):
        s.append(f'<line x1="{X(v)}" y1="40" x2="{X(v)}" y2="340" stroke="{col}" stroke-width="1.8" stroke-dasharray="5 4"/>')
        s.append(V.text(X(v) + (-4 if anchor == "end" else 4), 30, lab, 11.5, 700, col, anchor))
    s.append(V.text(0, 14, "STILL SAVING AFTER A YEAR NEEDED FOR ONE AGENT TO BE NPV POSITIVE", 12.5, 700, US))
    pays = [(f"{inr(SAL_M)} salary only", "costs nothing per saver", BE5, BE3, GOOD, "#a9cbb8"),
            ("+ 0.5% a year of his balance", f"{inr(BAL_YR)} a saver a year; the fund pays {inr(FUND_YR)}", BE5_BAL, BE3_BAL, "#b7835a", "#e0cbb6"),
            ("+ 1% of what he collects", f"{inr(COL_YR)} a saver a year", BER[(5, COLL, MID)], BER[(3, COLL, MID)], BAD, None)]
    for i, (lab, sub, b5, b3, col, light) in enumerate(pays):
        y = 62 + i * 96
        s.append(V.text(x0 - 14, y + 18, lab, 14, 800, INK, "end") + V.text(x0 - 14, y + 36, sub, 11.5, 400, MUTED, "end"))
        for j, (b, yrs, h) in enumerate(((b5, "5 years", 26), (b3, "3 years", 18))):
            yy = y + (0 if j == 0 else 32)
            if isinstance(b, float):
                s.append(f'<rect x="{x0}" y="{yy}" width="{X(b) - x0}" height="{h}" rx="4" fill="{col if j == 0 else light}"/>')
                lab2 = f"{up(b)} of 100 · {yrs}"
                inside = X(b) > 640
                s.append(V.text(X(b) - 6 if inside else X(b) + 6, yy + h - (8 if j == 0 else 5), lab2, 12.5 if j == 0 else 11, 800,
                                ("#fff" if j == 0 else INK) if inside else col, "end" if inside else "start"))
            else:
                s.append(f'<rect x="{x0}" y="{yy}" width="{x1 - x0}" height="{h}" rx="4" fill="url(#hatchbad)"/>')
                s.append(V.text((x0 + x1) / 2, yy + h - (8 if j == 0 else 5), f"never, even if all 100 keep saving · {yrs}", 12.5 if j == 0 else 11, 800, BAD, "middle"))
    for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        s.append(f'<line x1="{X(v)}" y1="340" x2="{X(v)}" y2="346" stroke="{MUTED}"/>' + V.text(X(v), 362, f"{v * 100:.0f}", 11.5, 400, MUTED, "middle"))
    s.append(V.text(X(0.5), 380, "of 100 still saving after a year", 11.5, 400, MUTED, "middle"))
    defs = (f'<defs><pattern id="hatchbad" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="7" height="7" fill="{V.TINT["bad"]}"/><line x1="0" y1="0" x2="0" y2="7" stroke="{BAD}" stroke-width="2" opacity="0.35"/></pattern></defs>')
    return V.svg(900, 386, defs + "".join(s))


# ---------- 12 · retention decides ----------
def p_retention():
    x0, x1, y0, y1 = 90, 760, 40, 330
    rmin, rmax = CURVE[0][0], CURVE[-1][0]
    vmax = math.ceil(max(c[2] for c in CURVE) / 200000) * 200000
    vmin = math.floor(min(min(c[1], c[2]) for c in CURVE) / 200000) * 200000
    X = lambda r: x0 + (x1 - x0) * (r - rmin) / (rmax - rmin)
    Y = lambda v: y0 + (y1 - y0) * (vmax - v) / (vmax - vmin)
    s = [V.text(0, 14, "ONE AGENT'S NPV ON SALARY ONLY, BY HOW MANY STILL SAVE AFTER A YEAR", 12.5, 700, US),
         f'<rect x="{X(0.3)}" y="{y0}" width="{X(0.4) - X(0.3)}" height="{y1 - y0}" fill="{V.TINT["warn"]}"/>',
         V.text((X(0.3) + X(0.4)) / 2, y0 + 16, "bear case", 11.5, 700, WARN, "middle"),
         f'<line x1="{X(ONLINE_R12)}" y1="{y0}" x2="{X(ONLINE_R12)}" y2="{y1}" stroke="{APP}" stroke-width="1.5" stroke-dasharray="4 4"/>',
         V.text(X(ONLINE_R12) - 4, y0 + 16, f"online: {ONLINE_R12 * 100:.0f}", 11.5, 700, APP, "end")]
    for v in range(int(vmin), int(vmax) + 1, 200000):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}" stroke-width="{1.4 if v == 0 else 0.8}"/>')
        s.append(V.text(x0 - 8, Y(v) + 4, "₹0" if v == 0 else lakh(v, 0), 11, 400, MUTED, "end"))
    for r in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        s.append(V.text(X(r), y1 + 20, f"{r * 100:.0f} of 100", 11.5, 400, MUTED, "middle"))
    for idx, col, w, lab in ((2, US, 3.5, "5 years"), (1, THEM, 3, "3 years")):
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(c[0]):.1f},{Y(c[idx]):.1f}" for i, c in enumerate(CURVE))
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"/>')
        s.append(V.text(x1 + 10, Y(CURVE[-1][idx]) + 5, lab, 13.5, 800, col))
        vals = NPV5 if idx == 2 else NPV3
        for r in (0.55, 0.7):
            v = vals[r]
            s.append(f'<circle cx="{X(r)}" cy="{Y(v)}" r="5" fill="{col}" stroke="#fff" stroke-width="2"/>')
            s.append(halo(V.text(X(r) - 9, Y(v) - 9, sinr(v), 12, 800, col, "end")))
    for b, col, dx, dy, anchor in ((BE5, US, -10, -10, "end"), (BE3, THEM, 10, 22, "start")):
        s.append(f'<circle cx="{X(b)}" cy="{Y(0)}" r="7" fill="#fff" stroke="{col}" stroke-width="3"/>')
        s.append(halo(V.text(X(b) + dx, Y(0) + dy, f"{up(b)}", 13, 800, col, anchor)))
    return V.svg(900, 360, "".join(s))


# ---------- 13 · what could break it ----------
STATUS_OF = {"approved": "approved", "fee": "fee", "apply": "apply", "eligible": "eligible", "ticket": "ticket", "card_share": "card_share",
             "card_fee": "card_fee", "card_fee_fd": "card_fee_fd", "other": "other", "signups": "signups", "salary": "agent_pay", "trail": "trail",
             "daily": "daily", "taken_back": "taken_back", "collections": "rec_fee"}
TAG = {"operator": ("#e6eef7", THEM), "evidence": (V.TINT["good"], GOOD), "derived": ("#ecebe8", MUTED),
       "judgement": (V.TINT["warn"], WARN), "unverified": (V.TINT["bad"], BAD)}
SHORT = {"other": "other products", "signups": "sign-ups", "apply": "the apply rate", "daily": "the daily amount", "salary": "his salary",
         "trail": "the fund commission", "ticket": "loan size", "eligible": "eligibility", "approved": "approval", "card_share": "the card share",
         "card_fee": "the card fee", "card_fee_fd": "an FD-secured card fee", "fee": "the origination fee", "taken_back": "fees taken back",
         "collections": "recovery fees"}


def oneway(r12):
    return [r for r in ONE if abs(float(r["r12"]) - r12) < 1e-9]


def p_tornado(r12=0.4):
    o = oneway(r12)
    base = float(o[0]["npv5_base"])
    lo_all = min(0.0, min(min(float(r["npv5_at_low"]), float(r["npv5_at_high"])) for r in o))
    hi_all = max(max(float(r["npv5_at_low"]), float(r["npv5_at_high"])) for r in o)
    x0, x1 = 430, 700
    X = lambda v: x0 + (x1 - x0) * (v - lo_all) / (hi_all - lo_all)
    gap, ytop = 27, 44
    yb = ytop + gap * len(o)
    s = [V.text(0, 14, f"ONE AGENT'S 5-YEAR NPV, SALARY ONLY, {r12 * 100:.0f} OF 100 STILL SAVING: EACH INPUT MOVED ALONE", 12.5, 700, US),
         V.text(0, ytop - 10, "STATUS", 9.5, 700, MUTED) + V.text(900, ytop - 10, "5-YEAR NPV AT LOW → HIGH", 9.5, 700, MUTED, "end"),
         f'<line x1="{X(base)}" y1="{ytop - 4}" x2="{X(base)}" y2="{yb}" stroke="{INK}" stroke-width="1.5"/>',
         f'<line x1="{X(0)}" y1="{ytop - 4}" x2="{X(0)}" y2="{yb}" stroke="{BAD}" stroke-width="1.5" stroke-dasharray="4 3"/>',
         V.text(X(0) - 4, yb + 16, "₹0", 11.5, 800, BAD, "end") + V.text(X(base) + 4, yb + 16, f"middle case {sinr(base)}", 11.5, 800, INK)]
    for i, r in enumerate(o):
        y = ytop + i * gap
        st = INP[STATUS_OF[r["input"]]]["status"]
        bg, fg = TAG[st]
        s.append(f'<rect x="0" y="{y + 2}" width="76" height="17" rx="8.5" fill="{bg}"/>' + V.text(38, y + 14.5, st, 10.5, 700, fg, "middle"))
        s.append(V.text(x0 - 10, y + 15, r["name"], 11.5, 600, INK, "end"))
        a, b = float(r["npv5_at_low"]), float(r["npv5_at_high"])
        lo, hi = min(a, b), max(a, b)
        s.append(f'<rect x="{X(lo)}" y="{y + 2}" width="{max(X(base) - X(lo), 1)}" height="17" rx="3" fill="#d8a49b"/>')
        s.append(f'<rect x="{X(base)}" y="{y + 2}" width="{max(X(hi) - X(base), 1)}" height="17" rx="3" fill="#9cc3ad"/>')
        if lo < 0:
            s.append(f'<rect x="{X(lo)}" y="{y + 2}" width="{X(0) - X(lo)}" height="17" rx="3" fill="{BAD}"/>')
        s.append(V.text(900 - 98, y + 15, sinr(a), 10.5, 800, BAD if a < 0 else MUTED, "end") + V.text(900 - 88, y + 15, "→", 10.5, 700, MUTED, "middle") +
                 V.text(900, y + 15, sinr(b), 10.5, 800, BAD if b < 0 else MUTED, "end"))
    return V.svg(900, yb + 24, "".join(s))


# ---------- 14 · our final thought ----------
def p_final():
    loans, cards, apps = (PR["pilot_year1_loans_r0.55"], PR["pilot_year1_cards_r0.55"], PR["pilot_year1_applications_r0.55"])
    rules = [("Months 1–3", "Sign-ups", f"{PR['signups_plan_a_month']:.0f} a month ({SU_YR:,.0f} a year)", ("bad", "stop", f"below {STOP_SU} a month")),
             ("Months 3 and 6", "Still saving", f"{G3}+ of 100 at month 3, {G6}+ at month 6", ("bad", "stop", f"below {G3} at month 3 or {G6} at month 6")),
             ("Months 7–12", "The marketplace", f"by month 12: about {apps:.0f} applications ({ip('apply') * 100:.0f} in 100 proven savers a year), {loans:.0f} loans and {cards:.0f} cards",
              ("warn", "rethink", f"at {int(PR['rethink_loans_by_m12'])} loan or none")),
             ("Month 12", "Visits and UPI", f"at 55 of 100, year 2 needs {V2_55:.0f} cash visits a day if none use UPI: {up(UPI_Y2)}+ of 100 must be on UPI",
              ("bad", "stop", f"over {CAPV:.0f} a day with few on UPI")),
             ("Month 12", "Still saving after a year", f"{G12}+ of 100 ({G12_3}+ for a 3-year payback)", ("bad", "stop", f"below {G12}: do not scale"))]
    n, bw, gap = len(rules), 172, 10
    s = [f'<line x1="{bw / 2}" y1="50" x2="{(n - 1) * (bw + gap) + bw / 2}" y2="50" stroke="{US}" stroke-width="4"/>']
    for i, (when, what, go, (kind, word, stop)) in enumerate(rules):
        bx = i * (bw + gap)
        cx = bx + bw / 2
        s.append(f'<circle cx="{cx}" cy="50" r="14" fill="{US}"/>' + V.text(cx, 56, str(i + 1), 14, 800, "#fff", "middle"))
        s.append(V.text(cx, 22, when, 14, 800, US, "middle"))
        s.append(f'<rect x="{bx}" y="78" width="{bw}" height="214" rx="14" fill="{PAPER}"/>')
        s.append(V.text(bx + 12, 102, what, 13.5, 800, INK))
        s.append(V.badge(bx + 12, 130, "good", "go", 12, "start"))
        gl = wrap(go, 22)
        for j, ln in enumerate(gl):
            s.append(V.text(bx + 12, 152 + j * 15, ln, 11.5, 600, GOOD))
        ys = max(214, 152 + len(gl) * 15 + 22)
        s.append(V.badge(bx + 12, ys, kind, word, 12, "start"))
        for j, ln in enumerate(wrap(stop, 22)):
            s.append(V.text(bx + 12, ys + 22 + j * 15, ln, 11.5, 600, COL_OF[kind]))
    s.append(V.text(0, 312, f"The month-3 line assumes a steady drop-off and reads only about {PR['first_month_signups']:.0f} savers (month 1's sign-ups): "
                    "read it as a warning, not a verdict.", 12, 700, MUTED))
    s.append(V.text(0, 330, "The visits and UPI gate assumes savers on UPI stay and earn as cash savers do; the pilot's UPI-only group tests this.", 12, 700, MUTED))
    s.append(f'<g transform="translate(0,18)"><rect x="0" y="326" width="900" height="100" rx="14" fill="#f6efe7"/>')
    s.append(V.text(20, 352, "THE PILOT YEAR, IN CASH", 12, 700, US))
    s.append(V.text(20, 378, f"salary {inr(COST_PILOT)}; his savers bring in {inr(PILOT_INC[0.3])}–{inr(PILOT_INC[0.7])}", 13, 600, INK))
    s.append(V.text(20, 404, f"net cost {inr(-PILOT[0.7])}–{inr(-PILOT[0.3])}", 15, 800, BAD))
    s.append(V.text(20, 420, "recovery fees (later) and support costs not counted", 11, 400, MUTED))
    s.append(f'<line x1="430" y1="340" x2="430" y2="414" stroke="{RULE}" stroke-width="1.5"/>')
    s.append(V.text(452, 352, "IF IT SCALES: 5-YEAR NPV PER AGENT, BY HOW MANY STILL SAVE", 11.5, 700, US))
    for i, r in enumerate(R12S):
        x = 452 + i * 112
        s.append(V.text(x, 380, f"{r * 100:.0f} of 100", 12.5, 600, MUTED))
        s.append(V.text(x, 406, sinr(NPV5[r]), 14.5, 800, GOOD if NPV5[r] >= 0 else BAD))
    s.append("</g>")
    return V.svg(900, 446, "".join(s))


# ---------- appendix ----------
UNIT = {"Rs a month": "a month", "Rs a day": "a day", "Rs per saver": "per saver", "Rs": "", "share a year": "a year", "share": "",
        "share of the loan": "of the loan", "share of fees": "of fees", "share of loans": "of loans", "Rs a loan": "a loan", "Rs a card": "a card",
        "Rs a saver a year": "a saver a year", "Rs a saver": "a saver", "sign-ups a year": "a year", "loans": "a year", "days": "days",
        "months": "months", "a year": "a year", "visits a day": "a day"}
STATUS_CLS = {"operator": "you", "evidence": "ev", "derived": "est", "judgement": "int", "unverified": "unv"}


def fmt_in(key, unit, v):
    x = float(v)
    if key in ("r12", "online_r12"):
        return f"{x * 100:.0f} of 100" if key == "r12" else f"{x * 100:.1f} of 100"
    if unit.startswith("Rs"):
        return inr(x)
    if unit.startswith("share") or unit == "a year":
        return pc(x)
    return f"{x:,.2f}".rstrip("0").rstrip(".")


def table(head, body, widths, numeric=(), cls="tbl at2", row_cls=None):
    cg = "".join(f'<col style="width:{w}%">' for w in widths)
    th = "".join(f'<th class="{"n" if i in numeric else ""}">{h}</th>' for i, h in enumerate(head))
    trs = []
    for j, r in enumerate(body):
        rc = f' class="{row_cls[j]}"' if row_cls and row_cls[j] else ""
        trs.append(f"<tr{rc}>" + "".join(f'<td class="{"n" if i in numeric else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>")
    return f'<table class="{cls}"><colgroup>{cg}</colgroup><tr>{th}</tr>{"".join(trs)}</table>'


def tag(st):
    return f'<span class="tag {STATUS_CLS[st]}">{st}</span>'


def a1(part):
    keys = list(INP)
    keys = keys[:15] if part == 1 else keys[15:]
    body, rc = [], []
    for k in keys:
        r = INP[k]
        same = r["low"] == r["middle"] == r["high"]
        lo = "" if same else fmt_in(k, r["unit"], r["low"])
        hi = "" if same else fmt_in(k, r["unit"], r["high"])
        body.append([f"<b>{r['name in plain words']}</b>", lo, f"<b>{fmt_in(k, r['unit'], r['middle'])}</b>", hi, UNIT[r["unit"]],
                     r["source_ids"].replace("tables/", "").replace("agent_3yr.py", "the 3-year agent model"), tag(r["status"]), r["note"]])
        rc.append({"judgement": "j", "unverified": "u"}.get(r["status"], ""))
    return table(["Input", "Low", "Middle", "High", "Per", "Source ids", "Status", "Note"], body, [21, 8, 9, 8, 8, 12, 9, 25],
                 numeric=(1, 2, 3), cls="tbl at2 a1t", row_cls=rc)


def a2():
    def rng(k):
        r = INP[k]
        return " / ".join(fmt_in(k, r["unit"], r[c]) for c in ("low", "middle", "high"))
    body = [
        ["<b>Proven savers who apply in a year</b>", rng("apply"), f"{ev('lend_kissht_ever')} ({evi('lend_kissht_ever')}); {ev('lend_brazil')} ({evi('lend_brazil')}); "
         f"{ev('lend_paytm_users')} ({evi('lend_paytm_users')})", "Between an app's lifetime figure and a payroll scheme's first year. Judgement."],
        [f"<b>Applicants who can carry a {TICKET_TXT} EMI</b>", rng("eligible"), f"{ev('lend_50pct')} ({evi('lend_50pct')}); {ev('lend_income')} ({evi('lend_income')}); "
         f"{ev('lend_active')} ({evi('lend_active')})", "About half clear the income bar for that EMI. Judgement."],
        ["<b>Eligible applicants a lender approves</b>", rng("approved"), f"One lender gave the founder {pc(ip('approved', 'low'))} (founder's data); {ev('lend_kissht_appr')} ({evi('lend_kissht_appr')})",
         f"Several lenders, and months of saving as a repeat-like record, can lift one lender's {pc(ip('approved', 'low'))}. Judgement, untested."],
        ["<b>= Loans per 100 proven savers a year</b>", rng("loans_per_100"), "apply × eligible × approved", "Derived."],
        ["<b>Loan size</b>", rng("ticket"), f"{ev('lend_paytm_ticket')} ({evi('lend_paytm_ticket')}); {ev('lend_bachatt')} ({evi('lend_bachatt')})",
         f"{TICKET_TXT} is yours; the range is our judgement."],
        ["<b>Origination fee, paid by the lender</b>", rng("fee"), "1.5 × a DSA's 1.75% on personal loans (XL-13, a DSA platform blog); benchmarks on A3",
         f"{ev('lend_pays')} ({evi('lend_pays')})."],
        ["<b>Fees taken back</b>", rng("taken_back"), f"{ev('lend_takeback')} ({evi('lend_takeback')})", "Unverified: DSA platform blogs."],
        ["<b>= What one loan earns us</b>", rng("fee_per_loan"), "loan size × fee × (1 − taken back)", "Derived."],
        ["<b>Recovery fees, per loan made</b>", rng("coll_per_loan"),
         f"{ev('lend_npa')} ({evi('lend_npa')}); {pc(ip('owed'))} still owed (judgement); {ev('lend_recovered')} ({evi('lend_recovered')}); our fee "
         f"{pc(ip('rec_fee', 'low'))}–{pc(ip('rec_fee', 'high'))} of what is recovered (unverified)",
         "An average over all loans, paid about 18 months later, so not in the pilot year's cash."],
    ]
    rc = ["j", "j", "j", "", "j", "", "u", "", "u"]
    note = f'<div class="tn">{ev("lend_offers")} ({evi("lend_offers")}). {ev("lend_rate_cap")} ({evi("lend_rate_cap")}): our {TICKET_TXT} loans sit above that line.</div>'
    return table(["Step", "Low / middle / high", "Evidence", "Why the middle"], body, [22, 17, 38, 23], row_cls=rc) + note


def a3():
    order = {"referral": 0, "ours": 1, "marketplace": 2, "full service": 3}
    b = sorted(BENCH, key=lambda r: (order[r["group"]], float(r["low_pct"])))
    x0, x1 = 360, 860
    X = lambda p: x0 + (x1 - x0) * p / 12
    s = [V.text(0, 14, "WHAT A LOAN EARNS THE ONE WHO SOURCES IT, % OF THE LOAN", 12.5, 700, US)]
    for p in range(0, 13, 2):
        s.append(f'<line x1="{X(p)}" y1="28" x2="{X(p)}" y2="{40 + 48 * len(b)}" stroke="{RULE}"/>' + V.text(X(p), 56 + 48 * len(b), f"{p}%", 11.5, 400, MUTED, "middle"))
    grp_col = {"referral": GREY, "ours": US, "marketplace": THEM, "full service": "#14467a"}
    for i, r in enumerate(b):
        y = 36 + i * 48
        lo, hi = float(r["low_pct"]), float(r["high_pct"])
        col_ = grp_col[r["group"]]
        s.append(V.text(x0 - 14, y + 14, r["who"], 13, 800, US if r["group"] == "ours" else INK, "end"))
        s.append(V.text(x0 - 14, y + 30, f"{r['note']} ({r['source_ids']})", 10.5, 400, MUTED, "end"))
        s.append(f'<rect x="{X(lo) - (4 if hi == lo else 0)}" y="{y + 4}" width="{max(X(hi) - X(lo), 8)}" height="24" rx="5" fill="{col_}"/>')
        lab = f"{lo:g}%" if hi == lo else f"{lo:g}–{hi:g}%"
        if r["group"] == "ours":
            mid = float(INP["fee"]["middle"]) * 100
            s.append(f'<line x1="{X(mid)}" y1="{y}" x2="{X(mid)}" y2="{y + 32}" stroke="{INK}" stroke-width="3"/>')
            lab = f"{lo:g}–{hi:g}%, middle {pc(mid / 100)}"
        s.append(V.text(X(hi) + 8, y + 21, lab, 12.5, 800, col_))
    return V.svg(900, 64 + 48 * len(b), "".join(s))


def a4():
    s = [f'<rect x="0" y="0" width="420" height="430" rx="16" fill="{PAPER}"/>', V.text(20, 30, "CARD MONEY, 100 PROVEN SAVERS", 12.5, 700, US)]
    st = [("100 proven savers", "saved 6+ months, still saving", 360), (f"{CARD_SHARE * 100:.0f} get a card", f"once, in month 7 (your {CARD_SHARE * 100:.0f}%)", 260)]
    for i, (lab, sub, w) in enumerate(st):
        y = 44 + i * 58
        s.append(f'<rect x="{210 - w / 2}" y="{y}" width="{w}" height="46" rx="10" fill="{US}" opacity="{1 - 0.2 * i}"/>')
        s.append(V.text(210, y + 21, lab, 15, 800, "#fff", "middle") + V.text(210, y + 38, sub, 11.5, 600, "#fff", "middle"))
    s.append(V.text(210, 182, f"× {inr(CARD_FEE)} a card (unverified)", 14, 700, INK, "middle"))
    s.append(V.text(210, 214, f"= {inr(P100['cards'])} once, not every year", 21, 800, US, "middle"))
    s.append(V.text(210, 236, f"one agent, steady book: {inr(CARDS_STEADY)} a year at 55 of 100", 11.5, 700, MUTED, "middle"))
    xa, xb = 40, 380
    Xf = lambda v: xa + (xb - xa) * v / 2500
    s.append(V.text(20, 262, "FEE PER APPROVED CARD", 11.5, 700, MUTED))
    bars = ((CHK["card_fee_typical_low"], CHK["card_fee_typical_high"], f"typical, unsecured ({evi('card_fee_bm')})", GREY, 280),
            (CHK["card_fee_gromo_low"], CHK["card_fee_gromo_high"], f"GroMo to its agents ({evi('card_fee_gromo')})", THEM, 312),
            (ip("card_fee_fd", "low"), ip("card_fee_fd", "high"), "FD-secured, assumed (XL-54)", WARN, 344))
    for k, (lo, hi, lab, c, y) in enumerate(bars):
        s.append(V.text(Xf(lo), y - 4, f"{inr(lo)}–{inr(hi)}: {lab}", 10.5, 700, MUTED if k == 0 else c))
        s.append(f'<rect x="{Xf(lo)}" y="{y}" width="{Xf(hi) - Xf(lo)}" height="12" rx="4" fill="{c}"/>')
        s.append(f'<line x1="{Xf(CARD_FEE)}" y1="{y}" x2="{Xf(CARD_FEE)}" y2="{y + 12}" stroke="{US}" stroke-width="3"/>')
    s.append(V.text(Xf(CARD_FEE), 374, f"▲ ours {inr(CARD_FEE)}", 11.5, 800, US, "middle"))
    for v in (0, 1000, 2000):
        s.append(V.text(Xf(v), 390, inr(v), 10.5, 400, MUTED, "middle"))
    c55 = CUST[0.55]
    s.append(V.text(20, 414, f"Per customer won, 5 years: {inr(c55['cards'])} at 55 of 100, {c55['cards'] / c55['total'] * 100:.0f}% of his value", 12, 700, INK))
    s.append(f'<rect x="450" y="0" width="450" height="430" rx="16" fill="#fff" stroke="{RULE}"/>')
    s.append(V.text(470, 30, "WHO CAN GET ONE, AND THE RULES", 12.5, 700, US))
    facts = [("bad", "card_unsecured"), ("bad", "card_fd"), ("warn", "card_fd_payout"), ("warn", "card_issuer"), ("warn", "card_no_dlg"),
             ("warn", "card_india"), ("good", "card_pb")]
    y = 58
    for kind, k in facts:
        s.append(f'<circle cx="480" cy="{y - 4}" r="8" fill="{COL_OF[kind]}"/>' + V.text(480, y, V.MARK[kind], 10, 800, "#fff", "middle"))
        lines = wrap(ev(k) + f" ({evi(k)})", 52)
        for j, ln in enumerate(lines):
            s.append(V.text(498, y + j * 16, ln, 12, 600 if j == 0 else 400, INK))
        y += 16 * len(lines) + 16
    return V.svg(900, 432, "".join(s))


def a5():
    ob = [r for r in OB if r["product"] not in ("Total (FD excluded: already in the fund line)", "Model input (XO-39)")]
    ob.sort(key=lambda r: -float(r["middle"]))
    tot = next(r for r in OB if r["product"].startswith("Total"))
    mod = next(r for r in OB if r["product"].startswith("Model input"))
    x0, x1 = 300, 520
    vmax = max(float(r["middle"]) for r in ob)
    X = lambda v: x0 + (x1 - x0) * v / vmax
    s = [V.text(0, 14, "RUPEES A PROVEN SAVER A YEAR, FROM MONTH 7, MIDDLE CASE (LOW–HIGH ALONGSIDE)", 12.5, 700, US)]
    for i, r in enumerate(ob):
        y = 30 + i * 32
        mid, lo, hi = float(r["middle"]), float(r["low"]), float(r["high"])
        s.append(V.text(x0 - 10, y + 15, r["product"], 12, 600, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y + 2}" width="{max(X(mid) - x0, 2)}" height="18" rx="3" fill="{COLS["other"]}"/>')
        s.append(V.text(X(mid) + 6, y + 15, f"₹{mid:.1f}", 12, 800, INK) + V.text(X(mid) + 50, y + 15, f"₹{lo:g}–{hi:g}", 10.5, 400, MUTED))
    y = 30 + len(ob) * 32 + 6
    s.append(f'<line x1="0" y1="{y}" x2="620" y2="{y}" stroke="{INK}"/>')
    ok = abs(float(tot["middle"]) - float(mod["middle"])) < 0.05
    s.append(V.text(x0 - 10, y + 22, "Total (FD excluded)", 13, 800, INK, "end") + V.text(x0, y + 22, f"₹{float(tot['middle']):.1f}", 15, 800, US) +
             V.text(x0 + 56, y + 22, f"low ₹{float(tot['low']):.1f}, high ₹{float(tot['high']):.1f}", 11.5, 400, MUTED))
    s.append(V.text(0, y + 46, (f"Matches the model's ₹{float(mod['middle']):.0f} (₹{float(mod['low']):.0f} / ₹{float(mod['high']):.0f}); the low and high differ only by rounding."
                                if ok else f"Does NOT match the model's ₹{float(mod['middle']):.0f}."), 11.5, 700, GOOD if ok else BAD))
    phonepe = CHK["phonepe_insurance_per_user"]
    bx = 650
    s.append(f'<rect x="{bx}" y="24" width="250" height="150" rx="14" fill="{V.TINT["warn"]}"/>')
    s.append(V.text(bx + 14, 48, "CROSS-CHECK", 11.5, 700, WARN))
    for j, ln in enumerate(wrap(f"Our four insurance lines add up to ₹{INS_LINES:.1f} a saver a year: {INS_LINES / phonepe:.1f}× PhonePe's ₹{phonepe:.0f} a user ({evi('ins_phonepe')}).", 34)):
        s.append(V.text(bx + 14, 72 + j * 17, ln, 12.5, 600 if j else 800, INK))
    for j, ln in enumerate(wrap(f"{ev('ins_xo38')} ({evi('ins_xo38')}).", 36)):
        s.append(V.text(bx + 14, 140 + j * 15, ln, 11, 400, MUTED))
    s.append(f'<rect x="{bx}" y="190" width="250" height="{y + 56 - 190}" rx="14" fill="{V.TINT["bad"]}"/>')
    s.append(V.text(bx + 14, 214, "RISK: IRDAI COMMISSION CAPS", 11.5, 700, BAD))
    yy = 236
    for k in ("ins_draft", "ins_health", "ins_motor", "ins_term", "ins_ide"):
        lines = wrap(f"{ev(k)} ({evi(k)})", 37)
        for j, ln in enumerate(lines):
            s.append(V.text(bx + 14, yy + j * 15, ln, 11.5, 600 if j == 0 else 400, INK))
        yy += 15 * len(lines) + 8
    return V.svg(900, max(y + 60, yy), "".join(s))


def a6():
    yr_ = [r for r in YRS if abs(float(r["r12"]) - 0.55) < 1e-9]
    body = []
    for r in yr_:
        f = lambda k: inr(float(r[k]))
        body.append([f"Year {r['year']}" + ("*" if r["year"] == "1" else ""), f"{float(r['savers_end']):,.0f}", f"{float(r['proven_end']):,.0f}", f"{float(r['loans']):.1f}", f"{float(r['cards_given']):.1f}",
                     f("fund"), f("origination"), f("cards"), f("other"), f("collections"), f"<b>{f('income')}</b>", f("cost"),
                     f"<b>{f('result')}</b>", f("pv_result"), f"{float(r['cash_visits_a_day_end']):,.0f}", f"{float(r['upi_share_needed_end']) * 100:.0f}%"])
    t1 = ('<div class="tt">One agent at 55 of 100 still saving after a year, salary only (money in each year, not discounted, except the discounted result). '
          f'* Year 1 includes {inr(yr(0.55, 1, "collections"))} of recovery fees, paid later; page 14 leaves them out.</div>' +
          table(["", "Savers at year end", "Proven savers", "Loans", "Cards", "Fund", "Loan fees", "Card fees", "Insurance and more", "Recoveries",
                 "Income", "Salary", "Result", "Result, discounted", "Visits a day needed", "Share on UPI needed"], body,
                [5, 6, 6, 4.5, 4.5, 6.5, 7, 6.5, 7, 6, 7, 7, 7, 7, 6.5, 6.5], numeric=tuple(range(1, 16)), cls="tbl at2 a6t"))
    body2 = []
    for r in R12S:
        ys = [x for x in YRS if abs(float(x["r12"]) - r) < 1e-9]
        body2.append([f"{r * 100:.0f} of 100 still saving"] + [inr(float(x["result"])) for x in ys] + [f"<b>{lakh(NPV5[r])}</b>", lakh(NPV3[r])])
    t2 = ('<div class="tt" style="margin-top:10px">Each year\'s result at each retention, and the NPV</div>' +
          table(["", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "5-year NPV", "3-year NPV"], body2, [22, 10, 10, 10, 10, 10, 14, 14], numeric=tuple(range(1, 8))))
    body3 = []
    for r in R12S:
        ys = [x for x in YRS if abs(float(x["r12"]) - r) < 1e-9]
        body3.append([f"{r * 100:.0f} of 100 still saving"] + [f"{float(x['savers_end']):,.0f} · {float(x['cash_visits_a_day_end']):,.0f} · "
                                                               f"{float(x['upi_share_needed_end']) * 100:.0f}%" for x in ys])
    t3 = (f'<div class="tt" style="margin-top:10px">Savers at year end · cash visits a day if none use UPI · share that must save by UPI to stay within '
          f'{CAPV:.0f} visits a day</div>' + table(["", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"], body3, [22, 15.6, 15.6, 15.6, 15.6, 15.6], numeric=tuple(range(1, 6))))
    return t1 + t2 + t3


def a7():
    head = [("phone", APP, "An app"), ("speaker", THEM, "Paytm: the closest to us"), ("person", US, "Our street agent")]
    th = "".join(f'<th><div class="ph">{V.svg(34, 34, V.icon(ic, 0, 0, 32, c))}<span style="color:{c}">{t}</span></div></th>' for ic, c, t in head)
    rws = [
        ("How he is won", "ads, installs, sign-up offers", "a field force at the shop", "an agent at the counter"),
        ("Cost to win him", inr(ONLINE_CAC), f"up to ~{inr(PT['paytm_cost_to_win_upto'])} per device added (an upper bound; includes servicing)", inr(CAC)),
        ("What keeps him", "push notifications", f"a box on the counter: device shops held through the 2024 shock ({PT['paytm_devices_dec23_cr']:.2f} → {PT['paytm_devices_mar24_cr']:.2f} crore)",
         "the visit every 2–3 days"),
        ("What he earns them every year", "the same products, if he stays", f"{inr(PT['paytm_rent_a_year'])} in device rent ({inr(PT['paytm_rent_a_month'])} a month), before loan fees",
         f"{inr(P2['our_all_in_per_proven_saver_year'])} all-in per proven saver (fund, loans, recoveries, insurance and more), plus {inr(math.floor(P2['our_card_once_per_proven_saver']))} once for a card"),
        ("What one loan earns", "a referral fee", f"{inr(PT['paytm_fee_per_loan_low'])}–{inr(PT['paytm_fee_per_loan_high'])} ({pc(PAYTM_TAKE[0])}–{pc(PAYTM_TAKE[1])} of {inr(PT['paytm_loan_ticket'])}), before first-loss cover",
         f"{inr(P2['our_fee_per_loan'])} ({pc(ip('fee'))} of {TICKET_TXT}, less {pc(ip('taken_back'))} taken back)"),
        ("How it collects", "the borrower's bank account", f"from the shop's daily payout: losses {PT['paytm_losses_low'] * 100:.1f}–{PT['paytm_losses_high'] * 100:.0f}%",
         "the lender collects; we earn a fee if a bad loan is recovered"),
    ]
    body = "".join(f'<tr><td class="rl">{a}</td><td>{b}</td><td>{c}</td><td class="us">{d}</td></tr>' for a, b, c, d in rws)
    strip = (f'<div class="pstrip"><div class="pg2 good">✓ <b>Our edge:</b> we win him for {inr(CAC)}, not up to {inr(PT["paytm_cost_to_win_upto"])}: '
             f'about {int(P2["paytm_cost_vs_ours_about"])}× less ({P2["paytm_cost_vs_ours"]:.1f}× against the upper bound).</div>'
             f'<div class="pg2 bad">✕ <b>Our gap:</b> Paytm\'s rent alone is {P2["rent_vs_our_all_in"]:.1f}× our all-in income per proven saver a year, and each Paytm loan '
             f'earns {P2["paytm_fee_vs_ours_low"]:.1f}–{P2["paytm_fee_vs_ours_high"]:.1f}× ours, because it collects over the loan\'s life.</div></div>')
    return (f'<div class="stack"><table class="ptab"><colgroup><col style="width:15%"><col style="width:19%"><col style="width:34%"><col style="width:32%"></colgroup>'
            f'<tr><th></th>{th}</tr>{body}</table>{strip}</div>')


def a8():
    lo, mid, hi = float(CACD["low"]), float(CACD["mode"]), float(CACD["high"])
    basis = CACG["basis"]
    g = re.search(r"Groww Rs ([\d,]+)-([\d,]+) with (\d+)% organic", basis)
    c = re.search(r"CPI Rs (\d+)-(\d+)", basis)
    j = re.search(r"clear Rs (\d+) only if half of sign-ups save", basis)
    rs_ = lambda t: inr(float(t.replace(",", "")))
    s = [V.text(0, 14, "WHAT WE CAN SEE PUBLISHED", 12.5, 700, US)]
    cards = [("Groww", f"{rs_(g.group(1))}–{rs_(g.group(2))[1:]} a customer, with {g.group(3)}% coming free"),
             ("Finance-app installs", f"{rs_(c.group(1))}–{rs_(c.group(2))[1:]} each"),
             ("Jar, Stable Money", f"{rs_(j.group(1))} a saver, only if half of sign-ups save")]
    for i, (who, what) in enumerate(cards):
        y = 30 + i * 84
        s.append(f'<rect x="0" y="{y}" width="290" height="70" rx="12" fill="{PAPER}"/>' + V.text(16, y + 28, who, 14, 800, INK) + V.text(16, y + 50, what, 12, 400, MUTED))
        s.append(V.arrow(294, y + 35, 340, 140, MUTED, 1.5))
    s.append(f'<rect x="344" y="96" width="210" height="88" rx="14" fill="#fff" stroke="{US}" stroke-width="2"/>')
    s.append(V.text(449, 124, "for shopkeepers:", 12.5, 700, INK, "middle") + V.text(449, 146, f"the same, × {CAC_MULT:g}", 15, 800, US, "middle") +
             V.text(449, 168, "our judgement: none is published", 11, 400, MUTED, "middle"))
    s.append(V.arrow(556, 140, 598, 140, MUTED, 2))
    x0, x1 = 618, 862
    Xl = lambda v: x0 + (x1 - x0) * (math.log(v) - math.log(150)) / (math.log(6000) - math.log(150))
    for row, (lab, vals, y) in enumerate((("cost to win a saver", (lo, mid, hi), 80), ("each saver still saving after a year", (lo / ONLINE_R12, mid / ONLINE_R12, hi / ONLINE_R12), 200))):
        s.append(V.text(x0, y - 26, lab.upper(), 11.5, 700, MUTED))
        s.append(f'<rect x="{Xl(vals[0])}" y="{y - 10}" width="{Xl(vals[2]) - Xl(vals[0])}" height="20" rx="10" fill="{V.TINT["bad"] if row else "#e6eef7"}"/>')
        for v, w in zip(vals, ("low", "middle", "high")):
            s.append(f'<circle cx="{Xl(v)}" cy="{y}" r="{7 if w == "middle" else 5}" fill="{BAD if row else THEM}"/>')
            s.append(V.text(Xl(v), y + 30, inr(v), 13 if w == "middle" else 11.5, 800 if w == "middle" else 600, BAD if row else THEM, "middle"))
            s.append(V.text(Xl(v), y + 46, w, 10.5, 400, MUTED, "middle"))
    s.append(V.text(x0, 300, f"÷ {ONLINE_R12 * 100:.1f} of 100 still saving after a year", 12, 700, INK))
    s.append(V.text(x0, 318, "(our evidence curve for an app)", 11, 400, MUTED))
    return V.svg(900, 330, "".join(s))


def a9():
    ours = {"IV-01": f"{yr(0.55, 5, 'savers_end'):,.0f} savers by year 5 at 55 of 100; {CAPV:.0f} cash visits a day reach {CASH_SAVERS:,.0f}",
            "IV-03": f"₹{ip('daily'):.0f} a day, {ip('days'):.0f} days a month (our judgement)",
            "IV-09": "loans, cards and insurance from month 7", "IV-10": "loans, cards and insurance from month 7",
            "IV-11": f"{RANGE} of 100 still saving after a year",
            "IV-12": f"{PR['signups_plan_a_month']:.0f} new savers a month",
            "IV-13": f"{inr(SAL_M)} a month, no cut of collections; {inr(ip('agent_pay', 'low'))}–{inr(ip('agent_pay', 'high'))} tested"}
    rs = lambda t: t.replace("Rs ", "₹")
    body = [[rs(r["question"]), rs(r["answer"]), ours.get(r["id"], "")] for r in IVR if r["id"] != "IV-15"]
    rc = ["hl" if r["id"] in ("IV-01", "IV-12", "IV-13") else "" for r in IVR if r["id"] != "IV-15"]
    return table(["Question", "One janta agent's answer (15 Oct 2026)", "What this deck assumes"], body, [28, 38, 34], row_cls=rc)


def a10():
    items = [
        ("phone", "cost", "Tele-sales and AI support", "Missed-debit follow-ups, the move to UPI, loan pre-checks. Not in any number here."),
        ("bank", "cost", "Office, managers, training", "One agent's salary is the only cost counted."),
        ("doc", "cost", "Licences", f"{ev('ins_ide')} ({evi('ins_ide')}); {ev('ins_ca')} ({evi('ins_ca')}); a mutual-fund distributor code; lender agreements."),
        ("person", "cost", "KYC, cash handling, agent churn", "Full output from month 1 is assumed; a new agent, or one who leaves, earns less."),
        ("coin", "up", "A Paytm-like fee for collecting on the visit", f"Paytm earns {pc(PAYTM_TAKE[0])}–{pc(PAYTM_TAKE[1])} a loan (XL-07); it needs first-loss cover, which RBI caps at {pc(CHK['dlg_cap'])} of loans (SE-04)."),
        ("hands", "up", "Repeat loans and renewals", f"{ev('lend_kissht_appr')} ({evi('lend_kissht_appr')}); insurance renewals are not counted."),
        ("broken", "risk", "Rules can cut the fees", f"{ev('ins_draft')} ({evi('ins_draft')}); {ev('lend_rate_cap')} ({evi('lend_rate_cap')})."),
        ("jar", "risk", "Copying", f"PhonePe already offers a {inr(CHK['phonepe_deposit_min'])}-a-day deposit (QM-33). That can hit how many keep saving."),
    ]
    cls = {"cost": ("bad", "cost not counted"), "up": ("good", "upside not counted"), "risk": ("warn", "risk")}
    cells = "".join(f'<div class="ni"><div class="ai">{V.svg(30, 30, V.icon(ic, 0, 0, 28, US))}</div><div><b>{t}</b> '
                    f'<span class="chip {cls[k][0]}" style="font-size:8.4pt;padding:0 7px">{cls[k][1]}</span><br>{d}</div></div>' for ic, k, t, d in items)
    return f'<div class="nis2 big10">{cells}</div>'


def a11():
    of = lambda v: f"{float(v) * 100:.1f}" if num(v) != v or isinstance(num(v), float) else v
    order = ("last", "today_signup_cards", "round0", "m1_alone", "m2_alone", "this_deck")
    body = [[f"<b>{EFF[k]['what']}</b>" if k == "this_deck" else EFF[k]["what"], of(EFF[k]["breakeven5"]), of(EFF[k]["breakeven3"]), inr(float(EFF[k]["npv5_r0.55"]))]
            for k in order]
    t1 = ('<div class="tt">The 5- and 3-year bars, step by step (still saving after a year, salary only)</div>' +
          table(["Step", "5-year bar", "3-year bar", "5-year NPV at 55 of 100"], body, [58, 13, 13, 16], numeric=(1, 2, 3),
                row_cls=["", "", "", "j", "j", "hl"], cls="tbl at2 a1t"))
    body2 = [[f"<b>{r['what']}</b>", r["last deck"], f"<b>{r['this deck']}</b>", r["why"].replace("tables/", "")] for r in CHG]
    t2 = ('<div class="tt" style="margin-top:8px">What else changed</div>' +
          table(["", "Before", "Now", "Effect or why"], body2, [22, 22, 32, 24], cls="tbl at2 a1t"))
    return t1 + t2


# ---------- assembly ----------
def page(no, kicker, title, body, caption, src):
    lab = f"{no} / {TOTAL}" if isinstance(no, int) else f"{no} / A{NA}"
    return (f'<section class="slide"><div class="kick"><span class="pg">{lab}</span>{kicker}</div><h1>{title}</h1>'
            f'<div class="vis">{body}</div><div class="cap">{caption}</div><div class="foot">{src}</div></section>')


def col(html):
    return f'<div class="col" style="width:100%">{html}</div>'


def build():
    o40 = oneway(0.4)
    neg40 = [r for r in o40 if r["low_turns_negative"] == "True"]
    top3 = [SHORT[r["input"]] for r in o40[:3]]
    o55neg = [r for r in oneway(0.55) if r["low_turns_negative"] == "True"]
    c55 = CUST[0.55]
    below = [r for r in R12S if CUST[r]["total"] < CAC]
    pages = [
        page(1, "Key conclusions and our final thought",
             f"The street can win this saver for less than an app, and a loan marketplace can pay for the agent if {G12} of 100 keep saving: we should pilot it.",
             p_conclusions(), "Everything after this page is the evidence; every assumption is in appendix A1.",
             f"{BASE_FOOT} Tables: xs_money_v2.csv, xs_breakeven_v2.csv, pilot_rules_v2.csv; online: story_unit.csv."),
        page(2, "The problem",
             f"Online, winning a daily saver costs {inr(ONLINE_CAC)}, and each one still saving a year later costs {inr(ONLINE_KEPT)}.",
             p_problem(), f"With every product we sell, an app's saver earns back {inr(ONL['total'])} of the {inr(ONLINE_CAC)} it paid to win him.",
             f"{BASE_FOOT} Tables: distributions.csv (online cost to win: TB-18..22, TB-37, TB-38, BM-04, BM-05, NG-043), story_unit.csv, xs_money_v2.csv; SBI daily SIP: NG-033."),
        page(3, "Our hypothesis",
             "A street agent can win him for less, keep him saving with a visit every 2–3 days, and earn more from him than he costs.",
             p_hypothesis(), "Each part can fail on its own. Pages 5–9 test them; page 14 is how the pilot checks them.",
             f"{BASE_FOOT} Tables: xs_money_v2.csv, xs_breakeven_v2.csv, story_unit.csv."),
        page(4, "The model",
             "We sign him up at his shop, collect into a fund in his name, move him to UPI, and from month 7 offer loans, cards and insurance.",
             p_model(), "Every rupee we earn comes from a partner; the visit keeps him long enough to reach month 7.",
             f"{BASE_FOOT} Tables: xs_inputs_v2.csv, xs_years_v2.csv. The lender pays the fee: XL-01; every matching offer shown: XL-46; the issuer decides: REG-087."),
        page(5, "H1 · Win him for less",
             f"The street wins him for {inr(CAC)}, not {inr(ONLINE_CAC)}.",
             p_h1(), f"Even at 30 of 100 still saving, each saver kept costs {inr(CAC / 0.3)}, not {inr(ONLINE_KEPT)}; only against the cheapest online estimate "
             "is the bear case no cheaper.",
             f"{BASE_FOOT} Tables: story_unit.csv, distributions.csv (online cost to win, low end)."),
        page(6, "H2 · Keep him",
             f"He already saves daily, in cash, with an agent he trusts; one janta agent's churn implies about {JANTA * 100:.0f} of 100 still save a year later.",
             SX.p3(), "This is one agent's account of his own long-standing book, not a group of new savers we have measured.",
             "Agent interview, 15 Oct 2026 (IV-01, IV-03, IV-06 to IV-08, IV-12): 6–10 of 200–400 leave a month. Tables: story_unit.csv."),
        page(7, "H3, part 1 · Savings alone",
             f"Savings alone do not pay the agent: the fund earns about {inr(FUND_YR)} a saver a year.",
             p_savings_alone(), f"On savings alone, one agent's 5-year NPV is negative at every retention we test; he would need {up(BE5_SAV)} of 100 still saving.",
             f"{BASE_FOOT} Tables: xs_npv_v2.csv, xs_breakeven_v2.csv. Fund commission: XB-04."),
        page(8, "H3, part 2 · Where the money comes from",
             f"100 proven savers can bring {inr(MKT_YEAR)} a year from the marketplace, plus {inr(MKT_ONCE)} once from cards.",
             p_marketplace_money(), f"Once his book is steady, cards bring one agent about {inr(CARDS_STEADY)} a year at 55 of 100, if issuers accept his savers.",
             f"{BASE_FOOT} Tables: xs_money_v2.csv, xs_years_v2.csv. Funnel: A2; fee: A3; cards: A4; insurance and more: A5."),
        page(9, "What one customer is worth",
             f"At 55 of 100 still saving, one customer won can earn us about {round(c55['total'] / CAC)}× what he costs to win and serve; an app's saver earns back "
             f"{'under half' if ONL['total'] / ONLINE_CAC < 0.5 else 'less'} of his.",
             p_customer(), "Loan fees and the fund carry most of his value"
             + (f"; at {' and '.join(f'{r * 100:.0f}' for r in below)} of 100 still saving he earns back less than his {inr(CAC)}." if below else "."),
             f"{BASE_FOOT} Tables: xs_money_v2.csv (one sign-up's first 60 months, at 55 of 100 unless shown; street cost = salary per sign-up)."),
        page(10, "Can we beat Paytm at its game?",
             f"We win him about {int(P2['paytm_cost_vs_ours_about'])}× cheaper, but Paytm earns more from each one.",
             p_paytm(), "Paytm's loan fee pays for collecting from the shop's daily payout; ours is a one-off fee from the lender. Round 2 is what the pilot tests.",
             f"{BASE_FOOT} Tables: story_paytm.csv (QM-06..22, XL-07, XB-08), xs_paytm_v2.csv. Detail: A7."),
        page(11, "The pay rule",
             "Salary is the only pay that works.",
             p_pay_rule(), f"The fund pays us {inr(FUND_YR)} a saver a year; 0.5% of his balance costs {inr(BAL_YR)} and 1% of collections {inr(COL_YR)}, "
             "so those pays lose money on every saver kept.",
             f"{BASE_FOOT} Tables: xs_breakeven_v2.csv, story_unit.csv."),
        page(12, "Retention decides",
             f"On salary, one agent pays for himself over 5 years if {G12} of 100 still save after a year.",
             p_retention(), f"Over 3 years he needs {G12_3} of 100, above the bear case; at 30 of 100 he loses {inr(-NPV5[0.3])} over 5 years.",
             f"{BASE_FOOT} Tables: xs_npv_curve_v2.csv, xs_npv_v2.csv, xs_breakeven_v2.csv."),
        page(13, "What could break it",
             f"At 40 of 100 still saving the margin is thin: {len(neg40)} of {len(o40)} inputs, each alone at its bad end, turn the 5-year NPV negative.",
             p_tornado(0.4), f"{top3[0].capitalize()}, {top3[1]} and {top3[2]} swing it most. At 55 of 100, "
             f"{'no input' if not o55neg else str(len(o55neg)) + ' inputs'} alone turns it negative.",
             f"{BASE_FOOT} Tables: xs_oneway_v2.csv (also at 55 of 100), status from xs_inputs_v2.csv."),
        page(14, "Our final thought",
             f"Pilot one salaried agent for a year; scale only if {G12} of 100 still save at month 12.",
             p_final(), "Run a UPI-only comparison group alongside, and ask two lenders and one card issuer to confirm the fee and who they would approve.",
             f"{BASE_FOOT} Tables: pilot_rules_v2.csv, xs_years_v2.csv, xs_npv_v2.csv. Support costs: A10."),
    ]
    a1_note = "Rows shaded amber are our judgement; rows shaded red rest on sources we could not verify. Both are labelled where they are used."
    rule = ("Status rule: operator = your figure; evidence = a company filing or regulator; unverified = a blog or affiliate guide; "
            "derived = our arithmetic; judgement = our call.")
    A = [
        page("A1", "Appendix · every assumption (1 of 2)", "Every assumption, with its low, middle and high value, where it comes from, and how sure we are.",
             col(a1(1)), a1_note, f"{rule} Table: xs_inputs_v2.csv. IV = agent interview, 15 Oct 2026."),
        page("A1", "Appendix · every assumption (2 of 2)", "Every assumption, continued: the loan, card and product inputs, and the online comparison.",
             col(a1(2)), a1_note, f"{rule} Table: xs_inputs_v2.csv."),
        page("A2", "Appendix · the loan funnel", f"The loan funnel, step by step: {ip('apply') * 100:.0f}% apply × {ip('eligible') * 100:.0f}% eligible × "
             f"{ip('approved') * 100:.0f}% approved = {LOANS100:.1f} loans per 100 proven savers a year, each earning {inr(FEE_LOAN)}.",
             col(a2()), "All three funnel rates are our judgement and untested; they are what the pilot's months 7–12 must measure.",
             "Tables: xs_inputs_v2.csv, xs_evidence_v2.csv; research/xs_lending.csv, market_benchmarks.csv; interview (IV-04)."),
        page("A3", "Appendix · origination fee benchmarks",
             f"Why {pc(ip('fee'))} is defensible: it is inside the DSA band and below Paisabazaar's ceiling; full-service models earn more because they "
             "collect or carry losses.",
             a3(), "We would be a referral marketplace with no first-loss cover, so the DSA band is our comparison, not Paytm's or Moneyview's fee.",
             "Table: xs_benchmarks_v2.csv (LEV-009, XL-13, XL-09, LEV-065, XL-07, LEV-061, each checked against research/*.csv). DSA rates come from platform blogs: unverified."),
        page("A4", "Appendix · credit cards",
             f"Credit cards: {CARD_SHARE * 100:.0f} in 100 proven savers at {inr(CARD_FEE)} is {inr(P100['cards'])} once per 100, not a yearly amount; "
             "the share is yours, the fee unverified.",
             a4(), "The fee we can see is for unsecured cards, which need income proof; the card that fits our saver, FD-secured, has no published fee.",
             f"Tables: xs_money_v2.csv, xs_years_v2.csv, xs_inputs_v2.csv, xs_evidence_v2.csv: "
             f"{', '.join(sorted(set(i.strip() for k in EVD if k.startswith('card') for i in evi(k).split(','))))}."),
        page("A5", "Appendix · insurance and other products",
             f"Insurance and other products, product by product: ₹{float(next(r for r in OB if r['product'].startswith('Total'))['middle']):.0f} a proven saver a year "
             f"from month 7; a draft IRDAI rule can cut the insurance lines, ₹{INS_LINES:.1f} of it.",
             a5(), "No single product is big; the take-up rates are our judgement. FD referrals are left out because the fund line already counts his balance.",
             "Table: xs_other_build_v2.csv (from research/xs_other_summary.md, XO-01 to XO-39); xs_evidence_v2.csv (XO-10, XO-38, REG-053, REG-054, XO-18 to XO-20, REG-057)."),
        page("A6", "Appendix · year by year",
             f"Year by year for one agent: year 1 loses; by year 5 at 55 of 100 he needs {UPI_Y5 * 100:.0f}% of his book on UPI to stay within {CAPV:.0f} visits a day.",
             col(a6()), f"The pilot year is year 1: {inr(PILOT[0.55])} at 55 of 100 in cash, without recovery fees. Loans, cards and insurance start in month 7.",
             f"{BASE_FOOT} Tables: xs_years_v2.csv, xs_npv_v2.csv."),
        page("A7", "Appendix · Paytm in detail", "Paytm against an app and our street agent, line by line, on this deck's numbers.",
             a7(), "Our edge is the cheap win and the visit. Our gap is what each customer pays us.",
             "Tables: story_paytm.csv (QM-06..22, XL-07, XB-08), xs_paytm_v2.csv."),
        page("A8", "Appendix · the online cost to win",
             f"How we estimate the online cost to win: three published signals, scaled up {MULT_PCT} for shopkeepers, give {inr(float(CACD['low']))} / "
             f"{inr(float(CACD['mode']))} / {inr(float(CACD['high']))} a saver.",
             a8(), f"Divided by {ONLINE_R12 * 100:.1f} of 100 still saving after a year, each saver kept costs {inr(float(CACD['low']) / ONLINE_R12)}–{inr(float(CACD['high']) / ONLINE_R12)}. "
             "The × 1.1 is our judgement.",
             "Tables: distributions.csv (online cost to win: TB-18..TB-22, TB-37, TB-38, BM-04, BM-05, NG-043), story_unit.csv."),
        page("A9", "Appendix · the one interview",
             "The one interview behind the best case, and where our plan asks far more of an agent than his job does today.",
             col(a9()), "He is a co-operative bank employee of 10+ years with a mature book, so his 72 of 100 may flatter what fresh sign-ups do.",
             "Agent interview, 15 Oct 2026 (IV-01 to IV-14; the agent's identity, IV-15, is withheld). Tables: xs_years_v2.csv, pilot_rules_v2.csv."),
        page("A10", "Appendix · what is left out",
             "What is left out: the cost of tele-sales, AI support, the office and licences, and two upsides we have not counted.",
             a10(), "The support costs need modelling before the pilot budget is set; the pilot year cost on page 14 is the agent alone.",
             "Table: xs_evidence_v2.csv (REG-057, REG-059, REG-053, REG-078, XL-41); XL-07, SE-04 (research/story_evidence.csv); QM-33 (research/qr_moat.csv)."),
        page("A11", "Appendix · what changed from the last deck",
             f"What changed: tighter balances and later insurance raise the 5-year bar from {float(EFF['round0']['breakeven5']) * 100:.1f} to "
             f"{float(EFF['this_deck']['breakeven5']) * 100:.1f} of 100; the last deck's was {float(EFF['last']['breakeven5']) * 100:.1f}.",
             col(a11()), "Each change is shown alone (amber rows) and then together; M3, M4 and M5 do not move the bar.",
             "Tables: xs_fix_effects_v2.csv, xs_changes_v2.csv (built from npv_takes.csv, pilot_rules.csv, story_paytm.csv, mkt_fee_sensitivity.csv and this model)."),
    ]
    css = SX.A3.CSS + SX.A3.EXTRA_CSS + SX.OD.SD.STORY_CSS + SX.OD.CSS_EXTRA + FD.EXTRA + EXTRA
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Offline model: final v2</title><style>{css}</style></head>'
            f'<body>{"".join(pages)}{"".join(A)}</body></html>')
    head, body = html.split("<body>", 1)
    nb = lambda t: re.sub(r"\b([A-Z]{2,4})-(\d{2,3})\b", "\\1\u2011\\2", t)          # source ids never split across lines
    return head + "<body>" + re.sub(r">([^<]+)<", lambda mm: ">" + nb(mm.group(1)) + "<", body)


EXTRA = f"""
.a1t td {{ font-size: 7.9pt; padding: 2.6px 4px; line-height: 1.22; }}
.a1t th {{ font-size: 7.2pt; }}
.a6t td {{ font-size: 7.6pt; padding: 2.5px 3px; }} .a6t th {{ font-size: 6.6pt; padding: 2px 3px; }}
.tbl tr.j td {{ background: #fbf3e2; }}
.tbl tr.u td {{ background: #f9e9e6; }}
.tag {{ font-size: 7.4pt; }}
.nis2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px 12px; width: 100%; }}
.nis2 .ni {{ font-size: 9.4pt; }}
.nis2.big10 {{ gap: 14px 16px; }} .nis2.big10 .ni {{ font-size: 11.2pt; padding: 14px 16px; line-height: 1.45; }}
.nis2.big10 .ai {{ width: 34px; }}
.ni .chip {{ display: inline-flex; align-items: center; border-radius: 999px; font-weight: 700; }}
.big1 .cgrid5 {{ gap: 10px; }}
.big1 .cgrid5 .cc {{ padding: 16px 14px 18px; gap: 10px; min-height: 66mm; }}
.big1 .cgrid5 .ct {{ font-size: 12.5pt; }} .big1 .cgrid5 .cn {{ font-size: 25pt; }} .big1 .cgrid5 .cs {{ font-size: 11.6pt; line-height: 1.4; }}
.big1 .cgrid5 .ch svg {{ width: 38px; height: 38px; }}
.big1 .verdict {{ margin-top: 18px; padding: 18px 22px; }} .big1 .verdict .vh {{ font-size: 17pt; }} .big1 .verdict .vb {{ font-size: 13pt; line-height: 1.5; }}
.gloss {{ margin-top: 14px; font-size: 11pt; color: {MUTED}; }}
.ptab.bigt td {{ font-size: 14.5pt; padding: 30px 12px; line-height: 1.45; }} .ptab.bigt .ph {{ font-size: 14pt; }} .ptab.bigt .chip {{ font-size: 12pt; }}
.ptab.bigt .rn {{ font-size: 10pt; }}
"""


def main():
    out = ROOT / "brief" / "qr_moat" / "final_deck_v2.html"
    html = build()
    visible = re.sub(r"<[^>]+>", " ", html.split("</style>")[1])
    for bad in ("Bueno", "BetterPlace", "Arvinder", "Singh", "Bareilly", "PNB", "r12", "R12", "card_share", "pv5_", "npv5_", "npv_savings", "npv_middle", "_r0.",
                "cac_target", "disc_rate", "PAYS", ".py", "Rs "):
        assert bad not in visible, bad
    out.write_text(html)
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

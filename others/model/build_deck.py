"""Write the Slides deck (deck/project/…) from the frozen tables.

Every number on a slide comes from tables/deck_numbers.csv (model outputs),
tables/deck_facts.csv (sourced facts), tables/inputs*.csv (assumptions) or
tables/inputs_path.csv / channels.csv, looked up by id. The ids each slide
used go to deck/used_ids.json; check_deck.py confirms nothing was typed by hand.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
DECK = ROOT / "deck"
SLIDES = DECK / "project" / "slides"

NUM = {r["id"]: r for r in csv.DictReader(open(T / "deck_numbers.csv"))}
FACT = {r["id"]: r for r in csv.DictReader(open(T / "deck_facts.csv"))}
INP = {}
for f in ("inputs.csv", "inputs_lending_first.csv"):
    for r in csv.DictReader(open(T / f)):
        INP[r["id"]] = r
PATH = list(csv.DictReader(open(T / "inputs_path.csv")))
VERIFY = json.loads((T / "verify_result.json").read_text())
assert VERIFY["mismatches"] == 0, "workbook and engine disagree: fix before building the deck"
CHAN = {r["channel"]: r for r in csv.DictReader(open(T / "channels.csv"))}

USED: dict[str, list[str]] = {}
_cur = [""]


def _use(kind, id):
    USED.setdefault(_cur[0], []).append(f"{kind}:{id}")


def N(id):
    _use("num", id)
    return NUM[id]["display"]


def F(id):
    _use("fact", id)
    return FACT[id]["display"]


def I(id, scen="base", fmt="{:.0f}", seg="gig"):
    """An input value (seg='ng' reads the non-gig column, falling back to gig). fmt: 'pct', 'inr' or a format string."""
    _use("input", f"{id}.{scen}.{seg}")
    ngv = INP[id].get("ng_" + scen, "")
    v = float(ngv if (seg == "ng" and ngv not in ("", None)) else INP[id][scen])
    if fmt == "pct":
        return f"{v * 100:.1f}".rstrip("0").rstrip(".") + "%"
    if fmt == "inr":
        return "₹" + (f"{v:,.2f}" if v != int(v) else f"{v:,.0f}")
    return fmt.format(v)


def PY(year, field, fmt="{:,.0f}"):
    _use("path", f"{year}.{field}")
    return fmt.format(float(PATH[year - 1][field]))


def CH(channel, field, fmt="{:,.0f}"):
    _use("channel", f"{channel}.{field}")
    return fmt.format(float(CHAN[channel][field]))


# ---------------------------------------------------------------- look
INK, PAPER, SAND, BODY, MUTED = "#14213D", "#F7F4EE", "#ECE5D6", "#4A5568", "#5B6270"
ACC_TXT, ORANGE, BLUE, LBLUE, GREY = "#9A4A0B", "#D9822B", "#2F66A8", "#A9C4E6", "#C9C1B2"
SAFFRON, DARK_SOFT, CARD, AP_HEAD = "#F2C48D", "#C8D2E2", "#FFFDF8", "#E0D6C2"
SERIF = "'Source Serif 4', Georgia, serif"
SANS = "'IBM Plex Sans', Arial, sans-serif"


def eyebrow(t, color=ACC_TXT):
    return f'<p style="font-size:24px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{color}">{t}</p>'


def title(t, color=INK):
    return f'<h2 style="font-family:{SERIF};font-size:56px;font-weight:600;line-height:1.12;color:{color}">{t}</h2>'


def lead(t, color=BODY, width=1600):
    return f'<p style="font-size:28px;line-height:1.4;color:{color};width:{width}px">{t}</p>'


def footer(src, page, color=MUTED):
    return (f'<div style="position:absolute;left:128px;right:128px;bottom:64px;display:flex;gap:32px">'
            f'<p style="flex:1;font-size:24px;color:{color}">{src}</p>'
            f'<p style="font-size:24px;color:{color}">{page}</p></div>')


def notes(t):
    t = " ".join(t.split())
    assert len(t) <= 4000, len(t)
    return f"<aside>{t}</aside>"


def section(id, body, bg=PAPER, fg=INK, extra_style=""):
    style = (f"background:{bg};color:{fg};font-family:{SANS};padding:128px 128px 160px;"
             f"display:flex;flex-direction:column;gap:28px{extra_style}")
    return f'<section id="{id}" data-transition="fade" style="{style}">\n{body}\n</section>\n'


def p(t, size=24, color=BODY, weight=400, extra=""):
    w = f"font-weight:{weight};" if weight != 400 else ""
    return f'<p style="font-size:{size}px;line-height:1.35;color:{color};{w}{extra}">{t}</p>'


def kpi(num, cap, color=INK, capcolor=BODY, size=56):
    return (f'<div style="display:flex;flex-direction:column;gap:6px">'
            f'<p style="font-size:{size}px;font-weight:600;line-height:1.1;color:{color}">{num}</p>'
            f'<p style="font-size:24px;line-height:1.35;color:{capcolor}">{cap}</p></div>')


def card(inner, bg=CARD, border="#E3DDD0", pad=32, flex="flex:1;", gap=12):
    return (f'<div style="{flex}display:flex;flex-direction:column;gap:{gap}px;background:{bg};padding:{pad}px;'
            f'border:1px solid {border};border-radius:16px">{inner}</div>')


def table(header, rows, widths, size=24, color=INK, head_bg=SAND, width=1664, bold_first=False):
    ths = "".join(f'<th style="width:{w}%">{h}</th>' for h, w in zip(header, widths))
    out = [f'<table style="font-family:{SANS};font-size:{size}px;color:{color};width:{width}px">',
           f'<tr style="background:{head_bg}">{ths}</tr>']
    for r in rows:
        tds = "".join(f"<td>{('<b>' + c + '</b>') if (j == 0 and bold_first) else c}</td>" for j, c in enumerate(r))
        out.append(f"<tr>{tds}</tr>")
    out.append("</table>")
    return "".join(out)


SLIDES_OUT: list[tuple[str, str]] = []


def slide(id):
    def deco(fn):
        _cur[0] = id
        SLIDES_OUT.append((id, fn()))
        return fn
    return deco


PLAN_SRC = "Model: savings_first_model.xlsx, 30 Sep 2026. Plan = daily saving + 5% loss cover + gold."


# ================================================================ 1. cover
@slide("cover")
def _():
    body = f"""
{eyebrow("An honest test · 30 September 2026", SAFFRON)}
<div style="display:flex;flex-direction:column;gap:36px">
<h1 style="font-family:{SERIF};font-size:120px;font-weight:600;line-height:1.05;color:{PAPER}">Save first, lend later</h1>
<h2 style="font-family:{SERIF};font-size:56px;font-weight:400;line-height:1.2;color:{PAPER};width:1560px">Gig workers and the self-employed could save {I('daily_amount', fmt='inr')}–{I('daily_amount', fmt='inr', seg='ng')} a day automatically, and that habit might be the cheapest way to lend to them later.</h2>
</div>
<div style="display:flex;flex-direction:column;gap:12px">
{p("This deck tests whether the numbers add up. Short answer: not in the base case. In the best case, yes, and cross-sell is the one thing that must go right.", 28, DARK_SOFT, extra="width:1500px")}
{p("Sandeep Arora · co-founder and CEO of Bueno Finance 2019–22 (YC W21) · IIT Delhi", 24, DARK_SOFT)}
</div>
{notes(f'''Say: This is a micro-savings app for two kinds of people in equal numbers: app delivery and ride workers, and the self-employed, meaning shopkeepers, tradespeople, drivers outside the apps and small business owners. They save {I('daily_amount', fmt='inr')} to {I('daily_amount', fmt='inr', seg='ng')} a day automatically, the money sits with partners and never with us, and we earn later by offering loans, cards and insurance. I ran the opposite model at Bueno, lending first to gig and blue-collar workers. This deck is an honest test of whether saving first is the better business. The answer: not on today's evidence in the base case, and yes in the best case, where cross-sell is the one assumption that must hold. The last slide is a one-year pilot that settles it. Likely question: So is this a pitch or not? Answer: It is a test. I want you to see the numbers that would make me stop, before any money goes in.''')}
"""
    return section("cover", body, bg=INK, fg=PAPER, extra_style=";justify-content:space-between;padding:128px")


# ================================================================ 2. Bueno
@slide("bueno")
def _():
    parts = [("Interest and fees received", "lf_base_loan_interest_received"), ("Paid to the lending partner", "lf_base_loan_paid_to_nbfc"),
             ("Losses on late loans", "lf_base_loan_losses"), ("Collections", "lf_base_loan_collection"),
             ("Operations", "lf_base_loan_ops"), ("Platform data fee", "lf_base_loan_platform_fee")]
    lo, hi, H = -300.0, 1400.0, 260
    sc = H / (hi - lo)
    y = lambda v: (hi - v) * sc
    run, cols = 0.0, []
    for name, nid in parts:
        v = float(NUM[nid]["value"])
        a, b = run, run + v
        cols.append((name, N(nid), y(max(a, b)), y(min(a, b)) - y(max(a, b)), BLUE if v > 0 else ORANGE))
        run = b
    tv = float(NUM["lf_base_loan_total"]["value"])
    cols.append(("Result, before finding the borrower", N("lf_base_loan_total"), y(0), y(tv) - y(0), "#8A3B08"))
    zero = y(0)
    colhtml = []
    for name, disp, top, h, color in cols:
        colhtml.append(
            f'<div style="flex:1;display:flex;flex-direction:column;gap:8px">'
            f'<div style="position:relative;height:{H}px">'
            f'<div style="position:absolute;left:0;top:{zero:.0f}px;width:150px;height:2px;background:{MUTED}"></div>'
            f'<div style="position:absolute;left:20px;top:{top:.0f}px;width:110px;height:{max(h, 3):.0f}px;background:{color};border-radius:4px"></div></div>'
            f'<p style="font-size:28px;font-weight:600;color:{INK}">{disp}</p>'
            f'<p style="font-size:24px;line-height:1.3;color:{BODY}">{name}</p></div>')
    body = f"""
{eyebrow("What I learnt at Bueno")}
{title(f"At Bueno I made {F('bueno_loans')} loans a month to gig workers, and the first loan lost money.")}
<div style="display:flex;gap:64px;flex:1">
<div style="width:400px;display:flex;flex-direction:column;justify-content:space-between">
{kpi(F("bueno_loans"), f"loans in our best month, with a team of {F('bueno_team')} and {F('bueno_raised')} raised")}
{kpi(F("bueno_approval"), "of applicants approved; the rest cost money and earned nothing")}
{kpi(N("lf_base_cac"), f"to find each borrower: {N('lf_base_cac_per_applicant')} per applicant, divided by {F('bueno_approval')}")}
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:16px">
{p(f"One {F('bueno_ticket')}, {I('lf_tenor')}-month first loan, line by line (base case)", 28, INK, 600)}
<div style="display:flex;gap:12px">{''.join(colhtml)}</div>
</div>
</div>
{footer("Source: founder data (Bueno, 2019–22); model, Lending-first tab, base case.", 2)}
{notes(f'''Say: Bueno lent small three-month loans to blue-collar and gig workers, mostly through platforms like Swiggy. At our peak we made {F('bueno_loans')} loans a month with {F('bueno_team')} people. A partner NBFC funded the loans at {F('bueno_nbfc')} a year and we covered all its losses. Borrowers paid about {F('bueno_irr')} a year including fees. Walk the bars: on one {F('bueno_ticket')} first loan we kept {N('lf_base_loan_interest_received')} of interest and fees, paid {N('lf_base_loan_paid_to_nbfc')} to the partner, lost {N('lf_base_loan_losses')} on late loans ({F('bueno_dpd')} of loans went 90+ days late and we recovered about half), and spent on collections, operations and the platform's data fee. The first loan ends at {N('lf_base_loan_total')}, before the {N('lf_base_cac')} it cost to find the borrower. Repeat loans were better, but only {F('bueno_repeat')} of repayers came back. Likely question: How did Bueno end? Answer: BetterPlace acquired it in May 2023. The lesson I took: platforms were the best channel, the employer channel was too small, and the first loan never paid for itself.''')}
"""
    return section("bueno", body)


# ================================================================ 3. customer
@slide("customer")
def _():
    gig = "".join([kpi(F("rider_net"), f"net a month for a rider working full days, after fuel and phone ({F('rider_gross')} before)", size=36),
                   kpi(F("rider_tenure"), "average time on one platform", size=36),
                   kpi(F("rider_borrowed").capitalize(), f"borrowed for their bike or phone; {F('rider_missed')} of them missed a repayment", size=36)])
    ng = "".join([kpi(F("se_urban_income"), f"average earnings a month, urban self-employed; the survey doesn't say if before or after business costs ({F('se_delhi_income')} in Delhi)", size=36),
                  kpi(F("se_delhi_share"), "of Delhi's workers are self-employed", size=36),
                  kpi(F("vendor_save_x"), "as much saved by market vendors as by bike-taxi drivers given the same account (Kenya)", size=36)])
    body = f"""
{eyebrow("The customer")}
{title("Half our savers are delivery riders; half are shopkeepers and the self-employed, who likely save more and stay longer.")}
<div style="display:flex;gap:32px;flex:1">
{card(p("<b>Half: app delivery and ride workers</b>", 28, INK) + '<div style="display:flex;flex-direction:column;gap:20px">' + gig + '</div>')}
{card(p("<b>Half: shopkeepers, tradespeople, drivers outside the apps, small business owners</b>", 28, INK) + '<div style="display:flex;flex-direction:column;gap:20px">' + ng + '</div>', bg=SAND, border=SAND)}
</div>
{footer(f"Sources: IDinsight 2024 ({F('rider_n')} riders); PLFS 2025; Dupas and Robinson 2013 (Kenya); Economic Survey 2025–26.", 3)}
{notes(f'''Say: Half our savers are app delivery and ride workers. The best data is IDinsight's 2024 survey of {F('rider_n')} riders on one platform across India: a full-time rider nets {F('rider_net')} after fuel and phone, lasts about {F('rider_tenure')} on a platform, and {F('rider_borrowed')} of those who owned a bike or phone borrowed to buy it. The other half are the self-employed: shopkeepers, tradespeople like electricians and tailors, auto and car drivers outside the apps, domestic workers and small business owners. They make up {F('se_delhi_share')} of Delhi's workers. The urban self-employed average {F('se_urban_income')} a month ({F('se_delhi_income')} in Delhi) in the government's labour survey, but that average includes shop owners with staff, and the survey does not say whether it is before or after business costs, so it cannot be compared cleanly with a rider's {F('rider_net')} net or {F('rider_gross')} gross. Street vendors mostly earn {F('vendor_income')}. The only head-to-head study, from Kenya, found market vendors saved {F('vendor_save_x')} as much as bike-taxi drivers. Likely question: Why two customers at once? Answer: The self-employed stay longer and save more, which raises the best case; they are also riskier borrowers. The pilot reads each half separately.''')}
"""
    return section("customer", body)


# ================================================================ 4. problem
@slide("problem")
def _():
    boxes = [(0, 0, "1. A slow week or a breakdown cuts earnings"), (600, 0, "2. No savings to fall back on"),
             (600, 280, "3. Borrow fast: loan app, moneylender, platform advance"), (0, 280, "4. Repayments eat next week's earnings")]
    bx = "".join(f'<p style="position:absolute;left:{l}px;top:{t}px;width:440px;height:170px;padding:24px;font-size:28px;line-height:1.3;'
                 f'color:{INK};background:{CARD};border:2px solid {ORANGE};border-radius:16px">{txt}</p>' for l, t, txt in boxes)
    st = f'style="color:{ORANGE};border-width:3px"'
    con = (f'<x-connector x1="440" y1="85" x2="600" y2="85" {st}></x-connector>'
           f'<x-connector x1="820" y1="170" x2="820" y2="280" {st}></x-connector>'
           f'<x-connector x1="600" y1="365" x2="440" y2="365" {st}></x-connector>'
           f'<x-connector x1="220" y1="280" x2="220" y2="170" {st}></x-connector>')
    body = f"""
{eyebrow("The problem")}
{title("With no savings buffer, one bad week pushes workers into costly debt, and no formal product fits daily income.")}
<div style="display:flex;gap:64px;flex:1;align-items:center">
<!-- A 0,0,440,170  B 600,0,440,170  C 600,280,440,170  D 0,280,440,170 -->
<div style="position:relative;width:1040px;height:450px">{bx}{con}</div>
<div style="flex:1;display:flex;flex-direction:column;gap:24px">
{kpi(F("gig_under15k"), "of gig workers earn under ₹15,000 a month")}
{kpi(F("loans_90plus"), "of ₹10–50k personal loans go 90+ days late")}
{kpi(F("sip_min"), "the smallest daily investment most mutual funds take")}
</div>
</div>
{footer("Sources: Economic Survey 2025–26; CRIF High Mark, Jan 2025; AMC notices, Oct 2024.", 4)}
{notes(f'''Say: The loop on the left is what a rider's month looks like with no buffer. One slow week or a breakdown cuts earnings; with nothing saved they borrow fast from a loan app, a moneylender or a platform advance; repayments then eat next week's earnings. On the right, the evidence: {F('gig_under15k')} of gig workers earn under ₹15,000 a month; small personal loans of ₹10-50k reach 90+ days late at {F('loans_90plus')}; and formal saving doesn't fit daily cash. Most funds need {F('sip_min')} for a daily SIP, and SEBI's small-SIP scheme is monthly only. Likely question: Isn't this what microfinance solves? Answer: Microfinance lends. It doesn't build a buffer, and RBI now caps a low-income household's repayments at half its income.''')}
"""
    return section("problem", body)


# ================================================================ 5. funnel
@slide("funnel")
def _():
    W = 900
    a, b, c = (float(NUM[k]["value"]) for k in ("lf_funnel_applicants", "lf_funnel_approved", "lf_funnel_repaid"))
    bars = [(N("lf_funnel_applicants"), "applicants", W, N("lf_base_cac_per_applicant") + " each to find, check and KYC", LBLUE),
            (N("lf_funnel_approved"), f"approved ({F('bueno_approval')})", W * b / a, N("lf_base_cac") + " per borrower", BLUE),
            (N("lf_funnel_repaid"), "repay the first loan", W * c / a, N("lf_base_cac_per_good_borrower") + " per good borrower", INK)]
    rows = "".join(
        f'<div style="display:flex;flex-direction:column;gap:8px">'
        f'<div style="display:flex;gap:20px;align-items:baseline"><p style="font-size:36px;font-weight:600;color:{INK}">{num}</p>'
        f'<p style="font-size:28px;color:{BODY}">{lab}</p><div style="flex:1"></div>'
        f'<p style="font-size:28px;font-weight:600;color:{ACC_TXT}">{cost}</p></div>'
        f'<div style="width:{w:.0f}px;height:36px;background:{col};border-radius:6px"></div></div>'
        for num, lab, w, cost, col in bars)
    body = f"""
{eyebrow("Why lending-first leaks")}
{title("Lending-first pays to find four applicants for every borrower, and the way Bueno absorbed losses is now barred.")}
{lead(f"You pay to acquire every applicant, then turn most away. Savings-first turns nobody away: anyone can save {F('gold_min')}.")}
<div style="display:flex;gap:64px;flex:1">
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">{rows}</div>
<div style="width:480px;display:flex;flex-direction:column;gap:24px">
{card(p("<b>Then: Bueno, 2019–22</b>", 28, INK) + p("We covered 100% of the lending partner's losses.", 28, BODY))}
{card(p("<b>Now: RBI rules</b>", 28, INK) + p(f"An app may cover at most {F('dlg_cap')} of the loans it sources. More needs our own NBFC.", 28, BODY), bg=SAND, border=SAND)}
</div>
</div>
{footer("Sources: founder data (Bueno); RBI Digital Lending Directions, May 2025; model, Lending-first tab.", 5)}
{notes(f'''Say: This is the leak in lending-first. Of {N('lf_funnel_applicants')} applicants at Bueno, we approved {N('lf_funnel_approved')}, and {N('lf_funnel_repaid')} repaid the first loan without going 90+ days late. Each applicant cost {N('lf_base_cac_per_applicant')} to find, check and KYC, so each borrower cost {N('lf_base_cac')} and each good borrower {N('lf_base_cac_per_good_borrower')}. The second problem is structural. We could do it because we covered 100% of our NBFC partner's losses. Under RBI's digital lending rules any guarantee on a loan book counts as default-loss cover, and an app may cover at most {F('dlg_cap')}. So Bueno's model can't run today without our own NBFC, which needs {F('nof')} minimum. Likely question: Couldn't a better model fix the approval rate? Answer: Partly. But the people you reject still cost money to find, and the capital problem remains.''')}
"""
    return section("funnel", body)


# ================================================================ 6. flip (accent)
@slide("flip")
def _():
    steps = [("Day 1", f"Save from {F('gold_min')} a day into gold and a liquid fund"),
             (f"Month {I('ins_start')}", "Accident and health cover"),
             (f"Month {I('loan_start')}", "A first small loan from a partner lender"),
             (f"Month {I('fd_start')}", "A bank FD for goals, a card backed by it, an equity SIP"),
             (f"Month {I('unsec_start')}", "An unsecured card for good savers")]
    W, P_, H, R = 300, 341, 200, 60
    boxes = "".join(
        f'<div style="position:absolute;left:{i * P_}px;top:{(len(steps) - 1 - i) * R}px;width:{W}px;height:{H}px;background:{CARD};'
        f'border:2px solid {INK};border-radius:16px;padding:20px;display:flex;flex-direction:column;gap:8px">'
        f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{when}</p>'
        f'<p style="font-size:24px;line-height:1.3;color:{INK}">{what}</p></div>' for i, (when, what) in enumerate(steps))
    body = f"""
{eyebrow("The flip", INK)}
{title("The flip: everyone can save, so start there and offer credit once the habit and the data exist.")}
{lead("Nobody is turned away at the front door. Each step up uses what the earlier steps showed us: the saving streak, the payout record and the FD.", INK)}
<!-- steps: left i*341, top (4-i)*60, 300x200 -->
<div style="position:relative;width:1664px;height:440px">{boxes}</div>
{footer("Timings are model assumptions (Inputs tab), for the pilot to test.", 6, INK)}
{notes(f'''Say: This is the flip. Instead of lending first and rejecting most people, everyone starts by saving, from {F('gold_min')} a day into gold and a liquid fund. Insurance comes from month {I('ins_start')}. A first small loan comes from month {I('loan_start')}: a partner lender funds it, and we cover up to {F('dlg_cap')} of its losses. From month {I('fd_start')} the saver can move goal money into a bank FD, get a card backed by it, and start an equity SIP. An unsecured card follows from month {I('unsec_start')} for good savers. Every product is sold by a regulated partner; we distribute and never hold the money. Likely question: Why would a saver want a loan at all? Answer: They already borrow, from loan apps and moneylenders. We offer a cheaper loan to people whose saving we can see.''')}
"""
    return section("flip", body, bg=SAFFRON)


# ================================================================ 7. why now
@slide("whynow")
def _():
    rows = [
        ["May 2025", f"RBI caps an app's loss cover at {F('dlg_cap')} of the loans it sources", "Door", "We can share loan risk without our own NBFC"],
        ["Jun 2025; in force Apr 2026", "No loans against gold, including digital gold", "Fence", "Only FD money can back a card or a loan"],
        ["Oct 2025; live Dec 2025", "Any UPI app can see and move a saver's auto-debit", "Fence", "Savers can leave, or be poached, in a tap"],
        ["Nov 2025", "SEBI: digital gold is outside its rules", "Fence", "Gold carries rule-change risk"],
        ["Apr 2026", f"RBI: auto-debits up to {F('emandate_limit')} need no fresh approval", "Door", "Daily auto-saving works at any size we need"],
        ["Sep 2026 (draft)", f"IRDAI caps commission: {F('irdai_health')} first year, {F('irdai_loan')} if sold with a loan", "Fence", "Insurance earns less than today"],
    ]
    body = f"""
{eyebrow("Why now")}
{title(f"The 2025–26 rules open the door with daily UPI Autopay and {F('dlg_cap')} loss cover, and fence it: no loans against gold, and capped insurance commissions.")}
{table(["When", "What changed", "Door or fence", "What it means for us"], rows, [18, 40, 12, 30])}
{footer("Sources: RBI, NPCI, SEBI and IRDAI circulars (regulation_rails.csv).", 7)}
{notes(f'''Say: Six rule changes set the frame. The doors: RBI's digital lending rules let an app cover up to {F('dlg_cap')} of a partner's loan losses, which lets us earn more per loan without becoming a lender; and RBI's 2026 e-mandate framework lets auto-debits up to {F('emandate_limit')} run without fresh approval. UPI Autopay is the standing instruction that debits a bank account on schedule; it carries no merchant fee even after the new fee on UPI payments above ₹2,000 from 15 Oct 2026. The fences: RBI bars loans against gold, including digital gold, from April 2026; NPCI lets any UPI app show and move a saver's mandate; SEBI says digital gold is outside its rules; and IRDAI's draft of 23 Sep 2026 would cap insurance commissions. The Labour Codes of 21 Nov 2025 cover gig workers but give a private savings product no hook. Likely question: Is 2025-26 a real window? Answer: The doors are real but small. The fences matter more: they decide which savings product we can build on.''')}
"""
    return section("whynow", body)


# ================================================================ 8. product
@slide("product")
def _():
    pots = [(0, "Digital gold", f"vault partner · from {F('gold_min')}"),
            (160, "Liquid fund", f"fund house · {F('sip_min')}+ a debit · take out {F('instant_redeem')} a day"),
            (320, "Bank FD", f"partner bank · from {F('fd_min')} · backs the FD card")]
    el = [f'<div style="position:absolute;left:0;top:0;width:320px;height:110px;background:{SAND};border-radius:16px;padding:20px">'
          f'<p style="font-size:24px;font-weight:600;color:{INK}">Our app: the window</p>'
          f'<p style="font-size:24px;color:{BODY}">goals, streaks, offers</p></div>',
          f'<div style="position:absolute;left:0;top:160px;width:320px;height:150px;background:{INK};border-radius:16px;padding:24px">'
          f'<p style="font-size:28px;font-weight:600;line-height:1.2;color:{PAPER}">Worker\'s own bank account</p>'
          f'<p style="font-size:24px;color:{DARK_SOFT}">the payout lands here</p></div>']
    for top, name, sub in pots:
        el.append(f'<div style="position:absolute;left:900px;top:{top}px;width:620px;height:150px;background:{CARD};border:2px solid {BLUE};'
                  f'border-radius:16px;padding:20px"><p style="font-size:28px;font-weight:600;color:{INK}">{name}</p>'
                  f'<p style="font-size:24px;line-height:1.3;color:{BODY}">{sub}</p></div>')
    st = f'style="color:{BLUE};border-width:3px"'
    el += [f'<x-connector x1="320" y1="235" x2="900" y2="75" route="elbow" {st}></x-connector>',
           f'<x-connector x1="320" y1="235" x2="900" y2="235" {st}></x-connector>',
           f'<x-connector x1="320" y1="235" x2="900" y2="395" route="elbow" {st}></x-connector>',
           f'<x-connector x1="160" y1="110" x2="160" y2="160" head="none" style="color:{MUTED};border-width:2px;border-style:dashed"></x-connector>',
           f'<p style="position:absolute;left:350px;top:150px;width:220px;font-size:24px;font-weight:600;color:{BLUE}">Daily auto-debit</p>',
           f'<p style="position:absolute;left:340px;top:24px;width:240px;font-size:24px;line-height:1.3;color:{MUTED}">sets up the mandate; never holds money</p>']
    body = f"""
{eyebrow("The product")}
{title("The money always sits with a partner, never with us: gold and a liquid fund for the daily habit, bank FDs for goals.")}
<!-- app 0,0,320,110  bank 0,160,320,150  gold 900,0,620,150  fund 900,160,620,150  FD 900,320,620,150 -->
<div style="position:relative;width:1664px;height:470px">{''.join(el)}</div>
{p("The app never holds the money: that would be an unregulated deposit, and fund purchases must come from the saver's own account.", 28, BODY)}
{footer("Sources: BUDS Act 2019; SEBI MF master circular, Mar 2026; SafeGold; AMC and RBI rules.", 8)}
{notes(f'''Say: Follow the money. The platform pays the rider's own bank account. A UPI Autopay mandate, a standing instruction the rider sets once, debits a small amount every day and sends it straight to three partners. The fund house and the bank are regulated; the gold vault partner is not, because nobody regulates digital gold. Digital gold, held in a partner's vault, takes {F('gold_min')}, so it carries the daily habit. A liquid fund, a very short-term debt fund from a fund house, takes {F('sip_min')} a debit and lets the rider take out up to {F('instant_redeem')} a day instantly. A bank FD holds goal money for {F('fd_min')} or more and can back a secured card. Our app is only the window: goals, streaks and offers. It never touches the money, because holding it would be an unregulated deposit, and fund purchases must come from the investor's own account. Likely question: Can the platform deduct savings straight from the payout? Answer: Not into a fund. The payout has to land in the worker's bank first; the worker's own mandate then debits it.''')}
"""
    return section("product", body)


# ================================================================ 9. instrument
@slide("instrument")
def _():
    rows = [
        ["Digital gold", F("gold_min"), f"about {I('gold_margin', fmt='pct')} of each purchase (unverified)", "No: RBI bars loans against gold", "nobody (SEBI caution)", f"{F('gold_spread')} spread + {F('gold_gst')} GST"],
        ["Liquid fund", F("sip_min") + " a debit", f"{F('trail_liquid')} of the balance a year", "Yes: a loan against fund units", "SEBI and AMFI", "a small fund fee"],
        ["Bank FD", F("fd_min") + " minimum", f"about {F('fd_fee')} of the FD (unverified)", "Yes, but only at the same bank", "RBI", "nothing"],
    ]
    body = f"""
{eyebrow("The key design choice")}
{title("The savings instrument decides the business: gold pays for the daily habit, but only an FD can back a card or a loan.")}
{lead(f"Gold is the only home for daily amounts under the {F('sip_min')} fund minimum, and the only one that earns real money per rupee saved. It is also the one we can't lend against, and nobody regulates it.")}
{table(["Where the money sits", "Smallest daily save", "What we earn", "Can back a loan or card?", "Who regulates it", "What the saver pays"], rows, [16, 14, 21, 19, 15, 15])}
{footer("Sources: SafeGold and Jar; AMC factsheets, Aug 2026; RBI gold directions, Jun 2025; SEBI, Nov 2025.", 9)}
{notes(f'''Say: This is the most important design choice, and your brief flagged it. Gold takes {F('gold_min')}, so it is the only home for small daily saves; it pays a distributor about {I('gold_margin', fmt='pct')} of each purchase in our base case (Jar reportedly earned {F('gold_comm')} as a distributor, unverified); and rewards on it are not prohibited, while fund distributors may not offer rebates or gifts. But RBI bars lending against gold, including digital gold, from April 2026, SEBI says it is outside its rules, and the saver pays a {F('gold_spread')} spread plus {F('gold_gst')} GST, so gold sold within a year loses money. A liquid fund earns us only {F('trail_liquid')} a year, about {F('trail_liquid_rs')} on ₹5,000. A bank FD can back a secured card, but only at the same bank. Likely question: Why not funds only, and avoid gold's risk? Answer: Then daily saves must be at least {F('sip_min')}, and savings revenue is close to zero. That is the idea as briefed, and it is weaker in every case.''')}
"""
    return section("instrument", body)


# ================================================================ 10. go-to-market
@slide("gtm")
def _():
    rows = [
        ("Gig", [("Savings buddy", "referral", "Two friends share a goal and see each other's streaks.", "No cash bonus for fund referrals; no pooling."),
                 ("Rider hubs, dark stores", "hub_field", "Field agents with QR codes sign riders up between shifts.", "Staff who explain funds need NISM certificates."),
                 ("Save on payout day", "save_at_source", "The rider's own mandate debits right after the payout lands.", "A platform may not pay into a fund directly.")]),
        ("Self-employed", [("Associations, groups", "associations", "Sessions at trader associations, cooperatives and SHGs.", "No pooling; no fee for fund or insurance sales."),
                           ("Save from UPI sales", "upi_sales", "A mandate timed after the shop's daily UPI collections land.", "Funds need the money in the shop's own bank first."),
                           ("Supplier networks", "supplier", "Distributors who visit shops weekly introduce us.", "Paid only for gold, unless they register as distributors.")]),
    ]
    blocks = []
    for seg, chans in rows:
        cards = "".join(card(f'<p style="font-size:28px;font-weight:600;line-height:1.2;color:{INK}">{name}</p>'
                             f'<p style="font-size:36px;font-weight:600;line-height:1.1;color:{BLUE}">{N(f"ch_{cid}_cac")}</p>'
                             + p("<b>Legal:</b> " + legal, 24, BODY), pad=24, gap=8)
                        for name, cid, how, legal in chans)
        blocks.append(f'<div style="display:flex;gap:20px;align-items:stretch">'
                      f'<p style="width:260px;font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{seg}</p>{cards}</div>')
    lo = min(float(NUM[f"ch_{c}_cac"]["value"]) for c in ("referral", "hub_field", "save_at_source", "associations", "upi_sales", "supplier"))
    hi = max(float(NUM[f"ch_{c}_cac"]["value"]) for c in ("referral", "hub_field", "save_at_source", "associations", "upi_sales", "supplier"))
    lo_id = min(("referral", "hub_field", "save_at_source", "associations", "upi_sales", "supplier"), key=lambda c: float(NUM[f"ch_{c}_cac"]["value"]))
    hi_id = max(("referral", "hub_field", "save_at_source", "associations", "upi_sales", "supplier"), key=lambda c: float(NUM[f"ch_{c}_cac"]["value"]))
    body = f"""
{eyebrow("Go-to-market")}
{title(f"Cheap channels win a first debit for {N(f'ch_{lo_id}_cac')}–{N(f'ch_{hi_id}_cac')} in both halves, under half of what paid ads cost.")}
<div style="display:flex;flex-direction:column;gap:20px">{''.join(blocks)}</div>
<div style="flex:1"></div>
{p(f"<b>The benchmark to beat:</b> paid ads cost {N('ch_paid_digital_cac')} per saver who makes a first debit. All channel costs are assumptions for the pilot to measure.", 24, INK)}
{footer("Source: model, Funnel & CAC tab; legal checks in marketing_ideas.md and own_checks.csv.", 10)}
{notes(f'''Say: How each works. Savings buddy: two friends share a goal and see each other's streaks. Rider hubs: field agents with QR codes sign riders up between shifts. Payout day: the rider's own mandate debits right after the platform payout lands. Associations: sessions at trader associations, cooperatives and self-help groups. UPI sales: a mandate timed after the shop's daily UPI collections land. Suppliers: distributors who visit shops weekly introduce us. These are costs per saver who completes a first auto-debit, fully loaded: field staff or media, KYC at about {CH('hub_field', 'kyc_cost', '₹{:,.0f}')}, the mandate, and any partner fee. For gig workers: savings buddy {N('ch_referral_cac')}, rider hubs {N('ch_hub_field_cac')}, saving on payout day {N('ch_save_at_source_cac')}. For the self-employed: trade associations and self-help groups {N('ch_associations_cac')}, a mandate timed after the shop's daily UPI sales {N('ch_upi_sales_cac')}, and supplier networks {N('ch_supplier_cac')}; market field agents cost {N('ch_market_field_cac')}. Paid ads cost {N('ch_paid_digital_cac')}. Two legal limits shape the self-employed channels: a fund distributor may share commission only with registered sub-distributors, and nobody but a licensed intermediary may be paid for insurance leads. So suppliers and associations can be paid only for gold referrals, or not at all. No payments firm publishes its merchant acquisition cost, so the self-employed channel costs are the least certain numbers in the model; the base case already adds half again to the acquisition part. Likely question: Why not lucky draws or cashback? Answer: A non-bank may not run prize draws, and cashback is barred on fund saving.''')}
"""
    return section("gtm", body)


# ================================================================ 11. revenue
@slide("revenue")
def _():
    groups = [("Gold", ["Savings: gold"], ORANGE), ("Loans", ["Loans (partner)"], BLUE), ("Insurance", ["Insurance"], LBLUE),
              ("Cards, FDs, funds, SIPs", ["Cards", "Savings: FDs", "Savings: liquid fund", "SIPs"], GREY)]
    vals = []
    for y in range(1, 6):
        g = []
        for name, lines, col in groups:
            g.append((name, sum(float(NUM[f"plan_base_rev_pa_y{y}::{l}"]["value"]) for l in lines), col))
            for l in lines:
                _use("num", f"plan_base_rev_pa_y{y}::{l}")
        vals.append(g)
    mx = max(sum(v for _, v, _ in g) for g in vals)
    TRACK = 320
    sc = TRACK / mx
    bars = []
    for y, g in enumerate(vals, 1):
        segs = "".join(f'<div style="height:{v * sc:.0f}px;background:{col}"></div>' for _, v, col in reversed(g) if v * sc >= 1)
        bars.append(f'<div style="width:150px;display:flex;flex-direction:column;gap:8px">'
                    f'<p style="font-size:28px;font-weight:600;color:{INK};text-align:center">{N(f"plan_base_rev_pa_y{y}")}</p>'
                    f'<div style="height:{TRACK}px;display:flex;flex-direction:column;justify-content:flex-end">{segs}</div>'
                    f'<p style="font-size:24px;color:{BODY};text-align:center">Year {y}</p></div>')
    legend = "".join(f'<div style="display:flex;gap:12px;align-items:center"><div style="width:28px;height:28px;background:{col};border-radius:4px"></div>'
                     f'<p style="font-size:24px;color:{INK}">{name}</p></div>' for name, _, col in groups)
    body = f"""
{eyebrow("How we make money")}
{title("Funds and FDs earn almost nothing, so gold and cross-sell have to carry the business.")}
<div style="display:flex;gap:64px;flex:1">
<div style="display:flex;flex-direction:column;gap:12px">
{p("Revenue per active saver per year, by year of the saver's life (base case)", 24, MUTED)}
<div style="display:flex;gap:40px;align-items:flex-end">{''.join(bars)}</div>
</div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;flex-direction:column;gap:12px">{legend}</div>
{kpi(N("plan_base_rev_pa_y2::Savings: liquid fund") + " and " + N("plan_base_rev_pa_y2::Savings: FDs"), "what the liquid fund and the FDs earn per active saver in year 2")}
{kpi(N("plan_bull_rev_pa_y2"), "per active saver in year 2 in the best case, when loans, gold and insurance all sell")}
</div>
</div>
{footer(PLAN_SRC + " Gross revenue to us.", 11)}
{notes(f'''Say: This is revenue per saver who is still active, by year of the saver's life, in the base case. In year 2 it is {N('plan_base_rev_pa_y2')}: gold margin, loan fees and insurance commission make up almost all of it. The liquid fund earns {N('plan_base_rev_pa_y2::Savings: liquid fund')} and FDs {N('plan_base_rev_pa_y2::Savings: FDs')} per saver a year, which is why the brief's claim 5 holds: savings alone does not pay. Loan fees here assume our {F('dlg_cap')} loss cover, which lets lenders pay us about {I('lsp_fee', fmt='pct')} plus {I('dlg_fee_uplift', fmt='pct')} of each loan instead of {I('lsp_fee', fmt='pct')}. In the best case the same saver brings {N('plan_bull_rev_pa_y2')} in year 2. Jar is the reference point: its filed FY25 revenue was {F('jar_roc')}, mostly gold resold; its own 'operating revenue' figure was {F('jar_opr')}, which cannot be rebuilt from the filing; and it still lost {F('jar_loss')}. Likely question: Why does revenue fall after year 2? Answer: Loan take-up saturates among the savers who stay.''')}
"""
    return section("revenue", body)


# ================================================================ 12. unit economics (dark)
@slide("unit")
def _():
    rows = [
        ["Cost to win a customer (CAC)", N("plan_base_cac") + " per saver", N("lf_base_cac") + " per borrower"],
        ["Months to earn back the CAC", f"never; best case {N('plan_bull_payback')}", "never"],
        ["Profit a customer brings (LTV)", N("plan_base_ltv60"), N("lf_base_ltv60")],
        ["LTV ÷ CAC: bear / base / best", f"{N('plan_bear_ltv60_cac')} / {N('plan_base_ltv60_cac')} / {N('plan_bull_ltv60_cac')}",
         f"{N('lf_bear_ltv60_cac')} / {N('lf_base_ltv60_cac')} / {N('lf_bull_ltv60_cac')}"],
        ["Left per customer after CAC", N("plan_base_net_per_customer"), N("lf_base_net_per_customer")],
        ["LTV ÷ CAC by half: gig / self-employed", f"{N('seg_gig_base_ltv60_cac')} / {N('seg_ng_base_ltv60_cac')}", "not split (gig and blue-collar)"],
        ["Capital locked per ₹1 of revenue", N("plan_base_cap_per_rev") + " in deposits", N("lf_base_cap_per_rev") + " of NBFC equity"],
        ["Legal to run this way today?", "Yes", f"No: cover capped at {F('dlg_cap')}"],
    ]
    _use("num", "plan_base_payback"); _use("num", "lf_base_payback")
    ths = "".join(f'<th style="width:{w}%">{h}</th>' for h, w in zip(["Base case unless stated", "Save-first (the plan)", "Lend-first (Bueno as run)"], [40, 30, 30]))
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    tbl = f'<table style="font-family:{SANS};font-size:24px;color:{PAPER};width:1664px"><tr style="background:#2A3D63">{ths}</tr>{trs}</table>'
    body = f"""
{eyebrow("Unit economics, side by side", SAFFRON)}
{title("Neither model pays back in the base case, but save-first loses less per customer and needs no loan book or licence.", PAPER)}
{lead(f"LTV: the profit a customer brings over 60 months after serving costs, discounted at {I('disc_rate', fmt='pct')} a year. CAC: the full cost of winning them.", DARK_SOFT)}
{tbl}
{footer(PLAN_SRC + " Lend-first from founder data.", 12, DARK_SOFT)}
{notes(f'''Say: Here is the honest comparison. Save-first costs {N('plan_base_cac')} to win a saver who makes a first debit; lend-first cost {N('lf_base_cac')} to win a borrower. Neither earns back its CAC within five years in the base case. The saver brings {N('plan_base_ltv60')} of discounted profit, a loss, because serving a daily saver costs more than the base-case cross-sell earns. The borrower brings {N('lf_base_ltv60')}. After paying to win them, save-first is at {N('plan_base_net_per_customer')} a customer and lend-first at {N('lf_base_net_per_customer')}. The real difference is capital and legality. Save-first locks {N('plan_base_cap_per_rev')} of loss-cover deposit per rupee of revenue; lend-first needs {N('lf_base_cap_per_rev')} of equity in our own NBFC, because the way Bueno ran it is now barred. In the best case save-first reaches {N('plan_bull_ltv60_cac')} times CAC against {N('lf_bull_ltv60_cac')}. Likely question: So why flip at all? Answer: The flip is legal, needs little capital and has the higher ceiling. It is still a bet on the next slide's three assumptions.''')}
"""
    return section("unit", body, bg=INK, fg=PAPER)


# ================================================================ 13. what has to be true
@slide("wtbt")
def _():
    def tag(nid):
        v = float(NUM[nid]["value"])
        return N(nid) + (": must hold" if v < 3 else (": matters" if v < 4 else ": helps"))
    rows = [
        ["1. Cross-sell sells", f"{N('plan_base_m12_borrowed')} borrowed, {N('plan_base_m12_insured')} insured by month 12",
         f"{N('plan_bull_m12_borrowed')} and {N('plan_bull_m12_insured')}", tag("wtbt_all_bull_except_cross_sell"),
         f"Offer loans from month {I('loan_start')} and cover from month {I('ins_start')}; count take-up"],
        ["2. Debits cost paise", f"{I('cost_debit', fmt='inr')} a debit", I("cost_debit", "bull", fmt="inr"), tag("wtbt_all_bull_except_debit_cost"),
         f"Sign a payment contract at {I('cost_debit', 'bull', fmt='inr')} or less before launch"],
        ["3. Savers stay", f"{N('plan_base_m12_still')} still saving at a year", N("plan_bull_m12_still"), tag("wtbt_all_bull_except_retention"),
         "Track every saver monthly, each half separately"],
        ["4. They save more", f"{N('plan_base_m1_saved')} a month", N("plan_bull_m1_saved"), tag("wtbt_all_bull_except_amount"),
         "Measure money saved per active saver"],
        ["5. Cheap to win", N("plan_base_cac") + " per saver", N("plan_bull_cac"), tag("wtbt_all_bull_except_cac"),
         "Measure CAC channel by channel"],
    ]
    body = f"""
{eyebrow("What has to be true")}
{title("Cross-sell is the one assumption that must hold; a one-year pilot can test it and the other four.")}
{table(["Assumption", "Base today", "Needed (best case)", "LTV ÷ CAC if only this one misses", "Pilot test"], rows, [17, 21, 14, 17, 31])}
{p(f"With every assumption at its best case, LTV ÷ CAC is {N('plan_bull_ltv60_cac')}. Only cross-sell, falling back to base on its own, pulls it below 3; debits and retention each cost about 2 points.", 28, INK)}
{footer(PLAN_SRC + " Both halves; 'Needed' = the best-case inputs.", 13)}
{notes(f'''Say: This is the slide the pilot is built around. We grouped every input into five assumptions. With all of them at their best case, LTV divided by CAC is {N('plan_bull_ltv60_cac')}. Then we let one group at a time fall back to base, each half to its own base values. Without cross-sell it falls to {N('wtbt_all_bull_except_cross_sell')}: that is the one that must hold. With debits at {I('cost_debit', fmt='inr')} instead of {I('cost_debit', 'bull', fmt='inr')} it falls to {N('wtbt_all_bull_except_debit_cost')}; with base retention, to {N('wtbt_all_bull_except_retention')}. Adding the self-employed made the best case sturdier: they save more and stay longer, so it survives a miss on debits or retention alone. No single assumption rescues the base case: cross-sell at its best case with everything else at base gives only {N('wtbt_only_cross_sell_bull')}. Likely question: Isn't 'everything at best case' wishful? Answer: Yes. That is why no money should go past the pilot until the month-12 readings show cross-sell working.''')}
"""
    return section("wtbt", body)


# ================================================================ 14. path to $100M
@slide("path")
def _():
    base = [float(NUM[f"plan_base_path_y{y}_usd_m"]["value"]) for y in range(1, 11)]
    bull = [float(NUM[f"plan_bull_path_y{y}_usd_m"]["value"]) for y in range(1, 11)]
    for y in range(1, 11):
        _use("num", f"plan_base_path_y{y}_usd_m"); _use("num", f"plan_bull_path_y{y}_usd_m")
    H = 340
    sc = H / max(bull)
    groups = "".join(
        f'<div style="width:96px;display:flex;flex-direction:column;gap:8px">'
        f'<div style="height:{H}px;display:flex;gap:6px;align-items:flex-end;justify-content:center">'
        f'<div style="width:36px;height:{max(bull[y - 1] * sc, 2):.0f}px;background:{BLUE}"></div>'
        f'<div style="width:36px;height:{max(base[y - 1] * sc, 2):.0f}px;background:{GREY}"></div></div>'
        f'<p style="font-size:24px;color:{BODY};text-align:center">Y{y}</p></div>' for y in range(1, 11))
    body = f"""
{eyebrow("Market and the path to $100M")}
{title(f"The best case reaches about {N('plan_bull_path_y10_usd_m')} a year by year 10, but the base case only {N('plan_base_path_y10_usd_m')}.")}
<div style="display:flex;gap:56px;flex:1">
<div style="display:flex;flex-direction:column;gap:12px">
{p("Revenue per year: best case (blue) and base case (grey)", 24, MUTED)}
<div style="display:flex;gap:12px">{groups}</div>
</div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">
{kpi(N("plan_bull_path_y10_usd_m"), f"in year 10, best case, from {N('plan_bull_path_y10_active_m')} active savers; base case {N('plan_base_path_y10_usd_m')}")}
{kpi(N("lever_A+Cgigonly_bull_y10"), "in year 10, best case, with gig workers only: the self-employed half is what reaches $100M")}
{kpi(F("udyam_micro"), f"micro enterprises on the Udyam portal, and {F('gig_2030')} gig workers expected by 2029–30: the pool is not the limit")}
</div>
</div>
{footer(PLAN_SRC + f" Growth plan: inputs_path.csv; {F('usd_inr')} per US$.", 14)}
{notes(f'''Say: Bottom-up: savers acquired each year, half gig and half self-employed, times revenue per saver by year of their life, times how many stay. The growth plan is an assumption: {PY(1, 'new_activated')} savers in year 1, rising to {PY(10, 'new_activated')} new savers a year by year 10, with CAC rising as channels saturate. In the best case revenue reaches {N('plan_bull_path_y10_usd_m')} in year 10 from {N('plan_bull_path_y10_active_m')} active savers, and first passes $100M in {N('lever_A+C_bull_first100')}; in the base case {N('plan_base_path_y10_usd_m')}. With gig workers only, the best case stops at {N('lever_A+Cgigonly_bull_y10')}. The pool is not the constraint: India had {F('gig_fy25')} gig workers in FY25, heading to {F('gig_2030')}, and {F('udyam_micro')} micro enterprises are registered on Udyam. Dollars at {F('usd_inr')}. Likely question: How much capital does the best case need? Answer: It peaks at {N('plan_bull_peak_cr')}; the base case never turns cash-positive, which is the point of the pilot.''')}
"""
    return section("path", body)


# ================================================================ 15. competition
@slide("competition")
def _():
    W, H = 1100, 520
    chips = [(40, 16, "Jar", f"digital gold; {F('jar_users')} registered"),
             (40, 128, "Bachatt", "our self-employed half; sells loans"),
             (40, 240, "Us", "gig + self-employed; edge = credit"),
             (40, 400, "PhonePe, Paytm, BharatPe", f"PhonePe alone: {F('phonepe_merchants')} merchants"),
             (600, 16, "KreditBee, Kissht", "credit first, thin-file borrowers"),
             (600, 400, "Moneyview, Fibe, Navi", "credit first, salaried borrowers")]
    el = [f'<div style="position:absolute;left:549px;top:0;width:2px;height:{H}px;background:{MUTED}"></div>',
          f'<div style="position:absolute;left:0;top:369px;width:{W}px;height:2px;background:{MUTED}"></div>']
    for l, t, name, fact in chips:
        us = name == "Us"
        el.append(f'<div style="position:absolute;left:{l}px;top:{t}px;width:460px;background:{INK if us else CARD};border:2px solid {INK if us else "#E3DDD0"};'
                  f'border-radius:14px;padding:12px 18px"><p style="font-size:28px;font-weight:600;color:{PAPER if us else INK}">{name}</p>'
                  f'<p style="font-size:24px;line-height:1.3;color:{DARK_SOFT if us else BODY}">{fact}</p></div>')
    body = f"""
{eyebrow("Competition")}
{title("Jar and Bachatt own daily saving and payment apps own the shopkeeper, so our only edge would be credit.")}
<div style="display:flex;gap:48px;flex:1">
<div style="display:flex;flex-direction:column;gap:8px">
<div style="display:flex;width:{W}px"><p style="flex:1;font-size:24px;font-weight:600;color:{MUTED}">SELLS SAVING FIRST</p><p style="flex:1;font-size:24px;font-weight:600;color:{MUTED};text-align:right">SELLS CREDIT FIRST</p></div>
<!-- quadrant lines x=549, y=369; chips 460 wide -->
<div style="position:relative;width:{W}px;height:{H}px">{''.join(el)}</div>
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:24px">
{p("<b>Above the line:</b> gig workers and the self-employed. <b>Below:</b> merchants' payment apps and salaried borrowers.", 24, BODY)}
{p("<b>Where we could win:</b> lending to savers better than a loan app can, using the saving streak plus platform payout data.", 28, INK)}
{p("<b>Likely conflicted investors:</b> Accel, Lightspeed and Info Edge (Bachatt); Tiger Global, Arkam and Tribe (Jar).", 24, BODY)}
</div>
</div>
{footer("Sources: RoC filings via Entrackr and Inc42; company releases (market_benchmarks.csv).", 15)}
{notes(f'''Say: Jar owns daily gold saving: {F('jar_users')} registered users, but a {F('jar_loss')} loss in FY25 even after two profitable quarters. Bachatt is aimed squarely at our self-employed half: daily fund saving for merchants earning {F('bachatt_band')} a month (its stated target); it already sells loans and cards, and Accel, Lightspeed and Info Edge put {F('bachatt_raise')} into it in March 2026. Payment apps own the shopkeeper relationship: PhonePe alone has {F('phonepe_merchants')} registered merchants, and India has {F('upi_merchants')} UPI merchants. PhonePe already offers daily gold saving built with Jar, and Paytm and Google Pay offer gold and FDs. So the saving habit is not a moat. The only defensible edge would be credit: lending to savers better than a loan app can, because we see the saving streak and, with a platform partner, the payout record. Research shows delivery-app data predicts creditworthiness for people with no credit history (RappiCard, Mexico); no study yet shows the same for saving in India. Likely question: What stops Bachatt from targeting riders? Answer: Nothing. Speed and a platform partnership are the only answers, and neither is a moat.''')}
"""
    return section("competition", body)


# ================================================================ 16. pre-mortem
@slide("premortem")
def _():
    fee_total = float(INP["lsp_fee"]["base"]) + float(INP["dlg_fee_uplift"]["base"])
    _use("input", "lsp_fee.base"); _use("input", "dlg_fee_uplift.base")
    ft = f"{fee_total * 100:.0f}%"
    rows = [
        ["Savers stop saving", f"under {N('plan_base_m3_still')} still saving at month 3", "Move debits to payout day; stop spending on acquisition"],
        ["Fees stay thin", f"lenders offer under {ft} of each loan with our cover", "Sell insurance apart from loans; test an own NBFC later"],
        ["Gold rules tighten", "gold becomes a security, or rewards on it are barred", f"Move daily saves into {F('sip_min')}+ fund debits"],
        [f"Losses beat the {F('dlg_cap')} cover", f"over {I('loan_dpd90', fmt='pct')} (gig) or {I('loan_dpd90', fmt='pct', seg='ng')} (self-employed) of first loans 90+ late", "Smaller first loans; stricter eligibility"],
        ["Two customers split the team", "the halves' month-6 readings diverge", "Put the next year's money into the half that works"],
        ["Debits cost rupees, not paise", f"payment quotes above {I('cost_debit', 'bull', fmt='inr')} a debit", "Switch to one debit a week"],
        ["A platform or big app does it", "PhonePe already offers daily gold with Jar", "Partner with a platform instead of competing"],
    ]
    body = f"""
{eyebrow("Pre-mortem")}
{title("How this fails: savers leave, fees stay thin, gold rules tighten, or a platform does it itself.")}
{table(["How it fails", "The early warning", "What we do"], rows, [25, 41, 34])}
{footer("Warning levels are the model's base-case values (see What has to be true).", 16)}
{notes(f'''Say: Assume it is 2028 and this failed. The likeliest reasons, each with the signal we would see first. Savers stop: if under {N('plan_base_m3_still')} are still saving at month 3, we are below even the base case. Fees stay thin: our base assumes lenders pay about {ft} of each loan with our {F('dlg_cap')} cover; Moneyview's partner fees are about {F('mv_fee')} of partner loans, but it lends to people earning far more. Gold rules tighten: the Finance Ministry is reportedly consulting on making digital gold a security. Losses beat the cover: our base assumes {I('loan_dpd90', fmt='pct')} of gig first loans and {I('loan_dpd90', fmt='pct', seg='ng')} of self-employed first loans go 90+ days late, against {F('loans_90plus')} for small personal loans and {F('ubl_90plus')} for small business loans to the self-employed; PM SVANidhi street-vendor loans ran {F('svanidhi_npa')} bad, and Delhi microfinance has {F('delhi_mfi_par180')} of its book 180+ days late. Moneyview actually paid {F('mv_dlg_paid')} of covered loans in FY26. Two customers also means two sales approaches for a small team: if the halves' readings diverge by month 6, the money goes to the one that works. Debits: the list price is {F('debit_list')} a debit. And a big app could do this: PhonePe already offers daily gold with Jar. Likely question: Which of these worries you most? Answer: Retention. Riders change platforms about every {F('rider_tenure')}, and any UPI app can now move their mandate.''')}
"""
    return section("premortem", body)


# ================================================================ 17. pilot
@slide("pilot")
def _():
    rows = [
        ["Still saving after a year", N("plan_base_m12_still"), N("plan_bull_m12_still")],
        ["Active savers who have borrowed", N("plan_base_m12_borrowed"), N("plan_bull_m12_borrowed")],
        ["Active savers with insurance", N("plan_base_m12_insured"), N("plan_bull_m12_insured")],
        ["Cost per debit", I("cost_debit", fmt="inr"), I("cost_debit", "bull", fmt="inr")],
        ["Cost to win a saver", N("plan_base_cac"), N("plan_bull_cac")],
        ["Saved per active saver a month", N("plan_base_m1_saved"), N("plan_bull_m1_saved")],
    ]
    body = f"""
{eyebrow("The next step")}
{title(f"The next step is a one-year pilot with {PY(1, 'new_activated')} savers in Delhi NCR, half of them gig workers, to test all five assumptions.")}
<div style="display:flex;gap:64px;flex:1">
<div style="width:520px;display:flex;flex-direction:column;justify-content:space-between">
{kpi(N("plan_base_need_y1_cr"), f"to run it for a year (base case); {N('plan_bull_need_y1_cr')} to {N('plan_bear_need_y1_cr')} across cases")}
{kpi(N("plan_base_y1_fixed_opex_cr"), "of that is the team and fixed costs")}
{kpi(N("plan_base_y1_cac_spend_cr"), f"is the cost of winning {PY(1, 'new_activated')} savers")}
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:16px">
{p("Readings at month 12: stop at the base case, go at the best case", 28, INK, 600)}
{table(["Month-12 reading", "Stop if about", "Go if at least"], rows, [50, 25, 25], width=1080)}
{p("Read each number for each half separately. Partners to sign first: a platform, a gold vault, a fund house, a bank, a lender, an insurer, a payment company.", 24, BODY)}
</div>
</div>
{footer(PLAN_SRC + " Year 1 of the growth plan.", 17)}
{notes(f'''Say: The next step is not a big round. It is a one-year pilot with {PY(1, 'new_activated')} savers in Delhi NCR: half gig workers through one platform partner, half shopkeepers and the self-employed through markets, suppliers and associations. In the base case it costs {N('plan_base_need_y1_cr')}: {N('plan_base_y1_fixed_opex_cr')} is the team and fixed costs, and {N('plan_base_y1_cac_spend_cr')} is winning the savers. At month 12 we read six numbers. If they sit at the base case, for example {N('plan_base_m12_still')} still saving after a year and {N('plan_base_m12_borrowed')} of active savers borrowing, we stop. If they reach the best case, {N('plan_bull_m12_still')} and {N('plan_bull_m12_borrowed')}, the model says LTV is {N('plan_bull_ltv60_cac')} times CAC and we raise to scale. Cost per debit is settled before launch: a contract at {I('cost_debit', 'bull', fmt='inr')} or less, or we switch to weekly debits. Likely question: Could a smaller pilot answer this? Answer: Sign-up and saving, yes. But loans and insurance only start at months {I('loan_start')} and {I('ins_start')}, so cross-sell needs a year and enough savers who stay.''')}
"""
    return section("pilot", body)


# ================================================================ Appendix
AP = dict(bg=SAND)


def ap_head(label, t):
    return eyebrow(f"Appendix {label}") + "\n" + title(t)


@slide("a1_regmap")
def _():
    rows = [["Fund distribution", "AMFI registration + certified staff", "AMFI", "weeks", F("arn_fee") + " + GST"],
            ["Digital gold", "none: we distribute a vault partner", "nobody", "contract", "commercial"],
            ["Bank FDs, FD card", "a referral tie-up with one bank", "the bank", "contract", "commercial"],
            ["Loans we source", "contract; the lender lists us with RBI", "the lender", "contract", f"up to {F('dlg_cap')} as cash cover"],
            ["Own NBFC (lever B)", "RBI certificate of registration", "RBI", F("nbfc_time"), F("nof") + " minimum"],
            ["Insurance", "IRDAI corporate agent", "IRDAI", F("ca_time") + "*", F("ca_networth") + " net worth"],
            ["Auto-debits", "an RBI-authorised payment company", "RBI, NPCI", "days", F("debit_list") + " a debit (list)"]]
    body = f"""
{ap_head("A1", "Each product needs a different licence or partner; only an own NBFC needs real capital.")}
{table(["Product", "Licence or partner", "Granted by", "Time", "Cost or capital"], rows, [19, 35, 12, 15, 19], head_bg=AP_HEAD)}
{footer("* unverified. Sources: regulatory_map.md and regulation_rails.csv (AMFI, RBI, IRDAI, NPCI, Cashfree).", "A1")}
{notes(f'''The distribution model needs an AMFI registration, IRDAI corporate-agent status and contracts with lenders, a gold vault partner and a bank. Only lever B, an own NBFC, needs real capital: {F('nof')} minimum, and in practice equity near a third of the loan book. The FD-backed card must come from the same bank that holds the FD.''')}
"""
    return section("a1_regmap", body, **AP)


@slide("a2_outputs")
def _():
    rows = [["Cost to win a saver (CAC)", N("plan_bear_cac"), N("plan_base_cac"), N("plan_bull_cac")],
            ["Months to earn back CAC", "never", "never", N("plan_bull_payback")],
            ["LTV over 36 months", N("plan_bear_ltv36"), N("plan_base_ltv36"), N("plan_bull_ltv36")],
            ["LTV over 60 months", N("plan_bear_ltv60"), N("plan_base_ltv60"), N("plan_bull_ltv60")],
            ["LTV ÷ CAC, 36 / 60 months", f"{N('plan_bear_ltv36_cac')} / {N('plan_bear_ltv60_cac')}", f"{N('plan_base_ltv36_cac')} / {N('plan_base_ltv60_cac')}",
             f"{N('plan_bull_ltv36_cac')} / {N('plan_bull_ltv60_cac')}"],
            ["Revenue per active saver, yrs 1 / 2 / 5", f"{N('plan_bear_rev_pa_y1')} / {N('plan_bear_rev_pa_y2')} / {N('plan_bear_rev_pa_y5')}",
             f"{N('plan_base_rev_pa_y1')} / {N('plan_base_rev_pa_y2')} / {N('plan_base_rev_pa_y5')}", f"{N('plan_bull_rev_pa_y1')} / {N('plan_bull_rev_pa_y2')} / {N('plan_bull_rev_pa_y5')}"],
            ["LTV ÷ CAC: gig half / self-employed half", f"{N('seg_gig_bear_ltv60_cac')} / {N('seg_ng_bear_ltv60_cac')}",
             f"{N('seg_gig_base_ltv60_cac')} / {N('seg_ng_base_ltv60_cac')}", f"{N('seg_gig_bull_ltv60_cac')} / {N('seg_ng_bull_ltv60_cac')}"],
            ["Revenue in year 10", N("plan_bear_path_y10_usd_m"), N("plan_base_path_y10_usd_m"), N("plan_bull_path_y10_usd_m")],
            ["Peak capital over 10 years", N("plan_bear_peak_cr"), N("plan_base_peak_cr"), N("plan_bull_peak_cr")]]
    _use("num", "plan_bear_payback"); _use("num", "plan_base_payback")
    body = f"""
{ap_head("A2", "Model outputs: the plan, half gig and half self-employed, in the bear, base and best cases.")}
{table(["Per activated saver unless stated", "Bear", "Base", "Best case"], rows, [37, 21, 21, 21], head_bg=AP_HEAD)}
{footer(PLAN_SRC + f" LTV = contribution margin discounted {I('disc_rate', fmt='pct')} a year.", "A2")}
{notes(f'''All outputs are from the Outputs tab of savings_first_model.xlsx. The workbook's formulas are checked against a separate Python engine on {VERIFY['checked']:,} values across {VERIFY['cases']} cases. Peak capital in the bear and base cases is large because those cases never turn cash-positive while the growth plan keeps spending, which is exactly why nothing should scale before the pilot readings.''')}
"""
    return section("a2_outputs", body, **AP)


@slide("a3_levers")
def _():
    names = [("As briefed", "Savings and distribution only"), ("A", "A. Take 5% of loan losses"), ("B", "B. Own NBFC from year 3"),
             ("C", "C. Add digital gold"), ("A+C", "A + C: the plan"), ("B+C", "B + C"), ("A+Cgigonly", "The plan, gig workers only")]
    rows = [[lab, N(f"lever_{k.replace(' ', '')}_base_ltv60_cac"), N(f"lever_{k.replace(' ', '')}_bull_ltv60_cac"),
             N(f"lever_{k.replace(' ', '')}_bull_y10"), N(f"lever_{k.replace(' ', '')}_bull_first100")] for k, lab in names]
    body = f"""
{ap_head("A3", "Four levers tested: none makes the base case pay back; they raise the ceiling.")}
{table(["Lever (daily saving; half gig, half self-employed)", "LTV ÷ CAC, base", "LTV ÷ CAC, best", "Year 10 revenue, best", "First year at $100M, best"], rows, [32, 15, 15, 17, 21], head_bg=AP_HEAD)}
{footer("Source: model, Levers tab (levers.py); lever inputs sourced in levers.csv.", "A3")}
{notes(f'''Lever A, a {F('dlg_cap')} loss cover, lets lenders pay us about {I('lsp_fee', fmt='pct')} plus {I('dlg_fee_uplift', fmt='pct')} of each loan, against {F('lsp_nodlg')} for plain sourcing; Moneyview's partner fees are about {F('mv_fee')} of partner loans. Lever B, an own NBFC, pays about {I('nbfc_cof', fmt='pct')} to borrow and needs equity of about a third of its book; small digital NBFCs lose money for their first years. Lever C, gold, earns about {I('gold_margin', fmt='pct')} of each purchase. The last row shows what the self-employed half adds: with gig workers only, the plan's best case is {N('lever_A+Cgigonly_bull_ltv60_cac')} and {N('lever_A+Cgigonly_bull_y10')} in year 10. Salaried blue-collar workers through employers were tested earlier and dropped: flexi staff churn {F('flexi_churn')} a quarter.''')}
"""
    return section("a3_levers", body, **AP)


@slide("a4_bueno")
def _():
    rows = [["Loans in the best month", F("bueno_loans"), "founder CV"], ["Applicants approved", F("bueno_approval"), "founder data"],
            ["First loans 90+ days late", F("bueno_dpd"), "founder data"], ["Typical first loan", F("bueno_ticket"), "founder data (midpoint)"],
            ["Yearly rate paid by borrowers, with fees", F("bueno_irr"), "founder data"], ["Yearly rate paid to the partner NBFC", F("bueno_nbfc"), "founder data"],
            ["Loans sourced through platforms", F("bueno_platform"), "founder data"], ["Platform data fee per loan", F("bueno_fee"), "founder data"],
            ["Repayers who took a second loan", F("bueno_repeat"), "founder data"]]
    body = f"""
{ap_head("A4", "Bueno's numbers, as the founder gave them, drive the lending-first comparison.")}
{table(["Bueno, 2019–22", "Value", "Basis"], rows, [55, 20, 25], head_bg=AP_HEAD)}
{footer("Source: founder data, confirmed 30 Sep 2026 (tables/inputs_founder_bueno.csv).", "A4")}
{notes('''These are the founder's numbers, confirmed on 30 September 2026. Where not given, the model assumes: KYC and bureau cost per applicant in the founder's range of ₹20-60; repeat-loan late rate of 1-2%; nearly all of a loan still owed when it went 90+ days late; about half of that recovered. The partner NBFC funded the loans and Bueno covered 100% of losses, a structure now capped at 5%.''')}
"""
    return section("a4_bueno", body, **AP)


@slide("a5_marketing")
def _():
    rows = [["1. Save on payout day ★", N("ch_save_at_source_cac"), "Payout goes to the rider's bank; their own mandate debits it"],
            ["2. Rider hubs, dark stores ★", N("ch_hub_field_cac"), "Staff who explain funds need NISM certification; no sign-up gifts"],
            ["3. Savings buddy ★", N("ch_referral_cac"), "No cash referral bonus for funds; no pooling (a chit fund)"],
            ["4. Local creators, WhatsApp", N("ch_creators_cac"), "Education only: no fund tips or return claims (SEBI)"],
            ["5. Festival and goal campaigns", "lowers other CACs", "No lucky draws or 'save and win' prizes"],
            ["6. Fleet owners, staffing firms", "not modelled", "Payroll saving into funds is still a SEBI draft"],
            ["7. Women-first", "not modelled", f"Women are {F('rider_women')} of riders: a later segment"],
            ["8. Cash top-ups at kiranas", "dropped", "Only a bank's business correspondent may take cash"]]
    body = f"""
{ap_head("A5", "Eight ways to reach gig savers cheaply, each checked against Indian law.")}
{table(["Idea (★ = on slide 10)", "CAC per first debit", "Legal check"], rows, [33, 19, 48], head_bg=AP_HEAD)}
{footer(f"Paid ads, the benchmark: {N('ch_paid_digital_cac')}. Details: research/marketing_ideas.md.", "A5")}
{notes('''The three starred channels are on slide 10. Everything here grows through convenience and habit, not prizes: the Prize Chits Act bans lucky draws by non-banks, the Chit Funds Act covers any pooled savings circle, fund distributors may not offer rebates or gifts, and the app may never hold cash or savings. Reviving old Bueno borrowers is not on the list: that data belongs to BetterPlace and was collected for lending, so using it here would break purpose limits under the IT Act rules and the DPDP Act.''')}
"""
    return section("a5_marketing", body, **AP)


@slide("a5b_marketing_ng")
def _():
    rows = [["1. Associations, cooperatives, SHGs", N("ch_associations_cac"), "No pooling (a chit fund); no fee for fund or insurance sales"],
            ["2. Save from daily UPI sales", N("ch_upi_sales_cac"), "Small merchants' UPI money lands in their own bank; the mandate debits it after"],
            ["3. Supplier and distributor networks", N("ch_supplier_cac"), "Paid only for gold referrals, unless registered as fund sub-distributors"],
            ["4. Field agents in markets", N("ch_market_field_cac"), "Staff who explain funds need NISM certificates; no sign-up gifts"]]
    body = f"""
{ap_head("A5b", "Four ways to reach the self-employed, each checked against Indian law.")}
{table(["Idea", "CAC per first debit", "Legal check"], rows, [33, 19, 48], head_bg=AP_HEAD)}
{p(f"No payments firm publishes its merchant acquisition cost, and no product yet saves from a merchant's daily UPI sales. These are the least certain numbers in the model; the base case adds half again to their acquisition cost.", 24, BODY)}
{footer("Sources: own_checks.csv (AMFI, Insurance Act s.40, RBI PA directions); nongig.csv.", "A5b")}
{notes(f'''The legal constraint that shapes these channels: under AMFI rules a fund distributor may share commission only with sub-distributors who hold their own registration, and under section 40 of the Insurance Act nobody may be paid for insurance leads except a licensed agent or intermediary. So a supplier's salesmen or a trade association can be paid only for gold referrals, which are unregulated, unless they register. Payment aggregators may pay out on a merchant's instruction, but fund purchases must come from the merchant's own bank account, so saving from UPI sales is a mandate timed after the day's collections land. Supplier-network finance that exists today (udaan, HUL) is trade credit for stock, which the plan does not offer.''')}
"""
    return section("a5b_marketing_ng", body, **AP)


@slide("a6_comps")
def _():
    rows = [["Jar (India)", f"{F('jar_users')} registered users still meant a {F('jar_loss')} loss in FY25; its margin is the gold spread"],
            ["Stable Money (India)", f"FDs alone don't pay: {F('stable_users')} investors, {F('stable_rev')} of FY25 revenue"],
            ["Fi Money (India)", f"Raised {F('fi_raised')}, then stopped banking when loan distribution shrank"],
            ["Chime (US)", f"Earns from the payroll flow it sees: payments were {F('chime_pay')} of FY25 revenue"],
            ["M-Shwari, Fuliza (Kenya)", f"Credit at the point of spending grew to {F('fuliza_x')} savings-linked loans"],
            ["TymeBank (S. Africa)", f"Savings first, lending later: {F('tyme_years')} to a first monthly profit"],
            ["GCash (Philippines)", f"Wallet first; credit became the money-maker, with {F('gcash_borrowers')} of users borrowing"],
            ["Nubank (Brazil)", f"Card-first worked against {F('brazil_revolve')} card rates; India has {F('india_cards')} cards, mostly at 4 banks"]]
    body = f"""
{ap_head("A6", "Comparables: one lesson each.")}
{table(["Company", "The lesson"], rows, [23, 77], head_bg=AP_HEAD)}
{footer("Sources: market_benchmarks.csv (filings, company results, press, NBER and CGAP).", "A6")}
{notes(f'''The pattern: savings and wallets reach people cheaply, but money comes from credit or from the flow of payments. Every savings-first player that lasted added lending. Nubank's card-first path does not transfer: in India only banks and RBI-approved NBFCs can issue cards, and thin-file workers are best reached with an FD-secured card. On whether saving predicts repayment, the best evidence is correlation only: savings-linked self-help-group loans run an NPA of {F('shg_npa')} for microfinance.''')}
"""
    return section("a6_comps", body, **AP)


QA = [
    ("Why can't PhonePe or Jar just do this?", lambda: "They could, and PhonePe already offers daily gold with Jar. Our only defensible edge would be credit: lending to savers better than a loan app, using the saving streak and payout data. The pilot must show it."),
    ("The base case loses money. Why fund anything?", lambda: f"Fund only the pilot: {N('plan_base_need_y1_cr')} for a year, with stop and go readings set in advance. Scale only if the three must-hold assumptions show up."),
    ("Why daily debits when each costs money?", lambda: f"The daily habit is the thesis. It works only at {I('cost_debit', 'bull', fmt='inr')} a debit or less; the list price is {F('debit_list')}. If we can't get that, we switch to weekly."),
    ("Isn't digital gold a regulatory time bomb?", lambda: f"It is a real risk: unregulated, with a framework under consultation. Plan B is {F('sip_min')}+ fund debits. Gold can't back a loan in any case."),
    ("What stops savers leaving?", lambda: "Nothing structural: any UPI app can now show and move a mandate. Retention is must-hold assumption 3; payday timing and goals are our levers."),
    ("Do savers really make better borrowers?", lambda: f"Not proven in India. Savings-linked group loans show NPA of {F('shg_npa')} for microfinance, but that is correlation. The pilot measures late loans against the {F('loans_90plus')} benchmark."),
    ("Why not lend from your own NBFC?", lambda: f"It needs {F('nof')} and equity near a third of the book, and small NBFCs lose money for years. Tested as lever B: best case {N('lever_B_bull_ltv60_cac')} against {N('plan_bull_ltv60_cac')} for the plan."),
    ("What's the moat?", lambda: "Weak, honestly. Candidates: platform partnerships, a marketplace where lenders compete for pre-qualified savers, and referral loops without cash bonuses. None is proven."),
    ("How big can this get?", lambda: f"Best case {N('plan_bull_path_y10_usd_m')} in year 10 from {N('plan_bull_path_y10_active_m')} active savers. Gig workers alone stop at {N('lever_A+Cgigonly_bull_y10')}."),
    ("What kind of company is this?", lambda: f"A distributor and software company, not a lender: fund distributor, insurance agent, gold distributor and loan service provider with a {F('dlg_cap')} loss cover. Thin margins; valued like distribution."),
    ("Why you?", lambda: f"I ran Bueno: {F('bueno_loans')} loans a month to this segment. Before that, credit policy at Capital One, loss models for Citi at EXL, Encore Capital, and analytics at Swiggy."),
    ("Why did Bueno end?", lambda: "BetterPlace acquired it in May 2023. The lessons: first loans lost money, platforms were the best channel, and the employer channel was too small."),
    ("What does the loss cover cost?", lambda: f"About {F('dlg_cap')} of each covered loan held as cash: {N('plan_base_cap_per_rev')} per ₹1 of year-1 revenue. Lenders then pay about {I('lsp_fee', fmt='pct')} + {I('dlg_fee_uplift', fmt='pct')} of each loan, not {I('lsp_fee', fmt='pct')}."),
    ("Why two customer groups from day one?", lambda: f"The self-employed save more and stay longer, lifting the best case from {N('lever_A+Cgigonly_bull_ltv60_cac')} to {N('plan_bull_ltv60_cac')} times CAC. The cost: two sales approaches and riskier borrowers. The pilot reads each half separately."),
    ("Why would a platform partner with you?", lambda: "A free savings benefit for riders as the Labour Codes push social security, and Bueno's Swiggy relationship. Unproven: the pilot needs one platform to sign."),
]


def qa_slide(n, qs):
    sid = f"a{6 + n}_qa{n}"
    _cur[0] = sid
    items = "".join(card(p(f"<b>{q}</b>", 28, INK) + p(a(), 24, BODY), pad=24, flex="", gap=8) for q, a in qs)
    body = f"""
{ap_head(f"A{6 + n}", f"The hardest VC questions, with answers ({n} of 3).")}
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:20px">{items}</div>
{footer("Numbers: model outputs and sourced facts used elsewhere in this deck.", f"A{6 + n}")}
{notes("These answers are deliberately short. The long versions sit in the speaker notes of the main slides.")}
"""
    return sid, section(sid, body, **AP)


for n in (1, 2, 3):
    SLIDES_OUT.append(qa_slide(n, QA[(n - 1) * 5: n * 5]))


def sources_slides(per=10):
    """One row per source row-id group, listing the facts it supports on the slides."""
    used = []
    for sid, ids in USED.items():
        for u in ids:
            k, v = u.split(":", 1)
            if k == "fact" and v not in used:
                used.append(v)
    groups: dict[str, dict] = {}
    for fid in used:
        r = FACT[fid]
        key = "founder" if r["source_ids"] == "founder" else r["source_ids"]
        g = groups.setdefault(key, {"src": "Founder: CV, and data confirmed 30 Sep 2026" if key == "founder" else r["source_short"], "facts": []})
        if r["display"] not in g["facts"]:
            g["facts"].append(r["display"])
    rows = []
    for key, g in groups.items():
        facts = "; ".join(g["facts"])
        if len(facts) > 56:
            facts = facts[:56].rsplit("; ", 1)[0] + "; …"
        rows.append([g["src"], key, facts])
    chunks = [rows[i:i + per] for i in range(0, len(rows), per)]
    out = []
    for n, chunk in enumerate(chunks, 1):
        sid = f"a{9 + n}_sources{n}"
        _cur[0] = sid
        body = f"""
{ap_head(f"A{9 + n}", f"Sources for the facts on these slides ({n} of {len(chunks)}).")}
{table(["Source and date", "Row id", "Facts it supports on the slides"], chunk, [36, 18, 46], head_bg=AP_HEAD)}
{footer("Full list: the model's Sources tab and research/*.csv, all accessed 30 Sep 2026.", f"A{9 + n}")}
{notes("Every fact on a slide traces to a row id in research/market_benchmarks.csv, regulation_rails.csv, levers.csv or own_checks.csv, or to founder data. Every model number traces to savings_first_model.xlsx.")}
"""
        out.append((sid, section(sid, body, **AP)))
    return out


SLIDES_OUT.extend(sources_slides())


def main():
    SLIDES.mkdir(parents=True, exist_ok=True)
    for f in SLIDES.glob("*.html"):
        f.unlink()
    order = []
    for sid, html in SLIDES_OUT:
        (SLIDES / f"{sid}.html").write_text(html)
        order.append(sid)
    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "lists": "css",
        "title": "Save First, Lend Later",
        "cover": "cover",
        "order": order,
        "sections": {
            "s1": {"description": "The idea and what Bueno taught", "start": "cover"},
            "s2": {"description": "Customer, problem and the flip", "start": "customer"},
            "s3": {"description": "Product, channels and money", "start": "product"},
            "s4": {"description": "Does it add up", "start": "unit"},
            "s5": {"description": "The next step", "start": "pilot"},
            "s6": {"description": "Appendix", "start": "a1_regmap"},
        },
        "faces": {
            "source-serif-4": {"family": "Source Serif 4", "href": "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&display=swap"},
            "ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"},
        },
        "designSystems": [],
    }
    (DECK / "project" / "deck.json").write_text(json.dumps(deck, indent=1, ensure_ascii=False))
    (DECK / "used_ids.json").write_text(json.dumps(USED, indent=1, ensure_ascii=False))
    print(f"wrote {len(order)} slides: {order}")


if __name__ == "__main__":
    main()

"""Write the evidence deck for a senior friend (brief/project/…): should we build this business?

Main section: one short claim and one picture per slide, at the evidence middle (every input
at the middle of its evidence range), with the founder's plan alongside. Appendix: the
reasoning and numbers, the assumption register, the Monte Carlo, the sensitivity, the critique
of the model, the fact checks and the sources.

Every number comes from the frozen tables by id (N / F / I / PY); check_deck.py traces every
digit. No past company is named.
"""
from __future__ import annotations

import csv
import json
import re

import build_deck as B
import viz
from build_deck import (ACC_TXT, AP_HEAD, BLUE, BODY, CARD, DARK_SOFT, GREY, INK, LBLUE, MUTED, ORANGE, PAPER, SAFFRON, SAND,
                        SERIF, F, I, N, card, eyebrow, footer, kpi, notes, p, section, table)

OUT = B.ROOT / "brief"
SLIDES = OUT / "project" / "slides"
T = B.T
CREATED = {"v": 1, "at": "2026-10-02T04:57:19Z"}   # the published index's value: keep it
LIGHT = viz.LIGHT
SHORT = "Model: savings_first_model.xlsx and mc.py, 2 Oct 2026."
EVID = "Evidence middle: every input at the middle of its evidence range (assumption register). " + SHORT
PAGES: list[tuple[str, str]] = []
MAIN_TOTAL = 12
PLABEL: list[str] = []
APPX = [0]
SEC: dict[str, list[int]] = {}


def V(i):
    return float(B.NUM[i]["value"])


def rd(name):
    return list(csv.DictReader(open(T / name)))


def title(t, color=INK, size=44):
    return f'<h2 style="font-family:{SERIF};font-size:{size}px;font-weight:600;line-height:1.15;color:{color}">{t}</h2>'


RAW: list[dict] = []


def page(label, line, body, src, say, bg=None, appendix=False):
    """Record a slide; layout() decides its place, id and footer."""
    RAW.append(dict(label=label, line=line, body=body, src=src, say=say, bg=bg, appendix=appendix))


def emit(r, appendix, label=None):
    label = label or r["label"]
    if appendix:
        APPX[0] += 1
        SEC.setdefault(label, []).append(APPX[0])
        sid, foot = f"a{APPX[0]:02d}", f"A{APPX[0]}"
    else:
        i = len(PAGES) + 1
        sid, foot = f"m{i:02d}", f"{i} / {MAIN_TOTAL}"
    tag = f"Appendix · {label}" if appendix else label
    html = f"""
{eyebrow(tag)}
{title(r["line"])}
{r["body"]}
{footer(r["src"], foot)}
{notes(r["say"])}
"""
    PAGES.append((sid, section(sid, html, bg=r["bg"] or (SAND if appendix else B.PAPER))))
    PLABEL.append(label)
    return sid


def caption(t, size=24, color=MUTED):
    return p(t, size, color)


def tile(num, cap, bg=CARD, border="#E3DDD0", size=72):
    return card(kpi(num, cap, size=size), pad=36, bg=bg, border=border)


def anchors(items):
    """A row of small evidence cards: (number, what it is, source)."""
    cards = "".join(card(f'<p style="font-size:32px;font-weight:600;color:{INK}">{n}</p>' + p(w, 24, BODY) + p(s, 24, MUTED), pad=22, gap=6)
                    for n, w, s in items)
    return f'<div style="display:flex;gap:20px">{cards}</div>'


LABELS = {
    "pay_flat": "Payment pricing: flat list price, not a %", "fail_billed": "Failed debits billed at list price",
    "pay_pct": "Payment fee as a share of each debit", "cost_notice": "Pre-debit notice cost",
    "cac_target@gig": "Cost to win a gig saver", "cac_target@ng": "Cost to win a shopkeeper",
    "ret_m12@gig": "Gig savers still saving at month 12", "ret_m12@ng": "Shopkeepers still saving at month 12",
    "ret_m24_ratio": "Year-2 retention as a share of year 1", "churn_late": "Monthly churn after year 2",
    "daily_amount@gig": "Gig amount per debit", "daily_amount@ng": "Shopkeeper amount per debit",
    "debits_success@gig": "Gig successful debits a month", "debits_success@ng": "Shopkeeper successful debits a month",
    "cost_support": "Support cost per active saver a month", "cost_tech": "Tech cost per active saver a month",
    "gold_margin": "Gold margin on money saved", "ins_premium": "Insurance premium a year", "ins_uptake@gig": "Gig insurance take-up a month",
    "ins_uptake@ng": "Shopkeeper insurance take-up a month", "ins_comm_first": "First-year insurance commission",
    "loan_apply": "Savers applying for a loan a month", "card_uptake": "FD-card take-up a month", "cost_fraud": "Fraud loss on money saved",
}
NAMES = {r["id"]: r["name"] for r in csv.DictReader(open(T / "inputs.csv"))}


def label(k):
    return LABELS.get(k, NAMES.get(k.split("@")[0], k))


# ================================================================ MAIN 1: cover
B._cur[0] = "m01"
PAGES.append(("m01", section("m01", f"""
{eyebrow("A note for your honest view · 2 October 2026", SAFFRON)}
<div style="display:flex;flex-direction:column;gap:36px">
<h1 style="font-family:{SERIF};font-size:120px;font-weight:600;line-height:1.05;color:{PAPER}">Save first, lend later</h1>
<h2 style="font-family:{SERIF};font-size:56px;font-weight:400;line-height:1.2;color:{PAPER};width:1560px">Worth testing, not yet building: as a savings-led lender to shopkeepers, it pays back in about two-thirds of futures.</h2>
</div>
{p("Every assumption checked against outside evidence. One point and one picture per slide; the numbers sit in the appendix.", 28, DARK_SOFT, extra="width:1500px")}
{notes(f'''This note asks one question: should we build a save-first, lend-later business? My answer: worth testing, not yet building. As a savings-led lender to shopkeepers, a customer pays back in about two-thirds of the futures we simulated. Four numbers decide it: what it costs to win a shopkeeper, how many borrow, the rate we can charge, and how well they repay. One pilot can measure all four before we spend real money. I'd value your honest view; the last slide has three questions.''')}
""", bg=INK, fg=PAPER, extra_style=";justify-content:space-between;padding:128px")))
PLABEL.append("The answer")

# ================================================================ MAIN 2: the odds
hist = [(float(r["lo"]), float(r["hi"]), float(r["share"])) for r in rd("mc_hist.csv") if r["variant"] == "independent"]
page("The answer in one picture",
     "In 10,000 simulated futures, not one saver turns a profit.",
     viz.histogram_marked(hist, height=360, markers=[(V("mc_independent_net_p50"), f"median {N('mc_independent_net_p50')}"),
                                                     (V("mc_independent_net_p95"), f"best 5% of futures: above {N('mc_independent_net_p95')}")])
     + caption(f"Net value per saver: five-year profit minus the cost to win them, across 10,000 futures. Profitable futures: {N('mc_independent_p_net_pos')}. The best single future still loses {N('mc_independent_net_max')}. The end bars also hold the most extreme 1% on each side."),
     "Monte Carlo, daily design, inputs independent: " + SHORT,
     f"""This is the whole answer. I drew each uncertain input from the range the evidence supports and ran the model 10,000 times. Every bar is the share of futures with that net value per saver: what a saver brings in over five years, after serving costs and discounted, minus what it costs to win them. All of it sits left of break-even. The median saver loses {N('mc_independent_net_p50')}; even the best 5% lose at least {N('mc_independent_net_p95')}. Linking the inputs (savers who stay also save and buy more) does not change this: {N('mc_correlated_p_net_pos')} profitable.""")

# ================================================================ MAIN 3: the problem
page("The customer",
     f"Daily earners save little and borrow: {F('rider_bike_borrowed')} riders borrowed to buy their bike.",
     f'''<div style="display:flex;gap:28px">
{card(viz.dots(4, ORANGE, size=30) + kpi(F('gig_under15k'), "of gig workers earn under ₹15,000 a month"), pad=36, gap=22)}
{card(viz.dots(5, BLUE, size=30) + kpi(F('rider_borrowed').capitalize(), "of riders who own a phone borrowed to buy it"), pad=36, gap=22)}
{card(viz.dots(6, BLUE, size=30) + kpi(F('rider_bike_borrowed'), f"riders who own their bike borrowed for it; {F('rider_missed')} of borrowers missed a payment"), pad=36, gap=22)}
</div>''',
     f"Sources: Indian Staffing Federation via Economic Survey 2025-26; IDinsight 2025 report ({F('rider_n')} riders of one platform, weighted).",
     f"""The customer: people paid daily or weekly. {F('gig_under15k')} of gig workers report earning under ₹15,000 a month (the Economic Survey cites the Indian Staffing Federation; gross or net is not stated). In IDinsight's survey of {F('rider_n')} riders on one platform, half borrowed to buy their phone and {F('rider_bike_borrowed')} to buy their bike, and {F('rider_missed')} of those borrowers missed at least one repayment. The survey's response rate was low, so read it as indicative.""")

# ================================================================ MAIN 4: the size
page("The customer",
     f"The pool is large: {F('gig_fy25')} gig workers and {F('udyam_micro')} small firms.",
     f'''<div style="display:flex;gap:24px;align-items:stretch">
{tile(F('gig_fy25')[0].upper() + F('gig_fy25')[1:], "gig workers in FY25")}
<div style="display:flex;flex-direction:column;justify-content:center"><x-shape kind="arrow-right" style="background:{ORANGE};width:80px;height:40px"></x-shape></div>
{tile(F('gig_2030'), "gig workers projected for 2029-30")}
{tile(F('udyam_micro'), "micro enterprises registered on Udyam", bg=SAND, border=SAND)}
</div>''' + caption(f"For scale: Swiggy alone has {F('swiggy_riders')} delivery partners active in an average month."),
     "Sources: Indian Staffing Federation via Economic Survey 2025-26; NITI Aayog (Jun 2022); Udyam dashboard; Swiggy Q1 FY27.",
     f"""Two pools, half each of our savers. Gig workers: {F('gig_fy25')} in FY25 on the Indian Staffing Federation's count, which the Economic Survey uses; NITI Aayog's own path for that year is close, and it projects {F('gig_2030')} by 2029-30. The self-employed: {F('udyam_micro')} micro enterprises are registered on Udyam. Workers and enterprises are different units, so these are not added. Market size is not the problem; the next slides are about what each saver is worth.""")

# ================================================================ MAIN 5: the idea
steps = ["1. Saves a little every day, automatically, from their own bank account",
         "2. The money sits with a bank, fund or gold partner, in the saver's name",
         "3. Months of saving show who is steady",
         "4. Partners insure them and lend to them; we earn a fee on each"]
Wb, Gb, Hb = 368, 64, 250
boxes = "".join(f'<div style="position:absolute;left:{k * (Wb + Gb)}px;top:0;width:{Wb}px;height:{Hb}px;background:{CARD};border:2px solid {INK};'
                f'border-radius:16px;padding:24px"><p style="font-size:30px;line-height:1.3;color:{INK}">{t}</p></div>' for k, t in enumerate(steps))
arrows = "".join(f'<x-connector x1="{k * (Wb + Gb) + Wb + 4}" y1="{Hb // 2}" x2="{(k + 1) * (Wb + Gb) - 4}" y2="{Hb // 2}" style="color:{ORANGE};border-width:3px"></x-connector>'
                 for k in range(3))
page("The idea",
     "The idea: save a little daily, build a record, then sell loans and cover.",
     f'<div style="position:relative;width:1664px;height:{Hb}px">{boxes}{arrows}</div>'
     + p(f"We would be a distributor, like an insurance or loan agent with an app: partners hold the money and the loans, and we cover at most {F('dlg_cap')} of a lender's losses.", 28, INK),
     "Design: founder, 30 Sep and 2 Oct 2026.",
     f"""The idea in four steps. A worker sets up one UPI Autopay mandate and a small amount moves every day from their own bank account into digital gold, a liquid fund or an FD in their name. The saving record shows who is steady. Partner insurers and lenders then sell to them through us: the first two loans secured against savings, then part secured, then unsecured. We earn fees and commissions; we never hold money or loans.""")

# ================================================================ MAIN 6: why now
page("The idea",
     f"Two 2025-26 rules make it possible: {F('emandate_limit')} auto-debits and {F('dlg_cap')} loss cover.",
     f'''<div style="display:flex;gap:28px">
{tile(F('emandate_limit'), "auto-debits up to this need no fresh approval, so a daily debit is practical (RBI, 2026)")}
{tile(F('dlg_cap'), "of a lender's losses an app may cover, so we can share loan risk without a lending licence (RBI, 2025)", bg=SAND, border=SAND)}
</div>''',
     "Sources: RBI e-mandate framework; RBI Digital Lending Directions (May 2025).",
     f"""Two rule changes open the door. RBI's e-mandate framework lets recurring debits up to {F('emandate_limit')} run without fresh approval. RBI's digital lending rules let an app cover up to {F('dlg_cap')} of a partner lender's losses, so we can earn more per loan without becoming a lender. The rules make the product possible; they do not make it pay.""")

# ================================================================ MAIN 7: retention
months = [1, 3, 6, 12, 24]
ev_s = [V(f"ev_daily_still_m{m}") for m in months]
pl_s = [V(f"plan_base_m{m}_still") for m in months]
H7 = 240
cols = "".join(
    f'<div style="width:220px;display:flex;flex-direction:column;gap:8px">'
    f'<div style="height:{H7}px;display:flex;gap:10px;align-items:flex-end;justify-content:center">'
    f'<div style="width:72px;height:{max(3, e * H7):.0f}px;background:{BLUE};border-radius:4px 4px 0 0"></div>'
    f'<div style="width:72px;height:{max(3, q * H7):.0f}px;background:{GREY};border-radius:4px 4px 0 0"></div></div>'
    f'<p style="font-size:28px;font-weight:600;color:{INK};text-align:center">{N(f"ev_daily_still_m{m}")}</p>'
    f'<p style="font-size:24px;color:{BODY};text-align:center">month {m}</p></div>' for m, e, q in zip(months, ev_s, pl_s))
page("Why it doesn't pay",
     f"Savers keep saving about {N('ev_daily_active_months_5y')} on average; here your plan and the evidence agree.",
     f'<div style="display:flex;gap:40px;align-items:flex-end"><div style="display:flex;gap:16px">{cols}</div>'
     f'<div style="flex:1;display:flex;flex-direction:column;gap:12px">{p("<b>Still saving</b>", 28, INK)}'
     f'<div style="display:flex;gap:10px;align-items:center"><div style="width:28px;height:28px;background:{BLUE}"></div>{p("evidence middle", 24, INK)}</div>'
     f'<div style="display:flex;gap:10px;align-items:center"><div style="width:28px;height:28px;background:{GREY}"></div>{p("your plan", 24, INK)}</div></div></div>'
     + anchors([(F("ev_chhoti_churn"), "of ₹250 first-time SIPs close each month", "Business Standard, 2026"),
                (F("ev_jannivesh"), "of SBI's daily ₹250 SIPs stopped in their first year", "SBI Funds RHP"),
                (F("ev_zomato_exit"), "Zomato riders leave voluntarily", "CEO, Jan 2026")]),
     "Share of savers who made a first debit, both halves. Evidence: tri_behaviour.csv. " + SHORT,
     f"""Retention is not where the plan goes wrong. At the evidence middle, {N('ev_daily_still_m12')} of savers are still saving after a year and {N('ev_daily_still_m24')} after two; my plan says {N('plan_base_m12_still')} and {N('plan_base_m24_still')}. The closest Indian analogues bracket it: ₹250 first-time SIPs lose {F('ev_chhoti_churn')} of their book each month, and {F('ev_jannivesh')} of SBI's daily ₹250 SIPs started in FY26 had stopped by year end. Riders churn hard: Zomato loses {F('ev_zomato_exit')}. Over five years the average saver is active about {N('ev_daily_active_months_5y')}. The problem is what they are worth while they stay.""")

# ================================================================ MAIN 8: money in vs out
sc8 = 1300 / V("ev_daily_cost_pa_y2")
rev_p = [("Gold", "ev_daily_rev_pa_y2::Savings: gold", ORANGE), ("Cards", "ev_daily_rev_pa_y2::Cards", LBLUE), ("Insurance", "ev_daily_rev_pa_y2::Insurance", BLUE)]
cost_p = [("Debits", "ev_daily_cost_pa_y2::pay", viz.BROWN), ("Support and tech", "ev_daily_cost_pa_y2::service", GREY)]


def stack(parts, total_id, rest):
    segs = "".join(f'<div style="width:{V(i) * sc8:.0f}px;height:56px;background:{c}"></div>' for _, i, c in parts)
    r_ = V(total_id) - sum(V(i) for _, i, _ in parts)
    segs += f'<div style="width:{max(0, r_) * sc8:.0f}px;height:56px;background:{LIGHT}"></div>'
    leg = "".join(f'<div style="display:flex;gap:10px;align-items:center"><div style="width:24px;height:24px;background:{c};border-radius:4px"></div>'
                  f'<p style="font-size:24px;color:{INK}">{lab} {N(i)}</p></div>' for lab, i, c in parts)
    leg += f'<div style="display:flex;gap:10px;align-items:center"><div style="width:24px;height:24px;background:{LIGHT};border-radius:4px"></div><p style="font-size:24px;color:{INK}">{rest}</p></div>'
    return f'<div style="display:flex">{segs}</div><div style="display:flex;gap:28px;flex-wrap:wrap">{leg}</div>'


page("Why it doesn't pay",
     f"An active saver brings in {N('ev_daily_rev_pa_y2')} a year but costs {N('ev_daily_cost_pa_y2')} to serve.",
     f'''<div style="display:flex;flex-direction:column;gap:12px">{p(f"<b>Brings in a year: {N('ev_daily_rev_pa_y2')}</b>", 28, INK)}{stack(rev_p, "ev_daily_rev_pa_y2", "loans, funds, FDs")}</div>
<div style="display:flex;flex-direction:column;gap:12px">{p(f"<b>Costs to serve that year: {N('ev_daily_cost_pa_y2')}</b>", 28, INK)}{stack(cost_p, "ev_daily_cost_pa_y2", "loans, insurance, cards, fraud")}</div>'''
     + caption(f"Your plan: brings {N('plan_base_rev_pa_y2')}, costs {N('story_base_cost_pa_y2')}. Either way, a saver loses money every year they stay."),
     "Per active saver, year 2, both halves; evidence middle. " + SHORT,
     f"""At the evidence middle, an active saver in their second year brings us {N('ev_daily_rev_pa_y2')}: gold margin {N('ev_daily_rev_pa_y2::Savings: gold')}, card fees {N('ev_daily_rev_pa_y2::Cards')}, insurance commission {N('ev_daily_rev_pa_y2::Insurance')}, and very little from loans, funds and FDs. Serving them costs {N('ev_daily_cost_pa_y2')}: debits {N('ev_daily_cost_pa_y2::pay')}, support and tech {N('ev_daily_cost_pa_y2::service')}. My plan had {N('plan_base_rev_pa_y2')} against {N('story_base_cost_pa_y2')}. Both lose money for every year a saver stays, which is why longer retention makes the loss bigger, not smaller.""")

# ================================================================ MAIN 9: per debit
dmax = V("ev_daily_cost_per_debit_flat")
page("Why it doesn't pay",
     f"Serving costs more than they bring in: a debit earns us {N('ev_daily_gold_per_debit')} but costs up to {N('ev_daily_cost_per_debit_flat')}.",
     viz.share_bars([("What one debit earns us (gold margin)", V("ev_daily_gold_per_debit") / dmax, N("ev_daily_gold_per_debit")),
                     (f"Cost if the payment firm charges {F('ev_debit_pct')}", V("ev_daily_cost_per_debit_pct") / dmax, N("ev_daily_cost_per_debit_pct")),
                     ("Cost at list price, ₹5 plus GST", 1.0, N("ev_daily_cost_per_debit_flat"))], label_w=620, track_w=820)
     + anchors([(F("debit_list"), "list price per Autopay debit at Cashfree and Zoho, before GST", "price pages, 2026"),
                (F("ev_debit_pct"), "of each debit where firms charge a percentage", "Razorpay reported; PhonePe PG"),
                (F("ev_rail_cost"), "what one UPI transaction costs the whole system", "analyst estimate, 2024")]),
     "Gig half, evidence middle. Evidence: tri_costs.csv. " + SHORT,
     f"""The heart of the problem, per debit. At the evidence middle a gig saver puts in {N('ev_daily_debit_amount_gig')} a debit; half goes to gold, where we keep about {N('ev_gold_margin')}, so we earn {N('ev_daily_gold_per_debit')}. Collecting it costs {N('ev_daily_cost_per_debit_pct')} if the payment company charges a percentage, or {N('ev_daily_cost_per_debit_flat')} at the published list price of {F('debit_list')} plus GST, at Cashfree and Zoho alike. Nobody publishes a negotiated price; the system's own cost is about {F('ev_rail_cost')}. Daily collection of small amounts costs more than it earns at every price we found.""")

# ================================================================ MAIN 10: CAC
cac_row = [r for r in rd("distributions.csv") if r["input"] == "cac_target" and r["segment"] == "gig"][0]
page("Why it doesn't pay",
     f"Winning a saver costs about {N('ev_daily_cac')}, not the {N('plan_base_cac')} in your plan.",
     viz.dist_with_markers("lognormal", float(cac_row["low"]), float(cac_row["mode"]), float(cac_row["high"]),
                           [(V("seg_gig_base_cac"), f"your plan {N('seg_gig_base_cac')}", ORANGE),
                            (float(cac_row["mode"]), f"evidence middle {N('ev_daily_cac')}", INK)], w=1664, h=250)
     + anchors([(F("ev_groww_cac"), "Groww's cost per new customer, with 81-84% arriving on their own", "Entrackr, 2025"),
                (F("ev_cpi"), "per app install for wealth apps, before anyone saves", "vendor benchmarks, 2026")]),
     "Cost per saver who makes a first debit, gig half. Evidence: tri_behaviour.csv. " + SHORT,
     f"""My plan says {N('plan_base_cac')} to win a saver who makes a first debit. The evidence centres near {N('ev_daily_cac')}: Groww pays {F('ev_groww_cac')} per new customer even though most arrive on their own, and wealth-app installs cost {F('ev_cpi')} each before anyone saves. My {N('seg_gig_base_cac')} for gig workers is cheaper than {N('reg_cac_target_gig_fav')} of the evidence range. Swiggy has also tied up with Zerodha Fund House for riders, which takes my cheapest gig channel.""")

# ================================================================ MAIN 11: loans
lad = [("Savers who make a first debit", 1.0, "100%", BLUE), ("ever take a loan", V("ev_daily_borrow_60"), N("ev_daily_borrow_60"), BLUE),
       ("reach loan 3, part secured", V("ev_daily_reach3"), N("ev_daily_reach3"), BLUE),
       ("reach loan 5, unsecured", V("ev_daily_reach5"), N("ev_daily_reach5"), ORANGE)]
page("Why it doesn't pay",
     f"Loans can't carry it: {N('ev_daily_borrow_60')} of savers ever borrow, and a first loan is {N('ev_daily_sec_start')}.",
     viz.share_bars([(a, max(b, 0.004), c) for a, b, c, _ in lad], label_w=560, track_w=900)
     + anchors([(F("ev_lamf"), "of Indian fund investors ever borrowed against their funds", "Volt, 2026"),
                (F("ev_lafd"), "a bank's whole margin on a loan against an FD", "bank terms, 2026"),
                ("M-Shwari", "froze savings against loans at launch and quickly dropped it", "CGAP, 2015")]),
     "Within five years, both halves. Evidence: tri_behaviour.csv, tri_costs.csv. " + SHORT,
     f"""Lending was meant to pay for the saving. At the evidence middle only {N('ev_daily_borrow_60')} of savers ever take a loan within five years, {N('ev_daily_reach3')} reach the part-secured third loan and {N('ev_daily_reach5')} the unsecured fifth. A first loan against savings is about {N('ev_daily_sec_start')}. People rarely borrow against their own savings: only {F('ev_lamf')} of fund investors ever have, and M-Shwari in Kenya dropped its frozen-savings rule. Banks earn only {F('ev_lafd')} on loans against FDs, so the fee on small secured loans is thin. Over five years loans bring {N('ev_daily_rev60_loans')} of our revenue.""")

# ================================================================ MAIN 12: the gap
gmax = V("ev_daily_rev_needed_per_active_year")
jar_rng = [float(x) for x in re.findall(r"[\d,]+", F("ev_jar_rev_active").replace(",", ""))[:2]]
page("Why it doesn't pay",
     f"To break even, each active saver-year must bring {N('ev_daily_rev_needed_per_active_year')}: {N('ev_daily_rev_needed_multiple')} times today.",
     viz.share_bars([("Today, at the evidence middle", V("ev_daily_rev_per_active_year") / gmax, N("ev_daily_rev_per_active_year")),
                     ("What Jar's filings imply (excluding jewellery)", sum(jar_rng) / 2 / gmax, F("ev_jar_rev_active")),
                     ("Needed to repay serving costs and the cost to win", 1.0, N("ev_daily_rev_needed_per_active_year"))], label_w=640, track_w=760)
     + f'''<div style="display:flex;gap:20px">
{card(kpi(N("ev_daily_cac"), "to win each saver, paid up front", size=48), pad=24)}
{card(kpi(N("ev_daily_cost_per_active_year"), "to serve each active saver a year", size=48), pad=24)}
{card(kpi(N("ev_daily_pv_active_months"), "of saving per saver won, after discounting", size=48), pad=24, bg=SAND, border=SAND)}
</div>'''
     + caption("Per active saver per year, discounted. Jar's figure is approximate: revenue less jewellery, divided by an estimated 4-7% of users being active."),
     "Evidence middle, daily design; Jar derived from filings coverage. " + SHORT,
     f"""Turn it around: what would a saver need to bring in? An activated saver stays active about {N('ev_daily_active_months_5y')}, worth {N('ev_daily_pv_active_months')} after discounting. To repay serving costs and the {N('ev_daily_cac')} to win them, each active saver-year must bring {N('ev_daily_rev_needed_per_active_year')}, against {N('ev_daily_rev_per_active_year')} at the evidence middle: {N('ev_daily_rev_needed_multiple')} times more. Even Jar, the market leader, implies only about {F('ev_jar_rev_active')} per active saver from its filings. The gap is too big for tuning; it needs a different engine.""")

# ================================================================ MAIN 13: the flip (could savers just save more?)
rider = float(F("rider_net").replace("₹", "").replace(",", ""))
fmax = V("flip_ev_flat_monthly_gig")
page("Why it doesn't pay",
     f"Saving more doesn't fix it: a saver would have to put in {N('flip_ev_flat_amount')} a day.",
     viz.share_bars([(f"Your plan's numbers: {N('flip_plan_amount')} a day", V("flip_plan_monthly_gig") / fmax, f"{N('flip_plan_monthly_gig')} a month", LBLUE),
                     (f"Best case, flat fee: {N('flip_best_flat_amount')} a day", V("flip_best_flat_monthly_gig") / fmax, f"{N('flip_best_flat_monthly_gig')} a month", LBLUE),
                     ("A full-time rider's whole net income", rider / fmax, f"{F('rider_net')} a month", INK),
                     (f"Evidence middle, flat fee: {N('flip_ev_flat_amount')} a day", 1.0, f"{N('flip_ev_flat_monthly_gig')} a month", ORANGE),
                     ("If the fee is a % of each debit", 0.004, "no amount works", GREY)], label_w=600, track_w=700)
     + anchors([(f"{F('ev_debit_gst')} → {F('ev_debit_high')}", f"list price per debit, up to and above {F('ev_debit_tier')}", "Cashfree and Zoho, 2026"),
                (N("ev_keep_share"), f"of each rupee saved that we keep: half goes to gold, at about {N('ev_gold_margin')}", "evidence middle"),
                (F("ev_gullak"), "a month: what Gullak's savers actually put in", "Gullak launch data, 2022")]),
     f"Monthly = daily minimum x {N('flip_ev_flat_debits_gig')} debits (gig half). tables/flip_breakeven.csv.",
     f"""Flip the question: how much would each saver have to put in for us to break even on them? I swept the daily minimum in ₹50 steps. With my plan's own numbers, including a ₹2 debit that no payment company publishes, it is {N('flip_plan_amount')} a day, about {N('flip_plan_monthly_gig')} a month: {N('flip_plan_income_gig')} of a full-time rider's net income. At the evidence middle it is {N('flip_ev_flat_amount')} a day, about {N('flip_ev_flat_monthly_gig')} a month, several times what a rider earns. The reason: we keep only about {N('ev_keep_share')} of each rupee saved, while every debit costs {F('ev_debit_gst')}, rising to {F('ev_debit_high')} above {F('ev_debit_tier')}. Below that step the best any amount does is {N('flip_ev_flat_best_upto_1000')} per saver. If the payment company charges a percentage, a bigger minimum only loses more. And this is the kind version: it assumes a higher minimum loses no savers and bounces no extra debits.""")

# ================================================================ MAIN 14: one customer, everything sold (lifetime value, payback)
L = "ltv_evidence_everything_mid"
page("Why it doesn't pay",
     f"Even if we sell them everything, a customer never pays back: we lose {N(L + '_loss')} on each.",
     viz.waterfall([("To win a customer", -V(L + "_cac"), "−" + N(L + "_cac"), "cost"),
                    ("What their savings earn us", V(L + "_savings_pv"), "+" + N(L + "_savings_pv"), "income"),
                    ("Everything else we sell them: loans, SIPs, insurance, pension, cards, bills", V(L + "_cross_sell_pv"), "+" + N(L + "_cross_sell_pv"), "income"),
                    ("Serving them, mostly the fee on every debit", -V(L + "_serve_pv"), "−" + N(L + "_serve_pv"), "cost"),
                    ("What one customer is worth to us", 0.0, N(L + "_net60"), "total")])
     + p(f"<b>Payback: {N(L + '_payback')}.</b> Only if every product hit its best case at once would a customer pay back, in {N('ltv_evidence_everything_best_payback')}.", 30, INK),
     "One customer won, over five years, discounted; evidence middle. Selling starts in month one, before its own costs. ltv_cases.csv.",
     f"""This is the whole business in one line per customer. Winning a customer costs {N(L + '_cac')}. Over five years their savings earn us {N(L + '_savings_pv')}, and everything else we could sell them adds {N(L + '_cross_sell_pv')}: loans of every kind, mutual-fund SIPs, insurance, pension, an FD-backed card, bills and recharges, priced product by product in the appendix. Serving them costs {N(L + '_serve_pv')}, most of it the fee on every debit. So a customer is worth {N(L + '_ltv60')} before we even count the cost of winning them, and {N(L + '_net60')} after. We never get the {N(L + '_cac')} back, even over ten years. That is generous: selling starts in month one and its own costs are left out. Only if every product hit its best case at the same time would a customer pay back, in {N('ltv_evidence_everything_best_payback')}, and even then they only just break even over five years.""")

# ================================================================ MAIN 15: drivers
page("How sure are we",
     f"Payment pricing decides {N('mc_independent_drv_payment_pricing')} of the odds; the cost to win a saver {N('mc_independent_drv_cost_to_win_a_saver')}.",
     viz.share_bars([("Payment pricing (flat list price or a %)", V("mc_independent_drv_payment_pricing"), N("mc_independent_drv_payment_pricing")),
                     ("Cost to win a saver", V("mc_independent_drv_cost_to_win_a_saver"), N("mc_independent_drv_cost_to_win_a_saver")),
                     ("Retention", V("mc_independent_drv_retention"), N("mc_independent_drv_retention")),
                     (f"All other {N('reg_total')} inputs", max(V("mc_independent_drv_debits_and_amounts") + V("mc_independent_drv_everything_else"), 0.005),
                      N("mc_independent_drv_everything_else"))], label_w=620, track_w=820)
     + caption("Share of the spread in net value per saver across 10,000 futures that each input explains (rank regression)."),
     "Monte Carlo drivers, daily design: mc_drivers.csv. " + SHORT,
     f"""What moves the result most? Across the 10,000 futures, whether the payment company charges a flat list price or a percentage explains {N('mc_independent_drv_payment_pricing')} of the spread in net value per saver, and the cost to win a saver {N('mc_independent_drv_cost_to_win_a_saver')}. Retention explains {N('mc_independent_drv_retention')}. So the first two things to pin down are a signed payment price and a real acquisition cost.""")

# ================================================================ MAIN 14: nothing crosses break-even
oat = rd("sens_oat.csv")[:8]
trows = []
for r in oat:
    k = r["input"].replace("@", "_")
    lo_id, hi_id = (f"oat_{k}_net_at_p10", f"oat_{k}_net_at_p90") if float(r["net_at_p10"]) <= float(r["net_at_p90"]) else (f"oat_{k}_net_at_p90", f"oat_{k}_net_at_p10")
    trows.append((label(r["input"]), float(r["net_at_p10"]), float(r["net_at_base"]), float(r["net_at_p90"]), f"{N(lo_id)} to {N(hi_id)}"))
page("How sure are we",
     f"Even with every input at its good end at once, a saver still loses {N('ev_corner_net').lstrip('−')}.",
     viz.tornado_zero(trows, track_w=920) + caption("Net value per saver as each input moves across its evidence range (10th to 90th percentile), all else at the evidence middle. The ink line is break-even."),
     "One at a time around the evidence middle: sens_oat.csv; corner: ev_centre.csv. " + SHORT,
     f"""No single input gets a saver to break-even: every bar stays left of the line. Moving all of them to their favourable end together, the corner of the evidence, still leaves a saver at {N('ev_corner_net')}. This is the strongest sign that the problem is the design, not a few unlucky numbers.""")

# ================================================================ MAIN 15: weekly
page("How sure are we",
     f"Weekly debits cut the median loss to {N('mc_weekly_net_p50')}, but still no profitable saver.",
     viz.ranges([("Daily debits", V("mc_independent_net_p5"), V("mc_independent_net_p50"), V("mc_independent_net_p95"), f"median {N('mc_independent_net_p50')}"),
                 ("Daily, inputs linked", V("mc_correlated_net_p5"), V("mc_correlated_net_p50"), V("mc_correlated_net_p95"), f"median {N('mc_correlated_net_p50')}"),
                 ("Weekly, on payout day", V("mc_weekly_net_p5"), V("mc_weekly_net_p50"), V("mc_weekly_net_p95"), f"median {N('mc_weekly_net_p50')}")], width=1020)
     + caption(f"Band: 5th to 95th percentile of net value per saver across 10,000 futures; dark tick: median; orange line: break-even. Profitable futures, weekly: {N('mc_weekly_p_net_pos')}."),
     "Monte Carlo, daily and weekly designs: mc_summary.csv. " + SHORT,
     f"""The obvious fix is fewer, bigger debits: one a week after payout, the same money a month. It helps a lot when the payment company charges a flat fee per debit: the median loss falls from {N('mc_independent_net_p50')} to {N('mc_weekly_net_p50')}. But the band never reaches break-even: profitable futures {N('mc_weekly_p_net_pos')}. Collection cost is only part of the gap; revenue per saver is the rest.""")

# ================================================================ MAIN 16: optimism
REG = rd("assumption_register.csv")
chk = [r for r in REG if r["status"] == "triangulated" and r["plan_value"] != ""]
vc = {v: sum(1 for r in chk if r["verdict"] == v) for v in ("plan optimistic", "plan leans optimistic", "plan within evidence", "plan cautious")}
opt = sorted([r for r in chk if r["verdict"] in ("plan optimistic", "plan leans optimistic")], key=lambda r: -(float(r["swing_rs"]) if r["swing_rs"] else 0))
nice = []
for r in opt:
    nm = LABELS.get(r["input"] + ("@" + r["segment"] if r["segment"] != "all" else ""), r["assumption"])
    if nm not in nice:
        nice.append(nm)
legend = "".join(f'<div style="display:flex;gap:12px;align-items:center"><div style="width:28px;height:28px;border-radius:50%;background:{c}"></div>{p(f"{lab}: {N(i)}", 26, INK)}</div>'
                 for lab, i, c in (("More optimistic than the evidence", "reg_plan_optimistic", ORANGE), ("Leans optimistic", "reg_plan_leans_optimistic", SAFFRON),
                                   ("Within the evidence", "reg_plan_within_evidence", BLUE), ("More cautious", "reg_plan_cautious", GREY)))
page("How sure are we",
     f"{N('reg_any_optimistic')} of the {N('reg_checked')} assumptions we could check are more optimistic than the evidence.",
     f'''<div style="display:flex;gap:56px">
<div style="display:flex;flex-direction:column;gap:28px">{viz.dot_grid([(vc["plan optimistic"], ORANGE), (vc["plan leans optimistic"], SAFFRON), (vc["plan within evidence"], BLUE), (vc["plan cautious"], GREY)], per_row=10)}
<div style="display:flex;flex-direction:column;gap:10px">{legend}</div></div>
{card(p("<b>Optimistic and matter most</b>", 28, INK) + "".join(p("· " + x, 24, BODY) for x in nice[:7]), pad=28, gap=8, bg=SAND, border=SAND)}
</div>''',
     "One dot per checked assumption: assumption_register.csv; evidence in research/tri_*.csv.",
     f"""I checked {N('reg_triangulated')} inputs against independent sources. Of the {N('reg_checked')} where my plan has a number to compare, {N('reg_plan_optimistic')} are more optimistic than 80% of the evidence and {N('reg_plan_leans_optimistic')} more than 60%; only {N('reg_plan_cautious')} is cautious. The biggest are the cost to win a saver, debits per month, the pre-debit notice cost, insurance take-up and premium, and loan applications. {N('reg_provisional')} inputs could not be checked and keep a widened range; they are listed in the appendix.""")

# ================================================================ MAIN 17: competition map
pl = [(40, 30, "PhonePe, Paytm, Google Pay", f"daily gold inside the payment app ({F('phonepe_daily')} on PhonePe)", CARD),
      (40, 210, "Jar", f"daily gold; {F('jar_users')} registered", CARD),
      (40, 390, "Swiggy x Zerodha Fund House", f"riders can invest from {F('ev_swiggy_zerodha')}", CARD),
      (900, 210, "Bachatt", f"daily saving, then loans {F('bachatt_loans')}; {F('bachatt_raise')} raised", CARD),
      (900, 390, "Us", "daily saving, then loans and cover, for riders and shopkeepers", SAND)]
els = [f'<div style="position:absolute;left:{x}px;top:{y}px;width:720px;height:150px;background:{bg};border:2px solid {INK};border-radius:16px;padding:20px">'
       f'<p style="font-size:28px;font-weight:600;color:{INK}">{n}</p><p style="font-size:24px;line-height:1.3;color:{BODY}">{d}</p></div>' for x, y, n, d, bg in pl]
els.append(f'<div style="position:absolute;left:820px;top:0px;width:4px;height:560px;background:{GREY}"></div>')
els.append(f'<p style="position:absolute;left:40px;top:575px;width:720px;font-size:24px;font-weight:600;color:{ACC_TXT};text-align:center">SAVING ONLY</p>')
els.append(f'<p style="position:absolute;left:900px;top:575px;width:720px;font-size:24px;font-weight:600;color:{ACC_TXT};text-align:center">SAVING, THEN LENDING</p>')
page("Competition",
     "Daily saving is already sold to our customers by apps with far more reach.",
     f'<div style="position:relative;width:1664px;height:615px">{"".join(els)}</div>',
     "Sources: Medianama 2024; TechCrunch 2025; Whalesbook 2026; Entrackr 2026; company releases.",
     f"""Who already serves our customers. PhonePe, Paytm and Google Pay sell daily gold inside the payment app; PhonePe's runs {F('phonepe_daily')}, built with Jar, which has {F('jar_users')} registered users. Swiggy lets riders invest from {F('ev_swiggy_zerodha')} through Zerodha Fund House. Bachatt already does save-then-lend for shopkeepers: daily saving, then loans {F('bachatt_loans')} through {F('bachatt_lenders')} lenders, with {F('bachatt_raise')} raised. A standalone app would be late on both halves.""")

# ================================================================ MAIN 18: what would have to change
page("What would have to change",
     "It pays only inside a platform that already covers acquisition, collection and the app.",
     viz.steps_bars([("A saver today, evidence middle", V("ev_daily_net"), N("ev_daily_net")),
                     ("if debits were free", V("ev_daily_whatif_free_debits"), N("ev_daily_whatif_free_debits")),
                     ("and winning savers were free", V("ev_daily_whatif_free_acquisition"), N("ev_daily_whatif_free_acquisition")),
                     ("and support and tech were free", V("ev_daily_whatif_free_support_tech"), N("ev_daily_whatif_free_support_tech"))], height=380)
     + caption("Net value per saver over five years, removing one cost at a time; the ink line is break-even."),
     "What-if steps at the evidence middle: ev_centre.csv. " + SHORT,
     f"""Remove the costs one at a time. A saver at the evidence middle is worth {N('ev_daily_net')}. Free debits bring that to {N('ev_daily_whatif_free_debits')}; free acquisition as well, {N('ev_daily_whatif_free_acquisition')}; free support and tech as well, {N('ev_daily_whatif_free_support_tech')}. So the product only works where someone else already pays to acquire the customer, to collect the money and to run the app: as a benefit inside a platform, a bank or a payroll, not as a standalone app. That is the redesign worth testing.""")

# ================================================================ MAIN 19: the cheapest tests
tests = [("1. Price", "Get a signed price for daily debits from two payment companies", f"Pass: {F('ev_debit_pct')} of the debit or less, not {F('debit_list')} a debit"),
         ("2. Partner", "Ask one platform or bank to run saving as a benefit for its workers", "Pass: they pay to acquire and collect; we supply the product"),
         ("3. Buying", "Offer cover and small loans to an existing group of savers through that partner", f"Pass: on track to {N('ev_daily_rev_needed_per_active_year')} a year per active saver")]
Wt, Ht = 500, 300
tb = "".join(f'<div style="position:absolute;left:{k * (Wt + 82)}px;top:0;width:{Wt}px;height:{Ht}px;background:{CARD if k < 2 else SAND};border:2px solid {INK};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:10px">'
             f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p>'
             f'<p style="font-size:28px;font-weight:600;line-height:1.25;color:{INK}">{b}</p><p style="font-size:24px;line-height:1.3;color:{BODY}">{c}</p></div>'
             for k, (a, b, c) in enumerate(tests))
ta = "".join(f'<x-connector x1="{k * (Wt + 82) + Wt + 4}" y1="{Ht // 2}" x2="{(k + 1) * (Wt + 82) - 4}" y2="{Ht // 2}" style="color:{ORANGE};border-width:3px"></x-connector>' for k in range(2))
page("What would have to change",
     f"Three cheap tests come before any build, not a {N('plan_base_need_y1_cr')} pilot.",
     f'<div style="position:relative;width:1664px;height:{Ht}px">{tb}{ta}</div>'
     + p("Stop at the first test that fails. Each takes weeks and costs little next to a year-long pilot.", 28, INK),
     "Pass lines from the evidence middle and the break-even calculation. " + SHORT,
     f"""Before spending {N('plan_base_need_y1_cr')} on a year-long pilot, three cheap tests settle whether a redesign could work. One: a signed debit price; if it is the list price of {F('debit_list')} plus GST, daily saving is dead. Two: one platform or bank willing to run saving as a benefit and pay to acquire and collect; without that, acquisition alone sinks it. Three: through that partner, offer cover and small loans to savers already on board, and see whether revenue per active saver could approach {N('ev_daily_rev_needed_per_active_year')} a year.""")

# ================================================================ MAIN 20: the verdict, side by side
page("What would have to change",
     "Your plan and the evidence agree on the verdict; they differ on how far off it is.",
     f'''<div style="display:flex;gap:28px">
{card(p("Your plan, middle case", 24, MUTED) + kpi(N("plan_base_net_per_customer"), "net value per saver") + kpi(N("plan_base_cac"), "to win a saver", size=40) + kpi(N("plan_base_rev_pa_y2"), "brought in per active saver a year", size=40), pad=32, gap=18)}
{card(p("Evidence middle", 24, MUTED) + kpi(N("ev_daily_net"), "net value per saver") + kpi(N("ev_daily_cac"), "to win a saver", size=40) + kpi(N("ev_daily_rev_pa_y2"), "brought in per active saver a year", size=40), pad=32, gap=18, bg=SAND, border=SAND)}
{card(p("10,000 futures", 24, DARK_SOFT) + kpi(N("mc_independent_net_p50"), "median net value per saver", color=PAPER, capcolor=DARK_SOFT) + kpi(N("mc_independent_p_net_pos"), "profitable", size=40, color=PAPER, capcolor=DARK_SOFT), pad=32, gap=18, bg=INK, border=INK)}
</div>''',
     "Plan: inputs.csv base case; evidence middle and futures: mc.py. " + SHORT,
     f"""Side by side. My plan's middle case already lost money: {N('plan_base_net_per_customer')} per saver. At the evidence middle it is {N('ev_daily_net')}, mostly because winning a saver costs {N('ev_daily_cac')} rather than {N('plan_base_cac')} and a saver brings in {N('ev_daily_rev_pa_y2')} rather than {N('plan_base_rev_pa_y2')}. Across 10,000 futures the median is {N('mc_independent_net_p50')} and {N('mc_independent_p_net_pos')} is profitable. The verdict is the same either way; the evidence says the gap is wider.""")

# ================================================================ NEW: the answer staircase
stair = [("As first designed: gold, a fee on every debit", 0.004, N("rd_original_p"), ORANGE),
         ("Redesign: shopkeepers, saving into funds, loans via lenders", V("rd_var_base_p"), N("rd_var_base_p"), LBLUE),
         ("+ proven savers keep borrowing after they stop saving", V("rd_var_grad_p"), N("rd_var_grad_p"), LBLUE),
         (f"+ {N('rd_grid_takeup_20')} of them takes a loan each year", V("rd_var_grad_20_p"), N("rd_var_grad_20_p"), BLUE),
         (f"+ we win each shopkeeper for {N('rd_target_cac')}", V("rd_var_best_p"), N("rd_var_best_p"), INK)]
page("The answer in one picture",
     f"As designed, no future pays back; redesigned around loans to proven savers, {N('rd_var_best_p')} can.",
     viz.share_bars([(a, b / V("rd_var_best_p"), c, d) for a, b, c, d in stair], label_w=760, track_w=640)
     + caption("Futures in which a customer pays back what it cost to win them, within five years. Each step adds one change to the one above."),
     "Original: 10,000 futures. Redesign: 4,000 futures per step. tables/redesign_variants.csv.",
     f"""This is the whole note in one picture. As first designed, with half the money in digital gold and a fee on every debit, no customer pays back in any of 10,000 futures. Redesigned for shopkeepers, with saving going into mutual funds where there is no fee per debit and the money made on loans that partner lenders give to proven savers, {N('rd_var_base_p')} futures pay back. If savers who proved themselves keep borrowing after they stop saving, {N('rd_var_grad_p')}. If {N('rd_grid_takeup_20')} of them takes a loan each year, {N('rd_var_grad_20_p')}. And if we can win each shopkeeper for {N('rd_target_cac')}, {N('rd_var_best_p')}. The rest of the deck explains each step and what must be true.""")

# ================================================================ NEW: what Bachatt does differently
def design_card(head, rows_, bg=CARD, border="#E3DDD0"):
    body = "".join(p(f"<b>{a}</b>", 24, MUTED) + p(b, 28, INK) for a, b in rows_)
    return card(p(head, 32, INK, extra="font-weight:600") + body, pad=32, gap=10, bg=bg, border=border)


page("What we were missing",
     "Bachatt avoids our biggest cost: saving through mutual funds has no fee per debit.",
     '<div style="display:grid;grid-template-columns:1fr 1fr;gap:28px">'
     + design_card("Our first design", [("Where the money goes", "half digital gold, half funds and FDs"),
                                         ("Cost of each debit", f"{F('ev_debit_gst')} to a payment company"),
                                         ("What earns the money", "the margin on gold")])
     + design_card("Bachatt's design", [("Where the money goes", "debt mutual funds"),
                                         ("Cost of each debit", f"{F('mf_distributor_fee')}: the fund house pays the exchange"),
                                         ("What earns the money", f"loans {F('bachatt_loans')} through partner lenders")], bg=SAND, border=SAND)
     + "</div>"
     + caption(f"Bachatt claims {F('bachatt_users')} users; its fund transactions suggest {F('bachatt_daily_savers')} saving daily."),
     "Cafemutual (BSE StAR MF fees); Bachatt press release, Mar 2026. research/xs_bachatt.csv.",
     f"""Why did Bachatt get funded when our model says this business loses money? Two differences. First, it sells daily saving as mutual-fund SIPs through the exchange's fund platform, where the distributor pays {F('mf_distributor_fee')} per transaction; the fund house pays the exchange {F('amc_fee')}. Our biggest cost, {F('ev_debit_gst')} on every debit, disappears. Second, savings is not where it makes money: it lends, {F('bachatt_loans')}, through partner banks and NBFCs. It claims {F('bachatt_users')} users, though its fund transactions suggest {F('bachatt_daily_savers')} save daily. Funding also reflects a bet on growth, not proven profits.""")

# ================================================================ NEW: one loan vs five years of saving
page("What we were missing",
     f"One {N('rd_loan_ticket')} loan earns us {N('rd_one_loan')}; five years of a saver's savings earn {N('rd_stayer_trail_5y')}.",
     viz.share_bars([("Five years of one saver's savings (the fund's fee to us)", V("rd_stayer_trail_5y") / V("rd_one_loan"), N("rd_stayer_trail_5y"), LBLUE),
                     (f"One {N('rd_loan_ticket')} loan through a partner lender ({N('rd_loan_fee')} fee)", 1.0, N("rd_one_loan"), BLUE)], label_w=760, track_w=640)
     + p("So saving is the hook and the filter; the loans pay for the business.", 32, INK, extra="font-weight:600"),
     "Shopkeeper who saves for five years at the evidence middle; loan net of fee clawback and handling cost. tables/redesign_deck.csv.",
     f"""This is why the answer lies in lending, as you said. A shopkeeper who saves daily for five years earns us about {N('rd_stayer_trail_5y')} in fund fees over the whole time. One {N('rd_loan_ticket')} loan that a partner lender makes to them, with a {N('rd_loan_fee')} fee to us, earns {N('rd_one_loan')} after fees taken back on bad loans and our handling cost. So saving can't pay for itself; its job is to attract good customers and to show, through months of steady saving, who can be trusted with a loan.""")

# ================================================================ NEW: the redesign flow
flow = [("1. Save daily", "Shopkeeper saves into a debt mutual fund; no fee per debit"),
        ("2. Prove it", "Six months of steady saving shows cash flow; credit score checked"),
        ("3. Borrow", "A partner lender offers an unsecured loan, books it and carries the risk"),
        ("4. We earn", "1–3% of each loan, taken back if it goes bad early; repeat loans")]
Wf, Hf, Gf = 380, 300, 48
fb = "".join(f'<div style="position:absolute;left:{k * (Wf + Gf)}px;top:0;width:{Wf}px;height:{Hf}px;background:{CARD if k < 3 else SAND};border:2px solid {INK};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:10px">'
             f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p>'
             f'<p style="font-size:28px;line-height:1.3;color:{INK}">{b}</p></div>' for k, (a, b) in enumerate(flow))
fa = "".join(f'<x-connector x1="{k * (Wf + Gf) + Wf + 4}" y1="{Hf // 2}" x2="{(k + 1) * (Wf + Gf) - 4}" y2="{Hf // 2}" style="color:{ORANGE};border-width:3px"></x-connector>' for k in range(3))
page("The redesign",
     "The redesign: saving proves who is reliable; partner lenders lend; we earn a fee.",
     f'<div style="position:relative;width:1664px;height:{Hf}px">{fb}{fa}</div>'
     + caption(f"Plus insurance and other products, and SEBI's bonus of {F('sebi_women_bonus')} per new woman or small-town investor."),
     "Design from the founder's idea; fees and rules: research/xs_lending.csv, xs_bachatt.csv.",
     f"""The redesign in four steps. A shopkeeper saves a little every day into a debt mutual fund; through the exchange's fund platform there is no fee per debit. After six months, the saving record shows steady cash flow, and with a credit-score check that identifies who is reliable. A partner bank or NBFC offers them an unsecured loan, books it and carries the credit risk. We earn a referral fee of 1 to 3% of the loan, which the lender takes back if the loan goes bad early, and repeat loans follow. Insurance and other products add a little, and SEBI now pays distributors up to {F('sebi_women_bonus')} for each new woman or small-town investor.""")

# ================================================================ NEW: the redesign, one customer at target
T_ = "rd_target"
page("The redesign",
     f"A customer pays back in {N('rd_target_payback')} if we win them for {N('rd_target_cac')} and {N('rd_grid_takeup_20')} borrow each year.",
     viz.waterfall([("To win a shopkeeper", -V(T_ + "_cac"), "−" + N(T_ + "_cac"), "cost"),
                    ("What their savings earn us", V(T_ + "_savings"), "+" + N(T_ + "_savings"), "income"),
                    (f"Loans to proven savers, {N('rd_grid_takeup_20')} a year", V(T_ + "_loans"), "+" + N(T_ + "_loans"), "income"),
                    ("Everything else we sell them", V(T_ + "_other"), "+" + N(T_ + "_other"), "income"),
                    ("Serving them, with no fee per debit", -V(T_ + "_serve"), "−" + N(T_ + "_serve"), "cost"),
                    ("What one customer is worth to us", 0.0, N(T_ + "_net"), "total")])
     + p(f"<b>At today's evidence it is {N('rd_centre_net')}:</b> {N('rd_centre_cac')} to win a shopkeeper, and {N('rd_centre_takeup')} borrowing.", 28, INK),
     "One shopkeeper won, five years, discounted; evidence middle otherwise. tables/redesign_deck.csv.",
     f"""One shopkeeper under the redesign. Win them for {N('rd_target_cac')}. Their savings earn us {N(T_ + '_savings')}, loans to them earn {N(T_ + '_loans')} if {N('rd_grid_takeup_20')} proven savers takes a loan each year, and everything else we sell adds {N(T_ + '_other')}. Serving them costs {N(T_ + '_serve')}, now that there is no fee per debit. So each customer is worth {N(T_ + '_net')}, and pays back in {N('rd_target_payback')}. At today's evidence, though, winning a shopkeeper costs about {N('rd_centre_cac')} and the middle of the evidence is {N('rd_centre_takeup')} borrowing, which leaves each customer at {N('rd_centre_net')}. The next slide shows how the odds move between the two.""")

# ================================================================ NEW: what must be true (odds grid)
gc = (150, 250, 400, 500)
gt = (5, 10, 20, 30)
gvals = [[V(f"rd_grid_{c_}_{t_}_p") for t_ in gt] for c_ in gc]
gdisp = {round(V(f"rd_grid_{c_}_{t_}_p"), 6): N(f"rd_grid_{c_}_{t_}_p") for c_ in gc for t_ in gt}
page("What must be true",
     "Two things decide it: what it costs to win a shopkeeper, and how many borrow.",
     viz.heatmap([N(f"rd_grid_cac_{c_}") + (" (about today's evidence)" if c_ == 500 else "") for c_ in gc],
                 [N(f"rd_grid_takeup_{t_}") for t_ in gt], gvals, lambda v: gdisp[round(v, 6)],
                 row_head="Cost to win", col_head="Proven savers who take a loan each year", cell_w=250, label_w=420)
     + anchors([(F("paytm_borrow_rate"), "a year: Paytm's most engaged merchants who borrow", "Paytm results, 2026"),
                (F("fintech_borrow_rate"), "a year: ordinary fintech users taking any loan or cover", "Paytm results, 2026")]),
     "Futures in which a customer pays back within five years; 2,000 futures per cell. tables/redesign_grid.csv.",
     f"""This is what must be true. Down the side, what it costs to win a shopkeeper who starts saving; across, how many proven savers take a loan each year. Each cell is the share of futures in which a customer pays back. At today's evidence, about {N('rd_grid_cac_500')} to win, even {N('rd_grid_takeup_20')} borrowing pays back in only {N('rd_grid_500_20_p')}. At {N('rd_grid_cac_250')} to win and {N('rd_grid_takeup_20')} borrowing, {N('rd_grid_250_20_p')}. For comparison, Paytm's most engaged merchants borrow at {F('paytm_borrow_rate')} a year; ordinary fintech users take any product at {F('fintech_borrow_rate')}. So we need the take-up of the best-placed player in India, and half today's cost to win a customer.""")

# ================================================================ SALARIED: the customer
page("The customer",
     "Our customer: salaried blue-collar workers, reached through their employers.",
     anchors([(F("salaried_pay"), "a month: average urban salaried pay (office staff included)", "PLFS 2025"),
              (F("salaried_capacity"), "the loan a ₹18–26k salary can carry under RBI's cap", "derived"),
              (F("salaried_tenure"), "average blue-collar tenure; most hires are temporary", "Deloitte, 2025"),
              (F("ewa_ticket"), "salary advances already repaid straight from pay", "an NBFC, via a blog, 2025")])
     + p("Factory, warehouse, security, facility and retail staff: a steady salary, an employer who can deduct from pay, and real need for credit.", 30, INK),
     "research/segments.csv (SG-07, SG-14, SG-22, SG-40).",
     f"""Our customer is the salaried blue-collar worker: factory, warehouse, security, facility-management and retail staff. Urban salaried pay averages {F('salaried_pay')} a month, though that includes office staff; a salary of ₹18–26k can carry a loan of {F('salaried_capacity')} under RBI's cap. Jobs are short, {F('salaried_tenure')} on average, and most hires are temporary. What makes them different from riders or shopkeepers is the employer: it can bring them to us and deduct saving and repayments from pay. Salary advances of {F('ewa_ticket')} are already repaid that way.""")

# ================================================================ SALARIED: the answer staircase
stair_s = [("As first designed: gold, a fee on every debit", 0.004, N("rd_original_p"), ORANGE),
           ("Salaried redesign, loans stop when they change jobs", V("rs_var_job_p"), N("rs_var_job_p"), LBLUE),
           ("+ the account moves with the worker", V("rs_var_port_p"), N("rs_var_port_p"), LBLUE),
           (f"+ {N('rd_grid_takeup_20')} of them borrows each year", V("rs_var_port_20_p"), N("rs_var_port_20_p"), BLUE),
           (f"+ we win each worker through employers for {N('rs_target_cac')}", V("rs_var_best_p"), N("rs_var_best_p"), INK)]
page("The answer in one picture",
     f"As designed, no future pays back; redesigned for salaried workers, {N('rs_var_best_p')} can.",
     viz.share_bars([(a, b / V("rs_var_best_p"), c, d) for a, b, c, d in stair_s], label_w=760, track_w=640)
     + caption("Futures in which a worker pays back what it cost to win them, within five years. Each step adds one change to the one above."),
     "Original: 10,000 futures. Salaried redesign: 4,000 futures per step. tables/rs_variants.csv.",
     f"""The whole note in one picture. As first designed, no customer pays back in any of 10,000 futures. Redesigned for salaried workers, saving from pay into mutual funds with no fee per debit and earning on loans that partner lenders make to proven savers, {N('rs_var_job_p')} futures pay back if loans stop when a worker changes jobs; {N('rs_var_port_p')} if the account moves with them; {N('rs_var_port_20_p')} if {N('rd_grid_takeup_20')} borrow each year; and {N('rs_var_best_p')} if we can also win each worker through employers for {N('rs_target_cac')}.""")

# ================================================================ SALARIED: which customer
segbars = [(f"Delivery riders (loans of {F('rider_loans')})", V("seg_riders_20"), N("seg_riders_20"), LBLUE),
           ("Drivers and home-service workers (vehicle loans)", V("seg_drivers_20"), N("seg_drivers_20"), LBLUE),
           ("Shopkeepers (already served by Paytm and BharatPe)", V("seg_shopkeepers_20"), N("seg_shopkeepers_20"), LBLUE),
           ("Salaried workers through employers", V("seg_salaried_20"), N("seg_salaried_20"), BLUE)]
page("Which customer",
     f"Salaried workers are worth the most: we could pay up to {N('seg_salaried_20')} to win one.",
     viz.share_bars([(a, b / V("seg_salaried_20"), c, d) for a, b, c, d in segbars], label_w=760, track_w=640)
     + caption(f"The most we could pay to win one customer and still break even, if {N('rd_grid_takeup_20')} borrow each year. Same redesign for every group; only loan size and how long people stay differ."),
     "model/segment_value.py: tables/segment_value.csv; evidence research/segments.csv.",
     f"""Which customer? The same redesign, run for each group, with only what differs between them changed: how big a loan they can take and how long they keep saving. Delivery riders actually borrow {F('rider_loans')}, so even if {N('rd_grid_takeup_20')} borrow, a rider is worth at most {N('seg_riders_20')}. Drivers and home-service workers need vehicle loans: {N('seg_drivers_20')}. Shopkeepers: {N('seg_shopkeepers_20')}, but Paytm and BharatPe already lend to them. Salaried workers reached through employers stay longest and can carry the biggest loans: {N('seg_salaried_20')}, if their account moves with them when they change jobs ({N('seg_salaried_job_20')} if loans stop at the job change). Women's savings groups and farmers were ruled out: their loans are small or already subsidised.""")

# ================================================================ SALARIED: the redesign flow
flow_s = [("1. Save from pay", "The employer deducts a fixed amount each payday into a debt fund; enrolled automatically, free to leave"),
          ("2. Prove it", "Six months of saving, a steady salary and a credit-score check"),
          ("3. Borrow", "A partner lender offers an unsecured loan, repaid from pay, and carries the risk"),
          ("4. Move with them", "Account and loan follow the worker to a new job; we earn 1–3% of each loan")]
fbs = "".join(f'<div style="position:absolute;left:{k * (Wf + Gf)}px;top:0;width:{Wf}px;height:{Hf}px;background:{CARD if k < 3 else SAND};border:2px solid {INK};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:10px">'
              f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p>'
              f'<p style="font-size:28px;line-height:1.3;color:{INK}">{b}</p></div>' for k, (a, b) in enumerate(flow_s))
page("The redesign",
     "The redesign: save from pay, prove it, borrow, and keep the account when you change jobs.",
     f'<div style="position:relative;width:1664px;height:{Hf}px">{fbs}{fa}</div>'
     + caption(f"Automatic enrolment matters: a UK payroll trial got {F('uk_optin')} saving when workers had to opt in, {F('uk_optout')} when enrolled automatically."),
     "Design: founder's idea + research/segments.csv (SG-08, SG-09, SG-40).",
     f"""The redesign for salaried workers in four steps. One: the employer deducts a fixed amount each payday into a debt mutual fund, with workers enrolled automatically and free to leave; there is no fee per debit. Two: after six months of saving, a steady salary and a credit-score check show who is reliable. Three: a partner bank or NBFC offers an unsecured loan, repaid from pay, and carries the credit risk. Four: when the worker changes jobs, the account and the loan go with them; we earn 1 to 3% of each loan. Automatic enrolment matters: in a UK payroll trial, {F('uk_optin')} of new joiners saved when they had to opt in and {F('uk_optout')} when enrolled automatically.""")

# ================================================================ SALARIED: one worker at target
S_ = "rs_target"
page("The redesign",
     f"A worker pays back in {N('rs_target_payback')} if we win them for {N('rs_target_cac')} and {N('rd_grid_takeup_20')} borrow each year.",
     viz.waterfall([("To win a worker through their employer", -V(S_ + "_cac"), "−" + N(S_ + "_cac"), "cost"),
                    ("What their savings earn us", V(S_ + "_savings"), "+" + N(S_ + "_savings"), "income"),
                    (f"Loans to proven savers, {N('rd_grid_takeup_20')} a year", V(S_ + "_loans"), "+" + N(S_ + "_loans"), "income"),
                    ("Everything else we sell them", V(S_ + "_other"), "+" + N(S_ + "_other"), "income"),
                    ("Serving them, with no fee per debit", -V(S_ + "_serve"), "−" + N(S_ + "_serve"), "cost"),
                    ("What one worker is worth to us", 0.0, N(S_ + "_net"), "total")])
     + p(f"<b>At today's consumer evidence it is {N('rs_today_net')}:</b> {N('rs_today_cac')} to win (no employer figure is published), {N('rs_takeup_mid')} borrowing.", 28, INK),
     "One worker won, five years, discounted; evidence middle otherwise. tables/rs_deck.csv.",
     f"""One salaried worker under the redesign. Win them through their employer for {N(S_ + '_cac')}. Their savings earn us {N(S_ + '_savings')}; loans earn {N(S_ + '_loans')} if {N('rd_grid_takeup_20')} proven savers borrow each year; everything else we sell adds {N(S_ + '_other')}. Serving them costs {N(S_ + '_serve')}. Each worker is worth {N(S_ + '_net')} and pays back in {N('rs_target_payback')}. At today's consumer evidence, {N('rs_today_cac')} to win and {N('rs_takeup_mid')} borrowing, it is {N('rs_today_net')}. No one publishes what the employer route costs, so that is the first thing to measure.""")

# ================================================================ SALARIED: what must be true (odds grid)
gc_s = (100, 250, 400, 500)
gvals_s = [[V(f"rs_grid_{c_}_{t_}_p") for t_ in gt] for c_ in gc_s]
gdisp_s = {round(V(f"rs_grid_{c_}_{t_}_p"), 6): N(f"rs_grid_{c_}_{t_}_p") for c_ in gc_s for t_ in gt}
page("What must be true",
     "Two things decide it: what it costs to win a worker, and how many borrow.",
     viz.heatmap([N(f"rs_grid_cac_{c_}" if c_ == 100 else f"rd_grid_cac_{c_}") + (" (consumer apps today)" if c_ == 500 else "") for c_ in gc_s],
                 [N(f"rd_grid_takeup_{t_}") for t_ in gt], gvals_s, lambda v: gdisp_s[round(v, 6)],
                 row_head="Cost to win", col_head="Proven savers who take a loan each year", cell_w=250, label_w=420)
     + anchors([(F("paytm_borrow_rate"), "a year: Paytm's most engaged merchants who borrow", "Paytm results, 2026"),
                (F("fintech_borrow_rate"), "a year: ordinary fintech users taking any loan or cover", "Paytm results, 2026")]),
     "Futures in which a worker pays back within five years; 2,000 futures per cell; account moves with the worker. tables/rs_grid.csv.",
     f"""This is what must be true. Down the side, what it costs to win a worker who starts saving; across, how many proven savers take a loan each year. Each cell is the share of futures in which a worker pays back. At {N('rd_grid_cac_250')} to win and {N('rd_grid_takeup_10')} borrowing, {N('rs_grid_250_10_p')}; at {N('rd_grid_takeup_20')}, {N('rs_grid_250_20_p')}. Even at the consumer-app cost of about {N('rd_grid_cac_500')}, {N('rd_grid_takeup_20')} borrowing gives {N('rs_grid_500_20_p')}. The cost to win a worker drives {N('rs_drv_cac')} of the outcome, and the employer route is the one place it might be low.""")

# ================================================================ NEW: risks
risks = [("The payroll route isn't final", "SEBI's rule letting employers pay into mutual funds is a draft, for listed or PF-registered employers only."),
         ("People change jobs", f"{F('staffing_exit')} of staffing workers leave each quarter; the account and loan must move with them."),
         ("The biggest employers are taken", f"The two largest staffing firms ({F('staffing_reach')} workers) already have finance partners; we start mid-size."),
         ("Demand for big loans is unproven", f"Today's salary advances are {F('ewa_ticket')}; and good savers may not be good borrowers.")]
page("Risks",
     "Four risks could break it; the first is that the payroll route isn't final yet.",
     '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">' + "".join(card(p(f"<b>{a}</b>", 30, INK) + p(b, 26, BODY), pad=28, gap=10) for a, b in risks) + "</div>",
     "SEBI draft circular, May 2026; Quess and TeamLease filings; research/segments.csv (SG-06, SG-08, SG-40, SG-47).",
     f"""Four things could break it. One, the payroll route is not final: SEBI's rule letting employers pay into mutual funds on workers' behalf is still a draft, and it covers only listed or PF-registered employers. Two, people change jobs: {F('staffing_exit')} of staffing workers leave every quarter, so the account and the loan have to move with them, or most of the value goes. Three, the biggest employers are taken: the two largest staffing firms, with {F('staffing_reach')} workers, already work with finance partners, so we would start with mid-size employers. Four, demand for big loans is unproven: today's salary advances are {F('ewa_ticket')}, and the belief that good savers make good borrowers has not been tested.""")

# ================================================================ NEW: two cheap tests
tests2 = [("Test 1 · The employer route", "Sign 2–3 mid-size employers and enrol their workers automatically, free to leave",
           f"Pass: {N('rs_target_cac')} or less per worker who keeps saving, and about half staying enrolled ({F('uk_optout')} in the UK trial)"),
          ("Test 2 · Lender appetite", "Get a lender's term sheet for loans repaid from pay, after six months of saving",
           f"Pass: a {N('rd_loan_fee')} fee, and {N('rd_grid_takeup_20')} savers who qualify and want a loan")]
Wt2, Ht2 = 760, 320
tb2 = "".join(f'<div style="position:absolute;left:{k * (Wt2 + 144)}px;top:0;width:{Wt2}px;height:{Ht2}px;background:{CARD};border:2px solid {INK};border-radius:16px;padding:28px;display:flex;flex-direction:column;gap:12px">'
              f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p>'
              f'<p style="font-size:30px;font-weight:600;line-height:1.25;color:{INK}">{b}</p><p style="font-size:26px;line-height:1.3;color:{BODY}">{c}</p></div>'
              for k, (a, b, c) in enumerate(tests2))
ta2 = f'<x-connector x1="{Wt2 + 4}" y1="{Ht2 // 2}" x2="{Wt2 + 140}" y2="{Ht2 // 2}" style="color:{ORANGE};border-width:3px"></x-connector>'
page("Next",
     "Two cheap tests settle it before any build: the employer route, and who will borrow.",
     f'<div style="position:relative;width:1664px;height:{Ht2}px">{tb2}{ta2}</div>'
     + p("Also measure who keeps saving after changing jobs. Stop at the first test that fails.", 28, INK),
     "Pass lines from the redesign grid (tables/redesign_grid.csv).",
     f"""Two cheap tests come before any build. First, the employer route: sign two or three mid-size employers, enrol their workers automatically with a free choice to leave, and count the cost per worker who keeps saving; the pass line is {N('rs_target_cac')}, with about half staying enrolled, as in the UK trial's {F('uk_optout')}. Second, lender appetite: get a term sheet from a bank or NBFC for loans repaid from pay after six months of saving, at a {N('rd_loan_fee')} fee, and check how many savers would qualify and want one; we need about {N('rd_grid_takeup_20')} a year. Alongside, measure how many keep saving after changing jobs. If either test fails, stop.""")

# ================================================================ LEND: the hook
hook = [(F("mf_distributor_fee"), "fee per debit: saving goes into debt mutual funds through the exchange's fund platform", "Cafemutual; exchange rules"),
        (N("rd_stayer_trail_5y"), "what one saver's fund fees earn us over five years", "model"),
        ("A record", "of who saves steadily: the best signal we can get before lending", "the idea")]
page("The hook",
     "Savings is the hook: simple debt mutual funds, cheap to run; it earns little, and doesn't need to.",
     anchors(hook)
     + p(f"On its own, a savings app loses money: our first plan lost {N('ltv_evidence_everything_mid_loss')} on every customer (appendix). Saving is how we find people and learn who is reliable.", 30, INK),
     "research/xs_bachatt.csv (XB-01); tables/rs_deck.csv, ltv_cases.csv.",
     f"""Saving is the front door, not the business. Like Bachatt, we keep it simple: daily or monthly saving into debt mutual funds, bought through the exchange's fund platform, where we pay {F('mf_distributor_fee')} per debit. A saver's fund fees earn us only about {N('rd_stayer_trail_5y')} over five years, so as a standalone business saving loses money; our first plan lost {N('ltv_evidence_everything_mid_loss')} per customer. That is fine. Saving's job is to bring people in cheaply and to show, month after month, who is reliable enough to lend to.""")

# ================================================================ LEND: the engine
eng = [(f"Refer it to a lender ({N('rd_loan_fee')} fee)", V("ln_shop_ref"), N("ln_shop_ref"), LBLUE),
       ("Lend ourselves, if our savers repay better", V("ln_shop_safe"), N("ln_shop_safe"), BLUE),
       ("Lend ourselves, at normal industry losses", V("ln_shop_normal"), N("ln_shop_normal"), BLUE),
       ("Lend ourselves, at today's digital-lender losses", 0.004 * V("ln_shop_safe"), N("ln_shop_today"), ORANGE)]
page("The engine",
     f"Lending ourselves earns {N('ln_shop_normal')} on a {N('ln_shop_size')} loan, against {N('ln_shop_ref')} for referring it.",
     viz.share_bars([(a, b / V("ln_shop_safe"), c, d) for a, b, c, d in eng], label_w=760, track_w=640)
     + caption(f"One {N('ln_shop_size')} shopkeeper loan over 12 months at 26% a year, after what we pay to borrow ({F('nbfc_cof_range')}), bad loans and running costs. Today's digital lenders lose {F('digital_credit_cost')} of their book a year."),
     "model/lend_self.py: tables/lend_loan.csv; evidence research/levers.csv (LEV-014..029), lend_self.csv.",
     f"""The engine is lending, and lending ourselves earns far more than referring. On one {N('ln_shop_size')} shopkeeper loan over a year, a referral fee earns us about {N('ln_shop_ref')}. Lending it from our own NBFC, after paying {F('nbfc_cof_range')} to borrow the money and covering bad loans and running costs, earns {N('ln_shop_normal')} at normal industry losses and {N('ln_shop_safe')} if our savers repay better. But at the losses and running costs digital lenders report today, {F('digital_credit_cost')} of the book lost a year and {F('digital_running_cost')} spent running it, the same loan loses {N('ln_shop_today')}. So everything depends on how well our borrowers repay.""")

# ================================================================ LEND: the crux
crux = [(f"Our savers repay better ({N('lend_credit_safe')} lost a year)", V("lc_shop_safe_20"), N("lc_shop_safe_20"), BLUE),
        (f"Normal industry losses ({N('lend_credit_normal')} a year)", V("lc_shop_normal_20"), N("lc_shop_normal_20"), LBLUE),
        (f"Today's digital lenders ({N('lend_credit_today')} a year)", 0.004 * V("lc_shop_safe_20"), N("lc_shop_today_20"), ORANGE)]
page("The crux",
     "Everything rests on one claim: our savers repay better than today's digital borrowers.",
     viz.share_bars([(a, b / V("lc_shop_safe_20"), c, d) for a, b, c, d in crux], label_w=760, track_w=640)
     + caption(f"What one shopkeeper is worth to us over five years, after the cost to win them, if {N('lc_takeup_20')} proven savers borrow each year.")
     + anchors([(F("founder_repeat_late"), "of repeat loans went late in your past lending", "your data"),
                (F("crif_big_ticket"), "of loans above ₹50,000 ever go 90+ days late", "CRIF"),
                (F("digital_credit_cost"), "of the loan book lost a year by digital lenders today", "ratings notes")]),
     "model/lend_self.py: tables/lend_customer.csv. Running costs move with losses: 3% / 5% / 8% a year.",
     f"""This is the crux. If people who save with us repay better than today's digital-lending borrowers, losing about {N('lend_credit_safe')} of the book a year, each shopkeeper we win is worth {N('lc_shop_safe_20')}. At normal industry losses, {N('lend_credit_normal')}, it is {N('lc_shop_normal_20')}. At what digital lenders lose today, it is {N('lc_shop_today_20')}. The signs point the right way: in your past lending, repeat borrowers went late only {F('founder_repeat_late')} of the time, and CRIF finds only {F('crif_big_ticket')} of loans above ₹50,000 ever go seriously late. But no Indian study yet shows that saving itself predicts better repayment. That is what we must prove.""")

# ================================================================ LEND: one customer
LTS = "lt_safe"
page("One customer",
     f"If savers repay better, one shopkeeper earns us {N('lt_safe_net')} and pays back in {N('lt_safe_pb')}.",
     viz.waterfall([("To win a shopkeeper", -V(LTS + "_cac"), "−" + N(LTS + "_cac"), "cost"),
                    ("What their savings earn us", V(LTS + "_savings"), "+" + N(LTS + "_savings"), "income"),
                    (f"Interest and fees on our loans, {N('lc_takeup_20')} borrowing a year", V(LTS + "_loans"), "+" + N(LTS + "_loans"), "income"),
                    ("Insurance, pension, bills and the rest", V(LTS + "_other"), "+" + N(LTS + "_other"), "income"),
                    ("Serving them", -V(LTS + "_serve"), "−" + N(LTS + "_serve"), "cost"),
                    ("What one shopkeeper is worth to us", 0.0, N(LTS + "_net"), "total")]),
     "One shopkeeper won at today's cost to win; five years, discounted; loans net of funding, bad loans and running costs. tables/lend_target.csv.",
     f"""One shopkeeper, worked through. Winning them costs about {N(LTS + '_cac')}. Their savings earn us {N(LTS + '_savings')} over five years. If {N('lc_takeup_20')} proven savers borrow each year and our losses stay near {N('lend_credit_safe')} a year, our loans to them earn {N(LTS + '_loans')} after funding, bad loans and running costs. Insurance, pension, bills and the rest add {N(LTS + '_other')}; serving them costs {N(LTS + '_serve')}. So each shopkeeper is worth {N(LTS + '_net')}, and we get the cost of winning them back in {N('lt_safe_pb')}. Other products help a little; the loans carry it.""")

# ================================================================ LEND: borrowing
cases_ = [("Our savers repay better", "safe"), ("Normal industry losses", "normal"), ("Today's digital lenders", "today")]
tks = (10, 20, 35, 50)
gv = [[V(f"lc_shop_{c}_{t}") for t in tks] for _, c in cases_]
gd = {round(V(f"lc_shop_{c}_{t}"), 4): N(f"lc_shop_{c}_{t}") for _, c in cases_ for t in tks}
page("Borrowing",
     f"The more savers borrow, the safer the bet: at {N('lc_takeup_35')} borrowing it works even at normal losses.",
     viz.heatmap([a for a, _ in cases_], [N(f"lc_takeup_{t}") for t in tks], gv, lambda v: gd[round(v, 4)],
                 row_head="If losses are…", col_head="Proven savers who borrow each year", cell_w=250, label_w=420)
     + anchors([(F("brazil_takeup"), "of eligible workers took a payroll loan in Brazil's first year", "Brazil, 2026"),
                (F("rider_bike_borrowed"), "delivery riders borrowed to buy their bike", "IDinsight"),
                (F("paytm_borrow_rate"), "a year: Paytm's most engaged merchants who borrow", "Paytm, 2026")]),
     "What one shopkeeper is worth to us over five years, after today's cost to win them. tables/lend_customer.csv.",
     f"""You expect more savers to borrow than our cautious middle case, and it matters. Each cell is what one shopkeeper is worth to us. If {N('lc_takeup_35')} of proven savers borrow each year, a shopkeeper is worth {N('lc_shop_normal_35')} even at normal industry losses; if half do, {N('lc_shop_normal_50')}. Demand is there: when Brazil let workers borrow against pay, {F('brazil_takeup')} took a loan in the first year, and {F('rider_bike_borrowed')} delivery riders borrowed to buy their bike. But borrowing more cannot rescue today's digital-lender losses: that row stays negative.""")

# ================================================================ LEND: who
who = [(f"Shopkeepers ({N('ln_shop_size')} loans)", V("lc_shop_safe_20"), N("lc_shop_safe_20"), BLUE),
       (f"Drivers and home-service workers ({N('ln_drivers_size')} loans, via platforms)", V("lc_drivers_safe_20"), N("lc_drivers_safe_20"), BLUE),
       (f"Delivery riders ({N('ln_riders_size')} loans)", 0.004 * V("lc_shop_safe_20"), N("lc_riders_safe_20"), ORANGE)]
page("Who",
     "Who: shopkeepers, then drivers and home-service workers; riders can save, but their loans are too small to pay.",
     viz.share_bars([(a, b / V("lc_shop_safe_20"), c, d) for a, b, c, d in who], label_w=760, track_w=640)
     + caption(f"What one customer is worth to us, if savers repay better and {N('lc_takeup_20')} borrow each year. Salaried workers through employers were set aside: that route failed in your past lending.")
     + anchors([(F("payout_deduction"), "repayment from payouts exists for Zomato's restaurants (NeoGrowth), not its riders or drivers", "NeoGrowth"),
                (F("crif_big_ticket"), "of loans above ₹50,000 go seriously late; small ones go late more often", "CRIF")]),
     "model/lend_self.py: tables/lend_customer.csv; research/segments.csv, lend_self.csv.",
     f"""Who to serve follows from the loan size. Shopkeepers can carry {N('ln_shop_size')} loans and are worth {N('lc_shop_safe_20')} each. Drivers and home-service workers need {N('ln_drivers_size')} vehicle and tool loans, worth {N('lc_drivers_safe_20')} each. Repayment straight from platform payouts exists today only for Zomato's restaurants (NeoGrowth); we found no current case for riders or drivers, so we collect from their own bank. Delivery riders borrow about {N('ln_riders_size')} at a time, which never covers the cost of winning them ({N('lc_riders_safe_20')}); they can save with us but will not pay. Salaried workers through employers were set aside because that route failed in your past lending.""")

# ================================================================ LEND: how big
page("How big",
     f"How big it must get: {N('sc_shop_safe_20_5')} shopkeepers a year carry an NBFC; the pool is in crores.",
     anchors([(N("sc_shop_safe_20_5"), "shopkeepers won a year to cover an NBFC's running cost, if savers repay better", "model"),
              (N("sc_shop_normal_20_5"), "a year if losses are normal for the industry", "model"),
              (F("udyam_micro"), "micro enterprises on Udyam", "Udyam, 2026"),
              (F("gig_fy25"), "gig workers today, 23.5M by 2030", "NITI Aayog")])
     + p(f"An NBFC needs {F('nbfc_nof')} of capital and costs {F('nbfc_fixed')} a year to run. Co-lending with a bank, keeping {F('colend_min')} of each loan, needs far less capital.", 30, INK),
     "tables/lend_scale.csv (at a ₹5 crore running cost; ₹3–8 crore in the appendix); facts as cited.",
     f"""How big must it get? An NBFC needs {F('nbfc_nof')} of its own capital and costs about {F('nbfc_fixed')} a year to run. Covering that takes {N('sc_shop_safe_20_5')} shopkeepers won a year if savers repay better, or {N('sc_shop_normal_20_5')} at normal losses. The pool is far bigger: {F('udyam_micro')} micro enterprises on Udyam and {F('gig_fy25')} gig workers, heading for 23.5M by 2030. To start with less capital, RBI's co-lending rules from 2026 let us keep as little as {F('colend_min')} of each loan, with a bank lending the rest.""")

# ================================================================ LEND: edge
EDGE = [["Paytm, BharatPe, PhonePe", "shopkeepers", "partner lenders book the loans", "payments data"],
        ["Bachatt", "shopkeepers, self-employed", f"refers loans {F('bachatt_loans')} to partners", "saving"],
        ["Swiggy and its lending partners", "delivery riders", "partner lenders arrange the loans", "earnings data"],
        ["Us", "shopkeepers, drivers", "we lend ourselves, or co-lend", "saving record + your lending know-how"]]
page("Edge",
     "Our edge, if it holds: your lending know-how, lending ourselves, and saving records to pick safer borrowers.",
     table(["Who", "Lends to", "How", "What they judge borrowers on"], EDGE, [28, 22, 26, 24], size=26),
     "Paytm Q4 FY26 release; Bachatt releases; NeoGrowth; research/xs_bachatt.csv, lend_self.csv.",
     f"""Who else is here, and why anyone would choose us. Paytm, BharatPe and PhonePe already lend to shopkeepers through partner lenders, judging them on payments data. Bachatt saves with shopkeepers and refers loans {F('bachatt_loans')} to partners. Swiggy arranges loans for its riders through lending partners; we found no public case of repayments being taken out of payouts, and Zomato's NeoGrowth deduction is for restaurants, not riders. Our edge, if it holds, is three things together: your experience running a lending business with platform partners, lending ourselves instead of referring, and a saving record that should pick out safer borrowers. The last one is unproven, and it is the one that matters.""")

# ================================================================ LEND: risks
risks_l = [("Savers may not repay better", f"Untested in India. Digital lenders lose {F('digital_credit_cost')} of their book a year; at that rate we lose on every loan."),
           ("An NBFC takes capital and time", f"{F('nbfc_nof')} minimum capital, {F('nbfc_fixed')} a year to run, and licences have taken {F('nbfc_licence_time')}."),
           ("Others lend to the same people", f"Paytm ({F('paytm_devices')} device merchants), BharatPe, PhonePe; riders' platforms have NBFC partners."),
           ("The free fund route could change", f"Fund houses pay the exchange {F('amc_fee')} a transaction and could limit tiny daily SIPs.")]
page("Risks",
     "Four risks: savers may not repay better; an NBFC takes capital and time; others lend to the same people; the fund route could change.",
     '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">' + "".join(card(p(f"<b>{a}</b>", 30, INK) + p(b, 26, BODY), pad=28, gap=10) for a, b in risks_l) + "</div>",
     "research/levers.csv (LEV-021..032), xs_bachatt.csv, lend_self.csv.",
     f"""Four things could break it. One, the central claim may be wrong: if our savers repay no better than today's digital-lending borrowers, who cost lenders {F('digital_credit_cost')} of the book a year, we lose money on every loan. Two, an NBFC needs {F('nbfc_nof')} of capital, costs {F('nbfc_fixed')} a year to run, and licences have taken {F('nbfc_licence_time')}; co-lending can bridge that. Three, the big payment apps and the riders' platforms already lend to these people. Four, the free fund route depends on fund houses continuing to pay the exchange {F('amc_fee')} a transaction.""")

# ================================================================ LEND: the test
tflow = [("1. Save", "A first group of shopkeepers and drivers saves daily into debt funds for six months"),
         ("2. Lend", "Offer them ₹50,000–1.5 lakh loans, lending jointly with a bank partner"),
         ("3. Compare", "Track repayment at 6 and 12 months against similar people who did not save")]
Wq, Hq, Gq = 500, 300, 82
tq = "".join(f'<div style="position:absolute;left:{k * (Wq + Gq)}px;top:0;width:{Wq}px;height:{Hq}px;background:{CARD if k < 2 else SAND};border:2px solid {INK};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:10px">'
             f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p>'
             f'<p style="font-size:28px;line-height:1.3;color:{INK}">{b}</p></div>' for k, (a, b) in enumerate(tflow))
tqa = "".join(f'<x-connector x1="{k * (Wq + Gq) + Wq + 4}" y1="{Hq // 2}" x2="{(k + 1) * (Wq + Gq) - 4}" y2="{Hq // 2}" style="color:{ORANGE};border-width:3px"></x-connector>' for k in range(2))
page("Next",
     "One test decides it: lend to early savers and compare how they repay.",
     f'<div style="position:relative;width:1664px;height:{Hq}px">{tq}{tqa}</div>'
     + p(f"Pass: losses near {N('lend_credit_safe')} a year, not {N('lend_credit_today')}, and at least {N('lc_takeup_20')} savers borrowing. Also count what each saver cost to win.", 30, INK),
     "Pass lines from tables/lend_customer.csv.",
     f"""One test settles the crux before we build anything big. Bring a first group of shopkeepers and drivers into daily saving for six months. Then offer them ₹50,000–1.5 lakh loans through a co-lending partner, so we need little capital. Track how they repay at 6 and 12 months against similar people from the same channels who did not save. It passes if losses run near {N('lend_credit_safe')} a year rather than the {N('lend_credit_today')} digital lenders see, and if at least {N('lc_takeup_20')} savers want a loan. Count what each saver cost to win along the way.""")

# ================================================================ STORY: how it works
hw = [("1. Save", "A shopkeeper saves a little every day into a debt mutual fund: no fee per debit for us"),
      ("2. Prove it", "Six months of steady saving, plus a credit check, shows who is reliable"),
      ("3. Borrow", "We lend ₹50,000–2.5 lakh ourselves, or jointly with a bank"),
      ("4. Earn", "The interest pays for winning, serving and the savings")]
Wh, Hh, Gh = 380, 300, 48
hb = "".join(f'<div style="position:absolute;left:{k * (Wh + Gh)}px;top:0;width:{Wh}px;height:{Hh}px;background:{CARD if k < 3 else SAND};border:2px solid {INK};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:10px">'
             f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p>'
             f'<p style="font-size:28px;line-height:1.3;color:{INK}">{b}</p></div>' for k, (a, b) in enumerate(hw))
ha = "".join(f'<x-connector x1="{k * (Wh + Gh) + Wh + 4}" y1="{Hh // 2}" x2="{(k + 1) * (Wh + Gh) - 4}" y2="{Hh // 2}" style="color:{ORANGE};border-width:3px"></x-connector>' for k in range(3))
page("How it works",
     "How it works: saving shows us who is reliable; lending to them ourselves pays for everything.",
     f'<div style="position:relative;width:1664px;height:{Hh}px">{hb}{ha}</div>'
     + p("Like Bachatt, saving stays simple and cheap. Unlike Bachatt, we lend ourselves instead of passing customers to other lenders.", 30, INK),
     "Design agreed with the founder, 2 Oct 2026.",
     """The business in four steps. A shopkeeper saves a little every day into a debt mutual fund, bought through the exchange's fund platform, so each debit costs us nothing. Six months of steady saving, plus a credit check, tells us who is reliable. We then lend to them ourselves, from our own NBFC or jointly with a bank, and the interest pays for winning the customer, serving them and running the savings. Saving is the hook and the filter; lending is the engine.""")

# ================================================================ STORY: why lend
wl = [("Five years of one saver's savings (fund fees)", V("rd_stayer_trail_5y"), N("rd_stayer_trail_5y"), LBLUE),
      (f"Refer one {N('ln_shop_size')} loan to a lender", V("ln_shop_ref"), N("ln_shop_ref"), LBLUE),
      (f"Lend it ourselves, at normal industry losses", V("ln_shop_normal"), N("ln_shop_normal"), BLUE)]
page("Why lend",
     f"Why lend: one {N('ln_shop_size')} loan earns us {N('ln_shop_normal')}; five years of a saver's savings earn {N('rd_stayer_trail_5y')}.",
     viz.share_bars([(a, b / V("ln_shop_normal"), c, d) for a, b, c, d in wl], label_w=760, track_w=640)
     + caption(f"One 12-month shopkeeper loan at 26% a year, after what we pay to borrow ({F('nbfc_cof_range')}), bad loans and running costs."),
     "model/lend_self.py: tables/lend_loan.csv; tables/rs_deck.csv.",
     f"""Why the money has to come from lending. A saver's fund fees earn us about {N('rd_stayer_trail_5y')} over five years. Passing one {N('ln_shop_size')} loan to another lender earns a referral fee of about {N('ln_shop_ref')}. Lending it ourselves, after paying {F('nbfc_cof_range')} for the money, normal bad loans and running costs, earns {N('ln_shop_normal')}. So saving brings people in; lending ourselves pays the bills.""")

# ================================================================ STORY: the funnel
fnl = [("Shopkeepers we win", 1.0, "100", LBLUE),
       ("still saving at six months", V("fn_m6") / 100, N("fn_m6"), LBLUE),
       ("still saving at a year", V("fn_m12") / 100, N("fn_m12"), LBLUE),
       (f"loans they take over five years, if {N('lc_takeup_20')} proven savers borrow a year", V("fn_loans_20") / 100, N("fn_loans_20"), BLUE),
       (f"…if {N('lc_takeup_35')} borrow", V("fn_loans_35") / 100, N("fn_loans_35"), BLUE)]
page("The funnel",
     f"Of 100 shopkeepers we win, {N('fn_m6')} are still saving at six months; {N('fn_loans_20')} loans follow over five years.",
     viz.share_bars([(a, b, c, d) for a, b, c, d in fnl], label_w=760, track_w=640)
     + caption("Those loans carry the business: most people we win never borrow, so each loan must pay for several who don't."),
     "Evidence middle for how long people save; tables/lend_funnel.csv.",
     f"""The funnel explains the economics. Of 100 shopkeepers we win, about {N('fn_m6')} are still saving at six months and {N('fn_m12')} at a year, which is what Indian small-saver evidence suggests. If {N('lc_takeup_20')} proven savers borrow each year, about {N('fn_loans_20')} loans follow over five years; if {N('lc_takeup_35')} do, {N('fn_loans_35')}. Each loan has to pay for the cost of winning and serving several customers who never borrow.""")

# ================================================================ STORY: a typical shopkeeper
LTN = "lt_normal"
page("One customer",
     f"At normal industry losses, one shopkeeper earns us about {N(LTN + '_net')} and pays back in {N(LTN + '_pb')}.",
     viz.waterfall([("To win a shopkeeper", -V(LTN + "_cac"), "−" + N(LTN + "_cac"), "cost"),
                    ("What their savings earn us", V(LTN + "_savings"), "+" + N(LTN + "_savings"), "income"),
                    (f"Our loans to them, {N('lc_takeup_20')} borrowing a year", V(LTN + "_loans"), "+" + N(LTN + "_loans"), "income"),
                    ("Insurance, pension, bills and the rest", V(LTN + "_other"), "+" + N(LTN + "_other"), "income"),
                    ("Serving them", -V(LTN + "_serve"), "−" + N(LTN + "_serve"), "cost"),
                    ("What one shopkeeper is worth to us", 0.0, N(LTN + "_net"), "total")])
     + p(f"<b>If our savers repay better, the same shopkeeper is worth {N('lt_safe_net')}</b> and pays back in {N('lt_safe_pb')}.", 28, INK),
     "One shopkeeper won, five years, discounted; normal industry losses; loans net of funding, bad loans and running costs. tables/lend_target.csv.",
     f"""One shopkeeper, at the middle of the evidence and normal industry losses. Winning them costs about {N(LTN + '_cac')}. Savings earn {N(LTN + '_savings')}, our loans to them {N(LTN + '_loans')} after funding, bad loans and running costs, and other products {N(LTN + '_other')}; serving them costs {N(LTN + '_serve')}. So this shopkeeper is worth about {N(LTN + '_net')} and pays back in {N(LTN + '_pb')}. If our savers repay better, the same shopkeeper is worth {N('lt_safe_net')}.""")

# ================================================================ STORY: how sure
lh = [(float(r["lo"]), float(r["hi"]), float(r["share"])) for r in rd("lmc_hist.csv") if r["segment"] == "shopkeepers"]
page("How sure",
     f"How sure: a shopkeeper pays back in {N('lmc_shop_p')} futures; in the rest we lose money.",
     viz.histogram_marked(lh, height=340, markers=[(V("lmc_shop_p50"), f"typical: {N('lmc_shop_p50')}")], first_row=1)
     + caption(f"Value of one shopkeeper over five years, after the cost to win them, across 10,000 futures with every input drawn from its evidence range. Worst 5%: below {N('lmc_shop_p5')}; best 5%: above {N('lmc_shop_p95')}. The end bars also hold the most extreme 1%."),
     "model/lend_mc.py: tables/lmc_summary.csv, lmc_hist.csv; inputs in the appendix.",
     f"""How sure can we be? I ran the shopkeeper business 10,000 times, drawing every uncertain input from its evidence range: what it costs to win a shopkeeper, how long they save, how many borrow, the rate, the loan size, losses, running costs and what we pay to borrow. A shopkeeper pays back in {N('lmc_shop_p')} of those futures, {N('lmc_shop_p_2y')} within two years. The typical outcome is {N('lmc_shop_p50')}; the worst 5% lose more than {N('lmc_shop_p5')}, the best 5% earn more than {N('lmc_shop_p95')}. Worth pursuing, but not a sure thing.""")

# ================================================================ STORY: what decides it
# each number moved alone, the others at today's evidence (operator, 3 Oct 2026: the variance-share chart "doesn't make sense")
BE = [("What it costs to win a shopkeeper", "cost_to_win", "no more than", "lo", "hi"),
      ("Proven savers who borrow each year", "takeup", "at least", "hi", "lo"),
      ("Interest rate we charge", "rate", "at least", "hi", "lo"),
      ("Losses on loans, a year", "losses", "no more than", "lo", "hi")]
BEROWS = [[lab, N(f"be_{k}_today"), f"{d} {N(f'be_{k}')}",
           f"{N(f'be_{k}_{g}')}: +{N(f'be_{k}_{g}_val')}".replace("+−", "−"), f"{N(f'be_{k}_{b}')}: {N(f'be_{k}_{b}_val')}"] for lab, k, d, g, b in BE]
page("What decides it",
     "Four numbers decide it, and each has little room before a shopkeeper stops paying back.",
     table(["The number", "Today's evidence", "Pays back if it is…", "If it goes well", "If it goes badly"], BEROWS, [30, 15, 21, 17, 17], size=26)
     + p(f"Each row moves one number, with the other three at today's evidence, where a shopkeeper is worth {N('lt_normal_net')}.", 28, INK),
     "One shopkeeper won, five years, discounted; normal industry losses unless the row says otherwise. tables/lend_breakeven.csv.",
     f"""What decides it, in plain numbers. At today's evidence a shopkeeper is worth {N('lt_normal_net')}: positive, but thin. Each of four numbers has little room. Winning a shopkeeper can cost up to {N('be_cost_to_win')}, against about {N('be_cost_to_win_today')} today. At least {N('be_takeup')} of proven savers must borrow each year, against {N('be_takeup_today')} assumed. The rate must stay above {N('be_rate')}, against {N('be_rate_today')}. Losses must stay below {N('be_losses')} a year, against {N('be_losses_today')} for the industry. Each row moves one number with the rest held at today's evidence; if two slip together, the margin goes faster. These are the lines the pilot has to beat.""")

# ================================================================ STORY: the crux within
cr2 = [("If our losses stay at 4% a year or less", V("lmc_shop_p_low"), N("lmc_shop_p_low"), BLUE),
       ("Across all futures", V("lmc_shop_p"), N("lmc_shop_p"), LBLUE),
       ("If losses reach 7% or more, like digital lenders today", V("lmc_shop_p_high"), N("lmc_shop_p_high"), ORANGE)]
page("The crux",
     f"If our savers repay better, the odds rise to {N('lmc_shop_p_low')}; if they don't, they fall to {N('lmc_shop_p_high')}.",
     viz.share_bars([(a, b, c, d) for a, b, c, d in cr2], label_w=760, track_w=640)
     + caption("Futures in which a shopkeeper pays back, split by the loss rate drawn.")
     + anchors([(F("founder_repeat_late"), "of repeat loans went late in your past lending", "your data"),
                (F("crif_big_ticket"), "of loans above ₹50,000 ever go 90+ days late", "CRIF"),
                (F("digital_credit_cost"), "of the book lost a year by digital lenders today", "ratings notes")]),
     "model/lend_mc.py: tables/lmc_summary.csv.",
     f"""The belief at the heart of the idea is that people who save with us repay better. If our losses stay at 4% a year or less, a shopkeeper pays back in {N('lmc_shop_p_low')} futures; if they reach the 7% or more that digital lenders see today, {N('lmc_shop_p_high')}. The signs point the right way: repeat borrowers in your past lending went late only {F('founder_repeat_late')} of the time, and only {F('crif_big_ticket')} of loans above ₹50,000 ever go seriously late. But no Indian study shows that saving itself predicts repayment.""")

# ================================================================ STORY: who
WHO2 = [["Shopkeepers", N("ln_shop_size"), N("lmc_shop_p"), "start here"],
        ["Drivers and home-service workers", N("ln_drivers_size"), N("lmc_drivers_p"), "next, repaying from their own bank; no platform deducts for outside lenders today"],
        ["Delivery riders", N("ln_riders_size"), "never at today's cost to win", "savers only: their loans are too small"],
        ["Salaried workers via employers", N("lmi_loan_size_salaried_mode"), N("lmc_sal_p"), "only at 26%+ rates or low losses (appendix)"]]
page("Who",
     "Who: shopkeepers first; drivers and home-service workers next; riders' loans are too small to pay.",
     table(["Customer", "Typical loan", "Futures that pay back", "Verdict"], WHO2, [28, 16, 20, 36], size=26),
     "model/lend_mc.py, lend_self.py; research/segments.csv, lend_self.csv.",
     f"""Who to serve follows from the loan they can carry. Shopkeepers take {N('ln_shop_size')} loans and pay back in {N('lmc_shop_p')} futures: start there. Drivers and home-service workers need {N('ln_drivers_size')} vehicle and tool loans and pay back in {N('lmc_drivers_p')}; they come next, repaying from their own bank: we found no platform that takes an outside lender's repayments out of payouts today (Zomato's NeoGrowth deduction is for restaurants, not riders). Delivery riders borrow about {N('ln_riders_size')} at a time, which never covers the cost of winning them, so they can save but will not pay. Salaried workers through employers pay back in {N('lmc_sal_p')}: they stay longer but can borrow more cheaply elsewhere, so they pay only at rates of 26% or more, or if taking repayment from pay keeps losses low (appendix).""")

# ================================================================ STORY: salaried workers via employers
sal_cases = [("Losses low (repayment from pay)", "safe"), ("Normal industry losses", "normal"), ("Today's digital lenders", "today")]
srt = (22, 24, 26, 28)
sv = [[V(f"ls_ev_{c}_{r}") for r in srt] for _, c in sal_cases]
sd = {round(V(f"ls_ev_{c}_{r}"), 4): N(f"ls_ev_{c}_{r}") for _, c in sal_cases for r in srt}
page("Salaried",
     "Salaried workers through employers stay longer, but the rate decides it: they pay at 26% or with low losses.",
     viz.heatmap([a for a, _ in sal_cases], [N(f"ls_rate_{r}") for r in srt], sv, lambda v: sd[round(v, 4)],
                 row_head="If losses are…", col_head="Interest rate we charge a year", cell_w=250, label_w=420)
     + anchors([(N("lmc_sal_p"), "futures in which a salaried worker pays back, at today's cost to win", "Monte Carlo"),
                (N("lmc_sal_cac100_p"), f"if employers let us win workers for {N('lmc_cac_100')}", "Monte Carlo"),
                (N("lmc_sal_p_low"), "futures that pay back if repayment from pay keeps losses at 4% or less", "Monte Carlo")]),
     "Value of one worker: ₹1 lakh loans over 18 months, 1 in 5 borrowing, today's cost to win. tables/lend_salaried.csv.",
     f"""Salaried workers reached through employers or staffing firms like Quess stay longer: about {N('rsd_ret_m12_salaried_mode')} are still saving a year on, against about a quarter of shopkeepers. But they can usually borrow more cheaply elsewhere, so the rate we can charge decides it: across 10,000 futures it explains {N('lmd_sal_the_rate_we_charge')} of the outcome. At normal industry losses, a worker is worth {N('ls_ev_normal_24')} at 24% a year and {N('ls_ev_normal_26')} at 26%. If taking repayment straight from pay keeps losses low, it works at any rate shown: {N('ls_ev_safe_24')} at 24%. Overall they pay back in {N('lmc_sal_p')} futures at today's cost to win, and {N('lmc_sal_cac100_p')} if employers let us win them for {N('lmc_cac_100')}. Your past lending found this route's market too small; the model says it works only if payroll deduction really lowers losses or the rate holds up.""")

# ================================================================ STORY: how big
page("How big",
     f"How big: {N('pz_5_won')} shopkeepers a year builds a {N('pz_5_book')} loan book earning {N('pz_5_val_med')} to {N('pz_5_val_safe')} a year.",
     anchors([(N("pz_5_lent"), "lent a year", "model"),
              (N("pz_5_book"), "average loan book", "model"),
              (f"{N('pz_5_val_med')}–{N('pz_5_val_safe')}", "value created a year: typical future, and if savers repay better", "model"),
              (f"{N('pz_5_eq_co')}–{N('pz_5_eq_own')}", "capital needed: co-lending with a bank, or our own NBFC", "model")])
     + p(f"{N('pz_5_won')} shopkeepers a year is {N('pz_5_share')} of the {F('udyam_micro')} micro enterprises on Udyam. A solid lending business, not a giant one, unless savers really repay better.", 30, INK),
     "tables/lend_prize.csv: 1 in 5 borrowing; value after an NBFC running cost of ₹5 crore a year; 1 lakh and 10 lakh in the appendix.",
     f"""How big could it get? Winning {N('pz_5_won')} shopkeepers a year, about {N('pz_5_share')} of the {F('udyam_micro')} micro enterprises on Udyam, means lending about {N('pz_5_lent')} a year on an average book of {N('pz_5_book')}. That creates {N('pz_5_val_med')} of value a year in a typical future and {N('pz_5_val_safe')} if savers repay better, after the NBFC's own running costs. It needs {N('pz_5_eq_co')} of capital if we co-lend with a bank, or {N('pz_5_eq_own')} on our own books. A solid lending business rather than a giant one, unless the central belief holds.""")

# ================================================================ STORY: risks
risks_s = [("Winning shopkeepers may cost too much", f"It must stay under {N('be_cost_to_win')} a shopkeeper; consumer apps pay about {N('be_cost_to_win_today')}."),
           ("Savers may not repay better", f"Untested in India; digital lenders lose {F('digital_credit_cost')} of their book a year."),
           ("An NBFC takes capital and time", f"{F('nbfc_nof')} minimum, {F('nbfc_fixed')} a year to run, licences {F('nbfc_licence_time')}; co-lending needs less."),
           ("Others lend to the same people", f"Paytm ({F('paytm_devices')} device merchants), BharatPe, PhonePe and Bachatt.")]
page("Risks",
     "Four risks: winning shopkeepers may cost too much, savers may not repay better, an NBFC takes capital, and others lend to them too.",
     '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">' + "".join(card(p(f"<b>{a}</b>", 30, INK) + p(b, 26, BODY), pad=28, gap=10) for a, b in risks_s) + "</div>",
     "tables/lmc_drivers.csv; research/levers.csv, xs_bachatt.csv, lend_self.csv.",
     f"""Four things could break it. One, winning shopkeepers may cost too much: it must stay under {N('be_cost_to_win')} a shopkeeper, and consumer apps pay about {N('be_cost_to_win_today')} per saver. Two, savers may not repay better than today's digital borrowers, who cost lenders {F('digital_credit_cost')} of the book a year. Three, an NBFC needs {F('nbfc_nof')} of capital and {F('nbfc_fixed')} a year to run, and licences have taken {F('nbfc_licence_time')}; co-lending with a bank needs far less. Four, the big payment apps and Bachatt already lend to these shopkeepers. A smaller fifth: the free fund route depends on fund houses continuing to pay the exchange.""")

# ================================================================ STORY: the pilot
PIL = [["What it costs to win a shopkeeper", f"about {N('be_cost_to_win_today')}, from consumer apps", f"well under {N('be_cost_to_win')} through our own channel"],
       ["Proven savers who borrow each year", f"{N('be_takeup_today')}, assumed", f"well above {N('be_takeup')}"],
       ["Interest rate borrowers accept", f"{N('be_rate_today')}, assumed", f"well above {N('be_rate')}"],
       ["Losses on loans to savers, a year", f"{N('be_losses_today')}, industry normal", f"well under {N('be_losses')}; ideally near {N('pl_losses')}"]]
page("Next",
     "One pilot measures all four numbers before we build.",
     table(["The number", "What we assume today", "What the pilot must show"], PIL, [36, 30, 34], size=26)
     + p(f"The lines are where a shopkeeper stops paying back; the pilot must clear all four with room to spare. If losses come in at {N('pl_losses')} or less, a shopkeeper pays back in {N('lmc_shop_p_low')} futures. The pilot: win a first group through one channel, let them save six months, lend jointly with a bank, and track repayment against similar non-savers for a year.", 28, INK),
     "Break-even lines from tables/lend_breakeven.csv; odds from lmc_summary.csv.",
     f"""One pilot settles all four numbers. Win a first group of shopkeepers through one channel and count what each cost. Let them save for six months. Then lend to them jointly with a bank, so our capital at risk stays small, at a rate around {N('pl_rate')}. Track how many borrow and how they repay for a year, against similar people who did not save. It passes only if all four clear their lines with room to spare: winning well under {N('be_cost_to_win')}, borrowing well above {N('be_takeup')}, a rate well above {N('be_rate')}, and losses well under {N('be_losses')} a year, ideally near {N('pl_losses')}.""")

# ================================================================ MAIN 21: questions
qs = [("1", "Do savers repay better? Have you seen any evidence, anywhere?", f"Digital lenders today lose {F('digital_credit_cost')} of their book a year."),
      ("2", "Our own NBFC, or co-lend with a bank first?", f"Co-lending lets us keep as little as {F('colend_min')} of each loan."),
      ("3", "Which channel wins shopkeepers cheaply?", f"It is the biggest single factor; today a saver costs about {N('rd_centre_cac')} to win.")]
page("Your view",
     "Three questions where your view would help most.",
     '<div style="display:flex;gap:24px;align-items:stretch">' + "".join(
         card(f'<p style="font-size:56px;font-weight:600;line-height:1;color:{ORANGE}">{a}</p>' + p(f"<b>{b}</b>", 28, INK) + p(c, 24, BODY), pad=32, gap=14) for a, b, c in qs) + "</div>"
     + "",
     "Every number in this note traces to the model or a dated, sourced fact; the appendix shows each.",
     f"""Three questions where an experienced eye would help most. One: do savers repay better? Have you seen any evidence, anywhere, that people who save steadily default less, given that digital lenders today lose {F('digital_credit_cost')} of their book a year? Two: should we get our own NBFC, or co-lend with a bank first, keeping as little as {F('colend_min')} of each loan? Three: which channel wins shopkeepers and drivers cheaply, when a saver costs about {N('rd_centre_cac')} to win today?""")

# ================================================================ APPENDIX (the divider is inserted in main())
# ---- A1: method
mboxes = [("Assumptions", f"{N('reg_total')} uncertain inputs, each with an evidence range"), ("Evidence", f"{N('reg_triangulated')} checked against outside sources; the rest widened"),
          ("Draws", "10,000 sets of inputs, fixed seed; savers who stay may also save more"), ("Model", "the same engine the spreadsheet is checked against"),
          ("Results", "net value per saver, odds, drivers")]
Wm, Hm = 300, 230
mb = "".join(f'<div style="position:absolute;left:{k * (Wm + 41)}px;top:0;width:{Wm}px;height:{Hm}px;background:{CARD};border:2px solid {INK};border-radius:16px;padding:20px;display:flex;flex-direction:column;gap:8px">'
             f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{a}</p><p style="font-size:24px;line-height:1.3;color:{INK}">{b}</p></div>' for k, (a, b) in enumerate(mboxes))
ma = "".join(f'<x-connector x1="{k * (Wm + 41) + Wm + 4}" y1="{Hm // 2}" x2="{(k + 1) * (Wm + 41) - 4}" y2="{Hm // 2}" style="color:{ORANGE};border-width:3px"></x-connector>' for k in range(4))
vrows = [["Daily, inputs independent", "the main case", N("mc_independent_net_p50"), N("mc_independent_p_net_pos")],
         ["Daily, inputs linked", "retention, amounts and take-up move together", N("mc_correlated_net_p50"), N("mc_correlated_p_net_pos")],
         ["Weekly, on payout day", "same money a month, one debit a week", N("mc_weekly_net_p50"), N("mc_weekly_p_net_pos")]]
page("Monte Carlo", "How the Monte Carlo works: evidence ranges in, 10,000 futures out.",
     f'<div style="position:relative;width:1664px;height:{Hm}px">{mb}{ma}</div>'
     + table(["Variant", "What it assumes", "Median net value per saver", "Profitable futures"], vrows, [26, 38, 18, 18], head_bg=AP_HEAD),
     "model/mc.py, tables/distributions.csv; spreadsheet tabs 'Monte Carlo' and 'Assumption register'.",
     "Each uncertain input gets a distribution from its evidence: triangular, lognormal, beta, uniform or a two-way switch. Retention moves as one curve from a month-12 draw; the cost to win a saver is drawn in rupees; payment pricing is a 50/50 switch between the flat list price and a percentage, because nobody publishes what a new app would get. The linked variant ties retention, amounts and take-up through one engagement factor. Founder decisions stay fixed.", appendix=True)

# ---- A2: results table
S = {(r["variant"], r["metric"]): r for r in rd("mc_summary.csv")}
res_rows = []
for v_, nm in (("independent", "Daily"), ("weekly", "Weekly")):
    for m, lab in (("net", "Net value per saver"), ("ltv60", "Five-year profit per saver"), ("cac", "Cost to win a saver"), ("rev_pa_y2", "Revenue per active saver, year 2"), ("y10_usd_m", "Revenue in year 10")):
        res_rows.append([f"{nm}: {lab}", N(f"mc_{v_}_{m}_p5"), N(f"mc_{v_}_{m}_p50"), N(f"mc_{v_}_{m}_p95")])
page("Monte Carlo", "Results: every percentile of net value per saver is below zero.",
     table(["Across 10,000 futures", "5th percentile", "Median", "95th percentile"], res_rows, [46, 18, 18, 18], head_bg=AP_HEAD, size=24),
     "tables/mc_summary.csv (all metrics and variants, with means). " + SHORT,
     f"Read across: the 5th, 50th and 95th percentile of each output. Year-10 revenue varies only through unit economics: the growth plan (new savers a year) is typed in, not simulated. Under the linked variant the median net value per saver is {N('mc_correlated_net_p50')}.", appendix=True)

# ---- A3: one at a time (table)
oat_all = rd("sens_oat.csv")[:10]
orows = []
for r in oat_all:
    k = r["input"].replace("@", "_")
    lo_v, hi_v = float(r["p10_value"]), float(r["p90_value"])
    orows.append([label(r["input"]), N(f"oat_{k}_net_at_p10"), N(f"oat_{k}_net_at_p90")])
page("Sensitivity", "One at a time, no input reaches break-even.",
     table(["Input (10th to 90th percentile of its evidence range)", "Net value at 10th", "Net value at 90th"], orows, [58, 21, 21], head_bg=AP_HEAD, size=24),
     "tables/sens_oat.csv (all inputs, with the values tested and break-even searches). " + SHORT,
     f"Around the evidence middle ({N('ev_daily_net')} per saver), each input is moved alone to the 10th and 90th percentile of its range. Sorted by swing. A wide search for a break-even value finds none for any single input.", appendix=True)

# ---- A4: heatmap debit cost x retention
GR = rd("sens_grid.csv")
cds = sorted({r["cost_debit"] for r in GR}, key=float)
qs_ = sorted({r["retention_percentile"] for r in GR}, key=float)
vals = [[float(next(r["net"] for r in GR if r["cost_debit"] == cd and r["retention_percentile"] == q)) for q in qs_] for cd in cds]
gid = lambda cd, q: f"grid_{cd.replace('.', '_')}_{int(round(float(q) * 100))}"
disp = {(i_, j_): N(gid(cd, q)) for i_, cd in enumerate(cds) for j_, q in enumerate(qs_)}
cells = [[(i_, j_) for j_ in range(len(qs_))] for i_ in range(len(cds))]
row_labels = [(N("ev_daily_cost_per_debit_flat") if cd == "5.9" else "₹" + (f"{float(cd):.2f}" if float(cd) < 1 else f"{float(cd):.0f}")) + " a debit" for cd in cds]
hm_vals = vals
page("Sensitivity", "Cheaper debits and longer retention never reach break-even together.",
     viz.heatmap(row_labels, [f"{int(round(float(q) * 100))}th" for q in qs_], hm_vals,
                 lambda v: next(disp[(i_, j_)] for i_ in range(len(cds)) for j_ in range(len(qs_)) if abs(hm_vals[i_][j_] - v) < 1e-9),
                 row_head="Cost per debit", col_head="Retention percentile (whole curve, both halves)", cell_w=220, cell_h=74, label_w=260),
     "tables/sens_grid.csv; all else at the evidence middle. " + SHORT,
     "Rows: what each debit costs; columns: how long savers stay, as a percentile of the evidence. Longer retention makes the loss bigger, because each active month loses money. Even at a quarter rupee a debit, no cell reaches break-even.", appendix=True)

# ---- A5: plan's ten steps
GRD = rd("mc_greedy.csv")
SHORTL = {"cost_debit": "debit cost", "daily_amount": "amount", "gold_margin": "gold margin", "cac_mult": "cost to win",
          "ins_premium": "premium", "ret_m24": "year-2 savers", "debits_success": "debits", "ins_uptake": "cover take-up",
          "ins_comm_first": "commission", "ret_m12": "year-1 savers"}
gsteps = [("your plan", V("plan_base_net_per_customer"), N("plan_base_net_per_customer"))] + [
    ("+ " + SHORTL.get(r["input"], r["input"]), float(r["net_after"]), N(f"plan_greedy_{r['step']}")) for r in GRD]
page("Sensitivity", f"Even in your own plan, {N('plan_greedy_steps')} inputs must hit their best case before a saver breaks even.",
     viz.steps_bars(gsteps, height=340, gap=12),
     "tables/mc_greedy.csv: inputs moved to the plan's best case, most helpful first. " + SHORT,
     f"Starting from my plan's middle case, each step moves the one input whose best-case value helps most, until the average saver breaks even. It takes {N('plan_greedy_steps')}. The plan's best case needs all of them at once.", appendix=True)

# ---- A6-A9: register tables
SHARE_INPUTS = {"ret_m12", "ret_m24_ratio", "churn_late", "gold_margin", "trail_liquid", "fd_fee", "ins_comm_first", "ins_comm_renew",
                "ins_uptake", "ins_persist", "lsp_fee", "dlg_fee_uplift", "secured_fee", "loan_apply", "loan_repeat", "ladder_dpd90",
                "card_uptake", "cost_fraud", "pay_pct", "loan_approval", "loan_eligible", "withdraw_rate", "amount_growth", "sip_uptake"}


UNITS = {r["id"]: r.get("unit", "") for r in rd("inputs.csv")}


def fmt_val(x, inp):
    """Register cells: shares as whole percentages (one decimal under 10%, two figures under 1%),
    rupee inputs with a rupee sign, counts as plain numbers."""
    if x == "":
        return ""
    v = float(x)
    u = UNITS.get(inp, "")
    if inp in SHARE_INPUTS or u.startswith("share") or u == "per year":
        q = v * 100
        if q == 0:
            return "0%"
        if q >= 10:
            return f"{q:.0f}%"
        if q >= 1:
            return f"{q:.1f}".rstrip("0").rstrip(".") + "%"
        return f"{q:.2g}%"
    if inp == "cac_target" or u.startswith("INR"):
        return "₹0" if v == 0 else f"₹{v:,.0f}" if v >= 10 else f"₹{v:.2g}"
    return f"{v:,.0f}" if v >= 10 else f"{v:.2g}"


def ev_ids(txt, k=3):
    ids = [x.strip() for x in txt.split(",") if x.strip()]
    return ", ".join(ids[:k]) + (" and more" if len(ids) > k else "")


reg_rows = []
for r in [r for r in REG if r["status"] in ("triangulated", "assumption", "unevidenced")]:
    nm = LABELS.get(r["input"] + ("@" + r["segment"] if r["segment"] != "all" else ""), r["assumption"])
    rng = ("two prices, even odds" if r["input"] == "pay_flat" else "billed or not, even odds" if r["input"] == "fail_billed"
           else f"{fmt_val(r['low'], r['input'])} / {fmt_val(r['mode'], r['input'])} / {fmt_val(r['high'], r['input'])}")
    reg_rows.append([nm, fmt_val(r["plan_value"], r["input"]), rng,
                     r["verdict"].replace("plan ", "") if r["verdict"] != "no plan value" else "n/a", ev_ids(r["evidence"])])
chunks = [reg_rows[i:i + 7] for i in range(0, len(reg_rows), 7)]
for n_, ch in enumerate(chunks, 1):
    page("Assumption register", f"Your plan against the evidence ({n_} of {len(chunks)}), most important first.",
         table(["Assumption", "Your plan", "Evidence: low / middle / high", "Verdict", "Evidence rows"], ch, [34, 11, 21, 14, 20], head_bg=AP_HEAD, size=24),
         "tables/assumption_register.csv; evidence rows in research/tri_costs.csv, tri_behaviour.csv, market_benchmarks.csv, nongig.csv.",
         "Low and high are the 5th and 95th percentile for lognormal and beta ranges, and the ends for triangular ones. Verdict: where the plan's value sits in the evidence, in the plan's own optimistic direction. One caution: the month-12 retention ranges are centred on the plan's own 20% and 25%. The research judged those defensible inside an evidence band of about 10 to 40%, so their spread comes from the evidence but their centre is a judgement. Retention explains only a small share of the spread, so this does not move the verdict.", appendix=True)
prov = [r for r in REG if r["status"] == "provisional"]
pnames = sorted({LABELS.get(r["input"], r["assumption"]) for r in prov})
half = (len(pnames) + 1) // 2
page("Assumption register", f"{N('reg_provisional')} inputs could not be checked; they keep a widened range.",
     f'<div style="display:flex;gap:48px">' + "".join(
         f'<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + "".join(p("· " + x, 24, BODY) for x in col) + "</div>"
         for col in (pnames[:half], pnames[half:])) + "</div>",
     "tables/distributions.csv (status 'provisional').",
     "For these inputs no independent source was found in the time available. Each keeps the plan's bear, base and bull widened by half a range on each side. Together they explain little of the spread (see the drivers), but they are not evidence.", appendix=True)

# ---- A10-A11: key distributions, small multiples
DST = {(r["input"], r["segment"]): r for r in rd("distributions.csv")}
picks = [("cac_target", "gig", "seg_gig_base_cac"), ("ret_m12", "gig", None), ("ret_m24_ratio", "all", None), ("daily_amount", "gig", None),
         ("debits_success", "gig", None), ("ins_uptake", "gig", None), ("ins_premium", "all", None), ("gold_margin", "all", None),
         ("loan_apply", "all", None), ("cost_support", "all", None), ("cost_tech", "all", None), ("secured_fee", "all", None)]
regd = {(r["input"], r["segment"]): r for r in REG}


def small(i, seg):
    r = DST[(i, seg)]
    lo, mo, hi = float(r["low"]), float(r["mode"]), float(r["high"])
    if r["dist"] == "beta":
        a_, b_ = (float(x) for x in r["params"].split(";"))
        svg = viz.dist_svg("triangular", lo, mo, hi, w=440, h=120)
    else:
        svg = viz.dist_svg("lognormal" if r["dist"] == "lognormal" else "triangular", lo, mo, hi, w=440, h=120)
    pv = regd.get((i, seg), {}).get("plan_value", "")
    nm = LABELS.get(i + ("@" + seg if seg != "all" else ""), regd.get((i, seg), {}).get("assumption", i))
    return card(p(f"<b>{nm}</b>", 24, INK) + svg + p(f"evidence {fmt_val(r['low'], i)} / {fmt_val(r['mode'], i)} / {fmt_val(r['high'], i)}"
                                                    + (f" · plan {fmt_val(pv, i)}" if pv != "" else ""), 24, MUTED), pad=20, gap=8)


for n_, grp in enumerate((picks[:6], picks[6:]), 1):
    grid_ = "".join(small(i, s) for i, s, _ in grp)
    page("Evidence ranges", f"Each key input's evidence range ({n_} of 2), with your plan's value.",
         f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">{grid_}</div>',
         "tables/distributions.csv; shapes drawn from low / middle / high (beta shown as its 5th-mean-95th triangle).",
         "Each curve is the range the Monte Carlo draws from. The plan's value is shown for comparison; the register gives the verdict and the evidence rows.", appendix=True)

# ---- A12: per saver, plan vs evidence middle
cmp_rows = [["Cost to win a saver", N("plan_base_cac"), N("ev_daily_cac")],
            ["Still saving after a year", N("plan_base_m12_still"), N("ev_daily_still_m12")],
            ["Saved per active saver a month, year 2", "", N("ev_daily_saved_pm_y2")],
            ["Revenue per active saver, year 2", N("plan_base_rev_pa_y2"), N("ev_daily_rev_pa_y2")],
            ["Cost to serve per active saver, year 2", N("story_base_cost_pa_y2"), N("ev_daily_cost_pa_y2")],
            ["Savers who ever take a loan, five years", N("story_base_borrow_60"), N("ev_daily_borrow_60")],
            ["Share of five-year revenue from gold", N("story_base_rev60_gold"), N("ev_daily_rev60_gold")],
            ["Five-year profit per saver", N("plan_base_ltv60"), N("ev_daily_ltv60")],
            ["Net value per saver", N("plan_base_net_per_customer"), N("ev_daily_net")]]
page("Per saver", "Per saver, your plan against the evidence middle.",
     table(["Per activated saver unless stated", "Your plan", "Evidence middle"], cmp_rows, [52, 24, 24], head_bg=AP_HEAD, size=26),
     "Plan: deck_numbers (model base case). Evidence middle: ev_centre.csv. " + SHORT,
     "Both columns run through the same model; only the inputs differ. The evidence middle sets every uncertain input at the middle of its evidence range, with the cheaper (percentage) payment pricing.", appendix=True)

# ---- lifetime value: the payback curve and the cases
CUR = {}
for r in rd("ltv_curve.csv"):
    CUR.setdefault(r["case"], [(0, -V(f"ltv_{r['case']}_cac"))]).append((int(r["month"]), float(r["cum_net_undiscounted"])))
LCASE = [("evidence_everything_best", "every product at its best", ORANGE, False),
         ("evidence_everything_mid", "selling everything (middle)", BLUE, False),
         ("evidence_savings_only", "savings only", LBLUE, False),
         ("plan_as_is", "your plan's numbers", BODY, True)]
pb_best = int(V("ltv_evidence_everything_best_payback"))
page("Lifetime value", "When does a customer pay back? Never, unless every product hits its best case.",
     viz.lines([(lab, CUR[c], col, dash) for c, lab, col, dash in LCASE], 120,
               x_ticks=[(m, f"year {m // 12}") for m in range(12, 121, 24)],
               marks=[(pb_best, 0.0, N("ltv_evidence_everything_best_payback"))])
     + caption(f"Running total per customer won, not discounted, from {N('ltv_evidence_everything_mid_cac')} spent to win them (evidence middle; your plan starts at {N('ltv_plan_as_is_cac')}). Ten years."),
     "model/ltv.py: tables/ltv_curve.csv. " + SHORT,
     f"""Each line starts at what it cost to win the customer and adds what they bring in less what they cost to serve, month by month. With savings only, the line falls: serving a customer costs more than they bring in. Selling them everything (middle case) slows the fall but never turns it. Your plan's own numbers also never pay back. Only with every product at its best case at once does the line cross break-even, in {N('ltv_evidence_everything_best_payback')}.""", appendix=True)
LROWS = [("Evidence middle, savings only", "evidence_savings_only"), ("Evidence middle, selling everything (middle)", "evidence_everything_mid"),
         ("Evidence middle, every product at its best", "evidence_everything_best"), ("Your plan, as built", "plan_as_is"),
         ("Your plan, selling everything (middle)", "plan_everything_mid")]
page("Lifetime value", "One customer, case by case.",
     table(["Case", "Cost to win", "Worth over 5 years, before that cost", "After that cost", "Payback"],
           [[lab, N(f"ltv_{c}_cac"), N(f"ltv_{c}_ltv60"), N(f"ltv_{c}_net60"), N(f"ltv_{c}_payback")] for lab, c in LROWS],
           [34, 14, 20, 16, 16], head_bg=AP_HEAD, size=26),
     "tables/ltv_cases.csv. Worth = savings + cross-sell - cost to serve; five years, discounted.",
     "Selling everything replaces the model's own few cross-sell lines with the full product list, so nothing is counted twice. With the model's own lines left in, the calculation reproduces the model's five-year value exactly; that check runs every time.", appendix=True)

# ---- the redesign, in numbers
RDL = "The shopkeeper version, in numbers"
RNAME = {"wc_loans_year": "Proven savers taking a loan each year", "wc_ticket": "Loan size", "wc_fee": "Our referral fee",
         "wc_clawback": "Fee taken back on loans that go bad", "fund_trail": "Fund fee to us, a year on the balance",
         "incentive_share": "Savers who earn SEBI's new-investor bonus", "xs_other": "Everything else we sell, per saver a year"}
rd_in = [[RNAME[r["input"]], f"{N('rdd_' + r['input'] + '_low')} / {N('rdd_' + r['input'] + '_mode')} / {N('rdd_' + r['input'] + '_high')}", ev_ids(r["evidence"], 3)]
         for r in rd("redesign_distributions.csv")]
page(RDL, "The redesign's new inputs, each drawn from its evidence range.",
     table(["Input", "Low / middle / high", "Evidence"], rd_in, [42, 30, 28], head_bg=AP_HEAD, size=24),
     "tables/redesign_distributions.csv; evidence rows in research/xs_bachatt.csv, xs_lending.csv, crosssell_map.csv.",
     f"""Everything else is drawn exactly as in the original test: retention, amounts, the cost to win a shopkeeper, support and tech. The redesign switches off the first design's gold, FDs, small secured loans, card, SIP and insurance lines and replaces them with these. Loans start after six months of saving. The take-up range runs from ordinary fintech users, {F('fintech_borrow_rate')} a year, to Paytm's most engaged merchants, {F('paytm_borrow_rate')}.""", appendix=True)
VROWS = [("As first designed", "rd_original_p", None), ("Redesign, loans only while saving", "rd_var_base_p", "rd_var_base_net_p50"),
         ("+ proven savers keep borrowing", "rd_var_grad_p", "rd_var_grad_net_p50"),
         (f"+ {N('rd_grid_takeup_20')} borrow each year", "rd_var_grad_20_p", "rd_var_grad_20_net_p50"),
         (f"+ cost to win {N('rd_target_cac')} (take-up drawn)", "rd_var_grad_cac250_p", "rd_var_grad_cac250_net_p50"),
         (f"+ both: {N('rd_grid_takeup_20')} borrow and {N('rd_target_cac')} to win", "rd_var_best_p", "rd_var_best_net_p50")]
page(RDL, f"Every step of the redesign; the cost to win a shopkeeper drives {N('rd_drv_cac')} of the outcome.",
     table(["Step", "Futures that pay back", "Median per customer"], [[a, N(b), N(c) if c else N("mc_independent_net_p50")] for a, b, c in VROWS],
           [52, 24, 24], head_bg=AP_HEAD, size=26),
     "tables/redesign_variants.csv, redesign_drivers.csv; 4,000 futures per step (original: 10,000).",
     f"""Each step adds one change. In the redesign with loans only while saving, the cost to win a shopkeeper explains {N('rd_drv_cac')} of the spread in outcomes and loan take-up only {N('rd_drv_takeup')}, because most savers stop within a year and take their borrowing with them. Letting proven savers keep borrowing is what makes take-up matter; winning shopkeepers cheaply is what makes it pay.""", appendix=True)
EVR = [[f"Distributors pay {F('mf_distributor_fee')} per fund transaction; fund houses pay {F('amc_fee')}", "Cafemutual on BSE StAR MF (XB-01)"],
       [f"Paytm: {F('paytm_devices')} device merchants; borrowing at {F('paytm_borrow_rate')} a year", "Paytm Q4 FY26 release (XB-06)"],
       [f"Merchant-loan losses {F('paytm_ecl')}, on lenders' books", "Paytm Q4 FY26 release (XB-07)"],
       [f"Bachatt: {F('bachatt_users')} users; {F('bachatt_daily_savers')} saving daily; loans {F('bachatt_loans')}", "Bachatt release; derived (XB-03, XB-10)"],
       [f"SEBI bonus: {F('sebi_women_bonus')} per new woman or small-town investor", "Cafemutual; Business Standard (XB-05)"],
       [f"Repayments capped at {F('rbi_mf_cap')} of income for lower-income households", "RBI microfinance rules (XL-34)"]]
page(RDL, "The evidence behind the redesign.",
     table(["Fact", "Source"], EVR, [62, 38], head_bg=AP_HEAD, size=24),
     "research/xs_bachatt.csv (XB rows), xs_lending.csv (XL rows).",
     "Each fact was read from the primary release or a trade publication's report of it. Bachatt's daily-saver figure is derived from its own transaction count and is approximate.", appendix=True)

# ---- lending ourselves, in numbers
LSL = "Lending ourselves, in numbers"
SEGN = [("Shopkeepers", "shop"), ("Drivers and home-service workers", "drivers"), ("Delivery riders", "riders")]
LROWS2 = [[f"{a} ({N('ln_' + k + '_size')})", N(f"ln_{k}_ref"), N(f"ln_{k}_safe"), N(f"ln_{k}_normal"), N(f"ln_{k}_today")] for a, k in SEGN]
page(LSL, "What one loan earns us, by customer and by how well they repay.",
     table(["One loan to…", "Refer it", "Lend: savers repay better", "Lend: normal losses", "Lend: today's losses"], LROWS2, [32, 14, 18, 18, 18], head_bg=AP_HEAD, size=26),
     "model/lend_self.py: tables/lend_loan.csv.",
     f"""Each loan is repaid in equal monthly instalments. Shopkeepers: {N('ln_shop_size')} over 12 months at 26% a year; drivers: {N('ln_drivers_size')} over 18 months at 26%; riders: {N('ln_riders_size')} over 6 months at 30%; processing fee 2.5-3%. We pay {F('nbfc_cof_range')} to borrow. Bad-loan losses and running costs are shares of the loan balance a year: {N('lend_credit_safe')} and {N('lend_running_safe')} if savers repay better; {N('lend_credit_normal')} and {N('lend_running_normal')} normal; {N('lend_credit_today')} and {N('lend_running_today')} as digital lenders report today. Winning the customer is counted separately.""", appendix=True)
LEVR = [["What we pay to borrow", F("nbfc_cof_range"), "Moneyview, Kissht, KreditBee (LEV-014..016, 062)"],
        ["Bad loans, digital lenders today", F("digital_credit_cost"), "KreditBee, Kissht, Groww (LEV-021, 022, 029)"],
        ["Running cost incl. marketing", F("digital_running_cost"), "KreditBee, Kissht, Stashfin (LEV-018, 019, 026)"],
        ["What digital lenders keep as profit", F("digital_roa"), "industry report (LEV-027)"],
        ["Late repeat loans, your past lending", F("founder_repeat_late"), "your data"],
        ["Loans above ₹50,000 ever 90+ days late", F("crif_big_ticket"), "CRIF (LEV-066)"],
        ["Least share a co-lender keeps", F("colend_min"), "RBI, from Jan 2026 (LS-01)"]]
page(LSL, "The lending evidence behind each number.",
     table(["What", "Value", "Source"], LEVR, [40, 18, 42], head_bg=AP_HEAD, size=24),
     "research/levers.csv, lend_self.csv.",
     "Digital lenders' running costs include marketing; our model counts winning customers separately, so it uses lower running costs (3-8% a year). The profit check: digital lenders keep 1-4% of their book a year after everything.", appendix=True)
SCR = [[f"{a}, {c}", N(f"sc_{k}_{ck}_20_3"), N(f"sc_{k}_{ck}_20_5"), N(f"sc_{k}_{ck}_20_8")]
       for a, k in SEGN[:2] for c, ck in (("savers repay better", "safe"), ("normal losses", "normal"))]
page(LSL, "Customers a year needed to cover an NBFC's running cost.",
     table(["Customer and case (1 in 5 borrowing)", "At ₹3 crore a year", "At ₹5 crore", "At ₹8 crore"], SCR, [46, 18, 18, 18], head_bg=AP_HEAD, size=26),
     "tables/lend_scale.csv; NBFC running cost from Jupiter and Groww precedents (inputs.csv nbfc_fixed_cr).",
     "The NBFC's own fixed cost (compliance, risk, audit) must be covered by the value of the customers won each year. Co-lending with a bank lowers the capital needed but not this fixed cost.", appendix=True)

# ---- lending Monte Carlo
LMC = "The lending Monte Carlo"
LMNAME = {"credit_cost": "Losses on loans, a year", "running_cost": "Running cost, a year", "cost_of_funds": "What we pay to borrow, a year",
          "rate": "Interest rate we charge", "fee": "Processing fee", "takeup": "Proven savers borrowing a year",
          "loan_size_shopkeepers": "Loan size: shopkeepers (12 months)", "loan_size_drivers": "Loan size: drivers (18 months)",
          "loan_size_salaried": "Loan size: salaried (18 months)", "rate_salaried": "Interest rate: salaried", "ret_m12_salaried": "Salaried still saving at a year"}
LMEV = {r["input"]: r["evidence"] for r in rd("lmc_distributions.csv")}
lm_in = [[LMNAME[i], f"{N('lmi_' + i + '_low')} / {N('lmi_' + i + '_mode')} / {N('lmi_' + i + '_high')}", ev_ids(LMEV[i], 3)] for i in LMNAME]
page(LMC, "The lending inputs, each drawn from its evidence range.",
     table(["Input", "Low / middle / high", "Evidence"], lm_in, [42, 30, 28], head_bg=AP_HEAD, size=24),
     "tables/lmc_distributions.csv; research/levers.csv, lend_self.csv, xs_bachatt.csv.",
     "All triangular and drawn independently, 10,000 futures per customer group. Customer inputs (what it costs to win, how long people save, amounts, support and tech, other products) are drawn from the same evidence ranges as the first design. One real risk is not modelled: more borrowing could mean riskier borrowers.", appendix=True)
LMR = [["Shopkeepers", N("lmc_shop_p"), N("lmc_shop_p_2y"), N("lmc_shop_p_low"), N("lmc_shop_p_high"), N("lmc_shop_p5"), N("lmc_shop_p50"), N("lmc_shop_p95")],
       ["Drivers", N("lmc_drivers_p"), N("lmc_drivers_p_2y"), N("lmc_drivers_p_low"), N("lmc_drivers_p_high"), N("lmc_drivers_p5"), N("lmc_drivers_p50"), N("lmc_drivers_p95")],
       ["Salaried", N("lmc_sal_p"), N("lmc_sal_p_2y"), N("lmc_sal_p_low"), N("lmc_sal_p_high"), N("lmc_sal_p5"), N("lmc_sal_p50"), N("lmc_sal_p95")]]
page(LMC, "Results: how often a customer pays back, and the range of outcomes.",
     table(["Group", "Pays back", "Within 2 years", "If losses ≤ 4%", "If losses ≥ 7%", "Worst 5%", "Typical", "Best 5%"], LMR,
           [16, 12, 12, 12, 12, 12, 12, 12], head_bg=AP_HEAD, size=24),
     "tables/lmc_summary.csv. Value per customer won, five years, discounted, after the cost to win.",
     "Pays back means the customer's value over five years is above zero. The loss split shows how much the central belief matters: the odds change by about thirty points between low and high losses.", appendix=True)
DRK = [("cost_to_win", "What it costs to win them"), ("how_many_borrow", "How many proven savers borrow"), ("the_rate_we_charge", "The interest rate we charge"),
       ("losses", "Losses on loans"), ("loan_size", "Loan size"), ("how_long_they_save", "How long they keep saving"), ("running_cost", "Running cost"),
       ("other_products", "Other products"), ("what_we_pay_to_borrow", "What we pay to borrow"), ("processing_fee", "Processing fee")]
lm_d = [[lab] + [N(f"lmd_{g}_{k}") if f"lmd_{g}_{k}" in B.NUM else "" for g in ("shop", "drivers", "sal")] for k, lab in DRK]
page(LMC, "What drives the outcome, for each customer group.",
     table(["Input", "Shopkeepers", "Drivers", "Salaried"], lm_d, [43, 19, 19, 19], head_bg=AP_HEAD, size=24),
     "tables/lmc_drivers.csv: share of the spread in value per customer each input explains (rank regression).",
     "For drivers, the rate and losses matter more and borrowing less, because their loans are longer. For salaried workers the rate dominates: at the rates they can get elsewhere, each loan barely covers its costs, so more borrowing adds little.", appendix=True)

# ---- the prize
PZ = [[N(f"pz_{k}_won"), N(f"pz_{k}_lent"), N(f"pz_{k}_book"), f"{N(f'pz_{k}_val_med')} to {N(f'pz_{k}_val_safe')}", f"{N(f'pz_{k}_eq_co')} to {N(f'pz_{k}_eq_own')}"] for k in ("1", "5", "10")]
page("The prize", "How big it could get: three scales.",
     table(["Shopkeepers won a year", "Lent a year", "Average loan book", "Value a year: typical → savers repay better", "Capital: co-lending → own NBFC"], PZ,
           [18, 16, 18, 26, 22], head_bg=AP_HEAD, size=24),
     "tables/lend_prize.csv: 1 in 5 proven savers borrowing; value after an NBFC running cost of ₹5 crore a year.",
     f"""Value a year is what each year's new shopkeepers are worth over their lives, less the NBFC's own running cost. Capital is a third of the average loan book on our own books, or a tenth if we co-lend and keep only the {F('colend_min')} RBI requires. At the smallest scale the typical future does not cover the NBFC's running cost.""", appendix=True)

# ---- customer groups (lending frame)
CG = [["Shopkeepers", N("ln_shop_size"), N("lmc_shop_p"), "Paytm, BharatPe, PhonePe, Bachatt", "start here"],
      ["Drivers and home-service workers", N("ln_drivers_size"), N("lmc_drivers_p"), "platforms' lending partners", "next, if platforms deduct repayments"],
      ["Delivery riders", N("ln_riders_size"), "never", "Swiggy and Zomato with NBFCs", "savers only"],
      ["Salaried workers via employers", N("lmi_loan_size_salaried_mode"), N("lmc_sal_p"), "SalarySe, Refyne", "only at 26%+ or low losses"],
      ["Women's savings groups", F("shg_loan"), "not modelled", "subsidised bank loans", "not now"],
      ["Farmers", "Kisan Credit Card", "not modelled", f"{F('kcc_rate')} subsidised loans, gold loans", "not now"]]
page("Customer groups", "Every customer group we looked at.",
     table(["Group", "Loans", "Futures that pay back", "Already served by", "Verdict"], CG, [26, 14, 18, 24, 18], head_bg=AP_HEAD, size=24),
     "model/lend_mc.py, lend_self.py; research/segments.csv, lend_self.csv.",
     "Riders were run with the deterministic model only: even if savers repay better and 1 in 5 borrow, a rider never pays back at today's cost to win. Groups marked not modelled were ruled out on loan size, an existing subsidised supply, or your past experience.", appendix=True)

# ---- what the lending model cannot tell
lim = [("Saving's effect on repayment is assumed", "The loss range spans better-than-industry to today's digital lenders; no data yet links saving to repayment."),
       ("More borrowing may mean riskier borrowers", "Borrowing and losses are drawn independently; in reality they may move together."),
       ("The cost to win comes from consumer apps", "No published figure exists for our channels; the pilot must measure it."),
       ("Rates may be pushed down", "We assume 22–30% a year; competition for good shopkeepers could lower it."),
       ("The NBFC sits outside each customer", "Its running cost and capital are shown separately, at three scales."),
       ("Five years only", "Value beyond five years, and the cost of capital, are left out.")]
page("Model limits", "Six things the lending model cannot tell you.",
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">' + "".join(card(p(f"<b>{a}</b>", 26, INK) + p(b, 24, BODY), pad=24, gap=8) for a, b in lim) + "</div>",
     "model/lend_self.py, lend_mc.py.",
     "These are limits of the model's structure. The pilot is designed to replace the two biggest assumptions, the cost to win and the effect of saving on repayment, with measured numbers.", appendix=True)

# ---- the salaried version, in numbers
RSL = "The salaried version, in numbers"
RSD = {r["input"]: r for r in rd("rs_distributions.csv")}
rs_in = [["Still saving at month 12", f"{N('rsd_ret_m12_salaried_low')} / {N('rsd_ret_m12_salaried_mode')} / {N('rsd_ret_m12_salaried_high')}", "SG-06, SG-07"],
         ["Loan size", f"{N('rsd_wc_ticket_salaried_low')} / {N('rsd_wc_ticket_salaried_mode')} / {N('rsd_wc_ticket_salaried_high')}", "SG-22, SG-14, SG-40"],
         ["Fee per debit", "none: deducted from pay into a fund", "SG-08, SG-40, XB-01"],
         ["Cost to win a worker", "no employer figure published; consumer evidence used", "SG-43"],
         ["Everything else", "as in the shopkeeper version", "redesign inputs"]]
page(RSL, "What the salaried version changes, and its evidence.",
     table(["Input", "Low / middle / high", "Evidence"], rs_in, [36, 40, 24], head_bg=AP_HEAD, size=24),
     "tables/rs_distributions.csv; research/segments.csv.",
     f"""The salaried version changes only what the segment research says differs. Staying: staffing firms lose {F('staffing_exit')} of workers a quarter, and blue-collar tenure averages {F('salaried_tenure')}, so {N('rs_ret_m12')} are still saving a year on. Loan size: a ₹18–26k salary can carry {F('salaried_capacity')}, though today's salary advances are {F('ewa_ticket')}. There is no fee per debit because saving comes out of pay. No one publishes what the employer route costs, so the Monte Carlo keeps the consumer evidence and the grid shows fixed values.""", appendix=True)
RVROWS = [("As first designed", "rd_original_p", None), ("Salaried, loans stop when they change jobs", "rs_var_job_p", "rs_var_job_net_p50"),
          ("+ the account moves with the worker", "rs_var_port_p", "rs_var_port_net_p50"),
          (f"+ {N('rd_grid_takeup_20')} borrow each year", "rs_var_port_20_p", "rs_var_port_20_net_p50"),
          (f"+ win for {N('rs_target_cac')} (take-up drawn)", "rs_var_port_cac250_p", "rs_var_port_cac250_net_p50"),
          (f"+ both: {N('rd_grid_takeup_20')} borrow and {N('rs_target_cac')} to win", "rs_var_best_p", "rs_var_best_net_p50")]
page(RSL, f"Every step of the salaried version; the cost to win a worker drives {N('rs_drv_cac')} of the outcome.",
     table(["Step", "Futures that pay back", "Median per worker"], [[a, N(b), N(c) if c else N("mc_independent_net_p50")] for a, b, c in RVROWS],
           [52, 24, 24], head_bg=AP_HEAD, size=26),
     "tables/rs_variants.csv, rs_drivers.csv; 4,000 futures per step (original: 10,000).",
     "Each step adds one change. The account moving with the worker matters because blue-collar jobs are short; winning workers cheaply through employers is what makes it pay.", appendix=True)
SEGROWS = [["Delivery riders", F("rider_loans"), "platforms (Swiggy, Zomato)", "Swiggy and Zomato with lenders", N("seg_riders_20")],
           ["Drivers and home-service workers", "vehicle loans, ₹75,000–3 lakh", "platforms, if they deduct from payouts", "platforms' own lending partners", N("seg_drivers_20")],
           ["Shopkeepers", "₹1–5 lakh", "supplier networks, associations", "Paytm, BharatPe, PhonePe, Bachatt", N("seg_shopkeepers_20")],
           ["Salaried workers via employers", F("salaried_capacity"), "employers and staffing firms", "big staffing firms' partners", N("seg_salaried_20")],
           ["Women's savings groups", F("shg_loan"), "government missions", "subsidised bank loans", "not modelled"],
           ["Farmers", "Kisan Credit Card", "none cheap", f"{F('kcc_rate')} subsidised loans, gold loans", "not modelled"]]
page(RSL, "Every customer group we looked at, side by side.",
     table(["Group", "Loans they take or can carry", "Cheapest way in", "Already served by", "Most we could pay to win one"], SEGROWS, [22, 20, 21, 21, 16], head_bg=AP_HEAD, size=24),
     "research/segments.csv, segments_summary.md; tables/segment_value.csv (at 1 in 5 borrowing a year).",
     f"""The last column is the most we could pay to win one customer and break even, if 1 in 5 borrow each year, under the same redesign. Riders borrow too little; shopkeepers are contested; drivers and home-service workers ({F('uc_pay')} a month at Urban Company) are a good second step if a platform will deduct repayments from payouts. Salaried workers through employers come first. Women's savings groups and farmers were not modelled: their loans are small or already subsidised, and repayment is mostly in cash.""", appendix=True)

# ---- the flip, in full
FCASE = [("plan", "Your plan's numbers (₹2 a debit)"), ("best_flat", "Best case, flat fee"), ("ev_flat", "Evidence middle, flat fee"),
         ("ev_flat_billed", "Evidence middle, failed debits also billed"), ("ev_flat_weekly", "Evidence middle, weekly debits (per weekly debit)"),
         ("ev_pct", "Evidence middle, fee as a % of each debit"), ("best_pct", "Best case, fee as a % of each debit")]


def _fl(fid, k):
    i = f"flip_{fid}_{k}"
    return N(i) if i in B.NUM else "n/a"


page("The flip", "The daily minimum that breaks even, case by case.",
     table(["Case", "Minimum per debit", "A month (gig)", "Share of a rider's net income", f"Best net per saver, debits up to {F('ev_debit_tier')}"],
           [[lab, _fl(f, "amount"), _fl(f, "monthly_gig"), _fl(f, "income_gig"), _fl(f, "best_upto_1000")] for f, lab in FCASE],
           [34, 15, 15, 18, 18], head_bg=AP_HEAD, size=24),
     f"tables/flip_breakeven.csv, flip_amount.csv; rider income {F('rider_net')} (IDinsight 2024). " + SHORT,
     f"""Each row moves only the amount every saver puts in per successful debit, in ₹50 steps, and holds everything else. "Best case" puts every other input at whichever end of its evidence range helps most at that amount. The flat fee steps from {F('ev_debit_gst')} to {F('ev_debit_high')} above {F('ev_debit_tier')}, which is why the best result up to {F('ev_debit_tier')} is still a loss at the evidence middle. None of this includes the savers a higher minimum would lose.""", appendix=True)
mc_amts = [500, 750, 1000, 1250, 2000, 3000, 4000, 5000]
page("The flip", f"Across futures, even {N('flipmc_3000_amount')} a day loses money in most of them.",
     viz.share_bars([(f"{N(f'flipmc_{a}_amount')} a day" + (f" (fee steps up above {F('ev_debit_tier')})" if a == 1250 else ""), max(V(f"flipmc_{a}_p_pos_flat"), 0.004), N(f"flipmc_{a}_p_pos_flat"), ORANGE if a > 1000 else BLUE)
                     for a in mc_amts], label_w=640, track_w=760)
     + caption(f"Share of flat-fee futures where a saver makes money. Blue: debits up to {F('ev_debit_tier')} ({F('ev_debit_gst')} each); orange: above ({F('ev_debit_high')}). Where the fee is a percentage: {N('flipmc_5000_p_pos_percent')} at every amount."),
     "Monte Carlo by amount, 2,000 draws each, same draws throughout: tables/flip_mc.csv.",
     f"""The same draws as the main Monte Carlo, with every saver's amount fixed at the minimum. Under a flat fee, a {F('ev_debit_tier')} minimum makes money in {N('flipmc_1000_p_pos_flat')} of futures; just above it the fee triples and the share falls to {N('flipmc_1250_p_pos_flat')}. At {N('flipmc_4000_amount')} a day it is {N('flipmc_4000_p_pos_flat')}. Under percentage pricing no amount ever makes money.""", appendix=True)

XS_ROWS = [r for r in rd("crosssell_map.csv") if not r["product"].startswith("TOTAL")]


def _xs(r, k):
    slug = re.sub(r"[^a-z0-9]+", "_", r["product"].lower()).strip("_")[:40]
    i = f"xs_{slug}_{k}"
    return N(i) if i in B.NUM else "no data"


xs_rows = [[r["product"], f"{_xs(r, 'low')} / {_xs(r, 'mid')} / {_xs(r, 'high')}", r["take_rate_mid"].replace("Rs ", "₹"), r["verdict"], ev_ids(r["evidence"], 1)] for r in XS_ROWS]
xchunks = [xs_rows[i:i + 6] for i in range(0, len(xs_rows), 6)]
for n_, ch in enumerate(xchunks, 1):
    page("Cross-sell", f"What each product adds per active saver a year ({n_} of {len(xchunks)}).",
         table(["Product", "₹ a year: low / mid / high", "We earn (middle)", "Verdict", "Evidence"], ch, [30, 18, 19, 21, 12], head_bg=AP_HEAD, size=24),
         "research/xs_lending.csv (XL rows), xs_other.csv (XO rows); combined in tables/crosssell_map.csv.",
         f"""Per active saver a year = take rate x ticket x the share of savers who buy in a year. Take rates and tickets are sourced; take-up is the researchers' estimate, anchored on, for example, {F('ev_paytm_fin')} of Paytm's monthly users taking any financial product in a quarter. Lenders claw back referral fees on early defaults, and IRDAI has proposed capping health-renewal commission at {F('xs_irdai_renewal_cap')}. Paytm calls fund, gold and add-on insurance revenue {F('xs_paytm_negligible')}.""", appendix=True)

# ---- A13: critique of the model
crit = [("The headline ratio misleads", "Profit ÷ cost to win turns more negative as costs fall when profit is negative; this deck uses net value instead."),
        ("Year-10 revenue is an input", "New savers a year (25,000 rising to millions) are typed in, not derived from budgets or channels; the Monte Carlo does not vary them."),
        ("Fixed costs are not stress-tested", "Team and office costs follow a typed path; they are outside the Monte Carlo."),
        ("Secured-loan demand is assumed", "Savers who can withdraw instantly have little reason to borrow against their own money."),
        ("Gold rules are a scenario", "If digital gold is regulated or its margin capped, the largest revenue line is at risk; not in the draws."),
        ("Founder views are not evidence", "Retention, the ladder and the secured fee started as judgement; the register shows which the evidence now supports.")]
page("What the model cannot tell", "Six things the model itself cannot tell you.",
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">' + "".join(card(p(f"<b>{a}</b>", 26, INK) + p(b, 24, BODY), pad=24, gap=8) for a, b in crit) + "</div>",
     "research/critical_review.md.",
     "These are limits of the model's structure, separate from whether each input is right. None of them would turn the verdict positive: the two that could (year-10 revenue and fixed costs) only matter once a single saver is profitable.", appendix=True)

# ---- A14: fact checks
fc_rows = [[f"{F('gig_under15k')} of gig workers earn under {F('emandate_limit')} a month", "Economic Survey, citing the Indian Staffing Federation", "source corrected"],
           [f"{F('gig_fy25')[0].upper() + F('gig_fy25')[1:]} gig workers in FY25", "Indian Staffing Federation; NITI path similar", "source corrected"],
           ["Half of riders borrowed for their phone", "IDinsight: half for phones, 6 in 10 for bikes", "bike figure added"],
           ["Swiggy delivery partners a month", "Swiggy shareholder letter", "confirmed"],
           ["Micro enterprises on Udyam", "Udyam dashboard; ministry release", "confirmed"],
           [f"{F('debit_list')} list price per Autopay debit", "Cashfree and Zoho price pages", "confirmed"],
           ["Digital gold outside SEBI's rules; no loans against it", "SEBI release; RBI gold-lending rules", "confirmed"],
           [f"{F('emandate_limit')} auto-debits; {F('dlg_cap')} loss cover", "RBI, Apr 2026 and May 2025, via law-firm notes", "confirmed"],
           [f"Jar {F('jar_users')} users, {F('jar_opr')} revenue; PhonePe {F('phonepe_daily')}", "Business Standard, Inc42, Entrackr; PhonePe", "confirmed"],
           [f"Bachatt {F('bachatt_raise')}; Swiggy x Zerodha from {F('ev_swiggy_zerodha')}", "YourStory, BW Disrupt; Outlook Business", "confirmed"]]
page("Fact checks", "Each main-slide fact, checked against a second source.",
     table(["Fact", "Second source", "Result"], fc_rows, [44, 38, 18], head_bg=AP_HEAD, size=24),
     "research/tri_facts.csv, tri_costs.csv, regulation_rails.csv.",
     "Facts were checked against the primary document or an independent outlet. Two attributions were corrected and one figure refined. Company figures for Jar, Bachatt, Stable Money and Fibe rest on filings coverage by Entrackr, Inc42 and TechCrunch, and on company releases.", appendix=True)

# ---- A15: sources
src = [("model/lend_self.py, lend_mc.py", "lending ourselves: one loan, one customer, 10,000 futures"),
       ("tables/lend_*.csv, lmc_*.csv", "every lending result: loans, customers, funnel, prize, odds, drivers"),
       ("research/levers.csv, lend_self.csv", "lenders' costs, losses and funding; co-lending; payout deduction"),
       ("research/xs_bachatt.csv, segments.csv, xs_*.csv", "Bachatt and fund rails; customer groups; other products"),
       ("research/tri_costs.csv, tri_behaviour.csv, tri_facts.csv", "the first design's evidence; second sources for facts"),
       ("model/savings_first_model.xlsx", "the spreadsheet, with a tab for every result above")]
page("Sources", "Where every number lives.",
     table(["File", "What it holds"], [[a, b] for a, b in src], [50, 50], head_bg=AP_HEAD, size=24),
     "Folder: ~/Desktop/savings-first-deck, 2 Oct 2026.",
     "Every number on a slide is looked up by id from these tables, and a script checks that each digit on every slide traces back to one of them.", appendix=True)


# ================================================================ LAYOUT (operator, 2 Oct 2026: ten main slides around one customer)
MAIN_ORDER = [("How it works", "How it works: saving shows us"),
              ("Why lend", "Why lend: one"),
              ("How sure", "How sure: a shopkeeper pays back in"),
              ("What decides it", "Four numbers decide it"),
              ("The crux", "If our savers repay better, the odds"),
              ("Who", "Who: shopkeepers first"),
              ("How big", "How big: "),
              ("Edge", "Our edge, if it holds"),
              ("Risks", "Four risks: winning shopkeepers"),
              ("Next", "One pilot measures all four"),
              ("Your view", "Three questions")]
SUPPORT = "Supporting detail"
FULLER = "The fuller story"


def layout():
    used = set()
    for lab, start in MAIN_ORDER:
        hits = [k for k, r in enumerate(RAW) if r["line"].startswith(start) and k not in used]
        assert len(hits) == 1, (start, hits)
        used.add(hits[0])
        emit(RAW[hits[0]], False, lab)
    assert len(PAGES) == MAIN_TOTAL, len(PAGES)
    # the appendix keeps only what supports the twelve slides (operator, 3 Oct 2026: "keep only the relevant one")
    support = ("Of 100 shopkeepers we win", "At normal industry losses, one shopkeeper", "Salaried workers through employers stay longer")
    keep_past = ("Even if we sell them everything", "Bachatt avoids our biggest cost")
    drop = ("Customers a year needed to cover",)
    order = [LMC, LSL, SUPPORT, "The prize", "Customer groups", FULLER, "Model limits", "Fact checks", "Sources"]
    rest = []
    for k, r in enumerate(RAW):
        if k in used or r["line"].startswith(drop):
            continue
        if r["appendix"]:
            if r["label"] in order:
                rest.append((r["label"], r))
        elif r["line"].startswith(support):
            rest.append((SUPPORT, r))
        elif r["line"].startswith(keep_past):
            rest.append((FULLER, r))
    for lab, r in sorted(rest, key=lambda x: order.index(x[0])):
        emit(r, True, lab)


DESC = {FULLER: "How we got here: why a savings app alone fails", SUPPORT: "The funnel, one shopkeeper worked through, salaried workers", LSL: "Lending ourselves: every loan, every case, the evidence",
        LMC: "The lending Monte Carlo: inputs, results, drivers", "The prize": "How big it could get, at three scales",
        "Customer groups": "Every customer group we looked at", "Model limits": "What the lending model cannot tell",
        "Cross-sell": "Other products: what each could add", RDL: "The shopkeeper version: its inputs, every step, the evidence", RSL: "The salaried version and every customer group, in numbers", "Monte Carlo": "How the Monte Carlo works, and its results", "Sensitivity": f"One input at a time; debit cost x retention; your plan's {N('plan_greedy_steps')} steps",
        "Lifetime value": "One customer: lifetime value and payback", "The flip": "The daily minimum that breaks even", "Cross-sell": "What selling other products could add",
        "Assumption register": "Your plan against the evidence, input by input", "Evidence ranges": "Each key input's evidence range",
        "Per saver": "Per saver: your plan against the evidence middle", "What the model cannot tell": "What the model itself cannot tell",
        "Fact checks": "Fact checks", "Sources": "Sources and files"}


def divider():
    B._cur[0] = "a00"
    items = [(f"A{v[0]}" + (f"-A{v[-1]}" if len(v) > 1 else ""), DESC.get(k, k)) for k, v in SEC.items()]
    rows_ = "".join(f'<div style="display:flex;gap:24px;align-items:baseline"><p style="width:150px;font-size:26px;font-weight:600;color:{ACC_TXT}">{a}</p>'
                    f'<p style="flex:1;font-size:26px;line-height:1.3;color:{INK}">{b}</p></div>' for a, b in items)
    return ("a00", section("a00", f"""
{eyebrow("Appendix")}
<h1 style="font-family:{SERIF};font-size:72px;font-weight:600;line-height:1.05;color:{INK}">The evidence and the numbers</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">{rows_}</div>
{notes("The appendix holds the reasoning and every number behind the main slides: the Monte Carlo, the sensitivity, the assumption register with its evidence, the critique of the model, the fact checks and the sources.")}
""", bg=SAND, extra_style=";justify-content:center;gap:40px"))


def first(label):
    return next(sid for (sid, _), lab in zip(PAGES, PLABEL) if lab == label)


def main():
    layout()
    PAGES.insert(MAIN_TOTAL, divider())
    PLABEL.insert(MAIN_TOTAL, "Appendix")
    for sid, html in PAGES:
        bad = re.findall(r"(?i)bueno|betterplace", html)
        assert not bad, f"{sid} names the founder's past company: {bad}"
    SLIDES.mkdir(parents=True, exist_ok=True)
    for f in SLIDES.glob("*.html"):
        f.unlink()
    for sid, html in PAGES:
        (SLIDES / f"{sid}.html").write_text(html)
    deck = {
        "v": 4, "createdOnFiles": CREATED, "lists": "css", "title": "Save First, Lend Later: Should We?", "cover": "m01",
        "order": [sid for sid, _ in PAGES],
        "sections": {"s1": {"description": "The answer and how it works", "start": "m01"}, "s2": {"description": "How sure, and what decides it", "start": first("How sure")},
                     "s3": {"description": "Who and how big", "start": first("Who")}, "s4": {"description": "Competition, risks, the pilot", "start": first("Edge")},
                     "s5": {"description": "Appendix: the evidence and the numbers", "start": "a00"}},
        "faces": {"source-serif-4": {"family": "Source Serif 4", "href": "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&display=swap"},
                  "ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"}},
        "designSystems": [],
    }
    (OUT / "project" / "deck.json").write_text(json.dumps(deck, indent=1, ensure_ascii=False))
    print(f"wrote {len(PAGES)} slides ({MAIN_TOTAL} main)")


if __name__ == "__main__":
    main()

"""Write the story deck (story/project/…): nine slides that say what the model means,
then an appendix: the per-saver maths behind slides 4-5, and the full numbers deck.

Same rule as build_deck.py: every number comes from the frozen tables by id
(N / F / I / PY), and check_deck.py traces every digit on these slides too.
The founder asked (30 Sep 2026) that the new deck not name his past company, so
the full deck is copied in with those mentions reworded, and the build fails if
any survive.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import build_deck as B
from build_deck import (ACC_TXT, BLUE, BODY, CARD, DARK_SOFT, GREY, INK, LBLUE, MUTED, ORANGE, PAPER, SAFFRON, SAND,
                        SERIF, SANS, AP_HEAD, F, I, N, PY, card, eyebrow, footer, kpi, notes, p, section, table, title)

ROOT = B.ROOT
OUT = ROOT / "story"
SLIDES = OUT / "project" / "slides"
SHORT = "Model: savings_first_model.xlsx, 30 Sep 2026."
SRC = SHORT + " Plan = daily saving + 5% loss cover + gold; half gig, half self-employed."
BROWN = "#8A3B08"

STORY: list[tuple[str, str]] = []


def story(id):
    def deco(fn):
        B._cur[0] = id
        STORY.append((id, fn()))
        return fn
    return deco


def arrow(a, b):
    return f"{a} → {b}"


# ================================================================ 1. cover
@story("cover")
def _():
    body = f"""
{eyebrow("The story in nine slides · 30 September 2026", SAFFRON)}
<div style="display:flex;flex-direction:column;gap:36px">
<h1 style="font-family:{SERIF};font-size:120px;font-weight:600;line-height:1.05;color:{PAPER}">Save first, lend later</h1>
<h2 style="font-family:{SERIF};font-size:56px;font-weight:400;line-height:1.2;color:{PAPER};width:1560px">Does the story add up? Not yet. Here is what would make it add up.</h2>
</div>
{p("Saving first makes customers cheap to win and needs almost no capital. But it pays only if three things go right together: savers stay, daily debits get cheap, and savers go on to buy loans and insurance. A one-year pilot can settle all three.", 36, DARK_SOFT, extra="width:1560px")}
{notes(f'''Say: This is the story in nine slides; the full numbers deck follows as the appendix. The idea is a micro-savings app for delivery and ride workers and for shopkeepers and the self-employed, in equal numbers. They save {I('daily_amount', fmt='inr')} to {I('daily_amount', fmt='inr', seg='ng')} a day automatically, partners hold the money, and we earn later by selling loans and insurance. The short answer to whether it adds up: in the middle case, no; each saver loses money. It becomes a strong business only when three things go right together, and a one-year pilot can test all three before any big money goes in. Likely question: So is the idea dead? Answer: No. It is unproven. The best case is real if the three readings come in.''')}
"""
    return section("cover", body, bg=INK, fg=PAPER, extra_style=";justify-content:space-between;padding:128px")


# ================================================================ 2. the idea
@story("idea")
def _():
    steps = [f"1. Saves {I('daily_amount', fmt='inr')}–{I('daily_amount', fmt='inr', seg='ng')} a day, automatically",
             "2. The money sits with a bank, fund or gold partner, in the saver's name",
             "3. Months of saving show who is steady",
             "4. Partners lend and insure; we earn a fee on each"]
    W, G, H = 368, 64, 150
    boxes = "".join(
        f'<div style="position:absolute;left:{i * (W + G)}px;top:0;width:{W}px;height:{H}px;background:{CARD};border:2px solid {INK};'
        f'border-radius:16px;padding:20px"><p style="font-size:24px;line-height:1.3;color:{INK}">{t}</p></div>' for i, t in enumerate(steps))
    arrows = "".join(f'<x-connector x1="{i * (W + G) + W + 4}" y1="{H // 2}" x2="{(i + 1) * (W + G) - 4}" y2="{H // 2}" style="color:{ORANGE};border-width:3px"></x-connector>'
                     for i in range(3))
    body = f"""
{eyebrow("The idea")}
{title("Workers save a little every day; once we see who is steady, partners lend to them and insure them, and we earn a fee.")}
<div style="display:flex;gap:32px">
{card(p("<b>The problem</b>", 28, INK) + p("A delivery rider or a shopkeeper earns every day but saves nothing, so a bad week means borrowing fast and at a high price.", 28, BODY))}
{card(p("<b>Our idea</b>", 28, INK) + p(f"An app that saves {I('daily_amount', fmt='inr')}–{I('daily_amount', fmt='inr', seg='ng')} a day from their own bank account into gold, a fund or an FD in their own name. That record then earns them loans and cover from partners.", 28, BODY), bg=SAND, border=SAND)}
</div>
<!-- steps: 4 boxes 368x150 at x = 0, 432, 864, 1296; arrows between edge midpoints -->
<div style="position:relative;width:1664px;height:{H}px">{boxes}{arrows}</div>
{p(f"<b>What kind of company:</b> a distributor with an app, like an insurance or loan agent. Partners hold the money and the loans; we cover at most {F('dlg_cap')} of loan losses. <b>Who:</b> half app delivery and ride workers, half shopkeepers and the self-employed.", 24, BODY)}
{footer("Daily amounts are middle-case model inputs (Inputs tab), 30 Sep 2026.", 2)}
{notes(f'''Say: The problem is simple. People who earn daily, a Swiggy rider or a kirana owner, save nothing, so when a bad week comes they borrow fast from a loan app or a moneylender. Our idea: an app that auto-saves {I('daily_amount', fmt='inr')} to {I('daily_amount', fmt='inr', seg='ng')} a day from their own bank account, through UPI Autopay, into gold, a liquid fund or a bank FD held in their own name. After a few months the saving record shows who is steady, and partners offer them loans and insurance through us. We are a distributor, not a lender: we never hold the money, the partner lender carries the loan, and we cover at most {F('dlg_cap')} of its losses, the most RBI allows. Likely question: Why would a saver want a loan from us? Answer: They already borrow; we can offer a cheaper loan because we can see their saving.''')}
"""
    return section("idea", body)


# ================================================================ 3. why save first
@story("whysave")
def _():
    def dots(n_on, n=4):
        return "".join(f'<div style="width:48px;height:48px;border-radius:50%;background:{BLUE if i < n_on else GREY}"></div>' for i in range(n))

    def panel(name, n_on, cap, k1, c1, k2, c2, bg, border):
        inner = (p(f"<b>{name}</b>", 28, INK)
                 + f'<div style="display:flex;gap:16px;align-items:center">{dots(n_on)}<p style="font-size:24px;color:{BODY};width:420px">{cap}</p></div>'
                 + kpi(k1, c1) + kpi(k2, c2))
        return card(inner, bg=bg, border=border, gap=24)
    body = f"""
{eyebrow("Why save first")}
{title("Lending first turns most people away and needs capital; saving first turns nobody away and needs almost none.")}
<div style="display:flex;gap:32px">
{panel("Lend first", 1, f"{F('bueno_approval')} of applicants approved", N("lf_base_cac"), "to find each borrower, paying for the ones turned away",
       N("lf_base_cap_per_rev"), "of capital per ₹1 of revenue, to fund the loans", SAND, SAND)}
{panel("Save first", 4, f"anyone can start, from {F('gold_min')} a day", N("plan_base_cac"), "to win each saver who makes a first debit",
       N("plan_base_cap_per_rev"), f"of capital per ₹1 of revenue: partners hold the money and the loans; we put up a {F('dlg_cap')} loss cover", CARD, "#E3DDD0")}
</div>
{p(f"<b>The hope in the name:</b> people who save steadily repay better. It is not proven: the model assumes gig savers go 90+ days late on {I('loan_dpd90', fmt='pct')} of loans, against {I('lf_dpd90_first', fmt='pct')} of lend-first first loans.", 28, INK)}
{footer("Middle case. Lend-first figures from the founder's past lending data. " + SHORT, 3)}
{notes(f'''Say: Lending first, you pay to find every applicant and then turn most away: only {F('bueno_approval')} were approved in the founder's past lending data, so each borrower cost {N('lf_base_cac')} to find. Someone also has to fund the loans: {N('lf_base_cap_per_rev')} of capital for every rupee of revenue. And covering all of a lender's losses, the old way to make this work, is now barred: an app may cover at most {F('dlg_cap')}. Saving first, nobody is turned away. A saver costs {N('plan_base_cac')} to win, and because partners hold both the money and the loans, we lock up only {N('plan_base_cap_per_rev')} per rupee of revenue, the {F('dlg_cap')} loss cover. The part nobody has proven is that savers repay better. The model assumes it for gig workers, {I('loan_dpd90', fmt='pct')} of loans 90+ days late against {I('lf_dpd90_first', fmt='pct')}, but assumes {I('loan_dpd90', fmt='pct', seg='ng')} for the self-employed, who are riskier. Likely question: Is a saver worth the same as a borrower? Answer: No, and the next two slides are about exactly that.''')}
"""
    return section("whysave", body)


# ================================================================ 4. first catch: money in vs money out
@story("catch1")
def _():
    scale = 1600 / float(B.NUM["story_base_cost_pa_y2"]["value"])
    rev = [("Gold", "plan_base_rev_pa_y2::Savings: gold", ORANGE), ("Loans", "plan_base_rev_pa_y2::Loans (partner)", BLUE),
           ("Insurance", "plan_base_rev_pa_y2::Insurance", LBLUE)]
    cost = [("Debit fees", "story_base_cost_pa_y2_pay", BROWN), ("Support and tech", "story_base_cost_pa_y2_service", GREY),
            ("Loans, insurance, cards and fraud", "story_base_cost_pa_y2_other", MUTED)]

    def bar(parts, total_id, rest_label=None):
        vals = [(lab, N(i), float(B.NUM[i]["value"]), c) for lab, i, c in parts]
        segs = "".join(f'<div style="width:{v * scale:.0f}px;height:48px;background:{c}"></div>' for _, _, v, c in vals)
        legend = [f'<div style="display:flex;gap:10px;align-items:center"><div style="width:24px;height:24px;background:{c};border-radius:4px"></div>'
                  f'<p style="font-size:24px;color:{INK}">{lab} {d}</p></div>' for lab, d, _, c in vals]
        if rest_label:
            rest = float(B.NUM[total_id]["value"]) - sum(v for _, _, v, _ in vals)
            segs += f'<div style="width:{rest * scale:.0f}px;height:48px;background:#DDD6C8"></div>'
            legend.append(f'<div style="display:flex;gap:10px;align-items:center"><div style="width:24px;height:24px;background:#DDD6C8;border-radius:4px"></div>'
                          f'<p style="font-size:24px;color:{INK}">{rest_label}</p></div>')
        return (f'<div style="display:flex;gap:0">{segs}</div>'
                f'<div style="display:flex;gap:32px;flex-wrap:wrap">{"".join(legend)}</div>')

    def row(label, total_id, parts, rest_label=None):
        return (f'<div style="display:flex;flex-direction:column;gap:8px">'
                f'<div style="display:flex;gap:20px;align-items:baseline"><p style="font-size:28px;font-weight:600;color:{INK}">{label}</p>'
                f'<p style="font-size:36px;font-weight:600;color:{INK}">{N(total_id)}</p></div>'
                + bar(parts, total_id, rest_label) + "</div>")
    body = f"""
{eyebrow("The first catch")}
{title("Saving earns almost nothing, and collecting it every day costs more than a saver brings in.")}
<div style="display:flex;flex-direction:column;gap:36px">
{row("What a saver brings us in their second year (middle case)", "plan_base_rev_pa_y2", rev, "Cards, funds and FDs")}
{row("What serving them costs us that year", "story_base_cost_pa_y2", cost)}
</div>
<div style="display:flex;gap:32px">
{card(p(f"<b>Why:</b> each debit costs about {I('cost_debit', fmt='inr')} and a saver makes about {I('debits_success')} a month. The fund and the FD, where most savings apps earn, bring us {N('plan_base_rev_pa_y2::Savings: liquid fund')} and {N('plan_base_rev_pa_y2::Savings: FDs')} a year.", 24, BODY), pad=24)}
{card(p(f"<b>Best case:</b> the same saver brings {N('plan_bull_rev_pa_y2')} and costs {N('story_bull_cost_pa_y2')}, because debits fall to {I('cost_debit', 'bull', fmt='inr')} each and many more savers buy loans, insurance and gold.", 24, BODY), pad=24, bg=SAND, border=SAND)}
</div>
{footer("Per active saver in their second year, both halves. " + SHORT, 4)}
{notes(f'''Say: This is the first catch, and the old deck never said it plainly. Take one saver in their second year, middle case. They bring us {N('plan_base_rev_pa_y2')} a year: gold margin {N('plan_base_rev_pa_y2::Savings: gold')}, loan fees {N('plan_base_rev_pa_y2::Loans (partner)')}, insurance commission {N('plan_base_rev_pa_y2::Insurance')}. Serving them costs {N('story_base_cost_pa_y2')}, and {N('story_base_cost_pa_y2_pay')} of that is debit fees alone: about {I('cost_debit', fmt='inr')} a debit, about {I('debits_success')} debits a month, plus pre-debit notices and failed debits. Support and tech add {N('story_base_cost_pa_y2_service')}. The money itself earns almost nothing: {N('plan_base_rev_pa_y2::Savings: liquid fund')} from the fund and {N('plan_base_rev_pa_y2::Savings: FDs')} from FDs. In the best case the picture flips: {N('plan_bull_rev_pa_y2')} in, {N('story_bull_cost_pa_y2')} out, mostly because a debit costs {I('cost_debit', 'bull', fmt='inr')} and far more savers buy. Likely question: Why not debit weekly? Answer: That cuts the fee by about 80%, but the daily habit is the product. The pilot prices daily debits before launch; if the price stays high, switch to weekly.''')}
"""
    return section("catch1", body)


# ================================================================ 5. second catch: savers stop before they borrow
@story("catch2")
def _():
    W = 900
    rows = [("plan_base_m3_still", "still saving at month 3"), ("plan_base_m12_still", "still saving after a year"),
            ("plan_base_m24_still", "still saving after two years"), ("story_base_borrow_60", "take a loan within five years")]
    bars = "".join(
        f'<div style="display:flex;flex-direction:column;gap:8px">'
        f'<div style="display:flex;gap:16px;align-items:baseline"><p style="font-size:36px;font-weight:600;color:{INK}">{N(i)}</p>'
        f'<p style="font-size:28px;color:{BODY}">{lab}</p></div>'
        f'<div style="width:{float(B.NUM[i]["value"]) * W:.0f}px;height:32px;background:{ORANGE if i.startswith("story") else BLUE};border-radius:4px"></div></div>'
        for i, lab in rows)
    body = f"""
{eyebrow("The second catch")}
{title(f"Most savers stop before they ever borrow, so a borrower costs about {N('story_base_borrower_cost_x_lf')} times what lending first pays to find one.")}
<div style="display:flex;gap:64px">
<div style="flex:1;display:flex;flex-direction:column;gap:24px">
{p("Of all savers who make a first debit (middle case):", 24, MUTED)}
{bars}
</div>
<div style="width:560px;display:flex;flex-direction:column;gap:28px">
{kpi(N("story_base_cac_per_borrower"), f"to find each saver who ever borrows: {N('plan_base_cac')} per saver, divided by {N('story_base_borrow_60')}")}
{kpi(N("lf_base_cac"), "to find each borrower by lending first", color=MUTED)}
{p(f"<b>Best case:</b> {N('story_bull_borrow_60_one_in')} savers borrow, and a borrower costs {N('story_bull_cac_per_borrower')}, still {N('story_bull_borrower_cost_x_lf')} times lending first.", 24, BODY)}
</div>
</div>
{p("So loans alone can't pay for finding savers. Gold and insurance must earn too, and savers must stay long enough to buy.", 28, INK)}
{footer("Share of activated savers. " + SRC, 5)}
{notes(f'''Say: The second catch. Loans are offered from month {I('loan_start')}, but by month 3 only {N('plan_base_m3_still')} of savers are still saving, {N('plan_base_m12_still')} after a year and {N('plan_base_m24_still')} after two, which is what the founder expects for these workers. So in the middle case only {N('story_base_borrow_60_one_in')}, {N('story_base_borrow_60')}, ever takes a loan within five years. If loans had to pay for finding savers, each borrower would cost {N('story_base_cac_per_borrower')}: {N('plan_base_cac')} per saver divided by {N('story_base_borrow_60')}. Lending first costs {N('lf_base_cac')}. So the flip does not make borrowers cheaper; it makes savers cheaper, and savers only pay if they also buy gold and insurance and stay. Even in the best case, {N('story_bull_borrow_60_one_in')} borrow and a borrower costs {N('story_bull_cac_per_borrower')}, against {N('lf_bull_cac')} lending first. Likely question: Couldn't you offer loans sooner? Answer: Yes, from month 3 in the best case, but then you are lending on three months of data, which is close to lending first.''')}
"""
    return section("catch2", body)


# ================================================================ 6. the crux: three things together
@story("crux")
def _():
    def dial(n, name, sub, base_v, bull_v, why, tag=None):
        tagp = (f'<p style="font-size:24px;font-weight:600;color:{PAPER};background:{ACC_TXT};padding:4px 16px;border-radius:24px">{tag}</p>'
                if tag else "")
        head = (f'<div style="display:flex;gap:16px;align-items:center;justify-content:space-between">'
                f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{n} · {name}</p>{tagp}</div>')
        return card(head + p(sub, 24, BODY)
                    + f'<p style="font-size:56px;font-weight:600;line-height:1.1;color:{INK}">{arrow(base_v, bull_v)}</p>'
                    + p(why, 24, BODY), pad=32, gap=10)
    body = f"""
{eyebrow("What has to go right")}
{title("So it rests on three things going right together: savers stay, debits get cheap, and what we sell pays.")}
<div style="display:flex;gap:24px">
{dial(1, "Savers stay", "Still saving after a year", N("plan_base_m12_still"), N("plan_bull_m12_still"),
      "Every month a saver stays is another month to sell to them.")}
{dial(2, "Debits get cheap", "Cost per debit", I("cost_debit", fmt="inr"), I("cost_debit", "bull", fmt="inr"),
      "At today's price, debit fees alone are more than a saver brings in.")}
{dial(3, "What we sell pays", "Active savers who borrowed by month 12", N("plan_base_m12_borrowed"), N("plan_bull_m12_borrowed"),
      f"<b>Must hold:</b> miss it and even the best case earns only {N('wtbt_all_bull_except_cross_sell')} times what a saver cost to win.")}
</div>
<div style="display:flex;gap:24px;align-items:center">
{card(p("Middle case today", 24, MUTED) + p(f"Each saver loses {N('plan_base_ltv60').lstrip('−')} over five years, on top of the {N('plan_base_cac')} it cost to win them. {N('plan_base_path_y10_usd_m')} revenue in year 10.", 24, INK), bg=SAND, border=SAND, gap=8, pad=24)}
<x-shape kind="arrow-right" style="background:{ORANGE};width:80px;height:40px"></x-shape>
{card(p("All three go right (best case)", 24, DARK_SOFT) + p(f"Each saver earns {N('plan_bull_ltv60')} over five years, {N('plan_bull_ltv60_cac')} times the {N('plan_bull_cac')} it cost to win them. {N('plan_bull_path_y10_usd_m')} in year 10.", 24, PAPER), bg=INK, border=INK, gap=8, pad=24)}
</div>
{footer("Middle case → what the best case needs. Profit is after serving costs, discounted 20% a year. Model, 30 Sep 2026.", 6)}
{notes(f'''Say: Put the two catches together and the story rests on three things. One: savers stay; {N('plan_base_m12_still')} still saving after a year in the middle case, {N('plan_bull_m12_still')} needed. Two: debits get cheap; {I('cost_debit', fmt='inr')} a debit today, {I('cost_debit', 'bull', fmt='inr')} needed. Three: what we sell pays; {N('plan_base_m12_borrowed')} of active savers have borrowed by month 12 in the middle case, {N('plan_bull_m12_borrowed')} needed, with insurance at {N('plan_base_m12_insured')} against {N('plan_bull_m12_insured')}, and gold, loan and insurance fees at their best-case rates. With all three, each saver earns {N('plan_bull_ltv60')} over five years, {N('plan_bull_ltv60_cac')} times what it cost to win them, and revenue reaches about {N('plan_bull_path_y10_usd_m')} in year 10. If only the third goes right, it still doesn't work; if everything goes right except the third, it falls to {N('wtbt_all_bull_except_cross_sell')}. Missing cheap debits or savers staying costs about two points each ({N('wtbt_all_bull_except_debit_cost')} and {N('wtbt_all_bull_except_retention')}), which still clears 3. Two smaller assumptions, how much people save and what they cost to win, matter less. Likely question: Isn't 'all three at once' wishful? Answer: Yes. That is why no money goes past the pilot until the three readings come in.''')}
"""
    return section("crux", body)


# ================================================================ 7. two kinds of saver
@story("segments")
def _():
    rows = [["Saved a day", I("daily_amount", fmt="inr"), I("daily_amount", fmt="inr", seg="ng")],
            ["Still saving after a year", N("seg_gig_base_still_m12"), N("seg_ng_base_still_m12")],
            ["Loans 90+ days late", I("loan_dpd90", fmt="pct"), I("loan_dpd90", fmt="pct", seg="ng")],
            ["Profit per saver ÷ cost to win them, middle case", N("seg_gig_base_ltv60_cac"), N("seg_ng_base_ltv60_cac")],
            ["The same, best case", N("seg_gig_bull_ltv60_cac"), N("seg_ng_bull_ltv60_cac")]]
    body = f"""
{eyebrow("Two kinds of saver")}
{title("Shopkeepers and the self-employed make the best case sturdier: they save more and stay longer, but repay worse.")}
{table(["Middle case unless stated", "Delivery and ride workers", "Shopkeepers and the self-employed"], rows, [38, 28, 34], size=28)}
{p("The self-employed numbers are the least certain in the model: nobody publishes what it costs to sign up a shopkeeper or how long they keep saving. The pilot reads each half separately.", 28, INK)}
{footer("Model inputs and outputs by half. " + SHORT, 7)}
{notes(f'''Say: Half our savers are delivery and ride workers, half are shopkeepers, tradespeople, drivers outside the apps and small business owners. The model assumes the self-employed save {I('daily_amount', fmt='inr', seg='ng')} a day against {I('daily_amount', fmt='inr')} and stay longer, {N('seg_ng_base_still_m12')} still saving after a year against {N('seg_gig_base_still_m12')}, but go 90+ days late on {I('loan_dpd90', fmt='pct', seg='ng')} of loans against {I('loan_dpd90', fmt='pct')}. In the middle case both halves lose money. In the best case the self-employed reach {N('seg_ng_bull_ltv60_cac')} times their cost against {N('seg_gig_bull_ltv60_cac')}, which is why the mix makes the best case sturdier: gig workers alone would stop at {N('lever_A+Cgigonly_bull_y10')} in year 10. Likely question: Why not start with one group? Answer: Two groups means two sales approaches for a small team. If their month-6 readings diverge, the next year's money goes to the one that works.''')}
"""
    return section("segments", body)


# ================================================================ 8. how it dies
@story("dies")
def _():
    items = [("Before launch", "Debits stay expensive", f"Payment quotes stay above {I('cost_debit', 'bull', fmt='inr')} a debit; the list price is {F('debit_list')}.", "Switch to one debit a week."),
             ("Month 3", "Savers stop", f"Fewer than {N('plan_base_m3_still')} of savers are still saving.", "Stop paying for sign-ups; fix the product first."),
             ("Months 6 to 12", "Savers don't buy", f"Only about {N('plan_base_m12_borrowed')} of active savers have borrowed by month 12.", "Stop: what is left is a thin gold margin."),
             ("Any time", "Gold rules tighten", f"Gold becomes a regulated security, or its margin is cut. Gold is {N('story_base_rev60_gold')} of revenue over five years.", f"Move daily saving into {F('sip_min')}+ fund debits.")]
    cards = "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:{CARD};padding:24px;border:1px solid {ORANGE};border-top:8px solid {ORANGE};border-radius:16px">'
        f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACC_TXT}">{when}</p>'
        f'<p style="font-size:28px;font-weight:600;line-height:1.2;color:{INK}">{what}</p>'
        + p(sign, 24, BODY) + '<div style="flex:1"></div>' + p(f"<b>Then:</b> {act}", 24, INK) + "</div>"
        for when, what, sign, act in items)
    body = f"""
{eyebrow("How it dies")}
{title("Four ways it dies, and we would see each one within the first year.")}
<div style="display:flex;gap:24px;align-items:stretch">{cards}</div>
{p("A fifth risk is outside our control: a big app does it first. PhonePe already offers daily gold with Jar.", 28, INK)}
{footer("Warning levels are the model's middle-case values. " + SHORT, 8)}
{notes(f'''Say: Assume this failed. There are four likely ways, and each shows up early. Before launch: if payment companies won't quote {I('cost_debit', 'bull', fmt='inr')} a debit or less, against a list price of {F('debit_list')}, daily saving can't pay, so we switch to weekly. Month 3: if fewer than {N('plan_base_m3_still')} are still saving, we are below even the middle case, and we stop spending on sign-ups. Months 6 to 12: if only about {N('plan_base_m12_borrowed')} of active savers have borrowed by month 12, the middle case, the business is a thin gold margin and we stop. Any time: gold is unregulated and carries the daily habit, {N('story_base_rev60_gold')} of five-year revenue in the middle case; if its rules tighten we move to {F('sip_min')}+ fund debits, which earn far less. And a big app could simply do this first. Likely question: Which worries you most? Answer: Savers stopping. Riders change platforms often, and any UPI app can now move their mandate.''')}
"""
    return section("dies", body)


# ================================================================ 9. the test
@story("test")
def _():
    rows = [["1. Do savers stay?", "Still saving after a year", N("plan_base_m12_still"), N("plan_bull_m12_still")],
            ["2. Do debits get cheap?", "Cost per debit, in a contract signed before launch", I("cost_debit", fmt="inr"), I("cost_debit", "bull", fmt="inr")],
            ["3. Do savers buy?", "Active savers who borrowed by month 12", N("plan_base_m12_borrowed"), N("plan_bull_m12_borrowed")],
            ["", "Active savers with insurance by month 12", N("plan_base_m12_insured"), N("plan_bull_m12_insured")]]
    body = f"""
{eyebrow("The test")}
{title(f"A one-year pilot with {PY(1, 'new_activated')} savers settles all three questions for {N('plan_base_need_y1_cr')}.")}
{table(["The question", "What we read", "Stop at (middle case)", "Go at (best case)"], rows, [24, 40, 18, 18], size=28)}
<div style="display:flex;gap:32px">
{card(p(f"<b>{N('plan_base_need_y1_cr')}</b> for the year in the middle case ({N('plan_bull_need_y1_cr')} to {N('plan_bear_need_y1_cr')} across cases). {N('plan_base_y1_fixed_opex_cr')} of it is the team and fixed costs.", 24, BODY), pad=24)}
{card(p("<b>Who:</b> half gig workers through one platform partner, half shopkeepers through markets, suppliers and associations. Read every number for each half separately.", 24, BODY), pad=24, bg=SAND, border=SAND)}
</div>
{footer("Year 1 of the growth plan. " + SHORT, 9)}
{notes(f'''Say: The next step is not a big round; it is a one-year pilot with {PY(1, 'new_activated')} savers in Delhi NCR, half gig workers, half the self-employed. It costs about {N('plan_base_need_y1_cr')} in the middle case, mostly the team. At month 12 we read the three numbers on this slide. If they sit at the middle case, we stop. If they reach the best case, the model says each saver earns {N('plan_bull_ltv60_cac')} times what it cost to win them, and we raise to scale. The debit price is settled before launch, in a signed contract, so the first question is answered before a rupee of sign-up money is spent. Likely question: Could a smaller or shorter pilot do? Answer: Sign-ups and saving, yes. But loans start in month {I('loan_start')} and insurance in month {I('ins_start')}, so the third question needs a year and enough savers who stay.''')}
"""
    return section("test", body)


# ================================================================ appendix: divider + the per-saver maths
@story("ap_divider")
def _():
    items = [("A", "The per-saver maths behind slides 4 and 5"),
             ("Full deck 3–17", "The full numbers deck: customer, problem, product, channels, money, unit economics, what has to be true, the path to $100M, competition, risks, the pilot"),
             ("Full deck A1–A15", "The law, all model outputs, levers, lend-first data, channels, comparables, hard questions, sources")]
    rows = "".join(f'<div style="display:flex;gap:32px;align-items:baseline"><p style="width:300px;font-size:28px;font-weight:600;color:{ACC_TXT}">{a}</p>'
                   f'<p style="flex:1;font-size:28px;line-height:1.35;color:{INK}">{b}</p></div>' for a, b in items)
    body = f"""
{eyebrow("Appendix")}
<h1 style="font-family:{SERIF};font-size:120px;font-weight:600;line-height:1.05;color:{INK}">Behind the story</h1>
<div style="display:flex;flex-direction:column;gap:28px">{rows}</div>
{notes("The appendix holds the evidence. First one new slide with the per-saver maths behind slides 4 and 5. Then the full numbers deck, numbered as it was (its slides 3 to 17 and A1 to A15), with the founder's past company no longer named.")}
"""
    return section("ap_divider", body, bg=SAND, extra_style=";justify-content:center;gap:48px")


@story("ap_maths")
def _():
    def pair(s, ids):
        return " / ".join(N(i.format(s=s)) for i in ids)
    rows = [["What a saver brings us a year", N("plan_base_rev_pa_y2"), N("plan_bull_rev_pa_y2")],
            ["…from gold / loans / insurance", pair("base", ["plan_{s}_rev_pa_y2::Savings: gold", "plan_{s}_rev_pa_y2::Loans (partner)", "plan_{s}_rev_pa_y2::Insurance"]),
             pair("bull", ["plan_{s}_rev_pa_y2::Savings: gold", "plan_{s}_rev_pa_y2::Loans (partner)", "plan_{s}_rev_pa_y2::Insurance"])],
            ["What serving them costs a year", N("story_base_cost_pa_y2"), N("story_bull_cost_pa_y2")],
            ["…debit fees / support and tech / loans, insurance, cards, fraud", pair("base", ["story_{s}_cost_pa_y2_pay", "story_{s}_cost_pa_y2_service", "story_{s}_cost_pa_y2_other"]),
             pair("bull", ["story_{s}_cost_pa_y2_pay", "story_{s}_cost_pa_y2_service", "story_{s}_cost_pa_y2_other"])],
            ["Savers who took a loan by month 12 / 24 / 60", pair("base", ["story_{s}_borrow_12", "story_{s}_borrow_24", "story_{s}_borrow_60"]),
             pair("bull", ["story_{s}_borrow_12", "story_{s}_borrow_24", "story_{s}_borrow_60"])],
            ["Cost to win a saver / per saver who ever borrows", pair("base", ["plan_{s}_cac", "story_{s}_cac_per_borrower"]), pair("bull", ["plan_{s}_cac", "story_{s}_cac_per_borrower"])],
            ["Lending first: cost to find a borrower", N("lf_base_cac"), N("lf_bull_cac")],
            ["Five-year revenue from gold / loans / insurance", pair("base", ["story_{s}_rev60_gold", "story_{s}_rev60_loans", "story_{s}_rev60_ins"]),
             pair("bull", ["story_{s}_rev60_gold", "story_{s}_rev60_loans", "story_{s}_rev60_ins"])]]
    body = f"""
{eyebrow("Appendix A")}
{title("A saver's money in and out, and the borrower maths, in the middle and best cases.")}
{table(["Per active saver in their second year, unless stated", "Middle case", "Best case"], rows, [48, 26, 26], head_bg=AP_HEAD)}
{footer("Model: savings_first_model.xlsx, Outputs tab (story block), 30 Sep 2026. Both halves; loans share = of activated savers.", "A")}
{notes(f'''Every number here is on the Outputs tab of savings_first_model.xlsx, in the story block, and the workbook's formulas are checked against a separate Python engine on {B.VERIFY['checked']:,} values across {B.VERIFY['cases']} cases. The cost per saver who ever borrows is the cost to win a saver divided by the share of activated savers who take a first loan within 60 months. It overstates what a borrower costs, because savers also bring gold and insurance revenue; it is there to show that saving first does not make borrowers cheaper to find.''')}
"""
    return section("ap_maths", body, bg=SAND)


# ================================================================ the full deck, without the founder's past company's name
DROP = {"cover", "bueno"}          # the story's cover replaces one; the other was the old company's story
RENAME = {"a4_bueno": "a4_lendfirst"}
EDITS = {
    "funnel": [("and the way Bueno absorbed losses is now barred.", "and covering all of the lender's losses is now barred."),
               ("<b>Then: Bueno, 2019–22</b>", "<b>Then: 2019–22</b>"),
               ("We covered 100% of the lending partner's losses.", "A lend-first app could cover 100% of the lending partner's losses."),
               ("Sources: founder data (Bueno);", "Sources: founder's past lending data;"),
               ("applicants at Bueno, we approved", "applicants, a lend-first app approved"),
               ("We could do it because we covered 100% of our NBFC partner's losses.", "Lend-first apps did it by covering 100% of the partner NBFC's losses."),
               ("So Bueno's model can't run today", "So that model can't run today")],
    "unit": [("Lend-first (Bueno as run)", "Lend-first (founder's past data)"),
             ("because the way Bueno ran it is now barred", "because covering all the losses is now barred")],
    "a4_bueno": [("Bueno's numbers, as the founder gave them, drive the lending-first comparison.",
                  "The founder's past lending numbers drive the lending-first comparison."),
                 (">Bueno, 2019–22<", ">Lend-first, 2019–22<"),
                 (" (tables/inputs_founder_bueno.csv)", ""),
                 ("and Bueno covered 100% of losses", "and the app covered 100% of losses")],
    "a5_marketing": [(" Reviving old Bueno borrowers is not on the list: that data belongs to BetterPlace and was collected for lending, "
                      "so using it here would break purpose limits under the IT Act rules and the DPDP Act.", "")],
}
QA_EDIT = {
    "Why you?": ("Why you?", lambda: f"I have lent to this segment at scale: {F('bueno_loans')} loans a month. Before that, credit policy at Capital One, loss models for Citi at EXL, Encore Capital, and analytics at Swiggy."),
    "Why did Bueno end?": ("Do most savers ever borrow?", lambda: f"No. In the base case {N('story_base_borrow_60_one_in')} takes a loan within five years, so each borrower costs {N('story_base_cac_per_borrower')} to find, against {N('lf_base_cac')} lending first."),
    "Why would a platform partner with you?": ("Why would a platform partner with you?", lambda: "A free savings benefit for riders as the Labour Codes push social security, and an existing relationship with Swiggy. Unproven: the pilot needs one platform to sign."),
}
FOOT = re.compile(r'(bottom:64px;display:flex;gap:32px"><p style="flex:1;font-size:24px;color:#[0-9A-Fa-f]{6}">.*?'
                  r'</p><p style="font-size:24px;color:#[0-9A-Fa-f]{6}">)([^<]*)(</p></div>)', re.S)


def full_deck():
    qa = [QA_EDIT.get(q, (q, a)) for q, a in B.QA]
    replaced = dict(B.SLIDES_OUT)
    replaced["a9_qa3"] = B.qa_slide(3, qa[10:15])[1]
    out = []
    for sid, html in B.SLIDES_OUT:
        if sid in DROP:
            continue
        html = replaced[sid]
        for old, new in EDITS.get(sid, []):
            assert old in html, f"{sid}: expected text not found: {old[:60]}"
            html = html.replace(old, new)
        html = html.replace(B.PLAN_SRC, "Model, 30 Sep 2026. Plan = daily saving + 5% loss cover + gold.")
        feet = FOOT.findall(html)
        assert len(feet) == 1, f"{sid}: expected one footer page label, found {len(feet)}"
        html = FOOT.sub(lambda m: f"{m.group(1)}Full deck · {m.group(2)}{m.group(3)}", html)
        nid = "full_" + RENAME.get(sid, sid)
        html = html.replace(f'<section id="{sid}"', f'<section id="{nid}"', 1)
        out.append((nid, html))
    return out


def main():
    slides = STORY + full_deck()
    for sid, html in slides:
        bad = re.findall(r"(?i)bueno|betterplace", sid + html)
        assert not bad, f"{sid} still names the founder's past company: {bad}"
    SLIDES.mkdir(parents=True, exist_ok=True)
    for f in SLIDES.glob("*.html"):
        f.unlink()
    order = []
    for sid, html in slides:
        (SLIDES / f"{sid}.html").write_text(html)
        order.append(sid)
    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "lists": "css",
        "title": "Save First, Lend Later: The Story",
        "cover": "cover",
        "order": order,
        "sections": {
            "s1": {"description": "The story in nine slides", "start": "cover"},
            "s2": {"description": "Appendix: the per-saver maths", "start": "ap_divider"},
            "s3": {"description": "Full deck: customer, problem and the flip", "start": "full_customer"},
            "s4": {"description": "Full deck: product, channels and money", "start": "full_product"},
            "s5": {"description": "Full deck: does it add up", "start": "full_unit"},
            "s6": {"description": "Full deck: the next step", "start": "full_pilot"},
            "s7": {"description": "Full deck: appendix", "start": "full_a1_regmap"},
        },
        "faces": {
            "source-serif-4": {"family": "Source Serif 4", "href": "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&display=swap"},
            "ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"},
        },
        "designSystems": [],
    }
    (OUT / "project" / "deck.json").write_text(json.dumps(deck, indent=1, ensure_ascii=False))
    (OUT / "used_ids.json").write_text(json.dumps(B.USED, indent=1, ensure_ascii=False))
    print(f"wrote {len(order)} slides ({len(STORY)} story + appendix): {order[:12]} …")


if __name__ == "__main__":
    main()

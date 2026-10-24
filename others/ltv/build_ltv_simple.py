"""The one-saver LTV/CAC deck: the meeting document (final/3). Rebased 24 Oct 2026; round 2 applies the merged review fixes
(reviews/2026-10-24_rebase/FIXES.md, sections A, B and C). Founders 23 Oct: "super complicated ... keep things pointed"; 24 Oct:
"by just cross-selling, what are our 5-year and 8-year LTVs?"
Main pages: the answer (cover, cross-selling in rupees first); where the value comes from (one waterfall page); what changed (the
bridge); what's uncertain; what it takes (one lever at a time, then the ladder); the four facts. Appendix: the inputs, the company.
Every number is read from tables/ (model/ltv_odds.py, model/ltv_bridge.py, model/online_plan.py), never retyped; the shared pages
come from ltv/odds_pages.py and the page frame from ltv/build_ltv_deck.py. Writes ltv/LTV_CAC_simple.html and .pdf.
Usage (from others/): PYTHONPATH=model:ltv:online:seed python ltv/build_ltv_simple.py"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_ltv_deck as ld  # noqa: E402  (page frame, colours, svg helpers)
import odds_pages as od  # noqa: E402  (the shared main-case pages and the tables)

op, sp, lo = ld.op, ld.sp, od.lo
T, R, svg, page, chips, two = ld.T, ld.R, ld.svg, ld.page, ld.chips, ld.two
INK, NAVY, TEAL, AMBER, SLATE, LINE, LATE, MUTE = ld.INK, ld.NAVY, ld.TEAL, ld.AMBER, ld.SLATE, ld.LINE, ld.LATE, ld.MUTE
NAVY2, NAVY3, NAVY4, RED = ld.NAVY2, ld.NAVY3, ld.NAVY4, ld.RED
rs, pct, x, usd, month, halo = ld.rs, ld.pct, od.x, od.usd, od.month, od.halo
S5, S8, CAC, MAIN = od.S5, od.S8, od.CAC, od.MAIN
LIGHT_TEAL = "#7cc4b8"
SERVE = LATE                     # serving: the same colour in every deck


def rev(s):
    return float(s["Fund fees"] + s["Loans (all referrals)"] + s["Cards"] + s["Insurance"] + s["Other products"])


def cross_words():
    """FIXES B1: the cross-sell answer, in rupees, before and after serving."""
    return (f"That is {x(S5['cross-sell / CAC'])} and {x(S8['cross-sell / CAC'])} of the {rs(CAC)} it costs to win a saver, before serving, and less than "
            f"the {rs(S5['serving'])} / {rs(S8['serving'])} it costs to serve them, so on its own it never pays back "
            f"({x(S5['cross-sell net of serving / CAC'])} after serving). Insurance, recharge, bills, FD and NPS are not counted.")


def unconfirmed_words():
    """FIXES B3: the two inputs still to be confirmed in writing, and what they would do."""
    return (f"Assumes debits cost us ₹{op.DEBIT_COST:.0f} and a {pct(op.EQ_TRAIL, 2)} equity fund fee, both still to be confirmed in writing: "
            f"₹2 a weekly debit would cut a saver to about {x(od.ltvl('We pay Rs 2 a debit, weekly'))}, a 0.5% fee to about "
            f"{x(od.ltvl('Equity fund fee 0.5%, not 0.75%'))}.")


# ---------------------------------------------------------------------------------------------------------- 1 the answer (cover)
def cover(n):
    big = (f'<div class="ctile" style="padding:18px 24px 16px;border:2px solid {TEAL}">'
           f'<div style="font-size:12px;font-weight:800;letter-spacing:.12em;color:{TEAL}">CROSS-SELLING ALONE (LOANS AND CARDS), PER SAVER</div>'
           f'<div class="cbig" style="font-size:40px;margin-top:4px">{rs(S5["cross-sell"])} in 5 years · {rs(S8["cross-sell"])} in 8</div>'
           f'<div class="csub" style="font-size:13.5px;margin-top:6px">{cross_words()}</div></div>')
    net = (f'<div class="ctile" style="padding:16px 24px 14px">'
           f'<div style="font-size:12px;font-weight:800;letter-spacing:.12em;color:{SLATE}">WITH FUND FEES, AFTER SERVING (LTV/CAC)</div>'
           f'<div class="cbig" style="font-size:34px;margin-top:4px">{od.XMED} in 5 years · {od.XMED8} in 8</div>'
           f'<div class="csub" style="font-size:13.5px">Pays back in month {od.PAY}. LTV/CAC: {od.GLOSS["ltv"]}.</div></div>')
    conf = (f'<div class="ctile" style="padding:14px 24px 12px;border-left:6px solid {AMBER}">'
            f'<div style="font-size:12px;font-weight:800;letter-spacing:.12em;color:{AMBER}">TWO INPUTS STILL TO CONFIRM IN WRITING</div>'
            f'<div class="csub" style="font-size:13.5px;margin-top:4px;color:{INK}">{unconfirmed_words()}</div></div>')
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:50px;margin-top:120px">What one saver is worth</div>
  <div class="ctag">The answer to "by just cross-selling, what are our 5-year and 8-year LTVs?", on the founders' inputs of 24 October.</div>
  <div class="cmeta">October 2026 · Confidential · {n} pages</div>
</div>
<div class="cright" style="padding:44px 50px"><div style="display:grid;gap:12px">{big}{net}{conf}</div>
<div class="cnote" style="margin-top:12px;font-size:12.5px;line-height:1.45">Cost to win: {od.CAC_WORDS}. Funds are bought in the saver's own name;
the app never holds money.</div></div>
</section>"""


# ---------------------------------------------------------------------------------------------------------- 2 where the value comes from
def wf_svg(s, head, W=560, H=312, hi=960.0):
    steps = [("Fund fees", float(s["Fund fees"]), NAVY), ("Loans", float(s["Loans (all referrals)"]), NAVY3),
             ("Cards", float(s["Cards"]), LIGHT_TEAL), ("Serving", -float(s["serving"]), SERVE)]
    top, bot = 70, H - 52
    Y = lambda v: bot - (bot - top) * v / hi
    bw, gap, x0 = 76, 22, 10
    out = [T(0, 16, head, 13, 800, NAVY, ls=1.1)]
    out.append(f'<line x1="0" y1="{bot}" x2="{W}" y2="{bot}" stroke="{INK}" stroke-width="1.2"/>')
    run, xs = 0.0, []
    for i, (nm, v, c) in enumerate(steps):
        xx = x0 + i * (bw + gap)
        xs.append(xx)
        a, b = run, run + v
        out.append(R(xx, Y(max(a, b)), bw, max(abs(Y(a) - Y(b)), 2), c, r=5))
        ty = Y(max(a, b)) - 8 if v >= 0 else Y(min(a, b)) + 18
        out.append(halo(T(xx + bw / 2, ty, ("+" if v >= 0 else "−") + rs(abs(v)), 15, 800, c if c != LIGHT_TEAL else TEAL, "middle"), 5))
        out.append(T(xx + bw / 2, bot + 20, nm, 12.5, 700, SLATE, "middle"))
        if i < len(steps) - 1:
            out.append(f'<line x1="{xx + bw}" y1="{Y(b):.1f}" x2="{xx + bw + gap}" y2="{Y(b):.1f}" stroke="{MUTE}" stroke-dasharray="3 3"/>')
        run = b
    # the cross-sell bracket: loans + cards, against serving
    cross = float(s["Loans (all referrals)"] + s["Cards"])
    bx0, bx1 = xs[1], xs[2] + bw
    by = Y(float(s["Fund fees"]) + cross) - 30
    out.append(f'<path d="M{bx0} {by + 8} L{bx0} {by} L{bx1} {by} L{bx1} {by + 8}" fill="none" stroke="{TEAL}" stroke-width="1.8"/>')
    out.append(halo(T((bx0 + bx1) / 2, by - 7, f"cross-sell {rs(cross)}, less than serving {rs(s['serving'])}", 12, 800, TEAL, "middle")))
    xx = x0 + len(steps) * (bw + gap)
    out.append(R(xx, Y(run), bw, bot - Y(run), NAVY2, r=5))
    out.append(f'<line x1="{xx - 6}" y1="{Y(CAC):.1f}" x2="{xx + bw + 8}" y2="{Y(CAC):.1f}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
    out.append(T(xx + bw + 12, Y(CAC) - 2, rs(CAC), 11.5, 800, RED) + T(xx + bw + 12, Y(CAC) + 12, "to win", 11, 700, RED))
    inside = run < CAC and Y(run) - Y(CAC) < 30                 # the net's label would touch the ₹495 line: put it inside the bar
    out.append(T(xx + bw / 2, Y(run) + 20, rs(run), 16, 800, "white", "middle") if inside else
               halo(T(xx + bw / 2, Y(run) - 8, rs(run), 17, 800, NAVY2, "middle"), 5))
    out.append(T(xx + bw / 2, bot + 20, "What's left", 12.5, 800, INK, "middle"))
    out.append(T(xx + bw / 2, bot + 38, f"= {x(run / CAC)}", 13, 800, NAVY, "middle"))
    return svg(W, H, "".join(out))


def p_value(n):
    hi = max(rev(S8), CAC) * 1.12
    F = od.FUN
    ty = F[F.index.str.startswith("type:")]
    nloans = float(ty["per 100 savers won"].sum())
    X = od.X
    body = two(wf_svg(S5, "FIRST 5 YEARS (₹ PER SAVER WON)", hi=hi), wf_svg(S8, "FIRST 8 YEARS", hi=hi), 560) + chips([
        (f"Fund fees: {od.val('blend')} a year of the balance", f"80% in equity funds at {pct(op.EQ_TRAIL, 2)}, 20% in a debt fund at ~{pct(od.DEBT_MAIN, 2)}, "
                                                              "paid while the saver keeps saving. A saver who stops takes the balance, so the fees stop."),
        (f"Loans: about {nloans:.0f} per 100 savers in 5 years", f"One-off lender fees: {od.lakh(X['ticket'])} first loans at {pct(X['fee'])}; "
                                                                 f"{pct(op.LOAN_APPLY)} of the users we can reach apply a year and {pct(X['approved_first'])} of first "
                                                                 f"loans are approved (gold {pct(op.GOLD_APPROVAL)}, home and property {pct(X['loan_home_approval'])})."),
        (f"Serving: {rs(S5['serving'])} in 5 years", f"₹{X['support_cost']:.0f} of support a month per saver still saving and ₹{op.TECH_PER_SAVER:.0f} of tech "
                                                     f"for each of the {op.LOAN_REACH:.2f} people reached, plus the 10% contingency. Debits ₹0 (to confirm).")])
    title = (f"Fund fees bring {float(S5['Fund fees']) / rev(S5):.0%} of a saver's revenue in 5 years; cross-selling brings {rs(S5['cross-sell'])}, "
             f"less than the {rs(S5['serving'])} it costs to serve the saver")
    p600 = od.levm_usd("Cost to win Rs 600 (our funnel)")
    return page(n, "The answer", "WHERE ONE SAVER'S VALUE COMES FROM", title, body,
                f"One online saver won, the main case, undiscounted. Loans count the KYC'd sign-ups who came with the saver ({od.GLOSS['kyc']}). Cards: "
                f"{pct(X['card_share'])} of savers still saving at month 7 take one. Cost to win: ₹{op.CAC:.0f} + 10% = {rs(CAC)}; at ₹600 (₹660 with the "
                f"contingency) a saver is about {x(od.ltvl('Cost to win Rs 600 (our funnel)'))} / {x(od.ltvl8('Cost to win Rs 600 (our funnel)'))} and the "
                f"company needs {p600}.")


# ---------------------------------------------------------------------------------------------------------- 3 the bridge
BRIDGE_ROWS = [   # (a word the table's step must contain, what the row says, the line under it, to confirm?)
    ("contingency", "Serving carries the 10% contingency (a correction)", "as the cost to win and the company model already did", False),
    ("70k", "Personal and business loans ₹70k, not ₹1.7 lakh", "Bachatt's figure for a first loan; repeats 10% bigger a year repaid, plus top-ups", False),
    ("today's market", "Apply and approval at today's market, no yearly rises", "20% of the users we can reach apply a year (was 27%); 20% of first loans approved (was 25%)", False),
    ("Home", "Home ₹12 lakh and property ₹5 lakh", "market sizes; they were ₹20.6 lakh and ₹14.6 lakh", False),
    ("payout", "Lender payout 2% flat", "the market's middle; it was rising 24% by year 5", False),
    ("fade", "Sign-ups who never save fade within ~3 months", "they now count as 1.06 people per saver in value, not 1.72", False),
    ("Recharge", "Recharge, bills, FD and NPS off", "not in the launch app", False),
    ("Debits", "Debits at ₹0 to us", "through BSE StAR MF or the fund house's mandate", True),
    ("Still saving", "Still saving at 12 months: Bachatt's 30–40%", "the median, 35%, with the debt fund's fee and repeat approval at the Monte Carlo median", False)]


def bridge_rows():
    """The bridge with each step's change taken from the ROUNDED values, so the labels add up (FIXES C2)."""
    B = od.BRIDGE
    assert len(B) == len(BRIDGE_ROWS) + 1, "a bridge step without its words"
    v5 = [round(float(v), 2) for v in B["LTV/CAC 5y"]]
    v8 = [round(float(v), 2) for v in B["LTV/CAC 8y"]]
    out = []
    for i, (key, nm, sub, conf) in enumerate(BRIDGE_ROWS, start=1):
        assert key.lower() in str(B["step"].iloc[i]).lower(), (key, B["step"].iloc[i])
        out.append((nm, sub, conf, v5[i - 1], v5[i], v8[i]))
    return v5, v8, out


def bridge_svg(W=1152):
    v5, v8, rows = bridge_rows()
    x0, x1_, top, rh = 500, 900, 2.0, 35
    X_ = lambda v: x0 + (x1_ - x0) * float(v) / top
    cc, c5, c8 = 980, 1070, W
    out = [T(0, 14, "EACH DECISION, ONE AT A TIME", 11, 700, SLATE, ls=1), T(x0, 14, "LTV/CAC, 5 YEARS", 11, 700, SLATE, ls=1),
           T(cc, 14, "CHANGE", 11, 700, SLATE, "end", ls=1), T(c5, 14, "5 YEARS", 11, 700, SLATE, "end", ls=1), T(c8, 14, "8 YEARS", 11, 700, SLATE, "end", ls=1)]
    n = len(rows) + 2
    out.append(f'<line x1="{X_(1):.1f}" y1="22" x2="{X_(1):.1f}" y2="{24 + n * rh}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    y = 24
    out.append(T(0, y + 22, "23 October main case", 14, 800, SLATE) + R(x0, y + 7, X_(v5[0]) - x0, 20, od.MID, r=4)
               + T(c5, y + 22, x(v5[0]), 15, 800, SLATE, "end") + T(c8, y + 22, x(v8[0]), 13, 700, SLATE, "end"))
    y += rh
    for nm, sub, conf, a_, b_, b8 in rows:
        d = b_ - a_
        col = TEAL if d > 0 else LATE
        out.append(T(0, y + 15, nm, 12.5, 700, INK) + T(0, y + 29, sub, 10.5, 500, SLATE))
        if conf:
            w = 7.2 * len(nm) + 14
            out.append(R(w, y + 3, 84, 16, sp.AMBER_L, r=8) + T(w + 42, y + 15, "to confirm", 10.5, 800, AMBER, "middle"))
        lo_, hi_ = sorted((a_, b_))
        out.append(R(X_(lo_), y + 7, max(X_(hi_) - X_(lo_), 2), 20, col, r=4))
        out.append(f'<line x1="{X_(a_):.1f}" y1="{y - 8}" x2="{X_(a_):.1f}" y2="{y + 7}" stroke="{MUTE}" stroke-dasharray="2 2"/>')
        out.append(T(cc, y + 22, f"{'+' if d > 0 else '−'}{abs(d):.2f}", 13.5, 800, col, "end"))
        out.append(T(c5, y + 22, x(b_), 13.5, 700, INK, "end") + T(c8, y + 22, x(b8), 12.5, 600, SLATE, "end"))
        y += rh
    out.append(R(-6, y, W + 12, rh - 2, sp.NAVY_L, r=8))
    out.append(T(0, y + 22, "Today's main case (24 October)", 14, 800, NAVY) + R(x0, y + 7, X_(v5[-1]) - x0, 20, NAVY, r=4)
               + T(c5, y + 22, x(v5[-1]), 15, 800, NAVY, "end") + T(c8, y + 22, x(v8[-1]), 13, 700, NAVY, "end"))
    y += rh
    out.append(T(X_(1), y + 14, "1×", 12, 800, RED, "middle"))
    for v in (0.5, 1.5):
        out.append(T(X_(v), y + 14, f"{v:g}×", 11, 600, MUTE, "middle"))
    return svg(W, y + 20, "".join(out))


def p_bridge(n):
    v5, _v8, rows = bridge_rows()
    big = -sum(b - a for nm, _s, _c, a, b, _b8 in rows if nm.startswith(("Personal", "Apply")))
    deb = next(b - a for nm, _s, _c, a, b, _b8 in rows if nm.startswith("Debits"))
    take = (f'<div style="margin-top:8px;font-size:13.5px;line-height:1.45;border-left:5px solid {TEAL};background:{sp.TEAL_L};border-radius:10px;'
            f'padding:8px 14px"><b style="color:{NAVY}">The ₹70k loan and market apply and approval rates took {big:.2f}×;</b> moving debits to ₹0 '
            f"won back {deb:.2f}×, and that one is still to be confirmed in writing.</div>")
    return page(n, "What changed", "THE BRIDGE", f"From the 23 October {x(v5[0])} to {x(v5[-1])} today", bridge_svg() + take,
                "Each row applies one decision on top of the rows above it, so the order changes the size of a step but not where it ends. Changes are "
                "between the rounded values, so they add up. One online saver; cost to win ₹495 throughout; undiscounted.")


# ---------------------------------------------------------------------------------------------------------- appendix: the inputs
TAG = {"market": ("market", NAVY3, sp.BLUE_L), "bachatt": ("Bachatt", TEAL, sp.TEAL_L), "founders": ("founders' figure", NAVY3, sp.BLUE_L),
       "drawn": ("uncertain", AMBER, sp.AMBER_L), "confirm": ("to confirm", LATE, "#f8ebe6"),
       "off": ("off for now", SLATE, sp.BG), "floor": ("our floor", NAVY3, sp.BLUE_L)}


def input_cards():
    """(what, value, where it comes from, tag): the short words for each card; the values are the model's own."""
    X = od.X
    k = lo.drawn(lo.at(od.T_MAIN))
    return [("Saved a day", f"₹{X['daily']:.0f}", "our product's floor; Bachatt's average is unknown, and its own minimums are lower (₹51/₹101 a day)", "floor"),
            ("Still saving at 12 months", "30–40%", f"Bachatt's own range (main case {k['r12']:.0%}); the drop-off after a year moves with it, 2.5% to 1.5% a month",
             "drawn"),
            ("Equity fund fee to us", pct(op.EQ_TRAIL, 2), "a year of the balance, on active equity funds", "confirm"),
            ("Debt fund fee to us", "0.10–0.35%", f"a liquid to a short-duration fund (main case {pct(od.DEBT_MAIN, 2)}); {od.val('blend')} blended", "drawn"),
            ("Cost of a daily debit", f"₹{op.DEBIT_COST:.0f}", "BSE's exchange SIP is free to distributors; fund houses pay BSE", "confirm"),
            ("First personal or business loan", od.lakh(X["ticket"]), "Bachatt's number (our research: ₹15k–58.5k); repeats 10% bigger a year, "
                                                                     "plus top-ups", "bachatt"),
            ("Apply for a loan, a year", pct(op.LOAN_APPLY), "of the users we can reach", "market"),
            ("First loans approved", pct(X["approved_first"]), f"between 11% (an app lender's new applicants) and 25% (our past data); gold "
                                                               f"{pct(op.GOLD_APPROVAL)}, home and property {pct(X['loan_home_approval'])}", "market"),
            ("Yearly rises in take-up, approval", "none", "no source found for any rise", "market"),
            ("Home / property loan size", f"₹{X['loan_home_ticket'] / 1e5:g} / ₹{X['loan_lap_ticket'] / 1e5:g} lakh",
             "affordable home loans ₹6–15 lakh; small property loans ~₹3.9 lakh", "market"),
            ("Lender payout, personal or business", f"{pct(X['fee'])} flat", "the middle of the market's 1–3%", "market"),
            ("People reached per saver (value)", f"{op.LOAN_REACH:.2f}", "about 2.5 KYC'd people come with each saver, but non-savers fade within ~3 months",
             "market"),
            ("Recharge, bills, FD, NPS", "off", "not in the launch app; upside once built", "off"),
            ("Cost to win a saver", rs(CAC), f"₹{op.CAC:.0f} at scale + our 10% contingency; the seed budgets ₹{op.SEED_CAC:.0f} and measures it", "founders")]


def p_inputs(n):
    cards = []
    for lab, v, src, tag in input_cards():
        word, ink, bg = TAG[tag]
        cards.append(f'<div style="background:#fff;border:1px solid {LINE};border-top:4px solid {ink};border-radius:10px;padding:7px 11px 8px">'
                     f'<div style="font-size:11.5px;font-weight:700;color:{SLATE};line-height:1.2;white-space:nowrap;overflow:hidden">{lab}</div>'
                     f'<div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin:1px 0 2px">'
                     f'<span style="font-size:21px;font-weight:800;color:{NAVY};letter-spacing:-.01em;white-space:nowrap">{v}</span>'
                     f'<span style="font-size:9.5px;font-weight:800;color:{ink};background:{bg};border-radius:9px;padding:2px 7px;white-space:nowrap">{word}</span></div>'
                     f'<div style="font-size:10.5px;line-height:1.32;color:{INK}">{src}</div></div>')
    body = f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:9px">{"".join(cards)}</div>'
    X = od.X
    title = "The inputs: two are still uncertain and two still to be confirmed in writing; the founders fixed the rest"
    return page(n, "Appendix", "A1 · EVERY INPUT AND ITS SOURCE", title, body,
                f"Also fixed: fund mix 80% equity, 20% debt; {X['r3']:.0%} still saving at month 3; {pct(X['approved_repeat'])} of repeat loans approved; "
                f"loans over {X['tenure']:.0f} months; top-ups {pct(X['topup_share'])} a year at {pct(X['topup_size'])} of the loan. Small loans outside the "
                f"apply funnel: durables ({od.lakh(X['loan_cd_ticket'])}) and two-wheelers. Not counted: loans against savings (10% of applications), "
                f"insurance (a fixed referral fee, to be agreed). {od.GLOSS['sip']}; {od.GLOSS['mandate']}.")


# ---------------------------------------------------------------------------------------------------------- the shared pages
def p_odds(n):
    return page(n, "What's uncertain", *od.p_odds())


def p_levers(n):
    return page(n, "What it takes", *od.p_upside_levers())


def p_ladder(n):
    return page(n, "What it takes", *od.p_ladder())


def p_facts(n):
    return page(n, "What to find out", *od.p_prove())


def p_company(n):
    k, t, b, s = od.p_company()
    return page(n, "Appendix", "A2 · " + k, t, b, s)


STALE = ("0.78×", "1.37×", "month 73", "₹126", "2.87×", "$5.0M", "month 67", "3× is out of reach", "measured", "7.7×", "₹3 lakh", "35% apply",
         "2.5 KYC'd", "month 63", "$4.7M", "₹2 a debit", "our targets", "at our target", "so the main case is cautious", "a floor")
NUMERIC = ("0.78×", "1.37×", "month 73", "2.87×", "month 67")   # the bridge's steps pass through these legitimately: checked off the bridge
STALE_OK = {"0.78×": ("debt fund's fee moves",), "2.5 KYC'd": ("about 2.5 KYC'd",)}   # the debt fee's high end; FIXES B12's own words


def check(pages):
    for pg in pages:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", pg))
        bridge = "THE BRIDGE" in text
        for bad in ("Bueno", "BetterPlace", ".py", ".csv", "tables/", "nobody serves both", "clawback") + STALE:
            if bridge and bad in NUMERIC:
                continue
            for m in re.finditer(re.escape(bad), text, re.I):
                ctx = text[max(0, m.start() - 220):m.end() + 20]
                assert any(ok in ctx for ok in STALE_OK.get(bad, ())), (bad, ctx)
        assert not re.search(r"\b(DSA|MDR|TER|NPV)\b", text), "unexplained jargon"
        assert not re.search(r"\b(he|his|him|she|her|hers)\b", text, re.I), "gendered word"


def build():
    main = [p_value, p_bridge, p_odds, p_levers, p_ladder, p_facts]
    appx = [p_inputs, p_company]
    n = len(main) + len(appx) + 1
    pages = [cover(n)] + [f(i) for i, f in enumerate(main + appx, start=2)]
    css = sp.CSS + (".at.compact td { padding: 4px 8px; } .at.compact th { padding: 4px 8px; }"
                    ".chips3 { margin-top: 10px !important; gap: 14px; } .chip { font-size: 12.5px; padding: 10px 14px; line-height: 1.4; } .chip b { font-size: 13.5px; }"
                    ".at.fin td { padding: 2.5px 8px; } .at.fin th { padding: 3px 8px; }")
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>What one saver is worth</title><style>{css}</style></head><body>{"".join(pages)}</body></html>'
    html = re.sub(r"\bRs\.?\s?(?=\d)", "₹", html)
    check(re.findall(r"<section.*?</section>", html, re.S))
    out = HERE / "LTV_CAC_simple.html"
    out.write_text(html)
    pdf = HERE / "LTV_CAC_simple.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf, len(pages), "pages")


if __name__ == "__main__":
    build()

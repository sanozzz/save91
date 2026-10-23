"""The short LTV/CAC deck: one point a page, how each assumption moves the number (founders 23 Oct: "easy to understand ... keep things pointed").
Every number is worked out from model/online_plan.py and the detailed deck's helpers (build_ltv_deck.py); market values are the middle of the
evidence in reviews/2026-10-23_ltv_cac_check (evidence.md). Writes ltv/LTV_CAC_simple.html and .pdf.
Usage (from others/): PYTHONPATH=model python ltv/build_ltv_simple.py"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_ltv_deck as ld  # noqa: E402  (page frame, colours, the plan's numbers, the fee test and the fragility chart)

op, sp = ld.op, ld.sp
ON, X, P, REACH = ld.ON, ld.X, ld.P, ld.REACH
T, R, svg, page, chips, two, table = ld.T, ld.R, ld.svg, ld.page, ld.chips, ld.two, ld.table
INK, NAVY, TEAL, AMBER, SLATE, LINE, LATE = ld.INK, ld.NAVY, ld.TEAL, ld.AMBER, ld.SLATE, ld.LINE, ld.LATE
rs, x, pct, short_rs = ld.rs, ld.x, ld.pct, ld.short_rs
CAC = -ON["cac"]                                               # ₹495: the ₹450 input plus the 10% contingency


def ltvx(ov=None, cac=None, reach=None, ramp=True):
    """Online LTV/CAC over five years with some plan inputs changed; ramp=False holds the lender payout at its starting rate."""
    op.OV.clear()
    op.OV.update(ov or {})
    op._CACHE.clear()
    try:
        d = op.ltv_parts(op.saver_inputs(), reach)
        t = np.arange(1, op.M + 1)
        held = 0.0 if ramp else d["personal and business loans"] * (1 / (1.0 + 0.5 * np.minimum(t - 1, 59) / 59) - 1)
        ltv = float((d["income"] + held - d["serving"])[:60].sum())
        return ltv / ((op.CAC if cac is None else cac) * (1 + op.CONTINGENCY))
    finally:
        op.OV.clear()
        op._CACHE.clear()


assert abs(ltvx() - ON["ltvcac"]) < 0.01, (ltvx(), ON["ltvcac"])   # the same engine as the plan

# One assumption at a time: (name, ours, today's market, overrides, cac, reach, ramp, inside the evidence?, short source)
ONE = [("Average personal or business loan", short_rs(X["ticket"], "rs"), "₹50,000", {"ticket": 50000.0}, None, None, True, False,
        "first loans ₹5,000–25,000; digital lenders ₹15,000–1.2 lakh (bureau, FACE)"),
       ("Share of reachable users who apply, a year", pct(op.LOAN_APPLY), "20%", op.loan_mix(0.20), None, None, True, False,
        "1–5% of app users borrow a year (Paytm, Kissht, PhonePe filings)"),
       ("Cost to win a saver", rs(op.CAC), "₹750", {}, 750.0, None, True, False, "₹800–1,400 per new investor at the largest investing app"),
       ("Loan offers to KYC'd users who never save", f"{REACH - 1:.1f} per saver", "savers only (not measured)", {}, None, 1.0, True, False, "not measured anywhere"),
       ("Still saving after a year, and after", f"{X['r12']:.0%}, then 1.5% stop a month", "35%, then 2.5%", {"r12": 0.35, "churn_late": 0.025},
        None, None, True, True, "24–45% at a year; 1–4% a month after"),
       ("First applications approved", pct(X["approved_first"]), "20%", {"approved_first": 0.20}, None, None, True, False,
        "11% of new applicants at an app lender (prospectus)"),
       ("Yearly rises in take-up and approvals", "+5% and +10% a year", "no rise (no source)", ld.FLAT, None, None, True, False, "no source found"),
       ("Home and property loan size", f"{short_rs(X['loan_home_ticket'], 'rs')} / {short_rs(X['loan_lap_ticket'], 'rs')}", "₹12 lakh / ₹5 lakh",
        {"loan_home_ticket": 1.2e6, "loan_lap_ticket": 5e5}, None, None, True, False, "mass-market lenders ₹10–15 lakh / ₹3–10 lakh"),
       ("Lender payout on personal and business loans", f"{pct(X['fee'])} rising to {pct(X['fee'] * 1.5)}", f"{pct(X['fee'])}, flat", {}, None, None,
        False, False, "rate cards 1–2.5%, flat"),
       ("Fund trail (our share of fund fees)", pct(X["trail"], 2), "0.62%", {"trail": 0.0062}, None, None, True, True,
        "0.50–0.88% equity, 0.08–0.50% debt"),
       ("Repeat applications approved", pct(X["approved_repeat"]), "74%", {"approved_repeat": 0.735}, None, None, True, True,
        "74% of repeat customers at an app lender")]
ONE = [(*r[:3], ltvx(r[3], r[4], r[5], r[6]), *r[7:]) for r in ONE]           # -> (name, ours, market, LTV/CAC, inside, source)
ONE.sort(key=lambda r: r[3])


def cover():
    m_fee, m_x = ld.market()
    tiles = [(rs(CAC), "to win one online saver<br>(₹450 + our 10% contingency)"), (rs(ON["ltv"]), "back over five years,<br>after the cost of serving them"),
             (x(ON["ltvcac"]), f"LTV/CAC, paid back in month {ON['pay']},<br><b>if our loan targets hold</b>")]
    t = "".join(f'<div class="ctile"><div class="cbig" style="font-size:40px">{a}</div><div class="csub" style="font-size:14px">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:50px">What one saver is worth</div>
  <div class="ctag">LTV/CAC in eight pages: how one saver makes money, and how each assumption changes the number.</div>
  <div class="cmeta">October 2026 · Confidential</div>
</div>
<div class="cright"><div class="cgrid" style="grid-template-columns:1fr">{t}</div>
<div class="cnote" style="margin-top:18px;font-size:14px;line-height:1.45">Loans are {(ON['pb'] + ON['ol']) / ON['rev']:.0%} of the money. At today's market
rates for app users the same saver returns {x(m_x)}. The seed's first job is to find out which world we are in.</div></div>
</section>"""


def waterfall_svg(W=1100, H=360):
    steps = [("Cost to win", -CAC, LATE), ("Fund fees", ON["fund"], NAVY), ("Personal and business loans", ON["pb"], ld.NAVY3),
             ("Other lenders' loans", ON["ol"], ld.NAVY4), ("Cards and everyday products", ON["cards"] + ON["oth"] + ON["ins"], "#7cc4b8"),
             ("Serving them", ON["serve"], LATE)]
    lo, hi = -700.0, 4200.0
    top, bot = 30, H - 70
    Y = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    n = len(steps) + 1
    bw, gap = 112, (W - 40 - (len(steps) + 1) * 112) / len(steps)
    out = [f'<line x1="20" y1="{Y(0):.1f}" x2="{W - 10}" y2="{Y(0):.1f}" stroke="{SLATE}" stroke-width="1"/>']
    run = 0.0
    for i, (lab, v, col) in enumerate(steps):
        x0 = 20 + i * (bw + gap)
        a, b = run, run + v
        out.append(R(x0, Y(max(a, b)), bw, max(abs(Y(a) - Y(b)), 2), col, r=4))
        out.append(T(x0 + bw / 2, Y(max(a, b)) - 8, ("+" if v > 0 else "−") + rs(abs(v)), 15, 800, NAVY if v > 0 else LATE, "middle"))
        for k, w in enumerate(lab.split(" and ") if len(lab) > 16 else [lab]):
            out.append(T(x0 + bw / 2, bot + 22 + 15 * k, (w if k == 0 else "and " + w), 12, 600, INK, "middle"))
        if i < len(steps) - 1:
            out.append(f'<line x1="{x0 + bw}" y1="{Y(b):.1f}" x2="{x0 + bw + gap}" y2="{Y(b):.1f}" stroke="{SLATE}" stroke-dasharray="3 3"/>')
        run = b
    x0 = 20 + len(steps) * (bw + gap)
    out.append(R(x0, Y(run), bw, Y(0) - Y(run), NAVY, r=4))
    out.append(T(x0 + bw / 2, Y(run) - 8, rs(run), 15, 800, NAVY, "middle"))
    out.append(T(x0 + bw / 2, bot + 22, "Net, 5 years", 12, 700, INK, "middle"))
    return svg(W, H, "".join(out))


def p_money(n):
    body = waterfall_svg() + chips([
        ("Loans make the money", f"Lenders pay us a referral fee on every loan we bring: {rs(ON['pb'] + ON['ol'])} of the {rs(ON['rev'])} a saver brings in five years."),
        ("Saving pays its own way, just", f"Fund fees ({rs(ON['fund'])}) about cover the cost of serving a saver ({rs(-ON['serve'])}): support, tech and payments."),
        (f"{x(ON['ltvcac'])}", f"{rs(ON['ltv'])} back (revenue less serving) on {rs(CAC)} to win, paid back in month {ON['pay']}.")])
    return page(n, "The answer", "HOW ONE SAVER MAKES MONEY",
                f"One online saver: {rs(CAC)} to win, {rs(ON['ltv'])} back in five years: {x(ON['ltvcac'])}", body,
                "One online saver won, months 1–60, undiscounted. Net after the cost to win = LTV less the cost to win.")


def funnel_svg(W=1100, H=210):
    first = float(P["loans_first"][0][:60].sum() * REACH * 100)
    rep = float(P["loans_repeat"][0][:60].sum() * REACH * 100)
    top_ = float(P["topups"][0][:60].sum() * REACH * 100)
    lent = float(P["money_lent"][0][:60].sum() * REACH * 100)
    boxes = [("100", "savers won"), (f"{REACH * 100:.0f}", "KYC'd users see loan offers (5 sign-ups a saver, half finish KYC)"),
             (pct(op.LOAN_APPLY), "of them apply for a loan each year"), (pct(X["approved_first"]), "of first applications approved"),
             (f"{first + rep + top_:.0f} loans", f"in five years, ₹{lent / (first + rep + top_) / 1e5:.1f} lakh on average: ₹{lent / 1e5:,.0f} lakh lent"),
             (rs(ON["pb"]), f"in fees per saver won (about {ON['pb'] / lent * 100:.1%} of each loan)")]
    bw, gap = 158, (W - 6 * 158) / 5
    out = []
    for i, (big, small) in enumerate(boxes):
        x0 = i * (bw + gap)
        fill = NAVY if i == len(boxes) - 1 else sp.NAVY_L
        ink = "white" if i == len(boxes) - 1 else NAVY
        out.append(R(x0, 10, bw, 150, fill, r=12))
        out.append(T(x0 + 14, 52, big, 26, 800, ink))
        words, line, lines = small.split(), "", []
        for w in words:
            if len(line + " " + w) > 22:
                lines.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        lines.append(line)
        for k, l_ in enumerate(lines[:5]):
            out.append(T(x0 + 14, 78 + 16 * k, l_, 12, 500, "white" if i == len(boxes) - 1 else INK))
        if i < len(boxes) - 1:
            ax = x0 + bw + 4
            out.append(f'<path d="M{ax} 85 L{ax + gap - 8} 85" stroke="{SLATE}" stroke-width="2" marker-end="url(#ar)"/>')
    defs = f'<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{SLATE}"/></marker></defs>'
    return svg(W, H - 40, defs + "".join(out))


def p_loans(n):
    body = funnel_svg() + chips([
        ("The three loan targets", f"{pct(op.LOAN_APPLY)} apply a year, {pct(X['approved_first'])} approved, {short_rs(X['ticket'], 'rs')} loans. Together they make "
                                   f"{rs(ON['pb'])} of the {rs(ON['ltv'])}."),
        ("Other lenders' loans", f"Gold, property and home loans referred to other lenders add {rs(ON['ol'])}, most of it from a few large property and home loans."),
        ("Who pays", "The lender, once, when the loan is paid out; part comes back if a loan closes or goes bad within six months. We never lend our own money.")])
    return page(n, "The answer", "WHERE THE LOAN MONEY COMES FROM",
                f"100 savers won bring {REACH * 100:.0f} people who can see loan offers; {sum(float(P[k][0][:60].sum()) for k in ('loans_first', 'loans_repeat', 'topups')) * REACH * 100:.0f} "
                f"loans later, that is {rs(ON['pb'])} a saver", body,
                "Per 100 online savers won, first five years. Offers reach users while the saver who brought them keeps saving.")


def one_svg(W=1100):
    top = 8.0
    L, Bw, rh = 470, 470, 26
    out, y = [], 20
    x_ = lambda v: L + Bw * min(v, top) / top
    out.append(T(L, 12, "0×", 11, 600, SLATE, "middle"))
    for v in (3, 6):
        out.append(T(x_(v), 12, f"{v}×", 11, 600, SLATE, "middle"))
    for name, ours, mkt, v, inside, _src in ONE:
        out.append(T(0, y + 13, name, 12.5, 700, NAVY))
        out.append(T(0, y + 26, f"{ours}  →  {mkt}", 10.5, 500, SLATE))
        out.append(R(L, y + 4, Bw * ON["ltvcac"] / top, 18, "#e2e8f0", r=4))
        col = TEAL if inside else (LATE if v < 3 else AMBER)
        out.append(R(L, y + 4, max(Bw * min(v, top) / top, 3), 18, col, r=4))
        out.append(T(x_(v) + 6, y + 18, f"{v:.1f}×", 12.5, 800, col))
        y += rh + 6
    out.append(f'<line x1="{x_(ON["ltvcac"]):.1f}" y1="16" x2="{x_(ON["ltvcac"]):.1f}" y2="{y}" stroke="{NAVY}" stroke-width="1.5"/>')
    out.append(T(x_(ON["ltvcac"]), y + 14, f"plan {x(ON['ltvcac'])}", 11.5, 700, NAVY, "middle"))
    out.append(f'<line x1="{x_(3):.1f}" y1="16" x2="{x_(3):.1f}" y2="{y}" stroke="{SLATE}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    return svg(W, y + 22, "".join(out))


def p_one(n):
    big = ONE[0]
    legend = (f'<div style="display:flex;gap:18px;font-size:12px;color:{INK};margin:2px 0 4px">'
              f'<span><b style="color:{LATE}">■</b> not proven, below 3×</span><span><b style="color:{AMBER}">■</b> not proven, 3× or more</span>'
              f'<span><b style="color:{TEAL}">■</b> our number is inside the evidence</span><span style="color:{SLATE}">each row: ours → today\'s market; grey: the plan, {x(ON["ltvcac"])}</span></div>')
    return page(n, "Each assumption", "ONE AT A TIME",
                f"Change one assumption to today's market value and see the number: {big[0].lower()} moves it most, to {x(big[3])}",
                legend + one_svg(),
                "Each bar: online LTV/CAC over five years with that one assumption at the market value and everything else as planned. Market values: the middle "
                "of the 2024–26 evidence; sources on the last page.")


def p_together(n):
    chart, worst_one, _ = ld.fragile_svg()
    right = (f'<div style="font-size:15px;line-height:1.5;color:{INK}"><p style="margin:0 0 12px"><b style="color:{NAVY}">One miss is survivable.</b> '
             f"Any single target can fall to the market and the saver still returns {worst_one:.1f}× or more.</p>"
             f'<p style="margin:0 0 12px"><b style="color:{LATE}">Two misses are not.</b> The targets are linked: smaller savers borrow smaller loans, less often. '
             "When two fall together the answer drops below 3×.</p>"
             f'<p style="margin:0"><b style="color:{NAVY}">So it is one bet:</b> our savers earn more and want credit, and their saving record makes lenders say yes '
             "more often and lend more. If it holds, the targets hold together.</p></div>")
    left = (f'<div style="font-size:11.5px;font-weight:700;letter-spacing:1.1px;color:{SLATE}">ONLINE LTV/CAC, 5 YEARS</div>' + chart)
    return page(n, "Several at once", "WHEN TARGETS MISS TOGETHER",
                f"One target can miss and it stays at {worst_one:.1f}× or more; two together take it below 3×", two(left, right, 600),
                "One target misses: only that input changes. Two or three miss: the inputs named change together. Today's market rates: every input at "
                "the middle of the evidence.")


def p_fee(n):
    title, body, src = ld.fee_test()
    return page(n, "The one number", "WHAT LENDERS MUST PAY US", title, body, src)


PASS = [("A lender's pre-screen", "A lending partner soft-checks the credit of our first 1,000 KYC'd sign-ups.",
         f"approval near {pct(X['approved_first'])}, eligible loans near {short_rs(X['ticket'], 'rs')}"),
        ("Terms in writing", "The payout, clawbacks and approval rules for savers with 3–6 months of saving, signed.", f"a payout of {pct(X['fee'])} or more after clawbacks"),
        ("Who signs up", "The income of the first sign-ups; it sets the loan size more than anything we assume.",
         f"income of ₹{ld.emi(X['ticket'], 0.24, X['tenure']) / 0.5 / 1e3:.0f}k+ a month for {short_rs(X['ticket'], 'rs')} loans"),
        ("Opt-in and apply", "How many KYC'd users ask to see lender offers, and how many apply in 3 months.", f"{pct(op.LOAN_APPLY)} or more opting in"),
        ("The real cost to win", "What the pilot pays per saver who makes a first debit.", f"{rs(op.SEED_CAC)} or less in the seed, {rs(op.CAC)} after")]


def p_seed(n):
    cards = "".join(
        f'<div style="flex:1;background:{sp.NAVY_L};border-radius:12px;padding:14px 14px 12px">'
        f'<div style="width:34px;height:34px;border-radius:17px;background:{NAVY};color:white;font-weight:800;font-size:16px;display:flex;'
        f'align-items:center;justify-content:center;margin-bottom:10px">{i}</div>'
        f'<div style="font-size:14.5px;font-weight:800;color:{NAVY};margin-bottom:6px">{a}</div>'
        f'<div style="font-size:12.5px;line-height:1.4;color:{INK};min-height:70px">{b}</div>'
        f'<div style="font-size:12px;line-height:1.35;color:{TEAL};font-weight:700;border-top:1px solid {LINE};padding-top:8px">Pass: {c}</div></div>'
        for i, (a, b, c) in enumerate(PASS, start=1))
    body = (f'<div style="display:flex;gap:12px">{cards}</div>'
            f'<div style="margin-top:16px;font-size:14px;line-height:1.5;color:{INK};border-left:5px solid {TEAL};background:{sp.TEAL_L};'
            f'border-radius:10px;padding:10px 16px"><b style="color:{NAVY}">Checks 1 and 2 need no money lent and take weeks.</b> If they pass, '
            f"{x(ON['ltvcac'])} has evidence behind it. If they come back at market levels, we know before the money goes into scale, and we change the "
            "plan: bigger savers, a cheaper way to win them, or more per loan.</div>")
    return page(n, "What the seed proves", "FIVE CHECKS", "Five checks tell us whether the bet holds, most of them before we lend a rupee", body,
                "Pass marks are the plan's own targets. A soft credit check reads a bureau file without touching the person's score.")


def p_table(n):
    rows = [[f"<b>{nm}</b>", ours, mkt, f"<b>{v:.1f}×</b>", "yes" if inside else "no", src] for nm, ours, mkt, v, inside, src in ONE]
    tb = table(["Assumption", "Ours", "Today's market", "LTV/CAC at market", "Inside the evidence?", "Where the market figure comes from"], rows,
               [24, 15, 13, 11, 10, 27], 11.5, compact=True)
    return page(n, "Appendix", "EVERY ASSUMPTION ON ONE PAGE", f"Our numbers against today's market, and what each does to the {x(ON['ltvcac'])}", tb,
                "Market figures: Indian sources 2024–26 (company filings and prospectuses, bureau and FACE reports, DSA rate cards, AMFI). The live workbook "
                "lets any assumption be changed and the answer recalculates.")


def build():
    pages = [cover()] + [f(i) for i, f in enumerate([p_money, p_loans, p_one, p_together, p_fee, p_seed, p_table], start=2)]
    css = sp.CSS + (".at.compact td { padding: 4px 8px; } .at.compact th { padding: 4px 8px; }"
                    ".chips3 { margin-top: 10px !important; gap: 14px; } .chip { font-size: 12.5px; padding: 10px 14px; line-height: 1.4; } .chip b { font-size: 13.5px; }")
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>LTV/CAC in eight pages</title><style>{css}</style></head><body>{"".join(pages)}</body></html>'
    html = ld.deck_words(html)
    text = re.sub(r"<[^>]+>", " ", html)
    for bad in ("Bueno", "BetterPlace", "Bachatt", ".py", ".csv", "tables/"):
        assert bad.lower() not in text.lower(), bad
    assert not re.search(r"\b(he|his|him|she|her)\b", text), "gendered word"
    out = HERE / "LTV_CAC_simple.html"
    out.write_text(html)
    pdf = HERE / "LTV_CAC_simple.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf, len(pages), "pages")


if __name__ == "__main__":
    build()

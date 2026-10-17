"""The QR-moat test as a PDF (operator, 12 Oct 2026: "CaN WE CREATE pdf (not artifact) that is actually
the case?"). It TESTS the premise; it is not written to prove it.

Quotes only tables/qr_moat_numbers.csv (model/qr_moat.py) and research/qr_moat.csv (evidence), and
recomputes nothing. Writes brief/qr_moat/qr_moat.html, then prints it to QR_moat_test.pdf with Chrome.
"""
import csv
import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = {r["key"]: float(r["value"]) for r in csv.DictReader((ROOT / "tables" / "qr_moat_numbers.csv").open())}
EV = list(csv.DictReader((ROOT / "research" / "qr_moat.csv").open()))
OUT_DIR = ROOT / "brief" / "qr_moat"
PDF = ROOT / "QR_moat_test.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

INK, MUTED, RULE = "#1f2328", "#59636e", "#e3ded4"
BROWN, GREY = "#8A3B08", "#B9AE9B"


def n(k):
    return NUM[k]


def pct(k, d=0):
    return f"{n(k) * 100:.{d}f}%"


def rs(x):
    return f"₹{x:,.0f}"


def bars(vals, labels, texts, colours, w=200, h=150, top=22, bottom=34):
    """Vertical bars anchored at the baseline, 4px rounded data-ends, every bar labelled."""
    k = len(vals)
    gap = 10
    bw = (w - gap * (k + 1)) / k
    vmax = max(vals)
    plot = h - top - bottom
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">',
           f'<line x1="0" y1="{h - bottom}" x2="{w}" y2="{h - bottom}" stroke="{RULE}" stroke-width="1"/>']
    for i, (v, lab, t, c) in enumerate(zip(vals, labels, texts, colours)):
        bh = max(plot * v / vmax, 2)
        x = gap + i * (bw + gap)
        y = h - bottom - bh
        r = min(4, bw / 2, bh)
        out.append(f'<path d="M{x},{h - bottom} V{y + r} Q{x},{y} {x + r},{y} H{x + bw - r} Q{x + bw},{y} {x + bw},{y + r} V{h - bottom} Z" fill="{c}"/>')
        out.append(f'<text x="{x + bw / 2}" y="{y - 6}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK}">{t}</text>')
        for j, part in enumerate(lab.split("|")):
            out.append(f'<text x="{x + bw / 2}" y="{h - bottom + 14 + j * 12}" text-anchor="middle" font-size="10" fill="{MUTED}">{part}</text>')
    out.append("</svg>")
    return "".join(out)


def loss_line():
    """Where losses must land: a 0-10% line with the till-holders' band, our two lines and the no-till band."""
    w, h, x0, x1 = 660, 150, 30, 630
    X = lambda p: x0 + (x1 - x0) * p / 0.10
    lo, hi = n("paytm_ecl_low"), n("paytm_ecl_high")
    dlo, dhi = n("digital_losses_low"), n("digital_losses_high")
    today, be = n("losses_today"), n("be_losses")
    s = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img">',
         f'<line x1="{x0}" y1="70" x2="{x1}" y2="70" stroke="{MUTED}" stroke-width="1"/>']
    s.append(f'<rect x="{X(lo)}" y="58" width="{X(hi) - X(lo)}" height="24" rx="4" fill="#2f6b4f" opacity="0.85"/>')
    s.append(f'<text x="{(X(lo) + X(hi)) / 2}" y="46" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">Paytm-sourced shop loans</text>')
    s.append(f'<text x="{(X(lo) + X(hi)) / 2}" y="32" text-anchor="middle" font-size="10" fill="{MUTED}">repaid from the till: {lo * 100:.1f}–{hi * 100:.1f}%</text>')
    s.append(f'<rect x="{X(dlo)}" y="58" width="{X(dhi) - X(dlo)}" height="24" rx="4" fill="{GREY}" opacity="0.9"/>')
    s.append(f'<text x="{(X(dlo) + X(dhi)) / 2}" y="46" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">Digital lenders, no till</text>')
    s.append(f'<text x="{(X(dlo) + X(dhi)) / 2}" y="32" text-anchor="middle" font-size="10" fill="{MUTED}">{dlo * 100:.0f}–{dhi * 100:.0f}% a year</text>')
    for p in range(0, 11, 1):
        s.append(f'<line x1="{X(p / 100)}" y1="66" x2="{X(p / 100)}" y2="74" stroke="{MUTED}" stroke-width="1"/>')
        s.append(f'<text x="{X(p / 100)}" y="98" text-anchor="middle" font-size="10" fill="{MUTED}">{p}%</text>')
    for p, lab, sub, yy, side in ((today, "Our model today", f"{today * 100:.0f}%", 124, "end"), (be, "Our break-even", f"{be * 100:.1f}%", 142, "start")):
        tx = X(p) - 6 if side == "end" else X(p) + 6
        s.append(f'<line x1="{X(p)}" y1="54" x2="{X(p)}" y2="86" stroke="{BROWN}" stroke-width="2"/>')
        s.append(f'<line x1="{X(p)}" y1="104" x2="{X(p)}" y2="{yy + 4}" stroke="{BROWN}" stroke-width="2"/>')
        s.append(f'<circle cx="{X(p)}" cy="70" r="5" fill="{BROWN}" stroke="#fff" stroke-width="2"/>')
        s.append(f'<text x="{tx}" y="{yy}" text-anchor="{side}" font-size="11" fill="{INK}"><tspan font-weight="600">{lab}</tspan> {sub}</text>')
    s.append("</svg>")
    return "".join(s)


def lane(y, title, boxes, verdict, colour):
    s = [f'<text x="0" y="{y - 14}" font-size="13" font-weight="700" fill="{INK}">{title}</text>']
    bw, gap, bh = 150, 26, 74
    for i, (head, body, hl) in enumerate(boxes):
        x = i * (bw + gap)
        fill = "#f6efe7" if hl else "#f7f6f3"
        stroke = colour if hl else RULE
        s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="{2 if hl else 1}"/>')
        s.append(f'<text x="{x + 10}" y="{y + 20}" font-size="11.5" font-weight="700" fill="{INK}">{head}</text>')
        for j, line in enumerate(body.split("|")):
            s.append(f'<text x="{x + 10}" y="{y + 38 + j * 14}" font-size="10.5" fill="{MUTED}">{line}</text>')
        if i < len(boxes) - 1:
            ax = x + bw + 3
            s.append(f'<path d="M{ax},{y + bh / 2} h{gap - 10}" stroke="{MUTED}" stroke-width="1.5"/>')
            s.append(f'<path d="M{ax + gap - 10},{y + bh / 2 - 4} l6,4 l-6,4 z" fill="{MUTED}"/>')
    s.append(f'<text x="0" y="{y + bh + 22}" font-size="11.5" font-weight="600" fill="{colour}">{verdict}</text>')
    return "".join(s)


def who_gets_paid_first():
    a = lane(30, "A Paytm or PhonePe shop loan", [
        ("Customer pays", "₹500 at the counter", False),
        ("Their QR", "they see every rupee|paid on it", False),
        ("Instalment taken", "today's loan instalment|is cut first", True),
        ("Shop is paid", "the rest reaches|the shop's bank", False)],
        "They are paid BEFORE the shopkeeper.", "#2f6b4f")
    b = lane(190, "Our shop loan", [
        ("Customer pays", "₹500 at the counter", False),
        ("Any QR", "we see none of it", False),
        ("Shop is paid", "all of it reaches|the shop's bank", False),
        ("We ask next day", "Autopay asks the bank|for our instalment", True)],
        f"We are paid AFTER the shopkeeper, if money is left. {pct('autopay_fail_low')}–{pct('autopay_fail_high')} of Autopay debits failed at big banks (Aug 2025).", BROWN)
    return f'<svg viewBox="0 0 680 320" width="100%" role="img">{a}{b}</svg>'


def tile(label, chip, kind, proof):
    icon = {"good": "✓", "warn": "!", "bad": "✕"}[kind]
    return f'<div class="tile"><div class="tlabel">{label}</div><div class="chip {kind}"><span>{icon}</span>{chip}</div><p>{proof}</p></div>'


def card(no, title, chip, kind, points):
    icon = {"good": "✓", "warn": "!", "bad": "✕"}[kind]
    li = "".join(f"<li>{p}</li>" for p in points)
    return f'<div class="card"><div class="chead"><span class="no">{no}</span><h3>{title}</h3><span class="chip {kind}"><span>{icon}</span>{chip}</span></div><ul>{li}</ul></div>'


def page():
    paytm_a = bars([n("paytm_share_dec23"), n("paytm_share_dec24")], ["Dec 2023", "Dec 2024"],
                   [f"{n('paytm_share_dec23'):.1f}%", f"{n('paytm_share_dec24'):.1f}%"], [GREY, BROWN])
    paytm_b = bars([n("paytm_dev_dec23"), n("paytm_dev_mar24"), n("paytm_dev_mar26"), n("paytm_dev_jun26")],
                   ["Dec|2023", "Mar|2024", "Mar|2026", "Jun|2026"],
                   [f"{n(k):.2f}" for k in ("paytm_dev_dec23", "paytm_dev_mar24", "paytm_dev_mar26", "paytm_dev_jun26")],
                   [GREY, BROWN, BROWN, BROWN])
    paytm_c = bars([n("paytm_ml_q3fy24"), n("paytm_ml_q4fy24")], ["Oct–Dec|2023", "Jan–Mar|2024"],
                   [rs(n("paytm_ml_q3fy24")), rs(n("paytm_ml_q4fy24"))], [GREY, BROWN])
    phonepe = bars([n("phonepe_ml_fy23"), n("phonepe_ml_fy24"), n("phonepe_ml_fy25"), n("phonepe_ml_h1fy26")],
                   ["FY23", "FY24", "FY25", "Apr–Sep|2025 only"],
                   [rs(n(k)) for k in ("phonepe_ml_fy23", "phonepe_ml_fy24", "phonepe_ml_fy25", "phonepe_ml_h1fy26")],
                   [BROWN, BROWN, BROWN, GREY], w=300, h=150)

    tiles = "".join([
        tile("The QR code", "Easy to copy", "good",
             f"{n('qr_codes_cr'):.1f} crore QR codes for 6.5 crore shops: about {n('qr_per_merchant'):.0f} each. BharatPe signed up 1.3 crore+ shops from nothing after 2018."),
        tile("The soundbox on the counter", "Sticky", "warn",
             f"When Paytm's share of UPI payments halved, shops paying for its devices held through the shock ({n('paytm_dev_dec23'):.2f} → {n('paytm_dev_mar24'):.2f} crore) and are {n('paytm_dev_jun26'):.2f} crore today."),
        tile("Repayment taken from the till", "Hard to beat", "bad",
             f"Paytm-sourced shop loans expect {pct('paytm_ecl_low', 1)}–{pct('paytm_ecl_high', 0)} losses. We break even at {pct('be_losses', 1)}, collecting by Autopay instead."),
        tile("Our savings hook", "Already copied", "bad",
             "PhonePe launched a ₹100-a-day deposit on 6 Aug 2026: the same shape as ours (for consumers, so far)."),
    ])

    layers = "".join([
        card(1, "The QR code", "Easy to copy", "good", [
            "BharatPe launched the first QR any UPI app could pay in 2018. Since then a shop can add one more QR in a minute.",
            f"India has {n('qr_codes_cr'):.1f} crore QR codes for 6.5 crore shops: about {n('qr_per_merchant'):.0f} per shop (counts include inactive ones).",
            "It earns little, so it locks in little: payments up to ₹2,000 stay free even after the 0.4% fee starts on 15 Oct 2026, and small shops are exempt.",
            "BharatPe went from zero to 1.3 crore+ registered shops, and reached break-even in FY25 before employee-stock costs."]),
        card(2, "The soundbox and the people on the ground", "Sticky, but bought", "warn", [
            "Paytm has 1.57 crore shops paying for a device (+27 lakh in a year). PhonePe has 91.9 lakh speakers, 25,657 staff and 31,000+ agents.",
            "Paytm spends up to about ₹5,000 of staff cost per device it adds (our estimate, an upper bound).",
            "Cracks: shops left Paytm's ₹125-a-month box for PhonePe's ₹49 one; some hand the box back once rent starts; NPCI is reported to be building one box that announces payments from any QR (not confirmed)."]),
        card(3, "Seeing the shop's takings", "Strong, but partial", "warn", [
            "Each company sees only what comes through its own QR. PhonePe reportedly lends only to shops taking ₹15,000+ a month on PhonePe QR for 3+ months.",
            f"With about {n('qr_per_merchant'):.0f} QR codes per shop, no one company sees the whole shop.",
            f"Account Aggregator, the RBI's consent system, lets any regulated lender read a shop's whole bank statement. Lending that used it reached ₹{n('aa_lakh_cr'):.2f} lakh crore in FY26 ({pct('aa_share_value', 1)} of retail and small-business lending). It shows every QR's money, if the shopkeeper agrees."]),
        card(4, "Taking repayment from the till", "Hard to beat", "bad", [
            "PhonePe takes a small instalment from the shop's daily payout. A missed one is added to the next day's; long misses are taken from the bank account. Paytm works the same way.",
            f"Result: Paytm-sourced shop loans expect {pct('paytm_ecl_low', 1)}–{pct('paytm_ecl_high', 0)} losses, and more than half the money goes to repeat borrowers.",
            f"Without the till, we would collect by UPI Autopay. In Aug 2025, {pct('autopay_fail_low')}–{pct('autopay_fail_high')} of Autopay debits failed at the big banks, mostly for lack of money."]),
        card(5, "Lending to shops at scale", "Already there", "bad", [
            f"PhonePe's shop loans grew from ₹11 crore (FY23) to {rs(n('phonepe_ml_fy25'))} crore (FY25), and {rs(n('phonepe_ml_h1fy26'))} crore in Apr–Sep 2025 alone, {n('phonepe_ml_h1_x'):.1f}× a year earlier.",
            "BharatPe earns 60% of its revenue from financial services, mostly shop loans of about ₹1 lakh over 11 months. Google Pay lends to shops through partners too.",
            "Paytm and PhonePe do not lend their own money: Paytm will not seek a lending licence, and PhonePe has applied three times since 2021. BharatPe lends 25–30% through its own lending company. The lenders behind them are partners we could also approach."]),
        card(6, "Our savings hook", "Already copied", "bad", [
            "PhonePe Daily Recurring Deposit: ₹100–1,000 a day, withdraw after 7 days, with Shivalik Small Finance Bank (6 Aug 2026, for consumers).",
            "PhonePe has offered daily saving in gold with Jar since 2024. BharatPe sells deposits to 80 lakh+ shops through its investment platform.",
            "A shop version is a small step for any of them. So savings can open the door, but it is not an edge they cannot copy."]),
    ])

    rows = [
        ("Cost to win a shopkeeper", f"at most {rs(n('be_cost'))}", f"today {rs(n('cost_today'))}",
         f"Up to ~₹5,000 of staff cost per device; {n('phonepe_people') // 1000 * 1000:,.0f}+ people on the ground at PhonePe alone.",
         "warn", "Unknown", "A savings-only offer is cheaper to deliver, but these shops are already visited by others. Only a pilot can tell."),
        ("Proven savers who borrow each year", f"at least {pct('be_takeup')}", f"today {pct('takeup_today')}",
         "Their good shops already get loan offers; repeat borrowers take more than half of Paytm's loan money.",
         "bad", "Pushed down", "The shops left for us are the ones they turn down or under-serve."),
        ("Interest rate", f"at least {pct('be_rate', 1)}", f"today {pct('rate_today')}",
         "Quoted shop-loan prices run from about 15% to above 30% a year (low confidence).",
         "good", "Not the problem", f"{pct('rate_today')} sits inside the market."),
        ("Losses", f"at most {pct('be_losses', 1)}", f"today {pct('losses_today')}",
         f"{pct('paytm_ecl_low', 1)}–{pct('paytm_ecl_high', 0)}, with repayment from the till.",
         "bad", "The main risk", f"Lenders without the till run {pct('digital_losses_low')}–{pct('digital_losses_high')}: at or above our line."),
    ]
    trs = "".join(
        f'<tr><td><b>{a}</b><div class="sub">{b} · {c}</div></td><td>{d}</td>'
        f'<td><span class="chip {k}"><span>{ {"good": "✓", "warn": "!", "bad": "✕"}[k] }</span>{e}</span><div class="sub">{f}</div></td></tr>'
        for a, b, c, d, k, e, f in rows)

    status_word = {"primary": "Opened: company or regulator", "news": "Opened: news report", "search summary": "Search summary only", "earlier": "Earlier research"}
    src = "".join(
        f'<tr><td>{r["id"]}</td><td>{html.escape(r["claim"])}</td><td>{html.escape(r["source"])}<div class="sub">{html.escape(r["date"])}</div></td>'
        f'<td>{status_word[r["status"]]}{(" (" + html.escape(r["note"].split(";")[0]) + ")") if r["status"] == "earlier" and r["note"] else ""}</td></tr>'
        for r in sorted(EV, key=lambda r: int(r['id'].split('-')[1])))
    n_search = sum(r["status"] == "search summary" for r in EV)

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>QR moat test</title>
<style>
@page {{ size: A4; margin: 14mm 15mm 14mm 15mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; color: {INK}; font-size: 10.5pt; line-height: 1.45; background: #fff; }}
.kicker {{ font-size: 8.5pt; letter-spacing: .08em; text-transform: uppercase; color: {MUTED}; }}
h1 {{ font-size: 21pt; line-height: 1.15; margin: 4px 0 10px; letter-spacing: -.01em; }}
h2 {{ font-size: 14pt; margin: 0 0 4px; }}
h3 {{ font-size: 11pt; margin: 0; }}
.answer {{ font-size: 12.5pt; line-height: 1.5; border-left: 4px solid {BROWN}; padding: 2px 0 2px 14px; margin: 10px 0 14px; }}
.premise {{ background: #f7f6f3; border-radius: 8px; padding: 10px 14px; color: {MUTED}; margin-bottom: 14px; }}
.tiles {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 6px 0 14px; }}
.tile {{ border: 1px solid {RULE}; border-radius: 10px; padding: 10px 12px; }}
.tlabel {{ font-size: 9pt; color: {MUTED}; text-transform: uppercase; letter-spacing: .05em; }}
.tile p {{ margin: 6px 0 0; font-size: 9.8pt; }}
.chip {{ display: inline-flex; align-items: center; gap: 6px; font-weight: 700; font-size: 10pt; padding: 2px 9px 2px 3px; border-radius: 999px; margin-top: 4px; white-space: nowrap; }}
.chip span {{ display: inline-flex; width: 17px; height: 17px; border-radius: 50%; align-items: center; justify-content: center; color: #fff; font-size: 9pt; }}
.chip.good {{ background: #e6f2ea; color: #1d5a3c; }} .chip.good span {{ background: #2f6b4f; }}
.chip.warn {{ background: #fbf1dc; color: #7a5300; }} .chip.warn span {{ background: #9a6700; }}
.chip.bad {{ background: #f8e6e3; color: #8f1d12; }} .chip.bad span {{ background: #b42318; }}
.means {{ border: 2px solid {INK}; border-radius: 10px; padding: 10px 14px; }}
.means p {{ margin: 4px 0; }}
.brk {{ break-before: page; }}
.lede {{ color: {MUTED}; margin: 0 0 10px; }}
.fig {{ border: 1px solid {RULE}; border-radius: 10px; padding: 12px 14px; margin: 8px 0 14px; break-inside: avoid; }}
.fig .cap {{ font-size: 9.5pt; color: {MUTED}; margin-top: 4px; }}
.trio {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
.trio .m h3 {{ font-size: 10pt; min-height: 30px; }}
.trio .m .unit {{ font-size: 8.5pt; color: {MUTED}; }}
.trio .m .say {{ font-weight: 700; font-size: 10pt; margin-top: 2px; }}
.legend {{ font-size: 9pt; color: {MUTED}; margin-top: 6px; }}
.sw {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; vertical-align: -1px; margin: 0 4px 0 10px; }}
.take {{ background: #f7f6f3; border-radius: 8px; padding: 10px 14px; }}
.take ol {{ margin: 4px 0 0 18px; padding: 0; }}
.cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
.card {{ border: 1px solid {RULE}; border-radius: 10px; padding: 10px 12px; break-inside: avoid; }}
.chead {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.chead .no {{ width: 20px; height: 20px; border-radius: 50%; background: {INK}; color: #fff; font-size: 9pt; display: inline-flex; align-items: center; justify-content: center; }}
.chead h3 {{ flex: 1; }}
.chead .chip {{ margin-top: 0; font-size: 9pt; }}
.card ul {{ margin: 6px 0 0 16px; padding: 0; font-size: 9.6pt; }}
.card li {{ margin-bottom: 3px; }}
.prec {{ border-left: 4px solid {GREY}; padding: 4px 0 4px 12px; margin: 12px 0 0; font-size: 10pt; }}
table {{ width: 100%; border-collapse: collapse; }}
.four td {{ border-top: 1px solid {RULE}; padding: 8px 6px; vertical-align: top; font-size: 9.8pt; }}
.four th {{ text-align: left; font-size: 8.5pt; color: {MUTED}; text-transform: uppercase; letter-spacing: .05em; padding: 4px 6px; }}
.sub {{ color: {MUTED}; font-size: 9pt; margin-top: 2px; }}
.opts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px; }}
.opt {{ border: 1px solid {RULE}; border-radius: 10px; padding: 8px 12px; font-size: 9.6pt; break-inside: avoid; }}
.opt b {{ display: block; font-size: 10.2pt; margin-bottom: 2px; }}
.pilot ol {{ margin: 4px 0 0 18px; padding: 0; }}
.pilot li {{ margin-bottom: 3px; }}
.src td {{ border-top: 1px solid {RULE}; padding: 4px 5px; font-size: 8pt; vertical-align: top; line-height: 1.3; }}
.src th {{ text-align: left; font-size: 8pt; color: {MUTED}; padding: 3px 5px; }}
.src td:first-child {{ white-space: nowrap; color: {MUTED}; }}
.foot {{ font-size: 8.5pt; color: {MUTED}; margin-top: 10px; }}
</style></head><body>

<div class="kicker">Save first, lend later · testing one premise · 12 October 2026</div>
<h1>Can Paytm and PhonePe stop a newcomer from winning shopkeepers?</h1>
<div class="premise"><b>The premise.</b> The plan wins shopkeepers with a daily savings habit, then lends to the ones who save well. That needs a newcomer to win, and lend to, shops that Paytm, PhonePe and BharatPe already serve. You put it as: <i>"the QR code strategy is not defensible."</i> This note tests that. It is not written to prove it.</div>
<div class="answer"><b>Half true.</b> The QR code itself protects no one: any shop can put up another, and most already have several. But the QR was never what protects Paytm and PhonePe. What protects them is that a shop's daily takings pass through their hands, so they <b>take the loan instalment before the shop is paid</b>. That part is hard to beat, and lending is exactly where we planned to make our money.</div>

<div class="tiles">{tiles}</div>

<div class="means">
<p><b>What it means for us.</b> The idea does not stand or fall on the QR. It stands or falls on a narrower question nobody has answered yet:</p>
<p style="font-size:11.5pt"><b>Can a shopkeeper's saving record, plus our own way of collecting, lend as safely as a lender who sits on the till?</b></p>
<p>Until a pilot shows it can, shopkeepers are the hardest place to start, because that is where the till-holders are strongest. Pages 2–4 show the evidence; page 5 lists four ways the idea can live with the moat.</p>
</div>

<div class="brk"></div>
<h2>The real moat: who gets paid first</h2>
<p class="lede">The same ₹500 sale, and two loans. The difference is the order in which people get paid.</p>
<div class="fig">{who_gets_paid_first()}</div>

<h2>Where losses must land</h2>
<p class="lede">Bad-loan losses a year, as a share of what is lent. One shopkeeper stops paying back for us above {pct('be_losses', 1)} (our break-even line from the deck).</p>
<div class="fig">{loss_line()}
<div class="cap">The till-holders sit {n('headroom_vs_paytm') * 100:.1f} points under our break-even. Lenders who must ask for their money, as we would, sit at or above it. The deck assumes {pct('losses_today')}; this is why that number carries the most risk.</div></div>

<div class="brk"></div>
<h2>Two live tests</h2>
<p class="lede">Two things have already happened that show which parts of the moat hold.</p>
<h3 style="margin:10px 0 2px">1. The 2024 shock: what happened when a QR giant was hit</h3>
<p class="lede">In January 2024 the RBI ordered Paytm Payments Bank to stop most of its business, and Paytm had to move shops' payouts to other banks. It is the nearest thing to a live test of which layer holds.</p>
<div class="fig">
<div class="trio">
<div class="m"><h3>Customers: Paytm app's share of UPI payments</h3>{paytm_a}<div class="say">Halved in a year</div><div class="unit">customers switch apps easily</div></div>
<div class="m"><h3>Shops paying for a Paytm device, crore</h3>{paytm_b}<div class="say">Flat through the shock, then +{pct('paytm_dev_since')}</div><div class="unit">the box on the counter stayed</div></div>
<div class="m"><h3>Paytm shop loans given out, ₹ crore a quarter</h3>{paytm_c}<div class="say">Down {pct('paytm_ml_drop')} in one quarter</div><div class="unit">the lenders behind Paytm pulled back</div></div>
</div>
<div class="legend"><span class="sw" style="background:{GREY};margin-left:0"></span>before the RBI action<span class="sw" style="background:{BROWN}"></span>after</div>
</div>
<div class="take"><b>What the test says.</b><ol>
<li>Which app customers pay with is <b>not</b> a moat. A new app can reach shopkeepers.</li>
<li>The device and the daily payout <b>are</b> a moat. Shops stayed even while Paytm was in trouble.</li>
<li>The lending is only as steady as the lenders behind it. Those lenders are partners anyone can approach, including us.</li></ol></div>
<h3 style="margin:18px 0 2px">2. Khatabook: winning shops with a hook that never touches the till</h3>
<div class="prec">Khatabook won shopkeepers with a free ledger app. Like savings, a ledger never touches the till. Then it found it <i>"can't lend enough"</i>: loans too small, data unreliable, too little presence on the ground (Morning Context, 2023). FY24: revenue ₹102.7 crore, loss ₹116.2 crore. Winning shops with a hook worked; lending off the hook did not, yet.</div>

<div class="brk"></div>
<h2>Layer by layer</h2>
<p class="lede">What Paytm, PhonePe and BharatPe actually hold, and how hard each piece is to take.</p>
<div class="cards">{layers}</div>


<div class="brk"></div>
<h2>What this does to our four numbers</h2>
<p class="lede">The deck's four break-even lines for one shopkeeper, against what the till-holders show.</p>
<table class="four"><tr><th style="width:24%">Our number</th><th style="width:38%">What the till-holders show</th><th>Effect on us</th></tr>{trs}</table>
<p style="margin:10px 0 14px"><b>For shopkeepers, the premise that matters is losses, not the QR.</b></p>

<h2>How Bachatt lives without the till</h2>
<p class="lede">Bachatt already sells daily saving to this customer, and investors have put about ${n('bachatt_raised'):.0f} million into it. It does not sit on the counter, and it does not hold the loan. Two different filters are easy to mix up.</p>
<div class="take"><ol>
<li><b>Who shows up is a filter, and it is small.</b> Bachatt claims {n('bachatt_users') / 1e6:.0f} million users since May 2025. In February 2026 it ran {n('bachatt_txns') / 1e6:.0f} million fund purchases. If one daily saver produces about {n('debits_per_saver'):.0f} purchases a month, that is about {n('bachatt_daily_savers') / 1e5:.0f} lakh people still saving: {pct('bachatt_saver_share', 1)} of the people who signed up. The other {100 - n('bachatt_saver_share') * 100:.0f}% never become a lending problem. Our model already works this way. The cost to win and the value per shopkeeper count the person we got, not every shop on the street.</li>
<li><b>Who repays is a second filter, and nobody has shown it.</b> Partners book Bachatt's loans, up to ₹{n('bachatt_loan_cap') / 100000:.0f} lakh, so a {pct('digital_losses_low')}–{pct('digital_losses_high')} loss sits on the partner, not on Bachatt. We said we would hold the loan. Holding it, and changing only the loss rate, one shopkeeper is worth {rs(n('value_if_losses_3'))} at 3% losses, {rs(n('value_today'))} at the 6% the model assumes, and {rs(n('value_if_losses_10')).replace('₹-', '−₹')} at 10%. The 3% is the hope that people who choose to save are safer. It is not the base case.</li>
</ol></div>
<p>Bachatt has published no retention, loan volume, or default figure. The funding is a bet that the second filter is real. It is not evidence that it is.</p>

<h2>Four ways the idea can live with the moat</h2>
<div class="opts">
<div class="opt"><b>A. Go where no one holds the till</b>Salaried workers through employers: the salary deduction becomes our till. In our model, at 24% a salaried customer is worth +{rs(n('sal_safe_24'))} in the low-loss case (3% losses), but {rs(n('sal_normal_24')).replace('₹-', '−₹')} in the normal case (6%). So it works only if deduction keeps losses low.</div>
<div class="opt"><b>B. Ask for the whole bank statement</b>Make Account Aggregator consent part of joining. We would then see money from all of a shop's QR codes, where Paytm sees only its own.</div>
<div class="opt"><b>C. Let the savings secure the loan</b>A year of ₹100 a day is {rs(n('save_year'))}, about {pct('save_year_share_of_loan')} of a ₹1.5 lakh loan, if every debit succeeds. Lending against the saver's own fund units would make each loss smaller.</div>
<div class="opt"><b>D. Partner instead of fighting</b>Be the savings product inside BharatPe's or PhonePe's app. Shops become cheap to reach, but the partner keeps the customer and the lending, which removes the business we modelled.</div>
</div>

<div class="take pilot" style="margin-top:12px"><b>What the pilot must add</b> to the four numbers it already measures:<ol>
<li>How many of our savers already have a Paytm, PhonePe or BharatPe loan.</li>
<li>How many will share their bank statement through Account Aggregator.</li>
<li>What share of daily Autopay <i>loan instalments</i> succeed (not savings debits).</li>
<li>Whether shopkeepers keep saving with us when PhonePe offers ₹100 a day at the same counter.</li></ol></div>

<div class="brk"></div>
<h2>Sources</h2>
<p class="lede">Every figure above, one row each. "Search summary only" means the number was seen in a search engine's summary and the page itself was not opened ({n_search} of {len(EV)} rows); treat those as reported, not checked. The tables behind this note are research/qr_moat.csv and tables/qr_moat_numbers.csv.</p>
<table class="src"><tr><th>Id</th><th>What it says</th><th>Source</th><th>How checked</th></tr>{src}</table>
<div class="foot">Derived figures (computed in model/qr_moat.py): QR codes per shop = QM-01 ÷ QM-02; Paytm share fall = 1 − QM-16 ÷ QM-15; device change = QM-07 ÷ QM-06 and QM-09 ÷ QM-07; loan fall = 1 − QM-18 ÷ QM-17; PhonePe growth = QM-30 ÷ its Apr–Sep 2024 value. Bachatt daily savers = QM-42 × 1 million ÷ QM-43, then ÷ QM-41. The ₹597 and −₹319 move only the loss rate to the 3% and 10% ends of its range; every other shopkeeper input stays at today's evidence (tables/lend_breakeven.csv). Other break-even lines: the same table, and tables/lend_salaried.csv.</div>
</body></html>"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    src = OUT_DIR / "qr_moat.html"
    src.write_text(page())
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", src.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {src}\nwrote {PDF}")


if __name__ == "__main__":
    main()

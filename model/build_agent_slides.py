"""Two-page PDF: what one street agent (Rs 4 lakh a year) costs and what has to pay for him
(operator, 16 Oct 2026: "create a 1-2 slider ... pdf, pictures, flowchart, tables. be very precise";
"take out the cost of the fleet on street guy which is roughly 4L per year").

Quotes only tables written by model/invert_deposit_cost.py (tables/invert_agent_*.csv). Reuses the drawing
helpers of build_qr_visual.py. Writes brief/qr_moat/agent_slides.html and Street_agent_economics.pdf.
"""
import csv
import subprocess
from pathlib import Path

import build_qr_visual as V

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
PDF = ROOT / "Street_agent_economics.pdf"
BOOK = list(csv.DictReader((T / "invert_agent_book.csv").open()))
ST = {k: float(v) for k, v in next(csv.DictReader((T / "invert_agent_stack.csv").open())).items()}
FILL = list(csv.DictReader((T / "invert_agent_fill.csv").open()))
SIZE = list(csv.DictReader((T / "invert_agent_loan_size.csv").open()))
NOTE = {r["key"]: float(r["value"]) for r in csv.DictReader((T / "invert_agent_notes.csv").open())}
AGENT, SAVERS, DAILY = 400000, 300, 350
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD


def inr(x):
    """Indian digit grouping: 337000 -> Rs 3,37,000."""
    v = round(x)
    s, neg = str(abs(v)), v < 0
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("−" if neg else "") + "₹" + s


def crore(x):
    return f"₹{x / 1e7:.2f} crore"


def lakh(x):
    return f"₹{x / 1e5:.2f} lakh"


def pct(x, d=0):
    return f"{x * 100:.{d}f}%"


# ---------- page 1 ----------
def flow_cost():
    s = [V.text(0, 14, "WHAT ONE AGENT COSTS", 12.5, 700, US), V.text(300, 14, "PAID BACK, MIDDLE CASE", 12.5, 700, THEM)]
    left = [("person", THEM, "Street agent", f"{inr(AGENT)} a year, all-in", None),
            ("hands", INK, f"{SAVERS} savers", f"× ₹{DAILY} a day × 240 days", None),
            ("jar", US, crore(ST["deposits_a_year"]), "deposited in a year", None),
            ("coin", US, f"Agent = {pct(ST['cost_pct'], 2)}", "of every rupee deposited", US)]
    for i, (ic, c, t, sub, hl) in enumerate(left):
        y = 28 + i * 88
        s.append(V.node(0, y, 262, 64, ic, c, t, sub, hl))
        if i < 3:
            s.append(V.arrow(131, y + 66, 131, y + 86))
    right = [("bank", THEM, f"Fund commission {inr(ST['fund_mid'])}", f"0.35% a year on {crore(ST['balance'])} held", None),
             ("doc", THEM, f"Other products {inr(ST['other_mid'])}", "insurance, bills etc: ₹63 a saver", None),
             ("coin", THEM, f"Pays back {inr(ST['nonloan_mid'])}", f"= {pct(ST['covered_mid'])} of the agent's cost", THEM)]
    for i, (ic, c, t, sub, hl) in enumerate(right):
        y = 28 + i * 88
        s.append(V.node(300, y, 262, 64, ic, c, t, sub, hl))
        if i < 2:
            s.append(V.text(431, y + 84, "+" if i == 0 else "=", 22, 800, MUTED, "middle"))
    s.append(V.arrow(131, 360, 131, 382, BAD, 2.5))
    s.append(V.arrow(431, 270, 431, 382, BAD, 2.5))
    s.append(f'<rect x="0" y="384" width="562" height="62" rx="12" fill="{V.TINT["bad"]}" stroke="{BAD}" stroke-width="2"/>')
    s.append(V.icon("broken", 14, 395, 40, BAD))
    s.append(V.text(66, 410, f"{inr(AGENT)} − {inr(ST['nonloan_mid'])} = {inr(ST['gap_mid'])} a year still to find", 16, 800, BAD))
    s.append(V.text(66, 432, f"{inr(ST['gap_per_saver_mid'])} per saver a year · only loans are big enough (page 2)", 13, 400, BAD))
    return V.svg(562, 450, "".join(s))


def table_book():
    rows = []
    labels = {51.0: "Bachatt's minimum", 100.0: "our model's saver", 350.0: "Arvinder's middle", 500.0: "Arvinder's top"}
    for r in BOOK:
        a, need = float(r["saver_puts_in_a_day"]), float(r["savers_needed_for_1_5pct"])
        ok = need <= 400
        mark = f'<span class="chip {"good" if ok else "bad"}"><span>{"✓" if ok else "✕"}</span>{need:,.0f}</span>'
        rows.append(f'<tr{" class=hl" if a == DAILY else ""}><td>₹{a:.0f} a day <span class="m">{labels[a]}</span></td>'
                    f'<td class="n">{inr(float(r["deposits_a_year"]))}</td><td class="n">{mark}</td>'
                    f'<td class="n">{pct(float(r["cost_pct_at_300_savers"]), 1)}</td></tr>')
    return ('<div class="tt">How many savers one agent needs for ₹4 lakh to be 1.5% of deposits</div>'
            '<table class="tbl"><colgroup><col style="width:38%"><col style="width:20%"><col style="width:20%"><col style="width:22%"></colgroup>'
            '<tr><th>Each saver puts in</th><th class="n">Deposits a year</th><th class="n">Savers needed</th>'
            '<th class="n">Cost if he has 300</th></tr>' + "".join(rows) + '</table>'
            '<div class="tn">✕ = more savers than one person can visit every day (Arvinder visits 200–400).</div>')


def table_payback():
    def row(label, k, bold=False, fmt=inr):
        cells = "".join(f'<td class="n">{"<b>" if bold else ""}{fmt(ST[f"{k}_{c}"])}{"</b>" if bold else ""}</td>' for c in ("low", "mid", "high"))
        return f'<tr{" class=hl" if bold else ""}><td>{label}</td>{cells}</tr>'
    return ('<div class="tt">What his 300 savers pay back in a year</div>'
            '<table class="tbl"><colgroup><col style="width:52%"><col style="width:16%"><col style="width:16%"><col style="width:16%"></colgroup>'
            '<tr><th></th><th class="n">Low</th><th class="n">Middle</th><th class="n">High</th></tr>'
            + row(f"Fund commission, 0.20 / 0.35 / 0.50% of {crore(ST['balance'])} held", "fund")
            + row("Other products, ₹8 / ₹63 / ₹259 a saver", "other")
            + row("Total paid back", "nonloan", True)
            + row("Share of the ₹4 lakh agent", "covered", False, lambda x: pct(x))
            + row("Gap left for loans", "gap", True)
            + '</table>')


# ---------- page 2 ----------
def table_fill():
    order = sorted(FILL, key=lambda r: float(r["short_by"]))
    nice = {"Lend a shop loan ourselves, losses 3% (savers really safer)": "Lend ₹1.5L ourselves, 3% losses",
            "Lend a shop loan ourselves (Rs 1.5 lakh, 12 months, 26%)": "Lend ₹1.5L ourselves, 6% losses",
            "Refer a shop loan (Rs 1.5 lakh)": "Refer ₹1.5L shop loan (2%)",
            "Refer a personal loan (Rs 25,557)": "Refer ₹25,557 personal loan (2%)",
            "Small term-life policy": "Small term-life policy",
            "Accident or hospital-cash policy": "Accident / hospital cash",
            "Two-wheeler insurance": "Two-wheeler insurance"}
    rows = []
    for r in order:
        sb = float(r["short_by"])
        kind = "warn" if sb < 10 else "bad"
        rows.append(f'<tr><td>{nice[r["product"]]}</td><td class="n">{inr(float(r["earns_per_unit"]))}</td>'
                    f'<td class="n"><b>{float(r["units_per_agent_a_year"]):,.0f}</b></td><td class="n">{float(r["per_saver_a_year"]):.2f}</td>'
                    f'<td class="n">{float(r["evidence_per_saver_a_year"]):.2f}</td>'
                    f'<td class="n"><span class="chip {kind}"><span>{"!" if kind == "warn" else "✕"}</span>{sb:.0f}×</span></td></tr>')
    return ('<div class="tt">To fill the ₹3,37,000 gap with one product alone (all per year)</div>'
            '<table class="tbl"><colgroup><col style="width:40%"><col style="width:12%"><col style="width:13%"><col style="width:12%"><col style="width:10%"><col style="width:13%"></colgroup>'
            '<tr><th>Product</th><th class="n">Earns per unit</th><th class="n">Needed per agent</th>'
            '<th class="n">Needed per saver</th><th class="n">Savers buy</th><th class="n">Short by</th></tr>' + "".join(rows) + '</table>'
            '<div class="tn">"Savers buy" for loans = approved loans per saver a year, evidence middle (range 0.01–0.08). '
            'Our model assumes 0.20: short of the 0.24 needed at 6% losses, enough at 3% (0.13).</div>')


def flow_losses():
    s = [V.text(0, 14, "DOES A ₹1.5 LAKH SHOP LOAN MAKE MONEY?", 12.5, 700, US)]
    s.append(V.diamond(88, 128, 168, 110, "Bad-loan losses|a year?", US))
    cases = [("3%", NOTE["loss_3pct_net_per_loan"], f"{NOTE['loans_needed_3pct']:.0f} loans per agent a year", GOOD, 34),
             ("6%", NOTE["loss_6pct_net_per_loan"], f"{NOTE['loans_needed_6pct']:.0f} loans per agent a year", WARN, 102),
             ("9%", NOTE["loss_9pct_net_per_loan"], "every loan loses: no number is enough", BAD, 170)]
    for lab, net, sub, c, y in cases:
        s.append(V.arrow(172, 128, 214, y + 30, c, 2))
        s.append(V.node(216, y, 262, 60, None, c, f"{lab} → {'+' if net > 0 else ''}{inr(net)} a loan", sub, c))
    s.append(V.text(0, 252, "Digital lenders today run 7–10% losses; Paytm-sourced shop loans 4.5–5%.", 12, 400, MUTED))
    return V.svg(480, 258, "".join(s))


def bars_size():
    can = float(SIZE[0]["saver_can_repay_12m"])
    w, x0, x1 = 480, 0, 420
    vmax = 1300000
    X = lambda v: x0 + (x1 - x0) * v / vmax
    s = [V.text(0, 14, "HOW BIG EACH LOAN MUST BE (LENDING OURSELVES, 6% LOSSES)", 12.5, 700, US)]
    rows = [(f"If 3 in 100 savers borrow a year (evidence)", float(SIZE[0]["loan_size_needed"]), float(SIZE[0]["times"])),
            (f"If 20 in 100 borrow a year (our model)", float(SIZE[1]["loan_size_needed"]), float(SIZE[1]["times"]))]
    for i, (lab, v, times) in enumerate(rows):
        y = 34 + i * 58
        s.append(V.text(X(can) + 10, y + 2, lab, 12.5, 600, INK))
        s.append(f'<rect x="{x0}" y="{y + 10}" width="{X(v) - x0}" height="24" rx="4" fill="{US}"/>')
        s.append(V.text(X(v) + 8 if X(v) < 330 else X(v) - 8, y + 28, f"{lakh(v)} = {times:.1f}×", 13.5, 800, INK if X(v) < 330 else "#fff", "start" if X(v) < 330 else "end"))
    s.append(f'<line x1="{X(can)}" y1="30" x2="{X(can)}" y2="150" stroke="{GOOD}" stroke-width="2.5" stroke-dasharray="5 4"/>')
    s.append(V.text(X(can) + 6, 158, f"Green line: what a ₹{DAILY}-a-day saver's own saving repays in 12 months, {inr(can)}", 12, 700, GOOD))
    return V.svg(w, 166, "".join(s))


def also_true():
    items = [("hands", f"<b>He must sign {NOTE['signups_to_keep_book']:,.0f} people</b> to have 300 still saving a year later (24 of 100 stay): {NOTE['signups_per_working_day']:.1f} sign-ups every working day."),
             ("phone", "<b>UPI is the only way past 400 savers.</b> Below ₹350 a day, one agent needs more savers than one person can visit (page 1)."),
             ("jar", "<b>Only digital gold pays on every rupee:</b> about 2.4% of each purchase (Jar), and the saver pays it through GST and the buy-sell gap.")]
    cells = "".join(f'<div class="at"><div class="ai">{V.svg(48, 48, V.icon(ic, 0, 0, 44, US))}</div><div>{t}</div></div>' for ic, t in items)
    return f'<div class="also">{cells}</div>'


CSS = V.CSS.replace("INK", INK).replace("MUTED", MUTED).replace("RULE", RULE).replace("US", US) + f"""
.grid {{ display: grid; gap: 14px 18px; flex: 1; min-height: 0; }}
.g1 {{ grid-template-columns: 54% 1fr; }}
.g2 {{ grid-template-columns: 50% 1fr; }}
.col {{ display: flex; flex-direction: column; gap: 10px; min-width: 0; }}
.tt {{ font-size: 10.5pt; font-weight: 700; margin: 0 0 4px; }}
.tbl {{ width: 100%; border-collapse: collapse; font-size: 9.2pt; table-layout: fixed; }}
.tbl th {{ text-align: left; font-size: 7.8pt; color: {MUTED}; text-transform: uppercase; letter-spacing: .04em; padding: 3px 5px; border-bottom: 1.5px solid {INK}; vertical-align: bottom; }}
.tbl td {{ padding: 3px 5px; border-bottom: 1px solid {RULE}; vertical-align: middle; }}
.tbl .n {{ text-align: right; white-space: nowrap; }}
.tbl th.n {{ white-space: normal; line-height: 1.2; }}
.tbl tr.hl td {{ background: #f6efe7; }}
.tbl .m {{ color: {MUTED}; font-size: 8.4pt; }}
.tbl .chip {{ display: inline-flex; align-items: center; gap: 4px; font-weight: 700; font-size: 8.2pt; padding: 1px 7px 1px 2px; border-radius: 999px; white-space: nowrap; }}
.tbl .chip span {{ display: inline-flex; width: 13px; height: 13px; border-radius: 50%; align-items: center; justify-content: center; color: #fff; font-size: 7.5pt; }}
.chip.good {{ background: {V.TINT['good']}; color: {GOOD}; }} .chip.good span {{ background: {GOOD}; }}
.chip.warn {{ background: {V.TINT['warn']}; color: {WARN}; }} .chip.warn span {{ background: {WARN}; }}
.chip.bad {{ background: {V.TINT['bad']}; color: {BAD}; }} .chip.bad span {{ background: {BAD}; }}
.tn {{ font-size: 8.2pt; color: {MUTED}; margin-top: 4px; line-height: 1.3; }}
.also {{ display: grid; grid-template-columns: 1fr; gap: 6px; margin-top: 4px; }}
.at {{ display: flex; gap: 8px; align-items: center; background: {V.PAPER}; border-radius: 10px; padding: 5px 10px; font-size: 8.8pt; line-height: 1.3; }}
.ai {{ width: 26px; flex: none; }}
.foot {{ font-size: 7.6pt; color: {MUTED}; margin-top: 6px; line-height: 1.35; }}
h1 {{ font-size: 18pt; margin-bottom: 8px; }}
.g1 .col svg, .g2 .col svg {{ width: 100%; height: auto; }}
"""

ASSUME = ("Assumptions: agent ₹4,00,000 a year all-in (your figure) · 300 savers × ₹350 a day, the middle of Arvinder's 200–400 savers and ₹200–500 a day "
          "(interview, 15 Oct 2026) · 240 deposit days a year (20 a month; our estimate from Bachatt's 2M purchases ÷ ~1 lakh savers) · "
          "half a year's deposits held on average (year one, nothing withdrawn) · fund commission 0.2–0.5% a year (XB-04) · other products "
          "₹8 / ₹63 / ₹259 a saver a year (XO-39) · shop loan ₹1.5 lakh, 12 months, 26%, our model's net after funding, losses and running cost "
          "(tables/lend_loan.csv) · referral 2% of the loan less 2.5% taken back (XL-13) · 24 of 100 savers still saving after a year (tables/lend_funnel.csv).")


def page(no, kicker, title, body, caption):
    return (f'<section class="slide"><div class="kick"><span class="pg">{no} / 2</span>{kicker}</div><h1>{title}</h1>{body}'
            f'<div class="cap">{caption}</div><div class="foot">{ASSUME} Built by model/invert_deposit_cost.py → tables/invert_agent_*.csv.</div></section>')


def build():
    p1 = page(1, "Street agent at ₹4 lakh a year · one janta-size book",
              f"One street agent costs ₹4 lakh a year. On a janta-size book that is {pct(ST['cost_pct'], 1)} of deposits, "
              f"and what his savers buy pays only {pct(ST['covered_mid'])} of it.",
              f'<div class="grid g1"><div class="col">{flow_cost()}</div><div class="col">{table_book()}{table_payback()}</div></div>',
              "The book size works only at ₹350+ a day. Even then the savings side pays a sixth of the agent; loans must pay the rest.")
    p2 = page(2, "Street agent at ₹4 lakh a year · what fills the gap",
              f"Filling the ₹3.37 lakh gap takes {NOTE['loans_needed_6pct']:.0f} shop loans a year per agent: 1 for every "
              f"{1 / float(next(r for r in FILL if r['product'].startswith('Lend a shop loan ourselves (Rs'))['per_saver_a_year']):.0f} savers. "
              f"The evidence shows 1 for every {1 / 0.03:.0f}.",
              f'<div class="grid g2"><div class="col">{table_fill()}{also_true()}</div><div class="col">{flow_losses()}{bars_size()}</div></div>',
              "It works only if savers borrow far more than evidence shows, loans run well above what savings repay, and losses stay near 3–6%.")
    css = CSS
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Street agent economics</title><style>{css}</style></head><body>{p1}{p2}</body></html>'


def main():
    out = ROOT / "brief" / "qr_moat" / "agent_slides.html"
    out.write_text(build())
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

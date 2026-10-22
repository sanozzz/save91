"""The final deck (operator, 16 Oct 2026: "we need to have key conclusion first in the slide and our final thought.
should we pilot or not").

Page 1 = key conclusions and the verdict; the last page = the final thought: pilot or not, on what terms. In between,
the stress-tested story (titles from story/storyline_2026-10-16.csv where the page is kept) with the agent-pay pages
rebuilt on the 3- and 5-year NPV (model/agent_npv.py: tables/npv_*.csv) and the pilot rules (tables/pilot_rules.csv).
Writes brief/qr_moat/final_deck.html and Offline_model_final.pdf.
"""
import csv
import subprocess
from pathlib import Path

import build_qr_visual as V
import build_stress_deck as SX
import agent_npv as N
from build_agent_slides import inr, pct

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
PDF = ROOT / "Offline_model_final.pdf"
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD
TAKES = list(csv.DictReader((T / "npv_takes.csv").open()))
MAXC = list(csv.DictReader((T / "npv_max_balance_commission.csv").open()))
PR = {r["key"]: float(r["value"]) for r in csv.DictReader((T / "pilot_rules.csv").open())}
TOTAL = 12
R12S = ("0.3", "0.4", "0.55", "0.7")
PAY_SAL, PAY_BAL, PAY_COL = "salary only", "salary + 0.5% a year of balance", "salary + 1% of collections"


def tk(years, pay, r12, col):
    v = next(r for r in TAKES if r["years"] == str(years) and r["pay"] == pay and r["r12"] == r12)[col]
    try:
        return float(v)
    except ValueError:
        return v


def lakh(x, d=2):
    return ("−" if x < 0 else "+") + f"₹{abs(x) / 1e5:.{d}f} lakh"


BE5, BE3 = tk(5, PAY_SAL, "break-even", "npv_middle_mix"), tk(3, PAY_SAL, "break-even", "npv_middle_mix")
BE5P = tk(5, PAY_SAL, "break-even", "npv_middle_mix_paytm_fee")
BAL_BE5P = tk(5, PAY_BAL, "break-even", "npv_middle_mix_paytm_fee")
FUND_YR = N.TRAIL * N.MONTHLY_SAVE * 12 * 0.5          # Rs 147: 0.35% on half a year's deposits
BAL_YR = 0.005 * N.MONTHLY_SAVE * 12 * 0.5             # Rs 210: 0.5% of the same balance
COL_YR = 0.01 * N.MONTHLY_SAVE * 12                    # Rs 840: 1% of a year's collections


def maxc(years, fee, r12):
    return float(next(r for r in MAXC if r["years"] == str(years) and r["loan_fee"] == fee and r["r12"] == r12)["max_balance_commission_a_year"])


# ---------- page 1: key conclusions and the verdict ----------
def p_conclusions():
    cards = [
        ("phone", "Online is costly to keep", f"{inr(SX.ONLINE_KEPT)}",
         f"per saver still saving after a year ({inr(SX.ONLINE_CAC)} to win, 24 of 100 stay); an app never earns it back."),
        ("person", "The street wins him for less", f"{inr(SX.CAC)} a saver",
         f"on a ₹20,000 salary and 1,000 sign-ups a year: {inr(SX.CAC / 0.7)}–{inr(SX.CAC / 0.3)} per saver kept."),
        ("coin", "Pay decides it", f"under {maxc(5, '1% loan fee', '0.55') * 100:.1f}%",
         f"a year of his balance is the most we can add to salary (55 of 100 saving, 5 years). 0.5% of balance never pays at a 1% loan fee; 1% of collections never."),
        ("hands", "On salary, retention decides", f"{BE5 * 100:.0f} of 100",
         f"still saving after a year makes one agent 5-year NPV positive ({BE3 * 100:.0f} for 3 years). Bear 30–40; one janta book says 72."),
        ("bank", "The biggest upside: loan fee", f"{BE5P * 100:.0f} of 100",
         "is the 5-year bar if each loan earns a Paytm-like 4.5% (collect on the visit, share first losses) instead of 1%."),
    ]
    cells = "".join(f'<div class="cc"><div class="ch">{V.svg(40, 40, V.icon(ic, 0, 0, 38, US))}<div class="ct">{t}</div></div>'
                    f'<div class="cn">{big}</div><div class="cs">{sub}</div></div>' for ic, t, big, sub in cards)
    verdict = (f'<div class="verdict"><div class="vh">✓ Our final thought: pilot it, small and on salary</div>'
               f'<div class="vb">One agent for 12 months, paid ₹20,000 a month with no cut of savings, beside a UPI-only comparison group. '
               f'The pilot year costs {inr(-PR["pilot_year1_result_r0.7"])}–{inr(-PR["pilot_year1_result_r0.3"])} after what his savers bring in (support not counted). '
               f'Stop at month 3 if sign-ups fall below 62 a month; stop at month 6 if fewer than {PR["five_year_breakeven_m6"] * 100:.0f} of 100 still save. '
               f'Scale only if month 12 shows {BE5 * 100:.0f}+ of 100 still saving.</div></div>')
    return f'<div class="stack"><div class="cgrid5">{cells}</div>{verdict}</div>'


# ---------- pay pages ----------
def p_pay_npv():
    w, x0, x1, y0, y1 = 900, 80, 600, 30, 250
    X = lambda r: x0 + (x1 - x0) * (float(r) - 0.3) / 0.4
    vmax, vmin = 700000, -3400000
    Y = lambda v: y0 + (y1 - y0) * (vmax - v) / (vmax - vmin)
    s = [V.text(0, 14, "ONE AGENT'S 5-YEAR NPV (MIDDLE CROSS-SELL, 20% A YEAR DISCOUNT), BY HOW MANY STILL SAVE AFTER A YEAR", 12.5, 700, US)]
    for v in (500000, 0, -1000000, -2000000, -3000000):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{INK if v == 0 else RULE}" stroke-width="{1.4 if v == 0 else 1}"/>')
        s.append(V.text(x0 - 8, Y(v) + 4, "₹0" if v == 0 else lakh(v, 0), 11, 400, MUTED, "end"))
    for r in R12S:
        s.append(V.text(X(r), y1 + 20, f"{int(float(r) * 100)} of 100", 12, 400, MUTED, "middle"))
    for pay, col, lab in ((PAY_SAL, GOOD, "₹20k salary only"), (PAY_BAL, "#b7835a", "₹20k + 0.5% of balance"), (PAY_COL, BAD, "₹20k + 1% of collections")):
        pts = [(r, tk(5, pay, r, "npv_middle_mix")) for r in R12S]
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(r):.1f},{Y(v):.1f}" for i, (r, v) in enumerate(pts))
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.5"/>')
        for r, v in pts:
            s.append(f'<circle cx="{X(r)}" cy="{Y(v)}" r="5" fill="{col}" stroke="#fff" stroke-width="2"/>')
        r, v = pts[-1]
        s.append(V.text(X(r) + 12, Y(v) + 5, f"{lab}: {lakh(v)}", 12.5, 800, col))
    s.append(f'<circle cx="{X(BE5)}" cy="{Y(0)}" r="7" fill="#fff" stroke="{GOOD}" stroke-width="3"/>')
    s.append(V.text(X(BE5) + 12, Y(0) + 22, f"positive from {BE5 * 100:.1f} of 100", 12.5, 800, GOOD))
    return V.svg(w, 276, "".join(s))


def p_per_saver():
    base, top = 250, 30
    Y = lambda v: base - (base - top) * v / 900
    bars = [(FUND_YR, GOOD, "the fund pays us", "0.35% a year of his balance"), (BAL_YR, "#b7835a", "0.5% of balance to the agent", "more than the fund pays"),
            (COL_YR, BAD, "1% of collections to the agent", "5.7× what the fund pays")]
    s = [V.text(0, 14, "ONE SAVER, ONE YEAR (₹350 A DAY; HALF A YEAR'S DEPOSITS, ₹42,000, SITS IN HIS FUND)", 12.5, 700, US),
         f'<line x1="20" y1="{base}" x2="880" y2="{base}" stroke="{INK}" stroke-width="1.2"/>']
    for i, (v, col, lab, sub) in enumerate(bars):
        x = 60 + i * 280
        s.append(f'<rect x="{x}" y="{Y(v)}" width="180" height="{base - Y(v)}" rx="6" fill="{col}"/>')
        s.append(V.text(x + 90, Y(v) - 10, inr(v), 24, 800, col, "middle"))
        s.append(V.text(x + 90, base + 22, lab, 13, 700, INK, "middle"))
        s.append(V.text(x + 90, base + 40, sub, 11.5, 400, MUTED, "middle"))
    return V.svg(900, 296, "".join(s))


def p_takes():
    def be(years, pay, col):
        v = tk(years, pay, "break-even", col)
        return f"{v * 100:.1f} of 100" if isinstance(v, float) else "never"
    rows = [("₹20k salary only", PAY_SAL), ("₹20k + 0.5% a year of balance", PAY_BAL), ("₹20k + 1% of collections", PAY_COL)]
    body = "".join(f'<tr><td><b>{lab}</b></td><td class="n">{be(3, pay, "npv_middle_mix")}</td><td class="n">{be(5, pay, "npv_middle_mix")}</td>'
                   f'<td class="n">{be(3, pay, "npv_middle_mix_paytm_fee")}</td><td class="n">{be(5, pay, "npv_middle_mix_paytm_fee")}</td></tr>' for lab, pay in rows)
    t1 = ('<div class="tt">Still saving after a year needed for one agent to be NPV positive (middle cross-sell)</div><table class="tbl">'
          '<colgroup><col style="width:32%"><col style="width:17%"><col style="width:17%"><col style="width:17%"><col style="width:17%"></colgroup>'
          '<tr><th>Agent pay</th><th class="n">3 years, 1% loan fee</th><th class="n">5 years, 1% loan fee</th><th class="n">3 years, Paytm-like 4.5%</th>'
          '<th class="n">5 years, Paytm-like 4.5%</th></tr>' + body + '</table>')
    body2 = "".join(f'<tr><td>{int(float(r) * 100)} of 100 still saving</td><td class="n">{maxc(5, "1% loan fee", r) * 100:.2f}% a year</td>'
                    f'<td class="n">{maxc(5, "Paytm-like 4.5%", r) * 100:.2f}% a year</td></tr>' for r in ("0.4", "0.55", "0.7"))
    t2 = ('<div class="tt" style="margin-top:14px">The most we can pay him on the balance, on top of ₹20,000, and stay 5-year positive</div><table class="tbl">'
          '<colgroup><col style="width:40%"><col style="width:30%"><col style="width:30%"></colgroup>'
          '<tr><th></th><th class="n">1% loan fee</th><th class="n">Paytm-like 4.5% loan fee</th></tr>' + body2 + '</table>')
    return f'<div class="col" style="width:100%">{t1}{t2}</div>'


def p_final():
    rules = [("Months 1–3", "Sign-ups", "62+ a month (about 750 a year)", f"below 62 a month: stop"),
             ("Month 3 and 6", "Still saving", f"{PR['five_year_breakeven_m3'] * 100:.0f}+ of 100 at month 3, {PR['five_year_breakeven_m6'] * 100:.0f}+ at month 6",
              f"fewer at month 6: stop"),
             ("Month 12", "Still saving after a year", f"{BE5 * 100:.0f}+ of 100 (5-year NPV positive); {BE3 * 100:.0f}+ for 3 years", f"below {BE5 * 100:.0f}: do not scale")]
    s = [f'<line x1="40" y1="56" x2="860" y2="56" stroke="{US}" stroke-width="4"/>']
    for i, (when, what, go, stop) in enumerate(rules):
        x = 40 + i * 410
        s.append(f'<circle cx="{x}" cy="56" r="14" fill="{US}"/>' + V.text(x, 62, str(i + 1), 14, 800, "#fff", "middle"))
        s.append(V.text(x, 26, when, 15, 800, US, "middle"))
        bx = max(0, min(x - 135, 630))
        s.append(f'<rect x="{bx}" y="84" width="270" height="150" rx="14" fill="{V.PAPER}"/>')
        s.append(V.text(bx + 14, 112, what, 15.5, 800, INK))
        for k, (kind, txt) in enumerate((("good", go), ("bad", stop))):
            y = 146 + k * 52
            s.append(V.badge(bx + 14, y, kind, "go" if kind == "good" else "stop", 13, "start"))
            words, line, lines = txt.split(), "", []
            for wd in words:
                if len(line) + len(wd) > 26:
                    lines.append(line)
                    line = wd
                else:
                    line = (line + " " + wd).strip()
            lines.append(line)
            for j, ln in enumerate(lines):
                s.append(V.text(bx + 70, y + 2 + j * 15, ln, 12, 600, GOOD if kind == "good" else BAD))
    s.append(f'<rect x="0" y="252" width="900" height="74" rx="14" fill="#f6efe7"/>')
    s.append(V.text(20, 278, "Each agent's 5-year NPV, by how many still save after a year (middle cross-sell): why the month-12 line matters", 13.5, 800, INK))
    vals = [(r, PR[f"npv5_per_agent_r{r}"]) for r in R12S]
    for i, (r, v) in enumerate(vals):
        s.append(V.text(20 + i * 220, 306, f"{int(float(r) * 100)} of 100: {lakh(v)}", 15, 800, GOOD if v >= 0 else BAD))
    return V.svg(900, 330, "".join(s))


EXTRA = """
.cgrid5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.cgrid5 .cc { background: #f7f5f0; border-radius: 12px; padding: 8px 10px; display: flex; flex-direction: column; gap: 4px; border-top: 5px solid #8A3B08; }
.cgrid5 .ch { display: flex; align-items: center; gap: 6px; } .cgrid5 .ch svg { width: 30px; height: 30px; flex: none; }
.cgrid5 .ct { font-weight: 700; font-size: 9.6pt; line-height: 1.2; }
.cgrid5 .cn { font-size: 15pt; font-weight: 800; color: #8A3B08; line-height: 1.1; }
.cgrid5 .cs { font-size: 8.8pt; line-height: 1.3; }
.verdict { margin-top: 10px; border-radius: 14px; padding: 12px 16px; background: #e6f2ea; border: 2px solid #2f6b4f; }
.verdict .vh { font-size: 14pt; font-weight: 800; color: #1d5a3c; }
.verdict .vb { font-size: 10.5pt; line-height: 1.45; margin-top: 4px; color: #1f2328; }
"""


def page(no, kicker, title, body, caption, src):
    return (f'<section class="slide"><div class="kick"><span class="pg">{no} / {TOTAL}</span>{kicker}</div><h1>{title}</h1>'
            f'<div class="vis">{body}</div><div class="cap">{caption}</div><div class="foot">{src}</div></section>')


def kept(pid, no, body, title=None, caption=None):
    r = SX.SL[pid]
    return page(no, r["kicker"], title or r["title"], body, caption or r["caption"], SX.sources(pid))


def build():
    npv_src = ("Built by model/agent_npv.py → tables/npv_takes.csv, npv_max_balance_commission.csv. One agent: ₹20,000 a month, 1,000 sign-ups a year, "
               "₹350 a day per saver, half a year's deposits in the fund (0.35% a year to us), 20% a year discount; middle cross-sell = insurance and other "
               "products ₹63 a saver a year, cards (5% × ₹1,250, unverified), 2.5 loans of ₹2.5 lakh per 100 proven savers a year at 1%.")
    pages = [
        page(1, "Key conclusions and our final thought",
             "The street can win and keep this saver for far less than an app. Whether one agent pays depends on two things: how we pay him, and how many keep saving.",
             p_conclusions(), "Everything after this page is the evidence; the last page is the pilot plan.",
             npv_src + " Pilot rules: tables/pilot_rules.csv."),
        kept("1", 2, SX.OD.p_problem()),
        kept("2", 3, SX.p2()),
        kept("3", 4, SX.p3()),
        kept("4", 5, SX.p4()),
        kept("5", 6, SX.p5()),
        kept("6", 7, SX.p6()),
        page(8, "Stress test · the pay rule",
             f"The pay rule decides it: on salary one agent is 5-year NPV positive from {BE5 * 100:.1f} of 100 still saving after a year; "
             "on 0.5% of balance or 1% of collections he never is, at a 1% loan fee.",
             p_pay_npv(), "On 1% of collections, better retention makes it worse. On 0.5% of balance it improves too slowly to turn positive. On salary it turns positive.",
             npv_src),
        page(9, "Stress test · why",
             f"Why: the fund pays us {inr(FUND_YR)} a year on a saver's balance. Paying the agent more than that, as 0.5% of balance ({inr(BAL_YR)}) "
             f"or 1% of collections ({inr(COL_YR)}) does, loses money on every saver he keeps.",
             p_per_saver(), "A janta bank can pay its agents a share of collections because it keeps and lends the deposit. Our saver's money sits in his own fund.",
             "Fund commission 0.35% a year (XB-04, middle); ₹350 a day × 240 days = ₹84,000 a year, half held = ₹42,000. Arvinder's pay: interview IV-13."),
        page(10, "What it takes",
             f"What it takes: on salary, {BE5 * 100:.0f} of 100 still saving over 5 years ({BE3 * 100:.0f} over 3). A Paytm-like loan fee lowers the bar to {BE5P * 100:.0f} "
             f"and makes 0.5% of balance workable at {BAL_BE5P * 100:.0f}+.",
             p_takes(), "If we want to pay the agent on the balance, keep it under about 0.2% a year, or earn a Paytm-like fee on loans first.",
             npv_src),
        kept("11", 11, SX.p11()),
        page(12, "Our final thought",
             f"Pilot it: one salaried agent for 12 months. It costs {inr(-PR['pilot_year1_result_r0.7'])}–{inr(-PR['pilot_year1_result_r0.3'])}, before support costs, "
             "to learn the one number that decides the business.",
             p_final(), "Run a UPI-only comparison group alongside, and ask a lender what fee it pays if our agent collects the instalments on his visit.",
             f"Year-1 cost: tables/scn_retention.csv (salary only, y1_result: {inr(-PR['pilot_year1_result_r0.7'])}–{inr(-PR['pilot_year1_result_r0.3'])}); "
             "month-3/6 lines: the month-12 bar under a steady monthly drop-off (tables/pilot_rules.csv); value per agent: tables/npv_takes.csv. Support costs are not counted."),
    ]
    appx = SX.build().split('<section class="slide">')[13:]
    appx_html = "".join('<section class="slide">' + a.split("</body>")[0] for a in appx)
    css = SX.A3.CSS + SX.A3.EXTRA_CSS + SX.OD.SD.STORY_CSS + SX.OD.CSS_EXTRA + EXTRA
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Offline model: final</title><style>{css}</style></head><body>{"".join(pages)}{appx_html}</body></html>'


def main():
    out = ROOT / "brief" / "qr_moat" / "final_deck.html"
    out.write_text(build())
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

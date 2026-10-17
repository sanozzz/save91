"""Two-page PDF: who can get a Rs 2.5 lakh loan, and one street agent's three years, on the operator's
assumptions (16 Oct 2026): 1,000 sign-ups a year to 3,000, collection every 2-3 days, agent Rs 4 lakh a year,
average loan Rs 2.5 lakh at a 1% fee to us, cards for 5% of savers, "loan eligibility and yearly take rates...
think of everything".

Quotes only tables written by model/agent_3yr.py (agent3_funnel.csv, agent3_funnel_inputs.csv, agent3_emi.csv,
agent3_years.csv). Writes brief/qr_moat/agent3_slides.html and Street_agent_3_years.pdf
(the earlier version is kept as Street_agent_3_years_v1.pdf).
"""
import csv
import subprocess
from pathlib import Path

import build_qr_visual as V
from build_agent_slides import CSS, inr, pct

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
PDF = ROOT / "Street_agent_3_years.pdf"
FUN = list(csv.DictReader((T / "agent3_funnel.csv").open()))
FIN = list(csv.DictReader((T / "agent3_funnel_inputs.csv").open()))
EMI = list(csv.DictReader((T / "agent3_emi.csv").open()))
YRS = list(csv.DictReader((T / "agent3_years.csv").open()))
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD
SRC = [("fund", "Fund commission", "#1F64A8"), ("other", "Other products", "#4E9BD9"), ("cards", "Credit cards", "#B08A2E"),
       ("loanfees", "Loan fees", "#8A3B08")]          # validated: dataviz validate_palette.js, light mode
COST3 = 1200000
VIEWS = [("all_stay", "Every saver stays", "your assumption"), ("janta", "Janta-like retention", "Arvinder's book: 72 of 100 after a year"),
         ("evidence", "App-like retention", "our model's evidence: 24 of 100")]


def f(view, year):
    r = next(r for r in FUN if r["view"] == view and r["year"] == str(year))
    return {k: (float(v) if k not in ("view", "year") else v) for k, v in r.items()}


def step(name):
    r = next(r for r in FIN if r["step"].startswith(name))
    return [float(r[k]) for k in ("low", "mid", "high")], r["basis"]


def lakh(x):
    return f"₹{x / 1e5:.2f}L"


# ---------- page 1: the loan funnel ----------
def funnel_flow():
    elig, _ = step("can carry")
    app, _ = step("applies")
    apr, _ = step("lender approves")
    fee, _ = step("fee kept")
    n = [100.0, 100 * elig[1], 100 * elig[1] * app[1], 100 * elig[1] * app[1] * apr[1]]
    lo = [100.0, 100 * elig[0], 100 * elig[0] * app[0], 100 * elig[0] * app[0] * apr[0]]
    hi = [100.0, 100 * elig[2], 100 * elig[2] * app[2], 100 * elig[2] * app[2] * apr[2]]
    boxes = [("hands", "Proven savers", "saved 6+ months, still saving"),
             ("doc", "Can carry the EMI", "₹2.5L EMI fits the 50% rule"),
             ("phone", "Apply this year", "want a loan now"),
             ("bank", "Lender approves", "loan is disbursed")]
    s = [V.text(0, 14, "OUT OF 100 PROVEN SAVERS, IN ONE YEAR (MIDDLE CASE; LOW–HIGH BELOW)", 12.5, 700, US)]
    for i, (ic, t, sub) in enumerate(boxes):
        y = 30 + i * 92
        w = 520 - i * 70
        s.append(f'<rect x="0" y="{y}" width="{w}" height="70" rx="12" fill="{V.PAPER}" stroke="{THEM if i < 3 else US}" stroke-width="{1.5 if i < 3 else 3}"/>')
        s.append(V.icon(ic, 12, y + 15, 40, THEM if i < 3 else US))
        s.append(V.text(64, y + 30, t, 15, 700))
        s.append(V.text(64, y + 50, sub, 12, 400, MUTED))
        val = f"{n[i]:.1f}" if n[i] < 10 else f"{n[i]:.0f}"
        rng = "" if i == 0 else (f"{lo[i]:.1f}–{hi[i]:.1f}" if hi[i] < 10 else f"{lo[i]:.0f}–{hi[i]:.0f}")
        s.append(V.text(w - 14, y + 36, val, 26, 800, THEM if i < 3 else US, "end"))
        if rng:
            s.append(V.text(w - 14, y + 56, rng, 11.5, 400, MUTED, "end"))
        if i < 3:
            s.append(V.arrow(40, y + 72, 40, y + 90))
    y = 30 + 4 * 92
    s.append(f'<rect x="0" y="{y - 6}" width="470" height="58" rx="12" fill="{V.TINT["warn"]}"/>')
    s.append(V.icon("coin", 12, y + 3, 40, US))
    s.append(V.text(64, y + 18, f"{n[3]:.1f} loans × {inr(fee[1])} kept = {inr(n[3] * fee[1])}", 16, 800, US))
    s.append(V.text(64, y + 40, f"per 100 proven savers a year (1% of ₹2.5L, 2.5% taken back)", 12, 400, US))
    return V.svg(522, y + 56, "".join(s))


def funnel_table():
    rows = []
    for name in ("can carry", "applies", "lender approves", "approved loans", "fee kept"):
        v, basis = step(name)
        label = {"can carry": "Can carry a ₹2.5L EMI", "applies": "Applies in a year", "lender approves": "Lender approves",
                 "approved loans": "Loans per proven saver a year", "fee kept": "Fee we keep per loan"}[name]
        fmt = (lambda x: inr(x)) if name == "fee kept" else (lambda x: pct(x, 1) if x < 0.1 else pct(x))
        bold = name == "approved loans"
        rows.append(f'<tr{" class=hl" if bold else ""}><td>{"<b>" if bold else ""}{label}{"</b>" if bold else ""}</td>'
                    + "".join(f'<td class="n">{"<b>" if bold else ""}{fmt(x)}{"</b>" if bold else ""}</td>' for x in v) + '</tr>')
    return ('<div class="tt">The loan funnel, low / middle / high</div><table class="tbl">'
            '<colgroup><col style="width:46%"><col style="width:18%"><col style="width:18%"><col style="width:18%"></colgroup>'
            '<tr><th>Step</th><th class="n">Low</th><th class="n">Middle</th><th class="n">High</th></tr>' + "".join(rows) + '</table>'
            '<div class="tn">Basis: EMI fit vs incomes of ₹20–40k and 41% already borrowing (XB-09); Kissht 17.5% ever borrowed (XL-42), '
            'Brazil payroll 20% in year one (LS-06), founder 35%; approval 25% from the founder\'s past lending data. '
            'The middle, 2.5 a year, matches the evidence middle of 3 (XL-48).</div>')


def emi_table():
    rows = []
    for e in EMI:
        ok20, ok40 = e["fits_50pct_rule_at_20k"] == "True", e["fits_50pct_rule_at_40k"] == "True"
        chip = lambda ok: f'<span class="chip {"good" if ok else "bad"}"><span>{"✓" if ok else "✕"}</span>{"fits" if ok else "too high"}</span>'
        rows.append(f'<tr><td>{e["months"]} months</td><td class="n">{inr(float(e["emi"]))}</td><td class="n">{float(e["times_monthly_saving"]):.1f}×</td>'
                    f'<td class="n">{pct(float(e["share_of_income_low"]))}–{pct(float(e["share_of_income_high"]))}</td>'
                    f'<td class="n">{chip(ok20)}</td><td class="n">{chip(ok40)}</td></tr>')
    return ('<div class="tt">Can a ₹350-a-day saver carry ₹2.5 lakh? (26% a year)</div><table class="tbl">'
            '<colgroup><col style="width:17%"><col style="width:16%"><col style="width:17%"><col style="width:18%"><col style="width:16%"><col style="width:16%"></colgroup>'
            '<tr><th>Loan over</th><th class="n">EMI a month</th><th class="n">× his ₹7,000 saving</th><th class="n">Share of ₹20–40k income</th>'
            '<th class="n">50% rule at ₹20k</th><th class="n">at ₹40k</th></tr>' + "".join(rows) + '</table>'
            f'<div class="tn">Even over 36 months the EMI ({inr(float(EMI[2]["emi"]))}) is just above half of a ₹20,000 income (₹10,000). '
            f'It fits from about {inr(2 * float(EMI[2]["emi"]))} a month, and only with no other EMI. 12 months never fits.</div>')


# ---------- page 2: one agent, three years ----------
def stacked():
    w, base, top = 540, 290, 36
    vmax = 1500000
    Y = lambda v: base - (base - top) * v / vmax
    s = [V.text(0, 14, "3-YEAR INCOME PER AGENT, MIDDLE CASE, AGAINST HIS ₹12 LAKH COST", 12.5, 700, US)]
    for v in (0, 500000, 1000000, 1500000):
        s.append(f'<line x1="56" y1="{Y(v)}" x2="{w}" y2="{Y(v)}" stroke="{RULE}"/>')
        s.append(V.text(50, Y(v) + 4, f"₹{v / 1e5:.0f}L", 11, 400, MUTED, "end"))
    s.append(f'<line x1="56" y1="{Y(COST3)}" x2="{w}" y2="{Y(COST3)}" stroke="{BAD}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    s.append(V.text(w, Y(COST3) - 6, "agent cost ₹12L", 12, 700, BAD, "end"))
    for i, (view, lab, sub) in enumerate(VIEWS):
        r = f(view, "1-3")
        x, bw, y0 = 76 + i * 156, 112, base
        for key, name, col in SRC:
            v = r[f"{key}_mid"]
            hgt = (base - top) * v / vmax
            s.append(f'<rect x="{x}" y="{y0 - hgt + 1}" width="{bw}" height="{max(hgt - 2, 1)}" rx="3" fill="{col}"/>')
            if hgt >= 18:
                s.append(V.text(x + bw / 2, y0 - hgt / 2 + 4, lakh(v), 11.5, 700, "#fff", "middle"))
            y0 -= hgt
        s.append(V.text(x + bw / 2, y0 - 8, f"{lakh(r['income_mid'])} = {pct(r['covered_mid'])}", 13, 800, GOOD if r["covered_mid"] >= 1 else BAD, "middle"))
        s.append(V.text(x + bw / 2, base + 18, lab, 12, 700, INK, "middle"))
        s.append(V.text(x + bw / 2, base + 33, sub.split(":")[0], 10.5, 400, MUTED, "middle"))
    return V.svg(w, base + 40, "".join(s))


def legend_table():
    cols = [f(v, "1-3") for v, _, _ in VIEWS]
    rows = "".join(f'<tr><td><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{col};margin-right:6px"></span>{name}</td>'
                   + "".join(f'<td class="n">{inr(c[f"{key}_mid"])}</td>' for c in cols) + '</tr>' for key, name, col in reversed(SRC))
    rows += '<tr class="hl"><td><b>Total, 3 years</b></td>' + "".join(f'<td class="n"><b>{inr(c["income_mid"])}</b></td>' for c in cols) + '</tr>'
    return ('<table class="tbl"><colgroup><col style="width:34%"><col style="width:22%"><col style="width:22%"><col style="width:22%"></colgroup>'
            '<tr><th>Income source (middle)</th>' + "".join(f'<th class="n">{lab}</th>' for _, lab, _ in VIEWS) + '</tr>' + rows + '</table>')


def result_table():
    def cells(view, key, fmt):
        return "".join(f'<td class="n">{fmt(f(view, "1-3")[f"{key}_{c}"])}</td>' for c in ("low", "mid", "high"))
    sign = lambda x: ("+" if x >= 0 else "−") + inr(abs(x))
    rows = []
    for view, lab, sub in VIEWS:
        rows.append(f'<tr class="hl"><td colspan="4"><b>{lab}</b> <span class="m">({sub})</span></td></tr>')
        rows.append(f'<tr><td>Income over 3 years</td>{cells(view, "income", inr)}</tr>')
        rows.append(f'<tr><td>After the ₹12L agent cost</td>{cells(view, "result", lambda x: "<b>" + sign(x) + "</b>")}</tr>')
        rows.append(f'<tr><td>Agent cost it can carry a year</td>{cells(view, "affordable_agent_cost_a_year", inr)}</tr>')
    return ('<div class="tt">3 years, low / middle / high (every input moved together)</div><table class="tbl">'
            '<colgroup><col style="width:43%"><col style="width:19%"><col style="width:19%"><col style="width:19%"></colgroup>'
            '<tr><th></th><th class="n">Low</th><th class="n">Middle</th><th class="n">High</th></tr>' + "".join(rows) + '</table>')


def year_rows():
    sign = lambda x: ("+" if x >= 0 else "−") + inr(abs(x))
    body = ""
    for view, lab, _ in VIEWS:
        t = f(view, "1-3")
        body += (f'<tr><td>{lab}</td>' + "".join(f'<td class="n">{sign(f(view, y)["result_mid"])}</td>' for y in (1, 2, 3))
                 + f'<td class="n">{t["loans_mid"]:.0f} / {t["loans_needed_mid"]:.0f}</td></tr>')
    return ('<div class="tt">Middle case: year by year after the ₹4L cost, and ₹2.5L loans we get / need over 3 years</div><table class="tbl">'
            '<colgroup><col style="width:31%"><col style="width:17%"><col style="width:17%"><col style="width:17%"><col style="width:18%"></colgroup>'
            '<tr><th></th><th class="n">Year 1</th><th class="n">Year 2</th><th class="n">Year 3</th><th class="n">Loans get / need</th></tr>' + body + '</table>')


ASSUME = ("Assumptions: agent ₹4,00,000 a year; 1,000 sign-ups a year for 3 years; collected every 2.5 days; ₹350 a day per saver, 240 days "
          "(your figures and Arvinder's middle) · average loan ₹2.5 lakh, 1% fee to us (your figures), 2.5% of fees taken back in the middle case "
          "(XL-13) · cards: 5% of sign-ups (your figure), ₹500 / ₹1,250 / ₹2,000 each (BM-08, unverified) · loans offered after 6 months of saving · "
          "fund commission 0.20 / 0.35 / 0.50% on half a year's deposits (XB-04) · other products ₹8 / ₹63 / ₹259 a saver a year (XO-39) · retention: "
          "everyone stays (you), janta-like 8 of 300 leaving a month (Arvinder), app-like = our model's evidence (24.2% at 12 months, 14.5% at 24, 11.8% at 36) · "
          "EMI at 26% a year; 50% rule (SG-22). "
          "Built by model/agent_3yr.py → tables/agent3_*.csv.")


TOTAL = 6
SURV = list(csv.DictReader((T / "agent3_survival.csv").open()))
BE = {k: float(v) for k, v in next(csv.DictReader((T / "agent3_breakeven.csv").open())).items()}
YR = {(r["view"], r["year"]): r for r in YRS}


def page(no, kicker, title, body, caption, foot=None):
    return (f'<section class="slide"><div class="kick"><span class="pg">{no} / {TOTAL}</span>{kicker}</div><h1>{title}</h1>{body}'
            f'<div class="cap">{caption}</div><div class="foot">{foot or ASSUME}</div></section>')


def tag(kind):
    label = {"you": "Your figure", "int": "One interview", "ev": "Evidence", "weak": "Weak evidence", "est": "Our estimate", "jud": "Judgement",
             "unv": "Unverified"}[kind]
    return f'<span class="tag {kind}">{label}</span>'


def assume_table(title, rows):
    body = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{" ".join(tag(k) for k in e)}</td></tr>' for a, b, c, d, e in rows)
    return (f'<div class="tt">{title}</div><table class="tbl at2"><colgroup><col style="width:17%"><col style="width:23%"><col style="width:14%"><col style="width:30%"><col style="width:16%"></colgroup>'
            '<tr><th>Assumption</th><th>Value used</th><th>Range tested</th><th>Where it comes from</th><th>How sure</th></tr>' + body + '</table>')


# ---------- page 1: key conclusions ----------
def conclusions():
    a, j, e = f("all_stay", "1-3"), f("janta", "1-3"), f("evidence", "1-3")
    j3 = f("janta", 3)
    rate, fee = step("approved loans")[0], step("fee kept")[0]
    emi36 = float(EMI[2]["emi"])
    sv = SURV[11]
    upi_j = float(YR[("janta", "3")]["upi_share_needed_end"])
    upi_a = float(YR[("all_stay", "3")]["upi_share_needed_end"])
    cut = 400000 - j["affordable_agent_cost_a_year_mid"]
    cards = [
        ("hands", "Retention decides it", f"{BE['still_saving_m12'] * 100:.0f} of 100",
         f"must still be saving after a year to break even. App evidence says {BE['evidence_m12'] * 100:.0f}. Arvinder's book (6–10 join, 6–10 leave a month) "
         f"implies {float(sv['still_saving_janta_mid']) * 100:.0f} ({float(sv['still_saving_janta_worst']) * 100:.0f}–{float(sv['still_saving_janta_best']) * 100:.0f}).", "pages 3, 5"),
        ("coin", "At janta-like retention, close", pct(j["covered_mid"]),
         f"of his 3-year cost is covered, and year 3 alone pays {pct(j3['covered_mid'])}: {float(YR[('janta', '1-3')]['active_end']):,.0f} savers by then. "
         f"Every saver staying: {pct(a['covered_mid'])}; app-like: {pct(e['covered_mid'])}.", "page 3"),
        ("phone", "Target for tele-sales and AI", inr(cut) + " a year",
         f"of work to take off each agent: janta-like retention carries {inr(j['affordable_agent_cost_a_year_mid'])} a year, not ₹4,00,000. "
         f"App-like carries {inr(e['affordable_agent_cost_a_year_mid'])}; every saver staying, {inr(a['affordable_agent_cost_a_year_mid'])}.", "page 3"),
        ("bank", "Loans at 1% are the smallest income", f"{inr(rate[1] * fee[1])} a saver",
         f"a year: {100 * rate[1]:.1f} loans per 100 proven savers a year at {inr(fee[1])} each, less than the {inr(a['fund_mid'] / a['saver_years'])} the fund pays on the same saver.", "page 2"),
        ("doc", "₹2.5 lakh fits only over 36 months", inr(emi36) + " EMI",
         f"needs about {inr(2 * emi36)} of monthly income under the 50% rule, with no other loan. 12 months never fits a ₹20–40k income.", "page 2"),
        ("jar", "Many savers must pay by UPI", f"{pct(upi_j)}–{pct(upi_a)}",
         "by year 3 (janta-like to every saver staying): one person collects cash from about 1,000 savers (400 a day, every 2.5 days).", "page 3"),
    ]
    cells = "".join(f'<div class="cc"><div class="ch">{V.svg(44, 44, V.icon(ic, 0, 0, 42, US))}<div class="ct">{t}</div></div>'
                    f'<div class="cn">{big}</div><div class="cs">{sub}</div><div class="cp">{pg}</div></div>' for ic, t, big, sub, pg in cards)
    nxt = ("1. Measure who is still saving at month 12 in the pilot; it decides everything.",
           "2. Compare savers the agent visits with UPI-only savers: does the visit keep them saving?",
           f"3. Give tele-sales and the AI team the target: {inr(cut)} a year of each agent's work.",
           "4. Raise what each loan earns: at 1% of ₹2.5 lakh, loans cannot carry the agent.")
    return (f'<div class="cgrid">{cells}</div><div class="next"><b>What to do next</b>'
            + "".join(f"<div>{x}</div>" for x in nxt) + '</div>')


# ---------- assumption pages ----------
def assume_book():
    rows = [
        ("Agent cost", "₹4,00,000 a year, all-in", "none", "You, 16 Oct", ["you"]),
        ("Sign-ups", "1,000 a year for 3 years, joining at the start of each month", "none", "You, 16 Oct", ["you"]),
        ("Collection", "every 2.5 days", "2–3 days", "You, 16 Oct", ["you"]),
        ("Collections one person makes", "400 a day", "200–400", "Arvinder's book: 200–400 customers, most visited most days (interview, 15 Oct)", ["int"]),
        ("Each saver puts in", "₹350 a day", "₹200–500", "Arvinder's customers: ₹200–500 a day; ₹350 is the middle", ["int"]),
        ("Who stays", "three views: everyone; janta-like (8 of 300 leave a month); app-like", "page 5", "you; Arvinder's 6–10 in and out a month; our model's evidence", ["you", "int", "ev"]),
        ("Deposit days", "240 a year (20 a month)", "none", "Bachatt: 2M fund purchases in Feb 2026 ÷ about 1 lakh daily savers", ["est"]),
        ("Money left in the fund", "half a year's deposits on average", "none", "janta accounts close when the term ends (Arvinder: 'the term finished')", ["jud"]),
        ("Savers' income", "₹20,000–40,000 a month", "none", "Arvinder's customers (interview, 15 Oct)", ["int"]),
        ("Loan rate for the EMI check", "26% a year", "22–30% in our lending model", "our lending model (tables/lmc_distributions.csv)", ["est"]),
        ("Loans offered", "after 6 months of saving", "none", "our model's rule: a proven saver has saved 6 months", ["jud"]),
    ]
    return '<div class="col">' + assume_table("", rows) + '</div>'


def survival_chart():
    w, h, x0, x1, y0, y1 = 540, 300, 44, 520, 30, 250
    X = lambda m: x0 + (x1 - x0) * (m - 1) / 35
    Y = lambda v: y1 - (y1 - y0) * v
    s = [V.text(0, 14, "OUT OF 100 WHO START, STILL SAVING IN MONTH…", 12.5, 700, US)]
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{RULE}"/>')
        s.append(V.text(x0 - 6, Y(v) + 4, f"{v * 100:.0f}", 11, 400, MUTED, "end"))
    for m in (1, 6, 12, 24, 36):
        s.append(V.text(X(m), y1 + 18, f"{m}", 11, 400, MUTED, "middle"))
    lo = [(int(r["month"]), float(r["still_saving_janta_worst"])) for r in SURV]
    hi = [(int(r["month"]), float(r["still_saving_janta_best"])) for r in SURV]
    band = " ".join(f"{'M' if i == 0 else 'L'}{X(m):.1f},{Y(v):.1f}" for i, (m, v) in enumerate(hi)) + " " + \
           " ".join(f"L{X(m):.1f},{Y(v):.1f}" for m, v in reversed(lo)) + " Z"
    s.append(f'<path d="{band}" fill="{THEM}" opacity="0.12"/>')
    lines = (("still_saving_breakeven", GOOD, "needed to break even", "7 5", (12, 36), -20),
             ("still_saving_janta_mid", THEM, "", "", (12, 36), 0),
             ("still_saving_evidence", US, "app-like: our evidence", "", (1, 3, 6, 12, 24, 36), 18))
    for key, c, lab, dash, marks, dy in lines:
        pts = [(int(r["month"]), float(r[key])) for r in SURV]
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(m):.1f},{Y(v):.1f}" for i, (m, v) in enumerate(pts))
        s.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="{dash}"/>')
        for m in marks:
            v = pts[m - 1][1]
            s.append(f'<circle cx="{X(m)}" cy="{Y(v)}" r="4.5" fill="{c}" stroke="#fff" stroke-width="2"/>')
            s.append(V.text(X(m) + (6 if m < 36 else -6), Y(v) - 8, f"{v * 100:.1f}", 11.5, 700, c, "start" if m < 36 else "end"))
        if lab:
            s.append(V.text(x1, Y(pts[-1][1]) + dy, lab, 11.5, 700, c, "end"))
    s.append(V.text(x1, 186, "Arvinder's book (line = middle;", 11.5, 700, THEM, "end"))
    s.append(V.text(x1, 200, "band = 6–10 of 200–400 leave a month)", 11.5, 700, THEM, "end"))
    s.append(V.text(x0, y1 + 36, "month", 11, 400, MUTED))
    return V.svg(w, h + 20, "".join(s))


def retention_table():
    sv = SURV[11]
    rows = [
        ("Our model, today's evidence (app-like)", "still saving at 12 / 24 / 36 months",
         f"{BE['evidence_m12'] * 100:.1f} / {BE['evidence_m24'] * 100:.1f} / {BE['evidence_m36'] * 100:.1f}", ["ev", "jud"]),
        ("Founder's view (tables/inputs.csv)", "of 100 who start, still saving after 1 / 2 years", "about 20 / 10", ["jud"]),
        ("SBI Jan Nivesh ₹250 daily SIP (NG-033)", "FY26 registrations stopped by 1 Apr 2026", "35.6%", ["ev"]),
        ("Chhoti SIP ₹250 (TB-04)", "share of the book closing in May 2026", "~8% a month", ["ev"]),
        ("Arvinder's janta book", "6–10 join and 6–10 leave a month, 200–400 customers: still saving after a year",
         f"{float(sv['still_saving_janta_worst']) * 100:.0f} / {float(sv['still_saving_janta_mid']) * 100:.0f} / {float(sv['still_saving_janta_best']) * 100:.0f}", ["int"]),
        ("Arvinder's janta book", "how long most customers have saved with him", "5+ years", ["int"]),
        ("Needed for the agent to break even", "still saving at 12 months", f"{BE['still_saving_m12'] * 100:.1f}", ["est"]),
    ]
    body = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="n">{c}</td><td>{" ".join(tag(k) for k in d)}</td></tr>' for a, b, c, d in rows)
    return ('<div class="tt">What we know about how long daily savers keep saving</div><table class="tbl at2">'
            '<colgroup><col style="width:29%"><col style="width:31%"><col style="width:24%"><col style="width:16%"></colgroup>'
            '<tr><th>Source</th><th>What it measures</th><th class="n">Value</th><th>How sure</th></tr>' + body + '</table>'
            '<div class="tn">Janta values: worst 10 of 200, middle 8 of 300, best 6 of 400 leaving a month, the same every month. '
            'App savers drop off fast; a daily visit may keep them. Only the pilot can tell which applies to us.</div>')


def assume_money():
    rows = [
        ("Fund commission", "0.20 / 0.35 / 0.50% a year on the balance", "low–high", "XB-04: regular minus direct fund costs (fund-house and adviser blogs)", ["weak"]),
        ("Other products", "₹8 / ₹63 / ₹259 a saver a year", "low–high", "XO-39: insurance, bills, recharge, pension, priced item by item", ["ev", "jud"]),
        ("Credit cards", "5% of sign-ups, one card each", "none", "You, 16 Oct", ["you"]),
        ("Card fee", "₹500 / ₹1,250 / ₹2,000 a card", "low–high", "BM-08: affiliate guides only", ["unv"]),
        ("Average loan", "₹2.5 lakh", "none", "You, 16 Oct", ["you"]),
        ("Our fee", "1% of each loan", "none", "You, 16 Oct (from our lender)", ["you"]),
        ("Fee taken back", "5% / 2.5% / 0% of fees", "low–high", "XL-13: lenders take it back if a loan closes or defaults within 6 months", ["ev"]),
        ("Loan funnel", "eligible 50%, apply 20%, approved 25% (middle)", "page 2", "XB-09, XL-42, LS-06, the founder's past lending data; middle matches XL-48", ["ev", "jud"]),
    ]
    return assume_table("Money coming in", rows)


def not_included():
    items = [
        ("coin", "worse", "GST on our fees", "If the lender's 1% includes 18% GST, we keep ₹2,119 of each ₹2,500. Check the contract."),
        ("doc", "worse", "Costs beyond the agent", "App, KYC (₹3 per Aadhaar e-KYC, REG-068), support and cash banking are not counted."),
        ("bank", "worse", "Cash rules for funds", "Fund money must come from the saver's own bank account (GIG-32); cash into funds is capped at ₹50,000 per fund house a year."),
        ("hands", "worse", "Agent ramp-up and churn", "Full output from month 1 is assumed. A new agent, or one who leaves, earns less."),
        ("phone", "risk", "Copying", "PhonePe already offers a ₹100-a-day deposit (since 6 Aug 2026). That hits retention."),
        ("broken", "risk", "Credit losses", "On referred loans the lender carries them, but high losses mean fewer approvals."),
    ]
    cls = {"worse": "bad", "risk": "warn"}
    cells = "".join(f'<div class="ni"><div class="ai">{V.svg(30, 30, V.icon(ic, 0, 0, 28, US))}</div><div><b>{t}</b> '
                    f'<span class="chip {cls[k]}" style="font-size:7.6pt;padding:0 6px">{"makes it worse" if k == "worse" else "risk"}</span><br>{d}</div></div>'
                    for ic, k, t, d in items)
    return f'<div class="tt">Not in these numbers</div><div class="nis">{cells}</div>'


EXTRA_CSS = f"""
.cgrid {{ display: grid; grid-template-columns: repeat(3, 1fr); grid-auto-rows: 1fr; gap: 8px; flex: 1; min-height: 0; }}
.cc {{ background: {V.PAPER}; border-radius: 12px; padding: 7px 11px; display: flex; flex-direction: column; gap: 3px; border-top: 5px solid {US}; }}
.ch {{ display: flex; align-items: center; gap: 8px; }} .ch svg {{ width: 34px; height: 34px; flex: none; }}
.ct {{ font-weight: 700; font-size: 10.5pt; line-height: 1.2; }}
.cn {{ font-size: 17pt; font-weight: 800; color: {US}; line-height: 1.1; }}
.cs {{ font-size: 9pt; line-height: 1.3; flex: 1; }}
.cp {{ font-size: 8pt; color: {MUTED}; }}
.next {{ margin-top: 8px; background: #f6efe7; border-radius: 12px; padding: 7px 14px; font-size: 9.4pt; display: grid; grid-template-columns: 100px 1fr 1fr 1fr 1fr; gap: 10px; align-items: center; }}
.tag {{ display: inline-block; font-size: 7.8pt; font-weight: 700; padding: 1px 7px; border-radius: 999px; margin: 1px 2px 1px 0; white-space: nowrap; }}
.tag.you {{ background: #e6eef7; color: {THEM}; }} .tag.int {{ background: {V.TINT['warn']}; color: {WARN}; }}
.tag.ev {{ background: {V.TINT['good']}; color: {GOOD}; }} .tag.weak {{ background: #eef2ea; color: #5b6b52; }}
.tag.est, .tag.jud {{ background: #ecebe8; color: {MUTED}; }} .tag.unv {{ background: {V.TINT['bad']}; color: {BAD}; }}
.at2 td {{ font-size: 8.8pt; line-height: 1.3; vertical-align: top; padding: 4px 5px; }}
.nis {{ display: grid; grid-template-columns: 1fr; gap: 6px; }}
.ni {{ display: flex; gap: 8px; align-items: flex-start; background: {V.PAPER}; border-radius: 10px; padding: 6px 9px; font-size: 8.8pt; line-height: 1.3; }}
.ni .ai {{ width: 24px; flex: none; }}
.g3 {{ grid-template-columns: 58% 1fr; }}
"""



def build():
    rate = step("approved loans")[0]
    fee = step("fee kept")[0]
    a, e = f("all_stay", "1-3"), f("evidence", "1-3")
    p0 = page(1, "Key conclusions · one street agent, ₹2.5 lakh loans at 1%, 3 years",
              f"One ₹4 lakh street agent covers {pct(a['covered_mid'])} of his 3-year cost if every saver stays, {pct(f('janta', '1-3')['covered_mid'])} at janta-like "
              f"retention and {pct(e['covered_mid'])} at app-like retention. Retention decides it; loans at 1% cannot.",
              conclusions(), "Every number here is worked out on the pages that follow; the last three pages list every assumption and how sure we are of it.")
    p1 = page(2, "Loan eligibility and yearly take-up · ₹2.5 lakh average loan, 1% fee",
              f"Of 100 savers who have saved 6+ months, about {100 * rate[1]:.1f} get a ₹2.5 lakh loan in a year, and each earns us {inr(fee[1])}.",
              f'<div class="grid g1"><div class="col">{funnel_flow()}</div><div class="col">{funnel_table()}{emi_table()}</div></div>',
              f"So loans earn about {inr(rate[1] * fee[1])} per proven saver a year, less than the fund commission on the same saver "
              f"({inr(a['fund_mid'] / a['saver_years'])} a year at ₹350 a day).")
    p2 = page(3, "One street agent over three years · everything included",
              f"With loans at 1% of ₹2.5 lakh, the agent covers {pct(a['covered_mid'])} of his cost if every saver stays, "
              f"{pct(f('janta', '1-3')['covered_mid'])} at janta-like retention and {pct(e['covered_mid'])} at app-like retention.",
              f'<div class="grid g1"><div class="col">{stacked()}{legend_table()}</div><div class="col">{result_table()}{year_rows()}</div></div>',
              f"Loans are the smallest income line. At janta-like retention the agent pays from year 3; taking "
              f"{inr(400000 - f('janta', '1-3')['affordable_agent_cost_a_year_mid'])} a year off his cost breaks even over 3 years.")
    src = "Sources: interview with Arvinder Singh, 15 Oct 2026; research and model tables named in each row. Built by model/agent_3yr.py and model/build_agent3_slides.py."
    p3 = page(4, "Key assumptions · 1 of 3", "The agent, his savers and the loan check: most of these are your figures or one interview.",
              f'<div class="grid" style="grid-template-columns:1fr;align-content:start">{assume_book()}</div>',
              "Five of eleven rest on a single interview. The next two calls should test the 200–400 book, ₹200–500 a day and ₹20–40k income.", src)
    p4 = page(5, "Key assumptions · 2 of 3 · how long savers keep saving",
              f"The agent breaks even only if about {BE['still_saving_m12'] * 100:.0f} of 100 savers are still saving after a year. "
              f"App evidence says {BE['evidence_m12'] * 100:.0f}; Arvinder's book implies {float(SURV[11]['still_saving_janta_mid']) * 100:.0f}.",
              f'<div class="grid g3"><div class="col">{survival_chart()}</div><div class="col">{retention_table()}</div></div>',
              "This is the one assumption that flips the answer. Measure it first.", src)
    p5 = page(6, "Key assumptions · 3 of 3 · money coming in, and what is left out",
              "Your figures set the loan and card income; the fund commission rests on weak evidence; six things are not counted.",
              f'<div class="grid g3"><div class="col">{assume_money()}</div><div class="col">{not_included()}</div></div>',
              "Everything left out makes the result worse or riskier, so the middle case is, if anything, generous.", src)
    css = CSS + EXTRA_CSS
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Street agent over 3 years</title><style>{css}</style></head><body>{p0}{p1}{p2}{p3}{p4}{p5}</body></html>'


def main():
    out = ROOT / "brief" / "qr_moat" / "agent3_slides.html"
    out.write_text(build())
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

"""The synthesized story (operator, 16 Oct 2026): "Whole game is that we are able to acquire and build a relationship
... better than any online model ... We need to synthesize better the story. It's too number driven."

Six story pages, one claim each, a picture each, one or two numbers each; the six detailed pages follow as an
appendix (A1-A6, from build_agent3_slides.py). Story numbers come only from tables/story_unit.csv,
story_unit_curve.csv, agent3_survival.csv, agent3_funnel.csv and agent3_years.csv.
Writes brief/qr_moat/story_deck.html and Street_vs_online_story.pdf.
"""
import csv
import subprocess
from pathlib import Path

import build_qr_visual as V
import build_agent3_slides as A3
from build_agent_slides import inr, pct

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
PDF = ROOT / "Street_vs_online_story.pdf"
U = {r["channel"]: r for r in csv.DictReader((T / "story_unit.csv").open())}
CURVE = list(csv.DictReader((T / "story_unit_curve.csv").open()))
SURV = list(csv.DictReader((T / "agent3_survival.csv").open()))
PT = {r["key"]: float(r["value"]) for r in csv.DictReader((T / "story_paytm.csv").open())}
SE = {r["id"]: r for r in csv.DictReader((ROOT / "research" / "story_evidence.csv").open())}
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD
APP, STREET = "#7a8796", US          # app = slate grey-blue, street = our brown


def u(ch, k):
    return float(U[ch][k])


def dots(x0, y0, kept, colour, size=11, gap=4):
    """100 savers as a 10 x 10 grid; the first `kept` are filled."""
    s = []
    for i in range(100):
        r, c = divmod(i, 10)
        cx, cy = x0 + c * (size + gap) + size / 2, y0 + r * (size + gap) + size / 2
        on = i < kept
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{size / 2}" fill="{colour if on else "#fff"}" stroke="{colour}" stroke-width="1.4"/>')
    return "".join(s)


# ---------- story pages ----------
def s1_picture():
    s = []
    for i, (ch, icon, name) in enumerate((("online", "phone", "An app"), ("street", "person", "Our street agent"))):
        x = i * 470
        col = APP if ch == "online" else STREET
        kept = round(u(ch, "still_saving_m12") * 100)
        s.append(f'<rect x="{x}" y="0" width="440" height="330" rx="16" fill="{V.PAPER}"/>')
        s.append(V.icon(icon, x + 20, 18, 44, col))
        s.append(V.text(x + 74, 40, name, 20, 800, INK))
        s.append(V.text(x + 74, 60, f"pays {inr(u(ch, 'cost_to_win'))} to win a saver", 13, 400, MUTED))
        s.append(dots(x + 24, 86, kept, col))
        s.append(V.text(x + 190, 120, f"{kept}", 46, 800, col))
        s.append(V.text(x + 190, 146, "of 100 still saving", 14, 700, INK))
        s.append(V.text(x + 190, 164, "after a year", 14, 700, INK))
        s.append(V.text(x + 190, 214, inr(u(ch, "cost_per_saver_still_saving_m12")), 30, 800, col))
        s.append(V.text(x + 190, 236, "for each saver", 13, 400, MUTED))
        s.append(V.text(x + 190, 252, "who stays", 13, 400, MUTED))
        verdict = ("earns back half its cost in 3 years" if ch == "online" else f"pays back in month {U[ch]['payback_month']}")
        s.append(V.badge(x + 220, 300, "bad" if ch == "online" else "good", verdict, 14))
    return V.svg(910, 334, "".join(s))


def s2_picture():
    marks = [(1, "start"), (3, "3 months"), (6, "6 months"), (12, "1 year"), (36, "3 years")]
    s = [V.icon("phone", 0, 8, 46, APP), V.text(56, 30, f"Pay {inr(u('online', 'cost_to_win'))}", 18, 800, INK),
         V.text(56, 50, "ads, installs, sign-up offers", 12.5, 400, MUTED)]
    for i, (m, lab) in enumerate(marks):
        v = 100.0 if m == 1 and lab == "start" else float(SURV[m - 1]["still_saving_evidence"]) * 100
        w = 7.6 * v
        y = 80 + i * 52
        s.append(f'<rect x="0" y="{y}" width="{w}" height="38" rx="6" fill="{APP}" opacity="{0.35 + 0.65 * v / 100}"/>')
        s.append(V.text(w + 10, y + 26, f"{v:.0f} of 100", 17, 800, INK))
        s.append(V.text(-8, y + 26, lab, 12.5, 600, MUTED, "end"))
    return f'<svg viewBox="-90 0 1000 350" width="100%" role="img">{"".join(s)}</svg>'


def s3_picture():
    s = []
    steps = [("person", "The agent visits", "every 2–3 days, at the counter"), ("hands", "The habit stays alive", "6–10 join, 6–10 leave a month"),
             ("jar", "The money moves to UPI", "over time; cash only where needed")]
    for i, (ic, t, sub) in enumerate(steps):
        x = i * 300
        s.append(f'<rect x="{x}" y="0" width="270" height="120" rx="14" fill="{V.PAPER}" stroke="{STREET}" stroke-width="1.5"/>')
        s.append(V.icon(ic, x + 16, 18, 46, STREET))
        s.append(V.text(x + 74, 40, t, 15.5, 800, INK))
        s.append(V.text(x + 74, 62, sub.split(", ")[0] if ", " in sub else sub, 12, 400, MUTED))
        if ", " in sub:
            s.append(V.text(x + 74, 78, sub.split(", ")[1], 12, 400, MUTED))
        if i < 2:
            s.append(V.arrow(x + 272, 60, x + 298, 60, MUTED, 2))
    kept = round(u("street", "still_saving_m12") * 100)
    s.append(f'<rect x="0" y="150" width="870" height="150" rx="14" fill="#f6efe7"/>')
    s.append(dots(24, 168, kept, STREET, 10, 3))
    s.append(V.text(170, 200, f"{kept} of 100", 34, 800, STREET))
    s.append(V.text(170, 222, "still saving after a year (Arvinder's book)", 13, 600, INK))
    s.append(V.text(170, 260, f"{inr(u('street', 'cost_to_win'))} to win each saver", 22, 800, STREET))
    s.append(V.text(170, 282, "₹4 lakh a year ÷ 1,000 sign-ups, collection included", 12.5, 400, MUTED))
    s.append(V.text(560, 200, "“Bank employees. They collect cash", 15, 700, INK))
    s.append(V.text(560, 220, "and have trust.”", 15, 700, INK))
    s.append(V.text(560, 244, "your note after the call, 15 Oct", 12, 400, MUTED))
    s.append(V.text(560, 276, "Most of his customers have saved", 12.5, 400, INK))
    s.append(V.text(560, 292, "with him for 5+ years.", 12.5, 400, INK))
    return V.svg(870, 304, "".join(s))


def s4_picture():
    w, h, x0, x1, y0, y1 = 900, 330, 60, 860, 20, 280
    vmax = 900
    X = lambda m: x0 + (x1 - x0) * (m - 1) / 35
    Y = lambda v: y1 - (y1 - y0) * v / vmax
    s = []
    for v in (0, 300, 600, 900):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{RULE}"/>')
        s.append(V.text(x0 - 8, Y(v) + 4, f"₹{v}", 12, 400, MUTED, "end"))
    for m in (1, 12, 24, 36):
        s.append(V.text(X(m), y1 + 20, f"month {m}", 12, 400, MUTED, "middle"))
    for ch, col in (("street", STREET), ("online", APP)):
        cac = u(ch, "cost_to_win")
        s.append(f'<line x1="{x0}" y1="{Y(cac)}" x2="{x1}" y2="{Y(cac)}" stroke="{col}" stroke-width="1.5" stroke-dasharray="6 5"/>')
        s.append(V.text(x0 + 6, Y(cac) - 6, f"{'An app' if ch == 'online' else 'Our street agent'}: cost to win {inr(cac)}", 12, 700, col))
    lines = (("street_paytm_fee", GOOD, "street, Paytm-like 4.5% loan fee", -12), ("street", STREET, "street, 1% loan fee", -12), ("online", APP, "an app", 24))
    for ch, col, lab, dy in lines:
        pts = [(int(r["month"]), float(r[ch])) for r in CURVE]
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(m):.1f},{Y(v):.1f}" for i, (m, v) in enumerate(pts))
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.5"/>')
        m, v = pts[-1]
        s.append(f'<circle cx="{X(m)}" cy="{Y(v)}" r="6" fill="{col}"/>')
        s.append(V.text(X(m) - 10, Y(v) + dy, f"{lab}: {inr(v)} in 3 years", 13.5, 800, col, "end"))
        if ch != "online":
            pay = int(U[ch]["payback_month"])
            s.append(f'<circle cx="{X(pay)}" cy="{Y(u(ch, "cost_to_win"))}" r="7" fill="#fff" stroke="{col}" stroke-width="3"/>')
            s.append(V.text(X(pay), Y(u(ch, "cost_to_win")) + 24, f"month {pay}", 12.5, 800, col, "middle"))
    return V.svg(w, h, "".join(s))


def s5_picture():
    rows = [("street_paytm_fee", "Street agent, Paytm-like 4.5% per loan", GOOD),
            ("street", "Street agent, 1% per loan", STREET),
            ("street_stress", "Street agent, savers drop off like an app's", "#b7835a"),
            ("online", "An app", APP)]
    s = [V.text(0, 16, "WHAT EACH ₹1 SPENT ON WINNING A SAVER EARNS BACK IN 3 YEARS", 12.5, 700, US)]
    x0, x1 = 330, 820
    X = lambda v: x0 + (x1 - x0) * v / 2.5
    s.append(f'<line x1="{X(1)}" y1="30" x2="{X(1)}" y2="236" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s.append(V.text(X(1), 252, "₹1: pays back", 12, 700, INK, "middle"))
    for i, (ch, lab, col) in enumerate(rows):
        y = 34 + i * 50
        v = u(ch, "value_per_rupee_of_cost")
        s.append(V.text(x0 - 12, y + 24, lab, 13, 700, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y + 6}" width="{X(v) - x0}" height="30" rx="5" fill="{col}"/>')
        s.append(V.text(X(v) + 8, y + 27, f"₹{v:.2f}", 15, 800, col))
    return V.svg(900, 258, "".join(s))


def s5_cards():
    j = A3.f("janta", "1-3")
    items = [("person", "1. Make the visit our till",
              f"The agent collects loan instalments on the same visit. Lenders who collect in person: self-help groups {float(SE['SE-01']['value']):.2f}% bad loans, "
              f"microfinance {float(SE['SE-02']['value']):.1f}% in a bad year; Paytm {PT['paytm_losses_low'] * 100:.1f}–{PT['paytm_losses_high'] * 100:.0f}%."),
             ("bank", "2. Earn like Paytm on each loan",
              f"Take part of the risk (RBI allows up to {float(SE['SE-04']['value']):.0f}% first-loss cover) to move from 1% to about 4.5% a loan. "
              f"A kept saver then pays back in month {U['street_paytm_fee']['payback_month']}; one agent covers {pct(PT['agent_covered_janta_paytm_fee'])} of 3 years."),
             ("phone", "3. Stay up to 12× cheaper to win",
              f"1,000 sign-ups a year per agent at {inr(u('street', 'cost_to_win'))} each; tele-sales and AI take {inr(400000 - j['affordable_agent_cost_a_year_mid'])} a year of work off him."),
             ("hands", "The bet underneath all three",
              f"The visit keeps about {round(u('street', 'still_saving_m12') * 100)} of 100 saving after a year. If savers drop off like an app's, we lose even with a cheap win.")]
    return '<div class="mt">' + "".join(f'<div class="mc"><div class="mi">{V.svg(40, 40, V.icon(ic, 0, 0, 38, US))}</div><div><b>{t}</b><br>{d}</div></div>' for ic, t, d in items) + '</div>'


def s6_picture():
    marks = [(0, "Month 0", "Hire one agent", "sign-ups and cost per sign-up", f"pass: 1,000 a year at about {inr(u('street', 'cost_to_win'))} each"),
             (1, "Month 6", "First proven savers", "loans, cards, instalments on the visit", "pass: take-up at our funnel, instalments collected on time"),
             (2, "Month 12", "Who is still saving?", "visited savers vs a UPI-only group", f"pass: about {round(u('street', 'still_saving_m12') * 100)} of 100 still saving, well above an app's {round(u('online', 'still_saving_m12') * 100)}")]
    s = [f'<line x1="40" y1="60" x2="860" y2="60" stroke="{STREET}" stroke-width="4"/>']
    for i, when, what, measure, passline in marks:
        x = 40 + i * 410
        s.append(f'<circle cx="{x}" cy="60" r="14" fill="{STREET}"/>')
        s.append(V.text(x, 66, str(i + 1), 14, 800, "#fff", "middle"))
        s.append(V.text(x, 30, when, 15, 800, STREET, "middle"))
        bx = max(0, min(x - 130, 640))
        s.append(f'<rect x="{bx}" y="90" width="260" height="150" rx="14" fill="{V.PAPER}"/>')
        s.append(V.text(bx + 14, 120, what, 16, 800, INK))
        s.append(V.text(bx + 14, 146, "Measure:", 12, 700, MUTED))
        s.append(V.text(bx + 14, 164, measure, 12.5, 400, INK))
        s.append(V.text(bx + 14, 194, passline.split(":")[0] + ":", 12, 700, GOOD))
        rest = passline.split(": ", 1)[1]
        words, line, lines = rest.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 34:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        for k, ln in enumerate(lines):
            s.append(V.text(bx + 14, 212 + k * 16, ln, 12.5, 600, GOOD))
    return V.svg(900, 250, "".join(s))


def s_paytm():
    head = [("phone", APP, "An app"), ("speaker", THEM, "Paytm: the closest to us"), ("person", STREET, "Our street agent")]
    th = "".join(f'<th><div class="ph">{V.svg(34, 34, V.icon(ic, 0, 0, 32, c))}<span style="color:{c}">{t}</span></div></th>' for ic, c, t in head)
    rows = [
        ("How he is won", "ads, installs, sign-up offers", "a field force at the shop", "an agent at the counter"),
        ("Cost to win him", inr(u("online", "cost_to_win")), f"up to ~{inr(PT['paytm_cost_to_win_upto'])} per device added", inr(u("street", "cost_to_win"))),
        ("What keeps him", "push notifications", f"a box on the counter: device shops held through the 2024 shock ({PT['paytm_devices_dec23_cr']:.2f} → {PT['paytm_devices_mar24_cr']:.2f} crore)",
         "the visit every 2–3 days"),
        ("What he pays every year", "nothing", f"{inr(PT['paytm_rent_a_year'])} in device rent ({inr(PT['paytm_rent_a_month'])} a month)",
         f"nothing; the fund and products pay us {inr(PT['our_income_per_saver_year'])}"),
        ("What one loan earns", "a referral fee", f"{inr(PT['paytm_fee_per_loan_low'])}–{inr(PT['paytm_fee_per_loan_high'])} (4.5–5% of {inr(PT['paytm_loan_ticket'])})",
         f"{inr(PT['our_fee_per_loan'])} (1% of ₹2.5 lakh)"),
        ("How it collects", "the borrower's bank account", f"from the shop's daily payout: losses {PT['paytm_losses_low'] * 100:.1f}–{PT['paytm_losses_high'] * 100:.0f}%", "the saver's bank account (UPI AutoPay)"),
    ]
    body = "".join(f'<tr><td class="rl">{a}</td><td>{b}</td><td>{c}</td><td class="us">{d}</td></tr>' for a, b, c, d in rows)
    strip = (f'<div class="pstrip"><div class="pg2 good">✓ <b>Our edge:</b> we win him for {inr(u("street", "cost_to_win"))}, '
             f'not up to {inr(PT["paytm_cost_to_win_upto"])} ({PT["paytm_cost_vs_ours"]:.1f}× less).</div>'
             f'<div class="pg2 bad">✕ <b>Our gap:</b> Paytm earns {PT["rent_vs_our_income"]:.1f}× more a year from each customer, and '
             f'{PT["paytm_fee_vs_ours_low"]:.1f}–{PT["paytm_fee_vs_ours_high"]:.1f}× more per loan.</div></div>')
    return (f'<div class="stack"><table class="ptab"><colgroup><col style="width:16%"><col style="width:22%"><col style="width:34%"><col style="width:28%"></colgroup>'
            f'<tr><th></th>{th}</tr>{body}</table>{strip}</div>')


def s0_scoreboard():
    head = [("speaker", THEM, "Paytm"), ("person", STREET, "Us, with a street agent")]
    th = "".join(f'<th><div class="ph">{V.svg(34, 34, V.icon(ic, 0, 0, 32, c))}<span style="color:{c}">{t}</span></div></th>' for ic, c, t in head)
    kept = round(u("street", "still_saving_m12") * 100)
    rows = [
        ("Round 1", "Win the shopkeeper", f"field force: up to ~{inr(PT['paytm_cost_to_win_upto'])} a device", f"agent: {inr(u('street', 'cost_to_win'))} a saver",
         "good", f"Us, up to {PT['paytm_cost_vs_ours']:.1f}× cheaper"),
        ("Round 2", "Keep him", "a box on the counter; held through the 2024 shock", f"the visit; Arvinder's janta book keeps {kept} of 100 a year", "warn", "Open: our pilot decides"),
        ("Round 3", "Earn from him", f"{inr(PT['paytm_rent_a_year'])} a year rent; {inr(PT['paytm_fee_per_loan_low'])}+ a loan, collected from the till",
         f"{inr(PT['our_income_per_saver_year'])} a year; {inr(PT['our_fee_per_loan'])} a loan", "bad", f"Paytm, {PT['rent_vs_our_income']:.0f}× more a year"),
    ]
    mark = {"good": "✓", "warn": "?", "bad": "✕"}
    body = "".join(f'<tr><td class="rl"><span class="rn">{a}</span><br>{b}</td><td>{c}</td><td class="us">{d}</td>'
                   f'<td><span class="chip {k}"><span>{mark[k]}</span>{e}</span></td></tr>' for a, b, c, d, k, e in rows)
    strip = (f'<div class="pstrip"><div class="pg2 good"><b>How we win round 3:</b> make the agent’s visit our till and earn a Paytm-like 4.5% a loan. '
             f'A kept saver then pays back in month {U["street_paytm_fee"]["payback_month"]}, and one agent covers {pct(PT["agent_covered_janta_paytm_fee"])} of his 3-year cost.</div>'
             f'<div class="pg2 bad"><b>What could stop us:</b> if our savers drop off like an app\'s ({round(u("online", "still_saving_m12") * 100)} of 100 a year), '
             f'the cheap win is wasted and Paytm wins every round.</div></div>')
    return (f'<div class="stack"><table class="ptab score"><colgroup><col style="width:18%"><col style="width:31%"><col style="width:27%"><col style="width:24%"></colgroup>'
            f'<tr><th></th>{th}<th>Who is ahead</th></tr>{body}</table>{strip}</div>')


def story_page(no, kicker, title, body, caption):
    return (f'<section class="slide"><div class="kick"><span class="pg">{no} / 7</span>{kicker}</div><h1>{title}</h1>'
            f'<div class="vis">{body}</div><div class="cap">{caption}</div>'
            f'<div class="foot">Same saver and products in both channels: ₹350 a day; fund commission, other products, cards and loans as in the appendix. '
            f'App cost to win ₹499 is our model\'s evidence (₹186–1,340: Groww, finance-app installs, Jar and Stable Money). Street ₹400 = your ₹4 lakh agent ÷ 1,000 '
            f'sign-ups a year. Built by model/story_unit.py → tables/story_unit.csv. Paytm figures: research/qr_moat.csv QM-06..22, XL-07, XB-08; in-person collection: research/story_evidence.csv SE-01..05. Detail and every assumption: appendix A1–A6.</div></section>')


STORY_CSS = """
.mt { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; width: 100%; margin-top: 10px; }
.mc { display: flex; gap: 8px; background: #f7f5f0; border-radius: 12px; padding: 9px 10px; font-size: 9.6pt; line-height: 1.35; }
.mi { width: 32px; flex: none; }
.stack { display: flex; flex-direction: column; width: 100%; align-items: stretch; }
.ptab { width: 100%; border-collapse: collapse; font-size: 10.5pt; }
.ptab th { text-align: left; padding: 6px 8px; border-bottom: 2px solid #1f2328; }
.ptab .ph { display: flex; align-items: center; gap: 8px; font-size: 12pt; font-weight: 800; }
.ptab .ph svg { width: 30px; height: 30px; }
.ptab td { padding: 8px 8px; border-bottom: 1px solid #e3ded4; vertical-align: top; line-height: 1.35; }
.ptab td.rl { font-weight: 700; color: #5b636c; }
.ptab td.us { background: #f6efe7; font-weight: 600; }
.pstrip { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }
.pg2 { border-radius: 12px; padding: 10px 14px; font-size: 11pt; line-height: 1.35; }
.pg2.good { background: #e6f2ea; color: #1d5a3c; } .pg2.bad { background: #f8e6e3; color: #8f1d12; }
.score td { font-size: 11.5pt; padding: 12px 8px; } .score .rn { font-size: 9pt; color: #5b636c; text-transform: uppercase; letter-spacing: .05em; }
.ptab .chip { display: inline-flex; align-items: center; gap: 6px; font-weight: 700; font-size: 10.5pt; padding: 2px 10px 2px 3px; border-radius: 999px; }
.ptab .chip span { display: inline-flex; width: 18px; height: 18px; border-radius: 50%; align-items: center; justify-content: center; color: #fff; font-size: 9pt; }
.ptab .chip.good { background: #e6f2ea; color: #2f6b4f; } .ptab .chip.good span { background: #2f6b4f; }
.ptab .chip.warn { background: #fbf1dc; color: #9a6700; } .ptab .chip.warn span { background: #9a6700; }
.ptab .chip.bad { background: #f8e6e3; color: #b42318; } .ptab .chip.bad span { background: #b42318; }
"""


def build():
    pages = [
        story_page(1, "The question",
                   "Can we beat Paytm at its own game? We can win the shopkeeper for far less. To beat Paytm, we must also keep him and earn like Paytm.",
                   s0_scoreboard(), "Paytm's game: win the shop on the street, keep it with something on the counter, earn rent and loan fees from it."),
        story_page(2, "Rounds 1 and 2: win and keep",
                   "We win the same saver for less than an app, and a janta-style visit keeps three times as many saving.",
                   s1_picture(), f"Apps lose three in four within a year; SBI's ₹250 daily SIP lost 35.6% of FY26's new savers within the year."),
        story_page(3, "Why the street keeps him",
                   "A collection agent keeps the habit alive. The visit is the product, and no app has it.",
                   s3_picture(), f"Each saver a street agent keeps for a year costs {inr(u('street', 'cost_per_saver_still_saving_m12'))}, about "
                   f"{u('online', 'cost_per_saver_still_saving_m12') / u('street', 'cost_per_saver_still_saving_m12'):.0f}× less than online."),
        story_page(4, "Round 3: earn",
                   "Paytm earns far more from each shopkeeper: it charges rent and collects its loans from the till.",
                   s_paytm(), "Our edge is the cheap win and the visit. Our gap is what each customer pays us."),
        story_page(5, "What a kept saver is worth",
                   f"A saver we keep pays back in {U['street']['payback_month']} months at a 1% loan fee, and in {U['street_paytm_fee']['payback_month']} months at a Paytm-like 4.5%. An app's never does.",
                   s4_picture(), "Most of it is the money he keeps saving. A Paytm-like loan fee is what turns a slow payback into a fast one."),
        story_page(6, "How we beat Paytm",
                   "Three moves win round 3, and all of them rest on one bet: the visit keeps savers.",
                   f'<div class="stack">{s5_picture()}{s5_cards()}</div>', "Cheaper to win, a visit that keeps and collects, and a Paytm-like fee: that is beating Paytm at its own game."),
        story_page(7, "The test",
                   "Run one agent for 12 months and measure three things.",
                   s6_picture(), f"If month 12 shows about {round(u('street', 'still_saving_m12') * 100)} of 100 still saving, we have an edge Paytm and the apps do not. If it shows {round(u('online', 'still_saving_m12') * 100)}, we do not."),
    ]
    orig = A3.page
    A3.page = lambda no, *a, **k: orig(f"A{no}", *a, **k)
    appendix = A3.build().split('<section class="slide">')[1:]
    A3.page = orig
    appx = "".join('<section class="slide">' + sec.split("</body>")[0] for sec in appendix)
    css = A3.CSS + A3.EXTRA_CSS + STORY_CSS
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Street vs online</title><style>{css}</style></head>'
            f'<body>{"".join(pages)}{appx}</body></html>')


def main():
    out = ROOT / "brief" / "qr_moat" / "story_deck.html"
    out.write_text(build())
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

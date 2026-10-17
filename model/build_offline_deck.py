"""The offline business model, told as one argument (operator, 16 Oct 2026: "Still the story is not too tight ...
We can increase the slides but the story has to flow and has to be tight ... We are building an offline business model").

Claim chain, one page each (each title follows from the one before):
  1 what we are building   2 the customer           3 why online fails      4 what keeps him: the visit
  5 how the model works    6 why it beats apps and Paytm                    7 one kept saver pays back
  8 one agent's book pays  9 what must be true (one real bet)               10 how we prove it
Appendix A1-A8: the detailed pages. Numbers come only from tables/ and research/ files named in each footer.
Writes brief/qr_moat/offline_deck.html and Offline_savings_business.pdf.
"""
import csv
import subprocess
from pathlib import Path

import build_qr_visual as V
import build_agent3_slides as A3
import build_story_deck as SD
from build_agent_slides import inr, pct

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
R = ROOT / "research"
PDF = ROOT / "Offline_savings_business.pdf"
IV = {r["id"]: r["answer"] for r in csv.DictReader((R / "interview_arvinder_2026-10-15.csv").open())}
MON = [r for r in csv.DictReader((T / "agent3_monthly.csv").open()) if r["view"] == "janta"]
INK, MUTED, RULE, THEM, US, GOOD, WARN, BAD = V.INK, V.MUTED, V.RULE, V.THEM, V.US, V.GOOD, V.WARN, V.BAD
u, U, PT, APP = SD.u, SD.U, SD.PT, SD.APP
TOTAL = 10
KEPT = round(u("street", "still_saving_m12") * 100)
APP_KEPT = round(u("online", "still_saving_m12") * 100)
J = A3.f("janta", "1-3")
CUT = 400000 - J["affordable_agent_cost_a_year_mid"]


def evd(id_):
    for p in list(R.glob("*.csv")) + list((ROOT / "janta_pipe").glob("*.csv")):
        for r in csv.reader(p.open()):
            if r and r[0] == id_:
                return r
    raise KeyError(id_)


EVD03 = evd("EVD-03")      # SHG-BLP 2.05% vs microfinance 8.72% (NABARD, Mar 2024)
SIZE22 = evd("SIZE-22")    # Maharashtra: 2 lakh+ daily collection agents, about 1 crore families


# ---------- new pictures ----------
def p_answer():
    steps = [("person", "WIN", "An agent signs him up at his shop", inr(u("street", "cost_to_win")) + " a saver",
              f"apps pay {inr(u('online', 'cost_to_win'))}; Paytm up to {inr(PT['paytm_cost_to_win_upto'])}"),
             ("hands", "KEEP", "The agent visits every 2–3 days", f"{KEPT} of 100", f"still saving after a year (apps: {APP_KEPT})"),
             ("bank", "EARN", "Loans, cards and insurance on the same relationship",
              f"month {U['street_paytm_fee']['payback_month']}–{U['street']['payback_month']}", "when a kept saver has paid back his cost")]
    s = []
    for i, (ic, tag, what, big, sub) in enumerate(steps):
        x = i * 305
        s.append(f'<rect x="{x}" y="0" width="280" height="300" rx="18" fill="{V.PAPER}"/>')
        s.append(f'<rect x="{x}" y="0" width="280" height="8" rx="4" fill="{US}"/>')
        s.append(V.text(x + 24, 46, tag, 15, 800, US))
        s.append(V.icon(ic, x + 200, 22, 56, US))
        s.append(V.text(x + 24, 104, what if len(what) < 30 else what[:what.rfind(" ", 0, 30)] + "|" + what[what.rfind(" ", 0, 30) + 1:], 15, 700, INK, lh=20))
        s.append(V.text(x + 24, 200, big, 34, 800, US))
        s.append(V.text(x + 24, 230, sub if len(sub) < 34 else sub[:sub.rfind(" ", 0, 34)] + "|" + sub[sub.rfind(" ", 0, 34) + 1:], 13, 400, MUTED, lh=17))
        if i < 2:
            s.append(V.arrow(x + 282, 150, x + 303, 150, MUTED, 2.5))
    return V.svg(890, 304, "".join(s))


def p_customer():
    s = []
    for i in range(8):
        s.append(f'<rect x="{10 + i * 40}" y="10" width="40" height="30" fill="{US if i % 2 == 0 else "#f0e4d6"}"/>')
    s.append(f'<rect x="18" y="40" width="304" height="110" fill="{V.PAPER}"/>')
    s.append(V.icon("person", 60, 66, 70, "#9b8f7d"))
    s.append(V.icon("person", 200, 72, 64, US))
    s.append(V.text(232, 160, "the janta agent", 12, 700, US, "middle"))
    s.append(f'<rect x="10" y="150" width="320" height="90" rx="6" fill="#e9e3d8" stroke="#d6cdbd"/>')
    s.append(V.icon("coin", 40, 168, 40, US))
    s.append(V.icon("doc", 96, 168, 40, THEM))
    s.append(V.text(170, 196, "cash + passbook,", 13, 700, INK))
    s.append(V.text(170, 214, "every day", 13, 700, INK))
    facts = [("coin", f"Saves {IV['IV-03'].replace('Rs ', '₹').replace(' to ', '–')} a day, in cash, with a janta agent", "interview"),
             ("phone", f"{IV['IV-06'].replace(' or ', '–')} in 10 have UPI, yet {IV['IV-07'].replace(' or more', '+')} of every ₹100 he saves comes in cash: “{IV['IV-08'].lower()}”", "interview"),
             ("bank", f"Asks his agent about loans and insurance; earns {IV['IV-04'].replace('Rs ', '₹').replace(' to ', '–')} a month", "interview"),
             ("hands", "Maharashtra alone: 2 lakh+ daily-collection agents serving about 1 crore families", "SIZE-22")]
    for i, (ic, t, src) in enumerate(facts):
        y = 8 + i * 62
        s.append(V.icon(ic, 370, y + 4, 36, US))
        words, line, lines = t.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 58:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        for k, ln in enumerate(lines):
            s.append(V.text(420, y + 20 + k * 18, ln, 14, 600 if k == 0 else 400, INK))
        s.append(V.text(420, y + 20 + len(lines) * 18, src, 10.5, 400, MUTED))
    return V.svg(900, 250, "".join(s))


def p_loop():
    nodes = [(0, 0, "person", "Sign him up at his shop", f"KYC and a savings mandate: {inr(u('street', 'cost_to_win'))}"),
             (300, 0, "hands", "Visit every 2–3 days", "collect, remind, answer questions"),
             (600, 0, "jar", "His money, in his name", "his bank account, then his fund"),
             (600, 150, "phone", "Move him to UPI", "frees the agent's visits"),
             (300, 150, "bank", "After 6 months: credit", "loans, cards, insurance via partners"),
             (0, 150, "coin", "Collect on the visit", "instalments: the visit is our till")]
    s = []
    for x, y, ic, t, sub in nodes:
        s.append(V.node(x, y, 262, 74, ic, US, t, sub, US if ic in ("hands", "coin") else None))
    s.append(V.arrow(264, 37, 298, 37))
    s.append(V.arrow(564, 37, 598, 37))
    s.append(V.arrow(731, 76, 731, 148))
    s.append(V.arrow(598, 187, 564, 187))
    s.append(V.arrow(298, 187, 264, 187))
    s.append(f'<path d="M131,148 C131,110 400,110 420,78" fill="none" stroke="{US}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(f'<path d="M420,78 l-9,3 l5,-8 z" fill="{US}"/>')
    s.append(V.text(300, 140, "back to the next visit", 12, 700, US, "middle"))
    s.append(f'<rect x="0" y="252" width="862" height="64" rx="14" fill="#e6eef7"/>')
    s.append(V.icon("phone", 14, 262, 42, THEM))
    s.append(V.text(66, 280, "Behind every agent: tele-sales and an AI agent", 15, 800, THEM))
    s.append(V.text(66, 302, f"missed-debit follow-ups, the switch to UPI, loan pre-checks: about {inr(CUT)} a year of his work", 13, 400, INK))
    return V.svg(864, 320, "".join(s))


def p_agent_book():
    w, x0, x1, y0, y1 = 900, 50, 520, 20, 230
    X = lambda m: x0 + (x1 - x0) * (m - 1) / 35
    Y = lambda v: y1 - (y1 - y0) * v / 2000
    s = [V.text(0, 12, "SAVERS IN ONE AGENT'S BOOK (JANTA-LIKE RETENTION)", 12, 700, US)]
    for v in (0, 1000, 2000):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{RULE}"/>')
        s.append(V.text(x0 - 6, Y(v) + 4, f"{v:,}", 11, 400, MUTED, "end"))
    pts = [(int(r["month"]), float(r["active"])) for r in MON]
    d = " ".join(f"{'M' if i == 0 else 'L'}{X(m):.1f},{Y(v):.1f}" for i, (m, v) in enumerate(pts))
    s.append(f'<path d="{d}" fill="none" stroke="{US}" stroke-width="3.5"/>')
    for m in (12, 24, 36):
        v = pts[m - 1][1]
        s.append(f'<circle cx="{X(m)}" cy="{Y(v)}" r="5.5" fill="{US}" stroke="#fff" stroke-width="2"/>')
        s.append(V.text(X(m), Y(v) - 12, f"{v:,.0f}", 13, 800, US, "middle"))
        s.append(V.text(X(m), y1 + 18, f"year {m // 12}", 12, 400, MUTED, "middle"))
    # yearly result bars
    bx0, bx1, base = 600, 890, 130
    vmax = 320000
    Yb = lambda v: base - 100 * v / vmax
    s.append(V.text(bx0, 12, "AFTER HIS ₹4 LAKH COST, EACH YEAR", 12, 700, US))
    s.append(f'<line x1="{bx0}" y1="{base}" x2="{bx1}" y2="{base}" stroke="{INK}" stroke-width="1.2"/>')
    for i in range(3):
        v = A3.f("janta", i + 1)["result_mid"]
        x = bx0 + 20 + i * 95
        top, hgt = (Yb(v), base - Yb(v)) if v >= 0 else (base, Yb(v) - base)
        s.append(f'<rect x="{x}" y="{top}" width="60" height="{max(hgt, 2)}" rx="4" fill="{GOOD if v >= 0 else BAD}"/>')
        lab = ("+" if v >= 0 else "−") + inr(abs(v))
        s.append(V.text(x + 30, (top - 8) if v >= 0 else (top + hgt + 16), lab, 12.5, 800, GOOD if v >= 0 else BAD, "middle"))
        s.append(V.text(x + 30, 252, f"year {i + 1}", 12, 400, MUTED, "middle"))
    return V.svg(w, 262, "".join(s))


def p_bets():
    cards = [("hands", "warn", "The bet", "Savers keep saving",
              f"{KEPT} of 100 still saving after a year, as in Arvinder's book; apps manage {APP_KEPT}. One interview says yes. Only the pilot can prove it."),
             ("bank", "good", "Negotiate", "Each loan earns like Paytm's",
              f"About 4.5% a loan instead of 1%: collect instalments on the visit and share first losses (RBI allows up to 5%). "
              f"Savings-linked group loans already repay better: 2.05% bad loans vs 8.72% in microfinance (NABARD)."),
             ("phone", "good", "Operate", "One agent does more",
              f"1,000 sign-ups a year; about half his savers on UPI by year 3; tele-sales and AI take {inr(CUT)} a year of work off him.")]
    out = []
    for ic, kind, chip, title, body in cards:
        out.append(f'<div class="bc {kind}"><div class="bh">{V.svg(46, 46, V.icon(ic, 0, 0, 44, US))}'
                   f'<span class="chip {kind}"><span>{"!" if kind == "warn" else "✓"}</span>{chip}</span></div>'
                   f'<div class="bt">{title}</div><div class="bb">{body}</div></div>')
    return '<div class="bets">' + "".join(out) + '</div>'


CSS_EXTRA = """
.bets { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; width: 100%; }
.bc { background: #f7f5f0; border-radius: 16px; padding: 16px 18px; border-top: 6px solid #9a6700; }
.bc.good { border-top-color: #2f6b4f; }
.bh { display: flex; align-items: center; justify-content: space-between; }
.bh svg { width: 44px; height: 44px; }
.bc .chip { display: inline-flex; align-items: center; gap: 6px; font-weight: 800; font-size: 11pt; padding: 3px 12px 3px 4px; border-radius: 999px; }
.bc .chip span { display: inline-flex; width: 20px; height: 20px; border-radius: 50%; align-items: center; justify-content: center; color: #fff; font-size: 10pt; }
.bc .chip.warn { background: #fbf1dc; color: #9a6700; } .bc .chip.warn span { background: #9a6700; }
.bc .chip.good { background: #e6f2ea; color: #2f6b4f; } .bc .chip.good span { background: #2f6b4f; }
.bt { font-size: 15pt; font-weight: 800; margin: 12px 0 6px; }
.bb { font-size: 11pt; line-height: 1.45; }
"""


CAC_BASIS = next(r for r in csv.reader((T / "distributions.csv").open()) if r and r[0] == "cac_target" and r[1] == "gig")[-2]
assert "Groww Rs 796-1,374 with 83% organic" in CAC_BASIS and "CPI Rs 100-300" in CAC_BASIS and "Rs 249" in CAC_BASIS


def p_problem():
    s = [V.text(0, 14, "HOW AN APP WINS A DAILY SAVER, AND WHAT IT COSTS", 12.5, 700, US)]
    chain = [("phone", "Ads and installs", "₹100–300 an install"), ("doc", "Sign-up", "many never save"),
             ("coin", f"{inr(u('online', 'cost_to_win'))} a saver", "who starts saving"),
             ("broken", f"{APP_KEPT} of 100", "still saving after a year")]
    for i, (ic, t, sub) in enumerate(chain):
        x = i * 150
        hl = i >= 2
        s.append(f'<rect x="{x}" y="30" width="136" height="150" rx="14" fill="{V.TINT["bad"] if i == 3 else V.PAPER}" stroke="{BAD if i == 3 else (US if hl else RULE)}" stroke-width="{2 if hl else 1}"/>')
        s.append(V.icon(ic, x + 46, 44, 44, BAD if i == 3 else (US if hl else APP)))
        s.append(V.text(x + 68, 118, t, 14.5 if i < 2 else 17, 800, BAD if i == 3 else INK, "middle"))
        s.append(V.text(x + 68, 140, sub, 11.5, 400, MUTED, "middle"))
        if i < 3:
            s.append(V.arrow(x + 138, 105, x + 148, 105, MUTED, 2))
    s.append(f'<rect x="0" y="200" width="586" height="96" rx="14" fill="{V.TINT["bad"]}"/>')
    s.append(V.text(24, 238, inr(u("online", "cost_per_saver_still_saving_m12")), 34, 800, BAD))
    s.append(V.text(24, 264, "for each saver still saving after a year", 14, 700, BAD))
    s.append(V.text(320, 236, f"and he earns back only {inr(u('online', 'value_36m'))}", 14, 700, INK))
    s.append(V.text(320, 256, "in his first 3 years: the app", 14, 400, INK))
    s.append(V.text(320, 276, "never recovers what it paid", 14, 400, INK))
    ev = [("Groww", "₹796–1,374 a customer, with 83% coming free"), ("Finance-app installs", "₹100–300 each"),
          ("Jar, Stable Money", "₹249 a saver, only if half of sign-ups save"), ("SBI's ₹250 daily SIP", "lost 35.6% of FY26's new savers within the year")]
    s.append(V.text(626, 14, "WHAT THE EVIDENCE SAYS", 12.5, 700, US))
    for i, (who, what) in enumerate(ev):
        y = 34 + i * 66
        s.append(f'<rect x="626" y="{y}" width="274" height="56" rx="10" fill="{V.PAPER}"/>')
        s.append(V.text(640, y + 22, who, 13, 800, INK))
        s.append(V.text(640, y + 42, what, 12, 400, MUTED))
    return V.svg(900, 300, "".join(s))


def p_hypothesis():
    rows = [("H1", "Win him offline for less", "person",
             f"{inr(u('street', 'cost_to_win'))} a saver", "one agent: ₹4 lakh a year, 1,000 sign-ups", f"online: {inr(u('online', 'cost_to_win'))}"),
            ("H2", "Build a relationship that keeps him saving", "hands",
             f"{KEPT} of 100", "still saving after a year, as in a janta book", f"online: {APP_KEPT} of 100"),
            ("H3", "Earn from that relationship", "bank",
             f"month {U['street']['payback_month']}", f"when he has paid back his cost (month {U['street_paytm_fee']['payback_month']} with a Paytm-like loan fee)",
             "online: never, in 3 years")]
    s = []
    for i, (h, t, ic, big, sub, vs) in enumerate(rows):
        x = i * 300
        s.append(f'<rect x="{x}" y="0" width="282" height="300" rx="18" fill="{V.PAPER}"/>')
        s.append(f'<rect x="{x}" y="0" width="282" height="8" rx="4" fill="{US}"/>')
        s.append(f'<circle cx="{x + 36}" cy="46" r="20" fill="{US}"/>')
        s.append(V.text(x + 36, 52, h, 14, 800, "#fff", "middle"))
        s.append(V.icon(ic, x + 212, 24, 48, US))
        words, line, lines = t.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 24:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        for k, ln in enumerate(lines):
            s.append(V.text(x + 20, 102 + k * 22, ln, 17, 800, INK))
        s.append(V.text(x + 20, 190, big, 30, 800, US))
        words, line, lines = sub.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 36:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        for k, ln in enumerate(lines):
            s.append(V.text(x + 20, 214 + k * 16, ln, 12, 400, MUTED))
        s.append(f'<rect x="{x + 20}" y="258" width="242" height="28" rx="14" fill="{V.TINT["bad"]}"/>')
        s.append(V.text(x + 141, 277, vs, 12.5, 700, BAD, "middle"))
    return V.svg(882, 304, "".join(s))


def page(no, kicker, title, body, caption, src):
    return (f'<section class="slide"><div class="kick"><span class="pg">{no} / {TOTAL}</span>{kicker}</div><h1>{title}</h1>'
            f'<div class="vis">{body}</div><div class="cap">{caption}</div><div class="foot">{src}</div></section>')


def build():
    base = ("Same saver in every comparison: ₹350 a day; fund commission, other products, cards and loans as in appendix A6. "
            "App cost to win ₹499: our model's evidence (Groww, finance-app installs, Jar, Stable Money). Street ₹400: your ₹4 lakh agent ÷ 1,000 sign-ups a year.")
    pages = [
        page(1, "The problem",
             f"Winning a daily saver online costs {inr(u('online', 'cost_to_win'))}. Keeping one for a year costs {inr(u('online', 'cost_per_saver_still_saving_m12'))}.",
             p_problem(), "Online, this customer is cheap to reach but expensive to keep: three in four stop within a year.",
             "Cost to win: tables/distributions.csv cac_target (TB-18..22, TB-37, TB-38, BM-04, BM-05), ₹186–1,340 range, ₹499 middle. Retention: our model's evidence; "
             "SBI daily SIP: NG-033. Value: tables/story_unit.csv. " + base),
        page(2, "Our hypothesis",
             "Our hypothesis: offline, we can win this customer for less, and build a relationship that keeps him saving and borrowing.",
             p_hypothesis(), "Each of the three is tested in the pilot (page 10). The pages in between show why we believe them.",
             base),
        page(3, "Our customer",
             "Our customer already saves every day, in cash, with someone he trusts.",
             p_customer(), "The habit and the trust already exist. What is missing is a better home for the money, and credit.",
             "Interview with Arvinder Singh, a janta agent in Bareilly, 15 Oct 2026 (research/interview_arvinder_2026-10-15.csv). "
             "Maharashtra count: SIZE-22 (Indian Cooperative 2025-26; PIB, Ministry of Cooperation 2025); no national count exists."),
        page(4, "H2: the relationship",
             "What keeps him is the visit: a janta-style agent keeps three times as many saving.",
             SD.s1_picture(), f"Most of Arvinder's customers have saved with him for {IV['IV-11'].lower()}. "
             f"Each saver kept for a year costs us {inr(u('street', 'cost_per_saver_still_saving_m12'))}, about "
             f"{u('online', 'cost_per_saver_still_saving_m12') / u('street', 'cost_per_saver_still_saving_m12'):.0f}× less than online.",
             "Janta-like retention: Arvinder's book gains and loses 6–10 a month on 200–400 customers (interview). " + base),
        page(5, "How the model works",
             "So we build the business around the visit: sign up, visit, move to UPI, lend, and collect on the same visit.",
             p_loop(), "One person, one relationship: the agent who keeps him saving is the one who collects his loan.",
             "The cash rules shape the loop: fund money must come from the saver's own bank account (GIG-32); cash into funds is capped at ₹50,000 per fund house a year."),
        page(6, "H1 and H2 against the best offline player",
             "This beats apps and Paytm where it is hardest, winning and keeping him. Paytm still earns more from each customer, for now.",
             SD.s0_scoreboard(), "Paytm's game: win the shop on the street, keep it with a box on the counter, earn rent and loan fees from it.",
             "Paytm: research/qr_moat.csv QM-06..22, XL-07, XB-08 (cost to win is an upper bound that includes servicing). " + base),
        page(7, "H3: earning from the relationship",
             f"One kept saver pays back his cost in {U['street']['payback_month']} months, or {U['street_paytm_fee']['payback_month']} if each loan earns like Paytm's.",
             SD.s4_picture(), "Most of the value is the money he keeps saving. A Paytm-like loan fee is what makes payback fast.",
             "Built by model/story_unit.py → tables/story_unit.csv. Loans: 2.5 per 100 proven savers a year, ₹2.5 lakh at 1% (4.5% in the Paytm-like case). " + base),
        page(8, "One agent's book",
             f"One agent's book grows to about {float(A3.YR[('janta', '1-3')]['active_end']):,.0f} savers in three years and turns profitable in year 3.",
             p_agent_book(), f"Over all three years he covers {pct(J['covered_mid'])} of his cost; {inr(CUT)} a year of support, or a Paytm-like loan fee "
             f"({pct(PT['agent_covered_janta_paytm_fee'])} covered), closes the gap.",
             "One agent: ₹4 lakh a year, 1,000 sign-ups a year, collection every 2.5 days; janta-like retention; middle case (appendix A3)."),
        page(9, "What must be true",
             "Three things must be true, and only one is a real bet: that savers keep saving.",
             p_bets(), "The other two are things we can negotiate and run. Retention we can only measure.",
             f"EVD-03: NABARD, Status of Microfinance in India 2023-24: {EVD03[3]} (March 2024). RBI first-loss cap: SE-04. Agent support target: appendix A3."),
        page(10, "How we test the hypothesis",
             "We test all three parts with one agent in 12 months.",
             SD.s6_picture(), f"If month 12 shows about {KEPT} of 100 still saving, the hypothesis holds. If it shows {APP_KEPT}, it does not.",
             "Pass lines come from the model: cost to win (H1), janta-like retention (H2, appendix A5), the loan funnel (H3, appendix A2)."),
    ]
    # appendix: the six detailed pages, plus the Paytm table and the ₹1-earns-back chart
    orig = A3.page
    A3.page = lambda no, *a, **k: orig(f"A{no}", *a, **k)
    secs = A3.build().split('<section class="slide">')[1:]
    A3.page = orig
    appx = "".join('<section class="slide">' + sec.split("</body>")[0] for sec in secs)
    appx += page("A7", "Appendix · the closest model in detail", "Paytm against an app and our street agent, line by line.", SD.s_paytm(),
                 "Our edge is the cheap win and the visit. Our gap is what each customer pays us.", "research/qr_moat.csv QM-06..22, XL-07, XB-08. " + base)
    appx += page("A8", "Appendix · what each ₹1 earns back", "What each ₹1 spent on winning a saver earns back in 3 years.",
                 f'<div class="stack">{SD.s5_picture()}</div>', "If savers drop off like an app's, the street loses too.", "tables/story_unit.csv. " + base)
    css = A3.CSS + A3.EXTRA_CSS + SD.STORY_CSS + CSS_EXTRA
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Offline savings business</title><style>{css}</style></head><body>{"".join(pages)}{appx}</body></html>'


def main():
    out = ROOT / "brief" / "qr_moat" / "offline_deck.html"
    out.write_text(build())
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", out.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {out}\nwrote {PDF}")


if __name__ == "__main__":
    main()

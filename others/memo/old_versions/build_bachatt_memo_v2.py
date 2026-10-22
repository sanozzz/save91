"""Co-founder memo v2 to Piyush, built on the operator's Bachatt Model slide (19 Oct 2026).
Operator: "In the memo also define the pdf slide that I have the bachatt model. That slide defines Bachatt now which
makes the entry clear and future contested."
Structure: the slide = Bachatt now -> the ✓ squares = entry (table stakes) -> the ✗ squares + offline = the contested
future -> the economics that decide it -> the challenger's version of the same slide -> gates, pilot, decisions.
Every number cites a research row ID; "our estimate" / "to verify" where not sourced. Builds Bachatt_teardown_memo.pdf."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAVY, INK, MUTED, RULE = "#1f3a5f", "#1f2328", "#6b7280", "#e5e7eb"
ACQ, RET, SER = "#2563eb", "#7c3aed", "#059669"
GREEN, RED, AMBER, BLUE = "#15803d", "#b91c1c", "#b45309", "#1f64a8"

PER_USER = 50e7 / 3_000_000        # BAC-04 / BAC-02, ≈ ₹167
AVG_BAL = 350 * 20 * 12 / 2        # illustrative committed saver, our estimate (₹42,000)


def inr(x, d=0):
    whole = f"{abs(x):.{d}f}"
    w, _, frac = whole.partition(".")
    if len(w) > 3:
        head, tail = w[:-3], w[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        w = head + "," + tail
    return ("−" if x < 0 else "") + "₹" + w + (("." + frac) if frac else "")


# ---------- the slide (Bachatt now), optionally annotated ----------
BACHATT = {
    "ACQUISITION": (ACQ, [("✓", "Savings product through debt funds", "stake"), ("✓", "Online acquisition", "stake"),
                          ("✗", "Offline acquisition", "wedge"), ("✓", "Low-ticket entry (~₹250)", "stake"),
                          ("✓", "→ Digital loans through DSA", "stake")]),
    "RETENTION": (RET, [("✓", "Financial products (MF, Insta Fund, Gold/Silver)", "stake"),
                        ("✗", "Wallet-like: save in / withdraw out", "contest"),
                        ("✓", "Daily / flexible SIP for irregular incomes", "stake"), ("✓", "No lock-in, instant withdraw", "stake")]),
    "SERVICING": (SER, [("✗", "① AI financial planning", "contest"), ("✓", "② Lean DSA + digital", "stake"),
                        ("✓", "③ Loans on book (to verify, XL-12)", "contest"), ("✗", "④ 3-month EMI + gold loan", "contest")]),
}
TAG = {"stake": ("TABLE STAKES", "#e7f5ec", GREEN), "contest": ("CONTESTED", "#fdeceb", RED), "wedge": ("OUR WEDGE", "#fff4e0", AMBER)}


def slide(annotate=False, data=BACHATT, title="Bachatt Model", sub="Acquisition + Retention + Servicing",
          footer="Vision → go-to financial planning app / wallet (save in, withdraw out, finance purchases)",
          footer2="Power move: own the customer relationship + money flows → EMI on products deepens habit and data"):
    cols = []
    for name, (col, items) in data.items():
        rows = ""
        for mark, txt, kind in items:
            mc = GREEN if mark == "✓" else RED
            tag = ""
            if annotate:
                lab, bg, fg = TAG[kind]
                tag = f'<span class="stag" style="background:{bg};color:{fg}">{lab}</span>'
            rows += f'<div class="srow"><span class="smark" style="color:{mc}">{mark}</span><span class="stxt">{txt}</span>{tag}</div>'
        cols.append(f'<div class="scol"><div class="shead" style="background:{col}">{name}</div>{rows}</div>')
    legend = '<div class="slegend"><span style="color:#15803d">✓ Built / live</span><br><span style="color:#b91c1c">✗ Vision / not built</span></div>'
    return (f'<div class="slide"><div class="stop"><div><div class="stitle">{title}</div><div class="ssub">{sub}</div></div>{legend}</div>'
            f'<div class="scols">{"".join(cols)}</div><div class="sfoot"><b>{footer}</b><br><span>{footer2}</span></div></div>')


CHALLENGER = {
    "ACQUISITION": (ACQ, [("✓", "Savings through debt funds: match Bachatt", "stake"),
                          ("✓", "Online and OFFLINE: assisted, local agents serve cash earners", "wedge"),
                          ("✓", "Low ticket; cash first, then UPI", "stake"),
                          ("✓", "→ Loans: partner first, then risk-share, then own book", "contest")]),
    "RETENTION": (RET, [("✓", "Same product shelf (funds, not digital gold)", "stake"),
                        ("✓", "Habit from a person: a visit every few days plus the app", "wedge"),
                        ("✓", "Save in / withdraw out on fund rails (within instant-redemption limits)", "contest"),
                        ("✓", "Daily SIP; never hold customer money", "stake")]),
    "SERVICING": (SER, [("✓", "AI planning delivered through the agent (AI + human)", "contest"),
                        ("✓", "Collections as a capability: the agent knows the borrower", "wedge"),
                        ("✓", "Credit judged on the savings record → own book when earned", "contest"),
                        ("✓", "Gold loans and EMI through partners, with doorstep gold checks", "contest")]),
}


def ex_value():
    import math
    rows = [("Bachatt today: trail on ~" + inr(PER_USER) + " per user", PER_USER * 0.0035, "a year", NAVY, "0.2–0.5% a year on debt funds (XB-04); ₹50 crore ÷ 30 lakh users (BAC-02/04)"),
            ("A committed ₹350-a-day saver (~" + inr(AVG_BAL) + " held)", AVG_BAL * 0.0035, "a year", NAVY, f"{inr(AVG_BAL * .002)}–{inr(AVG_BAL * .005)}; liquid fund only ~8 bp (REG-039)"),
            ("One personal loan (₹58,522) via DSA", 58522 * 0.02, "once", AMBER, "1–2.5% of the loan (XL-13); average ticket (XL-29)"),
            ("The same loan if we collect and share risk", 58522 * 0.0475, "once", AMBER, "4.5–5% (Paytm-style; SE-05, XB-07)")]
    x0, x1, top, gap = 320, 760, 30, 50
    lo, hi = math.log10(0.1), math.log10(10000)
    X = lambda v: x0 + (x1 - x0) * (math.log10(max(v, .1)) - lo) / (hi - lo)
    s = [f'<text x="0" y="14" font-size="11.5" font-weight="700" fill="{NAVY}">WHAT ONE USER IS WORTH (₹, LOG SCALE)</text>']
    for v in (1, 10, 100, 1000, 10000):
        s.append(f'<line x1="{X(v)}" y1="{top - 6}" x2="{X(v)}" y2="{top + gap * 4 - 12}" stroke="{RULE}"/>'
                 f'<text x="{X(v)}" y="{top + gap * 4}" font-size="10" fill="{MUTED}" text-anchor="middle">{inr(v)}</text>')
    for i, (lab, v, per, col, note) in enumerate(rows):
        y = top + i * gap
        s.append(f'<text x="0" y="{y + 14}" font-size="11.5" font-weight="700" fill="{INK}">{lab}</text>'
                 f'<text x="0" y="{y + 30}" font-size="9.3" fill="{MUTED}">{note}</text>'
                 f'<rect x="{x0}" y="{y + 2}" width="{max(X(v) - x0, 3)}" height="20" rx="4" fill="{col}"/>'
                 f'<text x="{X(v) + 6}" y="{y + 17}" font-size="12" font-weight="800" fill="{col}">{inr(v, 1 if v < 10 else 0)} {per}</text>')
    return f'<svg viewBox="0 0 820 {top + gap * 4 + 6}" width="100%" font-family="Helvetica, Arial, sans-serif">{"".join(s)}</svg>'


CSS = f"""
@page {{ size: A4; margin: 15mm 14mm; }}
body {{ font-family: Helvetica, Arial, sans-serif; color: {INK}; font-size: 10.3pt; line-height: 1.42; }}
h1 {{ color: {NAVY}; font-size: 19pt; margin: 0 0 2px; }}
h2 {{ color: {NAVY}; font-size: 13.5pt; margin: 14px 0 6px; border-bottom: 2px solid {NAVY}; padding-bottom: 3px; }}
.sub {{ color: {MUTED}; font-size: 9.8pt; margin-bottom: 8px; }}
.box {{ background: #f3f6fa; border-left: 4px solid {NAVY}; padding: 7px 11px; margin: 8px 0; }}
.rec {{ background: #e9f3ee; border-left: 4px solid {GREEN}; padding: 7px 11px; margin: 8px 0; }}
.cap {{ font-size: 8.8pt; color: {MUTED}; margin: 4px 0 8px; }}
.pb {{ page-break-before: always; }}
.slide {{ border-radius: 10px; overflow: hidden; border: 1px solid #d7dde6; margin: 8px 0; page-break-inside: avoid; background: #f7f8fa; }}
.stop {{ background: #1e3a5f; color: #fff; padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; }}
.stitle {{ font-size: 17pt; font-weight: 800; }} .ssub {{ font-size: 9.5pt; color: #c7d2e0; }}
.slegend {{ background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 8.5pt; font-weight: 700; }}
.scols {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; padding: 10px; }}
.scol {{ background: #fff; border-radius: 6px; padding-bottom: 6px; }}
.shead {{ color: #fff; font-weight: 800; text-align: center; padding: 6px; font-size: 10.5pt; border-radius: 6px 6px 0 0; }}
.srow {{ padding: 5px 8px; font-size: 9.2pt; display: flex; gap: 5px; align-items: flex-start; flex-wrap: wrap; }}
.smark {{ font-weight: 800; }} .stxt {{ flex: 1; min-width: 60%; }}
.stag {{ font-size: 7pt; font-weight: 800; padding: 1px 5px; border-radius: 6px; white-space: nowrap; }}
.sfoot {{ background: #1e3a5f; color: #fff; text-align: center; padding: 8px 10px; font-size: 9.5pt; }} .sfoot span {{ color: #c7d2e0; font-size: 8.5pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.9pt; table-layout: fixed; }}
th {{ background: {NAVY}; color: #fff; text-align: left; padding: 5px 6px; }}
td {{ border-bottom: 1px solid {RULE}; padding: 5px 6px; vertical-align: top; }}
tr {{ page-break-inside: avoid; }}
ol, ul {{ margin: 3px 0 3px 18px; padding: 0; }} li {{ margin: 2px 0; }}
.three {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin: 6px 0; }}
.tile {{ border: 1px solid {RULE}; border-radius: 8px; padding: 8px 10px; }}
.tile b {{ color: {NAVY}; }}
.big {{ font-size: 15pt; font-weight: 800; color: {NAVY}; }}
.small {{ font-size: 8.5pt; color: {MUTED}; }}
"""

SUMMARY = f"""
<h1>Bachatt today: entry is clear, the future is contested</h1>
<div class="sub">Memo for Piyush · From Sandeep · 19 October 2026 · Should we launch a challenger, and where do we fight?</div>
{slide()}
<div class="cap">Exhibit 1: The Bachatt model as it stands. Each square is built (✓) or still a vision (✗). We use this slide as our map of the market.</div>
<div class="three">
<div class="tile"><b>Entry is clear</b><br>Every ✓ square can be matched with a distributor code, payment rails and lender partners: <b>table stakes, not a moat</b>. Bachatt's lead is scale (about 30 lakh users, about $16M raised), not capability.</div>
<div class="tile"><b>The future is contested</b><br>The ✗ squares (offline, wallet, AI planning, short EMI and gold loans) plus loans on book are where value will be won.
Paytm, PhonePe, Jar, Snapmint and gold lenders all want them too.</div>
<div class="tile"><b>Our ground</b><br>Offline is Bachatt's empty square and our wedge. It feeds the rest: retention from a person, collections, credit from the savings record, and doorstep gold checks for gold loans.</div>
</div>
<div class="rec"><b>Recommendation.</b> Launch as a challenger only if we take the contested squares Bachatt can't easily reach: <b>assisted acquisition and servicing</b>, and a <b>credit engine with real collections</b>.
Match the ✓ squares quickly. Prove the wedge in a 6-month, one-city pilot before raising.</div>
"""

ENTRY = f"""
<div class="pb"></div>
<h2>1. Entry is clear: the ✓ squares are table stakes</h2>
<p>Everything Bachatt marks as built can be matched. What it takes:</p>
<table><colgroup><col style="width:26%"><col style="width:46%"><col style="width:28%"></colgroup>
<tr><th>✓ Square</th><th>What it takes to match</th><th>Moat?</th></tr>
<tr><td>Savings through debt funds</td><td>An AMFI ARN for the company (₹40,000) and NISM-certified staff (₹1,500 an exam) (REG-036/037), fund transaction rails, KYC, UPI auto-debit.</td><td>No: months, not years</td></tr>
<tr><td>Low-ticket entry; daily / flexible SIP</td><td>Daily UPI SIPs from about ₹51–100 (BAC-05). The cost is per-debit payment fees.</td><td>No</td></tr>
<tr><td>Online acquisition</td><td>Performance marketing. Online costs about ₹500 per activated saver (our estimate). Groww's cost to acquire a customer rose from ₹796 to ₹1,374 (TB-18).</td><td>No: money, and it's expensive</td></tr>
<tr><td>Financial products (MF, Insta Fund, gold/silver)</td><td>The same fund shelf. Distributors earn trail only on regular plans; liquid funds pay about 8 bp (REG-039).</td><td>No</td></tr>
<tr><td>No lock-in, instant withdraw</td><td>Instant redemption from liquid funds, capped at ₹50,000 or 90% a day per scheme (REG-041).</td><td>No: rule-bound</td></tr>
<tr><td>Digital loans through DSA; lean DSA + digital</td><td>Partner NBFCs, as Bachatt lists (XL-12), under the Digital Lending Directions. Pays 1–3% a loan, once (XL-13).</td><td>No: the lenders own it</td></tr>
<tr><td>Loans on book</td><td>Needs an NBFC. Bachatt's site says partner NBFCs disburse (XL-12). <b>Verify</b> before treating this as built.</td><td>Possibly, if real</td></tr>
</table>
<div class="box"><b>Implication.</b> A well-funded team can reach the ✓ column in about 6–9 months. Copying Bachatt gives us parity at best. What decides the market is <b>who wins the contested squares</b>.</div>

<h2>2. Why the contested squares decide the market: the money is not in savings</h2>
<div class="slide" style="background:#fff;padding:10px">{ex_value()}</div>
<div class="cap">Exhibit 2: What one user is worth. Savings trail is under ₹1 a user a year at Bachatt's visible balances.
One loan is worth more than years of trail, and the economics improve again when we collect and share risk.
An own NBFC earns a ~21% margin but carries 8–10% credit cost (Stashfin, LEV-026). The ₹350-a-day saver is our illustration.</div>
"""

CONTEST = """
<div class="pb"></div>
<h2>3. The future is contested, square by square</h2>
<table><colgroup><col style="width:17%"><col style="width:25%"><col style="width:22%"><col style="width:36%"></colgroup>
<tr><th>✗ Square</th><th>Why it matters</th><th>Who else wants it</th><th>What wins it, and our angle</th></tr>
<tr><td><b>Offline acquisition</b> (Bachatt ✗)</td><td>Cash-heavy earners trust a person. Apps keep roughly 1 in 4 savers a year.</td><td>Banks' daily-deposit agents; PhonePe (≈25,700 field staff, QM-12) and Paytm sell to merchants, not to savers.</td><td><b>Our wedge.</b> Agents who open accounts and come back every few days. A field-led savings fintech reports agents onboarding 100+ a month (practitioner, one data point).</td></tr>
<tr><td><b>Wallet-like: save in / withdraw out</b></td><td>A daily habit and money flows; the base for everything else.</td><td>Paytm and PhonePe wallets; Jar daily savings.</td><td>It must run on fund rails: no stored value without an RBI licence, payments from the saver's own account (REG-066), never hold money (REG-081), within instant-redemption caps (REG-041). <b>The winner makes "in and out" feel instant</b>, with a person to call.</td></tr>
<tr><td><b>AI financial planning</b></td><td>The relationship layer: engagement and cross-sell.</td><td>Every app will claim it.</td><td>AI alone is a commodity. <b>AI through a trusted agent</b> is not. Acting on money (auto-switching) raises advice and discretion rules (to verify), so start with one-tap actions the user confirms.</td></tr>
<tr><td><b>3-month EMI + gold loan</b></td><td>Credit is where the money is (Exhibit 2).</td><td>Gold: Muthoot, Manappuram, banks (≈3.8 crore gold loans a quarter, XL-28). EMI: Snapmint, Bajaj Finance.</td><td><b>Gold loans need physical gold.</b> RBI bars lending against gold fund units or digital gold (REG-022/023). So the gold loan needs <b>doorstep appraisal: an offline capability</b>. EMI credit on UPI is open only to banks and small finance banks (REG-074), so partner with one.</td></tr>
<tr><td><b>Loans on book</b> (contested even if ✓)</td><td>The biggest prize, and the biggest risk.</td><td>Fintech NBFCs (Moneyview, KreditBee, Kissht).</td><td>The edge is credit quality: the savings record plus collections (Paytm resolves 83–90% of early-overdue loans, XB-07). Earn the book step by step: DSA, then risk-share, then NBFC.</td></tr>
</table>
<div class="box"><b>The pattern.</b> Bachatt's empty square, offline, is the one that unlocks the others:
<ul><li><b>Retention:</b> a person keeps the saver saving.</li>
<li><b>Collections:</b> the agent knows the borrower.</li>
<li><b>Gold loans:</b> the agent can check the gold at the door.</li>
<li><b>AI:</b> it lands through someone the saver trusts.</li></ul>
That is why we treat offline as the wedge, not a side channel.</div>
"""

CHALLENGER_PAGE = f"""
<div class="pb"></div>
<h2>4. The challenger's slide: same map, different ground</h2>
{slide(annotate=True, data=CHALLENGER, title="Challenger model", sub="Same three columns; we compete on the contested squares",
        footer="Vision → the trusted daily money partner for cash earners: save, withdraw, borrow, protect, with a person behind the app",
        footer2="Power move: a person + the savings record + collections → credit quality nobody online can match")}
<div class="cap">Exhibit 3: Our version of the slide. Green tags (table stakes) we match; amber tags (our wedge) we lead; red tags (contested) we fight for with the wedge behind us.</div>
<h2>5. What could stop us</h2>
<table><colgroup><col style="width:28%"><col style="width:72%"></colgroup>
<tr><td><b>Money flows</b></td><td>Fund subscriptions must come from the saver's own account (REG-066). Collecting cash for funds needs a legal opinion; SEBI limits cash in funds (≈₹50,000 per investor a year, to verify). Never hold money (REG-081).</td></tr>
<tr><td><b>Offline cost and scale</b></td><td>Agents cost money every month. The wedge only works if a person wins and keeps savers for less per saver kept than online does, and if cities don't saturate too quickly.</td></tr>
<tr><td><b>Credit risk</b></td><td>Fintech NBFC credit costs run 6–10% (LEV-022/026). The savings record has to prove it predicts repayment before we take loans onto our book.</td></tr>
<tr><td><b>Rules in motion</b></td><td>IRDAI draft caps on insurance commission (REG-053). DLG capped at 5% (SE-04). SEBI warns on digital gold (SAV-11).</td></tr>
<tr><td><b>Bachatt adds offline</b></td><td>With $16M it can. Our defence is execution depth (collections, gold appraisal, the city playbook) and speed in one region first.</td></tr>
</table>
<h2>6. Prove it in one city, in 6 months</h2>
<ol><li><b>Savers won per agent a month, and the cost per saver who stays,</b> against online's ≈₹500 per activated saver.</li>
<li><b>Share still saving at months 3, 6 and 12,</b> against apps' ≈1 in 4 at a year.</li>
<li><b>Share of deposits moved from cash to UPI:</b> this decides how many savers one agent can serve.</li>
<li><b>Loan take-up, plus signed lender terms</b> for risk-sharing, above the 1–3% DSA fee.</li>
<li><b>Gold-loan pilot with a partner lender:</b> doorstep appraisal volume and quality.</li></ol>
<h2>7. Decisions for us</h2>
<ol><li>Do we agree the fight is on the contested squares, with offline as the wedge?</li>
<li>Which city and segment first? For example NCR shopkeepers and vendors.</li>
<li>Credit path: when to move from DSA to risk-share to our own NBFC, and who leads credit and collections?</li>
<li>What are the kill thresholds for the five pilot numbers, agreed in advance?</li></ol>
"""

SOURCES = [
    ("BAC-02/03/05, XB-03", "Bachatt press release / Series A: ~3M users, 2M MF transactions (Feb 2026), product details", "https://bachatt.app/press-release"),
    ("BAC-04, XL-12", "Bachatt homepage: ₹50 crore+ invested; loans via partner NBFCs (Bachatt as LSP)", "https://bachatt.app/"),
    ("QM-45", "Entrackr: Bachatt $12M Series A (Accel); about $16M raised in all", "https://entrackr.com/news/wealthtech-startup-bachatt-raises-12-mn-in-series-a-led-by-accel-11438527"),
    ("REG-036/037", "AMFI ARN fee (₹40,000 for a private company); NISM V-A exam ₹1,500 + GST", "AMFI / NISM (research/regulation_rails.csv)"),
    ("REG-039", "Trail only on regular plans; liquid-fund regular-direct gap ≈ 8 bp", "research/regulation_rails.csv"),
    ("REG-041", "Instant Access Facility: lower of ₹50,000 or 90% a day per scheme", "research/regulation_rails.csv"),
    ("REG-022/023", "RBI Gold Lending Directions 2025: no loans against gold ETF or MF units, or digital gold", "research/regulation_rails.csv"),
    ("XB-04", "Debt-fund distributor trail 0.2–0.5% a year", "https://www.kotakmf.com/Information/blogs/direct-vs-regular-plan"),
    ("XL-13", "DSA payouts on personal loans 1–2.5%", "https://gromo.in/blog/dsa-loan-agent-commission/"),
    ("XL-28/29", "CRIF: ≈381 lakh gold loans a quarter; personal-loan average ₹58,522", "https://www.crifhighmark.com/media/5315/how-india-lends-report-june2025.pdf"),
    ("SE-05, XB-07", "Paytm: 4.5–5% per merchant loan; early-overdue resolution 83–90%", "https://paytm.com/document/ir/financial-results/fy2025-26/Paytm_Earning-Release_Q4-FY2026-FY-2026.pdf"),
    ("LEV-022, LEV-026", "KreditBee credit cost 6–8%; Stashfin credit cost 8–10%, NIM 21.3%, RoMA 1.2%", "https://www.icra.in/Rating/GetRationalReportFilePdf?id=138434"),
    ("TB-18", "Groww cost to acquire a customer ₹796 → ₹1,374", "https://entrackr.com/news/growws-customer-acquisition-cost-spikes-73-in-h1-fy26-10799610"),
    ("QM-12", "PhonePe: 25,657 field staff + 31,000+ agents (DRHP)", "https://www.thehansindia.com/amp/business/phonepes-merchant-network-hits-47-million-businesses-drhp-reveals-diversified-monetisation-1054264"),
    ("REG-066, REG-081, REG-074", "SEBI own-account payments; BUDS Act; UPI credit lines only for banks and small finance banks", "research/regulation_rails.csv"),
    ("REG-053, SE-04, SAV-11", "IRDAI draft commission caps; DLG cap 5%; SEBI on digital gold", "research/regulation_rails.csv"),
]


def build():
    src = "".join(f"<tr><td>{a}</td><td>{b}</td><td style='word-break:break-all'>{c}</td></tr>" for a, b, c in SOURCES)
    sources = (f'<div class="pb"></div><h2>Sources</h2><p class="small">IDs are rows in our research files. Bachatt figures are company claims. '
               f'"Our estimate" and "to verify" mark items that are not sourced facts.</p>'
               f'<table><colgroup><col style="width:18%"><col style="width:44%"><col style="width:38%"></colgroup><tr><th>ID</th><th>What</th><th>Where</th></tr>{src}</table>')
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>Bachatt memo</title><style>{CSS}</style></head><body>{SUMMARY}{ENTRY}{CONTEST}{CHALLENGER_PAGE}{sources}</body></html>'
    out = HERE / "Bachatt_teardown_memo.html"
    out.write_text(html)
    pdf = HERE / "Bachatt_teardown_memo.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf)


if __name__ == "__main__":
    build()

"""Co-founder memo to Piyush: Bachatt teardown and where a newcomer can win (19 Oct 2026).
Every number cites a research row ID (research/*.csv) or is marked as our estimate / external / to verify.
Builds memo/Bachatt_teardown_memo.html -> memo/Bachatt_teardown_memo.pdf (Chrome headless)."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAVY, INK, MUTED, RULE, GREEN, RED, AMBER, BLUE = "#1f3a5f", "#1f2328", "#6b7280", "#e5e7eb", "#2f6b4f", "#b42318", "#a15c07", "#1f64a8"

# ---------- numbers (all traceable) ----------
BAC_USERS = 3_000_000            # BAC-02 (company claim, users acquired since May 2025)
BAC_INVESTED = 50e7              # BAC-04 (Rs 50 crore+, website banner, unverified)
PER_USER_BAL = BAC_INVESTED / BAC_USERS            # ~Rs 167
TRAIL_LO, TRAIL_MID, TRAIL_HI = 0.002, 0.0035, 0.005   # XB-04 debt-fund distributor trail 0.2-0.5%
LIQ = 0.0005                     # TC-22 liquid-fund trail ~0.05%
DAILY, DAYS = 350, 20            # illustrative committed saver (our estimate)
AVG_BAL = DAILY * DAYS * 12 / 2  # half a year's deposits held on average (our estimate)
PL_TICKET = 58_522               # XL-29 average personal-loan ticket, Q1 FY26
DSA = 0.02                       # XL-13 typical 1-2.5%
PAYTM = 0.0475                   # SE-05 / XB-07 4.5-5%


def inr(x, d=0):
    s = f"{abs(x):,.{d}f}"
    # Indian grouping
    whole, _, frac = s.partition(".")
    whole = whole.replace(",", "")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        whole = head + "," + tail
    return ("−" if x < 0 else "") + "₹" + whole + (("." + frac) if frac else "")


def svg(w, h, body):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif">{body}</svg>'


def t(x, y, s, size=12, weight=400, fill=INK, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


# ---------- Exhibit 2: what one user is worth (log scale) ----------
def ex_user_value():
    rows = [
        ("Bachatt today: savings trail on ~" + inr(PER_USER_BAL) + " per user", PER_USER_BAL * TRAIL_MID, "a year", NAVY,
         f"{inr(PER_USER_BAL * TRAIL_LO, 1)}–{inr(PER_USER_BAL * TRAIL_HI, 1)} at 0.2–0.5% (BAC-02/04, XB-04)"),
        ("A committed ₹350-a-day saver: trail on ~" + inr(AVG_BAL) + " held", AVG_BAL * TRAIL_MID, "a year", NAVY,
         f"{inr(AVG_BAL * TRAIL_LO)}–{inr(AVG_BAL * TRAIL_HI)} (XB-04; liquid fund only {inr(AVG_BAL * LIQ)}, TC-22)"),
        ("One average personal loan (" + inr(PL_TICKET) + ") sourced as a DSA", PL_TICKET * DSA, "once", AMBER,
         f"1–2.5% of the loan (XL-13, LEV-009; ticket XL-29)"),
        ("The same loan, if we collect and share risk (Paytm-style)", PL_TICKET * PAYTM, "once", AMBER,
         "4.5–5% of the loan (SE-05, XB-07)"),
    ]
    import math
    x0, x1, top, gap = 330, 760, 34, 52
    lo, hi = math.log10(0.1), math.log10(10000)
    X = lambda v: x0 + (x1 - x0) * (math.log10(max(v, 0.1)) - lo) / (hi - lo)
    s = [t(0, 16, "WHAT ONE USER IS WORTH TO A DISTRIBUTOR (₹, LOG SCALE)", 11.5, 700, NAVY)]
    for v in (1, 10, 100, 1000, 10000):
        s.append(f'<line x1="{X(v)}" y1="{top - 6}" x2="{X(v)}" y2="{top + gap * len(rows) - 14}" stroke="{RULE}"/>')
        s.append(t(X(v), top + gap * len(rows) - 2, inr(v), 10, 400, MUTED, "middle"))
    for i, (lab, v, per, col, note) in enumerate(rows):
        y = top + i * gap
        s.append(t(0, y + 13, lab, 11.5, 600))
        s.append(t(0, y + 28, note, 9.5, 400, MUTED))
        s.append(f'<rect x="{x0}" y="{y + 2}" width="{max(X(v) - x0, 3)}" height="22" rx="4" fill="{col}"/>')
        s.append(t(X(v) + 6, y + 18, f"{inr(v, 1 if v < 10 else 0)} {per}", 12, 800, col))
    return svg(820, top + gap * len(rows) + 6, "".join(s))


# ---------- Exhibit 3: credit economics ladder ----------
def ex_credit_ladder():
    rows = [
        ("DSA / connector", "1–3% of the loan, once", 2.0, "no credit risk; commission clawed back if the loan closes early (XL-13, LEV-009)"),
        ("Marketplace (Paisabazaar-like)", "≤ 4.6% of disbursal, incl. card fees", 4.6, "upper bound, no balance-sheet risk (XL-09)"),
        ("Collect + share risk (Paytm-like)", "4.5–5% of each loan", 4.75, "the platform collects; lender books the loan (SE-05, XB-07)"),
        ("Full-servicing LSP with first-loss cover", "~11% gross, ~8–9% after DLG losses", 8.5, "Moneyview blend; DLG capped at 5% (LEV-061, SE-04)"),
        ("Own NBFC (book)", "NIM ~21% of AUM a year", 21.3, "but credit cost 8–10% of disbursal, opex ~9% → RoMA ~1.2% (Stashfin FY25, LEV-026)"),
    ]
    x0, x1, top, gap = 270, 560, 30, 50
    X = lambda v: x0 + (x1 - x0) * v / 22
    s = [t(0, 14, "THE CREDIT LADDER: WHAT A PLATFORM EARNS PER ₹100 OF CREDIT", 11.5, 700, NAVY)]
    for i, (lab, txt, v, note) in enumerate(rows):
        y = top + i * gap
        col = AMBER if i < 3 else (BLUE if i == 3 else RED)
        s.append(t(0, y + 15, lab, 11.5, 700))
        s.append(f'<rect x="{x0}" y="{y + 2}" width="{X(v) - x0}" height="18" rx="4" fill="{col}" opacity="0.9"/>')
        s.append(t(X(v) + 6, y + 16, txt, 10.5, 700, col))
        s.append(t(0, y + 35, note, 9.3, 400, MUTED))
    return svg(820, top + gap * len(rows), "".join(s))


# ---------- Exhibit 4: the market funnel ----------
def ex_market():
    rows = [
        ("Unorganised workers registered on e-Shram", 31.89, "SEG-02", MUTED),
        ("All self-employed (rural + urban)", 34.6, "NG-003 (derived from PLFS 2025)", MUTED),
        ("URBAN self-employed: our addressable pool", 7.0, "6.5–7.7 crore; NG-002 shares × ~19 crore urban workers (our estimate)", NAVY),
        ("…in ~500 cities big enough for a field team", 4.5, "~65% of the pool on a rank-size estimate (ours)", BLUE),
        ("Reachable if ~1 in 5 of a city ever signs up", 0.9, "about 90 lakh people: our judgement on city saturation", GREEN),
        ("Bachatt's stated target", 3.0, "30 million users in 12–24 months (XB-03): registered users, not active savers", AMBER),
    ]
    x0, x1, top, gap = 330, 700, 30, 44
    X = lambda v: x0 + (x1 - x0) * v / 36
    s = [t(0, 14, "HOW BIG IS THE PRIZE? (CRORE PEOPLE)", 11.5, 700, NAVY)]
    for i, (lab, v, note, col) in enumerate(rows):
        y = top + i * gap
        s.append(t(0, y + 13, lab, 11.5, 700))
        s.append(t(0, y + 28, note, 9.3, 400, MUTED))
        s.append(f'<rect x="{x0}" y="{y + 1}" width="{max(X(v) - x0, 3)}" height="20" rx="4" fill="{col}"/>')
        s.append(t(X(v) + 6, y + 15, f"{v:g} crore", 11, 800, col))
    return svg(820, top + gap * len(rows), "".join(s))


CSS = f"""
@page {{ size: A4; margin: 16mm 15mm 16mm 15mm; }}
body {{ font-family: Helvetica, Arial, sans-serif; color: {INK}; font-size: 10.4pt; line-height: 1.45; }}
h1 {{ color: {NAVY}; font-size: 20pt; margin: 0 0 2px; }}
h2 {{ color: {NAVY}; font-size: 13.5pt; margin: 18px 0 6px; border-bottom: 2px solid {NAVY}; padding-bottom: 3px; }}
h3 {{ color: {NAVY}; font-size: 11pt; margin: 12px 0 4px; }}
.sub {{ color: {MUTED}; font-size: 10pt; margin-bottom: 10px; }}
.meta {{ font-size: 9.8pt; margin: 6px 0 10px; }}
.box {{ background: #f3f6fa; border-left: 4px solid {NAVY}; padding: 8px 12px; margin: 8px 0; }}
.rec {{ background: #e9f3ee; border-left: 4px solid {GREEN}; padding: 8px 12px; margin: 8px 0; }}
.warn {{ background: #fbf3e6; border-left: 4px solid {AMBER}; padding: 8px 12px; margin: 8px 0; }}
.ex {{ border: 1px solid {RULE}; border-radius: 8px; padding: 10px 12px; margin: 10px 0; page-break-inside: avoid; }}
.exh {{ font-size: 9pt; color: {MUTED}; margin-top: 4px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; table-layout: fixed; }}
th {{ background: {NAVY}; color: #fff; text-align: left; padding: 5px 6px; font-weight: 700; }}
td {{ border-bottom: 1px solid {RULE}; padding: 5px 6px; vertical-align: top; }}
tr {{ page-break-inside: avoid; }}
.pb {{ page-break-before: always; }}
ol, ul {{ margin: 4px 0 4px 18px; padding: 0; }}
li {{ margin: 2px 0; }}
.tag {{ display: inline-block; font-size: 8pt; font-weight: 700; padding: 1px 6px; border-radius: 8px; }}
.now {{ background: #e9f3ee; color: {GREEN}; }} .next {{ background: #e8f0f9; color: {BLUE}; }}
.later {{ background: #f1f1f1; color: {MUTED}; }} .care {{ background: #fbf3e6; color: {AMBER}; }}
.small {{ font-size: 8.6pt; color: {MUTED}; }}
"""

SUMMARY = f"""
<h1>Bachatt: what it has built, where it is thin, and where we can win</h1>
<div class="sub">One-page summary · Internal memo for Piyush · From Sandeep · 19 October 2026</div>
<div class="box"><b>The question for us.</b> Bachatt's own memo concludes "the current model is sound" and plans to add a wallet, AI planning and EMI-on-products.
We are deciding whether to launch a competitor. This memo tests that model against public evidence and our own modelling, and sets out where a newcomer can win.</div>
<h3>Five things that matter</h3>
<ol>
<li><b>Bachatt has won sign-ups, not yet the relationship.</b> About 30 lakh users acquired in under a year (BAC-02). But about ₹50 crore invested (BAC-04) is only <b>~{inr(PER_USER_BAL)} per user</b>, and no retention figure is published. Most users look like trial or dormant savers.</li>
<li><b>Savings is the hook, not the business.</b> A distributor earns 0.2–0.5% a year on debt funds (XB-04), and about 0.05% on liquid funds (TC-22).
That's <b>under ₹1 a user a year</b> at Bachatt's balances, and only about {inr(AVG_BAL * TRAIL_LO)}–{inr(AVG_BAL * TRAIL_HI)} even for a committed ₹350-a-day saver. The money is in credit.</li>
<li><b>In credit, the power is in collections and the book, not the referral.</b> A DSA earns 1–3% once. A platform that collects and shares risk earns 4.5–5% (Paytm). An own NBFC earns a ~21% NIM but carries 8–10% credit cost (Stashfin).
The edge is <b>credit quality</b>: the savings record plus the ability to collect. A licence alone doesn't give it.</li>
<li><b>The market has a ceiling, so depth beats breadth.</b> "30 crore" is the e-Shram universe (SEG-02). The urban self-employed a field or app business can serve is about <b>6.5–7.7 crore</b> (NG-002).
If at most about 1 in 5 in a city ever signs up, the reachable pool is roughly 90 lakh people. Bachatt's "30 million users" target can only mean registrations.</li>
<li><b>Bachatt's gaps are our wedge.</b> It has no offline channel (its own slide). It publishes no retention figure. Its lending is referral-only: partner NBFCs disburse (XL-12), which contradicts the slide's "loans on book ✓".
Its gold story leans on digital gold, which SEBI says is unregulated (SAV-11).</li>
</ol>
<div class="rec"><b>Recommendation.</b> Enter only if we are different on the two things that create power:
<b>(1) assisted, local acquisition and servicing</b> for cash-heavy earners, which buys retention and trust that apps don't get;
and <b>(2) a credit engine from day one</b>: data, collections and lender terms, moving from a referral fee to risk-sharing to our own book.
Prove it with a 6-month pilot that measures five numbers (Section 7) before we raise.</div>
<h3>Decisions we need to make together</h3>
<ol><li>Our wedge: assisted-first (field plus app) or digital-first with an assisted layer.</li>
<li>Our credit path: how fast we move from DSA to risk-sharing to an NBFC (capital, licence, credit team).</li>
<li>Our first segment and city: merchants and shopkeepers in one metro, and what we must prove there in 6 months.</li></ol>
"""

BODY = f"""
<div class="pb"></div>
<h1>Bachatt teardown and the case for a challenger</h1>
<div class="sub">Internal memo · To: Piyush · From: Sandeep · 19 October 2026 · Sources: research row IDs in brackets; list on the last page</div>

<h2>1. What Bachatt has built, and what the evidence shows</h2>
<p>Bachatt's slide splits its model into Acquisition, Retention and Servicing, marking each item built or vision.
The table checks each claim against public evidence, so we start from what is verified, not from what is claimed.</p>
<div class="ex"><table>
<colgroup><col style="width:30%"><col style="width:15%"><col style="width:55%"></colgroup>
<tr><th>Claim (their slide / memo)</th><th>Status</th><th>What the evidence says</th></tr>
<tr><td>Savings through debt funds; low ticket (~₹250)</td><td>Built</td><td>Daily UPI SIPs from about ₹51–100 into debt and liquid ("Insta") funds; gold and silver funds (BAC-05, XB-03). About 2 million fund transactions in Feb 2026 (BAC-03).</td></tr>
<tr><td>Online acquisition ✓, offline ✗</td><td>Built (online)</td><td>About 30 lakh users acquired since the May 2025 launch, a company claim (BAC-02). About $16M raised: $4M seed and a $12M Series A led by Accel (QM-45).</td></tr>
<tr><td>Retention (no lock-in, flexible SIP)</td><td><span class="tag care">unproven</span></td><td>No retention, active-saver or AUM-per-user figure is published. ₹50 crore+ invested (BAC-04) over 30 lakh users ≈ <b>{inr(PER_USER_BAL)} a user</b>.</td></tr>
<tr><td>Digital loans through DSA ✓; "Loans on book ✓"</td><td><span class="tag care">conflict</span></td><td>Bachatt's site says loans up to ₹5 lakh are disbursed by partner NBFCs, with Bachatt as the lending service provider (XL-12). That is referral and servicing, not its own book. <b>To verify:</b> has Bachatt since licensed or acquired an NBFC?</td></tr>
<tr><td>Gold/silver as a hook, "0% GST angle"</td><td><span class="tag care">imprecise</span></td><td>True for gold and silver <i>funds</i>. Digital gold carries 3% GST (LEV-037), and SEBI has warned it is outside its regulation (SAV-11).</td></tr>
<tr><td>Wallet (save in / withdraw out), AI planning, EMI-on-products</td><td>Vision</td><td>None is live. Each has a licence or regulatory gate (Section 6).</td></tr>
</table><div class="exh">Exhibit 1: Bachatt's claims checked against public evidence. Every Bachatt figure is a company claim; none is audited.</div></div>

<h2>2. The economics: savings is the hook, credit is the business</h2>
<p>A distributor earns a trail on the money parked: 0.2–0.5% a year on debt funds (XB-04), and only about 0.05% on liquid funds (TC-22).
At Bachatt's visible balances, that is <b>pennies per user</b>. Even a disciplined daily saver is worth a few hundred rupees a year.
One personal loan sourced through the platform is worth more than years of trail. The memo's own flywheel (savings → trust and data → loans) is right. The question is who captures the credit economics.</p>
<div class="ex">{ex_user_value()}<div class="exh">Exhibit 2: Value per user by monetisation layer, in rupees on a log scale. The ₹350-a-day saver and the half-year average balance are our illustration, not Bachatt data.</div></div>
<div class="ex">{ex_credit_ladder()}<div class="exh">Exhibit 3: Each step up the credit ladder earns more per ₹100 lent and carries more risk.
The NBFC bar is a gross margin, not profit: Stashfin's return on managed assets was about 1.2% in FY25 (LEV-026). KreditBee's credit cost was 6–8% of assets (LEV-022).</div></div>
<div class="box"><b>So what.</b> Power in this segment comes from three things:
<ul><li><b>Underwriting from the savings record:</b> who saves, how regularly, and how they behave under stress.</li>
<li><b>The ability to collect:</b> Paytm resolves 83–90% of early-overdue loans and recovers 30–35% after 90 days (XB-07).</li>
<li><b>Funding:</b> NBFC cost of funds is about 13–14.5% (LEV-014).</li></ul>
A pure DSA (Bachatt's lending today) keeps 1–3% once and owns none of these.</div>

<h2>3. Bachatt's ideas, scored</h2>
<p>We score each idea in Bachatt's memo on four things: how much power it creates (relationship, money flow, data, switching cost), what it needs to build, what regulation gates it, and when it pays.</p>
<div class="ex"><table>
<colgroup><col style="width:21%"><col style="width:25%"><col style="width:30%"><col style="width:12%"><col style="width:12%"></colgroup>
<tr><th>Idea</th><th>Power it creates</th><th>What it takes / the gate</th><th>Payback</th><th>Verdict</th></tr>
<tr><td>Wallet: save in, withdraw out</td><td>High: daily habit, money flows</td><td>Must stay fund-backed with instant redemption, not a stored-value wallet (an RBI PPI licence). Payments must come from the saver's own account (REG-066). Never hold money (BUDS Act, REG-081).</td><td>Medium</td><td><span class="tag now">Do now</span></td></tr>
<tr><td>Credit on own book (+ collections)</td><td>Highest: income per user and data</td><td>NBFC licence and capital, a credit and collections team, funding at ~13–14.5% (LEV-014). DLG to partners capped at 5% (SE-04).</td><td>Slow, large</td><td><span class="tag next">Next: earn it</span></td></tr>
<tr><td>EMI on products (Snapmint-style)</td><td>Medium: purchase data, new revenue</td><td>A lender or NBFC plus merchant integrations. "EMI on UPI" credit lines are open to banks and small finance banks, not NBFCs (REG-074). Consumer-durable loans average ₹20,600, with about 2.2 crore a quarter (XL-28/29). A crowded market (Bajaj Finance and others).</td><td>Medium</td><td><span class="tag next">Next, via a partner</span></td></tr>
<tr><td>Cash-flow AI that acts</td><td>High once trusted</td><td>Auto-moving money or switching funds edges into advice and discretion (SEBI RIA/PMS rules: to verify). Start with nudges and one-tap actions the user confirms.</td><td>Medium</td><td><span class="tag care">Now, carefully</span></td></tr>
<tr><td>Merchant vertical products</td><td>Medium: better underwriting</td><td>Segment playbooks for kirana, jewellery and auto dealers (about 1.3–1.5 crore kiranas, NG-009).</td><td>Medium</td><td><span class="tag next">Next</span></td></tr>
<tr><td>Supplier / inventory finance</td><td>High: money both ways</td><td>Needs our own book or a co-lender, plus trade data. Crowded (Udaan, B2B lenders).</td><td>Slow</td><td><span class="tag later">Later</span></td></tr>
<tr><td>Embedded collections for merchants</td><td>High: daily flows</td><td>An RBI payment-aggregator licence or a partner PA.</td><td>Medium</td><td><span class="tag later">Later</span></td></tr>
<tr><td>Gold/silver as a daily hook</td><td>Medium</td><td>Use gold and silver <i>funds</i>, not digital gold, which SEBI says is unregulated (SAV-11). Jar earned about 2.4% per digital-gold purchase (LEV-036), but that business carries the regulatory risk.</td><td>Fast</td><td><span class="tag care">Funds only</span></td></tr>
<tr><td>Protection (health, shop, accident)</td><td>Medium: stickiness</td><td>Sell through a broker or corporate agent; the insurer prices the risk. IRDAI's draft caps on commission (REG-053). PhonePe earns about ₹8 a user a year on insurance (XO-10).</td><td>Medium</td><td><span class="tag next">Next</span></td></tr>
<tr><td>Network effects; generosity (bank-charge recovery)</td><td>Low–medium: trust</td><td>Cheap to build. Good for trust; little direct revenue.</td><td>Slow</td><td><span class="tag now">Do now</span> (cheap)</td></tr>
</table><div class="exh">Exhibit 4: Bachatt's own expansion ideas, scored. Our view: credit on book plus collections is the real power move. EMI-on-products is one channel into it, not the destination.</div></div>

<h2>4. How big is the prize, and where is the ceiling?</h2>
<div class="ex">{ex_market()}<div class="exh">Exhibit 5: From headline "30 crore" to a realistic reachable pool. The rank-size city estimate and the 1-in-5 city ceiling are our modelling judgements, shown to make the point that depth per customer matters more than headline users.</div></div>
<p>Two implications follow.</p>
<ol><li><b>A savings app chasing "30 million users" is counting registrations, not savers.</b> Active, money-parking savers are likely to be a small fraction.</li>
<li><b>The winner earns more per customer.</b> That means credit, protection and a daily habit, in fewer, deeper cities, not a thin national footprint.</li></ol>

<h2>5. Where a challenger can win</h2>
<ol>
<li><b>Assisted acquisition and servicing for cash-heavy earners.</b>
<ul>
<li><b>Online acquisition is expensive and leaky.</b> Groww's cost to acquire a customer rose from ₹796 to ₹1,374 (TB-18). App savers typically lapse within a year.</li>
<li><b>Even the digital giants run field teams.</b> PhonePe has about 25,700 field staff plus 31,000+ commissioned agents (QM-12). Paytm's 1.57 crore device merchants are field-sold (NG-028).</li>
<li><b>A field-led savings fintech reports agents onboarding 100+ customers a month</b> (practitioner conversation, 17 Oct; one data point).</li>
<li><b>Where Bachatt is weakest:</b> it has no offline channel. A human who visits wins trust and retention among cash earners.</li>
</ul></li>
<li><b>Collections as a product capability, not a back office.</b> The agent who knows the customer is our collections edge. It earns better lender terms: risk-sharing at 4.5–5% instead of 1–3% DSA fees.</li>
<li><b>Underwriting from the savings record.</b> Savings regularity is a credit signal no bureau has. Use it to move up the credit ladder (Exhibit 3) step by step.</li>
<li><b>Clean money flows.</b> Run on the fund's rails from the saver's own account, and never hold customer money. Our modelling found the cash-collection route needs a legal opinion first: SEBI limits cash in mutual funds, about ₹50,000 per investor a year (to verify).</li>
<li><b>Depth before breadth.</b> Win a few cities thoroughly. Saturation is real, so the business must grow income per saver, not just sign-ups.</li>
</ol>

<h2>6. Regulatory gates we must design around</h2>
<div class="ex"><table>
<colgroup><col style="width:24%"><col style="width:46%"><col style="width:30%"></colgroup>
<tr><th>Gate</th><th>Rule</th><th>Design implication</th></tr>
<tr><td>Mutual-fund distribution</td><td>An AMFI ARN. Subscriptions must come from the investor's own bank account (REG-066).</td><td>No pooling. Cash collection needs a legal opinion.</td></tr>
<tr><td>Deposits</td><td>The BUDS Act bans unregulated deposit schemes (REG-081).</td><td>Never hold customer money; it is not a "wallet" balance.</td></tr>
<tr><td>Digital lending</td><td>LSP rules; DLG capped at 5% (SE-04); no DLG on cards or revolving credit (REG-007).</td><td>Risk-sharing has limits. An own book means an NBFC.</td></tr>
<tr><td>Credit on UPI</td><td>Banks and small finance banks only, not NBFCs (REG-074).</td><td>EMI-on-UPI needs a bank partner.</td></tr>
<tr><td>Insurance</td><td>IRDAI draft caps on commission and a single distribution licence (REG-053; comments close 25 Oct 2026).</td><td>Plan on lower commissions; distribute through a broker.</td></tr>
<tr><td>Digital gold</td><td>SEBI caution: outside its regulation (SAV-11).</td><td>Use gold and silver funds instead.</td></tr>
</table><div class="exh">Exhibit 6: Regulatory gates. Items marked "to verify" need a lawyer before we build.</div></div>

<h2>7. What we must prove before we raise: a 6-month pilot</h2>
<table><colgroup><col style="width:30%"><col style="width:40%"><col style="width:30%"></colgroup>
<tr><th>Number</th><th>Why it decides the business</th><th>How we read it</th></tr>
<tr><td>1. Savers won per agent a month, and the cost to win each</td><td>Assisted acquisition must beat online's ~₹500 per activated saver (our estimate from TB-18..22) on cost per saver who stays.</td><td>Weekly, by agent</td></tr>
<tr><td>2. Still saving at months 3, 6 and 12</td><td>Our biggest swing factor. Apps keep roughly 1 in 4 savers at a year. We must do clearly better.</td><td>By monthly cohort</td></tr>
<tr><td>3. Cash-to-UPI migration</td><td>Decides how many savers one agent can serve.</td><td>Share of deposits by UPI</td></tr>
<tr><td>4. Loan take-up and lender terms</td><td>The economics live here: apply rate, approval rate, ticket, and the fee or risk-share a lender will give us.</td><td>Signed term sheets with 2 lenders</td></tr>
<tr><td>5. Legal opinion on money flows</td><td>Gates the whole cash model.</td><td>Before launch</td></tr>
</table>

<h2>8. Questions for us</h2>
<ol>
<li>Do we agree that credit, with collections, is the business and savings is the hook? If yes, when do we need an NBFC?</li>
<li>Assisted-first or digital-first? Which city and segment for the pilot (e.g. NCR shopkeepers)?</li>
<li>What would make us stop? Agree the kill thresholds for the five pilot numbers in advance.</li>
<li>Roles: who owns credit and risk, and who owns field operations and growth?</li>
<li>How do we answer an investor's question, "why not just partner with Bachatt"?</li>
</ol>
"""

SOURCES = [
    ("BAC-02/03/05, XB-03", "Bachatt press release and Series A coverage: 3M users, 2M MF transactions (Feb 2026), product details", "https://bachatt.app/press-release"),
    ("BAC-04, XL-12", "Bachatt homepage: ₹50 crore+ invested; loans via partner NBFCs, Bachatt as LSP", "https://bachatt.app/"),
    ("QM-45", "Entrackr: Bachatt raises $12M Series A led by Accel", "https://entrackr.com/news/wealthtech-startup-bachatt-raises-12-mn-in-series-a-led-by-accel-11438527"),
    ("XB-04", "Debt-fund distributor commission 0.2–0.5% a year (AMC and adviser blogs)", "https://www.kotakmf.com/Information/blogs/direct-vs-regular-plan"),
    ("TC-22", "Liquid-fund trail about 0.05% (distributor commission disclosures)", "https://www.hsbc.bank.in/content/dam/hsbc/in/documents/investments/amc-disclosure-document.pdf"),
    ("XL-13, LEV-009", "DSA payouts: personal loans 1–2.5% (0.5–4% range); 1–3% for NBFC/fintech lenders", "https://gromo.in/blog/dsa-loan-agent-commission/"),
    ("XL-09", "Paisabazaar core credit revenue ÷ disbursals ≈ 4.6% (upper bound, incl. card fees)", "https://www.multibagg.ai/market-pulse/articles/pbfintech-q1fy27-97909"),
    ("SE-05, XB-07", "Paytm merchant loans: 4.5–5% take rate; ECL 4.5–5%; bucket-1 resolution 83–90%; recovery after 90 days 30–35%", "https://paytm.com/document/ir/financial-results/fy2025-26/Paytm_Earning-Release_Q4-FY2026-FY-2026.pdf"),
    ("LEV-061", "Moneyview RHP: a DLG-bearing LSP earns about 11% of partner disbursal", "https://moneyview.in/images/Red-Herring-Prospectus.pdf"),
    ("LEV-012, LEV-014", "Moneyview NBFC: yield 25–28%, cost of borrowings 14.44%", "https://indiafintech.substack.com/p/moneyviews-drhp-decoded-the-economics"),
    ("LEV-022", "KrazyBee (KreditBee) credit cost 6.1–7.7% of average assets (CareEdge)", "https://www.careratings.com/upload/CompanyFiles/PR/202603120334_KrazyBee_Services_Limited.pdf"),
    ("LEV-026", "Akara (Stashfin) ICRA: credit cost 8–10% of disbursal, NIM 21.3%, opex 8.8%, RoMA 1.2% (FY25)", "https://www.icra.in/Rating/GetRationalReportFilePdf?id=138434"),
    ("NG-002, NG-003", "PLFS 2025: urban self-employed shares; about 34.6 crore self-employed in all", "https://dge.gov.in/sites/default/files/2026-07/Annual_Report_PLFS_2025.pdf"),
    ("SEG-02", "e-Shram: 31.89 crore unorganised workers registered (Aug 2026)", "https://organiser.org/2026/08/29/377578/bharat/five-years-of-e-shram-31-89-crore-unorganised-workers-join-indias-digital"),
    ("NG-009", "Kirana stores: 13–15 million (Redseer)", "https://theprint.in/economy/indian-kirana-stores-rapidly-adopting-digital-solutions-redseer/2272715/"),
    ("SAV-11", "SEBI warns digital gold is outside its regulation", "https://www.newsonair.gov.in/sebi-warns-investors-against-unregulated-digital-gold-schemes"),
    ("LEV-036/037", "Digital gold: about 2.4% distributor commission (Jar); 2–3% spread plus 3% GST", "https://blog.oropocket.com/safegold-review-2026-features-fees-alternatives/"),
    ("SE-04, REG-007", "RBI Digital Lending Directions 2025: DLG cap 5%; no DLG on cards or revolving credit", "https://www.rbi.org.in/scripts/NotificationUser.aspx?Id=12848&Mode=0"),
    ("REG-066", "SEBI MF Master Circular: subscriptions from the investor's own account", "https://www.sebi.gov.in/sebi_data/attachdocs/may-2026/1779276447538.pdf"),
    ("REG-081", "Banning of Unregulated Deposit Schemes Act 2019", "https://www.indiacode.nic.in/handle/123456789/11641"),
    ("REG-074", "Credit lines on UPI: banks and small finance banks only, not NBFCs", "https://www.business-standard.com/finance/news/rbi-allows-small-finance-banks-to-offer-pre-sanctioned-credit-line-on-upi"),
    ("REG-053", "IRDAI consultation on distribution economics (Sep 2026)", "https://www.khaitanco.com/sites/default/files/2026-09/Insurance_IRDA_Distribution%20Reforms_29%20September%202026_ergo.pdf"),
    ("XL-28/29", "CRIF How India Lends: consumer-durable loans about 2.2 crore a quarter, average ₹20,600; personal-loan average ₹58,522", "https://www.crifhighmark.com/media/5315/how-india-lends-report-june2025.pdf"),
    ("QM-12", "PhonePe DRHP: 25,657 field staff plus 31,000+ commissioned agents", "https://www.thehansindia.com/amp/business/phonepes-merchant-network-hits-47-million-businesses-drhp-reveals-diversified-monetisation-1054264"),
    ("NG-028, XO-11", "Paytm Q1 FY27: 1.57 crore device merchants; MF, gold and attached insurance 'negligible revenue'", "https://paytm.com/document/ir/financial-results/fy2026-27/Paytm_Earning-Release_Q1-FY-2027_INR.pdf"),
    ("XO-10", "PhonePe FY26: insurance revenue ₹191 crore ≈ ₹8 per monthly user", "https://www.outlookbusiness.com/corporate/phonepe-fy26-losses-rs-2792-cr-revenue-rises-11-pc-lending-wealth-insurance-gr"),
    ("TB-18", "Groww cost to acquire a customer: ₹796 (H1 FY25) to ₹1,374 (H1 FY26)", "https://entrackr.com/news/growws-customer-acquisition-cost-spikes-73-in-h1-fy26-10799610"),
    ("SAV-02/03", "Stable Money: about ₹5,000 crore invested; Series C at ₹2,507 crore post-money", "https://entrackr.com/exclusive/exclusive-stable-money-kicks-off-series-c-with-143-mn-from-existing-investors-12226556"),
]


def build():
    src = "".join(f"<tr><td>{a}</td><td>{b}</td><td style='word-break:break-all'>{c}</td></tr>" for a, b, c in SOURCES)
    sources = (f'<div class="pb"></div><h2>Sources</h2><p class="small">IDs refer to rows in our research files. Bachatt figures are company claims. '
               f'Items marked "our estimate" or "to verify" are not sourced facts.</p><table><colgroup><col style="width:16%"><col style="width:42%"><col style="width:42%"></colgroup>'
               f"<tr><th>ID</th><th>What</th><th>Link</th></tr>{src}</table>")
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>Bachatt teardown memo</title><style>{CSS}</style></head><body>{SUMMARY}{BODY}{sources}</body></html>'
    out = HERE / "Bachatt_teardown_memo.html"
    out.write_text(html)
    pdf = HERE / "Bachatt_teardown_memo.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf)


if __name__ == "__main__":
    build()

# [Name]: final storyline (v11, editor's merge of drafts A and B)

Merged 3 Oct 2026 from `draft_A.md` (customer-insight lens) and `draft_B.md` (investor-memo lens). Every number below has been checked against its source row or model table, and each check is a row in `verify.csv` next to this file.

**How to read the source keys**
- `SIZE-xx` and `GIG-xx` are rows in `janta_pipe/research_sizing.csv` and `research_gig30k.csv`.
- `NG-`, `TB-`, `XB-`, `XL-`, `LS-`, `LEV-`, `REG-` and `EVD-` are rows in `research/nongig.csv`, `tri_behaviour.csv`, `xs_bachatt.csv`, `xs_lending.csv`, `lend_self.csv`, `levers.csv`, `regulation_rails.csv` and `market_benchmarks.csv`.
- `tables/...` is the founder's lending model. It is quoted as it stands and never recomputed. The founder's past lending data is cited as `tables/inputs_founder_*.csv`.
- A name in quotes, such as 'why', is a slide in the current deck.

**Rounding rule used throughout**
- On the slide, numbers are round and rounded in the safe direction: down for a value or a size, up for a cost or a capital need, and toward the stricter side for a pass mark.
- Speaker notes quote the model to the nearest rupee or to two decimals.

---

## 1. The thesis and the three numbers to remember

**Thesis, in one line:** [Name] moves the daily saving habit that city business owners already have into a fund in their own name, and lends on the record it builds. Savings is the hook; the loan we make ourselves is the business.

| # | Number | What it says | Slide | Source |
|---|---|---|---|---|
| 1 | **1.4 crore** | City business owners earning over ₹30k a month gross. This is our customer, and a model estimate (range 1.0–1.8 crore). | S2 | SIZE-16 |
| 2 | **₹4,500 crore** | Shop loans PhonePe arranged in FY25, seeing only its own QR's slice of the shop's money. The money in this market is in lending. | S5 | XL-10 |
| 3 | **1 in 7** | Savers who must borrow each year for a shop owner to pay back the cost of winning them (break-even 14.24%; the model assumes 20%). | S9 | `tables/lend_breakeven.csv`, takeup |

---

## 2. Customer insights, ranked

The first three each get a main slide (S3, S4, S5). Insight 4 shapes the product (S6) and the first test (S9). Insight 5 is the customer slide (S2).

**1. They already save every day, but with the wrong partner.** An agent collects cash at the counter for a credit co-op society, which pays low interest, charges a penalty for taking money out early, and can fail.
*So what:* we don't have to create a habit, only give an existing one a better home.

**2. Saving is how they earn a loan.** The society that keeps their money is the one that lends it back to them. Meanwhile most small businesses have no formal credit.
*So what:* the loan is what they really want, and a daily saving streak is a record they can build themselves. This is the link that makes savings the hook and the loan the business.

**3. Each lender sees one slice of their money, and the slices meet only in their own bank account.**
- PhonePe and Paytm see the sales on their own QR code.
- Swiggy and Uber see their own payout.
- No QR company or platform controls the person's own bank account.

*So what:* sit at the bank account. The pipe then needs nobody's permission, and it works for a shop owner and a gig pro alike.

**4. Their money comes in unevenly, so a fixed daily debit misses days, and savers drift away.**
*So what:* treat missed days as normal, and make "are they still saving?" the pilot's first number.

**5. The customer worth serving is the better-off owner. In gig work, only skilled pros qualify, because take-home pay is far below gross.**
*So what:* aim at the top of the market, size loans on take-home pay, and leave delivery riders out as borrowers.

---

## 3. The storyline: 9 main slides, including the cover

**The titles alone, in order:**
1. [Name] turns the daily saving habit people already have into a record we lend on
2. Our customer is the better-off city business owner: about 1.4 crore people
3. Many already save every day, in cash with an agent, at low interest and real risk
4. Saving is how they earn a loan; most small businesses have no formal credit
5. Each lender sees one slice of their money; the slices meet only in their own bank
6. [Name] auto-saves ₹100 a day from their bank into a fund in their name, then lends on it
7. Bachatt shows owners sign up to save daily; PhonePe sells it too, so saving is no moat
8. Lending it ourselves makes a saver worth about ₹200, far more than referring the loan
9. The bet: savers stay, 1 in 7 borrow, and losses stay low. A pilot tests all three first

**The arc:**
- the thesis (S1);
- who the customer is (S2);
- three customer insights (S3–S5);
- the idea that follows from them (S6);
- the proof and the warning (S7);
- the money (S8);
- what must be true (S9).

All titles are 74–88 characters, and each carries at most one number.

Bachatt and gig workers are not chapters:
- Bachatt appears once, as proof and as warning (S7).
- Gig pros appear where they strengthen the argument: as a side slice of the customer (S2), as "their pay lands in their own bank" (S5), and as "reached the same way, direct" (S6).

Each slide spec below gives a **SO WHAT** line. It goes on the slide as a one-line footer above the sources, so every slide answers "so what".

---

### S1. Cover

**TITLE:** [Name] turns the daily saving habit people already have into a record we lend on

**SO WHAT:** The habit exists already; we move it, and the loan is the business.

**PICTURE:** one centred illustration.
- A phone screen shows a row of coins, each labelled "₹100", dropping one a day into a jar labelled "[Name] · in your name".
- A curved arrow leaves the side of the jar, labelled "loan". The arrow is in the accent colour; it is the only highlight.
- Below it, the strapline in large type: "Save every day. Borrow on your record."
- One small line under the strapline: "Savings is the hook. The loan is the business."
- No other numbers.

**NUMBERS:**
- ₹100 a day: the design amount ('k-pipe').

**SPEAKER NOTES:**
- What it is: a daily savings pipe for better-off city business owners, plus skilled gig pros. It runs from the person's own bank account, so it needs no QR company's or platform's permission.
- The founder's decisions this deck takes as given:
  - savings is the hook and need not pay;
  - loans are the business, and we lend ourselves;
  - gig pros are reached direct, through their own bank;
  - there is no employer or payroll route.
- Two words used throughout:
  - "gross" means pay before work costs, and is used for market size;
  - "take-home" means pay after work costs, and is used for loan size.
- "[Name]" is a placeholder. Any working name still needs a trademark search and a domain check ('cover').

**SOURCE LINE:** none on the cover.

---

### S2. Who: the customer (insight 5)

**TITLE:** Our customer is the better-off city business owner: about 1.4 crore people

**SO WHAT:** Aim at the top of the market, not the average shop. Gig pros are a small side slice.

**PICTURE:** a two-bar funnel, top to bottom, with bar widths to scale (1.4 is about 4% of 34).
- Bar 1, grey, full width: "About 34 crore self-employed in India (2025)".
- Connector text between the bars, with no numbers: "minus unpaid family helpers, farmers, village businesses, and everyone earning under ₹30k".
- Bar 2, the accent colour and the highlight: "≈1.4 crore run a business in a town or city and earn over ₹30k a month, gross (before business costs)". Under it, small: "our model; range 1.0–1.8 crore".
- To the right of bar 2 sits a small separate dot, drawn as an outline only. It is joined by a dashed line marked "not added in", and labelled "+ skilled gig pros (home-service pros, some owner-drivers): a few lakh at most take home over ₹30k".

**NUMBERS:**
- About 34 crore self-employed (SIZE-03; 33.97 crore, PLFS 2025).
- ≈1.4 crore over ₹30k gross, range 1.0–1.8 crore (SIZE-16; model estimate).
- "A few lakh at most" gig pros taking home over ₹30k (GIG-24; our judgement, 0.1–3 lakh).

**SPEAKER NOTES:**
- Bachatt's "30 crore" holds as a headline (SIZE-20): PLFS 2025 counts about 34 crore self-employed. But 9.2 crore of them are unpaid family helpers and 13 crore are farmers, which leaves 6.0 crore running non-farm work in towns and cities (SIZE-03, SIZE-04, SIZE-07, SIZE-08). The full funnel is in appendix A1.
- Why "better-off": the average urban self-employed earner makes ₹23,012 a month, gross (PLFS 2025; SIZE-10). Our core is the roughly 23% of the 6.0 crore who clear ₹30k gross (SIZE-15). That share is our model, scaled from the only published spread of earnings (2017-18), hence the 1.0–1.8 crore range. No source splits any of this by city tier.
- Gig comes from a different source base, so it is never added to the 1.4 crore. NITI's 1.43 crore gig workers is a 2022 projection for 2025-26, not a count (GIG-02, SIZE-23). A full-time delivery rider grosses ₹27.8k but takes home ₹18.8k (GIG-19), so only skilled pros clear ₹30k take-home.
- Riders are out as borrowers. In the founder's model, a rider is worth −₹275 even if savers repay better (`tables/lend_customer.csv`: Delivery riders, lend, savers safer, 1 in 5 borrowing, evidence cost to win).

**SOURCE LINE:** MoSPI PLFS Annual Report 2025; the last step is our model; NITI Aayog (2022); IDinsight (2025).

---

### S3. Insight 1: how they save today

**TITLE:** Many already save every day, in cash with an agent, at low interest and real risk

**SO WHAT:** We don't create a habit; we give an existing one a better home.

**PICTURE:** one loop of four nodes, drawn as a shop-counter scene, with arrows running clockwise.
1. "The owner hands over cash at the counter"
2. "An agent collects it every day"
3. "A credit co-op society holds it"
4. "It lends back to its own members" (the arrow returns to node 1)

Other elements:
- The arrow from node 1 to node 2 is highlighted in the accent colour and labelled "no effort: the agent comes to you".
- Three small red tags hang on node 3: "low interest", "a penalty to take it out early", "a credit society can fail".
- Two number callouts sit to the right:
  - "2 lakh+ daily agents in Maharashtra alone (2025–26)";
  - "Sahara's co-op societies: 27 lakh of 1.35 crore depositors repaid by Jul 2025".

**NUMBERS:**
- 2 lakh+ agents (SIZE-22, 'size').
- 27 lakh of 1.35 crore repaid (27.3 lakh by 23 Jul 2025; 'why', 'size').

**SPEAKER NOTES:**
- Why the habit survives: the agent comes every day and takes cash, so saving takes no effort, and the society that holds the money lends to its members ('why').
- What it costs the saver: low interest and a penalty for taking money out early, as Bachatt's CEO describes these societies (Inc42, Apr 2025; 'why').
- Insurance, said precisely: deposit insurance (DICGC) covers banks, including co-operative banks. So daily schemes run by co-op banks and public-sector banks (such as Canara Bank's Nitya Nidhi) ARE insured, and credit co-op societies are NOT ('why', 'size'). Our fund is not deposit-insured either, so we say "regulated, in your own name, out any day", never "insured".
- These numbers are clues, not a count. No national or city-tier count of daily-deposit savers exists (SIZE-22). In Maharashtra alone, the 2 lakh+ agents serve about 1 crore families.
- Gig pros save differently: in a 2022 Bengaluru diary study, none of 22 platform workers used a formal savings product, and chit funds were the most common (GIG-45).
- The honest limit: an app pulls from a bank account and cannot collect cash at the door (open question 1).

**SOURCE LINE:** Indian Cooperative (2025–26); DICGC; Angel One on Sahara refunds (Jul 2025); Inc42 (Apr 2025).

---

### S4. Insight 2: why they save

**TITLE:** Saving is how they earn a loan; most small businesses have no formal credit

**SO WHAT:** The loan is what they want, and a saving streak is a record they can build themselves.

**PICTURE:** two doors side by side, with an owner figure standing between them holding a folder marked "my record?".
- Left door, wide open, green, and the highlight: "Co-op society: save with us, borrow from us".
- Right door, nearly shut, grey: "Bank or lending app: show me your credit record". A callout under it reads "Only about 4 in 10 Indian small businesses, sole owners included, have formal credit".
- One line in the accent colour runs under both doors: "A daily saving streak is a record they can build themselves."

**NUMBERS:**
- About 4 in 10 have formal credit (NG-042: ~41% of commercial enterprises, incl. proprietors; XB-09: 41% with an active formal loan, Mar 2026).

**SPEAKER NOTES:**
- Saving and borrowing are one relationship for them. The society that keeps their money lends it back, so the deposit doubles as the route to a loan ('why').
- The same pattern abroad: in Kenya, M-Shwari savers said the main appeal of saving was "increasing access to credit in the future", not the interest rate (TB-33, CGAP 2015; foreign evidence).
- The 4 in 10 covers all Indian MSMEs, sole owners included, as of Mar 2026 (TransUnion CIBIL–SIDBI MSME Pulse, Jul 2026; NG-042, XB-09). Our better-off owners may have more formal credit than this average, and no source splits it.
- The founder's own past lending saw the same wall from the other side:
  - 1 in 4 applicants were approved, and most applicants had credit scores that were not good enough, so they had a record that said no (2019–22, all channels; `tables/inputs_founder_*.csv`, approval_rate and first_loan_loss rows).
  - Most of those loans came through platforms (`tables/deck_facts.csv`, founder data), so this was a different group from city shop owners. It stays in the notes (open question 3).
- The honest gap: nobody has shown that savers repay better, and the founder's own data calls it a hunch (saver_signal row). The pilot must show it (S9).

**SOURCE LINE:** TransUnion CIBIL–SIDBI MSME Pulse (Jul 2026); CGAP (2015); Inc42 (Apr 2025).

---

### S5. Insight 3: how money reaches them

**TITLE:** Each lender sees one slice of their money; the slices meet only in their own bank

**SO WHAT:** Sit at the bank account. It needs no QR company's or platform's permission, and it works for a shop owner and a gig pro alike.

**PICTURE:** hub and spoke.
- The centre is the largest element, in the accent colour and the highlight: "Their own bank account: the one place all their money can meet. No QR company or platform controls it."
- Five arrows flow in: "QR code 1", "QR code 2", "QR code 3 …", "Cash, once banked", "Platform payout (gig pros)".
- A magnifier sits over "QR code 1" only, labelled "PhonePe / Paytm lend on this one QR's sales. PhonePe arranged ₹4,500 crore of shop loans in FY25, the instalment cut from the day's sales."
- An eye sits over "Platform payout" only, labelled "Swiggy / Uber see only their own payout".
- A small badge near the QR arrows reads "about 9 QR codes per merchant (FY25)".

**NUMBERS:**
- ₹4,500 crore (XL-10: ₹4,507 crore, PhonePe merchant-loan disbursals, FY25).
- About 9 QR codes per merchant (SIZE-19).

**SPEAKER NOTES:**
- Payment apps lend against money coming in. PhonePe and Paytm settle a shop's QR sales, so they see them and cut the daily instalment before the shop is paid ('k-incumbents'). PhonePe's shop loans grew from ₹11 crore in FY23 to ₹4,507 crore in FY25. PhonePe arranges these loans for its lending partners rather than lending them itself (NG-029, XL-10).
- But each app sees only its own QR. India's 6.5 crore UPI merchants hold 56.86 crore QR codes (FY25; businesses, not people; SIZE-19), and only about 1 in 4 registered PhonePe shops used it in a month (NG-038).
- Small shops' UPI money lands straight in the owner's own personal bank account (P2PM merchants; DFS FAQ, Sep 2026; NG-030). Gig pay lands in the worker's own bank account, which platforms require (GIG-26). Uber Auto riders have paid drivers directly since Feb 2025 (GIG-28).
- Cash counts only once it is banked (open question 1).
- Payments earn almost nothing from small shops: there is no UPI fee on shop payments up to ₹2,000, even after 15 Oct 2026 (NG-030, 'qr'). The money is in the loan.

**SOURCE LINE:** Business Today on PhonePe's DRHP (Mar 2026); PIB (Dec 2025); PhonePe DRHP coverage (Hans India); DFS FAQ (Sep 2026); IDinsight (2025).

---

### S6. The idea

**TITLE:** [Name] auto-saves ₹100 a day from their bank into a fund in their name, then lends on it

**SO WHAT:** One pipe the customer owns and no QR company or platform can cut off, plus a loan that grows with the streak.

**PICTURE:** a flow of three boxes, left to right, with no QR company's or platform's logo anywhere.
1. "Money lands in their bank: from any QR, cash they bank, or a platform payout"
2. "₹100 a day moves by UPI AutoPay into a fund in their own name. They can take it out any day." This box is in the accent colour and is the highlight.
3. "We lend to them ourselves. The loan grows with how long and how steadily they save."

A thin amber strip runs under box 2: "Income is uneven, so debits miss: 55–90% of AutoPay attempts failed at major banks (Aug 2025). The streak allows for missed days."

**NUMBERS:**
- ₹100 a day (design amount, 'k-pipe').
- 55–90% of AutoPay attempts failed (TB-13).

**SPEAKER NOTES:**
- Why the person's own name matters: SEBI requires fund money to come from the investor's own bank account (GIG-32). So no QR company or platform can own the account, and it follows the person across QR codes, banks and platforms. Liquid funds can pay out instantly, up to ₹50,000 a day per fund (REG-041).
- ₹100 a day is about ₹2,500 a month at 25 saving days ('k-pipe').
- The 55–90% counts AutoPay attempts, not savers, across all mandates, and most failed for lack of balance (TB-13). Missed days are a design rule, not a failure.
- The loan is unsecured and sized on the streak, not lent against the balance.
  - PhonePe already lends against mutual funds (Sep 2025; 'b-copied'), so we never say "nobody lends against savings".
  - Almost nobody borrows that way: about 0.3% of fund investors ever did, through the largest platform for it (TB-44, rough ratio).
- What we give up is deduction at source: we collect by a mandate on their bank account, like any other lender. Gig pros join the same way, direct through their own bank, with no platform deal and no employer or payroll route (founder's decisions).

**SOURCE LINE:** SEBI mutual fund master circular (Mar 2026); SEBI liquid-fund rule; NPCI AutoPay data via Mint (Aug 2025).

---

### S7. Proof and warning

**TITLE:** Bachatt shows owners sign up to save daily; PhonePe sells it too, so saving is no moat

**SO WHAT:** The saving can be copied, so we must win on the loan.

**PICTURE:** a horizontal timeline with four dots. Bachatt's dots are in one colour and PhonePe's in another.
- "May 2025: Bachatt launches daily app saving for shop owners"
- "Dec 2025: PhonePe launches its own Daily SIP"
- "Feb 2026: Bachatt has ≈1 lakh daily savers (our estimate)"
- "Aug 2026: PhonePe Daily SIP has 5 lakh+ investors"

Under the timeline, one arrow in the accent colour: "The saving is easy to copy → the money must come from the loan".

Rule for the builder: no bars, because the two counts are not like-for-like.

**NUMBERS:**
- ≈1 lakh Bachatt daily savers (XB-03; our estimate, Feb 2026).
- 5 lakh+ PhonePe Daily SIP investors, everyone onboarded since launch ('b-copied').

**SPEAKER NOTES:**
- Bachatt (app live May 2025, $16M raised) runs the shop-owner version of this pipe: ₹51 a day by UPI AutoPay into debt funds, then loans of up to ₹5 lakh referred to 7 lending partners for a fee ('a1-facts', XB-10).
- It shows owners will sign up. It has published nothing on whether they keep saving, borrow or repay ('b-unproven').
  - The ≈1 lakh is our estimate: 2M fund purchases in Feb 2026 ÷ about 20 debits each.
  - Bachatt itself claims 3M users (XB-03).
- PhonePe launched Daily SIP from ₹10 a day in Dec 2025, seven months after Bachatt launched, with the same funds and the same AutoPay. Its 5 lakh+ counts everyone onboarded since launch, so it is never set against Bachatt's daily savers as bars ('b-copied').
- PhonePe says shop owners are taking up Daily SIP, and it already lends against mutual funds (Sep 2025). The one piece we did not find there is auto-saving a slice of each day's QR sales, so the window may be short ('hold').
- Whoever lends and collects earns most. Referring a ₹2 lakh loan earns ₹2,000–5,000 once, while PhonePe earns about ₹14,600 on the same loan because it also collects it. That PhonePe figure is a rough ratio ('b-copied', 'model').

**SOURCE LINE:** Bachatt Series A release (Mar 2026); bachatt.app (Oct 2026); Angel One and Outlook Business on PhonePe Daily SIP (2025–26).

---

### S8. The money

**TITLE:** Lending it ourselves makes a saver worth about ₹200, far more than referring the loan

**SO WHAT:** Savings is the hook; the loan we make ourselves is the business.

**PICTURE:** three horizontal bars from one zero line, with values printed at the bar ends.
- Caption above the bars: "What one shop owner is worth to us over 5 years, after about ₹500 to win them, if 1 in 5 savers borrow a year (the founder's lending model)".
- Bar 1, grey, just left of zero: "Refer the loan to a lender: −₹54".
- Bar 2, the accent colour and the highlight: "Lend ourselves, normal industry losses: about +₹200".
- Bar 3, the accent colour in a lighter shade: "Lend ourselves, if savers repay better: about +₹850".
- One line under the bars: "Savings is the hook: the fund pays us almost nothing."

**NUMBERS:** all from `tables/lend_customer.csv`, Shopkeepers rows, takeup 0.2, evidence cost to win (₹499.24):
- −₹54 (referral, −54.01);
- about +₹200 (lend, industry steady state, 204.59);
- about +₹850 (lend, savers safer, 858.60).

**SPEAKER NOTES:**
- These are the founder's model numbers for shop owners, quoted as they stand. Over 5 years, with 1 in 5 borrowing and a ₹499 cost to win each saver:
  - refer: −₹54;
  - lend at normal (steady-state) losses: +₹205;
  - lend if savers repay better: +₹859.
- Savings needn't pay, and it doesn't: at ₹100 a day the fund house pays us about ₹30–75 a year per saver ('money', 'k-money').
- Losses decide everything. At today's higher industry losses, lending ourselves is worth −₹580 per saver (same file, industry today), so the same saver swings from −₹580 to +₹859 on repayment alone.
- If 35% borrow, as the founder expects, lending earns +₹738 at normal losses and +₹1,882 if savers repay better, while referring earns +₹285 (same file, 0.35 rows). That is why the title says "far more" rather than "referring loses money".
  - Skilled gig pros come out thinner than shop owners: +₹21 at normal losses and +₹550 if savers repay better (same file: Drivers and home-service workers, 0.2).
- How big it gets (`tables/lend_prize.csv`; new appendix slide):
  - Winning 5 lakh shop owners a year is about 1% of Udyam's micro enterprises.
  - That means nearly ₹1,750 crore lent a year, on a book of nearly ₹1,000 crore.
  - Each year's intake is worth about ₹6 crore in a typical future, and nearly ₹38 crore if savers repay better. Both are after the NBFC's own running cost of ₹5 crore a year.
- Lending ourselves needs an NBFC licence either way: co-lending happens only between regulated lenders, and each keeps at least 10% of every loan (LS-01). The capital this needs is open question 2.

**SOURCE LINE:** the founder's lending model (`tables/lend_customer.csv`, `lend_prize.csv`); Kotak MF on trail commission; RBI Co-Lending Directions 2025.

---

### S9. What must be true

**TITLE:** The bet: savers stay, 1 in 7 borrow, and losses stay low. A pilot tests all three first

**SO WHAT:** The pilot reports these three numbers before anything else.

**PICTURE:** three gates in a row, left to right. Each is a tall arch with a question on top and its pass mark below.
1. "Still saving?" Pass mark: "still saving after a year" (no number). Small line below it: "the first number the pilot reports".
2. "Borrow?" Pass mark: "at least 1 in 7 savers a year".
3. "Repay?" Pass mark: "losses at most 7.5% of the loan book a year". A red marker beside the pass mark reads "digital lenders today: about 7–9%". This gate is the highlight, because it has the thinnest margin.

One line under the gates: "Bachatt has published none of these three. Our pilot reports them first."

**NUMBERS:**
- 1 in 7 (`tables/lend_breakeven.csv`, takeup break-even 0.14242).
- 7.5% (same file, losses break-even 0.07564).
- About 7–9% (LEV-021, LEV-022, LEV-029).

**SPEAKER NOTES:**
- Each pass mark is the founder's model break-even for shop owners, found by moving one number at a time (`tables/lend_breakeven.csv`):
  - at least 14.24% of savers borrow a year (the model assumes 20%);
  - losses stay at or below 7.56% of the loan book a year (it assumes 6%).
- Two more must hold (same file; the full chart is in appendix 'k-true'):
  - winning a saver must cost under ₹704 (today ₹499);
  - the interest rate must stay at or above 24.43%.
- Across 10,000 simulated futures, the cost of winning a shop owner is earned back in just under 64% of them (`tables/lmc_summary.csv`).
- Why gate 3 is the hard one: digital lenders lost about 7–9% of their loan book a year in FY25–26, around or above our 7.5%. So savers must repay better than today's market, not just as well as it.
  - The figures: Groww 7.06%, KreditBee 7.7%, Kissht 8.5–9.0% (LEV-029, LEV-022, LEV-021).
  - Two other benchmarks are measured differently and must not sit beside the 7.5%: Paytm-sourced shop loans carry a 4.5–5% expected loss (XB-07), and the founder's past 3-month first loans lost 6–7% of the amount lent.
- Why we think savers might repay better: bank loans to savings-linked self-help groups had 2.05% bad loans, against 8.72% across microfinance (EVD-03, NABARD, Mar 2024). That is a correlation, not proof. Nobody, Bachatt included, has published data showing that savers repay better.
- Gate 1 is the first worry: over a third (35.6%) of SBI's ₹250 daily SIPs opened in FY26 had stopped by 1 Apr 2026 (NG-033). The model assumes about 24 in 100 are still saving after a year (`tables/lend_funnel.csv`).
- The pilot reports three numbers: the share still saving at months 6 and 12, the share who borrow, and losses against 7.5%.

**SOURCE LINE:** the founder's lending model (`tables/lend_breakeven.csv`, `lmc_summary.csv`); CRISIL, CareEdge ratings notes (2025–26); NABARD (2024); SBI Funds RHP via Business Standard (Jul 2026).

---

## 4. Appendix map: which existing slides support which main slide

| Main slide | Existing appendix slides (current ids) | New appendix slide |
|---|---|---|
| S1 Cover | 'cover' is rebuilt as S1 | none |
| S2 Customer | 'ax-sizing' (A1, full funnel), 'who' (A17), 'segments' (A19), 'g-count' (A23), 'g-gross' (A24), 'g-pros' (demoted from main) | none |
| S3 How they save | 'size' (A2), 'why' (A3), 'what' (A4), 'a3-others' (A10, daily-agent panel) | none |
| S4 Save to earn a loan | 'why' (A3) | none. Add NG-042/XB-09 and TB-33 to a sources slide. |
| S5 One slice | 'qr' (A5), 'k-slice' (A6, already the hub picture), 'doors' (A8), 'a2-phonepe-paytm' (A9), 'vs' (A18), 'ax-gig' (A25), plus 'k-incumbents' and 'g-paid' (both demoted from main) | none |
| S6 The idea | 'disrupt' (A7), 'what' (A4), 'compare' (A13), 'product' (A14) | none |
| S7 Proof and warning | 'b-proves' and 'b-copied' (both demoted from main, full versions), 'a1-facts' (A11), 'b-unproven' (A12), 'edge' (A20), 'risk' (A21), 'hold' (A22) | none |
| S8 Money | 'k-money' (demoted from main: the 4-bar version with exact values), 'model' (A15), 'money' (A16) | **How big:** `tables/lend_prize.csv` at 1, 5 and 10 lakh shop owners a year (lent a year, average book, capital if co-lending vs whole book, value in a typical future vs if savers repay better) |
| S9 Must be true | 'k-true' (demoted from main: all four break-evens with evidence ranges), 'b-unproven' (A12), 'hold' (A22) | none |
| Sources | 'a4-sources', 'sources2', 'sources3' | none |

**Where the current main slides go:**
- 'cover' becomes S1. 'k-who' becomes S2. 'k-save' becomes S3.
- 'k-incumbents' is demoted; S5 is drawn from 'k-slice'.
- 'k-pipe' becomes S6. 'b-proves' and 'b-copied' are merged into S7.
- 'k-money' becomes S8 (its full version moves to the appendix). 'k-true' becomes S9 (its full version moves to the appendix).
- 'g-pros' and 'g-paid' go to the appendix.
- S4 is new on the main line.
- 'sec-bachatt', 'sec-gig', 'b-does' and 'b-earns' drop out, because Bachatt and gig are no longer chapters.

**Fix in the appendix before it ships.** These are not on the main line, but they contradict it.
1. Unlike loss measures are compared. 'k-true', 'b-unproven', 'b-proves', 'hold' and 'risk' set Paytm's 4.5–5% expected loss, and 'k-true' also the founder's 6–7% first-loan loss, as the bar for a yearly 7.6% break-even. These are different measures, so label them "measured differently" or use the yearly digital-lender figure.
2. 'k-true' shows 7.6% and 64%, while the main line says 7.5% and "just under 64%". Align them.
3. 'a2-phonepe-paytm' says PhonePe "lent" ₹4,507 crore. PhonePe arranges the loans for 56 lending partners, so say "arranged".
4. The agents' commission conflicts across sources. NG-041 says Maharashtra capped pigmy agents' pay at 2.5% (down from 3–4%) in 2026. But 'size', 'why', 'what', 'a3-others' and 'k-save' say "up to 3%" or "raised from 2.5% to 3%". Check before the appendix ships; the main line no longer uses this figure.
5. `tables/deck_facts.csv` (digital_credit_cost) says 7–10%, but the rows it cites give 7.06–9.0%. The main line uses 7–9%.

---

## 5. What changed versus each draft, and why

**Versus draft A (customer-insight lens).** The arc and the three insight slides (S3–S5) are A's.
- **S2 title** now uses B's wording: "the better-off city business owner" states the insight in one number.
- **S4 title** dropped "formal lenders see no record and mostly say no", for two reasons:
  - The 4-in-10 figure measures who has formal credit across all MSMEs. It does not measure refusals, and it does not describe our better-off core.
  - The founder's 1-in-4 approval rate comes from a different group: most of those loans came through platforms, and its applicants mostly HAD scores. That is a record that says no, not "no record". It moved to the notes and to open question 3.
- **S7 title** takes B's so-what ("so saving is no moat").
- **S8 title** now carries the number and holds at both borrowing levels (see "Numbers dropped or changed" below).
- **S9**: A's three dials became B's three gates, which add retention. Cost-to-win moved to the notes. The loss bar is now like-for-like.
- **Dropped from A's notes:**
  - TB-14 (20 million mandates revoked a month), because it rests on a search summary of an unreadable page;
  - the NG-042 "55% new to credit" line (see "Numbers dropped or changed" below).

**Versus draft B (investor-memo lens).**
- **B's thesis was not used.** "Payment apps lend on what people receive; [Name] lends on what they keep" reads as a loan against savings. PhonePe already offers that, and almost nobody takes it (TB-44).
- **B's slide 3 is split back into two insight slides** (S3, S4). The founder wants at least three insight slides, and "saving is how they earn a loan" is the link from savings to loans.
- **B's slide 4 title led with ₹4,500 crore.** S5 now leads with the insight (one slice), and the ₹4,500 crore becomes evidence in the picture.
- **B's "how big" slide moved to S8's notes and a new appendix slide.**
  - Another main slide of model outputs would bring back "too many numbers".
  - The scale does not change the bet: its own value line ("about ₹6 crore typical vs nearly ₹38 crore if savers repay better") just restates S9.
  - The capital need became open question 2.
- **B's "not insured" tag** on the society became "a credit society can fail". The insurance detail is now precise in the notes.
- **B's "agent's cut of up to 3%"** was dropped, because the sources conflict (see fix 4 in section 4).
- **There is no "ask" slide.** The founder has not stated one, and the deck tests the story rather than pitching it. B's "what is the ask" question is folded into open question 2.
- **B's "why now / why us" notes** are dropped from the main line.

**Numbers dropped or changed during verification**
1. **Loss break-even 7.6% → 7.5%.** The source value is 7.564%. Rounding up overstates the losses the business can absorb.
2. **"1 in 4 applicants approved"** moved off the picture (A, S4) and into the notes, because its group differs from the slide's claim.
3. **"55% of businesses taking a first loan in FY25 were new to credit"** (A, S4 notes) was dropped. NG-042 says 55% of all entities given a loan (up to ₹1 crore exposure) were new to credit, which is not 55% of first loans. XB-09 gives 42% for FY26, so the two years conflict.
4. **Paytm's 4.5–5% and the founder's 6–7%** shown as the bar for the break-even (A S9, B S9, B open question 2) were replaced in the picture by digital lenders' 7–9% a year. That is the same measure as the model's 7.5%. The other two stay in the notes, labelled "measured differently".
5. **"Referring loses money" in the S8 title** became "far more than referring". At the founder's expected 35% borrowing, referring earns +₹285 (`lend_customer.csv`, Shopkeepers, referral, 0.35). The picture still shows −₹54 at the base case of 1 in 5.
6. **S8 bars rounded on the safe side.** +₹205 and +₹859 became about +₹200 and +₹850 (rounded down), and the ₹499 cost to win became about ₹500 (a cost, rounded up). The notes keep the exact model values.
7. **"64% of futures" became "just under 64%"** (0.6376).
8. **Scale figures (B)** gained honest qualifiers: "nearly ₹1,750 crore" (1,749.10), "nearly ₹1,000 crore" book (984.62), and "nearly ₹38 crore" (37.93). Capital is now "about ₹100 crore" and "about ₹330 crore" (98.46 and 328.21; costs, rounded up).
9. **Rate break-even "24.4%" became 24.43%** in the notes. As a pass mark, rounding it down would let a failing rate pass.
10. **"PhonePe copied it"** became "PhonePe sells it too" in the title. "Copied" is our reading; launching the same product seven months later is the fact.

---

## 6. Open questions for the founder (3)

1. **Cash.** S3 says many save in cash, but [Name] pulls from a bank account. Should we serve only owners whose takings already reach the bank (UPI plus banked cash), or does the story need a way to put cash in? The answer decides whether S3 → S6 reads as a simple switch or as a gap we haven't closed.
2. **Licence, capital and the pilot.** We lend ourselves, and that needs an NBFC licence, even to co-lend (LS-01). There are two routes:
   - take our own licence before the pilot;
   - lend through a partner NBFC for the pilot, and convert once savers prove they repay.

   At 5 lakh shop owners a year, the capital is about ₹100 crore if we co-lend and keep 10% of each loan, or about ₹330 crore to keep the whole book (`tables/lend_prize.csv`). The answer changes S8–S9 and the pilot. If this ever becomes a raise, the ask follows from it, so there is no ask slide for now.
3. **Your past lending data.** Can it go on slides? If so, as "why us" in the appendix, or in S4/S9's notes only?
   - 1 in 4 applicants were approved (2019–22, all channels), and most had credit scores that weren't good enough. Most of the loans came through platforms, so these were not city shop owners.
   - 6–7% of a 3-month first loan was never repaid. That is a per-loan measure, not the yearly 7.5% on S9, so the two must never sit side by side.

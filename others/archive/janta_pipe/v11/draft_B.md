# [Name]: storyline draft B, the investor-memo lens

Drafted 3 Oct 2026. This is a storyline, not slides. It is written to be read the way a sharp investor reads a memo in three minutes: who the customer is, the gap, the product, why it wins, how it makes money, how big it can get, and what must be true.

**Where the source keys live**
- `SIZE-xx`: `janta_pipe/research_sizing.csv`
- `GIG-xx`: `janta_pipe/research_gig30k.csv`
- `TB-xx`, `NG-xxx`, `LS-xx`, `EVD-xx`: `research/tri_behaviour.csv`, `nongig.csv`, `lend_self.csv`, `market_benchmarks.csv`
- `tables/...`: the founder's lending model, quoted as it stands and never recomputed
- A slide id in quotes (for example 'qr') is a slide in the current deck.

---

## 1. The thesis and the three numbers

**Thesis, in one line:** Payment apps and gig platforms lend against the money people *receive*. [Name] lends against the money they *keep*: ₹100 a day, saved from their own bank into a fund in their own name.

**The memo in six lines.** The storyline follows this order.
1. **Customer.** About 1.4 crore city business owners earn over ₹30k a month gross. A few lakh skilled gig pros are one more slice.
2. **Insight.** They already save every day, with a cash agent, and they save in order to earn a loan.
3. **Gap.** Payment apps lend against one QR's sales. The savings apps that hold what people keep only refer loans, for a one-off fee.
4. **Product.** ₹100 a day goes by UPI AutoPay into a fund in the person's own name, and they can take it out instantly. The loan grows with the saving streak, and we lend it ourselves.
5. **Why it wins.** The saving product can be copied: PhonePe copied Bachatt in seven months. The edge is lending on the record ourselves, from a seat no QR company or platform can own.
6. **Money and the bet.** Lending ourselves earns ₹205–859 per saver won; referring loses ₹54. The business pays back if 1 in 7 savers borrow and losses stay under 7.6%. A pilot must also show that savers keep saving.

**The three numbers an investor should remember**

| # | Number | What it says | Source |
|---|---|---|---|
| 1 | **1.4 crore** | City business owners earning over ₹30k a month gross: our customer. Model estimate, range 1.0–1.8 crore. | SIZE-16 |
| 2 | **₹4,500 crore** | PhonePe's shop loans in FY25, up from ₹11 crore two years earlier and repaid out of the shop's daily sales. The money in this market is in lending, not in payments. | 'a2-phonepe-paytm' |
| 3 | **1 in 7** | Savers who must borrow each year for the business to pay back. The break-even is 14.2%, and the model assumes 20%. | tables/lend_breakeven.csv, row takeup |

(This table is for the editor only. None of it goes on a slide.)

---

## 2. Customer insights

Each insight below says which slide carries it.

### Insight 1. They already save every day; they just do it with a person who comes to the shop.
- **Evidence:**
  - 2 lakh+ daily collection agents serve about 1 crore families. This is Maharashtra's credit co-op societies only, 2025–26; no national count exists (SIZE-22; 'k-save', 'size').
  - That money has no deposit insurance, because DICGC covers banks and not credit co-op societies. Sahara's co-ops had repaid 27 lakh of their 1.35 crore depositors by Jul 2025 ('why').
- **So what:** we don't have to create a habit, only move it somewhere safer that pays more. The catch is that the agent takes all the effort away and accepts cash. An app can match "no effort" with an automatic debit, but it can't collect cash at the door.
- **Carried on:** slide 3.

### Insight 2. They save to earn a loan, not for the interest, and they don't want to borrow their own money back.
- **Evidence:**
  - The co-op society that takes the daily deposit lends to its own members, so the deposit is the route to a loan later ('why'). In Kenya, M-Shwari's customers said the main appeal of saving was "increasing access to credit in the future", not the interest rate (TB-33, CGAP 2015; a foreign example, not Indian data).
  - Borrowing against your own funds is rare. Only about 0.3% of Indian mutual-fund investors have ever borrowed against them through the largest platform for it (TB-44, 2025–26, a rough ratio). M-Shwari dropped loans secured on savings soon after launch (TB-33).
- **So what:** the promise of a loan is what keeps people saving, so the loan is both the business and the reason savers stay. The loan must also be unsecured and bigger than the balance, sized on how long and how steadily they have saved. Nobody borrows their own ₹2,500 back.
- **Carried on:** slides 3 and 5.

### Insight 3. No lender sees the whole person. Each sees only the money that flows through it.
- **Evidence:**
  - India's 6.5 crore UPI merchants hold 56.86 crore QR codes, about 9 each (FY25). These count businesses, not people (SIZE-19; 'qr'). Only about 1 in 4 registered PhonePe shops use it in a month ('qr').
  - Gig pay lands in the worker's own bank account, because a bank account is an entry requirement for platform work (GIG-26; IDinsight 2024, delivery riders on one platform).
- **So what:** every rupee ends up in the person's own bank account: sales on any QR, cash once banked, and platform payouts. A daily saving taken from there is the one record that spans all of it and shows what is left after costs. That is our thesis; nobody has yet published data showing it predicts repayment.
- **Carried on:** slides 4 and 5.

### Insight 4. Signing up is easy; staying is the hard part.
- **Evidence:**
  - 35.6% of SBI Mutual Fund's ₹250 daily Jan Nivesh SIPs registered in FY26 had stopped by 1 Apr 2026 (NG-033; 'b-unproven').
  - In Aug 2025, 55–90% of UPI AutoPay attempts failed at major banks, mostly for lack of balance. This counts attempts, not savers, across all mandates (TB-13).
- **So what:** the product has to cope with missed days. The first number the pilot reports is how many people are still saving, not how many signed up. This is also the gap in the competition: Bachatt publishes users but not retention.
- **Carried on:** slides 6 and 9.

### Insight 5. For gig workers, ₹30k gross is not ₹30k in hand, so only skilled pros have room for a loan.
- **Evidence:**
  - Full-time delivery riders gross ₹27.8k a month and take home ₹18.8k after fuel and repairs (GIG-19; IDinsight, 2024, one platform).
  - Urban Company pros who do 30+ jobs a month (65% of its active pros) take home ₹35.6k on average (GIG-16; company figure, Apr–Dec 2025).
- **So what:** our gig slice is skilled home-service pros and owner-drivers, a few lakh people at most (GIG-24, a judgement), not delivery riders. Their loans are sized on take-home pay. We reach them through their own bank, not through Swiggy or Uber.
- **Carried on:** slides 2 and 5.

---

## 3. Storyline: 9 main slides, including the cover

**The titles alone tell the story:**
1. [Name] turns a small daily saving into a loan record that no QR code or platform owns
2. Our customer is India's better-off city business owner: about 1.4 crore people
3. They already save daily with a cash agent, because saving is how they earn a loan
4. Payment apps lend against sales on their own QR: PhonePe arranged ₹4,500 crore in FY25
5. [Name] auto-saves ₹100 a day from the person's own bank, then lends on that record
6. Bachatt proved owners sign up to save daily; PhonePe copied it, so the edge is lending
7. Loans are the business: lending ourselves earns ₹200–850 per saver; referring loses money
8. At scale it is a ₹1,000 crore loan book; whether savers repay better decides its worth
9. The bet: savers stay, 1 in 7 borrow, and losses stay low. A pilot tests all three first

**Why Bachatt and gig workers are not chapters.** An investor asks two questions they answer: "who else is doing this?" and "is the gig angle real?"
- Bachatt appears once, as proof and as competition (slide 6).
- Gig workers appear as a slice of the customer (slide 2) and as evidence that the pipe needs no platform (slide 5).

Two separate chapters made the old deck read like a report on Bachatt with a gig study attached.

---

### Slide 1. Cover
**TITLE:** [Name] turns a small daily saving into a loan record that no QR code or platform owns

**PICTURE:** a shop owner's phone. A daily ₹100 tick drops into a jar with their name on it, and a loan arrow comes back out.

**NUMBERS:** none on the cover. The ₹100 in the picture comes from 'k-pipe'.

**NOTES:**
- The thesis: payment apps and platforms lend against the money people receive; we lend against the money they keep.
- Who it is for: India's city business owners, plus skilled gig pros.
- Name: the working names are Jama ("jama karo") and Save91. A trademark and domain check is still needed ('cover').
- "Gross" means before work costs and is used for market size. "Take-home" means after work costs and is used for loan size.

### Slide 2. The customer
**TITLE:** Our customer is India's better-off city business owner: about 1.4 crore people

**PICTURE:** a funnel that narrows from "34 crore self-employed" to "1.4 crore city business owners earning over ₹30k a month". A small side bubble reads "+ a few lakh skilled gig pros".

**NUMBERS:**
- About 1.4 crore city non-farm business owners earn over ₹30k a month gross. This is our model, range 1.0–1.8 crore (SIZE-16).
- 34 crore self-employed, of whom 9.2 crore are unpaid family helpers and 13 crore are farmers (SIZE-03, SIZE-04, SIZE-07). Bachatt says "30 crore" (SIZE-20).
- A few lakh gig workers at most take home over ₹30k (GIG-24, our judgement).

**NOTES:**
- Bachatt's "30 crore" holds as a headline, but more than half of it is farmers and family helpers. The reachable core is city shopkeepers, traders and small service businesses. 6.0 crore people run non-farm work in towns and cities, and about 23% of them clear ₹30k gross (SIZE-08, SIZE-15).
- 1.4 crore is a model estimate: PLFS publishes only an average (₹23,012 a month gross in cities). No source splits any of this by city tier.
- Gig is one slice, not a second market. NITI's 1.4 crore gig workers is a 2022 projection, and riders take home only ₹18.8k, so only skilled pros and owner-drivers clear ₹30k (insight 5).
- What these owners want, in Bachatt's description of the same group: cash comes in daily, and they want to save a little each day and borrow for stock ('who').

### Slide 3. How they save today
**TITLE:** They already save daily with a cash agent, because saving is how they earn a loan

**PICTURE:** one loop. The owner hands cash to an agent at the counter, a co-op society holds it, and the society lends back to the owner. A small "not insured" tag hangs on the society.

**NUMBERS:**
- 2 lakh+ daily agents serve about 1 crore families, in Maharashtra alone, 2025–26 (SIZE-22; 'k-save').
- Sahara's co-ops had repaid 27 lakh of 1.35 crore depositors by Jul 2025 ('why').

**NOTES:**
- Insight 1: the habit already exists. The agent comes every day and takes cash, so saving takes no effort.
- Insight 2: the society that holds the money lends to its members, so the deposit is the ticket to a loan. M-Shwari's savers in Kenya said the same thing: they saved to get credit later (TB-33).
- What it costs them: low interest, a penalty for taking money out early, the agent's cut of up to 3%, and no deposit insurance ('why').
- These numbers are clues, not a count. No national survey counts daily-deposit savers (SIZE-22).
- Our opening: a regulated fund in their own name beats the agent on price and safety. Its limit is that it pulls from a bank account and cannot collect cash at the door.

### Slide 4. The gap
**TITLE:** Payment apps lend against sales on their own QR: PhonePe arranged ₹4,500 crore in FY25

**PICTURE:** a shop counter with three QR stands and a cash box. A lender looks through only one of the QR stands and taps a slice of its sales. The owner's savings jar sits behind the counter, out of the lender's view.

**NUMBERS:**
- PhonePe's shop loans were ₹4,507 crore in FY25, up from ₹11 crore in FY23. The instalment is cut from the day's sales ('a2-phonepe-paytm', 'k-incumbents').
- About 9 QR codes per merchant: 56.86 crore QR codes for 6.5 crore UPI merchants, FY25 (SIZE-19).
- ₹0 fee on shop payments under ₹2,000, even after 15 Oct 2026 ('qr').

**NOTES:**
- Insight 3: each lender sees one slice. Only 1 in 4 registered PhonePe shops use it in a month, and it can't see cash or rival QR codes ('qr').
- The incumbent's seat: it settles the money, so it takes the instalment before the shop is paid. Gig platforms do the same for their own workers; Swiggy arranged ₹102 crore of rider loans in the year to Dec 2023 (GIG-34).
- Payments earn almost nothing from small shops. The money is in the loan.
- The savings apps that do hold what people keep only refer loans for a one-off fee (slide 6).

### Slide 5. The product
**TITLE:** [Name] auto-saves ₹100 a day from the person's own bank, then lends on that record

**PICTURE:** three steps, left to right, with no QR company or platform anywhere in the picture:
1. Money from any QR, cash or payout lands in their bank.
2. ₹100 a day flows by UPI AutoPay into a jar with their name on it.
3. A loan comes back, and it grows with the streak.

**NUMBERS:**
- ₹100 a day × 25 days = ₹2,500 a month, which can be taken out instantly, up to ₹50k a day, from a liquid fund ('k-pipe').
- SEBI requires fund money to come from the investor's own bank account (GIG-32).
- 55–90% of UPI AutoPay attempts failed at major banks in Aug 2025 (TB-13).

**NOTES:**
- Why the person's own name matters: under SEBI's rule, no QR company or platform can own the account, and it follows the person across QR codes, banks and platforms. That is how we bypass PhonePe, Paytm, Swiggy and Uber without asking any of them.
- It works for a skilled gig pro exactly as it does for a shopkeeper, because platform pay lands in the worker's own bank (GIG-26). We go direct, not through a platform (the founder's decision).
- Insight 2 shapes the loan: it is unsecured and grows with how long and how steadily they have saved. It is not a loan against the balance, which almost nobody takes (TB-44).
- What we give up is deduction at source; we collect through a mandate on their bank account, like any other lender. Daily debits from thin balances fail often, so the product must cope with missed days (insight 4).
- Savings is the hook and doesn't need to make money. The fund pays us about ₹30–75 a year per saver ('money').

### Slide 6. Why it wins
**TITLE:** Bachatt proved owners sign up to save daily; PhonePe copied it, so the edge is lending

**PICTURE:** a short timeline:
- May 2025: Bachatt launches at ₹51 a day.
- Dec 2025: PhonePe copies it at ₹10 a day.
- Aug 2026: PhonePe passes 5 lakh investors.

It ends in one arrow: "copied in months; the money is in lending".

**NUMBERS:**
- About 1 lakh Bachatt daily savers. This is our estimate: 2M fund purchases in Feb 2026 ÷ about 20 debits each. Bachatt has raised $16M ('b-proves').
- PhonePe Daily SIP starts at ₹10 a day, launched Dec 2025, and had 5 lakh+ investors by Aug 2026 ('b-copied').
- On a ₹2 lakh loan, a referrer earns ₹2,000–5,000 once. PhonePe earns about ₹14,600 because it also collects the loan; this is a rough ratio ('b-copied', 'model').

**NOTES:**
- What Bachatt proves: owners will sign up for automatic daily saving into a regulated fund, and investors will fund it. What it hasn't shown is retention, loan volumes or defaults (insight 4; 'b-unproven').
- The saving product is not a moat. It uses the same funds and the same AutoPay, and PhonePe copied it in seven months. Whoever lends and collects earns most, so [Name] lends itself rather than referring.
- Why now: daily auto-saving into funds became a product only in 2025. RBI's 2025 co-lending rules let each lender keep as little as 10% of every loan (LS-01).
- Why us: the founder has run a lending business before. The founder's past lending data: first loans of ₹10–25k over 3 months, with 6–7% never repaid (GIG-39). See open question 2.
- The window may be short. PhonePe already has the QR, the daily SIP and loans against funds. The one piece we didn't find there is auto-saving a slice of each day's QR sales ('hold').

### Slide 7. How it makes money
**TITLE:** Loans are the business: lending ourselves earns ₹200–850 per saver; referring loses money

**PICTURE:** three bars from one baseline:
- "lend ourselves": a tall bar spanning ₹205 to ₹859;
- "refer the loan": just below zero;
- "lend at today's losses": a faded bar well below zero.

**NUMBERS:**
- +₹205 to +₹859 per shop owner won, over 5 years, if we lend ourselves. The low end assumes normal industry losses; the high end assumes savers repay better. Both are after a ₹499 cost to win each saver, with 1 in 5 savers borrowing (tables/lend_customer.csv: Shopkeepers, lend, industry steady state and savers safer, 0.2, evidence).
- −₹54 if we only refer loans (same file: Shopkeepers, referral, 0.2, evidence).
- −₹580 if losses stay at today's higher industry level (same file: Shopkeepers, lend, industry today, 0.2, evidence).

**NOTES:**
- Savings is the hook, at about ₹30–75 a year per saver from the fund house. Loans are the business.
- These are the founder's own model numbers for shop owners, quoted as they stand.
- If 35% borrow, as the founder expects: +₹738 at normal losses and +₹1,882 if savers repay better (same file, rows at 0.35).
- Losses decide everything. The same saver is worth −₹580 or +₹859 depending only on how loans are repaid.
- Lending ourselves needs an NBFC licence either way. Under RBI's 2025 co-lending rules, both partners must be regulated lenders, and each keeps at least 10% of every loan (LS-01).

### Slide 8. How big it can get
**TITLE:** At scale it is a ₹1,000 crore loan book; whether savers repay better decides its worth

**PICTURE:** one loan-book bucket that new savers fill each year. Beside it, a gauge with two marks: "typical future" and "if savers repay better".

**NUMBERS** (tables/lend_prize.csv, row won_a_year = 5,00,000; shop owners, 1 in 5 borrowing):
- Winning 5 lakh shop owners a year means about ₹1,750 crore lent a year, on an average loan book of ₹985 crore.
- Value created a year: ₹6 crore in a typical future, or ₹38 crore if savers repay better. Both are after the NBFC's own running cost of ₹5 crore a year.
- Capital needed: ₹98 crore if we co-lend and keep 10% of each loan, or ₹328 crore if we keep the whole book.

**NOTES:**
- 5 lakh a year is about 1% of the 5.36 crore micro enterprises on Udyam (share_of_udyam_micro column in the same file).
- At 1 lakh a year, a typical future does not cover the NBFC's running cost (−₹3 crore to +₹4 crore). At 10 lakh a year, value is ₹18–81 crore a year (same file).
- Read honestly: in a typical future this is a solid lending business, and it becomes a much bigger one only if the thesis holds. That is why the next slide is the bet.
- Capital is the real constraint on lending ourselves. Co-lending keeps it to about a tenth of the book.

### Slide 9. What must be true
**TITLE:** The bet: savers stay, 1 in 7 borrow, and losses stay low. A pilot tests all three first

**PICTURE:** three gates in a row, "Still saving?", "Borrows?" and "Repays?", each with its pass mark.

**NUMBERS:**
- At least 14% of savers borrow each year; the model assumes 20% (tables/lend_breakeven.csv, row takeup).
- Losses must stay at or below 7.6%; the model assumes 6%. The bar to beat: lenders expect 4.5–5% losses on Paytm-sourced shop loans (lend_breakeven.csv, row losses; 'a2-phonepe-paytm').
- 35.6% of SBI's ₹250 daily SIPs opened in FY26 had stopped by Apr 2026 (NG-033).

**NOTES:**
- Each break-even moves one number while the others stay at today's evidence. Winning a saver must also cost under ₹704 (today ₹499), and the loan rate must stay at or above 24.4% (lend_breakeven.csv). Across 10,000 simulated futures, the cost of winning a shop owner is earned back in 64% of them (tables/lmc_summary.csv).
- Why we believe savers repay better: bank loans to savings-linked self-help groups had 2.05% bad loans, against 8.72% across microfinance (EVD-03, NABARD, Mar 2024). That is a correlation, not proof. Nobody, including Bachatt, has published data showing that savers repay better.
- Two honest risks:
  - small daily savings leak (insight 4);
  - we give up deduction at source, which the founder's past lending data says helped repayment (GIG-39).
- The pilot reports three numbers: how many are still saving at months 6 and 12, the share who borrow, and losses against 7.6%.

---

## 4. Appendix list: which existing slides support which main slide

| Main slide | Supporting appendix slides (current ids) |
|---|---|
| 2. Customer | 'ax-sizing' (A1, the full funnel); 'g-count' (A23); 'g-gross' (A24); 'g-pros' (demoted from main); 'who' (A17); 'segments' (A19) |
| 3. How they save | 'size' (A2); 'why' (A3); 'what' (A4) |
| 4. The gap | 'qr' (A5); 'k-slice' (A6); 'doors' (A8); 'a2-phonepe-paytm' (A9); 'a3-others' (A10); 'vs' (A18) |
| 5. The product | 'disrupt' (A7); 'g-paid' (demoted from main); 'ax-gig' (A25) |
| 6. Why it wins | 'b-proves' and 'b-copied' (both demoted from main, full versions); 'a1-facts' (A11); 'b-unproven' (A12); 'compare' (A13); 'product' (A14); 'edge' (A20); 'risk' (A21); 'hold' (A22) |
| 7. Money | 'model' (A15); 'money' (A16) |
| 8. How big | **NEW:** one appendix slide showing lend_prize.csv's three scales (1, 5 and 10 lakh a year). Nothing in the current deck covers this. |
| 9. What must be true | 'k-true' (demoted from main: the full break-even chart, including cost to win and rate); 'b-unproven' (A12); 'hold' (A22); **NEW, if the founder agrees (open question 2):** a one-page summary of the founder's past lending data |
| Sources | 'a4-sources'; 'sources2'; 'sources3' |

The section dividers ('sec-bachatt', 'sec-gig') and the unused 'b-does' and 'b-earns' drop out, because Bachatt and gig are no longer chapters.

---

## 5. Cut list: what happened to the current 10 main slides

| Current slide | What happens | Why |
|---|---|---|
| 'cover' | Kept, retitled as a claim. The "story in ten slides" note is cut. | The cover should state the thesis, not list the chapters. |
| 'k-who' | Kept as slide 2. The 5-band funnel becomes 2 bands plus a gig bubble. 24.8 / 11.8 / 6.0 crore move to the notes and A1. | Five crore figures on one slide was the "too many numbers" problem. An investor needs the top and the bottom. |
| 'k-save' | Kept as slide 3, retitled around insight 2 ("saving is how they earn a loan"). | The old title gave a statistic. The new one gives the reason, which sets up lending on savings. |
| 'k-incumbents' | Kept as slide 4. The gig column (Swiggy ₹102 crore) moves to the notes. The title drops "nobody lends against savings". | That claim is shaky, because PhonePe lends against funds and Bachatt's partners use behavioural data. "Each lender sees one slice" is true and is the insight. |
| 'k-pipe' | Kept as slide 5. Gig workers are added here as one line. | This is where gig strengthens the argument: their pay also lands in their own bank. |
| 'k-money' | Kept as slide 7. The 35% case and the savings ₹30–75 move to the notes. | One point per slide: lending ourselves pays, and referring doesn't. |
| 'k-true' | Merged into slide 9. The three-dial chart with four break-evens is demoted to the appendix. The title keeps only "1 in 7". | The old title carried three numbers. Retention (insight 4) was missing from "what must be true", and it is the first risk. |
| 'b-proves' + 'b-copied' | Merged into one slide (6). Full versions go to the appendix. | Investors ask "who else, and why you?" once. Two Bachatt slides made the deck read like a study of Bachatt. |
| 'g-pros' | Demoted to the appendix. Its conclusion (only skilled pros clear ₹30k take-home) is the gig bubble on slide 2 and insight 5. | It is a supporting fact, not a step in the argument. |
| 'g-paid' | Demoted to the appendix. Its conclusion (gig pay lands in the worker's own bank) is one line on slide 5. The labour-code material is appendix only. | The labour code doesn't move the argument. |
| (none) | **Added:** slide 8, how big it can get. | An investor memo needs the size of the prize and the capital it takes. The model already has both (lend_prize.csv). |

---

## 6. Open questions for the founder

1. **What is the ask?**
   - How much are you raising, and for what pilot: how many savers, how many months, which city?
   - Does it include NBFC capital?

   No file has this, and an investor memo ends on it. Slide 9 currently ends on "a pilot tests all three", which leaves the ask out.
2. **Can we show your past lending results on a main slide as "why us"?** The results are first loans of ₹10–25k, 6–7% never repaid, and 30–50% borrowing again.
   - For: it is the strongest answer to "why this team".
   - Against: a 6–7% loss sits close to the 7.6% break-even, so the number cuts both ways.

   We need your call on whether it goes on slide 6 or stays in the appendix.
3. **When do we take the lending licence?** There are two options:
   - get our own NBFC before the pilot, which needs ₹98–328 crore of capital at the 5-lakh-a-year scale;
   - lend through an existing NBFC for the pilot, and convert once savers prove they repay.

   Co-lending also needs a licence (LS-01), so "co-lend" does not avoid this choice. The answer changes slides 7–9 and the ask.

---

## Number rules this draft follows
- Gross and take-home are never compared. The 1.4 crore is gross, with PLFS as its base. Gig figures are take-home and appear only as a side bubble and in insight 5.
- No figure from one population is divided by a figure from another. The gig count (NITI 2022 projection) sits beside the funnel and is not subtracted from it. "5 lakh a year" is compared only with the model file's own Udyam base.
- Labels:
  - "Our estimate" marks Bachatt's ≈1 lakh savers.
  - "Model" marks the 1.4 crore and all the tables/ figures.
  - "Judgement" marks "a few lakh" gig pros.
  - "Rough ratio" marks PhonePe's ₹14,600.
  - "Company claim" marks Bachatt's 3M users and Urban Company's ₹35.6k.
- Two foreign or correlational pieces of evidence are labelled as such where they appear: M-Shwari (TB-33) and the self-help-group loans (EVD-03).
- Titles round numbers: ₹4,507 crore becomes ₹4,500 crore, ₹205–859 becomes ₹200–850 (rounded down), ₹985 crore becomes ₹1,000 crore, and 14.2% becomes 1 in 7. The exact figures are in NUMBERS.

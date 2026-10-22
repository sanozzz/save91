# The savings pipe: storyline draft

Drafted 3 Oct 2026. This is the storyline only, not the slides.

**How to read this.** Read the 15 titles in order and you have the whole story. Each slide lists:
- one picture;
- the 2–4 numbers on it, each with its fact ID;
- short speaker notes.

Where the fact IDs live:
- `SIZE-xx` is in `research_sizing.csv`.
- `GIG-xx` is in `research_gig30k.csv`.
- A slide name in quotes (for example 'qr') is a slide in the current deck.
- `tables/...` is the founder's own model output. It is quoted as it stands and not recomputed.

**The thesis in one line.** PhonePe, Paytm and the gig platforms lend against the money people *receive*. We hold the money people *keep*, in their own name. Then we lend against that record, so neither the QR code nor the platform is needed.

**Rules followed throughout.**
- All earnings are labelled **gross** or **net**, and the two are never compared.
- "Our estimate" and "model" mark derived numbers. Their arithmetic is in the CSV notes.

---

## Part 1. The key story (7 slides)

### K1. Who
**Title:** Of India's 34 crore self-employed, about 1.4 crore are city business owners earning over ₹30k a month

**Picture:** a funnel with five bands:
- 34 crore self-employed;
- 24.8 crore who run their own work;
- 11.8 crore outside farming;
- 6.0 crore in towns and cities;
- about 1.4 crore earning over ₹30k.

A small side-bubble beside the third band reads "gig workers, ~1.4 crore (a different source)".

**Numbers:**
- 34 crore self-employed (SIZE-03)
- 11.8 crore non-farm owners (SIZE-07)
- 6.0 crore of them urban (SIZE-08)
- ~1.4 crore earning over ₹30k gross, range 1.0–1.8 crore (SIZE-16, model)

**Speaker notes:**
- Bachatt's "300 Mn merchants and self-employed" (SIZE-20) holds at the headline: PLFS 2025 gives about 34 crore self-employed. But 9.2 crore of them are unpaid family helpers and 13.0 crore are farmers (SIZE-04, SIZE-07). So 30 crore is not 30 crore shop owners.
- Two cross-checks land in the same range as the 11.8 crore non-farm owners. Both count businesses, not people:
  - 6.5 crore UPI merchants (SIZE-19);
  - 9.76 crore Udyam registrations, 4.33 crore of them informal micro units (SIZE-17).
- The last step is a model. PLFS publishes only an average: ₹23,012 a month gross for the urban self-employed (SIZE-10). We scaled the only published spread (2017-18: about 10% earned above ₹20k) to 2025 (SIZE-12 to SIZE-15).
- PLFS earnings are gross; it does not say whether business costs come out first. There is no tier-1/2/3 split anywhere.
- The gig workers sit mostly inside the "outside farming" band. Their count comes from a different estimate, so it is shown beside the funnel and not subtracted from it.

### K2. How they save today
**Title:** They save daily in cash with an agent: Maharashtra alone has 2 lakh+ agents serving about 1 crore families

**Picture:** a collection agent at a shop counter with a cash bag and a passbook, coins going in.

**Numbers:**
- 2 lakh+ agents, ~1 crore families in Maharashtra ('size', SIZE-22)
- agents paid up to 3% of what they collect ('why' notes)
- Sahara had repaid 27.3 lakh of its 1.35 crore depositors by Jul 2025 ('why')
- gig workers: 0 of 22 in formal savings, chit funds used most (GIG-45)

**Speaker notes:**
- Why the habit survives: the agent comes every day and takes cash. The society that holds the money also lends to its members, so saving doubles as the way to borrow later ('why').
- What it costs the saver: low interest, a penalty for taking money out early, and no deposit insurance for credit societies.
- No national count of daily-deposit savers exists, and nobody splits them by city tier. These numbers are clues, not a count (SIZE-22).
- Gig workers save in chit funds, cash or by sending money home (GIG-44, GIG-45). We found no data on them using daily agents (GIG-47).
- The opening: a regulated fund beats the agent on price and safety, but it cannot collect cash at the door. It has to pull from a bank account.

### K3. Who reaches them today
**Title:** Incumbents lend against money coming in: PhonePe arranged ₹4,507 cr of loans via the QR in FY25

**Picture:** two incoming pipes.
- A shop's QR stand, with a lender's tap taking a slice of each day's sales.
- A platform payout, with a lender's tap on it too.
- Beside the person, a savings jar that nobody is touching.

**Numbers:**
- PhonePe ₹4,507 cr of shop loans in FY25, with the instalment cut from daily settlement ('a2-phonepe-paytm')
- Swiggy ₹102 cr of rider loans in the 12 months to Dec 2023 (GIG-34)
- the founder's past lending data: the platform deducted repayments at source and charged ₹200 a loan for data (GIG-39)

**Speaker notes:**
- The incumbent's seat: it settles the money, so it sees the money and takes the instalment before the person gets paid ('vs', 'doors').
- Platforms have done the same for their own workers' vehicle finance, at Uber in 2016 and with Moove in 2022 (GIG-38). The founder's past lending data says this channel gave cheaper borrowers who repaid better (GIG-39).
- Payments themselves earn almost nothing from small shops: no fee on payments under ₹2,000 ('qr'). The money is in the loan.
- Nobody lends against what these people keep. That record does not exist yet.

### K4. The opening
**Title:** Each lender sees one slice: a shop holds ~9 QR codes, and Uber auto drivers are now paid directly by UPI

**Picture:** one person in the middle with six arrows coming in (QR 1, QR 2, QR 3, cash, a platform payout, direct UPI). An incumbent peers through a keyhole at just one of them.

**Numbers:**
- ~9 QR codes per merchant: 56.86 crore QR codes ÷ 6.5 crore merchants (SIZE-19)
- 1 in 4 registered PhonePe shops use it in a month ('qr')
- Uber Auto since Feb 2025: drivers pay ₹20–40 a day, and passengers pay the driver directly by cash or UPI (GIG-28)

**Speaker notes:**
- Each incumbent's view is partial and getting thinner:
  - shops use many QR codes;
  - ride-hailing is moving to subscriptions (Rapido 2024, Uber Auto Feb 2025, Ola cabs Jun 2025, GIG-29).
- Under a subscription, the money no longer passes through the platform, so the platform cannot deduct an instalment.
- Every inflow ends up in the person's own bank account (GIG-26). That is the one place no QR company or platform controls, and it is where our pipe sits.
- The bet is that a daily saving streak shows the money left after costs. That is closer to what a lender needs than one QR's gross sales. It is a thesis: nobody has published data showing it yet.

### K5. The pipe
**Title:** Our pipe: auto-save ₹100 a day from the person's own bank into their own fund, then lend against that record

**Picture:** three steps from left to right.
1. Several inflows (QR, cash deposit, payout) pour into one bank account.
2. A daily UPI AutoPay arrow carries money into a jar with the person's name on it.
3. A loan arrow comes back out to the person, sized by how long the jar's streak is.

**Numbers:**
- ₹100 a day × 25 days = ₹2,500 a month ('money')
- fund money must come from the investor's own bank account (GIG-32)
- withdraw instantly up to ₹50k a day from a liquid fund ('what')

**Speaker notes:**
- Why the person's own name: SEBI requires fund money to come from the investor's own account (GIG-32). So no QR company or platform can own the relationship, and the account follows the person across QR codes, banks and platforms.
- Why it bypasses them: it needs nobody's permission. It works for a shop owner and for a gig worker alike.
- What we give up: deduction at source. We collect through a mandate on the person's bank account, like any other lender ('vs').
- Risk at the debit: in Aug 2025, 55–90% of UPI AutoPay attempts failed at major banks, counted per attempt (research/tri_behaviour.csv TB-13). Small daily debits from thin balances will fail often.

### K6. How it makes money
**Title:** Savings earns ~₹50 a saver a year; lending our own book nets ₹205–₹859 per saver won, referring loses ₹54

**Picture:** three coin stacks side by side:
- savings: a few coins;
- refer the loan: just below the line;
- lend ourselves: a tall stack.

**Numbers:**
- ₹30–75 a year in fund commission at ₹100 a day ('money')
- ₹205–₹859 net per saver won if 1 in 5 borrow (tables/lend_customer.csv, rows "Shopkeepers, lend, industry steady state / savers safer, 0.2, evidence")
- −₹54 if we only refer (same file, row "Shopkeepers, referral, 0.2, evidence")
- ₹738–₹1,882 if 35% borrow (same file, rows at 0.35)

**Speaker notes:**
- Savings is the hook and does not need to pay for itself (the founder's decision). Loans are the business.
- These are the founder's own model numbers, after a ₹499 cost to win each saver.
- The two lending cases differ only in losses. "Industry steady state" assumes losses at today's industry level. "Savers safer" assumes savers default less, which is the thesis.
- The founder believes more than 1 in 5 savers will borrow; the 35% rows show that case.
- At today's industry losses, every lending case loses ₹539–₹843 per saver (the "industry today" rows for shop owners and drivers). Losses decide everything (K7).
- Lending ourselves means an NBFC licence either way: RBI's 2025 co-lending rules are between regulated lenders, and each keeps at least 10% of every loan (research/lend_self.csv LS-01).

### K7. What must be true
**Title:** It works only if 1 in 7 savers borrow, losses stay under 7.6%, and winning a saver costs under ₹704

**Picture:** three dials (savers who borrow, losses, cost to win a saver). Each has a green zone and a needle showing where the model sits today.

**Numbers:**
- at least 14.2% of savers borrow (tables/lend_breakeven.csv, row takeup)
- losses at most 7.6% (row losses)
- cost to win a saver at most ₹704 (row cost_to_win)
- the cost of winning a saver is earned back in 64% of simulated futures for shop owners and 50% for drivers (tables/lmc_summary.csv)

**Speaker notes:**
- These are the founder's model break-evens for shop owners, at today's industry loss level and 1 in 5 borrowing, moving one number at a time. The interest rate must also stay at or above 24.4%.
- Benchmarks for losses:
  - Paytm-sourced shop loans: 4.5–5% expected loss ('a2-phonepe-paytm');
  - the founder's past first loans: 6–7% never repaid (GIG-39 source file);
  - unsecured business loans under ₹10 lakh: up to 10.2% go 90+ days late (research/nongig.csv NG-015).
- Nobody has published data showing that savers repay better, including Bachatt ('hold').
- The pilot must measure three things: do savers keep saving, do they borrow, and do they repay better than the market.

---

## Part 2. The Bachatt story (4 slides; compressed from the current deck)

### B1. What Bachatt does and proves
**Title:** Bachatt already runs the shop-owner version: ₹51 a day into debt funds, about 1 lakh daily savers

**Picture:** a shop owner's phone with a ₹51 daily debit flowing into a fund, and one arrow out to "loans from 7 lenders".

**Numbers:**
- ₹51 a day or ₹1,001 a week ('a1-facts')
- $16M raised, Accel-led Series A in Mar 2026 ('a1-facts')
- 2M fund purchases in Feb 2026 ÷ ~20 debits each ≈ 1 lakh daily savers (our estimate, 'risk' notes)
- loans up to ₹5 lakh from 7 lending partners ('a1-facts')

**Speaker notes:**
- Trusave Fintech, founded Nov 2024, app live May 2025 ('a1-facts').
- What it proves: shop owners will sign up for an automatic daily saving, sold partly by paid agents who copy the daily cash agent ('product').
- Its own numbers conflict: 3M users in the Series A release, but "10 lakh+" users and ₹50+ cr invested on the homepage (GIG-41).
- Its current copy names shop owners, jewellers, dealers and the salaried. It does not mention gig workers (GIG-41).

### B2. How Bachatt earns
**Title:** Bachatt earns ₹2,000–5,000 once per ₹2 lakh loan it refers; PhonePe earns ~₹14,600 by also collecting it

**Picture:** two bars for the same ₹2 lakh loan, short for Bachatt and long for PhonePe, plus a thin sliver labelled "a year of savings, ₹30–75".

**Numbers:**
- ₹30–75 a year in fund commission at ₹100 a day ('model')
- ₹2,000–5,000 referral fee, 1–2.5% of the loan ('model')
- PhonePe's ₹328 cr earned ÷ ₹4,507 cr lent ≈ 7.3%, which is ≈ ₹14,600 on ₹2 lakh ('model', rough ratio)

**Speaker notes:**
- Bachatt is a fund distributor and a loan service provider. The fund house and the lender pay it; the saver pays nothing ('model').
- The PhonePe figure is a rough ratio: revenue is earned over the loan's life. But it shows who gets paid more, the one who collects.
- This is why the founder wants to lend, not refer (K6).

### B3. What PhonePe has copied
**Title:** PhonePe copied the product in seven months: Daily SIP from ₹10, with 5 lakh+ investors by Aug 2026

**Picture:** a timeline:
- May 2025: Bachatt launches at ₹51;
- Dec 2025: PhonePe launches at ₹10;
- Aug 2026: PhonePe passes 5 lakh+ investors.

**Numbers:**
- ₹10 vs ₹51 lowest daily saving ('product')
- 5 lakh+ PhonePe Daily SIP investors, 77% from tier-2/3 towns ('risk')
- 5 crore+ shops on PhonePe's QR ('hold')

**Speaker notes:**
- The product is not a moat: same funds, same AutoPay. Paytm Money's direct plans leave the saver 0.2–0.5% a year better off ('product', 'compare').
- PhonePe also lends against mutual funds, with DSP Finance since Sep 2025 ('hold').
- The one piece we did not find at PhonePe is auto-saving a slice of today's QR sales. That is absence of evidence, and a small step for them ('hold').

### B4. What Bachatt has not proven
**Title:** Bachatt claims 3M users but has published no retention, loan-volume or default figure

**Picture:** three empty boxes with question marks: "still saving?", "borrowed?", "repaid?".

**Numbers:**
- 3M users (company claim, 'a1-facts')
- 35.6% of SBI's ₹250 daily Jan Nivesh SIPs opened in FY26 had stopped by 1 Apr 2026 (research/nongig.csv NG-033)
- 4.5–5% expected loss on Paytm shop loans, the bar savers must beat ('a2-phonepe-paytm')

**Speaker notes:**
- These three unknowns are exactly what our pilot must measure (K7).
- Small daily SIPs leak fast: about 8% of all ₹250 SIPs closed in May 2026 alone (research/tri_behaviour.csv TB-04).
- "India's 3rd-largest SIP initiator" has no stated basis ('a1-facts').
- If Bachatt ever publishes retention or default numbers, they will confirm or kill this thesis. Watch for them.

---

## Part 3. Gig workers earning more than ₹30k a month (4 slides)

### G1. How many
**Title:** Gig work is about 1.4 crore people, but only a few lakh at most take home over ₹30k a month

**Picture:** three nested circles:
- a big one: 1.4 crore gig workers;
- a smaller one: at most 33 lakh could gross over ₹30k;
- a dot: take home over ₹30k (skilled pros, owner-drivers).

**Numbers:**
- 1.43 crore in 2025-26 (NITI's 2022 projection, GIG-02) and 1.2 crore in FY25 (an industry estimate, GIG-04)
- 11.5 lakh registered on e-Shram by Aug 2026 (GIG-05)
- at most ~33 lakh gross over ₹30k: 1.43 crore × 23% full-time (GIG-25, upper bound)
- a few lakh at most take home over ₹30k (GIG-24, judgement)

**Speaker notes:**
- Both headline numbers are estimates, not counts. e-Shram is the only government count, and it excludes income-tax payers, so it misses the higher earners (GIG-05).
- Platform counts cannot be added up because riders work on several apps (GIG-09 to GIG-14):
  - Swiggy: 6.48 lakh riders a month;
  - Rapido: 20 lakh bike-taxi partners (claimed);
  - Urban Company: 46,625 active pros.
- 40% of gig workers earn under ₹15k a month; that source does not say gross or net (GIG-22).
- No source counts gig workers above ₹30k (GIG-23). The two bounds are ours, with the arithmetic in the CSV.

### G2. Gross is not take-home
**Title:** ₹30k gig incomes are mostly gross: a full-time rider grosses ₹27.8k but takes home ₹18.8k after costs

**Picture:** three bars, each a gross bar with the costs shaded grey:
- full-time rider: ₹27.8k → ₹18.8k;
- diary worker: ₹35.1k → ₹16.6k;
- Urban Company pro: ₹55.2k → ₹28.3k.

**Numbers:**
- rider: ₹27,814 gross, ₹18,761 take-home (GIG-19)
- diary workers: ₹35,075 gross, ₹16,604 take-home (GIG-20)
- Urban Company: ₹55,244 gross, ₹28,322 take-home (GIG-15)
- 43% of cab drivers take home under ₹500 a day (GIG-21)

**Speaker notes:**
- Costs eat a third to a half of gross: fuel, commission, travel and products.
- Never compare a gig take-home figure with PLFS's gross self-employed earnings (K1).
- Loans must be sized on take-home: a ₹18.8k earner carries a much smaller instalment than ₹27.8k suggests.
- The founder's model already drops riders as borrowers. Their loans are ₹2–10k, and lending to them loses money in almost every case (tables/lend_customer.csv, "Delivery riders" rows).

### G3. Who really clears ₹30k
**Title:** The real ₹30k earners are skilled pros: Urban Company's busier two-thirds take home ₹35,600 on average

**Picture:** a ladder of monthly take-home pay with a line drawn at ₹30k:
- motorbike rider ₹18.2k;
- EV rider ₹24.4k;
- Urban Company average ₹28.3k;
- Urban Company pros doing over 30 jobs a month ₹35.6k;
- Urban Company top 20% ₹42.4k.

**Numbers:**
- ₹35,637 average take-home for the 65% of Urban Company pros doing over 30 jobs a month (GIG-16)
- ₹42,418 for the top 20% (GIG-17)
- ~9,300 to ~30,300 Urban Company pros take home over ₹30k (GIG-18, our estimate)
- EV rider ₹24,370 take-home, still under ₹30k (GIG-19)

**Speaker notes:**
- Urban Company is the only platform that publishes how its partners' earnings spread (GIG-23).
- Owners who drive their own cab or goods vehicle may also clear ₹30k take-home, but no source gives their figure (GIG-23). Porter, for example, claims 3 lakh+ drivers (GIG-13).
- In the founder's model, drivers and home-service workers earn back the cost of winning them in 50% of simulated futures (tables/lmc_summary.csv). They net ₹550 per saver won if savers are safer (tables/lend_customer.csv, row "Drivers and home-service workers, lend, savers safer, 0.2").
- These pros are already offered loans through Urban Company's lending partners, plus a pension scheme (GIG-35).

### G4. How they are paid, and who is already there
**Title:** Gig pay already lands in the worker's own bank, and Swiggy started selling ₹100 savings in Jun 2026

**Picture:** a weekly calendar with payout arrows into the worker's bank account, some arriving instantly. Next to it is a Swiggy rider app with a "save ₹100" button.

**Numbers:**
- weekly payout as standard, cash-out any day from ₹200 at Uber (GIG-27) and within an hour at Swiggy since Sep 2026 (GIG-30)
- Swiggy and Zerodha Fund House: riders can invest from ₹100 in-app, launched Jun 2026 (GIG-33)
- platforms must pay 1–2% of turnover into a government welfare fund, but the rate is not yet set (GIG-06, GIG-08)

**Speaker notes:**
- For gig workers, the platform's weekly payout plays the part the QR settlement plays for a shop. But it lands in the worker's own account (GIG-26), so our pipe needs no platform's permission.
- We found no current, public case of a platform deducting an outside lender's instalment from payouts (GIG-40). The NeoGrowth–Zomato deduction is for restaurants, not riders (GIG-37).
- Platforms already cover the obvious needs:
  - free insurance from Zomato and Blinkit, about ₹100 cr a year (GIG-36);
  - loans from Swiggy and Urban Company (GIG-34, GIG-35);
  - now savings from Swiggy.
- The new labour code and state laws give insurance, not a pipe. The money goes to a government board, not into the worker's own account (GIG-06, GIG-42, GIG-43). Karnataka and Telangana are live; Rajasthan's and Bihar's laws have stalled.

---

## What goes to the appendix

1. **Sizing detail:** the full PLFS funnel with every multiplication (SIZE-01 to SIZE-08, SIZE-21). Also:
   - the earnings model and its assumptions (SIZE-10 to SIZE-16);
   - where the self-employed work (SIZE-09);
   - the Udyam and UPI cross-checks (SIZE-17 to SIZE-19);
   - why NITI and PLFS totals must not be mixed (SIZE-23).
2. **Janta deposits:** the current deck's slides 'size', 'why' and 'what'.
3. **The QR strategy in detail:** 'qr', 'doors', 'a2-phonepe-paytm', 'a3-others'.
4. **Bachatt in detail:** 'a1-facts', 'compare', 'product', 'risk', 'who', 'vs', 'segments', 'edge', 'model'.
5. **Gig detail:**
   - platform worker counts, with definitions and why they cannot be added (GIG-09 to GIG-14);
   - payout timing by platform (GIG-26 to GIG-31);
   - what platforms already offer in loans, insurance and savings (GIG-33 to GIG-41);
   - the labour code and state laws (GIG-05 to GIG-08, GIG-42, GIG-43);
   - savings habits (GIG-44 to GIG-47).
6. **The founder's lending model:** tables/lend_customer.csv, lend_breakeven.csv, lmc_summary.csv and segment_value.csv. Also a one-slide summary of the founder's past lending data (first loans ₹10–25k for 3 months, 25% approved, 6–7% first-loan loss, 30–50% took a second loan).
7. **Sources:** the current 'a4-sources' and 'sources2', plus every URL in the two new CSVs (accessed 3 Oct 2026 unless noted).

---

## Decisions for the founder

1. **Which "₹30k" defines the customer: gross or take-home?**
   - Gross is the PLFS measure: about 1.4 crore city business owners (K1).
   - Take-home is what decides loan size: for gig workers it is a few lakh at most (G1).
   - The two give markets about ten times apart. The deck should pick one and use it everywhere.
2. **Which group to lead with?**
   - **Shop owners:** the biggest group and the best odds in the model (64%), but PhonePe, Paytm and Bachatt are all already there.
   - **Skilled gig pros and owner-drivers:** a far smaller group, but no savings player targets them yet. Urban Company already lends to its pros, and Swiggy now sells savings to its riders.
   - Or both from day one.
3. **For gig workers, partner with a platform or go direct?**
   - **Partner:** repayments are deducted at source (the founder's past data says this gave better repayment). The cost is a per-loan fee, a platform that can switch you off or copy you, and coverage of only one platform.
   - **Direct, through the worker's own bank:** no permission needed, but no deduction either, so collection is weaker.
4. **How to lend, and when to take the licence?**
   - Co-lending under RBI's 2025 rules needs us to be a regulated lender that keeps at least 10% of each loan, so "co-lend" also means getting an NBFC licence.
   - The alternative is to start as a loan service provider with a capped 5% loss guarantee, and convert once the pilot proves that savers repay.
5. **Should the deck open on "34 crore" at all?** It matches Bachatt's headline and shows ambition, but more than half of it is farmers and family helpers. Opening on the 1.4 crore core is the more credible choice.

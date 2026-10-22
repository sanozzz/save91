# Draft A: customer-first storyline (v11)

Drafted 3 Oct 2026. This is a storyline, not slides. It uses the customer-first lens: the customer insights come first and the business idea follows from them.

**The story in one breath.** Better-off city business owners already save every day, but in cash with an agent, because the agent's society is the one that will lend to them. Formal lenders see no record of them. The lenders who do reach them (PhonePe, Paytm, Swiggy, Uber) each see one slice of their money. All the slices meet only in the person's own bank account. So [Name] sits there: it auto-saves ₹100 a day into a fund in their name and lends on that record. Bachatt shows owners will start saving this way. PhonePe shows the saving is easy to copy. So the money has to come from the loan, and the pilot must prove that savers borrow and repay.

**How to read the source IDs.**
- `SIZE-xx` and `GIG-xx` are rows in `janta_pipe/research_sizing.csv` and `research_gig30k.csv`.
- `NG-`, `TB-`, `XB-`, `XL-` and `LS-` IDs are rows in `research/nongig.csv`, `tri_behaviour.csv`, `xs_bachatt.csv`, `xs_lending.csv` and `lend_self.csv`.
- A name in quotes, such as 'why', is a slide in the current deck.
- `tables/...` is the founder's lending model, quoted as it stands.
- `tables/inputs_founder_*.csv` is the founder's past lending data. The file is cited by pattern so that its full name never appears on a slide.

---

## 1. Customer insights (ranked)

The top three carry the story. Each one becomes a main slide (S3, S4, S5).

### Insight 1. Many already save every day, just with the wrong partner
**The insight:** the daily saving habit already exists. An agent collects cash at the counter every day for a local credit co-op society, which pays low interest, charges a penalty for early withdrawal, and can fail.

**Evidence:**
- 2 lakh+ daily collection agents serve about 1 crore families in Maharashtra alone (2025–26; SIZE-22, 'size'). These are clues, not a count: there is no national or city-tier count of daily-deposit savers.
- Sahara's four co-op societies had repaid only 27 lakh of their 1.35 crore depositors by Jul 2025 ('why').

**So what for [Name]:** we don't have to create a habit. We only have to give an existing one a better home: a regulated fund in the person's own name, which they can withdraw from any day.

### Insight 2. Each lender sees one slice of their money; the slices meet only in their own bank account
**The insight:** their money arrives in pieces: several QR codes, cash, and a platform payout. PhonePe and Paytm lend against the one QR they settle, and Swiggy and Uber against the payout they make. The only place where every slice lands is the person's own bank account, and no QR company or platform controls it.

**Evidence:**
- About 9 QR codes per merchant: 56.86 crore QR codes for about 6.5 crore merchants (FY25; SIZE-19).
- Small shops' UPI money goes straight into the owner's own personal bank account (P2PM merchants, DFS FAQ, Sep 2026; NG-030). Gig pay lands in the worker's own bank account, because a bank account is an entry requirement for platform work (IDinsight 2024; GIG-26).

**So what for [Name]:** sit at the bank account. The pipe then needs no QR company's or platform's permission, and it works for a shop owner and a gig pro alike.

### Insight 3. Saving is how they earn a loan, and formal lenders see no record of them
**The insight:** for these people, saving and borrowing are one relationship. The society that keeps their money is the one that lends it back to them. Banks and lending apps, meanwhile, have nothing to judge them on, and mostly say no.

**Evidence:**
- About 4 in 10 Indian small enterprises, including sole proprietors, have formal credit (TransUnion CIBIL–SIDBI MSME Pulse, Jul 2026; NG-042).
- In the founder's past lending data, 1 in 4 applicants were approved, and most were turned down on credit scores that were not good enough (2019–22, all applicants; `tables/inputs_founder_*.csv`, approval_rate row).

**So what for [Name]:** the loan is what they really want, and a daily saving streak is a record they can build themselves. Savings is the hook; the loan is the business.

### Insight 4. Our customer is the better-off quarter, not the average shopkeeper
**The insight:** the people worth serving earn well above the average for city business owners. That gives them spare cash to save ₹100 a day and the income to repay a real loan.

**Evidence:**
- The average urban self-employed earner makes ₹23,012 a month, gross (PLFS 2025; SIZE-10).
- About 1.4 crore city business owners earn over ₹30k a month gross. This is a model estimate with a range of 1.0–1.8 crore (2025; SIZE-16).

**So what for [Name]:** aim at the top quarter, which is the same band Bachatt names (₹30–70k), and not at the mass of small shops.

### Insight 5. Their money comes in unevenly, so a fixed daily debit will miss days
**The insight:** on some days the balance is too thin for the debit. Small daily savings therefore leak, whatever app collects them.

**Evidence:**
- 55–90% of UPI AutoPay attempts failed at major banks in Aug 2025, mostly for lack of balance (all AutoPay executions, counted per attempt; TB-13).
- 35.6% of SBI's ₹250 daily Jan Nivesh SIPs opened in FY26 had stopped by 1 Apr 2026 (NG-033).

**So what for [Name]:** treat missed days as normal, and make "do they keep saving?" the pilot's first test.

### Insight 6. In gig work, headline pay is not take-home pay
**The insight:** work costs eat a third to a half of gig gross pay. Only skilled pros (home-service pros and some owner-drivers) take home more than ₹30k a month. Delivery riders don't.

**Evidence:**
- A full-time delivery rider grosses ₹27.8k a month but takes home ₹18.8k (one platform, 2024; GIG-19).
- Urban Company's busier 65% of pros take home ₹35.6k (Apr–Dec 2025, company figure; GIG-16).

**So what for [Name]:** gig is a small, skilled slice. Size its loans on take-home pay, and leave riders out as borrowers.

---

## 2. Storyline: 9 main slides

The titles in order, read as one story:

1. [Name] turns a ₹100-a-day saving habit into a record people can borrow on
2. Our core customer: about 1.4 crore better-off city business owners, plus skilled gig pros
3. Many already save every day, but in cash, with an agent, at low interest and real risk
4. Saving at the co-op earns them a loan; formal lenders see no record and mostly say no
5. Each lender sees one slice of their money; the slices meet only in their own bank
6. [Name] auto-saves ₹100 a day from their bank into a fund in their name, then lends on it
7. Bachatt shows owners will start saving daily by app; PhonePe shows it is easy to copy
8. So the money is in the loan, and only if we lend it ourselves rather than refer it
9. It pays back if 1 in 7 savers borrow and repay well; our pilot must prove they do

The arc: who the customer is (S2), three customer insights (S3–S5), the idea that follows from them (S6), the proof and the warning (S7), the money (S8), and what must be true (S9). Bachatt and gig workers are not separate chapters. Bachatt appears once, as proof and warning (S7). Gig pros appear where they share the story: in the customer (S2), in "their pay lands in their own bank" (S5), and in "go direct" (S6).

All titles are ≤ 89 characters with "[Name]" in place, and each carries at most one number.

---

### S1. Cover
**TITLE:** [Name] turns a ₹100-a-day saving habit into a record people can borrow on

**PICTURE:** a phone showing a streak of daily ₹100 coins dropping into a jar with the owner's name on it. A loan arrow grows out of the side of the jar. Strapline: "Save every day. Borrow on your record."

**NUMBERS:**
- ₹100 a day ≈ ₹2,500 a month at 25 saving days ('k-pipe')

**NOTES:**
- What it is: a savings pipe for India's better-off city business owners and skilled gig pros. It runs from the person's own bank account, so it needs neither the QR code nor the platform.
- Savings is the hook; loans are the business.
- "[Name]" is a placeholder for Jama ("jama karo") or Save91. A trademark search and a domain check are still needed ('cover').
- Two words used throughout: "gross" means pay before work costs, and "take-home" means pay after them. Market size uses gross; loan size uses take-home.

### S2. Who (customer)
**TITLE:** Our core customer: about 1.4 crore better-off city business owners, plus skilled gig pros

**PICTURE:** two nested circles.
- The big circle: "about 34 crore self-employed (Bachatt says 30 crore)".
- The small, highlighted core: "≈1.4 crore run a business in a town or city and earn over ₹30k a month before costs".
- Beside it, a separate small dot that is not added in: "skilled gig pros: home-service pros, owner-drivers".

**NUMBERS:**
- About 34 crore self-employed (PLFS 2025; SIZE-03). Bachatt's headline is 30 crore (SIZE-20).
- ≈1.4 crore earn over ₹30k a month gross. This is a model estimate, range 1.0–1.8 crore (SIZE-16).

**NOTES:**
- Bachatt's "30 crore" holds at the headline. But over half are unpaid family helpers (9.2 crore) or farmers (13 crore), and 6 crore run non-farm work in towns and cities (SIZE-04, SIZE-07, SIZE-08). The full funnel is in A1.
- They are the better-off quarter: the urban average is ₹23k a month gross (SIZE-10). The 1.4 crore is our model, scaled from the only published spread of earnings, from 2017-18 (SIZE-15). No source splits any of this by city tier.
- Gig comes from a different source base, so it is never added to the 1.4 crore (SIZE-23). At most about 33 lakh gig workers could gross over ₹30k (GIG-25, a ceiling). Only a few lakh take that much home (GIG-24, a judgement). Detail is in A23 and A24.
- Riders are out as borrowers. In the founder's model, lending to them loses money in almost every case (`tables/lend_customer.csv`, Delivery riders rows).

### S3. Insight 1: how they save today
**TITLE:** Many already save every day, but in cash, with an agent, at low interest and real risk

**PICTURE:** one loop at a shop counter:
1. the owner hands cash to an agent;
2. the agent takes it to a co-op society (gloss: a local savings-and-loan society);
3. the society lends back to its members.

Three small red tags sit on the loop: "low interest", "penalty to take it out early", "societies can fail".

**NUMBERS:**
- 2 lakh+ daily agents in Maharashtra alone, serving about 1 crore families (SIZE-22, 'size')
- Only 27 lakh of Sahara's 1.35 crore co-op depositors had been repaid by Jul 2025 ('why')

**NOTES:**
- Why the habit survives: the agent comes every day and takes cash, so saving takes no effort ('why').
- These numbers are clues, not a count. No national or city-tier count of daily-deposit savers exists (SIZE-22).
- Gig workers save differently. In a 2022 Bengaluru diary study, none of 22 platform workers used a formal savings product, and chit funds were the most common (GIG-45).
- Safety wording: say "regulated, in your own name, out any day", not "insured". A debt fund is not deposit-insured either, and some daily schemes (at co-op banks and PSU banks) are.
- The honest limit: the app pulls from a bank account and cannot collect cash at the door ('why'). See open question 1.

### S4. Insight 3: what they need, and why formal lenders fail them
**TITLE:** Saving at the co-op earns them a loan; formal lenders see no record and mostly say no

**PICTURE:** two doors side by side.
- Left door, open: "Co-op: save with us → borrow from us".
- Right door, nearly shut: "Bank or lending app: show me your credit record".

The owner stands between them holding an empty folder marked "record".

**NUMBERS:**
- About 4 in 10 small enterprises, including proprietors, have formal credit (TransUnion CIBIL–SIDBI, Jul 2026; NG-042)
- In the founder's past lending data, 1 in 4 applicants were approved (2019–22; `tables/inputs_founder_*.csv`, approval_rate row)

**NOTES:**
- Saving and borrowing are one relationship for them: the society that keeps their money lends it back ('why'). In Kenya, M-Shwari users said the main pull of saving was getting credit later (TB-33, CGAP 2015).
- The two numbers describe different groups (enterprises vs the founder's past applicants). Show them side by side and never combine them. "Mostly" is our reading of both.
- 55% of the businesses taking a first loan in FY25 were new to credit (NG-042). Lenders are reaching them, but with little to judge them on.
- So what: a daily saving streak is a record they can build themselves, and it is what [Name] lends on.
- Nobody has shown that savers repay better. The founder's own past data calls it "a hunch, no numbers" (`inputs_founder_*`, saver_signal row). The pilot must show it (S9).

### S5. Insight 2: how money reaches them
**TITLE:** Each lender sees one slice of their money; the slices meet only in their own bank

**PICTURE:** the person's bank account in the centre, with arrows flowing in from QR code 1, QR code 2, QR code 3, cash banked later, and a platform payout.
- PhonePe/Paytm hold a magnifier over QR 1 only, with a tap that cuts the loan instalment there.
- Swiggy/Uber look only at the payout.
- The bank account is labelled "the one place it all meets; no QR company or platform controls it".

**NUMBERS:**
- About 9 QR codes per shop (FY25; SIZE-19)
- ₹4,507 cr of shop loans arranged by PhonePe in FY25, with the instalment cut from the day's sales (XL-10, 'k-incumbents')

**NOTES:**
- PhonePe and Paytm lend against money coming in. They settle the sales, so they see them and take the instalment before the shop is paid ('k-incumbents').
- But each sees only the sales on its own QR, and only 1 in 4 registered PhonePe shops use it in a month (NG-038).
- Small shops' UPI money lands in their own personal account (NG-030). Gig pay lands in the worker's own bank (GIG-26). Since Feb 2025, Uber Auto riders pay the driver directly (GIG-28).
- Payments earn almost nothing from small shops: there is no UPI fee under ₹2,000, even after 15 Oct 2026 ('qr'). The money is in the loan.

### S6. The idea
**TITLE:** [Name] auto-saves ₹100 a day from their bank into a fund in their name, then lends on it

**PICTURE:** three steps, left to right:
1. Money lands in their bank.
2. ₹100 a day moves by UPI AutoPay into a jar with their name on it, which they can empty any day.
3. A loan comes back, and it grows with the length of the saving streak.

A small line under step 2 reads: "missed days are normal; the streak allows for them".

**NUMBERS:**
- ₹100 a day ≈ ₹2,500 a month ('k-pipe')
- 55–90% of UPI AutoPay attempts failed at major banks in Aug 2025, mostly for lack of balance (TB-13)

**NOTES:**
- The fund is a debt mutual fund in the person's own name. SEBI requires the money to come from their own bank account, so no QR company or platform can own the relationship (GIG-32). Liquid funds pay out instantly, up to ₹50k a day ('what').
- What we give up is deduction at source. We collect loans by a mandate on their bank account, like any other lender.
- Because their money comes in unevenly, missed debits are a design rule, not a failure. 20 million AutoPay mandates are revoked a month for low balances (TB-14).
- Gig pros are reached directly through their own bank, not through a platform deal. There is no employer or payroll route (founder's decisions).

### S7. Proof and warning
**TITLE:** Bachatt shows owners will start saving daily by app; PhonePe shows it is easy to copy

**PICTURE:** a short timeline:
- May 2025: Bachatt launches at ₹51 a day.
- Dec 2025: PhonePe launches Daily SIP from ₹10 a day.
- Aug 2026: PhonePe passes 5 lakh+ investors.

Under the timeline, one arrow: "the saving can be copied → the loan is what we must win".

**NUMBERS:**
- ≈1 lakh Bachatt daily savers (our estimate: 2M fund purchases in Feb 2026 ÷ ~20 each; XB-03, 'b-proves')
- 7 months from Bachatt's launch to PhonePe's copy ('b-copied')
- 5 lakh+ PhonePe Daily SIP investors by Aug 2026, counting everyone onboarded since launch ('b-copied')

**NOTES:**
- Bachatt (live May 2025, $16M raised) runs the shop-owner version of this pipe. Owners save ₹51 a day into debt funds, and it refers loans of up to ₹5 lakh to 7 lenders ('a1-facts').
- It proves owners will sign up. It has published nothing on whether they keep saving, borrow or repay (A12).
- The two counts are not like-for-like (daily savers vs everyone onboarded). Keep them on the timeline and never draw them as bars.
- PhonePe sells the same funds through the same AutoPay. It says shop owners are taking it up, and it already lends against mutual funds (Sep 2025) ('b-copied', 'hold').

### S8. The money
**TITLE:** So the money is in the loan, and only if we lend it ourselves rather than refer it

**PICTURE:** three bars showing what one shop owner is worth to us over 5 years, after ₹499 to win them, if 1 in 5 borrow:
- "refer the loan": just below zero;
- "lend ourselves, normal losses": above zero;
- "lend ourselves, if savers repay better": the tallest.

A hair-thin sliver at the side is labelled "savings fees".

**NUMBERS:** all from `tables/lend_customer.csv`, Shopkeepers rows at 0.2 with the evidence cost to win:
- −₹54 if we refer;
- +₹205 if we lend at normal losses;
- +₹859 if we lend and savers repay better.

**NOTES:**
- Savings needn't pay: the fund pays us about ₹30–75 a year per saver at ₹100 a day ('money').
- Whoever lends earns most. On a ₹2 lakh loan a referrer earns ₹2,000–5,000 once, while PhonePe earns about ₹14,600 because it also collects. That PhonePe figure is a rough ratio ('model').
- At today's high industry losses, lending ourselves loses ₹580 per saver (same file, "industry today" row). Losses decide everything (S9).
- If 35% borrow, as the founder expects: +₹738 at normal losses, and +₹1,882 if savers repay better (same file, 0.35 rows).
- Lending ourselves needs an NBFC licence either way: co-lending is between regulated lenders, and each keeps at least 10% of every loan (LS-01).

### S9. What must be true
**TITLE:** It pays back if 1 in 7 savers borrow and repay well; our pilot must prove they do

**PICTURE:** three dials. Each has a green "pays back" zone and a needle at today's assumption:
- savers who borrow in a year: green from 1 in 7, needle at 1 in 5;
- losses on loans: green up to 7.6%, needle at 6%;
- cost to win a saver: green up to ₹704, needle at ₹499.

Under the dials are three tick-boxes: "Do they keep saving? Do they borrow? Do they repay better?"

**NUMBERS:** all from `tables/lend_breakeven.csv`:
- at least 1 in 7 savers borrow (14.2%; takeup row);
- losses at most 7.6% (losses row);
- cost to win a saver at most ₹704 (cost_to_win row).

**NOTES:**
- These come from the founder's model for shop owners, moving one number at a time. The interest rate must also stay at or above 24.4% (rate row).
- Across 10,000 simulated futures, the cost of winning a shop owner is paid back in 64% of them (`tables/lmc_summary.csv`).
- The bars for losses: lenders expect 4.5–5% on Paytm-sourced shop loans (XB-07). The founder's past first loans lost 6–7%.
- Savers drift away: 35.6% of SBI's ₹250 daily SIPs opened in FY26 had stopped by Apr 2026 (NG-033).
- Bachatt has published none of these three answers. If it publishes them first, they will confirm or kill the thesis.

---

## 3. Appendix list: which existing slides support which main slide

| Main slide | Existing appendix slides |
|---|---|
| S2 Who | ax-sizing (A1 funnel), who (A17), segments (A19), g-count (A23), g-gross (A24), plus g-pros (demoted) |
| S3 How they save | size (A2), why (A3), what (A4), a3-others (A10, the daily-agent panel) |
| S4 Save to borrow / no record | why (A3), plus **one new slide** on who gets formal credit: NG-042 and the founder's past lending data (1 in 4 approved, 6–7% first-loan loss, 30–50% took a second loan) |
| S5 One slice | qr (A5), k-slice (A6), doors (A8), a2-phonepe-paytm (A9), vs (A18), ax-gig (A25), plus k-incumbents and g-paid (demoted) |
| S6 The idea | disrupt (A7), what (A4), compare (A13), product (A14) |
| S7 Bachatt / PhonePe | a1-facts (A11), b-unproven (A12), edge (A20), risk (A21), hold (A22), compare (A13) |
| S8 Money | model (A15), money (A16), plus **one new slide**: the full `lend_customer.csv` grid (all segments, refer vs lend, 1 in 5 and 35% borrowing) |
| S9 Must be true | b-unproven (A12), hold (A22) |
| Sources | a4-sources, sources2, sources3 |

---

## 4. Cut list: what happened to the current 10 main slides

| Current slide | What happens | Why |
|---|---|---|
| cover | Kept and retitled. | The "story in ten slides" note is out of date. The gross/take-home gloss stays on the cover; the sizing detail goes to S2. |
| k-who | Kept as S2. The funnel is cut from 5 bands to 2 numbers. | The middle steps (24.8, 11.8, 6.0 crore) are method, not story, and stay in A1. |
| k-save | Kept as S3, retitled. | The current title says "no deposit insurance", which is too broad: co-op banks' and PSU banks' daily schemes are insured. It also invites the question "is your fund insured?", which it isn't. The risk is now carried by "societies can fail". |
| k-incumbents | Merged into S5 and demoted. | Its title led with a statistic (₹4,507 cr). S5 now leads with the insight (one slice), and the ₹4,507 cr is evidence. Its "no record" column becomes S4. |
| k-pipe | Kept as S6. | "Out instantly up to ₹50k a day" moves to the notes; "missed days are normal" goes into the picture. |
| k-money | Kept as S8 and moved after Bachatt/PhonePe. | It now reads as the consequence of "the saving is easy to copy". The −₹580 row and the 35% case go to the notes. **Editor's call:** put −₹580 back as a fourth bar if hiding it reads as soft. |
| k-true | Kept as S9 and merged with Bachatt's three "not shown" questions. | The loss benchmarks go to the notes, and the three dials stay. |
| b-proves + b-copied | Merged into S7. | They are one point: Bachatt proves sign-up, and PhonePe shows it is easy to copy. Accel/$16M and the 77% tier-2/3 figure go to the notes. The ₹14,600 vs ₹2,000–5,000 comparison moves to S8's notes, where it argues for lending ourselves. |
| g-pros | Demoted to the appendix, next to g-gross. | Gig is one slice of the customer. A full slide reads as a separate chapter, which is the scattering the founder objected to. It survives as "plus skilled gig pros" on S2 and in S2's notes. |
| g-paid | Demoted and merged into ax-gig (A25). | Its one load-bearing fact (gig pay lands in the worker's own bank) becomes an arrow in S5. The labour-code material is context and moves to the appendix. |

**New on the main line:** S4 (saving earns a loan; formal lenders see no record). It is built from 'why' (A3), NG-042 and the founder's past lending data. NG-042 is marked confirmed in the research CSV but has not been on a deck slide, so it has not been through the deck's own check.

---

## 5. Open questions for the founder

1. **Cash:** S3 says many save in cash, but [Name] pulls from a bank account. Do we serve only owners whose money already reaches the bank (UPI and banked takings), or should the story promise a way to put cash in? The answer decides whether S3 → S6 reads as a simple switch or as a gap we haven't closed.
2. **Your past lending data on a main slide:** can S4 show "1 in 4 applicants approved"? Who were those applicants: mostly platform workers, or shop owners too? The number has to carry its group on the slide.
3. **Gig on the main line:** skilled gig pros appear only inside S2, S5 and S6, with no slide of their own. Is that enough? If not, the one gig slide would be: "Only skilled gig pros take home ₹30k, and their pay already lands in their own bank."

# Save91 / SaveMore: critical review from four angles

**Date:** 21 October 2026
**Reviewed:** the online v4 plan of record: the models, the four investor documents and the research folder.

Four fresh reviewers, none of whom built the work, each took one angle:

| Angle | Reviewer |
|---|---|
| Investment | A seed lead's IC memo |
| Analyst | Numbers and model code, every claim re-run |
| Story | A VC reading the decks cold |
| Regulation and operations | Compliance and ops lead |

Their full reports sit beside this file. This document merges them:
- issues raised by several angles come first;
- then what each angle adds on its own;
- then the corrected numbers, the decisions that are yours, and the fixes that need no decision.

Figures marked † were checked again while merging.

---

## 1. The verdict, in five lines

1. **The arithmetic is right.** Every headline reproduces exactly from the code (analyst): 4.10× and month 19 online, 3.83× and month 23 doorstep, profit from month 40, $2.46M needed, Monte Carlo median 3.79×.
2. **The core design is lawful.** No customer money is held, the units sit in the saver's name, and loans are referred with no credit risk. No RBI licence or new capital is needed (regulation).
3. **An investor would not lead on these materials.** They would lead a restructured seed under five conditions (section 6). The plan's base case sits 3–10× above the folder's own evidence on the inputs that carry it.
4. **The story is a spreadsheet story, and it contradicts the model.** The decks sell "credit as the reward for saving". The model earns 41% of a saver's value from loan offers to sign-ups who never save. The sharpest insight the team has ("savings is the hook, credit is the business") appears in no investor document.
5. **The common root is the loan funnel.** The plan's value sits in a funnel the folder has no evidence for, and the seed is exactly the experiment that would measure it. The honest pitch is "the seed buys the measurement", not "the plan says 4.1×".

---

## 2. Where the angles agree

### C1. The loan funnel carries the case, on judgement (all four angles)

| Input | Plan | Nearest evidence in the folder |
|---|---|---|
| Apply for a loan, a year | 35% | 1–2% (payments-app merchants, XF-16); ~3.6% (Paytm, XL-04); 8–17.5% of registered users *ever* borrowed (LEND-04, XL-42) |
| KYC'd users reached per saver | 2.5, non-savers reachable while savers stay | None. It also needs a separate consent (C2) |
| Personal + business loan | ₹1 lakh | **The founders' own 2019–22 book: ₹10–25k (XF-24)**; digital lenders ₹18,802 (XF-11); bureau ₹58,522 (XL-29) |
| Payout | 2% rising to 3% | Rate cards 1–2.5% (XF-01); the folder's own cost research uses 1.5% and calls 3% optimistic; the rise has no source |
| Take-up +5% and approval +10% a year | Judgement | "No data" |

- **One evidence value is enough to break 3×.** Each of these does it on its own:

  | Single input at its evidence value | LTV/CAC |
  |---|---|
  | 3.6% apply† | 1.73× |
  | ₹25k loans† | 2.56× |
  | 24% retention | 2.63× |
  | Offers to savers only† | 2.43× |
  | ₹2 per daily debit | 2.08× |

- **Combinations break the company.** Apply at 3.6%† alone moves company profit from month 40 to month 73 ($5.3M).

  | Case | Reviewer | LTV/CAC | Company |
  |---|---|---|---|
  | The three 18 Oct anchors together† | merge check | 1.07× | not profitable within 8 years |
  | "Moderate evidence", every input inside the plan's own ranges | investment | 0.93× | never profitable, $9.9M or more |

- **Three judgements carry most of year-5 profit.** The payout ramp and the two growth factors carry ₹16.4 cr of the ₹18.2 cr year-5 EBITDA. Without them, profit moves to month 52 (analyst).
- **Tying retention to loan demand barely matters.** Re-pairing the 1,000 futures so they move together lowers the bottom tenth only from 2.58× to 2.46×†. The exposure is in the levels, not the link.

### C2. The product the decks sell is not the product the model prices (all four angles)

- **What the decks say:**
  - cover: "credit as the reward for saving";
  - v4 p2: "save 6 months, see your loan offer"†.
- **What the model does:** loan offers from a user's first month to every KYC'd sign-up, 2.5 per saver, of whom 1.5 never save. They get the same approvals as savers. About ₹750 of the ₹1,845 LTV comes from them.
- **Modelled as the decks describe it** (offers from a saver's month 7, to savers only): 2.31× (payback month 34); company profit in month 57, $4.1M (analyst).
- **Consent makes 2.5 a ceiling anyway** (regulation, REG-085). Lender offers need a separate, optional consent that saving cannot depend on. Real reach is KYC'd users × the opt-in rate × how long consent lasts.

### C3. The daily debit: unconfirmed plumbing with a possible cost (analyst, regulation, investment)

- **Through the BSE StAR MF exchange platform, distributors pay nothing per order†** (XB-01). The fund house pays ₹6–30 an order (TC-12). A fund house may not accept a daily ₹80 + ₹20 split; ₹100 a day per scheme is the usual minimum† (REG-043).
- **Through our own payment provider,** list prices are ₹5 per Autopay execution† (TC-02, TC-06), and the money would pass through an app-contracted account, which the folder's own rules bar (REG-066, REG-081).
- **Cost of a ₹2 debit, 20 a month** (analyst):
  - one saver: 2.08×;
  - company: profit in month 56, $5.1M.
- **Weekly debits at ₹2** keep 3.58×.
- **Action:** get written confirmation from BSE and three fund houses in month 1, before release 1 is built. If daily does not work, redesign: weekly debits, or one hybrid scheme.

### C4. The labels claim more than the evidence (all four angles)

| Label | What it actually is |
|---|---|
| "Today's evidence" (about 20 times in v4 and the business case) | The base case, whose biggest drivers the LTV deck itself tags as founder's judgement |
| "98% chance of profit" (v4 p11) | Odds from the founders' own ranges. Those ranges centre on the plan and exclude the evidence: apply never below 10%, loans never below ₹50k, reach peaks at its maximum. The "bad-year" correlation is wired to inputs with no effect online, so the claim is false in effect. |
| "All 68 inputs checked" (v4 A10) | The audit file holds the earlier values (₹58,522, 3.6%, ₹300)†. The three biggest drivers of the current plan were never audited. |
| "We charge the saver nothing" | A regular plan costs the saver about 0.5–1% a year more than a direct plan |
| "Withdraw any day" | Equity funds commonly charge about 1% for redeeming within a year (to verify per scheme) |

**Re-centred on folder evidence** (the analyst moved eight inputs; the plan's values stay as the high end):
- median 1.18×;
- 1% of futures reach 3×.

### C5. There is no wedge against Bachatt (investment, story)

- **Bachatt already runs the full v4 product:**
  - daily SIP from ₹51–100;
  - loans up to ₹5 lakh through nine partners;
  - cards;
  - an AI assistant.
- **It has $16M and about 3M users.**
- **PhonePe sells ₹10-a-day saving built with Jar.**
- **No competition page.** "Nobody serves both" (v4 p2) is contradicted by the team's own memo, and no investor document has a competition page.
- **The claimed edge earns nothing for a referrer.** "Credit priced from the savings record" benefits the lender, which keeps the gain. The model shows it only as an assumed +10% a year in approvals.

### C6. Scale and valuation (investment, story)

- **Loans are 76% of company revenue over 5 years; the fund fee is 14%.** This is a loan lead-generation business found through saving.
- **A fund would price it like a referral business.** At 5–10× revenue, the profitable path is worth about $24–48M, not the 20× shown. "0.45× money saved" prices one year's fund fee at about 67×.
- **The only $1B plan is refuted on its own page.** It needs more sign-ups than the segment holds.
- **Action:** cut the unicorn pages. They cost more credibility than they add.

---

## 3. What each angle adds on its own

### Investment
- **Cross-checks the plan fails:**
  - ₹450 buys ₹83,867 of loans per saver, 0.54% of money lent, against Moneyview's 1.9–2.9% sourcing cost (LEND-03);
  - loan fees per user reached (₹295 a year) are close to Paytm's entire financial-services revenue per user (₹354), at half Paytm's fee rate.
- **The savings-only floor:** 1.47× at ₹450, 1.10× at ₹600.
- **Cost to win:**
  - unmeasured;
  - Groww's is ₹796–1,374, mostly organic, and rose 73% in a year as paid marketing grew (TB-18);
  - the seed asks for a 15× rise in savers a month within 12 months.
- **Team:**
  - no consumer-growth operator in a business decided by the cost to win;
  - the CEO also carries growth, partners, fund-raising, compliance, finance and the doorstep pilot;
  - no founder bios;
  - plan volatility: after the 18 Oct review called 18% apply too high, v4 raised it to 35%.
- **Repayment cap:** households earning up to ₹3 lakh a year can owe at most 50% of income in repayments (REG-077). A ₹1 lakh, 18-month loan takes 29–38% of a ₹23,000 monthly income.

### Analyst
- **The headline saver never exists.** It joins in month 1 at the post-seed ₹450 CAC.

  | Cohort | LTV/CAC |
  |---|---|
  | First real cohort (month 4, at ₹600) | 3.16× |
  | Month 19 at ₹450 | 4.79× |

  The later cohorts are higher only through the growth judgements.
- **The cost basis is inconsistent.** The company model spends ₹495 per saver (contingency included), and non-savers cost nothing to serve.

  | Correction | LTV/CAC |
  |---|---|
  | At ₹495 | 3.73× |
  | Plus serving non-savers | 3.34× |

- **Cost to win and reach are linked by arithmetic but drawn independently.** If ₹450 comes from better conversion, reach falls to 1.875 (3.41×). The "₹300 → 6.2×" lever is really 4.07×.
- **Durable and vehicle loans** sit outside the 35% funnel but are multiplied by 2.5 reach; gold converts at 100%. Correcting both gives 3.95×.
- **Bases not stated:**
  - if payouts are quoted including GST: 3.43×;
  - a 5% first-loss cover on the ramped payout would lock about ₹53 cr by month 60;
  - TDS sits as a refund receivable.
- **An upside the model omits:** if stopped SIPs stay invested, the trail continues: 4.5–5.0×. The LTV deck says both things on different pages.
- **Six cross-document inconsistencies,** for example the 24% retention case at 2.6× vs 2.7×, and a wrong title on the business case p6. There are also stale docstrings in `online_mc.py` and `online_plan.py`.

### Story
- **What a partner remembers** after 3 minutes: 4.1×, month 40, $0.5M, and "loans". After 30 minutes, four doubts:
  - the apply rate;
  - the 40% from non-savers;
  - the $1B plan that refutes itself;
  - no team, market or competition page.
- **Over 35 cases before the ask** (v4 p1, p7–p11). This breaks the one-case rule; the business case cover leads with "$1B in 3 of 5 combinations".
- **Missing pages:**
  - team (Seed p6 is a salary table with first names);
  - market;
  - why now;
  - evidence (the customer problem is sourced to practitioners, not customers);
  - the ask (v4 sends the reader to another document).
- **The seed milestones are profit months, not month-18 targets.** The LTV deck's p16 pass lines belong on v4 p12 and Seed p8.
- **Pages that should not travel:**
  - v4 A10–A13 ("8 wrong or unsourced… rebuilt 21 Oct", "118 of 120 checks");
  - the old plan's "₹1,108 crore over six rounds".
- **Internal shorthand:** "agreed" 20 times, research IDs in the LTV body, "Latin hypercube", "PERT".
- **Layout faults:** Seed p8's cards overflow the footer; the business case p6 has overlapping labels.
- **A 13-page storyline:**

  | # | Page |
  |---|---|
  | 1 | Cover |
  | 2 | The saver |
  | 3 | The insight |
  | 4 | The product |
  | 5 | The money flow |
  | 6 | Why now |
  | 7 | Competition |
  | 8 | One-saver waterfall |
  | 9 | What has to be true (the pass lines) |
  | 10 | One plan |
  | 11 | Go-to-market |
  | 12 | Team |
  | 13 | The ask |

  The LTV deck becomes the diligence pack; the short business case is retired.

### Regulation and operations
- **The insurance revenue share.** The model gives us 75% of a broker's commission. An unlicensed company likely cannot be paid that way (Insurance Act s.40; to verify). Fix: our own corporate-agent registration (about ₹35,500, 3–6 months, REG-059), or a fixed fee not linked to volume.
- **LSP from month 7.** v4 A5 says "become an LSP with the next round". In fact the app is a lending service provider from its first sourced loan, with every duty that comes with it:
  - the lender reports the app to RBI;
  - a Key Facts Statement for every loan;
  - fee clawback in the cooling-off period;
  - neutral display of matching offers;
  - a grievance officer.
- **The first-loss cover listed as a lever is unfunded:** about ₹40 cr on year-5 volumes.
- **Certification:** NISM V-A and an EUIN for everyone who explains funds (agents, support), not only the founders; POSP for anyone who discusses insurance.
- **Lines that cannot be earned:**
  - the Choti SIP incentive (₹7 a saver): the daily SIP disqualifies the saver;
  - digital gold (₹12): contradicts the folder's own "not at launch" row. Use a gold fund instead.
- **FD, NPS and bill payments** each need a partner agreement that is not scheduled.
- **Doorstep:** "no cash, ever" written into the agent contract. Drop the "cash cover" line and the cash legal opinion. Pay incentives on savers still saving at month 3.
- **Compliance:** no named owner in the seed. About ₹20–40 lakh more is needed in the seed, which the contingency can absorb.
- **Launch timing:** realistic launch is month 5–6, not month 4.
- **Licence table:** the full table (16 items, time, cost, whether budgeted) is in `review_regops.md` §7.

---

## 4. What the plan looks like after the corrections

Each row comes from the reviewer named; the input sets differ, so read the rows as a ladder, not one model.

| Case | Reviewer | Online LTV/CAC | Company profit | Money needed |
|---|---|---|---|---|
| Published plan | all | 4.10× | month 40 | $2.5M |
| Mechanical fixes only: ₹4 tech incl. non-savers, weekly debits at ₹2, CAC at ₹495 | analyst | 3.00× | month 47 | $3.25M |
| … and the product as described (offers from month 7, savers only) | analyst | 1.63× | month 66 | $5.4M |
| Half-way evidence: 20% apply, ₹60k, reach 2.0, 34% saving, ₹550 | investment | 1.66× | month 66 | $5.2M |
| The three 18 Oct anchors: 3.6%, ₹58,522, 24%† | merge | 1.07× | not within 8 years | $7.0M+ |
| Moderate evidence, inside the plan's own ranges | investment | 0.93× | never | $9.9M+ |

The mechanical fixes alone take the plan to exactly 3×. Everything below that row depends on the loan funnel, which only the seed can measure.

---

## 5. Decisions that are yours

1. **The base case.** Keep 35% apply / 2.5 reach / ₹1 lakh as the base, relabelled "the plan"? Or re-base on evidence and show 35% as "what it takes"? The investor makes re-basing condition 1.
2. **The product and credit promise.** Either:
   - (a) loan offers to every KYC'd user from day 1, and drop "credit as the reward for saving"; or
   - (b) credit after saving, and accept a base of about 2.3×.

   Either way, lender offers become a separate opt-in.
3. **The debit design.** Daily (only if BSE and the fund houses confirm), weekly, or one hybrid scheme.
4. **The insurance route.** Our own corporate-agent registration now, or a fixed referral fee through the broker.
5. **The unicorn and valuation pages.** Cut them, or move them to the appendix with plain caveats. Both reviewers who looked say cut.
6. **The seed structure.** Accept two tranches gated on measured cost to win and early retention? Are both founders full-time, and is a growth lead hired by month 6?
7. **The documents.** Make v4 the one main deck on the 13-page storyline, the LTV deck the diligence pack, and retire the short business case?

## 6. The investor's conditions to lead

1. The case is re-based on evidence. Base inputs:
   - apply 10–20%;
   - loans of ₹50–60k;
   - reach measured;
   - ₹600 to win.

   The unicorn pages and the futures-as-odds line go.
2. A signed letter of intent from a lender before close, with fee, loan size and approval criteria for this customer.
3. A one-page wedge against Bachatt: the segment, the channel and the feature Bachatt lacks.
4. Both founders full-time with 4-year vesting, and a consumer-growth lead hired by month 6.
5. Two tranches of $250k. The second is released once the product and a lender are live, with three months of cost-to-win and month-3 retention data that meet the milestones.

## 7. What the seed has to prove

The pass lines for 3×, one input at a time, alongside the investor's milestones:

| Measure | Pass line | Investor's milestone |
|---|---|---|
| KYC'd users who apply for a loan, a year | at least 21% | at least 20%, on 20,000 or more KYC'd users shown offers for 6 months or more |
| First approval | — | at least 25% |
| Median loan | at least ₹47,000 | at least ₹50,000 |
| Payout | at least 0.94% | at least 1.75%, in writing, from at least two lenders by month 9 |
| Cost to win a saver | at most ₹615 | at most ₹600, three months running, at 2,000 or more savers a month |
| Still saving | at least 27% at month 12 | at least 55% at month 6 and 30% at month 12 |
| Users reached per saver | at least 1.5 | measured, with consent on record |

Also report monthly:
- debit success rate and cost per debit;
- the consent opt-in rate;
- the doorstep arm against online (keep it only if it beats online month-12 retention by 10 points or more, at ₹500 or less).

## 8. Fixes that need no decision

These correct errors or labels. They do not change the plan.
- **One number for each case:**
  - the 24% retention case (2.6× vs 2.7×; use the savings-app curve, 2.63×);
  - label the doorstep values (₹1,717 revenue / ₹1,550 after serving / ₹1,145 net);
  - profit month written one way;
  - seed length 18 vs 24 months;
  - loans per 100 savers, 73 vs 37 on v4 p6.
- **The business case p6 title:** the cases it names give months 48 and 42, not 52–59.
- **Labels:**
  - "today's evidence" becomes "the plan";
  - "98% chance of profit" goes;
  - "77% of futures" becomes "77% of futures inside our own ranges";
  - the "bad-year correlation" claim goes until it is wired.
- **The input audit:** re-run on the 21 Oct values, or retitle v4 A10.
- **"We charge the saver nothing"** becomes "the fund house pays us out of its published fee; a regular plan costs about X% a year more than direct".
- **Revenue lines:**
  - remove the Choti SIP line;
  - replace digital gold with a gold fund;
  - correct the A5 wording on LSP and first-loss cover.
- **Pass lines:** add them to v4 p12 and Seed p8.
- **Layout:** fix Seed p8 and the business case p6.
- **Code:** refresh the stale docstrings in `online_mc.py` and `online_plan.py`.

---

**Files beside this one:**
- `review_invest.md`: IC memo, verdict and milestones;
- `review_analyst.md`: 15 findings, every recomputation, and the scripts in `analyst_scripts/`;
- `review_story.md`: page-by-page findings and the 13-page storyline;
- `review_regops.md`: findings by rulebook and the licence table.

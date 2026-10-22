# Investment review (18 Oct): what still applies to the online v4 plan

**Date:** 21 October 2026
**Reviewed against:** the plan of record (`model/online_plan.py`, `model/ltv_book.py`, the v4 and LTV/CAC decks).

The review in `INVESTMENT_REVIEW.md` was written on 18 October against the offline v3 base. That base had:
- 5,000 agents collecting cash at ₹350 a day;
- an on-book lender keeping 30% of personal loans;
- two valuation lenses.

The v4 plan replaced most of that machinery on 21 October. Each of the review's 29 findings and 10 questions is sorted below into one of three groups:
- still relevant;
- fixed in v4;
- no longer applies.

The v4 numbers come from the models, re-run today.

## The one thing that matters most

Each of the review's evidence anchors, applied alone, leaves the online saver at 1.7× or better. **All three together break the plan.**

| Case (online saver, 5 years, everything else at the plan) | LTV/CAC | Pays back |
|---|---|---|
| Plan: 35% apply a year, ₹1 lakh loans, 38% still saving at a year | 4.10× | month 19 |
| Apply 3.6% a year (the review's payments-app anchor) | 1.73× | month 41 |
| Loan size ₹58,522 (bureau average, which the row says skews high) | 3.24× | month 23 |
| Loan size ₹25,600 (a digital lender's segment average) | 2.56× | month 29 |
| 24% still saving at a year (savings apps) | 2.72× | month 25 |
| Offers to savers only (reach 1 instead of 2.5) | 2.43× | month 31 |
| Apply 10% and loans of ₹58,522 | 1.96× | month 37 |
| **All three anchors: 3.6% apply, ₹58,522, 24% saving** | **1.07×** | **month 58** |
| The same, with offers to savers only | 0.94× | month 63 |

The company, on the profitable path (20,000 online savers won a month from month 30):

| Case | Profit from month | Money needed | Year-5 EBITDA |
|---|---|---|---|
| Plan | 40 | $2.5M | ₹18.2 cr |
| Apply 3.6% a year | 73 | $5.3M | −₹7.2 cr |
| Loans of ₹58,522 | 47 | $2.9M | ₹8.7 cr |
| All three anchors | not within 8 years | $7.0M or more | −₹10.6 cr |

The plan works only if the loan funnel performs well above every number in the folder's own evidence. The review said this about an 18% apply rate. v4 uses 35%.

**Tying retention to loan demand costs little.** The review's point F27 is that the credit-hungry customer stays because they got the loan. I re-paired the 1,000 futures so that apply rate and retention move together, at a rank correlation of 0.5 and of 0.7:
- the bottom tenth fell from 2.58× to 2.46×;
- the share under 2× rose from 2.4% to 3.6%.

Inside our ranges, the link barely matters. What matters is whether the ranges themselves are too high.

## A. Still relevant: act on these

| Review item | Then (v3) | Now (v4) | What still bites | Suggested action |
|---|---|---|---|---|
| **F06** apply rate | 18% a year | **35% a year**, to 2.5 KYC'd users per saver | Worse than before. The review's anchor is 3.6% a year; the nearest observed rate in the LTV deck is 1–2%. At 3.6%: 1.73×, and the company is profitable in month 73. Pass line for 3×: 21%. | Founder's decision: keep 35% as the base, or present it as "what it takes" with a lower base. Get a lender or DSA platform's own rate for KYC'd users who apply in a year. |
| **F04** loan size | ₹2.5 lakh | ₹1 lakh blended (₹50k personal, ₹1.5 lakh business) | Still 2–4× the personal-loan evidence: ₹25,600 (XL-42), ₹58,522 (XL-29), digital ₹18,800–70,000 (XF-11). Merchant loans of ₹50,000–5 lakh support the business half only. At ₹58,522: 3.24×; at ₹25,600: 2.56×. | Evidence the personal-versus-business split. Ask a lender for the average ticket it would approve in this segment. |
| **F08, F27, F28** retention and the small save | 55% still saving at a year, ₹350 a day | 38% online (SBI daily SIP, extended from 6 to 12 months), 55% doorstep, ₹100 a day | 38% is still an extrapolation, above the 24% observed for savings apps (2.72× at 24%). Retention and loan demand are drawn independently, but linking them costs little (above). | In the seed, measure month-12 still-saving split by whether the saver got the loan they asked for. Pass line for 3×: 27%. |
| **New since the review** loan reach | not in v3 | 2.5 KYC'd users per saver; non-savers stay reachable as long as savers do | About ₹750 of the ₹1,845 LTV comes from users who never save. Offers to savers only give 2.43×. With the review's anchors: 0.94×. Nothing in the folder observes it. | Treat it as a fourth funnel number to measure. Pass line for 3×: 1.5 users per saver. |
| **F01, F02, F03** valuation yardsticks | Unicorn = 20× ARR and 0.45× AUM, almost one test, with NII inside the ARR | The same two yardsticks on the unicorn pages. No NII now; the two lenses no longer coincide (at today's evidence: 20× ARR ₹11,050 cr, 0.45× AUM ₹5,829 cr) | F02 still stands: 0.45× is Stable Money's price on cumulative money invested, applied to fund money the company does not own. A 20× multiple on loan-referral fees is also a judgement. | Drop 0.45× AUM, or label it a stretch. Lead valuation talk with revenue and EBITDA. |
| **F24** fund trail rate | 0.35% on the whole book | 0.75% equity, 0.35% debt, blended 0.67% | Rates are from guides and a listed distributor, not from a scheme we have chosen. Trail needs regular plans, which cost the saver about 0.5–1% a year more than direct plans. | Write the scheme, the plan type and the trail received. Prepare the answer to "why regular plans for low-income savers?". |
| **F29** OD++ (the wallet the customer thinks they have) | not in the model | Named in the v4 deck; loans against savings are 10% of applications, not counted | No product designed: who lends, against what balance. | My suggestion, not from the review: a loan-against-mutual-funds credit line from a partner lender. The money stays in the saver's funds, which keeps it clear of REG-081. It is a retention hook, not a revenue line. |
| **F26** Bachatt's online volume | ₹499 online cost, street-first | Online-first; ₹450 to win (₹600 in the seed); ₹300 used only as the good end | Still unknown whether Bachatt's "1 to 1.5 lakh online" is a month or a stock. Our profitable path signs about 1 lakh online sign-ups a month (20,000 savers × 5). | Ask Saket. If it is a stock, our volume is far beyond theirs. |
| **F14** pool and cap | 7 crore pool, 20% cap | Unchanged | Binds only the unicorn track: online sign-ups stop at the cap in month 75. The profitable path does not reach it. | Low priority. Show the pool as a range (6.5–7.8 crore) where the unicorn track is shown. |
| **F07** sign-ups per agent | 100 a month, the whole fleet | 100 a month, doorstep only (1 in 10 savers) | The doorstep cost of ₹404 rests on it. The only field interview is 6–10 a month. | Low weight now. Measure it in the 18-month doorstep test. |
| **F18** thin cost lines | 1 support person, flat ₹1.5 lakh tech | ₹5 support + ₹1 tech per saver per month; compliance ₹25 lakh a year | Support now scales. Check compliance for three regimes at once: fund distributor, insurance through a partner, and lending service provider. | Low–medium. Price the compliance team once the partners are named. |

Diligence questions that still apply:
- **Q1:** a lender's written ticket, fee and approval rate for this saver.
- **Q4:** month-12 still-saving, split by whether the saver got the loan.
- **Q5:** which round, at what price, without the AUM lens.
- **Q6:** what happens after the pool fills (unicorn track only).
- **Q10:** the amount savers are happy to keep saving, and the OD++.

## B. Fixed in v4

| Review item | What v4 does |
|---|---|
| F10 PAT was interest on raised cash | Interest on cash is not counted; profit is EBITDA, monthly |
| F15 ₹350 a day | ₹100 a day (a daily-savings app's minimum), ~20 debit days |
| F05 ₹25 lakh home loan | ₹8 lakh, 2% of applications, 0.5% payout |
| F09 cash route into the fund | UPI Autopay for every saver; the app never holds money |
| F22 debt-only book | 80% equity SIP / 20% debt; debt-only is a side case |
| F23 30% UPI cap | 100% UPI; the doorstep agent signs savers rather than collecting cash |
| F25 no customer problem | v4 page 2, "The saver's problem, not ours": three problems with remedies |
| F26 street-first, ₹499 online | Online-first, 90/10; Saket's ₹300 used only as the good end |
| F16 Paytm ₹407 comparison | Not used |
| F19 hidden cash tail | Money needed published as a band ($2.0M / $2.6M / $3.4M, P10 / P50 / P90); draws saved |

## C. No longer applies (v3 machinery that v4 removed)

| Review item | Why it no longer applies |
|---|---|
| F11 NBFC leverage, F12 keeping the best 30%, F17 on-book loss | v4 has no own-book lending: we earn a referral payout and the lender carries the credit risk |
| F03 (the NII part) | No net interest income in v4 |
| F13 round sizing, Round E | v4 has a $0.5M seed and a money-needed figure; no modelled cap table |
| F20 "Five years" column, F21 medians of parts | Labels in v3 tables and the v3 deck; the v4 tables do not have them |
| Q2, Q7, Q8, Q9 | Cash title, servicing a loan book, repricing rounds, agent incentive cuts: v3 only |

## What the seed has to prove now

The review's three pilot numbers, updated for v4, with the 3× pass line for each (one input at a time):

1. **The loan funnel:** the share of KYC'd users who apply in a year (at least 21%), with a lender's approval rate and payout (at least 0.94%).
2. **Retention:** the share still saving at month 12 (at least 27%), split by whether the saver got the loan.
3. **Loan size:** what the lender actually approves (at least ₹47,000).

Also measured: the cost to win a saver (at most ₹615) and the reach to non-savers (at least 1.5 users per saver).

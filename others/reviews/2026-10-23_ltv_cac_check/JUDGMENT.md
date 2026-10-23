# LTV/CAC check, 23 Oct 2026: the judgment

Two independent checks of the online saver's 5-year LTV/CAC (plan: 7.7×, paid back in month 12):
- `recalc.md`: a rebuild from the raw inputs, repo only.
- `evidence.md` / `evidence.csv`: 65 sourced Indian figures for the ten inputs that move it most.

The main cases were re-run through the model before this note was written.

## The answer

1. **The sums are right.** Rebuilt without the model's code, every line matches to within 0.1%. The bugs found are display-only (0.00×). Two cost slips are worth −0.15× together: contingency not applied to serving, and no clawback on other lenders' loans.
2. **The 7.7× is what you get when every input sits at the top of its evidence range at once.** On the evidence, one online saver returns **about 0.3×** (₹274 back on ₹825) and does not pay back within eight years.
3. **Keeping the founders' loan sizes, with everything else at the evidence, gives 1.3–1.5×.**
4. **Saving alone does not pay its way.** With no loans the plan returns 0.31×. At evidence values, serving a saver (₹420 over five years) costs more than the fund fees they bring (₹360). Every rupee of value has to come from loans.

So the business is a **loan-distribution business with a savings front end**. Whether it works depends almost entirely on one number nobody has measured: how much lenders pay us per saver won.

## Three readings of the same plan

| Reading | Online LTV/CAC, 5 years | Pays back |
|---|---|---|
| The plan as built | 7.7× | month 12 |
| A careful investor's reading of the plan's own inputs: no unsourced yearly rises, non-savers reachable only early, a real first cohort at seed cost (`recalc.md`) | about 4.5× | month 18 |
| The founders' loan sizes kept, every other input at the evidence | 1.3–1.5× | month 42–46 |
| Every input at the evidence (`evidence.md`) | 0.3× | after year 8 |

## Where the plan sits outside the evidence

| Input | Plan | Evidence | Effect alone (plan 7.7×) |
|---|---|---|---|
| Personal + business loan size | ₹3 lakh | ₹15,000–1.2 lakh; first loans ₹5–25k. A ₹3 lakh, 18-month loan needs ₹38–55k a month of income; these savers earn ₹20–40k. | 3.0× at ₹50k |
| First loans a year (apply × approved) | 35% × 30% = 10.5% of reachable users | 1–5% actually borrow on Paytm, Kissht and PhonePe. Kissht approves 11% of new applicants. | 4.4× at 20% apply; 6.1× at 20% approved |
| Cost to win a saver | ₹450 | ₹800–1,400 per new investor at Groww (83% organic sign-ups); our own seed budget is ₹600. | 4.6× at ₹750 |
| Home / property loan size | ₹30 lakh / ₹25 lakh | ₹10–15 lakh / ₹3–10 lakh at mass-market lenders | 6.5× at ₹12 lakh / ₹5 lakh |
| Payout rise, take-up and approval rises | 2%→3%; +5% and +10% a year | Rate cards say 1–2.5%, flat; nothing found for the yearly rises | 5.3× with all three flat |
| Non-savers seeing offers | 1.5 per saver, reachable while the saver saves; 54% of LTV | Not observed. The opt-in rate is unmeasured. | 3.5× with offers to savers only |

Inside the evidence, each worth under 1×: the fund commission, month-12 retention, repeat approvals and debit costs.

## What has to be true

Loan fees per saver won over five years are ₹3,686 in the plan and about ₹260 on the evidence. At the evidence's ₹750 cost to win and today's retention:
- **break-even (1×)** needs about ₹800 of loan fees per saver won, 3× the evidence;
- **3×** needs about ₹2,400, 9–10× the evidence.

In terms the seed can measure, the average approved loan needed is:

| First loans a year among reachable users | Cost to win ₹750: for 1× | ₹750: for 3× | Cost to win ₹450: for 1× | ₹450: for 3× |
|---|---|---|---|---|
| 4% (20% apply × 20% approved, the evidence) | ₹3.0 lakh | ₹10.8 lakh | ₹1.5 lakh | ₹6.0 lakh |
| 6% (25% × 25%) | ₹1.8 lakh | ₹6.8 lakh | ₹0.9 lakh | ₹3.7 lakh |
| 10.5% (35% × 30%, the plan) | ₹1.0 lakh | ₹3.8 lakh | ₹0.4 lakh | ₹2.1 lakh |

Even with the plan's funnel and the plan's cost to win, 3× needs loans averaging ₹2.1 lakh. That is above what this income band borrows.

## My judgment

- **The 7.7× should not be shown to investors as the base case.** Its inputs are labelled targets, but a diligence analyst will rebuild it from market data and land near 0.3–1.5×. That costs more credibility than a lower honest number would.
- **The real question is not "is LTV/CAC 7.7×?" but "can we earn ₹800–2,400 of lender fees per saver won?"** No public evidence says yes for ₹100-a-day savers. None says no either: nobody has measured savers who chose to see lender offers. That is exactly what the seed should buy.
- **Levers that change the economics** (founders' call; none is in the plan):
  1. **Prove the loan funnel first, cheaply.** Run lender offers to KYC'd users before scaling the savings product; it is the whole value.
  2. **Bigger savers.** ₹300 a day lifts the evidence case from 0.3× to 1.2× through fund fees and eligibility.
  3. **A cheaper way to win savers.** Employer, merchant or partner distribution: ₹300 to win gives 0.8× on the evidence, 2.5 times the base.
  4. **Earn more per loan than a 2% referral** (co-lending or an own book later). That needs capital and a licence.
  5. **Size loans to income.** Plan honestly on ₹50k–1.2 lakh personal and business loans.
- **The seed must measure, by monthly group of users:**
  - the share of KYC'd users who opt in to lender offers;
  - the share who take a first loan;
  - the median approved loan;
  - the fee lenders actually pay after clawbacks, in writing;
  - the cost per saver who makes a first debit;
  - still saving at months 3, 6 and 12, and the cost to serve each saver.

## What changed after this note (founders' choice, 23 Oct: option a)

The plan case stays at 7.7×. A "What has to be true: the one number" page now sits in the LTV/CAC deck (page 17) and the business case
(page 4). It shows, worked out from the model:
- the lender fees per saver won in the plan (₹3,686);
- what 3× needs (₹1,358) and break-even (₹368), with every other input as planned;
- the same at ₹750 to win and fewer keep saving (₹2,430 and ₹780);
- ordinary app users at today's market rates (₹258, 0.3×).

The deck's product table now counts durable and vehicle loans for savers only (₹13 each). The other display error (the inputs table's
10% extra-SIP take-up) and the two cost slips in `recalc.md` (contingency on serving, clawback on other lenders' loans; −0.15× together)
are not fixed: fixing the slips moves the headline to 7.6× and means re-pushing both sheets.

Later on 23 Oct the founders asked for this as a story in the LTV/CAC deck, told with pictures. Three pages now sit in its "What has to be
true" section:
- page 16, the credit bet: the plan against the market for each target, with a proven / not proven tag;
- page 17, the one number;
- page 18, how fragile it is and how we find out: LTV/CAC with one target missing and with two or three missing, then the five checks.

The cover, the answer page and the business case cover now say 7.7× "if our loan targets hold".

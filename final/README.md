# Save91 / SaveMore: final documents

Built 24 Oct 2026 by `final/make_final.py` from the files and tables in this repo. Do not edit this README by hand; edit the script and run it again.

The plan: savers put away ₹100 a day by UPI into mutual funds in their own name (80% equity, 20% debt). We earn fund fees and, as a loan marketplace, referral fees from lenders. 9 in 10 savers come online, pan-India; 1 in 10 through doorstep agents in NCR. The app never holds anyone's money.

## The numbers in three lines

- The cost to win is measured: ₹495 an online saver (₹450 plus the 10% contingency; ₹600 in the seed). The value of a saver is not: with its ten unmeasured inputs drawn anywhere between today's market and our targets (1,000 random what-ifs), the median online saver returns 1.75× over five years (1 in 10 below 0.8×) and pays back in month 39; 23% of the what-ifs reach 3× and 84% pay back.
- The main case is that median. At 20,000 online savers won a month from month 30 the company is EBITDA-positive from month 63, needs $4.7M in all, and adds up to −₹15 crore of EBITDA over eight years.
- The ladder: at 3× profit comes in month 46 on $3.1M; at our targets (7.7×, every loan target at once) month 33 on $1.8M; at today's market (0.4×) not by year 8.

Every figure is a plan with targets, not evidence. The targets the seed must prove (from `tables/online_inputs_audit.csv`):

- Personal + business loan size (blended): ₹3,00,000
- Loan apply rate a year: 35%
- Loan payout and its rise: 2% rising to 3% by month 60
- Cost to win a saver after the seed: ₹450 (495 with the 10% contingency)
- Loan against property ticket: ₹25,00,000
- KYC'd users who see loan offers, per saver: 2.5
- Lender-offer opt-in: at least 35% of KYC'd users

## Documents

| File | What it is | Pages | Built from |
|---|---|---|---|
| [`1_Online_business_case.pdf`](1_Online_business_case.pdf) | The short read: the main case (the LTV/CAC Monte Carlo median), the odds, the company at each LTV/CAC, the financials, and what the seed measures. | 9 | `others/online/Online_business_case.pdf` |
| [`2_Online_plan_v4.pdf`](2_Online_plan_v4.pdf) | The full online-first plan on the main case: the customer and product, one saver, the loan funnel, the odds, the company at each LTV/CAC, the financials, and an appendix with every input (market, main case, target), year-by-year tables, the Monte Carlo, the levers, the input audit and the spreadsheet check. | 28 | `others/online/Online_model_v4.pdf` |
| [`3_LTV_CAC_one_saver.pdf`](3_LTV_CAC_one_saver.pdf) | What one saver is worth, in ten pages: how one saver makes money at our targets, how each assumption changes the number, the odds, the company at each LTV/CAC, and the five checks the seed runs. | 10 | `others/ltv/LTV_CAC_simple.pdf` |
| [`4_Seed_plan_0.5M.pdf`](4_Seed_plan_0.5M.pdf) | The $0.5M seed: customers (1 lakh sign-ups), product and team for 24 months, the reserve, and what the seed must prove. | 9 | `others/seed/Seed_Plan_investor.pdf` |
| [`5_Bachatt_teardown_memo.pdf`](5_Bachatt_teardown_memo.pdf) | Context: what Bachatt has built, what is still vision, and where the market is open (memo, 19 Oct). | 8 | `others/memo/Bachatt_teardown_memo.pdf` |

## Live Google Sheets

- **[Save4More || Financial Model](https://docs.google.com/spreadsheets/d/1gDfeyy2YSmZt79-KTHM2wHdsanNyAVyTFQl7W9zQjMM)**: The company, live, on the main case. Start at the 'Start here' tab; change the blue cells on 'v4 Inputs' and every v4 tab recalculates. 'v4 Monte Carlo' has the LTV/CAC Monte Carlo and the company at each LTV/CAC. The older offline tabs are hidden (View > Hidden sheets).
- **[SaveMore || LTVCAC](https://docs.google.com/spreadsheets/d/1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4)**: One saver, live, on the main case: every input with today's market and our target beside it, the waterfall, the 1,000 futures of the LTV/CAC Monte Carlo, and a Projector tab that answers questions about them.

Both sheets are checked against the Python model: the company sheet's formulas are replayed in `others/model/v4_toy_check.py` (`others/tables/v4_toy_check.csv`), the workbook's in `others/model/ltv_book.py` (`others/tables/ltv_book_check.csv`).

## Open items

- BSE StAR MF and the fund houses to confirm a daily SIP on one mandate (questions: `others/outreach/2026-10-22_daily_sip_questions.md`). Until then the plan pays ₹2 a debit, weekly; at no debit cost the online saver's LTV/CAC rises (see the LTV/CAC deck, 'The tests that matter').
- Insurance: a fixed referral fee through a broker, to be agreed. The plan counts it as 0.
- Loan sizes (home ₹30 lakh, property ₹25 lakh, personal and business ₹3 lakh) are the founders' numbers of 22 Oct, above what the research observed; the seed's first lending partner measures them.
- Founder bios: later, when a pitch deck is built.

## Background (linked, not copied)

- [`others/reviews/2026-10-21/CRITICAL_REVIEW.pdf`](../others/reviews/2026-10-21/CRITICAL_REVIEW.pdf): The four-angle critical review (investment, analyst, story, regulation). Its numbers are from before the 22 Oct fixes and the loan-size change; what was fixed is in INVESTMENT_REVIEW_v4_status.md.
- [`others/reviews/INVESTMENT_REVIEW_v4_status.md`](../others/reviews/INVESTMENT_REVIEW_v4_status.md): Each point of the earlier investment review, with its status in the current plan.
- [`others/tables/online_inputs_audit.csv`](../others/tables/online_inputs_audit.csv): Every input against its source, with a verdict (matches, partly, judgement, target).
- [`others/research/`](../others/research/): The evidence: one row per source, with IDs the decks cite.
- [`others/ltv/LTV_CAC_deck.pdf`](../others/ltv/LTV_CAC_deck.pdf): The detailed LTV/CAC deck (32 pages): every assumption with its range and sources, at our targets. Its Monte Carlo pages are the earlier, plan-centred one (22 Oct); the current odds are in the decks in final/.
- [`others/README.md`](../others/README.md): The map of everything behind final/.

Superseded: [`others/archive/`](../others/archive/README.md) holds the earlier offline street-agent plan (16–18 Oct).

## Refreshing this folder

After changing an input, rebuild in this order (from the repo root), then run this script:

```
cd others/model && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python ltv_odds.py && PYTHONPATH=. python online_mc.py && PYTHONPATH=. python ltv_book.py <payload_dir>
cd .. && for b in ltv/build_ltv_deck.py ltv/build_ltv_simple.py online/build_online_v4.py online/build_online_case.py seed/build_seed_plan.py; do PYTHONPATH=model python $b; done
cd .. && python final/make_final.py
```

The sheets are pushed separately (`others/model/v4_gsheet.py`, `v4_toy_check.py`, `v4_ltv_tab.py`, `ltv_book.py`).

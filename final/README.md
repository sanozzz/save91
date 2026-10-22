# Save91 / SaveMore: final documents

Built 22 Oct 2026 by `final/make_final.py` from the files and tables in this repo. Do not edit this README by hand; edit the script and run it again.

The plan: savers put away ₹100 a day by UPI into mutual funds in their own name (80% equity, 20% debt). We earn fund fees and, as a loan marketplace, referral fees from lenders. 9 in 10 savers come online, pan-India; 1 in 10 through doorstep agents in NCR. The app never holds anyone's money.

## The plan in three lines

- One online saver costs ₹495 to win (with the 10% contingency) and returns 7.7× that over five years; it pays back in month 12. A doorstep saver returns 5.6×.
- The company, at 20,000 online savers won a month from month 30, is EBITDA-positive from month 33 and needs $1.8M in all; year-5 EBITDA ₹67.7 crore.
- Across 1,000 simulated futures (a stress test, not odds), the online saver's median LTV/CAC is 5.2× (1 in 10 below 2.9×); 89% reach 3×, and the company is profitable by month 60 in 99%.

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
| [`1_Online_business_case.pdf`](1_Online_business_case.pdf) | The short read: what the numbers say in the plan, and the five numbers that change them. | 9 | `online/Online_business_case.pdf` |
| [`2_Online_plan_v4.pdf`](2_Online_plan_v4.pdf) | The full online-first plan: the saver, the company year by year, the Monte Carlo, the levers, and an appendix with every input, its source and the input audit. | 28 | `online/Online_model_v4.pdf` |
| [`3_LTV_CAC_one_saver.pdf`](3_LTV_CAC_one_saver.pdf) | What one saver is worth: the cost to win them, each revenue stream, serving, payback, and the tests that matter. | 29 | `ltv/LTV_CAC_deck.pdf` |
| [`4_Seed_plan_0.5M.pdf`](4_Seed_plan_0.5M.pdf) | The $0.5M seed: customers (1 lakh sign-ups), product and team for 24 months, the reserve, and what the seed must prove. | 9 | `seed/Seed_Plan_investor.pdf` |
| [`5_Bachatt_teardown_memo.pdf`](5_Bachatt_teardown_memo.pdf) | Context: what Bachatt has built, what is still vision, and where the market is open (memo, 19 Oct). | 8 | `memo/Bachatt_teardown_memo.pdf` |

## Live Google Sheets

- **[Save4More || Financial Model](https://docs.google.com/spreadsheets/d/1gDfeyy2YSmZt79-KTHM2wHdsanNyAVyTFQl7W9zQjMM)**: The company, live. Start at the 'Start here' tab; change the blue cells on 'v4 Inputs' and every v4 tab recalculates. The older offline tabs are hidden (View > Hidden sheets).
- **[SaveMore || LTVCAC](https://docs.google.com/spreadsheets/d/1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4)**: One saver, live: every input, the waterfall, the 1,000 simulated futures, and a Projector tab that answers questions about them.

Both sheets are checked against the Python model: the company sheet's formulas are replayed in `model/v4_toy_check.py` (`tables/v4_toy_check.csv`), the workbook's in `model/ltv_book.py` (`tables/ltv_book_check.csv`).

## Open items

- BSE StAR MF and the fund houses to confirm a daily SIP on one mandate (questions: `outreach/2026-10-22_daily_sip_questions.md`). Until then the plan pays ₹2 a debit, weekly; at no debit cost the online saver's LTV/CAC rises (see the LTV/CAC deck, 'The tests that matter').
- Insurance: a fixed referral fee through a broker, to be agreed. The plan counts it as 0.
- Loan sizes (home ₹30 lakh, property ₹25 lakh, personal and business ₹3 lakh) are the founders' numbers of 22 Oct, above what the research observed; the seed's first lending partner measures them.
- Founder bios: later, when a pitch deck is built.

## Background (linked, not copied)

- [`reviews/2026-10-21/CRITICAL_REVIEW.pdf`](../reviews/2026-10-21/CRITICAL_REVIEW.pdf): The four-angle critical review (investment, analyst, story, regulation). Its numbers are from before the 22 Oct fixes and the loan-size change; what was fixed is in INVESTMENT_REVIEW_v4_status.md.
- [`INVESTMENT_REVIEW_v4_status.md`](../INVESTMENT_REVIEW_v4_status.md): Each point of the earlier investment review, with its status in the current plan.
- [`tables/online_inputs_audit.csv`](../tables/online_inputs_audit.csv): Every input against its source, with a verdict (matches, partly, judgement, target).
- [`research/`](../research/): The evidence: one row per source, with IDs the decks cite.

Superseded: the PDFs in the repo root and `START_HERE.md` describe the earlier offline street-agent plan (16–18 Oct).

## Refreshing this folder

After changing an input, rebuild in this order, then run this script:

```
cd model && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python online_mc.py && PYTHONPATH=. python ltv_book.py <payload_dir>
cd .. && for b in ltv/build_ltv_deck.py online/build_online_v4.py online/build_online_case.py seed/build_seed_plan.py; do PYTHONPATH=model python $b; done
python final/make_final.py
```

The sheets are pushed separately (`model/v4_gsheet.py`, `model/v4_toy_check.py`, `model/v4_ltv_tab.py`, `model/ltv_book.py`).

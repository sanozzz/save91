# Save91 / SaveMore: final documents

Built 24 Oct 2026 by `final/make_final.py` from the files and tables in this repo. Do not edit this README by hand; edit the script and run it again.

The plan: savers put away ₹100 a day by UPI into mutual funds in their own name (80% equity, 20% debt). We earn fund fees and, as a loan marketplace, referral fees from lenders. 9 in 10 savers come online, pan-India; 1 in 10 through doorstep agents in NCR. The app never holds anyone's money.

## The numbers in three lines

- Cross-selling alone (loans and cards) brings ₹143 per saver in five years and ₹173 in eight: 0.29× and 0.35× of the ₹495 it costs to win a saver (₹450 at scale, the founders' figure, plus the 10% contingency), and less than the ₹190 / ₹225 it costs to serve them (-0.10× after serving). With fund fees a saver returns 0.75× in five years and 1.32× in eight and pays back in month 75. How long savers keep saving (Bachatt's 30–40%) gives 0.60–0.93× at five years in 8 of 10 Monte Carlo draws. Debits at ₹0 and the 0.75% equity fund fee are still to be confirmed in writing.
- The main case: at 20,000 online savers won a month from month 30 the company is not EBITDA-positive by year 8; it needs at least $9.3M by month 96 and the cash is still falling then.
- What it takes: 2× (₹161 a day, 41% still saving at a year, loans most of the way to our old targets) brings profit in month 68 on $5.1M; 3× (₹194 a day, 44%) in month 55 on $4.0M.

Since 24 Oct the founders fixed every input of a saver's value (market figures, Bachatt, or our judgement: ₹70k first loans, 20% apply, 20% approved, 2% lender payout); only retention and the debt fund's fee are still drawn. The decisions and sources are in `others/reviews/2026-10-24_rebase/BRIEF.md` and `FIXES.md`; the bridge from last week's 1.75× is `others/tables/ltv_bridge.csv`.

## Documents

| File | What it is | Pages | Built from |
|---|---|---|---|
| [`1_Online_business_case.pdf`](1_Online_business_case.pdf) | The short read, rebased 24 Oct on the founders' market and measured inputs: one saver on the main case, the odds, what it takes (the ladder), the company's financials, and what the seed measures. | 8 | `others/online/Online_business_case.pdf` |
| [`2_Online_plan_v4.pdf`](2_Online_plan_v4.pdf) | The full online-first plan on the main case: the customer and product, one saver, the loan funnel, the odds, what it takes, the financials, and an appendix with every input, year-by-year tables, the Monte Carlo, the levers, the input audit and the spreadsheet check. | 29 | `others/online/Online_model_v4.pdf` |
| [`3_LTV_CAC_one_saver.pdf`](3_LTV_CAC_one_saver.pdf) | What one saver is worth over 5 and 8 years, and how much of it is cross-selling: the bridge from last week's 1.75×, the inputs now used, the odds, what it takes, the company, and the four facts that decide it. | 9 | `others/ltv/LTV_CAC_simple.pdf` |
| [`4_Seed_plan_0.5M.pdf`](4_Seed_plan_0.5M.pdf) | The $0.5M seed: customers (1 lakh sign-ups), product and team for 24 months, the reserve, and what the seed must prove. | 12 | `others/seed/Seed_Plan_investor.pdf` |
| [`5_Bachatt_teardown_memo.pdf`](5_Bachatt_teardown_memo.pdf) | Context: what Bachatt has built, what is still vision, and where the market is open (memo, 19 Oct). | 8 | `others/memo/Bachatt_teardown_memo.pdf` |

## Live Google Sheets

- **[Save4More || Financial Model](https://docs.google.com/spreadsheets/d/1gDfeyy2YSmZt79-KTHM2wHdsanNyAVyTFQl7W9zQjMM)**: The company, live, on the main case. Start at the 'Start here' tab; change the blue cells on 'v4 Inputs' and every v4 tab recalculates. 'v4 Monte Carlo' has the LTV/CAC Monte Carlo and what it takes. The older offline tabs are hidden (View > Hidden sheets).
- **[SaveMore || LTVCAC](https://docs.google.com/spreadsheets/d/1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4)**: One saver, live, on the main case: every input with its source (and its range where still uncertain), the waterfall, the 1,000 futures of the LTV/CAC Monte Carlo, and a Projector tab that answers questions about them.

Both sheets are checked against the Python model: the company sheet's formulas are replayed in `others/model/v4_toy_check.py` (`others/tables/v4_toy_check.csv`), the workbook's in `others/model/ltv_book.py` (`others/tables/ltv_book_check.csv`).

## Open items

- Debits at ₹0 to us are UNCONFIRMED: BSE StAR MF and the fund houses must confirm in writing a daily ₹100 SIP on one mandate, probably one hybrid fund since most daily minimums are ₹100 a scheme (questions: `others/outreach/2026-10-22_daily_sip_questions.md`). If we pay ₹2 a weekly debit, money needed rises to $11.7M.
- Bachatt's AVERAGE daily amount (₹100 is the minimum; ₹126 a day takes one saver to 1×) and its exact share still saving at 12 months (30–40% given; 41% takes one saver to 1×).
- The 0.75% equity fund fee in writing from a fund house (0.5% raises money needed to $10.6M).
- Insurance: a fixed referral fee through a broker, to be agreed. The plan counts it as 0. Recharge, bills, FD and NPS are not in the launch app.
- Founder bios: later, when a pitch deck is built.

## Background (linked, not copied)

- [`others/reviews/2026-10-21/CRITICAL_REVIEW.pdf`](../others/reviews/2026-10-21/CRITICAL_REVIEW.pdf): The four-angle critical review (investment, analyst, story, regulation). Its numbers are from before the 22 Oct fixes and the loan-size change; what was fixed is in INVESTMENT_REVIEW_v4_status.md.
- [`others/reviews/INVESTMENT_REVIEW_v4_status.md`](../others/reviews/INVESTMENT_REVIEW_v4_status.md): Each point of the earlier investment review, with its status in the current plan.
- [`others/tables/online_inputs_audit.csv`](../others/tables/online_inputs_audit.csv): Every input against its source, with a verdict (matches, partly, judgement, target).
- [`others/research/`](../others/research/): The evidence: one row per source, with IDs the decks cite.
- [`others/ltv/LTV_CAC_deck.pdf`](../others/ltv/LTV_CAC_deck.pdf): The detailed LTV/CAC deck (32 pages): every assumption with its range and sources. Older than the 24 Oct rebase; the current numbers are in the decks in final/.
- [`others/reviews/2026-10-24_rebase/BRIEF.md`](../others/reviews/2026-10-24_rebase/BRIEF.md): The 24 Oct rebase: each founders' decision, its source, and every headline number with its table.
- [`others/README.md`](../others/README.md): The map of everything behind final/.

Superseded: [`others/archive/`](../others/archive/README.md) holds the earlier offline street-agent plan (16–18 Oct).

## Refreshing this folder

After changing an input, rebuild in this order (from the repo root), then run this script:

```
cd others/model && PYTHONPATH=. python ltv_odds.py && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python ltv_bridge.py && PYTHONPATH=. python ltv_book.py <payload_dir>
cd .. && for b in ltv/build_ltv_deck.py ltv/build_ltv_simple.py online/build_online_v4.py online/build_online_case.py seed/build_seed_plan.py; do PYTHONPATH=model python $b; done
cd .. && python final/make_final.py
```

The sheets are pushed separately (`others/model/v4_gsheet.py`, `v4_toy_check.py`, `v4_ltv_tab.py`, `ltv_book.py`).

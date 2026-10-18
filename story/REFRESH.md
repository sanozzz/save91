# Refresh, 18 October 2026

The company, on the same streets and the same savings product as the 17 Oct base, with the loan, the borrowings and the collection rail set to figures the folder already contains. `tables/base_*.csv` is untouched. The deck still shows the old base. The engine run is `model/refresh_case.py`. A rerun of the published inputs on this path matches the base: year-5 revenue ₹468.22 crore, EBITDA −₹7.85 crore, PAT ₹16.99 crore, lenses ₹11,043 / ₹10,073 / ₹6,890 crore, ₹1,108 crore raised.

## What changed, and what did not

| Input | Published base | Refresh | Why |
|---|---|---|---|
| Personal-loan ticket | ₹2.5 lakh | ₹58,522 | XL-29, CRIF national average. XL-42's ₹25,557, the closer ticket for this segment, is not the one used. |
| Home-loan ticket | ₹25 lakh | ₹11.8 lakh | XL-25, Home First ATS. That book is mostly salaried. |
| Apply rate | 18% a year | 3.6% a year | The review's reading of XL-04: 0.93% of Paytm's monthly users are key financial-services customers in a quarter, times four. It is an annualised stock, not a counted apply rate, and the row says the 0.93% includes merchants and broking. |
| NBFC borrowings | 3× equity | 1.16× equity | LEV-023 gearing. At month 60 the book is above the ₹10 crore net-owned-funds floor and the multiple is 1.16×. Earlier months sit on the floor, with borrowings at zero. |
| UPI by month 12 | 30% | 100% | The Bachatt collection note. A cash share for smaller cities was not given, so none is modelled. |
| Bought-lead cost | ₹250 | ₹300 | Saket Khandelwal, both channels. This prices the bought half. Half of sign-ups are still bought leads. Agent salary is unchanged, so the street cost per sign-up is still about ₹240, not ₹300. |

Left as published, because no number was given: ₹350 a day, 55% still saving at month 12, the debt fund at 0.35% and about 7%, sign-ups per agent, the 5,000-agent cap, 30% of personal loans on book, loss at 0.6× the agreed. No OD++ limit. No wallet balance. No 80/20 trail. The online 1 to 1.5 lakh has no period, so the fleet was not replaced with an online plan.

The fleet path was not searched again. It is the published one: 300 agents by month 18, then 150 a month, cap 5,000, a new city when the best open city has under 25,000 sign-ups of headroom a head.

## The company at these inputs

| | 17 Oct base | Refresh |
|---|---|---|
| Active savers, month 60 | 36.6 lakh | 36.6 lakh |
| Fund AUM, month 60 | ₹22,383 crore | ₹22,383 crore |
| Year-5 fee revenue | ₹264.4 crore | ₹170.1 crore |
| Year-5 net interest | ₹178.9 crore | ₹9.5 crore |
| Year-5 processing fees | ₹24.9 crore | ₹1.1 crore |
| Year-5 revenue | ₹468.2 crore | ₹180.7 crore |
| Year-5 EBITDA | −₹7.9 crore | −₹264.8 crore |
| Year-5 interest on cash | +₹25.5 crore | +₹45.0 crore |
| Year-5 PAT | +₹17.0 crore | −₹220.4 crore |
| Cumulative EBITDA, months 1–60 | −₹368 crore | −₹760 crore |
| Cumulative EBITDA, months 1–96 | | −₹1,481 crore |
| Months with EBITDA above zero | from month 55 | none in 96 months |
| Loan book, net, month 60 | ₹1,576 crore | ₹71 crore |
| NBFC equity / borrowings, month 60 | ₹394 / ₹1,182 crore | ₹32.9 / ₹38.1 crore |
| Fee ARR, month 60 | ₹285 crore | ₹183 crore |
| Lens 1, 20× ARR, month 60 | ₹11,043 crore | ₹3,933 crore |
| Lens 2, 0.45× AUM, month 60 | ₹10,073 crore | ₹10,073 crore |
| Lens 3, 3× equity + 20× fee ARR, month 60 | ₹6,890 crore | ₹3,752 crore |
| Both headline lenses clear ₹10,000 crore | months 59–74 | not by month 96 |
| Raised | ₹1,108 crore | ₹1,853 crore |
| Lowest cash | ₹9.0 crore | ₹9.7 crore |

Cash stays positive because the round engine raises more, not because the business does. Seed ₹13 crore, A ₹53 crore in month 8, B ₹212 crore in month 18, C ₹570 crore in month 32 priced on the AUM lens, D ₹530 crore in month 48 priced on the AUM lens, E ₹475 crore in month 59. Round E is still labelled a unicorn round: the AUM lens crosses ₹10,000 crore, and the pre-money is the 1.5× step-up, ₹12,226 crore. Founders hold 24.5% after it. Twenty times the fee ARR is ₹3,653 crore. That, plus three times the ₹33 crore of book equity, is lens 3.

## What moved the result

`tables/refresh_bridge.csv` runs the same path four times.

| Case | Year-5 revenue | Year-5 EBITDA | Raised |
|---|---|---|---|
| Published inputs | ₹468.2 crore | −₹7.9 crore | ₹1,108 crore |
| Ticket, apply rate, 1.16× only | ₹180.7 crore | −₹270.8 crore | ₹1,893 crore |
| Those, plus UPI at 100% | ₹180.7 crore | −₹260.2 crore | ₹1,828 crore |
| Refresh (those, plus a ₹300 lead) | ₹180.7 crore | −₹264.8 crore | ₹1,853 crore |

The loan ticket, the apply rate and the borrowings do the damage. UPI at 100% saves about ₹11 crore of year-5 EBITDA by taking out the cash cost, and about ₹65 crore of capital. A ₹300 lead instead of ₹250 costs about ₹5 crore of year-5 EBITDA. Savers and AUM do not move in any of the four, so lens 2 does not move.

## The draws

One thousand draws. The five changed inputs are held at the refresh values. Retention, the daily amount, sign-ups and the city pool still vary. The funding plan is the ₹1,853 crore plan, fixed, so a bad draw does not raise a further round.

| | Result |
|---|---|
| Both headline lenses clear ₹10,000 crore at month 60 | 0 of 1,000 |
| Lens 1 clears | 0 |
| Lens 2 clears | about 41% |
| Lens 3 clears | 0 |
| EBITDA positive for good by month 60 | 0 |
| Year-5 PAT at or above zero | 0 |
| Median lens 1 / lens 2 / lens 3 | ₹4,000 / ₹9,366 / ₹3,824 crore |
| Median year-5 revenue / EBITDA / PAT | ₹186 / −₹260 / −₹215 crore |
| Median loan book at month 60 | ₹67 crore |

Median lens 2 is the same ₹9,366 crore as the published base. The savings book was not the thing this run changed.

## What this is not

It is not the product the later conversations describe. That product is a small amount he is happy to save, a drop-off of the rest, and a wallet he can borrow from, reached mostly online. This run still collects ₹350 a day, still keeps 55% saving at month 12 whether or not they get a loan, and still fields 5,000 agents. Putting those conversations in as rates would have meant inventing the amount, the drop-off, the OD++ limit and the trail.

Checks on the refresh: 28 of 28 in `tables/refresh_checks.csv`.

# Working the investment-committee review

18 October 2026. The agreed base numbers are unchanged. This pass fixes labels the review showed were wrong, and writes the customer problem that was missing. The findings that change a headline need a decision before the base moves.

The review itself stays in `INVESTMENT_REVIEW.md`. Do not edit it to mark findings closed.

## Done in this pass

| Finding | What changed |
|---|---|
| F11 | The 3× debt multiple is still the base. The source line no longer cites LEV-023's AUM/TNW of 3.25× as if it were gearing. LEV-023's gearing is 1.16×. The only row near 3× is LEV-063 (Moneyview, 3.2×). Updated in `dist_agreed_v1.csv`, `base_inputs.csv`, `nbfc.py`. |
| F12 | The check text said partners keep 85%. The executed base keeps 30%, so partners keep 70%. `base_checks.csv` and `base30_checks.csv` now say 70%. The 15% case still says 85%. The 50% case now says 50%. Comments in `base_plan.py` and `nbfc.py` say the 15% / 0.5× wording is the superseded case. |
| F18 | START_HERE §6 no longer says team leads, offices and licences are "not in the numbers". They are in. The app, support and NBFC operating cost are described as thin. |
| F20 | On an 8-year run the total column is named "Eight years". It was named "Five years" and held the 8-year total. `tables/base_yearly.csv` (and the 15/30/50 copies) are renamed. A 5-year run still says "Five years". |
| F07 | PR-01's confidence no longer starts with "Published". It is one practitioner's statement. The sign-up input was already labelled "Your number". |
| F25 | The customer's three problems are in `story/CUSTOMER_PROBLEM.md` and at the top of START_HERE §2. They are not yet a page in `Offline_model_v3.pdf`. |

## Not done, because each one replaces the agreed base

These are the committee's P1s. None has been rerun.

| Finding | Decision needed before a rerun |
|---|---|
| F01–F03 | Keep 20× ARR and 0.45× AUM as exhibits, and add fee-only ARR and lens 3 as the figures we would defend. |
| F04–F06 | Personal-loan ticket, home-loan ticket and the yearly apply rate. The folder's own anchors are about ₹58,500, ₹11.8 lakh and about 3.6% a year. The base is ₹2.5 lakh, ₹25 lakh and 18%. |
| F07–F08 | Sign-ups and month-12 survival. The base is 100 a month and 55% still saving. The field interview is 6–10 a month. The online evidence on the deck is 24% still saving. |
| F09, F23 | Cash collection versus a UPI mandate. Bachatt, by the conversation, is 100% UPI, with some cash only in smaller cities. |
| F10 | State year-5 EBITDA of −₹7.9 crore, and PAT excluding interest on cash, next to PAT of ₹17 crore. |
| F11 | Whether 3× stays, or the case is also shown at 1.2× and 2×. The citation is fixed. The multiple is not. |
| F12 | A haircut on the fee or the approval rate for the 70% left with partners. The label is fixed. The price is not. |
| F22, F24 | 80% equity SIP / 20% debt, and the trail on each. The Bachatt trail rate was not stated. The model cannot be rerun on it until it is. |
| F26 | Acquisition. Saket Khandelwal (growth, Bachatt) says most customers are online, the NCR street fleet is 40 to 50 people at about 5,000 a month, and CAC is about ₹300 on both channels. Filed as PR-02. The base is still half bought leads at ₹250, no app-only channel, and an online cost of ₹499. Not rerun. |
| F27 | Retention. Same conversation. He says the customer is credit hungry, and Bachatt retains better than Jar because it helps the customer get the loan they want. Filed as PR-03. He gave no rate. The base still holds 55% still saving apart from the 18% apply rate and the ₹2.5 lakh ticket. Not rerun. |
| F28 | Drop-off. Aniket, surname and role not stated, says the customer has a small amount he is happy to save, some keep saving, and the rest drop off. Filed as PR-04. No amount and no share. The base is still about ₹350 a day and 55% still saving. Not rerun. |
| F29 | Product shape. The operator says the customer treats Bachatt as a digital wallet he saves into and then borrows from, and that the product he wants is an OD++. Filed as PR-05. No limit and no rate. The base is still a term personal loan and a home loan. Not rerun. |

## Bachatt growth, recorded and not yet in the model

Source: conversation with Saket Khandelwal, https://www.linkedin.com/in/saket-khandelwal-1612ab122/. One conversation. The online 1 to 1.5 lakh has no period attached. Do not treat it as a monthly rate until he says so.

| | His figure | The base |
|---|---|---|
| Where customers come from | Mostly online | No app-only channel. Half of sign-ups are bought leads the agent still closes |
| Online volume | About 1 to 1.5 lakh customers, period not stated | Year-5 sign-ups, all cities, are 16.7 lakh for the year |
| NCR street | About 5,000 a month, 40 to 50 people | 540 agents in NCR once the city is mature |
| Per street person | 100 to 125 a month | 100 in year 1, falling to 70 |
| CAC | About ₹300 street and about ₹300 online | About ₹365 to win (about ₹240 salary + ₹125 leads). The online figure the deck beats is ₹499 |
| Why they stay | The customer is credit hungry. Bachatt gets them the loan they want. Jar does not. No rate given | 55% still saving at month 12, set on its own. The loan is a separate 18% apply rate |

## Why he says they keep the customer

Same conversation, filed as PR-03. He called this the insight. Bachatt retains better, he said, because the customer is credit hungry. They help the customer get the loan the customer wants. Jar does not. He did not give a still-saving rate or a Jar rate.

The base keeps these apart. Month-12 survival is 55%. The loan is an 18% yearly apply rate on a ₹2.5 lakh personal loan. If his mechanism is the one we adopt, a side case that cuts the ticket and the apply rate and leaves 55% in place overstates the book. The suggested run below is still the right first cut, and it has to be read that way: a revenue cut with survival held constant.

XB-10 already says Bachatt offers loans up to ₹5 lakh from partners. JAR-11 does not confirm that Jar makes the loan the saver asked for. Neither row is his retention number. Keeping the best 30% on our own book, and leaving partners the other 70%, is a different selection from "the loan they desire" if the partner then declines.

## The small save, the drop-off, and the wallet

Aniket, filed as PR-04. Surname, role and company were not stated. Do not attach him to Bachatt. The customer has a small amount he is happy to save. Some keep saving. The rest drop off. He gave no amount and no share. The operator's conclusion in that note is that technology has to do two jobs: help him save the small amount, and satisfy the credit hunger. That is the operator's test for whether a model exists. It is not a built product.

PR-05, the same sitting, is how the customer already sees Bachatt. A digital wallet. He saves something, then he borrows. The product he treats it as is an OD++. No limit and no rate.

The base is a different product. About ₹350 a day into a debt fund, collected by a person, plus a ₹2.5 lakh term loan and a ₹25 lakh home loan. No wallet balance. No overdraft. The right to borrow is not a function of the small amount saved.

## Suggested next run

One side case, not a replacement of `tables/base_*.csv`, using the folder's own anchors:

- personal-loan ticket ₹58,522;
- home-loan ticket ₹11.8 lakh;
- apply rate 3.6% a year;
- NBFC borrowings at 1.16× equity;
- valuation quoted as fee ARR and as lens 3, beside the two headline lenses.

Leave sign-ups, retention, the debt fund and the cash route as they are in that first run, so the lending and leverage effects can be read on their own. Read the 55% as held constant on purpose. PR-03 says the loan is why the customer stays, so that run is not a case in which the book would still look the same after the tickets are cut. The Bachatt product mix and the UPI rail are a second run, after the trail rate and the monthly SIP amount are written down. A retention split, by whether the customer got the loan they asked for, waits on a number he has not given.

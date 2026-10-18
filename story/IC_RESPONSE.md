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

## Suggested next run

One side case, not a replacement of `tables/base_*.csv`, using the folder's own anchors:

- personal-loan ticket ₹58,522;
- home-loan ticket ₹11.8 lakh;
- apply rate 3.6% a year;
- NBFC borrowings at 1.16× equity;
- valuation quoted as fee ARR and as lens 3, beside the two headline lenses.

Leave sign-ups, retention, the debt fund and the cash route as they are in that first run, so the lending and leverage effects can be read on their own. The Bachatt product mix and the UPI rail are a second run, after the trail rate and the monthly SIP amount are written down.

# Addendum 4: rates that grow with our pool's history (operator, 16 Oct 2026; OK'd by tap "OK as proposed")

## What the operator said (verbatim)

> "Also take up rates and sign ups and approva rates and loan size also go up over time on our pool as we gather more history and repayment of this customer"

## The five inputs

All five are agreed (`agreed_on` = 2026-10-16) and their confidence is "Our judgement". "Year" means calendar year of the business (pool history) unless it says the saver's own tenure.

| key | input | shape | low / likely / high | cap | context |
|---|---|---|---|---|---|
| signup_growth | Sign-ups per agent grow each year from year 2 (referrals, word of mouth) | pert | 0 / 10 / 20% a year | 100 a month | none: judgement |
| takeup_growth | All take-up hazards rise each calendar year as the pool's history grows (loan apply, cards, all 17 products) | pert | 0 / 5 / 15% a year, relative | 2× the agreed rate | |
| approval_growth | First-loan and card approval rise each calendar year as lenders see our pool's repayments | pert | 0 / 10 / 20% a year, relative | 80% absolute | XL-41 Kissht repeat 74% |
| ticket_growth | His next loan (repeat or top-up) is bigger for each year he has repaid | pert | 0 / 10 / 20% per year repaid, on the base ticket | ₹5 lakh | XL-12 Bachatt up to ₹5 lakh |
| topup_share | Top-up loans: share of borrowers with 12+ EMIs paid on time who take a top-up each year | pert | 5 / 15 / 30% | | NG-028: over half of Paytm merchant-loan money goes to repeat borrowers |
| topup_size | Top-up size, as a share of his original ticket (times ticket_growth) | pert | 25 / 40 / 60% | | |

**Mechanics:**

- **Year multipliers:** year y multiplier = (1 + g)^(y − 1). Apply it on top of the agreed rates and the early-months factors; caps apply after multiplying.
- **Top-ups:**
  - A top-up earns the origination fee net of taken back.
  - It does not block a repeat loan after the original ends, though at most one top-up runs at a time.
  - It adds to the collections base (fees per loan made apply to it pro rata by size).
  - Only borrowers who are still saving qualify; a top-up is the lender's call.
- **Sign-up growth** raises cash visits. The extra-capacity cost already handles it.

## Outputs to add

- Bridge steps: "sign-ups grow", "take-up and approvals grow with history", "loan size grows", "top-ups", placed after the early-months step.
- In the report:
  - top-ups per 100 borrowers a year;
  - average ticket by year;
  - money lent per agent by year;
  - P(NPV60 > 0) and P(NPV36 > 0) on the final settings.
- **Must-be-true:** add a band table for P(NPV60 > 0) by takeup_growth and approval_growth (0–5%, 5–10%, 10–20%).

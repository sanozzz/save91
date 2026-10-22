# Cohort-model inputs (shared list: the distribution sheet and the cohort model both use exactly these)

The operator said (16 Oct 2026):

> "So let's build a model of monthly cohort, their retention and saving rate and every detail and model it like that"

This list ADDS to the inputs in `story/BRIEF_distributions_2026-10-16.md`. Where an input appears in both, this file wins.

The proposed shapes are the lead's; the distribution builder checks the evidence. "Age" = months since he signed up (age 1 = his first month).

## 1. Sign-ups (each monthly cohort)

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| signups_run | Sign-ups a month once the agent is up to speed | pert | 50 / 83 / 100 | operator 1,000 a year = 83 a month |
| ramp_months | Months for a new agent to reach full speed (straight-line from 50%) | triangular | 0 / 3 / 6 | judgement |

## 2. Retention curve: share of a cohort still saving at each age

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| r3 | Still saving at month 3 | pert | 60% / 80% / 92% | janta steady ~2.7%/month gives ~92% (IV-11/12); app early drop (story_unit curve); SBI Choti SIP lost 36% of a year's sign-ups in the year (XO-05) |
| r12 | Still saving at month 12 | pert | 25% / 45% / 72% | as in the brief; the sampler enforces r12 < r3 |
| churn_late | Monthly drop-off after month 12 | pert | 1.0% / 1.5% / 3.0% | Acorns ~1–1.3% after year one (TB-11, distributions.csv `churn_late`); janta ~2.7% |

**Curve shape:**

- months 1–3: steady monthly drop-off h1 = 1 − r3^(1/3);
- months 4–12: h2 = 1 − (r12/r3)^(1/9);
- after month 12: churn_late.

A saver who stops saving withdraws his whole balance that month.

## 3. Saving rate (per active saver)

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| daily | Daily amount at sign-up | triangular | ₹200 / 350 / 500 | operator; IV-03 |
| days | Deposit days a month (while active) | pert | 16 / 20 / 24 | judgement |
| amount_growth | Growth in his daily amount per year saved | pert | 0% / 5% / 10% | judgement |

## 4. The fund (balance)

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| term | Savings term | fixed | 12 months | janta yearly terms |
| rollover | Share of the balance left in the fund at each term end | pert | 0% / 25% / 60% | judgement. **OPEN CHOICE** for the operator |
| withdraw_m | Share of the balance withdrawn mid-term, each month | pert | 0% / 1% / 3% | judgement |
| trail | Fund commission a year | pert | as in the brief (debt vs liquid: open choice) | |

## 5. UPI and capacity

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| upi_12 | Share of a cohort's active savers on UPI by month 12 | pert | 10% / 30% / 60% | operator: "some will turn into UPI and some will continue cash"; judgement |
| upi_ramp | UPI share | — | — | rises in a straight line from 0 at age 1 to upi_12 at age 12, then flat |
| visit_every | Days between cash visits | fixed | 2.5 | operator |
| capacity | Cash visits one agent can make a day | triangular | 300 / 400 / 450 | IV-01 |
| extra_capacity_cost | Cost of extra cash-collection capacity when visits exceed capacity | fixed | ₹20,000 a month per 400 visits a day, pro-rata (a second agent or a helper) | **This replaces "assume UPI absorbs it"** |

## 6. Loans (proven savers = age 7+, still saving)

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| apply | Apply a year (proven savers with no loan running) | pert | 8% / 18% / 35% | monthly hazard = 1 − (1 − apply)^(1/12) |
| eligible | Eligible | pert | 25% / 45% / 65% | as in the brief |
| approved_first | Approved, first loan | pert | 20% / 35% / 50% | as in the brief |
| approved_repeat | Approved, repeat loan (after repaying one) | pert | 50% / 70% / 85% | XL-41 Kissht 74% repeat vs 11% new; NG-028 Paytm: >50% of merchant-loan disbursals go to repeat borrowers |
| tenure | Loan tenure | triangular | 12 / 24 / 36 months | check XB-09 for the EMI basis of ₹10,073; set the likely value from it if the evidence says otherwise |
| ticket | Ticket | pert | ₹1.0 / 2.5 / 3.0 lakh | as in the brief |
| fee | Origination fee | pert | 1.5% / 2.625% / 3.5% | same on repeat loans |
| taken_back | Taken back | | as in the brief | |
| loss | Money lost on loans, after recoveries | pert | 1.5% / 3% / 5% | Paytm worst case (operator). The lender carries the loss |
| recovered, rec_fee | Recovered; our fee on recovered | | as in the brief | recovery fee = ticket × loss × recovered/(1 − recovered) × rec_fee, paid 18 months after disbursal |
| leaver_loan | A saver who stops saving keeps paying his loan | fixed | yes | his loan runs to term; he cannot get a repeat loan |
| coll_fee | Collection fee per EMI the agent collects | pert | 0% / 0% / 1% of each EMI | **OFF by default (likely 0)**. **OPEN CHOICE:** the operator said "our agent also helps us collect back"; a lender may pay for collecting every instalment |

## 7. Cards and insurance

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| card_share | Cards | pert | 1% / 3% / 6% of savers reaching month 7 | **OPEN CHOICE:** the operator said 5%. Issued spread evenly over ages 7–12, only to those still saving |
| card_fee | Fee per card | | as in the brief | |
| other | Insurance and other products | pert | ₹8 / 63 / 259 a proven saver a year | paid monthly (÷ 12) on proven savers still saving |

## 8. Costs and money terms

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| salary | Salary | fixed | ₹20,000 a month | decision |
| kyc_cost | Onboarding and KYC cost per sign-up | pert | ₹0 / 30 / 100 | judgement; check research/tri_costs*.md for a KYC cost |
| support_cost | Tele-sales and AI support, per active saver a month | fixed | ₹0 | **awaiting the operator's figure**; shown as a visible line at 0 |
| discount | Discount | fixed | 20% a year, monthly | |
| horizon | Horizon | fixed | 36 and 60 months | |

## 9. Regression switch (cohort model only)

A setting `legacy=True` must reproduce v2:

- steady drop-off from r12 only;
- half a year's deposits held in the cycle, with no rollover and no mid-term withdrawal;
- no amount growth, no ramp, no capacity cost;
- no repeat loans, with the apply hazard on all proven savers;
- cards at month 7, insurance from month 7;
- no KYC cost.

With legacy=True, it must match `tables/xs_npv_v2.csv` within ±1%, e.g. the 5-year NPV at 30 / 40 / 55 / 70 of −1,34,752 / +63,355 / +4,06,283 / +8,22,931.

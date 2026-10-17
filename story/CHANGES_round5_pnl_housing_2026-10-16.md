# Round 5: cumulative P&L instead of NPV, housing loans, the cash route, managers (operator taps, 16 Oct 2026)

## Operator answers (verbatim)

- **Discount:** "we dont need to have a discount rate as of now. Let VC calculate it. We need to show the numbers in cumulative PnL basis. My bad I said NPV."
- **Housing:** "These guys can get home loans upto 20-50 lakhs. so build accordingly..."
- **Cash route:** "he deposit to us and we move the funds to the debt fund account by depositing the cash in their account and providing them the reconciliation. next day every customer receives a message etc"
- **Managers:** "Founder in the pilot"

## 1. Metrics: undiscounted cumulative P&L

- Set the discount to 0. Keep the code path, with `discount` = 0 as a fixed decision.
- Headline measures, for one agent, undiscounted:
  - **Cumulative P&L at 36 months** and **at 60 months**: their p10 / p50 / p90 / mean;
  - P(cumulative P&L at 36 months > 0) and P(at 60 months > 0);
  - the **payback month** (the first month cumulative P&L turns positive and stays positive);
  - **pilot year 1 P&L**;
  - the **peak cash need**, i.e. the lowest point of cumulative P&L, which is how much money one agent needs before paying back.
- **Contract for the deck.** Write these to `tables/cohort_mc_summary.csv` with the `measure` names exactly as follows:
  - "Cumulative P&L at 36 months"
  - "Cumulative P&L at 60 months"
  - "P(cumulative P&L at 36 months > 0)"
  - "P(cumulative P&L at 60 months > 0)"
  - "Payback month (cumulative P&L turns positive)"
  - "Peak cash need (lowest cumulative P&L)"
  - "Year-1 P&L"

  Also write `tables/cohort_mc_cum_fan.csv`: month 1..60 × p10/p25/p50/p75/p90 of cumulative P&L. Keep the old NPV rows only as `legacy` (a measure prefix "NPV (legacy, 20% discount):").
- Must-be-true, drivers and bridge: re-run them on cumulative P&L at 60 months. The bridge step 0 for v2 is computed on the same undiscounted basis (legacy=True with discount 0).

## 2. Housing loans: two new products (other lenders' loans group)

| key prefix | product | take-up a year (active savers, no housing loan running) | ticket | our fee | evidence | confidence |
|---|---|---|---|---|---|---|
| loan_home | Home loan (affordable housing) | pert 0.3 / 1 / 2% | pert ₹10 / 25 / 50 lakh | pert 0.3 / 0.5 / 1.0% of the loan | XL-15 home-loan DSA 0.3–1% (typical 0.4–0.6%); XL-24 Aavas 61% self-employed; XL-25 Home First (income under ₹50k a month; 77% of leads via connectors); XL-26 PMAY-U 2.0 subsidy up to ₹1.8 lakh; XL-29 average home loan ₹32 lakh | ticket is "Your number" (operator: "upto 20-50 lakhs"); take-up is judgement |
| loan_lap | Loan against property (his shop or home) | pert 0.2 / 0.5 / 1% | pert ₹5 / 15 / 30 lakh | pert 0.5 / 1.0 / 1.5% | XL-16 | judgement |

**Rules:**

- **Once per saver** within 60 months: there are no repeats, and the loans are long-tenure.
- **Approval:** loan_home and loan_lap also pass an approval share, pert 30 / 45 / 60%. They are secured loans, so approval is higher than for unsecured loans (judgement).
- **Fee timing:** the fee is paid at disbursal, with no taken-back.
- **Early months:** the early-months factors apply. Approval growth applies too, with a cap of 80%.
- **Exclusions:** no collection fees on housing loans (the lender's own collections), and no ticket growth.
- **Eligibility caveat (show it on the A-page, not in the story):**
  - A ₹25 lakh home loan over 20 years at about 9% has an EMI of about ₹22,500. At a 50% EMI-to-income rule that needs about ₹45,000 a month of household income.
  - The interview says ₹20–40k (IV-04).
  - The take-up range is meant to reflect that only the better-off savers qualify.

## 3. The cash route (the operator's design): show it; flag the regulatory question

- **Flow:** saver hands cash to our agent → we deposit the cash into the debt fund's (AMC's) collection account and send the AMC the reconciliation → next day the saver gets a message confirming the units in his name.
- **Model:** no change. Cash-deposit charges sit inside the ₹5 running cost.
- **Flag (deck A12 and the sheet's decisions page): "needs a legal opinion before the pilot".** By the lead's reading of SEBI/AMFI rules, not in research:
  - distributors should not pool or handle investor money;
  - mutual-fund payments should come from the investor's own account (REG-066 / REG-081 in research say this);
  - cash investment in mutual funds is capped at about ₹50,000 per investor per year (to verify; not yet a research row).

  A ₹350-a-day saver puts in about ₹84,000 a year. It also reverses the earlier "the app never holds money" principle.

## 4. Managers

- Founder in the pilot: no manager cost in the pilot numbers.
- At scale, a team-lead cost is NOT included. Show this on A12.

## 5. A12 "what is left out": fix the stale lines

- **Support:** "Tele-sales and AI support: inside the ₹5 running cost" (it was "₹0 until you give a figure").
- **Managers:** "Managers: the founder in the pilot; a team lead per N agents at scale is not counted".
- **The cash route:** "Cash route: needs a legal opinion".
- **App:** "The customer app's build: not yet costed".
- **Licences:** as now.
- **Rules risks:** IRDAI caps (in the base), SEBI on digital gold.

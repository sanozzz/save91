# Addendum to COHORT_INPUTS: every cross-sell product, and collection fees on high-DPD buckets

## What the operator said (16 Oct 2026, verbatim)

> "Collection fee on collection done on high dpd buckets"

> "Have health insurance life insurance etc whatever the fuck we can cross sell"

This addendum REPLACES two things in `COHORT_INPUTS_2026-10-16.md`:

- the single `other` line (₹63 a saver a year) becomes the product lines in §1;
- `coll_fee` (a fee per EMI) becomes the DPD-bucket collection fees in §2.

Everything else stands.

**Sources:**

- Insurance, investment and payment numbers come from `research/xs_other_summary.md`, section 1, unless stated otherwise.
- Use **Our judgement** where no research row exists, and list it as a GAP. The operator may approve research to fill gaps; do not search the web.

## 1. Cross-sell products

Per proven saver (age 7+, still saving). Each product has a yearly take-up among proven savers who don't hold it, a ticket, and a commission. Insurance also renews.

| key prefix | product | take-up a year | ticket | our commission | renewal | basis |
|---|---|---|---|---|---|---|
| hlth_small | Small health / hospital cash | 2 / 6 / 15% | ₹300 / 800 / 1,500 premium | 10 / 15 / 20% of first-year premium | renews 30 / 50 / 70% a year at 5% commission | XO-19, XO-09, XO-10, XO-24, XO-30, XO-31, XO-35; IRDAI draft caps 15% first year / 5% renewal (REG-053..057) |
| hlth_family | Family health cover (₹3–5 lakh floater) | 0.5 / 2 / 5% | ₹6,000 / 10,000 / 15,000 premium | 10 / 15 / 20% | renews 60 / 75 / 89% at 5% | judgement; Policybazaar 89% health renewal (XO-09). **GAP:** no premium source |
| life_term | Term life (small cover) | 1 / 3 / 6% | ₹500 / 1,000 / 2,000 | 7.5 / 25 / 30% | renews 60 / 75 / 85% at 7.5% | XO-20, XO-32; renewal rate is judgement |
| accident | Personal accident | 2 / 5 / 10% | ₹100 / 250 / 500 | 10 / 15 / 20% | renews 30 / 50 / 70% at 5% | judgement within XO-19's range |
| two_wheeler | Two-wheeler insurance (savers with a vehicle) | 5 / 15 / 30% | ₹714 / 1,000 / 1,200 | 2.5 / 4.75 / 9.05% | renews 50 / 70 / 85% at the same rate | XO-18, XO-21, XO-22 |
| device | Mobile / device | 1 / 3 / 6% | ₹209 / 500 / 899 | 10 / 15 / 17.5% | no renewal | XO-34, XO-19 |
| shop | Shop insurance (fire and burglary) | 1 / 3 / 8% | ₹1,000 / 2,000 / 3,500 | 10 / 15 / 20% | renews 50 / 65 / 80% at 5% | judgement; IRDAI draft caps shopkeeper cover at 15%. **GAP:** no premium source |
| sip | Equity/hybrid SIP trail | 5 / 10 / 20% | ₹250 / 500 / 1,000 a month SIP | 0.5 / 0.75 / 0.9% of balance a year | SIP survives 50 / 65 / 80% a year | XO-06, XO-07, XO-08, XO-36 |
| choti | Choti SIP incentive | 4.5 / 9 / 18% | ₹500 once, paid at month 24 of the SIP if it survives | | survival to 24 months 15 / 25 / 40% | XO-01, XO-04, XO-05 |
| nps | NPS | 1 / 3 / 5% | ₹200 once | | | XO-16, XO-17 |
| gold | Digital gold | 3 / 8 / 15% | ₹100 / 300 / 600 a month bought | 2.4% of purchases | buying continues 50 / 65 / 80% a year | LEV-036 (Jar about 2.4%), LEV-037; SEBI caution SAV-11 |
| fd | FD via partner banks | 5 / 10 / 20% | FD ₹5,000 / 10,000 / 20,000 | 0.1 / 0.5 / 1% a year | | XO-37 |
| recharge | Mobile recharge | 10 / 25 / 50% (moved to us) | ₹2,600 a year | 1 / 2 / 3% | yearly while saving | XO-25, XO-33 |
| bills | Bill payments | 10 / 25 / 50% | 12 / 24 / 36 bills a year | ₹1 / 2 / 3 a bill | yearly while saving | XO-26 |
| loan_gold | Gold loan (other lenders) | 2 / 5 / 10% | ₹30,000 / 50,000 / 80,000 | 0.5 / 1 / 1.5% | | XL-28 (gold loans are the biggest category by count). **GAP:** payout |
| loan_cd | Consumer-durable loan | 0.5 / 2 / 5% | ₹10,000 / 20,000 / 30,000 | 1 / 2 / 3% | | XL-54 |
| loan_vehicle | Two-wheeler / e-rickshaw loan | 0.1 / 0.5 / 1% | ₹80,000 / 1.5 lakh / 6 lakh | 0.5 / 1 / 2% | | XL-54 |

**Shapes:** pert for every take-up, ticket and commission row, triangular where research gives only a flat range. "Take-up a year" = yearly hazard among proven savers still saving who don't hold the product.

**Renewals:**

- Renewals are counted only while he is still saving. (State this; it is conservative.)
- After he stops, a held policy lapses at its next renewal.

**Report and show:**

- the cross-sell money per proven saver a year, by product, as p10 / p50 / p90;
- the total, against the old ₹63 (XO-39).

**Note the IRDAI draft caps:** consultation comments close 25 Oct 2026 (REG-053..057). The high ends above stay within the draft caps.

## 2. Collection fees on high-DPD buckets

The lender pays us for what our agent collects on overdue loans. The agent's time is already in his salary.

| key | input | shape | low / likely / high | basis |
|---|---|---|---|---|
| rate | Loan interest rate | fixed | 26% a year | derived: the ₹10,073 EMI on ₹2.5 lakh over 36 months (agent3_funnel_inputs.csv). EMI = standard annuity |
| dpd30_rate | Running loans that fall 31–90 days overdue, a year | pert | 4% / 8% / 15% | judgement, anchored on CRIF 90+ 3.6% for loans over ₹50k (MAC-03) and Paytm's 83–90% early-bucket resolution (XB-07) |
| dpd30_emis | Overdue EMIs collected per case | pert | 1 / 2 / 3 EMIs | judgement |
| dpd30_resolve | Share of those cases our agent brings back | pert | 60% / 80% / 90% | XB-07 Paytm early-bucket resolution 83–90%; the operator: "our agent also helps us collect back" |
| dpd30_fee | Our fee on what is collected, 31–90 days | pert | 3% / 6% / 10% | judgement. **GAP:** no collection-agency rate card in research |
| loss | Money lost on loans, after recoveries | | unchanged (1.5 / 3 / 5%, Paytm worst case) | |
| recovered | Recovered after 90 days | pert | 30% / 35% / 50% | the low end = Paytm's 30–35% (XB-07); higher because the agent knows him (operator). Our judgement |
| rec_fee | Our fee on what is recovered after 90 days | pert | 8% / 12% / 18% | judgement; the NABARD tender of 5–7% for secured loans has no research row. **GAP** |

**Timing:**

- 31–90 day collections are paid in the month collected. Spread the cases evenly over a loan's life.
- 90+ recoveries are paid about 18 months after disbursal.

**Pilot:** in the pilot year almost no loans reach these buckets (loans start at month 7), so this is mostly year-2+ money. Say so.

## 3. Open choices (add to the operator's list)

1. **Research the GAPs?** The gaps are: a collection-agency rate card by DPD bucket, the family-health and shop-insurance premiums and commissions, and the gold-loan DSA payout. This would be a web search of up to about 8 queries, with the operator's approval.
2. **IRDAI caps:** model at today's rates or at the draft caps? The proposal above sits within the draft caps.

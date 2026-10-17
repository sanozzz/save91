# Cost and fee assumptions, checked against outside sources (2 Oct 2026)
Evidence: `research/tri_costs.csv`, rows TC-01..TC-41. "Same-origin" = repeats a source already in research/*.csv. Each block: our bear / base / bull, then the evidence, a verdict and a Monte Carlo (MC) distribution.

## Headline: collecting the money costs more than the gold margin earns on it
- One Rs 40 debit earns about **Rs 0.30**: half goes to gold at a 1.5% margin; the fund trail on the other half is negligible.
- The same debit costs Rs 0.94 if a 2% + GST fee applies (3x what it earns), **Rs 2 at our base (7x)**, and Rs 5.90 at the flat list price of Rs 5 + GST (20x).
- At base, the saving engine loses money on every debit. The model works only if lending pays for it. Weekly debits (`debits_scheduled` = 4) cut this cost about 5x.

## Payment costs
**cost_debit: Rs 5 / 2 / 0.5 per successful debit**
- **Evidence (two price shapes).** Flat: Cashfree and Zoho both list Rs 7.5 per mandate + **Rs 5 per execution under Rs 1,000**, before 18% GST (TC-02, TC-06). Percentage: about 2% of the debit, reported for Razorpay (unverified, TC-15/16) and shown by PhonePe PG as "1.99% FREE*" (TC-17); that is Rs 0.9-1.7 on Rs 40-50.
- Razorpay, Easebuzz, Setu, Decentro and Digio publish no Autopay price (TC-01, TC-04). The rails themselves cost Rs 0.15-0.4 (TC-08, TC-09).
- Zero MDR on Autopay is confirmed (TC-11), but payment companies still charge their own fee. BSE StAR MF puts the order fee on the fund house (TC-12), but Rs 20 daily fund orders sit under the Rs 100 daily minimum. Jar's accounts hint the gold provider may carry the payment cost (TC-10, unverified).
- **Verdict.** Base Rs 2 has no direct source; it needs percentage pricing or a negotiated rate. A new, low-volume app pays list price (Rs 5.90 with GST), so bear Rs 5 is too low. GST comes back as input credit only if our commissions are taxable; this needs checking.
- **MC:** lognormal, median 2.0, sigma 0.8 (p5 0.5, p95 7.5, mean 2.76). Better: one pricing switch shared with cost_failed, either flat Rs 5.90 or 2-3.4% of the debit.

**cost_failed: Rs 1 / 0.25 / 0 per failed debit**
- **Evidence.** No payment company says whether a failed execution is billed. With percentage pricing a failure costs about 0 (Razorpay reportedly passes bounces through at cost, TC-15). With a flat fee billed per attempt it costs Rs 5.90: Rs 8.85 per success at our 67% success rate, Rs 22.7 at 26%.
- Business declines average **about 74% of Autopay execution requests** (top 50 banks, mid-2025, TC-05). That count includes retries and stressed loan payments. The "8-15%" figure (TC-14) is an unsourced blog.
- **Verdict.** The base of 0.25 is a guess. The bigger risk is `debits_success` (not mine): our 67% is far above the roughly 26% ecosystem rate.
- **MC:** tied to the pricing switch. Percentage = 0. Flat = Rs 5.90 with probability 0.5, else 0.

**cost_notice: Rs 0.115 / 0 / 0 per scheduled debit**
- **Evidence.** Daily mandates are allowed (TC-03, REG-048). We trigger each pre-debit notice through the payment company at least 25 hours ahead; the payer's UPI app delivers it. Whether that call is billed: no data.
- **MC:** uniform 0 to 0.15.

## Savings revenue
**gold_margin: 1.0% / 1.5% / 2.4% of gold bought**
- **Evidence.** None independent. SafeGold's API docs confirm the distributor's margin is a slice of a markup shared with SafeGold, but give no rate (TC-13). The only number is still Jar's ~2.4%, from a case study (TC-19, same origin as LEV-036). Augmont (180+ partners) discloses nothing (TC-18). The 2-3% buy-sell spread must also pay for the provider, payments, trustee and custody.
- **Verdict.** Base is plausible but unproven; a newcomer has far less bargaining power than Jar.
- **MC:** triangular 0.5% / 1.25% / 2.4%.

**trail_liquid: 0.05% / 0.08% / 0.12% a year**
- **Evidence.** Base comes from the regular-minus-direct fee gap, an upper bound. Actually paid: 0.05% at 5 of 6 fund houses in 2021 tables (TC-21); 0.03-0.10% in 2025-26 readings, with ICICI at 0.075% then 0.025% (TC-22).
- **Verdict.** Base too high; our bear is the evidence's mode. Tiny money either way.
- **MC:** triangular 0.025% / 0.05% / 0.10%.

**fd_fee: 0.25% / 0.5% / 1.0% a year**
- **Evidence.** RBI bars banks from paying for deposits except to DSAs/DMAs, business correspondents and door-to-door agents (TC-24, RBI FAQ Q15). So it is a one-time sourcing fee. Stable Money's revenue implies at most 0.3-0.4% (TC-25). The 1% figure is anonymous (BM-03).
- **Verdict.** Base optimistic. Charge it only on new or rebooked FD money, and check that small finance banks can use the DSA exception.
- **MC:** triangular 0.1% / 0.3% / 0.6%.

## Insurance
- **ins_premium (Rs 1,500 / 3,000 / 5,000 a year).** IRDAI's own mass bundle, Bima Vistaar, costs **Rs 1,500** (TC-28). Accident-only cover costs Rs 20-100 (TC-27). Gig riders already get about Rs 2,100 of platform-paid cover plus PM-JAY (TC-26). Base too high, especially for the gig half. **MC:** triangular 500 / 1,500 / 3,500.
- **ins_comm_first (5% / 12% / 15%).** The draft caps are 15% for individual health sold by a distributor, 5% if sold with a loan, and 2.5% or 5% for group health (the two sources disagree) (TC-30, REG-054). Bima Vistaar pays 10% (TC-29). **MC:** triangular 5% / 10% / 15%.
- **ins_comm_renew (3% / 5% / 5%).** Draft cap 5%; 2.5% if sold with a loan. **MC:** triangular 2.5% / 4% / 5%.

## Lending
- **lsp_fee (1% / 1.5% / 3%).** Lead-based sourcing pays 1-3% (TC-34; different source from LEV-009, same range). Base supported; bull is optimistic for Rs 10-20k loans. **MC:** triangular 0.75% / 1.5% / 2.5%.
- **dlg_fee_uplift (3% / 5.5% / 7%).** No source splits fees with and without a guarantee. Moneyview's guarantee paid out 2.9-3.4% of the money lent under it each year (TC-41; the article's disbursal figure has a 10x units error). An uplift of 4-7% prices in about 3% losses. If our savers lose about 0.6%, lenders will bargain the uplift down, so base and our low-loss assumption contradict each other. **MC:** triangular 2.5% / 4.5% / 7%, correlated negatively with the loss rate.
- **secured_fee (2% flat).** A bank's whole margin on a loan against FD is 1-2% a year (0.5-1% over 6 months), with nil to 0.5% fees (TC-33). Loans against fund units start at Rs 25,000 with a Rs 999-2,000 minimum fee (TC-31, TC-32). No lender we found takes Rs 2-6k secured loans. Contradicted. **MC:** triangular 0.25% / 0.75% / 2%.

## Running costs per active saver per month
- **cost_support (Rs 8 / 5 / 3).** No direct data. A contact costs about Rs 50-150 (TC-38), so base needs at most ~5% of savers contacting us each month. Groww's non-tech operating cost is Rs 32 per active user (TC-37), an upper bound. **MC:** lognormal, median 6, p95 15.
- **cost_tech (Rs 6 / 4 / 2).** Jar's cloud bill is Rs 0.6-0.8 per *registered* user (TC-20). Groww spends Rs 28.6 per active user on tech plus transaction charges (TC-36). **MC:** triangular 2 / 4 / 10.
- **cost_fraud (0.2% / 0.1% / 0.05% of money saved).** 98.5% of fraud value is in payments above Rs 10,000; system-wide fraud is ~0.01% of value (TC-40, derived). Base is conservative. **MC:** triangular 0.02% / 0.05% / 0.2%.
- **kyc_cost (Rs 40).** Aadhaar e-KYC Rs 20 (2019 rate) + Rs 30-35 KYC registry + ~Rs 1 central KYC comes to Rs 25-60 (TC-35). **MC:** triangular 25 / 40 / 70.
- **mandate_cost (Rs 5).** List price Rs 7.5 + GST; Razorpay bundles it (TC-39). Over 20 million mandates are revoked a month (TC-05), so plan ~1.5 mandates per saver. **MC:** triangular 0 / 7.5 / 9.

**No evidence at all:** the distributor's gold margin from any filing; whether failed debits are billed; support cost per user at any Indian fintech; the split between guarantee and no-guarantee fees; any negotiated Autopay price.

# 24 Oct rebase: one fix list (numbers review + story review, merged by the lead)

The model changed after both reviews. **Rebuild from the tables. Never retype a number.** BRIEF.md is updated.

## A. Model changes already made (lead). Every table is regenerated.
1. **Serving now carries the plan's 10% contingency**, as the cost to win and company() do (`online_plan.ltv_parts`, `SERVE_CONTINGENCY`). Main case: **0.75× at 5 years (0.747), 1.32× at 8, payback month 75.**
2. **One retention definition everywhere.** The drop-off after a year moves on one line through Bachatt's range: 30% ↔ 2.5% a month, 40% ↔ 1.5%, 45% ↔ 1.0% (`online_plan.churn_for`). It applies to:
   - the ladder;
   - the upside lever;
   - LEVERS "24%", "45%" and "Credit-hungry".
3. **The ladder's low and high ends move retention only**, with the debt fee at the main case. They read **0.57× (30%) and 0.98× (40%)**, the same as the drivers table.
4. **3× is now reachable:** ₹194 a day, 44% still saving, 34% apply, 29% approved → EBITDA positive m55, $4.0M. All upside is 3.20×.
5. **The bridge has a new correction step after last week's 1.75×:** "Serving carries the 10% contingency, as the company model does (a correction)", −0.08. The last step now also names the debt fee and repeat approval.

**Current numbers** (from `ltv_saver_split.csv`, `ltv_odds_summary.csv`, `ltv_ladder.csv`, `ltv_upside_levers.csv`, `ltv_bridge.csv`):
- **Main case, 5 years:** fund fees ₹417, loans ₹125, cards ₹18, serving −₹190, net ₹370 = 0.75×.
- **Main case, 8 years:** ₹706 + ₹155 + ₹18 − ₹225 = ₹654 = 1.32×.
- **Cross-sell revenue** (loans + cards): ₹143 / ₹173 = 0.29× / 0.35× of the cost to win, before serving. After serving it is **−0.10×** at both horizons.
- **Monte Carlo:**
  - 5 years: 0.60 / 0.75 / 0.93 (P10 / P50 / P90); 0.3% of draws reach 1×.
  - 8 years: 1.00 / 1.32 / 1.76; 90% reach 1×.
  - Payback: month 64 / 75 / not by 96.
  - The company is unchanged: never EBITDA-positive by m96; $9.3M+ (8.8–9.8 in 8 of 10 draws); −₹80 Cr over 8 years.
- **One lever alone gets to 1×:** ₹130 a day, or 40.5% still saving. No single loan lever does. Apply 35% alone gives 0.92×; approval 30% alone gives 0.80×.
- **Ladder:**

| Rung | Daily | Still saving | Apply | Approved | LTV/CAC | Company |
|---|---|---|---|---|---|---|
| 1× | ₹116 | 36% | 22% | 22% | 1.00× | still not profitable by m96, $8.1M+ |
| 2× | ₹161 | 41% | 29% | 26% | 2.00× | m68, $5.1M |
| 3× | ₹194 | 44% | 34% | 29% | 3.00× | m55, $4.0M, +₹33 Cr over 8y |

## B. Every document (LTV deck, business case, seed plan, v4 deck)

1. **The cross-sell answer.** Lead with it, in rupees.
   - **Wording:** "Cross-selling alone (loans and cards): ₹143 per saver in 5 years, ₹173 in 8. That is 0.29× and 0.35× of the ₹495 it costs to win a saver, and less than the ₹190 / ₹225 it costs to serve them, so on its own it never pays back (−0.10× after serving). Insurance, recharge, bills, FD and NPS are not counted."
   - Then: "With fund fees, 0.75× in 5 years and 1.32× in 8; pays back in month 75."
   - LTV/CAC everywhere else is net of serving. **Never put the 0.29× revenue ratio beside net ratios without saying it's before serving.**
2. **Cost to win: never call it "measured".**
   - **Wording:** "₹450 at scale (the founders' figure; they call it 'fairly sorted') plus the 10% contingency = ₹495. The seed budgets ₹600 while the brand is new, and measures it."
   - Show once: at ₹600 (₹660 with contingency) a saver is about 0.56× / 0.99×. The company needs $12.0M+ (lever row "Cost to win Rs 600").
3. **Unconfirmed inputs: say so on the cover.**
   - **Wording:** "Assumes debits cost us ₹0 and a 0.75% equity fund fee, both still to be confirmed in writing (₹2 a weekly debit, or a 0.5% fee, would cut a saver to about [read the lever])."
   - On the bridge, mark the debit step "to confirm".
4. **The fund fee and the hybrid fund.**
   - The model uses 80% equity at 0.75% + 20% debt at ~0.22% = **0.64% blended**.
   - If the ₹100 goes into one hybrid fund (daily minimums are ~₹100 a scheme), that fund's distributor fee must be about 0.64% or more.
   - **Fact 4 becomes:** "the fee on the fund the ₹100 goes into, in writing (0.64% blended or better)."
5. **₹100 a day.**
   - **Wording:** "₹100 is our product's floor; Bachatt's average is unknown, and its own minimums are lower (₹51/₹101 a day; ₹20 for its liquid fund)."
   - Not "so the main case is cautious".
6. **The 20% approval rate.**
   - **Wording:** "founders' market figure, between 11% (an app lender's new applicants, XL-41) and 25% (our own past data, XF-24)."
   - Disclose that gold loans are approved at 70% and home/property at 45%.
7. **Uncertainty wording.**
   - Write "0.3% of the 1,000 draws, holding everything else at the main case", not a "chance".
   - Never write "everything else is market or measured". Instead: "everything else is fixed by the founders (market figures, Bachatt, or our judgement)".
   - Say "8 in 10 draws" for any P10–P90 range.
8. **Money needed.**
   - Always "+" (at least) where the company is still losing money at month 96.
   - Footnote once: "if run on, the cash hole bottoms around year 12 at about $10.6M."
   - Call the ₹5 crore a "cash buffer", not a floor.
   - State ₹95 = $1. Explain money needed = the seed + the deepest cash hole (fees arrive 2 months late) + the ₹5 crore buffer.
9. **"45% still saving" is one definition everywhere.** It includes the drop-off falling to 1.0% a month, from the lever row. Same for 24% and credit-hungry.
10. **What cross-selling CAN do.** "All three loan numbers at our old targets together give about [read 'Loan funnel at our old targets' in ltv_main_levers.csv / online_ltv_levers.csv] and bring profit in month [read]." Say why: loan fees arrive early, fund fees build slowly.
11. **Plain words at first use.** Gloss:
    - LTV/CAC: "what a saver brings in over 5 or 8 years, less the cost of serving them, divided by what it costs to win them";
    - EBITDA: "operating profit before interest, tax and depreciation";
    - KYC'd, SIP, mandate, the Monte Carlo ("we ran the model 1,000 times, picking retention and the debt fund's fee at random within their ranges"), median, percentile.
12. **Smaller corrections:**
    - Support is ₹5 a month per saver still saving. Only the ₹4 tech scales with the 1.06.
    - 1.06 is a value weight. About 2.5 KYC'd people come with each saver, but non-savers fade within ~3 months.
    - Cards: "3% of savers still saving at month 7 take one", which is ₹18 a saver won, not ₹30.
    - Not counted: loans against savings (10% of applications); a saver who stops withdraws everything, so fund fees stop. Small loans outside the apply funnel: consumer-durable (₹20k) and two-wheeler.

## C. LTV_CAC_simple.pdf (the meeting deck)
1. **Restructure to ~6 main pages plus an appendix:**
   1. Cover = the answer (B1, B3).
   2. Where the value comes from: ONE waterfall page merging old p2 and p3, cross-sell bracketed and labelled "₹143, less than serving ₹190".
   3. What changed (bridge).
   4. What's uncertain (odds).
   5. What it takes (one lever at a time plus the ladder on one page, or two).
   6. The four facts.

   Appendix: the inputs, the company. Fewer words per page; the founders want "pointed".
2. **Bridge:** title "From the 23 October 1.75× to 0.75× today". Compute step labels from the ROUNDED column so they add up. Fix the garbled sub-lines. Keep the 1× line off the labels.
3. **Ladder page:** show the main case with its 30–40% band (0.57–0.98×) as one band, then the 1×, 2× and 3× rows. Delete the "14% of the way" sentence.
4. **Four facts:** use B4 for fact 4. Add the missing main-case circle on fact 2. Don't colour the ₹130 break-even dot red.
5. **Chart nits:**
   - The dashed ₹495 line strikes through a label.
   - Histograms need a y-axis label: "share of 1,000 draws".

## D. Online_business_case.pdf
1. **Drop the $1B page** from this document. Keep `p_upside` working for v4, but fix its wording:
   - "on both yardsticks";
   - the capture row's "EBITDA positive month 96" is sign-ups stopping (year-8 EBITDA −₹140 Cr);
   - value labels go at the bar ends.
2. **p2:**
   - Retitle the card "Fund fees are 74% of revenue" to match its content.
   - Cost-to-win bar not teal.
   - Label the curve's low point.
   - Use the same serving colour as the LTV deck.
3. **p6 headline:** credit-hungry also brings profit; say so accurately.
4. **Same section names as the LTV deck:** "WHAT'S UNCERTAIN" (not "THE ODDS"); "THE COMPANY" (not "THE FINANCIALS").
5. **Next round:** read it from the ladder (main case $9.3M+; 2× about $5.1M less the seed). Don't use the old $8.8M / $4.5M unless recomputed.

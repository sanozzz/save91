# Company model: fix round 1 (review findings + operator decisions, 17 Oct 2026)

Apply all of these, re-run `company_model.py` and `company_mc.py`, and re-run the checks.

## Operator decisions (taps)

1. **Scale costs ("Add as proposed"):**
   - Risk and fraud lead at ₹1.5 lakh a month, from the month the fleet reaches 100 agents.
   - Cash reconciliation executives at ₹35,000 a month, 1 per 50 agents, rounded up from the first agent.
   - HR/recruiting executives at ₹50,000 a month, 1 per 100 agents, rounded up from the first agent.
   - Customer support lead at ₹60,000 a month, from the month the company has 50,000 savers.
   - All in central costs, with +10% statutory and 7% raises.
   - **Cash cover** = the larger of ₹1,000 per agent a month or 0.015% of the cash collected that month, in field servicing (CM2).
2. **Treasury: include interest on cash at 5.5% a year.**
   - Monthly, on the opening cash balance.
   - Shown below EBITDA as "Interest on cash (other income)".
   - It is taxable within the 25% rule, and it adds to the cash flow.

## Lead decisions (on review findings)

3. **One-time licences:** ₹7.5 lakh, the itemised sum (setup ₹1 lakh, ARN/NISM ₹0.5 lakh, legal opinion ₹6 lakh). Integrations stay ₹15 lakh in the app, capitalised.
4. **Agent pay:** agent salary also gets the 7% yearly raise, by company year.
5. **Sign-up decline runs on the BOOK's age, not the agent's tenure.** The decline reflects how busy the book keeps him. A replacement agent inherits the book's age for the decline, but restarts the ramp (3 months).
6. **MC:** add one common sign-up factor per draw (market-level `signups_run` scaling all agents in that draw), on top of agent-level variation. Quote break-even probability as "≈X% ± 2pp".
7. **Series A timing and size:**
   - Keep ₹75 crore at m18 as the base.
   - Add to `company_m18.csv` and `company_mc_summary.csv`:
     - the month the seed alone runs out;
     - "the A must close by month N";
     - slip cases with the A at m21 and m24: lowest cash, and whether it goes below 0;
     - **the smallest Series A** at m18 that keeps cash ≥ ₹5 crore through m60 (search it).
8. **The growth J-curve (story):** add `tables/company_fleet_scenarios.csv` with yearly EBITDA, cash at m60, savers at m60, and the EBITDA break-even month for three scenarios:
   - (a) the base 60 → 300;
   - (b) hiring frozen at 60 after m18;
   - (c) hiring frozen at 150 after m36.
9. **Labels:** label the two lowest-cash figures clearly ("seed only, through m18" vs "with the Series A, through m60").
10. **Ops executives scale:** +1 per 50 agents beyond 60, as built. Write the rule into the README of the tables.

## Report (under 250 words)

- The new yearly ladder: revenue, CM1, CM2, CM3, EBITDA, interest, PAT, closing cash.
- Headcount.
- The seed run-out month.
- The smallest Series A.
- The three fleet scenarios.
- The MC summary.
- Checks passing.

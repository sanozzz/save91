# Round 7: agent pay = salary + a share of balance (operator, 16 Oct 2026)

## Operator answers (verbatim)

> "I might need to have the agent on salary plus 0.25% of balance initially. Afterwards when balances and customers are with us and growth isnt a problem, i can have less incentive"

> "so after 5 years it will reduce to 0.1% in the company. for next 5 years 0.25% in growht phase"

## The input

- New fixed decision `agent_balance_pay`:
  - 0.25% a year of the average balance his savers hold, paid monthly (rate ÷ 12 × that month's balance), for company months 1–60 (the growth phase);
  - 0.10% a year from month 61.
- The ₹20,000 salary is unchanged.
- Confidence: "Your number".
- In the engine, add it as a cost line `cost_incentive` (keep the name stable) and include it in cost_total.
- The lead's quick check (`model/incentive_sweep.py` → `tables/cohort_incentive_sweep.csv`, at 30 sign-ups): P(cum P&L at 60 months > 0) 83% → 62%; median P&L at 60 months ₹4.8 lakh → ₹1.4 lakh; payback month 47 → 50; incentive about ₹3.3 lakh per agent over 5 years (₹1,700 a month at month 12, ₹11,800 at month 60).

## Deck

- Page 5 (fleet + app): the agent pay line becomes "₹20,000 a month + 0.25% of his savers' balance while we grow (0.10% after year 5)".
- A new appendix page "Paying the agent": the five pays from `tables/cohort_incentive_sweep.csv` as bars of P(5-year P&L > 0) and median 5-year P&L, with the base (0.25% for all 5 years) marked. Add one line: "From year 6, 0.10% instead of 0.25% saves about ₹7,000 a month per agent", computed from the month-60 incentive at the two rates.
- The bridge: add a step "agent pay: + 0.25% of balance".

# Brief: maximum growth with year-5 PAT ≥ 0, and the path to $100M ARR (operator, 17 Oct 2026)

## Operator (verbatim)

> "cant we scale more faster and figure what we need to raise to be PAT Positive in 5th year with maximum growth. It might mean different seed + series A raise."

> "What does it takes for us to reach $100mil revenue" / "$100 mil revenue ARR ...how many users"

All market inputs stay at the agreed likely values. Pay is ₹20,000 + 0.25% of balance, capped at ₹10,000 (rising 7% a year). The cost rules are as built: central team scaling, city rules, the scale functions, contingency, tax, 5.5% interest on cash, 2-month commission lag.

## Part A: maximum growth with year-5 PAT ≥ 0 (60 months)

**Search over:**
- agents at m18 ∈ {80, 100, 120, 150, 200};
- hiring after m18: h ∈ {0, 5, 10, 15, 20, 30} agents a month, with an optional faster rate once EBITDA > 0;
- central team: as built (scales with the fleet).

**Funding is sized by the model, not fixed:**
- seed at m0 = the smallest that keeps cash ≥ ₹5 crore until the Series A, rounded up to ₹1 crore;
- the Series A closes at m18 (also report m15 and m21 timing), sized the same way: cash ≥ ₹5 crore through m60, rounded up to ₹5 crore;
- the interest on that cash follows. Note the circularity (more cash means more interest, which means higher PAT) and solve it by iterating.

**Constraint:** year-5 PAT ≥ 0. **Also report:** year-5 EBITDA, and whether PAT is positive only because of interest.

**Objective:** maximise active savers at m60. Tie-break on year-5 revenue.

**Outputs:**
- `tables/growth_search.csv` (every plan);
- `tables/growth_frontier.csv`: the plans with PAT ≥ 0, sorted by savers, plus the same frontier with EBITDA ≥ 0 in year 5, if any;
- a recommended max-growth plan (`tables/growth_recommended_*.csv`, the same format as the company base outputs);
- a Monte Carlo for it: P(year-5 PAT ≥ 0), P(cash ≥ 0 through m60).

## Part B: the path to $100M ARR

- **The target.** $100M ARR = ₹1,000 crore a year at ₹100/$ (the operator's rate for the seed). Also show ₹850 crore (₹85/$). "ARR" = 12 × monthly revenue.
- **Steady-state arithmetic** (the lead's quick view, to be checked and refined):
  - a mature agent at tenure 60 has about 2,240 savers;
  - about ₹890 per saver a year;
  - AUM about ₹61,000 per saver.
  - So about 1.12 crore active savers, about 5,000 mature agents, and about ₹68,000 crore AUM.
- **Extend the company model to 120 months (10 years).**
  - Extend cohort_engine AGES and MONTHS as needed, with options defaulting to 60 and identical outputs.
  - Beyond month 60, hold the growth factors (take-up and approval growth caps, the fee multiplier at 1.5×) at their month-60 values unless the caps already bind. Document it.
- **Search hiring ramps** that reach ₹1,000 crore ARR by year 7, year 8 and year 10:
  - e.g. a fleet path to N agents, with hiring rate steps after EBITDA turns positive;
  - per path, the minimum total equity raised (staged rounds sized by the model at m0, m18, m36 and m60 to keep cash ≥ ₹5 crore);
  - and the month EBITDA turns positive.
- **For each target year, report:**
  - agents;
  - active savers (users);
  - AUM;
  - money lent a year (personal and housing);
  - cities, at one per 50 agents;
  - central headcount;
  - year-by-year revenue, EBITDA and PAT;
  - the total raised and when;
  - peak burn.
- **Outputs:**
  - `tables/arr100m_paths.csv`;
  - `tables/arr100m_recommended_yearly.csv` (years 1–10);
  - `tables/arr100m_steady_state.csv` (the users / agents / AUM / lending arithmetic).

## Report (under 350 words)

1. **Part A:** the recommended max-growth plan (fleet path, seed, Series A, year 1–5 ladder, savers at m60, EBITDA vs PAT) and the frontier's top 5.
2. **Part B:**
   - users, agents and AUM at $100M ARR;
   - the fastest feasible year;
   - total funding;
   - the year-by-year table for the recommended path.

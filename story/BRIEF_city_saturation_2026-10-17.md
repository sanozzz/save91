# Brief: marry the model with the real world. Cities have limits (operator, 17 Oct 2026)

## Operator (verbatim)

> "So we now need to marry the model with the real world. We can't outgrow a city. I believe we have some 30cr people that we have in this segment"

**Taps:**
- **TAM:** urban self-employed (recommended).
- **City cap:** 20%.
- **City data:** estimate (rank-size).

## The pool

**National addressable pool:** URBAN self-employed, own-account workers + employers + helpers.

| | Value | Basis |
|---|---|---|
| Pool size | pert 6.5 / **7.0** / 7.7 crore | NG-002: 40.4% of urban workers are self-employed, 34.0% own-account or employer |
| Urban workers | about 19 crore | lead's estimate: urban population about 52 crore × work participation about 37% |
| The operator's 30 crore | context only | SEG-02: e-Shram 31.9 crore unorganised workers; NG-003: 34.6 crore self-employed incl. rural. Show it on the page. |

## Cities (rank-size estimate; label it "estimate, not census")

- **Urban centres:** about 4,000 towns. A fleet serves only cities with population ≥ 1 lakh (about 500 "Class I" towns).
- **Calibration:**
  - Rank 1 = NCR, about 6.3% of urban India's population (NCR about 3.3 crore of about 52 crore urban). So NCR addressable ≈ 6.3% × 7 crore ≈ **44 lakh**.
  - Fit the rank-size exponent q so the sum over all about 4,000 towns = 7 crore.
  - Report q and the share of the pool in the top 50, 150 and 500 cities.
- **Names** for the top 15, in this order:
  1. NCR
  2. Mumbai MMR
  3. Kolkata
  4. Bengaluru
  5. Chennai
  6. Hyderabad
  7. Ahmedabad
  8. Pune
  9. Surat
  10. Jaipur
  11. Lucknow
  12. Kanpur
  13. Nagpur
  14. Indore
  15. Patna

  Then "City 16", "City 17" and so on. The sizes come from the curve, not from data.

## Saturation mechanics (company model)

- **Ceiling:** each city's cumulative sign-ups ≤ **20%** of its addressable pool.
- **Agent productivity in a city:** sign-ups a month = the agent's own level (with the decline on book age) × max(0, 1 − penetration / 20%).
  - Penetration = cumulative sign-ups ÷ addressable.
  - This is a straight-line slowdown to zero at the cap (judgement). Show a softer alternative (1 − (pen/cap)²) as a sensitivity.
- **Opening order:** cities open in rank order.
- **Allocating hires:** each new hire goes to the open city with the most remaining headroom per agent. Remaining headroom = 20% × addressable − cumulative sign-ups.
- **Opening the next city:** when no open city has more than X remaining sign-ups per agent. Choose X so an agent's 5-year sign-ups (about 5,000) fit: open the next city when headroom per agent < 5,000.
- **City costs:** launch ₹3 lakh, a city office, and a city manager per city, as before.

## Runs

1. **The current unicorn plan with saturation switched on**, and nothing else changed: what breaks? Per year:
   - sign-ups, active savers, AUM, ARR;
   - cities open;
   - national penetration;
   - NCR penetration;
   - EBITDA;
   - the m60 lens check.
2. **Re-plan under saturation:** the least-equity plan that is a unicorn on paper at m60 (both lenses), if feasible. The search can open cities faster, up to 500 Class I cities, and size the fleet to the headroom. If no plan is feasible:
   - (a) the best AUM-lens-only unicorn;
   - (b) the highest valuation reachable at m60 on each lens;
   - (c) the month a unicorn on paper becomes reachable (extend to m96).
   Re-price the rounds with the same rules.
3. **NCR alone** (the operator's question), in the unicorn plan with saturation:
   - agents in NCR by year;
   - sign-ups a year;
   - cumulative sign-ups;
   - active savers;
   - penetration by year;
   - when NCR hits its cap.
4. **Profitable-by-year-5 plan** (the 200-agent plan) with saturation: does it still hold?

## Outputs

- `tables/cities.csv`: rank, name, addressable, cap.
- `tables/sat_*.csv`, for the runs above:
  - `sat_unicorn_asis_yearly.csv`
  - `sat_unicorn_replan_yearly.csv` and `sat_unicorn_replan_rounds.csv`
  - `sat_ncr.csv`
  - `sat_profitable_yearly.csv`
  - `sat_city_penetration.csv` (top 30 cities by year)
- **Checks:** sign-ups never exceed the cap; agents are allocated; the sums reconcile.

Keep all existing tables unchanged (options default off).

## Report (under 350 words)

- q and the top-150 share.
- What breaks in run 1.
- The re-plan: feasible or not; the path; the rounds; founders %; the yearly table; the m60 lenses.
- NCR by year.
- The profitable plan under saturation.

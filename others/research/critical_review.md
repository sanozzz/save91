# Critical review of the model (2 Oct 2026)

What the model gets wrong, hides or cannot tell, separate from whether each input is right
(that is the triangulation in tri_costs.csv / tri_behaviour.csv). Numbers: engine.py on the
inputs as of 2 Oct 2026 (loan ladder, gold at half of savings), middle case unless stated.

## 1. The headline ratio misleads when a saver loses money
LTV ÷ CAC is negative in the middle case (−1.2). A cheaper CAC makes a negative ratio MORE
negative (cac_mult at its best value moves the ratio from −0.83 to −1.44), and longer retention
makes it worse, because each extra month of an active saver loses money. From here on the
odds are stated on NET value per activated saver = LTV − CAC (middle case −₹560), and on the
probability that LTV ÷ CAC reaches 3.

## 2. No single input rescues the middle case
- Free debits (₹0, no notice or failure cost): net −₹218 a saver.
- Free debits and free support and tech: net −₹149.
- Zero acquisition cost: the saver still loses ₹304 over five years (LTV is negative).
- One-at-a-time search over a wide range (sens_oat.csv): no input breaks even on its own.

## 3. The best case is a corner, not a scenario
Moving inputs to their best-case values one at a time, choosing the most helpful each step,
the average saver turns profitable only after TEN of them: debit cost, daily amount, gold
margin, acquisition cost, insurance premium, two-year retention, debits per month, insurance
take-up, first-year insurance commission, one-year retention. The best case needs all of
these at once; a Monte Carlo that samples each around its middle value almost never lands
there (see mc_summary.csv).

## 4. Structure the inputs cannot fix
- **Year-10 revenue is mostly an input.** The growth plan (25,000 new savers in year 1 to 7M a
  year by year 10, inputs_path.csv) is typed in, not derived from CAC budgets, channel capacity
  or market share. The Monte Carlo varies unit economics only; the growth plan is held fixed.
- **Fixed costs are not stress-tested.** ₹6 crore in year 1 rising to ₹145 crore by year 10.
- **Secured-loan demand is assumed, not shown.** A saver whose liquid fund can be redeemed
  instantly has little reason to borrow ₹1,400 against it. The secured rungs work like a
  credit-builder loan; demand for those in India is unproven.
- **Loan sizes use the average saver's balance.** Borrowers may hold more than average, which
  would make secured loans larger than modelled (this one runs in the model's disfavour).
- **Debit cost is per successful debit.** If a payment company bills per presentation,
  including failures, the cost per rupee saved is higher than modelled.
- **Gold rules are a scenario, not a distribution.** If digital gold becomes a regulated
  security or its margin is capped, 45% of five-year revenue is at stake; this is outside the
  Monte Carlo.
- **Founder views are not independent evidence.** Retention (20% at a year), the loan ladder
  and the secured-loan fee are the founder's judgement; the Monte Carlo treats them as the
  middle of a range, not as facts.
- **Independence understates the tails.** Savers who stay probably also save more and buy
  more. The 'correlated' variant links these through one engagement factor (rho 0.5).

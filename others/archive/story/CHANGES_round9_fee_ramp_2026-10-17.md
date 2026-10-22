# Round 9: origination fee starts at a DSA's rate and rises to 1.5× over 5 years (operator, 17 Oct 2026)

## Operator (verbatim)

> "One of the assumptions I dont like personally is the 1.5x DSA. I think we are like a DSA initially. Over time, we can charge more but initially we start like a DSA and then move that multiplier to 1.5x over few years...lets say 5 years...slowly..."

## Inputs

| key | change | shape and values | confidence and basis |
|---|---|---|---|
| `fee` | REDEFINED as a DSA's rate on personal loans (the starting fee) | pert 1.0% / **1.75%** / 2.5% | Industry guide, not verified: XL-13 personal-loan DSA 1–2.5%; LEV-009 |
| `fee_mult_start` | NEW | fixed 1.0 | Your number |
| `fee_mult_end` | NEW: reached at company month 60 | fixed 1.5 | Your number |

- **The fee in month t** = fee × (1 + (fee_mult_end − 1) × (t − 1) / 59), in calendar months. Use it for first loans, repeat loans and top-ups.
- **Housing loans (loan_home, loan_lap):** unchanged; already at DSA rates.
- **Taken-back fees:** as before.

## Outputs

- Re-run the deterministic run, the MC, the drivers, must-be-true and the bridge (add a step "fee starts at a DSA's rate, ramps to 1.5×").
- The lead re-runs the two sweeps.
- **Deck:** the A3 fee page shows the ramp (1.75% → 2.6% by year 5).
- **Google Sheet:** fee and multiplier inputs; the fee by month in Monthly.
- **START_HERE.md** is updated.

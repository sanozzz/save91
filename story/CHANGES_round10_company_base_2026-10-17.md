# Round 10: the company base plan and capped agent pay (operator, 17 Oct 2026)

## Operator decisions (verbatim, plus taps)

- **Profitability:** "I want to make the company profitable by 3rd - 4th year... I dont want this to be a loss making company."
- **Plan search result:** under the agreed market assumptions, no plan breaks even by m48. The operator chose **"Accept year 5"**: keep the closest plan.
- **Pay:** "salary only team is tough. i think some incentives have to be there over 20k salary". By tap, the only acceptable incentive is **0.25% of balance, capped at ₹10,000 a month per agent**.

## The company base (replaces the 60 → 300 base)

| Item | Base |
|---|---|
| Fleet | grow to **80 agents by m18** (the plan's path to m18), then **hire only to replace leavers** (30% a year) |
| Agent pay | ₹20,000 + 0.25% a year of his savers' balance, **capped at ₹10,000 a month per agent**; the salary and the cap rise 7% a year |
| Central team | the lean hold, about 15, as in the recommended plan (scale-per-agent executives as built) |
| UPI | 30% by m12 (agreed; no push) |
| Seed | ₹10 crore at m0 |
| Series A | **₹20 crore at m18** (the minimum to keep cash ≥ ₹5 crore through m60 is about ₹19 crore, and it must close by m20) |
| Everything else | as agreed |

**Keep the old 60 → 300 plan as scenario "growth plan"** in the outputs, for comparison.

## Agent unit (`cohort_engine`)

- Add the capped incentive to the agent-unit base: new agreed key `incentive_cap` = ₹10,000 a month, fixed, "Your number".
- Re-run cohort_engine (deterministic + bridge, with a step "incentive capped at ₹10,000") and cohort_mc.
- The lead re-runs the sweeps, with capped pay rows in the incentive sweep.

## Outputs

- `company_*` base tables: the new base; the yearly ladder, cash flow, headcount, m18, MC, break-even customers.
- `company_fleet_scenarios.csv`: base vs growth plan vs frozen-at-60.
- **The story line for the deck:**
  - "Break-even needs about 2.2 lakh active savers."
  - "Each saver earns about ₹17.50 a month after serving and acquiring him."
  - "The central team costs about ₹38 lakh a month."
  - "With take-up 40% higher, break-even moves to month 48."
  Recompute every one of these after the changes; they will move.

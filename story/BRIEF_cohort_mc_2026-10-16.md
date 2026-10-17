# Brief: monthly cohort model with a Monte Carlo around every input

## What the operator said (16 Oct 2026, verbatim)

> "So let's build a model of monthly cohort, their retention and saving rate and every detail and model it like that"

> "So cohort level modeling needs to happen with Monte Carlo around input assumptions."

> "we need to first agree on assumptions first - how many loans, everything is a distribution"

> "our worst case would be paytm default rates because of two things - 1. these are genuine self selected savers 2. and our agent also helps us collect back"

Project root: `~/Desktop/Random/savings-first-deck/` (not a git repo). Python: `~/.cortado-venv311/bin/python`, which has numpy, scipy and openpyxl.

**The inputs:** read `story/COHORT_INPUTS_2026-10-16.md` (the full input list, curve shapes, mechanics and the legacy switch) and `story/BRIEF_distributions_2026-10-16.md`.

- Another agent is building `tables/dist_proposal_v1.csv` with every input's distribution. It has been told to include every key in COHORT_INPUTS.
- Until that file exists with all keys, test with a temporary dict of likely values taken from COHORT_INPUTS.
- The final Monte Carlo must read its distributions from `tables/dist_proposal_v1.csv` by `key`, using `shape`, `low`, `likely` and `high`. Write the sampler so that swapping in an agreed file later (`dist_agreed_v1.csv`) is a one-line change.

**No deck work.** Do not touch existing scripts, tables or PDFs.

## Deliverables

### 1. `model/cohort_engine.py`: one agent, 60 calendar months, one cohort per month

- **Vectorised numpy.** The core is an **age profile per sign-up**: arrays over ages 1..60 for each line below. A calendar month t total is the sum over cohorts c ≤ t of signups[c] × profile[t − c + 1]. Sign-ups vary by month because of the ramp.
- **Lines per age:**
  - still saving;
  - stopped this month;
  - deposits;
  - balance (term cycle, rollover at term end, mid-term withdrawals, full withdrawal on stopping);
  - UPI share;
  - cash visits needed;
  - proven savers;
  - savers with a loan running;
  - loan applications;
  - loans made (first / repeat);
  - EMIs collected;
  - cards issued;
  - revenue lines: fund commission, origination fees net of taken back, recovery fees (18-month lag), collection fees (default 0), cards, insurance and other;
  - costs: KYC per sign-up.
- **Calendar-month lines:** salary, extra capacity cost (when cash visits a day exceed capacity, pro-rata), support cost (0, shown).
- **Running loans:** a borrower's loan runs `tenure` months, and he keeps paying even if he stops saving. While it runs he does not apply. After it ends, a saver still saving can re-apply at the repeat approval rate.
  - Track this with a state split inside the age profile: active savers with no loan / with a first loan running / repaid and eligible for a repeat.
  - Approximate if needed, but document how.
- **Outputs for one input set:**
  - monthly P&L;
  - NPV at 36 and 60 months, at 20% a year discounted monthly;
  - cumulative cash and the payback month;
  - value per sign-up (5-year, discounted);
  - pilot year 1 cash;
  - savers, visits a day and UPI share by month.
- **The `legacy=True` switch** must reproduce `tables/xs_npv_v2.csv` within ±1% at retention 30 / 40 / 55 / 70 (see COHORT_INPUTS §9). **Do this first.** It proves the engine before the new detail goes in.

### 2. `model/cohort_mc.py`: Monte Carlo, 10,000 draws, fixed seed

- Sample every input from its distribution: triangular, PERT (beta-PERT with λ = 4), lognormal (low = P5, likely = median, high = P95), beta, fixed.
- Enforce r12 < r3 by resampling.
- **Optional correlation**, a switch defaulting to OFF (an open operator choice): "bad years" make approvals and losses move together, via a Gaussian copula with ρ = −0.5 between approved_first/approved_repeat and loss.
- **Outputs:**
  - `tables/cohort_mc_draws.csv`: one row per draw, with every input and the key outputs;
  - `tables/cohort_mc_summary.csv`, covering:
    - NPV at 36 and 60 months (p5, p10, p25, p50, p75, p90, p95, mean);
    - P(NPV > 0) at 36 and 60 months;
    - payback month (p10 / p50 / p90, and the share that never pays back within 60);
    - value per sign-up;
    - year-1 pilot cash;
    - loans per 100 proven savers a year;
    - the UPI share needed and the extra capacity cost;
  - `tables/cohort_mc_drivers.csv`: the Spearman rank correlation of each input with NPV60, plus each input's "swing": the mean NPV60 in the input's top decile minus its bottom decile;
  - `tables/cohort_mc_by_r12.csv`: P(NPV60 > 0) and median NPV60 by r12 band (25–30, 30–35, … 70–75). This answers "what retention do we need" without fixing the other inputs.
- **Check convergence:** the p50 and P(NPV > 0) at 5,000 vs 10,000 draws must agree within 1 point.

### 3. `Cohort_model.xlsx`: the same deterministic model, with live formulas, for the operator to open and change

Follow the xlsx skill rules:

- **Inputs sheet:** blue inputs with a likely value per input. Each input has a cell comment carrying its source, and the low/high are shown alongside.
- **Retention curve sheet:** ages 1–60, built from r3, r12 and churn_late by formula.
- **Age profile sheet:** one column per line above, ages 1–60, all formulas referencing the Inputs sheet.
- **Monthly sheet:** months 1–60, totals built from the age profile × the sign-ups vector (SUMPRODUCT with INDEX/OFFSET, or a cohort triangle sheet if clearer). Include the P&L lines, the discount factor and cumulative NPV.
- **Cohort triangle sheet:** active savers by cohort (rows) × calendar month (columns), so the operator can SEE the cohorts.
- **Summary sheet:**
  - NPV at 36 and 60 months, the payback month and value per sign-up, all as formulas;
  - a clearly labelled block "Monte Carlo results (pasted from model/cohort_mc.py, 10,000 draws, date)" holding values only, with a note saying so.
- **Recalc:** run the skill's `scripts/recalc.py` (skill dir: `/Users/sandeeparora/.claude/skills/synced/70057717-e918-466d-92bc-da9297729c0d_77fa8776-f34a-49f5-8921-6e9ec7952d56/xlsx`). There must be zero formula errors.
- **Reconcile:** at the likely values, the Excel NPV at 36 and 60 months must match `cohort_engine.py` within 0.5%. Write the check to `tables/cohort_xlsx_check.csv`.

## Rules

- Tables first: every output is a CSV a script writes.
- Plain words in column names where a person reads them (the xlsx and the summary CSV). Code keys are fine in the draws CSV.
- No web research.
- Never name Bueno or BetterPlace. No customer names.
- Scratch: `$S/cohort/` only, where `$S=/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad`.

## Report back (under 500 words)

1. The legacy regression result: 4 retention levels × 2 horizons, cohort engine vs v2.
2. The deterministic result at the likely values: NPV at 36 and 60 months, payback month, value per sign-up, year-1 cash, peak cash visits a day, UPI share, extra capacity cost.
3. The Monte Carlo result:
   - P(NPV60 > 0) and P(NPV36 > 0);
   - NPV60 at p10 / p50 / p90;
   - the top 8 drivers;
   - P(NPV60 > 0) by r12 band.
4. The Excel vs Python check.
5. Every modelling approximation you made, especially for running loans and repeats.
6. Paths.

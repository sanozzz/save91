# Adversarial review: the cohort Monte Carlo says one agent pays back in about 99% of futures. Try to break it.

You are a fresh, sceptical reviewer. You did not build this. **Do not edit project files.** Scratch: `$S/revC/`, where `$S=/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad`.

- Root: `~/Desktop/Random/savings-first-deck/`
- Python: `~/.cortado-venv311/bin/python`

## Read first

- Operator decisions and inputs:
  - `story/COHORT_INPUTS_2026-10-16.md`
  - its three addenda: `COHORT_INPUTS_addendum_crosssell_dpd`, `addendum2_research`, `addendum3_collections_fix`
  - `story/COHORT_RERUN_agreed_2026-10-16.md`
- The agreed distributions: `tables/dist_agreed_v1.csv`.
- The code: `model/cohort_engine.py`, `model/cohort_mc.py`, `model/build_cohort_xlsx.py`.
- The outputs:
  - `tables/cohort_bridge.csv`
  - `tables/cohort_mc_summary.csv`
  - `tables/cohort_mc_must_be_true.csv`
  - `tables/cohort_mc_drivers.csv`
  - `tables/cohort_crosssell_reconcile.csv`
  - `tables/cohort_det_*.csv`
- The previous view, for contrast: v2 needed 37 of 100 still saving at 12 months for a 5-year break-even (`tables/xs_breakeven_v2.csv`).

## Context

- One salaried agent on ₹20,000 a month.
- Sign-ups: about 60 a month, agreed.
- Savers put in ₹350 a day into a debt fund (0.35% trail to us; about 7% return to him).
- From month 1 a marketplace sells loans (₹2.5 lakh, 2.625% fee), cards and 17 insurance, investment, payment and other-loan products. In months 1–6 take-up and approval are lower.
- The lender carries the loan losses.

## What to check (each finding: severity P1/P2/P3, evidence, exact fix, verified or plausible)

1. **Mechanics: independent recompute.** Write your own small cohort calculation for ONE cohort of 100 sign-ups at the likely values. Do not import the engine. Compare against the engine's age profile over 60 months:
   - still saving;
   - balance;
   - fund trail;
   - loans made;
   - origination fees;
   - cross-sell by product;
   - card fees;
   - collections.

   Tolerance ±2%. Then check that the calendar aggregation over cohorts and the discounting are right.
2. **Conservation and timing:**
   - savers who stop withdraw their whole balance;
   - a borrower with a loan running doesn't re-apply;
   - renewals happen only while he is still saving;
   - fees taken back within 6 months;
   - collections at +9 and +18 months;
   - the month-1 marketplace and the early-months multipliers applied as specified;
   - cards issued once.
3. **Plausibility against benchmarks.** These are the most important checks.
   - **Revenue per active saver per year.** Compute the model's all-in figure and compare it with:
     - Paytm's ₹407 a year per monthly user from all financial services (XO-11);
     - PhonePe's ₹8 per active user on insurance (XO-10);
     - Paytm's statement that funds and insurance are "negligible" (XO-11);
     - Paytm device rent of ₹1,080 a year per merchant.

     If the model is above Paytm per user, is that defensible for a saver an agent visits every 2–3 days? Say plainly.
   - **Loans per 100 active savers a year, and money lent per agent per year.** Compare with any evidence in `research/*.csv`, e.g. XL-42, LS-06, NG-028, XL-04.
   - **The retention curve after month 12** (churn_late likely 1.5% a month). Compare it with the only Indian data point, one janta agent's existing book losing 6–10 of 200–400 a month, about 2.7% (IV-01, IV-12). How much of the result rests on this?
   - **The fund step** (+₹1.2 lakh from 25% kept at term end and the return). Check that the balance compounding is right and not double-counted.
   - **"Marketplace from month 1"** (+₹3.3 lakh before the early-months factors). Is it reasonable that new savers get loans in month 1–2 at the agreed approval rates multiplied by the early factor?
4. **Monte Carlo.**
   - The sampler matches the agreed distributions (spot-check 10 keys: p10/p50/p90).
   - The −0.5 copula works.
   - There is no leak: no input stuck at its likely value, and no key silently falling back.
   - P(NPV60 > 0) stays stable at 5,000 vs 10,000 draws.
5. **The Excel.**
   - Open `Cohort_model.xlsx` with openpyxl. Check for hard-coded numbers inside formulas and for inputs not linked to the Inputs sheet.
   - Recompute one month by hand and match it to the Python.
6. **The headline.** Of everything that makes P(NPV60 > 0) about 99%, list the 3 assumptions that, if they are wrong in the plausible direction, would bring it below 70%. Give one run each. You may run the engine with changed inputs via its API; do not edit files.

## Report (under 700 words)

- The findings, P1 first.
- A one-paragraph verdict: is "about 99%" a fair headline for the operator? If not, what is the honest sentence?

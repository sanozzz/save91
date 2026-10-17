# Prompt: independent investment review of the "save91" business case

You are a senior investment professional at a venture/growth fund. You are doing diligence on an early-stage Indian fintech. You have been given the founder's full working folder:
- a deck;
- an assumptions book;
- Python models;
- the CSV outputs;
- research files.

**Your job is to find every inconsistency, error and weak point before the fund relies on any number.** Be sceptical, specific and quantitative. Assume nothing is right because it is written down.

## What the business is (as the founder describes it)

"Save first, borrow later" for India's urban self-employed daily earners: shopkeepers, vendors, drivers.

- **The agent.** A salaried field agent (₹20,000 a month + 0.25% of his savers' balance, capped at ₹10,000 a month) opens accounts. Half come from bought online leads. He visits every 2–3 days to collect about ₹350 a day.
- **The fund.** The money goes into a debt mutual fund in the saver's own name.
- **The marketplace.** From day one, a marketplace sells loans (personal, home, against property, gold, consumer, vehicle), credit cards, insurance, investments and payments. We earn distributor fees.
- **Own-book lending.** From month 30 an own NBFC keeps the top-quality 30% of personal loans on its book.
- **City limits.** Growth is capped by real-world city limits: at most 20% of a city's addressable self-employed pool can ever be signed.
- **The headline claim.** "Unicorn on paper" from about month 59: 20× ARR and 0.45× AUM both ≥ ₹10,000 crore at ₹100/$, after raising ₹1,108 crore over six rounds, with EBITDA positive from month 55.

## Where to look (priority order)

1. `START_HERE.md`: the map, the current base, and which files are current vs superseded. Read it first. Do NOT review superseded files except to check that the current files don't silently reuse their numbers.
2. **Source of truth for the company plan:** `tables/base_*.csv`:
   - `base_yearly`, `base_monthly`;
   - `base_rounds`, `base_city_plan`;
   - `base_lenses`, `base_headcount`;
   - `base_mc_summary`, `base_inputs`, `base_checks`.

   Also `tables/cities.csv`, `tables/share_compare.csv` and `tables/sat_sensitivity.csv`.
3. **Unit economics (one agent):**
   - `tables/cohort_det_*.csv`, `tables/cohort_mc_*.csv`, `tables/cohort_bridge.csv`;
   - `tables/cohort_signups_sweep*.csv`, `tables/cohort_incentive_sweep*.csv`.
4. **Inputs:**
   - `tables/dist_agreed_v1.csv` (every input as a distribution, with source IDs and confidence labels);
   - `Assumptions_agreed.pdf`.
5. **Evidence:** `research/*.csv` and `research/*.md`, one row per source with an ID (XL-, XO-, XB-, IV-, REG-, NG-, SEG-, GAP-, PR-, LEV-…).
6. **The deck:** `Offline_model_v3.pdf`.
   - Parts 1–3 are the agent unit economics; Part 4 is the company.
   - Treat the deck as presentation: every number in it must trace to a table.
7. **Code**, if you can run it (Python 3.11, numpy/scipy/pandas):
   - `model/cohort_engine.py`, `cohort_mc.py`;
   - `company_model.py`, `saturation.py`, `nbfc.py`;
   - `share_compare.py`, `base_plan.py`.
8. **Known exclusion:** `Cohort_model.xlsx` is known NOT to reconcile. Ignore it.
9. **Google Sheet:** a toy version exists in a Google Sheet called "Save4More". If you have no access, skip it.

## What to check (minimum; go beyond it)

**A. Numbers across files.**
- Every headline number in the deck and `START_HERE.md` must match its table. Check revenue, EBITDA, PAT, cash, savers, AUM, book, agents, cities, rounds, ownership, the lenses and the MC probabilities.
- Yearly totals must equal the sums of the monthly rows.
- The P&L ladder must add up: revenue → CM1 → CM2 → CM3 → EBITDA → PAT.
- Cash must roll forward: opening + operating + investing + financing = closing.

**B. Unit economics vs company.**
- Does the company model's per-agent behaviour match the one-agent model at the same inputs? Compare sign-ups, retention, savers per agent (about 2,238 at month 60), revenue per saver (about ₹890 a year mature) and AUM per saver (about ₹61,000).
- Is AUM per saver plausible for about ₹350 a day × 20 days a month with yearly terms, a 25% rollover and a 7% return?
- Revenue per active saver is about ₹730–890 a year against Paytm's about ₹407 per monthly user (cited). Is that defensible?

**C. City numbers.**
- The pool is about 7 crore urban self-employed, sized from PLFS shares. Is that number right?
- Check the rank-size estimate (q ≈ 0.865; NCR about 6.3% of urban India ≈ 44 lakh addressable).
- About 500 Class I cities, and a 20% cap, giving about 91 lakh people as the national ceiling. Check the arithmetic.
- Does `base_city_plan.csv` (172 cities, ≤ 4 new a month) respect each city's cap?
- Are active savers (peak about 37 lakh) consistent with cumulative sign-ups under the cap, given churn?
- Is NCR's penetration path plausible?
- Is the ~24% year-1 churn behaviour consistent between the unit and company models?

**D. Funding and ownership.**
- Recompute post-money, dilution and founders % after each round from `base_rounds.csv`, with the stated ESOP rule.
- Is any round priced below the previous post-money?
- Is the step-up rule (3× / 3× / 2.5× / 2× / 1.5×) applied as stated?
- Do round sizes match the stated 18–24 months of runway?
- Is the lowest cash ever negative?

**E. Valuation lenses.**
- The 0.45× AUM multiple comes from Stable Money's valuation over CUMULATIVE money invested, not AUM. Is applying it to AUM consistent?
- Is 20× ARR reasonable, given that ARR includes NBFC net interest income?
- Recompute lens 3 (3× NBFC book equity + 20× fee ARR).
- Is "unicorn on paper at month 59" robust or knife-edge? The AUM lens clears by about +0.7%; the MC gives about 29%.

**F. NBFC.**
- The terms: yield 26%, cost of funds 13.5%, leverage 3×, capital ≥ 15%, on-book loss 0.6× the agreed loss rate, processing fee 2%, net owned funds ₹10 crore.
- Check that interest, provisions, borrowings and equity reconcile.
- Is NBFC equity counted in group cash and also lent out (a double count)?
- Are collection fees on on-book loans removed?
- Does the "top 30% of loans by quality" selection leave the partner lenders with adverse selection, which the model doesn't price?

**G. Costs and the cost base.**
- Headcount × pay reconciles to people cost.
- Central-team scaling at 5,000 agents and 172 cities; field managers; the per-city costs.
- The ₹5 a month per saver running cost.
- The capped incentive.
- KYC, leads, cash cover, contingency, tax losses carried forward.
- Is anything missing or double counted? Examples: GST, TDS, licence costs, app build, technology at scale, cash-handling risk, agent fraud.

**H. Assumptions vs evidence.**
- For the inputs that move the result most (`tables/cohort_mc_drivers.csv`), check the cited research row says what the label claims.
- Check the confidence labels are honest ("Your number" / "Published" / "Industry guide, not verified" / "Our judgement").
- Flag any input sourced only from a blog or a single statement. Example: PR-01, a practitioner saying field agents onboard 100+ a month.

**I. Regulatory consistency.**
- The cash route: the agent collects cash, we deposit it into the fund's collection account, and send a reconciliation.
- Check it against the folder's own notes on SEBI and AMFI rules:
  - a distributor handling investor money;
  - payments from the investor's own account;
  - a cash cap of about ₹50,000 per investor a year, while the saver puts in about ₹84,000 a year.
- Also check the IRDAI commission caps, SEBI on digital gold, and NBFC licensing.

**J. Story vs model.**
- Does the narrative ("profitable", "unicorn", "agent pays back around month 40") hold in the current base tables?
- Flag any claim carried over from a superseded round. Earlier rounds used 30, 60 or 83 sign-ups, NPV at 20%, the 80-agent plan, and the unicorn track without city limits.
- Note the post-year-5 decline (active savers 37 lakh → 24 lakh by year 8). Is it acknowledged consistently?

## Rules

- **Re-compute; don't accept.** For each finding, show both numbers, the files and rows (or deck page) they come from, and your recomputation.
- **Separate the kinds of finding:**
  - (a) arithmetic or consistency errors;
  - (b) modelling choices you disagree with;
  - (c) judgement inputs you consider unrealistic.
- **Mark each finding:**
  - "verified": you recomputed it;
  - "suspected": you could not fully verify it.
- **Units:**
  - ₹ crore and lakh (1 crore = 100 lakh = 10 million);
  - the founder uses ₹100 = $1;
  - months are counted from company launch (m1 = the first month); "Y5" = months 49–60.
- **External facts:** do not introduce outside facts as truths. If you rely on outside knowledge (e.g. typical NBFC valuations), label it "external, unverified".

## Output format

### 1. Executive summary (5 bullets)

- Is the base plan internally consistent?
- Which three issues matter most?

### 2. Findings table, most severe first

| ID | Severity | Category | Where | What's inconsistent | Evidence (both values + sources) | Recalculation | Suggested fix | Status |
|---|---|---|---|---|---|---|---|---|

**Severity:**
- **P1:** changes the investment decision or a headline number by more than 10%;
- **P2:** material, but not decision-changing;
- **P3:** minor or presentational.

**Categories:**
- numbers;
- unit vs company;
- city;
- funding/ownership;
- valuation;
- NBFC;
- costs;
- evidence;
- regulatory;
- story vs model.

### 3. Ten diligence questions you would put to the founder

These are beyond the inconsistencies.

### 4. Investment view (half a page)

- Would you lead or join the next round on these numbers?
- What would have to be true?
- Which three numbers would you ask the pilot to prove first?

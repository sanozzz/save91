# Brief: lock the real-world city setting, and test an NBFC from year 3 (operator, 17 Oct 2026)

## Operator (taps)

- "Lock real-world setting"
- "Test NBFC from year 3"

## 1. Lock the real-world default everywhere

**The city layer is ON by default:**
- the soft saturation curve (1 − (pen/cap)²);
- a 3% a year pool refill;
- at most 4 new cities a month;
- a 20% city cap;
- the urban self-employed pool, pert 6.5/7.0/7.7 crore;
- about 500 Class I cities on the rank-size estimate.

**Re-run under the locked default:**
- (a) the profitable plan: 200 agents; cities opened as the AUTO rule allows (≤ 4 a month); funding sized; dilution capped at 25%, so fix the seed dilution;
- (b) the best unicorn attempt (AUM-only), as in sat_sensitivity.

**Write `tables/rw_*.csv`:**
- `rw_profitable_*`: yearly, monthly, rounds, city_plan;
- `rw_unicorn_*`: the same set.

Keep the earlier tables unchanged.

## 2. NBFC test, from month 30

**Inputs** (judgement unless sourced; label every one):

- **Licence:**
  - acquire or build an NBFC-ICC: ₹1 crore cost at m24 (LEV-031);
  - net owned funds (equity in the NBFC) of at least ₹10 crore from m24, held as capital;
  - extra NBFC opex from m24: ₹15 lakh a month (credit, risk, compliance, treasury), + ₹5 lakh a month per ₹500 crore of book.
- **On-book share of personal-loan volume:**
  - 10% at m30, rising linearly to 50% at m54, then flat;
  - top-ups follow the same share;
  - housing and the other lenders' loans stay with partners.
- **Economics of the on-book loans:**
  - yield 26% a year on outstanding (the EMI rate; LEV-012 25–28%);
  - a processing fee of 2% of the loan, paid by the borrower, at disbursal;
  - NO DSA origination fee on on-book loans (we are the lender);
  - cost of funds 13.5% a year on borrowings (LEV-014/015).
- **Funding:**
  - leverage, borrowings ≤ 3 × NBFC equity (LEV-023: AUM/TNW 3.25×);
  - capital adequacy ≥ 15% (keep 20% as the operating floor);
  - NBFC equity comes from company equity rounds, so the rounds must also fund the book's equity;
  - borrowings fill the rest.
- **Credit losses on the book** (now ours):
  - use the agreed `loss` distribution as the lifetime loss of money lent (likely 3%; Paytm worst case 5%);
  - recognise it as an expected-loss provision at disbursal: lifetime loss × amount;
  - recoveries per the agreed recovered share;
  - our collections fees on on-book loans are internal: drop them, and keep the agent's collection effort.
- **Amortisation:** EMIs over the tenure (36 months likely) for outstanding balances. Use the existing EMI mechanics.

**P&L presentation:** add lines for interest income, cost of funds, net interest income, processing fees and credit cost (provisions). Then CM1 = fee revenue + NII + processing fees − direct costs − credit cost. The rest of the ladder is as before.

**Valuation lenses at m60** (judgement):
- (1) 20× ARR, where ARR = 12 × (month-60 fee revenue + NII + processing fees);
- (2) 0.45× AUM (as before);
- (3) a NEW lending lens: 3× the NBFC's book equity (P/B, judgement; fintech NBFCs at Series-C-like stages), plus the platform at 20× its fee ARR. Show it as a cross-check.

## 3. Runs

For each: feasible? total raised; founders %; savers, AUM, loan book and NBFC equity at m60; the lens margins; EBITDA and PAT by year; the lowest cash.

- **NB1:** the profitable 200-agent plan + NBFC from m30.
  - Does it stay EBITDA-positive by m51–60?
  - What does the book add to year-5 revenue and PAT?
- **NB2:** the least-equity unicorn on paper by m60 (both lenses 1 and 2), with NBFC from m30, under the locked real-world city setting.
- **NB3:** the same as NB2 with an 80% on-book share, to show the upside and the capital it needs.

Write `tables/nbfc_*.csv`: inputs, yearly, rounds, lenses, checks.

## Report (under 300 words)

- The locked-default results (profitable and unicorn).
- NB1, NB2, NB3: what the NBFC adds, and whether a year-5 unicorn is feasible.
- The capital needed for the book.
- The risks: credit losses now on our P&L; leverage.

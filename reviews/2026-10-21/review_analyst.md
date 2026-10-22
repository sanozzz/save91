# Analyst review: Save91 / SaveMore online v4 numbers (21 Oct 2026)

**Reviewer angle:** diligence analyst doing the numbers and model review behind an IC memo.
**Scope:** `model/online_plan.py`, `model/online_mc.py`, `model/ltv_book.py`, `model/cohort_engine.py`, `model/cohort_mc.py`, the `tables/online_*` and `tables/ltv_*` outputs, the four investor decks (HTML), and the research rows they cite.
**Prior reviews:** I do not repeat `INVESTMENT_REVIEW.md` or `INVESTMENT_REVIEW_v4_status.md`. Where I touch the same input (apply rate, ticket, retention, reach), I add something new: a quantification, a contradiction, or a source the earlier review did not use.
**Method:** everything below marked *Verified* was re-run. The scripts are in `scratchpad/analyst/a1_headline.py` to `a13_stack.py`. They import the repo's own models and override inputs only through `op.OV`, `op.TECH_PER_SAVER` and the CAC argument. No repo file was edited.

---

## 0. Bottom line

**The arithmetic reproduces exactly:**
- 4.10× and month 19 online;
- 3.83× and month 23 doorstep;
- EBITDA positive in month 40;
- money needed $2.46M;
- Monte Carlo median 3.79×, 77% of futures at 3× or more, P10 2.58×.

The workbook check also holds. **The numbers are not ready for IC**, for four reasons:

1. **A cost line the folder itself priced has been dropped.** The 2 Oct model charged about ₹2 per daily UPI debit and ₹4 a month for tech. v4 charges nothing for debits and ₹1 for tech. At the folder's own base the online saver falls to 2.08× and the company needs $5.1M. At the published list price, LTV/CAC is negative.
2. **The model does not describe the product in the deck.** The deck sells "credit as the reward for saving: save 6 months, see your loan offer". The model shows loan offers from day 1 to every KYC'd user, including the 1.5 per saver who never save. Those non-savers supply about 40% of LTV. Modelled as described, the saver is worth 2.31× and the company needs $4.1M.
3. **Year-5 profit rests on three judgements with no evidence.** They are the DSA payout ramp, take-up growth and approval growth. Together they carry ₹16.4 cr of the ₹18.2 cr year-5 EBITDA.
4. **The Monte Carlo cannot fail.** Its ranges are centred on the plan, and its low ends sit above the evidence they cite. Its "bad-year" correlation is wired to inputs that have no effect. Re-centred on the folder's own evidence, the median is 1.18× and 1% of futures reach 3×.

---

## 1. Headline numbers: recomputed, and consistency across documents

| Headline | Recomputed | Decks | Match |
|---|---|---|---|
| Online LTV/CAC, 5 years | 4.101× (LTV ₹1,845.3, revenue ₹1,972.2, serving ₹126.9) | 4.1× (v4 cover and p5, business case p1–2, LTV deck p1 and p3) | Yes |
| Online payback | month 19 | month 19 | Yes |
| Doorstep LTV/CAC, payback | 3.834×, month 23, CAC ₹404.2, LTV ₹1,549.7 | 3.8×, month 23, ₹404, "₹1,550 back" | Yes |
| EBITDA positive (20k a month) | month 40; deepest cash hole month 42 (−₹18.4 cr) + ₹5 cr floor | month 40 | Yes |
| Money needed | $2.464M | $2.5M | Yes |
| Year-5 / year-8 EBITDA | ₹18.19 cr / ₹52.50 cr | ₹18 / ₹52 cr (A6) | Yes |
| LTV Monte Carlo P10 / P50 / P90 | 2.58 / 3.79 / 5.69; ≥3× 77.4%; <1× 0.1% | 2.6 / 3.8 / 5.7; 77% | Yes |
| Company Monte Carlo | profit month 37 / 42 / 49; money $2.04M / $2.57M / $3.39M; 98.4% positive by month 60 | same (v4 p11, A8) | Yes |
| Seed: still saving at month 18 | 13,929 | "~13,800" (seed plan p1) | Rounding off by ~130 |

Inconsistencies found (all Verified):

- **AN-13a (P2) "24% still saving" has two answers.**
  - v4 p7 and business case p3: **2.6×** (r12 24%, r3 52%; `online_ltv_levers.csv` 2.63).
  - LTV deck p6 and A1, and the v4 status note: **2.7×** (2.72; r12 24% with r3 held at 80%).
  - Fix: one definition. The savings-app curve has r3 at 52%, so 2.63× is the honest number.
- **AN-13b (P2) Business case p6 has a wrong title.** It says savings-app retention or debt-only funds "push it to months 52–59". The model gives month 48 and month 42. The 52–59 cases are "savers only" (52) and "10% apply" (59).
- **AN-13c (P2) The trail after a saver stops is described two ways in one deck.**
  - LTV deck p8: the trail is "paid while the money stays invested, even after a saver stops adding".
  - LTV deck p7 and the engine: "a saver who stops takes the balance" (`cohort_engine.py:22`, `:459`). Fund fees are earned only on savers still saving (`:560`).
  - See AN-11.
- **AN-13d (P3) Two decks explain the Monte Carlo median in two different ways.**
  - v4 p11 points to "₹119 a day, 34% applying".
  - LTV p15 says "ranges are wider on the downside".
  - Neither names the main cause. Reach is drawn PERT(1, 2.5, 2.5), so its most likely value is its maximum; at its median (2.31) it costs −0.22×. Late churn (−0.11×), the apply rate (−0.10×) and r12 (−0.09×) follow. The daily amount (+0.23×) and the ticket (+0.13×) skew upward.
- **AN-13e (P3) Labels and docstrings do not match the code.**
  - `online_unit.csv` "other products 60m" (₹413) includes the ₹315 of other-lender loans; the waterfall's "Other products" is ₹97.
  - v4 A6 "Loan fees" leaves gold, LAP and home referrals out and books them under "Other products". That gives loans 59% of year-5 revenue in A6 against 63% on the LTV pages.
  - `online_mc.py:5-8` still documents apply 1% / 3.6% / 18% and a ticket of ₹25,557 / 58,522 / 2,05,000. The code draws 10% / 35% / 50% and ₹50k / 1L / 2L.
  - `online_plan.py:8-12, 20` still say ₹300 base, ₹550 stress and 95,800 sign-ups.
  - A data-room reader of the code would be misled.
- **AN-13f (P2) "Today's evidence" labels judgement.** The phrase labels the base 9 times in v4 and 11 times in the business case. Yet the LTV deck itself tags the base's largest drivers as judgement:
  - apply 35%: "Founder's judgement; no observed rate" (p9);
  - reach 2.5: founders' choice;
  - ₹450: "founder's judgement".

  The code's own label is "BASE = TODAY'S EVIDENCE + 'what it takes'" (`online_plan.py:10`). The decks drop the second half. Fix: call it "the plan" or "what it takes".

---

## 2. Model mechanics

**AN-02 (P1) The model does not match the product it is meant to price.**
- *Where:*
  - v4 p2, problem 4: "Credit tied to the streak: save 6 months, see your loan offer". The cover reads "credit as the reward for saving".
  - v4 p3 / A5: loan offers ship in release 3, company months 7–12.
  - The code: `marketplace_from = 1` (`cohort_engine.py:137`) and `LOAN_REACH = 2.5` (`online_plan.py:124-125`), multiplied into all loan revenue (`:188-190`, `:319-320`).
  - LTV deck p4: "Loans start in month 1 for every KYC'd user".
- *What:* the deck sells credit earned by saving. The model gives offers from day 1 to every KYC'd sign-up, and 1.5 of every 2.5 never save at all. Those non-savers get the same approval rates and the same yearly approval growth as savers, even though the proposition is that the saving record earns the approval.
- *Evidence:* ₹750 of the ₹1,845 LTV (41%) comes from non-savers (LTV deck p3).
- *Recomputed with offers from a saver's month 7, to savers only:*
  - 2.31×, payback month 34;
  - company profitable in month 57, $4.14M, year-5 EBITDA −₹1.0 cr.
  - Adding a ticket of ₹58,522 gives 1.98× and month 64.
- *Fix:* choose one. Either the deck says loan offers go to non-savers from day 1 (and drops "reward for saving"), or the model uses age 7 and reach 1.
- *Verified.*

**AN-03 (P1) Year-5 EBITDA is mostly three "track record" judgements.**
- *Where:*
  - `fee_mult` 1×→1.5× (`online_plan.py:193`, `:313`). It is hard-coded and not drawn in the Monte Carlo.
  - `takeup_growth` +5% a year and `approval_growth` +10% a year (`cohort_engine.py:447-450`). Both are labelled "Our judgement; no data" in `dist_agreed_v1.csv`.
- *Recomputed (company, 20k a month):*

| Case | Profit month | Money | Year-5 EBITDA |
|---|---|---|---|
| Plan | 40 | $2.46M | ₹18.2 cr |
| Payout flat at 2% | 44 | $2.69M | ₹11.0 cr |
| Growth off | 47 | $2.93M | ₹6.0 cr |
| Both off | 52 | $3.26M | ₹1.8 cr |

- At the saver level: 4.10× → 3.69× (no ramp), 3.56× (no growth), 3.25× (neither).
- The folder's own regulatory note expects lenders to "approve fewer loans and pay smaller fees than in 2019–22" (`regulation_summary.md` §1.1). Its cost research sets the lead-sourcing fee at a 1.5% base and calls 3% optimistic (`tri_costs_summary.md`, `lsp_fee`).
- *Fix:* show year-5 EBITDA with and without these three. Draw the ramp in the Monte Carlo.
- *Verified.*

**AN-08 (P2) The headline saver never exists.**
- *Where:* `ltv_book.py:580-598`, and LTV deck p2, "The cautious saver".
- *What:* the 4.10× pairs the revenue of a saver who joins in company month 1 with the post-seed ₹450 CAC. The company launches in month 4. Loans start in month 7. ₹450 applies only from month 19.
- *Recomputed by cohort (`a3_cohort.py`):*

| Cohort | LTV/CAC | Payback |
|---|---|---|
| Month 4 at ₹600 (first real savers) | 3.16× | month 23 |
| Month 12 at ₹600 | 3.40× | — |
| Month 19 at ₹450 | 4.79× | — |
| Month 31 at ₹450 | 5.19× | — |

- The later cohorts sit above the headline only through AN-03's growth judgements. The company P&L at scale therefore runs on about 5× cohorts that are mostly judgement.
- *Fix:* show the seed-cohort number (3.2×) and the steady-state number with and without the growth factors.
- *Verified.*

**AN-07 (P2) The LTV/CAC uses a cost basis the company model does not use.**
- *Where:* contingency, `online_plan.py:219` (10% on marketing spend); serving, `:321` (savers only); A3 footnote: "₹450 to win costs ₹495 in the company model".
- *Recomputed:*
  - at ₹495: 3.73×;
  - serving the 1.5 non-saver KYC'd users at the same ₹6 a month: 3.68×;
  - both: 3.34×;
  - doorstep at ₹404 × 1.1: 3.49×.
- Company with non-saver serving: profit month 44, $2.84M.
- The LTV review (fix 17) flagged non-saver serving as an assumption. It was not priced. Loan applicants generate support contacts and grievances, which the digital lending rules make mandatory.
- *Fix:* publish LTV/CAC at the CAC the plan actually spends.
- *Verified.*

**AN-09 (P2) Cost to win and reach are linked by arithmetic, but drawn independently.**
- *Where:* `SIGNUPS_PER_SAVER × KYC_SHARE` (`online_plan.py:124`); the Monte Carlo draws `cac` and `on_reach` independently (rank correlation −0.05).
- *What:* at the seed's own unit costs (₹100 a sign-up, ₹40 a KYC for half), CAC = 120 × sign-ups per saver and reach = CAC ÷ 240.
  - If ₹450 comes from better conversion, reach is 1.875 and LTV/CAC is **3.41×**.
  - The "₹300 to win → 6.2×" lever becomes **4.07×** (reach 1.25). Keeping reach at 2.5 needs ₹40 a sign-up, which is below the ₹75 fintech install median the seed plan itself cites.
- *Fix:* model CAC as cost per sign-up × sign-ups per saver, and derive reach from the same number.
- *Verified.*

**AN-10 (P3) The loan reach covers loans outside the 35% funnel.**
- *Where:* `LOAN_XS` includes `loan_cd` and `loan_vehicle` (`online_plan.py:126`). `LOAN_MIX` (`:128`) splits the 35% only across personal and business, gold, LAP and home.
- *What:*
  - Durable and vehicle loans come on top of "35% apply (all loan types)", at street take-ups, and are multiplied by 2.5.
  - These and gold loans are the "once" kind with no approval step (`cohort_engine.py:357-366`), so they convert at 100%.
- *Effect:* removing the extra reach on durable and vehicle loans and giving gold 70% approval: 4.10× → 3.95×.
- *Verified.*

**AN-11 (P2) Balances of savers who stop.**
- *What:* the engine assumes every stopper redeems the whole balance at once. For an equity SIP, stopped SIPs often stay invested. The LTV deck p8 says the trail continues.
- *Recomputed (an upside the model omits):* +₹174 to +₹422 over 5 years at 5% to 0% monthly redemption, giving 4.49× to 5.04×. It also affects the AUM lens.
- *Fix:* pick one behaviour, model it, and correct whichever page is wrong. This is the only finding here that raises the number.
- *Verified.*

**Checked and found sound (Verified):**
- the loan state machine and top-up recurrences (the engine's own `state_split_check`, `topup_check` and `crosssell_check` pass);
- the age-to-calendar convolution;
- tax with losses carried forward (`:223-228`);
- the 2-month cash lag (`:229-230`);
- the deepest-hole definition of money needed;
- the ₹40 KYC inside the ₹600 seed CAC;
- seed-phase spend in the company model: $322k gross over months 1–18, against the seed plan's $338k before contingency. Consistent.

---

## 3. Assumptions against evidence: the inputs that drive the answer

| Input | Plan | Folder evidence (row) | Quality | Distance |
|---|---|---|---|---|
| Apply for a loan a year | 35% | 1–2% a year, merchants on a payments app (XF-16, derived); 3.6% review proxy; 49% re-borrow *among borrowers* (XF-17, not an apply rate) | No observed apply rate | 10–35× the nearest observation; **founder judgement shown as "today's evidence"** |
| KYC'd users reached per saver | 2.5, non-savers reachable as long as savers | none | No source | Unobserved; Monte Carlo mode = maximum |
| Personal + business ticket | ₹1 lakh | Digital NBFC ₹18,802 (XF-11); **founder's own past loans ₹10–25k (XF-24)**; merchant ₹2.05L needs ₹15k+ a month in QR (XF-09/10) | Published / own data | 4–10× personal-loan evidence. XF-24 is cited for approval (p10) but **its ticket is not**. At ₹25k: 2.54×, month 53, $3.59M |
| First approval | 30%, +10% a year (44% by year 5) | Kissht 11% of new applicants (XL-41); founder 25% (XF-24, 2019–22, before the DLG rules); XF-18's 80% is pre-qualified PSU MSME | Mixed | Above both observations; Monte Carlo low end of 20% is above 11% |
| DSA payout | 2% → 3% | 1–2.5% indicative (XF-01); 1.5% base (`tri_costs` lsp_fee) | Indicative | Start at the mid-high end; the ramp has no source (audit row: "operator-set, no rate evidence") |
| Still saving at month 12 | 38% (r3 80%) | SBI daily SIP: 36% stopped by ~6 months, average age (NG-033/XO-05), extended; "ceased may include never-started mandates" (`tri_costs`); savings apps 24% | Extrapolated | Halfway between |
| Cost to win | ₹450 | seed funnel *budget* ₹600; ₹300 per undefined "customer" (PR-02) | Judgement | Below the only costed funnel |
| Successful debit days | 20 a month | UPI Autopay business declines ~74% (TC-05); the 2 Oct model used 20 with "67% … far above the ~26% ecosystem rate" | Weak | Optimistic; low LTV sensitivity (16 days: 3.86×) but it scales any debit cost |
| Serving per saver | ₹5 support + ₹1 tech | 2 Oct base: support ₹5–6, **tech ₹4**, **debit ₹2 × 20**; Groww ₹28.6 tech + transactions per active user (TC-36) | Published / own research | 6× below the folder's own all-in base (₹49) |
| Equity trail | 0.75% | Prudent 0.88–0.91% gross yield (XO-08) | Published | Reasonable; plan type is open (prior F24) |
| Track-record growth (3 factors) | +5% / +10% / 1.5× | none | Judgement | ₹16.4 cr of ₹18.2 cr year-5 EBITDA |

**AN-05 (P1) The input audit on v4 A10 does not audit this plan.**
- *Where:* v4 p23, "All 68 inputs checked against their sources: 18 match". `tables/online_inputs_audit.csv`.
- *What:* the audit's rows were written for an earlier v4 base:
  - personal-loan ticket **₹58,522**, verdict "matches";
  - apply rate **3.6%**, "Not an apply rate. Impact small online (loan fees ₹11 per saver)";
  - CAC **₹300**.

  The plan of record uses ₹1 lakh, 35% and ₹450. Loans are now 63% of revenue. The three biggest drivers were never re-audited, yet the page tells investors every input was checked.
- *Fix:* re-run the audit on the 21 Oct values, or retitle A10.
- *Verified.*

---

## 4. What is missing from the cost and revenue base

**AN-01 (P1) Payment costs on daily debits.**
- *Where:* nowhere in v4. Serving is ₹5 + ₹1 (`online_plan.py:120`, `:321`).
- *Evidence the folder already has:*
  - `tri_costs_summary.md` (2 Oct): `cost_debit` ₹5 / 2 / 0.5 per successful debit. Cashfree and Zoho list ₹5 + GST per Autopay execution under ₹1,000 (TC-02, TC-06), plus a ₹7.5 mandate fee.
  - `tables/inputs.csv:84` carried ₹2 as the base.
  - The earlier deck (`build_deck.py:807`) said: "It works only at ₹0.5 a debit or less … if we can't get that, we switch to weekly."
  - TC-12 says BSE StAR MF bills ₹6–30 per order to the fund house, not to us. That moves the problem to a fund house paying more per ₹100 daily order than it earns in TER. It does not remove it.
- *Recomputed (tech ₹4 plus debits, 20 a month):*

| Debit price | LTV/CAC | Payback | Company profit | Money |
|---|---|---|---|---|
| ₹0.5 | 3.49× | — | month 45 | $3.0M |
| ₹2 | **2.08×** | month 42 | **month 56** | **$5.1M** |
| ₹5.90 (list) | **−1.59×** | — | not by month 96 | $24M |
| Weekly at ₹2 | 3.58× | — | month 45 | $2.9M |

- *Fix:* add a payment line with the design choice (daily vs weekly, who is the merchant on the mandate), or a signed quote. Until then this is the largest open number in the plan.
- *Verified* recomputation; *Suspected* on who finally bears the cost.

**AN-12 (P2) GST and TDS basis.**
- No line states whether payouts and trail are quoted with or without GST. The folder's DSA payout rows are marked "gross (before TDS/GST)".
- If payouts are GST-inclusive, revenue is ÷1.18: **3.43×**, profit month 44, $2.74M.
- TDS on commissions (194H / 194D) sits as a refund receivable while the company makes losses. That is about ₹0.3 cr of working capital by month 42. Small, but it belongs in money needed.
- *Suspected.*

**AN-15 (P2) Default-loss guarantee cash, if the payout ramp needs one.**
- v4 A5 pairs "larger fees" with "first-loss cover capped at 5%" in the next round. The model ramps the payout from month 1 and holds no guarantee cash.
- Year-5 personal and business disbursals are **₹799 cr**. A 5% guarantee on 18 months of disbursals locks **₹53 cr ($5.6M) by month 60**, more than twice the money needed.
- Moneyview's guarantee paid out about 3% of money lent a year (TC-41). That is about ₹24 cr in year 5, more than the ₹22.9 cr of personal and business payout revenue.
- *Fix:* state that the 3% payout is earned without a guarantee, or model the guarantee.
- *Suspected.*

**Other omissions (P3):**
- **Clawbacks:** only personal and business loans carry "taken back". Insurance free-look cancellations and other-lender clawbacks are not modelled.
- **KYC attempts:** KYC is costed per completion, not per attempt. Abandoned sign-ups still incur PAN and penny-drop checks.
- **Lender integration and partner management:** no cost line for 17 products and at least 5 lenders.
- **Team:** about 30 heads at month 60, with one growth lead for ₹1 cr a month of ad spend and one compliance head across MF distribution, insurance via a partner, lending service provider and data protection. Doubling post-round team cost gives month 44 and $3.0M.
- **Fraud and failed mandates:** no line; failed mandates also need re-creation (TC-39).

---

## 5. Monte Carlo design

**AN-04 (P1) The Monte Carlo is a restatement of the plan, not a test of it.** *Verified*, with recomputation (`a7_mc.py` reproduces the published 2.58 / 3.79 / 5.69 / 77% exactly).

1. **The ranges are centred on the plan, and the low ends never reach the evidence they cite.**
   - Apply rate: PERT 10 / 35 / 50, while its basis column cites 1–2% for the low end (v4 A1). Under 0.1% of futures draw below 10.5%.
   - Ticket: low end ₹50k against an ₹18,802 source. 1.2% of futures fall below ₹58,522.
   - Reach: PERT(1, 2.5, 2.5). 0.4% of futures fall below 1.5.
   - CAC: capped at the seed's unmeasured ₹600 budget.
   - Mean draws: ₹125 a day, 33% apply, ₹1.08 lakh ticket.
2. **The "bad-year" correlation does nothing.**
   - The copula links `approved_first`, `approved_repeat` and `loss` (`cohort_mc.py:36`; `online_mc.py:58-62`).
   - Online, `approved_first` is replaced by the independent `on_approved` (`FIXED_DESIGN`, `online_mc.py:48`).
   - `loss` affects only the EMIs line, because collection fees are zero.
   - Varying `loss` from 1.5% to 5%, or `approved_first`, leaves LTV/CAC at exactly 4.100698.
   - The claim "approvals and losses move together in bad years" (v4 p11, A8; LTV p15) is false in effect. Every driver is independent.
3. **The inputs that should move together are drawn apart.** Rank correlations measured in the draws:
   - apply vs ticket: −0.04;
   - apply vs approval: −0.02;
   - CAC vs reach: −0.05.

   The evidence pairs high frequency with small tickets (Paytm's 13% a quarter includes BNPL, XF-15), and wider funnels with lower approval. CAC and reach are linked by arithmetic (AN-09).
4. **"94 inputs drawn" overstates coverage.** 11 are inert for both savers (street mechanics: `lead_cost`, `capacity`, `cash_cover`, `loss`, `recovered`…). 14 are inert online. With about 80 small independent inputs, their noise cancels and the spread narrows.
5. **The evidence-centred rerun.** I kept the same uniforms and only re-centred eight inputs on folder evidence, with the plan's values as the high end:
   - apply 2 / 10 / 35%;
   - ticket ₹18.8k / 58.5k / 1.5L;
   - reach 1 / 1.5 / 2.5;
   - r12 24 / 30 / 45% (r3 52 / 70 / 85%);
   - first approval 11 / 25 / 35%;
   - payout 1 / 1.5 / 2.5%;
   - CAC ₹300 / 600 / 800.

| Ranges | P10 | P50 | P90 | ≥3× | <1× |
|---|---|---|---|---|---|
| Published | 2.58 | 3.79 | 5.69 | 77% | 0% |
| Published + tech ₹4 + ₹2 × 20 debits | 0.77 | 1.90 | 3.53 | 16% | 17% |
| Loan funnel re-centred only | 1.13 | 1.78 | 2.84 | 7% | 5% |
| Retention + CAC re-centred only | 1.68 | 2.53 | 3.88 | 30% | 0% |
| All eight re-centred | 0.73 | **1.18** | 1.95 | **1%** | 32% |

- *Fix:*
  - present "77%" as "77% of futures inside our own ranges";
  - add an evidence-centred run;
  - wire the copula to `on_approved` and to a real loss or approval link, or delete the claim;
  - correlate apply with ticket and approval, and derive reach from CAC.

---

## 6. Sensitivity: the minimum evidence that breaks it

All runs are one-at-a-time or combinations from the plan base, at 20,000 online savers a month (`a4_costs.py`, `a5_combos.py`). Pass lines below come from the LTV deck.

**3× breaks with ONE input at a folder evidence value:**

| Input at evidence value | LTV/CAC | Payback | Company profit | Money |
|---|---|---|---|---|
| Apply 3.6% | 1.73× | — | month 73 | $5.3M |
| Ticket ₹25k (the founder's own loans) | 2.54× | — | month 53 | $3.6M |
| Daily debits at ₹2 | 2.08× | — | month 56 | $5.1M |
| Offers to savers only | 2.43× | — | month 52 | $3.6M |
| Product as described | 2.31× | — | month 57 | $4.1M |
| Savings-app retention | 2.63× | — | month 48 | $3.0M |

One input is enough. Each of these is a single folder evidence value, against pass lines of 21% apply, ₹47k ticket, 27% retention and 1.5 reach.

**Company profitability within 5 years breaks with ONE input or with TWO:**
- *One input:* apply at 3.6% gives month 73.
- *Two inputs:*

| Pair | Company profit | Money |
|---|---|---|
| Ticket ₹25k + savers only | month 69 | $4.9M |
| Retention 24% + savers only | month 64 | $4.4M |
| Apply 10% + ticket ₹58.5k | month 66 | $4.6M |
| Debit ₹2 + retention 24% | month 70 | $6.0M |
| Debit ₹2 + ticket ₹58.5k | month 78 | $7.5M |

**Company profitability within 8 years breaks with TWO inputs:**
- Debit ₹2 + savers only: 0.41× and no profit by month 96 ($11.6M or more).

**A corrected base, before any judgement input changes:**
- *Mechanical fixes only* (tech ₹4, non-saver tech ₹4, weekly debits at ₹2, CAC ₹495): **3.00×**, company month 47, $3.25M.
- *With the product as described:* 1.63×, month 66, $5.4M.

---

## 7. Corrections I would require before IC

1. **Add the payment line (AN-01).** Get a written per-debit quote, or switch to weekly debits. Re-run every headline.
2. **Reconcile the product and the model (AN-02).** Either change the proposition to "loan offers to every KYC'd user from day 1", or model offers from month 7 to savers only. Publish both numbers.
3. **Separate evidence from judgement in year-5 EBITDA (AN-03).** Show the plan with and without the payout ramp and the two growth factors (₹18.2 cr vs ₹1.8 cr). Draw the ramp in the Monte Carlo.
4. **Fix the Monte Carlo (AN-04).**
   - Add an evidence-centred run beside the published one.
   - Wire or remove the "bad-year" correlation claim.
   - Correlate apply with ticket and approval.
   - Derive reach from CAC.
   - State the 77% as "inside our ranges".
5. **Re-run the input audit on the 21 Oct values (AN-05),** or retitle A10.
6. **Put one cost basis on every LTV/CAC (AN-07, AN-08).**
   - Use the CAC the company pays (₹495) and serve non-savers.
   - Show the seed-cohort (3.2×) and steady-state numbers beside the month-1 headline.
7. **State the bases (AN-12, AN-15, AN-11).** GST and TDS on all commissions, guarantee use for the payout ramp, and what happens to a stopper's balance.
8. **Clean the inconsistencies (AN-13).**
   - The 24% case: one number.
   - Business case p6 title.
   - "Today's evidence" → "the plan".
   - Stale docstrings in `online_mc.py` and `online_plan.py`.
   - Table labels for other-lender loans.
   - Seed figure of 13,800.
   - The stated reasons for the Monte Carlo median.
9. **Use the founder's own loan data (XF-24).** It is already cited for approval. Its ₹10–25k ticket and 30–50% second-loan rate belong in the ticket and repeat ranges.

# One online saver: the plan's inputs checked against Indian evidence

**Date:** 23 October 2026
**What this is:** the evidence half of the LTV/CAC check. A separate check recomputes the model's arithmetic (the `recalc` files in this folder). This one asks a different question: when each input that moves the answer is set to what Indian data from 2024–2026 supports, what does one saver return?
**Read:** the research folder (`others/research/*.csv`), the input audit, the 21 October critical review and the LTV deck, plus about 40 new searches. Every source, date and exact figure is in `evidence.csv` beside this file.

---

## Summary

1. **On the evidence, one online saver returns about 0.3× their cost to win over five years** (₹274 back against ₹825), not the plan's 7.7×, and never pays back within eight years. If the founders' loan sizes stay as they are, it is 1.3× (payback month 46). The plan's 7.7× is what you get only when every input sits at the top of its evidence range at the same time (7.7×).
2. **These inputs are furthest outside the evidence:**
   - **The ₹3 lakh personal or business loan.** App lenders lend first-time and thin-file borrowers ₹5,000–25,000. A ₹3 lakh, 18-month loan needs ₹38,000–51,000 a month of take-home pay, two to four times the average worker's income.
   - **The ₹30 lakh home loan and ₹25 lakh property loan.** Mass-market lenders average ₹10–12 lakh and ₹3.9 lakh.
   - **The share who borrow.** The plan has 10.5% of reachable users taking a first loan each year (35% apply × 30% approved). Large apps show 1–5%.
3. **Also outside the evidence:**
   - **₹450 to win a saver.** India's largest investing app, with mostly free sign-ups, pays ₹800–1,400 for each new investor, and the seed's own budget is ₹600.
   - **The payout rising from 2% to 3%.** Rate cards say 1–2.5%, with no rise.
4. **Inside the evidence, or close to it:** the fund commission, the month-12 retention figure, repeat-loan approvals and the debit cost. Each moves the answer by less than 1×.
5. **What the seed must measure, for each month's group of savers:**
   - the share of KYC'd users who take a first loan;
   - the median loan lenders actually approve for them;
   - the fee lenders pay after money taken back, in writing;
   - the cost per saver who makes a first debit;
   - still saving at month 12, and the cost to serve each saver.

---

## How to read this

Each input section keeps three things apart:
- **Founders' number:** what the plan uses today.
- **Evidence:** what was found, with the date and whether it is **primary** (a filing, a regulator, a credit bureau, the industry body's own report, a company's own letter or price list) or **secondary** (press, blogs, analyst notes, or primary figures reported by press). "Not found" means a real search turned up nothing.
- **Judgment:** my range, a defensible base value and a confidence level.

"Effect" is always one change at a time, starting from the plan (7.70×). Every run uses the plan's model unchanged (`others/model/online_plan.py`). Only values were changed, in memory. The founders' decisions stay as they are in every run: 90/10 online/doorstep, insurance at 0, weekly debits, the 10% contingency, the opt-in counted inside the apply rate, and no discounting. The loan sizes are also a founders' decision. They are tested here, and the answer is shown both with and without them.

## The ten inputs at a glance

| # | Input | Plan | Evidence range | Defensible base | Confidence | Effect alone (plan 7.70×) |
|---|---|---|---|---|---|---|
| 1 | Cost to win a saver (before the 10% contingency) | ₹450 | ₹300 – ₹1,400 | ₹750 | low | 4.62× |
| 2 | Still saving | 80% m3, 38% m12, then 1.5% stop a month | 24–45% at m12; 1–4% a month after | 80% m3, 35% m12, then 2.5% a month | low | 5.84× |
| 3 | Apply for a loan, a year | 35% | 4–45% (implied); 1–5% actually borrow | 20% | low | 4.44× |
| 4 | First loans approved | 30%, +10% a year | 11–30% | 20% (growth kept) | medium | 6.07× |
| 5 | Personal + business loan | ₹3,00,000 | ₹15,000 – ₹1,20,000 | ₹50,000 | medium (high that ₹3 lakh is outside) | 2.99× |
| 6 | Loan payout | 2% rising to 3% | 1–2.5%, flat | 2% flat | medium | 6.58× |
| 7 | Home / property loan | ₹30 lakh / ₹25 lakh | ₹10–15 lakh / ₹3–10 lakh | ₹12 lakh / ₹5 lakh | high | 6.52× |
| 8 | Fund commission (trail) | 0.75% equity, 0.35% debt (0.67%) | 0.50–0.88% equity; 0.08–0.50% debt | 0.75% equity, 0.10% liquid (0.62%) | medium | 7.62× |
| 9 | Cost per debit | ₹2, weekly | ₹0 – ₹5 | ₹2 weekly (plan kept) | medium | 7.70× (₹0: 8.07×; ₹5: 7.15×) |
| 10 | Repeat loans and top-ups | repeat 70%; top-ups 15% a year | repeat 50–74%; top-ups not found | plan kept | medium / low | 7.70× (range 7.49–7.81×) |
| | **All ten at the defensible base** | | | | | **0.33×** |
| | All ten, founders' loan sizes kept | | | | | 1.32× |

---

## 1. Cost to win a saver

**Founders' number.** ₹450 a saver after the seed (₹495 with the 10% contingency). The seed itself budgets ₹600: ₹100 a sign-up, half finish KYC, and 1 in 5 sign-ups starts saving. Neither figure has been measured.

**Evidence.**
- **Groww, its own letter to shareholders, November 2025 (primary).** "The CAC for H1 FY26 was ₹1,374 … (H1 FY25) … it was ₹796." Groww counts a new user once they have "deposited or invested ₹1,000 or more". That is close to our "saver won".
- **Groww, October–December 2025 (secondary, January 2026):** ₹900.
- **Groww's prospectus, via a broker note (secondary):** 83% of new customers came organically in the June 2025 quarter. So the best-known investing brand in India, mostly free sign-ups, still pays ₹800–1,400 for each new investor.
- **Analyst figures, via Business Standard, October 2025 (secondary):** Groww ₹616 per client, but ₹1,441 per *activated* client. Angel One ₹1,014 per client and ₹6,076 per activated client.
- **Jar, FY24–25 accounts (secondary, derived):** ₹30–50 of marketing per new *registration*. Only a small share of registrations become regular savers, and gold needs no KYC.
- **A growth lead at a daily-savings app, 18 October 2026 (unaudited conversation):** about ₹300 per "customer". It was not said whether that means a sign-up or a saver.
- **Paid installs in India, 2026 (vendor blogs, low quality):** ₹30–300, median about ₹75. At ₹75 an install, with 1 in 3 finishing KYC and 1 in 3 of those making a first debit, a saver costs about ₹675 before any brand spend.

**Judgment.**
- **Range:** ₹300–1,400.
- **Defensible base:** ₹750, which is ₹825 with the contingency. That sits between the seed's own ₹600 budget and Groww's lowest recent ₹900.
- **Confidence:** low. No one publishes a cost per first-debit saver for a mass-market savings app.
- **Where the plan sits:** ₹450 is below every number except the ₹300 conversation.

**Effect alone.** At ₹750, LTV/CAC is 4.62× and pays back in month 17.

| Cost to win | LTV/CAC |
|---|---|
| ₹600 | 5.78× |
| ₹1,400 | 2.48× |
| ₹300 | 11.55× |

## 2. Who keeps saving

**Founders' number.**
- 80% still saving at month 3 and 38% at month 12.
- After that, 1.5% stop each month, so 18% are still saving at month 60.

**Evidence.**
- **SBI Mutual Fund's ₹250 daily-option SIP for first-time investors, from its prospectus via Business Standard, July 2026 (secondary).** "81,570 Jan Nivesh SIP registrations in FY26, of which 29,072 had ceased" (35.64%). The prospectus itself warns of "higher discontinuance rates" because of the low ticket, the daily frequency and first-time investors. Registrations were about 6 months old on average. Extending that to month 12 gives about 28% (straight line) to 41% (a steady monthly loss). The plan's 38% is the steady-loss reading. This is the closest product anyone has observed.
- **All SIPs, AMFI data for September 2026 (secondary, 13 October 2026).** 49.68 lakh plans "discontinued or completed" against 10.06 crore running, so about 4.9% of all SIPs end each month, at every age and income. That figure includes plans that reached their end date.
- **₹250 Chhoti SIPs, SEBI data via Business Standard, July 2026 (secondary).** About 20,000 closures a month against 28,000 new ones, on 322,000 running.
- **"SEBI data shows that even in bullish phases, 73% of investors do not stay invested for more than two years" (Cafemutual, April 2025, secondary).** The SEBI document itself was not found.
- **Failed debits, NPCI data via Mint, September 2025 (secondary).** In August 2025, 55–90% of UPI AutoPay debits at major banks failed, mostly because the balance was too low. A daily or weekly SIP counts as stopped after three missed debits in a row.
- **The plan's 1.5% a month after year one leans on a US micro-investing app (Acorns, 2021, primary but not Indian):** about 1% a month.

**Judgment.**
- **Range:** 24–45% at month 12; 1–4% a month after that.
- **Defensible base:** 80% at month 3, 35% at month 12, then 2.5% a month. That leaves about 27% at month 24, in line with the "73% leave within two years" figure, and 10% at month 60.
- **Confidence:** low. Nobody has observed a ₹100-a-day product for a year.
- **Where the plan sits:** month 12 is inside the evidence. The 1.5% a month after it is optimistic next to Indian SIP data.

**Effect alone.** 5.84× (35% at a year alone: 7.14×; 2.5% a month alone: 6.29×). Low end (52% at month 3, 24% at month 12, 3% a month): 3.66×. High end (45%, 1% a month): 10.07×.

## 3. How many apply for a loan each year

**Founders' number.**
- 35% of reachable KYC'd users apply each year, and 70% of those applications are for personal or business loans.
- The lender-offer opt-in is counted inside the 35%.
- With 30% approved, 10.5% of reachable users take a first loan each year (at the full rate, from month 7).

**Evidence.** No published figure for the share of app users who apply when shown a loan offer was found. The evidence measures the share who actually borrow:
- **Paytm, own results, January 2026 (primary).** 7.1 lakh customers took a financial product in the quarter, against 7.6 crore monthly users: under 1% a quarter.
- **Paytm at its lending peak, July 2023 (secondary, older).** 49 lakh new borrowers in a year, against 9.2 crore monthly users: about 5% a year, mostly tiny postpaid loans.
- **Kissht, a loan app, prospectus April 2026 (primary).** About 2 million new borrowers in nine months, against 53–64 million registered users: about 4.6% a year. And these are people who downloaded the app to borrow.
- **PhonePe merchant loans, March 2026 (secondary, derived).** About 1–2% of merchants borrow each year.
- **Delivery workers, IDinsight, February 2025 (primary research).** "6% took out a digital loan" since joining.
- **A daily-savings app says its customers are "credit hungry" (unaudited conversation, October 2026).** No rate was given.

**Judgment.**
- **What the evidence implies:** borrowing a year (1–5%) divided by first approval (11–25%) gives an apply rate of roughly 4–45%.
- **Defensible base:** 20%. With 20% approved, that means 4% of reachable users take a first loan each year, at the top of what platforms show. That is generous, given the "credit hungry" description.
- **Confidence:** low.
- **Where the plan sits:** the 35% is not contradicted on its own. The plan's apply rate times approval, however, is 2–10 times what any platform shows.

**Effect alone.**

| Apply rate a year | LTV/CAC | Payback |
|---|---|---|
| 20% | 4.44× | month 20 |
| 10% | 2.34× | — |
| 5% | 1.32× | — |

## 4. First loans approved

**Founders' number.** 30% of first applications, rising 10% a year (to about 44% by year 5, capped at 80%). Repeat loans 70%.

**Evidence.**
- **Kissht's prospectus, April 2026 (primary):** "an underwriting approval rate of 11.20% for new applicants and 73.54% for repeat customers in the nine months ended December 31, 2025."
- **The founders' own 2019–22 lending book:** about 25%.
- **TransUnion CIBIL via Business Standard, September 2025 (secondary):** first-time borrowers fell to "16 per cent of loan originations", from 18% a year earlier and 20% in 2023. Lenders are tightening on exactly this group.
- **FACE, the RBI-recognised fintech industry body, March 2026 (primary, bureau data):** borrowers with under a year of credit history received 6% of the money digital lenders lent.
- **Approvals rising 10% a year for a referral partner's users:** not found.

**Judgment.**
- **Range:** 11–30%.
- **Defensible base:** 20%, between the one filing (11%) and the founders' own book (25%). The +10% a year is kept, as it is a judgement no source can test.
- **Confidence:** medium.

**Effect alone.** 6.07×. At Kissht's 11%: 4.43×. With no yearly rise: 6.72×.

## 5. Personal and business loan size

**Founders' number.** ₹3 lakh blended (founders, 22 October). Repeat loans grow 10% a year, capped at ₹5 lakh, and top-ups are 40% of the loan.

**Evidence: what these lenders actually lend.**
- **FACE, March 2026 (primary, bureau data), average loan April–December 2025:**

  | Lender or borrower group | Average loan |
  |---|---|
  | App lenders (digital NBFCs) | ₹15,493 |
  | Other NBFCs | ₹98,056 |
  | Banks | ₹4.91 lakh |
  | App-lender borrowers with under a year of credit history | ₹5,476 |
  | 1–2 years of credit history | ₹7,455 |
  | Rural borrowers | ₹12,582 |

- **The same series for April–June 2026, via Business Today, October 2026 (secondary):** ₹18,802 for app lenders.
- **Individual lenders:**
  - Kissht ₹25,557 (prospectus, primary).
  - KreditBee about ₹30,000 (rating note, March 2026, primary).
  - Moneyview's product for people with little credit history about ₹20,000 over 8 months, and its riskiest borrowers ₹72,489 (prospectus summaries, September 2026, secondary).
- **Even good-credit fintech borrowers averaged ₹44,000 at the end of 2024** (TransUnion CIBIL, primary).
- **Small-business loans:**
  - Mudra in FY25 (secondary): Shishu ₹37,403 and Kishor ₹1.2 lakh, which together make up 96% of accounts.
  - Paytm's merchants with card machines average ₹2.05 lakh (secondary, 2024). That is the high end.
- **The founders' own 2019–22 book:** ₹10,000–25,000.

**Evidence: does ₹3 lakh fit a ₹100-a-day saver?** This is our arithmetic, built on the sources above.
- **The monthly instalment:** a ₹3 lakh loan over 18 months at 18–26% a year costs **₹19,142–20,305 a month**.
- **The income it needs:** lenders keep all instalments within about 40–60% of take-home pay (lender pages, 2026). So the loan needs **₹38,000–51,000 a month of take-home pay with no other loans**.
- **What people earn:** the Economic Survey 2024–25 puts average monthly income at **₹13,279 for the self-employed and ₹20,702 for salaried workers** (2023–24, secondary). Someone who puts aside ₹2,000–3,000 a month fits that band far better than a ₹40,000+ one.
- **The RBI rule for lower-income households (primary, January 2025):** for a household earning under ₹3 lakh a year, every collateral-free loan counts as microfinance, and all its repayments together may take at most 50% of income. At ₹25,000 a month that caps an 18-month loan at about ₹1.85 lakh. Lenders give first-time borrowers far less.

**Judgment.**
- **Range:** ₹15,000–1.2 lakh.
- **Defensible base:** ₹50,000, which blends small first personal loans with micro-business loans.
- **Confidence:** medium on the exact value. High that ₹3 lakh sits outside what lenders give this income band. The loan size is the founders' call, and this tests it; it does not re-argue it.

**Effect alone.** 2.99× (payback month 27).

| Personal + business loan | LTV/CAC |
|---|---|
| ₹25,000 | 2.51× |
| ₹15,500 (app-lender average) | 2.33× |
| ₹1.2 lakh | 4.31× |

## 6. What the lender pays

**Founders' number.** 2% of the loan, rising to 3% by year 5, with 2.5% taken back. Home 0.5%, property 1%, gold 0.5%.

**Evidence.**
- **A large loan-agent network's own page, 2026 (secondary).** Personal and business loans "1-2%". Home loans "0.20-0.25%". Property loans "0.30-0.50%". About 90% of the fee is paid after the first disbursal.
- **GroMo, August 2026 (secondary).** Personal and business loans "1% - 2.5%", with a range of 0.5–4% across partners. The fee can be taken back if the loan closes or defaults within 6 months.
- **A consultant page on lender–fintech lead deals with no credit risk (secondary, 2026):** "1 to 3%".
- **Paisabazaar, Q1 FY27 (secondary, reporting results).** ₹127 crore of credit revenue on ₹2,776 crore lent, about 4.6%. This is an upper bound: it includes credit-card fees, and its borrowers are mostly good-credit.
- **Paytm (secondary, January 2025):** 4.5–5%, but that pays for collections and covering losses too. It is not a referral fee.
- **A referral partner's fee rising from 2% to 3%:** not found.

**Judgment.**
- **Range:** 1–2.5%, flat.
- **Defensible base:** 2%, flat.
- **Confidence:** medium. High that the rise is unsupported.
- **Home and property payouts:** home 0.5% and property 1% sit at the top of the lender rates. They are kept, because they move the answer by little.

**Effect alone.** 2% flat: 6.58×. 1.5% flat: 5.44×. 1% flat: 4.31×. 2.5% flat: 7.71×.

## 7. Home and property loan sizes

**Founders' number.**
- Home ₹30 lakh and property ₹25 lakh (founders, 22 October).
- 2% of loan applications are for a home loan and 3% for a property loan.
- 45% of those applications are approved, rising each year with the approval growth (capped at 80%).

**Evidence.**

| Lender or source | What it shows | Type, date |
|---|---|---|
| Home First | Families "with a monthly income of < ₹50,000"; average loan ₹11.8 lakh; 77% of leads from outside connectors | primary, Nov 2025 |
| Aavas | Book average ₹10 lakh; new home loans ₹15 lakh; 83% of loans under ₹15 lakh | primary, May 2026 |
| Aadhar Housing | About ₹10.9 lakh | broker note, May 2026 |
| Aptus | About ₹10 lakh | call summary, FY26 |
| CRIF (credit bureau), all incomes | National average ₹32 lakh; 73% of home loans under ₹35 lakh | primary, 2025 |
| Five Star (small-business property loans) | Average ₹3.9 lakh; sweet spot ₹3–10 lakh | primary, rating note, Jul 2026 |

- **The income test** (our arithmetic):
  - ₹30 lakh over 20 years at 9.5% costs ₹27,964 a month, which needs ₹56,000–70,000 a month of income.
  - ₹25 lakh over 15 years at 13% costs ₹31,631, which needs ₹63,000–79,000.

**Judgment.**
- **Ranges:** home ₹10–15 lakh; property ₹3–10 lakh.
- **Defensible base:** home ₹12 lakh; property ₹5 lakh.
- **Confidence:** high.
- **Where the plan sits:** ₹30 lakh is the national average across all incomes, not the mass-market figure. ₹25 lakh is about 6 times what small-business property lenders lend.

**Effect alone.** 6.52× (home alone 7.43×; property alone 6.80×). Separately, at 30% approval instead of 45% (no lender figure was found either way), the plan would be 7.18×.

## 8. Fund commission (trail)

**Founders' number.** Equity 0.75% a year, debt 0.35%, blended 0.67% on an 80/20 mix.

**Evidence.**
- **Prudent, a large fund distributor (earnings calls, May and July 2026, secondary).** 0.91% for FY26. After the April 2026 rules, "gross yield settled at around 88 basis points" (0.88%), and the firm is "well poised to maintain" it.
- **Kotak MF (2026):** regular plans cost 0.5–1.0% a year more than direct plans.
- **Liquid funds (Value Research, 2026):** the regular plan costs only about 0.08% more than direct. If the 20% "debt" share is an instant-withdrawal liquid fund, the commission on it is about 0.1%, not 0.35%.
- **SEBI's 2026 fund rules (from 1 April 2026):** the fee is now a base fee, with statutory levies shown separately. No separate cut to distributor commission was found.
- **SEBI's new-investor incentive (Cafemutual, March 2026, secondary).** 1% of the first year's SIP money, capped at ₹2,000, for new investors from beyond the top 30 cities and new women investors. It excludes short-duration debt funds. This upside is not in the plan: up to about ₹190, once, for a full-year saver who qualifies. Whether a daily SIP qualifies is not confirmed.

**Judgment.**
- **Range:** equity 0.50–0.88%; debt 0.08–0.50%.
- **Defensible base:** equity 0.75% and a liquid fund at 0.10%, which blends to 0.62%.
- **Confidence:** medium.
- **Where the plan sits:** inside the evidence.

**Effect alone.** 7.62×. Low end (0.50% / 0.10%): 7.30×. High end (0.88% / 0.35%): 7.87×.

## 9. Cost per debit

**Founders' number.** ₹2 a debit, weekly, until BSE StAR MF and the fund houses confirm a daily SIP on one mandate.

**Evidence.**
- **BSE StAR MF (Cafemutual, 2016–18, secondary, old).** "Transaction charges are not applicable on mutual fund distributors". Fund houses pay ₹6–30 an order instead. No current fee schedule was found. If fund houses pay per order, some may refuse ₹100-a-day orders.
- **The new UPI merchant fee from 15 October 2026 does not apply to SIP debits** (NPCI's FAQ via Business Today, September 2026). A payment company's own fee is separate.
- **Published payment-company prices, 2026:** ₹7.50 to set up a mandate and ₹5 a debit under ₹1,000 (Zoho Payments price list, primary; Cashfree page, secondary).
- **Daily SIPs do exist.** A BSE notice from March 2025 lists a daily SIP facility for one fund house on BSE StAR MF (search summary; the notice itself could not be opened). Paytm Money, Groww and HDFC Securities offer daily SIPs, usually from ₹100 a day (Business Standard, May 2025).

**Judgment.**
- **Range:** ₹0–5 a debit.
- **Defensible base:** the plan's ₹2 weekly.
- **Confidence:** medium.
- **How much it matters:** little.

**Effect alone.**

| Debit setup | LTV/CAC |
|---|---|
| ₹0 weekly (through BSE StAR MF) | 8.07× |
| ₹5 weekly | 7.15× |
| Daily at ₹2 | 6.36× |
| Daily at ₹0 | 8.07× |

## 10. Repeat loans and top-ups

**Founders' number.**
- 70% of repeat applications are approved, and repeats happen at the same yearly apply rate once a loan is repaid.
- Top-ups go to 15% a year after 12 instalments, at 40% of the loan.

**Evidence.**
- **Kissht (primary):** repeat approval 73.54%; repeat customers hold 50.62% of loans outstanding.
- **TransUnion CIBIL, May 2025 (primary).** "Of the 20.2 million FinTech consumers in India in December 2023 … approximately 9.8 million availed new loans between January and June 2024". About half borrow again within six months.
- **Moneyview (prospectus summaries, secondary):** repeat customers rose from 42% of loans to 61% between FY24 and FY26.
- **Paytm merchant loans (primary):** repeat borrowers are "more than 50% of disbursements".
- **The founders' own book:** 30–50% of those who repaid took a second loan.
- **A top-up rate:** not found for any Indian lender.

**Judgment.**
- **Repeat approval:** 70% is inside the evidence; kept.
- **Top-ups:** a judgement; kept.
- **Confidence:** medium for repeats, low for top-ups.
- **How much it matters:** little. Repeat approval at 50% gives 7.49×; at 73.5%, 7.74×. No top-ups gives 7.61×; 30% a year gives 7.81×.

---

## The judgment

### Plan against evidence

| Case | LTV/CAC, 5 years | Pays back |
|---|---|---|
| The plan | **7.70×** | month 12 |
| Every input at the **top** of its evidence range at once | 7.71× | month 13 |
| **All ten at the defensible base** | **0.33×** (₹274 back against ₹825) | not within 8 years (0.61× at 8 years) |
| All ten at the base, founders' loan sizes kept (₹3 lakh / ₹30 lakh / ₹25 lakh) | 1.32× | month 46 |
| Personal + business funnel only at the base (apply, approval, loan size, payout); rest at plan | 1.59× | month 45 |
| Every input at the **bottom** of its evidence range at once | −0.13× | never |

The plan's answer is the evidence's best case: every input at the top of its range together, which no single source shows.

### From the plan to the evidence, one step at a time

| Step (each adds to the one above) | LTV/CAC |
|---|---|
| The plan | 7.70× |
| Cost to win ₹750 | 4.62× |
| Retention: 35% at a year, then 2.5% stop a month | 3.50× |
| Fund commission 0.62% (the debt share is a liquid fund) | 3.47× |
| Payout 2%, flat | 2.99× |
| Home ₹12 lakh, property ₹5 lakh | 2.44× |
| First approval 20% | 1.80× |
| Apply 20% a year | 1.01× |
| Personal + business loan ₹50,000 | **0.33×** |

**Checks on the result.**
- **Repeat borrowing does not rescue it.** In the model, one apply rate drives first and repeat loans, so lowering it also lowers repeats. With repeat approval at 100% and top-ups doubled, the evidence case is still 0.34×.
- **A ₹1 lakh loan gives 0.47×.**
- **To reach 3× with everything else at the evidence**, personal and business loan fees would have to be about 21 times the evidence value: about ₹2,300 a saver won over five years, against ₹111. That is close to the plan's own ₹2,802.

### The things that decide whether this works

1. **How many KYC'd users take a first loan each year.**
   - Plan: 10.5%. Evidence: 1–5%.
   - It is the product of the opt-in, applying and being approved, and it is the biggest single lever after loan size.
   - *The seed must measure, for each month's group of users:* the share who opt in to lender offers, apply, and are approved, with the lender's own records as the check. At the plan's other inputs, 3× needs about 4% taking a first loan a year.
2. **How big their loans are, which comes down to who the saver is.**
   - Plan: ₹3 lakh. Evidence: ₹5,000–25,000 for first-time app borrowers, up to ₹1.2 lakh for micro-businesses.
   - *The seed must measure:* the income and credit history recorded at KYC, and the median loan the partner lenders actually approve for these users. At the plan's other inputs, 3× needs a median of about ₹51,000.
3. **What the lender pays, after money taken back.**
   - Plan: 2% rising to 3%. Evidence: 1–2.5% flat.
   - *The seed must measure:* the fee in a signed letter from two or more lenders, and the share taken back in the first six months on real loans.
4. **The cost to win a saver who makes a first debit.**
   - Plan: ₹450. Evidence: ₹600–1,400.
   - *The seed must measure:* the cost per first-debit saver, by channel, with paid and free sign-ups shown separately, for three months running at 2,000 or more savers a month.
5. **Whether saving pays its own way.**
   - With no loans at all, the plan returns 0.31× (the evidence 0.04×). Over five years the fund commission (₹531 in the plan) barely covers the cost to serve (₹501). Tech at ₹4 a month for each KYC'd user is the largest serving line.
   - So every rupee of value comes from loans, and from loans to KYC'd users who never save: with offers to savers only, the plan falls to 3.52×.
   - *The seed must measure:* still saving at months 3, 6 and 12, the share of debits that succeed, and the cost to serve each active saver each month.

### Where the plan sits outside the evidence, plainly

- **₹3 lakh personal and business loans.** That is roughly 10–20 times what app lenders lend first-time borrowers, and it needs two to four times the income of a typical ₹100-a-day saver.
- **₹30 lakh home and ₹25 lakh property loans.** That is 2–3 times and about 6 times what mass-market lenders lend.
- **10.5% of reachable users taking a first loan each year.** That is 2–10 times what Paytm, Kissht and PhonePe show.
- **The payout rising to 3%.** No source supports it.
- **₹450 to win a saver.** That is below Groww (₹800–1,400) and below the seed's own ₹600 budget.
- **Inside the evidence:** the fund commission, month-12 retention, repeat approval and the debit cost.

None of this says the business cannot work. It says the case rests on four loan numbers that no evidence supports today, and that the seed exists to measure them:
- **If the seed measures the founders' targets** (35% apply, 30% approved, ₹3 lakh, 2%) and everything else lands at today's evidence, LTV/CAC is about 2.4× (2.9× with the payout rise).
- **If the loan numbers come in near today's evidence**, it stays below 1×.

---

## Not found

- The share of app users who apply when shown a loan offer.
- Approvals rising year on year for a referral partner's users.
- A referral payout rising over time.
- A top-up rate for any Indian lender.
- A current BSE StAR MF fee schedule.
- Whether a failed UPI AutoPay debit is billed.
- A primary-source cost per first-debit saver for a mass-market savings app.
- The SEBI document behind "73% do not stay invested more than two years".
- Payouts that affordable home lenders pay their connectors.

## How the runs were made

- **Model.** The model was imported read-only, without calling `main()` or any code that writes tables. Values were changed only in memory, through `op.OV`, and `op._CACHE` was cleared before each run. The baseline reproduces exactly: 7.70× and month 12.
- **Payout held flat.** This needed one change made outside the model. The loan-fee rise (×1.0 to ×1.5 by month 60) is fixed inside `ltv_parts`, so the script repeats `ltv_parts` with that factor set to 1 and changes nothing else.
- **Override values for the defensible base:**
  - `r12` 0.35 and `churn_late` 0.025;
  - `loan_mix(0.20)` and `approved_first` 0.20;
  - `ticket` 50,000;
  - `loan_home_ticket` 12,00,000 and `loan_lap_ticket` 5,00,000;
  - `trail` 0.0062;
  - cost to win 750, with the model adding its 10%;
  - payout factor held at 1.
- **Where the scripts are.** The run script and the CSV builder are in the session's scratchpad: `/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad/ev_runs.py` and `write_evidence_csv.py`. macOS clears that folder after a few days. The override values above are enough to repeat every run.

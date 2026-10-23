# One online saver's LTV/CAC: an independent recalculation

23 October 2026 · Agent A ("recalculate") · repo commit 8275822 · read-only review: no model, table or deck was changed.

## Summary

1. **It reconciles.** Rebuilt month by month from the inputs without the model's code, every line matches to within 0.1%: ₹3,813 returned, **7.70×**, paid back in month 12, 12.16× over 8 years.
2. **No arithmetic bug moves the answer.** The two bugs are display errors worth 0.00×: the deck's product table (A7) shows durable and vehicle loans 2.5 times too high, and the inputs table shows a 10% extra-SIP take-up the model switches off.
3. **One cost inconsistency, and the corrected figure.** The LTV view adds the 10% contingency to the cost to win but not to serving, which the company plan grosses up too (−0.10×). Corrected LTV/CAC: **7.70× with bugs only fixed; 7.60× with this fixed too.**
4. **The answer is right but narrow.** Non-savers kept on the saver's retention curve bring 54% of the LTV. Rises in payout, take-up and approval with no source add 2.4×, and fresh 30% re-draws after a rejection add 1.3×. It is also a month-1 saver who never exists, priced at the post-seed cost: the first real cohort at its own cost gives 6.0×.
5. **A careful investor's reading, with no input changed, is about 4.5×** (3.6× if a lender's "no" sticks to the person), paid back in month 18–19; separately, a ₹3 lakh loan over 18 months needs about ₹40,000–55,000 a month of income, above the folder's own evidence for this saver.

How to read this note. Three kinds of number appear, each labelled:
- **Founders' number:** an input or result in the plan.
- **Evidence:** a row in `others/research/`, cited by its ID.
- **My judgement:** my own view or an illustration I made up to size an effect. It is never a fact.

---

## 1. Line-by-line reconciliation

`recalc.py` reads every value from `others/tables/ltv_inputs.csv`. The few switches that live only in the code are restated with the file and line they come from. The script re-derives the mechanics from the engine's description (`cohort_engine.py:19-71`) and the deck's appendix A11:
- the retention curve;
- the fund balance;
- the three loan states (never borrowed, repaying, free to borrow again);
- top-ups;
- the one-off referrals with their approval;
- cards and everyday products;
- serving.

It never imports the model.

| Line (one online saver won, months 1–60) | Founders (₹) | Recalc (₹) | Gap |
|---|---:|---:|---:|
| Cost to win (₹450 + 10%) | −495 | −495.00 | 0.0% |
| Fund trail (0.67% a year) | 531 | 531.17 | 0.0% |
| Personal + business loans | 2,802 | 2,802.05 | 0.0% |
| Other lenders' loans | 884 | 884.15 | 0.0% |
| · gold | 73 | 73.04 | 0.0% |
| · loan against property | 561 | 560.70 | 0.0% |
| · home | 225 | 224.83 | 0.0% |
| · durables | 13 | 13.05 | 0.0% |
| · vehicles | 13 | 12.53 | 0.0% (rounding) |
| Cards | 18 | 18.27 | 0.0% |
| Recharge, bills, FD, NPS | 78 | 77.77 | 0.0% |
| Insurance | 0 | 0 | 0 |
| Serving | −501 | −500.55 | 0.0% |
| **LTV (revenue less serving)** | **3,813** | **3,812.86** | **0.0%** |
| **LTV/CAC** | **7.70×** | **7.70×** | **0.0%** |
| Payback month | 12 | 12 | 0 |
| 8 years: revenue / LTV/CAC | 6,642 / 12.16× | 6,642 / 12.16× | 0.0% |

Every line matched on the first full run, so there was nothing to explain away. The model's arithmetic does what its description says.

### What sits underneath the ₹3,813

All per online saver won, over 5 years, from my rebuild:

**The saver and serving**
- **Saver-months.** The average saver won saves for 21.15 months out of 60: 80% are left at month 3, 38% at month 12 and 18% at month 60.
- **Serving.** Serving is ₹23.67 a month per saver still saving: ₹5 support, ₹10 tech (₹4 × 2.5 KYC'd users) and ₹8.67 debits (₹2 × 4.33 a month).

**Loans**
- **Loans are 85.5% of revenue, not 88%.** The 88% in the brief is everything except the fund trail (87.7%). The deck itself says this correctly on p3.
- **Personal and business loans, per 100 savers won:** 32.5 first loans, 4.5 repeats and 1.4 top-ups, from 104.8 applications. Lenders pay out ₹1,15,109 per saver won.
- **The payout people actually earn is about 2.4%, not 2%.** Weighted by money lent, the month-1 saver's loans earn 2.50% gross, or 2.43% after the 2.5% clawback. The ramp from 2% to 3% is already a quarter of the way up when most loans are made.
- **First-loan approval is not 30% for long.** It is 18% in months 1–6, then 30%, 33%, 36%, 40% and 44% at months 12, 24, 36, 48 and 60. The apply rate climbs from 35% to about 41% a year by year 5. The summary states only the year-1 rates.

**Who earns it**
- **Loans to the 1.5 KYC'd users who never save bring ₹2,196, or ₹2,069 after their tech cost.** That is 54% of the LTV.
- **Property and home loans bring ₹786, 18% of revenue.** They come from 2.2 property loans and 1.5 home loans per 100 savers won.
- **The cost to win is small against the money it brings to lenders.** It is 0.43% of the personal and business money lent through the saver.

---

## 2. Findings, ranked by effect

Each row changes one thing from the plan. "Effect" is the change in 5-year LTV/CAC from 7.70×.

| # | Finding | Where | LTV/CAC | Effect | Kind |
|---|---|---|---:|---:|---|
| F5b | Non-savers reachable only in their first 3 months | `online_plan.py:205, 339`; `cohort_engine.py:484-491` | 3.64× | −4.06 | judgement (severe) |
| F16a | No rises without a source: payout flat at 2%, take-up and approvals flat | `online_plan.py:331`; `cohort_engine.py:447-450` | 5.33× | −2.37 | hidden assumption + judgement |
| F17b | Loans sized to what ₹30,000 a month can repay (personal/business ₹2.25 lakh, home ₹15.5 lakh, property ₹11.3 lakh) | inputs; test of arithmetic | 5.45× | −2.26 | affordability test |
| F12 | ₹450 comes from better conversion (1 in 3.75 save), so reach is 1.875, not 2.5 | `online_plan.py:52, 135`; deck p5 | 5.96× | −1.74 | inconsistency (linked inputs) |
| F1a | First real cohort: joins at launch (month 4) at the seed's ₹600 (₹660 with contingency) | `online_plan.py:49, 52` vs `:332` (row 0 = a month-1 joiner), `:346` | 6.02× | −1.69 | inconsistency |
| F1b | ...the other way: a saver won in month 19 at ₹450 | same | 9.60× | +1.89 | inconsistency |
| F10c | Take-up and approval held flat at the stated 35% and 30% | `cohort_engine.py:447-450` | 6.17× | −1.54 | hidden assumption |
| F5a | Non-savers reachable on the savings-app curve (52% at month 3, 24% at 12), not the savers' 80%/38% | `online_plan.py:132-136, 205, 339` | 6.21× | −1.49 | judgement |
| F17a | Personal + business loans sized to ₹30,000 a month: ₹2.25 lakh | test of arithmetic | 6.29× | −1.42 | affordability test |
| F4 | Every quoted payout and trail includes 18% GST | deck p2 ("quoted before GST") | 6.37× | −1.33 | judgement (basis unconfirmed) |
| F7 | A user a lender rejects stays rejected, instead of a fresh 30% chance every month | `cohort_engine.py:476-487` | 6.38× | −1.33 | hidden assumption |
| F11 | Payout stays at 2% (no rise to 3%) | `online_plan.py:331` | 6.58× | −1.13 | judgement (no source) |
| F8 | No payout on repeat loans and top-ups to a lender's own borrower | `cohort_engine.py:520-523, 560` | 6.75× | −0.95 | judgement |
| F13 | Missing variable costs, my illustration: ₹250 a loan, ₹30 an application, one ₹20 e-KYC re-check at year 2, ₹5 support for non-savers | not in `online_plan.py:338-342` | 7.00× | −0.70 | missing cost (my numbers) |
| F9b | Clawbacks at 10% of payouts | `ltv_inputs` taken_back; XL-47 | 7.27× | −0.44 | judgement |
| F6 | Support for non-savers, ₹5 a month while reachable | `online_plan.py:340` | 7.38× | −0.32 | missing cost |
| F3 | Fees arrive 2 months after they are earned (the company model's own lag) | `online_plan.py:56, 246` | 7.39× | −0.31 | timing (payback month 14) |
| F9a | Clawbacks at 5% (top of the plan's range) | inputs | 7.56× | −0.15 | judgement |
| F2 | Serving carries the 10% contingency, as the cost to win does | `online_plan.py:236` vs `:340, :346` | 7.60× | −0.10 | **inconsistency (mechanical)** |
| — | The 2.5% clawback is applied to personal/business payouts but not to gold, property, home, durables or vehicles | `cohort_engine.py:365-366` vs `:560` | 7.66× | −0.04 | inconsistency |
| — | Deck A7 multiplies durable and vehicle loans by 2.5 while labelling them "savers only" (₹33 and ₹31 instead of ₹13 and ₹13); its rows add to ₹4,352, not ₹4,313 | `others/ltv/build_ltv_deck.py:881-882` | 7.70× | 0.00 | **bug (display)** |
| — | `ltv_inputs.csv` shows the extra equity SIP at 10% take-up; the model sets it to 0 for the 80/20 saver | `ltv_inputs.csv:99` vs `online_plan.py:73` | 7.70× | 0.00 | **bug (display)** |
| — | Brief: "loans are 88% of revenue"; they are 85.5% | brief vs deck p3 | — | 0.00 | wording |

Combined cases (judgement, no input changed):

- **F14 = F2 + F3 + F5a + F6 + F10c: 4.51×, paid back in month 18.** It holds the stated rates flat, counts the cash when it arrives, serves everyone at the plan's own cost and applies the contingency to serving. It also puts non-savers on a savings-app curve.
- **F15 = F14 + F7: 3.64×, paid back in month 19.**
- **F16b = F16a at the seed's ₹660: 4.00×.** With no unsourced rises the joining month stops mattering, so this is what a seed-era saver is worth on the stated rates.

All rows are in `recalc_findings.csv`; month-by-month lines for the plan are in `recalc_monthly.csv`.

---

## 3. The questions asked, one by one

### Is the ₹495 cost to win for the same population that earns the revenue?

**On people, yes.** At ₹450, the founders' funnel (deck p5) buys 5 sign-ups at ₹70 and 2.5 identity checks at ₹40. Revenue counts the 1 saver plus the 1.5 KYC'd non-savers from those same 5 sign-ups. The 2.5 who never finish KYC earn nothing and cost nothing. Nobody is counted twice.

**On timing, no.** The revenue is for a saver who joins in business month 1 (`online_plan.py:332`, row 0 of the profile). But:
- the business launches in month 4 (`:49`);
- seed savers cost ₹600 (`:52`);
- ₹450 applies only from month 19.

The deck says so ("the cautious saver", p2), but the pairing is still a saver who never exists. Paired honestly:
- the first real cohort at its own cost gives **6.02×** (F1a);
- a month-19 saver at ₹450 gives **9.60×** (F1b).

The month-19 figure is higher only because of the payout ramp and the yearly growth factors; without them both are 5.33× at ₹495 (F16a).

**On the funnel, a hidden link.** ₹450 with 2.5 KYC'd users per saver works only if each sign-up gets cheaper (₹100 to ₹70) while still only 1 in 5 starts saving. If the saving comes from better conversion instead (1 in 3.75), reach falls to 1.875 and LTV/CAC to **5.96×** (F12). The Monte Carlo links the two; the base case does not.

### Do the 2.5 KYC'd users follow the saver's retention curve? Is that fair? Are non-savers double-counted?

**Yes, exactly the saver's curve.** The model takes the saver's loan profile and multiplies it by 2.5 (`online_plan.py:205, 338-339`). The loan states run on the saver's survival (`cohort_engine.py:484-491`). So the 1.5 non-savers' reach falls to 80% at month 3, 38% at a year and 18% at 5 years, because somebody else keeps saving.

**Fair? A judgement, and the weakest link.** A non-saver has no saving to stop, so the curve measures a different behaviour. The folder's own evidence points the other way:
- a listed lending app had monetised 8% of its registered users (LEND-04);
- fintech apps' daily-to-monthly use is 22% (XF-22).

They might also be more credit-hungry than savers, which the plan cannot tell. Effects:
- savings-app curve: **6.21×** (F5a);
- first 3 months only: **3.64×** (F5b);
- savers only: **3.52×**, the founders' own lever (F5c).

**Not double-counted, but under-costed.**
- The saver is one of the 2.5. Fund, cards, products, durables and vehicles count once; only the loan lines count 2.5 times.
- Serving charges tech for all 2.5 but support and debits for the saver only. That is right for debits but not for support, because borrowers raise queries. Support for the non-savers at the plan's ₹5 a month costs **0.32×** (F6).

### How are the payout ramp and the clawbacks timed?

**The ramp** runs by business month: straight from 2% in month 1 to 3% in month 60, held after (`online_plan.py:331`). It applies to the month the loan is paid out. For the month-1 saver, the money-weighted payout is 2.50% gross and 2.43% after clawbacks; for a month-19 saver it is 2.67%.

The rise has no source (the inputs audit says so). The folder's rate cards are 1–2.5%, up to 3% (XF-01, LEV-009). Without the rise: **6.58×** (F11).

**Clawbacks** are a flat 2.5% cut on every personal and business payout, taken in the same month as the payout (`cohort_engine.py:560`).
- **Timing.** In practice they land up to 6 months later (XL-47). That barely matters over five undiscounted years.
- **Level.** This matters more. The folder notes that a third of this segment's borrowers miss a payment and that small-loan defaults peak at 6–9% (XL-47's note, MAC-03), which can push clawbacks well above 2.5%. At 5%: **7.56×**; at 10%: **7.27×** (F9).
- **Missing lines.** No clawback is applied to gold, property, home, durable or vehicle referrals (`cohort_engine.py:365-366`): −0.04×.

### GST, and when the cash arrives

**GST.** The deck says "Fees are quoted before GST and TDS" (p2). No lender letter or fund-house schedule in the folder confirms that basis.
- If the payouts and trail are quoted including 18% GST, every rupee of revenue is 1/1.18 of the quote: **6.37×**, payback month 14 (F4).
- This is the cheapest fix in the list: one line in each partner agreement.

**TDS (tax withheld at source on commissions)** is not a cost, but it is cash locked away until the tax return. A loss-making company carries it as a receivable for a year or more. GST paid on marketing and tech is credited against GST collected, so it is timing, not cost.

**Cash timing.** The company model assumes fees arrive 2 months after they are earned (`online_plan.py:56, 246`); the LTV view books them on the day. With the lag, the last two months fall outside five years: **7.39×**, and payback moves from **month 12 to month 14** (F3).

### Missing costs

These are not in the one-saver view at all (`online_plan.py:338-342`):

- **Grievances.** As each lender's lending service provider, the app needs a grievance officer and must handle borrowers' complaints.
- **Key-facts sheets.** A key-facts statement must go with every loan.
- **Cooling-off exits.** Borrowers who exit in the cooling-off period trigger clawbacks.
- **Fraud.** Identity fraud and mule accounts usually mean a full clawback.
- **Credit checks.** Bureau checks may be needed to pre-screen 1.05 applications per saver won.
- **KYC re-checks.** Customer records need periodic re-checks.

My illustration totals ₹348 per saver won, or **−0.70×** (F13). The made-up costs are:
- ₹250 a loan across 0.57 loans per saver won (₹142);
- ₹30 an application (₹31);
- one ₹20 e-KYC re-check at year 2 (₹16; the folder's Aadhaar price is ₹20, TC-35);
- ₹5 support for non-savers (₹159).

Each ₹100 of servicing per loan costs about 0.11×.

**Fixed costs belong in the company plan, not here.** Lender integration and compliance staff are company costs:
- the company model carries compliance at ₹10 lakh a year in the seed and ₹25 lakh after;
- it has no separate lender-integration line.

**First-loss cover is assumed to be zero.** It is not a missing cost in the plan's design. It is a risk to the design: see the investor challenges below.

### Can a ₹100-a-day saver repay these loans?

My arithmetic uses standard instalment maths. "Share of income to repayments" is what lenders call FOIR; 40–50% is the usual ceiling. Full table: `recalc_affordability.csv`.

| Loan (founders' size) | Rate a year (my range) | Monthly instalment | Income needed at 50% / 40% | Instalment ÷ ₹2,000 saved a month |
|---|---|---:|---:|---:|
| Personal + business ₹3 lakh, 18 months | 18% | ₹19,142 | ₹38,300 / ₹47,900 | 9.6× |
| | 24% | ₹20,011 | ₹40,000 / ₹50,000 | 10.0× |
| | 30% | ₹20,901 | ₹41,800 / ₹52,300 | 10.5× |
| | 36% | ₹21,813 | ₹43,600 / ₹54,500 | 10.9× |
| Home ₹30 lakh, 20 years | 8.5–12% | ₹26,035–33,033 | ₹52,100–66,100 / ₹65,100–82,600 | 13–17× |
| Loan against property ₹25 lakh, 15 years | 11–18% | ₹28,415–40,261 | ₹56,800–80,500 / ₹71,000–1,00,700 | 14–20× |
| Loan against property ₹25 lakh, 10 years | 11–18% | ₹34,438–45,046 | ₹68,900–90,100 / ₹86,100–1,12,600 | 17–23× |

**Against the folder's own income evidence:**
- a typical customer earns ₹20,000–40,000 a month (IV-04);
- urban self-employed average ₹23,012 (NG-005);
- in Delhi, ₹34,868 (NG-006);
- a daily-savings app targets ₹30,000–70,000 (NG-031).

**What that means for the ₹3 lakh loan:**
- On ₹30,000 a month with no other debt, the largest 18-month loan at 24% is ₹1.8–2.25 lakh. On ₹23,000 it is ₹1.4–1.7 lakh.
- Under RBI's microfinance rule (REG-077), a household earning up to ₹3 lakh a year (₹25,000 a month) may spend at most half its income on all loan repayments. That caps it near ₹1.9 lakh at 24% over 18 months.
- So a ₹3 lakh average over 18 months means the approved borrowers earn ₹40,000–55,000 a month or more: the top of the typical customer's band.
- The 30% approval rate and the ₹3 lakh size are drawn separately in the base case. In practice a lender meets this segment with a smaller loan or a "no", not both at full size.

**Home and property loans:**
- The ₹30 lakh home loan needs ₹52,000–90,000 a month. It also needs a deposit of at least ₹3.3 lakh against a home worth ₹33 lakh or more.
- After five years a saver still saving holds about ₹1.2 lakh (my rebuild).
- The ₹25 lakh property loan needs ₹57,000–1,13,000 a month and a property worth roughly twice the loan (my judgement on the usual loan-to-value).

**What this does to the answer.** The loan sizes are the founders' decision, so this is a test of what must be true, not a different choice. If lenders size loans to what ₹30,000 a month can repay at half of income:
- personal and business loans of ₹2.25 lakh give **6.29×** (F17a);
- adding home at ₹15.5 lakh and property at ₹11.3 lakh gives **5.45×** (F17b).

### Is anything counted per saver won that should be per saver still saving, or the reverse?

Every revenue and serving line is per saver still saving (or per user still reachable), and the cost to win is per saver won. That part is right.

The real mismatch is the reverse case. The 1.5 non-savers are a fixed count per saver won, but their reach is tied to the saver's continued saving, a behaviour they do not have (F5). One smaller point: the model applies tech only while the saver's curve says "reachable". A KYC'd user's records still have to be kept after that, so a small tech or storage cost per user remains. It is too small to move the answer.

### One arithmetic consequence of a founders' decision (not re-argued)

The opt-in is counted inside the 35% apply rate, and the deck says at least 35% of KYC'd users must opt in.
- **At exactly 35% opt-in, every user who opts in must apply every year.** At 50% opt-in, 70% of them must apply.
- **The model's yearly take-up rise pushes the apply rate to about 41% by year 5,** above the stated minimum opt-in.
- Holding the apply rate at 35% (take-up flat) gives **7.04×** (F10a). F10a also flattens the other products' take-up, which is tiny.

---

## 4. Judgement

### The corrected number

- **Bugs only, inputs unchanged: 7.70×.** The two bugs are display errors (deck A7, the inputs table) and move nothing.
- **Fixing the one mechanical inconsistency as well (contingency on serving): 7.60×**, still paid back in month 12. The line that moves is serving: −₹501 becomes −₹551, and LTV goes from ₹3,813 to ₹3,763.
- **Adding the missing 2.5% clawback on other lenders' loans: 7.56×.**

The founders' 7.7× is the true output of their model on their inputs. Nothing in the arithmetic needs to be retracted.

### The five mechanics that decide the answer

1. **Who can be offered a loan.** 2.5 KYC'd users per saver won, with the 1.5 non-savers kept on the saver's curve, bring 54% of the LTV. The range is 3.5× (savers only) to 7.7×; any realistic curve for non-savers lands between 3.6× and 6.2×.
2. **Money lent per reachable user.** ₹3 lakh × 24.5% applying a year for personal or business loans, with a 30% approval re-drawn every month, gives ₹1.15 lakh lent per saver won. If a lender's "no" sticks to the person: 6.38×. If loans are sized to the folder's incomes: 5.5–6.3×.
3. **The three rises without a source.** The payout goes from 2% to 3% (2.43% earned on average), take-up rises 5% a year and approvals 10% a year. Together they are worth 2.4× (7.70× to 5.33×). The summary does not mention the last two.
4. **The cost to win and which saver it buys.** ₹495 is the post-seed cost paired with a month-1 saver. The real first cohort at ₹660 is worth 6.0×, and the ₹450 holds reach at 2.5 only if sign-ups get cheaper rather than convert better.
5. **Retention.** 38% still saving at a year, already tested by the founders (5.1–9.0×). It counts twice, because the non-savers ride on the same curve.

### What a careful investor would challenge

**How the base case is built**
- **The headline saver does not exist.** It joins before launch and is paired with a later saver's cost. Lead with a real cohort: 6.0× at the seed's cost, or 5.3× on the stated rates with no rises.
- **Half the value comes from people who never saved.** It stays reachable because somebody else keeps saving. The seed has to measure non-savers' reach and opt-in directly.
- **A lender's "no" is treated as a fresh 30% chance every month.** On these mechanics a persistent applicant is almost certain to be approved eventually. In my check, with no one stopping, 60% applying a year and a fixed 50% approval, 97% had a loan within 8 years; if the "no" sticks to the person, the cap is 50%.
- **The summary states year-1 rates.** The model then raises approvals, take-up and the payout every year to year 5, with no source for any of the three. The year-5 apply rate also outruns the stated minimum opt-in.

**Whether the loans are real**
- **Loan size against income.** A ₹3 lakh loan over 18 months is about 10 times what the saver puts aside each month, and needs about ₹40,000–55,000 a month of income. The folder's own evidence puts the typical customer at ₹20,000–40,000. Home and property loans need ₹52,000–1,13,000 a month. Between them they are 18% of revenue.
- **The cost to win against the money it unlocks.** The cost to win is 0.43% of the money lent through the saver. A listed digital lender spends 1.9–2.9% of what it lends on marketing and sourcing (LEND-03). Either this app is 5 times more efficient, or the funnel is too generous.
- **No first-loss cover.** The plan earns a pure referral fee and assumes the lender carries all the risk. The folder's own evidence shows how large a cover can be: one large lending app's first-loss expense was 3.4% of the loans it covered (LEV-060), more than the 2.43% payout. Whether this segment's lenders will pay 2–3% for thin-file referrals without one has not been asked in writing.

**What is not yet in writing or not counted**
- **The tax basis of every payout.** GST-inclusive or not is a 1.3× question, settled by one sentence in each agreement.
- **Variable costs per loan.** Grievances, key-facts sheets, disputes and fraud checks are zero today. Each ₹100 per loan costs about 0.11×.

**My overall view.** The model is careful and its arithmetic is sound. The 7.7× is the top of what it can honestly show, not the middle. Count only what is stated, served and paid in cash, and do not let the non-savers ride on the saver's curve: the same model gives about 4.5×, paid back in month 18. That still clears the 3× line, and the gap is almost entirely the loan funnel the seed is meant to measure.

---

### Files

- `recalc.py`: the independent rebuild. Run it from the repo root with `~/.cortado-venv311/bin/python others/reviews/2026-10-23_ltv_cac_check/recalc.py`.
- `recalc_reconcile.csv`: the line-by-line reconciliation.
- `recalc_findings.csv`: every finding with its LTV/CAC, effect and payback month.
- `recalc_affordability.csv`: instalments, the incomes they need, and the largest loan at each income.
- `recalc_monthly.csv`: one saver, months 1–96, every line.

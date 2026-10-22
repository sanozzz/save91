# Four structural levers: evidence summary

Researched on 30 Sep 2026. Every number below comes from a row in `levers.csv` (LEV-001 to LEV-071), where you'll find the population, date and source for each one. Figures marked **derived** are my own arithmetic on disclosed numbers. Figures marked **judgment** are my own picks where no source gives a number.

## Lever A: the app provides a 5% default-loss guarantee (DLG)

No source publishes the fee a lender pays an LSP with a DLG next to the fee it pays one without. The two best proxies are both derived from primary filings:

| Input (% of disbursal unless stated) | Low | Base | High | Evidence |
|---|---|---|---|---|
| LSP fee **without** DLG (origination only, no servicing) | 1.0 | 1.5 | 3.0 | Direct selling agents (DSAs) get 1–3% from NBFCs and 0.5–1.5% from banks (LEV-009). For Paisabazaar, revenue ÷ disbursal is at most 4.7%, and that figure includes card fees (LEV-065). |
| LSP fee **with** 5% DLG + servicing | 4 | 7 | 10 | Moneyview fees are 13.3% of average off-book assets under management (AUM) per year, about 11% of partner disbursal (derived, LEV-059). The equivalent figure for Kissht is 17.4% (LEV-064). An anonymous blog puts it at 2.5–4.5% (LEV-008, unverified). |
| DLG losses actually paid | 3.0 | 4.5 | 5.0 (cap) | Moneyview paid 3.40% of DLG disbursal in FY26 and 2.85% in FY25 (RHP, LEV-060). Thin-file loans of ₹10–50K reach 6–7% at 90+ days past due (DPD) (LEV-066), so the cap probably binds. |
| Cash locked as DLG collateral | 4.5 | 5 | 5 | Moneyview posted 4.5–4.8% of DLG disbursal as lien FDs (LEV-002). Its DLG outstanding is 44% of net worth (LEV-003). |
| Borrower APR / processing fee | 25% / 2% | 28–30% / 3–4% | 36%+ / 5.5% | Moneyview's on-book yield is 27.6% (LEV-062). Kissht averages 30.7% and charges up to 36%. KreditBee's APR runs 17–50% (LEV-011–013). |
| Partner lender's cost of funds | 7.8% | 8.5% | 8.9% | Large NBFCs (LEV-068). Digital-lender NBFCs pay 13.3–14.7% (LEV-015, LEV-062). |

**What the numbers say (derived):** at base, the DLG route earns about 7% gross and loses about 4.5% to defaults, leaving roughly 2.5%. Without a DLG the app earns about 1.5%, so the DLG adds only about 1 point of disbursal. That comes on top of servicing costs and about 5% of each disbursal tied up as collateral. The lever works only if losses stay well below the 5% cap. Moneyview manages that with borrowers earning about ₹47k a month.

## Lever B: the app runs its own NBFC from year 3

| Input | Low | Base | High | Evidence |
|---|---|---|---|---|
| Cost of funds | 12% | 14% | 16% | Jupiter's NBFC Amica pays 11.5–12.5%, helped by loans from its parent; it is rated BB (LEV-028). Kissht pays 13.3–13.7% at A- (LEV-015). Moneyview's NBFC paid 14.44% in FY25 and 14.74% in FY26 (LEV-062). Stashfin's NCD coupons run 9.85–14.5% (LEV-025). The 16% high is judgment. |
| Opex, % of average book | 9% | 12% | 16% | KreditBee 9.6%, Stashfin 8.8%, Kissht 14.5–16.1% (LEV-018, -019, -026). |
| Credit cost, % of average book | 7% | 9% | 12% | KreditBee 7.7%, Groww 7.1%, Kissht 8.5–9.0%. Stashfin loses 9.9% of disbursal and Amica 8.8% (cumulative). CRIF data puts 90+ DPD at 6–9.5% (LEV-021–029, -066). |
| Debt/equity (actual, not regulatory) | 1x | 2x | 3x | Peers run at 1.1–2.1x and Moneyview's NBFC at 3.2x. Rating downgrade triggers sit at 3–3.5x (LEV-023, -024, -063). The 15% CRAR minimum doesn't bind: peers hold 24–48%. |
| Yield on loans | 25% | 28% | 30% | LEV-062, LEV-064 |
| Time to licence | 12 mo | 12–18 mo | 36+ mo | MobiKwik took about 12 months, starting from scratch (LEV-069). Groww took about 23 months (LEV-029). PhonePe has applied three times since 2021 without approval (LEV-070). |
| Equity at entry | ₹10 cr | ₹15 cr | ₹100 cr+ | The legal minimum net owned fund is ₹10 cr, and MobiKwik put in ₹9.99 cr. Amica received about ₹120 cr and Groww about ₹678 cr (LEV-028, -029, -069). |

**What the numbers say (derived):** at base, a small own-book NBFC loses about 2% of its book a year. The arithmetic: 28% yield, minus 14% cost of funds on the two-thirds that is debt, minus 12% opex, minus 9% credit cost. The precedents look the same. Amica returned -2.7% on managed assets and Groww went from -6.3% to +0.7%. Only lenders above ₹5,000 cr earn 4–5% (KreditBee, Kissht). Paytm decided in May 2026 not to seek an NBFC licence at all (LEV-070).

## Lever C: add digital gold as a savings option

| Input | Low | Base | High | Evidence |
|---|---|---|---|---|
| Distributor commission, buy side only | 1.0% | 1.5% | 2.4% | The only published figure is "Jar earns ~2.4%", from a case study (LEV-036, unverified). Augmont's DRHP confirms partners earn "commission per transaction" but gives no rate (LEV-071). SafeGold's own gross margin is only about 0.44% (LEV-035). |
| Buy-sell spread (the saver pays it) | 2% | 3% | 5% | Plus 3% GST on purchases (LEV-037). That means about 5–6% round-trip cost to a saver. |
| Custody cost to the app | 0 | 0 | 0 | Storage is free for 5 years, then charged to the customer. Sources disagree on the fee, 0.03% vs 0.3% (LEV-038, contradicted). |
| Minimum ticket | ₹1 | ₹10 | ₹10 | LEV-039 |

- **Jar FY25 (LEV-033/034):** revenue was ₹2,447.8 cr and purchases ₹2,333.6 cr. The gap is ₹114.2 cr, or 4.67% of revenue. No accessible source discloses the change in inventory. Jar became a *principal* in FY25, which is a different business from distribution. Its ₹208 cr "operating revenue" is a company-defined figure that **cannot be reconciled** with the RoC filing.
- **Market size:** digital gold bought via UPI averaged about ₹2,500 cr a month in Jun–Aug 2026, up 110% year on year in August (WGC/NPCI, LEV-044).
- **Jar usage:** the average user saves 22 times a month, and Jar handles 1M+ transactions a day. That implies about 7% of registered users are active savers (derived, LEV-040). Jar publishes no average daily amount.
- **Regulation:** press reports from 17–18 Sep 2026 say the Finance Ministry is consulting on treating digital gold as a security, with joint RBI-SEBI oversight and 1:1 backing. There is no official document, so this is unverified (LEV-041). SEBI-registered brokers and advisers are already barred from selling it. I found no bar on AMFI-registered MF distributors (LEV-042). No rule prohibits rewards today (LEV-043), but that could change if gold becomes a security.

## Lever D: widen to all blue-collar workers through employers

| Input | Low | Base | High | Evidence |
|---|---|---|---|---|
| Staying 12 months with one employer | 30% | 45% | 60% | TeamLease and Quess each see about 21–22% of headcount leave per quarter (derived from gross hires vs net change, LEV-048, -053). Deloitte finds an average tenure of 21 months and that 69% of hires are temporary (LEV-049). |
| Opt-in take-up among covered employees | 1% | 5% | 15% | UK payroll saving drew 1% under opt-in vs 53% under auto-enrol (LEV-054). Refyne reported 50–70% take-up of earned wage access, but that is a 2021 company claim for a liquidity product, not savings (LEV-055). **Base and high are judgment.** |
| Wage | ₹13k | ₹18.5k | ₹25k/mo | Delhi's unskilled minimum is ₹18,456, per the 15-Apr-2025 order, the latest on the official site (LEV-051). Staffing firms bill about ₹25.6–32.1k per associate including statutory costs (derived, LEV-047, -052). Wages grow 5–6% a year (LEV-050). |
| Employer-channel CAC | — | — | — | Not published by anyone (LEV-057) |

- **Size:** Indian Staffing Federation (ISF) members employ 1.91M flexi staff (FY26). TeamLease's general staffing has 2.9 lakh associates and Quess 4.69 lakh. EPFO had 7.37 cr contributing members in FY24 (LEV-046, -047, -052, -058).
- **SEBI payroll MF circular (LEV-045):** it is **still a draft** as of 30 Sep 2026. I checked SEBI's own circular list up to 9 Sep and found no final version. The draft covers "listed and EPFO registered companies" and AMCs, requires employee opt-in, and gives AMFI the job of setting the details. Staffing firms would qualify as employers. Gig platforms would not.

## Where the evidence contradicts the brief

1. **Cost of funds for a new NBFC:** A-minus digital lenders pay 13.3–14.7%. Only a parent-subsidised BB NBFC reaches the 11–12.5% end. Use a 14% base, not 11–12%.
2. **15% CRAR:** actual leverage is 1–3x debt/equity, not the roughly 5.7x a 15% CRAR would allow.
3. **Jar ₹208 cr:** it cannot be rebuilt from the filing. Revenue minus purchases is ₹114 cr.
4. **DLG:** the actual payout at Moneyview (3.4%) is below the cap, but for gig-worker borrowers the full 5% should be assumed lost.
5. **Delhi minimum wage:** a widely cited ₹20,358 is not supported by the official page, which shows ₹18,456.

## What I could not verify

- A published comparison of LSP fees with and without a DLG. Moneyview's RHP does not split partner fees or separate partner disbursals from its own NBFC's (the ~11% is an estimate).
- Jar's change in inventory, what makes up its ₹208 cr, the share of users saving daily, and average daily amounts.
- Any digital-gold distributor commission from a filing. The storage fee after 5 years (sources disagree).
- Market prices for NBFC shells. The only figure is one asking price: a ₹60 lakh premium, with a net owned fund below the ₹10 cr minimum.
- Blue-collar attrition as reported by any company (only derived figures exist). Employer-channel CAC and active-user rates for Refyne, Jify, SalarySe or Minvest.
- Whether SEBI's payroll circular has been finalised since 9 Sep 2026. Any official digital-gold framework document.

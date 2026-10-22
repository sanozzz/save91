# Investment committee memo: Save91 / SaveMore, $0.5M seed (lead)

**Date:** 21 October 2026 · **Reviewer:** partner, India early-stage fintech fund (independent; did not build the work) · **Materials:** plan of record "online v4" (21 Oct) and the folder's research. No web research. Where I rely on general knowledge I say so.

**Short names.** v4 = `online/Online_model_v4` (printed page numbers). LTV = `ltv/LTV_CAC_deck`. Seed = `seed/Seed_Plan_investor`. Memo = `memo/Bachatt_teardown_memo`. IDs such as XF-01 are rows in `research/*.csv`. **[V]** = verified (I recomputed it with `model/ltv_book.py` / `model/online_plan.py`, or read it off the row). **[S]** = suspected (direction clear, size not proven). LTV/CAC = what one saver brings in over 5 years, less the cost of serving them, divided by the cost to win them (undiscounted).

## Recommendation

**Do not lead on these materials. We would lead a restructured seed (invest with conditions, section 8).**

The seed is cheap and well measured. The team is analytically strong and has run a lending business before. But the plan's base case sits 3–10× above the folder's own evidence on the inputs that carry it. The product is one the main competitor already runs with about 30× the capital.

## Findings, ranked

| # | Sev. | Finding | Tag |
|---|---|---|---|
| F1 | P1 | The loan funnel carries the case, and its four main inputs (apply rate, reach to non-savers, loan size, fee rise) are founder judgement above all the folder's evidence. On moderate evidence: 0.93× per saver, and the company is never EBITDA-positive in 8 years. | V |
| F2 | P1 | ₹450 buys ₹83,867 of loans per saver: 0.54% of money lent, against Moneyview's 1.9–2.9% (LEND-03). The cost to win or the loan volume is off by about 4×. | V / S which |
| F3 | P1 | No wedge: Bachatt already serves both saving and borrowing. The pitch ("save 6 months, see your loan offer") contradicts the model, which lends from month 1 to everyone who finished identity checks. | V |
| F4 | P1 | A loan-referral business: loans are 76% of 5-year company revenue, the fund fee 14%. The unicorn yardsticks do not apply. | V |
| F5 | P2 | "Today's evidence" is a mislabel; the input audit predates the final loan inputs; "98 of 100 futures" is not odds. | V |
| F6 | P2 | No per-debit payment cost at 20 debits a month; the folder's 2 Oct costing found it made the saver loss-making. | V / S size |
| F7 | P2 | The cost to win is unmeasured; the nearest benchmark is ₹796–1,374, mostly organic (TB-18). | V |
| F8 | P2 | Dependence on lender fees and on rate, repayment and consent rules. | V / S impact |
| F9 | P2 | Two founders on $1,000 a month; no growth operator; loan inputs raised after the 18 Oct review. | V |
| F10 | P3 | Floor: with no loans, the savings core returns 1.47× at ₹450, 1.10× at ₹600. | V |

## 1. Thesis, and whether we believe it

**The thesis.** India's self-employed put ₹100 a day by UPI Autopay into mutual funds held in their own name. The app holds no money and earns the distributor's fee, 0.67% of the balance a year. The daily-saving habit then becomes the cheapest place to refer partners' loans, insurance and cards. Those referral fees carry the economics: ₹1,249 of the ₹1,972 one online saver brings in over five years (LTV p3) [V].

**Do we believe it? Half.** The pattern (saving builds trust, then cross-sell) is real: GCash turned a wallet into a lender (CMP-07). The folder's own line, "savings is the hook, credit is the business" (Memo §2), is right. I do not believe the size of the loan funnel (F1, F2). I do not believe this team wins the hook against Bachatt (F3).

**Why now.** Real: daily UPI mandates are allowed (REG-048), fund debits up to ₹1 lakh need no second authentication (REG-049), referral fees are clean under the 2025 lending rules (REG-011), and the category is proven (Bachatt's $12M Series A, BAC-01; Jar profitable for two quarters, JAR-06). The same facts make the lane crowded.

**Why this team.** In 2019–22 the founders ran a lending business with platform partners. Approval was about 25%, 30–50% of borrowers borrowed again, tickets were ₹10–25k, and an applicant cost under ₹150 (XF-24; brief slide m09). That is the right muscle for lender negotiation, and the folder shows rare rigour. The gaps:
- no consumer-growth operator, in a business decided by the cost to win;
- the CEO covers growth, partnerships, fund-raising, compliance, finance and the doorstep pilot (Seed p6);
- no founder bios in the folder;
- the plan is volatile. v4 replaced the offline plan in four days. After the 18 Oct review called v3's 18% apply rate about 5× the evidence, v4 raised it to 35% and added 2.5× reach (`INVESTMENT_REVIEW_v4_status.md`, row F06) [V].

**Why this wedge.** Weak.
- Bachatt already runs the full v4 product (`story/BACHATT_PROPOSITION.md`; XL-12):
  - a daily SIP (a fixed regular investment into a fund) from ₹51–100;
  - loans up to ₹5 lakh through nine partners;
  - cards;
  - an AI assistant, "Saathi".
- Its founders include an ex-BCG partner and an ex-OYO revenue head. It has raised $16M (QM-45) and has 3M users (BAC-02).
- PhonePe sells ₹10-a-day saving built with Jar (SAV-08).

v4's 18-month roadmap rebuilds Bachatt's live product with $0.5M. The Memo concludes "our room is depth". v4 has no depth feature that Bachatt lacks.

## 2. Market and customer

**The pool.** 7 crore urban self-employed with a 20% cap: 1.4 crore savers (`online_plan.py` POOL, CAP). The PLFS arithmetic holds (6.5–7.8 crore, prior review F14). But the cap counts *savers*, and each saver takes five *sign-ups*, so a 20% cap means the whole pool signs up.
- Grow-fast needs 5.45 crore online sign-ups by month 96, which is 78% of the pool [V].
- The profitable path needs 74 lakh (11%), which is plausible.

**Who the customer is: three different people.**
1. **The saver.** They need a smartphone, UPI, PAN and ₹2,000 a month to spare. That is 9% of the ₹23,012 urban self-employed mean, a gross mean that excludes zero earners (NG-005).
   - The one field interview describes shopkeepers who save ₹200–500 a day *in cash* with a bank collector they trust. Ninety per cent or more is cash, by habit, though 9 in 10 have UPI (IV-03 to IV-08, IV-14).
   - v4 asks them to change three things at once: cash to UPI, a person to an app, a deposit to an 80%-equity fund.
   - The person who converts online looks like Bachatt's merchant on ₹30–70k a month (BAC-05). Paytm, PhonePe and BharatPe already lend to that person on payments data.
2. **The borrower.** About 60% of loan revenue (about ₹750 of ₹1,845) comes from sign-ups who finished identity checks (KYC) and never save (LTV p3) [V].
3. **The payer: the lender.**

The online saver who also borrows ₹1 lakh is, I estimate, a low single-digit-crore segment at most [S].

## 3. Unit economics on the folder's evidence

The plan is 4.10×, paid back in month 19. Each row changes one input to the folder's nearest evidence; everything else stays at the plan.

| Input (plan) | Nearest evidence in the folder | One saver on that evidence alone [V] |
|---|---|---|
| Apply for a loan a year: **35%**, founder judgement (LTV p9) | Payments-app merchants 1–2% (XF-16); Paytm about 3.6% a year (XL-04). Lending apps' *registered* users ever borrowing: 17.5% (XL-42), 8% (LEND-04). | 3.6%: **1.73×**, month 41 · 10%: **2.19×**, month 34 |
| People who see loan offers per saver: **2.5**; non-savers borrow like savers | None. Jar: about 7% of registered users are active (LEV-040). | 1.0: **2.43×**, month 31 |
| Personal/business loan size: **₹1 lakh** | Digital lenders ₹18,802 (XF-11); Kissht ₹24,768 (LEND-02); bureau ₹58,522 (XL-29); the founders' own ₹10–25k (XF-24) | ₹25k: **2.54×** · ₹58.5k: **3.24×** |
| Loan-agent fee from the lender: **2%, rising to 3%** | Rate cards 1–2.5% (XF-01); the rise is "operator-set, no rate evidence" (`tables/online_inputs_audit.csv`) | Flat 2%: 3.69× |
| First approval: **30%** | Kissht approves 11.2% of new applicants (XL-41); the founders' own book about 25% | 25%: 3.81× |
| Cost to win after the seed: **₹450**, founder judgement | The seed's budget is ₹600 (not measured); Groww ₹796–1,374, 81–84% organic (TB-18) | ₹600: **3.08×** · ₹900: **2.05×** |
| Still saving at month 12: **38%**, extrapolated (LTV p6) | Savings apps 24% | 24%: **2.63×** |
| Serving: **₹6 a month**, no per-debit cost | ₹2 per debit base, ₹5.90 list (`research/tri_costs_summary.md`, TC-02/06) | ₹2 × 20 debits: **2.22×**, month 40 |
| Take-up +5%, approvals +10% a year | "Our judgement; no data" (LTV p13) | No rise: 3.56× |

**Combinations, run in the plan's own code [V]:**
- **Moderate evidence.** Every input at or inside the plan's own range: apply 10%, ₹50k loans, reach 1.5, 30% still saving, ₹600 to win, flat 2% fee, 25% approval, no yearly rise.
  - One saver: **0.93×**, no payback in 5 years.
  - Company: **never EBITDA-positive in 8 years**; needs **at least $9.9M**.
- **Half-way.** Apply 20%, ₹60k loans, reach 2.0, 34% still saving, ₹550 to win.
  - One saver: **1.66×**, paid back in month 41.
  - Company: **profit from month 66, $5.2M** (the plan says month 40, $2.5M).
- **Savings alone, with no loans:** 1.47× at ₹450, 1.10× at ₹600 (F10).

**The plan fails three cross-checks [V]:**
- Loans per rupee spent (F2): 0.54% of money lent, against Moneyview's 1.9–2.9%.
- Loan fees per reachable user: ₹295 a year, against about ₹354 a year for Paytm's *entire* financial-services revenue per user (XL-05), earned on 4–5% fees, not 2%.
- Year-5 revenue per active saver: ₹1,159, more than three times Paytm's financial-services figure.

**The 1,000 simulated futures give no comfort (F5).** The ranges peak at the plan's own values and exclude the evidence (`ALLSPEC` in `ltv_book.py`):
- reach is drawn from 1 to 2.5 and peaks at its maximum;
- the apply rate never goes below 10%;
- loans never go below ₹50k;
- the cost to win never goes above ₹600.

LTV p15 rightly calls this "a stress test, not a forecast". The v4 cover then presents "98 of 100 futures" as odds.

**The evidence labels do not hold up (F5).** v4 p1, p7 and p8 call the plan "today's evidence", while LTV p9 and A1–A2 label the same inputs founder judgement. v4 A10's "all 68 inputs checked" rests on `tables/online_inputs_audit.csv`, which does not match the model:
- It was saved at 14:39 on 21 Oct.
- It shows apply 3.6%, ₹58,522 loans and ₹300 to win, and has no row for reach.
- The model and tables were rebuilt at 19:08 with 35%, ₹1 lakh, ₹450 and 2.5 [V].

**Payment rails (F6).** v4's ₹5 a month covers "support, the app, bank charges and supervision" (LTV p13). The code has no per-debit cost [V]. On 2 Oct the same saver was −₹570, "mostly the fee on every debit" (`brief/project/slides/a11.html`). If BSE StAR MF's mandates cost the distributor nothing, the risk goes away. The exchange charges the order fee to the fund house (TC-12). Get it in writing, with the debit success rate [S].

## 4. Business model and valuation

**What it is.** At company level, over 5 years, loans are **76%** of revenue (personal and business 58%, other loans 18%) and the fund fee is **14%** [V; the decks' 63% is the one-saver view]. This is loan lead-generation, and the savings product is how it finds customers.

**Dependence on lenders and rules (F8).**
- Lenders set the fee, the approval rate and the loan size.
- A multi-lender referrer must show all matching offers neutrally (REG-014).
- Draft rate ceilings cover loans of ₹50,000 or less from April 2027 (REG-078).
- Households on ₹3 lakh a year or less can owe at most 50% of income in repayments (REG-077). A ₹1 lakh, 18-month loan at 26% costs ₹6,768 a month: 29% of ₹23,012, or 38% with the ₹2,000 of saving [V].
- Marketing loans to people who signed up to save, and never did, needs consent for that specific purpose (REG-084/085) [S].

Two precedents from the folder. Fi Money was a loan distributor whose lending was "scaled back sharply" under tighter RBI rules, after raising $137–169M (FI-02/03). Khatabook "can't lend enough to justify its valuation" (QM-37).

**How long the fees last.** Loan-agent fees are a commodity, and the rise to 3% has no support. The fund fee needs regular plans, which cost the saver 0.5–1% a year more than direct plans (OWN-04). The units sit in the saver's name and mandates can move between apps (REG-046), so a competitor can switch the saver to a direct plan. A lasting fee needs credit risk, either first-loss cover up to 5% (REG-003) or an own book, and v4 defers both.

**What a fund would pay.** A lead-generation multiple. In my general knowledge (unverified), listed Indian distribution fintechs trade at mid-single-digit to low-double-digit multiples of revenue, and loan-agent aggregators lower.
- Month-60 revenue run-rate: ₹45.6 cr a year [V].
- At 5–10×: ₹230–460 cr ($24–48M), not the ₹913 cr shown on v4 p9.

That is a fair seed outcome on plan inputs and none on evidence; venture returns need the grow-fast path, at $10.4M even on plan inputs.

**The unicorn yardsticks (v4 p9–p10).** 20× revenue is a software multiple on referral fees. 0.45× money saved borrows Stable Money's private round: ₹2,507 cr post-money on ₹5,000 cr of *cumulative* money invested and ₹4.3 cr of operating revenue (SAV-01 to SAV-03), about 580× revenue. Here it is applied to fund balances the company does not own, which prices one year's 0.67% fee at about 67× [V]. Every unicorn case needs 12.5 lakh sign-ups a month and "credit-hungry" inputs. Remove these pages; they cost credibility with a fund.

## 5. Defensibility and competitive response

**There is no moat in v4.** A distributor registration (₹40,000), loan-agent contracts, UPI Autopay and an AI coach can all be bought, and all are live at Bachatt.

**The claimed edge, "credit priced from the savings record", earns nothing for a referrer.** The lender underwrites and keeps the gain. v4 shows the edge only as an assumed +10% a year in approvals. The evidence that saving predicts repayment is correlational (EVD-03) or nil (EVD-01). Savings can even replace borrowing: Chilean micro-entrepreneurs given savings accounts cut informal debt by 24–36% (TB-08).

**The credit-as-reward promise does not survive the model.** Gate loans to savers after six months, as v4 p2 promises, and one saver returns about **2.4×** [V, approximate: loan income zeroed in months 1–6; `online_plan.py` lines 121–125, 188–190].

**Competitors can respond within a quarter.** Bachatt has a 40–50-person street team in NCR at about ₹300 a customer (PR-02); PhonePe and Jar already offer small daily saving.

**A warning sign on volume.** Bachatt's 2M fund transactions in February suggest 70–100k daily savers on 3M users (the folder's inference, BAC-03), about 3% active. The seed plan expects 13,800 still saving from 1 lakh sign-ups, about 14% (Seed p7) [S].

## 6. Capital plan and month-18 gates

**The budget** (Seed p2): product and team $205k, acquisition $133k, contingency $162k (32%) [V].

It can measure the cost to win, early retention, the daily amount, first-loan application, approval, size and fee, and the doorstep comparison. It cannot measure repeat borrowing, repayment by savings streak (the loans run 18 months), or the cost to win at scale.

**Risks inside the seed:**
- ₹100 per sign-up is priced like an install (Seed p9: installs cost ₹75–300). Many installs never sign up [S, general knowledge]. The plan still fits at ₹200 a sign-up (Seed p7) [V].
- A lender live from month 7 is the critical path. Nothing in the folder shows a lender conversation.
- Growing from 1,296 to 20,000 online savers a month within 12 months is 15× [V]. Groww's cost to win rose 73% in a year as paid marketing grew (TB-18).

**The next round.** The plan says $2.0M. My half-way case needs $5.2M, and the moderate case at least $9.9M.

**Term-sheet milestones (tranche triggers and Series A gates):**
1. **Lenders.** At least two signed lender agreements by month 9, each with a written fee of at least 1.75% and its approval criteria for this customer.
2. **Loan funnel.** Measured on at least 20,000 users who finished identity checks, each shown offers for at least 6 months:
   - application rate of at least 20% a year;
   - first approval of at least 25%;
   - median loan of at least ₹50k;
   - loan fees of at least ₹150 per user a year.
3. **Cost to win.** At most ₹600 per saver (one who has made 3 or more debits), for three months running, at 2,000 or more savers a month.
4. **Retention.** At least 55% still saving at month 6 and 30% at month 12, for the first three groups of savers; debit success rate and cost reported monthly.
5. **Non-savers.** Loans to non-savers measured, with consent on record.
6. **Doorstep.** Keep the arm only if it beats online retention at month 12 by at least 10 points, at ₹500 or less all-in.

## 7. Top risks

| Rank | Risk (type) | Sev. | What retires it |
|---|---|---|---|
| 1 | Loan funnel above the evidence; F2 (business) | P1 | Lender's written terms before close; milestones 1–2 |
| 2 | No wedge against Bachatt, PhonePe or Jar (competitive) | P1 | Better retention or cost to win in one named segment by month 9, or a product they lack (for example, a loan against the saver's own funds) |
| 3 | Cost to win unmeasured; rises with scale (business) | P1 | Milestone 3 |
| 4 | Lender fees and rules (regulatory) | P2 | Two lenders signed; legal opinions on the referral model and consent |
| 5 | Debit cost absent (business) | P2 | Exchange's written confirmation; success rate |
| 6 | 38% retention extrapolated (business) | P2 | Milestone 4 |
| 7 | Team breadth; plan volatility (team) | P2 | Full-time founders; growth hire; frozen base case |
| 8 | 80% equity for emergency savers; "loan app" label (reputational) | P3 | Suitability rule; loans gated on saving |
| 9 | Unicorn pages, odds, stale audit (credibility) | P3 | Re-base the deck |

## 8. Verdict

**Pass as lead on the current plan. Invest with conditions.** We would lead the $0.5M if all five hold:

1. **The investor case is re-based on evidence.** Base inputs: apply 10–20%, loans of ₹50–60k, reach measured, ₹600 to win. 35% / 2.5 / ₹1 lakh moves to "what it takes". The unicorn pages and the futures-as-odds line are removed.
2. **A signed letter of intent from a lender before close**, with fee, loan size and approval criteria for this customer.
3. **A one-page wedge against Bachatt:** segment, channel, and the feature Bachatt lacks.
4. **Both founders full-time and exclusive**, with 4-year vesting, and a consumer-growth lead hired by month 6.
5. **Two tranches.** $250k at close. $250k once the product and a lender are live and three months of cost-to-win and month-3 retention data meet the milestones. Plus monthly cohort information rights and pro-rata rights in the Series A. The folder states no price or instrument; price it as a referral business.

**Three questions for the partner meeting:**
1. "A shopkeeper already has Bachatt and PhonePe on their phone. Why do they save with you, and which number proves it by month 9?"
2. "Your own lending book ran ₹10–25k loans at about 25% approval. Which lender will approve ₹1 lakh for a ₹23,000-a-month self-employed person who signed up to save, and at what fee? Show us their email."
3. "60% of your loan revenue comes from people who never saved. If you can't reach them, and only 10% of savers apply, what is this company, and in which month do you stop?"

# Behaviour and CAC triangulation: summary (rows TB-01..TB-45 in tri_behaviour.csv, accessed 2 Oct 2026)
Each block gives (a) our bear/base/bull, (b) the range the evidence supports, (c) a verdict, (d) a Monte Carlo distribution. "Analogue" means a different product or population.
**Bottom line:** retention base is defensible (but needs to be shaped differently). CAC base is the most optimistic number in the model. The loan and insurance cross-sell rates have almost no support. On secured loans 1-2, the evidence points against us.

## 1. Retention: ret_m1/m3/m6/m12/m24 (HIGHEST PRIORITY)
- (a) Gig 60/38/24/13/6, **70/48/33/20/10**, 80/60/45/32/20. Self-employed base 72/53/40/25/15. The gig base implies 12.6% monthly churn to m12, then 5.6%/month in year 2.
- (b) Ceilings (richer, self-selected users): mainstream SIP cohorts keep 52-58% at 1-2 years (TB-01/02); Acorns keeps 55-75% at 12m (TB-11, company claim). Small-ticket Indian SIPs: SBI JanNivesh daily Rs 250 lost 35.6% of FY26 registrations within the year (NG-033). At a constant hazard that is ~8%/month, so ~62% at m6 and ~38% at m12. Chhoti SIP books churn 8-17% a month (TB-04).
- RCT middle: 45% completed a 3-6 month weekly plan (John, TB-05). SEED had 33% regular depositors at 12m (TB-07). Chile had 39 of 53 openers active (TB-08).
- Floors: free accounts given to the unbanked got 5+ deposits in 2 years from only 3-17% of those offered (TB-06). Jar's active savers are ~4-7% of everyone it registered (TB-16). Zomato loses 1.5-2 lakh riders a month (TB-12); the 13-month tenure in INC-01 comes from a length-biased sample of active riders. UPI AutoPay sees 20M mandate revocations a month on low balances (TB-14).
- (c) **m12 base 20% (gig) / 25% (self-employed) is NOT too optimistic.** It sits between the RCT floor and the small-SIP ceiling (supported range 10-40%). The gig curve is the riskier one: rider churn and bounced debits push it toward bear. The self-employed base may be low (JanNivesh-like ~38%).
- **The curve's SHAPE is wrong in two ways:** (1) Acorns, SIP vintages and the PMJJBY stock all show churn flattening after year 1. Our year-2 churn of 5.6%/month (20 to 10) is high: m24 of 0.6-0.75 x m12 fits the evidence better than 0.5x. (2) There is no reactivation, yet Acorns says 30% of year-1 leavers come back within 12 months (TB-11).
- **There is no evidence at all on Indian daily-saver retention past 12 months.** Searches for RD, India Post, pigmy and Atal Pension Yojana persistency found nothing (TB-09, TB-42). Jar, Bachatt and Gullak publish no retention figures.
- (d) ret_m12 gig ~ **Beta(4,16)**: mean 0.20, 5-95% 0.07-0.36. Self-employed ~ **Beta(5,15)**: mean 0.25. Draw ret_m24 = ret_m12 x r, with r ~ **Triangular(0.4, 0.6, 0.8)**. Earlier months: scale the base shape by one common draw, so m1-m12 stay ordered.

## 2. daily_amount (gig 25/**40**/60, self-employed 30/**50**/100 INR per debit)
- (b) Jar's average purchase is at least ~Rs 64 including lump sums (TB-17, derived), so Rs 40 for a pure daily save is plausible. But Gullak's transacting users saved only ~Rs 580 a month, about 1/9 of the founders' own $2/day thesis (TB-40). Bachatt's Rs 51-200/day is a product minimum, not observed behaviour (BAC-05). Most gig workers have no emergency fund (TB-15). Pigmy ticket sizes are not published.
- (c) Per debit, the base is fine. **Per month it is optimistic:** Rs 40 x 20 = Rs 800 (gig) and Rs 50 x 22 = Rs 1,100 (self-employed), against ~Rs 580 observed at Gullak.
- (d) **Lognormal.** Gig: median Rs 35, 5-95% Rs 20-65. Self-employed: median Rs 45, 5-95% Rs 25-110. The right skew is real: a few large savers drive balances (M-Shwari: 30-day actives hold 4x the average balance, TB-34).

## 3. debits_success (15/**20**/24 of 30)
- (b) All-India NACH: ~69% of debits succeed by count (TB-36). That is a monthly, mostly salaried EMI population, and our base 67% equals it. UPI AutoPay: 55-90% of execution attempts failed at major banks in Aug 2025, mostly on insufficient balance (TB-13; this counts attempts, not savers). Jar claims ~22 saves a month (LEV-040, company claim).
- (c) **The base assumes riders bounce no more than the average Indian EMI payer, which is optimistic for riders.** The bull case (80%) beats the national average with no evidence behind it. Self-employed users with daily cash are more plausible.
- (d) **Triangular(10, 17, 24)** gig. Self-employed: Triangular(12, 19, 25). Make it the first metric the pilot measures.

## 4. CAC per activated saver (base Rs 249 gig / Rs 263 self-employed; paid benchmark Rs 750)
- (b) Groww blended CAC is Rs 796-1,374 even with ~83% organic acquisition (TB-18). Finance-app installs cost Rs 75 at the median and Rs 100-300 for wealth apps (TB-19), so our paid funnel (12% install-to-activation) costs ~Rs 1,300, not Rs 750.
- Marketing only, per REGISTERED user: Jar ~Rs 30-50 (TB-20) and Stable Money ~Rs 125-200 (TB-38). Altcase paid Rs 5,000 per transacting FD user (BM-04).
- Field inputs are cheap: bank agents get Rs 10-140 per account opened (TB-22). But field staff turn over ~40% a year (TB-37). 68% of people abandon finance applications (TB-21). Swiggy already has a fund-house savings partner, a direct risk to our largest gig channel (TB-45).
- (c) **The base is too optimistic: it is the best case for a field-led funnel, not a central estimate.** Rs 249 requires 36-50% of installs to activate. No Indian firm publishes that funnel. Jar's marketing-only figure clears Rs 249 only if half of its registrants make a first save.
- (d) **Lognormal, median Rs 450, sigma 0.6 (5-95%: Rs 170-1,200).** Under this, our base sits at the 16th percentile. Keep cac_mult on top for the self-employed.

## 5. loan_apply (2/**4**/6% a month of eligible) and demand for loans secured on own savings
- (b) Base implies ~19% of active savers borrowing within 12 months of eligibility. Evidence: Paytm ~0.9% of monthly users take ANY loan/broking/insurance per quarter (TB-31); Moneyview 8%, GCash 11% ever borrowed (LEND-04, CMP-07); M-Shwari 30-34%, but there the loan was the hook and unsecured (TB-34, CMP-05).
- On SECURED-on-own-savings demand: M-Shwari launched with savings frozen against loans and "quickly changed" it (TB-33). Under 1% of MF investors borrow against funds (TB-44). Savings access made Chilean micro-entrepreneurs borrow LESS (TB-08). For: 12-30% co-hold debt and savings (TB-28); a boom in pledging (not selling) gold (TB-29); Self has 1M+ US credit-builder customers (TB-39).
- (c) **Too optimistic for loans 1-2.** Rational savers withdraw rather than borrow their own Rs 2,000. Demand will come from the PROMISE of the unsecured rungs. The useful upside: M-Shwari users saved mainly to become eligible for credit, which helps retention.
- (d) **Triangular(0.5%, 1.5%, 4%)** per month. Re-test with loans 1-2 removed: they may be a cost, not a revenue line.

## 6. loan_repeat (30/**45**/60%)
- (b) Repeat borrowers are >50% of Paytm merchant-loan disbursal (TB-31) and ~73% of Kissht's book (TB-43). 68% of PM SVANidhi repayers took a second loan (NG-014). Bueno saw 30-50%. These are value shares, not the share of repayers who borrow again.
- (c) **Supported; possibly conservative.** (d) **Triangular(0.30, 0.50, 0.65)**.

## 7. ins_uptake (1/**2**/3% a month; ~15% of active savers insured by m12)
- (b) PhonePe sold ~4M policies a year to hundreds of millions of users, roughly 1-2% a YEAR (TB-25). Paytm: under 1% a quarter for all financial products (TB-31). Optional add-ons attach at 3-6% (TB-26, vendor figure). Pioneer reached ~15% of a microfinance membership only after years of agent selling (TB-41). Platforms already give riders Rs 1-2 lakh of free cover (TB-27).
- (c) **Too optimistic: about 10x what India's largest apps achieve, and for riders it competes with free cover.** (d) **Triangular(0.2%, 0.8%, 2.5%)** a month. Self-employed users have no platform cover, so use a mode of 1.2%.

## 8. ins_persist (40/**55**/70%)
- (b) Voluntary microinsurance renewal rose from 23% to 46% only after a dedicated redesign (TB-41). Life 13th-month persistency by count is 64-83% (TB-24): long-term, agent-sold policies. Auto-debited PMJJBY/PMSBY keep 51-70% of all-time enrolments active (TB-23), on tiny premiums.
- (c) **Plausible only if renewal is a default auto-debit.** If renewal needs a fresh decision, use the bear case. (d) **Beta(4.5,5.5)**: mean 0.45, 5-95% 0.20-0.71.

## 9. card_uptake (1.5/**3**/4.5%) and the savers-repay-better claim
- **No data.** No count of FD-secured cards issued and no payout rate was found (TB-35, BM-08). Behaviour data predicts repayment in general (TB-30, EVD-02), but no study shows that a SAVING streak lowers default in India. Model card_uptake as **Uniform(0.5%, 3%)** and label it unevidenced. Keep ladder_dpd90 as founder data.

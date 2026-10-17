# Market benchmarks: savings-first app for gig workers (Delhi NCR)

Researched 2026-09-30. Every number below has a row in `market_benchmarks.csv` (the IDs are in brackets). Low/base/high values are **suggested model inputs**. They are not facts. Where they rest on weak evidence, this file says so.

## 1. Numbers the model needs (most important first)

| Input | Low / Base / High | Evidence and caveats |
|---|---|---|
| **Liquid-fund distributor trail** | 5 / **8** / 12 bps a year on AUM | Regular minus direct TER, Aug 2026: ICICI Pru Liquid 0.25% vs 0.17%; SBI Liquid 0.29% vs 0.17% [BM-01]. Overnight funds pay 3 / 5 / 8 bps (ICICI 0.13% vs 0.07%) [BM-02]. On a Rs 5,000 balance the trail is about **Rs 4 per user per year**. |
| **FD distribution fee** | 0.25% / **0.5%** / 1.0% of the FD, one-time | Anecdotal only. One source says Stable Money earns about 1%; Altcase earned Rs 300 a year on a Rs 75,000 FD (0.4%) [BM-03]. No bank publishes its rate. |
| **Personal-loan LSP/DSA payout** | 1.0% / **2.0%** / 3.0% of disbursal | Agent-platform blogs: 1-2.5% is typical, 0.5-4% by campaign [BM-07]. No source gives rates for loans under Rs 50k. |
| **FD-secured card payout** | Rs 200 / **500** / 1,000 per activated card | **Assumption.** Unsecured-card affiliate payouts are Rs 500-2,000 [BM-08]. No payout for a secured card was found. |
| **Health/PA insurance commission** | 5% / **12%** / 15% of premium | FY25 actual: 14-20% of net premium at standalone health insurers [BM-09]. An IRDAI draft of 23 Sep 2026 proposes caps of 15% (first sale), 5% (renewal) and **5% for insurance sold with a loan** [BM-10]. Comments close 25 Oct 2026. |
| **Lending CAC** | 1.9% / 2.4% / 2.9% of disbursal | Moneyview's marketing and direct-sourcing cost, FY26 / FY25 / FY24 [LEND-03]. No lender discloses a rupee CAC per applicant. |
| **Savings/FD CAC** | Rs 50-300 per install (unverified); **Rs 5,000 per transacting FD user** | Rs 5,000 is Altcase's figure, and Altcase pivoted within 5 months [BM-04, BM-05]. Stable Money's FY25 ad spend was 25.3 cr, about 6x its operating revenue [SAV-01]. |
| **Share of users who ever borrow** | 8% / 11% / 34% | Moneyview: 8% of registered users have ever used a revenue product [LEND-04]. GCash: about 11% of lifetime users are borrowers [CMP-07]. M-Shwari: 34% of *eligible* users take a loan [CMP-05]. |
| **Loss on Rs 10-50k loans** | 6% / **7%** / 9% vintage 90+ | CRIF, H1 FY25: peak 90+ is 6.0% across all lenders and 7.2% at NBFCs. Loans under Rs 10k peak at 8.9-9.5% [MAC-03]. |
| **Worker income** | Rs 12k / **18.8k** / 28k per month | IDinsight 2024 (n=2,547): full-time riders gross Rs 27,814 and net **Rs 18,761** after 32% costs [INC-01]. The Economic Survey says 40% of gig workers earn under Rs 15k [INC-03]. |
| **Rider tenure** (sets churn) | about **13 months** on average | 77% of riders are part-time and 23% are students [INC-01]. |
| **Existing debt stress** | 50% borrowed to buy assets; ~1/3 missed a repayment | IDinsight [INC-02]. |

**Segment size.** NITI Aayog counted 7.7M gig workers in 2020-21 and projects 23.5M by 2029-30 [SEG-01]. By mid-2026 only 10-12 lakh gig workers had registered on e-Shram [SEG-03], of whom 49,479 are in Delhi NCT (Jan 2026) [SEG-04]. Monthly active delivery partners by platform:

- Swiggy: 648k (Q1 FY27) [SEG-05]
- Zomato food delivery: 4.73 lakh (FY25) [SEG-06]
- Blinkit: 409k (Q4 FY26) [SEG-07]

These overlap because riders work on several apps, so they cannot be added up. No platform publishes a Delhi NCR headcount.

**Jar's revenue per registered user:** Rs 59 on the 208 cr figure, or Rs 699 on 2,447.8 cr gross [JAR-09]. Both use a Sep-2025 cumulative user base against FY25 revenue, so both are understated. Jar publishes no MAU, so a per-active-user figure is not possible.

## 2. Findings that contradict or correct the brief

1. **Jar's Rs 208 cr is not its statutory operating revenue.**
   - In the RoC filing, revenue from operations is **Rs 2,447.8 cr** (gold sold as principal). FY24 was Rs 49 cr [JAR-01].
   - Rs 208 cr is a company-defined net figure from a press release [JAR-02]. RoC revenue minus gold purchases gives only Rs 114 cr, before inventory change [JAR-03].
   - The "9x growth" implies a FY24 base of about Rs 23 cr (the Dec-2023 ARR), not the RoC's Rs 49 cr.
   - Jar was profitable in Q4 FY25 and Q1 FY26, but **FY25 as a whole still lost Rs 50.5 cr** [JAR-04, JAR-06].
2. **Bachatt:**
   - It has **no FD product**. Its press release calls FDs unsuitable, and its gold and silver are fund-based.
   - It targets merchants and the self-employed.
   - It **already cross-sells loans (up to Rs 5 lakh) and credit cards** [BAC-05].
   - It claims 3M users [BAC-02], but its website shows 10 lakh users and Rs 50 cr invested, roughly Rs 500 per user [BAC-04].
3. **Fi Money raised about $137M (Inc42) or about $169M (TechCrunch)** [FI-02].
4. **M-Shwari does not prove that saving predicts repayment.** Bharadwaj-Jack-Suri measures resilience to shocks [CMP-05]. Since then, M-Shwari lending has **shrunk 3% a year while Fuliza, an overdraft built into M-Pesa payments, reached 13x its size** [CMP-11].
5. The gig-worker counts on e-Shram are inconsistent across ministry statements [SEG-03]. FY24 household savings were revised from 5.1% to 5.8% of GNDI [MAC-02].

## 3. One lesson per comparable

- **Jar:** 35M registrations still gave a FY25 loss. Its margin comes from the gold spread, which this plan gives up by skipping digital gold. So revenue has to come from cross-sell, and at Rs 4 of trail per user, it cannot come from the liquid fund.
- **Bachatt:** This is the closest competitor, funded by Accel, Lightspeed and Info Edge. It gets rapid sign-ups but tiny balances [BAC-01..05].
- **Stable Money:** FD distribution alone cannot pay for acquisition: 40 lakh users produced 4.3 cr of operating revenue [SAV-01/02].
- **Fi Money:** When a front-end's revenue depends on distributing other lenders' loans, it disappears when partners or rules change [FI-03].
- **Jupiter:** High CAC and thin fees led it to take its own NBFC licence to capture lending economics [JUP-01/02].
- **Chime:** It monetises the payroll flow it sees. Payments revenue, mostly interchange, was about 68% of FY25 revenue. MyPay's losses early on were about 89% of its revenue [CMP-02/03].
- **M-Shwari / Fuliza:** Savings-linked credit reached scale with a 2% NPL (2015), but credit at the point of spending grew faster [CMP-04, CMP-11].
- **TymeBank:** It gets distribution through retailer kiosks. Its first monthly profit came about 5 years after launch, with SME cash advances and BNPL on top of deposits [CMP-06].
- **GCash:** It started as a wallet. Credit became the monetiser: 10.5M borrowers and PHP 362bn lent in 2025 [CMP-07].
- **Nubank:** Card-first worked against 450%-a-year revolving rates and concentrated banks. In India only banks and RBI-approved NBFCs can issue cards, so fintechs must partner with them. There are 123M cards, and the four largest issuers hold about 70%. For thin-file workers the realistic entry is a card secured by an FD [CMP-09/10].
- **US credit-builder RCT:** It raised scores by about 60 points for people without existing debt. It hurt people who already had debt, and 39% of borrowers paid late at least once [EVD-01]. Most riders already carry debt.
- **Chioda et al. (RappiCard):** Delivery-app data predicts creditworthiness for people with no bureau history [EVD-02]. The founder's underwriting edge may be payout data rather than savings history.
- **India SHGs:** Savings-linked SHG loans run a 2.05% NPA against 8.72% for microfinance. This is a correlation only [EVD-03].

## 4. Could not verify

- **Jar:**
  - MAU, transacting users and daily savers
  - the personal-loan launch date
  - a **Rainmatter** investment (no source found)
  - FY26 financials
- **Bachatt:** AUM and revenue, other than the website banner.
- **Commission rates:**
  - FD commissions actually paid by banks and SFBs
  - sourcing fees for FD-secured cards (OneCard, Kiwi, SBM, IDFC WOW)
  - LSP rates for loans under Rs 50k
- **CAC:** per install, per KYC'd user or per transacting user for any Indian savings app, and CAC per applicant for any lender.
- **Workforce:** active driver counts for Uber, Ola and Rapido; platform headcounts for Delhi NCR; Zepto's DRHP rider count (secondary source only) [SEG-08/09].
- **Rider credit:** volumes of loans that platforms arrange for riders (Swiggy and Zomato programmes are merchant loans) [LEND-11].
- **Savings and repayment:** any Indian or gig-segment evidence that savings behaviour predicts repayment.
- **Studies named in the brief:** the "Janwani" study (the study found is PAIGAM + IFAT, 2024), CLRA, and BCG/MSDF gig estimates.
- **Lenders:** KreditBee's PAT (237 cr standalone vs 473 cr reported) [LEND-06], and Refyne, TrueBalance and Pocketly financials.

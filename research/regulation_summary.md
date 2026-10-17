# Regulation and payment rails: what they mean for the savings-first app

As of 30 Sep 2026. The `REG-xxx` ids point to rows in `regulation_rails.csv` (source, date and verdict for each). Map of licences: `regulatory_map.md`.

## 1. What it means for the business model

1. **The Bueno model is not allowed any more.** In the old model the app paid the lender a fixed 18% IRR and absorbed 100% of losses. RBI now treats any guarantee linked to how a loan book performs, "called by whatever name", as a Default Loss Guarantee (DLG). A DLG is capped at **5% of the amount disbursed** from a fixed portfolio. It must be put up in cash, a lien-marked FD or a bank guarantee, held for the longest loan tenor, and invoked by 120 days overdue [REG-003-009]. No DLG is allowed at all on credit cards or revolving credit lines [REG-007]. So the app earns a **fee from the lender** and cannot charge borrowers [REG-011], while the lender keeps at least 95% of the credit risk. My inference: expect lenders to approve fewer loans and pay smaller fees than in 2019-22. Each Rs 1 crore of loans the app sources with a DLG locks up to Rs 5 lakh of its cash.
2. **The app can never touch the money.** MF purchases must come from the investor's **own** bank account (MF Master Circular, 20 Mar 2026). SEBI's May-2026 draft would allow third-party payments only for listed or EPFO-registered *employers* paying for *employees*, which does not cover gig platforms [REG-066]. Holding worker money in an app wallet risks the unregulated-deposit law (2-7 years in jail) [REG-081]. So "saving straight from platform payouts" has to work like this: the platform pays the worker's own bank account, then the worker's own mandate debits it. I found no rule that lets a platform deduct part of a gig worker's payout into a savings product [REG-067].
3. **Daily UPI Autopay is legal but expensive per rupee saved.** Daily mandates are allowed [REG-048]. Each debit needs a pre-debit notice at least 24h ahead (sent by the worker's bank or UPI app), must run off-peak (before 10:00, 13:00-17:00 or after 21:30), and gets 1 attempt plus 3 retries [REG-047, 049]. There is **no MDR on Autopay**, even after the new 0.4% MDR on merchant payments above Rs 2,000 starts on 15 Oct 2026 [REG-052]. But payment aggregators charge per debit. At Cashfree's list price of **Rs 5 per debit, a Rs 50 daily save loses 10%**. Weekly batching or negotiated paise-level pricing is essential [REG-050]. Since 31 Dec 2025, any UPI app can show a worker's mandates and port them, and the app may not offer inducements to stop a port [REG-046].
4. **The savings leg earns almost nothing, so cross-sell has to pay for everything.** Liquid-fund trail is about 8 bps a year [REG-039]. *Illustration, my assumptions:* a worker saving Rs 1,300 a month has an average balance of about Rs 8,450 in year 1, which earns about **Rs 7 of trail in the year**. Daily-SIP minimums are about Rs 100, so Rs 10-99 saves have to accumulate in the worker's bank first [REG-043]. The Rs 250 "Choti SIP" pays the distributor up to **Rs 500 per new investor, but only after 24 months**. It is monthly-only, equity/hybrid-only, limited to first-time investors and 3 per investor, and early exits are reportedly high (unverified) [REG-031-035].
5. **Insurance commissions are about to be capped (draft).** IRDAI's 23 Sep 2026 paper would cap commissions for open-architecture distributors. Health: 15% of first-year premium, 5% on renewal. Pure term life: 25% first year, 7.5% renewal. Loan-linked life: 2.5% then 1%. Small towns and rural areas get an uplift of 10-20% of the first-year cap. The expense glide path starts in FY2027-28 [REG-053-057]. Model insurance revenue at these caps, not today's market rates.
6. **FD-secured card: sourcing only.** The card must come from the same bank that holds the FD [REG-029]. Only the issuer decides who gets a card, and the app gets no card-transaction data [REG-087].
7. **An own NBFC is a later option.** It needs Rs 10 crore net owned fund by Mar 2027 [REG-017]. RBI's charter says 90 days to decide a complete application; practitioners say 8-14 months end to end [REG-018]. Unsecured consumer loans still carry a 125% risk weight; the 2025 relief covered only microfinance loans [REG-076]. Loans to households earning up to Rs 3 lakh count as microfinance: repayments are capped at 50% of household income [REG-077].
8. **The Labour Codes give no hook for a private savings product.** Aggregators will pay 1-2% of turnover (capped at 5% of worker payouts) into a government fund, and the rate is still not notified [REG-062, 063]. **Delhi has no gig-worker Act**; Karnataka's fee is 1% with a cap of Rs 0.50-1.50 per transaction [REG-064, 065].
9. **Marketing limits.** No lucky draws for savers [REG-079]. No pooled savings circles without chit registration [REG-080]. No cashback on MF or insurance purchases [REG-082, 083].
10. **Data.** The Bueno borrower list belongs to BetterPlace, which acquired Bueno in May 2023, and was collected for lending. Reusing it for this app would breach purpose limits under today's IT Act and SPDI Rules, and the DPDP Act from 13 May 2027 (penalties up to Rs 250 crore) [REG-084-086].

## 2. Costs per transaction (Rs, excluding GST unless noted)

| Item | Low | Base | High | Basis |
|---|---|---|---|---|
| UPI Autopay mandate creation | 3 | 5 | 7.5 | Cashfree list 7.5; Rs 3 cited for Razorpay (secondary) [REG-050] |
| UPI Autopay debit (< Rs 1,000) | 0.5* | 2* | 5 | Cashfree list 5; *low/base are my assumptions for negotiated pricing* [REG-050] |
| UPI MDR on Autopay | 0 | 0 | 0 | DFS FAQ Q22 [REG-052] |
| e-NACH mandate / debit | 7.5 / 7.5 | 7.5 / 7.5 | 20 / 10 | Cashfree list; one bank tariff [REG-050, 051] |
| Failed debit / retry | 0 | UNVERIFIED | UNVERIFIED | Razorpay says no per-retry charge within limits [REG-050] |
| Own reminder SMS / WhatsApp utility message | 0.10 / 0.08 | 0.15 / 0.115 | 0.20 / 0.115 | Statutory notice is sent by the bank, so these are optional [REG-072, 073] |
| Aadhaar e-KYC (UIDAI fee / vendor) | 3 | 5 | 7 | UIDAI Rs 3 incl. tax (2021) [REG-068, 069] |
| KRA KYC upload / download | 30 / 35 | 30 / 35 | 50 / 50* | 2012 NDML tariff; *high is my assumption* [REG-045] |
| CKYC lookup | 5 | 10 | 15 | Vendor range, UNVERIFIED [REG-069] |
| Video KYC | 20 | 100 | 150 | Vendor range, UNVERIFIED [REG-069] |
| PAN check / penny drop | 1 / 2 | 2 / 3 | 3 / 5 | Vendor range, UNVERIFIED [REG-069] |
| Account Aggregator fetch | 0.01 | 5* | 25 | Setu band; *base is my assumption* [REG-070] |
| Credit bureau pull | 10* | 30* | 60* | Not published; all three are my assumptions [REG-071] |
| **Onboarding one saver (e-KYC + KRA + PAN + penny drop)** | **36** | **40** | **65** | Sum of the rows above; about Rs 100+ if video KYC is needed |

**Revenue-side rules.** Liquid trail: 5 / 8 / 15 bps a year [REG-039]. EOP (direct plans): at most Rs 2 per transaction [REG-038]. Choti SIP: up to Rs 500 after 24 months [REG-033]. LSP fee: paid by the lender, amount commercial (not researched). DLG: up to 5% of disbursals at risk.

## 3. Where the brief was wrong
- **Small-ticket SIP.** There was **no final SEBI circular**. The scheme runs under a SEBI letter of 20 Feb 2025. The proposed incentive was funded from investor-education budgets, not the IEPF. Choti SIP is monthly only [REG-030-032].
- **DPMACI** (formed May 2026) is real, but **Jar is not a founding member**. Gullak, PhonePe, CRED, MMTC-PAMP, SafeGold and others are [REG-027].
- **NPCI OC-223** added *view* and *port* from any UPI app. Revoke, pause and modify already existed [REG-046].
- **UPI MDR** is no longer zero for merchant payments above Rs 2,000 from 15 Oct 2026. Autopay is exempt [REG-052].
- **The UIDAI e-KYC cut** (Rs 20 → Rs 3) happened in 2021, not 2025 [REG-068].
- **The 2025 risk-weight rollback** covered microfinance loans and bank loans to NBFCs only, not personal loans [REG-076].
- **IRDAI life caps of 20% / 25%** apply only to policies with premium terms of 10+ years. Term life is 25% / 30% [REG-055].
- **T+1 for liquid funds** is market practice. SEBI's limit is T+3 [REG-042].

Everything else I checked was confirmed: the DLG rules and 5% cap, the NOF glide path, the gold-loan dates and the ban on primary gold and gold ETFs/MF units, the SEBI and Pandey statements on digital gold, the Labour Codes date and the 1-2%/5% contribution, the Autopay limits, and the IRDAI health caps and 25 Oct deadline.

## 4. What I could not verify
- How fintechs are paid for sourcing FDs, and whether that needs any licence.
- LSP fee levels and credit-card sourcing fees.
- Bureau pull prices, current KRA and CKYC tariffs, and negotiated payment-aggregator prices per debit or per failed debit.
- Net-worth requirements for IMFs and web aggregators, and POSP rules.
- Whether a non-regulated app can be an Account Aggregator data user (FIU).
- How many new NBFC registrations RBI granted in 2024-26, and NBFC loan-to-value rules for loans against MF units.
- Whether the digital-gold framework, SEBI's third-party-payment circular and RBI's draft APR ceilings for loans up to Rs 50,000 have been finalised.
- Current Choti SIP counts.
- Gig-worker laws in Haryana and UP (Gurugram, Noida).
- Any rule on payout deductions for gig workers.
- Whether the 125% risk weight on personal loans is unchanged in 2026.

# Non-gig half: evidence summary and suggested model inputs

Researched 2026-09-30. Row IDs (NG-xxx) point to `nongig.csv` (46 rows: 34 confirmed, 1 corrected, 11 unverified). Where a number is **my derivation or judgement** rather than a source figure, it says so.

## 1. Suggested inputs for the non-gig half (vs the gig half)

| Input | Gig half (given) | Non-gig LOW | Non-gig BASE | Non-gig HIGH | Evidence |
|---|---|---|---|---|---|
| **Monthly income** | ₹18,761 net | ₹10,000 | ₹23,000 | ₹35,000 | Low: street vendors ₹9–15k (Ludhiana, N=605, NG-045). Domestic workers about ₹10k (WIEGO 2020 via BehanBox, unverified, NG-026). Base: PLFS 2025 urban self-employed mean ₹23,012 (NG-005). High: PLFS 2025 Delhi self-employed mean ₹34,868 (NG-006). PLFS figures are *gross* means that exclude zero earners, so they flatter the typical person. |
| **Savings retention (1 / 12 / 24 months)** | 70% / 20% / 10% | 70 / 20 / 10 | 70 / 25 / 15 *(judgement)* | 75 / 40 / 25 *(judgement)* | No shopkeeper-specific savings-retention data exists (NG-032, NG-037). For comparison, SBI MF's ₹250 **daily** Jan Nivesh SIP lost 35.6% of its FY26 registrations within the same year (NG-033). Your curve predicts that about 44% of a cohort spread over one year would still be alive; this SIP shows about 64%, so your curve is on the cautious side. The Chhoti SIP book loses about 6.7% a month, which is about 44% surviving over 12 months at book level (NG-034). Small-ticket SIP folios are the only ones shrinking (NG-035). In a Kenya RCT, market vendors kept saving and bicycle-taxi drivers did not (NG-040). |
| **CAC per activated saver** | ₹250 | ₹250 | ₹1,000 *(placeholder; no evidence)* | ₹5,000 | No firm discloses cost per *active* merchant (NG-043). High: Paytm's sales-and-service staff cost per net device added is about ₹5,000, derived and an upper bound (NG-028). Ongoing alternative: pigmy doorstep collectors are paid **2.5–4% of the amount collected** (NG-041). At ₹50/day that is about ₹450 per saver per year (derived). |
| **₹10–50k PL, 90+ DPD at peak** | 6–7% (CRIF) | 6% | 10% | 16% | Low: CRIF PL ₹10–50k across all lenders is 6.0%. Base: CRIF unsecured business loans <₹10L to self-employed individuals peak at **10.2%** (NBFCs 11.1%, private banks 7.0%) (NG-015). The MSME Pulse ≤₹10L exposure band shows 5.8% of balances at 90+ (NG-017). High: PM SVANidhi NPA was 15.9% of loans to May 2022 (NG-013). The MSME Pulse "ever 90+ within 12 months" is 16.2% for FY24 originations, but which exposure band that belongs to is unclear (NG-018). |
| **Platform/occupation tenure** | ~13 months | no data | no data | no data | No credible 1–2-year survival rate was found for Indian micro-enterprises or street vendors. Proxies: a lobby claims about 1.5% of kiranas close each year (unverified, 45% of them in metros, NG-039). 68–75% of vendors who repay a SVANidhi loan take the next tranche (NG-014). |

**Size is not a constraint.** 39.1% of Delhi's workers are self-employed (NG-004). Delhi has 11.9 lakh Udyam micro enterprises plus 7.3 lakh informal micro units, but these are registrations, not active businesses (NG-008). Other Delhi counts:
- about 1 lakh auto permits (NG-021);
- 60–78k street vendors identified, with estimates of 1.3–3.5 lakh (NG-011);
- 1.4 lakh+ SVANidhi loans repaid (NG-012).

Nationally there are about 6.5 crore UPI merchants (NG-027). Only about 24% of PhonePe's registered merchants are active in a given month (NG-038).

## 2. What contradicts the founder's assumptions

1. **Bachatt's ₹30–70k is a target band, not a measured income** (NG-031). It sits above the PLFS urban self-employed mean (₹23k) and matches only Delhi's mean. Using it as the segment's income overstates it.
2. **The non-gig segment is not a safer credit risk.** Small loans to the self-employed peak at about 10% 90+ DPD, against 6–7% for your gig reference. Delhi microfinance has 21.3% of loans at 180+ days past due (NG-020).
   - At the base case, losses would use up the **whole 5% default-loss guarantee**. The guarantee cost per loan should be modelled at the cap, not below it.
3. **₹250 CAC has no support for a field or merchant channel** (NG-043).
4. **"Auto-save from daily UPI sales" has no working model to copy** (NG-046).
   - Small P2PM merchants receive UPI money **directly into their own personal account** and pay zero MDR below ₹1 lakh a month (NG-030). There is no payment-aggregator settlement to split, so saving has to run as a mandate on the merchant's own account.
   - PhonePe already runs Jar-powered ₹10/day gold for consumers. A merchant version is a short step for the incumbents.
5. **Retention may be *better* than assumed, not worse.** The 20% at 12 months looks cautious next to the daily-SIP data. But "not ceased" is not the same as "still paying", so treat this as upside, not the base case.

## 3. Legal checks per channel

Not covered here. The coordinator reassigned task 6 to the main session.

## 4. What could not be verified

- Merchant acquisition cost per active merchant at Paytm, PhonePe, BharatPe or Pine Labs. None of the filings found disclose it.
- Published retention for any merchant savings product. The 12% Club was P2P lending and was paused. Paytm Payments Bank lost its licence on 24-Apr-2026 (NG-037). Bachatt publishes no retention figures.
- Survival rates for micro-enterprises and street vendors.
- Delhi auto-driver earnings. Only a vendor blog gives a figure, about ₹21–22k net (NG-022).
- Delhi domestic-worker wages. Domestic work is not a scheduled employment in Delhi; the unskilled minimum wage is ₹18,456 (NG-025).
- A bureau split of small-PL delinquency for self-employed vs salaried borrowers (NG-016).
- An official kirana count. Estimates range from 13M to 15M+ (NG-009).
- Delhi counts of P2PM merchants or soundboxes.
- Which exposure band the MSME Pulse 16.2% belongs to. The chart legend conflicts with the headline (NG-018).
- Referral economics for B2B supplier platforms. udaan, HUL and others offer only trade credit (NG-044).

# Addendum 3: fix the collections chain, and cap insurance commissions (lead decision, 16 Oct 2026)

## Why

Addendum 2 chained the vendor's bucket cure rates (GAP-02) backwards from the loss rate. Those cure rates are per-spell or monthly rates, not lifetime shares, so the chain implied that 124% of loans reach 31–60 days overdue. That is wrong, and the error was the lead's.

## Collections, replacing addendum 2's collections section

Keep `loss` (1.5 / 3 / 5%, Paytm worst case) as the anchor the operator set.

| key | input | shape | low / likely / high | evidence | confidence |
|---|---|---|---|---|---|
| owed | Share of the loan still owed when it goes 90+ days bad | fixed | 0.5 | | Our judgement |
| recovered | Recovered after 90 days | pert | 30 / 35 / 50% | GAP-02, XB-07 | Published low end; judgement range |
| p90 | Share of loans that ever go 90+ days bad | derived, not an input | loss / (owed × (1 − recovered)) | about 9.7% at the likely values. Check on the page: NG-015 (CRIF: unsecured business loans to the self-employed, under ₹10 lakh, peak 10.2%) and MAC-03 (personal loans over ₹50k, 3.6%) | |
| early_cured | Share of loans that fall 31–90 days behind and that our agent brings back before 90 days | pert | 10 / 20 / 35% | no published figure | Our judgement |
| fee_early | Our fee per early account brought back | pert | ₹200 / 450 / 1,000 | GAP-01: ₹200–400 at 31–60 days, ₹500–1,000 at 61–90 | Industry guide, not verified |
| fee_b3 | Our fee per 90+ account recovered | pert | ₹1,000 / 2,500 / 5,000 | GAP-01 | Industry guide, not verified |

- **Dropped:** cure_b1, cure_b2, fee_b1 and fee_b2.
- **Fees per loan made** = early_cured × fee_early, paid about 9 months after disbursal, plus p90 × recovered × fee_b3, paid about 18 months after.
- **Page check:** early_cured + p90 must stay ≤ 50%. Show the implied p90 against NG-015 and MAC-03.

## Insurance commissions, capped at IRDAI's draft caps for open-shelf distributors

We are a distributor. The highs are capped at the draft distributor caps (REG-053..057):

| Product | Commission (low / likely / high) |
|---|---|
| Small health, family health, accident, shop | 10 / 15 / 15% (the likely value sits at the cap, so use pert 10 / 14 / 15) |
| Term life | 7.5 / 20 / 25% |
| Device | 10 / 13 / 15% |

- Renewals stay at 5% (health) and 7.5% (term).
- The open choice "draft caps or today's rates" stays open for the operator. The base uses the caps, the cautious choice.
- The vehicle-loan low of ₹80,000 stays (it covers two-wheeler loans); mark it judgement, with XL-54's ₹1.5–6 lakh for autos and e-rickshaws as context.

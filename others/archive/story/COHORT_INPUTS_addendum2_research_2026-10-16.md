# Addendum 2: operator decisions and research results (16 Oct 2026)

Evidence rows: `research/gaps_2026-10-16.csv` (GAP-01..06), from 8 web searches the operator approved.

## Operator decisions (taps)

| Input | Decision |
|---|---|
| trail | debt fund, pert 0.20 / 0.35 / 0.50% |
| r12 | pert 25 / **55** / 72% |
| card_share | pert 1 / **3** / 6% |
| tenure | pert 24 / 36 / 48 months |

## Collections on overdue loans: per account resolved, by bucket

This REPLACES `dpd30_fee` and `rec_fee` as percentages. No percentage rate card is published; lenders pay agencies per bucket (GAP-01).

| key | input | shape | low / likely / high | evidence |
|---|---|---|---|---|
| cure_b1 | Share of 31–60 day cases our agent brings back | pert | 70 / 80 / 90% | GAP-02 70–85%; XB-07 Paytm 83–90% |
| cure_b2 | Share of 61–90 day cases brought back | pert | 50 / 60 / 75% | GAP-02 50–70% |
| recovered | Recovered after 90 days | pert | 30 / 35 / 50% | GAP-02 30–50%; XB-07 Paytm 30–35% |
| fee_b1 | Our fee per 31–60 day account brought back | pert | ₹200 / 300 / 400 | GAP-01 |
| fee_b2 | Fee per 61–90 day account brought back | pert | ₹500 / 750 / 1,000 | GAP-01 |
| fee_b3 | Fee per 90+ account recovered | pert | ₹1,000 / 2,500 / 5,000 | GAP-01 |

**Consistency (derive the flows; don't add independent inputs):**

- The `loss` input (1.5 / 3 / 5%, Paytm worst case) stays the anchor.
- Share of loans that ever reach 90+ days: p90 = loss / (owed × (1 − recovered)), with owed = 0.5 (fixed, judgement).
- Share that reach 61–90: p60 = p90 / (1 − cure_b2).
- Share that reach 31–60: p30 = p60 / (1 − cure_b1).
- Show the implied p30, p60 and p90 so the operator can see them. Flag any draw where p30 > 40%.
- Fees per loan made = p30 × cure_b1 × fee_b1 + p60 × cure_b2 × fee_b2 + p90 × recovered × fee_b3.
- Timing: the 31–90 fees come about 9 months after disbursal, the 90+ fees about 18 months after.
- `dpd30_rate`, `dpd30_emis`, `dpd30_resolve` and `rec_fee` are dropped. Keep `rate` 26% for EMIs only if still used elsewhere.
- Confidence for fee_b1–3 and cure_b2: "Industry guide, not verified" (a vendor table with no stated source). For recovered: "Published" (Paytm) at the low end; mark the range as judgement.

## Products: updated tickets

| key | new value | evidence | confidence |
|---|---|---|---|
| hlth_family ticket | pert ₹5,500 / 8,000 / 15,000 a year, excluding GST, for ₹3–5 lakh floater cover | GAP-04 ₹5,581–6,560 for ₹5 lakh at age 30; family of four at 35 costs more | Industry guide |
| shop ticket | pert ₹250 / 700 / 2,600 a year | GAP-05 (Digit via Fino: ₹550 for ₹3 lakh, ₹2,600 for ₹15 lakh; ICICI Lombard from ₹250) | Published |
| loan_gold fee | keeps 0.5 / 1 / 1.5% | no gold-loan payout found (GAP-06); general DSA 1–3% | Our judgement |

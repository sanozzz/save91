# Cross-selling loans: what can it earn per saver?

**Bottom line:** Referring savers to lenders adds about **Rs 10 to Rs 115 per active saver per year** (mid case, all loan types together, ~Rs 115). The gap is **Rs 1,029** (Rs 1,168 needed minus Rs 139 today). Lending closes roughly **a tenth of it**. The only lending route that reaches "hundreds" per saver is acting as a full-service lender partner that guarantees the loans (a DLG, a default-loss guarantee). That means the app's own cash pays when savers default, which works against a "save first" brand.

All evidence is in `xs_lending.csv`, rows XL-01 to XL-54, accessed 2026-10-02.

## How to read the table

- **Rs per saver per year = take rate × ticket × take-up.** Take-up means approved loans *through the app* per active saver per year.
- **Take rate and ticket come from sources.** **Take-up is my estimate.** No public source measures it for a savings app, so I anchored it on the closest real numbers:
  - Only **6% of delivery riders ever** took a digital loan (XL-37).
  - A loan app approves **11% of new applicants** and **74% of repeat borrowers** (XL-41).
  - **Under 1%** of Paytm's monthly users take any financial product in a quarter (XL-04).
- The gap to close is **Rs 1,029** per saver per year.

| Product | Take rate low / mid / high | Ticket (Rs) low / mid / high | Take-up per saver per year low / mid / high | **Rs per saver per year** low / mid / high (calculation for mid) | Licence needed | Verdict | Evidence |
|---|---|---|---|---|---|---|---|
| Small personal loan, referral (no guarantee) | 1% / 2% / 3% | 15k / 25k / 58.5k | 1% / 3% / 8% | **1.5 / 15 / 140** (2% × 25,000 × 3%) | LSP contract with each lender, or DSA empanelment; no RBI licence | Small | XL-13, 41, 42, 29, 37, 45, 48 |
| Personal loan as full lender partner **with guarantee** (gross fee) | 4.5% / 5% / 7.5% | same | same | **6.8 / 37.5 / 351 gross**; the guarantee can cost up to 5% of the loan, about Rs 234 at the high case | LSP, plus cash or FD pledged up to 5% of loans | Reaches hundreds only by taking credit risk. **Not recommended** | XL-02, 07, 10, 11, 49 |
| Two-wheeler incl. EV | 0.5% / 1% / 2% | 70k / 94k / 120k | 0.2% / 0.5% / 2% | **0.7 / 4.7 / 48** (1% × 93,900 × 0.5%) | DSA / dealer tie-up | Small | XL-19, 21, 22, 23, 31, 36, 50 |
| Auto-rickshaw, used car, commercial vehicle | 0.5% / 1% / 2% | 1.5L / 3L / 6L | 0.1% / 0.3% / 1% | **0.75 / 9 / 120** (1% × 3L × 0.3%) | DSA | Small | XL-18, 44, 54 |
| Gold loan | 0.5% / 1% / 1.5% | 30k / 75k / 1.5L | 1% / 3% / 8% | **1.5 / 22.5 / 180** (1% × 75,000 × 3%) | DSA / referral partner | Small, and the safest loan to refer | XL-17, 29, 32, 52 |
| Home loan (affordable) | 0.3% / 0.5% / 1% | 8L / 11L / 15L | 0.05% / 0.2% / 0.5% | **1.2 / 11 / 75** (0.5% × 11L × 0.2%) | "Connector" or DSA with a housing finance company | Small: a big fee per loan but very rare | XL-15, 24 to 27, 30, 51 |
| Property loan / small-business loan / working capital | 1% / 2% / 2.5% | 50k / 1L / 2L | 0.5% / 1.5% / 3% | **2.5 / 30 / 150** (2% × 1L × 1.5%) | DSA. Mudra and PM SVANidhi pay **nothing** | Small. Best non-risk upside, shopkeepers only | XL-14, 16, 43, 53 |
| Phone / consumer-durable EMI | 1% / 2% / 3% (assumed, no data) | 10k / 20.6k / 30k | 0.5% / 2% / 5% | **0.5 / 8 / 45** (2% × 20,600 × 2%) | DSA. Sold at the shop counter, so hard for an app to win | Small | XL-29, 35, 54 |
| Credit card (FD-secured) | Rs 300 / 750 / 1,500 per card (assumed; ordinary cards pay Rs 1,000 to 2,400) | n/a | 0.5% / 2% / 5% | **1.5 / 15 / 75** (Rs 750 × 2%) | DSA / DMA; the bank decides who gets a card | Small, but fits the story well | XL-20, 40, 54 |
| Microfinance group loans (business correspondent) | no data | n/a | n/a | **not computable** | Business correspondent agreement with a bank, a 5 to 10% first-loss deposit, and weekly field meetings | Not reachable for an app-only business | XL-33, 34 |
| **All lending, excluding the guarantee route** | | | | **~10 / ~115 / ~833**. The high case assumes every product does its best at once, which is not plausible | | Closes about 11% of the gap at mid | XL-54 |

**Cross-checks from listed companies:**

- **Paisabazaar** earns at most **4.6% of loans disbursed**: Rs 127 crore on Rs 2,776 crore, Q1 FY27. Card fees are included, so the true loan figure is lower (XL-09).
- **Paytm** earned at most **3.9%** in its last quarter that disclosed both numbers: Rs 607 crore on Rs 15,535 crore, Q3 FY24 (XL-45).
- **PhonePe** merchant loans earned **7.3%**: Rs 328 crore on Rs 4,507 crore, FY25. This fee covers collecting repayments over the loan's life (XL-11).
- A one-off referrer should expect **1 to 3%**. Even Paytm makes only about **Rs 350 to 430 per monthly user per year**, before costs, from all its financial products together (XL-05, XL-06). India's biggest payments-to-credit distributor does not reach Rs 1,000 per user.

## What would have to be true

**Home loans.** Each loan pays well: about Rs 2,400 to Rs 15,000 (XL-51). To close the gap alone, **7% to 19% of savers** would need to take a home loan through the app every year. That cannot happen. India books about 31 lakh home loans a year across *all* borrowers (XL-28).

For even the mid case (0.2% a year), all of these must hold:

1. **Income.** Savers' household income must reach the level affordable lenders serve, up to about Rs 50,000 a month. Their records (Home First, XL-25) show that **86% of their borrowers already have a credit history**.
2. **Down payment.** Aavas lends on average 55% of the property value (XL-24). For an Rs 11 lakh loan the saver needs roughly Rs 4 to 9 lakh up front. At Rs 100 a day that is 10 to 25 years of saving.
3. **Lender access.** The app must sign up as a "connector" with a housing finance company. This part is realistic: **77% of Home First's leads come from connectors** (XL-25).

The government's PMAY-U 2.0 subsidy (up to about Rs 1.8 lakh, XL-26) helps the borrower, not the referrer.

**Verdict:** "your savings became your down payment" is a great story, but it is not a revenue line.

**Two-wheeler loans.** Each loan pays about Rs 350 to Rs 2,400. Closing the gap would need more than 40% of savers financing a bike every year.

For it to matter at all:

- **Timing.** The app must reach riders before they buy. Today 73% already own a bike and 15% rent one, and most bought before joining the platform (XL-36).
- **The shop counter.** The app must beat the dealer's own financier and platform deals such as Swiggy with Hero (XL-23).
- **Lender appetite.** Lenders must approve thin-file riders. In 2025 they were tightening two-wheeler lending because of rising defaults (XL-31).

The better customer story is a rider moving from renting an EV (Rs 120 to 160 a day) to owning one (XL-22). That still pays only about Rs 1,000 per bike, once.

## Risks

**Regulatory**

- The lender must pay the app. The app cannot charge borrowers or route repayments through itself (XL-01).
- If the app works with several lenders, it must show every matching offer side by side and must not push any one lender (XL-46).
- Any guarantee is capped at 5% of loans and must be pledged as cash, an FD or a bank guarantee (XL-02).
- **Most users count as "microfinance" borrowers in law.** Households earning up to Rs 3 lakh a year (about Rs 25,000 a month) fall in this group. Every lender must cap their total repayments at 50% of household income (XL-34). Industry rules add a maximum of 3 lenders and Rs 2 lakh of total debt per borrower.
- Mudra and PM SVANidhi allow no agents and pay no fee (XL-43).
- An RBI draft would cap all-in interest rates on loans up to Rs 50,000 from April 2027. That may shrink lenders' appetite for exactly these tickets (regulation_rails.csv REG-078).

**Credit**

- About **1 in 3 rider borrowers missed a payment** (XL-36).
- Lenders claw back the referral fee if a loan defaults or closes within 6 months (XL-47).
- Small loans have high early default rates: 6 to 9% of small personal loans and over 10% of small-business loans reach 90 days overdue (MAC-03, NG-015).
- The guarantee route turns these losses into the app's own losses.

**Reputational**

- Pushing loans at 20 to 30% a year to people who joined to *save* invites the "loan-app trap" label.
- 39% of riders face money shocks averaging Rs 61,000, about four months' pay (XL-38). A loan offer at that moment can feel predatory.
- A lender's repayment mandate can compete with the savings Autopay mandate. A default under the app's name would also hurt trust in the savings product.

**Safer design if lending is tested:**

- Offer credit only after months of steady saving. Repeat borrowers are approved at 74% versus 11% for new applicants (XL-41).
- Start with secured products: FD-backed cards and gold loans.
- Cap loan size relative to the saver's savings.
- Never provide a guarantee.

**Closest competitor:** Bachatt already offers loans up to Rs 5 lakh through 9 partners. The partners include middleman platforms (GroMo, Moneyview, Kissht), so Bachatt likely shares the fee (XL-12). It discloses no volumes or revenue.

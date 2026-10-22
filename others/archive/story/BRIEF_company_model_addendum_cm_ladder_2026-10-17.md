# Addendum: the financial statements (operator, 17 Oct 2026)

## What the operator said (verbatim)

> "I am hoping we will be building financial model as well where i can look at my cm1,2,3 and revenue and ebitda and pat over month on month and rollup numbers and cashflow numbers of the company"

> "ok, do add that in the google sheet as well"

## Decisions (taps)

- **Ladder:** transaction → serve → acquire.
- **Agent cost:** split by time.
- **Capex:** capitalise, decided by the lead because the operator said "you decide. I guess capitalize".

## The P&L ladder (monthly, then rolled up by year)

| Line | What it contains |
|---|---|
| **Revenue, by line** | Net of fees taken back; GST passes through. Lines: fund trail; personal-loan origination; top-ups; housing loans; other lenders' loans; cards; insurance (net of the broker's share); investments; payments; collection fees. |
| − **Direct costs** | Bureau pulls (₹25 per loan application); fraud provision (0.05% of cash collected). |
| **= CM1** | Transaction margin |
| − **Field servicing** | The SERVICING share of agent cost (salary + 0.25% incentive + statutory ₹3,000); helpers for cash visits; cash cover; the running cost of ₹5 a saver a month; team leads; city managers; city offices. |
| **= CM2** | After serving the book |
| − **Acquisition** | The ACQUISITION share of agent cost; online leads; KYC; agent hiring and kit (₹12,000 per hire, including replacements); city launch (₹3 lakh); brand marketing (₹2 lakh a month). |
| **= CM3** | After acquiring customers |
| − **Central costs** | Central team (salaries + 10% statutory + 7% raises); app cloud base (₹1.5 lakh a month); licences and compliance (yearly ₹10 lakh; one-time ₹15 lakh excluding integrations, expensed); HQ office; travel; tools; fundraising costs (expensed when incurred); 10% contingency on all opex lines above. |
| **= EBITDA** | |
| − **Depreciation** | Laptops (₹60,000 per central hire) and app integrations (₹15 lakh), each over 36 months, straight-line from the month bought. |
| **= EBIT** | |
| − **Tax** | 25% on positive EBIT after past losses are used (carry the losses forward). |
| **= PAT** | |

**Agent cost split:**
- For each agent, by HIS tenure month k, the acquisition share = 50% for k = 1–12, then a straight line down to 20% at k = 60.
- The rest is servicing.
- A replacement hire restarts at k = 1.

## The cash-flow statement (monthly, then by year)

| Section | Lines |
|---|---|
| **Operating** | PAT + depreciation − increase in commissions receivable (revenue arrives 2 months after it is earned) − tax actually paid (the same month as the expense). |
| **Investing** | − capex (laptops, integrations). |
| **Financing** | + seed ₹10 crore at m0, + Series A ₹75 crore at m18. Raise costs sit in central costs. |
| **Closing cash** | Net change and closing cash; the lowest cash point and its month. |

## Outputs (add to the company model)

- `tables/company_monthly.csv`: every line above, months 1–60.
- `tables/company_yearly.csv`: years 1–5, the same lines summed, plus closing cash.
- `tables/company_pnl_ladder_yearly.csv`: an investor-format P&L with CM1/CM2/CM3 as % of revenue.
- `tables/company_cashflow_yearly.csv`.
- **Checks:**
  - CM1 − servicing − acquisition − central = EBITDA every month;
  - cash closing(t) = closing(t−1) + net change;
  - the sum of the yearly columns equals the sum of the monthly ones.

## Google Sheet (later, by the toy agent, after review)

Add these tabs:
- "Company inputs": hiring plan, team table, costs, funding — blue cells.
- "Company monthly": the P&L ladder and cash flow by month, as formulas.
- "Company yearly": roll-ups with SUMIFS by year.
- "Company summary": month-18 metrics, runway, the lowest cash point, EBITDA break-even month.

The toy's one-agent lines by tenure month are stacked with the hiring plan, using one MMULT/MAKEARRAY formula per line, the same technique as the toy's monthly tab.

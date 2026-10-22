# Brief: the company model, from one agent's unit economics to company financials

## What the operator said (17 Oct 2026, verbatim)

> "Assume we create a company and have online + offline channel spend every month. Lets say we want to raise $1m for seed and then move from there. Eventually in next 18 months do a bigger round. So how many people to hire which department, app cost, etc... we should model everything... focus on acquiring customers etc have those assumptions too... and extend this model eventually to that"

> "even the toy model should extend like that and we should have company financials with year level numbers and licence costs etc"

> "also make sure we bake in all other small to big costs"

**Metric:** undiscounted cumulative P&L and cash. No NPV (operator).

Project: `~/Desktop/Random/savings-first-deck/`. Python: `~/.cortado-venv311/bin/python`.

## Build on the agent unit, do not rebuild it

- `model/cohort_engine.py` `run(x)` gives one agent's monthly lines for months 1–60 of HIS tenure. This includes his own sign-ups, savers, cash visits, every revenue line and the agent-level costs (salary, 0.25% incentive, helpers for cash visits above 400 a day, online leads, KYC, the ₹5 running cost a saver, cash cover).
- Inputs: `tables/dist_agreed_v1.csv` (95+ inputs, all agreed; round 9 has the fee ramp from a DSA's 1.75% to 1.5×).
- **The fee ramp and the calendar-growth inputs** (take-up and approvals growing with the pool's history) belong to COMPANY calendar time, not agent tenure. When you stack agents hired at different months, apply the company-month multipliers correctly; refactor `run()` to take a start-month offset if needed. Keep `legacy=True` working.

## Company inputs (all agreed by the operator in taps, 17 Oct)

**Fleet:**
- Agents on the street, by company month (end of month):
  - m3: 5;
  - m6: 10;
  - m9: 20;
  - m12: 30;
  - m15: 45;
  - m18: 60;
  - m36: 150;
  - m60: 300.
  Linear between points.
- Each agent draws his own sign-up level and decline (`signups_run`, `signup_decline_y5`) from the agreed distributions (operator: "each guy will be different").
- Market-level inputs (retention, take-ups, fees, losses and so on) are common to all agents within a draw.

**Attrition:**
- 30% of agents leave a year.
- A leaver is replaced by a new hire, who inherits the book.
- 10% of the inherited savers stop at the handover.
- The new agent starts his own sign-ups from tenure month 1 (ramp).
- Replacement hires incur the hiring and kit costs again.

**Cities:**
- 1 at the start; 2 from m9; 3 by m18; then one city per 50 agents.
- ₹3 lakh launch cost per new city, once.
- ₹50,000 a month per city office.
- One city manager at ₹80,000 a month per city.
- One team lead at ₹40,000 a month per 10 agents.

**Central team (lean), monthly pay; hired at m0 unless stated:**

| Role | Count | Pay a month |
|---|---|---|
| Founders | 2 | ₹1.5 lakh |
| Tech lead | 1 | ₹2.5 lakh |
| Engineers | 3 (2 at m0, 1 at m3) | ₹1.2 lakh |
| Product/design | 1 (m2) | ₹1.5 lakh |
| Compliance + ops head | 1 | ₹1.5 lakh |
| Ops executives | 2 (m3) | ₹40,000 |
| Growth/marketing | 1 (m3) | ₹1.2 lakh |
| Finance/admin | 1 (m1) | ₹70,000 |

- Scale-up after m18: +1 engineer per 50 agents beyond 60, +1 ops executive per 50 agents, and the city and team-lead rules above.

**Team extras (operator: "Leaner"):**
- +10% statutory on all central and field-management salaries;
- 7% raises each year;
- laptop ₹60,000 one-time per central hire;
- no recruiting fees.

**Agent extras (operator: "Leaner"):**
- +₹3,000 a month per agent (statutory only; no fuel allowance);
- ₹12,000 one-time per hire, including replacements (he uses his own phone).

**App (build in-house):**
- the engineers are above;
- cloud, SMS and KYC tools ₹1.5 lakh a month base;
- ₹15 lakh one-time for integrations (funds, insurance broker, lenders) at m1–m3.

**Licences and compliance (operator: "Lower (lean)"):**
- one-time ₹15 lakh in total: company setup ₹1 lakh, AMFI ARN/NISM ₹0.5 lakh, legal opinion on the cash route ₹6 lakh, integrations counted in the app;
- yearly ₹10 lakh: audit/CA/secretarial ₹5 lakh, infosec/DPDP ₹3 lakh, insurance and misc ₹2 lakh.

**Overheads (lean):**
- HQ ₹1.5 lakh a month;
- city offices as above;
- travel ₹1 lakh a month;
- brand marketing ₹2 lakh a month. Online leads are already in the agent unit.

**Small costs:**
- bureau pulls ₹25 per loan application;
- fraud provision 0.05% of cash collected (cash deposits = deposits × cash share);
- UPI fees ₹0 (they run on the fund's rails);
- tools ₹1,000 a month per central person.

**Finance:**
- commissions arrive 2 months after they're earned. Model cash separately from the P&L;
- GST passes through (no P&L effect);
- income tax 25% on profit after past losses are used;
- 10% contingency on all running (opex) costs.

**Funding:**
- seed ₹10 crore at m0 (operator: about $1M at ₹100), with ₹5 lakh raise costs;
- Series A ₹75 crore at m18, with ₹15 lakh raise costs.

## Outputs

1. **`model/company_model.py`** (deterministic, at the likely values plus the agent-level draws) writes:
   - `tables/company_monthly.csv`, months 1–60:
     - agents (start, hired, left), cities, central headcount by department;
     - savers, AUM, money lent;
     - revenue by line, costs by line, EBITDA, tax, net profit;
     - cash in and out, cash balance;
   - `tables/company_yearly.csv`, years 1–5, in investor-style P&L format: revenue by line, costs by department, EBITDA, PAT, closing cash, headcount, savers, AUM, money lent;
   - `tables/company_headcount.csv`, by department by year;
   - `tables/company_m18.csv`, the metrics at month 18 for the Series A story:
     - savers;
     - AUM;
     - money lent;
     - monthly revenue run-rate;
     - burn;
     - cash left;
     - agents and cities;
     - cost to win a saver;
     - contribution per agent.
2. **`model/company_mc.py`**, a Monte Carlo of 2,000 draws:
   - market inputs drawn once per draw, and agent sign-up levels drawn per agent;
   - use the agent-type approach if needed for speed (for example 20 agent types sampled per draw), documented.
   - Outputs: `tables/company_mc_summary.csv`, covering:
     - P(cash stays above 0 before m18);
     - the minimum cash and the month it occurs;
     - P(cash stays above 0 through m60 with the Series A);
     - extra funding needed (if any) to m60;
     - EBITDA break-even month;
     - year-5 revenue, EBITDA and PAT at p10/p50/p90;
     - savers and AUM at m18 and m60.
3. **Checks:**
   - one agent hired at m1 with no attrition and no central costs reproduces `cohort_engine` at the likely values, with the fee ramp aligned;
   - headcount × salary reconciles to the people cost;
   - cash = P&L ± the timing differences.

   Write `tables/company_checks.csv`.

## Report (under 300 words)

- Year-by-year revenue, EBITDA, PAT and closing cash.
- Headcount by year.
- Runway on the seed: is cash ever below 0 before m18?
- The m18 metrics.
- The extra funding needed to m60, if any.
- The MC summary.
- Approximations.
- Paths.

Do not touch other files beyond the refactor of `cohort_engine.py`, if one is needed. Keep its outputs identical.

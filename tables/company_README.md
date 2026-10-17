# Company model tables (written by model/company_model.py and model/company_mc.py; do not edit by hand)

Rupee values are in rupees. Months are company months 1-60; year 1 = months 1-12. Spec: story/BRIEF_company_model_2026-10-17.md,
the CM-ladder addendum and story/FIXES_company_round1_2026-10-17.md. One agent's economics come from model/cohort_engine.py.

## Tables
- company_monthly.csv: every line, month by month (fleet, headcount, savers, AUM, lending, the P&L ladder, the cash flow).
- company_yearly.csv: the same lines by year (flows summed, stocks at year end).
- company_pnl_ladder_yearly.csv: investor-format P&L: revenue, CM1, CM2, CM3 (with shares of revenue), EBITDA, interest, PAT.
- company_cashflow_yearly.csv: operating, investing, financing, closing cash, the lowest cash and its month.
- company_headcount.csv: headcount by department and role at each year end.
- company_m18.csv: the Series A story at month 18, the seed run-out, the slips and the smallest Series A.
- company_fleet_scenarios.csv: the growth J-curve: base (60 -> 300), hiring frozen at 60 after m18, frozen at 150 after m36.
- company_mc_summary.csv: 2,000-draw Monte Carlo.
- company_checks.csv: the reconciliations; every row must say Passes = True.

## Staffing rules
- Agents (round 10 base): grow to 80 by m18 (m0 0, m3 7, m6 13, m9 27, m12 40, m15 60, m18 80), then hire only to replace leavers; 30% leave a year, replaced the next month; the replacement inherits the book (10% of its savers stop). The growth plan (60 at m18, 300 by m60) is a scenario.
- Central team (round 10 base): lean hold: after the launch team, no central hires until EBITDA first turns positive, except the cash-reconciliation and HR executives that scale per agent; then the rules below apply.
- Cities: 1 from m1, 2 from m9, 3 from m18, then one per 50 agents (rounded up). One city manager per city; one team lead per 10 agents (rounded up).
- Central team at the start: Founders 2 from m1; Tech lead 1 from m1; Engineers 2 from m1, 3 from m3; Product and design 1 from m2; Compliance and operations head 1 from m1; Operations executives 2 from m3; Growth and marketing 1 from m3; Finance and admin 1 from m1.
- Engineers and operations executives: +1 each per 50 agents beyond 60, after m18 (rounded down; the 'beyond 60' applies to both).
- Risk and fraud lead: from the month the fleet reaches 100 agents; Cash reconciliation executives: 1 per 50 agents, rounded up from the first agent; HR and recruiting executives: 1 per 100 agents, rounded up from the first agent; Customer support lead: from the month the company has 50,000 savers.
- Pay: +10% statutory on central and field-management pay; agents + Rs 3,000 a month statutory; everyone's pay (agents too, their statutory with it) rises 7% each company year. Agent pay on balance: 0.25% a year of his book's balance, capped at Rs 10,000 a month per agent (the cap rises with the salary).

## Money rules
- Ladder: revenue - direct (bureau, fraud) = CM1; - field servicing = CM2; - acquisition = CM3; - central = EBITDA; - depreciation = EBIT;
  + interest on cash (5.5% a year on the opening cash) = profit before tax; - tax (25% after past losses) = PAT.
- Agent cost (salary, statutory, pay on balance) is split by his tenure: 50% acquisition in months 1-12, falling to 20% at month 60.
- Laptops and integrations are capitalised over 36 months; commissions arrive 2 months after they are earned.
- Funding: seed Rs 10 crore at m0, Series A Rs 50 crore at the end of m18; their costs are expensed in central costs.

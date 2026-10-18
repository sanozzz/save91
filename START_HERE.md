# START HERE: "save first, borrow later", an offline savings business

**State as of 18 Oct 2026.** The current company case is the refresh in `story/REFRESH.md` and `tables/refresh_*.csv`. It keeps the published fleet and the ₹350-a-day debt fund, and replaces the loan ticket, the apply rate, the NBFC borrowings, the UPI share and the bought-lead cost with figures the folder already had. `tables/base_*.csv` is the 17 Oct base, kept so the old headlines can be checked. The deck `Offline_model_v3.pdf` still shows that old base. The OD++, the small amount a customer is happy to save, the 80/20 fund mix and a month for the online 1 to 1.5 lakh were not given as numbers, so they are not in the refresh.

**To Claude, if you are reading this for someone:**
- **Current vs superseded.** Answer from the CURRENT files listed in section 7, and say which file each answer comes from. Many files are earlier rounds of the same work and are superseded; they are marked as such.
- **Kinds of input.** Separate what is evidence, what is the operator's own number, and what is judgement. Each input carries a confidence label in `tables/dist_agreed_v1.csv`.
- **Results.** Model results are only as good as the inputs. The headline numbers below come from a Monte Carlo over agreed ranges, not from a single forecast.

---

## 1. What we are building

India's self-employed daily earners (shopkeepers, vendors) already save in cash every day with a bank's "janta deposit" agent, but earn only a bank savings-account rate, about 2.5%. We would serve them **physically**: a salaried **fleet of agents on the street**, plus a **customer app**.

1. **Omni-channel acquisition, offline service.** Each agent opens about 100 accounts a month at first, falling to about 70 by year 5 as his book grows. Half come from online leads we buy (about ₹250 each); half he finds on the street.
   - He serves every saver himself on a daily route: cash pickups every 2–3 days for savers who pay cash (about ₹350 a day), and visits to UPI savers.
   - There is no app-only channel.
   - Evidence: a field-led savings fintech's agents onboard 100+ a month, top agents 120–150 (`research/practitioner_2026-10-17.csv`, PR-01).
2. **The fund.** The money goes into a **debt fund in the saver's own name**, earning about 7%. That return is the hook: about ₹1,890 a year more than a janta deposit on ₹350 a day.
3. **The marketplace.** From day one a Paisabazaar-like marketplace offers loans (personal, home, against property, gold, consumer and vehicle), credit cards, insurance, investments and payments. Lenders and insurers decide; we list, at no cost to us.
4. **Collections.** Because the agent knows the customer, he also helps collect overdue loans for lenders, for a fee.

We earn:
- the fund distributor's trail (0.35% a year of balance);
- loan origination fees (about 2.6% of each loan, i.e. 1.5× a DSA's rate);
- card fees;
- insurance and investment commissions (insurance through a broker partner, who keeps about 25%);
- collection fees.

**The question:** can we acquire and keep this customer more cheaply than online, and earn more from the relationship than the agent costs?

## 2. The story (deck: `Offline_model_v3.pdf`)

**The customer's problem** (`story/CUSTOMER_PROBLEM.md`). The published deck does not have this page yet. It still opens on our cost of winning him.

1. He is sold a product on the word of an investment person he knows. Nothing is recorded. The method is "believe me".
2. He cannot start a small SIP on his own. A small instalment happens today because a person comes and collects it.
3. Once the money is in, he is forgotten. Nobody comes back to ask what else he needs.

1. **The problem with online** (pages 1–3). It costs about ₹499 to win a daily saver online, and only 24 in 100 still save after a year, so each saver kept costs about ₹2,067. The app never earns it back.
2. **Our approach** (pages 4–8):
   - the 7% hook;
   - the fleet plus app;
   - how his cash reaches the fund;
   - the marketplace from day one;
   - the agent helps collect.
3. **What our analysis says** (pages 9–15):
   - a monthly cohort model run 10,000 times;
   - the chance of profit;
   - where the money comes from;
   - what grows with history;
   - what must be true;
   - what could break it;
   - the answer: pilot one salaried agent for 12 months.
4. **Appendix** (A1–A14):
   - every assumption as a distribution, with sources;
   - the bridge from the previous deck;
   - loans, cross-sell and collections detail;
   - year by year;
   - the online cost method;
   - the one interview;
   - what is left out;
   - sign-ups; agent pay.

## 3. Where it stands now (current base case)

**Base case:**
- one agent, **about 100 sign-ups a month** in year 1 (range 60–150 across agents), falling in a straight line to about 70% of that by year 5;
- half from online leads at about ₹250 each (range ₹150–499);
- **₹20,000 a month salary + 0.25% a year of his savers' balance, capped at ₹10,000 a month**, during the 5-year growth phase (0.10% after);
- loan origination fee: a DSA's rate (1.75%), rising in a straight line to 1.5× (about 2.6%) by month 60;
- still saving at month 12: 55% likely (range 25–72%);
- UPI 30% of a cohort by month 12, with paid helpers for cash visits beyond his 400 a day;
- debt fund at 0.35% trail;
- running cost ₹5 a saver a month;
- cash cover ₹1,000 an agent a month.

All numbers are **undiscounted cumulative P&L** for one agent. The operator's choice: no discount rate; investors can apply their own.

| One agent, 10,000 Monte Carlo draws | Result |
|---|---|
| Chance cumulative P&L is positive by month 60 | **94%** |
| Chance it is positive by month 36 | **36%** |
| Cumulative P&L at month 60: p10 / median / p90 | +₹2.6 lakh / **+₹16.6 lakh** / +₹37.7 lakh |
| Payback month: median (p10–p90) | **40** (29–55) |
| Peak cash need per agent (median) | **₹4.7 lakh** |
| Year-1 P&L (median) | −₹3.7 lakh |
| Savers in his book at month 60 (likely values) | about 2,240 |
| Peak cash visits a day (likely values) | about 668 (he can make 400; helpers cover the rest) |
| Over 60 months (likely values): helper cost / online lead cost | ₹3.0 lakh / ₹6.7 lakh |
| Revenue per active saver a year (median) | ₹732 (Paytm earns about ₹407 per monthly user from financial services) |

Sources: `tables/cohort_mc_summary.csv`, `tables/cohort_det_summary.csv`; deck pages 10–15.

**Honest reading:**
- At the most-likely values one agent breaks even over 5 years at about **44 sign-ups a month** (`tables/cohort_signups_sweep_likely.csv`), so 100 leaves a wide margin.
- **Over 3 years it is a coin toss at best** (36%).
- The incentive is the largest single lever the operator controls. Salary only gives 98.5%; the operator rejected salary-only and chose the ₹10,000 cap; see §4.

**The pilot's main job is to measure two things:**
1. how many savers one agent can open a month while also serving his book;
2. how many of them move to UPI.

## 3b. The company plan: the FINAL BASE (17 Oct 2026, late)

**How we got here:**
1. **Unicorn track.** The operator chose "unicorn by year 5".
2. **Real-world cities** ("We can't outgrow a city").
   - The pool is about **7 crore urban self-employed** (NG-002; the operator's "30 crore" is e-Shram's 31.9 crore unorganised workers, SEG-02, shown as context).
   - Cities are sized on a rank-size curve (estimate), across about 500 Class I cities.
   - At most **20%** of a city's pool can ever be signed.
   - The slowdown is soft (1 − (pen/cap)²), the pool refills 3% a year, and we open ≤ 4 cities a month.
   - So about **91 lakh people** is the national ceiling.
   - Without own-book lending, no plan is a unicorn on both lenses by m60: the revenue lens is ~35% short.
3. **NBFC from month 30.** The operator chose it, and picked **30% of personal loans (the top-quality 30%) on our own book**.

**The base** (`tables/base_*.csv`; deck Part 4; inputs in `tables/base_inputs.csv`):
- **Fleet:** 300 agents by month 18, then +150 a month to 5,000. Cities open in size order (NCR first), 172 by year 5.
- **The NBFC's own book:**
  - 26% yield and a 2% processing fee;
  - 13.5% cost of funds;
  - 3× leverage, capital ≥ 15%;
  - loss 0.6× the agreed rate;
  - ₹10 crore of owned funds and a ₹1 crore licence.

| ₹ crore | Y1 | Y2 | Y3 | Y4 | Y5 | Y6 | Y7 | Y8 |
|---|---|---|---|---|---|---|---|---|
| Revenue | 0.5 | 7 | 57 | 228 | 468 | 599 | 617 | 572 |
| EBITDA | −9 | −48 | −148 | −155 | −8 | 150 | 156 | 96 |
| PAT | −8 | −39 | −129 | −126 | 17 | 171 | 167 | 100 |
| Closing cash | 58 | 218 | 655 | 579 | 380 | 435 | 601 | 753 |
| Active savers (lakh) | 0.6 | 4.7 | 20 | 35 | 37 | 32 | 28 | 24 |
| Own loan book | 0 | 0 | 148 | 727 | 1,576 | 2,048 | 2,068 | 1,874 |
| Agents | 150 | 1,200 | 3,000 | 4,800 | 5,000 | 5,000 | 5,000 | 5,000 |
| Cities | 20 | 68 | 116 | 164 | 172 | 172 | 172 | 172 |

**Rounds:**

| Round | Month | Raise (₹ crore) | Pre-money | Post-money | Founders after |
|---|---|---|---|---|---|
| Seed | 0 | 13 | 40 | 53 | 65.5% |
| A | 9 | 53 | 159 | 212 | 47.3% |
| B | 18 | 212 | 636 | 848 | 34.2% |
| C | 32 | 605 | 2,227 | 2,832 | 26.9% |
| D | 48 | 215 | 7,620 | 7,835 | 26.1% |
| E | 57 | 10 | 11,753 | 11,763 | 26.1% |

Total raised: **₹1,108 crore**.

**Unicorn on paper from month 59, only just.** At month 60:
- 20× ARR = ₹11,043 crore (+10%);
- 0.45× AUM = ₹10,073 crore (**+0.7%**);
- the lending cross-check (3× NBFC book equity + 20× fee ARR) ≈ ₹6,890 crore ($0.69B).

Monte Carlo (1,000 draws): both lenses clear at m60 in **29%**; EBITDA is positive by m60 in 56%.

**Which share on book** (`tables/share_compare.csv`):

| On-book share | Raised | Unicorn on paper | Year-5 PAT | Notes |
|---|---|---|---|---|
| 15% | ₹643 crore | no | ₹32 crore | founders 30% |
| 30% (base) | ₹1,108 crore | from month 59 | ₹17 crore | |
| 50% | ₹1,033 crore | yes | ₹94 crore | the most credit risk; cash survival 74% |

**After year 5 the business shrinks.** Cities fill, sign-ups slow and churn continues, so active savers fall from 37 lakh to 24 lakh by Y8. Growth beyond Y5 needs new levers:
- smaller towns;
- a wider segment;
- more products per saver.

**Earlier plans are kept for reference:**
- the unicorn track without city limits (`unicorn_*`);
- the round-10 plan (`company_*`);
- max growth with Y5 PAT ≥ 0 (`growth_*`);
- the $100M ARR path (`arr100m_*`);
- real-world runs (`rw_*`, `sat_*`);
- NBFC tests (`nbfc_*`, `base15_*`, `base50_*`).

## 4. What moves the answer most

Swing in 5-year cumulative P&L when each input moves from its bottom tenth to its top tenth (`tables/cohort_mc_drivers.csv`):

| Input | Swing |
|---|---|
| Personal-loan size | ₹20.1 lakh |
| Still saving at month 12 | ₹17.8 lakh |
| Savers who apply for a loan, a year | ₹15.4 lakh |
| Sign-ups a month in year 1 | ₹15.2 lakh |
| Take-up growth with our pool's history | ₹9.9 lakh |
| Origination fee at the start (a DSA's rate) | ₹9.7 lakh |
| Approval growth with history | ₹9.5 lakh |
| Applicants eligible | ₹8.9 lakh |

**Sign-ups target** (year-1 level, with the 70% decline by year 5; `tables/cohort_signups_sweep.csv`; deck A13):

| Sign-ups a month in year 1 | In profit by month 60 | By month 36 |
|---|---|---|
| 40 | 43% | 1% |
| 60 | 78% | 7% |
| 80 | 91% | 24% |
| 100 | 95% | 37% |
| 120 | 96% | 45% |
| 150 | 98% | 54% |

**Agent pay** (`tables/cohort_incentive_sweep.csv`; deck A14):

| Agent pay | In profit by month 60 | Median 5-year P&L |
|---|---|---|
| Salary only | 98.5% | ₹21.4 lakh |
| + 0.25% for 2 years, then 0 | 98% | ₹20.0 lakh |
| + 0.25% for 1 year, then 0.10% | 96% | ₹17.7 lakh |
| + 0.25% for 2 years, then 0.10% | 96% | ₹17.0 lakh |
| **+ 0.25% of balance capped at ₹10,000 a month (the base)** | **94%** | **₹16.6 lakh** |
| + 0.25% of balance, uncapped | 90% | ₹12.4 lakh |

## 5. Decisions the operator has made (16–17 Oct 2026)

Every model input is agreed, as a distribution (low / likely / high), in `tables/dist_agreed_v1.csv` and `Assumptions_agreed.pdf`. The main decisions:

- **Fund:** debt fund (0.35% trail), not a liquid fund (about 0.05%).
- **Sign-ups and channel (round 8, 17 Oct):**
  - 100 a month per agent in year 1 (60–150 across agents), falling to about 70 by year 5.
  - Half from online leads at about ₹250, all served offline by the same agent.
  - No app-only channel; no split between openers and collectors.
  - This rests on practitioner evidence (PR-01). Earlier rounds used 30, then 60, then 83 a month.
- **Retention:** 55% still saving at 12 months is most likely.
- **Cards:** 3% of savers get one (the evidence), not 5%.
- **Marketplace:** opens in month 1, at no cost to us. In months 1–6, take-up runs at 50% and approval at 60% of the agreed rates.
- **Rates grow with our pool's history:**
  - take-up +5% a year;
  - approvals +10% a year;
  - loan size +10% per year repaid;
  - top-ups for 15% of borrowers.
- **Loans:** loan size ₹25,000–5 lakh (₹2.5 lakh likely). Home loans ₹10–50 lakh, because family income counts.
- **Losses:** the worst case is Paytm's loss rate (4.5–5%), because our savers chose to save first and the agent helps collect. The lender carries the losses.
- **Collection fees** are paid per account brought back, by how late the loan is.
- **Insurance commissions** are at IRDAI's draft caps. Insurance is sold through a broker partner, so we keep about 75%.
- **Costs:** running cost ₹5 a saver a month; cash cover ₹1,000 an agent a month; no fee to the saver; partners' licences; the founder manages the pilot.
- **Metric:** cumulative P&L, not NPV.

## 6. Open questions and risks (not resolved)

- **The cash route needs a legal opinion.** The operator's design: the agent collects cash, we deposit it into the fund's collection account with a reconciliation, and the saver gets a message next day. By our reading, SEBI and AMFI rules limit distributors handling investor money. They also want fund payments to come from the investor's own account. And they cap cash investments in funds at about ₹50,000 per investor a year, while a ₹350-a-day saver puts in about ₹84,000.
- **In the company numbers.** An earlier line on this page said team leads, offices and licences were left out. They are in: one team lead per 10 agents, a city office, a city manager, and the partner and NBFC licence costs. What is still thin, not absent: the customer app is a flat ₹1.5 lakh a month for cloud, SMS and KYC; customer support stays at one person; NBFC operating cost is about ₹3 crore in year 5 on a book of about ₹1,600 crore. A full app build, NISM and an EUIN as a hiring limit for every seller, and a credit and collections operation sized to the book are still not costed.
- **Revenue per saver (₹732 a year) is above Paytm's per user.** This is driven mostly by loan size and home loans, and it is the number most open to challenge.
- **Untested inputs.**
  - Sign-ups per agent rests on one practitioner's statement (PR-01: 100+ a month). Their agents onboard and guide the first investment, while ours also collect cash daily. A janta agent adds 6–10 a month, but he isn't selling. A later conversation with Bachatt's growth lead (PR-02) puts a 40-to-50-person NCR street fleet at about 5,000 customers a month, which is 100 to 125 a person, and puts most of Bachatt's customers online at a CAC of about ₹300 on both channels.
  - At 100 a month the book reaches about 2,100 savers by month 60, so helpers are needed for cash visits beyond 400 a day unless more than 30% move to UPI.
  - Loan apply, eligibility and approval rates are judgement. The same Bachatt conversation (PR-03) says the customer stays because they are credit hungry and Bachatt gets them the loan they want, which Jar does not. He gave no retention rate. The base still treats 55% still saving at month 12 as its own input, separate from the loan.
  - The amount he keeps saving. Aniket (PR-04; surname and role not stated) says he has a small amount he is happy to save, some keep saving, and the rest drop off. No amount was given. The operator (PR-05) says the customer treats Bachatt as a digital wallet he saves into and then borrows from, an OD++, and that technology has to do both jobs. The base is still about ₹350 a day plus a term loan.
- **Rule changes.** IRDAI commission caps are in draft, and SEBI has cautioned on digital gold.

## 7. Folder map

### Current, use these

| File | What it is |
|---|---|
| `Offline_model_v3.pdf` | The deck (32 pages) |
| `Assumptions_agreed.pdf` | Every input as a distribution, 15 pages. `Assumptions_to_agree.pdf` is an identical copy. |
| `tables/dist_agreed_v1.csv` | All agreed inputs: shape, low/likely/high, p10/p50/p90, confidence, sources |
| `tables/cohort_mc_summary.csv` | The Monte Carlo headline (one agent, 10,000 draws) |
| `tables/cohort_mc_drivers.csv` | Sensitivity, input by input |
| `tables/cohort_mc_must_be_true.csv` | Chance of profit by retention × sign-ups |
| `tables/cohort_mc_cum_fan.csv` | Cumulative P&L by month, p10–p90 |
| `tables/cohort_mc_draws_sample1000.csv` | 1,000 of the 10,000 draws (inputs and outputs). The full draws are left out for size; re-run the model to get them. |
| `tables/cohort_det_*.csv` | One run at the likely values: monthly P&L, age profile, summary |
| `tables/cohort_bridge.csv` | Step by step from the previous deck's answer to this one |
| `tables/cohort_signups_sweep*.csv`, `tables/cohort_incentive_sweep*.csv` | The sign-ups and agent-pay tables |
| `tables/story_unit.csv` | The online comparison (₹499, 24 in 100, ₹2,067) |
| `tables/refresh_*.csv`, `story/REFRESH.md` | The 18 Oct refresh. Same fleet path as the base. Read this for the company. |
| `tables/base_*.csv` | The 17 Oct base (30% on book). Kept. The deck still uses these numbers. |
| `tables/cities.csv`, `tables/share_compare.csv`, `tables/sat_sensitivity.csv` | City pools (rank-size estimate); the 15/30/50% book comparison; city-model sensitivities |
| `tables/unicorn_*.csv` | The earlier unicorn track WITHOUT city limits (superseded) |
| `tables/growth_*.csv`, `tables/arr100m_*.csv` | Max growth with year-5 PAT ≥ 0; the path to $100M ARR |
| `tables/company_*.csv` | The earlier round-10 company plan (80 agents) and its lever/plan searches | The company model: `company_monthly.csv`, `company_yearly.csv`, `company_pnl_ladder_yearly.csv`, `company_cashflow_yearly.csv`, `company_headcount.csv`, `company_m18.csv`, `company_mc_summary.csv`, `company_levers.csv`, `company_plan_search.csv`, `company_breakeven_customers.csv`, `company_fleet_scenarios.csv` (README: `company_README.md`) |
| `research/*.csv`, `research/*.md` | The evidence, one row per source with an ID |
| `story/*.md` | The briefs and the operator's decisions, round by round, in his own words |
| Google Sheet "Save4More" | A toy version of the model with live formulas (the operator has the link). It matches the full model to within 0.3%. |

The evidence ID prefixes:

| Prefix | Topic |
|---|---|
| XL | lending |
| XO | other cross-sell |
| XB | benchmarks (Paytm, Bachatt) |
| IV | the janta-agent interview |
| REG | regulation |
| TB / TC | behaviour and cost research |
| GAP | 16 Oct web research |
| SE | story evidence |
| QM | the QR-moat research |
| LEV / MAC / NG / SG | earlier research rounds |

### Superseded: history only, do not quote as current

- **Earlier decks:**
  - `Offline_model_final.pdf`
  - `Offline_model_final_v2.pdf`
  - `Offline_model_stress_test.pdf`
  - `Offline_savings_business.pdf`
  - `Street_vs_online_story.pdf`
  - `Street_agent_3_years*.pdf`
  - `Street_agent_economics.pdf`

  These use earlier assumptions (60–83 sign-ups, a 20% discount rate, salary-only pay, no cohort model).
- **Earlier side studies:**
  - `QR_moat_test.pdf`, `QR_moat_story.pdf`: is a QR-code moat defensible?
  - `Save91_SWOT_and_Competitors.pdf`
- **`Cohort_model.xlsx`: does NOT reconcile after the last changes** (Excel −₹3.0 lakh against Python +₹0.97 lakh at month 60). Use the Google Sheet instead.
- **Earlier model tables:** `tables/xs_*_v2.csv`, `scn_*`, `npv_*`, `mkt_*`, `agent3_*`, `invert_*`, `mc_*` and other non-`cohort_` tables come from earlier rounds or an earlier app-first model.
- **Earlier folders:** `deck/`, `swot/`, `janta_pipe/` (the janta-agent interview questionnaire) and `brief/` (the HTML behind the PDFs).

## 8. How the model works and how to re-run it

**The model:**
- `model/cohort_engine.py`: one agent, a new cohort of sign-ups every month, tracked month by month for 60 months. It covers:
  - retention curve, deposits, balance (yearly terms, rollover, withdrawals, 7% return);
  - UPI share and cash-visit capacity;
  - marketplace take-up by product, with first, repeat and top-up loans;
  - collections, and every cost line.
  - With `legacy=True` it reproduces the previous deck exactly.
- `model/cohort_mc.py`: samples every input from `tables/dist_agreed_v1.csv` (Latin hypercube, 10,000 draws; approvals and losses linked at ρ −0.5) and writes the `cohort_mc_*` tables.

**Requirements:** Python 3.11 with numpy, scipy and pandas. Google Chrome is needed for the PDF builds. The project's virtual environment is left out.

**Re-run, in this order:**

```
python model/dist_proposal.py
python model/cohort_engine.py
python model/cohort_mc.py
python model/signups_sweep.py
python model/incentive_sweep.py
python model/company_model.py
python model/company_mc.py
python model/company_plan.py
python model/growth_model.py
python model/arr100m.py
python model/unicorn_plan.py
python model/build_deck_v3.py
```

What each step writes:

| Step | Writes |
|---|---|
| `model/dist_proposal.py` | `tables/dist_agreed_v1.csv` and the assumptions PDFs |
| `model/cohort_engine.py` | the deterministic tables, the bridge and the legacy check |
| `model/cohort_mc.py` | the Monte Carlo tables (and the full draws, about 34 MB) |
| `model/signups_sweep.py`, `model/incentive_sweep.py` | the sign-ups and agent-pay tables |
| `model/company_model.py`, `model/company_mc.py`, `model/company_plan.py` | the company P&L, cash flow and Monte Carlo, and the plan search |
| `model/build_deck_v3.py` | `Offline_model_v3.pdf` |

**Reviews done:**
- The cohort engine was checked by an independent recompute of one cohort, matching on all 29 lines at every age.
- An adversarial reviewer found no arithmetic errors and named the three assumptions the result rests on:
  - sign-ups per agent;
  - the loan sizes lenders will give;
  - running costs.

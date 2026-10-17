# START HERE: "save first, borrow later", an offline savings business

**State as of 17 Oct 2026, night (unicorn track).** This folder holds the work behind a business case: research, models, decks and the agreed assumptions. Read this page first. It says what we are building, where the numbers stand, and which files are current.

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

## 3b. The company plan: the UNICORN TRACK (17 Oct 2026, night)

**The operator's choices:**
- "Unicorn by year 5", with no own-book lending (NBFC) for 5 years.
- "Assume we can raise as much as possible if everything keeps holding... work backwards to make us unicorn on paper by year 5."
- Built by `model/unicorn_plan.py`; outputs in `tables/unicorn_*.csv`; deck Part 4.

**Unicorn on paper** means BOTH valuation lenses reach ≥ $1B (₹10,000 crore at ₹100/$) at month 60:
- **20× ARR;**
- **0.45× AUM**, the ratio of Stable Money's last round to money invested through it (SAV-02/03).

Both multiples are our judgement, built on one comparable.

**The plan:**
- **Fleet:** 300 agents by month 18, then +200 a month to a cap of 7,500 by year 5; after that, replacements only.
- **Agent pay:** ₹20,000 + 0.25% of balance, capped at ₹10,000 a month.
- **Business model:** distribution only.

**Rounds** (pricing is the higher of a step-up from the last round and the lens value; at most 25% dilution a round; a 10% ESOP pool):

| Round | Month | Raise (₹ crore) | Pre-money | Post-money | Founders after |
|---|---|---|---|---|---|
| Seed | 0 | 13 | 40 | 53 | 65.5% |
| A | 10 | 53 | 159 | 212 | 47.3% |
| B | 20 | 212 | 636 | 848 | 34.2% |
| C | 32 | 610 | 2,768 | 3,378 | 28.0% |
| D | 48 | 315 | 12,072 (≈$1.2B) | 12,387 | 27.3% |
| E | 54 | 105 | 18,581 | 18,686 | **27.1%** |

Total raised: **₹1,308 crore (about $130M)**.

| ₹ crore | Y1 | Y2 | Y3 | Y4 | Y5 | Y6 | Y7 | Y8 |
|---|---|---|---|---|---|---|---|---|
| Revenue | 0.5 | 7 | 65 | 248 | 577 | 903 | 1,147 | 1,321 |
| EBITDA | −8 | −45 | −182 | −264 | −218 | 26 | 174 | 263 |
| PAT | −7 | −39 | −163 | −236 | −185 | 55 | 208 | 311 |
| Closing cash | 59 | 229 | 659 | 699 | 558 | 565 | 738 | 1,023 |
| Agents | 150 | 1,500 | 3,900 | 6,300 | 7,500 | 7,500 | 7,500 | 7,500 |
| Active savers (lakh) | 0.6 | 5 | 27 | 61 | 100 | 127 | 145 | 157 |

**At month 60:**
- ARR ₹739 crore, so 20× = ₹14,771 crore (+48% over $1B);
- AUM ₹50,113 crore, so 0.45× = ₹22,551 crore (+126%);
- Monte Carlo: both lenses clear in 91% of 1,000 draws; cash stays ≥ 0 through month 96 in 84%.

**What it asks of operations:**
- 150 cities by year 5, opening 48 new cities a year in years 3–4;
- up to 382 agent hires in one month, including replacements;
- a central team of about 535.

**$100M ARR (₹1,000 crore a year)** needs about 1.1–1.2 crore active savers, about 5,000 mature agents (7,500 with a growing fleet), and about ₹70,000 crore AUM (`tables/arr100m_*.csv`). This plan reaches it during year 7.

**The other road** (`tables/growth_frontier.csv`; deck page "The other road"):
- profitable by year 5: 200 agents, about ₹43 crore raised, EBITDA positive from month 51, about 3.9 lakh savers at year 5;
- the round-10 plan (80 agents, ₹10 crore seed + ₹50 crore Series A) is kept in the `company_*` tables and the Google Sheet notes.

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
- **Not in the numbers:**
  - the customer app's build and running cost;
  - team leads at scale;
  - office and licences.
- **Revenue per saver (₹732 a year) is above Paytm's per user.** This is driven mostly by loan size and home loans, and it is the number most open to challenge.
- **Untested inputs.**
  - Sign-ups per agent rests on one practitioner's statement (PR-01: 100+ a month). Their agents onboard and guide the first investment, while ours also collect cash daily. A janta agent adds 6–10 a month, but he isn't selling.
  - At 100 a month the book reaches about 2,100 savers by month 60, so helpers are needed for cash visits beyond 400 a day unless more than 30% move to UPI.
  - Loan apply, eligibility and approval rates are judgement.
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
| `tables/unicorn_*.csv` | THE CURRENT COMPANY PLAN (unicorn track): rounds and cap table, yearly and monthly statements, milestones, Monte Carlo, search, checks |
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

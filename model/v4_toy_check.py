"""v4 sheet twin (21 Oct 2026): the SAME maths as the v4 Google Sheet tabs (model/v4_gsheet.py writes them), in numpy, the
reconciliation against the online-first Python model (model/online_plan.py, company()) and a replay of every v4 formula through
model/toy_check.py's small Google Sheets interpreter.

What the sheet does (and this file, line for line)
  'v4 Per saver'  one saver's ages 1-96. Every line except "still saving" is the same PER ACTIVE SAVER for the online and the
                  doorstep saver (the engine's take-up, loan-state and cross-sell maths all scale with still-saving; checked
                  below to 1e-15), so the tab works the per-active machinery once and multiplies by each saver's still-saving
                  curve. The 19 cross-sell products are worked product by product in closed form (take-ups = never-held x
                  hazard; money = take-ups convolved with a per-kind kernel: at take-up, yearly renewals, the Choti bonus at
                  month 24, monthly holdings for gold / recharge / bills, the SIP trail).
                  It is the profile of a saver who joins once the pool's history is mature: take-up and approval growth at the
                  held calendar year (year 5), as every cohort from month 49 on. Equal to the engine's month-49+ cohorts to 1e-9.
  'v4 Monthly'    months 1-96: online savers won (seed, ramp, level x growth, the 20% pool cap), doorstep agents and savers
                  (3-month ramp per agent), active savers by age x the per-active lines, revenue, acquisition, team (headcount
                  rules), other costs, the 10% contingency on every expensed line (inside EBITDA), EBITDA, tax after losses
                  carried forward, PAT, cash received (revenue 2 months late), cash flow, cumulative cash (money needed).

The one approximation: calendar growth
  The engine gives every monthly cohort its own profile (take-up +5% and approval +10% each calendar year, held after year 5).
  The sheet uses the held-year profile for every cohort and scales each month's total by a calendar factor relative to the held
  year: take-up for insurance and other products, take-up x approval for loan fees, cards, home loans and LAP. Per product, the
  money booked at take-up takes this month's factor; the later money takes the factor of its lag: insurance renewals 12 months
  (the first renewal), the Choti bonus 24 (its payment month), holdings (gold, recharge, bills, SIP) LAG_HOLD = 6 months, a
  sheet-only calibration (the money-weighted lag overcorrects because the never-held pool is larger when past factors were
  lower; 6 was the best of 0/3/6/9 on years 4-6 at both levels, and holds for every lever). Exact for cohorts from month 49.
  Result: revenue within about 0.2% in every year (gaps in tables/v4_toy_check.csv).

Writes tables/v4_toy_check.csv. Asserts: per-active profile equals the engine's cohort-60 profile (1e-9); with the spec present,
every formula evaluates without error and every Monthly line and Summary/Yearly live cell equals the numpy twin (1e-9), at the
base and at three other scenarios (grow fast, a pool-cap run with growth, online-only + debt funds + caps).
Run: python model/v4_gsheet.py, then python model/v4_toy_check.py.
"""
import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohort_engine as ce  # noqa: E402
import online_plan as op  # noqa: E402
import toy_check as tc  # noqa: E402

sys.setrecursionlimit(20000)
T = op.TAB
SPEC = T / "v4_gsheet_spec.json"
OUT = T / "v4_toy_check.csv"
M = op.M                      # 96 months / ages
CR = op.CR
PFX = "v_"                    # every v4 named range starts with this (no clash with the old tabs' 430 names)
RUN_DATE = "22 Oct 2026"
LEVELS = (20000, 150000)
LAG_HOLD = 6                  # months: holdings' calendar factor lag (sheet-only calibration; see main() sweep)
LATER_LAG = {"ins": 12, "bonus": 24}   # renewals 12 months after take-up (the first renewal); Choti paid at month 24

X_ON = op.saver_inputs()
X_DO = op.saver_inputs(doorstep=True)
X0 = op.X0
INS = ce.INSURANCE


# ---------------------------------------------------------------- inputs: (key, label, unit, format, value, basis)
def input_sections():
    seed_online = op.SEED_ONLINE
    return [
        ("Scenario (change these to play the plan)", [
            ("level", "Online savers won a month from month 30 (the plan level)", "savers a month", "inr", 20000.0,
             "SCENARIO. 20,000 = the profitable path; 1,50,000 = grow fast (online_plan.py frontier; online_mc.py plans)"),
            ("growth", "Savers won a month grow by this factor each year after month 30 (1.0 = flat)", "x a year", "mult", 1.0,
             "SCENARIO. Every case in online_plan.py runs flat (1.0)"),
            ("door_after", "Doorstep agents keep signing savers after the 18-month test (1 = yes, 0 = online only after month 18)",
             "1 or 0", "num0", 1.0, "Operator 21 Oct: 90% online, 10% offline. 'Online only after m18' is a lever (v4 Levers)"),
        ]),
        ("Savers won: the path", [
            ("launch", "First month savers are won", "month", "num0", float(op.LAUNCH), "Seed plan: build months 1-3, launch month 4"),
            ("seed_end", "Last month of the seed", "month", "num0", float(op.SEED_END), "Seed plan (18 months)"),
            ("ramp_end", "Month online savers won reach the plan level (straight line from the seed level after the seed)", "month",
             "num0", float(op.RAMP_END), "online_plan.py"),
            ("seed_online", "Online savers won a month in the seed (months 4-18)", "savers a month", "inr1", seed_online,
             "Seed plan at 90/10: 97,200 online sign-ups x 50% x 40% (1 in 5 save) over 15 months = 19,440"),
            ("door_share", "Doorstep share of all savers won", "share", "pct", op.DOOR_SHARE, "Operator 21 Oct: 90% online, 10% offline"),
            ("pool", "Pool of target savers", "people", "inr", op.POOL, "Agreed pool (7 crore)"),
            ("pool_cap", "Cumulative savers won stop at this share of the pool", "share", "pct", op.CAP, "Agreed city cap (20%)"),
        ]),
        ("Cost to win a saver", [
            ("seed_cac", "Cost to win an online saver in the seed (months 1-18), all-in", "₹ a saver", "inr", op.SEED_CAC,
             "The seed plan's own funnel: ₹100 a sign-up + ₹40 KYC for 1 in 2; 1 in 5 save. Range ₹300-600 (operator 21 Oct)"),
            ("cac_rs", "Cost to win an online saver after the seed, all-in (marketing + KYC)", "₹ a saver", "inr", op.CAC,
             "Operator 21 Oct: ₹450 base, range ₹300-600 (audit: PR-02's ₹300 is per 'customer', undefined; our funnel says ₹600)"),
        ]),
        ("Doorstep agents (10% of savers)", [
            ("agent_signups", "Savers one doorstep agent signs a month at full speed", "savers a month", "num0", op.AGENT_SIGNUPS,
             "Agreed signups_run (tables/dist_agreed_v1.csv)"),
            ("agent_ramp1", "An agent's speed in his first month (share of full)", "share", "pct", op.RAMP[0], "Agreed ramp_months 3: 50%"),
            ("agent_ramp2", "An agent's speed in his second month", "share", "pct", op.RAMP[1], "Straight line to full speed: 2/3"),
            ("agent_ramp3", "An agent's speed in his third month", "share", "pct", op.RAMP[2], "5/6; full speed from month 4"),
            ("agent_cost", "Agent cost a month: salary 20,000 + statutory 3,000 + incentive 2,000 + cash cover 1,000", "₹ a month", "inr",
             float(op.AGENT_COST), "Agreed salary; incentive our estimate; cash cover agreed"),
            ("hire_kit", "Hiring and kit per agent hired", "₹ an agent", "inr", op.HIRE_KIT, "base_inputs"),
            ("agent_churn", "Agents who leave a year (each replacement costs a kit)", "a year", "pct", op.AGENT_CHURN, "base_inputs"),
            ("lead_pay", "Field lead pay a month incl. 10% statutory", "₹ a month", "inr", float(op.LEAD_PAY), "base_inputs (₹40,000 + 10%)"),
            ("per_lead", "Agents per field lead", "agents", "num0", float(op.PER_LEAD), "base_inputs"),
            ("city_office", "City office a month", "₹ a month", "inr", op.CITY_OFFICE, "base_inputs"),
            ("per_city", "Agents per city office", "agents", "num0", float(op.PER_CITY), "base_inputs"),
            ("big_from", "Field leads and city offices only when agents are more than this (a founder leads below it)", "agents",
             "num0", 5.0, "online_plan.py"),
            ("door_kyc", "KYC per doorstep saver won", "₹ a saver", "inr", op.DOOR_KYC, "online_plan.py"),
        ]),
        ("Saving", [
            ("daily", "Daily amount a saver puts in", "₹ a day", "inr", X_ON["daily"], "Operator 21 Oct: ₹100 a day (Bachatt's stated minimum)"),
            ("deposit_days", "Debit days a month", "days", "num1", X_ON["days"], "Agreed ~20 debit days"),
            ("amount_growth", "His daily amount steps up each year he saves", "a year", "pct", X_ON["amount_growth"], "Agreed"),
            ("term", "Savings year (the step-up and the balance roll-over happen every this many months)", "months", "num0",
             X_ON["term"], "Agreed"),
            ("rollover", "Share of the balance kept at each year end (an SIP has no yearly payout)", "share", "pct", X_ON["rollover"],
             "Online design: 100%"),
            ("withdraw_m", "Share of the balance withdrawn each month", "a month", "pct", X_ON["withdraw_m"], "Agreed"),
        ]),
        ("The fund (80% equity SIP / 20% debt)", [
            ("eq_share", "Equity share of the savings (0 = debt fund only)", "share", "pct", 0.8, "Bachatt conversation (F22): about 80% "
             "choose equity SIPs. Debt-only is a lever"),
            ("eq_return", "Equity return a year, net", "a year", "pct", op.EQ_RETURN, "Our estimate (conservative)"),
            ("debt_return", "Debt fund return a year, net", "a year", "pct", op.DEBT_RETURN, "Agreed"),
            ("eq_trail", "Our trail on equity SIP balances", "a year", "pct2", op.EQ_TRAIL, "Agreed SIP commission 0.75%"),
            ("debt_trail", "Our trail on debt fund balances", "a year", "pct2", op.DEBT_TRAIL, "Agreed debt fund trail 0.35%"),
            ("sip_takeup_debt", "SIP cross-sell take-up a year when the savings sit in a debt fund (equity share 0)", "a year", "pct",
             X0["sip_takeup"], "Agreed; 0 while the core balance IS the equity SIP"),
        ]),
        ("Still saving", [
            ("on_r3", "Online saver: still saving at month 3", "share", "pct", X_ON["r3"], "SBI MF ₹250 daily SIP: a steady ~7% a month"),
            ("on_r12", "Online saver: still saving at month 12", "share", "pct", X_ON["r12"],
             "Operator 21 Oct: 38% (SBI MF daily SIP). 24% savings apps (downside), 45% credit hook (upside)"),
            ("door_r3", "Doorstep saver: still saving at month 3", "share", "pct", X_DO["r3"], "Agreed street"),
            ("door_r12", "Doorstep saver: still saving at month 12", "share", "pct", X_DO["r12"], "Agreed street 55%"),
            ("churn_late", "Both savers: drop-off a month after month 12", "a month", "pct", X_ON["churn_late"], "Agreed"),
        ]),
        ("Marketplace timing and calendar growth", [
            ("early_takeup", "Take-up factor in a saver's months 1-6 (loans, cards, every product)", "x full rate", "mult",
             X_ON["early_takeup_mult"], "Agreed"),
            ("early_approval", "Approval factor in a saver's months 1-6 (first loans, cards, home loans, LAP)", "x full rate", "mult",
             X_ON["early_approval_mult"], "Agreed"),
            ("takeup_growth", "Every take-up rises each calendar year as the pool's history grows (cap 2x)", "a year", "pct",
             X_ON["takeup_growth"], "Agreed"),
            ("approval_growth", "Approvals rise each calendar year (cap 80% approval)", "a year", "pct", X_ON["approval_growth"], "Agreed"),
            ("year_hold", "Calendar year after which that growth is held", "year", "num0", 5.0, "online_plan.py (year_cap 5)"),
            ("lag_hold", "SHEET ONLY: holdings (gold, recharge, bills, SIP) take the calendar factor of this many months earlier",
             "months", "num0", float(LAG_HOLD), "Calibrated in model/v4_toy_check.py so the sheet tracks the Python model's per-cohort "
             "profiles (insurance renewals take 12 months, the Choti bonus 24: their timing). 0 = this month's factor"),
        ]),
        ("Personal and business loans (partner lenders; we earn a DSA payout)", [
            ("apply", "Reachable users with no loan running who apply for a personal or business loan, a year", "a year", "pct", X_ON["apply"],
             "Operator 21 Oct: 35% of reachable users apply for a loan a year; 70% of applications are personal or business"),
            ("eligible", "Applicants eligible (1 = eligibility sits inside the approval share)", "share", "pct", X_ON["eligible"], "Operator 21 Oct"),
            ("approved_first", "Approved, first loan (share of applications)", "share", "pct", X_ON["approved_first"],
             "Operator 21 Oct: 30% (founders' past lending ~25%; PSU banks approve ~80% of pre-qualified MSMEs)"),
            ("approved_repeat", "Approved, repeat loan", "share", "pct", X_ON["approved_repeat"], "Operator 21 Oct: 70%"),
            ("ticket", "Loan size, personal + business blended", "₹", "inr", X_ON["ticket"],
             "Founders 22 Oct: ₹3 lakh (research found smaller: digital personal loans ₹18.8k-70k, FACE/CRIF; merchant loans ₹50k-5 lakh, Paytm ~₹2 lakh)"),
            ("fee", "Our payout at the start: a DSA's rate", "of the loan", "pct3", X_ON["fee"], "DSA payouts 1-2.5% on personal and business loans (research 21 Oct)"),
            ("fee_mult_start", "Fee multiplier in month 1", "x", "mult", X_ON["fee_mult_start"], "Agreed"),
            ("fee_mult_end", "Fee multiplier reached by month 60 (straight line, held after)", "x", "mult", X_ON["fee_mult_end"], "Agreed"),
            ("taken_back", "Fees taken back", "share", "pct", X_ON["taken_back"], "Agreed"),
            ("tenure", "Loan tenure (no new loan while one runs)", "months", "num0", X_ON["tenure"], "Personal and business loans run 12-24 months"),
            ("ticket_growth", "Next loan bigger for each year repaid (repeat loans and top-ups)", "a year", "pct", X_ON["ticket_growth"], "Agreed"),
            ("ticket_cap", "Cap on a repeat loan", "₹", "inr", ce.TICKET_CAP, "Engine constant (XL-12)"),
            ("topup_share", "Borrowers with 12+ EMIs paid who take a top-up, a year", "a year", "pct", X_ON["topup_share"], "Agreed"),
            ("topup_size", "Top-up size, share of the original loan", "share", "pct", X_ON["topup_size"], "Agreed"),
        ]),
        ("Cards and insurance", [
            ("card_share", "Savers who get a card (spread over his months 1-6; the early factors' shortfall in months 7-12)", "share",
             "pct", X_ON["card_share"], "Agreed"),
            ("card_fee", "Fee per card", "₹ a card", "inr", X_ON["card_fee"], "Agreed"),
            ("ins_share", "Share of insurance commission that reaches us through a broker partner", "share", "pct",
             X_ON["ins_partner_share"], "Founder 22 Oct: a fixed referral fee through the broker, to be agreed; not counted (0)"),
        ]),
        ("Running cost", [
            ("support", "Support cost per active saver a month", "₹ a month", "inr", X_ON["support_cost"], "Agreed"),
        ]),
        ("Team: seed (months 1-18)", [
            ("pay_founder_seed", "Founder pay a month (2 founders)", "₹ a month", "inr", op.PAY["founder_seed"], "Seed plan: $1,000 a month at ₹95"),
            ("pay_eng_seed", "Engineer from month 1", "₹ a month", "inr", float(op.PAY["engineer_seed"]), "Seed plan"),
            ("pay_ops_seed", "Ops hire", "₹ a month", "inr", float(op.PAY["ops_seed"]), "Seed plan"),
            ("ops_from", "Ops hire joins in month", "month", "num0", 4.0, "Seed plan"),
            ("pay_jr_seed", "Junior engineer", "₹ a month", "inr", float(op.PAY["jr_eng_seed"]), "Seed plan"),
            ("jr_from", "Junior engineer joins in month", "month", "num0", 7.0, "Seed plan"),
        ]),
        ("Team: after the round (from month 19; pay incl. 10% statutory, +7% each year after month 18)", [
            ("pay_founder", "Founder (2)", "₹ a month", "inr", op.PAY["founder"], "base_inputs"),
            ("pay_engineer", "Engineer", "₹ a month", "inr", op.PAY["engineer"], "base_inputs"),
            ("pay_product", "Product", "₹ a month", "inr", op.PAY["product"], "base_inputs"),
            ("pay_compliance", "Compliance (1)", "₹ a month", "inr", op.PAY["compliance"], "base_inputs"),
            ("pay_ops", "Ops", "₹ a month", "inr", op.PAY["ops"], "base_inputs"),
            ("pay_growth", "Growth", "₹ a month", "inr", op.PAY["growth"], "base_inputs"),
            ("pay_finance", "Finance", "₹ a month", "inr", op.PAY["finance"], "base_inputs"),
            ("pay_risk", "Risk (1, from the risk month)", "₹ a month", "inr", op.PAY["risk"], "base_inputs"),
            ("raise_rate", "Pay rise each year after month 18", "a year", "pct", 0.07, "online_plan.py"),
            ("eng_base", "Engineers: base count", "people", "num0", 3.0, "JUDGEMENT"),
            ("eng_per", "Engineers: one more per this many active savers", "savers", "inr", 2e5, "JUDGEMENT"),
            ("eng_cap", "Engineers: at most", "people", "num0", 40.0, "JUDGEMENT"),
            ("product_per", "Product: 1 + one per this many active savers", "savers", "inr", 5e5, "JUDGEMENT"),
            ("ops_per", "Ops: one per this many active savers (rounded up)", "savers", "inr", 2e4, "JUDGEMENT"),
            ("ops_min", "Ops: at least", "people", "num0", 2.0, "JUDGEMENT"),
            ("ops_cap", "Ops: at most", "people", "num0", 400.0, "JUDGEMENT"),
            ("growth_per", "Growth: 1 + one per this much spent winning online savers a month", "₹ a month", "inr", 1e7, "JUDGEMENT"),
            ("finance_per", "Finance: 1 + one per this many active savers", "savers", "inr", 1e6, "JUDGEMENT"),
            ("risk_from", "Risk lead joins in month", "month", "num0", 24.0, "JUDGEMENT"),
        ]),
        ("Other costs", [
            ("tech_build", "Tech build, spread over months 1-3", "₹", "inr", 1_500_000.0, "base_inputs"),
            ("tech_base", "Tech a month", "₹ a month", "inr", 150000.0, "base_inputs"),
            ("tech_per_saver", "Tech a month per KYC'd user reached (savers and the KYC'd users who came with them)", "₹ a month", "inr1",
             op.TECH_PER_SAVER, "The 2 Oct costing (critical review 22 Oct; was ₹1 per active saver)"),
            ("office_seed", "Office a month in the seed", "₹ a month", "inr", 75000.0, "Seed plan"),
            ("office_base", "Office a month after the seed", "₹ a month", "inr", 150000.0, "online_plan.py"),
            ("office_per_head", "Office per head a month after the seed", "₹ a month", "inr", 10000.0, "online_plan.py"),
            ("comp_setup", "Compliance set-up in month 1", "₹", "inr", 125000.0, "Seed plan"),
            ("comp_seed_year", "Compliance a year in the seed", "₹ a year", "inr", 1_000_000.0, "Seed plan"),
            ("comp_year", "Compliance a year after the seed", "₹ a year", "inr", 2_500_000.0, "online_plan.py"),
            ("brand", "Brand a month after the seed", "₹ a month", "inr", 200000.0, "online_plan.py"),
            ("design", "Design a month in months 1-3", "₹ a month", "inr", 100000.0, "Seed plan"),
            ("raise_seed", "Fund-raising cost of the seed (month 1)", "₹", "inr", 500000.0, "Seed plan"),
            ("raise_round", "Fund-raising cost of the round (month after the seed)", "₹", "inr", 1_500_000.0, "online_plan.py"),
        ]),
        ("Finance and the two lenses at month 60", [
            ("contingency", "Contingency on every expensed line (acquisition, team, tech, office, compliance, brand, design, "
             "fund-raising, support), inside EBITDA", "share", "pct", op.CONTINGENCY, "Agreed base convention (company_model.py)"),
            ("comm_lag", "Revenue is booked when earned; the cash arrives this many months later (cash only, not EBITDA)", "months",
             "num0", float(op.COMMISSION_LAG), "Agreed base convention"),
            ("tax_rate", "Tax on profit after losses carried forward", "share", "pct", 0.25, "online_plan.py"),
            ("floor", "Cash floor added to the deepest cumulative cash hole (money needed)", "₹", "inr", 5 * CR, "online_plan.py"),
            ("lens_month", "Month of the lenses", "month", "num0", 60.0, "Investment review F01-F03"),
            ("arr_mult", "Lens 1: x revenue run-rate (12 x the month's revenue)", "x", "mult", 20.0, "OUR JUDGEMENT"),
            ("aum_mult", "Lens 2: x AUM (average fund balance)", "x", "mult", 0.45, "OUR JUDGEMENT"),
            ("rs_per_usd", "Rupees a dollar", "₹ a $", "inr", op.FX, "Operator 21 Oct"),
        ]),
    ]


# inputs placed after the product table (added 21 Oct), so no earlier row or named range moves
EXTRA_INPUTS = ("Loan marketplace and payments (added 21-22 Oct 2026)", [
    ("loan_reach", "KYC'd users who see loan offers per online saver won (5 sign-ups a saver, half complete KYC; doorstep counts 1)",
     "people", "mult", op.LOAN_REACH, "Operator 21 Oct: offers to anyone KYC'd who opts in, from day 1, reachable as long as savers keep saving"),
    ("debit_cost", "Payment cost per debit", "₹ a debit", "inr1", op.DEBIT_COST,
     "The 2 Oct costing ₹2 base (₹0 to us through BSE StAR MF once confirmed; ₹5 list through a gateway)"),
    ("debits_month", "Debits a month per active saver (weekly until a daily SIP on one mandate is confirmed)", "debits a month", "f3",
     op.DEBITS_A_MONTH, "Founder 22 Oct: weekly (52 / 12) until BSE StAR MF and the fund houses confirm daily in writing"),
])


def base_inputs():
    v = {k: float(val) for _s, rows in input_sections() for k, _l, _u, _f, val, _b in rows}
    v.update({k: float(val) for k, _l, _u, _f, val, _b in EXTRA_INPUTS[1]})
    return v


# derived (grey on 'v4 Inputs'): key, label, unit, format, sheet formula with {p} for the prefix; numpy twin in derived()
DERIVED = [
    ("fund_return", "Saver's net fund return a year (equity share x equity + rest x debt)", "a year", "pct2",
     "={p}eq_share*{p}eq_return+(1-{p}eq_share)*{p}debt_return"),
    ("trail", "Our trail a year on the average balance (blended)", "a year", "pct3", "={p}eq_share*{p}eq_trail+(1-{p}eq_share)*{p}debt_trail"),
    ("fund_m", "Fund return a month", "a month", "pct3", "=(1+{p}fund_return)^(1/12)-1"),
    ("door_ratio", "Doorstep savers per online saver", "x", "f3", "={p}door_share/(1-{p}door_share)"),
    ("mt_hold", "Take-up growth factor at the held year", "x", "f3", "=(1+{p}takeup_growth)^({p}year_hold-1)"),
    ("ma_hold", "Approval growth factor at the held year", "x", "f3", "=(1+{p}approval_growth)^({p}year_hold-1)"),
    ("tf_e", "Take-up factor, his months 1-6 (held year, cap 2)", "x", "f3", "=MIN(2,{p}early_takeup*{p}mt_hold)"),
    ("tf_f", "Take-up factor, from his month 7 (held year, cap 2)", "x", "f3", "=MIN(2,{p}mt_hold)"),
    ("apply_m", "Loan application chance a month (no loan running)", "a month", "pct3", "=1-(1-{p}apply)^(1/12)"),
    ("af_e", "First-loan approval, his months 1-6 (held year, cap 80%)", "share", "pct", "=MIN(0.8,{p}approved_first*{p}early_approval*{p}ma_hold)"),
    ("af_f", "First-loan approval, from his month 7 (held year, cap 80%)", "share", "pct", "=MIN(0.8,{p}approved_first*{p}ma_hold)"),
    ("q1e", "First-loan chance a month, his months 1-6", "a month", "pct3", "={p}apply_m*{p}tf_e*{p}eligible*{p}af_e"),
    ("q1f", "First-loan chance a month, from his month 7", "a month", "pct3", "={p}apply_m*{p}tf_f*{p}eligible*{p}af_f"),
    ("tenure_m", "Loan tenure in whole months", "months", "num0", "=MAX(1,ROUND({p}tenure,0))"),
    ("rep_ticket", "Repeat loan size (after the tenure repaid)", "₹", "inr", "=MIN({p}ticket_cap,{p}ticket*(1+{p}ticket_growth)^({p}tenure_m/12))"),
    ("topup_amt", "Top-up size (after a year repaid)", "₹", "inr", "={p}topup_size*{p}ticket*(1+{p}ticket_growth)"),
    ("topup_m", "Top-up chance a month for an eligible borrower", "a month", "pct3", "=1-(1-{p}topup_share)^(1/12)"),
    ("card_ae", "Card approval factor, his months 1-6 (held year, cap 2)", "x", "f3", "=MIN(2,{p}early_approval*{p}ma_hold)"),
    ("card_catchup", "Share of cards the early factors held back, issued in his months 7-12", "share", "pct",
     "=MAX(0,1-{p}early_takeup*{p}early_approval)"),
    ("card_cg", "Card factor in his months 7-12 (held year)", "x", "f3", "=MIN(2,{p}mt_hold)*MIN(2,{p}ma_hold)"),
    ("door_cac", "Doorstep cost to win a saver (agent cost / savers a month + KYC; information)", "₹ a saver", "inr",
     "={p}agent_cost/{p}agent_signups+{p}door_kyc"),
]


def derived(v):
    d = {}
    d["fund_return"] = v["eq_share"] * v["eq_return"] + (1 - v["eq_share"]) * v["debt_return"]
    d["trail"] = v["eq_share"] * v["eq_trail"] + (1 - v["eq_share"]) * v["debt_trail"]
    d["fund_m"] = (1 + d["fund_return"]) ** (1 / 12) - 1
    d["door_ratio"] = v["door_share"] / (1 - v["door_share"])
    d["mt_hold"] = (1 + v["takeup_growth"]) ** (v["year_hold"] - 1)
    d["ma_hold"] = (1 + v["approval_growth"]) ** (v["year_hold"] - 1)
    d["tf_e"] = min(2.0, v["early_takeup"] * d["mt_hold"])
    d["tf_f"] = min(2.0, d["mt_hold"])
    d["apply_m"] = 1 - (1 - v["apply"]) ** (1 / 12)
    d["af_e"] = min(0.8, v["approved_first"] * v["early_approval"] * d["ma_hold"])
    d["af_f"] = min(0.8, v["approved_first"] * d["ma_hold"])
    d["q1e"] = d["apply_m"] * d["tf_e"] * v["eligible"] * d["af_e"]
    d["q1f"] = d["apply_m"] * d["tf_f"] * v["eligible"] * d["af_f"]
    d["tenure_m"] = max(1.0, float(math.floor(v["tenure"] + 0.5)))
    d["rep_ticket"] = min(v["ticket_cap"], v["ticket"] * (1 + v["ticket_growth"]) ** (d["tenure_m"] / 12))
    d["topup_amt"] = v["topup_size"] * v["ticket"] * (1 + v["ticket_growth"])
    d["topup_m"] = 1 - (1 - v["topup_share"]) ** (1 / 12)
    d["card_ae"] = min(2.0, v["early_approval"] * d["ma_hold"])
    d["card_catchup"] = max(0.0, 1 - v["early_takeup"] * v["early_approval"])
    d["card_cg"] = min(2.0, d["mt_hold"]) * min(2.0, d["ma_hold"])
    d["door_cac"] = v["agent_cost"] / v["agent_signups"] + v["door_kyc"]
    return d


# ---------------------------------------------------------------- the 19 cross-sell products (the engine's PRODUCTS, online values)
KIND_WORDS = {"ins": "insurance: commission at take-up, renewal commission each year while he saves",
              "once": "once: commission at take-up", "secured": "home loan / LAP: application x approval, fee at disbursal",
              "bonus": "Choti SIP: ₹500 at month 24 if the SIP survives", "flow": "holding: buys a month while he holds it",
              "flow_year": "holding: spend a year / 12 while he holds it", "trail": "SIP trail on the SIP balance"}


def product_rows():
    out = []
    for p, kind, nm, dd in ce.PRODUCTS:
        g = lambda q: float(X_ON[f"{p}_{q}"]) if f"{p}_{q}" in X_ON else None
        kind2 = "flow_year" if kind == "flow_year" else kind
        row = {"p": p, "name": nm, "kind": kind2, "takeup": g("takeup"), "ticket": g("ticket"), "comm": g("comm"),
               "renew": g("renew"), "rcomm": g("renew_comm"), "appr": g("approval"), "ins": 1.0 if p in INS else 0.0,
               "loan": 1.0 if p in op.LOAN_REACH_XS else 0.0}    # reach applies to gold, property and home loans only
        if kind == "ins" and row["rcomm"] is None:          # two-wheeler renews at its first-year rate (engine)
            row["rcomm_same"] = True
            row["rcomm"] = row["comm"]
        if p == "sip":
            row["takeup_formula"] = True                     # =IF(eq_share>0,0,sip_takeup_debt)
        out.append(row)
    return out


def product_values(v, prods):
    """Product parameters as the sheet sees them (SIP take-up follows the equity share; two-wheeler renewal = its commission)."""
    out = []
    for r in prods:
        r = dict(r)
        if r.get("takeup_formula"):
            r["takeup"] = 0.0 if v["eq_share"] > 0 else v["sip_takeup_debt"]
        if r.get("rcomm_same"):
            r["rcomm"] = r["comm"]
        sh = v["ins_share"] if r["ins"] == 1 else 1.0
        r["book"] = r["ticket"] * r["comm"] * sh if r["kind"] in ("once", "secured", "ins") else 0.0   # money booked at take-up
        r["lag"] = float(LATER_LAG.get(r["kind"], v["lag_hold"] if r["kind"] in ("flow", "flow_year", "trail") else 0))
        r["house"] = 1.0 if r["kind"] == "secured" else 0.0
        out.append(r)
    return out


# ---------------------------------------------------------------- the numpy twin of the sheet
def per_saver(v, prods):
    d = derived(v)
    pr = product_values(v, prods)
    A = np.arange(1, M + 1, dtype=float)
    ps = {"age": A}
    ret = lambda r3, r12: (r3 ** (np.minimum(A - 1, 3) / 3) * (r12 / r3) ** (np.clip(A - 4, 0, 9) / 9)
                           * (1 - v["churn_late"]) ** np.maximum(A - 13, 0))
    ps["s_on"], ps["s_door"] = ret(v["on_r3"], v["on_r12"]), ret(v["door_r3"], v["door_r12"])
    dep = v["daily"] * v["deposit_days"] * (1 + v["amount_growth"]) ** np.floor((A - 1) / v["term"])
    be, acc = np.zeros(M), 0.0
    for i in range(M):
        a = A[i]
        roll = v["rollover"] if (a - 1) - v["term"] * math.floor((a - 1) / v["term"]) == 0 else 1.0
        acc = (acc * roll * (1 - v["withdraw_m"]) + 0.5 * dep[i]) * (1 + d["fund_m"]) + 0.5 * dep[i]
        be[i] = acc
    bavg = (be - 0.5 * dep) / (1 + d["fund_m"])
    ps.update(dep=dep, endbal=be, bavg=bavg, trail_pa=bavg * d["trail"] / 12)
    tf = np.where(A <= 6, d["tf_e"], d["tf_f"])
    q1 = d["apply_m"] * tf * v["eligible"] * np.where(A <= 6, d["af_e"], d["af_f"])
    n0 = (1 - d["q1e"]) ** np.where(A - 1 > 6, 6, A - 1) * (1 - d["q1f"]) ** np.where(A - 7 > 0, A - 7, 0)
    first = n0 * q1
    back, rep, loans = np.zeros(M), np.zeros(M), np.zeros(M)
    Tn = d["tenure_m"]
    for i in range(M):
        if i:
            j = int(A[i] - 1 - Tn)
            back[i] = back[i - 1] - rep[i - 1] + (loans[max(1, j) - 1] if j >= 1 else 0.0)
        rep[i] = back[i] * d["apply_m"] * tf[i] * v["eligible"] * v["approved_repeat"]
        loans[i] = first[i] + rep[i]
    u = d["topup_m"]
    W = np.zeros(M)
    for i in range(M):
        a = int(A[i])
        if Tn > 13 and a >= 14:
            W[i] = sum(loans[max(1, a - 12 - k) - 1] * (1 - u) ** (k - 1) if a - 12 - k >= 1 else 0.0
                       for k in range(1, int(max(1, Tn - 13)) + 1))
    topups = u * W
    lent = first * v["ticket"] + rep * d["rep_ticket"] + topups * d["topup_amt"]
    cards = np.where(A <= 6, v["card_share"] / 6 * tf * d["card_ae"],
                     np.where(A <= 12, v["card_share"] * d["card_catchup"] / 6 * d["card_cg"], 0.0))
    ps.update(tf=tf, q1=q1, n0=n0, first=first, back=back, repeat=rep, loans=loans, tpool=W, topups=topups, lent=lent,
              loanfee_pa=lent * v["fee"] * (1 - v["taken_back"]), cards=cards, cardfee_pa=cards * v["card_fee"])
    # products
    NP = len(pr)
    he, hf = np.zeros(NP), np.zeros(NP)
    for k, r in enumerate(pr):
        hz = 1 - (1 - r["takeup"]) ** (1 / 12)
        sec = r["kind"] == "secured"
        he[k] = hz * d["tf_e"] * (min(0.8, r["appr"] * v["early_approval"] * d["ma_hold"]) if sec else 1.0)
        hf[k] = hz * d["tf_f"] * (min(0.8, r["appr"] * d["ma_hold"]) if sec else 1.0)
    G = np.zeros((M, NP))
    for k in range(NP):
        G[:, k] = np.where(A <= 6, (1 - he[k]) ** (A - 1) * he[k], (1 - he[k]) ** 6 * (1 - hf[k]) ** (A - 7) * hf[k])
    money = np.zeros((M, NP))
    for k, r in enumerate(pr):
        kd, tk = r["kind"], r["ticket"]
        sh = v["ins_share"] if r["ins"] == 1 else 1.0
        for i in range(M):
            a = i + 1
            g = G[i, k]
            if kd in ("once", "secured"):
                x = g * tk * r["comm"]
            elif kd == "ins":
                x = g * tk * r["comm"] + sum(G[max(1, a - 12 * kk) - 1, k] * r["renew"] ** kk * tk * r["rcomm"] if a - 12 * kk >= 1 else 0.0
                                             for kk in range(1, 8))
            elif kd == "bonus":
                x = G[max(1, a - 24) - 1, k] * r["renew"] * tk if a > 24 else 0.0
            else:
                x = sum(G[j - 1, k] * r["renew"] ** ((a - j) / 12) * ((a - j + 0.5) * tk * r["comm"] / 12 if kd == "trail" else
                                                                       (tk * r["comm"] / 12 if kd == "flow_year" else tk * r["comm"]))
                        for j in range(1, a + 1))
            money[i, k] = sh * x
    ins_mask = np.array([r["ins"] for r in pr])
    house_mask = np.array([r["house"] for r in pr])
    book = np.array([r["book"] for r in pr])
    ps.update(he=he, hf=hf, takeups=G, prodmoney=money, prodnow=G * book[None, :], ins_pa=money @ ins_mask, house_pa=money @ house_mask,
              pr_lag=np.array([r["lag"] for r in pr]), pr_ins=ins_mask, pr_house=house_mask,
              pr_loan=np.array([r.get("loan", 0.0) for r in pr]))
    ps["oth_pa"] = money @ np.ones(NP) - ps["ins_pa"] - ps["house_pa"]
    ps["support_pa"] = np.full(M, v["support"])
    ps["rev_pa"] = ps["trail_pa"] + ps["loanfee_pa"] + ps["cardfee_pa"] + ps["ins_pa"] + ps["house_pa"] + ps["oth_pa"]
    for sv in ("on", "door"):
        s = ps[f"s_{sv}"]
        ps[f"{sv}_dep"], ps[f"{sv}_bal"], ps[f"{sv}_trail"] = s * dep, s * bavg, s * ps["trail_pa"]
        ps[f"{sv}_loanfee"], ps[f"{sv}_cards"], ps[f"{sv}_ins"] = s * ps["loanfee_pa"], s * ps["cardfee_pa"], s * ps["ins_pa"]
        ps[f"{sv}_oth"] = s * (ps["oth_pa"] + ps["house_pa"])
        ps[f"{sv}_rev"] = ps[f"{sv}_trail"] + ps[f"{sv}_loanfee"] + ps[f"{sv}_cards"] + ps[f"{sv}_ins"] + ps[f"{sv}_oth"]
        reach_tech = v["loan_reach"] if sv == "on" else 1.0
        ps[f"{sv}_supp"] = s * (v["support"] + v["tech_per_saver"] * reach_tech + v["debit_cost"] * v["debits_month"])
        ps[f"{sv}_cum"] = np.cumsum(ps[f"{sv}_rev"] - ps[f"{sv}_supp"])
    ps["_d"] = d
    return ps


def roundup0(x):
    """Sheets ROUNDUP(x, 0) as toy_check's interpreter computes it."""
    x = np.asarray(x, dtype=float)
    return np.sign(x) * np.ceil(np.abs(x) - 1e-12)


def monthly(v, ps):
    d = ps["_d"]
    t = np.arange(1, M + 1, dtype=float)
    m = {"month": t}
    m["year"] = np.floor((t - 1) / 12) + 1
    m["yc"] = np.where(m["year"] > v["year_hold"], v["year_hold"], m["year"])
    m["f_t"] = (1 + v["takeup_growth"]) ** (m["yc"] - 1) / d["mt_hold"]
    m["f_ta"] = m["f_t"] * (1 + v["approval_growth"]) ** (m["yc"] - 1) / d["ma_hold"]
    m["feemult"] = v["fee_mult_start"] + (v["fee_mult_end"] - v["fee_mult_start"]) * (np.where(t > 60, 60, t) - 1) / 59
    raw = np.zeros(M)
    for i, tt in enumerate(t):
        if tt < v["launch"]:
            raw[i] = 0.0
        elif tt <= v["seed_end"]:
            raw[i] = v["seed_online"]
        elif tt <= v["ramp_end"]:
            raw[i] = v["seed_online"] + (v["level"] - v["seed_online"]) * (tt - v["seed_end"]) / (v["ramp_end"] - v["seed_end"])
        else:
            raw[i] = v["level"] * v["growth"] ** ((tt - v["ramp_end"]) / 12)
    m["raw"] = raw
    acc, cum = 0.0, np.zeros(M)
    for i in range(M):
        acc = acc + raw[i] * (1 + d["door_ratio"])
        cum[i] = acc
    m["cumraw"] = cum
    room = v["pool"] * v["pool_cap"]
    m["on_won"] = np.array([max(0.0, min(raw[i], (room - (cum[i - 1] if i else 0.0)) / (1 + d["door_ratio"]))) for i in range(M)])
    ag = np.zeros(M)
    for i, tt in enumerate(t):
        if tt < v["launch"] or (tt > v["seed_end"] and v["door_after"] < 0.5) or m["on_won"][i] <= 0:
            ag[i] = 0.0
        else:
            ag[i] = max(1.0, float(roundup0(m["on_won"][i] * d["door_ratio"] / v["agent_signups"])))
    m["agents"] = ag
    door = np.zeros(M)
    for i in range(M):
        a0 = ag[i]
        a1 = ag[i - 1] if i >= 1 else 0.0
        a2 = ag[i - 2] if i >= 2 else 0.0
        a3 = ag[i - 3] if i >= 3 else 0.0
        door[i] = v["agent_signups"] * (a0 - (1 - v["agent_ramp1"]) * max(0.0, a0 - a1) - (1 - v["agent_ramp2"]) * max(0.0, min(a0, a1) - a2)
                                        - (1 - v["agent_ramp3"]) * max(0.0, min(a0, a1, a2) - a3))
    m["door_won"] = door
    m["won"] = m["on_won"] + door
    Amat = np.zeros((M, M))                      # active savers in month m at age a
    for i in range(M):
        for a in range(i + 1):
            Amat[i, a] = m["on_won"][i - a] * ps["s_on"][a] + door[i - a] * ps["s_door"][a]
    m["active"] = Amat @ np.ones(M)
    m["aum"] = Amat @ ps["bavg"]
    m["r_fund"] = m["aum"] * d["trail"] / 12
    m["r_loan"] = (Amat @ ps["loanfee_pa"]) * m["f_ta"] * m["feemult"]
    m["r_cards"] = (Amat @ ps["cardfee_pa"]) * m["f_ta"]
    # cross-sell by product: money booked at take-up at this month's factor (home loans and LAP: take-up x approval), the
    # rest (renewals, the Choti bonus, holdings) at the take-up factor of its lag
    lag = ps["pr_lag"]
    tt = np.arange(1, M + 1)
    Flater = np.stack([m["f_t"][np.maximum(1, tt - int(L)) - 1] for L in lag], axis=1)
    Fnow = np.where(ps["pr_house"][None, :] == 1, m["f_ta"][:, None], m["f_t"][:, None])
    m["xs"] = (Amat @ ps["prodmoney"]) * Flater + (Amat @ ps["prodnow"]) * (Fnow - Flater)
    m["r_ins"] = m["xs"] @ ps["pr_ins"]
    m["r_oth"] = m["xs"] @ (1 - ps["pr_ins"])
    # loans to KYC'd users who came with online savers and never save: the online cohorts' loan money x (reach - 1)
    Aon = np.zeros((M, M))
    for i in range(M):
        for a in range(i + 1):
            Aon[i, a] = m["on_won"][i - a] * ps["s_on"][a]
    xs_on = (Aon @ ps["prodmoney"]) * Flater + (Aon @ ps["prodnow"]) * (Fnow - Flater)
    m["r_reach"] = (v["loan_reach"] - 1) * ((Aon @ ps["loanfee_pa"]) * m["f_ta"] * m["feemult"] + xs_on @ ps["pr_loan"])
    m["active_on"] = Aon @ np.ones(M)
    m["revenue"] = m["r_fund"] + m["r_loan"] + m["r_cards"] + m["r_ins"] + m["r_oth"] + m["r_reach"]
    m["mkt"] = m["on_won"] * np.where(t <= v["seed_end"], v["seed_cac"], v["cac_rs"])
    m["hires"] = np.array([max(0.0, ag[i] - (ag[i - 1] if i else 0.0)) for i in range(M)]) + ag * v["agent_churn"] / 12
    m["door_cost"] = (ag * v["agent_cost"] + np.where(ag > v["big_from"], roundup0(ag / v["per_lead"]) * v["lead_pay"]
                                                       + roundup0(ag / v["per_city"]) * v["city_office"], 0.0)
                      + m["hires"] * v["hire_kit"] + door * v["door_kyc"])
    m["acquisition"] = m["mkt"] + m["door_cost"]
    post = t > v["seed_end"]
    m["rf"] = np.where(post, (1 + v["raise_rate"]) ** np.floor((t - v["seed_end"] - 1) / 12), 1.0)
    m["seed_heads"] = np.where(post, 0.0, 3 + (t >= v["ops_from"]) + (t >= v["jr_from"]))
    m["seed_pay"] = np.where(post, 0.0, 2 * v["pay_founder_seed"] + v["pay_eng_seed"] + (t >= v["ops_from"]) * v["pay_ops_seed"]
                             + (t >= v["jr_from"]) * v["pay_jr_seed"])
    act = m["active"]
    m["eng"] = np.where(post, np.minimum(v["eng_cap"], v["eng_base"] + np.floor(act / v["eng_per"])), 0.0)
    m["product"] = np.where(post, 1 + np.floor(act / v["product_per"]), 0.0)
    m["ops"] = np.where(post, np.minimum(v["ops_cap"], np.maximum(v["ops_min"], roundup0(act / v["ops_per"]))), 0.0)
    m["growth_hc"] = np.where(post, 1 + np.floor(m["mkt"] / v["growth_per"]), 0.0)
    m["finance"] = np.where(post, 1 + np.floor(act / v["finance_per"]), 0.0)
    m["risk"] = np.where(post & (t >= v["risk_from"]), 1.0, 0.0)
    m["heads"] = m["seed_heads"] + np.where(post, 3.0, 0.0) + m["eng"] + m["product"] + m["ops"] + m["growth_hc"] + m["finance"] + m["risk"]
    m["team"] = (m["seed_pay"] + np.where(post, 2 * v["pay_founder"] + v["pay_compliance"], 0.0) + m["eng"] * v["pay_engineer"]
                 + m["product"] * v["pay_product"] + m["ops"] * v["pay_ops"] + m["growth_hc"] * v["pay_growth"]
                 + m["finance"] * v["pay_finance"] + m["risk"] * v["pay_risk"]) * m["rf"]
    m["tech"] = np.where(t <= 3, v["tech_build"] / 3, 0.0) + v["tech_base"] + (act + (v["loan_reach"] - 1) * m["active_on"]) * v["tech_per_saver"]
    m["office"] = np.where(post, v["office_base"] + m["heads"] * v["office_per_head"], v["office_seed"])
    m["compliance"] = np.where(t == 1, v["comp_setup"], 0.0) + np.where(post, v["comp_year"], v["comp_seed_year"]) / 12
    m["brand"] = np.where(post, v["brand"], 0.0)
    m["design"] = np.where(t <= 3, v["design"], 0.0)
    m["raise"] = np.where(t == 1, v["raise_seed"], 0.0) + np.where(t == v["seed_end"] + 1, v["raise_round"], 0.0)
    m["support"] = act * (v["support"] + v["debit_cost"] * v["debits_month"])
    m["other"] = m["tech"] + m["office"] + m["compliance"] + m["brand"] + m["design"] + m["raise"] + m["support"]
    m["contingency"] = v["contingency"] * (m["mkt"] + m["door_cost"] + m["team"] + m["tech"] + m["office"] + m["compliance"]
                                           + m["brand"] + m["design"] + m["raise"] + m["support"])
    m["ebitda"] = m["revenue"] - m["acquisition"] - m["team"] - m["other"] - m["contingency"]
    m["cum_ebitda"] = np.cumsum(m["ebitda"])
    m["tax"] = np.where((m["cum_ebitda"] > 0) & (m["ebitda"] > 0), v["tax_rate"] * np.minimum(m["ebitda"], m["cum_ebitda"]), 0.0)
    m["pat"] = m["ebitda"] - m["tax"]
    L = v["comm_lag"]
    m["received"] = np.array([m["revenue"][max(1, int(tt - L)) - 1] if tt > L else 0.0 for tt in t])
    m["cash_flow"] = m["pat"] - m["revenue"] + m["received"]
    m["cum"] = np.cumsum(m["cash_flow"])
    m["lens1"] = v["arr_mult"] * 12 * m["revenue"]
    m["lens2"] = v["aum_mult"] * m["aum"]
    return m


def sheet(v, prods=None):
    prods = prods or product_rows()
    ps = per_saver(v, prods)
    return ps, monthly(v, ps)


def profit_month(e):
    neg = np.flatnonzero(np.asarray(e) < 0)
    if not neg.size:
        return 1.0
    last = int(neg[-1]) + 1
    return float(last + 1) if last < len(e) else "after m96"


def measures(m, v):
    """The Summary measures (₹ crore where money), from the twin's monthly lines or from an engine run mapped to the same keys."""
    y = lambda a, k: float(np.asarray(a)[12 * (k - 1):12 * k].sum())
    lm = int(v["lens_month"]) - 1
    need = max(0.0, -float(np.min(m["cum"]))) + v["floor"]
    out = {"Revenue, year 5 (₹ crore)": y(m["revenue"], 5) / CR, "EBITDA, year 5 (₹ crore)": y(m["ebitda"], 5) / CR,
           "Revenue, year 8 (₹ crore)": y(m["revenue"], 8) / CR, "EBITDA, year 8 (₹ crore)": y(m["ebitda"], 8) / CR,
           "EBITDA positive from month (stays at or above 0 from here)": profit_month(m["ebitda"]),
           "Money needed: deepest cumulative cash hole + the ₹5 crore floor (₹ crore)": need / CR,
           "Money needed ($ million)": need / v["rs_per_usd"] / 1e6,
           "Active savers, month 60": float(m["active"][59]), "AUM (average fund balance), month 60 (₹ crore)": float(m["aum"][59]) / CR,
           "Savers won by month 60 (online + doorstep)": float(np.sum(m["on_won"][:60]) + np.sum(m["door_won"][:60])),
           "Lens 1 at month 60: 20 x revenue run-rate (₹ crore)": v["arr_mult"] * 12 * float(m["revenue"][lm]) / CR,
           "Lens 2 at month 60: 0.45 x AUM (₹ crore)": v["aum_mult"] * float(m["aum"][lm]) / CR}
    return out


def engine_monthly(o):
    """online_plan.company() output in the twin's keys."""
    return {"revenue": o["revenue"], "ebitda": o["ebitda"], "cum": np.cumsum(o["cash_flow"]), "active": o["active"], "aum": o["aum"],
            "on_won": o["online_won"], "door_won": o["door_won"], "agents": o["agents"], "pat": o["pat"],
            "r_fund": o["rev"]["Fund trail"], "r_loan": o["rev"]["Loan marketing fees"], "r_cards": o["rev"]["Cards"],
            "r_ins": o["rev"]["Insurance"], "r_oth": o["rev"]["Other products"], "acquisition": o["acquisition"],
            "team": o["people"], "other": o["opex"] - o["people"], "heads": o["heads"]}


# ---------------------------------------------------------------- engine checks and the reconciliation
def check_per_active_exact(v):
    """The sheet's per-active profile = the engine's profile of a cohort from month 49 on (calendar factor held), 1e-9."""
    ps = per_saver(v, product_rows())
    for xx, sk in ((X_ON, "s_on"), (X_DO, "s_door")):
        P = op.profiles(xx)
        c = 59                                              # cohort month 60
        s = P["still_saving"][c]
        assert np.allclose(ps[sk], s, rtol=1e-12, atol=0), sk
        pairs = [("balance", ps["bavg"]), ("rev_fund", ps["trail_pa"]), ("rev_origination", ps["loanfee_pa"]),
                 ("rev_cards", ps["cardfee_pa"]), ("loans", ps["loans"]), ("topups", ps["topups"]), ("money_lent", ps["lent"]),
                 ("cost_support", ps["support_pa"])]
        pairs += [(f"rev_xs_{p}", ps["prodmoney"][:, k]) for k, (p, *_r) in enumerate(ce.PRODUCTS)]
        for key, mine in pairs:
            ref = P[key][c] / s
            assert np.allclose(mine, ref, rtol=1e-9, atol=1e-12), (sk, key, float(np.max(np.abs(mine - ref))))
    return len(pairs)


LEVER_MAP = {  # online_plan.LEVERS / main() cases -> the v4 Inputs cells that reproduce them (all at 80,000 a month)
    "The plan": {},
    "24% still saving at a year (savings apps)": {"on_r12": 0.2415, "on_r3": 0.52},
    "45% still saving at a year": {"on_r12": 0.45},
    "Rs 200 a day": {"daily": 200.0},
    "Rs 300 a day": {"daily": 300.0},
    "10% apply for a loan a year": {f"takeup:{k[:-7]}" if k.endswith("_takeup") else k: x for k, x in op.loan_mix(0.10).items()},
    "50% apply for a loan a year": {f"takeup:{k[:-7]}" if k.endswith("_takeup") else k: x for k, x in op.loan_mix(0.50).items()},
    "Loan offers to savers only": {"loan_reach": 1.0},
    "Credit-hungry: 45% stay + 50% apply": {"on_r12": 0.45, **{f"takeup:{k[:-7]}" if k.endswith("_takeup") else k: x for k, x in op.loan_mix(0.50).items()}},
    "Cost to win Rs 300": {"cac_rs": 300.0},
    "Cost to win Rs 600 (our funnel)": {"cac_rs": 600.0},
    "Debt-only funds": {"eq_share": 0.0},
    "Online only after m18": {"door_after": 0.0},
}


def engine_lever(name, ch):
    ov = {}
    for k, val in ch.items():
        if k in ("on_r12", "on_r3", "daily", "apply"):
            ov[{"on_r12": "r12", "on_r3": "r3"}.get(k, k)] = val
        elif k.startswith("takeup:"):
            ov[f"{k[7:]}_takeup"] = val
        elif k == "loan_reach":
            ov["_loan_reach"] = val
    op.OV.clear()
    op.OV.update(ov)
    try:
        o = op.company(op.LEVER_LEVEL, 1.0, cac=ch.get("cac_rs", op.CAC), mix="debt" if ch.get("eq_share") == 0.0 else "80/20",
                       doorstep_after=ch.get("door_after", 1.0) >= 0.5)
    finally:
        op.OV.clear()
    return o


def gap_row(level, measure, sheet_v, py_v, kind, ebitda_like=False):
    if isinstance(sheet_v, str) or isinstance(py_v, str):
        return {"case": level, "measure": measure, "sheet": sheet_v, "python": py_v, "gap": "", "gap_pct": "",
                "target": "months equal or +/-1", "ok": sheet_v == py_v}
    gap = sheet_v - py_v
    gp = gap / abs(py_v) if py_v else float("nan")
    if kind == "month":
        ok, tgt = abs(gap) <= 1, "equal or +/-1 month"
    elif kind == "money":
        ok, tgt = abs(gp) <= 0.02, "within 2%"
    elif ebitda_like and abs(py_v) < 2.0:                    # EBITDA near zero: report the absolute gap (Rs crore)
        ok, tgt = abs(gap) <= 0.10, "near zero: absolute gap <= Rs 0.10 crore"
    else:
        ok, tgt = abs(gp) <= 0.01, "within 1%"
    return {"case": level, "measure": measure, "sheet": round(sheet_v, 6), "python": round(py_v, 6), "gap": round(gap, 6),
            "gap_pct": round(gp, 6) if gp == gp else "", "target": tgt, "ok": ok}


def reconcile():
    v0 = base_inputs()
    rows = []
    for lv in LEVELS:
        v = {**v0, "level": float(lv)}
        _ps, m = sheet(v)
        o = op.company(lv, 1.0)
        em = engine_monthly(o)
        for k in range(1, 9):
            s_ = slice(12 * (k - 1), 12 * k)
            rows.append(gap_row(lv, f"Revenue, year {k} (Rs crore)", m["revenue"][s_].sum() / CR, em["revenue"][s_].sum() / CR, "flow"))
            rows.append(gap_row(lv, f"EBITDA, year {k} (Rs crore)", m["ebitda"][s_].sum() / CR, em["ebitda"][s_].sum() / CR, "flow",
                                ebitda_like=True))
        ms, me = measures(m, v), measures(em, v)
        rows.append(gap_row(lv, "EBITDA positive from month", ms["EBITDA positive from month (stays at or above 0 from here)"],
                            me["EBITDA positive from month (stays at or above 0 from here)"], "month"))
        rows.append(gap_row(lv, "Money needed (Rs crore)", ms["Money needed: deepest cumulative cash hole + the ₹5 crore floor (₹ crore)"],
                            me["Money needed: deepest cumulative cash hole + the ₹5 crore floor (₹ crore)"], "money"))
        rows.append(gap_row(lv, "Active savers, month 60", ms["Active savers, month 60"], me["Active savers, month 60"], "flow"))
        rows.append(gap_row(lv, "AUM month 60 (Rs crore)", ms["AUM (average fund balance), month 60 (₹ crore)"],
                            me["AUM (average fund balance), month 60 (₹ crore)"], "flow"))
        rows.append(gap_row(lv, "Lens 1: 20x revenue run-rate m60 (Rs crore)", ms["Lens 1 at month 60: 20 x revenue run-rate (₹ crore)"],
                            me["Lens 1 at month 60: 20 x revenue run-rate (₹ crore)"], "flow"))
    # the levers at 80,000 a month: the same inputs typed into v4 Inputs
    for name, ch in LEVER_MAP.items():
        v = {**v0, "level": float(op.LEVER_LEVEL), **{k: x for k, x in ch.items() if not k.startswith("takeup:")}}
        prods = [dict(r, takeup=ch.get(f"takeup:{r['p']}", r["takeup"])) for r in product_rows()]
        _ps, m = sheet(v, prods)
        em = engine_monthly(engine_lever(name, ch))
        for k in (5, 8):
            s_ = slice(12 * (k - 1), 12 * k)
            rows.append(gap_row(f"lever: {name}", f"Revenue, year {k} (Rs crore)", m["revenue"][s_].sum() / CR, em["revenue"][s_].sum() / CR, "flow"))
            rows.append(gap_row(f"lever: {name}", f"EBITDA, year {k} (Rs crore)", m["ebitda"][s_].sum() / CR, em["ebitda"][s_].sum() / CR,
                                "flow", ebitda_like=True))
        rows.append(gap_row(f"lever: {name}", "EBITDA positive from month", profit_month(m["ebitda"]), profit_month(em["ebitda"]), "month"))
        rows.append(gap_row(f"lever: {name}", "Money needed (Rs crore)", (max(0, -m["cum"].min()) + v["floor"]) / CR,
                            (max(0, -em["cum"].min()) + v["floor"]) / CR, "money"))
    return rows


# ---------------------------------------------------------------- formula replay
MONTHLY_KEYS_FROM_SPEC = "_monthly_columns"


def replay_check(spec, v, label, ps=None, m=None):
    book = tc.Book(spec)
    t0 = time.time()
    errs = book.evaluate_all()
    assert not errs, (label, errs[:8])
    if m is None:
        ps, m = sheet(v)
    bad = []
    for key, col in spec[MONTHLY_KEYS_FROM_SPEC].items():
        got = np.array([float(book.cell("v4 Monthly", r_, tc.col_num(col))) for r_ in range(2, M + 2)])
        if not np.allclose(got, m[key], rtol=1e-9, atol=1e-6):
            bad.append((key, float(np.max(np.abs(got - m[key])))))
    for key, col in spec["_per_saver_columns"].items():
        got = np.array([float(book.cell("v4 Per saver", r_, tc.col_num(col))) for r_ in range(2, M + 2)])
        if not np.allclose(got, ps[key], rtol=1e-9, atol=1e-12):
            bad.append(("ps:" + key, float(np.max(np.abs(got - ps[key])))))
    for title, blocks in spec["_blocks"].items():
        for key, col in blocks.items():
            want_b = ps[key] if title == "v4 Per saver" else m[key]
            got = np.array([[float(book.cell(title, r_, tc.col_num(col) + j)) for j in range(want_b.shape[1])] for r_ in range(2, M + 2)])
            if not np.allclose(got, want_b, rtol=1e-9, atol=1e-9):
                bad.append((title, key, float(np.max(np.abs(got - want_b)))))
    r_, c_ = tc.parse_a1(spec["_summary_text_cell"])
    lm = int(v["lens_month"]) - 1
    yes = "yes" if min(m["lens1"][lm], m["lens2"][lm]) >= 1e9 * v["rs_per_usd"] else "no"
    if book.cell("v4 Summary", r_, c_) != yes:
        bad.append(("$1B cell", book.cell("v4 Summary", r_, c_), yes))
    want = measures(m, v)
    for cell, measure in spec["_summary_live"].items():
        r_, c_ = tc.parse_a1(cell)
        got = book.cell("v4 Summary", r_, c_)
        w = want[measure]
        ok = (got == w) if isinstance(w, str) else (not isinstance(got, str) and abs(float(got) - w) <= 1e-9 * max(1.0, abs(w)))
        if not ok:
            bad.append((cell, measure, got, w))
    for cell, (line, year) in spec["_yearly_live"].items():
        r_, c_ = tc.parse_a1(cell)
        got = float(book.cell("v4 Yearly", r_, c_))
        w = yearly_value(m, line, year)
        if abs(got - w) > 1e-9 * max(1.0, abs(w)):
            bad.append((cell, line, year, got, w))
    assert not bad, (label, bad[:10])
    return book.n_formulas, time.time() - t0


YEARLY = [  # label, monthly key, how (sum|end), scale (1 or crore)
    ("Online savers won", "on_won", "sum", 1), ("Doorstep savers won", "door_won", "sum", 1),
    ("Doorstep agents (year end)", "agents", "end", 1), ("Active savers (year end)", "active", "end", 1),
    ("AUM, average fund balance (year end, ₹ crore)", "aum", "end", CR),
    ("Revenue: fund trail (₹ crore)", "r_fund", "sum", CR), ("Revenue: loan marketing fees (₹ crore)", "r_loan", "sum", CR),
    ("Revenue: cards (₹ crore)", "r_cards", "sum", CR), ("Revenue: insurance (₹ crore)", "r_ins", "sum", CR),
    ("Revenue: other products incl. home loans and LAP (₹ crore)", "r_oth", "sum", CR),
    ("Revenue: loans to KYC'd users who never save (₹ crore)", "r_reach", "sum", CR), ("Revenue (₹ crore)", "revenue", "sum", CR),
    ("Cost to win online savers (₹ crore)", "mkt", "sum", CR), ("Doorstep agents' cost (₹ crore)", "door_cost", "sum", CR),
    ("Acquisition (₹ crore)", "acquisition", "sum", CR), ("Team (₹ crore)", "team", "sum", CR),
    ("Other costs: tech, office, compliance, brand, design, fund-raising, support (₹ crore)", "other", "sum", CR),
    ("Contingency (10%) (₹ crore)", "contingency", "sum", CR),
    ("EBITDA (₹ crore)", "ebitda", "sum", CR), ("Tax (₹ crore)", "tax", "sum", CR), ("PAT (₹ crore)", "pat", "sum", CR),
    ("Cash received from revenue (2 months after it is earned) (₹ crore)", "received", "sum", CR),
    ("Cash flow: PAT - revenue + cash received (₹ crore)", "cash_flow", "sum", CR),
    ("Cumulative cash, year end (₹ crore)", "cum", "end", CR), ("Heads (year end)", "heads", "end", 1),
]


def yearly_value(m, key, year):
    lab = next(y for y in YEARLY if y[1] == key)
    a = np.asarray(m[key], dtype=float)
    if year == 0:                                   # years 1-8 total
        return float(a.sum()) / lab[3]
    if lab[2] == "sum":
        return float(a[12 * (year - 1):12 * year].sum()) / lab[3]
    return float(a[12 * year - 1]) / lab[3]


def scenario_spec(spec, changes):
    s2 = json.loads(json.dumps(spec))
    inp = next(s for s in s2["sheets"] if s["title"] == "v4 Inputs")
    for k, val in changes.items():
        inp["cells"][inp["named_ranges"][PFX + k]] = val
    return s2


def main():
    v0 = base_inputs()
    n = check_per_active_exact(v0)
    print(f"per-active profile = the engine's month-60 cohort for both savers ({n} lines, 1e-9)")
    rows = reconcile()
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if not str(r["case"]).startswith("lever"):
            g = r["gap_pct"]
            print(f"  {r['case']!s:>7} {r['measure']:<44} sheet {r['sheet']!s:>14} python {r['python']!s:>14} "
                  f"gap {r['gap']!s:>10} {'' if g in ('', None) else f'{g:+.3%}':>9} {'ok' if r['ok'] else 'MISS'}")
    lev = [r for r in rows if str(r["case"]).startswith("lever")]
    print(f"levers: {sum(r['ok'] for r in lev)}/{len(lev)} within target; worst revenue gap "
          f"{max(abs(r['gap_pct']) for r in lev if 'Revenue' in r['measure']):.3%}")
    miss = [r for r in rows if not r["ok"]]
    print(f"wrote {OUT} ({len(rows)} rows; {len(miss)} outside target)")
    for r in miss:
        print("  MISS", r)
    if SPEC.exists():
        spec = json.loads(SPEC.read_text())
        nf, dt = replay_check(spec, v0, "base")
        print(f"formula replay (base, 20,000 a month): {nf} formulas, 0 errors; every Monthly / Per saver line, Summary and Yearly "
              f"live cell = the numpy twin ({dt:.0f}s)")
        for ch in ({"level": 150000.0},
                   {"level": 250000.0, "growth": 1.15, "cac_rs": 450.0, "on_r12": 0.45, "apply": 0.30},
                   {"level": 60000.0, "door_after": 0.0, "eq_share": 0.0, "approved_first": 0.7, "approval_growth": 0.3,
                    "takeup_growth": 0.3, "tenure": 30.4, "daily": 200.0}):
            v = {**v0, **ch}
            ps, m = sheet(v)
            nf, dt = replay_check(scenario_spec(spec, ch), v, str(ch), ps, m)
            capm = int(np.argmax(m["on_won"][op.SEED_END:] <= 0)) + op.SEED_END + 1 if (m["on_won"][op.SEED_END:] <= 0).any() else None
            print(f"formula replay {ch}: equal ({dt:.0f}s){'; pool cap stops sign-ups in month ' + str(capm) if capm else ''}")
    return rows


if __name__ == "__main__":
    main()

"""Monthly cohort model of one street agent: 60 calendar months, one cohort of sign-ups per month (operator, 16 Oct 2026:
"So let's build a model of monthly cohort, their retention and saving rate and every detail and model it like that").

Spec: story/BRIEF_cohort_mc_2026-10-16.md, story/COHORT_INPUTS_2026-10-16.md,
story/COHORT_INPUTS_addendum_crosssell_dpd_2026-10-16.md (17 cross-sell products; collection fees on high-DPD buckets) and
story/COHORT_INPUTS_addendum2_research_2026-10-16.md (operator decisions; new tickets) and
story/COHORT_INPUTS_addendum3_collections_fix_2026-10-16.md (collections per account; insurance commissions at the IRDAI
draft distributor caps).

How it works
  1. AGE PROFILE per sign-up: arrays over ages 1..60 ("age" = months since he signed up; age 1 = his first month) for
     every line (still saving, deposits, balance, UPI, visits, proven savers, the loan state split, loans, EMIs, cards,
     each cross-sell product, every revenue line, KYC). A Monte Carlo of D draws is one (D, 60) array per line.
  2. CALENDAR: month t total = sum over cohorts c <= t of signups[c] x profile[t - c + 1] (a truncated convolution;
     sign-ups vary by month because of the ramp). Salary, extra cash-collection capacity and support are calendar lines.
  3. OUTPUTS: monthly P&L, NPV at 36 and 60 months (20% a year, discounted monthly, month 1 discounted one month as v2),
     cumulative cash and the payback month, value per sign-up, pilot year-1 cash, savers / visits / UPI by month.

Mechanics (legacy=False)
  retention   s(1) = 1; s(a+1) = s(a) x (1 - h(a)); h = 1 - r3^(1/3) for ages 1-3, 1 - (r12/r3)^(1/9) for ages 4-12,
              churn_late after. So s(4) = r3 and s(13) = r12: "still saving at month m" = survived m monthly drop-offs,
              the v2 convention (v2: n(k) = (1 - c)^(k - 1), r12 = n(13)). A stopper withdraws his whole balance.
  saving      daily x days a month, stepped up by amount_growth at each yearly term start: x (1 + g)^floor((a-1)/12).
  balance     per active saver: start(a) = end(a-1), x rollover at a term end; withdraw_m of the start balance is taken
              out each month; the month's average = start(a)(1 - w) + deposit/2 (deposits spread over the month: v2's
              "k - 0.5"); the saver's net return (fund_return a year, monthly rate rm) accrues on that average at month end:
              end(a) = start(a)(1 - w) + deposit(a) + average x rm, so withdrawals and rollover apply to returns too.
              Fund commission = average balance x trail / 12.
  UPI         share of a cohort's active savers on UPI = upi_12 x min(1, (a - 1)/(upi_ramp - 1)): 0 at age 1, upi_12 from 12.
  capacity    cash visits a day = cash savers / visit_every. Above `capacity`, extra cost = Rs 20,000 a month per 400
              visits a day, pro-rata (a helper or a second agent).
  marketplace loans, cards and cross-sell are offered from age `marketplace_from` (operator 16 Oct: "the marketplace opens
              as soon as possible... It's not at our cost": month 1; v2 and legacy=True: month 7). "Offered" savers = still
              saving at age >= marketplace_from (the old "proven savers"). No marketplace cost line: the only costs are
              salary, extra capacity, KYC per sign-up and support (0).
  early       in a saver's months 1-6 (EARLY_MONTHS), every take-up hazard (loan apply, cards, the 17 products) x
              early_takeup_mult, and first-loan and card approval x early_approval_mult (operator 16 Oct: "month 1 for
              marketplace can have low take up rates and approval rates but business starts from there"); 1.0 from month 7.
  loans       Monthly apply hazard 1 - (1 - apply)^(1/12) on offered savers with no loan running. State split inside the age profile (all shares of the cohort's sign-ups):
                n0(a) active, never borrowed  -> first loans  = n0 x hazard x eligible x approved_first
                e(a)  active, repaid a loan   -> repeat loans = e  x hazard x eligible x approved_repeat
                active with a loan running    = s - n0 - e
              A loan made at age j is out of the applicant pool for ages j+1..j+T (T = tenure rounded to whole months;
              EMIs in ages j+1..j+T); the borrowers still saving at age j+T+1 return to e. Churn does not depend on the
              loan state, so the survivors of loan vintage j at age b are loans(j) x s(b)/s(j).
              A saver who stops keeps paying his loan (leaver_loan = yes) but never gets a repeat.
              EMI = the standard annuity on the ticket at `rate` (26% a year: the Rs 10,073 36-month EMI on Rs 2.5 lakh);
              used only for the EMIs-collected line.
  fees        origination = loans x ticket x fee x (1 - taken_back), first and repeat alike.
              overdue loans, per account (addendum 3), anchored on `loss` (owed = 0.5 when a loan goes 90+ days bad):
                p90 = loss / (owed x (1 - recovered)), the share of loans that ever go 90+ days bad
                31-90 days = early_cured x fee_early per loan made, paid 9 months after disbursal
                90+        = p90 x recovered x fee_b3 per loan made, paid 18 months after disbursal
              page check: early_cured + p90 <= 50%; fees due after month 60 fall outside the horizon.
  cards       card_share, issued once, evenly over the first 6 marketplace months (ages 1-6 from month 1), only to
              those still saving: cards(a) = card_share / 6 x s(a) x the early factors; the share the early factors held
              back (1 - their average over those months) is issued over the next 6 months at full rates (review fix, P3).
  cross-sell  17 products (PRODUCTS). Per product a yearly take-up hazard among offered savers still saving who never held
              it: never-held share N(a) = prod over j < a of (1 - H(j)), H(a) = hz x early factor (a >= mf =
              marketplace_from, else 0), take-ups(a) = s(a) N(a) H(a); a lapsed holder is not sold the
              product again (conservative). G(a) = take-ups(a) / s(a). Kinds:
                ins    first-year commission ticket x comm at take-up; renewal k years later: s(a) x G(a - 12k) x renew^k x
                       ticket x renew_comm (two-wheeler: the same rate as the first year)
                once   ticket x comm at take-up (device, NPS, FD, gold / consumer-durable / vehicle loans)
                flow   holders per active saver R(a) = R(a-1) x renew^(1/12) + G(a); s(a) x R(a) x monthly value
                       (gold: purchases x 2.4%; recharge: Rs 2,600 / 12 x comm; bills: bills a year / 12 x Rs a bill)
                trail  SIP: Q(a) = renew^(1/12)(Q(a-1) + R(a-1)); balance per active saver = SIP x (Q + R/2); x comm / 12
                bonus  Choti SIP: Rs 500 at month 24 of the SIP: s(a) x G(a - 24) x survival-to-24-months x 500
              Renewals and continuing flows are counted only while he is still saving: a policy lapses at its next
              renewal after he stops (stated as conservative).
  costs       KYC per sign-up at age 1; support per active saver (0, shown); salary; extra capacity.

Round 10 (story/CHANGES_round10_company_base_2026-10-17.md): the 0.25% pay on balance is capped at incentive_cap (Rs 10,000 a
month per agent, agreed key; fallback 10,000). The cap is flat here, like the agent unit's salary; the company model raises both
7% a year. Inputs without the key (legacy=True, v2_inputs, the bridge before its last step) are uncapped.

legacy=True reproduces tables/xs_npv_v2.csv (model/crosssell_money.py, salary only): steady drop-off from r12, the
yearly cycle balance with no rollover or withdrawal, no growth, no ramp, no capacity cost, no UPI, loans = proven x
apply/12 x eligible x approved (no state split, no repeats), cards once at month 7, insurance and other = Rs 63 a proven
saver a year flat (no products), no 31-90 day fees, no KYC, and the old recovery fee (ticket x npa x owed x recovered x
rec_fee) booked at disbursal x 1.2^-1.5 (v2's convention; `loss` is then v2's npa x owed x (1 - recovered)).

Distributions: DIST_FILE below (tables/dist_agreed_v1.csv, agreed 16 Oct; the proposal was dist_proposal_v1.csv).
Writes tables/cohort_legacy_check.csv, cohort_det_summary.csv, cohort_det_monthly.csv, cohort_det_age_profile.csv,
cohort_det_crosssell.csv.
"""
import csv
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
DIST_FILE = T / "dist_agreed_v1.csv"            # agreed with the operator 16 Oct (was dist_proposal_v1.csv)
FUND = "debt"                                     # operator decision 16 Oct: debt fund (trail_debt); "liquid" -> trail_liquid

AGES = 60
MONTHS = 60
REC_LAG = 18                 # months from disbursal to the 90+ recovery fee
DPD_LAG = 9                  # months from disbursal to the 31-90 day fees (addendum 2)
EARLY_P90_CAP = 0.50         # addendum 3: early_cured + p90 must stay <= 50%
HELPER_VISITS = 400.0        # extra_capacity_cost is Rs 20,000 a month per 400 visits a day, pro-rata
CARD_MONTHS = 6              # cards spread over ages 7-12
CHOTI_MONTHS = 24            # Choti SIP incentive paid at month 24 of the SIP
EARLY_MONTHS = 6             # a saver's months 1-6: early take-up and approval factors apply
SIGNUP_CAP = 100.0           # addendum 4 caps: sign-ups a month
TAKEUP_CAP = 2.0             # every take-up hazard (and the card approval factor) at most 2x the agreed rate
APPROVAL_CAP = 0.80          # first-loan approval at most 80%, absolute (XL-41: Kissht repeat 74%)
TICKET_CAP = 500000.0        # a repeat loan at most Rs 5 lakh (XL-12)
TOPUP_LAG = 13               # a top-up from the 13th month after disbursal (12 EMIs paid)
DECLINE_FROM, DECLINE_TO = 12, 49   # round 8: sign-ups flat in months 1-12, then a straight line to signup_decline_y5 at month 49

# ---------------------------------------------------------------- inputs
P_, T_, F_ = "pert", "triangular", "fixed"
BASE_FALLBACK = {  # (shape, low, likely, high): COHORT_INPUTS + the addendum; used only for keys DIST_FILE lacks
    "signups_run": (P_, 60, 100, 150), "ramp_months": (T_, 0, 3, 6),                     # round 8: year-1 level (PR-01)
    "signup_decline_y5": (P_, 0.5, 0.7, 0.9), "online_lead_share": (P_, 0.3, 0.5, 0.7), "lead_cost": (P_, 150, 250, 499),
    "fee_mult_start": (F_, 1.0, 1.0, 1.0), "fee_mult_end": (F_, 1.5, 1.5, 1.5),                # round 9: fee ramps from a DSA's rate
    "r3": (P_, 0.60, 0.80, 0.92), "r12": (P_, 0.25, 0.55, 0.72), "churn_late": (P_, 0.010, 0.015, 0.030),
    "daily": (T_, 200, 350, 500), "days": (P_, 16, 20, 24), "amount_growth": (P_, 0.0, 0.05, 0.10),
    "term": (F_, 12, 12, 12), "rollover": (P_, 0.0, 0.25, 0.60), "withdraw_m": (P_, 0.0, 0.01, 0.03),
    "fund_return": (P_, 0.06, 0.07, 0.075), "early_takeup_mult": (P_, 0.25, 0.50, 0.75), "early_approval_mult": (P_, 0.40, 0.60, 0.80),
    "signup_growth": (F_, 0.0, 0.0, 0.0), "takeup_growth": (P_, 0.0, 0.05, 0.15), "approval_growth": (P_, 0.0, 0.10, 0.20),   # signup_growth superseded in round 8
    "ticket_growth": (P_, 0.0, 0.10, 0.20), "topup_share": (P_, 0.05, 0.15, 0.30), "topup_size": (P_, 0.25, 0.40, 0.60),
    "trail": (P_, 0.002, 0.0035, 0.005),
    "upi_12": (P_, 0.10, 0.30, 0.60), "upi_ramp": (F_, 12, 12, 12), "visit_every": (F_, 2.5, 2.5, 2.5),
    "capacity": (T_, 300, 400, 450), "extra_capacity_cost": (F_, 20000, 20000, 20000),
    "apply": (P_, 0.08, 0.18, 0.35), "eligible": (P_, 0.25, 0.45, 0.65),
    "approved_first": (P_, 0.20, 0.35, 0.50), "approved_repeat": (P_, 0.50, 0.70, 0.85),
    "tenure": (P_, 24, 36, 48), "ticket": (P_, 25000, 250000, 500000), "fee": (P_, 0.010, 0.0175, 0.025),
    "taken_back": (T_, 0.0, 0.025, 0.05), "rate": (F_, 0.26, 0.26, 0.26), "loss": (P_, 0.015, 0.03, 0.05),
    "owed": (F_, 0.5, 0.5, 0.5), "recovered": (P_, 0.30, 0.35, 0.50), "early_cured": (P_, 0.10, 0.20, 0.35),
    "fee_early": (P_, 200, 450, 1000), "fee_b3": (P_, 1000, 2500, 5000),
    "leaver_loan": (F_, 1, 1, 1),
    "card_share": (P_, 0.01, 0.03, 0.06), "card_fee": (P_, 300, 1000, 2000),
    "salary": (F_, 20000, 20000, 20000), "kyc_cost": (P_, 0, 30, 100), "support_cost": (P_, 0, 5, 15),
    "discount": (F_, 0.20, 0.20, 0.20), "marketplace_from": (F_, 1, 1, 1),
    "cash_cover": (P_, 500, 1000, 2000), "ins_partner_share": (P_, 0.60, 0.75, 0.90),     # round 6
    "agent_balance_pay": (F_, 0.0025, 0.0025, 0.0025),                                     # round 7: a year of his savers' balance
    "incentive_cap": (F_, 10000, 10000, 10000),                                            # round 10: Rs a month per agent
}
# 17 cross-sell products (addendum section 1): prefix, kind, plain name, {param: (shape, low, likely, high)}, unit notes
PRODUCTS = [
    ("hlth_small", "ins", "Small health / hospital cash", {"takeup": (P_, 0.02, 0.06, 0.15), "ticket": (P_, 300, 800, 1500),
     "comm": (P_, 0.10, 0.14, 0.15), "renew": (P_, 0.30, 0.50, 0.70), "renew_comm": (F_, 0.05, 0.05, 0.05)}),
    ("hlth_family", "ins", "Family health cover", {"takeup": (P_, 0.005, 0.02, 0.05), "ticket": (P_, 5500, 8000, 15000),
     "comm": (P_, 0.10, 0.14, 0.15), "renew": (P_, 0.60, 0.75, 0.89), "renew_comm": (F_, 0.05, 0.05, 0.05)}),
    ("life_term", "ins", "Term life (small cover)", {"takeup": (P_, 0.01, 0.03, 0.06), "ticket": (P_, 500, 1000, 2000),
     "comm": (P_, 0.075, 0.20, 0.25), "renew": (P_, 0.60, 0.75, 0.85), "renew_comm": (F_, 0.075, 0.075, 0.075)}),
    ("accident", "ins", "Personal accident", {"takeup": (P_, 0.02, 0.05, 0.10), "ticket": (P_, 100, 250, 500),
     "comm": (P_, 0.10, 0.14, 0.15), "renew": (P_, 0.30, 0.50, 0.70), "renew_comm": (F_, 0.05, 0.05, 0.05)}),
    ("two_wheeler", "ins", "Two-wheeler insurance", {"takeup": (P_, 0.05, 0.15, 0.30), "ticket": (P_, 714, 1000, 1200),
     "comm": (P_, 0.025, 0.0475, 0.0905), "renew": (P_, 0.50, 0.70, 0.85)}),                     # renews at the same rate
    ("device", "once", "Mobile / device insurance", {"takeup": (P_, 0.01, 0.03, 0.06), "ticket": (P_, 209, 500, 899),
     "comm": (P_, 0.10, 0.13, 0.15)}),
    ("shop", "ins", "Shop insurance (fire and burglary)", {"takeup": (P_, 0.01, 0.03, 0.08), "ticket": (P_, 250, 700, 2600),
     "comm": (P_, 0.10, 0.14, 0.15), "renew": (P_, 0.50, 0.65, 0.80), "renew_comm": (F_, 0.05, 0.05, 0.05)}),
    ("sip", "trail", "Equity/hybrid SIP trail", {"takeup": (P_, 0.05, 0.10, 0.20), "ticket": (P_, 250, 500, 1000),
     "comm": (P_, 0.005, 0.0075, 0.009), "renew": (P_, 0.50, 0.65, 0.80)}),
    ("choti", "bonus", "Choti SIP incentive", {"takeup": (P_, 0.045, 0.09, 0.18), "ticket": (F_, 500, 500, 500),
     "renew": (P_, 0.15, 0.25, 0.40)}),
    ("nps", "once", "NPS", {"takeup": (P_, 0.01, 0.03, 0.05), "ticket": (F_, 200, 200, 200), "comm": (F_, 1, 1, 1)}),
    ("gold", "flow", "Digital gold", {"takeup": (P_, 0.03, 0.08, 0.15), "ticket": (P_, 100, 300, 600), "comm": (F_, 0.024, 0.024, 0.024),
     "renew": (P_, 0.50, 0.65, 0.80)}),
    ("fd", "once", "FD via partner banks", {"takeup": (P_, 0.05, 0.10, 0.20), "ticket": (P_, 5000, 10000, 20000),
     "comm": (P_, 0.001, 0.005, 0.01)}),
    ("recharge", "flow_year", "Mobile recharge", {"takeup": (P_, 0.10, 0.25, 0.50), "ticket": (F_, 2600, 2600, 2600),
     "comm": (P_, 0.01, 0.02, 0.03), "renew": (F_, 1, 1, 1)}),
    ("bills", "flow_year", "Bill payments", {"takeup": (P_, 0.10, 0.25, 0.50), "ticket": (P_, 12, 24, 36), "comm": (P_, 1, 2, 3),
     "renew": (F_, 1, 1, 1)}),
    ("loan_gold", "once", "Gold loan (other lenders)", {"takeup": (P_, 0.02, 0.05, 0.10), "ticket": (P_, 30000, 50000, 80000),
     "comm": (P_, 0.005, 0.01, 0.015)}),
    ("loan_cd", "once", "Consumer-durable loan", {"takeup": (P_, 0.005, 0.02, 0.05), "ticket": (P_, 10000, 20000, 30000),
     "comm": (P_, 0.01, 0.02, 0.03)}),
    ("loan_vehicle", "once", "Two-wheeler / e-rickshaw loan", {"takeup": (P_, 0.001, 0.005, 0.01), "ticket": (P_, 80000, 150000, 600000),
     "comm": (P_, 0.005, 0.01, 0.02)}),
    # round 5 (operator: "These guys can get home loans upto 20-50 lakhs"): other lenders' secured loans, once per saver
    ("loan_home", "secured", "Home loan (affordable housing)", {"takeup": (P_, 0.005, 0.015, 0.03), "ticket": (P_, 1000000, 2500000, 5000000),   # take-up: round 6 (family income counts)
     "comm": (P_, 0.003, 0.005, 0.01), "approval": (P_, 0.30, 0.45, 0.60)}),
    ("loan_lap", "secured", "Loan against property (shop or home)", {"takeup": (P_, 0.002, 0.005, 0.01), "ticket": (P_, 500000, 1500000, 3000000),
     "comm": (P_, 0.005, 0.01, 0.015), "approval": (P_, 0.30, 0.45, 0.60)}),
]
PNAME = {p: nm for p, _k, nm, _d in PRODUCTS}
INSURANCE = ("hlth_small", "hlth_family", "life_term", "accident", "two_wheeler", "device", "shop")
PKIND = {p: k for p, k, _nm, _d in PRODUCTS}
PARAM_WORDS = {"takeup": "take-up a year (savers offered who don't hold it)", "ticket": "ticket", "comm": "our commission",
               "renew": "renews / continues a year", "renew_comm": "renewal commission", "approval": "approval share"}
PARAM_WORDS_BY = {"sip": {"ticket": "SIP a month (Rs)", "comm": "trail a year, of the SIP balance", "renew": "SIP survives a year"},
                  "choti": {"ticket": "incentive (Rs, once at month 24)", "renew": "SIP survives to month 24"},
                  "gold": {"ticket": "bought a month (Rs)", "comm": "commission on purchases", "renew": "buying continues a year"},
                  "fd": {"ticket": "FD amount (Rs)", "comm": "commission (one year of the FD)"},
                  "recharge": {"ticket": "recharges a year (Rs)", "comm": "commission"},
                  "bills": {"ticket": "bills a year", "comm": "Rs a bill"},
                  "loan_home": {"ticket": "loan size (Rs)", "comm": "our fee, share of the loan"},
                  "loan_lap": {"ticket": "loan size (Rs)", "comm": "our fee, share of the loan"}}
FALLBACK = dict(BASE_FALLBACK)
for _p, _k, _nm, _d in PRODUCTS:
    for _q, _v in _d.items():
        FALLBACK[f"{_p}_{_q}"] = _v
KEYS = tuple(FALLBACK)
PRODUCT_KEYS = tuple(k for k in KEYS if k not in BASE_FALLBACK)

# Operator decisions, 16 Oct 2026 (coordinator message): enforced whatever the file says, and reported.
DECIDED = {"trail": (P_, 0.002, 0.0035, 0.005), "r12": (P_, 0.25, 0.55, 0.72), "card_share": (P_, 0.01, 0.03, 0.06),
           "tenure": (P_, 24, 36, 48),
           "discount": (F_, 0.0, 0.0, 0.0)}   # round 5: "we dont need to have a discount rate as of now ... cumulative PnL basis"
LEGACY_DISCOUNT = 0.20       # kept only for the "NPV (legacy, 20% discount)" rows
AGENT_PAY_AFTER = 0.0010     # round 7: agent pay on balance from company month 61 (outside the 60-month horizon)
GROWTH_MONTHS = 60           # round 7: the growth phase, company months 1-60
# Rows the addendum replaced: if the file still carries the pre-addendum values, the addendum's values are used.
STALE = {"signups_run": (P_, 20, 30, 45), "signup_growth": (P_, 0.0, 0.10, 0.20),     # round 8 rebase replaces these
         "fee": (P_, 0.015, 0.02625, 0.035),                                            # round 9: now a DSA's starting rate
         "recovered": (T_, 0.25, 0.325, 0.40), "loan_home_takeup": (P_, 0.003, 0.01, 0.02),   # round 5 value, raised in round 6
         **{f"{_p}_comm": (P_, 0.10, 0.15, 0.20) for _p in ("hlth_small", "hlth_family", "accident", "shop")},   # addendum 3 caps
         "life_term_comm": (P_, 0.075, 0.25, 0.30), "device_comm": (P_, 0.10, 0.15, 0.175)}
SUFFIX_ALIASES = {"takeup": ("takeup", "take_up", "take", "uptake"), "ticket": ("ticket", "premium", "amount", "size"),
                  "comm": ("comm", "commission", "fee", "rate", "take_rate"),
                  "renew": ("renew", "renewal", "persist", "persistence", "survive", "survival", "continue", "survive24"),
                  "renew_comm": ("renew_comm", "renewal_comm", "renew_commission", "renewal_commission"),
                  "approval": ("approval", "approved", "approve", "approval_share", "approve_share")}

NAMES = {
    "signups_run": "Sign-ups a month in year 1, once up to speed",
    "signup_decline_y5": "Sign-ups by month 49, as a share of the year-1 level (straight line from month 12)",
    "online_lead_share": "Share of onboardings that start as bought online leads", "lead_cost": "Our cost per online lead the agent converts (Rs)", "ramp_months": "Months for a new agent to reach full speed",
    "r3": "Still saving at month 3", "r12": "Still saving at month 12", "churn_late": "Monthly drop-off after month 12",
    "daily": "Daily amount at sign-up (Rs)", "days": "Deposit days a month", "amount_growth": "Growth in his daily amount per year saved",
    "term": "Savings term (months)", "rollover": "Share of the balance left in the fund at each term end",
    "withdraw_m": "Share of the balance withdrawn mid-term, each month", "trail": "Fund commission a year (debt fund)",
    "fund_return": "Saver's net return on the fund, a year", "early_takeup_mult": "Take-up factor in a saver's months 1-6",
    "early_approval_mult": "Approval factor in a saver's months 1-6 (first loans, cards)",
    "signup_growth": "Sign-up growth a year (superseded in round 8: 0)",
    "takeup_growth": "Every take-up rises each calendar year with the pool's history (cap 2x)",
    "approval_growth": "First-loan and card approval rise each calendar year (cap 80% absolute)",
    "ticket_growth": "Next loan bigger for each year repaid (cap Rs 5 lakh)",
    "topup_share": "Borrowers with 12+ EMIs paid who take a top-up, a year", "topup_size": "Top-up size, share of his original ticket",
    "upi_12": "Share of active savers on UPI by month 12", "upi_ramp": "Age at which the UPI share reaches its month-12 level",
    "visit_every": "Days between cash visits", "capacity": "Cash visits one agent can make a day",
    "extra_capacity_cost": "Extra capacity cost a month per 400 visits a day (Rs)",
    "apply": "Proven savers with no loan running who apply, a year", "eligible": "Applicants eligible",
    "approved_first": "Approved, first loan", "approved_repeat": "Approved, repeat loan", "tenure": "Loan tenure (months)",
    "ticket": "Loan size (Rs)", "fee": "Origination fee at the start: a DSA's rate (ramps up, see the multipliers)",
    "fee_mult_start": "Fee multiplier in company month 1", "fee_mult_end": "Fee multiplier reached in company month 60", "taken_back": "Fees taken back", "rate": "Loan interest rate a year (EMI basis)",
    "loss": "Money lost on loans, after recoveries", "owed": "Share of the loan still owed when it goes 90+ days bad",
    "recovered": "Recovered after 90 days", "early_cured": "Loans that fall 31-90 days behind and our agent brings back",
    "fee_early": "Our fee per early account brought back (Rs)", "fee_b3": "Our fee per 90+ account recovered (Rs)",
    "leaver_loan": "A saver who stops keeps paying his loan (1 = yes)",
    "card_share": "Savers reaching month 7 who get a card", "card_fee": "Fee per card (Rs)",
    "salary": "Agent's salary a month (Rs)", "kyc_cost": "Onboarding and KYC cost per sign-up (Rs)",
    "support_cost": "Support cost per active saver a month (Rs)", "discount": "Discount rate a year",
    "marketplace_from": "First month a saver is offered loans, cards and cross-sell (age)",
    "cash_cover": "Cash cover: fidelity and cash-in-transit insurance, per agent a month (Rs)",
    "ins_partner_share": "Share of insurance commission that reaches us through a broker partner",
    "agent_balance_pay": "Agent pay on his savers' average balance, a year (company months 1-60; 0.10% after)",
    "incentive_cap": "Cap on the agent's balance pay, per agent a month (Rs)",
}
for _p, _k, _nm, _d in PRODUCTS:
    for _q in _d:
        NAMES[f"{_p}_{_q}"] = f"{_nm}: {PARAM_WORDS_BY.get(_p, {}).get(_q, PARAM_WORDS[_q])}"


def _same(row_spec, spec, tol=1e-9):
    return row_spec[0] == spec[0] and all(abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b))) for a, b in zip(row_spec[1:4], spec[1:4]))


def load_dists(path=DIST_FILE, fund=FUND):
    """{key: (shape, low, likely, high, source)} for every engine key, read from the distribution file by `key`.
    `trail` is read from trail_<fund> when the file has it, else from `trail`. Product keys also match common suffix
    variants (e.g. hlth_small_premium for hlth_small_ticket). Keys the file lacks use FALLBACK (COHORT_INPUTS and the
    addendum). Operator decisions (DECIDED) are enforced; rows still carrying pre-addendum values (STALE) are replaced.
    Returns (dists, missing, notes)."""
    rows = {}
    if Path(path).exists():
        for r in csv.DictReader(Path(path).open()):
            rows[r["key"]] = r
    out, missing, notes = {}, [], {}
    for k in KEYS:
        r = rows.get(k)
        if k == "trail" and f"trail_{fund}" in rows:
            r = rows[f"trail_{fund}"]
            notes[k] = f"read from trail_{fund}"
        if r is None and k in PRODUCT_KEYS:
            p = next(pp for pp, *_ in PRODUCTS if k.startswith(pp + "_"))
            q = k[len(p) + 1:]
            for alt in SUFFIX_ALIASES.get(q, ()):
                if f"{p}_{alt}" in rows and alt != q:
                    r = rows[f"{p}_{alt}"]
                    notes[k] = f"read from {p}_{alt}"
                    break
        if r is None or not r.get("shape") or r.get("likely") in ("", None):
            sh, lo, li, hi = FALLBACK[k]
            spec = (sh, float(lo), float(li), float(hi), "fallback: COHORT_INPUTS / addendum")
            missing.append(k)
        else:
            sh = r["shape"].strip().lower()
            lo, li, hi = (float(r[c]) if r.get(c) not in ("", None) else float(r["likely"]) for c in ("low", "likely", "high"))
            src = "; ".join(v for v in (r.get("source_ids", ""), r.get("evidence_points", "")) if v)
            spec = (sh, lo, li, hi, src or Path(path).name)
        if k in DECIDED and not _same(spec, DECIDED[k]):
            notes[k] = f"operator decision enforced in code (file had {spec[0]} {spec[1]:g}/{spec[2]:g}/{spec[3]:g})"
            spec = (*DECIDED[k], "operator decision 16 Oct 2026")
        elif k in DECIDED:
            notes.setdefault(k, "file matches the operator decision")
        if k in STALE and _same(spec, STALE[k]):
            notes[k] = "file still had the pre-addendum values; addendum used"
            spec = (*FALLBACK[k], "addendum 16 Oct 2026")
        out[k] = spec
    return out, missing, notes


def likely_inputs(dists=None):
    dists = dists or load_dists()[0]
    return {k: v[2] for k, v in dists.items()}


def v2_inputs(r12):
    """The v2 base case (model/crosssell_money.py BASE, salary only), in this engine's keys (legacy=True)."""
    npa, owed, rec = 0.05, 0.5, 0.325
    return {"signups_run": 1000 / 12, "ramp_months": 0.0, "r3": r12 ** 0.25, "r12": r12, "churn_late": 1 - r12 ** (1 / 12),
            "daily": 350.0, "days": 20.0, "amount_growth": 0.0, "term": 12, "rollover": 0.0, "withdraw_m": 0.0, "trail": 0.0035,
            "fund_return": 0.0, "early_takeup_mult": 1.0, "early_approval_mult": 1.0, "signup_growth": 0.0, "takeup_growth": 0.0,
            "approval_growth": 0.0, "ticket_growth": 0.0, "topup_share": 0.0, "topup_size": 0.40,
            "upi_12": 0.0, "upi_ramp": 12, "visit_every": 2.5, "capacity": 400.0, "extra_capacity_cost": 20000.0,
            "apply": 0.20, "eligible": 0.50, "approved_first": 0.35, "approved_repeat": 0.35, "tenure": 36, "rate": 0.26,
            "ticket": 250000.0, "fee": 1.5 * 0.0175, "taken_back": 0.025, "loss": npa * owed * (1 - rec), "recovered": rec,
            "rec_fee": 0.10, "leaver_loan": 1, "card_share": 0.05, "card_fee": 1250.0, "other": 63.0,
            "salary": 20000.0, "kyc_cost": 0.0, "support_cost": 0.0, "discount": 0.20, "marketplace_from": 7,
            "cash_cover": 0.0, "ins_partner_share": 1.0, "agent_balance_pay": 0.0,
            "signup_decline_y5": 1.0, "online_lead_share": 0.0, "lead_cost": 0.0, "fee_mult_start": 1.0, "fee_mult_end": 1.0}


def _col(x, k, D):
    v = np.asarray(x[k], dtype=float).reshape(-1)
    return np.broadcast_to(v, (D,)).astype(float) if v.size in (1, D) else v


def _n(x):
    return max(np.asarray(v).size for v in x.values())


XS_REV = tuple(f"rev_xs_{p}" for p, *_ in PRODUCTS)
XS_BUYS = tuple(f"takeups_{p}" for p, *_ in PRODUCTS)
REVENUE = ("rev_fund", "rev_origination", "rev_dpd31_90", "rev_recovery90", "rev_cards", *XS_REV, "rev_other_v2")
AGE_LINES = ("still_saving", "stopped", "deposits", "balance", "fund_end", "withdrawn", "upi_share", "cash_savers", "cash_visits_a_day",
             "proven", "no_loan_yet", "repaid_eligible", "savers_with_loan", "applications", "loans_first", "loans_repeat", "loans",
             "topups", "money_lent_new", "money_lent", "loans_with_emi_due", "emis_collected", "accounts_cured_31_90",
             "accounts_recovered_90", "cards", *XS_BUYS, *REVENUE, "income", "cost_kyc", "cost_support")


def crosssell(s, a, pa, g, D, em_t, apf=None):
    """Take-ups and revenue per product, per sign-up, ages 1..AGES (see the module docstring).
    apf: approval factor (early months x pool history) for the secured loans, whose approval share is capped at 80%."""
    NA = s.shape[1]                                             # ages (60 unless the 120-month company run)
    out = {}
    for p, kind, _nm, _d in PRODUCTS:
        q = lambda name: g(f"{p}_{name}")
        H = (1 - (1 - q("takeup")) ** (1 / 12)) * em_t * (a > pa)
        if kind == "secured":                                   # applications x approval; the approved leave the pool
            H = H * np.minimum(APPROVAL_CAP, q("approval") * (1.0 if apf is None else apf))
        N = np.ones((D, NA))
        N[:, 1:] = np.cumprod(1 - H[:, :-1], axis=1)
        buys = s * N * H
        G = buys / s
        rev = np.zeros((D, NA))
        if kind in ("once", "secured"):
            rev = buys * q("ticket") * q("comm")
        elif kind == "ins":
            rev = buys * q("ticket") * q("comm")
            rc = q("renew_comm") if f"{p}_renew_comm" in FALLBACK else q("comm")
            for k in range(1, NA // 12 + 1):
                L = 12 * k
                rev[:, L:] += s[:, L:] * G[:, :-L] * q("renew") ** k * q("ticket") * rc
        elif kind == "bonus":
            rev[:, CHOTI_MONTHS:] = s[:, CHOTI_MONTHS:] * G[:, :-CHOTI_MONTHS] * q("renew") * q("ticket")
        else:                                                   # flow, flow_year, trail
            rho = q("renew")[:, 0] ** (1 / 12)
            R, Q = np.zeros((D, NA)), np.zeros((D, NA))
            for i in range(NA):
                if i:
                    R[:, i] = R[:, i - 1] * rho
                    Q[:, i] = rho * (Q[:, i - 1] + R[:, i - 1])
                R[:, i] += G[:, i]
            if kind == "trail":
                rev = s * q("ticket") * (Q + 0.5 * R) * q("comm") / 12
            else:
                rev = s * R * q("ticket") * q("comm") / (12 if kind == "flow_year" else 1)
        if p in INSURANCE:                                      # round 6: insurance through a broker partner
            rev = rev * g("ins_partner_share")
        out[f"takeups_{p}"] = buys
        out[f"rev_xs_{p}"] = rev
    return out


FEATURES = ("retention", "saving", "fund", "signups", "kyc", "capacity", "loans", "cards", "crosssell", "collections")


def _features(legacy):
    """legacy=True -> every new mechanic off (v2); False -> all on; a set/tuple -> only those on (the bridge)."""
    if legacy is True:
        return frozenset()
    if legacy is False or legacy is None:
        return frozenset(FEATURES)
    bad = set(legacy) - set(FEATURES)
    assert not bad, bad
    return frozenset(legacy)


def age_profile(x, legacy=False, cohort=None, ages=None, year_cap=None):
    """Per sign-up, ages 1..AGES. Returns {line: (R, AGES)} plus a few '_' entries used downstream.
    cohort: optional (R,) sign-up month of each row; then the calendar-year multipliers of addendum 4 (take-up and approval
    growing with the pool's history) apply at calendar month cohort + age - 1. Without it every row is in calendar year 1's
    terms (exact when takeup_growth = approval_growth = 0).
    ages (the 120-month company run, BRIEF_growth_and_100m): profile length; default AGES (60). year_cap: hold the calendar-year
    multipliers (take-up and approval growth) at that year's value after it (5 = their month-60 value); default none."""
    NA = AGES if ages is None else int(ages)
    on = _features(legacy)
    D = _n(x)
    g = lambda k: _col(x, k, D)[:, None]
    a = np.arange(1, NA + 1)[None, :]
    pa = int(round(float(np.mean(x["marketplace_from"])))) - 1          # offers from age pa + 1
    term = int(round(float(np.mean(x["term"]))))
    dm = (1 + g("discount")) ** (1 / 12) - 1
    # retention
    if "retention" not in on:
        h = np.broadcast_to(1 - g("r12") ** (1 / 12), (D, NA))
    else:
        h1, h2 = 1 - g("r3") ** (1 / 3), 1 - (g("r12") / g("r3")) ** (1 / 9)
        h = np.where(a <= 3, h1, np.where(a <= 12, h2, g("churn_late")))
    s = np.ones((D, NA))
    s[:, 1:] = np.cumprod(1 - h[:, :-1], axis=1)
    stopped = np.zeros((D, NA))
    stopped[:, 1:] = s[:, :-1] - s[:, 1:]
    # saving and the fund
    growth = 0.0 if "saving" not in on else g("amount_growth")
    dps = g("daily") * g("days") * (1 + growth) ** ((a - 1) // term)
    roll = np.zeros(D) if "fund" not in on else g("rollover")[:, 0]
    w = np.zeros(D) if "fund" not in on else g("withdraw_m")[:, 0]
    rm = (1 + g("fund_return")[:, 0]) ** (1 / 12) - 1                # the saver's net return, monthly
    em_t = np.where(a <= EARLY_MONTHS, g("early_takeup_mult"), 1.0)   # early-months factors (1.0 from month 7)
    em_a = np.where(a <= EARLY_MONTHS, g("early_approval_mult"), 1.0)
    if cohort is None:
        year = np.ones((D, NA))
    else:
        year = (np.asarray(cohort, dtype=float)[:, None] + a - 2) // 12 + 1     # calendar year of the business
        if year_cap is not None:
            year = np.minimum(year, year_cap)
    mt = (1 + g("takeup_growth")) ** (year - 1)
    ma = (1 + g("approval_growth")) ** (year - 1)
    tf = np.minimum(TAKEUP_CAP, em_t * mt)                                   # every take-up hazard's factor
    af = np.minimum(APPROVAL_CAP, g("approved_first") * em_a * ma)           # first-loan approval, absolute
    cf = tf * np.minimum(TAKEUP_CAP, em_a * ma)                              # cards: take-up x approval factors
    bs, be = np.zeros((D, NA)), np.zeros((D, NA))
    for i in range(NA):
        if i:
            bs[:, i] = be[:, i - 1] * (roll if i % term == 0 else 1.0)
        be[:, i] = bs[:, i] * (1 - w) + dps[:, i] + (bs[:, i] * (1 - w) + 0.5 * dps[:, i]) * rm
    bavg = bs * (1 - w[:, None]) + 0.5 * dps
    withdrawn = s * w[:, None] * bs
    withdrawn[:, 1:] += stopped[:, 1:] * be[:, :-1]
    for i in range(term, NA, term):
        withdrawn[:, i] += s[:, i] * (1 - roll) * be[:, i - 1]
    # UPI and visits
    upi = np.zeros((D, NA)) if "capacity" not in on else g("upi_12") * np.minimum(1.0, (a - 1) / (g("upi_ramp") - 1))
    cash = s * (1 - upi)
    proven = s * (a > pa)
    # loans
    Tn = np.maximum(1, np.floor(_col(x, "tenure", D) + 0.5)).astype(int)     # Excel ROUND for positive numbers
    rows = np.arange(D)
    topups = np.zeros((D, NA))
    if "loans" not in on:
        q = g("apply") / 12 * g("eligible") * g("approved_first")
        first, rep = proven * q, np.zeros((D, NA))
        apps = proven * g("apply") / 12
        n0 = e = None
    else:
        hz = (1 - (1 - g("apply")) ** (1 / 12)) * tf                     # (D, NA)
        q1 = hz * g("eligible") * af
        q2 = hz * g("eligible") * g("approved_repeat")
        n0, e = np.zeros((D, NA)), np.zeros((D, NA))
        first, rep, apps = np.zeros((D, NA)), np.zeros((D, NA)), np.zeros((D, NA))
        n0[:, 0] = 1.0
        for i in range(NA):
            if i + 1 > pa:
                first[:, i], rep[:, i], apps[:, i] = n0[:, i] * q1[:, i], e[:, i] * q2[:, i], (n0[:, i] + e[:, i]) * hz[:, i]
            if i + 1 < NA:
                sig = s[:, i + 1] / s[:, i]
                n0[:, i + 1] = (n0[:, i] - first[:, i]) * sig
                j = i - Tn                                   # loans made at index j are back in the pool at j+T+1
                ok = j >= 0
                jj = np.where(ok, j, 0)
                back = np.where(ok, (first[rows, jj] + rep[rows, jj]) * s[:, i + 1] / s[rows, jj], 0.0)
                e[:, i + 1] = (e[:, i] - rep[:, i]) * sig + back
        # top-ups (addendum 4): borrowers still saving with 12+ EMIs paid and EMIs still due, at most one per loan;
        # window sum W over loan vintages j in [age - T + 1, age - 13] of loans(j)/s(j) x (1 - u)^(age - j - 13)
        u = 1 - (1 - _col(x, "topup_share", D)) ** (1 / 12)
        lps_ = (first + rep) / s
        W = np.zeros((D, NA))
        drop = (1 - u) ** np.maximum(0, Tn - TOPUP_LAG)
        for i in range(1, NA):
            W[:, i] = (1 - u) * W[:, i - 1]
            if i >= TOPUP_LAG:
                W[:, i] += lps_[:, i - TOPUP_LAG] * (Tn > TOPUP_LAG)
            jj = i - Tn
            W[:, i] -= np.where((jj >= 0) & (Tn > TOPUP_LAG), lps_[rows, np.maximum(jj, 0)] * drop, 0.0)
        topups = s * u[:, None] * W
    loans = first + rep
    cl = np.zeros((D, NA + 1))
    cl[:, 1:] = np.cumsum(loans, axis=1)
    lo = np.maximum(0, np.arange(NA)[None, :] - Tn[:, None])
    due = cl[:, :NA] - cl[rows[:, None], lo]                     # loans made at ages a-T..a-1: an EMI is due at age a
    if "loans" not in on:
        cls = np.zeros((D, NA + 1))
        cls[:, 1:] = np.cumsum(loans / s, axis=1)
        with_loan = s * (cls[:, :NA] - cls[rows[:, None], lo])   # display only: same window as the state split
    else:
        with_loan = s - n0 - e
    im = _col(x, "rate", D) / 12
    emi = _col(x, "ticket", D) * im / (1 - (1 + im) ** (-Tn.astype(float)))
    emis = due * emi[:, None] * (1 - g("loss") / (1 - g("recovered")))
    rep_ticket = np.minimum(TICKET_CAP, g("ticket") * (1 + g("ticket_growth")) ** (Tn[:, None] / 12))   # after T/12 years repaid
    topup_amt = g("topup_size") * g("ticket") * (1 + g("ticket_growth"))                                # after a year repaid
    lent_new = first * g("ticket") + rep * rep_ticket
    lent = lent_new + topups * topup_amt
    loan_eq = loans + topups * topup_amt / g("ticket")             # collections base: top-ups pro rata by size
    # revenue: overdue-loan fees
    recovery, dpd = np.zeros((D, NA)), np.zeros((D, NA))
    cured, recd = np.zeros((D, NA)), np.zeros((D, NA))
    if "collections" not in on:
        rec_per_loan = g("ticket") * g("loss") * g("recovered") / (1 - g("recovered")) * g("rec_fee")
        recovery = loan_eq * rec_per_loan * (1 + dm) ** -REC_LAG
        dpd_per_loan = np.zeros((D, 1))
        p90 = early = np.full((D, 1), np.nan)
    else:
        p90 = g("loss") / (g("owed") * (1 - g("recovered")))
        early = g("early_cured")
        dpd_per_loan = early * g("fee_early")
        rec_per_loan = p90 * g("recovered") * g("fee_b3")
        dpd[:, DPD_LAG:] = loan_eq[:, :-DPD_LAG] * dpd_per_loan
        recovery[:, REC_LAG:] = loan_eq[:, :-REC_LAG] * rec_per_loan
        cured[:, DPD_LAG:] = loan_eq[:, :-DPD_LAG] * early
        recd[:, REC_LAG:] = loan_eq[:, :-REC_LAG] * p90 * g("recovered")
    cards = np.zeros((D, NA))
    if "cards" not in on:
        cards[:, pa] = s[:, pa] * g("card_share")[:, 0]
    else:
        win, nxt = slice(pa, pa + CARD_MONTHS), slice(pa + CARD_MONTHS, pa + 2 * CARD_MONTHS)
        cards[:, win] = (s * g("card_share") / CARD_MONTHS * cf)[:, win]
        # review fix (P3): the share the early-months factors held back is issued in the next 6 months at full rates
        rem = np.maximum(0.0, 1 - (em_t * em_a)[:, win].mean(axis=1, keepdims=True))
        cg = np.minimum(TAKEUP_CAP, mt) * np.minimum(TAKEUP_CAP, ma)
        cards[:, nxt] = (s * g("card_share") * rem / CARD_MONTHS * cg)[:, nxt]
    out = {
        "still_saving": s, "stopped": stopped, "deposits": s * dps, "balance": s * bavg, "fund_end": s * be, "withdrawn": withdrawn,
        "upi_share": upi + 0 * s, "cash_savers": cash, "cash_visits_a_day": cash / g("visit_every"), "proven": proven,
        "no_loan_yet": n0 if n0 is not None else np.full((D, NA), np.nan),
        "repaid_eligible": e if e is not None else np.full((D, NA), np.nan),
        "savers_with_loan": with_loan, "applications": apps, "loans_first": first, "loans_repeat": rep, "loans": loans,
        "topups": topups, "money_lent_new": lent_new, "money_lent": lent,
        "loans_with_emi_due": due, "emis_collected": emis, "accounts_cured_31_90": cured, "accounts_recovered_90": recd, "cards": cards,
        "rev_fund": s * bavg * g("trail") / 12, "rev_origination": lent * g("fee") * (1 - g("taken_back")),
        "rev_dpd31_90": dpd, "rev_recovery90": recovery, "rev_cards": cards * g("card_fee"),
    }
    if "crosssell" not in on:
        out.update({k: np.zeros((D, NA)) for k in XS_BUYS + XS_REV})
        out["rev_other_v2"] = proven * g("other") / 12
    else:
        out.update(crosssell(s, a, pa, g, D, tf, em_a * ma))
        out["rev_other_v2"] = np.zeros((D, NA))
    out["income"] = sum(out[k] for k in REVENUE)
    kyc = np.zeros((D, NA))
    if "kyc" in on:
        kyc[:, 0] = g("kyc_cost")[:, 0]
    out["cost_kyc"] = kyc
    out["cost_support"] = np.zeros((D, NA)) if "kyc" not in on else s * g("support_cost")
    out["_hazard"] = h + 0 * s
    out["_emi"] = emi
    out["_tenure_months"] = Tn
    out["_dm"] = dm[:, 0]
    out["_rec90_per_loan"] = rec_per_loan[:, 0]
    out["_dpd31_90_per_loan"] = dpd_per_loan[:, 0]
    out["_p90"], out["_early"] = p90[:, 0], early[:, 0]
    out["_year"] = year + 0 * s
    return out


def signups(x, legacy=False, months=MONTHS):
    D = _n(x)
    run_ = _col(x, "signups_run", D)[:, None]
    t = np.arange(1, months + 1)[None, :]
    if "signups" not in _features(legacy):
        return np.broadcast_to(run_, (D, months)).copy()
    ramp = _col(x, "ramp_months", D)[:, None]
    f = np.where(ramp > 0, np.minimum(1.0, 0.5 + 0.5 * (t - 1) / np.where(ramp > 0, ramp, 1.0)), 1.0)
    # round 8: year-1 level, then a straight line from month 12 to signup_decline_y5 of it at month 49, flat after (no growth, no cap)
    dec = _col(x, "signup_decline_y5", D)[:, None]
    decline = np.where(t <= DECLINE_FROM, 1.0, 1.0 + (dec - 1.0) * np.minimum(1.0, (t - DECLINE_FROM) / (DECLINE_TO - DECLINE_FROM)))
    return run_ * f * decline


MONTH_LINES = ("still_saving", "stopped", "deposits", "balance", "fund_end", "withdrawn", "cash_savers", "cash_visits_a_day", "proven",
               "savers_with_loan", "applications", "loans_first", "loans_repeat", "loans", "topups", "money_lent_new", "money_lent",
               "loans_with_emi_due", "emis_collected", "accounts_cured_31_90", "accounts_recovered_90", "cards", *XS_BUYS, *REVENUE,
               "income", "cost_kyc", "cost_support")


def to_calendar(S, prof, lines=MONTH_LINES, months=MONTHS):
    """month t total = sum over ages a <= t of signups[t - a + 1] x profile[a]."""
    P = np.stack([prof[k] for k in lines], axis=1)                # (D, K, AGES)
    out = np.zeros((P.shape[0], len(lines), months))
    for ti in range(months):
        out[:, :, ti] = np.einsum("da,dka->dk", S[:, ti::-1], P[:, :, :ti + 1])
    return {k: out[:, i, :] for i, k in enumerate(lines)}


def to_calendar_by_cohort(S, prof, D, C, lines=MONTH_LINES, months=MONTHS):
    """Cohort-specific profiles: rows d*C + (c-1). month t total = sum over cohorts c <= t of signups[c] x profile_c[t - c + 1]."""
    P = np.stack([prof[k] for k in lines], axis=1).reshape(D, C, len(lines), AGES)
    out = np.zeros((D, len(lines), months))
    for c in range(min(C, months)):
        out[:, :, c:] += S[:, c, None, None] * P[:, c, :, :months - c]
    return {k: out[:, i, :] for i, k in enumerate(lines)}


def calendar_growth(x, legacy=False):
    D = _n(x)
    return bool(np.any(_col(x, "takeup_growth", D) != 0) or np.any(_col(x, "approval_growth", D) != 0))


def run(x, legacy=False, months=MONTHS, force_cohorts=False, start_month=1):
    """One agent. x: {key: scalar or (D,) array}. Returns profiles, the monthly lines and the outputs (all (D,) or (D, M)).
    With calendar growth (takeup_growth or approval_growth not zero) every cohort has its own profile: rows = draws x cohorts.
    start_month (company model, 17 Oct): the company month of his tenure month 1. The company-calendar inputs (take-up and
    approval growth with the pool's history, the round-9 fee ramp, held at 1.5x after company month 60, and the agent-pay
    growth phase) then run on company month start_month + t - 1; his sign-ups, ramp and decline stay on his own tenure.
    The default (1) is the one-agent model unchanged."""
    D = _n(x)
    S = signups(x, legacy, months)
    off = int(start_month) - 1
    if calendar_growth(x, legacy) or force_cohorts:
        C = months
        xr = {k: np.repeat(_col(x, k, D), C) for k in x}
        coh = np.tile(np.arange(1, C + 1), D) + off
        pr = age_profile(xr, legacy, cohort=coh)
        m = to_calendar_by_cohort(S, pr, D, C, months=months)
        first_rows = np.arange(D) * C                               # cohort 1 of each draw: its own 60 months
        prof = {k: (v[first_rows] if np.ndim(v) >= 1 and np.shape(v)[0] == D * C else v) for k, v in pr.items()}
    else:
        prof = age_profile(x, legacy)
        m = to_calendar(S, prof, months=months)
    m["signups"] = S
    # round 9: origination fee in calendar month t = fee x (start + (end - start)(t - 1)/59), on first, repeat and top-up loans.
    # Origination is paid at disbursal and is linear in money lent, so the multiplier applies exactly to the month's line.
    tt0 = np.arange(1, months + 1)[None, :] + off
    if off:
        tt0 = np.minimum(tt0, MONTHS)                                      # the ramp is reached at company month 60 and held
    fmult = (_col(x, "fee_mult_start", D)[:, None]
             + (_col(x, "fee_mult_end", D) - _col(x, "fee_mult_start", D))[:, None] * (tt0 - 1) / (MONTHS - 1))
    m["fee_multiplier"] = fmult + 0 * S
    new_orig = m["rev_origination"] * fmult
    m["income"] = m["income"] + new_orig - m["rev_origination"]
    m["rev_origination"] = new_orig
    amult = fmult[:, :AGES] if AGES <= months else fmult                  # cohort 1: age a is calendar month a
    prof = {**prof, "income": prof["income"] + prof["rev_origination"] * (amult - 1), "rev_origination": prof["rev_origination"] * amult}
    cap, ve = _col(x, "capacity", D)[:, None], _col(x, "visit_every", D)[:, None]
    m["cost_salary"] = np.broadcast_to(_col(x, "salary", D)[:, None], (D, months)).copy()
    m["cost_extra_capacity"] = (np.zeros((D, months)) if "capacity" not in _features(legacy) else
                                np.maximum(0.0, m["cash_visits_a_day"] - cap) * _col(x, "extra_capacity_cost", D)[:, None] / HELPER_VISITS)
    m["cost_cash_cover"] = np.broadcast_to(_col(x, "cash_cover", D)[:, None], (D, months)).copy()
    tt = np.arange(1, months + 1)[None, :] + off                         # company month (growth phase = company months 1-60)
    pay_rate = np.where(tt <= GROWTH_MONTHS, _col(x, "agent_balance_pay", D)[:, None], AGENT_PAY_AFTER)
    m["cost_incentive"] = pay_rate / 12 * m["balance"]                     # round 7: rate / 12 x that month's average balance
    if "incentive_cap" in x:                                                # round 10: capped per agent a month (flat here, as the
        m["cost_incentive"] = np.minimum(m["cost_incentive"], _col(x, "incentive_cap", D)[:, None])   # salary; the company raises both)
    m["cost_leads"] = _col(x, "online_lead_share", D)[:, None] * _col(x, "lead_cost", D)[:, None] * S   # round 8: bought online leads
    m["cost_total"] = (m["cost_salary"] + m["cost_extra_capacity"] + m["cost_kyc"] + m["cost_support"] + m["cost_cash_cover"]
                       + m["cost_incentive"] + m["cost_leads"])
    m["net"] = m["income"] - m["cost_total"]
    act = np.where(m["still_saving"] > 0, m["still_saving"], np.nan)
    m["upi_share"] = 1 - m["cash_savers"] / act
    m["upi_share_needed"] = np.maximum(0.0, 1 - cap * ve / act)
    m["rev_crosssell"] = sum(m[k] for k in XS_REV) + m["rev_other_v2"]
    dm = prof["_dm"][:, None]
    t = np.arange(1, months + 1)[None, :]
    m["discount_factor"] = 1 / (1 + dm) ** t                       # discount = 0 since round 5: cumulative P&L
    m["pv_net"] = m["net"] * m["discount_factor"]
    m["cum_npv"] = np.cumsum(m["pv_net"], axis=1)
    m["cum_cash"] = np.cumsum(m["net"], axis=1)
    pos = m["cum_cash"] >= 0
    stays = np.flip(np.logical_and.accumulate(np.flip(pos, axis=1), axis=1), axis=1)   # positive from this month to month 60
    payback = np.where(stays.any(axis=1), stays.argmax(axis=1) + 1.0, np.nan)
    d20 = 1 / (1 + LEGACY_DISCOUNT) ** (t / 12)
    cum20 = np.cumsum(m["net"] * d20, axis=1)
    agedisc = 1 / (1 + dm) ** (np.arange(AGES)[None, :])
    value = ((prof["income"] - prof["cost_kyc"] - prof["cost_support"]) * agedisc).sum(axis=1)
    pv = lambda k, n: (m[k][:, :n] * m["discount_factor"][:, :n]).sum(axis=1)
    proven_years = m["proven"].sum(axis=1) / 12
    loans60 = m["loans"].sum(axis=1)
    yr = lambda k, y: m[k][:, 12 * (y - 1):12 * y].sum(axis=1)
    o = {
        "npv36": m["cum_npv"][:, 35], "npv60": m["cum_npv"][:, 59], "payback_month": payback,
        "cum_pnl36": m["cum_cash"][:, 35], "cum_pnl60": m["cum_cash"][:, 59],
        "peak_cash_need": np.minimum(0.0, m["cum_cash"].min(axis=1)),
        "npv36_legacy20": cum20[:, 35], "npv60_legacy20": cum20[:, 59],
        "housing_loans60": m["takeups_loan_home"].sum(axis=1) + m["takeups_loan_lap"].sum(axis=1),
        "housing_lent60": m["takeups_loan_home"].sum(axis=1) * (_col(x, "loan_home_ticket", D) if "loan_home_ticket" in x else 0.0)
                          + m["takeups_loan_lap"].sum(axis=1) * (_col(x, "loan_lap_ticket", D) if "loan_lap_ticket" in x else 0.0),
        "housing_fees60": m["rev_xs_loan_home"].sum(axis=1) + m["rev_xs_loan_lap"].sum(axis=1),
        "value_per_signup": value, "salary_per_signup": _col(x, "salary", D) / _col(x, "signups_run", D),
        "year1_cash": m["net"][:, :12].sum(axis=1), "cum_cash60": m["cum_cash"][:, 59],
        "savers_m12": m["still_saving"][:, 11], "savers_m60": m["still_saving"][:, 59], "offered_m60": m["proven"][:, 59],
        "visits_peak": m["cash_visits_a_day"].max(axis=1), "visits_m60": m["cash_visits_a_day"][:, 59],
        "upi_share_m60": m["upi_share"][:, 59], "upi_share_needed_m60": m["upi_share_needed"][:, 59],
        "extra_capacity_pv60": pv("cost_extra_capacity", 60), "extra_capacity_total60": m["cost_extra_capacity"].sum(axis=1),
        "extra_capacity_m60": m["cost_extra_capacity"][:, 59],
        "first_extra_capacity_month": np.where((m["cost_extra_capacity"] > 0).any(axis=1), (m["cost_extra_capacity"] > 0).argmax(axis=1) + 1.0, np.nan),
        "loans_per_100_offered_year": 100 * loans60 / proven_years,
        "first_loans_per_100_offered_year": 100 * m["loans_first"].sum(axis=1) / proven_years,
        "repeat_share_of_loans": m["loans_repeat"].sum(axis=1) / np.where(loans60 > 0, loans60, np.nan),
        "loans60": loans60, "cards60": m["cards"].sum(axis=1), "signups60": S.sum(axis=1),
        "topups60": m["topups"].sum(axis=1),
        "topups_per_100_borrowers_year": 100 * m["topups"].sum(axis=1) / (m["savers_with_loan"].sum(axis=1) / 12),
        "topups_per_100_loans": 100 * m["topups"].sum(axis=1) / np.where(loans60 > 0, loans60, np.nan),
        "money_lent60": m["money_lent"].sum(axis=1),
        **{f"money_lent_y{y}": yr("money_lent", y) for y in range(1, 6)},
        **{f"avg_ticket_y{y}": yr("money_lent_new", y) / np.where(yr("loans", y) > 0, yr("loans", y), np.nan) for y in range(1, 6)},
        **{f"loans_y{y}": yr("loans", y) for y in range(1, 6)},
        **{f"topups_y{y}": yr("topups", y) for y in range(1, 6)},
        "dpd31_90_per_loan": prof["_dpd31_90_per_loan"], "rec90_per_loan": prof["_rec90_per_loan"],
        "collections_per_loan": prof["_dpd31_90_per_loan"] + prof["_rec90_per_loan"],
        "p90": prof["_p90"], "early_plus_p90": prof["_early"] + prof["_p90"],
        "early_plus_p90_over_50pct": (prof["_early"] + prof["_p90"] > EARLY_P90_CAP).astype(float),
        "dpd31_90_paid60_per_loan": m["rev_dpd31_90"].sum(axis=1) / loans60, "rec90_paid60_per_loan": m["rev_recovery90"].sum(axis=1) / loans60,
        "xs_total_per_offered_year": m["rev_crosssell"].sum(axis=1) / proven_years,
        **{f"xs_{p}_per_offered_year": m[f"rev_xs_{p}"].sum(axis=1) / proven_years for p, *_ in PRODUCTS},
        "income_per_active_year": m["income"].sum(axis=1) / (m["still_saving"].sum(axis=1) / 12),
        "income_per_active_year_m60": 12 * m["income"][:, 59] / m["still_saving"][:, 59],
        "year1_collections": (m["rev_dpd31_90"][:, :12] + m["rev_recovery90"][:, :12]).sum(axis=1),
        "pv_income60": pv("income", 60), "pv_cost60": pv("cost_total", 60), "pv60_rev_crosssell": pv("rev_crosssell", 60),
        **{f"pv60_{k}": pv(k, 60) for k in REVENUE},
        **{f"pv60_{k}": pv(k, 60) for k in ("cost_salary", "cost_extra_capacity", "cost_kyc", "cost_support", "cost_cash_cover", "cost_incentive")},
        "lead_cost60": m["cost_leads"].sum(axis=1), "signups_m12": S[:, 11], "signups_m60": S[:, 59],
        "fee_m1": _col(x, "fee", D) * fmult[:, 0], "fee_m60": _col(x, "fee", D) * fmult[:, -1],
        "incentive_total60": m["cost_incentive"].sum(axis=1), "incentive_m12": m["cost_incentive"][:, 11],
        "incentive_m60": m["cost_incentive"][:, 59],
        "emi": prof["_emi"], "tenure_months": prof["_tenure_months"].astype(float),
    }
    return {"profile": prof, "monthly": m, "out": o}


def npv(x, months=60, legacy=False):
    return run(x, legacy)["monthly"]["cum_npv"][:, months - 1]


# ---------------------------------------------------------------- checks and tables
def legacy_check():
    v2 = {(int(r["years"]), float(r["r12"])): float(r["npv"]) for r in csv.DictReader((T / "xs_npv_v2.csv").open()) if r["pay"] == "salary only"}
    rows = []
    for r12 in (0.30, 0.40, 0.55, 0.70):
        res = run(v2_inputs(r12), legacy=True)["monthly"]["cum_npv"][0]
        for months in (36, 60):
            mine, theirs = res[months - 1], v2[(months // 12, r12)]
            rows.append({"r12": r12, "years": months // 12, "npv_v2": theirs, "npv_cohort_legacy": mine, "difference": mine - theirs,
                         "difference_pct": (mine - theirs) / abs(theirs) * 100, "within_1pct": abs(mine - theirs) <= 0.01 * abs(theirs)})
    assert all(r["within_1pct"] for r in rows), rows
    return rows


def state_split_check(x):
    """n0 + e + (active with a loan running) = still saving, with the loan window computed independently."""
    p = age_profile(x)
    Tn, s, L = p["_tenure_months"], p["still_saving"], p["loans"]
    for d in range(s.shape[0]):
        for i in range(AGES):
            win = sum(L[d, j] * s[d, i] / s[d, j] for j in range(max(0, i - Tn[d]), i))
            assert abs(p["savers_with_loan"][d, i] - win) < 1e-9, (d, i)
    return True


def cohort_path_check(x):
    """With take-up and approval growth at 0 the per-cohort path must equal the single age profile."""
    x0 = {**x, "takeup_growth": 0.0, "approval_growth": 0.0}
    a_, b_ = run(x0)["monthly"], run(x0, force_cohorts=True)["monthly"]
    for k in ("income", "net", "loans", "topups", "rev_crosssell", "cards"):
        assert np.allclose(a_[k], b_[k], rtol=1e-10, atol=1e-8), k
    return True


def topup_check(x):
    """The top-up recurrence against a direct sum over loan vintages."""
    p = age_profile(x)
    s, L, Tn = p["still_saving"][0], p["loans"][0], int(p["_tenure_months"][0])
    u = 1 - (1 - float(np.asarray(x["topup_share"]).reshape(-1)[0])) ** (1 / 12)
    want = np.zeros(AGES)
    for b in range(AGES):
        for j in range(AGES):
            k = b - j
            if TOPUP_LAG <= k <= Tn - 1:
                want[b] += L[j] * s[b] / s[j] * (1 - u) ** (k - TOPUP_LAG) * u
    assert np.allclose(p["topups"][0], want, rtol=1e-9, atol=1e-12)
    return True


def crosssell_check(x):
    """Each product's recurrence against a direct sum over take-up vintages."""
    p = age_profile(x)
    s = p["still_saving"][0]
    for pr, kind, _nm, d in PRODUCTS:
        G = p[f"takeups_{pr}"][0] / s
        v = lambda q: float(np.asarray(x[f"{pr}_{q}"]).reshape(-1)[0])
        want = np.zeros(AGES)
        for i in range(AGES):
            for j in range(i + 1):
                m = i - j
                if kind in ("once", "secured") and m == 0:
                    want[i] += s[i] * G[j] * v("ticket") * v("comm")
                elif kind == "ins":
                    if m % 12 == 0:
                        k = m // 12
                        want[i] += s[i] * G[j] * v("renew") ** k * v("ticket") * (v("comm") if k == 0 else v("renew_comm") if "renew_comm" in d else v("comm"))
                elif kind == "bonus" and m == CHOTI_MONTHS:
                    want[i] += s[i] * G[j] * v("renew") * v("ticket")
                elif kind in ("flow", "flow_year"):
                    want[i] += s[i] * G[j] * v("renew") ** (m / 12) * v("ticket") * v("comm") / (12 if kind == "flow_year" else 1)
                elif kind == "trail":
                    want[i] += s[i] * G[j] * v("renew") ** (m / 12) * v("ticket") * (m + 0.5) * v("comm") / 12
        if pr in INSURANCE:
            want = want * float(np.asarray(x["ins_partner_share"]).reshape(-1)[0])
        assert np.allclose(p[f"rev_xs_{pr}"][0], want, rtol=1e-9, atol=1e-12), pr
    return True


BRIDGE = [  # (feature switched on, plain words, keys taken from the agreed likely values at this step)
    ("retention", "Retention curve (r3 80%, r12 55%, then 1.5% a month) replaces the steady drop-off", ["r3", "r12", "churn_late"]),
    ("saving", "Saving rate: deposit days and 5% a year amount growth", ["daily", "days", "amount_growth"]),
    ("fund", "The fund: 25% kept at each term end, 1% a month withdrawn mid-term", ["term", "rollover", "withdraw_m", "trail"]),
    (None, "Fund return 7% a year accrues to his balance (raises the AUM and the trail)", ["fund_return"]),
    ("signups", "Sign-ups 60 a month (the earlier agreed value), with a 3-month ramp (from 83 flat)", ["signups_run", "ramp_months"],
     {"signups_run": 60.0}),
    ("kyc", "KYC cost per sign-up", ["kyc_cost"]),
    ("capacity", "UPI share and extra cash-collection capacity", ["upi_12", "upi_ramp", "capacity", "visit_every", "extra_capacity_cost"]),
    ("loans", "Loans at the agreed likely values (apply 18%, eligible 45%, approved 35%, tenure 36, repeats, fee, taken back)",
     ["apply", "eligible", "approved_first", "approved_repeat", "tenure", "ticket", "fee", "taken_back", "rate", "leaver_loan"],
     {"fee": 0.02625}),                                             # the earlier agreed 1.5 x a DSA; round 9's ramp is its own step
    ("cards", "Cards at 3%, spread over months 7-12 (fee Rs 1,000)", ["card_share", "card_fee"]),
    ("crosssell", "Seventeen cross-sell products plus home loans and LAP replace Rs 63 a year", list(PRODUCT_KEYS), {"loan_home_takeup": 0.01}),
    (None, "Marketplace from month 1 (was month 7): loans, cards and cross-sell", ["marketplace_from"]),
    (None, "Early-months factors: take-up x 0.5 and approval x 0.6 in a saver's months 1-6", ["early_takeup_mult", "early_approval_mult"]),
    (None, "Take-up and approvals grow with the pool's history (+5% and +10% a year)", ["takeup_growth", "approval_growth"]),
    (None, "Loan size grows 10% per year repaid (repeat loans and top-ups, cap Rs 5 lakh)", ["ticket_growth"]),
    (None, "Top-ups: 15% a year of borrowers with 12+ EMIs paid, at 40% of the ticket", ["topup_share", "topup_size"]),
    ("collections", "Collections by overdue bucket replace the old recovery fee", ["loss", "owed", "recovered", "early_cured", "fee_early", "fee_b3"]),
    (None, "Running cost Rs 5 an active saver a month (support, app, cash-deposit charges, supervision)", ["support_cost"]),
    (None, "Ticket range Rs 25,000 to 5 lakh (the likely value stays Rs 2.5 lakh: moves only the Monte Carlo)", ["ticket"]),
    (None, "Home-loan take-up 1.5% a year (family income counts; was 1%)", ["loan_home_takeup"]),
    (None, "Cash cover: fidelity and cash-in-transit insurance, Rs 1,000 an agent a month", ["cash_cover"]),
    (None, "Insurance through a broker partner: we keep 75% of insurance commissions", ["ins_partner_share"]),
    (None, "Sign-ups 30 a month (operator, after the sign-ups sweep; was 60)", ["signups_run"], {"signups_run": 30.0}),
    (None, "Agent pay: + 0.25% a year of his savers' balance (round 7)", ["agent_balance_pay"]),
    (None, "Sign-ups 100 a month in year 1, falling to 70 by year 5 (round 8 rebase, PR-01)", ["signups_run", "signup_decline_y5"]),
    (None, "Online leads at Rs 250 for half of onboardings (served offline)", ["online_lead_share", "lead_cost"]),
    (None, "Fee starts at a DSA's rate (1.75%) and ramps to 1.5x by month 60 (was 2.625% flat)", ["fee", "fee_mult_start", "fee_mult_end"]),
    (None, "Agent pay on balance capped at Rs 10,000 a month (round 10)", ["incentive_cap"]),
]


def bridge(xa, r12=0.55):
    """From the v2 legacy setting at r12 = 55%, switch on one change at a time, cumulatively (COHORT_RERUN section 3)."""
    x, on = {**v2_inputs(r12), "discount": xa["discount"]}, set()       # round 5: v2 on the same (undiscounted) basis
    res = run(x, legacy=True)
    rows = [{"step": 0, "what": f"v2 legacy setting, still saving at month 12 = {r12:.0%}", "npv60": float(res["out"]["npv60"][0]),
             "npv36": float(res["out"]["npv36"][0]), "change_in_npv60": "", "change_in_npv36": "",
             "payback_month": float(res["out"]["payback_month"][0])}]
    for i, (feat, what, keys, *ov) in enumerate(BRIDGE, 1):
        if feat:
            on.add(feat)
        x.update({k: xa[k] for k in keys})
        x.update(ov[0] if ov else {})                                 # a value a later step changes
        if feat == "retention":
            x["r12"] = r12
        o = run(x, legacy=frozenset(on))["out"]
        prev = rows[-1]
        rows.append({"step": i, "what": what, "npv60": float(o["npv60"][0]), "npv36": float(o["npv36"][0]),
                     "change_in_npv60": float(o["npv60"][0]) - prev["npv60"], "change_in_npv36": float(o["npv36"][0]) - prev["npv36"],
                     "payback_month": float(o["payback_month"][0])})
    left = {k for k in KEYS if k in xa and abs(float(x.get(k, np.nan)) - float(xa[k])) > 1e-12}
    final = run({**xa, "r12": r12})["out"]
    assert not left or left == {"r12"}, f"bridge did not reach the agreed inputs: {left}"
    assert abs(rows[-1]["npv60"] - float(final["npv60"][0])) < 1e-6, "bridge end != full model"
    return rows


def write(name, rows):
    with (T / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


DET_LABELS = [  # key, plain words, unit
    ("cum_pnl36", "Cumulative P&L at 36 months", "Rs, undiscounted"), ("cum_pnl60", "Cumulative P&L at 60 months", "Rs, undiscounted"),
    ("payback_month", "Payback month (cumulative P&L turns positive)", "month (and stays positive)"),
    ("peak_cash_need", "Peak cash need (lowest cumulative P&L)", "Rs (negative: the cash needed is its size)"),
    ("npv36_legacy20", "NPV (legacy, 20% discount): NPV at 36 months", "Rs"), ("npv60_legacy20", "NPV (legacy, 20% discount): NPV at 60 months", "Rs"),
    ("housing_loans60", "Home loans and LAP made in 60 months (other lenders)", "loans"),
    ("housing_lent60", "Home-loan and LAP money lent in 60 months (other lenders' books)", "Rs"),
    ("housing_fees60", "Our fees on home loans and LAP in 60 months", "Rs"),
    ("value_per_signup", "Value per sign-up, his first 5 years, discounted to his sign-up month", "Rs"),
    ("salary_per_signup", "Agent's salary per sign-up (for comparison)", "Rs"),
    ("year1_cash", "Year-1 P&L", "Rs (months 1-12)"), ("cum_cash60", "Cumulative cash at month 60", "Rs"),
    ("savers_m12", "Savers still saving at month 12", "savers"), ("savers_m60", "Savers still saving at month 60", "savers"),
    ("offered_m60", "Savers offered the marketplace at month 60", "savers"), ("visits_peak", "Peak cash visits a day", "visits a day"),
    ("visits_m60", "Cash visits a day at month 60", "visits a day"), ("upi_share_m60", "Share of savers on UPI at month 60", "share"),
    ("upi_share_needed_m60", "UPI share needed at month 60 to stay within one agent's capacity", "share"),
    ("first_extra_capacity_month", "First month extra capacity is needed", "month"),
    ("extra_capacity_m60", "Extra capacity cost in month 60", "Rs a month"), ("extra_capacity_total60", "Extra capacity cost, 60 months, not discounted", "Rs"),
    ("extra_capacity_pv60", "Extra capacity cost, 60 months, discounted", "Rs"),
    ("loans_per_100_offered_year", "Loans per 100 savers offered the marketplace, a year (first + repeat)", "loans"),
    ("first_loans_per_100_offered_year", "First loans per 100 savers offered the marketplace, a year", "loans"),
    ("repeat_share_of_loans", "Repeat loans as a share of all loans", "share"), ("loans60", "Loans made in 60 months", "loans"),
    ("p90", "Implied share of loans that ever go 90+ days bad (p90; CRIF NG-015 10.2%, MAC-03 3.6%)", "share of loans"),
    ("early_plus_p90", "Early brought back + p90 (page check: at most 50%)", "share of loans"),
    ("dpd31_90_per_loan", "31-90 day collection fees per loan made", "Rs a loan"),
    ("rec90_per_loan", "90+ recovery fees per loan made", "Rs a loan"),
    ("collections_per_loan", "All collection fees per loan made", "Rs a loan"),
    ("dpd31_90_paid60_per_loan", "31-90 day fees paid within 60 months, per loan made", "Rs a loan"),
    ("rec90_paid60_per_loan", "90+ fees paid within 60 months, per loan made", "Rs a loan"),
    ("year1_collections", "Collection fees (31-90 days and 90+) in the pilot year", "Rs"),
    ("xs_total_per_offered_year", "Cross-sell money per saver offered the marketplace, a year, all 17 products (old Rs 63)", "Rs"),
    *[(f"xs_{p}_per_offered_year", f"  {nm}", "Rs a saver offered, a year") for p, _k, nm, _d in PRODUCTS],
    ("income_per_active_year", "All-in revenue per active saver a year, 60-month average (fund + loans + cards + products + collections)", "Rs"),
    ("income_per_active_year_m60", "All-in revenue per active saver a year, month-60 run rate", "Rs"),
    ("topups60", "Top-ups in 60 months", "top-ups"),
    ("topups_per_100_borrowers_year", "Top-ups per 100 borrowers a year (borrowers still saving with a loan running)", "top-ups"),
    ("topups_per_100_loans", "Top-ups per 100 loans made", "top-ups"),
    ("money_lent60", "Money lent in 60 months (first, repeat and top-up loans)", "Rs"),
    *[(f"money_lent_y{y}", f"  money lent in year {y}", "Rs") for y in range(1, 6)],
    *[(f"avg_ticket_y{y}", f"  average ticket of first and repeat loans, year {y}", "Rs") for y in range(1, 6)],
    ("cards60", "Cards issued in 60 months", "cards"), ("signups60", "Sign-ups in 60 months", "sign-ups"),
    ("pv_income60", "Income, 60 months, discounted", "Rs"), ("pv_cost60", "Costs, 60 months, discounted", "Rs"),
    ("pv60_rev_fund", "  of which fund commission", "Rs"), ("pv60_rev_origination", "  of which origination fees net of taken back", "Rs"),
    ("pv60_rev_dpd31_90", "  of which 31-90 day collection fees", "Rs"), ("pv60_rev_recovery90", "  of which 90+ recovery fees", "Rs"),
    ("pv60_rev_cards", "  of which cards", "Rs"), ("pv60_rev_crosssell", "  of which cross-sell (17 products)", "Rs"),
    ("pv60_cost_salary", "  cost: salary", "Rs"), ("pv60_cost_extra_capacity", "  cost: extra capacity", "Rs"),
    ("pv60_cost_kyc", "  cost: KYC", "Rs"), ("pv60_cost_support", "  cost: running cost (support, app, deposits)", "Rs"),
    ("pv60_cost_cash_cover", "  cost: cash cover", "Rs"), ("pv60_cost_incentive", "  cost: agent pay on balance", "Rs"),
    ("fee_m1", "Origination fee in month 1 (a DSA's rate)", "share of the loan"), ("fee_m60", "Origination fee in month 60", "share of the loan"),
    ("lead_cost60", "Online lead cost, 60 months", "Rs"), ("signups_m12", "Sign-ups in month 12", "sign-ups"),
    ("signups_m60", "Sign-ups in month 60", "sign-ups"),
    ("incentive_total60", "Agent pay on balance, 60 months", "Rs"), ("incentive_m12", "Agent pay on balance in month 12", "Rs a month"),
    ("incentive_m60", "Agent pay on balance in month 60", "Rs a month"),
    ("emi", "EMI on one loan", "Rs a month"), ("tenure_months", "Loan tenure used (rounded)", "months"),
]


def main():
    leg = legacy_check()
    write("cohort_legacy_check.csv", leg)
    dists, missing, notes = load_dists()
    x = likely_inputs(dists)
    br = bridge(x)
    write("cohort_bridge.csv", br)
    state_split_check({k: np.array([v, v]) if k != "tenure" else np.array([v, 30.0]) for k, v in x.items()})
    crosssell_check(x)
    topup_check(x)
    cohort_path_check(x)
    res = run(x)
    o = {k: float(v[0]) for k, v in res["out"].items()}
    dl, _, nl = load_dists(fund="liquid")
    alt = {k: float(v[0]) for k, v in run({**x, "trail": dl["trail"][2]})["out"].items()} if "trail_liquid" in str(nl.get("trail")) else {}
    m7 = {k: float(v[0]) for k, v in run({**x, "marketplace_from": 7})["out"].items()}
    c27 = {k: float(v[0]) for k, v in run({**x, "churn_late": 0.027})["out"].items()}
    write("cohort_det_summary.csv", [{"measure": nm, "unit": u, "value": o[k], "if_marketplace_from_month_7": m7.get(k, ""),
                                      "if_late_drop_off_2_7pct": c27.get(k, ""), "if_liquid_fund": alt.get(k, "")} for k, nm, u in DET_LABELS])
    print(f"  SIDE marketplace from month 7: NPV60 {m7['npv60']:,.0f}; late drop-off 2.7%: NPV60 {c27['npv60']:,.0f}, NPV36 {c27['npv36']:,.0f}")
    m = res["monthly"]
    cols = ["signups", "still_saving", "stopped", "proven", "cash_savers", "cash_visits_a_day", "upi_share", "upi_share_needed", "deposits",
            "balance", "fund_end", "withdrawn", "applications", "loans_first", "loans_repeat", "loans", "savers_with_loan", "loans_with_emi_due",
            "emis_collected", "accounts_cured_31_90", "accounts_recovered_90", "cards", *XS_BUYS, *REVENUE, "rev_crosssell", "income",
            "cost_salary", "cost_extra_capacity",
            "cost_kyc", "cost_support", "cost_cash_cover", "cost_incentive", "cost_leads", "cost_total", "net", "discount_factor", "pv_net",
            "cum_npv", "cum_cash"]
    write("cohort_det_monthly.csv", [{"month": t + 1, **{c: float(m[c][0, t]) for c in cols}} for t in range(MONTHS)])
    p = res["profile"]
    write("cohort_det_age_profile.csv", [{"age": i + 1, "monthly_drop_off": float(p["_hazard"][0, i]), **{c: float(p[c][0, i]) for c in AGE_LINES}}
                                         for i in range(AGES)])
    write("cohort_det_lending.csv", [{"year": y, "loans_first_and_repeat": o[f"loans_y{y}"], "topups": o[f"topups_y{y}"],
                                      "average_ticket_first_and_repeat": o[f"avg_ticket_y{y}"], "money_lent": o[f"money_lent_y{y}"]}
                                     for y in range(1, 6)])
    py = m["proven"][0].sum() / 12
    write("cohort_det_crosssell.csv", [{"product": nm, "key": pr, "kind": kd, "takeups_60_months": float(m[f"takeups_{pr}"][0].sum()),
                                        "money_60_months": float(m[f"rev_xs_{pr}"][0].sum()), "per_saver_offered_a_year": float(m[f"rev_xs_{pr}"][0].sum() / py),
                                        "pv60": o.get(f"pv60_rev_xs_{pr}", "")}
                                       for pr, kd, nm, _d in PRODUCTS])
    print("LEGACY v2 regression (salary only):")
    for r in leg:
        print(f"  R12 {r['r12']:.0%} {r['years']}y: v2 {r['npv_v2']:>12,.0f}  cohort {r['npv_cohort_legacy']:>12,.0f}  diff {r['difference_pct']:+.6f}%")
    print(f"distributions from {DIST_FILE.name}; {len(missing)} keys from the fallback: {missing}")
    for k, v in notes.items():
        print(f"  note {k}: {v}")
    for b in br:
        ch = b["change_in_npv60"]
        print(f"  BRIDGE {b['step']:>2} NPV60 {b['npv60']:>11,.0f} ({'' if ch == '' else f'{ch:+,.0f}':>10}) NPV36 {b['npv36']:>11,.0f} "
              f"payback {b['payback_month']!s:>5}  {b['what']}")
    for k, nm, u in DET_LABELS:
        print(f"  {nm:<80} {o[k]:>14,.2f} {u}" + (f"   (liquid fund: {alt[k]:,.0f})" if alt and k in ('npv36', 'npv60') else ""))
    return leg, o, missing


if __name__ == "__main__":
    main()

"""The money each product makes, with tight assumptions (operator, 16 Oct 2026: "Story should carry tight assumptions,
money we can make on credit card etc. show that ... build a tight story. show those assumptions in appendix").

Builds on model/agent_npv.py (saver, agent pay, retention, discount) and model/marketplace.py (loan funnel, ticket,
collections). Both are imported, never edited; the engine below reproduces them and asserts that it does.

Base case (story/BRIEF_final_v2_2026-10-16.md, decided):
  agent        Rs 20,000 a month, salary only; stress pays + 0.5% a year of balance, + 1% of collections (N.PAYS)
  saver        1,000 sign-ups a year joining monthly; Rs 350 a day x 20 days; steady monthly drop-off from "still saving
               after 12 months"; balance = half a year's deposits; 20% a year discount, monthly; 3 and 5 years
  loans        per proven saver (saved 6+ months) a year: apply 20% x eligible 50% x approved 35% = 3.5 per 100;
               Rs 2.5 lakh at 2.625% (1.5 x a DSA's 1.75%), less 2.5% taken back = Rs 6,398 a loan
  collections  marketplace.py middle: Rs 155 a loan (small)
  cards        TIGHTENED: 5% of PROVEN savers, once, in month 7, Rs 1,250 a card (was 5% of sign-ups in the month he joins)
  other        insurance and other products Rs 63 a year per PROVEN saver, from month 7 (fix round 1, M2; XO-39)
  balance      yearly terms (fix round 1, M1): in saver-month k he holds Rs 7,000 x (((k-1) mod 12) + 0.5); Rs 42,000 on
               average over a full term; a saver who stops withdraws, so his balance (and our commission) goes to zero
  capacity     about 400 cash visits a day, one visit every 2.5 days = 1,000 savers on cash (agent_3yr.py, scenarios.py);
               no second agent: the share of his book that must save by UPI is reported by year (M3)
  pilot cash   recovery fees arrive ~18 months after a loan, so they are left out of the pilot year (M4)

Writes tables/xs_inputs_v2.csv, xs_money_v2.csv, xs_npv_v2.csv, xs_breakeven_v2.csv, xs_oneway_v2.csv,
pilot_rules_v2.csv, plus the page tables xs_years_v2.csv, xs_benchmarks_v2.csv, xs_other_build_v2.csv,
xs_paytm_v2.csv, xs_changes_v2.csv.
"""
import csv
import math
from dataclasses import dataclass, replace, fields
from pathlib import Path

import agent_npv as N
import marketplace as M
from build_agent_slides import inr

ROOT = Path(__file__).resolve().parent.parent
T, R = ROOT / "tables", ROOT / "research"
PAY_SAL, PAY_BAL, PAY_COL = "salary only", "salary + 0.5% a year of balance", "salary + 1% of collections"
PAYS = (PAY_SAL, PAY_BAL, PAY_COL)
R12S = (0.30, 0.40, 0.55, 0.70)
TORNADO_R12 = 0.40          # top of the operator's bear case (30-40 of 100)
DSA_PL = 0.0175             # middle of the 1-2.5% personal-loan DSA payout (XL-13)
ONLINE_CAC = 499.2394       # tables/distributions.csv cac_target@ng mode (as model/story_unit.py)
STORY = {r["channel"]: r for r in csv.DictReader((T / "story_unit.csv").open())}
ONLINE_R12 = float(STORY["online"]["still_saving_m12"])
assert abs(float(STORY["online"]["cost_to_win"]) - ONLINE_CAC) < 1e-6


@dataclass(frozen=True)
class P:
    signups: float = 1000.0
    daily: float = 350.0
    days: float = 20.0
    trail: float = N.TRAIL
    salary: float = N.PAY_M
    apply: float = M.CASES["middle"][0]
    eligible: float = M.CASES["middle"][1]
    approved: float = M.CASES["middle"][2]
    ticket: float = M.TICKET
    fee: float = 1.5 * DSA_PL
    taken_back: float = M.CASES["middle"][4]
    npa: float = M.CASES["middle"][5]
    recovered: float = M.CASES["middle"][6]
    rec_fee: float = M.CASES["middle"][7]
    card_share: float = 0.05
    card_fee: float = M.CASES["middle"][9]
    other: float = M.CASES["middle"][8]
    proven_after: int = 6
    balance_mode: str = "cycle"      # "cycle" (v2 fix round 1) or "flat" (agent_npv.run: half a year's deposits from month 1)
    other_start: str = "proven"      # "proven" (from month 7) or "all" (every active saver from month 1, as marketplace.py)
    capacity: float = 400.0          # cash visits one agent can make a day
    every: float = 2.5               # days between visits to a cash saver


BASE = P()
ROUND0 = replace(BASE, balance_mode="flat", other_start="all")     # v2 as first built (before fix round 1)


def held(k, p):
    """Balance in saver-month k (1-based) as a multiple of one month's deposits."""
    return (((k - 1) % 12) + 0.5) if p.balance_mode == "cycle" else 6.0


def savings_only(p):
    return replace(p, apply=0.0, card_share=0.0, other=0.0)
LOW_COLL = dict(npa=M.CASES["low"][5], recovered=M.CASES["low"][6], rec_fee=M.CASES["low"][7])
HIGH_COLL = dict(npa=M.CASES["high"][5], recovered=M.CASES["high"][6], rec_fee=M.CASES["high"][7])


def fee_per_loan(p):
    return p.ticket * p.fee * (1 - p.taken_back)


def coll_per_loan(p):
    return p.ticket * p.npa * M.OWED_AT_DEFAULT * p.recovered * p.rec_fee * M.COLLECT_LAG


def loans_rate(p):
    return p.apply * p.eligible * p.approved


PRODUCTS = ("fund", "origination", "collections", "cards", "other")
NICE = {"fund": "Fund commission on his savings", "origination": "Loan origination fees", "collections": "Fees on recovered bad loans",
        "cards": "Credit cards", "other": "Insurance and other products"}


def simulate(r12, months, pay=PAY_SAL, p=BASE, card_mode="proven"):
    """One agent, month by month. Returns rows of undiscounted money plus the discount factor.
    card_mode 'proven' (v2): card_share of savers still saving at month 7 get a card that month;
    'signup' (old marketplace.py / agent_npv.py): card_share of sign-ups, in the month they join."""
    rate, base = N.PAYS[pay]
    c = 1 - r12 ** (1 / 12)
    su_m, save_m = p.signups / 12, p.daily * p.days
    out = []
    for t in range(months):
        active = proven = newly = bal = 0.0
        for m in range(t + 1):
            k = t - m + 1
            n = su_m * (1 - c) ** (k - 1)
            active += n
            if k > p.proven_after:
                proven += n
            if k == p.proven_after + 1:
                newly += n
            bal += n * save_m * held(k, p)
        comm = 0.0 if base is None else (rate / 12 * bal if base == "balance" else rate * active * save_m)
        loans = proven / 12 * loans_rate(p)
        cards = (newly if card_mode == "proven" else su_m) * p.card_share * p.card_fee
        out.append({"month": t + 1, "disc": (1 + N.DISC_M) ** (t + 1), "signups": su_m, "active": active, "proven": proven,
                    "new_proven": newly, "loans": loans, "cost": p.salary + comm, "commission": comm,
                    "fund": bal * p.trail / 12, "origination": loans * fee_per_loan(p), "collections": loans * coll_per_loan(p),
                    "cards": cards, "other": (proven if p.other_start == "proven" else active) * p.other / 12,
                    "cash_visits_a_day": active / p.every, "upi_share_needed": max(0.0, 1 - p.capacity * p.every / active) if active else 0.0})
    return out


def npv(r12, months, pay=PAY_SAL, p=BASE, card_mode="proven"):
    rows = simulate(r12, months, pay, p, card_mode)
    pv = {k: sum(r[k] / r["disc"] for r in rows) for k in PRODUCTS + ("cost", "signups")}
    income = sum(pv[k] for k in PRODUCTS)
    return {"npv": income - pv["cost"], "pv_income": income, "pv_cost": pv["cost"], **{f"pv_{k}": pv[k] for k in PRODUCTS},
            "pv_signups": pv["signups"], "savers_end": rows[-1]["active"], "proven_end": rows[-1]["proven"]}


def breakeven(months, pay=PAY_SAL, p=BASE, card_mode="proven", f=None):
    f = f or (lambda r: npv(r, months, pay, p, card_mode)["npv"])
    lo, hi = 0.01, 0.99
    if f(hi) < 0:
        return None
    if f(lo) >= 0:
        return lo
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) < 0 else (lo, m)
    return hi


def cohort(r12, months=60, p=BASE, condition_proven=False):
    """One customer won: his own first `months` months, each product discounted to the month he joins.
    condition_proven: the same for a saver known to be still saving at month 7 (a proven saver)."""
    c = 1 - r12 ** (1 / 12)
    save_m = p.daily * p.days
    v = dict.fromkeys(PRODUCTS, 0.0)
    s7 = (1 - c) ** p.proven_after
    for k in range(1, months + 1):
        s = (1 - c) ** (k - 1)
        if condition_proven:
            s = 1.0 if k <= p.proven_after else s / s7
        d = (1 + N.DISC_M) ** (k - 1)
        v["fund"] += s * save_m * held(k, p) * p.trail / 12 / d
        if p.other_start == "all" or k > p.proven_after:
            v["other"] += s * p.other / 12 / d
        if k > p.proven_after:
            lr = s * loans_rate(p) / 12
            v["origination"] += lr * fee_per_loan(p) / d
            v["collections"] += lr * coll_per_loan(p) / d
        if k == p.proven_after + 1:
            v["cards"] += s * p.card_share * p.card_fee / d
    v["total"] = sum(v[k] for k in PRODUCTS)
    return v


def pilot_year(r12, p=BASE):
    """The pilot's 12 months in cash (not discounted): what his savers bring in less his salary."""
    rows = simulate(r12, 12, PAY_SAL, p)
    inc = {k: sum(r[k] for r in rows) for k in PRODUCTS}
    cash = {k: v for k, v in inc.items() if k != "collections"}      # M4: recovery fees arrive ~18 months after the loan
    cost = sum(r["cost"] for r in rows)
    return {"income": sum(cash.values()), "cost": cost, "result": sum(cash.values()) - cost, **inc,
            "result_with_recoveries": sum(inc.values()) - cost,
            "signups": sum(r["signups"] for r in rows), "active_end": rows[-1]["active"], "proven_end": rows[-1]["proven"],
            "loans": sum(r["loans"] for r in rows), "applications": sum(r["proven"] / 12 * p.apply for r in rows),
            "cards_given": sum(r["new_proven"] for r in rows) * p.card_share, "cash_visits_a_day_end": rows[-1]["cash_visits_a_day"]}


# ---------- reconciliation with the two models this builds on ----------
def reconcile():
    for months in (36, 60):
        for pay in PAYS:
            for r in R12S:
                a, b = N.run(r, months, pay), npv(r, months, pay, ROUND0)
                assert abs(a["pv_cost"] - b["pv_cost"]) < 1e-6 and abs(a["pv_revenue"] - b["pv_fund"]) < 1e-6, (months, pay, r)
        for pay in (PAY_SAL, PAY_BAL):
            for r in R12S:
                m, b = M.npv(r, months, pay, "middle"), npv(r, months, pay, replace(ROUND0, fee=0.02), card_mode="signup")
                for k in ("other_products", "loan_origination", "loan_collections", "cards"):
                    mine = {"other_products": "pv_other", "loan_origination": "pv_origination", "loan_collections": "pv_collections", "cards": "pv_cards"}[k]
                    assert abs(m[f"pv_{k}"] - b[mine]) < 1e-6, (k, months, pay, r)
    sens = {(r["fee"], r["years"], r["pay"]): r for r in csv.DictReader((T / "mkt_fee_sensitivity.csv").open())}
    old = sens[("0.02625", "5", PAY_SAL)]
    assert abs(breakeven(60, p=ROUND0, card_mode="signup") - float(old["breakeven_r12"])) < 1e-4
    assert abs(fee_per_loan(BASE) - float(old["fee_per_loan_after_takeback"])) < 1e-6
    # M1: a saver who stays a full term earns the fund the same Rs 147 as the old flat balance (within rounding)
    full = sum(BASE.daily * BASE.days * held(k, BASE) * BASE.trail / 12 for k in range(1, 13))
    assert abs(full - BASE.daily * BASE.days * 6 * BASE.trail) < 0.01, full
    for r in R12S:
        assert abs(N.run(r, 60, PAY_SAL)["npv"] - npv(r, 60, PAY_SAL, savings_only(ROUND0))["npv"]) < 1e-6
    return float(old["breakeven_r12"]), float(sens[("0.02625", "3", PAY_SAL)]["breakeven_r12"])


# ---------- evidence: every hand-entered benchmark must be in research/ ----------
def ev(id_, token):
    for path in R.glob("*.csv"):
        for row in csv.reader(path.open()):
            if row and row[0] == id_:
                assert token in ",".join(row), f"{id_}: '{token}' not found"
                return
    raise KeyError(id_)


BENCH = [  # (group, who, low %, high %, ids, token to check, note)
    ("referral", "DSA, banks", 0.5, 1.5, "LEV-009", "0.5-1.5 (banks)", "one-off, no servicing"),
    ("referral", "DSA, NBFC and fintech lenders", 1.0, 3.0, "LEV-009", "1-3 (NBFC/fintech lenders)", "one-off, no servicing"),
    ("referral", "DSA, personal loans (typical)", 1.0, 2.5, "XL-13", "1-2.5 (typical)", "can be taken back within 6 months"),
    ("marketplace", "Paisabazaar, at most", 4.6, 4.7, "XL-09, LEV-065", "4.6 (upper bound)", "includes card fees, so the loan-only fee is lower"),
    ("full service", "Paytm, merchant loans, no first-loss cover", 4.5, 5.0, "XL-07", "4.5-5 (no DLG)", "sources and collects over the loan's life"),
    ("full service", "Moneyview, with first-loss cover", 11.0, 11.0, "LEV-061", "~11 gross", "gross, carries first losses"),
]
for _g, _w, _lo, _hi, _ids, _tok, _n in BENCH:
    ev(_ids.split(",")[0].strip(), _tok)
ev("LEV-065", "<= 4.7")

OTHER_BUILD = [  # product, low, middle, high Rs per active saver a year (research/xs_other_summary.md table), evidence ids
    ("Accident, hospital cash, small health", 0.6, 7.2, 45.0, "XO-19, XO-09, XO-10"),
    ("Term life (small cover)", 0.4, 7.5, 36.0, "XO-20, XO-32"),
    ("Two-wheeler insurance", 0.9, 7.1, 33.2, "XO-18, XO-21, XO-22"),
    ("Mobile insurance", 0.2, 2.3, 9.4, "XO-34, XO-19"),
    ("NPS / NPS Lite", 0.3, 6.0, 10.0, "XO-16, XO-17"),
    ("Mobile recharge", 2.6, 13.0, 39.0, "XO-25, XO-33"),
    ("Bill payments", 1.2, 12.0, 54.0, "XO-26"),
    ("Equity SIP trail", 0.4, 2.3, 10.8, "XO-08, XO-06, XO-07"),
    ("Choti SIP incentive", 1.7, 5.6, 18.0, "XO-01, XO-04, XO-05"),
    ("Government schemes (PMJJBY, PMSBY, APY)", 0.0, 0.0, 4.0, "XO-12 to XO-15"),
]
EVIDENCE = [  # key, what the page says (plain words), ids, token that must appear in the first id's research row
    ("card_fee_bm", "₹500–2,000 is typical per approved card", "BM-08", "500-2,000 typical"),
    ("card_fee_gromo", "GroMo pays its sub-agents ₹1,000–2,400 per approved card", "XL-20", "1,000-2,400"),
    ("card_unsecured", "Unsecured cards need salaried or ITR income and a bureau score", "XL-20", "salaried/ITR income"),
    ("card_pb", "Paisabazaar issued 91,000 cards in one quarter (Apr–Jun 2026)", "XL-08", "91,000 credit cards"),
    ("card_india", "Only 3% of Indians hold a credit card; new cards fell 28% in a year", "XL-40", "3% of the population"),
    ("card_issuer", "The issuer decides who gets a card; we may only source it", "REG-087", "sourcing only"),
    ("card_fd", "An FD-secured card needs an FD at the issuing bank; our fund is not one", "REG-029, XL-54, TB-35", "must come from the bank holding the FD"),
    ("card_fd_payout", "No published payout for FD-secured cards, and no count of them", "TB-35, BM-08", "not published"),
    ("card_no_dlg", "No first-loss cover is allowed on credit cards", "REG-007", "credit cards"),
    ("ins_phonepe", "PhonePe earns ₹8 of insurance revenue per active user a year", "XO-10", "8.1"),
    ("ins_xo38", "Savers buy more than the average UPI user, so 2–3× PhonePe is defensible; 9× is not", "XO-38", "2-3x PhonePe"),
    ("ins_draft", "IRDAI draft caps: comments close 25 Oct 2026; not yet law", "REG-053", "2026-10-25"),
    ("ins_health", "Health and accident, first sale: 15%; health renewals: 5%", "REG-054, XO-19", "first-time 15% for IDEs"),
    ("ins_motor", "Third-party motor: nil to 2.5%", "XO-18", "Motor TP: new vehicle Nil / 2.5%"),
    ("ins_term", "Term life: 7.5–25% in the first year", "XO-20", "Pure term: single premium 7.5%"),
    ("ins_ide", "A distributor licence (IDE) needs ₹10 lakh of capital", "REG-057", "initial capital Rs 10 lakh"),
    ("ins_ca", "A corporate agent selling only insurance needs ₹50 lakh net worth", "REG-059", "Rs 50 lakh"),
    ("lend_pays", "The lender pays our fee; the borrower pays us nothing", "XL-01", "paid directly by the RE"),
    ("lend_offers", "With several lenders we must show every matching offer and push none", "XL-46", "ALL matching offers"),
    ("lend_kissht_ever", "Kissht: 17.5% of registered users ever borrowed", "XL-42", "17.5% of registered users"),
    ("lend_brazil", "Brazil payroll loans: 20% of eligible workers borrowed in year one", "LS-06", "20.2"),
    ("lend_paytm_users", "Paytm: under 1% of monthly users take a financial product in a quarter", "XL-04", "0.93"),
    ("lend_active", "41% of small-business borrowers already have an active loan", "XB-09", "41%"),
    ("lend_50pct", "Repayments are capped at 50% of income for households up to ₹3 lakh a year", "XL-34", "50% of monthly household income"),
    ("lend_income", "His customers earn ₹20,000–40,000 a month", "IV-04", "20,000 to 40,000"),
    ("lend_kissht_appr", "Kissht approves 11% of new applicants and 74% of repeat ones", "XL-41", "11.20%"),
    ("lend_npa", "CRIF: loans over ₹50,000 peak at 3.6% going 90+ days bad", "MAC-03", ">Rs 50K 3.6%"),
    ("lend_recovered", "Paytm-sourced loans: 30–35% recovered after 90+ days", "XB-07", "30% to 35%"),
    ("lend_takeback", "DSA fees can be taken back if a loan closes or goes bad within 6 months", "XL-47", "within 6 months"),
    ("lend_paytm_ticket", "Paytm's average merchant loan: ₹2.05 lakh", "XB-08", "205000"),
    ("lend_bachatt", "Bachatt's partners lend up to ₹5 lakh", "XL-12", "up to Rs 5 lakh"),
    ("lend_dlg", "RBI caps a lending partner's first-loss cover at 5% of loans", "SE-04", "first-loss cover"),
    ("lend_rate_cap", "RBI draft: rate ceilings on loans up to ₹50,000 from April 2027", "REG-078", "Rs 50,000"),
    ("fund_trail", "Debt-fund distributor commission: 0.2–0.5% a year", "XB-04", "0.2-0.5"),
    ("other_total", "Insurance and other products: ₹8 / ₹63 / ₹259 a saver a year", "XO-39", "8 / 63 / 259"),
]
for _k, _t, _ids, _tok in EVIDENCE:
    ev(_ids.split(",")[0].strip(), _tok)

CHECKS = [  # key, value, unit, ids, token: numbers the appendix draws, each checked against its research row
    ("card_fee_typical_low", 500.0, "Rs a card", "BM-08", "500-2,000 typical"),
    ("card_fee_typical_high", 2000.0, "Rs a card", "BM-08", "500-2,000 typical"),
    ("card_fee_gromo_low", 1000.0, "Rs a card", "XL-20", "1,000-2,400"),
    ("card_fee_gromo_high", 2400.0, "Rs a card", "XL-20", "1,000-2,400"),
    ("phonepe_insurance_per_user", 8.1, "Rs a user a year", "XO-10", "8.1 (derived = 191 cr / 23.7 cr MAU)"),
    ("phonepe_deposit_min", 100.0, "Rs a day", "QM-33", "phonepe_daily_rd_min_rs,100"),
    ("dlg_cap", 0.05, "share of loans", "SE-04", "dlg_cap_pct,5"),
]
for _k, _v, _u, _ids, _tok in CHECKS:
    ev(_ids, _tok)


# ---------- the inputs table ----------
def inputs_rows():
    """Status rule (fix round 1): blog or affiliate sources = unverified; company filings or regulators = evidence;
    our arithmetic = derived; our call = judgement; the operator's figure = operator."""
    fl = lambda p: fee_per_loan(p)
    rows = [
        # key, name, low, middle, high, unit, sources, status, note
        ("agent_pay", "Agent's salary", 15000, N.PAY_M, 25000, "Rs a month", "operator; IV-13", "operator",
         "₹20,000 is yours; ₹15,000–25,000 is the janta agent's pay. Stress pays: + 0.5% of balance, + 1% of collections"),
        ("signups", "Sign-ups per agent a year", 750, 1000, 1250, "sign-ups a year", "operator", "operator", "1,000 is yours; ±25% is our range"),
        ("r12", "Still saving after a year", 0.30, 0.55, 0.70, "share", "operator (30–70)", "judgement",
         "55 is ours: between the bear case (30–40) and one janta agent's book (72); same drop-off every month"),
        ("daily", "Daily amount a saver puts in", 200, 350, 500, "Rs a day", "operator; IV-03", "operator", "₹350 is yours; ₹200–500 from the interview"),
        ("days", "Deposit days a month", 20, 20, 20, "days", "none", "judgement", "240 deposit days a year; no source"),
        ("balance", "Money held in his fund", 3500, 42000, 80500, "Rs per saver", "derived", "derived",
         "Yearly terms: builds by ₹7,000 a month, paid out at each term's end; ₹42,000 on average"),
        ("trail", "Fund commission a year, on the balance", 0.002, 0.0035, 0.005, "share a year", "XB-04", "unverified", "Debt-fund distributor commission (AMC and adviser blogs)"),
        ("proven_after", "Months of saving before he is offered products", 6, 6, 6, "months", "operator", "operator",
         "From month 7 he is a proven saver: loans, cards, insurance and more"),
        ("visit_every", "Days between visits to a cash saver", 2, 2.5, 3, "days", "operator", "operator", "Every 2–3 days"),
        ("capacity", "Cash visits one agent can make a day", 400, 400, 400, "visits a day", "IV-01; agent_3yr.py", "judgement",
         "Top of a 200–400 janta book; 400 a day at every 2.5 days = 1,000 savers on cash"),
        ("apply", "Proven savers who apply for a loan in a year", 0.10, 0.20, 0.35, "share a year", "XL-42, LS-06, XL-04", "judgement",
         "Kissht 17.5% ever borrowed; Brazil 20% in year one; founder 35%"),
        ("eligible", "Applicants who can carry a ₹2.5 lakh EMI", 0.30, 0.50, 0.70, "share", "XB-09, IV-04, XL-34", "judgement",
         "₹10,073 EMI needs ₹20,145+ income at the 50% rule; customers earn ₹20–40k"),
        ("approved", "Eligible applicants a lender approves", 0.25, 0.35, 0.50, "share", "XL-41; founder", "judgement",
         "Several lenders; one lender gave the founder 25%; Kissht approves 11% new, 74% repeat"),
        ("loans_per_100", "Loans per 100 proven savers a year", 100 * 0.10 * 0.30 * 0.25, 100 * loans_rate(BASE), 100 * 0.35 * 0.70 * 0.50, "loans",
         "derived", "derived", "Apply × eligible × approved"),
        ("ticket", "Loan size", 100000, M.TICKET, 300000, "Rs", "operator; XB-08, XL-12", "operator",
         "₹2.5 lakh is yours; range is our judgement (Paytm average ₹2.05 lakh)"),
        ("fee", "Origination fee, paid by the lender", 0.02, BASE.fee, 0.03, "share of the loan", "operator; XL-13, LEV-009, BM-07", "operator",
         "1.5 × a DSA's 1.75% (the middle of blog-reported 1–2.5%); range 2% and 1.5 × 2%"),
        ("taken_back", "Fees taken back (loan closed or bad in 6 months)", 0.05, 0.025, 0.0, "share of fees", "XL-13, XL-47", "unverified", "DSA platform blogs"),
        ("fee_per_loan", "What one loan earns us", fl(replace(BASE, fee=0.02, taken_back=0.05)), fl(BASE), fl(replace(BASE, fee=0.03, taken_back=0.0)), "Rs a loan",
         "derived", "derived", "Loan size × fee × (1 − taken back)"),
        ("npa", "Loans that go 90+ days bad", M.CASES["low"][5], BASE.npa, M.CASES["high"][5], "share of loans", "MAC-03", "judgement",
         "CRIF: 3.6% peak for loans over ₹50,000; 5% is ours"),
        ("owed", "Owed when a loan goes bad", M.OWED_AT_DEFAULT, M.OWED_AT_DEFAULT, M.OWED_AT_DEFAULT, "share of the loan", "none", "judgement", "Half the loan"),
        ("recovered", "Recovered of what is owed", M.CASES["low"][6], BASE.recovered, M.CASES["high"][6], "share", "XB-07", "evidence", "Paytm's results: 30–35%"),
        ("rec_fee", "Our fee on what is recovered", M.CASES["low"][7], BASE.rec_fee, M.CASES["high"][7], "share", "NABARD tender (no id)", "unverified",
         "Paid about 18 months after the loan, so not in the pilot year"),
        ("coll_per_loan", "Recovery fees, per loan made", coll_per_loan(replace(BASE, **LOW_COLL)), coll_per_loan(BASE), coll_per_loan(replace(BASE, **HIGH_COLL)),
         "Rs a loan", "derived", "derived", "An average over all loans; small: about 2% of the origination fee"),
        ("card_share", "Proven savers who get a card (once, month 7)", 0.005, BASE.card_share, BASE.card_share, "share", "operator; XL-54", "operator",
         "5% is yours and the top of XL-54's 0.5–5% band for FD-secured cards, which is itself assumed"),
        ("card_fee", "Fee per approved card", 500, BASE.card_fee, 2000, "Rs a card", "BM-08, XL-20", "unverified",
         "Affiliate guides for unsecured cards, which need income proof"),
        ("card_fee_fd", "Fee per FD-secured card (one-way test only)", 300, 750, 1500, "Rs a card", "XL-54", "judgement",
         "Assumed in XL-54; no published payout (TB-35)"),
        ("other", "Insurance and other products, from month 7", 8, BASE.other, 259, "Rs a saver a year", "XO-39, XO-10", "judgement",
         "Proven savers only; take-ups are ours; PhonePe earns ₹8 a user on insurance"),
        ("discount", "Discount rate", 0.20, 0.20, 0.20, "a year", "tables/inputs.csv", "judgement", "Applied monthly"),
        ("online_cac", "Online cost to win a saver", 186, ONLINE_CAC, 1340, "Rs a saver", "TB-18..22, NG-043", "judgement",
         "App signals × 1.1 for shopkeepers: no firm publishes it"),
        ("online_r12", "Online: still saving after a year", ONLINE_R12, ONLINE_R12, ONLINE_R12, "share", "tables/story_unit.csv", "derived", "Our evidence curve"),
    ]
    return rows


NICE_ONEWAY = [  # key, plain name, low value, high value
    ("approved", "Lender approves (25% → 50%)", dict(approved=0.25), dict(approved=0.50)),
    ("fee", "Origination fee (2% → 3%)", dict(fee=0.02), dict(fee=0.03)),
    ("apply", "Proven savers who apply (10% → 35%)", dict(apply=0.10), dict(apply=0.35)),
    ("eligible", "Applicants eligible (30% → 70%)", dict(eligible=0.30), dict(eligible=0.70)),
    ("ticket", "Loan size (₹1 lakh → ₹3 lakh)", dict(ticket=100000.0), dict(ticket=300000.0)),
    ("card_share", "Proven savers who get a card (0.5% → 5%)", dict(card_share=0.005), dict(card_share=0.05)),
    ("card_fee", "Fee per card (₹500 → ₹2,000)", dict(card_fee=500.0), dict(card_fee=2000.0)),
    ("card_fee_fd", "FD-secured card fee (₹300 → ₹1,500)", dict(card_fee=300.0), dict(card_fee=1500.0)),
    ("other", "Insurance and other products (₹8 → ₹259)", dict(other=8.0), dict(other=259.0)),
    ("signups", "Sign-ups a year (750 → 1,250)", dict(signups=750.0), dict(signups=1250.0)),
    ("salary", "Agent's salary (₹15,000 → ₹25,000)", dict(salary=15000.0), dict(salary=25000.0)),
    ("trail", "Fund commission (0.20% → 0.50%)", dict(trail=0.002), dict(trail=0.005)),
    ("daily", "Daily amount (₹200 → ₹500)", dict(daily=200.0), dict(daily=500.0)),
    ("taken_back", "Fees taken back (5% → 0%)", dict(taken_back=0.05), dict(taken_back=0.0)),
    ("collections", "Recovery fees (₹51 → ₹349 a loan)", LOW_COLL, HIGH_COLL),
]


def lk(x):
    return ("−" if x < 0 else "+") + f"₹{abs(x) / 1e5:.2f}"


def write(name, rows):
    with (T / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def be_or_text(b):
    return b if b is not None else "not reachable"


def main():
    old_be5, old_be3 = reconcile()
    # 1. inputs
    write("xs_inputs_v2.csv", [dict(zip(("key", "name in plain words", "low", "middle", "high", "unit", "source_ids", "status", "note"), r))
                               for r in inputs_rows()])

    # 2. money by product
    per100 = {"fund": 100 * BASE.daily * BASE.days * 6 * BASE.trail, "origination": 100 * loans_rate(BASE) * fee_per_loan(BASE),
              "collections": 100 * loans_rate(BASE) * coll_per_loan(BASE), "cards": 100 * BASE.card_share * BASE.card_fee, "other": 100 * BASE.other}
    kind = {"fund": "yearly", "origination": "yearly", "collections": "yearly", "cards": "once", "other": "yearly"}
    co = {r: cohort(r) for r in R12S}
    cp = {r: cohort(r, condition_proven=True) for r in R12S}
    onl = cohort(ONLINE_R12)
    money = []
    for k in PRODUCTS + ("total",):
        row = {"product": k, "name": NICE.get(k, "Total"), "kind": kind.get(k, ""),
               "a_year_per_100_proven": per100[k] if k != "total" else sum(per100.values()),
               "a_year_per_proven_saver": (per100[k] if k != "total" else sum(per100.values())) / 100,
               "basis_per_100_proven": {"fund": "100 x 0.35% x Rs 42,000 (average over a term)", "origination": "3.5 loans x Rs 6,398",
                                        "collections": "3.5 loans x Rs 155", "cards": "5 cards x Rs 1,250, once, in month 7", "other": "100 x Rs 63",
                                        "total": "sum"}[k]}
        for r in R12S:
            row[f"pv5_per_customer_won_r{r}"] = co[r][k]
        for r in R12S:
            row[f"pv5_per_proven_saver_r{r}"] = cp[r][k]
        row["pv5_per_customer_online"] = onl[k]
        money.append(row)
    money.append({"product": "marketplace_yearly", "name": "Marketplace, every year (loans, recoveries, insurance and more)", "kind": "yearly",
                  "a_year_per_100_proven": sum(per100[k] for k in ("origination", "collections", "other")), "a_year_per_proven_saver": "",
                  "basis_per_100_proven": "origination + collections + other"})
    money.append({"product": "marketplace_once", "name": "Marketplace, once (cards)", "kind": "once", "a_year_per_100_proven": per100["cards"],
                  "a_year_per_proven_saver": "", "basis_per_100_proven": "cards"})
    money.append({"product": "cost_to_win_and_serve", "name": "Street: agent's salary per sign-up (wins and visits him)", "kind": "",
                  "a_year_per_100_proven": "", "a_year_per_proven_saver": "", "basis_per_100_proven": "Rs 20,000 x 12 / 1,000",
                  **{f"pv5_per_customer_won_r{r}": BASE.salary * 12 / BASE.signups for r in R12S}, **{f"pv5_per_proven_saver_r{r}": "" for r in R12S},
                  "pv5_per_customer_online": ONLINE_CAC})
    write("xs_money_v2.csv", money)

    # 3. NPV
    npvs = []
    for months in (36, 60):
        for pay in PAYS:
            for r in R12S:
                x = npv(r, months, pay)
                npvs.append({"years": months // 12, "pay": pay, "r12": r, "npv": x["npv"],
                             "npv_savings_only": npv(r, months, pay, savings_only(BASE))["npv"], "pv_cost": x["pv_cost"],
                             "pv_income": x["pv_income"], **{f"pv_{k}": x[f"pv_{k}"] for k in PRODUCTS}, "savers_end": x["savers_end"],
                             "proven_end": x["proven_end"], "npv_before_fix_round1": npv(r, months, pay, ROUND0)["npv"]})
    write("xs_npv_v2.csv", npvs)
    write("xs_npv_curve_v2.csv", [{"r12": i / 100, "npv3_salary": npv(i / 100, 36)["npv"], "npv5_salary": npv(i / 100, 60)["npv"]}
                                  for i in range(20, 76)])

    # 4. break-even
    be = []
    fees = (("2%", 0.02), ("2.625% (1.5 × a DSA)", BASE.fee), ("3% (1.5 × 2%)", 0.03))
    for months in (36, 60):
        for pay in PAYS:
            for fl, fv in fees:
                be.append({"years": months // 12, "pay": pay, "case": f"fee {fl}", "breakeven_r12": be_or_text(breakeven(months, pay, replace(BASE, fee=fv)))})
        for case, p in (("low funnel (10% x 30% x 25%)", replace(BASE, apply=0.10, eligible=0.30, approved=0.25)),
                        ("750 sign-ups a year", replace(BASE, signups=750.0)), ("savings only (no cross-sell)", savings_only(BASE))):
            be.append({"years": months // 12, "pay": PAY_SAL, "case": case, "breakeven_r12": be_or_text(breakeven(months, PAY_SAL, p))})
    cb = breakeven(60, f=lambda r: cohort(r)["total"] - BASE.salary * 12 / BASE.signups)
    be.append({"years": 5, "pay": PAY_SAL, "case": "one customer won, his own first 5 years (value = Rs 240)", "breakeven_r12": be_or_text(cb)})
    write("xs_breakeven_v2.csv", be)
    BE = {(r["years"], r["pay"], r["case"]): r["breakeven_r12"] for r in be}
    MID = "fee 2.625% (1.5 × a DSA)"
    be5, be3 = BE[(5, PAY_SAL, MID)], BE[(3, PAY_SAL, MID)]

    # 4b. what each fix-round-1 change does to the break-even, one at a time and combined
    takes = list(csv.DictReader((T / "npv_takes.csv").open()))
    tk = lambda y, r, col="npv_middle_mix": float(next(x for x in takes if x["years"] == str(y) and x["pay"] == PAY_SAL and x["r12"] == r)[col])
    steps = [("last", "Last deck: 1% fee, 2.5 loans per 100, cards on every sign-up", None, None),
             ("today_signup_cards", "Today's fee and funnel, cards still paid on every sign-up", ROUND0, "signup"),
             ("round0", "v2 as first built: cards only to proven savers, once, in month 7", ROUND0, "proven"),
             ("m1_alone", "M1 alone: the balance builds over each yearly term", replace(ROUND0, balance_mode="cycle"), "proven"),
             ("m2_alone", "M2 alone: insurance and other products from month 7, proven savers only", replace(ROUND0, other_start="proven"), "proven"),
             ("this_deck", "M1 + M2 together: this deck", BASE, "proven")]
    eff = []
    for key, lab, p, cm in steps:
        if p is None:
            b5, b3, n55 = tk(5, "break-even"), tk(3, "break-even"), tk(5, "0.55")
        else:
            b5, b3, n55 = breakeven(60, PAY_SAL, p, cm), breakeven(36, PAY_SAL, p, cm), npv(0.55, 60, PAY_SAL, p, cm)["npv"]
        eff.append({"step": key, "what": lab, "breakeven5": be_or_text(b5), "breakeven3": be_or_text(b3), "npv5_r0.55": n55})
    assert abs(eff[1]["breakeven5"] - old_be5) < 1e-4 and abs(eff[1]["breakeven3"] - old_be3) < 1e-4
    assert abs(eff[-1]["breakeven5"] - be5) < 1e-12
    write("xs_fix_effects_v2.csv", eff)
    EF = {e["step"]: e for e in eff}

    # 5. one-way swings (5-year NPV, salary only) at the bear-case top and the middle
    one = []
    for r12 in (TORNADO_R12, 0.55):
        base5 = npv(r12, 60)["npv"]
        for key, nice, lo, hi in NICE_ONEWAY:
            a, b = npv(r12, 60, p=replace(BASE, **lo))["npv"], npv(r12, 60, p=replace(BASE, **hi))["npv"]
            one.append({"r12": r12, "input": key, "name": nice, "npv5_at_low": a, "npv5_at_high": b, "npv5_base": base5, "swing": abs(b - a),
                        "low_turns_negative": min(a, b) < 0})
    one.sort(key=lambda x: (x["r12"], -x["swing"]))
    write("xs_oneway_v2.csv", one)

    # 6. year by year for one agent (undiscounted money, the discounted result, and the visit load)
    yrs = []
    for r in R12S:
        rows = simulate(r, 60)
        for y in range(5):
            part = rows[12 * y:12 * (y + 1)]
            inc = {k: sum(x[k] for x in part) for k in PRODUCTS}
            cost = sum(x["cost"] for x in part)
            yrs.append({"r12": r, "year": y + 1, "signups": sum(x["signups"] for x in part), "savers_end": part[-1]["active"],
                        "proven_end": part[-1]["proven"], "loans": sum(x["loans"] for x in part),
                        "cards_given": sum(x["new_proven"] for x in part) * BASE.card_share, **inc, "income": sum(inc.values()), "cost": cost,
                        "result": sum(inc.values()) - cost,
                        "pv_result": sum((sum(x[k] for k in PRODUCTS) - x["cost"]) / x["disc"] for x in part),
                        "cash_visits_a_day_end": part[-1]["cash_visits_a_day"], "upi_share_needed_end": part[-1]["upi_share_needed"]})
    write("xs_years_v2.csv", yrs)
    Y = {(x["r12"], x["year"]): x for x in yrs}

    # 7. pilot rules
    py = {r: pilot_year(r) for r in R12S}
    low_f = BE[(5, PAY_SAL, "low funnel (10% x 30% x 25%)")]
    up = lambda x: math.ceil(x * 100 - 1e-9)
    rules = [("five_year_breakeven_m12", be5, "xs_breakeven_v2.csv: 5 years, salary only, 2.625% fee"),
             ("five_year_breakeven_m3", be5 ** (3 / 12), "same steady monthly drop-off: R12^(3/12)"),
             ("five_year_breakeven_m6", be5 ** (6 / 12), "R12^(6/12)"),
             ("three_year_breakeven_m12", be3, "xs_breakeven_v2.csv: 3 years, salary only, 2.625% fee"),
             ("go_m3_of_100", up(be5 ** (3 / 12)), "go line at month 3, whole savers of 100, rounded up"),
             ("go_m6_of_100", up(be5 ** (6 / 12)), "go line at month 6, rounded up"),
             ("go_m12_of_100", up(be5), "go line at month 12 (5-year NPV positive), rounded up"),
             ("go_m12_3y_of_100", up(be3), "month-12 line for a 3-year payback, rounded up"),
             ("first_month_signups", BASE.signups / 12, "the savers the month-3 line is read on"),
             ("signups_plan_a_month", BASE.signups / 12, "1,000 a year"),
             ("signups_stop_a_month", math.ceil(750 / 12), "750 a year (low end of the range, judgement) = 62.5 a month, rounded up"),
             ("five_year_breakeven_at_750_signups", BE[(5, PAY_SAL, "750 sign-ups a year")], "xs_breakeven_v2.csv"),
             ("loans_per_100_proven_plan", 100 * loans_rate(BASE), "middle funnel 20% x 50% x 35%"),
             ("five_year_breakeven_low_funnel", be_or_text(low_f), "xs_breakeven_v2.csv"),
             ("rethink_loans_by_m12", 1, "rethink at 1 loan or none by month 12 (lead's rule)"),
             ("apply_rate_plan", BASE.apply, "share of proven savers applying in a year"),
             ("capacity_visits_a_day", BASE.capacity, "cash visits one agent can make a day"),
             ("cash_savers_one_agent", BASE.capacity * BASE.every, "400 a day x one visit every 2.5 days"),
             ("pilot_salary_12m", BASE.salary * 12, "Rs 20,000 a month")]
    for r in R12S:
        rules += [(f"pilot_year1_result_r{r}", py[r]["result"], "12 months in cash, not discounted; recovery fees and support costs not counted"),
                  (f"pilot_year1_income_r{r}", py[r]["income"], "what his savers bring in during the pilot (no recovery fees)"),
                  (f"pilot_year1_result_with_recoveries_r{r}", py[r]["result_with_recoveries"], "the same if recovery fees were counted (M4 effect)"),
                  (f"pilot_year1_loans_r{r}", py[r]["loans"], "loans made in months 7-12"),
                  (f"pilot_year1_applications_r{r}", py[r]["applications"], "loan applications in months 7-12"),
                  (f"pilot_year1_cards_r{r}", py[r]["cards_given"], "cards given in months 7-12"),
                  (f"pilot_year1_proven_end_r{r}", py[r]["proven_end"], "proven savers at month 12"),
                  (f"pilot_year1_savers_end_r{r}", py[r]["active_end"], "savers at month 12"),
                  (f"pilot_cash_visits_a_day_m12_r{r}", py[r]["cash_visits_a_day_end"], "if every saver is on cash"),
                  (f"upi_share_needed_end_y2_r{r}", Y[(r, 2)]["upi_share_needed_end"], "share of his book that must save by UPI at the end of year 2"),
                  (f"upi_share_needed_end_y5_r{r}", Y[(r, 5)]["upi_share_needed_end"], "the same at the end of year 5"),
                  (f"npv5_per_agent_r{r}", npv(r, 60)["npv"], "xs_npv_v2.csv"),
                  (f"npv3_per_agent_r{r}", npv(r, 36)["npv"], "xs_npv_v2.csv")]
    write("pilot_rules_v2.csv", [{"key": k, "value": v, "from": f} for k, v, f in rules])

    # 8. page tables: fee benchmarks, other-products build, Paytm comparison, what changed
    bench = [{"group": g, "who": w, "low_pct": lo, "high_pct": hi, "source_ids": ids, "note": n} for g, w, lo, hi, ids, _t, n in BENCH]
    bench.append({"group": "ours", "who": "Us: 1.5 × a DSA (range 2%–3%)", "low_pct": 2.0, "high_pct": 3.0, "source_ids": "operator; XL-13",
                  "note": f"middle {BASE.fee * 100:.3f}%"})
    write("xs_benchmarks_v2.csv", bench)
    ob = [{"product": a, "low": b, "middle": c, "high": d, "source_ids": e} for a, b, c, d, e in OTHER_BUILD]
    tot = {k: sum(x[k] for x in ob) for k in ("low", "middle", "high")}
    ob.append({"product": "Total (FD excluded: already in the fund line)", **tot, "source_ids": "XO-39"})
    ob.append({"product": "Model input (XO-39)", "low": 8.0, "middle": 63.0, "high": 259.0, "source_ids": "XO-39"})
    write("xs_other_build_v2.csv", ob)
    pt = {r["key"]: float(r["value"]) for r in csv.DictReader((T / "story_paytm.csv").open())}
    cac = BASE.salary * 12 / BASE.signups
    yearly_all_in = sum(per100[k] for k in ("fund", "origination", "collections", "other")) / 100
    write("xs_paytm_v2.csv", [
        {"key": "our_cost_to_win", "value": cac, "from": "Rs 20,000 x 12 / 1,000"},
        {"key": "paytm_cost_vs_ours", "value": pt["paytm_cost_to_win_upto"] / cac, "from": "story_paytm.csv / ours (Paytm's is an upper bound)"},
        {"key": "paytm_cost_vs_ours_about", "value": math.floor(pt["paytm_cost_to_win_upto"] / cac / 5) * 5, "from": "rounded down to a multiple of 5: 'about'"},
        {"key": "our_all_in_per_proven_saver_year", "value": yearly_all_in, "from": "fund + loan fees + recoveries + insurance and other, a year"},
        {"key": "our_card_once_per_proven_saver", "value": per100["cards"] / 100, "from": "5% x Rs 1,250, once"},
        {"key": "rent_vs_our_all_in", "value": pt["paytm_rent_a_year"] / yearly_all_in, "from": "Paytm device rent a year / our all-in a year"},
        {"key": "our_fee_per_loan", "value": fee_per_loan(BASE), "from": "2.625% of Rs 2.5 lakh, less 2.5% taken back"},
        {"key": "paytm_fee_vs_ours_low", "value": pt["paytm_fee_per_loan_low"] / fee_per_loan(BASE), "from": "ratio"},
        {"key": "paytm_fee_vs_ours_high", "value": pt["paytm_fee_per_loan_high"] / fee_per_loan(BASE), "from": "ratio"},
        {"key": "our_breakeven_r12_5y", "value": be5, "from": "xs_breakeven_v2.csv"},
    ])
    opr = {r["key"]: float(r["value"]) for r in csv.DictReader((T / "pilot_rules.csv").open())}
    old_bal = next(x for x in takes if x["years"] == "5" and x["pay"] == PAY_BAL and x["r12"] == "break-even")["npv_middle_mix"]
    p0 = {r: pilot_year(r, ROUND0) for r in (0.3, 0.7)}
    of = lambda b: f"{b * 100:.1f}" if isinstance(b, float) else b
    chg = [
        ("Origination fee per loan", "1% of ₹2.5 lakh: ₹2,438 kept", f"2.625% (1.5 × a DSA): {inr(fee_per_loan(BASE))} kept", "operator: 1.5 × a DSA"),
        ("Loans per 100 proven savers a year", "2.5 (one lender approves 25%)", f"{100 * loans_rate(BASE):.1f} (a marketplace approves 35%)", "several lenders"),
        ("Credit cards", "5% of sign-ups, ₹1,250, in the month he joins", "5% of proven savers, ₹1,250, once, in month 7", "a card is a lender product"),
        ("Recovery fees on bad loans", "not counted", f"{inr(coll_per_loan(BASE))} a loan on average", "the marketplace model's middle case"),
        ("M1: money in his fund", "₹42,000 from his first day", "builds ₹7,000 a month; paid out at each term's end; ₹42,000 on average",
         f"5-year bar alone: {of(EF['round0']['breakeven5'])} → {of(EF['m1_alone']['breakeven5'])}"),
        ("M2: insurance and other products", "every saver, from month 1", "proven savers only, from month 7",
         f"5-year bar alone: {of(EF['round0']['breakeven5'])} → {of(EF['m2_alone']['breakeven5'])}"),
        ("M3: one agent's capacity", "not checked", f"{BASE.capacity:.0f} cash visits a day; {Y[(0.55, 5)]['upi_share_needed_end'] * 100:.0f} of 100 on UPI by year 5 at 55 of 100",
         "no effect on NPV: a condition the pilot must test"),
        ("M4: recovery fees in the pilot year", "counted", "left out: they arrive about 18 months after a loan", "pilot year only"),
        ("M5: one-way tests", "13 rows", f"{len(NICE_ONEWAY)} rows: salary ₹15,000–25,000, FD-secured card fee ₹300–1,500, card share 0.5–5%", "no effect on the base"),
        ("0.5% of balance, 5-year break-even", "never, at a 1% fee" if old_bal == "not reachable" else f"{float(old_bal) * 100:.0f} of 100",
         f"{of(BE[(5, PAY_BAL, MID)])} of 100", "new fee, funnel, cards, M1, M2"),
        ("Pilot year, after what his savers bring in", f"{inr(opr['pilot_year1_result_r0.7'])} to {inr(opr['pilot_year1_result_r0.3'])}",
         f"{inr(py[0.7]['result'])} to {inr(py[0.3]['result'])}", f"first v2 build: {inr(p0[0.7]['result_with_recoveries'])} to {inr(p0[0.3]['result_with_recoveries'])}"),
        ("Stop lines at months 3 / 6", f"{opr['five_year_breakeven_m3'] * 100:.0f} / {opr['five_year_breakeven_m6'] * 100:.0f} of 100",
         f"{up(be5 ** 0.25)} / {up(be5 ** 0.5)} of 100", "follow the new month-12 bar (rounded up)"),
        ("Paytm earns more per loan", f"{pt['paytm_fee_vs_ours_low']:.1f}–{pt['paytm_fee_vs_ours_high']:.1f}×",
         f"{pt['paytm_fee_per_loan_low'] / fee_per_loan(BASE):.1f}–{pt['paytm_fee_per_loan_high'] / fee_per_loan(BASE):.1f}×", "against ₹6,398 kept"),
    ]
    write("xs_evidence_v2.csv", [{"key": k, "says": t, "source_ids": i} for k, t, i, _ in EVIDENCE])
    write("xs_checks_v2.csv", [{"key": k, "value": v, "unit": u, "source_ids": i} for k, v, u, i, _ in CHECKS])
    write("xs_changes_v2.csv", [{"what": a, "last deck": b, "this deck": c, "why": d} for a, b, c, d in chg])

    # ---------- print ----------
    print(f"fee per loan Rs {fee_per_loan(BASE):,.2f}; collections Rs {coll_per_loan(BASE):,.2f}; loans/100 proven {100 * loans_rate(BASE):.2f}")
    print("per 100 proven savers a year:", {k: round(v) for k, v in per100.items()}, "yearly marketplace",
          round(sum(per100[k] for k in ('origination', 'collections', 'other'))), "once", round(per100["cards"]))
    for e in eff:
        print(f"EFFECT {e['what']:<78} 5y {of(e['breakeven5'])} 3y {of(e['breakeven3'])} NPV5@55 {e['npv5_r0.55']:,.0f}")
    for b in be:
        v = b["breakeven_r12"]
        print(f"BE {b['years']}y {b['pay']:<32} {b['case']:<50} {v if isinstance(v, str) else f'{v:.1%}'}")
    for x in npvs:
        if x["pay"] == PAY_SAL or x["years"] == 5:
            print(f"NPV {x['years']}y {x['pay']:<32} R12 {x['r12']:.0%}: {x['npv']:>12,.0f} (savings only {x['npv_savings_only']:>12,.0f}; before fix {x['npv_before_fix_round1']:>12,.0f})")
    for r in R12S:
        print(f"customer won 5y R12 {r:.0%}: " + ", ".join(f"{k} {co[r][k]:.0f}" for k in PRODUCTS) + f" | total {co[r]['total']:.0f} vs cost 240")
    print("online customer 5y: " + ", ".join(f"{k} {onl[k]:.0f}" for k in PRODUCTS) + f" | total {onl['total']:.0f} vs CAC {ONLINE_CAC:.0f}")
    for r in R12S:
        print(f"pilot year R12 {r:.0%}: income {py[r]['income']:,.0f} cost {py[r]['cost']:,.0f} result {py[r]['result']:,.0f} (with recoveries "
              f"{py[r]['result_with_recoveries']:,.0f}) apps {py[r]['applications']:.1f} loans {py[r]['loans']:.1f} cards {py[r]['cards_given']:.1f} "
              f"savers {py[r]['active_end']:.0f} visits/day {py[r]['cash_visits_a_day_end']:.0f}")
    for x in yrs:
        print(f"Y r{x['r12']} y{x['year']} savers {x['savers_end']:,.0f} visits {x['cash_visits_a_day_end']:.0f} UPI needed {x['upi_share_needed_end']:.0%} result {x['result']:,.0f}")
    for o in one:
        print(f"oneway R12 {o['r12']:.0%} {o['name']:<46} {o['npv5_at_low']:>11,.0f} {o['npv5_at_high']:>11,.0f} (base {o['npv5_base']:,.0f})")
    for k, v, f in rules:
        print(f"rule {k:<40} {v}")


if __name__ == "__main__":
    main()

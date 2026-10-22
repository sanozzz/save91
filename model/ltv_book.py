"""SaveMore LTV/CAC workbook (operator 21 Oct 2026): "a separate google sheet for ltv to cac that we built, we should do monte carlo
on it and then project any number. Devil lies in the numbers and assumptions and so does god reside in the details."
Taps the same day: a NEW file ("SaveMore || LTVCAC"), the Monte Carlo as Python draws with a LIVE projector, online AND doorstep.

One saver won, months 1-96, rebuilt cell by cell from model/cohort_engine.py's age_profile -- the month-1 joiner that
online_plan.ltv_parts uses -- one row per month and one column per step; every input is a blue cell with its range and source.
Checked: model/toy_check.py's formula interpreter replays every formula and must match online_plan at the base AND at sample
Monte Carlo futures (tables/ltv_book_check.csv). The Monte Carlo is the SAME 1,000 futures as model/online_mc.py (same seed,
same draws), so each future's LTV/CAC sits next to that future's company profit month.

Usage: python model/ltv_book.py <payload_dir>
Writes tables/ltv_book_spec.json, ltv_mc_draws.csv, ltv_mc_summary.csv, ltv_one_at_a_time.csv, ltv_drivers.csv,
ltv_book_check.csv, ltv_inputs.csv, and the connector payloads into <payload_dir>."""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
import cohort_engine as ce  # noqa: E402
import online_mc as om  # noqa: E402
import online_plan as op  # noqa: E402
import toy_check as tc  # noqa: E402

T = ROOT / "tables"
SHEET_ID = "1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4"
R0, R1 = 5, 100                      # month 1 .. month 96 on Engine / Products / Saver
R60 = R0 + 59
M = 96
TABS = {"README": 0, "LTV-CAC": 1, "Projector": 2, "Inputs": 3, "Saver": 4, "Engine": 5, "Products": 6, "Monte Carlo": 7,
        "What moves it": 8, "Sources": 9}
NAVY, TEAL, AMBER, SLATE, GREY, BLUE = (0.06, 0.2, 0.36), (0.06, 0.62, 0.54), (0.85, 0.47, 0.04), (0.39, 0.45, 0.55), (0.45, 0.45, 0.45), (0, 0, 1)
DISTS = ce.load_dists()[0]
ALLSPEC = {**{k: tuple(DISTS[k][:4]) for k in ce.KEYS}, **{k: tuple(v[:4]) for k, v in om.ONLINE.items()}}
AGREED = {r["key"]: r for r in csv.DictReader((T / "dist_agreed_v1.csv").open())}
X0 = op.X0
DOOR_CAC = op.unit_rows_door_cac()


def neutral(text):
    text = str(text)
    for a, b in (("his shop or home", "the saver's shop or home"), ("each year he has repaid", "each year they have repaid"),
                 ("His next loan", "A saver's next loan"), ("his daily amount", "the daily amount"), ("his balance", "the balance"),
                 ("his original ticket", "the original ticket"), ("his loan", "the loan"), ("his savers", "the agent's savers"),
                 ("He ", "They "), (" he ", " they "), (" his ", " their "), (" him ", " them "), ("His ", "Their ")):
        text = text.replace(a, b)
    assert not re.search(r"\b(he|his|him|she|her|hers)\b", text, re.I), text
    return text


CLEAN = [("37% is the 5-year break-even on the last deck's inputs", "37% was the earlier street model's 5-year break-even"),
         ("an existing janta book", "an agent's existing book"), (" (an existing book)", ""), ("(OWN-02) (OWN-02)", "(OWN-02)"),
         ("(our guess) (judgement)", "(our judgement)"), (" (agent3_survival)", ""), (" (story_unit)", ""), (" (xs_breakeven_v2)", ""), (" (distributions.csv)", ""), (" (xs_inputs_v2)", ""),
         ("last deck needed 37%", "the earlier street model needed 37%"), ("last deck", "the earlier street model"),
         ("37% is the 5-year break-even on the earlier street model's inputs", "37% was the earlier street model's 5-year break-even"),
         ("your bear case 30–40% (operator)", "the operator's bear case 30–40%"), ("your first figure 5% (operator)", "the operator's first figure 5%"),
         ("the evidence value you agreed", "the agreed evidence value"), ("Engine default (cohort_engine.PRODUCTS).", "Our assumption; no outside source yet."),
         ("Company model (online_plan.py)", "Company model"), (" (saver_inputs)", ""), ("(research/xs_funnel_2026-10-21.csv)", "(loan research, XF rows on Sources)"),
         ("renewals pay two_wheeler_comm (the same rate)", "renewals pay the same commission"), ("approval_growth", "approval growth"),
         ("a janta book", "an agent's existing book"), ("janta book", "agent's existing book"), ("(judgement)", "(our judgement)")]


PLAIN = [("Bachatt conversation", "Conversation with a daily-savings app"), ("Bachatt minimum", "a daily-savings app's minimum"),
         ("Bachatt film", "that app's film"), ("Bachatt's partners", "a daily-savings app's partners"), ("Bachatt homepage", "A daily-savings app's homepage"),
         ("Bachatt acts", "The app acts"), ("Bachatt", "a daily-savings app"),
         ("Operator, 21 Oct", "Founder's judgement, 21 Oct"), ("operator:", "founder:"), ("the operator's", "the founder's"), ("by the operator", "by the founder"),
         ("the operator named", "the founder named"),
         ("the earlier street model 0%; earlier model 0–20%", "earlier versions of our plan: 0% and 0–20%"),
         ("37% was the earlier street model's 5-year break-even", "37% was the 5-year break-even in an earlier version of our plan"),
         ("half the earlier model's provisional 0–20% range", "half the provisional 0–20% range in an earlier version of our plan"),
         ("the earlier street model", "an earlier version of our plan"), ("the earlier model", "an earlier version of our plan"), ("earlier model", "an earlier version of our plan"),
         ("Engine rule", "Model rule"), ("Engine cap", "Model cap"), ("Engine convention", "Model convention"),
         ("Company model", "Our business-plan model"), ("the company model", "our business-plan model"), ("the pool's history", "the business's track record")]


def plain(text):
    """Investor wording: no internal shorthand, the competitor unnamed, ₹ not Rs (the deck applies the same list)."""
    text = str(text)
    for a, b in PLAIN:
        text = text.replace(a, b)
    text = re.sub(r"\bRs\.?\s?(?=\d)", "₹", text)          # Rs 250 → ₹250
    return re.sub(r"\bRs\b\.?", "₹", text)                   # Rs premium a year → ₹ premium a year


def clean(text):
    for a, b in CLEAN:
        text = text.replace(a, b)
    assert not re.search(r"[a-z]+_[a-z]+\b|\.py\b|\.csv\b", re.sub(r"\b[id]_[a-z0-9_]+\b", "", text)), text
    return text


def scrub(text):
    """Research text for the Sources tab: gender-neutral and grammatical."""
    text = str(text)
    for a, b in ((" he is ", " they are "), (" he has ", " they have "), (" he treats ", " they treat "), (" he can ", " they can "),
                 ("He is ", "They are "), ("He has ", "They have ")):
        text = text.replace(a, b)
    text = re.sub(r"\bhe\b", "they", text)
    text = re.sub(r"\bHe\b", "They", text)
    text = re.sub(r"\b(his|her)\b", "their", text)
    text = re.sub(r"\b(His|Her)\b", "Their", text)
    text = re.sub(r"\bhim\b", "them", text)
    text = re.sub(r"\bshe\b", "they", text)
    return text


# ---------------------------------------------------------------------------------------------------------------- inputs
def rng_txt(spec, pct):
    sh, lo, li, hi = spec
    f = (lambda v: f"{v:.1%}" if abs(v) < 0.1 and v else f"{v:.0%}") if pct else (lambda v: f"{v:,.0f}" if abs(v) >= 10 else f"{v:g}")
    return f"drawn: {sh.upper()} {f(lo)} / {f(li)} / {f(hi)}" if sh != "fixed" and lo != hi else "fixed"


def ag(k, field="evidence_points"):
    r = AGREED.get(k)
    return neutral(r[field]) if r and r.get(field) else ""


# (group, key, label, value, unit, mc key or None, source, why, number format). mc key: the Monte Carlo key whose range applies.
P = "pct"
G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, G12 = (
    "1. Cost to win a saver", "2. Who keeps saving", "3. How much they save", "4. The fund, and what it pays us",
    "5. Loans: who sees the offers, who applies", "6. Personal and business loans (our DSA payout)",
    "7. Other loans (other lenders pay a referral fee)", "8. The first months, and growth with the pool's history", "9. Cards",
    "10. Insurance (through a broker partner)", "11. Other products", "12. Cost to serve a saver")
INS = [p for p in ce.INSURANCE]
PRODUCT_LABEL = {p: neutral(nm) for p, _k, nm, _d in ce.PRODUCTS}


def inputs_list():
    L = []
    a = L.append
    a((G1, "cac_on", "Online saver: cost to win after the seed, all-in (before our 10% contingency)", op.CAC, "₹ a saver won", "cac",
       "Operator, 21 Oct: ₹450 base, range ₹300–600.",
       "₹300 is a competitor's figure per 'customer' (PR-02; the customer is not defined). ₹600 is our own seed funnel: ₹100 a sign-up + "
       "₹40 KYC for 1 in 2 sign-ups, and 1 in 5 sign-ups start saving. The seed (months 4–18) is budgeted at ₹600; this is a saver won after it.", "rs"))
    a((G1, "cac_door", "Doorstep saver: cost to win, all-in at scale (before our 10% contingency)", round(DOOR_CAC, 2), "₹ a saver won", None,
       "Company model (online_plan.py), months 31–96: agent pay ₹26,000 a month (salary, statutory, incentive, fidelity cover), a ₹15,500 kit with NISM V-A, "
       "30% of agents leaving a year, field leads, city offices and ₹40 KYC, divided by doorstep savers won.",
       "Worked out, not assumed. In the Monte Carlo it moves with each future's agent output (sign-ups a month per agent).", "rs"))
    a((G1, "contingency", "Our 10% contingency on the cost to win", op.CONTINGENCY, "share", None,
       "Our business plan's convention: 10% on every cost line, the cost to win included.",
       "So the LTV/CAC divides by what the plan actually spends: ₹450 × 1.1 = ₹495 online (critical review, 22 Oct).", P))
    a((G2, "r3_on", "Online: still saving at month 3", 0.80, "share of savers won", "on_r3", om.ONLINE["on_r3"][5],
       "SBI MF's ₹250 daily SIP: 35.64% had stopped at an average age of about 6 months (NG-033, XO-05), a steady ~7% a month, which is ~80% at month 3.", P))
    a((G2, "r12_on", "Online: still saving at month 12", 0.38, "share of savers won", "on_r12", om.ONLINE["on_r12"][5],
       "Operator, 21 Oct: the SBI ₹250 daily SIP (first-time investors, no loans) as the base; savings apps (24%) as the downside; "
       "a credit hook (45%) as the upside.", P))
    a((G2, "r3_door", "Doorstep: still saving at month 3", op.DOOR["r3"], "share of savers won", "r3", ag("r3"), ag("r3", "why_this_shape"), P))
    a((G2, "r12_door", "Doorstep: still saving at month 12", op.DOOR["r12"], "share of savers won", "r12", ag("r12"),
       "Agreed street retention: an agent visits, which keeps more people saving than an app does.", P))
    a((G2, "churn_late", "Both: share who stop each month after month 12", X0["churn_late"], "share a month", "churn_late",
       ag("churn_late"), ag("churn_late", "why_this_shape"), P))
    a((G3, "daily", "Daily amount", 100.0, "₹ a day", "on_daily", om.ONLINE["on_daily"][5],
       "Operator, 21 Oct: ₹100 a day, the stated minimum of a daily-savings app; the range runs from a ₹50 daily SIP to ₹300.", "rs"))
    a((G3, "days", "Saving days a month", X0["days"], "days a month", "days", ag("days"), ag("days", "why_this_shape"), "n1"))
    a((G3, "amount_growth", "Daily amount steps up each year saved", X0["amount_growth"], "a year", "amount_growth",
       ag("amount_growth"), ag("amount_growth", "why_this_shape"), P))
    a((G3, "term", "Step-up period", 12.0, "months", None, "Engine convention.", "The daily amount steps up once every 12 months.", "n0"))
    a((G3, "rollover", "Share of the balance that stays at each year end", 1.0, "share", None,
       "Online design: an SIP keeps running; there is no yearly payout.", "1 = nothing is paid out at the year end (the street product paid out).", P))
    a((G3, "withdraw_m", "Share of the balance withdrawn each month", X0["withdraw_m"], "share a month", "withdraw_m",
       ag("withdraw_m"), ag("withdraw_m", "why_this_shape"), P))
    a((G4, "eq_share", "Equity share of the savings", 0.80, "share", "eq_share", om.ONLINE["eq_share"][5],
       "Operator, 21 Oct: 80% equity SIP / 20% debt fund is the base; debt-only is a side case.", P))
    a((G4, "eq_return", "Equity fund return to the saver, net", op.EQ_RETURN, "a year", "eq_return", "Our estimate.",
       "Conservative against long-run Indian equity returns; it only grows the balance the trail is paid on.", P))
    a((G4, "debt_return", "Debt fund return to the saver, net", op.DEBT_RETURN, "a year", "fund_return", ag("fund_return"),
       ag("fund_return", "why_this_shape"), P))
    a((G4, "eq_trail", "Our trail on equity funds", op.EQ_TRAIL, "share of the balance a year", "sip_comm", ag("sip_comm"),
       "Distributor trail on an equity SIP, paid by the fund house on the balance.", "pct2"))
    a((G4, "debt_trail", "Our trail on debt funds", op.DEBT_TRAIL, "share of the balance a year", "trail", ag("trail"),
       ag("trail", "why_this_shape"), "pct2"))
    a((G5, "reach_on", "Online: KYC'd users who see loan offers, per saver won", op.LOAN_REACH, "users per saver won", "on_reach",
       om.ONLINE["on_reach"][5],
       "Operator, 21 Oct: offers go to anyone KYC'd from day 1. 5 sign-ups for each saver, half finish KYC = 2.5. A KYC'd user who never "
       "saves stays reachable for as long as a saver keeps saving. Low end: offers to savers only (1).", "n2"))
    a((G5, "reach_door", "Doorstep: users who see loan offers, per saver won", 1.0, "users per saver won", None,
       "The agent signs a saver one to one.", "No extra KYC'd non-savers come with a doorstep saver.", "n2"))
    a((G5, "loan_apply", "Reachable users who apply for a loan in a year (all loan types)", op.LOAN_APPLY, "share a year", "on_apply",
       om.ONLINE["on_apply"][5], "Operator, 21 Oct: 35% a year, split by loan type below.", P))
    for k, lab in (("pb", "personal or business loans"), ("gold", "gold loans"), ("lap", "loans against property"), ("home", "home loans")):
        key = {"pb": "apply", "gold": "loan_gold_takeup", "lap": "loan_lap_takeup", "home": "loan_home_takeup"}[k]
        a((G5, f"mix_{k}", f"Share of applications: {lab}", op.LOAN_MIX[key], "share of applications", None,
           "Operator, 21 Oct (research/xs_funnel_2026-10-21.csv).", "The other 10% are loans against the saver's own savings: tiny money, not counted.", P))
    a((G5, "gold_approval", "Gold-loan applications approved", op.GOLD_APPROVAL, "share", None,
       "Our assumption: gold loans are secured, so most are approved (the lender's call).",
       "A gold loan is a once-only referral in the model, so approval scales its take-up (critical review, 22 Oct).", P))
    a((G6, "eligible", "Applicants who can carry the loan", 1.0, "share", None, "Operator, 21 Oct.",
       "1 = eligibility is inside the approval share below (lenders' approval rates already reflect who qualifies).", P))
    a((G6, "approved_first", "First applications a lender approves", 0.30, "share", "on_approved", om.ONLINE["on_approved"][5],
       "Operator, 21 Oct: 30% first, 70% repeat (XF-18, XF-24).", P))
    a((G6, "approved_repeat", "Repeat applications approved (after repaying one)", X0["approved_repeat"], "share", "approved_repeat",
       ag("approved_repeat"), "Operator, 21 Oct: 70% (a repaid borrower is a known borrower).", P))
    a((G6, "ticket", "Loan size, blended personal and business", 100000.0, "₹ a loan", "on_ticket", om.ONLINE["on_ticket"][5],
       "Blend of personal loans ~₹50,000 (digital NBFCs ₹18,800–70,000, XF-11) and business loans ~₹1.5 lakh (merchant loans ₹50,000–5 lakh, XF-09/10).", "rs"))
    a((G6, "fee", "Our DSA payout at the start", 0.02, "share of the loan", "on_fee", om.ONLINE["on_fee"][5],
       "DSA payouts on personal loans 1–2.5%, up to 3% (XF-01, XF-02); paid by the lender on disbursal.", "pct2"))
    a((G6, "fee_mult_end", "Payout rises to this multiple by month 60", 1.5, "× the starting payout", None,
       "Operator, 21 Oct: 'DSA rates, rising'.", "A straight line from 1× in month 1 to 1.5× in month 60 (2% → 3%), as volume grows.", "n2"))
    a((G6, "tenure", "Loan tenure", 18.0, "months", None, "Research: 12–24 months for this segment (saver_inputs).",
       "A loan repaid at month 18 frees the borrower for a repeat loan.", "n0"))
    a((G6, "taken_back", "Payouts taken back (loan closed or bad within 6 months)", X0["taken_back"], "share of payouts",
       "taken_back", ag("taken_back"), ag("taken_back", "why_this_shape"), P))
    a((G6, "ticket_growth", "Next loan is bigger for each year repaid", X0["ticket_growth"], "a year repaid", "ticket_growth",
       ag("ticket_growth"), ag("ticket_growth", "why_this_shape"), P))
    a((G6, "topup_share", "Borrowers with 12+ EMIs paid who take a top-up, a year", X0["topup_share"], "share a year", "topup_share",
       ag("topup_share"), ag("topup_share", "why_this_shape"), P))
    a((G6, "topup_size", "Top-up size, share of the original loan", X0["topup_size"], "share", "topup_size",
       ag("topup_size"), ag("topup_size", "why_this_shape"), P))
    a((G6, "approval_cap", "Approval never above", ce.APPROVAL_CAP, "share", None, "Engine cap (XL-41: a lender's repeat approval 74%).",
       "Keeps approval plus its yearly growth realistic.", P))
    a((G6, "ticket_cap", "A repeat loan never above", ce.TICKET_CAP, "₹", None, "Engine cap (XL-12).", "₹5 lakh.", "rs"))
    a((G6, "topup_lag", "Top-up from this month after disbursal", float(ce.TOPUP_LAG), "month", None, "Engine rule.",
       "After 12 EMIs paid on time; at most one top-up per loan.", "n0"))
    for q in ("loan_gold", "loan_lap", "loan_home", "loan_cd", "loan_vehicle"):
        nm = PRODUCT_LABEL[q]
        if q in ("loan_cd", "loan_vehicle"):
            a((G7, f"{q}_takeup", f"{nm}: take-up a year", X0[f"{q}_takeup"], "share of savers without one, a year", f"{q}_takeup",
               ag(f"{q}_takeup"), ag(f"{q}_takeup", "why_this_shape"), "pct2"))
        src = {"loan_gold": "XF-12 (₹1.96 lakh industry average, smaller for this segment); payout XF-05.",
               "loan_lap": "XF-13 (micro-LAP ₹3.9 lakh); payout XF-04.", "loan_home": "XF-13 (₹6–8 lakh affordable housing); payout XF-03."}
        tk = X0[f"{q}_ticket"] if q in ("loan_cd", "loan_vehicle") else op.saver_inputs()[f"{q}_ticket"]
        cm = X0[f"{q}_comm"] if q in ("loan_cd", "loan_vehicle") else op.saver_inputs()[f"{q}_comm"]
        a((G7, f"{q}_ticket", f"{nm}: loan size", tk, "₹ a loan", f"{q}_ticket" if q in ("loan_cd", "loan_vehicle") else None,
           src.get(q, ag(f"{q}_ticket")), "Operator, 21 Oct baseline." if q in src else ag(f"{q}_ticket", "why_this_shape"), "rs"))
        a((G7, f"{q}_comm", f"{nm}: our referral fee", cm, "share of the loan", f"{q}_comm" if q in ("loan_cd", "loan_vehicle") else None,
           src.get(q, ag(f"{q}_comm")), "Paid once by the lender on disbursal.", "pct2"))
        if q in ("loan_lap", "loan_home"):
            a((G7, f"{q}_approval", f"{nm}: applications approved", X0[f"{q}_approval"], "share", f"{q}_approval",
               ag(f"{q}_approval"), ag(f"{q}_approval", "why_this_shape"), P))
    a((G8, "early_takeup_mult", "Months 1–6: take-up of every product, share of the full rate", X0["early_takeup_mult"], "share",
       "early_takeup_mult", ag("early_takeup_mult"), ag("early_takeup_mult", "why_this_shape"), P))
    a((G8, "early_approval_mult", "Months 1–6: loan and card approvals, share of the full rate", X0["early_approval_mult"], "share",
       "early_approval_mult", ag("early_approval_mult"), ag("early_approval_mult", "why_this_shape"), P))
    a((G8, "takeup_growth", "Take-up of every product rises each business year", X0["takeup_growth"], "a year", "takeup_growth",
       ag("takeup_growth"), ag("takeup_growth", "why_this_shape"), P))
    a((G8, "approval_growth", "Approvals rise each business year (lenders see our repayments)", X0["approval_growth"], "a year",
       "approval_growth", ag("approval_growth"), ag("approval_growth", "why_this_shape"), P))
    a((G8, "early_months", "The first months run at the early factors", float(ce.EARLY_MONTHS), "months", None, "Engine rule.",
       "Full rates from month 7.", "n0"))
    a((G8, "year_cap", "Growth with the pool's history stops after year", 5.0, "year", None, "Engine rule (held at the year-5 value).",
       "No growth is assumed after year 5.", "n0"))
    a((G8, "takeup_cap", "No take-up factor above", ce.TAKEUP_CAP, "× the agreed rate", None, "Engine cap.", "At most 2× the agreed rate.", "n2"))
    a((G9, "card_share", "Savers who get a card (once)", X0["card_share"], "share", "card_share", ag("card_share"),
       ag("card_share", "why_this_shape"), P))
    a((G9, "card_fee", "Our fee per approved card", X0["card_fee"], "₹ a card", "card_fee", ag("card_fee"), ag("card_fee", "why_this_shape"), "rs"))
    a((G10, "ins_partner_share", "Share of insurance commission that reaches us", op.OFF_PRODUCTS["ins_partner_share"], "share", None,
       "Founder's decision, 22 Oct: a fixed referral fee through the broker partner, to be agreed; not counted.",
       "A share of a broker's commission is likely not payable to an unlicensed company (to verify with counsel); our own corporate-agent "
       "registration can come later. Set a share here to see what a licence would add.", P))
    words = {"takeup": ("take-up a year", "share of savers without it, a year", "pct2"), "ticket": ("premium or ticket", "₹", "rs"),
             "comm": ("our commission", "share", "pct2"), "renew": ("renews a year", "share renewing", P),
             "renew_comm": ("commission on a renewal", "share of the renewal premium", "pct2")}
    for p, kind, _nm, d in ce.PRODUCTS:
        if p.startswith("loan_"):
            continue
        grp = G10 if p in INS else G11
        for par in d:
            k = f"{p}_{par}"
            if p == "sip" and par == "comm":
                continue                                   # the SIP product's trail is the equity trail (group 4)
            w, unit, fm = words.get(par, (par, "", "n2"))
            r = AGREED.get(k)
            unit = r["unit"] if r and r.get("unit") else unit
            if p == "bills" and par == "comm":
                fm = "rs"
            if (p, par) in (("bills", "ticket"), ("recharge", "renew"), ("bills", "renew"), ("nps", "comm")):
                fm = "n2"
            mck = k if ALLSPEC.get(k, ("fixed",))[0] != "fixed" else None
            why = ag(k, "why_this_shape") or ("Fixed: renews every year (a habit)" if par == "renew" else "")
            if p == "sip" and par == "takeup":
                why = "Off while the core savings are the equity SIP (equity share above 0); on for debt-only savers."
            if p == "choti" and par == "renew":
                why = "Share of Choti SIPs still running at month 24, when the ₹500 incentive is paid."
            if p == "nps" and par == "comm":
                why = "₹200 once per new account (the ticket × 1)."
            val, src = X0[k], ag(k) or "Engine default (cohort_engine.PRODUCTS)."
            if k in op.OFF_PRODUCTS:                       # critical review, 22 Oct
                val, mck, src = op.OFF_PRODUCTS[k], None, "Off (critical review, 22 Oct)."
                why = {"choti_takeup": "The Choti SIP incentive is for a first-time investor's monthly SIP only; our daily SIP disqualifies it.",
                       "gold_takeup": "No digital gold at launch (unregulated; the folder's own row advises against it); a gold fund later."}[k]
            a((grp, k, f"{PRODUCT_LABEL[p]}: {w}", val, neutral(unit), mck, src, neutral(why), fm))
    a((G12, "support_cost", "Support cost per saver still saving", X0["support_cost"], "₹ a month", "support_cost", ag("support_cost"),
       ag("support_cost", "why_this_shape"), "rs2"))
    a((G12, "tech", "Tech cost per KYC'd user reached, a month", op.TECH_PER_SAVER, "₹ a month", None,
       "The 2 Oct costing: ₹4 a month (cloud, SMS, KYC calls); was ₹1, our judgement.",
       "Charged for every KYC'd user who came with the saver (reach), savers or not, while the saver keeps saving.", "rs2"))
    a((G12, "debit_cost", "Payment cost per debit", op.DEBIT_COST, "₹ a debit", None,
       "The 2 Oct costing: ₹2 base (₹5 list price through a payment gateway, TC-02/06; ₹0 to us through BSE StAR MF, XB-01).",
       "Until BSE StAR MF and the fund houses confirm a daily SIP on one mandate in writing, we assume weekly debits at ₹2.", "rs2"))
    a((G12, "debits_month", "Debits a month per saver still saving", op.DEBITS_A_MONTH, "debits a month", None,
       "Founder's decision, 22 Oct: weekly until daily is confirmed.", "52 weeks ÷ 12. The monthly amount is unchanged.", "n2"))
    return L


DERIVED = [   # (after key, key, label, formula, format)
    ("contingency", "cac_all_on", "Online: cost to win with the contingency", "=i_cac_on*(1+i_contingency)", "rs"),
    ("contingency", "cac_all_door", "Doorstep: cost to win with the contingency", "=i_cac_door*(1+i_contingency)", "rs"),
    ("r12_on", "h1_on", "Online: drop-off a month, months 1–3", "=1-i_r3_on^(1/3)", "pct2"),
    ("r12_on", "h2_on", "Online: drop-off a month, months 4–12", "=1-(i_r12_on/i_r3_on)^(1/9)", "pct2"),
    ("r12_door", "h1_door", "Doorstep: drop-off a month, months 1–3", "=1-i_r3_door^(1/3)", "pct2"),
    ("r12_door", "h2_door", "Doorstep: drop-off a month, months 4–12", "=1-(i_r12_door/i_r3_door)^(1/9)", "pct2"),
    ("withdraw_m", "dep1", "Deposits a month while saving, year 1", "=i_daily*i_days", "rs"),
    ("debt_trail", "fund_return", "Blended fund return", "=i_eq_share*i_eq_return+(1-i_eq_share)*i_debt_return", "pct2"),
    ("debt_trail", "rm", "Blended fund return, a month", "=(1+d_fund_return)^(1/12)-1", "pct3"),
    ("debt_trail", "trail", "Blended trail we earn on the balance", "=i_eq_share*i_eq_trail+(1-i_eq_share)*i_debt_trail", "pct3"),
    ("mix_home", "apply_pb", "Apply for a personal or business loan, a year", "=i_loan_apply*i_mix_pb", "pct2"),
    ("mix_home", "takeup_loan_gold", "Approved gold loans, a year (applications × approval)", "=i_loan_apply*i_mix_gold*i_gold_approval", "pct2"),
    ("mix_home", "takeup_loan_lap", "Apply for a loan against property, a year", "=i_loan_apply*i_mix_lap", "pct2"),
    ("mix_home", "takeup_loan_home", "Apply for a home loan, a year", "=i_loan_apply*i_mix_home", "pct2"),
    ("topup_lag", "hz0", "Chance a reachable user applies in a month (full rate)", "=1-(1-d_apply_pb)^(1/12)", "pct3"),
    ("topup_lag", "tn", "Tenure in whole months", "=MAX(1,INT(i_tenure+0.5))", "n0"),
    ("topup_lag", "u", "Chance an eligible borrower tops up in a month", "=1-(1-i_topup_share)^(1/12)", "pct3"),
    ("topup_lag", "drop", "Top-up window: share of a loan's top-up chance unused at the end of the tenure", "=(1-d_u)^MAX(0,d_tn-i_topup_lag)", "n3"),
    ("topup_lag", "rep_ticket", "Repeat loan size", "=MIN(i_ticket_cap,i_ticket*(1+i_ticket_growth)^(d_tn/12))", "rs"),
    ("topup_lag", "topup_amt", "Top-up size", "=i_topup_size*i_ticket*(1+i_ticket_growth)", "rs"),
    ("card_fee", "card_rem", "Cards held back by the early months, issued in months 7–12", "=MAX(0,1-i_early_takeup_mult*i_early_approval_mult)", P),
    ("sip_renew", "sip_takeup", "Extra SIP: take-up a year, as used", "=IF(i_eq_share>0,0,i_sip_takeup)", "pct2"),
]
FMT = {"pct": "0.0%", "pct2": "0.00%", "pct3": "0.000%", "rs": "#,##0", "rs2": "#,##0.00", "n0": "0", "n1": "0.0", "n2": "0.00", "n3": "0.000"}


def inputs_sheet(L):
    cells, names, rows_fmt, blue, grey, bold = {}, {}, [], [], [], []
    cells["A1"] = "Inputs: every number behind one saver's LTV/CAC"
    cells["A2"] = ("Blue = an assumption you can change; every tab recalculates. Grey = worked out from the blue cells (do not type there). "
                   "Low / likely / high = the range the Monte Carlo draws from (PERT unless stated; 'fixed' = not drawn). "
                   "Sources: the IDs (XF-, XO-, PR- ...) are on the Sources tab.")
    head = ["", "Input", "Value", "Unit", "Low", "Likely", "High", "Monte Carlo", "Source", "Why this number", "Name in formulas"]
    for j, h in enumerate(head):
        cells[f"{tc.col_name(j + 1)}3"] = h
    r = 4
    after = {}
    for d in DERIVED:
        after.setdefault(d[0], []).append(d)
    last_grp = None
    for grp, key, lab, val, unit, mck, src, why, fm in L:
        if grp != last_grp:
            cells[f"A{r}"] = grp
            bold.append(r)
            r += 1
            last_grp = grp
        cells[f"B{r}"], cells[f"C{r}"], cells[f"D{r}"] = lab, float(val), unit
        spec = ALLSPEC.get(mck) if mck else None
        if spec and spec[0] != "fixed":
            cells[f"E{r}"], cells[f"F{r}"], cells[f"G{r}"] = float(spec[1]), float(spec[2]), float(spec[3])
            cells[f"H{r}"] = f"drawn ({spec[0].upper()})"
        else:
            cells[f"H{r}"] = "fixed"
        cells[f"I{r}"], cells[f"J{r}"], cells[f"K{r}"] = clean(neutral(src)), clean(neutral(why)), f"i_{key}"
        names[f"i_{key}"] = f"C{r}"
        rows_fmt.append((r, fm))
        blue.append(r)
        r += 1
        for _a, dk, dlab, f, dfm in after.get(key, []):
            cells[f"B{r}"], cells[f"C{r}"] = f"→ worked out: {dlab}", f
            cells[f"H{r}"], cells[f"K{r}"] = "follows", f"d_{dk}"
            names[f"d_{dk}"] = f"C{r}"
            rows_fmt.append((r, dfm))
            grey.append(r)
            r += 1
    return {"title": "Inputs", "cells": cells, "named_ranges": names, "_fmt": rows_fmt, "_blue": blue, "_grey": grey, "_bold": bold, "_last": r - 1}


# ---------------------------------------------------------------------------------------------------- month-by-month tabs
REF = re.compile(r"\[(?:([A-Za-z]+)!)?([\w.]+)(@p|:above)?\]")


class Tab:
    def __init__(self, title, note):
        self.title, self.note, self.cols, self.order = title, note, {}, []

    def add(self, key, band, head, f1, f2=None, fm="n3"):
        self.cols[key] = tc.col_name(len(self.order) + 1)
        self.order.append((key, band, head, f1, f1 if f2 is None else f2, fm))


def render(tpl, tab, tabs, r):
    def sub(mm):
        sh, k, mod = mm.group(1), mm.group(2), mm.group(3)
        t = tabs[sh] if sh else tab
        c = t.cols[k]
        pre = f"{sh}!" if sh else ""
        if mod == "@p":
            return f"{pre}{c}{r - 1}"
        if mod == ":above":
            return f"{pre}{c}${R0}:{c}{r - 1}"
        return f"{pre}{c}{r}"
    return REF.sub(sub, tpl) if isinstance(tpl, str) else tpl


def engine_tab():
    t = Tab("Engine", "Per saver STILL SAVING, months 1-96 (a saver who joins in the business's month 1). Saver multiplies each money "
                      "column by the share still saving. Everything here follows from Inputs; do not type on this tab.")
    t.add("m", "", "Month after joining", 1, "=[m@p]+1", "n0")
    t.add("year", "CALENDAR", "Business year (growth held after year 5)", "=MIN(i_year_cap,INT(([m]-1)/12)+1)", fm="n0")
    t.add("emt", "CALENDAR", "Early take-up factor", "=IF([m]<=i_early_months,i_early_takeup_mult,1)", fm="n2")
    t.add("ema", "CALENDAR", "Early approval factor", "=IF([m]<=i_early_months,i_early_approval_mult,1)", fm="n2")
    t.add("mt", "CALENDAR", "Take-up growth with the pool's history", "=(1+i_takeup_growth)^([year]-1)")
    t.add("ma", "CALENDAR", "Approval growth with the pool's history", "=(1+i_approval_growth)^([year]-1)")
    t.add("tf", "CALENDAR", "Take-up factor (every product)", "=MIN(i_takeup_cap,[emt]*[mt])")
    t.add("af", "CALENDAR", "First-loan approval", "=MIN(i_approval_cap,i_approved_first*[ema]*[ma])", fm="pct")
    t.add("apf", "CALENDAR", "Approval factor: secured loans, cards", "=[ema]*[ma]")
    t.add("cf", "CALENDAR", "Card factor (take-up × approval)", "=[tf]*MIN(i_takeup_cap,[apf])")
    t.add("ramp", "CALENDAR", "DSA payout ramp (× the starting payout)", "=1+(i_fee_mult_end-1)*MIN([m]-1,59)/59")
    t.add("dps", "THE FUND", "Deposits this month (₹)", "=i_daily*i_days*(1+i_amount_growth)^INT(([m]-1)/i_term)", fm="rs2")
    t.add("bs", "THE FUND", "Balance at the start (₹)", 0, "=[be@p]*IF(MOD([m]-1,i_term)=0,i_rollover,1)", fm="rs2")
    t.add("be", "THE FUND", "Balance at the end (₹)", "=[bs]*(1-i_withdraw_m)+[dps]+([bs]*(1-i_withdraw_m)+0.5*[dps])*d_rm", fm="rs2")
    t.add("bavg", "THE FUND", "Average balance (₹)", "=[bs]*(1-i_withdraw_m)+0.5*[dps]", fm="rs2")
    t.add("fund", "THE FUND", "Fund fees: our trail (₹)", "=[bavg]*d_trail/12", fm="rs2")
    t.add("hz", "PERSONAL + BUSINESS LOANS", "Chance a user applies this month", "=d_hz0*[tf]", fm="pct3")
    t.add("n0", "PERSONAL + BUSINESS LOANS", "Never borrowed", 1, "=[n0@p]-[first@p]")
    t.add("first", "PERSONAL + BUSINESS LOANS", "First loans", "=[n0]*[hz]*i_eligible*[af]", fm="n4")
    t.add("e", "PERSONAL + BUSINESS LOANS", "Repaid, can borrow again", 0, "=[e@p]-[rep@p]+IF([m]-1-d_tn>=1,INDEX([loans:above],[m]-1-d_tn),0)")
    t.add("rep", "PERSONAL + BUSINESS LOANS", "Repeat loans", "=[e]*[hz]*i_eligible*i_approved_repeat", fm="n4")
    t.add("loans", "PERSONAL + BUSINESS LOANS", "Loans made (first + repeat)", "=[first]+[rep]", fm="n4")
    t.add("apps", "PERSONAL + BUSINESS LOANS", "Applications", "=([n0]+[e])*[hz]", fm="n4")
    t.add("W", "PERSONAL + BUSINESS LOANS", "Loans in the top-up window", 0,
          "=(1-d_u)*[W@p]+IF(AND([m]>=i_topup_lag+1,d_tn>i_topup_lag),INDEX([loans:above],[m]-i_topup_lag),0)"
          "-IF(AND([m]-d_tn>=1,d_tn>i_topup_lag),INDEX([loans:above],[m]-d_tn)*d_drop,0)", fm="n4")
    t.add("topups", "PERSONAL + BUSINESS LOANS", "Top-up loans", "=d_u*[W]", fm="n4")
    t.add("lent", "PERSONAL + BUSINESS LOANS", "Money lent (₹)", "=[first]*i_ticket+[rep]*d_rep_ticket+[topups]*d_topup_amt", fm="rs2")
    t.add("orig", "PERSONAL + BUSINESS LOANS", "Payout at the starting rate (₹)", "=[lent]*i_fee*(1-i_taken_back)", fm="rs2")
    t.add("cards", "CARDS", "Cards issued", "=IF([m]<=6,i_card_share/6*[cf],IF([m]<=12,i_card_share*d_card_rem/6*MIN(i_takeup_cap,[mt])*MIN(i_takeup_cap,[ma]),0))", fm="n4")
    t.add("cardfee", "CARDS", "Card fees (₹)", "=[cards]*i_card_fee", fm="rs2")
    return t


def products_tab():
    t = Tab("Products", "Per saver STILL SAVING, months 1-96: every cross-sell product. 'Not yet bought' falls as people buy; a policy "
                        "renews each year at its renewal rate; a habit (gold, recharge, bills) keeps running at its renewal rate. "
                        "Insurance pays us the broker partner's share. Do not type on this tab.")
    t.add("m", "", "Month after joining", "=[Engine!m]", fm="n0")
    t.add("tf", "", "Take-up factor", "=[Engine!tf]", fm="n3")
    t.add("apf", "", "Approval factor", "=[Engine!apf]", fm="n3")
    TK = {"loan_gold": "d_takeup_loan_gold", "loan_lap": "d_takeup_loan_lap", "loan_home": "d_takeup_loan_home", "sip": "d_sip_takeup"}
    revs = {}
    for p, kind, nm, d in ce.PRODUCTS:
        band = PRODUCT_LABEL[p].upper()
        tk = TK.get(p, f"i_{p}_takeup")
        h = f"(1-(1-{tk})^(1/12))*[tf]"
        if kind == "secured":
            h += f"*MIN(i_approval_cap,i_{p}_approval*[apf])"
        t.add(f"{p}.N", band, "Not yet bought", 1, f"=[{p}.N@p]-[{p}.G@p]")
        t.add(f"{p}.G", band, "Buys this month", f"=[{p}.N]*{h}", fm="n5")
        ins = "*i_ins_partner_share" if p in INS else ""
        if kind == "ins":
            rc = f"i_{p}_renew_comm" if f"{p}_renew_comm" in ce.FALLBACK else f"i_{p}_comm"
            t.add(f"{p}.P", band, "Renewals due (policies)", 0, f"=IF([m]>12,i_{p}_renew*(INDEX([{p}.G:above],[m]-12)+INDEX([{p}.P:above],[m]-12)),0)", fm="n5")
            t.add(f"{p}.rev", band, "Our money (₹)", f"=([{p}.G]*i_{p}_ticket*i_{p}_comm+[{p}.P]*i_{p}_ticket*{rc}){ins}", fm="rs3")
        elif kind in ("once", "secured"):
            t.add(f"{p}.rev", band, "Our money (₹)", f"=[{p}.G]*i_{p}_ticket*i_{p}_comm{ins}", fm="rs3")
        elif kind == "bonus":
            t.add(f"{p}.rev", band, "Our money (₹)", 0, f"=IF([m]>24,INDEX([{p}.G:above],[m]-24)*i_{p}_renew*i_{p}_ticket,0)", fm="rs3")
        else:
            rho = f"i_{p}_renew^(1/12)"
            t.add(f"{p}.R", band, "Still running", f"=[{p}.G]", f"=[{p}.R@p]*{rho}+[{p}.G]", fm="n5")
            if kind == "trail":
                t.add(f"{p}.Q", band, "Months of SIP built up", 0, f"={rho}*([{p}.Q@p]+[{p}.R@p])", fm="n5")
                t.add(f"{p}.rev", band, "Our money (₹)", f"=i_{p}_ticket*([{p}.Q]+0.5*[{p}.R])*i_eq_trail/12", fm="rs3")
            else:
                div = "/12" if kind == "flow_year" else ""
                t.add(f"{p}.rev", band, "Our money (₹)", f"=[{p}.R]*i_{p}_ticket*i_{p}_comm{div}", fm="rs3")
        revs[p] = f"[{p}.rev]"
    loans = [p for p, *_ in ce.PRODUCTS if p.startswith("loan_")]
    oth = [p for p, *_ in ce.PRODUCTS if p not in INS and not p.startswith("loan_")]
    t.add("ins", "TOTALS", "Insurance (₹)", "=" + "+".join(revs[p] for p in INS), fm="rs3")
    reach_l = [p for p in loans if p in op.LOAN_REACH_XS]
    t.add("oloans", "TOTALS", "Other loans in the 35% funnel: gold, property, home (₹)", "=" + "+".join(revs[p] for p in reach_l), fm="rs3")
    t.add("oloans_s", "TOTALS", "Other loans, savers only: durables, vehicles (₹)", "=" + "+".join(revs[p] for p in loans if p not in reach_l), fm="rs3")
    t.add("other", "TOTALS", "Other products: SIP, Choti, NPS, gold, FD, recharge, bills (₹)", "=" + "+".join(revs[p] for p in oth), fm="rs3")
    return t


SV = (("on", "ONLINE SAVER"), ("door", "DOORSTEP SAVER"))


def saver_tab():
    t = Tab("Saver", "One saver won, months 1-96, in ₹: the share still saving × each per-saver line on Engine and Products. Loans count "
                     "every KYC'd user who came with the saver (reach) and the payout ramp. Do not type on this tab.")
    t.add("m", "", "Month after joining", 1, "=[m@p]+1", "n0")
    for sv, band in SV:
        t.add(f"{sv}.h", band, "Drop-off this month", f"=IF([m]<=3,d_h1_{sv},IF([m]<=12,d_h2_{sv},i_churn_late))", fm="pct2")
        t.add(f"{sv}.s", band, "Still saving", 1, f"=[{sv}.s@p]*(1-[{sv}.h@p])", fm="pct")
        t.add(f"{sv}.dep", band, "Deposits (₹)", f"=[{sv}.s]*[Engine!dps]", fm="rs")
        t.add(f"{sv}.bal", band, "Average balance (₹)", f"=[{sv}.s]*[Engine!bavg]", fm="rs")
        t.add(f"{sv}.fund", band, "Fund fees (₹)", f"=[{sv}.s]*[Engine!fund]", fm="rs2")
        t.add(f"{sv}.pb", band, "Personal + business loan payouts (₹)", f"=[{sv}.s]*[Engine!orig]*[Engine!ramp]*i_reach_{sv}", fm="rs2")
        t.add(f"{sv}.ol", band, "Other loan referrals (₹)", f"=[{sv}.s]*([Products!oloans]*i_reach_{sv}+[Products!oloans_s])", fm="rs2")
        t.add(f"{sv}.ins", band, "Insurance (₹)", f"=[{sv}.s]*[Products!ins]", fm="rs2")
        t.add(f"{sv}.cards", band, "Cards (₹)", f"=[{sv}.s]*[Engine!cardfee]", fm="rs2")
        t.add(f"{sv}.oth", band, "Other products (₹)", f"=[{sv}.s]*[Products!other]", fm="rs2")
        t.add(f"{sv}.rev", band, "Revenue (₹)", f"=[{sv}.fund]+[{sv}.pb]+[{sv}.ol]+[{sv}.ins]+[{sv}.cards]+[{sv}.oth]", fm="rs2")
        t.add(f"{sv}.serve", band, "Serving: support, tech for every KYC'd user reached, payments (₹)",
              f"=[{sv}.s]*(i_support_cost+i_tech*i_reach_{sv}+i_debit_cost*i_debits_month)", fm="rs2")
        t.add(f"{sv}.net", band, "Revenue less serving (₹)", f"=[{sv}.rev]-[{sv}.serve]", fm="rs2")
        t.add(f"{sv}.cum", band, ("Online" if sv == "on" else "Doorstep") + ": cumulative ₹ after the cost to win",
              f"=-d_cac_all_{sv}+[{sv}.net]", f"=[{sv}.cum@p]+[{sv}.net]", fm="rs")
    return t


def expand(t, tabs):
    cells = {"A1": f"{t.title}: " + {"Engine": "fund, loans and cards, per saver still saving", "Products": "every cross-sell product, per saver still saving",
                                      "Saver": "one saver won, month by month (₹)"}[t.title], "A2": t.note}
    for key, band, head, f1, f2, _fm in t.order:
        c = t.cols[key]
        if band:
            cells[f"{c}3"] = band
        cells[f"{c}4"] = head
        for r in range(R0, R1 + 1):
            cells[f"{c}{r}"] = render(f1 if r == R0 else f2, t, tabs, r)
    # the copy-down rule: every row from month 3 is month 2's formula shifted
    for key, *_ in t.order:
        c = t.cols[key]
        for r in (R0 + 5, R1):
            assert shift(cells[f"{c}{R0 + 1}"], r - R0 - 1) == cells[f"{c}{r}"], (t.title, key, r)
    return {"title": t.title, "cells": cells, "named_ranges": {}}


def shift(f, k):
    if not isinstance(f, str):
        return f
    return re.sub(r"(?<![$A-Za-z_])([A-Z]{1,3})(\$?)(\d+)", lambda m: f"{m.group(1)}{m.group(2)}{m.group(3) if m.group(2) else int(m.group(3)) + k}", f)


# ------------------------------------------------------------------------------------------------------------ answer tab
LINES = [("Cost to win", None), ("Fund fees (our trail on the savings)", "fund"), ("Personal + business loan payouts", "pb"),
         ("Other loan referrals (gold, property, home, durables, vehicles)", "ol"), ("Insurance", "ins"), ("Cards", "cards"),
         ("Other products (recharge, bills, FD, NPS)", "oth"), ("Serving (support, tech, payments)", "serve")]


def answer_tab(sv_tab, py):
    c = {}
    col = sv_tab.cols
    c["A1"] = "LTV/CAC: what one saver won is worth, live"
    c["A2"] = ("Per saver won, undiscounted ₹. LTV = revenue less serving over 5 years (8 years alongside); LTV/CAC = LTV ÷ cost to win; pays back = "
               "the month cumulative revenue less serving reaches the cost to win. A saver who joins in the business's month 1. Not in this view: "
               "the team, office and brand (company costs), the 10% contingency, tax. Change any blue cell on Inputs and every number here moves.")
    head = ["Per saver won (₹)", "Online, 5 years", "Doorstep, 5 years", "Online, 8 years", "Doorstep, 8 years", None,
            "Plan model: online, 5 years (fixed)", "Plan model: doorstep, 5 years (fixed)", "Sheet − plan model, online"]
    for j, h in enumerate(head):
        if h:
            c[f"{tc.col_name(j + 1)}4"] = h
    for i, (lab, k) in enumerate(LINES):
        r = 5 + i
        c[f"A{r}"] = lab
        for x, sv, last in (("B", "on", R60), ("C", "door", R60), ("D", "on", R1), ("E", "door", R1)):
            if k is None:
                c[f"{x}{r}"] = f"=-d_cac_all_{sv}"
            else:
                cc = col[f"{sv}.{k}"]
                c[f"{x}{r}"] = f"={'-' if k == 'serve' else ''}SUM(Saver!{cc}{R0}:{cc}{last})"
        c[f"G{r}"], c[f"H{r}"] = round(py["on"][k or "cac"], 2), round(py["door"][k or "cac"], 2)
        c[f"I{r}"] = f"=B{r}-G{r}"
    c["A13"] = "Net after the cost to win"
    c["A15"] = "Revenue"
    c["A16"] = "LTV: revenue less serving"
    c["A17"] = "LTV/CAC"
    c["A18"] = "Pays back in month"
    c["A19"] = "Cross-sell share of revenue (everything except fund fees)"
    c["A20"] = "Still saving at month 12"
    c["A21"] = "Deposits over the period (₹)"
    for x, sv, last in (("B", "on", R60), ("C", "door", R60), ("D", "on", R1), ("E", "door", R1)):
        c[f"{x}13"] = f"=SUM({x}5:{x}12)"
        c[f"{x}15"] = f"=SUM({x}6:{x}11)"
        c[f"{x}16"] = f"={x}15+{x}12"
        c[f"{x}17"] = f"={x}16/-{x}5"
        cum = col[f"{sv}.cum"]
        c[f"{x}18"] = f'=IFERROR(MATCH(1,ARRAYFORMULA((Saver!{cum}{R0}:{cum}{R1}>=0)*1),0),"after month 96")'
        c[f"{x}19"] = f"=({x}15-{x}6)/{x}15"
        c[f"{x}20"] = f"=Saver!{col[f'{sv}.s']}{R0 + 12}"
        dep = col[f"{sv}.dep"]
        c[f"{x}21"] = f"=SUM(Saver!{dep}{R0}:{dep}{last})"
    for r, k in ((13, "net"), (15, "rev"), (16, "ltv"), (17, "ltvcac"), (18, "pay"), (19, "xs"), (20, "s12"), (21, "dep")):
        c[f"G{r}"], c[f"H{r}"] = round(py["on"][k], 4), round(py["door"][k], 4)
        c[f"I{r}"] = f'=IFERROR(B{r}-G{r},"")'
    c["A23"] = "1,000 futures (the Monte Carlo tab: the same futures as the company Monte Carlo). Ask any other question on Projector."
    for j, h in enumerate(["", "10th percentile", "Median", "90th percentile", "Share of futures at 3× or more", "Share paid back within 24 months",
                           "Share never paid back in 8 years"]):
        if h:
            c[f"{tc.col_name(j + 1)}24"] = h
    rows = [("Online saver: LTV/CAC, 5 years", "mc_on_ltv60", "mc_on_pay"), ("Online saver: pays back in month", "mc_on_pay", None),
            ("Doorstep saver: LTV/CAC, 5 years", "mc_door_ltv60", "mc_door_pay"), ("Doorstep saver: pays back in month", "mc_door_pay", None)]
    for i, (lab, nm, pay) in enumerate(rows):
        r = 25 + i
        c[f"A{r}"] = lab
        c[f"B{r}"], c[f"C{r}"], c[f"D{r}"] = f"=PERCENTILE({nm},0.1)", f"=MEDIAN({nm})", f"=PERCENTILE({nm},0.9)"
        if pay:
            c[f"E{r}"] = f'=COUNTIF({nm},">=3")/COUNT({nm})'
            c[f"F{r}"] = f'=COUNTIF({pay},"<=24")/COUNT({pay})'
            c[f"G{r}"] = f'=COUNTIF({pay},">96")/COUNT({pay})'
    c["A30"] = ("Charts: the waterfall is the online saver's 5 years (column B); the curve is each saver's cumulative ₹ after the cost to win "
                "(Saver tab), crossing zero in the payback month.")
    return {"title": "LTV-CAC", "cells": c, "named_ranges": {}}


# -------------------------------------------------------------------------------------------------- Python side (truth)
def py_view(x, cac, reach):
    d = op.ltv_parts(x, reach)
    p = d["_p"]
    lines = {"fund": d["Fund fees"], "pb": d["personal and business loans"], "ol": d["Loans (all referrals)"] - d["personal and business loans"],
             "ins": d["Insurance"], "cards": d["Cards"], "oth": d["Other products"], "serve": d["serving"]}
    cum = np.cumsum(d["income"] - d["serving"]) - cac
    pay = int(np.argmax(cum >= 0)) + 1 if (cum >= 0).any() else 97
    out = {"_m": {k: v.copy() for k, v in lines.items()}, "_cum": cum, "_s": p["still_saving"][0].copy()}
    for n, tag in ((60, ""), (96, "96")):
        for k, v in lines.items():
            out[k + tag] = float(v[:n].sum()) * (-1 if k == "serve" else 1)
        rev = float(d["income"][:n].sum())
        out["rev" + tag], out["ltv" + tag] = rev, rev - float(d["serving"][:n].sum())
        out["ltvcac" + tag], out["net" + tag] = out["ltv" + tag] / cac, out["ltv" + tag] - cac
    out["cac"], out["pay"] = -cac, pay
    out["xs"] = (out["rev"] - out["fund"]) / out["rev"]
    out["s12"] = float(p["still_saving"][0][12])
    out["dep"] = float(p["deposits"][0][:60].sum())
    return out


def base_params():
    return {k: float(ALLSPEC[k][2]) for k in ALLSPEC}


def apply_params(pp):
    """The Monte Carlo's mapping (online_mc.run_draw) without the company run: sets op.OV / op.DOOR / op.AGENT_SIGNUPS."""
    op._CACHE.clear()
    ov = {k: pp[k] for k in ce.KEYS if k not in om.FIXED_DESIGN}
    eq = pp["eq_share"]
    ov.update({"daily": pp["on_daily"], "r3": pp["on_r3"], "r12": pp["on_r12"], **op.loan_mix(pp["on_apply"]), "ticket": pp["on_ticket"],
               "approved_first": pp["on_approved"], "fee": pp["on_fee"], "_loan_reach": pp["on_reach"],
               "trail": eq * pp["sip_comm"] + (1 - eq) * pp["trail"], "fund_return": eq * pp["eq_return"] + (1 - eq) * pp["fund_return"],
               "sip_takeup": 0.0})
    op.OV.clear()
    op.OV.update(ov)
    op.DOOR.update({"r3": pp["r3"], "r12": pp["r12"]})
    op.AGENT_SIGNUPS = pp["signups_run"]


def reset():
    op.OV.clear()
    op.DOOR.update({"r3": 0.80, "r12": X0["r12"]})
    op.AGENT_SIGNUPS = 100.0
    op._CACHE.clear()


def evaluate(pp, door_cac=True):
    apply_params(pp)
    dc = op.unit_rows_door_cac() if door_cac else DOOR_CAC
    k = 1 + op.CONTINGENCY                                   # the plan spends the cost to win plus its 10% contingency
    on = py_view(op.saver_inputs(), pp["cac"] * k, pp["on_reach"])
    dr = py_view(op.saver_inputs(doorstep=True), dc * k, 1.0)
    reset()
    return on, dr, dc


def sheet_values(pp, door_cac):
    """Blue-cell values on Inputs for a Monte Carlo parameter set (inverse of apply_params)."""
    v = {}
    for grp, key, lab, val, *_ in inputs_list():
        v[key] = float(val)
    for k in ce.KEYS:
        if k not in om.FIXED_DESIGN and k in v:
            v[k] = pp[k]
    v.update({"daily": pp["on_daily"], "r3_on": pp["on_r3"], "r12_on": pp["on_r12"], "cac_on": pp["cac"], "loan_apply": pp["on_apply"],
              "ticket": pp["on_ticket"], "approved_first": pp["on_approved"], "fee": pp["on_fee"], "reach_on": pp["on_reach"],
              "eq_share": pp["eq_share"], "eq_return": pp["eq_return"], "debt_return": pp["fund_return"], "eq_trail": pp["sip_comm"],
              "debt_trail": pp["trail"], "r3_door": pp["r3"], "r12_door": pp["r12"], "cac_door": door_cac})
    return v


# ---------------------------------------------------------------------------------------------------------- Monte Carlo
MC_IN = [("on_daily", "Daily amount (₹)"), ("on_r12", "Online: still saving at month 12"), ("on_r3", "Online: still saving at month 3"),
         ("cac", "Cost to win an online saver (₹)"), ("on_apply", "Apply for a loan in a year"), ("on_ticket", "Personal + business loan size (₹)"),
         ("on_approved", "First applications approved"), ("on_fee", "DSA payout at the start"), ("on_reach", "KYC'd users per online saver"),
         ("eq_share", "Equity share"), ("eq_return", "Equity return a year"), ("r12", "Doorstep: still saving at month 12")]
MC_OUT = [("on_ltv60", "Online: LTV/CAC, 5 years"), ("on_ltv96", "Online: LTV/CAC, 8 years"), ("on_pay", "Online: pays back in month"),
          ("on_rev60", "Online: revenue, 5 years (₹)"), ("on_fund60", "Online: fund fees, 5 years (₹)"),
          ("on_pb60", "Online: personal + business loan payouts, 5 years (₹)"), ("on_ol60", "Online: other loan referrals, 5 years (₹)"),
          ("on_ins60", "Online: insurance, 5 years (₹)"), ("on_co60", "Online: cards + other products, 5 years (₹)"),
          ("on_serve60", "Online: serving, 5 years (₹)"), ("on_net60", "Online: net after the cost to win, 5 years (₹)"),
          ("door_cac", "Doorstep: cost to win (₹)"), ("door_ltv60", "Doorstep: LTV/CAC, 5 years"), ("door_pay", "Doorstep: pays back in month"),
          ("co_profit", "Company: profit from month (profitable path)"), ("co_money", "Company: money needed ($M)")]


def mc_run():
    xm = om.sample()
    co = list(csv.DictReader((T / "online_mc_draws.csv").open()))
    assert len(co) == om.N
    rows = []
    for i in range(om.N):
        pp = {k: float(xm[k][i]) for k in ALLSPEC}
        for k in ("on_daily", "on_r12", "cac", "on_apply", "r12", "loss"):
            assert abs(float(co[i][k]) - pp[k]) < 1e-5 * max(1, abs(pp[k])), (i, k)
        on, dr, dc = evaluate(pp)
        r = {"draw": i + 1, **{k: pp[k] for k in ALLSPEC},
             "on_ltv60": on["ltvcac"], "on_ltv96": on["ltvcac96"], "on_pay": on["pay"], "on_rev60": on["rev"], "on_fund60": on["fund"],
             "on_pb60": on["pb"], "on_ol60": on["ol"], "on_ins60": on["ins"], "on_co60": on["cards"] + on["oth"], "on_serve60": on["serve"],
             "on_net60": on["net"], "door_cac": dc, "door_ltv60": dr["ltvcac"], "door_pay": dr["pay"],
             "co_profit": float(co[i]["profit_month_p"]), "co_money": float(co[i]["money_p"])}
        rows.append(r)
    return rows


def drivers(rows):
    keys = [k for k in drawn_keys() if np.ptp([r[k] for r in rows]) > 0]
    out = []
    for k in keys:
        xs = [r[k] for r in rows]
        out.append({"key": k, "on": float(stats.spearmanr(xs, [r["on_ltv60"] for r in rows]).statistic),
                    "pay": float(stats.spearmanr(xs, [r["on_pay"] for r in rows]).statistic),
                    "door": float(stats.spearmanr(xs, [r["door_ltv60"] for r in rows]).statistic)})
    out.sort(key=lambda d: -abs(d["on"]))
    return out


def drawn_keys():
    """Inputs the Monte Carlo actually varies (online_mc.run_draw): the agreed keys outside the fixed design, the online ranges,
    and the four it maps itself (doorstep retention, the debt trail and return) plus the agent's sign-ups (the doorstep cost to win)."""
    return [k for k in ALLSPEC if ALLSPEC[k][0] != "fixed" and ALLSPEC[k][1] != ALLSPEC[k][3]
            and (k not in om.FIXED_DESIGN or k in ("r3", "r12", "trail", "fund_return", "signups_run"))]


def label_of(k):
    if k in om.ONLINE:
        return om.ONLINE[k][4].replace("(Rs", "(₹")
    special = {"r3": "Doorstep: still saving at month 3", "r12": "Doorstep: still saving at month 12", "trail": "Our trail on debt funds",
               "fund_return": "Debt fund return, net", "sip_comm": "Our trail on equity funds",
               "signups_run": "Doorstep agent: sign-ups a month (sets the doorstep cost to win)"}
    if k in special:
        return special[k]
    for grp, key, lab, *_ in inputs_list():
        if key == k:
            return lab
    return neutral(AGREED[k]["name"]) if k in AGREED else k


def one_at_a_time(drv):
    base = base_params()
    b_on, b_dr, _ = evaluate(base)
    out = []
    for d in drv:
        k = d["key"]
        sh, lo, li, hi = ALLSPEC[k]
        res = {}
        for tag, v in (("lo", lo), ("hi", hi)):
            pp = dict(base)
            pp[k] = float(v)
            if k in ("on_r3", "on_r12", "r3", "r12"):           # keep month 12 below month 3
                a3, a12 = ("on_r3", "on_r12") if k.startswith("on_") else ("r3", "r12")
                if pp[a12] >= pp[a3]:
                    pp[a3] = min(0.99, pp[a12] + 0.05)
            on, dr, dc = evaluate(pp)
            res[tag] = (on, dr)
        out.append({"key": k, "label": label_of(k), "low": lo, "likely": li, "high": hi,
                    "on_lo": res["lo"][0]["ltvcac"], "on_hi": res["hi"][0]["ltvcac"], "pay_lo": res["lo"][0]["pay"], "pay_hi": res["hi"][0]["pay"],
                    "door_lo": res["lo"][1]["ltvcac"], "door_hi": res["hi"][1]["ltvcac"], "rank_on": d["on"], "rank_door": d["door"]})
    out.sort(key=lambda r: (-round(abs(r["on_hi"] - r["on_lo"]), 4), -abs(r["door_hi"] - r["door_lo"])))
    return out, b_on, b_dr


# ------------------------------------------------------------------------------------------------------------ the check
def book_for(spec_sheets, values):
    sh = [dict(s) for s in spec_sheets]
    inp = next(s for s in sh if s["title"] == "Inputs")
    inp["cells"] = dict(inp["cells"])
    for k, v in values.items():
        inp["cells"][inp["named_ranges"][f"i_{k}"]] = float(v)
    b = tc.Book({"sheets": sh})
    for t in ("Engine", "Products", "Saver"):                 # warm row by row: shallow recursion
        cells = next(s for s in sh if s["title"] == t)["cells"]
        by_row = {}
        for a in cells:
            rr, cc = tc.parse_a1(a)
            by_row.setdefault(rr, []).append(cc)
        for r in range(R0, R1 + 1):
            for cc in sorted(by_row.get(r, [])):
                b.cell(t, r, cc)
    return b


def check(spec_sheets, sv_tab, cases):
    rows = []
    for name, pp, dc in cases:
        b = book_for(spec_sheets, sheet_values(pp, dc))
        on, dr, _ = evaluate(pp, door_cac=False) if dc == DOOR_CAC else evaluate(pp)
        for sv, py, col_b in (("on", on, "B"), ("door", dr, "C")):
            worst = 0.0
            for k in ("fund", "pb", "ol", "ins", "cards", "oth", "serve"):
                cc = tc.col_num(sv_tab.cols[f"{sv}.{k}"])
                sheet_m = np.array([float(b.cell("Saver", r, cc)) for r in range(R0, R1 + 1)])
                pm = py["_m"][k]
                worst = max(worst, float(np.max(np.abs(sheet_m - pm)) / max(1e-9, np.max(np.abs(pm)))))
            ltv = float(b.cell("LTV-CAC", 17, tc.col_num(col_b)))
            pay = b.cell("LTV-CAC", 18, tc.col_num(col_b))
            pay = 97 if isinstance(pay, str) else int(pay)
            rows.append({"case": name, "saver": sv, "sheet LTV/CAC 5y": round(ltv, 6), "python LTV/CAC 5y": round(py["ltvcac"], 6),
                         "sheet payback": pay, "python payback": py["pay"], "worst monthly line gap (share of the line's peak)": f"{worst:.2e}"})
            assert abs(ltv - py["ltvcac"]) < 1e-6 * max(1, abs(py["ltvcac"])) and pay == py["pay"] and worst < 1e-8, rows[-1]
    return rows


# ------------------------------------------------------------------------------------------------------------- the tabs
def mc_tab(rows):
    c = {"A1": "Monte Carlo: 1,000 futures of one saver (pasted from the plan's model; the same futures and draws as the company Monte Carlo)",
         "A2": ("Each row is one future: the inputs drawn for it (the main ones shown; every other input on Inputs marked 'drawn' was drawn too) "
                "and what one saver is worth in it. 97 in a 'pays back' or 'profit from' column = not within 8 years. Values, not formulas: "
                "Projector asks questions of this table live.")}
    head = ["Future"] + [h for _k, h in MC_IN] + [h for _k, h in MC_OUT]
    for j, h in enumerate(head):
        c[f"{tc.col_name(j + 1)}3"] = h
    data = []
    for r in rows:
        line = [None]
        for k, _h in MC_IN:
            v = r[k]
            line.append(round(v) if abs(v) >= 100 else round(v, 3 if abs(v) < 1 else 2))
        for k, _h in MC_OUT:
            v = r[k]
            line.append(round(v, 2) if k in ("on_ltv60", "on_ltv96", "door_ltv60", "co_money") else int(round(v)))
        data.append(line)
    c["A4"] = f"=SEQUENCE({len(rows)})"
    names = {"mc_data": f"A4:{tc.col_name(len(head))}{3 + len(rows)}", "mc_head": f"A3:{tc.col_name(len(head))}3"}
    for j, (k, _h) in enumerate(MC_OUT):
        cc = tc.col_name(2 + len(MC_IN) + j)
        names[f"mc_{k}"] = f"{cc}4:{cc}{3 + len(rows)}"
    return {"title": "Monte Carlo", "cells": c, "named_ranges": names, "_data": data, "_ncol": len(head)}


def projector_tab():
    c = {"A1": "Projector: ask the 1,000 futures any question (live)",
         "A2": ("1) Pick what you want to see in B4 (any column of the Monte Carlo tab). 2) Optionally keep only some futures: pick up to three "
                "columns in B6:B8 with a range (leave from/to blank for no limit). 3) Set a line in B10 to get the share of futures above and below it."),
         "A4": "Show", "B4": "Online: LTV/CAC, 5 years",
         "A5": "Keep only futures where (blank = all)", "B5": "column", "C5": "from", "D5": "to",
         "A6": "Filter 1", "A7": "Filter 2", "A8": "Filter 3", "A10": "Line to test", "B10": 3,
         "A12": "Answer", "B12": "=B4"}
    stat = [("Futures that pass the filters", "=SUM(J4:J1003)"), ("Mean", "=AVERAGE(FILTER(K4:K1003,J4:J1003=1))")]
    for q, lab in ((0.05, "5th percentile"), (0.10, "10th percentile"), (0.25, "25th percentile"), (0.50, "Median"),
                   (0.75, "75th percentile"), (0.90, "90th percentile"), (0.95, "95th percentile")):
        stat.append((lab, f"=PERCENTILE(FILTER(K4:K1003,J4:J1003=1),{q})"))
    stat += [("Lowest", "=MIN(FILTER(K4:K1003,J4:J1003=1))"), ("Highest", "=MAX(FILTER(K4:K1003,J4:J1003=1))"),
             ("Share of these futures at or above the line", '=IFERROR(COUNTIFS(K4:K1003,">="&B10,J4:J1003,1)/B13,0)'),
             ("Share of these futures below the line", '=IFERROR(COUNTIFS(K4:K1003,"<"&B10,J4:J1003,1)/B13,0)')]
    for i, (lab, f) in enumerate(stat):
        c[f"A{13 + i}"], c[f"B{13 + i}"] = lab, f
    c["A29"] = "Spread of the answer across the futures that pass (20 equal bins, lowest to highest)"
    c["A30"], c["B30"], c["C30"] = "From", "To", "Futures"
    for i in range(20):
        r = 31 + i
        c[f"A{r}"] = f"=$B$22+($B$23-$B$22)*{i}/20"
        c[f"B{r}"] = f"=$B$22+($B$23-$B$22)*{i + 1}/20"
        c[f"C{r}"] = (f'=COUNTIFS($K$4:$K$1003,">="&A{r},$K$4:$K$1003,"<"&B{r},$J$4:$J$1003,1)' if i < 19 else
                      f'=COUNTIFS($K$4:$K$1003,">="&A{r},$K$4:$K$1003,"<="&B{r},$J$4:$J$1003,1)')
    c["J3"], c["K3"] = "Passes the filters (1 = yes)", "=B4"
    conds = []
    for r in (6, 7, 8):
        col = f"INDEX(mc_data,0,MATCH(B{r},mc_head,0))"
        conds.append(f'IF(B{r}="",1,IFERROR(({col}>=IF(C{r}="",-1E+300,C{r}))*({col}<=IF(D{r}="",1E+300,D{r})),1))')
    c["J4"] = "=ARRAYFORMULA(SEQUENCE(ROWS(mc_data),1,1,0)*" + "*".join(conds) + ")"
    c["K4"] = "=ARRAYFORMULA(INDEX(mc_data,0,MATCH(B4,mc_head,0)))"
    c["E4"] = '=IF(ISNA(MATCH(B4,mc_head,0)),"Pick a column name from the list","")'
    # ready answers
    c["M3"] = "Ready answers (all 1,000 futures, whatever the filters on the left)"
    ready = [("Online saver: LTV/CAC (5 years), median", "=MEDIAN(mc_on_ltv60)"),
             ("Online saver: share of futures at 3× or more", '=COUNTIF(mc_on_ltv60,">=3")/1000'),
             ("Online saver: share of futures below 1× (never earns back its cost in 5 years)", '=COUNTIF(mc_on_ltv60,"<1")/1000'),
             ("Online saver: pays back in month, median", "=MEDIAN(mc_on_pay)"),
             ("Online saver: share paid back within 24 months", '=COUNTIF(mc_on_pay,"<=24")/1000'),
             ("Doorstep saver: LTV/CAC (5 years), median", "=MEDIAN(mc_door_ltv60)"),
             ("Doorstep saver: pays back in month, median", "=MEDIAN(mc_door_pay)"),
             ("Company: share of futures profitable by month 60", '=COUNTIF(mc_co_profit,"<=60")/1000'),
             ("Online LTV/CAC median, in futures where under 20% apply for a loan a year",
              f'=MEDIAN(FILTER(mc_on_ltv60,INDEX(mc_data,0,MATCH("Apply for a loan in a year",mc_head,0))<0.2))'),
             ("Online LTV/CAC median, in futures where online savers keep saving less (under 30% at month 12)",
              f'=MEDIAN(FILTER(mc_on_ltv60,INDEX(mc_data,0,MATCH("Online: still saving at month 12",mc_head,0))<0.3))'),
             ("Company profit month, median, in futures where online LTV/CAC is under 3×", '=MEDIAN(FILTER(mc_co_profit,mc_on_ltv60<3))'),
             ("Company profit month, median, in futures where online LTV/CAC is 3× or more", '=MEDIAN(FILTER(mc_co_profit,mc_on_ltv60>=3))')]
    for i, (lab, f) in enumerate(ready):
        c[f"M{4 + i}"], c[f"N{4 + i}"] = lab, f
    return {"title": "Projector", "cells": c, "named_ranges": {}}


def moves_tab(oat, b_on):
    c = {"A1": "What moves LTV/CAC: one input at a time, and across the 1,000 futures (pasted from the plan's model)",
         "A2": (f"Left: each input set to the low and then the high end of its Monte Carlo range, everything else at the base "
                f"(online LTV/CAC {b_on['ltvcac']:.2f}×, paid back in month {b_on['pay']}). Sorted by how far it moves the online saver. "
                "Right: rank correlation with LTV/CAC over the 1,000 futures (all inputs moving at once): near 0 = it hardly matters. "
                "To see one live, type its low or high into Inputs.")}
    head = ["Input", "Low", "Likely", "High", "Online LTV/CAC at low", "Online LTV/CAC at high", "Swing (high − low)",
            "Online pays back at low (month)", "at high", "Doorstep LTV/CAC at low", "Doorstep LTV/CAC at high",
            "Rank correlation with online LTV/CAC (1,000 futures)", "Rank correlation with doorstep LTV/CAC"]
    for j, h in enumerate(head):
        c[f"{tc.col_name(j + 1)}4"] = h
    data = []
    for r in oat:
        def nn(v):
            return round(v) if abs(v) >= 1000 else round(v, 4)
        data.append([r["label"], nn(r["low"]), nn(r["likely"]), nn(r["high"]), round(r["on_lo"], 2), round(r["on_hi"], 2),
                     round(r["on_hi"] - r["on_lo"], 2), r["pay_lo"], r["pay_hi"], round(r["door_lo"], 2), round(r["door_hi"], 2),
                     round(r["rank_on"], 3), round(r["rank_door"], 3)])
    return {"title": "What moves it", "cells": c, "named_ranges": {}, "_data": data}


def sources_tab(all_text):
    ids = sorted(set(re.findall(r"\b([A-Z]{2,3}-\d{2,3})\b", all_text)) | {f"XF-{i:02d}" for i in range(1, 25)})
    found = {}
    for f in sorted((ROOT / "research").glob("*.csv")):
        for r in csv.DictReader(f.open()):
            i = (r.get("id") or "").strip()
            if i in ids and i not in found:
                claim = r.get("claim") or r.get("metric") or r.get("answer") or r.get("question") or ""
                if f.name.startswith("xs_funnel"):
                    claim = f"{r.get('topic', '')}: {r.get('metric', '')}"
                found[i] = [i, scrub(claim), scrub(f"{r.get('value', '')} {r.get('unit', '')}".strip()),
                            scrub(r.get("source_title") or r.get("source") or ""), r.get("source_url") or r.get("url") or "",
                            r.get("as_of") or r.get("source_date") or r.get("date") or "", scrub(r.get("note") or r.get("notes") or "")]
    for i in ids:
        if i in found and i.startswith("IV-"):
            found[i][3] = "Interview with a doorstep savings agent, 15 Oct 2026"
        if i in found and ("linkedin" in found[i][4].lower() or "Saket" in found[i][3]):
            found[i][3], found[i][4] = "Conversation with a competitor's growth lead, 18 Oct 2026", ""
    cut = lambda z, n: z if len(z) <= n else z[:n - 1].rstrip() + "…"
    SRC_FIX = [("0.3% used in model/stayer.py", ""), ("(market_benchmarks.csv MAC-03)", "(MAC-03)"),
               ("Derived from tri_costs TC-25 (YourStory Dec-2025) and market_benchmarks SAV-01 (Entrackr FY25)", "Derived from YourStory (Dec 2025) and Entrackr (FY25)"),
               ("not the janta 6 to 10", "not an existing agent book's 6 to 10"), ("per tri_costs TC-29 (unverified secondary)", "(TC-29, unverified secondary)")]

    def fx(z):
        for a_, b_ in SRC_FIX:
            z = z.replace(a_, b_)
        return z
    data = [[r_[0], fx(cut(r_[1], 260)), cut(r_[2], 80), fx(cut(r_[3], 140)), r_[4], r_[5], fx(cut(r_[6], 160))] for r_ in (found[i] for i in ids if i in found)]
    missing = [i for i in ids if i not in found]
    c = {"A1": "Sources: every ID quoted on Inputs, and the loan-marketplace research of 21 Oct 2026",
         "A2": "Inputs marked 'our judgement' or 'founder's judgement' have no outside source; they say so on Inputs.",
         "A4": "ID", "B4": "What it says", "C4": "Value", "D4": "Source", "E4": "Link", "F4": "As of", "G4": "Note"}
    txt = json.dumps(data, ensure_ascii=False)
    for bad in ("Bueno", "BetterPlace", "Arvinder", "Saket"):
        assert bad.lower() not in txt.lower(), bad
    assert not re.search(r"\b[6-9]\d{9}\b", txt), "phone number in sources"
    return {"title": "Sources", "cells": c, "named_ranges": {}, "_data": data}, missing


def readme_tab(checks, oat_n):
    lines = [
        "SaveMore: LTV/CAC model (21 Oct 2026)",
        "What one saver won is worth, with every assumption visible: the investor plan's own model, rebuilt here cell by cell.",
        "",
        "THE ANSWER",
        "LTV-CAC: the waterfall (cost to win → each revenue line → serving → net), LTV/CAC over 5 and 8 years, the payback month, for an online and a doorstep saver; and the same across 1,000 futures.",
        "",
        "HOW TO USE IT",
        "1. Change any BLUE cell on Inputs: LTV-CAC, Saver, Engine and Products recalculate. Grey cells are worked out; do not type there.",
        "2. Projector: ask the 1,000 futures any question: the median, any percentile, the share above a line, for any column, with up to three filters (e.g. only futures where fewer than 20% apply for a loan).",
        "3. What moves it: every drawn input at the low and high end of its range, one at a time, sorted by how much it moves LTV/CAC.",
        "",
        "TABS",
        "LTV-CAC: the answer, live, next to the plan model's values (the gap column should read 0).",
        "Projector: live questions to the Monte Carlo.",
        "Inputs: every assumption, its value, unit, range, Monte Carlo treatment, source and reason; the 'Name in formulas' column is the named range the formulas use.",
        "Saver: one saver won, months 1–96: still saving, deposits, balance, each revenue line, serving, and the cumulative ₹ after the cost to win.",
        "Engine: the per-saver machinery for the fund, personal and business loans (first, repeat and top-up loans) and cards.",
        "Products: the per-saver machinery for 19 cross-sell products (7 insurance, 5 other loans, 7 others).",
        "Monte Carlo: 1,000 futures (values). What moves it: one at a time and rank correlations (values). Sources: the research behind the inputs.",
        "",
        "DEFINITIONS",
        "Saver won = someone who starts saving (not a sign-up). Cost to win = all-in marketing and onboarding per saver won.",
        "Revenue = what we are paid: our trail on the fund balance, DSA payouts on loans, referral fees, insurance commission (our broker partner's share), card fees and product commissions. The app never holds the money.",
        "LTV = revenue less serving cost (support + tech per saver still saving) over 5 years, undiscounted (8 years alongside). LTV/CAC = LTV ÷ cost to win. Pays back = the first month cumulative revenue less serving reaches the cost to win.",
        "A saver who joins in the business's month 1: their take-up and approval factors grow with the business's years (held after year 5); a saver who joins later starts higher, so this is the cautious case.",
        "Loans: offers reach every KYC'd user who came with the saver (online 2.5 per saver won, doorstep 1); a KYC'd user who never saves stays reachable for as long as the saver keeps saving.",
        "Not in this view: the team, office and brand (company costs, in our business-plan model), the 10% contingency, the 2-month wait for fees to arrive, tax.",
        "",
        "CHECKS",
        f"The sheet's formulas were replayed by a formula interpreter and match the plan's model at the base and at {len(checks) // 2 - 1} Monte Carlo futures: "
        "LTV/CAC to 6 decimals, the payback month exactly, every monthly line to 1 part in 100 million.",
        f"The Monte Carlo uses the same 1,000 futures as the company Monte Carlo, so each future's LTV/CAC sits next to that future's profit month. {oat_n} inputs are drawn.",
    ]
    return {"title": "README", "cells": {f"A{i + 1}": t for i, t in enumerate(lines)}, "named_ranges": {}, "_n": len(lines)}


# --------------------------------------------------------------------------------------------------------------- payloads
def runs(pats):
    """[(first col, last col, pattern)] for consecutive equal patterns (1-based columns)."""
    out = []
    for j, p_ in enumerate(pats, 1):
        if out and out[-1][2] == p_ and out[-1][1] == j - 1:
            out[-1][1] = j
        else:
            out.append([j, j, p_])
    return out


def row_runs(d):
    out = []
    for r in sorted(d):
        if out and out[-1][2] == d[r] and out[-1][1] == r - 1:
            out[-1][1] = r
        else:
            out.append([r, r, d[r]])
    return out


def grid(sid, r1, c1, r2, c2):
    return {"sheetId": sid, "startRowIndex": r1 - 1, "endRowIndex": r2, "startColumnIndex": c1 - 1, "endColumnIndex": c2}


def a1grid(sid, ref):
    p = tc.parse_a1(ref)
    return grid(sid, *(p if len(p) == 4 else (*p, *p)))


def rgb(c):
    return {"red": c[0], "green": c[1], "blue": c[2]}


def fmt_req(sid, ref, pattern):
    return {"repeatCell": {"range": a1grid(sid, ref), "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": pattern}}},
                           "fields": "userEnteredFormat.numberFormat"}}


def style_req(sid, ref, bold=False, color=None, fill=None, wrap=False, italic=False, size=None):
    f, fields = {}, []
    tf = {}
    if bold:
        tf["bold"] = True
        fields.append("userEnteredFormat.textFormat.bold")
    if italic:
        tf["italic"] = True
        fields.append("userEnteredFormat.textFormat.italic")
    if size:
        tf["fontSize"] = size
        fields.append("userEnteredFormat.textFormat.fontSize")
    if color:
        tf["foregroundColorStyle"] = {"rgbColor": rgb(color)}
        fields.append("userEnteredFormat.textFormat.foregroundColorStyle")
    if tf:
        f["textFormat"] = tf
    if fill:
        f["backgroundColorStyle"] = {"rgbColor": rgb(fill)}
        fields.append("userEnteredFormat.backgroundColorStyle")
    if wrap:
        f["wrapStrategy"] = "WRAP"
        fields.append("userEnteredFormat.wrapStrategy")
    return {"repeatCell": {"range": a1grid(sid, ref), "cell": {"userEnteredFormat": f}, "fields": ",".join(fields)}}


def width_req(sid, c1, c2, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": c1 - 1, "endIndex": c2},
                                          "properties": {"pixelSize": px}, "fields": "pixelSize"}}


def freeze_req(sid, rows, cols=0):
    return {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols}},
                                      "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}


def dense(title, cells, r1, r2, c1, c2):
    rows = [[cells.get(f"{tc.col_name(c)}{r}") for c in range(c1, c2 + 1)] for r in range(r1, r2 + 1)]
    return {"range": f"'{title}'!{tc.col_name(c1)}{r1}:{tc.col_name(c2)}{r2}", "formulas": rows}


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    L = inputs_list()
    inp = inputs_sheet(L)
    eng, prd, sav = engine_tab(), products_tab(), saver_tab()
    tabs = {"Engine": eng, "Products": prd, "Saver": sav}
    base = base_params()
    b_on, b_dr, _ = evaluate(base, door_cac=False)
    assert abs(b_on["ltvcac"] - op.ltv_view(op.saver_inputs(), op.CAC)[2]["LTV/CAC 60m"]) < 0.006, b_on["ltvcac"]
    py = {"on": b_on, "door": b_dr}
    sheets = [inp, expand(eng, tabs), expand(prd, tabs), expand(sav, tabs), answer_tab(sav, py)]
    print("rows on Inputs", inp["_last"], "| columns: Engine", len(eng.order), "Products", len(prd.order), "Saver", len(sav.order))
    # Monte Carlo + one at a time
    rows = mc_run()
    drv = drivers(rows)
    oat, b_on2, _ = one_at_a_time(drv)
    assert abs(b_on2["ltvcac"] - b_on["ltvcac"]) < 1e-9
    # the formula check: base + five futures (spread across the LTV/CAC range)
    order = np.argsort([r["on_ltv60"] for r in rows])
    picks = [int(order[q]) for q in (20, 250, 500, 750, 980)]
    cases = [("base (21 Oct inputs)", base, DOOR_CAC)] + [(f"future {i + 1}", {k: rows[i][k] for k in ALLSPEC}, rows[i]["door_cac"]) for i in picks]
    mc, proj, mov = mc_tab(rows), projector_tab(), moves_tab(oat, b_on)
    allsheets = sheets + [mc, proj]
    chk = check(allsheets, sav, cases)
    for r in chk:
        print(r)
    text = json.dumps([inp["cells"]], ensure_ascii=False)
    src, missing = sources_tab(text)
    print("source IDs not found in research/:", missing)
    rd = readme_tab(chk, len(drawn_keys()))
    bad = re.compile(r"operator|Bachatt|Engine (rule|cap|convention)|pool's history|street model|earlier model|\bRs\b", re.I)
    for sh in sheets + [mc, proj, mov, src, rd]:            # investor wording on every text cell; formulas must not need it
        for c, v in sh["cells"].items():
            if isinstance(v, str):
                if not v.startswith("="):
                    sh["cells"][c] = v = plain(v)
                assert not bad.search(v), (sh["title"], c, v[:80])
    # tables
    def wcsv(name, recs):
        with (T / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(recs[0]))
            w.writeheader()
            w.writerows(recs)
    wcsv("ltv_book_check.csv", chk)
    wcsv("ltv_mc_draws.csv", [{k: r[k] for k in ["draw"] + [k for k, _ in MC_IN] + [k for k, _ in MC_OUT]} for r in rows])
    wcsv("ltv_one_at_a_time.csv", oat)
    wcsv("ltv_drivers.csv", [{"key": d["key"], "label": label_of(d["key"]), "rank corr online LTV/CAC": round(d["on"], 3),
                              "rank corr online payback": round(d["pay"], 3), "rank corr doorstep LTV/CAC": round(d["door"], 3)} for d in drv])
    wcsv("ltv_inputs.csv", [{"group": g, "key": k, "label": lab, "value": v, "unit": u, "mc": (ALLSPEC.get(m) if m else None), "source": s, "why": w}
                            for g, k, lab, v, u, m, s, w, _f in L])
    summ = []
    for k, lab in MC_OUT:
        v = np.array([r[k] for r in rows])
        summ.append({"measure": lab, "P10": round(float(np.percentile(v, 10)), 3), "P50": round(float(np.median(v)), 3),
                     "P90": round(float(np.percentile(v, 90)), 3), "mean": round(float(v.mean()), 3)})
    on = np.array([r["on_ltv60"] for r in rows])
    pay = np.array([r["on_pay"] for r in rows])
    dl = np.array([r["door_ltv60"] for r in rows])
    summ.append({"measure": "share online LTV/CAC >= 3", "P50": round(float((on >= 3).mean()), 3)})
    summ.append({"measure": "share online LTV/CAC < 1", "P50": round(float((on < 1).mean()), 3)})
    summ.append({"measure": "share online paid back <= 24 months", "P50": round(float((pay <= 24).mean()), 3)})
    summ.append({"measure": "share doorstep LTV/CAC >= 3", "P50": round(float((dl >= 3).mean()), 3)})
    wcsv("ltv_mc_summary.csv", [{k: s.get(k, "") for k in ("measure", "P10", "P50", "P90", "mean")} for s in summ])
    for s in summ:
        print(s)
    print("top drivers:", [(d["key"], round(d["on"], 2)) for d in drv[:10]])
    # ------------------------------------------------------------------ payloads
    sid = TABS
    setup = [{"updateSheetProperties": {"properties": {"sheetId": 0, "title": "README", "gridProperties": {"rowCount": 60, "columnCount": 4}},
                                        "fields": "title,gridProperties.rowCount,gridProperties.columnCount"}}]
    sizes = {"LTV-CAC": (40, 12), "Projector": (1005, 16), "Inputs": (inp["_last"] + 5, 11), "Saver": (R1 + 2, len(sav.order)),
             "Engine": (R1 + 2, len(eng.order)), "Products": (R1 + 2, len(prd.order)), "Monte Carlo": (1005, mc["_ncol"]),
             "What moves it": (len(mov["_data"]) + 6, 13), "Sources": (len(src["_data"]) + 6, 7)}
    colors = {"LTV-CAC": NAVY, "Projector": TEAL, "Inputs": BLUE, "Saver": SLATE, "Engine": SLATE, "Products": SLATE, "Monte Carlo": AMBER,
              "What moves it": AMBER, "Sources": GREY}
    for t, (nr, ncol) in sizes.items():
        setup.append({"addSheet": {"properties": {"sheetId": sid[t], "title": t, "index": list(TABS).index(t),
                                                  "gridProperties": {"rowCount": nr, "columnCount": ncol}, "tabColorStyle": {"rgbColor": rgb(colors[t])}}}})
    names = []
    for sh in [inp, mc]:
        for nm, ref in sh["named_ranges"].items():
            names.append({"addNamedRange": {"namedRange": {"name": nm, "range": a1grid(sid[sh["title"]], ref)}}})
    (out / "lb_setup.json").write_text(json.dumps(setup + names, ensure_ascii=False, separators=(",", ":")))
    blocks = [dense("README", rd["cells"], 1, rd["_n"], 1, 1), dense("Inputs", inp["cells"], 1, inp["_last"], 1, 11)]
    for t in (eng, prd, sav):
        sh = next(s for s in sheets if s["title"] == t.title)
        blocks.append(dense(t.title, sh["cells"], 1, R0 + 1, 1, len(t.order)))
    blocks.append(dense("LTV-CAC", sheets[4]["cells"], 1, 30, 1, 9))
    blocks.append(dense("Projector", proj["cells"], 1, 50, 1, 14))
    blocks.append(dense("Monte Carlo", mc["cells"], 1, 4, 1, mc["_ncol"]))
    blocks.append(dense("What moves it", mov["cells"], 1, 4, 1, 13))
    blocks.append(dense("Sources", src["cells"], 1, 4, 1, 7))
    for n, b in enumerate(blocks, 1):
        (out / f"lb_cells_{n:02d}.json").write_text(json.dumps(b, ensure_ascii=False, separators=(",", ":")))
    vals = [("What moves it", 5, mov["_data"]), ("Sources", 5, src["_data"])]
    step = 200
    for i in range(0, len(mc["_data"]), step):
        vals.append(("Monte Carlo", 4 + i, mc["_data"][i:i + step]))
    for n, (t, r, data) in enumerate(vals, 1):
        c0 = 2 if t == "Monte Carlo" else 1
        data = [row[1:] for row in data] if t == "Monte Carlo" else data
        ncol = len(data[0])
        (out / f"lb_vals_{n:02d}.json").write_text(json.dumps({"range": f"'{t}'!{tc.col_name(c0)}{r}:{tc.col_name(c0 + ncol - 1)}{r + len(data) - 1}", "values": data},
                                                                ensure_ascii=False, separators=(",", ":")))
    # copy month 2 down to month 96, then formats and charts
    fin = []
    for t in (eng, prd, sav):
        s = sid[t.title]
        fin.append({"copyPaste": {"source": grid(s, R0 + 1, 1, R0 + 1, len(t.order)), "destination": grid(s, R0 + 2, 1, R1, len(t.order)),
                                  "pasteType": "PASTE_NORMAL"}})
        pats = [FMT.get(fm, {"n4": "0.0000", "n5": "0.00000", "rs3": "#,##0.000"}.get(fm, "0.000")) for *_x, fm in t.order]
        if t.title == "Products":                         # one format for every product column: shares and ₹ both read at 4 decimals
            pats = ["0"] + ["#,##0.0000"] * (len(pats) - 1)
        for j1, j2, pat in runs(pats):
            fin.append(fmt_req(s, f"{tc.col_name(j1)}{R0}:{tc.col_name(j2)}{R1}", pat))
        fin += [style_req(s, "A1:A1", bold=True, size=12), style_req(s, f"A3:{tc.col_name(len(t.order))}4", bold=True, wrap=True),
                freeze_req(s, 4, 1), width_req(s, 2, len(t.order), 118), width_req(s, 1, 1, 80)]
        bands = {}
        for j, (key, band, *_r) in enumerate(t.order, 1):
            if band:
                bands.setdefault(band, []).append(j)
        for k, (band, js) in enumerate(bands.items()):
            fin.append(style_req(s, f"{tc.col_name(js[0])}3:{tc.col_name(js[-1])}3", fill=(0.93, 0.95, 0.98) if k % 2 == 0 else (0.98, 0.96, 0.92)))
    s = sid["Inputs"]
    fm_of = dict(inp["_fmt"])
    UNI = {"pct": "0.0##%", "pct2": "0.0##%", "pct3": "0.0##%", "rs": "#,##0", "rs2": "#,##0.00"}
    seq, cur = {}, None
    for r in range(4, inp["_last"] + 1):                 # group-header rows inherit the format above (their C:G cells are empty)
        if r in fm_of:
            cur = UNI.get(fm_of[r])
        seq[r] = cur
    for r1, r2, pat in row_runs(seq):
        if pat:
            fin.append(fmt_req(s, f"C{r1}:G{r2}", pat))
    fin.append(style_req(s, f"C4:C{inp['_last']}", color=BLUE, fill=(1.0, 0.98, 0.85)))
    for r1, r2, _p in row_runs({r: 1 for r in inp["_grey"]}):
        fin.append(style_req(s, f"B{r1}:C{r2}", color=GREY, italic=True, fill=(1, 1, 1)))
    for r in inp["_bold"]:
        fin.append(style_req(s, f"A{r}:K{r}", bold=True, fill=(0.93, 0.95, 0.98)))
    fin += [style_req(s, "A1:A1", bold=True, size=12), style_req(s, "A3:K3", bold=True, wrap=True), style_req(s, f"I4:J{inp['_last']}", wrap=True),
            freeze_req(s, 3, 2), width_req(s, 1, 1, 24), width_req(s, 2, 2, 330), width_req(s, 3, 3, 90), width_req(s, 4, 4, 150),
            width_req(s, 5, 8, 80), width_req(s, 9, 10, 380), width_req(s, 11, 11, 150)]
    s = sid["LTV-CAC"]
    fin += [fmt_req(s, "B5:I16", "#,##0;-#,##0;0"), fmt_req(s, "B17:I17", '0.00"×"'), fmt_req(s, "B18:I18", "0"), fmt_req(s, "B19:I20", "0%"),
            fmt_req(s, "B21:I21", "#,##0"), fmt_req(s, "B25:D25", '0.00"×"'), fmt_req(s, "B27:D27", '0.00"×"'), fmt_req(s, "B26:D26", "0"),
            fmt_req(s, "B28:D28", "0"), fmt_req(s, "E25:G28", "0%"),
            style_req(s, "A1:A1", bold=True, size=14), style_req(s, "A2:I2", wrap=True), style_req(s, "A4:I4", bold=True, wrap=True),
            style_req(s, "A13:I13", bold=True), style_req(s, "A17:I18", bold=True, fill=(0.93, 0.97, 0.96)), style_req(s, "G5:H21", color=GREY),
            style_req(s, "A23:A23", bold=True), style_req(s, "A24:G24", bold=True, wrap=True), width_req(s, 1, 1, 400), width_req(s, 2, 9, 120),
            {"mergeCells": {"range": a1grid(s, "A2:I2"), "mergeType": "MERGE_ALL"}},
            {"updateDimensionProperties": {"range": {"sheetId": s, "dimension": "ROWS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 64}, "fields": "pixelSize"}},
            freeze_req(s, 4)]
    on_cum, door_cum = sav.cols["on.cum"], sav.cols["door.cum"]
    src_ = lambda sh, ref: {"sourceRange": {"sources": [a1grid(sid[sh], ref)]}}
    fin.append({"addChart": {"chart": {"spec": {"title": "One online saver won: first 5 years (₹, live)", "waterfallChart": {
        "domain": {"data": src_("LTV-CAC", "A5:A12")},
        "series": [{"data": src_("LTV-CAC", "B5:B12"), "customSubtotals": [{"subtotalIndex": 7, "label": "Net, 5 years", "dataIsSubtotal": False}],
                    "positiveColumnsStyle": {"color": rgb(NAVY)}, "negativeColumnsStyle": {"color": rgb(TEAL)}, "subtotalColumnsStyle": {"color": rgb(SLATE)}}],
        "stackedType": "STACKED", "connectorLineStyle": {"width": 1}}},
        "position": {"overlayPosition": {"anchorCell": {"sheetId": s, "rowIndex": 31, "columnIndex": 0}, "widthPixels": 640, "heightPixels": 360}}}}})
    fin.append({"addChart": {"chart": {"spec": {"title": "When a saver pays back: cumulative ₹ after the cost to win (live)", "basicChart": {
        "chartType": "LINE", "legendPosition": "BOTTOM_LEGEND", "headerCount": 1,
        "axis": [{"position": "BOTTOM_AXIS", "title": "Months after the saver joins"}, {"position": "LEFT_AXIS", "title": "₹ per saver won"}],
        "domains": [{"domain": src_("Saver", f"A4:A{R1}")}],
        "series": [{"series": src_("Saver", f"{on_cum}4:{on_cum}{R1}"), "targetAxis": "LEFT_AXIS", "color": rgb(NAVY)},
                   {"series": src_("Saver", f"{door_cum}4:{door_cum}{R1}"), "targetAxis": "LEFT_AXIS", "color": rgb(AMBER)}]}},
        "position": {"overlayPosition": {"anchorCell": {"sheetId": s, "rowIndex": 31, "columnIndex": 3}, "widthPixels": 640, "heightPixels": 360}}}}})
    s = sid["Projector"]
    ncol = mc["_ncol"]
    head_rng = f"='Monte Carlo'!$A$3:${tc.col_name(ncol)}$3"
    for ref in ("B4:B4", "B6:B8"):
        fin.append({"setDataValidation": {"range": a1grid(s, ref), "rule": {"condition": {"type": "ONE_OF_RANGE", "values": [{"userEnteredValue": head_rng}]},
                                                                             "strict": False, "showCustomUi": True}}})
    fin += [style_req(s, "A1:A1", bold=True, size=14), style_req(s, "A2:H2", wrap=True), {"mergeCells": {"range": a1grid(s, "A2:H2"), "mergeType": "MERGE_ALL"}},
            {"updateDimensionProperties": {"range": {"sheetId": s, "dimension": "ROWS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 52}, "fields": "pixelSize"}},
            style_req(s, "B4:D10", color=BLUE, fill=(1.0, 0.98, 0.85)), style_req(s, "A12:B12", bold=True), style_req(s, "A13:B25", fill=(0.93, 0.97, 0.96)),
            fmt_req(s, "B13:B13", "0"), fmt_req(s, "B14:B23", "#,##0.00"), fmt_req(s, "B24:B25", "0.0%"), fmt_req(s, "A31:B50", "#,##0.00"), style_req(s, "A30:C30", bold=True),
            style_req(s, "A29:A29", bold=True), style_req(s, "J3:K3", bold=True, wrap=True), style_req(s, "J4:K1003", color=GREY),
            style_req(s, "M3:M3", bold=True), style_req(s, "M4:M15", wrap=True), fmt_req(s, "N4:N15", "0.00"),
            fmt_req(s, "N5:N6", "0%"), fmt_req(s, "N8:N8", "0%"), fmt_req(s, "N11:N11", "0%"), style_req(s, "E4:E4", color=(0.8, 0.1, 0.1), bold=True),
            width_req(s, 1, 1, 300), width_req(s, 2, 4, 230), width_req(s, 5, 9, 60), width_req(s, 10, 11, 110), width_req(s, 12, 12, 20),
            width_req(s, 13, 13, 430), width_req(s, 14, 14, 90)]
    fin.append({"addChart": {"chart": {"spec": {"title": "How the answer spreads across the futures that pass the filters", "basicChart": {
        "chartType": "COLUMN", "legendPosition": "NO_LEGEND",
        "axis": [{"position": "BOTTOM_AXIS", "title": "Value (bin start)"}, {"position": "LEFT_AXIS", "title": "Futures"}],
        "domains": [{"domain": src_("Projector", "A31:A50")}], "series": [{"series": src_("Projector", "C31:C50"), "targetAxis": "LEFT_AXIS", "color": rgb(TEAL)}]}},
        "position": {"overlayPosition": {"anchorCell": {"sheetId": s, "rowIndex": 17, "columnIndex": 12}, "widthPixels": 560, "heightPixels": 320}}}}})
    s = sid["Monte Carlo"]
    fin += [style_req(s, "A1:A1", bold=True, size=12), style_req(s, f"A3:{tc.col_name(ncol)}3", bold=True, wrap=True, fill=(0.93, 0.95, 0.98)),
            freeze_req(s, 3, 1), width_req(s, 1, 1, 60), width_req(s, 2, ncol, 110),
            style_req(s, f"{tc.col_name(2 + len(MC_IN))}3:{tc.col_name(ncol)}3", fill=(0.93, 0.97, 0.96)),
            fmt_req(s, f"B4:{tc.col_name(1 + len(MC_IN))}1003", "#,##0.000")]
    for j, (k, _h) in enumerate(MC_IN):
        cc = tc.col_name(2 + j)
        fin.append(fmt_req(s, f"{cc}4:{cc}1003", "#,##0" if k in ("on_daily", "cac", "on_ticket") else ("0.00" if k == "on_reach" else "0.0%")))
    for j, (k, _h) in enumerate(MC_OUT):
        cc = tc.col_name(2 + len(MC_IN) + j)
        fin.append(fmt_req(s, f"{cc}4:{cc}1003", "0.00" if k in ("on_ltv60", "on_ltv96", "door_ltv60", "co_money") else "#,##0"))
    s = sid["What moves it"]
    fin += [style_req(s, "A1:A1", bold=True, size=12), style_req(s, "A2:M2", wrap=True), {"mergeCells": {"range": a1grid(s, "A2:M2"), "mergeType": "MERGE_ALL"}},
            {"updateDimensionProperties": {"range": {"sheetId": s, "dimension": "ROWS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 52}, "fields": "pixelSize"}},
            style_req(s, "A4:M4", bold=True, wrap=True, fill=(0.93, 0.95, 0.98)), freeze_req(s, 4, 0), width_req(s, 1, 1, 380), width_req(s, 2, 13, 105),
            fmt_req(s, f"E5:G{len(mov['_data']) + 4}", "0.00"), fmt_req(s, f"J5:K{len(mov['_data']) + 4}", "0.00"),
            fmt_req(s, f"L5:M{len(mov['_data']) + 4}", "0.00")]
    s = sid["Sources"]
    fin += [style_req(s, "A1:A1", bold=True, size=12), style_req(s, "A4:G4", bold=True, fill=(0.93, 0.95, 0.98)), freeze_req(s, 4, 1),
            width_req(s, 1, 1, 70), width_req(s, 2, 2, 380), width_req(s, 3, 3, 160), width_req(s, 4, 4, 260), width_req(s, 5, 5, 260),
            width_req(s, 6, 6, 90), width_req(s, 7, 7, 300), style_req(s, f"B5:G{len(src['_data']) + 4}", wrap=True)]
    s = 0
    fin += [style_req(s, "A1:A1", bold=True, size=14), width_req(s, 1, 1, 1100), style_req(s, f"A2:A{rd['_n']}", wrap=True)]
    for i, t in enumerate(rd["cells"].values()):
        if t.isupper() and t:
            fin.append(style_req(s, f"A{i + 1}:A{i + 1}", bold=True, color=NAVY))
    (out / "lb_finish.json").write_text(json.dumps(fin, ensure_ascii=False, separators=(",", ":")))
    spec = {"sheet_id": SHEET_ID, "sheets": [{k: v for k, v in s_.items() if not k.startswith("_")} for s_ in allsheets + [mov, src, rd]]}
    (T / "ltv_book_spec.json").write_text(json.dumps(spec, ensure_ascii=False))
    nf = sum(1 for s_ in allsheets for v in s_["cells"].values() if isinstance(v, str) and v.startswith("="))
    print(f"formulas in the full workbook: {nf}; payload files in {out}: {sorted(p.name for p in out.glob('lb_*'))}")
    print("sizes KB:", {p.name: round(p.stat().st_size / 1024, 1) for p in sorted(out.glob('lb_*'))})


if __name__ == "__main__":
    main()

"""Every model input as a proposed distribution, to agree with the operator BEFORE any model or deck is rebuilt.

Operator, 16 Oct 2026: "we need to first agree on assumptions first - how many loans, everything is a distribtuion.
Lets first finalize the distribution"; "create a slide that should show those distribution. every take rate, every
thing"; "build a model of monthly cohort, their retention and saving rate and every detail"; "cohort level modeling
needs to happen with Monte Carlo around input assumptions"; on losses: "our worst case would be paytm default rates
because of two things - 1. these are genuine self selected savers 2. and our agent also helps us collect back as this
guy knows everything about the customer"; "Collection fee on collection done on high dpd buckets"; "Have health
insurance life insurance etc whatever the fuck we can cross sell".

Briefs (later ones win where they overlap): story/BRIEF_distributions_2026-10-16.md, COHORT_INPUTS_2026-10-16.md,
COHORT_INPUTS_addendum_crosssell_dpd_2026-10-16.md, COHORT_INPUTS_addendum2_research_2026-10-16.md, plus the operator's
taps of 16 Oct (debt fund; still saving at month 12 likely 55%; card share 3%; research approved and done).
Key names are used exactly: the cohort Monte Carlo reads tables/dist_proposal_v1.csv by key, shape, low, likely, high.

kind: distribution (draw it) | decision (fixed: shape=fixed, low = likely = high, except `horizon`: 36 = low, 60 = likely
= high, run both) | reference (trail_liquid: the fund not chosen) | legacy (other: the v2 single ₹63 line, legacy=True only).

Writes
  tables/dist_proposal_v1.csv   one row per input (shape, low / likely / high, sampled p10 / p50 / p90 / mean, evidence)
  tables/dist_derived_v1.csv    20,000 independent draws, fixed seed: loans, fee per loan, collections by bucket (implied
                                shares reaching each bucket and fees per loan made), cross-sell money per active saver a year by
                                product, marketplace money per 100 active savers, the retention curve and deposits by age
  Assumptions_to_agree.pdf      A4 landscape, the QR_moat_story.pdf look (build_qr_visual.py helpers, Chrome headless)
The HTML that Chrome prints goes to $DIST_OUT (default: the system temp folder), never into the project.

Reads, never edits: tables/xs_inputs_v2.csv (last deck's middle values), story_unit.csv, agent3_survival.csv,
pilot_rules_v2.csv, distributions.csv, agent_npv.EVIDENCE_LOANS. Every evidence id is checked against research/*.csv (or the
named research/*.md) with a token from its row.

Shapes. triangular(low, likely, high); pert(low, likely, high), lambda 4; lognormal: low = P5, likely = median, high = P95;
beta: low = P5, likely = mean, high = P95 (as tables/distributions.csv).
Retention curve: months 1-3 drop h1 = 1 - r3^(1/3); months 4-12 h2 = 1 - (r12/r3)^(1/9); then churn_late. r12 is capped
at r3 in a draw where r12 > r3 (the share is printed).
Collections (addendum 3, replacing addendum 2's bucket chain): share of loans that ever go 90+ days bad p90 = loss / (owed x
(1 - recovered)), about 9.7% at the likely values (checked against NG-015's 10.2% and MAC-03's 3.6%); fees per loan made =
early_cured x fee_early (~9 months after the loan) + p90 x recovered x fee_b3 (~18 months after); check early_cured + p90 <= 50%.
Insurance first-year commissions are capped at IRDAI's draft caps for open-shelf distributors (addendum 3).
Cross-sell money per active saver a year, "once holdings settle": insurance h = t / (1 - r + t) holders, money =
(1 - h) t P c1 + h r P c2; SIP h = t / (1 - s + t), balance = 12 m (s / (1 - s) + 0.5), money = h x balance x trail; gold
h = t / (1 - b + t), money = h x 12 m x 2.4%; Choti t x 500 x survive24 / 2 and NPS t x 200 (one-offs, as XO-39); FD,
recharge, bills, other loans t x ticket x fee. "First year" = t x ticket x first-year fee (the XO-39 method, for the old ₹63).

AGREED with the operator, 16 Oct 2026 (taps; later: "the marketplace opens as soon as possible. Simple. It's not at our cost.",
so marketplace_from = 1 and proven_after = 6 is kept as a superseded row; every take-up applies to active savers from
month 1): still saving at month 12 likely 55%; sign-ups 30 a month (pert 20 / 30 / 45; revised from 60 after the sweep);
a debt fund at 0.35%; card share 3%; bad years linked (Gaussian copula, rho -0.5 between loss and each of approved_first and
approved_repeat, so every draw here is linked); 25% left in at term end; IRDAI's draft caps; the research gaps filled.
tables/dist_agreed_v1.csv = the proposal rows + corr_approved_loss (kind=decision, -0.5) + agreed_on: the cohort model reads it.
Assumptions_to_agree.pdf is the agreed version, also copied to Assumptions_agreed.pdf.
Operator, later on 16 Oct: "month 1 for marketplace can have low take up rates and approval rates but business starts from
there. Hook is high savings rate in debt funds that we offer" -> early_takeup_mult, early_approval_mult and fund_return
(Our judgement; OK'd by the operator 16 Oct).
Operator: "It's a bank savings account rate at public sector bank. Those rates" -> janta_rate, a reference row (not an NPV input):
the fund page shows what his money earns a year (janta deposit, a liquid fund, our debt fund) and the gain on ₹350 a day.
Addendum 4 (operator: "take up rates and sign ups and approva rates and loan size also go up over time on our pool as we gather
more history and repayment of this customer"; OK'd "OK as proposed"): signup_growth, takeup_growth, approval_growth,
ticket_growth, topup_share, topup_size. Year y multiplier = (1 + g)^(y - 1), on top of the agreed rates and the early-months
factors; caps apply after multiplying (in each row's note).
After an adversarial review (taps, 16 Oct): support_cost becomes a distribution (₹0 / 5 / 15 an active saver a month, "Your
number"); ticket widens to ₹25,000 / 2.5 lakh / 5 lakh ("range 25k upto 5 lacs"), ticket_growth's cap stays ₹5 lakh.
Round 5 (story/CHANGES_round5_pnl_housing_2026-10-16.md): discount = 0 (cumulative P&L; the VC applies their own discount);
housing loans loan_home_* and loan_lap_* (take-up x approval x ticket x fee, once per saver, no collections, no ticket growth);
decision rows cash_route (agent -> the fund's collection account + reconciliation: needs a legal opinion) and managers (founder).
Round 6 (story/CHANGES_round6_2026-10-16.md): loan_home_takeup 0.5 / 1.5 / 3% ("Family income counts"); cash_cover (fidelity and
cash-in-transit insurance, per agent a month); ins_partner_share (insurance commissions reach us through a broker partner);
decision rows saver_fee = 0 ("No fee") and licences = partners.
Round 7 (story/CHANGES_round7_agent_pay_2026-10-16.md): agent_balance_pay, 0.25% a year of his savers' balance in company months
1-60 (likely = high), 0.10% from month 61 (low), on top of the ₹20,000 salary; the engine's cost line is cost_incentive.
Round 8 (story/CHANGES_round8_rebase_omnichannel_2026-10-17.md; practitioner evidence PR-01): signups_run 60 / 100 / 150 a month;
signup_decline_y5 (sign-ups fall to this share of the year-1 level by month 49); online_lead_share and lead_cost (bought online
leads, served offline by the agent); signup_growth superseded (fixed 0); decision row channel (online + street, served offline).
Round 9 (story/CHANGES_round9_fee_ramp_2026-10-17.md): fee is a DSA's rate at the start (1.0 / 1.75 / 2.5%); the fee in company
month t = fee x (1 + (fee_mult_end - 1) x (t - 1) / 59), with fee_mult_start = 1.0 and fee_mult_end = 1.5 (fixed, month 60).
Round 10 (story/CHANGES_round10_company_base_2026-10-17.md): incentive_cap (the balance pay is capped at ₹10,000 a month per agent;
the salary and the cap rise 7% a year) and the company plan as decision rows: fleet_plan, seed, series_a, central_team.
The final base plan (30% on book): every row of tables/base_inputs.csv not already here is added under its own key (BASE_MAP:
cities, fleet path, central-team pay, costs and finance, the NBFC from month 30, round rules, valuation lenses, model settings),
as fixed decision rows, except the addressable pool (city_pool, a pert distribution). The NBFC's yield and loss reuse `rate` and
`loss`. Conflicts resolved in favour of the final base (tables/base_*): fleet_plan, seed and central_team now follow it; series_a is
superseded by `rounds` (read from tables/base_rounds.csv); incentive_cap stays.
"""
import csv
import html
import math
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from itertools import permutations
from pathlib import Path

import numpy as np
from scipy import stats

import agent_npv as N
import build_qr_visual as V
from build_agent_slides import inr

ROOT = Path(__file__).resolve().parent.parent
T, R = ROOT / "tables", ROOT / "research"
PDF = ROOT / "Assumptions_to_agree.pdf"
PDF_AGREED = ROOT / "Assumptions_agreed.pdf"
AGREED_ON = "2026-10-16"
AGREED_17 = ("signups_run", "signup_decline_y5", "online_lead_share", "lead_cost", "channel", "signup_growth", "fee", "fee_mult_start", "fee_mult_end",
             "incentive_cap", "fleet_plan", "seed", "series_a", "central_team", "rounds")   # round 8, agreed 17 Oct
PENDING = ()       # early_takeup_mult, early_approval_mult, fund_return: OK'd by the operator 16 Oct (taps)
RHO = -0.5                                                    # agreed: approvals fall as losses rise
SEED, DRAWS = 20261016, 20000
INK, MUTED, RULE, PAPER, THEM, US, GREY, BAD, GOOD = V.INK, V.MUTED, V.RULE, V.PAPER, V.THEM, V.US, V.GREY, V.BAD, V.GOOD
FLAT = "#eceae5"

XS = {r["key"]: r for r in csv.DictReader((T / "xs_inputs_v2.csv").open())}
STORY = {r["channel"]: r for r in csv.DictReader((T / "story_unit.csv").open())}
SURV = list(csv.DictReader((T / "agent3_survival.csv").open()))
RULES = {r["key"]: float(r["value"]) for r in csv.DictReader((T / "pilot_rules_v2.csv").open())}
CAC = next(r for r in csv.DictReader((T / "distributions.csv").open()) if r["input"] == "cac_target" and r["segment"] == "ng")
APP_R12 = float(STORY["online"]["still_saving_m12"])          # 0.2415: our app curve at month 12
JANTA_R12 = float(STORY["street"]["still_saving_m12"])        # 0.7230: a janta book losing 8 of 300 a month
APP = [1.0] + [float(r["still_saving_evidence"]) for r in SURV]            # months 0..36
JANTA = [1.0] + [float(r["still_saving_janta_mid"]) for r in SURV]
assert abs(APP[12] - APP_R12) < 1e-9 and abs(JANTA[12] - JANTA_R12) < 1e-9
NEED_R12 = RULES["five_year_breakeven_m12"]                   # 0.369: 5-year NPV break-even on the last deck's inputs
LAST = {k: float(XS[k]["middle"]) for k in XS}
BALANCE = LAST["balance"]                                     # Rs 42,000 held on average over a yearly term
JANTA_LOSS = 8 / 300                                          # a janta book loses 6-10 a month of 200-400 (IV-01, IV-12)
OWED = 0.5                                                    # share of the loan still owed when it goes bad (fixed)
OLD_OTHER = 63.0                                              # XO-39 middle: the v2 single line

YOURS, PUB, GUIDE, OURS = "Your number", "Published", "Industry guide, not verified", "Our judgement"
ROUNDS = list(csv.DictReader((T / "base_rounds.csv").open()))
ROUNDS_TOTAL = sum(float(r["Amount (Rs)"]) for r in ROUNDS) / 1e7
ROUNDS_TEXT = (f"{len(ROUNDS)} rounds per tables/base_rounds.csv: "
               + "; ".join(f"{'seed' if r['Round'] == 'Seed' else r['Round']} ₹{float(r['Amount (Rs)']) / 1e7:,.0f} crore m{r['Month']}" for r in ROUNDS)
               + f"; ₹{ROUNDS_TOTAL:,.0f} crore in total")
HEAD_CENTRAL = [float(v) for v in next(r for r in csv.DictReader((T / "base_headcount.csv").open())
                                       if r["Department"] == "Central team" and r["Role"] == "Total") .values() if v.replace(".", "", 1).isdigit()]
CONFS = (YOURS, PUB, GUIDE, OURS)


# ---------- formatting ----------
def trim(v, d=3):
    return f"{v:.{d}f}".rstrip("0").rstrip(".")


def pc(v):                       # exact: 0.02625 -> 2.625%, 0.0005 -> 0.05%
    return trim(v * 100, 3) + "%"


def pcr(v):                      # sampled values: two significant figures
    x = v * 100
    return (f"{x:.0f}" if x >= 10 else trim(x, 1) if x >= 1 else f"{x:.2g}") + "%"


def rs(v):
    return inr(v)


def rsr(v):                      # sampled rupees, rounded
    step = 1 if v < 100 else 10 if v < 10000 else 100 if v < 100000 else 1000
    return inr(round(v / step) * step)


def lakh(v):
    return f"₹{trim(v / 1e5, 2)} lakh" if v >= 1e5 else inr(v)


def cnt(v):
    return f"{v:,.0f}"


def num(v):
    return trim(v, 1)


# ---------- the inputs ----------
@dataclass
class E:                         # one evidence point: a tick, a range bar or a line we must clear
    v: float
    label: str
    ids: str
    tok: str = ""
    hi: float = None
    who: str = "ev"              # ev (research, blue) | you (operator, ink) | last (our earlier model, grey) | need (red)
    axis: bool = True            # False: evidence for the table only, not drawn on an axis

    def text(self):
        return f"{self.label} ({self.ids})"


@dataclass
class In:
    group: str
    key: str
    name: str
    short: str
    shape: str
    low: float
    likely: float
    high: float
    unit: str
    conf: str
    ev: list
    src: str
    why: str
    vf: object = pc              # value format
    pf: object = pcr             # sampled-value format
    ax: tuple = None             # detail-page axis
    gax: tuple = None            # grid-tile axis
    params: tuple = None         # beta a, b
    kind: str = "distribution"
    note: str = ""               # evidence without an axis position (goes into evidence_points)
    mean_mark: bool = False
    suf: str = ""                # unit shown after a value on the pages
    shown: str = ""              # fixed items: value as shown on a flat tile
    sub: str = ""                # fixed items: line under it
    extra: str = ""              # tiles: text appended to the range line

    def __post_init__(self):
        if self.gax is None and self.shape not in ("fixed",):
            pad = (self.high - self.low) * 0.04
            self.gax = (max(self.low - pad, 0) if self.low >= 0 else self.low - pad, self.high + pad)
        if self.ax is None:
            self.ax = self.gax

    def v(self, x):
        return f"{self.vf(x)}{self.suf}"

    def rng_text(self):
        if self.vf is lakh and self.high >= 1e5:
            return f"₹{trim(self.low / 1e5, 2)}–{trim(self.high / 1e5, 2)} lakh"
        return f"{self.vf(self.low)}–{self.vf(self.high)}{self.suf}"

    def mean(self):
        d = self.frozen()
        return float(d.mean()) if d is not None else self.likely

    def mean_differs(self, th=0.05):
        return self.shape != "fixed" and self.likely != 0 and abs(self.mean() / self.likely - 1) > th

    def frozen(self):
        lo, mo, hi = self.low, self.likely, self.high
        if self.shape == "triangular":
            return stats.triang((mo - lo) / (hi - lo), loc=lo, scale=hi - lo)
        if self.shape == "pert":
            a, b = 1 + 4 * (mo - lo) / (hi - lo), 1 + 4 * (hi - mo) / (hi - lo)
            return stats.beta(a, b, loc=lo, scale=hi - lo)
        if self.shape == "lognormal":
            return stats.lognorm(s=(math.log(hi) - math.log(lo)) / (2 * stats.norm.ppf(0.95)), scale=mo)
        if self.shape == "beta":
            return stats.beta(*self.params)
        return None

    def sample(self, rng, n):
        if self.shape == "fixed":
            return np.full(n, float(self.likely))
        if self.shape == "triangular":
            return rng.triangular(self.low, self.likely, self.high, n)
        if self.shape == "pert":
            return self.low + (self.high - self.low) * rng.beta(*self.frozen().args[:2], n)
        if self.shape == "lognormal":
            return rng.lognormal(math.log(self.likely), self.frozen().kwds["s"], n)
        return rng.beta(*self.params, n)


_A = APP_R12 * 20                # online still saving: Beta(a, b), mean = our app curve, a + b = 20 as the earlier Beta(5, 15)
_OB = stats.beta(_A, 20 - _A)
CAC_P5, CAC_MED, CAC_P95 = float(CAC["low"]), float(CAC["mode"]), float(CAC["high"])
SALARY = N.PAY_M
months = lambda v: trim(v, 1)

CORE = [
    # ---- the saver: retention curve and saving rate
    In("saver", "daily", "Daily amount at sign-up", "Daily amount", "triangular", 200, 350, 500, "Rs a day", YOURS,
       [E(350, "yours ₹350", "operator", who="you"), E(200, "a janta agent's savers ₹200–500", "IV-03", "Rs 200 to 500", 500)],
       "operator; IV-03", "Triangular: the interview gives a firm floor and ceiling and you gave the middle; nothing says it leans either way.",
       rs, rsr, (150, 550), (190, 510)),
    In("saver", "days", "Deposit days a month (while active)", "Deposit days a month", "pert", 16, 20, 24, "days a month", OURS,
       [E(20, "last deck 20", "xs_inputs_v2", who="last"), E(26, "shop open ~26 days (our guess)", "judgement", who="last")],
       "judgement", "PERT around 20: a shop opens about 26 days a month and some days are missed; no data, so a plain symmetric shape.",
       num, num, (14, 28), (15.5, 24.5)),
    In("saver", "amount_growth", "Growth in his daily amount per year saved", "Amount growth a year", "pert", 0.0, 0.05, 0.10, "share a year", OURS,
       [E(0.0, "last deck 0%", "xs_inputs_v2", who="last"), E(0.0, "earlier model 0–20%", "distributions.csv", hi=0.20, who="last")],
       "judgement", "PERT 0–10%: no data on how a daily saver's amount grows; half the earlier model's provisional 0–20% range.",
       pc, pcr, (0, 0.21), (0, 0.105)),
    In("saver", "r3", "Still saving at month 3", "Still saving, month 3", "pert", 0.60, 0.80, 0.92, "share of a cohort", OURS,
       [E(APP[3], f"an app's savers {APP[3] * 100:.0f}%", "agent3_survival", who="last"),
        E(JANTA[3], f"a janta book ~{JANTA[3] * 100:.0f}% (an existing book)", "IV-12, IV-01", "6 to 10 / 6 to 10"),
        E(0.64, "SBI ₹250 SIP, all frequencies: 64% still on at ~6 months (avg age)", "XO-05", "35.64", axis=False)],
       "IV-01, IV-12; agent3_survival; XO-05",
       "PERT leaning high: an existing janta book keeps ~92% at month 3, an app keeps about half; the street sits nearer the janta book.",
       pc, pcr, (0.4, 1.0), (0.58, 0.94),
       note="XO-05 is SBI MF's ₹250 Jan Nivesh SIP (daily, weekly and monthly; not Choti SIP): 35.64% of FY26 sign-ups had stopped by 1 Apr 2026, "
            "at an average age of ~6 months, so 64% still on at ~6 months (shown at month 6 on the curve)"),
    In("saver", "r12", "Still saving at month 12", "Still saving, month 12", "pert", 0.25, 0.55, 0.72, "share of a cohort", OURS,
       [E(APP_R12, "an app's savers 24%", "story_unit", who="last"), E(0.30, "your bear case 30–40%", "operator", hi=0.40, who="you"),
        E(NEED_R12, f"last deck needed {NEED_R12 * 100:.0f}%", "xs_breakeven_v2", who="need"),
        E(JANTA_R12, "a janta book ~72% (an existing book)", "IV-12, IV-11, IV-01", "6 to 10 / 6 to 10")],
       "operator (agreed 16 Oct: likely 55%); story_unit; IV-01, IV-11, IV-12; xs_breakeven_v2",
       "PERT with your agreed 55%: between your bear case and an existing janta book's 72%; the app's 24% sits below the low end.",
       pc, pcr, (0.15, 0.80), (0.23, 0.74),
       note="agreed by the operator 16 Oct (likely 55%); a janta book of 200–400 loses 6–10 a month: 8 of 300 a month is 72% after a year (IV-01, "
            "IV-12), an existing book's churn, not a new cohort; most have saved 5+ years (IV-11); 37% is the 5-year break-even on the last deck's inputs"),
    In("saver", "churn_late", "Monthly drop-off after month 12", "Later monthly drop-off", "pert", 0.010, 0.015, 0.030, "share a month", OURS,
       [E(0.010, "Acorns ~1–1.3%", "TB-11", "~1-1.3% monthly churn", 0.013), E(JANTA_LOSS, "a janta book ~2.7%", "IV-12, IV-01", "6 to 10 / 6 to 10"),
        E(0.008, "earlier model 0.8–3%", "distributions.csv", hi=0.03, who="last")],
       "TB-11; IV-01, IV-12; distributions.csv churn_late",
       "PERT leaning low: savers who last a year rarely leave (Acorns ~1%); the janta book's steady 2.7% is the top.",
       pc, pcr, (0.005, 0.034), (0.009, 0.031)),
    # ---- the agent
    In("agent", "signups_run", "Sign-ups a month in year 1, once the agent is up to speed", "Sign-ups a month", "pert", 60, 100, 150, "sign-ups a month", YOURS,
       [E(100, "yours 100", "operator", who="you"), E(100, "PR-01: most field agents 100+", "PR-01", "100+ customers a month"),
        E(120, "PR-01: top agents 120–150", "PR-01", "120-150", 150), E(30, "earlier 30", "operator", who="last"),
        E(6, "a janta agent: 6–10 new a month", "IV-12", "6 to 10", 10)],
       "operator (17 Oct: 100 a month; 'each guy will be different'); PR-01; IV-12",
       "PERT around 100: your figure, matching a practitioner's field agents (100+ a month, the best 120–150, PR-01); the range is agent-to-agent variation.",
       cnt, cnt, (0, 160), (55, 155), suf=" a month",
       note="PR-01 counts onboarding, not daily cash collection; our agent also serves and collects; the janta agent's 6–10 is a bank collector who is not selling"),
    In("agent", "signup_decline_y5", "Sign-ups fall in a straight line from the year-1 level (months 1–12, after the ramp) to this share of it by month 49, then flat",
       "Sign-ups by year 5", "pert", 0.5, 0.7, 0.9, "share of the year-1 level", YOURS, [], "operator (17 Oct): 'This can decline to 70 over 5 years'",
       "PERT around 70%: his time goes to the growing book, so he signs fewer.", pc, pcr),
    In("agent", "online_lead_share", "Share of onboardings that start as bought online leads (the agent closes and serves them)", "Online leads", "pert",
       0.3, 0.5, 0.7, "share of onboardings", YOURS, [], "operator (17 Oct: 50%); range judgement",
       "PERT around half: your figure; the range is our judgement. Served offline, they keep and buy like street savers.", pc, pcr,
       note="no app-only channel: every saver is served offline by the agent"),
    In("agent", "lead_cost", "Our cost per online lead the agent converts", "Lead cost", "pert", 150, 250, 499, "Rs a converted lead", YOURS,
       [E(100, "finance-app installs ₹100–300", "TB-19", "wealth/broking Rs 100-300", 300), E(499, "our full online cost per active saver ₹499", "story_unit", who="last")],
       "operator (17 Oct: ₹250); context: TB-18..TB-22, story_unit",
       "PERT ₹150–499 around your ₹250: above an app install (₹100–300), below our full online cost per active saver (₹499).", rs, rsr, (80, 560), (140, 510)),
    In("agent", "ramp_months", "Months for a new agent to reach full speed (straight line from 50%)", "Months to full speed", "triangular", 0, 3, 6,
       "months", OURS, [], "judgement", "Triangular 0–6 months around 3: no data on how fast a new street agent signs savers.",
       months, num, (0, 6.5), (0, 6.2), suf=" months", note="no data; starts at 50% of full speed and rises in a straight line"),
    In("agent", "capacity", "Cash visits one agent can make a day", "Cash visits a day", "triangular", 300, 400, 450, "visits a day", OURS,
       [E(200, "a janta agent's book: 200–400 savers", "IV-01", "200 to 400", 400), E(400, "model so far 400", "agent_3yr.py", who="last")],
       "IV-01; agent_3yr.py", "Triangular: 400 is the top of a janta agent's book, with a little room above; beyond it, extra cash capacity is paid for.",
       cnt, cnt, (150, 480), (290, 460)),
    In("agent", "upi_12", "Share of a cohort's active savers on UPI by month 12", "On UPI by month 12", "pert", 0.10, 0.30, 0.60, "share of active savers", OURS,
       [E(0.10, "today: under 10% of collections by UPI", "IV-07", "90 or more")],
       "operator; IV-06, IV-07", "PERT leaning low: 9 in 10 have UPI, but 90%+ of today's collections are cash, by habit.",
       pc, pcr, (0, 0.7), (0.08, 0.62),
       note="9 or 10 of 10 customers have UPI (IV-06) but 90 or more of every ₹100 is collected in cash (IV-07), by habit (IV-08); "
            "the share rises in a straight line from 0 at month 1 to this value at month 12, then stays flat"),
    In("agent", "kyc_cost", "Onboarding and KYC cost per sign-up", "KYC cost a sign-up", "pert", 25, 40, 100, "Rs a sign-up", OURS,
       [E(25, "build-up ₹25–60", "TC-35", "roughly Rs 25-60", 60), E(30, "fund KYC upload ₹30 (2012)", "REG-045", "Rs 30 per KYC upload"),
        E(50, "video KYC ₹50–150", "REG-069", "Video KYC (V-CIP) Rs 50-150", 150)],
       "TC-35, REG-045, REG-069",
       "PERT on the research build-up (Aadhaar e-KYC ₹20 + fund KYC ₹30–35 + checks): ₹25–60, with a tail for video KYC.",
       rs, rsr, (0, 160), (20, 105)),
    In("agent", "support_cost", "Running cost per active saver a month (support, app, bank cash-deposit charges, supervision)", "Running cost a saver",
       "pert", 0, 5, 15, "Rs an active saver a month", YOURS, [], "operator (agreed 16 Oct)",
       "PERT ₹0–15 around ₹5 a month: the operator's figure for support, the app, bank cash-deposit charges and supervision.", rs, rsr, (0, 16), (0, 15.5)),
    In("agent", "cash_cover", "Fidelity and cash-in-transit insurance, per agent a month (fixed per agent)", "Cash cover an agent", "pert", 500, 1000, 2000,
       "Rs per agent a month", OURS, [], "judgement; GAP (no research row)",
       "PERT ₹500–2,000 around ₹1,000 a month: cover for the cash he carries; same-day bank deposit keeps it small; no research row.", rs, rsr,
       note="operator: 'Daily deposit + cover'; GAP: no research row for fidelity or cash-in-transit cover; deposit charges sit inside the ₹5 running cost"),
    # ---- the fund: agreed 16 Oct, a debt fund
    In("fund", "trail", "Fund commission a year: a debt or short-duration fund (agreed)", "Fund commission (debt)", "pert", 0.002, 0.0035, 0.005,
       "share of balance a year", GUIDE,
       [E(0.002, "fund and adviser blogs: 0.2–0.5%", "XB-04", "0.2-0.5", 0.005), E(0.002, "a 2026 guide: 0.20–0.60%", "TC-23", "0.20-0.60", 0.006),
        E(0.0035, "last deck 0.35%", "xs_inputs_v2", who="last")],
       "operator (agreed 16 Oct: debt fund); XB-04, TC-23", "PERT on blog-reported fee gaps; the gap may overstate what is paid, as it does for liquid funds.",
       pc, pcr, (0.0015, 0.0065), (0.0019, 0.0051)),
    In("fund", "rollover", "Share of the balance left in the fund at each term end", "Left in at term end", "pert", 0.0, 0.25, 0.60, "share of the balance", OURS,
       [E(0.0, "last deck 0% (all paid out)", "xs_inputs_v2", who="last")], "judgement",
       "PERT 0–60% around the agreed 25%: janta savers take the money at the end of a term; no data on how much a fund keeps.",
       pc, pcr, (0, 0.65), (0, 0.62)),
    In("fund", "withdraw_m", "Share of the balance withdrawn mid-term, each month", "Taken out each month", "pert", 0.0, 0.01, 0.03, "share of the balance a month",
       OURS, [E(0.0, "last deck 0%", "xs_inputs_v2", who="last")], "judgement",
       "PERT 0–3% a month leaning low: a saving habit with yearly terms, but emergencies happen; no data.", pc, pcr, (0, 0.033), (0, 0.031)),
    In("fund", "fund_return", "Debt-fund return to the saver, net of costs, accruing to his balance", "Fund return to him", "pert", 0.060, 0.070, 0.075,
       "a year, net of costs", OURS, [E(0.05, "liquid funds 5–6% (OWN-02)", "OWN-02", "5-6% a year", 0.06)],
       "context: OWN-02; judgement (agreed 16 Oct)",
       "PERT 6–7.5% around 7%: above liquid funds' 5–6% (OWN-02); the hook the operator named (agreed 16 Oct).", pc, pcr, (0.045, 0.08), (0.059, 0.076),
       note="operator: 'Hook is high savings rate in debt funds that we offer'; GAP: no short-duration debt-fund return row in research"),
    # ---- loans: every active saver from month 1 (marketplace_from = 1, agreed 16 Oct; was proven savers, age 7+)
    In("loans", "apply", "Active savers with no loan running who apply in a year", "Apply for a loan, a year", "pert", 0.08, 0.18, 0.35, "share a year", OURS,
       [E(0.175, "Kissht 17.5% ever", "XL-42", "17.5% of registered users"), E(0.202, "Brazil 20% year one", "LS-06", "20.2"),
        E(0.35, "founder 35%", "founder", who="you"), E(0.0093, "Paytm, any financial product ~0.9% a quarter", "XL-04", "0.93", axis=False)],
       "XL-42, LS-06, XL-04; founder",
       "PERT leaning low: 18% sits just under Kissht's all-time and Brazil's first-year shares; the founder's 35% is the ceiling. Monthly hazard 1 − (1 − apply)^(1/12).",
       pc, pcr, (0, 0.40), (0.07, 0.36), note="XL-42 is cumulative since launch among loan-app users, so a yearly rate is far lower"),
    In("loans", "eligible", "Applicants who can carry a ₹2.5 lakh EMI", "Eligible for ₹2.5 lakh", "pert", 0.25, 0.45, 0.65, "share", OURS,
       [E(0.50, "last deck 50%", "xs_inputs_v2", who="last"), E(0.30, "earlier range 30–70%", "agent3_funnel_inputs", hi=0.70, who="last")],
       "context: XL-34, IV-04, XB-09", "PERT, near symmetric: the 50% EMI rule passes most ₹20–40k earners, but many already carry a loan.",
       pc, pcr, (0.15, 0.75), (0.24, 0.66),
       note="no direct measure: a ₹10,073 EMI (36 months) needs ₹20,145+ income under the 50% rule (XL-34); his savers earn ₹20–40k (IV-04); "
            "41% of small-business borrowers already have a loan (XB-09)"),
    In("loans", "approved_first", "Eligible applicants a lender approves, first loan (several lenders)", "Approved, first loan", "pert", 0.20, 0.35, 0.50,
       "share", OURS,
       [E(0.112, "Kissht: 11% of new applicants", "XL-41", "11.20"), E(0.25, "founder, one lender: 25%", "founder", who="you")],
       "XL-41; founder", "PERT: several lenders should beat one lender's 25%, and savers are known to us; Kissht approves 11% of new applicants.",
       pc, pcr, (0, 0.55), (0.19, 0.51)),
    In("loans", "approved_repeat", "Approved, repeat loan (after repaying one)", "Approved, repeat loan", "pert", 0.50, 0.70, 0.85, "share", OURS,
       [E(0.7354, "Kissht: 74% of repeat ones", "XL-41", "73.54"),
        E(0.50, "Paytm: >50% of loan money goes to repeat borrowers", "NG-028", ">50% of merchant-loan", axis=False)],
       "XL-41, NG-028", "PERT around Kissht's 74% for repeat applicants; a repaid loan is the best evidence a lender gets.",
       pc, pcr, (0.4, 0.9), (0.48, 0.87),
       note="NG-028 is a share of loan money, not an approval rate; PM SVANidhi: 68% of first-loan repayers took a second (NG-014)"),
    In("loans", "tenure", "Loan tenure", "Loan length", "pert", 24, 36, 48, "months", OURS,
       [E(36, "EMI basis ₹10,073 = 36 months", "agent3_funnel_inputs", who="last")],
       "agent3_funnel_inputs.csv (the ₹10,073 EMI basis)",
       "PERT 24–48 months around 36: the eligibility test's ₹10,073 EMI is a 36-month loan; shorter loans need more income, longer ones less.",
       months, num, (20, 52), (23, 49), suf=" months", mean_mark=True, note="₹2.5 lakh over 36 months at about 26% a year gives the ₹10,073 EMI"),
    In("loans", "ticket", "Loan size", "Loan size", "pert", 25000, 250000, 500000, "Rs", YOURS,
       [E(250000, "yours ₹2.5 lakh", "operator", who="you"), E(205000, "Paytm average ₹2.05 lakh (Q4 FY24)", "XB-08", "205000"),
        E(25557, "segment average ~₹25.6k (Kissht)", "XL-42", "25,556")],
       "operator (agreed 16 Oct: range ₹25,000 to ₹5 lakh); XB-08, XL-42",
       "PERT ₹25,000–5 lakh around your ₹2.5 lakh ('range 25k upto 5 lacs'); the segment's average loan is ~₹25,600 (XL-42), so the low end is real.",
       lakh, lambda v: lakh(round(v / 1e4) * 1e4), (0, 530000), (15000, 515000), mean_mark=True,
       note="ticket_growth's cap stays ₹5 lakh"),
    In("loans", "fee", "Origination fee at the start: a DSA's rate on personal loans (first, repeat and top-up loans; paid by the lender)", "Starting fee",
       "pert", 0.010, 0.0175, 0.025, "share of the loan", GUIDE,
       [E(0.005, "bank DSA 0.5–1.5%", "LEV-009", "0.5-1.5 (banks)", 0.015), E(0.01, "DSA personal loans 1–2.5%", "XL-13", "1-2.5 (typical)", 0.025),
        E(0.02625, "1.5× by year 5: 2.625%", "operator", who="you"), E(0.045, "Paytm 4.5–5%", "XL-07", "4.5-5 (no DLG)", 0.05),
        E(0.046, "Paisabazaar ≤4.6–4.7%, incl. cards", "XL-09, LEV-065", "4.6 (upper bound)", 0.047)],
       "XL-13, LEV-009; operator (17 Oct: start like a DSA, 1.5× over 5 years)",
       "PERT around a DSA's 1.75% (XL-13: 1–2.5%); the fee in month t = fee × (1 + (fee_mult_end − 1)(t − 1)/59), so 2.625% by month 60.",
       pc, pcr, (0, 0.052), (0.009, 0.026),
       note="operator: 'initially we start like a DSA and then move that multiplier to 1.5x over few years...lets say 5 years...slowly'; "
            "housing loans keep their own DSA rates"),
    In("loans", "taken_back", "Fees taken back (loan closed or bad within 6 months)", "Fees taken back", "triangular", 0.0, 0.025, 0.05,
       "share of fees", OURS, [E(0.025, "last deck 2.5%", "xs_inputs_v2", who="last")],
       "XL-13, XL-47", "Triangular 0–5%: DSA guides say fees can be taken back within 6 months, but no one publishes how often.",
       pc, pcr, (0, 0.06), (0, 0.052), note="fees can be taken back if the loan closes or goes bad within 6 months (XL-47); no published rate"),
    In("loans", "loss", "Money lost on loans, after recoveries (share of money lent)", "Money lost on loans", "pert", 0.015, 0.03, 0.05,
       "share of money lent", OURS,
       [E(0.0174, "self-help groups 1.7–2.1%", "SE-01, EVD-03", "1.74", 0.0205), E(0.045, "Paytm 4.5–5% (your worst case)", "XB-07, QM-22", "4.5-5.0", 0.05),
        E(0.054, "NBFC-MFI 5.4%", "SE-02", "5.4")],
       "XB-07, QM-22, SE-01, EVD-03, SE-02; operator",
       "PERT with your worst case at Paytm's 5%: savers chose to save first and the agent who knows them helps collect; the low sits near savings-linked self-help groups.",
       pc, pcr, (0.005, 0.06), (0.013, 0.052),
       note="the anchor for the collection buckets; Paytm's 4.5–5% is expected credit loss on merchant loans it sources, Q4 FY26, on lenders' books "
            "(XB-07, QM-22); SHG figures are gross bad loans (SE-01 1.74%, EVD-03 2.05%); NBFC-MFI 5.4% is gross, a stressed year (SE-02); the loss falls "
            "on the lender, not us (no first-loss cover): it moves the fee and approvals a lender gives us"),
    In("insurance", "ins_partner_share", "Share of insurance commission that reaches us through a broker partner (first-year and renewal)",
       "Insurance: our share", "pert", 0.60, 0.75, 0.90, "share of the commission", OURS, [], "operator (partners' licences); judgement",
       "PERT 60–90% around 75%: we sell insurance under a broker partner's licence, which keeps a cut; applies to all 7 insurance products.", pc, pcr,
       note="operator: 'Partners' licences'; fund trail (our own ARN), loan and card fees and the other-lender loans stay whole"),
    # ---- the marketplace's first six months (operator, 16 Oct; Our judgement, agreed)
    In("loans", "early_takeup_mult", "In months 1–6, every take-up (loan applications, cards, all cross-sell products) as a share of the agreed rate",
       "Early take-up (1–6)", "pert", 0.25, 0.50, 0.75, "share of the agreed take-up, months 1–6 (100% from month 7)", OURS, [],
       "judgement (agreed 16 Oct)",
       "PERT around a half: the marketplace opens in month 1, but a saver of a few weeks is not yet ready to buy; 100% from month 7.", pc, pcr,
       note="operator: 'month 1 for marketplace can have low take up rates and approval rates but business starts from there'"),
    In("loans", "early_approval_mult", "In months 1–6, loan and card approvals as a share of the agreed rate", "Early approval (1–6)", "pert", 0.40, 0.60, 0.80,
       "share of the agreed approval, months 1–6 (100% from month 7)", OURS,
       [E(0, "Kissht approves 11% of new applicants vs 74% of repeat ones", "XL-41", "11.20", axis=False)],
       "context: XL-41; judgement (agreed 16 Oct)",
       "PERT around 60%: a lender sees a thinner saving record in the first months; Kissht's new vs repeat gap (XL-41) shows how much history counts.",
       pc, pcr),
    # ---- rates that grow with our pool's history (addendum 4; Our judgement, agreed 16 Oct)
    In("loans", "takeup_growth", "All take-up hazards rise each calendar year as the pool's history grows (loan apply, cards, all cross-sell products)",
       "Take-up growth a year", "pert", 0.0, 0.05, 0.15, "a year, relative", OURS, [], "judgement (agreed 16 Oct)",
       "PERT 0–15% around 5%: a known pool gets more offers and buys more; no data.", pc, pcr,
       note="cap: 2× the agreed rate; year y multiplier (1 + g)^(y − 1), on top of the early-months factor"),
    In("loans", "approval_growth", "First-loan and card approval rise each calendar year as lenders see our pool's repayments", "Approval growth a year",
       "pert", 0.0, 0.10, 0.20, "a year, relative", OURS, [E(0, "Kissht approves 74% of repeat applicants", "XL-41", "73.54", axis=False)],
       "context: XL-41; judgement (agreed 16 Oct)",
       "PERT 0–20% around 10%: repayment history is what lenders price; Kissht's repeat applicants get 74% (XL-41).", pc, pcr,
       note="cap: 80% absolute; year y multiplier (1 + g)^(y − 1)"),
    In("loans", "ticket_growth", "His next loan (repeat or top-up) is bigger for each year he has repaid", "Loan size growth", "pert", 0.0, 0.10, 0.20,
       "per year repaid, on the base ticket", OURS, [E(0, "Bachatt's partners lend up to ₹5 lakh", "XL-12", "up to Rs 5 lakh", axis=False)],
       "context: XL-12; judgement (agreed 16 Oct)",
       "PERT 0–20% around 10% per year repaid: a repaid loan earns a bigger one, up to the ₹5 lakh cap.", pc, pcr,
       note="cap: ₹5 lakh (XL-12: Bachatt's partners lend up to ₹5 lakh)"),
    In("loans", "topup_share", "Top-up loans: share of borrowers with 12+ EMIs paid on time who take a top-up each year", "Top-up share a year", "pert",
       0.05, 0.15, 0.30, "share of eligible borrowers a year", OURS,
       [E(0, "over half of Paytm's merchant-loan money goes to repeat borrowers", "NG-028", ">50% of merchant-loan", axis=False)],
       "context: NG-028; judgement (agreed 16 Oct)",
       "PERT 5–30% around 15%: lenders top up good payers; Paytm lends most of its money to repeat borrowers (NG-028).", pc, pcr,
       note="earns the origination fee net of taken back; at most one top-up runs at a time; still-saving borrowers only; the lender's call"),
    In("loans", "topup_size", "Top-up size, as a share of his original ticket (times ticket_growth)", "Top-up size", "pert", 0.25, 0.40, 0.60,
       "share of the original ticket", OURS, [], "judgement (agreed 16 Oct)",
       "PERT 25–60% around 40% of the original loan; no data.", pc, pcr,
       note="adds to the collections base pro rata by size"),
    # ---- collections on overdue loans (addendum 3): loss is the anchor; p90 is derived from it
    In("collections", "early_cured", "Share of loans that fall 31–90 days behind and that our agent brings back before 90 days", "Brought back early",
       "pert", 0.10, 0.20, 0.35, "share of loans made", OURS, [], "judgement (no published figure)",
       "PERT 10–35% around 20%: no published lifetime figure; vendor bucket cure rates are per spell, not per loan (GAP-02).", pc, pcr,
       note="no published figure; GAP-02's 70–85% / 50–70% are per-spell cure rates, so they cannot be chained into a lifetime share"),
    In("collections", "fee_early", "Our fee per early (31–90 day) account brought back", "Fee, early account", "pert", 200, 450, 1000, "Rs an account", GUIDE,
       [E(200, "vendor table: ₹200–400 at 31–60 days, ₹500–1,000 at 61–90", "GAP-01", "200-400 / 500-1000 / 1000-5000", 1000)], "GAP-01",
       "PERT across the vendor table's 31–60 and 61–90 day costs per account: no published rate card by bucket exists.", rs, rsr),
    In("collections", "recovered", "Recovered of what is owed after 90 days", "Recovered, 90+ days", "pert", 0.30, 0.35, 0.50, "share of what is owed", PUB,
       [E(0.30, "Paytm's figure 30–35%", "XB-07", "30% to 35%", 0.35), E(0.30, "vendor table 30–50%", "GAP-02", "70-85 / 50-70 / 30-50", 0.50)],
       "XB-07, GAP-02; operator", "PERT: the low end is Paytm's published figure; above it is our judgement, because the agent knows him (operator).",
       pc, pcr, note="Published at the low end (Paytm, XB-07); the range above 35% is our judgement"),
    In("collections", "fee_b3", "Our fee per 90+ account recovered", "Fee, 90+ days", "pert", 1000, 2500, 5000, "Rs an account", GUIDE,
       [E(1000, "vendor table ₹1,000–5,000", "GAP-01", "200-400 / 500-1000 / 1000-5000", 5000)], "GAP-01", "PERT on the vendor table.", rs, rsr),
    # ---- cards
    In("cards", "card_share", "Active savers who get a card (once, spread over ages 1–6; was ages 7–12)", "Get a card (once)", "pert", 0.01, 0.03, 0.06, "share", OURS,
       [E(0.03, "3% of Indians hold a card", "XL-40", "3% of the population"), E(0.05, "your first figure 5%", "operator", who="you"),
        E(0.005, "FD-secured card guess 0.5–5%", "XL-54", "0.5-5%", 0.05)],
       "operator (agreed 16 Oct: 3%); XL-40, XL-54", "PERT on the evidence value you agreed, 3%, which matches card holding in India.",
       pc, pcr, (0, 0.07), (0.008, 0.062), note="XL-40's 3% is a stock of card holders (PwC 2022), not a take-up rate"),
    In("cards", "card_fee", "Fee per approved card", "Fee per card", "pert", 300, 1000, 2000, "Rs a card", GUIDE,
       [E(500, "affiliate guides ₹500–2,000", "BM-08", "500-2,000 typical", 2000), E(1000, "GroMo sub-agents ₹1,000–2,400", "XL-20", "1,000-2,400", 2400),
        E(300, "FD-secured guess ₹300–1,500", "XL-54", "Rs 300-1,500", 1500)],
       "BM-08, XL-20, XL-54", "PERT: bank cards pay ₹500–2,000, but our savers will mostly get FD-secured cards, which likely pay less.",
       rs, rsr, (0, 2500), (250, 2050)),
    # ---- online, for comparison only
    In("online", "online_cac", "Online cost to win a saver", "Online cost to win", "lognormal", CAC_P5, CAC_MED, CAC_P95, "Rs a saver", OURS,
       [E(SALARY * 12 / 1000, "street: ₹240 a sign-up", "salary ÷ sign-ups", who="last"), E(796, "Groww ₹796–1,374", "TB-18", "Rs 796 / Rs 1,374", 1374)],
       "TB-18..TB-22, NG-043 (distributions.csv cac_target, shopkeepers)",
       "Lognormal: a cost cannot fall below zero and has a long right tail; the earlier model's shopkeeper row, unchanged.",
       rs, rsr, (0, 1800), (0, 1700)),
    In("online", "online_r12", "Online: still saving after a year", "Still saving (online)", "beta",
       float(_OB.ppf(0.05)), APP_R12, float(_OB.ppf(0.95)), "share of savers", OURS,
       [E(APP_R12, "our app curve 24%", "story_unit", who="last"), E(0.38, "SBI ₹250 SIP ~38% (our extrapolation)", "NG-033, XO-05", "35.64"),
        E(0.10, "research range 10–40%", "tri_behaviour_summary.md", "supported range 10-40%", 0.40)],
       "story_unit; NG-033, XO-05; tri_behaviour_summary.md",
       "Beta: a share between 0 and 1, centred on our app curve's 24%, as wide as the earlier model's Beta(5, 15).",
       pcr, pcr, (0, 0.55), (0.03, 0.5), params=(_A, 20 - _A),
       note="the ~38% at month 12 is our constant-drop extrapolation of SBI's 35.64% stopped at an average age of ~6 months"),
]

# ---- cross-sell products (addendum 1, with addendum 2's tickets): prefix, group, tile name, long name, rows
ATTR = {"takeup": "take-up a year", "ticket": "ticket", "comm": "our commission", "renew": "renews a year", "survive24": "survives to 24 months",
        "approval": "approval share"}
F = lambda *a: a
PRODUCTS = [
    ("hlth_small", "insurance", "Small health", "Small health / hospital cash", [
        F("takeup", "pert", .02, .06, .15, "share of active savers without it, a year", OURS, pc, [E(0, "62.2% of platform workers have no health cover", "XO-31", "62.2"),
          E(0, "PhonePe ₹8 insurance revenue a user", "XO-10", "8.1")], "XO-31, XO-10; judgement"),
        F("ticket", "pert", 300, 800, 1500, "Rs premium a year", GUIDE, rs, [E(0, "hospital cash from ₹799", "XO-35", "799"), E(0, "Bima Vistaar ₹1,500", "XO-30", "1500")],
          "XO-35, XO-30"),
        F("comm", "pert", .10, .14, .15, "share of first-year premium", PUB, pc, [E(0, "draft cap 15% (distributors) / 20% (agents)", "REG-054", "first-time 15%")],
          "REG-054, XO-19", "capped at the draft distributor (IDE) cap of 15% (16.5–18% in small towns and rural areas, XO-19); agreed 16 Oct: the draft caps"),
        F("renew", "pert", .30, .50, .70, "share renewing a year, at 5%", OURS, pc, [E(0, "micro-insurance renewals 4–61%", "XO-24", "61 percent"),
          E(0, "auto-debited PMJJBY / PMSBY 51–70%", "TB-23", "~51% (PMJJBY) and ~70% (PMSBY)")], "XO-24, TB-23")], .05),
    ("hlth_family", "insurance", "Family health", "Family health cover (₹3–5 lakh floater)", [
        F("takeup", "pert", .005, .02, .05, "share of active savers without it, a year", OURS, pc, [], "judgement"),
        F("ticket", "pert", 5500, 8000, 15000, "Rs premium a year, excl. GST", GUIDE, rs, [E(0, "₹5 lakh floater ₹5,581–6,560", "GAP-04", "5581-6560")], "GAP-04",
          "a family of four at age 35 costs more than GAP-04's 30-year-old"),
        F("comm", "pert", .10, .14, .15, "share of first-year premium", PUB, pc, [E(0, "draft cap 15% / 20%", "REG-054", "first-time 15%")], "REG-054",
          "capped at the draft distributor cap of 15%"),
        F("renew", "pert", .60, .75, .89, "share renewing a year, at 5%", OURS, pc, [E(0, "Policybazaar health renewals ~89%", "XO-09", "nearly 89%")], "XO-09")], .05),
    ("life_term", "insurance", "Term life", "Term life (small cover)", [
        F("takeup", "pert", .01, .03, .06, "share of active savers without it, a year", OURS, pc, [E(0, "65% of gig workers lack life cover", "XO-32", "65% lacking life insurance")],
          "XO-32"),
        F("ticket", "pert", 500, 1000, 2000, "Rs premium a year", OURS, rs, [], "judgement", "no premium source in research"),
        F("comm", "pert", .075, .20, .25, "share of first-year premium", PUB, pc, [E(0, "draft caps: single 7.5%, multi-year 25% / 30%", "XO-20", "multi-year premium 25% / 7.5%")],
          "XO-20", "capped at the draft distributor cap of 25% for multi-year pure term"),
        F("renew", "pert", .60, .75, .85, "share renewing a year, at 7.5%", OURS, pc, [E(0, "13th-month persistency 64–83%", "TB-24", "64-83%")], "TB-24")], .075),
    ("accident", "insurance", "Accident", "Personal accident", [
        F("takeup", "pert", .02, .05, .10, "share of active savers without it, a year", OURS, pc, [E(0, "44% of platform workers have no accident cover", "XO-31", "44.2")], "XO-31"),
        F("ticket", "pert", 100, 250, 500, "Rs premium a year", OURS, rs, [], "judgement", "no premium source in research"),
        F("comm", "pert", .10, .14, .15, "share of first-year premium", PUB, pc, [E(0, "draft cap: retail 15% / 17.5%", "XO-19", "retail 15% (IDEs) / 17.5% (agents)")],
          "XO-19", "capped at the draft distributor cap of 15% for retail personal accident"),
        F("renew", "pert", .30, .50, .70, "share renewing a year, at 5%", OURS, pc, [E(0, "auto-debited PMSBY ~70%", "TB-23", "~70% (PMSBY)")], "TB-23")], .05),
    ("two_wheeler", "insurance", "Two-wheeler", "Two-wheeler insurance (savers with a vehicle)", [
        F("takeup", "pert", .05, .15, .30, "share of active savers without it, a year", OURS, pc, [E(0, "54% of vehicles uninsured", "XO-22", "54")], "XO-22"),
        F("ticket", "pert", 714, 1000, 1200, "Rs premium a year", PUB, rs, [E(0, "third-party ₹714 (IRDAI)", "XO-21", "714")], "XO-21"),
        F("comm", "pert", .025, .0475, .0905, "blended share of premium", PUB, pc, [E(0, "draft caps: motor TP nil–5%, OD 5–15%", "XO-18", "Motor TP")], "XO-18"),
        F("renew", "pert", .50, .70, .85, "share renewing a year, at the same commission", OURS, pc, [], "judgement",
          "renewals pay two_wheeler_comm (the same rate)")], None),
    ("device", "insurance", "Phone cover", "Mobile / device insurance", [
        F("takeup", "pert", .01, .03, .06, "share of active savers without it, a year", OURS, pc, [], "judgement"),
        F("ticket", "triangular", 209, 500, 899, "Rs premium a year", GUIDE, rs, [E(0, "plans ₹209–899", "XO-34", "209-899")], "XO-34"),
        F("comm", "pert", .10, .13, .15, "share of premium", PUB, pc, [E(0, "draft cap: retail 15% / 17.5%", "XO-19", "retail 15% (IDEs) / 17.5% (agents)")], "XO-19",
          "capped at the draft distributor cap of 15%")], None),
    ("shop", "insurance", "Shop cover", "Shop insurance (fire and burglary)", [
        F("takeup", "pert", .01, .03, .08, "share of active savers without it, a year", OURS, pc, [], "judgement"),
        F("ticket", "pert", 250, 700, 2600, "Rs premium a year", PUB, rs, [E(0, "Digit via Fino ₹550–2,600; ICICI Lombard from ₹250", "GAP-05", "250 / 550 / 2600")], "GAP-05"),
        F("comm", "pert", .10, .14, .15, "share of first-year premium", PUB, pc, [E(0, "draft cap: retail incl. shopkeepers 15% / 17.5%", "XO-19", "shopkeepers")],
          "XO-19", "capped at the draft distributor cap of 15% for retail cover"),
        F("renew", "pert", .50, .65, .80, "share renewing a year, at 5%", OURS, pc, [], "judgement")], .05),
    ("sip", "investments", "SIP trail", "Equity/hybrid SIP trail", [
        F("takeup", "pert", .05, .10, .20, "share of active savers without one, a year", OURS, pc, [E(0, "77% of gig workers hold no fund", "XO-32", "77% holding no mutual funds")], "XO-32"),
        F("ticket", "pert", 250, 500, 1000, "Rs into the SIP a month", OURS, rs, [E(0, "all-India average SIP ₹3,224 a month", "XO-07", "3,224")], "XO-07"),
        F("comm", "pert", .005, .0075, .009, "trail, share of the balance a year", PUB, pc, [E(0, "Prudent earns 0.88–0.91%", "XO-08", "0.88-0.91")], "XO-08, XO-36",
          "Groww sells direct plans and earns about nothing (XO-36)"),
        F("renew", "pert", .50, .65, .80, "share of SIPs still running after a year", OURS, pc, [E(0, "SIP stoppage ratio 81% of new ones", "XO-06", "81.05")], "XO-06")], None),
    ("choti", "investments", "Choti SIP", "Choti SIP incentive (₹500 once, paid at month 24 if the SIP survives)", [
        F("takeup", "pert", .045, .09, .18, "share of active savers, a year", OURS, pc, [E(0, "3.22 lakh Choti SIPs by Jun 2026", "XO-04", "322,000")], "XO-04"),
        F("survive24", "pert", .15, .25, .40, "share of SIPs surviving to month 24", OURS, pc,
          [E(0, "+28,000 / −20,000 a month on 3.22 lakh", "XO-04", "+28,000/-20,000")], "XO-04, XO-05")], None),
    ("nps", "investments", "NPS", "NPS (₹200 once a new account)", [
        F("takeup", "pert", .01, .03, .05, "share of active savers, a year", OURS, pc, [], "judgement")], None),
    ("gold", "investments", "Digital gold", "Digital gold", [
        F("takeup", "pert", .03, .08, .15, "share of active savers, a year", OURS, pc, [], "judgement",
          "SEBI cautioned on digital gold (SAV-11), which also backs the founder's no-gold-at-launch choice"),
        F("ticket", "pert", 100, 300, 600, "Rs bought a month", OURS, rs, [], "judgement"),
        F("renew", "pert", .50, .65, .80, "share still buying after a year", OURS, pc, [], "judgement")], None),
    ("fd", "investments", "FD", "FD via partner banks", [
        F("takeup", "pert", .05, .10, .20, "share of active savers, a year", OURS, pc, [], "judgement"),
        F("ticket", "pert", 5000, 10000, 20000, "Rs an FD", OURS, rs, [], "judgement"),
        F("comm", "pert", .001, .005, .01, "share of the FD a year", GUIDE, pc, [E(0, "Stable Money 0.11% of FD assets", "XO-37", "0.11"),
          E(0, "FD platforms ~0.4–1%", "BM-03", "~1% / 0.4%")], "XO-37, BM-03")], None),
    ("recharge", "payments", "Recharge", "Mobile recharge", [
        F("takeup", "pert", .10, .25, .50, "share moving their recharge to us", OURS, pc, [], "judgement"),
        F("comm", "pert", .01, .02, .03, "share of recharge value", GUIDE, pc, [E(0, "Jio retailer margin 2–4%", "XO-25", "2 (base) to 4")], "XO-25",
          "an app usually gets less than a retailer")], None),
    ("bills", "payments", "Bill payments", "Bill payments (BBPS)", [
        F("takeup", "pert", .10, .25, .50, "share paying bills through us", OURS, pc, [], "judgement"),
        F("ticket", "pert", 12, 24, 36, "bills a year", OURS, cnt, [], "judgement"),
        F("comm", "triangular", 1, 2, 3, "Rs a bill", GUIDE, rs, [E(0, "agent rate cards ₹1–3 a bill", "XO-26", "1-3")], "XO-26")], None),
    ("loan_gold", "other_loans", "Gold loan", "Gold loan (other lenders)", [
        F("takeup", "pert", .02, .05, .10, "share of active savers, a year", OURS, pc, [E(0, "gold loans: 381 lakh a quarter, the most by count", "XL-28", "Gold 381.0")], "XL-28"),
        F("ticket", "pert", 30000, 50000, 80000, "Rs a loan", OURS, rs, [], "judgement"),
        F("comm", "pert", .005, .01, .015, "share of the loan", OURS, pc, [E(0, "no gold-loan payout found; DSA 1–3% in general", "GAP-06", "1-3 (general)")], "GAP-06",
          "gold loans are short and low-margin")], None),
    ("loan_cd", "other_loans", "Consumer loan", "Consumer-durable loan", [
        F("takeup", "pert", .005, .02, .05, "share of active savers, a year", OURS, pc, [], "XL-54"),
        F("ticket", "pert", 10000, 20000, 30000, "Rs a loan", OURS, rs, [E(0, "₹10,000–30,000 (assumed)", "XL-54", "Rs 10,000-30,000")], "XL-54"),
        F("comm", "pert", .01, .02, .03, "share of the loan", OURS, pc, [E(0, "1–3% (assumed)", "XL-54", "1-3% (assumed)")], "XL-54")], None),
    ("loan_vehicle", "other_loans", "Vehicle loan", "Two-wheeler / e-rickshaw loan", [
        F("takeup", "pert", .001, .005, .01, "share of active savers, a year", OURS, pc, [E(0, "0.1–1% (assumed)", "XL-54", "x 0.1-1%")], "XL-54"),
        F("ticket", "pert", 80000, 150000, 600000, "Rs a loan", OURS, lakh, [E(0, "₹1.5–6 lakh for autos and e-rickshaws (context)", "XL-54", "Rs 1.5-6 lakh")],
          "judgement; context: XL-54", "judgement: the ₹80,000 low covers two-wheeler loans; XL-54's ₹1.5–6 lakh is for autos and e-rickshaws"),
        F("comm", "pert", .005, .01, .02, "share of the loan", OURS, pc, [E(0, "0.5–2% (assumed)", "XL-54", "0.5-2% x")], "XL-54")], None),
    ("loan_home", "other_loans", "Home loan", "Home loan (affordable housing; once per saver, other lenders)", [
        F("takeup", "pert", .005, .015, .03, "share of active savers with no housing loan running, a year", OURS, pc,
          [E(0, "Aavas: 61% of borrowers self-employed", "XL-24", "61% self-employed"), E(0, "Home First serves incomes under ₹50,000 a month", "XL-25", "< Rs 50,000")],
          "XL-24, XL-25; operator (family income counts); judgement", "a ₹25 lakh loan over 20 years at ~9% has a ₹22,500 EMI, which needs ~₹45,000 a "
          "month of income at the 50% rule; his savers earn ₹20–40k (IV-04); family income counts (operator), so co-applicants widen eligibility"),
        F("ticket", "pert", 1000000, 2500000, 5000000, "Rs a loan", YOURS, lakh, [E(0, "average home loan ₹32 lakh", "XL-29", "HL 32.0 lakh"),
          E(0, "PMAY-U 2.0 subsidy up to ₹1.8 lakh", "XL-26", "1.80 lakh")], "operator ('upto 20-50 lakhs'); XL-29, XL-26"),
        F("comm", "pert", .003, .005, .010, "share of the loan, at disbursal, none taken back", GUIDE, pc,
          [E(0, "home-loan DSA 0.3–1% (typical 0.4–0.6%)", "XL-15", "0.3-1 (typical 0.4-0.6)")], "XL-15"),
        F("approval", "pert", .30, .45, .60, "share of applicants approved (secured)", OURS, pc, [], "judgement",
          "secured, so above unsecured approval; early-months factors and approval_growth (cap 80%) apply; no collection fees, no ticket growth")], None),
    ("loan_lap", "other_loans", "Loan on property", "Loan against property (his shop or home; once per saver)", [
        F("takeup", "pert", .002, .005, .01, "share of active savers with no housing loan running, a year", OURS, pc, [], "judgement"),
        F("ticket", "pert", 500000, 1500000, 3000000, "Rs a loan", OURS, lakh, [], "judgement"),
        F("comm", "pert", .005, .010, .015, "share of the loan, at disbursal, none taken back", GUIDE, pc,
          [E(0, "LAP DSA 0.5–1.5%", "XL-16", "0.5-1.5")], "XL-16"),
        F("approval", "pert", .30, .45, .60, "share of applicants approved (secured)", OURS, pc, [], "judgement",
          "secured, so above unsecured approval; early-months factors and approval_growth (cap 80%) apply; no collection fees, no ticket growth")], None),
]
FIXED_PRODUCT = {  # key: (value, unit, conf, src, shown, sub)
    "choti_ticket": (500, "Rs once, at month 24 if the SIP survives", PUB, "XO-01", "₹500 once", "at month 24"),
    "nps_ticket": (200, "Rs once, a new account", PUB, "XO-16", "₹200 once", "a new account"),
    "gold_comm": (0.024, "share of purchases", GUIDE, "LEV-036, LEV-037", "2.4%", "of purchases"),
    "recharge_ticket": (2600, "Rs of recharges a year", PUB, "XO-33", "₹2,600 a year", "Jio ARPU ₹216 a month"),
}
FIXED_TOK = {"choti_ticket": ("XO-01", "Up to Rs. 500"), "nps_ticket": ("XO-16", "Rs. 200"), "gold_comm": ("LEV-036", "~2.4"),
             "recharge_ticket": ("XO-33", "215.6")}

XSELL, RENEW_COMM = [], []
for _pre, _grp, _tile, _long, _rows, _rc in PRODUCTS:
    for _attr, _shape, _lo, _mo, _hi, _unit, _conf, _vf, _ev, _src, *_note in _rows:
        _pf = pcr if _vf is pc else (rsr if _vf is rs else (lambda v: lakh(round(v / 1e4) * 1e4)) if _vf is lakh else cnt)
        XSELL.append(In(_grp, f"{_pre}_{_attr}", f"{_long}: {ATTR[_attr]}", _tile, _shape, _lo, _mo, _hi, _unit, _conf, list(_ev), _src,
                        f"{_shape.upper() if _shape == 'pert' else _shape.capitalize()} {_vf(_lo)} / {_vf(_mo)} / {_vf(_hi)}"
                        + (": research gives only a flat range" if _shape == "triangular" else "") + ("; " + _note[0] if _note else "") + ".",
                        _vf, _pf, note=_note[0] if _note else "",
                        extra=(f" · paid {pc(_rc)}" if _attr == "renew" and _rc else (" · same rate" if _attr == "renew" and _pre == "two_wheeler" else ""))))
    if _rc:
        RENEW_COMM.append(_pre)


def fixed(key, name, short, value, unit, conf, src, why, shown, sub, low=None, high=None, group="decision", rule=False):
    i = In(group, key, name, short, "fixed", value if low is None else low, value, value if high is None else high, unit, conf, [], src, why,
           kind="decision", shown=shown, sub=sub)
    i.rule = rule
    return i


DECISIONS = [
    fixed("salary", "Agent's salary", "Agent's pay", SALARY, "Rs a month", YOURS, "operator; IV-13",
          "Your decision: ₹20,000 a month, plus agent_balance_pay capped at incentive_cap (a janta agent is paid ₹15,000–25,000, IV-13).",
          "₹20,000 + 0.25%", "of balance, cap ₹10,000"),
    fixed("agent_balance_pay", "Agent pay on his savers' balance, a year, paid monthly (rate ÷ 12 × that month's balance)", "Balance pay", 0.0025,
          "share of balance a year: 0.25% in company months 1–60 (likely, high), 0.10% from month 61 (low)", YOURS, "operator (16 Oct)",
          "Your decision: 'salary plus 0.25% of balance initially', reducing to 0.1% after 5 years; engine cost line cost_incentive.",
          "0.25% of balance", "0.10% after year 5", low=0.0010, rule=True),
    fixed("incentive_cap", "Cap on the agent's balance pay, per agent a month (the salary and the cap rise 7% a year)", "Pay cap", 10000,
          "Rs per agent a month", YOURS, "operator (17 Oct): 'salary only team is tough... some incentives'; tap: '0.25% of balance, capped'",
          "Your decision: 0.25% of balance, capped at ₹10,000 a month per agent; the salary and the cap rise 7% a year.", "₹10,000", "a month", rule=True),
    fixed("fleet_plan", "Company fleet plan", "Fleet", 300,
          "agents by month 18, then +150 a month to a cap of 5,000, within real-world city limits", YOURS, "final base plan (tables/base_*); operator (17 Oct)",
          "300 agents by m18, then +150 a month to a cap of 5,000, within real-world city limits", "300 by m18", "+150 a month to 5,000",
          group="company", rule=True),
    fixed("seed", "Seed round", "Seed", 1.3e8, "Rs at month 0 (₹13 crore; pre-money ₹40 crore)", YOURS, "final base plan (tables/base_rounds.csv)",
          "₹13 crore at m0, pre-money ₹40 crore", "₹13 crore", "month 0", group="company", rule=True),
    fixed("series_a", "Series A", "Series A", 5e8, "Rs at month 18 (₹50 crore, operator: \"50cr for sure\"; the minimum to keep cash ≥ ₹5 crore is about ₹19 crore, closing by m20)",
          YOURS, "operator (17 Oct)", "₹50 crore at m18", "₹50 crore", "month 18", group="company", rule=True),
    fixed("central_team", "Central team", "Central team", HEAD_CENTRAL[4], f"people: scales with the fleet (tables/base_headcount.csv): "
          f"{HEAD_CENTRAL[0]:.0f} at year 1, {HEAD_CENTRAL[4]:.0f} by year 5", YOURS, "final base plan (tables/base_headcount.csv)",
          "scales with the fleet (base_headcount.csv)", f"{HEAD_CENTRAL[0]:.0f} → {HEAD_CENTRAL[4]:.0f}", "scales with the fleet",
          low=HEAD_CENTRAL[0], group="company", rule=True),
    fixed("rounds", "Funding rounds (tables/base_rounds.csv)", "Rounds", len(ROUNDS), ROUNDS_TEXT, OURS, "final base plan (tables/base_rounds.csv)",
          ROUNDS_TEXT, f"{len(ROUNDS)} rounds", f"₹{ROUNDS_TOTAL:,.0f} crore in total", group="company", rule=True),
    fixed("marketplace_from", "Month the marketplace opens to a saver (loans, cards, insurance and more)", "Marketplace opens", 1, "month of saving",
          YOURS, "operator (16 Oct)", "Your decision 16 Oct: 'the marketplace opens as soon as possible. Simple. It's not at our cost.'",
          "month 1", "no cost to us"),
    fixed("visit_every", "Days between cash visits", "Visit gap", 2.5, "days", YOURS, "operator", "Your decision (every 2–3 days).", "2.5 days", ""),
    fixed("term", "Savings term", "Term", 12, "months", OURS, "janta yearly terms", "Our judgement: janta savers save in yearly terms.", "12 months", ""),
    fixed("upi_ramp", "UPI share ramp: straight line from 0 at age 1 to upi_12 at age 12, then flat", "UPI ramp", 12,
          "months to reach upi_12", OURS, "COHORT_INPUTS", "A rule, not a range: the share on UPI rises evenly through the first year.", "months 1–12", ""),
    fixed("extra_capacity_cost", "Cost of extra cash-collection capacity when visits exceed capacity", "Extra capacity", 20000,
          "Rs a month per 400 cash visits a day above capacity, pro-rata", YOURS, "COHORT_INPUTS",
          "A second agent or a helper at the same pay; replaces 'assume UPI absorbs it'.", "₹20,000 a month", "per 400 visits"),
    fixed("leaver_loan", "A saver who stops saving keeps paying his loan", "Leaver's loan", 1, "1 = yes: his loan runs to term; no repeat loan", OURS,
          "COHORT_INPUTS", "Held: his loan runs to term and he cannot get a repeat loan.", "to term", ""),
    fixed("discount", "Discount rate (0: cumulative P&L, undiscounted)", "Discount rate", 0.0, "a year", YOURS, "operator (16 Oct)",
          "operator: show cumulative P&L; let VC apply their discount", "0%", "undiscounted"),
    fixed("cash_route", "How a saver's cash reaches the fund: agent -> the fund's (AMC's) collection account + reconciliation", "Cash route", 1,
          "1 = agent → AMC collection account + reconciliation; legal opinion needed", YOURS, "operator (16 Oct); REG-066, REG-081",
          "The operator's design: agent → AMC collection account + reconciliation; legal opinion needed before the pilot. No change to the model: "
          "cash-deposit charges sit inside the ₹5 running cost.", "via AMC account", "legal opinion needed"),
    fixed("saver_fee", "Fee the saver pays us", "Saver fee", 0, "Rs", YOURS, "operator (16 Oct): 'No fee'", "Free to the saver.", "₹0", ""),
    fixed("licences", "Whose licences we use", "Licences", 1, "1 = partners: our own ARN for funds; insurance via a broker partner (we keep ~75%); "
          "lenders' direct sourcing partner", YOURS, "operator (16 Oct): 'Partners' licences'",
          "Partners' licences: our own fund-distributor code (ARN); insurance through a broker partner; lenders' direct sourcing partner.",
          "partners", "ARN, broker, lenders"),
    fixed("channel", "Acquisition and service channel", "Channel", 1, "1 = online + street acquisition, all served offline by the agent; no app-only",
          YOURS, "operator (17 Oct)", "online + street acquisition, all served offline by the agent; no app-only", "omni-channel", "served offline"),
    fixed("managers", "Manager cost: the founder in the pilot", "Managers", 0, "Rs a month of manager cost in the pilot", YOURS, "operator (16 Oct)",
          "founder in the pilot; a team lead per N agents at scale is not counted", "founder", ""),
    fixed("horizon", "Horizon (the model runs both)", "Horizons", 60, "months: both 36 (low) and 60", YOURS, "operator", "Your decision: 3 and 5 years.",
          "3, 5 years", "", low=36),
    fixed("owed", "Share of the loan still owed when it goes 90+ days bad", "Owed when bad", OWED, "share of the loan", OURS, "addendum 3 (judgement)",
          "Held at half the loan: it turns the loss rate into the share of loans reaching 90+ days.", "half", "of the loan", group="collections", rule=True),
    fixed("fee_mult_start", "Fee multiplier on the DSA rate at company month 1", "Fee multiplier, start", 1.0, "× the starting fee", YOURS,
          "operator (17 Oct)", "start like a DSA...", "1.0×", "month 1", group="loans", rule=True),
    fixed("fee_mult_end", "Fee multiplier on the DSA rate, reached at company month 60 (straight line)", "Fee multiplier, end", 1.5, "× the starting fee",
          YOURS, "operator (17 Oct)", "1.5x over 5 years", "1.5×", "month 60", group="loans", rule=True),
    fixed("rate", "Loan interest rate (EMI basis only)", "Loan rate", 0.26, "a year", OURS, "derived: agent3_funnel_inputs.csv",
          "Derived: the ₹10,073 EMI on ₹2.5 lakh over 36 months; only states the EMI basis, no fee depends on it.", "26%", "EMI basis only",
          group="loans", rule=True),
]
for _k, (_v, _u, _c, _s, _sh, _sub) in FIXED_PRODUCT.items():
    _prod = next(pr for pr in PRODUCTS if _k.startswith(pr[0] + "_"))
    DECISIONS.append(fixed(_k, f"{_prod[3]}: {_u}", _prod[2], _v, _u, _c, _s, "Fixed by the scheme or the source, not a range.", _sh, _sub,
                           group=_prod[1], rule=True))
for _pre in RENEW_COMM:
    _rc = next(rc for p, *_, rc in PRODUCTS if p == _pre)
    DECISIONS.append(fixed(f"{_pre}_renew_comm", f"{next(pr[3] for pr in PRODUCTS if pr[0] == _pre)}: commission on a renewal", "Renewal commission", _rc, "share of the renewal premium", PUB,
                           "REG-054, XO-19, XO-20", "Draft cap on renewals (5% health and retail; 7.5% term life).", pc(_rc), "on renewals",
                           group="insurance", rule=True))
BASE_ROWS = list(csv.DictReader((T / "base_inputs.csv").open()))
BASE_MAP = [  # key, group, Input prefix, value, tile name, shown, sub[, low]
    ("city_towns", "cities", "Urban towns on the rank-size", 4000, "Urban towns", "4,000", "on the rank-size curve"),
    ("city_served", "cities", "Cities a fleet serves", 500, "Cities served", "500", "population ≥ 1 lakh"),
    ("city_ncr_share", "cities", "NCR's share of urban India", 0.063, "NCR's share", "6.3%", "of urban India"),
    ("city_rank_q", "cities", "Rank-size exponent q", 0.8648, "Rank-size q", "0.865", "fitted, not census"),
    ("city_cap", "cities", "City cap", 0.2, "City cap", "20%", "of a city's pool"),
    ("city_saturation", "cities", "Saturation curve", 2, "Slowdown", "soft", "× (1 − (pen/cap)²)"),
    ("city_refill", "cities", "Pool refill", 0.03, "Pool refill", "3% a year", "new shops, migrants"),
    ("city_max_new", "cities", "Most new cities a month", 4, "New cities", "≤4 a month", "operating pace"),
    ("city_open_headroom", "cities", "Open the next city when", 25000, "Open next city", "25,000", "headroom a head"),
    ("city_launch_cost", "cities", "City launch cost", 300000, "City launch", "₹3 lakh", "once per city"),
    ("city_office", "cities", "City office", 50000, "City office", "₹50,000", "a month per city"),
    ("city_manager", "cities", "City manager", 80000, "City manager", "₹80,000", "a month, one a city"),
    ("team_lead", "cities", "Team lead, one per 10 agents", 40000, "Team lead", "₹40,000", "a month per 10 agents"),
    ("fleet_m18", "fleet", "Agents by month 18", 300, "Fleet by m18", "300 agents", "m3 25 … m18 300"),
    ("fleet_hires_after_m18", "fleet", "Hires a month after month 18", 150, "Hires after m18", "150 a month", "agents"),
    ("fleet_cap", "fleet", "Agent cap", 5000, "Agent cap", "5,000", "then replace leavers"),
    ("agent_attrition", "fleet", "Agents who leave a year", 0.3, "Agents who leave", "30% a year", "replaced next month"),
    ("saver_loss_on_replace", "fleet", "Savers who stop when their agent", 0.1, "Savers lost", "10%", "when he is replaced"),
    ("agent_statutory", "fleet", "Agent statutory on top of salary", 3000, "Agent statutory", "₹3,000", "a month"),
    ("hire_cost", "fleet", "Hiring and kit", 12000, "Hiring and kit", "₹12,000", "per hire"),
    ("pay_rise", "fleet", "Pay rise, agents and staff", 0.07, "Pay rise", "7% a year", "agents and staff"),
    ("acq_share_agent_cost", "fleet", "Acquisition share of agent cost", 0.5, "Acquisition share", "50% → 20%", "of agent cost, m1–12 → m60", 0.2),
    ("pay_founders", "central", "Founders (Founders)", 150000, "Founders", "₹1.5 lakh", "a month each"),
    ("pay_tech_lead", "central", "Tech lead (Technology)", 250000, "Tech lead", "₹2.5 lakh", "a month"),
    ("pay_engineer", "central", "Engineers (Technology)", 120000, "Engineers", "₹1.2 lakh", "a month each"),
    ("pay_product", "central", "Product and design (Technology)", 150000, "Product, design", "₹1.5 lakh", "a month each"),
    ("pay_compliance_head", "central", "Compliance and operations head", 150000, "Compliance head", "₹1.5 lakh", "a month"),
    ("pay_ops_exec", "central", "Operations executives", 40000, "Ops executives", "₹40,000", "a month each"),
    ("pay_growth", "central", "Growth and marketing", 120000, "Growth", "₹1.2 lakh", "a month each"),
    ("pay_finance_admin", "central", "Finance and admin", 70000, "Finance, admin", "₹70,000", "a month each"),
    ("pay_risk_lead", "central", "Risk and fraud lead", 150000, "Risk lead", "₹1.5 lakh", "from 100 agents"),
    ("pay_cash_recon", "central", "Cash reconciliation executives", 35000, "Cash reconciliation", "₹35,000", "1 per 50 agents"),
    ("pay_hr", "central", "HR and recruiting executives", 50000, "HR, recruiting", "₹50,000", "1 per 100 agents"),
    ("pay_support_lead", "central", "Customer support lead", 60000, "Support lead", "₹60,000", "from 50,000 savers"),
    ("central_scale", "central", "Engineers and ops executives after m18", 50, "Team scaling", "+1 per 50", "agents beyond 60"),
    ("statutory_central", "costs", "Statutory on central", 0.1, "Statutory", "10%", "of central pay"),
    ("laptop_cost", "costs", "Laptop per central hire", 60000, "Laptop", "₹60,000", "per central hire"),
    ("tools_per_person", "costs", "Tools per central person", 1000, "Tools", "₹1,000", "a person a month"),
    ("app_cloud", "costs", "App: cloud, SMS and KYC tools", 150000, "App running", "₹1.5 lakh", "a month"),
    ("app_integrations", "costs", "App integrations, months 1-3", 1500000, "App build", "₹15 lakh", "months 1–3"),
    ("licences_setup", "costs", "Licences and setup, one-time", 750000, "Licences, setup", "₹7.5 lakh", "once"),
    ("licences_yearly", "costs", "Licences and compliance, yearly", 1000000, "Licences, yearly", "₹10 lakh", "a year"),
    ("head_office", "costs", "Head office", 150000, "Head office", "₹1.5 lakh", "a month"),
    ("travel", "costs", "Travel", 100000, "Travel", "₹1 lakh", "a month"),
    ("brand_marketing", "costs", "Brand marketing", 200000, "Brand marketing", "₹2 lakh", "a month"),
    ("bureau_pull", "costs", "Bureau pull per personal-loan", 25, "Bureau pull", "₹25", "per loan application"),
    ("fraud_provision", "costs", "Fraud provision on cash collected", 0.0005, "Fraud provision", "0.05%", "of cash collected"),
    ("cash_cover_share", "costs", "Cash cover: the larger of", 0.00015, "Cash cover share", "0.015%", "of his cash, min ₹1,000"),
    ("contingency", "costs", "Contingency on every expensed line", 0.1, "Contingency", "10%", "on expensed lines"),
    ("income_tax", "costs", "Income tax on profit", 0.25, "Income tax", "25%", "after past losses"),
    ("interest_on_cash", "costs", "Interest on cash", 0.055, "Interest on cash", "5.5% a year", ""),
    ("commission_lag", "costs", "Commissions arrive after", 2, "Commission lag", "2 months", ""),
    ("depreciation_months", "costs", "Depreciation of laptops", 36, "Depreciation", "36 months", "straight line"),
    ("raise_cost_seed", "costs", "Fund-raising cost", 500000, "Raising the seed", "₹5 lakh", "cost"),
    ("raise_cost_round", "costs", "Fund-raising cost", 1500000, "Raising a round", "₹15 lakh", "each later round"),
    ("nbfc_month", "nbfc", "NBFC-ICC acquired or built", 24, "NBFC licence", "month 24", "acquired or built"),
    ("nbfc_licence_cost", "nbfc", "Licence cost", 10000000, "Licence cost", "₹1 crore", "once"),
    ("nbfc_nof", "nbfc", "Net owned funds held", 100000000, "Net owned funds", "₹10 crore", "from the licence month"),
    ("nbfc_opex", "nbfc", "NBFC opex: credit, risk", 1500000, "NBFC running cost", "₹15 lakh", "a month"),
    ("nbfc_opex_scaling", "nbfc", "NBFC opex that scales with the book", 500000, "Cost with the book", "₹5 lakh", "a month per ₹500 cr"),
    ("onbook_start", "nbfc", "On-book lending starts", 30, "On-book lending", "month 30", "starts"),
    ("nbfc_yield", "nbfc", "Yield on the outstanding book", 0.26, "Yield", "26% a year", "= rate"),
    ("nbfc_processing_fee", "nbfc", "Processing fee at disbursal", 0.02, "Processing fee", "2%", "paid by the borrower"),
    ("nbfc_cost_of_funds", "nbfc", "Cost of borrowings", 0.135, "Cost of funds", "13.5% a year", ""),
    ("nbfc_leverage", "nbfc", "Borrowings at most this multiple", 3.0, "Leverage cap", "3× equity", "borrowings"),
    ("onbook_share", "nbfc", "On-book share of personal-loan volume", 0.3, "On our book", "30%", "best part by score"),
    ("onbook_loss_mult", "nbfc", "On-book loss as a multiple", 0.6, "On-book loss", "0.6× loss", "the top 30% by score"),
    ("nbfc_equity_share", "nbfc", "NBFC equity = the larger of NOF", 0.25, "NBFC equity", "max(₹10 cr, 25%)", "of the book"),
    ("capital_floor_reg", "nbfc", "Capital floor", 0.15, "Capital, regulatory", "15%", "of the book"),
    ("capital_floor_op", "nbfc", "Capital floor", 0.20, "Capital, operating", "20% (25% held)", "of the book"),
    ("onbook_dsa_fee", "nbfc", "DSA origination fee on on-book loans", 0, "DSA fee on book", "none", "we are the lender"),
    ("onbook_coll_fee", "nbfc", "Collection fees on on-book loans", 0, "Collection fees", "internal", "partners' 70% unchanged"),
    ("seed_premoney", "rounds", "Seed pre-money", 400000000, "Seed pre-money", "₹40 crore", ""),
    ("stepup_a", "rounds", "Step-up into round A", 3.0, "Step-up into A", "3×", ""),
    ("stepup_b", "rounds", "Step-up into round B", 3.0, "Step-up into B", "3×", ""),
    ("stepup_c", "rounds", "Step-up into round C", 2.5, "Step-up into C", "2.5×", ""),
    ("stepup_d", "rounds", "Step-up into round D", 2.0, "Step-up into D", "2×", ""),
    ("stepup_e", "rounds", "Step-up into round E", 1.5, "Step-up into E", "1.5×", ""),
    ("stepup_later", "rounds", "Step-up for later rounds", 1.5, "Later rounds", "1.5×", ""),
    ("stepup_extension", "rounds", "Step-up for later rounds", 1.0, "Extensions", "1×", ""),
    ("premoney_rule", "rounds", "Pre-money = the higher of", 1, "Pre-money rule", "higher of the two", "never below last post"),
    ("lens_a_arr", "rounds", "Lens pricing", 25, "Round A lens", "25× ARR", "or 0.45× AUM"),
    ("lens_later_arr", "rounds", "Lens pricing", 20, "Later lens", "20× ARR", "or 0.45× AUM"),
    ("dilution_cap", "rounds", "Dilution cap per round", 0.25, "Dilution cap", "25%", "a round"),
    ("round_cadence", "rounds", "Cadence", 12, "Cadence", "every 12 months", "seed m0, A m12 …"),
    ("early_round_runway", "rounds", "A round comes earlier", 6, "Early round", "6 months", "of forward burn"),
    ("round_size_months", "rounds", "Round size", 24, "Round size", "24 months", "of burn (or 18)"),
    ("round_buffer", "rounds", "Round size", 100000000, "Round buffer", "₹10 crore", "on top"),
    ("esop_pool", "rounds", "ESOP pool", 0.1, "ESOP pool", "10%", "topped up at A, B"),
    ("unicorn_threshold", "lenses", "Unicorn threshold", 100000000000, "Unicorn", "₹10,000 crore", "$1B at ₹100"),
    ("lens_arr", "lenses", "Lens 1: x ARR", 20, "Lens: ARR", "20×", "fee + interest ARR"),
    ("lens_aum", "lenses", "Lens 2: x AUM", 0.45, "Lens: AUM", "0.45×", "month-end fund"),
    ("lens_nbfc_pb", "lenses", "Lens 3 (cross-check)", 3, "Lens: NBFC", "3× book equity", "+ 20× fee ARR"),
    ("model_horizon", "model", "Horizon", 96, "Horizon", "96 months", "the unicorn plan"),
    ("mc_draws", "model", "Monte Carlo draws", 1000, "MC draws", "1,000", "fleet and funding fixed"),
]
BASE_SKIPPED = ("Addressable pool: urban", "Addressable pool, range", "Lifetime credit loss after recoveries")   # city_pool; `loss`


def _base_row(prefix):
    m = [r for r in BASE_ROWS if r["Input"].startswith(prefix)]
    assert len(m) == 1, (prefix, len(m))
    return m[0]


for _key, _grp, _pre, _val, _short, _shown, _sub, *_lo in BASE_MAP:
    _r = _base_row(_pre)
    try:
        _num = float(_r["Value"].replace(",", ""))
        assert abs(_num - _val) <= 1e-9 * max(1, abs(_val)) or _lo, (_key, _num, _val)
    except ValueError:
        pass                                               # text values ("soft", "50% -> 20%", "rule", ...) are encoded in BASE_MAP
    DECISIONS.append(fixed(_key, _r["Input"], _short, _val, _r["Unit"] or "", _r["Confidence"], _r["Source"],
                           f"Base plan (tables/base_inputs.csv): {_r['Value']} {_r['Unit']}".strip(), _shown, _sub,
                           low=_lo[0] if _lo else None, group=_grp, rule=True))
assert {r["Input"] for r in BASE_ROWS} == {_base_row(m[2])["Input"] for m in BASE_MAP} | {r["Input"] for r in BASE_ROWS if r["Input"].startswith(BASE_SKIPPED)}
BASE_KEYS = [m[0] for m in BASE_MAP] + ["city_pool"]

for _d in DECISIONS:
    _d.rule = getattr(_d, "rule", False)

REFERENCE = [
    In("agent", "signup_growth", "Sign-ups per agent grow each year from year 2 (superseded 17 Oct by signup_decline_y5)", "Sign-up growth a year", "fixed",
       0.0, 0.0, 0.0, "a year", OURS, [], "superseded 17 Oct", "Superseded 17 Oct: sign-ups now decline to signup_decline_y5 by year 5; no growth.",
       pc, pc, kind="superseded"),
    In("fund", "janta_rate", "What a janta daily deposit earns him: a public-sector bank's savings-account rate", "Janta deposit rate", "triangular",
       0.025, 0.025, 0.027, "a year", YOURS, [], "operator (16 Oct)",
       "The operator: a janta daily deposit earns a public-sector bank's savings-account rate; SBI / PNB savings rates are about 2.5–2.7%.",
       pc, pcr, kind="reference",
       note="the exact bank rate is not yet in research: verify it; a reference for the fund page, NOT a model input to the NPV"),
    In("decision", "proven_after", "Months of saving before he is offered products (superseded 16 Oct by marketplace_from = 1)", "Proven saver", "fixed",
       6, 6, 6, "months (offers from month 7)", YOURS, [], "operator", "Superseded 16 Oct: the marketplace opens in month 1, not month 7.",
       num, num, kind="superseded"),
    In("fund", "trail_liquid", "Fund commission a year, if a liquid fund (not chosen)", "Liquid fund (not chosen)", "pert", 0.00025, 0.0005, 0.001,
       "share of balance a year", GUIDE,
       [E(0.0005, "paid at 5 of 6 fund houses: 0.05%", "TC-21", "5 bps at 5 of 6"), E(0.0003, "2025–26 tables: 0.03–0.10%", "TC-22", "0.03-0.10", 0.001),
        E(0.0008, "fee gap 0.08–0.12%: a ceiling", "BM-01", "8 bps", 0.0012)],
       "TC-21, TC-22, BM-01", "Reference only (not chosen 16 Oct): what fund houses actually pay on liquid funds.", pc, pcr, (0, 0.0013), (0.0002, 0.00105),
       kind="reference"),
    In("cards", "other", "Insurance and other products, a proven saver a year (v2 single line)", "Insurance and more (v2)", "pert", 8, 63, 259,
       "Rs a proven saver a year", OURS, [E(63, "our product build, middle ₹63", "XO-39", "8 / 63 / 259")], "XO-39, XO-10",
       "Legacy only (legacy=True reproduces v2): replaced by the product lines.", rs, rsr, kind="legacy"),
]

CITY_POOL = In("cities", "city_pool", "Addressable pool: urban self-employed (own-account workers, employers, helpers)", "Addressable pool", "pert",
               6.5e7, 7.0e7, 7.7e7, "people", OURS, [E(0, "40.4% of urban workers self-employed", "NG-002", "40.4", axis=False)],
               "NG-002 (40.4% of urban workers self-employed, 34.0% own-account or employer); urban workers about 19 crore (lead's estimate)",
               "PERT 6.5–7.7 crore around 7 crore: the base plan's pool and its Monte Carlo range (tables/base_inputs.csv).",
               lambda v: f"{v / 1e7:.1f} cr", lambda v: f"{v / 1e7:.2f} cr")
for _d in [d for d in DECISIONS if d.key == "series_a"]:          # superseded 17 Oct by `rounds`
    DECISIONS.remove(_d)
    _d.kind, _d.why = "superseded", "Superseded 17 Oct by `rounds` (the final base's six rounds); kept for the record."
    REFERENCE.append(_d)
INPUTS = CORE + XSELL + [CITY_POOL]
I = {i.key: i for i in INPUTS + DECISIONS + REFERENCE}
COHORT_KEYS = ["signups_run", "ramp_months", "r3", "r12", "churn_late", "daily", "days", "amount_growth", "term", "rollover", "withdraw_m", "trail",
               "upi_12", "upi_ramp", "visit_every", "capacity", "extra_capacity_cost", "apply", "eligible", "approved_first", "approved_repeat",
               "tenure", "ticket", "fee", "taken_back", "loss", "recovered", "leaver_loan", "card_share", "card_fee",
               "salary", "kyc_cost", "support_cost", "discount", "horizon", "early_cured", "fee_early", "fee_b3", "owed", "rate", "marketplace_from",
               "early_takeup_mult", "early_approval_mult", "fund_return", "signup_growth", "takeup_growth", "approval_growth",
               "ticket_growth", "topup_share", "topup_size", "cash_cover", "ins_partner_share", "saver_fee", "licences", "cash_route",
               "managers", "agent_balance_pay", "signup_decline_y5", "online_lead_share", "lead_cost", "channel", "fee_mult_start", "fee_mult_end",
               "incentive_cap", "fleet_plan", "seed", "series_a", "central_team", "rounds"]
assert all(k in I for k in COHORT_KEYS), [k for k in COHORT_KEYS if k not in I]
assert len(I) == len(INPUTS) + len(DECISIONS) + len(REFERENCE)
for _gone in ("coll_fee", "rec_fee", "trail_debt", "approved", "signups", "dpd30_rate", "dpd30_emis", "dpd30_resolve", "dpd30_fee",
              "cure_b1", "cure_b2", "fee_b1", "fee_b2"):
    assert _gone not in I


# ---------- evidence: every id must be in research/, with the words we quote ----------
ID_RE = re.compile(r"\b[A-Z]{2,4}-\d{2,3}\b")
_ROWS = {}
for _p in sorted(R.glob("*.csv")):
    for _row in csv.reader(_p.open()):
        if _row and ID_RE.fullmatch(_row[0]):
            _ROWS.setdefault(_row[0], (_p.name, ",".join(_row)))


def ev_check(e):
    ids = ID_RE.findall(e.ids)
    for x in ids:
        assert x in _ROWS, f"{x} not found in research/*.csv"
    if e.ids.endswith(".md"):
        assert e.tok in (R / e.ids).read_text(), f"{e.ids}: '{e.tok}' not found"
        return e.ids
    if e.tok:
        assert ids and e.tok in _ROWS[ids[0]][1], f"{ids[0]}: '{e.tok}' not found"
    return ",".join(ids)


LOANS_EV = [E(N.EVIDENCE_LOANS[0], f"older evidence: low {N.EVIDENCE_LOANS[0]}", "agent3_funnel_inputs", who="last"),
            E(N.EVIDENCE_LOANS[1], f"middle {N.EVIDENCE_LOANS[1]}", "agent3_funnel_inputs", who="last"),
            E(N.EVIDENCE_LOANS[2], f"high {N.EVIDENCE_LOANS[2]}", "agent3_funnel_inputs", who="last"),
            E(LAST["loans_per_100"], f"last deck {LAST['loans_per_100']:.1f}", "xs_inputs_v2", who="last"),
            E(3.0, "XL-48 middle: 3", "XL-48", "x 3%")]
FEE_EV = [E(250000 * 0.01 * 0.975, "1% fee: ₹2,438", "agent_npv", who="last"), E(LAST["fee_per_loan"], "last deck ₹6,398", "xs_inputs_v2", who="last"),
          E(250000 * 0.045 * 0.975, "Paytm-like 4.5%: ₹10,969", "XL-07", "4.5-5 (no DLG)")]
SRC = {"loans": "XL-41, XL-42, LS-06, XL-48", "keep": "IV-01, IV-11, IV-12, TB-11, XO-05", "save": "IV-03",
       "agent": "IV-01, IV-07, IV-12, TC-35, REG-045, REG-069, TB-18, XO-05, NG-033", "fund": "TC-21, TC-22, TC-23, BM-01, XB-04, OWN-02",
       "rest": "LEV-009, XL-07, XL-09, XL-13, XL-41, NG-028, XB-08, XB-07, QM-22, SE-01, EVD-03, SE-02",
       "coll": "GAP-01, GAP-02, XB-07, NG-015, MAC-03", "xsell": "XO-01 to XO-39, GAP-04 to GAP-06, XL-28, XL-54, LEV-036"}
CHECKED = set()
for _e in [e for i in INPUTS + DECISIONS + REFERENCE for e in i.ev] + LOANS_EV + FEE_EV:
    CHECKED.update(x for x in ev_check(_e).split(",") if x)
for _k, (_id, _tok) in FIXED_TOK.items():
    ev_check(E(0, "", _id, _tok))
for _x in ID_RE.findall(" ".join([i.src + " " + i.note + " " + i.why for i in INPUTS + DECISIONS + REFERENCE] + list(SRC.values()))):
    if _x not in _ROWS:
        raise KeyError(_x)
    CHECKED.add(_x)


# ---------- sampling ----------
def draw():
    rng = np.random.default_rng(SEED)
    d = {i.key: i.sample(rng, DRAWS) for i in INPUTS}
    # agreed 16 Oct: in a bad year approvals fall as losses rise (Gaussian copula, rho -0.5 between loss and each approval)
    r2 = np.random.default_rng(SEED + 3)
    zl = r2.standard_normal(DRAWS)
    for k in ("approved_first", "approved_repeat"):
        d[k] = I[k].frozen().ppf(stats.norm.cdf(RHO * zl + math.sqrt(1 - RHO ** 2) * r2.standard_normal(DRAWS)))
    d["loss"] = I["loss"].frozen().ppf(stats.norm.cdf(zl))
    return d


def summary(x):
    return {"p10": float(np.percentile(x, 10)), "p50": float(np.percentile(x, 50)), "p90": float(np.percentile(x, 90)), "mean": float(np.mean(x))}


def p90_share(loss, rec):
    """Share of loans that ever go 90+ days bad, from the loss anchor (addendum 3)."""
    return loss / (OWED * (1 - rec))


def coll_fees(d, loss=None):
    p90 = p90_share(d["loss"] if loss is None else loss, d["recovered"])
    early, late = d["early_cured"] * d["fee_early"], p90 * d["recovered"] * d["fee_b3"]
    return early, late, p90


def xsell(d, first_year=False):
    """Cross-sell money per active saver a year, by product: once holdings settle (default) or in the first year (XO-39 method)."""
    g = lambda k: d[k] if k in d else I[k].likely
    out = {}
    for pre, grp, *_rest in PRODUCTS:
        if grp == "insurance":
            t, P, c1 = g(f"{pre}_takeup"), g(f"{pre}_ticket"), g(f"{pre}_comm")
            r = g(f"{pre}_renew") if f"{pre}_renew" in I else 0.0
            c2 = g(f"{pre}_renew_comm") if f"{pre}_renew_comm" in I else c1
            ps = g("ins_partner_share")                     # a broker partner's licence: we keep this share of every insurance commission
            if first_year:
                out[pre] = t * P * c1 * ps
            else:
                h = t / (1 - r + t)
                out[pre] = ((1 - h) * t * P * c1 + h * r * P * c2) * ps
        elif pre == "sip":
            t, m, tr, s = g("sip_takeup"), g("sip_ticket"), g("sip_comm"), g("sip_renew")
            out[pre] = t * 6 * m * tr if first_year else t / (1 - s + t) * 12 * m * (s / (1 - s) + 0.5) * tr
        elif pre == "gold":
            t, m, b = g("gold_takeup"), g("gold_ticket"), g("gold_renew")
            out[pre] = (t if first_year else t / (1 - b + t)) * 12 * m * g("gold_comm")
        elif pre == "choti":
            out[pre] = g("choti_takeup") * g("choti_ticket") * g("choti_survive24") / 2
        elif pre == "nps":
            out[pre] = g("nps_takeup") * g("nps_ticket")
        elif pre in ("loan_home", "loan_lap"):              # housing: take-up x approval x ticket x fee (once per saver; first years' flow)
            out[pre] = g(f"{pre}_takeup") * g(f"{pre}_approval") * g(f"{pre}_ticket") * g(f"{pre}_comm")
        else:                                              # fd, recharge, bills, other loans: take-up x ticket x fee
            out[pre] = g(f"{pre}_takeup") * g(f"{pre}_ticket") * g(f"{pre}_comm")
    return out


def survival(r3, r12, late, n_months=36):
    """Share of a cohort still saving at months 0..n. Returns (curve array [draws, n+1], share of draws capped)."""
    r12c = np.minimum(r12, r3)
    h1, h2 = 1 - r3 ** (1 / 3), 1 - (r12c / r3) ** (1 / 9)
    m = np.arange(n_months + 1)[None, :]
    s = np.where(m <= 3, (1 - h1[:, None]) ** m, np.where(m <= 12, r3[:, None] * (1 - h2[:, None]) ** (m - 3),
                                                         r12c[:, None] * (1 - late[:, None]) ** (m - 12)))
    return s, float(np.mean(r12 > r3))


def deposits(daily, days_, growth, n_months=36):
    """Deposits a month per active saver at ages 1..n: his daily amount grows once at each completed year saved."""
    age = np.arange(1, n_months + 1)[None, :]
    return daily[:, None] * days_[:, None] * (1 + growth[:, None]) ** ((age - 1) // 12)


def derived(d):
    loans = 100 * d["apply"] * d["eligible"] * d["approved_first"]
    fee_loan = d["ticket"] * d["fee"] * (1 - d["taken_back"])
    early, late, p90 = coll_fees(d)
    coll = early + late
    behind = d["early_cured"] + p90
    xs = xsell(d)
    xs_total = sum(xs.values())
    xs_first = sum(xsell(d, first_year=True).values())
    once = 100 * d["card_share"] * d["card_fee"]
    yearly = loans * (fee_loan + coll) + 100 * xs_total
    lr = loans / 100
    loans_rep = 100 * lr / (1 + lr * d["tenure"] / 12)        # steady state: a saver with a loan running does not apply
    # open choice: approvals fall as losses rise (Gaussian copula, correlation -0.5; the same two marginals)
    loss_i = np.random.default_rng(SEED + 1).permutation(d["loss"])     # the same draws with the agreed link broken, for comparison
    yearly_i = loans * (fee_loan + sum(coll_fees(d, loss_i)[:2])) + 100 * xs_total
    surv, capped = survival(d["r3"], d["r12"], d["churn_late"])
    dep = deposits(d["daily"], d["days"], d["amount_growth"])
    mid = {k: np.array([I[k].likely]) for k in I}
    mf = lambda x: float(np.asarray(x).ravel()[0])
    m_loans = mf(100 * mid["apply"] * mid["eligible"] * mid["approved_first"])
    m_fee = mf(mid["ticket"] * mid["fee"] * (1 - mid["taken_back"]))
    me, ml, m90 = (mf(v) for v in coll_fees(mid))
    m_xs = {k: mf(v) for k, v in xsell(mid).items()}
    m_surv, _ = survival(mid["r3"], mid["r12"], mid["churn_late"])
    m_dep = deposits(mid["daily"], mid["days"], mid["amount_growth"])
    L_loans, L_fee, L_rec = LAST["loans_per_100"], LAST["fee_per_loan"], LAST["coll_per_loan"]
    L_c = 1 - LAST["r12"] ** (1 / 12)
    rows = [
        ("loans_per_100", "First loans per 100 active savers a year", "loans", loans, m_loans, L_loans, "100 × apply × eligible × approved_first"),
        ("loans_per_100_months_1_6", "First loans per 100 active savers a year, in a saver's months 1–6", "loans",
         loans * d["early_takeup_mult"] * d["early_approval_mult"], m_loans * 0.5 * 0.6, "", "loans × early_takeup_mult × early_approval_mult (agreed)"),
        ("loans_per_100_repeat_rule", "The same, if a saver with a loan running does not apply (steady state)", "loans", loans_rep,
         m_loans / (1 + m_loans / 100 * 3), "", "loans ÷ (1 + loans/100 × tenure in years); none of this bites in a saver's first loan year"),
        ("fee_per_loan", "What one loan earns us at the start (origination fee kept, a DSA's rate)", "Rs a loan", fee_loan, m_fee, L_fee,
         "loan size × fee × (1 − taken back), company month 1"),
        ("fee_per_loan_month60", "What one loan earns us at month 60 (1.5× the starting fee)", "Rs a loan", fee_loan * I["fee_mult_end"].likely,
         m_fee * I["fee_mult_end"].likely, "", "× fee_mult_end"),
        ("loss_rate", "Money lost on loans, after recoveries (the input, as drawn)", "share of money lent", d["loss"], 0.03, "",
         "pert 1.5 / 3 / 5%; falls on the lender, not us (no first-loss cover)"),
        ("share_90plus", "Implied share of loans that ever go 90+ days bad", "share of loans", p90, m90, "",
         "loss / (owed × (1 − recovered)); compare NG-015 10.2% (self-employed unsecured, < ₹10 lakh) and MAC-03 3.6% (personal loans > ₹50k)"),
        ("share_falling_behind", "Share of loans that fall 31–90 days behind (brought back early + go 90+)", "share of loans", behind,
         mf(mid["early_cured"]) + m90, "", "early_cured + p90; checked against 50%"),
        ("draws_behind_above_50pct", "Share of draws where early_cured + p90 is above 50%", "share of draws", (behind > 0.5).astype(float), "", "",
         "the addendum 3 check"),
        ("coll_fee_early_per_loan", "Fees on early accounts brought back, per loan made (~9 months after)", "Rs a loan", early, me, "",
         "early_cured × fee_early"),
        ("coll_fee_b3_per_loan", "Fees on 90+ accounts recovered, per loan made (~18 months after)", "Rs a loan", late, ml, L_rec,
         "p90 × recovered × fee_b3; last deck: recovery fees ₹155 a loan"),
        ("collections_per_loan", "All collection fees per loan made", "Rs a loan", coll, me + ml, L_rec, "early + 90+ (undiscounted)"),
        ("origination_per_100", "Origination fees per 100 active savers a year", "Rs a year", loans * fee_loan, m_loans * m_fee, L_loans * L_fee,
         "loans × fee per loan"),
        ("collections_per_100", "Collection fees per 100 active savers a year", "Rs a year", loans * coll, m_loans * (me + ml), L_loans * L_rec,
         "loans × collection fees per loan"),
    ]
    for pre, grp, tile, *_ in PRODUCTS:
        rows.append((f"xsell_{pre}", f"Cross-sell: {tile}, per active saver a year (holdings settled)", "Rs a year", xs[pre], m_xs[pre], "", grp))
    rows += [
        ("xsell_total", "Cross-sell, all products, per active saver a year (holdings settled)", "Rs a year", xs_total, sum(m_xs.values()), OLD_OTHER,
         f"sum of the {len(PRODUCTS)} products; last deck: one line, ₹63 (XO-39)"),
        ("xsell_total_months_1_6", "Cross-sell, all products, per active saver a year, in months 1–6", "Rs a year",
         xs_total * d["early_takeup_mult"], sum(m_xs.values()) * 0.5, "", "× early_takeup_mult (agreed)"),
        ("fund_return_on_balance", "What the fund earns him a year on ₹42,000 held", "Rs a year", BALANCE * d["fund_return"], BALANCE * 0.07, "",
         "balance × fund_return (agreed)"),
        ("gain_vs_janta", "What he gains a year on ₹350 a day against a janta deposit (₹42,000 held)", "Rs a year",
         BALANCE * (d["fund_return"] - I["janta_rate"].likely), BALANCE * (I["fund_return"].likely - I["janta_rate"].likely), "",
         "balance × (fund_return − janta_rate 2.5%); janta_rate is a reference row, not an NPV input"),
        ("xsell_total_first_year", "Cross-sell, all products, first-year sales only (the XO-39 method)", "Rs a year", xs_first,
         sum(mf(v) for v in xsell(mid, first_year=True).values()), OLD_OTHER, "take-up × ticket × first-year commission"),
        ("cost_to_win_per_saver", "Cost to win a saver: salary ÷ sign-ups + online share × lead cost", "Rs a saver",
         SALARY / d["signups_run"] + d["online_lead_share"] * d["lead_cost"], SALARY / 100 + 0.5 * 250, "",
         "₹20,000 ÷ sign-ups a month + online_lead_share × lead_cost; against ₹499 online (story_unit)"),
        ("card_once_per_active", "A credit card, once, per active saver", "Rs once", d["card_share"] * d["card_fee"], 30.0, 62.5, "card share × fee per card"),
        ("marketplace_yearly_per_100", "Marketplace money per 100 active savers, every year", "Rs a year", yearly,
         m_loans * (m_fee + me + ml) + 100 * sum(m_xs.values()), L_loans * (L_fee + L_rec) + 100 * LAST["other"],
         "origination + collections + cross-sell (holdings settled); approvals and losses linked (agreed, rho -0.5)"),
        ("marketplace_once_per_100", "Marketplace money per 100 active savers, once (cards)", "Rs once", once, 100 * 0.03 * 1000.0,
         100 * LAST["card_share"] * LAST["card_fee"], "100 × card share × fee per card"),
        ("marketplace_yearly_per_100_independent", "Marketplace money per 100 active savers, every year, if approvals and losses were independent",
         "Rs a year", yearly_i, "", "", "comparison only: the loss draws shuffled against the approvals; same marginals"),
    ]
    for m in (3, 6, 12, 24, 36):
        rows.append((f"still_saving_m{m}", f"Share of a cohort still saving at month {m}", "share", surv[:, m], mf(m_surv[0, m]),
                     (1 - L_c) ** m, "curve from r3, r12, churn_late; last deck: the same monthly drop-off from r12 = 55%"))
    for a in (1, 13, 25):
        rows.append((f"deposits_age{a}", f"Deposits a month per active saver at age {a}", "Rs a month", dep[:, a - 1], mf(m_dep[0, a - 1]),
                     LAST["daily"] * LAST["days"], "daily × days × (1 + growth)^(years saved)"))
    out = []
    for key, name, unit, x, at_mid, last, how in rows:
        out.append({"key": key, "name": name, "unit": unit, **{k: round(v, 4) for k, v in summary(x).items()},
                    "at_likely_values": "" if at_mid == "" else round(at_mid, 4), "last_deck": "" if last == "" else round(last, 4), "how": how})
    samples = {"loans": loans, "fee_loan": fee_loan, "yearly": yearly, "once": once, "surv": surv, "dep": dep, "capped": capped,
               "m_surv": m_surv[0], "m_dep": m_dep[0], "xs": xs, "xs_total": xs_total, "xs_first": xs_first, "coll": (early, late, p90, behind)}
    return out, samples


def write(name, rows):
    with (T / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def sig(v):
    return float(f"{v:.6g}")


def proposal_rows(d):
    rows = []
    rng = np.random.default_rng(SEED + 2)
    for i in INPUTS + DECISIONS + REFERENCE:
        x = d[i.key] if i.key in d else (i.sample(rng, DRAWS) if i.shape != "fixed" else None)
        s = summary(x) if x is not None else {k: i.likely for k in ("p10", "p50", "p90", "mean")}
        evs = "; ".join([e.text() for e in i.ev] + ([i.note] if i.note else []))
        rows.append({"group": i.group, "key": i.key, "name": i.name, "kind": i.kind, "shape": i.shape, "low": sig(i.low), "likely": sig(i.likely),
                     "high": sig(i.high), **{k: sig(v) for k, v in s.items()}, "unit": i.unit, "confidence": i.conf, "evidence_points": evs,
                     "source_ids": i.src, "why_this_shape": i.why})
    return rows


# ---------- drawing ----------
EVC = {"ev": THEM, "you": INK, "last": MUTED, "need": BAD}
SVG_W, PADX = 1000, 14


def svg(w, h, body):
    """build_qr_visual.svg with a small side margin, so labels at either edge are never cut."""
    return V.svg(w, h, body).replace(f'viewBox="0 0 {w} {h}"', f'viewBox="{-PADX} 0 {w + 2 * PADX} {h}"', 1)


def tk(x, y, s, size=9, weight=400, fill=MUTED, anchor="middle", halo=False):
    """A tick, axis or evidence label: excluded from the page word count."""
    h = ' stroke="#fff" stroke-width="3" paint-order="stroke"' if halo else ""
    return (f'<text class="tk" x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{h}>'
            f'{html.escape(s)}</text>')


def tw(s, size, bold=False):
    return len(s) * size * (0.54 if bold else 0.5)


def dot(cx, cy, conf, r=5.5):
    if conf == YOURS:
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}"/>'
    if conf == PUB:
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{THEM}"/>'
    if conf == GUIDE:
        return f'<circle cx="{cx}" cy="{cy}" r="{r - 1}" fill="#fff" stroke="{THEM}" stroke-width="2.2"/>'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREY}"/>'


def icon(name, x, y, s, c):
    if name == "card":
        g = (f'<rect x="3" y="10" width="42" height="28" rx="4" fill="{c}"/><rect x="3" y="16" width="42" height="5" fill="#fff" opacity="0.55"/>'
             f'<rect x="8" y="28" width="12" height="4" rx="1" fill="#fff"/>')
        return f'<g transform="translate({x},{y}) scale({s / 48})">{g}</g>'
    return V.icon(name, x, y, s, c)


def nice_ticks(lo, hi, n=4):
    span = hi - lo
    mag = 10 ** math.floor(math.log10(span / n))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if span / (m * mag) <= n)
    v, out = math.ceil(lo / step - 1e-9) * step, []
    while v <= hi + 1e-9:
        out.append(round(v, 12))
        v += step
    return out


def axis(x, w, base, lo, hi, X, fmt, size, n, skip=()):
    """Axis line and tick labels; a label never runs off the page, and none sits under an evidence marker."""
    s = [f'<line x1="{x}" y1="{base}" x2="{x + w}" y2="{base}" stroke="{MUTED}" stroke-width="1"/>']
    for t in nice_ticks(lo, hi, n):
        lab = fmt(t)
        half = tw(lab, size) / 2
        cx = min(max(X(t), half - PADX + 1), SVG_W + PADX - half - 1)
        s.append(f'<line x1="{X(t):.1f}" y1="{base}" x2="{X(t):.1f}" y2="{base + 3}" stroke="{MUTED}" stroke-width="1"/>')
        if all(abs(X(t) - sx) > 7 for sx in skip):
            s.append(tk(cx, base + 13, lab, size))
    return "".join(s)


def place(items, gap=7):
    """Stack labels in lanes under the axis. A label may not overlap another in its lane, may not sit on the leader of an
    item drawn deeper, and its own leader may not pass through a label in a shallower lane. Tries anchors middle, end, start,
    and every order of the items, keeping the layout with the fewest crossings, then the fewest lanes."""
    def greedy(order):
        placed, cross = [], 0
        for it in order:
            best = None
            for k in range(8):
                for anchor in it["anchors"]:
                    left, right = it["ext"](anchor)
                    ok = True
                    for p in placed:
                        if p["lane"] == k and not (left >= p["right"] + gap or right <= p["left"] - gap):
                            ok = False
                        elif it["lx"] is not None and p["lane"] < k and p["left"] - 3 <= it["lx"] <= p["right"] + 3:
                            ok = False
                        elif p["lx"] is not None and p["lane"] > k and left - 3 <= p["lx"] <= right + 3:
                            ok = False
                        if not ok:
                            break
                    if ok:
                        best = (k, anchor, left, right)
                        break
                if best:
                    break
            if best is None:
                cross += 1
                for k in range(12):
                    left, right = it["ext"](it["anchors"][0])
                    if all(p["lane"] != k or left >= p["right"] + gap or right <= p["left"] - gap for p in placed):
                        best = (k, it["anchors"][0], left, right)
                        break
            k, anchor, left, right = best
            placed.append({**it, "lane": k, "anchor": anchor, "left": left, "right": right})
        return (cross, 1 + max(p["lane"] for p in placed), sum(p["lane"] for p in placed)), placed

    if not items:
        return []
    base = sorted(items, key=lambda t: t["x"])
    orders = permutations(base) if len(base) <= 6 else [base]
    return min((greedy(list(o)) for o in orders), key=lambda r: r[0])[1]


def evidence(evs, X, x0, x1, base, top, size):
    """Evidence under an axis: a marker on the axis with a dotted leader, a range bar, or a red line we must clear."""
    items = []
    lo_page, hi_page = -PADX + 1, SVG_W + PADX - 1
    for e in evs:
        if not e.axis:
            continue
        w = tw(e.label, size, True)
        a = X(e.v)
        b = X(e.hi) if e.hi is not None else a
        lo_b, hi_b = max(x0 + w / 2, lo_page + w / 2), min(x1 - w / 2, hi_page - w / 2)
        if e.hi is not None:
            c = min(max((a + b) / 2, min(lo_b, hi_b)), max(lo_b, hi_b))
            ext = (lambda anc, c=c, w=w, a=a, b=b: (min(c - w / 2, a), max(c + w / 2, b)))
            items.append({"x": a, "lx": None, "ext": ext, "anchors": ("middle",), "e": e, "a": a, "b": b, "c": c})
        else:
            def ext(anc, a=a, w=w, lo_b=lo_b, hi_b=hi_b, x0=max(x0, lo_page), x1=min(x1, hi_page)):
                if anc == "middle":
                    c = min(max(a, min(lo_b, hi_b)), max(lo_b, hi_b))
                    return c - w / 2, c + w / 2
                left = a + 4 - w if anc == "end" else a - 4
                left = min(max(left, x0), max(x1 - w, x0))
                return left, left + w
            items.append({"x": a, "lx": a, "ext": ext, "anchors": ("middle", "end", "start"), "e": e, "a": a, "b": a, "c": a})
    placed = place(items)
    n = 1 + max([p["lane"] for p in placed] or [-1])
    s, lh, y0 = [], size + 9, base + 33
    for p in placed:
        e, a, b = p["e"], p["a"], p["b"]
        col = EVC[e.who]
        yl = y0 + p["lane"] * lh
        cx = (p["left"] + p["right"]) / 2 if e.hi is None else p["c"]
        if e.who == "need":
            s.append(f'<line x1="{a}" y1="{top - 2}" x2="{a}" y2="{yl - size - 1}" stroke="{BAD}" stroke-width="1.8" stroke-dasharray="4 3"/>')
        elif e.hi is None:
            s.append(f'<path d="M{a},{base - 0.5} l-4,-7 h8 z" fill="{col}"/>')
            s.append(f'<line x1="{a}" y1="{base + 4}" x2="{a}" y2="{yl - size - 1}" stroke="{col}" stroke-width="0.9" stroke-dasharray="1.5 2"/>')
        else:
            yb = yl - size - 2
            s.append(f'<line x1="{a}" y1="{yb}" x2="{b}" y2="{yb}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        s.append(tk(cx, yl, e.label, size, 600, col))
    marks = [X(e.v) for e in evs if e.axis and e.hi is None]
    return "".join(s), n, marks


def plabels(X, x, w, top, p10, p50, p90, pf, size):
    a, b, c = f"p10 {pf(p10)}", f"p50 {pf(p50)}", f"p90 {pf(p90)}"
    wa, wb, wc = tw(a, size), tw(b, size, True), tw(c, size)
    ra = min(max(X(p10) + 3, x + wa), x + w - wc - 10)
    lc = max(min(X(p90) - 3, x + w - wc), ra + 8)
    cb = min(max(X(p50), x + wb / 2), x + w - wb / 2)
    return tk(cb, top - 15, b, size, 700, INK) + tk(ra, top - 3, a, size, 400, INK, "end") + tk(lc, top - 3, c, size, 400, INK, "start")


def curve(i, x, y, w, hp, ax=None, evs=True, ev_size=9.5, tick_size=9, p_size=9.5, show_p=True, label=True, lab_size=12.5,
          label_text=None, n_ticks=5, col=US, label_y=None):
    """One density curve with the p10-p90 band, p10/p50/p90 marks, axis ticks and evidence ticks. Returns (svg, bottom y)."""
    lo, hi = ax or i.ax
    X = lambda v: x + (min(max(v, lo), hi) - lo) / (hi - lo) * w
    top = y + (26 if show_p else 4)
    base = top + hp
    d = i.frozen()
    xs = np.linspace(lo, hi, 320)
    pdf = np.nan_to_num(d.pdf(xs), posinf=0.0)
    m = pdf.max()
    Y = lambda p: base - min(p / m, 1.0) * hp
    p10, p50, p90 = (float(d.ppf(q)) for q in (0.1, 0.5, 0.9))
    s = []
    pts = " ".join(f"L{X(a):.1f},{Y(p):.1f}" for a, p in zip(xs, pdf))
    s.append(f'<path d="M{X(lo):.1f},{base} {pts} L{X(hi):.1f},{base} Z" fill="{col}" opacity="0.16"/>')
    bx = np.concatenate(([p10], xs[(xs > p10) & (xs < p90)], [p90]))
    bp = np.nan_to_num(d.pdf(bx), posinf=0.0)
    s.append(f'<path d="M{X(p10):.1f},{base} ' + " ".join(f"L{X(a):.1f},{Y(p):.1f}" for a, p in zip(bx, bp)) +
             f' L{X(p90):.1f},{base} Z" fill="{col}" opacity="0.5"/>')
    s.append(f'<path d="M{X(xs[0]):.1f},{Y(pdf[0]):.1f} {pts}" fill="none" stroke="{col}" stroke-width="1.6"/>')
    s.append(f'<line x1="{X(p50):.1f}" y1="{base}" x2="{X(p50):.1f}" y2="{Y(float(d.pdf(p50))):.1f}" stroke="{INK}" stroke-width="1.6"/>')
    if i.mean_mark or i.mean_differs(0.10):
        mu = i.mean()
        right = X(mu) > x + w * 0.55
        s.append(f'<line x1="{X(mu):.1f}" y1="{base}" x2="{X(mu):.1f}" y2="{Y(float(d.pdf(mu))):.1f}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="3 2"/>')
        s.append(tk(X(mu) + (-4 if right else 4), Y(float(d.pdf(mu))) + 10, f"mean {i.pf(mu)}", p_size, 700, INK, "end" if right else "start", halo=True))
    if show_p:
        s.append(plabels(X, x, w, top, p10, p50, p90, i.pf, p_size))
    nl, es, marks = 0, "", []
    if evs and i.ev:
        es, nl, marks = evidence(i.ev, X, x, x + w, base, top, ev_size)
    s.append(axis(x, w, base, lo, hi, X, i.vf, tick_size, n_ticks, marks))
    s.append(es)
    bottom = base + 33 + nl * (ev_size + 9) + (2 if nl else -12)
    if label:
        ly = label_y if label_y is not None else bottom
        txt = label_text or f"{i.short}: likely {i.v(i.likely)} ({i.rng_text()})"
        s.append(dot(x + 6, ly + 9 - lab_size * 0.35, i.conf, lab_size * 0.42))
        s.append(V.text(x + 16, ly + 9, txt, lab_size, 700, INK))
        bottom = ly + lab_size + 6
    return "".join(s), bottom


def hist(x_samples, x, y, w, hp, ax, vf, pf, evs, label, bins=44, ev_size=10, tick_size=9.5, col=US, n_ticks=6, label_y=None):
    lo, hi = ax
    X = lambda v: x + (min(max(v, lo), hi) - lo) / (hi - lo) * w
    top = y + 26
    base = top + hp
    v = np.clip(x_samples, lo, hi - 1e-9)
    counts, edges = np.histogram(v, bins=np.linspace(lo, hi, bins + 1))
    p10, p50, p90 = np.percentile(x_samples, [10, 50, 90])
    m = counts.max()
    s = []
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        if c == 0:
            continue
        h = c / m * hp
        inside = p10 <= (a + b) / 2 <= p90
        s.append(f'<rect x="{X(a) + 0.6:.1f}" y="{base - h:.1f}" width="{max(X(b) - X(a) - 1.2, 0.5):.1f}" height="{h:.1f}" fill="{col}" opacity="{0.62 if inside else 0.2}"/>')
    k50 = min(int((p50 - lo) / (hi - lo) * bins), bins - 1)
    s.append(f'<line x1="{X(p50):.1f}" y1="{base}" x2="{X(p50):.1f}" y2="{base - counts[k50] / m * hp - 4:.1f}" stroke="{INK}" stroke-width="2"/>')
    for q in (p10, p90):
        s.append(f'<line x1="{X(q):.1f}" y1="{top}" x2="{X(q):.1f}" y2="{base}" stroke="{INK}" stroke-width="0.8" stroke-dasharray="2 2"/>')
    s.append(plabels(X, x, w, top, p10, p50, p90, pf, 10.5))
    es, nl, marks = evidence(evs, X, x, x + w, base, top, ev_size)
    s.append(axis(x, w, base, lo, hi, X, vf, tick_size, n_ticks, marks))
    s.append(es)
    bottom = base + 33 + nl * (ev_size + 9) + 2
    ly = label_y if label_y is not None else bottom
    s.append(V.text(x, ly + 10, label, 13.5, 800, INK))
    return "".join(s), ly + 16


def fan(x, y, w, h, curves, start, mid, ylo, yhi, yfmt, ytick, xlab, ylab, col=US, overlays=(), marks=()):
    """A fan over age: p10-p90 band of `curves` (draws x ages) and the likely-values line; overlays are (values, colour,
    label) lines; marks are (age, value, label, colour) points."""
    n = curves.shape[1]
    ages = np.arange(n) + start
    X = lambda a: x + (a - ages[0]) / (ages[-1] - ages[0]) * w
    Y = lambda v: y + h - (v - ylo) / (yhi - ylo) * h
    q10, q90 = np.percentile(curves, [10, 90], axis=0)
    s = []
    for t in nice_ticks(ylo, yhi, ytick):
        s.append(f'<line x1="{x}" y1="{Y(t):.1f}" x2="{x + w}" y2="{Y(t):.1f}" stroke="{RULE}" stroke-width="1"/>' + tk(x - 6, Y(t) + 3.5, yfmt(t), 9.5, 400, MUTED, "end"))
    for t in range(0, int(ages[-1]) + 1, 6):
        if t >= ages[0]:
            s.append(tk(X(t), y + h + 15, str(t), 9.5))
    s.append(f'<line x1="{x}" y1="{y + h}" x2="{x + w}" y2="{y + h}" stroke="{MUTED}" stroke-width="1"/>')
    pts = " ".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in zip(ages, q90)) + " " + " ".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in zip(ages[::-1], q10[::-1]))
    s.append(f'<polygon points="{pts}" fill="{col}" opacity="0.32"/>')
    s.append(f'<polyline points="{" ".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in zip(ages, mid))}" fill="none" stroke="{col}" stroke-width="2.6"/>')
    ends = [(Y(mid[-1]), "our likely", col, 800)]
    for vals, c, lab in overlays:
        s.append(f'<polyline points="{" ".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in zip(ages, vals))}" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="6 4"/>')
        ends.append((Y(vals[-1]), lab, c, 700))
    ends.sort()
    for k in range(1, len(ends)):                          # keep end labels at least 13 units apart
        if ends[k][0] - ends[k - 1][0] < 13:
            ends[k] = (ends[k - 1][0] + 13,) + ends[k][1:]
    for yy, lab, c, wt in ends:
        s.append(tk(X(ages[-1]) + 6, yy + 4, lab, 11, wt, c, "start"))
    for a, v, lab, c in marks:
        s.append(f'<circle cx="{X(a):.1f}" cy="{Y(v):.1f}" r="4.5" fill="{c}" stroke="#fff" stroke-width="1.5"/>' + tk(X(a) + 8, Y(v) + 4, lab, 10.5, 700, c, "start", halo=True))
    s.append(tk(x + w / 2, y + h + 34, xlab, 12, 600, MUTED))
    s.append(tk(x, y - 12, ylab, 12, 700, MUTED, "start"))
    return "".join(s), X, Y


# ---------- pages ----------
TILE_GROUPS = [("saver", "Saver", "jar"), ("agent", "Agent", "person"), ("fund", "Fund", "coin"), ("loans", "Loans", "bank"),
               ("collections", "Collections", "hands"), ("xsell", "Cross-sell", "card"), ("online", "Online, cities", "phone")]
XSELL_GROUPS = ("cards", "insurance", "investments", "payments", "other_loans")
OP_DECISIONS = [d for d in DECISIONS if not d.rule]
TOTAL = 15


def gkey(i):
    return "xsell" if i.group in XSELL_GROUPS else "online" if i.group == "cities" else i.group


def legend(x, y, size=11):
    s, cx = [], x
    for c in CONFS:
        s.append(dot(cx + 6, y - size * 0.35, c, size * 0.45))
        s.append(tk(cx + 16, y, c, size, 600, INK, "start"))
        cx += 16 + tw(c, size, True) + 18
    return "".join(s), cx


def p_agree():
    s = []
    tiles = TILE_GROUPS + [("decision", "Fixed", "doc")]
    for k, (g, name, ic) in enumerate(tiles):
        r, c = divmod(k, 4)
        x, y = c * 158, r * 196
        dec = g == "decision"
        items = [i for i in INPUTS if gkey(i) == g] if not dec else DECISIONS
        s.append(f'<rect x="{x}" y="{y}" width="146" height="182" rx="14" fill="{FLAT if dec else PAPER}"/>')
        s.append(icon(ic, x + 14, y + 14, 40, MUTED if dec else US))
        s.append(V.text(x + 132, y + 50, str(len(items)), 34, 800, MUTED if dec else US, "end"))
        s.append(V.text(x + 14, y + 86, name, 15, 700, INK))
        per, step, r0 = (15, 8.4, 3.0) if len(items) > 80 else (10, 13, 4.4) if len(items) > 18 else (6, 20, 6.5)
        for j, i in enumerate(items):
            rr, cc = divmod(j, per)
            if dec:
                s.append(f'<rect x="{x + 14 + cc * step - r0}" y="{y + 112 + rr * (step - 1) - r0}" width="{2 * r0}" height="{2 * r0}" rx="2" fill="{GREY}"/>')
            else:
                s.append(dot(x + 20 + cc * step, y + 112 + rr * (step - 1), i.conf, r0))
    lg, _ = legend(0, 404, 11.5)
    s.append(lg)
    cx = 655
    s.append(tk(cx, -2, "✓ AGREED", 12, 700, GOOD, "start"))
    chips = [("Agreed", "Still saving: 55%"), ("Agreed", "Sign-ups 100 → 70; half online"), ("Agreed", "Debt fund"),
             ("Agreed", "Cards 3%"), ("Agreed", "Approvals, losses linked"), ("Agreed", "25% kept at term end"),
             ("Agreed", "IRDAI caps"),
             ("Agreed", "Months 1–6 lower"),
             ("Agreed", "Rates grow"), ("Agreed", "Agent: ₹20,000 + 0.25%, capped"),
             ("Agreed", "Fee: DSA → 1.5× by year 5"),
             ("Agreed", "Company: 300 → 5,000 agents; 6 rounds, ₹1,108 crore"),
             ("Agreed", "Cities: 20% cap, soft slowdown, 3% refill, ≤4 a month"),
             ("Agreed", "NBFC from m30: top 30% of loans on our book")]
    n_open = 0
    y = 6
    for k, (state, t) in enumerate(chips):
        lines = [t]
        if len(t) * 12.5 * 0.54 > 300:                                          # a long chip wraps onto two lines
            cut = t.find("; ") if "; " in t else t.find(", ", len(t) // 2 - 6)
            lines = [t[:cut], t[cut + 2:]] if cut > 0 else [t]
        hc = 31 + 15 * (len(lines) - 1)
        ok = state != "open"
        s.append(f'<rect x="{cx}" y="{y}" width="350" height="{hc}" rx="15.5" fill="{V.TINT["good" if ok else "bad"]}"/>')
        if ok:
            s.append(f'<circle cx="{cx + 20}" cy="{y + 15.5}" r="10.5" fill="{GOOD}"/>' + V.text(cx + 20, y + 20, "✓", 12, 800, "#fff", "middle"))
        else:
            n_open += 1
            s.append(f'<circle cx="{cx + 20}" cy="{y + 18.5}" r="12" fill="{BAD}"/>' + V.text(cx + 20, y + 23, str(n_open), 12, 800, "#fff", "middle"))
        fs = 12.5 if len(lines) > 1 else min(12.5, 300 / (len(t) * 0.54))
        sep = ";|" if "; " in t else ",|"
        s.append(V.text(cx + 40, y + 20, sep.join(lines) if len(lines) > 1 else t, fs, 700, INK, lh=15))
        y += hc + 6
    return svg(1000, max(412, y), "".join(s)), n_open


def tile(i, x, y, w=140, h=118, tick=9.5):
    if i.shape == "fixed":
        return dtile(i, x, y, w, h)
    ref = i.kind == "reference"
    rng_line = i.rng_text() + (f" · mean {i.pf(i.mean())}" if i.mean_differs() or i.mean_mark else "") + i.extra
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{FLAT if ref else PAPER}"/>',
         V.text(x + 8, y + 15, i.short, 10, 700, MUTED if ref else INK), dot(x + w - 9, y + 11, i.conf, 4.8),
         V.text(x + 8, y + 37, i.v(i.likely), 17, 800, MUTED if ref else US),
         V.text(x + 8, y + 50, rng_line, min(9.5, (w - 14) / max(len(rng_line), 1) / 0.5), 500, MUTED)]
    col = MUTED if ref else US
    lo, hi = i.gax
    d = i.frozen()
    X = lambda v: x + 8 + (min(max(v, lo), hi) - lo) / (hi - lo) * (w - 16)
    base, hp = y + h - 22, h - 76
    xs = np.linspace(lo, hi, 160)
    pdf = np.nan_to_num(d.pdf(xs), posinf=0.0)
    m = pdf.max()
    Y = lambda p: base - min(p / m, 1.0) * hp
    p10, p50, p90 = (float(d.ppf(q)) for q in (0.1, 0.5, 0.9))
    pts = " ".join(f"L{X(a):.1f},{Y(p):.1f}" for a, p in zip(xs, pdf))
    s.append(f'<path d="M{X(lo):.1f},{base} {pts} L{X(hi):.1f},{base} Z" fill="{col}" opacity="0.16"/>')
    bx = np.concatenate(([p10], xs[(xs > p10) & (xs < p90)], [p90]))
    bp = np.nan_to_num(d.pdf(bx), posinf=0.0)
    s.append(f'<path d="M{X(p10):.1f},{base} ' + " ".join(f"L{X(a):.1f},{Y(p):.1f}" for a, p in zip(bx, bp)) + f' L{X(p90):.1f},{base} Z" fill="{col}" opacity="0.5"/>')
    s.append(f'<path d="M{X(xs[0]):.1f},{Y(pdf[0]):.1f} {pts}" fill="none" stroke="{col}" stroke-width="1.3"/>')
    s.append(f'<line x1="{X(p50):.1f}" y1="{base}" x2="{X(p50):.1f}" y2="{Y(float(d.pdf(p50))):.1f}" stroke="{INK}" stroke-width="1.3"/>')
    s.append(f'<line x1="{x + 8}" y1="{base}" x2="{x + w - 8}" y2="{base}" stroke="{MUTED}" stroke-width="0.8"/>')
    ticks = nice_ticks(lo, hi, 3)
    labs = [i.vf(t) for t in ticks]
    if sum(tw(l, tick) for l in labs) > (w - 16) * 0.8:            # keep tick labels apart: every other one
        ticks, labs = ticks[::2], labs[::2]
    for t, lab in zip(ticks, labs):
        half = tw(lab, tick) / 2
        s.append(f'<line x1="{X(t):.1f}" y1="{base}" x2="{X(t):.1f}" y2="{base + 2.5}" stroke="{MUTED}" stroke-width="0.8"/>')
        s.append(tk(min(max(X(t), x + 4 + half), x + w - 4 - half), base + 13, lab, tick))
    return "".join(s)


def dtile(i, x, y, w=140, h=62):
    yy = y + (h - 62) / 2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{FLAT}"/>' + dot(x + w - 9, y + 11, i.conf, 4.6)
            + V.text(x + 8, yy + 16, i.short, 10, 700, MUTED)
            + V.text(x + 8, yy + 40, i.shown, 15 if len(i.shown) < 13 else 12.5, 800, INK) + V.text(x + 8, yy + 54, i.sub, 9, 500, MUTED))


def blank(x, y, w, h, text_="—"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{RULE}" stroke-width="1.2" stroke-dasharray="4 3"/>'
            + tk(x + w / 2, y + h / 2 + 4, text_, 10, 600, MUTED))


def glabel(x, y, h, text_):
    lines = text_.split("|")
    s = [f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{US}"/>']
    y0 = y + h / 2 - (len(lines) - 1) * 6 + 3
    for k, ln in enumerate(lines):
        s.append(V.text(x + 9, y0 + k * 12, ln.upper(), 8.5, 800, US))
    return "".join(s)


def legend_row(y, x0=60):
    lg, cx = legend(x0, y, 10.5)
    return (lg + f'<rect x="{cx + 6}" y="{y - 9}" width="22" height="10" fill="{US}" opacity="0.5"/>' + V.text(cx + 34, y, "8 in 10 draws (p10–p90)", 10.5, 600, INK)
            + f'<line x1="{cx + 186}" y1="{y - 11}" x2="{cx + 186}" y2="{y + 1}" stroke="{INK}" stroke-width="1.6"/>' + V.text(cx + 194, y, "p50", 10.5, 600, INK))


def grid(rows, decisions=(), TH=118, dec_per=6, dec_w=140):
    s = []
    TW, G, LW = 140, 6, 60
    y = 0
    for row in rows:
        x = 0
        for lab, keys in row:
            s.append(glabel(x, y, TH, lab))
            x += LW
            for k in keys:
                s.append(tile(I[k], x, y, TW, TH))
                x += TW + G
            x += 8
        y += TH + 10
    for r0 in range(0, len(decisions), dec_per):
        part = decisions[r0:r0 + dec_per]
        s.append(glabel(0, y, 62, "FIXED" if r0 == 0 else "FIXED|(MORE)"))
        for j, i in enumerate(part):
            s.append(dtile(i, LW + j * (dec_w + G), y, dec_w))
        y += 62 + 8
    y += 16
    s.append(legend_row(y))
    return svg(1000, y + 6, "".join(s))


def matrix(cols, rows, TH=112):
    """Columns are products, rows are what we need for each (take-up, ticket, commission, renewal)."""
    s = []
    LW, G = 66, 6
    TW = (1000 - LW - G * (len(cols) - 1)) / len(cols)
    y = 0
    for rkey, rlab in rows:
        s.append(glabel(0, y, TH, rlab))
        for j, (pre, cells) in enumerate(cols):
            x = LW + j * (TW + G)
            cell = cells.get(rkey)
            if cell is None:
                s.append(blank(x, y, TW, TH))
            elif cell in I:
                s.append(tile(I[cell], x, y, TW, TH))
            else:
                s.append(blank(x, y, TW, TH, cell))
        y += TH + 8
    y += 14
    s.append(legend_row(y, LW))
    return svg(1000, y + 6, "".join(s))


def prod_cells(pre):
    keys = [k for k in I if k.startswith(pre + "_") and not k.endswith("_renew_comm")]
    m = {}
    for k in keys:
        attr = k[len(pre) + 1:]
        m["renew" if attr in ("renew", "survive24") else attr] = k
    return pre, m


def p_grid1():
    return grid([[("SAVER", ["daily", "days", "amount_growth", "r3", "r12", "churn_late"])],
                 [("AGENT", ["signups_run", "signup_decline_y5", "online_lead_share", "lead_cost", "ramp_months", "capacity"])],
                 [("AGENT|(MORE)", ["upi_12", "kyc_cost"]), ("COSTS", ["support_cost", "cash_cover"])],
                 [("FUND", ["trail", "fund_return", "rollover", "withdraw_m"])]], OP_DECISIONS, TH=112, dec_per=7, dec_w=125)


def p_grid2():
    return grid([[("LOANS", ["apply", "eligible", "approved_first", "approved_repeat", "tenure", "ticket"])],
                 [("LOANS|(MORE)", ["fee", "taken_back", "loss", "rate"]), ("CARDS", ["card_share", "card_fee"])],
                 [("COLLEC-|TIONS", ["early_cured", "fee_early", "recovered", "fee_b3", "owed"]), ("INSUR-|ANCE", ["ins_partner_share"])],
                 [("MONTHS|1–6", ["early_takeup_mult", "early_approval_mult"]), ("ONLINE", ["online_cac", "online_r12"])],
                 [("GROWS|WITH|HISTORY", ["takeup_growth", "approval_growth", "ticket_growth", "topup_share", "topup_size"])]], TH=110)


def p_grid3():
    cols = [prod_cells(p) for p, g, *_ in PRODUCTS if g == "insurance"]
    return matrix(cols, [("takeup", "TAKE-UP|A YEAR"), ("ticket", "PREMIUM|A YEAR"), ("comm", "FIRST-YEAR|COMMISSION"), ("renew", "RENEWS|A YEAR")])


def p_grid4():
    cols = [prod_cells(p) for p, g, *_ in PRODUCTS if g == "investments"]
    for pre, m in cols:
        if pre == "choti":
            m["comm"] = "the ₹500 is the fee"
        if pre == "nps":
            m.setdefault("comm", "the ₹200 is the fee")
            m.setdefault("renew", "one-off")
    return matrix(cols, [("takeup", "TAKE-UP|A YEAR"), ("ticket", "TICKET"), ("comm", "OUR|COMMISSION"), ("renew", "KEEPS|GOING")])


def emi(P, rate, months):
    r = rate / 12
    return P * r / (1 - (1 + r) ** -months)


HOME_EMI = emi(2500000, 0.09, 240)                  # ₹25 lakh over 20 years at ~9%: about ₹22,500 a month


def p_cities():
    return grid([[("LIMITS", ["city_pool", "city_cap", "city_saturation", "city_refill", "city_max_new", "city_open_headroom"])],
                 [("THE CURVE|AND COSTS", ["city_towns", "city_served", "city_ncr_share", "city_rank_q", "city_launch_cost", "city_office"])],
                 [("FIELD|MANAGERS", ["city_manager", "team_lead"]), ("FLEET", ["fleet_m18", "fleet_hires_after_m18", "fleet_cap"])],
                 [("FLEET|(MORE)", ["agent_attrition", "saver_loss_on_replace", "agent_statutory", "hire_cost", "pay_rise", "acq_share_agent_cost"])]],
                TH=100)


def p_nbfc():
    return grid([[("LICENCE", ["nbfc_month", "nbfc_licence_cost", "nbfc_nof", "onbook_start", "nbfc_opex", "nbfc_opex_scaling"])],
                 [("THE BOOK", ["onbook_share", "nbfc_yield", "nbfc_processing_fee", "nbfc_cost_of_funds", "nbfc_leverage", "onbook_loss_mult"])],
                 [("CAPITAL|AND FEES", ["nbfc_equity_share", "capital_floor_reg", "capital_floor_op", "onbook_dsa_fee", "onbook_coll_fee", "loss"])]],
                TH=104)


def p_grid5():
    cols = [prod_cells(p) for p, g, *_ in PRODUCTS if g in ("payments", "other_loans")]
    sv = matrix(cols, [("takeup", "TAKE-UP|A YEAR"), ("ticket", "TICKET"), ("comm", "OUR FEE"), ("approval", "APPROVAL")], TH=106)
    h = int(re.search(r'viewBox="[^"]*? ([0-9.]+)"', sv).group(1))
    note = (f"Home-loan caveat: a ₹25 lakh loan over 20 years at ~9% has a {rsr(HOME_EMI)} EMI, which needs ~{rsr(2 * HOME_EMI)} a month of income "
            "at the 50% rule;|his savers earn ₹20–40k (IV-04), but family income counts (operator), so co-applicants widen who qualifies.")
    extra = f'<rect x="66" y="{h + 4}" width="934" height="46" rx="10" fill="{V.TINT["warn"]}"/>' + V.text(80, h + 22, note, 11.5, 700, INK, lh=17)
    return sv.replace(f' {h}"', f' {h + 56}"', 1).replace("</svg>", extra + "</svg>")


def p_loans(S):
    s = []
    W, GAP = 270, 45
    kw = dict(ev_size=9, tick_size=8.5, p_size=9, lab_size=11.5, n_ticks=4)
    keys = ("apply", "eligible", "approved_first")
    ly = max(curve(I[k], j * (W + GAP), 0, W, 54, label=False, **kw)[1] for j, k in enumerate(keys))
    for k, key in enumerate(keys):
        x = k * (W + GAP)
        sv, b = curve(I[key], x, 0, W, 54, label_y=ly, **kw)
        s.append(sv)
        if k < 2:
            s.append(V.text(x + W + GAP / 2, 66, "×", 30, 300, MUTED, "middle"))
    y0 = b + 4
    s.append(V.arrow(300, y0, 300, y0 + 30, MUTED, 2.5) + V.text(286, y0 + 24, "=", 26, 400, MUTED, "end"))
    h1 = (S["loans"], 0, y0 + 26, 600, 130, (0, 12), num, num, LOANS_EV, "First loans per 100 active savers a year")
    h2 = (S["fee_loan"], 670, y0 + 26, 330, 130, (0, 18000), inr, rsr, FEE_EV, "Fee per loan at the start: size × fee × kept")
    ly = max(hist(*h1)[1], hist(*h2, bins=30, n_ticks=3)[1]) - 16
    sv, b1 = hist(*h1, label_y=ly)
    s.append(sv)
    sv, b2 = hist(*h2, bins=30, n_ticks=3, label_y=ly)
    s.append(sv)
    return svg(1000, max(b1, b2) + 2, "".join(s))


def p_keep(S):
    s = []
    y = 0
    for key in ("r3", "r12", "churn_late"):
        sv, y = curve(I[key], 0, y, 330, 46, ev_size=8.5, tick_size=8.5, p_size=9, lab_size=11, n_ticks=4)
        s.append(sv)
        y += 12
    marks = [(12, JANTA_R12, "~72%", THEM), (12, APP_R12, "24%", MUTED), (12, NEED_R12, f"last deck needed {NEED_R12 * 100:.0f}%", BAD),
             (6, 0.64, "SBI ₹250 SIP, all frequencies: 64% still on at ~6 months (avg age)", THEM)]
    fx, fy, fw, fh = 420, 24, 470, 340
    sv, X, Y = fan(fx, fy, fw, fh, S["surv"], 0, S["m_surv"], 0, 1, lambda v: f"{v * 100:.0f}%", 5, "months since he signed up",
                   "STILL SAVING, SHARE OF A COHORT", overlays=[(np.array(JANTA), THEM, "a janta book"), (np.array(APP), MUTED, "an app")], marks=marks)
    s.append(sv)
    s.append(tk(X(1.2), Y(0.985), "janta book: an existing book's churn, not a new cohort", 10, 600, THEM, "start", halo=True))
    xb = X(12)
    s.append(f'<line x1="{xb - 9}" y1="{Y(0.40)}" x2="{xb - 9}" y2="{Y(0.30)}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
             + tk(xb - 15, Y(0.35) + 4, "your bear 30–40%", 10.5, 700, INK, "end", halo=True))
    return svg(1000, max(y, 410), "".join(s))


def p_save(S):
    s = []
    y = 0
    for key in ("daily", "days", "amount_growth"):
        sv, y = curve(I[key], 0, y, 330, 46, ev_size=8.5, tick_size=8.5, p_size=9, lab_size=11, n_ticks=4)
        s.append(sv)
        y += 12
    sv, *_ = fan(420, 24, 470, 330, S["dep"], 1, S["m_dep"], 0, 12000, lambda v: inr(v), 4, "months since he signed up",
                 "DEPOSITS A MONTH, PER SAVER STILL SAVING", overlays=[(np.full(36, LAST["daily"] * LAST["days"]), MUTED, "last deck")])
    s.append(sv)
    return svg(1000, max(y, 400), "".join(s))


def p_agent():
    s = []
    sv, y1 = curve(I["signups_run"], 0, 0, 440, 200, ev_size=11, tick_size=10, p_size=11.5, lab_size=13,
                   label_text="Sign-ups a month: likely 100 (60–150), agreed")
    s.append(sv)
    s.append(f'<rect x="0" y="{y1 + 14}" width="440" height="62" rx="12" fill="{FLAT}"/>'
             + V.text(16, y1 + 38, "Agent pay", 12.5, 700, MUTED) + V.text(16, y1 + 64, "₹20,000 + 0.25% of balance, capped at ₹10,000 a month", 14, 800, INK))
    X0, W, G = 500, 235, 30
    kw = dict(ev_size=8.5, tick_size=8.5, p_size=9, lab_size=10.5, n_ticks=4)
    cells = [("signup_decline_y5", "By year 5: 70% of year 1"), ("online_lead_share", "Online leads: half"),
             ("lead_cost", "Lead cost: ₹250"), ("ramp_months", "Full speed: likely 3 months"),
             ("upi_12", "On UPI by month 12: likely 30%"), ("capacity", "Cash visits a day: likely 400")]
    y = 0
    for r in range(3):
        col = lambda key: MUTED if key in ("online_cac", "online_r12") else US
        ly = max(curve(I[k], X0 + c * (W + G), y, W, 40, label=False, col=col(k), **kw)[1] for c, (k, _) in enumerate(cells[2 * r:2 * r + 2]))
        for c, (k, lt) in enumerate(cells[2 * r:2 * r + 2]):
            sv, b = curve(I[k], X0 + c * (W + G), y, W, 40, label_text=lt, label_y=ly, col=col(k), **kw)
            s.append(sv)
        y = b + 14

    sv, yc = curve(I["support_cost"], 0, y1 + 92, 440, 40, ev_size=9, tick_size=9, p_size=9.5, lab_size=11.5, n_ticks=4,
                   label_text="Running cost a saver a month: likely ₹5 (₹0–15)")
    s.append(sv)
    return svg(1000, max(y, yc + 4), "".join(s))


def p_fund():
    """The hook (what his money earns a year), our commission on the agreed debt fund, then the return, rollover and withdrawal curves."""
    s = []
    jr, fr, tr = I["janta_rate"], I["fund_return"], I["trail"]
    gain = BALANCE * (fr.likely - jr.likely)                          # what he gains a year on ₹350 a day, held over a yearly term
    s.append(tk(0, 14, "WHAT HIS MONEY EARNS A YEAR", 12, 800, GOOD, "start"))
    x0, w, hi = 190, 230, 0.08
    X = lambda v: x0 + v / hi * w
    d = fr.frozen()
    bars = [("Janta deposit (bank savings rate)", jr.likely, None, None, MUTED, "~2.5%"),
            ("A liquid fund (OWN-02)", 0.055, 0.05, 0.06, THEM, "5–6%"),
            ("Our debt fund", fr.likely, float(d.ppf(0.1)), float(d.ppf(0.9)), GOOD, "~7%")]
    for k, (lab, v, lo, hi_, c, txt) in enumerate(bars):
        y = 40 + k * 44
        s.append(V.text(x0 - 10, y + 5, lab, 12, 700, INK, "end"))
        s.append(f'<rect x="{x0}" y="{y - 11}" width="{X(v) - x0:.1f}" height="22" rx="4" fill="{c}" opacity="0.85"/>')
        if lo is not None:
            s.append(f'<line x1="{X(lo):.1f}" y1="{y}" x2="{X(hi_):.1f}" y2="{y}" stroke="{INK}" stroke-width="2"/>'
                     f'<line x1="{X(lo):.1f}" y1="{y - 6}" x2="{X(lo):.1f}" y2="{y + 6}" stroke="{INK}" stroke-width="2"/>'
                     f'<line x1="{X(hi_):.1f}" y1="{y - 6}" x2="{X(hi_):.1f}" y2="{y + 6}" stroke="{INK}" stroke-width="2"/>')
        s.append(tk(X(hi_ if hi_ else v) + 8, y + 5, txt, 13, 800, c, "start"))
    s.append(axis(x0, w, 40 + 2 * 44 + 22, 0, hi, X, lambda v: f"{v * 100:.0f}%", 9, 4))
    s.append(f'<rect x="0" y="198" width="480" height="40" rx="12" fill="{V.TINT["good"]}"/>'
             + V.text(240, 223, f"Free to him; about {rsr(gain)} more a year on ₹350 a day", 14.5, 800, GOOD, "middle"))
    # our commission on the agreed debt fund; the liquid fund was not chosen
    sv, b = curve(tr, 540, 50, 440, 70, ev_size=9.5, tick_size=9, p_size=10, lab_size=12, n_ticks=5,
                  label_text=f"Our commission: likely {pc(tr.likely)} ({pc(tr.low)}–{pc(tr.high)})")
    hcard = max(b, 238) + 8
    s.insert(0, f'<rect x="520" y="0" width="480" height="{hcard}" rx="16" fill="{PAPER}"/>')
    s.append(V.text(540, 28, "DEBT FUND: OUR COMMISSION", 12, 800, US))
    s.append(f'<rect x="540" y="36" width="{tw("AGREED", 10, True) + 16}" height="17" rx="8.5" fill="{V.TINT["good"]}"/>' + V.text(548, 48.5, "AGREED", 10, 800, GOOD))
    s.append(V.text(980, 34, f"₹{tr.likely * BALANCE:,.0f}", 26, 800, US, "end") + V.text(980, 50, "a saver a year", 11, 600, MUTED, "end"))
    s.append(sv)
    s.append(tk(540, b + 8, f"Liquid fund, not chosen: {pc(I['trail_liquid'].likely)}, ₹{I['trail_liquid'].likely * BALANCE:,.0f} a saver a year",
                10.5, 600, MUTED, "start"))
    y = hcard + 22
    keys = ("fund_return", "rollover", "withdraw_m")
    lt = {"fund_return": "Return to him: likely 7% (6–7.5%), agreed", "rollover": "Left in at term end: 25%, agreed",
          "withdraw_m": "Taken out each month: likely 1%"}
    kw = dict(ev_size=9, tick_size=9, p_size=9.5, lab_size=11.5, n_ticks=4)
    W3, G3 = 310, 35
    ly = max(curve(I[k], j * (W3 + G3), y, W3, 50, label=False, **kw)[1] for j, k in enumerate(keys))
    for j, k in enumerate(keys):
        sv, b = curve(I[k], j * (W3 + G3), y, W3, 50, label_text=lt[k], label_y=ly, col=GOOD if k == "fund_return" else US, **kw)
        s.append(sv)
    return svg(1000, b + 4, "".join(s))


def p_rest():
    s = []
    sv, y = curve(I["fee"], 0, 0, 1000, 70, ev_size=9.5, tick_size=9, p_size=10.5, lab_size=12.5, n_ticks=10)
    s.append(sv)
    y += 16
    W, G = 180, 25
    kw = dict(ev_size=8.5, tick_size=8, p_size=8.5, lab_size=10.5, n_ticks=4)
    keys = ("loss", "taken_back", "ticket", "tenure", "approved_repeat")
    lt = {"ticket": "Loan size: likely ₹2.5 lakh", "taken_back": "Taken back: likely 2.5%", "loss": "Money lost: likely 3%",
          "approved_repeat": "Approved, repeat: likely 70%", "tenure": "Loan length: likely 36 months"}
    ly = max(curve(I[k], j * (W + G), y, W, 46, label=False, **kw)[1] for j, k in enumerate(keys))
    for j, k in enumerate(keys):
        sv, b = curve(I[k], j * (W + G), y, W, 46, label_text=lt[k], label_y=ly, **kw)
        s.append(sv)
    s.append(tk(4 * (W + G) + 16, b + 6, "Paytm: >50% of loan money", 8.5, 600, THEM, "start")
             + tk(4 * (W + G) + 16, b + 17, "goes to repeat borrowers (NG-028)", 8.5, 600, THEM, "start"))
    y = b + 40
    s.append(tk(0, y, "GROWS WITH HISTORY: LIKELY VALUES, YEARS 1–5", 11, 800, GOOD, "start"))
    ap, tkt = I["approved_first"].likely, I["ticket"].likely
    ga, gt = I["approval_growth"].likely, I["ticket_growth"].likely
    series = [("First-loan approval, +10% a year (cap 80%)", [min(ap * (1 + ga) ** (k - 1), 0.80) for k in range(1, 6)], 0.80, 0.9, pcr,
               lambda v: f"{v * 100:.0f}%"),
              ("Next loan size, +10% per year repaid (cap ₹5 lakh)", [min(tkt * (1 + gt) ** (k - 1), 5e5) for k in range(1, 6)], 5e5, 5.6e5,
               lambda v: lakh(round(v / 1e4) * 1e4), lambda v: f"₹{trim(v / 1e5, 1)}L" if v else "₹0"),
              ("Loan fee: a DSA's rate, to 1.5× by month 60", [fee_at(1 + 12 * (k - 1) if k < 5 else 60) for k in range(1, 6)],
               I["fee"].likely * I["fee_mult_end"].likely, 0.03, lambda v: f"{v * 100:.2f}%", pcr)]
    for j, (title, vals, cap, top, vf, yf) in enumerate(series):
        x0, w, h, y0 = j * 335 + 30, 262, 96, y + 26
        X = lambda k: x0 + (k - 1) / 4 * w
        Yv = lambda v: y0 + h - v / top * h
        s.append(tk(x0 - 30, y0 - 6, title, 10.5, 700, INK, "start"))
        for t in nice_ticks(0, top, 3):
            s.append(f'<line x1="{x0}" y1="{Yv(t):.1f}" x2="{x0 + w}" y2="{Yv(t):.1f}" stroke="{RULE}" stroke-width="1"/>')
        s.append(f'<line x1="{x0}" y1="{Yv(cap):.1f}" x2="{x0 + w}" y2="{Yv(cap):.1f}" stroke="{BAD}" stroke-width="1.5" stroke-dasharray="5 4"/>'
                 + (tk(x0 + w, Yv(cap) - 5, "cap", 10, 700, BAD, "end") if j < 2 else tk(x0 + 2, Yv(cap) - 5, "1.5× the start", 10, 700, BAD, "start")))
        s.append(f'<polyline points="{" ".join(f"{X(k):.1f},{Yv(v):.1f}" for k, v in enumerate(vals, 1))}" fill="none" stroke="{GOOD}" stroke-width="2.5"/>')
        for k, v in enumerate(vals, 1):
            s.append(f'<circle cx="{X(k):.1f}" cy="{Yv(v):.1f}" r="4" fill="{GOOD}"/>' + tk(X(k), Yv(v) - 9, vf(v), 9.5, 700, GOOD, halo=True)
                     + tk(X(k), y0 + h + 14, f"year {k}" if j < 2 or k < 5 else "month 60", 9, 400, MUTED))
    return svg(1000, y + 26 + 96 + 22, "".join(s))


def fee_at(t):
    """The origination fee in company month t at the likely starting fee (straight line to fee_mult_end at month 60)."""
    return I["fee"].likely * (I["fee_mult_start"].likely + (I["fee_mult_end"].likely - I["fee_mult_start"].likely) * (t - 1) / 59)


def p_collect(S, D):
    """Running loan -> falls 31-90 days behind -> brought back by our agent (fee), or -> 90+ -> recovered (fee)."""
    s = []
    early, late, p90, behind = S["coll"]
    q = lambda x: float(np.percentile(x, 50))
    rngt = lambda x: f"p10 {rsr(np.percentile(x, 10))} · p90 {rsr(np.percentile(x, 90))}"
    W, H, Y0 = 230, 62, 26
    bx = [(0, "Running loan", PAPER), (385, "31–90 days behind", V.TINT["warn"]), (770, "90+ days bad", V.TINT["bad"])]
    for x, t, fill in bx:
        s.append(f'<rect x="{x}" y="{Y0}" width="{W}" height="{H}" rx="12" fill="{fill}"/>' + V.text(x + W / 2, Y0 + 37, t, 15, 800, INK, "middle"))
    for k, lab in enumerate((f"{pcr(q(behind))} of loans fall behind", f"{pcr(q(p90))} go on to 90+")):
        xa, xb = bx[k][0] + W, bx[k + 1][0]
        s.append(V.arrow(xa + 4, Y0 + H / 2, xb - 4, Y0 + H / 2, MUTED, 2.5) + tk((xa + xb) / 2, Y0 + H / 2 - 9, lab, 11, 800, INK))
    downs = [(bx[1][0], [f"{pc(I['early_cured'].likely)} of loans", "brought back by our agent", f"₹{I['fee_early'].likely:,.0f} an account"], early, "start"),
             (bx[2][0], [f"{pc(I['recovered'].likely)} of what is owed", "recovered", f"₹{I['fee_b3'].likely:,.0f} an account"], late, "end")]
    yb = Y0 + H + 80
    for x, lines, money, anc in downs:
        s.append(V.arrow(x + W / 2, Y0 + H + 4, x + W / 2, yb - 6, GOOD, 2.5))
        lx = x + W / 2 + (8 if anc == "start" else -8)                    # the right-hand labels sit left of their arrow
        for j, ln in enumerate(lines):
            s.append(tk(lx, Y0 + H + 24 + j * 15, ln, 11, 700, GOOD, anc, halo=True))
        s.append(f'<rect x="{x}" y="{yb}" width="{W}" height="86" rx="12" fill="{V.TINT["good"]}"/>')
        s.append(V.text(x + W / 2, yb + 22, "fee per loan made", 11, 600, MUTED, "middle"))
        s.append(V.text(x + W / 2, yb + 54, rsr(q(money)), 26, 800, GOOD, "middle") + tk(x + W / 2, yb + 74, rngt(money), 10.5, 600, INK))
    tot = D["collections_per_loan"]
    s.append(f'<rect x="0" y="{yb}" width="{W}" height="86" rx="12" fill="{PAPER}"/>')
    s.append(V.text(W / 2, yb + 22, "all collection fees", 11, 600, MUTED, "middle"))
    s.append(V.text(W / 2, yb + 54, rsr(tot["p50"]), 26, 800, US, "middle") + tk(W / 2, yb + 74, f"p10 {rsr(tot['p10'])} · p90 {rsr(tot['p90'])}", 10.5, 600, INK))
    s.append(tk(W / 2, Y0 + H + 34, f"origination: {rsr(D['fee_per_loan']['p50'])}", 11, 600, MUTED) + tk(W / 2, Y0 + H + 50, "per loan, for scale", 10, 500, MUTED))
    # the check: implied 90+ share against two published peaks
    yc = yb + 118
    x0, w, lo, hi = 230, 560, 0.0, 0.14
    X = lambda v: x0 + (v - lo) / (hi - lo) * w
    s.append(tk(0, yc + 4, "CHECK: 90+ SHARE", 11, 800, MUTED, "start"))
    a, m, b = (float(np.percentile(p90, v)) for v in (10, 50, 90))
    s.append(f'<line x1="{X(a):.1f}" y1="{yc}" x2="{X(b):.1f}" y2="{yc}" stroke="{US}" stroke-width="9" stroke-linecap="round" opacity="0.45"/>'
             f'<circle cx="{X(m):.1f}" cy="{yc}" r="5.5" fill="{US}"/>' + tk(X(m), yc - 12, f"ours {pcr(m)}", 11, 800, US))
    s.append(axis(x0, w, yc + 14, lo, hi, X, lambda v: f"{v * 100:.0f}%", 9, 7))
    for v, lab in ((0.036, "MAC-03: personal loans > ₹50k, 3.6%"), (0.102, "NG-015: self-employed unsecured, 10.2%")):
        s.append(f'<path d="M{X(v):.1f},{yc + 13} l-4,-7 h8 z" fill="{THEM}"/>' + tk(X(v), yc + 42, lab, 10, 700, THEM))
    share = D["draws_behind_above_50pct"]["mean"]
    s.append(tk(X(hi) + 12, yc + 4, f"✓ behind ≤ 50% in {100 - share * 100:.0f}% of draws", 11, 800, GOOD, "start"))
    s.append(tk(0, yc + 66, "31–90 day fees come ~9 months after a loan; 90+ fees ~18 months. Loss is the anchor: half the loan owed when bad.",
                10.5, 600, MUTED, "start"))
    return svg(1000, yc + 72, "".join(s))


def p_xsell(S, D):
    """Money per active saver a year by product (holdings settled), p10-p90 bars sorted, with the total against the old ₹63."""
    s = []
    xs = S["xs"]
    rows = sorted(((pre, tile, grp) for pre, grp, tile, *_ in PRODUCTS), key=lambda r: -np.percentile(xs[r[0]], 50))
    x0, w, lh = 190, 560, 21
    hi = max(np.percentile(xs[p], 90) for p, *_ in rows) * 1.08
    X = lambda v: x0 + min(v, hi) / hi * w
    GC = {"insurance": US, "investments": THEM, "payments": "#6b7a8a", "other_loans": GOOD}
    for k, (pre, tile_, grp) in enumerate(rows):
        y = 18 + k * lh
        p10, p50, p90 = np.percentile(xs[pre], [10, 50, 90])
        s.append(V.text(x0 - 10, y + 4, tile_, 11.5, 600, INK, "end"))
        s.append(f'<line x1="{X(p10):.1f}" y1="{y}" x2="{X(p90):.1f}" y2="{y}" stroke="{GC[grp]}" stroke-width="7" stroke-linecap="round" opacity="0.45"/>')
        s.append(f'<circle cx="{X(p50):.1f}" cy="{y}" r="4.5" fill="{GC[grp]}"/>')
        s.append(tk(X(p90) + 8, y + 4, f"₹{p50:,.0f}", 10.5, 700, INK, "start"))
    yax = 18 + len(rows) * lh - 6
    s.append(axis(x0, w, yax, 0, hi, X, lambda v: inr(v), 9, 5))
    s.append(tk(x0 + w / 2, yax + 30, "₹ per active saver a year, once holdings settle (dot p50, bar p10–p90)", 10.5, 600, MUTED))
    k = 0
    for grp, lab in (("insurance", "insurance"), ("investments", "investments"), ("payments", "payments"), ("other_loans", "other loans")):
        s.append(f'<circle cx="{x0 + k * 120 + 5}" cy="{yax + 48}" r="4.5" fill="{GC[grp]}"/>' + tk(x0 + k * 120 + 14, yax + 52, lab, 10.5, 600, INK, "start"))
        k += 1
    # the total against the old ₹63
    tot, first = D["xsell_total"], D["xsell_total_first_year"]
    xr = 800
    s.append(f'<rect x="{xr}" y="0" width="200" height="200" rx="16" fill="{PAPER}"/>')
    s.append(V.text(xr + 100, 30, "ALL PRODUCTS", 11.5, 800, MUTED, "middle"))
    s.append(V.text(xr + 100, 78, rsr(tot["p50"]), 38, 800, US, "middle"))
    s.append(tk(xr + 100, 100, f"p10 {rsr(tot['p10'])} · p90 {rsr(tot['p90'])}", 11, 600, INK))
    s.append(tk(xr + 100, 132, f"first-year sales only: {rsr(first['p50'])}", 11, 600, INK))
    s.append(tk(xr + 100, 156, f"old single line: ₹{OLD_OTHER:.0f}", 12, 800, BAD))
    s.append(tk(xr + 100, 178, "(XO-39, first-year method)", 10, 500, MUTED))
    card = D["card_once_per_active"]
    s.append(f'<rect x="{xr}" y="214" width="200" height="86" rx="16" fill="{FLAT}"/>')
    s.append(V.text(xr + 100, 240, "PLUS A CARD, ONCE", 11, 800, MUTED, "middle"))
    s.append(V.text(xr + 100, 276, rsr(card["p50"]), 26, 800, INK, "middle"))
    s.append(tk(xr + 100, 293, f"p10 {rsr(card['p10'])} · p90 {rsr(card['p90'])}", 10, 600, INK))
    return svg(1000, max(yax + 60, 300), "".join(s))


def p_decisions(D):
    s = []
    tiles = [i for i in OP_DECISIONS if i.key != "cash_route"]
    for k, i in enumerate(tiles):
        r, c = divmod(k, 5)
        x, y = c * 202, r * 96
        s.append(f'<rect x="{x}" y="{y}" width="188" height="86" rx="14" fill="{FLAT}"/>')
        s.append(V.text(x + 16, y + 22, i.short, 12.5, 700, MUTED))
        s.append(V.text(x + 16, y + 52, i.shown, 19 if len(i.shown) < 11 else 16, 800, INK))
        s.append(V.text(x + 16, y + 72, i.sub, 11, 500, MUTED))
    y = 96 * ((len(tiles) + 4) // 5) + 4
    b, a = D["marketplace_yearly_per_100"], D["marketplace_yearly_per_100_independent"]
    s.append(f'<rect x="0" y="{y}" width="1000" height="40" rx="12" fill="{V.TINT["good"]}"/>'
             + f'<circle cx="22" cy="{y + 20}" r="12" fill="{GOOD}"/>' + V.text(22, y + 25, "✓", 13, 800, "#fff", "middle")
             + V.text(44, y + 25, "Bad years linked", 13.5, 800, INK)
             + tk(985, y + 25, f"marketplace a year per 100 savers, p10–p90: linked {rsr(b['p10'])}–{rsr(b['p90'])}; apart {rsr(a['p10'])}–{rsr(a['p90'])}",
                  10.5, 600, MUTED, "end"))
    y += 58
    s.append(tk(0, y + 8, "THE CASH ROUTE (YOUR DESIGN)", 11.5, 800, US, "start"))
    steps = ["Cash to our agent", "Fund's collection account", "Reconciliation sent", "SMS next day"]
    W, G, y0 = 226, 32, y + 18
    for k, t in enumerate(steps):
        x = k * (W + G)
        s.append(f'<rect x="{x}" y="{y0}" width="{W}" height="54" rx="12" fill="{PAPER}"/>' + V.text(x + W / 2, y0 + 32, t, 13, 700, INK, "middle"))
        if k < 3:
            s.append(V.arrow(x + W + 3, y0 + 27, x + W + G - 3, y0 + 27, MUTED, 2.2))
    yf = y0 + 70
    s.append(f'<rect x="0" y="{yf}" width="1000" height="40" rx="12" fill="{V.TINT["bad"]}"/>'
             + V.text(16, yf + 26, "Needs a legal opinion before the pilot", 14, 800, BAD)
             + tk(985, yf + 25, "distributors may not pool investor money; payments from his own account (REG-066, REG-081); fund cash cap ~₹50,000 a year (to verify)",
                  10, 600, BAD, "end"))
    return svg(1000, yf + 44, "".join(s))


def slide(no, kicker, title, visual, caption="", src="", cls=""):
    return (f'<section class="slide {cls}"><div class="kick"><span class="pg">{no} / {TOTAL}</span>{kicker}</div>'
            f'<h1>{title}</h1><div class="vis">{visual}</div>'
            + (f'<div class="cap">{caption}</div>' if caption else "") + (f'<div class="src">Sources: {src}</div>' if src else "") + '</section>')


GRID_PAGES = (2, 3, 4, 5, 6, 7, 8)


def build(S, D):
    css = V.CSS.replace("INK", INK).replace("MUTED", MUTED).replace("RULE", RULE).replace("US", US)
    css += ".grid h1 { margin-bottom: 6px; } .grid .vis { align-items: flex-start; }"
    ln, rep = D["loans_per_100"], D["loans_per_100_repeat_rule"]
    agree, _ = p_agree()
    n_in = len(INPUTS)
    g = lambda k: f"Every assumption, as a distribution ({k} of 7)"
    pages = [
        slide(1, "Agreed 16–17 Oct", f"{n_in - len(PENDING)} inputs, {len(DECISIONS)} fixed", agree),
        slide(2, g(1), "The saver, the agent, the fund", p_grid1(), "", "tables/dist_agreed_v1.csv", "grid"),
        slide(3, g(2), "Every take rate: loans, cards, collections, timing", p_grid2(), "", "tables/dist_agreed_v1.csv", "grid"),
        slide(4, g(3), "Insurance: every product's take-up, premium and commission", p_grid3(), "", "XO-09 to XO-35, REG-054, GAP-04, GAP-05", "grid"),
        slide(5, g(4), "Investments: take-up, ticket and commission", p_grid4(), "", "XO-01 to XO-37, LEV-036, BM-03", "grid"),
        slide(6, g(5), "Payments and other lenders' loans, with housing", p_grid5(), "",
              "XO-25, XO-26, XO-33, XL-28, XL-54, GAP-06, XL-15, XL-16, XL-24 to XL-26, XL-29, IV-04", "grid"),
        slide(0, g(6), "Cities (real-world limits)", p_cities(), "", "tables/base_inputs.csv; NG-002", "grid"),
        slide(0, g(7), "Our own NBFC from month 30", p_nbfc(), "", "tables/base_inputs.csv; LEV-012, LEV-014, LEV-015, LEV-023, LEV-031", "grid"),
        slide(7, "How many loans", f"About {trim(ln['p50'], 1)} first loans a year per 100 active savers; 8 in 10 draws: {trim(ln['p10'], 1)} to {trim(ln['p90'], 1)}",
              p_loans(S), f"The middle sits near the older evidence's 2.5. If a saver with a loan running cannot apply, it falls to {trim(rep['p50'], 1)}.",
              SRC["loans"]),
        slide(8, "The saver: who keeps saving", "Still saving after a year: agreed at 55%; the last deck needed 37%",
              p_keep(S), "", SRC["keep"]),
        slide(9, "The saver: how much he saves", "About ₹7,000 a month at the start, rising a little each year",
              p_save(S), "The band is 8 in 10 draws.", SRC["save"]),
        slide(10, "The agent", "Sign-ups: 100 a month, falling to 70 by year 5",
              p_agent(), "A janta agent collects; he does not sell.", SRC["agent"]),
        slide(11, "The fund", "The hook: his money earns ~7% in a debt fund",
              p_fund(), "Agreed: a quarter of the balance stays in at term end.", SRC["fund"]),
        slide(12, "Loans, the rest", "The fee starts at a DSA's rate and rises to 1.5× by year 5",
              p_rest(), "Worst case = Paytm's losses: our savers chose to save first, and the agent who knows them helps collect.", SRC["rest"]),
        slide(13, "Collections on overdue loans", "Collections pay per account, mostly from year 2",
              p_collect(S, D), "Few loans reach these buckets in the pilot year: a loan takes months to fall behind.", SRC["coll"]),
        slide(14, "Everything we can cross-sell", f"{len(PRODUCTS)} products: about {rsr(D['xsell_total']['p50'])} an active saver a year, against the old ₹63",
              p_xsell(S, D), "Insurance commissions sit at the draft distributor caps, as agreed.", SRC["xsell"]),
        slide(15, "Decisions", "Decisions, cash route",
              p_decisions(D)),
    ]
    pages = [re.sub(r'<span class="pg">\d+ / \d+</span>', f'<span class="pg">{k} / {len(pages)}</span>', pg, count=1) for k, pg in enumerate(pages, 1)]
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Agreed assumptions</title><style>{css}</style></head><body>{"".join(pages)}</body></html>'


def word_counts(doc):
    out = []
    for k, sec in enumerate(re.findall(r"<section.*?</section>", doc, flags=re.S), 1):
        body = re.sub(r'<span class="pg">.*?</span>', " ", sec)
        no_tk = re.sub(r'<text class="tk".*?</text>', " ", body, flags=re.S)
        words = lambda h: [w for w in html.unescape(re.sub(r"<[^>]+>", " ", h)).split() if re.search(r"\w", w)]
        out.append((k, len(words(no_tk)), len(words(body))))
    return out


def main():
    d = draw()
    rows = proposal_rows(d)
    write("dist_proposal_v1.csv", rows)
    corr = {**dict.fromkeys(rows[0], ""), "group": "loans", "key": "corr_approved_loss", "kind": "decision", "shape": "fixed",
            **dict.fromkeys(("low", "likely", "high", "p10", "p50", "p90", "mean"), RHO),
            "name": "Correlation in a draw between loss and each of approved_first and approved_repeat (Gaussian copula)",
            "unit": "correlation of normal scores", "confidence": YOURS, "evidence_points": "operator, 16 Oct: link approvals and losses in bad years",
            "source_ids": "operator", "why_this_shape": "Agreed: in a bad year approvals fall as losses rise; the two approvals then share +0.25."}
    write("dist_agreed_v1.csv", [{**r, "agreed_on": "pending" if r["key"] in PENDING else "2026-10-17" if r["key"] in AGREED_17 + tuple(BASE_KEYS) else AGREED_ON}
                                 for r in rows + [corr]])
    D_rows, S = derived(d)
    write("dist_derived_v1.csv", D_rows)
    D = {r["key"]: r for r in D_rows}
    out_dir = Path(os.environ.get("DIST_OUT", tempfile.gettempdir()))
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = build(S, D)
    src = out_dir / "assumptions_to_agree.html"
    src.write_text(doc)
    subprocess.run([V.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", src.as_uri()],
                   check=True, capture_output=True)
    shutil.copyfile(PDF, PDF_AGREED)
    lk = np.corrcoef(stats.rankdata(d["loss"]), stats.rankdata(d["approved_first"]))[0, 1]
    print(f"rank correlation, loss vs approved_first in the draws: {lk:.2f}")
    from collections import Counter
    print(f"evidence ids checked in research/: {len(CHECKED)}: {', '.join(sorted(CHECKED))}")
    print(f"rows by kind: {dict(Counter(r['kind'] for r in rows))}")
    print(f"keys ({len(rows)}): {', '.join(r['key'] for r in rows)}")
    print(f"draws with r12 > r3 (r12 capped at r3 in the curve): {S['capped']:.2%}")
    for r in D_rows:
        print(f"DERIVED {r['key']:<42} p10 {r['p10']:>12,.4f} p50 {r['p50']:>12,.4f} p90 {r['p90']:>12,.4f} mean {r['mean']:>12,.4f} "
              f"at likely {r['at_likely_values']!s:>12} last {r['last_deck']!s:>10}")
    fail = False
    for k, n_words, n_all in word_counts(doc):
        cap = "exempt (grid)" if k in GRID_PAGES else ("OK" if n_words <= 90 else "OVER 90")
        fail |= cap == "OVER 90"
        print(f"page {k}: {n_words} words excluding tick, axis and evidence labels ({n_all} with them) {cap}")
    print(f"wrote {T / 'dist_proposal_v1.csv'}\nwrote {T / 'dist_agreed_v1.csv'}\nwrote {T / 'dist_derived_v1.csv'}\nwrote {src}\nwrote {PDF}\nwrote {PDF_AGREED}")
    if fail:
        raise SystemExit("a page is over 90 words")


if __name__ == "__main__":
    main()

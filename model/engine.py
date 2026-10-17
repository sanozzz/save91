"""Reference engine for the savings-first model.

Reads the frozen input tables in ../tables/, follows one monthly cohort for 60
months, and writes the Outputs tables the deck quotes. build_xlsx.py writes the
same logic as spreadsheet formulas; verify.py checks the two agree.

Conventions (hold fixed, VCs check them):
- LTV is on contribution margin, discounted monthly at `disc_rate` per year.
- CAC is fully loaded, per activated saver (first successful auto-debit).
- Loan, card and insurance economics are booked in the month the loan,
  card or policy is issued (expected value at origination).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "tables"
MONTHS = 60
SCENARIOS = ("bear", "base", "bull")


# ---------------------------------------------------------------- inputs
def _read(name):
    with open(TABLES / name, newline="") as f:
        return list(csv.DictReader(f))


SEGMENTS = ("gig", "ng")


def load_inputs(scenario: str, overrides: dict | None = None, segment: str = "gig") -> dict:
    """Inputs for one customer segment. Non-gig uses its ng_* value where one is set,
    else the gig value. An override 'key' applies to both segments; 'key@gig' or
    'key@ng' to one."""
    rows = _read("inputs.csv")
    p = {}
    for r in rows:
        ng = r.get("ng_" + scenario, "")
        p[r["id"]] = float(ng if (segment == "ng" and ng != "") else r[scenario])
    for k, v in (overrides or {}).items():
        key, _, seg = k.partition("@")
        if not seg or seg == segment:
            p[key] = v
    return p


def scenario_values(scenario: str, keys) -> dict:
    """Segment-specific overrides that set `keys` to their `scenario` values in both segments."""
    out = {}
    for seg in SEGMENTS:
        vals = load_inputs(scenario, segment=seg)
        for k in keys:
            out[f"{k}@{seg}"] = vals[k]
    return out


def load_variant(name: str | None, scenario: str) -> dict:
    """Overrides for a product-design variant (tables/variants.csv); {} for the inputs as they stand."""
    if not name:
        return {}
    rows = [r for r in _read("variants.csv") if r["variant"] == name]
    assert rows, f"unknown variant {name}"
    return {r["input"]: float(r[scenario]) for r in rows}


def load_channels() -> list[dict]:
    out = []
    for r in _read("channels.csv"):
        d = {k: (float(v) if k not in ("channel", "segment", "label", "basis", "notes") else v) for k, v in r.items()}
        out.append(d)
    return out


def load_lf(scenario: str, overrides: dict | None = None) -> dict:
    p = {r["id"]: float(r[scenario]) for r in _read("inputs_lending_first.csv")}
    if overrides:
        p.update(overrides)
    return p


# ---------------------------------------------------------------- CAC
def channel_cac(ch: dict, mult: float) -> dict:
    """Fully loaded CAC per activated saver for one channel."""
    k2a = ch["p_kyc_mandate"] * ch["p_mandate_debit"]           # KYC'd -> activated
    i2a = ch["p_install_kyc"] * k2a                             # install -> activated
    acq = ch["cost_per_install"] * mult / i2a
    kyc = ch["kyc_cost"] / k2a
    mandate = ch["mandate_cost"] / ch["p_mandate_debit"]
    other = ch["reward"] + ch["referral_cost"] + ch["partner_fee"]
    return {
        "channel": ch["channel"],
        "label": ch["label"],
        "mix": ch["mix"],
        "install_to_active": i2a,
        "acquisition": acq,
        "kyc": kyc,
        "mandate": mandate,
        "rewards_referral_partner": other,
        "cac": acq + kyc + mandate + other,
    }


def blended_cac(p: dict, channels: list[dict], segment: str = "gig") -> tuple[float, list[dict]]:
    seg = "gig" if segment == "gig" else "nongig"
    rows = [channel_cac(c, p["cac_mult"]) for c in channels if c.get("segment", "gig") == seg]
    total_mix = sum(r["mix"] for r in rows)
    return sum(r["cac"] * r["mix"] for r in rows) / total_mix, rows


# ---------------------------------------------------------------- retention
def survival(p: dict, t: int) -> float:
    """Share of activated savers still saving in month t (t >= 1)."""
    anchors = [(0, 1.0), (1, p["ret_m1"]), (3, p["ret_m3"]), (6, p["ret_m6"]),
               (12, p["ret_m12"]), (24, p["ret_m24"])]
    if t > 24:
        return p["ret_m24"] * (1 - p["churn_late"]) ** (t - 24)
    for (a, sa), (b, sb) in zip(anchors, anchors[1:]):
        if t <= b:
            return sa * (sb / sa) ** ((t - a) / (b - a))
    raise AssertionError(t)


# ---------------------------------------------------------------- loan maths (closed forms, mirrored in the workbook)
def _per_rupee_interest(annual_rate: float, n: int) -> float:
    """Total interest on Rs 1 lent for n months with equal monthly instalments."""
    i = annual_rate / 12
    return i / (1 - (1 + i) ** -n) * n - 1


def _avg_balance_share(annual_rate: float, n: int) -> float:
    """Mean opening balance over the loan's life as a share of the amount lent."""
    g = (1 + annual_rate / 12) ** n
    return (g - (g - 1) / (n * annual_rate / 12)) / (g - 1)


# ---------------------------------------------------------------- cohort
def cohort(p: dict) -> list[dict]:
    """One monthly cohort of `cohort_size` activated savers, months 1..60."""
    N = p["cohort_size"]
    ym = p["fund_yield"] / 12
    rows: list[dict] = []
    T = int(p["loan_tenor"])
    nbfc_interest = _per_rupee_interest(p["nbfc_apr"], T)
    nbfc_cof = _per_rupee_interest(p["nbfc_cof"], T)
    nbfc_avg_frac = _avg_balance_share(p["nbfc_apr"], T)
    prev = {"S": 1.0, "Pa": 0.0, "D": 0.0, "B": 0.0, "K": 0.0, "U": 0.0,
            "Q": 0.0, "Ssip": 0.0, "I": 0.0, "roll": 0.0, "roll_all": 0.0}
    for t in range(1, MONTHS + 1):
        r: dict = {"month": t}
        S = survival(p, t)
        A = N * S
        r["survival"] = S
        r["active"] = A

        # --- saving and balances
        per_saver = p["daily_amount"] * (1 + p["amount_growth"]) ** ((t - 1) // 12) * p["debits_success"]
        C = A * per_saver
        keep = S / prev["S"]
        grown = prev["Pa"] * (1 + ym)
        stay = grown * keep
        leave = grown * (1 - keep)
        Pa = stay * (1 - p["withdraw_rate"]) + C
        D = prev["D"] * (1 + ym) * (1 - p["dormant_withdraw"]) + leave * (1 - p["leaver_withdraw"])
        W = stay * p["withdraw_rate"] + leave * p["leaver_withdraw"] + prev["D"] * (1 + ym) * p["dormant_withdraw"]
        aum = Pa + D
        gold = aum * p["gold_on"] * p["gold_share"]
        fd = (aum - gold) * p["fd_share"] if t >= p["fd_start"] else 0.0
        liquid = aum - gold - fd
        r.update(contributions=C, withdrawals=W, bal_active=Pa, bal_dormant=D,
                 aum=aum, aum_gold=gold, aum_fd=fd, aum_liquid=liquid)

        # --- savings revenue
        r["rev_liquid"] = liquid * p["trail_liquid"] / 12
        r["rev_fd"] = fd * p["fd_fee"] / 12
        r["rev_gold"] = C * p["gold_on"] * p["gold_share"] * p["gold_margin"]
        r["rev_mf_incentive"] = 0.0  # attached to SIP starts below

        # --- loans via partners (we are the loan service provider)
        on = t >= p["loan_start"]
        uptake = p["loan_apply"] * p["loan_approval"]
        B = prev["B"] + (p["loan_eligible"] - prev["B"]) * uptake if on else 0.0
        new_b = A * (p["loan_eligible"] - prev["B"]) * uptake if on else 0.0
        # the ladder (founder, 2 Oct 2026): loans 1-2 secured against the saver's fund + FD money,
        # 3-4 part secured, 5+ unsecured. A loan leads to the next rung when it is repaid and the
        # saver, still active, borrows again.
        T = int(p["loan_tenor"])
        step = p["loan_repeat"] * (1 - p["ladder_dpd90"])
        if t > T:
            back = rows[t - T - 1]
            surv = S / back["survival"]
            r2, r3, r4 = (step * back[k] * surv for k in ("loans_r1", "loans_r2", "loans_r3"))
            r5new = step * back["loans_r4"] * surv
            r5 = r5new + step * back["loans_r5"] * surv
        else:
            r2 = r3 = r4 = r5new = r5 = 0.0
        r1 = new_b
        lendable = (Pa / A if A else 0.0) * (1 - p["gold_on"] * p["gold_share"])   # gold cannot back a loan
        sec = p["secured_ltv"] * lendable                                           # secured loan size
        disb_sec = (r1 + r2 + r3 + r4) * sec
        disb_uns = (r3 + r4) * sec * p["part_unsec_multiple"] + r5 * p["loan_ticket"]
        disb = disb_sec + disb_uns
        loans = r1 + r2 + r3 + r4 + r5
        repeat = loans - r1
        # money lent in the last T months: unsecured money sets the guarantee deposit; all money, an NBFC's book
        rolling = prev["roll"] + disb_uns - (rows[t - T - 1]["disb_unsec"] if t > T else 0.0)
        roll_all = prev["roll_all"] + disb - (rows[t - T - 1]["disbursal"] if t > T else 0.0)
        lost = p["ladder_dpd90"] * p["loan_ead"] * p["loan_lgd"]       # share of unsecured money never recovered
        if p["nbfc_on"]:
            ni = (nbfc_interest * (1 - p["ladder_dpd90"]) + p["nbfc_proc_fee"] - nbfc_cof)
            r["rev_loans"] = disb * ni
            r["cost_loans"] = disb_uns * lost + loans * (p["loan_ops_cost"] + p["service_cost"])
            capital = p["nbfc_equity"] * nbfc_avg_frac * roll_all
        else:
            r["rev_loans"] = disb_sec * p["secured_fee"] + disb_uns * (p["lsp_fee"] + p["dlg_on"] * p["dlg_fee_uplift"])
            # the guarantee, and our servicing and collection, cover only loans with unsecured money
            r["cost_loans"] = loans * p["loan_ops_cost"] + p["dlg_on"] * (min(lost, p["dlg_cap"]) * disb_uns + (r3 + r4 + r5) * p["service_cost"])
            capital = p["dlg_on"] * p["dlg_cap"] * rolling
        r.update(borrowed_share=B, loans_new=new_b, loans_repeat=repeat, loans=loans, disbursal=disb,
                 loans_r1=r1, loans_r2=r2, loans_r3=r3, loans_r4=r4, loans_r5=r5, loans_r5new=r5new,
                 lendable=lendable, sec_loan=sec, disb_sec=disb_sec, disb_unsec=disb_uns,
                 disb_rolling=rolling, roll_all=roll_all, capital_locked=capital)

        # --- FD-secured card, then unsecured
        con = t >= p["card_start"]
        c_elig = p["card_eligible"] * (1 - p["gold_on"] * p["gold_share"])   # only FD money can back the card
        K = prev["K"] * (1 - p["card_churn"]) + (c_elig - prev["K"]) * p["card_uptake"] if con else 0.0
        new_c = A * (c_elig - prev["K"]) * p["card_uptake"] if con else 0.0
        holders = A * K
        uon = t >= p["unsec_start"]
        U = prev["U"] + max(0.0, prev["K"] - prev["U"]) * p["unsec_grad"] if uon else prev["U"]
        new_u = A * (U - prev["U"])
        r.update(card_share=K, cards_new=new_c, card_holders=holders, unsec_share=U, unsec_new=new_u)
        r["rev_cards"] = new_c * p["card_fee"] + holders * p["card_spend"] * p["card_ic_share"] + new_u * p["unsec_fee"]
        r["cost_cards"] = (new_c + new_u) * p["card_ops_cost"]

        # --- equity SIP beyond the micro-savings
        son = t >= p["sip_start"]
        Q = prev["Q"] * (1 - p["sip_stop"]) + (p["sip_eligible"] - prev["Q"]) * p["sip_uptake"] if son else 0.0
        new_s = A * (p["sip_eligible"] - prev["Q"]) * p["sip_uptake"] if son else 0.0
        Ssip = prev["Ssip"] * (1 + p["sip_return"] / 12) * (1 - p["sip_redeem"]) + A * Q * p["sip_amount"]
        r.update(sip_share=Q, sips_new=new_s, sip_aum=Ssip)
        r["rev_mf_incentive"] = new_s * p["first_time_share"] * p["mf_incentive"]
        r["rev_sip"] = Ssip * p["trail_equity"] / 12

        # --- insurance (annual policies, renewals at 12-month anniversaries)
        ion = t >= p["ins_start"]
        I = prev["I"] + (p["ins_eligible"] - prev["I"]) * p["ins_uptake"] if ion else 0.0
        new_p = A * (p["ins_eligible"] - prev["I"]) * p["ins_uptake"] if ion else 0.0
        if t > 12:
            back = rows[t - 13]
            renew = (back["policies_new"] + back["policies_renewed"]) * p["ins_persist"]
        else:
            renew = 0.0
        r.update(insured_share=I, policies_new=new_p, policies_renewed=renew)
        r["rev_insurance"] = (new_p * p["ins_comm_first"] + renew * p["ins_comm_renew"]) * p["ins_premium"]
        r["cost_insurance"] = new_p * p["ins_ops_cost"]

        # --- cost to serve
        failed = max(0.0, p["debits_scheduled"] - p["debits_success"])
        r["cost_payments"] = A * (p["debits_success"] * p["cost_debit"]
                                  + p["debits_scheduled"] * p["cost_notice"]
                                  + failed * p["cost_failed"])
        r["cost_service"] = A * (p["cost_support"] + p["cost_tech"] + p["cost_rewards"])
        r["cost_fraud"] = C * p["cost_fraud"]

        rev_cols = ("rev_liquid", "rev_fd", "rev_gold", "rev_mf_incentive", "rev_loans", "rev_cards", "rev_sip", "rev_insurance")
        cost_cols = ("cost_loans", "cost_cards", "cost_insurance", "cost_payments", "cost_service", "cost_fraud")
        r["revenue"] = sum(r[c] for c in rev_cols)
        r["cost"] = sum(r[c] for c in cost_cols)
        r["contribution"] = r["revenue"] - r["cost"]

        rows.append(r)
        prev = {"S": S, "Pa": Pa, "D": D, "B": B, "K": K, "U": U, "Q": Q, "Ssip": Ssip, "I": I, "roll": rolling, "roll_all": roll_all}
    return rows


REV_LINES = {
    "Savings: liquid fund": ("rev_liquid",),
    "Savings: FDs": ("rev_fd",),
    "Savings: gold": ("rev_gold",),
    "Loans (partner)": ("rev_loans",),
    "Cards": ("rev_cards",),
    "SIPs": ("rev_sip", "rev_mf_incentive"),
    "Insurance": ("rev_insurance",),
}


def summarize(p: dict, rows: list[dict], cac: float) -> dict:
    N = p["cohort_size"]
    dm = (1 + p["disc_rate"]) ** (1 / 12) - 1
    disc = [r["contribution"] / N / (1 + dm) ** r["month"] for r in rows]
    ltv36 = sum(disc[:36])
    ltv60 = sum(disc[:60])
    cum, payback = 0.0, None
    for r in rows:
        cum += r["contribution"] / N
        if payback is None and cum >= cac:
            payback = r["month"]
    out = {
        "cac": cac,
        "payback_months": payback,
        "ltv36": ltv36,
        "ltv60": ltv60,
        "ltv36_cac": ltv36 / cac,
        "ltv60_cac": ltv60 / cac,
    }
    out["m12_still"] = rows[11]["survival"]
    y1_rev = sum(r["revenue"] for r in rows[:12])
    out["capital_per_rev"] = (sum(r["capital_locked"] for r in rows[:12]) / 12 / y1_rev) if y1_rev else 0.0
    for y in range(1, 6):
        yr = rows[(y - 1) * 12: y * 12]
        active_years = sum(r["active"] for r in yr) / 12
        out[f"y{y}_active_avg"] = active_years
        out[f"y{y}_rev_per_active"] = sum(r["revenue"] for r in yr) / active_years
        out[f"y{y}_cm_per_active"] = sum(r["contribution"] for r in yr) / active_years
        out[f"y{y}_rev_per_activated"] = sum(r["revenue"] for r in yr) / N
        out[f"y{y}_cm_per_activated"] = sum(r["contribution"] for r in yr) / N
        out[f"y{y}_capital_per_activated"] = sum(r["capital_locked"] for r in yr) / 12 / N
        for line, cols in REV_LINES.items():
            out[f"y{y}_rev_per_active::{line}"] = sum(r[c] for r in yr for c in cols) / active_years
    return out


COST_LINES = {"pay": "cost_payments", "service": "cost_service", "fraud": "cost_fraud",
              "loans": "cost_loans", "cards": "cost_cards", "ins": "cost_insurance"}
STORY_REV = {"gold": ("rev_gold",), "loans": ("rev_loans",), "ins": ("rev_insurance",)}


def story(p: dict, rows: list[dict], out: dict) -> dict:
    """The story deck's numbers: cost per active saver by line, how many savers ever
    borrow, what that makes each borrower cost to find, and which lines earn over 60 months."""
    N = p["cohort_size"]
    s = {}
    for y in range(1, 6):
        yr = rows[(y - 1) * 12: y * 12]
        act = sum(r["active"] for r in yr) / 12
        for slug, col in COST_LINES.items():
            s[f"y{y}_cost_{slug}"] = sum(r[col] for r in yr) / act
    for n in (12, 24, 60):
        s[f"borrow_{n}"] = sum(r["loans_new"] for r in rows[:n]) / N
    s["cac_per_borrower"] = out["cac"] / s["borrow_60"]
    s["reach3"] = sum(r["loans_r3"] for r in rows[:60]) / N        # reached loan 3 (part secured)
    s["reach5"] = sum(r["loans_r5new"] for r in rows[:60]) / N     # reached loan 5 (first unsecured)
    s["sec_start"] = rows[int(p["loan_start"]) - 1]["sec_loan"]    # secured loan size when loans start
    s["sec_m12"] = rows[11]["sec_loan"]
    rev60 = sum(r["revenue"] for r in rows[:60])
    for slug, cols in STORY_REV.items():
        s[f"rev60_{slug}"] = sum(r[c] for r in rows[:60] for c in cols) / rev60
    return s


# ---------------------------------------------------------------- lending-first
def amortised(principal: float, annual_rate: float, n: int) -> tuple[float, float]:
    """(total interest, mean opening balance as a share of principal)."""
    i = annual_rate / 12
    emi = principal * i / (1 - (1 + i) ** -n)
    bal, opening = principal, []
    for _ in range(n):
        opening.append(bal)
        bal = bal * (1 + i) - emi
    return emi * n - principal, sum(opening) / n / principal


def lending_first(q: dict, disc_rate: float) -> tuple[list[dict], dict]:
    """A Bueno-style cohort: 1,000 applicants, loans booked at disbursal."""
    Na = q["lf_applicants"]
    T = int(q["lf_tenor"])
    P = q["lf_ticket"]
    interest, avg_frac = amortised(P, q["lf_irr"], T)
    cof, _ = amortised(P, q["lf_cof"], T)
    borrowers = Na * q["lf_approval"]
    rows: list[dict] = []
    for t in range(1, MONTHS + 1):
        first = borrowers if t == 1 else 0.0
        if t > T:
            b = rows[t - T - 1]
            rep = q["lf_repeat"] * ((1 - q["lf_dpd90_first"]) * b["loans_first"] + (1 - q["lf_dpd90_repeat"]) * b["loans_repeat"])
        else:
            rep = 0.0
        net_rev = first * (interest * (1 - q["lf_dpd90_first"]) - cof) + rep * (interest * (1 - q["lf_dpd90_repeat"]) - cof)
        lost = q["lf_ead"] * q["lf_lgd"]
        losses = (first * q["lf_dpd90_first"] + rep * q["lf_dpd90_repeat"]) * lost * P * q["lf_risk_share"]
        per_loan = q["lf_collection"] + q["lf_ops_cost"] + q["lf_platform_share"] * q["lf_platform_fee"]
        cost = losses + (first + rep) * per_loan
        rows.append({"month": t, "loans_first": first, "loans_repeat": rep,
                     "revenue": net_rev, "losses": losses, "cost": cost,
                     "contribution": net_rev - cost,
                     "book": (first + rep) * P * avg_frac * T})  # loan-months of balance started this month
    cac_applicant = q["lf_cost_per_applicant"] + q["lf_underwrite_cost"]
    cac_borrower = cac_applicant / q["lf_approval"]
    cac_good = cac_applicant / (q["lf_approval"] * (1 - q["lf_dpd90_first"]))
    dm = (1 + disc_rate) ** (1 / 12) - 1
    disc = [r["contribution"] / borrowers / (1 + dm) ** r["month"] for r in rows]
    cum, payback = 0.0, None
    for r in rows:
        cum += r["contribution"] / borrowers
        if payback is None and cum >= cac_borrower:
            payback = r["month"]
    y1 = rows[:12]
    y1_rev = sum(r["revenue"] for r in y1)
    avg_book_y1 = sum(r["book"] for r in y1) / 12
    out = {
        "cac_per_applicant": cac_applicant,
        "cac": cac_borrower,
        "cac_per_good_borrower": cac_good,
        "payback_months": payback,
        "ltv36": sum(disc[:36]),
        "ltv60": sum(disc[:60]),
        "ltv36_cac": sum(disc[:36]) / cac_borrower,
        "ltv60_cac": sum(disc[:60]) / cac_borrower,
        "first_loan_contribution": interest * (1 - q["lf_dpd90_first"]) - cof - q["lf_dpd90_first"] * q["lf_ead"] * q["lf_lgd"] * P * q["lf_risk_share"] - (q["lf_collection"] + q["lf_ops_cost"] + q["lf_platform_share"] * q["lf_platform_fee"]),
        "y1_rev_per_borrower": y1_rev / borrowers,
        "y1_cm_per_borrower": sum(r["contribution"] for r in y1) / borrowers,
        "capital_per_rev": q["lf_equity_ratio"] * avg_book_y1 / y1_rev if y1_rev > 0 else float("inf"),
    }
    return rows, out


# ---------------------------------------------------------------- path to $100M
PATH_YEARS = 10


def load_path() -> list[dict]:
    return [{k: (float(v) if k not in ("basis", "notes") else v) for k, v in r.items()} for r in _read("inputs_path.csv")]


def cohort_year_curves(p: dict, out: dict) -> dict:
    """Per activated saver, by cohort year k = 0..PATH_YEARS (k=0 is zero)."""
    N = p["cohort_size"]
    tail = (1 - p.get("churn_path", p["churn_late"])) ** 12
    curves = {}
    for key, src in (("rev", "rev_per_activated"), ("cm", "cm_per_activated"), ("active", "active_avg"),
                     ("capital", "capital_per_activated")):
        vals = [0.0] + [out[f"y{k}_{src}"] / (N if key == "active" else 1) for k in range(1, 6)]
        for k in range(6, PATH_YEARS + 1):
            vals.append(vals[5] * tail ** (k - 5))
        curves[key] = vals
    return curves


def path(p: dict, out: dict, alt: tuple[dict, dict] | None = None, switch_year: int | None = None) -> list[dict]:
    """Calendar years 1..10. Savers acquired evenly through a year spend on
    average half a year in their first cohort year, so calendar year Y gets
    0.5*v(Y-c) + 0.5*v(Y-c+1) from the cohort acquired in year c.

    Capital locked (guarantee deposits, or NBFC equity with its minimum net
    owned fund) is cash the company must hold: its increase is a cash outflow.
    `alt` = (p, out) of another design used from `switch_year` on (e.g. own NBFC from year 3)."""
    plan = load_path()
    curves = cohort_year_curves(p, out)
    alt_curves = cohort_year_curves(*alt) if alt else None
    rows, cum, cap_prev = [], 0.0, 0.0
    for Y in range(1, PATH_YEARS + 1):
        r = {"year": Y}
        use_alt = alt is not None and Y >= switch_year
        cv, pp = (alt_curves, alt[0]) if use_alt else (curves, p)
        for key in ("rev", "cm", "active", "capital"):
            v = cv[key]
            r[key] = sum(plan[c - 1]["new_activated"] * 0.5 * (v[Y - c] + v[Y - c + 1]) for c in range(1, Y + 1))
        if pp["nbfc_on"]:
            r["capital"] = max(pp["nbfc_nof_cr"] * 1e7, r["capital"])
        pl = plan[Y - 1]
        r["new_activated"] = pl["new_activated"]
        r["cac_spend"] = pl["new_activated"] * out["cac"] * pl["cac_scale"]
        r["fixed_opex"] = (pl["fixed_opex_cr"] + pp["nbfc_on"] * pp["nbfc_fixed_cr"]) * 1e7
        r["capital_increase"] = r["capital"] - cap_prev
        cap_prev = r["capital"]
        r["cash"] = r["cm"] - r["cac_spend"] - r["fixed_opex"] - r["capital_increase"]
        cum += r["cash"]
        r["cum_cash"] = cum
        r["rev_usd_m"] = r["rev"] / p["usd_inr"] / 1e6
        r["rev_per_active"] = r["rev"] / r["active"] if r["active"] else 0.0
        rows.append(r)
    return rows


# ---------------------------------------------------------------- sensitivity
def tornado(metric: str = "ltv60_cac", variant: str | None = None) -> list[dict]:
    """Swing each input from its bear to its bull value (in both segments), others at base."""
    base_p = load_inputs("base", load_variant(variant, "base"))
    _, _, base_out, _ = run("base", variant=variant)
    bear_p = load_inputs("bear", load_variant(variant, "bear"))
    bull_p = load_inputs("bull", load_variant(variant, "bull"))
    bear_n = load_inputs("bear", load_variant(variant, "bear"), "ng")
    bull_n = load_inputs("bull", load_variant(variant, "bull"), "ng")
    rows = []
    for k in base_p:
        if bear_p[k] == bull_p[k] and bear_n[k] == bull_n[k]:
            continue
        lo = run("base", {f"{k}@gig": bear_p[k], f"{k}@ng": bear_n[k]}, variant)[2][metric]
        hi = run("base", {f"{k}@gig": bull_p[k], f"{k}@ng": bull_n[k]}, variant)[2][metric]
        rows.append({"input": k, "bear_value": bear_p[k], "base_value": base_p[k], "bull_value": bull_p[k],
                     "metric_at_bear": lo, "metric_at_base": base_out[metric], "metric_at_bull": hi,
                     "swing": abs(hi - lo)})
    return sorted(rows, key=lambda r: -r["swing"])


def solve_for(inp: str, target: float = 3.0, metric: str = "ltv60_cac", scenario: str = "base",
              lo: float | None = None, hi: float | None = None, extra: dict | None = None) -> float | None:
    """Value of one input that makes `metric` hit `target`, all else at `scenario`.
    Bisection between lo and hi (default: 0 and 10x the bull value). None if the
    target is not reachable inside that range."""
    p = load_inputs(scenario)
    bull = load_inputs("bull")[inp]
    lo = 0.0 if lo is None else lo
    hi = max(abs(bull) * 10, 1e-6) if hi is None else hi

    def f(x):
        return run(scenario, {**(extra or {}), inp: x})[2][metric] - target

    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        fm = f(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return (lo + hi) / 2


# ---------------------------------------------------------------- runners
ADDITIVE_SKIP = {"month", "survival", "borrowed_share", "card_share", "unsec_share", "sip_share", "insured_share", "lendable", "sec_loan"}
SHARES = ("borrowed_share", "card_share", "unsec_share", "sip_share", "insured_share")


def combine(parts: list[list[dict]], N: float) -> list[dict]:
    """Add segment cohorts month by month. Shares are weighted by active savers."""
    rows = []
    for ms in zip(*parts):
        r = {"month": ms[0]["month"]}
        for k in ms[0]:
            if k not in ADDITIVE_SKIP:
                r[k] = sum(m[k] for m in ms)
        r["survival"] = r["active"] / N
        for k in SHARES:
            r[k] = sum(m[k] * m["active"] for m in ms) / r["active"] if r["active"] else 0.0
        for k in ("lendable", "sec_loan"):
            r[k] = sum(m[k] * m["active"] for m in ms) / r["active"] if r["active"] else 0.0
        rows.append(r)
    return rows


def run(scenario: str, overrides: dict | None = None, variant: str | None = None) -> tuple[dict, list[dict], dict, list[dict]]:
    """One monthly cohort of `cohort_size` activated savers: mix_gig of them gig, the rest non-gig."""
    ov = {**load_variant(variant, scenario), **(overrides or {})}
    ps = {seg: load_inputs(scenario, ov, seg) for seg in SEGMENTS}
    N, mix = ps["gig"]["cohort_size"], ps["gig"]["mix_gig"]
    weights = {"gig": mix, "ng": 1 - mix}
    chans = load_channels()
    seg_rows, seg_out, cacs, ch_rows = {}, {}, {}, []
    for seg in SEGMENTS:
        if weights[seg] <= 0:
            continue
        pseg = {**ps[seg], "cohort_size": N * weights[seg]}
        cacs[seg], chs = blended_cac(pseg, chans, seg)
        ch_rows += chs
        seg_rows[seg] = cohort(pseg)
        seg_out[seg] = summarize(pseg, seg_rows[seg], cacs[seg])
    rows = combine(list(seg_rows.values()), N)
    cac = sum(weights[s] * cacs[s] for s in cacs)
    p = {**ps["gig"], "churn_path": sum(weights[s] * ps[s]["churn_late"] for s in cacs)}
    out = summarize(p, rows, cac)
    out["seg"] = seg_out
    out["seg_cac"] = cacs
    return p, rows, out, ch_rows


if __name__ == "__main__":
    import sys
    VAR = sys.argv[1] if len(sys.argv) > 1 else None
    print(f"variant: {VAR or 'inputs as they stand'}")
    for s in SCENARIOS:
        p, rows, out, ch = run(s, variant=VAR)
        lrows, lout = lending_first(load_lf(s), p["disc_rate"])
        print(f"\n=== {s} ===")
        print(f"CAC {out['cac']:.0f}  payback {out['payback_months']}  LTV36 {out['ltv36']:.0f}  LTV60 {out['ltv60']:.0f}  LTV60/CAC {out['ltv60_cac']:.2f}")
        for y in range(1, 6):
            parts = "  ".join(f"{k.split('::')[1]}={v:.0f}" for k, v in out.items() if k.startswith(f"y{y}_rev_per_active::"))
            print(f" y{y} rev/active {out[f'y{y}_rev_per_active']:.0f}  cm/active {out[f'y{y}_cm_per_active']:.0f}  | {parts}")
        print(f" lending-first: CAC/borrower {lout['cac']:.0f}  first-loan CM {lout['first_loan_contribution']:.0f}  LTV60 {lout['ltv60']:.0f}  LTV60/CAC {lout['ltv60_cac']:.2f}  payback {lout['payback_months']}")
        pr = path(p, out)
        print(" path: " + "  ".join(f"Y{r['year']} ${r['rev_usd_m']:.0f}M/{r['active']/1e6:.1f}M act" for r in pr))
        print(f" peak cash need Rs {-min(r['cum_cash'] for r in pr)/1e7:.0f} cr")
    print("\nTornado on LTV60/CAC (base):")
    for r in tornado()[:8]:
        print(f"  {r['input']:<16} {r['metric_at_bear']:6.2f} .. {r['metric_at_bull']:6.2f}  swing {r['swing']:.2f}")

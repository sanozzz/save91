"""Monte Carlo around the online-first model (21 Oct 2026). Operator: "ranges + Monte Carlo"; online ranges agreed the same
day ("OK as proposed"); every other engine input keeps its agreed 16 Oct distribution (tables/dist_agreed_v1.csv), sampled by
model/cohort_mc.py's Latin hypercube. The agreed bad-year copula (approvals and losses, rho -0.5) is still sampled, but online
it moves nothing: first approval is drawn from ONLINE below and losses fall on the lender (critical review AN-04, 22 Oct).
Instead LINKS (below) ties the inputs that move together. The plan is each range's most likely value and the low ends reach
the folder's evidence (22 Oct); the ranges are still ours, so read the results as a stress test, not odds.

Online ranges (PERT low / likely / high): the ONLINE dict below (daily amount, retention, cost to win, apply rate, loan size,
first approval, payout, loan reach, equity share and return).
Fixed: doorstep share 10% of savers; the online design switches (UPI, no term payout, no collection fees, KYC inside the CAC);
insurance (fixed referral fee, not counted), Choti SIP and digital gold off. Doorstep savers draw the agreed street r3 / r12;
agents draw signups_run.

Each draw runs both plans: the PROFITABLE PATH (20,000 online savers a month from month 30) and GROW FAST (1.5 lakh).
Writes tables/online_mc_draws.csv, online_mc_summary.csv, online_mc_drivers.csv, online_mc_inputs.csv."""
import csv
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.stats import qmc

import cohort_engine as E
import cohort_mc as MC
import online_plan as op

N = 1000
SEED = 20261021
PLANS = (("Profitable path", 20000), ("Grow fast", 150000))
P_ = "pert"
ONLINE = {   # key: (shape, low, likely, high, label, basis)
    "on_daily": (P_, 50, 100, 300, "Daily amount (Rs)", "PhonePe daily SIP ~Rs 50 / Bachatt minimum Rs 100 / Bachatt film Rs 300"),
    "on_r12": (P_, 0.24, 0.38, 0.45, "Online: still saving at 12 months", "savings apps 24% / SBI MF Rs 250 daily SIP ~38% / credit hook 45%"),
    "on_r3": (P_, 0.52, 0.80, 0.85, "Online: still saving at month 3", "app curve 52% / SBI steady drop ~80%"),
    # critical review 22 Oct: the plan stays the most likely value; the low (or high) ends now reach the folder's own evidence
    "cac": (P_, 300, 450, 800, "Cost to win a saver after the seed (Rs, all-in)", "a competitor's figure (PR-02) / midpoint (operator 21 Oct) / costs rise with scale (Groww Rs 796-1,374, TB-18)"),
    "on_apply": (P_, 0.02, 0.35, 0.50, "Reachable users who apply for a loan a year (all loan types)",
                 "payments-app merchants ~1-2% (XF-16) / founders' 35% / credit-hungry; fintech borrowers ~49% re-borrow in 6 months (XF-15..17)"),
    "on_ticket": (P_, 25000, 300000, 500000, "Personal + business loan size, blended (Rs)",
                  "the founders' own 2019-22 book Rs 10-25k (XF-24) / founders' Rs 3 lakh (22 Oct) / unsecured business loans up to Rs 5 lakh (XF-09)"),
    "on_approved": (P_, 0.11, 0.30, 0.45, "First loan applications approved", "a digital lender's 11% of new applicants (XL-41) / 30% / PSU banks approve ~80% of pre-qualified (XF-18, XF-24)"),
    "on_fee": (P_, 0.01, 0.02, 0.03, "Our payout on personal + business loans, at the start", "DSA payout 1-2.5%, up to 3% (XF-01/02); rises 1.5x by year 5"),
    "on_reach": (P_, 1.0, 2.5, 2.5, "KYC'd users reached by loan offers, per online saver won", "savers only / every KYC'd user (5 sign-ups, half KYC) staying as long as savers"),
    "eq_share": (P_, 0.50, 0.80, 0.90, "Equity share of the savings", "Bachatt conversation: about 80% choose equity SIPs"),
    "eq_return": (P_, 0.06, 0.10, 0.12, "Equity return a year, net", "our estimate"),
}
# critical review 22 Oct: inputs that move together are drawn together (Gaussian copula on the online draws):
# credit-hungry savers stay (Saket, PR-03); more sign-ups per saver raise both the cost to win and the loan reach;
# a wider funnel brings smaller loans and lower approval.
LINKS = {("on_apply", "on_r12"): 0.5, ("cac", "on_reach"): 0.5, ("on_apply", "on_ticket"): -0.3, ("on_apply", "on_approved"): -0.3}
NAMES = {r["key"]: r["name"] for r in csv.DictReader((op.TAB / "dist_agreed_v1.csv").open())}
FIXED_DESIGN = {"rollover", "upi_12", "upi_ramp", "fee_early", "fee_b3", "kyc_cost", "marketplace_from", "term", "r3", "r12",
                "daily", "apply", "ticket", "trail", "fund_return", "sip_takeup", "signups_run", "loan_home_ticket",
                # the loan marketplace baseline (21 Oct) replaces the agreed loan funnel; drawn below from ONLINE instead
                "eligible", "approved_first", "fee", "tenure", "loan_gold_takeup", "loan_gold_ticket", "loan_gold_comm",
                "loan_lap_takeup", "loan_lap_ticket", "loan_lap_comm", "loan_home_takeup", "loan_home_comm",
                # critical review 22 Oct: insurance earns a fixed referral fee (not counted); Choti SIP and digital gold off
                "ins_partner_share", "choti_takeup", "gold_takeup"}
OUT = ("profit_month_p", "money_p", "y5_ebitda_p", "y8_ebitda_p", "profit_month_f", "money_f", "y5_ebitda_f", "y8_ebitda_f",
       "online_rev60", "door_rev60")


def sample():
    dists = E.load_dists()[0]
    keys = list(E.KEYS) + list(ONLINE)
    allspec = {**{k: dists[k][:4] for k in E.KEYS}, **{k: v[:4] for k, v in ONLINE.items()}}
    U = qmc.LatinHypercube(d=len(keys), seed=SEED).random(N)
    r = MC.bad_year_rho()
    cov = np.array([[1, r * r, r], [r * r, 1, r], [r, r, 1]])
    cols = [keys.index(k) for k in MC.COPULA_KEYS]
    U[:, cols] = stats.norm.cdf(stats.norm.ppf(U[:, cols]) @ np.linalg.cholesky(cov).T)
    lk = sorted({k for pair in LINKS for k in pair})
    C = np.eye(len(lk))
    for (a, b), rho in LINKS.items():
        C[lk.index(a), lk.index(b)] = C[lk.index(b), lk.index(a)] = rho
    cols = [keys.index(k) for k in lk]
    U[:, cols] = stats.norm.cdf(stats.norm.ppf(U[:, cols]) @ np.linalg.cholesky(C).T)
    x = {k: MC.ppf(*allspec[k], U[:, i]) for i, k in enumerate(keys)}
    rng = np.random.default_rng(SEED + 7)
    for a, b in (("r3", "r12"), ("on_r3", "on_r12")):             # still saving at 12 months below month 3
        bad = x[b] >= x[a]
        while bad.any():
            for k in (a, b):
                x[k][bad] = MC.ppf(*allspec[k], rng.random(int(bad.sum())))
            bad = x[b] >= x[a]
    return x


def run_draw(x, i):
    op._CACHE.clear()
    ov = {k: float(x[k][i]) for k in E.KEYS if k not in FIXED_DESIGN}
    eq = float(x["eq_share"][i])
    ov.update({"daily": float(x["on_daily"][i]), "r3": float(x["on_r3"][i]), "r12": float(x["on_r12"][i]),
               **op.loan_mix(float(x["on_apply"][i])), "ticket": float(x["on_ticket"][i]),
               "approved_first": float(x["on_approved"][i]), "fee": float(x["on_fee"][i]), "_loan_reach": float(x["on_reach"][i]),
               "trail": eq * float(x["sip_comm"][i]) + (1 - eq) * float(x["trail"][i]),
               "fund_return": eq * float(x["eq_return"][i]) + (1 - eq) * float(x["fund_return"][i]), "sip_takeup": 0.0})
    op.OV.clear()
    op.OV.update(ov)
    op.DOOR.update({"r3": float(x["r3"][i]), "r12": float(x["r12"][i])})
    op.AGENT_SIGNUPS = float(x["signups_run"][i])
    res = {}
    for tag, (nm, lvl) in zip(("p", "f"), PLANS):
        o = op.company(lvl, 1.0, cac=float(x["cac"][i]))
        m = op.positive_from(o["ebitda"])
        res[f"profit_month_{tag}"] = m if m is not None else 97
        res[f"money_{tag}"] = o["money_needed"] / op.FX / 1e6
        res[f"y5_ebitda_{tag}"] = o["ebitda"][48:60].sum() / op.CR
        res[f"y8_ebitda_{tag}"] = o["ebitda"][84:96].sum() / op.CR
    res["online_rev60"] = op.ltv_parts(op.saver_inputs())["income"][:60].sum()
    res["door_rev60"] = op.ltv_parts(op.saver_inputs(doorstep=True), 1.0)["income"][:60].sum()
    return res


def pct(v):
    return {f"P{q}": round(float(np.percentile(v, q)), 2) for q in (10, 50, 90)}


def main():
    x = sample()
    rows = [run_draw(x, i) for i in range(N)]
    o = {k: np.array([r[k] for r in rows], dtype=float) for k in OUT}
    op.OV.clear()
    op.DOOR.update({"r3": 0.80, "r12": op.X0["r12"]})
    op.AGENT_SIGNUPS = 100.0
    summ = []
    for tag, (nm, lvl) in zip(("p", "f"), PLANS):
        pm = o[f"profit_month_{tag}"]
        summ.append({"plan": nm, "online savers a month": lvl, "draws": N,
                     "chance EBITDA positive by month 60": round(float((pm <= 60).mean()), 3),
                     "chance by month 54": round(float((pm <= 54).mean()), 3),
                     "chance never by month 96": round(float((pm > 96).mean()), 3),
                     **{f"profit month {k}": v for k, v in pct(pm).items()},
                     **{f"money needed $M {k}": v for k, v in pct(o[f'money_{tag}']).items()},
                     **{f"Y5 EBITDA Rs cr {k}": v for k, v in pct(o[f'y5_ebitda_{tag}']).items()},
                     **{f"Y8 EBITDA Rs cr {k}": v for k, v in pct(o[f'y8_ebitda_{tag}']).items()}})
    summ.append({"plan": "One online saver, 60-month revenue (Rs)", **{k: v for k, v in pct(o["online_rev60"]).items()}})
    summ.append({"plan": "One doorstep saver, 60-month revenue (Rs)", **{k: v for k, v in pct(o["door_rev60"]).items()}})
    keys = [k for k in list(E.KEYS) + list(ONLINE) if np.ptp(x[k]) > 0 and k not in FIXED_DESIGN and k not in ("signups_run_unused",)]
    drv = []
    for k in keys:
        if k in FIXED_DESIGN and k not in ("r3", "r12", "trail", "fund_return", "signups_run"):
            continue
        rho_m = stats.spearmanr(x[k], o["money_p"]).statistic
        rho_e = stats.spearmanr(x[k], o["y5_ebitda_p"]).statistic
        drv.append({"input": k, "label": ONLINE[k][4] if k in ONLINE else NAMES.get(k, k),
                    "rank corr with money needed (profitable path)": round(float(rho_m), 3),
                    "rank corr with Y5 EBITDA (profitable path)": round(float(rho_e), 3)})
    drv.sort(key=lambda r: -abs(r["rank corr with money needed (profitable path)"]))
    with (op.TAB / "online_mc_summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in summ for k in r}, key=lambda k: list(summ[0]).index(k) if k in summ[0] else 99))
        w.writeheader()
        w.writerows(summ)
    with (op.TAB / "online_mc_drivers.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(drv[0]))
        w.writeheader()
        w.writerows(drv)
    with (op.TAB / "online_mc_draws.csv").open("w", newline="") as f:
        cols = list(ONLINE) + ["r3", "r12", "signups_run", "sip_comm", "trail", "fund_return", "approved_first", "loss"] + list(OUT)
        w = csv.writer(f)
        w.writerow(cols)
        for i in range(N):
            w.writerow([round(float(x[c][i]), 6) if c in x else round(float(o[c][i]), 4) for c in cols])
    with (op.TAB / "online_mc_inputs.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "label", "shape", "low", "likely", "high", "basis"])
        for k, (sh, lo, li, hi, lab, basis) in ONLINE.items():
            w.writerow([k, lab, sh, lo, li, hi, basis])
    for s in summ:
        print(s)
    print("top drivers:")
    for d in drv[:12]:
        print(d)


if __name__ == "__main__":
    main()

"""Seed plan (21 Oct 2026): the $0.5M pitch, mostly to build the product.
Operator, 21 Oct, in order:
  - "raise around 0.5 mil to 1mil ... create app, tie-ups with mutual funds etc" -> "I am pitching 0.5m"
  - "This money is raised majorly to build the product"
  - "company setup takes 1.25 lacs"; "We will be a marketing company not LSP initially"
  - "My costs on salaries shouldnt be more than 100k total across 2 years ... including founders taking 1K each per month";
    "we can add 1-2 more incase required"
  - "100,000 signups only"
  - "Piyush CEO, Sandeep CPTO. Piyush owns growth as well"
Channel: online-first, ~20% of SAVERS from a doorstep test arm (operator 19 Oct).

The $0.5M = customers (whatever 1 lakh sign-ups costs) + product and team for 24 months + whatever is left (reserve).
Cost inputs are the agreed ones (tables/base_inputs.csv, dist_agreed_v1.csv likely values) unless marked OPERATOR or
JUDGEMENT. Revenue is left out on purpose (conservative). The "lean" cost set is the critical review's proposal, shown
side by side and NOT applied to the plan until the operator agrees.
Writes tables/seed_inputs.csv, seed_plans.csv, seed_people.csv, seed_monthly_pitch.csv, seed_sensitivity.csv."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "tables"

FX = 95.0                      # OPERATOR 21 Oct: "Plannign rate should be 95 rs"
RAISE_USD = 500_000            # OPERATOR
TARGET_SIGNUPS = 100_000       # OPERATOR 21 Oct: "100,000 signups only" (online sign-ups + doorstep sign-ups)
SALARY_CAP_USD, PLAN_MONTHS = 100_000, 24   # OPERATOR 21 Oct
LAUNCH, SELL_END = 4, 18       # JUDGEMENT: app + ARN + exchange + KYC ready in 3 months; customers won in months 4-18

PAY = {"Piyush (CEO)": 1_000 * FX, "Sandeep (CPTO)": 1_000 * FX,            # OPERATOR: $1k a month each
       "Engineer (full-stack + mobile)": 110_000,                           # JUDGEMENT, all-in CTC, set to fit the cap
       "Ops + support executive": 30_000,                                   # (agreed base: engineer 120,000; ops 40,000)
       "Junior engineer": 50_000,
       "Growth executive (performance ads)": 40_000}
TEAMS = {"plan": [("Piyush (CEO)", 1), ("Sandeep (CPTO)", 1), ("Engineer (full-stack + mobile)", 1),
                  ("Ops + support executive", 4), ("Junior engineer", 7)],
         # if Piyush hands growth off: a growth executive in place of the junior engineer (both do not fit the cap)
         "growth_hire": [("Piyush (CEO)", 1), ("Sandeep (CPTO)", 1), ("Engineer (full-stack + mobile)", 1),
                         ("Ops + support executive", 4), ("Growth executive (performance ads)", 4)]}
DESIGN = 100_000               # JUDGEMENT: outsourced design while the app is built, months 1-3 only

COSTS = {   # "agreed" = base_inputs (operator 17 Oct) + co-working; "lean" = the critical review's proposal (JUDGEMENT)
    "agreed": {"tech_oneoff": 1_500_000, "tech_month": lambda m: 150_000, "lic_year": 1_000_000, "office": 75_000},
    "lean": {"tech_oneoff": 500_000, "tech_month": lambda m: 50_000 if m <= 6 else 100_000, "lic_year": 500_000, "office": 40_000},
}
SETUP = 125_000                # OPERATOR 21 Oct: company setup Rs 1.25 lakh, one-time (read as incl. ARN + NISM)
RAISE_COST = 500_000           # fund-raising cost, seed (base_inputs)

REG_COST = 100                 # Rs per online registration (install + sign-up): TB-19 installs Rs 100-300, low end with
                               # referrals; = agreed online_cac Rs 499 per saver at the 20% activation below
KYC_RATE = 0.50                # JUDGEMENT: registrations that complete KYC
SAVE_RATE = 0.40               # JUDGEMENT: KYC'd who start a SIP -> 20% of registrations become savers
KYC_COST = 40                  # Rs per KYC (dist_agreed kyc_cost likely)
SUPPORT = 5                    # Rs per active saver a month (dist_agreed support_cost likely)
R12_ONLINE, R12_OFFLINE = 0.38, 0.55   # still saving at month 12: online = SBI MF's Rs 250 daily SIP (operator 21 Oct;
                                       # was the savings-app 24%); doorstep = agreed street r12

AGENT_MONTH = 20_000 + 3_000 + 2_000   # salary + statutory (base_inputs) + incentive ~Rs 2k in year 1 (our estimate)
AGENT_SIGNUPS = 100            # sign-ups a month at full speed (dist_agreed signups_run likely)
RAMP = [0.5, 2 / 3, 5 / 6]     # first three months on the job (dist_agreed ramp_months 3, from 50%)
HIRE_KIT = 12_000              # per hire incl. replacements (base_inputs); 30% of agents leave a year (base_inputs)
CASH_COVER = 1_000             # per agent a month (dist_agreed cash_cover likely)
OFFLINE_SHARE = 0.10           # share of SAVERS from the doorstep arm (operator 21 Oct: 90% online, 10% offline); Piyush supervises, no field lead
                               # and no city office (people review 21 Oct)

ACQ_COLS = ["Online acquisition", "KYC", "Doorstep test arm"]
TP_COLS = ["Salaries", "Design (outsourced)", "App and tech", "Licences and compliance", "Office and fund-raising", "Support"]


def agent_signups(months_on):
    return sum(AGENT_SIGNUPS * (RAMP[i] if i < 3 else 1) for i in range(months_on))


def size(registrations):
    need = registrations * KYC_RATE * SAVE_RATE * OFFLINE_SHARE / (1 - OFFLINE_SHARE)
    return max(1, round(need / agent_signups(SELL_END - LAUNCH + 1)))


def run(registrations, agents, months, team="plan", costs="agreed"):
    """Month by month. Online registrations spread evenly over months LAUNCH..SELL_END; agents work the same months."""
    c = COSTS[costs]
    selling = SELL_END - LAUNCH + 1
    s_on, s_off = R12_ONLINE ** (1 / 12), R12_OFFLINE ** (1 / 12)
    rows, act_on, act_off = [], 0.0, 0.0
    for m in range(1, months + 1):
        sell = LAUNCH <= m <= SELL_END
        reg = registrations / selling if sell else 0
        k = m - LAUNCH
        new_on = reg * KYC_RATE * SAVE_RATE
        new_off = agents * AGENT_SIGNUPS * (RAMP[k] if k < 3 else 1) if sell else 0
        act_on = act_on * s_on + new_on
        act_off = act_off * s_off + new_off
        h = (agents if m == LAUNCH else agents * 0.3 / 12) if sell else 0
        rows.append({
            "month": m, "registrations": reg, "new_online_savers": new_on, "new_offline_savers": new_off,
            "active_online": act_on, "active_offline": act_off,
            "Salaries": sum(PAY[r] for r, st in TEAMS[team] if m >= st),
            "Design (outsourced)": DESIGN if m <= 3 else 0,
            "Online acquisition": reg * REG_COST,
            "KYC": (reg * KYC_RATE + new_off) * KYC_COST,
            "Doorstep test arm": agents * (AGENT_MONTH + CASH_COVER) * sell + h * HIRE_KIT,
            "App and tech": (c["tech_oneoff"] / 3 if m <= 3 else 0) + c["tech_month"](m),
            "Licences and compliance": (SETUP if m == 1 else 0) + c["lic_year"] / 12,
            "Office and fund-raising": c["office"] + (RAISE_COST if m == 1 else 0),
            "Support": (act_on + act_off) * SUPPORT,
        })
    df = pd.DataFrame(rows)
    df["acquisition"] = df[ACQ_COLS].sum(axis=1)
    df["team_and_product"] = df[TP_COLS].sum(axis=1)
    return df


def solve_signups(target):
    lo, hi = 0.0, 1e7
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if mid + agent_signups(SELL_END - LAUNCH + 1) * size(mid) <= target else (lo, mid)
    return lo


def plan(name, registrations, team="plan", costs="agreed"):
    agents = size(registrations)
    acq = run(registrations, agents, SELL_END, team, costs)["acquisition"].sum()
    budget = RAISE_USD * FX - acq                     # everything not spent on customers runs product and team
    runway = max(m for m in range(SELL_END, 80) if run(registrations, agents, m, team, costs)["team_and_product"].sum() <= budget)
    d = run(registrations, agents, max(runway, PLAN_MONTHS), team, costs)
    d24 = d.iloc[:PLAN_MONTHS]
    off, on = d["new_offline_savers"].sum(), d["new_online_savers"].sum()
    out = {"plan": name, "team": team, "costs": costs, "online_registrations": registrations, "doorstep_signups": off,
           "customers": registrations + off, "savers_won": on + off, "agents": agents,
           "active_savers_m18": d.active_online.iloc[SELL_END - 1] + d.active_offline.iloc[SELL_END - 1],
           "acq_usd": acq / FX, "acq_per_saver": acq / (on + off), "tp_24_usd": d24["team_and_product"].sum() / FX,
           "salaries_24_usd": d24["Salaries"].sum() / FX, "reserve_24_usd": (budget - d24["team_and_product"].sum()) / FX,
           "runway_months": runway, "tp_month_after_18": d["team_and_product"].iloc[SELL_END]}
    for col in ACQ_COLS + TP_COLS:
        out[col] = d24[col].sum()
    if name == "pitch":
        d.to_csv(TAB / "seed_monthly_pitch.csv", index=False)
    return out


def main():
    reg = solve_signups(TARGET_SIGNUPS)
    p = pd.DataFrame([plan("pitch", reg), plan("pitch_lean_costs", reg, costs="lean"), plan("pitch_growth_hire", reg, team="growth_hire")])
    p.to_csv(TAB / "seed_plans.csv", index=False)

    people = []
    for team in TEAMS:
        for role, st in TEAMS[team]:
            people.append({"team": team, "role": role, "start_month": st, "pay_rs_month": PAY[role],
                           "cost_24_usd": PAY[role] * (PLAN_MONTHS - st + 1) / FX})
    pd.DataFrame(people).to_csv(TAB / "seed_people.csv", index=False)

    global REG_COST, SAVE_RATE
    base = (REG_COST, SAVE_RATE)
    sens = []
    for lab, rc, sr in (("Agreed inputs", *base), ("Online sign-up costs Rs 60 (referrals work)", 60, base[1]),
                        ("Online sign-up costs Rs 200", 200, base[1]), ("1 in 10 sign-ups starts saving (Jar-like)", base[0], 0.20),
                        ("3 in 10 sign-ups start saving", base[0], 0.60)):
        REG_COST, SAVE_RATE = rc, sr
        r = solve_signups(TARGET_SIGNUPS)
        d = run(r, size(r), SELL_END)
        sav = d["new_online_savers"].sum() + d["new_offline_savers"].sum()
        sens.append({"case": lab, "acq_usd": d["acquisition"].sum() / FX, "savers_won": sav, "acq_per_saver": d["acquisition"].sum() / sav})
    REG_COST, SAVE_RATE = base
    pd.DataFrame(sens).to_csv(TAB / "seed_sensitivity.csv", index=False)

    inputs = [("Planning rate", FX, "Rs per $", "operator 21 Oct"),
              ("Raise", "$500k", "", "operator 21 Oct"),
              ("Sign-ups target", "1,00,000 (online + doorstep)", "", "operator 21 Oct"),
              ("Customers won", f"months {LAUNCH}-{SELL_END}", "", "JUDGEMENT"),
              ("Salary cap", "$100k over 24 months, founders included", "", "operator 21 Oct"),
              ("Piyush (CEO) / Sandeep (CPTO)", "$1,000 each", "a month", "operator 21 Oct"),
              ("Engineer (full-stack + mobile), month 1", PAY["Engineer (full-stack + mobile)"], "Rs a month, all-in", "JUDGEMENT (agreed base 120,000)"),
              ("Ops + support executive, month 4", PAY["Ops + support executive"], "Rs a month, all-in", "JUDGEMENT (agreed base 40,000)"),
              ("Junior engineer, month 7", PAY["Junior engineer"], "Rs a month, all-in", "JUDGEMENT"),
              ("Design while building (months 1-3)", DESIGN, "Rs a month", "JUDGEMENT"),
              ("Company setup, one-time", SETUP, "Rs", "operator 21 Oct (read as incl. ARN, NISM)"),
              ("Licences and compliance a year (CA, legal, renewals)", COSTS["agreed"]["lic_year"], "Rs", "base_inputs"),
              ("App integrations / running", "1,500,000 / 150,000 a month", "Rs", "base_inputs"),
              ("Office (co-working)", COSTS["agreed"]["office"], "Rs a month", "JUDGEMENT"),
              ("Online cost per registration", REG_COST, "Rs", "TB-19; = online_cac 499 at 20%"),
              ("Registrations that finish KYC / KYC'd who start saving", f"{KYC_RATE} / {SAVE_RATE}", "share", "JUDGEMENT"),
              ("KYC cost", KYC_COST, "Rs a KYC", "dist_agreed kyc_cost"),
              ("Support", SUPPORT, "Rs per active saver a month", "dist_agreed"),
              ("Still saving at 12 months, online / doorstep", f"{R12_ONLINE} / {R12_OFFLINE}", "share", "SBI MF Rs 250 daily SIP (operator 21 Oct) / agreed street r12"),
              ("Doorstep agent all-in", AGENT_MONTH + CASH_COVER, "Rs a month", "base_inputs + our incentive estimate"),
              ("Agent sign-ups at full speed", AGENT_SIGNUPS, "a month", "dist_agreed signups_run"),
              ("Doorstep share of savers", OFFLINE_SHARE, "share", "operator 19 Oct")]
    pd.DataFrame(inputs, columns=["input", "value", "unit", "source"]).to_csv(TAB / "seed_inputs.csv", index=False)
    for old in ("seed_monthly_one_million.csv", "seed_monthly_five_lakh.csv", "seed_monthly_half_million.csv"):
        (TAB / old).unlink(missing_ok=True)
    pd.set_option("display.width", 220)
    print(p[["plan", "customers", "online_registrations", "doorstep_signups", "savers_won", "active_savers_m18", "agents", "acq_usd",
             "salaries_24_usd", "tp_24_usd", "reserve_24_usd", "runway_months", "acq_per_saver"]].round(0).to_string())
    print(p.set_index("plan")[ACQ_COLS + TP_COLS].div(FX * 1e3).round(1).to_string())
    print(pd.DataFrame(sens).round(0).to_string())


if __name__ == "__main__":
    main()

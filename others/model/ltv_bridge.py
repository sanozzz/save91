"""The bridge from the 23 Oct main case (1.75x) to the 24 Oct main case: the founders' decisions applied one at a time. Writes tables/ltv_bridge.csv."""
import csv, online_plan as op
op.use_main_case(); NEW = dict(op.MAIN); op.use_main_case(False)
OLD = {"ticket": 169600.0, **op.loan_mix(0.2717), "approved_first": 0.2478, "takeup_growth": 0.0239, "approval_growth": 0.0478,
       "loan_home_ticket": 2061120.0, "loan_lap_ticket": 1456800.0, "_payout_rise": 0.2392, "r12": 0.3644, "churn_late": 0.0202,
       "_debt_trail": 0.0022, "approved_repeat": 0.7183, "_loan_reach": 1.7176, "_debit_cost": 2.0, "_debits_a_month": 52 / 12,
       "recharge_takeup": 0.25, "bills_takeup": 0.25, "fd_takeup": 0.10, "nps_takeup": 0.03, "_serve_contingency": False}
STEPS = [("Last week's main case (23 Oct)", {}),
         ("Serving carries the 10% contingency, as the company model does (a correction)", {"_serve_contingency": None}),
         ("Personal loans Rs 70k (Bachatt), not Rs 1.7 lakh", {"ticket": None}),
         ("Apply and approval at today's market, no yearly rises", {"apply": None, "loan_gold_takeup": None, "loan_lap_takeup": None,
            "loan_home_takeup": None, "approved_first": None, "takeup_growth": None, "approval_growth": None}),
         ("Home Rs 12 lakh and property Rs 5 lakh (market sizes)", {"loan_home_ticket": None, "loan_lap_ticket": None}),
         ("Lender payout 2% flat (market), no rise", {"_payout_rise": None}),
         ("Non-savers fade within ~3 months", {"_loan_reach": None}),
         ("Recharge, bills, FD and NPS not in the launch app", {"recharge_takeup": None, "bills_takeup": None, "fd_takeup": None, "nps_takeup": None}),
         ("Debits at Rs 0 to us (fund house / BSE StAR MF)", {"_debit_cost": None, "_debits_a_month": None}),
         ("Still saving at 12 months: Bachatt's 30-40% (median 35%); debt fund fee and repeat approval at the Monte Carlo median", {"r12": None, "churn_late": None, "_debt_trail": None, "approved_repeat": None})]
cur, rows, prev = dict(OLD), [], None
for nm, ch in STEPS:
    for k in ch:
        if k in NEW: cur[k] = NEW[k]
        else: cur.pop(k, None)
    op.SERVE_CONTINGENCY = "_serve_contingency" not in cur
    op.OV.clear(); op._CACHE.clear(); op.OV.update({k: v for k, v in cur.items() if k != "_serve_contingency"})
    _d, cum, v = op.ltv_view(op.saver_inputs(), op.CAC)
    x5 = float(cum[59]) / (op.CAC * (1 + op.CONTINGENCY))
    rows.append({"step": nm, "LTV/CAC 5y": round(x5, 3), "change 5y": "" if prev is None else round(x5 - prev[0], 3),
                 "LTV/CAC 8y": v["LTV/CAC 96m"], "change 8y": "" if prev is None else round(v["LTV/CAC 96m"] - prev[1], 2),
                 "saver pays back in month": v["pays back in month"]})
    prev = (x5, v["LTV/CAC 96m"])
op.OV.clear()
op.SERVE_CONTINGENCY = True
with (op.TAB / "ltv_bridge.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)

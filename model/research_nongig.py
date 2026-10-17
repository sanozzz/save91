from update_inputs import vng
R = "benchmark proxies"
UPDATES = {"inputs.csv": {
    "ret_m1": vng(0.70, 0.80, 0.88, f"{R}: daily micro-SIPs and shop survival outlast gig tenure", "NG-033, NG-034, NG-039, NG-040"),
    "ret_m3": vng(0.48, 0.62, 0.75, R, "NG-033, NG-034"),
    "ret_m6": vng(0.33, 0.50, 0.64, f"{R}: about 64% of SBI daily Rs 250 SIPs still alive at ~6 months (derived)", "NG-033"),
    "ret_m12": vng(0.20, 0.35, 0.45, f"{R}: Choti SIP attrition about 55% a year (derived); bear = gig base", "NG-034"),
    "ret_m24": vng(0.10, 0.22, 0.32, R, "NG-034, NG-039"),
    "churn_late": vng(0.02, 0.015, 0.01, "assumption", ""),
    "daily_amount": vng(30, 60, 100, "benchmark: shopkeepers save more; the mix includes low earners",
                        "NG-006, NG-031, NG-040, NG-041, NG-026, NG-045"),
    "debits_success": vng(16, 22, 25, "assumption: daily cash flow bounces fewer debits", "NG-041"),
    "loan_dpd90": vng(0.10, 0.07, 0.05, "benchmark (claim 2 still applies): the self-employed are riskier borrowers than gig",
                      "NG-015, NG-013, NG-020, NG-019"),
    "loan_approval": vng(0.35, 0.55, 0.70, "assumption: more new-to-credit, no payslip or platform data", "NG-042"),
}}

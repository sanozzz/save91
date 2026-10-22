from update_inputs import vng
R = "benchmark proxies + judgement (no shopkeeper-specific data)"
UPDATES = {"inputs.csv": {
    "ret_m1": vng(0.70, 0.72, 0.80, R, "NG-033, NG-034"),
    "ret_m3": vng(0.48, 0.53, 0.65, R, "NG-033, NG-034"),
    "ret_m6": vng(0.33, 0.40, 0.53, R + "; SBI daily Rs 250 SIP lost 35.6% of FY26 registrations within the year", "NG-033"),
    "ret_m12": vng(0.20, 0.25, 0.40, R + "; bear = gig base", "NG-033, NG-034"),
    "ret_m24": vng(0.10, 0.15, 0.25, R, "NG-034, NG-039"),
    "daily_amount": vng(30, 50, 100, "benchmark: self-employed average income Rs 23k urban (vs gig net Rs 18.8k); vendors save more (Kenya RCT); mix includes low earners",
                        "NG-005, NG-040, NG-031, NG-041, NG-026, NG-045"),
    "loan_dpd90": vng(0.12, 0.07, 0.05, "benchmark (claim 2 applies): self-employed small unsecured loans peak 10.2% at 90+; PM SVANidhi NPA 12-16%",
                      "NG-015, NG-013, NG-020"),
    "cac_mult": vng(3.0, 1.5, 1.0, "assumption, UNVERIFIED: no merchant CAC published; Paytm device merchants cost up to ~Rs 5,000 each (with hardware)",
                    "NG-043, NG-028"),
}}

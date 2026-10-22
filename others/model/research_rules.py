from update_inputs import v
UPDATES = {"inputs.csv": {
    "cost_debit": v(5.0, 2.0, 0.5, "benchmark: payment-company list price (bear); base is an assumed negotiated rate", "REG-050", "2026-09-30",
                    "Cashfree list: Rs 5 per UPI Autopay debit under Rs 1,000 and Rs 7.5 per mandate, paid by the merchant, never the customer [REG-049]. UPI Autopay carries no MDR [REG-052]. Who pays when an AMC collects directly is UNVERIFIED."),
    "cost_notice": v(0.20, 0.136, 0.10, "benchmark (vendor rate cards, unverified)", "REG-072, REG-073", "2026-09-30",
                     "WhatsApp utility message Rs 0.115 + 18% GST; transactional SMS Rs 0.10-0.20. A notice is required 24h before every debit [REG-049]."),
    "cost_failed": v(1.0, 0.25, 0.0, "assumption; no published failed-debit fee", "REG-050", "2026-09-30",
                     "Razorpay: no per-retry charge within limits. Morning debits failed in 2026 when banks ran them in the 10:00-13:00 window [REG-047]."),
    "mf_incentive": v(0, 0, 0, "regulation: SEBI Choti SIP (not available to this design)", "REG-032, REG-033", "2025-08-11",
                      "Rs 500 per new-to-MF investor, paid after 24 months, monthly Rs 250 equity SIP only. Forfeited if the investor holds ANY other SIP or lumpsum, and our liquid-fund saving comes first. So Rs 0 here."),
    "dlg_cap": v(0.05, 0.05, 0.05, "regulation", "REG-003, REG-008", "2025-05-08",
                 "RBI (Digital Lending) Directions 2025: a loan service provider's default-loss guarantee is capped at 5% of the portfolio. Not allowed on cards or revolving credit [REG-007]."),
    "debits_success": v(15, 20, 24, "assumption", "REG-047", "2026-09-30",
                        "Daily plan. Debits may run only outside peak hours; one attempt plus three retries."),
}}

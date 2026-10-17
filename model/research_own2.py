from update_inputs import v
UPDATES = {"inputs.csv": {
    "trail_equity": v(0.005, 0.0075, 0.010, "benchmark: regular minus direct TER gap", "OWN-04", "2026", "Equity funds 0.5-1.0% a year; an upper bound on trail actually paid"),
    "card_ic_share": v(0.0, 0.0, 0.0025, "assumption", "REG-087", "2022-04-21",
                       "A sourcing partner gets no card-transaction data and usually no ongoing share. Bull assumes a co-brand deal that shares 0.25% of spend."),
}}

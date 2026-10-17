from update_inputs import v
UPDATES = {"inputs.csv": {
    "gold_margin": v(0.01, 0.02, 0.024, "benchmark, UNVERIFIED (distributor commission)", "LEV-036, LEV-035, LEV-037", "2026",
                     "Jar earned about 2.4% commission per purchase as a distributor (case study). SafeGold's own margin is about 0.44% of turnover. "
                     "Savers pay a 2-3% spread + 3% GST, so a round trip inside a year LOSES them money."),
    "gold_on": v(0, 0, 0, "lever switch", "REG-022, REG-023, REG-024, LEV-041, LEV-043", "2026-09-30",
                 "Gold takes Rs 10 saves [LEV-039] and rewards on it are not prohibited (unverified) [LEV-043]. Unregulated; framework under consultation; cannot back a loan."),
}}

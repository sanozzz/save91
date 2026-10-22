from update_inputs import v
UPDATES = {"inputs.csv": {
    "dlg_fee_uplift": v(0.01, 0.02, 0.025, "benchmark, UNVERIFIED: LSP take rate with a guarantee vs plain sourcing", "LEV-008, LEV-009, LEV-007", "2026-09",
                        "Moneyview take rate on partner loans 2.5-4.5% (blog on its RHP, unverified) vs DSA 1-3%. RBI sets no fee formula; the fee is bilateral."),
    "dlg_cap": v(0.05, 0.05, 0.05, "regulation + practice", "REG-003, LEV-002", "2026-09",
                 "Cap 5% of the amount disbursed. Moneyview posts 4.5-4.8% of guaranteed disbursals as lien-marked deposits."),
    "nbfc_apr": v(0.24, 0.28, 0.32, "benchmark", "LEV-012, LEV-013", "2026-09",
                  "Moneyview on-book yield 25-28%; Kissht average 30%; KreditBee 12-28.5% + fee. RBI draft wants APR ceilings on loans up to Rs 50k [REG-078]."),
    "nbfc_proc_fee": v(0.02, 0.025, 0.035, "benchmark", "LEV-011, LEV-013", "2026", "Moneyview from 2%; KreditBee up to 5.5%"),
    "nbfc_cof": v(0.16, 0.145, 0.13, "benchmark", "LEV-014, LEV-015, LEV-025", "2026",
                  "A- rated digital lenders pay 13.3-14.4%; BBB Stashfin NCDs 11.9-14.5%. A new, unrated NBFC pays more."),
    "nbfc_equity": v(0.50, 0.40, 0.30, "benchmark", "LEV-023, LEV-024, LEV-029", "2026",
                     "Digital unsecured lenders run 1-2x debt/equity, not the 5-6x a 15% CRAR allows. Groww Creditserv: Rs 678 cr equity for Rs 1,396 cr AUM."),
    "nbfc_collect": v(250, 150, 100, "founder data + benchmark", "LEV-018, LEV-019", "2026",
                      "Bueno Rs 100-300 per loan. Digital-lender opex 9.6-16% of managed assets includes sourcing, which a captive book avoids."),
}}

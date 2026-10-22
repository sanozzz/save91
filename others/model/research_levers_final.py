from update_inputs import v
UPDATES = {"inputs.csv": {
    "lsp_fee": v(0.01, 0.015, 0.03, "benchmark (origination only, no servicing)", "LEV-009, LEV-065, BM-07", "2026",
                 "DSAs get 1-3% from NBFCs, 0.5-1.5% from banks; Paisabazaar's revenue/disbursal is at most 4.7% incl. cards. The lender pays; never the borrower [REG-011]."),
    "dlg_fee_uplift": v(0.03, 0.055, 0.07, "benchmark (derived from filings) + judgment", "LEV-059, LEV-064, LEV-008", "2026-09",
                        "Total fee with a 5% guarantee + servicing: 4 / 7 / 10% of disbursal, minus the no-guarantee fee. Moneyview partner fees about 11% of partner disbursal (derived); Kissht 17.4% of off-book AUM a year. No source splits guarantee vs no-guarantee fees."),
    "service_cost": v(350, 250, 150, "founder data + benchmark", "LEV-018, LEV-019", "2026",
                      "Collection and servicing per loan when WE service it (under the guarantee or our own NBFC). Bueno: Rs 100-300 per loan in collections."),
    "nbfc_apr": v(0.25, 0.28, 0.30, "benchmark", "LEV-062, LEV-064, LEV-011, LEV-013", "2026", "Yield on loans at Moneyview 27.6%, Kissht 30.7%"),
    "nbfc_proc_fee": v(0.02, 0.03, 0.04, "benchmark", "LEV-011, LEV-013", "2026", "Moneyview from 2%; KreditBee up to 5.5%"),
    "nbfc_cof": v(0.16, 0.14, 0.12, "benchmark", "LEV-015, LEV-028, LEV-062", "2026",
                  "Moneyview's NBFC 14.44-14.74%, Kissht 13.3-13.7%, Amica (parent-subsidised) 11.5-12.5%"),
    "nbfc_equity": v(0.50, 0.33, 0.25, "benchmark", "LEV-023, LEV-024, LEV-063", "2026",
                     "Peers run 1-3x debt/equity (equity = 1/(1+D/E)); the 15% CRAR floor does not bind (peers hold 24-48%)"),
    "gold_margin": v(0.01, 0.015, 0.024, "benchmark, UNVERIFIED (distributor commission)", "LEV-036, LEV-071, LEV-035, LEV-037", "2026",
                     "Only published figure: Jar about 2.4% as a distributor (case study). Augmont confirms a per-transaction commission, rate undisclosed. Savers pay a 2-3% spread + 3% GST: a round trip inside a year loses them money."),
}}

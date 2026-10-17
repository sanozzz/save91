"""Evidence for the QR-moat test (operator, 12 Oct 2026: "the entire idea is dependent on the premise
that QR code strategy is not defensible"). Freezes every figure the PDF quotes into
research/qr_moat.csv, one row per number, with its source and how far it was checked:

  primary         opened on the company's or regulator's own document
  news            opened on a news report of company or regulator data
  search summary  seen only in a search engine's summary; the page itself was not opened
  earlier         carried over from an earlier research table (its id is in `note`)
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "research" / "qr_moat.csv"
COLS = ["id", "key", "value", "value_high", "unit", "claim", "scope", "date", "source", "url", "status", "note"]

ROWS = [
    # 1. the QR code itself
    ("QM-01", "qr_codes_cr", 56.86, "", "crore QR codes", "UPI QR codes deployed", "All India, FY 2024-25", "2025-03-31",
     "PIB (Ministry of Finance)", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2200569", "earlier", "NG-027"),
    ("QM-02", "upi_merchants_cr", 6.5, "", "crore merchants", "merchants those QR codes were deployed to", "All India, FY 2024-25", "2025-03-31",
     "PIB (Ministry of Finance)", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2200569", "earlier", "NG-027; gross, not active"),
    ("QM-03", "bharatpe_start_year", 2018, "", "year", "BharatPe launched the first interoperable UPI QR (any app can pay it) and promised zero fees to shops",
     "BharatPe", "2018", "YourStory; BharatPe company history", "https://yourstory.com/2020/10/product-roadmap-bharatpe-tech-50-million-sme/amp", "search summary", ""),
    ("QM-04", "bharatpe_merchants_cr", 1.3, 1.7, "crore registered merchants", "BharatPe registered merchants, built from zero since 2018",
     "BharatPe", "2025", "BharatPe (1.3 crore, 450+ cities); AngelOne on FY25 results (1.7 crore+)", "https://www.angelone.in/news/startups/bharatpe-fy25-financials-1-667-crore-revenue-loss-drops-82-to-88-crore", "search summary", "sources differ; NG-043 carries the 1.7 crore figure"),
    ("QM-05", "mdr_pct", 0.4, "", "% of payment", "From 15 Oct 2026 shops pay 0.4% on UPI payments above Rs 2,000 (cap Rs 300); payments up to Rs 2,000 stay free; small shops taking up to Rs 1 lakh a month are exempt",
     "UPI P2M payments", "2026-10-15", "Department of Financial Services FAQ (15 Sep 2026); Business Today", "https://www.businesstoday.in/personal-finance/story/upi-mdr-of-0-4-on-transactions-above-rs2000-from-october-15-what-you-need-to-know-555709-2026-09-15", "earlier", "REG-052"),
    # 2. the soundbox and the field force
    ("QM-06", "paytm_devices_dec23_cr", 1.06, "", "crore device merchants", "Paytm merchants paying a monthly device subscription, Dec 2023 (before the RBI action)",
     "Paytm", "2023-12-31", "Inc42 on Paytm Q4 FY24 results", "https://inc42.com/?p=458350", "news", ""),
    ("QM-07", "paytm_devices_mar24_cr", 1.07, "", "crore device merchants", "the same, Mar 2024 (after the RBI action); only 1 lakh added in the quarter, with higher attrition in Feb-Mar",
     "Paytm", "2024-03-31", "Inc42 on Paytm Q4 FY24 results; Business Standard", "https://inc42.com/?p=458350", "news", ""),
    ("QM-08", "paytm_devices_mar26_cr", 1.51, "", "crore device merchants", "the same, Mar 2026",
     "Paytm", "2026-03-31", "Paytm Earnings Release Q4 FY2026", "https://paytm.com/document/ir/financial-results/fy2025-26/Paytm_Earning-Release_Q4-FY2026-FY-2026.pdf", "earlier", "XB-06"),
    ("QM-09", "paytm_devices_jun26_cr", 1.57, "", "crore device merchants", "the same, Jun 2026: +27 lakh in a year",
     "Paytm", "2026-06-30", "Paytm Earnings Release Q1 FY2027", "https://paytm.com/document/ir/financial-results/fy2026-27/Paytm_Earning-Release_Q1-FY-2027_INR.pdf", "earlier", "NG-028"),
    ("QM-10", "device_rent_rs", 49, 125, "Rs a month", "Soundbox rent: PhonePe Rs 49, Paytm Rs 125 a month; some Paytm shops moved to PhonePe for the cheaper box, and some return the box once rent starts",
     "Paytm, PhonePe soundboxes", "2023-09", "YourStory: fintech startups in the race for soundbox domination", "https://yourstory.com/2023/09/fintech-startups-soundbox-payments-paytm-pine-labs-phonepe-card", "search summary", "Paytm's own revenue per device was Rs 90 a month in Q4 FY24 (Inc42)"),
    ("QM-11", "phonepe_speakers_lakh", 91.9, "", "lakh devices", "PhonePe SmartSpeakers installed",
     "PhonePe", "2025-09-30", "PhonePe DRHP via The Hans India", "https://www.thehansindia.com/amp/business/phonepes-merchant-network-hits-47-million-businesses-drhp-reveals-diversified-monetisation-1054264", "earlier", "NG-029"),
    ("QM-12", "phonepe_field_staff", 25657, 31000, "people", "PhonePe field staff (25,657) plus commissioned agents (31,000+)",
     "PhonePe", "2025-09-30", "PhonePe DRHP via The Hans India", "https://www.thehansindia.com/amp/business/phonepes-merchant-network-hits-47-million-businesses-drhp-reveals-diversified-monetisation-1054264", "earlier", "NG-029"),
    ("QM-13", "paytm_cost_per_device_rs", 5000, "", "Rs per device added", "Paytm sales and service staff cost per net device added (an upper bound; derived)",
     "Paytm", "2026-06-30", "derived from Paytm Q1 FY27 release", "https://paytm.com/document/ir/financial-results/fy2026-27/Paytm_Earning-Release_Q1-FY-2027_INR.pdf", "earlier", "NG-043; derived"),
    ("QM-14", "npci_unified_soundbox", "", "", "", "NPCI is reported to be building one soundbox service that announces payments from ANY QR code",
     "NPCI", "2024", "Inc42 (citing sources; NPCI did not comment)", "https://inc42.com/buzz/npci-to-roll-out-unified-soundbox-infrastructure-for-merchants-report/", "news", "unconfirmed report"),
    # 3. the 2024 shock to Paytm
    ("QM-15", "paytm_upi_share_dec23", 13.09, "", "% of UPI payments", "share of UPI payments made through the Paytm app, Dec 2023",
     "Paytm (payer app)", "2023-12-31", "Business Standard, NPCI data", "https://www.business-standard.com/companies/news/paytm-s-upi-market-share-continues-to-slide-down-after-rbi-crackdown-124060600688_1.html", "search summary", "this is the CUSTOMER side (which app people pay with), not the shop side"),
    ("QM-16", "paytm_upi_share_dec24", 6.88, "", "% of UPI payments", "the same, Dec 2024 (PhonePe 47.72%, Google Pay 36.7%)",
     "Paytm (payer app)", "2024-12-31", "Business Standard, NPCI data", "https://www.business-standard.com/amp/companies/news/navi-crosses-1-market-share-in-upi-transactions-in-december-2024-125010801052_1.html", "search summary", ""),
    ("QM-17", "paytm_merchant_loans_q3fy24_cr", 3579, "", "Rs crore a quarter", "Paytm merchant loans given out, Oct-Dec 2023",
     "Paytm", "2023-12-31", "Inc42 on Paytm Q4 FY24 results", "https://inc42.com/?p=458350", "news", ""),
    ("QM-18", "paytm_merchant_loans_q4fy24_cr", 1671, "", "Rs crore a quarter", "the same, Jan-Mar 2024, after lenders pulled back (Piramal and Clix ended ties)",
     "Paytm", "2024-03-31", "Inc42 on Paytm Q4 FY24 results", "https://inc42.com/?p=458350", "news", ""),
    # 4. seeing the till and taking repayment from it
    ("QM-19", "phonepe_edi", "", "", "", "PhonePe merchant loans are repaid by a small amount taken from the shop's DAILY SETTLEMENT; a missed amount is added to the next day's; long misses are taken from the linked bank account",
     "PhonePe merchant loans", "2026", "PhonePe merchant help: How can a merchant repay a loan?", "https://cms.phonepe.com/en/ace/loans/repaying-loan/how-can-merchant-repay-loan", "search summary", "PhonePe's own help page; the page itself returned an error when opened"),
    ("QM-20", "paytm_daily_emi", "", "", "", "Paytm merchant loans: a daily EMI collected mostly from the merchant's daily settlement with Paytm",
     "Paytm merchant loans", "2020-2025", "YourStory (2020); loan-comparison sites", "https://yourstory.com/smbstory/paytm-collateral-free-msme-loans", "search summary", ""),
    ("QM-21", "phonepe_eligibility_rs", 15000, "", "Rs a month on PhonePe QR", "to get a PhonePe merchant loan a shop must take more than Rs 15,000 a month on PhonePe QR, for 3 months or more",
     "PhonePe merchant loans", "2026", "search summary of a loan-information site", "", "search summary", "not checked on a PhonePe page"),
    ("QM-22", "paytm_ecl_low", 4.5, 5.0, "% expected credit loss", "expected losses on Paytm-sourced merchant loans (lenders' books; Paytm collects)",
     "Paytm merchant loans", "2026-03-31", "Paytm Earnings Release Q4 FY2026", "https://paytm.com/document/ir/financial-results/fy2025-26/Paytm_Earning-Release_Q4-FY2026-FY-2026.pdf", "earlier", "XB-07"),
    ("QM-23", "paytm_repeat_pct", 50, "", "% of disbursals", "more than half of Paytm merchant-loan money goes to repeat borrowers",
     "Paytm merchant loans", "2026-06-30", "Paytm Earnings Release Q1 FY2027", "https://paytm.com/document/ir/financial-results/fy2026-27/Paytm_Earning-Release_Q1-FY-2027_INR.pdf", "earlier", "NG-028"),
    ("QM-24", "aa_lending_lakh_cr", 3.82, "", "Rs lakh crore", "lending done using Account Aggregator data in FY26 (3.68 crore loans): any regulated lender can read a customer's bank statements with consent",
     "India, FY26", "2026-03-31", "Sahamati data via Finahub (Aug 2026)", "https://blog.finahub.com/2026/08/account-aggregator-framework-consent-based-data-lending.html", "search summary", ""),
    ("QM-25", "aa_share_value_pct", 8.4, 11.8, "% of retail + MSME lending", "Account Aggregator share of retail and MSME lending in FY26: 8.4% by value, 11.8% by number",
     "India, FY26", "2026-03-31", "Sahamati data via Finahub (Aug 2026)", "https://blog.finahub.com/2026/08/account-aggregator-framework-consent-based-data-lending.html", "search summary", ""),
    ("QM-26", "autopay_fail_pct", 55, 90, "% of Autopay debits", "share of UPI Autopay debits that did not go through, by bank, Aug 2025 (mostly not enough money in the account)",
     "all UPI Autopay, major Indian banks", "2025-08", "Mint (HT Syndication), NPCI data", "https://www.htsyndication.com/mint/article/upi-autopay-s-recurring-woes-are-forcing-an-industry-rethink/93925664", "earlier", "TB-13"),
    ("QM-40", "digital_lender_losses_pct", 7, 10, "% a year", "losses at digital lenders that do NOT hold the borrower's till: KreditBee 7.7%, Kissht 8.5-9%, Groww 7%, Stashfin 9.9%",
     "Indian digital lenders, FY25-FY26", "2026", "CRISIL, CARE and ICRA rating notes", "https://www.careratings.com/upload/CompanyFiles/PR/202603120334_KrazyBee_Services_Limited.pdf", "earlier", "LEV-021, LEV-022, LEV-026, LEV-029"),
    # 5. lending already at scale
    ("QM-27", "phonepe_ml_fy23_cr", 11, "", "Rs crore", "PhonePe merchant loans given out, FY23", "PhonePe", "2023-03-31",
     "PhonePe DRHP via Business Today", "https://www.businesstoday.in/personal-finance/news/story/phonepe-sharpens-focus-on-merchant-lending-consumer-loans-ahead-of-ipo-push-519975-2026-03-10", "earlier", "XL-10"),
    ("QM-28", "phonepe_ml_fy24_cr", 1718, "", "Rs crore", "the same, FY24", "PhonePe", "2024-03-31",
     "PhonePe DRHP via Business Today", "https://www.businesstoday.in/personal-finance/news/story/phonepe-sharpens-focus-on-merchant-lending-consumer-loans-ahead-of-ipo-push-519975-2026-03-10", "earlier", "XL-10"),
    ("QM-29", "phonepe_ml_fy25_cr", 4507, "", "Rs crore", "the same, FY25", "PhonePe", "2025-03-31",
     "PhonePe DRHP via Business Today", "https://www.businesstoday.in/personal-finance/news/story/phonepe-sharpens-focus-on-merchant-lending-consumer-loans-ahead-of-ipo-push-519975-2026-03-10", "earlier", "XL-10"),
    ("QM-30", "phonepe_ml_h1fy26_cr", 3820, 1838, "Rs crore a half-year", "the same, Apr-Sep 2025 (Apr-Sep 2024: 1,838)", "PhonePe", "2025-09-30",
     "PhonePe DRHP via Business Today", "https://www.businesstoday.in/personal-finance/news/story/phonepe-sharpens-focus-on-merchant-lending-consumer-loans-ahead-of-ipo-push-519975-2026-03-10", "search summary", "H1 FY25 figure from the same report"),
    ("QM-31", "bharatpe_lending_share_pct", 60, "", "% of revenue", "BharatPe FY25: revenue Rs 1,667 crore; Rs 6 crore profit before tax EXCLUDING employee-stock costs (net loss Rs 88 crore); 60% of revenue from financial services, mostly shop loans; average loan Rs 1 lakh over 11 months; own lending company Trillion Loans makes 25-30% of its loans",
     "BharatPe", "2025-08-11", "Inc42: BharatPe's merchant-first playbook brings FY25 turnaround", "https://inc42.com/features/bharatpe-merchant-first-playbook-brings-fy25-turnaround-but-whats-next/", "news", ""),
    ("QM-32", "no_own_lending", "", "", "", "Paytm will NOT apply for a lending licence (May 2026); PhonePe has applied three times since 2021 with no approval reported: both pass loans to partner lenders",
     "Paytm, PhonePe", "2026-05-08", "Medianama; Business Standard", "https://www.medianama.com/2026/05/223-paytm-not-applying-for-nbfc-licence-rbi-crackdown/", "earlier", "LEV-070"),
    # 6. the savings hook
    ("QM-33", "phonepe_daily_rd_min_rs", 100, 1000, "Rs a day", "PhonePe Daily Recurring Deposit, Rs 100-1,000 a day, withdraw after 7 days, with Shivalik Small Finance Bank; launched 6 Aug 2026 for consumers",
     "PhonePe", "2026-08-06", "PhonePe press release", "https://www.phonepe.com/press/phonepe-launches-fixed-deposit-distribution-in-partnership-with-leading-banks-nbfcs/", "primary", ""),
    ("QM-34", "phonepe_daily_gold", 10, 5000, "Rs a day", "PhonePe Daily Savings in digital gold, Rs 10-5,000 a day, built with Jar (Oct 2024)",
     "PhonePe", "2024-09-30", "PhonePe press release", "https://www.phonepe.com/press/phonepe-partners-with-jar-to-launch-daily-savings-in-digital-gold/", "earlier", "TF-21"),
    ("QM-35", "bharatpe_invest_platform_lakh", 80, "", "lakh merchants", "BharatPe Investment Platform lets regulated firms sell deposits and investments to its 80 lakh+ merchants",
     "BharatPe", "2022", "IBS Intelligence", "https://ibsintelligence.com/ibsi-news/bharatpe-introduces-new-investment-platform-for-merchants", "search summary", ""),
    # 7. the closest precedent: win shops with a non-payment hook, then lend
    ("QM-36", "khatabook_rev_fy24_cr", 102.7, 116.24, "Rs crore (revenue; loss)", "Khatabook FY24: revenue Rs 102.7 crore, loss Rs 116.2 crore",
     "Khatabook", "2024-03-31", "YourStory (Nov 2024)", "https://yourstory.com/2024/11/ms-dhoni-backed-khatabook-clocks-rs-1027-cr-revenue-cuts-losses-7-in-fy24", "search summary", ""),
    ("QM-37", "khatabook_lending", "", "", "", "Khatabook 'can't lend enough to justify its valuation': small loans, unreliable data and a mostly digital presence held back lending to the shops its free ledger had won",
     "Khatabook", "2023-05-01", "The Morning Context", "https://themorningcontext.com/internet/khatabook-cant-lend-enough-to-justify-its-valuation", "news", ""),
    ("QM-38", "gpay_merchant_credit", 15000, "", "Rs smallest loan", "Google Pay also lends to shops through partners: sachet loans from Rs 15,000 (DMI), credit lines (ePayLater, ICICI), repeat loans (Indifi)",
     "Google Pay", "2023-10-18", "TechCrunch", "https://techcrunch.com/2023/10/18/google-pay-deepens-consumer-and-merchant-lending-offerings-in-india", "search summary", ""),
    ("QM-39", "loan_rate_market", "", "", "", "Shop-loan prices quoted: Paytm APR 15-46% (loan-comparison site); PhonePe up to 30% flat a year (unverified)",
     "Paytm, PhonePe merchant loans", "2026", "Paisabazaar; loan-information sites", "https://paisabazaar.com/business-loan/paytm", "search summary", "low confidence; used only to say 26% is inside the market range"),
    # 8. Bachatt: the funded company that does not hold the till
    ("QM-41", "bachatt_users_m", 3, "", "million users", "Bachatt users acquired since the May 2025 launch (company claim). The homepage has also said 10 lakh+ users; the two figures are not reconciled",
     "Bachatt (Trusave Fintech)", "2026-03-30", "Bachatt press release, Series A", "https://bachatt.app/press-release", "earlier", "XB-03, BAC-02; company claim"),
    ("QM-42", "bachatt_mf_txns_m", 2, "", "million transactions", "mutual-fund transactions Bachatt executed in February 2026",
     "Bachatt", "2026-02", "Bachatt press release, Series A", "https://bachatt.app/press-release", "earlier", "XB-03; company claim"),
    ("QM-43", "debits_per_daily_saver", 20, "", "debits a month", "our assumption for the estimate: a person saving every day produces about 20 fund purchases a month",
     "our estimate, not a Bachatt figure", "2026-10-02", "note on XB-03", "https://bachatt.app/press-release", "earlier", "XB-03 note; assumption"),
    ("QM-44", "bachatt_loan_cap_rs", 500000, "", "Rs", "Bachatt offers loans up to Rs 5 lakh from partner banks and NBFCs and acts as a lending service provider: the partner books and holds the loan. No loan volume or default figure published",
     "Bachatt users", "2026", "Bachatt homepage; earlier rows XB-10 and XL-12", "https://bachatt.app/", "earlier", "company claim"),
    ("QM-45", "bachatt_raised_usd_m", 16, "", "USD million", "about $16 million raised: $4 million seed (Apr 2025) plus $12 million Series A led by Accel (Mar 2026). No retention figure published",
     "Bachatt", "2026-03-30", "Entrackr; Bachatt press release", "https://entrackr.com/news/wealthtech-startup-bachatt-raises-12-mn-in-series-a-led-by-accel-11438527", "earlier", "BAC-01; seed plus Series A"),
]


def main():
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in ROWS:
            assert len(r) == len(COLS), r[0]
            w.writerow(r)
    print(f"wrote {OUT} ({len(ROWS)} rows)")


if __name__ == "__main__":
    main()

# 24 Oct rebase: brief for every agent

> **UPDATE (later on 24 Oct): the numbers below are SUPERSEDED.** After the two reviews, serving carries the 10% contingency, and one retention line applies everywhere. Main case now **0.75× (5y) / 1.32× (8y), payback month 75**. The current numbers and every fix are in `FIXES.md`, section A. Always read numbers from the tables.

The founders questioned every LTV input on 24 Oct and replaced the hopeful ones with market or measured numbers. The model is already rebased: `others/model/online_plan.py` (docstring "REBASE 24 Oct") and `others/model/ltv_odds.py` (rewritten). The tables in `others/tables/` are already regenerated. **Your job is to make the documents and sheets tell this new story correctly.** The founders have a meeting tomorrow (25 Oct). Their question: "by just cross-selling, what are our 5-year and 8-year LTVs?"

## The decisions (founders, 24 Oct)

| Input | Was (23 Oct main case) | Now | Source |
|---|---|---|---|
| Personal/business loan | ₹1.7 lakh (drawn ₹50k–3L) | **₹70k first loan**; repeats 10% bigger a year repaid, plus top-ups (15% a year, 40% of the loan) | Bachatt's number. Our research had ₹15k / 25k / 58.5k. |
| Apply for a loan a year | 27% | **20%** (market) | |
| First loans approved | 25% | **20%** (market) | |
| Yearly rises in take-up and approval | 2.4% / 4.8% | **none** | |
| Home loan / LAP size | ₹20.6L / ₹14.6L | **₹12L / ₹5L** (market) | |
| Lender payout | 2% rising 24% by year 5 | **2% flat** (market middle of 1/2/3%) | research/xs_lending_summary.md |
| KYC'd non-savers | 1.72 reached per saver, kept as long as savers | **fade within ~3 months** → reach 1.06 (each is worth ~4% of a saver's loan fees: lenders rarely approve in a user's first months) | |
| Recharge, bills, FD, NPS | on | **off** (not in the launch app) | |
| Debit cost | ₹2, weekly | **₹0** through BSE StAR MF or the fund house's mandate. **Unconfirmed in writing.** XSIP is free to distributors (TC-42); fund houses pay BSE (TC-43). Daily minimum ~₹100 per scheme (TC-45), so the ₹80+₹20 split likely becomes one hybrid fund. | research/tri_costs.csv TC-42..47; outreach/2026-10-22_daily_sip_questions.md |
| Still saving at 12 months | 36% | **Bachatt's 30–40%**, drawn (drop-off after a year 2.5%→1.5% a month moves with it) | Bachatt; SBI's daily ₹250 SIP agrees (~38%) |
| Equity fund fee | 0.75% | 0.75% (active funds, **unconfirmed**) | |
| Daily amount | ₹100 | ₹100 = the product **minimum**, so cautious; Bachatt's average not yet known | |
| Cost to win | ₹450 + 10% = ₹495 (₹600 seed) | unchanged (measured) | |

## The numbers (read them from the tables, never retype)

- `tables/ltv_saver_split.csv`: **main case per online saver**. 5 years: fund fees ₹418, loans ₹125, cards ₹18, serving −₹173 → net ₹388 = **0.78×**. 8 years: fund fees ₹708, loans ₹156, cards ₹18, serving −₹205 → ₹677 = **1.37×**. **Cross-sell alone** (loans + cards) = **0.29× (5y), 0.35× (8y)**; cross-sell after serving is negative (−0.06×). Fund fees alone 0.84× / 1.43× (418.17 / 495 = 0.845).
- `tables/ltv_odds_summary.csv`, `ltv_odds_draws.csv`: the Monte Carlo (2 drawn inputs: retention, debt-fund fee). 5y P10/P50/P90 = 0.63 / 0.78 / 0.97; **4% of draws reach 1× at 5 years**. 8y = 1.03 / 1.37 / 1.81; **95% reach 1× by 8 years**. Saver pays back: month 62 / 73 / 93. Company (20,000 online savers a month from month 30): **EBITDA is not positive by month 96 in any draw**; money needed $8.8M / $9.3M / $9.8M, and the cash hole is still deepening at month 96, so that is a floor. Cumulative EBITDA to month 96 ≈ −₹80 Cr.
- `tables/ltv_odds_drivers.csv`: retention moves the median from 0.60× (30%) to 1.02× (40%); the debt-fund fee 0.75×–0.82×. The ladder's low and high ends now move retention ONLY (debt fee at the main case), so they read the same 0.60× / 1.02×.
- `tables/ltv_upside_levers.csv`: one lever at a time from the main case. **₹126 a day alone → 1×** (₹200 → 1.63×). **39.6% still saving alone → 1×** (45% → 1.30×; the drop-off after a year moves on the same line as Bachatt's range: 30% ↔ 2.5%, 40% ↔ 1.5%, 45% ↔ 1.0% a month). Apply 35% alone → 0.96× (needs 39% for 1×). Approval 30% alone 0.84×; rises alone 0.84×: **loans alone can't reach 1×**.
- `tables/ltv_ladder.csv` + `ltv_ladder_yearly.csv`: "what it takes". The five upside levers move together from the main case (u=0) to the upside (u=1): ₹100→₹200 a day, retention→45% (drop-off 1.0%), apply 20%→35%, approval 20%→30%, rises 0→5%/10%. Rungs: Low end (30%) 0.60×; **Main case 0.78×** (never profitable by m96, $9.3M+); 1× (₹113 a day, 36%, 22% apply, 21% approved; still not profitable by m96, $8.3M+); High end (40%) 1.02×; **2× (₹160 a day, 41%, 29% apply, 26% approved → EBITDA positive m68, $5.2M)**; **3× (₹193, 44%, 34%, 29% → m56, $4.1M, 8-year cumulative +₹31 Cr)**; All upside 3.25× (m54, $3.9M, +₹44 Cr). Read every value from the table.
- `tables/ltv_bridge.csv` (model/ltv_bridge.py): **1.75× → 0.78×**, one decision at a time: ₹70k loans −0.58; market apply/approval −0.35; home/LAP market −0.15; payout flat −0.02; non-savers fade −0.03; products off −0.13; debits ₹0 **+0.34**; Bachatt retention −0.03.
- `tables/ltv_main_levers.csv` (and online_levers.csv, same at 20k/month): one change at a time on the company. ₹200 a day → EBITDA m76, $5.9M; ₹300 → m61, $4.6M; loan funnel at our old targets → m85, $6.0M; credit-hungry → m86; **we pay ₹2 a weekly debit → $11.7M**; **equity fee 0.5% → $10.6M**; cost to win ₹600 → $12.0M.
- `tables/ltv_main_funnel.csv`: the loan funnel per 100 savers won.
- All `online_*.csv` tables are now the main case too (online_plan.py runs under use_main_case()).

## The story the documents must tell (plain English, one point a page)

1. **The answer first.** One online saver earns back 0.78× its ₹495 cost in 5 years and 1.37× in 8; it pays back in about month 73. Cross-selling alone (loans and cards) earns 0.29× in 5 years and 0.35× in 8, which doesn't even cover the cost of serving the saver. **At market numbers this is a fund-fee business; loans are a small add-on.**
2. **What changed and why** (the bridge): each founders' decision and what it cost. The ₹70k loan and market approval/apply rates did most of it. Moving debits to ₹0 through the exchange won back a third.
3. **What's still uncertain** is mostly how long savers keep saving (Bachatt 30–40%): 0.63–0.97× at 5 years, 1.03–1.81× at 8.
4. **What it takes:** a higher average daily amount (₹126 for 1×) or longer saving (about 40% for 1×). No single loan number gets there alone (all three loan numbers at our old targets together give 1.16× and profit from month 85 on $6.0M). 2× needs ₹160 a day, 41% still saving and loans most of the way to our old targets; 3× needs nearly every upside lever.
5. **The company at the main case doesn't turn profitable within 8 years.** Each saver costs more than it earns back within 5 years, so growing faster deepens the loss. 2× gives profit from month 68 on $5.2M.
6. **The four facts that decide it**, all cheap to get: Bachatt's **average** daily amount; Bachatt's exact 12-month retention; written ₹0 debit cost (BSE / fund houses; one hybrid fund at ₹100 a day); the 0.75% fee in writing.

## Rules (standing founder constraints)
- **PDF decks only.** No claude.ai artifacts. **Do not commit or push** (git or Google Sheets): the lead does that.
- **One case.** The main case is the only case. The ladder and levers are "what it takes", never alternative plans. Don't present "our targets / 7.7×" anywhere as a plan; old targets appear only as the upside end of the ladder, named "our old targets".
- LTV/CAC shows to **2 decimals** (0.78×, 1.37×). Undiscounted cumulative P&L, **never NPV**. ₹ Cr to 2 decimals below 10.
- **Gender-neutral** language (they/them, "the saver's"); no customer names or phone numbers; never name Bueno or BetterPlace; never frame Bachatt as the enemy (naming it as a benchmark source is fine); never write "nobody serves both"; **the app never holds money** (funds are bought in the saver's own name); no reuse of old borrower data (DPDP).
- Plain words: no "DSA", "clawback", "MDR", "TER" without saying what they mean. Write "refunds to lenders", "lender payout", "fund fee".
- Run Python with `~/.cortado-venv311/bin/python`, from `others/` with `PYTHONPATH=model:ltv:online:seed`. PDFs print with Chrome headless (see each builder). Keep shared modules importable at every step: `ltv/build_ltv_deck.py` imports `model/ltv_book.py`; `ltv/odds_pages.py` and `online/build_online_case.py` import both; `online/build_online_v4.py` imports `online/build_online_case.py`, `ltv/odds_pages.py` and `seed/build_seed_plan.py`. **Don't change another agent's files.** If you need a change in one, write a local helper in your own file instead.
- **Look at every page you build.** Render the PDF to PNGs (e.g. `pdftoppm -r 50 -png`) and open them with the Read tool. Check for overflow, clipped text, empty charts and stale numbers ("1.75×", "7.7×", "₹3 lakh", "₹1.7 lakh", "35% apply", "2.5 KYC'd", "month 63", "$4.7M", "₹2 a debit" as base).
- Finish with a short report: files changed, the PDFs and pages built, checks run, and anything you couldn't resolve.

## File ownership
| Agent | Owns | Produces |
|---|---|---|
| Decks | `ltv/odds_pages.py`, `ltv/build_ltv_simple.py`, `online/build_online_case.py`, `ltv/build_ltv_deck.py` | `ltv/LTV_CAC_simple.pdf` (final/3), `online/Online_business_case.pdf` (final/1) |
| v4 deck (after Decks) | `online/build_online_v4.py` | `online/Online_model_v4.pdf` (final/2) |
| Save4More sheet | `model/v4_toy_check.py`, `model/v4_gsheet.py`, `model/v4_ltv_tab.py`, `model/v4_push_blocks.py`, `tables/v4_start_here.json` | spec + checks + push blocks (no push) |
| LTV workbook | `model/ltv_book.py` | checks + push payloads (no push) |
| Seed plan | `seed/build_seed_plan.py` | `seed/Seed_Plan_investor.pdf` (final/4) |

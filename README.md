# save91: daily savings in mutual funds, online-first, with a loan marketplace

**Start with [`final/`](final/README.md).** It holds the current documents (the online business case, the full online plan, the
LTV/CAC deck, the $0.5M seed plan, the Bachatt memo), links to the two live Google Sheets, the headline numbers read from the
model, and the open items. `python final/make_final.py --check` says whether it is up to date.

---

**Everything below describes the earlier offline street-agent plan (16–18 Oct), kept for history.** [`START_HERE.md`](START_HERE.md) describes:
- what we are building and the current base plan;
- the year-by-year financials;
- every decision taken so far;
- which files are current and which are history;
- how to re-run the models.

## Quick map

| What | Where |
|---|---|
| The deck (current) | `Offline_model_v3.pdf` |
| Agreed assumptions (every input as a distribution) | `Assumptions_agreed.pdf`, `tables/dist_agreed_v1.csv` |
| One-agent cohort model + Monte Carlo | `model/cohort_engine.py`, `model/cohort_mc.py` |
| Company model, city limits, NBFC, funding rounds | `model/company_model.py`, `model/saturation.py`, `model/nbfc.py`, `model/share_compare.py`, `model/base_plan.py` |
| Current base plan outputs | `tables/base_*.csv` |
| Evidence (one row per source, with IDs) | `research/` |
| Operator decisions, round by round | `story/` |

A toy version of the model with live formulas lives in a separate Google Sheet ("Save4More").

**Not in the repo:** the Python environment and the raw Monte Carlo draws, both large. Re-create the draws with `python model/cohort_mc.py`.

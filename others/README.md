# others: everything behind `final/`

The current documents are in [`../final/`](../final/README.md). This folder holds what builds them and what came before. Paths in the
code and in the decks' footnotes (`model/...`, `tables/...`) are relative to this folder; run scripts from here.

| Folder | What is in it |
|---|---|
| `model/` | The Python models. **Current:** `online_plan.py` (the plan and the company; `use_main_case()` switches every input to the main case, which the v4 deck and both sheets use), `ltv_odds.py` (the LTV/CAC Monte Carlo with the cost to win fixed, and the ladder; its median is the business case's main case), `online_mc.py` (the earlier, plan-centred Monte Carlo; superseded by `ltv_odds.py`, kept for history), `ltv_book.py` (the LTV/CAC workbook on the main case and its checks; `base_params()` still gives our targets for the LTV decks), `seed_plan.py` (the $0.5M seed), `v4_gsheet.py`, `v4_toy_check.py`, `v4_ltv_tab.py` (the Save4More sheet and its formula check), and `cohort_engine.py`, the per-saver engine they all use. The other scripts are from the offline plan, kept for history and not maintained. |
| `tables/` | Model inputs and outputs (CSV). **Current outputs** start with `online_`, `ltv_` (`ltv_odds_*` and `ltv_ladder*` from `ltv_odds.py`), `seed_` and `v4_`; the agreed input distributions are `dist_agreed_v1.csv`; the input audit is `online_inputs_audit.csv`. The rest are offline-plan outputs. |
| `research/` | The evidence: one row per source, with the IDs the decks cite (XF-, XL-, PR-, …). |
| `online/`, `ltv/`, `seed/`, `memo/` | The deck builders. Each writes the PDF that `final/` copies: `online/` the business case and the full plan, `ltv/` the LTV/CAC decks (the ten-page one in `final/`, `build_ltv_simple.py`; the detailed 32-page one, `build_ltv_deck.py`) and the Monte Carlo pages both the ten-page deck and the business case use (`odds_pages.py`), `seed/` the seed plan, `memo/` the Bachatt memo (earlier drafts in `memo/old_versions/`). |
| `reviews/` | The four-angle critical review of 21–22 Oct (`2026-10-21/`), the earlier investment review, and the status of each of its points in the current plan. |
| `outreach/` | Questions to partners: BSE StAR MF and the fund houses on a daily SIP. |
| `archive/` | The offline street-agent plan of 16–18 Oct, superseded. See [`archive/README.md`](archive/README.md). |

To rebuild after changing an input (from this folder):

```
cd model && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python ltv_odds.py && PYTHONPATH=. python online_mc.py && PYTHONPATH=. python ltv_book.py <payload_dir>
cd .. && for b in ltv/build_ltv_deck.py ltv/build_ltv_simple.py online/build_online_v4.py online/build_online_case.py seed/build_seed_plan.py; do PYTHONPATH=model python $b; done
cd .. && python final/make_final.py
```

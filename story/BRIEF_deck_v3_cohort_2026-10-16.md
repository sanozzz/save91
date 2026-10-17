# Brief: deck v3, the simple picture-first story on the cohort Monte Carlo

## Inputs

- **The story:** `story/STORYLINE_v3_2026-10-16.md`, three parts:
  1. the problem with online;
  2. our offline approach (fleet on the street plus app; the 7% debt-fund hook; the marketplace from day one at no cost to us; the agent helps collect);
  3. what our analysis says, ending on the pilot.
- **The style and hard word budget:** `story/BRIEF_final_v3_visual_2026-10-16.md` §A.
  - Story pages: at most 70 words including sources; title at most 12 words; one takeaway line at most 14 words; one big picture a page.
  - Appendix pages: at most 150 words (the assumptions grid is exempt).
  - Enforce it with `check_words()` (pypdfium2, using the system `python3` with `$S/lib`). The build fails if any page breaks the budget.
  - **Reference look:** `QR_moat_story.pdf` (`model/build_qr_visual.py` helpers: V.text, icon, badge, arrow, node, svg, CSS, colours, CHROME).
- **The numbers:** ONLY from the cohort model's tables on the agreed distributions. Use the latest run's `tables/cohort_*` files; where the builder wrote `_v2` versions, use those.
  - Online figures: `tables/story_unit.csv` (₹499, 24 of 100, ₹2,067).
  - Never use the `xs_*_v2` tables, except for the online comparison if needed.
- **Assumptions for the appendix:** `tables/dist_agreed_v1.csv`. You may reuse pages 2–6 of `Assumptions_agreed.pdf` by rebuilding them with `model/dist_proposal.py`'s functions (import, don't edit), or redraw them.

## The honest headline (from the adversarial review; do not inflate it)

Use this framing on the analysis pages and the final page. Fill in the final run's numbers:

> "On the inputs we agreed, one agent's 5-year NPV is positive in about X of 10 futures (median ₹Y). Over 3 years it is positive in about Z of 10; payback is around month M."

**What must be true** goes in a picture, not a paragraph. Show the three conditions the reviewer found:

1. Sign-ups of about 60 a month (a janta agent adds 6–10).
2. Lenders lending these savers the loan sizes we assume.
3. Running costs staying near ₹5 per saver a month.

For each, show the chance at the bad end, from the must-be-true tables. If a needed figure is not in a table, compute it with the engine in a script that writes a CSV. Never type a number by hand.

## Pages (about 13 story + appendix)

### Part 1: the problem with online

1. Online costs ₹499 to win a daily saver.
2. Only 24 in 100 still save a year later.
3. Each saver kept costs ₹2,067; the app never earns it back.

### Part 2: our approach

4. The hook: about 7% in a debt fund vs about 2.5% in a janta deposit (the PSB savings rate). Show "about ₹1,890 more a year for him", taken from `dist_derived_v1.csv` or computed.
5. A fleet on the street, plus an app in his hand: two halves joined at the shop.
6. A marketplace from day one, at no cost to us: loans, cards and 17 products. Lenders and insurers decide.
7. The agent knows him, so he helps collect: the overdue flow, with Paytm's losses as our worst case.

### Part 3: what our analysis says

8. We modelled every monthly cohort, 10,000 times. Picture: a cohort triangle feeding a fan of draws.
9. One agent pays back over 5 years in about X of 10 futures. Picture: a fan of cumulative discounted cash by month (p10–p90), with the 36- and 60-month marks.
10. Where the money comes from. Picture: a stacked area of revenue by line over 60 months, against the cost line.
11. The longer he saves and repays, the more we earn. Picture: small multiples by year 1–5 of approval, loan size, top-ups, take-up and sign-ups.
12. What must be true. Picture: a heatmap of P(NPV60 > 0) by r12 band × sign-ups band, plus the three conditions as tiles.
13. Our answer: pilot one salaried agent for 12 months. Picture: the gate timeline (go and stop numbers from the model), plus the pilot-year cash tile.

### Appendix

- A1–A3: the agreed assumptions grid (every input as a distribution).
- A4: where each comes from, one line a row.
- A5: the bridge from the last deck, as a waterfall (`cohort_bridge`).
- A6: how many loans.
- A7: cross-sell by product. Use the booked ₹/saver-year as the page number, with the "settled" run rate as a small note.
- A8: collections.
- A9: year by year for one agent.
- A10: the online cost method.
- A11: the one interview.
- A12: what is left out (tele-sales detail, office, licences, regulatory risk such as the IRDAI caps and SEBI on digital gold).

## Rules

- Never name Bueno or BetterPlace. No customer names; the interview is "a janta agent".
- "Can", not "will", for anything untested. Plain words; no raw keys on pages.
- ₹ with Indian grouping.
- Every number on a page comes from a CSV a script writes.
- Output: `model/build_deck_v3.py` → `Offline_model_v3.pdf`. Do not touch other PDFs or scripts.
- Render-check every page with the system `python3 $S/render.py <pdf> $S/deck3 $S/lib 1.0`. Look at every PNG.
- `$S=/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad`

## Report (under 300 words)

- The page titles.
- The word-count table.
- The headline numbers used and their source tables.
- Anything you couldn't fit.

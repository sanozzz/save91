# Reviewer briefs for Offline_model_final_v2.pdf

Both reviewers first read `story/BRIEF_final_v2_2026-10-16.md` (what the builder was asked to do).

- Root: `~/Desktop/Random/savings-first-deck/`
- Python: `~/.cortado-venv311/bin/python`
- Scratchpad: `$S=/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad`

You are reviewers. **Do not edit any file in the project.** Write only to your own scratch folder.

Return findings as a numbered list. Give each finding:

- a severity:
  - **P1**: wrong number, misleading claim, or broken page;
  - **P2**: unclear or loose;
  - **P3**: polish;
- the page number;
- what is wrong;
- the evidence: a table row, a calculation, or a line of the screenshot;
- the exact fix.

Only list a finding you have checked. Say "verified" with the check you ran, or "plausible" if you could not run one.

## Reviewer A: numbers and assumptions (scratch folder `$S/revA/`)

1. **Re-run the model.** Run `model/crosssell_money.py` into a copy of the tables (or diff its outputs) and confirm the CSVs are reproducible.
2. **Check every number on the page against its table.** Extract the PDF text with pypdfium2:

   ```python
   import sys
   sys.path.insert(0, "$S/lib")
   import pypdfium2 as pdfium
   page.get_textpage().get_text_range()
   ```

   For every ₹ figure, percentage and "N of 100" on pages 1 to the end, find the CSV value it comes from. List any figure with no table source, or one that differs after rounding.
3. **Recompute the core arithmetic independently.** Write your own short script; do not import the builder's.
   - Funnel: loans per 100 proven savers a year = apply × eligible × approved.
   - Fee per loan = ₹2.5L × 2.625% × (1 − 2.5%).
   - Card money per 100 proven savers.
   - Other products ₹63 per saver a year.
   - The 5-year NPV at 55 of 100 still saving, salary only.
   - The 5-year break-even.

   Tolerance: ±1%.
4. **Assumption tightness.** For each input in `tables/xs_inputs_v2.csv`:
   - Is the cited source ID real, and does it say what the row claims? Grep `research/*.csv` and `research/*.md`.
   - Is `status` honest? Any judgement must not be labelled evidence.
   - Is anything double-counted? For example, Paisabazaar's 4.7% includes card fees while we also count cards; cards to non-proven savers; other products counted on savers who have left.
   - Is anything timed too early? For example, a card or loan fee before month 7, or collections before the default lag.
5. **Pilot rules.** Check that the month-12 go line equals the 5-year break-even, that months 3 and 6 equal R12^(3/12) and R12^(6/12), and that the pilot-year cost reconciles to a table.

## Reviewer B: story, precision and layout (scratch folder `$S/revB/`)

1. **Render every page:**

   ```
   ~/.cortado-venv311/bin/python $S/render.py <root>/Offline_model_final_v2.pdf $S/revB $S/lib 1.3
   ```

   Look at **every** PNG with the Read tool.
2. **Layout.** Check for clipped SVGs, overlapping labels, text overflowing boxes, tables too wide, empty or half-empty pages, and a duplicated title.
3. **The story chain.** Write out only the page titles in order. Does reading them alone make one tight argument?
   - problem → hypothesis → evidence → where the money comes from → what a customer is worth → pay rule → retention → risks → pilot.

   Flag:
   - any title that does not follow from the one before;
   - any repetition;
   - any page that could be cut;
   - any jump.
4. **The operator's standing complaints.** These are "too much text", "too number driven", "story not tight", "be very precise" and "key conclusions first, final thought: pilot or not". Flag:
   - pages with more than about 40 words of body or caption text;
   - number dumps where a picture would do;
   - "will" used for untested things;
   - jargon (R12, CM1, DLG unexplained, raw keys);
   - any Bueno/BetterPlace mention;
   - customer names.
5. **Credit cards and cross-sell money.** The operator explicitly asked to see "money we can make on credit card etc." Is it clearly visible in the main story, not only in the appendix? Is the card assumption (who gets one, when, the fee) stated tightly where it is used?
6. **Assumptions in the appendix.** Does every assumption a main-page number relies on appear in an appendix page, with its source and status? Is it obvious which inputs are judgement or untested?

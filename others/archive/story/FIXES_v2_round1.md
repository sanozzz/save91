# Fix round 1 for Offline_model_final_v2.pdf (two reviews merged; decisions made by the lead)

Apply everything below, re-run `crosssell_money.py`, then `build_final_deck_v2.py`, and render-check every page. Keep v2 as the file name and overwrite it; the old Offline_model_final.pdf stays untouched. **Report the new headline numbers and how each model change moved the break-evens, one change at a time.**

## A. Model changes (tighter, decided)

- **M1, the balance.** Replace "every saver holds ₹42,000 from day one" with the honest yearly-term cycle.
  - In his saver-month k the balance is ₹7,000 × (((k−1) mod 12) + 0.5). The average over a full term is still about ₹42,000.
  - A saver who stops withdraws, so his balance and commission go to zero.
  - Use the same balance for the "0.5% of balance" pay.
  - Re-implement this inside `crosssell_money.py`; do not edit `agent_npv.py`.
  - Check that the fund income for a saver who stays a full year matches the old one within rounding.
- **M2, insurance and other products start at month 7, on proven savers only**, like loans and cards. The story (page 5) says the marketplace opens at month 7. The model must match.
- **M3, capacity.**
  - One agent can make about 400 cash visits a day; at one visit every 2.5 days that is about 1,000 savers on cash visits (`agent_3yr.py` / `scenarios.py`).
  - Do not add a second agent. Instead, compute by year the share of his book that must save by UPI (no cash visit) for the plan to hold.
  - Show it on page 5 or page 13, and on A6 as "visits a day needed" and "share on UPI needed".
  - Make it a pilot gate on page 14: visits a day, and the share moved to UPI.
  - Say plainly that the NPV assumes the salary covers the whole book only because most savers move to UPI.
- **M4.** Recovery fees arrive about 18 months after the loan. Exclude them from the pilot-year cash.
- **M5, tornado rows to add:**
  - agent salary ₹15,000–₹25,000 a month (interview range);
  - card fee for an FD-secured card, ₹300–1,500 (XL-54, assumed);
  - card share 0.5–5% (XL-54's band).

## B. Labels and sources

- The base 5% card share = the top of XL-54's 0.5–5% FD-secured band, which is itself assumed. Reword the A1 note.
- On page 8, next to the card money, add: "if issuers accept him: most cards need income proof".
- The middle retention of 55 of 100: status → judgement ("between the bear case and the one janta agent's book"). IV-11 and IV-12 do not say 55.
- The online cost to win ×1.1 for shopkeepers: status → judgement.
- The `days` row: cite IV-03 if it supports 20 deposit days a month; otherwise mark it judgement with no source. XB-03 is wrong.
- One rule for status:
  - blog or affiliate-guide sources → "unverified";
  - company filings or regulator documents → "evidence";
  - our own arithmetic → "derived";
  - our call → "judgement";
  - the operator's figure → "operator".

  Apply it to every A1 row (trail XB-04, taken back XL-13/LEV-009, card fee BM-08, and so on).
- Page 4 title: "his churn implies about 72 of 100", not as if it were measured.
- Page 5 labels:
  - "₹6,398 a loan (2.625% of ₹2.5 lakh, less 2.5% taken back)";
  - "+₹155 a loan on average, from recovery fees".
- Use ₹6,398 on every page; page 10 uses ₹6,563.
- Paytm, like for like: its ₹1,080 a year device rent against our all-in income per proven saver a year (fund + loans + cards + other, on the new numbers). No ratio built on fund + other only. "About 20×", not "20.8×", because the ~₹5,000 is an upper bound.
- A11: relabel the "22.3 / 27.4" row "today's fee and funnel, cards still paid on every sign-up". Add a row for each change in section A.

## C. Story and text

- **Order:**
  1. conclusions;
  2. problem;
  3. hypothesis;
  4. model;
  5. H1 (win him for less);
  6. H2 (keep him);
  7. H3 part 1;
  8. H3 part 2;
  9. what one customer is worth;
  10. can we beat Paytm;
  11. salary is the only pay that works;
  12. retention decides;
  13. what could break it;
  14. our final thought.

  Keep the Paytm page in the main story: it is the operator's core question. Make its title one number.
- **One number per title** at most two. Page 11 title: "Salary is the only pay that works". Leave the break-even to page 12.
- **One rounding in the main story:** whole numbers ("29 of 100", "36 of 100"). Use decimals only in the appendix.
  - Drop page 9's 24.7 sentence.
  - Round month-3 lines up consistently.
  - "Below 63 a month", not 62, since 750 ÷ 12 = 62.5.
- **"₹35,485 a year"** (or its new value): split it into "₹X a year, plus ₹Y once" wherever it appears (page 1, page 8, A4). Cards pay once.
- **Text:**
  - Cut the repeated ~70-word base-case footer to one short line, "Base case and sources: A1", plus the page's own table names.
  - Cut page 1's verdict box to two lines; the thresholds live on page 14.
  - Aim for 40 words or fewer of body and caption text on each story page.
- **Page 1:** add a one-line gloss: "NPV = today's value of income minus cost, discounted 20% a year." Explain "bear case" once: "bear case = 30–40 of 100 still saving after a year".
- **No raw keys on any page:** `disc_rate`, `cac_target`, `npv_savings_only`, `PAYS`, and so on. Use plain names.
- **Pilot page 14:**
  - make the stop rules match page 1 exactly: month 3 below 74 (or the new value), month 6 below 54 (or new);
  - state the marketplace gate in counts readable by month 12, e.g. "about 3 loans and N cards by month 12; rethink at 1 or none", plus the apply rate;
  - add visits a day and the share moved to UPI;
  - add one line: "month-3 line assumes a steady drop-off; about 80 savers by then, so read it as a warning, not a verdict".
- **Layout:**
  - remove the empty bands (about 120px) on pages 1, 6 and 10 and on A10;
  - use non-breaking hyphens in source IDs (LEV‑009, IV‑04, XB‑09) so they don't split;
  - page 6: put the ₹600 label outside its bar like the others;
  - where the small kicker repeats the opening of the title (pages 2, 3, 5, 10–14), keep only one of the two.
- **Label the cards segment on page 9.** On page 8, add the per-agent card money once his book is steady (from A6), with the eligibility caveat.

## D. Report back

Give:

- the new title chain;
- each model change's effect on the 5-year and 3-year break-evens, one at a time and then combined;
- the new headline numbers: NPV at 30 / 40 / 55 / 70; money per customer won by product; the yearly and one-off marketplace money per 100 proven savers; the pilot-year cost; the stop/go lines;
- whether the verdict "pilot it" still holds. If the 5-year break-even ends above 40 of 100, say so plainly. Do not soften it.

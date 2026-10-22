# Brief: final deck v3, picture-first. Same numbers, far less text, clean assumptions

## What the operator said about v2 (16 Oct 2026, verbatim)

> "No I still dont like the story. Too much text. I want more pictures,charts, flowcharts explaining the story. Also assumptions have to be clean etc."

Measured: v2's story pages carry **110–303 words** each. The style the operator accepted earlier is **`QR_moat_story.pdf`** (built by `model/build_qr_visual.py`). Open its renders; they are the reference.

- Each page has ONE big picture filling the page.
- A title of about 10 words.
- One takeaway line.
- A tiny sources line.
- About **70 words a page including sources**.

v3 must look like that.

## What stays the same

- **The model and every number.** Use `model/crosssell_money.py` and the `tables/xs_*_v2.csv` and `pilot_rules_v2.csv` as they are. Do not change the model unless section C says so.
- **The verdict:** pilot, small and on salary. The 5-year break-even is 37 of 100; the 3-year is 47.
- **The rules:**
  - every number comes from a table;
  - never name Bueno or BetterPlace, and no customer names;
  - "can", not "will";
  - ₹ with Indian grouping.

## Output

- `model/build_final_deck_v3.py` → `Offline_model_final_v3.pdf`. Leave v2 untouched.
- Reuse the helpers in V (`build_qr_visual.py`) and from v2, plus the same CSS look.

## A. Hard text budget (check it by script, and fail the build if any page breaks it)

Add `check_words()` to the builder. Extract each page's text with pypdfium2, using the system `python3` with `$S/lib`, and print a table of pages and word counts. **The build is not done until every page passes.**

- **Story pages:**
  - **at most 70 words in total**, including the sources line;
  - title at most 12 words;
  - one takeaway line, at most 14 words;
  - sources line at most 15 words, e.g. "Sources: A3, A5. Tables: xs_money_v2.csv".
- **No paragraphs, captions, notes or base-case footers on story pages.** If a fact needs a sentence, it goes in the appendix.
- **Numbers live inside the picture:** as bar labels, a big number, or a node in a flow. Not in text.
- **No more than 4 distinct numbers in a picture's labels**, except on charts with axes.
- **Appendix pages:** at most 150 words, except A1/A2 (the assumption tables).

## B. The story: 13 pages, one picture each

Titles are given; keep each within its word cap. Use these pictures.

1. **"We should pilot: the street wins him cheaper, if 37 in 100 stay."** (Conclusions first.)
   - **Picture:** a 3-step flow of big tiles with icons, then a verdict stamp:
     - [phone] Online: ₹2,067 per saver kept;
     - → [person] Street: ₹240 to win;
     - → [hands] Pays back if 37 of 100 still save.
   - **Stamp:** a green "PILOT ✓ 1 agent · 12 months · ₹1.3–1.7 lakh".
   - **Takeaway:** "Every page after this is the proof; every assumption is in the appendix."
2. **"Online, a saver kept costs ₹2,067."**
   - **Picture:** a pictogram of 100 phone-person icons, 24 coloured.
   - Beside it: "₹499 to win each" → "÷ 24 still saving" → a big ₹2,067.
3. **"Our bet: win, keep and earn on the street."**
   - **Picture:** a 3-box flowchart. H1 Win him for less [person] → H2 Keep him with a visit [hands] → H3 Earn from the relationship [bank]. Each box has a small "test: page N" tag.
4. **"How it works: save for 6 months, then the marketplace opens."**
   - **Picture:** a horizontal journey timeline:
     - shop sign-up;
     - a visit every 2–3 days (dots);
     - a fund in his name (a growing mini bar);
     - a UPI arrow;
     - **month 7 gate**;
     - three branches: loans, cards, insurance.
   - Icons and short labels only. No sentences.
5. **"H1: the street wins him for half the price."**
   - **Picture:** two paired bar groups. Cost to win: ₹499 vs ₹240. Cost per saver kept: ₹2,067 vs ₹343–800 (a range bar).
6. **"H2: he already saves daily, with someone he trusts."**
   - **Picture:** survival curves of the share still saving by month, 0–12:
     - an app curve to 24;
     - the bear band 30–40;
     - a janta-book curve to about 72.
   - Use `tables/agent3_survival.csv` or a curve you write to a table.
   - Mark 37 as a dashed line: "we need".
7. **"H3: his savings alone don't pay the agent."**
   - **Picture:** two bars per agent-year with a steady book: what his savers' fund pays us vs his ₹2.4 lakh salary. Pick one year and one retention, and label which.
   - Or show per saver: ₹147 a year vs the cost. Choose the clearer one.
8. **"The money comes after month 7: loans, cards, insurance."**
   - **Picture:** a funnel (100 → 20 apply → 10 eligible → 3.5 loans) flowing into a stacked bar of rupees per 100 proven savers:
     - loans ₹22,395 a year;
     - insurance ₹6,300 a year;
     - recoveries ₹541 a year;
     - cards ₹6,250 **once** (hatched).

   No other text.
9. **"At 55 in 100, a customer earns us about 2× his cost."**
   - **Picture:** the stacked bars per customer won (app, 30, 40, 55, 70) with the cost line. Keep v2's chart; strip all text except the labels.
10. **"Paytm earns more per user; we win him far cheaper."**
    - **Picture:** a two-panel bar chart. Cost to win: Paytm up to ₹5,000 vs us ₹240. Earns a year: ₹1,080 device rent vs our ₹439 per proven saver.
    - Two shop icons on top.
11. **"Pay him a salary; a cut of savings loses money."**
    - **Picture:** three bars per saver per year:
      - the fund pays us ₹147;
      - 0.5% of balance to him ₹210;
      - 1% of collections to him ₹840.
    - A red "loses" stamp on the last two.
12. **"Retention decides: positive from 37 of 100."**
    - **Picture:** v2's NPV curve (5y and 3y). Mark the bear band, online 24 and the janta book 72. Break-even markers at 37 and 47.
13. **"What could break it."**
    - **Picture:** the tornado at 40 of 100.
      - Top 8 rows only; the rest go to the appendix.
      - Use status dots, not pills.
      - Remove the low→high text columns; put the values at the bar ends.
14. **"The pilot: one agent, 12 months, five gates."**
    - **Picture:** v2's gate timeline. Each gate box shows ONE go number and ONE stop number, with icons.
    - The pilot-year cost goes in a single big-number tile.
    - No sentences in the boxes. The caveats about the month-3 sample and UPI behaving like cash go to the appendix.

(That is 14. If pages 11 and 12 read better merged, merge them; otherwise keep 14.)

## C. Clean assumptions (the appendix)

The v2 A1 mixes inputs with results, uses 5 status labels, and has long notes. Clean it up as follows.

1. **Only true inputs are assumptions.** Move derived rows out of the assumption pages, e.g. "loans per 100 proven savers = apply × eligible × approved" and "money held in his fund". They become results.
2. **Four confidence labels only**, each shown as a coloured dot with a legend:
   - **Your number** (operator);
   - **Published** (a company filing, regulator or official data);
   - **Industry guide, not verified** (blogs, affiliate guides);
   - **Our judgement**.
3. **Group the inputs into 6 blocks**, each a picture of small cards:
   - The saver: daily amount, deposit days, still saving after a year.
   - The agent: salary, sign-ups, visits a day, visit gap.
   - The fund: commission.
   - Loans: apply, eligible, approved, ticket, fee, taken back, bad-loan rate, recovery fee.
   - Cards: share, fee.
   - Insurance and other products: ₹ a year.
   - Money terms: discount, horizon.

   Each card shows the input name in plain words, the MIDDLE value big, low–high small underneath, and a confidence dot.
4. **A1 "Every assumption at a glance":** the card grid above, on one page if it fits, otherwise two.
5. **A2 "Where each comes from":** a clean table with columns input · middle (low–high) · source in plain words (e.g. "Janta agent interview, 15 Oct", "Paisabazaar results, Q1 FY27", "DSA payout guides") · confidence dot · ID. Use one line per row, no wrapping notes, and no long notes column. Put an ID column at the far right in small type.
6. **Then one picture page per assumption group that drives the result:**
   - **A3 Loan funnel:** the funnel with the evidence for each step as small tags.
   - **A4 Origination fee:** a number line 0–11% showing:
     - the bank DSA band 0.5–1.5%;
     - the NBFC/fintech DSA band 1–3%;
     - our 2.625% marker "1.5× a DSA";
     - the Paisabazaar ≤4.6–4.7% marker "incl. cards";
     - Paytm 4.5–5%;
     - Moneyview about 11% "with first-loss cover".
   - **A5 Credit cards:** fee range bars plus the who-can-get-one icon list (keep v2's A4, trimmed).
   - **A6 Insurance and other products:** horizontal bars per product summing to ₹63, plus a callout for the IRDAI cap draft.
   - **A7 Year by year:** small charts (savers, visits a day, UPI share needed, NPV by year). No big table, or a table only below a chart.
   - **A8 What changed since the last deck:** a step chart of the 5-year break-even 22 → 29 → 33 → 37, with each step labelled by its cause.
   - **A9 What's left out, and caveats:** an icon list covering tele-sales and AI support, office, licences, the month-3 sample size, UPI behaving like cash, and the 1,000-savers capacity.
   - **A10 Paytm detail, A11 online cost-to-win method, A12 the interview:** keep v2's, trimmed to the budget.
7. **One rounding everywhere in the story:** whole numbers. Decimals only in A2.

## D. Process

1. Build pages 1–4 and A1 first. Render them and look at them (system `python3 $S/render.py <pdf> $S/v3 $S/lib 1.0`).
2. Run `check_words()`.
3. Then build the rest.
4. Render-check all pages: no clipping, no overlaps, no half-empty pages. Every picture should fill most of the page.
5. Report back:
   - the page list;
   - the word-count table;
   - anything you couldn't fit within budget and how you resolved it;
   - the paths.

`$S=/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad`. Use `$S/v3/` only.

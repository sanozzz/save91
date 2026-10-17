# Brief: agree the assumptions first, as distributions (before any deck work)

## What the operator said (16 Oct 2026, verbatim)

> "I dont agree with the slide 16, we need to first agree on assumptions first - how many loans, everything is a distribtuion. Lets first finalize the distribution"

Earlier: "Too much text. I want more pictures, charts, flowcharts... assumptions have to be clean".

Slide 16 is v2's A1 (2 of 2), a table of low/middle/high values (render: `$S/lead3/p16.png`). The operator wants every uncertain input as an agreed **distribution**, finalized with them **before** the model and deck are rebuilt. **No deck work in this task.**

## Deliverables

1. **`tables/dist_proposal_v1.csv`**: one row per input. Columns:
   - `group`, `key`, `name` (plain words), `kind` (distribution | decision);
   - `shape` (triangular | pert | lognormal | beta | fixed), `low`, `likely`, `high`;
   - `p10`, `p50`, `p90`, `mean` (computed by sampling), `unit`;
   - `confidence` (one of: Your number | Published | Industry guide, not verified | Our judgement);
   - `evidence_points` (e.g. "Kissht 17.5% ever borrowed (XL-42); Brazil 20% year one (LS-06)"), `source_ids`, `why_this_shape` (one sentence).
2. **`model/dist_proposal.py`** writes the CSV. It also samples the derived quantities, 20,000 draws with a fixed seed: loans per 100 proven savers a year = apply × eligible × approved; fee per loan; marketplace money per 100 proven savers a year (yearly) and once (cards). It writes `tables/dist_derived_v1.csv` with p10/p50/p90/mean for each.
   - Use numpy/scipy in `~/.cortado-venv311/bin/python`.
   - Reuse the conventions in `model/mc_dists.py` / `tables/distributions.csv` where helpful.
3. **`Assumptions_to_agree.pdf`**, picture-first, in the `QR_moat_story.pdf` style (`model/build_qr_visual.py` helpers, Chrome headless, same look). Make it about 8–9 pages, at most 90 words a page excluding tick labels. Pages:
   1. **"What we need to agree"**: a picture of the input groups as tiles with an icon each. Each tile shows a count of inputs and a coloured dot for each one's confidence. Also show the 5 open choices for the operator (section C) as numbered chips.
   2. **"How many loans"**: the centrepiece.
      - Show three small distribution curves (apply, eligible, approved) multiplying into one histogram of loans per 100 proven savers a year.
      - Label p10/p50/p90.
      - Mark the evidence points as labelled ticks on the axis, including the older evidence range of 0.45 / 2.5 / 9.8 per 100 proven a year (`tables/agent3_funnel_inputs.csv` / `agent_npv.EVIDENCE_LOANS`).
      - Then show the fee per loan distribution.
   3. **The saver:** daily amount, deposit days, still saving after a year. Retention is the crux: show it with the app's 24 of 100, the operator's bear 30–40, the janta book's ~72 and "we need 37" marked.
   4. **The agent:** sign-ups a year (mark the operator's 1,000 and the interview's 6–10 a month), cash visits a day. Salary is a decision tile at ₹20,000.
   5. **The fund:** commission. Show two candidate products side by side, liquid fund vs debt fund (section C).
   6. **Loans, the rest:** origination fee (with the benchmark ticks: bank DSA, NBFC DSA, 1.5× DSA, Paisabazaar ≤4.6–4.7% incl. cards, Paytm 4.5–5%), taken back, ticket size, bad-loan rate, recovery.
   7. **Cards and insurance:** card share and fee; insurance and other products.
   8. **Decisions, not distributions:** salary, the month-7 gate, the visit gap, discount 20%, horizons 3 and 5 years. Show them as fixed tiles.
   9. Optional: **"Where each comes from"**, a one-line-per-row table with input, likely (low–high), source in plain words and a confidence dot.

   Each input is drawn as a small density curve with p10/p50/p90 marked and the evidence ticks on the axis. One line of label under it, no paragraphs.

   **THE OPERATOR'S EXPLICIT ASK (added mid-brief): "create a slide that should show those distribution. every take rate, every thing".** Make this slide **page 2**, right after "What we need to agree": **"Every assumption, as a distribution"**.

   - Show **every** uncertain input on ONE page as a grid of small-multiple density curves (about 22 tiles). This includes every take rate: apply, eligible, approved, the origination fee, taken back, bad loans, recovered, our recovery fee, the card share, the card fee, insurance and other products, and the fund commission. It also includes the saver, agent and online inputs.
   - Group the tiles by row (saver, agent, fund, loans, cards and insurance, online), with a small group label at the left.
   - Each tile shows:
     - the name in plain words;
     - the curve with the p10–p90 band shaded;
     - the likely value as a bold number;
     - "low–high" small underneath;
     - a confidence dot.
   - Decisions are shown as flat grey tiles with a single value.
   - Tick labels may be tiny, but they must be legible at A4.
   - If 22 tiles truly do not fit legibly, use two pages ("1 of 2", "2 of 2"), with the loans and cards rows together on one.
   - Exempt this page from the 90-word cap; the numbers in tiles are the content.

   The detailed group pages follow it.

## A. Proposed distributions (the lead's proposal; the agent may adjust ONLY with evidence, and must report each change)

Check every evidence ID by grep in `research/*.csv` and `*.md`. Where my number is not supported, say so.

**The saver**

| Input | Shape | Low / likely / high | Basis |
|---|---|---|---|
| Daily amount | triangular | ₹200 / 350 / 500 | operator; IV-03 |
| Deposit days a month | triangular | 16 / 20 / 24 | judgement: shop open about 26 days, some misses |
| Still saving after a year | pert | 25% / 45% / 72% | app 24 (story_unit), bear 30–40 (operator), janta book ~72 (IV-11/12 churn arithmetic) |

The likely value for retention is an **open choice**.

**The agent**

| Input | Shape | Low / likely / high | Basis |
|---|---|---|---|
| Sign-ups a year | pert | 600 / 1,000 / 1,200 | operator 1,000; the interview signs only 6–10 a month, but a janta agent isn't selling |
| Cash visits a day | triangular | 300 / 400 / 450 | IV-01, agent_3yr |

The sign-ups likely value is an **open choice**. Visits a day affect the UPI need only, not the NPV.

**The fund**

| Input | Shape | Low / likely / high | Basis |
|---|---|---|---|
| Commission | pert | 0.20% / 0.35% / 0.50% if a debt/short-duration fund (XB-04); 0.05% / 0.08% / 0.10% if a liquid fund (inputs.csv `trail_liquid`) | **Open choice:** which fund the daily money goes into |

**Loans**

| Input | Shape | Low / likely / high | Basis |
|---|---|---|---|
| Apply a year (proven savers) | pert | 8% / 18% / 35% | XL-42 Kissht 17.5% ever borrowed; LS-06 Brazil 20% year one; founder 35% |
| Eligible for the ticket | pert | 25% / 45% / 65% | XB-09 EMI rule; IV-04 incomes; XL-34 |
| Approved (several lenders) | pert | 20% / 35% / 50% | XL-41 Kissht 11% new / 74% repeat; founder's single-lender 25% |
| Ticket | pert | ₹1.0 / 2.5 / 3.0 lakh | operator ₹2.5L; XB-08 Paytm average ₹2.05L |
| Origination fee | pert | 1.5% / 2.625% / 3.5% | operator 1.5× DSA; XL-13, LEV-009; stays under Paisabazaar's ≤4.6% (which includes cards) |
| Taken back | triangular | 0% / 2.5% / 5% | XL-13, XL-47 |
| Money lost on loans, after recoveries (share of money lent): **UPDATED by the operator** | pert | 1.5% / 3% / 5% | worst case = Paytm's ECL 4.5–5% (XB-07, QM-22), per the operator: "our worst case would be paytm default rates… genuine self selected savers… our agent also helps us collect back"; low near SHG 1.74–2.05% (SE-01, EVD-03); NBFC-MFI 5.4% (SE-02) as a tick. The "owed when bad" input is dropped; recovery fee per loan = ticket × loss × recovered/(1 − recovered) × fee |
| Recovered | triangular | 25% / 32.5% / 40% | XB-07 |
| Our fee on recovered | triangular | 5% / 10% / 15% | NABARD tender, unverified |

- **Repeat borrowers:** a saver with a loan running does not apply again until it ends. Note this; model it only if it is easy in the sampler (probably negligible at about 3 per 100).

**Cards and insurance**

| Input | Shape | Low / likely / high | Basis |
|---|---|---|---|
| Card share (proven savers, once) | pert | 1% / 3% / 6% | operator said 5%; XL-40 only 3% of Indians hold a card; XL-54 0.5–5% FD-secured, assumed |
| Card fee | pert | ₹300 / 1,000 / 2,000 | BM-08 ₹500–2,000 unsecured; XL-20 GroMo ₹1,000–2,400 to sub-agents; XL-54 FD-secured ₹300–1,500 assumed |
| Insurance and other products | pert | ₹8 / 63 / 259 a proven saver a year | XO-39; PhonePe ₹8 a user on insurance (XO-10) |

- The card share likely value is an **open choice**.
- For insurance and other products, show the mean too: PERT's mean is above 63.

**Online comparison** (used for comparison only):

| Input | Shape | Values | Basis |
|---|---|---|---|
| Online cost to win | lognormal | P5 ₹186 / median ₹499 / P95 ₹1,340 | existing `distributions.csv` row `cac_target ng` |
| Online still saving after a year | beta | mean 24%, about 15–35% | story_unit; check research for a range |

**Decisions (fixed):** salary ₹20,000 a month; proven saver = 6+ months (offers from month 7); visit every 2.5 days; discount 20% a year; horizons 3 and 5 years.

**Independence:** treat inputs as independent, except note one link for the operator to decide: in a bad year, approvals fall and bad loans rise together.

## B. Rules

- Plain words only, and no raw keys on pages.
- ₹ with Indian grouping.
- Never name Bueno or BetterPlace.
- No customer names: the interview is "a janta agent".
- No web research; only `research/*`.
- Render-check every page with the system `python3 $S/render.py <pdf> $S/dist $S/lib 1.0`, and look at every PNG.
- Print a word count per page; any page over 90 words fails.
- Files: `$S/dist/` only.

`$S=/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad`

## C. Open choices for the operator (list them on page 1; do not decide them)

1. Still saving after a year: the likely value (proposed 45%).
2. Sign-ups a year: the likely value (proposed 1,000; low 600).
3. The fund for the daily money: liquid (about 0.08%) or debt/short-duration (about 0.35%).
4. Card share of proven savers: likely 3% (evidence) or 5% (the operator's figure).
5. Bad years: should approvals and bad loans move together?

## D. Report back (under 400 words)

- The page list.
- Derived p10/p50/p90/mean: loans per 100 proven savers a year; fee per loan; marketplace money per 100 proven savers (yearly, and once).
- Every place you changed my proposal, and the evidence.
- Every evidence ID that did not say what I claimed.
- The paths.

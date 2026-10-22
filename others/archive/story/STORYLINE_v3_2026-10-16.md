# Deck v3 storyline: simple, three parts, picture-first

## What the operator said (16 Oct 2026, verbatim)

> "So story in the deck should start from the current problems of online model and what our offline approach proposes to solve and what our analysis says… keep the story simple"

Also standing:

> "Too much text. I want more pictures, charts, flowcharts explaining the story."

Assumptions go in the appendix and must be clean. The style and word budget are in `story/BRIEF_final_v3_visual_2026-10-16.md` §A:

- at most 70 words a page;
- one picture a page;
- a title of at most 12 words;
- one takeaway line.

The numbers come from the cohort Monte Carlo on `tables/dist_agreed_v1.csv` (the `cohort_mc_*` tables), not from v2.

## Part 1: the problem with online (3 pages)

1. **Online, winning a daily saver costs ₹499.** A cost-to-win bar built from the three published signals (A: online cost method).
2. **Only 24 in 100 still save a year later.** A pictogram of 100 phone users, 24 coloured, with the app's retention curve beside it.
3. **So each saver kept costs ₹2,067, and the app never earns it back.** Two bars: cost per saver kept vs what an app saver earns back.

## Part 2: what our offline approach proposes (3 pages)

4. **The hook: his daily savings earn about 7% in a debt fund.**
   - Operator, 16 Oct: "Hook is high savings rate in debt funds that we offer".
   - **Picture:** three bars of what his money earns a year:
     - a janta deposit at a public-sector bank's savings-account rate, about 2.5% (operator, 16 Oct: "It's a bank savings account rate at public sector bank");
     - a liquid fund 5–6% (OWN-02);
     - our debt fund about 7%.
   - Big number: "about ₹X more a year for him on ₹350 a day". Take X from the sheet script (row `janta_rate`) or the cohort model.
   - Then: an agent at his shop, every 2–3 days.
4b. **Our approach: a fleet on the street, with an app in his hand.**
   - Operator, 16 Oct: "So the approach is to serve in a physical way i.e fleet on street with customer facing app etc".
   - **Picture:** two halves joined at the shop.
     - Left, THE FLEET (physical): signs him up at his shop, visits every 2–3 days, collects cash, builds trust, helps bring back overdue loans.
     - Right, THE APP (digital): his balance and ~7% return, UPI deposits, the marketplace (loans, cards, insurance), alerts.
   - Takeaway: "The agent wins and keeps him; the app serves him." The unit is ONE agent; a fleet is N of them.
   - Then the journey flowchart: sign-up at the shop → visits → a fund in his name → UPI on the app.
   - **Picture:** a journey flowchart: sign up at the shop → visits → a fund in his name → UPI.
   - Mark "cheaper to win (₹240 at 1,000 sign-ups; recompute at 60 a month)".
5. **From day one he gets a marketplace, at no cost to us.**
   - Operator, 16 Oct: "the marketplace opens as soon as possible. Simple. It's not at our cost."
   - **Picture:** the shop opening onto a marketplace of loans, cards and 17 products (icons by group). Lenders and insurers decide; we list.
6. **The agent knows him, so he also helps collect.**
   - **Picture:** the overdue-loan flow (brought back early, 90+ recovered), with Paytm's losses as our worst case.

## Part 3: what our analysis says (5–6 pages)

7. **We modelled every monthly cohort, 10,000 times.**
   - **Picture:** a simple cohort triangle (cohorts × months) feeding a "10,000 draws" fan.
   - One line: "every input is a distribution (appendix)".
8. **One agent pays back over 5 years in X of 10 futures.**
   - **Picture:** a fan chart of cumulative discounted cash by month (p10–p90), with the 3- and 5-year marks.
   - Big numbers: P(NPV60 > 0) and P(NPV36 > 0).
9. **Where the money comes from.**
   - **Picture:** a stacked area of revenue by line over 60 months for one agent (fund, loans, cards, insurance and other products, collections) against his cost line.
9b. **The longer he saves and repays, the more we earn.**
   - Operator, 16 Oct: rates "go up over time on our pool as we gather more history and repayment".
   - **Picture:** small multiples by year 1–5, at the likely values:
     - approval rate;
     - average loan size;
     - top-ups;
     - take-up;
     - sign-ups per agent.
   - Use `tables/` from the addendum-4 run.
10. **What must be true.**
    - **Picture:** a heatmap of P(NPV60 > 0) by still-saving-at-12-months band × sign-ups band. Mark the agreed likely cell.
11. **What could break it.**
    - **Picture:** the top 8 drivers as a tornado or a rank-correlation bar.
12. **Our answer: pilot one salaried agent for 12 months.**
    - **Picture:** the gate timeline. Each gate has one go and one stop number, recomputed from the cohort model.
    - The pilot-year cost goes in a single tile.

## Appendix (clean assumptions)

- **A1:** the agreed assumptions grid: page 2 of `Assumptions_agreed.pdf`, reused or rebuilt.
- **A2:** where each comes from, one line a row.
- **A3:** the bridge from the last deck (`tables/cohort_bridge.csv`) as a waterfall.
- **A4:** how many loans.
- **A5:** cross-sell by product.
- **A6:** collections.
- **A7:** the year-by-year table for one agent.
- **A8:** the online cost method.
- **A9:** the one interview.
- **A10:** what is left out: tele-sales and AI support cost (₹0 until the operator gives a figure), the customer app's build and running cost (not yet costed), the office, licences.

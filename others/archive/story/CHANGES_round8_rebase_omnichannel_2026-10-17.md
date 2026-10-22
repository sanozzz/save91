# Round 8: rebase, omni-channel acquisition with offline service (operator, 17 Oct 2026)

## The new evidence

A practitioner at a field-led savings fintech (LinkedIn chat with the operator, 17 Oct 2026; research row PR-01):

> "we do both online and offline. Online brings in more customers at a lower CAC, while the field team helps build trust and guides customers through their first investment. Most of our field agents onboard 100+ customers a month, with some reaching 120–150. ... Customers can choose based on their needs, whether it's mutual funds and SIPs for savings, gold and silver, or even loans and credit cards."

## The operator's model (confirmed by tap: "Yes, that's the model")

- One agent, one territory, end to end. He opens the accounts AND serves them on a daily route: cash pickups for savers who pay cash, and visits to UPI savers. Operator: "guys who open up the account and go everyday, also collects. that is the model."
- **No app-only channel.** Operator: "we acquire offline but we also serve offline to the customer as well to make sure of the retention is not bad". The app is for balance, UPI deposits and the marketplace.
- **Online leads:** half of an agent's onboardings start as online leads that we buy; the agent closes and serves them. They behave like street savers (same retention and take-up), because they are served offline.
- **Pay:** unchanged, ₹20,000 + 0.25% of his savers' balance (0.10% after month 60).
- **UPI:** unchanged, 30% likely by month 12 (operator tap). Cash visits above the 400-a-day capacity are bought as helpers at ₹20,000 per 400 visits a day; the existing extra-capacity line covers this.

## Input changes in `dist_agreed_v1.csv`

| key | change | shape and values | confidence and basis |
|---|---|---|---|
| `signups_run` | the year-1 level, once up to speed | pert 60 / **100** / 150 a month | Your number, plus Published practitioner evidence (PR-01: 100+ a month, top agents 120–150). The range covers agent-to-agent variation (operator: "each guy will be different"). |
| `signup_decline_y5` | NEW. Sign-ups fall in a straight line from the year-1 level (months 1–12, after the ramp) to this share of it by month 49, then flat | pert 0.5 / **0.7** / 0.9 | Your number (operator: "This can decline to 70 over 5 years"). Why: his time goes to the growing book. |
| `signup_growth` | SUPERSEDED: set to fixed 0; keep the row, marked superseded | | |
| `online_lead_share` | NEW. Share of onboardings that start as bought online leads | pert 0.3 / **0.5** / 0.7 | Your number (50%), range judgement |
| `lead_cost` | NEW. Our cost per online lead the agent converts | pert ₹150 / **250** / 499 | Your number (₹250). Context: finance-app installs ₹100–300 (TB-18..22); ₹499 is our full online cost per active saver (`story_unit`). |
| `ramp_months` | unchanged | 0 / 3 / 6 | |
| everything else | unchanged | | |

## Engine changes

- **Sign-up path:**
  - S(t) = signups_run × ramp(t) × decline(t);
  - decline(t) = 1 for months 1–12, then a straight line to signup_decline_y5 at month 49, flat after.
  - Remove the +10%/yr growth.
- **New cost line `cost_leads`** = online_lead_share × lead_cost × S(t). Add it to cost_total.
- **Must-be-true bands for sign-ups:** 60–80 / 80–100 / 100–120 / 120–150.
- **Bridge:** add steps "sign-ups 100 → 70 by year 5" and "online leads ₹250 for half".
- **Outputs (`cohort_mc_summary.csv`, same measure names), plus:**
  - lead cost over 60 months;
  - savers at month 60;
  - peak cash visits a day;
  - helper cost over 60 months.
- **Sweeps (the lead re-runs `model/signups_sweep.py` and `incentive_sweep.py` afterwards):**
  - the sign-up targets become 40, 60, 80, 100, 120, 150;
  - the sweep reads signups_run as the year-1 level, with the decline at its likely value.

## Deck, sheet and guide (after the engine run)

- **Page 5:**
  - cost to win each saver = salary ÷ sign-ups + online share × lead cost, i.e. about ₹200 + ₹125 = ₹325, against ₹499 online;
  - per saver kept: ÷ 55%.
- **Page 6/7 copy:** "online leads, served offline"; mention the practitioner evidence.
- **A13:** the sign-ups chart over 40–150.
- **A12:** delete any "app-only" mention.
- **The Google Sheet toy:** Inputs get `signup_decline_y5`, `online_lead_share` and `lead_cost`; remove signup_growth. Monthly gets the lead cost line and the new sign-up path. Re-verify against the engine.
- **START_HERE.md:** update §1, §3 and §5. Re-zip.

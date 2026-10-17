# Brief: the unicorn plan, on paper by year 5 (operator, 17 Oct 2026)

## Operator (verbatim)

> "So i want to be a unicorn by year 5..." (own-book lending is OUT for 5 years: "so ignore the nbfc angle till 5 year", "so till ignore lending")

> Tap: "Unicorn track"

> "also assume we can raise as much as possible if everything keeps holding, decide when to raise and how much and then work backwards to make us unicorn on paper by year 5"

**Basis:** ₹100/$ (the operator's convention). All market inputs as agreed. Pay is the ₹10,000-capped incentive. Distribution only, no own-book lending. Cost rules as built.

## The target, worked backwards

**"Unicorn on paper" at m60** = BOTH valuation lenses ≥ $1B (₹10,000 crore). Both are labelled "our judgement" everywhere:

| Lens | Rule | Threshold | Basis |
|---|---|---|---|
| Revenue | 20 × ARR at m60 (ARR = 12 × month-60 revenue) | ARR ≥ ₹500 crore | judgement: a multiple for a fintech growing more than 100% a year |
| AUM | 0.45 × AUM at m60 | AUM ≥ ₹22,222 crore | SAV-03: Stable Money's ₹2,507 crore post-money against about ₹5,000 crore invested (SAV-02). Caveat: that is CUMULATIVE money invested, not AUM, so the ratio is a rough proxy |

**Search** (re-use `model/arr100m.py` and `growth_model.py`, 120-month capable):
- fleet paths: agents at m18, hires a month after m18, the agent cap;
- find the LEAST total equity raised by m60 such that both lenses clear at m60 at the likely values.

Also report:
- the path that clears only the AUM lens;
- the path that clears both lenses at m54 (a faster alternative).

## Funding rounds (decide timing and size)

**Rounds:** seed at m0, A at m15–m18, B at about m30, C at about m42–m48, and a "unicorn round" D at about m60.

**For each round:**
- **Timing:** when cash would fall to 6 months of forward burn, or earlier at a milestone.
- **Size:** enough for 18 months of forward burn plus a ₹10 crore buffer, rounded to ₹5 crore (to ₹1 crore for the seed).
- **Pre-money valuation:** the HIGHER of the two lenses on that month's metrics, with stage multiples (judgement):
  - seed: ₹40 crore pre-money, fixed (about 20% dilution on ₹10 crore);
  - A: 25 × ARR or 0.45 × AUM;
  - B onwards: 20 × ARR or 0.45 × AUM.
- **Dilution check:** cap dilution at 25% a round. If a round would dilute more, raise less and bring the next round forward. Report it.

**Cap table:** founders start at 100%, with an ESOP pool of 10% created at the seed (diluting the founders) and topped up to 10% at A and B. Columns:
- round;
- month;
- amount;
- pre-money and post-money;
- dilution;
- founders %, ESOP %, investors %.

## Outputs

- `model/unicorn_plan.py`.
- `tables/unicorn_rounds.csv` (rounds, valuations and cap table).
- `tables/unicorn_yearly.csv`: years 1–5, plus 6–8 as context. Contents:
  - revenue by line, CM1/CM2/CM3, EBITDA, interest, PAT;
  - equity raised, closing cash;
  - agents, cities, central headcount;
  - savers, AUM, ARR, money lent (personal and housing).
- `tables/unicorn_monthly.csv`, months 1–96.
- `tables/unicorn_milestones.csv`: the metrics at each round month, the lens valuations, and the m60 unicorn check (both lenses, with the margin).
- `tables/unicorn_mc_summary.csv`, 1,000 draws with the funding plan fixed:
  - P(both lenses ≥ $1B at m60), P(AUM lens), P(ARR lens);
  - P(cash ≥ 0 through m96);
  - median valuation on each lens at m60.
- **Checks** (ladder sums, cash roll, cap table sums to 100%): `tables/unicorn_checks.csv`.

## Report (under 300 words)

- The recommended fleet path in plain words.
- The rounds table: month, amount, pre/post, dilution, founders % after.
- Total raised by m60.
- The yearly table (Y1–Y5, plus Y6–8).
- The m60 lens check.
- The MC.
- Founders' ownership at the unicorn round.

# Cohort model: re-run on the AGREED distributions, plus a bridge from v2

## 1. Point the model at the agreed file

- Set `DIST_FILE = T / "dist_agreed_v1.csv"`.
- Make the bad-years link (`corr_approved_loss` = −0.5) the BASE run. Keep the independent run as a side output (`_indep`).
- The operator's decisions are all in the file. Sign-ups are now pert 50 / 60 / 100; every other decision stands.

## 2. Re-run everything

- Deterministic run at the likely values.
- Monte Carlo: 10,000 draws.
- Rebuild the Excel at the likely values, and re-run the Excel ↔ Python check.

## 3. The bridge, NEW: why the answer moved

At r12 = 55%, start from the legacy v2 setting: NPV60 +₹4,06,283 and NPV36 +₹87,202. Switch on ONE change at a time, cumulatively, in this order:

1. The retention curve (r3, r12, late drop-off) replaces the steady drop-off.
2. The saving rate: deposit days and amount growth.
3. The fund: 25% kept at term end, and mid-term withdrawals.
4. Sign-ups: 60 a month likely, plus the ramp (from 83 flat).
5. The KYC cost.
6. UPI and extra cash-collection capacity.
7. Loans at the agreed likely values: apply, eligible, approved, tenure 36, repeats, fee 2.625%, taken back.
8. Cards at 3%, spread over months 7–12.
9. Seventeen cross-sell products replace ₹63 a year.
10. Collections by overdue bucket replace the old recovery fee.

Write `tables/cohort_bridge.csv` with columns step, NPV60, NPV36, change in NPV60, and the payback month.

## 4. What must be true (Monte Carlo, base run)

- P(NPV60 > 0) and the median NPV60 by band of:
  - sign-ups a month (50–60, 60–70, 70–80, 80–100);
  - late monthly drop-off (1–1.5%, 1.5–2%, 2–2.5%, 2.5–3%);
  - r12 (as before).
- A 2-way table: P(NPV60 > 0) by r12 band × sign-ups band.
- Write these to `tables/cohort_mc_must_be_true.csv`.

## 5. Report back (under 350 words)

- The bridge table.
- Deterministic results: NPV36, NPV60, payback month, year-1 cash, peak visits a day.
- Monte Carlo:
  - P(NPV60 > 0) and P(NPV36 > 0);
  - NPV60 at p10 / p50 / p90;
  - payback month at p10 / p50 / p90;
  - the top 8 drivers.
- The 2-way table.
- The Excel check.
- Reconcile the cross-sell definitions. The sheet says ₹239 a proven saver a year "once holdings settle"; the MC said ₹166 at p50. Say exactly what each measures, and which belongs on a page.

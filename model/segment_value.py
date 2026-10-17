"""One yardstick for every segment: the most we could pay to win a customer and still break even
(= what a customer is worth over five years before the cost to win them), under the redesign
(saving into funds with no fee per debit; unsecured loans by partner lenders; we earn a fee).

Each segment changes only what the segment research says differs: loan size, how long people
stay, and whether proven savers can keep borrowing after they stop saving. Everything else sits
at the evidence middle. Writes tables/segment_value.csv. Evidence: research/segments.csv (SG rows).
"""
import numpy as np

import mc
import redesign as R

SEGMENTS = [  # name, engine segment, loan size, month-12 still saving (None = evidence middle), keep borrowing after they stop, evidence
    ("Delivery riders", "gig", 25000.0, None, True, "SG-21 (actual loans Rs 2-10k; Rs 25k is generous), gig retention evidence"),
    ("Drivers and home-service workers", "gig", 150000.0, None, True, "SG-15 (UC Rs 28,322 net), vehicle loans Rs 75k-3 lakh; gig retention (no own data)"),
    ("Shopkeepers", "ng", 150000.0, None, True, "redesign base: XB-08, XB-10"),
    ("Salaried workers via employer", "ng", 100000.0, 0.79 ** 4, False, "SG-22 (Rs 18-26k pay carries Rs 1.7-2.5 lakh), SG-06 (21% of staff leave a quarter), SG-40 (pay deduction); loans stop when they leave"),
]


def main():
    dists = mc.load_dists()
    med = {r["input"]: float(mc.ppf(r, 0.5)) for r in R.new_rows()}
    cen = mc.centre(dists)
    out = []
    for name, seg, ticket, m12, grad, ev in SEGMENTS:
        c = dict(cen)
        if m12 is not None:
            c[f"ret_m12@{seg}"] = m12
        co = {k: float(np.ravel(v)[0]) for k, v in mc.to_overrides({k: np.asarray([v]) for k, v in c.items()}).items()}
        row = {"segment": name, "loan_size": ticket, "keep_borrowing": grad, "evidence": ev}
        for lam in (0.10, 0.20):
            r = R.customer(co, {**med, "wc_ticket": ticket, "wc_loans_year": lam}, graduate=grad, seg=seg)
            row[f"max_cac_{int(lam * 100)}"] = r["ltv60"]
            row["cac_evidence"] = r["cac"]
            row["still_m12"] = r["still_m12"]
        out.append(row)
        print(f"{name:<34} loan {ticket:>8,.0f}  still saving at 12m {row['still_m12']:.0%}  max cost to win: {row['max_cac_10']:>6,.0f} (1 in 10 borrow) / "
              f"{row['max_cac_20']:>6,.0f} (1 in 5)  evidence cost to win {row['cac_evidence']:,.0f}")
    mc.write("segment_value.csv", out)


if __name__ == "__main__":
    main()

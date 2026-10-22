"""The NBFC layer: an own book of personal loans from month 30 (story/BRIEF_realworld_lock_and_nbfc_2026-10-17.md, operator tap
"Test NBFC from year 3"). A post-processing layer on company_model.simulate() output; nothing else calls it.

Inputs (NBFC_INPUTS below; every one labelled with its basis):
  licence     acquire or build an NBFC-ICC at m24 for Rs 1 crore (LEV-031); net owned funds >= Rs 10 crore held as capital from
              m24; NBFC opex from m24: Rs 15 lakh a month + Rs 5 lakh a month per Rs 500 crore of book (pro rata; judgement).
  share       module default: on-book share of personal-loan volume (first, repeat and top-ups) ramps from 10% at m30 to 50% at m54.
              base_plan.py overrides this to a flat 30% from m30, and loss_mult to 0.6. Housing and other lenders' loans stay
              with partners.
  economics   yield 26% a year on the outstanding book (the agreed EMI rate; LEV-012 25-28%); processing fee 2% of the loan at
              disbursal (paid by the borrower); NO DSA origination fee on on-book loans; cost of funds 13.5% a year on
              borrowings (LEV-014/015); our collection fees on on-book loans are internal and dropped (the agent's effort and
              cost stay).
  credit      the agreed `loss` (lifetime loss of money lent, after recoveries; likely 3%) provisioned at disbursal (expected
              loss); losses are taken pro rata as the loans amortise, so the net book = (1 - loss) x the scheduled book, and
              interest is earned on the net book (defaulted principal stops earning; an approximation).
  book        each month's on-book disbursals amortise on the standard EMI schedule at the agreed rate over the agreed tenure
              (36 months), as cohort_engine's EMI mechanics; no prepayment.
  funding     NBFC equity = the larger of the Rs 10 crore NOF and 25% of the net book (borrowings <= 3 x equity: our choice.
              LEV-023 states gearing of 1.16x; its 3.25x is AUM/TNW, not debt/equity. LEV-063 Moneyview is 3.2x.
              capital 25% >= the 20% operating floor >= the 15% minimum); borrowings fill the rest. The equity is company cash:
              the rounds fund it (its growth is an investing outflow of free cash); NOF not yet lent is held, not free.
P&L: revenue = fee revenue (distribution commissions, DSA fees on the off-book share) + net interest income (interest - cost of
funds) + processing fees; CM1 = revenue - direct costs - credit cost (provisions); NBFC opex and the licence sit in central costs
(with the 10% contingency); the rest of the ladder as before. The 2-month commission lag applies to fee revenue only.
Lenses at m60 (judgement): (1) 20 x ARR, ARR = 12 x (fee revenue + NII + processing fees) in month 60; (2) 0.45 x AUM; (3) a
lending cross-check: 3 x the NBFC's book equity (P/B) + 20 x the platform's fee ARR.
"""
import numpy as np

import company_model as C

CR, LAKH = C.CRORE, C.LAKH
NBFC_INPUTS = (  # key, value, unit, plain words, basis
    ("licence_month", 24, "company month", "NBFC-ICC acquired or built", "LEV-031"),
    ("licence_cost", 1 * CR, "Rs, once", "Licence cost", "LEV-031"),
    ("nof", 10 * CR, "Rs", "Net owned funds held as capital from the licence month", "RBI minimum for an NBFC-ICC (Rs 10 crore)"),
    ("opex_base", 15 * LAKH, "Rs a month", "NBFC opex: credit, risk, compliance, treasury", "judgement"),
    ("opex_per_500cr", 5 * LAKH, "Rs a month per Rs 500 crore of book", "NBFC opex that scales with the book (pro rata)", "judgement"),
    ("share_start_month", 30, "company month", "On-book lending starts", "operator tap: test NBFC from year 3"),
    ("share_start", 0.10, "share of personal-loan volume", "On-book share at the start", "brief"),
    ("share_full_month", 54, "company month", "On-book share reaches its full level", "brief"),
    ("share_full", 0.50, "share of personal-loan volume", "On-book share from then on (NB3: 0.80)", "brief"),
    ("yield", None, "a year", "Yield on the outstanding book = the agreed EMI rate (rate)", "agreed input; LEV-012 25-28%"),
    ("processing_fee", 0.02, "share of the loan", "Processing fee at disbursal, paid by the borrower", "judgement"),
    ("cost_of_funds", 0.135, "a year", "Cost of borrowings", "LEV-014/015"),
    ("leverage", 3.0, "x equity", "Borrowings at most this multiple of NBFC equity",
     "3x is our choice (LEV-063 Moneyview 3.2x is the only row near it). LEV-023 gearing is 1.16x; AUM/TNW 3.25x is not debt/equity"),
    ("capital_floor", 0.20, "share of the book", "Operating capital floor (regulatory minimum 15%)", "brief"),
    ("loss", None, "share of money lent", "Lifetime credit loss after recoveries = the agreed `loss`", "agreed input (likely 3%; Paytm worst 5%)"),
)
DEFAULT = {**{k: v for k, v, *_ in NBFC_INPUTS},
           "loss_mult": 1.0}       # module default. The executed base passes 0.6 (base_plan.py). The old 0.5x was the superseded 15% case.


def shift(a, k):
    out = np.zeros_like(a)
    out[:, k:] = a[:, :-k] if k else a
    return out


def apply_nbfc(o, x, cfg=None):
    """o: company_model.simulate() output (any D). Returns a new dict with the NBFC lines and the restated P&L and cash lines."""
    c = {**DEFAULT, **(cfg or {})}
    o = dict(o)
    D, M = o["revenue"].shape
    t = np.arange(1, M + 1)[None, :]
    g = lambda k: C.E._col(x, k, D)[:, None]
    span = max(1, c["share_full_month"] - c["share_start_month"])            # a flat share: start = full
    share = np.where(t < c["share_start_month"], 0.0,
                     c["share_start"] + (c["share_full"] - c["share_start"]) * np.clip((t - c["share_start_month"]) / span, 0, 1))
    share = share + 0 * o["revenue"]
    disb = share * o["money_lent"]
    # fees: DSA origination only on the off-book share; collection fees on on-book vintages become internal
    o["rev_orig_loans"] = o["rev_orig_loans"] * (1 - share)
    o["rev_orig_topups"] = o["rev_orig_topups"] * (1 - share)
    o["rev_collections"] = o["rev_dpd31_90"] * (1 - shift(share, C.E.DPD_LAG)) + o["rev_recovery90"] * (1 - shift(share, C.E.REC_LAG))
    fee = sum(o[k] for k, _ in C.REVENUE)
    # the book: EMI amortisation at the agreed rate over the agreed tenure
    rate = float(np.mean(x["rate"])) if c["yield"] is None else c["yield"]
    i = rate / 12
    Tn = int(np.floor(float(np.mean(x["tenure"])) + 0.5))
    k = np.arange(M)
    frac = np.where(k <= Tn, ((1 + i) ** Tn - (1 + i) ** np.minimum(k, Tn)) / ((1 + i) ** Tn - 1), 0.0)
    G = np.zeros((D, M))
    for d in range(D):
        G[d] = np.convolve(disb[d], frac)[:M]
    loss = (g("loss") if c["loss"] is None else c["loss"]) * c["loss_mult"]
    N = (1 - loss) * G
    Gp = np.concatenate([np.zeros((D, 1)), G[:, :-1]], axis=1)
    interest = i * (1 - loss) * Gp
    lic = t >= c["licence_month"]
    E_req = np.where(lic, np.maximum(c["nof"], N / (1 + c["leverage"])), 0.0)
    Bw = np.maximum(0.0, N - E_req)
    idle = np.maximum(0.0, E_req - N)
    Bwp = np.concatenate([np.zeros((D, 1)), Bw[:, :-1]], axis=1)
    cof = c["cost_of_funds"] / 12 * Bwp
    proc = c["processing_fee"] * disb
    credit = loss * disb
    nbfc_opex = np.where(lic, c["opex_base"] + c["opex_per_500cr"] * N / (500 * CR), 0.0)
    licence = np.where(t == c["licence_month"], c["licence_cost"], 0.0)
    o.update(nbfc_share=share, nbfc_disbursed=disb, nbfc_book_gross=G, nbfc_book=N, nbfc_equity=E_req, nbfc_borrowings=Bw,
             nbfc_idle_capital=idle, nbfc_interest=interest, nbfc_cost_of_funds=cof, nbfc_nii=interest - cof, nbfc_processing=proc,
             nbfc_credit_cost=credit, nbfc_opex=nbfc_opex, nbfc_licence=licence, fee_revenue=fee,
             nbfc_capital_ratio=np.divide(E_req, N, out=np.full_like(N, np.nan), where=N > 0),
             nbfc_leverage=np.divide(Bw, E_req, out=np.zeros_like(N), where=E_req > 0))
    # P&L restated
    o["revenue"] = fee + o["nbfc_nii"] + proc
    o["direct"] = o["cost_bureau"] + o["cost_fraud"]
    o["cm1"] = o["revenue"] - o["direct"] - credit
    o["cm2"] = o["cm1"] - o["servicing"]
    o["cm3"] = o["cm2"] - o["acquisition"]
    o["nbfc_central"] = nbfc_opex + licence
    cen_ex0 = sum(o[k] for k, _ in C.CENTRAL_COSTS) - o["cost_raise_a"] + o["nbfc_central"]
    cont0 = o["_contingency"] * (o["direct"] + o["servicing"] + o["acquisition"] + cen_ex0)
    o["ebitda_ex_a"] = o["cm3"] - cen_ex0 - cont0
    # cash: commissions lag on fee revenue only; the book's equity growth is an investing outflow; borrowings are financing
    o["received"] = np.zeros_like(fee)
    o["received"][:, C.COMMISSION_LAG:] = fee[:, :-C.COMMISSION_LAG]
    o["receivable"] = sum(np.pad(fee, ((0, 0), (j, 0)))[:, :M] for j in range(C.COMMISSION_LAG))
    o["cf_receivable"] = -np.diff(o["receivable"], axis=1, prepend=0.0)
    o["cf_book"] = -np.diff(N, axis=1, prepend=0.0) - np.diff(idle, axis=1, prepend=0.0)
    o["cf_investing"] = o["cf_capex_laptops"] + o["cf_capex_integrations"] + o["cf_book"]
    o["cf_fin_extra"] = np.diff(Bw, axis=1, prepend=0.0)
    o["_nbfc_cfg"], o["_nbfc_loss"] = c, loss
    return o


def funded(o, seed_amt, rds):
    """The NBFC-restated o with a funding plan: fund-raising costs, contingency, central and EBITDA re-stated (NBFC central
    costs included); interest, tax and cash from treasury()."""
    o = dict(o)
    t = np.arange(1, C.M + 1)[None, :]
    o["cost_raise"] = o["cost_raise_seed"] + sum(C.SERIES_A_COST * (t == m) for m, a in rds if a > 0)
    cen_ex = sum(o[k] for k, _ in C.CENTRAL_COSTS) + o["nbfc_central"]
    o["cost_contingency"] = o["_contingency"] * (o["direct"] + o["servicing"] + o["acquisition"] + cen_ex)
    o["central"] = cen_ex + o["cost_contingency"]
    o["ebitda"] = o["cm3"] - o["central"]
    o["ebit"] = o["ebitda"] - o["depreciation"]
    o["opex"] = o["direct"] + o["servicing"] + o["acquisition"] + o["central"]
    tr = C.treasury(o, seed_size=seed_amt, rounds=rds)
    assert np.allclose(tr["ebit_plan"], o["ebit"], rtol=1e-12, atol=1e-6)
    o.update(tr)
    o["burn"] = -(o["cf_operating"] + o["cf_investing"] + o["cf_borrowings"])
    return o


def lenses(o, m=60, d=0):
    """The three lenses at month m: (1) 20 x ARR (fee + NII + processing), (2) 0.45 x AUM, (3) 3 x NBFC equity + 20 x fee ARR."""
    arr = 12 * float(o["revenue"][d, m - 1])
    fee_arr = 12 * float(o.get("fee_revenue", o["revenue"])[d, m - 1])
    eq = float(o["nbfc_equity"][d, m - 1]) if "nbfc_equity" in o else 0.0
    return {"ARR": arr, "Fee ARR": fee_arr, "AUM": float(o["fund_end"][d, m - 1]), "NBFC equity": eq,
            "Lens 1 (20 x ARR)": 20 * arr, "Lens 2 (0.45 x AUM)": 0.45 * float(o["fund_end"][d, m - 1]),
            "Lens 3 (3 x NBFC equity + 20 x fee ARR)": 3 * eq + 20 * fee_arr}

import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-sandeeparora-cortadoBE/96e5789c-001e-4572-b8e8-224696a0b756/scratchpad/analyst")
from a4_costs import run, p
import online_plan as op
R = {"r12":0.2415,"r3":0.52}
cases = [
 ("ticket 58.5k + r12 24%", dict(ov={"ticket":58522.0, **R})),
 ("ticket 58.5k + reach 1", dict(ov={"ticket":58522.0}, reach=1.0)),
 ("ticket 25k + reach 1", dict(ov={"ticket":25000.0}, reach=1.0)),
 ("r12 24% + reach 1", dict(ov=R, reach=1.0)),
 ("debit Rs2 (+tech4) + reach 1", dict(tech=44, reach=1.0)),
 ("debit Rs2 (+tech4) + ticket 58.5k", dict(ov={"ticket":58522.0}, tech=44)),
 ("debit Rs2 (+tech4) + r12 24%", dict(ov=R, tech=44)),
 ("weekly debit Rs2 + ticket 58.5k + r12 24%", dict(ov={"ticket":58522.0, **R}, tech=12)),
 ("apply 10% + ticket 58.5k", dict(ov={**op.loan_mix(0.10), "ticket":58522.0})),
 ("apply 10% + ticket 58.5k + r12 24%", dict(ov={**op.loan_mix(0.10), "ticket":58522.0, **R})),
 ("apply 3.6% + ticket 58.5k + r12 24% (review anchors)", dict(ov={**op.loan_mix(0.036), "ticket":58522.0, **R})),
 ("CAC 600 + ticket 58.5k + r12 24%", dict(ov={"ticket":58522.0, **R}, cac=600.0)),
 ("CAC 600 + reach 1", dict(cac=600.0, reach=1.0)),
 ("GST-incl + reach 1", dict(gst=1.18, reach=1.0)),
 ("offers from age 7, savers only", dict(ov={"marketplace_from":7}, reach=1.0)),
 ("offers from age 7, savers only, ticket 58.5k", dict(ov={"marketplace_from":7, "ticket":58522.0}, reach=1.0)),
]
for n, kw in cases: p(n, run(**kw))

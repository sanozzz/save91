from update_inputs import v
UPDATES = {"inputs.csv": {
    "cost_notice": v(0.115, 0.0, 0.0, "regulation + benchmark", "REG-049, REG-072", "2026-09-30",
                     "The statutory 24h pre-debit notice is sent by the worker's bank or UPI app, not by us. Bear case: we also send our own WhatsApp reminder (Rs 0.115 + GST)."),
    "cost_rewards": v(3, 0, 0, "regulation", "REG-082, REG-083", "2026-09-30",
                      "Fund distributors may not attract investors with rebates, gifts or cashback, and insurance rebates are banned. So no streak cashback. Bear case: Rs 3/month of non-cash or non-fund engagement rewards (legal opinion needed)."),
}}

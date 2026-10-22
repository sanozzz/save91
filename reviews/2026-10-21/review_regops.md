# Regulation and operations review: Save91 / SaveMore, online plan v4 (21 Oct 2026)

**Angle:** compliance and operations lead advising a VC: can this legally run in India, and what will it really take?
**Read:** `research/regulatory_map.md`, `regulation_rails.csv` (REG-001–090), `regulation_summary.md`; research rows XL-, XF-, TC-, XO-; `model/online_plan.py`, `model/cohort_engine.py`; `online/Online_model_v4.html` ("v4 p.N"), `ltv/LTV_CAC_deck.html` ("LTV p.N"), `seed/Seed_Plan_investor.html` ("Seed p.N"); both earlier reviews.
**Conventions:** "[REG-xxx]" = checked in the folder's research. "**GK, to verify**" = my general knowledge, not checked here; counsel should confirm. "est." = my estimate.
**Correction to the brief:** the model's one-off compliance cost is **₹1.25 lakh**, not ₹12.5 lakh (`online_plan.py` line 214; Seed p.9).

## Summary

The design is lawful and well chosen: a fund distributor that never touches money, orders through an exchange platform, units in the saver's own name, and a referral partner for loans with no credit risk. Four things as written do not comply or are unchecked, and each touches the core product or the biggest revenue line:

1. **P1:** loan offers to KYC'd users who never save (about ₹750 of the ₹1,845 LTV) need a separate, optional consent; the plan assumes everyone gets offers.
2. **P1:** the insurance line credits us with 75% of a broker's commission, which an unlicensed company cannot lawfully be paid (GK, to verify).
3. **P1:** the core product is described as costing the saver nothing and as "withdraw any day", while it is 80% equity in regular plans, sold to savers who think it is a wallet.
4. **P1:** the daily-SIP plumbing is unconfirmed: ₹100 split 80/20 is ₹80 and ₹20 per scheme, below the usual ₹100 daily minimum, and the folder never shows the exchange platform supports daily UPI SIPs.

Behind these: compliance has no named owner in the seed and is thinly budgeted throughout.

---

## 1. Mutual fund distribution (SEBI / AMFI)

**The plan:** own ARN "to be registered" (LTV p.8); NISM for the two founders only (Seed p.5); orders through BSE StAR MF, money from the saver's bank to the exchange's clearing house to the fund house (v4 p.4); one UPI mandate, ₹100 a day, 80/20; trail of 0.75% equity and 0.35% debt, so regular plans; "we charge the saver nothing" (v4 p.4); "Withdraw any day" (v4 p.3).

**MF-1 (P1): Conduct and disclosure on the core product.**
- *Where:* v4 p.2–4.
- *Problem:* "we charge the saver nothing (the trail comes from the fund's own expense ratio)". A regular plan costs the saver about 0.5–1% a year more than direct (v4 status, F24; REG-039). Savers think the product is "a wallet they save into and then borrow from" (v4 p.2), yet 80% is equity, and equity schemes commonly charge about 1% to redeem within 12 months (GK, to verify per scheme). A daily earner withdrawing in an emergency pays a charge the app said did not exist.
- *Rules:* distributors must disclose commission and must not mislead (GK, to verify the circular); no rebates or gifts [REG-082].
- *Why P1:* this is where enforcement, press and complaint volume start.
- *Fix:* write "Regular plan: about X% a year more than direct; this is how we are paid". Choose nil or low exit-load schemes, or a liquid/arbitrage fund for the first months. Show the risk-o-meter and ask basic suitability questions. Never use "wallet", "savings account" or "like an FD".

**MF-2 (P1, launch gate): Daily-SIP plumbing.**
- *Where:* v4 p.3; Seed p.3, p.5.
- *Problem:* ₹80 and ₹20 a day sit below the usual ₹100 daily minimum per scheme [REG-043]. The folder documents only that distributors pay no fee on BSE StAR MF (XB-01, TC-12), not that it supports daily SIPs or one UPI mandate across two schemes (GK, to verify).
- *If the team falls back to its own payment aggregator (REG-050 cost rows):* money passes through an app-contracted account, which REG-066 and REG-081 bar (and SEBI's 2021 no-pooling rule for distributors, GK, to verify). Debits at ₹2–5 each would cost ₹40–100 a month per saver, against about ₹7 a month of trail in year 1.
- *Fix:* in month 1, get written confirmation from BSE and three fund houses on frequency, per-scheme minimums and mandate structure. Otherwise redesign: equity four days and debt one, or one hybrid scheme. Do not start building release 1 until this is settled.

**MF-3 (P2): Everyone who sells must be certified.**
- *Problem:* only the founders are budgeted for NISM (Seed p.5). The folder's own note says "Anyone who explains or sells funds needs NISM V-A certification and an EUIN [REG-036, REG-037]" (`research/marketing_ideas.md`). That covers doorstep agents, who "sign savers up and set the UPI mandate" (v4 p.3), and support staff who explain schemes.
- *Cost and time:* about ₹3,500 a person [REG-036, 037], plus 2–4 weeks of study before an agent can start (est.), repeated at 30% agent churn (`AGENT_CHURN`).
- *Also:* an assisted sale must quote the agent's EUIN; marking it "execution-only" would be false (GK, to verify).

**MF-4 (P2): KYC in practice.**
- *Rules:* "KYC Validated" status needs fresh Aadhaar-based KYC [REG-044]. A distributor needs a licensed partner for Aadhaar e-KYC and KRA access (regulatory map, e-KYC row).
- *Problem:* a PAN not linked to Aadhaar puts KYC on hold (GK, to verify). Name mismatches between PAN, Aadhaar and the bank account fail the bank check. The half of sign-ups assumed to finish KYC (`KYC_SHARE`) is unmeasured, and every exception falls to one ops person.
- *Fix:* pick the KYC partner in month 1, measure completion in the beta, and budget about ₹100 a video KYC as a fallback [REG summary §2].

**MF-5 (P3): Choti SIP income cannot be earned.** The model counts ₹7 a saver (LTV p.23, 25), but the Choti SIP is monthly only, for first-time investors only, and any other SIP disqualifies the investor [REG-032, 033]. The daily SIP is another SIP. Remove the line.

**MF-6 (P3): Stay a distributor, not an adviser.** The "AI money coach" and "why this fund, in one sentence" (v4 p.2–3) are fine if the guidance comes only with the sale. Do not turn it into a paid service or use the word "adviser" (GK, to verify). The 2026 MF Regulations push trail down [REG-040].

## 2. Digital lending (RBI)

**LN-1 (P2): Wrong label, and an unfunded "next round" step.**
- *Where:* v4 A5 p.18 and Seed p.5: "With the next round: become a lending service provider… first-loss cover capped at 5%".
- *Problem:* an app that shows lenders' offers and takes applications is a lending service provider (LSP) from its first sourced loan [REG-001, 011, 016]. Its duties start in month 7:
  - each lender lists the app and reports it to RBI [REG-016];
  - fees come only from the lender [REG-011];
  - the lender gives a Key Facts Statement with the APR [REG-012];
  - fees are clawed back when a borrower cancels in the cooling-off period [REG-013];
  - the app shows all matching offers, ranked only on a disclosed metric [REG-014];
  - it keeps minimal data on Indian servers and cannot read contacts or media [REG-015];
  - a named grievance officer [REG-016].
- *The first-loss cover is unfunded:* it must be posted as cash, a lien-marked FD or a bank guarantee, up to 5% of disbursals [REG-003, 005]. Re-running `online_plan.py`, personal and business loans reach ₹799 crore in year 5. That locks about ₹40 crore per yearly book for the loan tenor, more than the whole $2.5M plan.
- *Fix:* rewrite A5. Budget each lender's due diligence (security audit, policies, grievance officer). Drop the first-loss cover as a lever unless the capital comes with it.

**LN-2 (P2): Rules for this segment.** Any loan without collateral to a household earning up to ₹3 lakh a year is a microfinance loan, with repayments capped at 50% of income [REG-077] (reported industry guardrails add a ₹2 lakh unsecured cap, unverified). A draft rule would ceiling APRs on loans up to ₹50,000 [REG-078]. Unsecured loans carry a 125% risk weight [REG-075, 076]. Many ₹100-a-day savers sit near ₹3 lakh, which limits the ₹1.5 lakh business ticket and the 30% approval rate. Add these rules to diligence question Q1.

**LN-3 (P2): Clawbacks are under-priced.** The model takes back 2.5% of payouts (LTV p.10). DSA contracts take back payouts when a loan "closes or defaults within 6 months" (XL-47), and in this segment about a third of borrowers miss a payment (XL-36). Model the clawback from contract terms.

**LN-4 (P2): Loan against savings, the overdraft idea and the "wallet-like view"** (v4 p.2–3).
- Only the lender lends, against a lien on the units [REG-028: banks up to 75% of equity units, 85% of debt units].
- Fintech loans against funds start at ₹25,000 and need ₹50,000 invested (TC-31), so most savers are ineligible for 2+ years.
- Revolving lines cannot carry first-loss cover [REG-007], and credit lines on UPI are for banks and small finance banks only [REG-074].
- "Wallet" invites questions about prepaid-wallet licensing (GK, to verify) and sits close to the deposits ban [REG-081].
- *Fix:* call it "your fund balance". Keep it out of revenue, as the model already does.

**LN-5 (P3): Loan timing.** The model offers loans from a saver's first month (LTV p.6; `marketplace_from` = 1), but the first lender arrives in company month 7 (Seed p.3). The year-1 money is small (₹0.07 crore), but it contradicts "save 6 months, see your loan offer" (v4 p.2).

## 3. Insurance (IRDAI)

**IN-1 (P1): The broker revenue share.**
- *Where:* `cohort_engine.py` `ins_partner_share` = 0.75; LTV p.22 ("Partners' licences"); v4 A5 ("our own licence later").
- *Rule:* pay for soliciting or procuring insurance may go only to licensed agents and intermediaries (GK, to verify: Insurance Act 1938 s.40), and IRDAI's outsourcing rules bar volume-linked payments (GK, to verify). A broker passing 75% of its commission to an unlicensed app is the kind of arrangement regulators have acted against. Rebates are banned [REG-083].
- *What staff and agents may do:* nothing that counts as soliciting or explaining policies, unless each person is certified as a POSP under the broker (GK, to verify). POSP pay goes to the person, not to us [REG-057].
- *Fix, one of:*
  - (a) apply now for our own registration: a corporate agent [REG-059: about ₹35,500 in fees; a trained Principal Officer; 3–6 months], an insurance marketing firm [REG-088], or the draft single distribution licence once final [REG-057: ₹10 lakh capital];
  - (b) take only a fixed fee not linked to volume, and let the broker do the selling.
- *Money at stake:* ₹76 of ₹1,972 revenue a saver (LTV p.25). The fix is cheap; the exposure is the partner's licence and our name.

**IN-2 (P3): Draft caps already modelled.** The model uses the draft commission caps [REG-054, 055]. The 25% partner share comes on top of them.

## 4. Data protection (DPDP Act)

**DP-1 (P1): Loan reach to users who never save.**
- *Where:* LTV p.3 ("about ₹750 of the ₹1,845"); LTV p.9 ("One who never saves stays reachable as long as savers do").
- *Rules:*
  - today, IT Act s.43A, the SPDI Rules (financial data is sensitive) and s.72A [REG-085];
  - from 13 May 2027, about month 6–7 of the plan [REG-084], DPDP consent must be "free, specific, informed, unconditional… limited to the specified purpose" [REG-085].
- *My reading (GK, to verify):* the savings service cannot be made conditional on accepting loan marketing. Data must be deleted once its purpose ends or consent is withdrawn. KRA and CKYC records fetched for fund KYC are for KYC only, and Aadhaar data stays in a vault.
- *Also required:* sharing with each lender needs explicit consent, an audit trail and minimal data [REG-015]. Marketing SMS needs registration and consent [REG-073; REG-086 note].
- *So:* 2.5 reach per saver is a ceiling. Real reach = KYC'd users × opt-in rate × how long consent lasts.
- *Fix:* use a separate, unticked "offers from partner lenders" consent. Measure the opt-in rate in the beta, and restate the LTV at that rate (at a reach of 1.0, v4 status shows 2.43×). Ask again after 12 months of inactivity.

**DP-2 (P2): The savings-record score** (v4 p.3, release 4). Sharing it with any lender needs explicit consent. Better: let the lender fetch fund holdings itself through an Account Aggregator, as the data user [REG-070]. A score that uses lenders' repayment data raises credit-information-law questions (GK, to verify).

**DP-3 (P3): The founders' no-reuse rule.** The folder confirms the old borrower list cannot be reused [REG-086]. Using aggregate past-lending figures is fine (XF-24). Write the rule into a board policy and the shareholders' agreement, and keep no record-level data in company systems.

**DP-4 (P3): At scale.** A possible "significant data fiduciary" designation (data protection officer, audits) and 6-hour cyber-incident reporting (both GK, to verify). Budget security audits.

## 5. Doorstep agents

**DA-1 (P2): Decide no cash.**
- *Contradiction:* v4 p.3 says agents "never handle cash", but Seed p.5 and v4 A5 still plan an opinion on "any cash at the doorstep". The agent cost also carries ₹1,000 a month of "cash cover", defined in the code as "fidelity and cash-in-transit insurance" (`online_plan.py` line 113; `cohort_engine.py`).
- *Rules:* cash breaks the own-account rule [REG-066] and the deposits ban [REG-081], and distributors cannot accept cash (GK, to verify). The only lawful cash route is a bank's business correspondent.
- *Fix:* make "no cash, ever" a sacking offence in the agent contract, turn the line into fidelity cover, and drop the opinion.

**DA-2 (P2): Certification for each product an agent discusses.** Funds: NISM V-A and an EUIN. Insurance: POSP. Loans: the lender's code of conduct and background checks. Agents must be our employees or hold their own ARN (both GK, to verify).

**DA-3 (P2): Mis-selling and fraud.** Paying incentives on 100 sign-ups a month invites:
- fake sign-ups;
- agents setting mandates on the saver's phone, when only the saver may authenticate the first debit [REG-049];
- steering savers to particular loans.

*Fix:* pay incentives on savers still saving at month 3. Call back every pilot sign-up, geotag sign-ups, require the saver's own authentication, and use mystery shoppers.

## 6. Operations

**OP-1 (P2): Support and grievance load.**
- *Seed:* one ops person from month 4 (Seed p.6) faces about 13,900 active savers and about 48,600 KYC'd users by month 18, roughly 2.8 lakh debits a month.
- *Model gap:* support is costed only on active savers (`cost_support` = still saving × ₹5). The extra 1.5 KYC'd users per saver who see loan offers cost nothing to serve.
- *Channels needed:* fund houses; the lender's route to the RBI Ombudsman through our grievance officer [REG-016]; the broker's IRDAI channel; and data-protection grievances (GK).
- *Fix:* name a grievance officer at launch, and cost support on all KYC'd users.

**OP-2 (P2): No fraud budget.** v3's fraud provision was tied to cash (`tables/base_inputs.csv`), and v4 removed it with nothing in its place. Risks include third-party-account mandates (name-match the bank check), synthetic identities among never-savers (loan fraud and clawbacks) and agent fraud. Budget ₹2–5 lakh a year plus fidelity cover (est.).

**OP-3 (P2): Compliance staffing and budget, the most likely cause of delay.**
- *The plan:*
  - In the seed, the CEO owns compliance on top of growth, partners, fund-raising and the pilot (Seed p.6), with ₹1.25 lakh once plus ₹10 lakh a year.
  - After the round, there is one compliance person at every scale, even at 27 lakh active savers on the grow-fast path (`headcount()`; v4 A7).
- *My estimate (est.):*
  - Seed: ₹12–23 lakh one-off (4–5 legal opinions and documents) plus ₹15–30 lakh a year (a part-time compliance officer, security audits, CA and company-secretary work, insurance cover). That is ₹20–40 lakh ($20–40k) above budget, which the $162k contingency can absorb.
  - Year 5 of the profitable path: 3–5 people, about ₹60–100 lakh a year.

**OP-4 (P2): Marketing rules constrain the ₹450 cost to win** ("app, referrals and performance ads", v4 p.3).
- No gifts or rebates [REG-082].
- No inducement to stop a mandate port [REG-046].
- SMS registration [REG-073].
- Fund advertising rules, and SEBI's bar on its regulated entities and their agents working with unregistered finfluencers (GK, to verify).

**OP-5 (P2): Timeline.**
- Launch in month 4 is tight; my estimate is month 5–6. NISM then the ARN take 4–8 weeks, KYC integration 4–8 weeks, and MF-2 comes first.
- Loans in month 7 need a lender's due diligence of 2–6 months (est.).
- Our own insurance licence adds 3–6 months [REG-059].

**Other products (P3):**
- Digital gold (₹12 a saver, LTV p.25) is unregulated [REG-024–026], and the folder's own row says the evidence "supports the 'no digital gold at launch' choice" [REG-026]. Use a gold fund under the ARN instead.
- Banks may pay for deposits only to DSAs, DMAs or correspondents (TC-24), so each FD partner needs an agreement. An FD-backed card must come from the bank holding the FD [REG-029, 087].
- NPS needs a PFRDA route, and bill payments a Bharat Connect operator (both GK, to verify).

## 7. Licences, registrations and partner contracts

Times are estimates unless cited.

| Item | Holder | Time | Cost | In budget and timeline? |
|---|---|---|---|---|
| Company, GST, SMS registration | Company | 2–4 wks | ~₹0.5 lakh; SMS ₹5,900 + GST [REG-073] | Yes |
| Corporate ARN | Company | 2–6 wks after NISM [REG-036, unverified] | ₹40,000 + GST; renewal ₹20,000 every 3 yrs [REG-036] | Yes |
| NISM V-A + EUIN, everyone who sells or explains | Each person | 2–4 wks | ~₹3,500 each [REG-036, 037] | **Founders only** |
| BSE StAR MF; daily UPI SIP confirmed | Company | 2–4 wks | Nil (XB-01) | Yes; **support unconfirmed** |
| 3–5 fund-house empanelments | Company | 1–4 wks each | Nil | Yes |
| KYC partner (KRA, Aadhaar e-KYC, CKYC, video) | Vendor | 4–8 wks | ₹36–65 a KYC [REG summary] | Yes (₹40) |
| Legal opinions (fund flow, LSP, insurance, consent, agents) | Counsel | 4–8 wks | ₹8–15 lakh | **Partly** |
| Data protection programme, security audit, incident reporting | Company | Ongoing | ₹5–10 lakh a yr | **No line** |
| LSP agreement per lender; app reported; grievance officer [REG-016] | Lender + company | 2–6 months each | ₹0.5–1.5 lakh legal each | Timeline yes; **budget no** |
| First-loss cover (optional) | Company | With LSP contract | ≤5% of disbursals [REG-003, 005] | No; keep it out |
| Own insurance registration | Company | 3–6 months [REG-059] | ~₹35,500 + Principal Officer ₹12–18 lakh a yr | **No (deferred)** |
| Broker referral agreement (interim) | Broker | 1–2 months | Fixed fee (to verify) | Yes; **wrong structure** |
| POSP certification for agents | Each person | 1–2 wks | Small | **No** |
| Card issuer DSA agreement [REG-087] | Bank | 2–4 months | Nil | Yes |
| FD sourcing agreements (TC-24) | Bank | 2–4 months | Nil | **Not scheduled** |
| NPS and bill-payment routes | Partner | To verify | Small | **Not scheduled** |
| Fidelity, cyber and indemnity cover | Company | Weeks | ₹2–4 lakh a yr | Partly |
| Trademark check, "Save91 / SaveMore" | Company | 12–24 months to register | ₹0.2–0.5 lakh | **No** |

## 8. Verdict

**Can it run as designed?** Mostly yes, with changes. Three parts are lawful as designed: distribution without holding money, loan referrals without credit risk, and UPI-only doorstep agents. Five things must change:
- the insurance revenue share;
- the consent design behind loan reach;
- how the core product is described to savers;
- confirmed daily-SIP plumbing;
- a named and funded compliance function.

None needs an RBI licence or new capital. The consent opt-in rate and the clawback terms will lower the loan line; the rest costs little.

**The five things to do first:**
1. **Month 1: get the plumbing in writing.** BSE StAR MF and three fund houses confirm in writing that a ₹100 daily SIP split across two schemes runs on one UPI mandate. If not, redesign before building.
2. **Rebuild consent and restate reach.** Make lender offers a separate opt-in, measure the opt-in rate in the beta, re-run the LTV at that rate, and get a data-protection and LSP opinion.
3. **Fix insurance now.** Apply for our own registration (corporate agent or insurance marketing firm), or model a fixed referral fee. Take no share of a broker's commission, and let no one sell without POSP certification.
4. **Describe the product truthfully.** Disclose the regular-plan cost, exit loads and equity risk, and drop "wallet". Choose low-exit-load schemes. Pay agents on savers still saving, and make "no cash" a written rule.
5. **Name and fund compliance.** Hire a part-time compliance officer from month 1 who is also the grievance officer. Certify everyone who sells, and move ₹20–40 lakh from the contingency. Correct v4 A5: the company is an LSP from month 7, and the first-loss cover is unfunded.

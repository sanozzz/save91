# Daily SIP: questions for BSE StAR MF and the fund houses

**Why we are sending these.** Our plan collects ₹100 a day by UPI Autopay into mutual funds in the saver's own name, 80% equity and 20% debt.
- **The cost of each debit decides the case.** These are the 24 Oct working numbers (₹70k first loans, a market-level loan funnel, 35% still saving at 12 months), not yet rebuilt:
  - a daily SIP through BSE StAR MF at no cost to us: one saver is worth **0.78×** its cost to win;
  - we pay ₹2 a debit, weekly: **0.45×**;
  - we pay ₹2 a debit, daily: **negative**.
- **Updated 24 Oct:** most fund houses' daily minimum is ₹100 per scheme (research TC-45), so ₹80 + ₹20 won't fit. The likely fix is one hybrid or multi-asset scheme taking the whole ₹100. The questions below now ask about that.
- **What we need:** a written answer to each question below. A verbal "should be fine" is not enough.

**Send to:**
- **Email 1:** BSE StAR MF's distributor onboarding or business development team.
- **Email 2:** the distributor relations team at three or more fund houses that already offer daily SIPs. Our research lists:
  - Axis, ICICI Prudential, Tata, HDFC, UTI and LIC MF (REG-043);
  - SBI MF's daily Jan Nivesh SIP (NG-033);
  - The Wealth Company, which has offered a ₹100 daily SIP on six schemes, including Multi Asset and Flexi Cap, since Jan 2026 (TC-45).

  Skip JM, which raised a daily minimum to ₹500.

Fill in the [brackets] before sending.

---

## Email 1: BSE StAR MF

**Subject:** Daily SIPs of ₹100 through StAR MF for a new distributor: six questions

Dear StAR MF team,

We are building a savings app for India's self-employed: shopkeepers, vendors and small-business owners. They will save ₹100 a day into mutual funds held in their own name. We are registering as a corporate mutual fund distributor [ARN status: applied on / to apply by date]. We plan to place every order through BSE StAR MF, so that money moves from the saver's bank to the clearing house to the fund house and never through us.

Before we build, we would be grateful for written answers to six questions:

1. **Daily frequency.** Does StAR MF support a daily SIP placed by a distributor, with the instalment collected by a UPI Autopay mandate on daily frequency? Which order type (XSIP or other) and which API?
2. **One mandate, two schemes.** Can a single UPI Autopay mandate fund two daily SIPs for the same investor, for example ₹80 into an equity scheme and ₹20 into a debt scheme? Or does each SIP need its own mandate, or one mandate for at least the combined amount? If the simplest route is one daily SIP of ₹100 into a single hybrid scheme, please say so.
3. **Minimum per scheme.** Is the minimum daily instalment set by each fund house, or does StAR MF apply a floor? Would ₹80 and ₹20 be accepted, or is ₹100 per scheme the practical minimum?
4. **Charges.** Your XSIP page says the facility is free to distributors. We understand fund houses pay StAR MF a fee per transaction, agreed with each fund house. Does that fee apply to every daily instalment? Is there any charge to us, the distributor, for registering a mandate, for each debit, or for a failed debit?
5. **Failed debits.** What happens when a daily debit fails (for example, insufficient balance)? Is it retried? Does the SIP continue the next day, and after how many failures does it cancel?
6. **Onboarding.** What does a new corporate distributor need to go live on StAR MF (documents, API access, testing), and how long does it usually take?

If there is a better person or team for these questions, please point us to them.

Thank you,
[Sandeep Arora]
Co-founder and CPTO, [company name] (Save91 is our working name)
[phone] · [email]

---

## Email 2: fund houses (one per fund house)

**Subject:** Daily SIPs of ₹100 from a new distributor serving self-employed savers

Dear [fund house] distributor relations team,

We are building a savings app for India's self-employed: shopkeepers, vendors and small-business owners. Each saver puts ₹100 a day into mutual funds in their own name, by UPI Autopay, with orders placed through BSE StAR MF. We are registering as a corporate mutual fund distributor [ARN status]. We would like to offer [scheme names: one hybrid or multi-asset scheme, or one equity scheme and one debt scheme] to our savers.

Could you confirm in writing:

1. **Daily SIP through StAR MF.** Do you accept daily SIP instalments placed by a distributor through BSE StAR MF? Which of your schemes allow a daily frequency?
2. **Minimum.** What is the minimum daily instalment per scheme? Would you accept ₹80 a day into an equity scheme and ₹20 a day into a debt scheme? If ₹100 per scheme is the minimum, would you accept ₹100 a day into one aggressive hybrid or multi-asset scheme instead?
3. **Exit loads.** What exit load applies to those schemes if a saver redeems within the first 12 months? Our savers may need money in an emergency, so we would choose schemes with nil or low exit loads.
4. **Trail.** What trail commission does a distributor receive on the regular plan of those schemes? Our plan assumes about 0.75% a year on equity and 0.35% on debt. What is it on your hybrid or multi-asset scheme?
5. **Small daily orders.** Is there any limit or concern on your side with a high volume of small daily orders (₹100 each)? Does the per-transaction fee you pay BSE StAR MF make you limit daily SIPs placed through the exchange?
6. **Empanelment.** What do you need from a new corporate distributor to empanel us, and how long does it take?

Thank you,
[Sandeep Arora]
Co-founder and CPTO, [company name] (Save91 is our working name)
[phone] · [email]

---

## What we do with the answers

| Answer | Model change | One saver |
|---|---|---|
| Daily SIP works on one mandate, no charge to us, ₹80 + ₹20 accepted | Daily debits at ₹0 | 0.78× (24 Oct working case) |
| Daily works only at ₹100 per scheme | One hybrid scheme at ₹100 a day; the 80/20 sits inside the fund | about 0.78×, if the hybrid trail is close to 0.75% |
| Daily not possible through StAR MF | Weekly debits through StAR MF, at ₹0 to us if confirmed | about the same at ₹0; the product becomes weekly |
| A per-debit charge to us | Debit cost at the quoted rate | ₹2 weekly: 0.45×; ₹2 daily: negative |
| Only through our own payment gateway | Not allowed: the money would pass through our account (REG-066, REG-081) | — |

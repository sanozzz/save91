"""Builds final/: the current documents under plain names, and final/README.md with the headline numbers read from others/tables/.

The PDFs are copies of what the builders write (others/online/, ltv/, seed/, memo/), so after rebuilding any of them run:
    python final/make_final.py            copy the documents and rewrite the README
    python final/make_final.py --check    exit 1 if a copy differs from its source or the README is out of date
"""
import csv
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "final"
SRC = ROOT / "others"                  # everything behind final/: models, tables, research, deck builders, reviews, archive
T = SRC / "tables"

DOCS = [  # (name in final/, source, what it is)
    ("1_Online_business_case.pdf", "online/Online_business_case.pdf",
     "The short read, rebased 24 Oct on the founders' market and measured inputs: one saver on the main case, the odds, what it takes "
     "(the ladder), the company's financials, and what the seed measures."),
    ("2_Online_plan_v4.pdf", "online/Online_model_v4.pdf",
     "The full online-first plan on the main case: the customer and product, one saver, the loan funnel, the odds, what it takes, "
     "the financials, and an appendix with every input, year-by-year tables, the Monte Carlo, the levers, the input audit and the spreadsheet check."),
    ("3_LTV_CAC_one_saver.pdf", "ltv/LTV_CAC_simple.pdf",
     "What one saver is worth over 5 and 8 years, and how much of it is cross-selling: the bridge from last week's 1.75×, the inputs "
     "now used, the odds, what it takes, the company, and the four facts that decide it."),
    ("4_Seed_plan_0.5M.pdf", "seed/Seed_Plan_investor.pdf",
     "The $0.5M seed: customers (1 lakh sign-ups), product and team for 24 months, the reserve, and what the seed must prove."),
    ("5_Bachatt_teardown_memo.pdf", "memo/Bachatt_teardown_memo.pdf",
     "Context: what Bachatt has built, what is still vision, and where the market is open (memo, 19 Oct)."),
]
SHEETS = [  # (name, link, what it holds)
    ("Save4More || Financial Model", "https://docs.google.com/spreadsheets/d/1gDfeyy2YSmZt79-KTHM2wHdsanNyAVyTFQl7W9zQjMM",
     "The company, live, on the main case. Start at the 'Start here' tab; change the blue cells on 'v4 Inputs' and every v4 tab recalculates. "
     "'v4 Monte Carlo' has the LTV/CAC Monte Carlo and what it takes. The older offline tabs are hidden (View > Hidden sheets)."),
    ("SaveMore || LTVCAC", "https://docs.google.com/spreadsheets/d/1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4",
     "One saver, live, on the main case: every input with its source (and its range where still uncertain), the waterfall, the 1,000 futures of the "
     "LTV/CAC Monte Carlo, and a Projector tab that answers questions about them."),
]
OPEN = [  # edited by hand as items close
    "Debits at ₹0 to us are UNCONFIRMED: BSE StAR MF and the fund houses must confirm in writing a daily ₹100 SIP on one mandate, probably one "
    "hybrid fund since most daily minimums are ₹100 a scheme (questions: `others/outreach/2026-10-22_daily_sip_questions.md`). If we pay ₹2 a "
    "weekly debit, money needed rises to $11.7M.",
    "Bachatt's AVERAGE daily amount (₹100 is the minimum; ₹126 a day takes one saver to 1×) and its exact share still saving at 12 months "
    "(30–40% given; 41% takes one saver to 1×).",
    "The 0.75% equity fund fee in writing from a fund house (0.5% raises money needed to $10.6M).",
    "Insurance: a fixed referral fee through a broker, to be agreed. The plan counts it as 0. Recharge, bills, FD and NPS are not in the launch app.",
    "Founder bios: later, when a pitch deck is built.",
]
BACKGROUND = [  # linked, not copied: useful, but not the current numbers
    ("others/reviews/2026-10-21/CRITICAL_REVIEW.pdf", "The four-angle critical review (investment, analyst, story, regulation). Its numbers "
     "are from before the 22 Oct fixes and the loan-size change; what was fixed is in INVESTMENT_REVIEW_v4_status.md."),
    ("others/reviews/INVESTMENT_REVIEW_v4_status.md", "Each point of the earlier investment review, with its status in the current plan."),
    ("others/tables/online_inputs_audit.csv", "Every input against its source, with a verdict (matches, partly, judgement, target)."),
    ("others/research/", "The evidence: one row per source, with IDs the decks cite."),
    ("others/ltv/LTV_CAC_deck.pdf", "The detailed LTV/CAC deck (32 pages): every assumption with its range and sources. Older than the "
     "24 Oct rebase; the current numbers are in the decks in final/."),
    ("others/reviews/2026-10-24_rebase/BRIEF.md", "The 24 Oct rebase: each founders' decision, its source, and every headline number with its table."),
    ("others/README.md", "The map of everything behind final/."),
]


def rows(name):
    with (T / name).open() as f:
        return list(csv.DictReader(f))


def pick(name, key, value):
    return next(r for r in rows(name) if r[key] == value)


def headline():
    lad = {r["rung"]: r for r in rows("ltv_ladder.csv")}
    od = {r["measure"]: r for r in rows("ltv_odds_summary.csv")}
    sp = {(r["case"], r["years"]): r for r in rows("ltv_saver_split.csv")}
    m, two, three = lad["Main case"], lad.get("2×"), lad.get("3×")
    s5, s8 = sp[("Main case", "5y")], sp[("Main case", "8y")]
    pm = lambda r: f"month {int(float(r['EBITDA positive from month']))}" if float(r["EBITDA positive from month"]) <= 96 else "not by year 8"
    f = lambda r, k: float(r[k])
    return [
        f"Cross-selling alone (loans and cards) brings ₹{f(s5, 'cross-sell'):,.0f} per saver in five years and ₹{f(s8, 'cross-sell'):,.0f} in eight: "
        f"{f(s5, 'cross-sell / CAC'):.2f}× and {f(s8, 'cross-sell / CAC'):.2f}× of the ₹{f(s5, 'cost to win'):,.0f} it costs to win a saver (₹450 at scale, "
        f"the founders' figure, plus the 10% contingency), and less than the ₹{f(s5, 'serving'):,.0f} / ₹{f(s8, 'serving'):,.0f} it costs to serve "
        f"them ({f(s5, 'cross-sell net of serving / CAC'):.2f}× after serving). With fund fees a saver returns {f(s5, 'LTV/CAC'):.2f}× in five years "
        f"and {f(s8, 'LTV/CAC'):.2f}× in eight and pays back in month {int(f(m, 'saver pays back in month'))}. How long savers keep saving "
        f"(Bachatt's 30–40%) gives {f(od['LTV/CAC, 5 years'], 'P10'):.2f}–{f(od['LTV/CAC, 5 years'], 'P90'):.2f}× at five years in 8 of 10 "
        f"Monte Carlo draws. Debits at ₹0 and the 0.75% equity fund fee are still to be confirmed in writing.",
        (f"The main case: at 20,000 online savers won a month from month 30 the company is not EBITDA-positive by year 8; it needs at least "
         f"${f(m, 'money needed $M'):.1f}M by month 96 and the cash is still falling then." if f(m, "EBITDA positive from month") > 96 else
         f"The main case: at 20,000 online savers won a month from month 30 the company is EBITDA-positive from {pm(m)} and needs "
         f"${f(m, 'money needed $M'):.1f}M."),
        (f"What it takes: 2× (₹{f(two, 'saved a day Rs'):.0f} a day, {f(two, 'still saving at 12 months'):.0%} still saving at a year, loans most of "
         f"the way to our old targets) brings profit in {pm(two)} on ${f(two, 'money needed $M'):.1f}M" if two else "What it takes: see the ladder")
        + (f"; 3× (₹{f(three, 'saved a day Rs'):.0f} a day, {f(three, 'still saving at 12 months'):.0%}) in {pm(three)} on "
           f"${f(three, 'money needed $M'):.1f}M." if three else "."),
    ]


def pages(p):
    try:
        out = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True, check=True).stdout
        return next(int(l.split()[-1]) for l in out.splitlines() if l.startswith("Pages:"))
    except (OSError, subprocess.CalledProcessError, StopIteration):
        return None


def readme():
    L = ["# Save91 / SaveMore: final documents", "",
         f"Built {date.today():%d %b %Y} by `final/make_final.py` from the files and tables in this repo. Do not edit this README by hand; "
         "edit the script and run it again.", "",
         "The plan: savers put away ₹100 a day by UPI into mutual funds in their own name (80% equity, 20% debt). We earn fund fees "
         "and, as a loan marketplace, referral fees from lenders. 9 in 10 savers come online, pan-India; 1 in 10 through doorstep "
         "agents in NCR. The app never holds anyone's money.", "",
         "## The numbers in three lines", ""]
    L += [f"- {s}" for s in headline()]
    L += ["", "Since 24 Oct the founders fixed every input of a saver's value (market figures, Bachatt, or our judgement: ₹70k first loans, "
          "20% apply, 20% approved, 2% lender payout); only retention and the debt fund's fee are still drawn. The decisions and sources are in "
          "`others/reviews/2026-10-24_rebase/BRIEF.md` and `FIXES.md`; the bridge from last week's 1.75× is `others/tables/ltv_bridge.csv`."]
    L += ["", "## Documents", "", "| File | What it is | Pages | Built from |", "|---|---|---|---|"]
    for name, src, what in DOCS:
        L.append(f"| [`{name}`]({name}) | {what} | {pages(SRC / src) or ''} | `others/{src}` |")
    L += ["", "## Live Google Sheets", ""]
    L += [f"- **[{n}]({u})**: {w}" for n, u, w in SHEETS]
    L += ["", "Both sheets are checked against the Python model: the company sheet's formulas are replayed in "
          "`others/model/v4_toy_check.py` (`others/tables/v4_toy_check.csv`), the workbook's in `others/model/ltv_book.py` "
          "(`others/tables/ltv_book_check.csv`).",
          "", "## Open items", ""]
    L += [f"- {s}" for s in OPEN]
    L += ["", "## Background (linked, not copied)", ""]
    L += [f"- [`{p}`](../{p}): {w}" for p, w in BACKGROUND]
    L += ["", "Superseded: [`others/archive/`](../others/archive/README.md) holds the earlier offline street-agent plan (16–18 Oct).",
          "", "## Refreshing this folder", "", "After changing an input, rebuild in this order (from the repo root), then run this script:", "", "```",
          "cd others/model && PYTHONPATH=. python ltv_odds.py && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python ltv_bridge.py && PYTHONPATH=. python ltv_book.py <payload_dir>",
          "cd .. && for b in ltv/build_ltv_deck.py ltv/build_ltv_simple.py online/build_online_v4.py online/build_online_case.py seed/build_seed_plan.py; do PYTHONPATH=model python $b; done",
          "cd .. && python final/make_final.py", "```", "",
          "The sheets are pushed separately (`others/model/v4_gsheet.py`, `v4_toy_check.py`, `v4_ltv_tab.py`, `ltv_book.py`).", ""]
    return "\n".join(L)


def body(text):
    return [l for l in text.splitlines() if not l.startswith("Built ")]


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for name, src, _what in DOCS:
        s, d = SRC / src, OUT / name
        if check:
            if not d.exists() or d.read_bytes() != s.read_bytes():
                stale.append(name)
        else:
            shutil.copyfile(s, d)
    text = readme()
    if check:
        r = OUT / "README.md"
        if not r.exists() or body(r.read_text()) != body(text):
            stale.append("README.md")
        print("final/ is up to date" if not stale else f"final/ is stale: {', '.join(stale)} (run python final/make_final.py)")
        sys.exit(1 if stale else 0)
    (OUT / "README.md").write_text(text)
    print(f"final/: {len(DOCS)} documents copied, README.md written")


if __name__ == "__main__":
    main()

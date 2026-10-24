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
     "The short read: the main case (the LTV/CAC Monte Carlo median), the odds, the company at each LTV/CAC, the financials, and what the seed measures."),
    ("2_Online_plan_v4.pdf", "online/Online_model_v4.pdf",
     "The full online-first plan at our targets (7.7×), not yet re-based on the main case: the saver, the company year by year, the earlier "
     "Monte Carlo, the levers, and an appendix with every input, its source and the input audit."),
    ("3_LTV_CAC_one_saver.pdf", "ltv/LTV_CAC_simple.pdf",
     "What one saver is worth, in ten pages: how one saver makes money at our targets, how each assumption changes the number, the odds, "
     "the company at each LTV/CAC, and the five checks the seed runs."),
    ("4_Seed_plan_0.5M.pdf", "seed/Seed_Plan_investor.pdf",
     "The $0.5M seed: customers (1 lakh sign-ups), product and team for 24 months, the reserve, and what the seed must prove."),
    ("5_Bachatt_teardown_memo.pdf", "memo/Bachatt_teardown_memo.pdf",
     "Context: what Bachatt has built, what is still vision, and where the market is open (memo, 19 Oct)."),
]
SHEETS = [  # (name, link, what it holds)
    ("Save4More || Financial Model", "https://docs.google.com/spreadsheets/d/1gDfeyy2YSmZt79-KTHM2wHdsanNyAVyTFQl7W9zQjMM",
     "The company, live. Start at the 'Start here' tab; change the blue cells on 'v4 Inputs' and every v4 tab recalculates. "
     "The older offline tabs are hidden (View > Hidden sheets)."),
    ("SaveMore || LTVCAC", "https://docs.google.com/spreadsheets/d/1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4",
     "One saver, live: every input, the waterfall, the 1,000 simulated futures, and a Projector tab that answers questions about them."),
]
OPEN = [  # edited by hand as items close
    "BSE StAR MF and the fund houses to confirm a daily SIP on one mandate (questions: `others/outreach/2026-10-22_daily_sip_questions.md`). "
    "Until then the plan pays ₹2 a debit, weekly; at no debit cost the online saver's LTV/CAC rises (see the LTV/CAC deck, 'The tests that matter').",
    "Insurance: a fixed referral fee through a broker, to be agreed. The plan counts it as 0.",
    "Loan sizes (home ₹30 lakh, property ₹25 lakh, personal and business ₹3 lakh) are the founders' numbers of 22 Oct, above what the "
    "research observed; the seed's first lending partner measures them.",
    "Founder bios: later, when a pitch deck is built.",
    "The v4 plan deck (`2_Online_plan_v4.pdf`) and both Google Sheets are still built on our targets (7.7×) and the earlier Monte Carlo; "
    "re-basing them on the main case is the next step.",
]
BACKGROUND = [  # linked, not copied: useful, but not the current numbers
    ("others/reviews/2026-10-21/CRITICAL_REVIEW.pdf", "The four-angle critical review (investment, analyst, story, regulation). Its numbers "
     "are from before the 22 Oct fixes and the loan-size change; what was fixed is in INVESTMENT_REVIEW_v4_status.md."),
    ("others/reviews/INVESTMENT_REVIEW_v4_status.md", "Each point of the earlier investment review, with its status in the current plan."),
    ("others/tables/online_inputs_audit.csv", "Every input against its source, with a verdict (matches, partly, judgement, target)."),
    ("others/research/", "The evidence: one row per source, with IDs the decks cite."),
    ("others/ltv/LTV_CAC_deck.pdf", "The detailed LTV/CAC deck (32 pages): every assumption with its range, sources and the 1,000 simulated futures."),
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
    m, t3, top, mk = lad["Median"], lad["3×"], lad["Our targets"], lad["Today's market"]
    pm = lambda r: f"month {int(float(r['EBITDA positive from month']))}" if float(r["EBITDA positive from month"]) <= 96 else "not by year 8"
    return [
        f"The cost to win is measured: ₹{float(m['LTV Rs']) / float(m['LTV/CAC 5y']):,.0f} an online saver (₹450 plus the 10% contingency; ₹600 in the "
        f"seed). The value of a saver is not: with its ten unmeasured inputs drawn anywhere between today's market and our targets (1,000 random what-ifs), "
        f"the median online saver returns {float(m['LTV/CAC 5y']):.1f}× over five years (1 in 10 below {float(od['LTV/CAC, 5 years']['P10']):.1f}×) and "
        f"pays back in month {int(float(m['saver pays back in month']))}; {float(od['chance LTV/CAC >= 3']['P50']):.0%} of the what-ifs reach 3× and "
        f"{float(od['chance LTV/CAC >= 1']['P50']):.0%} pay back.",
        f"The main case is that median. At 20,000 online savers won a month from month 30 the company is EBITDA-positive from {pm(m)}, needs "
        f"${float(m['money needed $M']):.1f}M in all, and adds up to {'−' if float(m['cumulative EBITDA 8y Rs cr']) < 0 else ''}₹{abs(float(m['cumulative EBITDA 8y Rs cr'])):.0f} crore of EBITDA over eight years.",
        f"The ladder: at 3× profit comes in {pm(t3)} on ${float(t3['money needed $M']):.1f}M; at our targets ({float(top['LTV/CAC 5y']):.1f}×, every loan "
        f"target at once) {pm(top)} on ${float(top['money needed $M']):.1f}M; at today's market ({float(mk['LTV/CAC 5y']):.1f}×) {pm(mk)}.",
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
    L += ["", "Every figure is a plan with targets, not evidence. The targets the seed must prove (from `tables/online_inputs_audit.csv`):", ""]
    L += [f"- {r['input'][0].upper() + r['input'][1:]}: {'₹' if r['unit'].startswith('Rs') else ''}{r['likely_value'].replace('Rs ', '₹')}"
          for r in rows("online_inputs_audit.csv") if r["verdict"] == "target"]
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
          "cd others/model && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python ltv_odds.py && PYTHONPATH=. python online_mc.py && PYTHONPATH=. python ltv_book.py <payload_dir>",
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

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
     "The short read: what the numbers say in the plan, and the five numbers that change them."),
    ("2_Online_plan_v4.pdf", "online/Online_model_v4.pdf",
     "The full online-first plan: the saver, the company year by year, the Monte Carlo, the levers, and an appendix with every "
     "input, its source and the input audit."),
    ("3_LTV_CAC_one_saver.pdf", "ltv/LTV_CAC_deck.pdf",
     "What one saver is worth: the cost to win them, each revenue stream, serving, payback, and the tests that matter."),
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
]
BACKGROUND = [  # linked, not copied: useful, but not the current numbers
    ("others/reviews/2026-10-21/CRITICAL_REVIEW.pdf", "The four-angle critical review (investment, analyst, story, regulation). Its numbers "
     "are from before the 22 Oct fixes and the loan-size change; what was fixed is in INVESTMENT_REVIEW_v4_status.md."),
    ("others/reviews/INVESTMENT_REVIEW_v4_status.md", "Each point of the earlier investment review, with its status in the current plan."),
    ("others/tables/online_inputs_audit.csv", "Every input against its source, with a verdict (matches, partly, judgement, target)."),
    ("others/research/", "The evidence: one row per source, with IDs the decks cite."),
    ("others/README.md", "The map of everything behind final/."),
]


def rows(name):
    with (T / name).open() as f:
        return list(csv.DictReader(f))


def pick(name, key, value):
    return next(r for r in rows(name) if r[key] == value)


def headline():
    on = pick("online_ltv_levers.csv", "case", "The plan")
    door = pick("online_unit.csv", "saver", "Doorstep saver")
    door_x = (float(door["revenue 60 months Rs"]) - float(door["serving 60 months Rs"])) / float(door["cost to win Rs"])
    co = pick("online_levers.csv", "case", "The plan")
    mc = {r["measure"]: r for r in rows("ltv_mc_summary.csv")}
    cmc = pick("online_mc_summary.csv", "plan", "Profitable path")
    return [
        f"One online saver costs ₹{float(on['cost to win Rs']):,.0f} to win (with the 10% contingency) and returns "
        f"{float(on['LTV/CAC 60m']):.1f}× that over five years; it pays back in month {int(float(on['pays back in month']))}. "
        f"A doorstep saver returns {door_x:.1f}×.",
        f"The company, at 20,000 online savers won a month from month 30, is EBITDA-positive from month "
        f"{int(float(co['EBITDA positive from month']))} and needs ${float(co['money needed $M']):.1f}M in all; "
        f"year-5 EBITDA ₹{float(co['Y5 EBITDA Rs cr']):.1f} crore.",
        f"Across 1,000 simulated futures (a stress test, not odds), the online saver's median LTV/CAC is "
        f"{float(mc['Online: LTV/CAC, 5 years']['P50']):.1f}× (1 in 10 below {float(mc['Online: LTV/CAC, 5 years']['P10']):.1f}×); "
        f"{float(mc['share online LTV/CAC >= 3']['P50']):.0%} reach 3×, and the company is profitable by month 60 in "
        f"{float(cmc['chance EBITDA positive by month 60']):.0%}.",
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
         "## The plan in three lines", ""]
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
          "cd others/model && PYTHONPATH=. python online_plan.py && PYTHONPATH=. python online_mc.py && PYTHONPATH=. python ltv_book.py <payload_dir>",
          "cd .. && for b in ltv/build_ltv_deck.py online/build_online_v4.py online/build_online_case.py seed/build_seed_plan.py; do PYTHONPATH=model python $b; done",
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

"""Trace every number on every slide (and in its speaker notes) to a frozen table.

A number is traced when its value appears in deck_numbers.csv, deck_facts.csv
(display or population text), inputs*.csv (any scenario; percentages both ways),
channels.csv, inputs_path.csv or a short list of labels (years, slide numbers,
thresholds named in the brief). Everything else is printed for review.
"""
import csv
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
NUMRE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def nums(text):
    out = []
    for m in NUMRE.finditer(text):
        raw = m.group(0).rstrip(",")
        try:
            out.append((raw, float(raw.replace(",", ""))))
        except ValueError:
            pass
    return out


allowed = set()


def allow(text):
    for _, v in nums(str(text)):
        allowed.add(round(v, 2))


def allow_value(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return
    for x in (f, f * 100, f / 1e7, f / 1e6):
        allowed.add(round(x, 2))
        allowed.add(round(x, 1))
        allowed.add(round(x, 0))


for r in csv.DictReader(open(T / "deck_numbers.csv")):
    allow(r["display"])
for r in csv.DictReader(open(T / "deck_facts.csv")):
    allow(r["display"]); allow(r["population"]); allow(r["source_short"]); allow(r["source_ids"])
for f in ("inputs.csv", "inputs_lending_first.csv"):
    for r in csv.DictReader(open(T / f)):
        for k in ("bear", "base", "bull"):
            allow_value(r[k])
for r in csv.DictReader(open(T / "channels.csv")):
    for k, v in r.items():
        allow_value(v) if k not in ("channel", "label", "basis", "notes") else allow(v)
# the Monte Carlo's frozen ranges and the register's plan values (2 Oct 2026)
for f in ("distributions.csv", "assumption_register.csv"):
    if (T / f).exists():
        for r in csv.DictReader(open(T / f)):
            for k in ("low", "mode", "high", "plan_value"):
                if r.get(k) not in (None, ""):
                    allow_value(r[k])
if (T / "sens_grid.csv").exists():
    for r in csv.DictReader(open(T / "sens_grid.csv")):
        allow_value(r["cost_debit"])
for r in csv.DictReader(open(T / "inputs_path.csv")):
    for k in ("new_activated", "fixed_opex_cr", "cac_scale"):
        allow_value(r[k])
import json
for v in json.loads((T / "verify_result.json").read_text()).values():
    allow_value(v)
# labels, not data: years, slide and appendix numbers, the brief's $100M target and 3x bar,
# model horizon (36/60 months), 90+ days late, cohort years, step numbers, 24h notice
for v in list(range(0, 41)) + list(range(2017, 2040)) + [100, 60, 36, 90, 2019.22, 2025.26, 2029.30]:
    allowed.add(float(v))

section_re = re.compile(r'<section id="([^"]+)"')
flags = 0
DECK_DIR = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "deck")   # "story" checks the story deck
for f in sorted((DECK_DIR / "project" / "slides").glob("*.html")):
    src = f.read_text()
    text = html.unescape(re.sub(r"<[^>]+>", " ", src))
    for raw, v in nums(text):
        if round(v, 2) in allowed or round(v, 1) in allowed or round(v, 0) in allowed and float(v).is_integer():
            continue
        i = text.find(raw)
        ctx = " ".join(text[max(0, i - 50): i + 40].split())
        print(f"[{f.stem}] {raw!r}: ...{ctx}...")
        flags += 1
print(f"{flags} untraced number(s)")
sys.exit(1 if flags else 0)

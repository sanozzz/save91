"""Build the Save91 SWOT + competitor page from the CSVs in this folder.

The CSVs are the source of truth: edit a row there, then run
    python3 build_swot.py
It writes swot.html (the published page body) and swot_offline.html (opens in any browser).
"""
import csv, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(name):
    with open(os.path.join(HERE, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fmt(s):
    """CSV text -> display text: Rs -> rupee sign, true minus, en dash in ranges."""
    s = html.escape(s or "")
    s = re.sub(r"(^|[\s(])-Rs ", lambda m: m.group(1) + "\u2212\u20b9", s)
    s = re.sub(r"(^|[\s(])\+Rs ", lambda m: m.group(1) + "+\u20b9", s)
    s = s.replace("Rs ", "\u20b9")
    s = re.sub(r"(^|[\s(])-(\d)", lambda m: m.group(1) + "\u2212" + m.group(2), s)
    s = re.sub(r"(\d)-(\d)", "\\1\u2013\\2", s)
    s = s.replace(" x ", " \u00d7 ")
    return s


swot = rows("swot_items.csv")
moves = rows("moves.csv")
comps = rows("competitors.csv")
matrix = rows("landscape_matrix.csv")
h2h = rows("head_to_head.csv")
watch = rows("watch_list.csv")

Q = [  # quadrant, css key, title, one-line reading of the quadrant
    ("Strength", "s", "Strengths",
     "Only S5 is hard to copy. Bachatt has S1, S2 and S4 too, and S3 is ours only once we build on it."),
    ("Weakness", "w", "Weaknesses",
     "W2 and W5 depend on how we run the pilot. The rest come with a savings-first model, and loans have to pay for them."),
    ("Opportunity", "o", "Opportunities",
     "O1 to O6 are open now. O7 opens once savers prove they repay."),
    ("Threat", "t", "Threats",
     "Four are already happening. PhonePe (T1) is the one that could close the market."),
]
TAG_TONE = {
    "Hard to copy": "good", "Ours to build": "build", "Bachatt has it too": "flat",
    "Fixable in the pilot": "good", "Built into the model": "flat",
    "Now": "good", "Later": "flat",
    "Already happening": "bad", "Could happen": "warn",
}


def quadrant(qname, key, title, reading):
    items = [r for r in swot if r["quadrant"] == qname]
    lis = []
    for r in items:
        num = f'<span class="kn">{fmt(r["key_number"])}</span>' if r["key_number"] else ""
        lis.append(
            f'<li><span class="id">{r["id"]}</span><div class="it">'
            f'<p class="hl">{fmt(r["headline"])}</p>{num}'
            f'<span class="tag {TAG_TONE.get(r["tag"], "flat")}">{fmt(r["tag"])}</span></div></li>')
    return (f'<section class="quad q-{key}" aria-labelledby="q-{key}">'
            f'<h3 id="q-{key}"><span class="ql">{title[0]}</span>{title}</h3>'
            f'<ol>{"".join(lis)}</ol><p class="read">{reading}</p></section>')


def evidence(qname, title):
    items = [r for r in swot if r["quadrant"] == qname]
    out = []
    for r in items:
        src = fmt(r["source"])
        if r["url"]:
            src = f'<a href="{html.escape(r["url"])}" target="_blank" rel="noopener">{src}</a>'
        out.append(f'<div class="ev"><span class="id">{r["id"]}</span><div><p class="hl">{fmt(r["headline"])}</p>'
                   f'<p>{fmt(r["detail"])}</p><p class="src">{src} &middot; {html.escape(r["source_date"])}</p></div></div>')
    return f'<details><summary>{title}: the evidence, item by item</summary>{"".join(out)}</details>'


def dot(v, hl=False):
    v = int(v)
    label = ["none", "some", "strong"][v]
    if v == 2:
        shape = '<circle cx="9" cy="9" r="7" class="f"/>'
    elif v == 1:
        shape = '<circle cx="9" cy="9" r="6.25" class="r"/><path d="M9 2 A7 7 0 0 1 9 16 Z" class="f"/>'
    else:
        shape = '<circle cx="9" cy="9" r="6.25" class="r"/>'
    return f'<svg class="dot" viewBox="0 0 18 18" role="img" aria-label="{label}">{shape}</svg>'


COLS = [("daily_contact", "Daily contact with the owner"), ("holds_savings", "Holds their savings"),
        ("lends_and_collects", "Lends and collects"), ("insurance_and_wealth", "Insurance and wealth"),
        ("built_for_owners", "Built for business owners")]


def matrix_table():
    head = "".join(f"<th scope=\"col\">{c[1]}</th>" for c in COLS)
    body = []
    for r in matrix:
        ours = r["row_id"].startswith("S91")
        cls = ' class="ours"' if ours else ""
        cells = "".join(f"<td>{dot(r[c[0]])}</td>" for c in COLS)
        body.append(f'<tr{cls}><th scope="row">{fmt(r["row_label"])}<span class="why">{fmt(r["why"])}</span></th>{cells}</tr>')
    return (f'<div class="scroll"><table class="mx"><thead><tr><th scope="col">Who</th>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


THREAT = {"High": "bad", "Medium": "warn", "Low": "flat"}


def comp_card(r):
    src = fmt(r["key_fact_source"])
    if r["url"]:
        src = f'<a href="{html.escape(r["url"])}" target="_blank" rel="noopener">{src}</a>'
    return (f'<article class="cc"><header><h3>{fmt(r["group"])}</h3>'
            f'<span class="tag {THREAT[r["threat"]]}">{r["threat"]} threat</span></header>'
            f'<p class="players">{fmt(r["players"])}</p>'
            f'<dl><dt>How they reach owners</dt><dd>{fmt(r["how_they_reach_the_owner"])}</dd>'
            f'<dt>How they make money</dt><dd>{fmt(r["how_they_earn"])}</dd></dl>'
            f'<p class="fact">{fmt(r["key_fact"])}</p>'
            f'<div class="vs"><div><h4>Where they beat us</h4><p>{fmt(r["where_they_beat_us"])}</p></div>'
            f'<div><h4>Where we beat them</h4><p>{fmt(r["where_we_beat_them"])}</p></div></div>'
            f'<p class="src">{src} &middot; {html.escape(r["key_fact_date"])}</p></article>')


def move_card(r):
    uses = "".join(f'<span class="use u-{u[0].lower()}">{u}</span>' for u in r["uses"].split())
    return (f'<article class="mv"><p class="mid">{r["id"]}</p><h3>{fmt(r["title"])}</h3>'
            f'<dl><dt>The problem</dt><dd>{fmt(r["problem"])}</dd>'
            f'<dt>The move</dt><dd>{fmt(r["move"])}</dd>'
            f'<dt>How we will know</dt><dd>{fmt(r["how_we_know"])}</dd></dl>'
            f'<p class="uses">Built from {uses}</p></article>')


def h2h_table():
    body = "".join(f'<tr><th scope="row">{fmt(r["dimension"])}</th><td class="ours">{fmt(r["save91"])}</td>'
                   f'<td>{fmt(r["bachatt"])}</td><td>{fmt(r["phonepe"])}</td></tr>' for r in h2h)
    return (f'<div class="scroll"><table class="h2h"><thead><tr><th scope="col"></th><th scope="col" class="ours">Save91</th>'
            f'<th scope="col">Bachatt</th><th scope="col">PhonePe</th></tr></thead><tbody>{body}</tbody></table></div>')


def watch_table():
    body = "".join(f'<tr><td>{fmt(r["signal"])}</td><td>{fmt(r["why_it_matters"])}</td><td>{fmt(r["what_we_do"])}</td></tr>'
                   for r in watch)
    return (f'<div class="scroll"><table class="wt"><thead><tr><th scope="col">If this happens</th>'
            f'<th scope="col">Why it matters</th><th scope="col">What we do</th></tr></thead><tbody>{body}</tbody></table></div>')


def sources():
    seen, out = set(), []
    for r in swot + comps:
        name = r.get("source") or r.get("key_fact_source")
        url = r["url"]
        key = (name, url)
        if key in seen:
            continue
        seen.add(key)
        label = fmt(name)
        out.append(f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">{label}</a></li>' if url
                   else f"<li>{label}</li>")
    return "".join(out)


CSS = open(os.path.join(HERE, "swot.css"), encoding="utf-8").read()

import slides
SLIDE1 = slides.slide1(rows("summary_items.csv"), rows("summary_flow.csv"), fmt)
SLIDE2 = slides.slide2(rows("landscape_map.csv"), fmt)

page = f"""<title>Save91 SWOT and Rivals</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Serif:wght@500;600&display=swap">
<style>{CSS}</style>
<main class="wrap">
{SLIDE1}
{SLIDE2}
<div class="appendix">
<header class="apxh">
  <p class="eyebrow">Save91 &middot; strategy review &middot; 8 October 2026</p>
  <h1>Appendix</h1>
  <ol class="toc"><li>A1 The answer in five lines</li><li>A2 SWOT, all 24 items</li><li>A3 What the SWOT tells us to do</li><li>A4 The competitive landscape</li><li>A5 Watch list</li><li>A6 The evidence, item by item</li><li>A7 Sources and method</li></ol>
</header>
<header class="top">
  <h2 class="big">Where Save91 stands: strengths, gaps and rivals</h2>
  <p class="lede">Saving is a good way in, but it is not a moat. Save91 wins only if it reaches owners more cheaply than Bachatt and PhonePe, and is first to prove that savers repay.</p>
</header>

<section class="answer" aria-labelledby="ans">
  <h2 id="ans"><span class="an">A1</span> The answer in five lines</h2>
  <ul>
    <li><span class="ql s">S</span><p>Our best asset is a habit owners already have, kept in their own name. But only one of our five strengths is hard to copy: the founder's lending experience.</p></li>
    <li><span class="ql w">W</span><p>At launch we are Bachatt's product, about 17 months later. An owner is worth +&#8377;180 over five years if winning one costs &#8377;250, and &minus;&#8377;70 at today's evidence of about &#8377;500.</p></li>
    <li><span class="ql o">O</span><p>6 in 10 small businesses have no formal loan, and online lenders are pulling back. No digital player has yet shown that a savings record earns an owner a loan.</p></li>
    <li><span class="ql t">T</span><p>PhonePe has every piece but one, and 5 crore shops. Bachatt runs the same play with $16M and a head start.</p></li>
    <li class="so"><span class="ql">So</span><p>Compete on how we win owners and on what we know about their money, not on the savings product. Prove the three numbers within 12 months, with a stop rule agreed now.</p></li>
  </ul>
</section>

<section aria-labelledby="sw">
  <h2 id="sw"><span class="an">A2</span> SWOT, all 24 items</h2>
  <p class="sub">Each item has one number behind it. The tag says how much it really helps or hurts us. The evidence for each item is in A6.</p>
  <div class="grid4">{''.join(quadrant(*q) for q in Q)}</div>
</section>

<section aria-labelledby="mvh">
  <h2 id="mvh"><span class="an">A3</span> What the SWOT tells us to do</h2>
  <p class="sub">Four moves. Each one uses a strength or an opening to answer a weakness or a threat.</p>
  <div class="moves">{''.join(move_card(m) for m in moves)}</div>
</section>

<section aria-labelledby="lsh">
  <h2 id="lsh"><span class="an">A4</span> The competitive landscape</h2>
  <p class="sub">Every player ends at loans. They differ in how they reach the owner and who collects the repayment.</p>
  <figure class="chart">
    <figcaption><strong>Today only the cash co-op joins daily contact, savings and lending, and PhonePe is closest to doing it digitally.</strong> At launch, our row looks almost the same as Bachatt's.</figcaption>
    {matrix_table()}
    <p class="legend"><span>{dot(2)} strong</span><span>{dot(1)} some</span><span>{dot(0)} none</span><span class="note">Ratings are our judgement from the facts below; each row's reason is in grey and in landscape_matrix.csv.</span></p>
  </figure>
  <div class="cards">{''.join(comp_card(c) for c in comps)}</div>
  <h3 class="h3">The closest two, side by side</h3>
  {h2h_table()}
</section>

<section aria-labelledby="wh">
  <h2 id="wh"><span class="an">A5</span> Watch list</h2>
  <p class="sub">Signals that would change this picture, and what we would do.</p>
  {watch_table()}
</section>

<section aria-labelledby="apx">
  <h2 id="apx"><span class="an">A6</span> The evidence, item by item</h2>
  <div class="folds">{''.join(evidence(q[0], q[2]) for q in Q)}</div>
</section>

<details class="method"><summary>A7 Sources and method</summary>
  <p>Numbers come from the sources listed, or from your model's tables in <code>~/Desktop/savings-first-deck/tables/</code>. Tags, threat levels and the dots in the landscape chart are judgement, and are labelled as such. Company claims are marked. Items checked on the web on 8 Oct 2026: online business lenders, gold loans, Account Aggregator lending, Tide India and Jar.</p>
  <ul class="srcs">{sources()}</ul>
  <p>Files: <code>swot_items.csv</code>, <code>competitors.csv</code>, <code>landscape_matrix.csv</code>, <code>moves.csv</code>, <code>head_to_head.csv</code>, <code>watch_list.csv</code>, all in <code>~/Desktop/savings-first-deck/swot/</code>. This page is built from them by <code>build_swot.py</code>.</p>
</details>
</div>
</main>
"""

with open(os.path.join(HERE, "swot.html"), "w", encoding="utf-8") as f:
    f.write(page)
with open(os.path.join(HERE, "swot_offline.html"), "w", encoding="utf-8") as f:
    f.write('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>'
            + page + "</body></html>")
print("built", len(page), "chars")

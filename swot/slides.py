"""The two summary slides at the front of the SWOT page. Called by build_swot.py.

Slide 1: SWOT (top three per box) -> three moves -> a 12-month test with a pass/fail branch.
Slide 2: a map of where each player sits (how often they are in touch x what they do about loans),
         with Save91's route from where it starts to the corner that pays.
"""

QUADS = [("Strength", "s", "Strengths", "S"), ("Weakness", "w", "Weaknesses", "W"),
         ("Opportunity", "o", "Opportunities", "O"), ("Threat", "t", "Threats", "T")]


def slide1(items, flow, fmt):
    def box(q, key, title, letter):
        lis = "".join(
            f'<li><span class="sid">{r["id"]}</span><div><b>{fmt(r["short"])}</b>'
            f'<span>{fmt(r["number"])}</span></div></li>'
            for r in items if r["quadrant"] == q)
        return (f'<div class="qb q-{key}"><h3><span class="ql">{letter}</span>{title}</h3>'
                f'<ul>{lis}</ul></div>')

    steps = {r["step"]: r for r in flow}

    def step(n):
        r = steps[n]
        uses = "".join(f'<span class="use u-{u[0].lower()}">{u}</span>' for u in r["uses"].split())
        return (f'<div class="st"><span class="num">{n}</span><div><b>{fmt(r["label"])}</b>'
                f'<p>{fmt(r["detail"])}</p><p class="uses">Answers {uses}</p></div></div>')

    g, y, n = steps["gate"], steps["yes"], steps["no"]
    plan = (f'<div class="plan"><p class="colh">So we do this</p>{step("1")}<i class="dn"></i>{step("2")}'
            f'<i class="dn"></i>{step("3")}<i class="dn"></i>'
            f'<div class="gate"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 22 12 12 22 2 12Z"/></svg>'
            f'<div><b>{fmt(g["label"])}</b><p>{fmt(g["detail"])}</p></div></div>'
            f'<div class="fork"><i class="dl"></i><i class="dr"></i></div>'
            f'<div class="branches"><div class="br yes"><b>{fmt(y["label"])}</b><p>{fmt(y["detail"])}</p></div>'
            f'<div class="br no"><b>{fmt(n["label"])}</b><p>{fmt(n["detail"])}</p></div></div></div>')

    swot = (f'<div class="swotbox"><p class="colh h-help">Helps us</p><p class="colh h-hurt">Hurts us</p>'
            f'{box(*QUADS[0])}{box(*QUADS[1])}{box(*QUADS[2])}{box(*QUADS[3])}'
            f'<p class="rowh r-in">Inside us</p><p class="rowh r-out">Around us</p></div>')
    arrow = ('<div class="so" aria-hidden="true"><svg viewBox="0 0 40 120"><path d="M6 10 L30 60 L6 110" />'
             '</svg></div>')
    return f"""<section class="slide" aria-labelledby="sl1">
  <header class="sh">
    <p class="eyebrow">Summary 1 of 2 &middot; SWOT and what it tells us to do</p>
    <h2 id="sl1">Saving brings owners in. Winning them cheaply and proving they repay is what makes it pay.</h2>
    <p class="pi"><b>The problem:</b> our savings product is easy to copy, and Bachatt and PhonePe already have it. <b>Our idea:</b> compete on how we win owners and on what we know about their money.</p>
  </header>
  <div class="flow">{swot}{arrow}{plan}</div>
  <p class="foot">Top three items per box. All 24 items with sources: appendix A2 and A6. The four moves in full: A3.</p>
</section>"""


# map geometry (SVG user units)
X0, X1, Y0, Y1 = 120, 780, 24, 400


def px(x):
    return X0 + float(x) * (X1 - X0) / 10


def py(y):
    return Y1 - float(y) * (Y1 - Y0) / 10


def marker(cx, cy, kind, cls="pt"):
    if kind == "full":
        return f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="7" class="{cls} f"/>'
    ring = f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="6.25" class="{cls} r"/>'
    if kind == "half":
        return ring + f'<path d="M{cx:.0f} {cy - 7:.0f} A7 7 0 0 1 {cx:.0f} {cy + 7:.0f} Z" class="{cls} f"/>'
    return ring


def slide2(points, fmt):
    g = []
    # the corner that pays
    zx, zy = px(7.0), py(6.7)
    g.append(f'<rect x="{zx:.0f}" y="{Y0}" width="{X1 - zx:.0f}" height="{zy - Y0:.0f}" rx="8" class="zone"/>')
    g.append(f'<text x="{zx + 10:.0f}" y="{Y0 + 18}" class="zl">THE CORNER THAT PAYS</text>')
    # grid midlines + axes
    g.append(f'<line x1="{px(5):.0f}" y1="{Y0}" x2="{px(5):.0f}" y2="{Y1}" class="mid"/>')
    g.append(f'<line x1="{X0}" y1="{py(5):.0f}" x2="{X1}" y2="{py(5):.0f}" class="mid"/>')
    g.append(f'<path d="M{X0} {Y1} H{X1}" class="ax" marker-end="url(#axh)"/>')
    g.append(f'<path d="M{X0} {Y1} V{Y0}" class="ax" marker-end="url(#axh)"/>')
    for x, lab, anc in ((0, "Rarely", "start"), (5, "Daily, by app", "middle"), (10, "Daily, in person", "end")):
        g.append(f'<text x="{px(x):.0f}" y="{Y1 + 18}" text-anchor="{anc}" class="tk">{lab}</text>')
    g.append(f'<text x="{(X0 + X1) / 2:.0f}" y="{Y1 + 38}" text-anchor="middle" class="at">How often they are in touch with the owner</text>')
    for y, l1, l2 in ((10, "Lend and", "collect"), (5, "Refer", "loans"), (0, "No", "loans")):
        yy = py(y)
        yy = min(max(yy, Y0 + 10), Y1 - 16)
        g.append(f'<text x="{X0 - 10}" y="{yy:.0f}" text-anchor="end" class="tk">{l1}</text>')
        g.append(f'<text x="{X0 - 10}" y="{yy + 13:.0f}" text-anchor="end" class="tk">{l2}</text>')
    g.append(f'<text transform="translate(26 {(Y0 + Y1) / 2:.0f}) rotate(-90)" text-anchor="middle" class="at">What they do about loans</text>')

    # Save91: start, route, target
    sx, sy = px(5.6), py(5.0)
    tx, ty = px(8.3), py(8.72)
    g.append(f'<path d="M{sx + 9:.0f} {sy:.0f} H{tx:.0f} V{ty + 14:.0f}" class="route" marker-end="url(#rth)"/>')
    g.append(f'<text x="{(sx + tx) / 2 + 6:.0f}" y="{sy + 18:.0f}" text-anchor="middle" class="rl">1 &middot; Win owners in person</text>')
    for i, (t, c) in enumerate((("2 &middot; Lend to them", "rl"), ("better borrowers,", "rs"), ("then our own book", "rs"))):
        g.append(f'<text x="{tx + 9:.0f}" y="{sy - 40 + 14 * i:.0f}" class="{c}">{t}</text>')
    g.append(marker(sx, sy, "full", "us"))
    g.append(f'<text x="{sx:.0f}" y="{sy - 14:.0f}" text-anchor="middle" class="nm us-t">Save91 at launch</text>')
    g.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="10" class="us-ring"/>' + marker(tx, ty, "full", "us"))
    g.append(f'<text x="{tx - 16:.0f}" y="{ty - 2:.0f}" text-anchor="end" class="nm us-t">Save91 if the plan works</text>')
    g.append(f'<text x="{tx - 16:.0f}" y="{ty + 12:.0f}" text-anchor="end" class="sb">daily contact plus lending</text>')

    for p in points:
        cx, cy = px(p["x"]), py(p["y"])
        if p["high_threat"] == "1":
            g.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="11.5" class="thr"/>')
        g.append(marker(cx, cy, p["savings"]))
        dx, dy = float(p["dx"]), float(p["dy"])
        g.append(f'<text x="{cx + dx:.0f}" y="{cy + dy:.0f}" text-anchor="{p["anchor"]}" class="nm">{fmt(p["name"])}</text>')
        g.append(f'<text x="{cx + dx:.0f}" y="{cy + dy + 14:.0f}" text-anchor="{p["anchor"]}" class="sb">{fmt(p["sub"])}</text>')

    # legend
    ly = Y1 + 66
    leg = [(X0, "full", "holds their savings"), (X0 + 150, "half", "savings on the side"), (X0 + 300, "none", "no savings")]
    for lx, k, t in leg:
        g.append(marker(lx + 7, ly - 4, k) + f'<text x="{lx + 20}" y="{ly}" class="tk">{t}</text>')
    g.append(f'<circle cx="{X0 + 457}" cy="{ly - 4}" r="9" class="thr"/><text x="{X0 + 474}" y="{ly}" class="tk">high threat to us</text>')

    svg = (f'<svg class="map" viewBox="0 0 800 {Y1 + 78}" role="img" aria-labelledby="mapt">'
           '<title id="mapt">Map of competitors by how often they are in touch with the owner and what they do about loans</title>'
           '<defs><marker id="axh" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0 0 L10 5 L0 10 z" class="axh"/></marker>'
           '<marker id="rth" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
           '<path d="M0 0 L10 5 L0 10 z" class="rth"/></marker></defs>'
           + "".join(g) + "</svg>")

    side = """<aside class="reads">
      <div class="rd t"><b>PhonePe is almost in the corner.</b><p>It has the shops, a Daily SIP and loans repaid from daily sales. The one piece it lacks is saving from sales.</p></div>
      <div class="rd w"><b>We start in Bachatt's spot.</b><p>Same product, about 17 months later, with $1M against its $16M.</p></div>
      <div class="rd s"><b>The co-op shows the corner pays.</b><p>It holds savings and lends in cash, with no deposit insurance. That is the habit we replace.</p></div>
      <div class="rd route"><b>Our route: first right, then up.</b><p>Win owners in person first. Then lend: sell lenders better borrowers, and later run our own loan book.</p></div>
    </aside>"""
    return f"""<section class="slide" aria-labelledby="sl2">
  <header class="sh">
    <p class="eyebrow">Summary 2 of 2 &middot; the competitive landscape</p>
    <h2 id="sl2">The money is in daily contact plus lending. PhonePe is closest to it, and we start next to Bachatt.</h2>
  </header>
  <div class="mapwrap"><figure class="mapfig">{svg}</figure>{side}</div>
  <p class="foot">Positions are our judgement from the facts in appendix A4, where each group has a card with its numbers and sources.</p>
</section>"""

"""Compact push plan for the v4 tabs: dense cell blocks for spreadsheets.values.update (USER_ENTERED; None = skipped, so the
spill areas stay empty) plus one batchUpdate of tabs + named ranges + merged formats. Writes <out>/blk_*.json.
Usage: python model/v4_push_blocks.py <out_dir>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_push_payloads as pp  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)


def letters(c):
    s = ""
    c += 1
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


def blocks(cells):
    """Greedy: merge consecutive rows whose column spans sit within 2 columns of the current block's span."""
    rows = {}
    for (r, c), v in cells.items():
        rows.setdefault(r, {})[c] = v
    out, cur = [], None
    for r in sorted(rows):
        c0, c1 = min(rows[r]), max(rows[r])
        w, cw = c1 - c0 + 1, (cur["c1"] - cur["c0"] + 1) if cur else 0
        if cur and r <= cur["r1"] + 2 and c0 >= cur["c0"] - 2 and c1 <= cur["c1"] + 2 and (cw <= 20 or w * 2 >= cw):
            cur["r1"] = r
            cur["c0"], cur["c1"] = min(cur["c0"], c0), max(cur["c1"], c1)
        else:
            if cur:
                out.append(cur)
            cur = {"r0": r, "r1": r, "c0": c0, "c1": c1}
    if cur:
        out.append(cur)
    res = []
    for b in out:
        grid = [[rows.get(r, {}).get(c) for c in range(b["c0"], b["c1"] + 1)] for r in range(b["r0"], b["r1"] + 1)]
        res.append((f"{letters(b['c0'])}{b['r0'] + 1}:{letters(b['c1'])}{b['r1'] + 1}", grid))
    return res


def merged_number_formats(sid, number):
    by = {}
    for ref, pat in number.items():
        r, c = pp.a1(ref) if ":" not in ref else (None, None)
        if r is None:
            by.setdefault(("rng", ref, pat), None)
            continue
        by.setdefault((c, pat), []).append(r)
    reqs = []
    for key, rs in by.items():
        if key[0] == "rng":
            reqs.append((pp.grid(sid, key[1]), key[2]))
            continue
        c, pat = key
        rs = sorted(rs)
        start = prev = rs[0]
        for r in rs[1:] + [None]:
            if r is not None and r == prev + 1:
                prev = r
                continue
            reqs.append(({"sheetId": sid, "startRowIndex": start, "endRowIndex": prev + 1, "startColumnIndex": c, "endColumnIndex": c + 1}, pat))
            if r is not None:
                start = prev = r
    return [{"repeatCell": {"range": g, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": p}}},
                            "fields": "userEnteredFormat.numberFormat"}} for g, p in reqs]


def merged_font(sid, refs, rgb):
    by = {}
    for ref in refs:
        if ":" in ref:
            by.setdefault("rng", []).append(pp.grid(sid, ref))
            continue
        r, c = pp.a1(ref)
        by.setdefault(c, []).append(r)
    grids = list(by.pop("rng", []))
    for c, rs in by.items():
        rs = sorted(rs)
        start = prev = rs[0]
        for r in rs[1:] + [None]:
            if r is not None and r == prev + 1:
                prev = r
                continue
            grids.append({"sheetId": sid, "startRowIndex": start, "endRowIndex": prev + 1, "startColumnIndex": c, "endColumnIndex": c + 1})
            if r is not None:
                start = prev = r
    return [{"repeatCell": {"range": g, "cell": {"userEnteredFormat": {"textFormat": {"foregroundColorStyle": {"rgbColor": rgb}}}},
                            "fields": "userEnteredFormat.textFormat.foregroundColorStyle"}} for g in grids]


def main():
    sheets = pp.SPEC["sheets"]
    setup = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
    reqs = []
    for i, sh in enumerate(sheets):
        cells = {pp.a1(k): v for k, v in sh["cells"].items()}
        rows = max(max(r for r, _ in cells) + 1, 100) + 5
        cols = max(max(c for _, c in cells) + 1, 26) + 2
        reqs.append({"addSheet": {"properties": {"sheetId": sh["sheetId"], "title": sh["title"], "index": 18 + i,
                                                 "gridProperties": {"rowCount": rows, "columnCount": cols},
                                                 "tabColorStyle": {"rgbColor": {"red": 0.06, "green": 0.62, "blue": 0.54}}}}})
    for sh in sheets:
        for nm, ref in sh.get("named_ranges", {}).items():
            reqs.append({"addNamedRange": {"namedRange": {"name": nm, "range": pp.grid(sh["sheetId"], ref)}}})
    (OUT / "blk_00_setup.json").write_text(json.dumps(reqs, ensure_ascii=False, separators=(",", ":")))
    fm = []
    for sh in sheets:
        sid, f = sh["sheetId"], sh.get("formats", {})
        fm += merged_number_formats(sid, f.get("number", {}))
        fm += merged_font(sid, f.get("blue_font", []), {"red": 0, "green": 0, "blue": 1})
        fm += merged_font(sid, f.get("grey_font", []), {"red": 0.45, "green": 0.45, "blue": 0.45})
        for r in f.get("bold_rows", []):
            fm.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": r - 1, "endRowIndex": r},
                                      "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}}, "fields": "userEnteredFormat.textFormat.bold"}})
        for r in f.get("wrap_rows", []):
            fm.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": r - 1, "endRowIndex": r},
                                      "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}}, "fields": "userEnteredFormat.wrapStrategy"}})
        gp, fields = {}, []
        if f.get("freeze_rows"):
            gp["frozenRowCount"], _ = f["freeze_rows"], fields.append("gridProperties.frozenRowCount")
        if f.get("freeze_cols"):
            gp["frozenColumnCount"], _ = f["freeze_cols"], fields.append("gridProperties.frozenColumnCount")
        if gp:
            fm.append({"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": gp}, "fields": ",".join(fields)}})
        for colL, px in f.get("col_widths", {}).items():
            ci = pp.col_idx(colL)
            fm.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": ci, "endIndex": ci + 1},
                                                     "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    (OUT / "blk_99_formats.json").write_text(json.dumps(fm, ensure_ascii=False, separators=(",", ":")))
    k = 0
    for sh in sheets:
        cells = {pp.a1(key): v for key, v in sh["cells"].items() if v not in (None, "")}
        for rng, grid in blocks(cells):
            k += 1
            (OUT / f"blk_{k:02d}.json").write_text(json.dumps({"range": f"'{sh['title']}'!{rng}", "formulas": grid}, ensure_ascii=False, separators=(",", ":")))
    for p in sorted(OUT.glob("blk_*.json")):
        d = json.loads(p.read_text())
        info = d["range"] if isinstance(d, dict) else f"{len(d)} requests"
        print(p.name, info, f"{p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()

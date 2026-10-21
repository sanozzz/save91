"""Turn tables/v4_gsheet_spec.json into Google Sheets batchUpdate request batches (one JSON file per batch) for the parent to
send with the Sheets connector: add the 8 v4 tabs, add every named range, write each tab's cells as typed updateCells row runs
(formulas as formulaValue, so the spills stay empty), then the formats. Writes <out>/v4push_NN_<what>.json and prints a plan.
Usage: python model/v4_push_payloads.py <out_dir>"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "tables" / "v4_gsheet_spec.json").read_text())
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
MAX_CELLS = 450                                  # cells per batch, keeps one connector call small


def col_idx(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def a1(ref):
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    return int(m.group(2)) - 1, col_idx(m.group(1))


def grid(sheet_id, ref):
    """'B3' or 'B3:D9' -> GridRange."""
    parts = ref.split(":")
    r0, c0 = a1(parts[0])
    r1, c1 = a1(parts[-1])
    return {"sheetId": sheet_id, "startRowIndex": r0, "endRowIndex": r1 + 1, "startColumnIndex": c0, "endColumnIndex": c1 + 1}


def cell_value(v):
    if isinstance(v, bool):
        return {"boolValue": v}
    if isinstance(v, (int, float)):
        return {"numberValue": v}
    s = str(v)
    if s.startswith("="):
        return {"formulaValue": s}
    return {"stringValue": s}


def runs(cells):
    """{(r, c): v} -> [(r, c0, [v...])] contiguous runs along each row."""
    by_row = {}
    for (r, c), v in cells.items():
        by_row.setdefault(r, {})[c] = v
    out = []
    for r in sorted(by_row):
        cols = sorted(by_row[r])
        start = prev = cols[0]
        vals = [by_row[r][start]]
        for c in cols[1:]:
            if c == prev + 1:
                vals.append(by_row[r][c])
            else:
                out.append((r, start, vals))
                start, vals = c, [by_row[r][c]]
            prev = c
        out.append((r, start, vals))
    return out


def write(n, what, requests):
    p = OUT / f"v4push_{n:02d}_{what}.json"
    p.write_text(json.dumps(requests, ensure_ascii=False, separators=(",", ":")))
    return p


def main():
    n = 0
    plan = []
    sheets = SPEC["sheets"]
    adds = []
    for i, sh in enumerate(sheets):
        cells = {a1(k): v for k, v in sh["cells"].items()}
        rows = max(r for r, _ in cells) + 1
        cols = max(c for _, c in cells) + 1
        rows = max(rows, 100) + 5
        cols = max(cols, 26) + 2
        adds.append({"addSheet": {"properties": {"sheetId": sh["sheetId"], "title": sh["title"], "index": 18 + i,
                                                 "gridProperties": {"rowCount": rows, "columnCount": cols},
                                                 "tabColorStyle": {"rgbColor": {"red": 0.06, "green": 0.62, "blue": 0.54}}}}})
    n += 1
    plan.append((write(n, "add_tabs", adds), len(adds)))
    names = []
    for sh in sheets:
        for nm, ref in sh.get("named_ranges", {}).items():
            names.append({"addNamedRange": {"namedRange": {"name": nm, "range": grid(sh["sheetId"], ref)}}})
    n += 1
    plan.append((write(n, "named_ranges", names), len(names)))
    for sh in sheets:
        cells = {a1(k): v for k, v in sh["cells"].items() if v not in (None, "")}
        batch, count = [], 0
        for r, c0, vals in runs(cells):
            batch.append({"updateCells": {"start": {"sheetId": sh["sheetId"], "rowIndex": r, "columnIndex": c0},
                                          "rows": [{"values": [{"userEnteredValue": cell_value(v)} for v in vals]}],
                                          "fields": "userEnteredValue"}})
            count += len(vals)
            if count >= MAX_CELLS:
                n += 1
                plan.append((write(n, "cells_" + sh["title"].replace(" ", "_"), batch), count))
                batch, count = [], 0
        if batch:
            n += 1
            plan.append((write(n, "cells_" + sh["title"].replace(" ", "_"), batch), count))
    fmts = []
    for sh in sheets:
        sid, f = sh["sheetId"], sh.get("formats", {})
        for ref, pattern in f.get("number", {}).items():
            fmts.append({"repeatCell": {"range": grid(sid, ref), "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": pattern}}},
                                        "fields": "userEnteredFormat.numberFormat"}})
        for ref in f.get("blue_font", []):
            fmts.append({"repeatCell": {"range": grid(sid, ref), "cell": {"userEnteredFormat": {"textFormat": {"foregroundColorStyle": {"rgbColor": {"red": 0, "green": 0, "blue": 1}}}}},
                                        "fields": "userEnteredFormat.textFormat.foregroundColorStyle"}})
        for ref in f.get("grey_font", []):
            fmts.append({"repeatCell": {"range": grid(sid, ref), "cell": {"userEnteredFormat": {"textFormat": {"foregroundColorStyle": {"rgbColor": {"red": 0.45, "green": 0.45, "blue": 0.45}}}}},
                                        "fields": "userEnteredFormat.textFormat.foregroundColorStyle"}})
        for r in f.get("bold_rows", []):
            fmts.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": r - 1, "endRowIndex": r},
                                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}}, "fields": "userEnteredFormat.textFormat.bold"}})
        for r in f.get("wrap_rows", []):
            fmts.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": r - 1, "endRowIndex": r},
                                        "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}}, "fields": "userEnteredFormat.wrapStrategy"}})
        gp, fields = {}, []
        if f.get("freeze_rows"):
            gp["frozenRowCount"] = f["freeze_rows"]
            fields.append("gridProperties.frozenRowCount")
        if f.get("freeze_cols"):
            gp["frozenColumnCount"] = f["freeze_cols"]
            fields.append("gridProperties.frozenColumnCount")
        if gp:
            fmts.append({"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": gp}, "fields": ",".join(fields)}})
        for colL, px in f.get("col_widths", {}).items():
            ci = col_idx(colL)
            fmts.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": ci, "endIndex": ci + 1},
                                                       "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    for i in range(0, len(fmts), 200):
        n += 1
        plan.append((write(n, "formats", fmts[i:i + 200]), len(fmts[i:i + 200])))
    for p, k in plan:
        print(f"{p.name}: {k} items, {p.stat().st_size // 1024} KB")
    cp = [sh["title"] for sh in sheets if sh.get("formats", {}).get("copy_down")]
    if cp:
        print("copy_down present on:", cp, "(all its rows are in the spec cells; nothing extra to do)")


if __name__ == "__main__":
    main()

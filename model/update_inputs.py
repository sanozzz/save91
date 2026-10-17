"""Apply research findings to tables/inputs*.csv. Each update names its source row id."""
import csv, sys
from pathlib import Path

T = Path(__file__).resolve().parent.parent / "tables"


def apply(table, updates):
    p = T / table
    rows = list(csv.DictReader(open(p, newline="")))
    fields = list(rows[0].keys())
    ids = {r["id"] for r in rows}
    for k in updates:
        assert k in ids, f"unknown input {k}"
    for r in rows:
        if r["id"] in updates:
            r.update({k: str(v) for k, v in updates[r["id"]].items()})
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{table}: updated {len(updates)} rows")


def v(bear, base, bull, basis, source, as_of="2026-09-30", notes=None):
    d = {"bear": bear, "base": base, "bull": bull, "basis": basis, "source": source, "as_of": as_of}
    if notes is not None:
        d["notes"] = notes
    return d


def vng(bear, base, bull, basis, source=""):
    """Non-gig values for an input (blank = same as gig)."""
    return {"ng_bear": bear, "ng_base": base, "ng_bull": bull, "ng_basis": basis, "ng_source": source}


if __name__ == "__main__":
    import importlib
    batch = importlib.import_module(sys.argv[1])
    for table, ups in batch.UPDATES.items():
        apply(table, ups)

import argparse
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation

parser = argparse.ArgumentParser(description="Summarize rug stock by design and dimensions.")
parser.add_argument("csv_file")
args = parser.parse_args()
groups = defaultdict(lambda: [0, Decimal(0), Decimal(0)])
with open(args.csv_file, encoding="utf-8-sig", newline="") as source:
    rows = csv.DictReader(source)
    required = {"design", "width_m", "length_m", "quantity", "rate_per_m2"}
    if required - set(rows.fieldnames or []):
        parser.error("Missing columns: " + ", ".join(sorted(required - set(rows.fieldnames or []))))
    for row in rows:
        try:
            design = row["design"].strip()
            w, h, rate = (Decimal(row[k]) for k in ("width_m", "length_m", "rate_per_m2"))
            count = int(row["quantity"])
            if not design or not all(x.is_finite() for x in (w, h, rate)) or min(w, h) <= 0 or min(count, rate) < 0:
                raise ValueError
        except (ValueError, TypeError, AttributeError, InvalidOperation):
            parser.error(f"Invalid inventory data on line {rows.line_num}")
        if count:
            totals = groups[design, w, h]
            area = w * h * count
            totals[0] += count
            totals[1] += area
            totals[2] += area * rate
for (design, w, h), (count, area, value) in sorted(groups.items()):
    print(f"{design} | {w} × {h} m | {count} pcs | {area:.2f} m² | {value:.2f}")
count, area, value = map(sum, zip(*groups.values())) if groups else (0, 0, 0)
print(f"Total | {count} pcs | {area:.2f} m² | {value:.2f}")

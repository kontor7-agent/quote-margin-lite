#!/usr/bin/env python3
"""quote_margin - price a job from a CSV of lines and check your margin.

Read-only: reads one CSV, prints a report. No network, writes no files.

CSV columns (header required):
  description, qty, unit_cost, unit_price
unit_price is optional. If empty, it is unit_cost * (1 + markup).

Example:
  python quote_margin.py lines.csv --markup 25 --target-margin 35 --tax 19
"""
import argparse
import csv
import sys


def num(text, field, row_no):
    text = (text or "").strip().replace(",", ".")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        sys.exit(f"Row {row_no}: '{text}' in column '{field}' is not a number.")


def main():
    p = argparse.ArgumentParser(description="Price a job and check the margin.")
    p.add_argument("csv_file", help="CSV with description,qty,unit_cost[,unit_price]")
    p.add_argument("--markup", type=float, default=25.0,
                   help="markup %% on cost when unit_price is empty (default 25)")
    p.add_argument("--target-margin", type=float, default=35.0,
                   help="warn if margin %% of price is below this (default 35)")
    p.add_argument("--tax", type=float, default=0.0,
                   help="sales tax / VAT %% added to the customer total (default 0)")
    a = p.parse_args()

    if a.target_margin >= 100:
        sys.exit("--target-margin must be below 100.")

    try:
        f = open(a.csv_file, newline="", encoding="utf-8-sig")
    except OSError as e:
        sys.exit(f"Cannot open file: {e}")

    cost_total = price_total = 0.0
    lines = []
    with f:
        rd = csv.DictReader(f)
        need = {"description", "qty", "unit_cost"}
        if not rd.fieldnames or not need.issubset({h.strip() for h in rd.fieldnames}):
            sys.exit("CSV needs the columns: description, qty, unit_cost (unit_price optional).")
        for i, row in enumerate(rd, start=2):
            row = {(k or "").strip(): v for k, v in row.items()}
            if not (row.get("description") or "").strip():
                continue
            qty = num(row.get("qty"), "qty", i)
            cost = num(row.get("unit_cost"), "unit_cost", i)
            price = num(row.get("unit_price"), "unit_price", i)
            if qty is None or cost is None:
                sys.exit(f"Row {i}: qty and unit_cost are required.")
            if price is None:
                price = cost * (1 + a.markup / 100)
            lc, lp = qty * cost, qty * price
            cost_total += lc
            price_total += lp
            lines.append((row["description"].strip(), qty, lc, lp))

    if not lines:
        sys.exit("No lines found.")

    profit = price_total - cost_total
    margin = profit / price_total * 100 if price_total else 0.0
    tax = price_total * a.tax / 100

    w = max(len(l[0]) for l in lines)
    print(f"{'Line'.ljust(w)}  {'Qty':>7}  {'Cost':>10}  {'Price':>10}")
    for d, q, c, pr in lines:
        print(f"{d.ljust(w)}  {q:>7g}  {c:>10.2f}  {pr:>10.2f}")
    print("-" * (w + 33))
    print(f"{'Total cost'.ljust(w)}  {'':>7}  {cost_total:>10.2f}")
    print(f"{'Price (net)'.ljust(w)}  {'':>7}  {'':>10}  {price_total:>10.2f}")
    if a.tax:
        print(f"{('Tax ' + format(a.tax, 'g') + '%').ljust(w)}  {'':>7}  {'':>10}  {tax:>10.2f}")
        print(f"{'Customer total'.ljust(w)}  {'':>7}  {'':>10}  {price_total + tax:>10.2f}")
    print(f"\nProfit: {profit:.2f}   Margin: {margin:.1f}% of price")
    if margin < a.target_margin:
        needed = cost_total / (1 - a.target_margin / 100)
        print(f"WARNING: below target {a.target_margin:g}%. "
              f"Net price for the target margin: {needed:.2f}")
    else:
        print(f"OK: at or above target {a.target_margin:g}%.")
    print("Note: a calculator, not tax or accounting advice.")


if __name__ == "__main__":
    main()

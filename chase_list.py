#!/usr/bin/env python3
"""chase_list - who owes you money, and who to chase today.

Read-only: reads one CSV, prints a list. No network, writes no files.

CSV columns (header required):
  invoice, customer, amount, invoice_date, paid
  invoice_date as YYYY-MM-DD. paid = yes/y/1/true if settled (else empty/no).
  Optional column: terms_days (overrides --terms for that row).

Example:
  python chase_list.py invoices.csv --terms 14
"""
import argparse
import csv
import sys
from datetime import date, datetime, timedelta

PAID = {"yes", "y", "1", "true", "paid", "x"}


def main():
    p = argparse.ArgumentParser(description="List unpaid invoices by days overdue.")
    p.add_argument("csv_file")
    p.add_argument("--terms", type=int, default=14, help="payment terms in days (default 14)")
    p.add_argument("--today", help="override today's date, YYYY-MM-DD (for testing)")
    a = p.parse_args()

    try:
        today = datetime.strptime(a.today, "%Y-%m-%d").date() if a.today else date.today()
    except ValueError:
        sys.exit("--today must look like 2026-01-31.")

    try:
        f = open(a.csv_file, newline="", encoding="utf-8-sig")
    except OSError as e:
        sys.exit(f"Cannot open file: {e}")

    rows, bad = [], 0
    with f:
        rd = csv.DictReader(f)
        need = {"invoice", "customer", "amount", "invoice_date"}
        if not rd.fieldnames or not need.issubset({h.strip() for h in rd.fieldnames}):
            sys.exit("CSV needs the columns: invoice, customer, amount, invoice_date, paid.")
        for r in rd:
            r = {(k or "").strip(): (v or "").strip() for k, v in r.items()}
            if not r["invoice"]:
                continue
            if r.get("paid", "").lower() in PAID:
                continue
            try:
                amount = float(r["amount"].replace(",", "."))
                inv = datetime.strptime(r["invoice_date"], "%Y-%m-%d").date()
                terms = int(r["terms_days"]) if r.get("terms_days") else a.terms
            except ValueError:
                bad += 1
                print(f"Skipped invoice {r['invoice']}: bad amount, date or terms.", file=sys.stderr)
                continue
            due = inv + timedelta(days=terms)
            rows.append((r["invoice"], r["customer"], amount, due, (today - due).days))

    rows.sort(key=lambda x: -x[4])
    print(f"Open invoices as of {today}:\n")
    print(f"{'Invoice':<10} {'Customer':<22} {'Amount':>10}  {'Due':<10}  {'Days over':>9}  Action")
    for inv, cust, amt, due, over in rows:
        if over > 30:
            action = "CALL TODAY"
        elif over > 0:
            action = "Send reminder"
        elif over >= -3:
            action = "Due soon"
        else:
            action = "-"
        print(f"{inv:<10} {cust[:22]:<22} {amt:>10.2f}  {due}  {max(over, 0):>9}  {action}")
    owed = sum(r[2] for r in rows)
    late = sum(r[2] for r in rows if r[4] > 0)
    print(f"\nTotal open: {owed:.2f}   of which overdue: {late:.2f}")
    if bad:
        print(f"{bad} row(s) skipped - check the file.")


if __name__ == "__main__":
    main()

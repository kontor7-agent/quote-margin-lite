# quote-margin-lite

**Know your margin before you send the quote, and know who to chase today – two tiny offline tools for people who quote on site.**

## What it does

- `quote_margin.py` – reads a CSV of quote lines (labour, materials, travel), applies a markup where you gave no price, and prints the net price, tax, profit and margin. It warns you if the margin is below your target and tells you the price needed to reach it.
- `chase_list.py` – reads a CSV of invoices and lists the unpaid ones, most overdue first, with a suggested action (due soon / send reminder / call today) and totals.

Both are read-only: they read one CSV and print to the screen. No network, no files written, no dependencies beyond Python's standard library.

## Quick start

```bash
python quote_margin.py lines.csv --markup 25 --target-margin 35 --tax 19
python chase_list.py invoices.csv --terms 14
```

The included `lines.csv` and `invoices.csv` are fictional samples. Copy them and put in your own jobs.

`lines.csv`:

```csv
description,qty,unit_cost,unit_price
Labour (hours),6,30,65
Materials: tap set,1,42.50,
Travel (km),40,0.30,0.60
```

Leave `unit_price` empty and the price becomes cost + markup. Dates in `invoices.csv` are `YYYY-MM-DD`; mark settled invoices with `yes` in the `paid` column. An optional `terms_days` column overrides `--terms` per row.

Use `--today 2026-10-13` with `chase_list.py` to test with a fixed date.

## Requirements

- Python 3.8 or newer. Nothing to install.
- Amounts have no currency symbol, so use any currency.

These are calculators, not tax or accounting advice. Margin is shown before tax.

Created with AI assistance by an automated system.

## Full version

The free tools cover the maths of one quote and a simple overdue list. The full **Quote It Right** Excel workbook adds, among other things:

- a printable one-page customer quote with a private margin box
- a job log from quote to payment (room for 300 jobs) with profit, margin and hours-vs-quote per job
- receipts linked to jobs, a price list that fills in costs, and a settings sheet for your rates
- a dashboard with money owed, win rate, earned per hour and a chase list

It needs Excel 2016 or newer and uses no macros. Details: https://kontor7-agent.github.io/p/quote-it-right-job-quote-materials-margin-sheet?s=github

## License

MIT – see `LICENSE`.

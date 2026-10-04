# Raw data — source, licence and integrity

**Author of this project: Pranit Ajay Chaudhari.**
**The dataset is not mine.** It is sample content distributed by Tableau Software; all credit and
all rights remain with the publisher. It is included here unmodified except for one documented
privacy step.

---

## Dataset

| | |
|---|---|
| **Name** | Sample — Superstore |
| **Publisher** | Tableau Software, distributed as sample content with Tableau Desktop and widely redistributed for teaching and portfolio work |
| **Source URL** | `https://public.tableau.com/app/learn/sample-data` (Tableau's sample data page). The copy used here was obtained from the public GitHub repository `subhas07/superstore-sales-analysis` |
| **Description** | Order lines for a fictional United States office-supplies retailer: every line carries sales, quantity, discount and profit, with product, customer-segment and geographic attributes |
| **Rows** | **9,994 order lines** |
| **Columns** | **21 as published**; **20 after the privacy step** below |
| **Time period** | **3 January 2014 to 30 December 2017** — 48 continuous months, no gaps |
| **Orders / products / states** | 5,009 orders · 1,862 products · 49 states |
| **Licence** | Tableau distributes it as freely usable sample data for learning and demonstration. It is not released under a named open licence such as CC-BY, so it is used here for a non-commercial portfolio project and credited to Tableau |
| **Date obtained** | 1 October 2026 |

### Integrity

| File state | SHA-256 |
|---|---|
| **As published by Tableau** (21 columns, with `Customer Name`) | `58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97` |
| **As committed here** (20 columns, after the privacy step below) | `7242eeb66700c5c5937cc169dea9342224d763a1725940b16df151bcb0033103` |

Both are published so provenance stays checkable: download the original, confirm the first hash,
run `python/00_prepare_raw.py`, and you reproduce the committed file and its hash exactly.

**Provenance check.** The file was byte-compared against a second, unrelated public repository
(`SanKet2106/Superstore_Sales_Analysis`) and the two are **identical**. A third copy, held as an
Excel workbook in `arindamdatta1024/SuperstoreDataset`, reconciles to the same 9,994 rows and the
same total sales and profit. That is reasonable evidence this is the genuine published file rather
than someone's edited copy.

---

## Available fields

| Field | Type | Used for |
|---|---|---|
| Row ID | integer | Line identifier |
| Order ID, Order Date, Ship Date, Ship Mode | text / date | Order identity and timing |
| Customer ID, Segment | text | Segment is used as a revenue dimension only |
| Country, City, State, Postal Code, Region | text | Regional analysis (Country is constant: United States) |
| Product ID, Category, Sub-Category, Product Name | text | Product hierarchy |
| **Sales** | numeric | **Net revenue** — verified to be net of discount |
| **Quantity** | integer | Units |
| **Discount** | numeric | Discount rate, 0 to 0.80 |
| **Profit** | numeric | Per-line profit |

## Fields the dataset does NOT contain

This matters more than the list above, because it bounds what the project is allowed to claim:

- **No operating expenses, overheads, payroll, rent, marketing spend or tax.** There is therefore
  no operating margin, no EBITDA and no net profit in the accounting sense anywhere in this
  project, and none is estimated.
- **No unit cost or supplier cost.** Cost is only recoverable as a residual (`Revenue − Profit`),
  which is what `ImpliedCost` is and is labelled as.
- **No list price field.** The list value is recovered as `Sales / (1 − Discount)`; the identity is
  tested at run time and the test is described in `docs/METHODOLOGY.md`.
- **No currency column.** The retailer is United States-based and the amounts are conventionally
  read as US dollars. The dataset does not state this, so it is an assumption and is labelled one.
- **No returns, refunds or cancellations**, so revenue here is gross of any later return.
- **No budget or forecast**, so no variance analysis is possible.

## Cleaning requirements

The file is in good condition. Checked and found: **0 missing values**, **0 duplicate Row IDs**,
**0 unparseable dates**, **0 ship dates before their order date**, **0 non-positive sales or
quantities**, and **0 discounts outside [0, 1)**. One row is identical to another on all columns
except Row ID, which is legitimate — the same product can appear twice on one order. **No rows were
removed.** Dates needed parsing from `M/D/YYYY` text and the derived financial fields needed
building; both are logged in `data/cleaned/cleaning_log.csv`.

## Privacy step

The published file contains a **`Customer Name`** column holding **793 full personal names**. This
project never analyses individual people — it measures revenue, cost, profit and margin by product,
category, region and period — so the names serve no analytical purpose and are not shipped.
`python/00_prepare_raw.py` removes that column, then re-scans every remaining cell for email
addresses and phone numbers and refuses to pass if any are found. `Customer ID` is kept because it
is a pseudonymous key (`CG-12520`) needed to count distinct customers; `City`, `State` and
`Postal Code` are kept because regional performance is a required analysis and a postal code
without a name or street address does not identify a household.

## Dataset limitations

**The most important one: this is sample data, not a real company's financial statements.** Tableau
publishes it as demonstration content. Every figure in this project is computed honestly from the
file and nothing is invented — but the underlying business is fictional, so the findings
demonstrate financial-analysis method rather than describing a real firm's performance. That is
stated again in `README.md` and `docs/LIMITATIONS.md` rather than buried here.

## Reproducing the download

```bash
git clone --depth 1 https://github.com/subhas07/superstore-sales-analysis.git
cp "superstore-sales-analysis/Sample - Superstore.csv" data/raw/sample_superstore.csv
sha256sum data/raw/sample_superstore.csv   # expect 58fb59c6... (the published file)
python python/00_prepare_raw.py            # removes the personal-name column
sha256sum data/raw/sample_superstore.csv   # now 7242eeb66700c5c5937cc169dea9342224d763a1725940b16df151bcb0033103 (the committed file)
```

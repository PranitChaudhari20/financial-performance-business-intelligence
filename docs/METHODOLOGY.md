# Methodology

*Author: Pranit Ajay Chaudhari*

## 1. How the dataset was chosen

Two candidates were profiled before one was picked, and the rejected one is recorded here because
the reason it failed is itself a lesson.

**Rejected: DataCo Smart Supply Chain** (180,519 rows, 53 columns, published with a DOI). It is far
larger than the dataset chosen and carries revenue, profit, discount, category, region and
quantity. It was rejected because **its time axis is not a business timeline**. Counting rows by
market and month shows the file is partitioned by market: LATAM appears alone from Jan–May 2015,
Europe alone from Jun 2015–Jan 2016, Pacific Asia alone from Nov 2015–Apr 2016, and so on. Whole
departments appear and vanish with them — Fan Shop is 39% of lines before October 2017 and 5%
after, while Book Shop and Discs Shop appear from nothing. A month-on-month revenue series built on
that file would mostly measure **which market the file happens to cover that month**, and the brief
asks for monthly, quarterly and yearly trend analysis. Publishing growth rates from it would have
produced confident, wrong findings.

**Chosen: Sample — Superstore** (9,994 order lines). Smaller, but it has what the analysis needs:
genuine sales, quantity, discount and profit per line, a product hierarchy, US regions and states,
and — critically — **48 continuous months with all four regions present in every year**, so period
comparisons mean what they appear to mean. Its weakness is that it is sample data rather than a
real company's accounts, which is stated plainly in `README.md`, `data/raw/README.md` and
`docs/LIMITATIONS.md` rather than glossed over.

## 2. The financial model

Every derived figure is an arithmetic transformation of fields the dataset actually contains. The
formulas are in one place here, repeated in the workbook's Data Dictionary sheet, and implemented
identically in Python, SQL and Excel.

| Measure | Formula | Status |
|---|---|---|
| Net revenue | the dataset's `Sales` | **given** |
| Profit | the dataset's `Profit` | **given** |
| Quantity, Discount rate | as given | **given** |
| Gross sales (list value) | `Sales / (1 − Discount)` | derived |
| Discount value | `GrossSales − Sales` | derived |
| Implied cost of sales | `Sales − Profit` | derived, a **residual** |
| Net margin | `Profit / Sales` | derived |
| Cost-to-revenue ratio | `ImpliedCost / Sales` | derived |
| Discount rate on a group | `Σ DiscountValue / Σ GrossSales` | derived |
| Average order value | `Σ Revenue / distinct orders` | derived |
| Profit per order | `Σ Profit / distinct orders` | derived |

### Why `GrossSales` is legitimate rather than invented

The dataset has no list-price column, so recovering one needs justification. For products sold at
two or more discount levels, `Sales / (Quantity × (1 − Discount))` is **constant**: the coefficient
of variation of that implied list price is **0.0000 for 98.3% of such products**, and the
within-product correlation between realised unit price and discount rate has a **median of −1.000**.
`Sales` is therefore net of discount, and the list value is recoverable exactly. The cleaning
script re-tests this at run time and **stops the pipeline** if the identity ever stops holding.

### Why ratios are never averaged

Every ratio in this project is computed as a ratio of sums, never as an average of row-level ratios.
The average of per-line margins is not the margin of the business, and the two differ sharply here
because loss-making lines carry extreme negative ratios. This rule is applied identically in Python,
in SQL (`SUM(profit)/SUM(revenue)`, never `AVG(margin)`) and in Excel.

### Terminology that is deliberately NOT used

The dataset has no operating expenses, overheads, payroll or tax. So this project contains **no
gross profit, no net profit in the accounting sense, no operating margin and no EBITDA**, and makes
no estimate of any of them. "Profit" means the dataset's own per-line profit figure; "net margin"
means that profit over net revenue. "Implied cost of sales" is a residual and is labelled as one
every time it appears, because it is not a reported cost line and includes whatever the publisher
folded into its profit calculation.

## 3. Seasonality is tested, not asserted

Four complete years makes a month-of-year pattern testable. Each month's revenue is indexed against
**that year's own monthly average**, so growth across years cannot masquerade as seasonality, and a
month is only called seasonal if it lands on the same side of the line in **all four years**. Three
months clear that bar on the upside (September, November, December) and five on the downside
(January, February, April, June, July). The remaining four are reported as mixed rather than
rounded into a story.

## 4. Rounding

MySQL's `ROUND()` rounds a half away from zero while NumPy rounds a half to even, so an exact 26.25
becomes 26.3 in one and 26.2 in the other. Every published figure passes through a
`Decimal(ROUND_HALF_UP)` helper, so the three tools agree **exactly** rather than nearly.

## 5. Verification

`python/06_verify.py` compares the Python result tables, the SQL result sets and the Excel cached
values and exits non-zero on any disagreement. It distinguishes three outcomes: **0** everything
agreed, **1** a figure disagreed, **2** the Excel workbook had no cached values so its checks could
not be run. That third case matters — "could not verify" is not the same as "verified".

## 6. What this project deliberately does not do

No customer segmentation, no RFM, no cohort or retention analysis, no campaign-response analysis and
no acquisition analysis. Those belong to other projects in this portfolio; the reasoning is in
`docs/DIFFERENTIATION.md`. `Segment` appears here only as a revenue and margin dimension, never as a
behavioural grouping.

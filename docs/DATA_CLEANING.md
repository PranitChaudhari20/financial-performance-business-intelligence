# Data cleaning

*Author: Pranit Ajay Chaudhari*

The table below is **generated from the pipeline itself** (`data/cleaned/cleaning_log.csv`), so it
cannot drift from what the code actually did. Every step is a check; the Finding column records what
the check returned, including the checks that found nothing.

| # | Step | Rows after | Finding |
|---|---|---|---|
| 1 | Raw order lines loaded | 9,994 | 20 columns |
| 2 | Privacy check: no personal-name column | 9,994 | Customer Name removed by 00_prepare_raw.py |
| 3 | Duplicate check | 9,994 | 0 duplicate Row IDs, 1 rows identical on all other columns |
| 4 | Missing values | 9,994 | none in any column |
| 5 | Dates parsed (M/D/YYYY) | 9,994 | 0 unparseable values |
| 6 | Ship date is on or after order date | 9,994 | 0 violations |
| 7 | Numeric columns coerced | 9,994 | Sales/Profit/Discount as float, Quantity as integer; 0 coercion failures |
| 8 | Non-positive revenue lines | 9,994 | 0 lines with Sales <= 0 |
| 9 | Non-positive quantity lines | 9,994 | 0 lines with Quantity <= 0 |
| 10 | Discount outside [0, 1) | 9,994 | 0 lines |
| 11 | Category/region text trimmed | 9,994 | Country is constant ('United States'), so no country dimension exists |
| 12 | Discount identity re-tested | 9,994 | implied list price stable for 98.3% of discounted products |
| 13 | Derived financial fields built | 9,994 | GrossSales, DiscountValue, Revenue, ImpliedCost, Margin, UnitPrice, IsLossMaking, IsFirstLineOfOrder |
| 14 | Lines where implied cost is negative | 9,994 | 0 (0.00%) - profit exceeds revenue on these lines; kept and reported, not removed |
| 15 | Time fields built | 9,994 | 48 distinct months across 4 years (2014-2017) |
| 16 | Calendar completeness | 9,994 | 48 of 48 months present - continuous, so period comparisons are valid |
| 17 | Discount bands assigned | 9,994 | fixed documented bands, reproducible in SQL and Excel |

---

## The headline: no rows were removed

Every validation passed. The file has **no missing values**, **no duplicate Row IDs**, **no
unparseable dates**, **no ship date before its order date**, **no non-positive sales or quantities**
and **no discount outside [0, 1)**. Reporting a clean result honestly matters as much as reporting a
dirty one: a cleaning section that claims to have fixed problems the data did not have would be
fabrication.

## The decisions worth explaining

**Missing values.** None, in any of the 20 columns. Nothing was imputed because nothing was
missing.

**Duplicates.** Zero duplicate `Row ID` values. One row is identical to another on all *other*
columns, which is legitimate — the same product can appear twice on one order — so it was recorded
and kept rather than silently dropped.

**Date conversion.** `Order Date` and `Ship Date` are text in `M/D/YYYY` form and were parsed with
that explicit format rather than letting pandas guess. Guessing is how 03/04/2014 silently becomes
4 March in one row and 3 April in another. All 9,994 parsed; none failed.

**Numeric conversion.** `Sales`, `Profit` and `Discount` were coerced to float and `Quantity` to a
nullable integer, with the count of coercion failures logged. It was zero.

**Category cleanup.** Text dimensions were trimmed of stray whitespace. `Country` turned out to hold
a single value, "United States", so there is no country dimension to analyse and the project does
not pretend otherwise.

**Outliers.** None were removed. In a financial analysis the extreme values are frequently the
finding — the single most loss-making order line is not noise, it is the thing management needs to
see. Instead of trimming them, the analysis reports the loss distribution directly.

**Excluded records.** None.

**Derived fields.** `GrossSales`, `DiscountValue`, `Revenue`, `ImpliedCost`, `Margin`, `UnitPrice`,
`IsLossMaking`, `IsFirstLineOfOrder`, and the time fields. Each formula is listed in
`docs/METHODOLOGY.md` and in the workbook's Data Dictionary sheet. The derivation of `GrossSales`
depends on `Sales` being net of discount, which the script **re-tests at run time** and halts if the
test fails.

**Privacy.** The `Customer Name` column, holding 793 personal names, is removed by
`python/00_prepare_raw.py` before the file is committed. See `data/raw/README.md`.

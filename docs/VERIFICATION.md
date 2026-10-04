# Verification

*Author: Pranit Ajay Chaudhari*

The project's credibility rests on one claim: Python, MySQL and Excel compute the **same** figures
from the same cleaned data. This page records the checks that were actually run.

Run it yourself:

```bash
python python/06_verify.py
```

| Exit code | Meaning |
|---|---|
| **0** | every check passed |
| **1** | at least one figure disagrees |
| **2** | the Excel workbook has no cached values, so its checks **could not be run** |

That third code matters. "Could not verify" is not the same as "verified", and a script that
conflated them would be the exact failure this project is meant to avoid.

## Result

**94 of 94 checks pass.**

| Group | Checks |
|---|---|
| 17 headline KPIs, Python vs MySQL | 17 |
| Yearly revenue, profit and margin (4 years) | 12 |
| Category revenue, profit and margin (3 categories) | 9 |
| All 17 sub-categories: profit and margin | 1 check covering 34 comparisons |
| Regional revenue, margin and discount rate (4 regions) | 12 |
| Discount band margin and loss-line share (6 bands) | 12 |
| Loss-making states: count and total | 2 |
| Cost structure: 4 components | 4 |
| Python vs Excel cached values | 16 |
| Excel discount bands | 6 |
| Excel cost structure | 3 |

## The SQL load self-check

`04_run_sql.py` prints a self-check straight after loading, and it must match Python before any
query result below it can be trusted:

| | |
|---|---|
| fact rows | 9,994 |
| products | 1,862 |
| geographies | 632 |
| dates | 1,458 |
| revenue | 2,297,200.86 |
| profit | 286,397.02 |

## Excel recomputes the analysis independently

The workbook does not display numbers copied from Python. Every reported figure is a **live formula**
over the Data sheet — `SUMIF`, `COUNTIF`, `SUM` — so the workbook arrives at the totals by its own
route. If Excel and Python disagreed, the verifier would catch it. The workbook contains **686
formulas, all with cached values, and 0 error cells**.

## Defects this process caught

Both were found by running the pipeline, not by reading it.

**1. Two cost-structure labels were being parsed as formulas.** The rows were labelled `= Net
revenue` and `= Profit` for the accounting look. A cell value beginning with `=` is a formula, so
LibreOffice evaluated them and wrote `#VALUE!` and `#NAME?` into the workbook. Found by
`07_recalc_excel.py`, which reports error cells rather than only counting them. Fixed by labelling
the subtotal rows in bold instead.

**2. A KPI formula would have made the workbook unusable.** Counting distinct orders in Excel needs
`SUMPRODUCT(1/COUNTIF(range,range))`, which over 9,994 rows is roughly 100 million operations.
Replaced with an `IsFirstLineOfOrder` flag computed once during cleaning, turning the count into a
`SUM`. The workbook now recalculates in about 15 seconds.

A third was caught earlier, in the analysis rather than the workbook: a chart title described the
figures as rupees. The dataset is a **US** retailer, so the currency convention is US dollars. The
labels were corrected and the currency assumption is now stated in `docs/LIMITATIONS.md`.

## Rounding

MySQL's `ROUND()` rounds a half away from zero while NumPy rounds a half to even, so an exact 26.25
becomes 26.3 in one and 26.2 in the other. Every published figure passes through a
`Decimal(ROUND_HALF_UP)` helper, so the three tools agree exactly rather than nearly.

## Determinism

Running the pipeline twice produces byte-identical cleaned data and output tables. This is checked
as part of the clean-extraction rebuild recorded in `docs/FINAL_AUDIT.md`.

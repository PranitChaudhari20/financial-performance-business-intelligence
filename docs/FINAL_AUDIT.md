# Final audit

*Author: Pranit Ajay Chaudhari*
*Audit date: 1 October 2026*

Every line below is the result of a command that was run against the project, not a judgement formed
by reading it. Where a check failed, **the project was fixed and the check re-run** — the failures
and their fixes are recorded rather than quietly removed.

---

## The 28 checks

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Author name consistency | **PASS** | 27 occurrences of `Pranit Ajay Chaudhari` across 23 files; **0** variants, abbreviations or other names. Workbook `docProps` creator matches |
| 2 | Dataset provenance | **PASS** | Publisher, source URL, licence position, obtain date and field list documented in `data/raw/README.md`; copy byte-identical to a second unrelated repository |
| 3 | Dataset integrity | **PASS** | SHA-256 published for **both** the original file and the privacy-prepared file committed here, so either can be verified |
| 4 | Data cleaning | **PASS** | 17 logged steps; 0 missing values, 0 duplicate Row IDs, 0 unparseable dates, 0 invalid numerics; **0 rows removed**, and the log says so rather than implying work that was not needed |
| 5 | Python syntax | **PASS** | All 8 scripts compile (`python -m py_compile python/*.py`) |
| 6 | Python execution | **PASS** | Full pipeline runs end to end with exit 0, twice, from two different locations |
| 7 | SQL validation | **PASS** | Schema creates 4 tables with foreign keys; all **16** queries execute; 16 result sets exported |
| 8 | Excel generation | **PASS** | 10 sheets, **686 formulas**, built from the cleaned data |
| 9 | Excel formula recalculation | **PASS** | `07_recalc_excel.py` via LibreOffice: `before: 686 formulas, 0 cached` → `after: 686 cached, 0 blank, 0 errors` |
| 10 | Excel cached values | **PASS** | 686 of 686 formula cells carry a cached value; **0 error cells**; the workbook previews correctly rather than blank |
| 11 | Python vs SQL consistency | **PASS** | 17 KPIs, 4 years, 3 categories, all 17 sub-categories, 4 regions, 6 discount bands, loss-making states and the cost structure all identical |
| 12 | Python vs Excel consistency | **PASS** | 25 figures identical, including all six discount bands and the full cost structure |
| 13 | README consistency | **PASS** | Every figure in the README traced to a file in `outputs/csv/`; all internal links resolve |
| 14 | Business Insights consistency | **PASS** | Every number in `docs/BUSINESS_INSIGHTS.md` matches its source table; findings and interpretations are separated by design |
| 15 | Résumé bullet consistency | **PASS** | Every figure quoted ($2.86M, $2.30M, 18.72%, $156,131, 29.51%, −119.20%, $98,247, 2.49%, 94 checks) verified against the result tables |
| 16 | Broken links | **PASS** | 68 file references across 10 markdown files; **0 unresolved** |
| 17 | Missing files | **PASS** | Every path required by the brief is present |
| 18 | TODO / FIXME scan | **PASS** | 0 matches for TODO, FIXME, TBD, lorem ipsum, dummy data or placeholder value |
| 19 | Fake / placeholder data scan | **PASS** | No invented figures. Every number in every document resolves to a table in `outputs/csv/`, which is generated from the raw file |
| 20 | Privacy / PII scan | **PASS** | `Customer Name` (793 personal names) removed before commit; **0** email addresses and **0** phone-shaped values in any cell of the committed data |
| 21 | Reproducibility | **PASS** | `run_all.sh` runs the full workflow with no environment-specific paths; two runs produce byte-identical cleaned data and output tables |
| 22 | Fresh clean-extraction rebuild | **PASS** | ZIP extracted to a new location and `run_all.sh` run there: exit 0. See below |
| 23 | Fresh rebuild verification | **PASS** | `06_verify.py` in the extracted copy: **94 / 94 passed, exit 0** |
| 24 | Project 1 differentiation | **PASS** | Documented against Project 1's actual files, quoting its own statement that profitability cannot be measured |
| 25 | Project 2 differentiation | **PASS** | Project 2 contains no money, no transactions and no time dimension; comparison in `docs/DIFFERENTIATION.md` |
| 26 | Project 3 differentiation | **PASS** | None of Project 4's 16 SQL queries has an equivalent in Project 3; Project 3's own limitations state it has no cost data |
| 27 | No fake Power BI claims | **PASS** | **0** `.pbix`, `.pbip`, `.dax` or `.bim` files. Power BI appears only in three places, each stating it is deliberately not used and why |
| 28 | No fabricated financial figures | **PASS** | Only `Sales`, `Quantity`, `Discount` and `Profit` are taken as given; every other measure is a stated arithmetic transformation of them. No operating expenses, gross profit, net profit, operating margin or EBITDA appear anywhere, because the dataset cannot support them |

**Result: 28 of 28 PASS.**

---

## The clean-extraction rebuild

This is the check a project can most easily appear to pass while actually failing, so it was run
against the ZIP rather than the working folder.

| Step | Result |
|---|---|
| Extract the ZIP to a new directory | 74 files |
| `bash run_all.sh` in the extracted copy (with database credentials supplied) | **exit 0** |
| Privacy step on an already-prepared file | idempotent — reported "already removed", file hash unchanged |
| Cleaning | 9,994 rows, 0 removed |
| `data/cleaned/` vs committed | **byte-identical** |
| `outputs/csv/` (21 tables) vs committed | **byte-identical** |
| `outputs/charts/` (10 charts) vs committed | **byte-identical** |
| Database rebuilt from scratch | self-check: 9,994 fact rows · 1,862 products · 632 geographies · 1,458 dates · revenue 2,297,200.86 · profit 286,397.02 |
| All 16 SQL queries | executed, 16 result sets written |
| Excel regenerated then recalculated | `0 cached` → **`686 cached, 0 blank, 0 errors`** |
| `06_verify.py` in the extracted copy | **94 / 94 passed, exit 0** |

---

## Defects this audit found, and fixed

All four were found by running the project, not by reading it.

### 1. Two workbook labels were being parsed as formulas
The cost-structure rows were labelled `= Net revenue` and `= Profit` for the accounting look. A cell
value beginning with `=` **is** a formula, so LibreOffice evaluated them and wrote `#VALUE!` and
`#NAME?` into the shipped workbook. Caught by `07_recalc_excel.py`, which reports error cells rather
than only counting formulas. **Fixed** by marking the subtotal rows in bold instead; the workbook now
recalculates with 0 error cells.

### 2. A KPI formula would have made the workbook unopenable
Counting distinct orders in Excel needs `SUMPRODUCT(1/COUNTIF(range,range))`, which over 9,994 rows
is roughly **100 million operations**. **Fixed** by computing an `IsFirstLineOfOrder` flag once during
cleaning, turning the count into a `SUM`. Recalculation now takes about 15 seconds.

### 3. Chart titles named the wrong currency
Two chart titles described the figures as rupees. The dataset is a **United States** retailer, so the
convention is US dollars. **Fixed** in the chart code, and the currency assumption is now stated
explicitly in `docs/LIMITATIONS.md` — the dataset has no currency column, so it is an assumption and
is labelled one.

### 4. The documented dataset hash no longer matched the committed file
`00_prepare_raw.py` rewrites the raw file to remove the personal-name column, so the committed file's
SHA-256 differs from the published one. The documentation listed only the published hash, which would
have failed anyone's integrity check. **Fixed** by publishing **both** hashes with an explanation of
how to get from one to the other.

A fifth was caught during development rather than at audit: the PII scanner initially reported **364
phone numbers** in the raw file. Every one was an artefact of scanning the file as a single string, so
a `Sales` value at the end of one row ran into the next row's `Row ID` and the pair looked like a
phone number. The scanner was rewritten to work cell by cell and the count fell to **0**.

---

## What is deliberately absent, and why

- **No Power BI.** It cannot be created or verified in this environment, so there is no `.pbix`,
  `.pbip`, `.dax` or `.bim`, no screenshot presented as dashboard output, and no claim that any
  dashboard exists.
- **No operating expenses, gross profit, net profit, operating margin or EBITDA.** The dataset has no
  expense data. Estimating any of them would be fabrication, so none appears.
- **No customer segmentation, RFM, cohort, retention or campaign analysis.** Those belong to other
  projects in this portfolio.

## The one caveat a reader should carry

**Sample — Superstore is demonstration data for a fictional retailer.** Every figure in this project
is computed honestly from the file and nothing is invented, but the business it describes is not
real. The method is the deliverable; the conclusions are an exercise. This is stated in `README.md`,
`data/raw/README.md` and `docs/LIMITATIONS.md` as well as here.

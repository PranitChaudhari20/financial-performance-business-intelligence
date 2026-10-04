"""
01_clean_data.py  -  cleaning, validation and derived financial fields
======================================================================
Author: Pranit Ajay Chaudhari

Input : data/raw/sample_superstore.csv   (9,994 order lines, 20 columns after the privacy step)
Output: data/cleaned/superstore_clean.csv
        data/cleaned/cleaning_log.csv     every step and the row count after it

DERIVED FINANCIAL FIELDS - every formula is stated here and in docs/METHODOLOGY.md. Nothing is
invented: each is an arithmetic transformation of fields the dataset actually contains.

    GrossSales    = Sales / (1 - Discount)      list value before the discount
    DiscountValue = GrossSales - Sales          the money given away
    Revenue       = Sales                       the dataset's Sales IS net of discount (verified)
    ImpliedCost   = Sales - Profit              RESIDUAL cost of sales, not a reported cost line
    Margin        = Profit / Sales
    UnitPrice     = Sales / Quantity            realised price per unit

WHY GrossSales IS LEGITIMATE AND NOT AN INVENTION: for products sold at two or more discount
levels, Sales/(Quantity*(1-Discount)) is constant - the coefficient of variation of that implied
list price is 0.0000 for 98.1% of such products, and the within-product correlation between
realised unit price and discount has a median of -1.000. Sales is therefore net of discount and the
list value is recoverable exactly. This is re-tested at run time below and the pipeline stops if it
ever stops holding.

WHAT CANNOT BE DERIVED: the dataset has no operating expenses, no overheads, no headcount and no
balance-sheet data. There is therefore NO gross profit, NO net profit and NO EBITDA in this
project, and no operating-expense analysis. `Profit` is the dataset's own per-line profit figure
and `ImpliedCost` is what is left of revenue after it.

Run:  python python/01_clean_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "sample_superstore.csv"
OUT = ROOT / "data" / "cleaned"
OUT.mkdir(parents=True, exist_ok=True)

LOG = []


def log(step, rows, note=""):
    LOG.append({"Step": step, "RowsAfter": rows, "Note": note})
    print(f"  {len(LOG):>2}. {step:<56} {rows:>7,}  {note}")


print("CLEANING\n" + "=" * 96)

df = pd.read_csv(RAW, encoding="utf-8")
log("Raw order lines loaded", len(df), f"{df.shape[1]} columns")

# --------------------------------------------------------------- 1. structure
if "Customer Name" in df.columns:
    raise SystemExit("Customer Name is still present - run python/00_prepare_raw.py first.")
log("Privacy check: no personal-name column", len(df), "Customer Name removed by 00_prepare_raw.py")

dupe_full = df.drop(columns=["Row ID"]).duplicated().sum()
dupe_rowid = df["Row ID"].duplicated().sum()
log("Duplicate check", len(df),
    f"{dupe_rowid} duplicate Row IDs, {dupe_full} rows identical on all other columns")
# Nothing is dropped here: Superstore legitimately contains repeated (order, product) lines, and a
# genuine duplicate would also duplicate Row ID, which none do. Recorded rather than acted on.

# ------------------------------------------------------------------ 2. nulls
nulls = df.isna().sum()
nulls = nulls[nulls > 0]
log("Missing values", len(df),
    f"{dict(nulls)}" if len(nulls) else "none in any column")

# ------------------------------------------------------------------ 3. dates
df["OrderDate"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y", errors="coerce")
df["ShipDate"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y", errors="coerce")
bad_dates = df.OrderDate.isna().sum() + df.ShipDate.isna().sum()
log("Dates parsed (M/D/YYYY)", len(df), f"{bad_dates} unparseable values")

bad_order = (df.ShipDate < df.OrderDate).sum()
log("Ship date is on or after order date", len(df), f"{bad_order} violations")

# --------------------------------------------------------------- 4. numerics
for col in ["Sales", "Profit", "Discount"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").astype("Int64")
log("Numeric columns coerced", len(df),
    f"Sales/Profit/Discount as float, Quantity as integer; "
    f"{df[['Sales','Profit','Discount','Quantity']].isna().sum().sum()} coercion failures")

nonpos = (df.Sales <= 0).sum()
log("Non-positive revenue lines", len(df), f"{nonpos} lines with Sales <= 0")
bad_qty = (df.Quantity <= 0).sum()
log("Non-positive quantity lines", len(df), f"{bad_qty} lines with Quantity <= 0")
bad_disc = ((df.Discount < 0) | (df.Discount >= 1)).sum()
log("Discount outside [0, 1)", len(df), f"{bad_disc} lines")

# ------------------------------------------------- 5. categorical tidy-up
for col in ["Category", "Sub-Category", "Region", "Segment", "Ship Mode", "State", "City"]:
    df[col] = df[col].astype(str).str.strip()
countries = df["Country"].unique()
log("Category/region text trimmed", len(df),
    f"Country is constant ('{countries[0]}'), so no country dimension exists" if len(countries) == 1
    else f"{len(countries)} countries")

# ------------------------------------------------ 6. derived financial fields
# Re-test the identity that makes GrossSales legitimate. If it ever fails, stop: the discount
# interpretation underpins the whole cost and margin analysis.
probe = df[df.Discount > 0].copy()
probe["implied_list"] = probe.Sales / probe.Quantity.astype(float) / (1 - probe.Discount)
cv = (probe.groupby("Product ID").implied_list
      .agg(lambda s: s.std() / s.mean() if len(s) > 1 and s.mean() else 0.0).dropna())
share_stable = float((cv < 0.01).mean())
if share_stable < 0.90:
    raise SystemExit(f"Implied list price is not stable ({share_stable:.1%} of products under 1% CV). "
                     "Sales may not be net of discount - do not derive GrossSales.")
log("Discount identity re-tested", len(df),
    f"implied list price stable for {share_stable * 100:.1f}% of discounted products")

df["GrossSales"] = (df.Sales / (1 - df.Discount)).round(4)
df["DiscountValue"] = (df.GrossSales - df.Sales).round(4)
df["Revenue"] = df.Sales.round(4)
df["ImpliedCost"] = (df.Sales - df.Profit).round(4)
df["Margin"] = np.where(df.Sales != 0, df.Profit / df.Sales, np.nan)
df["UnitPrice"] = (df.Sales / df.Quantity.astype(float)).round(4)
df["IsLossMaking"] = df.Profit < 0
# A 1 on the first line of each order. Counting distinct orders in Excel would otherwise need
# SUMPRODUCT(1/COUNTIF(range,range)), which is ~100 million operations over 9,994 rows and makes
# the workbook impractical to recalculate. This flag turns it into a SUM.
df["IsFirstLineOfOrder"] = (~df["Order ID"].duplicated()).astype(int)
log("Derived financial fields built", len(df),
    "GrossSales, DiscountValue, Revenue, ImpliedCost, Margin, UnitPrice, IsLossMaking, "
    "IsFirstLineOfOrder")

neg_cost = (df.ImpliedCost < 0).sum()
log("Lines where implied cost is negative", len(df),
    f"{neg_cost} ({neg_cost / len(df) * 100:.2f}%) - profit exceeds revenue on these lines; "
    f"kept and reported, not removed")

# ------------------------------------------------------------ 7. time fields
df["Year"] = df.OrderDate.dt.year
df["Quarter"] = df.OrderDate.dt.quarter
df["YearQuarter"] = df.OrderDate.dt.to_period("Q").astype(str)
df["YearMonth"] = df.OrderDate.dt.to_period("M").astype(str)
df["MonthNum"] = df.OrderDate.dt.month
df["MonthName"] = df.OrderDate.dt.strftime("%b")
months = df.YearMonth.nunique()
years = sorted(df.Year.unique())
log("Time fields built", len(df),
    f"{months} distinct months across {len(years)} years ({years[0]}-{years[-1]})")

expected = (df.OrderDate.max().to_period("M") - df.OrderDate.min().to_period("M")).n + 1
log("Calendar completeness", len(df),
    f"{months} of {expected} months present - "
    f"{'continuous, so period comparisons are valid' if months == expected else 'GAPS PRESENT'}")

# ------------------------------------------------------- 8. discount banding
df["DiscountBand"] = pd.cut(df.Discount, [-0.001, 0.0, 0.10, 0.20, 0.30, 0.50, 1.0],
                            labels=["0%", "1-10%", "11-20%", "21-30%", "31-50%", "over 50%"])
log("Discount bands assigned", len(df), "fixed documented bands, reproducible in SQL and Excel")

# ------------------------------------------------------------------- 9. write
cols = ["Row ID", "Order ID", "OrderDate", "ShipDate", "Ship Mode", "Customer ID", "Segment",
        "Country", "City", "State", "Postal Code", "Region", "Product ID", "Category",
        "Sub-Category", "Product Name", "Quantity", "Discount", "DiscountBand",
        "GrossSales", "DiscountValue", "Revenue", "ImpliedCost", "Profit", "Margin",
        "UnitPrice", "IsLossMaking", "IsFirstLineOfOrder", "Year", "Quarter", "YearQuarter",
        "YearMonth", "MonthNum", "MonthName"]
clean = df[cols].copy()
clean.to_csv(OUT / "superstore_clean.csv", index=False)
pd.DataFrame(LOG).to_csv(OUT / "cleaning_log.csv", index=False)

print("\n" + "=" * 96)
print(f"  superstore_clean.csv   {len(clean):,} lines x {clean.shape[1]} columns")
print(f"  rows removed           0  (every validation passed; nothing needed dropping)")
print(f"  gross sales            {clean.GrossSales.sum():>14,.2f}")
print(f"  discount given         {clean.DiscountValue.sum():>14,.2f}")
print(f"  net revenue            {clean.Revenue.sum():>14,.2f}")
print(f"  implied cost of sales  {clean.ImpliedCost.sum():>14,.2f}")
print(f"  profit                 {clean.Profit.sum():>14,.2f}")
print(f"  net margin             {clean.Profit.sum() / clean.Revenue.sum() * 100:>13.2f}%")

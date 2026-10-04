"""
02_analysis.py  -  the financial performance analysis
=====================================================
Author: Pranit Ajay Chaudhari

Input : data/cleaned/superstore_clean.csv
Output: outputs/csv/*.csv   every table quoted anywhere in the documentation

The analysis is deliberately FINANCIAL. It measures revenue, discount, implied cost, profit and
margin by product, category, region, segment and period, and builds a KPI set for management. It
contains no customer segmentation, no RFM, no cohort or retention analysis and no campaign
analysis - those belong to other projects in this portfolio and are listed in docs/DIFFERENTIATION.md.

Run:  python python/02_analysis.py
"""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "outputs" / "csv"
CSV.mkdir(parents=True, exist_ok=True)


# MySQL's ROUND() rounds a half away from zero; NumPy rounds a half to even, so an exact 26.25
# becomes 26.3 in SQL and 26.2 in pandas. Every published figure goes through r() so the Python,
# SQL and Excel numbers are identical rather than nearly so.
def r(x, dp=2):
    if pd.isna(x):
        return x
    return float(Decimal(str(float(x))).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def rs(s, dp=2):
    return s.map(lambda v: r(v, dp))


d = pd.read_csv(ROOT / "data" / "cleaned" / "superstore_clean.csv", parse_dates=["OrderDate", "ShipDate"])
TOT_REV, TOT_PROFIT = d.Revenue.sum(), d.Profit.sum()

print("FINANCIAL PERFORMANCE ANALYSIS\n" + "=" * 100)


def fin(g):
    """The standard financial block, applied to any grouping."""
    out = g.agg(Lines=("Row ID", "count"), Orders=("Order ID", "nunique"),
                Units=("Quantity", "sum"), GrossSales=("GrossSales", "sum"),
                DiscountValue=("DiscountValue", "sum"), Revenue=("Revenue", "sum"),
                ImpliedCost=("ImpliedCost", "sum"), Profit=("Profit", "sum"),
                LossLines=("IsLossMaking", "sum")).reset_index()
    out["MarginPct"] = rs(out.Profit / out.Revenue * 100)
    out["CostToRevenuePct"] = rs(out.ImpliedCost / out.Revenue * 100)
    out["DiscountRatePct"] = rs(out.DiscountValue / out.GrossSales * 100)
    out["RevenueSharePct"] = rs(out.Revenue / TOT_REV * 100)
    out["ProfitSharePct"] = rs(out.Profit / TOT_PROFIT * 100)
    out["LossLineSharePct"] = rs(out.LossLines / out.Lines * 100)
    out["AvgOrderValue"] = rs(out.Revenue / out.Orders)
    out["ProfitPerOrder"] = rs(out.Profit / out.Orders)
    for c in ["GrossSales", "DiscountValue", "Revenue", "ImpliedCost", "Profit"]:
        out[c] = rs(out[c])
    return out


# ================================================================ 1. KPI SET
print("\n1. BUSINESS KPIs\n" + "-" * 100)
kpi = pd.DataFrame({"Metric": [
    "Order lines", "Orders", "Units sold", "Distinct products", "Distinct customers",
    "Gross sales (list value)", "Discount given", "Discount rate (% of gross sales)",
    "Net revenue", "Implied cost of sales", "Profit", "Net margin (% of net revenue)",
    "Cost-to-revenue ratio (%)", "Average order value", "Profit per order",
    "Average revenue per line", "Profit per unit", "Loss-making order lines",
    "Loss-making order lines (%)", "Profit lost on loss-making lines",
    "Period covered", "Months covered"],
    "Value": [
    len(d), d["Order ID"].nunique(), int(d.Quantity.sum()), d["Product ID"].nunique(),
    d["Customer ID"].nunique(), r(d.GrossSales.sum()), r(d.DiscountValue.sum()),
    r(d.DiscountValue.sum() / d.GrossSales.sum() * 100), r(TOT_REV), r(d.ImpliedCost.sum()),
    r(TOT_PROFIT), r(TOT_PROFIT / TOT_REV * 100), r(d.ImpliedCost.sum() / TOT_REV * 100),
    r(TOT_REV / d["Order ID"].nunique()), r(TOT_PROFIT / d["Order ID"].nunique()),
    r(TOT_REV / len(d)), r(TOT_PROFIT / d.Quantity.sum()), int(d.IsLossMaking.sum()),
    r(d.IsLossMaking.mean() * 100), r(d.loc[d.IsLossMaking, "Profit"].sum()),
    f"{d.OrderDate.min().date()} to {d.OrderDate.max().date()}", d.YearMonth.nunique()]})
kpi.to_csv(CSV / "kpi_summary.csv", index=False)
print(kpi.to_string(index=False))

# =========================================================== 2. YEARLY TREND
print("\n2. YEARLY PERFORMANCE AND GROWTH\n" + "-" * 100)
yr = fin(d.groupby("Year"))
yr["RevenueGrowthPct"] = rs(yr.Revenue.pct_change() * 100)
yr["ProfitGrowthPct"] = rs(yr.Profit.pct_change() * 100)
yr["MarginChangePP"] = rs(yr.MarginPct.diff())
yr.to_csv(CSV / "yearly_performance.csv", index=False)
print(yr[["Year", "Orders", "Revenue", "ImpliedCost", "Profit", "MarginPct",
          "RevenueGrowthPct", "ProfitGrowthPct", "MarginChangePP", "AvgOrderValue"]].to_string(index=False))
n_years = len(yr)
cagr = r(((yr.Revenue.iloc[-1] / yr.Revenue.iloc[0]) ** (1 / (n_years - 1)) - 1) * 100)
print(f"\n   Revenue CAGR {yr.Year.iloc[0]}-{yr.Year.iloc[-1]}: {cagr}%")

# ======================================================== 3. QUARTERLY TREND
qt = fin(d.groupby("YearQuarter"))
qt["RevenueGrowthPct"] = rs(qt.Revenue.pct_change() * 100)
qt.to_csv(CSV / "quarterly_performance.csv", index=False)

# ========================================================== 4. MONTHLY TREND
mo = fin(d.groupby("YearMonth"))
mo["RevenueGrowthPct"] = rs(mo.Revenue.pct_change() * 100)
mo["Revenue3MthAvg"] = rs(mo.Revenue.rolling(3).mean())
mo.to_csv(CSV / "monthly_performance.csv", index=False)
print("\n3. MONTHLY TREND (last 8 months)\n" + "-" * 100)
print(mo[["YearMonth", "Orders", "Revenue", "Profit", "MarginPct", "RevenueGrowthPct"]].tail(8).to_string(index=False))
print(f"\n   Best month by revenue : {mo.loc[mo.Revenue.idxmax(), 'YearMonth']} ({mo.Revenue.max():,.2f})")
print(f"   Worst month by revenue: {mo.loc[mo.Revenue.idxmin(), 'YearMonth']} ({mo.Revenue.min():,.2f})")
print(f"   Months with a loss    : {(mo.Profit < 0).sum()} of {len(mo)}")

# ========================================================== 5. SEASONALITY
print("\n4. SEASONALITY TEST\n" + "-" * 100)
# 4 complete years means a month-of-year pattern can be tested rather than asserted. For each
# calendar month the revenue is indexed against that YEAR's monthly average, so growth across years
# does not masquerade as seasonality. A pattern is only called seasonal if it repeats in all 4 years.
tmp = d.groupby(["Year", "MonthNum"]).Revenue.sum().reset_index()
tmp["YearAvg"] = tmp.groupby("Year").Revenue.transform("mean")
tmp["Index"] = tmp.Revenue / tmp.YearAvg * 100
seas = tmp.pivot_table(index="MonthNum", columns="Year", values="Index").round(1)
seas["MeanIndex"] = rs(seas.mean(axis=1), 1)
seas["MinIndex"] = rs(seas.iloc[:, :n_years].min(axis=1), 1)
seas["AboveAverageInAllYears"] = seas.iloc[:, :n_years].gt(100).all(axis=1)
seas["BelowAverageInAllYears"] = seas.iloc[:, :n_years].lt(100).all(axis=1)
seas = seas.reset_index()
seas["MonthName"] = pd.to_datetime(seas.MonthNum, format="%m").dt.strftime("%b")
seas.to_csv(CSV / "seasonality.csv", index=False)
print(seas[["MonthNum", "MonthName"] + list(range(d.Year.min(), d.Year.max() + 1)) +
           ["MeanIndex", "AboveAverageInAllYears", "BelowAverageInAllYears"]].to_string(index=False))
cons_hi = seas[seas.AboveAverageInAllYears].MonthName.tolist()
cons_lo = seas[seas.BelowAverageInAllYears].MonthName.tolist()
print(f"\n   Consistently ABOVE the yearly average in all {n_years} years: {cons_hi or 'none'}")
print(f"   Consistently BELOW the yearly average in all {n_years} years: {cons_lo or 'none'}")

# ===================================================== 6. CATEGORY ANALYSIS
print("\n5. CATEGORY AND SUB-CATEGORY\n" + "-" * 100)
cat = fin(d.groupby("Category")).sort_values("Revenue", ascending=False)
cat.to_csv(CSV / "category_performance.csv", index=False)
print(cat[["Category", "Orders", "Units", "Revenue", "RevenueSharePct", "ImpliedCost", "Profit",
           "ProfitSharePct", "MarginPct", "DiscountRatePct", "LossLineSharePct"]].to_string(index=False))

sub = fin(d.groupby(["Category", "Sub-Category"])).sort_values("Revenue", ascending=False)
sub.to_csv(CSV / "subcategory_performance.csv", index=False)
print("\n   Sub-categories by revenue:")
print(sub[["Category", "Sub-Category", "Revenue", "RevenueSharePct", "Profit", "MarginPct",
           "DiscountRatePct", "LossLineSharePct"]].to_string(index=False))
loss_sub = sub[sub.Profit < 0]
print(f"\n   Sub-categories that LOSE money overall: {len(loss_sub)} of {len(sub)}"
      f" -> {loss_sub['Sub-Category'].tolist()}")
if len(loss_sub):
    print(f"   Combined loss: {loss_sub.Profit.sum():,.2f} on revenue of {loss_sub.Revenue.sum():,.2f}")

# high revenue / low margin quadrant
med_rev, med_mar = sub.Revenue.median(), sub.MarginPct.median()
sub["Quadrant"] = np.select(
    [(sub.Revenue >= med_rev) & (sub.MarginPct >= med_mar),
     (sub.Revenue >= med_rev) & (sub.MarginPct < med_mar),
     (sub.Revenue < med_rev) & (sub.MarginPct >= med_mar)],
    ["High revenue, high margin", "High revenue, LOW margin", "Low revenue, high margin"],
    default="Low revenue, low margin")
quad = sub.groupby("Quadrant").agg(SubCategories=("Sub-Category", "count"),
                                   Revenue=("Revenue", "sum"), Profit=("Profit", "sum")).reset_index()
quad["MarginPct"] = rs(quad.Profit / quad.Revenue * 100)
quad["RevenueSharePct"] = rs(quad.Revenue / TOT_REV * 100)
quad.to_csv(CSV / "revenue_margin_quadrants.csv", index=False)
sub[["Category", "Sub-Category", "Revenue", "MarginPct", "Quadrant"]].to_csv(
    CSV / "subcategory_quadrants.csv", index=False)
print(f"\n   Revenue/margin quadrants (split at the median sub-category revenue "
      f"{med_rev:,.2f} and median margin {med_mar}%):")
print(quad.to_string(index=False))

# ====================================================== 7. REGIONAL ANALYSIS
print("\n6. REGIONAL PERFORMANCE\n" + "-" * 100)
reg = fin(d.groupby("Region")).sort_values("Revenue", ascending=False)
reg.to_csv(CSV / "regional_performance.csv", index=False)
print(reg[["Region", "Orders", "Revenue", "RevenueSharePct", "ImpliedCost", "Profit",
           "ProfitSharePct", "MarginPct", "DiscountRatePct", "AvgOrderValue"]].to_string(index=False))

reg_yr = fin(d.groupby(["Region", "Year"]))
reg_yr = reg_yr.sort_values(["Region", "Year"])
reg_yr["RevenueGrowthPct"] = rs(reg_yr.groupby("Region").Revenue.pct_change() * 100)
reg_yr.to_csv(CSV / "regional_yearly.csv", index=False)

st = fin(d.groupby(["Region", "State"])).sort_values("Revenue", ascending=False)
st.to_csv(CSV / "state_performance.csv", index=False)
loss_states = st[st.Profit < 0]
print(f"\n   States analysed: {len(st)}. States that lose money overall: {len(loss_states)}")
print(loss_states[["Region", "State", "Revenue", "Profit", "MarginPct", "DiscountRatePct"]]
      .head(12).to_string(index=False))
print(f"   Combined loss from loss-making states: {loss_states.Profit.sum():,.2f}")

# ======================================================= 8. SEGMENT ANALYSIS
seg = fin(d.groupby("Segment")).sort_values("Revenue", ascending=False)
seg.to_csv(CSV / "segment_performance.csv", index=False)
ship = fin(d.groupby("Ship Mode")).sort_values("Revenue", ascending=False)
ship.to_csv(CSV / "shipmode_performance.csv", index=False)

# ====================================================== 9. DISCOUNT ANALYSIS
print("\n7. DISCOUNT AND MARGIN\n" + "-" * 100)
disc = fin(d.groupby("DiscountBand", observed=True))
disc.to_csv(CSV / "discount_band_performance.csv", index=False)
print(disc[["DiscountBand", "Lines", "GrossSales", "DiscountValue", "Revenue", "ImpliedCost",
            "Profit", "MarginPct", "LossLineSharePct"]].to_string(index=False))

rate = fin(d.groupby("Discount"))
rate.to_csv(CSV / "discount_rate_performance.csv", index=False)
print("\n   By exact discount rate:")
print(rate[["Discount", "Lines", "Revenue", "Profit", "MarginPct", "LossLineSharePct"]].to_string(index=False))
breakeven = rate[rate.MarginPct < 0].Discount.min()
last_pos = rate[rate.MarginPct >= 0].Discount.max()
print(f"\n   Margin is positive up to and including a {last_pos:.0%} discount and negative from "
      f"{breakeven:.0%} upward.")

# ================================================= 10. REVENUE CONCENTRATION
print("\n8. REVENUE AND PROFIT CONCENTRATION\n" + "-" * 100)
prod = d.groupby("Product ID").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
                                   Units=("Quantity", "sum"), Lines=("Row ID", "count")).reset_index()
prod = prod.sort_values("Revenue", ascending=False)
prod["CumRevenuePct"] = rs(prod.Revenue.cumsum() / TOT_REV * 100)
prod["RankPct"] = rs(pd.Series((np.arange(len(prod)) + 1) / len(prod) * 100, index=prod.index))
conc = pd.DataFrame({"Measure": [
    "Products", "Products producing 50% of revenue", "Top 20% of products - share of revenue (%)",
    "Top 10% of products - share of revenue (%)", "Products that lose money",
    "Products that lose money (%)", "Combined loss from loss-making products",
    "Profit from profitable products"],
    "Value": [
    len(prod), int((prod.CumRevenuePct <= 50).sum() + 1),
    r(prod.Revenue.head(int(np.ceil(len(prod) * 0.20))).sum() / TOT_REV * 100),
    r(prod.Revenue.head(int(np.ceil(len(prod) * 0.10))).sum() / TOT_REV * 100),
    int((prod.Profit < 0).sum()), r((prod.Profit < 0).mean() * 100),
    r(prod.loc[prod.Profit < 0, "Profit"].sum()), r(prod.loc[prod.Profit > 0, "Profit"].sum())]})
conc.to_csv(CSV / "revenue_concentration.csv", index=False)
print(conc.to_string(index=False))

top_prod = prod.head(20).merge(d[["Product ID", "Product Name", "Category", "Sub-Category"]]
                               .drop_duplicates("Product ID"), on="Product ID", how="left")
top_prod["MarginPct"] = rs(top_prod.Profit / top_prod.Revenue * 100)
top_prod[["Product ID", "Product Name", "Category", "Sub-Category", "Revenue", "Profit",
          "MarginPct", "Units"]].to_csv(CSV / "top_products_by_revenue.csv", index=False)

worst = prod.nsmallest(20, "Profit").merge(d[["Product ID", "Product Name", "Category", "Sub-Category"]]
                                           .drop_duplicates("Product ID"), on="Product ID", how="left")
worst["MarginPct"] = rs(worst.Profit / worst.Revenue * 100)
worst[["Product ID", "Product Name", "Category", "Sub-Category", "Revenue", "Profit",
       "MarginPct", "Units"]].to_csv(CSV / "worst_products_by_profit.csv", index=False)
print(f"\n   The 20 worst products by profit lose {worst.Profit.sum():,.2f} between them.")

# ================================================== 11. COST STRUCTURE
print("\n9. COST STRUCTURE\n" + "-" * 100)
cost = pd.DataFrame({"Component": [
    "Gross sales (list value)", "less: discount given", "= Net revenue",
    "less: implied cost of sales", "= Profit"],
    "Amount": [r(d.GrossSales.sum()), r(-d.DiscountValue.sum()), r(TOT_REV),
               r(-d.ImpliedCost.sum()), r(TOT_PROFIT)],
    "PctOfGrossSales": [100.0, r(-d.DiscountValue.sum() / d.GrossSales.sum() * 100),
                        r(TOT_REV / d.GrossSales.sum() * 100),
                        r(-d.ImpliedCost.sum() / d.GrossSales.sum() * 100),
                        r(TOT_PROFIT / d.GrossSales.sum() * 100)],
    "PctOfNetRevenue": [r(d.GrossSales.sum() / TOT_REV * 100),
                        r(-d.DiscountValue.sum() / TOT_REV * 100), 100.0,
                        r(-d.ImpliedCost.sum() / TOT_REV * 100), r(TOT_PROFIT / TOT_REV * 100)]})
cost.to_csv(CSV / "cost_structure.csv", index=False)
print(cost.to_string(index=False))
print("\n   NOTE: the dataset contains no operating expenses, overheads or payroll, so no operating")
print("   margin, EBITDA or net profit in the accounting sense can be computed. Those are outside")
print("   this dataset's scope and are not estimated anywhere in this project.")

cost_yr = yr[["Year", "Revenue", "ImpliedCost", "Profit", "CostToRevenuePct", "MarginPct"]].copy()
cost_yr["CostGrowthPct"] = rs(cost_yr.ImpliedCost.pct_change() * 100)
cost_yr["RevenueGrowthPct"] = rs(cost_yr.Revenue.pct_change() * 100)
cost_yr.to_csv(CSV / "cost_trend.csv", index=False)
print("\n   Cost trend:")
print(cost_yr.to_string(index=False))

print("\n" + "=" * 100)
print(f"  {len(list(CSV.glob('*.csv')))} result tables written to outputs/csv/")

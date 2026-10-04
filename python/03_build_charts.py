"""
03_build_charts.py  -  charts, generated from the computed result tables
========================================================================
Author: Pranit Ajay Chaudhari

Input : outputs/csv/*.csv   (written by 02_analysis.py)
Output: outputs/charts/*.png

Design rules followed: one y-axis per chart and no dual axes anywhere; categorical hues assigned in
a fixed validated order and never cycled; profit-versus-loss uses a validated diverging blue/red
pair rather than a categorical hue, because the sign carries the meaning; a direct value label on
every mark, which also provides the required relief for palette slots below 3:1 contrast on a light
surface. The CSV tables in outputs/csv/ are the table view of every chart.

Run:  python python/03_build_charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "outputs" / "csv"
CH = ROOT / "outputs" / "charts"
CH.mkdir(parents=True, exist_ok=True)

C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"          # categorical, fixed order
POS, NEG = "#2a78d6", "#d03b3b"                        # diverging: profit / loss
ORD5 = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e1e0d9", "#fcfcfb"

plt.rcParams.update({
    "figure.dpi": 110, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c3c2b7", "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "axes.titlesize": 12, "axes.titleweight": "600",
    "axes.titlecolor": INK, "axes.labelcolor": INK2, "axes.labelsize": 9.5,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.frameon": False, "legend.fontsize": 9})

made = []


def save(name, note=""):
    plt.tight_layout()
    plt.savefig(CH / name, bbox_inches="tight", facecolor=SURFACE)
    plt.close()
    made.append(name)
    print(f"  {name:<40} {note}")


def label(ax, bars, fmt="{:,.0f}", size=8.5, pad=0.012):
    hs = [b.get_height() for b in bars]
    span = (max(hs) - min(min(hs), 0)) or 1
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + span * pad * (1 if h >= 0 else -2.2),
                fmt.format(h), ha="center", va="bottom" if h >= 0 else "top",
                fontsize=size, color=INK2)


print("Charts\n" + "=" * 72)

# ------------------------------------------------- 1. cost structure waterfall
cost = pd.read_csv(CSV / "cost_structure.csv")
fig, ax = plt.subplots(figsize=(8.2, 4.4))
labels = ["Gross\nsales", "Discount\ngiven", "Net\nrevenue", "Implied cost\nof sales", "Profit"]
amounts = cost.Amount.tolist()
running, bottoms, heights, colours = 0.0, [], [], []
for i, a in enumerate(amounts):
    if i in (0, 2, 4):
        bottoms.append(0); heights.append(a); colours.append(C1 if i != 4 else C3)
        running = a
    else:
        bottoms.append(running + a); heights.append(-a); colours.append(C2)
        running = running + a
bars = ax.bar(labels, heights, bottom=bottoms, color=colours, width=0.6)
for lab_, b_, h_, a_ in zip(labels, bottoms, heights, amounts):
    ax.text(labels.index(lab_), b_ + h_ + 55000, f"{a_:,.0f}", ha="center", fontsize=9, color=INK2)
ax.set_title("From list price to profit: where every dollar of gross sales goes\n"
             "Discount takes 19.79% and the cost of sales takes 70.21%")
ax.set_ylabel("USD")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
ax.set_ylim(0, 3_250_000)
save("01_cost_structure.png", "waterfall")

# --------------------------------------------------- 2. yearly revenue & profit
yr = pd.read_csv(CSV / "yearly_performance.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.1))
b = a1.bar(yr.Year.astype(str), yr.Revenue, color=C1, width=0.6)
label(a1, b, "{:,.0f}")
a1.set_title("Net revenue", fontsize=11); a1.set_ylabel("USD")
a1.set_ylim(0, yr.Revenue.max() * 1.18)
b2 = a2.bar(yr.Year.astype(str), yr.MarginPct, color=C2, width=0.6)
label(a2, b2, "{:.2f}%")
a2.set_title("Net margin", fontsize=11); a2.set_ylabel("Percent of net revenue")
a2.set_ylim(0, yr.MarginPct.max() * 1.25)
fig.suptitle("Revenue grew 14.83% a year while margin stayed in a narrow band\n"
             "2014-2017, four complete years", fontsize=12, fontweight="600", color=INK, y=1.05)
save("02_yearly_revenue_margin.png", "two panels, one scale each")

# ----------------------------------------------------------- 3. monthly trend
mo = pd.read_csv(CSV / "monthly_performance.csv")
fig, ax = plt.subplots(figsize=(10.6, 4.0))
x = np.arange(len(mo))
ax.plot(x, mo.Revenue, color=C1, linewidth=1.6, label="Monthly net revenue")
ax.plot(x, mo.Revenue3MthAvg, color=C2, linewidth=2.4, label="3-month average")
ax.set_xticks(x[::3]); ax.set_xticklabels(mo.YearMonth[::3], rotation=60, ha="right", fontsize=8)
ax.set_title("Monthly net revenue, 48 continuous months\n"
             "Growth is real but the month-to-month swing is wide")
ax.set_ylabel("Net revenue (USD)")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
ax.legend(loc="upper left")
save("03_monthly_revenue.png", "line, 2 series")

# ------------------------------------------------------------ 4. seasonality
se = pd.read_csv(CSV / "seasonality.csv")
fig, ax = plt.subplots(figsize=(9.0, 4.1))
colours = [C1 if a else (C2 if b else "#b7d3f6")
           for a, b in zip(se.AboveAverageInAllYears, se.BelowAverageInAllYears)]
bars = ax.bar(se.MonthName, se.MeanIndex, color=colours, width=0.62)
label(ax, bars, "{:.0f}")
ax.axhline(100, color=INK2, linestyle="--", linewidth=1.2)
ax.text(11.4, 102, "yearly average", ha="right", fontsize=8.5, color=INK2)
ax.set_title("September, November and December beat the yearly average in all four years\n"
             "Revenue indexed against each year's own monthly average, so growth is not mistaken for season")
ax.set_xlabel("Month"); ax.set_ylabel("Index (year's monthly average = 100)")
ax.set_ylim(0, 205)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (C1, C2, "#b7d3f6")]
ax.legend(handles, ["Above average in all 4 years", "Below average in all 4 years", "Mixed"],
          ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.19))
save("04_seasonality.png", "seasonality index")

# --------------------------------------------------------- 5. category split
cat = pd.read_csv(CSV / "category_performance.csv")
fig, ax = plt.subplots(figsize=(8.8, 4.3))
x = np.arange(len(cat)); w = 0.26
b1 = ax.bar(x - w - 0.012, cat.RevenueSharePct, w, color=C1, label="Share of revenue (%)")
b2 = ax.bar(x, cat.ProfitSharePct, w, color=C2, label="Share of profit (%)")
b3 = ax.bar(x + w + 0.012, cat.MarginPct, w, color=C3, label="Net margin (%)")
for bb in (b1, b2, b3):
    label(ax, bb, "{:.1f}", size=8)
ax.set_xticks(x); ax.set_xticklabels(cat.Category)
ax.set_title("Furniture is a third of revenue and a sixteenth of profit\n"
             "Its 2.49% margin is a seventh of Technology's")
ax.set_ylabel("Percent"); ax.set_ylim(0, 60)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.13))
save("05_category_revenue_vs_profit.png", "3 series, slots 1-3")

# ------------------------------------------------------ 6. sub-category margin
sub = pd.read_csv(CSV / "subcategory_performance.csv").sort_values("MarginPct")
fig, ax = plt.subplots(figsize=(8.4, 6.0))
cols = [NEG if m < 0 else POS for m in sub.MarginPct]
bars = ax.barh(sub["Sub-Category"], sub.MarginPct, color=cols, height=0.66)
for b_, m in zip(bars, sub.MarginPct):
    ax.text(m + (1.2 if m >= 0 else -1.2), b_.get_y() + b_.get_height() / 2, f"{m:.2f}%",
            va="center", ha="left" if m >= 0 else "right", fontsize=8.5, color=INK2)
ax.axvline(0, color=INK2, linewidth=1)
ax.set_title("Three sub-categories lose money on every dollar of revenue\n"
             "Tables, Bookcases and Supplies, together -22,387 USD on 368,519 of revenue")
ax.set_xlabel("Net margin (%)"); ax.set_xlim(-16, 52)
save("06_subcategory_margin.png", "diverging, sign carries meaning")

# ------------------------------------------------------- 7. discount vs margin
db = pd.read_csv(CSV / "discount_band_performance.csv")
fig, ax = plt.subplots(figsize=(9.0, 4.3))
cols = [NEG if m < 0 else POS for m in db.MarginPct]
bars = ax.bar(db.DiscountBand.astype(str), db.MarginPct, color=cols, width=0.6)
label(ax, bars, "{:.2f}%")
ax.axhline(0, color=INK2, linewidth=1)
ax.set_title("Margin turns negative once the discount passes 20%\n"
             "Every order line discounted over 50% loses money")
ax.set_xlabel("Discount band"); ax.set_ylabel("Net margin (%)")
ax.set_ylim(-145, 45)
save("07_discount_vs_margin.png", "the central finding")

# ---------------------------------------------------------- 8. region margin
reg = pd.read_csv(CSV / "regional_performance.csv").sort_values("MarginPct", ascending=False)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.1))
b = a1.bar(reg.Region, reg.MarginPct, color=ORD5[::-1][:len(reg)], width=0.58)
label(a1, b, "{:.2f}%")
a1.set_title("Net margin", fontsize=11); a1.set_ylabel("Percent"); a1.set_ylim(0, reg.MarginPct.max() * 1.25)
b2 = a2.bar(reg.Region, reg.DiscountRatePct, color=ORD5[::-1][:len(reg)], width=0.58)
label(a2, b2, "{:.2f}%")
a2.set_title("Discount as a share of gross sales", fontsize=11); a2.set_ylabel("Percent")
a2.set_ylim(0, reg.DiscountRatePct.max() * 1.25)
fig.suptitle("The region that discounts most earns least\n"
             "Central gives away 24.56% of list value and returns a 7.92% margin",
             fontsize=12, fontweight="600", color=INK, y=1.05)
save("08_regional_margin_vs_discount.png", "two panels")

# ------------------------------------------------------- 9. loss-making states
st = pd.read_csv(CSV / "state_performance.csv")
loss = st[st.Profit < 0].sort_values("Profit")
fig, ax = plt.subplots(figsize=(8.6, 4.6))
bars = ax.barh(loss.State, loss.Profit, color=NEG, height=0.64)
for b_, v in zip(bars, loss.Profit):
    ax.text(v - 500, b_.get_y() + b_.get_height() / 2, f"{v:,.0f}", va="center", ha="right",
            fontsize=8.5, color=INK2)
ax.axvline(0, color=INK2, linewidth=1)
ax.set_title("Ten states lose money, costing 98,247 USD in total\n"
             "Every one of them discounts at least 29% of list value")
ax.set_xlabel("Profit (USD)"); ax.set_xlim(loss.Profit.min() * 1.32, 0)
ax.invert_yaxis()
save("09_loss_making_states.png", "diverging, loss only")

# ----------------------------------------------------- 10. revenue concentration
prod = pd.read_csv(CSV / "revenue_concentration.csv")
top = pd.read_csv(CSV / "top_products_by_revenue.csv")
fig, ax = plt.subplots(figsize=(8.8, 4.3))
vals = [float(prod.loc[prod.Measure == "Top 10% of products - share of revenue (%)", "Value"].iloc[0]),
        float(prod.loc[prod.Measure == "Top 20% of products - share of revenue (%)", "Value"].iloc[0]),
        100.0]
bars = ax.bar(["Top 10% of products", "Top 20% of products", "All 1,862 products"], vals,
              color=[ORD5[4], ORD5[2], ORD5[0]], width=0.55)
label(ax, bars, "{:.2f}%")
ax.set_title("Revenue is concentrated: a fifth of the catalogue carries over three quarters of it\n"
             "133 of 1,862 products produce half of all revenue")
ax.set_ylabel("Share of net revenue (%)"); ax.set_ylim(0, 118)
save("10_revenue_concentration.png", "ordinal ramp")

print("=" * 72)
print(f"  {len(made)} charts written to outputs/charts/")
